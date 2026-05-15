#!/usr/bin/env node
/**
 * 兩階段：先抓所有歷史國家 QID + 英文名 + 年代 + 大陸，
 * 然後批次補抓中文名（多 zh 變體：zh-hant > zh-tw > zh-hk > zh > zh-hans > zh-cn）。
 */

import { writeFileSync } from 'node:fs'

const SPARQL_URL = 'https://query.wikidata.org/sparql'
const UA = 'know-graph-lab/1.0 (https://github.com/redpiigpig/know-graph-lab)'

async function sparql(query) {
  const params = new URLSearchParams({ query, format: 'json' })
  const res = await fetch(SPARQL_URL + '?' + params, {
    headers: { 'Accept': 'application/sparql-results+json', 'User-Agent': UA },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`)
  return res.json()
}

// ========== Stage 1: 抓所有歷史國家骨架 ==========
const Q_HISTORICAL_COUNTRY = 'Q3024240'
const Q_ANCIENT_CIV = 'Q28171280'
const Q_FORMER_KINGDOM = 'Q1763761'
const Q_EMPIRE = 'Q48349'

// 各類型分開查（避免 UNION 太大 timeout）
async function queryStatesOfType(p31Pattern, label) {
  const q = `
SELECT DISTINCT ?state ?stateLabel ?inception ?dissolved WHERE {
  ${p31Pattern}
  OPTIONAL { ?state wdt:P571 ?inception . }
  OPTIONAL { ?state wdt:P576 ?dissolved . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 6000
`
  console.log(`Stage 1.${label}: query ${label}…`)
  const r = await sparql(q)
  console.log(`  got ${r.results.bindings.length}`)
  return r.results.bindings
}

const byState = new Map()
function ingest(b) {
  const id = b.state.value.split('/').pop()
  if (!byState.has(id)) {
    byState.set(id, {
      qid: id,
      name_en: b.stateLabel?.value || '',
      name_zh: '',
      inception: b.inception?.value || null,
      dissolved: b.dissolved?.value || null,
      continents: new Set(),
    })
  }
  const e = byState.get(id)
  if (!e.inception && b.inception?.value) e.inception = b.inception.value
  if (!e.dissolved && b.dissolved?.value) e.dissolved = b.dissolved.value
}

const types = [
  [`?state wdt:P31/wdt:P279* wd:${Q_HISTORICAL_COUNTRY} .`, 'historical-country'],
  [`?state wdt:P31 wd:${Q_ANCIENT_CIV} .`, 'ancient-civilization'],
  [`?state wdt:P31 wd:${Q_FORMER_KINGDOM} .`, 'former-kingdom'],
  [`?state wdt:P31/wdt:P279* wd:${Q_EMPIRE} .`, 'empire'],
]
for (const [pattern, label] of types) {
  try {
    const bindings = await queryStatesOfType(pattern, label)
    for (const b of bindings) ingest(b)
  } catch (e) {
    console.warn(`  ${label} failed: ${e.message.slice(0,100)}`)
  }
}
console.log(`Total unique states: ${byState.size}`)

// ========== Stage 2: 批次查中文名（zh 變體）==========
const allQids = [...byState.keys()]
const BATCH = 200
console.log(`Stage 2: fetch Chinese labels in batches of ${BATCH}…`)

async function fetchZhBatch(qids) {
  const values = qids.map(q => `wd:${q}`).join(' ')
  const q = `
SELECT ?state ?zh ?zhHant ?zhHans ?zhTw ?zhHk ?zhCn WHERE {
  VALUES ?state { ${values} }
  OPTIONAL { ?state rdfs:label ?zh FILTER(LANG(?zh) = "zh") }
  OPTIONAL { ?state rdfs:label ?zhHant FILTER(LANG(?zhHant) = "zh-hant") }
  OPTIONAL { ?state rdfs:label ?zhHans FILTER(LANG(?zhHans) = "zh-hans") }
  OPTIONAL { ?state rdfs:label ?zhTw FILTER(LANG(?zhTw) = "zh-tw") }
  OPTIONAL { ?state rdfs:label ?zhHk FILTER(LANG(?zhHk) = "zh-hk") }
  OPTIONAL { ?state rdfs:label ?zhCn FILTER(LANG(?zhCn) = "zh-cn") }
}
`
  return sparql(q)
}

function pickZh(b) {
  return b.zhHant?.value || b.zhTw?.value || b.zhHk?.value
      || b.zh?.value || b.zhHans?.value || b.zhCn?.value || ''
}

for (let i = 0; i < allQids.length; i += BATCH) {
  const batch = allQids.slice(i, i + BATCH)
  try {
    const r = await sparql(`
SELECT ?state ?zh ?zhHant ?zhHans ?zhTw ?zhHk ?zhCn WHERE {
  VALUES ?state { ${batch.map(q => `wd:${q}`).join(' ')} }
  OPTIONAL { ?state rdfs:label ?zh FILTER(LANG(?zh) = "zh") }
  OPTIONAL { ?state rdfs:label ?zhHant FILTER(LANG(?zhHant) = "zh-hant") }
  OPTIONAL { ?state rdfs:label ?zhHans FILTER(LANG(?zhHans) = "zh-hans") }
  OPTIONAL { ?state rdfs:label ?zhTw FILTER(LANG(?zhTw) = "zh-tw") }
  OPTIONAL { ?state rdfs:label ?zhHk FILTER(LANG(?zhHk) = "zh-hk") }
  OPTIONAL { ?state rdfs:label ?zhCn FILTER(LANG(?zhCn) = "zh-cn") }
}
`)
    for (const b of r.results.bindings) {
      const id = b.state.value.split('/').pop()
      const e = byState.get(id)
      if (!e) continue
      const zh = pickZh(b)
      if (zh && !e.name_zh) e.name_zh = zh
    }
    process.stdout.write(`  batch ${Math.floor(i/BATCH)+1}/${Math.ceil(allQids.length/BATCH)}\r`)
  } catch (e) {
    console.warn(`\n  batch ${i}–${i+BATCH} failed: ${e.message.slice(0,80)}`)
  }
}
console.log('\n')

// ========== Output ==========
function parseIsoDateToYear(iso) {
  if (!iso) return null
  const m = iso.match(/^([+-]?)(\d+)-/)
  if (!m) return null
  const sign = m[1] === '-' ? -1 : 1
  return sign * parseInt(m[2], 10)
}

const out = [...byState.values()]
  .map(e => ({
    qid: e.qid,
    name_en: e.name_en,
    name_zh: e.name_zh || null,
    inception_year: parseIsoDateToYear(e.inception),
    dissolved_year: parseIsoDateToYear(e.dissolved),
    continents: [...e.continents].sort(),
  }))
  .filter(e => e.name_en && !e.name_en.startsWith('Q'))
  .sort((a, b) => {
    const ay = a.inception_year ?? 9999
    const by = b.inception_year ?? 9999
    return ay - by || a.name_en.localeCompare(b.name_en)
  })

const OUT_FILE = 'public/maps/wikidata-states.json'
writeFileSync(OUT_FILE, JSON.stringify(out))
console.log(`Wrote ${OUT_FILE} (${out.length} states, ${Math.round(JSON.stringify(out).length / 1024)} KB)`)

const withZh = out.filter(e => e.name_zh).length
console.log(`  with Chinese name: ${withZh} (${(withZh*100/out.length).toFixed(1)}%)`)
console.log(`  with inception year: ${out.filter(e => e.inception_year != null).length}`)
console.log(`  with dissolution year: ${out.filter(e => e.dissolved_year != null).length}`)
