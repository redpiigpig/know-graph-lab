<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader :title="displayTitle" :back="{ to: `/works/${slug}`, label: '口述訪談列表' }" container-class="max-w-4xl">
      <template #actions>
        <a
          v-if="!error"
          :href="docxUrl"
          class="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md bg-rose-50 text-rose-700 hover:bg-rose-100 transition"
          :download="`${displayTitle}.docx`"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          下載 Word
        </a>
      </template>
    </AppHeader>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <div v-if="loading" class="flex items-center justify-center h-64 text-gray-400 text-sm">載入中⋯</div>
      <div v-else-if="error" class="flex items-center justify-center h-64 text-gray-400 text-sm">
        找不到訪談紀錄：{{ route.params.name }}
      </div>
      <div v-else>
        <div class="bg-white rounded-2xl border border-gray-100 px-8 py-8">
          <div class="interview-page" v-html="formatted" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const slug = computed(() => String(route.params.slug ?? ''))
const content = ref('')
const loading = ref(true)
const error = ref(false)

const displayTitle = computed(() => {
  const name = decodeURIComponent(route.params.name as string)
  return name.replace(/\.(txt|docx)$/i, '')
})

const docxUrl = computed(() => `/api/thesis/interview-docx?name=${encodeURIComponent(displayTitle.value)}`)

useHead(() => ({ title: `${displayTitle.value} — 口述訪談` }))

function formatInterview(text: string): string {
  if (!text) return ''
  const lines = text.split('\n')
  const out: string[] = []
  let isFirst = true

  for (const line of lines) {
    let t = line.trim()
    if (!t) {
      out.push('<div class="i-gap"></div>')
      continue
    }

    // 註釋標記 [n](#footnoteN)：定義在論文附錄，網頁渲染成統一上標（nonchurch 格式外觀）
    t = t.replace(/\[(\d+)\]\(#footnote\d+\)/g, '<sup class="footnote-ref" title="註 $1（全註見碩士論文附錄）">$1</sup>')

    // First non-empty line → interview title
    if (isFirst) {
      isFirst = false
      out.push(`<h1 class="i-title">${t}</h1>`)
      continue
    }

    // Metadata lines
    if (/^(受訪者|訪問者|訪問時間|訪問地點|訪談時間|訪談地點|採訪者|採訪時間|採訪地點)：/.test(t)) {
      out.push(`<p class="i-meta">${t}</p>`)
      continue
    }

    // Section headings with Chinese numeral prefix: 一、二、三、…
    if (/^[一二三四五六七八九十]+、/.test(t)) {
      out.push(`<h2 class="i-section">${t}</h2>`)
      continue
    }

    // Subsection headings: （一）（二）…
    if (/^（[一二三四五六七八九十]+）/.test(t)) {
      out.push(`<h3 class="i-subsection">${t}</h3>`)
      continue
    }

    // Interviewer question: 筆者：...
    if (/^筆者：/.test(t)) {
      const body = t.replace(/^筆者：/, '')
      out.push(`<div class="i-q"><span class="i-q-label">問</span><span class="i-q-body">${body}</span></div>`)
      continue
    }

    // Interviewee answer: short Chinese name + title suffix + colon
    const answerMatch = t.match(/^([一-鿿]{1,4}(?:法師|教授|主教|和尚|居士|博士|老師|牧師|女士|先生))：(.+)/)
    if (answerMatch) {
      const label = answerMatch[1]
      const body = answerMatch[2]
      out.push(`<div class="i-a"><span class="i-a-label">${label}</span><span class="i-a-body">${body}</span></div>`)
      continue
    }

    // Short standalone line (≤ 25 chars, no punctuation at end) → unlabelled heading
    if (t.length <= 25 && !/[。，、；：？！…]$/.test(t) && !/^[\[【（〔]/.test(t)) {
      out.push(`<h2 class="i-section">${t}</h2>`)
      continue
    }

    // Regular paragraph
    out.push(`<p class="i-para">${t}</p>`)
  }

  return out.join('')
}

const formatted = computed(() => formatInterview(content.value))

onMounted(async () => {
  try {
    const filename = decodeURIComponent(route.params.name as string)
    const text = await $fetch<string>(`/content/interviews/${filename}.txt`)
    content.value = text as string
  } catch {
    error.value = true
  }
  loading.value = false
})
</script>

<style scoped>
/* 註釋上標（nonchurch 格式外觀） */
:deep(sup.footnote-ref) { font-size: 0.68em; vertical-align: super; color: #2563eb; }

.interview-page {
  font-family: 'Georgia', 'Noto Serif TC', serif;
  color: #1a1a1a;
}

:deep(.i-title) {
  font-size: 1.375rem;
  font-weight: 700;
  text-align: center;
  letter-spacing: 0.06em;
  margin: 0 0 1.5rem;
  line-height: 1.6;
  color: #111827;
}

:deep(.i-meta) {
  font-size: 0.8125rem;
  color: #6b7280;
  text-align: center;
  margin: 0.15rem 0;
  letter-spacing: 0.03em;
}

:deep(.i-gap) {
  height: 0.75rem;
}

:deep(.i-section) {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #374151;
  margin: 2.5rem 0 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1.5px solid #e5e7eb;
  letter-spacing: 0.04em;
}

:deep(.i-subsection) {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #4b5563;
  margin: 1.5rem 0 0.6rem;
  letter-spacing: 0.02em;
}

:deep(.i-para) {
  font-size: 0.9rem;
  line-height: 2.2;
  text-indent: 2em;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

:deep(.i-q) {
  margin: 1.25rem 0 0.5rem;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-left: 3px solid #d1d5db;
  border-radius: 0 0.5rem 0.5rem 0;
}

:deep(.i-q-label) {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  color: #6b7280;
  background: #e5e7eb;
  border-radius: 0.25rem;
  padding: 0.15rem 0.5rem;
  letter-spacing: 0.05em;
  font-style: normal;
  margin-bottom: 0.4rem;
}

:deep(.i-q-body) {
  display: block;
  font-size: 0.875rem;
  line-height: 2;
  color: #374151;
  font-style: italic;
  text-indent: 2em;
}

:deep(.i-a) {
  margin: 0.5rem 0 1.25rem;
}

:deep(.i-a-label) {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  color: #be123c;
  background: #ffe4e6;
  border-radius: 0.25rem;
  padding: 0.15rem 0.5rem;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
}

:deep(.i-a-body) {
  display: block;
  font-size: 0.9125rem;
  line-height: 2.15;
  color: #111827;
  text-indent: 2em;
}
</style>
