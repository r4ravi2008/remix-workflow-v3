use std::fs;

use serde_json::{Value, json};
use video_studio::{
    CommitProject, ContentHash, CreateProject, EntityId, ExportRequest, FrameInspectionRequest,
    FrameInspectionVerificationRequest, Studio, StudioError,
};

fn execute(args: &[String]) -> Result<Value, Box<dyn std::error::Error>> {
    if args[1..]
        .first()
        .is_some_and(|operation| operation == "discover")
        && (args.len() == 2 || args.len() == 5)
    {
        let mut inventory = json!({"schema":1,"library":"video-studio","operations":["project.create","project.inspect","project.commit","asset.verify","asset.inspect-frame","asset.verify-frame-inspection","project.prepare-export","project.export","project.cancel-export","project.verify-export","project.reconcile-export-staging"],"capabilities":[{"name":"project_revisions_and_imports","state":"Implemented","scope":"Immutable revisions, stable intents, measured CAS bytes, stored origin and exact probe build/host/framework identity for new or guarded-refreshed measurements; legacy measurements remain unbound until refresh, source-measurement refresh guarded by the prior metadata hash and fixed media kind; one measured stream per file"},{"name":"native_sample_index","state":"Implemented","scope":"Complete compressed movie sample index using Core Media output PTS/DTS/duration; differing raw encoded times remain stored; this is separate from decoded coverage"},{"name":"source_frame_inspection","state":"Implemented","scope":"Read-only revision and measurement-bound presentation ordinal; checked native prefix PTS, coded RGBA/PNG hashes and decoder identity; source FD hash and pathname identity checked before and after decode, without excluding changes between observations; descriptor-relative exclusive writes and final file identity/hash checks; all partial files remain preserved on failure. No motion or creative acceptance."},{"name":"saved_frame_integrity","state":"Implemented","scope":"Read-only classification of complete, partial, foreign, corrupt and unverifiable frame directories; expected semantic receipt ID, request equality, exact PNG and decoded RGBA hashes, revision/source relationship and current source bytes; no movie re-decode or producer attestation; all files retained"},{"name":"native_decode_probe","state":"Implemented","scope":"Movie first sample at import and selected ranges at plan preparation; static PNG import fully decodes straight source sample values and measured alpha facts"},{"name":"static_png_picture","state":"Implemented","scope":"Eight-bit or expanded lower-depth PNG source samples, complete stream validation, dimensions, straight RGBA hash and non-opaque alpha facts; opaque inputs retain legacy bytes, transparent inputs use copied premultiplied UNORM16 execution; one source sample with explicit hold ordinal zero; animation and sixteen-bit samples rejected; no ICC/gamma/color conversion"},{"name":"immutable_export_plan","state":"Implemented","scope":"Schema2 movie evidence; schema3 opaque static images; schema4 ordered picture layers; schema5 typed motion; schema6 analytic axis reveals; schema7 directly used transparent PNGs with one closed alpha policy and unique per-image alpha identity; exact canonical audio mapping"},{"name":"native_movie_export","state":"Implemented","scope":"H.264/AAC MP4, compatibility NativeColorMasterV1 ProRes4444/PCM24LE QuickTime without a color claim, or closed NativeColorMasterV2 with the complete Rec.709 writer tuple, ShouldPropagate input attachments and every encoded/decoded native tuple observed as ITU_R_709_2; legacy adjacent clips, schema4/5/6 ordered opaque movie/PNG layers and schema7 straight-alpha PNG composition into an opaque canvas, one measured48kHz stereo PCM clip, up to 100000 frames within an explicit 1800-second native operation deadline; bounded 4096-frame stereo PCM chunks, capacity-two channels and incremental zero-offset audio verification, exact PCM24 codes, Receipt3 V1 observations and Receipt4 V2 tuple observations; A16 accepted the bounded mask/mastering ROI and exact-PCM policy, while alpha-specific independent native output proof remains pending; coded BGRA source geometry and decoded output alpha=255 scans; orientation, aperture, SAR and source color metadata remain unverified; V2 defines output numeric mapping without ICC, gamma or source-gamut conversion; explicit contain/cover/stretch and normalized crop retaining at least one source pixel per dimension, each owned source/canvas BGRA frame up to 128 MiB, complete coverage, unity gain and zero pan"},{"name":"export_ownership","state":"Implemented","scope":"Fenced epochs, renewable leases, cancellation checks, attempt history, exclusive stage ownership, cleanup of owner-recorded hashed stages from retired dead owners and promoted-file recovery"},{"name":"vp9_native_decode","state":"Unsupported","scope":"Observed AVFoundation -11833 for the bound AVf7upKp7TM VP9 source on macOS26.0.1; another representation requires an explicit source map"},{"name":"native_layered_picture_composition","state":"Implemented","scope":"Up to four nonempty picture track workers and one compositor; capacity-one picture channels; exact source ordinals and PTS, bottom-to-top order, signed destination rectangles, fixed-point opacity, transparent contain bars and complete visible temporal union;512MiB logical payload admission and reservations, serialized PNG decoding, without total process/native-memory or maximum-throughput proof; A13 accepted the bounded independent picture proof; full-film and creative acceptance remain separate"},{"name":"native_picture_motion","state":"Implemented","scope":"Optional independent x/y/width/height/opacity curves; integer local-frame keys, step or signed rational linear interpolation, final holds and constant programs; schema5 normalized immutable execution with bounded per-frame coverage/admission and rechecked pose/source observations; A14 accepted the bounded native motion proof; full-film and creative acceptance remain separate"},{"name":"native_picture_masks","state":"Implemented","scope":"One clip-owned horizontal or vertical axis-reveal mask; sparse constant/step/linear progress curves, Q16 box coverage and inversion in the unclipped destination picture window; effective-weight visibility and bounded raster admission; opaque inputs remain unchanged; A16 accepted bounded NativeColorMasterV1 mask output under the unchanged ROI and exact-PCM policy; creative acceptance is separate"},{"name":"native_picture_alpha","state":"Implemented","scope":"Plan7 transparent eight-bit PNG inputs; straight RGBA source authority, copied premultiplied BGRA UNORM16 rasters, Q16/Q32 sampling, intrinsic-alpha/opacity/mask composition, positive runtime coverage, bounded logical permits and opaque output-alpha scans; legacy opaque bytes and arithmetic remain preserved; independent ordinary-CLI native output proof is pending and creative acceptance is separate"},{"name":"native_color_text","state":"Planned"},{"name":"exact_file_creative_review","state":"Planned"},{"name":"tenant_effect_gpu_orchestration","state":"Planned"}],"rendererSubprocess":false,"verifiedCapabilityReceipts":[],"evidenceUsage":"discover STATE PROJECT EXPORT_INTENT reopens an exact completed output and attaches source, build, host and coverage evidence"});
        if args.len() == 5 {
            let result = Studio::open(&args[2])?
                .project(EntityId::parse(&args[3])?)?
                .verify_export(EntityId::parse(&args[4])?)?;
            inventory["verifiedCapabilityReceipts"] = json!([{ "state":"Verified", "scope":"Exact completed export only; excludes playback and creative acceptance", "evidence":result }]);
        }
        return Ok(inventory);
    }
    if args.len() < 4 {
        return Err(
            "usage: video-studio discover | OPERATION STATE [PROJECT] [REQUEST_OR_REVISION]".into(),
        );
    }
    let studio = Studio::open(&args[2])?;
    let result = match (args[1].as_str(), args.len()) {
        ("asset.verify-frame-inspection", 5) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .verify_frame_inspection(serde_json::from_slice::<
                    FrameInspectionVerificationRequest,
                >(&fs::read(&args[4])?)?)?,
        )?,
        ("asset.inspect-frame", 6) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .inspect_frame(serde_json::from_slice::<FrameInspectionRequest>(
                    &fs::read(&args[4])?,
                )?)?
                .save_new(&args[5])?,
        )?,
        ("project.reconcile-export-staging", 4) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .reconcile_export_staging()?,
        )?,
        ("project.verify-export", 5) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .verify_export(EntityId::parse(&args[4])?)?,
        )?,
        ("project.cancel-export", 5) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .cancel_export(EntityId::parse(&args[4])?)?,
        )?,
        ("project.create", 4) => serde_json::to_value(studio.create_project(
            serde_json::from_slice::<CreateProject>(&fs::read(&args[3])?)?,
        )?)?,
        ("project.inspect", 4) => {
            serde_json::to_value(studio.project(EntityId::parse(&args[3])?)?.head()?)?
        }
        ("project.inspect", 5) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .inspect(ContentHash::parse(&args[4])?)?,
        )?,
        ("project.export", 5) => {
            serde_json::to_value(studio.project(EntityId::parse(&args[3])?)?.export(
                serde_json::from_slice::<ExportRequest>(&fs::read(&args[4])?)?,
            )?)?
        }
        ("project.prepare-export", 5) => {
            serde_json::to_value(studio.project(EntityId::parse(&args[3])?)?.prepare_export(
                serde_json::from_slice::<ExportRequest>(&fs::read(&args[4])?)?,
            )?)?
        }
        ("project.commit", 5) => {
            serde_json::to_value(studio.project(EntityId::parse(&args[3])?)?.commit(
                serde_json::from_slice::<CommitProject>(&fs::read(&args[4])?)?,
            )?)?
        }
        ("asset.verify", 5) => serde_json::to_value(
            studio
                .project(EntityId::parse(&args[3])?)?
                .verify_assets(ContentHash::parse(&args[4])?)?,
        )?,
        _ => return Err("Unknown operation or incorrect argument count".into()),
    };
    Ok(json!({"schema":1,"result":result}))
}

fn main() {
    match execute(&std::env::args().collect::<Vec<_>>()) {
        Ok(value) => println!("{value}"),
        Err(error) => {
            let detail = if let Some(error) = error.downcast_ref::<StudioError>() {
                json!(error)
            } else {
                json!({"code":"cli_error","detail":error.to_string()})
            };
            println!("{}", json!({"schema":1,"error":detail}));
            std::process::exit(1);
        }
    }
}
