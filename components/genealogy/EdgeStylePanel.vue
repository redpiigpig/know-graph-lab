<template>
  <div class="flex flex-col h-full text-sm">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
      <span class="font-semibold text-gray-700">連線樣式</span>
      <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="$emit('close')">×</button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 py-3 space-y-4">

      <!-- ─ 線條類型 ─ -->
      <section>
        <label class="sec-label">線條類型</label>
        <div class="grid grid-cols-2 gap-1.5">
          <button
            v-for="t in EDGE_LINE_TYPES" :key="t.id"
            class="py-1.5 rounded-lg text-xs border transition text-left px-2 flex flex-col"
            :class="form.lineType === t.id ? 'bg-amber-50 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'"
            @click="form.lineType = t.id; emitUpdate()"
          >
            <span class="font-medium">{{ t.label }}</span>
            <span class="text-gray-400 text-[10px]">{{ t.desc }}</span>
          </button>
        </div>
      </section>

      <!-- ─ 十六色卡 ─ -->
      <section>
        <label class="sec-label">顏色（點色卡選取，點名稱可命名）</label>
        <div class="grid grid-cols-4 gap-1.5 mb-2">
          <button
            v-for="c in EDGE_COLORS" :key="c"
            class="w-full aspect-square rounded-md border-2 transition hover:scale-110"
            :style="{ background: c, borderColor: form.color === c ? '#1f2937' : 'transparent' }"
            :title="colorLegend[c] || c"
            @click="form.color = c; emitUpdate()"
          />
        </div>
        <!-- Name input for selected color -->
        <div v-if="form.color" class="flex items-center gap-2">
          <div class="w-5 h-5 rounded flex-shrink-0" :style="{ background: form.color }" />
          <input
            :value="colorLegend[form.color] || ''"
            class="flex-1 border border-gray-200 rounded-lg px-2 py-1 text-xs outline-none focus:border-amber-400"
            placeholder="為此顏色命名…"
            @input="e => updateColorName(form.color, (e.target as HTMLInputElement).value)"
          />
        </div>
      </section>

      <!-- ─ 線條樣式 ─ -->
      <section>
        <label class="sec-label">線條樣式（可命名）</label>
        <div class="space-y-1.5">
          <div
            v-for="s in EDGE_DASH_STYLES" :key="s.id"
            class="flex items-center gap-2 rounded-lg border px-2 py-1.5 cursor-pointer transition"
            :class="form.dashStyleId === s.id ? 'bg-amber-50 border-amber-300' : 'border-gray-200 hover:border-gray-300'"
            @click="form.dashStyleId = s.id; form.strokeDasharray = s.dasharray; emitUpdate()"
          >
            <!-- Line preview -->
            <svg width="36" height="10" class="flex-shrink-0">
              <line x1="0" y1="5" x2="36" y2="5"
                stroke="#374151" stroke-width="2"
                :stroke-dasharray="s.dasharray || ''" />
            </svg>
            <span class="text-xs text-gray-600 flex-1">{{ lineStyleLegend[s.id] || s.label }}</span>
            <input
              :value="lineStyleLegend[s.id] || ''"
              class="w-20 border border-gray-100 rounded px-1.5 py-0.5 text-xs outline-none focus:border-amber-400 bg-white"
              placeholder="自訂名稱"
              @click.stop
              @input="e => updateLineStyleName(s.id, (e.target as HTMLInputElement).value)"
            />
          </div>
        </div>
      </section>

      <!-- ─ 線條粗細 ─ -->
      <section>
        <label class="sec-label">線條粗細（{{ form.strokeWidth }}px）</label>
        <input type="range" v-model.number="form.strokeWidth" min="1" max="8" step="0.5"
          class="w-full accent-amber-500" @input="emitUpdate" />
      </section>

      <!-- ─ 標籤 ─ -->
      <section>
        <label class="sec-label">連線標籤</label>
        <input v-model="form.label" type="text" class="field-input" placeholder="例：長子、繼室…" @input="emitUpdate" />
      </section>

      <!-- ─ 動畫 ─ -->
      <section class="flex items-center justify-between">
        <label class="sec-label mb-0">流動動畫</label>
        <button
          class="w-9 h-5 rounded-full transition relative flex-shrink-0"
          :class="form.animated ? 'bg-amber-400' : 'bg-gray-200'"
          @click="form.animated = !form.animated; emitUpdate()"
        >
          <span class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
            :class="form.animated ? 'left-4' : 'left-0.5'" />
        </button>
      </section>
    </div>

    <div class="px-4 py-3 border-t border-gray-100">
      <button class="w-full py-1.5 rounded-lg text-xs font-medium text-red-500 border border-red-200 hover:bg-red-50 transition"
        @click="$emit('delete')">刪除連線</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Edge } from '@vue-flow/core'
import { EDGE_COLORS, EDGE_DASH_STYLES, EDGE_LINE_TYPES } from '~/composables/useGenealogyStyles'

const props = defineProps<{
  edge: Edge
  colorLegend: Record<string, string>
  lineStyleLegend: Record<string, string>
}>()

const emit = defineEmits<{
  update: [data: Record<string, any>]
  delete: []
  close: []
  updateColorLegend: [hex: string, name: string]
  updateLineStyleLegend: [id: string, name: string]
}>()

const form = reactive({
  lineType: 'smoothstep',
  color: '#6b7280',
  dashStyleId: 'solid',
  strokeDasharray: '',
  strokeWidth: 2,
  label: '',
  animated: false,
})

watch(() => props.edge, (edge) => {
  if (!edge) return
  const dash = EDGE_DASH_STYLES.find(s => s.dasharray === (edge.data?.strokeDasharray || '')) ?? EDGE_DASH_STYLES[0]
  Object.assign(form, {
    lineType:         edge.data?.lineType       || edge.type || 'smoothstep',
    color:            edge.data?.color          || '#6b7280',
    dashStyleId:      edge.data?.dashStyleId    || dash.id,
    strokeDasharray:  edge.data?.strokeDasharray || '',
    strokeWidth:      edge.data?.strokeWidth    || 2,
    label:            (edge.label as string)    || '',
    animated:         edge.animated             || false,
  })
}, { immediate: true })

function emitUpdate() {
  emit('update', { ...form })
}

function updateColorName(hex: string, name: string) {
  emit('updateColorLegend', hex, name)
}
function updateLineStyleName(id: string, name: string) {
  emit('updateLineStyleLegend', id, name)
}
</script>

<style scoped>
.sec-label { @apply block text-xs font-medium text-gray-500 mb-1.5; }
.field-input { @apply w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 outline-none focus:border-amber-400 transition; }
</style>
