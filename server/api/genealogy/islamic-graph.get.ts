export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  // ── View-based tradition filter ──────────────────────────
  // 5 個 view 累進納入更多傳統人物 + JSONB 套用：
  //   quranic       : quranic only（穆斯林世界普世共識；中立預設）
  //   sunni         : + sunni + historical
  //   shia_twelver  : 上述 + shia_twelver（十二派伊瑪目鏈 Hasan→Mahdi）
  //   shia_ismaili  : quranic + sunni + shia_ismaili（伊斯瑪儀於 Ja'far 分支）
  //   shia_zaidi    : quranic + sunni + shia_zaidi（栽德派於 Zayd b. Ali 分支）
  //
  // sufi 暫無資料，保留 view 名但不阻擋未來擴充。
  // shia_* 三派互不混雜（各派視角獨立）。
  const q = getQuery(event)
  const viewRaw = String(q.view ?? 'quranic').toLowerCase()
  type View = 'quranic' | 'sunni' | 'shia_twelver' | 'shia_ismaili' | 'shia_zaidi'
  const view: View =
    viewRaw === 'sunni'        ? 'sunni' :
    viewRaw === 'shia_twelver' ? 'shia_twelver' :
    viewRaw === 'shia_ismaili' ? 'shia_ismaili' :
    viewRaw === 'shia_zaidi'   ? 'shia_zaidi' :
                                 'quranic'

  const allowedTraditions = new Set<string>(['quranic'])
  if (view !== 'quranic') {
    allowedTraditions.add('sunni')
    allowedTraditions.add('historical')
  }
  if (view === 'shia_twelver') allowedTraditions.add('shia_twelver')
  if (view === 'shia_ismaili') allowedTraditions.add('shia_ismaili')
  if (view === 'shia_zaidi')   allowedTraditions.add('shia_zaidi')

  // Which tradition's JSONB to apply for conflict resolution
  const mergeKey: 'shia_twelver' | 'shia_ismaili' | 'shia_zaidi' | null =
    view === 'shia_twelver' ? 'shia_twelver' :
    view === 'shia_ismaili' ? 'shia_ismaili' :
    view === 'shia_zaidi'   ? 'shia_zaidi'   :
                              null

  const { data: allPeople, error } = await supabase
    .from('islamic_people')
    .select('*')
    .order('generation', { ascending: true, nullsFirst: false })
    .order('sort_order', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!allPeople?.length) return { nodes: [], edges: [] }

  const people = allPeople.filter(p => allowedTraditions.has(p.tradition ?? 'sunni'))

  // Apply per-tradition JSONB merges based on selected view.
  // Track which children were ADDED via tradition_children → tag those edges with tradition.
  const traditionAddedChildName = new Map<string, Map<string, string>>()
  for (const p of people) {
    if (!mergeKey) continue
    const addChildren = (p.tradition_children as Record<string, string> | null)?.[mergeKey]
    const addSpouse   = (p.tradition_spouse   as Record<string, string> | null)?.[mergeKey]
    const hideChildrenRaw = (p.tradition_hide_children as Record<string, string> | null)?.[mergeKey]
    if (addChildren) {
      const childNames = addChildren.split(/[,，、]/).map((s: string) => s.trim()).filter(Boolean)
      let tmap = traditionAddedChildName.get(p.id)
      if (!tmap) { tmap = new Map(); traditionAddedChildName.set(p.id, tmap) }
      for (const cn of childNames) tmap.set(cn, mergeKey)
      p.children = p.children ? `${p.children}、${addChildren}` : addChildren
    }
    if (addSpouse) {
      p.spouse = p.spouse ? `${p.spouse}、${addSpouse}` : addSpouse
    }
    if (hideChildrenRaw && p.children) {
      const hideSet = new Set(hideChildrenRaw.split(/[,，、]/).map((s: string) => s.trim()).filter(Boolean))
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

  function genLabel(p: typeof people[0]): string {
    if (p.generation == null) return ''
    return `第 ${p.generation} 代`
  }

  const nodes = people.map(p => ({
    id: p.id,
    type: 'person',
    position: { x: 0, y: 0 },
    data: {
      name: p.name_zh,
      name_ar: p.name_ar ?? '',
      name_en: p.name_en ?? '',
      kunya: p.kunya ?? '',
      gender: p.gender === '男' ? 'male' : p.gender === '女' ? 'female' : 'unknown',
      generation: genLabel(p),
      generationNum: p.generation ?? 0,
      sortOrder: p.sort_order ?? 9999,
      birthYear: p.birth_year != null
        ? (p.birth_year < 0 ? `前${Math.abs(p.birth_year)}` : `${p.birth_year}`)
        : '',
      deathYear: p.death_year != null
        ? (p.death_year < 0 ? `前${Math.abs(p.death_year)}` : `${p.death_year}`)
        : '',
      notes: p.notes ?? '',
      tradition: p.tradition ?? 'sunni',
      shape: 'rectangle',
      borderStyleId: 'solid-md',
      borderColor: '#d1d5db',
    },
  }))

  // ── Edges ─────────────────────────────────────────────
  type Kind = 'biological' | 'shia_twelver' | 'shia_ismaili' | 'shia_zaidi' | 'sunni' | 'historical'
  function relationKind(parentId: string, childId: string, childName: string): Kind {
    const tradMap = traditionAddedChildName.get(parentId)
    if (tradMap) {
      const trad = tradMap.get(childName)
      if (trad === 'shia_twelver' || trad === 'shia_ismaili' || trad === 'shia_zaidi') return trad
    }
    const parent = idMap.get(parentId)
    const child  = idMap.get(childId)
    const tradList = [parent?.tradition, child?.tradition].filter(t =>
      t === 'shia_twelver' || t === 'shia_ismaili' || t === 'shia_zaidi' || t === 'historical'
    )
    if (tradList.length > 0) return tradList[0] as Kind
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
        edges.push({
          id: eid,
          source: p.id,
          target: childId,
          type: 'familyTree',
          markerEnd: 'arrowclosed',
          style: { stroke: '#6b7280', strokeWidth: 1.5 },
          data: {
            relationshipType: 'parentChild',
            relationKind: kind,
            color: '#6b7280', strokeWidth: 1.5,
            strokeDasharray: '', lineType: 'familyTree', dashStyleId: 'solid',
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
