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

        <!-- Apostle row -->
        <div
          v-for="a in cv.apostles" :key="a.id"
          class="absolute rounded-lg bg-white border border-slate-200 shadow-sm"
          :style="{ left: a.x + 'px', top: a.y + 'px', width: a.w + 'px', minHeight: a.h + 'px' }"
          :title="a.tooltip"
        >
          <div class="px-2 py-1 text-center">
            <div class="text-[10.5px] font-semibold text-slate-800 truncate">{{ a.name_zh }}</div>
            <div class="text-[8px] text-slate-400 truncate">{{ a.name_en }}</div>
          </div>
        </div>

        <!-- Jesus card -->
        <div
          v-if="cv.jesus"
          class="absolute rounded-lg bg-amber-50 border-2 border-amber-400 shadow"
          :style="{ left: cv.jesus.x + 'px', top: cv.jesus.y + 'px', width: cv.jesus.w + 'px', minHeight: cv.jesus.h + 'px' }"
        >
          <div class="px-2 py-1.5 text-center">
            <div class="text-[13px] font-bold text-amber-700">{{ cv.jesus.label }}</div>
          </div>
        </div>

        <!-- See header badges (expandable column controls) -->
        <button
          v-for="col in cv.columns" :key="'col'+col.id"
          class="absolute text-center cursor-default rounded-md border border-transparent hover:border-violet-300 hover:bg-violet-50 transition"
          :style="{
            left: col.x + 'px',
            top: col.headerY + 'px',
            width: COL_W + 'px',
            padding: '4px 2px',
          }"
          @click.stop="toggleColumn(col.id)"
        >
          <div class="flex items-center justify-center gap-1">
            <span class="text-[10px]" :style="{ color: col.color }">{{ isColExpanded(col.id) ? '▾' : '▸' }}</span>
            <span class="font-bold text-[12px]" :style="{ color: col.color }">{{ col.see_zh }}</span>
            <span class="text-[9px] text-slate-400 tabular-nums">{{ col.totalBishops }}</span>
          </div>
          <div class="text-[9px] text-slate-400">{{ col.church_short }}</div>
        </button>

        <!-- Bishop cards -->
        <button
          v-for="n in cv.nodes" :key="n.id"
          class="absolute rounded-lg bg-white border shadow-sm hover:shadow-md transition cursor-default"
          :style="{
            left: n.x + 'px',
            top: n.y + 'px',
            width: n.w + 'px',
            minHeight: n.h + 'px',
            borderColor: n.color + '55',
          }"
          :title="n.tooltip || ''"
          @click.stop="onBishopClick(n)"
        >
          <div class="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-full"
               :style="{ background: n.color }" />
          <div class="pl-3 pr-2 py-1 leading-tight text-left">
            <div class="flex items-baseline gap-1.5 text-[11.5px]">
              <span v-if="n.successionNum != null" class="text-[9px] text-slate-400 tabular-nums">#{{ n.successionNum }}</span>
              <span class="font-semibold text-slate-800 truncate flex-1">{{ n.label }}</span>
              <span v-if="n.consecratedCount && n.consecratedCount > 0"
                    class="text-[8.5px] text-violet-600 tabular-nums shrink-0"
                    :title="'按立 ' + n.consecratedCount + ' 條外部教座'">▶{{ n.consecratedCount }}</span>
            </div>
            <div v-if="n.sub" class="text-[9px] text-slate-500 truncate">{{ n.sub }}</div>
          </div>
        </button>
      </div>

      <!-- Controls -->
      <div class="absolute top-3 right-3 z-40 flex flex-col gap-1.5 pointer-events-auto">
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoom = Math.min(3, zoom + 0.1)">+</button>
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoom = Math.max(0.1, zoom - 0.1)">−</button>
        <div class="text-[9px] text-gray-400 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</div>
        <button class="px-1.5 py-1.5 bg-white/90 border border-violet-300 rounded-lg text-violet-700 text-[10px] font-medium shadow-sm hover:bg-violet-50 transition cursor-default"
                @click.stop="fitAll">定位<br>全圖</button>
        <button class="px-1.5 py-1.5 bg-white/90 border border-gray-200 rounded-lg text-gray-600 text-[10px] font-medium shadow-sm hover:bg-gray-50 transition cursor-default"
                @click.stop="collapseAll">收起<br>全部</button>
      </div>

      <!-- Legend -->
      <div class="absolute bottom-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-2.5 text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-0.5 max-w-[260px]">
        <div class="font-semibold text-slate-700 mb-1">按立樹</div>
        <div>{{ cv.columns.length }} 條教座鏈 · {{ cv.nodes.length }} 位主教（顯示中）</div>
        <div class="text-[9px] text-slate-400 mt-1">▸/▾ 點教座標題展開/收起　·　▶N 表該主教按立外部教座</div>
        <div class="text-[9px] text-slate-400">縱向 = 同教座承繼　·　橫向 = 跨教座按立</div>
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
interface ApostleIn { id: string; name_zh: string; name_en: string }
interface GraphIn {
  jesus: { id: string; name_zh: string; name_en: string }
  apostles: ApostleIn[]
  spines: SpineIn[]
  branches: BranchIn[]
  teachings?: unknown[]
}

const props = defineProps<{ graph: GraphIn | null }>()
const ready = computed(() => !!props.graph)

// ── Expand state ───────────────────────────────────────────
// 預設只展開 7 大 spine 的「第一任主教」位置（spine 自己預設折疊）。
// 點 see 標題 = toggle column expand/collapse.
const expandedColumns = ref<Set<string>>(new Set())
function isColExpanded(colKey: string): boolean {
  return expandedColumns.value.has(colKey)
}
function toggleColumn(colKey: string) {
  const s = new Set(expandedColumns.value)
  if (s.has(colKey)) s.delete(colKey)
  else s.add(colKey)
  expandedColumns.value = s
}
function collapseAll() { expandedColumns.value = new Set() }

// 點主教卡：若該主教按立了外部教座，展開對應分支 column
function onBishopClick(n: any) {
  if (n.consecratedColIds && n.consecratedColIds.length > 0) {
    const s = new Set(expandedColumns.value)
    for (const ck of n.consecratedColIds) s.add(ck)
    expandedColumns.value = s
  }
}

// ── Layout constants ──
const COL_W   = 160
const COL_GAP = 30
const BISH_H  = 36
const BISH_VG = 16
const PAD     = 40
const HEADER_H = 38
const JESUS_W = 110
const JESUS_H = 36
const APO_W   = 100
const APO_H   = 34
const APO_HG  = 18

// ── Layout ──
const cv = computed(() => {
  const nodes: any[] = []
  const paths: any[] = []
  const columns: any[] = []
  let w = 1200, h = 600
  let jesus: any = null
  const apostles: any[] = []

  if (!props.graph) return { nodes, paths, columns, apostles, jesus, w, h }
  const g = props.graph

  // Build (see, church) → bishops
  type Col = { key: string; see_zh: string; church: string; color: string; bishops: BishopIn[]; isSpine: boolean; spineKey?: string }
  const colMap = new Map<string, Col>()
  function colKey(see_zh: string, church: string | null | undefined) { return `${see_zh}|${church ?? ''}` }
  function addBishop(see_zh: string, b: BishopIn, color: string, isSpine: boolean, spineKey?: string) {
    const k = colKey(see_zh, b.church)
    if (!colMap.has(k)) colMap.set(k, { key: k, see_zh, church: b.church ?? '', color, bishops: [], isSpine, spineKey })
    colMap.get(k)!.bishops.push(b)
  }
  for (const sp of g.spines) {
    if (!sp.see) continue
    for (const b of sp.bishops) addBishop(sp.see.see_zh, b, sp.color, true, sp.key)
  }
  for (const br of g.branches) {
    const sp = g.spines.find(s => s.key === br.parent_spine_key)
    const color = sp?.color ?? '#94a3b8'
    for (const b of br.bishops) addBishop(br.see_zh, b, color, false)
  }
  // Sort each col's bishops by succession_number then year
  for (const col of colMap.values()) {
    col.bishops.sort((a, b) => {
      const an = a.succession_number ?? 99999
      const bn = b.succession_number ?? 99999
      if (an !== bn) return an - bn
      return (a.start_year ?? 99999) - (b.start_year ?? 99999)
    })
  }

  // bishop → col + bishop record
  const bishopColKey = new Map<string, string>()
  const bishopById = new Map<string, BishopIn>()
  for (const col of colMap.values()) for (const b of col.bishops) {
    bishopColKey.set(b.id, col.key)
    bishopById.set(b.id, b)
  }

  // For each bishop: which OTHER-col bishops they consecrated
  // (= reverse map: consecrator_bishop_id → set of bishops consecrated by them, FILTERED to cross-col only)
  const consecratedExternal = new Map<string, BishopIn[]>()   // bishopId → bishops consecrated in other cols
  for (const b of bishopById.values()) {
    if (!b.consecrator_bishop_id) continue
    const myColKey = bishopColKey.get(b.id)
    const conColKey = bishopColKey.get(b.consecrator_bishop_id)
    if (!myColKey || !conColKey || myColKey === conColKey) continue   // same-col = succession, not external
    if (!consecratedExternal.has(b.consecrator_bishop_id)) consecratedExternal.set(b.consecrator_bishop_id, [])
    consecratedExternal.get(b.consecrator_bishop_id)!.push(b)
  }

  // 7 spine columns 均分排列（apostle 列上方）
  const spineCols = g.spines.map(sp => sp.see ? colMap.get(colKey(sp.see.see_zh, getSpineMainChurch(sp))) : null)
  // Spines may have multiple churches — use first non-empty col matching the spine see_zh & primaryChurches
  function getSpineMainChurch(sp: SpineIn): string {
    // pick the col with most bishops (or '未分裂教會' / '東正教' / etc.)
    return sp.see?.church ?? ''
  }
  // Filter out null spines
  const validSpineCols = spineCols.filter(c => c != null) as Col[]

  // ─ Layout: Jesus + Apostles + Spines + Branches ─
  // Apostle row total width
  const apostleRowW = g.apostles.length * APO_W + (g.apostles.length - 1) * APO_HG

  // Canvas width: at least apostle row + padding, but expand horizontally as branches expand
  // First pass: spines均分 below apostles (7 spines)
  const N_SPINES = validSpineCols.length || 7
  // Calculate min canvas width to fit both apostle row and 7 spines均分
  const spineSpan = N_SPINES * COL_W + (N_SPINES - 1) * Math.max(COL_GAP, 80)
  const baseW = Math.max(apostleRowW, spineSpan) + PAD * 2

  // Y positions
  const jesusY = PAD
  const apostleY = jesusY + JESUS_H + 40
  const spineHeaderY = apostleY + APO_H + 60
  const spineFirstY = spineHeaderY + HEADER_H + 8

  // Jesus card centered
  jesus = { x: (baseW - JESUS_W) / 2, y: jesusY, w: JESUS_W, h: JESUS_H, label: '耶穌基督' }

  // Apostles centered
  const apostleStartX = (baseW - apostleRowW) / 2
  const apostleX = new Map<string, number>()
  for (let i = 0; i < g.apostles.length; i++) {
    const a = g.apostles[i]
    const ax = apostleStartX + i * (APO_W + APO_HG)
    apostles.push({ id: a.id, name_zh: a.name_zh, name_en: a.name_en, x: ax, y: apostleY, w: APO_W, h: APO_H, tooltip: `${a.name_zh}（${a.name_en}）` })
    apostleX.set(a.id, ax + APO_W / 2)
  }

  // Render Jesus → apostles fan
  const fanY = jesusY + JESUS_H + 18
  paths.push({ d: `M${jesus.x + JESUS_W/2},${jesusY + JESUS_H} L${jesus.x + JESUS_W/2},${fanY}`, stroke: '#a16207', width: 1.8 })
  if (g.apostles.length > 0) {
    const xs = g.apostles.map(a => apostleX.get(a.id)!)
    const xMin = Math.min(...xs), xMax = Math.max(...xs)
    paths.push({ d: `M${xMin},${fanY} L${xMax},${fanY}`, stroke: '#a16207', width: 1.8 })
    for (const x of xs) paths.push({ d: `M${x},${fanY} L${x},${apostleY}`, stroke: '#a16207', width: 1.5 })
  }

  // Spines均分 horizontally — total span = N_SPINES * COL_W + (N_SPINES-1) * gap
  const spineGap = Math.max(COL_GAP, (apostleRowW - N_SPINES * COL_W) / Math.max(1, N_SPINES - 1))
  const spineRowStartX = (baseW - (N_SPINES * COL_W + (N_SPINES - 1) * spineGap)) / 2
  const spineColX = new Map<string, number>()   // colKey → X
  for (let i = 0; i < validSpineCols.length; i++) {
    const col = validSpineCols[i]
    spineColX.set(col.key, spineRowStartX + i * (COL_W + spineGap))
  }

  // ─ Render each spine column + recursive expand branches ─
  // For collapsed: only see header + first bishop
  // For expanded: see header + all bishops + lines + ▶ markers on those who consecrate external

  const rendered = new Set<string>()   // colKeys already rendered
  let nextBranchX = spineRowStartX + N_SPINES * (COL_W + spineGap)   // X for next branch column (right of spines)
  const colYRanges = new Map<string, { topY: number; bottomY: number }>()   // for layout overlap calc

  function renderColumn(col: Col, headerX: number, parentBishopY?: number) {
    if (rendered.has(col.key)) return
    rendered.add(col.key)
    const expanded = isColExpanded(col.key)
    // Y starts at spineFirstY for spine; for branch, at parentBishopY (from consecrator)
    const startY = parentBishopY != null ? parentBishopY : spineFirstY
    // Header position: just above startY
    const headerY = startY - HEADER_H

    const bishopsToShow = expanded ? col.bishops : col.bishops.slice(0, 1)

    columns.push({
      id: col.key,
      see_zh: col.see_zh,
      church: col.church,
      church_short: col.church.length > 10 ? col.church.slice(0, 10) + '…' : col.church,
      color: col.color,
      x: headerX,
      headerY,
      totalBishops: col.bishops.length,
    })

    let cy = startY
    let prevY: number | null = null
    let prevCx: number | null = null
    for (const b of bishopsToShow) {
      // Within-column vertical line
      if (prevY != null) {
        const cx = headerX + COL_W / 2
        paths.push({ d: `M${cx},${prevY + BISH_H} L${cx},${cy}`, stroke: col.color, width: 2.5, opacity: 0.7 })
      }
      // External consecrations from this bishop?
      const ext = consecratedExternal.get(b.id) ?? []
      const externalColKeys = [...new Set(ext.map(eb => bishopColKey.get(eb.id)!).filter(k => k !== col.key))]
      nodes.push({
        id: 'b_' + b.id,
        label: b.name_zh,
        sub: b.start_year != null ? `${formatYear(b.start_year)}${b.end_year != null ? '–' + formatYear(b.end_year) : ''}` : '',
        x: headerX, y: cy, w: COL_W, h: BISH_H,
        color: col.color,
        successionNum: b.succession_number,
        consecratedCount: externalColKeys.length,
        consecratedColIds: externalColKeys,
        tooltip: `${b.name_zh}${b.name_en ? ' / ' + b.name_en : ''}\n任期：${formatYear(b.start_year)}–${formatYear(b.end_year)}${b.notes ? '\n' + b.notes : ''}`,
      })
      prevY = cy
      prevCx = headerX + COL_W / 2

      // Recurse: if this bishop consecrated external sees, render those branches IF EXPANDED
      // The branch column expands to the right at nextBranchX
      // For now, just compute and render expanded branches
      if (externalColKeys.length > 0 && expanded) {
        for (const extColKey of externalColKeys) {
          if (rendered.has(extColKey)) continue
          const extCol = colMap.get(extColKey)
          if (!extCol) continue
          // Place this branch column at nextBranchX, attach at this bishop's Y row
          const branchX = nextBranchX
          nextBranchX += COL_W + COL_GAP
          // Draw consecration line from current bishop card right edge → branch column left edge
          const consY = cy + BISH_H / 2
          const fromX = headerX + COL_W
          const toX = branchX
          const branchStartY = cy   // align top of branch first bishop with consecrator
          paths.push({
            d: `M${fromX},${consY} L${(fromX + toX) / 2},${consY} L${(fromX + toX) / 2},${branchStartY + BISH_H / 2} L${toX},${branchStartY + BISH_H / 2}`,
            stroke: col.color, width: 2, opacity: 0.9,
          })
          renderColumn(extCol, branchX, branchStartY)
        }
      }

      cy += BISH_H + BISH_VG
    }
    colYRanges.set(col.key, { topY: startY, bottomY: cy })
  }

  // Render the 7 spine columns
  for (const col of validSpineCols) {
    const headerX = spineColX.get(col.key)!
    renderColumn(col, headerX)
  }

  // Compute canvas dimensions
  w = Math.max(baseW, nextBranchX + PAD)
  let maxBottom = 0
  for (const r of colYRanges.values()) maxBottom = Math.max(maxBottom, r.bottomY)
  h = maxBottom + PAD

  // Draw apostle → spine connection lines (primary apostle → spine header)
  for (const sp of g.spines) {
    if (!sp.see) continue
    const ck = colKey(sp.see.see_zh, sp.see.church)
    const headerX = spineColX.get(ck)
    if (headerX == null) continue
    const headerCX = headerX + COL_W / 2
    const apX = apostleX.get(sp.primaryApostleId)
    if (apX != null) {
      const fromY = apostleY + APO_H
      const toY = spineHeaderY
      const midY = (fromY + toY) / 2
      paths.push({ d: `M${apX},${fromY} L${apX},${midY} L${headerCX},${midY} L${headerCX},${toY}`, stroke: sp.color, width: 1.8 })
    }
  }

  return { nodes, paths, columns, apostles, jesus, w, h }
})

function formatYear(y: number | null | undefined): string {
  if (y == null) return '?'
  return y < 0 ? `主前${Math.abs(y)}` : String(y)
}

// ── Pan / zoom ──
const viewportRef = ref<HTMLDivElement | null>(null)
const panX = ref(0)
const panY = ref(0)
const zoom = ref(0.8)
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
