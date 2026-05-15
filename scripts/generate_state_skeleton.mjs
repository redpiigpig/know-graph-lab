#!/usr/bin/env node
/**
 * 從 historical-states.geojson + historical-sphere-fills.geojson 抽出
 * 每個獨特國家／文明的骨架資料：
 *   - name_en
 *   - earliest_from / latest_to（跨多 snapshot 合併）
 *   - modern_countries[]（從 sphere-fills 統計）
 *   - snapshots[]（出現於哪些年份）
 *
 * 輸出：public/maps/state-skeleton.json
 */

import { readFileSync, writeFileSync } from 'node:fs'

const STATES_FILE = 'public/maps/historical-states.geojson'
const FILLS_FILE = 'public/maps/historical-sphere-fills.geojson'
const OUT_FILE = 'public/maps/state-skeleton.json'

const states = JSON.parse(readFileSync(STATES_FILE, 'utf8'))
const fills = JSON.parse(readFileSync(FILLS_FILE, 'utf8'))

const byName = new Map()

// 從 states 抽 name + year ranges + snapshots
for (const f of states.features) {
  const name = f.properties.name
  const yf = f.properties.year_from
  const yt = f.properties.year_to
  if (!name) continue
  if (!byName.has(name)) {
    byName.set(name, {
      name_en: name,
      earliest_from: yf,
      latest_to: yt,
      modern_countries: new Set(),
      snapshots: new Set(),
    })
  }
  const e = byName.get(name)
  e.earliest_from = Math.min(e.earliest_from, yf)
  e.latest_to = Math.max(e.latest_to, yt)
  e.snapshots.add(yf)
}

// 從 fills 統計 modern_countries（同 state_name + iso 對應）
for (const f of fills.features) {
  const name = f.properties.state_name
  const iso = f.properties.iso_a3
  if (!name || !iso) continue
  const e = byName.get(name)
  if (!e) continue  // state not in whitelist
  e.modern_countries.add(iso)
}

// 轉成 array，sort by earliest_from
const out = [...byName.values()]
  .map(e => ({
    name_en: e.name_en,
    earliest_from: e.earliest_from,
    latest_to: e.latest_to,
    modern_countries: [...e.modern_countries].sort(),
    snapshots: [...e.snapshots].sort((a, b) => a - b),
  }))
  .sort((a, b) => a.earliest_from - b.earliest_from || a.name_en.localeCompare(b.name_en))

writeFileSync(OUT_FILE, JSON.stringify(out))
console.log(`Wrote ${OUT_FILE} (${out.length} unique states, ${Math.round(JSON.stringify(out).length / 1024)} KB)`)
