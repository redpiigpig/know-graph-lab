<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader :title="`第 ${n} 期`" :back="{ to: '/research-data/yinshun-hongshi/log', label: '學團日誌' }" container-class="max-w-3xl" />

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="entry" class="mb-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">學團日誌</span>
          <span class="text-xs text-gray-400">第 {{ entry.n }} 期 · {{ entry.range }}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">弘誓學團日誌</h1>
      </div>

      <div v-if="entry" class="bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-10">
        <article class="log-prose whitespace-pre-wrap text-[15px] leading-loose text-gray-800">{{ entry.text }}</article>
      </div>
      <div v-else-if="loaded" class="py-20 text-center text-sm text-gray-400">找不到這一期。</div>
      <div v-else class="py-20 text-center text-sm text-gray-400">載入中…</div>

      <div v-if="entry" class="mt-6 flex items-center justify-between text-sm">
        <NuxtLink v-if="hasNewer" :to="`/research-data/yinshun-hongshi/log/${n + 1}`" class="text-amber-700 hover:underline">← 較新一期</NuxtLink>
        <span v-else></span>
        <NuxtLink v-if="n > 1" :to="`/research-data/yinshun-hongshi/log/${n - 1}`" class="text-amber-700 hover:underline">較舊一期 →</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

definePageMeta({ middleware: 'auth' });

const route = useRoute();
const n = computed(() => parseInt(String(route.params.n)));
interface Entry { n: number; range: string; text: string }
const entry = ref<Entry | null>(null);
const loaded = ref(false);
const hasNewer = ref(false);

useHead(() => ({ title: `學團日誌 第 ${n.value} 期 — 印順學派與弘誓研究資料` }));

onMounted(async () => {
  try {
    const r = await fetch(`/content/research-data/yinshun-hongshi/log/${n.value}.json`);
    if (r.ok) entry.value = await r.json();
    const idx = await fetch('/content/research-data/yinshun-hongshi/log-index.json');
    if (idx.ok) { const list: Entry[] = await idx.json(); hasNewer.value = list.some(e => e.n === n.value + 1); }
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
