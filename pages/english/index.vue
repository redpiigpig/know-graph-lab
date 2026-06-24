<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 via-rose-50 to-sky-50">
    <EnglishHeader />

    <main class="max-w-5xl mx-auto px-4 py-6">
      <!-- Hero / 學習狀態 -->
      <section class="rounded-3xl bg-white shadow-sm border border-amber-100 p-5 sm:p-6 mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div class="text-5xl">🌈</div>
          <div class="flex-1 min-w-[200px]">
            <h1 class="text-2xl font-extrabold text-gray-800">Happy English 快樂學英語</h1>
            <p class="text-gray-500 text-sm mt-0.5">國小英語 1000 字 ‧ 20 個主題單元 ‧ 一起來闖關！</p>
          </div>
          <div class="flex gap-3">
            <div class="text-center px-4 py-2 rounded-2xl bg-emerald-50">
              <div class="text-2xl font-extrabold text-emerald-600">{{ progress.today_minutes }}</div>
              <div class="text-[11px] text-emerald-700">今天分鐘</div>
            </div>
            <div class="text-center px-4 py-2 rounded-2xl bg-rose-50">
              <div class="text-2xl font-extrabold text-rose-600">{{ progress.streak_days }}</div>
              <div class="text-[11px] text-rose-700">連續天數</div>
            </div>
            <div class="text-center px-4 py-2 rounded-2xl bg-sky-50">
              <div class="text-2xl font-extrabold text-sky-600">{{ Math.round(progress.total_minutes) }}</div>
              <div class="text-[11px] text-sky-700">總分鐘</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 複習測驗：每 5 單元段考 + 總複習 -->
      <section class="mb-6">
        <h2 class="text-sm font-bold text-gray-500 mb-2 px-1">🏆 複習測驗</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          <NuxtLink
            v-for="r in reviews" :key="r.range"
            :to="`/english/review/${r.range}`"
            class="rounded-2xl p-3 text-center no-underline transition hover:-translate-y-0.5 hover:shadow-md text-white"
            :class="r.range === 'all' ? 'col-span-2 sm:col-span-1' : ''"
            :style="{ background: r.range === 'all' ? 'linear-gradient(135deg,#7C3AED,#DB2777)' : '#8E7CC3' }"
          >
            <div class="text-2xl">{{ r.range === 'all' ? '👑' : '🏆' }}</div>
            <div class="text-sm font-bold mt-1 leading-tight">{{ r.label }}</div>
            <div v-if="best[`0:${r.type}`] != null" class="text-xs font-bold mt-1 bg-white/25 rounded-full px-2 py-0.5 inline-block">★ {{ best[`0:${r.type}`] }}</div>
            <div v-else class="text-[11px] text-white/70 mt-1">未測驗</div>
          </NuxtLink>
        </div>
      </section>

      <!-- 課程格 -->
      <h2 class="text-sm font-bold text-gray-500 mb-2 px-1">📚 20 個單元</h2>
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <NuxtLink
          v-for="(l, i) in lessons"
          :key="l.no"
          :to="`/english/${l.no}`"
          class="group rounded-2xl bg-white border-2 p-4 no-underline transition hover:-translate-y-0.5 hover:shadow-md"
          :style="{ borderColor: palette[i % palette.length] + '40' }"
        >
          <div class="flex items-center gap-3">
            <span
              class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-extrabold text-sm flex-shrink-0"
              :style="{ background: palette[i % palette.length] }"
            >L{{ l.no }}</span>
            <img v-if="l.theme_emoji" :src="emojiUrl(l.theme_emoji)" class="w-8 h-8" alt="" loading="lazy" />
          </div>
          <h2 class="mt-3 font-bold text-gray-800 leading-tight">{{ l.title_zh }}</h2>
          <p class="text-xs text-gray-400 truncate">{{ l.title_en }}</p>
          <div class="mt-3 flex items-center justify-between">
            <span class="text-[11px] text-gray-400">50 個單字 ‧ 5 種測驗</span>
            <span
              v-if="best[`${l.no}:comprehensive`] != null"
              class="text-xs font-bold px-2 py-0.5 rounded-full"
              :class="scoreClass(best[`${l.no}:comprehensive`])"
            >★ {{ best[`${l.no}:comprehensive`] }}</span>
          </div>
        </NuxtLink>
      </section>

      <p class="text-center text-xs text-gray-400 mt-8">
        Happy English ‧ 點任一單元開始學習與測驗 ‧ 朗讀速度為 0.75 倍方便聽清楚
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "english-auth" });

interface Lesson { no: number; title_en: string; title_zh: string; theme_emoji?: string }

const palette = [
  "#E8505B","#F9A03F","#F6C90E","#5FAD56","#3DB2C7","#4F86C6","#8E7CC3",
  "#E36588","#F08A5D","#C5A300","#3F9C72","#2C97A6","#5C6BC0","#A65DAE",
  "#D7385E","#EB7B59","#BFA600","#2E8B7A","#2980B9","#9B59B6",
];

const { data: lessons } = await useFetch<Lesson[]>("/content/english/lessons.json", {
  key: "english-lessons",
  default: () => [],
});

const progress = ref({ today_minutes: 0, total_minutes: 0, streak_days: 0 });
const best = ref<Record<string, number>>({});

const reviews = [
  { range: "1-5", label: "第 1–5 課", type: "review_1_5" },
  { range: "6-10", label: "第 6–10 課", type: "review_6_10" },
  { range: "11-15", label: "第 11–15 課", type: "review_11_15" },
  { range: "16-20", label: "第 16–20 課", type: "review_16_20" },
  { range: "all", label: "總複習", type: "review_all" },
];

function scoreClass(p: number) {
  if (p >= 80) return "bg-emerald-100 text-emerald-700";
  if (p >= 60) return "bg-amber-100 text-amber-700";
  return "bg-rose-100 text-rose-700";
}

onMounted(async () => {
  try {
    const [p, s] = await Promise.all([
      authedFetch<typeof progress.value>("/api/english/progress"),
      authedFetch<{ best: Record<string, number> }>("/api/english/scores"),
    ]);
    progress.value = p;
    best.value = s.best || {};
  } catch { /* 未登入或首次：保持預設 0 */ }
});
</script>
