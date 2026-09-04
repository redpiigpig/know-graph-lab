<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="台灣福音派研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣福音派研究資料</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          福音派系統的報刊與研究文獻。收這一批的理由是對照：福音派長期主張政教分離、
          不介入公共事務，卻在性別議題上高度動員——沒有這條線，第六章只會看到「宗教界的結盟」，
          看不到基督教內部的分裂。
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <NuxtLink to="/research-data/evangelical/ct" class="tool-card group border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
          <div class="tool-icon bg-orange-50 text-orange-600">🗞️</div>
          <div class="flex-1">
            <h2 class="tool-title">基督教論壇報</h2>
            <p class="tool-desc">1965 年創刊，福音派系統最主要的教派報紙；站上可回溯至 2019 年，與《台灣教會公報》同區段可逐年並排</p>
          </div>
          <span class="tool-badge bg-orange-50 text-orange-600">{{ ctCount ? `${ctCount.toLocaleString()} 篇` : '…' }}</span>
        </NuxtLink>

      </div>

      <p class="mt-6 text-xs text-gray-400 leading-relaxed">
        《華神期刊》（中華福音神學院）與校園書房出版社的《校園》雜誌篇目已改走華藝，
        收在<a href="/research-data/press" class="text-orange-600 hover:underline">期刊與報紙</a>那一層；
        校園書房自家網站只有商品頁、無全文，仍不收。
        待補：中原大學宗教研究所相關學位論文、
        護家盟與下一代幸福聯盟 2013–2018 的聲明文宣（多已下架，需走 Wayback）。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣福音派研究資料 — 論文資料整理' });

const ctCount = ref(0);

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/evangelical/ct-index.json');
    if (!r.ok) return;
    const d = await r.json() as { count: number }[];
    ctCount.value = d.reduce((s, x) => s + (x.count ?? 0), 0);
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
