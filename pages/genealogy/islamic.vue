<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">伊斯蘭族譜</span>
      <span class="text-xs text-gray-400 ml-1">{{ people.length > 0 ? `${people.length} 人` : '' }}</span>
      <div class="flex-1" />
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">表格</span>
        <span class="text-xs px-2.5 py-1 rounded-md font-medium text-gray-400 cursor-not-allowed" title="即將推出">族譜圖</span>
      </div>
    </nav>

    <!-- Filter bar -->
    <div class="flex flex-wrap items-center gap-2 px-4 py-2 bg-white border-b border-gray-100 flex-shrink-0">
      <div class="relative">
        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-300 text-[11px] pointer-events-none select-none">🔍</span>
        <input
          v-model="search"
          class="pl-7 pr-3 py-1 text-xs border border-gray-200 rounded-lg outline-none focus:border-emerald-400 transition bg-white w-56"
          placeholder="搜尋姓名（中文／阿拉伯／英文）…"
        />
      </div>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="t in traditionOptions"
          :key="t.value"
          class="text-xs px-2.5 py-1 rounded-lg border transition"
          :class="traditionFilter === t.value
            ? `${t.bg} ${t.border} ${t.text} font-medium`
            : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="traditionFilter = traditionFilter === t.value ? '' : t.value"
        >
          <span class="inline-block w-2 h-2 rounded-full mr-1 align-middle" :class="t.dot" />
          {{ t.label }}
        </button>
      </div>
      <span v-if="search || traditionFilter" class="text-xs text-gray-400">{{ filtered.length }} / {{ people.length }} 筆</span>
    </div>

    <!-- Table -->
    <div class="flex-1 min-h-0 overflow-auto p-4">
      <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中…</div>
      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap w-14">代</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">中文姓名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap" dir="rtl">الاسم</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">英文</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">傳統</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">性別</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">配偶</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">兒女</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">出處</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="9" class="px-4 py-10 text-center text-gray-400">
                {{ people.length === 0 ? '尚無資料' : '沒有符合的搜尋結果' }}
              </td>
            </tr>
            <tr
              v-for="p in filtered"
              :key="p.id"
              class="border-b border-gray-100 hover:bg-gray-50 transition"
              :class="rowBg(p.tradition)"
            >
              <td class="px-3 py-2 text-gray-400 text-xs">{{ p.generation ?? '—' }}</td>
              <td class="px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{{ p.name_zh }}<span v-if="p.kunya" class="ml-1 text-xs text-gray-400">·{{ p.kunya }}</span></td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap" dir="rtl">{{ p.name_ar }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs whitespace-nowrap">{{ p.name_en }}</td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span class="text-[10px] px-1.5 py-0.5 rounded font-medium" :class="traditionBadge(p.tradition)">{{ traditionLabel(p.tradition) }}</span>
              </td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ p.gender }}</td>
              <td class="px-3 py-2 text-gray-700 text-xs max-w-[200px] truncate" :title="p.spouse">{{ p.spouse || '—' }}</td>
              <td class="px-3 py-2 text-gray-700 text-xs max-w-[260px] truncate" :title="p.children">{{ p.children || '—' }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs max-w-[320px] truncate" :title="p.sources">{{ p.sources || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '伊斯蘭族譜 — Know Graph Lab' })

type Person = {
  id: string
  name_zh: string
  name_ar?: string | null
  name_en?: string | null
  kunya?: string | null
  gender?: string | null
  generation?: number | null
  tradition: string
  spouse?: string | null
  children?: string | null
  sources?: string | null
}

const people = ref<Person[]>([])
const loading = ref(true)
const search = ref('')
const traditionFilter = ref('')

const traditionOptions = [
  { value: 'quranic',      label: '古蘭明文',   bg: 'bg-white',        border: 'border-gray-400',  text: 'text-gray-900',  dot: 'bg-gray-400' },
  { value: 'sunni',        label: '順尼派',     bg: 'bg-emerald-50',   border: 'border-emerald-400', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  { value: 'shia_twelver', label: '十二伊瑪目', bg: 'bg-rose-50',      border: 'border-rose-400',  text: 'text-rose-700',  dot: 'bg-rose-500' },
  { value: 'shia_ismaili', label: '伊斯瑪儀',   bg: 'bg-purple-50',    border: 'border-purple-400',text: 'text-purple-700',dot: 'bg-purple-500' },
  { value: 'shia_zaidi',   label: '栽德派',     bg: 'bg-orange-50',    border: 'border-orange-400',text: 'text-orange-700',dot: 'bg-orange-500' },
  { value: 'sufi',         label: '蘇菲',       bg: 'bg-teal-50',      border: 'border-teal-400',  text: 'text-teal-700',  dot: 'bg-teal-500' },
  { value: 'historical',   label: '史傳',       bg: 'bg-gray-100',     border: 'border-gray-400',  text: 'text-gray-700',  dot: 'bg-gray-400' },
]

function rowBg(t: string) {
  const m: Record<string, string> = {
    quranic: '',
    sunni: 'bg-emerald-50/40',
    shia_twelver: 'bg-rose-50/40',
    shia_ismaili: 'bg-purple-50/40',
    shia_zaidi: 'bg-orange-50/40',
    sufi: 'bg-teal-50/40',
    historical: 'bg-gray-50/60',
  }
  return m[t] ?? ''
}

function traditionBadge(t: string) {
  const m: Record<string, string> = {
    quranic: 'bg-gray-100 text-gray-700',
    sunni: 'bg-emerald-100 text-emerald-700',
    shia_twelver: 'bg-rose-100 text-rose-700',
    shia_ismaili: 'bg-purple-100 text-purple-700',
    shia_zaidi: 'bg-orange-100 text-orange-700',
    sufi: 'bg-teal-100 text-teal-700',
    historical: 'bg-gray-100 text-gray-500',
  }
  return m[t] ?? 'bg-gray-100 text-gray-500'
}

function traditionLabel(t: string) {
  return traditionOptions.find(o => o.value === t)?.label ?? t
}

const filtered = computed(() => {
  let list = people.value
  if (traditionFilter.value) list = list.filter(p => p.tradition === traditionFilter.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(p =>
      (p.name_zh || '').toLowerCase().includes(q) ||
      (p.name_ar || '').toLowerCase().includes(q) ||
      (p.name_en || '').toLowerCase().includes(q)
    )
  }
  return list
})

async function load() {
  loading.value = true
  try {
    people.value = await $fetch<Person[]>('/api/genealogy/islamic-people')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
