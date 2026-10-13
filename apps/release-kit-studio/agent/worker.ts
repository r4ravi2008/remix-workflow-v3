import { loadWorkerConfig } from './config'
import { runWorker } from './production'

const path = process.argv[2]
if (!path) throw new Error('Pass the private worker configuration path.')
console.log(JSON.stringify(await runWorker(await loadWorkerConfig(path))))
