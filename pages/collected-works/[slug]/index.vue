<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader :title="author?.name ?? '全集'" :back="{ to: '/collected-works', label: '全集' }" container-class="max-w-5xl" :editable="false" />

    <div v-if="!author" class="max-w-5xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
      找不到這位學者。<NuxtLink to="/collected-works" class="text-sky-600 hover:underline">返回全集</NuxtLink>
    </div>

    <div v-else class="max-w-5xl mx-auto px-6 py-10">
      <!-- ── 頂部：肖像 + 學術貢獻簡介 ── -->
      <section class="flex flex-col sm:flex-row gap-8 mb-12">
        <div class="flex-shrink-0 sm:w-56">
          <img
            v-if="author.portraitUrl"
            :src="author.portraitUrl"
            :alt="author.name"
            class="w-full rounded-2xl object-cover bg-gray-100 ring-1 ring-gray-200 shadow-sm"
            loading="lazy"
          />
          <div
            v-else
            class="w-full aspect-[3/4] rounded-2xl bg-gray-100 ring-1 ring-gray-200 shadow-sm flex items-center justify-center text-6xl"
          >{{ author.emoji }}</div>
          <p v-if="author.portraitCredit" class="mt-2 text-[11px] text-gray-400 text-center">{{ author.portraitCredit }}</p>
        </div>

        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900">{{ author.name }}</h1>
          <p class="text-sm text-gray-500 mt-0.5">
            <span v-if="author.nameOriginal" class="italic">{{ author.nameOriginal }}</span>
            <span class="font-mono ml-2">{{ author.lifespan }}</span>
          </p>
          <div class="mt-2 flex items-center gap-1.5 flex-wrap">
            <span
              v-for="f in author.fields"
              :key="f"
              class="text-xs px-2 py-0.5 rounded-full"
              :class="`bg-${author.color}-50 text-${author.color}-700`"
            >{{ f }}</span>
          </div>

          <div class="mt-4 space-y-3">
            <p
              v-for="(p, i) in author.contribution"
              :key="i"
              class="text-sm text-gray-700 leading-relaxed"
              v-html="renderBold(p)"
            ></p>
          </div>

          <p v-if="author.sourceNote" class="mt-4 text-xs text-gray-500 leading-relaxed border-l-2 pl-3" :class="`border-${author.color}-200`">
            <span class="font-medium text-gray-600">來源與語言：</span>{{ author.sourceNote }}
          </p>
        </div>
      </section>

      <!-- ── 生平學術年表 ── -->
      <section class="mb-12">
        <h2 class="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span>🗓️</span> 生平學術年表
        </h2>
        <ol class="relative border-l-2 ml-2" :class="`border-${author.color}-100`">
          <li v-for="(t, i) in author.timeline" :key="i" class="ml-5 pb-4 last:pb-0">
            <span
              class="absolute -left-[7px] w-3 h-3 rounded-full ring-4 ring-slate-50"
              :class="`bg-${author.color}-500`"
            ></span>
            <div class="flex items-baseline gap-3">
              <span class="text-xs font-mono font-semibold text-gray-500 flex-shrink-0 w-20">{{ t.year }}</span>
              <span class="text-sm text-gray-700 leading-relaxed">{{ t.text }}</span>
            </div>
          </li>
        </ol>
      </section>

      <!-- ── 著作目錄（按類別與年分；依年分依序轉錄） ── -->
      <section>
        <h2 class="text-base font-bold text-gray-800 mb-1 flex items-center gap-2">
          <span>📚</span> 著作目錄
        </h2>
        <p class="text-xs text-gray-400 mb-5">按類別與年分編排，依年分依序轉錄為原文／繁中多欄對照。</p>

        <div v-for="g in workGroups" :key="g.category" class="mb-8">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-200">{{ g.category }}</h3>
          <ul class="space-y-2">
            <li v-for="(w, i) in g.items" :key="i">
              <component
                :is="linkTarget(w) ? RowLink : 'div'"
                :to="linkTarget(w)"
                class="work-row group"
                :class="linkTarget(w)
                  ? `bg-white border-${author.color}-100 hover:border-${author.color}-300 hover:shadow-sm cursor-pointer no-underline`
                  : 'bg-gray-50 border-gray-100'"
              >
                <span class="text-xs font-mono text-gray-400 w-20 flex-shrink-0">{{ w.year }}</span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-gray-800 font-medium">
                    {{ w.title }}
                    <span v-if="w.languages" class="ml-1.5 align-middle">
                      <span
                        v-for="l in w.languages"
                        :key="l"
                        class="text-[10px] px-1 py-px rounded bg-gray-100 text-gray-500 mr-0.5"
                      >{{ langLabel(l) }}</span>
                    </span>
                  </div>
                  <div v-if="w.titleOriginal" class="text-xs text-gray-400 italic truncate">{{ w.titleOriginal }}</div>
                  <div v-if="w.note" class="text-[11px] text-gray-400 mt-0.5 leading-snug">{{ w.note }}</div>
                </div>
                <span class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0 self-start" :class="statusClass(effStatus(w))">
                  {{ statusLabel(effStatus(w)) }}
                </span>
              </component>
            </li>
          </ul>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CwWork, WorkStatus } from '~/stores/collectedWorks'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const store = useCollectedWorksStore()
const author = computed(() => store.bySlug(route.params.slug as string))

// Bind the resolved NuxtLink component object (NOT the string 'NuxtLink') to
// <component :is>. Auto-imported components aren't reliably resolvable by string
// name at runtime, so `:is="'NuxtLink'"` can render a dead <nuxtlink> element
// with no href — the cards then look clickable but do nothing.
const RowLink = resolveComponent('NuxtLink')

// Live transcription progress: a work with >1 chunk in the DB has real content,
// so auto-upgrade a 'planned' work with an ebookId to clickable 轉錄中 without
// hand-editing the store as the background queue fills books in.
const liveChunks = ref<Record<string, number>>({})
onMounted(async () => {
  try {
    const data = await $fetch<any>('/api/ebooks?collection=collected-works')
    const list = Array.isArray(data) ? data : data?.ebooks ?? []
    const m: Record<string, number> = {}
    for (const e of list) if (e?.id) m[e.id] = e.chunk_count ?? 0
    liveChunks.value = m
  } catch {
    /* hub still renders from the static store if the fetch fails */
  }
})

function effStatus(w: CwWork): WorkStatus {
  if (w.status === 'done') return 'done'
  if (w.ebookId && (liveChunks.value[w.ebookId] ?? 0) > 1) return 'in-progress'
  return w.status
}
function isReadable(w: CwWork): boolean {
  const s = effStatus(w)
  return !!w.ebookId && (s === 'done' || s === 'in-progress')
}
// Navigation target for a work row: an external corpus/portal (e.g. 東方聖書)
// takes precedence; otherwise the全集專屬三欄 reader when the work is readable
// (全集不再走 /ebook UI — 見 pages/collected-works/[slug]/[work].vue)。
// Returns undefined → the row renders as a non-clickable <div>.
function linkTarget(w: CwWork): string | undefined {
  if (w.externalUrl) return w.externalUrl
  return isReadable(w) ? `/collected-works/${route.params.slug}/${w.ebookId}` : undefined
}

useHead(() => ({ title: author.value ? `${author.value.name} — 全集` : '全集' }))

// 按 works 陣列中類別首次出現的順序分組，組內依年分排序
const workGroups = computed(() => {
  if (!author.value) return []
  const order: string[] = []
  const map = new Map<string, CwWork[]>()
  for (const w of author.value.works) {
    if (!map.has(w.category)) {
      map.set(w.category, [])
      order.push(w.category)
    }
    map.get(w.category)!.push(w)
  }
  return order.map((category) => ({
    category,
    items: [...map.get(category)!].sort((a, b) => a.yearSort - b.yearSort),
  }))
})

const LANG_LABELS: Record<string, string> = { en: '英', de: '德', la: '拉', fr: '法', el: '希', grc: '希臘', he: '希伯來', zh: '繁中' }
const langLabel = (l: string) => LANG_LABELS[l] ?? l

const STATUS: Record<WorkStatus, { label: string; cls: string }> = {
  done: { label: '已轉錄', cls: 'bg-emerald-50 text-emerald-700' },
  'in-progress': { label: '轉錄中', cls: 'bg-amber-50 text-amber-700' },
  planned: { label: '待轉錄', cls: 'bg-gray-100 text-gray-500' },
  copyright: { label: '版權待源', cls: 'bg-stone-100 text-stone-500' },
}
const statusLabel = (s: WorkStatus) => STATUS[s].label
const statusClass = (s: WorkStatus) => STATUS[s].cls

// 受信任的自製內容：只把 **粗體** 轉成 <strong>
function renderBold(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
}
</script>

<style scoped>
.work-row {
  @apply flex items-start gap-3 px-3 py-2.5 rounded-xl border transition-all duration-150;
}
</style>

<!-- Dynamic Tailwind colors (bg-${color}-*, text-${color}-*, border-${color}-*) are safelisted in tailwind.config.ts -->
