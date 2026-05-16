<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 論文寫作系統</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">碩士論文線上版</span>
      </div>
    </nav>

    <!-- 封面 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-700">碩士論文</span>
          <span class="text-xs text-gray-400">國立臺北教育大學 台灣文化研究所</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 leading-snug mb-1">
          印順導師人間佛教思想的傳承與實踐：
          <span class="text-purple-700">以昭慧法師、性廣法師為核心</span>
        </h1>
        <p class="text-sm text-gray-400 italic mb-5">
          The Inheritance and Practice of Master Yin-shun's "Buddhism for Human Realm" Thoughts: Centering on Venerables Chao-hwei and Shing-kuang.
        </p>
        <div class="flex flex-wrap gap-5 text-sm text-gray-600 mb-4">
          <div><span class="text-gray-400 mr-1">作者</span>張辰瑋</div>
          <div><span class="text-gray-400 mr-1">指導教授</span>侯坤宏 博士 ／ 蘇瑞鏘 博士</div>
          <div><span class="text-gray-400 mr-1">完成時間</span>中華民國 114 年 6 月（2025）</div>
        </div>
        <div class="flex flex-wrap gap-2">
          <span v-for="kw in keywords" :key="kw" class="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600">{{ kw }}</span>
        </div>
      </div>
    </div>

    <!-- 分頁 -->
    <div class="bg-white border-b border-gray-100 sticky top-14 z-30">
      <div class="max-w-5xl mx-auto px-6">
        <div class="flex">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id; $router.replace({ query: { tab: tab.id } })"
            :class="['px-5 py-3.5 text-sm font-medium border-b-2 transition-colors', activeTab === tab.id ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-500 hover:text-gray-800']">
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 內容 -->
    <div class="max-w-5xl mx-auto px-6 py-8">

      <!-- ① 論文內容 -->
      <div v-if="activeTab === 'content'" class="flex gap-6">
        <!-- 章節側欄 -->
        <aside class="w-48 flex-shrink-0 hidden md:block">
          <div class="sticky top-28 space-y-0.5">
            <button v-for="ch in chapters" :key="ch.id" @click="selectChapter(ch.id)"
              :class="['w-full text-left px-3 py-2 rounded-lg text-xs transition-colors leading-snug', activeChapter === ch.id ? 'bg-purple-100 text-purple-700 font-medium' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700']">
              {{ ch.shortTitle }}
            </button>
          </div>
        </aside>

        <!-- 正文 -->
        <div class="flex-1 min-w-0">
          <div class="md:hidden mb-4">
            <select v-model="activeChapter" @change="loadChapter(activeChapter)" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option v-for="ch in chapters" :key="ch.id" :value="ch.id">{{ ch.shortTitle }}</option>
            </select>
          </div>
          <div class="thesis-page">
            <div v-if="loading" class="flex items-center justify-center h-40 text-gray-400 text-sm">載入中⋯</div>
            <div v-else class="thesis-body" v-html="formattedChapter"></div>
          </div>
        </div>
      </div>

      <!-- ② 口述訪談 -->
      <div v-if="activeTab === 'interviews'">
        <div class="mb-5 flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 class="text-base font-semibold text-gray-900">口述訪談紀錄</h2>
            <p class="text-xs text-gray-500 mt-0.5">共 {{ interviews.length }} 位受訪者，2023–2025 年間完成</p>
          </div>
          <div class="flex gap-2 flex-wrap">
            <button v-for="cat in categories" :key="cat" @click="activeCategory = cat"
              :class="['text-xs px-3 py-1.5 rounded-full border transition-colors', activeCategory === cat ? 'bg-purple-600 text-white border-purple-600' : 'border-gray-200 text-gray-500 hover:border-gray-400']">
              {{ cat }}
            </button>
          </div>
        </div>
        <div class="grid gap-3 sm:grid-cols-2">
          <NuxtLink v-for="iv in filteredInterviews" :key="iv.id"
            :to="`/thesis/interview/${encodeURIComponent(iv.filename)}`"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:border-purple-200 hover:shadow-sm transition-all no-underline">
            <div class="flex items-start gap-3">
              <div :class="['w-9 h-9 rounded-full flex items-center justify-center text-sm flex-shrink-0', catStyle(iv.category)]">
                {{ catIcon(iv.category) }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline justify-between gap-2">
                  <h3 class="text-sm font-semibold text-gray-900 truncate">{{ iv.name }}</h3>
                  <span class="text-xs text-gray-400 flex-shrink-0">{{ iv.date }}</span>
                </div>
                <p class="text-xs text-gray-500 mt-0.5">{{ iv.role }}</p>
                <p class="text-xs text-purple-500 mt-1.5">閱讀全文 →</p>
              </div>
            </div>
          </NuxtLink>
        </div>

        <!-- Drive 上尚未有正式紀錄的訪談 -->
        <section class="mt-10 bg-white rounded-xl border border-amber-100 p-5">
          <div class="flex items-baseline justify-between mb-1">
            <h3 class="text-sm font-semibold text-amber-700">Drive 上尚未有正式紀錄</h3>
            <span class="text-xs text-amber-500">
              共 {{ driveMissingByStatus.draft.length + driveMissingByStatus.audioOnly.length + driveMissingByStatus.outlineOnly.length }} 人
            </span>
          </div>
          <p class="text-xs text-gray-500 mb-4">
            訪談已進行（或排定），但 Drive 上沒有最終整理過的「口述訪談紀錄.docx」。
            <span class="text-gray-400">部分人物的逐字稿已在網站上呈現，但仍待回寫成正式檔。</span>
          </p>

          <div v-if="driveMissingByStatus.draft.length" class="mb-4">
            <h4 class="text-xs font-semibold text-gray-600 mb-2">📝 已有逐字稿草稿（m4a.txt）</h4>
            <ul class="grid gap-1.5 sm:grid-cols-2 text-xs">
              <li v-for="iv in driveMissingByStatus.draft" :key="iv.id" class="flex items-baseline gap-2">
                <span :class="['inline-block px-1.5 py-0.5 rounded text-[10px]', catStyle(iv.category)]">{{ iv.category }}</span>
                <span class="text-gray-800">{{ iv.name }}</span>
                <span class="text-gray-400">{{ iv.date }}</span>
              </li>
            </ul>
          </div>

          <div v-if="driveMissingByStatus.audioOnly.length" class="mb-4">
            <h4 class="text-xs font-semibold text-gray-600 mb-2">🎙️ 只有錄音 m4a，尚未轉文字</h4>
            <ul class="grid gap-1.5 sm:grid-cols-2 text-xs">
              <li v-for="iv in driveMissingByStatus.audioOnly" :key="iv.id" class="flex items-baseline gap-2">
                <span :class="['inline-block px-1.5 py-0.5 rounded text-[10px]', catStyle(iv.category)]">{{ iv.category }}</span>
                <span class="text-gray-800">{{ iv.name }}</span>
                <span class="text-gray-400">{{ iv.date }}</span>
                <span v-if="iv.note" class="text-gray-400 italic">— {{ iv.note }}</span>
              </li>
            </ul>
          </div>

          <div v-if="driveMissingByStatus.outlineOnly.length">
            <h4 class="text-xs font-semibold text-gray-600 mb-2">📋 只有訪綱，連錄音也沒有</h4>
            <ul class="grid gap-1.5 sm:grid-cols-2 text-xs">
              <li v-for="iv in driveMissingByStatus.outlineOnly" :key="iv.id" class="flex items-baseline gap-2">
                <span :class="['inline-block px-1.5 py-0.5 rounded text-[10px]', catStyle(iv.category)]">{{ iv.category }}</span>
                <span class="text-gray-800">{{ iv.name }}</span>
                <span class="text-gray-400">{{ iv.date }}</span>
                <span v-if="iv.note" class="text-gray-400 italic">— {{ iv.note }}</span>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <!-- ③ 參考資料 -->
      <div v-if="activeTab === 'references'">
        <div class="thesis-page">
          <div v-if="refLoading" class="flex items-center justify-center h-40 text-gray-400 text-sm">載入中⋯</div>
          <div v-else class="thesis-body" v-html="formattedRef"></div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '碩士論文 — 印順導師人間佛教思想的傳承與實踐' })

const route = useRoute()
const activeTab = ref((route.query.tab as string) || 'content')
const activeChapter = ref('abstract')
const activeCategory = ref('全部')
const chapterText = ref('')
const refRawText = ref('')
const loading = ref(false)
const refLoading = ref(false)

const keywords = ['人間佛教', '太虛大師', '印順導師', '昭慧法師', '性廣法師', '佛教弘誓學院']
const tabs = [
  { id: 'content', label: '論文內容' },
  { id: 'interviews', label: '口述訪談' },
  { id: 'references', label: '參考資料' },
]
const chapters = [
  { id: 'abstract', shortTitle: '摘要 / Abstract', title: '摘要' },
  { id: 'ch1', shortTitle: '第一章　緒論', title: '第一章　緒論' },
  { id: 'ch2', shortTitle: '第二章　印順導師人間佛教', title: '第二章　印順導師人間佛教的體系演變與思想傳承' },
  { id: 'ch3', shortTitle: '第三章　人間佛教事業', title: '第三章　昭慧法師與性廣法師的人間佛教事業' },
  { id: 'ch4', shortTitle: '第四章　社運界、教育界', title: '第四章　昭慧法師與性廣法師在社運界、教育界的行動' },
  { id: 'ch5', shortTitle: '第五章　思想特徵', title: '第五章　昭慧法師與性廣法師的思想特徵' },
  { id: 'ch6', shortTitle: '第六章　結論', title: '第六章　結論' },
  { id: 'app2', shortTitle: '附錄一、二　組織圖・年表', title: '附錄一、二' },
  { id: 'app3', shortTitle: '附錄三　著作目錄', title: '附錄三' },
  { id: 'app4', shortTitle: '附錄四　訪談人物分類表', title: '附錄四' },
]

// ── 文字格式化 ──────────────────────────────────────────
function esc(s: string) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}

function parseTableRow(line: string): string[] {
  return line.split('|').slice(1, -1).map(c => c.trim())
}
function isAlignRow(row: string[]): boolean {
  return row.every(c => /^:?-+:?$/.test(c) || c === '')
}
function renderTable(rows: string[][]): string {
  const filtered = rows.filter(r => !isAlignRow(r) && !r.every(c => c === ''))
  if (!filtered.length) return ''
  const [head, ...body] = filtered
  const thead = `<thead><tr>${head.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead>`
  const tbody = body.length ? `<tbody>${body.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody>` : ''
  return `<div class="t-table-wrap"><table class="t-table">${thead}${tbody}</table></div>`
}

function formatThesis(text: string): string {
  if (!text) return ''
  const lines = text.split('\n')
  const out: string[] = []
  let inEn = false
  const tableRows: string[][] = []

  for (const line of lines) {
    const t = line.trim()

    if (t.startsWith('|')) {
      tableRows.push(parseTableRow(t))
      continue
    }

    if (tableRows.length) {
      out.push(renderTable(tableRows))
      tableRows.length = 0
    }

    if (!t) { out.push('<div class="t-gap"></div>'); continue }

    // Strip trailing table artifact from lines that mix heading text with a table marker
    const pipeIdx = t.indexOf(' |  |')
    const clean = pipeIdx > -1 ? t.substring(0, pipeIdx).trim() : t
    if (!clean) continue

    // 跳過目錄頁碼（純數字行）
    if (/^\d{1,3}$/.test(clean)) continue
    // 跳過目錄條目（包含大量省略號）
    if ((/[…．·.]{4,}/.test(clean) || /\.{4,}/.test(clean)) && /\d+\s*$/.test(clean)) continue
    // 跳過論文目錄標題行
    if (/^論\s+文\s+目/.test(clean)) continue

    if (clean === '摘要') {
      inEn = false
      out.push(`<h2 class="t-meta-title">${esc(clean)}</h2>`)
    } else if (clean === 'Abstract') {
      inEn = true
      out.push(`<h2 class="t-meta-title">${esc(clean)}</h2>`)
    } else if (/^第[一二三四五六七八九十百]+章/.test(clean)) {
      inEn = false
      out.push(`<h2 class="t-chapter">${esc(clean)}</h2>`)
    } else if (/^第[一二三四五六七八九十百]+節/.test(clean)) {
      out.push(`<h3 class="t-section">${esc(clean)}</h3>`)
    } else if (/^[一二三四五六七八九十]+、/.test(clean)) {
      out.push(`<h4 class="t-subsection">${esc(clean)}</h4>`)
    } else if (/^（[一二三四五六七八九十]+）/.test(clean)) {
      out.push(`<h5 class="t-subsubsection">${esc(clean)}</h5>`)
    } else if (/^附錄[一二三四五六七八九十]+/.test(clean)) {
      out.push(`<h4 class="t-subsection">${esc(clean)}</h4>`)
    } else if (clean.startsWith('關鍵字：') || clean.startsWith('Keywords')) {
      out.push(`<p class="t-keywords">${esc(clean)}</p>`)
    } else if (/^\[\d+\]/.test(clean)) {
      out.push(`<p class="t-footnote">${esc(clean)}</p>`)
    } else if (inEn) {
      out.push(`<p class="t-para-en">${esc(clean)}</p>`)
    } else {
      out.push(`<p class="t-para">${esc(clean)}</p>`)
    }
  }

  if (tableRows.length) out.push(renderTable(tableRows))
  return out.join('')
}

const formattedChapter = computed(() => formatThesis(chapterText.value))

const formattedRef = computed(() => {
  const raw = refRawText.value
  if (!raw) return ''
  const idx = raw.indexOf('徵引資料')
  return formatThesis(idx > -1 ? raw.substring(idx) : raw)
})

// ── 資料載入 ──────────────────────────────────────────
async function loadChapter(id: string) {
  loading.value = true
  try {
    chapterText.value = await $fetch<string>(`/content/thesis/${id}.txt`) as string
  } catch { chapterText.value = '（載入失敗）' }
  loading.value = false
}

async function selectChapter(id: string) {
  activeChapter.value = id
  await loadChapter(id)
}

watch(activeTab, async (tab) => {
  if (tab === 'references' && !refRawText.value) {
    refLoading.value = true
    try {
      refRawText.value = await $fetch<string>('/content/thesis/ch6.txt') as string
    } catch { refRawText.value = '（載入失敗）' }
    refLoading.value = false
  }
})

onMounted(() => loadChapter('abstract'))

// ── 訪談列表（Pinia store） ─────────────────────────────
const interviewsStore = useThesisInterviewsStore()
const interviews = computed(() => interviewsStore.published)
const driveMissingByStatus = computed(() => interviewsStore.driveMissingByStatus)
const categories = ['全部', '法師', '學者', '宗教對話', '社運界', '其他']
const filteredInterviews = computed(() =>
  activeCategory.value === '全部' ? interviews.value : interviews.value.filter(iv => iv.category === activeCategory.value)
)
function catStyle(cat: string) {
  const m: Record<string,string> = { '法師':'bg-amber-100 text-amber-700','學者':'bg-blue-100 text-blue-700','宗教對話':'bg-green-100 text-green-700','社運界':'bg-rose-100 text-rose-700','其他':'bg-gray-100 text-gray-600' }
  return m[cat] ?? 'bg-gray-100 text-gray-600'
}
function catIcon(cat: string) {
  const m: Record<string,string> = { '法師':'🪷','學者':'📚','宗教對話':'🕊️','社運界':'✊','其他':'👤' }
  return m[cat] ?? '👤'
}
</script>

<style scoped>
/* ── 論文頁面容器 ── */
.thesis-page {
  background: white;
  border-radius: 1rem;
  border: 1px solid #f0f0f0;
  padding: 2.5rem 3rem;
  font-family: 'Georgia', 'Noto Serif TC', 'Source Han Serif TC', serif;
}

/* ── 論文正文排版 ── */
:deep(.t-chapter) {
  font-size: 1.375rem;
  font-weight: 700;
  text-align: center;
  margin: 3rem 0 1.5rem;
  letter-spacing: 0.08em;
  color: #111827;
  line-height: 1.5;
}
:deep(.t-meta-title) {
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
  margin: 2rem 0 1.25rem;
  color: #111827;
}
:deep(.t-section) {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 2.5rem 0 1rem;
  color: #1f2937;
  letter-spacing: 0.02em;
}
:deep(.t-subsection) {
  font-size: 1rem;
  font-weight: 600;
  margin: 1.75rem 0 0.75rem;
  color: #374151;
}
:deep(.t-subsubsection) {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 1.25rem 0 0.5rem;
  color: #374151;
}
:deep(.t-para) {
  font-size: 0.9rem;
  line-height: 2.2;
  text-indent: 2em;
  margin-bottom: 0.6rem;
  color: #1f2937;
}
:deep(.t-para-en) {
  font-size: 0.9rem;
  line-height: 1.9;
  margin-bottom: 0.75rem;
  color: #1f2937;
  font-family: 'Georgia', serif;
}
:deep(.t-keywords) {
  font-size: 0.875rem;
  font-weight: 500;
  border-left: 3px solid #a78bfa;
  padding-left: 1rem;
  margin: 1.5rem 0;
  color: #374151;
  line-height: 1.8;
}
:deep(.t-footnote) {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.8;
  padding-left: 2em;
  text-indent: -2em;
  margin-bottom: 0.375rem;
  border-top: 1px solid #f3f4f6;
  padding-top: 0.25rem;
}
:deep(.t-gap) {
  height: 0.4rem;
}
:deep(.t-table-wrap) {
  overflow-x: auto;
  margin: 1.5rem 0;
}
:deep(.t-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  line-height: 1.6;
}
:deep(.t-table th) {
  background: #f3f4f6;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  white-space: nowrap;
}
:deep(.t-table td) {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e5e7eb;
  vertical-align: top;
}
:deep(.t-table tbody tr:nth-child(even)) {
  background: #f9fafb;
}
</style>
