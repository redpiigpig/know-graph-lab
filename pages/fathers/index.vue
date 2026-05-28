<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">教父著作</span>
      <span class="text-xs text-gray-400 ml-1">Schaff 38 卷 / ACCS 27 卷</span>
      <div class="ml-auto flex items-center gap-3">
        <NuxtLink to="/translation-glossary" class="text-xs text-stone-600 hover:text-stone-900">📖 詞庫</NuxtLink>
      </div>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">✝️ 教父著作</h1>
        <p class="text-sm text-gray-500">
          Schaff 全集 38 卷（ANF 10 + NPNF1 14 + NPNF2 14）+ 中譯。點任一卷進入閱讀界面。
        </p>
      </div>

      <!-- Filter -->
      <div class="flex items-center gap-2 mb-5">
        <input v-model="q" type="search" placeholder="搜尋（書名／教父名）"
          class="text-sm px-3 py-1.5 border border-gray-300 rounded-md w-72 focus:outline-none focus:border-stone-500" />
        <span class="text-xs text-gray-400 ml-2">{{ filteredBooks.length }} / {{ books.length }} 卷</span>
      </div>

      <div v-if="loading" class="text-sm text-gray-500 py-12 text-center">載入中…</div>

      <template v-else>
        <section v-for="series in series" :key="series.key" class="mb-10">
          <div class="flex items-baseline gap-3 mb-3 border-b border-gray-200 pb-1.5">
            <h2 class="text-lg font-semibold text-gray-900">{{ series.label }}</h2>
            <span class="text-xs text-gray-400">{{ series.subtitle }}</span>
            <span class="ml-auto text-xs text-gray-400">{{ booksBySeries(series.key).length }} 卷</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <NuxtLink
              v-for="b in booksBySeries(series.key)" :key="b.id"
              :to="`/ebook/${b.id}`"
              class="group bg-white border border-gray-200 hover:border-stone-400 hover:shadow-sm rounded-lg p-4 transition flex flex-col gap-1"
            >
              <div class="flex items-baseline gap-2">
                <span class="text-xs font-bold text-stone-600 tabular-nums">Vol&nbsp;{{ b.vol }}</span>
                <span v-if="b.refined" class="text-[10px] px-1.5 py-px rounded bg-emerald-100 text-emerald-700 font-medium">已精修</span>
                <span v-else-if="b.parsed" class="text-[10px] px-1.5 py-px rounded bg-amber-100 text-amber-700 font-medium">粗譯</span>
                <span v-else class="text-[10px] px-1.5 py-px rounded bg-gray-100 text-gray-500">未譯</span>
              </div>
              <div class="text-sm font-medium text-gray-900 leading-snug group-hover:text-stone-700 line-clamp-2">{{ b.display_title }}</div>
              <div class="text-xs text-gray-500">{{ b.chunk_count || 0 }} 章節</div>
            </NuxtLink>
          </div>
        </section>
      </template>

      <div class="mt-12 text-xs text-gray-400 leading-relaxed">
        <p>狀態說明：</p>
        <ul class="mt-1 ml-4 list-disc">
          <li><b class="text-emerald-700">已精修</b>：跑過完整 5 步驟 pipeline + A+B+C 三層校對，T9 cross-bleed = 0</li>
          <li><b class="text-amber-700">粗譯</b>：完成翻譯但未經 v4 pipeline 精修，章節結構可能有 bleed bug</li>
          <li><b class="text-gray-500">未譯</b>：source 已在庫但尚未翻譯</li>
        </ul>
        <p class="mt-3">資料源：<a href="https://ccel.org/" class="text-stone-600 hover:underline" target="_blank">CCEL (Christian Classics Ethereal Library)</a> · Schaff 編輯 · T&amp;T Clark 1885-1890 原版。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '教父著作 — Know Graph Lab' })

const supabase = useSupabaseClient<any>()

interface BookRow {
  id: string
  title: string
  original_title: string | null
  chunk_count: number | null
  parsed_at: string | null
}
interface BookView extends BookRow {
  series: string
  vol: number
  display_title: string
  parsed: boolean
  refined: boolean
}

const books = ref<BookView[]>([])
const loading = ref(true)
const q = ref('')

// The handful of books that have been through the full v4 精修 pipeline.
// As more are polished, append their id here (or compute via a metadata
// column later).
const REFINED_IDS = new Set([
  'c98d358d-7066-4691-a896-b7232707b0db',  // ANF Vol 1
  '4e3d16fc-ef4f-420f-a3ec-56e2e92d659f',  // ANF Vol 2 (Hermas/Tatian/Athenagoras/Theophilus/Clement of Alexandria)
  '364dac2e-410f-4906-be63-8bb86b4865ee',  // ANF Vol 3 (Tertullian Apologetic + Anti-Marcion)
  '904661d3-16fc-4f37-bb04-f7c4aa7671e9',  // ANF Vol 4 (Tertullian IV / Minucius Felix / Commodian / Origen — De Principiis + Contra Celsum)
  '0e08c662-540b-4186-b250-9bca0cfe1002',  // ANF Vol 5 (Hippolytus / Cyprian / Caius / Novatian)
  'dffaae40-e088-41c1-ab7f-9b96f9249661',  // ANF Vol 6 (Gregory Thaumaturgus / Dionysius / Africanus / Anatolius+Minor / Archelaus / Methodius / Arnobius)
])

const series = [
  { key: 'ANF',   label: '前尼西亞教父集 ANF', subtitle: '~AD 100-325 · 10 卷' },
  { key: 'NPNF1', label: '尼西亞後教父集 第一系列 NPNF1', subtitle: '主要為奧古斯丁與屈梭多模 · 14 卷' },
  { key: 'NPNF2', label: '尼西亞後教父集 第二系列 NPNF2', subtitle: '東方教父：亞他那修、巴西流、貴格利、希拉流 等 · 14 卷' },
] as const

// Strip the Chinese-prefixed leading title (前尼西亞教父 第一卷：...) leaving
// just the work-distinguishing part so the card stays scannable.
function displayTitle(b: BookRow, series: string, vol: number): string {
  // Prefer original_title; else use title; either way trim「 - ANF Vol N」suffix.
  let raw = (b.original_title || b.title || '').trim()
  // Drop the trailing「 - ANF Vol N」or 「（… - ANF Vol N）」 marker
  raw = raw.replace(/\s*[-—–]\s*(ANF|NPNF[12])\s*Vol\s*\d+.*$/i, '')
  raw = raw.replace(/[（(][^）)]*(ANF|NPNF[12])\s*Vol\s*\d+[^）)]*[）)]\s*$/i, '')
  raw = raw.replace(/^前尼西亞教父\s*第[一二三四五六七八九十0-9]+卷[：:]\s*/, '')
  raw = raw.trim()
  return raw || `Vol ${vol}`
}

function parseSeriesVol(title: string): { series: string; vol: number } | null {
  const m = title.match(/(ANF|NPNF1|NPNF2)\s*Vol\.?\s*(\d+)/i)
  if (!m) return null
  return { series: m[1].toUpperCase(), vol: parseInt(m[2]) }
}

function booksBySeries(seriesKey: string): BookView[] {
  return filteredBooks.value
    .filter(b => b.series === seriesKey)
    .sort((a, b) => a.vol - b.vol)
}

const filteredBooks = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return books.value
  return books.value.filter(b =>
    (b.title || '').toLowerCase().includes(query)
    || (b.original_title || '').toLowerCase().includes(query)
    || b.display_title.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  const { data, error } = await supabase
    .from('ebooks')
    .select('id, title, original_title, chunk_count, parsed_at, subcategory')
    .ilike('subcategory', '%Schaff%')
  if (error) { console.error(error); loading.value = false; return }
  const rows: BookView[] = []
  for (const b of (data || []) as BookRow[]) {
    const parsed = parseSeriesVol(b.title) || parseSeriesVol(b.original_title || '')
    if (!parsed) continue
    rows.push({
      ...b,
      series: parsed.series,
      vol: parsed.vol,
      display_title: displayTitle(b, parsed.series, parsed.vol),
      parsed: !!b.parsed_at && (b.chunk_count || 0) > 0,
      refined: REFINED_IDS.has(b.id),
    })
  }
  books.value = rows
  loading.value = false
})
</script>
