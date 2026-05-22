<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">神學家與名詞中譯</span>
      <span class="text-xs text-gray-400 ml-1">{{ activeTab === 'people' ? theologians.length : terms.length }} 項</span>
      <div class="ml-auto flex items-center gap-2">
        <label class="text-xs text-gray-500 flex items-center gap-1 cursor-pointer select-none">
          <input type="checkbox" v-model="editMode" class="accent-stone-700" />
          編輯模式
        </label>
      </div>
    </nav>

    <div class="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🔤 神學家與名詞中譯</h1>
        <p class="text-sm text-gray-500">
          各傳統中譯對照 — 新教（華聯／證主／校園／改革宗）／ 思高 ／ 東正教 ／ 香港（基文／道風）／ 台灣（光啟／輔大）／ 中國學界。標 ★ 為建議採用譯名。
        </p>
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-1 mb-5 border-b border-gray-200">
        <button
          v-for="t in tabs" :key="t.key"
          @click="activeTab = t.key"
          class="px-4 py-2 text-sm border-b-2 -mb-px transition"
          :class="activeTab === t.key
            ? 'border-stone-700 text-stone-900 font-semibold'
            : 'border-transparent text-gray-500 hover:text-gray-800'"
        >{{ t.label }} <span class="text-xs text-gray-400">({{ t.key === 'people' ? theologians.length : terms.length }})</span></button>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-2 mb-4">
        <input
          v-model="q"
          type="search"
          placeholder="搜尋（原文／英文／中譯任一）"
          class="text-sm px-3 py-1.5 border border-gray-300 rounded-md w-72 focus:outline-none focus:border-stone-500"
        />
        <button
          v-if="activeTab === 'people'"
          @click="filterCentury = null"
          class="text-xs px-2.5 py-1 rounded-full border transition"
          :class="filterCentury === null
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >全部世紀</button>
        <button
          v-for="c in centuries" :key="c"
          @click="filterCentury = c"
          v-show="activeTab === 'people'"
          class="text-xs px-2.5 py-1 rounded-full border transition"
          :class="filterCentury === c
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ c }}</button>
        <button
          v-if="activeTab === 'terms'"
          @click="filterCategory = null"
          class="text-xs px-2.5 py-1 rounded-full border transition"
          :class="filterCategory === null
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >全部分類</button>
        <button
          v-for="c in categories" :key="c"
          @click="filterCategory = c"
          v-show="activeTab === 'terms'"
          class="text-xs px-2.5 py-1 rounded-full border transition"
          :class="filterCategory === c
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ c }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-sm text-gray-500 py-12 text-center">載入中…</div>

      <!-- People table -->
      <div v-else-if="activeTab === 'people'" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
            <tr>
              <th class="px-3 py-2 text-left font-medium">英文</th>
              <th class="px-3 py-2 text-left font-medium">原文</th>
              <th class="px-3 py-2 text-left font-medium">年代</th>
              <th class="px-3 py-2 text-left font-medium">出身</th>
              <th class="px-3 py-2 text-left font-medium">★ 建議</th>
              <th class="px-3 py-2 text-left font-medium">新教</th>
              <th class="px-3 py-2 text-left font-medium">思高</th>
              <th class="px-3 py-2 text-left font-medium">東正教</th>
              <th class="px-3 py-2 text-left font-medium">香港</th>
              <th class="px-3 py-2 text-left font-medium">台灣</th>
              <th class="px-3 py-2 text-left font-medium">中國</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in filteredPeople" :key="row.id">
              <tr
                class="border-b border-gray-100 hover:bg-stone-50/60 cursor-pointer"
                @click="toggleExpand(row.id)"
              >
                <td class="px-3 py-2 font-medium text-gray-900">{{ row.name_english }}</td>
                <td class="px-3 py-2 text-gray-700 font-serif">{{ row.name_original || '—' }}</td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ formatYears(row.born_year, row.died_year) }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.nationality || '—' }}</td>
                <td class="px-3 py-2 font-semibold text-amber-700">{{ row.name_recommended || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_protestant || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_catholic_sgs || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_orthodox || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_hk || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_tw || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.name_china_academic || '—' }}</td>
              </tr>
              <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                <td colspan="11" class="px-5 py-4">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                    <div>
                      <div class="text-gray-500 mb-1">基本資料</div>
                      <div class="text-gray-800">
                        <div><span class="text-gray-500">學派：</span>{{ row.school || '—' }}</div>
                        <div><span class="text-gray-500">身份：</span>{{ row.role || '—' }}</div>
                        <div><span class="text-gray-500">拉丁名：</span>{{ row.name_latin_std || '—' }}</div>
                      </div>
                    </div>
                    <div class="md:col-span-2">
                      <div class="text-gray-500 mb-1">建議理由</div>
                      <div v-if="!editMode" class="text-gray-800 whitespace-pre-wrap">{{ row.recommendation_reason || '—' }}</div>
                      <div v-else class="flex flex-col gap-2">
                        <input
                          v-model="editPerson.name_recommended"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="建議譯名"
                        />
                        <textarea
                          v-model="editPerson.recommendation_reason"
                          rows="3"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="建議理由（音譯接近度／傳統權威／學界通用度）"
                        />
                        <textarea
                          v-model="editPerson.notes"
                          rows="2"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="備註"
                        />
                        <div class="flex gap-2">
                          <button
                            @click.stop="savePerson(row.id)"
                            class="text-xs px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800"
                          >儲存</button>
                          <button
                            @click.stop="expanded = null"
                            class="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded"
                          >取消</button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-if="row.notes" class="mt-3 text-xs text-gray-600 border-t border-gray-200 pt-2">
                    <span class="text-gray-500">備註：</span>{{ row.notes }}
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="filteredPeople.length === 0">
              <td colspan="11" class="px-3 py-12 text-center text-sm text-gray-400">
                {{ theologians.length === 0 ? '尚無資料 — 請執行 scripts/seed_translation_glossary.py 批次填入' : '無符合搜尋條件的項目' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Terms table -->
      <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
            <tr>
              <th class="px-3 py-2 text-left font-medium">英文</th>
              <th class="px-3 py-2 text-left font-medium">原文</th>
              <th class="px-3 py-2 text-left font-medium">分類</th>
              <th class="px-3 py-2 text-left font-medium">★ 建議</th>
              <th class="px-3 py-2 text-left font-medium">新教</th>
              <th class="px-3 py-2 text-left font-medium">思高</th>
              <th class="px-3 py-2 text-left font-medium">東正教</th>
              <th class="px-3 py-2 text-left font-medium">香港</th>
              <th class="px-3 py-2 text-left font-medium">台灣</th>
              <th class="px-3 py-2 text-left font-medium">中國</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in filteredTerms" :key="row.id">
              <tr
                class="border-b border-gray-100 hover:bg-stone-50/60 cursor-pointer"
                @click="toggleExpand(row.id)"
              >
                <td class="px-3 py-2 font-medium text-gray-900">{{ row.term_english }}</td>
                <td class="px-3 py-2 text-gray-700 font-serif">{{ row.term_original || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.category || '—' }}</td>
                <td class="px-3 py-2 font-semibold text-amber-700">{{ row.zh_recommended || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_protestant || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_catholic_sgs || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_orthodox || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_hk || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_tw || '—' }}</td>
                <td class="px-3 py-2 text-gray-600">{{ row.zh_china_academic || '—' }}</td>
              </tr>
              <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                <td colspan="10" class="px-5 py-4">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                    <div>
                      <div class="text-gray-500 mb-1">原文細節</div>
                      <div class="text-gray-800">
                        <div><span class="text-gray-500">羅馬化：</span>{{ row.term_latin_translit || '—' }}</div>
                        <div><span class="text-gray-500">時期：</span>{{ row.era || '—' }}</div>
                      </div>
                      <div class="text-gray-500 mt-3 mb-1">中文釋義</div>
                      <div class="text-gray-800">{{ row.definition_zh || '—' }}</div>
                    </div>
                    <div class="md:col-span-2">
                      <div class="text-gray-500 mb-1">建議理由</div>
                      <div v-if="!editMode" class="text-gray-800 whitespace-pre-wrap">{{ row.recommendation_reason || '—' }}</div>
                      <div v-else class="flex flex-col gap-2">
                        <input
                          v-model="editTerm.zh_recommended"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="建議譯名"
                        />
                        <textarea
                          v-model="editTerm.recommendation_reason"
                          rows="3"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="建議理由"
                        />
                        <textarea
                          v-model="editTerm.definition_zh"
                          rows="2"
                          class="text-xs px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="中文釋義"
                        />
                        <div class="flex gap-2">
                          <button
                            @click.stop="saveTerm(row.id)"
                            class="text-xs px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800"
                          >儲存</button>
                          <button
                            @click.stop="expanded = null"
                            class="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded"
                          >取消</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="filteredTerms.length === 0">
              <td colspan="10" class="px-3 py-12 text-center text-sm text-gray-400">
                {{ terms.length === 0 ? '尚無資料 — 請執行 scripts/seed_translation_glossary.py 批次填入' : '無符合搜尋條件的項目' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '神學家與名詞中譯 — Know Graph Lab' })

const supabase = useSupabaseClient<any>()

const tabs = [
  { key: 'people', label: '神學家' },
  { key: 'terms', label: '神學名詞' },
] as const
const activeTab = ref<'people' | 'terms'>('people')

const loading = ref(true)
const theologians = ref<any[]>([])
const terms = ref<any[]>([])

const q = ref('')
const filterCentury = ref<string | null>(null)
const filterCategory = ref<string | null>(null)
const expanded = ref<string | null>(null)
const editMode = ref(false)
const editPerson = ref<any>({})
const editTerm = ref<any>({})

const CENTURY_ORDER = ['1c','2c','2-3c','3c','3-4c','4c','4-5c','5c','5-6c','6c','7c','8c','9c','10c','11c','12c','13c','14c','15c','16c']
const centuries = computed(() => {
  const set = new Set(theologians.value.map(t => t.century).filter(Boolean))
  return CENTURY_ORDER.filter(c => set.has(c))
})
const categories = computed(() => {
  const set = new Set(terms.value.map(t => t.category).filter(Boolean))
  return [...set].sort()
})

const filteredPeople = computed(() => {
  const query = q.value.trim().toLowerCase()
  const rows = theologians.value.filter(r => {
    if (filterCentury.value && r.century !== filterCentury.value) return false
    if (!query) return true
    return [r.name_english, r.name_original, r.name_latin_std, r.name_protestant, r.name_catholic_sgs, r.name_orthodox, r.name_hk, r.name_tw, r.name_china_academic, r.name_recommended, r.nationality]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
  return [...rows].sort((a, b) => effectiveYear(a) - effectiveYear(b))
})
const filteredTerms = computed(() => {
  const query = q.value.trim().toLowerCase()
  return terms.value.filter(r => {
    if (filterCategory.value && r.category !== filterCategory.value) return false
    if (!query) return true
    return [r.term_english, r.term_original, r.term_latin_translit, r.zh_protestant, r.zh_catholic_sgs, r.zh_orthodox, r.zh_hk, r.zh_tw, r.zh_china_academic, r.zh_recommended, r.definition_zh]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
})

function formatYears(b: number | null, d: number | null) {
  if (b == null && d == null) return '—'
  const fmt = (y: number | null) => y == null ? '' : (y < 0 ? `${-y} BC` : `${y}`)
  // 只有生年（還在世或卒年未知）→ "1920–"；只有卒年 → "–1920"；都有 → "1920–1980"
  return `${fmt(b)}–${fmt(d)}`
}

// 給排序用的等效年份：卒 → 生+40 → 世紀中點
function effectiveYear(r: any): number {
  if (r.died_year != null) return r.died_year
  if (r.born_year != null) return r.born_year + 40  // 假設 ~40 歲離世，給排序用
  const m = r.century?.match(/^(\d+)(?:-(\d+))?c/i)
  if (m) {
    const a = parseInt(m[1])
    const b = m[2] ? parseInt(m[2]) : a
    return (a + b - 1) * 50  // 1c→50, 2c→150, 4-5c→400, 20-21c→2000
  }
  return 9999
}

function toggleExpand(id: string) {
  if (expanded.value === id) {
    expanded.value = null
    return
  }
  expanded.value = id
  if (activeTab.value === 'people') {
    const row = theologians.value.find(r => r.id === id)
    editPerson.value = {
      name_recommended: row?.name_recommended || '',
      recommendation_reason: row?.recommendation_reason || '',
      notes: row?.notes || '',
    }
  } else {
    const row = terms.value.find(r => r.id === id)
    editTerm.value = {
      zh_recommended: row?.zh_recommended || '',
      recommendation_reason: row?.recommendation_reason || '',
      definition_zh: row?.definition_zh || '',
    }
  }
}

async function savePerson(id: string) {
  const patch = {
    ...editPerson.value,
    updated_at: new Date().toISOString(),
  }
  const { error } = await supabase.from('theologians').update(patch).eq('id', id)
  if (error) { alert('儲存失敗：' + error.message); return }
  Object.assign(theologians.value.find(r => r.id === id), patch)
  expanded.value = null
}

async function saveTerm(id: string) {
  const patch = {
    ...editTerm.value,
    updated_at: new Date().toISOString(),
  }
  const { error } = await supabase.from('theological_terms').update(patch).eq('id', id)
  if (error) { alert('儲存失敗：' + error.message); return }
  Object.assign(terms.value.find(r => r.id === id), patch)
  expanded.value = null
}

onMounted(async () => {
  // Sort done client-side via effectiveYear (卒年 ?? 生年+40 ?? 世紀中點)
  const [p, t] = await Promise.all([
    supabase.from('theologians').select('*'),
    supabase.from('theological_terms').select('*').order('sort_order', { ascending: true, nullsFirst: false }).order('category', { ascending: true }),
  ])
  theologians.value = p.data || []
  terms.value = t.data || []
  loading.value = false
})
</script>
