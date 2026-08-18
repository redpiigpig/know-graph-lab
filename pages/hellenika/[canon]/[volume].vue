<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="volume ? `${volume.sigil}　${volume.name}` : '希臘羅馬大藏經'"
      :back="{ to: '/hellenika', label: '希臘羅馬大藏經' }"
      container-class="max-w-5xl"
    >
      <template #actions>
        <span v-if="volume" class="text-xs text-gray-400">{{ total }} 種</span>
      </template>
    </AppHeader>

    <div v-if="!canon || !volume" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此卷。</div>

    <div v-else class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <!-- 所屬藏 -->
      <div class="mb-3">
        <NuxtLink to="/hellenika" class="text-sm font-bold text-gray-700 hover:text-stone-600 transition">{{ canon.glyph }}　{{ canon.name }}</NuxtLink>
        <span class="text-xs text-gray-400 ml-2">{{ canon.subtitle }}</span>
      </div>

      <!-- 卷標頭 -->
      <div class="mb-5">
        <div class="flex items-center gap-3 mb-1.5">
          <div class="shrink-0 w-11 h-11 rounded-lg bg-stone-900 text-white flex items-center justify-center text-2xl font-serif">{{ volume.sigil }}</div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold text-gray-900 leading-tight break-words">{{ volume.name }}</h1>
            <div class="text-xs text-gray-400">{{ volume.name_en }}</div>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] mb-2">
          <span v-if="volume.parallel" class="px-2 py-0.5 rounded bg-stone-100 text-stone-700 font-serif">對位　{{ volume.parallel }}</span>
          <span v-if="volume.span" class="text-gray-500">{{ volume.span }}</span>
          <span
            v-if="volume.clock"
            class="px-2 py-0.5 rounded"
            :class="volume.clock === 'mythic' ? 'bg-amber-50 text-amber-700' : 'bg-sky-50 text-sky-700'"
          >{{ volume.clock === 'mythic' ? '神話內敘時間' : '按成書年代' }}</span>
        </div>
        <p class="text-xs text-gray-600 leading-relaxed">{{ volume.summary }}</p>
      </div>

      <!-- 同藏卷次快速切換 -->
      <div class="flex flex-wrap gap-1.5 mb-4">
        <NuxtLink
          v-for="v in canon.volumes"
          :key="v.key"
          :to="`/hellenika/${canon.key}/${v.key}`"
          class="px-2 py-1 rounded-lg text-xs border transition"
          :class="v.key === volume.key ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-400'"
          :title="v.name"
        >
          <span class="font-serif font-semibold">{{ v.sigil }}</span> {{ v.name }}
        </NuxtLink>
      </div>

      <!-- 本卷用到的狀態圖例 -->
      <div v-if="usedStatuses.length" class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-6 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
        <span class="text-gray-500">存世狀態：</span>
        <span v-for="s in usedStatuses" :key="s" class="flex items-center gap-1.5">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="STATUS_META[s].dotCls" />
          <span :class="STATUS_META[s].titleCls">{{ STATUS_META[s].zh }}</span>
        </span>
        <span v-if="hasLatin" class="flex items-center gap-1.5">
          <span class="px-1 rounded text-[10px] bg-stone-200 text-stone-700">續</span>
          <span class="text-stone-600">拉丁續典</span>
        </span>
      </div>

      <!-- 各部 -->
      <section v-for="d in volume.divisions" :key="d.key" class="mb-8">
        <div class="flex items-baseline gap-2 mb-1 border-b border-stone-300 pb-1.5">
          <h2 class="text-base font-bold text-stone-800">{{ d.label }}</h2>
          <span v-if="d.label_en" class="text-[11px] text-gray-400">{{ d.label_en }}</span>
          <span class="text-xs text-gray-400 ml-auto">{{ d.works.length }} 種</span>
        </div>
        <p v-if="d.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2">{{ d.desc }}</p>

        <ol class="divide-y divide-gray-100 border-x border-b border-gray-100 rounded-b-md">
          <li v-for="(w, i) in d.works" :key="i" :class="w.status ? STATUS_META[w.status].rowCls : ''">
            <component
              :is="w.link ? 'NuxtLink' : 'div'"
              :to="w.link || undefined"
              class="flex flex-col sm:flex-row gap-x-6 gap-y-1 px-3 py-2.5 transition"
              :class="w.link ? 'hover:bg-emerald-50/60 cursor-pointer' : 'hover:bg-slate-50/70'"
            >
              <!-- 左：標題與書目資料 -->
              <div class="sm:w-2/5 sm:shrink-0">
                <div class="flex items-baseline gap-2">
                  <span class="shrink-0 text-[11px] font-mono text-gray-300 tabular-nums">{{ runningNo(d, i) }}</span>
                  <span class="inline-block w-2 h-2 rounded-full shrink-0 translate-y-[-1px]" :class="STATUS_META[w.status || 'whole'].dotCls" />
                  <span class="text-sm font-medium break-words" :class="STATUS_META[w.status || 'whole'].titleCls">{{ w.title_zh }}</span>
                  <span v-if="w.track === 'latin'" class="shrink-0 px-1 rounded text-[10px] bg-stone-200 text-stone-700">續</span>
                </div>
                <div v-if="w.title_orig" class="ml-6 text-[11px] text-gray-400 italic leading-tight break-words">{{ w.title_orig }}</div>
                <div class="ml-6 mt-1 text-[11px] text-stone-500 leading-relaxed flex flex-wrap gap-x-2">
                  <span v-if="w.extent" class="text-gray-400">{{ w.extent }}</span>
                  <span v-if="w.author">{{ w.author }}</span>
                  <span v-if="w.era">{{ w.era }}</span>
                  <span v-if="w.place">{{ w.place }}</span>
                  <span v-if="w.language">{{ w.language }}</span>
                  <span v-if="w.link" class="text-emerald-600">對照 →</span>
                </div>
                <div v-if="w.via" class="ml-6 mt-0.5 text-[11px] text-rose-600/80 leading-relaxed break-words">轉引自：{{ w.via }}</div>
                <div v-if="w.seealso" class="ml-6 mt-0.5 text-[11px] text-gray-400 leading-relaxed break-words">互見：{{ w.seealso }}</div>
              </div>
              <!-- 右：簡介 -->
              <div v-if="w.intro || w.note" class="flex-1 min-w-0 text-[12px] text-gray-600 leading-relaxed break-words">
                <span v-if="w.intro && w.note" class="block text-gray-500 mb-0.5">{{ w.note }}</span>
                {{ w.intro || w.note }}
              </div>
            </component>
          </li>
        </ol>
      </section>

      <!-- 翻頁 -->
      <div class="flex items-center justify-between gap-3 border-t border-gray-200 pt-4">
        <NuxtLink
          v-if="prev"
          :to="`/hellenika/${canon.key}/${prev.key}`"
          class="text-xs text-gray-600 hover:text-stone-900 transition min-w-0 truncate"
        >← {{ prev.sigil }}　{{ prev.name }}</NuxtLink>
        <span v-else />
        <NuxtLink
          v-if="next"
          :to="`/hellenika/${canon.key}/${next.key}`"
          class="text-xs text-gray-600 hover:text-stone-900 transition min-w-0 truncate text-right"
        >{{ next.sigil }}　{{ next.name }} →</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  findCanon, findVolume, neighbours, volumeWorkCount, STATUS_META,
  type HellenDivision, type WorkStatus,
} from '~/data/hellenika'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const canonKey = computed(() => String(route.params.canon))
const volumeKey = computed(() => String(route.params.volume))

const canon = computed(() => findCanon(canonKey.value))
const volume = computed(() => findVolume(canonKey.value, volumeKey.value))
const total = computed(() => (volume.value ? volumeWorkCount(volume.value) : 0))
const { prev, next } = { prev: computed(() => neighbours(canonKey.value, volumeKey.value).prev), next: computed(() => neighbours(canonKey.value, volumeKey.value).next) }

const usedStatuses = computed<WorkStatus[]>(() => {
  const set = new Set<WorkStatus>()
  volume.value?.divisions.forEach(d => d.works.forEach(w => set.add(w.status || 'whole')))
  return (['whole', 'fragment', 'inscription', 'hostile'] as WorkStatus[]).filter(s => set.has(s))
})
const hasLatin = computed(() => !!volume.value?.divisions.some(d => d.works.some(w => w.track === 'latin')))

useHead(() => ({ title: `${volume.value ? volume.value.sigil + ' ' + volume.value.name : '希臘羅馬大藏經'} — Know Graph Lab` }))

/** 卷內連續編號，如 Α 1、Α 2… */
function runningNo(d: HellenDivision, i: number) {
  if (!volume.value) return ''
  let n = 0
  for (const div of volume.value.divisions) {
    if (div.key === d.key) return `${volume.value.sigil} ${n + i + 1}`
    n += div.works.length
  }
  return ''
}
</script>
