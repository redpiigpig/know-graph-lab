#!/usr/bin/env node
/**
 * 一次性清理工具：把 dynasty-labels.ts 中 dynasty_zh 欄位的括號說明剝掉，
 * 讓地圖標籤保持乾淨（user feedback：國名不應有繁雜資訊，繁雜資訊到 detail 彈窗）。
 *
 * 規則：
 *   dynasty_zh: '武帝擴張（漠北之戰／絲路）' → '武帝擴張'
 *   dynasty_zh: '新王國 18 王朝（圖特摩斯／哈特謝普蘇特／阿肯那頓）' → '新王國 18 王朝'
 *   country_zh: '清' → '清'（不動）
 *
 * 只動 dynasty_zh 字串中的全形括號 `（...）` 結尾或中段。半形括號 `(...)` 不動。
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const FILE = resolve(__dirname, '..', 'data/maps/dynasty-labels.ts')

const src = readFileSync(FILE, 'utf8')
const lines = src.split(/\r?\n/)
const out = []
let stripped = 0
for (const line of lines) {
  // dynasty_zh: '...（...）...' 內的全形括號內容剝掉
  const m = line.match(/dynasty_zh: '([^']*)'/)
  if (!m) { out.push(line); continue }
  const orig = m[1]
  if (!/[（]/.test(orig)) { out.push(line); continue }
  // 剝掉所有 `（...）`
  const cleaned = orig.replace(/（[^）]*）/g, '').trim()
  if (cleaned === orig) { out.push(line); continue }
  out.push(line.replace(`dynasty_zh: '${orig}'`, `dynasty_zh: '${cleaned}'`))
  stripped++
  console.log(`  ${orig}\n  → ${cleaned}`)
}
writeFileSync(FILE, out.join('\n'))
console.log(`\n✅ Stripped ${stripped} entries`)
