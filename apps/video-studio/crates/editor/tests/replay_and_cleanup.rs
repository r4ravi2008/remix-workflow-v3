use std::fs;
use std::sync::atomic::{AtomicU64, Ordering};

use video_studio::*;

static NEXT: AtomicU64 = AtomicU64::new(0);
fn id(value: &str) -> EntityId {
    EntityId::parse(value).unwrap()
}
fn fixture() -> (std::path::PathBuf, Studio, CreateProject) {
    let root = std::env::temp_dir().join(format!(
        "video-studio-replay-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    fs::create_dir(&root).unwrap();
    let studio = Studio::open(&root).unwrap();
    let create = CreateProject {
        project: id("test"),
        intent: id("create"),
        name: "Replay test".into(),
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
    };
    (root, studio, create)
}

#[test]
fn intent_receipt_cannot_claim_another_project() {
    let (root, studio, create) = fixture();
    studio.create_project(create.clone()).unwrap();
    let db = rusqlite::Connection::open(root.join("studio.sqlite")).unwrap();
    let body: String = db
        .query_row("SELECT receipt FROM intents", [], |row| row.get(0))
        .unwrap();
    let mut receipt: serde_json::Value = serde_json::from_str(&body).unwrap();
    receipt["project"] = serde_json::json!("another-project");
    db.execute("UPDATE intents SET receipt=?1", [receipt.to_string()])
        .unwrap();
    assert_eq!(
        studio.create_project(create).unwrap_err().code,
        "intent_tampered"
    );
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn failed_imports_remove_the_owned_staging_file() {
    let (root, studio, create) = fixture();
    let first = studio.create_project(create).unwrap();
    let input = root.join("invalid-media.wav");
    fs::write(&input, b"invalid").unwrap();
    let request = CommitProject {
        intent: id("import"),
        base_revision: first.revision,
        imports: vec![AssetImport {
            previous_measurement: None,
            path: input,
            expected_hash: ContentHash::parse("0".repeat(64)).unwrap(),
            expected_bytes: 7,
            media_kind: MediaKind::Audio,
            origin: Origin::Imported {
                external_source: "invalid-fixture".into(),
                role: "test".into(),
            },
        }],
        canonical_audio: None,
        timelines: vec![],
    };
    assert_eq!(
        studio
            .project(id("test"))
            .unwrap()
            .commit(request)
            .unwrap_err()
            .code,
        "asset_changed"
    );
    assert_eq!(fs::read_dir(root.join("staging")).unwrap().count(), 0);
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn concurrent_first_open_applies_store_migrations_once() {
    let root = std::env::temp_dir().join(format!(
        "studio-migrate-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    fs::create_dir(&root).unwrap();
    let barrier = std::sync::Arc::new(std::sync::Barrier::new(4));
    let workers: Vec<_> = (0..4)
        .map(|_| {
            let root = root.clone();
            let barrier = barrier.clone();
            std::thread::spawn(move || {
                barrier.wait();
                Studio::open(root).unwrap();
            })
        })
        .collect();
    for worker in workers {
        worker.join().unwrap();
    }
    let db = rusqlite::Connection::open(root.join("studio.sqlite")).unwrap();
    assert_eq!(
        db.query_row("PRAGMA user_version", [], |row| row.get::<_, u32>(0))
            .unwrap(),
        4
    );
    fs::remove_dir_all(root).unwrap();
}
