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
      <span v-if="props.nodes.length > 0 && !hasSpine" class="text-xs text-red-400">
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

          <!-- Spine trunk guides (faint, behind cards) -->
          <line v-for="(g, i) in cv!.trunkGuides" :key="'tg'+i"
                v-show="!g.hidden"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- Marriage lines (red) -->
          <line v-for="m in cv!.marriages" :key="m.id"
                v-show="!m.hidden"
                :x1="m.x1" :y1="m.y" :x2="m.x2" :y2="m.y"
                stroke="#dc2626" stroke-width="2" stroke-linecap="round" />

          <!-- Vertical drops (parent → child) -->
          <line v-for="(d, i) in cv!.drops" :key="'d'+i"
                v-show="!d.hidden"
                :x1="d.x" :y1="d.y1" :x2="d.x" :y2="d.y2"
                :stroke="d.stroke || '#9ca3af'" stroke-width="1.5"
                stroke-linecap="round"
                :stroke-dasharray="d.dashed ? '6,4' : ''" />

          <!-- Horizontal bars -->
          <line v-for="(b, i) in cv!.hbars" :key="'b'+i"
                v-show="!b.hidden"
                :x1="b.x1" :y1="b.y" :x2="b.x2" :y2="b.y"
                :stroke="b.stroke || '#9ca3af'" stroke-width="1.5"
                stroke-linecap="round"
                :stroke-dasharray="b.dashed ? '6,4' : ''" />
        </svg>

        <!-- ② Person and clan cards -->
        <div
          v-for="n in cv!.nodes" :key="n.id"
          v-show="!n.hidden"
          class="node-card absolute"
          :class="cardClass(n)"
          :style="cardStyle(n)"
          @click.stop="onCardClick(n)"
        >
          <div v-if="n.spineKind === 'A'"      class="absolute left-0 top-2 bottom-2 w-[3px] bg-amber-400 rounded-full" />
          <div v-else-if="n.spineKind === 'B'" class="absolute left-0 top-2 bottom-2 w-[3px] bg-rose-400 rounded-full" />
          <div v-else-if="n.spineKind === 'S'" class="absolute left-0 top-2 bottom-2 w-[3px] bg-amber-400 rounded-full" />
          <div class="px-2.5 py-1.5" :class="n.spineKind ? 'pl-4' : ''">
            <div class="text-[9px] font-medium leading-none mb-0.5 tracking-wide opacity-60"
                 :class="genLabelColor(n)">
              {{ n.genLabel }}
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
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoomIn">+</button>
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoomOut">−</button>
        <div class="text-[9px] text-gray-400 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</div>
        <button class="px-1 py-1.5 bg-white/90 border border-amber-300 rounded-lg text-amber-600
                       text-[10px] font-medium shadow-sm hover:bg-amber-50 transition leading-tight
                       text-center cursor-default"
                @click.stop="fitSpine">定位<br>主幹</button>
      </div>

      <!-- Legend (only at top level) -->
      <div v-if="!props.rootId" class="absolute bottom-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-2 text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-0.5">
        <div class="flex items-center gap-1.5"><span class="w-3 h-[3px] bg-amber-400 rounded-full" />主幹 A：馬太譜系（猶大→所羅門→約瑟）</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-[3px] bg-rose-400 rounded-full" />主幹 B：路加譜系（猶大→拿單→馬利亞）</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-0 border-t border-dashed border-gray-400" />虛線：法律關係（約瑟→耶穌）</div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">滾輪：上下/左右移動　·　Ctrl+滾輪：縮放　·　拖曳：平移</div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'BiblicalSpineTree' })

interface BreadcrumbItem { id: string; name: string }

const props = defineProps<{
  nodes: any[]
  edges: any[]
  rootId?: string                   // when set: recursive single-spine mode
  breadcrumb?: BreadcrumbItem[]     // navigation crumbs (recursive only)
}>()
const emit = defineEmits<{
  selectPerson:    [id: string]
  closeRecursive:  []
}>()

// ── Layout constants ──────────────────────────────────────────────────
const NW          = 120  // person card width
const NH          = 52   // person card height
const CW          = 108  // clan card width
const CH          = 52
const MG          = 12   // wife stacking gap
const HG          = 20   // horizontal gap between cards
const VG          = 90   // vertical gap between rows
const RH          = NH + VG
const PAD         = 48
const MAR_GAP     = Math.round(VG / 2)
const DIVERGE_X   = 320  // half-distance between spine A and B center columns

const baseName  = (s: string) => s.split('（')[0].trim()
const shortName = (s: string) => { const b = baseName(s); return b.length <= 7 ? b : b.slice(0, 6) + '…' }
const rowY      = (row: number) => row * RH + PAD

// ── Graph maps ────────────────────────────────────────────────────────
const personById = computed(() => {
  const m = new Map<string, any>()
  for (const n of props.nodes) m.set(n.id, n)
  return m
})
const personByName = computed(() => {
  const m = new Map<string, any>()
  for (const n of props.nodes) m.set(n.data.name, n)
  return m
})

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
const parentsOf = computed(() => {
  const m = new Map<string, string[]>()
  for (const e of props.edges) {
    if (e.data?.relationshipType === 'parentChild') {
      if (!m.has(e.target)) m.set(e.target, [])
      m.get(e.target)!.push(e.source)
    }
  }
  return m
})

const relationKindMap = computed(() => {
  // edge key "parent|child" → 'legal' | 'biological'
  const m = new Map<string, string>()
  for (const e of props.edges) {
    if (e.data?.relationshipType === 'parentChild' && e.data?.relationKind) {
      m.set(`${e.source}|${e.target}`, e.data.relationKind)
    }
  }
  return m
})

// ── Spine path computation ────────────────────────────────────────────
function bfsPath(src: string, dst: string, ch: Map<string, string[]>): string[] {
  if (src === dst) return [src]
  const queue: string[][] = [[src]]
  const vis = new Set<string>()
  while (queue.length) {
    const path = queue.shift()!
    const cur  = path[path.length - 1]
    if (cur === dst) return path
    if (vis.has(cur)) continue
    vis.add(cur)
    for (const c of ch.get(cur) ?? []) if (!vis.has(c)) queue.push([...path, c])
  }
  return []
}

function resolveByName(name: string): string | undefined {
  return personByName.value.get(name)?.id
}

function spineFromWaypoints(names: string[], ch: Map<string, string[]>): string[] {
  const ids = names.map(resolveByName).filter(Boolean) as string[]
  if (ids.length < 2) return []
  const path: string[] = []
  for (let i = 0; i < ids.length - 1; i++) {
    const seg = bfsPath(ids[i], ids[i + 1], ch)
    if (!seg.length) return []
    if (i === 0) path.push(...seg)
    else path.push(...seg.slice(1))
  }
  return path
}

// Longest descent from a root (for recursive/single mode)
function longestDescent(rootId: string, ch: Map<string, string[]>): string[] {
  const memo = new Map<string, string[]>()
  function dfs(id: string, vis: Set<string>): string[] {
    if (memo.has(id)) return memo.get(id)!
    if (vis.has(id)) return [id]
    vis.add(id)
    let best: string[] = [id]
    for (const c of ch.get(id) ?? []) {
      const sub = dfs(c, new Set(vis))
      if (1 + sub.length > best.length) best = [id, ...sub]
    }
    memo.set(id, best)
    return best
  }
  return dfs(rootId, new Set())
}

// Top-level dual-spine waypoints (use names that exist in DB)
const SPINE_A_WAYPOINTS = [
  '亞當', '塞特', '挪亞', '閃', '亞伯拉罕', '以撒', '雅各',
  '猶大', '大衛（耶西之子）', '所羅門（大衛之子）',
  '雅各（馬但之子）', '約瑟（馬利亞之夫）', '耶穌（拿撒勒人）',
]
const SPINE_B_WAYPOINTS = [
  '亞當', '塞特', '挪亞', '閃', '亞伯拉罕', '以撒', '雅各',
  '猶大', '大衛（耶西之子）', '拿單（大衛之子）',
  '瑪塔（路加 3:24）', '約亞敬（聖母之父）', '馬利亞（耶穌之母）', '耶穌（拿撒勒人）',
]

const isDualMode = computed(() => !props.rootId)

const spineA = computed(() => isDualMode.value ? spineFromWaypoints(SPINE_A_WAYPOINTS, childrenOf.value) : [])
const spineB = computed(() => isDualMode.value ? spineFromWaypoints(SPINE_B_WAYPOINTS, childrenOf.value) : [])
const spineSingle = computed(() => isDualMode.value || !props.rootId ? [] : longestDescent(props.rootId, childrenOf.value))

const jesusId = computed(() => resolveByName('耶穌（拿撒勒人）'))

// Shared trunk (prefix that both A and B agree on)
const sharedTrunkIds = computed(() => {
  if (!isDualMode.value) return []
  const a = spineA.value, b = spineB.value
  if (!a.length || !b.length) return []
  const setB = new Set(b)
  const shared: string[] = []
  for (const id of a) {
    if (setB.has(id)) shared.push(id)
    else break
  }
  return shared
})

// Spine A unique (after shared trunk, excluding final Jesus)
const spineAUniqueIds = computed(() => {
  if (!isDualMode.value) return []
  const a = spineA.value
  const sharedLen = sharedTrunkIds.value.length
  const out: string[] = []
  for (let i = sharedLen; i < a.length; i++) {
    if (a[i] === jesusId.value) break
    out.push(a[i])
  }
  return out
})
const spineBUniqueIds = computed(() => {
  if (!isDualMode.value) return []
  const b = spineB.value
  const sharedLen = sharedTrunkIds.value.length
  const out: string[] = []
  for (let i = sharedLen; i < b.length; i++) {
    if (b[i] === jesusId.value) break
    out.push(b[i])
  }
  return out
})

const hasSpine = computed(() => {
  if (isDualMode.value) return spineA.value.length > 0 && spineB.value.length > 0
  return spineSingle.value.length > 0
})

// All ids on any spine (for non-spine detection)
const spineMembership = computed(() => {
  const m = new Map<string, 'A' | 'B' | 'S' | 'single'>()
  if (isDualMode.value) {
    for (const id of sharedTrunkIds.value) m.set(id, 'S')
    for (const id of spineAUniqueIds.value) m.set(id, 'A')
    for (const id of spineBUniqueIds.value) m.set(id, 'B')
    if (jesusId.value) m.set(jesusId.value, 'S')
  } else {
    for (const id of spineSingle.value) m.set(id, 'single')
  }
  return m
})

// ── Clan collector ────────────────────────────────────────────────────
function subtreeIds(id: string, vis = new Set<string>()): string[] {
  if (vis.has(id)) return []
  vis.add(id)
  return [id, ...(childrenOf.value.get(id) ?? []).flatMap(c => subtreeIds(c, vis))]
}

// ── Node interface ────────────────────────────────────────────────────
interface LNode {
  id: string
  rawName: string
  displayName: string
  genLabel: string
  generation: number
  gender: string
  x: number; y: number; w: number; h: number
  spineKind: 'A' | 'B' | 'S' | 'single' | null
  isClan: boolean
  isExpansionNode?: boolean   // node belongs to an expanded subtree
  clanCount?: number
  clanMemberIds?: string[]
  clanParentId?: string       // spine parent — used to toggle expansion
  clanCollapsed?: boolean     // for clan cards: shows ▼ when collapsed, ▲ when expanded
  hidden?: boolean            // occluded by another expansion → render invisible
}
interface VDrop { x: number; y1: number; y2: number; stroke?: string; dashed?: boolean; hidden?: boolean }
interface HBar  { x1: number; x2: number; y: number; stroke?: string; dashed?: boolean; hidden?: boolean }
interface MLine { id: string; x1: number; x2: number; y: number; hidden?: boolean }
interface TrunkGuide { x: number; y1: number; y2: number; color: string; hidden?: boolean }
interface ExpansionBox { x1: number; y1: number; x2: number; y2: number }

function getGenLabel(p: any): string {
  // Backend already formats as "L23" / "J33" / "第 N 代" / "" — just use it
  return p?.data?.generation ?? ''
}

// ── Helpers for placing a single spine person ─────────────────────────
interface PlaceParams {
  centerX: number              // spine column center X
  row: number                  // row index for this spine person
  childRow: number             // row index for spine child (next on the spine)
  wifeSide: 'left' | 'right'
  clanSide: 'left' | 'right'
}

// ── Main layout ───────────────────────────────────────────────────────
const cv = computed(() => {
  if (!hasSpine.value) return null

  const ch    = childrenOf.value
  const sp    = spousesOf.value
  const pMap  = personById.value
  const rk    = relationKindMap.value
  const membership = spineMembership.value

  const nodes:     LNode[] = []
  const drops:     VDrop[] = []
  const hbars:     HBar[]  = []
  const marriages: MLine[] = []
  const trunkGuides: TrunkGuide[] = []
  const shown = new Set<string>()
  const crossSpineDrawn = new Set<string>()  // dedup cross-spine marriage lines
  const expansionBoxes: ExpansionBox[] = [] // for occlusion detection
  const expansionNodeIds = new Set<string>() // nodes inside expanded subtrees

  // ── Subtree layout (used by in-place expansion) ────────────────────
  const SUB_RH = NH + 40   // tighter row gap inside expansions
  const SUB_HG = 16
  const subRowY = (depth: number, startY: number) => startY + depth * SUB_RH

  function layoutSubtree(
    rootId: string,
    depth: number,
    leftX: number,
    startY: number,
    vis: Set<string>,
  ): { nodes: LNode[]; drops: VDrop[]; hbars: HBar[]; maxX: number; maxY: number; rootCX: number } {
    if (vis.has(rootId)) {
      return { nodes: [], drops: [], hbars: [], maxX: leftX, maxY: startY, rootCX: leftX }
    }
    vis.add(rootId)
    const p = pMap.get(rootId)
    if (!p) {
      return { nodes: [], drops: [], hbars: [], maxX: leftX, maxY: startY, rootCX: leftX }
    }
    const kids = (childrenOf.value.get(rootId) ?? []).filter(c => !vis.has(c))

    const myY = subRowY(depth, startY)

    // Leaf: just place the node
    if (kids.length === 0) {
      const myNode: LNode = {
        id: rootId,
        rawName:     p.data.name,
        displayName: shortName(p.data.name),
        genLabel:    getGenLabel(p),
        generation:  p.data.generationNum || 0,
        gender:      p.data.gender,
        x: leftX, y: myY, w: NW, h: NH,
        spineKind:   null,
        isClan:      false,
        isExpansionNode: true,
      }
      return { nodes: [myNode], drops: [], hbars: [], maxX: leftX + NW, maxY: myY + NH, rootCX: leftX + NW / 2 }
    }

    // Internal: lay out kids first, then center root above them
    let cursorX = leftX
    const childResults: ReturnType<typeof layoutSubtree>[] = []
    let maxY = myY + NH
    for (const k of kids) {
      const r = layoutSubtree(k, depth + 1, cursorX, startY, vis)
      childResults.push(r)
      cursorX = r.maxX + SUB_HG
      maxY = Math.max(maxY, r.maxY)
    }
    const rightEdge = cursorX - SUB_HG
    const childrenWidth = rightEdge - leftX
    const rootX  = leftX + Math.max(0, childrenWidth - NW) / 2
    const rootCX = rootX + NW / 2
    const myNode: LNode = {
      id: rootId,
      rawName:     p.data.name,
      displayName: shortName(p.data.name),
      genLabel:    getGenLabel(p),
      generation:  p.data.generationNum || 0,
      gender:      p.data.gender,
      x: rootX, y: myY, w: NW, h: NH,
      spineKind:   null,
      isClan:      false,
      isExpansionNode: true,
    }
    // Connector lines: root → bar → each child
    const myDrops: VDrop[] = []
    const myHbars: HBar[]  = []
    const childCXs = childResults.map(r => r.rootCX)
    const barY = myY + NH + 12
    myDrops.push({ x: rootCX, y1: myY + NH, y2: barY })
    if (childCXs.length === 1) {
      myHbars.push({ x1: Math.min(rootCX, childCXs[0]), x2: Math.max(rootCX, childCXs[0]), y: barY })
      myDrops.push({ x: childCXs[0], y1: barY, y2: subRowY(depth + 1, startY) })
    } else {
      myHbars.push({ x1: Math.min(...childCXs), x2: Math.max(...childCXs), y: barY })
      for (const cc of childCXs) {
        myDrops.push({ x: cc, y1: barY, y2: subRowY(depth + 1, startY) })
      }
    }
    return {
      nodes: [myNode, ...childResults.flatMap(r => r.nodes)],
      drops: [...myDrops, ...childResults.flatMap(r => r.drops)],
      hbars: [...myHbars, ...childResults.flatMap(r => r.hbars)],
      maxX:  rightEdge,
      maxY,
      rootCX,
    }
  }

  function layoutExpansion(
    rootIds: string[],
    startX: number,
    startY: number,
    _side: 'left' | 'right',
  ): { nodes: LNode[]; drops: VDrop[]; hbars: HBar[]; bbox: ExpansionBox } {
    const vis = new Set<string>()
    let cursorX = startX
    const allNodes: LNode[] = []
    const allDrops: VDrop[] = []
    const allHbars: HBar[]  = []
    let maxY = startY
    for (const rid of rootIds) {
      const r = layoutSubtree(rid, 0, cursorX, startY, vis)
      allNodes.push(...r.nodes)
      allDrops.push(...r.drops)
      allHbars.push(...r.hbars)
      cursorX = r.maxX + SUB_HG
      maxY = Math.max(maxY, r.maxY)
    }
    // Record the bbox for occlusion detection
    const minX = Math.min(...allNodes.map(n => n.x))
    const maxX = Math.max(...allNodes.map(n => n.x + n.w))
    for (const n of allNodes) expansionNodeIds.add(n.id)
    return {
      nodes: allNodes,
      drops: allDrops,
      hbars: allHbars,
      bbox: { x1: minX - 8, y1: startY - 8, x2: maxX + 8, y2: maxY + 8 },
    }
  }

  // Determine: which spine person → row index
  // For uniform row pitch, use row = (index in spine), starting from 0 for the top of this view.
  const rowOf = new Map<string, number>()

  let bottomRow = 0

  if (isDualMode.value) {
    const shared = sharedTrunkIds.value
    const aUniq  = spineAUniqueIds.value
    const bUniq  = spineBUniqueIds.value

    // Shared trunk: rows 0..shared.length-1
    shared.forEach((id, i) => rowOf.set(id, i))

    const sharedEndRow = shared.length - 1

    // Stretch the shorter spine so both spines' bottoms land on the same row
    // (so 約瑟 [Matthew's last] and 馬利亞 [Luke's last] share a horizontal line,
    //  then Jesus drops below both).
    const maxLen = Math.max(aUniq.length, bUniq.length)
    const aStretch = aUniq.length > 1 ? (maxLen - 1) / (aUniq.length - 1) : 1
    const bStretch = bUniq.length > 1 ? (maxLen - 1) / (bUniq.length - 1) : 1

    aUniq.forEach((id, i) => rowOf.set(id, sharedEndRow + 1 + i * aStretch))
    bUniq.forEach((id, i) => rowOf.set(id, sharedEndRow + 1 + i * bStretch))

    // Jesus row = one row below the aligned bottoms of both spines
    bottomRow = sharedEndRow + maxLen + 1
    if (jesusId.value) rowOf.set(jesusId.value, bottomRow)
  } else {
    // Single spine: rows 0..N-1
    spineSingle.value.forEach((id, i) => rowOf.set(id, i))
    bottomRow = spineSingle.value.length - 1
  }

  // ── Wife counts to size the X canvas ───────────────────────────────
  const allSpineIds = Array.from(rowOf.keys())
  const maxWives = Math.max(0, ...allSpineIds.map(id => (sp.get(id) ?? []).length))

  // Wife area width (per side, both spines may have wives outside)
  const wifeAreaW = maxWives > 0
    ? MAR_GAP + maxWives * NW + Math.max(0, maxWives - 1) * MG
    : 0

  // Layout center
  const PAD_X = PAD + wifeAreaW
  let SHARED_CX: number, SPINE_A_CX: number, SPINE_B_CX: number, SINGLE_CX: number

  if (isDualMode.value) {
    SHARED_CX  = PAD_X + DIVERGE_X + NW / 2  // shared trunk center
    SPINE_A_CX = SHARED_CX + DIVERGE_X
    SPINE_B_CX = SHARED_CX - DIVERGE_X
    SINGLE_CX  = SHARED_CX  // unused in dual mode
  } else {
    SINGLE_CX  = PAD_X + NW / 2
    SHARED_CX  = SINGLE_CX
    SPINE_A_CX = SINGLE_CX
    SPINE_B_CX = SINGLE_CX
  }

  const cxOf = (id: string): number => {
    if (!isDualMode.value) return SINGLE_CX
    const k = membership.get(id)
    if (k === 'A') return SPINE_A_CX
    if (k === 'B') return SPINE_B_CX
    return SHARED_CX  // 'S' or jesus
  }

  // ── Trunk guides ───────────────────────────────────────────────────
  if (isDualMode.value) {
    const sharedFirst = sharedTrunkIds.value[0]
    const sharedLast  = sharedTrunkIds.value[sharedTrunkIds.value.length - 1]
    const aFirst = spineAUniqueIds.value[0]
    const aLast  = spineAUniqueIds.value[spineAUniqueIds.value.length - 1]
    const bFirst = spineBUniqueIds.value[0]
    const bLast  = spineBUniqueIds.value[spineBUniqueIds.value.length - 1]
    if (sharedFirst && sharedLast) {
      trunkGuides.push({ x: SHARED_CX, y1: rowY(rowOf.get(sharedFirst)!), y2: rowY(rowOf.get(sharedLast)!) + NH, color: '#f59e0b' })
    }
    if (aFirst && aLast) {
      trunkGuides.push({ x: SPINE_A_CX, y1: rowY(rowOf.get(aFirst)!), y2: rowY(rowOf.get(aLast)!) + NH, color: '#f59e0b' })
    }
    if (bFirst && bLast) {
      trunkGuides.push({ x: SPINE_B_CX, y1: rowY(rowOf.get(bFirst)!), y2: rowY(rowOf.get(bLast)!) + NH, color: '#f43f5e' })
    }
  } else {
    if (spineSingle.value.length) {
      const first = spineSingle.value[0]
      const last  = spineSingle.value[spineSingle.value.length - 1]
      trunkGuides.push({ x: SINGLE_CX, y1: rowY(rowOf.get(first)!), y2: rowY(rowOf.get(last)!) + NH, color: '#f59e0b' })
    }
  }

  // ── Place all spine person cards ───────────────────────────────────
  for (const sid of allSpineIds) {
    const p = pMap.get(sid); if (!p) continue
    const cx = cxOf(sid)
    const row = rowOf.get(sid)!
    nodes.push({
      id: sid,
      rawName:     p.data.name,
      displayName: shortName(p.data.name),
      genLabel:    getGenLabel(p),
      generation:  p.data.generationNum || 0,
      gender:      p.data.gender,
      x: cx - NW / 2, y: rowY(row), w: NW, h: NH,
      spineKind:   membership.get(sid) ?? null,
      isClan:      false,
    })
    shown.add(sid)
  }

  // ── Per spine person: wives, clans, child lines ────────────────────
  // Each spine person has:
  //  - spine-child(ren) (for layout, just down/diagonal lines)
  //  - non-spine children → clan card
  //  - wives → laid out to the outer side (toward outside of dual-spine)
  function placeOne(sid: string) {
    const p = pMap.get(sid); if (!p) return
    const cx = cxOf(sid)
    const row = rowOf.get(sid)!
    const k   = membership.get(sid)

    // Determine wife side & clan side
    // dual mode: shared/Jesus → wives left, clans right (no other column nearby)
    //            A → wives right (outside), clans left (inside between A & B)
    //            B → wives left  (outside), clans right (inside between A & B)
    // single mode: wives left, clans right (original)
    let wifeSide: 'left' | 'right' = 'left'
    let clanSide: 'left' | 'right' = 'right'
    if (isDualMode.value) {
      if (k === 'A') { wifeSide = 'right'; clanSide = 'left' }
      else if (k === 'B') { wifeSide = 'left'; clanSide = 'right' }
    }

    // Spine children of this person (could be 0, 1, or 2 for David)
    const spineChildIds: string[] = []
    for (const c of ch.get(sid) ?? []) {
      if (rowOf.has(c)) spineChildIds.push(c)
    }

    // Wives — split into "regular" (need card placed here) vs "cross-spine"
    // (already placed on another spine; just draw a direct marriage bridge).
    const allWifeIds      = sp.get(sid) ?? []
    const crossSpineWives = allWifeIds.filter(wid => rowOf.has(wid))
    const wifeIds         = allWifeIds.filter(wid => !rowOf.has(wid))
    const wifeLX          = new Map<string, number>()
    const marLineY        = rowY(row) + NH / 2

    // Cross-spine marriages: draw once per pair (dedupe via sorted key)
    for (const cwid of crossSpineWives) {
      const pairKey = [sid, cwid].sort().join('|')
      if (crossSpineDrawn.has(pairKey)) continue
      crossSpineDrawn.add(pairKey)
      const partner = nodes.find(n => n.id === cwid)
      if (!partner) continue
      const hL = cx - NW / 2, hR = cx + NW / 2
      const pL = partner.x,   pR = partner.x + partner.w
      if (pR < hL)       marriages.push({ id: `mscross_${pairKey}`, x1: pR, x2: hL, y: marLineY })
      else if (pL > hR)  marriages.push({ id: `mscross_${pairKey}`, x1: hR, x2: pL, y: marLineY })
    }

    for (let wi = 0; wi < wifeIds.length; wi++) {
      const wid = wifeIds[wi]
      let wx: number
      if (wifeSide === 'left') {
        wx = (cx - NW / 2) - MAR_GAP - (wi + 1) * NW - wi * MG
      } else {
        wx = (cx + NW / 2) + MAR_GAP + wi * (NW + MG)
      }
      wifeLX.set(wid, wx)

      if (!shown.has(wid)) {
        shown.add(wid)
        const wp = pMap.get(wid)
        if (wp) nodes.push({
          id: wid,
          rawName:     wp.data.name,
          displayName: shortName(wp.data.name),
          genLabel:    getGenLabel(wp),
          generation:  wp.data.generationNum || 0,
          gender:      wp.data.gender,
          x: wx, y: rowY(row), w: NW, h: NH,
          spineKind:   null,
          isClan:      false,
        })
      }

      // Marriage line — only the gap between card edges
      if (wifeSide === 'left') {
        if (wi === 0) {
          marriages.push({ id: `ms_${sid}_0`, x1: wx + NW, x2: cx - NW / 2, y: marLineY })
        } else {
          const prevWx = wifeLX.get(wifeIds[wi - 1])!
          marriages.push({ id: `ms_${sid}_${wi}`, x1: wx + NW, x2: prevWx, y: marLineY })
        }
      } else {
        if (wi === 0) {
          marriages.push({ id: `ms_${sid}_0`, x1: cx + NW / 2, x2: wx, y: marLineY })
        } else {
          const prevWx = wifeLX.get(wifeIds[wi - 1])!
          marriages.push({ id: `ms_${sid}_${wi}`, x1: prevWx + NW, x2: wx, y: marLineY })
        }
      }
    }

    // Marriage midpoint X — only shifts when there are *stacked* wives on this row.
    // Cross-spine spouses go through their own column, so midX stays at cx.
    let midX = cx
    if (wifeIds.length > 0) {
      if (wifeSide === 'left') midX = cx - NW / 2 - Math.round(MAR_GAP / 2)
      else                     midX = cx + NW / 2 + Math.round(MAR_GAP / 2)
    }

    // ── NEW: Place ALL first-gen kids individually (per user rule) ────
    // Rules:
    //   1. Group by mother in marriage order — 大老婆 group goes right, 小老婆 left
    //   2. Within same mother, 兄右弟左 (canonical order in husband.children = birth order)
    //   3. Unattributed-to-wife kids appended at the left
    //   4. Spine kids stay pinned at their spine-column X (current behavior)
    //   5. Non-spine kids with descendants get a ▼ clan card directly below them
    //      (click to expand the subtree in-place; ▲ to collapse).
    //   6. Kids without descendants render as plain cards, no clan attached.

    const spouseSetAll = new Set([sid, ...allWifeIds])

    // Build raw kid list: husband.children first (canonical order), then wives' kids
    // not already in the list. allWifeIds is used so we group by ALL wives including
    // any cross-spine spouse (e.g., Joseph↔Mary).
    const allKidsRaw: string[] = []
    for (const c of ch.get(sid) ?? []) {
      if (!spouseSetAll.has(c)) allKidsRaw.push(c)
    }
    for (const wid of allWifeIds) {
      for (const c of ch.get(wid) ?? []) {
        if (!spouseSetAll.has(c) && !allKidsRaw.includes(c)) allKidsRaw.push(c)
      }
    }

    if (allKidsRaw.length === 0) return  // no kids → nothing more to do

    // Attribute each kid → mother (first wife whose children list contains them)
    const kidMom = new Map<string, string | null>()
    for (const kid of allKidsRaw) {
      let mom: string | null = null
      for (const wid of allWifeIds) {
        if ((ch.get(wid) ?? []).includes(kid)) { mom = wid; break }
      }
      kidMom.set(kid, mom)
    }

    // Order RTL: first wife's kids first (rightmost), within wife by appearance order
    const orderedRTL: string[] = []
    const hasLinkage = Array.from(kidMom.values()).some(v => v !== null)
    if (hasLinkage) {
      for (const wid of allWifeIds) {
        for (const kid of allKidsRaw) {
          if (kidMom.get(kid) === wid) orderedRTL.push(kid)
        }
      }
      for (const kid of allKidsRaw) {
        if (kidMom.get(kid) === null) orderedRTL.push(kid)
      }
    } else {
      orderedRTL.push(...allKidsRaw)
    }

    // Compute X for each kid
    const KID_GAP = NW + HG
    const kidX = new Map<string, number>()

    // Spine kids: forced to spine column
    for (const sk of spineChildIds) kidX.set(sk, cxOf(sk))

    const spineKidIdxs = new Map<string, number>()
    for (const sk of spineChildIds) spineKidIdxs.set(sk, orderedRTL.indexOf(sk))

    if (spineChildIds.length === 0) {
      // No spine kid (rare). Center kids around parent cx.
      orderedRTL.forEach((k, i) => {
        kidX.set(k, cx + ((orderedRTL.length - 1) / 2 - i) * KID_GAP)
      })
    } else {
      // Has spine kid(s). Non-spine kids fan out around them.
      const validSpineIdxs = Array.from(spineKidIdxs.values()).filter(i => i >= 0)
      const minSpineIdx = validSpineIdxs.length ? Math.min(...validSpineIdxs) : 0
      const maxSpineIdx = validSpineIdxs.length ? Math.max(...validSpineIdxs) : 0

      const spineByX     = [...spineChildIds].sort((a, b) => kidX.get(b)! - kidX.get(a)!)
      const rightmostSpX = kidX.get(spineByX[0])!
      const leftmostSpX  = kidX.get(spineByX[spineByX.length - 1])!

      const rightGroup: string[] = []  // natural idx < minSpineIdx → place RIGHT of rightmost spine kid
      const leftGroup:  string[] = []  // natural idx > maxSpineIdx → place LEFT of leftmost spine kid
      const betweenGroup: string[] = []

      orderedRTL.forEach((kid, idx) => {
        if (spineKidIdxs.has(kid)) return
        if (idx < minSpineIdx) rightGroup.push(kid)
        else if (idx > maxSpineIdx) leftGroup.push(kid)
        else betweenGroup.push(kid)
      })

      // rightGroup: natural order has rightmost-natural FIRST (idx 0 = furthest right).
      // We want furthest-right kid placed at largest X — so walk rightGroup from the END.
      for (let i = 0; i < rightGroup.length; i++) {
        const kid = rightGroup[rightGroup.length - 1 - i]
        kidX.set(kid, rightmostSpX + (i + 1) * KID_GAP)
      }
      // leftGroup: natural order has leftmost-natural LAST. Closest-to-spine = first in leftGroup.
      for (let i = 0; i < leftGroup.length; i++) {
        kidX.set(leftGroup[i], leftmostSpX - (i + 1) * KID_GAP)
      }
      // betweenGroup: evenly between leftmost and rightmost spine kids
      if (betweenGroup.length > 0 && rightmostSpX > leftmostSpX) {
        const span = rightmostSpX - leftmostSpX
        for (let i = 0; i < betweenGroup.length; i++) {
          kidX.set(betweenGroup[i], leftmostSpX + ((i + 1) / (betweenGroup.length + 1)) * span)
        }
      }
    }

    // childY: align with spine kid's row if any; else use parent row + 1
    const childY = spineChildIds.length > 0
      ? rowY(rowOf.get(spineChildIds[0])!)
      : rowY(row + 1)

    // Place kid cards (spine kids are already in the nodes array; skip them here)
    for (const kid of orderedRTL) {
      if (rowOf.has(kid)) continue  // spine kid already rendered
      if (shown.has(kid)) continue
      shown.add(kid)
      const kp = pMap.get(kid)
      if (!kp) continue
      const kxVal = kidX.get(kid)!
      nodes.push({
        id: kid,
        rawName:     kp.data.name,
        displayName: shortName(kp.data.name),
        genLabel:    getGenLabel(kp),
        generation:  kp.data.generationNum || 0,
        gender:      kp.data.gender,
        x: kxVal - NW / 2, y: childY, w: NW, h: NH,
        spineKind:   null,
        isClan:      false,
      })

      // 2nd-gen onwards: ▼ clan card directly below, if this kid has any descendants
      const subtree = subtreeIds(kid).filter(id => id !== kid)
      if (subtree.length > 0) {
        const expanded  = expandedClans.value.has(kid)
        const baseLabel = `${baseName(kp.data.name)}支系`
        const label     = expanded ? `▲ 收起 ${baseLabel}` : `▼ ${baseLabel}`
        const clanCardY = childY + NH + 16
        nodes.push({
          id: `clan_${kid}`,
          rawName:     baseLabel,
          displayName: label,
          genLabel:    `旁支 · ${subtree.length}人`,
          generation:  0,
          gender: '',
          x: kxVal - CW / 2, y: clanCardY, w: CW, h: CH,
          spineKind:   null,
          isClan:      true,
          clanCount:   subtree.length,
          clanMemberIds: subtree,
          clanParentId: kid,
          clanCollapsed: !expanded,
        })
        drops.push({ x: kxVal, y1: childY + NH, y2: clanCardY })

        if (expanded) {
          const kidChildren = (ch.get(kid) ?? []).filter(c => !rowOf.has(c))
          if (kidChildren.length > 0) {
            const exp = layoutExpansion(kidChildren, kxVal - NW, clanCardY + CH + 20, 'right')
            nodes.push(...exp.nodes)
            drops.push(...exp.drops)
            hbars.push(...exp.hbars)
            expansionBoxes.push(exp.bbox)
          }
        }
      }
    }

    // T-bar from marriage midpoint to all kids (one drop per kid, colored per relationship)
    const allKidXs = orderedRTL.map(k => kidX.get(k)!).filter(v => v !== undefined)
    if (allKidXs.length > 0) {
      const barY = marLineY + Math.round((childY - marLineY) * 0.5)
      const minBarX = Math.min(midX, ...allKidXs)
      const maxBarX = Math.max(midX, ...allKidXs)
      drops.push({ x: midX, y1: marLineY, y2: barY })
      hbars.push({ x1: minBarX, x2: maxBarX, y: barY })
      const parentKind = membership.get(sid)
      for (const kid of orderedRTL) {
        const kxVal   = kidX.get(kid)!
        const isSpKid = rowOf.has(kid)
        const childKind = membership.get(kid)
        const isLegal = rk.get(`${sid}|${kid}`) === 'legal'
        const continuingKind = parentKind === 'S' ? (childKind ?? 'S') : parentKind
        const lineStroke = isLegal
          ? '#9ca3af'
          : !isSpKid                          ? '#9ca3af'
          : continuingKind === 'B'            ? '#f43f5e'
          : continuingKind === 'A'            ? '#f59e0b'
          : continuingKind === 'S'            ? '#f59e0b'
          : continuingKind === 'single'       ? '#f59e0b'
          :                                     '#6b7280'
        const kidActualY = isSpKid ? rowY(rowOf.get(kid)!) : childY
        drops.push({ x: kxVal, y1: barY, y2: kidActualY, stroke: lineStroke, dashed: isLegal })
      }
    }
  }

  for (const sid of allSpineIds) placeOne(sid)

  // ── Occlusion: anything overlapping an expansion bbox becomes hidden ──
  function boxOverlap(a: ExpansionBox, b: ExpansionBox): boolean {
    return !(a.x2 < b.x1 || a.x1 > b.x2 || a.y2 < b.y1 || a.y1 > b.y2)
  }
  function lineIntersectsBox(x1: number, y1: number, x2: number, y2: number, b: ExpansionBox): boolean {
    // axis-aligned line clip vs rect — works for both verticals (x1==x2) and horizontals (y1==y2)
    const minX = Math.min(x1, x2), maxX = Math.max(x1, x2)
    const minY = Math.min(y1, y2), maxY = Math.max(y1, y2)
    return !(maxX < b.x1 || minX > b.x2 || maxY < b.y1 || minY > b.y2)
  }
  if (expansionBoxes.length > 0) {
    for (const n of nodes) {
      if (n.isExpansionNode) continue
      // Spine parents whose own clan is expanded — keep them visible (they sit ABOVE the bbox)
      const nBox: ExpansionBox = { x1: n.x, y1: n.y, x2: n.x + n.w, y2: n.y + n.h }
      if (expansionBoxes.some(b => boxOverlap(nBox, b))) n.hidden = true
    }
    for (const d of drops) {
      if (expansionBoxes.some(b => lineIntersectsBox(d.x, d.y1, d.x, d.y2, b))) d.hidden = true
    }
    for (const b of hbars) {
      if (expansionBoxes.some(box => lineIntersectsBox(b.x1, b.y, b.x2, b.y, box))) b.hidden = true
    }
    for (const m of marriages) {
      if (expansionBoxes.some(box => lineIntersectsBox(m.x1, m.y, m.x2, m.y, box))) m.hidden = true
    }
    for (const g of trunkGuides) {
      if (expansionBoxes.some(box => lineIntersectsBox(g.x, g.y1, g.x, g.y2, box))) g.hidden = true
    }
  }
  // Expansion-internal nodes/lines never hidden — they ARE the expansion
  // (drops/hbars/etc. from the expansion are still in the same arrays, but the
  //  lineIntersectsBox would mark them; suppress that by skipping if endpoints are expansion nodes.
  //  Simpler heuristic: any drop/hbar added by layoutExpansion is already inside a bbox, mark it as such.)
  // We re-walk and unhide anything whose endpoint matches an expansionNodeIds member.
  function endpointIsExpansion(x: number, y: number): boolean {
    for (const n of nodes) {
      if (!n.isExpansionNode) continue
      if (x >= n.x - 4 && x <= n.x + n.w + 4 && y >= n.y - 8 && y <= n.y + n.h + 16) return true
    }
    return false
  }
  for (const d of drops) {
    if (d.hidden && (endpointIsExpansion(d.x, d.y1) || endpointIsExpansion(d.x, d.y2))) d.hidden = false
  }
  for (const b of hbars) {
    if (b.hidden && (endpointIsExpansion(b.x1, b.y) || endpointIsExpansion(b.x2, b.y))) b.hidden = false
  }

  // ── Canvas bounds ──────────────────────────────────────────────────
  const visNodes = nodes.filter(n => !n.hidden)
  const allX = visNodes.flatMap(n => [n.x, n.x + n.w])
  const minX = allX.length ? Math.min(...allX, PAD) : PAD
  const maxX = (allX.length ? Math.max(...allX) : PAD) + PAD
  const maxY = (visNodes.length ? Math.max(...visNodes.map(n => n.y + n.h)) : PAD) + PAD

  // Shift everything so minX >= PAD
  const shift = minX < PAD ? (PAD - minX) : 0
  if (shift > 0) {
    for (const n of nodes) n.x += shift
    for (const d of drops) d.x += shift
    for (const b of hbars) { b.x1 += shift; b.x2 += shift }
    for (const m of marriages) { m.x1 += shift; m.x2 += shift }
    for (const g of trunkGuides) g.x += shift
  }

  // Convergence column X for fitSpine (the shared trunk in dual mode, or single column)
  const convergeCX = (isDualMode.value ? SHARED_CX : SINGLE_CX) + shift

  return {
    nodes, drops, hbars, marriages, trunkGuides,
    w: maxX + shift, h: maxY,
    convergeCX,
    topY: PAD,
    botY: maxY - PAD,
  }
})

const ready = computed(() => !!cv.value && cv.value.nodes.length > 0)

// ── Expansion state — clan toggles in-place ───────────────────────────
// Keyed by the spine parent's id (the spine person whose clan we're expanding).
const expandedClans = ref<Set<string>>(new Set())

function toggleExpand(spineParentId: string) {
  const s = new Set(expandedClans.value)
  if (s.has(spineParentId)) s.delete(spineParentId)
  else s.add(spineParentId)
  expandedClans.value = s
}

// ── Card click ────────────────────────────────────────────────────────
function onCardClick(n: LNode) {
  if (n.isClan && n.clanParentId) {
    // Toggle in-place expansion at the spine parent
    toggleExpand(n.clanParentId)
  } else if (!n.isClan) {
    emit('selectPerson', n.id)
  }
}

// ── Card styling ──────────────────────────────────────────────────────
function cardClass(n: LNode) {
  if (n.isClan)
    return 'border-2 border-dashed border-amber-300 bg-amber-50/90 hover:bg-amber-100/90 rounded-xl cursor-pointer'
  if (n.spineKind === 'A' || n.spineKind === 'S' || n.spineKind === 'single')
    return 'border border-stone-300 bg-white shadow-sm hover:shadow-md rounded-xl cursor-pointer'
  if (n.spineKind === 'B')
    return 'border border-rose-300 bg-white shadow-sm hover:shadow-md rounded-xl cursor-pointer'
  if (n.gender === 'female')
    return 'border border-rose-200 bg-rose-50/90 hover:shadow-sm rounded-xl cursor-pointer'
  return 'border border-slate-200 bg-white hover:shadow-sm rounded-xl cursor-pointer'
}
function cardStyle(n: LNode) {
  return { left: n.x + 'px', top: n.y + 'px', width: n.w + 'px', minHeight: n.h + 'px' }
}
function genLabelColor(n: LNode) {
  if (n.isClan) return 'text-amber-600'
  if (n.spineKind === 'A' || n.spineKind === 'S' || n.spineKind === 'single') return 'text-amber-500'
  if (n.spineKind === 'B') return 'text-rose-500'
  return 'text-slate-400'
}

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
  // Ctrl/Meta + wheel = zoom around cursor; plain wheel = pan
  if (e.ctrlKey || e.metaKey) {
    const vp = viewportRef.value; if (!vp) return
    const { left, top } = vp.getBoundingClientRect()
    const cx = e.clientX - left
    const cy = e.clientY - top
    const newZ  = clamp(zoom.value * (e.deltaY < 0 ? 1.15 : 1 / 1.15))
    const ratio = newZ / zoom.value
    panX.value  = cx - (cx - panX.value) * ratio
    panY.value  = cy - (cy - panY.value) * ratio
    zoom.value  = newZ
    return
  }

  // Pan: deltaY → vertical, deltaX → horizontal (trackpad horizontal swipe)
  // Shift+wheel also swaps Y to X (common convention).
  if (e.shiftKey) {
    panX.value -= e.deltaY
  } else {
    panX.value -= e.deltaX
    panY.value -= e.deltaY
  }
}
function onPointerDown(e: PointerEvent) {
  // Skip cards & any interactive control (buttons, inputs) — let their own click handlers run.
  const t = e.target as HTMLElement
  if (t.closest('.node-card, button, input, a, [data-no-pan]')) return
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
  // Manual "定位主幹" button — fit so 14 rows are visible, centered on the spine.
  if (!cv.value || !viewportRef.value) return
  const vw = viewportRef.value.clientWidth
  const vh = viewportRef.value.clientHeight
  const c  = cv.value
  const targetH = 14 * RH
  const z = clamp(Math.min(vh / targetH, vw / c.w, 0.9))
  zoom.value = z
  panX.value = vw / 2 - c.convergeCX * z
  panY.value = 40
}

function resetToTop() {
  // Default view: 100% zoom, spine centered horizontally, top of chart at top of viewport
  if (!cv.value || !viewportRef.value) return
  const vw = viewportRef.value.clientWidth
  zoom.value = 1
  panX.value = vw / 2 - cv.value.convergeCX
  panY.value = 0
}

watch(ready, val => { if (val) nextTick(resetToTop) }, { immediate: true })
onMounted(() => { if (ready.value) nextTick(resetToTop) })
</script>

<style scoped>
.ft-enter-active, .ft-leave-active { transition: opacity .15s, transform .15s; }
.ft-enter-from, .ft-leave-to       { opacity: 0; transform: translateY(4px); }
</style>
