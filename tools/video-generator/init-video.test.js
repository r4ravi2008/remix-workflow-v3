const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {initializeVideoProject, parseArgs} = require('./init-video');

function makeFixture() {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'init-video-repo-'));
  fs.mkdirSync(path.join(repoRoot, '.git'));

  const workspaceRoot = path.join(repoRoot, 'icloud-root');
  const workspaceSlug = 'bella-bella-lofi';
  const workspaceDir = path.join(workspaceRoot, workspaceSlug);
  const templateDir = path.join(repoRoot, 'template');

  fs.mkdirSync(workspaceRoot);
  fs.mkdirSync(workspaceDir, {recursive: true});
  fs.mkdirSync(path.join(templateDir, 'src'), {recursive: true});
  fs.writeFileSync(path.join(templateDir, 'package.json'), '{"name":"fixture-template"}');
  fs.writeFileSync(path.join(templateDir, 'src', 'index.tsx'), 'export {};');
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot}, null, 2)
  );
  fs.writeFileSync(
    path.join(workspaceDir, 'meta.json'),
    JSON.stringify({video_title: 'Bella Bella', genre: 'Lo-Fi'}, null, 2)
  );
  fs.writeFileSync(path.join(workspaceDir, `${workspaceSlug}-remix-v1.mp3`), 'fake mp3');
  fs.writeFileSync(path.join(workspaceDir, 'design.json'), JSON.stringify({layout: {variant: 'cover-art'}}, null, 2));

  return {repoRoot, workspaceSlug, workspaceDir, templateDir};
}

test('uses selected_remix from meta.json for the remix audio source', () => {
  const fixture = makeFixture();
  fs.writeFileSync(
    path.join(fixture.workspaceDir, 'meta.json'),
    JSON.stringify(
      {
        video_title: 'Bella Bella',
        genre: 'Lo-Fi',
        status: {selected_remix: 'v2'},
      },
      null,
      2
    )
  );
  fs.rmSync(path.join(fixture.workspaceDir, `${fixture.workspaceSlug}-remix-v1.mp3`));
  fs.writeFileSync(path.join(fixture.workspaceDir, `${fixture.workspaceSlug}-remix-v2.mp3`), 'fake mp3 v2');

  const executedCommands = [];
  const logs = [];

  initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath: path.join(fixture.workspaceDir, 'design.json'),
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: command => {
      executedCommands.push(command);
      return '245.5';
    },
    logger: {
      log(message) {
        logs.push(message);
      },
      warn(message) {
        logs.push(message);
      },
      error() {},
    },
    processCwd: fixture.repoRoot,
  });

  assert.equal(executedCommands.length, 1);
  assert.match(executedCommands[0], /-remix-v2\.mp3/);
  assert.ok(logs.some(message => message.includes(`${fixture.workspaceSlug}-remix-v2.mp3`) && message.includes('audio.mp3')));
});

test('scaffolds the video project inside the configured workspace root', () => {
  const fixture = makeFixture();

  const result = initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath: path.join(fixture.workspaceDir, 'design.json'),
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: () => '180.25',
    logger: {log() {}, warn() {}, error() {}},
    processCwd: fixture.repoRoot,
  });

  assert.equal(result.videoDir, path.join(fixture.workspaceDir, 'video'));
  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'video-config.json')));
  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'design.json')));
});

test('throws a clear error when the slug workspace does not exist', () => {
  const fixture = makeFixture();

  assert.throws(
    () => initializeVideoProject({
      workspaceSlug: 'missing-slug',
      repoRoot: fixture.repoRoot,
      templateDir: fixture.templateDir,
      execSyncImpl: () => '180.25',
      logger: {log() {}, warn() {}, error() {}},
      processCwd: fixture.repoRoot,
    }),
    /Workspace "missing-slug" not found/
  );
});

test('copies image sequence manifest and stylized frames when provided', () => {
  const fixture = makeFixture();
  const imageSequencePath = path.join(fixture.workspaceDir, 'image-sequence.json');
  const stylizedFramesDir = path.join(fixture.workspaceDir, 'stylized-frames');
  const imageSequenceJson = JSON.stringify(
    {version: 1, frames: [{id: 'frame-001', image_path: 'stylized-frames/bella-bella-lofi-frame-001.jpg'}]},
    null,
    2
  );
  fs.mkdirSync(stylizedFramesDir);
  fs.writeFileSync(imageSequencePath, imageSequenceJson);
  fs.writeFileSync(path.join(stylizedFramesDir, 'bella-bella-lofi-frame-001.jpg'), 'fake jpg');

  const result = initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath: path.join(fixture.workspaceDir, 'design.json'),
    imageSequencePath,
    stylizedFramesDir,
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: () => '180.25',
    logger: {log() {}, warn() {}, error() {}},
    processCwd: fixture.repoRoot,
  });

  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'image-sequence.json')));
  assert.equal(fs.readFileSync(path.join(result.videoDir, 'public', 'image-sequence.json'), 'utf8'), imageSequenceJson);
  assert.equal(
    fs.readFileSync(path.join(result.videoDir, 'public', 'stylized-frames', 'bella-bella-lofi-frame-001.jpg'), 'utf8'),
    'fake jpg'
  );
});

test('parses optional image sequence and stylized frames flags', () => {
  assert.deepEqual(
    parseArgs([
      'slug',
      '--design=/tmp/design.json',
      '--image-sequence=/tmp/image-sequence.json',
      '--stylized-frames=/tmp/stylized-frames',
    ]),
    {
      workspaceSlug: 'slug',
      designPath: '/tmp/design.json',
      imageSequencePath: '/tmp/image-sequence.json',
      stylizedFramesDir: '/tmp/stylized-frames',
    }
  );
});

test('warns and skips optional assets with wrong path types', () => {
  const fixture = makeFixture();
  const designPath = path.join(fixture.workspaceDir, 'design-dir');
  const imageSequencePath = path.join(fixture.workspaceDir, 'image-sequence-dir');
  const stylizedFramesDir = path.join(fixture.workspaceDir, 'stylized-frames-file');
  const warnings = [];

  fs.mkdirSync(designPath);
  fs.mkdirSync(imageSequencePath);
  fs.writeFileSync(stylizedFramesDir, 'not a directory');

  assert.doesNotThrow(() => initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath,
    imageSequencePath,
    stylizedFramesDir,
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: () => '180.25',
    logger: {
      log() {},
      warn(message) {
        warnings.push(message);
      },
      error() {},
    },
    processCwd: fixture.repoRoot,
  }));

  assert.ok(warnings.some(message => message.includes('Design file not found')));
  assert.ok(warnings.some(message => message.includes('Image sequence file not found')));
  assert.ok(warnings.some(message => message.includes('Stylized frames directory not found')));
});

test('short template loads and passes image sequence to vertical layout', () => {
  const templateRoot = path.join(__dirname, 'template', 'src');
  const shortSource = fs.readFileSync(path.join(templateRoot, 'MusicVideoShort.tsx'), 'utf8');
  const verticalSource = fs.readFileSync(path.join(templateRoot, 'layouts', 'CoverArtVerticalLayout.tsx'), 'utf8');

  assert.match(shortSource, /loadImageSequence/);
  assert.match(shortSource, /imageSequence=\{imageSequence\}/);
  assert.match(verticalSource, /imageSequence\?: ImageSequence \| null/);
  assert.match(verticalSource, /activeSequenceFrame/);
  assert.match(verticalSource, /staticFile\(getSafeImageSrc\(activeImageSrc\)\)/);
});
