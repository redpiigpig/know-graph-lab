/**
 * Episcopal apostolic-succession graph
 *
 * Topology (per user spec):
 *   耶穌基督 (root)
 *     └── 16 使徒 (apostle row)
 *           └── 5 大宗主教座 (spine columns: 羅馬 / 安提阿 / 君士坦丁堡 / 亞歷山大 / 耶路撒冷)
 *                 └── 主教鏈 (bishops in succession_number order)
 *                       └── 旁支主教座 (branch sees with parent_see_id pointing into a spine)
 *
 * No marriage edges — only succession (parent-child along the spine + spawn for branches).
 */

interface SeeRow {
  id: string
  see_zh: string
  name_zh: string
  name_en: string | null
  church: string
  tradition: string
  founded_year: number | null
  parent_see_id: string | null
}

interface SuccRow {
  id: string
  name_zh: string
  name_en: string | null
  see: string
  church: string | null
  succession_number: number | null
  start_year: number | null
  end_year: number | null
  appointed_by: string | null
  status: string
  notes: string | null
}

// ── 16 apostles ───────────────────────────────────────────────────────
//
// Order: 12 主使徒 + 義人雅各 + 主弟猶大 + 巴拿巴 + 保羅
// `founderOfSeeKey` 對應到下方 SPINES key（只有 5 位是 5 大宗主教座的開創者）
const APOSTLES: Array<{
  id: string
  name_zh: string
  name_en: string
  notes?: string
}> = [
  { id: 'ap_peter',       name_zh: '彼得',           name_en: 'Peter' },
  { id: 'ap_andrew',      name_zh: '安得烈',         name_en: 'Andrew' },
  { id: 'ap_james_zeb',   name_zh: '雅各（西庇太之子）', name_en: 'James, son of Zebedee' },
  { id: 'ap_john',        name_zh: '約翰',           name_en: 'John' },
  { id: 'ap_philip',      name_zh: '腓力',           name_en: 'Philip' },
  { id: 'ap_bartholomew', name_zh: '巴多羅買',       name_en: 'Bartholomew' },
  { id: 'ap_matthew',     name_zh: '馬太',           name_en: 'Matthew' },
  { id: 'ap_thomas',      name_zh: '多馬',           name_en: 'Thomas' },
  { id: 'ap_james_alph',  name_zh: '雅各（亞勒腓之子）', name_en: 'James, son of Alphaeus' },
  { id: 'ap_thaddaeus',   name_zh: '達太',           name_en: 'Thaddaeus / Jude of James' },
  { id: 'ap_simon_zeal',  name_zh: '西門（奮銳黨）', name_en: 'Simon the Zealot' },
  { id: 'ap_matthias',    name_zh: '馬提亞',         name_en: 'Matthias' },
  { id: 'ap_james_just',  name_zh: '義人雅各',       name_en: 'James the Just' },
  { id: 'ap_jude_lord',   name_zh: '猶大（主弟）',   name_en: 'Jude, brother of the Lord' },
  { id: 'ap_barnabas',    name_zh: '巴拿巴',         name_en: 'Barnabas' },
  { id: 'ap_paul',        name_zh: '保羅',           name_en: 'Paul' },
]

// ── 7 大宗主教座 ───────────────────────────────────────────────────────
//
// Per user spec (5→7 spines)：每個 spine 可有 1 個主使徒 + 可選 1 個輔使徒：
//   羅馬       彼得 (主) + 保羅 (輔)
//   君士坦丁堡 安得烈
//   亞歷山大   彼得 (主，派遣馬可) + 巴拿巴 (輔)
//   安提阿     彼得
//   耶路撒冷   義人雅各
//   亞美尼亞   達太 (Thaddaeus + Bartholomew tradition；以 達太 為主)
//   亞述       多馬
type SpineKey = 'rome' | 'constantinople' | 'alexandria' | 'antioch' | 'jerusalem' | 'armenia' | 'assyria'

const SPINE_DEFS: Array<{
  key: SpineKey
  see_zh: string
  primaryChurches: string[]
  primaryApostleId: string
  secondaryApostleId?: string
  color: string
}> = [
  { key: 'rome',           see_zh: '羅馬',           primaryChurches: ['未分裂教會', '天主教'],
    primaryApostleId: 'ap_peter', secondaryApostleId: 'ap_paul',         color: '#dc2626' },
  { key: 'constantinople', see_zh: '君士坦丁堡',     primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_andrew',                                        color: '#2563eb' },
  { key: 'alexandria',     see_zh: '亞歷山卓',       primaryChurches: ['未分裂教會', '東正教', '科普特正教'],
    primaryApostleId: 'ap_peter', secondaryApostleId: 'ap_barnabas',     color: '#d97706' },
  { key: 'antioch',        see_zh: '安提阿',         primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_peter',                                         color: '#0891b2' },
  { key: 'jerusalem',      see_zh: '耶路撒冷',       primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_james_just',                                    color: '#16a34a' },
  { key: 'armenia',        see_zh: '埃奇米亞津',     primaryChurches: ['亞美尼亞使徒教會'],
    primaryApostleId: 'ap_thaddaeus', secondaryApostleId: 'ap_bartholomew', color: '#9333ea' },
  { key: 'assyria',        see_zh: '塞琉西亞—泰西封', primaryChurches: ['古代東方教會', '東方教會（亞述）'],
    primaryApostleId: 'ap_thomas',                                        color: '#475569' },
]

export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  // 1. all sees
  const { data: seeRows, error: seeErr } = await supabase
    .from('episcopal_sees')
    .select('id, see_zh, name_zh, name_en, church, tradition, founded_year, parent_see_id')
  if (seeErr) throw createError({ statusCode: 500, message: seeErr.message })

  const sees: SeeRow[] = seeRows ?? []
  const seeById = new Map<string, SeeRow>()
  for (const s of sees) seeById.set(s.id, s)

  // 2. all bishops (we'll filter to relevant sees only)
  // Supabase defaults to a 1000-row cap; episcopal_succession has 3000+ rows
  // (e.g. Pope Gregory I at #64 was getting cut off). Page through in 1000-row chunks.
  const succ: SuccRow[] = []
  for (let from = 0; ; from += 1000) {
    const { data: page, error: pageErr } = await supabase
      .from('episcopal_succession')
      .select('id, name_zh, name_en, see, church, succession_number, start_year, end_year, appointed_by, status, notes')
      .range(from, from + 999)
    if (pageErr) throw createError({ statusCode: 500, message: pageErr.message })
    if (!page || page.length === 0) break
    succ.push(...page)
    if (page.length < 1000) break
  }

  // 3. group bishops by (see + church)
  const bishopsBySeeChurch = new Map<string, SuccRow[]>()
  for (const b of succ) {
    const key = `${b.see}|${b.church ?? ''}`
    if (!bishopsBySeeChurch.has(key)) bishopsBySeeChurch.set(key, [])
    bishopsBySeeChurch.get(key)!.push(b)
  }
  for (const arr of bishopsBySeeChurch.values()) {
    arr.sort((a, b) => {
      const an = a.succession_number ?? 9999
      const bn = b.succession_number ?? 9999
      if (an !== bn) return an - bn
      return (a.start_year ?? 9999) - (b.start_year ?? 9999)
    })
  }

  // 4. pick spine sees & their bishops
  const spineSeeIds = new Set<string>()
  const spines = SPINE_DEFS.map(def => {
    // pick the main see record (prefer 未分裂教會 / 天主教 / 東正教 — tradition independent)
    const candidateSees = sees.filter(s => s.see_zh === def.see_zh)
    const main = candidateSees.find(s => def.primaryChurches.includes(s.church))
              ?? candidateSees[0]
    if (main) spineSeeIds.add(main.id)

    // gather all bishops for this see across all primaryChurches.
    // Dedupe: a bishop with the same (name_zh, start_year) appearing under
    // multiple "churches" (e.g. 聖馬爾谷 in both 未分裂教會 and 科普特正教)
    // is the same person — keep one (prefer 未分裂教會, else lowest succession_number).
    const bishopMergeMap = new Map<string, SuccRow>()
    for (const church of def.primaryChurches) {
      const list = bishopsBySeeChurch.get(`${def.see_zh}|${church}`) ?? []
      for (const b of list) {
        const key = `${b.name_zh}|${b.start_year ?? ''}`
        const prev = bishopMergeMap.get(key)
        if (!prev) {
          bishopMergeMap.set(key, b)
        } else {
          // Prefer the one with church=未分裂教會, else the one with succession_number set
          const prevPriority = (prev.church === '未分裂教會' ? 0 : 1)
                             + (prev.succession_number == null ? 1 : 0)
          const newPriority  = (b.church === '未分裂教會' ? 0 : 1)
                             + (b.succession_number == null ? 1 : 0)
          if (newPriority < prevPriority) bishopMergeMap.set(key, b)
        }
      }
    }
    const bishops = Array.from(bishopMergeMap.values())
    bishops.sort((a, b) => {
      const an = a.succession_number ?? 9999
      const bn = b.succession_number ?? 9999
      if (an !== bn) return an - bn
      return (a.start_year ?? 9999) - (b.start_year ?? 9999)
    })

    return {
      key: def.key,
      primaryApostleId: def.primaryApostleId,
      secondaryApostleId: def.secondaryApostleId ?? null,
      color: def.color,
      see: main ? {
        id: main.id,
        see_zh: main.see_zh,
        name_zh: main.name_zh,
        name_en: main.name_en,
        church: main.church,
        tradition: main.tradition,
        founded_year: main.founded_year,
      } : null,
      bishops: bishops.map(b => ({
        id: b.id,
        name_zh: b.name_zh,
        name_en: b.name_en,
        succession_number: b.succession_number,
        start_year: b.start_year,
        end_year: b.end_year,
        appointed_by: b.appointed_by,
        church: b.church,
        status: b.status,
        notes: b.notes,
      })),
    }
  })

  // 5. branch sees: any see whose parent_see_id is in spine OR (recursively) in another branch
  //    we'll do a BFS from spine see ids, collecting parent→children in episcopal_sees tree
  type BranchNode = {
    id: string
    see_zh: string
    name_zh: string
    name_en: string | null
    church: string
    tradition: string
    founded_year: number | null
    parent_see_id: string | null
    parent_spine_key: string  // root spine key
    parent_bishop_id: string | null  // bishop in the parent see whose tenure includes founded_year
    bishops: ReturnType<typeof mapBishop>[]
  }
  function mapBishop(b: SuccRow) {
    return {
      id: b.id,
      name_zh: b.name_zh,
      name_en: b.name_en,
      succession_number: b.succession_number,
      start_year: b.start_year,
      end_year: b.end_year,
      appointed_by: b.appointed_by,
      church: b.church,
      status: b.status,
      notes: b.notes,
    }
  }

  const childrenOfSee = new Map<string, SeeRow[]>()
  for (const s of sees) {
    if (s.parent_see_id) {
      if (!childrenOfSee.has(s.parent_see_id)) childrenOfSee.set(s.parent_see_id, [])
      childrenOfSee.get(s.parent_see_id)!.push(s)
    }
  }
  // sort children by founded_year
  for (const arr of childrenOfSee.values()) {
    arr.sort((a, b) => (a.founded_year ?? 9999) - (b.founded_year ?? 9999))
  }

  // map see id → spine key (only for spine sees)
  const spineKeyBySeeId = new Map<string, string>()
  for (const sp of spines) {
    if (sp.see) spineKeyBySeeId.set(sp.see.id, sp.key)
  }

  function findBishopAtYear(seeRow: SeeRow, year: number | null): string | null {
    if (year == null) return null
    // find bishop in seeRow whose [start_year, end_year] contains year, in any church
    const candidates: SuccRow[] = []
    for (const [k, arr] of bishopsBySeeChurch.entries()) {
      const [seeName] = k.split('|')
      if (seeName === seeRow.see_zh) candidates.push(...arr)
    }
    let best: SuccRow | null = null
    for (const b of candidates) {
      if (b.start_year != null && b.start_year <= year && (b.end_year == null || b.end_year >= year)) {
        if (!best || (b.start_year > (best.start_year ?? -99999))) best = b
      }
    }
    return best?.id ?? null
  }

  const branches: BranchNode[] = []
  // BFS from each spine see
  for (const sp of spines) {
    if (!sp.see) continue
    const queue: Array<{ seeId: string; spineKey: string }> = [{ seeId: sp.see.id, spineKey: sp.key }]
    const seen = new Set<string>([sp.see.id])
    while (queue.length) {
      const { seeId, spineKey } = queue.shift()!
      const kids = childrenOfSee.get(seeId) ?? []
      for (const k of kids) {
        if (seen.has(k.id)) continue
        seen.add(k.id)
        const parentSee = seeById.get(seeId)!
        const parentBishopId = findBishopAtYear(parentSee, k.founded_year)
        // gather bishops for this branch see (across all churches it carries)
        const allBishops: SuccRow[] = []
        for (const [bk, arr] of bishopsBySeeChurch.entries()) {
          const [seeName, ch] = bk.split('|')
          if (seeName === k.see_zh && ch === k.church) allBishops.push(...arr)
        }
        allBishops.sort((a, b) => {
          const an = a.succession_number ?? 9999
          const bn = b.succession_number ?? 9999
          if (an !== bn) return an - bn
          return (a.start_year ?? 9999) - (b.start_year ?? 9999)
        })
        // Per user spec: 教座分裂 (split) vs 設立教座 (founding)
        //   分裂 = daughter see has SAME see_zh as parent (rival successors claim the same chair).
        //   設立 = daughter see has DIFFERENT see_zh from parent (new see established).
        const parentSeeForSplit = seeById.get(seeId)
        const isSplit = parentSeeForSplit ? (k.see_zh === parentSeeForSplit.see_zh) : false

        branches.push({
          id: k.id,
          see_zh: k.see_zh,
          name_zh: k.name_zh,
          name_en: k.name_en,
          church: k.church,
          tradition: k.tradition,
          founded_year: k.founded_year,
          parent_see_id: seeId,
          parent_spine_key: spineKey,
          parent_bishop_id: parentBishopId,
          is_split: isSplit,
          bishops: allBishops.map(mapBishop),
        })
        queue.push({ seeId: k.id, spineKey })
      }
    }
  }

  // 6. teaching pairs (Jesus → disciples, Peter → Mark, John → Polycarp, Albertus → Aquinas, etc.)
  //    Returned as-is from church_teachings. The renderer decides whether to draw an
  //    orange teaching line based on whether both endpoints exist on canvas AND aren't
  //    already connected via institutional (spine/branch) chain.
  const { data: teachingRows } = await supabase
    .from('church_teachings')
    .select('id, teacher_name_zh, teacher_name_en, student_name_zh, student_name_en, period_year, relationship, source, notes, teacher_bishop_id, student_bishop_id')

  return {
    jesus: { id: 'jesus', name_zh: '耶穌基督', name_en: 'Jesus Christ' },
    apostles: APOSTLES,
    spines,
    branches,
    teachings: teachingRows ?? [],
  }
})
