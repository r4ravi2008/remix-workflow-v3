import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { access, readFile, readdir, writeFile } from 'node:fs/promises'
import { dirname, posix, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const directory = dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
if (args.length !== 0 && (args.length !== 2 || args[0] !== '--output')) {
  throw new Error('Use --output <new-file>, or no arguments for the legacy report.')
}
const output = args.length === 2 ? resolve(args[1]) : resolve(directory, 'spec-check.json')
const writeOptions = args.length === 2 ? { flag: 'wx' } : undefined
const root = resolve(directory, '..')
const repositoryRoot = resolve(root, '../../..')
const read = path => readFile(resolve(root, path), 'utf8')
const digest = value => createHash('sha256').update(value).digest('hex')
const ledgerContent = await read('capabilities.json')
const ledger = JSON.parse(ledgerContent)
const manifest = JSON.parse(await read('docs/features/coverage.json'))
const byId = new Map(ledger.capabilities.map(feature => [feature.id, feature]))
assert.equal(byId.size, ledger.capabilities.length, 'Capability IDs must be unique.')

const phases = new Set(['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'])
const areas = new Set()
const visiting = new Set()
const visited = new Set()
const visit = id => {
  assert(!visiting.has(id), `Dependency cycle at ${id}.`)
  if (visited.has(id)) return
  visiting.add(id)
  const feature = byId.get(id)
  assert(feature, `Missing dependency ${id}.`)
  for (const dependency of feature.dependsOn) visit(dependency)
  visiting.delete(id)
  visited.add(id)
}

for (const feature of ledger.capabilities) {
  assert.match(feature.id, /^[A-Z]+-[0-9]{2}$/)
  assert(['Rust', 'Effect', 'Foldkit', 'UI'].includes(feature.owner), `Unknown owner for ${feature.id}.`)
  assert(phases.has(feature.phase), `Unknown phase for ${feature.id}.`)
  assert(['planned', 'implemented', 'verified'].includes(feature.state), `Unknown state for ${feature.id}.`)
  assert(Array.isArray(feature.evidence), `Evidence must be an array for ${feature.id}.`)
  assert(['native', 'application'].includes(feature.layer), `Unknown layer for ${feature.id}.`)
  if (feature.layer === 'native') assert.equal(feature.owner, 'Rust', `Native ownership must be Rust for ${feature.id}.`)
  if (feature.phase === 'P0') assert.equal(feature.layer, 'native', `P0 must be independently native for ${feature.id}.`)
  if (feature.state === 'verified') assert(feature.evidence.length > 0, `Verified state needs evidence for ${feature.id}.`)
  for (const id of feature.dependsOn) {
    const dependency = byId.get(id)
    assert(dependency, `Missing dependency ${id}.`)
    assert(Number(dependency.phase.slice(1)) <= Number(feature.phase.slice(1)),
      `${feature.id} cannot precede dependency ${id}.`)
    if (feature.layer === 'native') assert.equal(dependency.layer, 'native', `${feature.id} cannot require an application adapter.`)
  }
  for (const ids of Object.values(feature.optionalDependencies ?? {})) {
    assert(Array.isArray(ids), `Optional dependencies must be arrays for ${feature.id}.`)
    for (const id of ids) assert(byId.has(id), `Unknown optional dependency ${id} for ${feature.id}.`)
  }
  for (const key of ['name', 'module', 'command', 'acceptance', 'source']) {
    assert.equal(typeof feature[key], 'string')
    assert(feature[key].length > 0, `${feature.id} requires ${key}.`)
  }
  assert.equal(feature.behaviorContract, `docs/features/${manifest.features[feature.id]}`,
    `Detailed contract must match the assigned document for ${feature.id}.`)
  await access(resolve(root, feature.behaviorContract))
  if (feature.sourceKind === 'owned-specification') {
    await access(resolve(root, feature.source))
  } else {
    assert.equal(feature.sourceKind, 'capability-family-reference')
    assert(new URL(feature.source).protocol === 'https:', `Invalid source for ${feature.id}.`)
  }
  areas.add(feature.area)
  visit(feature.id)
}

assert.equal(ledger.capabilities.length, 81)
assert.equal(areas.size, 11)
const required = ['AGENTS.md', 'README.md', 'docs/SPEC.md', 'docs/ARCHITECTURE.md',
  'docs/IMPLEMENTATION.md', 'docs/WORKFLOW.md', 'docs/PROGRESS.md', 'docs/TASKS.md',
  'docs/HISTORY.md', 'docs/decisions.tsv', 'docs/check-spec.mjs', 'docs/LAYERS.md', 'docs/CLI-EXAMPLES.md',
  'docs/FEATURES.md', 'docs/GUARDRAILS.md', 'docs/VERIFICATION.md', 'docs/SCRIPTING.md',
  'docs/WRITING.md', 'docs/INTENT-VERIFICATION.md', 'docs/archive/2026-10-05/manifest.json',
  'docs/features/coverage.json', 'docs/features/check.mjs', 'docs/features/intent-contracts.json',
  ...new Set(Object.values(manifest.features).map(path => `docs/features/${path}`)),
  'examples/project.json', 'examples/put-clip.json', 'examples/frame.json', 'examples/inspect.json']
const hashes = { 'capabilities.json': digest(ledgerContent) }
for (const path of required) {
  const content = await read(path)
  assert(content.trim().length > 0, `Empty document ${path}.`)
  hashes[path] = digest(content)
  if (!path.endsWith('.md')) continue
  for (const match of content.matchAll(/\]\(([^)]+)\)/g)) {
    const target = match[1]
    if (/^[a-z]+:/.test(target) || target.startsWith('#')) continue
    const linked = resolve(dirname(resolve(root, path)), target.split('#')[0])
    await access(linked)
  }
}

const isSafeRepositoryPath = value => typeof value === 'string' && value.length > 0 &&
  !value.startsWith('/') && !value.includes('\\') && posix.normalize(value) === value &&
  value.split('/').every(part => part.length > 0 && part !== '.' && part !== '..')
const archiveManifestPath = 'docs/archive/2026-10-05/manifest.json'
const archiveManifestRepositoryPath = 'apps/release-kit-studio/native-editor/docs/archive/2026-10-05/manifest.json'
const archiveManifest = JSON.parse(await read(archiveManifestPath))
assert.equal(archiveManifest.schemaVersion, 1, 'Archive manifest schema must be 1.')
assert.equal(archiveManifest.originalLinksUseOriginalPaths, true,
  'Archive links must preserve original recorded paths.')
assert(Array.isArray(archiveManifest.entries), 'Archive manifest entries must be an array.')
assert(archiveManifest.entries.length > 0, 'Archive manifest must list at least one payload file.')
const archiveRoot = resolve(repositoryRoot, 'apps/release-kit-studio/native-editor/docs/archive/2026-10-05')
const archivePayloads = new Set()
const inspectArchive = async directory => {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name)
    assert(!entry.isSymbolicLink(), `Symlink in the native archive: ${path}.`)
    if (entry.isDirectory()) {
      await inspectArchive(path)
    } else {
      assert(entry.isFile(), `Non-regular native archive entry: ${path}.`)
      const archivePath = relative(repositoryRoot, path).split(sep).join('/')
      if (archivePath !== archiveManifestRepositoryPath) archivePayloads.add(archivePath)
    }
  }
}
await inspectArchive(archiveRoot)
const assertExactArchiveMembership = (entries, payloads) => {
  assert(entries.length > 0, 'Archive manifest must list at least one payload file.')
  const originalPaths = new Set()
  const archivePaths = new Set()
  for (const [index, entry] of entries.entries()) {
    assert(entry && typeof entry === 'object', `Archive entry ${index} must be an object.`)
    assert.equal(typeof entry.originalPath, 'string', `Archive entry ${index} requires originalPath.`)
    assert.equal(typeof entry.archivePath, 'string', `Archive entry ${index} requires archivePath.`)
    assert(!originalPaths.has(entry.originalPath), `Duplicate archive original path ${entry.originalPath}.`)
    assert(!archivePaths.has(entry.archivePath), `Duplicate archive path ${entry.archivePath}.`)
    originalPaths.add(entry.originalPath)
    archivePaths.add(entry.archivePath)
    assert(payloads.has(entry.archivePath), `Archive manifest omits payload ${entry.archivePath}.`)
  }
  assert.equal(archivePaths.size, payloads.size, 'Archive manifest payload membership must be exact.')
  for (const archivePath of payloads) {
    assert(archivePaths.has(archivePath), `Unlisted native archive payload ${archivePath}.`)
  }
}
assertExactArchiveMembership(archiveManifest.entries, archivePayloads)
assert.throws(() => assertExactArchiveMembership([], archivePayloads), /at least one payload/)
assert.throws(() => assertExactArchiveMembership(archiveManifest.entries.slice(0, -1), archivePayloads), /membership|omits/)
assert.throws(() => assertExactArchiveMembership(
  [...archiveManifest.entries, { ...archiveManifest.entries[0] }], archivePayloads), /Duplicate/)
assert.throws(() => assertExactArchiveMembership(
  archiveManifest.entries.map((entry, index) => index === 0
    ? { ...entry, archivePath: `${entry.archivePath}.unlisted` }
    : entry), archivePayloads), /omits|membership/)
const originalPaths = new Set()
const archivePaths = new Set()
for (const [index, entry] of archiveManifest.entries.entries()) {
  assert(entry && typeof entry === 'object', `Archive entry ${index} must be an object.`)
  for (const key of ['originalPath', 'archivePath', 'action', 'reason', 'sha256', 'bytes', 'archivedOn']) {
    assert.equal(typeof entry[key], key === 'bytes' ? 'number' : 'string',
      `Archive entry ${index} requires ${key}.`)
  }
  assert(isSafeRepositoryPath(entry.originalPath), `Unsafe archive original path ${entry.originalPath}.`)
  assert(isSafeRepositoryPath(entry.archivePath), `Unsafe archive path ${entry.archivePath}.`)
  assert(entry.originalPath.startsWith('apps/release-kit-studio/native-editor/'),
    `Archive original path must stay in native-editor: ${entry.originalPath}.`)
  assert(entry.archivePath.startsWith('apps/release-kit-studio/native-editor/docs/archive/2026-10-05/'),
    `Archive path must stay in the versioned native archive: ${entry.archivePath}.`)
  assert(!originalPaths.has(entry.originalPath), `Duplicate archive original path ${entry.originalPath}.`)
  assert(!archivePaths.has(entry.archivePath), `Duplicate archive path ${entry.archivePath}.`)
  originalPaths.add(entry.originalPath)
  archivePaths.add(entry.archivePath)
  assert(archivePayloads.has(entry.archivePath), `Archive manifest omits payload ${entry.archivePath}.`)
  const archivedPath = resolve(repositoryRoot, entry.archivePath)
  const archivedContent = await readFile(archivedPath)
  assert.equal(archivedContent.byteLength, entry.bytes, `Archive byte count mismatch for ${entry.archivePath}.`)
  assert.equal(digest(archivedContent), entry.sha256, `Archive SHA-256 mismatch for ${entry.archivePath}.`)
}
assert.equal(archivePaths.size, archivePayloads.size, 'Archive manifest payload membership must be exact.')
for (const archivePath of archivePayloads) {
  assert(archivePaths.has(archivePath), `Unlisted native archive payload ${archivePath}.`)
}

const specification = await read('docs/SPEC.md')
for (const feature of ledger.capabilities) {
  assert(Array.isArray(feature.acceptanceCaseIds))
  assert(feature.acceptanceCaseIds.length > 0, `Missing acceptance cases for ${feature.id}.`)
  const contract = await read(feature.behaviorContract)
  for (const id of feature.acceptanceCaseIds) {
    if (feature.phase === 'P0') assert(specification.includes(`| ${id} |`), `Missing P0 acceptance case ${id}.`)
    assert(new RegExp(`${id}\\b`).test(contract), `Missing detailed acceptance case ${id}.`)
  }
}
assert(specification.includes('independently usable Rust library and direct Rust agent CLI'))
assert(specification.includes('FFmpeg executables, libav dependencies'))
assert(specification.includes('Effect and UI adapters are separate future applications'))
const appPackage = JSON.parse(await readFile(resolve(root, '../package.json'), 'utf8'))
assert.equal(appPackage.scripts['editor:local'], 'bun agent/editor-local.mjs serve')
assert.equal(appPackage.scripts['editor:local:setup'], 'bun agent/editor-local.mjs setup')
assert.equal(appPackage.scripts.native, undefined)
const ignored = new Set(['target', '.state', '.runs', '.git'])
const inspect = async directory => {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && ignored.has(entry.name)) continue
    const path = resolve(directory, entry.name)
    assert(!entry.isSymbolicLink(), `Symlink outside the owned source tree: ${path}.`)
    if (entry.isDirectory()) {
      await inspect(path)
    } else if (entry.isFile()) {
      const owned = relative(root, path)
      if (owned.startsWith('crates/')) assert(!/\.(?:[cm]?jsx?|tsx?|py)$/.test(owned), `Non-Rust runtime source: ${owned}.`)
      if (owned.endsWith('.rs') || owned.endsWith('Cargo.toml') || owned === 'Cargo.lock') {
        hashes[owned] = digest(await readFile(path))
      }
    }
  }
}
await inspect(root)
let nativeSourcePresent = false
try { await access(resolve(root, 'Cargo.toml')); nativeSourcePresent = true } catch {}

const receipt = {
  kind: 'specification-check',
  checkedAt: new Date().toISOString(),
  verdict: 'VERIFIED',
  scope: 'Document structure, ownership metadata, source inventory, and local links only. Runtime behavior is not checked.',
  capabilities: ledger.capabilities.length,
  areas: [...areas],
  checks: ['unique feature IDs', 'valid owners and phases', 'no dependency cycles', 'dependencies precede dependent phases',
    'native features have only native dependencies', 'P0 is Rust-only', 'required documents present',
    'local document links resolve', 'feature contracts match assignments', 'acceptance cases are defined',
    'optional dependency targets exist', 'historical package entries unchanged', 'no JavaScript or Python source in native crates'],
  nativeSourcePresent,
  runtimeChecked: false,
  runtimeVerified: false,
  cloudDeployed: false,
  creativelyAccepted: false,
  hashes,
}
await writeFile(output, JSON.stringify(receipt, null, 2) + '\n', writeOptions)
process.stdout.write(JSON.stringify(receipt, null, 2) + '\n')
