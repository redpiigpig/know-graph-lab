<template>
  <div class="flex flex-col h-full bg-white overflow-y-auto text-sm">

    <!-- ══ 節點工具 ══════════════════════════════ -->
    <section class="px-3 pt-3 pb-2 border-b border-gray-100">
      <div class="flex items-center gap-1.5 mb-2">
        <span class="text-[10px] font-bold uppercase tracking-wider text-amber-600">節點</span>
        <span v-if="selectedNode" class="text-[10px] text-amber-500 bg-amber-50 px-1.5 py-0.5 rounded-full">
          已選取：{{ selectedNode.data?.name || '未命名' }}
        </span>
        <span v-else class="text-[10px] text-gray-400">（點擊節點套用）</span>
      </div>

      <!-- 姓名快速編輯 -->
      <div v-if="selectedNode" class="mb-2 flex gap-1.5">
        <input
          :value="selectedNode.data?.name"
          class="flex-1 border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
          placeholder="姓名"
          @input="e => emit('updateNode', { name: (e.target as HTMLInputElement).value })"
        />
        <select
          :value="selectedNode.data?.gender || 'unknown'"
          class="border border-gray-200 rounded-lg px-1 py-1 text-xs outline-none focus:border-amber-400 bg-white"
          @change="e => emit('updateNode', { gender: (e.target as HTMLSelectElement).value })"
        >
          <option value="unknown">？</option>
          <option value="male">♂</option>
          <option value="female">♀</option>
        </select>
      </div>

      <!-- 輩分/年份 (only when selected) -->
      <div v-if="selectedNode" class="mb-2 flex gap-1.5">
        <input
          :value="selectedNode.data?.generation"
          class="flex-1 border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
          placeholder="輩分稱謂"
          @input="e => emit('updateNode', { generation: (e.target as HTMLInputElement).value })"
        />
      </div>
      <div v-if="selectedNode" class="mb-2 flex gap-1.5">
        <input
          :value="selectedNode.data?.birthYear"
          class="w-16 border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
          placeholder="生年"
          @input="e => emit('updateNode', { birthYear: (e.target as HTMLInputElement).value })"
        />
        <span class="text-gray-300 self-center">—</span>
        <input
          :value="selectedNode.data?.deathYear"
          class="w-16 border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
          placeholder="卒年"
          @input="e => emit('updateNode', { deathYear: (e.target as HTMLInputElement).value })"
        />
      </div>

      <!-- 節點形狀 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">形狀</p>
        <div class="flex gap-1.5">
          <button
            class="flex-1 py-1 rounded-lg text-xs border transition font-medium"
            :class="nodeShape === 'rectangle' ? 'bg-amber-100 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
            @click="setNodeShape('rectangle')"
          >▭ 方形</button>
          <button
            class="flex-1 py-1 rounded-lg text-xs border transition font-medium"
            :class="nodeShape === 'circle' ? 'bg-amber-100 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
            @click="setNodeShape('circle')"
          >◯ 圓形</button>
        </div>
      </div>

      <!-- 8 種框線樣式 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">框線樣式（8 種）</p>
        <div class="grid grid-cols-4 gap-1">
          <button
            v-for="bs in BORDER_STYLES" :key="bs.id"
            class="h-9 rounded-lg flex items-center justify-center transition border"
            :class="nodeBorderStyleId === bs.id
              ? 'bg-amber-50 border-amber-400 ring-1 ring-amber-300'
              : 'border-gray-200 bg-gray-50 hover:bg-gray-100'"
            :title="bs.label"
            @click="setNodeBorderStyle(bs.id)"
          >
            <div class="w-6 h-6 flex items-center justify-center" :style="{
              borderWidth: bs.borderWidth + 'px',
              borderStyle: bs.borderStyle,
              borderRadius: bs.borderRadius + 'px',
              borderColor: nodeBorderColor || '#374151',
            }" />
          </button>
        </div>
        <p class="text-[10px] text-gray-400 mt-1">{{ currentBorderLabel }}</p>
      </div>

      <!-- 框線顏色 (16色) -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">框線顏色</p>
        <div class="grid grid-cols-8 gap-1">
          <button
            v-for="c in EDGE_COLORS" :key="c"
            class="w-full aspect-square rounded border-2 transition hover:scale-110"
            :style="{ background: c, borderColor: nodeBorderColor === c ? '#1f2937' : 'transparent' }"
            @click="setNodeBorderColor(c)"
          />
        </div>
      </div>

      <!-- 填充顏色 -->
      <div class="mb-2 flex items-center gap-2">
        <p class="text-[10px] text-gray-400">填充</p>
        <input type="color" :value="nodeBgColor || '#ffffff'"
          class="w-7 h-7 rounded cursor-pointer border border-gray-200 flex-shrink-0"
          @input="e => setNodeBgColor((e.target as HTMLInputElement).value)" />
        <button class="text-[10px] text-gray-400 hover:text-gray-600 underline"
          @click="setNodeBgColor('')">重設</button>
      </div>

      <!-- Delete node -->
      <button v-if="selectedNode"
        class="w-full py-1 rounded-lg text-xs text-red-400 border border-red-200 hover:bg-red-50 transition mt-1"
        @click="emit('deleteNode')">刪除節點</button>
    </section>

    <!-- ══ 連線工具 ══════════════════════════════ -->
    <section class="px-3 pt-3 pb-3">
      <div class="flex items-center gap-1.5 mb-2">
        <span class="text-[10px] font-bold uppercase tracking-wider text-blue-600">連線</span>
        <span v-if="selectedEdge" class="text-[10px] text-blue-500 bg-blue-50 px-1.5 py-0.5 rounded-full">已選取</span>
        <span v-else class="text-[10px] text-gray-400">（點擊連線套用）</span>
      </div>

      <!-- 4 種線型 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">線型（4 種）</p>
        <div class="grid grid-cols-2 gap-1">
          <button
            v-for="t in EDGE_LINE_TYPES" :key="t.id"
            class="py-1.5 px-2 rounded-lg text-xs border transition text-left flex flex-col"
            :class="edgeLineType === t.id
              ? 'bg-blue-50 border-blue-300 text-blue-700'
              : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
            @click="setEdgeLineType(t.id)"
          >
            <span class="font-medium">{{ t.label }}</span>
            <span class="text-[10px] text-gray-400">{{ t.desc }}</span>
          </button>
        </div>
      </div>

      <!-- 16 色卡 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">顏色（16 色，可命名）</p>
        <div class="grid grid-cols-8 gap-1 mb-1.5">
          <button
            v-for="c in EDGE_COLORS" :key="c"
            class="w-full aspect-square rounded border-2 transition hover:scale-110"
            :style="{ background: c, borderColor: edgeColor === c ? '#1f2937' : 'transparent' }"
            :title="colorLegend[c] || c"
            @click="setEdgeColor(c)"
          />
        </div>
        <!-- Name selected color -->
        <div v-if="edgeColor" class="flex items-center gap-1.5">
          <div class="w-4 h-4 rounded flex-shrink-0" :style="{ background: edgeColor }" />
          <input
            :value="colorLegend[edgeColor] || ''"
            class="flex-1 border border-gray-200 rounded px-1.5 py-0.5 text-[11px] outline-none focus:border-amber-400"
            placeholder="為此顏色命名…"
            @input="e => emit('updateColorLegend', edgeColor, (e.target as HTMLInputElement).value)"
          />
        </div>
      </div>

      <!-- 4 種線條樣式 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">線條樣式（4 種，可命名）</p>
        <div class="space-y-1">
          <div
            v-for="s in EDGE_DASH_STYLES" :key="s.id"
            class="flex items-center gap-2 rounded-lg border px-2 py-1.5 cursor-pointer transition"
            :class="edgeDashStyleId === s.id
              ? 'bg-blue-50 border-blue-300'
              : 'border-gray-200 hover:border-gray-300'"
            @click="setEdgeDashStyle(s.id, s.dasharray)"
          >
            <svg width="32" height="8" class="flex-shrink-0">
              <line x1="0" y1="4" x2="32" y2="4" stroke="#374151" stroke-width="2"
                :stroke-dasharray="s.dasharray || ''" />
            </svg>
            <span class="text-xs text-gray-600 flex-1">
              {{ lineStyleLegend[s.id] || s.label }}
            </span>
            <input
              :value="lineStyleLegend[s.id] || ''"
              class="w-16 border border-gray-100 rounded px-1 py-0.5 text-[10px] outline-none focus:border-amber-400 bg-white"
              placeholder="命名"
              @click.stop
              @input="e => emit('updateLineStyleLegend', s.id, (e.target as HTMLInputElement).value)"
            />
          </div>
        </div>
      </div>

      <!-- 粗細 -->
      <div class="mb-2">
        <p class="text-[10px] text-gray-400 mb-1">粗細（{{ edgeStrokeWidth }}px）</p>
        <input type="range" v-model.number="edgeStrokeWidth" min="1" max="8" step="0.5"
          class="w-full accent-blue-500" @change="applyEdgeStyle" />
      </div>

      <!-- 標籤 + 動畫 -->
      <div v-if="selectedEdge" class="mb-2 space-y-1.5">
        <input v-model="edgeLabel" type="text"
          class="w-full border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
          placeholder="連線標籤…"
          @input="applyEdgeStyle" />
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-500">流動動畫</span>
          <button
            class="w-9 h-5 rounded-full transition relative flex-shrink-0"
            :class="edgeAnimated ? 'bg-blue-400' : 'bg-gray-200'"
            @click="edgeAnimated = !edgeAnimated; applyEdgeStyle()"
          >
            <span class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
              :class="edgeAnimated ? 'left-4' : 'left-0.5'" />
          </button>
        </div>
      </div>

      <!-- Delete edge -->
      <button v-if="selectedEdge"
        class="w-full py-1 rounded-lg text-xs text-red-400 border border-red-200 hover:bg-red-50 transition"
        @click="emit('deleteEdge')">刪除連線</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { Node, Edge } from '@vue-flow/core'
import {
  BORDER_STYLES, EDGE_COLORS, EDGE_DASH_STYLES, EDGE_LINE_TYPES,
  type BorderStyleId,
} from '~/composables/useGenealogyStyles'

const props = defineProps<{
  selectedNode: Node | null
  selectedEdge: Edge | null
  colorLegend: Record<string, string>
  lineStyleLegend: Record<string, string>
}>()

const emit = defineEmits<{
  updateNode:           [data: Record<string, any>]
  deleteNode:           []
  updateEdge:           [data: Record<string, any>]
  deleteEdge:           []
  updateColorLegend:    [hex: string, name: string]
  updateLineStyleLegend:[id: string, name: string]
}>()

// ── Node state ─────────────────────────────────────────────
const nodeShape         = ref<'circle'|'rectangle'>('rectangle')
const nodeBorderStyleId = ref<string>('solid-md')
const nodeBorderColor   = ref('#d1d5db')
const nodeBgColor       = ref('')

const currentBorderLabel = computed(() =>
  BORDER_STYLES.find(s => s.id === nodeBorderStyleId.value)?.label ?? ''
)

watch(() => props.selectedNode, (node) => {
  if (!node) return
  nodeShape.value         = node.data?.shape         ?? 'rectangle'
  nodeBorderStyleId.value = node.data?.borderStyleId ?? 'solid-md'
  nodeBorderColor.value   = node.data?.borderColor   ?? '#d1d5db'
  nodeBgColor.value       = node.data?.bgColor       ?? ''
}, { immediate: true })

function setNodeShape(shape: 'circle'|'rectangle') {
  nodeShape.value = shape
  if (props.selectedNode) emit('updateNode', { shape })
}
function setNodeBorderStyle(id: string) {
  nodeBorderStyleId.value = id
  if (props.selectedNode) emit('updateNode', { borderStyleId: id })
}
function setNodeBorderColor(c: string) {
  nodeBorderColor.value = c
  if (props.selectedNode) emit('updateNode', { borderColor: c })
}
function setNodeBgColor(c: string) {
  nodeBgColor.value = c
  if (props.selectedNode) emit('updateNode', { bgColor: c })
}

// ── Edge state ─────────────────────────────────────────────
const edgeLineType     = ref('smoothstep')
const edgeColor        = ref('#6b7280')
const edgeDashStyleId  = ref('solid')
const edgeDasharray    = ref('')
const edgeStrokeWidth  = ref(2)
const edgeLabel        = ref('')
const edgeAnimated     = ref(false)

watch(() => props.selectedEdge, (edge) => {
  if (!edge) return
  const dash = EDGE_DASH_STYLES.find(s => s.dasharray === (edge.data?.strokeDasharray ?? ''))
  edgeLineType.value    = edge.data?.lineType        ?? edge.type ?? 'smoothstep'
  edgeColor.value       = edge.data?.color           ?? '#6b7280'
  edgeDashStyleId.value = edge.data?.dashStyleId     ?? dash?.id ?? 'solid'
  edgeDasharray.value   = edge.data?.strokeDasharray ?? ''
  edgeStrokeWidth.value = edge.data?.strokeWidth     ?? 2
  edgeLabel.value       = (edge.label as string)     ?? ''
  edgeAnimated.value    = edge.animated              ?? false
}, { immediate: true })

function setEdgeLineType(id: string) {
  edgeLineType.value = id
  if (props.selectedEdge) applyEdgeStyle()
}
function setEdgeColor(c: string) {
  edgeColor.value = c
  if (props.selectedEdge) applyEdgeStyle()
}
function setEdgeDashStyle(id: string, dasharray: string) {
  edgeDashStyleId.value = id
  edgeDasharray.value   = dasharray
  if (props.selectedEdge) applyEdgeStyle()
}
function applyEdgeStyle() {
  if (!props.selectedEdge) return
  emit('updateEdge', {
    lineType:        edgeLineType.value,
    color:           edgeColor.value,
    dashStyleId:     edgeDashStyleId.value,
    strokeDasharray: edgeDasharray.value,
    strokeWidth:     edgeStrokeWidth.value,
    label:           edgeLabel.value,
    animated:        edgeAnimated.value,
  })
}
</script>
