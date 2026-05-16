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

          <!-- spine guide lines -->
          <line v-for="(g, i) in cv.guides" :key="'g'+i"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- succession lines: vertical drops + horizontal bars -->
          <path v-for="(p, i) in cv.paths" :key="'p'+i"
                :d="p.d" :stroke="p.stroke || '#9ca3af'" stroke-width="1.5"
                fill="none" stroke-linecap="round"
                :stroke-dasharray="p.dashed ? '4,3' : ''" />
        </svg>

        <!-- Cards -->
        <div
          v-for="n in cv.nodes" :key="n.id"
          class="absolute rounded-md text-center transition-shadow"
          :class="cardClass(n)"
          :style="{
            left: n.x + 'px',
            top: n.y + 'px',
            width: n.w + 'px',
            height: n.h + 'px',
            lineHeight: '1.15',
          }"
          :title="n.tooltip || ''"
        >
          <div class="flex flex-col items-center justify-center w-full h-full px-1.5 py-1 leading-tight overflow-hidden">
            <div v-if="n.kind === 'jesus'"
                 class="text-[15px] font-semibold text-white tracking-wide">
              {{ n.label }}
            </div>
            <template v-else-if="n.kind === 'apostle'">
              <div class="text-[11px] font-semibold text-slate-800 truncate w-full">{{ n.label }}</div>
              <div class="text-[8.5px] text-slate-400 truncate w-full">{{ n.sub }}</div>
            </template>
            <template v-else-if="n.kind === 'see'">
              <div class="text-[12px] font-bold tracking-wide text-white truncate w-full">{{ n.label }}</div>
              <div class="text-[8.5px] text-white/80 truncate w-full">{{ n.sub }}</div>
            </template>
            <template v-else-if="n.kind === 'bishop'">
              <div class="flex items-center gap-1 w-full text-[10px]">
                <span v-if="n.successionNum != null"
                      class="text-[8.5px] text-slate-400 tabular-nums w-5 text-right">
                  {{ n.successionNum }}
                </span>
                <span class="font-medium text-slate-700 truncate flex-1 text-left">{{ n.label }}</span>
              </div>
              <div v-if="n.sub" class="text-[8px] text-slate-400 truncate w-full text-left pl-6">{{ n.sub }}</div>
            </template>
            <template v-else-if="n.kind === 'branch-see'">
              <button
                class="flex items-center gap-1 w-full text-[10px] cursor-default"
                @click.stop="toggleBranch(n.branchId!)"
              >
                <span class="text-[10px] text-slate-500">{{ expandedBranches.has(n.branchId!) ? '▾' : '▸' }}</span>
                <span class="font-semibold truncate flex-1 text-left text-slate-700">{{ n.label }}</span>
                <span class="text-[8px] text-slate-400 tabular-nums">{{ n.bishopCount }}</span>
              </button>
              <div v-if="n.sub" class="text-[8px] text-slate-400 truncate w-full text-left">{{ n.sub }}</div>
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
                  text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-1">
        <div class="font-semibold text-gray-700 mb-1">使徒統緒</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-amber-600" />耶穌</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-amber-50 border border-amber-300" />使徒（16）</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-red-600" />五大宗主教座</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-white border border-slate-300" />主教</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-violet-50 border border-violet-300" />旁支教座（▸/▾）</div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">滾輪：垂直　·　Shift＋滾輪：水平　·　Ctrl＋滾輪：縮放</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'EpiscopalSpineTree' })

interface ApostleIn {
  id: string
  name_zh: string
  name_en: string
  founderOfSeeKey?: string
  founderOfMany?: string[]
}
interface SeeIn {
  id: string
  see_zh: string
  name_zh: string
  name_en: string | null
  church: string
  tradition: string
  founded_year: number | null
}
interface BishopIn {
  id: string
  name_zh: string
  name_en: string | null
  succession_number: number | null
  start_year: number | null
  end_year: number | null
  appointed_by: string | null
  church: string | null
  status: string
  notes: string | null
}
interface SpineIn {
  key: string
  apostleId: string
  color: string
  see: SeeIn | null
  bishops: BishopIn[]
}
interface BranchIn {
  id: string
  see_zh: string
  name_zh: string
  name_en: string | null
  church: string
  tradition: string
  founded_year: number | null
  parent_see_id: string
  parent_spine_key: string
  parent_bishop_id: string | null
  bishops: BishopIn[]
}
interface GraphIn {
  jesus: { id: string; name_zh: string; name_en: string }
  apostles: ApostleIn[]
  spines: SpineIn[]
  branches: BranchIn[]
}

const props = defineProps<{ graph: GraphIn | null }>()

const ready = computed(() => !!props.graph)

// ── Layout constants ────────────────────────────────────────
const PAD     = 60
const JESUS_W = 130
const JESUS_H = 42

const APO_W   = 110
const APO_H   = 38
const APO_HG  = 8
const APO_PER_ROW = 8
const APO_VG  = 8

const SEE_W   = 220
const SEE_H   = 46

const BISH_W  = 220
const BISH_H  = 26
const BISH_VG = 4

const SPINE_HG = 30   // gap between adjacent spine columns
const SPINE_GAP_AFTER_BRANCHES = 18

const BRANCH_W   = 200
const BRANCH_H   = 32
const BRANCH_BISH_W = 200
const BRANCH_BISH_H = 22
const BRANCH_INDENT = 18

// ── Expand state ────────────────────────────────────────────
const expandedBranches = ref<Set<string>>(new Set())
function toggleBranch(branchId: string) {
  const s = expandedBranches.value
  if (s.has(branchId)) s.delete(branchId)
  else s.add(branchId)
  expandedBranches.value = new Set(s)
}

// ── Layout result types ─────────────────────────────────────
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
interface LPath { d: string; stroke?: string; dashed?: boolean }
interface LGuide { x: number; y1: number; y2: number; color: string }

// ── Main layout (computed) ───────────────────────────────────
const cv = computed(() => {
  const nodes: LNode[] = []
  const paths: LPath[] = []
  const guides: LGuide[] = []
  let w = 0, h = 0

  if (!props.graph) return { nodes, paths, guides, w: 800, h: 600 }
  const g = props.graph

  // ── 1. Jesus ───────────────────────────────────────────────
  // Center will be re-computed once we know the canvas width.
  // Place Jesus first with placeholder x, fix later.
  const jesusY = PAD
  const jesusNode: LNode = {
    id: 'jesus',
    kind: 'jesus',
    label: '耶穌基督',
    sub: 'Jesus Christ',
    x: 0, y: jesusY, w: JESUS_W, h: JESUS_H,
    tooltip: '耶穌基督',
  }
  nodes.push(jesusNode)

  // ── 2. Apostles row (2 rows of 8) ─────────────────────────
  const apostleRowY1 = jesusY + JESUS_H + 50
  const apostleRowY2 = apostleRowY1 + APO_H + APO_VG
  const apostleWidth = APO_PER_ROW * APO_W + (APO_PER_ROW - 1) * APO_HG

  const apostleByCenterX = new Map<string, number>()
  for (let i = 0; i < g.apostles.length; i++) {
    const a = g.apostles[i]
    const row = Math.floor(i / APO_PER_ROW)
    const col = i % APO_PER_ROW
    const apY = row === 0 ? apostleRowY1 : apostleRowY2
    const apX = col * (APO_W + APO_HG)  // relative; will offset later
    nodes.push({
      id: 'ap_' + a.id,
      kind: 'apostle',
      label: a.name_zh,
      sub: a.name_en,
      x: apX, y: apY, w: APO_W, h: APO_H,
      tooltip: `${a.name_zh}（${a.name_en}）`,
    })
    apostleByCenterX.set(a.id, apX + APO_W / 2)
  }

  // ── 3. 5 Spine columns ────────────────────────────────────
  // Each spine is a column (see header + vertical bishop list).
  // Branch sees are inserted AT the row of the bishop they descend from
  // (when that branch is expanded). We render branches as a vertical
  // column to the right of their spine, indented under that bishop.

  const spineHeaderY = apostleRowY2 + APO_H + 60
  const spineCount = g.spines.length

  // Compute per-spine width including expanded branches.
  // We do a pass to figure out branches per spine that are expanded
  // and how much horizontal space they need.

  // Group branches by parent_spine_key
  const branchesBySpine = new Map<string, BranchIn[]>()
  for (const sp of g.spines) branchesBySpine.set(sp.key, [])
  for (const br of g.branches) {
    branchesBySpine.get(br.parent_spine_key)?.push(br)
  }
  // For each spine, we need to render branches in a "tree" — branches can
  // themselves have branches. We use parent_see_id to nest.
  // Build branch-children map by parent_see_id
  const branchChildren = new Map<string, BranchIn[]>()
  for (const br of g.branches) {
    if (!branchChildren.has(br.parent_see_id)) branchChildren.set(br.parent_see_id, [])
    branchChildren.get(br.parent_see_id)!.push(br)
  }
  for (const arr of branchChildren.values()) {
    arr.sort((a, b) => (a.founded_year ?? 9999) - (b.founded_year ?? 9999))
  }

  // Width per spine = SEE_W + (depth of expanded branches) * BRANCH_W
  // For a first version we treat all expanded branches at the same column
  // and stack them vertically — a branch column is BRANCH_W wide.
  // We compute how many "branch columns" each spine needs.
  function expandedDescendantCount(seeId: string): number {
    let n = 0
    const kids = branchChildren.get(seeId) ?? []
    for (const k of kids) {
      if (expandedBranches.value.has(k.id)) {
        n = Math.max(n, 1 + expandedDescendantCount(k.id))
      }
    }
    return n
  }

  const spineExpandedDepth = g.spines.map(sp =>
    sp.see ? expandedDescendantCount(sp.see.id) : 0
  )
  // Per-spine widths
  const spineWidths = g.spines.map((_, i) =>
    SEE_W + spineExpandedDepth[i] * (BRANCH_W + 12) + (spineExpandedDepth[i] > 0 ? SPINE_GAP_AFTER_BRANCHES : 0)
  )

  // X position of each spine column (left edge of see header)
  const spineX: number[] = []
  let cursor = PAD
  for (let i = 0; i < spineCount; i++) {
    spineX.push(cursor)
    cursor += spineWidths[i] + SPINE_HG
  }
  const spineColumnsTotalWidth = cursor - SPINE_HG  // last spine right edge

  // ── compute total canvas width ───────────────────────────
  const canvasMinW = Math.max(
    spineColumnsTotalWidth + PAD,
    apostleWidth + PAD * 2,
    JESUS_W + PAD * 2,
    900,
  )
  w = canvasMinW

  // Center jesus
  jesusNode.x = (w - JESUS_W) / 2

  // Center apostle row
  const apostleStartX = (w - apostleWidth) / 2
  for (const n of nodes) {
    if (n.kind === 'apostle') {
      n.x = apostleStartX + n.x
    }
  }
  // Update apostleByCenterX absolute X
  for (let i = 0; i < g.apostles.length; i++) {
    const a = g.apostles[i]
    const col = i % APO_PER_ROW
    apostleByCenterX.set(a.id, apostleStartX + col * (APO_W + APO_HG) + APO_W / 2)
  }

  // ── 4. Place spines & their bishops ───────────────────────
  const spineSeeCenterX: Record<string, number> = {}
  const spineBishopRowY = new Map<string, Map<string, number>>()  // spineKey -> bishopId -> Y center

  for (let i = 0; i < g.spines.length; i++) {
    const sp = g.spines[i]
    if (!sp.see) continue

    const headerX = spineX[i]
    const headerCX = headerX + SEE_W / 2
    spineSeeCenterX[sp.key] = headerCX

    nodes.push({
      id: 'see_' + sp.see.id,
      kind: 'see',
      label: sp.see.see_zh,
      sub: sp.see.name_zh,
      x: headerX, y: spineHeaderY, w: SEE_W, h: SEE_H,
      spineColor: sp.color,
      tooltip: `${sp.see.name_zh}（創立：${sp.see.founded_year ?? '?'}）`,
    })

    // bishop list
    const bishopMap = new Map<string, number>()
    let by = spineHeaderY + SEE_H + 22
    for (const b of sp.bishops) {
      const bishopY = by
      bishopMap.set(b.id, bishopY + BISH_H / 2)
      const churchTag = b.church && b.church !== '未分裂教會' ? `（${b.church}）` : ''
      nodes.push({
        id: 'bish_' + b.id,
        kind: 'bishop',
        label: b.name_zh,
        sub: b.start_year != null
          ? `${formatYear(b.start_year)}–${b.end_year != null ? formatYear(b.end_year) : ''}${churchTag}`
          : churchTag,
        x: headerX, y: bishopY, w: BISH_W, h: BISH_H,
        successionNum: b.succession_number,
        spineColor: sp.color,
        tooltip: `${b.name_zh}${churchTag}\n任期：${formatYear(b.start_year)}–${formatYear(b.end_year)}\n${b.notes ?? ''}`,
      })
      by += BISH_H + BISH_VG
    }
    spineBishopRowY.set(sp.key, bishopMap)

    // ── side branches: render as collapsible column to the right ──
    // We layout branches as nested columns within this spine.
    // Branch column index 0 = directly attached to spine, index 1 = attached to a branch, etc.
    // Each branch column shares the same spine X-area to the right of headerX + SEE_W

    const branchColBaseX = headerX + SEE_W + 16

    // Track Y of last placed branch in each (depth) column to avoid overlap
    const lastBranchYByDepth = new Map<number, number>()

    // Render top-level branches (parent = spine see)
    function renderBranchesOf(parentSeeId: string, depth: number) {
      const kids = branchChildren.get(parentSeeId) ?? []
      for (const br of kids) {
        // Y position of this branch header = Y of the parent bishop in the parent spine see, OR of parent branch header
        let attachY: number
        if (depth === 0 && br.parent_bishop_id && bishopMap.has(br.parent_bishop_id)) {
          attachY = bishopMap.get(br.parent_bishop_id)!
        } else {
          // No specific bishop — attach at the bishop nearest to founded_year
          const apxY = approxBishopYByYear(sp, br.founded_year, bishopMap, spineHeaderY + SEE_H + 22)
          attachY = apxY
        }
        const bx = branchColBaseX + depth * (BRANCH_W + 12)
        let by = Math.max(attachY - BRANCH_H / 2, spineHeaderY + SEE_H + 22)

        // De-overlap: if previous branch in same depth column overlaps, push this one down
        const prevY = lastBranchYByDepth.get(depth)
        if (prevY != null) {
          const minY = prevY + BRANCH_H + 6
          if (by < minY) by = minY
        }
        lastBranchYByDepth.set(depth, by)

        nodes.push({
          id: 'br_' + br.id,
          kind: 'branch-see',
          label: br.see_zh + (br.church ? ` · ${br.church}` : ''),
          sub: br.founded_year != null ? `${formatYear(br.founded_year)} 創立` : '',
          x: bx, y: by, w: BRANCH_W, h: BRANCH_H,
          branchId: br.id,
          bishopCount: br.bishops.length,
          tooltip: `${br.name_zh}（${br.church}）\n創立：${formatYear(br.founded_year)}`,
        })

        // succession line: from attach point (bishop on spine OR parent branch) → branch header
        if (depth === 0) {
          const fromX = headerX + SEE_W
          const fromY = attachY
          const toX = bx
          const toY = by + BRANCH_H / 2
          paths.push({
            d: `M${fromX},${fromY} L${(fromX + toX) / 2},${fromY} L${(fromX + toX) / 2},${toY} L${toX},${toY}`,
            stroke: sp.color,
            dashed: true,
          })
        } else {
          // attached to parent branch header
          const fromX = bx - 12 - BRANCH_W + BRANCH_W
          const fromY = attachY  // approximate — same Y as parent
          const toX = bx
          const toY = by + BRANCH_H / 2
          paths.push({
            d: `M${fromX},${fromY} L${(fromX + toX) / 2},${fromY} L${(fromX + toX) / 2},${toY} L${toX},${toY}`,
            stroke: sp.color,
            dashed: true,
          })
        }

        if (expandedBranches.value.has(br.id)) {
          // Render bishops of this branch as a vertical list directly below its header
          let cy = by + BRANCH_H + 6
          for (const bb of br.bishops) {
            const churchTag = bb.church && bb.church !== br.church ? `（${bb.church}）` : ''
            nodes.push({
              id: 'bbish_' + bb.id,
              kind: 'bishop',
              label: bb.name_zh,
              sub: bb.start_year != null
                ? `${formatYear(bb.start_year)}–${bb.end_year != null ? formatYear(bb.end_year) : ''}${churchTag}`
                : churchTag,
              x: bx + BRANCH_INDENT,
              y: cy,
              w: BRANCH_BISH_W - BRANCH_INDENT,
              h: BRANCH_BISH_H,
              successionNum: bb.succession_number,
              tooltip: `${bb.name_zh}\n任期：${formatYear(bb.start_year)}–${formatYear(bb.end_year)}`,
            })
            cy += BRANCH_BISH_H + BISH_VG
          }
          // recurse into sub-branches (rendered to the right)
          renderBranchesOf(br.id, depth + 1)
        }
      }
    }
    renderBranchesOf(sp.see.id, 0)

    // ── line: apostle → see header ────────────────────────
    const apX = apostleByCenterX.get(sp.apostleId)
    if (apX != null) {
      const fromY = (g.apostles.findIndex(a => a.id === sp.apostleId) < APO_PER_ROW
                    ? apostleRowY1 + APO_H
                    : apostleRowY2 + APO_H)
      const toY = spineHeaderY
      const toX = headerCX
      const midY = (fromY + toY) / 2
      paths.push({
        d: `M${apX},${fromY} L${apX},${midY} L${toX},${midY} L${toX},${toY}`,
        stroke: sp.color,
      })
    }

    // ── spine guide line down through bishops ─────────────
    if (sp.bishops.length > 0) {
      const lastY = by - BISH_VG
      guides.push({
        x: headerCX,
        y1: spineHeaderY + SEE_H,
        y2: lastY,
        color: sp.color,
      })
    }
  }

  // ── 5. Jesus → apostles top connection (single fan) ───
  const jesusBottomY = jesusY + JESUS_H
  const apostleTopY = apostleRowY1
  const fanY = jesusBottomY + 18
  // Trunk down to fan line
  paths.push({
    d: `M${jesusNode.x + JESUS_W / 2},${jesusBottomY} L${jesusNode.x + JESUS_W / 2},${fanY}`,
    stroke: '#a16207',
  })
  // Horizontal bar connecting all apostle X-centers in row 1
  if (g.apostles.length > 0) {
    const xs1 = g.apostles.slice(0, APO_PER_ROW).map(a => apostleByCenterX.get(a.id)!).filter(x => x != null)
    if (xs1.length > 0) {
      const xMin = Math.min(...xs1)
      const xMax = Math.max(...xs1)
      paths.push({
        d: `M${xMin},${fanY} L${xMax},${fanY}`,
        stroke: '#a16207',
      })
      // drops to each apostle
      for (const x of xs1) {
        paths.push({
          d: `M${x},${fanY} L${x},${apostleTopY}`,
          stroke: '#a16207',
        })
      }
    }
    // Row 2: drop from row 1 mid to row 2 cards
    const xs2 = g.apostles.slice(APO_PER_ROW).map(a => apostleByCenterX.get(a.id)!).filter(x => x != null)
    if (xs2.length > 0) {
      const fanY2 = apostleRowY1 + APO_H + APO_VG / 2
      const xMin = Math.min(...xs2)
      const xMax = Math.max(...xs2)
      // Drop from jesus trunk down through row 1 area into row 2 fan
      paths.push({
        d: `M${jesusNode.x + JESUS_W / 2},${apostleRowY1 - 4} L${jesusNode.x + JESUS_W / 2},${fanY2} L${xMin},${fanY2}`,
        stroke: '#a16207',
        dashed: true,
      })
      paths.push({
        d: `M${xMin},${fanY2} L${xMax},${fanY2}`,
        stroke: '#a16207',
      })
      for (const x of xs2) {
        paths.push({
          d: `M${x},${fanY2} L${x},${apostleRowY2}`,
          stroke: '#a16207',
        })
      }
    }
  }

  // ── 6. Bishop succession lines (vertical along the spine) ──
  for (const sp of g.spines) {
    const map = spineBishopRowY.get(sp.key)
    if (!map || sp.bishops.length === 0) continue
    // Spine guide already drawn; we add small connecting drops between consecutive bishop cards
    let prevY: number | null = null
    for (const b of sp.bishops) {
      const y = map.get(b.id)!
      if (prevY != null) {
        const cx = spineSeeCenterX[sp.key]
        // already covered by guide, no need
      }
      prevY = y
    }
    // First bishop ← see header
    const firstY = map.get(sp.bishops[0].id)
    if (firstY != null) {
      paths.push({
        d: `M${spineSeeCenterX[sp.key]},${spineHeaderY + SEE_H} L${spineSeeCenterX[sp.key]},${firstY}`,
        stroke: sp.color,
      })
    }
  }

  // ── 7. Compute canvas height ────────────────────────────
  let maxY = 0
  for (const n of nodes) maxY = Math.max(maxY, n.y + n.h)
  h = maxY + PAD

  return { nodes, paths, guides, w, h }
})

// helpers
function formatYear(y: number | null | undefined): string {
  if (y == null) return ''
  return y < 0 ? `主前${Math.abs(y)}` : String(y)
}

function approxBishopYByYear(sp: SpineIn, year: number | null, map: Map<string, number>, fallback: number): number {
  if (year == null) return fallback
  // find bishop with start_year closest (and ≤ year)
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
  if (n.kind === 'jesus') return 'bg-amber-600 text-white shadow-lg ring-1 ring-amber-700'
  if (n.kind === 'apostle') return 'bg-amber-50 border border-amber-300 hover:bg-amber-100'
  if (n.kind === 'see') {
    const colorBg: Record<string, string> = {
      '#dc2626': 'bg-red-600 ring-1 ring-red-700',
      '#2563eb': 'bg-blue-600 ring-1 ring-blue-700',
      '#d97706': 'bg-amber-600 ring-1 ring-amber-700',
      '#0891b2': 'bg-cyan-600 ring-1 ring-cyan-700',
      '#16a34a': 'bg-green-600 ring-1 ring-green-700',
    }
    return (colorBg[n.spineColor ?? ''] ?? 'bg-slate-600') + ' shadow-md'
  }
  if (n.kind === 'bishop') return 'bg-white border border-slate-200 hover:border-slate-400 hover:shadow-sm'
  if (n.kind === 'branch-see') return 'bg-violet-50 border border-violet-300 hover:bg-violet-100 cursor-pointer'
  return ''
}

// ── Pan & Zoom ──────────────────────────────────────────────
const viewportRef = ref<HTMLDivElement | null>(null)
const panX = ref(0)
const panY = ref(0)
const zoom = ref(0.85)
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

onMounted(() => {
  // Auto-fit on first load
  nextTick(() => fitAll())
})
watch(() => props.graph, () => {
  nextTick(() => fitAll())
})
</script>
