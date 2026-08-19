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
          <span class="text-[11px] px-2 py-0.5 rounded bg-sky-50 text-sky-700">銘文／紙草</span>
          <a
            :href="doc.url" target="_blank" rel="noopener"
            class="text-[11px] px-2 py-0.5 rounded bg-stone-100 text-stone-600 hover:bg-stone-200 transition"
          >CGRN {{ doc.cgrn }} ↗</a>
        </div>
        <div class="text-xs text-gray-400 italic break-words mb-2">{{ doc.title_en }}</div>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600">
          <div v-if="doc.date" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ doc.date }}</dd></div>
          <div v-if="doc.provenance" class="flex gap-2"><dt class="shrink-0 text-gray-400">出土地</dt><dd class="break-words">{{ doc.provenance }}</dd></div>
          <div v-if="doc.support" class="flex gap-2 sm:col-span-2"><dt class="shrink-0 text-gray-400">載體</dt><dd class="break-words">{{ doc.support }}</dd></div>
        </dl>
      </div>

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
              第 {{ seg.line_from }} 行起
            </div>
            <div class="grid gap-x-5 gap-y-2 px-3 py-2.5" :class="gridCls">
              <div v-if="cols.includes('greek')" class="min-w-0">
                <div class="text-[10px] text-gray-400 mb-0.5">希臘原文</div>
                <p class="text-[13px] leading-relaxed text-gray-800 break-words whitespace-pre-line font-serif">{{ seg.greek || '—' }}</p>
              </div>
              <div v-if="cols.includes('en')" class="min-w-0">
                <div class="text-[10px] text-gray-400 mb-0.5">英譯（CGRN）</div>
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
import { findAligned } from '~/data/hellenika/sources'

definePageMeta({ middleware: 'auth' })

const COLUMNS = [
  { key: 'greek', label: '希臘原文' },
  { key: 'en', label: '英譯' },
  { key: 'zh', label: '繁體中文' },
] as const

const route = useRoute()
const doc = computed(() => findAligned(String(route.params.slug)))
const translated = computed(() => doc.value?.segments.filter(s => s.zh).length ?? 0)
const backTo = computed(() => (doc.value ? `/hellenika/greek/${doc.value.volume}` : '/hellenika'))

const cols = ref<string[]>(['greek', 'en', 'zh'])
const showNames = ref(false)

function toggle(key: string) {
  if (cols.value.includes(key)) {
    if (cols.value.length > 1) cols.value = cols.value.filter(c => c !== key)
  } else {
    cols.value = COLUMNS.map(c => c.key).filter(k => cols.value.includes(k) || k === key)
  }
}

const gridCls = computed(() => ({
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-3',
}[cols.value.length] ?? 'grid-cols-1'))

useHead(() => ({ title: `${doc.value?.title_zh ?? '銘文對照'} — 希臘羅馬大藏經` }))
</script>
