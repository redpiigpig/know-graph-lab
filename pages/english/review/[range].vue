<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 via-rose-50 to-sky-50">
    <EnglishHeader :back="{ to: '/english', label: '所有單元' }" />
    <main v-if="ready" class="max-w-2xl mx-auto px-4 py-6">
      <EnglishQuizRunner
        :items="items"
        accent="#6D28D9"
        icon="🏆"
        :title="title"
        :subtitle="subtitle"
        :save-lesson-no="0"
        :save-quiz-type="quizType"
        :seconds="tracker.activeSeconds.value"
        back-to="/english"
        back-label="回首頁"
        @restart="rebuild"
      />
    </main>
    <div v-else class="max-w-2xl mx-auto px-4 py-20 text-center text-gray-400">{{ error || '載入中…' }}</div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "english-auth" });

const route = useRoute();
const range = String(route.params.range); // "all" | "1-5" | "6-10" | "11-15" | "16-20"

// 解析範圍
let from = 1, to = 20, valid = true;
if (range === "all") { from = 1; to = 20; }
else {
  const m = range.match(/^(\d{1,2})-(\d{1,2})$/);
  if (m) { from = Number(m[1]); to = Number(m[2]); } else valid = false;
}
const error = ref(valid ? "" : "找不到這個複習測驗");

const quizType = range === "all" ? "review_all" : `review_${from}_${to}`;
const title = range === "all" ? "總複習測驗" : `段考 ‧ 第 ${from}–${to} 課`;
const subtitle = range === "all" ? "涵蓋全部 20 個單元 ‧ 1000 字" : `涵蓋第 ${from} 到第 ${to} 課`;
const totalQ = range === "all" ? 20 : 15;

const { data: lessons } = await useFetch<any[]>("/content/english/lessons.json", { key: "english-lessons", default: () => [] });
const inRange = computed(() => (lessons.value || []).filter((l) => l.no >= from && l.no <= to));

const items = ref<any[]>([]);
const ready = computed(() => valid && items.value.length > 0);
const tracker = useEnglishTracker();
function rebuild() { if (inRange.value.length) items.value = buildReviewQuiz(inRange.value, totalQ); }

watch(inRange, (ls) => { if (valid && ls.length && !items.value.length) rebuild(); }, { immediate: true });
onMounted(() => { tracker.start(`review:${quizType}`); });
</script>
