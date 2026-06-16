<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink :to="`/dazangjing/${eraKey}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ collection?.name }}<span class="text-gray-400 mx-1">·</span>{{ collection?.soleCanonLabel || canonLabel.zh }}</span>
      <span v-if="canon" class="text-xs text-gray-400 ml-1">{{ total }} 卷</span>
    </nav>

    <div v-if="!collection || !canon" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此藏。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <!-- 時代標題＋說明 -->
      <div v-if="era" class="mb-3">
        <NuxtLink :to="`/dazangjing/${eraKey}`" class="text-lg font-bold text-gray-900 hover:text-stone-600 transition">{{ era.glyph }}　{{ era.name }}</NuxtLink>
        <p class="text-xs text-gray-400 mt-0.5 leading-relaxed">{{ era.subtitle }}</p>
      </div>

      <!-- 標頭 -->
      <div class="mb-5">
        <div class="flex items-center gap-3 mb-1.5">
          <div class="shrink-0 w-10 h-10 rounded-lg bg-stone-900 text-white flex items-center justify-center text-xl font-serif">{{ collection.glyph }}</div>
          <div>
            <h1 class="text-xl font-bold text-gray-900 leading-tight">
              {{ collection.name }}
              <span class="text-sm font-medium px-2 py-0.5 rounded ml-1" :class="collection.soleCanonLabel ? 'bg-stone-200 text-stone-700' : (canonKey === 'zheng' ? 'bg-emerald-100 text-emerald-800' : 'bg-stone-200 text-stone-700')">{{ collection.soleCanonLabel || canonLabel.zh }}</span>
            </h1>
            <div class="text-xs text-gray-400">{{ collection.name_en }}{{ collection.soleCanonLabel ? '' : ' · ' + canonLabel.en }}</div>
          </div>
        </div>
        <p v-if="!collection.soleCanonLabel" class="text-xs text-gray-500 leading-relaxed">{{ canonLabel.desc }}</p>
        <p v-if="canon.summary" class="text-xs text-gray-600 leading-relaxed mt-1">{{ canon.summary }}</p>
      </div>

      <!-- 十藏快速切換 -->
      <div v-if="era" class="flex flex-wrap gap-1.5 mb-3">
        <NuxtLink v-for="c in era.collections" :key="c.key"
          :to="`/dazangjing/${eraKey}/${c.key}/${c.soleCanonLabel ? 'zheng' : canonKey}`"
          class="px-2.5 py-1 rounded-lg text-xs border transition"
          :class="c.key === collKey ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-400'">
          <span class="font-serif font-semibold">{{ c.glyph }}</span> {{ c.name }}
        </NuxtLink>
      </div>

      <!-- 對照切換（單一目錄藏不顯示） -->
      <div class="flex items-center gap-2 mb-6 text-xs">
        <template v-if="!collection.soleCanonLabel">
          <NuxtLink :to="`/dazangjing/${eraKey}/${collKey}/zheng`"
            class="px-3 py-1 rounded-full border transition"
            :class="canonKey === 'zheng' ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-400'">正藏 ({{ count(collection.zheng) }})</NuxtLink>
          <NuxtLink :to="`/dazangjing/${eraKey}/${collKey}/wai`"
            class="px-3 py-1 rounded-full border transition"
            :class="canonKey === 'wai' ? 'bg-stone-700 text-white border-stone-700' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-400'">外藏 ({{ count(collection.wai) }})</NuxtLink>
        </template>
        <NuxtLink v-if="collection.portal" :to="collection.portal.to"
          class="ml-auto px-3 py-1 rounded-full bg-stone-100 text-stone-700 hover:bg-stone-200 transition">→ {{ collection.portal.label }}</NuxtLink>
      </div>

      <!-- 正典層級圖例 -->
      <div v-if="usedTiers.length" class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-6 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
        <span class="text-gray-500">正典層級：</span>
        <span class="flex items-center gap-1.5"><span class="inline-block w-2.5 h-2.5 rounded-full border border-gray-300 bg-white" /><span class="text-gray-700">正典（無色）</span></span>
        <span v-for="t in usedTiers" :key="t" class="flex items-center gap-1.5">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="TIERS[t].dotCls" />
          <span :class="TIERS[t].titleCls">{{ TIERS[t].zh }}</span>
        </span>
      </div>

      <!-- 外藏來源圖例 -->
      <div v-if="usedSources.length" class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-6 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
        <span class="text-gray-500">文獻來源：</span>
        <span v-for="k in usedSources" :key="k" class="flex items-center gap-1.5">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="SOURCES[k].dotCls" />
          <span :class="SOURCES[k].titleCls">{{ SOURCES[k].zh }}</span>
        </span>
      </div>

      <div v-if="total === 0" class="text-center text-gray-400 py-16 text-sm">{{ canon.summary ? '本目錄依「正典封閉」留白——詳見上方說明。' : '此目錄尚未建置書目。' }}</div>

      <!-- 各部：列表呈現 -->
      <section v-for="d in canon.divisions" :key="d.key" class="mb-8">
        <div class="flex items-baseline gap-2 mb-1 border-b border-stone-300 pb-1.5">
          <h2 class="text-base font-bold text-stone-800">{{ d.label }}</h2>
          <span v-if="d.label_en" class="text-[11px] text-gray-400">{{ d.label_en }}</span>
          <span class="text-xs text-gray-400 ml-auto">{{ d.works.length }} 卷</span>
        </div>
        <p v-if="d.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2">{{ d.desc }}</p>

        <ol class="divide-y divide-gray-100 border-x border-b border-gray-100 rounded-b-md">
          <li v-for="(w, i) in d.works" :key="i">
            <component
              :is="w.link ? 'NuxtLink' : 'div'"
              :to="w.link || undefined"
              class="flex flex-col sm:flex-row gap-x-6 gap-y-1 px-3 py-2.5 transition"
              :class="w.link ? 'hover:bg-emerald-50/60 cursor-pointer' : 'hover:bg-slate-50'"
            >
              <!-- 左：標題與書目資料 -->
              <div class="sm:w-2/5 sm:shrink-0">
                <div class="flex items-baseline gap-2">
                  <span class="shrink-0 text-[11px] font-mono text-gray-300 tabular-nums">{{ runningNo(d, i) }}</span>
                  <span class="text-sm font-medium" :class="w.tier ? TIERS[w.tier].titleCls : (w.source && SOURCES[w.source] ? SOURCES[w.source].titleCls : 'text-gray-900')">{{ w.title_zh }}</span>
                </div>
                <div v-if="w.title_orig" class="ml-6 text-[11px] text-gray-400 italic leading-tight">{{ w.title_orig }}</div>
                <div class="ml-6 mt-1 text-[11px] text-stone-500 leading-relaxed flex flex-wrap gap-x-2">
                  <span class="text-gray-400">第 {{ runningNo(d, i) }} 卷</span>
                  <span v-if="w.author">{{ w.author }}</span>
                  <span v-if="w.era">{{ w.era }}</span>
                  <span v-if="w.place">{{ w.place }}</span>
                  <span v-if="w.language">{{ w.language }}</span>
                  <span v-if="w.link" class="text-emerald-600">對照 →</span>
                </div>
              </div>
              <!-- 右：簡介 -->
              <div v-if="w.intro || w.note" class="flex-1 min-w-0 text-[12px] text-gray-600 leading-relaxed">{{ w.intro || w.note }}</div>
            </component>
          </li>
        </ol>
      </section>

      <div class="text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>「對照 →」表示該卷已有站內全文對照可閱讀；其餘為待補的「漢語神學尋寶圖」條目。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findEra, canonWorkCount, CANON_LABEL, TIER_LABEL, SOURCE_META, SOURCE_ORDER, type DazangCanon, type DazangDivision, type CanonKey, type CanonTier } from '~/data/dazangjing'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const eraKey = computed(() => String(route.params.era))
const collKey = computed(() => String(route.params.collection))
const canonKey = computed<CanonKey>(() => (String(route.params.canon) === 'wai' ? 'wai' : 'zheng'))

const era = computed(() => findEra(eraKey.value))
const collection = computed(() => era.value?.collections.find(c => c.key === collKey.value))
const canon = computed<DazangCanon | undefined>(() => collection.value?.[canonKey.value])
const canonLabel = computed(() => CANON_LABEL[canonKey.value])
const total = computed(() => (canon.value ? canonWorkCount(canon.value) : 0))

// 塗色圖例：僅當此目錄含分級書卷（經藏正藏）才顯示
const usedTiers = computed<CanonTier[]>(() => {
  if (!canon.value) return []
  const set = new Set<CanonTier>()
  for (const d of canon.value.divisions) for (const w of d.works) if (w.tier) set.add(w.tier)
  return (['lxx', 'eastern', 'patristic'] as CanonTier[]).filter(t => set.has(t))
})
const TIERS = TIER_LABEL
const SOURCES = SOURCE_META
// 外藏來源圖例：列出此目錄用到的來源
const usedSources = computed<string[]>(() => {
  if (!canon.value) return []
  const set = new Set<string>()
  for (const d of canon.value.divisions) for (const w of d.works) if (w.source) set.add(w.source)
  return SOURCE_ORDER.filter(k => set.has(k))
})

useHead(() => ({ title: `${collection.value?.name ?? '大藏經'}·${canonLabel.value.zh} — Know Graph Lab` }))

function count(c: DazangCanon) { return canonWorkCount(c) }
// 連續卷號（跨部累計）
function runningNo(div: DazangDivision, idx: number) {
  if (!canon.value) return idx + 1
  let n = 0
  for (const d of canon.value.divisions) {
    if (d.key === div.key) return n + idx + 1
    n += d.works.length
  }
  return idx + 1
}
</script>
