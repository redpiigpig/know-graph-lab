<template>
  <path
    :id="id"
    class="vue-flow__edge-path"
    :d="pathD"
    fill="none"
    :style="style"
    :marker-end="markerEnd"
    :marker-start="markerStart"
  />
</template>

<script setup lang="ts">
import type { EdgeProps } from '@vue-flow/core'

const props = defineProps<EdgeProps>()

const pathD = computed(() => {
  const midY = (props.sourceY + props.targetY) / 2
  return `M ${props.sourceX},${props.sourceY} L ${props.sourceX},${midY} L ${props.targetX},${midY} L ${props.targetX},${props.targetY}`
})
</script>
