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
  split_year: number | null
  founder_apostle_id: string | null   // 使徒源頭：當設定時表示「這個教座由某使徒直接建立」，渲染時掛在使徒底下而非 spine
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
  consecrator_bishop_id: string | null   // 按立者 UUID（跨教座按立鏈用）
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

// `primaryChurches` is for continuous time-sequential succession (e.g.
//   羅馬: 未分裂教會 → 天主教 is one chronological line, no overlap).
// `rivalChurches` is for parallel rival successions that split off and
//   should be rendered as a separate split branch, NOT merged into the spine
//   (e.g. 東方教會（亞述） split from 古代東方教會 in 1968 — both exist today).
// `rivalSplitYear` filters rival bishops to those AFTER the split, suppressing
//   pre-split duplicates (e.g. 科普特正教 DB has full 42-present list but
//   pre-451 entries duplicate 未分裂教會 — we only want post-Chalcedon ones).
// `patriarchateYear` = 該 spine 正式建立宗主教座 / Catholicosate 的年份。
// 此年份前 spine 線細，此年份後 spine 線粗（前端 render 時切兩段）。
//   - 五大宗主教座（羅馬/君士坦丁堡/亞歷山卓/安提阿/耶路撒冷）= 451（迦克墩會議 Canon 28 確立 Pentarchy）
//   - 埃奇米亞津 = 484（Edict of Vahan Mamikonian 確立 Catholicosate）
//   - 塞琉西亞-泰西封 = 410（Mar Isaac 主教會議確立 Catholicos）
const SPINE_DEFS: Array<{
  key: SpineKey
  see_zh: string
  primaryChurches: string[]
  rivalChurches?: string[]
  rivalSplitYear?: number
  primaryApostleId: string
  secondaryApostleId?: string
  color: string
  patriarchateYear: number
}> = [
  { key: 'rome',           see_zh: '羅馬',           primaryChurches: ['未分裂教會', '天主教'],
    primaryApostleId: 'ap_peter', secondaryApostleId: 'ap_paul',         color: '#dc2626', patriarchateYear: 451 },
  { key: 'constantinople', see_zh: '君士坦丁堡',     primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_andrew',                                        color: '#2563eb', patriarchateYear: 451 },
  { key: 'alexandria',     see_zh: '亞歷山卓',       primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_peter', secondaryApostleId: 'ap_barnabas',     color: '#d97706', patriarchateYear: 451 },
  { key: 'antioch',        see_zh: '安提阿',         primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_peter',                                         color: '#0891b2', patriarchateYear: 451 },
  { key: 'jerusalem',      see_zh: '耶路撒冷',       primaryChurches: ['未分裂教會', '東正教'],
    primaryApostleId: 'ap_james_just',                                    color: '#16a34a', patriarchateYear: 451 },
  { key: 'armenia',        see_zh: '埃奇米亞津',     primaryChurches: ['亞美尼亞使徒教會'],
    primaryApostleId: 'ap_thaddaeus', secondaryApostleId: 'ap_bartholomew', color: '#9333ea', patriarchateYear: 484 },
  { key: 'assyria',        see_zh: '塞琉西亞—泰西封', primaryChurches: ['古代東方教會'],
    rivalChurches: ['東方教會（亞述）'],
    primaryApostleId: 'ap_thomas',                                        color: '#475569', patriarchateYear: 410 },
]

export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  // 1. all sees
  const { data: seeRows, error: seeErr } = await supabase
    .from('episcopal_sees')
    .select('id, see_zh, name_zh, name_en, church, tradition, founded_year, parent_see_id, split_year, founder_apostle_id')
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
      .select('id, name_zh, name_en, see, church, succession_number, start_year, end_year, appointed_by, consecrator_bishop_id, status, notes')
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
    // Dedupe: same bishop may appear under multiple "churches" with different
    // Chinese translations (e.g. 亞歷山卓 #24 is 聖息羅一世 in 未分裂教會 but
    // 聖濟利祿一世 in 東正教 — both = Cyril of Alexandria, 412 AD).
    // Use (succession_number, start_year) as dedupe key when succession_number
    // is set; fall back to name+year otherwise.
    const bishopMergeMap = new Map<string, SuccRow>()
    for (const church of def.primaryChurches) {
      const list = bishopsBySeeChurch.get(`${def.see_zh}|${church}`) ?? []
      for (const b of list) {
        const key = b.succession_number != null
          ? `n${b.succession_number}|${b.start_year ?? ''}`
          : `z${b.name_zh}|${b.start_year ?? ''}`
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
      patriarchateYear: def.patriarchateYear,
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
        // Negative succession_number signals pre-canonical / pre-Catholicos tradition
        // (e.g. 亞美尼亞使徒寶座 8 位 #-8..#-1 排在格利高爾 #1 之前). Hide the number
        // on the card; the natural sort puts them in correct order.
        succession_number: (b.succession_number != null && b.succession_number > 0) ? b.succession_number : null,
        start_year: b.start_year,
        end_year: b.end_year,
        appointed_by: b.appointed_by,
        consecrator_bishop_id: b.consecrator_bishop_id,
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
      succession_number: (b.succession_number != null && b.succession_number > 0) ? b.succession_number : null,
      start_year: b.start_year,
      end_year: b.end_year,
      appointed_by: b.appointed_by,
      consecrator_bishop_id: b.consecrator_bishop_id,
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

  // ⚠ Critical: when a parent see is reused by a daughter (e.g. 坎特伯里|天主教 → 坎特伯里|英格蘭教會
  // both with see_zh="坎特伯里"), looking up bishops "by see_zh only" pulls the daughter's bishops
  // into the candidate pool and the wrong attach point is returned. Pass the parent's actual
  // church list (for spines: primaryChurches; for branches: [branch.church]) to restrict scope.
  function findBishopAtYear(seeRow: SeeRow, year: number | null, churchFilter?: string[]): string | null {
    if (year == null) return null
    const churches = churchFilter ?? [seeRow.church]
    const candidates: SuccRow[] = []
    for (const ch of churches) {
      const arr = bishopsBySeeChurch.get(`${seeRow.see_zh}|${ch}`) ?? []
      candidates.push(...arr)
    }
    let best: SuccRow | null = null
    for (const b of candidates) {
      if (b.start_year != null && b.start_year <= year && (b.end_year == null || b.end_year >= year)) {
        if (!best || (b.start_year > (best.start_year ?? -99999))) best = b
      }
    }
    return best?.id ?? null
  }

  // Spine see id → primary churches list (for cross-church bishop lookups along spine line)
  const spineSeeChurches = new Map<string, string[]>()
  for (let i = 0; i < SPINE_DEFS.length; i++) {
    const def = SPINE_DEFS[i]
    const sp = spines[i]
    if (sp.see) spineSeeChurches.set(sp.see.id, def.primaryChurches)
  }

  const branches: BranchNode[] = []
  // BFS from each spine see — SKIP sees with founder_apostle_id（這些屬於 apostolic subtree）
  for (const sp of spines) {
    if (!sp.see) continue
    const queue: Array<{ seeId: string; spineKey: string }> = [{ seeId: sp.see.id, spineKey: sp.key }]
    const seen = new Set<string>([sp.see.id])
    while (queue.length) {
      const { seeId, spineKey } = queue.shift()!
      const kids = childrenOfSee.get(seeId) ?? []
      for (const k of kids) {
        if (seen.has(k.id)) continue
        if (k.founder_apostle_id) continue   // 跳過使徒源頭教座（會由 apostolic-branches collector 處理）
        seen.add(k.id)
        const parentSee = seeById.get(seeId)!
        // Use split_year (if set) as the attach point — that's the moment the rival
        // line diverged. Otherwise use founded_year.
        const attachYear = k.split_year ?? k.founded_year
        // 如果 parent 是 spine see，跨多個 church（如 rome = 未分裂教會 + 天主教）
        // 否則只看 parent 自己的 church（避免 see_zh 相同的 daughter 攪進來）
        const parentChurches = spineSeeChurches.get(seeId) ?? [parentSee.church]
        const parentBishopId = findBishopAtYear(parentSee, attachYear, parentChurches)
        // gather bishops for this branch see (across all churches it carries)
        let allBishops: SuccRow[] = []
        for (const [bk, arr] of bishopsBySeeChurch.entries()) {
          const [seeName, ch] = bk.split('|')
          if (seeName === k.see_zh && ch === k.church) allBishops.push(...arr)
        }
        // If this branch see has split_year (e.g. 451 for Coptic Orthodox split from
        // Alexandria), drop pre-split bishops — they're duplicates of primary line.
        if (k.split_year != null) {
          allBishops = allBishops.filter(b => (b.start_year ?? 9999) >= k.split_year!)
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
          // For split branches show the split year (more informative than ancient see founding)
          founded_year: k.split_year ?? k.founded_year,
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

  // 5b. Synthetic split branches for `rivalChurches` (e.g. 東方教會（亞述） vs 古代東方教會 in assyria spine)
  //    These are parallel-existing rival successions on the same see_zh that must NOT be merged
  //    into the spine line (would interleave by succession_number and look broken).
  for (const def of SPINE_DEFS) {
    if (!def.rivalChurches || def.rivalChurches.length === 0) continue
    const sp = spines.find(s => s.key === def.key)
    if (!sp || !sp.see) continue

    for (const rivalChurch of def.rivalChurches) {
      let rivalBishopRows = bishopsBySeeChurch.get(`${def.see_zh}|${rivalChurch}`) ?? []
      // If rivalSplitYear is set, filter out pre-split bishops (they're duplicates
      // of primary line, e.g. 科普特正教 DB has full 42-present list but pre-451
      // entries duplicate 未分裂教會).
      if (def.rivalSplitYear != null) {
        rivalBishopRows = rivalBishopRows.filter(b => (b.start_year ?? 9999) >= def.rivalSplitYear!)
      }
      if (rivalBishopRows.length === 0) continue

      // Find a see row for this (see_zh, church) pair to use as the branch identity.
      // If none exists, synthesize an id from the rivalChurch name.
      const rivalSee = sees.find(s => s.see_zh === def.see_zh && s.church === rivalChurch)
      const branchId = rivalSee?.id ?? `synth_${def.key}_${rivalChurch}`

      // The split year = the earliest year this rival has its own succession.
      // Prefer the explicit rivalSplitYear or first remaining bishop's start_year.
      const foundedYear = def.rivalSplitYear ?? (rivalBishopRows[0]?.start_year ?? null) ?? rivalSee?.founded_year ?? null
      // Spine 的 rival 從 spine primaryChurches 找 parent bishop
      const parentBishopId = findBishopAtYear(sp.see as SeeRow, foundedYear, def.primaryChurches)

      branches.push({
        id: branchId,
        see_zh: def.see_zh,
        name_zh: rivalSee?.name_zh ?? rivalChurch,
        name_en: rivalSee?.name_en ?? null,
        church: rivalChurch,
        tradition: rivalSee?.tradition ?? '',
        founded_year: foundedYear,
        parent_see_id: sp.see.id,
        parent_spine_key: sp.key,
        parent_bishop_id: parentBishopId,
        is_split: true,
        bishops: rivalBishopRows.map(mapBishop),
      })
    }
  }

  // ── 5c. Apostolic branches — 使徒源頭教座，掛在 apostle card 下，預設收起 ──
  // 凡 founder_apostle_id 有設定的 see，連同其子樹一起放到 apostolicBranches[apostleId]
  // 內部結構與 spine branches 一樣 (parent_bishop_id, is_split, bishops...) 但 parent 是
  // 「使徒」概念而非 spine bishop —— 渲染時 attach 點 = 使徒卡片底部
  interface ApostolicBranch extends BranchNode {
    parent_apostle_id: string | null   // 直接掛在某 apostle 底下時設定（depth-0），子座為 null
  }
  const apostolicBranches: ApostolicBranch[] = []
  const apostolicRoots = sees.filter(s => s.founder_apostle_id)
  for (const root of apostolicRoots) {
    // BFS from this apostolic root (root + descendants)
    const queue: Array<{ seeId: string; depth: number }> = [{ seeId: root.id, depth: 0 }]
    const seen = new Set<string>()
    while (queue.length) {
      const { seeId, depth } = queue.shift()!
      if (seen.has(seeId)) continue
      seen.add(seeId)
      const see = seeById.get(seeId)
      if (!see) continue

      // Gather bishops for this see
      let allBishops: SuccRow[] = []
      for (const [bk, arr] of bishopsBySeeChurch.entries()) {
        const [seeName, ch] = bk.split('|')
        if (seeName === see.see_zh && ch === see.church) allBishops.push(...arr)
      }
      if (see.split_year != null) {
        allBishops = allBishops.filter(b => (b.start_year ?? 9999) >= see.split_year!)
      }
      allBishops.sort((a, b) => {
        const an = a.succession_number ?? 9999
        const bn = b.succession_number ?? 9999
        if (an !== bn) return an - bn
        return (a.start_year ?? 9999) - (b.start_year ?? 9999)
      })

      // Determine parent for visual: depth-0 → apostle card; deeper → parent_bishop_id in parent see
      let parentBishopId: string | null = null
      let isSplit = false
      if (depth > 0 && see.parent_see_id) {
        const parentSee = seeById.get(see.parent_see_id)
        if (parentSee) {
          const attachYear = see.split_year ?? see.founded_year
          parentBishopId = findBishopAtYear(parentSee, attachYear, [parentSee.church])
          isSplit = see.see_zh === parentSee.see_zh
        }
      }

      apostolicBranches.push({
        id: see.id,
        see_zh: see.see_zh,
        name_zh: see.name_zh,
        name_en: see.name_en,
        church: see.church,
        tradition: see.tradition,
        founded_year: see.split_year ?? see.founded_year,
        parent_see_id: see.parent_see_id ?? root.id,
        parent_spine_key: '',     // apostolic branches don't belong to a spine
        parent_bishop_id: parentBishopId,
        is_split: isSplit,
        bishops: allBishops.map(mapBishop),
        parent_apostle_id: depth === 0 ? root.founder_apostle_id : null,
      } as ApostolicBranch)

      for (const k of (childrenOfSee.get(seeId) ?? [])) {
        if (!seen.has(k.id)) queue.push({ seeId: k.id, depth: depth + 1 })
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
    apostolicBranches,
    teachings: teachingRows ?? [],
  }
})
