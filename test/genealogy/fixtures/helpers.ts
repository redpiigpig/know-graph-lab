// Mini-graph builders — shape mirrors what server/api/genealogy/*-graph.get.ts emit.
// node: { id, data: { name, gender, generation, generationNum, tradition, spouseField? } }
// edge: { source, target, data: { relationshipType: 'parentChild' | 'spouse', relationKind? } }

export interface FNode {
  id: string
  data: {
    name: string
    gender: string
    generation: string
    generationNum: number
    tradition?: string
    spouseField?: string
  }
}
export interface FEdge {
  source: string
  target: string
  data: { relationshipType: 'parentChild' | 'spouse'; relationKind?: string }
}

export function node(
  id: string,
  name: string,
  gender: 'male' | 'female',
  gen: number,
  opts: { label?: string; tradition?: string; spouseField?: string } = {},
): FNode {
  return {
    id,
    data: {
      name,
      gender,
      generation: opts.label ?? `第 ${gen} 代`,
      generationNum: gen,
      tradition: opts.tradition,
      spouseField: opts.spouseField,
    },
  }
}

export const pc = (source: string, target: string, relationKind?: string): FEdge => ({
  source,
  target,
  data: { relationshipType: 'parentChild', ...(relationKind ? { relationKind } : {}) },
})

export const sp = (a: string, b: string): FEdge => ({
  source: a,
  target: b,
  data: { relationshipType: 'spouse' },
})

// ── Geometry assertion helpers ────────────────────────────────────────
export interface Rect { x: number; y: number; w: number; h: number; id?: string; personId?: string }

/** True overlap (shared area), edge-touching allowed. eps guards float noise. */
export function rectsOverlap(a: Rect, b: Rect, eps = 0.5): boolean {
  const ax2 = a.x + a.w, ay2 = a.y + a.h
  const bx2 = b.x + b.w, by2 = b.y + b.h
  const xOverlap = Math.min(ax2, bx2) - Math.max(a.x, b.x)
  const yOverlap = Math.min(ay2, by2) - Math.max(a.y, b.y)
  return xOverlap > eps && yOverlap > eps
}

/** All colliding pairs among visible cards. Identical-id pairs are skipped. */
export function collisions(rects: Rect[]): Array<[Rect, Rect]> {
  const out: Array<[Rect, Rect]> = []
  for (let i = 0; i < rects.length; i++) {
    for (let j = i + 1; j < rects.length; j++) {
      if (rects[i].id && rects[i].id === rects[j].id) continue
      if (rectsOverlap(rects[i], rects[j])) out.push([rects[i], rects[j]])
    }
  }
  return out
}
