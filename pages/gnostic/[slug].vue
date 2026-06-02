<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink to="/gnostic" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <button
        @click="sidebarOpen = !sidebarOpen"
        :class="['flex items-center gap-1 px-2 py-1 rounded text-xs transition border',
          sidebarOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400']"
      ><span>📑</span><span class="hidden sm:inline">目錄</span></button>
      <span class="text-sm font-semibold text-gray-900 truncate">{{ docData?.document?.title_zh || '諾斯底主義文獻' }}</span>
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
      <div v-if="sidebarOpen" @click="sidebarOpen = false" class="lg:hidden fixed inset-0 bg-stone-900/40 z-30 transition-opacity"></div>

      <!-- Sidebar: category → doc tree -->
      <aside :class="['border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0 transition-transform duration-200',
        sidebarOpen ? 'fixed lg:relative inset-y-0 left-0 top-12 lg:top-0 w-72 lg:w-72 z-40 translate-x-0 shadow-xl lg:shadow-none'
          : 'fixed lg:relative -translate-x-full w-0 lg:w-0 lg:opacity-0 lg:overflow-hidden']">
        <div class="p-3">
          <div class="text-[10px] uppercase tracking-wider text-stone-400 mb-2 px-2">諾斯底主義文獻 · {{ allDocs.length }} 篇</div>
          <div v-for="c in categoryGroups" :key="c.key" class="mb-2">
            <button @click="toggleCat(c.key)"
              class="w-full flex items-center gap-1 px-2 py-1.5 rounded text-[13px] font-bold text-stone-900 hover:bg-stone-50 transition">
              <span class="text-stone-500 text-xs w-3 inline-block">{{ expandedCats.has(c.key) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left">{{ c.label }}</span>
              <span class="text-[10px] text-stone-400 font-normal">{{ c.docs.length }}</span>
            </button>
            <div v-if="expandedCats.has(c.key)" class="ml-1 mt-0.5 border-l border-stone-100 pl-1">
              <div v-for="d in c.docs" :key="d.slug" class="mb-0.5">
                <NuxtLink :to="`/gnostic/${d.slug}`" @click="sidebarOpen = false"
                  :class="['w-full flex items-center gap-1 px-2 py-1 rounded text-[12px] hover:bg-stone-50 transition no-underline',
                    d.slug === slug ? 'bg-amber-50 text-amber-800 font-medium' : 'text-stone-800',
                    d.total_sections === 0 ? 'opacity-50' : '']">
                  <span class="flex-1 text-left truncate">{{ d.title_zh_short || d.title_zh }}</span>
                  <span v-if="d.total_sections === 0" class="text-[9px] text-gray-400 italic">未轉錄</span>
                </NuxtLink>
              </div>
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
            <header v-if="currentPage === 1" class="mb-6 pb-4 border-b border-gray-200">
              <h1 class="text-2xl font-bold text-gray-900">{{ docData.document.title_zh }}</h1>
              <p class="text-sm text-gray-500 mt-1">
                <span class="font-medium">{{ docData.document.title_en }}</span>
                <span v-if="docData.document.title_orig" class="text-gray-400 ml-2 italic">{{ docData.document.title_orig }}</span>
              </p>
              <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
                <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ categoryLabel(docData.document.category) }}</span>
                <span v-if="docData.document.language_orig" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700">原文：{{ languageLabel(docData.document.language_orig) }}</span>
                <span v-if="formattedPeriod" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">{{ formattedPeriod }}</span>
                <a v-if="docData.document.source_url" :href="docData.document.source_url" target="_blank" rel="noopener"
                  class="px-2 py-0.5 rounded bg-blue-50 text-blue-600 hover:underline">gnosis.org ↗</a>
              </div>
              <p v-if="docData.document.summary_zh" class="mt-3 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3">{{ docData.document.summary_zh }}</p>
            </header>
            <header v-else class="mb-4 flex items-baseline gap-2 flex-wrap">
              <h2 class="text-base font-semibold text-stone-700">{{ docData.document.title_zh }}</h2>
              <span class="text-xs text-stone-400">段 {{ (currentPage - 1) * PAGE_SIZE + 1 }}–{{ Math.min(currentPage * PAGE_SIZE, docData.sections.length) }}</span>
            </header>

            <!-- Column controls -->
            <div class="grid gap-2 mb-4" :style="{ gridTemplateColumns: gridCols }">
              <div v-for="(col, idx) in columns" :key="idx" class="bg-white border border-gray-200 rounded px-2 py-1 flex items-center gap-1">
                <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
                <select v-model="col.versionCode" class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer">
                  <option v-for="v in optionsForCol(col)" :key="v.code" :value="v.code">{{ v.name_zh }}{{ v.public_domain ? '' : ' ©' }}</option>
                  <option v-if="optionsForCol(col).length === 0" :value="''" disabled>（暫無資料）</option>
                </select>
                <button v-if="columns.length > 1" @click="removeColumn(idx)" class="text-gray-300 hover:text-red-500 text-xs px-1">✕</button>
              </div>
              <button v-if="columns.length < 3" @click="addColumn"
                class="bg-white border border-dashed border-gray-300 rounded px-2 py-1 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700">+ 對照欄</button>
            </div>

            <div v-if="docData.sections.length === 0" class="text-center text-gray-400 py-16 text-sm">此文獻尚未轉錄上架。</div>

            <div v-else class="space-y-2">
              <article v-for="s in pagedSections" :key="s.order_index" :id="`section-${s.order_index}`"
                class="bg-white border border-gray-200 rounded-md overflow-hidden">
                <div v-if="s.section_label" class="flex items-center gap-2 px-3 py-1 bg-stone-50 border-b border-stone-100 text-[10px] text-stone-500">
                  <span class="font-mono">{{ s.section_label }}</span>
                </div>
                <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: gridCols }">
                  <div v-for="(col, idx) in columns" :key="idx"
                    class="bg-white px-4 py-3 text-[15px] leading-7 text-gray-900 whitespace-pre-line">
                    <template v-if="col.versionCode && s.byVersion[col.versionCode]">{{ s.byVersion[col.versionCode] }}</template>
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                </div>
              </article>
            </div>

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
import { CATEGORY_ORDER, categoryLabel, languageLabel } from '~/lib/gnostic-meta'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const slug = computed(() => String(route.params.slug))
const currentPage = computed(() => Math.max(1, Number(route.query.page) || 1))
const PAGE_SIZE = 10

type GVersion = { code: string; name_zh: string; name_en: string; language: string; category: string; public_domain: boolean; display_order: number; is_default_en: boolean; is_default_zh: boolean; is_default_orig: boolean }
type GDoc = { slug: string; title_zh: string; title_zh_short: string | null; title_en: string; category: string; total_sections: number }
type Section = { order_index: number; section_label: string | null; byVersion: Record<string, string> }
type DocRes = { document: GDoc & { title_orig: string | null; language_orig: string | null; composition_low: number | null; composition_high: number | null; summary_zh: string | null; source_url: string | null }; sections: Section[] }

const supabase = useSupabaseClient()
const versions = ref<GVersion[]>([])
const docData = ref<DocRes | null>(null)
const allDocs = ref<GDoc[]>([])
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
    const [v, d, all] = await Promise.all([
      $fetch<GVersion[]>('/api/gnostic/versions', { headers }),
      $fetch<DocRes>('/api/gnostic/document', { headers, query: { slug: slug.value } }),
      $fetch<GDoc[]>('/api/gnostic/documents', { headers }),
    ])
    versions.value = v; docData.value = d; allDocs.value = all; columns.value = []
  } catch (e: any) { error.value = e?.message || String(e) } finally { pending.value = false }
}
onMounted(load)
watch(slug, load)
useHead({ title: () => docData.value ? `${docData.value.document.title_zh} — 諾斯底主義文獻` : '諾斯底主義文獻' })

// ── Pagination ───────────────────────────────────────────────────
const totalPages = computed(() => Math.max(1, Math.ceil((docData.value?.sections.length ?? 0) / PAGE_SIZE)))
const pagedSections = computed(() => {
  if (!docData.value) return []
  const start = (currentPage.value - 1) * PAGE_SIZE
  return docData.value.sections.slice(start, start + PAGE_SIZE)
})
function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push(`/gnostic/${slug.value}?page=${p}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}

// ── Sidebar category tree ────────────────────────────────────────
const expandedCats = ref(new Set<string>())
const categoryGroups = computed(() =>
  CATEGORY_ORDER.map(c => ({ ...c, docs: allDocs.value.filter(d => d.category === c.key) }))
    .filter(c => c.docs.length > 0))
function toggleCat(k: string) {
  expandedCats.value.has(k) ? expandedCats.value.delete(k) : expandedCats.value.add(k)
  expandedCats.value = new Set(expandedCats.value)
}
watch([allDocs, slug], () => {
  const cur = allDocs.value.find(d => d.slug === slug.value)
  if (cur) { expandedCats.value.add(cur.category); expandedCats.value = new Set(expandedCats.value) }
})

// ── Columns (英 + 中) ────────────────────────────────────────────
type ColCategory = 'english' | 'chinese' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])
const availableVersions = computed(() => {
  if (!docData.value || !versions.value) return [] as GVersion[]
  const hasData = new Set<string>()
  for (const s of docData.value.sections) for (const k of Object.keys(s.byVersion)) hasData.add(k)
  return versions.value.filter(v => hasData.has(v.code))
})
function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  if (cat === 'english') { const d = avail.find(v => v.is_default_en); if (d) return d.code }
  if (cat === 'chinese') { const d = avail.find(v => v.is_default_zh); if (d) return d.code }
  if (cat === 'source') { const d = avail.find(v => v.is_default_orig); if (d) return d.code }
  return avail[0].code
}
watchEffect(() => {
  if (!availableVersions.value.length) {
    if (columns.value.length > 0 || !versions.value.length) return
    columns.value = [
      { label: '英文', category: 'english', versionCode: '' },
      { label: '中文', category: 'chinese', versionCode: '' },
    ]
    return
  }
  if (columns.value.length > 0) return
  const cols: Col[] = []
  const en = pickForCategory('english'); cols.push({ label: '英文', category: 'english', versionCode: en })
  const zh = pickForCategory('chinese'); cols.push({ label: '中文', category: 'chinese', versionCode: zh })
  const src = pickForCategory('source'); if (src) cols.push({ label: '原文', category: 'source', versionCode: src })
  columns.value = cols
})
function optionsForCol(col: Col): GVersion[] {
  if (!availableVersions.value.length) return (versions.value ?? []).filter(v => v.category === col.category)
  return availableVersions.value.filter(v => v.category === col.category)
}
function addColumn() {
  const used = new Set(columns.value.map(c => c.versionCode))
  for (const cat of ['source', 'english', 'chinese'] as ColCategory[]) {
    const v = availableVersions.value.find(x => x.category === cat && !used.has(x.code))
    if (v) { columns.value.push({ label: cat === 'source' ? '原文' : cat === 'english' ? '英文' : '中文', category: cat, versionCode: v.code }); return }
  }
}
function removeColumn(idx: number) { columns.value.splice(idx, 1) }
const gridCols = computed(() => `repeat(${columns.value.length}, minmax(0, 1fr))`)

const formattedPeriod = computed(() => {
  const d = docData.value?.document
  if (!d) return ''
  const low = d.composition_low, high = d.composition_high
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
})
</script>
