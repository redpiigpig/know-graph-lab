<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="doc ? doc.title_zh : '銘文對照'"
      :back="{ to: backTo, label: '希臘羅馬大藏經' }"
      container-class="max-w-6xl"
    >
      <template #actions>
        <span v-if="doc" class="text-xs text-gray-400">{{ doc.segments.length }} 段 · 已譯 {{ translated }}</span>
      </template>
    </AppHeader>

    <div v-if="!doc" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此篇。</div>

    <div v-else class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
      <!-- 篇首 -->
      <div class="mb-5">
        <div class="flex items-baseline gap-2 flex-wrap mb-1">
          <h1 class="text-xl font-bold text-gray-900 break-words">{{ doc.title_zh }}</h1>
          <span
            class="text-[11px] px-2 py-0.5 rounded"
            :class="doc.source === 'perseus' ? 'bg-emerald-50 text-emerald-700' : 'bg-sky-50 text-sky-700'"
          >{{ doc.source === 'perseus' ? '文獻' : '銘文／紙草' }}</span>
          <a
            :href="doc.url" target="_blank" rel="noopener"
            class="text-[11px] px-2 py-0.5 rounded bg-stone-100 text-stone-600 hover:bg-stone-200 transition"
          >{{ doc.siglum }} ↗</a>
        </div>
        <div class="text-xs text-gray-400 italic break-words mb-2">{{ doc.title_en }}</div>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600">
          <div v-if="doc.date" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ doc.date }}</dd></div>
          <div v-if="doc.provenance" class="flex gap-2"><dt class="shrink-0 text-gray-400">出土地</dt><dd class="break-words">{{ doc.provenance }}</dd></div>
          <div v-if="doc.support" class="flex gap-2 sm:col-span-2"><dt class="shrink-0 text-gray-400">載體</dt><dd class="break-words">{{ doc.support }}</dd></div>
          <div v-if="doc.author" class="flex gap-2"><dt class="shrink-0 text-gray-400">作者</dt><dd class="break-words">{{ doc.author }}</dd></div>
          <div v-if="doc.lines_total" class="flex gap-2"><dt class="shrink-0 text-gray-400">篇幅</dt><dd class="break-words">全 {{ doc.lines_total }} 行</dd></div>
        </dl>
      </div>

      <!-- 無英譯中介的告示：這是比經由學術英譯更高的風險，讀者有權知道 -->
      <div v-if="doc.pivot === 'none'" class="mb-4 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg">
        <div class="text-[11px] font-semibold text-amber-900 mb-0.5">繁中直接譯自希臘原文</div>
        <p class="text-[11px] text-amber-800 leading-relaxed break-words">{{ doc.pivot_note }}</p>
      </div>
      <!-- 有英譯中介、但切段方式需要說明者（如逐行對不起來的舊譯）走中性告示，不用警示色 -->
      <p
        v-else-if="doc.pivot_note"
        class="mb-4 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px] text-gray-500 leading-relaxed break-words"
      >{{ doc.pivot_note }}</p>

      <!-- 同組篇目：荷馬詩頌 33 首、俄耳甫斯詩頌 87 首各自成組，逐首一頁，須能互相走到 -->
      <nav v-if="series.length > 1" class="mb-5">
        <div class="flex flex-wrap gap-1">
          <NuxtLink
            v-for="t in series" :key="t.slug"
            :to="`/hellenika/text/${alignedSlug(t)}`"
            class="px-1.5 py-0.5 rounded text-[11px] border tabular-nums transition"
            :class="t.slug === slug
              ? 'bg-stone-900 text-white border-stone-900'
              : 'bg-white text-gray-500 border-gray-200 hover:border-stone-400'"
          >{{ seriesLabel(t) }}</NuxtLink>
        </div>
      </nav>

      <!-- 欄位切換 -->
      <div class="flex flex-wrap items-center gap-1.5 mb-4">
        <button
          v-for="c in COLUMNS" :key="c.key"
          class="px-2.5 py-1 rounded-lg text-xs border transition"
          :class="cols.includes(c.key)
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-400'"
          @click="toggle(c.key)"
        >{{ c.label }}</button>
        <button
          v-if="Object.keys(doc.names).length"
          class="ml-auto px-2.5 py-1 rounded-lg text-xs border bg-white text-gray-600 border-gray-200 hover:border-stone-400 transition"
          @click="showNames = !showNames"
        >專名定譯 {{ Object.keys(doc.names).length }} 條 {{ showNames ? '▲' : '▼' }}</button>
      </div>

      <!-- 專名表 -->
      <div v-if="showNames" class="mb-5 px-3 py-2.5 bg-white border border-gray-200 rounded-lg">
        <p class="text-[11px] text-gray-500 mb-2">本篇專名先一次定名，全篇逐段沿用——否則同一個名字會在不同段落被譯成不同寫法。</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-5 gap-y-0.5 text-[11px]">
          <div v-for="(zh, en) in doc.names" :key="en" class="flex gap-1.5 min-w-0">
            <span class="text-gray-400 italic truncate">{{ en }}</span>
            <span class="text-gray-300">→</span>
            <span class="text-gray-800 truncate">{{ zh }}</span>
          </div>
        </div>
      </div>

      <!-- 逐段對照 -->
      <div class="space-y-3">
        <template v-for="(seg, i) in doc.segments" :key="i">
          <div v-if="seg.face && seg.face !== doc.segments[i - 1]?.face"
               class="pt-2 text-sm font-bold text-stone-800 border-b border-stone-300 pb-1">{{ seg.face }}</div>

          <div v-if="seg.note" class="px-3 py-2 rounded-lg bg-amber-50 text-amber-800 text-[11px]">{{ seg.note }}</div>

          <div v-else class="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div class="px-3 py-1 bg-slate-50 border-b border-gray-100 text-[10px] font-mono text-gray-400">
              <template v-if="seg.case">案 {{ seg.case }}　第 {{ seg.line_from }}–{{ seg.line_to }} 行</template>
              <template v-else-if="!seg.case && seg.line_to">序　第 {{ seg.line_from }}–{{ seg.line_to }} 行</template>
              <template v-else>第 {{ seg.line_from }} 行起</template>
            </div>
            <div class="grid gap-x-5 gap-y-2 px-3 py-2.5" :class="gridCls">
              <div v-if="cols.includes('greek')" class="min-w-0">
                <div class="text-[10px] text-gray-400 mb-0.5">希臘原文</div>
                <p class="text-[13px] leading-relaxed text-gray-800 break-words whitespace-pre-line font-serif">{{ seg.greek || '—' }}</p>
              </div>
              <div v-if="cols.includes('en')" class="min-w-0">
                <div class="text-[10px] text-gray-400 mb-0.5">英譯（{{ EN_SOURCE[doc.pivot] ?? 'CGRN' }}）</div>
                <p class="text-[13px] leading-relaxed text-gray-700 break-words">{{ seg.en || '—' }}</p>
              </div>
              <div v-if="cols.includes('zh')" class="min-w-0">
                <div class="text-[10px] text-gray-400 mb-0.5">繁體中文</div>
                <p v-if="seg.zh" class="text-[13px] leading-relaxed text-gray-900 break-words">{{ seg.zh }}</p>
                <p v-else class="text-[12px] text-gray-300">待譯</p>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 書目與授權 -->
      <div class="mt-8 text-[11px] text-gray-400 leading-relaxed border-t border-gray-200 pt-4 space-y-1">
        <p v-if="doc.bibliography"><b class="text-gray-500">書目</b>　{{ doc.bibliography }}</p>
        <p><b class="text-gray-500">原文與英譯</b>　{{ doc.licence }}</p>
        <p><b class="text-gray-500">體例</b>　方括號 [ ] 為石面已缺而由編者補入，非石上實存；分段以石面行為單位，行號即引用基礎，未按語意重排。繁中為本站逐段翻譯。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AlignedRef } from '~/data/hellenika/sources'
import { ALIGNED_REFS, alignedSlug, hasEnglish, loadAligned } from '~/data/hellenika/sources'

definePageMeta({ middleware: 'auth' })

// 英譯欄該標誰的譯本。原本寫死「CGRN」，文獻篇目全標錯了。
const EN_SOURCE: Record<string, string> = {
  'cgrn': 'CGRN',
  'perseus-eng': 'Perseus',
  'taylor-eng': 'Taylor 1792',
}

const ALL_COLUMNS = [
  { key: 'greek', label: '希臘原文' },
  { key: 'en', label: '英譯' },
  { key: 'zh', label: '繁體中文' },
]

const route = useRoute()
// 正文按需載入：全部篇目合計 5.9 MB，不可在建置期一次打包（見 sources/index.ts）
const slug = computed(() => String(route.params.slug))
const { data: doc } = await useAsyncData(
  () => `hellenika-text-${slug.value}`,
  () => loadAligned(slug.value).then(d => d ?? null),
  { watch: [slug] })
const translated = computed(() => doc.value?.segments.filter(s => s.zh).length ?? 0)
const backTo = computed(() => (doc.value ? `/hellenika/greek/${doc.value.volume}` : '/hellenika'))

// 無英譯中介的篇目不出英譯欄，免得整欄都是「—」
const COLUMNS = computed(() =>
  ALL_COLUMNS.filter(c => c.key !== 'en' || (doc.value && hasEnglish(doc.value))))
const cols = ref<string[]>(['greek', 'en', 'zh'])
watchEffect(() => { cols.value = COLUMNS.value.map(c => c.key) })
const showNames = ref(false)

// 成組的篇目（slug 為「前綴-兩位數」者）。荷馬詩頌與俄耳甫斯詩頌都是逐首一頁，
// 書目那邊只掛得住一條連結，沒有這條列就走不到其餘各首。
const series = computed<AlignedRef[]>(() => {
  const m = slug.value.match(/^(.+)-(\d+)$/)
  if (!m) return []
  const prefix = `${m[1]}-`
  return ALIGNED_REFS.filter(
    t => t.slug.startsWith(prefix) && /^\d+$/.test(t.slug.slice(prefix.length)))
})

/** 俄耳甫斯詩頌的第 0 首是序詩，不是「第 0 首」，另標。 */
function seriesLabel(t: AlignedRef): string {
  const n = Number(t.slug.split('-').pop())
  return n === 0 ? '序' : String(n)
}

function toggle(key: string) {
  if (cols.value.includes(key)) {
    if (cols.value.length > 1) cols.value = cols.value.filter(c => c !== key)
  } else {
    cols.value = COLUMNS.value.map(c => c.key).filter(k => cols.value.includes(k) || k === key)
  }
}

const gridCls = computed(() => ({
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-3',
}[cols.value.length] ?? 'grid-cols-1'))

useHead(() => ({ title: `${doc.value?.title_zh ?? '銘文對照'} — 希臘羅馬大藏經` }))
</script>
