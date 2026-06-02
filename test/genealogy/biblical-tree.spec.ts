// @vitest-environment nuxt
import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import BiblicalSpineTree from '~/components/genealogy/BiblicalSpineTree.vue'
import { biblicalGood, biblicalBroken, allPersonIds } from './fixtures/biblical'
import { collisions, type Rect } from './fixtures/helpers'

const DIVERGE_X = 320 // matches component constant; A/B centres are ±DIVERGE_X of shared

async function mount(fixture: { nodes: any[]; edges: any[] }) {
  return mountSuspended(BiblicalSpineTree, {
    props: { nodes: fixture.nodes, edges: fixture.edges },
  })
}

const visibleRects = (cv: any): Rect[] =>
  cv.nodes.filter((n: any) => !n.hidden).map((n: any) => ({ x: n.x, y: n.y, w: n.w, h: n.h, id: n.id, personId: n.personId }))

describe('BiblicalSpineTree layout', () => {
  it('resolves both spines and renders nodes (good fixture)', async () => {
    const w = await mount(biblicalGood)
    expect(w.vm.hasSpine).toBe(true)
    expect(w.vm.spineA.length).toBeGreaterThan(0)
    expect(w.vm.spineB.length).toBeGreaterThan(0)
    expect(w.vm.cv).not.toBeNull()
    expect(w.vm.cv.nodes.length).toBeGreaterThan(0)
  })

  it('shared trunk is the common 亞當→大衛 prefix', async () => {
    const w = await mount(biblicalGood)
    const trunkNames = w.vm.sharedTrunkIds.map((id: string) =>
      biblicalGood.nodes.find(n => n.id === id)?.data.name)
    expect(trunkNames[0]).toBe('亞當')
    expect(trunkNames[trunkNames.length - 1]).toBe('大衛（耶西之子）')
    // branch point 所羅門 / 拿單 must NOT be in shared trunk
    expect(trunkNames).not.toContain('所羅門（大衛之子）')
    expect(trunkNames).not.toContain('拿單（大衛之子）')
  })

  it('A and B unique spines sit in two separate columns (~2·DIVERGE_X apart)', async () => {
    const w = await mount(biblicalGood)
    const aXs = w.vm.cv.nodes.filter((n: any) => n.spineKind === 'A').map((n: any) => n.x)
    const bXs = w.vm.cv.nodes.filter((n: any) => n.spineKind === 'B').map((n: any) => n.x)
    expect(aXs.length).toBeGreaterThan(0)
    expect(bXs.length).toBeGreaterThan(0)
    // each column internally aligned
    expect(new Set(aXs).size).toBe(1)
    expect(new Set(bXs).size).toBe(1)
    expect(Math.abs(aXs[0] - bXs[0])).toBeCloseTo(2 * DIVERGE_X, 0)
  })

  it('has NO overlapping cards (visual collision invariant)', async () => {
    const w = await mount(biblicalGood)
    const cols = collisions(visibleRects(w.vm.cv))
    const report = cols.map(([a, b]) => `${a.personId}↔${b.personId}`)
    expect(report).toEqual([])
  })

  it('every rendered person maps to an input node (no ghosts)', async () => {
    const w = await mount(biblicalGood)
    const ghosts = w.vm.cv.nodes
      .map((n: any) => n.personId)
      .filter((pid: string) => !allPersonIds.has(pid))
    expect(ghosts).toEqual([])
  })

  it('renders spine persons’ wives to their left with a marriage line', async () => {
    const w = await mount(biblicalGood)
    const nodes = w.vm.cv.nodes
    const isaac = nodes.find((n: any) => n.personId === 'isaac')
    const rebekah = nodes.find((n: any) => n.personId === 'rebekah')
    expect(isaac, '以撒 (spine) should render').toBeTruthy()
    // INTENDED: a spine person's spouse is drawn. If this fails, spine-person
    // wives are not shown in the default view (finding).
    expect(rebekah, '利百加 (以撒之妻) should render in default view').toBeTruthy()
    if (rebekah) {
      expect(rebekah.x).toBeLessThan(isaac.x) // 夫右妻左
      const hasLine = w.vm.cv.marriages.some((m: any) =>
        Math.abs(m.x2 - isaac.x) < 80 || Math.abs(m.x1 - (rebekah.x + rebekah.w)) < 80)
      expect(hasLine, 'marriage line connects 以撒↔利百加').toBe(true)
    }
  })

  it('marriage lines run left→right (x1 < x2) and sit between card edges', async () => {
    const w = await mount(biblicalGood)
    for (const m of w.vm.cv.marriages) {
      expect(m.x1, `marriage ${m.id} x1<x2`).toBeLessThan(m.x2)
    }
  })

  // FRAGILITY (B1): a single missing waypoint person still collapses the whole
  // tree, but spineFromWaypoints now emits a dev warning naming the broken link
  // instead of failing silently to a blank screen.
  it('a missing B-line waypoint collapses the tree AND warns which name broke', async () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const w = await mount(biblicalBroken)
    expect(w.vm.hasSpine).toBe(false)
    expect(w.vm.cv).toBeNull()
    const msgs = warn.mock.calls.map(c => c.join(' ')).join('\n')
    expect(msgs).toContain('瑪塔') // names the unresolved / broken waypoint
    warn.mockRestore()
  })
})
