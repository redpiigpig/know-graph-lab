<template>
  <div class="couple-node">
    <Handle id="left"   type="target" :position="Position.Left"   class="cpl-h" />
    <Handle id="right"  type="source" :position="Position.Right"  class="cpl-h" />
    <Handle id="top"    type="target" :position="Position.Top"    class="cpl-h" />
    <Handle id="bottom" type="source" :position="Position.Bottom" class="cpl-h" />
    <div class="dot" :class="data?.isMain ? 'main' : 'conc'" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
defineProps<{ id: string; data: any; selected: boolean }>()
</script>

<style scoped>
.couple-node {
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.main { background: #f43f5e; border: 2px solid #e11d48; }
.dot.conc { background: #fb7185; border: 2px solid #f43f5e; }
.cpl-h { opacity: 0 !important; width: 6px !important; height: 6px !important; }
</style>
