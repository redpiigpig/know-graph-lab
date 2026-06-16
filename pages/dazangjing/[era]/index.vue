<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/dazangjing" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ era?.name ?? '基督教大藏經' }}</span>
      <span v-if="era" class="text-xs text-gray-400 ml-1">{{ era.collections.length }} 藏{{ allSole ? '' : ' × 2（正藏／外藏）' }}</span>
    </nav>

    <div v-if="!era" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此時代。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ era.glyph }}　{{ era.name }}</h1>
        <p class="text-sm text-gray-500">{{ era.subtitle }}</p>
        <p v-if="era.boundary" class="text-xs text-gray-400 mt-1.5 leading-relaxed">📐 年代結界：{{ era.boundary }}</p>
        <p v-if="!allSole" class="text-xs text-gray-400 mt-1 leading-relaxed">每一藏分「正藏」（教會論邊界之內的群體記憶）與「外藏」（邊界之外、隱密上帝的平行啟示與見證，「外」無貶義）兩套平行目錄，各為獨立頁面。</p>
        <p v-else class="text-xs text-gray-400 mt-1 leading-relaxed">基督教之前無正／外之分，僅立「前藏」——邊界劃分之前的原始啟示母體。</p>
      </div>

      <!-- 十藏快速切換 -->
      <div class="flex flex-wrap gap-1.5 mb-6">
        <NuxtLink v-for="c in era.collections" :key="c.key"
          :to="`/dazangjing/${era.key}/${c.key}/zheng`"
          class="px-2.5 py-1 rounded-lg text-xs border bg-white text-gray-600 border-gray-200 hover:border-stone-400 transition">
          <span class="font-serif font-semibold">{{ c.glyph }}</span> {{ c.name }}
        </NuxtLink>
      </div>

      <!-- 十藏列表 -->
      <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
        <div
          v-for="(c, i) in era.collections"
          :key="c.key"
          class="flex items-center gap-4 px-4 py-3.5 hover:bg-slate-50 transition"
        >
          <div class="shrink-0 w-9 h-9 rounded-lg bg-stone-900 text-white flex items-center justify-center text-lg font-serif">{{ c.glyph }}</div>
          <div class="min-w-0 flex-1">
            <div class="flex items-baseline gap-2 flex-wrap">
              <span class="text-gray-300 text-xs font-mono">{{ String(i + 1).padStart(2, '0') }}</span>
              <span class="font-semibold text-gray-900">{{ c.name }}</span>
              <span class="text-[11px] text-gray-400">{{ c.name_en }}</span>
              <span v-if="c.genres" class="text-[10px] text-stone-500 font-serif">〔{{ c.genres }}〕</span>
            </div>
            <p class="text-xs text-gray-500 leading-relaxed mt-0.5 line-clamp-2">{{ c.summary }}</p>
          </div>
          <div class="shrink-0 flex items-center gap-1.5">
            <template v-if="c.soleCanonLabel">
              <NuxtLink
                :to="`/dazangjing/${era.key}/${c.key}/zheng`"
                class="px-2.5 py-1.5 rounded-lg bg-stone-900 text-white text-xs font-medium hover:bg-stone-700 transition whitespace-nowrap"
              >{{ c.soleCanonLabel }} <span class="opacity-80">{{ count(c.zheng) }}</span></NuxtLink>
            </template>
            <template v-else>
              <NuxtLink
                :to="`/dazangjing/${era.key}/${c.key}/zheng`"
                class="px-2.5 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium hover:bg-emerald-700 transition whitespace-nowrap"
              >正藏 <span class="opacity-80">{{ count(c.zheng) }}</span></NuxtLink>
              <NuxtLink
                :to="`/dazangjing/${era.key}/${c.key}/wai`"
                class="px-2.5 py-1.5 rounded-lg bg-stone-200 text-stone-700 text-xs font-medium hover:bg-stone-300 transition whitespace-nowrap"
              >外藏 <span class="opacity-70">{{ count(c.wai) }}</span></NuxtLink>
            </template>
          </div>
        </div>
      </div>

      <div class="mt-8 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p v-if="!allSole">綠＝正藏（教會論／社會學邊界之內的群體記憶）；灰＝外藏（邊界之外、隱密上帝的平行啟示與神聖見證，無貶義）。數字為該目錄卷數。</p>
        <p v-else>「前藏」＝邊界劃分之前的原始啟示母體——普遍之道在人類文明初期的漫溢、全人類共享的屬靈資產。數字為卷數。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findEra, canonWorkCount, type DazangCanon } from '~/data/dazangjing'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const era = computed(() => findEra(String(route.params.era)))
const allSole = computed(() => !!era.value && era.value.collections.length > 0 && era.value.collections.every(c => !!c.soleCanonLabel))
useHead(() => ({ title: `${era.value?.name ?? '基督教大藏經'} — Know Graph Lab` }))

function count(c: DazangCanon) { return canonWorkCount(c) }
</script>
