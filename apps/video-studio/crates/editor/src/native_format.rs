use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};
use std::ptr::NonNull;
use std::sync::mpsc;
use std::time::Duration;
use std::time::Instant;

use block2::RcBlock;
use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{
    AVAssetWriter, AVAssetWriterInput, AVAssetWriterInputPixelBufferAdaptor, AVAssetWriterStatus,
    AVFileTypeMPEG4, AVFileTypeQuickTimeMovie, AVMediaTypeAudio, AVMediaTypeVideo,
    AVVideoAverageBitRateKey, AVVideoColorPrimaries_ITU_R_709_2, AVVideoColorPrimariesKey,
    AVVideoColorPropertiesKey, AVVideoTransferFunction_ITU_R_709_2, AVVideoTransferFunctionKey,
    AVVideoYCbCrMatrix_ITU_R_709_2, AVVideoYCbCrMatrixKey,
};
use objc2_core_audio_types::AudioStreamBasicDescription;
use objc2_core_foundation::{CFRetained, CFString};
use objc2_core_media::{
    CMAudioFormatDescriptionCreate, CMBlockBuffer, CMFormatDescription, CMSampleBuffer,
    CMSampleTimingInfo, CMTime, kCMFormatDescriptionExtension_ColorPrimaries,
    kCMFormatDescriptionExtension_TransferFunction, kCMFormatDescriptionExtension_YCbCrMatrix,
    kCMTimeInvalid,
};
use objc2_core_video::{
    CVAttachmentMode, CVPixelBuffer, kCVImageBufferColorPrimaries_ITU_R_709_2,
    kCVImageBufferColorPrimariesKey, kCVImageBufferTransferFunction_ITU_R_709_2,
    kCVImageBufferTransferFunctionKey, kCVImageBufferYCbCrMatrix_ITU_R_709_2,
    kCVImageBufferYCbCrMatrixKey, kCVPixelFormatType_32BGRA,
};
use objc2_foundation::{NSDictionary, NSNumber, NSString, NSURL};
use serde::{Deserialize, Serialize};

use crate::{
    ContentHash, MovieProfile, NativeColorTupleEvidence, NativeMeasurements,
    NativeVideoColorEvidence, Result, Settings, StudioError,
};

fn error(detail: impl Into<String>) -> StudioError {
    StudioError::new("native_format_error", detail)
}
fn number(value: u32) -> Retained<AnyObject> {
    unsafe { Retained::cast_unchecked(NSNumber::new_u32(value)) }
}
fn text(value: &str) -> Retained<AnyObject> {
    unsafe { Retained::cast_unchecked(NSString::from_str(value)) }
}
fn dictionary(
    values: Vec<(&str, Retained<AnyObject>)>,
) -> Retained<NSDictionary<NSString, AnyObject>> {
    let owned: Vec<_> = values
        .iter()
        .map(|(key, _)| NSString::from_str(key))
        .collect();
    let keys: Vec<_> = owned.iter().map(|key| &**key).collect();
    let values: Vec<_> = values.iter().map(|(_, value)| &**value).collect();
    NSDictionary::from_slices(&keys, &values)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum StagePayloadName {
    Mp4,
    Mov,
}
impl StagePayloadName {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::Mp4 => "movie.mp4",
            Self::Mov => "movie.mov",
        }
    }
}

#[derive(Clone, Copy)]
enum Format {
    H264 { video: u32, audio: u32 },
    MasterV1,
    MasterV2,
}
#[derive(Clone, Copy)]
pub(crate) struct NativeFormatContract(Format);

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct FourCc([u8; 4]);
impl TryFrom<String> for FourCc {
    type Error = StudioError;
    fn try_from(value: String) -> Result<Self> {
        let bytes: [u8; 4] = value
            .as_bytes()
            .try_into()
            .map_err(|_| error("FourCC must contain four bytes"))?;
        if !bytes.iter().all(|byte| (32..=126).contains(byte)) {
            return Err(error("FourCC must contain printable ASCII"));
        }
        Ok(Self(bytes))
    }
}
impl From<FourCc> for String {
    fn from(value: FourCc) -> Self {
        String::from_utf8(value.0.to_vec()).expect("validated ASCII")
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeFormatEvidence {
    pub major_brand: FourCc,
    pub compatible_brands: Vec<FourCc>,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PcmEncodingEvidence {
    pub format_id: u32,
    pub format_flags: u32,
    pub bits_per_channel: u32,
    pub bytes_per_frame: u32,
    pub bytes_per_packet: u32,
    pub frames_per_packet: u32,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Pcm24Comparison {
    pub sample_frames: u64,
    pub maximum_code_delta: u32,
}

const REC709_NAME: &str = "ITU_R_709_2";

fn rec709_tuple() -> NativeColorTupleEvidence {
    NativeColorTupleEvidence {
        color_primaries: REC709_NAME.into(),
        transfer_function: REC709_NAME.into(),
        y_cb_cr_matrix: REC709_NAME.into(),
    }
}

fn require_rec709_tuple(
    color_primaries: Option<String>,
    transfer_function: Option<String>,
    y_cb_cr_matrix: Option<String>,
    scope: &str,
) -> Result<NativeColorTupleEvidence> {
    let observed = NativeColorTupleEvidence {
        color_primaries: color_primaries
            .ok_or_else(|| error(format!("{scope} color primaries are missing")))?,
        transfer_function: transfer_function
            .ok_or_else(|| error(format!("{scope} transfer function is missing")))?,
        y_cb_cr_matrix: y_cb_cr_matrix
            .ok_or_else(|| error(format!("{scope} YCbCr matrix is missing")))?,
    };
    if observed != rec709_tuple() {
        return Err(error(format!(
            "{scope} color tuple differs from the closed Rec.709 profile"
        )));
    }
    Ok(observed)
}

fn format_extension(description: &CMFormatDescription, key: &CFString) -> Option<String> {
    let value = unsafe { description.extension(key) }?;
    value
        .downcast::<CFString>()
        .ok()
        .map(|value| value.to_string())
}

fn buffer_attachment(image: &CVPixelBuffer, key: &CFString, scope: &str) -> Result<String> {
    let mut mode = CVAttachmentMode::ShouldNotPropagate;
    let value = unsafe { image.attachment(key, &mut mode) }
        .ok_or_else(|| error(format!("{scope} attachment is missing")))?;
    let value = value
        .downcast::<CFString>()
        .map_err(|_| error(format!("{scope} attachment is not a string")))?;
    if mode.0 != CVAttachmentMode::ShouldPropagate.0 {
        return Err(error(format!("{scope} attachment does not propagate")));
    }
    Ok(value.to_string())
}

fn observe_buffer_rec709(image: &CVPixelBuffer, scope: &str) -> Result<NativeColorTupleEvidence> {
    require_rec709_tuple(
        Some(buffer_attachment(
            image,
            unsafe { kCVImageBufferColorPrimariesKey },
            &format!("{scope} color primaries"),
        )?),
        Some(buffer_attachment(
            image,
            unsafe { kCVImageBufferTransferFunctionKey },
            &format!("{scope} transfer function"),
        )?),
        Some(buffer_attachment(
            image,
            unsafe { kCVImageBufferYCbCrMatrixKey },
            &format!("{scope} YCbCr matrix"),
        )?),
        scope,
    )
}

fn rec709_video_properties() -> Result<Retained<AnyObject>> {
    let primary_key = unsafe { AVVideoColorPrimariesKey }
        .ok_or_else(|| error("AVVideoColorPrimariesKey is unavailable"))?;
    let transfer_key = unsafe { AVVideoTransferFunctionKey }
        .ok_or_else(|| error("AVVideoTransferFunctionKey is unavailable"))?;
    let matrix_key = unsafe { AVVideoYCbCrMatrixKey }
        .ok_or_else(|| error("AVVideoYCbCrMatrixKey is unavailable"))?;
    let primary = unsafe { AVVideoColorPrimaries_ITU_R_709_2 }
        .ok_or_else(|| error("AVVideoColorPrimaries_ITU_R_709_2 is unavailable"))?;
    let transfer = unsafe { AVVideoTransferFunction_ITU_R_709_2 }
        .ok_or_else(|| error("AVVideoTransferFunction_ITU_R_709_2 is unavailable"))?;
    let matrix = unsafe { AVVideoYCbCrMatrix_ITU_R_709_2 }
        .ok_or_else(|| error("AVVideoYCbCrMatrix_ITU_R_709_2 is unavailable"))?;
    let properties = NSDictionary::from_slices(
        &[primary_key, transfer_key, matrix_key],
        &[primary, transfer, matrix],
    );
    Ok(unsafe { Retained::cast_unchecked(properties) })
}

fn attach_input_rec709(image: &CVPixelBuffer) -> Result<()> {
    unsafe {
        image.set_attachment(
            kCVImageBufferColorPrimariesKey,
            kCVImageBufferColorPrimaries_ITU_R_709_2,
            CVAttachmentMode::ShouldPropagate,
        );
        image.set_attachment(
            kCVImageBufferTransferFunctionKey,
            kCVImageBufferTransferFunction_ITU_R_709_2,
            CVAttachmentMode::ShouldPropagate,
        );
        image.set_attachment(
            kCVImageBufferYCbCrMatrixKey,
            kCVImageBufferYCbCrMatrix_ITU_R_709_2,
            CVAttachmentMode::ShouldPropagate,
        );
    }
    observe_buffer_rec709(image, "Writer input")?;
    Ok(())
}

impl NativeFormatContract {
    pub(crate) fn for_profile(profile: &MovieProfile) -> Result<Self> {
        Ok(Self(match *profile {
            MovieProfile::H264AacMp4 {
                video_bitrate,
                audio_bitrate,
            } => {
                if !(100000..=100000000).contains(&video_bitrate)
                    || !(64000..=512000).contains(&audio_bitrate)
                {
                    return Err(StudioError::new(
                        "invalid_profile",
                        "Output bitrate exceeds declared native profile",
                    ));
                }
                Format::H264 {
                    video: video_bitrate,
                    audio: audio_bitrate,
                }
            }
            MovieProfile::NativeColorMasterV1 => Format::MasterV1,
            MovieProfile::NativeColorMasterV2 => Format::MasterV2,
        }))
    }
    pub(crate) fn is_master(self) -> bool {
        matches!(self.0, Format::MasterV1 | Format::MasterV2)
    }
    fn is_master_v2(self) -> bool {
        matches!(self.0, Format::MasterV2)
    }
    pub(crate) fn output_mime(self) -> Option<&'static str> {
        self.is_master().then_some("video/quicktime")
    }
    pub(crate) fn stage_payload_name(self) -> StagePayloadName {
        if self.is_master() {
            StagePayloadName::Mov
        } else {
            StagePayloadName::Mp4
        }
    }
    pub(crate) fn artifact_path(self, root: &Path, hash: &ContentHash) -> PathBuf {
        root.join("artifacts").join(format!(
            "{}.{}",
            hash.as_str(),
            if self.is_master() { "mov" } else { "mp4" }
        ))
    }
    pub(crate) fn receipt_schema(self) -> u32 {
        match self.0 {
            Format::H264 { .. } => 2,
            Format::MasterV1 => 3,
            Format::MasterV2 => 4,
        }
    }
    pub(crate) fn validate_receipt(
        self,
        root: &Path,
        receipt: &crate::ArtifactReceipt,
    ) -> Result<()> {
        if receipt.schema != self.receipt_schema()
            || receipt.output_path != self.artifact_path(root, &receipt.output_sha256)
        {
            return Err(error(
                "Receipt schema or rooted artifact path differs from output profile",
            ));
        }
        self.validate_measurements(&receipt.technical)
    }
    pub(crate) fn validate_measurements(self, value: &NativeMeasurements) -> Result<()> {
        let expected = if self.is_master() {
            ("ap4h", "lpcm")
        } else {
            ("avc1", "aac ")
        };
        FourCc::try_from(value.video_track.codec.clone())?;
        FourCc::try_from(value.audio_track.codec.clone())?;
        if value.video_track.codec != expected.0 || value.audio_track.codec != expected.1 {
            return Err(error("Encoded codecs differ from output profile"));
        }
        if self.is_master() {
            for track in [&value.video_track, &value.audio_track] {
                if track.raw_sample_pts_start.timescale == 0
                    || track.raw_sample_pts_end.timescale == 0
                    || track.raw_sample_pts_end.ticks <= 0
                    || track.sample_buffers == 0
                {
                    return Err(error("Mastering encoded track clock is invalid"));
                }
            }
            let streaming = value
                .streaming_audio
                .as_ref()
                .ok_or_else(|| error("Mastering streaming clock evidence is missing"))?;
            for evidence in [&streaming.source, &streaming.output] {
                if evidence.sample_frames != value.audio_sample_frames
                    || evidence.sample_frames == 0
                    || evidence
                        .source_end_sample
                        .checked_sub(evidence.source_start_sample)
                        != Some(evidence.sample_frames)
                    || evidence.decoded_prefix_sample_frames < evidence.source_end_sample
                    || !(1..=crate::pcm::CHUNK_FRAMES)
                        .contains(&evidence.maximum_owned_chunk_frames)
                    || evidence.chunks == 0
                    || evidence.chunks > evidence.sample_frames
                {
                    return Err(error(
                        "Mastering streaming sample interval or bounds are invalid",
                    ));
                }
            }
            if !streaming.output.reader_reached_end
                || streaming.output.source_start_sample != 0
                || streaming.output.decoded_prefix_sample_frames != value.audio_sample_frames
                || !value.full_video_decode
                || value.video_frames == 0
                || value.video_track.raw_sample_pts_start.ticks != 0
                || value.audio_track.raw_sample_pts_start.ticks != 0
                || i128::from(value.audio_track.raw_sample_pts_end.ticks) * 48000
                    != i128::from(value.audio_sample_frames)
                        * i128::from(value.audio_track.raw_sample_pts_end.timescale)
            {
                return Err(error(
                    "Mastering output clocks or EOF evidence are incomplete",
                ));
            }
            let format = value
                .format
                .as_ref()
                .ok_or_else(|| error("Mastering container evidence is missing"))?;
            if format.major_brand.0 != *b"qt  "
                && !format
                    .compatible_brands
                    .iter()
                    .any(|brand| brand.0 == *b"qt  ")
            {
                return Err(error("Container has no QuickTime brand"));
            }
            let pcm = value
                .audio_track
                .pcm_encoding
                .as_ref()
                .ok_or_else(|| error("Mastering PCM layout is missing"))?;
            if pcm.format_id != 0x6c70636d
                || pcm.format_flags != 12
                || pcm.bits_per_channel != 24
                || pcm.bytes_per_frame != 6
                || pcm.bytes_per_packet != 6
                || pcm.frames_per_packet != 1
                || value.audio_track.audio_layout != Some((48000, 2))
            {
                return Err(error(
                    "Mastering PCM layout differs from signed packed PCM24LE stereo48kHz",
                ));
            }
            let comparison = value
                .pcm24_comparison
                .as_ref()
                .ok_or_else(|| error("PCM24 comparison is missing"))?;
            if comparison.sample_frames != value.audio_sample_frames
                || comparison.maximum_code_delta != 0
            {
                return Err(error("PCM24 output differs from selected source codes"));
            }
            if value.video_track.pcm_encoding.is_some() {
                return Err(error("Video track cannot contain PCM evidence"));
            }
        } else if value.format.is_some()
            || value.pcm24_comparison.is_some()
            || value.audio_track.pcm_encoding.is_some()
            || value.video_track.pcm_encoding.is_some()
        {
            return Err(error("Historical profile contains mastering evidence"));
        }
        match self.0 {
            Format::MasterV2 => {
                let color = value
                    .video_color
                    .as_ref()
                    .ok_or_else(|| error("V2 mastering color evidence is missing"))?;
                let expected = rec709_tuple();
                if color.encoded_samples != expected || color.decoded_buffers != expected {
                    return Err(error(
                        "V2 mastering color evidence differs from the closed Rec.709 profile",
                    ));
                }
            }
            Format::H264 { .. } | Format::MasterV1 => {
                if value.video_color.is_some() {
                    return Err(error("Historical profile contains V2 color evidence"));
                }
            }
        }
        Ok(())
    }
    pub(crate) fn observe_encoded_video_color(
        self,
        description: &CMFormatDescription,
    ) -> Result<Option<NativeColorTupleEvidence>> {
        if !self.is_master_v2() {
            return Ok(None);
        }
        Ok(Some(require_rec709_tuple(
            format_extension(description, unsafe {
                kCMFormatDescriptionExtension_ColorPrimaries
            }),
            format_extension(description, unsafe {
                kCMFormatDescriptionExtension_TransferFunction
            }),
            format_extension(description, unsafe {
                kCMFormatDescriptionExtension_YCbCrMatrix
            }),
            "Encoded sample",
        )?))
    }
    pub(crate) fn observe_decoded_video_color(
        self,
        image: &CVPixelBuffer,
    ) -> Result<Option<NativeColorTupleEvidence>> {
        if !self.is_master_v2() {
            return Ok(None);
        }
        Ok(Some(observe_buffer_rec709(image, "Decoded buffer")?))
    }
    pub(crate) fn finish_video_color(
        self,
        encoded_samples: Option<NativeColorTupleEvidence>,
        decoded_buffers: Option<NativeColorTupleEvidence>,
    ) -> Result<Option<NativeVideoColorEvidence>> {
        if self.is_master_v2() {
            return Ok(Some(NativeVideoColorEvidence {
                encoded_samples: encoded_samples
                    .ok_or_else(|| error("Encoded V2 color evidence is missing"))?,
                decoded_buffers: decoded_buffers
                    .ok_or_else(|| error("Decoded V2 color evidence is missing"))?,
            }));
        }
        if encoded_samples.is_some() || decoded_buffers.is_some() {
            return Err(error("Historical profile produced V2 color evidence"));
        }
        Ok(None)
    }
    pub(crate) fn inspect_container(self, path: &Path) -> Result<Option<NativeFormatEvidence>> {
        if !self.is_master() {
            return Ok(None);
        }
        let mut file = File::open(path)?;
        let length = file.metadata()?.len();
        let mut offset = 0u64;
        for _ in 0..128 {
            if offset.checked_add(8).is_none_or(|end| end > length) {
                break;
            }
            file.seek(SeekFrom::Start(offset))?;
            let mut header = [0; 8];
            file.read_exact(&mut header)?;
            let mut size = u64::from(u32::from_be_bytes(
                header[..4].try_into().expect("four bytes"),
            ));
            let mut header_bytes = 8u64;
            if size == 1 {
                let mut large = [0; 8];
                file.read_exact(&mut large)?;
                size = u64::from_be_bytes(large);
                header_bytes = 16;
            }
            if size == 0 {
                size = length - offset;
            }
            if size < header_bytes || offset.checked_add(size).is_none_or(|end| end > length) {
                return Err(error("Invalid container atom extent"));
            }
            if &header[4..] == b"ftyp" {
                let body_bytes = size - header_bytes;
                if !(8..=4096).contains(&body_bytes) || !(body_bytes - 8).is_multiple_of(4) {
                    return Err(error("Invalid or oversized ftyp"));
                }
                let mut body = vec![0; body_bytes as usize];
                file.read_exact(&mut body)?;
                let brand = |bytes: &[u8]| -> Result<FourCc> {
                    FourCc::try_from(
                        String::from_utf8(bytes.to_vec())
                            .map_err(|_| error("Non-ASCII container brand"))?,
                    )
                };
                let evidence = NativeFormatEvidence {
                    major_brand: brand(&body[..4])?,
                    compatible_brands: body[8..]
                        .chunks_exact(4)
                        .map(brand)
                        .collect::<Result<_>>()?,
                };
                if evidence.major_brand.0 != *b"qt  "
                    && !evidence
                        .compatible_brands
                        .iter()
                        .any(|value| value.0 == *b"qt  ")
                {
                    return Err(error("Container has no QuickTime brand"));
                }
                return Ok(Some(evidence));
            }
            offset += size;
        }
        Err(error("Container lacks a bounded readable QuickTime ftyp"))
    }
    pub(crate) fn start_writer(
        self,
        output: &Path,
        settings: &Settings,
        control: &crate::exports::ExportControl,
    ) -> Result<NativeWriterSession> {
        control.check()?;
        let file_type = if self.is_master() {
            unsafe { AVFileTypeQuickTimeMovie }
        } else {
            unsafe { AVFileTypeMPEG4 }
        }
        .ok_or_else(|| error("Native container type unavailable"))?;
        let url = NSURL::fileURLWithPath(&NSString::from_str(
            output
                .to_str()
                .ok_or_else(|| error("Non-UTF8 output path"))?,
        ));
        let writer = unsafe { AVAssetWriter::assetWriterWithURL_fileType_error(&url, file_type) }
            .map_err(|e| error(format!("{e:?}")))?;
        let mut video_settings = vec![
            (
                "AVVideoCodecKey",
                text(if self.is_master() { "ap4h" } else { "avc1" }),
            ),
            ("AVVideoWidthKey", number(settings.width)),
            ("AVVideoHeightKey", number(settings.height)),
        ];
        if self.is_master_v2() {
            let key = unsafe { AVVideoColorPropertiesKey }
                .ok_or_else(|| error("AVVideoColorPropertiesKey is unavailable"))?;
            if key.to_string() != "AVVideoColorPropertiesKey" {
                return Err(error("Unexpected AVVideoColorPropertiesKey value"));
            }
            video_settings.push(("AVVideoColorPropertiesKey", rec709_video_properties()?));
        }
        let audio_settings = match self.0 {
            Format::H264 { video, audio } => {
                let bitrate = number(video);
                let compression = NSDictionary::from_slices(
                    &[unsafe { AVVideoAverageBitRateKey }
                        .ok_or_else(|| error("Native bitrate key unavailable"))?],
                    &[&*bitrate],
                );
                video_settings.push(("AVVideoCompressionPropertiesKey", unsafe {
                    Retained::cast_unchecked(compression)
                }));
                dictionary(vec![
                    ("AVFormatIDKey", number(0x61616320)),
                    ("AVSampleRateKey", number(48000)),
                    ("AVNumberOfChannelsKey", number(2)),
                    ("AVEncoderBitRateKey", number(audio)),
                ])
            }
            Format::MasterV1 | Format::MasterV2 => dictionary(vec![
                ("AVFormatIDKey", number(0x6c70636d)),
                ("AVSampleRateKey", number(48000)),
                ("AVNumberOfChannelsKey", number(2)),
                ("AVLinearPCMBitDepthKey", number(24)),
                ("AVLinearPCMIsFloatKey", number(0)),
                ("AVLinearPCMIsBigEndianKey", number(0)),
                ("AVLinearPCMIsNonInterleaved", number(0)),
            ]),
        };
        let video_settings = dictionary(video_settings);
        let video_type =
            unsafe { AVMediaTypeVideo }.ok_or_else(|| error("Video type unavailable"))?;
        let audio_type =
            unsafe { AVMediaTypeAudio }.ok_or_else(|| error("Audio type unavailable"))?;
        if !unsafe {
            writer.canApplyOutputSettings_forMediaType(Some(&video_settings), video_type)
                && writer.canApplyOutputSettings_forMediaType(Some(&audio_settings), audio_type)
        } {
            return Err(error("Native writer rejected format settings"));
        }
        let video = unsafe {
            AVAssetWriterInput::assetWriterInputWithMediaType_outputSettings(
                video_type,
                Some(&video_settings),
            )
        };
        let audio = unsafe {
            AVAssetWriterInput::assetWriterInputWithMediaType_outputSettings(
                audio_type,
                Some(&audio_settings),
            )
        };
        if !unsafe { writer.canAddInput(&video) } {
            return Err(error("Writer rejected video input"));
        }
        unsafe { writer.addInput(&video) };
        if !unsafe { writer.canAddInput(&audio) } {
            return Err(error("Combined writer rejected audio input"));
        }
        unsafe { writer.addInput(&audio) };
        let pixels = dictionary(vec![("PixelFormatType", number(kCVPixelFormatType_32BGRA))]);
        let adaptor = unsafe {
            AVAssetWriterInputPixelBufferAdaptor::assetWriterInputPixelBufferAdaptorWithAssetWriterInput_sourcePixelBufferAttributes(&video, Some(&pixels))
        };
        let session = NativeWriterSession {
            writer,
            video,
            audio,
            adaptor,
            format: self,
        };
        control.check()?;
        if !unsafe { session.writer.startWriting() } {
            return Err(error(format!("Writer did not start: {:?}", unsafe {
                session.writer.error()
            })));
        }
        unsafe {
            session
                .writer
                .startSessionAtSourceTime(CMTime::new(0, 48000))
        };
        Ok(session)
    }
}

pub(crate) struct NativeWriterSession {
    writer: Retained<AVAssetWriter>,
    video: Retained<AVAssetWriterInput>,
    audio: Retained<AVAssetWriterInput>,
    adaptor: Retained<AVAssetWriterInputPixelBufferAdaptor>,
    format: NativeFormatContract,
}
impl NativeWriterSession {
    pub(crate) fn writing(&self) -> bool {
        unsafe { self.writer.status() == AVAssetWriterStatus::Writing }
    }
    pub(crate) fn video_ready(&self) -> bool {
        unsafe { self.video.isReadyForMoreMediaData() }
    }
    pub(crate) fn audio_ready(&self) -> bool {
        unsafe { self.audio.isReadyForMoreMediaData() }
    }
    pub(crate) fn append_picture(
        &self,
        image: &CVPixelBuffer,
        pts: CMTime,
        finished: bool,
    ) -> Result<()> {
        if self.format.is_master_v2() {
            attach_input_rec709(image)?;
        }
        if !unsafe {
            self.adaptor
                .appendPixelBuffer_withPresentationTime(image, pts)
        } {
            return Err(error(format!(
                "Native picture append failed: {:?}",
                unsafe { self.writer.error() }
            )));
        }
        if finished {
            unsafe { self.video.markAsFinished() };
        }
        Ok(())
    }
    pub(crate) fn append_audio(&self, samples: &[f32], first: u64, finished: bool) -> Result<()> {
        let sample = pcm_buffer(samples, first, self.format.is_master())?;
        if !unsafe { self.audio.appendSampleBuffer(&sample) } {
            return Err(error(format!("Native audio append failed: {:?}", unsafe {
                self.writer.error()
            })));
        }
        if finished {
            unsafe { self.audio.markAsFinished() };
        }
        Ok(())
    }
    pub(crate) fn finish(
        &self,
        frames: u64,
        control: &crate::exports::ExportControl,
    ) -> Result<()> {
        control.check()?;
        let end = unsafe {
            CMTime::new(
                i64::try_from(frames).map_err(|_| error("Output endpoint overflow"))?,
                48000,
            )
        };
        unsafe { self.writer.endSessionAtSourceTime(end) };
        let (send, receive) = mpsc::channel();
        let finished = RcBlock::new(move || {
            let _ = send.send(());
        });
        unsafe { self.writer.finishWritingWithCompletionHandler(&finished) };
        let deadline = Instant::now() + Duration::from_secs(30);
        loop {
            control.check()?;
            if Instant::now() > deadline {
                return Err(error("Native finalization deadline expired"));
            }
            match receive.recv_timeout(Duration::from_millis(25)) {
                Ok(()) => break,
                Err(mpsc::RecvTimeoutError::Timeout) => {}
                Err(mpsc::RecvTimeoutError::Disconnected) => {
                    return Err(error("Native finalization callback closed"));
                }
            }
        }
        control.check()?;
        if unsafe { self.writer.status() } != AVAssetWriterStatus::Completed {
            return Err(error(format!("Native finalization failed: {:?}", unsafe {
                self.writer.error()
            })));
        }
        Ok(())
    }
}
impl Drop for NativeWriterSession {
    fn drop(&mut self) {
        if unsafe { self.writer.status() } != AVAssetWriterStatus::Completed {
            unsafe { self.writer.cancelWriting() };
        }
    }
}

pub(crate) fn pcm24_code(value: f32) -> Result<i32> {
    if !value.is_finite() {
        return Err(error("PCM contains non-finite samples"));
    }
    Ok((f64::from(value.clamp(-1.0, 1.0)) * 8388608.0)
        .round_ties_even()
        .clamp(-8388608.0, 8388607.0) as i32)
}

fn pcm_buffer(pcm: &[f32], first: u64, master: bool) -> Result<CFRetained<CMSampleBuffer>> {
    if pcm.is_empty() || !pcm.len().is_multiple_of(2) {
        return Err(error("Invalid stereo PCM block"));
    }
    let bytes: Vec<u8> = if master {
        let mut bytes = Vec::with_capacity(pcm.len() * 3);
        for &value in pcm {
            bytes.extend_from_slice(&pcm24_code(value)?.to_le_bytes()[..3]);
        }
        bytes
    } else {
        pcm.iter().flat_map(|v| v.to_le_bytes()).collect()
    };
    let mut block = std::ptr::null_mut();
    let status = unsafe {
        CMBlockBuffer::create_with_memory_block(
            None,
            std::ptr::null_mut(),
            bytes.len(),
            None,
            std::ptr::null(),
            0,
            bytes.len(),
            0,
            NonNull::from(&mut block),
        )
    };
    if status != 0 {
        return Err(error(format!("PCM block allocation failed: {status}")));
    }
    let block = unsafe {
        CFRetained::from_raw(
            NonNull::new(block).ok_or_else(|| error("PCM allocation returned null"))?,
        )
    };
    if unsafe { block.assure_block_memory() } != 0 {
        return Err(error("PCM native memory allocation failed"));
    }
    let pointer = NonNull::new(bytes.as_ptr().cast_mut())
        .ok_or_else(|| error("Empty PCM bytes"))?
        .cast();
    if unsafe { CMBlockBuffer::replace_data_bytes(pointer, &block, 0, bytes.len()) } != 0 {
        return Err(error("PCM block copy failed"));
    }
    let mut asbd = AudioStreamBasicDescription {
        mSampleRate: 48000.0,
        mFormatID: 0x6c70636d,
        mFormatFlags: if master { 12 } else { 9 },
        mBytesPerPacket: if master { 6 } else { 8 },
        mFramesPerPacket: 1,
        mBytesPerFrame: if master { 6 } else { 8 },
        mChannelsPerFrame: 2,
        mBitsPerChannel: if master { 24 } else { 32 },
        mReserved: 0,
    };
    let mut description = std::ptr::null();
    let status = unsafe {
        CMAudioFormatDescriptionCreate(
            None,
            NonNull::from(&mut asbd),
            0,
            std::ptr::null(),
            0,
            std::ptr::null(),
            None,
            NonNull::from(&mut description),
        )
    };
    if status != 0 {
        return Err(error(format!("PCM description creation failed: {status}")));
    }
    let description: CFRetained<CMFormatDescription> = unsafe {
        CFRetained::from_raw(
            NonNull::new(description.cast_mut())
                .ok_or_else(|| error("PCM description returned null"))?,
        )
    };
    let timing = CMSampleTimingInfo {
        duration: unsafe { CMTime::new(1, 48000) },
        presentationTimeStamp: unsafe {
            CMTime::new(
                i64::try_from(first).map_err(|_| error("PCM PTS overflow"))?,
                48000,
            )
        },
        decodeTimeStamp: unsafe { kCMTimeInvalid },
    };
    let mut sample = std::ptr::null_mut();
    let size = if master { 6 } else { 8 };
    let status = unsafe {
        CMSampleBuffer::create_ready(
            None,
            Some(&block),
            Some(&description),
            isize::try_from(pcm.len() / 2).map_err(|_| error("PCM count overflow"))?,
            1,
            &timing,
            1,
            &size,
            NonNull::from(&mut sample),
        )
    };
    if status != 0 {
        return Err(error(format!("PCM sample creation failed: {status}")));
    }
    Ok(unsafe {
        CFRetained::from_raw(NonNull::new(sample).ok_or_else(|| error("PCM sample returned null"))?)
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    static NEXT: AtomicU64 = AtomicU64::new(0);

    #[test]
    fn pcm24_quantizer_has_declared_ties_saturation_and_finite_boundary() {
        let lsb = 1.0f32 / 8388608.0;
        for (input, expected) in [
            (0.5 * lsb, 0),
            (1.5 * lsb, 2),
            (2.5 * lsb, 2),
            (-0.5 * lsb, 0),
            (-1.5 * lsb, -2),
            (-2.5 * lsb, -2),
            (-1.0, -8388608),
            (-2.0, -8388608),
            (1.0, 8388607),
            (2.0, 8388607),
        ] {
            assert_eq!(pcm24_code(input).unwrap(), expected);
        }
        for input in [f32::NAN, f32::INFINITY, f32::NEG_INFINITY] {
            assert!(pcm24_code(input).is_err());
        }
    }

    #[test]
    fn public_master_profile_rejects_caller_format_overrides() {
        for kind in ["native_color_master_v1", "native_color_master_v2"] {
            let profile: MovieProfile =
                serde_json::from_value(serde_json::json!({"kind":kind})).unwrap();
            assert!(
                NativeFormatContract::for_profile(&profile)
                    .unwrap()
                    .is_master()
            );
            for key in [
                "video_bitrate",
                "audio_bitrate",
                "codec",
                "extension",
                "sample_rate",
                "color_primaries",
                "transfer_function",
                "y_cb_cr_matrix",
                "attachment_mode",
            ] {
                let value = serde_json::json!({"kind":kind, key: 1});
                assert!(serde_json::from_value::<MovieProfile>(value).is_err());
            }
        }
    }

    #[test]
    fn rec709_tuple_rejects_missing_partial_and_wrong_framework_values() {
        let exact = || Some(REC709_NAME.to_owned());
        assert_eq!(
            require_rec709_tuple(exact(), exact(), exact(), "test").unwrap(),
            rec709_tuple()
        );
        for values in [
            [None, exact(), exact()],
            [exact(), None, exact()],
            [exact(), exact(), None],
            [Some("SMPTE_C".into()), exact(), exact()],
            [exact(), Some("ITU_R_601_4".into()), exact()],
            [exact(), exact(), Some("ITU_R_601_4".into())],
        ] {
            let [primaries, transfer, matrix] = values;
            assert!(require_rec709_tuple(primaries, transfer, matrix, "test").is_err());
        }
    }

    #[test]
    fn writer_input_rec709_attachments_propagate_without_changing_bgra_samples() {
        let image = crate::pixels::Pixels {
            width: 2,
            height: 1,
            bytes: vec![1, 2, 3, 255, 4, 5, 6, 255],
        }
        .into_native()
        .unwrap();
        let before = crate::pixels::Pixels::copy(&image).unwrap().bytes;
        assert!(observe_buffer_rec709(&image, "test").is_err());

        attach_input_rec709(&image).unwrap();
        assert_eq!(
            observe_buffer_rec709(&image, "test").unwrap(),
            rec709_tuple()
        );
        assert_eq!(crate::pixels::Pixels::copy(&image).unwrap().bytes, before);

        unsafe {
            image.set_attachment(
                kCVImageBufferColorPrimariesKey,
                objc2_core_video::kCVImageBufferColorPrimaries_SMPTE_C,
                CVAttachmentMode::ShouldPropagate,
            );
        }
        assert!(observe_buffer_rec709(&image, "test").is_err());

        attach_input_rec709(&image).unwrap();
        unsafe {
            image.set_attachment(
                kCVImageBufferTransferFunctionKey,
                kCVImageBufferTransferFunction_ITU_R_709_2,
                CVAttachmentMode::ShouldNotPropagate,
            );
        }
        assert!(observe_buffer_rec709(&image, "test").is_err());
    }

    #[test]
    fn native_pcm24_input_has_exact_signed_interleaved_bytes_and_clock() {
        let sample =
            pcm_buffer(&[-1.0, 1.0, 1.0 / 8388608.0, -1.0 / 8388608.0], 8191, true).unwrap();
        assert_eq!(unsafe { sample.num_samples() }, 2);
        let pts = unsafe { sample.presentation_time_stamp() };
        assert_eq!((pts.value, pts.timescale, pts.epoch), (8191, 48000, 0));
        let block = unsafe { sample.data_buffer() }.unwrap();
        let mut bytes = [0u8; 12];
        assert_eq!(
            unsafe { block.copy_data_bytes(0, 12, NonNull::from(&mut bytes).cast()) },
            0
        );
        assert_eq!(bytes, [0, 0, 128, 255, 255, 127, 1, 0, 0, 255, 255, 255]);
        assert!(pcm_buffer(&[0.0], 0, true).is_err());
        assert!(pcm_buffer(&[0.0, f32::NAN], 0, true).is_err());
    }

    #[test]
    fn container_requires_bounded_valid_quicktime_brand_and_printable_fourcc() {
        let path = std::env::temp_dir().join(format!(
            "studio-ftyp-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        let master = NativeFormatContract::for_profile(&MovieProfile::NativeColorMasterV1).unwrap();
        let atom = |major: &[u8; 4], compatible: &[u8; 4]| {
            let mut bytes = 20u32.to_be_bytes().to_vec();
            bytes.extend_from_slice(b"ftyp");
            bytes.extend_from_slice(major);
            bytes.extend_from_slice(&0u32.to_be_bytes());
            bytes.extend_from_slice(compatible);
            bytes
        };
        for valid in [atom(b"qt  ", b"qt  "), atom(b"isom", b"qt  ")] {
            std::fs::write(&path, valid).unwrap();
            assert!(master.inspect_container(&path).unwrap().is_some());
        }
        for invalid in [
            atom(b"isom", b"mp42"),
            atom(b"qt  ", b"\0bad"),
            vec![0; 7],
            [5000u32.to_be_bytes().as_slice(), b"ftyp", &[0; 4992]].concat(),
            [7u32.to_be_bytes().as_slice(), b"ftyp"].concat(),
        ] {
            std::fs::write(&path, invalid).unwrap();
            assert!(master.inspect_container(&path).is_err());
        }
        assert!(FourCc::try_from(String::from("ap4h")).is_ok());
        for invalid in ["abc", "abcde", "éab", "\0abc"] {
            assert!(FourCc::try_from(String::from(invalid)).is_err());
        }
        std::fs::remove_file(path).unwrap();
    }
}
