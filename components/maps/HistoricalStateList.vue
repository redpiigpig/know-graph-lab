<template>
  <div class="space-y-3">
    <!-- 工具列 -->
    <div class="flex items-center gap-3 flex-wrap bg-white rounded-xl border border-gray-200 p-3">
      <div class="flex items-center gap-2">
        <input
          v-model="searchText"
          type="text"
          placeholder="搜尋國名（中英文）"
          class="px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none focus:border-amber-400 w-56"
        />
        <select v-model="filterRealm" class="px-2 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none">
          <option value="">所有界域</option>
          <option value="central">中央界域</option>
          <option value="eastern">東方界域</option>
          <option value="latin-america">拉美界域</option>
          <option value="western">西方界域</option>
          <option value="asia-pacific">亞太界域</option>
          <option value="southern">南方界域</option>
          <option value="northern">北方界域</option>
          <option value="north-america">北美界域</option>
        </select>
        <select v-model="filterDetail" class="px-2 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none">
          <option value="all">全部</option>
          <option value="with">已填詳細</option>
          <option value="without">僅骨架</option>
        </select>
      </div>
      <select v-model="filterPolygon" class="px-2 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none">
        <option value="all">所有</option>
        <option value="with">有地圖 polygon</option>
        <option value="without">無 polygon</option>
      </select>
      <select v-model="filterPolity" class="px-2 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none" title="政權標準：至少酋邦／城邦／建立王權的遊牧帝國">
        <option value="state">僅政權（含酋邦）</option>
        <option value="nonstate">僅部落／文化群</option>
        <option value="all">不過濾</option>
      </select>

      <!-- 匯出按鈕 -->
      <div class="relative">
        <button
          @click="exportMenuOpen = !exportMenuOpen"
          class="px-2.5 py-1.5 text-xs text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition flex items-center gap-1"
          :title="`匯出當前 ${filteredStates.length} 條結果`"
        >
          <span>⬇ 匯出</span>
          <span class="text-[10px] text-gray-400">({{ filteredStates.length }})</span>
        </button>
        <template v-if="exportMenuOpen">
          <!-- 透明覆蓋層，點擊空白處關閉 -->
          <div class="fixed inset-0 z-10" @click="exportMenuOpen = false" />
          <div
            class="absolute right-0 top-full mt-1 z-20 bg-white border border-gray-200 rounded-md shadow-lg overflow-hidden min-w-[160px]"
          >
            <button @click="exportAs('csv'); exportMenuOpen = false" class="block w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-amber-50">
              CSV <span class="text-gray-400">（Excel/Numbers）</span>
            </button>
            <button @click="exportAs('json'); exportMenuOpen = false" class="block w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-amber-50 border-t border-gray-100">
              JSON <span class="text-gray-400">（程式可讀）</span>
            </button>
          </div>
        </template>
      </div>

      <div class="ml-auto text-xs text-gray-500 flex items-baseline gap-2">
        <span>顯示</span>
        <span class="text-base font-bold text-gray-900 tabular-nums">{{ filteredStates.length.toLocaleString() }}</span>
        <span>/ {{ allStates.length.toLocaleString() }} 條目</span>
        <span class="text-gray-300">·</span>
        <span class="text-amber-700">政權 {{ polityCount }}</span>
        <span class="text-gray-300">·</span>
        <span class="text-blue-600">有 polygon {{ polygonCount }}</span>
        <span class="text-gray-300">·</span>
        <span class="text-emerald-600">人工詳細 {{ detailCount }}</span>
        <span class="text-gray-300">·</span>
        <span class="text-purple-600" title="自動由 modern_countries × country-sphere-timeline 推斷">推斷界域 {{ inferredSphereCount }}</span>
      </div>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="bg-gray-50 text-gray-500 text-[11px]">
            <tr>
              <th class="text-left px-3 py-2 cursor-pointer hover:text-gray-900" @click="setSort('name_en')">
                國名 <SortArrow :col="'name_en'" :sort="sortKey" :dir="sortDir" />
              </th>
              <th class="text-left px-3 py-2 cursor-pointer hover:text-gray-900" @click="setSort('year_start')">
                年代 <SortArrow :col="'year_start'" :sort="sortKey" :dir="sortDir" />
              </th>
              <th class="text-left px-3 py-2">朝代／統治</th>
              <th class="text-left px-3 py-2">巔峰人口</th>
              <th class="text-left px-3 py-2">巔峰面積</th>
              <th class="text-left px-3 py-2">主要首都</th>
              <th class="text-left px-3 py-2">現代涵蓋</th>
              <th class="text-left px-3 py-2">界域</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="s in pagedStates"
              :key="s.id"
              class="hover:bg-amber-50/50 transition cursor-pointer"
              :class="!s.has_detail && 'opacity-70'"
              @click="selected = s"
            >
              <td class="px-3 py-2">
                <div class="font-medium text-gray-900">{{ s.name_zh || s.name_en }}</div>
                <div v-if="s.name_zh" class="text-[10px] text-gray-400 mt-0.5">{{ s.name_en }}</div>
                <span v-if="!s.has_detail" class="inline-block text-[9px] text-gray-400 mt-0.5">骨架</span>
              </td>
              <td class="px-3 py-2 tabular-nums text-gray-600 whitespace-nowrap">
                <div v-if="s.year_start !== null">{{ formatYearShort(s.year_start) }}</div>
                <div v-else class="text-gray-300">?</div>
                <div class="text-gray-400">
                  – <template v-if="s.year_end === null">?</template>
                  <template v-else-if="s.year_end >= 9999">至今</template>
                  <template v-else>{{ formatYearShort(s.year_end) }}</template>
                </div>
              </td>
              <td class="px-3 py-2 text-gray-600 max-w-[180px]">
                <div v-if="s.dynasties?.length" class="space-y-0.5">
                  <div v-for="(d, i) in s.dynasties.slice(0, 3)" :key="i" class="text-[10px]">· {{ d }}</div>
                  <div v-if="s.dynasties.length > 3" class="text-[9px] text-gray-400">+{{ s.dynasties.length - 3 }} 更多</div>
                </div>
                <span v-else class="text-gray-300 text-[10px]">—</span>
              </td>
              <td class="px-3 py-2 tabular-nums text-gray-600 whitespace-nowrap">
                <span v-if="s.population_peak_wan" class="font-medium">{{ formatPopulation(s.population_peak_wan) }}</span>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-3 py-2 tabular-nums text-gray-600 whitespace-nowrap">
                <span v-if="s.area_peak_wan_km2" class="font-medium">{{ formatArea(s.area_peak_wan_km2) }}</span>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-3 py-2 text-gray-600 max-w-[140px]">
                <div v-if="s.capitals?.length" class="text-[10px]">
                  {{ s.capitals.join('、') }}
                </div>
                <span v-else class="text-gray-300 text-[10px]">—</span>
              </td>
              <td class="px-3 py-2 text-gray-600">
                <div v-if="s.modern_countries && s.modern_countries.length" class="flex flex-wrap gap-0.5">
                  <span
                    v-for="iso in s.modern_countries.slice(0, 6)"
                    :key="iso"
                    class="inline-block px-1 py-0.5 rounded bg-gray-100 text-[9px]"
                  >{{ countryZh(iso) }}</span>
                  <span v-if="s.modern_countries.length > 6" class="text-[9px] text-gray-400">+{{ s.modern_countries.length - 6 }}</span>
                </div>
                <div v-else-if="s.continents && s.continents.length" class="flex flex-wrap gap-0.5">
                  <span
                    v-for="c in s.continents"
                    :key="c"
                    class="inline-block px-1 py-0.5 rounded bg-gray-50 text-[9px] text-gray-500 italic"
                  >{{ c }}</span>
                </div>
                <span v-else class="text-gray-300 text-[10px]">—</span>
              </td>
              <td class="px-3 py-2">
                <span
                  v-if="s.realm_id"
                  class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px]"
                  :style="{ background: realmColor(s.realm_id) + '20', color: realmColor(s.realm_id) }"
                  :class="s.has_inferred_sphere ? 'border border-dashed border-purple-300' : ''"
                  :title="s.has_inferred_sphere ? '由 modern_countries 自動推斷' : '人工標註'"
                >
                  {{ realmName(s.realm_id) }}
                  <span v-if="s.has_inferred_sphere" class="text-purple-500 text-[8px]">推</span>
                </span>
                <span v-else class="text-gray-300 text-[10px]">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-3 py-3 border-t border-gray-100 bg-gray-50">
        <button @click="page = 1" :disabled="page === 1" class="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30">⟪ 第一頁</button>
        <button @click="page = Math.max(1, page - 1)" :disabled="page === 1" class="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30">← 上頁</button>
        <span class="text-xs text-gray-700">
          第 <span class="font-semibold tabular-nums">{{ page }}</span> /
          <span class="tabular-nums">{{ totalPages }}</span> 頁
          <span class="text-gray-400 ml-1">（每頁 {{ pageSize }} 國）</span>
        </span>
        <button @click="page = Math.min(totalPages, page + 1)" :disabled="page === totalPages" class="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30">下頁 →</button>
        <button @click="page = totalPages" :disabled="page === totalPages" class="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30">最末頁 ⟫</button>
      </div>
    </div>

    <!-- 詳細彈窗 -->
    <div v-if="selected" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selected = null">
      <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6 shadow-2xl">
        <div class="flex items-start justify-between gap-4 mb-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">{{ selected.name_zh || selected.name_en }}</h2>
            <div v-if="selected.name_zh" class="text-sm text-gray-500 mt-1">{{ selected.name_en }}</div>
            <div v-if="selected.qid" class="text-[10px] text-gray-400 mt-1">
              <a :href="`https://www.wikidata.org/wiki/${selected.qid}`" target="_blank" rel="noopener" class="hover:text-blue-600">Wikidata: {{ selected.qid }} ↗</a>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="selected.has_polygon"
              @click="locateOnMap(selected)"
              class="px-2.5 py-1 text-xs bg-amber-500 text-white rounded-md hover:bg-amber-600 transition flex items-center gap-1"
              :title="`切到地圖視圖並跳到 ${selected.year_start ?? '?'}`"
            >🗺️ 在地圖查看</button>
            <button @click="selected = null" class="text-gray-400 hover:text-gray-900 text-2xl">×</button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-4 text-xs">
          <div>
            <div class="text-gray-400 mb-0.5">存在年代</div>
            <div class="font-medium tabular-nums">
              <template v-if="selected.year_start !== null">{{ formatYearShort(selected.year_start) }}</template>
              <template v-else>?</template>
              –
              <template v-if="selected.year_end === null">?</template>
              <template v-else-if="selected.year_end >= 9999">至今</template>
              <template v-else>{{ formatYearShort(selected.year_end) }}</template>
            </div>
          </div>
          <div>
            <div class="text-gray-400 mb-0.5">所屬界域</div>
            <div class="font-medium">{{ selected.realm_id ? realmName(selected.realm_id) : '—' }}</div>
          </div>
          <div v-if="selected.population_peak_wan">
            <div class="text-gray-400 mb-0.5">巔峰人口</div>
            <div class="font-medium tabular-nums">{{ formatPopulation(selected.population_peak_wan) }}</div>
          </div>
          <div v-if="selected.area_peak_wan_km2">
            <div class="text-gray-400 mb-0.5">巔峰面積</div>
            <div class="font-medium tabular-nums">{{ formatArea(selected.area_peak_wan_km2) }}</div>
          </div>
        </div>

        <div v-if="selected.intro" class="mb-4 text-sm text-gray-700 leading-relaxed">{{ selected.intro }}</div>

        <div v-if="selected.dynasties?.length" class="mb-3">
          <div class="text-xs text-gray-400 mb-1">統治家族／朝代</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="d in selected.dynasties" :key="d" class="px-2 py-0.5 rounded-md bg-amber-50 border border-amber-200 text-xs">{{ d }}</span>
          </div>
        </div>

        <div v-if="selected.capitals?.length" class="mb-3">
          <div class="text-xs text-gray-400 mb-1">主要首都／重要城市</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="c in selected.capitals" :key="c" class="px-2 py-0.5 rounded-md bg-gray-50 border border-gray-200 text-xs">{{ c }}</span>
          </div>
        </div>

        <div v-if="selected.religions?.length" class="mb-3">
          <div class="text-xs text-gray-400 mb-1">主要宗教／信仰</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="r in selected.religions" :key="r" class="px-2 py-0.5 rounded-md bg-blue-50 border border-blue-200 text-xs">{{ r }}</span>
          </div>
        </div>

        <div v-if="selected.modern_countries?.length" class="mb-3">
          <div class="text-xs text-gray-400 mb-1">涵蓋現代國家 ({{ selected.modern_countries.length }})</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="iso in selected.modern_countries" :key="iso" class="px-2 py-0.5 rounded-md bg-gray-100 text-xs">{{ countryZh(iso) }} <span class="text-gray-400">({{ iso }})</span></span>
          </div>
        </div>

        <div v-if="selected.snapshots?.length" class="text-[10px] text-gray-400 mt-3">
          出現於 snapshot: {{ selected.snapshots.map(formatYearShort).join(', ') }}
        </div>

        <div v-if="!selected.has_detail" class="mt-4 p-2 bg-amber-50 border border-amber-200 rounded-md text-xs text-amber-800">
          📋 此國家僅有骨架資料（年代＋現代涵蓋國家）。中文名／朝代／人口／面積等待補。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, h } from 'vue'
import {
  type HistoricalState,
  type StateSkeleton,
  type WikidataState,
  type SphereInferenceEntry,
  STATE_DETAILS,
  mergeStates,
} from '~/data/maps/historical-states-db'
import { formatYearShort } from '~/data/maps/historical-epochs'
import { REALMS, COUNTRY_NAME_ZH, realmById } from '~/data/maps/world-religions'

const props = defineProps<{ highlightName?: string | null }>()
const emit = defineEmits<{ (e: 'locateOnMap', payload: { name: string; year: number | null }): void }>()

const allStates = ref<HistoricalState[]>([])
const polityClassification = ref<Record<string, { is_state: boolean }>>({})

const searchText = ref('')
const filterRealm = ref('')
const filterDetail = ref<'all' | 'with' | 'without'>('all')
const filterPolygon = ref<'all' | 'with' | 'without'>('all')
const filterPolity = ref<'state' | 'nonstate' | 'all'>('state')
const sortKey = ref<'name_en' | 'year_start'>('year_start')
const sortDir = ref<'asc' | 'desc'>('asc')
const page = ref(1)
const pageSize = 50
const selected = ref<HistoricalState | null>(null)
const exportMenuOpen = ref(false)

const detailCount = computed(() => allStates.value.filter(s => s.has_detail).length)
const polygonCount = computed(() => allStates.value.filter(s => s.has_polygon).length)
const inferredSphereCount = computed(() => allStates.value.filter(s => s.has_inferred_sphere).length)

// 政權判定：用 polygon-classifications.json（is_state）；wikidata-only 條目（無 polygon）若有 inception_year 視為政權
function isStatePolity(s: HistoricalState): boolean {
  const cls = polityClassification.value[s.name_en]
  if (cls) return cls.is_state
  // 沒分類資料的（多為 wikidata-only）— 有起始年份就視為政權
  return s.year_start !== null && s.year_start !== undefined
}

const polityCount = computed(() => allStates.value.filter(isStatePolity).length)

const filteredStates = computed(() => {
  let list = allStates.value
  if (searchText.value.trim()) {
    const q = searchText.value.trim().toLowerCase()
    list = list.filter(s =>
      s.name_en.toLowerCase().includes(q) ||
      (s.name_zh && s.name_zh.toLowerCase().includes(q))
    )
  }
  if (filterRealm.value) {
    list = list.filter(s => s.realm_id === filterRealm.value)
  }
  if (filterDetail.value === 'with') list = list.filter(s => s.has_detail)
  if (filterDetail.value === 'without') list = list.filter(s => !s.has_detail)
  if (filterPolygon.value === 'with') list = list.filter(s => s.has_polygon)
  if (filterPolygon.value === 'without') list = list.filter(s => !s.has_polygon)
  if (filterPolity.value === 'state') list = list.filter(s => isStatePolity(s))
  if (filterPolity.value === 'nonstate') list = list.filter(s => !isStatePolity(s))
  // sort
  list = [...list].sort((a, b) => {
    const dir = sortDir.value === 'asc' ? 1 : -1
    if (sortKey.value === 'name_en') return dir * a.name_en.localeCompare(b.name_en)
    const ay = a.year_start ?? 99999
    const by = b.year_start ?? 99999
    return dir * ((ay - by) || a.name_en.localeCompare(b.name_en))
  })
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredStates.value.length / pageSize)))

const pagedStates = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredStates.value.slice(start, start + pageSize)
})

function setSort(key: 'name_en' | 'year_start') {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortKey.value = key; sortDir.value = 'asc' }
  page.value = 1
}

function locateOnMap(s: HistoricalState) {
  emit('locateOnMap', { name: s.name_en, year: s.year_start })
  selected.value = null
}

function realmColor(id: string): string {
  return realmById(id as any)?.color || '#999'
}
function realmName(id: string): string {
  return realmById(id as any)?.name_zh || id
}
function countryZh(iso: string): string {
  return COUNTRY_NAME_ZH[iso] || iso
}
function formatPopulation(wan: number): string {
  if (wan >= 1e4) return `${(wan / 1e4).toFixed(1)} 億人`
  if (wan >= 1e3) return `${(wan / 1e3).toFixed(1)} 千萬人`
  return `${wan} 萬人`
}
function formatArea(wan_km2: number): string {
  if (wan_km2 >= 100) return `${wan_km2.toLocaleString()} 萬 km²`
  return `${wan_km2} 萬 km²`
}

// ===== 匯出 =====
function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: `${mime};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function exportAs(format: 'csv' | 'json') {
  const list = filteredStates.value
  const ts = new Date().toISOString().slice(0, 10)
  const tag = filterPolity.value === 'state' ? '政權' : filterPolity.value === 'nonstate' ? '非政權' : '全部'
  const stem = `historical-states_${tag}_${list.length}_${ts}`

  if (format === 'json') {
    const payload = list.map(s => ({
      id: s.id,
      name_en: s.name_en,
      name_zh: s.name_zh,
      year_start: s.year_start,
      year_end: s.year_end,
      realm_id: s.realm_id,
      sphere_id: s.sphere_id,
      has_inferred_sphere: s.has_inferred_sphere || false,
      dynasties: s.dynasties || null,
      capitals: s.capitals || null,
      religions: s.religions || null,
      population_peak_wan: s.population_peak_wan ?? null,
      area_peak_wan_km2: s.area_peak_wan_km2 ?? null,
      modern_countries: s.modern_countries || [],
      qid: s.qid || null,
      intro: s.intro || null,
      has_detail: s.has_detail,
      has_polygon: s.has_polygon,
    }))
    downloadFile(`${stem}.json`, JSON.stringify(payload, null, 2), 'application/json')
    return
  }

  // CSV
  const headers = [
    'id', 'name_zh', 'name_en', 'year_start', 'year_end',
    'realm_id', 'sphere_id', 'inferred_sphere',
    'dynasties', 'capitals', 'religions',
    'population_peak_wan', 'area_peak_wan_km2',
    'modern_countries', 'qid', 'has_detail', 'has_polygon',
  ]
  const esc = (v: any): string => {
    if (v === null || v === undefined) return ''
    let s = Array.isArray(v) ? v.join('|') : String(v)
    if (/[",\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"'
    return s
  }
  const rows = list.map(s => [
    s.id,
    s.name_zh || '',
    s.name_en,
    s.year_start ?? '',
    s.year_end ?? '',
    s.realm_id || '',
    s.sphere_id || '',
    s.has_inferred_sphere ? 'Y' : '',
    s.dynasties || [],
    s.capitals || [],
    s.religions || [],
    s.population_peak_wan ?? '',
    s.area_peak_wan_km2 ?? '',
    s.modern_countries || [],
    s.qid || '',
    s.has_detail ? 'Y' : 'N',
    s.has_polygon ? 'Y' : 'N',
  ].map(esc).join(','))
  const csv = '﻿' + headers.join(',') + '\n' + rows.join('\n')
  downloadFile(`${stem}.csv`, csv, 'text/csv')
}

// 小元件：排序箭頭
const SortArrow = (props: { col: string; sort: string; dir: string }) => {
  if (props.sort !== props.col) return h('span', { class: 'text-gray-300' }, '↕')
  return h('span', { class: 'text-amber-600' }, props.dir === 'asc' ? '↑' : '↓')
}

// 接受外部 highlight：找到 state，自動開啟詳細彈窗（filter 不限制 modal 顯示）
watch(() => props.highlightName, (name) => {
  if (!name) return
  const found = allStates.value.find(s => s.name_en === name)
  if (found) selected.value = found
})

// 也在資料載入完成後檢查一次（若 highlightName 比資料先到）
function applyHighlightAfterLoad() {
  const name = props.highlightName
  if (!name) return
  const found = allStates.value.find(s => s.name_en === name)
  if (found) selected.value = found
}

onMounted(async () => {
  try {
    const [skRes, wdRes, clsRes, infRes] = await Promise.all([
      fetch('/maps/state-skeleton.json'),
      fetch('/maps/wikidata-states.json'),
      fetch('/maps/polygon-classifications.json').catch(() => ({ ok: false } as any)),
      fetch('/maps/state-sphere-inference.json').catch(() => ({ ok: false } as any)),
    ])
    const skeleton: StateSkeleton[] = await skRes.json()
    const wikidata: WikidataState[] = await wdRes.json()
    let inference: Record<string, SphereInferenceEntry> = {}
    if (infRes && (infRes as Response).ok) {
      try { inference = await (infRes as Response).json() } catch {}
    }
    allStates.value = mergeStates(skeleton, wikidata, inference)
    if (clsRes && (clsRes as Response).ok) {
      try { polityClassification.value = await (clsRes as Response).json() } catch {}
    }
    applyHighlightAfterLoad()
  } catch (e) {
    console.error('states data load failed', e)
  }
})
</script>
