// 對帳：文獻母體 × 逐筆歸屬 × 代號主檔
//   node scripts/genealogy_audit_tags.mjs
// 三項檢查都印分母：① 母體每一筆都有 tag ② tag 沒有孤兒鍵 ③ 用到的代號都在主檔裡

import { readFileSync } from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const read = f => JSON.parse(readFileSync(path.join(ROOT, f), 'utf8'))

const corpus = read('data/christian-genealogy/corpus-1-2c.json')
const tagsDoc = read('data/christian-genealogy/doc-tags.json')
const tree = read('data/christian-genealogy/traditions.json')

// 主檔裡所有合法代號
const codes = new Set()
const collect = (node, arr) => {
  for (const n of arr) {
    codes.add(n.code)
    if (n.sub) collect(n, n.sub)
  }
}
collect(null, tree.layer1)
collect(null, tree.layer2)
collect(null, tree.layer3)
for (const n of tree.layer2) for (const s of n.sub || []) if (s.sub) collect(null, s.sub)

const works = corpus.works
const tags = tagsDoc.tags
const titles = new Set(works.map(w => w.title_zh))

const missing = works.filter(w => !tags[w.title_zh])
const orphans = Object.keys(tags).filter(k => !titles.has(k))
const badCodes = []
for (const [title, t] of Object.entries(tags)) {
  for (const c of t.t || []) if (!codes.has(c)) badCodes.push(`${title} → ${c}`)
}

const byKind = {}
const byTradition = {}
let untagged = 0
for (const w of works) {
  const t = tags[w.title_zh]
  if (!t) continue
  byKind[t.kind] = (byKind[t.kind] || 0) + 1
  byTradition[t.tradition] = (byTradition[t.tradition] || 0) + 1
  if (!t.t || !t.t.length) untagged++
}

const trajCount = {}
for (const t of Object.values(tags)) for (const c of t.t || []) trajCount[c] = (trajCount[c] || 0) + 1

console.log('母體             ', works.length)
console.log('主檔合法代號     ', codes.size)
console.log('')
console.log('① 母體缺 tag     ', missing.length, '/', works.length, missing.length ? '←✗' : '←✓')
for (const w of missing) console.log('     ✗', w.title_zh)
console.log('② tag 孤兒鍵     ', orphans.length, '/', Object.keys(tags).length, orphans.length ? '←✗' : '←✓')
for (const k of orphans) console.log('     ✗', k)
console.log('③ 查無此代號     ', badCodes.length, badCodes.length ? '←✗' : '←✓')
for (const b of badCodes) console.log('     ✗', b)
console.log('')
console.log('性質分佈：', byKind)
console.log('不掛軌跡者（城市傳統產物／猶太背景／抄本）:', untagged, '/', works.length)
console.log('')
console.log('城市傳統分佈：')
for (const [k, n] of Object.entries(byTradition).sort((a, b) => b[1] - a[1])) console.log('  ', String(n).padStart(3), k)
console.log('')
console.log('軌跡代號分佈：')
for (const [k, n] of Object.entries(trajCount).sort((a, b) => b[1] - a[1])) console.log('  ', String(n).padStart(3), k)

const ok = !missing.length && !orphans.length && !badCodes.length
console.log('')
console.log(ok ? '✓ 三項全綠' : '✗ 有未解項，見上')
process.exit(ok ? 0 : 1)
