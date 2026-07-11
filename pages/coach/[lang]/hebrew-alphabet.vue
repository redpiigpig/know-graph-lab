<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${lang}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 text-lg">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">✡️</span>
      <span class="text-sm font-semibold text-gray-900">認識希伯來字母</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <main class="flex-1 p-5 max-w-4xl mx-auto w-full space-y-4">
      <div v-if="loading" class="py-12 text-center text-sm text-gray-400">載入課程中…</div>
      <div v-else-if="!spec" class="py-12 text-center text-sm text-rose-500">找不到希伯來字母課程資料。</div>

      <template v-else>
        <section class="bg-gradient-to-br from-indigo-700 to-violet-700 text-white rounded-2xl p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div class="text-xs text-indigo-200">聖經希伯來文入門 · מֵאָלֶף עַד תָּו</div>
              <h1 class="text-xl font-bold mt-1">從 Alef 到 Tav：認識希伯來字母</h1>
              <p class="text-xs text-indigo-100 mt-2 leading-relaxed max-w-2xl">
                分六課認識由右至左的 22 個子音、5 個字尾形與常用母音點。每個例字可單獨點讀；每課最後用辨字測驗確認記憶。
              </p>
            </div>
            <div class="text-right shrink-0">
              <div class="text-2xl font-bold">{{ completed.size }} / {{ lessons.length }}</div>
              <div class="text-[11px] text-indigo-200">已完成課次</div>
            </div>
          </div>
          <div class="h-2 bg-white/20 rounded-full mt-4 overflow-hidden">
            <div class="h-full bg-amber-300 rounded-full transition-all" :style="{ width: `${progress}%` }" />
          </div>
        </section>

        <section class="flex gap-2 overflow-x-auto pb-1">
          <button v-for="(lesson, i) in lessons" :key="lesson.key" @click="selectLesson(i)"
            class="shrink-0 px-3 py-2 rounded-xl border text-left transition"
            :class="lessonIdx === i ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300'">
            <div class="text-[10px] opacity-70">第 {{ i + 1 }} 課 <span v-if="completed.has(i)">✓</span></div>
            <div class="text-xs font-semibold mt-0.5">{{ lesson.short }}</div>
          </button>
        </section>

        <section class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div class="text-xs text-indigo-500 font-semibold">第 {{ lessonIdx + 1 }} 課</div>
              <h2 class="text-lg font-bold text-gray-900 mt-0.5">{{ currentLesson.title }}</h2>
              <p class="text-xs text-gray-500 mt-1">{{ currentLesson.note }}</p>
            </div>
            <span v-if="completed.has(lessonIdx)" class="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700">✓ 已完成</span>
          </div>

          <div v-if="!quiz.started" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5 mt-4">
            <article v-for="letter in currentLesson.letters" :key="letter.char"
              class="rounded-xl bg-slate-50 border border-gray-100 p-3">
              <div dir="rtl" class="text-center text-4xl font-semibold text-gray-900 leading-none py-2">{{ letter.char }}</div>
              <div class="text-sm font-semibold text-indigo-700 mt-1">{{ letter.name }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ letter.sound }}</div>
              <button v-if="letter.example" type="button" @click="speakExample(letter)"
                class="w-full flex items-center justify-between gap-2 mt-2 px-2 py-1.5 rounded-lg bg-white border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition"
                :title="`朗讀 ${letter.example}`">
                <span dir="rtl" class="text-base text-gray-800">{{ letter.example }}</span>
                <span class="text-[11px] text-gray-400">{{ letter.gloss }} 🔊</span>
              </button>
            </article>
          </div>

          <div v-if="!quiz.started" class="flex flex-wrap gap-2 mt-5">
            <button @click="startQuiz" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700">
              開始本課辨字測驗
            </button>
            <button v-if="lessonIdx > 0" @click="selectLesson(lessonIdx - 1)"
              class="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-500 hover:border-indigo-300">← 上一課</button>
          </div>

          <div v-else-if="!quiz.done" class="mt-5 max-w-xl mx-auto">
            <div class="flex justify-between text-xs text-gray-400">
              <span>第 {{ quiz.idx + 1 }} / {{ quiz.questions.length }} 題</span>
              <span>答對 {{ quiz.score }} 題</span>
            </div>
            <div dir="rtl" class="text-center text-7xl font-semibold text-gray-900 py-8">{{ currentQuestion.letter.char }}</div>
            <p class="text-center text-xs text-gray-400 mb-3">這個字母／符號叫什麼？</p>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="option in currentQuestion.options" :key="option.char" @click="answer(option)"
                :disabled="quiz.answered"
                class="rounded-xl border-2 p-3 text-sm transition disabled:cursor-default"
                :class="optionClass(option)">
                {{ option.name }}
              </button>
            </div>
            <div v-if="quiz.answered" class="text-center mt-4">
              <p class="text-sm" :class="quiz.correct ? 'text-emerald-600' : 'text-rose-600'">
                {{ quiz.correct ? '答對了！' : `正解：${currentQuestion.letter.name}` }}
              </p>
              <button @click="nextQuestion" class="mt-3 px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm">
                {{ quiz.idx + 1 < quiz.questions.length ? '下一題 →' : '看結果' }}
              </button>
            </div>
          </div>

          <div v-else class="text-center py-7">
            <div class="text-4xl">{{ quiz.score === quiz.questions.length ? '🎉' : '👍' }}</div>
            <div class="text-2xl font-bold text-gray-900 mt-2">{{ quiz.score }} / {{ quiz.questions.length }}</div>
            <p class="text-xs text-gray-500 mt-1">本課已完成，可以繼續往下一組字母。</p>
            <div class="flex flex-wrap justify-center gap-2 mt-4">
              <button v-if="lessonIdx + 1 < lessons.length" @click="selectLesson(lessonIdx + 1)"
                class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold">下一課 →</button>
              <NuxtLink v-else :to="`/coach/${lang}/alphabet`"
                class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold">綜合字母測驗</NuxtLink>
              <button @click="startQuiz" class="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-500">再測一次</button>
            </div>
          </div>
        </section>

        <p class="text-[11px] text-gray-400 leading-relaxed">
          發音提示：瀏覽器使用現代希伯來語音朗讀例字，可協助建立字形與聲音連結；本課的字母名稱與音值仍以聖經希伯來文教學標示為準。
        </p>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { useSpeech } from "~/composables/useSpeech";

definePageMeta({ middleware: "coach-auth" });

interface Letter {
  char: string;
  name: string;
  sound: string;
  example?: string;
  gloss?: string;
}
interface Group { key: string; label: string; note?: string; letters: Letter[] }
interface AlphabetSpec { language: string; title: string; intro: string; groups: Group[] }
interface Lesson { key: string; short: string; title: string; note: string; letters: Letter[] }
interface Question { letter: Letter; options: Letter[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const tracker = useActivityTracker();
const speech = useSpeech();
const spec = ref<AlphabetSpec | null>(null);
const coach = ref<any>(null);
const loading = ref(true);
const lessonIdx = ref(0);
const completed = reactive(new Set<number>());

const lessons = computed<Lesson[]>(() => {
  const consonants = spec.value?.groups.find((group) => group.key === "consonants")?.letters || [];
  const finals = spec.value?.groups.find((group) => group.key === "finals")?.letters || [];
  const niqqud = spec.value?.groups.find((group) => group.key === "niqqud")?.letters || [];
  return [
    { key: "alef-he", short: "א—ה", title: "Alef 到 He", note: "先熟悉最前面的五個字母，以及希伯來文由右向左的方向。", letters: consonants.slice(0, 5) },
    { key: "vav-kaf", short: "ו—כ", title: "Vav 到 Kaf", note: "注意 Chet 的喉音，以及 Kaf 有 k／kh 兩種音值。", letters: consonants.slice(5, 11) },
    { key: "lamed-ayin", short: "ל—ע", title: "Lamed 到 Ayin", note: "辨認 Mem、Nun、Samek，並留意 Ayin 的喉音。", letters: consonants.slice(11, 16) },
    { key: "pe-tav", short: "פ—ת", title: "Pe 到 Tav", note: "完成 22 個子音；特別分清 Shin／Sin 的點位。", letters: consonants.slice(16, 22) },
    { key: "finals", short: "ךםןףץ", title: "五個字尾形 · Sofit", note: "Kaf、Mem、Nun、Pe、Tsade 位於詞尾時會換成另一種字形。", letters: finals },
    { key: "niqqud", short: "母音點", title: "常用母音點 · Niqqud", note: "母音點寫在子音下方或旁邊；先學會辨認最常見的八種。", letters: niqqud },
  ];
});
const currentLesson = computed(() => lessons.value[lessonIdx.value] || lessons.value[0]);
const progress = computed(() => lessons.value.length ? Math.round((completed.size / lessons.value.length) * 100) : 0);

const quiz = reactive({
  started: false,
  done: false,
  idx: 0,
  score: 0,
  answered: false,
  correct: false,
  picked: null as Letter | null,
  questions: [] as Question[],
});
const currentQuestion = computed<Question>(() => quiz.questions[quiz.idx] || { letter: currentLesson.value.letters[0], options: [] });

function shuffle<T>(items: T[]) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
function selectLesson(index: number) {
  lessonIdx.value = index;
  quiz.started = false;
  quiz.done = false;
}
function speakExample(letter: Letter) {
  if (letter.example) speech.speak(letter.example, coach.value?.ttsLang || "he-IL", 0.82);
}
function startQuiz() {
  const letters = currentLesson.value.letters;
  const all = spec.value?.groups.flatMap((group) => group.letters) || letters;
  quiz.questions = shuffle(letters).map((letter) => ({
    letter,
    options: shuffle([letter, ...shuffle(all.filter((item) => item.char !== letter.char)).slice(0, 3)]),
  }));
  quiz.started = true;
  quiz.done = false;
  quiz.idx = 0;
  quiz.score = 0;
  quiz.answered = false;
  quiz.picked = null;
}
function answer(option: Letter) {
  if (quiz.answered) return;
  quiz.picked = option;
  quiz.correct = option.char === currentQuestion.value.letter.char;
  quiz.answered = true;
  if (quiz.correct) quiz.score++;
}
function optionClass(option: Letter) {
  if (!quiz.answered) return "border-gray-200 text-gray-600 hover:border-indigo-300";
  if (option.char === currentQuestion.value.letter.char) return "border-emerald-400 bg-emerald-50 text-emerald-700";
  if (quiz.picked?.char === option.char) return "border-rose-400 bg-rose-50 text-rose-700";
  return "border-gray-100 text-gray-300";
}
function nextQuestion() {
  if (quiz.idx + 1 < quiz.questions.length) {
    quiz.idx++;
    quiz.answered = false;
    quiz.correct = false;
    quiz.picked = null;
    return;
  }
  quiz.done = true;
  completed.add(lessonIdx.value);
  localStorage.setItem("coach-hbo-alphabet-progress", JSON.stringify([...completed]));
}

onMounted(async () => {
  if (lang.value !== "hbo") {
    await navigateTo(`/coach/${lang.value}/alphabet`, { replace: true });
    return;
  }
  try {
    const [{ coaches }, result] = await Promise.all([
      $fetch<{ coaches: any[] }>("/api/lang/coaches"),
      authedFetch<{ available: boolean; alphabet: AlphabetSpec | null }>("/api/lang/alphabet?language=hbo"),
    ]);
    coach.value = coaches.find((item) => item.language === "hbo");
    if (result.available) spec.value = result.alphabet;
    const saved = JSON.parse(localStorage.getItem("coach-hbo-alphabet-progress") || "[]");
    if (Array.isArray(saved)) saved.filter((item) => Number.isInteger(item)).forEach((item) => completed.add(item));
  } finally {
    loading.value = false;
  }
  tracker.start("hbo", "reading", "hebrew-alphabet-course");
});

onUnmounted(() => speech.stopSpeaking());
</script>
