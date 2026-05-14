export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  // ── 統一視圖 + 衝突解視角 ────────────────────────────────────────────
  // 所有人物（不分傳統）一律回傳，前端用 card 顏色辨識來源傳統。
  // `?view=<key>` where key ∈ { protestant | catholic | orthodox }
  // 只用來解「耶穌弟兄是誰」的衝突（馬可 6:3 三派不同解）。
  // 規則：對每張 row 的 tradition_X JSONB 欄位：
  //   - rabbinic 值永遠 apply（無衝突）
  //   - 若 catholic 與 orthodox 同一欄位都有值 → 視為衝突，依 view 取一
  //   - 若只有 catholic 或只有 orthodox 有值 → 非衝突，永遠 apply
  // protestant 預設：兩派同時有值的欄位（衝突）兩派都不 apply。
  const q = getQuery(event)
  const viewRaw = String(q.view ?? 'protestant').toLowerCase()
  // early_consensus 等同 orthodox 的耶穌弟兄解（前妻說，Epiphanian view）；
  // 在 Jerome ~393 之前是早期教會主流。
  const view: 'protestant' | 'catholic' | 'orthodox' =
    viewRaw === 'catholic' ? 'catholic' :
    (viewRaw === 'orthodox' || viewRaw === 'early_consensus') ? 'orthodox' : 'protestant'

  const { data: allPeople, error } = await supabase
    .from('biblical_people')
    .select('*')
    .order('birth_year', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!allPeople?.length) return { nodes: [], edges: [] }

  const people = allPeople  // no tradition filter — show everyone, color via UI

  // Merge per-row tradition fields with the conflict-aware rule above.
  function mergeField(jsonb: Record<string, string> | null | undefined): string {
    if (!jsonb) return ''
    const cat = jsonb.catholic
    const orth = jsonb.orthodox
    const rab = jsonb.rabbinic
    const parts: string[] = []
    if (rab) parts.push(rab)
    if (cat && orth) {
      // Conflict — view picks one (protestant picks neither)
      if (view === 'catholic') parts.push(cat)
      else if (view === 'orthodox') parts.push(orth)
    } else {
      if (cat) parts.push(cat)
      if (orth) parts.push(orth)
    }
    return parts.join('、')
  }

  for (const p of people) {
    const addChildren = mergeField(p.tradition_children as Record<string, string> | null)
    const addSpouse   = mergeField(p.tradition_spouse   as Record<string, string> | null)
    const hideChildrenRaw = mergeField(p.tradition_hide_children as Record<string, string> | null)
    if (addChildren) {
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
      tradition: p.tradition ?? 'biblical',
      shape: 'rectangle',
      borderStyleId: 'solid-md',
      borderColor: '#d1d5db',
    },
  }))

  // ── Edges with relationKind for Joseph→Jesus (legal) vs Mary→Jesus (biological) ──
  const josephHusbandId = exactMap.get('約瑟（馬利亞之夫）')
  const maryMotherId    = exactMap.get('馬利亞（耶穌之母）')
  const jesusId         = exactMap.get('耶穌（拿撒勒人）')

  function relationKind(parentId: string, childId: string): 'legal' | 'biological' {
    if (childId === jesusId && parentId === josephHusbandId) return 'legal'
    return 'biological'
  }

  const edges: Record<string, unknown>[] = []
  const seen = new Set<string>()

  for (const p of people) {
    if (p.children) {
      for (const raw of p.children.split(/[,，、]/)) {
        const childId = resolveId(raw, p.name_zh)
        if (!childId || childId === p.id) continue
        const eid = `pc:${p.id}:${childId}`
        if (seen.has(eid)) continue
        seen.add(eid)
        const kind = relationKind(p.id, childId)
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
