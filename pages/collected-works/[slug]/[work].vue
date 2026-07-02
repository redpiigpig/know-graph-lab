<template>
  <div class="min-h-screen bg-stone-50 text-stone-900 flex flex-col">
    <!-- Topbar -->
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink :to="`/collected-works/${slug}`" class="text-stone-500 hover:text-stone-900 text-sm transition flex-shrink-0">← {{ author?.name ?? '全集' }}</NuxtLink>
          <span class="text-stone-300">·</span>
          <button @click="tocOpen = !tocOpen"
            :class="['flex items-center gap-1 px-2 py-1 rounded-md text-xs transition border flex-shrink-0',
              tocOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400']"
            title="目錄"><span>📑</span><span class="hidden sm:inline">目錄</span></button>
          <span class="text-sm font-medium text-stone-900 truncate">{{ work?.title ?? data?.title }}</span>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <!-- view toggle -->
          <div v-if="sourceOrder.length" class="hidden sm:flex items-center gap-0.5 mr-1">
            <button v-for="m in viewButtons" :key="m.mode" @click="setView(m.mode)"
              :class="['px-2 py-1 rounded text-xs transition', view === m.mode ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-600 hover:bg-stone-200']">{{ m.label }}</button>
          </div>
          <button @click="goPage(page - 1)" :disabled="page <= 1"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">‹</button>
          <input v-model.number="jump" @keyup.enter="goPage(jump)" type="number" :min="1" :max="totalPages"
            class="w-14 bg-white border border-stone-200 rounded-lg px-2 py-1 text-center text-sm focus:outline-none focus:border-blue-500" />
          <span class="text-xs text-stone-400">/ {{ totalPages }}</span>
          <button @click="goPage(page + 1)" :disabled="page >= totalPages"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">›</button>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 min-h-0">
      <!-- TOC drawer -->
      <aside v-if="tocOpen" class="w-72 flex-shrink-0 border-r border-stone-200 bg-white overflow-y-auto max-h-[calc(100vh-3.5rem)] sticky top-14">
        <div class="p-3">
          <div v-for="grp in tocGroups" :key="grp.label" class="mb-3">
            <div v-if="grp.label" class="text-[11px] font-semibold text-stone-500 px-2 py-1 uppercase tracking-wider">{{ grp.label }}</div>
            <button v-for="e in grp.items" :key="e.page" @click="goPage(e.page); tocOpen = false"
              :class="['block w-full text-left px-2 py-1.5 rounded text-xs transition truncate',
                e.page === page ? 'bg-blue-50 text-blue-700 font-medium' : 'text-stone-600 hover:bg-stone-100']">
              {{ e.short }}
            </button>
          </div>
        </div>
      </aside>

      <!-- Reader body -->
      <main class="flex-1 min-w-0 overflow-x-hidden">
        <div class="max-w-6xl mx-auto px-4 py-8">
          <div v-if="pending" class="text-center text-stone-400 py-24 text-sm">載入中…</div>

          <template v-else>
            <!-- ── 導讀卡：每卷最上面（page 1，含導讀） ── -->
            <div v-if="page === 1" class="max-w-2xl mx-auto mb-10">
              <div class="text-center mb-6">
                <div class="text-4xl mb-3">{{ author?.emoji ?? '📖' }}</div>
                <h1 class="text-2xl font-bold text-stone-900">{{ work?.title ?? data?.title }}</h1>
                <p v-if="work?.titleOriginal" class="text-sm text-stone-400 italic mt-1">{{ work.titleOriginal }}</p>
                <p class="text-sm text-stone-500 mt-1">{{ author?.name }}<span v-if="author?.nameEn" class="text-stone-400"> · {{ author.nameEn }}</span></p>
              </div>
              <div v-if="intro" class="bg-white rounded-2xl border border-stone-200 shadow-sm p-6 space-y-3">
                <div class="text-xs font-semibold text-amber-700 uppercase tracking-widest mb-1">簡介與導讀</div>
                <p v-for="(p, i) in intro.intro" :key="i" class="text-[0.95rem] leading-relaxed text-stone-700" v-html="md(p)"></p>
                <p v-if="intro.cite" class="text-xs text-stone-500 border-t border-stone-100 pt-3 mt-3">
                  <span class="font-medium">引用格式：</span><span v-html="md(intro.cite)"></span>
                </p>
              </div>
              <div v-else-if="work?.note" class="bg-white rounded-2xl border border-stone-200 shadow-sm p-6">
                <p class="text-sm leading-relaxed text-stone-600">{{ work.note }}</p>
              </div>
              <div v-if="isCover" class="text-center mt-6">
                <button @click="goPage(2)" class="px-5 py-2.5 rounded-xl bg-stone-900 text-white text-sm hover:bg-stone-700 transition">開始閱讀 →</button>
              </div>
            </div>

            <!-- ── 三欄逐段（引用號 + 繁中 + 原文欄…）；封面 chunk 不出 body ── -->
            <template v-if="!isCover">
              <!-- ── 三欄逐段 ── -->
            <div class="mb-4 flex items-baseline gap-2">
              <h2 class="text-base font-semibold text-stone-800">{{ cp.title }}</h2>
              <span v-if="cp.sub" class="text-xs text-stone-400">{{ cp.sub }}</span>
            </div>
            <!-- column headers -->
            <div class="grid gap-px mb-1 sticky top-14 z-10" :style="{ gridTemplateColumns: gridCols }">
              <div class="text-[10px] text-stone-400 uppercase text-center py-1">#</div>
              <div v-for="c in cols" :key="c.key" class="text-[11px] font-semibold text-stone-500 uppercase tracking-wider px-3 py-1 bg-stone-50/80 backdrop-blur">{{ c.label }}</div>
            </div>
            <div class="space-y-1.5">
              <template v-for="(row, i) in rows" :key="i">
                <!-- heading row (## …) spans all text columns -->
                <div v-if="row.heading" class="bg-gradient-to-r from-amber-50 to-white border-y border-amber-100 px-3 py-2 text-sm font-semibold text-stone-800">
                  {{ row.heading }}
                </div>
                <article v-else class="bg-white border border-stone-200 rounded-md overflow-hidden">
                  <div class="grid gap-px bg-stone-100" :style="{ gridTemplateColumns: gridCols }">
                    <button
                      class="bg-stone-50 px-1 py-3 text-[11px] font-mono font-bold text-stone-500 hover:text-blue-700 hover:bg-blue-50 flex items-start justify-center transition"
                      :title="citeTitle(row.anchor)" @click="copyCite(row.anchor)">{{ row.anchor }}</button>
                    <div v-for="c in cols" :key="c.key"
                      class="bg-white px-3 py-3 text-[0.92rem] leading-loose text-stone-800"
                      :class="c.key === 'grc' ? 'font-[Gentium,serif]' : ''"
                      :lang="c.key === 'zh' ? 'zh-Hant' : c.key"
                      style="font-family: 'Noto Serif TC', 'Source Han Serif TC', serif">
                      <span v-if="cell(row, c.key)" v-html="md(cell(row, c.key))"></span>
                      <span v-else class="text-stone-300 text-xs">—</span>
                    </div>
                  </div>
                </article>
              </template>
            </div>

            <!-- footer nav -->
            <div class="flex items-center justify-between mt-8">
              <button @click="goPage(page - 1)" :disabled="page <= 1" class="px-4 py-2 rounded-lg bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 text-sm transition">← 上一頁</button>
              <span class="text-xs text-stone-400">{{ cp.title }}</span>
              <button @click="goPage(page + 1)" :disabled="page >= totalPages" class="px-4 py-2 rounded-lg bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 text-sm transition">下一頁 →</button>
            </div>
            </template>
          </template>
        </div>
      </main>
    </div>
    <div v-if="copied" class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-stone-900 text-white text-xs px-4 py-2 rounded-full shadow-lg z-50">已複製引用</div>
  </div>
</template>

<script setup lang="ts">
import { normalizeSources, zipParallel, langLabel } from '~/lib/multilang-sources'
import { collectedWorksIntros } from '~/data/collectedWorksIntros'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const slug = route.params.slug as string
const ebookId = route.params.work as string

const store = useCollectedWorksStore()
const author = computed(() => store.bySlug(slug))
const work = computed(() => author.value?.works.find((w) => w.ebookId === ebookId))
const intro = computed(() => collectedWorksIntros[ebookId])

const page = ref(Math.max(1, Number(route.query.p) || 1))
const jump = ref(page.value)

const { data, pending, refresh } = await useAsyncData(
  () => `cw-${ebookId}-${page.value}`,
  () => $fetch<any>(`/api/ebooks/${ebookId}?includeToc=1&page=${page.value}`),
  { watch: [page] }
)

const totalPages = computed(() => data.value?.total_pages ?? 1)
const cur = computed(() => data.value?.currentPage ?? null)
const isCover = computed(() => cur.value?.chunk_type === 'cover')

useHead(() => ({ title: work.value ? `${work.value.title} — ${author.value?.name ?? '全集'}` : '全集' }))

function goPage(n: number) {
  const p = Math.min(Math.max(1, Math.floor(n || 1)), totalPages.value)
  page.value = p
  jump.value = p
  if (import.meta.client) {
    navigateTo({ query: { ...route.query, p: p } }, { replace: true })
    window.scrollTo({ top: 0 })
  }
}
watch(page, (p) => (jump.value = p))

// ── sources / view mode ──
const norm = computed(() => normalizeSources(cur.value ?? {}))
const sourceOrder = computed(() => norm.value.source_order)
const view = ref<string>('parallel')
function setView(m: string) { view.value = m }
const viewButtons = computed(() => [
  { mode: 'zh', label: '中' },
  { mode: 'parallel', label: '對照' },
  ...sourceOrder.value.map((l) => ({ mode: `src:${l}`, label: langLabel(l) })),
])
// columns for current view
const cols = computed<{ key: string; label: string }[]>(() => {
  if (!sourceOrder.value.length) return [{ key: 'zh', label: '中' }]
  if (view.value === 'zh') return [{ key: 'zh', label: '中' }]
  if (view.value.startsWith('src:')) {
    const l = view.value.slice(4)
    return [{ key: l, label: langLabel(l) }]
  }
  return [{ key: 'zh', label: '繁中' }, ...sourceOrder.value.map((l) => ({ key: l, label: langLabel(l) }))]
})
const gridCols = computed(() => `3.25rem ${cols.value.map(() => '1fr').join(' ')}`)

// ── rows ──
const SPLIT = /\n\s*\n/
function paras(s: string | null | undefined): string[] {
  return (s ?? '').split(SPLIT).map((p) => p.trim()).filter(Boolean)
}
const rows = computed(() => {
  const c = cur.value
  if (!c) return [] as any[]
  const zh = paras(c.content)
  const srcParas: Record<string, string[]> = {}
  for (const l of sourceOrder.value) srcParas[l] = paras(c.sources?.[l])
  const zipped = zipParallel(zh, srcParas, sourceOrder.value)
  const anchors: string[] = c.anchors ?? []
  return zipped.map((r, i) => {
    const zhText = r.zh
    const heading = /^#{1,4}\s+/.test(zhText) ? zhText.replace(/^#{1,4}\s+/, '') : null
    return {
      heading,
      zh: zhText,
      cols: r.cols,
      anchor: anchors[i] ?? (i === 0 && c.page_number != null ? String(c.page_number) : ''),
    }
  })
})
function cell(row: any, key: string): string {
  return key === 'zh' ? row.zh : (row.cols?.[key] ?? '')
}

// chapter path split for header
const cp = computed(() => {
  const raw = cur.value?.chapter_path ?? ''
  const parts = raw.split(' · ')
  return { title: parts.slice(0, 2).join(' · ') || raw, sub: parts.slice(2).join(' · ') }
})

// ── TOC ──
const tocOpen = ref(false)
const tocGroups = computed(() => {
  const toc: any[] = data.value?.toc ?? []
  const groups: { label: string; items: any[] }[] = []
  const byVol = new Map<string, any[]>()
  const order: string[] = []
  for (const e of toc) {
    if (e.chunk_type === 'cover') continue
    const vol = e.volume ?? ''
    if (!byVol.has(vol)) { byVol.set(vol, []); order.push(vol) }
    const label = (e.chapter_path ?? '').split(' · ').slice(-1)[0] || `頁 ${e.page ?? e.page_number}`
    byVol.get(vol)!.push({ page: e.page ?? (e.chunk_index != null ? e.chunk_index + 1 : 1), short: label })
  }
  for (const v of order) groups.push({ label: v, items: byVol.get(v)! })
  return groups
})

// ── citation copy ──
const copied = ref(false)
function citeTitle(a: string) {
  return a ? `複製引用：${author.value?.nameEn ?? author.value?.name ?? ''} · ${work.value?.title ?? ''} ${a}` : ''
}
async function copyCite(a: string) {
  if (!a || !import.meta.client) return
  const cite = `${author.value?.name ?? ''}《${work.value?.title ?? ''}》${a}`
  try {
    await navigator.clipboard.writeText(cite)
    copied.value = true
    setTimeout(() => (copied.value = false), 1400)
    navigateTo({ query: { ...route.query, p: page.value }, hash: `#cite-${a}` }, { replace: true })
  } catch { /* clipboard blocked — ignore */ }
}

// ── markdown-lite ──
function esc(s: string) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') }
function md(s: string) {
  if (!s) return ''
  let t = esc(s.replace(/^#{1,4}\s+/, ''))
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-stone-900">$1</strong>')
  t = t.replace(/\*(?!\s)([^*]+?)\*/g, '<em>$1</em>')
  t = t.replace(/\n/g, '<br>')
  return t
}
</script>
