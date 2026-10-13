use std::fs::{self, File, OpenOptions};
use std::io::{Read, Seek, SeekFrom};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

use crate::{ContentHash, Result, StudioError};

pub(crate) struct VerifiedSource {
    path: PathBuf,
    file: File,
    stamp: Stamp,
    hash: ContentHash,
}

#[derive(PartialEq, Eq)]
struct Stamp {
    device: u64,
    inode: u64,
    bytes: u64,
    mtime: (i64, i64),
    ctime: (i64, i64),
}

impl Stamp {
    fn read(metadata: &fs::Metadata) -> Result<Self> {
        if !metadata.is_file() {
            return Err(changed());
        }
        Ok(Self {
            device: metadata.dev(),
            inode: metadata.ino(),
            bytes: metadata.len(),
            mtime: (metadata.mtime(), metadata.mtime_nsec()),
            ctime: (metadata.ctime(), metadata.ctime_nsec()),
        })
    }
}

fn changed() -> StudioError {
    StudioError::new(
        "asset_tampered",
        "Source bytes or observed file identity changed",
    )
}

impl VerifiedSource {
    pub(crate) fn open(path: &Path, hash: &ContentHash, bytes: u64) -> Result<Self> {
        let file = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(path)?;
        let stamp = Stamp::read(&file.metadata()?)?;
        if stamp.bytes != bytes {
            return Err(changed());
        }
        let mut result = Self {
            path: path.into(),
            file,
            stamp,
            hash: hash.clone(),
        };
        result.verify()?;
        Ok(result)
    }

    pub(crate) fn verify(&mut self) -> Result<()> {
        self.check_stamp()?;
        self.file.seek(SeekFrom::Start(0))?;
        let mut hash = Sha256::new();
        let mut bytes = 0u64;
        let mut buffer = [0; 65536];
        loop {
            let count = self.file.read(&mut buffer)?;
            if count == 0 {
                break;
            }
            bytes += count as u64;
            if bytes > self.stamp.bytes {
                return Err(changed());
            }
            hash.update(&buffer[..count]);
        }
        if bytes != self.stamp.bytes || format!("{:x}", hash.finalize()) != self.hash.as_str() {
            return Err(changed());
        }
        self.check_stamp()
    }

    fn check_stamp(&self) -> Result<()> {
        let path = fs::symlink_metadata(&self.path).map_err(|_| changed())?;
        if Stamp::read(&path)? != self.stamp || Stamp::read(&self.file.metadata()?)? != self.stamp {
            return Err(changed());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_replaced_source_is_rejected_even_with_identical_bytes() {
        let root = std::env::temp_dir().join(format!("studio-frame-source-{}", std::process::id()));
        fs::create_dir(&root).unwrap();
        let path = root.join("source");
        fs::write(&path, b"source").unwrap();
        let mut source = VerifiedSource::open(&path, &ContentHash::bytes(b"source"), 6).unwrap();
        fs::write(root.join("replacement"), b"source").unwrap();
        fs::rename(root.join("replacement"), &path).unwrap();
        assert_eq!(source.verify().unwrap_err().code, "asset_tampered");
        fs::remove_dir_all(root).unwrap();
    }
}
