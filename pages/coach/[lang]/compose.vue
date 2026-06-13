<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">句子重組 · {{ coach?.langLabel }}</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-4">
      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入中…</div>
      <div v-else-if="!available" class="text-sm text-gray-500 py-10 text-center">這個語言還沒有重組題庫。</div>

      <template v-else>
        <div v-if="!started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
          <div>
            <h1 class="text-lg font-bold text-gray-900">句子重組</h1>
            <p class="text-xs text-gray-500 mt-1 leading-relaxed">
              看提示，把打散的詞卡點回正確順序，即時比對。**零 AI、確定性批改**。{{ sourceNote }}
            </p>
          </div>
          <div>
            <div class="text-xs font-semibold text-gray-400 mb-1.5">題數</div>
            <div class="flex gap-2">
              <button v-for="k in [10, 15, 20]" :key="k" @click="qCount = k" :class="cntClass(k)">{{ k }}</button>
            </div>
          </div>
          <p v-if="total === 0" class="text-xs text-amber-600">此語言的例句字庫還在建置中（gloss 補到此語言後自動出現），目前暫無題目。</p>
          <button @click="start" :disabled="total === 0" class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">開始</button>
        </div>

        <div v-else-if="!done" class="space-y-4">
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span>第 {{ idx + 1 }} / {{ items.length }} 題</span>
            <span>✅ {{ score }}　❌ {{ answeredCount - score }}</span>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-4">
            <div class="text-[11px] text-indigo-500 mb-1">{{ cur.prompt }}</div>
            <div v-if="cur.hint" class="text-xs text-gray-400">{{ cur.hint }}</div>
          </div>

          <!-- 作答區 -->
          <div class="bg-white rounded-2xl border border-gray-100 p-4 min-h-[3.5rem]" :dir="rtl ? 'rtl' : 'ltr'">
            <div v-if="!answer.length" class="text-xs text-gray-300">點下方詞卡，依正確順序排這裡</div>
            <div class="flex flex-wrap gap-1.5">
              <button v-for="(w, i) in answer" :key="'a' + i" @click="!answered && removeAt(i)"
                class="px-2.5 py-1.5 rounded-lg text-sm border transition"
                :class="answered ? slotClass(i) : 'bg-indigo-50 border-indigo-200 text-indigo-800 hover:bg-rose-50'">{{ w }}</button>
            </div>
          </div>

          <!-- 詞卡池 -->
          <div v-if="!answered" class="flex flex-wrap gap-1.5" :dir="rtl ? 'rtl' : 'ltr'">
            <button v-for="(w, i) in poolView" :key="'p' + i" @click="pick(i)"
              class="px-2.5 py-1.5 rounded-lg text-sm bg-white border border-gray-200 text-gray-700 hover:border-indigo-300 transition">{{ w.w }}</button>
          </div>

          <div v-if="!answered" class="flex gap-2">
            <button @click="submit" :disabled="answer.length !== cur.words.length"
              class="flex-1 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">
              {{ answer.length === cur.words.length ? '對答案' : `還差 ${cur.words.length - answer.length} 個` }}
            </button>
            <button @click="resetAnswer" class="px-4 py-2 rounded-xl bg-white border border-gray-200 text-gray-500 text-sm hover:border-gray-300">清空</button>
          </div>

          <!-- 答後 -->
          <div v-else class="bg-white rounded-2xl border border-gray-100 p-4">
            <p class="text-sm" :class="allCorrect ? 'text-emerald-600' : 'text-rose-600'">
              {{ allCorrect ? '✅ 完全正確！' : '部分順序有誤' }}
            </p>
            <div v-if="!allCorrect" class="mt-2 text-sm text-gray-700" :dir="rtl ? 'rtl' : 'ltr'">
              正解：<span class="font-medium">{{ cur.words.join(' ') }}</span>
            </div>
            <button @click="next" class="mt-3 w-full py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">
              {{ idx + 1 < items.length ? '下一題 →' : '看結果' }}
            </button>
          </div>
        </div>

        <!-- 結果 -->
        <div v-else class="bg-white rounded-2xl border border-gray-100 p-6 text-center space-y-4">
          <div class="text-4xl">{{ score === items.length ? '🎉' : score / items.length >= 0.7 ? '👍' : '💪' }}</div>
          <div class="text-2xl font-bold text-gray-900">{{ score }} / {{ items.length }}</div>
          <div class="flex gap-2 justify-center">
            <button @click="start" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">再來一輪</button>
            <button @click="reset" class="px-5 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">改題數</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

interface Item { prompt: string; hint: string; words: string[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const tracker = useActivityTracker();

const coach = ref<any>(null);
const loading = ref(true);
const available = ref(false);
const rtl = ref(false);
const total = ref(0);
const items = ref<Item[]>([]);

const sourceNote = computed(() => {
  if (lang.value === "en") return "英文取自情境實用句。";
  if (lang.value === "grc" || lang.value === "hbo") return "原文取自新約／舊約經文，重組＝重建該節的原文詞序。";
  return "句子取自共用字庫的例句。";
});

const started = ref(false);
const done = ref(false);
const idx = ref(0);
const score = ref(0);
const qCount = ref(10);
const answered = ref(false);

// pool：打散的詞卡（含原序索引，避免重複詞 key 衝突）；answer：已選詞（原序索引）
const pool = ref<{ w: string; oi: number }[]>([]);
const answer = ref<string[]>([]);
const answerOi = ref<number[]>([]);

const cur = computed(() => items.value[idx.value] || ({ words: [], prompt: "", hint: "" } as Item));
const answeredCount = computed(() => idx.value + (answered.value ? 1 : 0));
const poolView = computed(() => pool.value.filter((p) => !answerOi.value.includes(p.oi)));
const allCorrect = computed(() => answer.value.length === cur.value.words.length && answer.value.every((w, i) => w === cur.value.words[i]));

function cntClass(k: number) {
  return `text-xs px-4 py-1.5 rounded-lg border transition ${qCount.value === k ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}
function slotClass(i: number) {
  return answer.value[i] === cur.value.words[i]
    ? "bg-emerald-50 border-emerald-400 text-emerald-700"
    : "bg-rose-50 border-rose-400 text-rose-700 line-through decoration-rose-300";
}
function loadQuestion() {
  answered.value = false;
  answer.value = [];
  answerOi.value = [];
  const idxs = cur.value.words.map((_, i) => i);
  for (let i = idxs.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [idxs[i], idxs[j]] = [idxs[j], idxs[i]]; }
  pool.value = idxs.map((oi) => ({ w: cur.value.words[oi], oi }));
}
function pick(viewIdx: number) {
  const item = poolView.value[viewIdx];
  if (!item) return;
  answer.value.push(item.w);
  answerOi.value.push(item.oi);
}
function removeAt(i: number) {
  answer.value.splice(i, 1);
  answerOi.value.splice(i, 1);
}
function resetAnswer() { answer.value = []; answerOi.value = []; }
function submit() {
  if (answer.value.length !== cur.value.words.length) return;
  answered.value = true;
  if (allCorrect.value) score.value++;
}
function next() {
  if (idx.value + 1 < items.value.length) { idx.value++; loadQuestion(); }
  else done.value = true;
}

async function load(n: number) {
  const r = await authedFetch<any>(`/api/lang/compose?language=${lang.value}&n=${n}`);
  available.value = r.available;
  rtl.value = !!r.rtl;
  total.value = r.total || 0;
  items.value = r.items || [];
}
async function start() {
  await load(qCount.value);
  idx.value = 0; score.value = 0; started.value = true; done.value = false;
  loadQuestion();
}
function reset() { started.value = false; done.value = false; }

onMounted(async () => {
  try {
    const [{ coaches }] = await Promise.all([$fetch<{ coaches: any[] }>("/api/lang/coaches"), load(qCount.value)]);
    coach.value = coaches.find((c) => c.language === lang.value);
  } finally {
    loading.value = false;
  }
  tracker.start(lang.value, "writing", "compose");
});
</script>
