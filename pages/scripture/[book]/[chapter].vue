<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader :title="`${displayBookName || '聖經對照'} ${chapterNum}`" :back="{ to: '/scripture', label: '聖經對照' }" container-class="max-w-7xl">
      <template #actions>
        <span v-if="canon && CANON_LABEL[canon]" class="text-[10px] px-1.5 py-0.5 rounded-full bg-stone-100 text-stone-600">{{ CANON_LABEL[canon] }}</span>
        <button
          v-if="prevChapter"
          @click="navigate(prevChapter.book, prevChapter.chapter)"
          class="text-xs px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400"
        >← 上章</button>
        <button
          v-if="nextChapter"
          @click="navigate(nextChapter.book, nextChapter.chapter)"
          class="text-xs px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400"
        >下章 →</button>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      <!-- 補編提示：本卷在此傳統屬某卷的次經補編 -->
      <div v-if="asAddition" class="mb-4 text-xs bg-amber-50 border border-amber-300 rounded px-3 py-2 text-amber-800">
        ⚠ 本卷屬於<span class="font-semibold">次經範圍</span>——為《{{ parentOfThis?.name_zh || asAddition.parent_code }}》在此傳統的補編，並非獨立一卷。
        <NuxtLink :to="`/scripture/${asAddition.parent_code}/1${canonQS}`" class="underline hover:text-amber-950 ml-1">← 回母卷</NuxtLink>
      </div>

      <!-- Chapter picker -->
      <div class="flex flex-wrap items-center gap-1 mb-4">
        <span class="text-xs text-gray-500 mr-1">章：</span>
        <NuxtLink
          v-for="ch in chapterList"
          :key="ch"
          :to="`/scripture/${bookCode}/${ch}${canonQS}`"
          class="text-[11px] px-2 py-0.5 rounded border transition"
          :class="ch === chapterNum
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ ch }}</NuxtLink>
        <!-- 補編子卷（次經）：併入母卷，黃色標示 -->
        <template v-if="additionsOfBook.length">
          <span class="text-[11px] text-amber-600 ml-2 mr-1">補編：</span>
          <NuxtLink
            v-for="a in additionsOfBook"
            :key="a.book_code"
            :to="`/scripture/${a.book_code}/1${canonQS}`"
            class="text-[11px] px-2 py-0.5 rounded border border-amber-300 bg-amber-50 text-amber-700 hover:border-amber-500 transition"
          >{{ canonBookLabel(a.book_code) }}</NuxtLink>
        </template>
      </div>

      <!-- Column controls — one dropdown per visible column -->
      <div class="grid gap-3 mb-4" :style="{ gridTemplateColumns: gridCols }">
        <div
          v-for="(col, idx) in columns"
          :key="idx"
          class="bg-white border border-gray-200 rounded-md px-2 py-1.5 flex items-center gap-1"
        >
          <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
          <select
            v-model="col.versionCode"
            class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer"
          >
            <option
              v-for="v in optionsForCol(col)"
              :key="v.code"
              :value="v.code"
            >{{ v.name_zh }}{{ v.public_domain ? '' : ' ©' }}</option>
          </select>
          <button
            v-if="columns.length > 1"
            @click="removeColumn(idx)"
            class="text-gray-300 hover:text-red-500 text-xs px-1"
            title="移除此欄"
          >✕</button>
        </div>
        <button
          v-if="columns.length < availableVersions.length"
          @click="addColumn"
          class="bg-white border border-dashed border-gray-300 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700"
        >+ 對照欄</button>
      </div>

      <!-- 教父註釋 toggle -->
      <div class="flex items-center gap-3 mb-4">
        <button
          @click="toggleCommentary"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-medium transition"
          :class="showCommentary
            ? 'bg-amber-600 text-white border-amber-600'
            : 'bg-white text-amber-700 border-amber-300 hover:border-amber-500'"
        >
          <span class="text-sm leading-none">{{ showCommentary ? '✦' : '✧' }}</span>
          教父註釋（ACCS）
        </button>
        <span v-if="showCommentary && commentaryData" class="text-[11px] text-gray-400">
          <template v-if="commentaryData.available">{{ commentaryData.source_vol }}‧古代基督信仰聖經註釋叢書</template>
          <template v-else>本章尚無教父註釋資料</template>
        </span>
        <span v-if="commentaryPending" class="text-[11px] text-gray-400">載入註釋中…</span>
      </div>

      <!-- 詩篇編號提示（七十士 vs 希伯來編號差異）-->
      <p v-if="bookCode === 'psa'" class="mb-4 text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2.5 py-1.5 leading-relaxed">
        ⚠ 詩篇編號因傳統而異：希伯來（新教／和合本）與七十士譯本（天主教思高／東正教，詩 9 起相差一篇）不同。
        本頁各欄採所選版本「自身」的編號；同一傳統的欄位編號一致，跨傳統對照同一篇時請留意號碼位移。
      </p>

      <!-- Loading -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <!-- Verses table -->
      <div v-else-if="chapterData">
        <div v-if="chapterData.verses.length === 0" class="text-center text-gray-400 py-12 text-sm">
          此章節在已匯入的版本中尚無資料
        </div>

        <!-- Flat view (commentary off, or no ACCS data for this chapter) -->
        <div v-else-if="!showCommentary || !commentaryData?.available" class="space-y-1.5">
          <article
            v-for="v in chapterData.verses"
            :key="v.verse"
            class="bg-white border border-gray-200 rounded-md overflow-hidden"
          >
            <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: `auto ${gridCols}` }">
              <div class="bg-stone-50 px-2 py-2 text-xs font-mono font-semibold text-stone-700 flex items-start">
                {{ v.verse }}
              </div>
              <div
                v-for="(col, idx) in columns"
                :key="idx"
                class="bg-white px-3 py-2 text-sm leading-relaxed text-gray-800"
                :class="textClassFor(col.versionCode)"
              >
                <template v-if="col.versionCode && v.byVersion[col.versionCode]">
                  {{ v.byVersion[col.versionCode] }}
                </template>
                <span v-else class="text-gray-300 italic text-xs">—</span>
              </div>
            </div>
          </article>
        </div>

        <!-- Segmented view (commentary on): 經文上 · 教父註釋下，按 ACCS 段落分段 -->
        <div v-else class="space-y-4">
          <section
            v-for="(seg, si) in segments"
            :key="si"
          >
            <!-- pericope label chip -->
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-[11px] font-mono font-semibold text-stone-500">{{ seg.label }}</span>
              <div class="flex-1 h-px bg-stone-100" />
              <button
                v-if="seg.commentary"
                @click="togglePanel(si)"
                class="text-[11px] text-amber-700 hover:text-amber-900"
              >{{ panelOpen[si] === false ? '展開註釋 ▾' : '收合註釋 ▴' }}</button>
            </div>

            <!-- verses block -->
            <div class="space-y-1.5">
              <article
                v-for="v in seg.verses"
                :key="v.verse"
                class="bg-white border border-gray-200 rounded-md overflow-hidden"
              >
                <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: `auto ${gridCols}` }">
                  <div class="bg-stone-50 px-2 py-2 text-xs font-mono font-semibold text-stone-700 flex items-start">
                    {{ v.verse }}
                  </div>
                  <div
                    v-for="(col, idx) in columns"
                    :key="idx"
                    class="bg-white px-3 py-2 text-sm leading-relaxed text-gray-800"
                    :class="textClassFor(col.versionCode)"
                  >
                    <template v-if="col.versionCode && v.byVersion[col.versionCode]">
                      {{ v.byVersion[col.versionCode] }}
                    </template>
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                </div>
              </article>
            </div>

            <!-- commentary panel: 說明（overview）在上、教父註釋（comments）在下，明確分區 -->
            <div
              v-if="seg.commentary && panelOpen[si] !== false"
              class="mt-2 space-y-2.5"
            >
              <!-- 說明（編者導論） -->
              <div
                v-if="overviewsOf(seg).length"
                class="border border-amber-200 bg-amber-50 rounded-md px-3.5 py-3"
              >
                <div class="text-amber-800 text-base font-bold tracking-wide mb-1.5">說明</div>
                <div v-for="(e, ei) in overviewsOf(seg)" :key="'o' + ei" class="mb-2 last:mb-0">
                  <p v-if="e.heading" class="kaiti text-base font-bold text-amber-900 mb-1">{{ e.heading }}</p>
                  <p class="kaiti text-[15px] leading-loose text-stone-800">{{ e.body_zh }}</p>
                </div>
              </div>
              <!-- 教父註釋（具名引文） -->
              <div
                v-if="commentsOf(seg).length"
                class="border-l-2 border-stone-300 pl-3.5 space-y-3.5"
              >
                <div v-for="(e, ei) in commentsOf(seg)" :key="'c' + ei">
                  <p v-if="e.heading" class="text-sm font-semibold text-stone-600 mb-0.5">{{ e.heading }}</p>
                  <p class="text-[15px] leading-loose text-stone-800">{{ e.body_zh }}</p>
                  <p class="text-xs text-amber-800 mt-1 text-right">
                    — <span class="font-medium">{{ e.father_name }}</span>{{ e.work_title ? ` 《${e.work_title}》` : '' }}
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Coverage hint -->
        <p class="mt-6 text-[11px] text-gray-400 leading-relaxed">
          已匯入版本：{{ availableVersionsList }}。CUV2010 / NIV 為版權版本，預計透過合法來源逐步補入。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const bookCode = computed(() => String(route.params.book))
const chapterNum = computed(() => Number(route.params.chapter || 1))
type CanonKey = '' | 'protestant' | 'catholic' | 'orthodox' | 'syriac' | 'ethiopian'
const canon = computed<CanonKey>(() => (String(route.query.canon || '') as CanonKey))

// 各傳統的「預設對照版本」——同傳統的欄位採同一編號系統（如天主教思高/拉丁通行本=
// 七十士編號、新教和合/希伯來=希伯來編號），故詩篇等編號差異自然呈現、無需重對齊。
const CANON_LABEL: Record<string, string> = {
  protestant: '新教', catholic: '天主教‧思高', orthodox: '東正教',
  syriac: '敘利亞‧Peshitta', ethiopian: '衣索匹亞',
}
const canonQS = computed(() => (canon.value ? `?canon=${canon.value}` : ''))
// 本卷在此傳統的補編子卷（如但以理 → 蘇撒納/貝耳與大龍/阿匝黎雅；詩篇 → 詩151）
const additionsOfBook = computed(() =>
  canon.value ? (canonOrders.value[canon.value] || []).filter(r => r.parent_code === bookCode.value) : [])
// 本卷本身是否為某卷的補編（→ 標「屬於次經範圍」）
const asAddition = computed(() =>
  canon.value ? (canonOrders.value[canon.value] || []).find(r => r.book_code === bookCode.value && r.parent_code) || null : null)
const parentOfThis = computed(() => {
  const p = asAddition.value?.parent_code
  return p ? books.value.find(b => b.code === p) : null
})
function canonBookLabel(code: string): string {
  const ov = canon.value ? (canonOrders.value[canon.value] || []).find(r => r.book_code === code)?.name_override : null
  if (ov) return ov
  const b = books.value.find(x => x.code === code)
  if (!b) return code
  return (canon.value === 'catholic' && b.name_sigao) ? b.name_sigao : (b.name_zh_short || b.name_zh)
}

// 書名：傳統若有 name_override（如東正教以斯拉A/上/下）優先；否則只有天主教用思高本，
// 其餘所有傳統一律用和合本。
const displayBookName = computed(() => {
  const b = chapterData.value?.book
  if (!b) return ''
  if (canon.value) {
    const ov = canonOrders.value[canon.value]?.find(r => r.book_code === b.code)?.name_override
    if (ov) return ov
  }
  return (canon.value === 'catholic' && b.name_sigao) ? b.name_sigao : b.name_zh
})

const CANON_PREFS: Record<string, { chinese: string[]; english: string[]; source: string[] }> = {
  protestant: { chinese: ['cuv1919', 'cuv2010', 'tcv'], english: ['niv', 'asv', 'kjva'], source: ['wlc', 'sblgnt'] },
  catholic:   { chinese: ['sigao'], english: ['nabre', 'drc', 'knox'], source: ['vul', 'lxx'] },
  orthodox:   { chinese: ['sigao', 'tcv'], english: ['brenton', 'knox'], source: ['lxx', 'csl', 'rus_syn'] },
  syriac:     { chinese: ['sigao', 'tcv'], english: ['kjva'], source: ['peshitta', 'lxx'] },
  ethiopian:  { chinese: ['sigao', 'tcv'], english: ['kjva', 'brenton'], source: ['lxx'] },
}

type BibleBook = {
  code: string
  name_zh: string
  name_zh_short: string | null
  name_sigao?: string | null
  abbr_sigao?: string | null
  name_en: string
  testament: 'ot' | 'nt' | 'deutero' | 'apocrypha'
  display_order: number
  chapter_count: number | null
}
type BibleVersion = {
  code: string
  name_zh: string
  name_en: string
  language: string
  language_zh: string | null
  category: 'chinese' | 'english' | 'source' | 'ancient'
  scope: string
  public_domain: boolean
  copyright_notice: string | null
  source_url: string | null
  display_order: number
  is_default_zh: boolean
  is_default_en: boolean
  is_default_orig: boolean
}
type ChapterRes = {
  book: BibleBook
  chapter: number
  verses: { verse: number; byVersion: Record<string, string> }[]
}

const supabase = useSupabaseClient()
const books = ref<BibleBook[]>([])
const versions = ref<BibleVersion[]>([])
const chapterData = ref<ChapterRes | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

type CanonRow = { book_code: string; name_override: string | null; parent_code: string | null }
const canonOrders = ref<Record<string, CanonRow[]>>({})

async function loadBootstrap() {
  const headers = await authHeaders()
  const [b, v, co] = await Promise.all([
    $fetch<BibleBook[]>('/api/scripture/books', { headers }),
    $fetch<BibleVersion[]>('/api/scripture/versions', { headers }),
    $fetch<Record<string, CanonRow[]>>('/api/scripture/canon-order', { headers }).catch(() => ({})),
  ])
  books.value = b
  versions.value = v
  canonOrders.value = co || {}
}

async function loadChapter() {
  pending.value = true
  error.value = null
  try {
    const headers = await authHeaders()
    chapterData.value = await $fetch<ChapterRes>('/api/scripture/chapter', {
      headers,
      query: { book: bookCode.value, chapter: chapterNum.value },
    })
    // Reset columns so the defaults re-pick when chapter changes between OT and NT
    columns.value = []
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}

onMounted(async () => {
  await loadBootstrap()
  await loadChapter()
})

watch([bookCode, chapterNum], () => {
  if (books.value.length > 0) loadChapter()
})

useHead({
  title: () => chapterData.value
    ? `${chapterData.value.book.name_zh} ${chapterNum.value} — 聖經對照`
    : '聖經對照',
})

// ── Columns: each = { label, category, versionCode }
type ColCategory = 'chinese' | 'english' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])

const availableVersions = computed(() => {
  if (!chapterData.value || !versions.value) return [] as BibleVersion[]
  const hasData = new Set<string>()
  for (const v of chapterData.value.verses) {
    for (const k of Object.keys(v.byVersion)) hasData.add(k)
  }
  return versions.value.filter(v => hasData.has(v.code))
})

const availableVersionsList = computed(() =>
  availableVersions.value.map(v => v.name_zh.replace(/（[^）]*）/g, '').trim()).join(' / ')
)

function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  // 傳統優先：若該 canon 對此類別有偏好版本且已匯入，採用之（同傳統同編號系統）
  const prefs = canon.value ? CANON_PREFS[canon.value]?.[cat] : undefined
  if (prefs) {
    for (const code of prefs) {
      const hit = avail.find(v => v.code === code)
      if (hit) return hit.code
    }
  }
  // For source: prefer testament-matched (hbo for OT, grc for NT)
  if (cat === 'source' && chapterData.value) {
    const testament = chapterData.value.book.testament
    const preferred = testament === 'ot'
      ? avail.find(v => v.language === 'hbo')
      : testament === 'nt'
        ? avail.find(v => v.language === 'grc' && v.code === 'sblgnt')
        : avail.find(v => v.language === 'grc')  // deutero / apoc → Greek
    if (preferred) return preferred.code
  }
  // For Chinese / English: prefer default flag
  if (cat === 'chinese') {
    const def = avail.find(v => v.is_default_zh)
    if (def) return def.code
  }
  if (cat === 'english') {
    const def = avail.find(v => v.is_default_en)
    if (def) return def.code
  }
  return avail[0].code
}

// Build default columns: 中文 / 英文 / 原文
watchEffect(() => {
  if (!availableVersions.value.length) return
  if (columns.value.length > 0) return
  const cols: Col[] = []
  const zh = pickForCategory('chinese')
  if (zh) cols.push({ label: '中文', category: 'chinese', versionCode: zh })
  const en = pickForCategory('english')
  if (en) cols.push({ label: '英文', category: 'english', versionCode: en })
  const src = pickForCategory('source')
  if (src) cols.push({ label: '原文', category: 'source', versionCode: src })
  columns.value = cols
})

function optionsForCol(col: Col): BibleVersion[] {
  // For "source", let user pick any source-language version (Hebrew/Greek/Latin)
  return availableVersions.value.filter(v => {
    if (col.category === 'source') return v.category === 'source'
    return v.category === col.category
  })
}

function addColumn() {
  // Add an extra source column (most common need: compare original languages)
  const used = new Set(columns.value.map(c => c.versionCode))
  // Try to find an unused version, prefer source then english then chinese
  const order: ColCategory[] = ['source', 'english', 'chinese']
  for (const cat of order) {
    const v = availableVersions.value.find(x => x.category === cat && !used.has(x.code))
    if (v) {
      const label = cat === 'source' ? '原文' : cat === 'english' ? '英文' : '中文'
      columns.value.push({ label, category: cat, versionCode: v.code })
      return
    }
  }
}

function removeColumn(idx: number) {
  columns.value.splice(idx, 1)
}

const gridCols = computed(() => `repeat(${columns.value.length}, minmax(0, 1fr))`)

function textClassFor(code: string) {
  const v = versions.value?.find(x => x.code === code)
  if (!v) return ''
  if (v.language === 'hbo') return 'font-serif rtl-text text-right text-base'  // Hebrew RTL
  if (v.language === 'grc') return 'font-serif'                                // Greek
  if (v.language === 'lat') return 'font-serif italic'                         // Latin
  return ''
}

// ── Chapter navigation
const currentBook = computed(() =>
  books.value?.find(b => b.code === bookCode.value) || null
)

const chapterList = computed(() => {
  const n = currentBook.value?.chapter_count ?? 0
  return Array.from({ length: n }, (_, i) => i + 1)
})

const prevChapter = computed(() => {
  if (!currentBook.value || !books.value) return null
  if (chapterNum.value > 1) {
    return { book: bookCode.value, chapter: chapterNum.value - 1 }
  }
  const idx = books.value.findIndex(b => b.code === bookCode.value)
  if (idx > 0) {
    const prev = books.value[idx - 1]
    return { book: prev.code, chapter: prev.chapter_count || 1 }
  }
  return null
})

const nextChapter = computed(() => {
  if (!currentBook.value || !books.value) return null
  if (chapterNum.value < (currentBook.value.chapter_count || 0)) {
    return { book: bookCode.value, chapter: chapterNum.value + 1 }
  }
  const idx = books.value.findIndex(b => b.code === bookCode.value)
  if (idx >= 0 && idx + 1 < books.value.length) {
    return { book: books.value[idx + 1].code, chapter: 1 }
  }
  return null
})

function navigate(book: string, chapter: number) {
  router.push(`/scripture/${book}/${chapter}${canonQS.value}`)
}

// ── ACCS 教父註釋 ────────────────────────────────────────────────────────────
type CommentaryEntry = {
  section_kind: 'overview' | 'comment'
  heading: string | null
  father_name: string | null
  work_title: string | null
  body_zh: string
}
type Pericope = { verse_start: number; verse_end: number; entries: CommentaryEntry[] }
type CommentaryRes = {
  book: string; chapter: number; available: boolean
  source_vol: string; pericopes: Pericope[]
}

const showCommentary = ref(false)
const commentaryData = ref<CommentaryRes | null>(null)
const commentaryPending = ref(false)
const panelOpen = reactive<Record<number, boolean>>({})

async function loadCommentary() {
  commentaryPending.value = true
  try {
    const headers = await authHeaders()
    commentaryData.value = await $fetch<CommentaryRes>('/api/scripture/commentary', {
      headers,
      query: { book: bookCode.value, chapter: chapterNum.value },
    })
  } catch {
    commentaryData.value = null
  } finally {
    commentaryPending.value = false
  }
}

function toggleCommentary() {
  showCommentary.value = !showCommentary.value
  if (showCommentary.value && !commentaryData.value) loadCommentary()
}

// Reset panel state per chapter; reload commentary if it's currently shown
watch([bookCode, chapterNum], () => {
  commentaryData.value = null
  for (const k of Object.keys(panelOpen)) delete panelOpen[Number(k)]
  if (showCommentary.value) loadCommentary()
})

function togglePanel(idx: number) {
  panelOpen[idx] = panelOpen[idx] === false ? true : false
}

// Split a segment's commentary into 說明（overview）vs 教父引文（comment）
function overviewsOf(seg: { commentary: Pericope | null }): CommentaryEntry[] {
  return seg.commentary?.entries.filter(e => e.section_kind === 'overview') ?? []
}
function commentsOf(seg: { commentary: Pericope | null }): CommentaryEntry[] {
  return seg.commentary?.entries.filter(e => e.section_kind === 'comment') ?? []
}

// Group chapter verses into ACCS pericopes (經文上 → 註釋下). Verses outside any
// pericope render as their own commentary-less segment, in verse order.
const segments = computed(() => {
  const out: { label: string; verses: { verse: number; byVersion: Record<string, string> }[]; commentary: Pericope | null }[] = []
  if (!chapterData.value) return out
  const pericopes = (commentaryData.value?.pericopes ?? [])
    .slice()
    .sort((a, b) => a.verse_start - b.verse_start)
  const verses = chapterData.value.verses
  const bookShort = currentBook.value?.name_zh_short || currentBook.value?.name_zh || ''

  let pIdx = 0
  let i = 0
  while (i < verses.length) {
    const v = verses[i]
    const p = pericopes[pIdx]
    if (p && v.verse >= p.verse_start && v.verse <= p.verse_end) {
      // collect all verses within this pericope
      const grp: typeof verses = []
      while (i < verses.length && verses[i].verse <= p.verse_end) {
        grp.push(verses[i]); i++
      }
      const label = p.verse_start === p.verse_end
        ? `${bookShort} ${chapterNum.value}:${p.verse_start}`
        : `${bookShort} ${chapterNum.value}:${p.verse_start}–${p.verse_end}`
      out.push({ label, verses: grp, commentary: p })
      pIdx++
    } else if (p && v.verse > p.verse_end) {
      // pericope has no matching verses (gap) — skip it
      pIdx++
    } else {
      // verse before next pericope start → standalone, no commentary
      const label = `${bookShort} ${chapterNum.value}:${v.verse}`
      out.push({ label, verses: [v], commentary: null })
      i++
    }
  }
  return out
})
</script>

<style scoped>
.rtl-text {
  direction: rtl;
  unicode-bidi: bidi-override;
}
/* 標楷體 — 用於 ACCS「說明」導論，給古典註釋的質感 */
.kaiti {
  font-family: "標楷體", "DFKai-SB", "BiauKai", "TW-Kai", "AR PL UKai TW", "KaiTi", "STKaiti", serif;
}
</style>
