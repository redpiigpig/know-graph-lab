<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/works/million-masks" class="text-gray-400 hover:text-gray-700 transition text-sm">← 千面上帝</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700 truncate">{{ title }}</span>
      </div>
    </nav>

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="loading" class="flex items-center justify-center h-40 text-gray-400 text-sm">載入中⋯</div>
      <div v-else-if="error" class="text-center text-gray-400 py-20">
        <div class="text-3xl mb-3">⚠️</div>
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <!-- 標題區 -->
        <div class="mb-8">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 mb-3 inline-block">宗教史讀書會</span>
          <h1 class="text-xl font-bold text-gray-900 leading-snug">{{ title }}</h1>
        </div>

        <!-- 逐字稿 -->
        <div class="transcript-page">
          <div class="transcript-body" v-html="formatted"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const filename = computed(() => decodeURIComponent(route.params.filename as string))

const rawText = ref('')
const loading = ref(true)
const error = ref('')

const title = computed(() => {
  const lines = rawText.value.split('\n')
  return lines[0]?.trim() || filename.value
})

function formatTranscript(text: string): string {
  if (!text) return ''
  const lines = text.split('\n')
  const out: string[] = []
  const esc = (s: string) => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')

  for (const line of lines) {
    const t = line.trim()
    if (!t) { out.push('<div class="t-gap"></div>'); continue }
    if (out.length === 0) {
      out.push(`<h1 class="t-title">${esc(t)}</h1>`)
    } else if (/^【.+】$/.test(t)) {
      out.push(`<p class="t-note">${esc(t)}</p>`)
    } else if (/^(受訪者|訪問時間|訪問地點|主題|集數|日期)：/.test(t)) {
      out.push(`<p class="t-meta">${esc(t)}</p>`)
    } else {
      out.push(`<p class="t-para">${esc(t)}</p>`)
    }
  }
  return out.join('')
}

const formatted = computed(() => formatTranscript(rawText.value))

useHead(() => ({ title: `${title.value} — 宗教史讀書會 — Know Graph Lab` }))

onMounted(async () => {
  try {
    rawText.value = await $fetch<string>(`/content/million-masks-readings/${filename.value}.txt`) as string
  } catch {
    error.value = '逐字稿載入失敗，請確認檔案是否存在'
  }
  loading.value = false
})
</script>

<style scoped>
.transcript-page {
  background: white;
  border-radius: 1rem;
  border: 1px solid #f0f0f0;
  padding: 2.5rem 3rem;
  font-family: 'Georgia', 'Noto Serif TC', serif;
}
:deep(.t-title) {
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
  color: #111827;
}
:deep(.t-meta) {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  border-left: 3px solid #fcd34d;
  padding-left: 0.75rem;
}
:deep(.t-note) {
  font-size: 0.8rem;
  color: #9ca3af;
  font-style: italic;
  margin: 1rem 0;
}
:deep(.t-para) {
  font-size: 0.9rem;
  line-height: 2.2;
  text-indent: 2em;
  margin-bottom: 0.5rem;
  color: #1f2937;
}
:deep(.t-gap) {
  height: 0.6rem;
}
</style>
