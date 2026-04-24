<template>
  <div
    v-if="hasContent"
    class="absolute bottom-14 left-2 z-20 bg-white border border-gray-200 rounded-xl shadow-md p-2.5 min-w-[130px] max-w-[180px] pointer-events-none"
  >
    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">圖例</p>

    <!-- Named colors -->
    <div v-if="namedColors.length" class="space-y-1 mb-1.5">
      <div v-for="item in namedColors" :key="item.color" class="flex items-center gap-1.5">
        <div class="w-3.5 h-3.5 rounded-sm flex-shrink-0" :style="{ background: item.color }" />
        <span class="text-[11px] text-gray-700 truncate leading-none">{{ item.name }}</span>
      </div>
    </div>

    <!-- Divider -->
    <div v-if="namedColors.length && namedLineStyles.length" class="border-t border-gray-100 my-1.5" />

    <!-- Named line styles -->
    <div v-if="namedLineStyles.length" class="space-y-1">
      <div v-for="item in namedLineStyles" :key="item.id" class="flex items-center gap-1.5">
        <svg width="28" height="8" class="flex-shrink-0">
          <line x1="0" y1="4" x2="28" y2="4" stroke="#374151" stroke-width="1.5"
            :stroke-dasharray="item.dasharray" />
        </svg>
        <span class="text-[11px] text-gray-700 truncate leading-none">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { EDGE_DASH_STYLES } from '~/composables/useGenealogyStyles'

const props = defineProps<{
  colorLegend: Record<string, string>
  lineStyleLegend: Record<string, string>
}>()

const namedColors = computed(() =>
  Object.entries(props.colorLegend)
    .filter(([, name]) => name.trim())
    .map(([color, name]) => ({ color, name }))
)

const namedLineStyles = computed(() =>
  EDGE_DASH_STYLES
    .filter(s => props.lineStyleLegend[s.id]?.trim())
    .map(s => ({ id: s.id, dasharray: s.dasharray, name: props.lineStyleLegend[s.id] }))
)

const hasContent = computed(() => namedColors.value.length > 0 || namedLineStyles.value.length > 0)
</script>
