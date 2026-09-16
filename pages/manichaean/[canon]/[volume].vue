<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="volume ? volume.name : '摩尼教經典'"
      :back="{ to: '/manichaean', label: '摩尼教經典' }"
      container-class="max-w-5xl"
    >
      <template #actions>
        <span v-if="volume" class="text-xs text-gray-400">{{ volumeTextCount(volume) }} 篇</span>
      </template>
    </AppHeader>

    <div v-if="!volume || !canon" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此卷。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <!-- 卷首 -->
      <div class="mb-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="shrink-0 w-12 h-12 rounded-xl bg-slate-900 text-amber-300 flex items-center justify-center text-xl font-serif">{{ volume.sigil }}</div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold text-gray-900 leading-tight break-words">{{ volume.name }}</h1>
            <div class="text-[11px] text-gray-400 break-words">
              <span v-if="volume.name_orig" class="italic">{{ volume.name_orig }} · </span>{{ volume.name_en }}
            </div>
          </div>
        </div>

        <NuxtLink
          :to="`/manichaean#${canon.key}`"
          class="inline-block text-[11px] px-2 py-0.5 rounded mb-3"
          :class="canon.scriptural ? 'bg-amber-50 text-amber-800' : 'bg-stone-100 text-stone-600'"
        >{{ canon.name }} · {{ canon.subtitle }}</NuxtLink>

        <!-- 敵證藏的告示：讀者有權在讀之前就知道這不是摩尼教的經 -->
        <div v-if="!canon.scriptural" class="mb-3 px-3 py-2.5 bg-red-50 border border-red-200 rounded-lg">
          <div class="text-[11px] font-semibold text-red-900 mb-0.5">本卷不是摩尼教經典</div>
          <p class="text-[11px] text-red-800 leading-relaxed break-words">
            這一藏裡沒有一個字是摩尼教徒寫的——全部出自反對者的駁論、帝國的查禁法令與外部著錄。
            收錄有兩個理由：1904 年吐魯番殘卷出土之前，全世界對摩尼教的認識百分之百來自這一批；
            而且摩尼親撰七經今日僅存的若干段落，就夾在這些駁論的引文裡。
            <b>引用前請先看每一條的敵證等級</b>：逐句引錄的可當原話用，轉述的只能當大意，
            敵意框架的只能當「反對者如何理解」的證據。
          </p>
        </div>

        <!-- 漢文藏的告示：單欄呈現 -->
        <div v-if="canon.key === 'chinese'" class="mb-3 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="text-[11px] font-semibold text-amber-900 mb-0.5">本藏原文即中文，單欄呈現</div>
          <p class="text-[11px] text-amber-800 leading-relaxed break-words">
            其餘各藏是「原文轉寫／英譯／繁中」三欄對照，本藏不是——這些文獻本來就是漢文寫的。
            正文原樣呈現，不另譯成現代中文（那不是對照，是改寫），需要幫助的地方以註解處理。
          </p>
        </div>

        <p class="text-sm text-gray-600 leading-relaxed break-words mb-3">{{ volume.summary }}</p>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600">
          <div v-if="volume.provenance" class="flex gap-2 sm:col-span-2">
            <dt class="shrink-0 text-gray-400">出土／館藏</dt><dd class="break-words text-amber-800">{{ volume.provenance }}</dd>
          </div>
          <div v-if="volume.era" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ volume.era }}</dd></div>
          <div v-if="volume.extent" class="flex gap-2"><dt class="shrink-0 text-gray-400">規模</dt><dd class="break-words">{{ volume.extent }}</dd></div>
        </dl>
      </div>

      <!-- 各部 -->
      <section v-for="division in volume.divisions" :key="division.key" class="mb-8">
        <div class="flex items-baseline gap-2 mb-1 border-b border-amber-200 pb-1.5">
          <h2 class="text-sm font-bold text-amber-900 break-words">{{ division.label }}</h2>
          <span v-if="division.label_en" class="text-[11px] text-gray-400 break-words">{{ division.label_en }}</span>
        </div>
        <p v-if="division.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 break-words">{{ division.desc }}</p>

        <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <NuxtLink
            v-for="text in division.texts"
            :key="text.slug"
            :to="`/manichaean/text/${text.slug}`"
            class="flex items-start gap-3 px-4 py-2.5 hover:bg-slate-50 transition group"
            :class="statusOf(text).rowCls"
          >
            <span class="shrink-0 inline-block w-2 h-2 rounded-full mt-1.5" :class="statusOf(text).dotCls" />
            <span class="shrink-0 text-[11px] font-mono text-gray-400 w-24 mt-0.5 truncate" :title="text.siglum">{{ text.siglum }}</span>
            <div class="min-w-0 flex-1">
              <div class="flex items-baseline gap-2 flex-wrap">
                <span class="text-sm font-medium group-hover:underline break-words" :class="statusOf(text).titleCls">{{ text.title_zh }}</span>
                <span v-if="text.title_orig" class="text-[11px] text-gray-400 italic break-words">{{ text.title_orig }}</span>
                <span
                  v-if="text.hostile"
                  class="text-[10px] px-1.5 py-0.5 rounded"
                  :class="HOSTILE_META[text.hostile].cls"
                  :title="HOSTILE_META[text.hostile].desc"
                >{{ HOSTILE_META[text.hostile].zh }}</span>
              </div>
              <p v-if="text.note" class="text-[11px] text-gray-500 leading-relaxed mt-0.5 break-words">{{ text.note }}</p>
              <p v-if="text.via" class="text-[11px] text-rose-700 leading-relaxed mt-0.5 break-words">僅存於：{{ text.via }}</p>
              <p v-if="text.provenance" class="text-[11px] text-gray-400 leading-relaxed mt-0.5 break-words">{{ text.provenance }}</p>
            </div>
            <div class="shrink-0 flex gap-1 mt-0.5">
              <span
                v-for="c in colKeys"
                :key="c"
                class="text-[10px] px-1 py-0.5 rounded font-mono"
                :class="COLUMN_META[columnsOf(text, division)[c]].cls"
                :title="`${COL_LABEL[c]}：${COLUMN_META[columnsOf(text, division)[c]].zh}`"
              >{{ COL_SHORT[c] }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { COLUMN_META, HOSTILE_META, STATUS_META, columnsOf, findCanon, findVolume, volumeTextCount } from '~/data/manichaean'
import type { ManiText } from '~/data/manichaean'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const canon = computed(() => findCanon(String(route.params.canon)))
const volume = computed(() => findVolume(String(route.params.canon), String(route.params.volume)))

useHead(() => ({ title: volume.value ? `${volume.value.name} — 摩尼教經典` : '摩尼教經典' }))

function statusOf(text: ManiText) {
  // 本藏經的常態不是全本：不設 status 時預設殘篇，不預設全本。
  return STATUS_META[text.status ?? 'fragment']
}

const COL_SHORT = { orig: '原', en: '英', zh: '中' } as const
const COL_LABEL = { orig: '原文轉寫', en: '英譯', zh: '繁體中文' } as const

// 漢文藏原文即中文，不出「中」那一格——那一格會與「原」重複。
const colKeys = computed<Array<'orig' | 'en' | 'zh'>>(() =>
  canon.value?.key === 'chinese' ? ['orig', 'en'] : ['orig', 'en', 'zh'])
</script>
