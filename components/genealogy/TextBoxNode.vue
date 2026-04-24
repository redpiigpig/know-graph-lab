<template>
  <div
    class="text-box-node relative min-w-[120px] min-h-[40px] px-3 py-2 rounded-lg border-2 border-dashed cursor-text select-none transition-all duration-150"
    :class="selected ? 'border-amber-400 bg-amber-50' : 'border-gray-300 bg-white hover:border-gray-400'"
    @dblclick.stop="startEdit"
  >
    <Handle id="top" type="source" :position="Position.Top" class="handle-dot" />
    <Handle id="bottom" type="source" :position="Position.Bottom" class="handle-dot" />
    <Handle id="left" type="source" :position="Position.Left" class="handle-dot" />
    <Handle id="right" type="source" :position="Position.Right" class="handle-dot" />

    <textarea
      v-if="editing"
      ref="textareaRef"
      v-model="localText"
      class="w-full bg-transparent text-sm text-gray-700 resize-none outline-none leading-snug"
      :style="{ fontSize: data.fontSize + 'px', minHeight: '32px' }"
      @blur="stopEdit"
      @keydown.esc="stopEdit"
      @mousedown.stop
    />
    <div
      v-else
      class="text-sm text-gray-700 whitespace-pre-wrap leading-snug"
      :style="{ fontSize: data.fontSize + 'px' }"
    >
      {{ data.text || '雙擊編輯文字' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'

const props = defineProps<{
  id: string
  data: { text: string; fontSize?: number }
  selected: boolean
}>()

const emit = defineEmits<{ updateText: [id: string, text: string] }>()

const editing = ref(false)
const localText = ref(props.data.text)
const textareaRef = ref<HTMLTextAreaElement>()

function startEdit() {
  editing.value = true
  localText.value = props.data.text
  nextTick(() => textareaRef.value?.focus())
}

function stopEdit() {
  editing.value = false
  emit('updateText', props.id, localText.value)
}
</script>

<style scoped>
.handle-dot {
  width: 8px !important;
  height: 8px !important;
  background: #f59e0b !important;
  border: 2px solid white !important;
  border-radius: 50% !important;
  opacity: 0;
  transition: opacity 0.15s;
}
.text-box-node:hover .handle-dot {
  opacity: 1;
}
</style>
