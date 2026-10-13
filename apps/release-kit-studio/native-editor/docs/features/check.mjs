import { readFile, writeFile, access } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'

const directory = dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
if (args.length !== 0 && (args.length !== 2 || args[0] !== '--output')) {
  throw new Error('Use --output <new-file>, or no arguments for the legacy report.')
}
const output = args.length === 2 ? resolve(args[1]) : resolve(directory, 'coverage-check.json')
const writeOptions = args.length === 2 ? { flag: 'wx' } : undefined
const root = resolve(directory, '../..')
const digest = value => createHash('sha256').update(value).digest('hex')
const manifestBytes = await readFile(resolve(directory, 'coverage.json'))
const ledgerBytes = await readFile(resolve(root, 'capabilities.json'))
const manifest = JSON.parse(manifestBytes)
const ledger = JSON.parse(ledgerBytes)
const expected = new Map(ledger.capabilities.map(feature => [feature.id, feature]))
const issues = []
const observed = new Map()
const files = {}

if (Object.keys(manifest.features).length !== expected.size) issues.push('Coverage manifest does not match the capability count.')
for (const id of expected.keys()) if (!manifest.features[id]) issues.push(`Missing assignment for ${id}.`)
for (const id of Object.keys(manifest.features)) if (!expected.has(id)) issues.push(`Unknown assigned feature ${id}.`)

for (const file of new Set(Object.values(manifest.features))) {
  const path = resolve(directory, file)
  let content
  try { content = await readFile(path, 'utf8') } catch { issues.push(`Missing document ${file}.`); continue }
  files[file] = digest(content)
  const sections = [...content.matchAll(/^## ([A-Z]+-[0-9]{2})\. ([^\n]+)$/gm)]
  for (let index = 0; index < sections.length; index++) {
    const [heading, id, name] = sections[index]
    const body = content.slice(sections[index].index + heading.length, sections[index + 1]?.index ?? content.length)
    if (observed.has(id)) issues.push(`Duplicate feature section ${id}.`)
    observed.set(id, file)
    const feature = expected.get(id)
    if (!feature) { issues.push(`Unknown feature section ${id}.`); continue }
    if (manifest.features[id] !== file) issues.push(`Wrong owner document for ${id}.`)
    if (feature.behaviorContract !== `docs/features/${file}`) issues.push(`Ledger contract differs from assignment for ${id}.`)
    if (name.trim() !== feature.name) issues.push(`Feature title differs from ledger for ${id}.`)
    for (const heading of manifest.requiredSections) {
      const marker = `### ${heading}\n`
      if (!body.includes(marker)) { issues.push(`${id} lacks ${heading}.`); continue }
      const text = body.split(marker)[1].split(/^### /m)[0].trim()
      if (text.length < 50) issues.push(`${id} has an empty or insufficient ${heading}.`)
    }
    const pieces = new Set([...body.matchAll(new RegExp(`${id}\\.([1-9][0-9]*)`, 'g'))].map(match => match[1]))
    const cases = new Set([...body.matchAll(new RegExp(`${id}-([A-Z])\\b`, 'g'))].map(match => match[1]))
    if (pieces.size < 3) issues.push(`${id} needs at least three implementation pieces.`)
    if (cases.size < 2) issues.push(`${id} needs at least two named verification cases.`)
    if (feature.phase !== 'P0') {
      const expectedCases = [...cases].map(suffix => `${id}-${suffix}`).sort()
      if (JSON.stringify([...feature.acceptanceCaseIds].sort()) !== JSON.stringify(expectedCases)) {
        issues.push(`Ledger acceptance cases differ from detail cases for ${id}.`)
      }
    }
    if (!body.includes(feature.phase)) issues.push(`${id} omits its phase.`)
    if (!body.includes(feature.owner)) issues.push(`${id} omits its implementation owner.`)
    if (!body.includes(feature.command)) issues.push(`${id} omits its command boundary.`)
  }
  for (const link of content.matchAll(/\]\(([^)]+)\)/g)) {
    const target = link[1]
    if (/^[a-z]+:/.test(target) || target.startsWith('#')) continue
    try { await access(resolve(dirname(path), target.split('#')[0])) } catch { issues.push(`Unresolved link ${target} in ${file}.`) }
  }
}

for (const id of expected.keys()) if (!observed.has(id)) issues.push(`Feature details missing for ${id}.`)
const indexContent = await readFile(resolve(root, 'docs/FEATURES.md'), 'utf8')
files['../FEATURES.md'] = digest(indexContent)
const anchors = text => new Set([...text.matchAll(/^#{1,6} (.+)$/gm)].map(match =>
  match[1].toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s/g, '-')))
for (const link of indexContent.matchAll(/\]\(([^)]+)\)/g)) {
  const target = link[1]
  if (/^[a-z]+:/.test(target)) continue
  const [file, anchor] = target.split('#')
  try {
    const linkedContent = file ? await readFile(resolve(root, 'docs', file), 'utf8') : indexContent
    if (anchor && !anchors(linkedContent).has(anchor)) issues.push(`Unresolved feature index anchor ${target}.`)
  } catch { issues.push(`Unresolved feature index link ${target}.`) }
}
for (const id of expected.keys()) {
  if (!indexContent.includes(`[${id}](`)) issues.push(`Feature index omits ${id}.`)
}
const result = {
  kind: 'feature-document-coverage',
  checkedAt: new Date().toISOString(),
  verdict: issues.length === 0 ? 'VERIFIED' : 'NOT VERIFIED',
  scope: '81-family document coverage and structure only. Semantics require review; no editor runtime capability is promoted.',
  expectedFeatures: expected.size,
  observedFeatures: observed.size,
  documentCount: new Set(Object.values(manifest.features)).size,
  hashes: { 'coverage.json': digest(manifestBytes), 'capabilities.json': digest(ledgerBytes), ...files },
  issues,
}
await writeFile(output, JSON.stringify(result, null, 2) + '\n', writeOptions)
process.stdout.write(JSON.stringify({ verdict: result.verdict, expected: result.expectedFeatures, observed: result.observedFeatures, documents: result.documentCount, issues }, null, 2) + '\n')
if (issues.length > 0) process.exitCode = 1
