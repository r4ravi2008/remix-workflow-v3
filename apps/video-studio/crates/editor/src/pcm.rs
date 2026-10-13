use std::path::{Path, PathBuf};
use std::ptr::NonNull;
use std::sync::{
    Arc,
    atomic::{AtomicBool, Ordering},
    mpsc,
};
use std::time::{Duration, Instant};

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2_av_foundation::{
    AVAssetReader, AVAssetReaderStatus, AVAssetReaderTrackOutput, AVAssetTrack,
};
use objc2_core_media::CMAudioFormatDescriptionGetStreamBasicDescription;
use objc2_foundation::{NSDictionary, NSNumber, NSString};
use serde::{Deserialize, Serialize};

use crate::{MediaKind, Result, Span, StudioError, media};

pub(crate) const CHUNK_FRAMES: u64 = 4096;
pub(crate) const STREAM_DEADLINE: Duration = Duration::from_secs(1800);

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PcmStreamEvidence {
    pub source_start_sample: u64,
    pub source_end_sample: u64,
    pub sample_frames: u64,
    pub decoded_prefix_sample_frames: u64,
    pub chunks: u64,
    pub maximum_owned_chunk_frames: u64,
    pub reader_reached_end: bool,
}

pub(crate) struct PcmChunk {
    pub first_sample: u64,
    pub samples: Vec<f32>,
}

impl PcmChunk {
    pub(crate) fn frames(&self) -> u64 {
        self.samples.len() as u64 / 2
    }
}

enum Event {
    Chunk(PcmChunk),
    Complete(PcmStreamEvidence),
    Failure(StudioError),
}

#[derive(Clone)]
struct Signal {
    stopped: Arc<AtomicBool>,
    export: Option<crate::exports::ExportControl>,
}

impl Signal {
    fn check(&self) -> Result<()> {
        if let Some(control) = &self.export {
            control.check()?;
        }
        if self.stopped.load(Ordering::Acquire) {
            return Err(error("PCM stream consumer stopped"));
        }
        Ok(())
    }
}

pub(crate) struct Stream {
    receive: Option<mpsc::Receiver<Event>>,
    worker: Option<std::thread::JoinHandle<()>>,
    signal: Signal,
    deadline: Instant,
    evidence: Option<PcmStreamEvidence>,
}

fn error(detail: impl Into<String>) -> StudioError {
    StudioError::new("native_pcm_error", detail)
}

impl Stream {
    pub(crate) fn open(
        path: &Path,
        selection: Option<Span>,
        control: Option<crate::exports::ExportControl>,
    ) -> Result<Self> {
        Self::open_with_hint(path, selection, control, None)
    }

    pub(crate) fn open_with_hint(
        path: &Path,
        selection: Option<Span>,
        control: Option<crate::exports::ExportControl>,
        mime_hint: Option<&'static str>,
    ) -> Result<Self> {
        if let Some(selection) = &selection {
            selection.end()?;
        }
        let (send, receive) = mpsc::sync_channel(2);
        let signal = Signal {
            stopped: Arc::new(AtomicBool::new(false)),
            export: control,
        };
        let worker_signal = signal.clone();
        let path: PathBuf = path.into();
        let worker = std::thread::spawn(move || {
            let decode_send = send.clone();
            let decode_signal = worker_signal.clone();
            let wait_signal = worker_signal.clone();
            let result = media::with_track_cancellable_hint(
                &path,
                &MediaKind::Audio,
                mime_hint,
                STREAM_DEADLINE,
                move || wait_signal.check(),
                || {},
                move |track| decode(track, selection.as_ref(), &decode_send, &decode_signal),
            );
            let terminal = match result {
                Ok(evidence) => Event::Complete(evidence),
                Err(error) => Event::Failure(error),
            };
            let _ = push(&send, terminal, &worker_signal);
        });
        Ok(Self {
            receive: Some(receive),
            worker: Some(worker),
            signal,
            deadline: Instant::now() + STREAM_DEADLINE,
            evidence: None,
        })
    }

    pub(crate) fn next(&mut self) -> Result<Option<PcmChunk>> {
        if self.evidence.is_some() {
            return Ok(None);
        }
        loop {
            self.signal.check()?;
            if Instant::now() > self.deadline {
                return Err(error("PCM stream deadline expired"));
            }
            let receiver = self
                .receive
                .as_ref()
                .ok_or_else(|| error("PCM stream is closed"))?;
            match receiver.recv_timeout(Duration::from_millis(25)) {
                Ok(Event::Chunk(chunk)) => return Ok(Some(chunk)),
                Ok(Event::Failure(error)) => return Err(error),
                Ok(Event::Complete(evidence)) => {
                    self.evidence = Some(evidence);
                    self.join()?;
                    return Ok(None);
                }
                Err(mpsc::RecvTimeoutError::Timeout) => {}
                Err(mpsc::RecvTimeoutError::Disconnected) => {
                    self.join()?;
                    return Err(error("PCM worker closed without a terminal receipt"));
                }
            }
        }
    }

    pub(crate) fn evidence(&self) -> Result<&PcmStreamEvidence> {
        self.evidence
            .as_ref()
            .ok_or_else(|| error("PCM stream has not reached its declared endpoint"))
    }

    fn join(&mut self) -> Result<()> {
        if let Some(worker) = self.worker.take() {
            worker.join().map_err(|_| error("PCM worker panicked"))?;
        }
        Ok(())
    }
}

impl Drop for Stream {
    fn drop(&mut self) {
        self.signal.stopped.store(true, Ordering::Release);
        self.receive.take();
        let _ = self.join();
    }
}

fn push(send: &mpsc::SyncSender<Event>, mut event: Event, signal: &Signal) -> Result<()> {
    loop {
        signal.check()?;
        match send.try_send(event) {
            Ok(()) => return Ok(()),
            Err(mpsc::TrySendError::Full(pending)) => {
                event = pending;
                std::thread::sleep(Duration::from_millis(1));
            }
            Err(mpsc::TrySendError::Disconnected(_)) => {
                return Err(error("PCM consumer closed the bounded channel"));
            }
        }
    }
}

struct ReaderGuard<'a>(&'a AVAssetReader);
impl Drop for ReaderGuard<'_> {
    fn drop(&mut self) {
        unsafe { self.0.cancelReading() };
    }
}

fn decode(
    track: &AVAssetTrack,
    selection: Option<&Span>,
    send: &mpsc::SyncSender<Event>,
    signal: &Signal,
) -> Result<PcmStreamEvidence> {
    signal.check()?;
    let asset = unsafe { track.asset() }.ok_or_else(|| error("PCM track lost its asset"))?;
    let reader = unsafe { AVAssetReader::assetReaderWithAsset_error(&asset) }
        .map_err(|e| error(format!("{e:?}")))?;
    let _guard = ReaderGuard(&reader);
    let entries = [
        ("AVFormatIDKey", 0x6c70636d),
        ("AVSampleRateKey", 48000),
        ("AVNumberOfChannelsKey", 2),
        ("AVLinearPCMBitDepthKey", 32),
        ("AVLinearPCMIsFloatKey", 1),
        ("AVLinearPCMIsBigEndianKey", 0),
        ("AVLinearPCMIsNonInterleaved", 0),
    ];
    let keys: Vec<_> = entries
        .iter()
        .map(|(key, _)| NSString::from_str(key))
        .collect();
    let values: Vec<Retained<AnyObject>> = entries
        .iter()
        .map(|(_, value)| unsafe { Retained::cast_unchecked(NSNumber::new_u32(*value)) })
        .collect();
    let keys: Vec<_> = keys.iter().map(|key| &**key).collect();
    let values: Vec<_> = values.iter().map(|value| &**value).collect();
    let settings = NSDictionary::from_slices(&keys, &values);
    let output = unsafe {
        AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrack_outputSettings(
            track,
            Some(&settings),
        )
    };
    if !unsafe { reader.canAddOutput(&output) } {
        return Err(error("Reader rejected stereo float PCM"));
    }
    unsafe { reader.addOutput(&output) };
    if !unsafe { reader.startReading() } {
        return Err(error(format!("PCM reader did not start: {:?}", unsafe {
            reader.error()
        })));
    }
    let start = selection.map_or(0, |span| span.start);
    let target_end = selection.map(Span::end).transpose()?;
    let mut evidence = PcmStreamEvidence {
        source_start_sample: start,
        source_end_sample: start,
        sample_frames: 0,
        decoded_prefix_sample_frames: 0,
        chunks: 0,
        maximum_owned_chunk_frames: 0,
        reader_reached_end: false,
    };
    let deadline = Instant::now() + STREAM_DEADLINE;
    let mut count = 0_u64;
    loop {
        signal.check()?;
        if Instant::now() > deadline {
            return Err(error("PCM decode deadline expired"));
        }
        let Some(sample) = (unsafe { output.copyNextSampleBuffer() }) else {
            if unsafe { reader.status() } != AVAssetReaderStatus::Completed {
                return Err(error(format!(
                    "PCM reader ended without completion: {:?}",
                    unsafe { reader.error() }
                )));
            }
            evidence.reader_reached_end = true;
            break;
        };
        let frames = u64::try_from(unsafe { sample.num_samples() })
            .map_err(|_| error("Negative PCM sample count"))?;
        if frames == 0 {
            continue;
        }
        let format = unsafe { sample.format_description() }
            .ok_or_else(|| error("PCM sample has no format"))?;
        let layout = unsafe { CMAudioFormatDescriptionGetStreamBasicDescription(&format) };
        let layout = unsafe { layout.as_ref() }.ok_or_else(|| error("PCM sample has no layout"))?;
        if layout.mFormatID != 0x6c70636d
            || layout.mSampleRate != 48000.0
            || layout.mChannelsPerFrame != 2
            || layout.mBitsPerChannel != 32
            || layout.mBytesPerFrame != 8
            || layout.mFormatFlags & 1 == 0
            || layout.mFormatFlags & 34 != 0
        {
            return Err(error("Unexpected stereo float PCM layout"));
        }
        let pts = unsafe { sample.presentation_time_stamp() };
        if pts.timescale <= 0
            || pts.epoch != 0
            || pts.flags.0 & 1 == 0
            || pts.flags.0 & 28 != 0
            || i128::from(pts.value) * 48000 != i128::from(count) * i128::from(pts.timescale)
        {
            return Err(error("PCM source timestamps are discontinuous"));
        }
        let end = count
            .checked_add(frames)
            .ok_or_else(|| error("PCM clock overflow"))?;
        let first = count.max(start);
        let last = target_end.map_or(end, |limit| end.min(limit));
        if last > first {
            let block =
                unsafe { sample.data_buffer() }.ok_or_else(|| error("PCM sample has no data"))?;
            let mut selected = first;
            while selected < last {
                signal.check()?;
                let chunk_frames = CHUNK_FRAMES.min(last - selected);
                let offset = usize::try_from(
                    (selected - count)
                        .checked_mul(8)
                        .ok_or_else(|| error("PCM offset overflow"))?,
                )
                .map_err(|_| error("PCM offset exceeds address extent"))?;
                let size = chunk_frames as usize * 8;
                let mut bytes = vec![0; size];
                let pointer = NonNull::new(bytes.as_mut_ptr())
                    .ok_or_else(|| error("Empty PCM copy"))?
                    .cast();
                if unsafe { block.copy_data_bytes(offset, size, pointer) } != 0 {
                    return Err(error("PCM bounded copy failed"));
                }
                let mut floats = Vec::with_capacity(chunk_frames as usize * 2);
                for bytes in bytes.chunks_exact(4) {
                    let value = f32::from_le_bytes(
                        bytes.try_into().map_err(|_| error("Invalid PCM packing"))?,
                    );
                    if !value.is_finite() {
                        return Err(error("PCM contains non-finite samples"));
                    }
                    floats.push(value);
                }
                push(
                    send,
                    Event::Chunk(PcmChunk {
                        first_sample: selected - start,
                        samples: floats,
                    }),
                    signal,
                )?;
                evidence.chunks += 1;
                evidence.maximum_owned_chunk_frames =
                    evidence.maximum_owned_chunk_frames.max(chunk_frames);
                evidence.sample_frames = evidence
                    .sample_frames
                    .checked_add(chunk_frames)
                    .ok_or_else(|| error("PCM selected count overflow"))?;
                selected += chunk_frames;
                evidence.source_end_sample = selected;
            }
        }
        count = end;
        evidence.decoded_prefix_sample_frames = count;
        if target_end.is_some_and(|limit| count >= limit) {
            break;
        }
    }
    if selection.is_some_and(|span| evidence.sample_frames != span.length) {
        return Err(error(
            "PCM selection ended before its required sample count",
        ));
    }
    Ok(evidence)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicU64;

    static NEXT: AtomicU64 = AtomicU64::new(0);
    const FRAMES: u64 = 576000;
    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let path = std::env::temp_dir().join(format!(
                "studio-streaming-pcm-{}-{}.wav",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            let bytes = FRAMES as u32 * 4;
            let mut data = Vec::with_capacity(bytes as usize + 44);
            data.extend_from_slice(b"RIFF");
            data.extend_from_slice(&(36 + bytes).to_le_bytes());
            data.extend_from_slice(b"WAVEfmt ");
            data.extend_from_slice(&16u32.to_le_bytes());
            data.extend_from_slice(&1u16.to_le_bytes());
            data.extend_from_slice(&2u16.to_le_bytes());
            data.extend_from_slice(&48000u32.to_le_bytes());
            data.extend_from_slice(&192000u32.to_le_bytes());
            data.extend_from_slice(&4u16.to_le_bytes());
            data.extend_from_slice(&16u16.to_le_bytes());
            data.extend_from_slice(b"data");
            data.extend_from_slice(&bytes.to_le_bytes());
            for frame in 0..FRAMES {
                for channel in 0..2 {
                    data.extend_from_slice(&value(frame, channel).to_le_bytes());
                }
            }
            std::fs::write(&path, data).unwrap();
            Self(path)
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = std::fs::remove_file(&self.0);
        }
    }
    fn value(frame: u64, channel: usize) -> i16 {
        if channel == 0 {
            ((frame * 17 % 50000) as i32 - 25000) as i16
        } else {
            ((frame * 29 % 54000) as i32 - 27000) as i16
        }
    }

    #[test]
    fn selection_over_ten_seconds_has_exact_offset_and_bounded_owned_chunks() {
        let fixture = Fixture::new();
        let selection = Span {
            start: 8191,
            length: 480001,
        };
        let mut stream = Stream::open(&fixture.0, Some(selection.clone()), None).unwrap();
        let mut count = 0u64;
        while let Some(chunk) = stream.next().unwrap() {
            assert_eq!(chunk.first_sample, count);
            assert!((1..=CHUNK_FRAMES).contains(&chunk.frames()));
            for values in chunk.samples.chunks_exact(2) {
                for (channel, &observed) in values.iter().enumerate() {
                    assert_eq!(
                        observed,
                        f32::from(value(selection.start + count, channel)) / 32768.0
                    );
                }
                count += 1;
            }
        }
        assert_eq!(count, selection.length);
        let evidence = stream.evidence().unwrap();
        assert_eq!(
            (evidence.source_start_sample, evidence.source_end_sample),
            (8191, 488192)
        );
        assert_eq!(evidence.sample_frames, count);
        assert_eq!(evidence.maximum_owned_chunk_frames, CHUNK_FRAMES);
        assert!(!evidence.reader_reached_end);
    }

    #[test]
    fn full_reader_reaches_eof_and_early_selection_never_gets_a_complete_receipt() {
        let fixture = Fixture::new();
        let mut stream = Stream::open(&fixture.0, None, None).unwrap();
        let mut count = 0;
        while let Some(chunk) = stream.next().unwrap() {
            count += chunk.frames();
        }
        assert_eq!(count, FRAMES);
        assert!(stream.evidence().unwrap().reader_reached_end);
        let mut stream = Stream::open(
            &fixture.0,
            Some(Span {
                start: FRAMES - 1,
                length: 2,
            }),
            None,
        )
        .unwrap();
        assert_eq!(stream.next().unwrap().unwrap().frames(), 1);
        assert_eq!(stream.next().err().unwrap().code, "native_pcm_error");
        assert!(stream.evidence().is_err());
    }

    #[test]
    fn dropping_a_consumer_stops_a_worker_under_backpressure() {
        let fixture = Fixture::new();
        let mut stream = Stream::open(&fixture.0, None, None).unwrap();
        assert!(stream.next().unwrap().is_some());
        std::thread::sleep(Duration::from_millis(5));
        let before = Instant::now();
        drop(stream);
        assert!(before.elapsed() < Duration::from_secs(5));
    }

    #[test]
    fn the_shared_export_signal_stops_pcm_under_backpressure() {
        let fixture = Fixture::new();
        let control = crate::exports::ExportControl::test_active();
        let mut stream = Stream::open(&fixture.0, None, Some(control.clone())).unwrap();
        assert!(stream.next().unwrap().is_some());
        std::thread::sleep(Duration::from_millis(5));
        control.interrupt();
        assert_eq!(stream.next().err().unwrap().code, "export_interrupted");
        let before = Instant::now();
        drop(stream);
        assert!(before.elapsed() < Duration::from_secs(5));
    }

    #[test]
    fn a_stream_can_be_dropped_before_the_first_track_callback() {
        let fixture = Fixture::new();
        let stream = Stream::open(&fixture.0, None, None).unwrap();
        let before = Instant::now();
        drop(stream);
        assert!(before.elapsed() < Duration::from_secs(1));
    }
}
