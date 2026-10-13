use std::fs::OpenOptions;
use std::io::{Cursor, Read};
use std::os::unix::fs::OpenOptionsExt;
use std::path::Path;

use sha2::{Digest, Sha256};

use crate::{ContentHash, MediaDescriptor, Result, StoredAsset, StudioError, pixels};

const MAX_FILE_BYTES: u64 = pixels::MAX_OWNED_FRAME_BYTES + 1024 * 1024;

fn error(detail: impl Into<String>) -> StudioError {
    StudioError::new("invalid_image", detail)
}

fn read_file(path: &Path) -> Result<Vec<u8>> {
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(path)?;
    let metadata = file.metadata()?;
    if !metadata.is_file() || metadata.len() > MAX_FILE_BYTES {
        return Err(error("PNG file exceeds the bounded image input size"));
    }
    let mut bytes = Vec::new();
    file.take(MAX_FILE_BYTES + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > MAX_FILE_BYTES || bytes.len() as u64 != metadata.len() {
        return Err(error("PNG input length changed or exceeds the input bound"));
    }
    Ok(bytes)
}

pub(crate) fn probe(path: &Path) -> Result<MediaDescriptor> {
    Ok(decode(&read_file(path)?)?.1)
}

pub(crate) fn decode_asset(path: &Path, asset: &StoredAsset) -> Result<pixels::Pixels> {
    decode_picture_asset(path, asset)?.into_legacy_opaque()
}

pub(crate) fn decode_picture_asset(
    path: &Path,
    asset: &StoredAsset,
) -> Result<crate::alpha_picture::DecodedPicture> {
    decode_picture_asset_cancellable(path, asset, || Ok(()))
}

pub(crate) fn decode_picture_asset_cancellable(
    path: &Path,
    asset: &StoredAsset,
    mut check: impl FnMut() -> Result<()>,
) -> Result<crate::alpha_picture::DecodedPicture> {
    check()?;
    let bytes = read_file(path)?;
    if bytes.len() as u64 != asset.bytes || ContentHash::bytes(&bytes) != asset.hash {
        return Err(StudioError::new(
            "asset_tampered",
            "PNG bytes differ from the immutable asset",
        ));
    }
    let (pixels, descriptor) = decode_cancellable(&bytes, &mut check)?;
    if descriptor != asset.descriptor {
        return Err(StudioError::new(
            "measurement_changed",
            "Decoded PNG differs from its stored measurement",
        ));
    }
    Ok(pixels)
}

fn decode(bytes: &[u8]) -> Result<(crate::alpha_picture::DecodedPicture, MediaDescriptor)> {
    decode_cancellable(bytes, || Ok(()))
}

fn decode_cancellable(
    bytes: &[u8],
    mut check: impl FnMut() -> Result<()>,
) -> Result<(crate::alpha_picture::DecodedPicture, MediaDescriptor)> {
    check()?;
    validate_png_boundary(bytes)?;
    let mut options = png::DecodeOptions::default();
    options.set_ignore_crc(false);
    options.set_skip_ancillary_crc_failures(false);
    let mut decoder = png::Decoder::new_with_options(Cursor::new(bytes), options);
    decoder.set_limits(png::Limits {
        bytes: pixels::MAX_OWNED_FRAME_BYTES as usize,
    });
    decoder.set_transformations(png::Transformations::EXPAND);
    let mut reader = decoder.read_info().map_err(|e| error(e.to_string()))?;
    let info = reader.info();
    if info.animation_control.is_some() || info.frame_control.is_some() {
        return Err(StudioError::new(
            "unsupported_image_animation",
            "PNG animation requires a timed image implementation",
        ));
    }
    if info.bit_depth == png::BitDepth::Sixteen {
        return Err(StudioError::new(
            "unsupported_image_depth",
            "Sixteen-bit PNG samples require explicit precision and color handling",
        ));
    }
    let (width, height) = (info.width, info.height);
    let size = pixels::extent(width, height)?;
    if reader.output_buffer_size() > size {
        return Err(error("Expanded PNG extent exceeds its RGBA frame"));
    }
    let mut samples = vec![0; reader.output_buffer_size()];
    let output = reader
        .next_frame(&mut samples)
        .map_err(|e| error(e.to_string()))?;
    reader.finish().map_err(|e| error(e.to_string()))?;
    if reader.info().animation_control.is_some() || reader.info().frame_control.is_some() {
        return Err(StudioError::new(
            "unsupported_image_animation",
            "PNG animation is outside the static image scope",
        ));
    }
    if output.width != width || output.height != height || output.bit_depth != png::BitDepth::Eight
    {
        return Err(error("Expanded PNG layout changed or is not eight-bit"));
    }
    let samples = &samples[..output.buffer_size()];
    let mut rgba = Vec::with_capacity(size);
    let channels = match output.color_type {
        png::ColorType::Rgb => 3usize,
        png::ColorType::Rgba => 4,
        png::ColorType::Grayscale => 1,
        png::ColorType::GrayscaleAlpha => 2,
        png::ColorType::Indexed => return Err(error("PNG palette was not expanded")),
    };
    let row_samples = usize::try_from(width)
        .ok()
        .and_then(|width| width.checked_mul(channels))
        .ok_or_else(|| error("Expanded PNG row extent overflow"))?;
    if samples.len() != row_samples * height as usize {
        return Err(error("Expanded PNG sample extent differs from its layout"));
    }
    for row in samples.chunks_exact(row_samples) {
        check()?;
        match output.color_type {
            png::ColorType::Rgb => {
                for pixel in row.chunks_exact(3) {
                    rgba.extend_from_slice(&[pixel[0], pixel[1], pixel[2], 255]);
                }
            }
            png::ColorType::Rgba => rgba.extend_from_slice(row),
            png::ColorType::Grayscale => {
                for &value in row {
                    rgba.extend_from_slice(&[value, value, value, 255]);
                }
            }
            png::ColorType::GrayscaleAlpha => {
                for pixel in row.chunks_exact(2) {
                    rgba.extend_from_slice(&[pixel[0], pixel[0], pixel[0], pixel[1]]);
                }
            }
            png::ColorType::Indexed => unreachable!(),
        }
    }
    if rgba.len() != size {
        return Err(error("PNG pixel count differs from its dimensions"));
    }
    let rgba_sha256 = ContentHash::bytes(&rgba);
    let mut alpha_digest = Sha256::new();
    let (mut minimum, mut maximum) = (u8::MAX, u8::MIN);
    let (mut nonzero_pixels, mut nonopaque_pixels) = (0u64, 0u64);
    let rgba_row = width as usize * 4;
    for row in rgba.chunks_exact(rgba_row) {
        check()?;
        for pixel in row.chunks_exact(4) {
            let alpha = pixel[3];
            alpha_digest.update([alpha]);
            minimum = minimum.min(alpha);
            maximum = maximum.max(alpha);
            nonzero_pixels += u64::from(alpha != 0);
            nonopaque_pixels += u64::from(alpha != 255);
        }
    }
    let alpha = (nonopaque_pixels != 0).then(|| crate::ImageAlphaV1 {
        schema: 1,
        alpha_sha256: ContentHash::parse(format!("{:x}", alpha_digest.finalize()))
            .expect("SHA-256 digest is a canonical content hash"),
        minimum,
        maximum,
        nonzero_pixels,
        nonopaque_pixels,
    });
    if let Some(alpha) = &alpha {
        alpha.validate(width, height)?;
    }
    let descriptor = MediaDescriptor::Image {
        format: "png".into(),
        width,
        height,
        rgba_sha256,
        warnings: vec!["Source sample values only; ICC, gamma, color conversion and creative acceptance remain unverified".into()],
        alpha: alpha.clone(),
    };
    let picture = if alpha.is_some() {
        crate::alpha_picture::DecodedPicture::StraightAlpha(
            crate::alpha_picture::StraightRgba8::new(width, height, rgba)?,
        )
    } else {
        for pixel in rgba.chunks_exact_mut(4) {
            pixel.swap(0, 2);
        }
        crate::alpha_picture::DecodedPicture::LegacyOpaque(pixels::Pixels {
            width,
            height,
            bytes: rgba,
        })
    };
    Ok((picture, descriptor))
}

fn validate_png_boundary(bytes: &[u8]) -> Result<()> {
    if bytes.get(..8) != Some(b"\x89PNG\r\n\x1a\n") {
        return Err(error("Image input is not a PNG stream"));
    }
    let mut start = 8usize;
    while start < bytes.len() {
        let header = bytes
            .get(start..start.saturating_add(8))
            .ok_or_else(|| error("PNG chunk header is truncated"))?;
        let length = u32::from_be_bytes(
            header[..4]
                .try_into()
                .map_err(|_| error("Invalid PNG chunk length"))?,
        ) as usize;
        let end = start
            .checked_add(12)
            .and_then(|value| value.checked_add(length))
            .filter(|&value| value <= bytes.len())
            .ok_or_else(|| error("PNG chunk extent is truncated"))?;
        if &header[4..8] == b"IEND" {
            if length != 0 || end != bytes.len() {
                return Err(error("PNG must end exactly at its zero-length IEND chunk"));
            }
            return Ok(());
        }
        start = end;
    }
    Err(error("PNG has no terminal IEND chunk"))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn independent_fixture_root() -> std::path::PathBuf {
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/alpha")
    }

    fn png(color: png::ColorType, depth: png::BitDepth, samples: &[u8]) -> Vec<u8> {
        let mut bytes = Vec::new();
        let mut encoder = png::Encoder::new(&mut bytes, 2, 1);
        encoder.set_color(color);
        encoder.set_depth(depth);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(samples).unwrap();
        writer.finish().unwrap();
        bytes
    }

    fn opaque(bytes: &[u8]) -> pixels::Pixels {
        decode(bytes).unwrap().0.into_legacy_opaque().unwrap()
    }

    #[test]
    fn expanded_pixels_bind_hash_without_swapping_channel_semantics() {
        let bytes = png(
            png::ColorType::Rgb,
            png::BitDepth::Eight,
            &[255, 0, 7, 3, 40, 99],
        );
        let (pixels, descriptor) = decode(&bytes).unwrap();
        let pixels = pixels.into_legacy_opaque().unwrap();
        assert_eq!(pixels.bytes, [7, 0, 255, 255, 99, 40, 3, 255]);
        let MediaDescriptor::Image {
            rgba_sha256,
            width,
            height,
            ..
        } = descriptor
        else {
            panic!()
        };
        assert_eq!((width, height), (2, 1));
        assert_eq!(
            rgba_sha256,
            ContentHash::bytes(&[255, 0, 7, 255, 3, 40, 99, 255])
        );
        let gray = png(png::ColorType::Grayscale, png::BitDepth::Eight, &[0, 127]);
        assert_eq!(opaque(&gray).bytes, [0, 0, 0, 255, 127, 127, 127, 255]);
    }

    #[test]
    fn alpha_precision_and_complete_stream_are_measured() {
        let opaque = png(
            png::ColorType::Rgba,
            png::BitDepth::Eight,
            &[1, 2, 3, 255, 4, 5, 6, 255],
        );
        let (picture, descriptor) = decode(&opaque).unwrap();
        assert!(matches!(
            picture,
            crate::alpha_picture::DecodedPicture::LegacyOpaque(_)
        ));
        assert!(matches!(
            descriptor,
            MediaDescriptor::Image { alpha: None, .. }
        ));
        let alpha = png(
            png::ColorType::Rgba,
            png::BitDepth::Eight,
            &[1, 2, 3, 254, 4, 5, 6, 255],
        );
        let (picture, descriptor) = decode(&alpha).unwrap();
        assert!(matches!(
            picture,
            crate::alpha_picture::DecodedPicture::StraightAlpha(_)
        ));
        let MediaDescriptor::Image {
            rgba_sha256,
            alpha: Some(measured),
            ..
        } = descriptor
        else {
            panic!("transparent descriptor expected")
        };
        assert_eq!(
            rgba_sha256,
            ContentHash::bytes(&[1, 2, 3, 254, 4, 5, 6, 255])
        );
        assert_eq!(measured.alpha_sha256, ContentHash::bytes(&[254, 255]));
        assert_eq!((measured.minimum, measured.maximum), (254, 255));
        assert_eq!((measured.nonzero_pixels, measured.nonopaque_pixels), (2, 1));
        let sixteen = png(
            png::ColorType::Grayscale,
            png::BitDepth::Sixteen,
            &[0, 1, 0, 2],
        );
        assert_eq!(
            decode(&sixteen).err().unwrap().code,
            "unsupported_image_depth"
        );
        assert_eq!(
            decode(&opaque[..opaque.len() - 12]).err().unwrap().code,
            "invalid_image"
        );
        let mut corrupt = opaque;
        let idat = corrupt.windows(4).position(|part| part == b"IDAT").unwrap();
        corrupt[idat + 4] ^= 1;
        assert_eq!(decode(&corrupt).err().unwrap().code, "invalid_image");
    }

    #[test]
    fn grayscale_and_transparency_chunks_expand_to_straight_rgba() {
        fn measurement(bytes: &[u8], expected_rgba: &[u8], expected_alpha: &[u8]) {
            let (picture, descriptor) = decode(bytes).unwrap();
            assert!(matches!(
                picture,
                crate::alpha_picture::DecodedPicture::StraightAlpha(_)
            ));
            let MediaDescriptor::Image {
                rgba_sha256,
                alpha: Some(alpha),
                ..
            } = descriptor
            else {
                panic!("alpha measurement expected")
            };
            assert_eq!(rgba_sha256, ContentHash::bytes(expected_rgba));
            assert_eq!(alpha.alpha_sha256, ContentHash::bytes(expected_alpha));
        }

        let grayscale_alpha = png(
            png::ColorType::GrayscaleAlpha,
            png::BitDepth::Eight,
            &[10, 0, 200, 128],
        );
        measurement(
            &grayscale_alpha,
            &[10, 10, 10, 0, 200, 200, 200, 128],
            &[0, 128],
        );

        let mut indexed = Vec::new();
        let mut encoder = png::Encoder::new(&mut indexed, 2, 1);
        encoder.set_color(png::ColorType::Indexed);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_palette(vec![10, 20, 30, 40, 50, 60]);
        encoder.set_trns(vec![0, 128]);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[0, 1]).unwrap();
        writer.finish().unwrap();
        measurement(&indexed, &[10, 20, 30, 0, 40, 50, 60, 128], &[0, 128]);

        let mut rgb = Vec::new();
        let mut encoder = png::Encoder::new(&mut rgb, 2, 1);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_trns(vec![0, 10, 0, 20, 0, 30]);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[10, 20, 30, 1, 2, 3]).unwrap();
        writer.finish().unwrap();
        measurement(&rgb, &[10, 20, 30, 0, 1, 2, 3, 255], &[0, 255]);
    }

    #[test]
    fn independent_a03_decoder_variants_match_straight_pixel_facts() {
        let root = independent_fixture_root();
        let manifest_bytes = std::fs::read(root.join("alpha-fixture-a03.json")).unwrap();
        assert_eq!(
            ContentHash::bytes(&manifest_bytes).as_str(),
            "afdfb1848940b9063640871bf834c90c29ba2a2d4049811843514621dccb9ddc"
        );
        let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();
        for (name, filename) in [
            ("grayscale_alpha", "grayscale-alpha-a01.png"),
            ("indexed_trns", "indexed-trns-a01.png"),
            ("rgb_trns", "rgb-trns-a01.png"),
        ] {
            let declared = &manifest["decoderVariants"][name];
            let bytes = std::fs::read(root.join(filename)).unwrap();
            assert_eq!(bytes.len() as u64, declared["bytes"].as_u64().unwrap());
            assert_eq!(
                ContentHash::bytes(&bytes).as_str(),
                declared["compressedSha256"].as_str().unwrap()
            );
            let (picture, descriptor) = decode(&bytes).unwrap();
            assert!(matches!(
                picture,
                crate::alpha_picture::DecodedPicture::StraightAlpha(_)
            ));
            let MediaDescriptor::Image {
                width,
                height,
                rgba_sha256,
                alpha: Some(alpha),
                ..
            } = descriptor
            else {
                panic!("independent alpha descriptor expected")
            };
            let facts = &declared["facts"];
            assert_eq!(width as u64, facts["width"].as_u64().unwrap());
            assert_eq!(height as u64, facts["height"].as_u64().unwrap());
            assert_eq!(rgba_sha256.as_str(), facts["rgbaSha256"].as_str().unwrap());
            assert_eq!(
                alpha.alpha_sha256.as_str(),
                facts["alphaSha256"].as_str().unwrap()
            );
            assert_eq!(u64::from(alpha.minimum), facts["minimum"].as_u64().unwrap());
            assert_eq!(u64::from(alpha.maximum), facts["maximum"].as_u64().unwrap());
            assert_eq!(
                alpha.nonzero_pixels,
                facts["nonzeroPixels"].as_u64().unwrap()
            );
            assert_eq!(
                alpha.nonopaque_pixels,
                facts["nonopaquePixels"].as_u64().unwrap()
            );
        }
    }

    #[test]
    fn alpha_decode_observes_cancellation_at_row_boundaries() {
        let mut bytes = Vec::new();
        let mut encoder = png::Encoder::new(&mut bytes, 2, 2);
        encoder.set_color(png::ColorType::Rgba);
        encoder.set_depth(png::BitDepth::Eight);
        let mut writer = encoder.write_header().unwrap();
        writer
            .write_image_data(&[1, 2, 3, 0, 4, 5, 6, 255, 7, 8, 9, 128, 10, 11, 12, 64])
            .unwrap();
        writer.finish().unwrap();
        let mut checks = 0;
        let result = decode_cancellable(&bytes, || {
            checks += 1;
            if checks == 3 {
                Err(StudioError::new("cancelled_test", "stop"))
            } else {
                Ok(())
            }
        });
        let failure = match result {
            Err(failure) => failure,
            Ok(_) => panic!("decode cancellation expected"),
        };
        assert_eq!(failure.code, "cancelled_test");
    }

    #[test]
    fn animated_png_is_rejected_before_a_static_hold_can_hide_its_timing() {
        let mut bytes = Vec::new();
        let mut encoder = png::Encoder::new(&mut bytes, 2, 1);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_animated(2, 0).unwrap();
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[0, 0, 0, 255, 255, 255]).unwrap();
        writer.write_image_data(&[255, 0, 0, 0, 0, 255]).unwrap();
        writer.finish().unwrap();
        assert_eq!(
            decode(&bytes).err().unwrap().code,
            "unsupported_image_animation"
        );
    }

    #[test]
    fn trailers_and_concatenated_images_are_rejected() {
        let valid = png(
            png::ColorType::Rgb,
            png::BitDepth::Eight,
            &[1, 2, 3, 4, 5, 6],
        );
        let mut trailer = valid.clone();
        trailer.extend_from_slice(b"uninterpreted trailer");
        assert_eq!(decode(&trailer).err().unwrap().code, "invalid_image");
        let mut concatenated = valid.clone();
        concatenated.extend_from_slice(&valid);
        assert_eq!(decode(&concatenated).err().unwrap().code, "invalid_image");
    }

    #[test]
    fn lower_depth_gray_and_indexed_samples_expand_without_precision_loss() {
        let gray = png(
            png::ColorType::Grayscale,
            png::BitDepth::One,
            &[0b0100_0000],
        );
        assert_eq!(opaque(&gray).bytes, [0, 0, 0, 255, 255, 255, 255, 255]);
        let mut bytes = Vec::new();
        let mut encoder = png::Encoder::new(&mut bytes, 2, 1);
        encoder.set_color(png::ColorType::Indexed);
        encoder.set_depth(png::BitDepth::One);
        encoder.set_palette(vec![255, 0, 17, 9, 40, 255]);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[0b0100_0000]).unwrap();
        writer.finish().unwrap();
        assert_eq!(opaque(&bytes).bytes, [17, 0, 255, 255, 255, 40, 9, 255]);
    }

    #[test]
    fn corrupt_ancillary_chunk_crc_is_not_silently_recovered() {
        let mut bytes = Vec::new();
        let mut encoder = png::Encoder::new(&mut bytes, 2, 1);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[1, 2, 3, 4, 5, 6]).unwrap();
        writer
            .write_chunk(png::chunk::tEXt, b"Comment\0valid ancillary text")
            .unwrap();
        writer.finish().unwrap();
        assert!(decode(&bytes).is_ok());
        let start = bytes.windows(4).position(|part| part == b"tEXt").unwrap();
        let length = u32::from_be_bytes(bytes[start - 4..start].try_into().unwrap()) as usize;
        bytes[start + 4 + length..start + 8 + length].fill(0);
        assert_eq!(decode(&bytes).err().unwrap().code, "invalid_image");
    }
}
