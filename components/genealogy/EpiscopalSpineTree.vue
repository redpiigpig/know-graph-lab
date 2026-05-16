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

          <!-- spine guide lines (faint) -->
          <line v-for="(g, i) in cv.guides" :key="'g'+i"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- Lines: paths with optional dashes
               - Dashes:
                   none → 實線
                   '4,3' → 一般虛線
                   '2,4,8,4' → 鋸齒線（教座分裂）
                   '2,3' → 細點線（教導關係的暗示） -->
          <path v-for="(p, i) in cv.paths" :key="'p'+i"
                :d="p.d" :stroke="p.stroke || '#9ca3af'"
                :stroke-width="p.width ?? 1.5" fill="none"
                stroke-linecap="round"
                :stroke-dasharray="p.dashes ?? (p.dashed ? '4,3' : '')"
                :opacity="p.opacity ?? 1" />
        </svg>

        <!-- Cards -->
        <div
          v-for="n in cv.nodes" :key="n.id"
          class="node-card absolute"
          :class="cardClass(n)"
          :style="{
            left: n.x + 'px',
            top: n.y + 'px',
            width: n.w + 'px',
            minHeight: n.h + 'px',
          }"
          :title="n.tooltip || ''"
        >
          <!-- Spine bar (left edge) — skip for see kind which is pure text -->
          <div v-if="n.spineColor && n.kind !== 'see'"
               class="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-full"
               :style="{ background: n.spineColor }" />

          <div class="leading-tight"
               :class="n.kind === 'see' ? '' : (n.spineColor ? 'px-2 py-1.5 pl-3' : 'px-2 py-1.5')">
            <template v-if="n.kind === 'jesus'">
              <div class="text-[14px] font-bold text-amber-700 text-center tracking-wide">{{ n.label }}</div>
            </template>

            <template v-else-if="n.kind === 'apostle'">
              <div class="text-[11.5px] font-semibold text-slate-800 truncate text-center">{{ n.label }}</div>
              <div class="text-[8.5px] text-slate-400 truncate text-center mt-0.5">{{ n.sub }}</div>
            </template>

            <template v-else-if="n.kind === 'see'">
              <div class="text-[11px] font-bold truncate text-right tracking-wide"
                   :style="n.spineColor ? { color: n.spineColor } : undefined">{{ n.label }}</div>
            </template>

            <template v-else-if="n.kind === 'bishop'">
              <div class="flex items-center gap-1.5 w-full text-[10.5px]">
                <span v-if="n.successionNum != null"
                      class="text-[8.5px] text-slate-400 tabular-nums w-5 text-right shrink-0">
                  {{ n.successionNum }}
                </span>
                <span class="font-medium text-slate-800 truncate flex-1 text-left">{{ n.label }}</span>
              </div>
              <div v-if="n.sub"
                   class="text-[8px] text-slate-400 truncate w-full text-left"
                   :class="n.successionNum != null ? 'pl-6' : ''">
                {{ n.sub }}
              </div>
            </template>

            <template v-else-if="n.kind === 'branch-see'">
              <button
                class="flex items-center gap-1 w-full text-[10.5px] cursor-default"
                @click.stop="toggleBranch(n.branchId!)"
              >
                <span class="text-[10px] text-violet-500 w-3 shrink-0">{{ expandedBranches.has(n.branchId!) ? '▾' : '▸' }}</span>
                <span class="font-semibold truncate flex-1 text-left text-slate-800">{{ n.label }}</span>
                <span class="text-[8px] text-slate-400 tabular-nums shrink-0">{{ n.bishopCount }}</span>
              </button>
              <div v-if="n.sub" class="text-[8px] text-slate-400 truncate w-full text-left pl-3.5">{{ n.sub }}</div>
            </template>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="absolute top-3 right-3 z-40 flex flex-col gap-1.5 pointer-events-auto">
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoomIn">+</button>
        <button class="w-8 h-8 bg-white/90 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50
                       text-base font-medium shadow-sm transition flex items-center justify-center cursor-default"
                @click.stop="zoomOut">−</button>
        <div class="text-[9px] text-gray-400 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</div>
        <button class="px-1.5 py-1.5 bg-white/90 border border-violet-300 rounded-lg text-violet-700
                       text-[10px] font-medium shadow-sm hover:bg-violet-50 transition cursor-default"
                @click.stop="fitAll">定位<br>全圖</button>
      </div>

      <!-- Legend -->
      <div class="absolute bottom-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-2.5
                  text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-0.5 max-w-[260px]">
        <div class="font-semibold text-slate-700 mb-1">七大宗主教座</div>
        <div class="grid grid-cols-2 gap-x-2 gap-y-0.5">
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-red-500 rounded-full" />羅馬（彼得＋保羅）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-blue-500 rounded-full" />君士坦丁堡（安得烈）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-amber-500 rounded-full" />亞歷山卓（彼得＋巴拿巴）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-cyan-600 rounded-full" />安提阿（彼得）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-green-600 rounded-full" />耶路撒冷（雅各）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-purple-600 rounded-full" />亞美尼亞（達太）</div>
          <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-[3px] bg-slate-500 rounded-full" />亞述（多馬）</div>
        </div>
        <div class="font-semibold text-slate-700 mt-2 mb-0.5 pt-1.5 border-t border-gray-100">線條種類</div>
        <div class="space-y-0.5">
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 h-[1.5px] bg-slate-400" />
            教座傳承（spine 內承繼）
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 h-[2.5px] bg-slate-400" />
            設立教座（新建子座）
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 h-[2px]"
                  style="background-image: repeating-linear-gradient(90deg, #dc2626 0 2px, transparent 2px 6px, #dc2626 6px 14px, transparent 14px 18px);" />
            教座分裂（rival 繼承）
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 h-[1.5px] bg-orange-500 rounded-full" />
            師徒教導（橘）
          </div>
        </div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">▸/▾ 旁支收／展　·　Ctrl＋滾輪：縮放</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'EpiscopalSpineTree' })

interface ApostleIn { id: string; name_zh: string; name_en: string }
interface SeeIn {
  id: string; see_zh: string; name_zh: string; name_en: string | null
  church: string; tradition: string; founded_year: number | null
}
interface BishopIn {
  id: string; name_zh: string; name_en: string | null
  succession_number: number | null
  start_year: number | null; end_year: number | null
  appointed_by: string | null; church: string | null
  status: string; notes: string | null
}
interface SpineIn {
  key: string
  primaryApostleId: string
  secondaryApostleId: string | null
  color: string
  see: SeeIn | null
  bishops: BishopIn[]
}
interface BranchIn {
  id: string; see_zh: string; name_zh: string; name_en: string | null
  church: string; tradition: string; founded_year: number | null
  parent_see_id: string; parent_spine_key: string
  parent_bishop_id: string | null
  is_split: boolean    // true: 教座分裂 (same see_zh as parent); false: 設立教座 (new see)
  bishops: BishopIn[]
}
interface TeachingIn {
  id: string
  teacher_name_zh: string
  teacher_name_en: string | null
  student_name_zh: string
  student_name_en: string | null
  period_year: number | null
  relationship: string
  source: string | null
  notes: string | null
  teacher_bishop_id: string | null
  student_bishop_id: string | null
}
interface GraphIn {
  jesus: { id: string; name_zh: string; name_en: string }
  apostles: ApostleIn[]
  spines: SpineIn[]
  branches: BranchIn[]
  teachings?: TeachingIn[]
}

const props = defineProps<{ graph: GraphIn | null }>()
const ready = computed(() => !!props.graph)

// ── Layout constants ────────────────────────────────────────
const PAD     = 50

const JESUS_W = 110
const JESUS_H = 36

// Apostle cards are narrow — they're just identity badges; the wide cards
// belong to bishops below.
const APO_W   = 100
const APO_H   = 34
const APO_HG  = 20     // gap between apostle lanes (apostle row width is driven by spine clusters below)

// See name appears as PURE TEXT (no card frame) to the LEFT of bishop #2.
// User: 「教座名稱旁邊不要再有卡片框框，這會被跟人搞混」
const SEE_LABEL_W = 70    // text-only label, just enough for 4-5 chars
const SEE_LABEL_GAP = 6   // gap between label text and bishop card

const BISH_W  = 160       // bishop / branch-bishop cards — the "people" frames
const BISH_H  = 30
const BISH_VG = 90        // biblical-tree 規格：每一任之間至少 90px

// Within one apostle's lane, multiple spines (e.g. 彼得 has 羅馬/亞歷山卓/安提阿)
// are laid out horizontally with this gap between them.
const SPINE_IN_LANE_GAP = 16

// Between two adjacent apostle lanes.
const APOSTLE_LANE_GAP = 24

const BRANCH_W   = 160
const BRANCH_H   = 28
const BRANCH_GAP = 12
const BRANCH_INDENT = 16

// ── Expand state ────────────────────────────────────────────
const expandedBranches = ref<Set<string>>(new Set())
function toggleBranch(branchId: string) {
  const s = expandedBranches.value
  if (s.has(branchId)) s.delete(branchId)
  else s.add(branchId)
  expandedBranches.value = new Set(s)
}

interface LNode {
  id: string
  kind: 'jesus' | 'apostle' | 'see' | 'bishop' | 'branch-see'
  label: string
  sub?: string
  x: number; y: number; w: number; h: number
  successionNum?: number | null
  branchId?: string
  bishopCount?: number
  spineColor?: string
  tooltip?: string
}
interface LPath { d: string; stroke?: string; dashed?: boolean; dashes?: string; width?: number; opacity?: number }
interface LGuide { x: number; y1: number; y2: number; color: string }

const cv = computed(() => {
  const nodes: LNode[] = []
  const paths: LPath[] = []
  const guides: LGuide[] = []
  let w = 0, h = 0

  if (!props.graph) return { nodes, paths, guides, w: 800, h: 600 }
  const g = props.graph

  // ── Pre-compute branch children & per-spine expanded depth ──
  const branchChildren = new Map<string, BranchIn[]>()
  for (const br of g.branches) {
    if (!branchChildren.has(br.parent_see_id)) branchChildren.set(br.parent_see_id, [])
    branchChildren.get(br.parent_see_id)!.push(br)
  }
  for (const arr of branchChildren.values()) {
    arr.sort((a, b) => (a.founded_year ?? 9999) - (b.founded_year ?? 9999))
  }
  function expandedDepth(seeId: string): number {
    let n = 0
    for (const k of branchChildren.get(seeId) ?? []) {
      if (expandedBranches.value.has(k.id)) {
        n = Math.max(n, 1 + expandedDepth(k.id))
      }
    }
    return n
  }
  const spineExpandedDepth = g.spines.map(sp => sp.see ? expandedDepth(sp.see.id) : 0)
  // Per-spine column width — bishop card + optional expanded branch tree
  const spineColWidth = g.spines.map((_, i) =>
    BISH_W + spineExpandedDepth[i] * (BRANCH_W + BRANCH_GAP) + (spineExpandedDepth[i] > 0 ? 16 : 0)
  )
  // One "spine slot" = see label area + bishop column. Used to size apostle lanes.
  const SPINE_SLOT_LEFT = SEE_LABEL_W + SEE_LABEL_GAP
  const spineSlotWidth = spineColWidth.map(w => SPINE_SLOT_LEFT + w)

  // ── Group spines by primary apostle ──
  // Each apostle has a "lane" — wide enough to fit its apostle card AND
  // all spines hanging below it (e.g. 彼得 has 3: 羅馬, 亞歷山卓, 安提阿).
  const apostleSpineIdx = new Map<string, number[]>()
  for (let si = 0; si < g.spines.length; si++) {
    const ap = g.spines[si].primaryApostleId
    if (!apostleSpineIdx.has(ap)) apostleSpineIdx.set(ap, [])
    apostleSpineIdx.get(ap)!.push(si)
  }

  // Per-apostle lane width — max of apostle card width and spine cluster width
  const laneInfo = g.apostles.map(a => {
    const spineIdxs = apostleSpineIdx.get(a.id) ?? []
    let cluster = 0
    for (const si of spineIdxs) cluster += spineSlotWidth[si]
    cluster += Math.max(0, spineIdxs.length - 1) * SPINE_IN_LANE_GAP
    return { spineIdxs, width: Math.max(APO_W, cluster) }
  })

  const apostleRowWidth =
    laneInfo.reduce((s, l) => s + l.width, 0) +
    Math.max(0, g.apostles.length - 1) * APOSTLE_LANE_GAP

  w = Math.max(apostleRowWidth + PAD * 2, JESUS_W + PAD * 2, 1200)

  // ── 1. Jesus card centered ──────────────────────────────
  const jesusY = PAD
  const jesusX = (w - JESUS_W) / 2
  nodes.push({
    id: 'jesus', kind: 'jesus', label: '耶穌基督', sub: 'Jesus Christ',
    x: jesusX, y: jesusY, w: JESUS_W, h: JESUS_H,
  })

  // ── 2. Apostle row — laid out as lanes, each lane wide enough for its spines ─
  const apostleY = jesusY + JESUS_H + 60
  const apostleRowStartX = (w - apostleRowWidth) / 2
  const apostleCX = new Map<string, number>()
  const spineX: number[] = new Array(g.spines.length).fill(0)   // bishop column X per spine
  {
    let cursor = apostleRowStartX
    for (let i = 0; i < g.apostles.length; i++) {
      const a = g.apostles[i]
      const lane = laneInfo[i]
      const laneCenterX = cursor + lane.width / 2
      const ax = laneCenterX - APO_W / 2
      nodes.push({
        id: 'ap_' + a.id, kind: 'apostle',
        label: simplifyApostleName(a.name_zh),
        sub: a.name_en,
        x: ax, y: apostleY, w: APO_W, h: APO_H,
        tooltip: `${a.name_zh}（${a.name_en}）`,
      })
      apostleCX.set(a.id, laneCenterX)

      // Distribute spines belonging to this apostle inside the lane, centered.
      if (lane.spineIdxs.length > 0) {
        let cluster = 0
        for (const si of lane.spineIdxs) cluster += spineSlotWidth[si]
        cluster += Math.max(0, lane.spineIdxs.length - 1) * SPINE_IN_LANE_GAP
        let spineCursor = laneCenterX - cluster / 2
        for (const si of lane.spineIdxs) {
          spineX[si] = spineCursor + SPINE_SLOT_LEFT   // bishop column X
          spineCursor += spineSlotWidth[si] + SPINE_IN_LANE_GAP
        }
      }

      cursor += lane.width + APOSTLE_LANE_GAP
    }
  }

  // ── 3. Jesus → apostles fan ────────────────────────────
  const fanY = jesusY + JESUS_H + 22
  paths.push({
    d: `M${jesusX + JESUS_W / 2},${jesusY + JESUS_H} L${jesusX + JESUS_W / 2},${fanY}`,
    stroke: '#a16207', width: 1.8,
  })
  if (g.apostles.length > 0) {
    const xs = g.apostles.map(a => apostleCX.get(a.id)!)
    const xMin = Math.min(...xs), xMax = Math.max(...xs)
    paths.push({ d: `M${xMin},${fanY} L${xMax},${fanY}`, stroke: '#a16207' })
    for (const x of xs) {
      paths.push({ d: `M${x},${fanY} L${x},${apostleY}`, stroke: '#a16207' })
    }
  }

  // ── 4. Spine columns — spineX[] already set above per apostle lane ─
  const spineHeaderY = apostleY + APO_H + 80
  const spineCenterX: Record<string, number> = {}
  const spineBishopCenterY = new Map<string, Map<string, number>>()
  let lastBishopY = spineHeaderY

  // Apostle name aliases — used to detect when spine #1 bishop = apostle himself.
  // If matched, skip rendering bishop #1 (the apostle card already represents him).
  const APOSTLE_ALIASES: Record<string, string[]> = {
    ap_peter:      ['彼得', '聖伯多祿', '伯多祿', '聖彼得'],
    ap_andrew:     ['安得烈', '聖安得烈', '安得肋', '聖安得肋'],
    ap_james_just: ['義人雅各', '義人雅各伯', '雅各', '雅各伯'],
    ap_thaddaeus:  ['達太', '聖達太', '猶達塔陡'],
    ap_thomas:     ['多馬', '聖多馬', '多默', '聖多默'],
  }
  function isApostleHimself(apostleId: string, bishopName: string): boolean {
    return (APOSTLE_ALIASES[apostleId] ?? []).some(a => bishopName.includes(a) || a.includes(bishopName))
  }

  for (let i = 0; i < g.spines.length; i++) {
    const sp = g.spines[i]
    if (!sp.see) continue

    const headerX = spineX[i]
    const headerCX = headerX + BISH_W / 2
    spineCenterX[sp.key] = headerCX

    // Per user spec: don't render see header above the column. The see name
    // sits as a small badge NEXT TO the first rendered bishop (= 第二代).
    // Bishops start from index 1 (skip #1) if first bishop = apostle himself.
    let startIdx = 0
    if (sp.bishops[0] && isApostleHimself(sp.primaryApostleId, sp.bishops[0].name_zh)) {
      startIdx = 1
    }

    const bishopMap = new Map<string, number>()
    let by = spineHeaderY    // bishops start at the top of "spine area" (no see header above)
    let firstBishopY: number | null = null
    for (let bi = startIdx; bi < sp.bishops.length; bi++) {
      const b = sp.bishops[bi]
      const churchTag = b.church && b.church !== '未分裂教會' ? `（${b.church}）` : ''
      bishopMap.set(b.id, by + BISH_H / 2)
      if (firstBishopY == null) firstBishopY = by
      nodes.push({
        id: 'bish_' + b.id, kind: 'bishop',
        label: b.name_zh,
        sub: b.start_year != null
          ? `${formatYear(b.start_year)}–${b.end_year != null ? formatYear(b.end_year) : ''}${churchTag}`
          : churchTag,
        x: headerX, y: by, w: BISH_W, h: BISH_H,
        successionNum: b.succession_number,
        spineColor: sp.color,
        tooltip: `${b.name_zh}\n任期：${formatYear(b.start_year)}–${formatYear(b.end_year)}${b.notes ? '\n' + b.notes : ''}`,
      })
      by += BISH_H + BISH_VG
    }
    spineBishopCenterY.set(sp.key, bishopMap)
    lastBishopY = Math.max(lastBishopY, by)

    // See-name label — PURE TEXT (no card frame, per user spec) sitting to the
    // LEFT of the first rendered bishop card, at the same row level.
    if (firstBishopY != null) {
      nodes.push({
        id: 'see_' + sp.see.id, kind: 'see',
        label: sp.see.see_zh,
        x: headerX - SEE_LABEL_GAP - SEE_LABEL_W,
        y: firstBishopY,
        w: SEE_LABEL_W, h: BISH_H,
        spineColor: sp.color,
        tooltip: `${sp.see.name_zh}（創立 ${sp.see.founded_year ?? '?'}）`,
      })
    }

    // Spine guide line — from apostle card bottom area to last bishop card
    if (sp.bishops.length > startIdx) {
      guides.push({
        x: headerCX, y1: apostleY + APO_H, y2: by - BISH_VG, color: sp.color,
      })
    }

    // ── side branches (collapsible) ──
    const branchColBaseX = headerX + BISH_W + 16
    const lastBranchYByDepth = new Map<number, number>()

    // Track Y position of every branch bishop card so sub-branches can attach to
    // the right successor row (per user spec: 分裂/獨立必須在那任主教 row 才分出).
    const branchBishopMap = new Map<string, number>()

    function renderBranches(parentSeeId: string, depth: number, parentBranchY?: number) {
      const kids = branchChildren.get(parentSeeId) ?? []
      for (const br of kids) {
        // Find the Y of the parent bishop during whose tenure this daughter was founded.
        // Parent bishop may live in either:
        //   - the spine bishopMap (if direct child of spine)
        //   - the branchBishopMap (if child of an expanded branch)
        let attachY: number
        if (br.parent_bishop_id && bishopMap.has(br.parent_bishop_id)) {
          attachY = bishopMap.get(br.parent_bishop_id)!
        } else if (br.parent_bishop_id && branchBishopMap.has(br.parent_bishop_id)) {
          attachY = branchBishopMap.get(br.parent_bishop_id)!
        } else if (depth === 0) {
          // No specific bishop matched → approx by founding year along this spine
          attachY = approxYByYear(sp, br.founded_year, bishopMap, spineHeaderY)
        } else {
          // Sub-branch with no resolvable parent bishop (parent branch likely collapsed)
          // → fall back to parent branch header Y
          attachY = parentBranchY ?? (spineHeaderY)
        }
        const bx = branchColBaseX + depth * (BRANCH_W + BRANCH_GAP)
        let by = Math.max(attachY - BRANCH_H / 2, spineHeaderY)
        const prevY = lastBranchYByDepth.get(depth)
        if (prevY != null) {
          const minY = prevY + BRANCH_H + 6
          if (by < minY) by = minY
        }
        lastBranchYByDepth.set(depth, by)

        nodes.push({
          id: 'br_' + br.id, kind: 'branch-see',
          label: br.see_zh + (br.church ? ` · ${br.church}` : ''),
          sub: br.founded_year != null ? `${formatYear(br.founded_year)} 創立` : '',
          x: bx, y: by, w: BRANCH_W, h: BRANCH_H,
          branchId: br.id, bishopCount: br.bishops.length,
          spineColor: sp.color,
          tooltip: `${br.name_zh}（${br.church}）\n創立：${formatYear(br.founded_year)}`,
        })

        // Connection line from attach point → branch
        // - is_split (同名 see, rival successors): 紅色鋸齒線（強斷裂感）
        // - 設立教座 (子座新名): 粗實線·spine 色
        const fromX = depth === 0 ? headerX + BISH_W : bx - BRANCH_GAP
        const toX = bx
        const toY = by + BRANCH_H / 2
        const midX = (fromX + toX) / 2
        const dPath = `M${fromX},${attachY} L${midX},${attachY} L${midX},${toY} L${toX},${toY}`
        if (br.is_split) {
          paths.push({ d: dPath, stroke: '#dc2626', dashes: '2,4,8,4', width: 2, opacity: 0.85 })
        } else {
          paths.push({ d: dPath, stroke: sp.color, width: 2, opacity: 0.85 })
        }

        if (expandedBranches.value.has(br.id)) {
          let cy = by + BRANCH_H + 4
          for (const bb of br.bishops) {
            const churchTag = bb.church && bb.church !== br.church ? `（${bb.church}）` : ''
            // Track this branch bishop's Y so deeper sub-branches can attach to the
            // specific bishop row when their parent_bishop_id resolves to here.
            branchBishopMap.set(bb.id, cy + (BISH_H - 2) / 2)
            nodes.push({
              id: 'bbish_' + bb.id, kind: 'bishop',
              label: bb.name_zh,
              sub: bb.start_year != null
                ? `${formatYear(bb.start_year)}–${bb.end_year != null ? formatYear(bb.end_year) : ''}${churchTag}`
                : churchTag,
              x: bx + BRANCH_INDENT, y: cy,
              w: BRANCH_W - BRANCH_INDENT, h: BISH_H - 2,
              successionNum: bb.succession_number,
              tooltip: `${bb.name_zh}\n任期：${formatYear(bb.start_year)}–${formatYear(bb.end_year)}`,
            })
            cy += BISH_H - 2 + BISH_VG
          }
          renderBranches(br.id, depth + 1, by + BRANCH_H / 2)
        }
      }
    }
    renderBranches(sp.see.id, 0)
  }

  // ── 5. Apostle → spine connections (primary + secondary) ──
  for (const sp of g.spines) {
    const headerCX = spineCenterX[sp.key]
    if (headerCX == null) continue

    // Primary apostle line (solid)
    const primaryX = apostleCX.get(sp.primaryApostleId)
    if (primaryX != null) {
      const fromY = apostleY + APO_H
      const toY = spineHeaderY
      const midY = (fromY + toY) / 2
      paths.push({
        d: `M${primaryX},${fromY} L${primaryX},${midY} L${headerCX},${midY} L${headerCX},${toY}`,
        stroke: sp.color, width: 1.8,
      })
    }
    // Secondary apostle line (dashed)
    if (sp.secondaryApostleId) {
      const secX = apostleCX.get(sp.secondaryApostleId)
      if (secX != null) {
        const fromY = apostleY + APO_H
        const toY = spineHeaderY
        const midY = (fromY + toY) / 2 + 12   // slight Y offset so it doesn't overlap primary
        paths.push({
          d: `M${secX},${fromY} L${secX},${midY} L${headerCX},${midY} L${headerCX},${toY}`,
          stroke: sp.color, width: 1.2, dashed: true, opacity: 0.65,
        })
      }
    }
  }

  // ── 6. Teaching lines (orange) — connect bishop nodes that are master-disciple pairs ──
  // Skip pairs where the institutional spine/branch chain already shows the relationship
  // (per user spec: 設立教座/職位關係 takes precedence over 教導關係).
  if (g.teachings && g.teachings.length > 0) {
    // Build lookup: bishopId → node
    const nodeByBishopId = new Map<string, LNode>()
    for (const n of nodes) {
      if (n.kind === 'bishop' && n.id.startsWith('bish_')) {
        nodeByBishopId.set(n.id.slice(5), n)
      } else if (n.kind === 'bishop' && n.id.startsWith('bbish_')) {
        nodeByBishopId.set(n.id.slice(6), n)
      }
    }

    // Determine which (teacher_bishop_id, student_bishop_id) pairs are already
    // covered by spine/branch institutional lines:
    // - same spine adjacent succession (#N → #N+1): always institutional, skip
    // - branch.parent_bishop_id chain (Wesley→Coke is in same Baltimore see, so spine covers)
    const institutionalPairs = new Set<string>()
    for (const sp of g.spines) {
      for (let i = 0; i < sp.bishops.length - 1; i++) {
        institutionalPairs.add(`${sp.bishops[i].id}|${sp.bishops[i + 1].id}`)
      }
    }

    for (const t of g.teachings) {
      if (!t.teacher_bishop_id || !t.student_bishop_id) continue
      const teacherNode = nodeByBishopId.get(t.teacher_bishop_id)
      const studentNode = nodeByBishopId.get(t.student_bishop_id)
      if (!teacherNode || !studentNode) continue
      // Skip if already institutional
      if (institutionalPairs.has(`${t.teacher_bishop_id}|${t.student_bishop_id}`)) continue

      // Draw orange curved line from teacher card to student card
      const x1 = teacherNode.x + teacherNode.w
      const y1 = teacherNode.y + teacherNode.h / 2
      const x2 = studentNode.x
      const y2 = studentNode.y + studentNode.h / 2
      const midX = (x1 + x2) / 2
      // Use a quadratic-ish path with horizontal mid for clarity
      paths.push({
        d: `M${x1},${y1} C${midX},${y1} ${midX},${y2} ${x2},${y2}`,
        stroke: '#ea580c',  // orange-600
        width: 1.5,
        opacity: 0.7,
      })
    }
  }

  // ── 7. Compute canvas height ──────────────────────────
  let maxY = 0
  for (const n of nodes) maxY = Math.max(maxY, n.y + n.h)
  h = maxY + PAD

  return { nodes, paths, guides, w, h }
})

// ── Helpers ─────────────────────────────────────────────
function formatYear(y: number | null | undefined): string {
  if (y == null) return ''
  return y < 0 ? `主前${Math.abs(y)}` : String(y)
}

function simplifyApostleName(name: string): string {
  // Trim "（...之子）" disambiguators for compact display in narrow apostle row
  // Keep "（主弟）" / "（奮銳黨）" etc. since they're identity, not disambig
  const m = name.match(/^([^（]+)（(.+)）$/)
  if (!m) return name
  const base = m[1], disamb = m[2]
  // For "James, son of Zebedee" / "James, son of Alphaeus" / etc., keep short suffix
  if (disamb.includes('之子')) {
    const short = disamb.replace('之子', '')
    return `${base}·${short}`
  }
  return name
}

function approxYByYear(sp: SpineIn, year: number | null, map: Map<string, number>, fallback: number): number {
  if (year == null) return fallback
  let best: { id: string; start: number } | null = null
  for (const b of sp.bishops) {
    if (b.start_year != null && b.start_year <= year) {
      if (!best || b.start_year > best.start) best = { id: b.id, start: b.start_year }
    }
  }
  if (best && map.has(best.id)) return map.get(best.id)!
  return fallback
}

function cardClass(n: LNode): string {
  const base = 'rounded-lg shadow-sm hover:shadow transition-shadow'
  if (n.kind === 'jesus') return `${base} bg-amber-50 border-2 border-amber-400`
  if (n.kind === 'apostle') return `${base} bg-white border border-slate-200`
  if (n.kind === 'see') return 'flex items-center justify-end pr-1'   // no frame — pure text label
  if (n.kind === 'bishop') return `${base} bg-white border border-slate-200`
  if (n.kind === 'branch-see') return `${base} bg-violet-50 border border-violet-300 cursor-pointer hover:bg-violet-100`
  return base
}

// ── Pan & Zoom ──────────────────────────────────────────────
const viewportRef = ref<HTMLDivElement | null>(null)
const panX = ref(0)
const panY = ref(0)
const zoom = ref(1)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, panX: 0, panY: 0 })

function onWheel(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey) {
    const delta = -e.deltaY * 0.001
    const newZoom = Math.max(0.2, Math.min(3, zoom.value + delta))
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
function zoomIn()  { zoom.value = Math.min(3, zoom.value + 0.1) }
function zoomOut() { zoom.value = Math.max(0.2, zoom.value - 0.1) }
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

// Default: 100% zoom + center horizontally on Jesus card. User can click 「定位全圖」for fit-to-screen.
function centerOnJesus() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const c = cv.value
  zoom.value = 1
  panX.value = (rect.width - c.w) / 2
  panY.value = 20
}
onMounted(() => { nextTick(centerOnJesus) })
watch(() => props.graph, () => { nextTick(centerOnJesus) })
</script>
