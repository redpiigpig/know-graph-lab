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

          <!-- Spine trunk guide -->
          <line v-for="(g, i) in cv!.trunkGuides" :key="'tg'+i"
                :x1="g.x" :y1="g.y1" :x2="g.x" :y2="g.y2"
                :stroke="g.color" stroke-width="6" opacity="0.10" stroke-linecap="round" />

          <!-- Marriage lines (red) -->
          <line v-for="m in cv!.marriages" :key="m.id"
                :x1="m.x1" :y1="m.y" :x2="m.x2" :y2="m.y"
                stroke="#dc2626" stroke-width="2" stroke-linecap="round" />

          <!-- Vertical drops (parent → child) -->
          <line v-for="(d, i) in cv!.drops" :key="'d'+i"
                :x1="d.x" :y1="d.y1" :x2="d.x" :y2="d.y2"
                :stroke="d.stroke || '#9ca3af'" stroke-width="1.5"
                stroke-linecap="round" />

          <!-- Horizontal bars -->
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
        </div>
      </div>

      <!-- View switch widget — local toggle near Muhammad spine card -->
      <div
        v-if="muhammadScreenPos.visible"
        class="absolute z-40 bg-white/95 border border-gray-200 rounded-lg p-1 shadow-sm flex flex-col items-stretch gap-0.5 pointer-events-auto"
        :style="{ left: muhammadScreenPos.x + 'px', top: muhammadScreenPos.y + 'px' }"
      >
        <span class="text-[10px] text-gray-400 px-1.5 select-none leading-tight">視角</span>
        <button
          v-for="t in viewOptions"
          :key="t.value"
          class="text-[11px] px-2 py-1 rounded-md font-medium transition cursor-default text-left"
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
        <div class="flex items-center gap-1.5"><span class="w-3 h-[2px] bg-gray-400 rounded-full" />親子</div>
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
  { value: 'quranic',      label: '古蘭',     activeColor: 'text-gray-900',     tooltip: '只顯示古蘭明文人物（普世共識）' },
  { value: 'sunni',        label: '順尼',     activeColor: 'text-emerald-700',  tooltip: '順尼派視角：古蘭 + Sira/Hadith + 史傳' },
  { value: 'shia_twelver', label: '十二派',   activeColor: 'text-rose-700',     tooltip: '十二伊瑪目派：含 Hasan→Mahdi 鏈' },
  { value: 'shia_ismaili', label: '伊斯瑪儀', activeColor: 'text-purple-700',   tooltip: '伊斯瑪儀派：於 Ja\'far 接伊斯瑪儀分支' },
  { value: 'shia_zaidi',   label: '栽德',     activeColor: 'text-orange-700',   tooltip: '栽德派：於宰因·阿比丁接宰德分支' },
]

// ── Layout constants ──
const NW = 130
const NH = 56
const HG = 18         // sibling horizontal gap
const WIFE_HG = 36    // wife-stack horizontal gap from spine
const VG = 80         // vertical gap between rows
const RH = NH + VG
const PAD = 60

const baseName = (s: string) => s.split('（')[0].trim()
const disambigOf = (s: string) => {
  const m = s.match(/^[^（]+（(.+)）$/)
  return m ? m[1] : ''
}

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

// ── Spine path: Adam → Muhammad via BFS through waypoints ──
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

const SPINE_WAYPOINTS = [
  '阿丹', '努哈', '易卜拉欣', '伊斯瑪儀', '阿德南', '穆罕默德',
]

const spinePath = computed(() => spineFromWaypoints(SPINE_WAYPOINTS, childrenOf.value))
const hasSpine = computed(() => spinePath.value.length > 0)
const spineSet = computed(() => new Set(spinePath.value))

const muhammadId = computed(() => resolveByName('穆罕默德'))
const aliId      = computed(() => resolveByName('阿里（艾比·塔利卜之子）'))
const fatimaId   = computed(() => resolveByName('法蒂瑪（穆聖之女）'))

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
}
interface VDrop { x: number; y1: number; y2: number; stroke?: string }
interface HBar  { x1: number; x2: number; y: number; stroke?: string }
interface MLine { id: string; x1: number; x2: number; y: number }
interface TrunkGuide { x: number; y1: number; y2: number; color: string }

// ── Main layout ──
const cv = computed(() => {
  if (!hasSpine.value) return null

  const ch  = childrenOf.value
  const sp  = spousesOf.value
  const pa  = parentsOf.value
  const pMap = personById.value

  const nodes:    LNode[]      = []
  const drops:    VDrop[]      = []
  const hbars:    HBar[]       = []
  const marriages:MLine[]      = []
  const trunkGuides:TrunkGuide[] = []

  const placedPersonIds = new Set<string>()
  const positionByPerson = new Map<string, { x: number; y: number }>()
  const spineRowOf = new Map<string, number>()

  const SPINE_X = 600  // spine column center

  function placeNode(personId: string, x: number, y: number, isSpine = false): LNode | null {
    if (placedPersonIds.has(personId)) return null
    const p = pMap.get(personId)
    if (!p) return null
    placedPersonIds.add(personId)
    const raw  = p.data.name as string
    const base = baseName(raw)
    const dis  = disambigOf(raw)
    const display = base.length <= 8 ? base : base.slice(0, 7) + '…'
    const ln: LNode = {
      id: `n:${personId}`,
      personId,
      rawName:    raw,
      displayName: display,
      kunya:      (p.data.kunya as string) || '',
      disambig:   dis,
      genLabel:   p.data.generation || '',
      generation: p.data.generationNum ?? 0,
      gender:     p.data.gender,
      tradition:  p.data.tradition || 'sunni',
      x, y, w: NW, h: NH,
      isSpine,
    }
    nodes.push(ln)
    positionByPerson.set(personId, { x, y })
    return ln
  }

  // ── Step 1: place spine, vertical column ──
  const path = spinePath.value
  path.forEach((id, i) => {
    const y = PAD + i * RH
    placeNode(id, SPINE_X, y, true)
    spineRowOf.set(id, i)
  })

  // Spine trunk guide
  trunkGuides.push({
    x: SPINE_X + NW / 2,
    y1: PAD,
    y2: PAD + (path.length - 1) * RH + NH,
    color: '#10b981',
  })

  // Spine parent→child drops
  for (let i = 0; i < path.length - 1; i++) {
    const parentId = path[i], childId = path[i + 1]
    const py = PAD + i * RH + NH
    const cy = PAD + (i + 1) * RH
    drops.push({ x: SPINE_X + NW / 2, y1: py, y2: cy })
  }

  // ── Step 2: place spouses to the LEFT of each spine card (stacked if multiple) ──
  for (const spineId of path) {
    const wives = (sp.get(spineId) ?? []).filter(w => !spineSet.value.has(w) && !placedPersonIds.has(w))
    const spineCenter = positionByPerson.get(spineId)!
    wives.forEach((wifeId, idx) => {
      const wx = spineCenter.x - (WIFE_HG + NW) * (idx + 1)
      const wy = spineCenter.y
      const placed = placeNode(wifeId, wx, wy, false)
      if (placed) {
        // Marriage line between rightmost wife and spine card
        marriages.push({
          id: `m:${spineId}:${wifeId}`,
          x1: wx + NW,
          x2: spineCenter.x,
          y:  wy + NH / 2,
        })
      }
    })
  }

  // ── Step 3: place SIBLINGS of each spine person to the RIGHT side of that row ──
  // (Not their parents — siblings = spine parent's other children, except the next-spine child)
  for (let i = 0; i < path.length; i++) {
    const personId = path[i]
    const parents = pa.get(personId) ?? []
    if (!parents.length) continue
    // Find the spine parent (one row up)
    const spineParent = parents.find(p => spineRowOf.get(p) === i - 1) ?? parents[0]
    const siblings = (ch.get(spineParent) ?? []).filter(c => c !== personId && !spineSet.value.has(c) && !placedPersonIds.has(c))
    if (!siblings.length) continue

    const pY = positionByPerson.get(personId)!.y
    let cursorX = SPINE_X + NW + HG * 4
    for (const sibId of siblings) {
      placeNode(sibId, cursorX, pY, false)
      // sibling parent→child drop
      const spineParentPos = positionByPerson.get(spineParent)!
      drops.push({
        x: cursorX + NW / 2,
        y1: spineParentPos.y + NH,
        y2: pY,
      })
      // horizontal bar connecting spine-parent drop line to sibling drop
      hbars.push({
        x1: SPINE_X + NW / 2,
        x2: cursorX + NW / 2,
        y:  pY - VG / 2,
      })
      cursorX += NW + HG
    }
  }

  // ── Step 4: place non-spine children of spine spouses (e.g. Muhammad's daughters by Khadijah) ──
  // For Muhammad, place his 7 children below him as a row
  if (muhammadId.value) {
    const mKids = (ch.get(muhammadId.value) ?? []).filter(c => !placedPersonIds.has(c))
    if (mKids.length) {
      const mPos = positionByPerson.get(muhammadId.value)!
      const totalW = mKids.length * NW + (mKids.length - 1) * HG
      const startX = mPos.x + NW / 2 - totalW / 2
      const kidsY = mPos.y + RH
      mKids.forEach((kidId, idx) => {
        const kx = startX + idx * (NW + HG)
        placeNode(kidId, kx, kidsY, false)
        drops.push({ x: kx + NW / 2, y1: kidsY - VG / 2, y2: kidsY })
      })
      // h-bar above the kids row
      if (mKids.length > 0) {
        const lastIdx = mKids.length - 1
        hbars.push({
          x1: startX + NW / 2,
          x2: startX + lastIdx * (NW + HG) + NW / 2,
          y: kidsY - VG / 2,
        })
        drops.push({ x: mPos.x + NW / 2, y1: mPos.y + NH, y2: kidsY - VG / 2 })
      }
    }
  }

  // ── Step 5: place Ali + 12 Imams chain (below Fatima) ──
  if (fatimaId.value && aliId.value) {
    const fPos = positionByPerson.get(fatimaId.value)
    if (fPos) {
      // Place Ali next to Fatima as spouse (left side)
      const aliX = fPos.x - WIFE_HG - NW
      const aliY = fPos.y
      placeNode(aliId.value, aliX, aliY, false)
      marriages.push({
        id: `m:${aliId.value}:${fatimaId.value}`,
        x1: aliX + NW,
        x2: fPos.x,
        y:  fPos.y + NH / 2,
      })

      // BFS down from Ali, place imam chain as a single descending column to the right
      const imamColX = fPos.x + NW + HG * 3
      const seen = new Set<string>([aliId.value, fatimaId.value])
      const queue: Array<{ id: string; row: number; parentY: number; parentX: number }> = []
      for (const kid of (ch.get(aliId.value) ?? [])) {
        if (!placedPersonIds.has(kid)) {
          queue.push({ id: kid, row: 0, parentY: aliY, parentX: imamColX })
        }
      }
      let row = 0
      while (queue.length) {
        const batch = queue.splice(0, queue.length)
        // Lay this row horizontally
        const startX = imamColX
        batch.forEach((item, idx) => {
          if (seen.has(item.id) || placedPersonIds.has(item.id)) return
          seen.add(item.id)
          const x = startX + idx * (NW + HG)
          const y = fPos.y + RH * (row + 1)
          placeNode(item.id, x, y, false)
          // drop from row above (use parent's position)
          const pPos = positionByPerson.get(item.id === aliId.value ? aliId.value : (pa.get(item.id)?.[0] ?? aliId.value))
          if (pPos) {
            drops.push({ x: x + NW / 2, y1: pPos.y + NH, y2: y })
          }
          // enqueue this person's children
          for (const kid of (ch.get(item.id) ?? [])) {
            if (!seen.has(kid) && !placedPersonIds.has(kid)) {
              queue.push({ id: kid, row: row + 1, parentY: y, parentX: x })
            }
          }
        })
        row++
        if (row > 20) break
      }
    }
  }

  // ── Step 6: any remaining nodes (orphans) — place in a tail column on the far right ──
  let orphanX = SPINE_X + 1200
  let orphanY = PAD
  for (const node of props.nodes) {
    if (placedPersonIds.has(node.id)) continue
    placeNode(node.id, orphanX, orphanY, false)
    orphanY += RH * 0.7
    if (orphanY > 4000) { orphanY = PAD; orphanX += NW + HG * 2 }
  }

  // ── Canvas bounds ──
  let maxX = 0, maxY = 0, minX = 0
  for (const n of nodes) {
    if (n.x + n.w > maxX) maxX = n.x + n.w
    if (n.y + n.h > maxY) maxY = n.y + n.h
    if (n.x < minX) minX = n.x
  }

  // Shift all coords so nothing has negative x
  const shift = minX < PAD ? PAD - minX : 0
  if (shift !== 0) {
    for (const n of nodes) n.x += shift
    for (const d of drops) d.x += shift
    for (const b of hbars) { b.x1 += shift; b.x2 += shift }
    for (const m of marriages) { m.x1 += shift; m.x2 += shift }
    for (const g of trunkGuides) g.x += shift
    maxX += shift
    for (const [k, v] of positionByPerson) positionByPerson.set(k, { x: v.x + shift, y: v.y })
  }

  return {
    nodes, drops, hbars, marriages, trunkGuides,
    w: Math.max(maxX + PAD, 1200),
    h: Math.max(maxY + PAD, 800),
    spineCenterX: SPINE_X + shift,
    muhammadPos: muhammadId.value ? positionByPerson.get(muhammadId.value) : null,
  }
})

const ready = computed(() => hasSpine.value && cv.value !== null)

// ── Card visual ──
function cardClass(n: LNode) {
  const m: Record<string, string> = {
    quranic:      'border-gray-300 bg-white',
    sunni:        'border-emerald-300 bg-emerald-50',
    shia_twelver: 'border-rose-300 bg-rose-50',
    shia_ismaili: 'border-purple-300 bg-purple-50',
    shia_zaidi:   'border-orange-300 bg-orange-50',
    sufi:         'border-teal-300 bg-teal-50',
    historical:   'border-gray-300 bg-gray-50',
  }
  return `relative rounded-lg border shadow-sm hover:shadow transition cursor-pointer ${m[n.tradition] ?? m.sunni}`
}
function cardStyle(n: LNode) {
  return {
    left: n.x + 'px',
    top: n.y + 'px',
    width: n.w + 'px',
    height: n.h + 'px',
  }
}

function onCardClick(n: LNode) {
  emit('selectPerson', n.personId)
}

// ── Pan / zoom ──
const viewportRef = ref<HTMLElement | null>(null)
const zoom = ref(0.85)
const panX = ref(20)
const panY = ref(20)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, panX: 0, panY: 0 })

function onWheel(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey) {
    const delta = -e.deltaY * 0.001
    const newZoom = Math.max(0.2, Math.min(2, zoom.value + delta))
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
function zoomOut() { zoom.value = Math.max(0.2, zoom.value - 0.1) }

function fitSpine() {
  if (!cv.value || !viewportRef.value) return
  const rect = viewportRef.value.getBoundingClientRect()
  const targetZoom = Math.min(0.85, (rect.height - 80) / (cv.value.h))
  zoom.value = Math.max(0.25, targetZoom)
  panX.value = rect.width / 2 - cv.value.spineCenterX * zoom.value
  panY.value = 30
}

onMounted(() => {
  watch(ready, (r) => {
    if (r) nextTick(fitSpine)
  }, { immediate: true })
})

// ── Position of Muhammad card on screen, for view-switch widget anchor ──
const muhammadScreenPos = computed(() => {
  if (!cv.value?.muhammadPos) return { visible: false, x: 0, y: 0 }
  const mp = cv.value.muhammadPos
  const sx = mp.x * zoom.value + panX.value
  const sy = mp.y * zoom.value + panY.value
  return {
    visible: true,
    x: sx + NW * zoom.value + 8,
    y: sy,
  }
})
</script>
