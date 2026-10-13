use std::fs;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

use sha2::{Digest, Sha256};
use video_studio::*;

static NEXT: AtomicU64 = AtomicU64::new(0);
struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "video-studio-test-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
    fn studio(&self) -> Studio {
        Studio::open(self.0.join("state")).unwrap()
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}
fn id(value: &str) -> EntityId {
    EntityId::parse(value).unwrap()
}
fn create(studio: &Studio) -> RevisionReceipt {
    studio
        .create_project(CreateProject {
            project: id("test"),
            intent: id("create"),
            name: "Test project".into(),
            settings: Settings {
                width: 320,
                height: 180,
                frame_rate: Rate {
                    numerator: 24,
                    denominator: 1,
                },
                audio_rate: 48000,
                channels: 2,
                working_color: "rec709".into(),
            },
        })
        .unwrap()
}
fn edit(base: ContentHash, intent: &str, timeline: &str) -> CommitProject {
    CommitProject {
        intent: id(intent),
        base_revision: base,
        imports: vec![],
        canonical_audio: None,
        timelines: vec![Timeline {
            id: id(timeline),
            frame_count: 24,
            video_tracks: vec![],
            audio_tracks: vec![],
        }],
    }
}

#[test]
fn intent_replay_survives_new_head_and_changed_requests_fail() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let request = edit(initial.revision, "edit-first", "main");
    let first = p.commit(request.clone()).unwrap();
    p.commit(edit(first.revision.clone(), "edit-second", "second"))
        .unwrap();
    let reopened = f.studio().project(id("test")).unwrap();
    let replay = reopened.commit(request.clone()).unwrap();
    assert!(replay.replayed);
    assert_eq!(replay.revision, first.revision);
    let mut changed = request;
    changed.timelines[0].frame_count = 48;
    assert_eq!(
        reopened.commit(changed).unwrap_err().code,
        "intent_conflict"
    );
    assert_eq!(reopened.head().unwrap().receipt.sequence, 2);
}

#[test]
fn concurrent_edits_have_one_winner_and_keep_the_loser_atomic() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let a = s.project(id("test")).unwrap();
    let b = a.clone();
    let base = initial.revision;
    let barrier = std::sync::Arc::new(std::sync::Barrier::new(2));
    let ba = barrier.clone();
    let bb = barrier;
    let base_a = base.clone();
    let first = std::thread::spawn(move || {
        ba.wait();
        a.commit(edit(base_a, "actor-a", "a"))
    });
    let second = std::thread::spawn(move || {
        bb.wait();
        b.commit(edit(base, "actor-b", "b"))
    });
    let results = [first.join().unwrap(), second.join().unwrap()];
    assert_eq!(results.iter().filter(|r| r.is_ok()).count(), 1);
    assert_eq!(
        results
            .iter()
            .filter(|r| r.as_ref().is_err_and(|e| e.code == "revision_conflict"))
            .count(),
        1
    );
    let head = s.project(id("test")).unwrap().head().unwrap();
    assert_eq!(head.receipt.sequence, 1);
    assert_eq!(head.snapshot.timelines.len(), 1);
}

#[test]
fn invalid_edit_does_not_advance_head_or_consume_intent() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = edit(initial.revision.clone(), "fixable", "main");
    request.timelines[0].frame_count = 0;
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "timeline_extent"
    );
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    request.timelines[0].frame_count = 24;
    assert_eq!(p.commit(request).unwrap().sequence, 1);
}

#[test]
fn stored_revision_tampering_is_detected() {
    let f = Fixture::new();
    let s = f.studio();
    create(&s);
    let db = rusqlite::Connection::open(f.0.join("state/studio.sqlite")).unwrap();
    db.execute(
        "UPDATE revisions SET body=replace(body,'Test project','False project')",
        [],
    )
    .unwrap();
    assert_eq!(
        s.project(id("test")).unwrap().head().unwrap_err().code,
        "revision_tampered"
    );
}

#[test]
fn integer_clocks_reject_fractional_and_overflow_boundaries() {
    let rate = Rate {
        numerator: 24,
        denominator: 1,
    };
    assert_eq!(rate.samples_at_frame(6552, 48000).unwrap(), 13104000);
    assert_eq!(
        Rate {
            numerator: 30000,
            denominator: 1001
        }
        .samples_at_frame(1, 48000)
        .unwrap_err()
        .code,
        "fractional_sample_boundary"
    );
    assert_eq!(
        Span {
            start: u64::MAX,
            length: 1
        }
        .end()
        .unwrap_err()
        .code,
        "time_overflow"
    );
    assert!(ContentHash::parse("../wrong").is_err());
    assert!(EntityId::parse("../../escape").is_err());
}

fn wav(f: &Fixture) -> AssetImport {
    wav_with_frames(f, 480)
}
fn wav_with_frames(f: &Fixture, frames: u32) -> AssetImport {
    let bytes = frames * 4;
    let mut data = Vec::new();
    data.extend_from_slice(b"RIFF");
    data.extend_from_slice(&(36 + bytes).to_le_bytes());
    data.extend_from_slice(b"WAVEfmt ");
    data.extend_from_slice(&16_u32.to_le_bytes());
    data.extend_from_slice(&1_u16.to_le_bytes());
    data.extend_from_slice(&2_u16.to_le_bytes());
    data.extend_from_slice(&48000_u32.to_le_bytes());
    data.extend_from_slice(&192000_u32.to_le_bytes());
    data.extend_from_slice(&4_u16.to_le_bytes());
    data.extend_from_slice(&16_u16.to_le_bytes());
    data.extend_from_slice(b"data");
    data.extend_from_slice(&bytes.to_le_bytes());
    for n in 0..frames {
        let sample = ((f64::from(n) * 0.12).sin() * 1000.0) as i16;
        data.extend_from_slice(&sample.to_le_bytes());
        data.extend_from_slice(&(-sample).to_le_bytes());
    }
    let path = f.0.join("fixture.wav");
    fs::write(&path, &data).unwrap();
    AssetImport {
        previous_measurement: None,
        path,
        expected_hash: ContentHash::parse(format!("{:x}", Sha256::digest(&data))).unwrap(),
        expected_bytes: data.len() as u64,
        media_kind: MediaKind::Audio,
        origin: Origin::Imported {
            external_source: "test-generated-pcm".into(),
            role: "test_fixture".into(),
        },
    }
}

fn image(f: &Fixture, name: &str, rgb: &[u8]) -> AssetImport {
    let mut bytes = Vec::new();
    let mut encoder = png::Encoder::new(&mut bytes, 2, 1);
    encoder.set_color(png::ColorType::Rgb);
    encoder.set_depth(png::BitDepth::Eight);
    let mut writer = encoder.write_header().unwrap();
    writer.write_image_data(rgb).unwrap();
    writer.finish().unwrap();
    let path = f.0.join(name);
    fs::write(&path, &bytes).unwrap();
    AssetImport {
        previous_measurement: None,
        path,
        expected_hash: ContentHash::parse(format!("{:x}", Sha256::digest(&bytes))).unwrap(),
        expected_bytes: bytes.len() as u64,
        media_kind: MediaKind::Image,
        origin: Origin::Imported {
            external_source: "test-png".into(),
            role: "test-fixture".into(),
        },
    }
}

fn alpha_image(f: &Fixture, name: &str, width: u32, height: u32, rgba: &[u8]) -> AssetImport {
    let mut bytes = Vec::new();
    let mut encoder = png::Encoder::new(&mut bytes, width, height);
    encoder.set_color(png::ColorType::Rgba);
    encoder.set_depth(png::BitDepth::Eight);
    let mut writer = encoder.write_header().unwrap();
    writer.write_image_data(rgba).unwrap();
    writer.finish().unwrap();
    let path = f.0.join(name);
    fs::write(&path, &bytes).unwrap();
    AssetImport {
        previous_measurement: None,
        path,
        expected_hash: ContentHash::parse(format!("{:x}", Sha256::digest(&bytes))).unwrap(),
        expected_bytes: bytes.len() as u64,
        media_kind: MediaKind::Image,
        origin: Origin::Imported {
            external_source: "test-alpha-png".into(),
            role: "test-fixture".into(),
        },
    }
}

#[test]
fn image_holds_preserve_typed_lineage_and_have_separate_decode_evidence() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let input = image(&f, "source.png", &[255, 0, 0, 0, 0, 255]);
    let mut derived = image(&f, "derived.png", &[255, 99, 0, 0, 99, 255]);
    derived.origin = Origin::Derived {
        inputs: vec![SourceRange {
            asset: input.expected_hash.clone(),
            stream: MediaKind::Image,
            range: Span {
                start: 0,
                length: 1,
            },
        }],
        recipe: ContentHash::parse("1".repeat(64)).unwrap(),
        receipt: ContentHash::parse("2".repeat(64)).unwrap(),
    };
    let audio = wav_with_frames(&f, 48000);
    let mut request = edit(initial.revision, "bind-image", "main");
    request.imports = vec![input.clone(), derived.clone(), audio.clone()];
    request.timelines[0].video_tracks = vec![VideoTrack {
        id: id("picture"),
        clips: vec![VideoClip {
            motion: None,
            mask: None,
            placement: None,
            id: id("image-hold"),
            timeline_frames: Span {
                start: 0,
                length: 24,
            },
            asset: derived.expected_hash.clone(),
            source_samples: Span {
                start: 0,
                length: 1,
            },
            cadence: Cadence::Hold { ordinal: 0 },
            framing: Some(Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    x: 0.0,
                    y: 0.0,
                    width: 1.0,
                    height: 1.0,
                },
            }),
        }],
    }];
    request.timelines[0].audio_tracks = vec![AudioTrack {
        id: id("audio"),
        clips: vec![AudioClip {
            id: id("pcm"),
            timeline_samples: Span {
                start: 0,
                length: 48000,
            },
            source_samples: Span {
                start: 0,
                length: 48000,
            },
            asset: audio.expected_hash,
            source_rate: 48000,
            gain: 1.0,
            pan: 0.0,
        }],
    }];
    let committed = p.commit(request).unwrap();
    let export = ExportRequest {
        intent: id("image-plan"),
        revision: committed.revision,
        timeline: id("main"),
        profile: MovieProfile::H264AacMp4 {
            video_bitrate: 1000000,
            audio_bitrate: 192000,
        },
    };
    let prepared = p.prepare_export(export.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 3);
    assert!(prepared.plan.decode_evidence.is_empty());
    assert_eq!(prepared.plan.image_decode_evidence.len(), 1);
    assert_eq!(prepared.plan.video[0].presentation_ordinals, vec![0; 24]);
    assert!(
        prepared
            .plan
            .source_closure
            .contains_key(&input.expected_hash)
    );
    assert_eq!(
        prepared.plan.source_closure[&derived.expected_hash].origin,
        derived.origin
    );
    assert!(p.prepare_export(export.clone()).unwrap().replayed);
    let master = ExportRequest {
        intent: id("image-master"),
        profile: MovieProfile::NativeColorMasterV1,
        ..export
    };
    assert_eq!(p.prepare_export(master.clone()).unwrap().plan.schema, 3);
    let result = p.export(master).unwrap();
    assert_eq!(result.receipt.artifact.schema, 3);
    assert_eq!(
        result
            .receipt
            .artifact
            .technical
            .pcm24_comparison
            .unwrap()
            .maximum_code_delta,
        0
    );
}

#[test]
fn a_sole_alpha_hold_gets_plan7_canvas_placement_and_unique_alpha_evidence() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let picture = alpha_image(&f, "sole-alpha.png", 2, 1, &[255, 0, 0, 0, 0, 0, 255, 255]);
    let audio = wav_with_frames(&f, 48_000);
    let mut request = edit(initial.revision, "sole-alpha-edit", "main");
    request.imports = vec![picture.clone(), audio.clone()];
    request.timelines[0].video_tracks = vec![VideoTrack {
        id: id("picture"),
        clips: vec![VideoClip {
            id: id("alpha-hold"),
            timeline_frames: Span {
                start: 0,
                length: 24,
            },
            asset: picture.expected_hash.clone(),
            source_samples: Span {
                start: 0,
                length: 1,
            },
            cadence: Cadence::Hold { ordinal: 0 },
            framing: Some(Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    x: 0.0,
                    y: 0.0,
                    width: 1.0,
                    height: 1.0,
                },
            }),
            placement: None,
            motion: None,
            mask: None,
        }],
    }];
    request.timelines[0].audio_tracks = vec![AudioTrack {
        id: id("audio"),
        clips: vec![AudioClip {
            id: id("pcm"),
            timeline_samples: Span {
                start: 0,
                length: 48_000,
            },
            source_samples: Span {
                start: 0,
                length: 48_000,
            },
            asset: audio.expected_hash,
            source_rate: 48_000,
            gain: 1.0,
            pan: 0.0,
        }],
    }];
    let committed = p.commit(request).unwrap();
    let export = ExportRequest {
        intent: id("sole-alpha-plan"),
        revision: committed.revision,
        timeline: id("main"),
        profile: MovieProfile::H264AacMp4 {
            video_bitrate: 1_000_000,
            audio_bitrate: 192_000,
        },
    };
    let prepared = p.prepare_export(export.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 7);
    assert_eq!(
        prepared.plan.alpha_policy,
        Some(AlphaPolicy::StraightRgbaPremulUnorm16Q16V1)
    );
    assert_eq!(
        prepared.plan.video[0].placement,
        Some(PicturePlacement {
            destination: PixelRect {
                x: 0,
                y: 0,
                width: 320,
                height: 180,
            },
            opacity: Opacity::new(1.0).unwrap(),
        })
    );
    assert_eq!(prepared.plan.image_decode_evidence.len(), 1);
    assert_eq!(
        prepared.plan.image_decode_evidence[0].asset,
        picture.expected_hash
    );
    assert!(
        prepared.plan.image_decode_evidence[0]
            .source_alpha_id
            .is_some()
    );
    let video_use = serde_json::to_value(&prepared.plan.video[0]).unwrap();
    assert!(video_use.get("alpha").is_none());
    assert!(video_use.get("source_alpha_id").is_none());
    let exported = p.export(export.clone()).unwrap();
    assert_eq!(exported.receipt.artifact.plan_id, prepared.plan_id);
    assert_eq!(
        exported.picture_execution.as_ref().unwrap().composed_frames,
        24
    );
    let verified = p.verify_export(export.intent.clone()).unwrap();
    assert_eq!(verified.receipt.receipt_id, exported.receipt.receipt_id);
    assert!(verified.picture_execution.is_none());
    let replayed = p.export(export).unwrap();
    assert!(replayed.replayed);
    assert_eq!(replayed.receipt.receipt_id, exported.receipt.receipt_id);
}

#[test]
fn an_unused_alpha_ancestor_preserves_the_opaque_plan_selector() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let alpha = alpha_image(&f, "unused-alpha.png", 2, 1, &[1, 2, 3, 0, 4, 5, 6, 128]);
    let mut opaque = image(&f, "derived-opaque.png", &[20, 30, 40, 50, 60, 70]);
    opaque.origin = Origin::Derived {
        inputs: vec![SourceRange {
            asset: alpha.expected_hash.clone(),
            stream: MediaKind::Image,
            range: Span {
                start: 0,
                length: 1,
            },
        }],
        recipe: ContentHash::parse("3".repeat(64)).unwrap(),
        receipt: ContentHash::parse("4".repeat(64)).unwrap(),
    };
    let audio = wav_with_frames(&f, 48_000);
    let mut request = edit(initial.revision, "unused-alpha-edit", "main");
    request.imports = vec![alpha.clone(), opaque.clone(), audio.clone()];
    request.timelines[0].video_tracks = vec![VideoTrack {
        id: id("picture"),
        clips: vec![VideoClip {
            id: id("opaque-hold"),
            timeline_frames: Span {
                start: 0,
                length: 24,
            },
            asset: opaque.expected_hash.clone(),
            source_samples: Span {
                start: 0,
                length: 1,
            },
            cadence: Cadence::Hold { ordinal: 0 },
            framing: Some(Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    x: 0.0,
                    y: 0.0,
                    width: 1.0,
                    height: 1.0,
                },
            }),
            placement: None,
            motion: None,
            mask: None,
        }],
    }];
    request.timelines[0].audio_tracks = vec![AudioTrack {
        id: id("audio"),
        clips: vec![AudioClip {
            id: id("pcm"),
            timeline_samples: Span {
                start: 0,
                length: 48_000,
            },
            source_samples: Span {
                start: 0,
                length: 48_000,
            },
            asset: audio.expected_hash,
            source_rate: 48_000,
            gain: 1.0,
            pan: 0.0,
        }],
    }];
    let committed = p.commit(request).unwrap();
    let prepared = p
        .prepare_export(ExportRequest {
            intent: id("unused-alpha-plan"),
            revision: committed.revision,
            timeline: id("main"),
            profile: MovieProfile::H264AacMp4 {
                video_bitrate: 1_000_000,
                audio_bitrate: 192_000,
            },
        })
        .unwrap();
    assert_eq!(prepared.plan.schema, 3);
    assert!(prepared.plan.alpha_policy.is_none());
    assert!(
        prepared
            .plan
            .source_closure
            .contains_key(&alpha.expected_hash)
    );
    assert_eq!(prepared.plan.image_decode_evidence.len(), 1);
    assert_eq!(
        prepared.plan.image_decode_evidence[0].asset,
        opaque.expected_hash
    );
    assert!(
        prepared.plan.image_decode_evidence[0]
            .source_alpha_id
            .is_none()
    );
}

#[test]
fn a_crop_that_samples_only_an_alpha_hole_fails_runtime_coverage_before_publication() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let picture = alpha_image(
        &f,
        "cropped-alpha-hole.png",
        2,
        1,
        &[200, 10, 20, 0, 30, 40, 250, 255],
    );
    let audio = wav_with_frames(&f, 2_000);
    let mut request = edit(initial.revision, "alpha-hole-edit", "main");
    request.timelines[0].frame_count = 1;
    request.imports = vec![picture.clone(), audio.clone()];
    request.timelines[0].video_tracks = vec![VideoTrack {
        id: id("picture"),
        clips: vec![VideoClip {
            id: id("alpha-hole"),
            timeline_frames: Span {
                start: 0,
                length: 1,
            },
            asset: picture.expected_hash,
            source_samples: Span {
                start: 0,
                length: 1,
            },
            cadence: Cadence::Hold { ordinal: 0 },
            framing: Some(Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    x: 0.0,
                    y: 0.0,
                    width: 0.5,
                    height: 1.0,
                },
            }),
            placement: None,
            motion: None,
            mask: None,
        }],
    }];
    request.timelines[0].audio_tracks = vec![AudioTrack {
        id: id("audio"),
        clips: vec![AudioClip {
            id: id("pcm"),
            timeline_samples: Span {
                start: 0,
                length: 2_000,
            },
            source_samples: Span {
                start: 0,
                length: 2_000,
            },
            asset: audio.expected_hash,
            source_rate: 48_000,
            gain: 1.0,
            pan: 0.0,
        }],
    }];
    let committed = p.commit(request).unwrap();
    let export = ExportRequest {
        intent: id("alpha-hole-export"),
        revision: committed.revision,
        timeline: id("main"),
        profile: MovieProfile::H264AacMp4 {
            video_bitrate: 1_000_000,
            audio_bitrate: 192_000,
        },
    };
    assert_eq!(p.prepare_export(export.clone()).unwrap().plan.schema, 7);
    assert_eq!(p.export(export.clone()).unwrap_err().code, "video_coverage");
    assert!(p.verify_export(export.intent).is_err());
}

#[test]
fn image_cadence_and_single_sample_range_fail_atomically() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let input = image(&f, "source.png", &[255, 0, 0, 0, 0, 255]);
    let mut request = edit(initial.revision.clone(), "image-cadence", "main");
    request.imports.push(input.clone());
    request.timelines[0].video_tracks = vec![VideoTrack {
        id: id("picture"),
        clips: vec![VideoClip {
            motion: None,
            mask: None,
            placement: None,
            id: id("image-hold"),
            timeline_frames: Span {
                start: 0,
                length: 24,
            },
            asset: input.expected_hash,
            source_samples: Span {
                start: 0,
                length: 1,
            },
            cadence: Cadence::SourcePresentationTime,
            framing: None,
        }],
    }];
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "unsupported_image_cadence"
    );
    request.timelines[0].video_tracks[0].clips[0].cadence = Cadence::Hold { ordinal: 0 };
    request.timelines[0].video_tracks[0].clips[0]
        .source_samples
        .length = 2;
    assert_eq!(p.commit(request.clone()).unwrap_err().code, "source_bounds");
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    request.timelines[0].video_tracks[0].clips[0]
        .source_samples
        .length = 1;
    assert_eq!(p.commit(request).unwrap().sequence, 1);
}

fn layered_request(f: &Fixture, base: ContentHash) -> CommitProject {
    let picture = image(f, "layer-source.png", &[240, 20, 0, 240, 20, 0]);
    let audio = wav_with_frames(f, 48000);
    let mut request = edit(base, "layered-edit", "layers");
    request.imports = vec![picture.clone(), audio.clone()];
    let base_clip = VideoClip {
        id: id("base"),
        timeline_frames: Span {
            start: 0,
            length: 24,
        },
        asset: picture.expected_hash,
        source_samples: Span {
            start: 0,
            length: 1,
        },
        cadence: Cadence::Hold { ordinal: 0 },
        framing: Some(Framing {
            fit: PictureFit::Stretch,
            crop: NormalizedCrop {
                x: 0.0,
                y: 0.0,
                width: 1.0,
                height: 1.0,
            },
        }),
        motion: None,
        mask: None,
        placement: None,
    };
    let mut upper = base_clip.clone();
    upper.id = id("overlay");
    upper.timeline_frames = Span {
        start: 6,
        length: 6,
    };
    upper.placement = Some(PicturePlacement {
        destination: PixelRect {
            x: -50,
            y: 30,
            width: 160,
            height: 90,
        },
        opacity: Opacity::new(0.5).unwrap(),
    });
    request.timelines[0].video_tracks = vec![
        VideoTrack {
            id: id("lower"),
            clips: vec![base_clip],
        },
        VideoTrack {
            id: id("upper"),
            clips: vec![upper],
        },
    ];
    request.timelines[0].audio_tracks = vec![AudioTrack {
        id: id("audio"),
        clips: vec![AudioClip {
            id: id("pcm"),
            timeline_samples: Span {
                start: 0,
                length: 48000,
            },
            asset: audio.expected_hash,
            source_samples: Span {
                start: 0,
                length: 48000,
            },
            source_rate: 48000,
            gain: 1.0,
            pan: 0.0,
        }],
    }];
    request
}
fn layer_export(revision: ContentHash, intent: &str) -> ExportRequest {
    ExportRequest {
        intent: id(intent),
        revision,
        timeline: id("layers"),
        profile: MovieProfile::H264AacMp4 {
            video_bitrate: 2000000,
            audio_bitrate: 192000,
        },
    }
}

#[test]
fn sparse_layer_plans_normalize_defaults_and_native_export_keeps_receipt_identity() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let committed = p.commit(layered_request(&f, initial.revision)).unwrap();
    assert_eq!(p.head().unwrap().snapshot.schema, 1);
    let export = layer_export(committed.revision, "layers-export");
    let prepared = p.prepare_export(export.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 4);
    assert_eq!(prepared.plan.video[0].track, id("lower"));
    assert_eq!(prepared.plan.video[1].track, id("upper"));
    let base = prepared.plan.video[0].placement.as_ref().unwrap();
    assert_eq!(
        base.destination,
        PixelRect {
            x: 0,
            y: 0,
            width: 320,
            height: 180
        }
    );
    assert_eq!(base.opacity.value(), 1.0);
    assert!(p.prepare_export(export.clone()).unwrap().replayed);
    let result = p.export(export).unwrap();
    let counters = result.picture_execution.as_ref().unwrap();
    assert_eq!(counters.track_workers, 2);
    assert_eq!(counters.composed_frames, 24);
    assert!(counters.maximum_reserved_payload_bytes <= counters.admitted_payload_bytes);
    assert_eq!(result.receipt.artifact.schema, 2);
    let reopened = p.verify_export(id("layers-export")).unwrap();
    assert_eq!(reopened.receipt.receipt_id, result.receipt.receipt_id);
    assert_eq!(
        reopened.receipt.artifact.output_sha256,
        result.receipt.artifact.output_sha256
    );
    assert!(reopened.picture_execution.is_none());
}

#[test]
fn native_master_writes_reopens_exact_pcm_and_replays_receipt3_without_changing_picture_schema() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let committed = p.commit(layered_request(&f, initial.revision)).unwrap();
    let mut request = layer_export(committed.revision, "master-export");
    request.profile = MovieProfile::NativeColorMasterV1;
    let prepared = p.prepare_export(request.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 4);
    let result = p.export(request.clone()).unwrap();
    let receipt = &result.receipt.artifact;
    assert_eq!(receipt.schema, 3);
    assert_eq!(receipt.output_path.extension().unwrap(), "mov");
    assert_eq!(receipt.technical.video_track.codec, "ap4h");
    assert_eq!(receipt.technical.audio_track.codec, "lpcm");
    assert!(receipt.technical.video_color.is_none());
    assert_eq!(
        receipt
            .technical
            .audio_track
            .pcm_encoding
            .as_ref()
            .unwrap()
            .format_flags,
        12
    );
    assert_eq!(
        receipt
            .technical
            .pcm24_comparison
            .as_ref()
            .unwrap()
            .maximum_code_delta,
        0
    );
    assert_eq!(
        receipt
            .technical
            .pcm24_comparison
            .as_ref()
            .unwrap()
            .sample_frames,
        48000
    );
    assert_eq!(
        p.verify_export(request.intent.clone())
            .unwrap()
            .receipt
            .receipt_id,
        result.receipt.receipt_id
    );
    let replay = p.export(request).unwrap();
    assert!(replay.replayed);
    assert_eq!(replay.receipt.receipt_id, result.receipt.receipt_id);
}

#[test]
fn native_master_v2_records_rec709_on_every_reopened_path_and_replays_receipt4() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let committed = p.commit(layered_request(&f, initial.revision)).unwrap();
    let mut request = layer_export(committed.revision, "rec709-master-export");
    request.profile = MovieProfile::NativeColorMasterV2;
    let prepared = p.prepare_export(request.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 4);

    let result = p.export(request.clone()).unwrap();
    let receipt = &result.receipt.artifact;
    assert_eq!(receipt.schema, 4);
    assert_eq!(receipt.output_path.extension().unwrap(), "mov");
    assert_eq!(receipt.technical.video_track.codec, "ap4h");
    assert_eq!(receipt.technical.audio_track.codec, "lpcm");
    let tuple = video_studio::NativeColorTupleEvidence {
        color_primaries: "ITU_R_709_2".into(),
        transfer_function: "ITU_R_709_2".into(),
        y_cb_cr_matrix: "ITU_R_709_2".into(),
    };
    assert_eq!(
        receipt.technical.video_color,
        Some(video_studio::NativeVideoColorEvidence {
            encoded_samples: tuple.clone(),
            decoded_buffers: tuple,
        })
    );
    assert_eq!(
        receipt
            .technical
            .pcm24_comparison
            .as_ref()
            .unwrap()
            .maximum_code_delta,
        0
    );

    let verified = p.verify_export(request.intent.clone()).unwrap();
    assert_eq!(verified.receipt.receipt_id, result.receipt.receipt_id);
    assert_eq!(
        verified.receipt.artifact.technical.video_color,
        result.receipt.artifact.technical.video_color
    );
    let replay = p.export(request).unwrap();
    assert!(replay.replayed);
    assert_eq!(replay.receipt.receipt_id, result.receipt.receipt_id);
}

#[test]
fn invisible_layers_cannot_hide_coverage_gaps_and_same_track_overlap_is_atomic() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision.clone());
    let mut overlap = request.timelines[0].video_tracks[0].clips[0].clone();
    overlap.id = id("overlap");
    request.timelines[0].video_tracks[0].clips.push(overlap);
    assert_eq!(p.commit(request).unwrap_err().code, "track_overlap");
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    let mut request = layered_request(&f, initial.revision);
    request.timelines[0].video_tracks[0].clips[0].placement = Some(PicturePlacement {
        destination: PixelRect {
            x: 0,
            y: 0,
            width: 320,
            height: 180,
        },
        opacity: Opacity::new(0.0).unwrap(),
    });
    let committed = p.commit(request).unwrap();
    assert_eq!(
        p.prepare_export(layer_export(committed.revision, "invisible-plan"))
            .unwrap_err()
            .code,
        "video_coverage"
    );
}

#[test]
fn declared_constant_motion_selects_schema5_and_native_fades_keep_sparse_static_uses() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision);
    let motion: PictureMotion =
        serde_json::from_value(serde_json::json!({"x":{"keys":[{"frame":0,"value":0}]}})).unwrap();
    request.timelines[0].video_tracks[0].clips[0].motion = Some(motion);
    request.timelines[0].video_tracks[1].clips[0].motion = Some(
        serde_json::from_value(serde_json::json!({
            "x":{"keys":[{"frame":0,"value":-50,"to_next":"linear"},{"frame":5,"value":50}]},
            "opacity":{"keys":[{"frame":0,"value":0.0,"to_next":"linear"},{"frame":5,"value":1.0}]}
        }))
        .unwrap(),
    );
    // A second clip exercises the declared-static use within a schema-5 plan.
    let mut static_clip = request.timelines[0].video_tracks[1].clips[0].clone();
    static_clip.id = id("static-after-motion");
    static_clip.timeline_frames = Span {
        start: 18,
        length: 4,
    };
    static_clip.motion = None;
    request.timelines[0].video_tracks[1].clips.push(static_clip);
    let committed = p.commit(request).unwrap();
    let export = layer_export(committed.revision, "motion-native");
    let prepared = p.prepare_export(export.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 5);
    for use_ in &prepared.plan.video[..2] {
        assert!(use_.motion.is_some());
        assert!(use_.placement.is_none());
    }
    assert!(matches!(
        prepared.plan.video[0].motion.as_ref().unwrap().x,
        PlannedCurve::Constant { value: 0 }
    ));
    assert!(prepared.plan.video[2].placement.is_some());
    assert!(prepared.plan.video[2].motion.is_none());
    let result = p.export(export).unwrap();
    let evidence = result.picture_execution.as_ref().unwrap();
    assert_eq!(evidence.composed_frames, 24);
    assert!(evidence.maximum_reserved_payload_bytes <= evidence.admitted_payload_bytes);
    assert_eq!(result.receipt.artifact.schema, 2);
    assert_eq!(
        p.verify_export(id("motion-native"))
            .unwrap()
            .receipt
            .receipt_id,
        result.receipt.receipt_id
    );
}

#[test]
fn malformed_motion_is_atomic_and_frame_specific_invisibility_rejects_the_plan() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision.clone());
    request.timelines[0].video_tracks[0].clips[0].motion = Some(
        serde_json::from_value(serde_json::json!({
            "opacity":{"keys":[{"frame":1,"value":1.0}]}
        }))
        .unwrap(),
    );
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "invalid_picture_motion"
    );
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    request.timelines[0].video_tracks[0].clips[0].motion = Some(
        serde_json::from_value(serde_json::json!({
            "opacity":{"keys":[{"frame":0,"value":0.0,"to_next":"step"},{"frame":1,"value":1.0}]}
        }))
        .unwrap(),
    );
    let committed = p.commit(request).unwrap();
    assert_eq!(
        p.prepare_export(layer_export(committed.revision, "invisible-motion"))
            .unwrap_err()
            .code,
        "video_coverage"
    );
}

#[test]
fn constant_mask_selects_schema6_even_on_one_track_without_placement_or_motion() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision);
    request.timelines[0].video_tracks.truncate(1);
    request.timelines[0].video_tracks[0].clips[0].mask = Some(serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":0,"value":1.0}]},"inverted":false})).unwrap());
    let revision = p.commit(request).unwrap();
    let export = layer_export(revision.revision, "constant-mask");
    let prepared = p.prepare_export(export.clone()).unwrap();
    assert_eq!(prepared.plan.schema, 6);
    assert!(prepared.plan.video[0].placement.is_some());
    assert!(prepared.plan.video[0].motion.is_none());
    assert!(prepared.plan.video[0].mask.is_some());
    assert_eq!(prepared.plan.video[0].presentation_ordinals, vec![0; 24]);
    let replay = p.prepare_export(export).unwrap();
    assert!(replay.replayed);
    assert_eq!(replay.plan_id, prepared.plan_id);
}

#[test]
fn malformed_mask_is_atomic_and_hidden_only_frame_fails_before_execution() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision.clone());
    request.timelines[0].video_tracks[0].clips[0].mask = Some(serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":1,"value":1.0}]},"inverted":false})).unwrap());
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "invalid_picture_mask"
    );
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    request.timelines[0].video_tracks[0].clips[0].mask = Some(serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":0,"value":0.0,"to_next":"step"},{"frame":1,"value":1.0}]},"inverted":false})).unwrap());
    let revision = p.commit(request).unwrap();
    assert_eq!(
        p.prepare_export(layer_export(revision.revision, "uncovered-mask"))
            .unwrap_err()
            .code,
        "video_coverage"
    );
}

#[test]
fn excessive_track_and_picture_budget_are_rejected_before_execution() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let mut request = layered_request(&f, initial.revision);
    let base = request.timelines[0].video_tracks[0].clips[0].clone();
    for n in 2..5 {
        let mut clip = base.clone();
        clip.id = id(&format!("clip-{n}"));
        request.timelines[0].video_tracks.push(VideoTrack {
            id: id(&format!("track-{n}")),
            clips: vec![clip],
        });
    }
    let committed = p.commit(request).unwrap();
    assert_eq!(
        p.prepare_export(layer_export(committed.revision, "five-tracks"))
            .unwrap_err()
            .code,
        "unsupported_picture_tracks"
    );
    let initial = s
        .create_project(CreateProject {
            project: id("budget"),
            intent: id("create-budget"),
            name: "Budget".into(),
            settings: Settings {
                width: 8192,
                height: 4096,
                frame_rate: Rate {
                    numerator: 24,
                    denominator: 1,
                },
                audio_rate: 48000,
                channels: 2,
                working_color: "source-sample-values-unmanaged".into(),
            },
        })
        .unwrap();
    let p = s.project(id("budget")).unwrap();
    let request = layered_request(&f, initial.revision);
    let committed = p.commit(request).unwrap();
    assert_eq!(
        p.prepare_export(layer_export(committed.revision, "oversized-budget"))
            .unwrap_err()
            .code,
        "unsupported_picture_budget"
    );
}

#[test]
fn native_pcm_import_measures_bytes_clock_and_detects_tampering() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let input = wav(&f);
    let hash = input.expected_hash.clone();
    let mut request = edit(initial.revision, "bind-audio", "main");
    request.imports.push(input.clone());
    request.canonical_audio = Some(AudioBinding {
        asset: hash.clone(),
        source_samples: Span {
            start: 0,
            length: 480,
        },
        source_rate: 48000,
        channel_order: vec!["left".into(), "right".into()],
        channel_order_basis: "Explicit test fixture channel layout".into(),
    });
    let receipt = p.commit(request).unwrap();
    let inspection = p.verify_assets(receipt.revision.clone()).unwrap();
    assert!(matches!(
        inspection.snapshot.assets[&hash].descriptor,
        MediaDescriptor::Audio {
            rate: 48000,
            channels: 2,
            bits: 16,
            sample_frames: 480,
            ..
        }
    ));
    fs::remove_file(input.path).unwrap();
    assert_eq!(
        p.verify_assets(receipt.revision.clone())
            .unwrap()
            .receipt
            .sequence,
        1
    );
    let blob = f.0.join("state/blobs").join(hash.as_str());
    let mut permissions = fs::metadata(&blob).unwrap().permissions();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        permissions.set_mode(0o600);
    }
    fs::set_permissions(&blob, permissions).unwrap();
    fs::write(blob, b"changed bytes").unwrap();
    assert_eq!(
        p.verify_assets(receipt.revision).unwrap_err().code,
        "asset_tampered"
    );
}

#[test]
fn bad_audio_clock_or_source_range_cannot_commit() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let input = wav(&f);
    let mut request = edit(initial.revision.clone(), "bind", "main");
    request.imports.push(input.clone());
    request.canonical_audio = Some(AudioBinding {
        asset: input.expected_hash,
        source_samples: Span {
            start: 0,
            length: 481,
        },
        source_rate: 48000,
        channel_order: vec!["left".into(), "right".into()],
        channel_order_basis: "explicit".into(),
    });
    assert_eq!(p.commit(request.clone()).unwrap_err().code, "source_bounds");
    assert_eq!(p.head().unwrap().receipt.revision, initial.revision);
    let audio = request.canonical_audio.as_mut().unwrap();
    audio.source_samples.length = 480;
    audio.source_rate = 44100;
    assert_eq!(p.commit(request).unwrap_err().code, "audio_binding");
}

#[test]
fn source_measurement_refresh_requires_exact_previous_metadata_and_preserves_origin() {
    let f = Fixture::new();
    let s = f.studio();
    let initial = create(&s);
    let p = s.project(id("test")).unwrap();
    let input = wav(&f);
    let hash = input.expected_hash.clone();
    let mut request = edit(initial.revision, "bind-measurement", "main");
    request.imports.push(input.clone());
    let first = p.commit(request).unwrap();
    let previous = p
        .inspect(first.revision.clone())
        .unwrap()
        .asset_measurements[&input.expected_hash]
        .clone();
    let mut request = edit(first.revision.clone(), "refresh-measurement", "main");
    let mut refresh = input;
    refresh.previous_measurement = Some(ContentHash::parse("0".repeat(64)).unwrap());
    request.imports.push(refresh);
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "measurement_conflict"
    );
    request.imports[0].previous_measurement = Some(previous.clone());
    let origin = request.imports[0].origin.clone();
    request.imports[0].origin = Origin::Imported {
        external_source: "changed-origin".into(),
        role: "other".into(),
    };
    assert_eq!(
        p.commit(request.clone()).unwrap_err().code,
        "origin_conflict"
    );
    assert_eq!(p.head().unwrap().receipt.revision, first.revision);
    request.imports[0].origin = origin;
    request.imports[0].media_kind = MediaKind::Movie;
    assert_eq!(p.commit(request.clone()).unwrap_err().code, "wrong_stream");
    assert_eq!(p.head().unwrap().receipt.revision, first.revision);
    request.imports[0].media_kind = MediaKind::Audio;
    let measurement = p.inspect(first.revision.clone()).unwrap().snapshot.assets[&hash]
        .measurement
        .clone()
        .unwrap();
    assert_eq!(measurement.schema, 1);
    assert_eq!(measurement.producer.architecture, std::env::consts::ARCH);
    let second = p.commit(request.clone()).unwrap();
    assert!(p.commit(request).unwrap().replayed);
    assert_eq!(
        p.inspect(second.revision).unwrap().asset_measurements[&hash],
        previous
    );
}
