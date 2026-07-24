<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="學位論文" :back="{ to: '/writing', label: '學術活動紀錄' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-12">
      <div class="mb-10">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">學位論文</h1>
        <p class="text-sm text-gray-500">博士研究計畫、碩士論文與學士論文線上閱讀</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink to="/writing/doctoral-proposal" class="project-card border-amber-100 hover:border-amber-300 hover:shadow-amber-100 sm:col-span-2 lg:col-span-1">
          <div class="project-icon bg-amber-50 text-amber-600">📝</div>
          <div>
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <h2 class="project-title !mb-0">博士論文研究計畫</h2>
              <span class="text-[10px] font-medium rounded-full bg-amber-100 text-amber-700 px-2 py-0.5">第二版草案</span>
            </div>
            <p class="project-desc">入世轉向的兩條譜系：台灣人間佛教與以長老教會為核心之本土神學的歷史比較及神學比較</p>
            <p class="text-xs text-amber-600 mt-2">歷史學方法為主 · 八位核心人物 · 全文線上版</p>
            <p class="text-xs text-gray-400 mt-1">玄奘大學宗教與文化學系博士班</p>
          </div>
        </NuxtLink>

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
  @apply flex items-start gap-4 p-6 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline min-w-0;
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
