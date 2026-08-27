<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader title="教會拉丁文讀本（上下兩冊）" :back="{ to: '/original-readers', label: '讀本總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入兩冊一百課主資料…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="reader">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#241d18] px-6 py-9 text-[#f4efe2] shadow-xl sm:px-10">
          <p class="text-[11px] font-semibold tracking-[0.26em] text-amber-300">PRIVATE · ECCLESIASTICAL LATIN · 2 VOLUMES · 100 LESSONS</p>
          <h1 class="mt-3 max-w-4xl font-serif text-3xl font-semibold leading-tight sm:text-5xl break-words">{{ reader.title }}</h1>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-stone-300">{{ reader.subtitle }}</p>
          <p class="mt-2 text-xs text-stone-400">發音：{{ reader.pronunciation }}　·　資料產生於 {{ reader.generatedOn }}</p>
          <dl class="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div v-for="stat in stats" :key="stat.label" class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400 truncate">{{ stat.label }}</dt>
              <dd class="mt-1 text-xl font-semibold">{{ stat.value }}</dd>
            </div>
          </dl>
        </header>

        <section class="mt-6 grid gap-4 lg:grid-cols-[1fr_1fr]">
          <div class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-950">
            <p class="text-[10px] font-bold tracking-[0.2em] text-amber-700">RELEASE STATE　初版</p>
            <p class="mt-2 font-semibold">尚未完成，請勿當作定稿使用</p>
            <ul class="mt-3 list-disc space-y-1 pl-5 text-amber-900/90">
              <li v-for="problem in reader.openProblems" :key="problem" class="break-words">{{ problem }}</li>
            </ul>
            <p class="mt-3 text-amber-900/80">{{ reader.audioStatus.label }}：{{ reader.audioStatus.policy }}</p>
          </div>

          <NuxtLink :to="reader.terminal.href" class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">終卷 · ORDO MISSAE</p>
            <h2 class="mt-2 font-serif text-xl font-semibold break-words">{{ reader.terminal.title }}</h2>
            <p class="mt-1 text-sm text-stone-500 break-words">{{ reader.terminal.latinTitle }}</p>
            <p class="mt-3 text-sm text-stone-600">{{ reader.terminal.segmentCount }} 段，附於下冊，不佔五十篇讀本額度。</p>
            <p v-if="reader.terminal.translationNote" class="mt-1 text-xs text-stone-500 break-words">{{ reader.terminal.translationNote }}</p>
          </NuxtLink>

          <NuxtLink to="/original-readers/lat-lessons/tables" class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">APPENDIX · REFERENCE TABLES</p>
            <h2 class="mt-2 font-serif text-xl font-semibold break-words">附錄參考表</h2>
            <p class="mt-1 text-sm text-stone-500 break-words">專名按九類分節，另有數字、親屬、曆法、職分、禮儀年、文獻與經院用語各表</p>
            <p class="mt-3 text-sm text-stone-600">兩冊各自的附錄，次序與紙本讀本相同。</p>
          </NuxtLink>
        </section>

        <section v-for="volume in reader.volumes" :key="volume.slug" class="mt-8">
          <div class="flex flex-wrap items-baseline justify-between gap-3">
            <h2 class="font-serif text-2xl font-semibold">{{ volume.name }}　{{ volume.title }}</h2>
            <p class="text-xs text-stone-500">
              {{ volume.counts.words }} 詞　·　{{ volume.counts.memoryUnits }} 記憶單元　·　讀本 {{ volume.counts.readingWords.toLocaleString() }} 詞
            </p>
          </div>
          <p class="mt-1 text-sm text-stone-600">{{ volume.blurb }}</p>

          <ul class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="lesson in volume.lessons" :key="lesson.href">
              <NuxtLink :to="lesson.href" class="flex h-full flex-col rounded-2xl border border-stone-300 bg-white/80 px-4 py-3 transition hover:border-stone-500 hover:bg-white">
                <span class="text-[11px] font-semibold tracking-widest text-stone-400">第 {{ lesson.lesson }} 課</span>
                <span class="mt-1 line-clamp-2 font-serif text-[15px] leading-6 break-words">{{ lesson.title || "（無讀本）" }}</span>
                <span class="mt-2 text-[11px] text-stone-500">
                  {{ lesson.words }} 詞　·　記憶 {{ lesson.memoryUnits }}　·　讀本 {{ lesson.readingWords }} 詞
                </span>
              </NuxtLink>
            </li>
          </ul>
        </section>

        <section class="mt-10 rounded-3xl border border-stone-300 bg-white/70 p-6">
          <h2 class="font-serif text-xl font-semibold">凡例</h2>
          <dl class="mt-4 space-y-3 text-sm leading-6">
            <div v-for="item in reader.colophon" :key="item.label">
              <dt class="font-semibold text-stone-700">{{ item.label }}</dt>
              <dd class="mt-1 text-stone-600 break-words">{{ item.text }}</dd>
            </div>
          </dl>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
useHead({ title: "教會拉丁文讀本", meta: [{ name: "robots", content: "noindex, nofollow" }] });

const { data: reader, pending, error } = await useFetch("/api/original-readers/lat-lessons");

const stats = computed(() => {
  if (!reader.value) return [];
  const words = reader.value.volumes.reduce((total, volume) => total + volume.counts.words, 0);
  const units = reader.value.volumes.reduce((total, volume) => total + volume.counts.memoryUnits, 0);
  const readingWords = reader.value.volumes.reduce((total, volume) => total + volume.counts.readingWords, 0);
  return [
    { label: "課次", value: "100" },
    { label: "詞彙", value: words.toLocaleString() },
    { label: "記憶單元", value: `${units} / 200` },
    { label: "讀本原文", value: readingWords.toLocaleString() },
  ];
});
</script>
