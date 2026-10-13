use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;
use video_studio::*;

struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let root = std::env::temp_dir().join(format!("studio-frame-access-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        Self(root)
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

#[test]
fn inaccessible_frame_directories_are_classified_without_changing_files_or_head() {
    let fixture = Fixture::new();
    let studio = Studio::open(fixture.0.join("state")).unwrap();
    let project = EntityId::parse("test").unwrap();
    let created = studio
        .create_project(CreateProject {
            project: project.clone(),
            intent: EntityId::parse("create").unwrap(),
            name: "Frame directory access test".into(),
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
        .unwrap();
    let directory = fixture.0.join("inspection");
    fs::create_dir(&directory).unwrap();
    fs::write(directory.join("request.json"), b"preserved-request").unwrap();
    fs::set_permissions(&directory, fs::Permissions::from_mode(0o000)).unwrap();
    let result = studio.project(project).unwrap().verify_frame_inspection(
        FrameInspectionVerificationRequest {
            directory: directory.clone(),
            receipt_id: ContentHash::parse("0".repeat(64)).unwrap(),
        },
    );
    fs::set_permissions(&directory, fs::Permissions::from_mode(0o700)).unwrap();
    let result = result.unwrap();
    assert_eq!(
        result.state,
        FrameInspectionVerificationState::UnverifiableRetained
    );
    assert!(
        result
            .reasons
            .iter()
            .any(|reason| reason.contains("Permission denied"))
    );
    assert_eq!(
        fs::read(directory.join("request.json")).unwrap(),
        b"preserved-request"
    );
    assert_eq!(
        studio
            .project(EntityId::parse("test").unwrap())
            .unwrap()
            .head()
            .unwrap()
            .receipt
            .revision,
        created.revision
    );
}
