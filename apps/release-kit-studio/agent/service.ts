import { loadWorkerConfig } from './config'
import { supervise } from './supervisor'

const path = process.argv[2]
if (!path) throw new Error('Pass the private worker configuration path.')
await loadWorkerConfig(path)
const controller = new AbortController()
process.once('SIGINT', () => controller.abort())
process.once('SIGTERM', () => controller.abort())
await supervise(path, controller.signal).catch(error => {
  if (!controller.signal.aborted) throw error
})
console.log(JSON.stringify({ state: 'service-stopped', pid: process.pid }))
