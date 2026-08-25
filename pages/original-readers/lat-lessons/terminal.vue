<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader title="常年期主日彌撒經文" :back="{ to: '/original-readers/lat-lessons', label: '兩冊總覽' }" container-class="max-w-4xl" />

    <main class="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入彌撒經文…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="ordo">
        <header class="rounded-3xl border border-stone-300 bg-[#241d18] px-6 py-7 text-[#f4efe2]">
          <p class="text-[11px] font-semibold tracking-[0.24em] text-amber-300">終卷 · 附於下冊</p>
          <h1 class="mt-2 font-serif text-2xl font-semibold break-words sm:text-3xl">{{ ordo.title }}</h1>
          <p class="mt-1 text-sm text-stone-300 break-words">{{ ordo.latinTitle }}</p>
          <p v-if="ordo.translationNote" class="mt-3 text-xs leading-6 text-amber-200 break-words">{{ ordo.translationNote }}</p>
        </header>

        <ol class="mt-6 space-y-3">
          <li v-for="(row, index) in ordo.segments" :key="index" class="rounded-2xl border border-stone-200 bg-white/70 px-5 py-3">
            <p class="font-serif text-[17px] leading-8 break-words">{{ row.latin }}</p>
            <p class="mt-1 text-sm leading-7 text-stone-600 break-words">{{ row.zh || "〔中譯待補〕" }}</p>
          </li>
        </ol>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
useHead({ title: "常年期主日彌撒經文 · 教會拉丁文讀本", meta: [{ name: "robots", content: "noindex, nofollow" }] });
const { data: ordo, pending, error } = await useFetch("/api/original-readers/lat-lessons/terminal");
</script>
