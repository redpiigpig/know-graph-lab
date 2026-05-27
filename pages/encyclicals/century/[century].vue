<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0">
      <NuxtLink to="/encyclicals" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <span class="text-sm font-semibold text-stone-900">🕊️ 教宗訓導文獻</span>
      <span class="text-stone-300">/</span>
      <span class="text-sm text-stone-700">{{ century }} 世紀</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap">{{ popes.length }} 位教宗 / {{ docCount }} 篇</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="text-xs text-stone-400 mb-1">{{ centuryYearRange }}</div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight">{{ century }} 世紀</h1>
        <p class="text-sm text-stone-500 leading-relaxed mt-2">{{ centuryBlurb }}</p>
      </header>

      <div v-if="popes.length === 0" class="text-center text-stone-400 py-16 text-sm">
        此世紀尚未錄入教宗。
      </div>

      <div v-else class="space-y-3">
        <NuxtLink
          v-for="pope in popes"
          :key="pope.slug"
          :to="`/encyclicals/pope/${pope.slug}`"
          class="block bg-white border border-stone-200 rounded-xl px-6 py-5 hover:border-stone-400 hover:shadow-md transition-all duration-150"
        >
          <div class="flex items-start gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline flex-wrap gap-2 mb-1">
                <h3 class="font-bold text-stone-900 text-lg">{{ pope.nameZh }}</h3>
                <span class="text-xs italic text-stone-500">{{ pope.nameLat }}</span>
                <span class="text-[11px] font-mono text-stone-400">
                  {{ pope.pontificateStart.slice(0, 4) }}–{{ pope.pontificateEnd ? pope.pontificateEnd.slice(0, 4) : '今' }}
                </span>
                <span
                  v-if="centuriesOfPope(pope).length > 1"
                  class="text-[10px] px-1.5 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200"
                  :title="`此教宗任期跨 ${centuriesOfPope(pope).map(c => c + 'c').join(' + ')}`"
                >跨世紀</span>
              </div>
              <div class="text-xs text-stone-500 mb-2">
                {{ pope.nationality }}
                <span v-if="pope.birthName" class="text-stone-400">
                  · 俗名 {{ pope.birthName }}
                </span>
              </div>
              <div v-if="pope.notesZh" class="text-[13px] text-stone-700 leading-relaxed line-clamp-2">
                {{ pope.notesZh }}
              </div>
            </div>
            <div class="flex-shrink-0 text-right">
              <div v-if="docCountInThisCentury(pope.slug) > 0" class="text-2xl font-bold text-amber-700">
                {{ docCountInThisCentury(pope.slug) }}
              </div>
              <div v-else class="text-2xl font-bold text-stone-300">—</div>
              <div class="text-[10px] uppercase tracking-wider text-stone-400 mt-0.5">
                本世紀篇數
              </div>
              <div v-if="documentsByPope(pope.slug).length > docCountInThisCentury(pope.slug)" class="text-[10px] text-stone-400 mt-1">
                全教宗 {{ documentsByPope(pope.slug).length }} 篇
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  POPES,
  popesInCentury,
  centuriesOfPope,
  documentsInCentury,
  documentsByPope,
  documentCountForPopeInCentury,
} from '~/data/encyclicals'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const century = computed(() => parseInt(route.params.century as string, 10))

useHead(() => ({
  title: `${century.value} 世紀教宗 — 教宗訓導文獻`,
}))

const popes = computed(() => popesInCentury(century.value))
const docCount = computed(() => documentsInCentury(century.value).length)

function docCountInThisCentury(popeSlug: string): number {
  return documentCountForPopeInCentury(popeSlug, century.value)
}

const centuryYearRange = computed(() => {
  const start = (century.value - 1) * 100 + 1
  const end = century.value * 100
  return `${start}–${end}`
})

const CENTURY_BLURB: Record<number, string> = {
  21: '梵二後第二代教宗群：本篤十六世延續若望保祿二世神學遺產；方濟各以「整體生態學」與「對話」為主軸開啟新典範。',
  20: '梵二召開（1962-65）與其後續詮釋的世紀。社會訓導從《新事》接力寫到《在真理中實踐愛德》。若望保祿二世任內頒布 14 道通諭，是 19-21c 訓導文獻最豐沛的教宗。',
  19: '現代教廷通諭體裁奠基期。Pius IX 定義聖母無染原罪信理並召開梵一；Leo XIII《新事》1891 開啟近代天主教社會訓導傳統。',
}
const centuryBlurb = computed(() => CENTURY_BLURB[century.value] || '（待補）')
</script>
