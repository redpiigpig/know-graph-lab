export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  // ── View-based tradition filter + conflict resolution ───────────────
  // 4 個 view 累進納入更多傳統人物 + JSONB 套用：
  //   protestant      : biblical + rabbinic + early_consensus（後者僅作為 SPINE_B
  //                     必經的 約亞敬/亞拿/蘇比 等 anchor；用橘色卡視覺區隔，無 JSONB）
  //   early_consensus : + orthodox 全部人物 + orthodox JSONB（Epiphanian view，
  //                     Jerome 393 前主流。orthodox-tagged 的撒羅米/亞西亞/呂底亞/
  //                     革羅罷-約瑟之弟 屬此觀點，在此 view 一併納入）
  //   orthodox        : 同 early_consensus（Eastern church 保留 Epiphanian view）
  //   catholic        : + catholic 全部人物 + catholic JSONB（Hieronymian view，
  //                     不含 orthodox-tagged 的「約瑟前妻」系列）
  // rabbinic 傳統人物永遠顯示（不衝突）。
  const q = getQuery(event)
  const viewRaw = String(q.view ?? 'protestant').toLowerCase()
  // apocrypha / rabbinic view = 聖經 protestant 視角，但 widget UI 用「次經主題」/
  // 「拉比主題」做為視覺強調入口；後端 tradition allowlist 與 JSONB merge 行為一致。
  const view: 'protestant' | 'catholic' | 'orthodox' | 'early_consensus' | 'apocrypha' | 'rabbinic' =
    viewRaw === 'catholic'        ? 'catholic' :
    viewRaw === 'orthodox'        ? 'orthodox' :
    viewRaw === 'early_consensus' ? 'early_consensus' :
    viewRaw === 'apocrypha'       ? 'apocrypha' :
    viewRaw === 'rabbinic'        ? 'rabbinic' :
                                    'protestant'

  const allowedTraditions = new Set<string>(['biblical', 'rabbinic', 'early_consensus', 'apocrypha'])
  if (view === 'early_consensus' || view === 'orthodox') allowedTraditions.add('orthodox')
  if (view === 'catholic') allowedTraditions.add('catholic')

  // Which tradition's JSONB to apply for conflict resolution
  // (early_consensus + orthodox both use orthodox merges = Epiphanian view)
  const mergeKey: 'catholic' | 'orthodox' | null =
    view === 'catholic'                                       ? 'catholic' :
    (view === 'orthodox' || view === 'early_consensus')       ? 'orthodox' :
                                                                null

  const { data: allPeople, error } = await supabase
    .from('biblical_people')
    .select('*')
    .order('birth_year', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!allPeople?.length) return { nodes: [], edges: [] }

  const people = allPeople.filter(p => allowedTraditions.has(p.tradition ?? 'biblical'))

  // Apply per-tradition JSONB merges based on selected view.
  // Track which children were ADDED via tradition_children → so we can tag those
  // parent-child edges with the matching tradition (for tradition-colored line rendering).
  const traditionAddedChildName = new Map<string, Map<string, string>>()  // parentId → childName → tradition
  for (const p of people) {
    if (!mergeKey) continue
    const addChildren = (p.tradition_children as Record<string, string> | null)?.[mergeKey]
    const addSpouse   = (p.tradition_spouse   as Record<string, string> | null)?.[mergeKey]
    const hideChildrenRaw = (p.tradition_hide_children as Record<string, string> | null)?.[mergeKey]
    if (addChildren) {
      const childNames = addChildren.split(/[,，、]/).map(s => s.trim()).filter(Boolean)
      let tmap = traditionAddedChildName.get(p.id)
      if (!tmap) { tmap = new Map(); traditionAddedChildName.set(p.id, tmap) }
      for (const cn of childNames) tmap.set(cn, mergeKey)
      p.children = p.children ? `${p.children}、${addChildren}` : addChildren
    }
    if (addSpouse) {
      p.spouse = p.spouse ? `${p.spouse}、${addSpouse}` : addSpouse
    }
    if (hideChildrenRaw && p.children) {
      const hideSet = new Set(hideChildrenRaw.split(/[,，、]/).map(s => s.trim()).filter(Boolean))
      p.children = p.children.split(/[,，、]/).map((s: string) => s.trim()).filter((s: string) => s && !hideSet.has(s)).join('、')
    }
  }

  const exactMap = new Map<string, string>()
  const baseMap  = new Map<string, string[]>()
  const idMap    = new Map<string, typeof people[0]>()

  for (const p of people) {
    exactMap.set(p.name_zh, p.id)
    idMap.set(p.id, p)
    const base = p.name_zh.split('（')[0].trim()
    const arr  = baseMap.get(base) ?? []
    arr.push(p.id)
    baseMap.set(base, arr)
  }

  function resolveId(raw: string, parentName?: string): string | null {
    const n = raw.trim()
    if (!n) return null
    if (exactMap.has(n)) return exactMap.get(n)!
    const base = n.split('（')[0].trim()
    const candidates = baseMap.get(n) ?? baseMap.get(base) ?? []
    if (!candidates.length) return null
    if (candidates.length === 1) return candidates[0]
    // Disambiguate: check if parent name appears in the candidate's parenthetical hint
    if (parentName) {
      const pBase = parentName.split('（')[0].trim()
      const hit = candidates.find(id => {
        const m = idMap.get(id)?.name_zh.match(/（(.+)）/)
        return m && (m[1].includes(pBase) || m[1].includes(parentName))
      })
      if (hit) return hit
    }
    return null
  }

  // ── Build parent→child adjacency for tribeCode propagation ────────────
  const childIdsOf = new Map<string, string[]>()
  for (const p of people) {
    if (!p.children) continue
    const kids: string[] = []
    for (const raw of p.children.split(/[,，、]/)) {
      const cid = resolveId(raw, p.name_zh)
      if (cid && cid !== p.id) kids.push(cid)
    }
    if (kids.length) childIdsOf.set(p.id, kids)
  }

  // ── tribeCode: derive from descent of Jacob's 12 sons (+ Joseph's split) ──
  // R/S/L/J/D/N/G/A/I/Z/B = 11 of Jacob's sons. Patriarch 約瑟 himself has no
  // code, but his sons 瑪拿西 / 以法蓮 anchor M and E.
  const TRIBE_SEEDS: Array<[string, string]> = [
    ['呂便', 'R'],         // Reuben
    ['流便', 'R'],         // alternative name
    ['西緬', 'S'],
    ['利未', 'L'],
    ['猶大', 'J'],
    ['但', 'D'],
    ['拿弗他利', 'N'],
    ['迦得', 'G'],
    ['亞設', 'A'],
    ['以薩迦', 'I'],
    ['西布倫', 'Z'],
    ['便雅憫', 'B'],
    ['瑪拿西（約瑟之子）', 'M'],
    ['以法蓮（約瑟之子）', 'E'],
  ]
  const tribeCode = new Map<string, string>()
  for (const [seedName, code] of TRIBE_SEEDS) {
    const seedId = exactMap.get(seedName)
    if (!seedId) continue
    // DFS downward, but skip nodes that already have a code (first-seed wins)
    const stack: string[] = [seedId]
    const visited = new Set<string>()
    while (stack.length) {
      const cur = stack.pop()!
      if (visited.has(cur)) continue
      visited.add(cur)
      if (!tribeCode.has(cur)) tribeCode.set(cur, code)
      for (const c of childIdsOf.get(cur) ?? []) {
        if (!visited.has(c)) stack.push(c)
      }
    }
  }

  // 約瑟 the patriarch should NOT have a tribe code (he's the M/E split point).
  // Strip any code that got assigned via Joseph (e.g. if M propagated up by mistake).
  const josephPatriarch = exactMap.get('約瑟')  // patriarch is the bare-named one
  if (josephPatriarch) tribeCode.delete(josephPatriarch)

  // ── Format generation label: tribeCode + gen (e.g. "L23") or "第N代" ───
  function genLabel(p: typeof people[0]): string {
    if (p.generation == null) return ''
    const tc = tribeCode.get(p.id)
    return tc ? `${tc}${p.generation}` : `第 ${p.generation} 代`
  }

  const nodes = people.map(p => ({
    id: p.id,
    type: 'person',
    position: { x: 0, y: 0 },
    data: {
      name: p.name_zh,
      gender: p.gender === '男' ? 'male' : p.gender === '女' ? 'female' : 'unknown',
      generation: genLabel(p),
      birthYear: p.birth_year != null
        ? (p.birth_year < 0 ? `前${Math.abs(p.birth_year)}` : `${p.birth_year}`)
        : '',
      deathYear: p.death_year != null
        ? (p.death_year < 0 ? `前${Math.abs(p.death_year)}` : `${p.death_year}`)
        : '',
      notes: p.notes ?? '',
      sortOrder: p.sort_order ?? 9999,
      generationNum: p.generation ?? 0,
      tribeCode: tribeCode.get(p.id) ?? null,
      // 顏色標籤 — 早期教會 view 把 orthodox-tagged 的 Epiphanian 人物（撒羅米/亞西亞/
      // 呂底亞/革羅罷-約瑟之弟）以「早期共識橘色」呈現，避免跟東方教會 view 視覺撞色。
      tradition: (view === 'early_consensus' && p.tradition === 'orthodox')
        ? 'early_consensus'
        : (p.tradition ?? 'biblical'),
      shape: 'rectangle',
      borderStyleId: 'solid-md',
      borderColor: '#d1d5db',
    },
  }))

  // ── Edges with relationKind for Joseph→Jesus (legal) vs Mary→Jesus (biological) ──
  const josephHusbandId = exactMap.get('約瑟（馬利亞之夫）')
  const maryMotherId    = exactMap.get('馬利亞（耶穌之母）')
  const jesusId         = exactMap.get('耶穌（拿撒勒人）')

  // 拉比傳統 parent-child（聖經本文無此 link，只見於 rabbinic sources）：
  // 以利米勒 = 撒門之弟 = 拿順之子（Bava Batra 91a）— 渲染為藍色連線。
  const nahshonId    = exactMap.get('拿順（亞米拿達之子）')
  const elimelechId  = exactMap.get('以利米勒')
  const rabbinicPC = new Set<string>()
  if (nahshonId && elimelechId) rabbinicPC.add(`${nahshonId}|${elimelechId}`)

  type Kind = 'legal' | 'biological' | 'rabbinic' | 'catholic' | 'orthodox' | 'early_consensus' | 'apocrypha'
  function relationKind(parentId: string, childId: string, childName: string): Kind {
    if (rabbinicPC.has(`${parentId}|${childId}`)) return 'rabbinic'
    // Case B: child name added via tradition_children JSONB (catholic / orthodox)
    const tradMap = traditionAddedChildName.get(parentId)
    if (tradMap) {
      const trad = tradMap.get(childName)
      if (trad === 'catholic' || trad === 'orthodox') return trad
    }
    // Case A: parent OR child tagged with a non-biblical tradition.
    // The link is "this tradition" (Bible doesn't assert this parent-child relationship).
    // Example: 瑪塔 (biblical) → 約亞敬 (early_consensus) — 早期教會 tradition asserts this link.
    const parent = idMap.get(parentId)
    const child  = idMap.get(childId)
    const tradList = [parent?.tradition, child?.tradition].filter(t =>
      t === 'early_consensus' || t === 'catholic' || t === 'orthodox' || t === 'rabbinic' || t === 'apocrypha'
    )
    if (tradList.length > 0) return tradList[0] as Kind
    if (childId === jesusId && parentId === josephHusbandId) return 'legal'
    return 'biological'
  }

  const edges: Record<string, unknown>[] = []
  const seen = new Set<string>()

  for (const p of people) {
    if (p.children) {
      for (const raw of p.children.split(/[,，、]/)) {
        const childName = raw.trim()
        const childId = resolveId(childName, p.name_zh)
        if (!childId || childId === p.id) continue
        const eid = `pc:${p.id}:${childId}`
        if (seen.has(eid)) continue
        seen.add(eid)
        const kind = relationKind(p.id, childId, childName)
        const isLegal = kind === 'legal'
        edges.push({
          id: eid,
          source: p.id,
          target: childId,
          type: 'familyTree',
          markerEnd: 'arrowclosed',
          style: {
            stroke: '#6b7280',
            strokeWidth: 1.5,
            strokeDasharray: isLegal ? '5,4' : '',
          },
          data: {
            relationshipType: 'parentChild',
            relationKind: kind,
            color: '#6b7280', strokeWidth: 1.5,
            strokeDasharray: isLegal ? '5,4' : '',
            lineType: 'familyTree',
            dashStyleId: isLegal ? 'dashed' : 'solid',
          },
        })
      }
    }

    if (p.spouse) {
      for (const raw of p.spouse.split(/[,，、]/)) {
        const spouseId = resolveId(raw, p.name_zh)
        if (!spouseId || spouseId === p.id) continue
        const key = [p.id, spouseId].sort().join('|')
        const eid = `sp:${key}`
        if (seen.has(eid)) continue
        seen.add(eid)
        edges.push({
          id: eid,
          source: p.id,
          target: spouseId,
          type: 'straight',
          // No arrowhead: spouses are equal partners
          style: { stroke: '#f43f5e', strokeWidth: 2 },
          data: {
            relationshipType: 'spouse',
            color: '#f43f5e', strokeWidth: 2,
            strokeDasharray: '', lineType: 'straight', dashStyleId: 'solid',
          },
        })
      }
    }
  }

  return { nodes, edges }
})
