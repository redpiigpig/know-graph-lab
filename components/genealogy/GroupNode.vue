<template>
  <div
    class="group-node w-full h-full rounded-2xl border-2 border-dashed relative"
    :class="selected ? 'border-amber-400' : 'border-gray-300'"
    :style="{ backgroundColor: data.color || 'rgba(245,158,11,0.06)' }"
  >
    <NodeResizer
      :min-width="120"
      :min-height="80"
      :is-visible="selected"
      :line-class="'resize-line'"
      :handle-class="'resize-handle'"
    />
    <div
      class="absolute -top-3 left-3 px-2 py-0.5 rounded text-xs font-medium text-gray-500 bg-white border border-gray-200"
    >
      {{ data.label || '群組' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { NodeResizer } from '@vue-flow/node-resizer'

defineProps<{
  id: string
  data: { label?: string; color?: string }
  selected: boolean
}>()
</script>

<style scoped>
:deep(.resize-line) {
  border-color: #f59e0b !important;
}
:deep(.resize-handle) {
  background-color: #f59e0b !important;
  border-color: white !important;
  width: 8px !important;
  height: 8px !important;
}
</style>
