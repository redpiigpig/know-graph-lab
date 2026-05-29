<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">典外文獻搜索</span>
      <span class="text-xs text-gray-400 ml-1">{{ filteredDocs.length }} 份 / {{ versions.length }} 個版本</span>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📜 典外文獻搜索</h1>
        <p class="text-sm text-gray-500">OT 偽典 / 第二正典 + NT 偽典 + Nag Hammadi 諾斯底 + 昆蘭古卷 — 中文／英文／原文平行對照</p>
      </div>

      <!-- Search box -->
      <div class="mb-8 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
        <form @submit.prevent="runSearch" class="flex items-center gap-2">
          <span class="text-stone-500 text-lg select-none">🔍</span>
          <input
            v-model="searchQ"
            type="text"
            placeholder="搜尋典外文獻內文（中／英／希臘／科普特／敘利亞皆可，例：以諾、Enoch、πνεῦμα）"
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

      <!-- Category filter -->
      <div v-if="!searchActive" class="flex flex-wrap items-center gap-2 mb-6 text-xs">
        <span class="text-gray-500 mr-1">類別：</span>
        <button
          v-for="opt in categoryOpts"
          :key="opt.key"
          @click="activeCategory = opt.key"
          class="px-3 py-1.5 rounded-full border transition"
          :class="activeCategory === opt.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ opt.label }} ({{ opt.count }})</button>
      </div>

      <!-- Loading / error -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <!-- Documents grouped by category (hidden while searching) -->
      <div v-else-if="!searchActive">
        <div v-for="group in groupedDocs" :key="group.key" class="mt-6">
          <h2 class="text-sm font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-1">
            {{ group.label }}
            <span class="text-xs text-gray-400 font-normal">{{ group.items.length }} 份</span>
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
                <span v-if="doc.section_counts?.charles_apot || doc.section_counts?.mrjames_ntapoc || doc.section_counts?.robinson_nh || doc.section_counts?.charlesworth_otp"
                      class="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">英</span>
                <span v-if="doc.section_counts?.greek_orig || doc.section_counts?.coptic_orig || doc.section_counts?.syriac_orig || doc.section_counts?.hebrew_orig || doc.section_counts?.aramaic_orig || doc.section_counts?.ethiopic_orig || doc.section_counts?.latin_orig"
                      class="px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">原文</span>
                <span v-if="doc.composition_low" class="text-gray-400 ml-auto">
                  {{ formatPeriod(doc.composition_low, doc.composition_high) }}
                </span>
              </div>
            </NuxtLink>
          </div>
        </div>

        <div v-if="filteredDocs.length === 0" class="text-center text-gray-400 py-12 text-sm">
          所選類別內沒有文獻
        </div>
      </div>

      <div v-if="!searchActive" class="mt-12 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>中文資料來源：王曉朝主編《基督教典外文獻》10 冊（基督教文藝出版社 2008-2013）— OT 偽典 6 + NT 偽典 4。</p>
        <p class="mt-1">英譯：Charles APOT 1913 (PD) / M.R. James 1924 (PD) / Charlesworth OTP 1983-85 © / Robinson NHL 1977 ©；原文：Schwartz/Nestle critical editions + Nag Hammadi Coptic facsimiles。多數英譯與原文欄位仍待補。</p>
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

// ── Category filter ──────────────────────────────────────────────────────
type CatKey = 'all' | 'ot_apocrypha' | 'ot_pseudepigrapha' | 'nt_apocrypha' | 'nag_hammadi' | 'qumran'
const activeCategory = ref<CatKey>('all')

const categoryOpts = computed(() => {
  const all = docs.value
  return [
    { key: 'all' as const,               label: '全部',          count: all.length },
    { key: 'ot_apocrypha' as const,      label: 'OT 第二正典',   count: all.filter(d => d.category === 'ot_apocrypha').length },
    { key: 'ot_pseudepigrapha' as const, label: 'OT 偽典',       count: all.filter(d => d.category === 'ot_pseudepigrapha').length },
    { key: 'nt_apocrypha' as const,      label: 'NT 偽典',       count: all.filter(d => d.category === 'nt_apocrypha').length },
    { key: 'nag_hammadi' as const,       label: 'Nag Hammadi',   count: all.filter(d => d.category === 'nag_hammadi').length },
    { key: 'qumran' as const,            label: '昆蘭古卷',       count: all.filter(d => d.category === 'qumran').length },
  ]
})

const filteredDocs = computed(() => {
  if (activeCategory.value === 'all') return docs.value
  return docs.value.filter(d => d.category === activeCategory.value)
})

const groupedDocs = computed(() => {
  const groups: { key: string; label: string; items: ApocDoc[] }[] = [
    { key: 'ot_apocrypha',      label: 'OT 第二正典 / 次經', items: [] },
    { key: 'ot_pseudepigrapha', label: 'OT 偽典',             items: [] },
    { key: 'qumran',            label: '昆蘭古卷',             items: [] },
    { key: 'nt_apocrypha',      label: 'NT 偽典',             items: [] },
    { key: 'nag_hammadi',       label: 'Nag Hammadi 諾斯底', items: [] },
    { key: 'lost_gospel',       label: '失傳福音書',           items: [] },
  ]
  for (const d of filteredDocs.value) {
    const g = groups.find(g => g.key === d.category)
    if (g) g.items.push(d)
  }
  return groups.filter(g => g.items.length > 0)
})

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
