<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 論文寫作系統</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">學士論文線上版</span>
      </div>
    </nav>

    <!-- 封面 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">學士論文</span>
          <span class="text-xs text-gray-400">國立臺灣大學文學院歷史學系</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 leading-snug mb-1">
          福音派運動在台灣基督教中的
          <span class="text-blue-700">起源與發展</span>
        </h1>
        <p class="text-sm text-gray-400 italic mb-5">
          The Origin and Development of Evangelical Movement in Taiwan
        </p>
        <div class="flex flex-wrap gap-5 text-sm text-gray-600 mb-4">
          <div><span class="text-gray-400 mr-1">作者</span>張辰瑋</div>
          <div><span class="text-gray-400 mr-1">指導教授</span>羅士傑 博士</div>
          <div><span class="text-gray-400 mr-1">完成時間</span>中華民國 107 年 5 月（2018）</div>
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
            :class="['px-5 py-3.5 text-sm font-medium border-b-2 transition-colors', activeTab === tab.id ? 'border-blue-600 text-blue-700' : 'border-transparent text-gray-500 hover:text-gray-800']">
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
        <aside class="w-52 flex-shrink-0 hidden md:block">
          <div class="sticky top-28 space-y-0.5">
            <button v-for="ch in chapters" :key="ch.id" @click="selectChapter(ch.id)"
              :class="['w-full text-left px-3 py-2 rounded-lg text-xs transition-colors leading-snug', activeChapter === ch.id ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700']">
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

      <!-- ② 參考資料 -->
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
useHead({ title: '學士論文 — 福音派運動在台灣基督教中的起源與發展' })

const route = useRoute()
const activeTab = ref((route.query.tab as string) || 'content')
const activeChapter = ref('abstract')
const chapterText = ref('')
const refRawText = ref('')
const loading = ref(false)
const refLoading = ref(false)

const keywords = ['當代基督教史', '福音派', '洛桑運動', '台灣基督教史', '華語教會']
const tabs = [
  { id: 'content', label: '論文內容' },
  { id: 'references', label: '參考資料' },
]
const chapters = [
  { id: 'abstract', shortTitle: '摘要 / Abstract' },
  { id: 'ch1', shortTitle: '第一章　全球福音派的興起' },
  { id: 'ch2', shortTitle: '第二章　台灣福音派的歷史' },
  { id: 'ch3', shortTitle: '第三章　各教派與機構的角色' },
  { id: 'ch4', shortTitle: '第四章　政治環境與國際關係' },
  { id: 'ch5', shortTitle: '第五章　海外華人與宣教士' },
  { id: 'ch6', shortTitle: '第六章　總結' },
]

// ── 文字格式化 ──────────────────────────────────────────
function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function formatThesis(text: string): string {
  if (!text) return ''
  const lines = text.split('\n')
  const out: string[] = []
  let inEn = false

  for (const line of lines) {
    const t = line.trim()
    if (!t) { out.push('<div class="t-gap"></div>'); continue }

    // 跳過純數字行（頁碼）
    if (/^\d{1,3}$/.test(t)) continue
    // 跳過目錄條目（省略號 + 數字）
    if ((/[…．·.]{4,}/.test(t) || /\.{4,}/.test(t)) && /\d+\s*$/.test(t)) continue
    // 跳過目錄/圖目錄/表目錄標題
    if (/^[論圖表]\s+目\s+錄$/.test(t) || /^目\s+錄$/.test(t)) continue
    // 跳過羅馬數字頁碼行（i, ii, iii...）
    if (/^[ivxIVX]+$/.test(t)) continue

    if (t === '中文摘要' || t === '摘要') {
      inEn = false
      out.push(`<h2 class="t-meta-title">${esc(t)}</h2>`)
    } else if (t === 'Abstract') {
      inEn = true
      out.push(`<h2 class="t-meta-title">${esc(t)}</h2>`)
    } else if (t === '誌謝') {
      inEn = false
      out.push(`<h2 class="t-meta-title">${esc(t)}</h2>`)
    } else if (/^第[一二三四五六七八九十]+章/.test(t)) {
      inEn = false
      out.push(`<h2 class="t-chapter">${esc(t)}</h2>`)
    } else if (/^（[一二三四五六七八九十]+）/.test(t)) {
      out.push(`<h3 class="t-section">${esc(t)}</h3>`)
    } else if (/^[一二三四五六七八九十]+、/.test(t)) {
      out.push(`<h4 class="t-subsection">${esc(t)}</h4>`)
    } else if (/^（\d+）/.test(t)) {
      out.push(`<h5 class="t-subsubsection">${esc(t)}</h5>`)
    } else if (/^附錄/.test(t)) {
      out.push(`<h4 class="t-subsection">${esc(t)}</h4>`)
    } else if (t.startsWith('關鍵字：') || t.startsWith('Keywords')) {
      out.push(`<p class="t-keywords">${esc(t)}</p>`)
    } else if (/^\d+\s/.test(t) && /[。，、：；]|[A-Z]/.test(t.substring(0, 30))) {
      // 腳註定義行（數字開頭後接空格和文字）
      out.push(`<p class="t-footnote">${esc(t)}</p>`)
    } else if (inEn) {
      out.push(`<p class="t-para-en">${esc(t)}</p>`)
    } else {
      out.push(`<p class="t-para">${esc(t)}</p>`)
    }
  }
  return out.join('')
}

const formattedChapter = computed(() => formatThesis(chapterText.value))

const formattedRef = computed(() => {
  const raw = refRawText.value
  if (!raw) return ''
  const idx = raw.indexOf('參考文獻')
  return formatThesis(idx > -1 ? raw.substring(idx) : raw)
})

// ── 資料載入 ──────────────────────────────────────────
async function loadChapter(id: string) {
  loading.value = true
  try {
    chapterText.value = await $fetch<string>(`/content/bachelor/${id}.txt`) as string
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
      refRawText.value = await $fetch<string>('/content/bachelor/ref.txt') as string
    } catch { refRawText.value = '（載入失敗）' }
    refLoading.value = false
  }
})

onMounted(() => loadChapter('abstract'))
</script>

<style scoped>
.thesis-page {
  background: white;
  border-radius: 1rem;
  border: 1px solid #f0f0f0;
  padding: 2.5rem 3rem;
  font-family: 'Georgia', 'Noto Serif TC', 'Source Han Serif TC', serif;
}

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
  border-left: 3px solid #93c5fd;
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
</style>
