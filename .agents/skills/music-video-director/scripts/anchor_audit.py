#!/usr/bin/env python3
"""Audit anchor dimensions, matte geometry, names, hashes, and likely duplicates.

This is a technical preflight. It does not approve sharpness, identity, anatomy,
story continuity, or whether a visually similar pair is intentionally progressive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError as error:  # pragma: no cover - exercised by CLI environment
    raise SystemExit("Pillow is required; run with `uv run --with pillow python ...`") from error


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dhash(image):
    gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = gray.tobytes()
    value = 0
    for row in range(8):
        for column in range(8):
            value = (value << 1) | int(pixels[row * 9 + column] > pixels[row * 9 + column + 1])
    return value


def hamming(left, right):
    return (left ^ right).bit_count()


def region_matches(image, box, expected, tolerance):
    if box[0] == box[2] or box[1] == box[3]:
        return True
    extrema = image.crop(box).getextrema()
    for (minimum, maximum), target in zip(extrema[:3], expected):
        if minimum < max(0, target - tolerance) or maximum > min(255, target + tolerance):
            return False
    return True


def focus_proxy(image):
    gray = image.convert("L").filter(ImageFilter.FIND_EDGES)
    if gray.width > 4 and gray.height > 4:
        gray = gray.crop((2, 2, gray.width - 2, gray.height - 2))
    return round(ImageStat.Stat(gray).var[0], 2)


def validate_contract(contract):
    if contract.get("schemaVersion") != 1:
        raise ValueError("Unsupported contract schema")
    frame = contract["frame"]
    active = contract["activePicture"]
    for field in ("width", "height"):
        if type(frame.get(field)) is not int or frame[field] <= 0:
            raise ValueError(f"Invalid frame.{field}")
    for field in ("x", "y", "width", "height"):
        if type(active.get(field)) is not int or active[field] < 0:
            raise ValueError(f"Invalid activePicture.{field}")
    if active["width"] <= 0 or active["height"] <= 0:
        raise ValueError("Active picture must have positive dimensions")
    if active["x"] + active["width"] > frame["width"] or active["y"] + active["height"] > frame["height"]:
        raise ValueError("Active picture exceeds frame")
    color = contract["matte"]["color"]
    if not isinstance(color, list) or len(color) != 3 or any(type(value) is not int or not 0 <= value <= 255 for value in color):
        raise ValueError("matte.color must contain three 0-255 integers")
    tolerance = contract["matte"]["tolerance"]
    if type(tolerance) is not int or not 0 <= tolerance <= 255:
        raise ValueError("Invalid matte.tolerance")
    re.compile(contract["fileNamePattern"])


def audit(contract, directory):
    validate_contract(contract)
    frame = contract["frame"]
    active = contract["activePicture"]
    matte = contract["matte"]
    expected_size = (frame["width"], frame["height"])
    active_box = (
        active["x"],
        active["y"],
        active["x"] + active["width"],
        active["y"] + active["height"],
    )
    matte_boxes = [
        (0, 0, frame["width"], active["y"]),
        (0, active_box[3], frame["width"], frame["height"]),
        (0, active["y"], active["x"], active_box[3]),
        (active_box[2], active["y"], frame["width"], active_box[3]),
    ]
    pattern = re.compile(contract["fileNamePattern"])
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)
    records = []
    technical_issues = []

    for path in files:
        record = {"file": path.name, "sha256": sha256(path), "issues": []}
        if pattern.fullmatch(path.name) is None:
            record["issues"].append("filename_contract")
        try:
            with Image.open(path) as opened:
                image = opened.convert("RGB")
        except OSError as error:
            record["issues"].append(f"decode:{error}")
            records.append(record)
            continue
        record["width"], record["height"] = image.size
        if image.size != expected_size:
            record["issues"].append("frame_dimensions")
        else:
            if not all(region_matches(image, box, matte["color"], matte["tolerance"]) for box in matte_boxes):
                record["issues"].append("matte_contract")
            active_image = image.crop(active_box)
            record["dhash"] = f"{dhash(active_image):016x}"
            record["focusProxy"] = focus_proxy(active_image)
        records.append(record)

    hash_groups = {}
    for record in records:
        hash_groups.setdefault(record["sha256"], []).append(record["file"])
    exact_duplicates = [group for group in hash_groups.values() if len(group) > 1]

    distance_limit = contract.get("possibleDuplicateHammingDistance", 4)
    comparable = [record for record in records if "dhash" in record]
    possible_duplicates = []
    for index, left in enumerate(comparable):
        for right in comparable[index + 1:]:
            if left["sha256"] == right["sha256"]:
                continue
            distance = hamming(int(left["dhash"], 16), int(right["dhash"], 16))
            if distance <= distance_limit:
                possible_duplicates.append({"left": left["file"], "right": right["file"], "distance": distance})

    for record in records:
        technical_issues.extend({"file": record["file"], "issue": issue} for issue in record["issues"])
    if contract.get("failOnExactDuplicates", True):
        technical_issues.extend({"files": group, "issue": "exact_duplicate"} for group in exact_duplicates)

    return {
        "schemaVersion": 1,
        "directory": str(directory.resolve()),
        "contract": contract,
        "imageCount": len(records),
        "technicalPass": not technical_issues,
        "visualReviewRequired": True,
        "technicalIssues": technical_issues,
        "exactDuplicates": exact_duplicates,
        "possibleDuplicates": possible_duplicates,
        "images": records,
        "limitations": [
            "focusProxy is comparative evidence, not a sharpness verdict",
            "possibleDuplicates require chronological visual review",
            "identity, anatomy, story state, UI meaning, and composition are not automated",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text())
        if not args.directory.is_dir():
            raise ValueError(f"Not a directory: {args.directory}")
        report = audit(contract, args.directory)
        rendered = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        print(rendered, end="")
        return 0 if report["technicalPass"] else 1
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
