<template>
  <div class="flex items-center gap-0 px-2 h-12 bg-white border-b border-gray-200 flex-shrink-0 overflow-x-auto select-none">

    <!-- ─── 新增 ─────────────────────────────────── -->
    <div class="flex items-center gap-0.5 px-1">
      <button class="rb-btn" @click="$emit('addPerson')">🧑 人物</button>
      <button class="rb-btn" @click="$emit('addTextBox')">💬 文字</button>
      <button class="rb-btn" @click="$emit('addGroup')">⬜ 框選</button>
    </div>

    <div class="sep" />

    <!-- ─── 節點樣式 ─────────────────────────────── -->
    <div class="relative" ref="nodeMenuRef">
      <button
        class="rb-toggle flex items-center gap-1.5"
        :class="showNodeMenu ? 'active-amber' : ''"
        @click="showNodeMenu = !showNodeMenu"
      >
        <!-- border preview mini box -->
        <div class="flex-shrink-0" :style="nodeBorderPreview" />
        <!-- color dot -->
        <div class="w-3 h-3 rounded-full border border-gray-200 flex-shrink-0" :style="{ background: activeBorderColor }" />
        <span>節點</span>
        <span v-if="selectedNode" class="ml-0.5 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
        <span class="text-gray-300 text-[9px]">▼</span>
      </button>

      <div v-if="showNodeMenu" class="dropdown w-72 left-0">

        <!-- Quick edit when node selected -->
        <template v-if="selectedNode">
          <p class="dl">{{ selectedNode.data?.name || '未命名' }} · 快速編輯</p>
          <div class="flex gap-1.5 mb-1.5">
            <input :value="selectedNode.data?.name"
              class="flex-1 field" placeholder="姓名"
              @input="e => emit('updateNode', { name: (e.target as HTMLInputElement).value })" />
            <select :value="selectedNode.data?.gender || 'unknown'"
              class="field w-14 bg-white"
              @change="e => emit('updateNode', { gender: (e.target as HTMLSelectElement).value })">
              <option value="unknown">？</option>
              <option value="male">♂</option>
              <option value="female">♀</option>
            </select>
          </div>
          <input :value="selectedNode.data?.generation"
            class="w-full field mb-1.5" placeholder="輩分稱謂"
            @input="e => emit('updateNode', { generation: (e.target as HTMLInputElement).value })" />
          <div class="flex gap-1.5 mb-3">
            <input :value="selectedNode.data?.birthYear"
              class="flex-1 field" placeholder="生年"
              @input="e => emit('updateNode', { birthYear: (e.target as HTMLInputElement).value })" />
            <input :value="selectedNode.data?.deathYear"
              class="flex-1 field" placeholder="卒年"
              @input="e => emit('updateNode', { deathYear: (e.target as HTMLInputElement).value })" />
          </div>
          <div class="h-px bg-gray-100 mb-3" />
        </template>

        <!-- Shape -->
        <div class="mb-3">
          <p class="dl">形狀</p>
          <div class="flex gap-1.5">
            <button v-for="s in shapes" :key="s.value"
              class="flex-1 py-1.5 text-xs border rounded-lg transition font-medium"
              :class="activeShape === s.value
                ? 'bg-amber-100 border-amber-300 text-amber-700'
                : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
              @click="setNodeShape(s.value)">{{ s.label }}</button>
          </div>
        </div>

        <!-- 8 border styles -->
        <div class="mb-3">
          <p class="dl">框線樣式 · <span class="font-normal normal-case tracking-normal">{{ currentBorderLabel }}</span></p>
          <div class="grid grid-cols-4 gap-1">
            <button v-for="bs in BORDER_STYLES" :key="bs.id"
              class="h-9 rounded-lg flex items-center justify-center border transition"
              :class="activeBorderStyleId === bs.id
                ? 'bg-amber-50 border-amber-400 ring-1 ring-amber-300'
                : 'border-gray-200 bg-gray-50 hover:bg-gray-100'"
              :title="bs.label"
              @click="setBorderStyle(bs.id)">
              <div :style="{
                width: '20px', height: '20px',
                borderWidth: bs.borderWidth + 'px',
                borderStyle: bs.borderStyle,
                borderRadius: bs.borderRadius + 'px',
                borderColor: activeBorderColor || '#374151',
              }" />
            </button>
          </div>
        </div>

        <!-- 16 border colors -->
        <div class="mb-3">
          <p class="dl">框線顏色</p>
          <div class="grid grid-cols-8 gap-1">
            <button v-for="c in EDGE_COLORS" :key="c"
              class="w-full aspect-square rounded border-2 transition hover:scale-110"
              :style="{ background: c, borderColor: activeBorderColor === c ? '#1f2937' : 'transparent' }"
              @click="setBorderColor(c)" />
          </div>
        </div>

        <!-- Fill color -->
        <div class="mb-3 flex items-center gap-2">
          <p class="dl mb-0">填充色</p>
          <input type="color" :value="activeBgColor || '#ffffff'"
            class="w-7 h-7 rounded cursor-pointer border border-gray-200"
            @input="e => setBgColor((e.target as HTMLInputElement).value)" />
          <button class="text-[10px] text-gray-400 underline hover:text-gray-600 transition"
            @click="setBgColor('')">重設</button>
        </div>

        <!-- Global shape apply -->
        <button
          class="w-full py-1.5 text-xs text-amber-600 border border-amber-200 rounded-lg hover:bg-amber-50 transition mb-1.5"
          @click="emit('setShape', activeShape)">
          套用形狀至所有節點
        </button>

        <!-- Delete node -->
        <button v-if="selectedNode"
          class="w-full py-1.5 text-xs text-red-400 border border-red-200 rounded-lg hover:bg-red-50 transition"
          @click="emit('deleteNode'); showNodeMenu = false">刪除節點</button>
      </div>
    </div>

    <div class="sep" />

    <!-- ─── 連線樣式 ─────────────────────────────── -->
    <div class="relative" ref="edgeMenuRef">
      <button
        class="rb-toggle flex items-center gap-1.5"
        :class="showEdgeMenu ? 'active-blue' : ''"
        @click="showEdgeMenu = !showEdgeMenu"
      >
        <svg width="22" height="10" class="flex-shrink-0">
          <line x1="2" y1="5" x2="20" y2="5"
            :stroke="activeEdgeColor" stroke-width="1.8"
            :stroke-dasharray="activeEdgeDash || undefined" />
        </svg>
        <div class="w-3 h-3 rounded-full border border-gray-200 flex-shrink-0" :style="{ background: activeEdgeColor }" />
        <span>連線</span>
        <span v-if="selectedEdge" class="ml-0.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
        <span class="text-gray-300 text-[9px]">▼</span>
      </button>

      <div v-if="showEdgeMenu" class="dropdown w-80 left-0">

        <!-- 4 line types -->
        <div class="mb-3">
          <p class="dl">線型</p>
          <div class="grid grid-cols-2 gap-1">
            <button v-for="t in EDGE_LINE_TYPES" :key="t.id"
              class="py-1.5 px-2 text-xs border rounded-lg transition flex flex-col text-left"
              :class="activeEdgeLineType === t.id
                ? 'bg-blue-50 border-blue-300 text-blue-700'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
              @click="setEdgeLineType(t.id)">
              <span class="font-medium">{{ t.label }}</span>
              <span class="text-[10px] text-gray-400">{{ t.desc }}</span>
            </button>
          </div>
        </div>

        <!-- 16 edge colors with naming -->
        <div class="mb-3">
          <p class="dl">顏色（可命名）</p>
          <div class="grid grid-cols-8 gap-1 mb-2">
            <button v-for="c in EDGE_COLORS" :key="c"
              class="w-full aspect-square rounded border-2 transition hover:scale-110"
              :style="{ background: c, borderColor: activeEdgeColor === c ? '#1f2937' : 'transparent' }"
              :title="colorLegend[c] || c"
              @click="setEdgeColor(c)" />
          </div>
          <div v-if="activeEdgeColor" class="flex items-center gap-1.5">
            <div class="w-4 h-4 rounded flex-shrink-0" :style="{ background: activeEdgeColor }" />
            <input :value="colorLegend[activeEdgeColor] || ''"
              class="flex-1 field"
              placeholder="為此顏色命名…"
              @input="e => emit('updateColorLegend', activeEdgeColor, (e.target as HTMLInputElement).value)" />
          </div>
        </div>

        <!-- 4 dash styles with naming -->
        <div class="mb-3">
          <p class="dl">線條樣式（可命名）</p>
          <div class="space-y-1">
            <div v-for="s in EDGE_DASH_STYLES" :key="s.id"
              class="flex items-center gap-2 border rounded-lg px-2 py-1.5 cursor-pointer transition"
              :class="activeEdgeDashId === s.id
                ? 'bg-blue-50 border-blue-300'
                : 'border-gray-200 hover:border-gray-300'"
              @click="setEdgeDashStyle(s.id, s.dasharray)">
              <svg width="32" height="8" class="flex-shrink-0">
                <line x1="0" y1="4" x2="32" y2="4" stroke="#374151" stroke-width="2"
                  :stroke-dasharray="s.dasharray || undefined" />
              </svg>
              <span class="text-xs text-gray-600 flex-1">{{ lineStyleLegend[s.id] || s.label }}</span>
              <input :value="lineStyleLegend[s.id] || ''"
                class="w-16 border border-gray-100 rounded px-1 py-0.5 text-[10px] outline-none focus:border-amber-400 bg-white"
                placeholder="命名"
                @click.stop
                @input="e => emit('updateLineStyleLegend', s.id, (e.target as HTMLInputElement).value)" />
            </div>
          </div>
        </div>

        <!-- Width -->
        <div class="mb-3">
          <p class="dl">粗細（{{ activeEdgeWidth }}px）</p>
          <input type="range" v-model.number="activeEdgeWidth" min="1" max="8" step="0.5"
            class="w-full accent-blue-500" @change="applyEdge" />
        </div>

        <!-- Label + animated (only when edge selected) -->
        <template v-if="selectedEdge">
          <div class="mb-2 space-y-1.5">
            <input v-model="edgeLabel" type="text"
              class="w-full field" placeholder="連線標籤…"
              @input="applyEdge" />
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">流動動畫</span>
              <button
                class="w-9 h-5 rounded-full transition relative flex-shrink-0"
                :class="edgeAnimated ? 'bg-blue-400' : 'bg-gray-200'"
                @click="edgeAnimated = !edgeAnimated; applyEdge()">
                <span class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
                  :class="edgeAnimated ? 'left-4' : 'left-0.5'" />
              </button>
            </div>
          </div>
        </template>

        <!-- Delete edge -->
        <button v-if="selectedEdge"
          class="w-full py-1.5 text-xs text-red-400 border border-red-200 rounded-lg hover:bg-red-50 transition"
          @click="emit('deleteEdge'); showEdgeMenu = false">刪除連線</button>
      </div>
    </div>

    <div class="sep" />

    <!-- ─── 排版 ──────────────────────────────────── -->
    <div class="flex items-center gap-0.5 px-1">
      <button
        v-for="d in directions" :key="d.value"
        class="w-7 h-7 rounded flex items-center justify-center text-sm transition"
        :class="currentDirection === d.value
          ? 'bg-amber-100 text-amber-700'
          : 'text-gray-500 hover:bg-gray-100'"
        :title="d.label"
        @click="$emit('applyLayout', d.value)">{{ d.icon }}</button>
      <button class="rb-btn ml-0.5" title="調整視野至全部節點" @click="$emit('fitView')">⊡</button>
    </div>

    <div class="sep" />

    <!-- ─── AI ─────────────────────────────────────── -->
    <button
      class="rb-btn bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100"
      @click="$emit('openAi')">✨ AI 匯入</button>

    <div class="flex-1" />

    <!-- ─── 匯出 ──────────────────────────────────── -->
    <div class="relative flex-shrink-0" ref="exportMenuRef">
      <button class="rb-btn gap-0.5" @click="showExport = !showExport">
        ↓ 匯出 <span class="text-[9px] text-gray-300 ml-0.5">▼</span>
      </button>
      <div v-if="showExport" class="dropdown w-44 right-0 left-auto">
        <button class="export-item" @click="emit('export','png');         showExport=false">🖼 圖片（PNG）</button>
        <button class="export-item" @click="emit('export','pdf-diagram'); showExport=false">📄 PDF（純圖）</button>
        <button class="export-item" @click="emit('export','pdf-full');    showExport=false">📋 PDF（圖＋文）</button>
        <button class="export-item" @click="emit('export','word');        showExport=false">📝 Word（圖＋文）</button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Node, Edge } from '@vue-flow/core'
import { BORDER_STYLES, EDGE_COLORS, EDGE_DASH_STYLES, EDGE_LINE_TYPES } from '~/composables/useGenealogyStyles'

const props = defineProps<{
  currentDirection: string
  nodeShape: 'circle' | 'rectangle'
  selectedNode: Node | null
  selectedEdge: Edge | null
  colorLegend: Record<string, string>
  lineStyleLegend: Record<string, string>
}>()

const emit = defineEmits<{
  applyLayout:           [dir: string]
  setShape:              [shape: 'circle' | 'rectangle']
  addPerson:             []
  addTextBox:            []
  addGroup:              []
  fitView:               []
  openAi:                []
  export:                [format: string]
  updateNode:            [data: Record<string, any>]
  deleteNode:            []
  updateEdge:            [data: Record<string, any>]
  deleteEdge:            []
  updateColorLegend:     [hex: string, name: string]
  updateLineStyleLegend: [id: string, name: string]
}>()

// ── Dropdowns ──────────────────────────────────────────────
const showNodeMenu  = ref(false)
const showEdgeMenu  = ref(false)
const showExport    = ref(false)
const nodeMenuRef   = ref<HTMLElement>()
const edgeMenuRef   = ref<HTMLElement>()
const exportMenuRef = ref<HTMLElement>()

onClickOutside(nodeMenuRef,   () => { showNodeMenu.value  = false })
onClickOutside(edgeMenuRef,   () => { showEdgeMenu.value  = false })
onClickOutside(exportMenuRef, () => { showExport.value    = false })

// ── Node state ─────────────────────────────────────────────
const shapes = [
  { value: 'rectangle' as const, label: '▭ 方形' },
  { value: 'circle'    as const, label: '◯ 圓形' },
]

const activeShape         = ref<'circle' | 'rectangle'>('rectangle')
const activeBorderStyleId = ref('solid-md')
const activeBorderColor   = ref('#d1d5db')
const activeBgColor       = ref('')

const currentBorderLabel = computed(() =>
  BORDER_STYLES.find(s => s.id === activeBorderStyleId.value)?.label ?? ''
)

const nodeBorderPreview = computed(() => {
  const bs = BORDER_STYLES.find(s => s.id === activeBorderStyleId.value)
  if (!bs) return {}
  return {
    width: '18px', height: '18px', display: 'block', flexShrink: '0',
    borderWidth: `${bs.borderWidth}px`,
    borderStyle: bs.borderStyle,
    borderRadius: activeShape.value === 'circle' ? '50%' : `${bs.borderRadius}px`,
    borderColor: activeBorderColor.value || '#374151',
  }
})

watch(() => props.selectedNode, node => {
  if (!node) return
  activeShape.value         = node.data?.shape         ?? 'rectangle'
  activeBorderStyleId.value = node.data?.borderStyleId ?? 'solid-md'
  activeBorderColor.value   = node.data?.borderColor   ?? '#d1d5db'
  activeBgColor.value       = node.data?.bgColor       ?? ''
}, { immediate: true })

function setNodeShape(s: 'circle' | 'rectangle') {
  activeShape.value = s
  if (props.selectedNode) emit('updateNode', { shape: s })
}
function setBorderStyle(id: string) {
  activeBorderStyleId.value = id
  if (props.selectedNode) emit('updateNode', { borderStyleId: id })
}
function setBorderColor(c: string) {
  activeBorderColor.value = c
  if (props.selectedNode) emit('updateNode', { borderColor: c })
}
function setBgColor(c: string) {
  activeBgColor.value = c
  if (props.selectedNode) emit('updateNode', { bgColor: c })
}

// ── Edge state ─────────────────────────────────────────────
const activeEdgeLineType = ref('smoothstep')
const activeEdgeColor    = ref('#6b7280')
const activeEdgeDashId   = ref('solid')
const activeEdgeDash     = ref('')
const activeEdgeWidth    = ref(2)
const edgeLabel          = ref('')
const edgeAnimated       = ref(false)

watch(() => props.selectedEdge, edge => {
  if (!edge) return
  const ds = EDGE_DASH_STYLES.find(s => s.dasharray === (edge.data?.strokeDasharray ?? ''))
  activeEdgeLineType.value = edge.data?.lineType        ?? (edge.type as string) ?? 'smoothstep'
  activeEdgeColor.value    = edge.data?.color           ?? '#6b7280'
  activeEdgeDashId.value   = edge.data?.dashStyleId     ?? ds?.id ?? 'solid'
  activeEdgeDash.value     = edge.data?.strokeDasharray ?? ''
  activeEdgeWidth.value    = edge.data?.strokeWidth     ?? 2
  edgeLabel.value          = (edge.label as string)     ?? ''
  edgeAnimated.value       = edge.animated              ?? false
}, { immediate: true })

function setEdgeLineType(id: string) {
  activeEdgeLineType.value = id
  if (props.selectedEdge) applyEdge()
}
function setEdgeColor(c: string) {
  activeEdgeColor.value = c
  if (props.selectedEdge) applyEdge()
}
function setEdgeDashStyle(id: string, dasharray: string) {
  activeEdgeDashId.value = id
  activeEdgeDash.value   = dasharray
  if (props.selectedEdge) applyEdge()
}
function applyEdge() {
  if (!props.selectedEdge) return
  emit('updateEdge', {
    lineType:        activeEdgeLineType.value,
    color:           activeEdgeColor.value,
    dashStyleId:     activeEdgeDashId.value,
    strokeDasharray: activeEdgeDash.value,
    strokeWidth:     activeEdgeWidth.value,
    label:           edgeLabel.value,
    animated:        edgeAnimated.value,
  })
}

// ── Layout ─────────────────────────────────────────────────
const directions = [
  { value: 'TB', icon: '↓', label: '上→下' },
  { value: 'BT', icon: '↑', label: '下→上' },
  { value: 'LR', icon: '→', label: '左→右' },
  { value: 'RL', icon: '←', label: '右→左' },
]
</script>

<style scoped>
.rb-btn {
  @apply flex items-center gap-1 px-2.5 h-8 rounded-lg text-xs font-medium text-gray-600 border border-gray-200 bg-white hover:bg-gray-50 transition cursor-pointer whitespace-nowrap;
}
.rb-toggle {
  @apply flex items-center gap-1 px-2.5 h-8 rounded-lg text-xs font-medium text-gray-600 border border-gray-200 bg-white hover:bg-gray-50 transition cursor-pointer whitespace-nowrap;
}
.active-amber {
  @apply bg-amber-50 border-amber-300 text-amber-700;
}
.active-blue {
  @apply bg-blue-50 border-blue-300 text-blue-700;
}
.sep {
  @apply h-6 w-px bg-gray-200 mx-2 flex-shrink-0;
}
.dropdown {
  @apply absolute top-[calc(100%+6px)] bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-3;
}
.dl {
  @apply text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5 block;
}
.field {
  @apply border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400;
}
.export-item {
  @apply w-full text-left px-3 py-1.5 text-sm text-gray-700 hover:bg-amber-50 hover:text-amber-700 transition flex items-center gap-2;
}
</style>
