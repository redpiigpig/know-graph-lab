<template>
  <div v-if="creed" class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink to="/creeds" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ creed.nameZh }}</span>
      <span class="text-xs text-gray-400 ml-auto">{{ creed.year }}</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <!-- Header -->
      <header class="mb-8 border-b border-gray-200 pb-6">
        <div class="flex items-baseline gap-3 mb-2">
          <span v-if="creed.councilNo" class="font-mono text-stone-500 text-sm">第 {{ creed.councilNo }} 次大公會議</span>
          <span class="text-xs text-gray-400">{{ CATEGORY_LABEL_ZH[creed.category] }}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 leading-tight">{{ creed.nameZh }}</h1>
        <div class="text-sm text-gray-500 mt-1">{{ creed.nameEn }}</div>
        <div v-if="creed.nameLat" class="text-xs text-gray-400 italic mt-0.5">{{ creed.nameLat }}</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-5 text-sm">
          <div v-if="creed.location"><span class="text-gray-400">地點：</span><span class="text-gray-800">{{ creed.location }}</span></div>
          <div><span class="text-gray-400">年份：</span><span class="text-gray-800">{{ creed.year }}</span></div>
          <div v-if="creed.authors?.length" class="md:col-span-2"><span class="text-gray-400">主筆／簽署：</span><span class="text-gray-800">{{ creed.authors.join('、') }}</span></div>
          <div class="md:col-span-2"><span class="text-gray-400">主議題：</span><span class="text-gray-800">{{ creed.topic }}</span></div>
        </div>

        <!-- Traditions -->
        <div class="mt-5">
          <div class="text-xs text-gray-400 mb-1.5">接受傳統</div>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="t in creed.acceptedBy"
              :key="t"
              class="text-xs px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100"
            >{{ TRADITION_LABEL_ZH[t] }}</span>
          </div>
          <div v-if="creed.rejectedBy?.length" class="mt-2">
            <div class="text-xs text-gray-400 mb-1.5">不接受</div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="t in creed.rejectedBy"
                :key="t"
                class="text-xs px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-100"
              >{{ TRADITION_LABEL_ZH[t] }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Summary -->
      <section v-if="creed.summaryZh" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">📌 摘要</h2>
        <div class="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed bg-white p-4 rounded-lg border border-gray-200">{{ creed.summaryZh }}</div>
      </section>

      <!-- Versions: 中文 → 英文 → 原文 -->
      <section class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">📜 各版本對照</h2>

        <div class="space-y-3">
          <details
            v-for="(v, i) in sortedVersions"
            :key="`${v.lang}-${i}`"
            class="bg-white rounded-lg border border-gray-200 overflow-hidden"
            :open="i < 2"
          >
            <summary class="cursor-pointer px-4 py-3 hover:bg-stone-50 flex items-baseline gap-3 select-none">
              <span class="text-xs font-mono text-stone-500 uppercase">{{ v.lang }}</span>
              <span class="font-semibold text-gray-900 text-sm">{{ v.label }}</span>
              <span v-if="v.placeholder" class="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 ml-1">待補</span>
              <span class="text-xs text-gray-400 ml-auto">{{ LANG_LABEL_ZH[v.lang] }}</span>
            </summary>
            <div class="px-4 pb-4 pt-1 border-t border-gray-100">
              <pre class="whitespace-pre-wrap text-sm leading-relaxed text-gray-800 font-sans" :class="isOriginalScript(v.lang) ? 'font-serif text-[0.95rem]' : ''">{{ v.text }}</pre>
              <div v-if="v.source" class="text-xs text-gray-400 mt-3 pt-2 border-t border-gray-100">
                來源：{{ v.source }}<span v-if="v.translator"> ｜ 譯者：{{ v.translator }}</span>
              </div>
            </div>
          </details>
        </div>
      </section>

      <!-- Notes -->
      <section v-if="creed.notes" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">📝 歷史 Notes</h2>
        <div class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed bg-white p-4 rounded-lg border border-gray-200">{{ creed.notes }}</div>
      </section>

      <!-- Related -->
      <section v-if="relatedCreeds.length > 0" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">🔗 相關信條</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <NuxtLink
            v-for="r in relatedCreeds"
            :key="r.slug"
            :to="`/creeds/${r.slug}`"
            class="block bg-white border border-gray-200 rounded p-3 hover:border-stone-300 transition text-sm"
          >
            <div class="font-semibold text-gray-900">{{ r.nameZh }}</div>
            <div class="text-xs text-gray-500 mt-0.5">{{ r.year }} ｜ {{ r.nameEn }}</div>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="min-h-dvh flex items-center justify-center text-gray-400">
    找不到此信條：{{ route.params.slug }}
    <NuxtLink to="/creeds" class="ml-3 text-blue-500 underline">回信條列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { findCreed, ALL_CREEDS, CATEGORY_LABEL_ZH, TRADITION_LABEL_ZH, LANG_LABEL_ZH, type CreedLanguage, type CreedVersion } from '~/data/creeds'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const creed = computed(() => findCreed(route.params.slug as string))

useHead(() => ({
  title: creed.value ? `${creed.value.nameZh} — 信條對照` : '找不到信條',
}))

/**
 * 中文 → 英文 → 原文（user 確認 2026-05-21）
 * 中文內部排序：合一 / 聖公 / 信義 / 天主教 / 東正 / 改革宗 / 衛理 / 浸信 / 通用
 */
const ZH_ORDER: CreedLanguage[] = [
  'zh-Hant-Joint2019',
  'zh-Hant-Anglican',
  'zh-Hant-Lutheran',
  'zh-Hant-Catholic',
  'zh-Hant-Orthodox',
  'zh-Hant-Reformed',
  'zh-Hant-Methodist',
  'zh-Hant-Baptist',
  'zh-Hant-Protestant',
  'zh-Hant',
]

function langBucket(lang: CreedLanguage): number {
  if (lang.startsWith('zh-')) return 0
  if (lang === 'en') return 1
  // 原文（grc/lat/hye/cop/syr-east/syr-west/gez/arc/hbo/de/fr）
  return 2
}

function zhSubOrder(lang: CreedLanguage): number {
  const i = ZH_ORDER.indexOf(lang)
  return i === -1 ? 999 : i
}

const sortedVersions = computed<CreedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions].sort((a, b) => {
    const ba = langBucket(a.lang)
    const bb = langBucket(b.lang)
    if (ba !== bb) return ba - bb
    if (ba === 0) return zhSubOrder(a.lang) - zhSubOrder(b.lang)
    return 0
  })
})

const relatedCreeds = computed(() => {
  if (!creed.value?.related) return []
  return creed.value.related
    .map(slug => ALL_CREEDS.find(c => c.slug === slug))
    .filter((c): c is NonNullable<typeof c> => !!c)
})

function isOriginalScript(lang: CreedLanguage): boolean {
  return ['grc', 'lat', 'lat-filioque', 'hye', 'cop', 'cop-sa', 'syr-east', 'syr-west', 'gez', 'arc', 'hbo'].includes(lang)
}
</script>
