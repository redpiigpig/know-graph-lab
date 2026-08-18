<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="希臘羅馬大藏經 · 搜尋" :back="{ to: '/hellenika', label: '希臘羅馬大藏經' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">全書 {{ corpusSize }} 種</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
      <div class="flex items-center gap-2 mb-6">
        <input
          v-model="q"
          type="search"
          autofocus
          placeholder="🔍 書名（中／原文）、作者、卷名、年代、地點…"
          class="flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400 focus:border-stone-400"
        />
      </div>

      <p v-if="!q.trim()" class="text-center text-gray-400 py-16 text-sm">輸入關鍵字開始搜尋。</p>
      <p v-else-if="!hits.length" class="text-center text-gray-400 py-16 text-sm">找不到「{{ q }}」。</p>

      <template v-else>
        <p class="text-xs text-gray-500 mb-3">「{{ q }}」共 {{ hits.length }} 筆</p>
        <ol class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <li v-for="(h, i) in hits" :key="i" :class="h.work.status ? STATUS_META[h.work.status].rowCls : ''">
            <NuxtLink
              :to="`/hellenika/${h.canon.key}/${h.volume.key}`"
              class="flex flex-col sm:flex-row gap-x-6 gap-y-1 px-4 py-3 hover:bg-slate-50/70 transition"
            >
              <div class="sm:w-2/5 sm:shrink-0">
                <div class="flex items-baseline gap-2">
                  <span class="inline-block w-2 h-2 rounded-full shrink-0" :class="STATUS_META[h.work.status || 'whole'].dotCls" />
                  <span class="text-sm font-medium break-words" :class="STATUS_META[h.work.status || 'whole'].titleCls">{{ h.work.title_zh }}</span>
                  <span v-if="h.work.track === 'latin'" class="shrink-0 px-1 rounded text-[10px] bg-stone-200 text-stone-700">續</span>
                </div>
                <div v-if="h.work.title_orig" class="ml-4 text-[11px] text-gray-400 italic leading-tight break-words">{{ h.work.title_orig }}</div>
                <div class="ml-4 mt-1 text-[11px] text-stone-500 flex flex-wrap gap-x-2">
                  <span v-if="h.work.author">{{ h.work.author }}</span>
                  <span v-if="h.work.era">{{ h.work.era }}</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-[11px] text-gray-400 mb-0.5">
                  {{ h.canon.name }} · <span class="font-serif">{{ h.volume.sigil }}</span> {{ h.volume.name }} · {{ h.divisionLabel }}
                </div>
                <div v-if="h.work.intro || h.work.note" class="text-[12px] text-gray-600 leading-relaxed line-clamp-3 break-words">{{ h.work.intro || h.work.note }}</div>
              </div>
            </NuxtLink>
          </li>
        </ol>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { searchWorks, allWorks, STATUS_META } from '~/data/hellenika'

definePageMeta({ middleware: 'auth' })
useHead({ title: '搜尋 · 希臘羅馬大藏經 — Know Graph Lab' })

const route = useRoute()
const q = ref(String(route.query.q ?? ''))
const hits = computed(() => searchWorks(q.value))
const corpusSize = allWorks().length

watch(q, v => {
  navigateTo({ query: v.trim() ? { q: v.trim() } : {} }, { replace: true })
})
</script>
