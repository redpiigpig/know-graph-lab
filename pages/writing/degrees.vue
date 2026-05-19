<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 學術活動紀錄</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">學位論文</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-12">
      <div class="mb-10">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">學位論文</h1>
        <p class="text-sm text-gray-500">碩士論文與學士論文全文寫作系統</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <NuxtLink to="/thesis" class="project-card border-purple-100 hover:border-purple-300 hover:shadow-purple-100">
          <div class="project-icon bg-purple-50 text-purple-600">🎓</div>
          <div>
            <h2 class="project-title">碩士論文</h2>
            <p class="project-desc">印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心</p>
            <p class="text-xs text-purple-500 mt-2">六章正文 · 附錄 · 口述訪談 · 徵引資料</p>
            <p class="text-xs text-gray-400 mt-1">國立臺北教育大學台灣文化研究所碩士班</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/bachelor" class="project-card border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
          <div class="project-icon bg-blue-50 text-blue-600">📖</div>
          <div>
            <h2 class="project-title">學士論文</h2>
            <p class="project-desc">福音派運動在台灣基督教中的起源與發展</p>
            <p class="text-xs text-blue-500 mt-2">六章正文 · 參考文獻 · 歷史年表</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '學位論文 — 學術活動紀錄' })
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
