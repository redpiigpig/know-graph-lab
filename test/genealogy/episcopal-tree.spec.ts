// @vitest-environment nuxt
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import EpiscopalSpineTree from '~/components/genealogy/EpiscopalSpineTree.vue'
import { episcopalGood } from './fixtures/episcopal'
import { collisions, type Rect } from './fixtures/helpers'

async function mount(graph: any) {
  return mountSuspended(EpiscopalSpineTree, { props: { graph } })
}

const cardRects = (cv: any): Rect[] =>
  cv.nodes.map((n: any) => ({ x: n.x, y: n.y, w: n.w, h: n.h, id: n.id }))

describe('EpiscopalSpineTree layout', () => {
  it('renders jesus, apostles, spine bishops from graph', async () => {
    const w = await mount(episcopalGood)
    const kinds = w.vm.cv.nodes.map((n: any) => n.kind)
    expect(kinds).toContain('jesus')
    expect(kinds).toContain('apostle')
    expect(kinds).toContain('bishop')
    expect(w.vm.cv.paths.length).toBeGreaterThan(0) // succession lines
  })

  it('null graph renders an empty canvas without throwing', async () => {
    const w = await mount(null)
    expect(w.vm.cv.nodes.length).toBe(0)
    expect(w.vm.ready).toBe(false)
  })

  it('main-spine bishops align in a single column per spine; spines are separate columns', async () => {
    const w = await mount(episcopalGood)
    // only main-spine bishop cards (id 'bish_…'); branch bishops are 'bbish_…'
    const bishops = w.vm.cv.nodes.filter((n: any) => n.kind === 'bishop' && n.id.startsWith('bish_'))
    const byColor = new Map<string, number[]>()
    for (const b of bishops) {
      const arr = byColor.get(b.spineColor) ?? []
      arr.push(b.x)
      byColor.set(b.spineColor, arr)
    }
    expect(byColor.size).toBe(2) // rome + antioch
    for (const xs of byColor.values()) expect(new Set(xs).size).toBe(1) // each column aligned
    const colXs = [...byColor.values()].map(xs => xs[0])
    expect(colXs[0]).not.toBe(colXs[1]) // distinct columns
  })

  // Default-expand policy (watcher at EpiscopalSpineTree.vue:405-418, {immediate:true}):
  //   • 分裂 branch (is_split=true) → EXPANDED by design (並行對立支線，隨母教宗呈現)
  //   • 設立 branch (is_split=false) → collapsed (header only)
  //   • apostles → all collapsed
  it('split branches render expanded; 設立 branches collapsed (default policy)', async () => {
    const w = await mount(episcopalGood)
    const bbish = w.vm.cv.nodes.filter((n: any) => n.id.startsWith('bbish_')).map((n: any) => n.id)
    expect(bbish).toContain('bbish_r-rival')        // 分裂 → expanded, its bishop shows
    expect(bbish).not.toContain('bbish_c-augustine') // 設立 → collapsed, no bishop card
  })

  // 設立 branch 一律預設收進母主教的「+N 被立」選單（單一或多個、東方/天主教一致）；
  // 分裂 rival（≤2 路）仍並行顯示為 header。（取代舊 E2 focus-mode 測試）
  it('設立 branch → parent bishop menu；分裂 rival → visible header', async () => {
    const w = await mount(episcopalGood)
    const headers = w.vm.cv.nodes.filter((n: any) => n.kind === 'branch-see').map((n: any) => n.label).join(' ')
    const inMenu = new Set<string>()
    for (const n of w.vm.cv.nodes) for (const mb of (n.menuBranches ?? [])) inMenu.add(mb.label)
    expect(headers, '分裂 羅馬 rival 仍為 header').toContain('羅馬')
    expect([...inMenu].join(' '), '設立 坎特伯里 收進選單').toContain('坎特伯里')
  })

  // FIX #E3 — branch bishop cards now carry spineColor (was undefined).
  it('branch bishop cards carry a spineColor', async () => {
    const w = await mount(episcopalGood)
    const bb = w.vm.cv.nodes.find((n: any) => n.id === 'bbish_r-rival')
    expect(bb?.spineColor).toBeTruthy()
  })

  it('has NO overlapping cards', async () => {
    const w = await mount(episcopalGood)
    const cols = collisions(cardRects(w.vm.cv))
    expect(cols.map(([a, b]) => `${a.id}↔${b.id}`)).toEqual([])
  })

  it('succession is the only relation type — no marriage data present', async () => {
    const w = await mount(episcopalGood)
    expect(w.vm.cv).not.toHaveProperty('marriages')
  })
})
