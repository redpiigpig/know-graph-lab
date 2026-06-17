<template>
  <div :class="['min-h-screen', isEditorial ? 'bg-amber-50/40' : 'bg-slate-50']">

    <AppHeader
      :title="isEditorial ? '報紙社論' : '學術著作目錄'"
      :back="isEditorial ? { to: '/papers?type=editorial', label: '報紙社論' } : { to: '/papers', label: '學術著作目錄' }"
      container-class="max-w-3xl"
    >
      <template #actions>
        <a
          v-if="isEditorial && editorialMeta?.originalUrl"
          :href="editorialMeta.originalUrl" target="_blank" rel="noopener"
          class="text-xs font-medium text-orange-700 hover:text-orange-900 bg-orange-50 hover:bg-orange-100 px-3 py-1.5 rounded transition"
        >查看 tcnn.org.tw 原文 →</a>
      </template>
    </AppHeader>

    <!-- 報紙抬頭（社論專用） -->
    <div v-if="isEditorial && editorialMeta" class="bg-white border-b-4 border-double border-orange-700">
      <div class="max-w-3xl mx-auto px-6 py-5 flex items-end justify-between">
        <div>
          <div class="text-[11px] tracking-[0.3em] text-orange-700 mb-1">TAIWAN CHURCH NEWS</div>
          <div class="text-2xl font-bold text-orange-800" style="font-family: '標楷體', 'DFKai-SB', 'BiauKai', 'KaiTi', serif">{{ editorialMeta.venue }}</div>
        </div>
        <div class="text-right text-xs text-gray-500 leading-relaxed">
          <div>第 <span class="font-semibold text-gray-800">{{ editorialMeta.issue }}</span> 期</div>
          <div>{{ editorialMeta.date }}</div>
        </div>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="pending" class="text-center text-gray-400 py-20 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-400 py-20 text-sm">無法載入全文</div>
      <article
        v-else
        :class="[
          'bg-white rounded-2xl border px-10 py-12 md:px-16',
          isEditorial ? 'border-orange-100 shadow-sm editorial-article' : 'border-gray-100'
        ]"
      >
        <template v-for="(line, idx) in parsedLines" :key="idx">
          <!-- 標題 -->
          <h1 v-if="line.type === 'title'"
            :class="isEditorial
              ? 'text-3xl font-bold text-gray-900 text-center leading-snug mb-3 editorial-title'
              : 'text-xl font-bold text-gray-900 text-center leading-snug mb-2'">{{ line.text }}</h1>
          <!-- 作者、機構、期刊、日期等元資料（社論模式由抬頭顯示，這邊只留作者署名） -->
          <p v-else-if="line.type === 'meta'"
            :class="isEditorial
              ? (line.text === '張辰瑋' ? 'text-sm text-gray-600 text-center leading-snug mb-6 italic' : 'hidden')
              : 'text-sm text-gray-500 text-center leading-snug mb-0.5'">{{ line.text }}</p>
          <!-- 摘要 / Abstract 標籤 -->
          <div v-else-if="line.type === 'abstract-label'"
            class="text-sm font-bold text-gray-900 text-center mt-7 mb-2">{{ line.text }}</div>
          <!-- 關鍵字 -->
          <p v-else-if="line.type === 'keywords'"
            class="text-xs text-gray-400 text-center italic mb-6">{{ line.text }}</p>
          <!-- 一、二、三… 大節標題 -->
          <h2 v-else-if="line.type === 'h2'"
            class="text-base font-bold text-gray-900 text-center mt-10 mb-3">{{ line.text }}</h2>
          <!-- （一）（二）… 小節標題 -->
          <h3 v-else-if="line.type === 'h3'"
            class="text-sm font-semibold text-gray-800 text-center mt-6 mb-2">{{ line.text }}</h3>
          <!-- 參考資料 大標 -->
          <h2 v-else-if="line.type === 'ref-section'"
            class="text-base font-bold text-gray-900 text-center mt-12 mb-4 pt-6 border-t border-gray-200">{{ line.text }}</h2>
          <!-- 專書 / 單篇論文 子標 -->
          <h3 v-else-if="line.type === 'ref-subsection'"
            class="text-sm font-semibold text-gray-700 mt-5 mb-2">{{ line.text }}</h3>
          <!-- 參考資料條目 -->
          <p v-else-if="line.type === 'ref-item'"
            class="text-sm text-gray-600 leading-relaxed mb-1.5 pl-5 -indent-5">{{ line.text }}</p>
          <!-- 注釋 大標 -->
          <h2 v-else-if="line.type === 'note-section'"
            class="text-base font-bold text-gray-900 text-center mt-12 mb-4 pt-6 border-t border-gray-200">{{ line.text }}</h2>
          <!-- 注釋條目 -->
          <p v-else-if="line.type === 'note-item'"
            class="text-xs text-gray-500 leading-relaxed mb-1 pl-8 -indent-8"
            v-html="inline(line.text)"></p>
          <!-- 引用區塊 -->
          <blockquote v-else-if="line.type === 'quote'"
            class="text-sm leading-7 text-gray-700 my-6 pl-[3em]"
            style="font-family: '標楷體', 'DFKai-SB', 'BiauKai', 'KaiTi', serif"
            v-html="inline(line.text)"></blockquote>
          <!-- 正文段落 -->
          <p v-else
            class="text-sm leading-7 text-gray-800 mb-4 indent-[2em]"
            v-html="inline(line.text)"></p>
        </template>

        <!-- 社論結尾：原文連結 -->
        <div v-if="isEditorial && editorialMeta?.originalUrl" class="mt-10 pt-6 border-t border-double border-orange-200 text-center">
          <a
            :href="editorialMeta.originalUrl" target="_blank" rel="noopener"
            class="inline-flex items-center gap-2 text-xs text-orange-700 hover:text-orange-900 font-medium px-4 py-2 rounded-full bg-orange-50 hover:bg-orange-100 transition"
          >
            <span>原文刊於 {{ editorialMeta.venue }} 第 {{ editorialMeta.issue }} 期</span>
            <span>→</span>
          </a>
        </div>
      </article>
    </div>

  </div>
</template>

<script setup lang="ts">
const route = useRoute()

const EDITORIAL_META: Record<string, { venue: string; issue: string; date: string; originalUrl: string }> = {
  e1: { venue: '台灣教會公報', issue: '3473', date: '2018 年 9 月 21 日', originalUrl: 'https://tcnn.org.tw/archives/42359' },
  e2: { venue: '台灣教會公報', issue: '3471', date: '2018 年 9 月 7 日', originalUrl: 'https://tcnn.org.tw/archives/20975' },
  e3: { venue: '台灣教會公報', issue: '3435', date: '2017 年 12 月 26 日', originalUrl: 'https://tcnn.org.tw/archives/30630' },
}

const isEditorial = computed(() => {
  const id = String(route.params.id || '')
  return /^e\d+$/.test(id)
})
const editorialMeta = computed(() =>
  isEditorial.value ? EDITORIAL_META[String(route.params.id)] : null
)

const { data, pending, error } = useFetch(
  () => `/content/papers/${route.params.id}.txt`,
  { responseType: 'text' }
)

type LineType =
  | 'title' | 'meta' | 'abstract-label' | 'keywords'
  | 'h2' | 'h3'
  | 'ref-section' | 'ref-subsection' | 'ref-item'
  | 'note-section' | 'note-item'
  | 'quote' | 'body'

interface ParsedLine { type: LineType; text: string }

const parsedLines = computed((): ParsedLine[] => {
  if (!data.value) return []

  const lines = (data.value as string).split('\n')
  const result: ParsedLine[] = []
  let inHeader = true
  let headerCount = 0
  let inRef = false
  let inNotes = false

  for (const raw of lines) {
    const text = raw.trim()
    if (!text) continue

    // 參考文獻區段（優先處理，避免內部一、二、三被誤判為正文大節）
    if (inRef) {
      if (text === '注釋' || text === '注解') {
        inRef = false; inNotes = true
        result.push({ type: 'note-section', text }); continue
      }
      if (
        /^[一二三四五六七八九十百]+[、．.]/.test(text) ||
        text === '專書' || text === '單篇論文'
      ) {
        result.push({ type: 'ref-subsection', text }); continue
      }
      result.push({ type: 'ref-item', text }); continue
    }

    // 注釋區段
    if (inNotes) {
      result.push({ type: 'note-item', text }); continue
    }

    // 區段切換
    if (text === '參考資料' || text === '參考文獻' || text === 'References') {
      inRef = true; inHeader = false
      result.push({ type: 'ref-section', text }); continue
    }
    if (text === '注釋' || text === '注解') {
      inNotes = true; inHeader = false
      result.push({ type: 'note-section', text }); continue
    }

    // 引用區塊（三個全形空格開頭）
    if (/^　　　/.test(raw)) {
      result.push({ type: 'quote', text }); continue
    }

    // 一、二、三… 大節標題
    if (/^[一二三四五六七八九十百]+、/.test(text)) {
      inHeader = false
      result.push({ type: 'h2', text }); continue
    }
    // （一）（二）… 小節標題
    if (/^（[一二三四五六七八九十]+）/.test(text) || /^\([一二三四五六七八九十]+\)/.test(text)) {
      result.push({ type: 'h3', text }); continue
    }
    // 摘要 / Abstract
    if (text === '摘要' || text === 'Abstract') {
      inHeader = false
      result.push({ type: 'abstract-label', text }); continue
    }
    // 關鍵字
    if (/^關鍵字[：:]/.test(text) || /^Keywords[：:]/.test(text)) {
      result.push({ type: 'keywords', text }); continue
    }

    // 標題區塊
    if (inHeader) {
      if (headerCount === 0) {
        result.push({ type: 'title', text })
        headerCount++; continue
      }
      if (headerCount >= 2 && text.length > 50) {
        inHeader = false
        result.push({ type: 'body', text: stripIndent(text) })
        headerCount++; continue
      }
      result.push({ type: 'meta', text })
      headerCount++; continue
    }

    result.push({ type: 'body', text: stripIndent(text) })
  }

  return result
})

// 去除全形縮排（txt 中有些段落以全形空格手動縮排，CSS 統一處理）
function stripIndent(text: string): string {
  return text.replace(/^　+/, '')
}

// 將行內 [n] 轉為上標，並做基本 HTML 跳脫
function inline(text: string): string {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped.replace(
    /\[(\d+)\]/g,
    '<sup style="font-size:0.65em;color:#0d9488;margin-left:1px;vertical-align:super;font-weight:400">[$1]</sup>'
  )
}
</script>

<style scoped>
.editorial-title {
  font-family: '標楷體', 'DFKai-SB', 'BiauKai', 'KaiTi', serif;
  letter-spacing: 0.05em;
}
.editorial-article :deep(p.indent-\[2em\]) {
  font-size: 0.95rem;
  line-height: 1.95;
  color: #1f2937;
}
</style>
