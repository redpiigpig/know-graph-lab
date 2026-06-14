<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink to="/dazangjing" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ era?.name ?? '基督教大藏經' }}</span>
      <span v-if="era" class="text-xs text-gray-400 ml-1">{{ era.collections.length }} 藏</span>
    </nav>

    <div v-if="!era" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此時代。</div>

    <div v-else class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ era.glyph }}　{{ era.name }}</h1>
        <p class="text-sm text-gray-500">{{ era.subtitle }}</p>
        <p v-if="era.boundary" class="text-xs text-gray-400 mt-1.5 leading-relaxed">📐 年代結界：{{ era.boundary }}</p>
      </div>

      <!-- 藏目快速導覽 -->
      <div class="flex flex-wrap gap-1.5 mb-8 sticky top-12 bg-slate-50/90 backdrop-blur py-2 -mx-2 px-2 z-20">
        <a
          v-for="c in era.collections"
          :key="c.key"
          :href="`#${c.key}`"
          class="px-2.5 py-1 rounded-full border border-gray-200 bg-white text-xs text-gray-700 hover:border-stone-400 hover:text-stone-800 transition"
        >
          <span class="font-serif font-semibold">{{ c.glyph }}</span>
          <span class="ml-1">{{ c.name }}</span>
          <span class="text-gray-400 ml-1">({{ workCount(c) }})</span>
        </a>
      </div>

      <!-- 各藏 -->
      <section v-for="c in era.collections" :key="c.key" :id="c.key" class="mb-12 scroll-mt-28">
        <div class="flex items-start gap-3 mb-3 border-b-2 border-stone-800 pb-2">
          <div class="shrink-0 w-10 h-10 rounded-lg bg-stone-900 text-white flex items-center justify-center text-xl font-serif">{{ c.glyph }}</div>
          <div class="min-w-0 flex-1">
            <div class="flex items-baseline gap-2 flex-wrap">
              <h2 class="text-lg font-bold text-gray-900">{{ c.name }}</h2>
              <span class="text-xs text-gray-400">{{ c.name_en }}</span>
              <span v-if="c.genres" class="text-[11px] text-stone-500 font-serif">〔{{ c.genres }}〕</span>
            </div>
            <p class="text-xs text-gray-600 leading-relaxed mt-0.5">{{ c.summary }}</p>
          </div>
          <NuxtLink
            v-if="c.portal"
            :to="c.portal.to"
            class="shrink-0 text-[11px] px-2 py-1 rounded bg-stone-100 text-stone-700 hover:bg-stone-200 transition whitespace-nowrap"
          >→ {{ c.portal.label }}</NuxtLink>
        </div>

        <!-- 各部 -->
        <div v-for="d in c.divisions" :key="d.key" class="mb-5">
          <div class="flex items-baseline gap-2 mb-2">
            <h3 class="text-sm font-semibold text-stone-700">{{ d.label }}</h3>
            <span v-if="d.label_en" class="text-[10px] text-gray-400">{{ d.label_en }}</span>
            <span class="text-[10px] text-gray-400 ml-auto">{{ d.works.length }} 部</span>
          </div>
          <p v-if="d.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 -mt-0.5">{{ d.desc }}</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <component
              :is="w.link ? 'NuxtLink' : 'div'"
              v-for="(w, i) in d.works"
              :key="i"
              :to="w.link || undefined"
              class="block bg-white border border-gray-200 rounded-md px-3 py-2.5 transition"
              :class="w.link ? 'hover:border-stone-400 hover:shadow-sm cursor-pointer' : ''"
            >
              <div class="flex items-start gap-1.5">
                <div class="min-w-0 flex-1">
                  <div class="font-semibold text-gray-900 text-sm leading-tight">{{ w.title_zh }}</div>
                  <div v-if="w.title_orig" class="text-[11px] text-gray-500 mt-0.5 leading-tight italic">{{ w.title_orig }}</div>
                </div>
                <span v-if="w.era" class="shrink-0 text-[10px] text-gray-400 whitespace-nowrap">{{ w.era }}</span>
              </div>
              <div v-if="w.author" class="text-[11px] text-stone-600 mt-1">{{ w.author }}</div>
              <div v-if="w.note" class="text-[11px] text-gray-500 mt-1 leading-relaxed">{{ w.note }}</div>
              <div v-if="w.link" class="text-[10px] text-stone-400 mt-1">→ 站內對照</div>
            </component>
          </div>
        </div>
      </section>

      <div class="text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>書目為策展骨架——已有站內對照者標「→ 站內對照」可點擊閱讀；其餘為待補的「漢語神學尋寶圖」條目。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findEra, type DazangCollection } from '~/data/dazangjing'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const era = computed(() => findEra(String(route.params.era)))

useHead(() => ({ title: `${era.value?.name ?? '基督教大藏經'} — Know Graph Lab` }))

function workCount(c: DazangCollection) {
  return c.divisions.reduce((n, d) => n + d.works.length, 0)
}
</script>
