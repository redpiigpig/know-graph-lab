<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="實驗網站" :back="{ to: '/', label: '返回主頁' }" :editable="false" />

    <div class="max-w-7xl mx-auto px-6 py-10">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-0.5">實驗網站</h1>
        <p class="text-gray-500 text-sm">客製化專屬研究網站的展示模板，可依需求替換主題與內容</p>
      </div>

      <!-- 子站卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

        <!-- 玄奘佛學研究 -->
        <NuxtLink to="/Hsuan_Chuang_Studies" class="tool-card group border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
          <div class="tool-icon bg-orange-50 text-orange-500">🪷</div>
          <div class="flex-1">
            <h2 class="tool-title">玄奘佛學研究</h2>
            <p class="tool-desc">玄奘大學佛學期刊網站範本，含投稿、編輯、審查流程介紹</p>
          </div>
          <span class="tool-badge bg-orange-50 text-orange-500">示範</span>
        </NuxtLink>

        <!-- 龐君華會督文集典藏 -->
        <NuxtLink to="/pong-archive" class="tool-card group border-stone-200 hover:border-stone-400 hover:shadow-stone-100">
          <div class="tool-icon bg-stone-50 text-stone-600">✝️</div>
          <div class="flex-1">
            <h2 class="tool-title">龐君華會督文集典藏</h2>
            <p class="tool-desc">講道、著作、訪談、三讀三禱等龐會督事奉資料的數位典藏與校對協作平台</p>
          </div>
          <span class="tool-badge bg-stone-50 text-stone-600">示範</span>
        </NuxtLink>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const user = useSupabaseUser();
useHead({ title: "實驗網站 — Know Graph Lab" });
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
