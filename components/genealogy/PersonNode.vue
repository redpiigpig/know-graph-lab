<template>
  <div
    class="person-node relative flex flex-col items-center justify-center cursor-pointer transition-all duration-150"
    :class="[
      data.shape === 'circle' ? 'w-[110px] h-[110px]' : 'px-4 py-2.5 min-w-[120px]',
      selected ? 'shadow-lg' : 'shadow-sm hover:shadow-md',
    ]"
    :style="nodeStyle"
  >
    <!-- Handles – always visible rings -->
    <Handle id="top"    type="target" :position="Position.Top"    class="gn-handle" />
    <Handle id="bottom" type="source" :position="Position.Bottom" class="gn-handle" />
    <Handle id="left"   type="source" :position="Position.Left"   class="gn-handle" />
    <Handle id="right"  type="source" :position="Position.Right"  class="gn-handle" />

    <!-- Gender dot -->
    <div class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full" :class="genderDot" />

    <!-- Content -->
    <div class="text-center w-full px-1 select-none">
      <div v-if="data.generation" class="text-[10px] text-gray-400 leading-none mb-0.5 truncate">
        {{ data.generation }}
      </div>

      <!-- Inline name edit when selected -->
      <input
        v-if="selected"
        ref="nameInput"
        :value="data.name"
        placeholder="姓名"
        class="text-sm font-semibold text-center bg-transparent outline-none border-none w-full text-gray-900 placeholder-gray-300"
        :style="{ maxWidth: data.shape === 'circle' ? '90px' : '140px' }"
        @input="e => $emit('updateName', id, (e.target as HTMLInputElement).value)"
        @keydown.enter="($event.target as HTMLInputElement).blur()"
        @mousedown.stop
        @click.stop
      />
      <div v-else class="text-sm font-semibold text-gray-900 leading-tight truncate max-w-[110px]">
        {{ data.name || '未命名' }}
      </div>

      <div v-if="data.birthYear || data.deathYear" class="text-[10px] text-gray-400 mt-0.5 leading-none">
        {{ data.birthYear || '' }}{{ data.deathYear ? '—' + data.deathYear : (data.birthYear ? '—' : '') }}
      </div>
      <div v-if="data.notes" class="text-[10px] text-gray-500 mt-0.5 truncate max-w-[110px]">
        {{ data.notes }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { BORDER_STYLES } from '~/composables/useGenealogyStyles'

const props = defineProps<{
  id: string
  data: {
    name: string
    gender: 'male' | 'female' | 'unknown'
    generation?: string
    birthYear?: string
    deathYear?: string
    notes?: string
    shape?: 'circle' | 'rectangle'
    bgColor?: string
    borderStyleId?: string
    borderColor?: string
  }
  selected: boolean
}>()

defineEmits<{ updateName: [id: string, name: string] }>()

const nameInput = ref<HTMLInputElement>()

watch(() => props.selected, (val) => {
  if (val) nextTick(() => nameInput.value?.focus())
})

const borderStyle = computed(() => {
  return BORDER_STYLES.find(s => s.id === props.data.borderStyleId) ?? BORDER_STYLES[1]
})

const genderBg = computed(() => {
  if (props.data.bgColor) return props.data.bgColor
  if (props.data.gender === 'male') return '#eff6ff'
  if (props.data.gender === 'female') return '#fdf2f8'
  return '#f9fafb'
})

const genderDot = computed(() => {
  if (props.data.gender === 'male') return 'bg-blue-400'
  if (props.data.gender === 'female') return 'bg-pink-400'
  return 'bg-gray-300'
})

const nodeStyle = computed(() => ({
  backgroundColor: genderBg.value,
  borderWidth: borderStyle.value.borderWidth + 'px',
  borderStyle: borderStyle.value.borderStyle,
  borderRadius: borderStyle.value.borderRadius + 'px',
  borderColor: props.data.borderColor || (props.selected ? '#f59e0b' : '#d1d5db'),
  outline: props.selected ? '2px solid #fbbf24' : 'none',
  outlineOffset: '2px',
}))
</script>

<style>
/* Handles – always shown, amber rings */
.gn-handle.vue-flow__handle {
  width: 12px !important;
  height: 12px !important;
  background: white !important;
  border: 2px solid #f59e0b !important;
  border-radius: 50% !important;
  opacity: 0.55;
  transition: opacity 0.15s, transform 0.15s;
  z-index: 10;
}
.gn-handle.vue-flow__handle:hover {
  opacity: 1 !important;
  transform: scale(1.4) !important;
  cursor: crosshair !important;
}
</style>
