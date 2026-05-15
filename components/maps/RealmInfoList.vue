<template>
  <div class="space-y-6">
    <section
      v-for="realm in REALMS"
      :key="realm.id"
      class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
    >
      <header
        class="flex items-center gap-3 px-4 py-3 border-b border-gray-100"
        :style="{ background: realm.color + '14' }"
      >
        <div
          class="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
          :style="{ background: realm.color }"
        >
          {{ realm.index }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-gray-900 text-base">
            {{ realm.name_zh }}
            <span class="text-xs text-gray-400 font-normal ml-1">({{ realm.name_en }})</span>
          </div>
        </div>
      </header>

      <div class="divide-y divide-gray-100">
        <article
          v-for="sphere in spheresByRealm(realm.id)"
          :key="sphere.id"
          class="px-4 py-3"
        >
          <div class="flex items-baseline gap-2 mb-2">
            <h3 class="text-sm font-semibold text-gray-900">{{ sphere.name_zh }}</h3>
            <span class="text-[11px] text-gray-400">{{ sphere.name_en }}</span>

            <button
              v-if="historyOf(sphere.id).length"
              @click="toggleExpand(sphere.id)"
              class="ml-auto flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-900 px-1.5 py-0.5 rounded border border-gray-200 hover:border-gray-400 transition"
              :class="expanded[sphere.id] ? 'bg-amber-50 border-amber-200 text-amber-700 hover:text-amber-900' : ''"
            >
              <span>📜</span>
              <span>歷史期間</span>
              <span class="text-gray-400">{{ historyOf(sphere.id).length }}</span>
              <span class="ml-0.5">{{ expanded[sphere.id] ? '▴' : '▾' }}</span>
            </button>
            <span v-else class="ml-auto text-[10px] text-gray-300">— 歷史資料待補 —</span>
          </div>

          <!-- 現代成員國列表 -->
          <ol class="flex flex-wrap gap-x-1 gap-y-1.5 text-xs">
            <li
              v-for="(m, idx) in sphere.members"
              :key="`${sphere.id}-${m.iso_a3}-${m.admin1 || ''}-${idx}`"
              class="inline-flex items-center"
            >
              <span v-if="idx > 0" class="text-gray-300 mx-1 select-none">→</span>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md border"
                :class="m.is_extension
                  ? 'border-dashed border-gray-300 text-gray-500 bg-gray-50'
                  : 'border-gray-200 text-gray-800 bg-white'"
              >{{ m.label }}</span>
            </li>
          </ol>

          <!-- 歷史期間展開區 -->
          <div
            v-if="expanded[sphere.id] && historyOf(sphere.id).length"
            class="mt-3 pt-3 border-t border-dashed border-gray-200"
          >
            <ol class="relative space-y-2.5">
              <!-- 縱向時間軸線 -->
              <div class="absolute left-[5px] top-1 bottom-1 w-px bg-gray-200" />

              <li
                v-for="(entry, idx) in historyOf(sphere.id)"
                :key="idx"
                class="relative pl-5"
              >
                <span
                  class="absolute left-0 top-[6px] w-[11px] h-[11px] rounded-full border-2 bg-white"
                  :class="periodActive(entry) ? 'border-amber-500' : 'border-gray-300'"
                  :style="periodActive(entry) ? { boxShadow: '0 0 0 3px rgba(245, 158, 11, 0.2)' } : {}"
                />
                <div class="flex items-baseline gap-1.5 flex-wrap">
                  <span
                    class="text-[11px] font-semibold"
                    :class="periodActive(entry) ? 'text-amber-700' : 'text-gray-700'"
                  >{{ entry.period_label }}</span>
                  <span class="text-[10px] text-gray-400 tabular-nums">
                    {{ formatYearShort(entry.year_from) }} – {{ entry.year_to >= 9999 ? '至今' : formatYearShort(entry.year_to) }}
                  </span>
                </div>
                <div v-if="entry.states?.length" class="mt-1 flex flex-wrap gap-1">
                  <span
                    v-for="(s, i) in entry.states"
                    :key="`st-${i}`"
                    class="inline-block px-1.5 py-0.5 rounded text-[10px] border border-gray-200 bg-gray-50 text-gray-700"
                  >{{ s }}</span>
                </div>
                <div v-if="entry.places?.length" class="mt-1 text-[10px] text-gray-500">
                  <span class="text-gray-400">地：</span>{{ entry.places.join('、') }}
                </div>
                <div v-if="entry.faiths?.length" class="mt-0.5 text-[10px] text-gray-500">
                  <span class="text-gray-400">信仰：</span>{{ entry.faiths.join('、') }}
                </div>
                <div v-if="entry.note" class="mt-0.5 text-[10px] text-gray-400 italic">{{ entry.note }}</div>
              </li>
            </ol>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { REALMS, spheresByRealm } from '~/data/maps/world-religions'
import { historyForSphere, type SphereHistoryEntry } from '~/data/maps/sphere-history'
import { formatYearShort } from '~/data/maps/historical-epochs'

const props = withDefaults(defineProps<{ currentYear?: number }>(), { currentYear: 2026 })

const expanded = reactive<Record<string, boolean>>({})
function toggleExpand(id: string) {
  expanded[id] = !expanded[id]
}

function historyOf(id: string): SphereHistoryEntry[] {
  return historyForSphere(id)
}

function periodActive(entry: SphereHistoryEntry): boolean {
  const y = props.currentYear
  return y >= entry.year_from && y <= entry.year_to
}
</script>
