use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, mpsc};
use std::thread;
use std::time::Duration;
use std::time::{SystemTime, UNIX_EPOCH};

use rusqlite::{OptionalExtension, TransactionBehavior, params};
use serde::{Deserialize, Serialize};

use crate::export_stage::{ExportStage, Reclamation, StageOwner};
use crate::publication::{self, ActiveClaim, SealedStage, VerifiedOutput};
use crate::{
    BuildIdentity, ContentHash, EntityId, ExportRequest, NativeMeasurements, Project, Result,
    StudioError, movie,
};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArtifactReceipt {
    pub schema: u32,
    pub project: EntityId,
    pub revision: ContentHash,
    pub plan_id: ContentHash,
    pub renderer: BuildIdentity,
    pub output_path: PathBuf,
    pub output_sha256: ContentHash,
    pub output_bytes: u64,
    pub technical: NativeMeasurements,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{ExportPlan, MovieProfile, PreparedExport, Rate, Settings, Timeline};

    fn hash() -> ContentHash {
        ContentHash::parse("1".repeat(64)).unwrap()
    }
    fn id(value: &str) -> EntityId {
        EntityId::parse(value).unwrap()
    }
    fn measurements() -> NativeMeasurements {
        let video = crate::movie::NativeTrackEvidence {
            codec: "avc1".into(),
            sample_buffers: 48,
            raw_sample_pts_start: crate::MediaTime {
                ticks: 0,
                timescale: 24,
            },
            raw_sample_pts_end: crate::MediaTime {
                ticks: 48,
                timescale: 24,
            },
            audio_layout: None,
            pcm_encoding: None,
        };
        NativeMeasurements {
            streaming_audio: None,
            format: None,
            pcm24_comparison: None,
            video_color: None,
            video_frames: 48,
            audio_sample_frames: 96000,
            width: 16,
            height: 16,
            full_video_decode: true,
            audio_correlation: [0.9999705560560641, 0.9999708586933663],
            video_track: video.clone(),
            audio_track: crate::movie::NativeTrackEvidence {
                codec: "aac ".into(),
                audio_layout: Some((48000, 2)),
                ..video
            },
        }
    }
    fn rec709_evidence() -> crate::NativeVideoColorEvidence {
        let tuple = crate::NativeColorTupleEvidence {
            color_primaries: "ITU_R_709_2".into(),
            transfer_function: "ITU_R_709_2".into(),
            y_cb_cr_matrix: "ITU_R_709_2".into(),
        };
        crate::NativeVideoColorEvidence {
            encoded_samples: tuple.clone(),
            decoded_buffers: tuple,
        }
    }
    fn fixture() -> (Project, PreparedExport, StoredArtifact) {
        let root = std::env::temp_dir().join(format!(
            "studio-export-receipt-{}-{}",
            std::process::id(),
            DOCUMENT_COUNTER.fetch_add(1, Ordering::Relaxed)
        ));
        let studio = crate::Studio::open(&root).unwrap();
        let project = Project {
            studio,
            id: id("receipt-test"),
        };
        let build = BuildIdentity::current().unwrap();
        let prepared = PreparedExport {
            plan_id: hash(),
            replayed: false,
            plan: ExportPlan {
                schema: 2,
                project: project.id.clone(),
                revision: hash(),
                timeline: Timeline {
                    id: id("test"),
                    frame_count: 48,
                    video_tracks: vec![],
                    audio_tracks: vec![],
                },
                settings: Settings {
                    width: 16,
                    height: 16,
                    frame_rate: Rate {
                        numerator: 24,
                        denominator: 1,
                    },
                    audio_rate: 48000,
                    channels: 2,
                    working_color: "rec709".into(),
                },
                canonical_audio: None,
                profile: MovieProfile::H264AacMp4 {
                    video_bitrate: 1000000,
                    audio_bitrate: 192000,
                },
                renderer: build.clone(),
                source_closure: Default::default(),
                video: vec![],
                audio: vec![],
                timeline_sample_frames: 96000,
                decode_evidence: vec![],
                image_decode_evidence: vec![],
                alpha_policy: None,
            },
        };
        let artifact = ArtifactReceipt {
            schema: 2,
            project: project.id.clone(),
            revision: hash(),
            plan_id: hash(),
            renderer: build,
            output_path: project
                .studio
                .root
                .join("artifacts")
                .join(format!("{}.mp4", hash().as_str())),
            output_sha256: hash(),
            output_bytes: 42,
            technical: measurements(),
        };
        let receipt_id = ContentHash::document(&artifact).unwrap();
        fs::write(
            project
                .studio
                .root
                .join("receipts")
                .join(format!("{}.json", receipt_id.as_str())),
            serde_json::to_vec(&artifact).unwrap(),
        )
        .unwrap();
        let path = project
            .studio
            .root
            .join("receipts")
            .join(format!("{}.json", receipt_id.as_str()));
        let mut permissions = fs::metadata(&path).unwrap().permissions();
        permissions.set_readonly(true);
        fs::set_permissions(path, permissions).unwrap();
        (
            project,
            prepared,
            StoredArtifact {
                receipt_id,
                artifact,
            },
        )
    }

    fn plan7(project: EntityId) -> ExportPlan {
        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema5.json"))
                .unwrap();
        plan.schema = 7;
        plan.project = project;
        plan.alpha_policy = Some(crate::AlphaPolicy::StraightRgbaPremulUnorm16Q16V1);
        let asset = plan.image_decode_evidence[0].asset.clone();
        let stored = plan.source_closure.get_mut(&asset).unwrap();
        let crate::MediaDescriptor::Image {
            width,
            height,
            rgba_sha256,
            alpha,
            ..
        } = &mut stored.descriptor
        else {
            panic!("legacy image evidence must reference an image")
        };
        let pixels = u64::from(*width) * u64::from(*height);
        let facts = crate::ImageAlphaV1 {
            schema: 1,
            alpha_sha256: ContentHash::bytes(b"plan7-recovery-alpha-plane"),
            minimum: 0,
            maximum: 255,
            nonzero_pixels: pixels - 1,
            nonopaque_pixels: 1,
        };
        *alpha = Some(facts.clone());
        plan.image_decode_evidence[0].source_alpha_id =
            Some(crate::alpha_picture::source_alpha_id(&asset, rgba_sha256, &facts).unwrap());
        crate::plan::validate_decode_evidence(&plan).unwrap();
        plan
    }

    #[test]
    fn mastering_receipt_requires_complete_matching_profile_format_and_pcm_evidence() {
        let (project, _, stored) = fixture();
        let master = crate::native_format::NativeFormatContract::for_profile(
            &MovieProfile::NativeColorMasterV1,
        )
        .unwrap();
        let master_v2 = crate::native_format::NativeFormatContract::for_profile(
            &MovieProfile::NativeColorMasterV2,
        )
        .unwrap();
        let legacy =
            crate::native_format::NativeFormatContract::for_profile(&MovieProfile::H264AacMp4 {
                video_bitrate: 1000000,
                audio_bitrate: 192000,
            })
            .unwrap();
        let mut receipt = stored.artifact;
        assert!(
            master
                .validate_receipt(&project.studio.root, &receipt)
                .is_err()
        );
        let mut h264_with_color = receipt.clone();
        h264_with_color.technical.video_color = Some(rec709_evidence());
        assert!(
            legacy
                .validate_receipt(&project.studio.root, &h264_with_color)
                .is_err()
        );
        receipt.schema = 3;
        receipt.output_path = master.artifact_path(&project.studio.root, &receipt.output_sha256);
        receipt.technical.video_track.codec = "ap4h".into();
        receipt.technical.audio_track.codec = "lpcm".into();
        receipt.technical.format = Some(crate::NativeFormatEvidence {
            major_brand: crate::FourCc::try_from(String::from("qt  ")).unwrap(),
            compatible_brands: vec![],
        });
        receipt.technical.pcm24_comparison = Some(crate::Pcm24Comparison {
            sample_frames: 96000,
            maximum_code_delta: 0,
        });
        receipt.technical.audio_track.pcm_encoding = Some(crate::PcmEncodingEvidence {
            format_id: 0x6c70636d,
            format_flags: 12,
            bits_per_channel: 24,
            bytes_per_frame: 6,
            bytes_per_packet: 6,
            frames_per_packet: 1,
        });
        receipt.technical.streaming_audio = Some(crate::StreamingAudioEvidence {
            source: crate::PcmStreamEvidence {
                source_start_sample: 8191,
                source_end_sample: 104191,
                sample_frames: 96000,
                decoded_prefix_sample_frames: 104192,
                chunks: 24,
                maximum_owned_chunk_frames: 4096,
                reader_reached_end: false,
            },
            output: crate::PcmStreamEvidence {
                source_start_sample: 0,
                source_end_sample: 96000,
                sample_frames: 96000,
                decoded_prefix_sample_frames: 96000,
                chunks: 24,
                maximum_owned_chunk_frames: 4096,
                reader_reached_end: true,
            },
        });
        receipt.technical.audio_track.raw_sample_pts_end = crate::MediaTime {
            ticks: 96000,
            timescale: 48000,
        };
        master
            .validate_receipt(&project.studio.root, &receipt)
            .unwrap();
        assert!(
            master_v2
                .validate_receipt(&project.studio.root, &receipt)
                .is_err()
        );
        let mut v2 = receipt.clone();
        v2.schema = 4;
        v2.technical.video_color = Some(rec709_evidence());
        master_v2
            .validate_receipt(&project.studio.root, &v2)
            .unwrap();
        assert!(master.validate_receipt(&project.studio.root, &v2).is_err());
        assert!(legacy.validate_receipt(&project.studio.root, &v2).is_err());
        for mutation in 0..5 {
            let mut changed = v2.clone();
            match mutation {
                0 => changed.schema = 3,
                1 => changed.technical.video_color = None,
                2 => {
                    changed
                        .technical
                        .video_color
                        .as_mut()
                        .unwrap()
                        .encoded_samples
                        .color_primaries = "SMPTE_C".into()
                }
                3 => {
                    changed
                        .technical
                        .video_color
                        .as_mut()
                        .unwrap()
                        .decoded_buffers
                        .transfer_function = "ITU_R_601_4".into()
                }
                _ => {
                    changed.technical.video_color = Some(crate::NativeVideoColorEvidence {
                        encoded_samples: rec709_evidence().encoded_samples,
                        decoded_buffers: crate::NativeColorTupleEvidence {
                            color_primaries: "ITU_R_709_2".into(),
                            transfer_function: "ITU_R_709_2".into(),
                            y_cb_cr_matrix: String::new(),
                        },
                    })
                }
            }
            assert!(
                master_v2
                    .validate_receipt(&project.studio.root, &changed)
                    .is_err()
            );
        }
        let mut forbidden = receipt.clone();
        forbidden.technical.video_color = Some(rec709_evidence());
        assert!(
            master
                .validate_receipt(&project.studio.root, &forbidden)
                .is_err()
        );
        assert!(
            legacy
                .validate_receipt(&project.studio.root, &receipt)
                .is_err()
        );
        for flags in [0, 4, 8, 13, 14, 44] {
            let mut changed = receipt.clone();
            changed
                .technical
                .audio_track
                .pcm_encoding
                .as_mut()
                .unwrap()
                .format_flags = flags;
            assert!(
                master
                    .validate_receipt(&project.studio.root, &changed)
                    .is_err()
            );
        }
        for field in 0..12 {
            let mut changed = receipt.clone();
            match field {
                0 => changed.schema = 2,
                1 => changed
                    .output_path
                    .set_extension("mp4")
                    .then_some(())
                    .unwrap(),
                2 => changed.technical.format = None,
                3 => changed.technical.audio_track.pcm_encoding = None,
                4 => changed.technical.pcm24_comparison = None,
                5 => {
                    changed
                        .technical
                        .pcm24_comparison
                        .as_mut()
                        .unwrap()
                        .maximum_code_delta = 1
                }
                6 => {
                    changed
                        .technical
                        .pcm24_comparison
                        .as_mut()
                        .unwrap()
                        .sample_frames -= 1
                }
                7 => {
                    changed
                        .technical
                        .audio_track
                        .pcm_encoding
                        .as_mut()
                        .unwrap()
                        .bits_per_channel = 16
                }
                8 => changed.technical.video_track.codec = "avc1".into(),
                9 => changed.technical.streaming_audio = None,
                10 => {
                    changed
                        .technical
                        .streaming_audio
                        .as_mut()
                        .unwrap()
                        .output
                        .reader_reached_end = false
                }
                _ => {
                    changed
                        .technical
                        .streaming_audio
                        .as_mut()
                        .unwrap()
                        .source
                        .maximum_owned_chunk_frames = 4097
                }
            }
            assert!(
                master
                    .validate_receipt(&project.studio.root, &changed)
                    .is_err()
            );
        }
        fs::remove_dir_all(project.studio.root).unwrap();
    }
    #[test]
    fn altered_measurements_cannot_replay_under_the_original_receipt_id() {
        let (project, prepared, mut stored) = fixture();
        project
            .read_artifact(&serde_json::to_string(&stored).unwrap(), &prepared)
            .unwrap();
        stored.artifact.technical.video_frames = 1;
        assert_eq!(
            project
                .read_artifact(&serde_json::to_string(&stored).unwrap(), &prepared)
                .unwrap_err()
                .code,
            "job_tampered"
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }
    #[test]
    fn a_new_hash_without_its_immutable_document_cannot_replay() {
        let (project, prepared, mut stored) = fixture();
        stored.artifact.technical.audio_correlation = [0.0; 2];
        stored.receipt_id = ContentHash::document(&stored.artifact).unwrap();
        assert_eq!(
            project
                .read_artifact(&serde_json::to_string(&stored).unwrap(), &prepared)
                .unwrap_err()
                .code,
            "io_error"
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }
    #[test]
    fn renderer_receipts_cannot_claim_perceptual_acceptance() {
        let (project, prepared, stored) = fixture();
        let mut body = serde_json::to_value(stored).unwrap();
        body["artifact"]["heard"] = serde_json::json!(true);
        assert_eq!(
            project
                .read_artifact(&body.to_string(), &prepared)
                .unwrap_err()
                .code,
            "invalid_json"
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }
    #[test]
    fn fresh_measurements_reject_changed_claims_and_accept_rounding_noise() {
        let stored = measurements();
        let mut fresh = stored.clone();
        fresh.audio_correlation[0] += 1e-12;
        stored.compare(&fresh).unwrap();
        fresh.audio_sample_frames = 1;
        assert_eq!(
            stored.compare(&fresh).unwrap_err().code,
            "measurement_changed"
        );
    }

    #[test]
    fn oversized_native_canvas_fails_preflight_before_any_pixel_allocation() {
        let (project, mut prepared, _) = fixture();
        prepared.plan.settings.width = 8192;
        prepared.plan.settings.height = 8192;
        assert_eq!(
            movie::validate_pixel_extents(&prepared.plan)
                .unwrap_err()
                .code,
            "unsupported_pixel_extent"
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }

    #[test]
    fn lease_renewal_cannot_change_a_newer_epoch_and_stops_on_cancellation() {
        let (project, _, _) = fixture();
        let intent = id("export");
        let db = project.studio.connection().unwrap();
        db.execute("INSERT INTO exports(project,intent,request_hash,epoch,state,owner_pid,expires_at) VALUES(?1,?2,?3,7,'running',?4,1)",params![project.id.as_str(),intent.as_str(),hash().as_str(),std::process::id()]).unwrap();
        assert_eq!(renew_claim(&project, &intent, 7).unwrap(), 0);
        let expires: u64 = db
            .query_row("SELECT expires_at FROM exports", [], |r| r.get(0))
            .unwrap();
        assert!(expires > unix_millis().unwrap());
        db.execute("UPDATE exports SET epoch=8,expires_at=123", [])
            .unwrap();
        assert_eq!(renew_claim(&project, &intent, 7).unwrap(), 1);
        assert_eq!(
            db.query_row("SELECT expires_at FROM exports", [], |r| r.get::<_, u64>(0))
                .unwrap(),
            123
        );
        assert_eq!(
            project.cancel_export(intent.clone()).unwrap().state,
            "cancellation_requested"
        );
        assert_eq!(renew_claim(&project, &intent, 8).unwrap(), 2);
        assert_eq!(
            project
                .failure_for_claim(
                    &intent,
                    8,
                    StudioError::new("worker_fenced", "late guard failure")
                )
                .unwrap()
                .code,
            "export_cancelled"
        );
        assert_eq!(
            project
                .failure_for_claim(&intent, 7, StudioError::new("worker_fenced", "old epoch"))
                .unwrap()
                .code,
            "worker_fenced"
        );
        db.execute(
            "UPDATE exports SET state='completed',cancel_requested=0",
            [],
        )
        .unwrap();
        assert_eq!(project.cancel_export(intent).unwrap().state, "completed");
        assert!(
            !db.query_row("SELECT cancel_requested FROM exports", [], |r| r
                .get::<_, bool>(0))
                .unwrap()
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }

    #[test]
    fn verification_rejects_a_corrupted_export_to_plan_request_binding() {
        let (project, prepared, stored) = fixture();
        let intent = id("verify");
        let request = ExportRequest {
            intent: intent.clone(),
            revision: prepared.plan.revision.clone(),
            timeline: prepared.plan.timeline.id.clone(),
            profile: prepared.plan.profile.clone(),
        };
        let request_hash = ContentHash::document(&request).unwrap();
        let plan_hash = ContentHash::document(&prepared.plan).unwrap();
        let db = project.studio.connection().unwrap();
        db.execute(
            "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
            params![
                project.id.as_str(),
                intent.as_str(),
                request_hash.as_str(),
                plan_hash.as_str(),
                serde_json::to_string(&prepared.plan).unwrap()
            ],
        )
        .unwrap();
        db.execute("INSERT INTO exports(project,intent,request_hash,epoch,state,owner_pid,expires_at,receipt) VALUES(?1,?2,?3,1,'completed',0,0,?4)",params![project.id.as_str(),intent.as_str(),hash().as_str(),serde_json::to_string(&stored).unwrap()]).unwrap();
        assert_eq!(
            project.verify_export(intent.clone()).unwrap_err().code,
            "job_tampered"
        );
        db.execute("UPDATE plans SET request_hash=?1", [hash().as_str()])
            .unwrap();
        assert_eq!(
            project.verify_export(intent).unwrap_err().code,
            "job_tampered"
        );
        fs::remove_dir_all(project.studio.root).unwrap();
    }

    #[test]
    fn staging_reconciliation_reclaims_only_retired_dead_owners_in_this_project() {
        let (project, _, _) = fixture();
        let dead = StageOwner {
            project: project.id.clone(),
            intent: id("dead"),
            epoch: 1,
            owner_pid: 0,
        };
        let live = StageOwner {
            intent: id("live"),
            owner_pid: std::process::id(),
            ..dead.clone()
        };
        let other = StageOwner {
            project: id("other-project"),
            ..dead.clone()
        };
        let mut paths = vec![];
        let db = project.studio.connection().unwrap();
        for owner in [&dead, &live, &other] {
            let stage = ExportStage::create(
                &project.studio.root,
                owner.clone(),
                crate::native_format::StagePayloadName::Mp4,
            )
            .unwrap();
            fs::write(stage.path(), b"interrupted").unwrap();
            paths.push(stage.path());
            std::mem::forget(stage);
            db.execute("INSERT INTO export_attempts(project,intent,epoch,owner_pid,claimed_at,state) VALUES(?1,?2,?3,?4,1,'abandoned')",params![owner.project.as_str(),owner.intent.as_str(),owner.epoch,owner.owner_pid]).unwrap();
        }
        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema2.json"))
                .unwrap();
        plan.project = project.id.clone();
        db.execute(
            "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
            params![
                project.id.as_str(),
                dead.intent.as_str(),
                hash().as_str(),
                ContentHash::document(&plan).unwrap().as_str(),
                serde_json::to_string(&plan).unwrap()
            ],
        )
        .unwrap();
        let report = project.reconcile_export_staging().unwrap();
        assert_eq!(report.reclaimed, vec![(dead.intent, 1)]);
        assert_eq!(
            report.retained,
            vec![(live.intent, 1, "Owner process remains alive".into())]
        );
        assert!(!paths[0].exists());
        assert_eq!(fs::read(&paths[1]).unwrap(), b"interrupted");
        assert_eq!(fs::read(&paths[2]).unwrap(), b"interrupted");
        fs::remove_dir_all(project.studio.root).unwrap();
    }

    #[test]
    fn plan7_staging_recovery_reclaims_valid_evidence_and_retains_forgery() {
        let (project, _, _) = fixture();
        let valid_intent = id("alpha-valid-stage");
        let invalid_intent = id("alpha-invalid-stage");
        let v2_intent = id("v2-valid-stage");
        let valid = plan7(project.id.clone());
        let mut invalid = valid.clone();
        invalid.image_decode_evidence[0].source_alpha_id = None;
        let mut v2 = valid.clone();
        v2.profile = MovieProfile::NativeColorMasterV2;
        let db = project.studio.connection().unwrap();
        let mut paths = Vec::new();
        for (intent, plan) in [
            (valid_intent.clone(), valid),
            (invalid_intent.clone(), invalid),
            (v2_intent.clone(), v2),
        ] {
            let owner = StageOwner {
                project: project.id.clone(),
                intent: intent.clone(),
                epoch: 1,
                owner_pid: 0,
            };
            let stage = ExportStage::create(
                &project.studio.root,
                owner.clone(),
                crate::native_format::NativeFormatContract::for_profile(&plan.profile)
                    .unwrap()
                    .stage_payload_name(),
            )
            .unwrap();
            fs::write(stage.path(), b"interrupted-plan7-export").unwrap();
            paths.push(stage.path());
            std::mem::forget(stage);
            db.execute(
                "INSERT INTO export_attempts(project,intent,epoch,owner_pid,claimed_at,state) VALUES(?1,?2,1,0,1,'abandoned')",
                params![project.id.as_str(), intent.as_str()],
            )
            .unwrap();
            db.execute(
                "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
                params![
                    project.id.as_str(),
                    intent.as_str(),
                    hash().as_str(),
                    ContentHash::document(&plan).unwrap().as_str(),
                    serde_json::to_string(&plan).unwrap()
                ],
            )
            .unwrap();
        }

        let report = project.reconcile_export_staging().unwrap();
        assert_eq!(report.reclaimed, vec![(valid_intent, 1), (v2_intent, 1)]);
        assert_eq!(report.retained.len(), 1);
        assert_eq!(report.retained[0].0, invalid_intent);
        assert_eq!(report.retained[0].1, 1);
        assert!(report.retained[0].2.contains("invalid_decode_evidence"));
        assert!(!paths[0].exists());
        assert_eq!(fs::read(&paths[1]).unwrap(), b"interrupted-plan7-export");
        assert!(!paths[2].exists());
        fs::remove_dir_all(project.studio.root).unwrap();
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredArtifact {
    pub receipt_id: ContentHash,
    pub artifact: ArtifactReceipt,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArtifactVerification {
    pub schema: u32,
    pub artifact_receipt: ContentHash,
    pub output_sha256: ContentHash,
    pub verifier: BuildIdentity,
    pub technical: NativeMeasurements,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExportResult {
    pub receipt: StoredArtifact,
    pub verification_id: ContentHash,
    pub verification: ArtifactVerification,
    pub replayed: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub picture_execution: Option<crate::PictureExecutionEvidence>,
}

static DOCUMENT_COUNTER: AtomicU64 = AtomicU64::new(0);

#[derive(Clone)]
pub(crate) struct ExportControl(Arc<std::sync::atomic::AtomicU8>);
impl ExportControl {
    #[cfg(test)]
    pub(crate) fn test_active() -> Self {
        Self(Arc::new(std::sync::atomic::AtomicU8::new(0)))
    }
    pub(crate) fn interrupt(&self) {
        let _ = self
            .0
            .compare_exchange(0, 4, Ordering::AcqRel, Ordering::Acquire);
    }
    pub(crate) fn check(&self) -> Result<()> {
        match self.0.load(Ordering::Acquire) {
            0 => Ok(()),
            2 => Err(StudioError::new(
                "export_cancelled",
                "Export cancellation was requested",
            )),
            3 => Err(StudioError::new(
                "lease_unavailable",
                "Export lease could not be renewed",
            )),
            4 => Err(StudioError::new(
                "export_interrupted",
                "Native frame evaluation was interrupted",
            )),
            _ => Err(StudioError::new(
                "worker_fenced",
                "Export worker lost its lease epoch",
            )),
        }
    }
}
pub(crate) struct ExportLease {
    control: ExportControl,
    stop: mpsc::Sender<()>,
    worker: Option<thread::JoinHandle<()>>,
}
impl Drop for ExportLease {
    fn drop(&mut self) {
        let _ = self.stop.send(());
        if let Some(worker) = self.worker.take() {
            let _ = worker.join();
        }
    }
}
impl ExportLease {
    pub(crate) fn start(project: Project, claim: ActiveClaim) -> Self {
        let control = ExportControl(Arc::new(std::sync::atomic::AtomicU8::new(0)));
        let signal = control.clone();
        let (stop, wait) = mpsc::channel();
        let worker = thread::spawn(move || {
            loop {
                if wait.recv_timeout(Duration::from_secs(10))
                    != Err(mpsc::RecvTimeoutError::Timeout)
                {
                    break;
                }
                let state = match publication::renew(&project, &claim) {
                    Ok(_) => 0,
                    Err(error) if error.code == "export_cancelled" => 2,
                    Err(error) if error.code == "worker_fenced" => 1,
                    Err(_) => 3,
                };
                if state != 0 {
                    signal.0.store(state, Ordering::Release);
                    break;
                }
            }
        });
        Self {
            control,
            stop,
            worker: Some(worker),
        }
    }

    pub(crate) fn control(&self) -> ExportControl {
        self.control.clone()
    }

    pub(crate) fn quiesce(mut self) -> Result<ExportControl> {
        let _ = self.stop.send(());
        if let Some(worker) = self.worker.take() {
            worker.join().map_err(|_| {
                StudioError::new("lease_unavailable", "Export renewal worker panicked")
            })?;
        }
        self.control.check()?;
        Ok(self.control.clone())
    }
}

#[cfg(test)]
fn renew_claim(project: &Project, intent: &EntityId, epoch: u64) -> Result<u8> {
    let db = project.studio.connection()?;
    let now = unix_millis()?;
    let changed = db.execute("UPDATE exports SET expires_at=?1 WHERE project=?2 AND intent=?3 AND epoch=?4 AND state IN ('running','finalizing') AND cancel_requested=0",params![now+240000,project.id.as_str(),intent.as_str(),epoch])?;
    if changed == 1 {
        return Ok(0);
    }
    let cancelled: Option<bool> = db
        .query_row(
            "SELECT cancel_requested FROM exports WHERE project=?1 AND intent=?2 AND epoch=?3",
            params![project.id.as_str(), intent.as_str(), epoch],
            |r| r.get(0),
        )
        .optional()?;
    Ok(if cancelled == Some(true) { 2 } else { 1 })
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExportCancellation {
    pub intent: EntityId,
    pub epoch: u64,
    pub state: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StagingReconciliation {
    pub project: EntityId,
    pub reclaimed: Vec<(EntityId, u64)>,
    pub retained: Vec<(EntityId, u64, String)>,
}

struct Job {
    request_hash: String,
    epoch: u64,
    state: String,
    owner_pid: u32,
    expires_at: u64,
    receipt: Option<String>,
    error: Option<String>,
}
struct VerificationJob {
    state: String,
    receipt: Option<String>,
    plan_id: String,
    plan_body: String,
    export_request_hash: String,
    plan_request_hash: String,
}

pub(crate) fn unix_millis() -> Result<u64> {
    u64::try_from(
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|e| StudioError::new("clock_error", e.to_string()))?
            .as_millis(),
    )
    .map_err(|_| StudioError::new("clock_error", "System clock overflow"))
}
fn alive(pid: u32) -> bool {
    let Ok(pid) = i32::try_from(pid) else {
        return false;
    };
    if pid <= 0 {
        return false;
    }
    unsafe { libc::kill(pid, 0) == 0 || *libc::__error() == libc::EPERM }
}

impl Project {
    pub fn verify_export(&self, intent: EntityId) -> Result<ExportResult> {
        let db = self.studio.connection()?;
        let existing: Option<VerificationJob> = db.query_row("SELECT e.state,e.receipt,p.hash,p.body,e.request_hash,p.request_hash FROM exports e JOIN plans p ON p.project=e.project AND p.intent=e.intent WHERE e.project=?1 AND e.intent=?2",params![self.id.as_str(),intent.as_str()],|r|Ok(VerificationJob {state:r.get(0)?,receipt:r.get(1)?,plan_id:r.get(2)?,plan_body:r.get(3)?,export_request_hash:r.get(4)?,plan_request_hash:r.get(5)?})).optional()?;
        let job = existing.ok_or_else(|| {
            StudioError::new("export_missing", "Prepared export and artifact are absent")
        })?;
        if job.state != "completed" {
            return Err(StudioError::new(
                "export_incomplete",
                "Only a completed export can be verified by this operation",
            ));
        }
        let plan: crate::ExportPlan = serde_json::from_str(&job.plan_body)?;
        let plan_id = ContentHash::parse(job.plan_id)?;
        if ContentHash::document(&plan)? != plan_id
            || plan.project != self.id
            || !matches!(plan.schema, 2..=7)
        {
            return Err(StudioError::new(
                "plan_tampered",
                "Stored export plan hash, schema or project changed",
            ));
        }
        let request = ExportRequest {
            intent,
            revision: plan.revision.clone(),
            timeline: plan.timeline.id.clone(),
            profile: plan.profile.clone(),
        };
        if job.export_request_hash != job.plan_request_hash
            || ContentHash::document(&request)?.as_str() != job.export_request_hash
        {
            return Err(StudioError::new(
                "job_tampered",
                "Export and plan do not bind the same immutable request",
            ));
        }
        self.inspect(plan.revision.clone())?;
        self.verify_plan_sources(&plan)?;
        let prepared = crate::PreparedExport {
            plan_id,
            plan,
            replayed: true,
        };
        let stored = self.read_artifact(
            &job.receipt.ok_or_else(|| {
                StudioError::new("job_tampered", "Completed export has no artifact receipt")
            })?,
            &prepared,
        )?;
        self.verify_artifact(stored, &prepared.plan, true, None)
    }
    pub fn cancel_export(&self, intent: EntityId) -> Result<ExportCancellation> {
        let mut db = self.studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let job: Option<(u64, String)> = tx
            .query_row(
                "SELECT epoch,state FROM exports WHERE project=?1 AND intent=?2",
                params![self.id.as_str(), intent.as_str()],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .optional()?;
        let (epoch, state) =
            job.ok_or_else(|| StudioError::new("export_missing", "Export intent is absent"))?;
        let state = if state == "running" || state == "finalizing" {
            tx.execute(
                "UPDATE exports SET cancel_requested=1 WHERE project=?1 AND intent=?2 AND epoch=?3",
                params![self.id.as_str(), intent.as_str(), epoch],
            )?;
            "cancellation_requested".into()
        } else {
            state
        };
        tx.commit()?;
        Ok(ExportCancellation {
            intent,
            epoch,
            state,
        })
    }
    fn store_verification(&self, value: &ArtifactVerification) -> Result<ContentHash> {
        let bytes = serde_json::to_vec(value)?;
        let id = ContentHash::document(value)?;
        let destination = self
            .studio
            .root
            .join("receipts")
            .join(format!("{}.json", id.as_str()));
        if destination.is_file() {
            crate::project::verify_blob(&destination, &id, bytes.len() as u64)?;
            return Ok(id);
        }
        let stage = self.studio.root.join("staging").join(format!(
            "receipt-{}-{}",
            std::process::id(),
            DOCUMENT_COUNTER.fetch_add(1, Ordering::Relaxed)
        ));
        let result = (|| {
            let mut file = OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&stage)?;
            file.write_all(&bytes)?;
            file.sync_all()?;
            match fs::hard_link(&stage, &destination) {
                Ok(()) => {
                    let mut permissions = fs::metadata(&destination)?.permissions();
                    permissions.set_readonly(true);
                    fs::set_permissions(&destination, permissions)?;
                    File::open(self.studio.root.join("receipts"))?.sync_all()?;
                }
                Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                    crate::project::verify_blob(&destination, &id, bytes.len() as u64)?;
                }
                Err(e) => return Err(e.into()),
            }
            Ok(id)
        })();
        let _ = fs::remove_file(&stage);
        result
    }

    fn read_artifact(
        &self,
        body: &str,
        prepared: &crate::PreparedExport,
    ) -> Result<StoredArtifact> {
        let value: serde_json::Value = serde_json::from_str(body)?;
        if value.get("schema").is_some() {
            return Err(StudioError::new(
                "unsupported_receipt_schema",
                "Historical receipt is preserved; use its producer or a new export intent",
            ));
        }
        let stored: StoredArtifact = serde_json::from_value(value)?;
        let receipt = &stored.artifact;
        if ContentHash::document(receipt)? != stored.receipt_id
            || receipt.project != self.id
            || receipt.plan_id != prepared.plan_id
            || receipt.revision != prepared.plan.revision
            || receipt.renderer != prepared.plan.renderer
        {
            return Err(StudioError::new(
                "job_tampered",
                "Export receipt identity or plan binding changed",
            ));
        }
        crate::native_format::NativeFormatContract::for_profile(&prepared.plan.profile)?
            .validate_receipt(&self.studio.root, receipt)?;
        publication::verify_receipt_document(self, &stored)?;
        Ok(stored)
    }

    fn measure_artifact(
        &self,
        stored: &StoredArtifact,
        plan: &crate::ExportPlan,
        control: Option<ExportControl>,
    ) -> Result<ArtifactVerification> {
        let receipt = &stored.artifact;
        crate::project::verify_blob(
            &receipt.output_path,
            &receipt.output_sha256,
            receipt.output_bytes,
        )?;
        let technical = if let Some(control) = &control {
            movie::verify_owned(
                plan,
                &self.studio.root.join("blobs"),
                &receipt.output_path,
                control.clone(),
            )?
        } else {
            movie::verify(plan, &self.studio.root.join("blobs"), &receipt.output_path)?
        };
        if let Some(control) = &control {
            control.check()?;
        }
        receipt.technical.compare(&technical)?;
        Ok(ArtifactVerification {
            schema: 1,
            artifact_receipt: stored.receipt_id.clone(),
            output_sha256: receipt.output_sha256.clone(),
            verifier: BuildIdentity::current()?,
            technical,
        })
    }

    fn save_verification(
        &self,
        stored: StoredArtifact,
        verification: ArtifactVerification,
        replayed: bool,
    ) -> Result<ExportResult> {
        let verification_id = self.store_verification(&verification)?;
        Ok(ExportResult {
            receipt: stored,
            verification_id,
            verification,
            replayed,
            picture_execution: None,
        })
    }

    fn verify_artifact(
        &self,
        stored: StoredArtifact,
        plan: &crate::ExportPlan,
        replayed: bool,
        control: Option<ExportControl>,
    ) -> Result<ExportResult> {
        let verification = self.measure_artifact(&stored, plan, control)?;
        self.save_verification(stored, verification, replayed)
    }

    pub fn export(&self, request: ExportRequest) -> Result<ExportResult> {
        let prepared = self.prepare_export(request.clone())?;
        movie::validate_profile(&prepared.plan)?;
        let format =
            crate::native_format::NativeFormatContract::for_profile(&prepared.plan.profile)?;
        let request_hash = ContentHash::document(&request)?;
        let now = unix_millis()?;
        let mut db = self.studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let existing:Option<Job>=tx.query_row("SELECT request_hash,epoch,state,owner_pid,expires_at,receipt,error FROM exports WHERE project=?1 AND intent=?2",params![self.id.as_str(),request.intent.as_str()],|row|Ok(Job {request_hash:row.get(0)?,epoch:row.get(1)?,state:row.get(2)?,owner_pid:row.get(3)?,expires_at:row.get(4)?,receipt:row.get(5)?,error:row.get(6)?})).optional()?;
        let mut recovery = None;
        let epoch = if let Some(job) = existing {
            if job.request_hash != request_hash.as_str() {
                return Err(StudioError::new(
                    "intent_conflict",
                    "Export intent already binds another request",
                ));
            }
            if job.state == "completed" {
                let body = job.receipt.ok_or_else(|| {
                    StudioError::new("job_tampered", "Completed job has no receipt")
                })?;
                let stored = self.read_artifact(&body, &prepared)?;
                tx.commit()?;
                return self.verify_artifact(stored, &prepared.plan, true, None);
            }
            if job.state == "failed" {
                return Err(StudioError::new(
                    "export_failed",
                    job.error.unwrap_or_else(|| {
                        "Preserved export failed; inspect it before a new intent".into()
                    }),
                ));
            }
            let cancelled: bool = tx.query_row(
                "SELECT cancel_requested FROM exports WHERE project=?1 AND intent=?2",
                params![self.id.as_str(), request.intent.as_str()],
                |r| r.get(0),
            )?;
            if job.state == "cancelled" || cancelled {
                return Err(StudioError::new(
                    "export_cancelled",
                    "This export intent was cancelled; use a new intent for another attempt",
                ));
            }
            if job.expires_at > now && alive(job.owner_pid) {
                return Err(StudioError::new(
                    "export_in_progress",
                    format!(
                        "Export epoch {} remains owned by process {}",
                        job.epoch, job.owner_pid
                    ),
                ));
            }
            if job.state == "finalizing" {
                recovery = job.receipt;
            }
            job.epoch.checked_add(1).ok_or_else(|| {
                StudioError::new("epoch_overflow", "Export fencing epoch overflow")
            })?
        } else {
            1
        };
        if prepared.plan.renderer != BuildIdentity::current()? {
            return Err(StudioError::new(
                "renderer_changed",
                "Prepared plan belongs to another native build; use a new export intent",
            ));
        }
        tx.execute("INSERT INTO exports(project,intent,request_hash,epoch,state,owner_pid,expires_at,receipt,error,cancel_requested) VALUES(?1,?2,?3,?4,'running',?5,?6,NULL,NULL,0) ON CONFLICT(project,intent) DO UPDATE SET epoch=excluded.epoch,state='running',owner_pid=excluded.owner_pid,expires_at=excluded.expires_at,receipt=NULL,error=NULL,cancel_requested=0",params![self.id.as_str(),request.intent.as_str(),request_hash.as_str(),epoch,std::process::id(),now+240000])?;
        tx.execute("UPDATE export_attempts SET state='abandoned',closed_at=?1 WHERE project=?2 AND intent=?3 AND state IN ('running','finalizing')",params![now,self.id.as_str(),request.intent.as_str()])?;
        tx.execute("INSERT INTO export_attempts(project,intent,epoch,owner_pid,claimed_at,state) VALUES(?1,?2,?3,?4,?5,'running')",params![self.id.as_str(),request.intent.as_str(),epoch,std::process::id(),now])?;
        tx.commit()?;
        let claim = ActiveClaim {
            intent: request.intent.clone(),
            request_hash: request_hash.clone(),
            plan_id: prepared.plan_id.clone(),
            epoch,
            owner_pid: std::process::id(),
        };
        let lease = ExportLease::start(self.clone(), claim.clone());
        let control = lease.control.clone();
        let result: Result<ExportResult> = (|| {
            self.reconcile_export_staging()?;
            if let Some(body) = recovery {
                let stored = self.read_artifact(&body, &prepared)?;
                match fs::symlink_metadata(&stored.artifact.output_path) {
                    Ok(_) => {
                        let verification =
                            self.measure_artifact(&stored, &prepared.plan, Some(control.clone()))?;
                        let published = publication::complete_legacy(self, &claim, stored, lease)
                            .map_err(|failure| failure.into_error())?
                            .into_stored();
                        return self.save_verification(published, verification, true);
                    }
                    Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
                    Err(error) => return Err(error.into()),
                }
            }
            publication::validate_layout(self)?;
            let stage_owner = ExportStage::create(
                &self.studio.root,
                StageOwner {
                    project: self.id.clone(),
                    intent: request.intent.clone(),
                    epoch,
                    owner_pid: std::process::id(),
                },
                format.stage_payload_name(),
            )?;
            let stage = stage_owner.path();
            let picture_execution = movie::write(
                &prepared.plan,
                &self.studio.root.join("blobs"),
                &stage,
                control.clone(),
            )?;
            control.check()?;
            File::open(&stage)?.sync_all()?;
            self.verify_plan_sources(&prepared.plan)?;
            let technical = movie::verify_owned(
                &prepared.plan,
                &self.studio.root.join("blobs"),
                &stage,
                control.clone(),
            )?;
            control.check()?;
            let sealed = SealedStage::seal(stage_owner, &control)?;
            let stored = publication::publish(
                self,
                &claim,
                &prepared,
                VerifiedOutput {
                    stage: sealed,
                    technical,
                },
                lease,
            )
            .map_err(|failure| failure.into_error())?
            .into_stored();
            let mut verified = self.verify_artifact(stored, &prepared.plan, false, None)?;
            verified.picture_execution = picture_execution;
            Ok(verified)
        })();
        match result {
            Err(error) if error.code == "publication_outcome_unknown" => Err(error),
            Err(error) => Err(self.close_failed_claim(&claim, &error)?),
            result => result,
        }
    }

    pub fn reconcile_export_staging(&self) -> Result<StagingReconciliation> {
        let db = self.studio.connection()?;
        let mut query = db.prepare("SELECT intent,epoch,owner_pid FROM export_attempts WHERE project=?1 AND state IN ('completed','abandoned','failed','cancelled','fenced') ORDER BY intent,epoch")?;
        let attempts = query.query_map([self.id.as_str()], |r| {
            Ok((
                r.get::<_, String>(0)?,
                r.get::<_, u64>(1)?,
                r.get::<_, u32>(2)?,
            ))
        })?;
        let mut result = StagingReconciliation {
            project: self.id.clone(),
            reclaimed: vec![],
            retained: vec![],
        };
        for attempt in attempts {
            let (intent, epoch, owner_pid) = attempt?;
            let intent = EntityId::parse(intent)?;
            let owner = StageOwner {
                project: self.id.clone(),
                intent: intent.clone(),
                epoch,
                owner_pid,
            };
            if alive(owner_pid) {
                if ExportStage::present(&self.studio.root, &owner)? {
                    result
                        .retained
                        .push((intent, epoch, "Owner process remains alive".into()));
                }
                continue;
            }
            let document: Option<(String, String)> = db
                .query_row(
                    "SELECT hash,body FROM plans WHERE project=?1 AND intent=?2",
                    params![self.id.as_str(), intent.as_str()],
                    |row| Ok((row.get(0)?, row.get(1)?)),
                )
                .optional()?;
            let format = (|| -> Result<_> {
                let (hash, body) = document.ok_or_else(|| {
                    StudioError::new("plan_missing", "Stage has no immutable plan")
                })?;
                let plan: crate::ExportPlan = serde_json::from_str(&body)?;
                if ContentHash::document(&plan)?.as_str() != hash
                    || plan.project != self.id
                    || !matches!(plan.schema, 2..=7)
                {
                    return Err(StudioError::new(
                        "plan_tampered",
                        "Stage plan identity is invalid",
                    ));
                }
                if plan.schema == 7 {
                    crate::plan::validate_decode_evidence(&plan)?;
                } else {
                    crate::plan::validate_picture_mapping_cancellable(&plan, || Ok(()))?;
                }
                crate::native_format::NativeFormatContract::for_profile(&plan.profile)
            })();
            let format = match format {
                Ok(format) => format,
                Err(error) => {
                    if ExportStage::present(&self.studio.root, &owner)? {
                        result.retained.push((intent, epoch, error.to_string()));
                    }
                    continue;
                }
            };
            match ExportStage::reclaim(&self.studio.root, &owner, format.stage_payload_name())? {
                Reclamation::Reclaimed => result.reclaimed.push((intent, epoch)),
                Reclamation::Retained(reason) => result.retained.push((intent, epoch, reason)),
                Reclamation::Missing => {}
            }
        }
        Ok(result)
    }
    #[cfg(test)]
    fn failure_for_claim(
        &self,
        intent: &EntityId,
        epoch: u64,
        error: StudioError,
    ) -> Result<StudioError> {
        let cancelled: Option<bool> = self.studio.connection()?.query_row("SELECT cancel_requested FROM exports WHERE project=?1 AND intent=?2 AND epoch=?3 AND state!='completed'",params![self.id.as_str(),intent.as_str(),epoch],|r|r.get(0)).optional()?;
        Ok(if cancelled == Some(true) {
            StudioError::new(
                "export_cancelled",
                "Export cancellation stopped this attempt before promotion",
            )
        } else {
            error
        })
    }
    pub(crate) fn close_failed_claim(
        &self,
        claim: &ActiveClaim,
        error: &StudioError,
    ) -> Result<StudioError> {
        let mut db = self.studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let job: Option<(String, u64, u32, String, bool)> = tx.query_row(
            "SELECT request_hash,epoch,owner_pid,state,cancel_requested FROM exports WHERE project=?1 AND intent=?2",
            params![self.id.as_str(), claim.intent.as_str()],
            |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?, row.get(4)?))).optional()?;
        let mut classified = error.clone();
        if let Some((request, epoch, owner, state, cancelled)) = job {
            if request == claim.request_hash.as_str()
                && epoch == claim.epoch
                && owner == claim.owner_pid
                && state == "running"
            {
                let terminal = if cancelled { "cancelled" } else { "failed" };
                if cancelled {
                    classified = StudioError::new(
                        "export_cancelled",
                        "Cancellation confirmed while closing this exact export attempt",
                    );
                }
                let changed = tx.execute("UPDATE exports SET state=?1,error=?2,expires_at=0
                    WHERE project=?3 AND intent=?4 AND request_hash=?5 AND epoch=?6 AND owner_pid=?7 AND state='running'",
                    params![terminal, error.to_string(), self.id.as_str(), claim.intent.as_str(), claim.request_hash.as_str(), claim.epoch, claim.owner_pid])?;
                let attempts = tx.execute("UPDATE export_attempts SET state=?1,error=?2,closed_at=?3
                    WHERE project=?4 AND intent=?5 AND epoch=?6 AND owner_pid=?7 AND state='running'",
                    params![terminal, error.to_string(), unix_millis()?, self.id.as_str(), claim.intent.as_str(), claim.epoch, claim.owner_pid])?;
                if changed != 1 || attempts != 1 {
                    return Err(StudioError::new(
                        "publication_conflict",
                        "Failure closure requires one exact job and attempt",
                    ));
                }
            } else if request == claim.request_hash.as_str() && epoch > claim.epoch {
                classified = StudioError::new(
                    "worker_fenced",
                    "Newer epoch confirmed while closing this export attempt",
                );
                tx.execute("UPDATE export_attempts SET state='fenced',error=?1,closed_at=?2
                    WHERE project=?3 AND intent=?4 AND epoch=?5 AND owner_pid=?6 AND state='running'
                    AND EXISTS(SELECT 1 FROM plans p WHERE p.project=export_attempts.project AND p.intent=export_attempts.intent AND p.request_hash=?7 AND p.hash=?8)",
                    params![error.to_string(), unix_millis()?, self.id.as_str(), claim.intent.as_str(), claim.epoch, claim.owner_pid, claim.request_hash.as_str(), claim.plan_id.as_str()])?;
            }
        }
        tx.commit()?;
        Ok(classified)
    }
}
