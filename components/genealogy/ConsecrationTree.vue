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
    <div v-if="!ready" class="flex items-center justify-center h-full text-gray-400 text-sm">
      載入中…
    </div>

    <template v-else>
      <div
        class="absolute top-0 left-0 origin-top-left"
        :style="{
          width: cv.w + 'px',
          height: cv.h + 'px',
          transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
          willChange: 'transform',
        }"
      >
        <svg class="absolute inset-0 pointer-events-none overflow-visible"
             :width="cv.w" :height="cv.h">
          <path v-for="(p, i) in cv.paths" :key="'p'+i"
                :d="p.d" :stroke="p.stroke || '#9ca3af'"
                :stroke-width="p.width ?? 1.5" fill="none"
                stroke-linecap="round"
                :stroke-dasharray="p.dashes ?? ''"
                :opacity="p.opacity ?? 1" />
        </svg>

        <!-- Column see badges -->
        <div
          v-for="col in cv.columns" :key="'col'+col.id"
          class="absolute text-center font-bold tracking-wide"
          :style="{
            left: col.x + 'px',
            top: (col.headerY) + 'px',
            width: COL_W + 'px',
            color: col.color,
            fontSize: '13px',
          }"
        >
          <div>{{ col.see_zh }}</div>
          <div class="text-[10px] font-medium text-slate-400">{{ col.church_short || col.church }}</div>
        </div>

        <!-- Bishop cards -->
        <div
          v-for="n in cv.nodes" :key="n.id"
          class="absolute rounded-lg bg-white border shadow-sm hover:shadow-md transition-shadow"
          :style="{
            left: n.x + 'px',
            top: n.y + 'px',
            width: n.w + 'px',
            minHeight: n.h + 'px',
            borderColor: n.color + '55',
          }"
          :title="n.tooltip || ''"
        >
          <div class="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-full"
               :style="{ background: n.color }" />
          <div class="pl-3 pr-2 py-1 leading-tight">
            <div class="flex items-baseline gap-1.5 text-[11.5px]">
              <span v-if="n.successionNum != null" class="text-[9px] text-slate-400 tabular-nums">#{{ n.successionNum }}</span>
              <span class="font-semibold text-slate-800 truncate flex-1">{{ n.label }}</span>
            </div>
            <div v-if="n.sub" class="text-[9px] text-slate-500 truncate">{{ n.sub }}</div>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="absolute top-3 right-3 z-40 flex flex-col gap-1.5 pointer-events-auto">
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoom = Math.min(3, zoom + 0.1)">+</button>
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoom = Math.max(0.1, zoom - 0.1)">−</button>
        <div class="text-[9px] text-gray-400 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</div>
        <button class="px-1.5 py-1.5 bg-white/90 border border-violet-300 rounded-lg text-violet-700
                       text-[10px] font-medium shadow-sm hover:bg-violet-50 transition cursor-default"
                @click.stop="fitAll">定位<br>全圖</button>
      </div>

      <!-- Stats / Legend -->
      <div class="absolute bottom-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-2.5
                  text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-0.5">
        <div class="font-semibold text-slate-700 mb-1">按立樹</div>
        <div>{{ cv.columns.length }} 條教座鏈 · {{ cv.nodes.length }} 位主教</div>
        <div class="text-[9px] text-slate-400 mt-1">縱向 = 同教座內承繼　·　橫向 = 跨教座按立</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ConsecrationTree' })

interface BishopIn {
  id: string
  name_zh: string
  name_en: string | null
  succession_number: number | null
  start_year: number | null
  end_year: number | null
  consecrator_bishop_id?: string | null
  church: string | null
  status: string
  notes: string | null
}
interface SpineIn {
  key: string
  primaryApostleId: string
  secondaryApostleId: string | null
  color: string
  patriarchateYear?: number
  see: { id: string; see_zh: string; name_zh: string; church: string } | null
  bishops: BishopIn[]
}
interface BranchIn {
  id: string
  see_zh: string
  name_zh: string
  church: string
  founded_year: number | null
  parent_see_id: string
  parent_spine_key: string
  parent_bishop_id: string | null
  is_split: boolean
  bishops: BishopIn[]
}
interface GraphIn {
  jesus: { id: string; name_zh: string; name_en: string }
  apostles: { id: string; name_zh: string; name_en: string }[]
  spines: SpineIn[]
  branches: BranchIn[]
  teachings?: unknown[]
}

const props = defineProps<{ graph: GraphIn | null }>()
const ready = computed(() => !!props.graph)

// ── Layout constants ──
const COL_W   = 160
const COL_GAP = 30
const BISH_H  = 36
const BISH_VG = 22
const PAD     = 40
const HEADER_H = 50

// ── Layout computation ──
const cv = computed(() => {
  const nodes: { id: string; label: string; sub?: string; x: number; y: number; w: number; h: number;
                 color: string; successionNum?: number | null; tooltip?: string }[] = []
  const paths: { d: string; stroke?: string; width?: number; dashes?: string; opacity?: number }[] = []
  const columns: { id: string; see_zh: string; church: string; church_short?: string; color: string;
                   x: number; headerY: number; bishops: BishopIn[] }[] = []

  if (!props.graph) return { nodes, paths, columns, w: 800, h: 600 }
  const g = props.graph

  // 1) Build (see_zh, church) → list of bishops + color
  // For spine: color = spine.color, see_zh = spine.see.see_zh, church = bishop.church
  // For branch: color = parent spine's color, see_zh = branch.see_zh
  type Col = {
    key: string
    see_zh: string
    church: string
    color: string
    bishops: BishopIn[]
  }
  const colMap = new Map<string, Col>()
  function colKey(see_zh: string, church: string | null | undefined): string {
    return `${see_zh}|${church ?? ''}`
  }
  function addBishopToCol(see_zh: string, b: BishopIn, color: string) {
    const k = colKey(see_zh, b.church)
    if (!colMap.has(k)) {
      colMap.set(k, { key: k, see_zh, church: b.church ?? '', color, bishops: [] })
    }
    colMap.get(k)!.bishops.push(b)
  }
  for (const sp of g.spines) {
    if (!sp.see) continue
    for (const b of sp.bishops) addBishopToCol(sp.see.see_zh, b, sp.color)
  }
  for (const br of g.branches) {
    const sp = g.spines.find(s => s.key === br.parent_spine_key)
    const color = sp?.color ?? '#94a3b8'
    for (const b of br.bishops) addBishopToCol(br.see_zh, b, color)
  }

  // Sort bishops within each column by succession_number then start_year
  for (const col of colMap.values()) {
    col.bishops.sort((a, b) => {
      const an = a.succession_number ?? 99999
      const bn = b.succession_number ?? 99999
      if (an !== bn) return an - bn
      return (a.start_year ?? 99999) - (b.start_year ?? 99999)
    })
  }

  // 2) Build bishop → col map
  const bishopColKey = new Map<string, string>()
  for (const col of colMap.values()) for (const b of col.bishops) bishopColKey.set(b.id, col.key)

  // 3) Build parent-of-column relationship via consecrator chain
  // For each column, find its "founder bishop" (the one earliest in column whose consecrator is in a different column).
  // That different column = parent.
  const parentOfCol = new Map<string, string>()   // child col key → parent col key
  for (const col of colMap.values()) {
    for (const b of col.bishops) {
      if (!b.consecrator_bishop_id) continue
      const consecratorColKey = bishopColKey.get(b.consecrator_bishop_id)
      if (consecratorColKey && consecratorColKey !== col.key && !parentOfCol.has(col.key)) {
        parentOfCol.set(col.key, consecratorColKey)
        break   // first such bishop = founder
      }
    }
  }

  // 4) Identify root columns (no parent)
  const allColKeys = [...colMap.keys()]
  const rootCols = allColKeys.filter(k => !parentOfCol.has(k))

  // 5) Compute column depth (X position) via DFS
  const colDepth = new Map<string, number>()
  function computeDepth(k: string): number {
    if (colDepth.has(k)) return colDepth.get(k)!
    const parent = parentOfCol.get(k)
    const d = parent ? computeDepth(parent) + 1 : 0
    colDepth.set(k, d)
    return d
  }
  for (const k of allColKeys) computeDepth(k)

  // 6) Group cols by depth, assign Y ranges. For simplicity, each column has its own X (depth*step)
  //    but Y position depends on chronological start of first bishop.
  //    A "kindof timeline": Y proportional to (earliest start_year of bishop in column)
  const allBishopYears = [...colMap.values()].flatMap(c => c.bishops.map(b => b.start_year ?? 100))
  const minYear = Math.min(...allBishopYears, 100)
  const maxYear = Math.max(...allBishopYears, 2030)
  const yearRange = maxYear - minYear
  const YEAR_PX = 1.5   // 1 year = 1.5 px (so 2000 years = 3000 px tall)

  function yearToY(year: number): number {
    return PAD + HEADER_H + (year - minYear) * YEAR_PX
  }

  // 7) Position columns horizontally by depth, columns at same depth stacked left to right per occurrence
  //    For simplicity, within same depth, sort by parent col's X (group children of same parent together)
  const depthToCols = new Map<number, string[]>()
  for (const k of allColKeys) {
    const d = colDepth.get(k)!
    if (!depthToCols.has(d)) depthToCols.set(d, [])
    depthToCols.get(d)!.push(k)
  }
  // Sort each depth by earliest first-bishop year (chronological)
  for (const arr of depthToCols.values()) {
    arr.sort((a, b) => {
      const ay = colMap.get(a)!.bishops[0]?.start_year ?? 99999
      const by = colMap.get(b)!.bishops[0]?.start_year ?? 99999
      return ay - by
    })
  }

  const colX = new Map<string, number>()
  let cursorX = PAD
  const maxDepth = Math.max(...depthToCols.keys())
  for (let d = 0; d <= maxDepth; d++) {
    const cols = depthToCols.get(d) ?? []
    for (const k of cols) {
      colX.set(k, cursorX)
      cursorX += COL_W + COL_GAP
    }
  }
  const totalW = cursorX + PAD

  // 8) Build column metadata + render
  for (const k of allColKeys) {
    const col = colMap.get(k)!
    const x = colX.get(k)!
    const firstBishopY = col.bishops[0]?.start_year != null ? yearToY(col.bishops[0].start_year) : PAD + HEADER_H
    columns.push({
      id: k,
      see_zh: col.see_zh,
      church: col.church,
      church_short: col.church.length > 8 ? col.church.slice(0, 8) + '…' : col.church,
      color: col.color,
      x,
      headerY: Math.max(PAD, firstBishopY - 32),
      bishops: col.bishops,
    })
  }

  // 9) Render bishops + lines
  let maxY = 0
  for (const col of columns) {
    let prevY: number | null = null
    let prevId: string | null = null
    for (const b of col.bishops) {
      const y = b.start_year != null ? yearToY(b.start_year) : (prevY != null ? prevY + BISH_H + BISH_VG : PAD + HEADER_H)
      nodes.push({
        id: 'b_' + b.id,
        label: b.name_zh,
        sub: b.start_year != null
          ? `${formatYear(b.start_year)}${b.end_year != null ? '–' + formatYear(b.end_year) : ''}`
          : '',
        x: col.x,
        y,
        w: COL_W,
        h: BISH_H,
        color: col.color,
        successionNum: b.succession_number,
        tooltip: `${b.name_zh}${b.name_en ? ' / ' + b.name_en : ''}\n任期：${formatYear(b.start_year)}–${formatYear(b.end_year)}${b.notes ? '\n' + b.notes : ''}`,
      })
      // Within-column vertical line (predecessor → successor)
      if (prevY != null) {
        const cx = col.x + COL_W / 2
        paths.push({ d: `M${cx},${prevY + BISH_H} L${cx},${y}`, stroke: col.color, width: 1.5, opacity: 0.35 })
      }
      // Cross-column consecration line (from another col's bishop to this one)
      if (b.consecrator_bishop_id) {
        const conKey = bishopColKey.get(b.consecrator_bishop_id)
        if (conKey && conKey !== col.key) {
          // Find consecrator's position
          const conCol = colMap.get(conKey)!
          const conBishop = conCol.bishops.find(x => x.id === b.consecrator_bishop_id)
          if (conBishop) {
            const conX = colX.get(conKey)! + COL_W
            const conY = (conBishop.start_year != null ? yearToY(conBishop.start_year) : PAD + HEADER_H) + BISH_H / 2
            const toX = col.x
            const toY = y + BISH_H / 2
            const midX = (conX + toX) / 2
            paths.push({
              d: `M${conX},${conY} L${midX},${conY} L${midX},${toY} L${toX},${toY}`,
              stroke: col.color, width: 2.5, opacity: 0.9,
            })
          }
        }
      }
      prevY = y
      prevId = b.id
      maxY = Math.max(maxY, y + BISH_H)
    }
  }

  const w = Math.max(totalW, 1200)
  const h = Math.max(maxY + PAD, 600)
  return { nodes, paths, columns, w, h }
})

function formatYear(y: number | null | undefined): string {
  if (y == null) return '?'
  return y < 0 ? `主前${Math.abs(y)}` : String(y)
}

// ── Pan / zoom ──
const viewportRef = ref<HTMLDivElement | null>(null)
const panX = ref(0)
const panY = ref(0)
const zoom = ref(0.5)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, panX: 0, panY: 0 })

function onWheel(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey) {
    const delta = -e.deltaY * 0.001
    const newZoom = Math.max(0.1, Math.min(3, zoom.value + delta))
    const rect = viewportRef.value?.getBoundingClientRect()
    if (rect) {
      const mx = e.clientX - rect.left
      const my = e.clientY - rect.top
      const ratio = newZoom / zoom.value
      panX.value = mx - (mx - panX.value) * ratio
      panY.value = my - (my - panY.value) * ratio
    }
    zoom.value = newZoom
  } else if (e.shiftKey) {
    panX.value -= e.deltaY
  } else {
    panY.value -= e.deltaY
  }
}
function onPointerDown(e: PointerEvent) {
  if ((e.target as HTMLElement)?.closest('button')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY, panX: panX.value, panY: panY.value }
  ;(e.target as HTMLElement).setPointerCapture?.(e.pointerId)
}
function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  panX.value = dragStart.value.panX + (e.clientX - dragStart.value.x)
  panY.value = dragStart.value.panY + (e.clientY - dragStart.value.y)
}
function onPointerUp() { isDragging.value = false }

function fitAll() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const c = cv.value
  const sx = (rect.width  - 40) / c.w
  const sy = (rect.height - 40) / c.h
  zoom.value = Math.min(sx, sy, 1)
  panX.value = (rect.width  - c.w * zoom.value) / 2
  panY.value = 20
}

onMounted(() => { nextTick(fitAll) })
watch(() => props.graph, () => { nextTick(fitAll) })
</script>
