// One-off audit of the episcopal graph snapshot:
//  - completeness (orphan branches, see=null spines)
//  - attach sanity (parent_bishop_id resolves to a real, tenure-covering bishop)
//  - chronology (bishop chains monotonic by start_year)
//  - splits (is_split inventory for the equal-fork redesign)
import { readFileSync, writeFileSync } from 'node:fs'

const g = JSON.parse(readFileSync('test/genealogy/fixtures/snapshots/episcopal.json', 'utf8'))
const out = []
const log = (s = '') => out.push(s)

// ── index every bishop by id (across spines, branches, apostolicBranches) ──
const bishopById = new Map()
const bishopOwner = new Map() // bishopId -> chain label
function idx(bishops, label) {
  for (const b of bishops ?? []) { bishopById.set(b.id, b); bishopOwner.set(b.id, label) }
}
for (const sp of g.spines) idx(sp.bishops, `spine:${sp.key}`)
for (const br of g.branches) idx(br.bishops, `branch:${br.see_zh}|${br.church}`)
for (const ab of (g.apostolicBranches ?? [])) idx(ab.bishops, `apo:${ab.see_zh}`)

const totalBishops = bishopById.size
log(`=== TOTALS ===`)
log(`spines=${g.spines.length} branches=${g.branches.length} apostolicBranches=${(g.apostolicBranches ?? []).length} apostles=${g.apostles.length}`)
log(`unique bishop ids across all chains = ${totalBishops}`)
const sumBishops = g.spines.reduce((s, x) => s + x.bishops.length, 0)
  + g.branches.reduce((s, x) => s + x.bishops.length, 0)
  + (g.apostolicBranches ?? []).reduce((s, x) => s + x.bishops.length, 0)
log(`sum of bishops[] entries = ${sumBishops}  (duplicates across chains = ${sumBishops - totalBishops})`)

// ── spines with see=null ──
log(`\n=== SPINES ===`)
for (const sp of g.spines) {
  log(`  ${sp.key}: see=${sp.see ? sp.see.see_zh : 'NULL ⚠'} bishops=${sp.bishops.length} apostle=${sp.primaryApostleId ? 'y' : 'n'}`)
}

// ── orphan / attach audit for branches ──
function auditAttach(list, kind) {
  let nullParent = 0, missingAnchor = 0, futureAnchor = 0, predecessor = 0, covering = 0
  const problems = []
  for (const br of list) {
    const isDepth0Apostolic = kind === 'apo' && br.parent_apostle_id
    const pid = br.parent_bishop_id
    if (isDepth0Apostolic) { covering++; continue } // attaches to apostle card by design
    if (!pid) { nullParent++; problems.push(`⚠NULL: ${br.see_zh}|${br.church} (founded ${br.founded_year}, split=${br.is_split})`); continue }
    const anchor = bishopById.get(pid)
    if (!anchor) { missingAnchor++; problems.push(`⚠MISSING-ANCHOR: ${br.see_zh}|${br.church} → ${pid}`); continue }
    const y = br.founded_year
    if (y != null && anchor.start_year != null) {
      if (anchor.start_year > y) { futureAnchor++; problems.push(`⚠FUTURE-ANCHOR(年代錯亂): ${br.see_zh}|${br.church} founded ${y} → [${anchor.name_zh} starts ${anchor.start_year}] in ${bishopOwner.get(pid)}`) }
      else if (anchor.end_year == null || anchor.end_year >= y) covering++   // tenure covers
      else predecessor++   // attaches to nearest prior bishop (acceptable)
    } else covering++
  }
  log(`\n=== ATTACH AUDIT (${kind}) — n=${list.length} ===`)
  log(`  covering=${covering}  predecessor(ok)=${predecessor}  nullParent=${nullParent}  missingAnchor=${missingAnchor}  FUTURE-ANCHOR=${futureAnchor}`)
  for (const p of problems.slice(0, 40)) log(`   • ${p}`)
  if (problems.length > 40) log(`   …(+${problems.length - 40} more)`)
}
auditAttach(g.branches, 'branch')
auditAttach(g.apostolicBranches ?? [], 'apo')

// ── chronology: each chain's bishops monotonic non-decreasing by start_year ──
log(`\n=== CHRONOLOGY (non-monotonic start_year within a chain) ===`)
let chrono = 0
function checkChrono(bishops, label) {
  let prev = -Infinity, prevName = ''
  for (const b of bishops) {
    if (b.start_year == null) continue
    if (b.start_year < prev - 0) {
      chrono++
      if (chrono <= 40) log(`   • ${label}: ${prevName}(${prev}) → ${b.name_zh}(${b.start_year}) goes BACKWARD`)
    }
    prev = b.start_year; prevName = b.name_zh
  }
}
for (const sp of g.spines) checkChrono(sp.bishops, `spine:${sp.key}`)
for (const br of g.branches) checkChrono(br.bishops, `branch:${br.see_zh}|${br.church}`)
for (const ab of (g.apostolicBranches ?? [])) checkChrono(ab.bishops, `apo:${ab.see_zh}`)
log(`  total non-monotonic steps = ${chrono}`)

// ── splits inventory ──
log(`\n=== SPLIT (is_split) INVENTORY ===`)
const splits = g.branches.filter(b => b.is_split)
log(`  branch splits = ${splits.length} / ${g.branches.length}`)
// group splits by see_zh to see "same chair, N rival lines"
const bySee = new Map()
for (const b of g.branches) {
  if (!bySee.has(b.see_zh)) bySee.set(b.see_zh, [])
  bySee.get(b.see_zh).push(b)
}
log(`  sees that have >=1 split rival (chair contested):`)
for (const [see, arr] of bySee) {
  const sp = arr.filter(b => b.is_split)
  if (sp.length) log(`   • ${see}: ${sp.length} split rival(s) + ${arr.length - sp.length} non-split daughter(s) → ${sp.map(b => `${b.church}(${b.founded_year})`).join(', ')}`)
}

// ── diagnose null-parent root cause: does the PARENT see have a covering bishop? ──
// map see-id -> {see_zh, bishops[]}
const seeById = new Map()
for (const sp of g.spines) if (sp.see) seeById.set(sp.see.id, { see_zh: sp.see.see_zh, bishops: sp.bishops, kind: 'spine' })
for (const br of g.branches) seeById.set(br.id, { see_zh: br.see_zh, bishops: br.bishops, kind: 'branch' })
for (const ab of (g.apostolicBranches ?? [])) seeById.set(ab.id, { see_zh: ab.see_zh, bishops: ab.bishops, kind: 'apo' })

function parentHasCovering(parentSeeId, year) {
  const p = seeById.get(parentSeeId)
  if (!p) return { state: 'PARENT-SEE-MISSING', detail: parentSeeId }
  if (year == null) return { state: 'NO-YEAR' }
  const covering = p.bishops.find(b => b.start_year != null && b.start_year <= year && (b.end_year == null || b.end_year >= year))
  if (covering) return { state: 'PARENT-HAS-COVERING (lookup bug?)', detail: `${p.see_zh}: ${covering.name_zh} ${covering.start_year}-${covering.end_year}` }
  const any = p.bishops.length
  return { state: any ? 'PARENT-NO-COVERING-BISHOP (gap)' : 'PARENT-HAS-NO-BISHOPS', detail: `${p.see_zh} has ${any} bishops` }
}

log(`\n=== NULL-PARENT ROOT CAUSE (branches) ===`)
const causes = new Map()
for (const br of g.branches) {
  if (br.parent_bishop_id) continue
  const r = parentHasCovering(br.parent_see_id, br.founded_year)
  causes.set(r.state, (causes.get(r.state) ?? 0) + 1)
}
for (const [k, v] of [...causes].sort((a, b) => b[1] - a[1])) log(`  ${k}: ${v}`)
log(`  — samples —`)
let shown = 0
for (const br of g.branches) {
  if (br.parent_bishop_id || shown >= 25) continue
  const r = parentHasCovering(br.parent_see_id, br.founded_year)
  log(`   • ${br.see_zh}|${br.church} (founded ${br.founded_year}) → ${r.state} ${r.detail ? '['+r.detail+']' : ''}`)
  shown++
}

writeFileSync('C:/tmp/episcopal_audit.txt', out.join('\n'))
console.error(out.join('\n'))
