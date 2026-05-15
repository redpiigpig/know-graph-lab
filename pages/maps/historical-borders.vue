<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/maps" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">歷史國界地圖</span>
      <span class="hidden sm:inline text-xs text-gray-400 ml-1">Historical State Borders</span>

      <div class="ml-auto flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
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
    </nav>

    <div v-if="view === 'map'" class="flex-1 flex flex-col p-4 sm:p-6 gap-3">
      <div class="max-w-[1400px] w-full mx-auto flex-1 min-h-[420px]">
        <HistoricalBordersMap :current-year="currentYear" />
      </div>
      <div class="max-w-[1400px] w-full mx-auto">
        <TimeAxis v-model="currentYear" />
      </div>
    </div>

    <div v-else class="flex-1 p-4 sm:p-6 overflow-y-auto">
      <div class="max-w-7xl mx-auto">
        <HistoricalStateList />
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
</script>
