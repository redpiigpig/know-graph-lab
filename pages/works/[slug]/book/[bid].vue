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
            <!-- 本文 / 研究回顧 分頁 -->
            <div class="flex items-center gap-1 border-b border-gray-200 mb-6">
              <button @click="tab = 'book'"
                class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition"
                :class="tab === 'book' ? 'border-violet-500 text-violet-700' : 'border-transparent text-gray-500 hover:text-gray-800'">本文</button>
              <button @click="tab = 'review'"
                class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition"
                :class="tab === 'review' ? 'border-violet-500 text-violet-700' : 'border-transparent text-gray-500 hover:text-gray-800'">
                研究回顧<span v-if="litEntries.length" class="ml-1 text-xs" :class="tab === 'review' ? 'text-violet-500' : 'text-gray-400'">{{ litEntries.length }}</span>
              </button>
            </div>

            <div v-show="tab === 'book'">
            <!-- mobile chapter jump -->
            <div class="lg:hidden mb-4">
              <select @change="scrollTo(($event.target as HTMLSelectElement).value)"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white">
                <option value="">跳至章節…</option>
                <option v-for="(t, i) in toc" :key="i" :value="t.id">{{ t.title }}</option>
              </select>
            </div>

            <article class="book-prose bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-12 sm:py-10"
              v-html="html" @mouseover="onCiteOver" @mouseout="onCiteOut"></article>

            <!-- prev / next book -->
            <div class="mt-8 flex items-center justify-between gap-3">
              <NuxtLink v-if="prevBook" :to="`/works/${slug}/book/${prevBook.id}`"
                class="text-sm text-violet-700 hover:underline no-underline">← {{ prevBook.title }}</NuxtLink>
              <span v-else></span>
              <NuxtLink v-if="nextBook" :to="`/works/${slug}/book/${nextBook.id}`"
                class="text-sm text-violet-700 hover:underline no-underline">{{ nextBook.title }} →</NuxtLink>
            </div>
            </div>

            <!-- 研究回顧（本卷參考資料庫） -->
            <div v-show="tab === 'review'">
              <div class="mb-5">
                <h2 class="text-base font-semibold text-gray-900">研究回顧</h2>
                <p class="text-xs text-gray-500 mt-0.5">
                  參考資料庫 · 共 {{ litEntries.length }} 筆 · 依四領域分組（自然科學／心理學／哲學／宗教與神話）· 改寫本卷的依據
                </p>
              </div>
              <div v-if="litLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
              <div v-else-if="!litEntries.length" class="text-gray-400 text-sm py-12 text-center">本卷尚無研究回顧。</div>
              <div v-else class="space-y-8">
                <section v-for="grp in litGroups" :key="grp.theme">
                  <h3 class="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">{{ grp.theme }}<span class="ml-2 text-gray-300 normal-case">{{ grp.items.length }}</span></h3>
                  <div class="space-y-3">
                    <div v-for="e in grp.items" :key="e.id" class="bg-white rounded-2xl border border-gray-100 p-5">
                      <div class="flex flex-wrap items-center gap-1.5 mb-2">
                        <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ langLabel(e.language) }}</span>
                        <span v-if="e.dimension" class="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 break-words">{{ e.dimension }}</span>
                        <span v-if="e.stance" class="text-xs font-medium px-2 py-0.5 rounded-full break-words"
                          :class="e.stance === '反例' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-700'">立場：{{ e.stance }}</span>
                      </div>
                      <h4 class="text-sm font-semibold text-gray-900 leading-snug mb-1 break-words">
                        {{ e.authors }}<span v-if="e.year">（{{ e.year }}）</span>　{{ e.title }}
                      </h4>
                      <p v-if="e.venue" class="text-xs text-gray-500 mb-2 break-words">{{ e.venue }}</p>
                      <p v-if="e.abstract_zh" class="text-sm text-gray-700 leading-relaxed break-words">{{ e.abstract_zh }}</p>
                      <div class="mt-2 flex flex-wrap items-center gap-3 text-xs">
                        <NuxtLink v-if="e.has_fulltext" :to="`/works/${slug}/review/${e.ref_key}`"
                          class="text-violet-700 hover:underline font-medium">閱讀全文（原文／中譯）→</NuxtLink>
                        <a v-else-if="e.fulltext_url" :href="e.fulltext_url" target="_blank" rel="noopener"
                          class="text-blue-600 hover:underline break-all">原始連結 ↗</a>
                        <span v-else class="text-gray-300 italic">無線上全文</span>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 引用 hover 預覽浮窗 -->
    <Teleport to="body">
      <div v-if="preview.visible" class="cite-pop" :style="{ top: preview.top + 'px', left: preview.left + 'px' }"
        @mouseenter="cancelHide" @mouseleave="hidePreview">
        <div class="cite-pop-head">
          <span class="cite-pop-label">{{ preview.label }}</span>
          <span v-if="preview.date" class="cite-pop-date">{{ preview.date }}</span>
        </div>
        <div v-if="preview.loading" class="cite-pop-loading">載入中…</div>
        <div v-else-if="preview.error" class="cite-pop-error">{{ preview.error }}</div>
        <template v-else>
          <p v-if="preview.title" class="cite-pop-title">{{ preview.title }}</p>
          <p v-if="preview.prompt" class="cite-pop-q"><span class="cite-pop-tag">問</span>{{ preview.prompt }}</p>
          <p v-if="preview.response" class="cite-pop-a"><span class="cite-pop-tag">答</span>{{ preview.response }}</p>
        </template>
      </div>
    </Teleport>
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

// 本文 / 研究回顧（本卷參考資料庫，依四領域分組）分頁
interface LitEntry {
  id: number; ref_key: string; authors: string; year: number | null; title: string
  venue: string | null; language: string | null; theme: string | null; dimension: string | null
  stance: string | null; abstract_zh: string | null; fulltext_url: string | null; has_fulltext: boolean
}
const tab = ref<'book' | 'review'>('book')
const litEntries = ref<LitEntry[]>([])
const litLoading = ref(false)
const LANG_LABELS: Record<string, string> = { en: '英文', zh: '中文', de: '德文', fr: '法文', ja: '日文', la: '拉丁文', grc: '希臘文', es: '西班牙文', it: '義大利文' }
function langLabel(c: string | null) { return LANG_LABELS[c ?? ''] ?? (c || '—') }
const litGroups = computed(() => {
  const g: { theme: string; items: LitEntry[] }[] = []
  for (const e of litEntries.value) {
    const t = e.theme ?? ''
    let x = g.find(y => y.theme === t)
    if (!x) { x = { theme: t, items: [] }; g.push(x) }
    x.items.push(e)
  }
  return g
})
async function loadReview() {
  litLoading.value = true
  try {
    const d = await $fetch<{ entries: LitEntry[] }>('/api/lit-review/entries', { query: { slug: slug.value, bookId: bid.value } })
    litEntries.value = d.entries ?? []
  } catch { litEntries.value = [] } finally { litLoading.value = false }
}

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

// ── 引用 hover 預覽 ───────────────────────────────────────────────
// by-seq 端點需登入；本頁公開，故未登入時優雅提示。結果快取避免重抓。
const supabase = useSupabaseClient()
const preview = reactive({
  visible: false, loading: false, error: '', label: '',
  date: '', title: '', prompt: '', response: '', top: 0, left: 0,
})
const cite_cache = new Map<string, any>()
let hideTimer: ReturnType<typeof setTimeout> | null = null
let reqToken = 0

function clamp(s: string | null | undefined, n: number) {
  const t = (s ?? '').trim()
  return t.length > n ? t.slice(0, n) + '…' : t
}

function placePopup(rect: DOMRect) {
  const W = 360, margin = 12
  let left = rect.left + window.scrollX
  if (left + W > window.scrollX + window.innerWidth - margin)
    left = window.scrollX + window.innerWidth - W - margin
  preview.left = Math.max(window.scrollX + margin, left)
  preview.top = rect.bottom + window.scrollY + 6
}

async function onCiteOver(e: MouseEvent) {
  const a = (e.target as HTMLElement)?.closest?.('.cite-seq') as HTMLElement | null
  if (!a) return
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null }
  const label = (a.textContent || '').trim()
  if (!label) return
  placePopup(a.getBoundingClientRect())
  preview.label = label
  preview.visible = true
  preview.error = ''
  const my = ++reqToken

  if (cite_cache.has(label)) { Object.assign(preview, cite_cache.get(label), { visible: true, loading: false, error: '' }); return }

  preview.loading = true
  preview.title = preview.prompt = preview.response = preview.date = ''
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) {
      if (my === reqToken) { preview.loading = false; preview.error = '登入後可預覽對話內容' }
      return
    }
    const d: any = await $fetch('/api/ai-dialogues/by-seq', {
      query: { seq: label }, headers: { Authorization: `Bearer ${session.access_token}` },
    })
    const payload = {
      date: d.dialogue_date || '', title: clamp(d.title, 60),
      prompt: clamp(d.prompt, 160), response: clamp(d.response, 320),
    }
    cite_cache.set(label, payload)
    if (my === reqToken) Object.assign(preview, payload, { loading: false })
  } catch (err: any) {
    if (my === reqToken) { preview.loading = false; preview.error = err?.data?.message || '查閱失敗' }
  }
}

function onCiteOut(e: MouseEvent) {
  const a = (e.target as HTMLElement)?.closest?.('.cite-seq')
  if (!a) return
  hidePreview()
}
function hidePreview() { hideTimer = setTimeout(() => { preview.visible = false }, 180) }
function cancelHide() { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null } }

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
onMounted(() => { load(); loadReview() })
watch(() => bid.value, () => { tab.value = 'book'; load(); loadReview() })

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
/* 每節／章末對話編號引用（intro_schedule §6） */
.book-prose :deep(.section-source) { @apply mt-3 mb-6 text-[12px] leading-relaxed text-gray-400 border-l-2 border-violet-100 pl-3; }
.book-prose :deep(.chapter-source) { @apply mt-6 pt-3 border-l-0 border-t border-dashed border-violet-100 text-gray-500; }
/* 引用編號＝可點擊連結，連到 /ai-dialogues 編號查閱 */
.book-prose :deep(.cite-seq) { @apply font-mono text-violet-500/80 no-underline rounded px-0.5 transition-colors; }
.book-prose :deep(.cite-seq:hover) { @apply text-violet-700 underline bg-violet-50; }
</style>

<style scoped>
/* 引用 hover 預覽浮窗（Teleport 到 body，故不放 scoped book-prose 內） */
.cite-pop {
  @apply fixed z-50 w-[360px] max-w-[calc(100vw-24px)] rounded-xl border border-violet-100 bg-white shadow-xl shadow-violet-100/50 px-4 py-3 text-left;
}
.cite-pop-head { @apply flex items-center justify-between mb-1.5; }
.cite-pop-label { @apply font-mono text-xs font-semibold text-violet-600; }
.cite-pop-date { @apply text-[11px] text-gray-400; }
.cite-pop-loading { @apply text-xs text-gray-400 py-1; }
.cite-pop-error { @apply text-xs text-amber-600 py-1; }
.cite-pop-title { @apply text-sm font-semibold text-gray-800 mb-1.5 leading-snug; }
.cite-pop-q, .cite-pop-a { @apply text-[12.5px] leading-relaxed text-gray-600 mb-1.5; }
.cite-pop-a { @apply text-gray-700; }
.cite-pop-tag { @apply inline-block mr-1.5 px-1 rounded text-[10px] font-medium align-[1px]; }
.cite-pop-q .cite-pop-tag { @apply bg-gray-100 text-gray-500; }
.cite-pop-a .cite-pop-tag { @apply bg-violet-100 text-violet-600; }
</style>
