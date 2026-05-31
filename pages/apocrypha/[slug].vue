<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <!-- Top nav -->
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink to="/apocrypha" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <button
        @click="sidebarOpen = !sidebarOpen"
        :class="[
          'flex items-center gap-1 px-2 py-1 rounded text-xs transition border',
          sidebarOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400',
        ]"
      >
        <span>📑</span><span class="hidden sm:inline">目錄</span>
      </button>
      <span class="text-sm font-semibold text-gray-900 truncate">{{ docData?.document?.title_zh || '典外文獻' }}</span>
      <span v-if="docData?.document" class="text-xs text-gray-400 truncate hidden md:inline">{{ docData.document.title_en }}</span>
      <div class="ml-auto flex items-center gap-2 text-xs">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30"
        >‹</button>
        <span class="text-xs text-gray-500 tabular-nums">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30"
        >›</button>
      </div>
    </nav>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- Sidebar backdrop (narrow screens only) -->
      <div
        v-if="sidebarOpen"
        @click="sidebarOpen = false"
        class="lg:hidden fixed inset-0 bg-stone-900/40 z-30 transition-opacity"
      ></div>

      <!-- Sidebar: doc tree -->
      <aside
        :class="[
          'border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0 transition-transform duration-200',
          sidebarOpen
            ? 'fixed lg:relative inset-y-0 left-0 top-12 lg:top-0 w-72 lg:w-72 z-40 translate-x-0 shadow-xl lg:shadow-none'
            : 'fixed lg:relative -translate-x-full w-0 lg:w-0 lg:opacity-0 lg:overflow-hidden',
        ]"
      >
        <div class="p-3">
          <div class="text-[10px] uppercase tracking-wider text-stone-400 mb-2 px-2">典外文獻 · {{ allDocs.length }} 卷</div>

          <div v-for="t in testaments" :key="t.key" class="mb-3">
            <button
              @click="toggleTestament(t.key)"
              class="w-full flex items-center gap-1 px-2 py-1.5 rounded text-[13px] font-bold text-stone-900 hover:bg-stone-50 transition"
            >
              <span class="text-stone-500 text-xs w-3 inline-block">{{ expandedTestaments.has(t.key) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left">{{ t.label }}</span>
              <span class="text-[10px] text-stone-400 font-normal">{{ t.docCount }}</span>
            </button>
            <div v-if="expandedTestaments.has(t.key)" class="ml-1 mt-0.5 border-l border-stone-100 pl-1">
              <div v-for="g in t.genres" :key="g.key" class="mb-1.5">
                <button
                  @click="toggleGenre(t.key, g.key)"
                  class="w-full flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold text-stone-700 hover:bg-stone-50 transition"
                >
                  <span class="text-stone-400 text-[10px] w-3 inline-block">{{ isGenreOpen(t.key, g.key) ? '▾' : '▸' }}</span>
                  <span class="flex-1 text-left">{{ g.label }}</span>
                  <span class="text-[10px] text-stone-400 font-normal">{{ g.docs.length }}</span>
                </button>
                <div v-if="isGenreOpen(t.key, g.key)" class="ml-1 mt-0.5 border-l border-stone-100 pl-1">
                  <div v-for="d in g.docs" :key="d.slug" class="mb-0.5">
                    <button
                      @click="toggleDoc(d.slug)"
                      :class="[
                        'w-full flex items-center gap-1 px-2 py-1 rounded text-[12px] hover:bg-stone-50 transition',
                        d.slug === slug ? 'bg-amber-50 text-amber-800 font-medium' : 'text-stone-800',
                      ]"
                    >
                      <span class="text-stone-300 text-[10px] w-3 inline-block">{{ expandedDocs.has(d.slug) ? '▾' : '▸' }}</span>
                      <span class="flex-1 text-left truncate">{{ d.title_zh_short || d.title_zh }}</span>
                      <span v-if="d.total_sections === 0" class="text-[9px] text-gray-300">—</span>
                    </button>
                    <!-- Expanded doc → show page list -->
                    <div v-if="expandedDocs.has(d.slug)" class="ml-3 mt-0.5 space-y-0.5">
                      <NuxtLink
                        v-for="i in docPageCount(d)"
                        :key="i"
                        :to="`/apocrypha/${d.slug}?page=${i}`"
                        @click="sidebarOpen = false"
                        :class="[
                          'block px-2 py-0.5 rounded text-[11px] hover:bg-stone-50 transition no-underline',
                          d.slug === slug && i === currentPage
                            ? 'bg-stone-900 text-white font-medium'
                            : 'text-stone-500',
                        ]"
                      >
                        <span class="text-stone-300 mr-1">·</span>節 {{ (i - 1) * PAGE_SIZE + 1 }}–{{ Math.min(i * PAGE_SIZE, d.total_sections) }}
                      </NuxtLink>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main reading area -->
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-5xl w-full mx-auto px-4 py-6">
          <!-- Loading / error -->
          <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
          <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

          <template v-else-if="docData">
            <!-- Document header (only on page 1) -->
            <header v-if="currentPage === 1" class="mb-6 pb-4 border-b border-gray-200">
              <h1 class="text-2xl font-bold text-gray-900">{{ docData.document.title_zh }}</h1>
              <p class="text-sm text-gray-500 mt-1">
                <span class="font-medium">{{ docData.document.title_en }}</span>
                <span v-if="docData.document.title_orig" class="text-gray-400 ml-2 italic">{{ docData.document.title_orig }}</span>
              </p>
              <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
                <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ categoryLabel(docData.document.category) }}</span>
                <span v-if="docData.document.language_orig" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700">
                  原文：{{ languageLabel(docData.document.language_orig) }}
                </span>
                <span v-if="formattedPeriod" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">
                  {{ formattedPeriod }}
                </span>
                <span v-for="(accepted, key) in canonChips" :key="key" v-show="accepted" class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                  {{ canonLabel(key) }}
                </span>
              </div>
              <p v-if="docData.document.summary_zh" class="mt-3 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3">
                {{ docData.document.summary_zh }}
              </p>
            </header>

            <!-- Page header on subsequent pages -->
            <header v-else class="mb-4 flex items-baseline gap-2">
              <h2 class="text-base font-semibold text-stone-700">{{ docData.document.title_zh }}</h2>
              <span class="text-xs text-stone-400">節 {{ (currentPage - 1) * PAGE_SIZE + 1 }}–{{ Math.min(currentPage * PAGE_SIZE, docData.sections.length) }}</span>
            </header>

            <!-- Column controls -->
            <div class="grid gap-2 mb-4" :style="{ gridTemplateColumns: gridCols }">
              <div
                v-for="(col, idx) in columns"
                :key="idx"
                class="bg-white border border-gray-200 rounded px-2 py-1 flex items-center gap-1"
              >
                <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
                <select v-model="col.versionCode" class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer">
                  <option v-for="v in optionsForCol(col)" :key="v.code" :value="v.code">
                    {{ v.name_zh.replace(/（[^）]*）/g, '').trim() }}{{ v.public_domain ? '' : ' ©' }}
                  </option>
                  <option v-if="optionsForCol(col).length === 0" :value="''" disabled>（暫無資料）</option>
                </select>
                <button v-if="columns.length > 1" @click="removeColumn(idx)" class="text-gray-300 hover:text-red-500 text-xs px-1">✕</button>
              </div>
              <button
                v-if="columns.length < 4"
                @click="addColumn"
                class="bg-white border border-dashed border-gray-300 rounded px-2 py-1 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700"
              >+ 對照欄</button>
            </div>

            <!-- Empty -->
            <div v-if="docData.sections.length === 0" class="text-center text-gray-400 py-16 text-sm">
              此文獻尚無任何已上架版本。
            </div>

            <!-- Sections (10 per page) -->
            <div v-else class="space-y-2">
              <article
                v-for="s in pagedSections"
                :key="s.order_index"
                :id="`section-${s.order_index}`"
                class="bg-white border border-gray-200 rounded-md overflow-hidden"
              >
                <div v-if="s.page_number" class="flex items-center gap-2 px-3 py-1 bg-stone-50 border-b border-stone-100 text-[10px] text-stone-500">
                  <span class="font-mono">p.{{ s.page_number }}</span>
                </div>
                <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: gridCols }">
                  <div
                    v-for="(col, idx) in columns"
                    :key="idx"
                    class="bg-white px-4 py-3 text-[15px] leading-7 text-gray-900 whitespace-pre-line"
                    :class="textClassFor(col.versionCode)"
                  >
                    <template v-if="col.versionCode && s.byVersion[col.versionCode]">
                      <span v-html="renderWithFootnotes(s.byVersion[col.versionCode], s.order_index)" />
                    </template>
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                </div>
              </article>
            </div>

            <!-- Footnote consolidation at page bottom -->
            <section v-if="footnotesOnPage.length > 0" class="mt-8 pt-4 border-t-2 border-stone-300 text-xs leading-relaxed text-gray-700">
              <div class="font-semibold text-stone-700 mb-2">註釋</div>
              <ol class="space-y-1 list-none pl-0">
                <li v-for="f in footnotesOnPage" :key="f.id" :id="`fn-${f.id}`" class="flex gap-2">
                  <a :href="`#fnref-${f.id}`" class="text-amber-700 hover:underline shrink-0 font-mono font-semibold">{{ f.marker }}</a>
                  <span v-if="f.def" class="text-gray-700">{{ f.def }}</span>
                  <span v-else class="text-gray-400 italic">（編號 {{ f.marker }} 的註釋未抽到）</span>
                </li>
              </ol>
            </section>

            <!-- Bottom pagination -->
            <div class="mt-8 flex items-center justify-between">
              <button
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage <= 1"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30"
              >← 上一頁</button>
              <span class="text-sm text-gray-500">
                第 {{ currentPage }} / {{ totalPages }} 頁
              </span>
              <button
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage >= totalPages"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30"
              >下一頁 →</button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const slug = computed(() => String(route.params.slug))
const currentPage = computed(() => Math.max(1, Number(route.query.page) || 1))

const PAGE_SIZE = 10

type ApocVersion = {
  code: string
  name_zh: string
  name_en: string
  language: string
  language_zh: string | null
  category: 'chinese' | 'english' | 'source' | 'ancient'
  public_domain: boolean
  display_order: number
  is_default_zh: boolean
  is_default_en: boolean
  is_default_orig: boolean
}
type ApocDoc = {
  slug: string
  title_zh: string
  title_zh_short: string | null
  title_en: string
  category: string
  testament: 'ot' | 'nt' | 'mixed'
  genre: string | null
  total_sections: number
  section_counts: Record<string, number>
}
type Section = {
  order_index: number
  section_label: string | null
  page_number: number | null
  chapter: number | null
  byVersion: Record<string, string>
  footnotesByVersion?: Record<string, Record<string, string>>
}
type DocRes = {
  document: ApocDoc & {
    title_orig: string | null
    language_orig: string | null
    composition_low: number | null
    composition_high: number | null
    canon_status_jsonb: Record<string, boolean> | null
    summary_zh: string | null
  }
  sections: Section[]
}

const supabase = useSupabaseClient()
const versions = ref<ApocVersion[]>([])
const docData = ref<DocRes | null>(null)
const allDocs = ref<ApocDoc[]>([])
const pending = ref(true)
const error = ref<string | null>(null)
const sidebarOpen = ref(true)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load() {
  pending.value = true
  error.value = null
  try {
    const headers = await authHeaders()
    const [v, d, all] = await Promise.all([
      $fetch<ApocVersion[]>('/api/apocrypha/versions', { headers }),
      $fetch<DocRes>('/api/apocrypha/document', { headers, query: { slug: slug.value } }),
      $fetch<ApocDoc[]>('/api/apocrypha/documents', { headers }),
    ])
    versions.value = v
    docData.value = d
    allDocs.value = all
    columns.value = []  // reset; watchEffect picks defaults
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}
onMounted(load)
watch(slug, load)

useHead({
  title: () => docData.value ? `${docData.value.document.title_zh} — 典外文獻` : '典外文獻',
})

// ── Pagination ───────────────────────────────────────────────────────
const totalPages = computed(() => {
  const n = docData.value?.sections.length ?? 0
  return Math.max(1, Math.ceil(n / PAGE_SIZE))
})
const pagedSections = computed(() => {
  if (!docData.value) return []
  const start = (currentPage.value - 1) * PAGE_SIZE
  return docData.value.sections.slice(start, start + PAGE_SIZE)
})
function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push(`/apocrypha/${slug.value}?page=${p}`)
  // Scroll to top
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}

// ── Sidebar tree ─────────────────────────────────────────────────────
const GENRE_ORDER_OT = [
  { key: 'apocalyptic', label: '啟示文學' },
  { key: 'testaments',  label: '族長遺訓' },
  { key: 'legends',     label: '重述聖經／傳奇' },
  { key: 'wisdom',      label: '智慧文獻' },
  { key: 'deutero',     label: '隱藏經卷／第二正典' },
  { key: 'hymns',       label: '詩歌頌詞' },
  { key: 'fragments',   label: '希臘化猶太斷片' },
  { key: 'qumran',      label: '昆蘭古卷' },
]
const GENRE_ORDER_NT = [
  { key: 'gospels',     label: '福音書' },
  { key: 'papyri',      label: '蒲草紙殘片' },
  { key: 'acts',        label: '行傳' },
  { key: 'epistles',    label: '書信' },
  { key: 'apocalypses', label: '啟示錄' },
  { key: 'dialogues',   label: '對話錄／諾斯底' },
  { key: 'misc',        label: '其他' },
]

function buildGenres(testament: 'ot' | 'nt') {
  const docs = allDocs.value.filter(d => testament === 'ot' ? (d.testament === 'ot' || d.testament === 'mixed') : d.testament === 'nt')
  const order = testament === 'ot' ? GENRE_ORDER_OT : GENRE_ORDER_NT
  return order
    .map(g => ({ ...g, docs: docs.filter(d => d.genre === g.key) }))
    .filter(g => g.docs.length > 0)
}

const testaments = computed(() => [
  { key: 'ot' as const, label: '舊約典外', genres: buildGenres('ot'), docCount: allDocs.value.filter(d => d.testament !== 'nt').length },
  { key: 'nt' as const, label: '新約典外', genres: buildGenres('nt'), docCount: allDocs.value.filter(d => d.testament === 'nt').length },
])

const expandedTestaments = ref(new Set<'ot' | 'nt'>(['ot', 'nt']))
const expandedGenres = ref(new Set<string>())   // keys: `${testament}:${genre}`
const expandedDocs = ref(new Set<string>())

function toggleTestament(k: 'ot' | 'nt') {
  expandedTestaments.value.has(k) ? expandedTestaments.value.delete(k) : expandedTestaments.value.add(k)
  expandedTestaments.value = new Set(expandedTestaments.value)
}
function toggleGenre(t: 'ot' | 'nt', g: string) {
  const key = `${t}:${g}`
  expandedGenres.value.has(key) ? expandedGenres.value.delete(key) : expandedGenres.value.add(key)
  expandedGenres.value = new Set(expandedGenres.value)
}
function isGenreOpen(t: 'ot' | 'nt', g: string): boolean {
  return expandedGenres.value.has(`${t}:${g}`)
}
function toggleDoc(s: string) {
  expandedDocs.value.has(s) ? expandedDocs.value.delete(s) : expandedDocs.value.add(s)
  expandedDocs.value = new Set(expandedDocs.value)
}
function docPageCount(d: ApocDoc): number {
  return Math.max(1, Math.ceil((d.total_sections || 0) / PAGE_SIZE))
}

// Auto-expand the chain for current doc on first load
watch([allDocs, slug], () => {
  const cur = allDocs.value.find(d => d.slug === slug.value)
  if (!cur) return
  const tk = (cur.testament === 'nt' ? 'nt' : 'ot') as 'ot' | 'nt'
  expandedTestaments.value.add(tk)
  expandedTestaments.value = new Set(expandedTestaments.value)
  if (cur.genre) {
    expandedGenres.value.add(`${tk}:${cur.genre}`)
    expandedGenres.value = new Set(expandedGenres.value)
  }
  expandedDocs.value.add(cur.slug)
  expandedDocs.value = new Set(expandedDocs.value)
})

// ── Columns ─────────────────────────────────────────────────────────
type ColCategory = 'chinese' | 'english' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])

const availableVersions = computed(() => {
  if (!docData.value || !versions.value) return [] as ApocVersion[]
  const hasData = new Set<string>()
  for (const s of docData.value.sections) {
    for (const k of Object.keys(s.byVersion)) hasData.add(k)
  }
  return versions.value.filter(v => hasData.has(v.code))
})

function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  if (cat === 'chinese') {
    const def = avail.find(v => v.is_default_zh); if (def) return def.code
  }
  if (cat === 'english') {
    const def = avail.find(v => v.is_default_en); if (def) return def.code
  }
  if (cat === 'source') {
    const langMap: Record<string, string> = {
      greek: 'greek_orig', hebrew: 'hebrew_orig', aramaic: 'aramaic_orig',
      coptic: 'coptic_orig', syriac: 'syriac_orig', ethiopic: 'ethiopic_orig',
      latin: 'latin_orig',
    }
    const origLang = docData.value?.document.language_orig || ''
    const code = langMap[origLang]
    if (code) {
      const v = avail.find(x => x.code === code); if (v) return v.code
    }
    const def = avail.find(v => v.is_default_orig); if (def) return def.code
  }
  return avail[0].code
}

watchEffect(() => {
  if (!availableVersions.value.length) {
    if (columns.value.length > 0 || !versions.value.length) return
    if (versions.value.find(v => v.category === 'chinese')) {
      columns.value = [{ label: '中文', category: 'chinese', versionCode: '' }]
    }
    return
  }
  if (columns.value.length > 0) return
  const cols: Col[] = []
  const zh = pickForCategory('chinese')
  cols.push({ label: '中文', category: 'chinese', versionCode: zh })
  const en = pickForCategory('english')
  if (en) cols.push({ label: '英文', category: 'english', versionCode: en })
  const src = pickForCategory('source')
  if (src) cols.push({ label: '原文', category: 'source', versionCode: src })
  if (!en) cols.push({ label: '英文', category: 'english', versionCode: '' })
  if (!src) cols.push({ label: '原文', category: 'source', versionCode: '' })
  columns.value = cols
})

function optionsForCol(col: Col): ApocVersion[] {
  if (!availableVersions.value.length) {
    return (versions.value ?? []).filter(v => v.category === col.category)
  }
  return availableVersions.value.filter(v => v.category === col.category)
}
function addColumn() {
  const used = new Set(columns.value.map(c => c.versionCode))
  for (const cat of ['source', 'english', 'chinese'] as ColCategory[]) {
    const v = availableVersions.value.find(x => x.category === cat && !used.has(x.code))
    if (v) {
      const label = cat === 'source' ? '原文' : cat === 'english' ? '英文' : '中文'
      columns.value.push({ label, category: cat, versionCode: v.code }); return
    }
  }
}
function removeColumn(idx: number) { columns.value.splice(idx, 1) }
const gridCols = computed(() => `repeat(${columns.value.length}, minmax(0, 1fr))`)
function textClassFor(code: string) {
  const v = versions.value?.find(x => x.code === code)
  if (!v) return ''
  if (v.language === 'hbo') return 'font-serif rtl-text text-right'
  if (v.language === 'grc') return 'font-serif'
  if (v.language === 'lat') return 'font-serif italic'
  if (v.language === 'syr') return 'font-serif rtl-text text-right'
  return ''
}

// ── Footnote extraction & rendering ──────────────────────────────
// Unicode superscript digits map to ASCII for lookup in footnote_defs.
const SUPERSCRIPT_RE = /([⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g
const SUPER_TO_ASCII: Record<string, string> = {
  '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
  '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
}
function superToAscii(s: string): string {
  return s.split('').map(c => SUPER_TO_ASCII[c] ?? c).join('')
}

type Footnote = { id: string; marker: string; def: string | null }

// Collect footnotes from the 10 sections on this page, looking up definitions
// from each section's footnote_defs (per version_code).
const footnotesOnPage = computed<Footnote[]>(() => {
  const seen = new Map<string, Footnote>()  // id → footnote
  for (const s of pagedSections.value) {
    for (const [versionCode, text] of Object.entries(s.byVersion)) {
      const matches = text.match(SUPERSCRIPT_RE)
      if (!matches) continue
      for (const m of matches) {
        const marker_ascii = superToAscii(m)
        const id = `${s.order_index}-${marker_ascii}`
        if (seen.has(id)) continue
        const defMap = s.footnotesByVersion?.[versionCode] ?? {}
        const def = defMap[marker_ascii] ?? null
        seen.set(id, { id, marker: m, def })
      }
    }
  }
  // Sort by section order then by numeric marker
  return Array.from(seen.values()).sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }))
})

function renderWithFootnotes(text: string, sectionIdx: number): string {
  const esc = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return esc.replace(SUPERSCRIPT_RE, (m) => {
    const id = `${sectionIdx}-${superToAscii(m)}`
    return `<a href="#fn-${id}" id="fnref-${id}" class="text-amber-700 hover:underline">${m}</a>`
  })
}

// ── Labels ─────────────────────────────────────────────────────────
const CATEGORY_LABEL: Record<string, string> = {
  ot_apocrypha: 'OT 次經 / 第二正典',
  ot_pseudepigrapha: 'OT 偽典',
  nt_apocrypha: 'NT 偽典',
  nag_hammadi: 'Nag Hammadi 諾斯底',
  qumran: '昆蘭古卷',
  lost_gospel: '失傳福音書',
}
function categoryLabel(c: string) { return CATEGORY_LABEL[c] || c }

const LANG_LABEL: Record<string, string> = {
  greek: '希臘文', hebrew: '希伯來文', aramaic: '亞蘭文',
  coptic: '科普特文', syriac: '敘利亞文', ethiopic: "Ge'ez 文", latin: '拉丁文',
}
function languageLabel(l: string) { return LANG_LABEL[l] || l }

const CANON_LABEL: Record<string, string> = {
  protestant: '新教接受', catholic: '天主教第二正典', orthodox: '東正教接受',
  ethiopian: '衣索匹亞正典', syriac: '敘利亞接受',
}
function canonLabel(k: string) { return CANON_LABEL[k] || k }
const canonChips = computed(() => docData.value?.document.canon_status_jsonb || {})
const formattedPeriod = computed(() => {
  const d = docData.value?.document
  if (!d) return ''
  const low = d.composition_low; const high = d.composition_high
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
})
</script>

<style scoped>
.rtl-text {
  direction: rtl;
  unicode-bidi: bidi-override;
}
:deep(sup) {
  font-size: 0.7em;
  vertical-align: super;
}
</style>
