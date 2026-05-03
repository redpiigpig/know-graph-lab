<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-sm">← 返回主頁</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">寫作計畫</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-12">
      <div class="mb-10">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">寫作計畫</h1>
        <p class="text-sm text-gray-500">書寫計畫管理：構思中的書籍、讀書會影音逐字稿、章節草稿</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink to="/works/qiangmian" class="project-card border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
          <div class="project-icon bg-amber-50 text-amber-600">🌐</div>
          <div>
            <h2 class="project-title">千面上帝</h2>
            <p class="project-desc">探討世界宗教中神明概念的多元面貌，橫跨印度教、佛教、基督宗教、伊斯蘭教等傳統</p>
            <p class="text-xs text-amber-500 mt-2">宗教史讀書會逐字稿 · 書摘 · 章節構思</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '寫作計畫 — Know Graph Lab' })
</script>

<style scoped>
.project-card {
  @apply flex items-start gap-4 p-6 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline;
}
.project-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0;
}
.project-title {
  @apply text-sm font-semibold text-gray-900 mb-1;
}
.project-desc {
  @apply text-xs text-gray-500 leading-relaxed;
}
</style>
