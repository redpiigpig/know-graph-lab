<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-3xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/yinshun-hongshi/meeting" class="text-gray-400 hover:text-gray-700 transition text-sm">← 歷屆學術活動</NuxtLink>
      </div>
    </nav>
    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="item" class="mb-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-sky-100 text-sky-700">學術活動</span>
          <span v-if="item.year" class="text-xs text-gray-400">{{ item.year }}</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 leading-snug">{{ item.title }}</h1>
      </div>
      <div v-if="item" class="bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-10">
        <article class="whitespace-pre-wrap text-[15px] leading-loose text-gray-800">{{ item.text }}</article>
      </div>
      <div v-else-if="loaded" class="py-20 text-center text-sm text-gray-400">找不到此項目。</div>
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
interface Item { n: number; title: string; year: number; text: string }
const item = ref<Item | null>(null);
const loaded = ref(false);
useHead(() => ({ title: `${item.value?.title || '學術活動'} — 印順學派與弘誓研究資料` }));

onMounted(async () => {
  try {
    const r = await fetch(`/content/research-data/yinshun-hongshi/meeting/${n.value}.json`);
    if (r.ok) item.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
