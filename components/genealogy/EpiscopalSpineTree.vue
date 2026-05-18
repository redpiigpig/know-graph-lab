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

          <!-- spine 主線（vivid，明顯可見的主教傳承線）— width varies pre/post 宗主教座 establishment -->
          <line v-for="(g, i) in cv.guides" :key="'g'+i"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" :stroke-width="g.width ?? 6" :opacity="g.opacity ?? 0.55" stroke-linecap="round" />

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
              <button
                class="w-full text-center cursor-default"
                :class="n.apostleBranchCount ? 'hover:bg-amber-50/40 rounded transition' : ''"
                @click.stop="n.apostleBranchCount ? toggleApostle(n.apostleId!) : null"
              >
                <div class="flex items-center justify-center gap-1">
                  <span v-if="n.apostleBranchCount" class="text-[10px] text-amber-600 shrink-0">
                    {{ isApostleExpanded(n.apostleId!) ? '▾' : '▸' }}
                  </span>
                  <span class="text-[11.5px] font-semibold text-slate-800 truncate">{{ n.label }}</span>
                  <span v-if="n.apostleBranchCount"
                        class="text-[8.5px] text-amber-600 tabular-nums shrink-0">{{ n.apostleBranchCount }}</span>
                </div>
                <div class="text-[8.5px] text-slate-400 truncate mt-0.5">{{ n.sub }}</div>
              </button>
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
                <button v-if="n.menuBranchCount"
                        class="text-[9px] px-1 rounded bg-violet-100 text-violet-700 hover:bg-violet-200 cursor-default shrink-0"
                        @click.stop="toggleBishopMenu(n.id)">
                  +{{ n.menuBranchCount }} 被立
                </button>
              </div>
              <div v-if="n.sub"
                   class="text-[8px] text-slate-400 truncate w-full text-left"
                   :class="n.successionNum != null ? 'pl-6' : ''">
                {{ n.sub }}
              </div>
              <!-- Popup menu for multi-consecration -->
              <div v-if="openMenuBishopId === n.id && n.menuBranches"
                   class="absolute left-full top-0 ml-2 bg-white border border-violet-300 rounded-lg shadow-lg p-1 z-50 min-w-[200px] max-h-[300px] overflow-y-auto"
                   @click.stop>
                <div class="text-[9px] text-slate-500 px-2 py-1 border-b border-gray-100">
                  {{ n.label }} 任內按立 {{ n.menuBranches.length }} 個教座
                </div>
                <button v-for="mb in n.menuBranches" :key="mb.id"
                        class="block w-full text-left px-2 py-1 text-[10px] hover:bg-violet-50 rounded cursor-default"
                        @click.stop="revealMenuBranch(mb.id)">
                  <div class="flex items-center gap-1.5">
                    <span class="inline-block w-1 h-3 rounded-full"
                          :style="{ background: mb.is_split ? '#dc2626' : '#7c3aed' }" />
                    <span class="font-medium text-slate-800 flex-1 truncate">{{ mb.label }}</span>
                    <span class="text-[9px] text-slate-400 tabular-nums shrink-0">{{ mb.year }}</span>
                  </div>
                </button>
              </div>
            </template>

            <template v-else-if="n.kind === 'branch-see'">
              <button
                class="flex items-center gap-1 w-full text-[10.5px] cursor-default"
                @click.stop="toggleBranch(n.branchId!)"
              >
                <span class="text-[10px] text-violet-500 w-3 shrink-0">{{ isBranchExpanded(n.branchId!) ? '▾' : '▸' }}</span>
                <span class="font-semibold truncate flex-1 text-left text-slate-800">{{ n.label }}</span>
                <span class="text-[8px] text-slate-400 tabular-nums shrink-0">{{ n.bishopCount }}</span>
              </button>
              <div v-if="n.sub" class="text-[8px] text-slate-400 truncate w-full text-left pl-3.5">{{ n.sub }}</div>
            </template>
          </div>
        </div>
      </div>

      <!-- Search bar -->
      <div class="absolute top-3 left-3 z-40 pointer-events-auto" style="width: 320px;">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜尋主教或教座（中／英／教座名）"
            class="w-full px-3 py-2 text-[12px] bg-white/95 border border-gray-200 rounded-lg shadow-sm
                   focus:outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-200"
            @focus="searchOpen = true"
            @input="searchOpen = true"
            @keydown.escape="searchOpen = false"
          />
          <button v-if="searchQuery"
                  class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700 text-[14px] cursor-default"
                  @click.stop="searchQuery = ''; searchOpen = false">×</button>
        </div>
        <div v-if="searchOpen && searchResults.length > 0"
             class="mt-1 bg-white/98 border border-gray-200 rounded-lg shadow-lg max-h-[420px] overflow-y-auto">
          <button v-for="r in searchResults" :key="r.id"
                  class="block w-full text-left px-3 py-1.5 text-[11px] hover:bg-violet-50 border-b border-gray-50 cursor-default"
                  @click.stop="jumpTo(r)">
            <div class="flex items-center gap-2">
              <span class="inline-block w-[3px] h-[14px] rounded-full"
                    :style="{ background: r.spineColor || '#cbd5e1' }" />
              <span class="font-medium text-slate-800 flex-1 truncate">{{ r.label }}</span>
              <span class="text-[9px] text-slate-400 shrink-0">{{ r.kindLabel }}</span>
            </div>
            <div v-if="r.context" class="text-[9px] text-slate-400 truncate ml-3 mt-0.5">{{ r.context }}</div>
          </button>
        </div>
        <div v-else-if="searchOpen && searchQuery && searchResults.length === 0"
             class="mt-1 bg-white/95 border border-gray-200 rounded-lg shadow-sm px-3 py-2 text-[11px] text-gray-400">
          沒有結果
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
            <span class="inline-flex w-5 items-center gap-px">
              <span class="inline-block h-[2px] w-2 bg-slate-300 opacity-60 rounded-full" />
              <span class="inline-block h-[5px] w-2 bg-slate-300 opacity-60 rounded-full" />
            </span>
            spine 細→粗：建立宗主教座（451/410/484）
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
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 h-[1.5px] bg-amber-700 rounded-full" />
            使徒立座（琥珀）— 點使徒卡片展開
          </div>
        </div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">▸/▾ 旁支收／展　·　使徒卡片可點　·　Ctrl＋滾輪：縮放</div>
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
  patriarchateYear?: number   // 宗主教座建立年份；此前 spine 線細，此後 spine 線粗
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
interface ApostolicBranchIn extends BranchIn {
  parent_apostle_id: string | null   // 直接掛在使徒底下時設定（depth-0）；子座為 null
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
  apostolicBranches?: ApostolicBranchIn[]
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
// 預設所有分支都收起來；使用者點 ▸ 才一個個展開。
const collapsedBranches = ref<Set<string>>(new Set())
function isBranchExpanded(branchId: string): boolean {
  return !collapsedBranches.value.has(branchId)
}
function toggleBranch(branchId: string) {
  const s = collapsedBranches.value
  if (s.has(branchId)) s.delete(branchId)
  else s.add(branchId)
  collapsedBranches.value = new Set(s)
}
// 預設所有 apostle 也收起來 — 預設視圖只看 7 大宗主教
const collapsedApostles = ref<Set<string>>(new Set())
function isApostleExpanded(apostleId: string): boolean {
  return !collapsedApostles.value.has(apostleId)
}
function toggleApostle(apostleId: string) {
  const s = collapsedApostles.value
  if (s.has(apostleId)) s.delete(apostleId)
  else s.add(apostleId)
  collapsedApostles.value = new Set(s)
}
// 多教座按立選單：哪個主教的「+N 被立座」popup 目前開著、哪些被點過顯示
const openMenuBishopId = ref<string | null>(null)
const revealedFromMenu = ref<Set<string>>(new Set())
function toggleBishopMenu(bishopId: string) {
  openMenuBishopId.value = openMenuBishopId.value === bishopId ? null : bishopId
}
function revealMenuBranch(branchId: string) {
  const s = new Set(revealedFromMenu.value)
  s.add(branchId)
  revealedFromMenu.value = s
  // Also expand the branch so its bishops show
  const cs = new Set(collapsedBranches.value)
  cs.delete(branchId)
  collapsedBranches.value = cs
  openMenuBishopId.value = null
}
watch(() => props.graph, (g) => {
  if (!g) return
  if (g.branches) collapsedBranches.value = new Set(g.branches.map((b: any) => b.id))
  if (g.apostolicBranches) {
    for (const b of g.apostolicBranches) collapsedBranches.value.add(b.id)
  }
  // 所有 apostle 預設收起
  if (g.apostles) collapsedApostles.value = new Set(g.apostles.map((a: any) => a.id))
}, { immediate: true })

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
  apostleId?: string         // for apostle node — for click handler
  apostleBranchCount?: number   // for apostle node — # depth-0 apostolic branches under this apostle
  bishopId?: string          // for bishop node — raw bishop id (lookup menuCountByBishop)
  menuBranchCount?: number   // for bishop node — # daughter sees collapsed into menu
  menuBranches?: Array<{ id: string; label: string; year: number | null; is_split: boolean }>   // for popup menu
}
interface LPath { d: string; stroke?: string; dashed?: boolean; dashes?: string; width?: number; opacity?: number }
interface LGuide { x: number; y1: number; y2: number; color: string; width?: number }

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

  // ── 多教座按立選單：全圖一次性計算 branchesByParentBishop ──
  // 同一位主教按立 >= 2 個子座時，預設摺成「+N 被立座」選單，使用者從選單點才 reveal
  const branchesByParentBishop = new Map<string, BranchIn[]>()
  for (const br of g.branches) {
    if (!br.parent_bishop_id) continue
    if (!branchesByParentBishop.has(br.parent_bishop_id)) branchesByParentBishop.set(br.parent_bishop_id, [])
    branchesByParentBishop.get(br.parent_bishop_id)!.push(br)
  }
  function isBranchInMenu(br: BranchIn): boolean {
    const sibs = branchesByParentBishop.get(br.parent_bishop_id ?? '') ?? []
    return sibs.length >= 2 && !revealedFromMenu.value.has(br.id)
  }
  // Per bishop: how many hidden-in-menu daughter sees
  const menuCountByBishop = new Map<string, number>()
  for (const [bid, sibs] of branchesByParentBishop) {
    if (sibs.length < 2) continue
    const hidden = sibs.filter(s => !revealedFromMenu.value.has(s.id))
    if (hidden.length > 0) menuCountByBishop.set(bid, hidden.length)
  }
  function expandedDepth(seeId: string): number {
    let n = 0
    for (const k of branchChildren.get(seeId) ?? []) {
      if (isBranchExpanded(k.id)) {
        n = Math.max(n, 1 + expandedDepth(k.id))
      }
    }
    return n
  }
  const spineExpandedDepth = g.spines.map(sp => sp.see ? expandedDepth(sp.see.id) : 0)
  // 每個 spine 只要有「任何 branch（可展開／已展開都算）」就要保留至少 1 個 branch slot
  // —— 否則收起的 branch header 會 overlay 進下一個 spine 的領域
  function hasAnyBranch(seeId: string): boolean {
    const kids = branchChildren.get(seeId) ?? []
    if (kids.length > 0) return true
    return false
  }
  // Per-spine column width — bishop card + branch tree（至少預留 1 slot 給 collapsed headers）
  const spineColWidth = g.spines.map((sp, i) => {
    const minBranchDepth = sp.see && hasAnyBranch(sp.see.id) ? 1 : 0
    const depth = Math.max(spineExpandedDepth[i], minBranchDepth)
    return BISH_W + depth * (BRANCH_W + BRANCH_GAP) + (depth > 0 ? 16 : 0)
  })
  // 一個 spine slot = 左邊 see label 區 + bishop column
  const SPINE_SLOT_LEFT = SEE_LABEL_W + SEE_LABEL_GAP
  const spineSlotWidth = spineColWidth.map(w => SPINE_SLOT_LEFT + w)

  // ── 7 大宗主教座按順序「平均分配」橫排 ──
  // 每個 spine 都有獨立 slot；不再把多個 spine 塞進同一個 apostle lane
  const SPINE_BETWEEN_GAP = 36
  const spineRowWidth =
    spineSlotWidth.reduce((s, w) => s + w, 0) +
    Math.max(0, g.spines.length - 1) * SPINE_BETWEEN_GAP

  // 16 使徒也按順序平均分配
  const apostleRowWidth =
    g.apostles.length * APO_W + Math.max(0, g.apostles.length - 1) * APO_HG

  const contentWidth = Math.max(spineRowWidth, apostleRowWidth)
  w = Math.max(contentWidth + PAD * 2, JESUS_W + PAD * 2, 1200)

  // ── 1. Jesus card centered ──────────────────────────────
  const jesusY = PAD
  const jesusX = (w - JESUS_W) / 2
  nodes.push({
    id: 'jesus', kind: 'jesus', label: '耶穌基督', sub: 'Jesus Christ',
    x: jesusX, y: jesusY, w: JESUS_W, h: JESUS_H,
  })

  // ── Build apostolic-branches map (per-apostle, depth=0 only) ──
  const apostolicByApostle = new Map<string, ApostolicBranchIn[]>()
  for (const b of (g.apostolicBranches ?? [])) {
    if (b.parent_apostle_id) {
      if (!apostolicByApostle.has(b.parent_apostle_id)) apostolicByApostle.set(b.parent_apostle_id, [])
      apostolicByApostle.get(b.parent_apostle_id)!.push(b)
    }
  }
  // 排序：照 founded_year 由舊到新
  for (const arr of apostolicByApostle.values()) {
    arr.sort((a, b) => (a.founded_year ?? 9999) - (b.founded_year ?? 9999))
  }

  // ── 2. Apostle row — 16 位平均分配 ──
  const apostleY = jesusY + JESUS_H + 60
  const apostleRowStartX = (w - apostleRowWidth) / 2
  const apostleCX = new Map<string, number>()
  for (let i = 0; i < g.apostles.length; i++) {
    const a = g.apostles[i]
    const ax = apostleRowStartX + i * (APO_W + APO_HG)
    const cx = ax + APO_W / 2
    const branchCount = apostolicByApostle.get(a.id)?.length ?? 0
    nodes.push({
      id: 'ap_' + a.id, kind: 'apostle',
      label: simplifyApostleName(a.name_zh),
      sub: a.name_en,
      x: ax, y: apostleY, w: APO_W, h: APO_H,
      tooltip: `${a.name_zh}（${a.name_en}）`,
      apostleId: a.id,
      apostleBranchCount: branchCount || undefined,
    })
    apostleCX.set(a.id, cx)
  }

  // ── Spine row — 7 個平均分配，bishop column X 寫進 spineX[] ──
  const spineX: number[] = new Array(g.spines.length).fill(0)
  {
    const spineRowStartX = (w - spineRowWidth) / 2
    let cursor = spineRowStartX
    for (let i = 0; i < g.spines.length; i++) {
      spineX[i] = cursor + SPINE_SLOT_LEFT   // bishop column X
      cursor += spineSlotWidth[i] + SPINE_BETWEEN_GAP
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

  // ── 3.5. Apostolic branches — 使徒展開後才畫，掛在 apostle card 底下 ──
  // 預設所有 apostles 收起來；當某個 apostle 被展開，它的 depth-0 apostolic branches
  // 顯示為小 branch-see header（橘色，使徒色系），疊在 apostle card 下方
  const APO_BRANCH_W = 130
  const APO_BRANCH_H = 24
  const APO_BRANCH_GAP = 4
  const apostolicBranchY = apostleY + APO_H + 16   // start just below apostle row
  const apostolicBranchBishopMap = new Map<string, number>()   // apostolic branch bishop ID → Y
  for (const a of g.apostles) {
    if (!isApostleExpanded(a.id)) continue
    const branchesForApostle = apostolicByApostle.get(a.id) ?? []
    if (branchesForApostle.length === 0) continue
    const apX = apostleCX.get(a.id)!
    let cy = apostolicBranchY
    for (const ab of branchesForApostle) {
      const bx = apX - APO_BRANCH_W / 2
      nodes.push({
        id: 'apbr_' + ab.id, kind: 'branch-see',
        label: ab.see_zh + (ab.church ? ` · ${ab.church}` : ''),
        sub: ab.founded_year != null ? `${formatYear(ab.founded_year)} ${ab.is_split ? '分裂' : '使徒立座'}` : '',
        x: bx, y: cy, w: APO_BRANCH_W, h: APO_BRANCH_H,
        branchId: ab.id, bishopCount: ab.bishops.length,
        spineColor: '#a16207',   // amber — apostolic line color
        tooltip: `${ab.name_zh}（${ab.church}）\n${a.name_zh} 使徒立座`,
      })
      // Founding line from apostle card to branch header (amber)
      const apostleBottomY = apostleY + APO_H
      const branchMidY = cy + APO_BRANCH_H / 2
      paths.push({
        d: `M${apX},${apostleBottomY} L${apX},${branchMidY}`,
        stroke: '#a16207', width: 1.5,
      })
      cy += APO_BRANCH_H + APO_BRANCH_GAP

      // If apostolic branch is expanded → render its bishops below the header
      if (isBranchExpanded(ab.id)) {
        for (const bb of ab.bishops) {
          apostolicBranchBishopMap.set(bb.id, cy + (BISH_H - 2) / 2)
          nodes.push({
            id: 'apbish_' + bb.id, kind: 'bishop',
            label: bb.name_zh,
            sub: bb.start_year != null
              ? `${formatYear(bb.start_year)}–${bb.end_year != null ? formatYear(bb.end_year) : ''}`
              : '',
            x: apX - APO_BRANCH_W / 2 + 6,
            y: cy,
            w: APO_BRANCH_W - 12, h: BISH_H - 2,
            successionNum: bb.succession_number,
            spineColor: '#a16207',
            tooltip: `${bb.name_zh}\n任期：${formatYear(bb.start_year)}–${formatYear(bb.end_year)}`,
          })
          cy += BISH_H - 2 + 8
        }
        cy += 8   // gap before next apostolic branch
      }
    }
  }

  // ── 4. Spine columns — spineX[] already set above per apostle lane ─
  const spineHeaderY = apostleY + APO_H + 80
  const spineCenterX: Record<string, number> = {}
  const spineBishopCenterY = new Map<string, Map<string, number>>()
  let lastBishopY = spineHeaderY

  for (let i = 0; i < g.spines.length; i++) {
    const sp = g.spines[i]
    if (!sp.see) continue

    const headerX = spineX[i]
    const headerCX = headerX + BISH_W / 2
    spineCenterX[sp.key] = headerCX

    // Render all bishops starting from #1 (don't skip apostle-himself; per user spec)
    const startIdx = 0

    const bishopMap = new Map<string, number>()
    let by = spineHeaderY    // bishops start at the top of "spine area" (no see header above)
    let firstBishopY: number | null = null
    for (let bi = startIdx; bi < sp.bishops.length; bi++) {
      const b = sp.bishops[bi]
      bishopMap.set(b.id, by + BISH_H / 2)
      if (firstBishopY == null) firstBishopY = by
      const menuCount = menuCountByBishop.get(b.id) ?? 0
      const menuBranches = menuCount > 0
        ? (branchesByParentBishop.get(b.id) ?? [])
            .filter(br => !revealedFromMenu.value.has(br.id))
            .map(br => ({ id: br.id, label: br.see_zh + (br.church ? ' · ' + br.church : ''), year: br.founded_year, is_split: br.is_split }))
        : undefined
      nodes.push({
        id: 'bish_' + b.id, kind: 'bishop',
        label: b.name_zh,
        sub: b.start_year != null
          ? `${formatYear(b.start_year)}–${b.end_year != null ? formatYear(b.end_year) : ''}`
          : '',
        x: headerX, y: by, w: BISH_W, h: BISH_H,
        successionNum: b.succession_number,
        spineColor: sp.color,
        bishopId: b.id,
        menuBranchCount: menuCount || undefined,
        menuBranches,
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

    // Spine guide line — from apostle card bottom area to last bishop card.
    // 若有 patriarchateYear 則切兩段：建立宗主教座前線細（width 4），後線粗（width 10）。
    if (sp.bishops.length > startIdx) {
      const guideTop = apostleY + APO_H
      const guideBottom = by - BISH_VG
      if (sp.patriarchateYear != null) {
        const splitY = approxYByYear(sp, sp.patriarchateYear, bishopMap, guideTop)
        // 細線段：apostle 底 → 宗主教座建立年
        if (splitY > guideTop) {
          guides.push({ x: headerCX, y1: guideTop, y2: splitY, color: sp.color, width: 4 })
        }
        // 粗線段：宗主教座建立年 → 最後一任主教
        if (guideBottom > splitY) {
          guides.push({ x: headerCX, y1: splitY, y2: guideBottom, color: sp.color, width: 10 })
        }
      } else {
        guides.push({ x: headerCX, y1: guideTop, y2: guideBottom, color: sp.color })
      }
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
        // Skip if branch is in a menu and user hasn't revealed it yet
        if (isBranchInMenu(br)) continue
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

        if (isBranchExpanded(br.id)) {
          let cy = by + BRANCH_H + 4
          for (const bb of br.bishops) {
            // Track this branch bishop's Y so deeper sub-branches can attach to the
            // specific bishop row when their parent_bishop_id resolves to here.
            branchBishopMap.set(bb.id, cy + (BISH_H - 2) / 2)
            nodes.push({
              id: 'bbish_' + bb.id, kind: 'bishop',
              label: bb.name_zh,
              // 任期年份；不再附 church 後綴
              sub: bb.start_year != null
                ? `${formatYear(bb.start_year)}–${bb.end_year != null ? formatYear(bb.end_year) : ''}`
                : '',
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
  // 線錯開：每個 spine 用不同的水平 midY，避免多個 fan 在同一個 Y 重疊
  // 7 spine × 8px stagger = 跨 56px 範圍，剛好分散在 fromY/toY 之間
  const FAN_STAGGER = 8
  const fromY = apostleY + APO_H
  const toY = spineHeaderY
  const baseMidY = fromY + 18   // 緊貼 apostle 下方，留出 stagger 空間到 toY
  for (let i = 0; i < g.spines.length; i++) {
    const sp = g.spines[i]
    const headerCX = spineCenterX[sp.key]
    if (headerCX == null) continue

    const midY = baseMidY + i * FAN_STAGGER   // 每個 spine 獨立水平層

    // Primary apostle line (solid)
    const primaryX = apostleCX.get(sp.primaryApostleId)
    if (primaryX != null) {
      paths.push({
        d: `M${primaryX},${fromY} L${primaryX},${midY} L${headerCX},${midY} L${headerCX},${toY}`,
        stroke: sp.color, width: 1.8,
      })
    }
    // Secondary apostle line (dashed) — 用相同 midY 但偏移 4px
    if (sp.secondaryApostleId) {
      const secX = apostleCX.get(sp.secondaryApostleId)
      if (secX != null) {
        const sMidY = midY + 4
        paths.push({
          d: `M${secX},${fromY} L${secX},${sMidY} L${headerCX},${sMidY} L${headerCX},${toY}`,
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
  const highlight = highlightedNodeId.value === n.id ? ' ring-2 ring-violet-400 ring-offset-1' : ''
  if (n.kind === 'jesus') return `${base} bg-amber-50 border-2 border-amber-400${highlight}`
  if (n.kind === 'apostle') return `${base} bg-white border border-slate-200${highlight}`
  if (n.kind === 'see') return 'flex items-center justify-end pr-1'
  if (n.kind === 'bishop') return `${base} bg-white border border-slate-200${highlight}`
  if (n.kind === 'branch-see') return `${base} bg-violet-50 border border-violet-300 cursor-pointer hover:bg-violet-100${highlight}`
  return base
}

// ── Search ──────────────────────────────────────────────────
interface SearchResult {
  id: string
  label: string
  kindLabel: string
  context: string
  spineColor?: string
  // Anchor info — for jump-to
  spineKey?: string         // which spine (for spine bishops)
  branchId?: string         // which branch (for branch bishops or branch-see)
  bishopId?: string         // raw bishop id (for nested lookup)
  apostleId?: string        // apostolic-branch host
}
const searchQuery = ref('')
const searchOpen = ref(false)
const highlightedNodeId = ref<string | null>(null)

const searchIndex = computed<SearchResult[]>(() => {
  const out: SearchResult[] = []
  const g = props.graph
  if (!g) return out

  // Apostles
  for (const a of g.apostles) {
    out.push({
      id: 'ap_' + a.id, label: a.name_zh, kindLabel: '使徒',
      context: a.name_en, apostleId: a.id,
    })
  }
  // Spine sees + bishops
  for (const sp of g.spines) {
    if (sp.see) {
      out.push({
        id: 'see_' + sp.see.id, label: sp.see.see_zh, kindLabel: '宗主教座',
        context: `${sp.see.name_zh} · ${sp.see.church}`,
        spineColor: sp.color, spineKey: sp.key,
      })
    }
    for (const b of sp.bishops) {
      out.push({
        id: 'bish_' + b.id,
        label: b.name_zh,
        kindLabel: (sp.see?.see_zh ?? '') + (b.succession_number != null ? ` #${b.succession_number}` : ''),
        context: [b.name_en, b.start_year != null ? `${formatYear(b.start_year)}–${b.end_year != null ? formatYear(b.end_year) : ''}` : null].filter(Boolean).join(' · '),
        spineColor: sp.color, spineKey: sp.key, bishopId: b.id,
      })
    }
  }
  // Branch sees + bishops
  for (const br of g.branches) {
    out.push({
      id: 'br_' + br.id, label: `${br.see_zh}・${br.church}`, kindLabel: '旁支教座',
      context: br.founded_year != null ? `${formatYear(br.founded_year)} 創立` : '',
      branchId: br.id,
    })
    for (const bb of br.bishops) {
      out.push({
        id: 'bbish_' + bb.id,
        label: bb.name_zh,
        kindLabel: br.see_zh + (bb.succession_number != null ? ` #${bb.succession_number}` : ''),
        context: [bb.name_en, bb.start_year != null ? `${formatYear(bb.start_year)}–${bb.end_year != null ? formatYear(bb.end_year) : ''}` : null].filter(Boolean).join(' · '),
        branchId: br.id, bishopId: bb.id,
      })
    }
  }
  // Apostolic branches + their bishops
  for (const ab of (g.apostolicBranches ?? [])) {
    out.push({
      id: 'apbr_' + ab.id, label: `${ab.see_zh}・${ab.church}`, kindLabel: '使徒立座',
      context: ab.founded_year != null ? `${formatYear(ab.founded_year)} 使徒立座` : '',
      spineColor: '#a16207', branchId: ab.id, apostleId: ab.parent_apostle_id ?? undefined,
    })
    for (const bb of ab.bishops) {
      out.push({
        id: 'apbish_' + bb.id,
        label: bb.name_zh,
        kindLabel: ab.see_zh + (bb.succession_number != null ? ` #${bb.succession_number}` : ''),
        context: bb.name_en ?? '',
        branchId: ab.id, bishopId: bb.id,
      })
    }
  }
  return out
})

const searchResults = computed<SearchResult[]>(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (q.length < 1) return []
  const out: SearchResult[] = []
  for (const r of searchIndex.value) {
    if (
      r.label.toLowerCase().includes(q) ||
      (r.context && r.context.toLowerCase().includes(q)) ||
      (r.kindLabel && r.kindLabel.toLowerCase().includes(q))
    ) {
      out.push(r)
      if (out.length >= 100) break
    }
  }
  return out
})

function jumpTo(r: SearchResult) {
  // Auto-expand path to reveal target node
  if (r.apostleId) collapsedApostles.value = (() => { const s = new Set(collapsedApostles.value); s.delete(r.apostleId!); return s })()
  if (r.branchId) collapsedBranches.value = (() => { const s = new Set(collapsedBranches.value); s.delete(r.branchId!); return s })()

  // Wait for re-render, then find the rendered node and pan to it
  nextTick(() => {
    const node = cv.value.nodes.find(n => n.id === r.id)
    if (!node) {
      // Try fallbacks: if bishop is in a collapsed branch, find branch header
      const fallbackIds = [
        r.branchId ? 'br_' + r.branchId : null,
        r.branchId ? 'apbr_' + r.branchId : null,
        r.apostleId ? 'ap_' + r.apostleId : null,
      ].filter(Boolean) as string[]
      for (const fid of fallbackIds) {
        const fn = cv.value.nodes.find(n => n.id === fid)
        if (fn) { panToNode(fn); searchOpen.value = false; return }
      }
      searchOpen.value = false
      return
    }
    panToNode(node)
    searchOpen.value = false
  })
}

function panToNode(n: LNode) {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  // Center the node in the viewport
  const z = zoom.value
  const cx = n.x + n.w / 2
  const cy = n.y + n.h / 2
  panX.value = rect.width / 2 - cx * z
  panY.value = rect.height / 2 - cy * z
  highlightedNodeId.value = n.id
  setTimeout(() => { if (highlightedNodeId.value === n.id) highlightedNodeId.value = null }, 3000)
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

// Default: fit canvas WIDTH into viewport (canvas is ~3000px wide for 7 spines, viewport ~1800px).
// 縱向不 fit 因為 rome 有 261 任主教 ≈ 30000px 高，fit-to-height 會把 zoom 縮到 3%。
function centerOnJesus() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const c = cv.value
  const widthFit = (rect.width - 40) / c.w
  zoom.value = Math.min(widthFit, 1)
  panX.value = (rect.width - c.w * zoom.value) / 2
  panY.value = 20
}
onMounted(() => { nextTick(centerOnJesus) })
watch(() => props.graph, () => { nextTick(centerOnJesus) })
</script>
