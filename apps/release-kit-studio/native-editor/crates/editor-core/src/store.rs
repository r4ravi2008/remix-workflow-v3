use crate::frame::{self, Pending};
use crate::*;
use rusqlite::{params, Connection, OptionalExtension, Transaction, TransactionBehavior};
use std::fs;
use std::path::{Component, Path, PathBuf};
use std::time::Duration;

pub(crate) fn check_path(path: &Path) -> Result<(), EditorError> {
    let mut ancestor = PathBuf::new();
    for part in path.components() {
        if matches!(part, Component::ParentDir) {
            return Err(EditorError::invalid(
                "State paths cannot contain parent traversal.",
            ));
        }
        ancestor.push(part.as_os_str());
        match fs::symlink_metadata(&ancestor) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                return Err(EditorError::invalid(
                    "State and artifact paths cannot contain symlinks.",
                ))
            }
            Ok(_) => {}
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
            Err(e) => return Err(e.into()),
        }
    }
    Ok(())
}
pub(crate) fn safe_root(path: &Path) -> Result<PathBuf, EditorError> {
    let root = if path.is_absolute() {
        path.to_path_buf()
    } else {
        std::env::current_dir()?.join(path)
    };
    check_path(&root)?;
    Ok(root)
}
fn connection(directory: &Path, create: bool) -> Result<Connection, EditorError> {
    check_path(directory)?;
    let database = directory.join("project.sqlite3");
    check_path(&database)?;
    check_path(&directory.join("project.sqlite3-journal"))?;
    if !create && !database.is_file() {
        return Err(EditorError::new(
            ErrorCode::ProjectNotFound,
            "Project does not exist in the selected state directory.",
        ));
    }
    if create {
        fs::create_dir_all(directory)?;
    }
    let flags = if create {
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE | rusqlite::OpenFlags::SQLITE_OPEN_CREATE
    } else {
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE
    };
    let connection = Connection::open_with_flags(database, flags)?;
    connection.busy_timeout(Duration::ZERO)?;
    connection.pragma_update(None, "synchronous", "FULL")?;
    if create {
        connection.execute_batch("CREATE TABLE IF NOT EXISTS revisions(revision INTEGER PRIMARY KEY, snapshot TEXT NOT NULL, hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, result TEXT, pending TEXT);
            CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, receipt TEXT NOT NULL);")?;
    }
    Ok(connection)
}
fn snapshot(
    connection: &Connection,
    project_id: &ProjectId,
    revision: Option<Revision>,
) -> Result<Snapshot, EditorError> {
    let row: Option<(u64, String, String)> = if let Some(revision) = revision {
        connection
            .query_row(
                "SELECT revision,snapshot,hash FROM revisions WHERE revision=?",
                [revision.get()],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
            )
            .optional()?
    } else {
        connection
            .query_row(
                "SELECT revision,snapshot,hash FROM revisions ORDER BY revision DESC LIMIT 1",
                [],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
            )
            .optional()?
    };
    let (stored_revision, json, hash) = row.ok_or_else(|| {
        EditorError::new(
            if revision.is_some() {
                ErrorCode::RevisionNotFound
            } else {
                ErrorCode::ProjectNotFound
            },
            "Requested project revision does not exist.",
        )
    })?;
    let snapshot: Snapshot = serde_json::from_str(&json)?;
    if snapshot.snapshot_version != 1
        || snapshot.project_id != *project_id
        || snapshot.revision.get() != stored_revision
    {
        return Err(frame::integrity(
            "Stored snapshot belongs to another project or unsupported snapshot version.",
        ));
    }
    if structured_hash(&snapshot)? != hash {
        return Err(frame::integrity(
            "Stored immutable snapshot differs from its hash.",
        ));
    }
    Ok(snapshot)
}
fn write_snapshot(
    transaction: &Transaction<'_>,
    snapshot: &Snapshot,
) -> Result<ProjectResult, EditorError> {
    let hash = structured_hash(snapshot)?;
    transaction.execute(
        "INSERT INTO revisions(revision,snapshot,hash) VALUES (?,?,?)",
        params![
            snapshot.revision.get(),
            serde_json::to_string(snapshot)?,
            hash
        ],
    )?;
    Ok(ProjectResult {
        project_id: snapshot.project_id.clone(),
        revision: snapshot.revision,
        project_sha256: hash,
    })
}
#[derive(Debug)]
enum Intent {
    Absent,
    Pending(Pending),
    Completed(CommandResult),
}
fn intent(connection: &Connection, id: &IntentId, hash: &str) -> Result<Intent, EditorError> {
    let row: Option<(String, Option<String>, Option<String>)> = connection
        .query_row(
            "SELECT request_hash,result,pending FROM intents WHERE id=?",
            [id.as_str()],
            |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
        )
        .optional()?;
    match row {
        None => Ok(Intent::Absent),
        Some((stored_hash, result, pending)) => {
            if stored_hash != hash {
                return Err(EditorError::new(
                    ErrorCode::IntentConflict,
                    "The intent already identifies a different command.",
                ));
            }
            if let Some(result) = result {
                Ok(Intent::Completed(serde_json::from_str(&result)?))
            } else if let Some(pending) = pending {
                Ok(Intent::Pending(serde_json::from_str(&pending)?))
            } else {
                Err(EditorError::new(
                    ErrorCode::StorageFailure,
                    "Intent has no pending or completed state.",
                ))
            }
        }
    }
}
fn save_result(
    transaction: &Transaction<'_>,
    id: &IntentId,
    hash: &str,
    result: &CommandResult,
) -> Result<(), EditorError> {
    transaction.execute("INSERT INTO intents(id,request_hash,result,pending) VALUES (?,?,?,NULL) ON CONFLICT(id) DO UPDATE SET result=excluded.result,pending=NULL", params![id.as_str(), hash, serde_json::to_string(result)?])?;
    Ok(())
}
fn replay(
    directory: &Path,
    project_id: &ProjectId,
    connection: &Connection,
    result: CommandResult,
) -> Result<Execution, EditorError> {
    match &result {
        CommandResult::Project(result) if result.project_id != *project_id => {
            return Err(frame::integrity(
                "Replayed result belongs to another project.",
            ))
        }
        CommandResult::Artifact(receipt) if receipt.project_id != *project_id => {
            return Err(frame::integrity(
                "Replayed artifact belongs to another project.",
            ))
        }
        _ => {}
    }
    if let CommandResult::Project(result) = &result {
        let stored = snapshot(connection, project_id, Some(result.revision)).map_err(|error| {
            if error.code() == ErrorCode::RevisionNotFound {
                frame::integrity("Completed intent references a missing immutable revision.")
            } else {
                error
            }
        })?;
        if structured_hash(&stored)? != result.project_sha256 {
            return Err(frame::integrity(
                "Replayed result differs from its immutable snapshot.",
            ));
        }
    }
    if let CommandResult::Artifact(receipt) = &result {
        let snapshot = snapshot(connection, project_id, Some(receipt.revision))?;
        frame::verify(directory, &snapshot, receipt)?;
    }
    Ok(Execution {
        result,
        replayed: true,
    })
}

pub(crate) fn execute(editor: &Editor, command: Command) -> Result<Execution, EditorError> {
    let hash = command.identity()?;
    let project_id = match &command {
        Command::CreateProject(v) => &v.project_id,
        Command::InspectProject(v) => &v.project_id,
        Command::CommitProject(v) => &v.project_id,
        Command::RenderFrame(v) => &v.project_id,
        Command::VerifyArtifact(v) => &v.project_id,
    };
    let project_id = project_id.clone();
    let directory = editor.root.join(project_id.as_str());
    crate::checkpoint("before-transaction");
    let mut connection = connection(&directory, matches!(command, Command::CreateProject(_)))?;
    match command {
        Command::CreateProject(input) => {
            let transaction =
                connection.transaction_with_behavior(TransactionBehavior::Immediate)?;
            if let Intent::Completed(result) = intent(&transaction, &input.intent_id, &hash)? {
                return replay(&directory, &project_id, &transaction, result);
            }
            let exists: bool =
                transaction.query_row("SELECT EXISTS(SELECT 1 FROM revisions)", [], |row| {
                    row.get(0)
                })?;
            if exists {
                snapshot(&transaction, &project_id, None)?;
                return Err(EditorError::new(
                    ErrorCode::ProjectExists,
                    "A different creation intent already created this project.",
                ));
            }
            let snapshot = Snapshot {
                snapshot_version: 1,
                project_id: input.project_id,
                revision: Revision::new(0)?,
                name: input.name,
                timeline: input.timeline,
                clips: Vec::new(),
            };
            let result = CommandResult::Project(write_snapshot(&transaction, &snapshot)?);
            save_result(&transaction, &input.intent_id, &hash, &result)?;
            crate::checkpoint("during-revision-commit");
            transaction.commit()?;
            fs::File::open(&directory)?.sync_all()?;
            if let Some(parent) = directory.parent() {
                fs::File::open(parent)?.sync_all()?;
            }
            crate::checkpoint("after-commit");
            Ok(Execution {
                result,
                replayed: false,
            })
        }
        Command::InspectProject(input) => {
            let snapshot = snapshot(&connection, &project_id, input.revision)?;
            let project_sha256 = structured_hash(&snapshot)?;
            Ok(Execution {
                result: CommandResult::Inspection(Inspection {
                    snapshot,
                    project_sha256,
                }),
                replayed: false,
            })
        }
        Command::CommitProject(input) => {
            let transaction =
                connection.transaction_with_behavior(TransactionBehavior::Immediate)?;
            if let Intent::Completed(result) = intent(&transaction, &input.intent_id, &hash)? {
                return replay(&directory, &project_id, &transaction, result);
            }
            let mut snapshot = snapshot(&transaction, &project_id, None)?;
            if snapshot.revision != input.expected_revision {
                return Err(EditorError::revision_conflict(snapshot.revision));
            }
            snapshot.apply(&input.edits, &editor.limits)?;
            let result = CommandResult::Project(write_snapshot(&transaction, &snapshot)?);
            save_result(&transaction, &input.intent_id, &hash, &result)?;
            crate::checkpoint("during-revision-commit");
            transaction.commit()?;
            crate::checkpoint("after-commit");
            Ok(Execution {
                result,
                replayed: false,
            })
        }
        Command::RenderFrame(input) => {
            let transaction =
                connection.transaction_with_behavior(TransactionBehavior::Immediate)?;
            let pending = match intent(&transaction, &input.intent_id, &hash)? {
                Intent::Completed(result) => {
                    return replay(&directory, &project_id, &transaction, result)
                }
                Intent::Pending(pending) => pending,
                Intent::Absent => {
                    let snapshot = snapshot(&transaction, &project_id, Some(input.revision))?;
                    if input.frame.get() >= snapshot.timeline.duration_frames.get() {
                        return Err(EditorError::invalid("Frame is outside the timeline."));
                    }
                    let pending = Pending {
                        project_sha256: structured_hash(&snapshot)?,
                        binary_sha256: editor.binary_sha256.clone(),
                        renderer_version: format!("native-rgba-png/{}", VERSION),
                        artifact_id: ArtifactId::new(format!("frame-{}", &hash[..48]))?,
                        input: input.clone(),
                    };
                    transaction.execute(
                        "INSERT INTO intents(id,request_hash,result,pending) VALUES (?,?,NULL,?)",
                        params![
                            input.intent_id.as_str(),
                            hash,
                            serde_json::to_string(&pending)?
                        ],
                    )?;
                    pending
                }
            };
            transaction.commit()?;
            crate::checkpoint("after-pending");
            let transaction =
                connection.transaction_with_behavior(TransactionBehavior::Immediate)?;
            if let Intent::Completed(result) = intent(&transaction, &input.intent_id, &hash)? {
                return replay(&directory, &project_id, &transaction, result);
            }
            let snapshot = snapshot(&transaction, &project_id, Some(input.revision))?;
            if pending.project_sha256 != structured_hash(&snapshot)?
                || pending.binary_sha256 != editor.binary_sha256
                || pending.renderer_version != format!("native-rgba-png/{}", VERSION)
                || Command::RenderFrame(pending.input.clone()).identity()? != hash
            {
                return Err(frame::integrity(
                    "Pending artifact is bound to another snapshot or renderer build.",
                ));
            }
            let bytes = frame::encode(&snapshot, input.frame)?;
            frame::promote(&directory, &pending, &bytes)?;
            let receipt = pending.receipt(&snapshot, &bytes)?;
            transaction.execute(
                "INSERT INTO artifacts(id,receipt) VALUES (?,?)",
                params![
                    receipt.artifact_id.as_str(),
                    serde_json::to_string(&receipt)?
                ],
            )?;
            let result = CommandResult::Artifact(receipt);
            save_result(&transaction, &input.intent_id, &hash, &result)?;
            transaction.commit()?;
            crate::checkpoint("after-receipt-commit");
            Ok(Execution {
                result,
                replayed: false,
            })
        }
        Command::VerifyArtifact(input) => {
            let json: Option<String> = connection
                .query_row(
                    "SELECT receipt FROM artifacts WHERE id=?",
                    [input.artifact_id.as_str()],
                    |row| row.get(0),
                )
                .optional()?;
            let receipt: ArtifactReceipt = serde_json::from_str(&json.ok_or_else(|| {
                EditorError::new(
                    ErrorCode::ArtifactNotFound,
                    "Artifact is not registered in this project.",
                )
            })?)?;
            if receipt.project_id != input.project_id || receipt.artifact_id != input.artifact_id {
                return Err(frame::integrity(
                    "Receipt is registered under a different project or artifact.",
                ));
            }
            let snapshot = snapshot(&connection, &project_id, Some(receipt.revision))?;
            Ok(Execution {
                result: CommandResult::Verification(frame::verify(
                    &directory, &snapshot, &receipt,
                )?),
                replayed: false,
            })
        }
    }
}
