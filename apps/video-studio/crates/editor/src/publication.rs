use std::fs::{self, File, Metadata, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::path::{Path, PathBuf};

use rusqlite::{OptionalExtension, Transaction, TransactionBehavior, params};
use sha2::{Digest, Sha256};

use crate::export_stage::ExportStage;
use crate::exports::{ExportControl, ExportLease, unix_millis};
use crate::native_format::NativeFormatContract;
use crate::{
    ArtifactReceipt, ContentHash, EntityId, NativeMeasurements, PreparedExport, Project, Result,
    StoredArtifact, StudioError,
};

const RECEIPT_LIMIT: usize = 64 * 1024;
const LEASE_MILLIS: u64 = 240_000;

#[derive(Clone)]
pub(crate) struct ActiveClaim {
    pub intent: EntityId,
    pub request_hash: ContentHash,
    pub plan_id: ContentHash,
    pub epoch: u64,
    pub owner_pid: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct FileIdentity {
    device: u64,
    inode: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Observation {
    identity: FileIdentity,
    mode: u32,
    links: u64,
    bytes: u64,
    modified: (i64, i64),
    changed: (i64, i64),
}

impl Observation {
    fn read(metadata: Metadata) -> Result<Self> {
        if !metadata.file_type().is_file() {
            return Err(conflict("Publication payload is not a regular file"));
        }
        Ok(Self {
            identity: FileIdentity {
                device: metadata.dev(),
                inode: metadata.ino(),
            },
            mode: metadata.mode(),
            links: metadata.nlink(),
            bytes: metadata.len(),
            modified: (metadata.mtime(), metadata.mtime_nsec()),
            changed: (metadata.ctime(), metadata.ctime_nsec()),
        })
    }
}

struct VerifiedFile {
    file: File,
    path: PathBuf,
    observation: Observation,
    hash: ContentHash,
}

impl VerifiedFile {
    fn open(path: &Path, control: &ExportControl, seal: bool) -> Result<Self> {
        let mut file = open_regular(path)?;
        if seal {
            let mut permissions = file.metadata()?.permissions();
            permissions.set_readonly(true);
            file.set_permissions(permissions)?;
        }
        let before = Observation::read(file.metadata()?)?;
        if before.mode & 0o222 != 0 {
            return Err(conflict("Publication payload is writable"));
        }
        let mut digest = Sha256::new();
        let mut buffer = [0; 65_536];
        let mut bytes = 0_u64;
        loop {
            control.check()?;
            let count = file.read(&mut buffer)?;
            if count == 0 {
                break;
            }
            digest.update(&buffer[..count]);
            bytes += count as u64;
        }
        let after = Observation::read(file.metadata()?)?;
        if before != after || bytes != after.bytes {
            return Err(conflict("Publication payload changed during hashing"));
        }
        file.sync_all()?;
        let value = Self {
            file,
            path: path.to_path_buf(),
            observation: after,
            hash: ContentHash::parse(format!("{:x}", digest.finalize()))?,
        };
        value.check_path()?;
        Ok(value)
    }

    fn check_path(&self) -> Result<()> {
        if Observation::read(self.file.metadata()?)? != self.observation
            || Observation::read(open_regular(&self.path)?.metadata()?)? != self.observation
        {
            return Err(conflict(
                "Verified publication pathname or descriptor changed",
            ));
        }
        Ok(())
    }
}

pub(crate) struct SealedStage {
    stage: ExportStage,
    payload: VerifiedFile,
}

impl SealedStage {
    pub(crate) fn seal(stage: ExportStage, control: &ExportControl) -> Result<Self> {
        stage.check_owner()?;
        let payload = VerifiedFile::open(&stage.path(), control, true)?;
        File::open(
            stage
                .path()
                .parent()
                .ok_or_else(|| conflict("Stage has no directory"))?,
        )?
        .sync_all()?;
        Ok(Self { stage, payload })
    }
}

pub(crate) struct VerifiedOutput {
    pub stage: SealedStage,
    pub technical: NativeMeasurements,
}

pub(crate) struct PublishedArtifact(StoredArtifact);
impl PublishedArtifact {
    pub(crate) fn into_stored(self) -> StoredArtifact {
        self.0
    }
}

pub(crate) enum PublicationFailure {
    Definitive(StudioError),
    OutcomeUnknown(StudioError),
}

impl PublicationFailure {
    pub(crate) fn into_error(self) -> StudioError {
        match self {
            Self::Definitive(error) | Self::OutcomeUnknown(error) => error,
        }
    }
}

impl From<StudioError> for PublicationFailure {
    fn from(error: StudioError) -> Self {
        Self::Definitive(error)
    }
}

struct AvailableArtifact {
    file: File,
    path: PathBuf,
    observation: Observation,
    hash: ContentHash,
}

impl AvailableArtifact {
    fn check(&self) -> Result<()> {
        if Observation::read(self.file.metadata()?)? != self.observation
            || Observation::read(open_regular(&self.path)?.metadata()?)? != self.observation
        {
            return Err(conflict("Available artifact changed during publication"));
        }
        Ok(())
    }
}

#[cfg(test)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Point {
    FinalLink,
    ArtifactSync,
    ReceiptWrite,
    ReceiptLink,
    ReceiptSync,
    JobUpdate,
    AttemptUpdate,
    Commit,
    CommitResponse,
    CommitRejected,
    ReadbackUnavailable,
    CrashAfterFinalLink,
    CrashAfterReceiptLink,
    PauseBeforeCommit,
}

#[cfg(test)]
thread_local! {
    static FAULT: std::cell::RefCell<Option<Point>> = const { std::cell::RefCell::new(None) };
}

macro_rules! boundary {
    ($point:ident) => {
        #[cfg(test)]
        if FAULT.with(|fault| *fault.borrow() == Some(Point::$point)) {
            if matches!(
                Point::$point,
                Point::CrashAfterFinalLink | Point::CrashAfterReceiptLink
            ) {
                unsafe {
                    libc::kill(std::process::id() as i32, libc::SIGKILL);
                }
                panic!("SIGKILL did not terminate native publication control");
            }
            return Err(StudioError::new(
                "injected_publication_failure",
                stringify!($point),
            ));
        }
    };
}

struct AvailableReceipt {
    file: File,
    path: PathBuf,
    observation: Observation,
    bytes: Vec<u8>,
}

impl AvailableReceipt {
    fn open(project: &Project, stored: &StoredArtifact) -> Result<Self> {
        let bytes = serde_json::to_vec(&stored.artifact)?;
        if bytes.len() > RECEIPT_LIMIT || ContentHash::bytes(&bytes) != stored.receipt_id {
            return Err(conflict("Receipt extent or content identity is invalid"));
        }
        let path = project
            .studio
            .root
            .join("receipts")
            .join(format!("{}.json", stored.receipt_id.as_str()));
        let file = open_regular(&path)?;
        let observation = Observation::read(file.metadata()?)?;
        let receipt = Self {
            file,
            path,
            observation,
            bytes,
        };
        receipt.check()?;
        Ok(receipt)
    }

    fn check(&self) -> Result<()> {
        use std::os::unix::fs::FileExt;
        let before = Observation::read(self.file.metadata()?)?;
        if before != self.observation
            || before.bytes != self.bytes.len() as u64
            || before.mode & 0o222 != 0
        {
            return Err(conflict(
                "Available receipt identity, extent or mode changed",
            ));
        }
        let mut actual = vec![0; self.bytes.len()];
        self.file.read_exact_at(&mut actual, 0)?;
        if actual != self.bytes
            || Observation::read(self.file.metadata()?)? != before
            || Observation::read(open_regular(&self.path)?.metadata()?)? != before
        {
            return Err(conflict("Available receipt bytes or pathname changed"));
        }
        Ok(())
    }
}

struct PublicationGuard<'a> {
    tx: Transaction<'a>,
    project: &'a Project,
    claim: &'a ActiveClaim,
    control: &'a ExportControl,
    deadline: u64,
}

enum Attempt {
    Retry,
    Published(StoredArtifact),
    CommitUncertain(StoredArtifact, StudioError),
}

fn conflict(detail: &str) -> StudioError {
    StudioError::new("publication_conflict", detail)
}

fn open_regular(path: &Path) -> Result<File> {
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(path)?;
    Observation::read(file.metadata()?)?;
    Ok(file)
}

pub(crate) fn verify_receipt_document(project: &Project, stored: &StoredArtifact) -> Result<()> {
    AvailableReceipt::open(project, stored)?.check()
}

pub(crate) fn validate_layout(project: &Project) -> Result<()> {
    let mut device = None;
    for name in ["staging", "artifacts", "receipts"] {
        let metadata = fs::symlink_metadata(project.studio.root.join(name))?;
        if !metadata.file_type().is_dir() || device.is_some_and(|value| value != metadata.dev()) {
            return Err(StudioError::new(
                "unsupported_publication_layout",
                "Publication roots must be real directories on the same device",
            ));
        }
        device = Some(metadata.dev());
    }
    Ok(())
}

pub(crate) fn renew(project: &Project, claim: &ActiveClaim) -> Result<u64> {
    let deadline = unix_millis()? + LEASE_MILLIS;
    let db = project.studio.connection()?;
    let changed = db.execute(
        "UPDATE exports SET expires_at=?1 WHERE project=?2 AND intent=?3 AND request_hash=?4
         AND epoch=?5 AND owner_pid=?6 AND state='running' AND cancel_requested=0
         AND EXISTS(SELECT 1 FROM export_attempts a WHERE a.project=exports.project
         AND a.intent=exports.intent AND a.epoch=exports.epoch AND a.owner_pid=exports.owner_pid AND a.state='running')
         AND EXISTS(SELECT 1 FROM plans p WHERE p.project=exports.project AND p.intent=exports.intent
         AND p.request_hash=exports.request_hash AND p.hash=?7)",
        params![deadline, project.id.as_str(), claim.intent.as_str(), claim.request_hash.as_str(),
            claim.epoch, claim.owner_pid, claim.plan_id.as_str()])?;
    if changed != 1 {
        return Err(claim_failure(project, claim)?);
    }
    Ok(deadline)
}

fn claim_failure(project: &Project, claim: &ActiveClaim) -> Result<StudioError> {
    let row: Option<(u64, bool)> = project.studio.connection()?.query_row(
        "SELECT epoch,cancel_requested FROM exports WHERE project=?1 AND intent=?2 AND request_hash=?3 AND owner_pid=?4",
        params![project.id.as_str(), claim.intent.as_str(), claim.request_hash.as_str(), claim.owner_pid],
        |row| Ok((row.get(0)?, row.get(1)?))).optional()?;
    Ok(if row == Some((claim.epoch, true)) {
        StudioError::new(
            "export_cancelled",
            "Cancellation was admitted before publication",
        )
    } else {
        StudioError::new(
            "worker_fenced",
            "Exact publication claim is no longer active",
        )
    })
}

impl<'a> PublicationGuard<'a> {
    fn check(&self) -> Result<()> {
        self.control.check()?;
        let now = unix_millis()?;
        let admitted: bool = self.tx.query_row(
            "SELECT EXISTS(SELECT 1 FROM exports e JOIN export_attempts a
             ON a.project=e.project AND a.intent=e.intent AND a.epoch=e.epoch
             JOIN plans p ON p.project=e.project AND p.intent=e.intent
             WHERE e.project=?1 AND e.intent=?2 AND e.request_hash=?3 AND e.epoch=?4 AND e.owner_pid=?5
             AND e.state='running' AND e.cancel_requested=0 AND e.expires_at=?6 AND e.expires_at>?7
             AND a.owner_pid=e.owner_pid AND a.state='running' AND p.request_hash=e.request_hash AND p.hash=?8)",
            params![self.project.id.as_str(), self.claim.intent.as_str(), self.claim.request_hash.as_str(),
                self.claim.epoch, self.claim.owner_pid, self.deadline, now, self.claim.plan_id.as_str()],
            |row| row.get(0))?;
        if !admitted {
            let cancelled: bool = self.tx.query_row(
                "SELECT EXISTS(SELECT 1 FROM exports WHERE project=?1 AND intent=?2 AND request_hash=?3
                 AND epoch=?4 AND owner_pid=?5 AND cancel_requested=1)",
                params![self.project.id.as_str(), self.claim.intent.as_str(), self.claim.request_hash.as_str(),
                    self.claim.epoch, self.claim.owner_pid], |row| row.get(0))?;
            return Err(StudioError::new(
                if cancelled {
                    "export_cancelled"
                } else {
                    "worker_fenced"
                },
                "Publication guard rejected the exact claim or renewed deadline",
            ));
        }
        Ok(())
    }

    fn make_available(
        &self,
        stage: &VerifiedFile,
        destination: &Path,
        existing: Option<&VerifiedFile>,
    ) -> Result<Option<AvailableArtifact>> {
        self.check()?;
        stage.check_path()?;
        let file = if let Some(existing) = existing {
            existing.check_path()?;
            let file = open_regular(destination)?;
            if Observation::read(file.metadata()?)? != existing.observation {
                return Err(conflict(
                    "Shared final was replaced after its verified pathname check",
                ));
            }
            file
        } else {
            boundary!(FinalLink);
            match fs::hard_link(&stage.path, destination) {
                Ok(()) => {}
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => return Ok(None),
                Err(error) => return Err(error.into()),
            }
            boundary!(CrashAfterFinalLink);
            let simultaneous = Observation::read(stage.file.metadata()?)?;
            let final_file = open_regular(destination)?;
            if Observation::read(final_file.metadata()?)? != simultaneous
                || simultaneous.identity != stage.observation.identity
                || simultaneous.bytes != stage.observation.bytes
                || simultaneous.mode != stage.observation.mode
                || simultaneous.modified != stage.observation.modified
            {
                return Err(conflict(
                    "Final link does not resolve to the sealed payload",
                ));
            }
            final_file
        };
        let observation = Observation::read(file.metadata()?)?;
        boundary!(ArtifactSync);
        File::open(self.project.studio.root.join("artifacts"))?.sync_all()?;
        Ok(Some(AvailableArtifact {
            file,
            path: destination.to_path_buf(),
            observation,
            hash: stage.hash.clone(),
        }))
    }

    fn legacy_available(&self, verified: &VerifiedFile) -> Result<AvailableArtifact> {
        self.check()?;
        verified.check_path()?;
        let file = open_regular(&verified.path)?;
        let observation = Observation::read(file.metadata()?)?;
        if observation != verified.observation {
            return Err(conflict("Legacy final changed at publication guard"));
        }
        Ok(AvailableArtifact {
            file,
            path: verified.path.clone(),
            observation,
            hash: verified.hash.clone(),
        })
    }

    fn store_artifact(
        &self,
        available: &AvailableArtifact,
        stage: &ExportStage,
        prepared: &PreparedExport,
        technical: &NativeMeasurements,
    ) -> Result<(StoredArtifact, AvailableReceipt)> {
        self.check()?;
        available.check()?;
        let format = NativeFormatContract::for_profile(&prepared.plan.profile)?;
        let artifact = ArtifactReceipt {
            schema: format.receipt_schema(),
            project: self.project.id.clone(),
            revision: prepared.plan.revision.clone(),
            plan_id: prepared.plan_id.clone(),
            renderer: prepared.plan.renderer.clone(),
            output_path: available.path.clone(),
            output_sha256: available.hash.clone(),
            output_bytes: available.observation.bytes,
            technical: technical.clone(),
        };
        format.validate_receipt(&self.project.studio.root, &artifact)?;
        let bytes = serde_json::to_vec(&artifact)?;
        if bytes.len() > RECEIPT_LIMIT {
            return Err(conflict("Artifact receipt exceeds 64 KiB"));
        }
        let receipt_id = ContentHash::bytes(&bytes);
        let destination = self
            .project
            .studio
            .root
            .join("receipts")
            .join(format!("{}.json", receipt_id.as_str()));
        stage.check_owner()?;
        let temporary = stage.receipt_temporary();
        boundary!(ReceiptWrite);
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(&temporary)?;
        file.write_all(&bytes)?;
        let mut permissions = file.metadata()?.permissions();
        permissions.set_readonly(true);
        file.set_permissions(permissions)?;
        file.sync_all()?;
        boundary!(ReceiptLink);
        match fs::hard_link(&temporary, &destination) {
            Ok(()) => {}
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                let mut stored = open_regular(&destination)?;
                let before = Observation::read(stored.metadata()?)?;
                if before.bytes != bytes.len() as u64
                    || before.bytes > RECEIPT_LIMIT as u64
                    || before.mode & 0o222 != 0
                {
                    return Err(conflict("Existing receipt has conflicting extent or mode"));
                }
                let mut actual = Vec::with_capacity(bytes.len());
                std::io::Read::by_ref(&mut stored)
                    .take(RECEIPT_LIMIT as u64 + 1)
                    .read_to_end(&mut actual)?;
                if actual != bytes
                    || Observation::read(stored.metadata()?)? != before
                    || Observation::read(open_regular(&destination)?.metadata()?)? != before
                {
                    return Err(conflict("Existing receipt bytes or identity conflict"));
                }
            }
            Err(error) => return Err(error.into()),
        }
        boundary!(CrashAfterReceiptLink);
        boundary!(ReceiptSync);
        File::open(self.project.studio.root.join("receipts"))?.sync_all()?;
        let stored = StoredArtifact {
            receipt_id,
            artifact,
        };
        let available_receipt = AvailableReceipt::open(self.project, &stored)?;
        Ok((stored, available_receipt))
    }

    fn complete(
        self,
        stored: StoredArtifact,
        available: &AvailableArtifact,
        receipt: &AvailableReceipt,
    ) -> Result<Attempt> {
        self.check()?;
        available.check()?;
        receipt.check()?;
        let now = unix_millis()?;
        let body = serde_json::to_string(&stored)?;
        boundary!(JobUpdate);
        let changed = self.tx.execute(
            "UPDATE exports SET state='completed',receipt=?1,expires_at=0 WHERE project=?2 AND intent=?3
             AND request_hash=?4 AND epoch=?5 AND owner_pid=?6 AND state='running' AND cancel_requested=0 AND expires_at=?7 AND expires_at>?8",
            params![body, self.project.id.as_str(), self.claim.intent.as_str(), self.claim.request_hash.as_str(),
                self.claim.epoch, self.claim.owner_pid, self.deadline, now])?;
        boundary!(AttemptUpdate);
        let attempts = self.tx.execute(
            "UPDATE export_attempts SET state='completed',closed_at=?1,receipt_id=?2
             WHERE project=?3 AND intent=?4 AND epoch=?5 AND owner_pid=?6 AND state='running'",
            params![
                now,
                stored.receipt_id.as_str(),
                self.project.id.as_str(),
                self.claim.intent.as_str(),
                self.claim.epoch,
                self.claim.owner_pid
            ],
        )?;
        if changed != 1 || attempts != 1 {
            return Err(conflict(
                "Completed update did not bind exactly one job and attempt",
            ));
        }
        self.control.check()?;
        #[cfg(test)]
        if FAULT.with(|fault| *fault.borrow() == Some(Point::PauseBeforeCommit)) {
            std::thread::sleep(std::time::Duration::from_millis(250));
        }
        if unix_millis()? >= self.deadline {
            return Err(StudioError::new(
                "worker_fenced",
                "Renewed publication lease expired before commit",
            ));
        }
        available.check()?;
        receipt.check()?;
        boundary!(Commit);
        #[cfg(test)]
        if FAULT.with(|fault| *fault.borrow() == Some(Point::CommitRejected)) {
            self.tx.execute(
                "INSERT INTO deferred_publication_control(parent) VALUES(123)",
                [],
            )?;
        }
        match self.tx.commit() {
            Ok(()) => {
                #[cfg(test)]
                if FAULT.with(|fault| {
                    matches!(
                        *fault.borrow(),
                        Some(Point::CommitResponse | Point::ReadbackUnavailable)
                    )
                }) {
                    return Ok(Attempt::CommitUncertain(
                        stored,
                        StudioError::new(
                            "injected_commit_response_loss",
                            "COMMIT succeeded; response was lost",
                        ),
                    ));
                }
                Ok(Attempt::Published(stored))
            }
            Err(error) => Ok(Attempt::CommitUncertain(stored, error.into())),
        }
    }
}

fn resolve_commit(
    project: &Project,
    claim: &ActiveClaim,
    stored: StoredArtifact,
    cause: StudioError,
) -> std::result::Result<PublishedArtifact, PublicationFailure> {
    let read = (|| -> Result<_> {
        #[cfg(test)]
        if FAULT.with(|fault| *fault.borrow() == Some(Point::ReadbackUnavailable)) {
            return Err(StudioError::new(
                "storage_error",
                "Injected unavailable fresh readback",
            ));
        }
        let db = project.studio.connection()?;
        db.query_row(
            "SELECT e.request_hash,e.epoch,e.owner_pid,e.state,e.cancel_requested,e.receipt,a.state,a.receipt_id
             FROM exports e LEFT JOIN export_attempts a ON a.project=e.project AND a.intent=e.intent AND a.epoch=?3 AND a.owner_pid=e.owner_pid
             WHERE e.project=?1 AND e.intent=?2",
            params![project.id.as_str(), claim.intent.as_str(), claim.epoch],
            |row| Ok((row.get::<_, String>(0)?, row.get::<_, u64>(1)?, row.get::<_, u32>(2)?,
                row.get::<_, String>(3)?, row.get::<_, bool>(4)?, row.get::<_, Option<String>>(5)?,
                row.get::<_, Option<String>>(6)?, row.get::<_, Option<String>>(7)?))).optional().map_err(Into::into)
    })();
    if let Ok(Some((request, epoch, owner, state, cancelled, receipt, attempt, receipt_id))) = read
    {
        if request == claim.request_hash.as_str()
            && epoch == claim.epoch
            && owner == claim.owner_pid
        {
            if state == "completed"
                && receipt == serde_json::to_string(&stored).ok()
                && attempt.as_deref() == Some("completed")
                && receipt_id.as_deref() == Some(stored.receipt_id.as_str())
            {
                return Ok(PublishedArtifact(stored));
            }
            if state == "running" && receipt.is_none() && attempt.as_deref() == Some("running") {
                return Err(PublicationFailure::Definitive(if cancelled {
                    StudioError::new(
                        "export_cancelled",
                        "Cancellation confirmed by fresh publication readback",
                    )
                } else {
                    cause
                }));
            }
            if state == "cancelled" || cancelled {
                return Err(PublicationFailure::Definitive(StudioError::new(
                    "export_cancelled",
                    "Cancellation confirmed by fresh publication readback",
                )));
            }
        } else if epoch > claim.epoch {
            return Err(PublicationFailure::Definitive(StudioError::new(
                "worker_fenced",
                "Newer epoch confirmed by fresh publication readback",
            )));
        }
    }
    Err(PublicationFailure::OutcomeUnknown(StudioError::new(
        "publication_outcome_unknown",
        format!("Publication commit could not be classified through fresh readback: {cause}"),
    )))
}

pub(crate) fn publish(
    project: &Project,
    claim: &ActiveClaim,
    prepared: &PreparedExport,
    mut output: VerifiedOutput,
    lease: ExportLease,
) -> std::result::Result<PublishedArtifact, PublicationFailure> {
    let mut lease = lease;
    let destination = NativeFormatContract::for_profile(&prepared.plan.profile)?
        .artifact_path(&project.studio.root, &output.stage.payload.hash);
    for _ in 0..3 {
        let control = lease.control();
        control.check()?;
        let existing = match fs::symlink_metadata(&destination) {
            Ok(_) => {
                let verified = VerifiedFile::open(&destination, &control, false)?;
                if verified.hash != output.stage.payload.hash
                    || verified.observation.bytes != output.stage.payload.observation.bytes
                {
                    return Err(conflict("Shared artifact has conflicting bytes").into());
                }
                Some(verified)
            }
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => None,
            Err(error) => return Err(StudioError::from(error).into()),
        };
        let control = lease.quiesce()?;
        let deadline = renew(project, claim)?;
        let mut db = project.studio.connection()?;
        let attempt = (|| -> Result<Attempt> {
            let guard = PublicationGuard {
                tx: db.transaction_with_behavior(TransactionBehavior::Immediate)?,
                project,
                claim,
                control: &control,
                deadline,
            };
            guard.check()?;
            output.stage.stage.check_owner()?;
            let Some(available) =
                guard.make_available(&output.stage.payload, &destination, existing.as_ref())?
            else {
                return Ok(Attempt::Retry);
            };
            let (stored, receipt) = guard.store_artifact(
                &available,
                &output.stage.stage,
                prepared,
                &output.technical,
            )?;
            available.check()?;
            guard.complete(stored, &available, &receipt)
        })()?;
        drop(db);
        match attempt {
            Attempt::Retry => {
                renew(project, claim)?;
                lease = ExportLease::start(project.clone(), claim.clone());
                continue;
            }
            Attempt::Published(stored) => return Ok(PublishedArtifact(stored)),
            Attempt::CommitUncertain(stored, cause) => {
                let result = resolve_commit(project, claim, stored, cause);
                if matches!(&result, Err(PublicationFailure::OutcomeUnknown(_))) {
                    output.stage.stage.retain();
                }
                return result;
            }
        }
    }
    Err(conflict("Shared artifact changed during three guarded publication attempts").into())
}

pub(crate) fn complete_legacy(
    project: &Project,
    claim: &ActiveClaim,
    stored: StoredArtifact,
    lease: ExportLease,
) -> std::result::Result<PublishedArtifact, PublicationFailure> {
    let control = lease.control();
    let final_file = VerifiedFile::open(&stored.artifact.output_path, &control, false)?;
    if final_file.hash != stored.artifact.output_sha256
        || final_file.observation.bytes != stored.artifact.output_bytes
    {
        return Err(conflict("Legacy final artifact differs from its receipt").into());
    }
    let receipt = AvailableReceipt::open(project, &stored)?;
    let control = lease.quiesce()?;
    let deadline = renew(project, claim)?;
    let mut db = project.studio.connection()?;
    let guard = PublicationGuard {
        tx: db
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(StudioError::from)?,
        project,
        claim,
        control: &control,
        deadline,
    };
    guard.check()?;
    final_file.check_path()?;
    let available = guard.legacy_available(&final_file)?;
    let attempt = guard.complete(stored, &available, &receipt)?;
    drop(db);
    match attempt {
        Attempt::Published(stored) => Ok(PublishedArtifact(stored)),
        Attempt::CommitUncertain(stored, cause) => resolve_commit(project, claim, stored, cause),
        Attempt::Retry => unreachable!("Legacy completion does not link files"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::export_stage::StageOwner;
    use crate::{ExportPlan, Studio};
    use std::sync::atomic::{AtomicU64, Ordering};

    static COUNTER: AtomicU64 = AtomicU64::new(0);
    const PAYLOAD: &[u8] = b"storage control payload; this is not native movie acceptance";

    struct Fixture {
        project: Project,
        prepared: PreparedExport,
        claim: ActiveClaim,
        technical: NativeMeasurements,
    }

    impl Fixture {
        fn new() -> Self {
            FAULT.with(|fault| *fault.borrow_mut() = None);
            let root = std::env::temp_dir().join(format!(
                "studio-publication-{}-{}",
                std::process::id(),
                COUNTER.fetch_add(1, Ordering::Relaxed)
            ));
            let project = Project {
                studio: Studio::open(root).unwrap(),
                id: EntityId::parse("publication-control").unwrap(),
            };
            let mut plan: ExportPlan = serde_json::from_slice(include_bytes!(
                "../tests/fixtures/legacy/plan-schema2.json"
            ))
            .unwrap();
            plan.project = project.id.clone();
            let prepared = PreparedExport {
                plan_id: ContentHash::document(&plan).unwrap(),
                plan,
                replayed: false,
            };
            let claim = ActiveClaim {
                intent: EntityId::parse("storage-control").unwrap(),
                request_hash: ContentHash::bytes(b"request"),
                plan_id: prepared.plan_id.clone(),
                epoch: 1,
                owner_pid: std::process::id(),
            };
            let receipt: ArtifactReceipt = serde_json::from_slice(include_bytes!(
                "../tests/fixtures/legacy/receipt-schema2.json"
            ))
            .unwrap();
            let db = project.studio.connection().unwrap();
            db.execute_batch("CREATE TABLE deferred_publication_parent(id INTEGER PRIMARY KEY); CREATE TABLE deferred_publication_control(parent INTEGER REFERENCES deferred_publication_parent(id) DEFERRABLE INITIALLY DEFERRED);").unwrap();
            db.execute(
                "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
                params![
                    project.id.as_str(),
                    claim.intent.as_str(),
                    claim.request_hash.as_str(),
                    claim.plan_id.as_str(),
                    serde_json::to_string(&prepared.plan).unwrap()
                ],
            )
            .unwrap();
            db.execute("INSERT INTO exports(project,intent,request_hash,epoch,state,owner_pid,expires_at) VALUES(?1,?2,?3,1,'running',?4,?5)",
                params![project.id.as_str(), claim.intent.as_str(), claim.request_hash.as_str(), claim.owner_pid, unix_millis().unwrap()+LEASE_MILLIS]).unwrap();
            db.execute("INSERT INTO export_attempts(project,intent,epoch,owner_pid,claimed_at,state) VALUES(?1,?2,1,?3,1,'running')",
                params![project.id.as_str(), claim.intent.as_str(), claim.owner_pid]).unwrap();
            Self {
                project,
                prepared,
                claim,
                technical: receipt.technical,
            }
        }

        fn select_v2(&mut self) {
            self.prepared.plan.profile = crate::MovieProfile::NativeColorMasterV2;
            self.prepared.plan_id = ContentHash::document(&self.prepared.plan).unwrap();
            self.claim.plan_id = self.prepared.plan_id.clone();
            self.technical.video_track.codec = "ap4h".into();
            self.technical.video_track.raw_sample_pts_start = crate::MediaTime {
                ticks: 0,
                timescale: 600,
            };
            self.technical.audio_track.codec = "lpcm".into();
            self.technical.audio_track.raw_sample_pts_end = crate::MediaTime {
                ticks: self.technical.audio_sample_frames as i64,
                timescale: 48000,
            };
            self.technical.audio_track.pcm_encoding = Some(crate::PcmEncodingEvidence {
                format_id: 0x6c70636d,
                format_flags: 12,
                bits_per_channel: 24,
                bytes_per_frame: 6,
                bytes_per_packet: 6,
                frames_per_packet: 1,
            });
            let frames = self.technical.audio_sample_frames;
            self.technical.streaming_audio = Some(crate::StreamingAudioEvidence {
                source: crate::PcmStreamEvidence {
                    source_start_sample: 0,
                    source_end_sample: frames,
                    sample_frames: frames,
                    decoded_prefix_sample_frames: frames,
                    chunks: 1,
                    maximum_owned_chunk_frames: 4096,
                    reader_reached_end: false,
                },
                output: crate::PcmStreamEvidence {
                    source_start_sample: 0,
                    source_end_sample: frames,
                    sample_frames: frames,
                    decoded_prefix_sample_frames: frames,
                    chunks: 1,
                    maximum_owned_chunk_frames: 4096,
                    reader_reached_end: true,
                },
            });
            self.technical.format = Some(crate::NativeFormatEvidence {
                major_brand: crate::FourCc::try_from(String::from("qt  ")).unwrap(),
                compatible_brands: vec![],
            });
            self.technical.pcm24_comparison = Some(crate::Pcm24Comparison {
                sample_frames: frames,
                maximum_code_delta: 0,
            });
            let tuple = crate::NativeColorTupleEvidence {
                color_primaries: "ITU_R_709_2".into(),
                transfer_function: "ITU_R_709_2".into(),
                y_cb_cr_matrix: "ITU_R_709_2".into(),
            };
            self.technical.video_color = Some(crate::NativeVideoColorEvidence {
                encoded_samples: tuple.clone(),
                decoded_buffers: tuple,
            });
            self.project
                .studio
                .connection()
                .unwrap()
                .execute(
                    "UPDATE plans SET hash=?1,body=?2 WHERE project=?3 AND intent=?4",
                    params![
                        self.prepared.plan_id.as_str(),
                        serde_json::to_string(&self.prepared.plan).unwrap(),
                        self.project.id.as_str(),
                        self.claim.intent.as_str()
                    ],
                )
                .unwrap();
        }

        fn output(&self) -> VerifiedOutput {
            let stage = ExportStage::create(
                &self.project.studio.root,
                StageOwner {
                    project: self.project.id.clone(),
                    intent: self.claim.intent.clone(),
                    epoch: self.claim.epoch,
                    owner_pid: self.claim.owner_pid,
                },
                NativeFormatContract::for_profile(&self.prepared.plan.profile)
                    .unwrap()
                    .stage_payload_name(),
            )
            .unwrap();
            fs::write(stage.path(), PAYLOAD).unwrap();
            VerifiedOutput {
                stage: SealedStage::seal(stage, &ExportControl::test_active()).unwrap(),
                technical: self.technical.clone(),
            }
        }

        fn publish(
            &self,
            output: VerifiedOutput,
        ) -> std::result::Result<PublishedArtifact, PublicationFailure> {
            publish(
                &self.project,
                &self.claim,
                &self.prepared,
                output,
                ExportLease::start(self.project.clone(), self.claim.clone()),
            )
        }

        fn files(&self, name: &str) -> usize {
            fs::read_dir(self.project.studio.root.join(name))
                .unwrap()
                .count()
        }
        fn state(&self) -> (String, Option<String>, String, Option<String>) {
            self.project.studio.connection().unwrap().query_row("SELECT e.state,e.receipt,a.state,a.receipt_id FROM exports e JOIN export_attempts a USING(project,intent,epoch)", [],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?))).unwrap()
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            FAULT.with(|fault| *fault.borrow_mut() = None);
            fs::remove_dir_all(&self.project.studio.root).unwrap();
        }
    }

    #[test]
    fn admitted_cancellation_and_epoch_fencing_publish_zero_files() {
        for mutation in [
            "UPDATE exports SET cancel_requested=1",
            "UPDATE exports SET epoch=2",
        ] {
            let fixture = Fixture::new();
            let output = fixture.output();
            fixture
                .project
                .studio
                .connection()
                .unwrap()
                .execute(mutation, [])
                .unwrap();
            let error = fixture.publish(output).err().unwrap().into_error();
            assert!(matches!(
                error.code.as_str(),
                "export_cancelled" | "worker_fenced"
            ));
            assert_eq!(fixture.files("artifacts"), 0);
            assert_eq!(fixture.files("receipts"), 0);
            assert_eq!(fixture.files("staging"), 0);
        }
    }

    #[test]
    fn receipt4_publication_is_derived_from_the_v2_plan_contract() {
        let mut fixture = Fixture::new();
        fixture.select_v2();
        let stored = fixture
            .publish(fixture.output())
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .into_stored();
        assert_eq!(stored.artifact.schema, 4);
        assert_eq!(stored.artifact.output_path.extension().unwrap(), "mov");
        assert_eq!(
            stored.artifact.technical.video_color,
            fixture.technical.video_color
        );
        assert_eq!(fixture.state().0, "completed");
    }

    #[test]
    fn each_filesystem_and_sql_failure_retains_only_an_unpublished_prefix() {
        for point in [
            Point::FinalLink,
            Point::ArtifactSync,
            Point::ReceiptWrite,
            Point::ReceiptLink,
            Point::ReceiptSync,
            Point::JobUpdate,
            Point::AttemptUpdate,
            Point::Commit,
        ] {
            let fixture = Fixture::new();
            let output = fixture.output();
            FAULT.with(|fault| *fault.borrow_mut() = Some(point));
            assert_eq!(
                fixture.publish(output).err().unwrap().into_error().code,
                "injected_publication_failure"
            );
            assert_eq!(
                fixture.state(),
                ("running".into(), None, "running".into(), None)
            );
            assert_eq!(
                fixture.files("artifacts"),
                usize::from(point != Point::FinalLink)
            );
            assert_eq!(
                fixture.files("receipts"),
                usize::from(matches!(
                    point,
                    Point::ReceiptSync | Point::JobUpdate | Point::AttemptUpdate | Point::Commit
                ))
            );
            assert_eq!(fixture.files("staging"), 0);
            for entry in fs::read_dir(fixture.project.studio.root.join("receipts")).unwrap() {
                let receipt: ArtifactReceipt =
                    serde_json::from_slice(&fs::read(entry.unwrap().path()).unwrap()).unwrap();
                assert!(receipt.output_path.is_file());
                assert_eq!(fs::read(receipt.output_path).unwrap(), PAYLOAD);
            }
        }
    }

    #[test]
    fn lost_commit_response_is_confirmed_without_demoting_completion() {
        let fixture = Fixture::new();
        let output = fixture.output();
        FAULT.with(|fault| *fault.borrow_mut() = Some(Point::CommitResponse));
        let stored = fixture
            .publish(output)
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .into_stored();
        let state = fixture.state();
        assert_eq!(state.0, "completed");
        assert_eq!(state.2, "completed");
        assert_eq!(state.3.as_deref(), Some(stored.receipt_id.as_str()));
        assert_eq!(
            fixture
                .project
                .cancel_export(fixture.claim.intent.clone())
                .unwrap()
                .state,
            "completed"
        );
        assert_eq!(fixture.files("artifacts"), 1);
        assert_eq!(fixture.files("receipts"), 1);
    }

    #[test]
    fn exact_shared_final_is_reused_and_conflicting_final_is_retained() {
        for exact in [true, false] {
            let fixture = Fixture::new();
            let output = fixture.output();
            let final_path = NativeFormatContract::for_profile(&fixture.prepared.plan.profile)
                .unwrap()
                .artifact_path(&fixture.project.studio.root, &output.stage.payload.hash);
            fs::write(&final_path, if exact { PAYLOAD } else { b"foreign bytes" }).unwrap();
            let mut permissions = fs::metadata(&final_path).unwrap().permissions();
            permissions.set_readonly(true);
            fs::set_permissions(&final_path, permissions).unwrap();
            let inode = fs::metadata(&final_path).unwrap().ino();
            let result = fixture.publish(output);
            if exact {
                assert!(result.is_ok());
                assert_eq!(fixture.files("receipts"), 1);
            } else {
                assert_eq!(
                    result.err().unwrap().into_error().code,
                    "publication_conflict"
                );
                assert_eq!(fixture.files("receipts"), 0);
            }
            assert_eq!(fs::metadata(&final_path).unwrap().ino(), inode);
            assert_eq!(
                fs::read(final_path).unwrap(),
                if exact { PAYLOAD } else { b"foreign bytes" }
            );
        }
    }

    #[test]
    fn replaced_stage_and_symlink_final_cannot_publish_receipts() {
        for replace_stage in [true, false] {
            let fixture = Fixture::new();
            let output = fixture.output();
            if replace_stage {
                fs::remove_file(&output.stage.payload.path).unwrap();
                fs::write(&output.stage.payload.path, PAYLOAD).unwrap();
            } else {
                let final_path = NativeFormatContract::for_profile(&fixture.prepared.plan.profile)
                    .unwrap()
                    .artifact_path(&fixture.project.studio.root, &output.stage.payload.hash);
                std::os::unix::fs::symlink(&output.stage.payload.path, final_path).unwrap();
            }
            assert!(fixture.publish(output).is_err());
            assert_eq!(fixture.files("receipts"), 0);
            assert_eq!(fixture.state().0, "running");
        }
    }

    #[test]
    fn unknown_commit_readback_does_not_modify_job_or_attempt() {
        let fixture = Fixture::new();
        let stored = fixture
            .publish(fixture.output())
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .into_stored();
        fixture
            .project
            .studio
            .connection()
            .unwrap()
            .execute("UPDATE exports SET receipt='ambiguous'", [])
            .unwrap();
        let before = fixture.state();
        assert!(matches!(
            resolve_commit(
                &fixture.project,
                &fixture.claim,
                stored,
                StudioError::new("storage_error", "uncertain commit")
            ),
            Err(PublicationFailure::OutcomeUnknown(_))
        ));
        assert_eq!(fixture.state(), before);
    }

    #[test]
    fn rejected_sqlite_commit_is_freshly_classified_as_unpublished() {
        let fixture = Fixture::new();
        let output = fixture.output();
        FAULT.with(|fault| *fault.borrow_mut() = Some(Point::CommitRejected));
        let error = fixture.publish(output).err().unwrap().into_error();
        assert_eq!(error.code, "storage_error");
        assert_eq!(
            fixture.state(),
            ("running".into(), None, "running".into(), None)
        );
        assert_eq!(fixture.files("artifacts"), 1);
        assert_eq!(fixture.files("receipts"), 1);
        fixture
            .project
            .close_failed_claim(&fixture.claim, &error)
            .unwrap();
        assert_eq!(
            fixture.state(),
            ("failed".into(), None, "failed".into(), None)
        );
    }

    #[test]
    fn unavailable_commit_readback_retains_owned_stage_and_completed_ledger() {
        let fixture = Fixture::new();
        let output = fixture.output();
        let stage_path = output.stage.payload.path.clone();
        let temporary = output.stage.stage.receipt_temporary();
        FAULT.with(|fault| *fault.borrow_mut() = Some(Point::ReadbackUnavailable));
        assert!(matches!(
            fixture.publish(output),
            Err(PublicationFailure::OutcomeUnknown(_))
        ));
        assert_eq!(fixture.state().0, "completed");
        assert_eq!(fixture.state().2, "completed");
        assert!(stage_path.is_file());
        assert!(temporary.is_file());
        assert_eq!(fixture.files("artifacts"), 1);
        assert_eq!(fixture.files("receipts"), 1);
    }

    #[test]
    fn failure_closure_classifies_cancellation_in_one_exact_transaction() {
        let fixture = Fixture::new();
        fixture
            .project
            .cancel_export(fixture.claim.intent.clone())
            .unwrap();
        let error = fixture
            .project
            .close_failed_claim(
                &fixture.claim,
                &StudioError::new("io_error", "earlier failure"),
            )
            .unwrap();
        assert_eq!(error.code, "export_cancelled");
        assert_eq!(
            fixture.state(),
            ("cancelled".into(), None, "cancelled".into(), None)
        );
    }

    #[test]
    fn absent_attempt_rolls_back_failure_closure_instead_of_closing_only_job() {
        let fixture = Fixture::new();
        fixture
            .project
            .studio
            .connection()
            .unwrap()
            .execute("DELETE FROM export_attempts", [])
            .unwrap();
        assert_eq!(
            fixture
                .project
                .close_failed_claim(&fixture.claim, &StudioError::new("io_error", "failure"))
                .unwrap_err()
                .code,
            "publication_conflict"
        );
        let state: String = fixture
            .project
            .studio
            .connection()
            .unwrap()
            .query_row("SELECT state FROM exports", [], |row| row.get(0))
            .unwrap();
        assert_eq!(state, "running");
    }

    #[test]
    fn changed_owner_and_unknown_stage_files_prevent_publication_and_remain_retained() {
        for unknown in [true, false] {
            let fixture = Fixture::new();
            let output = fixture.output();
            let path = output.stage.payload.path.clone();
            let directory = path.parent().unwrap();
            if unknown {
                fs::write(directory.join("unknown.bin"), b"retain").unwrap();
            } else {
                fs::write(directory.join("owner.json"), b"{}").unwrap();
            }
            assert!(fixture.publish(output).is_err());
            assert_eq!(fixture.files("artifacts"), 0);
            assert_eq!(fixture.files("receipts"), 0);
            assert!(path.is_file());
            assert!(directory.join("owner.json").is_file());
        }
    }

    #[test]
    fn two_publishers_share_one_immutable_final_and_keep_distinct_receipts() {
        let fixture = Fixture::new();
        let first = fixture.output();
        let mut second_claim = fixture.claim.clone();
        second_claim.intent = EntityId::parse("second-storage-control").unwrap();
        second_claim.request_hash = ContentHash::bytes(b"second-request");
        let mut second_prepared = fixture.prepared.clone();
        second_prepared.plan.revision = ContentHash::bytes(b"second-revision");
        second_prepared.plan_id = ContentHash::document(&second_prepared.plan).unwrap();
        second_claim.plan_id = second_prepared.plan_id.clone();
        let db = fixture.project.studio.connection().unwrap();
        db.execute(
            "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
            params![
                fixture.project.id.as_str(),
                second_claim.intent.as_str(),
                second_claim.request_hash.as_str(),
                second_claim.plan_id.as_str(),
                serde_json::to_string(&second_prepared.plan).unwrap()
            ],
        )
        .unwrap();
        db.execute("INSERT INTO exports(project,intent,request_hash,epoch,state,owner_pid,expires_at) VALUES(?1,?2,?3,1,'running',?4,?5)",
            params![fixture.project.id.as_str(), second_claim.intent.as_str(), second_claim.request_hash.as_str(), second_claim.owner_pid, unix_millis().unwrap()+LEASE_MILLIS]).unwrap();
        db.execute("INSERT INTO export_attempts(project,intent,epoch,owner_pid,claimed_at,state) VALUES(?1,?2,1,?3,1,'running')",
            params![fixture.project.id.as_str(), second_claim.intent.as_str(), second_claim.owner_pid]).unwrap();
        let stage = ExportStage::create(
            &fixture.project.studio.root,
            StageOwner {
                project: fixture.project.id.clone(),
                intent: second_claim.intent.clone(),
                epoch: 1,
                owner_pid: second_claim.owner_pid,
            },
            NativeFormatContract::for_profile(&second_prepared.plan.profile)
                .unwrap()
                .stage_payload_name(),
        )
        .unwrap();
        fs::write(stage.path(), PAYLOAD).unwrap();
        let second = VerifiedOutput {
            stage: SealedStage::seal(stage, &ExportControl::test_active()).unwrap(),
            technical: fixture.technical.clone(),
        };
        let project = fixture.project.clone();
        let barrier = std::sync::Arc::new(std::sync::Barrier::new(2));
        let start = barrier.clone();
        let worker = std::thread::spawn(move || {
            start.wait();
            publish(
                &project,
                &second_claim,
                &second_prepared,
                second,
                ExportLease::start(project.clone(), second_claim.clone()),
            )
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .0
        });
        barrier.wait();
        let first = fixture
            .publish(first)
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .into_stored();
        let second = worker.join().unwrap();
        assert_ne!(first.receipt_id, second.receipt_id);
        assert_eq!(first.artifact.output_sha256, second.artifact.output_sha256);
        assert_eq!(fixture.files("artifacts"), 1);
        assert_eq!(fixture.files("receipts"), 2);
        assert_eq!(fixture.files("staging"), 0);
    }

    #[test]
    fn exact_receipt_reuse_is_bounded_and_conflicting_receipts_are_retained() {
        for mutation in ["exact", "changed", "oversized", "symlink"] {
            let fixture = Fixture::new();
            let output = fixture.output();
            FAULT.with(|fault| *fault.borrow_mut() = Some(Point::JobUpdate));
            assert!(fixture.publish(output).is_err());
            FAULT.with(|fault| *fault.borrow_mut() = None);
            let path = fs::read_dir(fixture.project.studio.root.join("receipts"))
                .unwrap()
                .next()
                .unwrap()
                .unwrap()
                .path();
            let original = fs::read(&path).unwrap();
            if mutation != "exact" {
                fs::remove_file(&path).unwrap();
                match mutation {
                    "changed" => {
                        let mut bytes = original.clone();
                        bytes[0] ^= 1;
                        fs::write(&path, bytes).unwrap();
                    }
                    "oversized" => fs::write(&path, vec![0; RECEIPT_LIMIT + 1]).unwrap(),
                    "symlink" => {
                        let target = fixture.project.studio.root.join("foreign-receipt");
                        fs::write(&target, &original).unwrap();
                        std::os::unix::fs::symlink(target, &path).unwrap();
                    }
                    _ => unreachable!(),
                }
                if mutation != "symlink" {
                    let mut permissions = fs::metadata(&path).unwrap().permissions();
                    permissions.set_readonly(true);
                    fs::set_permissions(&path, permissions).unwrap();
                }
            }
            let result = fixture.publish(fixture.output());
            if mutation == "exact" {
                assert!(result.is_ok());
                assert_eq!(fixture.state().0, "completed");
            } else {
                assert!(result.is_err());
                assert_eq!(fixture.state().0, "running");
            }
            assert_eq!(fixture.files("receipts"), 1);
            assert!(fs::symlink_metadata(path).is_ok());
        }
    }

    #[test]
    fn guard_first_cancellation_observes_completed_publication() {
        let fixture = Fixture::new();
        let output = fixture.output();
        let control = ExportControl::test_active();
        let deadline = renew(&fixture.project, &fixture.claim).unwrap();
        let mut db = fixture.project.studio.connection().unwrap();
        let guard = PublicationGuard {
            tx: db
                .transaction_with_behavior(TransactionBehavior::Immediate)
                .unwrap(),
            project: &fixture.project,
            claim: &fixture.claim,
            control: &control,
            deadline,
        };
        guard.check().unwrap();
        let project = fixture.project.clone();
        let intent = fixture.claim.intent.clone();
        let (started, ready) = std::sync::mpsc::channel();
        let worker = std::thread::spawn(move || {
            started.send(()).unwrap();
            project.cancel_export(intent).unwrap()
        });
        ready
            .recv_timeout(std::time::Duration::from_secs(2))
            .unwrap();
        let destination = NativeFormatContract::for_profile(&fixture.prepared.plan.profile)
            .unwrap()
            .artifact_path(&fixture.project.studio.root, &output.stage.payload.hash);
        let available = guard
            .make_available(&output.stage.payload, &destination, None)
            .unwrap()
            .unwrap();
        let (stored, receipt) = guard
            .store_artifact(
                &available,
                &output.stage.stage,
                &fixture.prepared,
                &output.technical,
            )
            .unwrap();
        assert!(matches!(
            guard.complete(stored, &available, &receipt).unwrap(),
            Attempt::Published(_)
        ));
        assert_eq!(worker.join().unwrap().state, "completed");
        assert_eq!(fixture.state().0, "completed");
    }

    #[test]
    fn held_receipt_and_final_path_replacement_prevent_completed_commit() {
        for receipt_replacement in [true, false] {
            let fixture = Fixture::new();
            let output = fixture.output();
            let control = ExportControl::test_active();
            let deadline = renew(&fixture.project, &fixture.claim).unwrap();
            let mut db = fixture.project.studio.connection().unwrap();
            let guard = PublicationGuard {
                tx: db
                    .transaction_with_behavior(TransactionBehavior::Immediate)
                    .unwrap(),
                project: &fixture.project,
                claim: &fixture.claim,
                control: &control,
                deadline,
            };
            let destination = NativeFormatContract::for_profile(&fixture.prepared.plan.profile)
                .unwrap()
                .artifact_path(&fixture.project.studio.root, &output.stage.payload.hash);
            let available = guard
                .make_available(&output.stage.payload, &destination, None)
                .unwrap()
                .unwrap();
            let (stored, receipt) = guard
                .store_artifact(
                    &available,
                    &output.stage.stage,
                    &fixture.prepared,
                    &output.technical,
                )
                .unwrap();
            let path = if receipt_replacement {
                &receipt.path
            } else {
                &available.path
            };
            fs::remove_file(path).unwrap();
            fs::write(path, b"replaced after publication check").unwrap();
            assert!(guard.complete(stored, &available, &receipt).is_err());
            assert_eq!(
                fixture.state(),
                ("running".into(), None, "running".into(), None)
            );
        }
    }

    #[test]
    fn foreign_attempt_owner_cannot_confirm_an_uncertain_completed_commit() {
        let fixture = Fixture::new();
        let stored = fixture
            .publish(fixture.output())
            .unwrap_or_else(|error| panic!("{}", error.into_error()))
            .into_stored();
        fixture
            .project
            .studio
            .connection()
            .unwrap()
            .execute("UPDATE export_attempts SET owner_pid=0", [])
            .unwrap();
        assert!(matches!(
            resolve_commit(
                &fixture.project,
                &fixture.claim,
                stored,
                StudioError::new("storage_error", "uncertain commit")
            ),
            Err(PublicationFailure::OutcomeUnknown(_))
        ));
        assert_eq!(fixture.state().0, "completed");
    }

    #[test]
    fn publication_stall_past_a_declared_short_lease_rolls_back_both_updates() {
        let fixture = Fixture::new();
        let output = fixture.output();
        let control = ExportControl::test_active();
        let deadline = unix_millis().unwrap() + 200;
        let mut db = fixture.project.studio.connection().unwrap();
        db.execute("UPDATE exports SET expires_at=?1", [deadline])
            .unwrap();
        let guard = PublicationGuard {
            tx: db
                .transaction_with_behavior(TransactionBehavior::Immediate)
                .unwrap(),
            project: &fixture.project,
            claim: &fixture.claim,
            control: &control,
            deadline,
        };
        let destination = NativeFormatContract::for_profile(&fixture.prepared.plan.profile)
            .unwrap()
            .artifact_path(&fixture.project.studio.root, &output.stage.payload.hash);
        let available = guard
            .make_available(&output.stage.payload, &destination, None)
            .unwrap()
            .unwrap();
        let (stored, receipt) = guard
            .store_artifact(
                &available,
                &output.stage.stage,
                &fixture.prepared,
                &output.technical,
            )
            .unwrap();
        FAULT.with(|fault| *fault.borrow_mut() = Some(Point::PauseBeforeCommit));
        assert_eq!(
            guard
                .complete(stored, &available, &receipt)
                .err()
                .unwrap()
                .code,
            "worker_fenced"
        );
        assert_eq!(
            fixture.state(),
            ("running".into(), None, "running".into(), None)
        );
        assert_eq!(fixture.files("artifacts"), 1);
        assert_eq!(fixture.files("receipts"), 1);
    }

    #[test]
    fn database_busy_does_not_admit_publication_or_create_files() {
        let fixture = Fixture::new();
        let output = fixture.output();
        let mut db = fixture.project.studio.connection().unwrap();
        let lock = db
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .unwrap();
        assert_eq!(
            fixture.publish(output).err().unwrap().into_error().code,
            "storage_error"
        );
        drop(lock);
        assert_eq!(
            fixture.state(),
            ("running".into(), None, "running".into(), None)
        );
        assert_eq!(fixture.files("artifacts"), 0);
        assert_eq!(fixture.files("receipts"), 0);
    }

    #[test]
    fn native_crash_prefix_child() {
        use crate::*;
        let Some(directory) = std::env::var_os("VIDEO_STUDIO_PUBLICATION_NATIVE_CHILD") else {
            return;
        };
        let directory = PathBuf::from(directory);
        let point = match std::env::var("VIDEO_STUDIO_PUBLICATION_NATIVE_POINT")
            .unwrap()
            .as_str()
        {
            "final" => Point::CrashAfterFinalLink,
            "receipt" => Point::CrashAfterReceiptLink,
            _ => panic!("Unknown private native crash point"),
        };
        let mut picture = Vec::new();
        let mut encoder = png::Encoder::new(&mut picture, 2, 1);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&[255, 30, 0, 0, 30, 255]).unwrap();
        writer.finish().unwrap();
        let picture_path = directory.join("picture.png");
        fs::write(&picture_path, &picture).unwrap();
        let frames = 16000_u32;
        let mut audio = Vec::new();
        audio.extend_from_slice(b"RIFF");
        audio.extend_from_slice(&(36 + frames * 4).to_le_bytes());
        audio.extend_from_slice(b"WAVEfmt ");
        audio.extend_from_slice(&16_u32.to_le_bytes());
        audio.extend_from_slice(&1_u16.to_le_bytes());
        audio.extend_from_slice(&2_u16.to_le_bytes());
        audio.extend_from_slice(&48000_u32.to_le_bytes());
        audio.extend_from_slice(&192000_u32.to_le_bytes());
        audio.extend_from_slice(&4_u16.to_le_bytes());
        audio.extend_from_slice(&16_u16.to_le_bytes());
        audio.extend_from_slice(b"data");
        audio.extend_from_slice(&(frames * 4).to_le_bytes());
        for ordinal in 0..frames {
            let code = ((f64::from(ordinal) * 0.12).sin() * 1000.0) as i16;
            audio.extend_from_slice(&code.to_le_bytes());
            audio.extend_from_slice(&(-code).to_le_bytes());
        }
        let audio_path = directory.join("audio.wav");
        fs::write(&audio_path, &audio).unwrap();
        let project_id = EntityId::parse("native-prefix").unwrap();
        let studio = Studio::open(directory.join("state")).unwrap();
        let initial = studio
            .create_project(CreateProject {
                project: project_id.clone(),
                intent: EntityId::parse("create").unwrap(),
                name: "Native publication crash prefix control".into(),
                settings: Settings {
                    width: 16,
                    height: 16,
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
        let project = studio.project(project_id).unwrap();
        let picture_hash = ContentHash::bytes(&picture);
        let audio_hash = ContentHash::bytes(&audio);
        let imports = vec![
            AssetImport {
                previous_measurement: None,
                path: picture_path,
                expected_hash: picture_hash.clone(),
                expected_bytes: picture.len() as u64,
                media_kind: MediaKind::Image,
                origin: Origin::Imported {
                    external_source: "native-crash-generated-picture".into(),
                    role: "test-fixture".into(),
                },
            },
            AssetImport {
                previous_measurement: None,
                path: audio_path,
                expected_hash: audio_hash.clone(),
                expected_bytes: audio.len() as u64,
                media_kind: MediaKind::Audio,
                origin: Origin::Imported {
                    external_source: "native-crash-generated-pcm".into(),
                    role: "test-fixture".into(),
                },
            },
        ];
        let timeline: Timeline = serde_json::from_value(serde_json::json!({
            "id":"main", "frame_count":8,
            "video_tracks":[{"id":"picture", "clips":[{"id":"image", "asset":picture_hash,
                "timeline_frames":{"start":0,"length":8}, "source_samples":{"start":0,"length":1},
                "cadence":{"kind":"hold","ordinal":0}, "framing":{"fit":"stretch","crop":{"x":0.0,"y":0.0,"width":1.0,"height":1.0}}}]}],
            "audio_tracks":[{"id":"audio", "clips":[{"id":"pcm", "asset":audio_hash, "timeline_samples":{"start":0,"length":16000},
                "source_samples":{"start":0,"length":16000}, "source_rate":48000,"gain":1.0,"pan":0.0}]}]
        })).unwrap();
        let revision = project
            .commit(CommitProject {
                intent: EntityId::parse("commit").unwrap(),
                base_revision: initial.revision,
                imports,
                canonical_audio: None,
                timelines: vec![timeline],
            })
            .unwrap();
        let request = ExportRequest {
            intent: EntityId::parse("export-prefix").unwrap(),
            revision: revision.revision,
            timeline: EntityId::parse("main").unwrap(),
            profile: MovieProfile::NativeColorMasterV1,
        };
        let prepared = project.prepare_export(request.clone()).unwrap();
        fs::write(
            directory.join("request.json"),
            serde_json::to_vec(&request).unwrap(),
        )
        .unwrap();
        fs::write(
            directory.join("plan.json"),
            serde_json::to_vec(&prepared.plan).unwrap(),
        )
        .unwrap();
        fs::write(directory.join("bindings.json"), serde_json::to_vec(&serde_json::json!({ "plan_id":prepared.plan_id, "producer":prepared.plan.renderer, "source_hashes":[picture_hash,audio_hash], "point":format!("{point:?}") })).unwrap()).unwrap();
        FAULT.with(|fault| *fault.borrow_mut() = Some(point));
        project.export(request).unwrap();
        panic!("Native crash checkpoint was not reached");
    }

    #[test]
    fn native_sigkill_after_each_link_keeps_prefix_unpublished_and_recovers_new_epoch() {
        use std::os::unix::process::ExitStatusExt;
        fn inventory(path: &Path) -> serde_json::Value {
            let mut rows = fs::read_dir(path).unwrap().map(|entry| {
                let path = entry.unwrap().path(); let metadata = fs::symlink_metadata(&path).unwrap();
                serde_json::json!({"path":path,"device":metadata.dev(),"inode":metadata.ino(),"bytes":metadata.len(),
                    "regular":metadata.file_type().is_file(), "sha256":if metadata.file_type().is_file() { Some(ContentHash::bytes(&fs::read(&path).unwrap())) } else { None } })
            }).collect::<Vec<_>>();
            rows.sort_by(|left, right| left["path"].as_str().cmp(&right["path"].as_str()));
            serde_json::json!(rows)
        }
        let saved_root = std::env::var_os("VIDEO_STUDIO_PUBLICATION_PROOF_ROOT").map(PathBuf::from);
        let root = saved_root.clone().unwrap_or_else(|| {
            std::env::temp_dir().join(format!(
                "studio-native-prefix-{}-{}",
                std::process::id(),
                COUNTER.fetch_add(1, Ordering::Relaxed)
            ))
        });
        fs::create_dir(&root).unwrap();
        for point in ["final", "receipt"] {
            let directory = root.join(point);
            fs::create_dir(&directory).unwrap();
            let execution = std::process::Command::new(std::env::current_exe().unwrap())
                .args([
                    "publication::tests::native_crash_prefix_child",
                    "--exact",
                    "--nocapture",
                ])
                .env("VIDEO_STUDIO_PUBLICATION_NATIVE_CHILD", &directory)
                .env("VIDEO_STUDIO_PUBLICATION_NATIVE_POINT", point)
                .output()
                .unwrap();
            fs::write(directory.join("child-stdout.txt"), &execution.stdout).unwrap();
            fs::write(directory.join("child-stderr.txt"), &execution.stderr).unwrap();
            assert_eq!(
                execution.status.signal(),
                Some(libc::SIGKILL),
                "{}",
                String::from_utf8_lossy(&execution.stdout)
            );
            let studio = Studio::open(directory.join("state")).unwrap();
            let project = studio
                .project(EntityId::parse("native-prefix").unwrap())
                .unwrap();
            let request: crate::ExportRequest =
                serde_json::from_slice(&fs::read(directory.join("request.json")).unwrap()).unwrap();
            let plan: crate::ExportPlan =
                serde_json::from_slice(&fs::read(directory.join("plan.json")).unwrap()).unwrap();
            let db = studio.connection().unwrap();
            let before: (u64, u32, String, Option<String>) = db
                .query_row(
                    "SELECT epoch,owner_pid,state,receipt FROM exports",
                    [],
                    |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?)),
                )
                .unwrap();
            assert_eq!(before.0, 1);
            assert_eq!(before.2, "running");
            assert!(before.3.is_none());
            let attempt_before: (u64, u32, String, Option<String>, Option<u64>) = db
                .query_row(
                    "SELECT epoch,owner_pid,state,receipt_id,closed_at FROM export_attempts",
                    [],
                    |row| {
                        Ok((
                            row.get(0)?,
                            row.get(1)?,
                            row.get(2)?,
                            row.get(3)?,
                            row.get(4)?,
                        ))
                    },
                )
                .unwrap();
            assert_eq!(attempt_before, (1, before.1, "running".into(), None, None));
            let stage_key =
                ContentHash::document(&(&plan.project, &request.intent, 1_u64)).unwrap();
            let stage = studio
                .root
                .join("staging")
                .join(format!("export-{}", stage_key.as_str()));
            let owner: StageOwner =
                serde_json::from_slice(&fs::read(stage.join("owner.json")).unwrap()).unwrap();
            assert_eq!(
                owner,
                StageOwner {
                    project: plan.project.clone(),
                    intent: request.intent.clone(),
                    epoch: 1,
                    owner_pid: before.1
                }
            );
            assert!(stage.join("movie.mov").is_file());
            assert_eq!(
                stage.join("artifact-receipt.json.tmp").is_file(),
                point == "receipt"
            );
            let stage_before = inventory(&stage);
            let artifacts = fs::read_dir(studio.root.join("artifacts"))
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .collect::<Vec<_>>();
            let receipts = fs::read_dir(studio.root.join("receipts"))
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .collect::<Vec<_>>();
            assert_eq!(artifacts.len(), 1);
            assert_eq!(receipts.len(), usize::from(point == "receipt"));
            let technical =
                crate::movie::verify(&plan, &studio.root.join("blobs"), &artifacts[0]).unwrap();
            assert_eq!(technical.video_frames, 8);
            assert_eq!(technical.audio_sample_frames, 16000);
            let artifact_file =
                VerifiedFile::open(&artifacts[0], &ExportControl::test_active(), false).unwrap();
            let before_files = serde_json::json!({"artifact": {"path":artifacts[0],"sha256":artifact_file.hash,"bytes":artifact_file.observation.bytes},
                "receipts": receipts.iter().map(|path|serde_json::json!({"path":path,"sha256":ContentHash::bytes(&fs::read(path).unwrap()),"body":serde_json::from_slice::<serde_json::Value>(&fs::read(path).unwrap()).unwrap()})).collect::<Vec<_>>() });
            fs::write(directory.join("before-recovery.json"),serde_json::to_vec_pretty(&serde_json::json!({"point":point,"signal":libc::SIGKILL,"job":before,"attempt":attempt_before,"stage":{"path":stage,"owner":owner,"entries":stage_before},"files":before_files,"technical":technical,"completed":false})).unwrap()).unwrap();
            drop(artifact_file);
            drop(db);
            let result = project.export(request.clone()).unwrap();
            assert_eq!(result.receipt.artifact.schema, 3);
            assert_eq!(result.receipt.artifact.technical.video_frames, 8);
            assert_eq!(result.receipt.artifact.technical.audio_sample_frames, 16000);
            let verified = project.verify_export(request.intent.clone()).unwrap();
            let replay = project.export(request).unwrap();
            assert_eq!(verified.receipt.receipt_id, result.receipt.receipt_id);
            assert_eq!(replay.receipt.receipt_id, result.receipt.receipt_id);
            assert!(replay.replayed);
            let after: (u64, String) = studio
                .connection()
                .unwrap()
                .query_row("SELECT epoch,state FROM exports", [], |row| {
                    Ok((row.get(0)?, row.get(1)?))
                })
                .unwrap();
            assert_eq!(after, (2, "completed".into()));
            let connection = studio.connection().unwrap();
            let mut query = connection.prepare("SELECT epoch,owner_pid,state,receipt_id,closed_at FROM export_attempts ORDER BY epoch").unwrap();
            let attempts_after = query
                .query_map([], |row| {
                    Ok((
                        row.get::<_, u64>(0)?,
                        row.get::<_, u32>(1)?,
                        row.get::<_, String>(2)?,
                        row.get::<_, Option<String>>(3)?,
                        row.get::<_, Option<u64>>(4)?,
                    ))
                })
                .unwrap()
                .map(|row| row.unwrap())
                .collect::<Vec<_>>();
            assert_eq!(attempts_after.len(), 2);
            assert_eq!(attempts_after[0].0, 1);
            assert_eq!(attempts_after[0].1, before.1);
            assert_eq!(attempts_after[0].2, "abandoned");
            assert!(attempts_after[0].3.is_none());
            assert!(attempts_after[0].4.is_some());
            assert_eq!(attempts_after[1].0, 2);
            assert_eq!(attempts_after[1].1, std::process::id());
            assert_eq!(attempts_after[1].2, "completed");
            assert_eq!(
                attempts_after[1].3.as_deref(),
                Some(result.receipt.receipt_id.as_str())
            );
            assert!(attempts_after[1].4.is_some());
            assert!(!stage.exists());
            assert_eq!(
                fs::read_dir(studio.root.join("staging")).unwrap().count(),
                0
            );
            fs::write(directory.join("after-recovery.json"),serde_json::to_vec_pretty(&serde_json::json!({"job":after,"attempts":attempts_after,"retired_stage_absent":!stage.exists(),"inventories":{"artifacts":inventory(&studio.root.join("artifacts")),"receipts":inventory(&studio.root.join("receipts")),"staging":inventory(&studio.root.join("staging"))},"result":result,"reverified":verified,"replay":replay,"watched":false,"heard":false,"creativeAccepted":false})).unwrap()).unwrap();
        }
        if saved_root.is_none() {
            fs::remove_dir_all(root).unwrap();
        }
    }
}
