<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 via-rose-50 to-sky-50">
    <EnglishHeader :back="{ to: `/english/${no}`, label: '回單元' }" />

    <main v-if="lesson" class="max-w-2xl mx-auto px-4 py-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-2xl">{{ meta.icon }}</span>
        <div>
          <h1 class="text-xl font-extrabold text-gray-800">{{ meta.label }}測驗</h1>
          <p class="text-xs text-gray-400">Unit {{ no }} ‧ {{ lesson.title_zh }}</p>
        </div>
        <div class="ml-auto text-sm font-bold text-gray-500" v-if="!finished">{{ idx + 1 }} / {{ items.length }}</div>
      </div>

      <!-- 進度條 -->
      <div v-if="!finished" class="h-2 rounded-full bg-gray-100 mb-5 overflow-hidden">
        <div class="h-full rounded-full transition-all" :style="{ width: ((idx) / items.length * 100) + '%', background: accent }"></div>
      </div>

      <!-- 結算 -->
      <section v-if="finished" class="rounded-3xl bg-white border border-amber-100 p-8 text-center">
        <div class="text-6xl mb-3">{{ pct >= 80 ? '🎉' : pct >= 60 ? '👍' : '💪' }}</div>
        <div class="text-5xl font-extrabold" :style="{ color: accent }">{{ pct }}<span class="text-2xl">分</span></div>
        <p class="text-gray-500 mt-2">答對 {{ score }} / {{ items.length }} 題</p>
        <p class="text-sm mt-1" :class="pct >= 80 ? 'text-emerald-600' : pct >= 60 ? 'text-amber-600' : 'text-rose-600'">
          {{ pct >= 80 ? '太棒了！你很厲害！' : pct >= 60 ? '不錯喔，再加油！' : '多練習幾次就會進步！' }}
        </p>
        <div class="flex gap-3 justify-center mt-6">
          <button @click="restart" class="px-5 py-2.5 rounded-full text-white font-bold" :style="{ background: accent }">🔄 再測一次</button>
          <NuxtLink :to="`/english/${no}`" class="px-5 py-2.5 rounded-full bg-gray-100 text-gray-600 font-bold no-underline">回單元</NuxtLink>
        </div>
      </section>

      <!-- 題目 -->
      <section v-else-if="cur" class="rounded-3xl bg-white border border-amber-100 p-6">
        <!-- MCQ -->
        <template v-if="cur.kind === 'mcq'">
          <div class="text-center mb-5">
            <button v-if="cur.audio" @click="say(cur.audio)" class="text-4xl mb-2">🔊</button>
            <img v-if="cur.emoji" :src="emojiUrl(cur.emoji)" class="w-16 h-16 mx-auto mb-2" alt="" />
            <p class="text-xl font-bold text-gray-800">{{ cur.prompt }}</p>
            <p v-if="cur.audio" class="text-xs text-gray-400 mt-1">點 🔊 再聽一次（0.75 倍）</p>
          </div>
          <div class="grid grid-cols-1 gap-2.5">
            <button v-for="opt in cur.options" :key="opt" @click="answer(opt)" :disabled="picked !== null"
              class="rounded-2xl border-2 px-4 py-3 font-semibold transition text-left"
              :class="optClass(opt)">
              {{ opt }}
            </button>
          </div>
        </template>

        <!-- TYPE（造句 / 翻譯） -->
        <template v-else-if="cur.kind === 'type'">
          <p class="text-sm text-gray-400 mb-1">{{ cur.hint }}</p>
          <p class="text-xl font-bold text-gray-800 mb-4">{{ cur.prompt }}</p>
          <input v-model="typed" @keyup.enter="picked === null && submitType()" :disabled="picked !== null"
            type="text" autocomplete="off" autocapitalize="off"
            class="w-full rounded-2xl border-2 border-gray-200 px-4 py-3 text-lg focus:border-amber-400 outline-none"
            placeholder="在這裡打出英文句子…" />
          <div v-if="picked !== null" class="mt-3 p-3 rounded-2xl" :class="lastCorrect ? 'bg-emerald-50' : 'bg-rose-50'">
            <span :class="lastCorrect ? 'text-emerald-700' : 'text-rose-700'" class="font-bold">{{ lastCorrect ? '✓ 答對了！' : '正確答案：' }}</span>
            <span class="text-gray-700">{{ cur.answer }}</span>
          </div>
          <button v-if="picked === null" @click="submitType" class="mt-4 w-full py-3 rounded-2xl text-white font-bold" :style="{ background: accent }">送出</button>
        </template>

        <!-- SPEAK（口說） -->
        <template v-else-if="cur.kind === 'speak'">
          <div class="text-center mb-4">
            <button @click="say(cur.answer)" class="text-3xl mb-2">🔊</button>
            <p class="text-2xl font-extrabold text-gray-800">{{ cur.answer }}</p>
            <p class="text-gray-400">{{ cur.zh }}</p>
            <p class="text-xs text-gray-400 mt-1">先聽 🔊（0.75x），再按麥克風唸唸看</p>
          </div>
          <div class="text-center">
            <button @click="toggleMic" class="w-20 h-20 rounded-full text-3xl text-white shadow-lg transition"
              :style="{ background: listening ? '#E8505B' : accent }">
              {{ listening ? '⏹' : '🎤' }}
            </button>
            <p class="text-sm text-gray-500 mt-3 min-h-[1.5rem]">{{ heard || interim || (listening ? '請開始說…' : '') }}</p>
            <p v-if="!sttSupported" class="text-xs text-rose-500 mt-1">此瀏覽器不支援語音辨識，請用 Chrome / Edge，或按「跳過」</p>
          </div>
          <div v-if="picked !== null" class="mt-3 p-3 rounded-2xl text-center" :class="lastCorrect ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">
            {{ lastCorrect ? '✓ 發音很棒！' : '再試試看，繼續加油！' }}
          </div>
          <button v-if="picked === null" @click="skipSpeak" class="mt-4 w-full py-2.5 rounded-2xl bg-gray-100 text-gray-500 font-bold">跳過這題</button>
        </template>

        <!-- 下一題 -->
        <button v-if="picked !== null" @click="nextQ" class="mt-5 w-full py-3 rounded-2xl text-white font-bold" :style="{ background: accent }">
          {{ idx + 1 >= items.length ? '看成績 🏁' : '下一題 →' }}
        </button>
      </section>
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

const { speak, startListening, stopListening, listening, interim, supported: sttSupported } = useSpeech();
const tracker = useEnglishTracker();
function say(t: string) { speak(t, "en-US", 0.75); }

// ---- quiz state ----
const items = ref<any[]>([]);
const idx = ref(0);
const score = ref(0);
const picked = ref<string | null>(null);
const lastCorrect = ref(false);
const typed = ref("");
const heard = ref("");
const finished = ref(false);

const cur = computed(() => items.value[idx.value]);
const pct = computed(() => items.value.length ? Math.round((score.value / items.value.length) * 100) : 0);

// ---- helpers ----
const shuffle = (a: any[]) => { const x = [...a]; for (let i = x.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [x[i], x[j]] = [x[j], x[i]]; } return x; };
const sample = (a: any[], n: number) => shuffle(a).slice(0, n);
const norm = (s: string) => (s || "").toLowerCase().replace(/[^a-z0-9 ]/g, "").replace(/\s+/g, " ").trim();

function build() {
  const L = lesson.value;
  if (!L) return;
  const words = L.words as { en: string; zh: string; emoji?: string }[];
  const out: any[] = [];

  const vocabMCQ = (n: number) => sample(words, n).map((w) => {
    const distract = sample(words.filter((x) => x.en !== w.en), 3).map((x) => x.en);
    return { kind: "mcq", prompt: w.zh, emoji: w.emoji, options: shuffle([w.en, ...distract]), answer: w.en };
  });
  const listenMCQ = (n: number) => sample(words, n).map((w) => {
    const distract = sample(words.filter((x) => x.zh !== w.zh), 3).map((x) => x.zh);
    return { kind: "mcq", prompt: "聽到的英文是什麼意思？", audio: w.en, options: shuffle([w.zh, ...distract]), answer: w.zh };
  });
  const grammarMCQ = (n: number) => {
    const pool: any[] = [];
    for (const ex of L.exercises || []) {
      if (ex.type === "fill_choice" || ex.type === "choice") {
        for (const it of ex.items || []) pool.push({ kind: "mcq", prompt: it.q, options: shuffle(it.opts), answer: it.ans });
      }
    }
    return sample(pool, Math.min(n, pool.length));
  };
  const sentenceItems = () => {
    const out2: any[] = [];
    for (const ex of L.exercises || []) {
      if (ex.type === "unscramble") for (const it of ex.items || []) out2.push({ kind: "type", hint: "把單字排成正確的句子", prompt: it.q, answer: it.ans });
      if (ex.type === "translate") for (const it of ex.items || []) out2.push({ kind: "type", hint: "把中文翻成英文", prompt: it.q, answer: it.ans });
    }
    return shuffle(out2).slice(0, 8);
  };
  const speakItems = (n: number) => sample(words, n).map((w) => ({ kind: "speak", answer: w.en, zh: w.zh }));

  if (quizType === "vocab") out.push(...vocabMCQ(Math.min(10, words.length)));
  else if (quizType === "listening") out.push(...listenMCQ(Math.min(10, words.length)));
  else if (quizType === "speaking") out.push(...speakItems(Math.min(6, words.length)));
  else if (quizType === "sentence") out.push(...sentenceItems());
  else if (quizType === "comprehensive") out.push(...shuffle([...vocabMCQ(4), ...listenMCQ(3), ...grammarMCQ(5)]));

  items.value = out;
  idx.value = 0; score.value = 0; picked.value = null; finished.value = false;
  maybeAutoPlay();
}

function maybeAutoPlay() {
  if (cur.value?.kind === "mcq" && cur.value.audio) setTimeout(() => say(cur.value.audio), 300);
}

function optClass(opt: string) {
  if (picked.value === null) return "border-gray-200 hover:border-amber-300 hover:bg-amber-50";
  if (opt === cur.value.answer) return "border-emerald-400 bg-emerald-50 text-emerald-700";
  if (opt === picked.value) return "border-rose-400 bg-rose-50 text-rose-700";
  return "border-gray-100 text-gray-400";
}

function answer(opt: string) {
  if (picked.value !== null) return;
  picked.value = opt;
  lastCorrect.value = opt === cur.value.answer;
  if (lastCorrect.value) score.value++;
}
function submitType() {
  picked.value = typed.value;
  lastCorrect.value = norm(typed.value) === norm(cur.value.answer);
  if (lastCorrect.value) score.value++;
}
function toggleMic() {
  if (listening.value) { stopListening(); return; }
  heard.value = "";
  startListening("en-US", (text: string) => {
    heard.value = text;
    stopListening();
    const target = norm(cur.value.answer);
    const got = norm(text);
    const tw = target.split(" ").filter(Boolean);
    const matched = tw.filter((w) => got.includes(w)).length;
    lastCorrect.value = got === target || (tw.length > 0 && matched / tw.length >= 0.6);
    picked.value = text;
    if (lastCorrect.value) score.value++;
  });
}
function skipSpeak() { picked.value = "skip"; lastCorrect.value = false; }

function nextQ() {
  if (idx.value + 1 >= items.value.length) return finish();
  idx.value++;
  picked.value = null; typed.value = ""; heard.value = "";
  maybeAutoPlay();
}
async function finish() {
  finished.value = true;
  stopListening();
  try {
    await authedFetch("/api/english/score", {
      method: "POST",
      body: { lesson_no: no, quiz_type: quizType, score: score.value, total: items.value.length },
    });
  } catch { /* ignore */ }
}
function restart() { build(); }

watch(lesson, (l) => { if (l && !items.value.length) build(); }, { immediate: true });
onMounted(() => { tracker.start(`quiz:${quizType}`); });
</script>
