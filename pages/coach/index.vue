<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">AI 語言教練</span>
    </nav>

    <div class="flex-1 px-6 py-10">
      <div class="max-w-4xl mx-auto">
        <div class="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">選一位語言教練開始練習</h1>
            <p class="text-sm text-gray-500 mt-1.5">
              每位教練有專屬人設與獨立記憶庫。語音對話（麥克風即時轉文字 + 教練語音回覆）建議用 Chrome / Edge。
            </p>
          </div>
          <NuxtLink to="/coach/dashboard" class="flex-shrink-0 text-sm px-4 py-2 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition whitespace-nowrap">📊 學習儀表板</NuxtLink>
        </div>

        <!-- 功能工具列 -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          <NuxtLink to="/coach/review" class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5 hover:border-amber-300 transition">
            <span class="text-xl">🗂️</span>
            <div><div class="text-sm font-medium text-gray-800">單字複習</div><div class="text-[11px] text-gray-400">SRS 間隔複習</div></div>
          </NuxtLink>
          <NuxtLink to="/coach/practice" class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5 hover:border-emerald-300 transition">
            <span class="text-xl">🎯</span>
            <div><div class="text-sm font-medium text-gray-800">技能練習</div><div class="text-[11px] text-gray-400">聽說讀寫 / 考試</div></div>
          </NuxtLink>
          <NuxtLink to="/coach/immersion" class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5 hover:border-sky-300 transition">
            <span class="text-xl">📺</span>
            <div><div class="text-sm font-medium text-gray-800">內容沉浸</div><div class="text-[11px] text-gray-400">YouTube / 文章</div></div>
          </NuxtLink>
          <NuxtLink to="/coach/dashboard" class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5 hover:border-indigo-300 transition">
            <span class="text-xl">📊</span>
            <div><div class="text-sm font-medium text-gray-800">儀表板</div><div class="text-[11px] text-gray-400">進度 / 目標</div></div>
          </NuxtLink>
        </div>

        <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <component
            :is="c.enabled ? 'NuxtLink' : 'div'"
            v-for="c in coaches"
            :key="c.language"
            :to="c.enabled ? `/coach/${c.language}` : undefined"
            class="group relative flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm transition"
            :class="c.enabled ? 'hover:shadow-md hover:border-indigo-300 cursor-pointer' : 'opacity-60'"
          >
            <div class="flex items-center justify-between">
              <div class="text-4xl">{{ c.emoji }}</div>
              <div class="text-2xl">{{ c.flag }}</div>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-900 text-base group-hover:text-indigo-700 transition">{{ c.name }}</span>
                <span class="text-xs text-gray-400">{{ c.nameNative }}</span>
              </div>
              <div class="text-xs font-medium text-indigo-600 mt-0.5">{{ c.langLabel }} · {{ c.accent }}</div>
              <p class="text-xs text-gray-500 mt-1.5 leading-relaxed">{{ c.blurb }}</p>
            </div>

            <div class="flex items-center gap-2 mt-1">
              <span v-if="progressMap[c.language]" class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">
                {{ progressMap[c.language].level }}
              </span>
              <span v-if="c.voiceless" class="text-[11px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">純文字（古語言）</span>
              <span v-if="!c.enabled" class="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 ml-auto">即將推出</span>
            </div>
          </component>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";

definePageMeta({ middleware: "coach-auth" });

const coaches = ref<any[]>([]);
const progressMap = ref<Record<string, any>>({});
const loading = ref(true);

onMounted(async () => {
  try {
    const [c, p] = await Promise.all([
      $fetch<{ coaches: any[] }>("/api/lang/coaches"),
      authedFetch<{ progress: any[] }>("/api/lang/progress").catch(() => ({ progress: [] })),
    ]);
    coaches.value = c.coaches;
    for (const row of p.progress) progressMap.value[row.language] = row;
  } finally {
    loading.value = false;
  }
});
</script>
