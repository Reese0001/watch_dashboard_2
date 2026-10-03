const fs = require('fs')
const path = require('path')
const os = require('os')
const crypto = require('crypto')
const { VvdManager } = require('@aiot-toolkit/emulator/lib')
const {
  getRunningAvdConfigByName
} = require('@aiot-toolkit/emulator/lib/emulatorutil/running')
const {
  createGrpcClient
} = require('@aiot-toolkit/emulator/lib/vvd/grpc')

const PACKAGE_NAME = 'com.application.watch.dashboard'
const RPK_PATH = path.resolve('dist/com.application.watch.dashboard.debug.1.0.2.rpk')
const devices = {
  xiaomi_s4: { fromX: 400, toX: 66, y: 230, pages: 3 },
  xiaomi_band_pro: { fromX: 292, toX: 44, y: 240, pages: 4 }
}

const wait = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds))
const digest = buffer => crypto.createHash('sha256').update(buffer).digest('hex')
const isRenderedFrame = buffer => buffer && buffer.length > 5000

async function startApp(deviceName) {
  const manager = new VvdManager({ sdkHome: path.join(os.homedir(), '.vela', 'sdk') })
  const { emulatorInstance } = await manager.startVvd({ vvdName: deviceName })
  await emulatorInstance.startApp(PACKAGE_NAME)
}

async function installLatestBuild(deviceName) {
  if (!fs.existsSync(RPK_PATH)) throw new Error(`RPK not found: ${RPK_PATH}`)
  const manager = new VvdManager({ sdkHome: path.join(os.homedir(), '.vela', 'sdk') })
  const { emulatorInstance } = await manager.startVvd({ vvdName: deviceName })
  const remotePath = await emulatorInstance.pushRpk(RPK_PATH, PACKAGE_NAME)
  await emulatorInstance.install(remotePath, { packageName: PACKAGE_NAME })
}

async function waitForRenderedFrame(client, deviceName) {
  let lastFrame
  for (let attempt = 1; attempt <= 4; attempt += 1) {
    await startApp(deviceName)
    await wait(attempt === 1 ? 3400 : 2600)
    lastFrame = await client.getScreenshot()
    if (isRenderedFrame(lastFrame)) return lastFrame
  }
  throw new Error(`Simulator stayed blank after retries (${lastFrame ? lastFrame.length : 0} bytes)`)
}

async function swipeLeft(client, geometry) {
  const steps = 14
  for (let index = 0; index <= steps; index += 1) {
    const x = geometry.fromX + ((geometry.toX - geometry.fromX) * index / steps)
    client.sendMouse({ x, y: geometry.y, buttons: 1 })
    await wait(18)
  }
  client.sendMouse({ x: geometry.toX, y: geometry.y, buttons: 0 })
  await wait(780)
}

async function captureDevice(deviceName, outputRoot) {
  const geometry = devices[deviceName]
  if (!geometry) throw new Error(`Unknown device: ${deviceName}`)

  if (process.env.SKIP_INSTALL !== '1') await installLatestBuild(deviceName)

  const config = getRunningAvdConfigByName(deviceName)
  if (!config) throw new Error(`Simulator is not running: ${deviceName}`)

  const outputDirectory = path.resolve(outputRoot, deviceName)
  fs.mkdirSync(outputDirectory, { recursive: true })

  const client = createGrpcClient(config)
  await client.waitForReady()
  let frame = await waitForRenderedFrame(client, deviceName)
  const pages = []

  for (let page = 1; page <= geometry.pages; page += 1) {
    const pagePath = path.join(outputDirectory, `page-${page}.png`)
    fs.writeFileSync(pagePath, frame)
    const frameHash = digest(frame)
    pages.push({ page, bytes: frame.length, sha256: frameHash, path: pagePath })

    if (page < geometry.pages) {
      let nextFrame
      let changed = false
      for (let attempt = 0; attempt < 3 && !changed; attempt += 1) {
        await swipeLeft(client, geometry)
        nextFrame = await client.getScreenshot()
        changed = isRenderedFrame(nextFrame) && digest(nextFrame) !== frameHash
      }
      if (!changed) throw new Error(`Page ${page} did not advance on ${deviceName}`)
      frame = nextFrame
    }
  }

  client.close()
  const reportPath = path.join(outputDirectory, 'report.json')
  fs.writeFileSync(reportPath, JSON.stringify({ deviceName, pages }, null, 2))
  return { deviceName, reportPath, pages }
}

async function main() {
  const requested = process.argv[2] || 'all'
  const outputRoot = process.argv[3] || 'build/visual-regression'
  const names = requested === 'all' ? Object.keys(devices) : [requested]
  const reports = []
  for (const name of names) reports.push(await captureDevice(name, outputRoot))
  console.log(JSON.stringify(reports, null, 2))
}

main().catch(error => {
  console.error(error.stack || error.message || error)
  process.exit(1)
})
