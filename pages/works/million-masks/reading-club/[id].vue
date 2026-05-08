<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/works/million-masks" class="text-gray-400 hover:text-gray-700 transition text-sm">← 千面上帝</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700 truncate">{{ data?.title ?? '載入中…' }}</span>
      </div>
    </nav>

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="pending" class="flex items-center justify-center h-40 text-gray-400 text-sm">載入中⋯</div>
      <div v-else-if="error" class="text-center text-gray-400 py-20">
        <div class="text-3xl mb-3">⚠️</div>
        <p>逐字稿載入失敗</p>
      </div>
      <div v-else-if="data">
        <!-- 標題區 -->
        <div class="mb-6">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 mb-3 inline-block">宗教史讀書會 第 {{ data.episode }} 集</span>
          <h1 class="text-xl font-bold text-gray-900 leading-snug mb-3">{{ data.title }}</h1>

          <!-- 日期 + 連結列 -->
          <div class="flex flex-wrap items-center gap-3 text-sm">
            <span v-if="data.video_date" class="text-gray-500">{{ data.video_date }}</span>
            <a v-if="data.youtube_id"
               :href="`https://www.youtube.com/watch?v=${data.youtube_id}`"
               target="_blank" rel="noopener"
               class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 text-red-600 hover:bg-red-100 transition text-xs font-medium">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              YouTube
            </a>
            <a v-if="data.ppt_r2_key"
               :href="`/api/works/ppt-download/${route.params.id}`"
               class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 hover:bg-amber-100 transition text-xs font-medium">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 16V4M12 16l-4-4M12 16l4-4M4 20h16" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              下載投影片
            </a>
          </div>
        </div>

        <div class="transcript-page">
          <div class="transcript-body" v-html="formatted"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const id = route.params.id as string

const { data, pending, error } = await useFetch<{
  content: string
  title: string
  episode: number
  video_date: string | null
  youtube_id: string | null
  ppt_r2_key: string | null
}>(`/api/works/transcript/${id}`)

useHead(() => ({ title: `${data.value?.title ?? '逐字稿'} — 宗教史讀書會 — Know Graph Lab` }))

function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const formatted = computed(() => {
  const text = data.value?.content ?? ''
  if (!text) return ''
  const out: string[] = []
  let first = true
  for (const line of text.split('\n')) {
    const t = line.trim()
    if (!t) { out.push('<div class="t-gap"></div>'); continue }
    if (first) { out.push(`<h1 class="t-title">${esc(t)}</h1>`); first = false; continue }
    if (/^\[.+\]$/.test(t)) { out.push(`<p class="t-note">${esc(t)}</p>`); continue }
    if (/^(Episode|Date):/.test(t)) { out.push(`<p class="t-meta">${esc(t)}</p>`); continue }
    if (t.startsWith('## ')) { out.push(`<h2 class="t-heading">${esc(t.slice(3))}</h2>`); continue }
    if (t.startsWith('---')) { out.push('<hr class="t-rule">'); continue }
    if (t.startsWith('*') && t.endsWith('*')) { out.push(`<p class="t-note">${esc(t.replace(/^\*+|\*+$/g, ''))}</p>`); continue }
    out.push(`<p class="t-para">${esc(t).replace(/\*([^*\n]+)\*/g, '<em>$1</em>')}</p>`)
  }
  return out.join('')
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
:deep(.t-title) { font-size:1.2rem; font-weight:700; text-align:center; margin-bottom:1.5rem; color:#111827; }
:deep(.t-meta)  { font-size:0.875rem; color:#6b7280; margin-bottom:0.25rem; border-left:3px solid #fcd34d; padding-left:0.75rem; }
:deep(.t-note)  { font-size:0.8rem; color:#9ca3af; font-style:italic; margin:1rem 0; }
:deep(.t-para)  { font-size:0.9rem; line-height:2.2; text-indent:2em; margin-bottom:0.5rem; color:#1f2937; }
:deep(.t-gap)   { height:0.6rem; }
:deep(.t-heading) { font-size:1rem; font-weight:700; color:#92400e; margin:2rem 0 0.6rem; padding-bottom:0.3rem; border-bottom:1px solid #fde68a; }
:deep(.t-rule) { border:none; border-top:1px solid #f3f4f6; margin:1.5rem 0; }
</style>
