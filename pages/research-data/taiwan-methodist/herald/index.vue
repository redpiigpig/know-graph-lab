<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="衛報" :back="{ to: '/research-data/taiwan-methodist', label: '台灣衛理公會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣衛理公會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">衛報 Wesleyan News</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          中華基督教衛理公會衛蘭中心發行的華文刊物。掃描原件以翻頁書形式呈現，並可下載原始 PDF。
          <span class="text-gray-400">目前收錄 {{ issues.length }} 期（2001–2003）。</span>
        </p>
      </div>

      <div v-if="issues.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <NuxtLink
          v-for="it in issues"
          :key="it.issue"
          :to="`/research-data/taiwan-methodist/herald/${it.issue}`"
          class="issue-card group"
        >
          <div class="aspect-[3/4] w-full overflow-hidden rounded-t-xl bg-gray-100">
            <img
              :src="`/herald/${it.issue}/page-01.jpg`"
              :alt="`衛報第 ${it.issue} 期封面`"
              loading="lazy"
              class="w-full h-full object-cover object-top group-hover:scale-[1.03] transition-transform duration-300"
            />
          </div>
          <div class="p-4 border border-t-0 border-gray-100 rounded-b-xl bg-white">
            <div class="flex items-center justify-between">
              <div class="text-xs text-gray-400">第 {{ it.issue }} 期 · {{ it.date_display }}</div>
              <a
                :href="`/api/herald/${it.issue}/pdf?download=1`"
                @click.stop
                class="text-gray-300 hover:text-purple-600 transition"
                title="下載原始掃描 PDF"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/></svg>
              </a>
            </div>
            <div class="text-sm font-semibold text-gray-800 mt-0.5 line-clamp-1">{{ it.title || '本期' }}</div>
            <div class="text-[11px] text-gray-500 mt-1">{{ it.page_count }} 頁 · 翻頁瀏覽</div>
          </div>
        </NuxtLink>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">載入中…</div>

      <div class="mt-12 p-4 rounded-xl bg-white border border-gray-100 text-xs text-gray-500 leading-relaxed">
        各期掃描原件以翻頁電子書方式呈現；第 55 期另附逐頁結構化純文字。原始 PDF 典藏於 Cloudflare R2，可於每期右上角或卡片下載。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '衛報 — 台灣衛理公會研究資料' });

interface IssueMeta {
  issue: number;
  date_display: string;
  title: string;
  page_count: number;
  mode: 'scan' | 'text';
}
const issues = ref<IssueMeta[]>([]);

onMounted(async () => {
  try {
    const res = await fetch('/herald/index.json');
    if (res.ok) issues.value = await res.json();
  } catch { /* leave empty → loading state */ }
});
</script>

<style scoped>
.issue-card {
  @apply block no-underline transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg rounded-xl overflow-hidden;
}
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
