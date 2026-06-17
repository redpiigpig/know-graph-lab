<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="歷屆學術活動" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-sky-100 text-sky-700">研究資料</span>
          <span class="text-xs text-gray-400">弘誓學團／玄奘大學</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">歷屆學術活動</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          「印順導師思想之理論與實踐」國際學術會議歷屆、「宗教文化與性別倫理」國際會議、動物倫理與入世佛教等研討會之公告、徵稿與議程。
          <span v-if="items.length" class="text-gray-400">共 {{ items.length }} 項。</span>
        </p>
      </div>

      <div v-if="items.length" class="space-y-2">
        <NuxtLink v-for="it in items" :key="it.n"
          :to="`/research-data/yinshun-hongshi/meeting/${it.n}`"
          class="block bg-white rounded-xl border border-gray-100 p-4 hover:border-sky-200 hover:shadow-sm transition-all no-underline">
          <div class="flex items-baseline gap-2">
            <span v-if="it.year" class="text-xs text-sky-600 font-medium flex-shrink-0">{{ it.year }}</span>
            <span class="text-sm text-gray-800 break-words">{{ it.title }}</span>
          </div>
        </NuxtLink>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '歷屆學術活動 — 印順學派與弘誓研究資料' });

interface Item { n: number; title: string; year: number; chars: number }
const items = ref<Item[]>([]);
const loaded = ref(false);

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/meeting-index.json');
    if (r.ok) items.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
