#!/usr/bin/env node
/**
 * 自動推斷 historical state 的 realm_id / sphere_id
 *
 * 邏輯：
 *   對每個 state 的 modern_countries[]，依 year_start（state 起始年）
 *   在 country-sphere-timeline 上 vote 出最常見的 sphere → 對應到 realm。
 *
 * 輸出：public/maps/state-sphere-inference.json
 *   { stateName: { sphere_id, realm_id, confidence, sources: [{iso, sphere}], reason } }
 *
 * 用法：node scripts/infer_state_realm_sphere.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

// ---------- parse country-sphere-timeline.ts ----------
function parseTimeline() {
  const text = readFileSync(resolve(ROOT, 'data/maps/country-sphere-timeline.ts'), 'utf8')
  // 抓 COUNTRY_SPHERE_TIMELINE = { ... } 區塊
  const start = text.indexOf('COUNTRY_SPHERE_TIMELINE')
  const open = text.indexOf('{', start)
  // 找配對的 }
  let depth = 0
  let end = -1
  for (let i = open; i < text.length; i++) {
    const c = text[i]
    if (c === '{') depth++
    else if (c === '}') {
      depth--
      if (depth === 0) { end = i; break }
    }
  }
  const body = text.slice(open + 1, end)
  // 抓每個 ISO: [ ... ]
  const tl = {}
  // 先抓 ISO 碼開頭：3 個大寫字母 + : + [
  const blockRe = /\b([A-Z]{3})\s*:\s*\[([\s\S]*?)\]\s*,/g
  let m
  while ((m = blockRe.exec(body)) !== null) {
    const iso = m[1]
    const inner = m[2]
    // 抓每個 { from: -X, sphere: 'foo', ... }
    const entries = []
    const entRe = /\{\s*from\s*:\s*(-?\d+)\s*,\s*sphere\s*:\s*'([^']+)'/g
    let em
    while ((em = entRe.exec(inner)) !== null) {
      entries.push({ from: Number(em[1]), sphere: em[2] })
    }
    if (entries.length) tl[iso] = entries
  }
  return tl
}

function sphereForCountryAtYear(timeline, iso, year) {
  const tl = timeline[iso]
  if (!tl) return null
  let active = null
  for (const e of tl) {
    if (e.from <= year) active = e.sphere
    else break
  }
  return active
}

// ---------- parse SPHERES → realm map ----------
function parseSphereRealmMap() {
  const text = readFileSync(resolve(ROOT, 'data/maps/world-religions.ts'), 'utf8')
  // 每個 sphere object 裡有 id: 'X' 與 realm_id: 'Y'
  // SPHERES = [ { id: '...', name_zh: '...', name_en: '...', realm_id: '...', ... }, ... ]
  const map = {}
  const re = /id:\s*'([\w-]+)'[^{}]*?realm_id:\s*'([\w-]+)'/g
  let m
  while ((m = re.exec(text)) !== null) {
    if (!map[m[1]]) map[m[1]] = m[2]
  }
  return map
}

// ---------- main ----------
function main() {
  const timeline = parseTimeline()
  const sphereToRealm = parseSphereRealmMap()
  console.log(`Parsed ${Object.keys(timeline).length} countries, ${Object.keys(sphereToRealm).length} spheres`)

  const skeleton = JSON.parse(readFileSync(resolve(ROOT, 'public/maps/state-skeleton.json'), 'utf8'))
  const wikidata = JSON.parse(readFileSync(resolve(ROOT, 'public/maps/wikidata-states.json'), 'utf8'))

  // 把 wikidata inception_year 也納入做為 fallback 起始年
  const wdMap = new Map()
  for (const w of wikidata) {
    const k = w.name_en.toLowerCase().replace(/\s+/g, '').replace(/[^\w]/g, '')
    wdMap.set(k, w)
  }
  const norm = (s) => s.toLowerCase().replace(/\s+/g, '').replace(/[^\w]/g, '')

  const out = {}
  let inferredCount = 0
  let skippedNoCountries = 0
  let skippedNoYear = 0
  let skippedNoSphere = 0

  for (const sk of skeleton) {
    const name = sk.name_en
    const moderns = sk.modern_countries || []
    if (!moderns.length) { skippedNoCountries++; continue }

    const wd = wdMap.get(norm(name))
    const yearStart = (typeof sk.earliest_from === 'number')
      ? sk.earliest_from
      : (wd?.inception_year ?? null)

    if (yearStart === null || yearStart === undefined) { skippedNoYear++; continue }

    // vote
    const tally = new Map()
    const sources = []
    for (const iso of moderns) {
      const sph = sphereForCountryAtYear(timeline, iso, yearStart)
      if (!sph) continue
      tally.set(sph, (tally.get(sph) || 0) + 1)
      sources.push({ iso, sphere: sph })
    }
    if (!tally.size) { skippedNoSphere++; continue }

    // 取最高票（平手取第一個）
    let topSphere = null, topCount = 0
    for (const [s, n] of tally) {
      if (n > topCount) { topSphere = s; topCount = n }
    }
    const realm = sphereToRealm[topSphere] || null
    const confidence = sources.length ? topCount / sources.length : 0

    out[name] = {
      sphere_id: topSphere,
      realm_id: realm,
      confidence: Number(confidence.toFixed(2)),
      sources,
      year_inferred_at: yearStart,
      reason: `vote ${topCount}/${sources.length} modern_countries match '${topSphere}' at year ${yearStart}`,
    }
    inferredCount++
  }

  const outPath = resolve(ROOT, 'public/maps/state-sphere-inference.json')
  writeFileSync(outPath, JSON.stringify(out, null, 0), 'utf8')

  console.log(`✓ wrote ${outPath}`)
  console.log(`  inferred: ${inferredCount}`)
  console.log(`  skipped (no modern_countries): ${skippedNoCountries}`)
  console.log(`  skipped (no year_start): ${skippedNoYear}`)
  console.log(`  skipped (no sphere match at year): ${skippedNoSphere}`)
  // 各 realm 分布
  const byRealm = {}
  for (const v of Object.values(out)) {
    const r = v.realm_id || '(null)'
    byRealm[r] = (byRealm[r] || 0) + 1
  }
  console.log('  by realm:', byRealm)
}

main()
