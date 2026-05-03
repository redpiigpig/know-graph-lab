<template>
  <div
    ref="viewportRef"
    class="absolute inset-0 bg-stone-50 select-none overflow-hidden"
    :class="isDragging ? 'cursor-grabbing' : 'cursor-grab'"
    @wheel.prevent="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <!-- Loading / error -->
    <div v-if="!ready" class="flex flex-col items-center justify-center h-full gap-2 pointer-events-none">
      <span class="text-gray-400 text-sm">
        {{ props.nodes.length === 0 ? '資料載入中…' : '計算族譜圖…' }}
      </span>
      <span v-if="props.nodes.length > 0 && spine.length === 0" class="text-xs text-red-400">
        找不到亞當→耶穌路徑（共 {{ props.nodes.length }} 人）
      </span>
    </div>

    <template v-else>
      <!-- Pan/zoom canvas -->
      <div
        class="absolute top-0 left-0 origin-top-left"
        :style="{
          width: cv!.w + 'px',
          height: cv!.h + 'px',
          transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
          willChange: 'transform',
        }"
      >
        <!-- ① SVG: all lines, drawn first so cards sit on top -->
        <svg class="absolute inset-0 pointer-events-none overflow-visible"
             :width="cv!.w" :height="cv!.h">

          <!-- Spine trunk guide (faint amber) -->
          <line :x1="cv!.spineCX" :y1="cv!.spineY1"
                :x2="cv!.spineCX" :y2="cv!.spineY2"
                stroke="#f59e0b" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- Marriage lines (red, passes behind person cards) -->
          <line v-for="m in cv!.marriages" :key="m.id"
                :x1="m.x1" :y1="m.y" :x2="m.x2" :y2="m.y"
                stroke="#dc2626" stroke-width="2" stroke-linecap="round" />

          <!-- Vertical drops (parent bottom → child/clan top) -->
          <line v-for="(d, i) in cv!.drops" :key="'d'+i"
                :x1="d.x" :y1="d.y1" :x2="d.x" :y2="d.y2"
                stroke="#9ca3af" stroke-width="1.5" stroke-linecap="round" />

          <!-- Horizontal bars (when patriarch has spine child + own clan) -->
          <line v-for="(b, i) in cv!.hbars" :key="'b'+i"
                :x1="b.x1" :y1="b.y" :x2="b.x2" :y2="b.y"
                stroke="#9ca3af" stroke-width="1.5" stroke-linecap="round" />
        </svg>

        <!-- ② Person and clan cards (on top of SVG) -->
        <div
          v-for="n in cv!.nodes" :key="n.id"
          class="node-card absolute"
          :class="cardClass(n)"
          :style="cardStyle(n)"
          @click.stop="n.isClan ? openClan(n) : $emit('selectPerson', n.id)"
        >
          <div v-if="n.isSpine" class="absolute left-0 top-2 bottom-2 w-[3px] bg-amber-400 rounded-full" />
          <div class="px-2.5 py-1.5" :class="n.isSpine ? 'pl-4' : ''">
            <div class="text-[9px] font-medium leading-none mb-0.5 tracking-wide opacity-60"
                 :class="n.isClan ? 'text-amber-600' : n.isSpine ? 'text-amber-500' : 'text-slate-400'">
              {{ n.isClan ? `旁支 · ${n.clanCount}人` : `第 ${n.generation} 代` }}
            </div>
            <div class="text-[12px] font-semibold leading-snug"
                 :class="n.isClan ? 'text-amber-800' : 'text-slate-800'"
                 :title="n.rawName">
              {{ n.displayName }}
            </div>
            <div v-if="n.isClan" class="text-[9px] text-amber-400 mt-0.5">點擊展開 ▶</div>
          </div>
        </div>
      </div>

      <!-- Controls (viewport-fixed) -->
      <div class="absolute top-3 right-3 z-40 flex flex-col gap-1.5 pointer-events-auto">
        <button
          class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                 text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
          @click.stop="zoomIn">+</button>
        <button
          class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                 text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
          @click.stop="zoomOut">−</button>
        <div class="text-[9px] text-gray-400 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</div>
        <button
          class="px-1 py-1.5 bg-white/90 border border-amber-300 rounded-lg text-amber-600
                 text-[10px] font-medium shadow-sm hover:bg-amber-50 transition leading-tight
                 text-center cursor-default"
          @click.stop="fitSpine">定位<br>主幹</button>
      </div>
    </template>

    <!-- Clan overlay (full-screen, fixed to viewport) -->
    <Transition name="ft">
      <div v-if="activeClan" class="absolute inset-0 z-50 bg-stone-50 flex flex-col">
        <div class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 shrink-0">
          <button class="text-sm text-gray-500 hover:text-gray-700 transition"
                  @click="activeClan = null">← 返回族譜</button>
          <div class="w-px h-4 bg-gray-200" />
          <span class="font-semibold text-sm text-gray-900">{{ activeClan.rawName }}</span>
          <span class="text-xs text-gray-400 ml-1">共 {{ activeClan.clanCount }} 人</span>
        </div>
        <div class="flex-1 overflow-auto p-4">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            <div v-for="m in clanMembers" :key="m.id"
                 class="bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs
                        cursor-pointer hover:border-amber-300 hover:shadow-sm transition"
                 @click="$emit('selectPerson', m.id)">
              <div class="font-semibold text-gray-800">{{ baseName(m.name) }}</div>
              <div class="text-gray-400 mt-0.5">第 {{ m.generation }} 代</div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ nodes: any[]; edges: any[] }>()
const emit  = defineEmits<{ selectPerson: [id: string] }>()

// ── Layout constants ──────────────────────────────────────────────────
const NW             = 120   // person card width
const NH             = 52    // person card height
const CW             = 108   // clan card width
const CH             = 52    // clan card height
const MG             = 12    // gap between stacked wives
const HG             = 20    // horizontal gap
const VG             = 90    // vertical gap between rows
const RH             = NH + VG
const PAD            = 48
const MAR_GAP        = Math.round(VG / 2)  // 45 – marriage line length (between card edges)
const SHOW_THRESHOLD = 4                    // show non-spine children individually if ≤ this

const baseName  = (s: string) => s.split('（')[0].trim()
const shortName = (s: string) => { const b = baseName(s); return b.length <= 7 ? b : b.slice(0, 6) + '…' }
const genY      = (g: number) => (g - 1) * RH + PAD
const marY      = (g: number) => genY(g) + NH / 2

// ── Graph maps ────────────────────────────────────────────────────────
const personById = computed(() => {
  const m = new Map<string, any>()
  for (const n of props.nodes) m.set(n.id, n)
  return m
})

// parentChild edges: source → [targets]
const childrenOf = computed(() => {
  const m = new Map<string, string[]>()
  for (const e of props.edges) {
    if (e.data?.relationshipType === 'parentChild') {
      if (!m.has(e.source)) m.set(e.source, [])
      m.get(e.source)!.push(e.target)
    }
  }
  return m
})

// spouse edges: bidirectional
const spousesOf = computed(() => {
  const m = new Map<string, string[]>()
  for (const e of props.edges) {
    if (e.data?.relationshipType === 'spouse') {
      const add = (a: string, b: string) => {
        if (!m.has(a)) m.set(a, [])
        if (!m.get(a)!.includes(b)) m.get(a)!.push(b)
      }
      add(e.source, e.target); add(e.target, e.source)
    }
  }
  return m
})

// ── Spine: BFS from 亞當 → 耶穌（拿撒勒人） ─────────────────────────
const spine = computed((): string[] => {
  const ch = childrenOf.value
  const adamId  = props.nodes.find(n => n.data?.name === '亞當')?.id ?? ''
  const jesusId = props.nodes.find(n => n.data?.name === '耶穌（拿撒勒人）')?.id ?? ''
  if (!adamId || !jesusId) return []
  const queue: string[][] = [[adamId]]
  const vis = new Set<string>()
  while (queue.length) {
    const path = queue.shift()!
    const cur  = path[path.length - 1]
    if (cur === jesusId) return path
    if (vis.has(cur)) continue
    vis.add(cur)
    for (const c of ch.get(cur) ?? []) if (!vis.has(c)) queue.push([...path, c])
  }
  return []
})

const spineSet = computed(() => new Set(spine.value))

// ── Subtree collector ─────────────────────────────────────────────────
function subtreeIds(id: string, vis = new Set<string>()): string[] {
  if (vis.has(id)) return []
  vis.add(id)
  return [id, ...(childrenOf.value.get(id) ?? []).flatMap(c => subtreeIds(c, vis))]
}

// ── Node type ─────────────────────────────────────────────────────────
interface LNode {
  id: string; rawName: string; displayName: string
  generation: number; gender: string
  x: number; y: number; w: number; h: number
  isSpine: boolean; isClan: boolean
  clanCount?: number; clanMemberIds?: string[]
}
interface VDrop { x: number; y1: number; y2: number }
interface HBar  { x1: number; x2: number; y: number }
interface MLine { id: string; x1: number; x2: number; y: number }

// ── Main layout ───────────────────────────────────────────────────────
const cv = computed(() => {
  const spn  = spine.value
  if (!spn.length) return null

  const spSet = spineSet.value
  const ch    = childrenOf.value
  const sp    = spousesOf.value
  const pMap  = personById.value

  // SPINE_X: enough room for all wives (stacked left) + MAR_GAP
  const maxWives = Math.max(0, ...spn.map(id => (sp.get(id) ?? []).length))
  const SPINE_X  = PAD + (maxWives > 0
    ? MAR_GAP + maxWives * NW + Math.max(0, maxWives - 1) * MG
    : 0)
  const spineCX  = SPINE_X + NW / 2

  const nodes:     LNode[] = []
  const drops:     VDrop[] = []
  const hbars:     HBar[]  = []
  const marriages: MLine[] = []
  const shown = new Set<string>()

  // ── Place all spine nodes first ────────────────────────────────────
  for (const sid of spn) {
    const p = pMap.get(sid); if (!p) continue
    const gen = p.data.generationNum || 0
    nodes.push({
      id: sid, rawName: p.data.name, displayName: shortName(p.data.name),
      generation: gen, gender: p.data.gender,
      x: SPINE_X, y: genY(gen), w: NW, h: NH,
      isSpine: true, isClan: false,
    })
    shown.add(sid)
  }

  // ── Per-spine-node: wives, children, lines ─────────────────────────
  for (let si = 0; si < spn.length; si++) {
    const sid = spn[si]
    const p   = pMap.get(sid); if (!p) continue
    const gen = p.data.generationNum || 0

    const spineChildId = spn[si + 1] ?? null
    const scP          = spineChildId ? pMap.get(spineChildId) : null
    const childGenY    = genY(scP?.data.generationNum || gen + 1)
    const marLineY     = marY(gen)

    // ── Place wives LEFT of patriarch ──────────────────────────────
    const wifeIds = sp.get(sid) ?? []
    const wifeLX  = new Map<string, number>()   // wid → card left-x

    for (let wi = 0; wi < wifeIds.length; wi++) {
      const wid = wifeIds[wi]
      // wi=0 nearest: right edge = SPINE_X - MAR_GAP
      const wx = SPINE_X - MAR_GAP - (wi + 1) * NW - wi * MG
      wifeLX.set(wid, wx)

      if (!shown.has(wid)) {
        shown.add(wid)
        const wp = pMap.get(wid)
        if (wp) nodes.push({
          id: wid, rawName: wp.data.name, displayName: shortName(wp.data.name),
          generation: wp.data.generationNum || gen, gender: wp.data.gender,
          x: wx, y: genY(gen), w: NW, h: NH,
          isSpine: false, isClan: false,
        })
      }

      // Marriage line segment — only the gap between card edges, not through any card
      if (wi === 0) {
        // Nearest wife right → patriarch left  (MAR_GAP wide)
        marriages.push({ id: `ms_${sid}_0`, x1: wx + NW, x2: SPINE_X, y: marLineY })
      } else {
        // Wife-wi right → wife-(wi-1) left  (MG wide)
        const prevWx = wifeLX.get(wifeIds[wi - 1])!
        marriages.push({ id: `ms_${sid}_${wi}`, x1: wx + NW, x2: prevWx, y: marLineY })
      }
    }

    // Marriage midpoint X — where all children descend from
    const midX = wifeIds.length > 0
      ? SPINE_X - Math.round(MAR_GAP / 2)
      : spineCX

    // ── Collect ALL non-spine children (wives + patriarch's own) ───
    const allWifeKidSet = new Set(wifeIds.flatMap(wid => ch.get(wid) ?? []))
    const unattributed  = (ch.get(sid) ?? []).filter(
      id => id !== spineChildId && !spSet.has(id) && !allWifeKidSet.has(id),
    )
    const wivesNonSpineKids = wifeIds.flatMap(wid =>
      (ch.get(wid) ?? []).filter(id => id !== spineChildId && !spSet.has(id)),
    )
    const allNonSpineKids = [...new Set([...wivesNonSpineKids, ...unattributed])]

    if (allNonSpineKids.length > 0) {
      if (allNonSpineKids.length <= SHOW_THRESHOLD) {
        // ── Show children individually ──────────────────────────────
        // Place to the RIGHT of the patriarch column to avoid overlapping wives
        const childStartX = SPINE_X + NW + HG
        const childCXs: number[] = []

        for (let ci = 0; ci < allNonSpineKids.length; ci++) {
          const cid = allNonSpineKids[ci]
          if (shown.has(cid)) continue
          const cp = pMap.get(cid)
          const cx = childStartX + ci * (NW + MG)
          childCXs.push(cx + NW / 2)
          nodes.push({
            id: cid,
            rawName:     cp?.data.name ?? cid,
            displayName: shortName(cp?.data.name ?? cid),
            generation:  cp?.data.generationNum || gen + 1,
            gender:      cp?.data.gender ?? '',
            x: cx, y: childGenY, w: NW, h: NH,
            isSpine: false, isClan: false,
          })
          shown.add(cid)
        }

        if (childCXs.length === 1) {
          // Orthogonal: down from midX → right to child → down
          if (childCXs[0] !== midX) {
            const jY = marLineY + Math.round((childGenY - marLineY) * 0.3)
            drops.push({ x: midX,       y1: marLineY, y2: jY })
            hbars.push({ x1: Math.min(midX, childCXs[0]), x2: Math.max(midX, childCXs[0]), y: jY })
            drops.push({ x: childCXs[0], y1: jY,      y2: childGenY })
          } else {
            drops.push({ x: midX, y1: marLineY, y2: childGenY })
          }
        } else if (childCXs.length > 1) {
          // T-bar: down from midX → bar → each child
          const barY = marLineY + Math.round((childGenY - marLineY) * 0.3)
          drops.push({ x: midX, y1: marLineY, y2: barY })
          hbars.push({ x1: Math.min(midX, ...childCXs), x2: Math.max(...childCXs), y: barY })
          for (const ccx of childCXs) drops.push({ x: ccx, y1: barY, y2: childGenY })
        }
      } else {
        // ── Clan node to the RIGHT of patriarch ────────────────────
        const allIds   = allNonSpineKids.flatMap(id => subtreeIds(id))
        const firstKid = pMap.get(allNonSpineKids[0])
        const label    = `${baseName(firstKid?.data.name ?? '')}等${allNonSpineKids.length}支`
        const clanX    = SPINE_X + NW + HG
        const clanCX   = clanX + CW / 2
        nodes.push({
          id: `clan_${sid}`, rawName: label, displayName: label,
          generation: gen + 1, gender: '',
          x: clanX, y: childGenY, w: CW, h: CH,
          isSpine: false, isClan: true,
          clanCount: allIds.length, clanMemberIds: allIds,
        })
        // Orthogonal: midX → right to clan → down
        const jY = marLineY + Math.round((childGenY - marLineY) * 0.3)
        drops.push({ x: midX,  y1: marLineY, y2: jY })
        hbars.push({ x1: Math.min(midX, clanCX), x2: Math.max(midX, clanCX), y: jY })
        drops.push({ x: clanCX, y1: jY, y2: childGenY })
      }
    }

    // ── Spine child line ───────────────────────────────────────────
    if (spineChildId) {
      if (midX === spineCX) {
        // No wives: straight drop from patriarch bottom
        drops.push({ x: spineCX, y1: genY(gen) + NH, y2: childGenY })
      } else {
        // Wives present: orthogonal from marriage midpoint back to spine column
        // (midX, marLineY) → down → right to spineCX → down
        const barY = marLineY + Math.round((childGenY - marLineY) * 0.65)
        drops.push({ x: midX,    y1: marLineY, y2: barY })
        hbars.push({ x1: Math.min(midX, spineCX), x2: Math.max(midX, spineCX), y: barY })
        drops.push({ x: spineCX, y1: barY,      y2: childGenY })
      }
    }
  }

  // ── Canvas bounds ──────────────────────────────────────────────────
  const maxRight = Math.max(...nodes.map(n => n.x + n.w), SPINE_X + NW) + PAD
  const maxBot   = Math.max(...nodes.map(n => n.y + n.h)) + PAD

  const firstSN = nodes.find(n => n.id === spn[0])
  const lastSN  = nodes.find(n => n.id === spn[spn.length - 1])

  return {
    nodes, drops, hbars, marriages,
    w: maxRight, h: maxBot,
    spineCX,
    spineY1: firstSN ? firstSN.y : PAD,
    spineY2: lastSN  ? lastSN.y + NH : PAD,
  }
})

const ready = computed(() => !!cv.value && cv.value.nodes.length > 0)

// ── Pan / zoom ────────────────────────────────────────────────────────
const viewportRef = ref<HTMLElement | null>(null)
const zoom        = ref(1)
const panX        = ref(0)
const panY        = ref(0)
const isDragging  = ref(false)
let _anchor = { x: 0, y: 0, px: 0, py: 0 }

const ZOOM_MIN = 0.06
const ZOOM_MAX = 3.0
const clamp = (z: number) => Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, z))

function onWheel(e: WheelEvent) {
  if (activeClan.value) return
  const vp = viewportRef.value; if (!vp) return
  const { left, top } = vp.getBoundingClientRect()
  const cx = e.clientX - left
  const cy = e.clientY - top
  const newZ  = clamp(zoom.value * (e.deltaY < 0 ? 1.15 : 1 / 1.15))
  const ratio = newZ / zoom.value
  panX.value  = cx - (cx - panX.value) * ratio
  panY.value  = cy - (cy - panY.value) * ratio
  zoom.value  = newZ
}

function onPointerDown(e: PointerEvent) {
  if (activeClan.value) return
  if ((e.target as HTMLElement).closest('.node-card')) return
  isDragging.value = true
  _anchor = { x: e.clientX, y: e.clientY, px: panX.value, py: panY.value }
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  panX.value = _anchor.px + (e.clientX - _anchor.x)
  panY.value = _anchor.py + (e.clientY - _anchor.y)
}

function onPointerUp() { isDragging.value = false }

function zoomIn()  { zoomAround(zoom.value * 1.25) }
function zoomOut() { zoomAround(zoom.value / 1.25) }

function zoomAround(newZ: number) {
  const vp = viewportRef.value; if (!vp) return
  const cx = vp.clientWidth  / 2
  const cy = vp.clientHeight / 2
  const cz = clamp(newZ)
  panX.value = cx - (cx - panX.value) * (cz / zoom.value)
  panY.value = cy - (cy - panY.value) * (cz / zoom.value)
  zoom.value = cz
}

function fitSpine() {
  if (!cv.value || !viewportRef.value) return
  const vw = viewportRef.value.clientWidth
  const vh = viewportRef.value.clientHeight
  const c  = cv.value
  // Show ~12 generations at a readable size instead of fitting the whole tree
  const targetH = 12 * RH
  const z = clamp(Math.min(vh / targetH, vw / c.w, 0.9))
  zoom.value = z
  panX.value = vw / 2 - c.spineCX * z
  panY.value = 40
}

watch(ready, val => { if (val) nextTick(fitSpine) }, { immediate: true })
onMounted(() => { if (ready.value) nextTick(fitSpine) })

// ── Clan overlay ──────────────────────────────────────────────────────
const activeClan = ref<LNode | null>(null)

const clanMembers = computed(() =>
  (activeClan.value?.clanMemberIds ?? [])
    .map(id => {
      const p = personById.value.get(id)
      return p ? { id, name: p.data.name, generation: p.data.generationNum || 0 } : null
    })
    .filter(Boolean)
    .sort((a, b) => a!.generation - b!.generation) as { id: string; name: string; generation: number }[]
)

function openClan(n: LNode) { activeClan.value = n }

// ── Card styling ──────────────────────────────────────────────────────
function cardClass(n: LNode) {
  if (n.isClan)
    return 'border-2 border-dashed border-amber-300 bg-amber-50/90 hover:bg-amber-100/90 rounded-xl cursor-pointer'
  if (n.isSpine)
    return 'border border-stone-300 bg-white shadow-sm hover:shadow-md rounded-xl cursor-pointer'
  if (n.gender === 'female')
    return 'border border-rose-200 bg-rose-50/90 hover:shadow-sm rounded-xl cursor-pointer'
  return 'border border-slate-200 bg-white hover:shadow-sm rounded-xl cursor-pointer'
}

function cardStyle(n: LNode) {
  return { left: n.x + 'px', top: n.y + 'px', width: n.w + 'px', minHeight: n.h + 'px' }
}
</script>

<style scoped>
.ft-enter-active, .ft-leave-active { transition: opacity .15s, transform .15s; }
.ft-enter-from, .ft-leave-to { opacity: 0; transform: translateY(4px); }
</style>
