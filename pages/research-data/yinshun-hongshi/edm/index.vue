<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/yinshun-hongshi" class="text-gray-400 hover:text-gray-700 transition text-sm">← 印順學派與弘誓研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">弘誓電子報</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700">研究資料</span>
          <span class="text-xs text-gray-400">佛教弘誓學院</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">弘誓電子報</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          弘誓學團電子報，刊載時事評論、活動預告與弘法動態。
          <span v-if="entries.length" class="text-gray-400">官網僅保留近期各期（第 {{ minN }}–{{ maxN }} 期），共 {{ entries.length }} 期；早期各期原站已不提供。</span>
        </p>
      </div>

      <div v-if="entries.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        <NuxtLink v-for="e in entries" :key="e.n"
          :to="`/research-data/yinshun-hongshi/edm/${e.n}`"
          class="block bg-white rounded-xl border border-gray-100 p-4 hover:border-indigo-200 hover:shadow-sm transition-all no-underline">
          <div class="flex items-baseline justify-between gap-2">
            <div class="text-sm font-bold text-gray-900">第 {{ e.n }} 期</div>
            <div v-if="e.date" class="text-xs text-gray-400">{{ e.date }}</div>
          </div>
          <div v-if="e.title" class="text-xs text-gray-600 mt-1 line-clamp-2 break-words">{{ e.title }}</div>
          <div class="text-[11px] text-indigo-600 mt-2">閱讀 →</div>
        </NuxtLink>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '弘誓電子報 — 印順學派與弘誓研究資料' });

interface Entry { n: number; date: string; title: string; chars: number }
const entries = ref<Entry[]>([]);
const loaded = ref(false);
const minN = computed(() => entries.value.length ? Math.min(...entries.value.map(e => e.n)) : 0);
const maxN = computed(() => entries.value.length ? Math.max(...entries.value.map(e => e.n)) : 0);

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/edm-index.json');
    if (r.ok) entries.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>

<style scoped>
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
