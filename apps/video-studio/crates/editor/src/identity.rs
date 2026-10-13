use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::os::unix::fs::MetadataExt;
use std::sync::OnceLock;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::{ContentHash, Result, StudioError};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BuildIdentity {
    pub executable_sha256: ContentHash,
    pub lock_sha256: ContentHash,
    pub native_backend: String,
    pub host_os: String,
    pub architecture: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub executable_uuid: Option<String>,
}

static CURRENT: OnceLock<Result<BuildIdentity>> = OnceLock::new();

unsafe extern "C" {
    fn _dyld_get_image_header(image_index: u32) -> *const u8;
}

#[repr(C)]
struct ProcRegionInfo {
    protections: [u32; 4],
    offset: u64,
    counters: [u32; 14],
    address: u64,
    size: u64,
}

#[repr(C)]
struct ProcRegionWithPathInfo {
    region: ProcRegionInfo,
    vnode: libc::vnode_info_path,
}

fn loaded_file_matches(metadata: &std::fs::Metadata) -> Result<()> {
    let address = unsafe { _dyld_get_image_header(0) };
    if address.is_null() {
        return Err(error("Running executable address is absent"));
    }
    let mut region = std::mem::MaybeUninit::<ProcRegionWithPathInfo>::zeroed();
    let size = std::mem::size_of::<ProcRegionWithPathInfo>();
    let measured = unsafe {
        libc::proc_pidinfo(
            std::process::id() as i32,
            8,
            address as u64,
            region.as_mut_ptr().cast(),
            size as i32,
        )
    };
    if measured != size as i32 {
        return Err(error("Kernel did not return the executable mapping vnode"));
    }
    let region = unsafe { region.assume_init() };
    if (address as u64) < region.region.address
        || (address as u64)
            >= region
                .region
                .address
                .checked_add(region.region.size)
                .ok_or_else(|| error("Executable mapping extent overflow"))?
    {
        return Err(error(
            "Kernel mapping does not contain the running executable header",
        ));
    }
    let vnode = region.vnode.vip_vi.vi_stat;
    if u64::from(vnode.vst_dev) != metadata.dev() || vnode.vst_ino != metadata.ino() {
        return Err(error(
            "Executable pathname inode differs from the running mapped image",
        ));
    }
    let mut process = std::mem::MaybeUninit::<libc::proc_bsdinfo>::zeroed();
    let size = std::mem::size_of::<libc::proc_bsdinfo>();
    let measured = unsafe {
        libc::proc_pidinfo(
            std::process::id() as i32,
            libc::PROC_PIDTBSDINFO,
            0,
            process.as_mut_ptr().cast(),
            size as i32,
        )
    };
    if measured != size as i32 {
        return Err(error("Kernel did not return the process launch time"));
    }
    let process = unsafe { process.assume_init() };
    let launched = i128::from(process.pbi_start_tvsec) * 1_000_000_000
        + i128::from(process.pbi_start_tvusec) * 1_000;
    let modified = i128::from(metadata.mtime()) * 1_000_000_000 + i128::from(metadata.mtime_nsec());
    let changed = i128::from(metadata.ctime()) * 1_000_000_000 + i128::from(metadata.ctime_nsec());
    if modified > launched || changed > launched {
        return Err(error(
            "Executable inode changed after this process launched",
        ));
    }
    Ok(())
}

fn error(detail: &str) -> StudioError {
    StudioError::new("executable_identity_changed", detail)
}

fn commands_size(header: &[u8]) -> Result<usize> {
    if header.len() < 32 || header[..4] != 0xfeedfacf_u32.to_le_bytes() {
        return Err(error(
            "Build identity requires a thin little-endian Mach-O64 executable",
        ));
    }
    let size = u32::from_le_bytes(
        header[20..24]
            .try_into()
            .map_err(|_| error("Invalid Mach-O header"))?,
    ) as usize;
    if !(8..=4 * 1024 * 1024).contains(&size) {
        return Err(error("Mach-O command extent is unsupported"));
    }
    Ok(size)
}

fn macho_uuid(bytes: &[u8]) -> Result<[u8; 16]> {
    let size = commands_size(bytes)?;
    if bytes.len() != 32 + size {
        return Err(error("Mach-O command extent is incomplete"));
    }
    let commands = u32::from_le_bytes(
        bytes[16..20]
            .try_into()
            .map_err(|_| error("Invalid command count"))?,
    );
    let mut offset = 32;
    let mut uuid = None;
    for _ in 0..commands {
        let command = bytes
            .get(offset..offset + 8)
            .ok_or_else(|| error("Mach-O command header is truncated"))?;
        let kind = u32::from_le_bytes(
            command[..4]
                .try_into()
                .map_err(|_| error("Invalid command type"))?,
        );
        let length = u32::from_le_bytes(
            command[4..]
                .try_into()
                .map_err(|_| error("Invalid command size"))?,
        ) as usize;
        if length < 8 || !length.is_multiple_of(8) {
            return Err(error("Mach-O command size is invalid"));
        }
        let end = offset
            .checked_add(length)
            .ok_or_else(|| error("Mach-O command size overflow"))?;
        let body = bytes
            .get(offset..end)
            .ok_or_else(|| error("Mach-O command is truncated"))?;
        if kind == 0x1b {
            if length != 24 || uuid.is_some() {
                return Err(error("Mach-O executable UUID is ambiguous"));
            }
            uuid = Some(
                body[8..24]
                    .try_into()
                    .map_err(|_| error("Invalid executable UUID"))?,
            );
        }
        offset = end;
    }
    if offset != bytes.len() {
        return Err(error("Mach-O command count differs from its extent"));
    }
    uuid.ok_or_else(|| error("Mach-O executable UUID is absent"))
}

fn running_uuid() -> Result<[u8; 16]> {
    let address = unsafe { _dyld_get_image_header(0) };
    if address.is_null() {
        return Err(error("dyld did not return the running executable"));
    }
    let header = unsafe { std::slice::from_raw_parts(address, 32) };
    let size = commands_size(header)?;
    // dyld owns this validated, mapped image. No file-path bytes enter this slice.
    let commands = unsafe { std::slice::from_raw_parts(address, 32 + size) };
    macho_uuid(commands)
}

fn file_uuid(file: &mut File) -> Result<[u8; 16]> {
    let mut bytes = vec![0; 32];
    file.read_exact(&mut bytes)?;
    let size = commands_size(&bytes)?;
    bytes.resize(32 + size, 0);
    file.read_exact(&mut bytes[32..])?;
    macho_uuid(&bytes)
}

fn signature(metadata: &std::fs::Metadata) -> (u64, u64, u64, i64, i64, i64, i64) {
    (
        metadata.dev(),
        metadata.ino(),
        metadata.len(),
        metadata.mtime(),
        metadata.mtime_nsec(),
        metadata.ctime(),
        metadata.ctime_nsec(),
    )
}

impl BuildIdentity {
    pub(crate) fn current() -> Result<Self> {
        CURRENT.get_or_init(Self::measure).clone()
    }

    fn measure() -> Result<Self> {
        let running = running_uuid()?;
        let mut executable = File::open(std::env::current_exe()?)?;
        let metadata = executable.metadata()?;
        loaded_file_matches(&metadata)?;
        let before = signature(&metadata);
        if file_uuid(&mut executable)? != running {
            return Err(error(
                "Executable pathname now identifies a different running-image UUID",
            ));
        }
        executable.seek(SeekFrom::Start(0))?;
        let mut digest = Sha256::new();
        let mut buffer = [0; 65536];
        loop {
            let n = executable.read(&mut buffer)?;
            if n == 0 {
                break;
            }
            digest.update(&buffer[..n]);
        }
        if signature(&executable.metadata()?) != before {
            return Err(error(
                "Executable inode changed during identity measurement",
            ));
        }
        let (host_os, native_backend) = crate::media::host_identity();
        Ok(Self {
            executable_sha256: ContentHash::parse(format!("{:x}", digest.finalize()))?,
            lock_sha256: ContentHash::bytes(include_bytes!("../../../Cargo.lock")),
            native_backend,
            host_os,
            architecture: std::env::consts::ARCH.into(),
            executable_uuid: Some(running.iter().map(|byte| format!("{byte:02x}")).collect()),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn uuid_parser_rejects_ambiguous_and_truncated_command_tables() {
        let mut bytes = vec![0; 56];
        bytes[..4].copy_from_slice(&0xfeedfacf_u32.to_le_bytes());
        bytes[16..20].copy_from_slice(&1_u32.to_le_bytes());
        bytes[20..24].copy_from_slice(&24_u32.to_le_bytes());
        bytes[32..36].copy_from_slice(&0x1b_u32.to_le_bytes());
        bytes[36..40].copy_from_slice(&24_u32.to_le_bytes());
        bytes[40..].fill(7);
        assert_eq!(macho_uuid(&bytes).unwrap(), [7; 16]);
        let second = bytes[32..56].to_vec();
        bytes.extend_from_slice(&second);
        bytes[16..20].copy_from_slice(&2_u32.to_le_bytes());
        bytes[20..24].copy_from_slice(&48_u32.to_le_bytes());
        assert!(macho_uuid(&bytes).is_err());
        bytes.pop();
        assert!(macho_uuid(&bytes).is_err());
    }

    #[test]
    fn current_identity_matches_the_running_image_and_survives_repeated_reads() {
        let current = BuildIdentity::current().unwrap();
        assert_eq!(current, BuildIdentity::current().unwrap());
        assert!(current.executable_uuid.is_some());
    }
}
