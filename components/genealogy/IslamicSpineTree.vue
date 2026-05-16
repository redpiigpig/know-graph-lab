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
    <div v-if="!ready" class="flex flex-col items-center justify-center h-full gap-2 pointer-events-none">
      <span class="text-gray-400 text-sm">
        {{ props.nodes.length === 0 ? '資料載入中…' : '計算族譜圖…' }}
      </span>
      <span v-if="props.nodes.length > 0 && !hasSpine" class="text-xs text-red-400">
        找不到阿丹→穆罕默德 路徑（共 {{ props.nodes.length }} 人）
      </span>
    </div>

    <template v-else>
      <div
        class="absolute top-0 left-0 origin-top-left"
        :style="{
          width: cv!.w + 'px',
          height: cv!.h + 'px',
          transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
          willChange: 'transform',
        }"
      >
        <svg class="absolute inset-0 pointer-events-none overflow-visible"
             :width="cv!.w" :height="cv!.h">

          <line v-for="(g, i) in cv!.trunkGuides" :key="'tg'+i"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- Marriage lines — red horizontal between spouses -->
          <line v-for="m in cv!.marriages" :key="m.id"
                :x1="m.x1" :y1="m.y" :x2="m.x2" :y2="m.y"
                stroke="#dc2626" stroke-width="2" stroke-linecap="round" />

          <!-- Vertical drops (parent → child / drop from marriage midpoint) -->
          <line v-for="(d, i) in cv!.drops" :key="'d'+i"
                :x1="d.x" :y1="d.y1" :x2="d.x" :y2="d.y2"
                :stroke="d.stroke || '#9ca3af'" stroke-width="1.5"
                stroke-linecap="round" />

          <!-- Horizontal T-bars -->
          <line v-for="(b, i) in cv!.hbars" :key="'b'+i"
                :x1="b.x1" :y1="b.y" :x2="b.x2" :y2="b.y"
                :stroke="b.stroke || '#9ca3af'" stroke-width="1.5"
                stroke-linecap="round" />
        </svg>

        <div
          v-for="n in cv!.nodes" :key="n.id"
          class="node-card absolute"
          :class="cardClass(n)"
          :style="cardStyle(n)"
          @click.stop="onCardClick(n)"
        >
          <div v-if="n.isSpine" class="absolute left-0 top-2 bottom-2 w-[3px] bg-emerald-400 rounded-full" />
          <div class="px-2.5 py-1.5" :class="n.isSpine ? 'pl-4' : ''">
            <div class="text-[9px] font-medium leading-none mb-0.5 tracking-wide opacity-60 min-h-[9px] text-slate-500">
              {{ n.genLabel || ' ' }}
            </div>
            <div class="text-[12px] font-semibold leading-snug text-slate-800" :title="n.rawName">
              {{ n.displayName }}
            </div>
            <div v-if="n.kunya"
                 class="text-[9px] leading-tight text-slate-400 mt-0.5 max-w-[110px] truncate"
                 :title="n.kunya">
              · {{ n.kunya }}
            </div>
            <div v-else-if="n.disambig"
                 class="text-[9px] leading-tight text-slate-400 mt-0.5 max-w-[110px] truncate"
                 :title="n.disambig">
              （{{ n.disambig }}）
            </div>
          </div>
          <!-- Subtree toggle (▼/▲) for cards with descendants -->
          <button
            v-if="n.hasSubtree"
            class="absolute -bottom-2 left-1/2 -translate-x-1/2 z-10
                   px-1.5 h-4 min-w-[20px] rounded-full bg-white text-[10px] leading-none
                   border border-emerald-300 text-emerald-700 hover:bg-emerald-50 shadow-sm
                   cursor-default flex items-center justify-center gap-0.5 tabular-nums"
            :title="n.subtreeExpanded ? '收起子孫' : `展開 ${n.subtreeSize} 名子孫`"
            @click.stop="toggleExpand(n.personId)"
          >
            <span>{{ n.subtreeExpanded ? '▲' : '▼' }}</span>
            <span v-if="!n.subtreeExpanded" class="text-[9px] opacity-70">{{ n.subtreeSize }}</span>
          </button>
        </div>
      </div>

      <!-- View switch widget — viewport-fixed top-left (always reachable) -->
      <div
        class="absolute top-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-1 shadow-sm flex flex-row items-center gap-0.5 pointer-events-auto"
      >
        <span class="text-[10px] text-gray-400 px-1.5 select-none leading-tight border-r border-gray-200 mr-0.5">視角</span>
        <button
          v-for="t in viewOptions"
          :key="t.value"
          class="text-[11px] px-2 py-1 rounded-md font-medium transition cursor-default"
          :class="props.view === t.value
            ? `bg-gray-100 ${t.activeColor}`
            : 'text-gray-500 hover:text-gray-700'"
          :title="t.tooltip"
          @click.stop="emit('update:view', t.value)"
        >{{ t.label }}</button>
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
        <button class="px-1 py-1.5 bg-white/90 border border-emerald-300 rounded-lg text-emerald-700
                       text-[10px] font-medium shadow-sm hover:bg-emerald-50 transition leading-tight
                       text-center cursor-default"
                @click.stop="fitSpine">定位<br>主幹</button>
        <button class="px-1 py-1.5 bg-white/90 border border-amber-300 rounded-lg text-amber-700
                       text-[10px] font-medium shadow-sm hover:bg-amber-50 transition leading-tight
                       text-center cursor-default"
                title="一鍵展開以色列先知鏈：易司哈格→葉爾孤白→穆薩/達烏德/蘇萊曼/麥爾彥/爾撒"
                @click.stop="expandProphets">先知<br>鏈</button>
      </div>

      <!-- Legend -->
      <div class="absolute bottom-3 left-3 z-40 bg-white/95 border border-gray-200 rounded-lg p-2 text-[10px] text-gray-600 shadow-sm pointer-events-none space-y-0.5">
        <div class="flex items-center gap-1.5"><span class="w-3 h-[3px] bg-emerald-400 rounded-full" />穆聖直系（阿丹→穆罕默德）</div>
        <div class="flex items-center gap-1.5 pt-1 mt-1 border-t border-gray-100"><span class="inline-block w-3 h-3 border border-gray-400 bg-white rounded" />古蘭明文</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-emerald-300 bg-emerald-50 rounded" />順尼派傳承</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-rose-300 bg-rose-50 rounded" />十二伊瑪目派</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-purple-300 bg-purple-50 rounded" />伊斯瑪儀派</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-orange-300 bg-orange-50 rounded" />栽德派</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-teal-300 bg-teal-50 rounded" />蘇菲傳承</div>
        <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 border border-gray-300 bg-gray-50 rounded" />史傳（不確定）</div>
        <div class="flex items-center gap-1.5 pt-1 mt-1 border-t border-gray-100"><span class="w-3 h-[2px] bg-rose-600 rounded-full" />婚姻</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-[2px] bg-gray-400 rounded-full" />親子（從婚姻中點下降）</div>
        <div class="text-gray-400 mt-1 pt-1 border-t border-gray-100">滾輪：移動　·　Ctrl+滾輪：縮放　·　拖曳：平移</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'IslamicSpineTree' })

type View = 'quranic' | 'sunni' | 'shia_twelver' | 'shia_ismaili' | 'shia_zaidi'

const props = defineProps<{
  nodes: any[]
  edges: any[]
  view?: View
}>()
const emit = defineEmits<{
  selectPerson:  [id: string]
  'update:view': [v: View]
}>()

const viewOptions: Array<{ value: View; label: string; activeColor: string; tooltip: string }> = [
  { value: 'quranic',      label: '古蘭',     activeColor: 'text-gray-900',     tooltip: '只顯示古蘭明文人物' },
  { value: 'sunni',        label: '順尼',     activeColor: 'text-emerald-700',  tooltip: '順尼派視角（預設）' },
  { value: 'shia_twelver', label: '十二派',   activeColor: 'text-rose-700',     tooltip: '十二伊瑪目派' },
  { value: 'shia_ismaili', label: '伊斯瑪儀', activeColor: 'text-purple-700',   tooltip: '伊斯瑪儀派' },
  { value: 'shia_zaidi',   label: '栽德',     activeColor: 'text-orange-700',   tooltip: '栽德派' },
]

// ── Layout constants ──
const NW       = 130    // node width
const NH       = 56     // node height
const HG       = 18     // sibling horizontal gap
const WIFE_HG  = 50     // wife horizontal gap
const SLOT_K   = NW + WIFE_HG
const VG       = 80     // row vertical gap
const RH       = NH + VG
const PAD      = 60
const SPINE_X  = 1200   // spine center X

const baseName = (s: string) => s.split('（')[0].trim()
const shortName = (s: string) => { const b = baseName(s); return b.length <= 8 ? b : b.slice(0, 7) + '…' }
const disambigOf = (s: string) => { const m = s.match(/^[^（]+（(.+)）$/); return m ? m[1] : '' }
const rowY = (gen: number) => PAD + (gen - 1) * RH

// ── Graph maps ──
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

// ── Spine path: Adam → Muhammad via BFS waypoints ──
function bfsPath(src: string, dst: string, ch: Map<string, string[]>): string[] {
  if (src === dst) return [src]
  const queue: string[][] = [[src]]
  const vis = new Set<string>()
  while (queue.length) {
    const path = queue.shift()!
    const cur = path[path.length - 1]
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

const SPINE_WAYPOINTS = ['阿丹', '努哈', '易卜拉欣', '伊斯瑪儀', '阿德南', '穆罕默德']
const spinePath = computed(() => spineFromWaypoints(SPINE_WAYPOINTS, childrenOf.value))
const hasSpine = computed(() => spinePath.value.length > 0)
const spineSet = computed(() => new Set(spinePath.value))

// ── Node interface ──
interface LNode {
  id: string
  personId: string
  rawName: string
  displayName: string
  kunya: string
  disambig: string
  genLabel: string
  generation: number
  gender: string
  tradition: string
  x: number; y: number; w: number; h: number
  isSpine: boolean
  hasSubtree?: boolean    // true → render ▼/▲ collapse button
  subtreeSize?: number    // total hidden descendants (only when collapsed)
  subtreeExpanded?: boolean
}
interface VDrop { x: number; y1: number; y2: number; stroke?: string }
interface HBar  { x1: number; x2: number; y: number; stroke?: string }
interface MLine { id: string; x1: number; x2: number; y: number }
interface TrunkGuide { x: number; y1: number; y2: number; color: string }

interface LayoutResult {
  nodes: LNode[]
  drops: VDrop[]
  hbars: HBar[]
  marriages: MLine[]
  rootCX: number
  maxX: number
  maxY: number
}

// ── Subtree expansion state ──
// Keyed by personId — when set, that person's full descendants are rendered.
// 預設一律收摺；點 ▼ 才展開。
const expandedClans = ref<Set<string>>(new Set())
function toggleExpand(personId: string) {
  const s = new Set(expandedClans.value)
  if (s.has(personId)) s.delete(personId)
  else s.add(personId)
  expandedClans.value = s
}

// 一鍵展開以色列先知鏈：易司哈格→葉爾孤白→[利未/猶大 兩線]→穆薩/哈倫 + Davidic kings/達烏德/蘇萊曼/麥爾彥/爾撒
function expandProphets() {
  const PROPHET_CHAIN = [
    '易司哈格', '葉爾孤白',
    // Moses line
    '利未', '卡哈特', '阿米蘭（穆薩之父）',
    '哈倫',  // 為了顯示 Aaron→Zechariah 線（21 代略過）
    // David line
    '猶大', '法勒斯', '希斯崙', '蘭', '阿米拿達', '拿順',
    '撒門', '波阿斯', '俄備得', '耶西', '達烏德', '蘇萊曼',
    // Davidic kings of Judah
    '羅波安', '亞比雅', '亞撒', '約沙法', '約蘭', '烏西雅',
    '約坦', '亞哈斯', '希西家', '瑪拿西', '亞們', '約西亞',
    '耶哥尼雅', '阿米蘭（馬利亞之父）', '麥爾彥',
    '宰凱里雅',  // 顯示 葉哈雅
  ]
  const byName = personByName.value
  const s = new Set(expandedClans.value)
  for (const name of PROPHET_CHAIN) {
    const node = byName.get(name)
    if (node) s.add(node.id)
  }
  expandedClans.value = s
}
// 觸發 subtree ▼ 的最小子孫數 — 1+ 就有 toggle，避免單獨葉節點長尾出現
const SUBTREE_MIN = 1

// ── Main layout ──
const cv = computed(() => {
  if (!hasSpine.value) return null

  const ch = childrenOf.value
  const sp = spousesOf.value
  const pa = parentsOf.value
  const pMap = personById.value
  const spineList = spinePath.value
  const spineMembership = spineSet.value
  const expandedSet = expandedClans.value

  // 計算每個人的子孫數（剔除 spine + 已 visited，遞迴限深 25）
  const descCountCache = new Map<string, number>()
  function countDescendants(id: string, vis: Set<string> = new Set()): number {
    if (vis.has(id)) return 0
    vis.add(id)
    if (descCountCache.has(id)) return descCountCache.get(id)!
    let n = 0
    for (const c of ch.get(id) ?? []) {
      if (spineMembership.has(c)) continue
      n += 1 + countDescendants(c, vis)
    }
    descCountCache.set(id, n)
    return n
  }

  const nodes: LNode[] = []
  const drops: VDrop[] = []
  const hbars: HBar[] = []
  const marriages: MLine[] = []
  const trunkGuides: TrunkGuide[] = []
  const placedPersonIds = new Set<string>()
  const positionByPerson = new Map<string, { x: number; y: number }>()
  const spineRowOf = new Map<string, number>()

  function makeLNode(personId: string, x: number, y: number, isSpine = false): LNode | null {
    if (placedPersonIds.has(personId)) return null
    const p = pMap.get(personId)
    if (!p) return null
    placedPersonIds.add(personId)
    const raw = p.data.name as string
    let descCount = isSpine ? 0 : countDescendants(personId)
    const isExpanded = expandedSet.has(personId)
    let hasSubtree = !isSpine && descCount >= SUBTREE_MIN
    // 妻子的 children 若被丈夫 children 涵蓋 → 不顯示 ▼（族譜慣例「子嗣放男方」）
    // e.g., 麗百加(利百加, ▼37) 跟 易司哈格(以撒, ▼38) 雙顯示重複，保留 易司哈格 一邊
    const isFemale = p.data.gender === '女' || p.data.gender === 'female'
    if (hasSubtree && isFemale) {
      const myKids = ch.get(personId) ?? []
      for (const spId of sp.get(personId) ?? []) {
        const spP = pMap.get(spId)
        if (!spP) continue
        const spIsMale = spP.data.gender === '男' || spP.data.gender === 'male'
        if (!spIsMale) continue
        const spKids = ch.get(spId) ?? []
        if (myKids.length > 0 && myKids.every(k => spKids.includes(k))) {
          hasSubtree = false
          descCount = 0
          break
        }
      }
    }
    const ln: LNode = {
      id: `n:${personId}`,
      personId,
      rawName:    raw,
      displayName: shortName(raw),
      kunya:      (p.data.kunya as string) || '',
      disambig:   disambigOf(raw),
      genLabel:   p.data.generation || '',
      generation: p.data.generationNum ?? 0,
      gender:     p.data.gender,
      tradition:  p.data.tradition || 'sunni',
      x, y, w: NW, h: NH,
      isSpine,
      hasSubtree,
      subtreeSize: hasSubtree ? descCount : undefined,
      subtreeExpanded: isExpanded,
    }
    positionByPerson.set(personId, { x, y })
    return ln
  }

  // Recursive subtree layout for a NON-SPINE person and their descendants.
  // Uses DB gen for Y; lays children left-to-right; root centered over them.
  // Marriage line + drop-from-midpoint rule per biblical spec.
  //
  // 收摺規則：rootId 在 expandedSet 才遞迴子孫；否則只放 root + 配偶。
  // 由 makeLNode 自動標 hasSubtree+subtreeSize，模板 render ▼/▲ 鈕。
  function layoutSubtree(rootId: string, leftX: number, vis: Set<string>, minGen: number, depth: number = 0): LayoutResult {
    const empty = (): LayoutResult => ({ nodes: [], drops: [], hbars: [], marriages: [], rootCX: leftX + NW / 2, maxX: leftX + NW, maxY: 0 })
    if (vis.has(rootId)) return empty()
    const p = pMap.get(rootId)
    if (!p) return empty()
    if (depth > 30) return empty()  // safety
    vis.add(rootId)

    const dbGen = p.data.generationNum || 1
    const gen = Math.max(dbGen, minGen)
    const myY = rowY(gen)

    // Wives (non-spine, not in vis, not already placed elsewhere)
    const wiveIds = (sp.get(rootId) ?? []).filter(w =>
      !spineMembership.has(w) && !vis.has(w) && pMap.has(w) && !placedPersonIds.has(w)
    )
    const wivesReach = wiveIds.length * SLOT_K

    // Children — skip those on spine (already drawn), skip vis duplicates
    const kids = (ch.get(rootId) ?? []).filter(c =>
      !spineMembership.has(c) && !vis.has(c) && pMap.has(c)
    )

    const myNodes: LNode[] = []
    const myDrops: VDrop[] = []
    const myHbars: HBar[]  = []
    const myMarriages: MLine[] = []

    // 收摺：root 未展開且有子孫 → 只放 root+配偶，不遞迴 kids
    const collapsed = kids.length > 0 && !expandedSet.has(rootId)

    if (kids.length === 0 || collapsed) {
      const rootX = leftX + wivesReach
      const rootCX = rootX + NW / 2
      const node = makeLNode(rootId, rootX, myY, false)
      if (node) myNodes.push(node)
      // place wives + marriage lines
      const wResult = placeWivesHere(rootId, rootCX, myY, wiveIds)
      myNodes.push(...wResult.nodes)
      myMarriages.push(...wResult.marriages)
      const maxXLeaf = Math.max(rootX + NW, wResult.maxX)
      return {
        nodes: myNodes, drops: [], hbars: [], marriages: myMarriages,
        rootCX, maxX: maxXLeaf, maxY: myY + NH,
      }
    }

    // Recurse children left-to-right
    let cursorX = leftX + wivesReach
    const childResults: LayoutResult[] = []
    let maxY = myY + NH
    for (const k of kids) {
      const r = layoutSubtree(k, cursorX, vis, gen + 1, depth + 1)
      if (r.nodes.length === 0) continue
      childResults.push(r)
      cursorX = r.maxX + HG
      maxY = Math.max(maxY, r.maxY)
    }
    if (childResults.length === 0) {
      // all kids skipped (visited / off-tree) → treat as leaf
      const rootX = leftX + wivesReach
      const rootCX = rootX + NW / 2
      const node = makeLNode(rootId, rootX, myY, false)
      if (node) myNodes.push(node)
      const wResult = placeWivesHere(rootId, rootCX, myY, wiveIds)
      myNodes.push(...wResult.nodes)
      myMarriages.push(...wResult.marriages)
      return {
        nodes: myNodes, drops: [], hbars: [], marriages: myMarriages,
        rootCX, maxX: Math.max(rootX + NW, wResult.maxX), maxY: myY + NH,
      }
    }

    const childCXs = childResults.map(r => r.rootCX)
    const cmin = Math.min(...childCXs)
    const cmax = Math.max(...childCXs)
    const rootCX = (cmin + cmax) / 2
    const rootX = rootCX - NW / 2
    const node = makeLNode(rootId, rootX, myY, false)
    if (node) myNodes.push(node)

    // wives
    const wResult = placeWivesHere(rootId, rootCX, myY, wiveIds)
    myNodes.push(...wResult.nodes)
    myMarriages.push(...wResult.marriages)

    // drop from marriage midpoint (or root bottom) to children
    const firstChildY = childResults[0].nodes[0]?.y ?? myY + RH
    const marY = myY + NH / 2
    const hasWives = wiveIds.length > 0
    const dropStartX = hasWives ? rootCX - SLOT_K / 2 : rootCX
    const dropStartY = hasWives ? marY : myY + NH
    const barY = dropStartY + Math.round((firstChildY - dropStartY) * 0.5)
    myDrops.push({ x: dropStartX, y1: dropStartY, y2: barY })
    if (childCXs.length === 1) {
      const cc = childCXs[0]
      if (Math.abs(dropStartX - cc) < 1) {
        myDrops.push({ x: cc, y1: barY, y2: firstChildY })
      } else {
        myHbars.push({ x1: Math.min(dropStartX, cc), x2: Math.max(dropStartX, cc), y: barY })
        myDrops.push({ x: cc, y1: barY, y2: firstChildY })
      }
    } else {
      const barMinX = Math.min(dropStartX, cmin)
      const barMaxX = Math.max(dropStartX, cmax)
      myHbars.push({ x1: barMinX, x2: barMaxX, y: barY })
      for (const cc of childCXs) {
        myDrops.push({ x: cc, y1: barY, y2: firstChildY })
      }
    }

    // collect descendants
    for (const r of childResults) {
      myNodes.push(...r.nodes)
      myDrops.push(...r.drops)
      myHbars.push(...r.hbars)
      myMarriages.push(...r.marriages)
    }

    const rightEdge = Math.max(rootX + NW, cursorX - HG, wResult.maxX)
    return {
      nodes: myNodes, drops: myDrops, hbars: myHbars, marriages: myMarriages,
      rootCX, maxX: rightEdge, maxY,
    }
  }

  function placeWivesHere(rootId: string, rootCX: number, myY: number, wiveIds: string[]): { nodes: LNode[]; marriages: MLine[]; maxX: number } {
    const ns: LNode[] = []
    const ms: MLine[] = []
    const marY = myY + NH / 2
    let maxX = rootCX + NW / 2
    for (let wi = 0; wi < wiveIds.length; wi++) {
      const wid = wiveIds[wi]
      const wcx = rootCX - (wi + 1) * SLOT_K
      const wx = wcx - NW / 2
      const node = makeLNode(wid, wx, myY, false)
      if (node) ns.push(node)
      const prevCx = wi === 0 ? rootCX : rootCX - wi * SLOT_K
      // Marriage line: from this wife's right edge to neighbor's left edge
      ms.push({
        id: `m:${rootId}:${wid}:${wi}`,
        x1: wcx + NW / 2,
        x2: prevCx - NW / 2,
        y: marY,
      })
      maxX = Math.max(maxX, wx + NW)
    }
    return { nodes: ns, marriages: ms, maxX }
  }

  // ── Place spine cards ──
  spineList.forEach((id, i) => {
    const y = rowY(i + 1)
    const node = makeLNode(id, SPINE_X, y, true)
    if (node) nodes.push(node)
    spineRowOf.set(id, i)
  })

  trunkGuides.push({
    x: SPINE_X + NW / 2,
    y1: rowY(1),
    y2: rowY(spineList.length) + NH,
    color: '#10b981',
  })

  // ── For each spine person, place wives + handle children-by-wife ──
  const vis = new Set<string>(spineList)  // mark all spine as visited for subtree recursion

  for (let i = 0; i < spineList.length; i++) {
    const spineId = spineList[i]
    const sp_p = pMap.get(spineId)
    if (!sp_p) continue
    const myY = rowY(i + 1)
    const rootCX = SPINE_X + NW / 2
    const marY = myY + NH / 2

    // Wives — exclude any spine wife (none expected) and already-placed
    // 按 spine 人物的 spouse 欄位字串順序排（赫蒂徹必為首妻，靠近穆聖卡）
    const rawWiveIds = (sp.get(spineId) ?? []).filter(w =>
      !spineMembership.has(w) && !placedPersonIds.has(w)
    )
    const spouseField: string = (sp_p.data.spouseField as string) || ''
    const orderHint: string[] = spouseField.split(/[,，、]/).map(s => s.trim()).filter(Boolean)
    const nameToId = new Map<string, string>()
    for (const w of rawWiveIds) {
      const wp = pMap.get(w)
      if (wp) nameToId.set(wp.data.name, w)
    }
    const ordered: string[] = []
    for (const name of orderHint) {
      const wid = nameToId.get(name)
      if (wid && !ordered.includes(wid)) ordered.push(wid)
    }
    for (const wid of rawWiveIds) if (!ordered.includes(wid)) ordered.push(wid)
    const wiveIds = ordered

    // Place wives — 全部單行排左側、固定 SLOT_K 間距、婚姻線都同長 (WIFE_HG)
    // 仿 biblical 雅各家族 4 妻單行排列。穆聖 12 妻寬度 = 12 * SLOT_K = 2160 px，
    // 由 resetToTop 預設 100% zoom 確保看得清楚，user 自己 pan/zoom 探索
    const wifePosByIdx = new Map<number, { cx: number; x: number; y: number }>()
    for (let wi = 0; wi < wiveIds.length; wi++) {
      const wcx = rootCX - (wi + 1) * SLOT_K
      const wx  = wcx - NW / 2
      wifePosByIdx.set(wi, { cx: wcx, x: wx, y: myY })
    }
    for (let wi = 0; wi < wiveIds.length; wi++) {
      const wid = wiveIds[wi]
      const pos = wifePosByIdx.get(wi)!
      const node = makeLNode(wid, pos.x, pos.y, false)
      if (node) nodes.push(node)
      const prevCx = wi === 0 ? rootCX : rootCX - wi * SLOT_K
      marriages.push({
        id: `m:spine:${spineId}:${wid}`,
        x1: pos.cx + NW / 2,
        x2: prevCx - NW / 2,
        y: marY,
      })
      vis.add(wid)
    }

    // Spine→spine child drop (handled via plain vertical line between consecutive spine cards below)
    // 為何只在最後一代 spine (穆罕默德) 才跑 "non-spine kids" 群組？因為對其他 spine 人物，
    // 他們的非 spine 子嗣 = 下一代 spine 的兄弟姐妹，會被下面的 "siblings of spine"
    // 迴圈在 i+1 處理（放在 spine 右側）。如果這裡也放一遍會：
    //   - 父輩 spine（i）把他們置中放在父下方 → X 碰到下一代 spine column + 妻
    //   - 子輩 spine（i+1）跑 siblings loop 看見已 placed 就跳過 → 結果留在錯位置
    // 對最後一代 spine 沒有 i+1，所以必須在這裡處理 spineId 自己的子嗣（穆聖 7 子女 + 12 妻）。
    const isLastSpine = !spineList[i + 1]

    // Find non-spine children, group by which wife (mother) they belong to
    const allKids = ch.get(spineId) ?? []
    const nonSpineKids = isLastSpine
      ? allKids.filter(c => !spineMembership.has(c) && !placedPersonIds.has(c))
      : []

    // Build mother → kids map. If we can identify the wife who is the mother
    // (by checking that wife's children field), use her; else "unknown mom".
    const motherIdOfKid = new Map<string, string>()  // kid → wife personId
    for (const kid of nonSpineKids) {
      for (const wid of wiveIds) {
        const wifeKids = ch.get(wid) ?? []
        if (wifeKids.includes(kid)) {
          motherIdOfKid.set(kid, wid)
          break
        }
      }
    }

    // Also check spine child's mother (法蒂瑪 from Khadijah for Muhammad)
    const spineNextId = spineList[i + 1]
    let spineNextMother: string | undefined
    if (spineNextId) {
      for (const wid of wiveIds) {
        if ((ch.get(wid) ?? []).includes(spineNextId)) {
          spineNextMother = wid
          break
        }
      }
    }

    // Group nonSpineKids by mother. unknown-mom kids go into "no mom" bucket.
    type Group = { wifeId: string | null; kids: string[] }
    const groups: Group[] = []
    const noMomGroup: Group = { wifeId: null, kids: [] }
    const wifeGroup = new Map<string, Group>()
    for (const wid of wiveIds) wifeGroup.set(wid, { wifeId: wid, kids: [] })
    for (const kid of nonSpineKids) {
      const mom = motherIdOfKid.get(kid)
      if (mom) wifeGroup.get(mom)!.kids.push(kid)
      else noMomGroup.kids.push(kid)
    }
    for (const wid of wiveIds) {
      const g = wifeGroup.get(wid)!
      if (g.kids.length) groups.push(g)
    }
    if (noMomGroup.kids.length) groups.push(noMomGroup)

    // Render each group beneath the mother-or-spine via T-bar
    // Mother (wife)→kid drop 起點 = 妻↔右鄰中點（婚姻線 midpoint），垂直下降到 T-bar，再分支到每個子嗣
    for (const grp of groups) {
      const wi = grp.wifeId ? wiveIds.indexOf(grp.wifeId) : -1
      let dropStartX: number
      let dropStartY: number
      if (wi < 0) {
        // no specific mother — drop from spine bottom
        dropStartX = rootCX
        dropStartY = myY + NH
      } else {
        const wpos = wifePosByIdx.get(wi)!
        const motherPrevCx = wi === 0 ? rootCX : rootCX - wi * SLOT_K
        dropStartX = (wpos.cx + motherPrevCx) / 2
        dropStartY = marY
      }

      // Each kid: recursive subtree layout (so descendants come along)
      // Lay them in a row at gen+1 with HG gap. Anchor row left edge near mother.
      let groupCursor = dropStartX - (grp.kids.length * (NW + HG)) / 2 + NW / 2
      const kidResults: LayoutResult[] = []
      for (const kid of grp.kids) {
        const r = layoutSubtree(kid, groupCursor - NW / 2, vis, (sp_p.data.generationNum || i + 1) + 1, 0)
        if (r.nodes.length === 0) continue
        kidResults.push(r)
        groupCursor = r.maxX + HG + NW / 2
      }
      if (kidResults.length === 0) continue
      const kidCXs = kidResults.map(r => r.rootCX)
      const firstChildY = kidResults[0].nodes[0]?.y ?? myY + RH
      const barY = dropStartY + Math.round((firstChildY - dropStartY) * 0.5)
      drops.push({ x: dropStartX, y1: dropStartY, y2: barY })
      if (kidCXs.length === 1) {
        const cc = kidCXs[0]
        if (Math.abs(dropStartX - cc) < 1) {
          drops.push({ x: cc, y1: barY, y2: firstChildY })
        } else {
          hbars.push({ x1: Math.min(dropStartX, cc), x2: Math.max(dropStartX, cc), y: barY })
          drops.push({ x: cc, y1: barY, y2: firstChildY })
        }
      } else {
        const bMin = Math.min(dropStartX, ...kidCXs)
        const bMax = Math.max(dropStartX, ...kidCXs)
        hbars.push({ x1: bMin, x2: bMax, y: barY })
        for (const cc of kidCXs) drops.push({ x: cc, y1: barY, y2: firstChildY })
      }
      for (const r of kidResults) {
        nodes.push(...r.nodes)
        drops.push(...r.drops)
        hbars.push(...r.hbars)
        marriages.push(...r.marriages)
      }
    }

    // Spine→Spine child line: from spine card bottom (or marriage midpoint if next spine kid has a known mother)
    if (spineNextId && !spineMembership.has(spineId)) {
      // never reached because spineId is always in spineMembership; we always draw spine link via simple vertical below
    }
    if (spineNextId) {
      const childY = rowY(i + 2)
      let dropX = rootCX
      let dropStartY = myY + NH
      if (spineNextMother) {
        const wi2 = wiveIds.indexOf(spineNextMother)
        const wpos2 = wifePosByIdx.get(wi2)
        if (wpos2) {
          const motherPrevCx = wi2 === 0 ? rootCX : rootCX - wi2 * SLOT_K
          dropX = (wpos2.cx + motherPrevCx) / 2
          dropStartY = marY
        }
      }
      const barY = dropStartY + Math.round((childY - dropStartY) * 0.5)
      drops.push({ x: dropX, y1: dropStartY, y2: barY })
      const targetCX = SPINE_X + NW / 2
      if (Math.abs(dropX - targetCX) < 1) {
        drops.push({ x: targetCX, y1: barY, y2: childY })
      } else {
        hbars.push({ x1: Math.min(dropX, targetCX), x2: Math.max(dropX, targetCX), y: barY })
        drops.push({ x: targetCX, y1: barY, y2: childY })
      }
    }
  }

  // ── For each spine person (except 穆罕默德), also layout SIBLINGS to the right ──
  // (children of spine_parent that are not on spine)
  for (let i = 1; i < spineList.length; i++) {
    const personId = spineList[i]
    const myY = rowY(i + 1)
    const spineParent = spineList[i - 1]
    const siblings = (ch.get(spineParent) ?? []).filter(c =>
      !spineMembership.has(c) && !placedPersonIds.has(c)
    )
    if (siblings.length === 0) continue
    // 防止跨 subtree X 碰撞 — 只看 SAME ROW 的 nodes
    // (之前用「row myY 或以下」太寬，會被遙遠 chain 的 X 拖很遠；
    //  例如 易司哈格 subtree gen 21 起 27 代展開時把 納比特 推到極右)
    let cursorX = SPINE_X + NW + HG * 3
    for (const n of nodes) {
      if (Math.abs(n.y - myY) < 1 && n.x + NW > cursorX) {
        cursorX = n.x + NW + HG
      }
    }
    const sibResults: LayoutResult[] = []
    for (const sibId of siblings) {
      const r = layoutSubtree(sibId, cursorX, vis, i + 1, 0)
      if (r.nodes.length === 0) continue
      sibResults.push(r)
      cursorX = r.maxX + HG
    }
    if (sibResults.length === 0) continue
    // Sibling drops from spine_parent
    const parentPos = positionByPerson.get(spineParent)!
    const parentMidX = parentPos.x + NW / 2
    const parentBottomY = parentPos.y + NH
    const targetY = sibResults[0].nodes[0]?.y ?? myY
    const barY = parentBottomY + Math.round((targetY - parentBottomY) * 0.5)
    for (const r of sibResults) {
      const cc = r.rootCX
      // Add sibling drop bar
      drops.push({ x: cc, y1: barY, y2: targetY })
    }
    // Bar from parent down to each sibling
    const allCXs = sibResults.map(r => r.rootCX)
    hbars.push({
      x1: Math.min(parentMidX, ...allCXs),
      x2: Math.max(parentMidX, ...allCXs),
      y: barY,
    })
    drops.push({ x: parentMidX, y1: parentBottomY, y2: barY })
    for (const r of sibResults) {
      nodes.push(...r.nodes)
      drops.push(...r.drops)
      hbars.push(...r.hbars)
      marriages.push(...r.marriages)
    }
  }

  // ── Orphan area ── 只放「真的無法連到 spine」的人（蘇菲、未連通的 historical）
  // 被 collapsed subtree 隱藏的後代不應變成 orphan—他們躲在收摺裡，user 展開 ▼ 才會顯現。
  // 判定：person 透過 parent chain 不能到達任何 spine person → orphan
  const reachesSpine = new Map<string, boolean>()
  function descendsFromSpine(id: string, vis: Set<string> = new Set()): boolean {
    if (reachesSpine.has(id)) return reachesSpine.get(id)!
    if (vis.has(id)) return false
    vis.add(id)
    if (spineMembership.has(id)) { reachesSpine.set(id, true); return true }
    // 透過 parents 往上追
    for (const par of pa.get(id) ?? []) {
      if (descendsFromSpine(par, vis)) { reachesSpine.set(id, true); return true }
    }
    // 透過 spouse — 嫁/娶 spine person 也算
    for (const spId of sp.get(id) ?? []) {
      if (spineMembership.has(spId)) { reachesSpine.set(id, true); return true }
    }
    reachesSpine.set(id, false); return false
  }

  // Orphans: 放在 spine 最後一代 + 2 row 下方（避免擠在 Adam 旁邊）
  // 限定在 SPINE_X 兩側 ±450 內，3 行排列
  const orphanY0 = rowY(spineList.length) + RH * 2
  const ORPHAN_COLS = 6
  let orphanCol = 0
  let orphanRow = 0
  for (const node of props.nodes) {
    if (placedPersonIds.has(node.id)) continue
    if (descendsFromSpine(node.id)) continue   // 屬於 collapsed subtree—暫時隱藏
    const ox = SPINE_X - (NW + HG) * ORPHAN_COLS / 2 + orphanCol * (NW + HG)
    const oy = orphanY0 + orphanRow * RH * 0.85
    const lnode = makeLNode(node.id, ox, oy, false)
    if (lnode) nodes.push(lnode)
    orphanCol++
    if (orphanCol >= ORPHAN_COLS) { orphanCol = 0; orphanRow++ }
  }

  // ── Canvas bounds: shift if anything negative ──
  let minX = 0, maxX = 0, maxY = 0
  for (const n of nodes) {
    if (n.x < minX) minX = n.x
    if (n.x + n.w > maxX) maxX = n.x + n.w
    if (n.y + n.h > maxY) maxY = n.y + n.h
  }
  const shift = minX < PAD ? PAD - minX : 0
  if (shift !== 0) {
    for (const n of nodes)     n.x += shift
    for (const d of drops)     d.x += shift
    for (const b of hbars)   { b.x1 += shift; b.x2 += shift }
    for (const m of marriages){ m.x1 += shift; m.x2 += shift }
    for (const g of trunkGuides) g.x += shift
    maxX += shift
    for (const [k, v] of positionByPerson) positionByPerson.set(k, { x: v.x + shift, y: v.y })
  }

  return {
    nodes, drops, hbars, marriages, trunkGuides,
    w: Math.max(maxX + PAD, 1600),
    h: Math.max(maxY + PAD, 800),
    spineCenterX: SPINE_X + shift,
  }
})

const ready = computed(() => hasSpine.value && cv.value !== null)

// ── Card visual ──
function cardClass(n: LNode) {
  // 不含 `relative`——`relative` 會在 Tailwind cascade 蓋掉 inline `absolute`，
  // 害 v-for 第 N 張卡片掉到 normal flow 第 N 行（debug 過：哈娃曾被推到 y=2181）。
  // 卡內子元素的 absolute 定位由 .node-card 既是 absolute 又有 left/top inline 提供 containing block。
  const m: Record<string, string> = {
    quranic:      'border-gray-300 bg-white',
    sunni:        'border-emerald-300 bg-emerald-50',
    shia_twelver: 'border-rose-300 bg-rose-50',
    shia_ismaili: 'border-purple-300 bg-purple-50',
    shia_zaidi:   'border-orange-300 bg-orange-50',
    sufi:         'border-teal-300 bg-teal-50',
    historical:   'border-gray-300 bg-gray-50',
  }
  return `rounded-lg border shadow-sm hover:shadow transition cursor-pointer ${m[n.tradition] ?? m.sunni}`
}
function cardStyle(n: LNode) {
  return { left: n.x + 'px', top: n.y + 'px', width: n.w + 'px', height: n.h + 'px' }
}
function onCardClick(n: LNode) { emit('selectPerson', n.personId) }

// ── Pan / zoom ──
const viewportRef = ref<HTMLElement | null>(null)
const zoom  = ref(0.65)
const panX  = ref(20)
const panY  = ref(20)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, panX: 0, panY: 0 })

function onWheel(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey) {
    const delta = -e.deltaY * 0.001
    const newZoom = Math.max(0.15, Math.min(2, zoom.value + delta))
    const rect = viewportRef.value?.getBoundingClientRect()
    if (rect) {
      const cx = e.clientX - rect.left, cy = e.clientY - rect.top
      const factor = newZoom / zoom.value
      panX.value = cx - (cx - panX.value) * factor
      panY.value = cy - (cy - panY.value) * factor
    }
    zoom.value = newZoom
  } else {
    panX.value -= e.deltaX
    panY.value -= e.deltaY
  }
}
function onPointerDown(e: PointerEvent) {
  if ((e.target as HTMLElement).closest('.node-card, button')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY, panX: panX.value, panY: panY.value }
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}
function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  panX.value = dragStart.value.panX + (e.clientX - dragStart.value.x)
  panY.value = dragStart.value.panY + (e.clientY - dragStart.value.y)
}
function onPointerUp(e: PointerEvent) {
  isDragging.value = false
  try { (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId) } catch {}
}
function zoomIn()  { zoom.value = Math.min(2, zoom.value + 0.1) }
function zoomOut() { zoom.value = Math.max(0.15, zoom.value - 0.1) }

function fitSpine() {
  // "定位主幹" — fit ~14 rows centered on spine column.
  // 不 fit canvas 整高（subtree 收摺後仍可能上千 px），改 fit spine rows。
  if (!cv.value || !viewportRef.value) return
  const vw = viewportRef.value.clientWidth
  const vh = viewportRef.value.clientHeight
  const c = cv.value
  const targetRows = 14
  const targetH = targetRows * RH
  const z = Math.max(0.15, Math.min(0.9, vh / targetH))
  zoom.value = z
  panX.value = vw / 2 - c.spineCenterX * z
  panY.value = 40
}

function resetToTop() {
  // 預設初始視野：100% zoom + spine 水平置中 + 頂端對齊 viewport
  // 仿 biblical 雅各家族那種視角，user 自己 scroll/zoom 探索
  if (!cv.value || !viewportRef.value) return
  const vw = viewportRef.value.clientWidth
  zoom.value = 1
  panX.value = vw / 2 - cv.value.spineCenterX
  panY.value = 0
}

watch(ready, (r) => { if (r) nextTick(resetToTop) }, { immediate: true })
onMounted(() => { if (ready.value) nextTick(resetToTop) })
</script>
