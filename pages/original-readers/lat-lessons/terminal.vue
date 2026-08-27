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

        <div v-if="audio.deviceSupported.value" class="mt-5 flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="rounded-full border border-stone-400 px-4 py-1.5 text-xs text-stone-600 transition hover:border-stone-700 hover:text-stone-900"
            @click="toggleAll"
          >{{ audio.playing.value ? "停止朗讀" : "從頭朗讀全篇" }}</button>
          <button
            v-if="audio.playing.value"
            type="button"
            class="rounded-full border border-stone-400 px-3 py-1.5 text-xs text-stone-600 transition hover:border-stone-700"
            @click="audio.togglePause()"
          >{{ audio.paused.value ? "繼續" : "暫停" }}</button>
          <label class="flex items-center gap-1 text-[11px] text-stone-500">
            語速
            <input v-model.number="audio.rate.value" type="range" min="0.5" max="1.1" step="0.02" class="w-24 accent-stone-700">
          </label>
        </div>
        <p v-if="audio.warning.value" class="mt-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-6 text-amber-900 break-words">{{ audio.warning.value }}</p>

        <ol class="mt-6 space-y-3">
          <li
            v-for="(row, index) in ordo.segments"
            :key="index"
            class="rounded-2xl border px-5 py-3 transition"
            :class="audio.currentSegmentId.value === `ordo-${index}`
              ? 'border-amber-400 bg-amber-50'
              : 'border-stone-200 bg-white/70'"
          >
            <p class="font-serif text-[17px] leading-8 break-words">
              <button
                v-if="audio.deviceSupported.value"
                type="button"
                class="mr-1 align-middle text-sm text-stone-400 transition hover:text-stone-800"
                aria-label="朗讀這一行"
                @click="audio.speakOne('la', row.latin)"
              >🔊</button>{{ row.latin }}</p>
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

// 彌撒經文是這本書最該用聽的一篇：固定對答本來就是唱唸的。
const audio = useOriginalReaderAudio();

const segments = computed(() =>
  (ordo.value?.segments || [])
    .map((row: { latin: string; zh: string }, index: number) => ({
      id: `ordo-${index}`,
      ordinal: index,
      ref: "",
      sourceText: row.latin,
      translationZh: row.zh || "",
    }))
    .filter((row) => row.sourceText.trim()),
);

function toggleAll() {
  if (audio.playing.value) audio.stop();
  else audio.playDevice("la", segments.value);
}
</script>
