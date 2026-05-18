/**
 * Generates two audit files:
 *   c:/tmp/episcopal-sees-337.txt  — full list of all sees with ancestry chain + bishop count
 *   c:/tmp/episcopal-incomplete-bishops.txt — sees whose bishop list is shorter than expected
 *
 * Run with: node scripts/episcopal-audit-export.mjs
 */
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}
const sb = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY)

const APOSTLE_NAMES = {
  ap_peter: '彼得', ap_andrew: '安得烈', ap_james_zeb: '雅各（西庇太之子）', ap_john: '約翰',
  ap_philip: '腓力', ap_bartholomew: '巴多羅買', ap_matthew: '馬太', ap_thomas: '多馬',
  ap_james_alph: '雅各（亞勒腓之子）', ap_thaddaeus: '達太', ap_simon_zeal: '西門（奮銳黨）',
  ap_matthias: '馬提亞', ap_james_just: '義人雅各', ap_jude_lord: '猶大（主弟）',
  ap_barnabas: '巴拿巴', ap_paul: '保羅',
}

// 7 大宗主教座的 see record + 它們聚合 bishop 時要跨的 church 範圍
const SPINE_PRIMARY = {
  '羅馬|天主教':                  ['未分裂教會', '天主教', '對立教宗（亞威農）', '對立教宗（比薩）', '烏特勒支舊天主教', '奧地利舊天主教', '德國舊天主教', '瑞士基督天主教', '波蘭民族天主教'],
  '君士坦丁堡|東正教':            ['未分裂教會', '東正教'],
  '亞歷山卓|東正教':              ['未分裂教會', '東正教'],
  '安提阿|東正教':                ['未分裂教會', '東正教'],
  '耶路撒冷|東正教':              ['未分裂教會', '東正教'],
  '埃奇米亞津|亞美尼亞使徒教會':  ['亞美尼亞使徒教會'],
  '塞琉西亞—泰西封|古代東方教會': ['古代東方教會', '東方教會（亞述）'],
}

const { data: sees } = await sb.from('episcopal_sees')
  .select('id, see_zh, name_zh, church, tradition, founded_year, split_year, parent_see_id, founder_apostle_id')
  .order('founded_year', { ascending: true, nullsFirst: false })

const succ = []
for (let from = 0; ; from += 1000) {
  const { data: page } = await sb.from('episcopal_succession').select('see, church').range(from, from + 999)
  if (!page || page.length === 0) break
  succ.push(...page)
  if (page.length < 1000) break
}
const bishopCount = new Map()
for (const b of succ) {
  const k = (b.see ?? '') + '|' + (b.church ?? '')
  bishopCount.set(k, (bishopCount.get(k) ?? 0) + 1)
}

function totalBishopCount(s) {
  const k = s.see_zh + '|' + s.church
  if (SPINE_PRIMARY[k]) {
    let sum = 0
    for (const ch of SPINE_PRIMARY[k]) sum += (bishopCount.get(s.see_zh + '|' + ch) ?? 0)
    return sum
  }
  return bishopCount.get(k) ?? 0
}

const seeById = new Map()
for (const s of sees) seeById.set(s.id, s)
function trace(s) {
  const chain = []
  let cur = s
  const seen = new Set()
  while (cur && !seen.has(cur.id)) {
    seen.add(cur.id)
    chain.unshift(cur)
    if (cur.parent_see_id) cur = seeById.get(cur.parent_see_id)
    else break
  }
  return chain
}
const isSpine = (s) => !!SPINE_PRIMARY[s.see_zh + '|' + s.church]

// ── 337 list ──────────────────────────────────────────────
const L337 = []
L337.push('# 使徒統緒族譜圖 — 337 教座完整名單 + 按立軌跡')
L337.push('產出時間：' + new Date().toISOString())
L337.push('共 ' + sees.length + ' 個教座')
L337.push('')
L337.push('格式：[編號] 標記 創立年 | 教座 | 教派 | tradition（附註）| 主教數')
L337.push('  軌跡：耶穌 → 使徒（如有）→ spine → ... → 自己')
L337.push('')
L337.push('★[宗主教]= 7 大族譜根   ☆[使徒立座]= 不經 spine、由使徒親建   ○= 旁支')
L337.push('========================================')
L337.push('')

let i = 0
for (const s of sees) {
  i++
  const cnt = totalBishopCount(s)
  const marker = isSpine(s) ? '★[宗主教]' : (s.founder_apostle_id ? '☆[使徒立座]' : '○')
  const notes = []
  if (s.split_year != null) notes.push('split=' + s.split_year)
  if (s.founder_apostle_id) notes.push('使徒源頭=' + (APOSTLE_NAMES[s.founder_apostle_id] ?? s.founder_apostle_id))
  const noteStr = notes.length ? '（' + notes.join(', ') + '）' : ''
  L337.push(`[${String(i).padStart(3,'0')}] ${marker} ${s.founded_year ?? '?'} | ${s.see_zh} | ${s.church} | ${s.tradition}${noteStr} | ${cnt} 任`)
  const chain = trace(s)
  const chainStr = chain.length === 1 ? '(此教座本身就是族譜根)' : chain.map(c => c.see_zh + '|' + c.church).join('  →  ')
  L337.push('      軌跡: ' + chainStr)
  if (s.founder_apostle_id) L337.push(`      使徒立座：耶穌 → ${APOSTLE_NAMES[s.founder_apostle_id]}`)
  L337.push('')
}

L337.push('========================================')
L337.push('# 統計')
L337.push('')
const byTrad = {}
for (const s of sees) byTrad[s.tradition] = (byTrad[s.tradition] ?? 0) + 1
for (const [t, n] of Object.entries(byTrad).sort((a, b) => b[1] - a[1])) L337.push('  ' + t + ': ' + n)
let total = 0
for (const v of bishopCount.values()) total += v
L337.push('')
L337.push('總主教數: ' + total)

fs.writeFileSync('c:/tmp/episcopal-sees-337.txt', L337.join('\n'), 'utf-8')
console.log('✔ saved c:/tmp/episcopal-sees-337.txt (' + sees.length + ' sees)')

// ── Incomplete list ──────────────────────────────────────
const incomplete = []
for (const s of sees) {
  const cnt = totalBishopCount(s)
  let expected = 0
  let reason = ''
  if (isSpine(s)) { expected = 50; reason = '宗主教座 spine（應至少 50 任）' }
  else if (s.split_year != null && (s.founded_year ?? 9999) < 1900) { expected = 5; reason = '自主/分裂教會（應至少 5 任）' }
  else if (s.founder_apostle_id) { expected = 3; reason = '使徒立座（應至少 3 任）' }
  else if (s.founded_year != null && s.founded_year < 1700) { expected = 3; reason = '古老教座（應至少 3 任）' }
  else if (s.founded_year != null && s.founded_year >= 1700) { expected = 1; reason = '現代教座（至少 1 任）' }
  else { expected = 1; reason = '未知年份' }
  if (cnt < expected) incomplete.push({ s, cnt, expected, reason })
}
incomplete.sort((a, b) => {
  if (a.expected !== b.expected) return b.expected - a.expected
  return a.cnt - b.cnt
})

const Linc = []
Linc.push('# 主教名單不齊的教座清單')
Linc.push('產出時間：' + new Date().toISOString())
Linc.push('')
Linc.push('共 ' + incomplete.length + ' / ' + sees.length + ' 個教座未達建議主教數')
Linc.push('')
Linc.push('格式：[實際/應有] 創立年 | 教座 | 教派 | tradition  ← 原因')
Linc.push('========================================')

let prevExpected = -1
for (const it of incomplete) {
  if (it.expected !== prevExpected) {
    Linc.push('')
    Linc.push('── 應該至少 ' + it.expected + ' 任 ──')
    prevExpected = it.expected
  }
  Linc.push(`[${it.cnt}/${it.expected}] ${it.s.founded_year ?? '?'} | ${it.s.see_zh} | ${it.s.church} | ${it.s.tradition}  ← ${it.reason}`)
}

Linc.push('')
Linc.push('========================================')
Linc.push('# 0 主教的教座（完全沒建檔）')
Linc.push('')
const zeros = sees.filter(s => totalBishopCount(s) === 0)
for (const s of zeros) Linc.push(`  ${s.founded_year ?? '?'} | ${s.see_zh} | ${s.church} | ${s.tradition}`)
Linc.push('')
Linc.push('共 ' + zeros.length + ' 個教座尚無任何主教')

fs.writeFileSync('c:/tmp/episcopal-incomplete-bishops.txt', Linc.join('\n'), 'utf-8')
console.log('✔ saved c:/tmp/episcopal-incomplete-bishops.txt (' + incomplete.length + ' incomplete)')
