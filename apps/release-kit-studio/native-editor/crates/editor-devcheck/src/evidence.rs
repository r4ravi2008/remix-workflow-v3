use crate::model::*;
use flate2::read::ZlibDecoder;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};

pub fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
pub fn file(path: &Path) -> io::Result<HashedFile> {
    let bytes = fs::read(path)?;
    Ok(HashedFile {
        path: path.display().to_string(),
        bytes: bytes.len() as u64,
        sha256: sha(&bytes),
    })
}
pub fn json(path: &Path) -> io::Result<Value> {
    serde_json::from_slice(&fs::read(path)?).map_err(io::Error::other)
}
pub fn write_new(path: &Path, value: &impl serde::Serialize) -> io::Result<()> {
    let mut f = fs::OpenOptions::new()
        .create_new(true)
        .write(true)
        .open(path)?;
    f.write_all(&serde_json::to_vec_pretty(value)?)?;
    f.write_all(b"\n")?;
    f.sync_all()
}
fn files(root: &Path, directory: &Path, output: &mut Vec<PathBuf>) -> io::Result<()> {
    for entry in fs::read_dir(directory)? {
        let e = entry?;
        if directory == root
            && ["target", ".runs", ".state", ".git"]
                .contains(&e.file_name().to_string_lossy().as_ref())
            && e.file_type()?.is_dir()
        {
            continue;
        }
        if e.file_type()?.is_symlink() {
            return Err(io::Error::other(format!(
                "symlink in observed inventory: {}",
                e.path().display()
            )));
        }
        if e.file_type()?.is_dir() {
            files(root, &e.path(), output)?
        } else if e.file_type()?.is_file() {
            output.push(e.path())
        }
    }
    Ok(())
}
pub fn source_identity(root: &Path) -> io::Result<SourceIdentity> {
    let mut paths = vec![];
    files(root, root, &mut paths)?;
    paths.extend(crate::policy::external_sources(root));
    paths.push(root.join("../package.json"));
    let mut observed = std::collections::BTreeSet::new();
    paths.retain(|p| p.canonicalize().is_ok_and(|p| observed.insert(p)));
    paths.sort();
    let mut sources = vec![];
    for path in paths {
        if fs::symlink_metadata(&path)?.file_type().is_symlink() {
            return Err(io::Error::other(format!(
                "symlink source input: {}",
                path.display()
            )));
        }
        let mut hash = file(&path)?;
        hash.path = path
            .strip_prefix(root)
            .unwrap_or(&path)
            .display()
            .to_string();
        sources.push(hash)
    }
    let digest = sha(&serde_json::to_vec(&sources)?);
    Ok(SourceIdentity {scope:"Every regular native-editor file excluding only root generated target, .runs, .state and .git directories, declared and referenced source inputs for every target kind and the document checker parent package input; current observed snapshot only".into(),files:sources,sha256:digest})
}
pub fn artifact_inventory(run: &Path) -> io::Result<(Vec<HashedFile>, Vec<EvidenceLink>)> {
    let mut paths = vec![];
    let mut links = vec![];
    fn collect(
        run: &Path,
        path: &Path,
        out: &mut Vec<PathBuf>,
        links: &mut Vec<EvidenceLink>,
    ) -> io::Result<()> {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            if entry.file_name() == "targets" {
                continue;
            }
            if entry.file_type()?.is_symlink() {
                let relative = entry.path().strip_prefix(run).unwrap().to_owned();
                let components: Vec<_> = relative
                    .components()
                    .map(|c| c.as_os_str().to_string_lossy().into_owned())
                    .collect();
                if components.len() < 4
                    || components[0] != "tests"
                    || !["default", "test-hooks"].contains(&components[1].as_str())
                    || !components[2].starts_with("P0-PATHS-")
                {
                    return Err(io::Error::other("unexpected symlink evidence"));
                }
                let target = fs::read_link(entry.path())?;
                let case = run.join("tests").join(&components[1]).join(&components[2]);
                if !target.starts_with(case)
                    || target
                        .components()
                        .any(|c| matches!(c, std::path::Component::ParentDir))
                {
                    return Err(io::Error::other("path fixture symlink escapes its case"));
                }
                let target = target.display().to_string();
                links.push(EvidenceLink {path:entry.path().display().to_string(),target_sha256:sha(target.as_bytes()),target,scope:"Deliberate P0 rejected-path fixture; link target is recorded and never followed as evidence".into()});
                continue;
            }
            if entry.file_type()?.is_dir() {
                collect(run, &entry.path(), out, links)?
            } else if entry.file_name() != "report.json" && entry.file_name() != "run.partial.json"
            {
                out.push(entry.path())
            }
        }
        Ok(())
    }
    collect(run, run, &mut paths, &mut links)?;
    paths.sort();
    let files = paths
        .iter()
        .map(|p| file(p))
        .collect::<io::Result<Vec<_>>>()?;
    Ok((files, links))
}

pub fn receipt(path: &Path, root: &Path) -> io::Result<Vec<Violation>> {
    let value = json(path)?;
    let mut v = vec![];
    let feature = path
        .file_name()
        .is_some_and(|n| n == "feature-coverage.json");
    let expected_kind = if feature {
        "feature-document-coverage"
    } else {
        "specification-check"
    };
    let shape_ok = if feature {
        value["expectedFeatures"] == 81
            && value["observedFeatures"] == 81
            && value["documentCount"] == 7
            && value["issues"] == serde_json::json!([])
    } else {
        value["capabilities"] == 81
            && value["runtimeChecked"] == false
            && value["runtimeVerified"] == false
            && value["cloudDeployed"] == false
            && value["creativelyAccepted"] == false
    };
    if value["kind"] != expected_kind
        || value["verdict"] != "VERIFIED"
        || !shape_ok
        || value["scope"].as_str().is_none_or(|s| !s.contains("only"))
    {
        v.push(Violation::new(
            "receipt-shape",
            Some(path.display().to_string()),
            "Receipt kind, verdict, counts or assurance scope differs",
        ));
    }

    let Some(hashes) = value["hashes"].as_object() else {
        return Ok(vec![Violation::new(
            "receipt-shape",
            Some(path.display().to_string()),
            "Missing receipt hashes",
        )]);
    };
    let required = if feature {
        vec![
            "coverage.json",
            "capabilities.json",
            "../FEATURES.md",
            "core.md",
            "media-cut.md",
            "editing.md",
            "audio.md",
            "color-photo.md",
            "fusion-ai.md",
            "delivery-collaboration-extensions.md",
        ]
    } else {
        vec![
            "capabilities.json",
            "Cargo.toml",
            "Cargo.lock",
            "docs/SPEC.md",
            "docs/ARCHITECTURE.md",
            "docs/check-spec.mjs",
            "docs/features/check.mjs",
        ]
    };
    for name in required {
        if !hashes.contains_key(name) {
            v.push(Violation::new(
                "receipt-input",
                Some(path.display().to_string()),
                format!("Missing receipt input {name}"),
            ));
        }
    }
    for (name, digest) in hashes {
        let target = if path
            .file_name()
            .is_some_and(|n| n == "feature-coverage.json")
            && name != "capabilities.json"
        {
            root.join("docs/features").join(name)
        } else {
            root.join(name)
        };
        if file(&target)?.sha256 != digest.as_str().unwrap_or("") {
            v.push(Violation::new(
                "receipt-hash",
                Some(target.display().to_string()),
                "Document receipt differs from actual bytes",
            ));
        }
    }
    if hashes.get("capabilities.json").and_then(|v| v.as_str())
        != Some(file(&root.join("capabilities.json"))?.sha256.as_str())
    {
        v.push(Violation::new(
            "receipt-ledger",
            None,
            "Receipt lacks current ledger binding",
        ));
    }
    Ok(v)
}
pub fn discovery(value: &Value, binary: &HashedFile) -> Vec<Violation> {
    let mut v = vec![];
    if value["binarySha256"].as_str() != Some(&binary.sha256)
        || value["schemaSha256"].as_str().is_none_or(|s| s.len() != 64)
        || value["protocolVersion"] != 1
        || value["identityVersion"] != 1
    {
        v.push(Violation::new(
            "runtime-identity",
            Some(binary.path.clone()),
            "Discovery identity differs from measured executable or P0 protocol",
        ));
    }
    let tools: BTreeSet<_> = value["tools"]
        .as_array()
        .map(|a| a.iter().filter_map(|t| t["name"].as_str()).collect())
        .unwrap_or_default();
    let expected: BTreeSet<_> = [
        "engine.capabilities",
        "project.create",
        "project.inspect",
        "project.commit",
        "frame.render",
        "artifact.verify",
    ]
    .into_iter()
    .collect();
    if tools != expected {
        v.push(Violation::new(
            "runtime-tools",
            None,
            "Default tools differ from the six P0 tools",
        ));
    }
    v
}
pub fn progress(value: &Value, ledger: &Value, discovery: &Value) -> Vec<Violation> {
    let mut v = vec![];
    if value["engine"] != *discovery {
        v.push(Violation::new(
            "runtime-progress-identity",
            None,
            "Progress engine differs from measured discovery",
        ));
    }
    let Some(features) = value["capabilities"].as_array() else {
        return vec![Violation::new(
            "runtime-progress-shape",
            None,
            "Missing progress families",
        )];
    };
    let Some(authored) = ledger["capabilities"].as_array() else {
        return vec![Violation::new(
            "ledger-shape",
            None,
            "Missing ledger families",
        )];
    };
    let ids: BTreeSet<_> = discovery["implementedFeatureIds"]
        .as_array()
        .map(|a| a.iter().filter_map(|v| v.as_str()).collect())
        .unwrap_or_default();
    if ids
        != [
            "CORE-01", "CORE-02", "CORE-03", "CORE-04", "CORE-05", "CORE-06", "CORE-07", "CORE-08",
        ]
        .into_iter()
        .collect()
    {
        v.push(Violation::new(
            "runtime-p0-families",
            None,
            "Compiled implemented families differ from bounded P0",
        ));
    }
    if features.len() != authored.len() {
        v.push(Violation::new(
            "runtime-progress-count",
            None,
            "Progress family count differs from ledger",
        ));
    }
    let expected_ids: BTreeSet<_> = authored.iter().filter_map(|f| f["id"].as_str()).collect();
    let actual_ids: BTreeSet<_> = features.iter().filter_map(|f| f["id"].as_str()).collect();
    if expected_ids != actual_ids || actual_ids.len() != features.len() {
        v.push(Violation::new(
            "runtime-progress-ids",
            None,
            "Progress IDs must be unique and exactly match the ledger",
        ));
    }
    for f in features {
        let id = f["id"].as_str().unwrap_or("");
        let expected = if ids.contains(id) {
            "implemented"
        } else {
            "planned"
        };
        if f["state"] != expected
            || f["evidence"] != serde_json::json!([])
            || !authored
                .iter()
                .any(|a| a["id"] == f["id"] && a["state"] == expected)
        {
            v.push(Violation::new(
                "runtime-progress-state",
                None,
                format!("Runtime/ledger state mismatch for {id}"),
            ));
        }
    }
    v
}
pub fn png_pixels(path: &Path) -> io::Result<(u32, u32, Vec<u8>)> {
    let bytes = fs::read(path)?;
    if bytes.get(..8) != Some(b"\x89PNG\r\n\x1a\n") {
        return Err(io::Error::other("PNG signature"));
    }
    let mut offset = 8usize;
    let mut dimensions = None;
    let mut data = vec![];
    let mut ended = false;
    while offset < bytes.len() {
        let header = bytes
            .get(offset..offset + 8)
            .ok_or_else(|| io::Error::other("PNG chunk header"))?;
        let length = u32::from_be_bytes(header[..4].try_into().unwrap()) as usize;
        let chunk = bytes
            .get(offset + 8..offset + 8 + length)
            .ok_or_else(|| io::Error::other("PNG truncated chunk"))?;
        let crc = bytes
            .get(offset + 8 + length..offset + 12 + length)
            .ok_or_else(|| io::Error::other("PNG CRC"))?;
        let mut actual = 0xffffffffu32;
        for b in header[4..].iter().chain(chunk) {
            actual ^= *b as u32;
            for _ in 0..8 {
                actual = (actual >> 1) ^ if actual & 1 == 1 { 0xedb88320 } else { 0 }
            }
        }
        if !actual != u32::from_be_bytes(crc.try_into().unwrap()) {
            return Err(io::Error::other("PNG CRC mismatch"));
        }
        match &header[4..] {
            b"IHDR" => {
                if chunk.len() != 13 || chunk[8..] != [8, 6, 0, 0, 0] {
                    return Err(io::Error::other("PNG format"));
                }
                dimensions = Some((
                    u32::from_be_bytes(chunk[..4].try_into().unwrap()),
                    u32::from_be_bytes(chunk[4..8].try_into().unwrap()),
                ));
            }
            b"IDAT" => data.extend_from_slice(chunk),
            b"IEND" => {
                ended = true;
                if !chunk.is_empty() {
                    return Err(io::Error::other("PNG IEND"));
                }
            }
            _ => {}
        }
        offset += length + 12;
    }
    let (w, h) = dimensions.ok_or_else(|| io::Error::other("PNG dimensions"))?;
    if !ended || w == 0 || h == 0 || w > 2048 || h > 2048 {
        return Err(io::Error::other("PNG limits"));
    }
    let stride = w as usize * 4;
    let expected = (stride + 1) * h as usize;
    let mut scan = vec![];
    ZlibDecoder::new(&data[..])
        .take(expected as u64 + 1)
        .read_to_end(&mut scan)?;
    if scan.len() != expected {
        return Err(io::Error::other("PNG scanline length"));
    }
    let mut pixels = vec![];
    for row in scan.chunks_exact(stride + 1) {
        if row[0] != 0 {
            return Err(io::Error::other(
                "P0 decoder requires unfiltered native output",
            ));
        }
        pixels.extend_from_slice(&row[1..])
    }
    Ok((w, h, pixels))
}
pub fn demo(run: &Path, response: &Value, binary: &HashedFile) -> io::Result<Vec<Violation>> {
    let demo = run.join("runtime/default/demo");
    let receipt = json(&demo.join("receipt.json"))?;
    let commit = json(&demo.join("commit.json"))?;
    let create = json(&demo.join("create.json"))?;
    let artifact = PathBuf::from(
        response["preview"]
            .as_str()
            .ok_or_else(|| io::Error::other("demo preview"))?,
    )
    .canonicalize()?;
    if !artifact.starts_with(demo.canonicalize()?) {
        return Ok(vec![Violation::new(
            "evidence-escape",
            None,
            "Demo artifact escapes its run",
        )]);
    }
    let pixels = png_pixels(&artifact)?;
    let rgba: Vec<u8> = commit["edits"][0]["clip"]["source"]["rgba"]
        .as_array()
        .ok_or_else(|| io::Error::other("RGBA input"))?
        .iter()
        .map(|p| p.as_u64().unwrap_or(256) as u8)
        .collect();
    let mut v = vec![];
    if pixels.0 as u64 != create["timeline"]["canvas"]["width"].as_u64().unwrap_or(0)
        || pixels.1 as u64 != create["timeline"]["canvas"]["height"].as_u64().unwrap_or(0)
        || pixels.2.chunks_exact(4).any(|p| p != rgba)
    {
        v.push(Violation::new(
            "demo-pixels",
            None,
            "Independently decoded pixels differ from saved input",
        ));
    }
    if receipt != response["receipt"]
        || receipt["binarySha256"].as_str() != Some(&binary.sha256)
        || receipt["sha256"].as_str() != Some(file(&artifact)?.sha256.as_str())
        || response["verification"]["measuredSha256"] != receipt["sha256"]
        || response["verification"]["verified"] != true
    {
        v.push(Violation::new(
            "demo-receipt",
            None,
            "Artifact bytes or receipt binding differs",
        ));
    }
    Ok(v)
}
pub fn suite(
    directory: &Path,
    binary: &HashedFile,
    schema: &str,
    required: &BTreeSet<String>,
) -> io::Result<Vec<Violation>> {
    let mut v = vec![];
    let mut coverage = BTreeSet::new();
    for entry in fs::read_dir(directory)? {
        let e = entry?;
        if !e.file_type()?.is_dir() {
            continue;
        }
        let name = e.file_name().to_string_lossy().into_owned();
        let discovery_path = e.path().join("discovery.json");
        if !discovery_path.exists() {
            if required
                .iter()
                .any(|case| name.starts_with(&format!("{case}-")))
            {
                v.push(Violation::new(
                    "suite-discovery",
                    Some(e.path().display().to_string()),
                    "Named case has no discovery evidence",
                ));
            }
            continue;
        }
        let before = v.len();
        let mut process_count = 0;
        let d = json(&discovery_path)?;
        v.extend(discovery(&d, binary));
        if d["schemaSha256"] != schema {
            v.push(Violation::new(
                "suite-schema",
                Some(discovery_path.display().to_string()),
                "Suite discovery schema differs",
            ));
        }
        for p in fs::read_dir(e.path())? {
            let p = p?.path();
            let name = p.file_name().unwrap().to_string_lossy();
            if name.starts_with("process-") && name.ends_with(".json") {
                process_count += 1;
                let suffix = name.trim_start_matches("process-");
                let record = json(&p)?;
                let request = fs::read(e.path().join(format!("request-{suffix}")))?;
                let response = fs::read(e.path().join(format!("response-{suffix}")))?;
                if record["exitCode"].as_i64().is_none()
                    || record["requestSha256"] != sha(&request)
                    || record["responseSha256"] != sha(&response)
                    || record["stderr"].as_str().is_none()
                {
                    v.push(Violation::new(
                        "suite-process",
                        Some(p.display().to_string()),
                        "Process record differs from saved request/response bytes",
                    ));
                }
                let parsed: Value = serde_json::from_slice(&response).map_err(io::Error::other)?;
                if parsed["schemaSha256"] != schema || parsed["protocolVersion"] != 1 {
                    v.push(Violation::new(
                        "suite-response",
                        Some(p.display().to_string()),
                        "Process response identity differs",
                    ));
                }
                let stderr = record["stderr"].as_str().unwrap_or("").as_bytes();
                let audit = serde_json::json!({"processSha256":file(&p)?.sha256,"requestSha256":sha(&request),"responseSha256":sha(&response),"stderrSha256":sha(stderr)});
                let audit_path = e.path().join(format!("audit-{suffix}"));
                if !audit_path.exists() {
                    write_new(&audit_path, &audit)?;
                }
            }
        }
        if v.len() == before && process_count > 0 {
            for case in required {
                if name.starts_with(&format!("{case}-")) {
                    coverage.insert(case.clone());
                }
            }
        }
    }
    for case in required.difference(&coverage) {
        v.push(Violation::new(
            "suite-coverage",
            None,
            format!("Missing fresh named P0 evidence {case}"),
        ));
    }
    Ok(v)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn altered_discovery_is_rejected() {
        let b = HashedFile {
            path: "bin".into(),
            bytes: 1,
            sha256: "measured".into(),
        };
        assert!(!discovery(&serde_json::json!({"binarySha256":"forged"}), &b).is_empty());
    }
    #[test]
    fn exclusive_report_cannot_replace_bytes() {
        let p = std::env::temp_dir().join(format!("devcheck-exclusive-{}", crate::process::now()));
        write_new(&p, &serde_json::json!({"first":true})).unwrap();
        let before = fs::read(&p).unwrap();
        assert!(write_new(&p, &false).is_err());
        assert_eq!(fs::read(&p).unwrap(), before);
    }
}

#[cfg(test)]
mod suite_tests {
    use super::*;
    #[test]
    fn empty_case_and_changed_response_do_not_count() {
        let root = std::env::temp_dir().join(format!("devcheck-evidence-{}", SystemClock::ticks()));
        let case = root.join("P0-DISCOVERY-1-0");
        fs::create_dir_all(&case).unwrap();
        let binary = HashedFile {
            path: "bin".into(),
            bytes: 1,
            sha256: "measured".into(),
        };
        let required = ["P0-DISCOVERY".into()].into_iter().collect();
        assert!(!suite(&root, &binary, "schema", &required)
            .unwrap()
            .is_empty());
        let d = serde_json::json!({"binarySha256":"measured","schemaSha256":"s".repeat(64),"protocolVersion":1,"identityVersion":1,"tools":[{"name":"engine.capabilities"},{"name":"project.create"},{"name":"project.inspect"},{"name":"project.commit"},{"name":"frame.render"},{"name":"artifact.verify"}]});
        write_new(&case.join("discovery.json"), &d).unwrap();
        fs::write(case.join("request-0.json"), b"{}").unwrap();
        let response = serde_json::to_vec(
            &serde_json::json!({"protocolVersion":1,"schemaSha256":"s".repeat(64)}),
        )
        .unwrap();
        fs::write(case.join("response-0.json"), &response).unwrap();
        write_new(&case.join("process-0.json"),&serde_json::json!({"exitCode":0,"requestSha256":sha(b"{}"),"responseSha256":sha(&response),"stderr":""})).unwrap();
        assert!(suite(&root, &binary, &"s".repeat(64), &required)
            .unwrap()
            .is_empty());
        fs::write(case.join("response-0.json"), b"{}").unwrap();
        assert!(suite(&root, &binary, &"s".repeat(64), &required)
            .unwrap()
            .iter()
            .any(|v| v.code == "suite-process"));
    }
    struct SystemClock;
    impl SystemClock {
        fn ticks() -> u128 {
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        }
    }
}

pub fn canonical(value: &Value) -> Vec<u8> {
    fn write(value: &Value, out: &mut String) {
        match value {
            Value::Object(object) => {
                let mut keys: Vec<_> = object.keys().collect();
                keys.sort_by_key(|k| k.encode_utf16().collect::<Vec<_>>());
                out.push('{');
                for (i, key) in keys.into_iter().enumerate() {
                    if i > 0 {
                        out.push(',')
                    }
                    out.push_str(&serde_json::to_string(key).unwrap());
                    out.push(':');
                    write(&object[key], out)
                }
                out.push('}')
            }
            Value::Array(values) => {
                out.push('[');
                for (i, v) in values.iter().enumerate() {
                    if i > 0 {
                        out.push(',')
                    }
                    write(v, out)
                }
                out.push(']')
            }
            _ => out.push_str(&serde_json::to_string(value).unwrap()),
        }
    }
    let mut out = String::new();
    write(value, &mut out);
    out.into_bytes()
}

#[cfg(test)]
mod progress_regressions {
    use super::*;
    #[test]
    fn duplicated_family_cannot_hide_missing_family() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .parent()
            .unwrap();
        let ledger = json(&root.join("capabilities.json")).unwrap();
        let discovery = serde_json::json!({"implementedFeatureIds":["CORE-01","CORE-02","CORE-03","CORE-04","CORE-05","CORE-06","CORE-07","CORE-08"]});
        let mut observed = ledger.clone();
        observed["engine"] = discovery.clone();
        assert!(progress(&observed, &ledger, &discovery).is_empty());
        observed["capabilities"][1] = observed["capabilities"][0].clone();
        assert!(progress(&observed, &ledger, &discovery)
            .iter()
            .any(|v| v.code == "runtime-progress-ids"));
    }
}

#[cfg(test)]
mod source_binding_regressions {
    use super::*;
    #[test]
    fn nested_generated_names_and_external_target_sources_are_bound() {
        let outer = std::env::temp_dir().join(format!(
            "devcheck-inputs-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let root = outer.join("native-editor");
        fs::create_dir_all(&root).unwrap();
        fs::write(outer.join("package.json"), "{}").unwrap();
        for role in ["editor-core", "editor-cli", "editor-devcheck"] {
            let base = root.join("crates").join(role);
            fs::create_dir_all(base.join("src")).unwrap();
            fs::write(base.join("src/lib.rs"), "").unwrap();
            fs::write(
                base.join("Cargo.toml"),
                format!("[package]\nname='{role}'\n"),
            )
            .unwrap();
        }
        let base = root.join("crates/editor-cli");
        fs::create_dir_all(base.join("tests/target")).unwrap();
        fs::write(
            base.join("tests/target/helpers.rs"),
            "pub const VALUE:u8=1;",
        )
        .unwrap();
        fs::write(base.join("Cargo.toml"),"[package]\nname='editor-cli'\n[[test]]\nname='external'\npath='../../../outside-test.rs'\n[[bench]]\nname='outside-bench'\npath='../../../outside-bench.rs'\n[[example]]\nname='outside-example'\npath='../../../outside-example.rs'").unwrap();
        for name in ["outside-test.rs", "outside-bench.rs", "outside-example.rs"] {
            fs::write(outer.join(name), "fn main(){}").unwrap();
        }
        fs::write(
            outer.join("outside-test.rs"),
            "#[path=\"outside-helper.rs\"] mod helper; fn main(){}",
        )
        .unwrap();
        fs::write(outer.join("outside-helper.rs"), "pub const VALUE:u8=1;").unwrap();
        fs::create_dir(root.join("target")).unwrap();
        fs::write(root.join("target/generated.rs"), "ignored").unwrap();
        let before = source_identity(&root).unwrap();
        assert!(before
            .files
            .iter()
            .any(|f| f.path.ends_with("tests/target/helpers.rs")));
        assert!(!before.files.iter().any(|f| f.path == "target/generated.rs"));
        for name in [
            "outside-test.rs",
            "outside-bench.rs",
            "outside-example.rs",
            "outside-helper.rs",
        ] {
            assert!(before.files.iter().any(|f| f.path.ends_with(name)));
        }
        fs::write(outer.join("outside-helper.rs"), "pub const VALUE:u8=2;").unwrap();
        assert_ne!(source_identity(&root).unwrap().sha256, before.sha256);
    }
}
