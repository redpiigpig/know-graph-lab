<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader :title="book?.title ?? '載入中…'" :back="{ to: `/works/${slug}`, label: '創生哲學' }" container-class="max-w-5xl">
      <template #actions>
        <span v-if="book" class="text-xs text-gray-400">{{ book.nChapters }} 章</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div v-if="pending" class="text-center text-gray-400 py-16 text-sm">載入中…</div>
      <div v-else-if="!book" class="text-center text-gray-400 py-24 text-sm">找不到這本書。</div>

      <template v-else>
        <div class="flex gap-8">
          <!-- TOC -->
          <aside class="w-48 flex-shrink-0 hidden lg:block">
            <div class="sticky top-4 space-y-0.5 max-h-[80vh] overflow-auto pr-1">
              <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-2 px-2">目錄</p>
              <button v-for="(t, i) in toc" :key="i" @click="scrollTo(t.id)"
                :class="['w-full text-left px-2 py-1.5 rounded-lg text-xs leading-snug transition-colors',
                         activeId === t.id ? 'bg-violet-100 text-violet-700 font-medium' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700']">
                {{ t.title }}
              </button>
            </div>
          </aside>

          <!-- content -->
          <div class="flex-1 min-w-0">
            <!-- mobile chapter jump -->
            <div class="lg:hidden mb-4">
              <select @change="scrollTo(($event.target as HTMLSelectElement).value)"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white">
                <option value="">跳至章節…</option>
                <option v-for="(t, i) in toc" :key="i" :value="t.id">{{ t.title }}</option>
              </select>
            </div>

            <article class="book-prose bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-12 sm:py-10" v-html="html"></article>

            <!-- prev / next book -->
            <div class="mt-8 flex items-center justify-between gap-3">
              <NuxtLink v-if="prevBook" :to="`/works/${slug}/book/${prevBook.id}`"
                class="text-sm text-violet-700 hover:underline no-underline">← {{ prevBook.title }}</NuxtLink>
              <span v-else></span>
              <NuxtLink v-if="nextBook" :to="`/works/${slug}/book/${nextBook.id}`"
                class="text-sm text-violet-700 hover:underline no-underline">{{ nextBook.title }} →</NuxtLink>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const slug = computed(() => String(route.params.slug))
const bid = computed(() => String(route.params.bid))

interface BookMeta { id: string; title: string; subtitle: string; file: string; nChapters: number }
interface BookGroup { branch: string; books: BookMeta[] }

const groups = ref<BookGroup[]>([])
const html = ref('')
const toc = ref<{ id: string; title: string }[]>([])
const activeId = ref('')
const pending = ref(true)

// The group containing the current book (prev/next stay within the same sub-series).
const curGroup = computed(() => groups.value.find(g => g.books.some(b => b.id === bid.value)) || null)
const book = computed(() => curGroup.value?.books.find(b => b.id === bid.value) || null)
const bookIdx = computed(() => curGroup.value?.books.findIndex(b => b.id === bid.value) ?? -1)
const prevBook = computed(() => curGroup.value && bookIdx.value > 0 ? curGroup.value.books[bookIdx.value - 1] : null)
const nextBook = computed(() => curGroup.value && bookIdx.value >= 0 && bookIdx.value < curGroup.value.books.length - 1 ? curGroup.value.books[bookIdx.value + 1] : null)

useHead(() => ({ title: book.value ? `${book.value.title} — 創生哲學` : '創生哲學' }))

// Inject ids into <h2> headings and build a table of contents from them.
function processHtml(raw: string): string {
  let n = 0
  const items: { id: string; title: string }[] = []
  const out = raw.replace(/<h2([^>]*)>([\s\S]*?)<\/h2>/g, (_m, attrs, inner) => {
    const id = `ch-${++n}`
    const title = inner.replace(/<[^>]+>/g, '').trim()
    items.push({ id, title })
    return `<h2 id="${id}"${attrs}>${inner}</h2>`
  })
  toc.value = items
  return out
}

function scrollTo(id: string) {
  if (!id) return
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function load() {
  pending.value = true
  try {
    const manifest = await $fetch<{ groups?: BookGroup[]; books?: BookMeta[] }>(`/content/works/${slug.value}-books.json`, { responseType: 'json' })
    groups.value = Array.isArray(manifest?.groups)
      ? manifest.groups
      : (Array.isArray(manifest?.books) ? [{ branch: '', books: manifest.books }] : [])
    const b = groups.value.flatMap(g => g.books).find(x => x.id === bid.value)
    if (b) {
      const raw = await $fetch<string>(b.file, { responseType: 'text' })
      html.value = processHtml(raw)
    } else {
      html.value = ''
    }
  } catch { html.value = '' } finally { pending.value = false }
}
onMounted(load)
watch(() => bid.value, load)

// Highlight the chapter currently in view.
let observer: IntersectionObserver | null = null
watch(html, async () => {
  await nextTick()
  observer?.disconnect()
  observer = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) activeId.value = (e.target as HTMLElement).id
    }
  }, { rootMargin: '0px 0px -75% 0px' })
  document.querySelectorAll('.book-prose h2[id]').forEach(el => observer!.observe(el))
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<style scoped>
.book-prose :deep(.book-head) { @apply mb-10 pb-8 border-b border-gray-100; }
.book-prose :deep(.book-kicker) { @apply text-xs text-violet-500 tracking-widest mb-2; }
.book-prose :deep(.book-title) { @apply text-3xl font-bold text-gray-900 mb-1; }
.book-prose :deep(.book-sub) { @apply text-base text-gray-500 mb-4; }
.book-prose :deep(.book-thesis) { @apply text-sm text-gray-600 leading-relaxed bg-violet-50/50 rounded-xl px-4 py-3; }
.book-prose :deep(.chapter) { @apply mb-12; }
.book-prose :deep(h2) { @apply text-2xl font-bold text-gray-900 mt-10 mb-5 scroll-mt-6; }
.book-prose :deep(h3) { @apply text-lg font-semibold text-gray-800 mt-7 mb-3; }
.book-prose :deep(p) { @apply text-[15px] leading-[1.95] text-gray-800 mb-4 tracking-wide; }
.book-prose :deep(blockquote) { @apply border-l-4 border-violet-200 pl-4 italic text-gray-600 my-5; }
.book-prose :deep(ul) { @apply list-disc pl-6 mb-4 space-y-1 text-[15px] leading-relaxed text-gray-800; }
.book-prose :deep(strong) { @apply font-semibold text-gray-900; }
/* 序／跋 */
.book-prose :deep(.vol-preface), .book-prose :deep(.vol-coda) { @apply mb-12 px-5 py-5 rounded-2xl bg-violet-50/40 border border-violet-100; }
.book-prose :deep(.vol-preface h2), .book-prose :deep(.vol-coda h2) { @apply text-xl text-violet-800 mt-0 mb-4; }
.book-prose :deep(.vol-preface p), .book-prose :deep(.vol-coda p) { @apply text-[15px] leading-[2] text-gray-700; }
/* 章末摘要與論證分析圖 */
.book-prose :deep(.chapter-recap) { @apply mt-8 pt-5 border-t border-dashed border-gray-200; }
.book-prose :deep(.chapter-recap h3) { @apply text-sm font-bold text-violet-600 uppercase tracking-widest mt-5 mb-2.5; }
.book-prose :deep(.recap-points) { @apply list-disc pl-6 space-y-1 text-[14px] text-gray-700; }
.book-prose :deep(.argmap) { @apply flex flex-col items-stretch gap-1.5 my-3 max-w-xl; }
.book-prose :deep(.arg-premise) { @apply text-[13px] leading-relaxed text-gray-700 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2; }
.book-prose :deep(.arg-step) { @apply text-[13px] leading-relaxed text-violet-800 bg-violet-50 border border-violet-200 rounded-lg px-3 py-2; }
.book-prose :deep(.arg-conclusion) { @apply text-[13px] leading-relaxed font-medium text-emerald-900 bg-emerald-50 border border-emerald-300 rounded-lg px-3 py-2; }
.book-prose :deep(.arg-op) { @apply text-center text-gray-400 text-xs leading-none; }
</style>
