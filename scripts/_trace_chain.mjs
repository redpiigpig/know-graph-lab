// Trace a branch see up to the spine, verifying each parent-bishop anchor exists.
// Usage: node scripts/_trace_chain.mjs "台北（衛理）|中華基督教衛理公會"
import { readFileSync } from 'node:fs'
const target = process.argv[2] ?? '台北（衛理）|中華基督教衛理公會'
const g = JSON.parse(readFileSync('test/genealogy/fixtures/snapshots/episcopal.json', 'utf8'))
const seeById = new Map(); const bishById = new Map()
for (const sp of g.spines) if (sp.see) { seeById.set(sp.see.id, { label: `脊柱·${sp.see.see_zh}`, parent_see: null, parent_bishop: null, bishops: sp.bishops, spine: true }); for (const b of sp.bishops) bishById.set(b.id, b) }
for (const br of [...g.branches, ...(g.apostolicBranches ?? [])]) { seeById.set(br.id, { label: `${br.see_zh}|${br.church}`, parent_see: br.parent_see_id, parent_bishop: br.parent_bishop_id, bishops: br.bishops, founded: br.founded_year }); for (const b of br.bishops) bishById.set(b.id, b) }
let id = null
for (const [k, s] of seeById) if (s.label === target) id = k
if (!id) { console.error('target see not found:', target); process.exit(1) }
console.error(`=== TRACE ${target} → 脊柱 ===`)
let guard = 0, broken = false
while (id && guard++ < 30) {
  const s = seeById.get(id); if (!s) { console.error('  ⚠ see missing:', id); broken = true; break }
  const f = s.bishops[0], l = s.bishops[s.bishops.length - 1]
  console.error(`▸ ${s.label}  [${s.bishops.length} 位: ${f?.name_zh}(${f?.start_year}) … ${l?.name_zh}(${l?.end_year ?? '在任'})]`)
  if (s.spine) { console.error('   └ 抵達脊柱頂 ✓'); break }
  if (!s.parent_see) { console.error('   └ ⚠⚠ parent_see = NULL（斷點）'); broken = true; break }
  const anchor = s.parent_bishop ? bishById.get(s.parent_bishop) : null
  console.error(`   └ 經 ${anchor ? anchor.name_zh + '(' + anchor.start_year + '-' + (anchor.end_year ?? '在任') + ')' : (s.parent_bishop ? '⚠錨點不在樹上' : '⚠NULL錨點→年份定位')} 上接`)
  id = s.parent_see
}
console.error(broken ? '\n結果：✗ 斷' : '\n結果：✓ 暢通')
