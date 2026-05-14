<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">地圖繪製</span>
    </nav>

    <div class="flex-1 flex items-center justify-center p-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-3xl">
        <NuxtLink
          to="/maps/world-religions"
          class="group flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-emerald-300 transition"
        >
          <div class="text-3xl">🌍</div>
          <div>
            <div class="font-semibold text-gray-900 text-base group-hover:text-emerald-700 transition">全球八大人文宗教界域</div>
            <div class="text-xs text-gray-400 mt-0.5">世界文化板塊主題地圖，按界域與文化圈劃定</div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '地圖繪製 — Know Graph Lab' })
</script>
