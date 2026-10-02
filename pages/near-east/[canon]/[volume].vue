<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="volume ? `${volume.sigil} ${volume.name}` : '古近東大藏經'"
      :back="{ to: canon ? `/near-east#${canon.key}` : '/near-east', label: '古近東大藏經' }"
      container-class="max-w-5xl"
    >
      <template #actions>
        <span v-if="volume" class="text-xs text-gray-400">{{ volumeTextCount(volume) }} 篇</span>
      </template>
    </AppHeader>

    <div v-if="!volume || !canon" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此卷。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8">
      <!-- 同藏卷次快速切換 -->
      <nav class="flex flex-wrap gap-1 mb-5">
        <NuxtLink
          v-for="v in canon.volumes"
          :key="v.key"
          :to="`/near-east/${canon.key}/${v.key}`"
          class="text-[11px] px-2 py-0.5 rounded border transition whitespace-nowrap"
          :class="v.key === volume.key ? 'bg-slate-900 text-teal-300 border-slate-900' : 'bg-white text-gray-600 border-gray-200 hover:border-teal-400'"
        >{{ v.sigil }} {{ v.name }}</NuxtLink>
      </nav>

      <!-- 卷首 -->
      <div class="mb-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="shrink-0 min-w-[3rem] h-12 px-2 rounded-xl bg-slate-900 text-teal-300 flex items-center justify-center text-base font-serif whitespace-nowrap">{{ volume.sigil }}</div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold text-gray-900 leading-tight break-words">{{ volume.name }}</h1>
            <div class="text-[11px] text-gray-400 break-words">{{ volume.name_en }}<span v-if="volume.era"> · {{ volume.era }}</span></div>
          </div>
        </div>

        <NuxtLink
          :to="`/near-east#${canon.key}`"
          class="inline-block text-[11px] px-2 py-0.5 rounded mb-3"
          :class="canon.scriptural ? 'bg-teal-50 text-teal-800' : 'bg-stone-100 text-stone-600'"
        >{{ canon.name }} · {{ canon.subtitle }}</NuxtLink>

        <div v-if="!canon.scriptural" class="mb-3 px-3 py-2.5 bg-stone-100 border border-stone-200 rounded-lg">
          <div class="text-[11px] font-semibold text-stone-800 mb-0.5">本卷不是古近東宗教的經典</div>
          <p class="text-[11px] text-stone-700 leading-relaxed break-words">
            這一藏是外人的記述：用希臘文替本國傳統作傳的祭司，以及希臘、羅馬、教父與伊斯蘭作者的轉述。
            引用前先問兩件事：作者讀得懂原文嗎？他是在描述，還是在用自己的神學詮釋？
          </p>
        </div>

        <p class="text-sm text-gray-600 leading-relaxed break-words">{{ volume.summary }}</p>
      </div>

      <!-- 各部 -->
      <section v-for="division in volume.divisions" :key="division.key" class="mb-8">
        <div class="flex items-baseline gap-2 mb-1 border-b border-teal-200 pb-1.5 flex-wrap">
          <h2 class="text-sm font-bold text-teal-900 break-words">{{ division.label }}</h2>
          <span v-if="division.label_en" class="text-[11px] text-gray-400 break-words">{{ division.label_en }}</span>
        </div>
        <p v-if="division.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 break-words">{{ division.desc }}</p>

        <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <article
            v-for="(text, i) in division.texts"
            :id="text.slug"
            :key="text.slug"
            class="px-4 py-3 scroll-mt-20"
            :class="[statusOf(text).rowCls, route.hash === `#${text.slug}` ? 'ring-2 ring-inset ring-teal-400' : '']"
          >
            <div class="flex items-start gap-3">
              <span class="shrink-0 text-[11px] font-mono text-gray-400 w-10 mt-0.5 tabular-nums">{{ numberOf(division, i) }}</span>
              <span class="shrink-0 inline-block w-2 h-2 rounded-full mt-1.5" :class="statusOf(text).dotCls" :title="statusOf(text).zh" />
              <div class="min-w-0 flex-1">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <NuxtLink v-if="hasText(text.slug)" :to="`/near-east/text/${text.slug}`" class="text-sm font-semibold break-words underline decoration-teal-300 underline-offset-2 hover:decoration-teal-600" :class="statusOf(text).titleCls">{{ text.title_zh }}</NuxtLink>
                  <span v-else class="text-sm font-semibold break-words" :class="statusOf(text).titleCls">{{ text.title_zh }}</span>
                  <span v-if="text.title_orig" class="text-[11px] text-gray-400 italic break-words">{{ text.title_orig }}</span>
                </div>
                <div class="flex flex-wrap items-center gap-1.5 mt-1">
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">{{ statusOf(text).zh }}</span>
                  <span v-if="text.siglum" class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono break-all">{{ text.siglum }}</span>
                  <span
                    v-for="c in COL_KEYS"
                    :key="c"
                    class="text-[10px] px-1 py-0.5 rounded font-mono"
                    :class="COLUMN_META[effectiveColumns(text, division, canon)[c]].cls"
                    :title="`${COL_LABEL[c]}：${COLUMN_META[effectiveColumns(text, division, canon)[c]].zh}`"
                  >{{ COL_SHORT[c] }}</span>
                </div>
                <p v-if="text.note" class="text-xs text-gray-600 leading-relaxed mt-1.5 break-words">{{ text.note }}</p>

                <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-0.5 mt-1.5 text-[11px] text-gray-500">
                  <div v-if="text.author" class="flex gap-2"><dt class="shrink-0 text-gray-400">作者</dt><dd class="break-words">{{ text.author }}</dd></div>
                  <div v-if="text.era" class="flex gap-2"><dt class="shrink-0 text-gray-400">成書</dt><dd class="break-words">{{ text.era }}</dd></div>
                  <div v-if="text.copies" class="flex gap-2"><dt class="shrink-0 text-gray-400">抄本</dt><dd class="break-words">{{ text.copies }}</dd></div>
                  <div v-if="text.language" class="flex gap-2"><dt class="shrink-0 text-gray-400">語言</dt><dd class="break-words">{{ text.language }}</dd></div>
                  <div v-if="text.provenance" class="flex gap-2"><dt class="shrink-0 text-gray-400">出土／館藏</dt><dd class="break-words">{{ text.provenance }}</dd></div>
                  <div v-if="text.extent" class="flex gap-2"><dt class="shrink-0 text-gray-400">篇幅</dt><dd class="break-words">{{ text.extent }}</dd></div>
                </dl>

                <p v-if="text.via" class="text-[11px] text-rose-700 leading-relaxed mt-1 break-words">僅存於：{{ text.via }}</p>
                <p v-if="text.bible" class="text-[11px] text-indigo-700 leading-relaxed mt-1 break-words">聖經對位：{{ text.bible }}</p>
                <div v-if="relatedOf(text).length" class="flex flex-wrap gap-1 mt-1.5">
                  <span class="text-[11px] text-gray-400">互見：</span>
                  <NuxtLink
                    v-for="r in relatedOf(text)"
                    :key="r.text.slug"
                    :to="`/near-east/${r.canon.key}/${r.volume.key}#${r.text.slug}`"
                    class="text-[11px] px-1.5 py-0.5 rounded bg-teal-50 text-teal-800 hover:bg-teal-100 break-words"
                  >{{ r.volume.sigil }}‧{{ r.text.title_zh }}</NuxtLink>
                </div>
                <p v-if="text.xref?.length" class="text-[11px] text-gray-400 leading-relaxed mt-1 break-words">站內他處：{{ text.xref.join('；') }}</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- 前後翻頁 -->
      <nav class="flex justify-between gap-3 mt-10 text-sm">
        <NuxtLink v-if="prev" :to="`/near-east/${canon.key}/${prev.key}`" class="min-w-0 truncate text-teal-800 hover:underline">← {{ prev.sigil }} {{ prev.name }}</NuxtLink>
        <span v-else />
        <NuxtLink v-if="next" :to="`/near-east/${canon.key}/${next.key}`" class="min-w-0 truncate text-teal-800 hover:underline text-right">{{ next.sigil }} {{ next.name }} →</NuxtLink>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { COLUMN_META, STATUS_META, effectiveColumns, findCanon, findVolume, hasText, relatedOf, volumeTextCount } from '~/data/near-east'
import type { NeDivision, NeText } from '~/data/near-east'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const canon = computed(() => findCanon(String(route.params.canon)))
const volume = computed(() => findVolume(String(route.params.canon), String(route.params.volume)))

useHead(() => ({ title: volume.value ? `${volume.value.sigil} ${volume.value.name} — 古近東大藏經` : '古近東大藏經' }))

const idx = computed(() => canon.value?.volumes.findIndex(v => v.key === volume.value?.key) ?? -1)
const prev = computed(() => (idx.value > 0 ? canon.value!.volumes[idx.value - 1] : undefined))
const next = computed(() => (canon.value && idx.value >= 0 && idx.value < canon.value.volumes.length - 1 ? canon.value.volumes[idx.value + 1] : undefined))

function statusOf(text: NeText) {
  // 不設 status＝綴合本，古近東大型文學作品的常態。
  return STATUS_META[text.status ?? 'composite']
}

/** 卷內連續編號，如「蘇一 7」。只供版面定位，不是引用號——引用請用學界編號。 */
function numberOf(division: NeDivision, i: number): number {
  if (!volume.value) return i + 1
  let n = 0
  for (const d of volume.value.divisions) {
    if (d.key === division.key) return n + i + 1
    n += d.texts.length
  }
  return i + 1
}

const COL_KEYS = ['orig', 'en', 'zh'] as const
const COL_SHORT = { orig: '原', en: '英', zh: '中' } as const
const COL_LABEL = { orig: '原文轉寫', en: '英譯', zh: '繁體中文' } as const
</script>
