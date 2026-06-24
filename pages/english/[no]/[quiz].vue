<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 via-rose-50 to-sky-50">
    <EnglishHeader :back="{ to: `/english/${no}`, label: '回單元' }" />
    <main v-if="lesson" class="max-w-2xl mx-auto px-4 py-6">
      <EnglishQuizRunner
        :items="items"
        :accent="accent"
        :icon="meta.icon"
        :title="`${meta.label}測驗`"
        :subtitle="`Unit ${no} ‧ ${lesson.title_zh}`"
        :save-lesson-no="no"
        :save-quiz-type="quizType"
        :seconds="tracker.activeSeconds.value"
        :back-to="`/english/${no}`"
        @restart="rebuild"
      />
    </main>
    <div v-else class="max-w-2xl mx-auto px-4 py-20 text-center text-gray-400">載入中…</div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "english-auth" });

const route = useRoute();
const no = Number(route.params.no);
const quizType = String(route.params.quiz);

const META: Record<string, { label: string; icon: string }> = {
  vocab: { label: "單字", icon: "📝" },
  listening: { label: "聽力", icon: "🎧" },
  speaking: { label: "口說", icon: "🎤" },
  sentence: { label: "造句", icon: "🧩" },
  comprehensive: { label: "綜合", icon: "🏆" },
};
const meta = META[quizType] || { label: "測驗", icon: "❓" };

const palette = ["#E8505B","#F9A03F","#F6C90E","#5FAD56","#3DB2C7","#4F86C6","#8E7CC3","#E36588","#F08A5D","#C5A300","#3F9C72","#2C97A6","#5C6BC0","#A65DAE","#D7385E","#EB7B59","#BFA600","#2E8B7A","#2980B9","#9B59B6"];
const accent = palette[(no - 1) % palette.length];

const { data: lessons } = await useFetch<any[]>("/content/english/lessons.json", { key: "english-lessons", default: () => [] });
const lesson = computed(() => (lessons.value || []).find((l) => l.no === no));

const items = ref<any[]>([]);
const tracker = useEnglishTracker();
function rebuild() { if (lesson.value) items.value = buildUnitQuiz(lesson.value, quizType); }

watch(lesson, (l) => { if (l && !items.value.length) rebuild(); }, { immediate: true });
onMounted(() => { tracker.start(`quiz:${quizType}`); });
</script>
