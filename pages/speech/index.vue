<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 學術活動紀錄</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">演講活動</span>
      </div>
    </nav>

    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-rose-100 text-rose-700">演講活動</span>
          <span class="text-xs text-gray-400">張辰瑋</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-4">受邀演講 · 學系專題 · 公開講座</h1>
        <div class="text-sm text-gray-500">
          <span><span class="font-semibold text-gray-800">{{ store.sorted.length }}</span> 場演講</span>
        </div>
      </div>
    </div>

    <div class="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <NuxtLink
        v-for="t in store.sorted" :key="t.id"
        :to="`/speech/${t.id}`"
        class="block bg-white rounded-2xl border border-gray-100 p-6 transition-all hover:border-rose-200 hover:shadow-sm"
      >
        <div class="flex flex-wrap items-start justify-between gap-3 mb-3">
          <div class="flex flex-wrap gap-1.5">
            <span :class="catStyle(t.category)" class="text-xs font-medium px-2 py-0.5 rounded-full">{{ catLabel(t.category) }}</span>
            <span v-if="t.hasTranscript" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">逐字稿</span>
            <span v-if="t.pptR2Key" class="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">投影片</span>
          </div>
          <span class="text-xs text-gray-500">{{ formatDate(t.date) }}<span v-if="t.duration" class="ml-1">‧ {{ t.duration }}</span></span>
        </div>
        <h2 class="text-base font-bold text-gray-900 mb-1 leading-snug">{{ t.title }}</h2>
        <p v-if="t.subtitle" class="text-sm text-gray-600 mb-3">── {{ t.subtitle }}</p>
        <p v-if="t.description" class="text-xs text-gray-500 leading-relaxed mb-3 line-clamp-2">{{ t.description }}</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-0.5 text-xs text-gray-500">
          <span class="sm:col-span-2"><span class="text-gray-400">場地　</span>{{ t.venue }}</span>
          <span><span class="text-gray-400">主辦　</span>{{ t.organizer }}</span>
          <span v-if="t.course"><span class="text-gray-400">課程　</span>{{ t.course }}</span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSpeechStore, type TalkCategory } from '~/stores/speech'

useHead({ title: '演講活動 — 學術活動紀錄' })

const store = useSpeechStore()

function catLabel(c: TalkCategory) {
  return ({
    lecture: '學系專題講座',
    seminar: '研討會專題',
    public: '公開講座',
    invited: '受邀演講',
    panel: '論壇與談',
  } as Record<TalkCategory, string>)[c]
}
function catStyle(c: TalkCategory) {
  return ({
    lecture: 'bg-rose-50 text-rose-700',
    seminar: 'bg-indigo-50 text-indigo-700',
    public: 'bg-emerald-50 text-emerald-700',
    invited: 'bg-purple-50 text-purple-700',
    panel: 'bg-amber-50 text-amber-700',
  } as Record<TalkCategory, string>)[c]
}
function formatDate(d: string) {
  const [y, m, day] = d.split('-')
  return `${y} 年 ${parseInt(m)} 月 ${parseInt(day)} 日`
}
</script>
