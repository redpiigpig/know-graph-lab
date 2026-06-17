<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="典外文獻搜索" :back="{ to: '/scripture-canon/christianity', label: '經典對照' }" container-class="max-w-6xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ filteredDocs.length }} 份 / {{ versions.length }} 個版本</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📜 典外文獻搜索</h1>
        <p class="text-sm text-gray-500">黃根春主編《基督教典外文獻》10 卷 — 舊約偽典／NT 偽典／Nag Hammadi／昆蘭古卷；中文／英文／原文平行對照</p>
      </div>

      <!-- Search box -->
      <div class="mb-6 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
        <form @submit.prevent="runSearch" class="flex items-center gap-2">
          <span class="text-stone-500 text-lg select-none">🔍</span>
          <input
            v-model="searchQ"
            type="text"
            placeholder="搜尋典外文獻內文（中／英／希臘／科普特／敘利亞皆可）"
            class="flex-1 text-sm bg-transparent border-none focus:outline-none placeholder:text-gray-300"
          />
          <select v-model="searchVersion" class="text-xs text-gray-600 bg-transparent border-l border-gray-200 pl-2 cursor-pointer">
            <option value="">全部版本</option>
            <option v-for="v in versions" :key="v.code" :value="v.code">{{ v.name_zh.replace(/（[^）]*）/g, '').trim() }}</option>
          </select>
          <button
            type="submit"
            class="text-xs px-3 py-1 rounded bg-stone-900 text-white hover:bg-stone-700 transition"
            :disabled="!searchQ || searchQ.length < 2"
          >搜尋</button>
        </form>
      </div>

      <!-- Search results -->
      <div v-if="searchActive" class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-700">
            搜尋結果
            <span class="text-xs text-gray-400 font-normal">
              「{{ lastQ }}」 — {{ searchTotal }} 筆{{ searchTotal > searchResults.length ? `（顯示前 ${searchResults.length} 筆）` : '' }}
            </span>
          </h2>
          <button @click="clearSearch" class="text-xs text-gray-400 hover:text-gray-700 transition">✕ 清除</button>
        </div>
        <div v-if="searchPending" class="text-center text-gray-400 py-8 text-sm">搜尋中…</div>
        <div v-else-if="searchResults.length === 0" class="text-center text-gray-400 py-8 text-sm">沒有符合的段落</div>
        <div v-else class="space-y-1">
          <NuxtLink
            v-for="(r, i) in searchResults"
            :key="`${r.doc_slug}-${r.version_code}-${r.order_index}-${i}`"
            :to="`/apocrypha/${r.doc_slug}#section-${r.order_index}`"
            class="block bg-white border border-gray-200 rounded px-3 py-2 hover:border-stone-400 hover:shadow-sm transition"
          >
            <div class="flex items-baseline gap-2 text-xs mb-1">
              <span class="font-mono font-semibold text-stone-700">
                {{ docTitle(r.doc_slug) }}
                <span class="text-gray-400">#{{ r.order_index }}</span>
              </span>
              <span class="text-gray-400">{{ versionLabel(r.version_code) }}</span>
              <span v-if="r.page_number" class="text-gray-300">p.{{ r.page_number }}</span>
            </div>
            <div class="text-sm text-gray-800 leading-relaxed" v-html="highlightMatch(snip(r.text, lastQ), lastQ)" />
          </NuxtLink>
        </div>
      </div>

      <!-- Testament top tabs -->
      <div v-if="!searchActive" class="flex items-center gap-1 mb-3 border-b border-gray-200">
        <button
          v-for="t in testamentTabs"
          :key="t.key"
          @click="activeTestament = t.key"
          class="px-4 py-2 -mb-px text-sm font-medium border-b-2 transition"
          :class="activeTestament === t.key
            ? 'border-stone-900 text-stone-900'
            : 'border-transparent text-gray-500 hover:text-stone-700'"
        >{{ t.label }} <span class="text-xs text-gray-400 font-normal">({{ t.count }})</span></button>
      </div>

      <!-- Genre chips for the active testament -->
      <div v-if="!searchActive" class="flex flex-wrap items-center gap-1.5 mb-6 text-xs">
        <button
          v-for="g in genreChips"
          :key="g.key"
          @click="activeGenre = g.key"
          class="px-3 py-1 rounded-full border transition"
          :class="activeGenre === g.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ g.label }} <span class="opacity-70">({{ g.count }})</span></button>
      </div>

      <!-- Loading / error -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <!-- Documents grouped by genre -->
      <div v-else-if="!searchActive">
        <div v-for="group in groupedDocs" :key="group.key" class="mt-2 mb-8">
          <h2 class="text-sm font-semibold text-stone-700 mb-3 border-b border-gray-200 pb-1.5 flex items-baseline gap-2">
            <span>{{ group.label }}</span>
            <span class="text-[10px] text-gray-400 font-normal">{{ group.label_en }}</span>
            <span class="text-xs text-gray-400 font-normal ml-auto">{{ group.items.length }} 份</span>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <NuxtLink
              v-for="doc in group.items"
              :key="doc.slug"
              :to="`/apocrypha/${doc.slug}`"
              class="block bg-white border border-gray-200 rounded-md px-3 py-2.5 hover:border-stone-400 hover:shadow-sm transition"
              :class="doc.total_sections === 0 ? 'opacity-60' : ''"
            >
              <div class="font-semibold text-gray-900 text-sm leading-tight">
                {{ doc.title_zh }}
                <span v-if="doc.title_zh_short && doc.title_zh_short !== doc.title_zh" class="text-[10px] text-gray-400 ml-1">({{ doc.title_zh_short }})</span>
              </div>
              <div class="text-[11px] text-gray-500 mt-0.5 leading-tight">{{ doc.title_en }}</div>
              <div class="flex items-center gap-2 mt-1.5 text-[10px]">
                <span v-if="doc.section_counts?.cct_zh"
                      class="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700">中 {{ doc.section_counts.cct_zh }}</span>
                <span v-if="hasEnglish(doc)"
                      class="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">英</span>
                <span v-if="hasOriginal(doc)"
                      class="px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">原文</span>
                <span v-if="doc.composition_low !== null || doc.composition_high !== null"
                      class="text-gray-400 ml-auto">
                  {{ formatPeriod(doc.composition_low, doc.composition_high) }}
                </span>
              </div>
            </NuxtLink>
          </div>
        </div>

        <div v-if="filteredDocs.length === 0" class="text-center text-gray-400 py-12 text-sm">
          這個類別暫無文獻
        </div>
      </div>

      <div v-if="!searchActive" class="mt-12 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>分類依黃根春主編《基督教典外文獻》10 冊（基督教文藝出版社 2008-2013）原書部別。</p>
        <p class="mt-1">英譯：Charles APOT 1913 (PD) / M.R. James 1924 (PD) / Charlesworth OTP 1983-85 © / Robinson NHL 1977 ©；原文：critical edition + Nag Hammadi Coptic facsimiles。多數英譯與原文欄位仍待補。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '典外文獻搜索 — Know Graph Lab' })

type ApocDoc = {
  slug: string
  title_zh: string
  title_zh_short: string | null
  title_en: string
  title_orig: string | null
  category: string
  testament: 'ot' | 'nt' | 'mixed'
  genre: string | null
  language_orig: string | null
  composition_low: number | null
  composition_high: number | null
  canon_status_jsonb: Record<string, boolean> | null
  summary_zh: string | null
  display_order: number
  section_counts: Record<string, number>
  total_sections: number
}
type ApocVersion = {
  code: string
  name_zh: string
  name_en: string
  language: string
  category: string
  public_domain: boolean
  display_order: number
  section_count: number
}
type SearchHit = {
  doc_slug: string
  version_code: string
  order_index: number
  section_label: string | null
  page_number: number | null
  text: string
}

const supabase = useSupabaseClient()
const docs = ref<ApocDoc[]>([])
const versions = ref<ApocVersion[]>([])
const pending = ref(true)
const error = ref<string | null>(null)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load() {
  try {
    const headers = await authHeaders()
    if (!('Authorization' in headers)) { pending.value = false; return }
    const [d, v] = await Promise.all([
      $fetch<ApocDoc[]>('/api/apocrypha/documents', { headers }),
      $fetch<ApocVersion[]>('/api/apocrypha/versions', { headers }),
    ])
    docs.value = d
    versions.value = v
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}
onMounted(load)

// ── Testament tabs + genre chips ───────────────────────────────────────
type Testament = 'ot' | 'nt'
const activeTestament = ref<Testament>('ot')
const activeGenre = ref<string>('all')

watch(activeTestament, () => {
  activeGenre.value = 'all'   // reset genre when switching testament
})

// Genre order + Chinese labels (mirrors 黃根春 book parts)
const GENRE_ORDER_OT: { key: string; label: string; label_en: string }[] = [
  { key: 'apocalyptic', label: '啟示文學',         label_en: 'Apocalyptic' },
  { key: 'testaments',  label: '族長遺訓',         label_en: 'Testaments' },
  { key: 'legends',     label: '重述聖經／傳奇',   label_en: 'Rewritten / Legendary' },
  { key: 'wisdom',      label: '智慧文獻',         label_en: 'Wisdom' },
  { key: 'deutero',     label: '隱藏經卷／第二正典', label_en: 'Deuterocanon' },
  { key: 'hymns',       label: '詩歌頌詞',         label_en: 'Hymns & Psalms' },
  { key: 'fragments',   label: '希臘化猶太斷片',   label_en: 'Hellenistic-Jewish Fragments' },
  { key: 'qumran',      label: '昆蘭古卷',         label_en: 'Qumran' },
]
const GENRE_ORDER_NT: { key: string; label: string; label_en: string }[] = [
  { key: 'gospels',     label: '福音書',           label_en: 'Gospels' },
  { key: 'papyri',      label: '蒲草紙殘片',       label_en: 'Papyrus Fragments' },
  { key: 'acts',        label: '行傳',             label_en: 'Acts' },
  { key: 'epistles',    label: '書信',             label_en: 'Epistles' },
  { key: 'apocalypses', label: '默示錄',           label_en: 'Apocalypses' },
  { key: 'dialogues',   label: '對話錄／諾斯底',   label_en: 'Dialogues / Gnostic' },
  { key: 'misc',        label: '其他',             label_en: 'Misc' },
]

const otDocs = computed(() => docs.value.filter(d => d.testament === 'ot' || d.testament === 'mixed'))
const ntDocs = computed(() => docs.value.filter(d => d.testament === 'nt'))

const testamentTabs = computed(() => [
  { key: 'ot' as Testament, label: '舊約典外', count: otDocs.value.length },
  { key: 'nt' as Testament, label: '新約典外', count: ntDocs.value.length },
])

const docsForActiveTestament = computed(() =>
  activeTestament.value === 'ot' ? otDocs.value : ntDocs.value
)

const genreChips = computed(() => {
  const order = activeTestament.value === 'ot' ? GENRE_ORDER_OT : GENRE_ORDER_NT
  const chips = [{ key: 'all', label: '全部', count: docsForActiveTestament.value.length }]
  for (const g of order) {
    const n = docsForActiveTestament.value.filter(d => d.genre === g.key).length
    if (n > 0) chips.push({ key: g.key, label: g.label, count: n })
  }
  return chips
})

const filteredDocs = computed(() => {
  if (activeGenre.value === 'all') return docsForActiveTestament.value
  return docsForActiveTestament.value.filter(d => d.genre === activeGenre.value)
})

const groupedDocs = computed(() => {
  const order = activeTestament.value === 'ot' ? GENRE_ORDER_OT : GENRE_ORDER_NT
  const groups: { key: string; label: string; label_en: string; items: ApocDoc[] }[] = []
  for (const g of order) {
    const items = filteredDocs.value.filter(d => d.genre === g.key)
    if (items.length > 0) {
      groups.push({ key: g.key, label: g.label, label_en: g.label_en, items })
    }
  }
  return groups
})

function hasEnglish(doc: ApocDoc): boolean {
  const c = doc.section_counts ?? {}
  return Boolean(c.charles_apot || c.mrjames_ntapoc || c.robinson_nh || c.charlesworth_otp)
}
function hasOriginal(doc: ApocDoc): boolean {
  const c = doc.section_counts ?? {}
  return Boolean(c.greek_orig || c.coptic_orig || c.syriac_orig || c.hebrew_orig
    || c.aramaic_orig || c.ethiopic_orig || c.latin_orig)
}

function formatPeriod(low: number | null, high: number | null) {
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
}

// ── Search ───────────────────────────────────────────────────────────────
const searchQ = ref('')
const searchVersion = ref('')
const searchResults = ref<SearchHit[]>([])
const searchTotal = ref(0)
const searchPending = ref(false)
const lastQ = ref('')
const searchActive = computed(() => lastQ.value.length > 0)

async function runSearch() {
  if (!searchQ.value || searchQ.value.length < 2) return
  searchPending.value = true
  lastQ.value = searchQ.value
  try {
    const headers = await authHeaders()
    const res = await $fetch<{ q: string; total: number; results: SearchHit[] }>(
      '/api/apocrypha/search',
      {
        headers,
        query: {
          q: searchQ.value,
          version: searchVersion.value || undefined,
          limit: 100,
        },
      },
    )
    searchResults.value = res.results
    searchTotal.value = res.total
  } catch (e: any) {
    searchResults.value = []
    searchTotal.value = 0
    error.value = e?.message || String(e)
  } finally {
    searchPending.value = false
  }
}

function clearSearch() {
  searchQ.value = ''
  lastQ.value = ''
  searchResults.value = []
  searchTotal.value = 0
}

function docTitle(slug: string) {
  const d = docs.value.find(x => x.slug === slug)
  return d ? d.title_zh : slug
}
function versionLabel(code: string) {
  const v = versions.value.find(x => x.code === code)
  return v ? v.name_zh.replace(/（[^）]*）/g, '').trim() : code
}
function snip(text: string, q: string, win = 140) {
  const idx = text.toLowerCase().indexOf(q.toLowerCase())
  if (idx < 0) return text.slice(0, win * 2)
  const start = Math.max(0, idx - win)
  const end = Math.min(text.length, idx + q.length + win)
  return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '')
}
function highlightMatch(text: string, q: string) {
  if (!q) return text
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const re = new RegExp(`(${escaped})`, 'gi')
  return text.replace(re, '<mark class="bg-yellow-200 text-stone-900 rounded px-0.5">$1</mark>')
}
</script>
