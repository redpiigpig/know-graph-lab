<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="論文資料整理" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" :editable="false" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">論文資料整理</h1>
        <p class="text-gray-500 text-sm">依研究主題彙整田野訪談、檔案文獻、報刊史料與年表</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- 台灣衛理公會研究資料 -->
        <NuxtLink to="/research-data/taiwan-methodist" class="tool-card group border-teal-100 hover:border-teal-300 hover:shadow-teal-100">
          <div class="tool-icon bg-teal-50 text-teal-600">⛪</div>
          <div class="flex-1">
            <h2 class="tool-title">台灣衛理公會研究資料</h2>
            <p class="tool-desc">年議會大會名表、財產清冊、部會職員名單、龐君華牧師事工報告</p>
          </div>
          <span class="tool-badge bg-teal-50 text-teal-600">4 筆資料</span>
        </NuxtLink>

        <!-- 印順學派與弘誓研究資料 -->
        <NuxtLink to="/research-data/yinshun-hongshi" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="tool-icon bg-rose-50 text-rose-600">🪷</div>
          <div class="flex-1">
            <h2 class="tool-title">印順學派與弘誓研究資料</h2>
            <p class="tool-desc">弘誓學院／玄奘大學刊物典藏：弘誓雙月刊、學團日誌、玄奘佛學研究學報，與福嚴會訊</p>
          </div>
          <span class="tool-badge bg-rose-50 text-rose-600">4 類刊物</span>
        </NuxtLink>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '論文資料整理 — Know Graph Lab' });
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
