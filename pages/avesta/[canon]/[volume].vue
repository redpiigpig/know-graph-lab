<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="volume ? volume.name : '祆教經典'"
      :back="{ to: '/avesta', label: '祆教經典' }"
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
          <div class="shrink-0 w-12 h-12 rounded-xl bg-orange-800 text-white flex items-center justify-center text-2xl font-serif">{{ volume.sigil }}</div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold text-gray-900 leading-tight break-words">{{ volume.name }}</h1>
            <div class="text-[11px] text-gray-400 break-words">
              <span v-if="volume.name_orig" class="italic">{{ volume.name_orig }} · </span>{{ volume.name_en }}
            </div>
          </div>
        </div>

        <NuxtLink
          :to="`/avesta#${canon.key}`"
          class="inline-block text-[11px] px-2 py-0.5 rounded mb-3"
          :class="canon.scriptural ? 'bg-orange-50 text-orange-800' : 'bg-stone-100 text-stone-600'"
        >{{ canon.name }} · {{ canon.subtitle }}</NuxtLink>

        <!-- 非經典附錄的告示：讀者有權在讀之前就知道 -->
        <div v-if="!canon.scriptural" class="mb-3 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="text-[11px] font-semibold text-amber-900 mb-0.5">本卷非祆教經典</div>
          <p class="text-[11px] text-amber-800 leading-relaxed break-words">
            王室銘文是否屬於祆教文獻，學界至今無定論——它們敬拜阿胡拉‧馬茲達、以「真理對謊言」構築世界觀，
            卻從未提及查拉圖斯特拉，也不見迦薩的專門術語。收錄的理由是年代：這是這個信仰世界最早的、
            有確切紀年與具名作者的文字證據。閱讀時請記住，這些是國王的政治文告，不是祭司的禮儀文本。
          </p>
        </div>

        <p class="text-sm text-gray-600 leading-relaxed break-words mb-3">{{ volume.summary }}</p>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600">
          <div v-if="volume.liturgy" class="flex gap-2 sm:col-span-2">
            <dt class="shrink-0 text-gray-400">誦於</dt><dd class="break-words text-orange-800">{{ volume.liturgy }}</dd>
          </div>
          <div v-if="volume.era" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ volume.era }}</dd></div>
          <div v-if="volume.extent" class="flex gap-2"><dt class="shrink-0 text-gray-400">規模</dt><dd class="break-words">{{ volume.extent }}</dd></div>
        </dl>
      </div>

      <!-- 各部 -->
      <section v-for="division in volume.divisions" :key="division.key" class="mb-8">
        <div class="flex items-baseline gap-2 mb-1 border-b border-orange-200 pb-1.5">
          <h2 class="text-sm font-bold text-orange-900 break-words">{{ division.label }}</h2>
          <span v-if="division.label_en" class="text-[11px] text-gray-400 break-words">{{ division.label_en }}</span>
        </div>
        <p v-if="division.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 break-words">{{ division.desc }}</p>

        <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <NuxtLink
            v-for="text in division.texts"
            :key="text.slug"
            :to="`/avesta/text/${text.slug}`"
            class="flex items-start gap-3 px-4 py-2.5 hover:bg-slate-50 transition group"
            :class="statusOf(text).rowCls"
          >
            <span class="shrink-0 inline-block w-2 h-2 rounded-full mt-1.5" :class="statusOf(text).dotCls" />
            <span class="shrink-0 text-[11px] font-mono text-gray-400 w-14 mt-0.5 truncate">{{ text.siglum }}</span>
            <div class="min-w-0 flex-1">
              <div class="flex items-baseline gap-2 flex-wrap">
                <span class="text-sm font-medium group-hover:underline break-words" :class="statusOf(text).titleCls">{{ text.title_zh }}</span>
                <span v-if="text.title_orig" class="text-[11px] text-gray-400 italic break-words">{{ text.title_orig }}</span>
              </div>
              <p v-if="text.note" class="text-[11px] text-gray-500 leading-relaxed mt-0.5 break-words">{{ text.note }}</p>
              <p v-if="text.via" class="text-[11px] text-rose-700 leading-relaxed mt-0.5 break-words">僅存於：{{ text.via }}</p>
            </div>
            <div class="shrink-0 flex gap-1 mt-0.5">
              <span
                v-for="c in ['orig', 'en', 'zh'] as const"
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
import { COLUMN_META, STATUS_META, columnsOf, findCanon, findVolume, volumeTextCount } from '~/data/avesta'
import type { ZoroText } from '~/data/avesta'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const canon = computed(() => findCanon(String(route.params.canon)))
const volume = computed(() => findVolume(String(route.params.canon), String(route.params.volume)))

useHead(() => ({ title: volume.value ? `${volume.value.name} — 祆教經典` : '祆教經典' }))

function statusOf(text: ZoroText) {
  return STATUS_META[text.status ?? 'whole']
}

const COL_SHORT = { orig: '原', en: '英', zh: '中' } as const
const COL_LABEL = { orig: '原文轉寫', en: '英譯', zh: '繁體中文' } as const
</script>
