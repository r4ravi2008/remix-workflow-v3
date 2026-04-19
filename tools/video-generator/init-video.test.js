const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {initializeVideoProject} = require('./init-video');

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
