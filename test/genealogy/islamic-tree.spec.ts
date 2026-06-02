// @vitest-environment nuxt
import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import IslamicSpineTree from '~/components/genealogy/IslamicSpineTree.vue'
import { islamicGood, islamicBroken, allPersonIds } from './fixtures/islamic'
import { collisions, type Rect } from './fixtures/helpers'

const SPINE_X = 1200
const NW = 130

async function mount(fixture: { nodes: any[]; edges: any[] }, view?: any) {
  return mountSuspended(IslamicSpineTree, {
    props: { nodes: fixture.nodes, edges: fixture.edges, ...(view ? { view } : {}) },
  })
}

const visibleRects = (cv: any): Rect[] =>
  cv.nodes.filter((n: any) => !n.hidden).map((n: any) => ({ x: n.x, y: n.y, w: n.w, h: n.h, id: n.id, personId: n.personId }))

describe('IslamicSpineTree layout', () => {
  it('resolves spine and renders (good fixture)', async () => {
    const w = await mount(islamicGood)
    expect(w.vm.hasSpine).toBe(true)
    expect(w.vm.spinePath.length).toBe(6) // 阿丹→努哈→易卜拉欣→伊斯瑪儀→阿德南→穆罕默德
    expect(w.vm.cv).not.toBeNull()
    expect(w.vm.cv.nodes.length).toBeGreaterThan(0)
  })

  it('spine persons sit in a single aligned column at SPINE_X', async () => {
    const w = await mount(islamicGood)
    const spineXs = w.vm.cv.nodes.filter((n: any) => n.isSpine).map((n: any) => n.x)
    expect(spineXs.length).toBe(6)
    expect(new Set(spineXs).size).toBe(1)
    // x = SPINE_X (modulo a global shift when content goes negative)
    expect(spineXs[0]).toBeGreaterThanOrEqual(SPINE_X)
  })

  it('has NO overlapping cards', async () => {
    const w = await mount(islamicGood)
    const cols = collisions(visibleRects(w.vm.cv))
    expect(cols.map(([a, b]) => `${a.personId}↔${b.personId}`)).toEqual([])
  })

  it('places 穆罕默德 wives to the left, 赫蒂徹 (spouseField首位) closest', async () => {
    const w = await mount(islamicGood)
    const nodes = w.vm.cv.nodes
    const m = nodes.find((n: any) => n.personId === 'muhammad')
    const khadija = nodes.find((n: any) => n.personId === 'khadija')
    const aisha = nodes.find((n: any) => n.personId === 'aisha')
    expect(m).toBeTruthy()
    expect(khadija, '赫蒂徹 should render').toBeTruthy()
    expect(aisha, '阿伊夏 should render').toBeTruthy()
    if (khadija && aisha) {
      expect(khadija.x).toBeLessThan(m.x)           // wives on the left
      expect(aisha.x).toBeLessThan(khadija.x)        // 赫蒂徹 closer to 穆聖 than 阿伊夏
      // single-row, fixed SLOT spacing
      expect(Math.abs((khadija.x - aisha.x))).toBeCloseTo(NW + 50, 0) // SLOT_K = NW+WIFE_HG
    }
  })

  it('every rendered person maps to an input node (no ghosts)', async () => {
    const w = await mount(islamicGood)
    const ghosts = w.vm.cv.nodes.map((n: any) => n.personId).filter((pid: string) => !allPersonIds.has(pid))
    expect(ghosts).toEqual([])
  })

  it('marriage lines run left→right', async () => {
    const w = await mount(islamicGood)
    for (const ml of w.vm.cv.marriages) {
      expect(ml.x1, `marriage ${ml.id}`).toBeLessThan(ml.x2)
    }
  })

  // view is a server-driven filter (page refetches); component does not refilter.
  it('view prop does not change in-component layout (server-side filtering finding)', async () => {
    const a = await mount(islamicGood, 'quranic')
    const b = await mount(islamicGood, 'shia_twelver')
    expect(a.vm.cv.nodes.length).toBe(b.vm.cv.nodes.length)
  })

  // FIX (I1): missing 阿德南 now DEGRADES — renders 阿丹→伊斯瑪儀 (resolvable prefix),
  // exposes the break, and warns. No whole-tree blank-out.
  it('a missing waypoint (阿德南) degrades to a partial tree + warns (no blank)', async () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const w = await mount(islamicBroken)
    expect(w.vm.hasSpine).toBe(true)
    expect(w.vm.cv).not.toBeNull()
    expect(w.vm.spinePath.length).toBe(4)   // 阿丹,努哈,易卜拉欣,伊斯瑪儀 (穆罕默德 unreachable)
    expect(w.vm.spineDegraded).toBeTruthy()
    const msgs = warn.mock.calls.map(c => c.join(' ')).join('\n')
    expect(msgs).toContain('阿德南')
    warn.mockRestore()
  })
})
