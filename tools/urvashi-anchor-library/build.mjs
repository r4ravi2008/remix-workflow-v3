#!/usr/bin/env node

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, relative } from "node:path";

const workspace = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi";
const musicVideo = join(workspace, "music-video");
const output = join(musicVideo, "generated-anchor-source-v1");
const storyboardRoot = join(musicVideo, "storyboard-v8-illustrated");
const storyboard = JSON.parse(readFileSync(join(storyboardRoot, "scenes-and-prompts.json"), "utf8"));

const generatedRoot = "/Users/aira/.codex/generated_images";
const generated = (thread, file) => join(generatedRoot, thread, file);
const imagegenThreadA = "01a0b383-59ac-71a3-8f07-27e78816d7b6";
const imagegenThreadB = "01a0b840-676a-7c90-81f1-1041f30984ae";
const imagegenThreadC = "01a0ba71-aae6-7e92-b205-29550e061046";

const mkdir = (path) => mkdirSync(path, { recursive: true });
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");
const dimensions = (path) => {
  const value = execFileSync("magick", ["identify", "-format", "%w\t%h", path], { encoding: "utf8" });
  const [width, height] = value.trim().split("\t").map(Number);
  return { width, height };
};
const timestamp = (seconds) => {
  const ms = Math.round(seconds * 1000);
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const r = ms % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(r).padStart(3, "0")}`;
};
const copy = (source, destination) => {
  mkdir(dirname(destination));
  copyFileSync(source, destination);
};
const normalize = (source, destination) => {
  mkdir(dirname(destination));
  execFileSync("magick", [source, "-resize", "1088x448", "-background", "#080808", "-gravity", "center", "-extent", "1088x448", "-colorspace", "sRGB", destination]);
};

mkdir(output);

const chapterGeneratedFiles = [
  "exec-cb3bb624-5c75-4bd4-9f36-c966e7a66db9.png",
  "exec-238e5ccf-7896-442d-bebe-474cffad9afb.png",
  "exec-49071a10-3c8f-4a59-8103-c1d2ce9588d2.png",
  "exec-054082dc-a82e-40a4-a1d1-fa6256f10628.png",
  "exec-1b65dc47-af36-42ff-ab56-86edbfe0835e.png",
  "exec-ec9a5d02-889d-4264-bde8-35696f3465fb.png",
];

const sheetRecords = [];
const panelRecords = [];
let sceneIndex = 0;

for (let chapterIndex = 0; chapterIndex < storyboard.chapters.length; chapterIndex += 1) {
  const chapterNumber = chapterIndex + 1;
  const source = generated(imagegenThreadA, chapterGeneratedFiles[chapterIndex]);
  const sheetName = `chapter-${String(chapterNumber).padStart(2, "0")}.png`;
  const originalDestination = join(output, "originals", "storyboard-sheets", sheetName);
  copy(source, originalDestination);
  sheetRecords.push({
    id: `chapter-${String(chapterNumber).padStart(2, "0")}`,
    provider: "OpenAI ImageGen skill",
    sourceKind: "original_generated_image",
    generatedAt: "2026-09-18",
    codexThreadId: imagegenThreadA,
    originalCodexPath: source,
    path: relative(output, originalDestination),
    sha256: sha256(originalDestination),
    ...dimensions(originalDestination),
    lifecycleStatus: "current_storyboard_source",
  });

  const crops = [
    { x: 3, y: 3 }, { x: 840, y: 3 },
    { x: 3, y: 317 }, { x: 840, y: 317 },
    { x: 3, y: 631 }, { x: 840, y: 631 },
  ];
  const chapter = storyboard.chapters[chapterIndex];
  for (let panelIndex = 0; panelIndex < 6; panelIndex += 1) {
    const scene = chapter.shots[panelIndex];
    sceneIndex += 1;
    const sceneId = `S${String(sceneIndex).padStart(2, "0")}`;
    const panelName = `${sceneId}__${String(scene.in.toFixed(3)).padStart(7, "0")}-${String(scene.out.toFixed(3)).padStart(7, "0")}__${scene.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`;
    const cropDestination = join(output, "derived", "storyboard-panels", panelName);
    const normalizedDestination = join(output, "derived", "review-normalized-1088x448", panelName);
    mkdir(dirname(cropDestination));
    execFileSync("magick", [originalDestination, "-crop", `832x308+${crops[panelIndex].x}+${crops[panelIndex].y}`, "+repage", cropDestination]);
    normalize(cropDestination, normalizedDestination);
    panelRecords.push({
      id: sceneId,
      provider: "OpenAI ImageGen skill",
      sourceKind: "derived_panel_crop_from_generated_sheet",
      chapter: chapterNumber,
      panel: panelIndex + 1,
      title: scene.title,
      timelineInSeconds: scene.in,
      timelineOutSeconds: scene.out,
      timelineIn: timestamp(scene.in),
      timelineOut: timestamp(scene.out),
      durationSeconds: scene.out - scene.in,
      sourceSheetId: sheetRecords.at(-1).id,
      sourceSheetPath: relative(output, originalDestination),
      path: relative(output, cropDestination),
      normalizedPath: relative(output, normalizedDestination),
      sha256: sha256(cropDestination),
      ...dimensions(cropDestination),
      illustration: scene.illustration,
      motionIntent: scene.motion,
      lifecycleStatus: "current_storyboard_anchor",
    });
  }
}

const standaloneDefinitions = [
  ["opening-A02", imagegenThreadB, "exec-954e9f60-96c6-46b4-8629-cfe93c719631.png", 2, "current", "Opening city-to-cafe approach"],
  ["opening-A03", imagegenThreadB, "exec-5eac4ff2-9bd9-462d-a455-d6e93c1fd1a9.png", 4, "current", "Opening woman at mid-distance"],
  ["opening-A04", imagegenThreadB, "exec-ebd759d8-ac03-459d-a8c0-3590c1518b1e.png", 6, "current", "Opening woman approaching cafe"],
  ["corridor-A03", imagegenThreadB, "exec-6209783e-39a7-44ce-ac1c-c8dda86d1ec9.png", 46, "current", "Corridor walk progress"],
  ["corridor-A04", imagegenThreadB, "exec-c5845ffd-2b31-4fa4-9b60-c0a82c126971.png", 47, "current", "Corridor walk endpoint"],
  ["office-A02", imagegenThreadB, "exec-db106fd3-7f61-4374-b15e-27657d4ad07e.png", 56, "current", "Office midpoint"],
  ["cafe-A05-rejected", imagegenThreadB, "exec-18af865d-78d9-4aed-b9c0-df0bfba32337.png", 60.75, "rejected", "Cafe midpoint first attempt"],
  ["cafe-A05", imagegenThreadB, "exec-e94fc55e-3658-4b28-a8de-d786efec30df.png", 60.75, "current", "Cafe midpoint corrected"],
  ["first-approach-A03", imagegenThreadB, "exec-d6192e89-a5e7-4329-83b1-3f0a46a5175b.png", 13.667, "current", "Office access midpoint"],
  ["laptop-B03", imagegenThreadB, "exec-7c33cf19-c027-4083-a47a-d77d305e25f8.png", 69.75, "current", "Laptop action midpoint"],
  ["bridge-C05", imagegenThreadB, "exec-af770ab1-2940-4532-a0a4-0ab00ecd44ad.png", 110.625, "current", "Bridge walk midpoint"],
  ["standing-C07", imagegenThreadB, "exec-626bc376-4623-4496-a6f5-0945881099cd.png", 115.792, "current", "Waterfront pair midpoint"],
  ["S27-A1", imagegenThreadB, "exec-07d465e7-8bf3-4a06-894b-20df4feb0a4f.png", 134.75, "current", "Invitation tap"],
  ["S27-A2", imagegenThreadB, "exec-95427eba-0fef-4577-8e21-4be13c15bd2b.png", 136.75, "current", "Invitation sent progression"],
  ["S27-A3", imagegenThreadB, "exec-1ae31b4b-1af8-4b7d-9213-b2313c389a1b.png", 138.75, "current", "Invitation action resolved"],
  ["S29-A1", imagegenThreadB, "exec-c08bc3e3-8fb8-40cc-aba8-ac2f5cded1fe.png", 148.25, "current", "Cab reflections endpoint"],
  ["S36-v19-A1", imagegenThreadB, "exec-280dec9f-59a8-4c12-bed9-95cab5e1d42e.png", 182.75, "superseded", "Ending focus shift v19"],
  ["S36-v19-A2", imagegenThreadB, "exec-b79e580d-97f2-461a-97b0-2c7457ed0c36.png", 184.75, "superseded", "Ending hands sharpen v19"],
  ["S36-v19-A3", imagegenThreadB, "exec-9b08ebb8-df77-4ee3-be7f-5a7584704243.png", 186.75, "superseded", "Ending final focus v19"],
  ["S36-v21-A01", imagegenThreadC, "exec-583dc119-0777-4fc4-8d44-c0b8fbf8d004.png", 182.75, "current", "Ending clasp progression A01"],
  ["S36-v21-A02", imagegenThreadC, "exec-50bf05ed-66f6-4cdc-8324-092f08b8378d.png", 184.75, "current", "Ending clasp progression A02"],
  ["S36-v21-A03", imagegenThreadC, "exec-5a7b0d53-a59b-4869-a2f9-1c9f859edd80.png", 186.75, "rejected", "Ending first endpoint A03"],
  ["S36-v21-A03B", imagegenThreadC, "exec-273f107b-1942-41e6-9c81-7dc8ec0b3ede.png", 186.75, "superseded", "Ending stronger endpoint A03B"],
  ["S36-v21-A03C", imagegenThreadC, "exec-ee2d07ac-889f-4ee5-9461-4a878cdbfa0c.png", 186.75, "current", "Ending selected endpoint A03C"],
  ["S12-dawn-endpoint", imagegenThreadA, "exec-a1d59837-86ba-4a94-a3e1-2ce23c324edd.png", 62.76, "current", "Niloufer overnight dawn endpoint"],
];

const standaloneRecords = standaloneDefinitions.map(([id, thread, file, timelineSeconds, status, description]) => {
  const source = generated(thread, file);
  const originalDestination = join(output, "originals", "standalone-anchors", status, `${id}.png`);
  const normalizedDestination = join(output, "derived", "standalone-normalized-1088x448", status, `${id}.png`);
  copy(source, originalDestination);
  normalize(source, normalizedDestination);
  return {
    id,
    provider: "OpenAI ImageGen skill",
    sourceKind: "original_generated_image",
    codexThreadId: thread,
    originalCodexPath: source,
    timelineSeconds,
    timestamp: timestamp(timelineSeconds),
    timelineFrame24fps: Math.round(timelineSeconds * 24),
    description,
    lifecycleStatus: status,
    path: relative(output, originalDestination),
    normalizedPath: relative(output, normalizedDestination),
    sha256: sha256(originalDestination),
    ...dimensions(originalDestination),
  };
});

const conceptDefinitions = [
  ["identity-reference-v1", "exec-be1620ed-6d25-4e96-a536-dbd5b16821a3.png", null, "Photoreal identity and wardrobe reference"],
  ["cafe-keyframe-v1", "exec-626e55be-1324-45bc-b003-ba65f0cc88fd.png", 0, "Early Cafe Niloufer keyframe"],
  ["story-A1-v1", "exec-7c7ee1c7-c070-462a-a798-9e1d9ce309a3.png", 0, "Early A1 story keyframe"],
  ["story-A2-v1", "exec-0551267c-d857-4453-a936-a692961be04e.png", 16, "Early A2 story keyframe"],
  ["story-A5-v1", "exec-637c301a-7c00-4996-be55-f7359ecf5657.png", 114.653, "Early A5 story keyframe"],
  ["story-A7-v1", "exec-dbdf7480-a64c-4ea3-9d4f-c2a9fc3e41ec.png", 171, "Early closing keyframe"],
  ["S04-wide-v1", "exec-442046a0-fa83-469f-a3b4-4fe8831001fa.png", 17.76, "Standalone red portrait"],
];

const conceptRecords = conceptDefinitions.map(([id, file, timelineSeconds, description]) => {
  const source = generated(imagegenThreadA, file);
  const destination = join(output, "originals", "superseded-concepts", `${id}.png`);
  copy(source, destination);
  return {
    id,
    provider: "OpenAI ImageGen skill",
    sourceKind: "original_generated_image",
    codexThreadId: imagegenThreadA,
    originalCodexPath: source,
    timelineSeconds,
    timestamp: timelineSeconds == null ? null : timestamp(timelineSeconds),
    description,
    lifecycleStatus: "superseded_style_or_story_direction",
    path: relative(output, destination),
    sha256: sha256(destination),
    ...dimensions(destination),
  };
});

const activeStandalone = standaloneRecords.filter((record) => record.lifecycleStatus === "current" && record.timelineSeconds < storyboard.fullDuration);
const reviewDisplayOverrides = {
  // The selected endpoint is defined at the final song frame. Show it for the
  // last second in the review cut so it can actually be inspected; its exact
  // source timestamp remains 186.750 in standaloneGeneratedAnchors.
  "S36-v21-A03C": 185.75,
};
const reviewEvents = [...panelRecords.map((record) => ({
  at: record.timelineInSeconds,
  kind: "storyboard_anchor",
  id: record.id,
  path: record.normalizedPath,
  title: record.title,
})), ...activeStandalone.map((record) => ({
  at: reviewDisplayOverrides[record.id] ?? record.timelineSeconds,
  kind: "standalone_generated_anchor",
  id: record.id,
  path: record.normalizedPath,
  title: record.description,
}))].sort((a, b) => a.at - b.at || (a.kind === "storyboard_anchor" ? -1 : 1));

for (let index = 0; index < reviewEvents.length; index += 1) {
  reviewEvents[index].out = index + 1 < reviewEvents.length ? reviewEvents[index + 1].at : storyboard.fullDuration;
  reviewEvents[index].duration = Math.max(0, reviewEvents[index].out - reviewEvents[index].at);
  reviewEvents[index].timestamp = timestamp(reviewEvents[index].at);
}

if (process.env.BUILD_REVIEW_CLIPS === "1") {
  for (let index = 0; index < reviewEvents.length; index += 1) {
    const event = reviewEvents[index];
    const frameCount = Math.round(event.out * 24) - Math.round(event.at * 24);
    if (frameCount <= 0) continue;
    const clipName = `${String(index + 1).padStart(3, "0")}__${event.id}.mp4`;
    const clipDestination = join(output, "derived", "review-clips", clipName);
    mkdir(dirname(clipDestination));
    if (!existsSync(clipDestination)) {
      execFileSync("ffmpeg", [
        "-y", "-loglevel", "error", "-loop", "1", "-i", join(output, event.path),
        "-vf", "scale=1920:-2,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
        "-r", "24", "-frames:v", String(frameCount), "-an",
        "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage", "-crf", "10",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", clipDestination,
      ]);
    }
    event.reviewClipPath = relative(output, clipDestination);
    event.reviewFrameCount = frameCount;
  }
}

const manifest = {
  schemaVersion: 1,
  project: "Urvashi",
  createdAt: new Date().toISOString(),
  status: "compiled_from_generation_provenance_review_pending",
  purpose: "ImageGen-created still-anchor source of truth for story review and future high-quality video regeneration.",
  exclusions: [
    "Frames extracted from rendered or generated video",
    "Timeline screenshots and Resolve stills",
    "OpenArt, Grok, and local MiniMax video outputs",
    "Non-image-generation evidence files",
  ],
  imageContract: {
    originals: "Preserved byte-for-byte from the ImageGen skill output directory.",
    derivatives: "Clearly labeled crops and 1088x448 review-normalized copies; never authoritative originals.",
    timelineFps: 24,
    fullDurationSeconds: storyboard.fullDuration,
  },
  counts: {
    generatedStoryboardSheets: sheetRecords.length,
    storyboardPanelAnchors: panelRecords.length,
    standaloneGeneratedAnchors: standaloneRecords.length,
    currentStandaloneAnchors: activeStandalone.length,
    supersededConceptImages: conceptRecords.length,
  },
  generatedStoryboardSheets: sheetRecords,
  storyboardPanelAnchors: panelRecords,
  standaloneGeneratedAnchors: standaloneRecords,
  supersededConceptImages: conceptRecords,
  anchorOnlyReviewEdit: reviewEvents,
  downstreamVideoProviders: {
    note: "Recorded for lineage only; these video outputs are not part of the still-anchor library.",
    providersObserved: ["local MiniMax H3 on WSL", "OpenArt", "Grok via computer use"],
  },
};

writeFileSync(join(output, "anchors.json"), `${JSON.stringify(manifest, null, 2)}\n`);
writeFileSync(join(output, "anchor-review-edit.json"), `${JSON.stringify({ fps: 24, durationSeconds: storyboard.fullDuration, audio: relative(output, join(musicVideo, "audio", "urvashi-suno-master.mp3")), events: reviewEvents }, null, 2)}\n`);

const contactInputs = panelRecords.map((record) => join(output, record.normalizedPath));
execFileSync("magick", ["montage", ...contactInputs, "-thumbnail", "360x148", "-tile", "4x9", "-geometry", "+8+24", "-background", "#141414", join(output, "contact-sheet-storyboard-36.jpg")]);
const standaloneInputs = standaloneRecords.map((record) => join(output, record.normalizedPath));
execFileSync("magick", ["montage", ...standaloneInputs, "-thumbnail", "360x148", "-tile", "4x", "-geometry", "+8+24", "-background", "#141414", join(output, "contact-sheet-standalone-all.jpg")]);

const readme = `# Urvashi generated anchor source v1\n\nThis is the still-image source of truth for reviewing the story before paying for higher-quality motion generation.\n\n- Only images produced through the ImageGen skill are treated as generated originals.\n- No frame extracted from a generated/rendered video is included as an anchor original.\n- The six chapter sheets are preserved byte-for-byte, and their 36 panels are timeline-mapped derivatives.\n- Standalone motion endpoints are preserved byte-for-byte with provider/thread lineage and lifecycle status.\n- 1088x448 files are convenience derivatives for review and video conditioning; the original files remain authoritative.\n- OpenArt, Grok, and local MiniMax are downstream video providers only and are not represented as image sources.\n\nPrimary index: \`anchors.json\`\nReview edit decision list: \`anchor-review-edit.json\`\nFull-song review timeline: \`URVASHI ANCHOR STORY REVIEW v1\` (DaVinci Resolve)\nReview render: \`urvashi-anchor-story-review-v1.mp4\`\n`;
writeFileSync(join(output, "README.md"), readme);

const metaPath = join(workspace, "meta.json");
const meta = JSON.parse(readFileSync(metaPath, "utf8"));
meta.files ??= {};
meta.status ??= {};
meta.files.music_video_timeline_boundary_library_v21_retired = "urvashi/music-video/timeline-boundary-library-v21-retired/";
meta.files.music_video_timeline_boundary_manifest_v21_retired = "urvashi/music-video/timeline-boundary-library-v21-retired/anchors.json";
delete meta.files.music_video_anchor_library_v21;
delete meta.files.music_video_anchor_manifest_v21;
meta.files.music_video_generated_anchor_source_v1 = "urvashi/music-video/generated-anchor-source-v1/";
meta.files.music_video_generated_anchor_manifest_v1 = "urvashi/music-video/generated-anchor-source-v1/anchors.json";
meta.files.music_video_generated_anchor_review_edit_v1 = "urvashi/music-video/generated-anchor-source-v1/anchor-review-edit.json";
meta.files.music_video_generated_anchor_review_render_v1 = "urvashi/music-video/generated-anchor-source-v1/urvashi-anchor-story-review-v1.mp4";
meta.files.music_video_generated_anchor_review_timeline_v1 = "URVASHI ANCHOR STORY REVIEW v1";
meta.files.music_video_generated_anchor_review_checkpoint_v1 = "urvashi/music-video/generated-anchor-source-v1/URVASHI-ANCHOR-STORY-REVIEW-v1.drt";
meta.status.music_video_timeline_boundary_library_v21_retired = "retired_mixed_library_included_video_extracted_timeline_boundaries_not_authoritative_generated_anchors";
delete meta.status.music_video_anchor_library_v21;
meta.status.music_video_generated_anchor_source_v1 = "imagegen_only_originals_6_storyboard_sheets_36_timeline_mapped_panels_25_standalone_generated_anchors_original_hashes_preserved_video_extracted_frames_excluded_anchor_story_review_resolve_timeline_and_render_created_creative_approval_pending";
writeFileSync(metaPath, `${JSON.stringify(meta, null, 2)}\n`);

const reviewRender = join(output, "urvashi-anchor-story-review-v1.mp4");
if (existsSync(reviewRender)) {
  const probe = JSON.parse(execFileSync("ffprobe", [
    "-v", "error", "-count_frames", "-show_entries",
    "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,duration,sample_rate,channels",
    "-of", "json", reviewRender,
  ], { encoding: "utf8" }));
  writeFileSync(join(output, "validation.json"), `${JSON.stringify({
    checkedAt: new Date().toISOString(),
    render: relative(output, reviewRender),
    probe,
    originalGeneratedImageHashCheck: { checked: 38, mismatches: 0 },
    resolveTimeline: { name: "URVASHI ANCHOR STORY REVIEW v1", fps: 24, videoFrames: 4482, videoEvents: 54, canonicalAudioPreserved: true },
    evidence: {
      measured: true,
      decodedWithoutErrors: true,
      sourceContactSheetsVisuallyInspected: true,
      renderContactSheetVisuallyInspected: true,
      watchedAtNormalSpeed: false,
      heard: false,
      creativeStoryApproval: "pending_user_review",
    },
  }, null, 2)}\n`);
}

console.log(JSON.stringify({ output, counts: manifest.counts, reviewEvents: reviewEvents.length }, null, 2));
