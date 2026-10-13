"""Verify a Release Kit ZIP without extraction or third-party dependencies."""

import hashlib
import json
from pathlib import Path
import sys
import zipfile

NAMES = (
    "film.mp4", "short-1.mp4", "short-2.mp4", "short-3.mp4",
    "thumbnail.jpg", "artwork.jpg", "project.json", "manifest.json",
)


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def verify(archive_path, descriptor):
    path = Path(archive_path)
    require(path.stat().st_size == descriptor["bytes"], "Archive byte count differs.")
    entries = descriptor["entries"]
    require(len(entries) == 8 and {item["name"] for item in entries} == set(NAMES),
            "Archive descriptor must identify exactly eight safe entries.")
    expected = {item["name"]: item for item in entries}
    require(expected["manifest.json"]["sha256"] == descriptor["manifestSha256"],
            "Manifest identity differs from the descriptor.")
    documents = {}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        require(len(infos) == 8 and {item.filename for item in infos} == set(NAMES),
                "Archive entries are missing, duplicate or unexpected.")
        for info in infos:
            wanted = expected[info.filename]
            require(not info.is_dir() and info.compress_type == zipfile.ZIP_STORED and
                    not info.flag_bits & 1 and info.file_size == wanted["bytes"] and
                    info.compress_size == info.file_size,
                    "Archive entry encoding or size differs.")
            checksum = hashlib.sha256()
            count = 0
            json_parts = []
            is_json = info.filename.endswith(".json")
            require(not is_json or info.file_size <= 4 * 1024 * 1024,
                    "Archive JSON exceeds 4 MiB.")
            with archive.open(info) as source:
                while chunk := source.read(1024 * 1024):
                    count += len(chunk)
                    require(count <= wanted["bytes"], "Archive entry exceeds its size.")
                    checksum.update(chunk)
                    if is_json:
                        json_parts.append(chunk)
            require(count == wanted["bytes"] and checksum.hexdigest() == wanted["sha256"],
                    "Archive entry checksum differs.")
            if is_json:
                documents[info.filename] = json.loads(b"".join(json_parts).decode("utf-8"))
    manifest = documents["manifest.json"]
    project = documents["project.json"]
    require(manifest["schemaVersion"] == 1 and manifest["format"] == "release-kit",
            "Unsupported kit manifest.")
    for field in ("jobId", "releaseId", "projectId", "revision"):
        require(manifest[field] == descriptor[field], "Manifest render binding differs.")
    for field in ("releaseId", "briefSha256", "audioSha256"):
        require(manifest[field] == project[field], "Project source binding differs.")
    require(manifest["project"] == expected["project.json"], "Project file binding differs.")
    files = manifest["files"]
    require(len(files) == 6 and {item["name"] for item in files} == set(NAMES[:6]),
            "Manifest must identify all six outputs.")
    for item in files:
        wanted = expected[item["name"]]
        require(item["name"] == item["id"] + (".jpg" if item["id"] in
                ("thumbnail", "artwork") else ".mp4") and
                item["bytes"] == wanted["bytes"] and item["sha256"] == wanted["sha256"] and
                item["completeDecode"] is True,
                "Manifest output binding differs.")
    require(manifest["verification"] == {"measured": True, "storedByteReadback": True},
            "Verified render evidence is missing.")
    require(all(manifest[field] is False for field in
                ("motionReviewed", "heard", "creativelyAccepted")),
            "Packaging cannot establish creative review.")
    return {"archiveEntriesVerified": 8, "manifestSha256": descriptor["manifestSha256"],
            "motionReviewed": False, "heard": False, "creativelyAccepted": False}


if __name__ == "__main__":
    try:
        require(len(sys.argv) == 3, "Provide archive and descriptor paths.")
        descriptor_path = Path(sys.argv[2])
        require(descriptor_path.stat().st_size <= 65536, "Descriptor exceeds 64 KiB.")
        print(json.dumps(verify(sys.argv[1], json.loads(descriptor_path.read_text())), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, RuntimeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}), file=sys.stderr)
        sys.exit(1)
