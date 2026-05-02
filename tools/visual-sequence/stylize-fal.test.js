const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  parseStylizeArgs,
  selectFramesForRun,
  planOutputs,
  stylizeFrameWithClient,
} = require('./stylize-fal.ts');

const frames = [
  {id: 'frame-001', source_image_path: 'source-frames/song-frame-001.jpg'},
  {id: 'frame-002', source_image_path: 'source-frames/song-frame-002.jpg'},
];

test('parseStylizeArgs parses slug prompt and limit', () => {
  const result = parseStylizeArgs(['song-slug', '--prompt-file=prompt.txt', '--limit=1']);
  assert.equal(result.slug, 'song-slug');
  assert.equal(result.promptFile, 'prompt.txt');
  assert.equal(result.limit, 1);
});

test('selectFramesForRun supports limit', () => {
  assert.deepEqual(selectFramesForRun(frames, {limit: 1}).map(frame => frame.id), ['frame-001']);
});

test('selectFramesForRun supports specific frame', () => {
  assert.deepEqual(selectFramesForRun(frames, {frame: 'frame-002'}).map(frame => frame.id), ['frame-002']);
});

test('planOutputs skips existing outputs unless overwrite is true', () => {
  const workspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stylize-fal-'));
  fs.mkdirSync(path.join(workspaceDir, 'stylized-frames'), {recursive: true});
  fs.writeFileSync(path.join(workspaceDir, 'stylized-frames', 'song-slug-frame-001.jpg'), 'exists');
  const skipped = planOutputs({slug: 'song-slug', workspaceDir, frames, overwrite: false});
  assert.equal(skipped[0].status, 'process');
  assert.equal(skipped[1].status, 'process');
  fs.writeFileSync(
    path.join(workspaceDir, 'stylized-frames', 'fal-stylized-frames.json'),
    JSON.stringify({version: 1, frames: {'frame-001': {output_path: 'stylized-frames/song-slug-frame-001.jpg'}}})
  );
  const generated = planOutputs({slug: 'song-slug', workspaceDir, frames, overwrite: false});
  assert.equal(generated[0].status, 'skip');
  const overwritten = planOutputs({slug: 'song-slug', workspaceDir, frames, overwrite: true});
  assert.equal(overwritten[0].status, 'process');
});

test('stylizeFrameWithClient writes downloaded fal output', async () => {
  const workspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stylize-fal-client-'));
  const sourcePath = path.join(workspaceDir, 'source.jpg');
  const outputPath = path.join(workspaceDir, 'out', 'output.jpg');
  fs.writeFileSync(sourcePath, 'source');
  const client = {
    uploadFile: async () => 'https://example.test/input.jpg',
    editImage: async () => ({url: 'https://example.test/output.jpg'}),
    downloadFile: async (_url, target) => {
      fs.mkdirSync(path.dirname(target), {recursive: true});
      fs.writeFileSync(target, 'fake-image');
    },
  };
  await stylizeFrameWithClient({client, prompt: 'prompt', sourcePath, outputPath});
  assert.equal(fs.readFileSync(outputPath, 'utf8'), 'fake-image');
});
