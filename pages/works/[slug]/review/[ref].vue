<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink :to="`/works/${slug}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ entry?.title || '研究回顧' }}</span>
      <span v-if="entry" class="text-xs text-gray-400 truncate hidden md:inline">{{ entry.authors }}<span v-if="entry.year"> ({{ entry.year }})</span></span>
      <div v-if="totalPages > 1" class="ml-auto flex items-center gap-2 text-xs">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30">‹</button>
        <span class="text-gray-500 tabular-nums">{{ currentPage }} / {{ totalPages }}</span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-stone-400 disabled:opacity-30">›</button>
      </div>
    </nav>

    <div class="flex-1 overflow-y-auto">
      <div class="max-w-5xl w-full mx-auto px-4 py-6">
        <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
        <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

        <template v-else-if="entry">
          <header v-if="currentPage === 1" class="mb-6 pb-4 border-b border-gray-200">
            <h1 class="text-xl font-bold text-gray-900 leading-snug">
              {{ entry.authors }}<span v-if="entry.year"> （{{ entry.year }}）</span>
            </h1>
            <p class="text-base text-gray-800 mt-1">{{ entry.title }}</p>
            <div class="flex flex-wrap items-center gap-2 mt-3 text-xs">
              <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ langLabel(entry.language) }}</span>
              <span v-if="entry.venue" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">{{ entry.venue }}</span>
              <span v-if="entry.dimension" class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-600">{{ entry.dimension }}</span>
              <span v-if="entry.stance" class="px-2 py-0.5 rounded bg-rose-50 text-rose-600">立場：{{ entry.stance }}</span>
              <a v-if="entry.fulltext_url" :href="entry.fulltext_url" target="_blank" rel="noopener"
                class="px-2 py-0.5 rounded bg-blue-50 text-blue-600 hover:underline">原始全文 ↗</a>
            </div>
            <p v-if="entry.abstract_zh" class="mt-3 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3">{{ entry.abstract_zh }}</p>
          </header>

          <div v-if="sections.length === 0" class="text-center text-gray-400 py-16 text-sm">
            此文獻尚未抓取全文逐段對照（全文翻譯排程中）。
            <div v-if="entry.fulltext_url" class="mt-3">
              <a :href="entry.fulltext_url" target="_blank" rel="noopener" class="text-blue-600 hover:underline">前往原始全文 ↗</a>
            </div>
          </div>

          <template v-else>
            <!-- column headers -->
            <div class="grid grid-cols-2 gap-px bg-gray-100 rounded-t-md overflow-hidden mb-px sticky top-12 z-10">
              <div class="bg-stone-50 px-4 py-1.5 text-[11px] font-semibold text-stone-600">逐段中譯</div>
              <div class="bg-stone-50 px-4 py-1.5 text-[11px] font-semibold text-stone-600">{{ langLabel(entry.language) }}原文</div>
            </div>

            <div class="space-y-2">
              <article v-for="s in pagedSections" :key="s.order_index"
                class="bg-white border border-gray-200 rounded-md overflow-hidden">
                <div class="grid grid-cols-2 gap-px bg-gray-100">
                  <div class="bg-white px-4 py-3 text-[15px] leading-7 text-gray-900 whitespace-pre-line">
                    <template v-if="s.byVersion.zh">{{ s.byVersion.zh }}</template>
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                  <div class="bg-white px-4 py-3 text-[14px] leading-7 text-gray-700 whitespace-pre-line">
                    <template v-if="s.byVersion.orig">{{ s.byVersion.orig }}</template>
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                </div>
              </article>
            </div>

            <div class="mt-8 flex items-center justify-between">
              <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">← 上一頁</button>
              <span class="text-sm text-gray-500">第 {{ currentPage }} / {{ totalPages }} 頁</span>
              <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages"
                class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-stone-400 disabled:opacity-30">下一頁 →</button>
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const slug = computed(() => String(route.params.slug))
const ref_key = computed(() => String(route.params.ref))
const currentPage = computed(() => Math.max(1, Number(route.query.page) || 1))
const PAGE_SIZE = 12

interface Entry {
  id: number; ref_key: string; authors: string; year: number | null; title: string
  venue: string | null; language: string | null; theme: string | null
  dimension: string | null; stance: string | null; abstract_zh: string | null
  fulltext_url: string | null; fulltext_status: string
}
interface Section { order_index: number; byVersion: Record<string, string> }

const LANG_LABELS: Record<string, string> = {
  en: '英文', zh: '中文', de: '德文', fr: '法文', ja: '日文',
  la: '拉丁文', grc: '希臘文', es: '西班牙文', it: '義大利文', other: '其他',
}
function langLabel(code: string | null) {
  return LANG_LABELS[code ?? ''] ?? (code || '')
}

const { data, pending, error } = await useFetch<{ entry: Entry; sections: Section[] }>(
  '/api/lit-review/entry',
  { query: { slug, ref: ref_key } }
)
const entry = computed(() => data.value?.entry ?? null)
const sections = computed(() => data.value?.sections ?? [])

useHead({ title: () => entry.value ? `${entry.value.title} — 研究回顧` : '研究回顧' })

const totalPages = computed(() => Math.max(1, Math.ceil(sections.value.length / PAGE_SIZE)))
const pagedSections = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return sections.value.slice(start, start + PAGE_SIZE)
})
function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push(`/works/${slug.value}/review/${ref_key.value}?page=${p}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}
</script>
