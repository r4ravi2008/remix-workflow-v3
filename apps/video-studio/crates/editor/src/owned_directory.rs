use std::ffi::CString;
use std::fs::{self, File, Metadata};
use std::io::{Read, Seek, SeekFrom, Write};
use std::os::fd::{AsRawFd, FromRawFd};
use std::os::unix::ffi::OsStrExt;
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

use crate::{ContentHash, Result, StudioError};

pub(crate) struct OwnedDirectory {
    path: PathBuf,
    parent: File,
    directory: File,
    files: Vec<OwnedFile>,
}

struct OwnedFile {
    name: CString,
    file: File,
    bytes: u64,
    hash: ContentHash,
}

fn ownership_error() -> StudioError {
    StudioError::new(
        "inspection_ownership_changed",
        "Inspection output ownership changed",
    )
}

fn name(value: &std::ffi::OsStr) -> Result<CString> {
    CString::new(value.as_bytes()).map_err(|_| ownership_error())
}

fn file_from_fd(fd: libc::c_int) -> Result<File> {
    if fd < 0 {
        return Err(std::io::Error::last_os_error().into());
    }
    Ok(unsafe { File::from_raw_fd(fd) })
}

fn same_file(left: &Metadata, right: &Metadata) -> bool {
    left.dev() == right.dev() && left.ino() == right.ino()
}

fn entry_matches(directory: &File, name: &CString, file: &File) -> Result<()> {
    let mut entry = std::mem::MaybeUninit::<libc::stat>::uninit();
    let status = unsafe {
        libc::fstatat(
            directory.as_raw_fd(),
            name.as_ptr(),
            entry.as_mut_ptr(),
            libc::AT_SYMLINK_NOFOLLOW,
        )
    };
    if status != 0 {
        return Err(ownership_error());
    }
    let entry = unsafe { entry.assume_init() };
    let current = file.metadata()?;
    if entry.st_dev as u64 != current.dev()
        || entry.st_ino != current.ino()
        || entry.st_mode & libc::S_IFMT != current.mode() as libc::mode_t & libc::S_IFMT
    {
        return Err(ownership_error());
    }
    Ok(())
}

impl OwnedDirectory {
    pub(crate) fn create(path: &Path) -> Result<Self> {
        let parent_path = path
            .parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or_else(|| Path::new("."))
            .canonicalize()?;
        let leaf = path.file_name().ok_or_else(ownership_error)?;
        let leaf_c = name(leaf)?;
        let parent_c = name(parent_path.as_os_str())?;
        let flags = libc::O_RDONLY | libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC;
        let parent = file_from_fd(unsafe { libc::open(parent_c.as_ptr(), flags) })?;
        if !same_file(&parent.metadata()?, &fs::symlink_metadata(&parent_path)?) {
            return Err(ownership_error());
        }
        if unsafe { libc::mkdirat(parent.as_raw_fd(), leaf_c.as_ptr(), 0o700) } != 0 {
            return Err(std::io::Error::last_os_error().into());
        }
        let path = parent_path.join(leaf);
        let created = fs::symlink_metadata(&path)?;
        let directory =
            file_from_fd(unsafe { libc::openat(parent.as_raw_fd(), leaf_c.as_ptr(), flags) })?;
        if !created.is_dir() || !same_file(&created, &directory.metadata()?) {
            return Err(ownership_error());
        }
        let result = Self {
            path,
            parent,
            directory,
            files: Vec::new(),
        };
        result.check_path()?;
        Ok(result)
    }

    pub(crate) fn path(&self) -> &Path {
        &self.path
    }

    fn check_path(&self) -> Result<()> {
        let parent_path = self.path.parent().ok_or_else(ownership_error)?;
        let parent = fs::symlink_metadata(parent_path).map_err(|_| ownership_error())?;
        let directory = fs::symlink_metadata(&self.path).map_err(|_| ownership_error())?;
        if !parent.is_dir()
            || !directory.is_dir()
            || !same_file(&parent, &self.parent.metadata()?)
            || !same_file(&directory, &self.directory.metadata()?)
        {
            return Err(ownership_error());
        }
        Ok(())
    }

    pub(crate) fn write(&mut self, filename: &str, bytes: &[u8]) -> Result<()> {
        self.check_path()?;
        let name = name(std::ffi::OsStr::new(filename))?;
        let flags =
            libc::O_RDWR | libc::O_CREAT | libc::O_EXCL | libc::O_NOFOLLOW | libc::O_CLOEXEC;
        let mut file = file_from_fd(unsafe {
            libc::openat(self.directory.as_raw_fd(), name.as_ptr(), flags, 0o600)
        })?;
        file.write_all(bytes)?;
        file.sync_all()?;
        self.files.push(OwnedFile {
            name,
            file,
            bytes: bytes.len() as u64,
            hash: ContentHash::bytes(bytes),
        });
        self.check_path()?;
        Ok(())
    }

    pub(crate) fn finish(mut self) -> Result<PathBuf> {
        self.check_path()?;
        for owned in &mut self.files {
            entry_matches(&self.directory, &owned.name, &owned.file)?;
            let before = owned.file.metadata()?;
            if !before.is_file() || before.len() != owned.bytes {
                return Err(ownership_error());
            }
            owned.file.seek(SeekFrom::Start(0))?;
            let mut hash = Sha256::new();
            let mut observed = 0u64;
            let mut buffer = [0; 65536];
            loop {
                let count = owned.file.read(&mut buffer)?;
                if count == 0 {
                    break;
                }
                observed += count as u64;
                if observed > owned.bytes {
                    return Err(ownership_error());
                }
                hash.update(&buffer[..count]);
            }
            let after = owned.file.metadata()?;
            if observed != owned.bytes
                || format!("{:x}", hash.finalize()) != owned.hash.as_str()
                || after.len() != owned.bytes
                || before.mtime() != after.mtime()
                || before.mtime_nsec() != after.mtime_nsec()
            {
                return Err(ownership_error());
            }
            entry_matches(&self.directory, &owned.name, &owned.file)?;
        }
        self.directory.sync_all()?;
        self.parent.sync_all()?;
        self.check_path()?;
        Ok(self.path)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::os::unix::fs::PermissionsExt;

    #[test]
    fn replacing_output_directory_preserves_both_directories() {
        let root = std::env::temp_dir().join(format!("studio-pinned-frame-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        let path = root.join("inspection");
        let preserved = root.join("preserved");
        let mut owned = OwnedDirectory::create(&path).unwrap();
        owned.write("request.json", b"owned-request").unwrap();
        fs::rename(&path, &preserved).unwrap();
        fs::create_dir(&path).unwrap();
        fs::write(path.join("foreign.txt"), b"foreign-file").unwrap();
        assert_eq!(
            owned.write("source-frame.png", b"image").unwrap_err().code,
            "inspection_ownership_changed"
        );
        assert_eq!(
            fs::read(preserved.join("request.json")).unwrap(),
            b"owned-request"
        );
        assert_eq!(fs::read(path.join("foreign.txt")).unwrap(), b"foreign-file");
        assert!(!path.join("source-frame.png").exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn metadata_only_changes_during_hashing_do_not_reject_owned_bytes() {
        let root =
            std::env::temp_dir().join(format!("studio-frame-metadata-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        let path = root.join("inspection");
        let mut owned = OwnedDirectory::create(&path).unwrap();
        owned
            .write("source-frame.png", &vec![7; 16 * 1024 * 1024])
            .unwrap();
        let file = path.join("source-frame.png");
        let active = std::sync::Arc::new(std::sync::atomic::AtomicBool::new(true));
        let updating = active.clone();
        let (ready, wait) = std::sync::mpsc::channel();
        let actor = std::thread::spawn(move || {
            fs::set_permissions(&file, fs::Permissions::from_mode(0o640)).unwrap();
            ready.send(()).unwrap();
            let mut mode = 0o600;
            while updating.load(std::sync::atomic::Ordering::Relaxed) {
                fs::set_permissions(&file, fs::Permissions::from_mode(mode)).unwrap();
                mode ^= 0o040;
                std::thread::sleep(std::time::Duration::from_micros(100));
            }
        });
        wait.recv().unwrap();
        let result = owned.finish();
        active.store(false, std::sync::atomic::Ordering::Relaxed);
        actor.join().unwrap();
        assert_eq!(result.unwrap(), path.canonicalize().unwrap());
        fs::remove_dir_all(root).unwrap();
    }
}
