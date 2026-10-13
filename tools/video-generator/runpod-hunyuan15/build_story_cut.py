#!/usr/bin/env python3
"""Seal accepted anchors and author a frame-exact Resolve review interchange."""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame(seconds):
    return int(math.floor(seconds * 24 + 0.5))


def rt(value):
    return {"OTIO_SCHEMA": "RationalTime.1", "value": value, "rate": 24}


def clip(name, path, duration):
    return {"OTIO_SCHEMA": "Clip.2", "name": name,
            "source_range": {"OTIO_SCHEMA": "TimeRange.1", "start_time": rt(0), "duration": rt(duration)},
            "media_references": {"DEFAULT_MEDIA": {"OTIO_SCHEMA": "ExternalReference.1", "target_url": path.as_uri(), "available_range": None}},
            "active_media_reference_key": "DEFAULT_MEDIA"}


def lua(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "{" + ",".join(map(lua, value)) + "}"
    if isinstance(value, dict):
        return "{" + ",".join("[" + lua(k) + "]=" + lua(v) for k, v in value.items()) + "}"
    if value is None:
        return "nil"
    return str(value).lower()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--library", type=Path, required=True)
    p.add_argument("--audio-map", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--timing", choices=("exact", "beat-aligned"), default="exact")
    p.add_argument("--cut-map", type=Path, help="Revised editorial JSON: cuts with anchorId, startFrame, endFrameExclusive")
    args = p.parse_args()
    catalog_path = args.library / ("shot-pool-v2.json" if args.cut_map else "anchors.json")
    catalog = json.loads(catalog_path.read_text())
    measured = json.loads(args.audio_map.read_text())
    audio = Path(measured["audio"])
    assert sha(audio) == measured["sha256"], "Beat map belongs to different audio"
    pool = catalog.get("assets")
    if pool:
        anchors = [dict(a, timestampSeconds=int(a["legacyTimestampToken"][1:])/1000, beat=a["beatSlug"]) for a in pool]
    else:
        anchors = catalog["anchors"]
    anchors = sorted(anchors, key=lambda a: (a["timestampSeconds"], a["anchorId"]))
    for a in anchors:
        if not pool:
            assert a["active"]["status"] == "accepted-normalized", a["anchorId"]
        assert sha(args.library / a["active"]["file"]) == a["active"]["sha256"], f"Catalog is being revised: {a['anchorId']}"
    assert not args.output.exists(), "Use a fresh versioned output directory"
    cuts, endpoints = [], []
    for a in anchors:
        if a["anchorId"] == "S12-I03":
            endpoints.append(a)
            continue
        seconds = a["timestampSeconds"]
        nearest = min(measured["beats"], key=lambda t: abs(t-seconds)) if seconds else 0
        target = nearest if args.timing == "beat-aligned" else seconds
        cuts.append(dict(anchorId=a["anchorId"], beat=a["beat"], canonicalSeconds=seconds,
                         startFrame=frame(target), nearestBeatSeconds=nearest,
                         adjustmentFrames=frame(target)-frame(seconds),
                         beatOffsetFrames=frame(target)-frame(nearest),
                         sourceFile=a["active"]["file"], sha256=a["active"]["sha256"]))
    total = frame(measured["duration"])
    if args.cut_map:
        proposed = json.loads(args.cut_map.read_text())
        assert proposed.get("fps", proposed.get("timeline", {}).get("fps")) == 24
        assert proposed.get("audioSha256", proposed.get("audio", {}).get("sha256")) == measured["sha256"]
        by_id = {a["anchorId"]: a for a in anchors}
        cuts = []
        for row in proposed["cuts"]:
            a = by_id[row["anchorId"]]
            start = row["startFrame"]
            assert isinstance(start, int) and 0 <= start < total
            nearest = min(measured["beats"], key=lambda t: abs(t-start/24)) if start else 0
            cuts.append(dict(row, beat=a["beat"], canonicalSeconds=a["timestampSeconds"],
                             nearestBeatSeconds=nearest, adjustmentFrames=start-frame(a["timestampSeconds"]),
                             beatOffsetFrames=start-frame(nearest), sourceFile=a["active"]["file"], sha256=a["active"]["sha256"]))
        assert cuts[0]["startFrame"] == 0
    for i, c in enumerate(cuts):
        end = cuts[i+1]["startFrame"] if i+1 < len(cuts) else total
        if args.cut_map:
            assert c["endFrameExclusive"] == end, "Revised map has a gap or overlap"
        c["endFrameExclusive"] = end
        c["durationFrames"] = c["endFrameExclusive"]-c["startFrame"]
        assert c["durationFrames"] > 0, f"Ambiguous coincident cut: {c['anchorId']}"
    args.output.mkdir(parents=True)
    image_dir = args.output / "anchors"
    image_dir.mkdir()
    for a in anchors:
        src = args.library / a["active"]["file"]
        dst = image_dir / src.name
        shutil.copy2(src, dst)
        assert sha(dst) == a["active"]["sha256"]
    manifest = dict(schemaVersion=1, status="REVIEW_CANDIDATE_NOT_APPROVED_FOR_GENERATION",
                    timingPolicy=args.timing, fps=24, totalFrames=total, durationSeconds=total/24,
                    audio=str(audio), audioSha256=sha(audio), catalogSha256=sha(catalog_path),
                    sourceCatalog=str(catalog_path), beatMap=str(args.audio_map), beatMapSha256=sha(args.audio_map),
                    cuts=cuts, endpointReferences=endpoints, messageGraphics=proposed.get("messageGraphics", []) if args.cut_map else [],
                    contract="After user approval, every generated plate must fill [startFrame,endFrameExclusive) exactly. Never move cuts to fit generated duration.")
    (args.output / "edit-contract.json").write_text(json.dumps(manifest, indent=2))
    shutil.copy2(catalog_path, args.output / "source-catalog.json")
    video = [clip(c["anchorId"]+" "+c["beat"], image_dir/Path(c["sourceFile"]).name, c["durationFrames"]) for c in cuts]
    timeline = {"OTIO_SCHEMA":"Timeline.1", "name":"URVASHI STORY CUT v1 - "+args.timing.upper(), "global_start_time":rt(0),
                "tracks":{"OTIO_SCHEMA":"Stack.1","name":"tracks","children":[
                    {"OTIO_SCHEMA":"Track.1","name":"Anchor pictures - locked boundaries","kind":"Video","children":video},
                    {"OTIO_SCHEMA":"Track.1","name":"Canonical song - untouched","kind":"Audio","children":[clip("Urvashi canonical song",audio,total)]}]}}
    (args.output / "story-cut.otio").write_text(json.dumps(timeline, indent=2))
    lines = ["# Story-cut frame contract", "", "Review candidate. No GPU work authorized until reviewed.", "",
             f"24 fps; {total} frames; {len(cuts)} image holds; {len(endpoints)} additional endpoint reference.", "",
             "| Anchor | Original time | Cut time | Frames [in,out) | Beat offset (frames) |", "|---|---:|---:|---|---:|"]
    for c in cuts:
        lines.append(f"| {c['anchorId']} | {c['canonicalSeconds']:.3f} | {c['startFrame']/24:.3f} | {c['startFrame']}–{c['endFrameExclusive']} | {c['beatOffsetFrames']:+d} |")
    (args.output / "CUT-POINTS.md").write_text("\n".join(lines)+"\n")
    script = '''local base = BASE
local plan = PLAN
local f = assert(io.open(base.."/resolve-assembly.tsv","w"))
local function log(k,v) f:write(k,"\\t",tostring(v),"\\n"); f:flush(); print(k,v) end
local ok,err = pcall(function()
  local pm=resolve:GetProjectManager()
  local p=assert(pm:GetCurrentProject())
  assert(p:GetName()=="URVASHI HYPERREAL STORY CUT 20260921", "Unexpected active project")
  assert(not p:IsRenderingInProgress(), "Render active")
  assert(pm:SaveProject())
  local tl=assert(p:GetMediaPool():ImportTimelineFromFile(base.."/story-cut.otio",{importSourceClips=true}), "Timeline import failed")
  assert(p:SetCurrentTimeline(tl))
  assert(tl:SetStartTimecode("00:00:00:00"))
  local items=tl:GetItemListInTrack("video",1)
  assert(#items==#plan.cuts,"Imported clip count mismatch")
  local start=tl:GetStartFrame()
  for i,c in ipairs(plan.cuts) do
    local item=items[i]
    log(c.anchorId,item:GetStart()-start..","..item:GetEnd()-start..","..item:GetDuration())
    assert(item:GetStart()-start==c.startFrame and item:GetDuration()==c.durationFrames,"Cut timing mismatch: "..c.anchorId)
    tl:AddMarker(c.startFrame,"Blue",c.anchorId,c.beat.."; generation interval "..c.startFrame.."-"..c.endFrameExclusive,1,c.anchorId)
  end
  local audio=tl:GetItemListInTrack("audio",1)
  assert(#audio==1 and audio[1]:GetStart()==start and audio[1]:GetDuration()==plan.totalFrames,"Audio range mismatch")
  assert(tl:GetEndFrame()-start==plan.totalFrames,"Programme duration mismatch")
  log("timeline",tl:GetName())
  log("frame-count",tl:GetEndFrame()-start)
  log("saved",pm:SaveProject())
  log("project-export",pm:ExportProject(p:GetName(),base.."/urvashi-story-cut-v1.drp",true))
  log("timeline-export",tl:Export(base.."/urvashi-story-cut-v1.drt",resolve.EXPORT_DRT))
  tl:SetCurrentTimecode("00:00:00:00")
end)
log("success",ok)
if not ok then log("error",err) end
f:close()
'''.replace("BASE", lua(str(args.output))).replace("PLAN", lua(manifest))
    (args.output / "assemble-in-resolve.lua").write_text(script)
    print(json.dumps({"output":str(args.output),"cutCount":len(cuts),"totalFrames":total,"timing":args.timing}))


if __name__ == "__main__":
    main()
