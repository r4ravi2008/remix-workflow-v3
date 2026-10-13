import { Schema } from 'effect'
import { readFile } from 'node:fs/promises'

import { WorkstationConfig, reconcileTransport } from './gpu'

const path = process.argv[2]
if (!path) throw new Error('Pass the private workstation configuration path.')
const config = Schema.decodeUnknownSync(WorkstationConfig)(
  JSON.parse(await readFile(path, 'utf8')),
)
console.log(JSON.stringify(await reconcileTransport(config)))
