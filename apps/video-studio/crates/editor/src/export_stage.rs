use std::ffi::CString;
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::os::fd::{AsRawFd, FromRawFd};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use crate::native_format::StagePayloadName;
use crate::{ContentHash, EntityId, Result, StudioError};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct StageOwner {
    pub project: EntityId,
    pub intent: EntityId,
    pub epoch: u64,
    pub owner_pid: u32,
}

impl StageOwner {
    fn directory(&self, root: &Path) -> Result<PathBuf> {
        let key = ContentHash::document(&(&self.project, &self.intent, self.epoch))?;
        Ok(root
            .join("staging")
            .join(format!("export-{}", key.as_str())))
    }
}

pub(crate) struct ExportStage {
    directory: PathBuf,
    owner: StageOwner,
    payload: StagePayloadName,
    cleanup: bool,
    directory_handle: File,
}

pub(crate) const RECEIPT_TEMPORARY: &str = "artifact-receipt.json.tmp";

pub(crate) enum Reclamation {
    Missing,
    Reclaimed,
    Retained(String),
}

impl ExportStage {
    pub(crate) fn present(root: &Path, owner: &StageOwner) -> Result<bool> {
        match fs::symlink_metadata(owner.directory(root)?) {
            Ok(_) => Ok(true),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
            Err(error) => Err(error.into()),
        }
    }
    pub(crate) fn create(
        root: &Path,
        owner: StageOwner,
        payload: StagePayloadName,
    ) -> Result<Self> {
        let directory = owner.directory(root)?;
        fs::create_dir(&directory).map_err(|error| {
            if error.kind() == std::io::ErrorKind::AlreadyExists {
                StudioError::new("staging_conflict", "Export stage already has an owner")
            } else {
                error.into()
            }
        })?;
        let save = (|| -> Result<()> {
            let mut file = OpenOptions::new()
                .create_new(true)
                .write(true)
                .open(directory.join("owner.json"))?;
            file.write_all(&serde_json::to_vec(&owner)?)?;
            file.sync_all()?;
            File::open(&directory)?.sync_all()?;
            File::open(root.join("staging"))?.sync_all()?;
            Ok(())
        })();
        if let Err(error) = save {
            let _ = fs::remove_file(directory.join("owner.json"));
            let _ = fs::remove_dir(&directory);
            return Err(error);
        }
        let directory_handle = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(&directory)?;
        Ok(Self {
            directory,
            owner,
            payload,
            cleanup: true,
            directory_handle,
        })
    }

    pub(crate) fn path(&self) -> PathBuf {
        self.directory.join(self.payload.as_str())
    }

    pub(crate) fn receipt_temporary(&self) -> PathBuf {
        self.directory.join(RECEIPT_TEMPORARY)
    }

    pub(crate) fn retain(&mut self) {
        self.cleanup = false;
    }

    pub(crate) fn check_owner(&self) -> Result<()> {
        let directory = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(&self.directory)?;
        let metadata = directory.metadata()?;
        let original = self.directory_handle.metadata()?;
        if (metadata.dev(), metadata.ino()) != (original.dev(), original.ino()) {
            return Err(StudioError::new(
                "staging_conflict",
                "Owned stage directory identity changed",
            ));
        }
        let file = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(self.directory.join("owner.json"))?;
        if !file.metadata()?.file_type().is_file() || file.metadata()?.len() > 4096 {
            return Err(StudioError::new(
                "staging_conflict",
                "Stage owner document has invalid extent or type",
            ));
        }
        let mut body = Vec::new();
        file.take(4097).read_to_end(&mut body)?;
        let owner: StageOwner = serde_json::from_slice(&body)?;
        if owner != self.owner {
            return Err(StudioError::new(
                "staging_conflict",
                "Stage owner no longer matches the active attempt",
            ));
        }
        for entry in fs::read_dir(&self.directory)? {
            let entry = entry?;
            if ![
                Some("owner.json"),
                Some(self.payload.as_str()),
                Some(RECEIPT_TEMPORARY),
            ]
            .contains(&entry.file_name().to_str())
                || !entry.file_type()?.is_file()
            {
                return Err(StudioError::new(
                    "staging_conflict",
                    "Owned stage contains unknown files or links",
                ));
            }
        }
        Ok(())
    }

    pub(crate) fn reclaim(
        root: &Path,
        owner: &StageOwner,
        payload: StagePayloadName,
    ) -> Result<Reclamation> {
        let directory = owner.directory(root)?;
        match fs::symlink_metadata(&directory) {
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                return Ok(Reclamation::Missing);
            }
            Err(error) => return Ok(Reclamation::Retained(error.to_string())),
            Ok(metadata) if !metadata.file_type().is_dir() => {
                return Ok(Reclamation::Retained(
                    "Stage is not an owned directory".into(),
                ));
            }
            Ok(_) => {}
        }
        match Self::remove_owned(&directory, owner, payload, None) {
            Ok(result) => Ok(result),
            Err(error) => Ok(Reclamation::Retained(error.to_string())),
        }
    }

    fn remove_owned(
        directory: &Path,
        expected: &StageOwner,
        payload: StagePayloadName,
        original_directory: Option<&File>,
    ) -> Result<Reclamation> {
        let pinned = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(directory)?;
        let metadata = pinned.metadata()?;
        let identity = (metadata.dev(), metadata.ino());
        if let Some(original) = original_directory {
            let original = original.metadata()?;
            if (original.dev(), original.ino()) != identity {
                return Ok(Reclamation::Retained(
                    "Stage directory identity changed".into(),
                ));
            }
        }
        let owner_file = directory.join("owner.json");
        if !fs::symlink_metadata(&owner_file)?.file_type().is_file() {
            return Ok(Reclamation::Retained(
                "Owner document is not a regular file".into(),
            ));
        }
        let owner_handle = open_owned_entry(&pinned, "owner.json")?;
        if owner_handle.metadata()?.len() > 4096 {
            return Ok(Reclamation::Retained(
                "Owner document exceeds its admission limit".into(),
            ));
        }
        let mut owner_body = Vec::new();
        (&owner_handle).take(4097).read_to_end(&mut owner_body)?;
        let stored: StageOwner = match serde_json::from_slice(&owner_body) {
            Ok(stored) => stored,
            Err(_) => return Ok(Reclamation::Retained("Owner document is invalid".into())),
        };
        if &stored != expected {
            return Ok(Reclamation::Retained(
                "Owner differs from the attempt ledger".into(),
            ));
        }
        for entry in fs::read_dir(directory)? {
            let entry = entry?;
            if ![
                Some("owner.json"),
                Some(payload.as_str()),
                Some(RECEIPT_TEMPORARY),
            ]
            .contains(&entry.file_name().to_str())
                || !entry.file_type()?.is_file()
            {
                return Ok(Reclamation::Retained(
                    "Stage contains unknown files or links".into(),
                ));
            }
        }
        let mut entries = Vec::new();
        for name in [payload.as_str(), RECEIPT_TEMPORARY] {
            match open_owned_entry(&pinned, name) {
                Ok(file) => entries.push((name, file)),
                Err(error) if error.code == "stage_entry_missing" => {}
                Err(error) => return Err(error),
            }
        }
        entries.push(("owner.json", owner_handle));
        let current = fs::symlink_metadata(directory)?;
        if !current.file_type().is_dir() || (current.dev(), current.ino()) != identity {
            return Ok(Reclamation::Retained(
                "Stage directory changed before cleanup".into(),
            ));
        }
        for (name, file) in &entries {
            entry_matches(&pinned, name, file)?;
        }
        for (name, file) in entries {
            entry_matches(&pinned, name, &file)?;
            let name = CString::new(name)
                .map_err(|_| StudioError::new("staging_conflict", "Invalid stage entry"))?;
            if unsafe { libc::unlinkat(pinned.as_raw_fd(), name.as_ptr(), 0) } != 0 {
                return Err(std::io::Error::last_os_error().into());
            }
        }
        pinned.sync_all()?;
        let current = fs::symlink_metadata(directory)?;
        if !current.file_type().is_dir() || (current.dev(), current.ino()) != identity {
            return Ok(Reclamation::Retained(
                "Stage directory changed after owned entry cleanup".into(),
            ));
        }
        fs::remove_dir(directory)?;
        if let Some(parent) = directory.parent() {
            File::open(parent)?.sync_all()?;
        }
        Ok(Reclamation::Reclaimed)
    }
}

fn open_owned_entry(directory: &File, name: &str) -> Result<File> {
    let name = CString::new(name)
        .map_err(|_| StudioError::new("staging_conflict", "Invalid stage entry"))?;
    let fd = unsafe {
        libc::openat(
            directory.as_raw_fd(),
            name.as_ptr(),
            libc::O_RDONLY | libc::O_NOFOLLOW | libc::O_CLOEXEC,
        )
    };
    if fd < 0 {
        let error = std::io::Error::last_os_error();
        return Err(if error.kind() == std::io::ErrorKind::NotFound {
            StudioError::new("stage_entry_missing", "Stage entry is absent")
        } else {
            error.into()
        });
    }
    let file = unsafe { File::from_raw_fd(fd) };
    if !file.metadata()?.file_type().is_file() {
        return Err(StudioError::new(
            "staging_conflict",
            "Stage entry is not a regular file",
        ));
    }
    Ok(file)
}

fn entry_matches(directory: &File, name: &str, file: &File) -> Result<()> {
    let current = open_owned_entry(directory, name)?;
    let expected = file.metadata()?;
    let actual = current.metadata()?;
    if (expected.dev(), expected.ino()) != (actual.dev(), actual.ino()) {
        return Err(StudioError::new(
            "staging_conflict",
            "Stage entry identity changed before cleanup",
        ));
    }
    Ok(())
}

impl Drop for ExportStage {
    fn drop(&mut self) {
        if self.cleanup {
            let _ = Self::remove_owned(
                &self.directory,
                &self.owner,
                self.payload,
                Some(&self.directory_handle),
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    static COUNTER: AtomicU64 = AtomicU64::new(0);

    fn owner(project: &str, intent: &str) -> StageOwner {
        StageOwner {
            project: EntityId::parse(project).unwrap(),
            intent: EntityId::parse(intent).unwrap(),
            epoch: 1,
            owner_pid: std::process::id(),
        }
    }
    fn root() -> PathBuf {
        let root = std::env::temp_dir().join(format!(
            "studio-stage-{}-{}",
            std::process::id(),
            COUNTER.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(root.join("staging")).unwrap();
        root
    }
    #[test]
    fn mov_stage_cannot_be_reclaimed_as_mp4_or_with_an_extra_payload() {
        let root = root();
        let expected = owner("project", "master");
        let stage = ExportStage::create(&root, expected.clone(), StagePayloadName::Mov).unwrap();
        fs::write(stage.path(), b"master").unwrap();
        assert!(matches!(
            ExportStage::reclaim(&root, &expected, StagePayloadName::Mp4).unwrap(),
            Reclamation::Retained(_)
        ));
        fs::write(stage.directory.join("movie.mp4"), b"unknown").unwrap();
        let directory = stage.directory.clone();
        drop(stage);
        assert!(directory.join("movie.mov").exists());
        fs::remove_file(directory.join("movie.mp4")).unwrap();
        assert!(matches!(
            ExportStage::reclaim(&root, &expected, StagePayloadName::Mov).unwrap(),
            Reclamation::Reclaimed
        ));
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn formerly_ambiguous_project_intent_pairs_have_independent_stages() {
        let root = root();
        let first = ExportStage::create(&root, owner("a-b", "c"), StagePayloadName::Mp4).unwrap();
        let second = ExportStage::create(&root, owner("a", "b-c"), StagePayloadName::Mp4).unwrap();
        assert_ne!(first.path(), second.path());
        fs::write(first.path(), b"first").unwrap();
        fs::write(second.path(), b"second").unwrap();
        drop(first);
        assert_eq!(fs::read(second.path()).unwrap(), b"second");
        drop(second);
        assert_eq!(fs::read_dir(root.join("staging")).unwrap().count(), 0);
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn existing_stage_conflict_preserves_the_owner_and_movie() {
        let root = root();
        let stage =
            ExportStage::create(&root, owner("project", "export"), StagePayloadName::Mp4).unwrap();
        fs::write(stage.path(), b"owned").unwrap();
        assert_eq!(
            ExportStage::create(&root, stage.owner.clone(), StagePayloadName::Mp4)
                .err()
                .unwrap()
                .code,
            "staging_conflict"
        );
        assert_eq!(fs::read(stage.path()).unwrap(), b"owned");
        drop(stage);
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn changed_owner_or_unknown_files_prevent_cleanup() {
        let root = root();
        let stage =
            ExportStage::create(&root, owner("project", "export"), StagePayloadName::Mp4).unwrap();
        let directory = stage.directory.clone();
        fs::write(directory.join("unknown"), b"retain").unwrap();
        drop(stage);
        assert!(directory.join("owner.json").exists());
        fs::remove_file(directory.join("unknown")).unwrap();
        assert!(matches!(
            ExportStage::reclaim(
                &root,
                &StageOwner {
                    owner_pid: 0,
                    ..owner("project", "export")
                },
                StagePayloadName::Mp4
            )
            .unwrap(),
            Reclamation::Retained(_)
        ));
        assert!(matches!(
            ExportStage::reclaim(&root, &owner("project", "export"), StagePayloadName::Mp4)
                .unwrap(),
            Reclamation::Reclaimed
        ));
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn substituted_directory_with_matching_owner_and_allowlist_is_never_cleaned() {
        let root = root();
        let stage = ExportStage::create(
            &root,
            owner("project", "substitution"),
            StagePayloadName::Mov,
        )
        .unwrap();
        let directory = stage.directory.clone();
        fs::write(stage.path(), b"owned movie").unwrap();
        let preserved = root.join("original-stage");
        fs::rename(&directory, &preserved).unwrap();
        fs::create_dir(&directory).unwrap();
        fs::write(
            directory.join("owner.json"),
            serde_json::to_vec(&stage.owner).unwrap(),
        )
        .unwrap();
        fs::write(directory.join("movie.mov"), b"foreign movie").unwrap();
        assert_eq!(stage.check_owner().unwrap_err().code, "staging_conflict");
        drop(stage);
        assert_eq!(
            fs::read(preserved.join("movie.mov")).unwrap(),
            b"owned movie"
        );
        assert_eq!(
            fs::read(directory.join("movie.mov")).unwrap(),
            b"foreign movie"
        );
        assert!(preserved.join("owner.json").is_file());
        assert!(directory.join("owner.json").is_file());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn ownerless_crash_stage_is_retained_without_a_reconciliation_error() {
        let root = root();
        let owner = owner("project", "killed-before-owner");
        let directory = owner.directory(&root).unwrap();
        fs::create_dir(&directory).unwrap();
        assert!(matches!(
            ExportStage::reclaim(&root, &owner, StagePayloadName::Mp4).unwrap(),
            Reclamation::Retained(_)
        ));
        assert!(directory.is_dir());
        let next = ExportStage::create(
            &root,
            StageOwner { epoch: 2, ..owner },
            StagePayloadName::Mp4,
        )
        .unwrap();
        drop(next);
        fs::remove_dir_all(root).unwrap();
    }
}
