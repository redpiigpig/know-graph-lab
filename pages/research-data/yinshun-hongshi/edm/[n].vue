<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-3xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/yinshun-hongshi/edm" class="text-gray-400 hover:text-gray-700 transition text-sm">← 弘誓電子報</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">第 {{ n }} 期</span>
      </div>
    </nav>

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="entry" class="mb-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700">弘誓電子報</span>
          <span class="text-xs text-gray-400">第 {{ entry.n }} 期<span v-if="entry.date"> · {{ entry.date }}</span></span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">弘誓電子報</h1>
      </div>

      <div v-if="entry" class="bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-10">
        <article class="whitespace-pre-wrap text-[15px] leading-loose text-gray-800">{{ entry.text }}</article>
      </div>
      <div v-else-if="loaded" class="py-20 text-center text-sm text-gray-400">找不到這一期。</div>
      <div v-else class="py-20 text-center text-sm text-gray-400">載入中…</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

definePageMeta({ middleware: 'auth' });

const route = useRoute();
const n = computed(() => parseInt(String(route.params.n)));
interface Entry { n: number; date: string; title: string; text: string }
const entry = ref<Entry | null>(null);
const loaded = ref(false);

useHead(() => ({ title: `弘誓電子報 第 ${n.value} 期 — 印順學派與弘誓研究資料` }));

onMounted(async () => {
  try {
    const r = await fetch(`/content/research-data/yinshun-hongshi/edm/${n.value}.json`);
    if (r.ok) entry.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
