<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <!-- Top nav -->
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink to="/canon-law" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
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
      <span class="text-sm font-semibold text-gray-900 truncate">{{ docData?.document?.title_zh || '教會法規' }}</span>
      <span v-if="docData?.document" class="text-xs text-gray-400 truncate hidden md:inline">{{ docData.document.title_en }}</span>
      <div class="ml-auto flex items-center gap-2 text-xs">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30">‹</button>
        <span class="text-xs text-gray-500 tabular-nums">{{ currentPage }} / {{ totalPages }}</span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30">›</button>
      </div>
    </nav>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- Sidebar backdrop (narrow screens) -->
      <div v-if="sidebarOpen" @click="sidebarOpen = false" class="lg:hidden fixed inset-0 bg-stone-900/40 z-30 transition-opacity"></div>

      <!-- Sidebar: 卷/題 tree -->
      <aside :class="[
        'border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0 transition-transform duration-200',
        sidebarOpen
          ? 'fixed lg:relative inset-y-0 left-0 top-12 lg:top-0 w-72 lg:w-72 z-40 translate-x-0 shadow-xl lg:shadow-none'
          : 'fixed lg:relative -translate-x-full w-0 lg:w-0 lg:opacity-0 lg:overflow-hidden',
      ]">
        <div class="p-3">
          <div class="text-[10px] uppercase tracking-wider text-stone-400 mb-2 px-2">{{ docData?.document?.structure_note || '目錄' }}</div>
          <div v-for="(bk, bi) in tree" :key="bi" class="mb-2">
            <button @click="toggleBook(bi)"
              class="w-full flex items-center gap-1 px-2 py-1.5 rounded text-[13px] font-bold text-stone-900 hover:bg-stone-50 transition">
              <span class="text-stone-500 text-xs w-3 inline-block">{{ expandedBooks.has(bi) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left truncate">{{ bk.label || '（未分卷）' }}</span>
            </button>
            <div v-if="expandedBooks.has(bi)" class="ml-1 mt-0.5 border-l border-stone-100 pl-1">
              <NuxtLink v-for="(ch, ci) in bk.chapters" :key="ci"
                :to="`/canon-law/${slug}?page=${ch.page}`" @click="sidebarOpen = false"
                :class="[
                  'block px-2 py-1 rounded text-[12px] hover:bg-stone-50 transition no-underline truncate',
                  ch.page === currentPage ? 'bg-amber-50 text-amber-800 font-medium' : 'text-stone-700',
                ]">
                <span class="text-stone-300 mr-1">·</span>{{ ch.label || ch.firstLabel }}
              </NuxtLink>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main reading area -->
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-5xl w-full mx-auto px-4 py-6">
          <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
          <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

          <template v-else-if="docData">
            <!-- Document header (page 1) -->
            <header v-if="currentPage === 1" class="mb-6 pb-4 border-b border-gray-200">
              <h1 class="text-2xl font-bold text-gray-900">{{ docData.document.title_zh }}</h1>
              <p class="text-sm text-gray-500 mt-1">
                <span class="font-medium">{{ docData.document.title_en }}</span>
                <span v-if="docData.document.title_lat" class="text-gray-400 ml-2 italic">{{ docData.document.title_lat }}</span>
              </p>
              <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
                <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ traditionLabel(docData.document.tradition) }}</span>
                <span v-if="docData.document.structure_note" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">{{ docData.document.structure_note }}</span>
                <span v-if="docData.document.promulgated_year" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700">{{ docData.document.promulgated_year }}</span>
              </div>
              <p v-if="docData.document.summary_zh" class="mt-3 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3">{{ docData.document.summary_zh }}</p>
            </header>
            <header v-else class="mb-4 flex items-baseline gap-2 flex-wrap">
              <h2 class="text-base font-semibold text-stone-700">{{ docData.document.title_zh }}</h2>
              <span v-if="pageBookLabel" class="text-sm text-amber-700 font-medium">{{ pageBookLabel }}</span>
            </header>

            <!-- Column controls -->
            <div class="grid gap-2 mb-4" :style="{ gridTemplateColumns: gridCols }">
              <div v-for="(col, idx) in columns" :key="idx" class="bg-white border border-gray-200 rounded px-2 py-1 flex items-center gap-1">
                <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
                <select v-model="col.versionCode" class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer">
                  <option v-for="v in optionsForCol(col)" :key="v.code" :value="v.code">{{ v.name_zh }}</option>
                  <option v-if="optionsForCol(col).length === 0" :value="''" disabled>（暫無資料）</option>
                </select>
                <button v-if="columns.length > 1" @click="removeColumn(idx)" class="text-gray-300 hover:text-red-500 text-xs px-1">✕</button>
              </div>
              <button v-if="columns.length < 4" @click="addColumn"
                class="bg-white border border-dashed border-gray-300 rounded px-2 py-1 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700">+ 對照欄</button>
            </div>

            <div v-if="docData.sections.length === 0" class="text-center text-gray-400 py-16 text-sm">此法規尚無任何已匯入版本。</div>

            <!-- Sections (10 per page), with 卷/題 heading bars on change -->
            <div v-else class="space-y-2">
              <template v-for="(s, i) in pagedSections" :key="s.order_index">
                <div v-if="headingBefore(i)" class="pt-3">
                  <div class="bg-gradient-to-r from-amber-100 to-amber-50 border border-amber-200 rounded px-3 py-1.5 text-sm font-semibold text-amber-900">
                    <span v-if="s.book_label">{{ s.book_label }}</span>
                    <span v-if="s.chapter_label" class="text-amber-700 font-normal"> · {{ s.chapter_label }}</span>
                  </div>
                </div>
                <article :id="`section-${s.order_index}`" class="bg-white border border-gray-200 rounded-md overflow-hidden scroll-mt-16">
                  <div class="flex items-center gap-2 px-3 py-1 bg-stone-50 border-b border-stone-100 text-[11px] text-stone-600 font-semibold">
                    {{ s.section_label || ('#' + s.order_index) }}
                  </div>
                  <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: gridCols }">
                    <div v-for="(col, idx) in columns" :key="idx"
                      class="bg-white px-4 py-3 text-[15px] leading-7 text-gray-900 whitespace-pre-line"
                      :class="textClassFor(col.versionCode)">
                      <template v-if="col.versionCode && s.byVersion[col.versionCode]">{{ s.byVersion[col.versionCode] }}</template>
                      <span v-else class="text-gray-300 italic text-xs">—</span>
                    </div>
                  </div>
                </article>
              </template>
            </div>

            <!-- Bottom pagination -->
            <div class="mt-8 flex items-center justify-between">
              <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">← 上一頁</button>
              <span class="text-sm text-gray-500">第 {{ currentPage }} / {{ totalPages }} 頁</span>
              <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">下一頁 →</button>
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

type CVersion = { code: string; name_zh: string; name_en: string; language: string; category: 'chinese' | 'english' | 'source'; public_domain: boolean; display_order: number; is_default_zh: boolean; is_default_en: boolean; is_default_orig: boolean }
type Section = { order_index: number; section_label: string | null; book_label: string | null; chapter_label: string | null; is_heading: boolean; byVersion: Record<string, string> }
type CDoc = { slug: string; title_zh: string; title_zh_short: string | null; title_en: string; title_lat: string | null; tradition: string; corpus: string; structure_note: string | null; promulgated_year: number | null; summary_zh: string | null }
type DocRes = { document: CDoc; sections: Section[] }

const TRADITION_LABEL: Record<string, string> = { catholic: '羅馬天主教', orthodox: '東正教', anglican: '聖公宗', protestant: '新教' }
function traditionLabel(t: string) { return TRADITION_LABEL[t] || t }

const supabase = useSupabaseClient()
const versions = ref<CVersion[]>([])
const docData = ref<DocRes | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)
const sidebarOpen = ref(true)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}
async function load() {
  pending.value = true; error.value = null
  try {
    const headers = await authHeaders()
    const [v, d] = await Promise.all([
      $fetch<CVersion[]>('/api/canon-law/versions', { headers }),
      $fetch<DocRes>('/api/canon-law/document', { headers, query: { slug: slug.value } }),
    ])
    versions.value = v; docData.value = d; columns.value = []
  } catch (e: any) { error.value = e?.message || String(e) } finally { pending.value = false }
}
onMounted(load)
watch(slug, load)
useHead({ title: () => docData.value ? `${docData.value.document.title_zh} — 教會法規` : '教會法規' })

// ── Pagination ───────────────────────────────────────────────────────
const totalPages = computed(() => Math.max(1, Math.ceil((docData.value?.sections.length ?? 0) / PAGE_SIZE)))
const pagedSections = computed(() => {
  if (!docData.value) return [] as Section[]
  const start = (currentPage.value - 1) * PAGE_SIZE
  return docData.value.sections.slice(start, start + PAGE_SIZE)
})
const pageBookLabel = computed(() => pagedSections.value.find(s => s.book_label)?.book_label || '')
function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push(`/canon-law/${slug.value}?page=${p}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}
// Show a heading bar before a section when its book/chapter differs from the previous visible one.
function headingBefore(i: number): boolean {
  const s = pagedSections.value[i]
  if (!s || (!s.book_label && !s.chapter_label)) return false
  const prev = i > 0 ? pagedSections.value[i - 1] : null
  if (!prev) return true
  return prev.book_label !== s.book_label || prev.chapter_label !== s.chapter_label
}

// ── Sidebar tree: book_label → chapter_label, with the page of first section ──
const tree = computed(() => {
  const out: { label: string | null; chapters: { label: string | null; firstLabel: string; page: number }[] }[] = []
  if (!docData.value) return out
  docData.value.sections.forEach((s, idx) => {
    const page = Math.floor(idx / PAGE_SIZE) + 1
    let bk = out[out.length - 1]
    if (!bk || bk.label !== s.book_label) { bk = { label: s.book_label, chapters: [] }; out.push(bk) }
    const lastCh = bk.chapters[bk.chapters.length - 1]
    if (!lastCh || lastCh.label !== s.chapter_label) {
      bk.chapters.push({ label: s.chapter_label, firstLabel: s.section_label || `#${s.order_index}`, page })
    }
  })
  return out
})
const expandedBooks = ref(new Set<number>())
function toggleBook(i: number) { expandedBooks.value.has(i) ? expandedBooks.value.delete(i) : expandedBooks.value.add(i); expandedBooks.value = new Set(expandedBooks.value) }
// Expand the book containing the current page on load / page change.
watch([tree, currentPage], () => {
  tree.value.forEach((bk, bi) => { if (bk.chapters.some(c => c.page === currentPage.value)) expandedBooks.value.add(bi) })
  expandedBooks.value = new Set(expandedBooks.value)
})

// ── Columns (中文 / 英文 / 原文) ───────────────────────────────────────
type ColCategory = 'chinese' | 'english' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])
const CAT_LABEL: Record<ColCategory, string> = { chinese: '中文', english: '英文', source: '原文' }

const availableVersions = computed(() => {
  if (!docData.value || !versions.value) return [] as CVersion[]
  const has = new Set<string>()
  for (const s of docData.value.sections) for (const k of Object.keys(s.byVersion)) has.add(k)
  return versions.value.filter(v => has.has(v.code))
})
function optionsForCol(col: Col) { return availableVersions.value.filter(v => v.category === col.category) }
function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  if (cat === 'chinese') return (avail.find(v => v.is_default_zh) || avail[0]).code
  if (cat === 'english') return (avail.find(v => v.is_default_en) || avail[0]).code
  return (avail.find(v => v.is_default_orig) || avail[0]).code
}
watchEffect(() => {
  if (columns.value.length > 0 || !availableVersions.value.length) return
  const cols: Col[] = []
  for (const cat of ['chinese', 'english', 'source'] as ColCategory[]) {
    const code = pickForCategory(cat)
    if (code) cols.push({ label: CAT_LABEL[cat], category: cat, versionCode: code })
  }
  columns.value = cols.length ? cols : [{ label: '中文', category: 'chinese', versionCode: '' }]
})
function addColumn() {
  if (columns.value.length >= 4) return
  const cat: ColCategory = 'chinese'
  columns.value.push({ label: CAT_LABEL[cat], category: cat, versionCode: pickForCategory(cat) })
}
function removeColumn(i: number) { columns.value.splice(i, 1) }
const gridCols = computed(() => columns.value.map(() => '1fr').join(' '))
function textClassFor(code: string) {
  const v = versions.value.find(x => x.code === code)
  if (!v) return ''
  if (v.language === 'la' || v.language === 'grc') return 'font-serif italic text-gray-800'
  return ''
}
</script>
