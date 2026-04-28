export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data: people, error } = await supabase
    .from('biblical_people')
    .select('*')
    .order('birth_year', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!people?.length) return { nodes: [], edges: [] }

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

  const nodes = people.map(p => ({
    id: p.id,
    type: 'person',
    position: { x: 0, y: 0 },
    data: {
      name: p.name_zh,
      gender: p.gender === '男' ? 'male' : p.gender === '女' ? 'female' : 'unknown',
      generation: p.generation != null ? `第 ${p.generation} 代` : '',
      birthYear: p.birth_year != null
        ? (p.birth_year < 0 ? `前${Math.abs(p.birth_year)}` : `${p.birth_year}`)
        : '',
      deathYear: p.death_year != null
        ? (p.death_year < 0 ? `前${Math.abs(p.death_year)}` : `${p.death_year}`)
        : '',
      notes: p.notes ?? '',
      sortOrder: p.sort_order ?? 9999,
      generationNum: p.generation ?? 0,
      shape: 'rectangle',
      borderStyleId: 'solid-md',
      borderColor: '#d1d5db',
    },
  }))

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
        edges.push({
          id: eid,
          source: p.id,
          target: childId,
          type: 'familyTree',
          markerEnd: 'arrowclosed',
          style: { stroke: '#6b7280', strokeWidth: 1.5 },
          data: {
            relationshipType: 'parentChild',
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
