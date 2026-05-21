<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist" class="text-gray-400 hover:text-gray-700 transition text-sm">← 台灣衛理公會研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">衛理報</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣衛理公會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">衛理報 Wesleyan News</h1>
        <p class="text-sm text-gray-500">中華基督教衛理公會衛蘭中心發行的華文刊物。掃描原件以翻頁書形式呈現。</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">

        <NuxtLink to="/research-data/taiwan-methodist/herald/55" class="issue-card group">
          <div class="aspect-[3/4] w-full overflow-hidden rounded-t-xl"
               :style="{ background: 'linear-gradient(90deg, #8b7c97 0 28%, #ffffff 28% 100%)' }">
            <div class="h-full flex flex-col px-5 pt-6 pb-4">
              <div class="font-serif text-3xl text-white tracking-widest leading-none">衛報</div>
              <div class="text-[10px] italic text-gray-700 mt-12 ml-[28%]">Wesleyan News</div>
              <div class="mt-auto ml-[28%]">
                <div class="text-[10px] text-gray-500">2002/11/30</div>
                <div class="text-sm font-bold text-gray-800">No.55</div>
              </div>
            </div>
          </div>
          <div class="p-4 border border-t-0 border-gray-100 rounded-b-xl bg-white">
            <div class="text-xs text-gray-400">第 55 期 · 2002/11/30</div>
            <div class="text-sm font-semibold text-gray-800 mt-0.5">將臨節第一主日</div>
            <div class="text-[11px] text-gray-500 mt-1">24 頁 · 翻頁瀏覽</div>
          </div>
        </NuxtLink>

      </div>

      <div class="mt-12 p-4 rounded-xl bg-white border border-gray-100 text-xs text-gray-500 leading-relaxed">
        本期數先以第 55 期作為示範，將原件掃描以翻頁電子書方式呈現。未來其他期數加入後會在此列表自動延伸。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '衛理報 — 台灣衛理公會研究資料' });
</script>

<style scoped>
.issue-card {
  @apply block no-underline transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg rounded-xl overflow-hidden;
}
</style>
