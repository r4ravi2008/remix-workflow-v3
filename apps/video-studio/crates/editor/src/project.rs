use std::collections::BTreeMap;
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

use rusqlite::{Connection, OptionalExtension, TransactionBehavior, params};
use sha2::{Digest, Sha256};

use crate::{
    AssetImport, CommitProject, ContentHash, CreateProject, EntityId, Inspection, Result,
    RevisionReceipt, Snapshot, StoredAsset, StudioError, media,
};

static STAGING_COUNTER: AtomicU64 = AtomicU64::new(0);

#[derive(Clone)]
pub struct Studio {
    pub(crate) root: PathBuf,
}
#[derive(Clone)]
pub struct Project {
    pub(crate) studio: Studio,
    pub(crate) id: EntityId,
}

impl Studio {
    pub fn open(root: impl AsRef<Path>) -> Result<Self> {
        crate::BuildIdentity::current()?;
        fs::create_dir_all(root.as_ref())?;
        let studio = Self {
            root: root.as_ref().canonicalize()?,
        };
        fs::create_dir_all(studio.root.join("blobs"))?;
        fs::create_dir_all(studio.root.join("staging"))?;
        fs::create_dir_all(studio.root.join("artifacts"))?;
        fs::create_dir_all(studio.root.join("receipts"))?;
        let mut db = studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let version: u32 = tx.query_row("PRAGMA user_version", [], |r| r.get(0))?;
        if version > 4 {
            return Err(StudioError::new(
                "unsupported_store_version",
                "This binary cannot open a newer store",
            ));
        }
        tx.execute_batch("
          CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, head TEXT NOT NULL, sequence INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS revisions(project TEXT NOT NULL, hash TEXT NOT NULL, body TEXT NOT NULL, sequence INTEGER NOT NULL, PRIMARY KEY(project,hash), UNIQUE(project,sequence));
          CREATE TABLE IF NOT EXISTS intents(project TEXT NOT NULL, intent TEXT NOT NULL, request_hash TEXT NOT NULL, receipt TEXT NOT NULL, PRIMARY KEY(project,intent));
          CREATE TABLE IF NOT EXISTS plans(project TEXT NOT NULL, intent TEXT NOT NULL, request_hash TEXT NOT NULL, hash TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(project,intent));
          CREATE TABLE IF NOT EXISTS exports(project TEXT NOT NULL,intent TEXT NOT NULL,request_hash TEXT NOT NULL,epoch INTEGER NOT NULL,state TEXT NOT NULL,owner_pid INTEGER NOT NULL,expires_at INTEGER NOT NULL,receipt TEXT,error TEXT,PRIMARY KEY(project,intent));
          ")?;
        if version < 4 {
            tx.execute_batch("
              ALTER TABLE exports ADD COLUMN cancel_requested INTEGER NOT NULL DEFAULT 0;
              CREATE TABLE export_attempts(project TEXT NOT NULL,intent TEXT NOT NULL,epoch INTEGER NOT NULL,owner_pid INTEGER NOT NULL,claimed_at INTEGER NOT NULL,closed_at INTEGER,state TEXT NOT NULL,receipt_id TEXT,error TEXT,PRIMARY KEY(project,intent,epoch));
              PRAGMA user_version=4;
              ")?;
        }
        tx.commit()?;
        Ok(studio)
    }
    pub(crate) fn connection(&self) -> Result<Connection> {
        let db = Connection::open(self.root.join("studio.sqlite"))?;
        db.busy_timeout(Duration::from_secs(5))?;
        let deadline = Instant::now() + Duration::from_secs(5);
        loop {
            let configure = (|| -> rusqlite::Result<()> {
                let mode: String = db.query_row("PRAGMA journal_mode", [], |r| r.get(0))?;
                if mode != "wal" {
                    let measured: String =
                        db.query_row("PRAGMA journal_mode=WAL", [], |r| r.get(0))?;
                    if measured != "wal" {
                        return Err(rusqlite::Error::InvalidQuery);
                    }
                }
                Ok(())
            })();
            match configure {
                Ok(()) => break,
                Err(rusqlite::Error::SqliteFailure(error, _))
                    if matches!(
                        error.code,
                        rusqlite::ErrorCode::DatabaseBusy | rusqlite::ErrorCode::DatabaseLocked
                    ) && Instant::now() < deadline =>
                {
                    std::thread::sleep(Duration::from_millis(10));
                }
                Err(error) => return Err(error.into()),
            }
        }
        db.execute_batch("PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON;")?;
        Ok(db)
    }
    pub fn create_project(&self, request: CreateProject) -> Result<RevisionReceipt> {
        let request_hash = ContentHash::document(&request)?;
        let mut db = self.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        if let Some(receipt) = replay(&tx, &request.project, &request.intent, &request_hash)? {
            return Ok(receipt);
        }
        let snapshot = Snapshot {
            schema: 1,
            project: request.project.clone(),
            name: request.name,
            parent: None,
            settings: request.settings,
            assets: BTreeMap::new(),
            canonical_audio: None,
            timelines: BTreeMap::new(),
        };
        snapshot.validate()?;
        let revision = ContentHash::document(&snapshot)?;
        let exists: bool = tx.query_row(
            "SELECT EXISTS(SELECT 1 FROM projects WHERE id=?1)",
            [request.project.as_str()],
            |r| r.get(0),
        )?;
        if exists {
            return Err(StudioError::new(
                "project_exists",
                "Project ID already exists with a different creation intent",
            ));
        }
        let receipt = RevisionReceipt {
            project: request.project.clone(),
            revision: revision.clone(),
            parent: None,
            sequence: 0,
            replayed: false,
        };
        tx.execute(
            "INSERT INTO projects(id,head,sequence) VALUES(?1,?2,0)",
            params![request.project.as_str(), revision.as_str()],
        )?;
        append_revision(&tx, &snapshot, &receipt, &request.intent, &request_hash)?;
        tx.commit()?;
        Ok(receipt)
    }
    pub fn project(&self, id: EntityId) -> Result<Project> {
        let exists: bool = self.connection()?.query_row(
            "SELECT EXISTS(SELECT 1 FROM projects WHERE id=?1)",
            [id.as_str()],
            |r| r.get(0),
        )?;
        if !exists {
            return Err(StudioError::new(
                "project_missing",
                "Project ID is absent from this store",
            ));
        }
        Ok(Project {
            studio: self.clone(),
            id,
        })
    }
    fn stage(&self, request: &AssetImport) -> Result<StoredAsset> {
        let staging = self.root.join("staging").join(format!(
            "import-{}-{}",
            std::process::id(),
            STAGING_COUNTER.fetch_add(1, Ordering::Relaxed)
        ));
        let result = (|| {
            let mut source = File::open(&request.path)?;
            let mut target = OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&staging)?;
            let mut digest = Sha256::new();
            let mut bytes = 0_u64;
            let mut buffer = [0; 65536];
            loop {
                let n = source.read(&mut buffer)?;
                if n == 0 {
                    break;
                }
                bytes = bytes
                    .checked_add(n as u64)
                    .ok_or_else(|| StudioError::new("asset_size", "Asset byte count overflow"))?;
                if bytes > request.expected_bytes {
                    return Err(StudioError::new(
                        "asset_size",
                        "Input is longer than expected",
                    ));
                }
                target.write_all(&buffer[..n])?;
                digest.update(&buffer[..n]);
            }
            target.sync_all()?;
            let hash = ContentHash::parse(format!("{:x}", digest.finalize()))?;
            if hash != request.expected_hash || bytes != request.expected_bytes {
                return Err(StudioError::new(
                    "asset_changed",
                    "Measured bytes differ from the import binding",
                ));
            }
            let destination = self.root.join("blobs").join(hash.as_str());
            match fs::hard_link(&staging, &destination) {
                Ok(()) => {
                    let mut permissions = fs::metadata(&destination)?.permissions();
                    permissions.set_readonly(true);
                    fs::set_permissions(&destination, permissions)?;
                    File::open(self.root.join("blobs"))?.sync_all()?;
                }
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                    verify_blob(&destination, &hash, bytes)?;
                }
                Err(error) => return Err(error.into()),
            }
            let producer = crate::BuildIdentity::current()?;
            let descriptor = media::probe(&destination, &request.media_kind)?;
            if request.media_kind == crate::MediaKind::Image {
                verify_blob(&destination, &hash, bytes)?;
            }
            let image_backend = matches!(
                &descriptor,
                crate::MediaDescriptor::Image { alpha: Some(_), .. }
            );
            Ok(StoredAsset {
                hash,
                bytes,
                origin: request.origin.clone(),
                descriptor,
                backend: if image_backend {
                    "Rust png 0.17.16 / straight RGBA8 alpha v1".into()
                } else if request.media_kind == crate::MediaKind::Image {
                    "Rust png 0.17.16 / opaque static PNG decode".into()
                } else {
                    "Rust objc2 0.3.2 / AVFoundation asynchronous track load".into()
                },
                measurement: Some(crate::NativeProbeIdentity {
                    schema: 1,
                    producer,
                }),
            })
        })();
        let cleanup = fs::remove_file(&staging);
        if result.is_ok() {
            cleanup?;
        }
        result
    }
}

impl Project {
    pub fn prepare_export(&self, request: crate::ExportRequest) -> Result<crate::PreparedExport> {
        let request_hash = ContentHash::document(&request)?;
        let db = self.studio.connection()?;
        if let Some(plan) = self.replay_plan(&db, &request.intent, &request_hash)? {
            crate::movie::validate_pixel_extents(&plan.plan)?;
            self.verify_plan_sources(&plan.plan)?;
            return Ok(plan);
        }
        let snapshot = self.verify_assets(request.revision.clone())?.snapshot;
        let mut prepared = crate::plan::compile(snapshot, &request)?;
        crate::movie::validate_pixel_extents(&prepared.plan)?;
        let evidence =
            crate::movie::verify_inputs(&prepared.plan, &self.studio.root.join("blobs"))?;
        prepared.plan.decode_evidence = evidence.movie;
        prepared.plan.image_decode_evidence = evidence.image;
        prepared.plan_id = ContentHash::document(&prepared.plan)?;
        self.verify_plan_sources(&prepared.plan)?;
        let mut db = self.studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        if let Some(plan) = self.replay_plan(&tx, &request.intent, &request_hash)? {
            crate::movie::validate_pixel_extents(&plan.plan)?;
            self.verify_plan_sources(&plan.plan)?;
            return Ok(plan);
        }
        tx.execute(
            "INSERT INTO plans(project,intent,request_hash,hash,body) VALUES(?1,?2,?3,?4,?5)",
            params![
                self.id.as_str(),
                request.intent.as_str(),
                request_hash.as_str(),
                prepared.plan_id.as_str(),
                serde_json::to_string(&prepared.plan)?
            ],
        )?;
        tx.commit()?;
        Ok(prepared)
    }
    fn replay_plan(
        &self,
        db: &Connection,
        intent: &EntityId,
        request_hash: &ContentHash,
    ) -> Result<Option<crate::PreparedExport>> {
        let row: Option<(String, String, String)> = db
            .query_row(
                "SELECT request_hash,hash,body FROM plans WHERE project=?1 AND intent=?2",
                params![self.id.as_str(), intent.as_str()],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
            )
            .optional()?;
        let Some((old_request, hash, body)) = row else {
            return Ok(None);
        };
        if old_request != request_hash.as_str() {
            return Err(StudioError::new(
                "intent_conflict",
                "Export intent already binds a different request",
            ));
        }
        let plan: crate::ExportPlan = serde_json::from_str(&body)?;
        if !matches!(plan.schema, 2..=7) {
            return Err(StudioError::new(
                "unsupported_plan_schema",
                "Historical plan remains preserved; prepare a new intent with scoped decode evidence",
            ));
        }
        let plan_id = ContentHash::parse(hash)?;
        if plan.project != self.id || ContentHash::document(&plan)? != plan_id {
            return Err(StudioError::new(
                "plan_tampered",
                "Stored export plan does not match its identity",
            ));
        }
        Ok(Some(crate::PreparedExport {
            plan_id,
            plan,
            replayed: true,
        }))
    }
    pub(crate) fn verify_plan_sources(&self, plan: &crate::ExportPlan) -> Result<()> {
        crate::plan::validate_decode_evidence(plan)?;
        for asset in plan.source_closure.values() {
            verify_blob(
                &self.studio.root.join("blobs").join(asset.hash.as_str()),
                &asset.hash,
                asset.bytes,
            )?;
        }
        Ok(())
    }
    pub fn head(&self) -> Result<Inspection> {
        let db = self.studio.connection()?;
        let (hash, sequence): (String, u64) = db.query_row(
            "SELECT head,sequence FROM projects WHERE id=?1",
            [self.id.as_str()],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )?;
        self.inspect_from(&db, ContentHash::parse(hash)?, sequence)
    }
    pub fn inspect(&self, revision: ContentHash) -> Result<Inspection> {
        let db = self.studio.connection()?;
        let sequence: Option<u64> = db
            .query_row(
                "SELECT sequence FROM revisions WHERE project=?1 AND hash=?2",
                params![self.id.as_str(), revision.as_str()],
                |r| r.get(0),
            )
            .optional()?;
        self.inspect_from(
            &db,
            revision,
            sequence.ok_or_else(|| {
                StudioError::new("revision_missing", "Revision is absent from this project")
            })?,
        )
    }
    fn inspect_from(
        &self,
        db: &Connection,
        revision: ContentHash,
        sequence: u64,
    ) -> Result<Inspection> {
        let body: String = db.query_row(
            "SELECT body FROM revisions WHERE project=?1 AND hash=?2",
            params![self.id.as_str(), revision.as_str()],
            |r| r.get(0),
        )?;
        let snapshot: Snapshot = serde_json::from_str(&body)?;
        if snapshot.project != self.id || ContentHash::document(&snapshot)? != revision {
            return Err(StudioError::new(
                "revision_tampered",
                "Stored revision no longer matches its identity",
            ));
        }
        snapshot.validate()?;
        let asset_measurements = snapshot
            .assets
            .iter()
            .map(|(id, asset)| Ok((id.clone(), ContentHash::document(asset)?)))
            .collect::<Result<BTreeMap<_, _>>>()?;
        Ok(Inspection {
            receipt: RevisionReceipt {
                project: self.id.clone(),
                revision,
                parent: snapshot.parent.clone(),
                sequence,
                replayed: false,
            },
            snapshot,
            asset_measurements,
        })
    }
    pub fn commit(&self, request: CommitProject) -> Result<RevisionReceipt> {
        let request_hash = ContentHash::document(&request)?;
        let db = self.studio.connection()?;
        if let Some(receipt) = replay(&db, &self.id, &request.intent, &request_hash)? {
            return Ok(receipt);
        }
        let mut snapshot = self.inspect(request.base_revision.clone())?.snapshot;
        let current = self.head()?.receipt;
        if current.revision != request.base_revision {
            return Err(StudioError::new(
                "revision_conflict",
                "Project head changed; inspect it before a new edit intent",
            ));
        }
        for import in &request.imports {
            if let Some(expected) = &import.previous_measurement {
                let old = snapshot.assets.get(&import.expected_hash).ok_or_else(|| {
                    StudioError::new(
                        "measurement_missing",
                        "No prior source measurement exists in this revision",
                    )
                })?;
                if old.origin != import.origin || old.bytes != import.expected_bytes {
                    return Err(StudioError::new(
                        "origin_conflict",
                        "Source measurement refresh cannot change immutable bytes or origin",
                    ));
                }
                if &ContentHash::document(old)? != expected {
                    return Err(StudioError::new(
                        "measurement_conflict",
                        "Previous source measurement differs from the requested replacement",
                    ));
                }
                old.descriptor.range_limit(&import.media_kind)?;
            }
            let asset = self.studio.stage(import)?;
            match (
                snapshot.assets.get(&asset.hash),
                &import.previous_measurement,
            ) {
                (None, Some(_)) => {
                    return Err(StudioError::new(
                        "measurement_missing",
                        "No prior source measurement exists in this revision",
                    ));
                }
                (Some(old), expected) => {
                    if old.origin != asset.origin
                        || old.hash != asset.hash
                        || old.bytes != asset.bytes
                    {
                        return Err(StudioError::new(
                            "origin_conflict",
                            "Source measurement refresh cannot change immutable bytes or origin",
                        ));
                    }
                    if let Some(expected) = expected {
                        if &ContentHash::document(old)? != expected {
                            return Err(StudioError::new(
                                "measurement_conflict",
                                "Previous source measurement differs from the requested replacement",
                            ));
                        }
                    } else if old != &asset {
                        return Err(StudioError::new(
                            "measurement_conflict",
                            "Changed native source measurements require the previous_measurement hash",
                        ));
                    }
                }
                (None, None) => {}
            }
            snapshot.assets.insert(asset.hash.clone(), asset);
        }
        if let Some(audio) = request.canonical_audio {
            snapshot.canonical_audio = Some(audio);
        }
        for timeline in request.timelines {
            snapshot.timelines.insert(timeline.id.clone(), timeline);
        }
        snapshot.parent = Some(request.base_revision.clone());
        snapshot.validate()?;
        let revision = ContentHash::document(&snapshot)?;
        let mut db = self.studio.connection()?;
        let tx = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        if let Some(receipt) = replay(&tx, &self.id, &request.intent, &request_hash)? {
            return Ok(receipt);
        }
        let (head, sequence): (String, u64) = tx.query_row(
            "SELECT head,sequence FROM projects WHERE id=?1",
            [self.id.as_str()],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )?;
        if head != request.base_revision.as_str() {
            return Err(StudioError::new(
                "revision_conflict",
                "Another edit committed while imports were being measured",
            ));
        }
        let sequence = sequence
            .checked_add(1)
            .ok_or_else(|| StudioError::new("sequence_overflow", "Revision sequence overflow"))?;
        let receipt = RevisionReceipt {
            project: self.id.clone(),
            revision: revision.clone(),
            parent: Some(request.base_revision),
            sequence,
            replayed: false,
        };
        append_revision(&tx, &snapshot, &receipt, &request.intent, &request_hash)?;
        tx.execute(
            "UPDATE projects SET head=?1,sequence=?2 WHERE id=?3",
            params![revision.as_str(), sequence, self.id.as_str()],
        )?;
        tx.commit()?;
        Ok(receipt)
    }
    pub fn verify_assets(&self, revision: ContentHash) -> Result<Inspection> {
        let inspection = self.inspect(revision)?;
        for asset in inspection.snapshot.assets.values() {
            verify_blob(
                &self.studio.root.join("blobs").join(asset.hash.as_str()),
                &asset.hash,
                asset.bytes,
            )?;
        }
        Ok(inspection)
    }
}

fn replay(
    db: &Connection,
    project: &EntityId,
    intent: &EntityId,
    hash: &ContentHash,
) -> Result<Option<RevisionReceipt>> {
    let row: Option<(String, String)> = db
        .query_row(
            "SELECT request_hash,receipt FROM intents WHERE project=?1 AND intent=?2",
            params![project.as_str(), intent.as_str()],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .optional()?;
    match row {
        None => Ok(None),
        Some((stored, body)) if stored == hash.as_str() => {
            let mut receipt: RevisionReceipt = serde_json::from_str(&body)?;
            let referenced: Option<(String, u64)> = db
                .query_row(
                    "SELECT body,sequence FROM revisions WHERE project=?1 AND hash=?2",
                    params![project.as_str(), receipt.revision.as_str()],
                    |row| Ok((row.get(0)?, row.get(1)?)),
                )
                .optional()?;
            let (body, sequence) = referenced.ok_or_else(|| {
                StudioError::new("intent_tampered", "Intent references an absent revision")
            })?;
            let snapshot: Snapshot = serde_json::from_str(&body)?;
            if receipt.project != *project
                || snapshot.project != *project
                || receipt.sequence != sequence
                || receipt.parent != snapshot.parent
                || ContentHash::document(&snapshot)? != receipt.revision
            {
                return Err(StudioError::new(
                    "intent_tampered",
                    "Intent receipt no longer matches its immutable revision",
                ));
            }
            snapshot.validate()?;
            receipt.replayed = true;
            Ok(Some(receipt))
        }
        Some(_) => Err(StudioError::new(
            "intent_conflict",
            "Intent ID already binds a different request",
        )),
    }
}

fn append_revision(
    db: &Connection,
    snapshot: &Snapshot,
    receipt: &RevisionReceipt,
    intent: &EntityId,
    request_hash: &ContentHash,
) -> Result<()> {
    db.execute(
        "INSERT INTO revisions(project,hash,body,sequence) VALUES(?1,?2,?3,?4)",
        params![
            snapshot.project.as_str(),
            receipt.revision.as_str(),
            serde_json::to_string(snapshot)?,
            receipt.sequence
        ],
    )?;
    db.execute(
        "INSERT INTO intents(project,intent,request_hash,receipt) VALUES(?1,?2,?3,?4)",
        params![
            snapshot.project.as_str(),
            intent.as_str(),
            request_hash.as_str(),
            serde_json::to_string(receipt)?
        ],
    )?;
    Ok(())
}

pub(crate) fn verify_blob(path: &Path, hash: &ContentHash, expected_bytes: u64) -> Result<()> {
    let mut file = File::open(path)?;
    let mut digest = Sha256::new();
    let mut bytes = 0_u64;
    let mut buffer = [0; 65536];
    loop {
        let n = file.read(&mut buffer)?;
        if n == 0 {
            break;
        }
        bytes += n as u64;
        digest.update(&buffer[..n]);
    }
    if bytes != expected_bytes || format!("{:x}", digest.finalize()) != hash.as_str() {
        return Err(StudioError::new(
            "asset_tampered",
            "Owned blob no longer matches its content binding",
        ));
    }
    Ok(())
}
