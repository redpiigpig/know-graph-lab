<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <AppHeader :title="docData?.document?.title_zh || '典外文獻'" :back="{ to: '/apocrypha', label: '典外文獻' }" container-class="max-w-7xl">
      <template #actions>
        <span class="text-xs text-gray-500 truncate">{{ currentLabel }}</span>
        <button v-if="prevTarget" @click="goPrev"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 text-xs">← {{ chapterMode ? '上章' : '上頁' }}</button>
        <button v-if="nextTarget" @click="goNext"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 text-xs">{{ chapterMode ? '下章' : '下頁' }} →</button>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <template v-else-if="docData">
        <!-- Document header + collapsible intro -->
        <header class="mb-4 pb-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-900">{{ docData.document.title_zh }}</h1>
          <p class="text-sm text-gray-500 mt-1">
            <span class="font-medium">{{ docData.document.title_en }}</span>
            <span v-if="docData.document.title_orig" class="text-gray-400 ml-2 italic">{{ docData.document.title_orig }}</span>
          </p>
          <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
            <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ categoryLabel(docData.document.category) }}</span>
            <span v-if="docData.document.language_orig" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700">原文：{{ languageLabel(docData.document.language_orig) }}</span>
            <span v-if="formattedPeriod" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">{{ formattedPeriod }}</span>
            <span v-for="(accepted, key) in canonChips" :key="key" v-show="accepted" class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">{{ canonLabel(key) }}</span>
          </div>
          <div v-if="introText" class="mt-3">
            <button @click="introOpen = !introOpen" class="flex items-center gap-1.5 text-xs font-medium text-stone-600 hover:text-stone-900 transition">
              <span class="text-stone-400">{{ introOpen ? '▾' : '▸' }}</span>
              <span>簡介{{ introOpen ? '' : '（點開）' }}</span>
            </button>
            <div v-if="introOpen" class="mt-2 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3 whitespace-pre-line">{{ introText }}</div>
          </div>
        </header>

        <!-- Chapter picker chip row (chapter mode) -->
        <div v-if="chapterMode" class="flex flex-wrap items-center gap-1 mb-4">
          <span class="text-xs text-gray-500 mr-1">章：</span>
          <button v-for="ch in chapterNums" :key="ch" @click="goToChapter(ch)"
            class="text-[11px] px-2 py-0.5 rounded border transition tabular-nums"
            :class="ch === currentChapter ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'">{{ ch }}</button>
        </div>
        <!-- Page picker (legacy docs without chapter structure) -->
        <div v-else-if="totalPages > 1" class="flex flex-wrap items-center gap-1 mb-4">
          <span class="text-xs text-gray-500 mr-1">頁：</span>
          <button v-for="p in totalPages" :key="p" @click="goToPage(p)"
            class="text-[11px] px-2 py-0.5 rounded border transition tabular-nums"
            :class="p === currentPage ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'">{{ p }}</button>
        </div>

        <!-- Column controls -->
        <div class="grid gap-3 mb-4" :style="{ gridTemplateColumns: gridCols }">
          <div v-for="(col, idx) in columns" :key="idx" class="bg-white border border-gray-200 rounded-md px-2 py-1.5 flex items-center gap-1">
            <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
            <select v-model="col.versionCode" class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="v in optionsForCol(col)" :key="v.code" :value="v.code">{{ v.name_zh.replace(/（[^）]*）/g, '').trim() }}{{ v.public_domain ? '' : ' ©' }}</option>
              <option v-if="optionsForCol(col).length === 0" :value="''" disabled>（暫無資料）</option>
            </select>
            <button v-if="columns.length > 1" @click="removeColumn(idx)" class="text-gray-300 hover:text-red-500 text-xs px-1" title="移除此欄">✕</button>
          </div>
          <button v-if="columns.length < 4" @click="addColumn"
            class="bg-white border border-dashed border-gray-300 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700">+ 對照欄</button>
        </div>

        <div v-if="docData.sections.length === 0" class="text-center text-gray-400 py-16 text-sm">此文獻尚無任何已上架版本。</div>

        <!-- ── Chapter mode: one chapter per view, per-verse rows ── -->
        <template v-else-if="chapterMode">
          <h2 class="text-lg font-bold text-stone-800 mb-3">第 {{ currentChapter }} 章</h2>
          <div class="space-y-1.5">
            <article v-for="s in versesOfChapter(currentChapter)" :key="s.order_index" :id="`section-${s.order_index}`"
              class="bg-white border border-gray-200 rounded-md overflow-hidden">
              <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: `auto ${gridCols}` }">
                <div class="bg-stone-50 px-2 py-2 text-xs font-mono font-semibold text-amber-700/80 flex items-start tabular-nums select-none">{{ s.verse }}</div>
                <div v-for="(col, idx) in columns" :key="idx"
                  class="bg-white px-3 py-2 text-[15px] leading-7 text-gray-900 whitespace-pre-line"
                  :class="textClassFor(col.versionCode)">
                  <template v-if="col.versionCode && s.byVersion[col.versionCode]">
                    <span v-html="renderWithFootnotes(s.byVersion[col.versionCode], s.order_index)" />
                  </template>
                  <span v-else class="text-gray-300 italic text-xs">—</span>
                </div>
              </div>
            </article>
          </div>

          <section v-if="footnotesOnPage.length > 0" class="mt-6 pt-4 border-t-2 border-stone-300 text-xs leading-relaxed text-gray-700">
            <div class="font-semibold text-stone-700 mb-2">註釋</div>
            <ol class="space-y-1 list-none pl-0">
              <li v-for="f in footnotesOnPage" :key="f.id" :id="`fn-${f.id}`" class="flex gap-2">
                <a :href="`#fnref-${f.id}`" class="text-amber-700 hover:underline shrink-0 font-mono font-semibold">{{ f.marker }}</a>
                <span v-if="f.def" class="text-gray-700">{{ f.def }}</span>
              </li>
            </ol>
          </section>

          <div class="mt-8 flex items-center justify-between">
            <button @click="goPrev" :disabled="!prevTarget"
              class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">← 上章</button>
            <span class="text-sm text-gray-500">第 {{ currentChapter }} 章 · {{ chIdx + 1 }}/{{ chapterNums.length }}</span>
            <button @click="goNext" :disabled="!nextTarget"
              class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">下章 →</button>
          </div>
        </template>

        <!-- ── Legacy mode: page blocks (docs not yet rebuilt to chapter:verse) ── -->
        <template v-else>
          <div class="mb-3 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded px-3 py-1.5">這卷尚未逐節重整（仍為整頁 OCR）；逐節對照陸續補上。</div>
          <div class="space-y-2">
            <article v-for="s in pagedLegacy" :key="s.order_index" :id="`section-${s.order_index}`" class="bg-white border border-gray-200 rounded-md overflow-hidden">
              <div v-if="s.page_number" class="flex items-center gap-2 px-3 py-1 bg-stone-50 border-b border-stone-100 text-[10px] text-stone-500"><span class="font-mono">p.{{ s.page_number }}</span></div>
              <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: gridCols }">
                <div v-for="(col, idx) in columns" :key="idx" class="bg-white px-4 py-3 text-[15px] leading-7 text-gray-900 whitespace-pre-line" :class="textClassFor(col.versionCode)">
                  <template v-if="col.versionCode && s.byVersion[col.versionCode]"><span v-html="renderWithFootnotes(s.byVersion[col.versionCode], s.order_index)" /></template>
                  <span v-else class="text-gray-300 italic text-xs">—</span>
                </div>
              </div>
            </article>
          </div>
          <div class="mt-8 flex items-center justify-between">
            <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1" class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">← 上一頁</button>
            <span class="text-sm text-gray-500">第 {{ currentPage }} / {{ totalPages }} 頁</span>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages" class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">下一頁 →</button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const slug = computed(() => String(route.params.slug))

const LEGACY_PAGE_SIZE = 10

type ApocVersion = {
  code: string; name_zh: string; name_en: string; language: string; language_zh: string | null
  category: 'chinese' | 'english' | 'source' | 'ancient'
  public_domain: boolean; display_order: number
  is_default_zh: boolean; is_default_en: boolean; is_default_orig: boolean
}
type ApocDoc = {
  slug: string; title_zh: string; title_zh_short: string | null; title_en: string
  category: string; testament: 'ot' | 'nt' | 'mixed'; genre: string | null
  total_sections: number; section_counts: Record<string, number>
}
type Section = {
  order_index: number; section_label: string | null; page_number: number | null
  chapter: number | null; verse: number | null
  byVersion: Record<string, string>; footnotesByVersion?: Record<string, Record<string, string>>
}
type DocRes = {
  document: ApocDoc & {
    title_orig: string | null; language_orig: string | null
    composition_low: number | null; composition_high: number | null
    canon_status_jsonb: Record<string, boolean> | null
    summary_zh: string | null; intro_zh: string | null
  }
  sections: Section[]
  chapters: { chapter: number; verses: number }[]
}

const supabase = useSupabaseClient()
const versions = ref<ApocVersion[]>([])
const docData = ref<DocRes | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)
const introOpen = ref(false)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}
async function load() {
  pending.value = true; error.value = null
  try {
    const headers = await authHeaders()
    const [v, d] = await Promise.all([
      $fetch<ApocVersion[]>('/api/apocrypha/versions', { headers }),
      $fetch<DocRes>('/api/apocrypha/document', { headers, query: { slug: slug.value } }),
    ])
    versions.value = v; docData.value = d; columns.value = []
  } catch (e: any) { error.value = e?.message || String(e) } finally { pending.value = false }
}
onMounted(load)
watch(slug, load)
useHead({ title: () => docData.value ? `${docData.value.document.title_zh} — 典外文獻` : '典外文獻' })

const introText = computed(() => docData.value?.document.intro_zh || docData.value?.document.summary_zh || '')

// ── Chapter navigation: one chapter per view ──────────────────────────
const chapterMode = computed(() => (docData.value?.chapters?.length ?? 0) > 0)
const chapterNums = computed(() => (docData.value?.chapters ?? []).map(c => c.chapter).sort((a, b) => a - b))
const currentChapter = computed(() => {
  const q = Number(route.query.chapter)
  if (q && chapterNums.value.includes(q)) return q
  return chapterNums.value[0] ?? 1
})
const chIdx = computed(() => chapterNums.value.indexOf(currentChapter.value))
const sectionsByChapter = computed(() => {
  const m = new Map<number, Section[]>()
  for (const s of docData.value?.sections ?? []) {
    if (s.chapter == null) continue
    if (!m.has(s.chapter)) m.set(s.chapter, [])
    m.get(s.chapter)!.push(s)
  }
  for (const arr of m.values()) arr.sort((a, b) => (a.verse ?? 0) - (b.verse ?? 0))
  return m
})
function versesOfChapter(ch: number): Section[] { return sectionsByChapter.value.get(ch) ?? [] }
function goToChapter(ch: number) {
  router.push(`/apocrypha/${slug.value}?chapter=${ch}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}

// ── Legacy mode (no chapter structure) ────────────────────────────────
const currentPage = computed(() => Math.max(1, Number(route.query.page) || 1))
const pagedLegacy = computed(() => {
  if (!docData.value) return []
  const start = (currentPage.value - 1) * LEGACY_PAGE_SIZE
  return docData.value.sections.slice(start, start + LEGACY_PAGE_SIZE)
})
function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push(`/apocrypha/${slug.value}?page=${p}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}

const totalPages = computed(() => chapterMode.value
  ? Math.max(1, chapterNums.value.length)
  : Math.max(1, Math.ceil((docData.value?.sections.length ?? 0) / LEGACY_PAGE_SIZE)))

// ── Unified prev/next (chapter or page) ───────────────────────────────
const currentLabel = computed(() => chapterMode.value ? `第 ${currentChapter.value} 章` : `第 ${currentPage.value}/${totalPages.value} 頁`)
const prevTarget = computed<number | null>(() => chapterMode.value
  ? (chIdx.value > 0 ? chapterNums.value[chIdx.value - 1] : null)
  : (currentPage.value > 1 ? currentPage.value - 1 : null))
const nextTarget = computed<number | null>(() => chapterMode.value
  ? (chIdx.value >= 0 && chIdx.value < chapterNums.value.length - 1 ? chapterNums.value[chIdx.value + 1] : null)
  : (currentPage.value < totalPages.value ? currentPage.value + 1 : null))
function goPrev() { if (prevTarget.value != null) (chapterMode.value ? goToChapter : goToPage)(prevTarget.value) }
function goNext() { if (nextTarget.value != null) (chapterMode.value ? goToChapter : goToPage)(nextTarget.value) }

// ── Visible sections (for footnotes) ──────────────────────────────────
const visibleSections = computed(() => chapterMode.value ? versesOfChapter(currentChapter.value) : pagedLegacy.value)

// ── Columns ───────────────────────────────────────────────────────────
type ColCategory = 'chinese' | 'english' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])
const availableVersions = computed(() => {
  if (!docData.value || !versions.value) return [] as ApocVersion[]
  const hasData = new Set<string>()
  for (const s of docData.value.sections) for (const k of Object.keys(s.byVersion)) hasData.add(k)
  return versions.value.filter(v => hasData.has(v.code))
})
function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  if (cat === 'chinese') { const def = avail.find(v => v.is_default_zh); if (def) return def.code }
  if (cat === 'english') { const def = avail.find(v => v.is_default_en); if (def) return def.code }
  if (cat === 'source') {
    const langMap: Record<string, string> = {
      greek: 'greek_orig', hebrew: 'hebrew_orig', aramaic: 'aramaic_orig',
      coptic: 'coptic_orig', syriac: 'syriac_orig', ethiopic: 'ethiopic_orig', latin: 'latin_orig',
    }
    const code = langMap[docData.value?.document.language_orig || '']
    if (code) { const v = avail.find(x => x.code === code); if (v) return v.code }
    const def = avail.find(v => v.is_default_orig); if (def) return def.code
  }
  return avail[0].code
}
watchEffect(() => {
  if (!availableVersions.value.length) {
    if (columns.value.length > 0 || !versions.value.length) return
    if (versions.value.find(v => v.category === 'chinese')) columns.value = [{ label: '中文', category: 'chinese', versionCode: '' }]
    return
  }
  if (columns.value.length > 0) return
  const cols: Col[] = []
  cols.push({ label: '中文', category: 'chinese', versionCode: pickForCategory('chinese') })
  const en = pickForCategory('english')
  if (en) cols.push({ label: '英文', category: 'english', versionCode: en })
  const src = pickForCategory('source')
  if (src) cols.push({ label: '原文', category: 'source', versionCode: src })
  if (!en) cols.push({ label: '英文', category: 'english', versionCode: '' })
  if (!src) cols.push({ label: '原文', category: 'source', versionCode: '' })
  columns.value = cols
})
function optionsForCol(col: Col): ApocVersion[] {
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
function textClassFor(code: string) {
  const v = versions.value?.find(x => x.code === code)
  if (!v) return ''
  if (v.language === 'hbo') return 'font-serif rtl-text text-right'
  if (v.language === 'grc') return 'font-serif'
  if (v.language === 'lat') return 'font-serif italic'
  if (v.language === 'syr') return 'font-serif rtl-text text-right'
  return ''
}

// ── Footnotes ─────────────────────────────────────────────────────────
const SUPERSCRIPT_RE = /([⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g
const SUPER_TO_ASCII: Record<string, string> = { '⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9' }
function superToAscii(s: string): string { return s.split('').map(c => SUPER_TO_ASCII[c] ?? c).join('') }
type Footnote = { id: string; marker: string; def: string | null }
const footnotesOnPage = computed<Footnote[]>(() => {
  const seen = new Map<string, Footnote>()
  for (const s of visibleSections.value) {
    for (const [versionCode, text] of Object.entries(s.byVersion)) {
      const matches = text.match(SUPERSCRIPT_RE)
      if (!matches) continue
      for (const m of matches) {
        const ascii = superToAscii(m)
        const id = `${s.order_index}-${ascii}`
        if (seen.has(id)) continue
        const def = s.footnotesByVersion?.[versionCode]?.[ascii] ?? null
        seen.set(id, { id, marker: m, def })
      }
    }
  }
  return Array.from(seen.values()).sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }))
})
function renderWithFootnotes(text: string, sectionIdx: number): string {
  const esc = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return esc.replace(SUPERSCRIPT_RE, (m) => {
    const id = `${sectionIdx}-${superToAscii(m)}`
    return `<a href="#fn-${id}" id="fnref-${id}" class="text-amber-700 hover:underline">${m}</a>`
  })
}

// ── Labels ────────────────────────────────────────────────────────────
const CATEGORY_LABEL: Record<string, string> = {
  ot_apocrypha: 'OT 次經 / 第二正典', ot_pseudepigrapha: 'OT 偽典', nt_apocrypha: 'NT 偽典',
  nag_hammadi: 'Nag Hammadi 諾斯底', qumran: '昆蘭古卷', lost_gospel: '失傳福音書',
}
function categoryLabel(c: string) { return CATEGORY_LABEL[c] || c }
const LANG_LABEL: Record<string, string> = {
  greek: '希臘文', hebrew: '希伯來文', aramaic: '亞蘭文', coptic: '科普特文',
  syriac: '敘利亞文', ethiopic: "Ge'ez 文", latin: '拉丁文',
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
  const low = d.composition_low, high = d.composition_high
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
})
</script>

<style scoped>
.rtl-text { direction: rtl; unicode-bidi: bidi-override; }
:deep(sup) { font-size: 0.7em; vertical-align: super; }
</style>
