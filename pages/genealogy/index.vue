<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">圖譜工具</span>
    </nav>

    <div class="flex-1 flex items-center justify-center p-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-3xl">
        <NuxtLink
          to="/genealogy/draw"
          class="group flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-amber-300 transition"
        >
          <div class="text-3xl">🌳</div>
          <div>
            <div class="font-semibold text-gray-900 text-base group-hover:text-amber-700 transition">族譜繪製</div>
            <div class="text-xs text-gray-400 mt-0.5">自由繪製個人族譜，支援 AI 匯入</div>
          </div>
        </NuxtLink>

        <NuxtLink
          to="/genealogy/biblical"
          class="group flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-indigo-300 transition"
        >
          <div class="text-3xl">📖</div>
          <div>
            <div class="font-semibold text-gray-900 text-base group-hover:text-indigo-700 transition">聖經人物族譜</div>
            <div class="text-xs text-gray-400 mt-0.5">創世記族譜資料庫，表格與圖表檢視</div>
          </div>
        </NuxtLink>

        <NuxtLink
          to="/genealogy/episcopal"
          class="group flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-violet-300 transition"
        >
          <div class="text-3xl">⛪</div>
          <div>
            <div class="font-semibold text-gray-900 text-base group-hover:text-violet-700 transition">使徒統緒</div>
            <div class="text-xs text-gray-400 mt-0.5">五大宗主教座歷任主教傳承表</div>
          </div>
        </NuxtLink>

        <NuxtLink
          to="/genealogy/islamic"
          class="group flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-emerald-300 transition"
        >
          <div class="text-3xl">☪</div>
          <div>
            <div class="font-semibold text-gray-900 text-base group-hover:text-emerald-700 transition">伊斯蘭族譜</div>
            <div class="text-xs text-gray-400 mt-0.5">阿丹至穆罕默德 + 12 伊瑪目傳承</div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '圖譜工具 — Know Graph Lab' })
</script>
