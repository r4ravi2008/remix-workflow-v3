#!/usr/bin/env python3
"""Audit versioned workflow files without printing credentials or accessing providers.

Run before publication and after a fresh clone. Generic credential literals and
historical machine paths need human review; the report contains locations only.
This is a focused migration check, not a complete security scanner.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

PATTERNS = {
    "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "github-token": r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b",
    "aws-access-id": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "provider-token": r"\b(?:rpa_[A-Za-z0-9_-]{24,}|sk-[A-Za-z0-9_-]{24,})\b",
    "google-token": r"\b(?:AIza[A-Za-z0-9_-]{30,}|ya29\.[A-Za-z0-9_-]{30,})\b",
    "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
}
LITERAL = re.compile(r'''(?i)(?:api[_-]?key|secret|password|token|bearer|authorization)[\w\s"']{0,24}\s*[:=]\s*["'][^"'\n]{12,}["']''')
LOCAL_PATH = re.compile(r"/Users/|/opt/homebrew|/Applications/|/mnt/c/|artifacts/scratch-video-goal")


def audit(root):
    names = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
    ).decode().split("\0")
    patterns = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}
    files, blocked, literals, local_paths, errors = [], [], [], [], []
    for name in sorted(set(filter(None, names))):
        path = root / name
        if not path.is_file():
            errors.append({"path": name, "reason": "missing versioned file"})
            continue
        raw = path.read_bytes()
        files.append({"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        if path.is_symlink():
            errors.append({"path": name, "reason": "symlink requires target review"})
        if len(raw) > 25 * 1024 * 1024:
            errors.append({"path": name, "reason": "large file requires publication review"})
        if path.suffix == ".docx":
            with zipfile.ZipFile(path) as archive:
                text = "\n".join(archive.read(p).decode() for p in archive.namelist() if p.endswith(".xml"))
        else:
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
        for line_number, line in enumerate(text.splitlines(), 1):
            location = {"path": name, "line": line_number}
            for rule, pattern in patterns.items():
                if pattern.search(line):
                    blocked.append({**location, "rule": rule})
            if LITERAL.search(line):
                literals.append(location)
            if LOCAL_PATH.search(line):
                local_paths.append(location)
    for folder in ("tools/video-generator/template", "tools/visual-sequence"):
        manifest = json.loads((root / folder / "package.json").read_text())
        lock_path = root / folder / "package-lock.json"
        if not lock_path.is_file():
            errors.append({"path": str(lock_path.relative_to(root)), "reason": "missing portable dependency lock"})
            continue
        lock = json.loads(lock_path.read_text()).get("packages", {}).get("", {})
        for field in ("dependencies", "devDependencies"):
            if lock.get(field, {}) != manifest.get(field, {}):
                errors.append({"path": str(lock_path.relative_to(root)), "reason": field + " differ from manifest"})
    fixture_root = root / "apps/video-studio/crates/editor/tests/fixtures/alpha"
    for name in ("alpha-fixture-a03.json", "alpha-primary-a01.png", "alpha-transparent-a01.png", "grayscale-alpha-a01.png", "indexed-trns-a01.png", "rgb-trns-a01.png"):
        if not (fixture_root / name).is_file():
            errors.append({"path": str((fixture_root / name).relative_to(root)), "reason": "missing independent Rust test fixture"})
    return {
        "file_count": len(files), "files": files,
        "credential_pattern_matches": blocked,
        "credential_literal_review_locations": literals,
        "historical_machine_path_locations": local_paths, "errors": errors,
        "platform_notes": [
            "apps/video-studio uses macOS AVFoundation and is not a Linux renderer.",
            "agent/install-service.py uses launchctl; do not run it on a workstation or start a duplicate worker.",
            "Song-specific scripts contain historical machine paths. Review their inputs before execution.",
            "Credentials, production workspaces, databases, model weights and provider receipts are outside Git.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.root.resolve())
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "files"}, indent=2))
    return int(bool(report["credential_pattern_matches"] or report["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
