<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="印順學派與弘誓研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">印順學派與弘誓研究資料</h1>
        <p class="text-gray-500 text-sm">佛教弘誓學院（昭慧法師、性廣法師創辦）刊物與福嚴佛學院會訊之數位典藏，作為《當代的大愛道革命》研究背景史料</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <NuxtLink to="/research-data/yinshun-hongshi/magazine" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="tool-icon bg-rose-50 text-rose-600">📕</div>
          <div class="flex-1">
            <h2 class="tool-title">弘誓雙月刊</h2>
            <p class="tool-desc">佛教弘誓學院機關刊物，收錄昭慧、性廣法師論述與學團紀實；每期整本掃描 PDF</p>
          </div>
          <span class="tool-badge bg-rose-50 text-rose-600">{{ magCount || '…' }} 期</span>
        </NuxtLink>

        <NuxtLink to="/research-data/yinshun-hongshi/log" class="tool-card group border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
          <div class="tool-icon bg-amber-50 text-amber-600">📓</div>
          <div class="flex-1">
            <h2 class="tool-title">學團日誌</h2>
            <p class="tool-desc">弘誓學團逐期紀事，記錄法會、學術會議、社運參與、訪賓與院務大事</p>
          </div>
          <span class="tool-badge bg-amber-50 text-amber-600">{{ logCount || '…' }} 則</span>
        </NuxtLink>

        <NuxtLink v-if="meetCount" to="/research-data/yinshun-hongshi/meeting" class="tool-card group border-sky-100 hover:border-sky-300 hover:shadow-sky-100">
          <div class="tool-icon bg-sky-50 text-sky-600">🎙️</div>
          <div class="flex-1">
            <h2 class="tool-title">歷屆學術活動</h2>
            <p class="tool-desc">「印順導師思想之理論與實踐」國際學術會議歷屆，及性別倫理、動物倫理等研討會公告／徵稿／議程</p>
          </div>
          <span class="tool-badge bg-sky-50 text-sky-600">{{ meetCount || '…' }} 項</span>
        </NuxtLink>

        <NuxtLink to="/research-data/yinshun-hongshi/xuanzang" class="tool-card group border-violet-100 hover:border-violet-300 hover:shadow-violet-100">
          <div class="tool-icon bg-violet-50 text-violet-600">🎓</div>
          <div class="flex-1">
            <h2 class="tool-title">玄奘佛學研究學報</h2>
            <p class="tool-desc">玄奘大學宗教與文化學系學術期刊，每篇論文全文；昭慧、性廣等學者人間佛教研究重鎮</p>
          </div>
          <span class="tool-badge bg-violet-50 text-violet-600">{{ xzCount || '…' }} 期</span>
        </NuxtLink>

        <NuxtLink to="/research-data/yinshun-hongshi/fuyan" class="tool-card group border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100">
          <div class="tool-icon bg-emerald-50 text-emerald-600">📗</div>
          <div class="flex-1">
            <h2 class="tool-title">福嚴會訊</h2>
            <p class="tool-desc">福嚴佛學院（印順導師創辦）會訊，印順學脈絡的教育與弘法記錄</p>
          </div>
          <span class="tool-badge bg-emerald-50 text-emerald-600">{{ fuyanCount || '…' }} 期</span>
        </NuxtLink>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '印順學派與弘誓研究資料 — 論文資料整理' });

const magCount = ref(0);
const logCount = ref(0);
const fuyanCount = ref(0);
const xzCount = ref(0);
const meetCount = ref(0);

async function count(url: string): Promise<number> {
  try {
    const r = await fetch(url);
    if (!r.ok) return 0;
    const d = await r.json();
    return Array.isArray(d) ? d.length : 0;
  } catch { return 0; }
}

onMounted(async () => {
  const base = '/content/research-data/yinshun-hongshi';
  magCount.value = await count(`${base}/magazine-index.json`);
  logCount.value = await count(`${base}/log-index.json`);
  fuyanCount.value = await count(`${base}/fuyan-index.json`);
  xzCount.value = await count(`${base}/xuanzang-index.json`);
  meetCount.value = await count(`${base}/meeting-index.json`);
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
