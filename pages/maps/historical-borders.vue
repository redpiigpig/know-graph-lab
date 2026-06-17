<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="歷史國界地圖" :back="{ to: '/maps', label: '地圖繪製' }" container-class="max-w-full">
      <template #actions>
        <span class="hidden sm:inline text-xs text-gray-400">Historical State Borders</span>
        <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
          <button
            @click="view = 'map'"
            class="px-3 py-1 text-xs rounded-md transition"
            :class="view === 'map' ? 'bg-white text-gray-900 shadow-sm font-medium' : 'text-gray-500 hover:text-gray-800'"
          >
            🗺️ 地圖
          </button>
          <button
            @click="view = 'list'"
            class="px-3 py-1 text-xs rounded-md transition"
            :class="view === 'list' ? 'bg-white text-gray-900 shadow-sm font-medium' : 'text-gray-500 hover:text-gray-800'"
          >
            📋 國家列表
          </button>
        </div>
      </template>
    </AppHeader>

    <div v-if="view === 'map'" class="flex-1 flex flex-col p-4 sm:p-6 gap-3">
      <div class="max-w-[1400px] w-full mx-auto flex-1 min-h-[420px]">
        <HistoricalBordersMap
          :current-year="currentYear"
          :highlight-name="mapHighlight"
          @locate-in-list="onLocateInList"
        />
      </div>
      <div class="max-w-[1400px] w-full mx-auto">
        <TimeAxis v-model="currentYear" />
      </div>
    </div>

    <div v-else class="flex-1 p-4 sm:p-6 overflow-y-auto">
      <div class="max-w-7xl mx-auto">
        <HistoricalStateList
          :highlight-name="listHighlight"
          @locate-on-map="onLocateOnMap"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HistoricalBordersMap from '~/components/maps/HistoricalBordersMap.vue'
import HistoricalStateList from '~/components/maps/HistoricalStateList.vue'
import TimeAxis from '~/components/maps/TimeAxis.vue'

definePageMeta({ middleware: 'auth' })
useHead({ title: '歷史國界地圖 — Know Graph Lab' })

const view = ref<'map' | 'list'>('map')
const currentYear = ref(-1500)
const mapHighlight = ref<string | null>(null)
const listHighlight = ref<string | null>(null)

function onLocateOnMap(payload: { name: string; year: number | null }) {
  view.value = 'map'
  if (typeof payload.year === 'number') currentYear.value = payload.year
  // 觸發 watch（用 nextTick 不必要，賦值 string 後 watch 即跑）
  mapHighlight.value = null
  // micro-defer 確保即使同名也能重新觸發
  setTimeout(() => { mapHighlight.value = payload.name }, 0)
}

function onLocateInList(payload: { name: string }) {
  view.value = 'list'
  listHighlight.value = null
  setTimeout(() => { listHighlight.value = payload.name }, 0)
}
</script>
