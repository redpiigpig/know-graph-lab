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

          <!-- Marriage lines (red). Joseph↔Mary is dashed (holy union, see Matt 1:18-25) -->
          <line v-for="m in cv!.marriages" :key="m.id"
                v-show="!m.hidden"
                :x1="m.x1" :y1="m.y" :x2="m.x2" :y2="m.y"
                stroke="#dc2626" stroke-width="2" stroke-linecap="round"
                :stroke-dasharray="m.holy ? '6,4' : ''" />

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

        <!-- ② Person cards -->
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
            <!-- Generation label — reserve fixed height even when empty so cards on the
                 same row align their names regardless of whether the person has gen set -->
            <div class="text-[9px] font-medium leading-none mb-0.5 tracking-wide opacity-60 min-h-[9px]"
                 :class="genLabelColor(n)">
              {{ n.genLabel || ' ' }}
            </div>
            <div class="text-[12px] font-semibold leading-snug text-slate-800"
                 :title="n.rawName">
              {{ n.displayName }}
            </div>
            <div v-if="n.disambig"
                 class="text-[9px] leading-tight text-slate-400 mt-0.5 max-w-[110px] truncate"
                 :title="n.disambig">
              （{{ n.disambig }}）
            </div>
          </div>
          <!-- Subtree toggle (▼/▲), only on kids that have descendants -->
          <button
            v-if="n.hasSubtree"
            class="absolute -bottom-2 left-1/2 -translate-x-1/2 z-10
                   px-1.5 h-4 min-w-[20px] rounded-full bg-white text-[10px] leading-none
                   border border-amber-300 text-amber-600 hover:bg-amber-50 shadow-sm
                   cursor-default flex items-center justify-center gap-0.5 tabular-nums"
            :title="n.subtreeExpanded ? '收起子孫' : `展開 ${n.subtreeSize} 名子孫`"
            @click.stop="toggleExpand(n.personId)"
          >
            <span>{{ n.subtreeExpanded ? '▲' : '▼' }}</span>
            <span v-if="!n.subtreeExpanded" class="text-[9px] opacity-70">{{ n.subtreeSize }}</span>
          </button>
          <!-- Same-person marker — click to pan to the OTHER position of this DB person -->
          <button
            v-if="n.samePerson"
            class="absolute -top-1.5 -right-1.5 z-10 h-4 min-w-[16px] px-1
                   rounded-full bg-indigo-500 text-white text-[9px] leading-4
                   font-medium shadow-sm flex items-center justify-center
                   hover:bg-indigo-600 cursor-default"
            title="同一人 — 點擊跳到他在族譜上的另一個位置"
            @click.stop="jumpToOther(n)"
          >♻</button>
        </div>
      </div>

      <!-- 耶穌聖家詮釋 — local toggle 緊鄰 約瑟 卡片右側（與 pan/zoom 同步）.
           Mark 6:3 has 4 traditional interpretations. early_consensus 在 Jerome
           ~393 之前等同 Epiphanian view（東方）. -->
      <div
        v-if="!props.rootId && josephScreenPos.visible"
        class="absolute z-40 bg-white/95 border border-gray-200 rounded-lg p-1 shadow-sm flex flex-col items-stretch gap-0.5 pointer-events-auto"
        :style="{ left: josephScreenPos.x + 'px', top: josephScreenPos.y + 'px' }"
      >
        <span class="text-[10px] text-gray-400 px-1.5 select-none leading-tight">耶穌聖家</span>
        <button
          v-for="t in brothersOptions"
          :key="t.value"
          class="text-[11px] px-2 py-1 rounded-md font-medium transition cursor-default text-left"
          :class="props.brothersView === t.value
            ? `bg-gray-100 ${t.activeColor}`
            : 'text-gray-500 hover:text-gray-700'"
          :title="t.tooltip"
          @click.stop="emit('update:brothersView', t.value)"
        >{{ t.label }}</button>
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
        <div class="flex items-center gap-1.5"><span class="w-3 h-0 border-t border-dashed border-red-600" />紅虛線：聖靈感孕婚姻（約瑟↔馬利亞）</div>
        <div class="flex items-center gap-1.5 pt-1 mt-1 border-t border-gray-100"><span class="inline-block w-3 h-3 border border-orange-300 bg-orange-50 rounded" />早期教會傳統（東西方共識）</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-purple-300 bg-purple-50 rounded" />天主教傳統</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-emerald-300 bg-emerald-50 rounded" />東方教會傳統</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-blue-300 bg-blue-50 rounded" />拉比傳統</div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">滾輪：上下/左右移動　·　Ctrl+滾輪：縮放　·　拖曳：平移　·　♻ 點擊跳同人</div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'BiblicalSpineTree' })

interface BreadcrumbItem { id: string; name: string }

type BrothersView = 'protestant' | 'early_consensus' | 'orthodox' | 'catholic'

const props = defineProps<{
  nodes: any[]
  edges: any[]
  rootId?: string                   // when set: recursive single-spine mode
  breadcrumb?: BreadcrumbItem[]     // navigation crumbs (recursive only)
  brothersView?: BrothersView       // 耶穌弟兄詮釋（馬可 6:3）
}>()
const emit = defineEmits<{
  selectPerson:        [id: string]
  closeRecursive:      []
  'update:brothersView': [v: BrothersView]
}>()

// 耶穌弟兄詮釋按鈕（局部 toggle）— 4 選項：
//   聖經（字面，5 弟兄為親生）
//   早期教會（Epiphanian view，~Jerome 之前主流，前妻說）→ API 等同 orthodox
//   東方（Epiphanian view 完整版）→ orthodox
//   天主教（Hieronymian view，~Jerome 393 AD 起，表親說）→ catholic
const brothersOptions: Array<{ value: BrothersView; label: string; activeColor: string; tooltip: string }> = [
  { value: 'protestant',      label: '聖經',     activeColor: 'text-gray-900',     tooltip: '聖經字面：5 弟兄為約瑟+馬利亞親生' },
  { value: 'early_consensus', label: '早期教會', activeColor: 'text-orange-700',   tooltip: '早期教會（Jerome 393 前）：前妻撒羅米所生' },
  { value: 'orthodox',        label: '東方',     activeColor: 'text-emerald-700',  tooltip: '東方教會（Epiphanian）：約瑟前妻撒羅米所生' },
  { value: 'catholic',        label: '天主教',   activeColor: 'text-purple-700',   tooltip: '天主教（Hieronymian）：馬利亞-革羅罷之子（表親）' },
]

// ── Layout constants ──────────────────────────────────────────────────
const NW          = 120  // person card width
const NH          = 52   // person card height
const CW          = 108  // clan card width
const CH          = 52
const MG          = 12   // wife stacking gap
const HG          = 20   // horizontal gap between cards (siblings)
const WIFE_HG     = 60   // horizontal gap for marriage lines (3× sibling gap so the line is visible)
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

const jesusId  = computed(() => resolveByName('耶穌（拿撒勒人）'))
const josephId = computed(() => resolveByName('約瑟（馬利亞之夫）'))
const maryId   = computed(() => resolveByName('馬利亞（耶穌之母）'))

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
// For descendants via marriage: if a person has no own children but does have
// a spouse, count the spouse's children as hers (e.g., 利百加 沒有 children 欄位，
// 但是 以撒 .children = 雅各、以掃 — 那 雅各、以掃 算 利百加 的後代). When a person
// has her own children (e.g., 利亞 with 7), use those directly (don't conflate
// with other-wife 雅各 kids).
function effectiveChildIds(id: string): string[] {
  const direct = childrenOf.value.get(id) ?? []
  if (direct.length > 0) return direct
  const result: string[] = []
  for (const spId of (spousesOf.value.get(id) ?? [])) {
    const spouseDirectKids = childrenOf.value.get(spId) ?? []
    const otherWives = (spousesOf.value.get(spId) ?? []).filter(w => w !== id)
    const otherWivesKids = new Set<string>()
    for (const ow of otherWives) {
      for (const c of childrenOf.value.get(ow) ?? []) otherWivesKids.add(c)
    }
    for (const c of spouseDirectKids) {
      if (otherWivesKids.has(c)) continue
      if (!result.includes(c)) result.push(c)
    }
  }
  return result
}

function subtreeIds(id: string, vis = new Set<string>()): string[] {
  if (vis.has(id)) return []
  vis.add(id)
  return [id, ...effectiveChildIds(id).flatMap(c => subtreeIds(c, vis))]
}

// ── Node interface ────────────────────────────────────────────────────
interface LNode {
  id: string                  // unique per render position (one DB person may have several LNodes)
  personId: string            // DB person id — same person across all their render positions
  rawName: string
  displayName: string
  genLabel: string
  generation: number
  gender: string
  x: number; y: number; w: number; h: number
  spineKind: 'A' | 'B' | 'S' | 'single' | null
  tradition?: 'biblical' | 'early_consensus' | 'catholic' | 'orthodox' | 'rabbinic'
  isClan: boolean             // legacy, retained for type compat; in new layout always false
  isExpansionNode?: boolean   // node belongs to an expanded subtree
  hasSubtree?: boolean        // true → render a ▼/▲ toggle on the card
  subtreeExpanded?: boolean
  subtreeSize?: number
  samePerson?: boolean        // true → this person also appears at another card; render ♻
  isExpansionRoot?: boolean   // true → this kid card's own ▼ is expanded; immune to occlusion
  hidden?: boolean
  disambig?: string           // disambiguator (parenthetical 內容), 顯示在名字下方 — 僅當
                              //   同 baseName 有多個 personId 同時被渲染時 set
}
interface VDrop { x: number; y1: number; y2: number; stroke?: string; dashed?: boolean; hidden?: boolean; isExpansionLine?: boolean }
interface HBar  { x1: number; x2: number; y: number; stroke?: string; dashed?: boolean; hidden?: boolean; isExpansionLine?: boolean }
interface MLine { id: string; x1: number; x2: number; y: number; hidden?: boolean; holy?: boolean }
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
  // Person-ids already placed on the chart as a row-level spouse (spine wife,
  // or one of a spine wife's same-gen extra spouses — Trinubium extension).
  // Used to suppress duplicate rendering of the same person as a kidWife at
  // a different row (e.g. 革羅罷-亞拿 sits with 亞拿 at gen 73 and must NOT
  // also appear as 馬利亞-革羅罷's husband at gen 74).
  const placedAsRowSpouse = new Set<string>()
  const crossSpineDrawn = new Set<string>()  // dedup cross-spine marriage lines
  const expansionBoxes: ExpansionBox[] = [] // for occlusion detection
  const expansionNodeIds = new Set<string>() // nodes inside expanded subtrees

  // ── Subtree layout (used by in-place expansion) ────────────────────
  // Uses the SAME main row pitch (RH) as the spine so a node at generation G
  // lands at exactly the same Y as a spine node at generation G. Each
  // recursive subtree is laid out left-to-right; the root sits centered above
  // the X-range of its children. Lines created here are flagged
  // `isExpansionLine: true` so the occlusion pass leaves them alone.
  function layoutSubtree(
    rootId: string,
    leftX: number,
    vis: Set<string>,
  ): { nodes: LNode[]; drops: VDrop[]; hbars: HBar[]; marriages: MLine[]; rootCX: number; maxX: number; maxY: number } {
    if (vis.has(rootId)) {
      return { nodes: [], drops: [], hbars: [], marriages: [], rootCX: leftX + NW / 2, maxX: leftX + NW, maxY: 0 }
    }
    vis.add(rootId)
    const p = pMap.get(rootId)
    if (!p) {
      return { nodes: [], drops: [], hbars: [], marriages: [], rootCX: leftX + NW / 2, maxX: leftX + NW, maxY: 0 }
    }
    const gen = p.data.generationNum || 1
    const myY = rowY(gen - 1)   // 1-based gen → 0-based row, same scale as main spine
    // Follow children via effectiveChildIds (includes via-spouse for women like
    // 利百加 / 拉班 daughters), BUT cut off at spine nodes — their descendants are
    // already drawn on the main spine, drawing them again would duplicate.
    // ALSO cut off at married-out daughters (in renderedAsSpouseOnSpine): the
    // daughter herself shows as a leaf in her father's tree, but her descendants
    // belong to husband's family tree and shouldn't be counted/drawn here.
    const isMarriedOut = renderedAsSpouseOnSpine.has(rootId)
    const kids = rowOf.has(rootId) || isMarriedOut
      ? []  // spine node or married-out daughter — render as leaf
      : effectiveChildIds(rootId).filter(c => !vis.has(c))

    // Wives to render alongside this subtree root (e.g., 以底特 next to 羅得 in
    // 哈蘭 expansion). Skip wives already drawn on the main chart (spine妻位).
    const wiveIds = (spousesOf.value.get(rootId) ?? []).filter(w =>
      !renderedAsSpouseOnSpine.has(w) && !vis.has(w) && pMap.has(w) && !rowOf.has(w)
    )
    for (const w of wiveIds) vis.add(w)
    const SLOT_K = NW + WIFE_HG
    const wivesReach = wiveIds.length * SLOT_K

    // Helper: place wives to the LEFT of root center, return their nodes + marriage lines
    function placeWives(rootCX: number): { nodes: LNode[]; marriages: MLine[] } {
      const ns: LNode[] = []
      const ms: MLine[] = []
      const marY = myY + NH / 2
      for (let wi = 0; wi < wiveIds.length; wi++) {
        const wid = wiveIds[wi]
        const wp = pMap.get(wid)!
        const wcx = rootCX - (wi + 1) * SLOT_K
        ns.push({
          id: `${wid}__exp_wife_of__${rootId}`,
          personId: wid,
          rawName:     wp.data.name,
          displayName: shortName(wp.data.name),
          genLabel:    getGenLabel(wp),
          generation:  wp.data.generationNum || 0,
          gender:      wp.data.gender,
          x: wcx - NW / 2, y: myY, w: NW, h: NH,
          spineKind:   null,
          tradition:   wp.data.tradition,
          isClan:      false,
          isExpansionNode: true,
        })
        const prevCx = wi === 0 ? rootCX : rootCX - wi * SLOT_K
        ms.push({ id: `expw_${rootId}_${wid}`, x1: wcx + NW / 2, x2: prevCx - NW / 2, y: marY })
      }
      return { nodes: ns, marriages: ms }
    }

    if (kids.length === 0) {
      // Leaf: root at leftX + wivesReach, wives to its left
      const rootX = leftX + wivesReach
      const rootCX = rootX + NW / 2
      const myNode: LNode = {
        id: `${rootId}__exp`,
        personId: rootId,
        rawName:     p.data.name,
        displayName: shortName(p.data.name),
        genLabel:    getGenLabel(p),
        generation:  gen,
        gender:      p.data.gender,
        x: rootX, y: myY, w: NW, h: NH,
        spineKind:   null,
        tradition:   p.data.tradition,
        isClan:      false,
        isExpansionNode: true,
      }
      const w = placeWives(rootCX)
      return {
        nodes: [myNode, ...w.nodes],
        drops: [], hbars: [], marriages: w.marriages,
        rootCX, maxX: rootX + NW, maxY: myY + NH,
      }
    }

    // Lay out children left-to-right, then center root above their span.
    // Shift kids start by wivesReach so wives can sit to root's left without
    // extending past leftX (preserves the subtree-x-contract).
    let cursorX = leftX + wivesReach
    const childResults: ReturnType<typeof layoutSubtree>[] = []
    let maxY = myY + NH
    for (const k of kids) {
      const r = layoutSubtree(k, cursorX, vis)
      childResults.push(r)
      cursorX = r.maxX + HG
      maxY = Math.max(maxY, r.maxY)
    }
    const childCXs = childResults.map(r => r.rootCX)
    const cmin = Math.min(...childCXs)
    const cmax = Math.max(...childCXs)
    const rootCX = (cmin + cmax) / 2
    const rootX  = rootCX - NW / 2
    const rightEdge = Math.max(rootX + NW, cursorX - HG)

    const myNode: LNode = {
      id: `${rootId}__exp`,
      personId: rootId,
      rawName:     p.data.name,
      displayName: shortName(p.data.name),
      genLabel:    getGenLabel(p),
      generation:  gen,
      gender:      p.data.gender,
      x: rootX, y: myY, w: NW, h: NH,
      spineKind:   null,
      tradition:   p.data.tradition,
      isClan:      false,
      isExpansionNode: true,
    }

    // Connector: root → barY → each child top
    const myDrops: VDrop[] = []
    const myHbars: HBar[]  = []
    const firstChildY = childResults[0].nodes[0]?.y ?? myY + NH + VG
    const barY = myY + NH + Math.round((firstChildY - myY - NH) * 0.5)
    myDrops.push({ x: rootCX, y1: myY + NH, y2: barY, isExpansionLine: true })
    if (childCXs.length === 1) {
      const cc = childCXs[0]
      if (Math.abs(rootCX - cc) < 1) {
        myDrops.push({ x: cc, y1: barY, y2: firstChildY, isExpansionLine: true })
      } else {
        myHbars.push({ x1: Math.min(rootCX, cc), x2: Math.max(rootCX, cc), y: barY, isExpansionLine: true })
        myDrops.push({ x: cc, y1: barY, y2: firstChildY, isExpansionLine: true })
      }
    } else {
      myHbars.push({ x1: cmin, x2: cmax, y: barY, isExpansionLine: true })
      for (const cc of childCXs) {
        myDrops.push({ x: cc, y1: barY, y2: firstChildY, isExpansionLine: true })
      }
    }

    const w = placeWives(rootCX)
    return {
      nodes: [myNode, ...w.nodes, ...childResults.flatMap(r => r.nodes)],
      drops: [...myDrops, ...childResults.flatMap(r => r.drops)],
      hbars: [...myHbars, ...childResults.flatMap(r => r.hbars)],
      marriages: [...w.marriages, ...childResults.flatMap(r => r.marriages)],
      rootCX,
      maxX: rightEdge,
      maxY,
    }
  }

  // Lay out the subtree(s) starting from `rootIds` (the children of the spine kid
  // being expanded), then SHIFT everything horizontally so the subtree's overall
  // center aligns with `centerX` (the spine kid's column position).
  function layoutExpansion(
    rootIds: string[],
    centerX: number,
  ): { nodes: LNode[]; drops: VDrop[]; hbars: HBar[]; marriages: MLine[]; bbox: ExpansionBox; rootCXs: number[]; firstY: number } {
    const vis = new Set<string>()
    let cursorX = 0
    const allNodes: LNode[] = []
    const allDrops: VDrop[] = []
    const allHbars: HBar[]  = []
    const allMarriages: MLine[] = []
    let maxY = 0
    const rootCXs: number[] = []
    let firstY = 0
    for (const rid of rootIds) {
      const r = layoutSubtree(rid, cursorX, vis)
      allNodes.push(...r.nodes)
      allDrops.push(...r.drops)
      allHbars.push(...r.hbars)
      allMarriages.push(...r.marriages)
      rootCXs.push(r.rootCX)
      cursorX = r.maxX + HG
      maxY = Math.max(maxY, r.maxY)
      if (firstY === 0 && r.nodes.length > 0) firstY = r.nodes[0].y
    }
    if (rootCXs.length === 0) {
      return { nodes: [], drops: [], hbars: [], marriages: [], bbox: { x1: 0, y1: 0, x2: 0, y2: 0 }, rootCXs, firstY }
    }
    const cmin = Math.min(...rootCXs)
    const cmax = Math.max(...rootCXs)
    const overallCenter = (cmin + cmax) / 2
    const shiftX = centerX - overallCenter
    for (const n of allNodes) n.x += shiftX
    for (const d of allDrops) d.x += shiftX
    for (const b of allHbars) { b.x1 += shiftX; b.x2 += shiftX }
    for (const m of allMarriages) { m.x1 += shiftX; m.x2 += shiftX }
    const shiftedRootCXs = rootCXs.map(c => c + shiftX)
    for (const n of allNodes) expansionNodeIds.add(n.id)
    const minX = Math.min(...allNodes.map(n => n.x)) - 8
    const maxX = Math.max(...allNodes.map(n => n.x + n.w)) + 8
    const minY = Math.min(...allNodes.map(n => n.y)) - 8
    return {
      nodes: allNodes, drops: allDrops, hbars: allHbars, marriages: allMarriages,
      bbox: { x1: minX, y1: minY, x2: maxX, y2: maxY + 8 },
      rootCXs: shiftedRootCXs,
      firstY,
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

  // ── Persons rendered as a SPOUSE on the main chart ─────────────────
  // 預先收集所有會被當成「配偶」畫在主圖上的 personId：
  //   1. spine person 的妻 (spine wife)
  //   2. spine wife 的「同代且不在 rowOf」其他配偶 (Trinubium 擴展)
  //   3. 非 spine 兒子（spine person 的旁支兒子）的妻 (kidWife)
  // 用途：layoutSubtree 在展開 ▼ 時，遇到已在配偶位渲染的女兒就跳過，
  // 避免「彼土利→利百加」與「以撒-利百加」同一人重覆畫；
  // 配偶卡的 ♻ 跳同人功能仍可從父親那邊找到她。
  const renderedAsSpouseOnSpine = new Set<string>()
  for (const sid of allSpineIds) {
    const sidGen = pMap.get(sid)?.data.generationNum
    for (const wid of sp.get(sid) ?? []) {
      renderedAsSpouseOnSpine.add(wid)
      const widGen = pMap.get(wid)?.data.generationNum
      for (const otherSp of sp.get(wid) ?? []) {
        if (otherSp === sid) continue
        const op = pMap.get(otherSp)
        if (!op) continue
        if (widGen != null && op.data.generationNum != null && op.data.generationNum !== widGen) continue
        renderedAsSpouseOnSpine.add(otherSp)
      }
    }
    for (const kidId of ch.get(sid) ?? []) {
      if (rowOf.has(kidId)) continue  // spine kid, skip
      for (const wid of sp.get(kidId) ?? []) {
        renderedAsSpouseOnSpine.add(wid)
      }
    }
    // also include spine person's own gen-mate spine spouse (cross-spine like Mary↔Joseph)
    if (sidGen != null) {
      for (const otherSp of sp.get(sid) ?? []) {
        renderedAsSpouseOnSpine.add(otherSp)
      }
    }
  }


  // Wife area width (per side, both spines may have wives outside).
  // Each wife claims one (NW + WIFE_HG) slot from the husband center.
  const wifeAreaW = maxWives > 0
    ? maxWives * (NW + WIFE_HG)
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
      personId: sid,
      rawName:     p.data.name,
      displayName: shortName(p.data.name),
      genLabel:    getGenLabel(p),
      generation:  p.data.generationNum || 0,
      gender:      p.data.gender,
      x: cx - NW / 2, y: rowY(row), w: NW, h: NH,
      spineKind:   membership.get(sid) ?? null,
      tradition:   p.data.tradition,
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

    // Placement rule (per user spec):
    //   夫右妻左         — husband on right, wife on left (universal)
    //   兄姊右弟妹左     — older siblings right of younger (handled in rightGroup/leftGroup split)
    //   大老婆右 小老婆左 — primary wife closest to husband (wifeIds[0] = primary, placed at wi=0 = closest)
    //   前妻前夫右 繼妻繼夫左 — first marriage closest to husband (same as above: wifeIds order)
    // So wifeSide is ALWAYS 'left' regardless of spine kind. Override only when the
    // husband has a cross-spine partner (then additional wives align with partner side).
    let wifeSide: 'left' | 'right' = 'left'
    let clanSide: 'left' | 'right' = 'right'  // (legacy, unused — kept for type compat)
    if (isDualMode.value) {
      if (k === 'A') clanSide = 'left'
      else if (k === 'B') clanSide = 'right'
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
    const wifeIdsBase     = allWifeIds.filter(wid => !rowOf.has(wid))

    // Trinubium-style extension: a spine wife may have her OWN other spouses
    // at the same generation (e.g. Catholic mode: 亞拿 → 約亞敬 + 革羅罷 + 撒羅馬).
    // Append them to the marriage row so they sit adjacent to the wife.
    // (Visually appears as one stack — the line between extras implies adjacency,
    // a UI compromise that's clearer than missing cards.)
    const sidGen = pMap.get(sid)?.data.generationNum
    const inMarriageRow = new Set<string>([sid, ...wifeIdsBase])
    const extraSpouses: string[] = []
    for (const wid of wifeIdsBase) {
      for (const otherSpId of sp.get(wid) ?? []) {
        if (inMarriageRow.has(otherSpId) || rowOf.has(otherSpId)) continue
        const op = pMap.get(otherSpId)
        if (!op) continue
        if (sidGen != null && op.data.generationNum != null && op.data.generationNum !== sidGen) continue
        inMarriageRow.add(otherSpId)
        extraSpouses.push(otherSpId)
        placedAsRowSpouse.add(otherSpId)
      }
    }
    const wifeIds = [...wifeIdsBase, ...extraSpouses]
    const wifeLX          = new Map<string, number>()
    const marLineY        = rowY(row) + NH / 2

    // If there's a cross-spine spouse, put non-cross-spine wives on the SAME side as
    // the cross-spine partner so the whole marriage stack lines up in one row.
    // Orthodox 約瑟 (spine A) + 馬利亞 (cross-spine on B/left) + 撒羅米 (regular):
    // 撒羅米 should sit BETWEEN 馬利亞 and 約瑟 (= 馬利亞 右邊, 約瑟 左邊).
    if (crossSpineWives.length > 0) {
      const csk = membership.get(crossSpineWives[0])
      if (csk === 'A')      wifeSide = 'right'
      else if (csk === 'B') wifeSide = 'left'
    }

    // Cross-spine marriages: draw once per pair (dedupe via sorted key).
    // Joseph↔Mary marked `holy` so the template can render it specially
    // (dashed red) — per Matt 1:18-25, Joseph took Mary as wife but Jesus'
    // conception was already by the Holy Spirit; not a typical union.
    for (const cwid of crossSpineWives) {
      const pairKey = [sid, cwid].sort().join('|')
      if (crossSpineDrawn.has(pairKey)) continue
      crossSpineDrawn.add(pairKey)
      const partner = nodes.find(n => n.id === cwid)
      if (!partner) continue
      const isHoly = josephId.value && maryId.value &&
        ((sid === josephId.value && cwid === maryId.value) ||
         (sid === maryId.value   && cwid === josephId.value))
      const hL = cx - NW / 2, hR = cx + NW / 2
      const pL = partner.x,   pR = partner.x + partner.w
      if (pR < hL)       marriages.push({ id: `mscross_${pairKey}`, x1: pR, x2: hL, y: marLineY, holy: !!isHoly })
      else if (pL > hR)  marriages.push({ id: `mscross_${pairKey}`, x1: hR, x2: pL, y: marLineY, holy: !!isHoly })
    }

    // Spine wife placement: card-to-card gap = WIFE_HG (wider than sibling HG so the
    // red marriage line is clearly visible — user spec: 「配偶線要 3 倍長」).
    const SLOT = NW + WIFE_HG  // 180px per slot when WIFE_HG=60
    for (let wi = 0; wi < wifeIds.length; wi++) {
      const wid = wifeIds[wi]
      let wx: number
      if (wifeSide === 'left') {
        wx = cx - (wi + 1) * SLOT - NW / 2  // wi=0 (closest wife) center at cx - SLOT
      } else {
        wx = cx + (wi + 1) * SLOT - NW / 2
      }
      wifeLX.set(wid, wx)

      // Always render the wife at this position (even if the same DB person appears
      // elsewhere — they're the SAME person, but the chart shows multiple roles).
      // Unique LNode.id keys this render; personId points back to the DB entry.
      const wp = pMap.get(wid)
      if (wp) nodes.push({
        id: `${wid}__wife_of__${sid}`,
        personId: wid,
        rawName:     wp.data.name,
        displayName: shortName(wp.data.name),
        genLabel:    getGenLabel(wp),
        generation:  wp.data.generationNum || 0,
        gender:      wp.data.gender,
        x: wx, y: rowY(row), w: NW, h: NH,
        spineKind:   null,
        tradition:   wp.data.tradition,
        isClan:      false,
      })

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

    // Marriage midpoint X — true midpoint between husband center and primary wife center
    // (which equals the midpoint of the HG-wide marriage line between them). With multi-
    // wife stacks, drop from the primary marriage so kids look like they come from the
    // canonical couple. Cross-spine spouses skip this — they're handled below.
    let midX = cx
    if (wifeIds.length > 0) {
      const wife0cx = wifeLX.get(wifeIds[0])! + NW / 2
      midX = (cx + wife0cx) / 2
    } else if (crossSpineWives.length > 0) {
      // Cross-spine marriage (Joseph↔Mary): drop from midpoint between the two spine cols
      const partner = nodes.find(n => n.id === crossSpineWives[0])
      if (partner) midX = (cx + partner.x + partner.w / 2) / 2
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

    // Order RTL: first wife's kids first (rightmost), within wife by sort_order ASC
    // (lower sort_order = older = rightmost per 兄右弟左). Fall back to canonical
    // appearance order when sort_order ties. sort_order overrides DB string order
    // for cases where biblical listing isn't birth order (e.g., 他拉 lists 亞伯蘭
    // first by importance, but he's actually the youngest).
    const origIdx = new Map<string, number>()
    allKidsRaw.forEach((k, i) => origIdx.set(k, i))
    function kidSortKey(kidId: string): [number, number] {
      const p = pMap.get(kidId)
      const so = (p?.data?.sortOrder !== undefined && p.data.sortOrder !== null && p.data.sortOrder !== 9999)
        ? p.data.sortOrder : 9999
      return [so, origIdx.get(kidId) ?? 0]
    }
    function sortKidsBirthOrder(group: string[]): string[] {
      return [...group].sort((a, b) => {
        const ka = kidSortKey(a), kb = kidSortKey(b)
        return ka[0] - kb[0] || ka[1] - kb[1]
      })
    }
    const orderedRTL: string[] = []
    const hasLinkage = Array.from(kidMom.values()).some(v => v !== null)
    if (hasLinkage) {
      for (const wid of allWifeIds) {
        const group = allKidsRaw.filter(k => kidMom.get(k) === wid)
        orderedRTL.push(...sortKidsBirthOrder(group))
      }
      const unattr = allKidsRaw.filter(k => kidMom.get(k) === null)
      orderedRTL.push(...sortKidsBirthOrder(unattr))
    } else {
      orderedRTL.push(...sortKidsBirthOrder(allKidsRaw))
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

      // Push-past: if the spine kid has WIVES on the same side that we're placing
      // siblings, the FIRST sibling on that side has to clear the entire wife
      // stack (otherwise sibling cards overlap wife cards on the same Y row,
      // because the spine kid's wives sit at the SAME row as its siblings —
      // both rendered at gen(spineKid) = gen(siblings)).
      function wifeReachOnSide(spineKidId: string, side: 'left' | 'right'): number {
        const spouses = (sp.get(spineKidId) ?? []).filter(w => !rowOf.has(w))
        if (spouses.length === 0) return 0
        let kidWifeSide: 'left' | 'right' = 'left'
        if (isDualMode.value) {
          const sk = membership.get(spineKidId)
          if (sk === 'A') kidWifeSide = 'right'
          else if (sk === 'B') kidWifeSide = 'left'
        }
        if (kidWifeSide !== side) return 0
        // Each spine kid's wife claims one (NW + WIFE_HG) marriage slot.
        return spouses.length * (NW + WIFE_HG)
      }

      // rightGroup: 兄姊右 — older brothers to the right of spine kid (younger).
      // Each right-sibling has wives on HIS left (夫右妻左). So the sibling card
      // sits to the RIGHT of his own wife stack. Walk from CLOSEST-to-spine outward:
      // rightCursor advances rightward through each sibling block (wives then sibling).
      const rightWifeReach = wifeReachOnSide(spineByX[0], 'right')
      const firstRightX = rightmostSpX + rightWifeReach + (NW + HG)
      let rightCursor = firstRightX
      for (let i = 0; i < rightGroup.length; i++) {
        const kid = rightGroup[rightGroup.length - 1 - i]  // closest-to-spine first
        const myWifeIds = (sp.get(kid) ?? []).filter(w => !rowOf.has(w))
        const wivesReach = myWifeIds.length * (NW + WIFE_HG)
        // Sibling card center = rightCursor + wivesReach (sibling sits RIGHT of his wives)
        kidX.set(kid, rightCursor + wivesReach)
        rightCursor += wivesReach + (NW + HG)
      }
      // leftGroup: leftmost-natural last; first kid in leftGroup is closest-to-spine
      const leftWifeReach = wifeReachOnSide(spineByX[spineByX.length - 1], 'left')
      const firstLeftX = leftmostSpX - leftWifeReach - (NW + HG)
      let leftCursor = firstLeftX
      for (let i = 0; i < leftGroup.length; i++) {
        const kid = leftGroup[i]
        kidX.set(kid, leftCursor)
        const myWifeIds = (sp.get(kid) ?? []).filter(w => !rowOf.has(w))
        leftCursor -= myWifeIds.length * (NW + WIFE_HG) + (NW + HG)
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

      // Does this kid have its own descendants (2nd-gen onwards)?
      // Rules from user:
      //  • Only MALES get a ▼ toggle (females collapse into a male's expansion)
      //  • If the kid is a spouse of a SPINE person, their descendants are
      //    already visible via the spine — hide ▼ to avoid duplicate trees
      //    (e.g., 撒拉 as 他拉's daughter would otherwise dupe 299 of 以撒's line)
      const kidSpouseIds = sp.get(kid) ?? []
      const hasSpineSpouse = kidSpouseIds.some(spId => rowOf.has(spId))
      const isFemale = kp.data.gender === 'female'
      // Cap subtree at married-out daughters — her descendants are husband's
      // tree, not this clan's. Otherwise 拿鶴 ▼ would include 利百加→Jacob→Jesus.
      const subtreeCapped = (id: string, vis = new Set<string>()): string[] => {
        if (vis.has(id)) return []
        vis.add(id)
        if (renderedAsSpouseOnSpine.has(id) && id !== kid) return [id]
        return [id, ...effectiveChildIds(id).flatMap(c => subtreeCapped(c, vis))]
      }
      const subtree = subtreeCapped(kid).filter(id => id !== kid)
      const hasSub  = subtree.length > 0 && !hasSpineSpouse && !isFemale
      // 小 clan (≤5 人) 預設展開 — 例如 斯多蘭→{亞拿,蘇比,以利沙白,施洗約翰} 不應藏在 ▼4 底下
      // 大 clan (如 拿鶴 ~300 人) 仍需手動點 ▼ 展開
      const expanded = expandedClans.value.has(kid) || (hasSub && subtree.length <= 5)

      nodes.push({
        id: kid,
        personId: kid,
        rawName:     kp.data.name,
        displayName: shortName(kp.data.name),
        genLabel:    getGenLabel(kp),
        generation:  kp.data.generationNum || 0,
        gender:      kp.data.gender,
        x: kxVal - NW / 2, y: childY, w: NW, h: NH,
        spineKind:   null,
        tradition:   kp.data.tradition,
        isClan:      false,
        hasSubtree:  hasSub,
        subtreeExpanded: expanded,
        subtreeSize: hasSub ? subtree.length : undefined,
        isExpansionRoot: expanded,  // never occlude the card whose own ▼ is expanded
      })

      // Non-spine kid's wives — placed OUTSIDE (away from spine) using the marriage
      // SLOT (NW + WIFE_HG = 180px). Wider than sibling gap (HG=20) so the red
      // marriage line is clearly visible — per user spec「配偶線要 3 倍長」.
      // Skip wives already drawn at a higher row as a row-level spouse (Trinubium).
      const kidWifeIds = (sp.get(kid) ?? []).filter(w => !rowOf.has(w) && !placedAsRowSpouse.has(w))
      if (kidWifeIds.length > 0) {
        // 夫右妻左: wives always on the kid's LEFT, regardless of which side of spine
        // the kid sits on. wi=0 (primary/大老婆/前妻) closest to kid.
        const marY = childY + NH / 2
        const SLOT_K = NW + WIFE_HG  // marriage gap (vs sibling NW+HG)
        for (let wi = 0; wi < kidWifeIds.length; wi++) {
          const wid = kidWifeIds[wi]
          const wp = pMap.get(wid); if (!wp) continue
          const wcx = kxVal - (wi + 1) * SLOT_K
          nodes.push({
            id: `${wid}__wife_of__${kid}`,
            personId: wid,
            rawName:     wp.data.name,
            displayName: shortName(wp.data.name),
            genLabel:    getGenLabel(wp),
            generation:  wp.data.generationNum || 0,
            gender:      wp.data.gender,
            x: wcx - NW / 2, y: childY, w: NW, h: NH,
            spineKind:   null,
            tradition:   wp.data.tradition,
            isClan:      false,
          })
          // Marriage line — segment between this wife's right edge and the previous
          // card's left edge (kid for wi=0, prev wife for wi>0).
          const prevCx = wi === 0 ? kxVal : kxVal - wi * SLOT_K
          marriages.push({ id: `nsm_${kid}_${wid}`, x1: wcx + NW / 2, x2: prevCx - NW / 2, y: marY })
        }
      }

      // When expanded: render the full subtree directly below, aligned to main row pitch
      if (hasSub && expanded) {
        // 跳過已在 spine 上以妻位渲染的 children（如 斯多蘭.children=[亞拿, 蘇比]，
        // 亞拿 已是 約亞敬 的 spine 妻 → 不要在 expansion 再畫一次）
        const kidChildren = (ch.get(kid) ?? []).filter(c => !rowOf.has(c) && !renderedAsSpouseOnSpine.has(c))
        if (kidChildren.length > 0) {
          const exp = layoutExpansion(kidChildren, kxVal)
          nodes.push(...exp.nodes)
          drops.push(...exp.drops)
          hbars.push(...exp.hbars)
          marriages.push(...exp.marriages)

          // Connect kid (parent) down to the subtree's root row
          const kidBottom = childY + NH
          const firstChildY = exp.firstY
          if (firstChildY > kidBottom) {
            const linkBarY = kidBottom + Math.round((firstChildY - kidBottom) * 0.5)
            drops.push({ x: kxVal, y1: kidBottom, y2: linkBarY, isExpansionLine: true })
            if (exp.rootCXs.length === 1) {
              const cc = exp.rootCXs[0]
              if (Math.abs(kxVal - cc) < 1) {
                drops.push({ x: cc, y1: linkBarY, y2: firstChildY, isExpansionLine: true })
              } else {
                hbars.push({ x1: Math.min(kxVal, cc), x2: Math.max(kxVal, cc), y: linkBarY, isExpansionLine: true })
                drops.push({ x: cc, y1: linkBarY, y2: firstChildY, isExpansionLine: true })
              }
            } else {
              const rmin = Math.min(...exp.rootCXs)
              const rmax = Math.max(...exp.rootCXs)
              hbars.push({ x1: Math.min(kxVal, rmin), x2: Math.max(kxVal, rmax), y: linkBarY, isExpansionLine: true })
              for (const cc of exp.rootCXs) {
                drops.push({ x: cc, y1: linkBarY, y2: firstChildY, isExpansionLine: true })
              }
            }
          }
          // Bbox covers the subtree but NOT the parent row, so the spine T-bar above stays visible.
          // Auto-expanded (subtree ≤5) clans do NOT occlude — small clans like 斯多蘭→{蘇比,
          // 以利沙白, 施洗約翰} should coexist with neighbouring spine kids (e.g. 約瑟+馬利亞
          // 的 5 子 西門/猶大 卡片中心位於 expansion bbox 內，但不該被隱藏)。
          if (expandedClans.value.has(kid)) expansionBoxes.push(exp.bbox)
        }
      }
    }

    // PER-MOTHER T-bar with STAGGERED barY: each wife gets her own T-bar at a
    // distinct Y so the bars don't visually merge even when their X ranges overlap.
    //   • Drop start = midpoint of the marriage SEGMENT between this wife and the
    //     preceding card (husband for primary, previous wife for later wives).
    //   • barY: closest-to-husband wife → bar near childY; furthest → bar near
    //     marLineY. So 利亞 的橫桿在底部，悉帕 在頂部，互不重疊。
    if (orderedRTL.length > 0) {
      const parentKind = membership.get(sid)

      function mommidX(momId: string | null): number {
        if (momId !== null) {
          const wi = wifeIds.indexOf(momId)
          if (wi >= 0) {
            // 每位妻子的子女 drop 從「她與相鄰卡片（往丈夫方向）的中間點」掉下：
            //   wi=0 (主妻) → 與丈夫之間的中點（真婚姻線）
            //   wi>0       → 與前一位妻子之間的中點（同列共妻 stack 視覺一致）
            // 所有 drop 都坐落在 marLineY 那條紅色婚姻線上，視覺接續清楚。
            const momCX  = wifeLX.get(momId)! + NW / 2
            const prevCX = wi === 0 ? cx : (wifeLX.get(wifeIds[wi - 1])! + NW / 2)
            return (momCX + prevCX) / 2
          }
          if (crossSpineWives.includes(momId)) {
            const partner = nodes.find(n => n.id === momId)
            if (partner) return (cx + partner.x + partner.w / 2) / 2
          }
        }
        // null mom (no recorded mother): drop OUTSIDE the wife stack — past the
        // smallest wife (last in wifeIds). 大衛 耶路撒冷生的 11 子聖經沒記載
        // 母親 — 應從 以格拉（最小妾）外側延伸出去，不從 拔示巴 婚姻線分支。
        if (wifeIds.length > 0) {
          const lastWifeCx = wifeLX.get(wifeIds[wifeIds.length - 1])! + NW / 2
          return wifeSide === 'left'
            ? lastWifeCx - (NW + WIFE_HG)
            : lastWifeCx + (NW + WIFE_HG)
        }
        return midX
      }

      // Group kids by mother
      const groupedByMom = new Map<string | null, string[]>()
      for (const kid of orderedRTL) {
        const mom = kidMom.get(kid) ?? null
        if (!groupedByMom.has(mom)) groupedByMom.set(mom, [])
        groupedByMom.get(mom)!.push(kid)
      }

      // Mother order: wives in DB order (大老婆→小老婆), then cross-spine, then null.
      const motherOrder: Array<string | null> = []
      for (const wid of wifeIds)        if (groupedByMom.has(wid))  motherOrder.push(wid)
      for (const cwid of crossSpineWives) if (groupedByMom.has(cwid)) motherOrder.push(cwid)
      if (groupedByMom.has(null))         motherOrder.push(null)

      // Pre-compute each mother's bar X range so we can detect overlap.
      // Bar spans from min(drop, kidXs) to max(drop, kidXs) at her barY.
      const motherSpans = new Map<string | null, { minX: number; maxX: number }>()
      for (const mom of motherOrder) {
        const groupKids = groupedByMom.get(mom)!
        const midX_m = mommidX(mom)
        const kidXs = groupKids.map(k => kidX.get(k)!).filter(v => v !== undefined)
        if (kidXs.length === 0) continue
        motherSpans.set(mom, { minX: Math.min(midX_m, ...kidXs), maxX: Math.max(midX_m, ...kidXs) })
      }

      // If no mother-pair's bar X range overlaps, all bars sit at the SAME midY
      // (cleaner visual — 亞伯拉罕的 3 妻 各有獨立 X 範圍時，子女線 一樣高 即可).
      // If any pair overlaps, stagger Ys so they don't visually merge.
      const spanList = motherOrder.filter(m => motherSpans.has(m))
      let hasOverlap = false
      for (let i = 0; i < spanList.length && !hasOverlap; i++) {
        const a = motherSpans.get(spanList[i])!
        for (let j = i + 1; j < spanList.length; j++) {
          const b = motherSpans.get(spanList[j])!
          if (!(a.maxX < b.minX || b.maxX < a.minX)) { hasOverlap = true; break }
        }
      }

      const N = motherOrder.length
      const verticalRange = childY - marLineY
      const motherBarY = new Map<string | null, number>()
      if (hasOverlap) {
        // Stagger: primary (closest-to-husband) at LOWEST bar; secondary higher
        for (let i = 0; i < N; i++) {
          const fraction = (N - i) / (N + 1)
          motherBarY.set(motherOrder[i], marLineY + Math.round(verticalRange * fraction))
        }
      } else {
        // All non-overlapping → single shared barY in the middle
        const sharedBarY = marLineY + Math.round(verticalRange * 0.5)
        for (const m of motherOrder) motherBarY.set(m, sharedBarY)
      }
      // 沒記載母親的兒子們（mom = null）— bar 直接坐落在 marLineY 上，
      // 視為婚姻線延伸（從最末妻外側延伸出去）；drop 從 barY 直接到 kid，
      // 不再有 marLineY→barY 的中間段。
      // 例：大衛在耶路撒冷生的 11 個沒記載母親的兒子，T-bar 跟 大衛↔妻 婚姻
      // 紅線同 Y，從 哈及 外側延伸出去，灰色 T-bar + 灰色 drop 往下到每個兒子。
      if (motherBarY.has(null)) motherBarY.set(null, marLineY)

      for (const mom of motherOrder) {
        const groupKids  = groupedByMom.get(mom)!
        const groupMidX  = mommidX(mom)
        const groupKidXs = groupKids.map(k => kidX.get(k)!).filter(v => v !== undefined)
        if (groupKidXs.length === 0) continue
        const barY = motherBarY.get(mom)!
        const minBarX = Math.min(groupMidX, ...groupKidXs)
        const maxBarX = Math.max(groupMidX, ...groupKidXs)
        // 婚姻線顏色：只有橫向婚姻線（夫妻之間）是紅色，其他全灰。
        // 例：亞當-夏娃 紅色婚姻線；marLineY→barY drop = 灰、T-bar = 灰、kid drop = 灰。
        if (barY !== marLineY) {
          drops.push({ x: groupMidX, y1: marLineY, y2: barY })
        }
        // null-mom 的 T-bar 跟 marLineY 同 Y → 視為婚姻線延伸，用紅色（與 marriages 同色）
        const hbarStroke = (mom === null && barY === marLineY) ? '#dc2626' : undefined
        hbars.push({ x1: minBarX, x2: maxBarX, y: barY, stroke: hbarStroke })
        for (const kid of groupKids) {
          const kxVal     = kidX.get(kid)!
          const isSpKid   = rowOf.has(kid)
          const childKind = membership.get(kid)
          const isLegal   = rk.get(`${sid}|${kid}`) === 'legal'
          const continuingKind = parentKind === 'S' ? (childKind ?? 'S') : parentKind
          const lineStroke = isLegal
            ? '#9ca3af'
            : !isSpKid                          ? '#9ca3af'  // 非主幹子女：一律灰色
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
  // ── Occlusion: PER-NODE / PER-LINE (not the big bbox) ──────────────
  // An expansion card / line claims its own footprint + a 0.5rem (8px) margin.
  // A non-expansion card or line is hidden ONLY if it actually overlaps that
  // claim. So 該隱's slim middle column at rows 3-6 won't hide spine cards at
  // those rows; only at the wide bottom row (where 拉麥's 4 children fan out)
  // will spine cards at the SAME row that get covered actually disappear.
  const OCCL_PAD = 8  // 0.5rem
  if (expansionBoxes.length > 0) {
    const exShapes: ExpansionBox[] = []
    for (const n of nodes) {
      if (!n.isExpansionNode) continue
      exShapes.push({
        x1: n.x - OCCL_PAD, y1: n.y - OCCL_PAD,
        x2: n.x + n.w + OCCL_PAD, y2: n.y + n.h + OCCL_PAD,
      })
    }
    for (const d of drops) {
      if (!d.isExpansionLine) continue
      exShapes.push({
        x1: d.x - OCCL_PAD, y1: Math.min(d.y1, d.y2) - OCCL_PAD,
        x2: d.x + OCCL_PAD, y2: Math.max(d.y1, d.y2) + OCCL_PAD,
      })
    }
    for (const b of hbars) {
      if (!b.isExpansionLine) continue
      exShapes.push({
        x1: Math.min(b.x1, b.x2) - OCCL_PAD, y1: b.y - OCCL_PAD,
        x2: Math.max(b.x1, b.x2) + OCCL_PAD, y2: b.y + OCCL_PAD,
      })
    }

    for (const n of nodes) {
      if (n.isExpansionNode) continue
      if (n.isExpansionRoot) continue  // the kid card whose own ▼ is open
      const nBox: ExpansionBox = { x1: n.x, y1: n.y, x2: n.x + n.w, y2: n.y + n.h }
      if (exShapes.some(s => boxOverlap(nBox, s))) n.hidden = true
    }
    for (const d of drops) {
      if (d.isExpansionLine) continue
      if (exShapes.some(s => lineIntersectsBox(d.x, d.y1, d.x, d.y2, s))) d.hidden = true
    }
    for (const b of hbars) {
      if (b.isExpansionLine) continue
      if (exShapes.some(s => lineIntersectsBox(b.x1, b.y, b.x2, b.y, s))) b.hidden = true
    }
    for (const m of marriages) {
      if (exShapes.some(s => lineIntersectsBox(m.x1, m.y, m.x2, m.y, s))) m.hidden = true
    }
    for (const g of trunkGuides) {
      if (exShapes.some(s => lineIntersectsBox(g.x, g.y1, g.x, g.y2, s))) g.hidden = true
    }

    // ── Stronger pass: hide ANY card/line inside an expansion bbox that isn't
    // part of that expansion's own subtree. User spec: 展開 ▼ 時，bbox 範圍裡的
    // 其他主幹和非主幹卡（如雅各的非主幹兒子 利未/西緬/呂便 夾在以掃 expansion 中）
    // 都要隱形，否則視覺上很亂。同步遮蔽 drops/hbars/trunkGuides，否則卡片消失
    // 但連線殘留會留下「幽靈線條」。
    // Spared: isExpansionNode (this expansion's own subtree) + isExpansionRoot
    // (the card whose ▼ was clicked) + lines flagged isExpansionLine.
    const lineInAnyBbox = (x1: number, y1: number, x2: number, y2: number): boolean => {
      const minX = Math.min(x1, x2), maxX = Math.max(x1, x2)
      const minY = Math.min(y1, y2), maxY = Math.max(y1, y2)
      return expansionBoxes.some(b => !(maxX < b.x1 || minX > b.x2 || maxY < b.y1 || minY > b.y2))
    }
    for (const n of nodes) {
      if (n.hidden) continue
      if (n.isExpansionNode || n.isExpansionRoot) continue
      const cx = n.x + n.w / 2, cy = n.y + n.h / 2
      if (expansionBoxes.some(b => cx >= b.x1 && cx <= b.x2 && cy >= b.y1 && cy <= b.y2)) {
        n.hidden = true
      }
    }
    for (const d of drops) {
      if (d.hidden || d.isExpansionLine) continue
      if (lineInAnyBbox(d.x, d.y1, d.x, d.y2)) d.hidden = true
    }
    for (const b of hbars) {
      if (b.hidden || b.isExpansionLine) continue
      if (lineInAnyBbox(b.x1, b.y, b.x2, b.y)) b.hidden = true
    }
    for (const m of marriages) {
      if (m.hidden) continue
      if (lineInAnyBbox(m.x1, m.y, m.x2, m.y)) m.hidden = true
    }
    for (const g of trunkGuides) {
      if (g.hidden) continue
      if (lineInAnyBbox(g.x, g.y1, g.x, g.y2)) g.hidden = true
    }
  }

  // ── Detect duplicate persons (same DB id rendered at multiple positions) ──
  const byPid = new Map<string, LNode[]>()
  for (const n of nodes) {
    if (n.hidden) continue
    const arr = byPid.get(n.personId) ?? []
    arr.push(n)
    byPid.set(n.personId, arr)
  }
  for (const list of byPid.values()) {
    if (list.length > 1) for (const n of list) n.samePerson = true
  }

  // Also mark ♻ on WIFE cards (people drawn only as a spouse, not as a parent's
  // child) when any ancestor in their DB chain is rendered. Click ♻ on these
  // walks up parent chain, expands the nearest rendered ancestor's ▼ clan and
  // pans to where the wife appears as her father's daughter.
  // E.g., 利亞 drawn as 雅各's wife → ancestor chain 拉班 ← 彼土利 ← 拿鶴.
  // 拿鶴 is rendered (亞伯拉罕's brother). Click expands 拿鶴 → 利亞 appears
  // as his great-granddaughter, ♻ resolves to that position.
  const pids = new Set<string>()
  for (const n of nodes) if (!n.hidden) pids.add(n.personId)
  for (const n of nodes) {
    if (n.hidden || n.samePerson || n.isExpansionNode) continue
    if (!n.id.includes('__wife_of__')) continue  // only wife/spouse cards get ancestry-aware ♻
    let cur: string | undefined = n.personId
    const seen = new Set<string>([n.personId])
    while (cur) {
      const parents = parentsOf.value.get(cur) ?? []
      if (parents.length === 0) break
      const par = parents[0]
      if (seen.has(par)) break
      seen.add(par)
      if (pids.has(par)) { n.samePerson = true; break }
      cur = par
    }
  }

  // ── Collision avoidance: 同 Y row 卡片不可重疊 ────────────────────────
  // 不同 clan 的 expansion 各自獨立排版，X 軸落點可能撞到（例如 謝拉's expansion
  // 在 J25 row 放 約巴/撒底，跟 法勒斯's expansion 的 哈母勒/希斯崙 撞在一起 70px
  // step → 50px 重疊）。post-pass：每個 Y row 內按 X 排序，左→右掃，重疊的右
  // 卡片往右推 (overlap + MIN_GAP)，連帶把連到 card 中心的 drops/hbars 端點一起
  // 移動，保留線條完整。
  {
    const MIN_GAP = 16
    function shiftCardAndLines(n: LNode, dx: number) {
      const oldCx = n.x + n.w / 2
      n.x += dx
      const newCx = n.x + n.w / 2
      for (const d of drops) {
        if (Math.abs(d.x - oldCx) < 0.5) d.x = newCx
      }
      for (const b of hbars) {
        if (Math.abs(b.x1 - oldCx) < 0.5) b.x1 = newCx
        if (Math.abs(b.x2 - oldCx) < 0.5) b.x2 = newCx
      }
    }
    const yBuckets = new Map<number, LNode[]>()
    for (const n of nodes) {
      if (n.hidden) continue
      const k = Math.round(n.y)
      if (!yBuckets.has(k)) yBuckets.set(k, [])
      yBuckets.get(k)!.push(n)
    }
    // spine 卡片位置由 spine column 鎖定，不可被 collision 推開 — 否則 amber/rose
    // 主幹 guide line 跟卡片就分離了。
    const isAnchored = (n: LNode) => rowOf.has(n.personId)
    for (const ns of yBuckets.values()) {
      // 多輪掃，最多 ns.length 次（cascading 收斂上限）
      for (let pass = 0; pass < ns.length + 2; pass++) {
        ns.sort((a, b) => a.x - b.x)
        let anyShift = false
        for (let i = 1; i < ns.length; i++) {
          const left = ns[i - 1]
          const right = ns[i]
          const overlap = (left.x + left.w + MIN_GAP) - right.x
          if (overlap <= 0) continue
          if (!isAnchored(right)) {
            shiftCardAndLines(right, overlap)
            anyShift = true
          } else if (!isAnchored(left)) {
            shiftCardAndLines(left, -overlap)
            anyShift = true
          }
          // 兩邊都是 spine（罕見）→ 接受重疊
        }
        if (!anyShift) break
      }
    }
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

  // Disambig pass: when 同 baseName 有多個不同 personId 被渲染（例如 馬利亞-耶穌之母
  // 與 馬利亞-革羅罷 同框），把 rawName 括號內容掛到 disambig 上，讓 card template 多
  // 顯示一行小字標明哪位「馬利亞」。
  const baseNamePersons = new Map<string, Set<string>>()
  for (const n of nodes) {
    if (n.hidden) continue
    const bn = baseName(n.rawName)
    if (!baseNamePersons.has(bn)) baseNamePersons.set(bn, new Set())
    baseNamePersons.get(bn)!.add(n.personId)
  }
  for (const n of nodes) {
    if ((baseNamePersons.get(baseName(n.rawName))?.size ?? 0) < 2) continue
    const m = n.rawName.match(/（(.+?)）/)
    if (m) n.disambig = m[1]
  }

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
// Card body opens the edit modal (using DB personId — same person across roles).
// The ▼/▲ toggle (separate button) handles subtree expansion via its own @click.stop.
function onCardClick(n: LNode) {
  emit('selectPerson', n.personId)
}

// ♻ marker click — center the viewport on this person's OTHER card position.
// If no rendered peer exists yet (because parent's ▼ clan is collapsed), expand
// the parent's clan first; after re-render, pan to the new peer.
function panToCard(target: LNode) {
  const vp = viewportRef.value
  if (!vp) return
  const rect = vp.getBoundingClientRect()
  const targetCX = target.x + target.w / 2
  const targetCY = target.y + target.h / 2
  panX.value = rect.width / 2 - targetCX * zoom.value
  panY.value = rect.height / 2 - targetCY * zoom.value
}

function jumpToOther(current: LNode) {
  if (!cv.value) return
  const peers = cv.value.nodes.filter(o =>
    o.personId === current.personId && o.id !== current.id && !o.hidden
  )
  if (peers.length > 0) { panToCard(peers[0]); return }

  // No rendered peer — walk up parent chain to find the NEAREST rendered
  // ancestor, expand their clan, then pan to the new peer after re-render.
  let cur: string | undefined = current.personId
  const seen = new Set<string>([current.personId])
  while (cur) {
    const parents = parentsOf.value.get(cur) ?? []
    if (parents.length === 0) break
    const par = parents[0]
    if (seen.has(par)) break
    seen.add(par)
    const ancestorNode = cv.value.nodes.find(n => n.personId === par && !n.hidden)
    if (ancestorNode) {
      if (!expandedClans.value.has(par)) toggleExpand(par)
      nextTick(() => {
        if (!cv.value) return
        const newPeers = cv.value.nodes.filter(o =>
          o.personId === current.personId && o.id !== current.id && !o.hidden
        )
        if (newPeers.length > 0) panToCard(newPeers[0])
      })
      return
    }
    cur = par
  }
}

// ── Card styling ──────────────────────────────────────────────────────
// Tradition colors override spine/gender styling. Chosen to avoid clashing
// with existing spine/female palette (which uses amber + rose + rose-50):
//   early_consensus (橘 orange) — east+west agree
//   catholic        (紫 purple) — bishops' colour; avoids red/rose clash
//   orthodox        (綠 emerald) — Byzantine green; avoids yellow/amber clash
//   rabbinic        (藍 blue)   — Rabbinic post-biblical
// Spine bar (amber/rose left edge) stays — it's rendered as a separate div.
function cardClass(n: LNode) {
  const base = 'shadow-sm hover:shadow-md rounded-xl cursor-pointer'
  if (n.tradition === 'early_consensus')
    return `border border-orange-300 bg-orange-50 ${base}`
  if (n.tradition === 'catholic')
    return `border border-purple-300 bg-purple-50 ${base}`
  if (n.tradition === 'orthodox')
    return `border border-emerald-300 bg-emerald-50 ${base}`
  if (n.tradition === 'rabbinic')
    return `border border-blue-300 bg-blue-50 ${base}`
  if (n.spineKind === 'A' || n.spineKind === 'S' || n.spineKind === 'single')
    return `border border-stone-300 bg-white ${base}`
  if (n.spineKind === 'B')
    return `border border-rose-300 bg-white ${base}`
  if (n.gender === 'female')
    return 'border border-rose-200 bg-rose-50/90 hover:shadow-sm rounded-xl cursor-pointer'
  return 'border border-slate-200 bg-white hover:shadow-sm rounded-xl cursor-pointer'
}
function cardStyle(n: LNode) {
  return { left: n.x + 'px', top: n.y + 'px', width: n.w + 'px', minHeight: n.h + 'px' }
}
function genLabelColor(n: LNode) {
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

// 約瑟（馬利亞之夫）卡片在 viewport 上的螢幕座標 — 給浮動「耶穌聖家詮釋」按鈕用
const josephScreenPos = computed(() => {
  if (!cv.value) return { x: 0, y: 0, visible: false }
  const joseph = cv.value.nodes.find(n => n.rawName === '約瑟（馬利亞之夫）' && !n.hidden)
  if (!joseph) return { x: 0, y: 0, visible: false }
  // Toggle 放在約瑟卡片的右側、與卡片頂部對齊
  const offsetX = joseph.w * zoom.value + 12
  return {
    x: joseph.x * zoom.value + panX.value + offsetX,
    y: joseph.y * zoom.value + panY.value,
    visible: true,
  }
})

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
