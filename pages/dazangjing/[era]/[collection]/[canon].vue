<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink :to="`/dazangjing/${eraKey}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ collection?.name }}<span class="text-gray-400 mx-1">·</span>{{ canonLabel.zh }}</span>
      <span v-if="canon" class="text-xs text-gray-400 ml-1">{{ total }} 卷</span>
    </nav>

    <div v-if="!collection || !canon" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此藏。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <!-- 標頭 -->
      <div class="mb-5">
        <div class="flex items-center gap-3 mb-1.5">
          <div class="shrink-0 w-10 h-10 rounded-lg bg-stone-900 text-white flex items-center justify-center text-xl font-serif">{{ collection.glyph }}</div>
          <div>
            <h1 class="text-xl font-bold text-gray-900 leading-tight">
              {{ collection.name }}
              <span class="text-sm font-medium px-2 py-0.5 rounded ml-1" :class="canonKey === 'zheng' ? 'bg-emerald-100 text-emerald-800' : 'bg-stone-200 text-stone-700'">{{ canonLabel.zh }}</span>
            </h1>
            <div class="text-xs text-gray-400">{{ collection.name_en }} · {{ canonLabel.en }}</div>
          </div>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed">{{ canonLabel.desc }}</p>
        <p v-if="canon.summary" class="text-xs text-gray-600 leading-relaxed mt-1">{{ canon.summary }}</p>
      </div>

      <!-- 對照切換 -->
      <div class="flex items-center gap-2 mb-6 text-xs">
        <NuxtLink :to="`/dazangjing/${eraKey}/${collKey}/zheng`"
          class="px-3 py-1 rounded-full border transition"
          :class="canonKey === 'zheng' ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-400'">正藏 ({{ count(collection.zheng) }})</NuxtLink>
        <NuxtLink :to="`/dazangjing/${eraKey}/${collKey}/wai`"
          class="px-3 py-1 rounded-full border transition"
          :class="canonKey === 'wai' ? 'bg-stone-700 text-white border-stone-700' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-400'">外藏 ({{ count(collection.wai) }})</NuxtLink>
        <NuxtLink v-if="collection.portal" :to="collection.portal.to"
          class="ml-auto px-3 py-1 rounded-full bg-stone-100 text-stone-700 hover:bg-stone-200 transition">→ {{ collection.portal.label }}</NuxtLink>
      </div>

      <div v-if="total === 0" class="text-center text-gray-400 py-16 text-sm">此目錄尚未建置書目。</div>

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
              class="flex items-baseline gap-3 px-3 py-2 transition"
              :class="w.link ? 'hover:bg-emerald-50/60 cursor-pointer' : 'hover:bg-slate-50'"
            >
              <span class="shrink-0 w-7 text-right text-[11px] font-mono text-gray-300 tabular-nums">{{ runningNo(d, i) }}</span>
              <div class="min-w-0 flex-1">
                <span class="text-sm font-medium text-gray-900">{{ w.title_zh }}</span>
                <span v-if="w.title_orig" class="text-[11px] text-gray-400 italic ml-2">{{ w.title_orig }}</span>
                <span v-if="w.author" class="text-[11px] text-stone-600 ml-2">／{{ w.author }}</span>
                <span v-if="w.note" class="text-[11px] text-gray-500 block leading-relaxed mt-0.5">{{ w.note }}</span>
              </div>
              <span v-if="w.era" class="shrink-0 text-[10px] text-gray-400 whitespace-nowrap">{{ w.era }}</span>
              <span v-if="w.link" class="shrink-0 text-[10px] text-emerald-600 whitespace-nowrap">對照 →</span>
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
import { findEra, canonWorkCount, CANON_LABEL, type DazangCanon, type DazangDivision, type CanonKey } from '~/data/dazangjing'

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
