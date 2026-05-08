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
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">研究資料</span>
          <span class="text-xs text-gray-400">建置中</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣衛理公會研究資料</h1>
        <p class="text-gray-500 text-sm">彙整台灣衛理公會的歷史檔案、人物、口述訪談與年表</p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-100 p-10 text-center text-gray-400 text-sm">
        尚未加入資料。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣衛理公會研究資料 — Know Graph Lab' });
</script>
