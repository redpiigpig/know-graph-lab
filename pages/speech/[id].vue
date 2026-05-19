<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-3xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/speech" class="text-gray-400 hover:text-gray-700 transition text-sm">← 演講活動</NuxtLink>
      </div>
    </nav>

    <div v-if="!talk" class="text-center text-gray-400 py-20 text-sm">找不到這場演講</div>

    <template v-else>
      <!-- 標題區 -->
      <div class="bg-white border-b border-gray-100">
        <div class="max-w-3xl mx-auto px-6 py-10">
          <div class="flex flex-wrap gap-1.5 mb-3">
            <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-rose-50 text-rose-700">演講活動</span>
            <span class="text-xs text-gray-500">{{ formatDate(talk.date) }}<span v-if="talk.duration"> ‧ {{ talk.duration }}</span></span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 leading-snug mb-2">{{ talk.title }}</h1>
          <p v-if="talk.subtitle" class="text-base text-gray-600 mb-5">── {{ talk.subtitle }}</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-xs text-gray-500 mb-4">
            <span class="sm:col-span-2"><span class="text-gray-400">場地　</span>{{ talk.venue }}</span>
            <span><span class="text-gray-400">主辦　</span>{{ talk.organizer }}</span>
            <span v-if="talk.course"><span class="text-gray-400">課程　</span>{{ talk.course }}</span>
          </div>
          <div class="flex flex-wrap gap-2 mt-5">
            <a v-if="talk.pptR2Key"
              :href="`/api/speech/ppt-download/${talk.id}`"
              class="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-medium transition"
            >📑 下載投影片 (PPTX)</a>
          </div>
        </div>
      </div>

      <!-- 逐字稿 -->
      <div class="max-w-3xl mx-auto px-6 py-10">
        <div v-if="pending" class="text-center text-gray-400 py-20 text-sm">載入逐字稿…</div>
        <div v-else-if="error" class="text-center text-red-400 py-20 text-sm">無法載入逐字稿</div>
        <article v-else class="bg-white rounded-2xl border border-gray-100 px-8 py-10 md:px-14">
          <template v-for="(b, i) in blocks" :key="i">
            <h2 v-if="b.type === 'h2'" class="text-base font-bold text-gray-900 mt-10 mb-3 pl-3 border-l-4 border-rose-300">{{ b.text }}</h2>
            <h3 v-else-if="b.type === 'h3'" class="text-sm font-semibold text-rose-700 mt-6 mb-2">{{ b.text }}</h3>
            <div v-else-if="b.type === 'speaker'" class="mt-4 mb-1 text-xs font-semibold text-rose-600">{{ b.text }}</div>
            <p v-else-if="b.type === 'note'" class="text-xs text-gray-400 italic my-2 text-center">{{ b.text }}</p>
            <p v-else class="text-sm leading-7 text-gray-800 mb-3 indent-[2em]">{{ b.text }}</p>
          </template>
        </article>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useSpeechStore } from '~/stores/speech'

const route = useRoute()
const store = useSpeechStore()
const talk = computed(() => store.talks.find(t => t.id === route.params.id))

useHead({ title: () => (talk.value ? `${talk.value.title} — 演講活動` : '演講活動') })

const { data, pending, error } = useFetch(
  () => `/content/speech/${route.params.id}.md`,
  { responseType: 'text' }
)

function formatDate(d: string) {
  const [y, m, day] = d.split('-')
  return `${y} 年 ${parseInt(m)} 月 ${parseInt(day)} 日`
}

type Block = { type: 'h2' | 'h3' | 'speaker' | 'note' | 'para'; text: string }

const blocks = computed((): Block[] => {
  if (!data.value) return []
  const result: Block[] = []
  for (const raw of (data.value as string).split('\n')) {
    const t = raw.trim()
    if (!t) continue
    if (t.startsWith('## ')) { result.push({ type: 'h2', text: t.slice(3).trim() }); continue }
    if (t.startsWith('### ')) { result.push({ type: 'h3', text: t.slice(4).trim() }); continue }
    if (/^（(休息|中斷|備註)/.test(t) || /^\(/.test(t)) { result.push({ type: 'note', text: t }); continue }
    // 「講者：」「提問A：」「提問：」「主持人：」
    const sp = t.match(/^(講者|主持人|提問[A-Z]?)：(.*)$/)
    if (sp) {
      result.push({ type: 'speaker', text: sp[1] })
      if (sp[2].trim()) result.push({ type: 'para', text: sp[2].trim() })
      continue
    }
    result.push({ type: 'para', text: t })
  }
  return result
})
</script>
