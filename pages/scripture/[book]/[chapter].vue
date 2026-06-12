<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ chapterData?.book?.name_zh || '聖經對照' }}</span>
      <span class="text-xs text-gray-500">{{ chapterNum }}</span>
      <div class="ml-auto flex items-center gap-2 text-xs">
        <button
          v-if="prevChapter"
          @click="navigate(prevChapter.book, prevChapter.chapter)"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400"
        >← 上章</button>
        <button
          v-if="nextChapter"
          @click="navigate(nextChapter.book, nextChapter.chapter)"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400"
        >下章 →</button>
      </div>
    </nav>

    <div class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      <!-- Chapter picker -->
      <div class="flex flex-wrap items-center gap-1 mb-4">
        <span class="text-xs text-gray-500 mr-1">章：</span>
        <NuxtLink
          v-for="ch in chapterList"
          :key="ch"
          :to="`/scripture/${bookCode}/${ch}`"
          class="text-[11px] px-2 py-0.5 rounded border transition"
          :class="ch === chapterNum
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ ch }}</NuxtLink>
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

            <!-- commentary panel -->
            <div
              v-if="seg.commentary && panelOpen[si] !== false"
              class="mt-2 border-l-2 border-amber-300 bg-amber-50/40 rounded-r-md pl-3 pr-3 py-2.5 space-y-3"
            >
              <div
                v-for="(e, ei) in seg.commentary.entries"
                :key="ei"
              >
                <!-- overview -->
                <div v-if="e.section_kind === 'overview'">
                  <p v-if="e.heading" class="text-xs font-semibold text-amber-900 mb-0.5">{{ e.heading }}</p>
                  <p class="text-[13px] leading-relaxed text-stone-700 italic">{{ e.body_zh }}</p>
                </div>
                <!-- patristic comment -->
                <div v-else>
                  <p v-if="e.heading" class="text-xs font-semibold text-stone-600 mb-0.5">{{ e.heading }}</p>
                  <p class="text-[13px] leading-relaxed text-stone-800">{{ e.body_zh }}</p>
                  <p class="text-[11px] text-amber-800 mt-0.5">
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

type BibleBook = {
  code: string
  name_zh: string
  name_zh_short: string | null
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

async function loadBootstrap() {
  const headers = await authHeaders()
  const [b, v] = await Promise.all([
    $fetch<BibleBook[]>('/api/scripture/books', { headers }),
    $fetch<BibleVersion[]>('/api/scripture/versions', { headers }),
  ])
  books.value = b
  versions.value = v
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
  router.push(`/scripture/${book}/${chapter}`)
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
</style>
