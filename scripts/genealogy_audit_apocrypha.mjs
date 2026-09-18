// 典外文獻歸屬對帳：福音書 30 種 ＋ 非福音 36 種 × 代號主檔 × 書目層
//   node scripts/genealogy_audit_apocrypha.mjs
// 每一項都印分母。actual 留空是允許的（材料不足），但必須在 rationale 裡說明。

import { readFileSync } from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const read = f => JSON.parse(readFileSync(path.join(ROOT, f), 'utf8'))

const files = [
  ['福音書', 'data/christian-genealogy/apocryphal-gospels.json'],
  ['非福音', 'data/christian-genealogy/nt-apocrypha.json'],
]
const tree = read('data/christian-genealogy/traditions.json')
const bib = read('data/christian-genealogy/bibliography.json').entries

const codes = new Set()
const collect = arr => { for (const n of arr) { codes.add(n.code); if (n.sub) collect(n.sub) } }
collect(tree.layer1); collect(tree.layer2); collect(tree.layer3)

const problems = []
let total = 0, withContent = 0, ownJudgment = 0, emptyActual = 0, beyond = 0, xref = 0
const noText = []
const trajCount = {}
const byNTA = {}

for (const [label, f] of files) {
  const docs = read(f).documents
  let n = 0
  for (const [slug, d] of Object.entries(docs)) {
    n++; total++
    if (!d.title) problems.push(`${slug}: 缺 title`)
    if (!d.rationale) problems.push(`${slug}: 缺 rationale`)
    if (!d.place) problems.push(`${slug}: 缺 place`)
    if (!d.place_kind) problems.push(`${slug}: 缺 place_kind`)
    if (!d.date || d.date.length !== 2) problems.push(`${slug}: 缺 date 區間`)
    if (d.sections > 0) withContent++; else noText.push(slug)
    if (d.text_in) xref++
    if (d.own_judgment) ownJudgment++
    if (d.beyond_scope) beyond++
    const actual = d.actual || []
    if (!actual.length) {
      emptyActual++
      if (!/留空|不足|無從|不足以/.test(d.rationale || '')) {
        problems.push(`${slug}: actual 留空但 rationale 未說明理由`)
      }
    }
    for (const c of [...(d.attributed || []), ...actual]) {
      if (!codes.has(c)) problems.push(`${slug}: 查無代號 ${c}`)
      else trajCount[c] = (trajCount[c] || 0) + 1
    }
    for (const k of d.support || []) if (!bib[k]) problems.push(`${slug}: support 查無書目 ${k}`)
    // 🚨 使用者的規定：有歸屬主張就要說得出憑什麼——引學者，或標明是本表判斷並寫出依據。
    //    2026-09-18 查出 9 種兩邊都沒有，而這支稽核當時照樣印「全部通過」：
    //    有欄位不等於有內容，稽核要問的是規定本身，不是欄位存在與否。
    if (actual.length && !(d.support || []).length && !d.own_judgment) {
      problems.push(`${slug}: 有 actual ${actual.join('/')} 卻既無 support 也沒標 own_judgment`)
    }
    // 只在「自行判斷**而且真的掛了代號**」時要求寫得出依據。
    // actual 留空的 own_judgment 是「材料不足、決定不填」，那一句話就說得完。
    if (d.own_judgment && actual.length && (d.rationale || '').length < 40) {
      problems.push(`${slug}: 掛了 ${actual.join('/')} 又標 own_judgment，但 rationale 只有 ${(d.rationale || '').length} 字`)
    }
    const nta = d.NTA || '(未分類)'
    byNTA[nta] = (byNTA[nta] || 0) + 1
  }
  console.log(`${label.padEnd(8)} ${String(n).padStart(3)} 種`)
}

console.log(`\n合計 ${total} 種`)
console.log(`  站上有全文      ${withContent} / ${total}　（其中 ${xref} 種全文在 /gnostic 不在 /apocrypha）`)
console.log(`  仍無全文        ${noText.length}：${noText.join('、') || '無'}`)
console.log(`  本表自行判斷    ${ownJudgment}`)
console.log(`  actual 留空     ${emptyActual}（材料不足，已於 rationale 說明）`)
console.log(`  逾 325 只列不計  ${beyond}`)

console.log('\nNTA 分類分佈：')
for (const [k, v] of Object.entries(byNTA).sort((a, b) => b[1] - a[1])) console.log(`  ${String(v).padStart(3)} ${k}`)

console.log('\n代號出現次數（attributed ＋ actual）：')
for (const [k, v] of Object.entries(trajCount).sort((a, b) => b[1] - a[1])) console.log(`  ${String(v).padStart(3)} ${k}`)

if (problems.length) {
  console.log(`\n✗ ${problems.length} 項問題：`)
  for (const p of problems) console.log('   ' + p)
  process.exit(1)
}
console.log('\n✓ 全部通過（欄位齊、代號查得到、書目引得到、留空皆有說明）')
