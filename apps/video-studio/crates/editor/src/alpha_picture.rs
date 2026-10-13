use serde::Serialize;

use crate::composition::{Bounds, LayerObservation, Mapping};
use crate::{ContentHash, ImageAlphaV1, Result, StudioError, pixels};

const UNORM16_MAX: u128 = 65_535;
const Q16_ONE: u128 = 65_536;
const Q32_ONE: u128 = Q16_ONE * Q16_ONE;

pub(crate) enum DecodedPicture {
    LegacyOpaque(pixels::Pixels),
    StraightAlpha(StraightRgba8),
}

impl DecodedPicture {
    pub(crate) fn into_legacy_opaque(self) -> Result<pixels::Pixels> {
        match self {
            Self::LegacyOpaque(pixels) => Ok(pixels),
            Self::StraightAlpha(_) => Err(StudioError::new(
                "unsupported_image_alpha",
                "Legacy picture execution cannot flatten a transparent source",
            )),
        }
    }
}

pub(crate) struct StraightRgba8 {
    width: u32,
    height: u32,
    rgba: Vec<u8>,
}

impl StraightRgba8 {
    pub(crate) fn new(width: u32, height: u32, rgba: Vec<u8>) -> Result<Self> {
        if rgba.len() != pixels::extent(width, height)?
            || rgba.chunks_exact(4).all(|pixel| pixel[3] == 255)
        {
            return Err(StudioError::new(
                "invalid_image_alpha",
                "Straight alpha pixels require a non-opaque checked RGBA8 extent",
            ));
        }
        Ok(Self {
            width,
            height,
            rgba,
        })
    }

    pub(crate) fn width(&self) -> u32 {
        self.width
    }

    pub(crate) fn height(&self) -> u32 {
        self.height
    }

    fn pixel(&self, x: u32, y: u32) -> Result<[u8; 4]> {
        if x >= self.width || y >= self.height {
            return Err(alpha_error(
                "Straight alpha sample exceeds its source coordinates",
            ));
        }
        let start = usize::try_from(
            (u64::from(y) * u64::from(self.width) + u64::from(x))
                .checked_mul(4)
                .ok_or_else(|| alpha_error("Straight alpha pixel offset overflow"))?,
        )
        .map_err(|_| alpha_error("Straight alpha pixel offset exceeds address space"))?;
        let pixel = self
            .rgba
            .get(start..start + 4)
            .ok_or_else(|| alpha_error("Straight alpha sample exceeds its source extent"))?;
        Ok([pixel[0], pixel[1], pixel[2], pixel[3]])
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
#[repr(C)]
pub(crate) struct PremulBgra16 {
    pub(crate) b: u16,
    pub(crate) g: u16,
    pub(crate) r: u16,
    pub(crate) coverage: u16,
}

const _: [(); 8] = [(); std::mem::size_of::<PremulBgra16>()];

pub(crate) struct AlphaRaster16 {
    pub(crate) bounds: Bounds,
    pixels: Vec<PremulBgra16>,
    positive_samples: u64,
}

impl AlphaRaster16 {
    pub(crate) fn has_positive_samples(&self) -> bool {
        self.positive_samples != 0
    }
}

#[derive(Serialize)]
#[serde(deny_unknown_fields)]
struct SourceAlphaIdentityV1<'a> {
    schema: u32,
    asset: &'a ContentHash,
    rgba_sha256: &'a ContentHash,
    alpha: &'a ImageAlphaV1,
}

pub(crate) fn source_alpha_id(
    asset: &ContentHash,
    rgba_sha256: &ContentHash,
    alpha: &ImageAlphaV1,
) -> Result<ContentHash> {
    ContentHash::document(&SourceAlphaIdentityV1 {
        schema: 1,
        asset,
        rgba_sha256,
        alpha,
    })
}

pub(crate) fn raster_bytes(bounds: &Bounds) -> Result<u64> {
    let bytes = u64::from(bounds.width)
        .checked_mul(u64::from(bounds.height))
        .and_then(|pixels| {
            pixels.checked_mul(u64::try_from(std::mem::size_of::<PremulBgra16>()).ok()?)
        });
    match bytes {
        Some(bytes) if bytes > 0 && bytes <= pixels::MAX_OWNED_FRAME_BYTES => Ok(bytes),
        _ => Err(StudioError::new(
            "unsupported_alpha_raster_extent",
            "Each owned premultiplied alpha raster must fit within 128 MiB",
        )),
    }
}

fn premultiply(channel: u8, alpha: u8) -> u16 {
    let channel = u128::from(channel) * 257;
    let alpha = u128::from(alpha) * 257;
    ((channel * alpha + UNORM16_MAX / 2) / UNORM16_MAX) as u16
}

fn sample_value(values: [u16; 4], weights: [u64; 4]) -> Result<u16> {
    let sum = values
        .into_iter()
        .zip(weights)
        .try_fold(0u128, |sum, (value, weight)| {
            sum.checked_add(u128::from(value) * u128::from(weight))
        })
        .ok_or_else(|| alpha_error("Premultiplied bilinear sample overflow"))?;
    u16::try_from((sum + Q32_ONE / 2) / Q32_ONE)
        .map_err(|_| alpha_error("Premultiplied bilinear sample exceeds UNORM16"))
}

pub(crate) fn sample_cancellable(
    source: &StraightRgba8,
    mapping: &Mapping,
    bounds: Option<&Bounds>,
    mut check: impl FnMut() -> Result<()>,
) -> Result<Option<AlphaRaster16>> {
    check()?;
    mapping.validate_source_extent(source.width, source.height)?;
    let Some(bounds) = bounds else {
        return Ok(None);
    };
    mapping.validate_requested_bounds(bounds)?;
    let bytes = raster_bytes(bounds)?;
    let count = usize::try_from(bytes / 8)
        .map_err(|_| alpha_error("Alpha raster extent exceeds address space"))?;
    let mut pixels = vec![PremulBgra16::default(); count];
    let mut positive_samples = 0u64;
    for y in 0..bounds.height {
        check()?;
        for x in 0..bounds.width {
            let footprint = mapping.bilinear_footprint_q16(bounds.x + x, bounds.y + y)?;
            let taps = [
                source.pixel(footprint.x0, footprint.y0)?,
                source.pixel(footprint.x1, footprint.y0)?,
                source.pixel(footprint.x0, footprint.y1)?,
                source.pixel(footprint.x1, footprint.y1)?,
            ];
            let weights = footprint.weights();
            let coverage = sample_value(taps.map(|pixel| u16::from(pixel[3]) * 257), weights)?;
            let sample_channel = |channel: usize| {
                sample_value(
                    taps.map(|pixel| premultiply(pixel[channel], pixel[3])),
                    weights,
                )
            };
            let pixel = PremulBgra16 {
                b: sample_channel(2)?,
                g: sample_channel(1)?,
                r: sample_channel(0)?,
                coverage,
            };
            if pixel.b > coverage || pixel.g > coverage || pixel.r > coverage {
                return Err(alpha_error(
                    "Premultiplied channel exceeds sampled intrinsic coverage",
                ));
            }
            positive_samples += u64::from(coverage != 0);
            pixels[(y * bounds.width + x) as usize] = pixel;
        }
    }
    Ok(Some(AlphaRaster16 {
        bounds: bounds.clone(),
        pixels,
        positive_samples,
    }))
}

pub(crate) fn blend_cancellable(
    canvas: &mut pixels::Pixels,
    raster: &AlphaRaster16,
    observation: &LayerObservation,
    check: impl FnMut() -> Result<()>,
) -> Result<u64> {
    if observation.effective_bounds.as_ref() != Some(&raster.bounds) {
        return Err(alpha_error(
            "Premultiplied alpha raster differs from its resolved observation",
        ));
    }
    blend_with_weights(
        canvas,
        raster,
        |x, y| crate::composition::layer_weight(observation, x, y),
        check,
    )
}

fn blend_with_weights(
    canvas: &mut pixels::Pixels,
    raster: &AlphaRaster16,
    weight_at: impl Fn(u32, u32) -> Result<u32>,
    mut check: impl FnMut() -> Result<()>,
) -> Result<u64> {
    check()?;
    let bounds = &raster.bounds;
    if canvas.bytes.len() != pixels::extent(canvas.width, canvas.height)?
        || bounds
            .x
            .checked_add(bounds.width)
            .is_none_or(|end| end > canvas.width)
        || bounds
            .y
            .checked_add(bounds.height)
            .is_none_or(|end| end > canvas.height)
        || raster.pixels.len() as u64 != u64::from(bounds.width) * u64::from(bounds.height)
    {
        return Err(alpha_error(
            "Premultiplied alpha raster differs from its canvas observation",
        ));
    }
    let denominator = UNORM16_MAX * Q16_ONE;
    let mut positive = 0u64;
    for y in 0..bounds.height {
        check()?;
        for x in 0..bounds.width {
            let input = (y * bounds.width + x) as usize;
            let output = (((bounds.y + y) * canvas.width + bounds.x + x) * 4) as usize;
            let source = raster.pixels[input];
            if source.b > source.coverage
                || source.g > source.coverage
                || source.r > source.coverage
            {
                return Err(alpha_error(
                    "Premultiplied alpha raster contains an invalid contribution",
                ));
            }
            let weight = u128::from(weight_at(bounds.x + x, bounds.y + y)?);
            if weight > Q16_ONE {
                return Err(alpha_error("Layer weight exceeds Q16 unity"));
            }
            let covered = u128::from(source.coverage) * weight;
            if covered > denominator {
                return Err(alpha_error("Effective alpha coverage exceeds unity"));
            }
            positive += u64::from(covered != 0);
            for (channel, premultiplied) in [source.b, source.g, source.r].into_iter().enumerate() {
                let lower = u128::from(canvas.bytes[output + channel]);
                let numerator = 255u128
                    .checked_mul(u128::from(premultiplied))
                    .and_then(|value| value.checked_mul(weight))
                    .and_then(|value| {
                        lower
                            .checked_mul(denominator - covered)
                            .and_then(|lower| value.checked_add(lower))
                    })
                    .ok_or_else(|| alpha_error("Alpha blend arithmetic overflow"))?;
                canvas.bytes[output + channel] =
                    u8::try_from((numerator + denominator / 2) / denominator)
                        .map_err(|_| alpha_error("Alpha blend result exceeds eight bits"))?;
            }
            canvas.bytes[output + 3] = 255;
        }
    }
    Ok(positive)
}

fn alpha_error(detail: impl Into<String>) -> StudioError {
    StudioError::new("invalid_alpha_picture", detail)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Framing, NormalizedCrop, Opacity, PictureFit, PicturePlacement, PixelRect};

    fn independent_fixture_root() -> std::path::PathBuf {
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/alpha")
    }

    fn decoded_alpha(path: &std::path::Path) -> StraightRgba8 {
        let bytes = std::fs::read(path).unwrap();
        let descriptor = crate::image::probe(path).unwrap();
        let asset = crate::StoredAsset {
            hash: ContentHash::bytes(&bytes),
            bytes: bytes.len() as u64,
            origin: crate::Origin::Imported {
                external_source: path.display().to_string(),
                role: "independent-alpha-vector".into(),
            },
            descriptor,
            backend: "independent test binding".into(),
            measurement: None,
        };
        match crate::image::decode_picture_asset(path, &asset).unwrap() {
            DecodedPicture::StraightAlpha(pixels) => pixels,
            DecodedPicture::LegacyOpaque(_) => panic!("alpha fixture decoded as opaque"),
        }
    }

    fn fraction(value: &serde_json::Value) -> f64 {
        if let Some(value) = value.as_f64() {
            return value;
        }
        let value = value.as_str().unwrap();
        let Some((numerator, denominator)) = value.split_once('/') else {
            return value.parse().unwrap();
        };
        numerator.parse::<f64>().unwrap() / denominator.parse::<f64>().unwrap()
    }

    fn mapping(source_width: u32, destination_width: u32) -> Mapping {
        Mapping::new(
            source_width,
            1,
            Some(&Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    x: 0.0,
                    y: 0.0,
                    width: 1.0,
                    height: 1.0,
                },
            }),
            &PicturePlacement {
                destination: PixelRect {
                    x: 0,
                    y: 0,
                    width: destination_width,
                    height: 1,
                },
                opacity: Opacity::new(1.0).unwrap(),
            },
            destination_width,
            1,
        )
        .unwrap()
    }

    #[test]
    fn representation_is_eight_bytes_and_hidden_rgb_does_not_bleed() {
        assert_eq!(std::mem::size_of::<PremulBgra16>(), 8);
        let source = StraightRgba8::new(2, 1, vec![255, 0, 0, 0, 0, 0, 255, 255]).unwrap();
        let mapping = mapping(2, 1);
        let bounds = mapping.bounds.as_ref().unwrap();
        let raster = sample_cancellable(&source, &mapping, Some(bounds), || Ok(()))
            .unwrap()
            .unwrap();
        assert_eq!(raster.pixels.len(), 1);
        assert_eq!(raster.pixels[0].r, 0);
        assert_eq!(raster.pixels[0].g, 0);
        assert_eq!(raster.pixels[0].b, 32_768);
        assert_eq!(raster.pixels[0].coverage, 32_768);
    }

    #[test]
    fn alpha_raster_limit_is_checked_before_allocation() {
        let valid = Bounds {
            x: 0,
            y: 0,
            width: 4096,
            height: 4096,
        };
        assert_eq!(raster_bytes(&valid).unwrap(), pixels::MAX_OWNED_FRAME_BYTES);
        let invalid = Bounds {
            width: 4097,
            ..valid
        };
        assert_eq!(
            raster_bytes(&invalid).unwrap_err().code,
            "unsupported_alpha_raster_extent"
        );
    }

    #[test]
    fn source_coordinates_and_mapping_extent_cannot_alias_a_later_row() {
        let source = StraightRgba8::new(
            2,
            2,
            vec![1, 2, 3, 0, 4, 5, 6, 255, 7, 8, 9, 255, 10, 11, 12, 255],
        )
        .unwrap();
        assert_eq!(
            source.pixel(2, 0).unwrap_err().code,
            "invalid_alpha_picture"
        );
        assert_eq!(
            source.pixel(0, 2).unwrap_err().code,
            "invalid_alpha_picture"
        );
        let mapping = mapping(4, 4);
        assert_eq!(
            sample_cancellable(&source, &mapping, mapping.bounds.as_ref(), || Ok(()))
                .err()
                .unwrap()
                .code,
            "unsupported_picture_alpha"
        );
    }

    fn observation(
        width: u32,
        opacity: f64,
        mask: Option<crate::mask::ResolvedPictureMask>,
    ) -> LayerObservation {
        let placement = PicturePlacement {
            destination: PixelRect {
                x: 0,
                y: 0,
                width,
                height: 1,
            },
            opacity: Opacity::new(opacity).unwrap(),
        };
        LayerObservation {
            placement: crate::motion::ResolvedPlacement::from_static(&placement).unwrap(),
            mask,
            picture_window: Some(crate::composition::PictureWindow {
                x: 0,
                y: 0,
                width,
                height: 1,
            }),
            effective_bounds: Some(Bounds {
                x: 0,
                y: 0,
                width,
                height: 1,
            }),
        }
    }

    #[test]
    fn intrinsic_alpha_mask_opacity_and_track_order_have_exact_bytes() {
        let source = StraightRgba8::new(1, 1, vec![200, 100, 50, 128]).unwrap();
        let mapping = mapping(1, 1);
        let bounds = mapping.bounds.as_ref().unwrap();
        let raster = sample_cancellable(&source, &mapping, Some(bounds), || Ok(()))
            .unwrap()
            .unwrap();
        let mask = crate::mask::ResolvedPictureMask {
            axis: crate::MaskAxis::Horizontal,
            progress_q16: crate::MaskProgressQ16::new(32_768).unwrap(),
            inverted: false,
        };
        let mut canvas = pixels::Pixels {
            width: 1,
            height: 1,
            bytes: vec![10, 20, 30, 255],
        };
        assert_eq!(
            blend_cancellable(
                &mut canvas,
                &raster,
                &observation(1, 1.0, Some(mask)),
                || Ok(())
            )
            .unwrap(),
            1
        );
        assert_eq!(canvas.bytes, [20, 40, 73, 255]);

        let red = StraightRgba8::new(1, 1, vec![255, 0, 0, 128]).unwrap();
        let blue = StraightRgba8::new(1, 1, vec![0, 0, 255, 128]).unwrap();
        let red = sample_cancellable(&red, &mapping, Some(bounds), || Ok(()))
            .unwrap()
            .unwrap();
        let blue = sample_cancellable(&blue, &mapping, Some(bounds), || Ok(()))
            .unwrap()
            .unwrap();
        let full = observation(1, 1.0, None);
        let mut red_then_blue = pixels::Pixels {
            width: 1,
            height: 1,
            bytes: vec![0, 0, 0, 255],
        };
        blend_cancellable(&mut red_then_blue, &red, &full, || Ok(())).unwrap();
        blend_cancellable(&mut red_then_blue, &blue, &full, || Ok(())).unwrap();
        assert_eq!(red_then_blue.bytes, [128, 0, 64, 255]);
        let mut blue_then_red = pixels::Pixels {
            width: 1,
            height: 1,
            bytes: vec![0, 0, 0, 255],
        };
        blend_cancellable(&mut blue_then_red, &blue, &full, || Ok(())).unwrap();
        blend_cancellable(&mut blue_then_red, &red, &full, || Ok(())).unwrap();
        assert_eq!(blue_then_red.bytes, [64, 0, 128, 255]);
    }

    #[test]
    fn alpha_sampling_and_blending_check_cancellation_per_row() {
        let source = StraightRgba8::new(
            2,
            2,
            vec![1, 2, 3, 1, 4, 5, 6, 2, 7, 8, 9, 3, 10, 11, 12, 4],
        )
        .unwrap();
        let mapping = Mapping::new(
            2,
            2,
            None,
            &PicturePlacement {
                destination: PixelRect {
                    x: 0,
                    y: 0,
                    width: 2,
                    height: 2,
                },
                opacity: Opacity::new(1.0).unwrap(),
            },
            2,
            2,
        )
        .unwrap();
        let bounds = mapping.bounds.as_ref().unwrap();
        let mut checks = 0;
        let sampled = sample_cancellable(&source, &mapping, Some(bounds), || {
            checks += 1;
            if checks == 3 {
                Err(StudioError::new("cancelled_test", "stop"))
            } else {
                Ok(())
            }
        });
        let failure = match sampled {
            Err(failure) => failure,
            Ok(_) => panic!("sample cancellation expected"),
        };
        assert_eq!(failure.code, "cancelled_test");

        let raster = sample_cancellable(&source, &mapping, Some(bounds), || Ok(()))
            .unwrap()
            .unwrap();
        let placement = PicturePlacement {
            destination: PixelRect {
                x: 0,
                y: 0,
                width: 2,
                height: 2,
            },
            opacity: Opacity::new(1.0).unwrap(),
        };
        let observation = LayerObservation {
            placement: crate::motion::ResolvedPlacement::from_static(&placement).unwrap(),
            mask: None,
            picture_window: None,
            effective_bounds: Some(bounds.clone()),
        };
        let mut canvas = pixels::Pixels {
            width: 2,
            height: 2,
            bytes: [0, 0, 0, 255].repeat(4),
        };
        let mut checks = 0;
        let blended = blend_cancellable(&mut canvas, &raster, &observation, || {
            checks += 1;
            if checks == 3 {
                Err(StudioError::new("cancelled_test", "stop"))
            } else {
                Ok(())
            }
        });
        assert_eq!(blended.unwrap_err().code, "cancelled_test");
    }

    #[test]
    fn independent_a03_vectors_match_every_pixel_and_crop_clamp() {
        let root = independent_fixture_root();
        let manifest_bytes = std::fs::read(root.join("alpha-fixture-a03.json")).unwrap();
        assert_eq!(
            ContentHash::bytes(&manifest_bytes).as_str(),
            "afdfb1848940b9063640871bf834c90c29ba2a2d4049811843514621dccb9ddc"
        );
        let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();
        let primary = decoded_alpha(&root.join("alpha-primary-a01.png"));
        let transparent = decoded_alpha(&root.join("alpha-transparent-a01.png"));
        assert_eq!((primary.width(), primary.height()), (64, 48));
        assert_eq!((transparent.width(), transparent.height()), (16, 12));

        for case in manifest["cases"].as_array().unwrap() {
            let width = case["canvas"]["width"].as_u64().unwrap() as u32;
            let height = case["canvas"]["height"].as_u64().unwrap() as u32;
            let background: Vec<u8> =
                serde_json::from_value(case["canvas"]["background"].clone()).unwrap();
            let mut canvas = pixels::Pixels {
                width,
                height,
                bytes: background.repeat((width * height) as usize),
            };
            let mut positive = 0u64;
            for layer in case["layers"].as_array().unwrap() {
                let destination = &layer["destination"];
                let placement = PicturePlacement {
                    destination: PixelRect {
                        x: destination["x"].as_i64().unwrap() as i32,
                        y: destination["y"].as_i64().unwrap() as i32,
                        width: destination["width"].as_u64().unwrap() as u32,
                        height: destination["height"].as_u64().unwrap() as u32,
                    },
                    opacity: Opacity::new(fraction(&layer["opacity"])).unwrap(),
                };
                let crop = &layer["framing"]["crop"];
                let framing = Framing {
                    fit: match layer["framing"]["fit"].as_str().unwrap() {
                        "contain" => PictureFit::Contain,
                        "cover" => PictureFit::Cover,
                        "stretch" => PictureFit::Stretch,
                        value => panic!("unexpected fit {value}"),
                    },
                    crop: NormalizedCrop {
                        x: fraction(&crop["x"]),
                        y: fraction(&crop["y"]),
                        width: fraction(&crop["width"]),
                        height: fraction(&crop["height"]),
                    },
                };
                let source = layer["source"].as_str().unwrap();
                if source == "lower_base" {
                    let declared = &manifest["sources"][source];
                    let source = pixels::Pixels {
                        width: declared["width"].as_u64().unwrap() as u32,
                        height: declared["height"].as_u64().unwrap() as u32,
                        bytes: serde_json::from_value(declared["bgra"].clone()).unwrap(),
                    };
                    let mapping = Mapping::new(
                        source.width,
                        source.height,
                        Some(&framing),
                        &placement,
                        width,
                        height,
                    )
                    .unwrap();
                    if let Some(raster) = mapping.rasterize(&source).unwrap() {
                        let count = u64::from(placement.opacity.weight() != 0)
                            * u64::from(raster.bounds.width)
                            * u64::from(raster.bounds.height);
                        crate::composition::blend(&mut canvas, &raster, placement.opacity).unwrap();
                        positive += count;
                    }
                    continue;
                }
                let source = match source {
                    "alpha_primary" => &primary,
                    "alpha_transparent" => &transparent,
                    value => panic!("unexpected alpha source {value}"),
                };
                let mapping = Mapping::new(
                    source.width(),
                    source.height(),
                    Some(&framing),
                    &placement,
                    width,
                    height,
                )
                .unwrap();
                let Some(bounds) = mapping.bounds.as_ref() else {
                    continue;
                };
                let raster = sample_cancellable(source, &mapping, Some(bounds), || Ok(()))
                    .unwrap()
                    .unwrap();
                let count = if layer["mask"].is_null() {
                    let observation = LayerObservation {
                        placement: crate::motion::ResolvedPlacement::from_static(&placement)
                            .unwrap(),
                        mask: None,
                        picture_window: None,
                        effective_bounds: Some(bounds.clone()),
                    };
                    blend_cancellable(&mut canvas, &raster, &observation, || Ok(())).unwrap()
                } else {
                    let mask = &layer["mask"];
                    assert_eq!(mask["kind"], "explicit_q16");
                    let mask_width = mask["width"].as_u64().unwrap() as u32;
                    let mask_height = mask["height"].as_u64().unwrap() as u32;
                    let values: Vec<u32> = serde_json::from_value(mask["values"].clone()).unwrap();
                    assert_eq!(values.len(), (mask_width * mask_height) as usize);
                    let opacity = u64::from(placement.opacity.weight());
                    blend_with_weights(
                        &mut canvas,
                        &raster,
                        |x, y| {
                            let mask = u64::from(values[(y * mask_width + x) as usize]);
                            Ok(((opacity * mask + 32_768) / 65_536) as u32)
                        },
                        || Ok(()),
                    )
                    .unwrap()
                };
                positive += count;
                let expected_layer = case["expected"]["layers"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .find(|expected| expected["id"] == layer["id"])
                    .unwrap();
                assert_eq!(
                    count,
                    expected_layer["positiveContributionPixels"]
                        .as_u64()
                        .unwrap(),
                    "{} / {}",
                    case["name"].as_str().unwrap(),
                    layer["id"].as_str().unwrap()
                );
            }
            let expected: Vec<u8> =
                serde_json::from_value(case["expected"]["bgra"].clone()).unwrap();
            assert_eq!(canvas.bytes, expected, "{}", case["name"].as_str().unwrap());
            assert_eq!(
                ContentHash::bytes(&canvas.bytes).as_str(),
                case["expected"]["bgraSha256"].as_str().unwrap()
            );
            assert_eq!(
                positive,
                case["expected"]["positiveContributionPixels"]
                    .as_u64()
                    .unwrap()
            );
            assert!(canvas.bytes.chunks_exact(4).all(|pixel| pixel[3] == 255));
        }
    }
}
