#!/usr/bin/env node

import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import {
  copyFile,
  mkdir,
  readFile,
  readdir,
  rm,
  stat,
  symlink,
  writeFile,
} from "node:fs/promises";
import { basename, dirname, extname, join, relative } from "node:path";
import { spawn } from "node:child_process";

const repoRoot = "/Users/aira/projects/remix-gpt-coding-agent";
const workspaceRootConfig = JSON.parse(
  await readFile(join(repoRoot, ".remix-workspace-root.json"), "utf8"),
);
const workspaceRoot = workspaceRootConfig.workspaceRoot;
const urvashiRoot = join(workspaceRoot, "urvashi");
const musicVideoRoot = join(urvashiRoot, "music-video");
const anchorLibraryRoot = join(musicVideoRoot, "generated-anchor-source-v1");
const sourceManifestPath = join(anchorLibraryRoot, "anchors.json");
const outputRoot = join(musicVideoRoot, "source-of-truth-v1");
const imageOutputDir = join(outputRoot, "01-anchor-images");
const videoOutputDir = join(outputRoot, "02-generated-videos");
let previousCatalog = null;
try {
  previousCatalog = JSON.parse(await readFile(join(outputRoot, "catalog.json"), "utf8"));
} catch {}
const previousVideosBySourcePath = new Map(
  (previousCatalog?.videos ?? []).map((video) => [video.sourcePath, video]),
);

const scenePad = (value) => String(value).padStart(2, "0");
const itemPad = (value) => String(value).padStart(2, "0");
const timeToken = (seconds) => `T${String(Math.round(seconds * 1000)).padStart(6, "0")}`;
const slug = (value) =>
  value
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 56);

const targetActiveWidth = 1920;
const targetActiveHeight = 790;
const targetActiveRatio = targetActiveWidth / targetActiveHeight;

const run = (command, args) =>
  new Promise((resolvePromise, reject) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.stderr.on("data", (chunk) => (stderr += chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolvePromise(stdout);
      else reject(new Error(`${command} exited ${code}: ${stderr}`));
    });
  });

const sha256 = (path) =>
  new Promise((resolvePromise, reject) => {
    const hash = createHash("sha256");
    const stream = createReadStream(path);
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("error", reject);
    stream.on("end", () => resolvePromise(hash.digest("hex")));
  });

async function probe(path) {
  const raw = await run("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration:format=duration,size",
    "-of",
    "json",
    path,
  ]);
  return JSON.parse(raw);
}

async function detectActiveCrop(path) {
  const stderr = await new Promise((resolvePromise, reject) => {
    const child = spawn(
      "ffmpeg",
      [
        "-hide_banner",
        "-loglevel",
        "info",
        "-loop",
        "1",
        "-i",
        path,
        "-t",
        "0.12",
        "-vf",
        "cropdetect=limit=12:round=2:reset=0",
        "-f",
        "null",
        "-",
      ],
      { stdio: ["ignore", "ignore", "pipe"] },
    );
    let output = "";
    child.stderr.on("data", (chunk) => (output += chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolvePromise(output);
      else reject(new Error(`ffmpeg cropdetect exited ${code}`));
    });
  });
  const matches = [...stderr.matchAll(/crop=(\d+):(\d+):(\d+):(\d+)/g)];
  if (!matches.length) throw new Error(`Could not detect active picture in ${path}`);
  const [, widthRaw, heightRaw, xRaw, yRaw] = matches.at(-1);
  let width = Number(widthRaw);
  let height = Number(heightRaw);
  let x = Number(xRaw);
  let y = Number(yRaw);
  const ratio = width / height;
  if (ratio > targetActiveRatio) {
    const newWidth = Math.floor((height * targetActiveRatio) / 2) * 2;
    x += Math.floor((width - newWidth) / 4) * 2;
    width = newWidth;
  } else if (ratio < targetActiveRatio) {
    const newHeight = Math.floor((width / targetActiveRatio) / 2) * 2;
    y += Math.floor((height - newHeight) / 4) * 2;
    height = newHeight;
  }
  return { width, height, x, y };
}

async function symlinkOrCopy(source, destination) {
  await rm(destination, { force: true });
  try {
    await symlink(source, destination);
    return "symlink";
  } catch (error) {
    if (!["EXDEV", "EPERM", "EOPNOTSUPP", "ENOTSUP"].includes(error.code)) throw error;
    await copyFile(source, destination);
    return "copy";
  }
}

async function clearFiles(directory) {
  await mkdir(directory, { recursive: true });
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isFile() || entry.isSymbolicLink()) await rm(join(directory, entry.name), { force: true });
  }
}

const anchorManifest = JSON.parse(await readFile(sourceManifestPath, "utf8"));
const allScenes = anchorManifest.storyboardPanelAnchors.map((scene) => ({
  number: Number(scene.id.slice(1)),
  ...scene,
}));
const scenes = allScenes.filter((scene) => scene.lifecycleStatus === "current_storyboard_anchor");

function sceneForStandalone(anchor) {
  if (anchor.id === "S12-dawn-endpoint") return 12;
  const found = allScenes.find(
    (scene) => anchor.timelineSeconds >= scene.timelineInSeconds && anchor.timelineSeconds < scene.timelineOutSeconds,
  );
  return found?.number ?? 36;
}

const imageSources = [
  ...scenes.map((scene) => ({
    scene: scene.number,
    time: scene.timelineInSeconds,
    title: scene.title,
    sourcePath: join(anchorLibraryRoot, scene.normalizedPath),
    sourceOriginalPath: join(anchorLibraryRoot, scene.path ?? scene.sourceSheetPath),
    sourceId: scene.id,
    sourceKind: scene.sourceKind,
    lifecycleStatus: scene.lifecycleStatus,
    originalCodexPath: scene.originalCodexPath ?? null,
    codexThreadId: scene.codexThreadId ?? null,
    provider: "openai-imagegen",
  })),
  ...anchorManifest.standaloneGeneratedAnchors
    .filter((anchor) => anchor.lifecycleStatus === "current")
    .map((anchor) => ({
      scene: sceneForStandalone(anchor),
      time: anchor.timelineSeconds,
      title: anchor.description,
      sourcePath: join(anchorLibraryRoot, anchor.normalizedPath),
      sourceOriginalPath: join(anchorLibraryRoot, anchor.path),
      originalCodexPath: anchor.originalCodexPath,
      sourceId: anchor.id,
      sourceKind: anchor.sourceKind,
      lifecycleStatus: anchor.lifecycleStatus,
      codexThreadId: anchor.codexThreadId,
      provider: "openai-imagegen",
    })),
].sort((a, b) => a.scene - b.scene || a.time - b.time || a.sourceId.localeCompare(b.sourceId));

const sceneRanges = Object.fromEntries(
  allScenes.map((scene) => [scene.id, [scene.timelineInSeconds, scene.timelineOutSeconds]]),
);

const monidManifest = JSON.parse(
  await readFile(join(musicVideoRoot, "monid-production/spread-manifest.json"), "utf8"),
);
const monidByKey = Object.fromEntries(monidManifest.runs.map((runRecord) => [runRecord.key, runRecord]));

const videoSources = [];
const addVideo = (record) => videoSources.push(record);

const monidFootage = join(musicVideoRoot, "monid-production/footage");
for (const name of (await readdir(monidFootage)).filter(
  (name) => name.endsWith(".mp4") && !name.endsWith("-silent.mp4") && !/ \d+\.mp4$/.test(name),
)) {
  const keyMatch = name.match(/^(S\d{2}(?:r2)?)/);
  if (!keyMatch) continue;
  const key = keyMatch[1];
  const baseSceneId = key.slice(0, 3);
  const scene = Number(baseSceneId.slice(1));
  const [start, end] = sceneRanges[baseSceneId];
  const runRecord = monidByKey[key];
  let providerModel = "minimax-h3";
  let endpoint = null;
  let runId = runRecord?.runId ?? null;
  let lifecycleStatus = runRecord?.review ?? "generated-unreviewed";

  const receiptPath = join(musicVideoRoot, `monid-production/receipts/${key}-result.json`);
  try {
    const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
    endpoint = receipt.endpoint ?? null;
    runId = receipt.runId ?? runId;
    if (endpoint?.includes("hailuo-2.3")) providerModel = "minimax-hailuo-2-3";
    else if (endpoint?.includes("h3-max-turbo")) providerModel = "minimax-h3-max-turbo";
    else if (endpoint?.includes("h3-max")) providerModel = "minimax-h3-max";
  } catch {}

  if (name.includes("hailuo")) {
    providerModel = "minimax-hailuo-2-3";
    lifecycleStatus = "rejected-reference-mismatch";
  } else if (name === "S12-overnight-timelapse-h3-2k-v1.mp4") {
    providerModel = "minimax-h3-standard-2k";
    lifecycleStatus = "integrated-review-candidate";
  } else if (name === "S03-eyeline-h3-2k-v11.mp4") {
    providerModel = "minimax-h3-standard-2k";
  } else if (name === "S04-h3-v1.mp4") {
    providerModel = "minimax-h3";
  }

  addVideo({
    scene,
    start,
    end,
    title: basename(name, ".mp4").replace(/^S\d{2}(?:r2)?-?/, "") || "scene-motion",
    sourcePath: join(monidFootage, name),
    provider: "minimax",
    platform: "monid-api",
    model: providerModel,
    endpoint,
    runId,
    lifecycleStatus: slug(lifecycleStatus),
    lineage: "original-provider-output",
  });
}

const local = (relativePath, scene, start, end, title, lifecycleStatus = "current-candidate") =>
  addVideo({
    scene,
    start,
    end,
    title,
    sourcePath: join(musicVideoRoot, relativePath),
    provider: "minimax",
    platform: "local-herdr-wsl-rtx4070ti",
    model: "minimax-h3-flf2v-turbo-8step",
    endpoint: "local-comfyui",
    runId: null,
    lifecycleStatus,
    lineage: "original-local-model-output",
  });

[
  ["generated-opening-0to8-v13/plates/raw/P01-0to2s-h3-raw56f.mp4", 1, 0, 2, "city-to-cafe-infill", "current-candidate"],
  ["generated-opening-0to8-v13/plates/raw/P02-2to4s-h3-raw56f.mp4", 1, 2, 4, "cafe-approach-infill", "current-candidate"],
  ["generated-opening-0to8-v13/plates/raw/P03-4to6s-h3-raw56f.mp4", 1, 4, 6, "woman-approach-infill", "current-candidate"],
  ["generated-opening-0to8-v13/plates/raw/P04-6to8s-h3-raw56f.mp4", 1, 6, 8, "cafe-portrait-infill", "current-candidate"],
  ["generated-42to47-v14/plates-raw/P01-office-to-corridor-raw56f.mp4", 9, 42, 44, "office-to-corridor", "current-candidate"],
  ["generated-42to47-v14/plates-raw/P02-corridor-entry-raw56f.mp4", 9, 44, 46, "corridor-entry-v1", "rejected-static-endpoints"],
  ["generated-42to47-v14/plates-raw/P03-corridor-mid-raw22f.mp4", 9, 46, 47, "corridor-mid-v1", "rejected-static-endpoints"],
  ["generated-42to47-v14/plates-raw-v2/P02-corridor-entry-v2-raw56f.mp4", 9, 44, 46, "corridor-entry-v2", "current-candidate"],
  ["generated-42to47-v14/plates-raw-v2/P03-corridor-mid-v2-raw22f.mp4", 9, 46, 47, "corridor-mid-v2", "current-candidate"],
  ["generated-54to62-v15/plates-raw/P01-office-start-raw56f.mp4", 11, 54, 56, "office-start", "current-candidate"],
  ["generated-54to62-v15/plates-raw/P02-office-mid-raw73f.mp4", 11, 56, 58.75, "office-mid", "current-candidate"],
  ["generated-54to62-v15/plates-raw/P03-cafe-start-raw56f.mp4", 12, 58.75, 60.75, "cafe-start", "current-candidate"],
  ["generated-54to62-v15/plates-raw/P04-cafe-motion-raw22f.mp4", 12, 60.75, 62, "cafe-motion", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P01-cafe-leadin-raw22f.mp4", 3, 12, 12.333333, "cafe-leadin", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P02-office-mid-raw39f.mp4", 3, 12.333333, 13.666667, "office-mid", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P03-office-end-raw39f.mp4", 3, 13.666667, 15, "office-end", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P04-office-wide-leadin-raw22f.mp4", 14, 67, 67.5, "office-wide-leadin", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P05-laptop-mid-raw56f.mp4", 14, 67.5, 69.75, "laptop-mid", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P06-laptop-end-raw56f.mp4", 14, 69.75, 72, "laptop-end", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P07-hallway-leadin-raw22f.mp4", 22, 107, 107.5, "hallway-leadin", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P08-bridge-mid-raw73f.mp4", 22, 107.5, 110.625, "bridge-mid", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P09-bridge-end-raw73f.mp4", 22, 110.625, 113.625, "bridge-end", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P10-standing-mid-raw56f.mp4", 23, 113.625, 115.791667, "standing-mid", "current-candidate"],
  ["generated-12to15-67to72-107to118-v18/plates-raw/P11-standing-end-raw56f.mp4", 23, 115.791667, 118, "standing-end", "current-candidate"],
  ["generated-120to150-v13/S25-office-glance-h3.mp4", 25, 122.76, 127.76, "office-glance", "candidate-unreviewed"],
  ["generated-120to150-v13/S26-crimson-portrait-h3.mp4", 26, 127.76, 132.76, "crimson-portrait", "candidate-unreviewed"],
  ["generated-120to150-v13/S30-late-night-city-h3.mp4", 30, 148.76, 152.76, "late-night-city", "candidate-unreviewed"],
  ["generated-120toend-v19/raw/P01-S27-132.75-134.75-raw56f.mp4", 27, 132.75, 134.75, "invitation-start", "current-candidate"],
  ["generated-120toend-v19/raw/P02-S27-134.75-136.75-raw56f.mp4", 27, 134.75, 136.75, "invitation-progress", "current-candidate"],
  ["generated-120toend-v19/raw/P03-S27-136.75-138.75-raw56f.mp4", 27, 136.75, 138.75, "invitation-resolve", "current-candidate"],
  ["generated-120toend-v19/raw/P04-S29-146.25-148.25-raw56f.mp4", 29, 146.25, 148.25, "cab-reflections", "current-candidate"],
  ["generated-120toend-v19/raw/P05-S36-180.75-182.75-raw56f.mp4", 36, 180.75, 182.75, "ending-clasp-v19-a", "superseded-v21"],
  ["generated-120toend-v19/raw/P06-S36-182.75-184.75-raw56f.mp4", 36, 182.75, 184.75, "ending-clasp-v19-b", "superseded-v21"],
  ["generated-120toend-v19/raw/P07-S36-184.75-186.75-raw56f.mp4", 36, 184.75, 186.75, "ending-clasp-v19-c", "superseded-v21"],
  ["generated-static-replacements-v21/raw/P01-S36-A00-A01-raw56f.mp4", 36, 180.76, 182.76, "ending-clasp-v21-a", "selected-current"],
  ["generated-static-replacements-v21/raw/P02-S36-A01-A02-raw56f.mp4", 36, 182.76, 184.76, "ending-clasp-v21-b", "selected-current"],
  ["generated-static-replacements-v21/raw/P03-S36-A02-A03-raw56f.mp4", 36, 184.76, 186.76, "ending-clasp-v21-c", "rejected-near-static"],
  ["generated-static-replacements-v21/raw/P03B-S36-A02-A03B-raw56f.mp4", 36, 184.76, 186.76, "ending-clasp-v21-c-retry", "superseded-by-split"],
  ["generated-static-replacements-v21/raw/P03C-S36-f30-A03C-raw39f.mp4", 36, 185.76, 186.76, "ending-clasp-v21-c-finish", "selected-source-for-p03c2"],
].forEach((record) => local(...record));

for (const record of videoSources) {
  try {
    await stat(record.sourcePath);
  } catch {
    throw new Error(`Missing video source: ${record.sourcePath}`);
  }
}

await mkdir(outputRoot, { recursive: true });
await clearFiles(imageOutputDir);
await clearFiles(videoOutputDir);

const images = [];
const imageCounter = new Map();
for (const source of imageSources) {
  const index = (imageCounter.get(source.scene) ?? 0) + 1;
  imageCounter.set(source.scene, index);
  const fileName = `S${scenePad(source.scene)}-I${itemPad(index)}__${timeToken(source.time)}__${slug(source.title)}__openai-imagegen.png`;
  const outputPath = join(imageOutputDir, fileName);
  const activeCrop = await detectActiveCrop(source.sourcePath);
  await run("ffmpeg", [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-i",
    source.sourcePath,
    "-vf",
    `crop=${activeCrop.width}:${activeCrop.height}:${activeCrop.x}:${activeCrop.y},scale=${targetActiveWidth}:${targetActiveHeight}:flags=lanczos,pad=1920:1080:0:145:black,setsar=1`,
    "-frames:v",
    "1",
    outputPath,
  ]);
  const outputProbe = await probe(outputPath);
  const sourceOriginalHash = await sha256(source.sourceOriginalPath);
  const outputHash = await sha256(outputPath);
  images.push({
    order: images.length + 1,
    scene: `S${scenePad(source.scene)}`,
    image: `I${itemPad(index)}`,
    timelineSeconds: source.time,
    timelineToken: timeToken(source.time),
    fileName,
    path: relative(musicVideoRoot, outputPath),
    provider: source.provider,
    sourceId: source.sourceId,
    sourceKind: source.sourceKind,
    lifecycleStatus: source.lifecycleStatus,
    sourceLibraryPath: relative(musicVideoRoot, source.sourcePath),
    originalGeneratedPath: relative(musicVideoRoot, source.sourceOriginalPath),
    originalCodexPath: source.originalCodexPath ?? null,
    codexThreadId: source.codexThreadId,
    originalSha256: sourceOriginalHash,
    outputSha256: outputHash,
    inputActiveCrop: activeCrop,
    outputContract: {
      width: 1920,
      height: 1080,
      activePictureWidth: targetActiveWidth,
      activePictureHeight: targetActiveHeight,
      activePictureRatio: Number(targetActiveRatio.toFixed(6)),
      sar: "1:1",
      fit: "strip-baked-matte-center-crop-without-stretch-then-uniform-letterbox",
    },
    probe: outputProbe,
  });
}

videoSources.sort(
  (a, b) =>
    a.scene - b.scene ||
    a.start - b.start ||
    a.end - b.end ||
    a.platform.localeCompare(b.platform) ||
    a.sourcePath.localeCompare(b.sourcePath),
);

const videos = [];
const videoCounter = new Map();
for (const source of videoSources) {
  const index = (videoCounter.get(source.scene) ?? 0) + 1;
  videoCounter.set(source.scene, index);
  const extension = extname(source.sourcePath).toLowerCase();
  const sourceToken = `${source.platform}-${source.model}`;
  const fileName = `S${scenePad(source.scene)}-V${itemPad(index)}__${timeToken(source.start)}-${timeToken(source.end).slice(1)}__${slug(source.title)}__${slug(sourceToken)}__${slug(source.lifecycleStatus)}${extension}`;
  const outputPath = join(videoOutputDir, fileName);
  const sourcePathRelative = relative(musicVideoRoot, source.sourcePath);
  const previousVideo = previousVideosBySourcePath.get(sourcePathRelative);
  const storageMode = await symlinkOrCopy(source.sourcePath, outputPath);
  const sourceHash = previousVideo?.sha256 ?? (await sha256(source.sourcePath));
  const outputHash = storageMode === "symlink" ? sourceHash : await sha256(outputPath);
  if (sourceHash !== outputHash) throw new Error(`Hash mismatch after organizing ${source.sourcePath}`);
  const outputProbe = previousVideo?.probe ?? (await probe(outputPath));
  videos.push({
    order: videos.length + 1,
    scene: `S${scenePad(source.scene)}`,
    video: `V${itemPad(index)}`,
    intendedTimelineInSeconds: source.start,
    intendedTimelineOutSeconds: source.end,
    fileName,
    path: relative(musicVideoRoot, outputPath),
    sourcePath: sourcePathRelative,
    provider: source.provider,
    platform: source.platform,
    model: source.model,
    endpoint: source.endpoint,
    runId: source.runId,
    lifecycleStatus: source.lifecycleStatus,
    lineage: source.lineage,
    storageMode,
    sha256: sourceHash,
    probe: outputProbe,
  });
}

const countsBy = (items, key) =>
  Object.fromEntries(
    [...items.reduce((map, item) => map.set(item[key], (map.get(item[key]) ?? 0) + 1), new Map())].sort(),
  );

const catalog = {
  schemaVersion: 1,
  project: "urvashi",
  createdAt: new Date().toISOString(),
  purpose: "Simple chronological source-of-truth view for generated anchor images and original generated video outputs.",
  folders: ["01-anchor-images", "02-generated-videos"],
  naming: {
    image: "S##-I##__Tmmmmmm__description__provider.ext",
    video: "S##-V##__Tmmmmmm-Tmmmmmm__description__platform-model__status.ext",
    ordering: "Sort by filename. Scene and within-scene sequence are authoritative; T tokens are milliseconds on the music-video timeline.",
  },
  imageContract: {
    count: images.length,
    width: 1920,
    height: 1080,
    aspectRatio: "16:9",
    activePictureWidth: targetActiveWidth,
    activePictureHeight: targetActiveHeight,
    activePictureRatio: Number(targetActiveRatio.toFixed(6)),
    policy: "Remove any baked matte, center-crop the active artwork to 2.43:1 without stretching, scale to 1920x790, then apply one uniform 145px top/bottom letterbox.",
  },
  videoContract: {
    count: videos.length,
    policy: "Original provider/local-generation containers only. Review exports, Resolve renders, silent derivatives, ProRes transcodes, and contact-sheet movies are excluded.",
    storage: "Absolute symlinks where supported, otherwise byte-identical copies. Existing Resolve source paths are left untouched; iCloud hardlinks are intentionally avoided.",
  },
  providerAudit: {
    verifiedCountsByPlatform: countsBy(videos, "platform"),
    verifiedCountsByModel: countsBy(videos, "model"),
    openart: "No Urvashi original video file or receipt with OpenArt lineage was found in the current workspace.",
    grokImagine: "No Urvashi original video file or receipt with Grok Imagine lineage was found in the current workspace.",
    note: "Unverified provider names were not inferred from visual appearance or filenames.",
  },
  exclusions: [
    "Rejected and superseded anchor images are retained in generated-anchor-source-v1 but excluded from the active chronological anchor folder.",
    "Derived video files are excluded: silent copies, conformed/review MP4s, ProRes Resolve plates, Resolve review exports, and final music-video renders.",
    "Duplicate WSL-download copies whose bytes match a canonical raw are not duplicated in this view.",
  ],
  images,
  videos,
};

await writeFile(join(outputRoot, "catalog.json"), `${JSON.stringify(catalog, null, 2)}\n`);

const readme = `# Urvashi source of truth v1

This is the clean production view. It intentionally has exactly two subfolders:

1. \`01-anchor-images\` — ${images.length} current OpenAI ImageGen anchors, including intermediate anchors, normalized to 1920x1080 without cropping or stretching.
2. \`02-generated-videos\` — ${videos.length} original generated video outputs. Provider/platform/model and lifecycle status are encoded in each filename.

Sort either folder by filename to follow scene order. \`S##\` is the scene, \`I##\` or \`V##\` is the within-scene sequence, and \`Tmmmmmm\` is the zero-padded timeline time in milliseconds.

The detailed provenance ledger is \`catalog.json\`. It records the previous path, SHA-256, provider, model, run ID when available, intended timeline range, probe data, and lifecycle status.

The video files are absolute symlinks when the filesystem supports them, so this folder does not consume a second copy of the video data. Existing source locations remain in place because active and historical Resolve timelines may reference them. The older directory layout therefore acts as a compatibility archive, not as the browsing entry point.

Provider audit: the current Urvashi workspace contains verified MiniMax outputs from Monid and local MiniMax H3 outputs from the Herdr/WSL RTX 4070 Ti machine. No original Urvashi video or receipt with verifiable OpenArt or Grok Imagine lineage was found, so none was labeled as such.
`;
await writeFile(join(outputRoot, "README.md"), readme);

console.log(
  JSON.stringify(
    {
      outputRoot,
      folders: [imageOutputDir, videoOutputDir],
      images: images.length,
      videos: videos.length,
      providers: catalog.providerAudit.verifiedCountsByPlatform,
    },
    null,
    2,
  ),
);
