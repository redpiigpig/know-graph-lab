<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">字母教學・測驗 · {{ coach?.langLabel }}</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-4xl mx-auto w-full space-y-4">
      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入中…</div>
      <div v-else-if="!spec" class="text-sm text-gray-500 py-10 text-center">這個語言沒有字母教學內容。</div>

      <template v-else>
        <!-- 標題 + 模式切換 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <h1 class="text-lg font-bold text-gray-900">{{ spec.title }}</h1>
          <p class="text-xs text-gray-500 mt-1 leading-relaxed">{{ spec.intro }}</p>
          <div class="flex gap-2 mt-3">
            <button @click="mode = 'teach'" :class="tabClass('teach')">📖 教學</button>
            <button @click="mode = 'quiz'; resetQuiz()" :class="tabClass('quiz')">✍️ 測驗</button>
          </div>
        </div>

        <!-- 分組選擇 -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] text-gray-400 mr-1">分組</span>
          <button v-for="g in spec.groups" :key="g.key" @click="toggleGroup(g.key)"
            class="text-xs px-2.5 py-1 rounded-full border transition"
            :class="selected.has(g.key) ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-gray-200 text-gray-500 hover:border-indigo-300'">
            {{ g.label }}<span class="opacity-70"> · {{ g.letters.length }}</span>
          </button>
        </div>

        <!-- ░░ 教學模式 ░░ -->
        <template v-if="mode === 'teach'">
          <div v-for="g in shownGroups" :key="g.key" class="bg-white rounded-2xl border border-gray-100 p-4">
            <div class="flex items-baseline gap-2 mb-2">
              <h2 class="text-sm font-semibold text-gray-800">{{ g.label }}</h2>
              <span v-if="g.note" class="text-[11px] text-gray-400">{{ g.note }}</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
              <button v-for="(l, i) in g.letters" :key="i" @click="speakLetter(l)"
                class="text-left bg-slate-50 hover:bg-indigo-50 border border-gray-100 hover:border-indigo-200 rounded-xl p-2.5 transition group">
                <div class="flex items-baseline gap-1.5" :dir="spec.rtl ? 'rtl' : 'ltr'">
                  <span class="text-2xl font-semibold text-gray-900 leading-none">{{ l.char }}</span>
                  <span v-if="l.upper && l.upper !== l.char" class="text-base text-gray-400 leading-none">{{ l.upper }}</span>
                  <span class="ml-auto text-gray-300 group-hover:text-indigo-500 text-sm">🔊</span>
                </div>
                <div class="text-[11px] text-gray-700 mt-1.5 font-medium">{{ l.name }}</div>
                <div class="text-[11px] text-indigo-600">{{ l.sound }}</div>
                <div v-if="l.example" class="text-[11px] text-gray-400 mt-0.5 truncate" :dir="spec.rtl ? 'rtl' : 'ltr'">
                  {{ l.example }}<span v-if="l.gloss" class="text-gray-300"> · {{ l.gloss }}</span>
                </div>
              </button>
            </div>
          </div>
        </template>

        <!-- ░░ 測驗模式 ░░ -->
        <template v-else>
          <!-- 設定 / 開始 -->
          <div v-if="!quiz.started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
            <div>
              <div class="text-xs font-semibold text-gray-400 mb-1.5">出題方向</div>
              <div class="flex flex-wrap gap-2">
                <button @click="direction = 'g2s'" :class="dirClass('g2s')">看字母 → 選讀音</button>
                <button @click="direction = 's2g'" :class="dirClass('s2g')">看讀音 → 選字母</button>
                <button @click="direction = 'mix'" :class="dirClass('mix')">混合</button>
              </div>
            </div>
            <div>
              <div class="text-xs font-semibold text-gray-400 mb-1.5">題數</div>
              <div class="flex flex-wrap gap-2">
                <button v-for="n in countOptions" :key="n" @click="qCount = n" :class="countClass(n)">{{ n === 0 ? `全部 (${poolSize})` : n }}</button>
              </div>
            </div>
            <div class="text-[11px] text-gray-400">題庫：{{ poolSize }} 個字母（依上方分組）</div>
            <button @click="startQuiz" :disabled="poolSize < 4"
              class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">
              {{ poolSize < 4 ? '至少需 4 個字母' : '開始測驗' }}
            </button>
          </div>

          <!-- 作答中 -->
          <div v-else-if="!quiz.done" class="bg-white rounded-2xl border border-gray-100 p-5">
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs text-gray-400">第 {{ quiz.idx + 1 }} / {{ quiz.questions.length }} 題</span>
              <span class="text-xs text-gray-500">✅ {{ quiz.score }}　❌ {{ answeredCount - quiz.score }}</span>
            </div>

            <!-- 題面 -->
            <div class="text-center py-4">
              <template v-if="cur.ask === 'glyph'">
                <div class="text-6xl font-bold text-gray-900 leading-none" :dir="spec.rtl ? 'rtl' : 'ltr'">{{ cur.letter.char }}</div>
                <div v-if="cur.letter.upper && cur.letter.upper !== cur.letter.char" class="text-2xl text-gray-300 mt-1">{{ cur.letter.upper }}</div>
                <button @click="speakLetter(cur.letter)" class="mt-2 text-xs text-indigo-500 hover:text-indigo-700">🔊 聽發音</button>
                <div class="text-xs text-gray-400 mt-2">這個字母的讀音是？</div>
              </template>
              <template v-else>
                <div class="text-3xl font-semibold text-indigo-700">{{ cur.letter.sound }}</div>
                <div class="text-xs text-gray-400 mt-1">{{ cur.letter.name }}</div>
                <div class="text-xs text-gray-400 mt-2">是哪一個字母？</div>
              </template>
            </div>

            <!-- 選項 -->
            <div class="grid grid-cols-2 gap-2.5 mt-2">
              <button v-for="(opt, i) in cur.options" :key="i" @click="pick(opt)" :disabled="answered"
                class="rounded-xl border-2 py-3 px-3 text-center transition disabled:cursor-default"
                :class="optClass(opt)">
                <span v-if="cur.ask === 'glyph'" class="text-base font-medium">{{ opt.sound }}</span>
                <span v-else class="text-3xl font-semibold" :dir="spec.rtl ? 'rtl' : 'ltr'">{{ opt.char }}</span>
              </button>
            </div>

            <!-- 答後回饋 -->
            <div v-if="answered" class="mt-4 text-center">
              <p class="text-sm" :class="lastCorrect ? 'text-emerald-600' : 'text-rose-600'">
                {{ lastCorrect ? '✅ 答對！' : '❌ 正解：' }}
                <span v-if="!lastCorrect" class="font-semibold">{{ cur.letter.char }} = {{ cur.letter.sound }}（{{ cur.letter.name }}）</span>
              </p>
              <p v-if="cur.letter.example" class="text-xs text-gray-400 mt-1" :dir="spec.rtl ? 'rtl' : 'ltr'">
                例：{{ cur.letter.example }}<span v-if="cur.letter.gloss"> · {{ cur.letter.gloss }}</span>
              </p>
              <button @click="next" class="mt-3 px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">
                {{ quiz.idx + 1 < quiz.questions.length ? '下一題 →' : '看結果' }}
              </button>
            </div>
          </div>

          <!-- 結果 -->
          <div v-else class="bg-white rounded-2xl border border-gray-100 p-6 text-center space-y-4">
            <div class="text-4xl">{{ quiz.score === quiz.questions.length ? '🎉' : quiz.score / quiz.questions.length >= 0.7 ? '👍' : '💪' }}</div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ quiz.score }} / {{ quiz.questions.length }}</div>
              <div class="text-xs text-gray-400 mt-1">正確率 {{ Math.round((quiz.score / quiz.questions.length) * 100) }}%</div>
            </div>
            <div v-if="quiz.wrong.length" class="text-left">
              <div class="text-xs font-semibold text-rose-400 mb-1.5">答錯的字母（再看一次）</div>
              <div class="flex flex-wrap gap-1.5">
                <button v-for="(l, i) in quiz.wrong" :key="i" @click="speakLetter(l)"
                  class="text-xs px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100" :dir="spec.rtl ? 'rtl' : 'ltr'">
                  {{ l.char }} {{ l.sound }}
                </button>
              </div>
            </div>
            <div class="flex gap-2 justify-center pt-1">
              <button @click="startQuiz" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">再測一次</button>
              <button @click="resetQuiz" class="px-5 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">改設定</button>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

interface AlphaLetter { char: string; upper?: string; name: string; sound: string; example?: string; gloss?: string; tts?: string }
interface AlphaGroup { key: string; label: string; note?: string; letters: AlphaLetter[] }
interface AlphabetSpec { language: string; title: string; intro: string; rtl?: boolean; groups: AlphaGroup[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const speech = useSpeech();
const tracker = useActivityTracker();
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const coach = ref<any>(null);
const spec = ref<AlphabetSpec | null>(null);
const loading = ref(true);
const mode = ref<"teach" | "quiz">("teach");
const selected = reactive(new Set<string>());
const direction = ref<"g2s" | "s2g" | "mix">("g2s");
const qCount = ref(20);
const countOptions = [10, 20, 30, 0];

function tabClass(m: string) {
  return `text-sm px-4 py-1.5 rounded-lg font-medium transition ${mode.value === m ? "bg-indigo-600 text-white" : "bg-slate-100 text-gray-500 hover:bg-slate-200"}`;
}
function dirClass(d: string) {
  return `text-xs px-3 py-1.5 rounded-lg border transition ${direction.value === d ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}
function countClass(n: number) {
  return `text-xs px-3 py-1.5 rounded-lg border transition ${qCount.value === n ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}

const shownGroups = computed(() => (spec.value?.groups || []).filter((g) => selected.has(g.key)));
const pool = computed<AlphaLetter[]>(() => shownGroups.value.flatMap((g) => g.letters).filter((l) => l.sound && l.char));
const poolSize = computed(() => pool.value.length);

function toggleGroup(key: string) {
  if (selected.has(key)) { if (selected.size > 1) selected.delete(key); }
  else selected.add(key);
  if (mode.value === "quiz") resetQuiz();
}

function speakLetter(l: AlphaLetter) {
  speech.speak(l.tts || l.example || l.char, coach.value?.ttsLang || TTS[lang.value] || "en-US");
}

// ── 測驗 ───────────────────────────────────────────────────────────────────
interface Question { letter: AlphaLetter; ask: "glyph" | "sound"; options: AlphaLetter[] }
const quiz = reactive<{ started: boolean; done: boolean; idx: number; score: number; questions: Question[]; wrong: AlphaLetter[] }>(
  { started: false, done: false, idx: 0, score: 0, questions: [], wrong: [] }
);
const answered = ref(false);
const picked = ref<AlphaLetter | null>(null);
const lastCorrect = ref(false);
const cur = computed(() => quiz.questions[quiz.idx] || { letter: { char: "", name: "", sound: "" }, ask: "glyph", options: [] } as Question);
const answeredCount = computed(() => quiz.idx + (answered.value ? 1 : 0));

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

function buildQuestion(letter: AlphaLetter): Question {
  const ask: "glyph" | "sound" = direction.value === "mix" ? (Math.random() < 0.5 ? "glyph" : "sound") : direction.value === "g2s" ? "glyph" : "sound";
  // 干擾項：依問法的「答案欄位」去重（glyph→比 sound、sound→比 char），避免兩個正解
  const keyOf = (l: AlphaLetter) => (ask === "glyph" ? l.sound : l.char);
  const distractors: AlphaLetter[] = [];
  const usedKeys = new Set([keyOf(letter)]);
  for (const d of shuffle(pool.value)) {
    if (distractors.length >= 3) break;
    if (usedKeys.has(keyOf(d))) continue;
    usedKeys.add(keyOf(d));
    distractors.push(d);
  }
  return { letter, ask, options: shuffle([letter, ...distractors]) };
}

function startQuiz() {
  const n = qCount.value === 0 ? pool.value.length : Math.min(qCount.value, pool.value.length);
  const picks = shuffle(pool.value).slice(0, n);
  quiz.questions = picks.map(buildQuestion);
  quiz.idx = 0; quiz.score = 0; quiz.wrong = []; quiz.started = true; quiz.done = false;
  answered.value = false; picked.value = null;
}
function resetQuiz() {
  quiz.started = false; quiz.done = false; quiz.idx = 0; quiz.score = 0; quiz.questions = []; quiz.wrong = [];
  answered.value = false; picked.value = null;
}
function pick(opt: AlphaLetter) {
  if (answered.value) return;
  answered.value = true;
  picked.value = opt;
  lastCorrect.value = opt.char === cur.value.letter.char;
  if (lastCorrect.value) quiz.score++;
  else quiz.wrong.push(cur.value.letter);
}
function next() {
  if (quiz.idx + 1 < quiz.questions.length) {
    quiz.idx++; answered.value = false; picked.value = null;
  } else {
    quiz.done = true;
  }
}
function optClass(opt: AlphaLetter) {
  if (!answered.value) return "border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50 text-gray-800";
  const isCorrect = opt.char === cur.value.letter.char;
  const isPicked = opt === picked.value;
  if (isCorrect) return "border-emerald-400 bg-emerald-50 text-emerald-700";
  if (isPicked) return "border-rose-400 bg-rose-50 text-rose-700";
  return "border-gray-200 bg-white text-gray-400 opacity-60";
}

onMounted(async () => {
  try {
    const [{ coaches }, r] = await Promise.all([
      $fetch<{ coaches: any[] }>("/api/lang/coaches"),
      authedFetch<{ available: boolean; alphabet: AlphabetSpec | null }>(`/api/lang/alphabet?language=${lang.value}`),
    ]);
    coach.value = coaches.find((c) => c.language === lang.value);
    if (r.available && r.alphabet) {
      spec.value = r.alphabet;
      r.alphabet.groups.forEach((g) => selected.add(g.key));
    }
  } finally {
    loading.value = false;
  }
  tracker.start(lang.value, "reading", "alphabet");
});
</script>
