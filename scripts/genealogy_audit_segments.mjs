// 段落層對帳：段落骨架 × 逐段歸屬 × 代號主檔
//   node scripts/genealogy_audit_segments.mjs
// 每一項都印分母。已完成的卷才檢查；未做的卷列出來，不當作通過。

import { readFileSync, existsSync, readdirSync } from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const read = f => JSON.parse(readFileSync(path.join(ROOT, f), 'utf8'))

const peri = read('data/christian-genealogy/nt-pericopes.json')
const tree = read('data/christian-genealogy/traditions.json')
const defs = read('data/christian-genealogy/nt-book-defaults.json').books

const codes = new Set()
const collect = arr => {
  for (const n of arr) {
    codes.add(n.code)
    if (n.sub) collect(n.sub)
  }
}
collect(tree.layer1); collect(tree.layer2); collect(tree.layer3)

const segDir = path.join(ROOT, 'data/christian-genealogy/segments')
const done = existsSync(segDir) ? readdirSync(segDir).filter(f => f.endsWith('.json')).map(f => f.replace('.json', '')) : []

const NT = Object.keys(peri.books)
let vTotal = 0, vDone = 0
const problems = []
const rows = []

for (const code of NT) {
  const segs = peri.books[code]
  const vs = segs.reduce((n, s) => n + s.verses, 0)
  vTotal += vs
  if (!done.includes(code)) { rows.push([code, segs.length, '—', vs, '未做']); continue }

  const doc = read(`data/christian-genealogy/segments/${code}.json`)
  const tags = doc.segments
  const skeletonRefs = segs.map(s => `${s.from[0]}:${s.from[1]}-${s.to[0]}:${s.to[1]}`)
  const missing = skeletonRefs.filter(r => !tags[r])
  const orphan = Object.keys(tags).filter(r => !skeletonRefs.includes(r))
  const noTitle = Object.entries(tags).filter(([, t]) => !t.title).map(([r]) => r)
  const noSrc = Object.entries(tags).filter(([, t]) => !t.sources || !t.sources.length).map(([r]) => r)
  const badCode = []
  for (const [r, t] of Object.entries(tags)) for (const c of t.sources || []) if (!codes.has(c)) badCode.push(`${r}→${c}`)
  if (doc.meta.editor !== defs[code].editor) problems.push(`${code}: editor ${doc.meta.editor} 與書卷層 ${defs[code].editor} 不一致`)
  if (missing.length) problems.push(`${code}: 骨架有 ${missing.length} 段沒有歸屬 — ${missing.slice(0, 3).join('、')}`)
  if (orphan.length) problems.push(`${code}: 歸屬有 ${orphan.length} 個孤兒段 — ${orphan.slice(0, 3).join('、')}`)
  if (noTitle.length) problems.push(`${code}: ${noTitle.length} 段沒有標題`)
  if (noSrc.length) problems.push(`${code}: ${noSrc.length} 段沒有來源`)
  if (badCode.length) problems.push(`${code}: ${badCode.length} 個代號查無此項 — ${badCode.slice(0, 3).join('、')}`)

  vDone += vs
  rows.push([code, segs.length, Object.keys(tags).length, vs, problems.length ? '有問題' : '完成'])
}

console.log(`${'卷'.padEnd(6)}${'骨架段'.padStart(8)}${'已歸屬'.padStart(8)}${'節數'.padStart(7)}   狀態`)
for (const [c, sk, tg, v, st] of rows) {
  if (st === '未做') continue
  console.log(`${c.padEnd(6)}${String(sk).padStart(8)}${String(tg).padStart(8)}${String(v).padStart(7)}   ${st}`)
}
const todo = rows.filter(r => r[4] === '未做')
console.log(`\n已做 ${done.length} / ${NT.length} 卷　逐節進度 ${vDone} / ${vTotal} 節（${(vDone / vTotal * 100).toFixed(1)}%）`)
console.log(`未做 ${todo.length} 卷：${todo.map(r => r[0]).join(' ')}`)

if (problems.length) {
  console.log('\n✗ 問題：')
  for (const p of problems) console.log('   ' + p)
} else if (done.length) {
  console.log('\n✓ 已做的卷全部通過（段落齊、無孤兒、標題與來源皆有、代號皆存在、editor 與書卷層一致）')
}
process.exit(problems.length ? 1 : 0)
