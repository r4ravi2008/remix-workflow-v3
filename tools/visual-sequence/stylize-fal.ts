const fs = require('node:fs');
const path = require('node:path');
const {Effect, Console} = require('effect');
const {fal} = require('@fal-ai/client');

const {resolveWorkspaceDir} = require('../shared/workspace-root');

const MODEL_ID = 'fal-ai/nano-banana-pro/edit';
const DEFAULT_CONCURRENCY = 2;
const OUTPUT_EXTENSION = '.jpg';
const MANIFEST_FILE = 'fal-stylized-frames.json';

function parsePositiveInteger(value, name) {
  if (!/^[1-9]\d*$/.test(String(value))) {
    throw new Error(`${name} must be a positive integer.`);
  }
  return Number.parseInt(String(value), 10);
}

function parseStylizeArgs(argv) {
  const [slug, ...rest] = argv;
  if (!slug) {
    throw new Error('Usage: tsx stylize-fal.ts <slug> --prompt-file=<path> [--limit=N] [--frame=frame-001] [--concurrency=N] [--overwrite] [--dry-run]');
  }
  const options = {
    slug,
    promptFile: null,
    limit: null,
    frame: null,
    concurrency: DEFAULT_CONCURRENCY,
    overwrite: false,
    dryRun: false,
  };
  for (const arg of rest) {
    if (arg.startsWith('--prompt-file=')) {
      options.promptFile = arg.replace('--prompt-file=', '');
    } else if (arg.startsWith('--limit=')) {
      options.limit = parsePositiveInteger(arg.replace('--limit=', ''), 'limit');
    } else if (arg.startsWith('--frame=')) {
      options.frame = arg.replace('--frame=', '');
    } else if (arg.startsWith('--concurrency=')) {
      options.concurrency = parsePositiveInteger(arg.replace('--concurrency=', ''), 'concurrency');
    } else if (arg === '--overwrite') {
      options.overwrite = true;
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  if (!options.promptFile) {
    throw new Error('--prompt-file is required.');
  }
  if (options.limit && options.frame) {
    throw new Error('Use either --limit or --frame, not both.');
  }
  return options;
}

function selectFramesForRun(frames, options = {}) {
  if (!Array.isArray(frames)) {
    throw new Error('frames must be an array.');
  }
  if (options.frame) {
    const selected = frames.filter(frame => frame.id === options.frame);
    if (selected.length === 0) {
      throw new Error(`Frame not found: ${options.frame}`);
    }
    return selected;
  }
  if (options.limit) {
    return frames.slice(0, options.limit);
  }
  return frames.slice();
}

function resolveOutputPath({workspaceDir, slug, frameId, extension = OUTPUT_EXTENSION}) {
  return path.join(workspaceDir, 'stylized-frames', `${slug}-${frameId}${extension}`);
}

function planOutputs({slug, workspaceDir, frames, overwrite = false}) {
  const manifestPath = path.join(workspaceDir, 'stylized-frames', MANIFEST_FILE);
  const manifest = fs.existsSync(manifestPath) ? readJson(manifestPath) : {frames: {}};
  return frames.map(frame => {
    const outputPath = resolveOutputPath({workspaceDir, slug, frameId: frame.id});
    const manifestEntry = manifest.frames?.[frame.id];
    const generated = manifestEntry?.output_path === path.relative(workspaceDir, outputPath) && fs.existsSync(outputPath);
    return {
      frame,
      outputPath,
      sourcePath: path.join(workspaceDir, frame.source_image_path),
      status: !overwrite && generated ? 'skip' : 'process',
    };
  });
}

function extractImageUrl(response) {
  if (response?.images?.[0]?.url) return response.images[0].url;
  if (response?.image?.url) return response.image.url;
  if (response?.url) return response.url;
  throw new Error('fal.ai response did not include an image URL.');
}

function createFalClient({apiKey, fetchImpl = fetch}) {
  if (!apiKey) {
    throw new Error('FAL_API_KEY is required.');
  }
  fal.config({credentials: apiKey});
  return {
    async uploadFile(filePath) {
      const blob = new Blob([fs.readFileSync(filePath)], {type: 'image/jpeg'});
      return fal.storage.upload(blob);
    },
    async editImage({imageUrl, prompt}) {
      const result = await fal.subscribe(MODEL_ID, {
        input: {
          prompt,
          image_urls: [imageUrl],
          output_format: 'jpeg',
          aspect_ratio: '16:9',
          num_images: 1,
          resolution: '1K',
          limit_generations: true,
        },
        logs: true,
      });
      return result.data;
    },
    async downloadFile(url, outputPath) {
      const response = await fetchImpl(url);
      if (!response.ok) {
        throw new Error(`fal.ai download failed: ${response.status} ${await response.text()}`);
      }
      fs.mkdirSync(path.dirname(outputPath), {recursive: true});
      const buffer = Buffer.from(await response.arrayBuffer());
      fs.writeFileSync(outputPath, buffer);
    },
  };
}

async function stylizeFrameWithClient({client, prompt, sourcePath, outputPath}) {
  const imageUrl = await client.uploadFile(sourcePath);
  const result = await client.editImage({imageUrl, prompt});
  const outputUrl = extractImageUrl(result);
  await client.downloadFile(outputUrl, outputPath);
  return outputPath;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function updateMetaAfterStylize(metaPath, slug) {
  const meta = readJson(metaPath);
  writeJson(metaPath, {
    ...meta,
    status: {...meta.status, visual_frames_stylized: true},
    files: {...meta.files, image_sequence: meta.files?.image_sequence ?? `${slug}/image-sequence.json`},
  });
}

function updateStylizedManifest({workspaceDir, slug, results}) {
  const stylizedDir = path.join(workspaceDir, 'stylized-frames');
  fs.mkdirSync(stylizedDir, {recursive: true});
  const manifestPath = path.join(stylizedDir, MANIFEST_FILE);
  const current = fs.existsSync(manifestPath) ? readJson(manifestPath) : {version: 1, generator: 'fal-ai/nano-banana-pro/edit', frames: {}};
  const next = {
    ...current,
    version: 1,
    generator: 'fal-ai/nano-banana-pro/edit',
    updated_at: new Date().toISOString(),
    frames: {...current.frames},
  };
  for (const result of results) {
    next.frames[result.frameId] = {
      output_path: path.relative(workspaceDir, result.outputPath),
      slug,
      generated_at: new Date().toISOString(),
    };
  }
  writeJson(manifestPath, next);
}

function retryPromise(factory, attempts = 3) {
  return Effect.promise(async () => {
    let lastError;
    for (let index = 0; index < attempts; index += 1) {
      try {
        return await factory();
      } catch (error) {
        lastError = error;
        if (index < attempts - 1) {
          await new Promise(resolve => setTimeout(resolve, 500 * (index + 1)));
        }
      }
    }
    throw lastError;
  });
}

async function processWithConcurrency(items, concurrency, worker) {
  const results = [];
  let nextIndex = 0;
  async function runWorker() {
    while (nextIndex < items.length) {
      const currentIndex = nextIndex;
      nextIndex += 1;
      try {
        results[currentIndex] = {ok: true, value: await worker(items[currentIndex])};
      } catch (error) {
        results[currentIndex] = {ok: false, error};
      }
    }
  }
  await Promise.all(Array.from({length: Math.min(concurrency, items.length)}, runWorker));
  return results;
}

function runCli(argv = process.argv.slice(2)) {
  return Effect.gen(function* () {
    const options = parseStylizeArgs(argv);
    const {workspaceDir} = resolveWorkspaceDir(options.slug, {repoRoot: path.resolve(__dirname, '../..')});
    const metaPath = path.join(workspaceDir, 'meta.json');
    const selectedFramesPath = path.join(workspaceDir, 'selected-visual-frames.json');
    if (!fs.existsSync(selectedFramesPath)) {
      throw new Error(`Missing selected frames: ${selectedFramesPath}. Run visual-sequence extract first.`);
    }
    if (!fs.existsSync(options.promptFile)) {
      throw new Error(`Missing prompt file: ${options.promptFile}`);
    }
    const prompt = fs.readFileSync(options.promptFile, 'utf8').trim();
    if (!prompt) {
      throw new Error(`Prompt file is empty: ${options.promptFile}`);
    }
    const selectedFrames = readJson(selectedFramesPath);
    const frames = selectFramesForRun(selectedFrames.frames || [], options);
    const plans = planOutputs({slug: options.slug, workspaceDir, frames, overwrite: options.overwrite});
    const toProcess = plans.filter(plan => plan.status === 'process');
    yield* Console.log(`Selected ${frames.length} frame(s): ${frames.map(frame => frame.id).join(', ')}`);
    yield* Console.log(`To process: ${toProcess.length}; skipped: ${plans.length - toProcess.length}`);
    if (options.dryRun) {
      return {processed: 0, skipped: plans.length - toProcess.length, failed: 0};
    }
    const apiKey = process.env.FAL_API_KEY;
    if (!apiKey) {
      throw new Error('FAL_API_KEY is required.');
    }
    const client = createFalClient({apiKey});
    const results = yield* Effect.promise(() => processWithConcurrency(toProcess, options.concurrency, async plan => {
      await Effect.runPromise(
        retryPromise(() => stylizeFrameWithClient({client, prompt, sourcePath: plan.sourcePath, outputPath: plan.outputPath}))
      );
      return plan.outputPath;
    }));
    const failures = results.filter(result => !result.ok);
    results.forEach((result, index) => {
      const frameId = toProcess[index].frame.id;
      if (result.ok) {
        console.log(`Wrote ${frameId}: ${result.value}`);
      } else {
        console.error(`Failed ${frameId}: ${result.error?.message || result.error}`);
      }
    });
    if (failures.length > 0) {
      throw new Error(`${failures.length} frame(s) failed.`);
    }
    updateStylizedManifest({
      workspaceDir,
      slug: options.slug,
      results: results
        .map((result, index) => ({result, plan: toProcess[index]}))
        .filter(item => item.result.ok)
        .map(item => ({frameId: item.plan.frame.id, outputPath: item.plan.outputPath})),
    });
    if (toProcess.length > 0 || plans.some(plan => fs.existsSync(plan.outputPath))) {
      updateMetaAfterStylize(metaPath, options.slug);
    }
    return {processed: toProcess.length, skipped: plans.length - toProcess.length, failed: 0};
  });
}

if (require.main === module) {
  Effect.runPromise(runCli()).catch(error => {
    console.error(error?.message || error);
    process.exit(1);
  });
}

module.exports = {
  parseStylizeArgs,
  selectFramesForRun,
  resolveOutputPath,
  planOutputs,
  createFalClient,
  stylizeFrameWithClient,
  extractImageUrl,
  runCli,
  updateStylizedManifest,
};
