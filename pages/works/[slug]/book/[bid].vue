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
              <div v-for="(t, i) in toc" :key="i" class="mb-0.5">
                <div class="group flex items-center gap-0.5">
                  <button @click="scrollTo(t.id)"
                    :class="['flex-1 min-w-0 text-left px-2 py-1.5 rounded-lg text-xs leading-snug transition-colors truncate',
                             activeId === t.id ? 'bg-violet-100 text-violet-700 font-medium' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700']">
                    {{ t.title }}
                  </button>
                  <button v-if="speech.supported" @click="startSpeak(t.id)" :title="`朗讀整章「${t.title}」`"
                    :class="['flex-shrink-0 w-6 h-6 rounded-md grid place-items-center text-[13px] transition',
                             speech.readingId === t.id ? 'text-violet-600 opacity-100' : 'text-gray-400 opacity-0 group-hover:opacity-100 hover:text-violet-600 hover:bg-violet-50']">
                    <span v-if="speech.readingId === t.id" class="animate-pulse">🔊</span><span v-else>▶</span>
                  </button>
                </div>
                <!-- 小節：可單獨朗讀 -->
                <div v-for="s in (t.sections || [])" :key="s.id" class="group flex items-center gap-0.5 pl-2.5">
                  <button @click="scrollTo(s.id)"
                    :class="['flex-1 min-w-0 text-left px-2 py-1 rounded-lg text-[11px] leading-snug transition-colors truncate',
                             activeId === s.id ? 'bg-violet-50 text-violet-700 font-medium' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600']">
                    {{ s.title }}
                  </button>
                  <button v-if="speech.supported" @click="startSpeak(s.id)" :title="`只朗讀本節「${s.title}」`"
                    :class="['flex-shrink-0 w-6 h-6 rounded-md grid place-items-center text-[12px] transition',
                             speech.readingId === s.id ? 'text-violet-600 opacity-100' : 'text-gray-300 opacity-0 group-hover:opacity-100 hover:text-violet-600 hover:bg-violet-50']">
                    <span v-if="speech.readingId === s.id" class="animate-pulse">🔊</span><span v-else>▶</span>
                  </button>
                </div>
              </div>
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
            <!-- 朗讀控制列（Gemini 雲端 TTS ／ 裝置語音；分章／全文） -->
            <div v-if="speech.supported" class="mb-5 px-3 py-2 rounded-xl bg-white border border-gray-100">
              <div class="flex items-center flex-wrap gap-2">
                <button v-if="!speech.playing" @click="startSpeak()"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-600 text-white text-sm font-medium hover:bg-violet-700 transition">
                  <span>▶</span> 朗讀全文
                </button>
                <template v-else>
                  <button @click="togglePause"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-100 text-violet-700 text-sm font-medium hover:bg-violet-200 transition">
                    {{ speech.paused ? '▶ 繼續' : '⏸ 暫停' }}
                  </button>
                  <button @click="stopSpeak"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-100 text-gray-600 text-sm font-medium hover:bg-gray-200 transition">
                    ⏹ 停止
                  </button>
                  <span class="text-xs text-gray-500 min-w-0 truncate">
                    <span v-if="speech.loading" class="text-violet-500">生成語音中⋯</span>
                    <template v-else>正在朗讀：<span class="text-violet-600 font-medium">{{ readingTitle || '⋯' }}</span></template>
                  </span>
                </template>

                <!-- 引擎切換 -->
                <div class="ml-auto flex items-center gap-1 rounded-lg bg-gray-100 p-0.5 flex-shrink-0">
                  <button @click="speech.engine = 'gemini'"
                    :class="['px-2 py-1 rounded-md text-xs font-medium transition', speech.engine === 'gemini' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-500 hover:text-gray-700']">Gemini 雲端</button>
                  <button @click="speech.engine = 'device'" :disabled="!speech.deviceSupported"
                    :class="['px-2 py-1 rounded-md text-xs font-medium transition disabled:opacity-40', speech.engine === 'device' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-500 hover:text-gray-700']">裝置</button>
                </div>

                <!-- 音色：依引擎切換來源 -->
                <label v-if="speech.engine === 'gemini'" class="flex items-center gap-1.5 text-xs text-gray-500 flex-shrink-0">
                  <span class="hidden sm:inline">音色</span>
                  <select v-model="geminiVoice" class="px-1.5 py-1 border border-gray-200 rounded-md text-xs bg-white text-gray-700">
                    <option v-for="v in GEMINI_VOICES" :key="v.id" :value="v.id">{{ v.label }}</option>
                  </select>
                </label>
                <label v-else-if="zhVoices.length" class="flex items-center gap-1.5 text-xs text-gray-500 flex-shrink-0 min-w-0">
                  <span class="hidden sm:inline">語音</span>
                  <select v-model="voiceURI" class="px-1.5 py-1 border border-gray-200 rounded-md text-xs bg-white text-gray-700 max-w-[9rem] truncate">
                    <option v-for="v in zhVoices" :key="v.voiceURI" :value="v.voiceURI">{{ voiceLabel(v) }}</option>
                  </select>
                </label>

                <label class="flex items-center gap-1.5 text-xs text-gray-500 flex-shrink-0">
                  語速
                  <select v-model.number="speech.rate" class="px-1.5 py-1 border border-gray-200 rounded-md text-xs bg-white text-gray-700">
                    <option :value="0.75">0.75×</option>
                    <option :value="0.9">0.9×</option>
                    <option :value="1">1×</option>
                    <option :value="1.15">1.15×</option>
                    <option :value="1.3">1.3×</option>
                    <option :value="1.5">1.5×</option>
                  </select>
                </label>
              </div>
              <p v-if="speech.error" class="mt-1.5 text-xs text-amber-600">{{ speech.error }}</p>
              <p v-else-if="speech.engine === 'gemini'" class="mt-1.5 text-[11px] text-gray-400">Gemini 雲端音色最自然，但免費額度小、長讀易用盡；用盡時可改「裝置」引擎（免費不限量）。</p>
              <p v-else-if="speech.engine === 'device' && !currentVoiceIsNatural" class="mt-1.5 text-[11px] text-amber-600">目前是裝置內建的機械音。想要自然中文語音？用 <b>Microsoft Edge</b> 開啟本頁，上面「語音」選單會多出「HsiaoChen · 自然」等神經語音——免費、不限量、音質接近雲端。</p>
              <p v-else-if="speech.engine === 'device'" class="mt-1.5 text-[11px] text-gray-400">已選用神經語音（· 自然），免費不限量。</p>
            </div>

            <!-- mobile chapter jump -->
            <div class="lg:hidden mb-4">
              <select @change="scrollTo(($event.target as HTMLSelectElement).value)"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white">
                <option value="">跳至章節…</option>
                <option v-for="(t, i) in toc" :key="i" :value="t.id">{{ t.title }}</option>
              </select>
            </div>

            <article class="book-prose bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-12 sm:py-10"
              v-html="html" @mouseover="onCiteOver" @mouseout="onCiteOut" @click="onFableSwitch"></article>

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
const toc = ref<{ id: string; title: string; sections?: { id: string; title: string }[] }[]>([])
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

// Inject ids into <h2>/<h3> headings and build a nested table of contents.
// 章＝h2（ch-N），小節＝h3（sec-N-M，可單獨朗讀）；章末「本章摘要／論證分析圖」不列為可播小節。
function processHtml(raw: string): string {
  let nc = 0, ns = 0
  const chapters: { id: string; title: string; sections: { id: string; title: string }[] }[] = []
  const out = raw.replace(/<(h2|h3)([^>]*)>([\s\S]*?)<\/\1>/g, (_m, tag, attrs, inner) => {
    const title = inner.replace(/<[^>]+>/g, '').trim()
    if (tag === 'h2') {
      const id = `ch-${++nc}`; ns = 0
      chapters.push({ id, title, sections: [] })
      return `<h2 id="${id}"${attrs}>${inner}</h2>`
    }
    const id = `sec-${nc}-${++ns}`
    if (chapters.length && !/本章摘要|論證分析圖/.test(title)) {
      chapters[chapters.length - 1].sections.push({ id, title })
    }
    return `<h3 id="${id}"${attrs}>${inner}</h3>`
  })
  toc.value = chapters
  return out
}

function scrollTo(id: string) {
  if (!id) return
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// ── 章首故事多變體：預設顯示第一個，「換個故事」按鈕輪換 ────────────
// HTML 格式：.chapter-fable > .fable-variant[data-fable-title]（≥2 個才顯示按鈕；舊單一故事區塊不受影響）
function fableLabel(fable: Element): string {
  const vs = Array.from(fable.querySelectorAll('.fable-variant'))
  const i = vs.findIndex(v => v.classList.contains('active'))
  const title = (vs[i] as HTMLElement)?.dataset?.fableTitle || ''
  return `${title}（${i + 1}/${vs.length}）`
}

function initFables() {
  document.querySelectorAll('.book-prose .chapter-fable').forEach(fable => {
    const vs = fable.querySelectorAll('.fable-variant')
    if (vs.length < 2 || fable.querySelector('.fable-head')) return
    vs.forEach((v, i) => v.classList.toggle('active', i === 0))
    const head = document.createElement('div')
    head.className = 'fable-head'
    head.innerHTML = `<span class="fable-story-title"></span><button type="button" class="fable-switch">⇄ 換個故事</button>`
    fable.prepend(head)
    head.querySelector('.fable-story-title')!.textContent = fableLabel(fable)
  })
}

function onFableSwitch(e: MouseEvent) {
  const btn = (e.target as HTMLElement)?.closest?.('.fable-switch')
  if (!btn) return
  const fable = btn.closest('.chapter-fable')!
  const vs = Array.from(fable.querySelectorAll('.fable-variant'))
  const cur = vs.findIndex(v => v.classList.contains('active'))
  vs[cur]?.classList.remove('active')
  vs[(cur + 1) % vs.length].classList.add('active')
  fable.querySelector('.fable-story-title')!.textContent = fableLabel(fable)
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

// ── 朗讀（雙引擎：Gemini 雲端 TTS ／ 裝置原生 SpeechSynthesis） ──────
// 內容已用 <h2 id="ch-N"> 分章；逐章從已渲染的 DOM 抽純文字排隊播放，逐章高亮。
//   • device：SpeechSynthesis，切 ≤120 字短句（避開 Chrome ~15s 截斷 bug）。
//   • gemini：呼叫 /api/works/tts 逐段生成 WAV 播放，切 ~500 字並預抓下一段接續。
type Engine = 'gemini' | 'device'
const speech = reactive({
  supported: false, deviceSupported: false,
  playing: false, paused: false, loading: false,
  readingId: '', rate: 1, engine: 'gemini' as Engine, error: '',
})
const readingTitle = computed(() => {
  const flat = toc.value.flatMap(c => [{ id: c.id, title: c.title }, ...(c.sections ?? [])])
  return flat.find(t => t.id === speech.readingId)?.title ?? ''
})

// Gemini 預建音色（多語，會自動判讀中文）
const GEMINI_VOICES = [
  { id: 'Kore', label: 'Kore · 沉穩' }, { id: 'Aoede', label: 'Aoede · 輕柔' },
  { id: 'Leda', label: 'Leda · 年輕' }, { id: 'Charon', label: 'Charon · 知性' },
  { id: 'Zephyr', label: 'Zephyr · 明亮' }, { id: 'Puck', label: 'Puck · 活潑' },
  { id: 'Orus', label: 'Orus · 穩重' }, { id: 'Callirrhoe', label: 'Callirrhoe · 隨和' },
]
const geminiVoice = ref('Kore')

// 裝置端可選中文語音（優先神經／自然語音，避開舊款電子音）
const zhVoices = ref<SpeechSynthesisVoice[]>([])
const voiceURI = ref('')
const VOICE_KEY = 'works-reader-voice', GVOICE_KEY = 'works-reader-gvoice', ENGINE_KEY = 'works-reader-engine'

let queue: { chId: string; text: string }[] = []
let qi = 0
let keepAlive: ReturnType<typeof setInterval> | null = null
// gemini 播放狀態
let audioEl: HTMLAudioElement | null = null
const segCache = new Map<number, string>()          // 段索引 → objectURL
const segAborts = new Map<number, AbortController>() // 進行中的抓取，停止時中止
let playToken = 0                                     // 每次 start 遞增，作廢舊的非同步流程

// 語音品質評分：神經／線上（Natural/Online/Neural）＞ Google ＞ 台灣優先
function voiceScore(v: SpeechSynthesisVoice): number {
  const n = v.name.toLowerCase(), l = v.lang.toLowerCase()
  let s = 0
  if (/natural|neural|online/.test(n)) s += 40
  if (/premium|enhanced/.test(n)) s += 20
  if (/google/.test(n)) s += 12
  if (/hsiaochen|hsiaoyu|yating|zhiwei|hanhan/.test(n)) s += 4 // 有 Natural 版時仍會被上面加權超過
  if (l.startsWith('zh-tw')) s += 8
  else if (l.startsWith('zh-hk')) s += 4
  return s
}

function loadVoices() {
  const vs = window.speechSynthesis?.getVoices?.() ?? []
  zhVoices.value = vs.filter(v => /^zh/i.test(v.lang)).sort((a, b) => voiceScore(b) - voiceScore(a))
  if (!zhVoices.value.length) return
  const saved = (() => { try { return localStorage.getItem(VOICE_KEY) || '' } catch { return '' } })()
  if (saved && zhVoices.value.some(v => v.voiceURI === saved)) voiceURI.value = saved
  else if (!voiceURI.value || !zhVoices.value.some(v => v.voiceURI === voiceURI.value)) voiceURI.value = zhVoices.value[0].voiceURI
}

const currentVoice = computed(() => zhVoices.value.find(v => v.voiceURI === voiceURI.value) ?? null)
// 目前選用的裝置語音是否為神經／自然聲線（否＝老款電子音，提示改用 Edge 取得免費神經語音）
const currentVoiceIsNatural = computed(() => /natural|neural|online/i.test(currentVoice.value?.name || ''))
watch(voiceURI, (u) => { try { localStorage.setItem(VOICE_KEY, u) } catch {} })
watch(geminiVoice, (v) => { try { localStorage.setItem(GVOICE_KEY, v) } catch {} })
watch(() => speech.engine, (e) => { try { localStorage.setItem(ENGINE_KEY, e) } catch {}; stopSpeak() })
// 語速即時套用到 gemini 音檔（device 引擎則於下一句生效）
watch(() => speech.rate, (r) => { if (audioEl) audioEl.playbackRate = r })

// 精簡顯示名：去掉 "Microsoft "、括號語系尾綴，標「自然」
function voiceLabel(v: SpeechSynthesisVoice): string {
  let n = v.name.replace(/^Microsoft\s+/i, '').replace(/\s*-\s*Chinese.*$/i, '').replace(/\s*\(.*\)\s*$/, '').trim()
  const natural = /natural|neural|online/i.test(v.name) ? ' · 自然' : ''
  const region = v.lang.toLowerCase().startsWith('zh-tw') ? '台' : v.lang.toLowerCase().startsWith('zh-hk') ? '港' : v.lang.toLowerCase().startsWith('zh-cn') ? '陸' : ''
  return `${n}${region ? `（${region}）` : ''}${natural}`
}

// 逐章抽文字：走 .book-prose 直接子節點，遇 <h2> 換章；移除引用編號/論證符號/出處註腳等雜訊
function chapterTextMap(): { id: string; title: string; text: string }[] {
  const article = document.querySelector('.book-prose')
  if (!article) return []
  const res: { id: string; title: string; text: string }[] = []
  let cur: { id: string; title: string; parts: string[] } | null = null
  const flush = () => { if (cur && cur.parts.length) res.push({ id: cur.id, title: cur.title, text: cur.parts.join('\n') }) }
  for (const node of Array.from(article.children)) {
    const el = node as HTMLElement
    if (el.tagName === 'H2') {
      flush()
      const title = (el.textContent || '').trim()
      cur = { id: el.id || `ch-x`, title, parts: title ? [title] : [] }
      continue
    }
    if (!cur) cur = { id: 'ch-0', title: '', parts: [] }
    const c = el.cloneNode(true) as HTMLElement
    c.querySelectorAll('.cite-seq, .arg-op, .section-source, .chapter-source, .fable-head, .fable-variant:not(.active)').forEach(n => n.remove())
    const t = (c.textContent || '').replace(/[ \t]+/g, ' ').replace(/\n{2,}/g, '\n').trim()
    if (t) cur.parts.push(t)
  }
  flush()
  return res
}

// 抽單一小節文字：從該 <h3> 起，走同層兄弟到下一個 h3／h2／區塊（章末 recap section）為止；
// 略過出處註腳（.section-source／.chapter-source）與引用編號／論證符號。
function sectionTextById(secId: string): { id: string; title: string; text: string } {
  const h = document.getElementById(secId)
  if (!h) return { id: secId, title: '', text: '' }
  const title = (h.textContent || '').trim()
  const parts: string[] = title ? [title] : []
  const clean = (el: Element) => {
    const c = el.cloneNode(true) as HTMLElement
    c.querySelectorAll('.cite-seq, .arg-op, .section-source, .chapter-source, .fable-head, .fable-variant:not(.active)').forEach(n => n.remove())
    return (c.textContent || '').replace(/[ \t]+/g, ' ').replace(/\n{2,}/g, '\n').trim()
  }
  let node = h.nextElementSibling
  while (node && !['H2', 'H3', 'SECTION'].includes(node.tagName)) {
    if (!node.classList.contains('section-source') && !node.classList.contains('chapter-source')) {
      const t = clean(node); if (t) parts.push(t)
    }
    node = node.nextElementSibling
  }
  return { id: secId, title, text: parts.join('\n') }
}

// 依中文標點斷句後合併成 ≤max 字的段（device 短句避 15s bug；gemini 較長省請求）
function toChunks(text: string, chId: string, max: number): { chId: string; text: string }[] {
  const sents = text.split(/(?<=[。！？；\n])/).map(s => s.trim()).filter(Boolean)
  const out: { chId: string; text: string }[] = []
  let buf = ''
  for (const s of sents) {
    if (buf && (buf + s).length > max) { out.push({ chId, text: buf }); buf = s }
    else buf += s
  }
  if (buf) out.push({ chId, text: buf })
  return out
}

// 切到某段時：更新章節高亮並捲動
function markChapter(i: number) {
  const chunk = queue[i]
  if (chunk && chunk.chId !== speech.readingId) {
    speech.readingId = chunk.chId
    activeId.value = chunk.chId
    scrollTo(chunk.chId)
  }
}

// ── 引擎 A：裝置原生 SpeechSynthesis ──────────────────────────────
function speakNext() {
  const synth = window.speechSynthesis
  if (!synth || !speech.playing || qi >= queue.length) { stopSpeak(); return }
  markChapter(qi)
  const u = new SpeechSynthesisUtterance(queue[qi].text)
  u.lang = currentVoice.value?.lang || 'zh-TW'
  if (currentVoice.value) u.voice = currentVoice.value
  u.rate = speech.rate
  u.onend = () => { if (speech.playing && !speech.paused) { qi++; speakNext() } }
  u.onerror = () => { if (speech.playing) { qi++; speakNext() } }
  synth.speak(u)
}

// Chrome 長時間播放會自行暫停；定時 pause→resume 續命
function armKeepAlive() {
  if (keepAlive) clearInterval(keepAlive)
  keepAlive = setInterval(() => {
    const s = window.speechSynthesis
    if (s && speech.playing && !speech.paused) { s.pause(); s.resume() }
  }, 9000)
}

// ── 引擎 B：Gemini 雲端 TTS（逐段抓 WAV，預抓下一段） ──────────────
function sleep(ms: number, token: number) {
  return new Promise<void>((res, rej) => setTimeout(() => (token === playToken ? res() : rej(new Error('stale'))), ms))
}

// 抓某段音檔並快取為 objectURL。免費層偶爾 429/OTHER，retries>0 時退避重試
// （播放主路徑會重試以避免中斷；預抓則不重試，不跟主路徑搶額度）。
async function fetchSeg(i: number, token: number, retries = 0): Promise<string> {
  if (segCache.has(i)) return segCache.get(i)!
  let lastErr: any
  for (let a = 0; a <= retries; a++) {
    if (token !== playToken) throw new Error('stale')
    const ctrl = new AbortController()
    segAborts.set(i, ctrl)
    try {
      const buf = await $fetch<Blob>('/api/works/tts', {
        method: 'POST', responseType: 'blob', signal: ctrl.signal,
        body: { text: queue[i].text, voice: geminiVoice.value },
      })
      if (token !== playToken) throw new Error('stale')
      const url = URL.createObjectURL(buf)
      segCache.set(i, url)
      return url
    } catch (e: any) {
      lastErr = e
      if (e?.message === 'stale' || token !== playToken) throw e
      if (a < retries) await sleep(2500 + a * 2500, token) // 2.5s,5s,7.5s… 退避
    } finally { segAborts.delete(i) }
  }
  throw lastErr
}

async function playGeminiAt(i: number, token: number) {
  if (token !== playToken || !speech.playing) return
  if (i >= queue.length) { stopSpeak(); return }
  markChapter(i)
  let url: string
  try {
    if (!segCache.has(i)) speech.loading = true
    url = await fetchSeg(i, token, 4) // 主路徑退避重試，避免免費層瞬時 429/OTHER 中斷朗讀
  } catch (e: any) {
    if (token !== playToken) return
    if (e?.message !== 'stale') {
      const quota = e?.statusCode === 429 || e?.data?.data?.code === 'quota_exhausted'
      speech.error = quota
        ? 'Gemini 免費語音額度暫時用盡，稍後再試，或改用「裝置」引擎（免費不限量）。'
        : (e?.data?.message || 'Gemini 語音暫時無法生成，可改用「裝置」引擎。')
      stopSpeak()
    }
    return
  }
  if (token !== playToken || !speech.playing) return
  speech.loading = false
  if (!audioEl) return
  audioEl.src = url
  audioEl.playbackRate = speech.rate
  audioEl.play().catch(() => {})
  // 預抓下一段（不重試，不與主路徑搶額度），接續時就不用等
  if (i + 1 < queue.length && !segCache.has(i + 1)) fetchSeg(i + 1, token, 0).catch(() => {})
}

function onGeminiEnded() {
  if (speech.engine !== 'gemini' || !speech.playing || speech.paused) return
  qi++
  playGeminiAt(qi, playToken)
}

// ── 共用控制 ──────────────────────────────────────────────────────
// targetId：ch-N＝只念該章；sec-N-M＝只念該小節；空＝念全文
function startSpeak(targetId?: string) {
  stopSpeak()
  speech.error = ''
  const gemini = speech.engine === 'gemini'
  if (!gemini) {
    if (!window.speechSynthesis) return
    if (!zhVoices.value.length) loadVoices()
  }
  const max = gemini ? 500 : 120
  if (targetId && targetId.startsWith('sec-')) {
    const sec = sectionTextById(targetId)
    queue = toChunks(sec.text, targetId, max)
  } else {
    const chapters = chapterTextMap()
    const chosen = targetId ? chapters.filter(c => c.id === targetId) : chapters
    queue = chosen.flatMap(c => toChunks(c.text, c.id, max))
  }
  qi = 0
  if (!queue.length) return
  speech.playing = true; speech.paused = false; speech.readingId = ''
  const token = ++playToken
  if (gemini) playGeminiAt(0, token)
  else { armKeepAlive(); speakNext() }
}

function togglePause() {
  if (!speech.playing) return
  if (speech.engine === 'gemini') {
    if (speech.paused) { audioEl?.play().catch(() => {}); speech.paused = false }
    else { audioEl?.pause(); speech.paused = true }
  } else {
    const synth = window.speechSynthesis
    if (!synth) return
    if (speech.paused) { synth.resume(); speech.paused = false }
    else { synth.pause(); speech.paused = true }
  }
}

function stopSpeak() {
  playToken++            // 作廢所有進行中的 gemini 抓取／播放流程
  window.speechSynthesis?.cancel()
  if (audioEl) { audioEl.pause(); audioEl.removeAttribute('src'); audioEl.load() }
  for (const c of segAborts.values()) c.abort()
  segAborts.clear()
  for (const url of segCache.values()) URL.revokeObjectURL(url)
  segCache.clear()
  speech.playing = false; speech.paused = false; speech.loading = false; speech.readingId = ''
  queue = []; qi = 0
  if (keepAlive) { clearInterval(keepAlive); keepAlive = null }
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
onMounted(() => {
  load(); loadReview()
  if (typeof window !== 'undefined') {
    speech.supported = true // gemini 引擎只需 fetch + <audio>，一律可用
    speech.deviceSupported = 'speechSynthesis' in window
    // 還原偏好
    try {
      const e = localStorage.getItem(ENGINE_KEY) as Engine | null
      if (e === 'device' && speech.deviceSupported) speech.engine = 'device'
      else if (e === 'gemini' || e === 'device') speech.engine = 'gemini'
      const gv = localStorage.getItem(GVOICE_KEY)
      if (gv && GEMINI_VOICES.some(v => v.id === gv)) geminiVoice.value = gv
    } catch {}
    if (!speech.deviceSupported) speech.engine = 'gemini'
    // 準備 gemini 播放用的 <audio>
    audioEl = new Audio()
    audioEl.onended = onGeminiEnded
    audioEl.onerror = () => { if (speech.engine === 'gemini' && speech.playing) onGeminiEnded() }
    if (speech.deviceSupported) {
      loadVoices()
      window.speechSynthesis.onvoiceschanged = loadVoices
    }
  }
})
watch(() => bid.value, () => { stopSpeak(); tab.value = 'book'; load(); loadReview() })

// Highlight the chapter currently in view.
let observer: IntersectionObserver | null = null
watch(html, async () => {
  await nextTick()
  initFables()
  observer?.disconnect()
  observer = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) activeId.value = (e.target as HTMLElement).id
    }
  }, { rootMargin: '0px 0px -75% 0px' })
  document.querySelectorAll('.book-prose h2[id]').forEach(el => observer!.observe(el))
})
onBeforeUnmount(() => { observer?.disconnect(); stopSpeak() })
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
/* 章首故事引子 */
.book-prose :deep(.chapter-fable) { @apply mb-8 px-5 py-4 rounded-2xl bg-amber-50/50 border border-amber-100; }
.book-prose :deep(.chapter-fable p) { @apply text-[15px] leading-[2] text-gray-700 italic; }
.book-prose :deep(.chapter-fable p.fable-bridge) { @apply not-italic text-gray-800 border-t border-dashed border-amber-200 pt-3 mt-3 mb-0; }
/* 章首故事多變體：預設全隱、僅 .active 顯示；換故事按鈕列 */
.book-prose :deep(.chapter-fable .fable-variant) { @apply hidden; }
.book-prose :deep(.chapter-fable .fable-variant.active) { @apply block; }
.book-prose :deep(.fable-head) { @apply flex items-center justify-between gap-2 mb-3 pb-2 border-b border-dashed border-amber-200; }
.book-prose :deep(.fable-story-title) { @apply text-xs font-medium text-amber-700 truncate; }
.book-prose :deep(.fable-switch) { @apply flex-shrink-0 px-2.5 py-1 rounded-lg text-xs font-medium text-amber-700 bg-amber-100/70 hover:bg-amber-200/70 transition; }
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
