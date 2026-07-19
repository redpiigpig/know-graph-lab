<template>
  <div class="fathers-home min-h-dvh flex flex-col">
    <!-- Custom parchment header — independent identity, entrance still via 經典對照 -->
    <header class="fathers-home-topbar sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink to="/scripture-canon/christianity" class="fathers-home-back flex-shrink-0">← 經典對照</NuxtLink>
          <span class="fathers-home-sep">·</span>
          <span class="font-semibold text-[#2a2013] truncate">✝ 教父著作</span>
        </div>
        <div class="flex items-center gap-3 flex-shrink-0">
          <span class="text-xs fathers-home-muted hidden sm:inline">Schaff 38 卷 / ACCS 27 卷</span>
          <NuxtLink to="/translation-glossary" class="fathers-home-link">📖 詞庫</NuxtLink>
        </div>
      </div>
    </header>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <!-- Hero -->
      <div class="fathers-hero mb-8">
        <div class="fathers-hero-ornament">❦</div>
        <h1 class="fathers-hero-title">教父著作</h1>
        <p class="fathers-hero-sub">Patristics · 前尼西亞至尼後教父</p>
        <p class="fathers-hero-desc">
          Schaff 全集 38 卷（ANF 10 · NPNF1 14 · NPNF2 14）＋ ACCS 27 卷，原文與逐段中譯對照。點任一卷進入閱讀界面。
        </p>
      </div>

      <!-- Series tabs -->
      <div class="fathers-tabs mb-6">
        <button v-for="s in series" :key="s.key"
          @click="activeSeries = s.key"
          :class="['fathers-tab', activeSeries === s.key ? 'is-on' : '']">
          {{ s.label }}
          <span class="fathers-tab-count">{{ booksBySeries(s.key).length }}</span>
        </button>
      </div>

      <!-- Filter -->
      <div class="flex items-center gap-3 mb-6 flex-wrap">
        <input v-model="q" type="search" placeholder="搜尋（書名／教父名）" class="fathers-search" />
        <span class="text-xs fathers-home-muted">{{ activeSeriesObj?.subtitle }} · {{ booksBySeries(activeSeries).length }} 卷</span>
      </div>

      <div v-if="loading" class="text-sm fathers-home-muted py-12 text-center">載入中…</div>

      <template v-else>
        <section class="mb-10">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <NuxtLink
              v-for="b in booksBySeries(activeSeries)" :key="b.id"
              :to="`/fathers/${b.id}`"
              class="fathers-card group"
            >
              <div class="flex items-baseline gap-2 mb-1.5">
                <span class="fathers-card-vol">卷&nbsp;{{ b.vol }}</span>
                <span v-if="b.refined" class="fathers-badge is-refined">已精修</span>
                <span v-else-if="b.parsed" class="fathers-badge is-rough">粗譯</span>
                <span v-else class="fathers-badge is-none">未譯</span>
              </div>
              <div class="fathers-card-title line-clamp-3">{{ b.display_title }}</div>
              <div class="fathers-card-meta">{{ b.chunk_count || 0 }} 章節</div>
            </NuxtLink>
          </div>
          <div v-if="!booksBySeries(activeSeries).length" class="text-sm fathers-home-muted py-12 text-center">
            此系列尚無書籍
          </div>
        </section>
      </template>

      <div class="fathers-legend">
        <p>狀態說明：</p>
        <ul>
          <li><b class="text-emerald-700">已精修</b>：跑過完整 5 步驟 pipeline + A+B+C 三層校對，T9 cross-bleed = 0</li>
          <li><b class="text-amber-700">粗譯</b>：完成翻譯但未經 v4 pipeline 精修，章節結構可能有 bleed bug</li>
          <li><b class="text-stone-500">未譯</b>：source 已在庫但尚未翻譯</li>
        </ul>
        <p class="mt-3">資料源：<a href="https://ccel.org/" target="_blank">CCEL (Christian Classics Ethereal Library)</a> · Schaff 編輯 · T&amp;T Clark 1885-1890 原版。</p>
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
  '9edb7c37-4231-412b-83bd-78f3f793cc0a',  // NPNF1 Vol 1 (Augustine — Confessions + Letters)
  'e01917ab-7429-41a0-9859-eddad413ef60',  // NPNF2 Vol 4 (Athanasius — Select Works and Letters)
  '1eb50be9-34ac-4ce3-874d-1280975851fc',  // NPNF1 Vol 2 (Augustine — City of God + On Christian Doctrine)
  'd7f66759-3fa9-4633-abde-87003cdbcc06',  // NPNF1 Vol 3 (Augustine — On the Holy Trinity + Doctrinal/Moral Treatises)
  '56ef3d65-c559-41f8-8d68-ba6c13e47876',  // NPNF1 Vol 4 (Augustine — Anti-Manichaean + Anti-Donatist)
  'df789501-5620-4833-a0a0-6e8f1a031bb1',  // NPNF1 Vol 5 (Augustine — Anti-Pelagian Writings)
  '7bff8a13-3c35-43d4-9b4c-b7c3c9f81076',  // NPNF1 Vol 6 (Augustine — Sermon on the Mount + Harmony of the Gospels + NT Sermons)
  '0069932a-7b27-4c06-9874-b74d51ad564e',  // NPNF1 Vol 7 (Augustine — Tractates on John + Homilies on 1 John + Soliloquies)
  '2accee20-5f9d-4099-9ce9-3dda0726a74b',  // NPNF1 Vol 8 (Augustine — Expositions on the Book of Psalms)
  '76df31fe-e732-4aa6-88c2-d650a09fb688',  // NPNF1 Vol 9 (金口若望 Chrysostom — On the Priesthood + Ascetic Treatises + Homilies)
  '0d160c29-8d61-4dbc-8f8e-d47fee694eab',  // NPNF1 Vol 10 (金口若望 Chrysostom — Homilies on the Gospel of Matthew)
  'bf2dd1b2-ae53-43c2-8fac-7ce10e137c10',  // NPNF1 Vol 12 (金口若望 Chrysostom — Homilies on 1 & 2 Corinthians)
  '4d73c561-aa4e-46b2-8e29-d331c5b9d28d',  // NPNF1 Vol 11 (金口若望 Chrysostom — Homilies on Acts + Romans)
  '9192cb77-3ce2-4adb-9d90-76200e452763',  // NPNF1 Vol 13 (金口若望 Chrysostom — Homilies on Galatians through Philemon)
  '91c7023f-2e63-4b16-897a-43bdf7d5e290',  // NPNF1 Vol 14 (金口若望 Chrysostom — Homilies on John + Hebrews)
  '91ff3a5e-cd1f-4ab4-acb7-70cb7a80c4b9',  // NPNF2 Vol 1 (Eusebius — Church History + Life of Constantine)
  '29782dd6-ece9-446a-83ed-9cc0892d7cc7',  // NPNF2 Vol 2 (Socrates Scholasticus + Sozomen — Ecclesiastical Histories)
  'a7e5956e-8851-4d0f-b3d2-1f823d1bdc81',  // NPNF2 Vol 3 (Theodoret + Jerome/Gennadius + Rufinus)
  '9b94e7c1-fa82-4910-a31f-9db1e2e040bb',  // NPNF2 Vol 5 (Gregory of Nyssa — Dogmatic/Ascetic/Philosophical/Apologetic/Oratorical/Letters)
  'd229a6d4-14de-4e28-92de-4855c75cbf68',  // NPNF2 Vol 6 (Jerome 耶柔米 — Letters + Treatises + Prolegomena)
  'af2cf8a7-b169-432c-863d-632647c8ab67',  // NPNF2 Vol 7 (Cyril of Jerusalem 耶路撒冷的區利羅《教理講授》+ Gregory Nazianzen 拿先斯的格列高里《講演集》《書信集》)
  '3c48472c-fbca-48fb-9db1-ca5a08827ef3',  // NPNF2 Vol 8 (Basil the Great 凱撒利亞的巴西流 — 論聖靈 + 六日創造論 + 書信集)
  '709f43f9-724c-4cd5-b6b0-570d26083d24',  // NPNF2 Vol 9 (Hilary of Poitiers 普瓦捷的希拉里 + John of Damascus 大馬士革的若望 — 論三位一體/論會議/詩篇講道 + 正統信仰詳解)
  'fd8a09e7-a6ab-4818-a6d7-6722e50da773',  // NPNF2 Vol 10 (Ambrose of Milan 米蘭的安波羅修 — 導論/論著選/書信選；源順序跨論著錯置故粗分三區)
  '24c53ede-8787-442e-a3ba-0cd55d0effac',  // NPNF2 Vol 11 (Sulpitius Severus 蘇皮修《聖瑪爾定傳》/書信/對話/神聖歷史 + Vincent of Lerins 勒蘭的文生《勸誡錄》 + John Cassian 若望‧格西安《會院規章》《會談錄》《論主之降生駁聶斯脫里》)
  '02a08547-6fb5-44b2-8a59-9b1f625f3a54',  // NPNF2 Vol 12 (Leo the Great 大良《書信集》《講道集》 + Gregory the Great 大額我略《牧靈規則》《書信集》)
  '90b55879-7179-41d7-9f6c-f6587a3dd429',  // NPNF2 Vol 13 (Gregory the Great II 大額我略《書信集卷九-十四》 + Ephraim Syrus 敘利亞的厄弗冷 讚美詩/聖詩/講道 + Aphrahat 波斯賢士阿弗拉哈特《論證集》)
  '63853a97-68be-441c-8dce-063ae89405c5',  // NPNF2 Vol 14 (The Seven Ecumenical Councils 基督教會七大公會議 — 尼西亞一/君堡一/以弗所/迦克墩/君堡二/君堡三/尼西亞二 + 教區會議法規 + 使徒法典)
])

const series = [
  { key: 'ANF',   label: 'ANF 前尼西亞教父',     subtitle: '~AD 100-325 · 10 卷' },
  { key: 'NPNF1', label: 'NPNF1 尼後教父第一系列', subtitle: '奧古斯丁與金口若望為主 · 14 卷' },
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
  'NPNF1-9':  '金口若望 — 論司祭職、苦修論集、講道選集',
  'NPNF1-10': '金口若望 — 馬太福音講道',
  'NPNF1-11': '金口若望 — 使徒行傳、羅馬書講道',
  'NPNF1-12': '金口若望 — 哥林多前後書講道',
  'NPNF1-13': '金口若望 — 加拉太、以弗所、腓立比、歌羅西、帖前後、提前後、提多、腓利門書講道',
  'NPNF1-14': '金口若望 — 約翰福音、希伯來書講道',
  // ── NPNF2 ───────────────────────────────────────────────────
  'NPNF2-1':  '優西比烏 — 教會史、君士坦丁傳',
  'NPNF2-2':  '蘇格拉底、索佐門 — 教會史',
  'NPNF2-3':  '狄奧多勒、耶柔米、根那狄、魯弗納 — 歷史著作',
  'NPNF2-4':  '亞他那修 — 著作選集與書信',
  'NPNF2-5':  '尼撒的格列高里 — 教義、苦修、哲學、護教、講演、書信',
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

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&display=swap');
</style>

<style scoped>
.fathers-home {
  background:
    radial-gradient(circle at 15% 0%, rgba(196,163,90,0.06), transparent 45%),
    #e7dcc4;
  color: #35291a;
  font-family: "Noto Serif TC", "Source Han Serif TC", "PingFang TC", "Microsoft JhengHei", serif;
}
.fathers-home-topbar {
  background: linear-gradient(#f3ead4, #ece0c6);
  border-bottom: 1px solid #cbb98f;
  box-shadow: 0 1px 3px rgba(120,90,40,0.08);
}
.fathers-home-back { color: #7a5c2e; font-size: 0.875rem; transition: color .15s; }
.fathers-home-back:hover { color: #4a3717; }
.fathers-home-sep { color: #c4a35a; }
.fathers-home-muted { color: #9c8a63; }
.fathers-home-link { font-size: 12px; color: #6b4f27; transition: color .15s; }
.fathers-home-link:hover { color: #4a3717; }

/* Hero */
.fathers-hero { text-align: center; padding: 1.5rem 0 0.5rem; }
.fathers-hero-ornament { color: #c4a35a; font-size: 1.5rem; margin-bottom: .5rem; }
.fathers-hero-title { font-size: 2.4rem; font-weight: 700; color: #2a2013; letter-spacing: .12em; }
.fathers-hero-sub { color: #8a7145; font-size: .9rem; letter-spacing: .1em; margin-top: .35rem; }
.fathers-hero-desc { color: #6b573a; font-size: .9rem; margin: 1rem auto 0; max-width: 40rem; line-height: 1.9; }

/* Tabs */
.fathers-tabs { display: flex; flex-wrap: wrap; gap: .5rem; justify-content: center; border-bottom: 1px solid #d0bd93; padding-bottom: .75rem; }
.fathers-tab {
  padding: 6px 16px; border-radius: 9999px; font-size: 13px; font-weight: 500; color: #7a5c2e;
  border: 1px solid transparent; transition: all .15s;
}
.fathers-tab:hover { color: #4a3717; background: #efe4cb; }
.fathers-tab.is-on { background: #6b4f27; color: #f3ead4; font-weight: 600; }
.fathers-tab-count { margin-left: 6px; font-size: 11px; opacity: .7; font-variant-numeric: tabular-nums; }

/* Filter */
.fathers-search {
  font-size: 14px; padding: 7px 14px; border-radius: 8px; width: 18rem; max-width: 100%;
  background: #fbf6e9; border: 1px solid #cbb98f; color: #35291a;
}
.fathers-search:focus { outline: none; border-color: #a9884a; }

/* Cards */
.fathers-card {
  display: flex; flex-direction: column; background: #fbf6e9; border: 1px solid #d8c9a8; border-radius: 8px;
  padding: 1rem 1.1rem; text-decoration: none; transition: all .18s; position: relative;
}
.fathers-card:hover { border-color: #a9884a; box-shadow: 0 6px 20px -8px rgba(90,64,20,0.28); transform: translateY(-1px); }
.fathers-card-vol { font-size: 12px; font-weight: 700; color: #7a5c2e; font-variant-numeric: tabular-nums; }
.fathers-card-title { font-size: 14.5px; font-weight: 600; color: #2a2013; line-height: 1.5; }
.fathers-card:hover .fathers-card-title { color: #6b4f27; }
.fathers-card-meta { font-size: 12px; color: #9c8a63; margin-top: .4rem; }
.fathers-badge { font-size: 10px; padding: 1px 7px; border-radius: 9999px; font-weight: 600; }
.fathers-badge.is-refined { background: #d1e7d3; color: #2f6b3a; }
.fathers-badge.is-rough { background: #f2e3bf; color: #8a6414; }
.fathers-badge.is-none { background: #e4d6b6; color: #8a7145; }

/* Legend */
.fathers-legend { margin-top: 3rem; font-size: 12px; color: #9c8a63; line-height: 1.8; }
.fathers-legend ul { margin: .35rem 0 0 1.25rem; list-style: disc; }
.fathers-legend a { color: #7a5c2e; text-decoration: underline; }
</style>
