<template>
  <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-3 sm:p-4">
    <!-- 頂部：當前年份 + 時代名 + 輸入框 -->
    <div class="flex items-center gap-3 mb-3 flex-wrap">
      <div class="flex items-baseline gap-2">
        <span class="text-xs text-gray-400 leading-none">當前年份</span>
        <span class="text-2xl font-bold text-gray-900 tabular-nums leading-none">{{ formatYear(modelValue) }}</span>
      </div>

      <div v-if="currentEpoch" class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 border border-amber-200 rounded-md">
        <span class="text-[11px] text-amber-700 font-medium">{{ currentEpoch.label_zh }}</span>
        <span v-if="currentEpoch.label_en" class="text-[10px] text-amber-500">{{ currentEpoch.label_en }}</span>
      </div>

      <div class="ml-auto flex items-center gap-1.5">
        <label class="text-[11px] text-gray-400">跳至</label>
        <div class="flex items-center bg-gray-50 border border-gray-200 rounded-md overflow-hidden">
          <input
            v-model.number="inputYear"
            type="number"
            :min="YEAR_MIN"
            :max="YEAR_MAX"
            class="w-20 px-2 py-1 bg-transparent text-sm text-gray-800 tabular-nums focus:outline-none"
            placeholder="2026"
            @keydown.enter="applyInput"
          />
          <select
            v-model="inputEra"
            class="px-1.5 py-1 bg-gray-100 border-l border-gray-200 text-xs text-gray-700 focus:outline-none cursor-pointer"
          >
            <option value="CE">公元</option>
            <option value="BCE">公元前</option>
          </select>
          <button
            @click="applyInput"
            class="px-2.5 py-1 bg-gray-700 text-white text-xs hover:bg-gray-900 transition"
          >前往</button>
        </div>
      </div>
    </div>

    <!-- 滑桿本體 -->
    <div class="relative">
      <input
        :value="modelValue"
        type="range"
        :min="YEAR_MIN"
        :max="YEAR_MAX"
        step="1"
        class="w-full timeline-slider"
        @input="onSlide($event)"
      />

      <!-- Epoch 刻度標記（疊在滑桿上） -->
      <div class="absolute inset-x-0 -bottom-1 pointer-events-none">
        <div class="relative h-3">
          <span
            v-for="e in EPOCHS"
            :key="e.year"
            class="absolute top-0 w-px h-2 bg-gray-300"
            :style="{ left: `${tickPercent(e.year)}%` }"
          />
        </div>
      </div>
    </div>

    <!-- 預設快照按鈕（横向捲動） -->
    <div class="mt-3 flex items-center gap-2">
      <div class="text-[11px] text-gray-400 flex-shrink-0">快照</div>
      <div class="flex-1 overflow-x-auto -mx-1 px-1 scrollbar-thin">
        <div class="flex items-center gap-1.5 min-w-min">
          <button
            v-for="e in EPOCHS"
            :key="`btn-${e.year}`"
            @click="jumpTo(e.year)"
            class="flex-shrink-0 px-2 py-1 text-[10px] rounded-md border whitespace-nowrap transition"
            :class="modelValue === e.year
              ? 'bg-amber-500 border-amber-500 text-white font-medium'
              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-400 hover:text-gray-900'"
            :title="e.note"
          >
            <span class="tabular-nums">{{ formatYearShort(e.year) }}</span>
            <span class="text-gray-400 mx-0.5" :class="modelValue === e.year ? 'text-amber-100' : ''">·</span>
            <span>{{ e.label_zh }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  EPOCHS,
  YEAR_MIN,
  YEAR_MAX,
  formatYear,
  formatYearShort,
  epochAt,
} from '~/data/maps/historical-epochs'

const props = defineProps<{ modelValue: number }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: number): void }>()

const currentEpoch = computed(() => epochAt(props.modelValue))

const inputEra = ref<'CE' | 'BCE'>(props.modelValue < 0 ? 'BCE' : 'CE')
const inputYear = ref<number>(
  props.modelValue < 0 ? -props.modelValue + 1 : props.modelValue
)

watch(() => props.modelValue, (v) => {
  if (v < 0) { inputEra.value = 'BCE'; inputYear.value = -v + 1 }
  else { inputEra.value = 'CE'; inputYear.value = v }
})

function onSlide(ev: Event) {
  const v = Number((ev.target as HTMLInputElement).value)
  if (!isNaN(v)) emit('update:modelValue', v)
}

function jumpTo(year: number) {
  emit('update:modelValue', year)
}

function applyInput() {
  let y = Number(inputYear.value)
  if (!Number.isFinite(y)) return
  if (inputEra.value === 'BCE') y = -(y - 1)  // 公元前 1 年 → 0
  y = Math.max(YEAR_MIN, Math.min(YEAR_MAX, y))
  emit('update:modelValue', y)
}

function tickPercent(year: number): number {
  return ((year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN)) * 100
}
</script>

<style scoped>
.timeline-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  background: linear-gradient(
    to right,
    #fef3c7 0%,
    #fde68a 10%,
    #fcd34d 25%,
    #fbbf24 45%,
    #f59e0b 65%,
    #d97706 85%,
    #92400e 100%
  );
  border-radius: 999px;
  outline: none;
  cursor: pointer;
}
.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid #0f172a;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  cursor: grab;
  transition: transform 100ms;
}
.timeline-slider::-webkit-slider-thumb:active { cursor: grabbing; transform: scale(1.15); }
.timeline-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid #0f172a;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  cursor: grab;
}
.scrollbar-thin::-webkit-scrollbar { height: 4px; }
.scrollbar-thin::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 999px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
</style>
