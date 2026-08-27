<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="台灣基督長老教會研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣基督長老教會研究資料</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          長老教會系統的報刊與史料典藏，作為博士論文「台灣長老教會的公共神學發展」一章的史料底本：
          黃彰輝的實況化、宋泉盛的故事神學、王憲治的鄉土神學、黃伯和的出頭天神學，以及三大聲明以降的公共介入。
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <NuxtLink to="/research-data/pct/tcnn" class="tool-card group border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
          <div class="tool-icon bg-blue-50 text-blue-600">📰</div>
          <div class="flex-1">
            <h2 class="tool-title">台灣教會公報新聞網</h2>
            <p class="tool-desc">公報社新聞網逐篇全文，2010 年 12 月起至今；教會決議、社會議題發言與各中會動態的當代報導底本</p>
          </div>
          <span class="tool-badge bg-blue-50 text-blue-600">{{ tcnnCount ? `${tcnnCount} 篇` : '…' }}</span>
        </NuxtLink>

      </div>

      <p class="mt-6 text-xs text-gray-400 leading-relaxed">
        待補：《新使者》（PCT 焚而不燬站）、賴永祥台灣教會史料庫（王憲治、黃彰輝相關傳記與神學文章）。
        《台灣教會公報》1885–2007 掃描檔須向公報社去信索取；2008 至 2010 年間的期別目前無免費線上來源。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣基督長老教會研究資料 — 論文資料整理' });

const tcnnCount = ref(0);

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/pct/tcnn-index.json');
    if (!r.ok) return;
    const d = await r.json() as { count: number }[];
    tcnnCount.value = d.reduce((s, x) => s + (x.count ?? 0), 0);
  } catch { /* keep 0 */ }
});
</script>

<style scoped>
.tool-card {
  @apply relative flex items-start gap-4 p-5 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline;
}
.tool-icon {
  @apply w-11 h-11 rounded-xl flex items-center justify-center text-xl select-none flex-shrink-0;
}
.tool-title {
  @apply text-sm font-semibold text-gray-900 mb-0.5;
}
.tool-desc {
  @apply text-xs text-gray-500 leading-relaxed;
}
.tool-badge {
  @apply self-start text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0;
}
</style>
