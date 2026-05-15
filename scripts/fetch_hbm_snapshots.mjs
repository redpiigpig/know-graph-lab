#!/usr/bin/env node
/**
 * Download all world_*.geojson from aourednik/historical-basemaps into C:/tmp/hbm-sample/.
 * Skips files that already exist.
 */
import { existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const HBM_DIR = 'C:\\tmp\\hbm-sample'
if (!existsSync(HBM_DIR)) mkdirSync(HBM_DIR, { recursive: true })

const API = 'https://api.github.com/repos/aourednik/historical-basemaps/contents/geojson'
const RAW_BASE = 'https://raw.githubusercontent.com/aourednik/historical-basemaps/master/geojson/'

console.log('Listing files via GitHub API…')
const list = await fetch(API).then(r => r.json())
const worlds = list.filter(f => /^world_.*\.geojson$/.test(f.name)).map(f => f.name)
console.log(`Found ${worlds.length} world_*.geojson on remote`)

let downloaded = 0, skipped = 0
for (const name of worlds) {
  const dst = join(HBM_DIR, name)
  if (existsSync(dst)) { skipped++; continue }
  const url = RAW_BASE + name
  process.stdout.write(`  ${name} ... `)
  try {
    const r = await fetch(url)
    if (!r.ok) { console.log(`FAIL ${r.status}`); continue }
    const buf = Buffer.from(await r.arrayBuffer())
    writeFileSync(dst, buf)
    console.log(`${(buf.length / 1024).toFixed(0)} KB`)
    downloaded++
  } catch (e) {
    console.log('ERR', e.message)
  }
}
console.log(`Done — downloaded ${downloaded}, already had ${skipped}`)
