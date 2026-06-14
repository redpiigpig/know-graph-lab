<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/yinshun-hongshi" class="text-gray-400 hover:text-gray-700 transition text-sm">← 印順學派與弘誓研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">學團日誌</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">研究資料</span>
          <span class="text-xs text-gray-400">佛教弘誓學院</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">學團日誌</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          弘誓學團逐期紀事，記錄法會、學術會議、社運參與、訪賓接待與院務大事；每期約涵蓋兩個月。
          <span v-if="entries.length" class="text-gray-400">收錄第 {{ minN }}–{{ maxN }} 期，共 {{ entries.length }} 則。</span>
        </p>
      </div>

      <div v-if="entries.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        <NuxtLink v-for="e in entries" :key="e.n"
          :to="`/research-data/yinshun-hongshi/log/${e.n}`"
          class="block bg-white rounded-xl border border-gray-100 p-4 hover:border-amber-200 hover:shadow-sm transition-all no-underline">
          <div class="text-sm font-bold text-gray-900">第 {{ e.n }} 期</div>
          <div class="text-xs text-gray-500 mt-0.5">{{ e.range }}</div>
          <div class="text-[11px] text-amber-600 mt-2">閱讀紀事 →</div>
        </NuxtLink>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '學團日誌 — 印順學派與弘誓研究資料' });

interface Entry { n: number; range: string; chars: number }
const entries = ref<Entry[]>([]);
const loaded = ref(false);
const minN = computed(() => entries.value.length ? Math.min(...entries.value.map(e => e.n)) : 0);
const maxN = computed(() => entries.value.length ? Math.max(...entries.value.map(e => e.n)) : 0);

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/log-index.json');
    if (r.ok) entries.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
