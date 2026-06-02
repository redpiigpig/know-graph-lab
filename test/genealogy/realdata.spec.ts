// @vitest-environment nuxt
// Regression tests against REAL graph data snapshotted from the live
// /api/genealogy/*-graph endpoints (test/genealogy/fixtures/snapshots/*.json).
// Dense real data is where card-overlap bugs actually surface — mini fixtures
// are too small. Re-snapshot with: node scripts/_snapshot_genealogy.mjs
import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import Biblical from '~/components/genealogy/BiblicalSpineTree.vue'
import Islamic from '~/components/genealogy/IslamicSpineTree.vue'
import Episcopal from '~/components/genealogy/EpiscopalSpineTree.vue'
import { collisions, type Rect } from './fixtures/helpers'

const load = (f: string) => JSON.parse(readFileSync(`test/genealogy/fixtures/snapshots/${f}.json`, 'utf8'))
const visRects = (cv: any): Rect[] =>
  cv.nodes.filter((n: any) => !n.hidden).map((n: any) => ({ x: n.x, y: n.y, w: n.w, h: n.h, id: n.id, personId: n.personId }))
const fmt = (cols: Array<[Rect, Rect]>) =>
  cols.slice(0, 20).map(([a, b]) => `${a.personId ?? a.id}@(${Math.round(a.x)},${Math.round(a.y)})↔${b.personId ?? b.id}@(${Math.round(b.x)},${Math.round(b.y)})`).join('\n')

describe('real-data: BiblicalSpineTree', () => {
  it('renders fully (all waypoints resolve, no degradation)', async () => {
    const g = load('biblical')
    const w = await mountSuspended(Biblical, { props: { nodes: g.nodes, edges: g.edges } })
    expect(w.vm.hasSpine).toBe(true)
    expect(w.vm.spineDegraded).toBeNull()
    expect(w.vm.cv.nodes.length).toBeGreaterThan(100)
  })

  // 5 dense-region overlaps FIXED via FORCE_EXPAND_SHIFT_X (利未 +600, 斯多蘭 -220).
  // Now strict 0 — guards against any new overlap creeping in.
  it('has NO overlapping cards', async () => {
    const g = load('biblical')
    const w = await mountSuspended(Biblical, { props: { nodes: g.nodes, edges: g.edges } })
    const cols = collisions(visRects(w.vm.cv))
    expect(cols.length, `overlaps:\n${fmt(cols)}`).toBe(0)
  })
})

describe('real-data: IslamicSpineTree', () => {
  it('renders fully and has NO overlapping cards', async () => {
    const g = load('islamic')
    const w = await mountSuspended(Islamic, { props: { nodes: g.nodes, edges: g.edges } })
    expect(w.vm.hasSpine).toBe(true)
    expect(w.vm.spineDegraded).toBeNull()
    const cols = collisions(visRects(w.vm.cv))
    expect(cols.length, `overlaps:\n${fmt(cols)}`).toBe(0)
  })
})

describe('real-data: EpiscopalSpineTree', () => {
  it('renders and has NO overlapping cards', async () => {
    const g = load('episcopal')
    const w = await mountSuspended(Episcopal, { props: { graph: g } })
    expect(w.vm.cv.nodes.length).toBeGreaterThan(100)
    const cols = collisions(w.vm.cv.nodes.map((n: any) => ({ x: n.x, y: n.y, w: n.w, h: n.h, id: n.id })))
    expect(cols.length, `overlaps:\n${fmt(cols)}`).toBe(0)
  })
})
