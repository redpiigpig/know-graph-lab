<template>
  <div class="flex flex-col h-full text-sm">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
      <span class="font-semibold text-gray-700">人物資訊</span>
      <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="$emit('close')">×</button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 py-3 space-y-3">

      <!-- Name -->
      <div>
        <label class="field-label">姓名</label>
        <input v-model="form.name" type="text" class="field-input" placeholder="輸入姓名"
          @input="emit('update', { name: form.name })" />
      </div>

      <!-- Gender -->
      <div>
        <label class="field-label">性別</label>
        <div class="flex gap-1.5">
          <button v-for="g in genders" :key="g.value"
            class="flex-1 py-1.5 rounded-lg text-xs font-medium border transition"
            :class="form.gender === g.value ? 'bg-amber-100 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'"
            @click="form.gender = g.value; emit('update', { gender: form.gender })"
          >{{ g.label }}</button>
        </div>
      </div>

      <!-- Generation + Years -->
      <div>
        <label class="field-label">輩分／稱謂</label>
        <input v-model="form.generation" type="text" class="field-input" placeholder="如：祖父、長子"
          @input="emit('update', { generation: form.generation })" />
      </div>
      <div class="flex gap-2">
        <div class="flex-1">
          <label class="field-label">出生年</label>
          <input v-model="form.birthYear" type="text" class="field-input" placeholder="如 1920"
            @input="emit('update', { birthYear: form.birthYear })" />
        </div>
        <div class="flex-1">
          <label class="field-label">卒年</label>
          <input v-model="form.deathYear" type="text" class="field-input" placeholder="如 1985"
            @input="emit('update', { deathYear: form.deathYear })" />
        </div>
      </div>

      <!-- Node shape -->
      <div>
        <label class="field-label">節點形狀</label>
        <div class="flex gap-2">
          <button class="flex-1 py-1.5 rounded-lg text-xs font-medium border transition"
            :class="form.shape === 'rectangle' ? 'bg-amber-100 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'"
            @click="form.shape = 'rectangle'; emit('update', { shape: 'rectangle' })"
          >▭ 方形</button>
          <button class="flex-1 py-1.5 rounded-lg text-xs font-medium border transition"
            :class="form.shape === 'circle' ? 'bg-amber-100 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'"
            @click="form.shape = 'circle'; emit('update', { shape: 'circle' })"
          >◯ 圓形</button>
        </div>
      </div>

      <!-- ─ Border styles (8 options) ─ -->
      <div>
        <label class="field-label">框線樣式（8 種）</label>
        <div class="grid grid-cols-4 gap-1.5">
          <button
            v-for="bs in BORDER_STYLES" :key="bs.id"
            class="h-9 rounded flex items-center justify-center transition"
            :class="form.borderStyleId === bs.id ? 'bg-amber-50 ring-2 ring-amber-400' : 'bg-gray-50 hover:bg-gray-100'"
            :title="bs.label"
            @click="form.borderStyleId = bs.id; emit('update', { borderStyleId: bs.id })"
          >
            <div
              class="w-7 h-7 flex items-center justify-center"
              :style="{
                borderWidth: bs.borderWidth + 'px',
                borderStyle: bs.borderStyle,
                borderRadius: bs.borderRadius + 'px',
                borderColor: form.borderColor || '#374151',
              }"
            />
          </button>
        </div>
        <p class="text-[10px] text-gray-400 mt-1">{{ currentBorderStyle?.label }}</p>
      </div>

      <!-- Border color -->
      <div>
        <label class="field-label">框線顏色</label>
        <div class="grid grid-cols-8 gap-1 mb-1.5">
          <button
            v-for="c in EDGE_COLORS" :key="c"
            class="w-full aspect-square rounded border-2 transition hover:scale-110"
            :style="{ background: c, borderColor: form.borderColor === c ? '#1f2937' : 'transparent' }"
            @click="form.borderColor = c; emit('update', { borderColor: c })"
          />
        </div>
        <div class="flex items-center gap-2">
          <input type="color" v-model="form.borderColor"
            class="w-7 h-7 rounded cursor-pointer border border-gray-200"
            @input="emit('update', { borderColor: form.borderColor })" />
          <button class="text-xs text-gray-400 hover:text-gray-600"
            @click="form.borderColor = '#d1d5db'; emit('update', { borderColor: '#d1d5db' })">重設預設</button>
        </div>
      </div>

      <!-- BG color -->
      <div>
        <label class="field-label">填充顏色</label>
        <div class="flex items-center gap-2">
          <input type="color" v-model="form.bgColor"
            class="w-7 h-7 rounded cursor-pointer border border-gray-200"
            @input="emit('update', { bgColor: form.bgColor })" />
          <button class="text-xs text-gray-400 hover:text-gray-600"
            @click="form.bgColor = ''; emit('update', { bgColor: '' })">重設</button>
        </div>
      </div>

      <!-- Notes -->
      <div>
        <label class="field-label">備注</label>
        <textarea v-model="form.notes" class="field-input resize-none h-14" placeholder="額外資訊…"
          @input="emit('update', { notes: form.notes })" />
      </div>
    </div>

    <div class="px-4 py-3 border-t border-gray-100">
      <button class="w-full py-1.5 rounded-lg text-xs font-medium text-red-500 border border-red-200 hover:bg-red-50 transition"
        @click="$emit('delete')">刪除節點</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Node } from '@vue-flow/core'
import { BORDER_STYLES, EDGE_COLORS } from '~/composables/useGenealogyStyles'

const props = defineProps<{ node: Node }>()
const emit = defineEmits<{
  update: [data: Record<string, any>]
  delete: []
  close: []
}>()

const genders = [
  { value: 'male',    label: '♂ 男' },
  { value: 'female',  label: '♀ 女' },
  { value: 'unknown', label: '？不明' },
]

const form = reactive({
  name: '', gender: 'unknown' as 'male'|'female'|'unknown',
  generation: '', birthYear: '', deathYear: '', notes: '',
  shape: 'rectangle' as 'circle'|'rectangle',
  borderStyleId: 'solid-md', borderColor: '#d1d5db', bgColor: '',
})

const currentBorderStyle = computed(() => BORDER_STYLES.find(s => s.id === form.borderStyleId))

watch(() => props.node, (node) => {
  if (!node) return
  Object.assign(form, {
    name:          node.data.name          || '',
    gender:        node.data.gender        || 'unknown',
    generation:    node.data.generation    || '',
    birthYear:     node.data.birthYear     || '',
    deathYear:     node.data.deathYear     || '',
    notes:         node.data.notes         || '',
    shape:         node.data.shape         || 'rectangle',
    borderStyleId: node.data.borderStyleId || 'solid-md',
    borderColor:   node.data.borderColor   || '#d1d5db',
    bgColor:       node.data.bgColor       || '',
  })
}, { immediate: true })
</script>

<style scoped>
.field-label { @apply block text-xs text-gray-500 mb-1; }
.field-input { @apply w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 outline-none focus:border-amber-400 transition; }
</style>
