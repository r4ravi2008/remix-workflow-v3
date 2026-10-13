use serde::Serialize;
use serde::de::DeserializeOwned;
use sha2::{Digest, Sha256};
use video_studio::{ArtifactReceipt, ExportPlan, Snapshot};

fn unchanged<T: DeserializeOwned + Serialize>(bytes: &[u8], expected: &str) {
    assert_eq!(format!("{:x}", Sha256::digest(bytes)), expected);
    let document: T = serde_json::from_slice(bytes).unwrap();
    let serialized = serde_json::to_vec(&document).unwrap();
    assert_eq!(serialized, bytes);
    assert_eq!(format!("{:x}", Sha256::digest(&serialized)), expected);
}

#[test]
fn actual_historical_snapshots_plans_and_receipts_keep_exact_hashes() {
    unchanged::<Snapshot>(
        include_bytes!("fixtures/legacy/snapshot-schema1.json"),
        "a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema2.json"),
        "97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema3.json"),
        "4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219",
    );
    unchanged::<Snapshot>(
        include_bytes!("fixtures/legacy/snapshot-schema1-placement.json"),
        "00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema4.json"),
        "5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687",
    );
    unchanged::<Snapshot>(
        include_bytes!("fixtures/legacy/snapshot-schema1-motion.json"),
        "1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema5.json"),
        "8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06",
    );
    unchanged::<ArtifactReceipt>(
        include_bytes!("fixtures/legacy/receipt-schema2.json"),
        "44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema6-masks-synthetic.json"),
        "5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28",
    );
    unchanged::<ExportPlan>(
        include_bytes!("fixtures/legacy/plan-schema6-masks-canonical.json"),
        "507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0",
    );
    unchanged::<Snapshot>(
        include_bytes!("fixtures/legacy/snapshot-schema1-masks.json"),
        "a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd",
    );
}
