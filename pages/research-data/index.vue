<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="論文資料整理" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" />

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
        <NuxtLink to="/research-data/evangelical" class="tool-card group border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
          <div class="tool-icon bg-orange-50 text-orange-600">🗞️</div>
          <div class="flex-1">
            <h2 class="tool-title">台灣福音派研究資料</h2>
            <p class="tool-desc">基督教論壇報等福音派報刊；長老教會公共神學的對照面，用來看基督教內部的分裂</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/research-data/mukyokai" class="tool-card group border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100">
          <div class="tool-icon bg-emerald-50 text-emerald-600">📄</div>
          <div class="flex-1">
            <h2 class="tool-title">無教會主義研究資料</h2>
            <p class="tool-desc">內村鑑三、矢內原忠雄一系的研究文獻與史料；日治時期台灣教會經驗與無教會在台活動</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/research-data/corpus" class="tool-card group border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
          <div class="tool-icon bg-amber-50 text-amber-600">📈</div>
          <div class="flex-1">
            <h2 class="tool-title">語料層：關鍵詞年表</h2>
            <p class="tool-desc">跨佛教／基督教刊物比對同一個詞的出現年代與消長，附脈絡取樣；概念史那一章的證據來源</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/research-data/pct" class="tool-card group border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
          <div class="tool-icon bg-blue-50 text-blue-600">⛪</div>
          <div class="flex-1">
            <h2 class="tool-title">台灣基督長老教會研究資料</h2>
            <p class="tool-desc">台灣教會公報新聞網逐篇全文；黃彰輝、宋泉盛、王憲治、黃伯和一線本土神學與教會公共介入的史料</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/research-data/yinshun-hongshi" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="tool-icon bg-rose-50 text-rose-600">🪷</div>
          <div class="flex-1">
            <h2 class="tool-title">印順學派與弘誓研究資料</h2>
            <p class="tool-desc">弘誓學院／玄奘大學典藏：弘誓雙月刊、學團日誌、玄奘佛學研究學報、歷屆學術活動，與福嚴會訊</p>
          </div>
          <span class="tool-badge bg-rose-50 text-rose-600">5 類資料</span>
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
