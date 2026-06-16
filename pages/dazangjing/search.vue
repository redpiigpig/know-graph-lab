<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/dazangjing" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">搜尋書卷</span>
    </nav>

    <div class="flex-1 max-w-4xl w-full mx-auto px-6 py-8">
      <div class="mb-5">
        <input
          v-model="q"
          type="search"
          autofocus
          placeholder="輸入書卷名或作者（中英文皆可，例：奧古斯丁 / Augustine / 神學大全 / Talmud）"
          class="w-full px-4 py-3 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400 focus:border-stone-400"
        />
        <p class="text-xs text-gray-400 mt-2">
          全藏共 {{ rows.length }} 卷。比對書卷漢語名、原文／西文名、作者。
          <span v-if="q.trim()">　找到 <b class="text-stone-700">{{ results.length }}</b> 卷{{ capped ? '（僅顯示前 300）' : '' }}</span>
        </p>
      </div>

      <div v-if="q.trim() && results.length === 0" class="text-center text-sm text-gray-400 py-16">
        查無符合「{{ q.trim() }}」的書卷。
      </div>

      <div v-else class="space-y-2.5">
        <NuxtLink
          v-for="(r, i) in results"
          :key="i"
          :to="`/dazangjing/${r.eraKey}/${r.colKey}/${r.canon}`"
          class="block bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-stone-300 transition"
        >
          <div class="flex items-center gap-1.5 mb-1.5 flex-wrap">
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-stone-900 text-white font-serif">{{ r.eraGlyph }}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-700 font-serif">{{ r.colGlyph }}{{ r.colName }}</span>
            <span
              class="text-[10px] px-1.5 py-0.5 rounded"
              :class="r.canon === 'zheng' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'"
            >{{ r.canon === 'zheng' ? '正藏' : '外藏' }}</span>
            <span class="text-[10px] text-gray-400">· {{ r.divLabel }}</span>
          </div>
          <div class="font-semibold text-gray-900 text-sm">
            {{ r.w.title_zh }}
            <span v-if="r.w.title_orig" class="text-gray-400 font-normal">　{{ r.w.title_orig }}</span>
          </div>
          <div class="text-xs text-gray-500 mt-0.5">
            <span v-if="r.w.author">{{ r.w.author }}</span>
            <span v-if="r.w.era"> · {{ r.w.era }}</span>
            <span v-if="r.w.place"> · {{ r.w.place }}</span>
            <span v-if="r.w.language"> · {{ r.w.language }}</span>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ERAS, type DazangWork } from '~/data/dazangjing'

type Row = {
  eraKey: string; eraGlyph: string
  colKey: string; colName: string; colGlyph: string
  canon: 'zheng' | 'wai'; divLabel: string
  w: DazangWork
}

const route = useRoute()
const q = ref(((route.query.q as string) || '').trim())

const rows = computed<Row[]>(() => {
  const out: Row[] = []
  for (const era of ERAS)
    for (const c of era.collections)
      for (const canon of ['zheng', 'wai'] as const)
        for (const d of c[canon].divisions)
          for (const w of d.works)
            out.push({
              eraKey: era.key, eraGlyph: era.glyph,
              colKey: c.key, colName: c.name, colGlyph: c.glyph,
              canon, divLabel: d.label, w,
            })
  return out
})

const norm = (s?: string) => (s || '').toLowerCase()
const matches = computed<Row[]>(() => {
  const k = q.value.trim().toLowerCase()
  if (!k) return []
  return rows.value.filter(
    (r) => norm(r.w.title_zh).includes(k) || norm(r.w.title_orig).includes(k) || norm(r.w.author).includes(k),
  )
})
const capped = computed(() => matches.value.length > 300)
const results = computed(() => matches.value.slice(0, 300))

definePageMeta({ middleware: 'auth' })
useHead({ title: '搜尋書卷 — 基督教大藏經' })
</script>
