<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data" class="text-gray-400 hover:text-gray-700 transition text-sm">← 論文資料整理</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">台灣衛理公會研究資料</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣衛理公會研究資料</h1>
        <p class="text-gray-500 text-sm">彙整自《中華基督教衛理公會年議會大會會議紀錄》等公開出版品的史料表格</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <NuxtLink to="/research-data/taiwan-methodist/annual-conferences" class="tool-card group border-teal-100 hover:border-teal-300 hover:shadow-teal-100">
          <div class="tool-icon bg-teal-50 text-teal-600">📜</div>
          <div class="flex-1">
            <h2 class="tool-title">年議會歷屆大會名表</h2>
            <p class="tool-desc">1956–2023 共 84 筆，記錄屆次、地點、會期、主席與書記</p>
          </div>
          <span class="tool-badge bg-teal-50 text-teal-600">可用</span>
        </NuxtLink>

        <NuxtLink to="/research-data/taiwan-methodist/properties" class="tool-card group border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100">
          <div class="tool-icon bg-emerald-50 text-emerald-600">🏛️</div>
          <div class="flex-1">
            <h2 class="tool-title">財團法人財產清冊</h2>
            <p class="tool-desc">全台堂會、牧宅、神學院、福音園等不動產地號與面積</p>
          </div>
          <span class="tool-badge bg-emerald-50 text-emerald-600">可用</span>
        </NuxtLink>

        <NuxtLink to="/research-data/taiwan-methodist/committees" class="tool-card group border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
          <div class="tool-icon bg-indigo-50 text-indigo-600">👥</div>
          <div class="flex-1">
            <h2 class="tool-title">第 XX 屆年議會各部會職員名單</h2>
            <p class="tool-desc">第 56–59 屆（2019–2022）20 個部會主席、書記、委員等職員結構</p>
          </div>
          <span class="tool-badge bg-indigo-50 text-indigo-600">可用</span>
        </NuxtLink>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣衛理公會研究資料 — Know Graph Lab' });
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
