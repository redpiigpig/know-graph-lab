<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 via-rose-50 to-sky-50">
    <EnglishHeader :back="{ to: '/english', label: '所有單元' }" />

    <main v-if="lesson" class="max-w-3xl mx-auto px-4 py-6">
      <!-- 標題 -->
      <div class="flex items-center gap-3 mb-5">
        <img v-if="lesson.theme_emoji" :src="emojiUrl(lesson.theme_emoji)" class="w-12 h-12" alt="" />
        <div>
          <div class="text-xs font-bold" :style="{ color: accent }">UNIT {{ lesson.no }}</div>
          <h1 class="text-2xl font-extrabold text-gray-800">{{ lesson.title_zh }}</h1>
          <p class="text-sm text-gray-400">{{ lesson.title_en }} ‧ {{ lesson.grammar }}</p>
        </div>
        <div class="ml-auto text-right">
          <span class="inline-block text-xs px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-bold whitespace-nowrap">⏱ 本次 {{ clock }}</span>
          <div class="text-[11px] text-gray-400 mt-1">今日 {{ todayMinutes }} 分鐘</div>
        </div>
      </div>

      <!-- 測驗入口 -->
      <section class="grid grid-cols-2 sm:grid-cols-5 gap-2.5 mb-6">
        <NuxtLink
          v-for="q in quizzes" :key="q.type" :to="`/english/${lesson.no}/${q.type}`"
          class="rounded-2xl bg-white border-2 p-3 text-center no-underline transition hover:-translate-y-0.5 hover:shadow"
          :style="{ borderColor: accent + '40' }"
        >
          <div class="text-2xl">{{ q.icon }}</div>
          <div class="text-xs font-bold text-gray-700 mt-1">{{ q.label }}</div>
          <div v-if="best[`${lesson.no}:${q.type}`] != null" class="text-[11px] font-bold mt-0.5" :class="scoreColor(best[`${lesson.no}:${q.type}`])">
            ★ {{ best[`${lesson.no}:${q.type}`] }}
          </div>
          <div v-else class="text-[11px] text-gray-300 mt-0.5">未測驗</div>
        </NuxtLink>
      </section>

      <!-- 課文 Reading -->
      <section v-if="lesson.reading" class="rounded-3xl bg-white border border-amber-100 p-5 mb-5">
        <div class="flex items-center justify-between mb-2">
          <h2 class="font-extrabold text-gray-800">📖 課文　<span class="text-sm font-normal text-gray-400">{{ lesson.reading.title_en }}</span></h2>
          <button @click="playPassage" class="text-xs px-3 py-1.5 rounded-full text-white" :style="{ background: accent }">
            🔊 整篇朗讀 (0.75x)
          </button>
        </div>
        <p class="text-sm text-gray-500 mb-3">{{ lesson.reading.title_zh }}</p>
        <div class="space-y-2">
          <p v-for="(s, i) in lesson.reading.sentences" :key="i"
             @click="say(s.en)"
             class="cursor-pointer rounded-xl px-3 py-2 hover:bg-amber-50 transition leading-relaxed">
            <span class="font-medium text-gray-800">{{ s.en }}</span>
            <span class="text-gray-400 text-sm ml-1">{{ s.zh }}</span>
          </p>
        </div>
      </section>

      <!-- 單字 Vocabulary -->
      <section class="rounded-3xl bg-white border border-amber-100 p-5 mb-5">
        <h2 class="font-extrabold text-gray-800 mb-3">🔤 單字 <span class="text-sm font-normal text-gray-400">Vocabulary (50) ‧ 點一下聽發音</span></h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          <button v-for="w in lesson.words" :key="w.en" @click="say(w.en)"
                  class="flex items-center gap-2 rounded-xl px-2.5 py-1.5 hover:bg-sky-50 transition text-left">
            <img v-if="w.emoji" :src="emojiUrl(w.emoji)" class="w-6 h-6 flex-shrink-0" alt="" loading="lazy" />
            <span v-else class="w-6 text-center flex-shrink-0" :style="{ color: accent }">‧</span>
            <span class="font-semibold text-gray-800">{{ w.en }}</span>
            <span class="text-gray-400 text-sm">{{ w.zh }}</span>
            <span class="ml-auto text-gray-300 text-xs">🔊</span>
          </button>
        </div>
      </section>

      <!-- 例句 Sentences -->
      <section v-if="lesson.sentences?.length" class="rounded-3xl bg-white border border-amber-100 p-5 mb-10">
        <h2 class="font-extrabold text-gray-800 mb-3">💬 常用例句 <span class="text-sm font-normal text-gray-400">點一下聽發音</span></h2>
        <div class="space-y-1.5">
          <p v-for="(s, i) in lesson.sentences" :key="i" @click="say(s.en)"
             class="cursor-pointer rounded-xl px-3 py-2 hover:bg-emerald-50 transition">
            <span class="font-medium text-gray-800">{{ s.en }}</span>
            <span class="text-gray-400 text-sm ml-1">{{ s.zh }}</span>
          </p>
        </div>
      </section>
    </main>

    <div v-else class="max-w-3xl mx-auto px-4 py-20 text-center text-gray-400">載入中…</div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "english-auth" });

const route = useRoute();
const no = Number(route.params.no);

const palette = ["#E8505B","#F9A03F","#F6C90E","#5FAD56","#3DB2C7","#4F86C6","#8E7CC3","#E36588","#F08A5D","#C5A300","#3F9C72","#2C97A6","#5C6BC0","#A65DAE","#D7385E","#EB7B59","#BFA600","#2E8B7A","#2980B9","#9B59B6"];
const accent = palette[(no - 1) % palette.length];

const quizzes = [
  { type: "vocab", label: "單字", icon: "📝" },
  { type: "listening", label: "聽力", icon: "🎧" },
  { type: "speaking", label: "口說", icon: "🎤" },
  { type: "sentence", label: "造句", icon: "🧩" },
  { type: "comprehensive", label: "綜合", icon: "🏆" },
];

const { data: lessons } = await useFetch<any[]>("/content/english/lessons.json", { key: "english-lessons", default: () => [] });
const lesson = computed(() => (lessons.value || []).find((l) => l.no === no));

const best = ref<Record<string, number>>({});
const todayMinutes = ref(0);
const { speak } = useSpeech();
const tracker = useEnglishTracker();
const clock = computed(() => {
  const s = Math.max(0, Math.floor(tracker.activeSeconds.value));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
});

function say(text: string) { speak(text, "en-US", 0.75); }
function scoreColor(p: number) { return p >= 80 ? "text-emerald-600" : p >= 60 ? "text-amber-600" : "text-rose-600"; }

let passageTimer: any = null;
function playPassage() {
  const sents = lesson.value?.reading?.sentences || [];
  if (!sents.length) return;
  let i = 0;
  const next = () => {
    if (i >= sents.length) return;
    say(sents[i].en);
    i++;
    passageTimer = setTimeout(next, 2600);
  };
  next();
}

onMounted(async () => {
  tracker.start("lesson");
  try {
    const [s, p] = await Promise.all([
      authedFetch<{ best: Record<string, number> }>("/api/english/scores"),
      authedFetch<{ today_minutes: number }>("/api/english/progress"),
    ]);
    best.value = s.best || {};
    todayMinutes.value = p.today_minutes ?? 0;
  } catch { /* ignore */ }
});
onBeforeUnmount(() => { if (passageTimer) clearTimeout(passageTimer); });
</script>
