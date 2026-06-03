<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">教父文獻翻譯詞庫</span>
      <span class="text-xs text-gray-400 ml-1">{{ activeTabCount }} 項</span>
      <div class="ml-auto flex items-center gap-2">
        <label class="text-xs text-gray-500 flex items-center gap-1 cursor-pointer select-none">
          <input type="checkbox" v-model="editMode" class="accent-stone-700" />
          編輯模式
        </label>
      </div>
    </nav>

    <div class="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🔤 教父文獻翻譯詞庫</h1>
        <p class="text-sm text-gray-500">
          每筆主譯名為 <span class="text-amber-700 font-medium">★ 中文翻譯</span>（建議採用，跨教派通用版本）。在<b>聖經人物</b>與<b>神學名詞</b>兩 tab 額外顯示<b>新教變體</b>與<b>天主教變體</b>欄，供脈絡需要時查閱（保羅／保祿、Logos／道／聖言 等）。
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
        >{{ t.label }} <span class="text-xs text-gray-400">({{ tabCount(t.key) }})</span></button>
      </div>

      <!-- Sub-tabs (人名 only) — era buckets -->
      <div v-if="activeTab === 'people'" class="flex flex-wrap items-center gap-1 mb-4">
        <button
          v-for="e in personEras" :key="e.key"
          @click="activePersonEra = e.key"
          class="text-xs px-2.5 py-1 rounded-full border transition"
          :class="activePersonEra === e.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ e.label }} <span class="ml-0.5 text-[10px] opacity-70">{{ personEraCount(e.key) }}</span></button>
      </div>

      <!-- Search -->
      <div class="flex flex-wrap items-center gap-2 mb-4">
        <input
          v-model="q"
          type="search"
          placeholder="搜尋（原文／英文／中譯／出處任一）"
          class="text-sm px-3 py-1.5 border border-gray-300 rounded-md w-72 focus:outline-none focus:border-stone-500"
        />
        <button
          v-if="editMode"
          @click="addNew"
          class="text-xs px-3 py-1 rounded-md bg-stone-900 text-white hover:bg-stone-800"
        >+ 新增</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-sm text-gray-500 py-12 text-center">載入中…</div>

      <!-- People table (人名 / 君主 / 哲學家 — all theologians table by figure_type) -->
      <div v-else-if="isPeopleTab" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
            <tr>
              <th class="px-3 py-2 text-left font-medium" style="width:16%">英文</th>
              <th class="px-3 py-2 text-left font-medium" style="width:14%">原文</th>
              <th class="px-3 py-2 text-left font-medium" style="width:18%">★ 中文翻譯</th>
              <!-- 雙翻譯欄位只在「聖經人物」sub-tab 顯示 — 一般教父的譯名
                   差異不大，多兩欄反而吵雜。聖經人物則常有保羅/保祿、
                   彼得/伯多祿、約翰/若望 等明顯分歧。-->
              <th v-if="showBiblicalCols" class="px-3 py-2 text-left font-medium" style="width:16%">新教變體</th>
              <th v-if="showBiblicalCols" class="px-3 py-2 text-left font-medium" style="width:16%">天主教變體</th>
              <th class="px-3 py-2 text-left font-medium" style="width:20%">首次出現出處</th>
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
                <td class="px-3 py-2 font-semibold text-amber-700">{{ row.name_recommended || '—' }}</td>
                <td v-if="showBiblicalCols" class="px-3 py-2 text-gray-700">{{ row.name_protestant || '—' }}</td>
                <td v-if="showBiblicalCols" class="px-3 py-2 text-gray-700">{{ row.name_catholic_sgs || '—' }}</td>
                <td class="px-3 py-2 text-gray-600 text-xs">{{ row.first_source || '—' }}</td>
              </tr>
              <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                <td :colspan="showBiblicalCols ? 6 : 4" class="px-5 py-4">
                  <div v-if="!editMode" class="text-xs text-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <div class="text-gray-500 mb-1">★ 中文翻譯（建議採用）</div>
                      <div class="text-amber-700 font-medium">{{ row.name_recommended || '—' }}</div>
                    </div>
                    <div>
                      <div class="text-gray-500 mb-1">新教變體</div>
                      <div class="text-stone-900">{{ row.name_protestant || '—' }}</div>
                    </div>
                    <div>
                      <div class="text-gray-500 mb-1">天主教變體</div>
                      <div class="text-stone-900">{{ row.name_catholic_sgs || '—' }}</div>
                    </div>
                    <div class="md:col-span-3">
                      <div class="text-gray-500 mb-1">首次出現出處</div>
                      <div class="text-stone-700">{{ row.first_source || '—' }}</div>
                    </div>
                    <div v-if="row.recommendation_reason" class="md:col-span-3">
                      <div class="text-gray-500 mb-1">備註</div>
                      <div class="text-gray-800 whitespace-pre-wrap">{{ row.recommendation_reason }}</div>
                    </div>
                  </div>
                  <div v-else class="flex flex-col gap-2 text-xs">
                    <label class="text-gray-500">★ 中文翻譯（建議採用）</label>
                    <input
                      v-model="editPerson.name_recommended"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="建議採用的譯名"
                    />
                    <div class="grid grid-cols-2 gap-2 mt-1">
                      <div>
                        <label class="text-gray-500">新教變體</label>
                        <input
                          v-model="editPerson.name_protestant"
                          class="px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="新教中譯（華聯/證主/校園/改革宗）"
                        />
                      </div>
                      <div>
                        <label class="text-gray-500">天主教變體</label>
                        <input
                          v-model="editPerson.name_catholic_sgs"
                          class="px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="天主教中譯（思高/光啟/輔大）"
                        />
                      </div>
                    </div>
                    <label class="text-gray-500 mt-1">分類</label>
                    <select v-model="editPerson.person_era" class="px-2 py-1 border border-gray-300 rounded w-full">
                      <option value="biblical">聖經人物</option>
                      <option value="early">初代教會（-638）</option>
                      <option value="medieval">中世紀教會（-1517）</option>
                      <option value="modern">近代教會（-1910）</option>
                      <option value="contemporary">現代教會</option>
                    </select>
                    <label class="text-gray-500 mt-1">首次出現出處（書名 / 卷 / chunk）</label>
                    <input
                      v-model="editPerson.first_source"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="例：ANF Vol 1 / 致丟格那妥書 / chunk 9"
                    />
                    <label class="text-gray-500 mt-1">備註（選填）</label>
                    <textarea
                      v-model="editPerson.recommendation_reason"
                      rows="2"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="可選備註"
                    />
                    <div class="flex gap-2 mt-1">
                      <button
                        @click.stop="savePerson(row.id)"
                        class="px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800"
                      >儲存</button>
                      <button
                        @click.stop="expanded = null"
                        class="px-3 py-1 bg-gray-100 text-gray-700 rounded"
                      >取消</button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="filteredPeople.length === 0">
              <td :colspan="showBiblicalCols ? 6 : 4" class="px-3 py-12 text-center text-sm text-gray-400">
                {{ theologians.length === 0 ? '尚無資料 — 請執行 scripts/seed_translation_glossary.py 批次填入' : '無符合搜尋條件的項目' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Terms table — covers tabs 'place' / 'work' / 'sect' / 'term'
           (all backed by theological_terms, filtered by entity_type). -->
      <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
            <tr>
              <th class="px-3 py-2 text-left font-medium" style="width:16%">英文</th>
              <th class="px-3 py-2 text-left font-medium" style="width:14%">原文</th>
              <th class="px-3 py-2 text-left font-medium" style="width:18%">★ 中文翻譯</th>
              <!-- 神學名詞 tab 才顯示雙翻譯欄；地名／作品名／教派名通常
                   只有一個譯法（差異在於有沒有人翻過而已），雙欄沒意義。-->
              <th v-if="activeTab === 'term'" class="px-3 py-2 text-left font-medium" style="width:16%">新教變體</th>
              <th v-if="activeTab === 'term'" class="px-3 py-2 text-left font-medium" style="width:16%">天主教變體</th>
              <th class="px-3 py-2 text-left font-medium" style="width:20%">首次出現出處</th>
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
                <td class="px-3 py-2 font-semibold text-amber-700">{{ row.zh_recommended || '—' }}</td>
                <td v-if="activeTab === 'term'" class="px-3 py-2 text-gray-700">{{ row.zh_protestant || '—' }}</td>
                <td v-if="activeTab === 'term'" class="px-3 py-2 text-gray-700">{{ row.zh_catholic_sgs || '—' }}</td>
                <td class="px-3 py-2 text-gray-600 text-xs">{{ row.first_source || '—' }}</td>
              </tr>
              <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                <td :colspan="activeTab === 'term' ? 6 : 4" class="px-5 py-4">
                  <div v-if="!editMode" class="text-xs text-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <div class="text-gray-500 mb-1">★ 中文翻譯（建議採用）</div>
                      <div class="text-amber-700 font-medium">{{ row.zh_recommended || '—' }}</div>
                    </div>
                    <div>
                      <div class="text-gray-500 mb-1">新教變體</div>
                      <div class="text-stone-900">{{ row.zh_protestant || '—' }}</div>
                    </div>
                    <div>
                      <div class="text-gray-500 mb-1">天主教變體</div>
                      <div class="text-stone-900">{{ row.zh_catholic_sgs || '—' }}</div>
                    </div>
                    <div class="md:col-span-3">
                      <div class="text-gray-500 mb-1">首次出現出處</div>
                      <div class="text-stone-700">{{ row.first_source || '—' }}</div>
                    </div>
                    <div v-if="row.definition_zh" class="md:col-span-3">
                      <div class="text-gray-500 mb-1">中文釋義</div>
                      <div class="text-gray-800 whitespace-pre-wrap">{{ row.definition_zh }}</div>
                    </div>
                  </div>
                  <div v-else class="flex flex-col gap-2 text-xs">
                    <label class="text-gray-500">★ 中文翻譯（建議採用）</label>
                    <input
                      v-model="editTerm.zh_recommended"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="建議採用的譯名"
                    />
                    <div class="grid grid-cols-2 gap-2 mt-1">
                      <div>
                        <label class="text-gray-500">新教變體</label>
                        <input
                          v-model="editTerm.zh_protestant"
                          class="px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="新教中譯"
                        />
                      </div>
                      <div>
                        <label class="text-gray-500">天主教變體</label>
                        <input
                          v-model="editTerm.zh_catholic_sgs"
                          class="px-2 py-1 border border-gray-300 rounded w-full"
                          placeholder="天主教中譯（思高）"
                        />
                      </div>
                    </div>
                    <label class="text-gray-500 mt-1">首次出現出處（書名 / 卷 / chunk）</label>
                    <input
                      v-model="editTerm.first_source"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="例：ANF Vol 1 / 革利免致哥林多人前書 / chunk 3"
                    />
                    <label class="text-gray-500 mt-1">中文釋義（選填）</label>
                    <textarea
                      v-model="editTerm.definition_zh"
                      rows="2"
                      class="px-2 py-1 border border-gray-300 rounded w-full"
                      placeholder="可選釋義"
                    />
                    <div class="flex gap-2 mt-1">
                      <button
                        @click.stop="saveTerm(row.id)"
                        class="px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800"
                      >儲存</button>
                      <button
                        @click.stop="expanded = null"
                        class="px-3 py-1 bg-gray-100 text-gray-700 rounded"
                      >取消</button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="filteredTerms.length === 0">
              <td :colspan="activeTab === 'term' ? 6 : 4" class="px-3 py-12 text-center text-sm text-gray-400">
                {{ filteredTerms.length === 0 && tabCount(activeTab) === 0 ? '此類別尚無資料，編輯模式 → + 新增 開始填入' : '無符合搜尋條件的項目' }}
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

// 5 categories. `people` is the theologians table (further sub-divided
// by `person_era`); `place` / `work` / `sect` / `term` are entity_type
// sub-buckets of theological_terms.
const tabs = [
  { key: 'people',      label: '人名' },
  { key: 'monarch',     label: '君主' },
  { key: 'philosopher', label: '哲學家' },
  { key: 'place',       label: '地名' },
  { key: 'work',        label: '作品名' },
  { key: 'sect',        label: '教派名' },
  { key: 'term',        label: '神學名詞' },
] as const
type TabKey = typeof tabs[number]['key']
const activeTab = ref<TabKey>('people')

// People-backed tabs all read the theologians table, split by figure_type:
//   people → 神學家 (theologian/null) · monarch → 君主 · philosopher → 哲學家
const PEOPLE_TABS = ['people', 'monarch', 'philosopher']
const isPeopleTab = computed(() => PEOPLE_TABS.includes(activeTab.value))
const isTheologianRow = (r: any) => !r.figure_type || r.figure_type === 'theologian'
function rowMatchesTab(r: any, key: string): boolean {
  if (key === 'people') return isTheologianRow(r)
  return r.figure_type === key  // 'monarch' | 'philosopher'
}
// 雙翻譯（新教/天主教變體）只在「人名 → 聖經人物」有意義；君主/哲學家不顯示。
const showBiblicalCols = computed(() => activeTab.value === 'people' && activePersonEra.value === 'biblical')

// Sub-tabs for 人名: era-based grouping. Boundaries:
//   biblical     — Bible characters (manual flag)
//   early        — to 638 (Islamic conquest / end of patristic age)
//   medieval     — 638-1516
//   modern       — 1517-1909 (Reformation through to 1910)
//   contemporary — 1910+
const personEras = [
  { key: 'all',          label: '全部' },
  { key: 'biblical',     label: '聖經人物' },
  { key: 'early',        label: '初代教會' },
  { key: 'medieval',     label: '中世紀教會' },
  { key: 'modern',       label: '近代教會' },
  { key: 'contemporary', label: '現代教會' },
] as const
type PersonEra = typeof personEras[number]['key']
const activePersonEra = ref<PersonEra>('all')

const loading = ref(true)
const theologians = ref<any[]>([])
const terms = ref<any[]>([])

const q = ref('')
const expanded = ref<string | null>(null)
const editMode = ref(false)
const editPerson = ref<any>({})
const editTerm = ref<any>({})

function tabCount(key: TabKey): number {
  if (key === 'people') return theologians.value.filter(isTheologianRow).length
  if (key === 'monarch' || key === 'philosopher')
    return theologians.value.filter(r => r.figure_type === key).length
  return terms.value.filter(t => (t.entity_type || 'term') === key).length
}
const activeTabCount = computed(() => tabCount(activeTab.value))

function personEraCount(era: PersonEra): number {
  const people = theologians.value.filter(isTheologianRow)
  if (era === 'all') return people.length
  return people.filter(p => (p.person_era || 'early') === era).length
}

const filteredPeople = computed(() => {
  const query = q.value.trim().toLowerCase()
  const era = activePersonEra.value
  const tab = activeTab.value
  const rows = theologians.value.filter(r => {
    if (!rowMatchesTab(r, tab)) return false
    // era sub-tabs only apply to 人名 (神學家); 君主/哲學家 是平面清單
    if (tab === 'people' && era !== 'all' && (r.person_era || 'early') !== era) return false
    if (!query) return true
    return [r.name_english, r.name_original, r.name_latin_std, r.name_recommended, r.role, r.first_source]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
  return [...rows].sort((a, b) => effectiveYear(a) - effectiveYear(b))
})
const filteredTerms = computed(() => {
  const query = q.value.trim().toLowerCase()
  return terms.value.filter(r => {
    if ((r.entity_type || 'term') !== activeTab.value) return false
    if (!query) return true
    return [r.term_english, r.term_original, r.term_latin_translit, r.zh_recommended, r.first_source, r.definition_zh]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
})

async function addNew() {
  const english = prompt('英文／拉丁名（必填）')?.trim()
  if (!english) return
  const original = prompt('原文（希臘／拉丁／希伯來，可空）')?.trim() || null
  const chinese = prompt('中文翻譯（必填）')?.trim()
  if (!chinese) return
  const source = prompt('首次出現出處（書名 / 卷 / chunk）')?.trim() || null
  if (isPeopleTab.value) {
    // For new entries, use the currently-active era sub-tab (or 'early'
    // when 「全部」 is selected — user can change after via edit modal).
    const era = activePersonEra.value === 'all' ? 'early' : activePersonEra.value
    const figure_type = activeTab.value === 'people' ? 'theologian' : activeTab.value
    // Store the user-supplied translation as both the recommended value
    // AND the protestant slot, so the row shows up consistently in the
    // ★ 中文翻譯 column and (for biblical figures) in the dual columns.
    // User can refine via edit modal afterwards.
    const { data, error } = await supabase.from('theologians').insert({
      name_english: english, name_original: original, name_latin_std: english,
      name_recommended: chinese,
      name_protestant: chinese,
      first_source: source,
      person_era: era,
      figure_type,
    }).select().single()
    if (error) { alert('新增失敗：' + error.message); return }
    theologians.value.push(data)
  } else {
    const { data, error } = await supabase.from('theological_terms').insert({
      term_english: english, term_original: original,
      zh_recommended: chinese,
      zh_protestant: chinese,
      first_source: source,
      entity_type: activeTab.value,
    }).select().single()
    if (error) { alert('新增失敗：' + error.message); return }
    terms.value.push(data)
  }
}

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
  if (isPeopleTab.value) {
    const row = theologians.value.find(r => r.id === id)
    editPerson.value = {
      name_recommended: row?.name_recommended || '',
      name_protestant: row?.name_protestant || '',
      name_catholic_sgs: row?.name_catholic_sgs || '',
      first_source: row?.first_source || '',
      person_era: row?.person_era || 'early',
      recommendation_reason: row?.recommendation_reason || '',
    }
  } else {
    const row = terms.value.find(r => r.id === id)
    editTerm.value = {
      zh_recommended: row?.zh_recommended || '',
      zh_protestant: row?.zh_protestant || '',
      zh_catholic_sgs: row?.zh_catholic_sgs || '',
      first_source: row?.first_source || '',
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
