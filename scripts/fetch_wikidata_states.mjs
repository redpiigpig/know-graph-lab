#!/usr/bin/env node
/**
 * 從 Wikidata SPARQL 抓全部「歷史國家／已消失主權國家」實體。
 *
 * Wikidata 用以下類型代表歷史國家：
 *   - Q3024240 historical country
 *   - Q839954 historical region
 *   - Q1763761 former kingdom
 *   - Q56061 administrative territorial entity
 *   - Q417175 historical period
 *
 * 抓欄位：name (en + zh) / inception / dissolution / continent
 *
 * 輸出：public/maps/wikidata-states.json
 */

import { writeFileSync } from 'node:fs'

const SPARQL_URL = 'https://query.wikidata.org/sparql'

// 用 instance of (P31) + subclass (P279) 找 historical country 與其子類
// 主要目標：former sovereign states, empires, ancient civilizations
const QUERY = `
SELECT DISTINCT ?state ?stateLabel ?stateZh ?inception ?dissolved ?continent ?continentLabel WHERE {
  {
    ?state wdt:P31/wdt:P279* wd:Q3024240 .  # historical country
  } UNION {
    ?state wdt:P31 wd:Q28171280 .            # ancient civilization
  } UNION {
    ?state wdt:P31 wd:Q1763761 .             # former kingdom
  } UNION {
    ?state wdt:P31/wdt:P279* wd:Q48349 .     # empire
  }
  OPTIONAL { ?state wdt:P571 ?inception . }   # inception
  OPTIONAL { ?state wdt:P576 ?dissolved . }   # dissolved/end date
  OPTIONAL { ?state wdt:P30 ?continent . }    # continent
  OPTIONAL { ?state rdfs:label ?stateZh FILTER(LANG(?stateZh) = "zh") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?inception
LIMIT 10000
`

console.log('Querying Wikidata SPARQL endpoint…')
const params = new URLSearchParams({ query: QUERY, format: 'json' })
const res = await fetch(SPARQL_URL + '?' + params, {
  headers: {
    'Accept': 'application/sparql-results+json',
    'User-Agent': 'know-graph-lab/1.0 (https://github.com/redpiigpig/know-graph-lab)',
  },
})

if (!res.ok) {
  console.error(`Error: ${res.status} ${res.statusText}`)
  console.error(await res.text())
  process.exit(1)
}

const data = await res.json()
console.log(`Got ${data.results.bindings.length} bindings`)

// 合併同一 state 的多筆 binding（continent 是 multi-value）
const byState = new Map()
for (const b of data.results.bindings) {
  const id = b.state.value.split('/').pop()
  if (!byState.has(id)) {
    byState.set(id, {
      qid: id,
      name_en: b.stateLabel?.value || '',
      name_zh: b.stateZh?.value || '',
      inception: b.inception?.value || null,
      dissolved: b.dissolved?.value || null,
      continents: new Set(),
    })
  }
  const e = byState.get(id)
  if (b.continentLabel?.value) e.continents.add(b.continentLabel.value)
  if (!e.name_zh && b.stateZh?.value) e.name_zh = b.stateZh.value
  if (!e.inception && b.inception?.value) e.inception = b.inception.value
  if (!e.dissolved && b.dissolved?.value) e.dissolved = b.dissolved.value
}

// 整理輸出：parse ISO dates 為天文年
function parseIsoDateToYear(iso) {
  if (!iso) return null
  // Wikidata 日期格式：'+0476-01-01T00:00:00Z' 或 '-0500-01-01T00:00:00Z'
  // 注意 BCE 用 '-' 前綴
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
  .filter(e => e.name_en && !e.name_en.startsWith('Q'))  // skip ones without label
  .sort((a, b) => {
    const ay = a.inception_year ?? 9999
    const by = b.inception_year ?? 9999
    return ay - by || a.name_en.localeCompare(b.name_en)
  })

const OUT_FILE = 'public/maps/wikidata-states.json'
writeFileSync(OUT_FILE, JSON.stringify(out))
console.log(`Wrote ${OUT_FILE} (${out.length} states, ${Math.round(JSON.stringify(out).length / 1024)} KB)`)

// stats
const withZh = out.filter(e => e.name_zh).length
const withInception = out.filter(e => e.inception_year != null).length
const withDissolution = out.filter(e => e.dissolved_year != null).length
console.log(`  with Chinese name: ${withZh}`)
console.log(`  with inception year: ${withInception}`)
console.log(`  with dissolution year: ${withDissolution}`)
