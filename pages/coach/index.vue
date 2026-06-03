<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">AI 語言教練</span>
    </nav>

    <div class="flex-1 px-6 py-10">
      <div class="max-w-4xl mx-auto">
        <div class="mb-8">
          <h1 class="text-2xl font-bold text-gray-900">選一個語言，進入專屬學習空間</h1>
          <p class="text-sm text-gray-500 mt-1.5">
            每個語言有獨立的首頁、儀表板、記憶庫與所有功能。語音對話建議用 Chrome / Edge。
          </p>
        </div>

        <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <template v-for="c in coaches" :key="c.language">
            <!-- 已開放：真正的 NuxtLink（用顯式標籤，編譯期保證渲染成 <a>，可點進去）-->
            <NuxtLink
              v-if="c.enabled"
              :to="`/coach/${c.language}`"
              class="group relative flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm transition hover:shadow-md hover:border-indigo-300 cursor-pointer"
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
              </div>
            </NuxtLink>

            <!-- 即將推出：純 div，不可點 -->
            <div
              v-else
              class="group relative flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm transition opacity-60"
            >
              <div class="flex items-center justify-between">
                <div class="text-4xl">{{ c.emoji }}</div>
                <div class="text-2xl">{{ c.flag }}</div>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-gray-900 text-base">{{ c.name }}</span>
                  <span class="text-xs text-gray-400">{{ c.nameNative }}</span>
                </div>
                <div class="text-xs font-medium text-indigo-600 mt-0.5">{{ c.langLabel }} · {{ c.accent }}</div>
                <p class="text-xs text-gray-500 mt-1.5 leading-relaxed">{{ c.blurb }}</p>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <span v-if="c.voiceless" class="text-[11px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">純文字（古語言）</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 ml-auto">即將推出</span>
              </div>
            </div>
          </template>
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
