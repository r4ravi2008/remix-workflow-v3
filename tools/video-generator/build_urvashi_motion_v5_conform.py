"""Prepare the Urvashi v5 motion conform for a new DaVinci Resolve timeline.

This is an offline preflight. It never imports into Resolve, starts a render, or
substitutes a still for missing motion. Re-run it after C039/C041 are accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path


ROOT = Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video"
)
PRODUCTION = ROOT / "motion-production-v5"
DESTINATION = ROOT / "resolve" / "motion-v5-finish-v1"
FPS = 24
TOTAL_FRAMES = 4482
AUDIO_SHA256 = "55134cca7e18f7cfb487bb0eca0bde43d9a4d238f18494054c537d1371f1f5aa"

# The locked story cuts remain in place. These selective handoffs carry the
# established trapezoid language; the other boundaries keep their clean cuts.
HERO_HANDOFFS = [
    ("C001", "C002", "parallel_trapezoid", 6),
    ("C003", "C004", "crimson_diagonal", 6),
    ("C005", "C006", "architectural_shutter", 6),
    ("C008", "C009", "portrait_slit", 6),
    ("C013", "C014", "crimson_diagonal", 8),
    ("C016", "C017", "architectural_shutter", 8),
    ("C019", "C020", "reflection_split", 8),
    ("C024", "C025", "parallel_trapezoid", 8),
    ("C026d", "C027", "reflection_split", 8),
    ("C030", "C031", "portrait_slit", 8),
    ("C034", "C035", "crossed_trapezoid", 8),
    ("C038", "C039", "broad_threshold", 10),
    ("C040b", "C041", "broad_threshold", 12),
]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    result = subprocess.check_output(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames",
         "-of", "json", str(path)], text=True
    )
    return json.loads(result)["streams"][0]


def parse_frames(value: str) -> int:
    if value == "0s":
        return 0
    numerator, denominator = value.removesuffix("s").split("/")
    assert int(denominator) == FPS
    return int(numerator)


def source_crop(item: dict, stream: dict) -> tuple[int, int, int, int]:
    width, height = int(stream["width"]), int(stream["height"])
    crop = item.get("sourceCrop")
    if crop is None and (width, height) == (1536, 640):
        crop = [0, 0, width, height]
    if crop is None:
        raise ValueError(
            f"Review the full generated frame and record sourceCrop=[x,y,w,h] "
            f"for {width}x{height} source {item['path']} before conforming it"
        )
    if len(crop) != 4 or any(not isinstance(v, int) for v in crop):
        raise ValueError(f"Invalid sourceCrop for {item['path']}: {crop}")
    x, y, w, h = crop
    if x < 0 or y < 0 or w < 2 or h < 2 or x + w > width or y + h > height:
        raise ValueError(f"sourceCrop is outside the source for {item['path']}: {crop}")
    if abs(w / h - 2.4) > .01:
        raise ValueError(f"sourceCrop must preserve the 2.4:1 active picture: {crop}")
    return x, y, w, h


def normalize(source: Path, target: Path, source_hash: str,
              crop: tuple[int, int, int, int], source_rate: str) -> dict:
    receipt = target.with_suffix(".json")
    if target.exists() and receipt.exists():
        old = json.loads(receipt.read_text())
        same_crop = old.get("sourceCrop") == list(crop) or (
            "sourceCrop" not in old and crop == (0, 0, 1536, 640)
        )
        same_rate = old.get("sourceFrameRate") == source_rate or (
            "sourceFrameRate" not in old and source_rate == "24/1"
        )
        if (old.get("sourceSha256") == source_hash and same_crop and same_rate
                and old.get("normalizedSha256") == sha(target)):
            return old
    temporary = target.with_suffix(".building.mp4")
    x, y, w, h = crop
    filters = f"crop={w}:{h}:{x}:{y},scale=1920:800:flags=lanczos,crop=1920:790:0:5,"
    filters += "pad=1920:1080:0:145:black,setsar=1"
    if source_rate != "24/1":
        filters += ",fps=24"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(source), "-map", "0:v:0", "-an",
         "-vf", filters,
         "-fps_mode", "passthrough", "-c:v", "libx264", "-preset", "medium",
         "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(temporary)], check=True
    )
    check = probe(temporary)
    assert (check["width"], check["height"], check["r_frame_rate"]) == (1920, 1080, "24/1")
    temporary.replace(target)
    record = {"source": str(source), "sourceSha256": source_hash,
              "normalized": str(target), "normalizedSha256": sha(target),
              "frames": int(check["nb_read_frames"]),
              "sourceCrop": list(crop), "sourceFrameRate": source_rate,
              "geometry": "1920x790 active picture; 145px top and bottom matte"}
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    media_dir = DESTINATION / "media"
    media_dir.mkdir(exist_ok=True)

    contract = json.loads((ROOT / "hyperreal-story-review-v5/edit-contract.json").read_text())
    inventory = json.loads((PRODUCTION / "downloaded-inventory.json").read_text())
    selections = json.loads((PRODUCTION / "motion-selections.json").read_text())
    beat_map = json.loads((ROOT / "analysis/urvashi-current/audio-map-measured.json").read_text())
    song = ROOT / "audio/urvashi-suno-master.mp3"
    assert sha(song) == AUDIO_SHA256 == beat_map["sha256"] == contract["audioSha256"]
    cuts = contract["cuts"]
    assert len(cuts) == 49 and cuts[0]["startFrame"] == 0 and cuts[-1]["endFrameExclusive"] == TOTAL_FRAMES
    assert all(left["endFrameExclusive"] == right["startFrame"] for left, right in zip(cuts, cuts[1:]))

    placement_by_cut = {"C007": ("C007", 0, 97)}
    for plan_path in sorted(PRODUCTION.glob("batch-*/plan.json")):
        plan = json.loads(plan_path.read_text())
        for job in plan["jobs"]:
            for placement in job["placements"]:
                cut_id = placement["cutId"]
                assert cut_id not in placement_by_cut, cut_id
                placement_by_cut[cut_id] = (
                    job["jobId"], placement["sourceInFrame"], placement["sourceOutFrameExclusive"]
                )
    assert set(placement_by_cut) == {cut["cutId"] for cut in cuts}

    cut_by_id = {cut["cutId"]: cut for cut in cuts}
    shift_by_cut = {}
    transitions = []
    beat_frames = [round(beat * FPS) for beat in beat_map["beats"]]
    onset_frames = [round(onset * FPS) for onset in beat_map["onsets"]]
    for outgoing, incoming, style, length in HERO_HANDOFFS:
        boundary = cut_by_id[incoming]["startFrame"]
        assert cut_by_id[outgoing]["endFrameExclusive"] == boundary
        assert cut_by_id[outgoing]["durationFrames"] >= length
        shift_by_cut[incoming] = length
        nearest = min(beat_frames, key=lambda beat: abs(beat - boundary))
        nearest_onset = min(onset_frames, key=lambda onset: abs(onset - boundary))
        music_role = ("beat handoff" if abs(boundary - nearest) <= 2 else
                      "transient handoff" if abs(boundary - nearest_onset) <= 2 else
                      "phrase handoff, pending listening")
        transitions.append({
            "outgoing": outgoing, "incoming": incoming, "family": style,
            "startFrame": boundary - length, "endFrameExclusive": boundary,
            "durationFrames": length, "nearestMeasuredBeatFrame": nearest,
            "beatOffsetFromCutFrames": boundary - nearest,
            "nearestMeasuredOnsetFrame": nearest_onset,
            "onsetOffsetFromCutFrames": boundary - nearest_onset,
            "musicRole": music_role,
            "incomingSourceStartFrame": length,
            "implementation": "Fusion masked incoming frames 0..N-1 over outgoing tail; clean incoming clip starts at N",
        })

    assets = {}
    placements = []
    missing = []
    for cut in cuts:
        cut_id = cut["cutId"]
        generation_id, source_in, source_out = placement_by_cut[cut_id]
        assert source_out - source_in == cut["durationFrames"], cut_id
        selected_id = selections.get(generation_id, {}).get("assetId", generation_id)
        item = inventory["assets"].get(selected_id)
        shift = shift_by_cut.get(cut_id, 0)
        if item is None:
            missing.append(cut_id)
            placements.append({"cutId": cut_id, "status": "MISSING_MOTION", "generationId": generation_id,
                               "timelineStartFrame": cut["startFrame"], "timelineEndFrameExclusive": cut["endFrameExclusive"]})
            continue
        assert item["reviewStatus"] != "REJECTED", selected_id
        source = Path(item["path"])
        assert source.exists() and sha(source) == item["sha256"], selected_id
        if generation_id in selections:
            assert item["sha256"] == selections[generation_id]["sha256"]
        if selected_id not in assets:
            original_probe = probe(source)
            crop = source_crop(item, original_probe)
            target = media_dir / f"{selected_id}-letterbox-v1.mp4"
            normalized = normalize(source, target, item["sha256"], crop,
                                   original_probe["r_frame_rate"]) if args.normalize else None
            assets[selected_id] = {"original": str(source), "originalSha256": item["sha256"],
                                   "originalFrames": int(original_probe["nb_read_frames"]),
                                   "originalFrameRate": original_probe["r_frame_rate"],
                                   "sourceCrop": list(crop),
                                   "normalized": str(target), "normalizedReceipt": normalized,
                                   "reviewStatus": item["reviewStatus"]}
        available = (assets[selected_id]["normalizedReceipt"]["frames"] if args.normalize
                     else int(Fraction(assets[selected_id]["originalFrames"] * FPS) /
                              Fraction(assets[selected_id]["originalFrameRate"])))
        assert source_out + shift <= available, (cut_id, source_out, shift, available)
        placements.append({
            "cutId": cut_id, "generationId": generation_id, "selectedAssetId": selected_id,
            "timelineStartFrame": cut["startFrame"], "timelineEndFrameExclusive": cut["endFrameExclusive"],
            "sourceStartFrame": source_in + shift, "sourceEndFrameExclusive": source_out + shift,
            "reviewStatus": item["reviewStatus"], "status": "PREPARED_UNREVIEWED",
        })

    manifest = {
        "status": "READY_FOR_RESOLVE_IMPORT" if not missing and args.normalize else "PREPARING",
        "timeline": "URVASHI MOTION V5 BEAT TRAPEZOID v1",
        "fps": FPS, "totalFrames": TOTAL_FRAMES, "audio": str(song), "audioSha256": AUDIO_SHA256,
        "sourceContract": str(ROOT / "hyperreal-story-review-v5/edit-contract.json"),
        "beatMap": str(ROOT / "analysis/urvashi-current/audio-map-measured.json"),
        "sourceMotionAccepted": (not missing and all(
            asset["reviewStatus"] == "ACCEPTED_NORMAL_SPEED" for asset in assets.values()
        )),
        "fullPlaybackReview": "PENDING",
        "assets": assets, "placements": placements, "missingCuts": missing,
        "transitions": transitions,
        "styleNotes": {
            "palette": ["charcoal", "crimson", "muted teal", "ivory", "warm gray"],
            "trapezoidAngleDegrees": 14,
            "rule": "Use crisp opaque image panels, no generic dissolve, black veil, repeating zoom jolt, or constant graphics.",
            "density": "13 deliberate handoffs across 48 boundaries; leave the micro-cut exchanges and intimate holds clean.",
        },
    }
    (DESTINATION / "assembly-plan.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if missing or not args.normalize:
        print(json.dumps({"status": manifest["status"], "missingCuts": missing,
                          "preparedAssets": len(assets), "transitions": len(transitions)}))
        return

    tree = ET.parse(ROOT / "hyperreal-story-review-v5/story-cut.fcpxml")
    project = tree.getroot().find(".//project")
    project.set("name", manifest["timeline"])
    resources = {asset.get("id"): asset for asset in tree.getroot().findall("./resources/asset")}
    rows = tree.getroot().findall(".//spine/asset-clip")
    assert len(rows) == len(placements)
    for row, placement in zip(rows, placements):
        assert row.get("name").split()[0] == placement["cutId"]
        asset = resources[row.get("ref")]
        selected = assets[placement["selectedAssetId"]]
        asset.set("src", Path(selected["normalized"]).as_uri())
        asset.set("name", placement["selectedAssetId"] + " v5 motion")
        asset.set("duration", f"{selected['normalizedReceipt']['frames']}/{FPS}s")
        row.set("name", placement["cutId"] + " " + placement["selectedAssetId"] + " MOTION")
        row.set("start", f"{placement['sourceStartFrame']}/{FPS}s")
        assert parse_frames(row.get("offset")) == placement["timelineStartFrame"]
        assert parse_frames(row.get("duration")) == cut_by_id[placement["cutId"]]["durationFrames"]
    target = DESTINATION / "urvashi-motion-v5-beat-trapezoid-v1.fcpxml"
    ET.indent(tree, space="  ")
    tree.write(target, encoding="utf-8", xml_declaration=True)
    print(json.dumps({"status": manifest["status"], "fcpxml": str(target),
                      "preparedAssets": len(assets), "transitions": len(transitions)}))


if __name__ == "__main__":
    main()
