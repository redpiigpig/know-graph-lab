#!/usr/bin/env node
/**
 * 歷史國界 100 年級距審查 v2 — 直接列出每年活躍 polygon
 *
 * 對每 100 年（-4000 → 2000）：
 *   - 列出所有活躍政權（過濾 is_state）
 *   - 標註重複名稱（同名 polygon 出現多次）
 *   - 標註明顯時代錯置（殖民地 prefix 出現在大航海前 / 帝國詞出現在帝國前）
 *   - 標註跨度過大 polygon（>2000 年）
 *
 * 輸出：scripts/_audit_historical_borders.txt
 */

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

const geojson = JSON.parse(readFileSync(resolve(ROOT, 'public/maps/historical-states.geojson'), 'utf8'))
const cls = JSON.parse(readFileSync(resolve(ROOT, 'public/maps/polygon-classifications.json'), 'utf8'))
const zhMap = JSON.parse(readFileSync(resolve(ROOT, 'public/maps/polygon-names-zh.json'), 'utf8'))

const states = geojson.features
  .map(f => ({
    name: f.properties.name,
    yearFrom: f.properties.year_from,
    yearTo: f.properties.year_to,
  }))
  .filter(s => cls[s.name]?.is_state !== false)

const lines = []
const log = (s) => lines.push(s)

const fmtYear = (y) => {
  if (y < 0) return `${-y + 1} BCE`
  if (y === 0) return '1 BCE'
  if (y >= 9999) return '至今'
  return `${y} CE`
}
const zhOf = (n) => zhMap[n] || n

// ===== Pre-pass：抓真正的時代錯置 =====
const ANACHRONISMS = []
const RULES = [
  { re: /^(British|England|English)\s/i, minYear: 1066, desc: '英王國盎格魯-諾曼後' },
  { re: /^(French|France)\s/i, minYear: 843, desc: '法蘭克分裂' },
  { re: /^(Spanish|Spain)\s/i, minYear: 1469, desc: '卡斯提爾+亞拉岡' },
  { re: /^(Portuguese|Portugal)\s/i, minYear: 1139, desc: '葡萄牙王國' },
  { re: /^(Dutch|Netherlands)\s/i, minYear: 1568, desc: '荷蘭獨立戰爭' },
  { re: /^(Italian|Italy)\s/i, minYear: 1861, desc: '義大利統一' },
  { re: /^(German|Germany)\s/i, minYear: 1871, desc: '德意志統一（神羅不算 Germany）' },
  { re: /^(Belgian|Belgium)\s/i, minYear: 1830, desc: '比利時獨立' },
  { re: /^(Russian Empire|Tsardom of Russia)/i, minYear: 1547, desc: '伊凡四世稱沙皇' },
  { re: /^(Soviet|USSR)/i, minYear: 1917, desc: 'Soviet 1917' },
  { re: /\b(Ottoman Empire)\b/i, minYear: 1299, desc: 'Ottoman 1299' },
  { re: /\b(Mughal Empire)\b/i, minYear: 1526, desc: 'Mughal 1526' },
  { re: /\b(Byzantine)\b/i, minYear: 330, desc: '通常 330+ 算拜占庭' },
  { re: /\b(Holy Roman Empire)\b/i, minYear: 800, desc: '查理曼加冕' },
  { re: /\b(Carolingian)\b/i, minYear: 751, desc: '加洛林王朝' },
  { re: /\b(Frankish Kingdom)\b/i, minYear: 481, desc: '克洛維建國' },
]
for (const s of states) {
  for (const r of RULES) {
    if (r.re.test(s.name) && s.yearFrom < r.minYear) {
      ANACHRONISMS.push({
        name: s.name, zh: zhOf(s.name),
        yearFrom: s.yearFrom, yearTo: s.yearTo,
        rule: r.desc, minYear: r.minYear,
      })
      break
    }
  }
}

// ===== Pre-pass：跨度過大 =====
const WIDE_SPANS = states
  .filter(s => s.yearTo - s.yearFrom > 1500 && s.yearTo < 9000)
  .sort((a, b) => (b.yearTo - b.yearFrom) - (a.yearTo - a.yearFrom))

// ===== Pre-pass：所有同年重複 =====
function detectDuplicatesPerYear(year) {
  const active = states.filter(s => year >= s.yearFrom && year <= s.yearTo)
  const counts = new Map()
  for (const s of active) {
    if (!counts.has(s.name)) counts.set(s.name, [])
    counts.get(s.name).push(s)
  }
  const dups = []
  for (const [name, entries] of counts) {
    if (entries.length > 1) {
      dups.push({ name, zh: zhOf(name), count: entries.length, entries })
    }
  }
  return { active, dups }
}

// ===== 主：每 100 年列出 =====
log(`# 歷史國界 100 年級距審查（v2）`)
log(`時間：${new Date().toISOString()}`)
log(`資料：historical-states.geojson ${geojson.features.length} features → 過濾政權後 ${states.length}\n`)

log(`## 預掃結果\n`)

log(`### A. 時代錯置（${ANACHRONISMS.length} 條）`)
for (const a of ANACHRONISMS) {
  log(`  - 「${a.name}」（${a.zh}）year_from=${fmtYear(a.yearFrom)} → ${fmtYear(a.yearTo)} | 規則：${a.rule}（min=${fmtYear(a.minYear)}）`)
}
log('')

log(`### B. 跨度過大 polygon（>1500 年，top 30）`)
for (const s of WIDE_SPANS.slice(0, 30)) {
  log(`  - 「${s.name}」（${zhOf(s.name)}） ${fmtYear(s.yearFrom)} → ${fmtYear(s.yearTo)} = ${s.yearTo - s.yearFrom} 年`)
}
if (WIDE_SPANS.length > 30) log(`  …還有 ${WIDE_SPANS.length - 30} 條`)
log('')

// ===== 每 100 年清單 =====
log(`## 每 100 年活躍政權清單\n`)
const STEP = 100
const yearStats = []
for (let year = -4000; year <= 2000; year += STEP) {
  const { active, dups } = detectDuplicatesPerYear(year)
  yearStats.push({ year, count: active.length, dups: dups.length })

  log(`\n### ${fmtYear(year)}  ·  ${active.length} 政權  ${dups.length ? `· 重複 ${dups.length} 條` : ''}`)

  if (dups.length > 0) {
    log(`  ⚠ 同名重複：`)
    for (const d of dups) {
      const spans = d.entries.map(e => `${fmtYear(e.yearFrom)}-${fmtYear(e.yearTo)}`).join('、')
      log(`    - 「${d.name}」（${d.zh}）x${d.count} | ${spans}`)
    }
  }

  // 全部列出（按 yearFrom 排序）
  const sorted = [...active].sort((a, b) => a.yearFrom - b.yearFrom || a.name.localeCompare(b.name))
  // 每行 4 個
  const formatted = sorted.map(s => `${zhOf(s.name)} (${s.name.slice(0, 28)})`)
  for (let i = 0; i < formatted.length; i += 3) {
    log('    ' + formatted.slice(i, i + 3).map(x => x.padEnd(50)).join(' '))
  }
}

// ===== 統計 =====
log(`\n## 各年總數（每 100 年）\n`)
for (let i = 0; i < yearStats.length; i += 5) {
  log('  ' + yearStats.slice(i, i + 5).map(s =>
    `${fmtYear(s.year).padStart(10)}: ${String(s.count).padStart(3)}${s.dups ? `(重${s.dups})` : ''}`
  ).join('  '))
}

writeFileSync(resolve(ROOT, 'scripts/_audit_historical_borders.txt'), lines.join('\n'), 'utf8')
console.log(`✓ 寫入 scripts/_audit_historical_borders.txt（${lines.length} 行）`)
console.log(`時代錯置：${ANACHRONISMS.length}，跨度過大：${WIDE_SPANS.length}`)
