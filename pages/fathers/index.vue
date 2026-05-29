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
          Schaff 全集 38 卷（ANF 10 + NPNF1 14 + NPNF2 14）+ ACCS 27 卷 + 中譯。點任一卷進入閱讀界面。
        </p>
      </div>

      <!-- Series tabs -->
      <div class="flex items-end gap-1 mb-5 border-b border-gray-200">
        <button v-for="s in series" :key="s.key"
          @click="activeSeries = s.key"
          :class="['px-4 py-2 text-sm font-medium transition border-b-2 -mb-px',
                   activeSeries === s.key
                     ? 'border-stone-800 text-stone-900'
                     : 'border-transparent text-gray-500 hover:text-stone-700']">
          {{ s.label }}
          <span class="ml-1.5 text-xs text-gray-400">{{ booksBySeries(s.key).length }}</span>
        </button>
      </div>

      <!-- Filter -->
      <div class="flex items-center gap-2 mb-5">
        <input v-model="q" type="search" placeholder="搜尋（書名／教父名）"
          class="text-sm px-3 py-1.5 border border-gray-300 rounded-md w-72 focus:outline-none focus:border-stone-500" />
        <span class="text-xs text-gray-400 ml-2">
          {{ activeSeriesObj?.subtitle }} · {{ booksBySeries(activeSeries).length }} 卷
        </span>
      </div>

      <div v-if="loading" class="text-sm text-gray-500 py-12 text-center">載入中…</div>

      <template v-else>
        <section class="mb-10">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <NuxtLink
              v-for="b in booksBySeries(activeSeries)" :key="b.id"
              :to="`/ebook/${b.id}`"
              class="group bg-white border border-gray-200 hover:border-stone-400 hover:shadow-sm rounded-lg p-4 transition flex flex-col gap-1"
            >
              <div class="flex items-baseline gap-2">
                <span class="text-xs font-bold text-stone-600 tabular-nums">卷&nbsp;{{ b.vol }}</span>
                <span v-if="b.refined" class="text-[10px] px-1.5 py-px rounded bg-emerald-100 text-emerald-700 font-medium">已精修</span>
                <span v-else-if="b.parsed" class="text-[10px] px-1.5 py-px rounded bg-amber-100 text-amber-700 font-medium">粗譯</span>
                <span v-else class="text-[10px] px-1.5 py-px rounded bg-gray-100 text-gray-500">未譯</span>
              </div>
              <div class="text-sm font-medium text-gray-900 leading-snug group-hover:text-stone-700 line-clamp-3">{{ b.display_title }}</div>
              <div class="text-xs text-gray-500">{{ b.chunk_count || 0 }} 章節</div>
            </NuxtLink>
          </div>
          <div v-if="!booksBySeries(activeSeries).length"
            class="text-sm text-gray-400 py-12 text-center">
            此系列尚無書籍
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
  '75d8aae0-7431-4be9-baee-c57d26599653',  // ANF Vol 7 (Lactantius / Venantius / Asterius / Methodius / Arnobius)
  'd09946ab-154b-4a97-853f-751cbb346221',  // ANF Vol 8 (Twelve Patriarchs / Pseudo-Clementine / NT Apocrypha / Decretals / Edessa / Remains)
  '72cb2f94-da86-4e16-bbbd-4cf3391031df',  // ANF Vol 9 (Gospel of Peter / Diatessaron / Apocalypses / Visio Pauli / Apocryphal Acts)
])

const series = [
  { key: 'ANF',   label: 'ANF 前尼西亞教父',     subtitle: '~AD 100-325 · 10 卷' },
  { key: 'NPNF1', label: 'NPNF1 尼後教父第一系列', subtitle: '奧古斯丁與屈梭多模為主 · 14 卷' },
  { key: 'NPNF2', label: 'NPNF2 尼後教父第二系列', subtitle: '東方教父：亞他那修、巴西流、貴格利、希拉流 等 · 14 卷' },
  { key: 'ACCS',  label: 'ACCS 古代基督徒聖經註釋', subtitle: 'IVP 編 · 27 卷（已上架 2 卷）' },
] as const

const activeSeries = ref<'ANF' | 'NPNF1' | 'NPNF2' | 'ACCS'>('ANF')
const activeSeriesObj = computed(() => series.find(s => s.key === activeSeries.value))

// (series, vol) → 中文卡片標題。短，能放下一張卡片不破版。
// 缺項時 fallback 到 displayTitle 的英文剝皮邏輯。
const ZH_TITLES: Record<string, string> = {
  // ── ANF ─────────────────────────────────────────────────────
  'ANF-1':  '使徒教父、殉道者猶斯定、愛任紐',
  'ANF-2':  '第二世紀教父：黑馬、他提安、雅典那哥拉、提阿非羅、亞歷山卓的革利免',
  'ANF-3':  '拉丁基督教：特土良 — 護教與駁馬吉安',
  'ANF-4':  '特土良卷四、密努修‧斐力克斯、科摩狄安、俄利根 — 論原理與駁塞爾蘇斯',
  'ANF-5':  '希波呂圖、居普良、該猶、諾窪天',
  'ANF-6':  '奇蹟行者格列高利、亞歷山卓的狄奧尼修、阿弗里卡努斯、亞納托利烏、阿基老、美多第烏、阿爾諾比烏斯',
  'ANF-7':  '拉克坦提烏斯、維南提烏、亞斯特里烏、美多第烏、阿爾諾比烏斯',
  'ANF-8':  '十二族長遺訓、書信殘篇、使徒憲典、講道集',
  'ANF-9':  '彼得福音、四福音合參、啟示錄、保羅異象、偽經行傳',
  'ANF-10': '參考書目、總索引',
  // ── NPNF1 ───────────────────────────────────────────────────
  'NPNF1-1':  '奧古斯丁 — 《懺悔錄》與信主之家手冊',
  'NPNF1-2':  '奧古斯丁 — 《上帝之城》、論基督教教義',
  'NPNF1-3':  '奧古斯丁 — 論聖三、神學論集',
  'NPNF1-4':  '奧古斯丁 — 駁摩尼派、駁多納徒派',
  'NPNF1-5':  '奧古斯丁 — 駁伯拉糾派著作',
  'NPNF1-6':  '奧古斯丁 — 論登山寶訓、四福音合參',
  'NPNF1-7':  '奧古斯丁 — 約翰福音講道、約翰一書講道、獨語錄',
  'NPNF1-8':  '奧古斯丁 — 詩篇講解',
  'NPNF1-9':  '屈梭多模 — 論司祭職、苦修論集、講道選集',
  'NPNF1-10': '屈梭多模 — 馬太福音講道',
  'NPNF1-11': '屈梭多模 — 使徒行傳、羅馬書講道',
  'NPNF1-12': '屈梭多模 — 哥林多前後書講道',
  'NPNF1-13': '屈梭多模 — 加拉太、以弗所、腓立比、歌羅西、帖前後、提前後、提多、腓利門書講道',
  'NPNF1-14': '屈梭多模 — 約翰福音、希伯來書講道',
  // ── NPNF2 ───────────────────────────────────────────────────
  'NPNF2-1':  '優西比烏 — 教會史、君士坦丁傳',
  'NPNF2-2':  '蘇格拉底、索佐門 — 教會史',
  'NPNF2-3':  '狄奧多雷、耶柔米、根那狄、魯弗納 — 歷史著作',
  'NPNF2-4':  '亞他那修 — 著作選集與書信',
  'NPNF2-5':  '尼撒的格列高理 — 教義論集',
  'NPNF2-6':  '耶柔米 — 書信與著作選集',
  'NPNF2-7':  '西瑞爾、拿先斯的格列高理 — 著作選集',
  'NPNF2-8':  '巴西流 — 書信與著作選集',
  'NPNF2-9':  '希拉里、大馬色的若望 — 著作選集',
  'NPNF2-10': '安波羅修 — 著作與書信選集',
  'NPNF2-11': '蘇皮修、勒蘭的文生、若望‧格西安',
  'NPNF2-12': '大良、大額我略 — 著作選集',
  'NPNF2-13': '大額我略卷二、敘利亞的艾弗冷、亞弗拉哈特',
  'NPNF2-14': '七大公會議',
  // ── ACCS ────────────────────────────────────────────────────
  'ACCS-12': '耶利米書、耶利米哀歌',
  'ACCS-15': '次經',
}

function displayTitle(b: BookRow, seriesKey: string, vol: number): string {
  const zh = ZH_TITLES[`${seriesKey}-${vol}`]
  if (zh) return zh
  // Fallback: strip trailing「 - SERIES Vol N」marker from English title
  let raw = (b.original_title || b.title || '').trim()
  raw = raw.replace(/\s*[-—–]\s*(ANF|NPNF[12]|ACCS)\s*Vol\s*\d+.*$/i, '')
  raw = raw.replace(/[（(][^）)]*(ANF|NPNF[12]|ACCS)\s*Vol\s*\d+[^）)]*[）)]\s*$/i, '')
  raw = raw.replace(/^前尼西亞教父\s*第[一二三四五六七八九十0-9]+卷[：:]\s*/, '')
  raw = raw.replace(/^古代基督徒聖經註釋叢書\s*卷[一二三四五六七八九十0-9]+[：:]\s*/, '')
  raw = raw.trim()
  return raw || `卷 ${vol}`
}

function parseSeriesVol(title: string): { series: string; vol: number } | null {
  const m = title.match(/(ANF|NPNF1|NPNF2|ACCS)\s*(?:on Scripture\s*)?vol\.?\s*(\d+)/i)
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
    .or('subcategory.ilike.%Schaff%,subcategory.ilike.%ACCS%')
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
