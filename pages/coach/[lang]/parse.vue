<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${lang}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">詞形判析 · {{ coach?.langLabel }}</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-3xl mx-auto w-full space-y-4">
      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入題庫中…</div>
      <div v-else-if="!available" class="text-sm text-gray-500 py-10 text-center">這個語言還沒有詞形判析題庫。</div>

      <template v-else>
        <!-- 開始前 -->
        <div v-if="!started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
          <div>
            <h1 class="text-lg font-bold text-gray-900">詞形判析（parsing）</h1>
            <p class="text-xs text-gray-500 mt-1 leading-relaxed">
              出自新約原文（STEPBible 黃金標註）。看經文中的目標字，逐項判斷它的詞形（格／數／性、時態／語態／語氣／人稱…），即時對答案。**完全不用 AI、不會出錯**。題庫 {{ total }} 題。
            </p>
          </div>
          <div>
            <div class="text-xs font-semibold text-gray-400 mb-1.5">題數</div>
            <div class="flex gap-2">
              <button v-for="n in [10, 15, 20]" :key="n" @click="qCount = n" :class="cntClass(n)">{{ n }}</button>
            </div>
          </div>
          <button @click="start" class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">開始</button>
        </div>

        <!-- 作答中 -->
        <div v-else-if="!done" class="space-y-4">
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span>第 {{ idx + 1 }} / {{ items.length }} 題</span>
            <span>✅ {{ score }}　❌ {{ answeredCount - score }}</span>
          </div>

          <!-- 經文脈絡 -->
          <div class="bg-white rounded-2xl border border-gray-100 p-4">
            <div class="text-[11px] text-indigo-500 mb-1.5">{{ cur.ref }}</div>
            <p class="text-lg leading-loose text-gray-700" :dir="rtl ? 'rtl' : 'ltr'">
              <span v-for="(w, i) in verseWords" :key="i"
                :class="i === cur.target_idx ? 'bg-amber-200 text-gray-900 font-bold rounded px-1' : ''">{{ w }} </span>
            </p>
            <div class="mt-2 text-xs text-gray-400">
              目標字：<span class="text-gray-700 font-semibold" :dir="rtl ? 'rtl' : 'ltr'">{{ cur.surface }}</span>
              <span v-if="cur.translit"> （{{ cur.translit }}）</span>
              · 詞性 <span class="text-gray-600">{{ cur.pos }}</span>
            </div>
          </div>

          <!-- 逐維度選答 -->
          <div class="bg-white rounded-2xl border border-gray-100 p-4 space-y-3">
            <div v-for="f in cur.fields" :key="f.k">
              <div class="text-xs font-semibold text-gray-500 mb-1.5">{{ dimLabels[f.k] || f.k }}</div>
              <div class="flex flex-wrap gap-1.5">
                <button v-for="opt in options[f.k]" :key="opt" @click="choose(f.k, opt)" :disabled="answered"
                  class="text-xs px-3 py-1.5 rounded-lg border transition disabled:cursor-default"
                  :class="optClass(f, opt)">{{ opt }}</button>
              </div>
            </div>

            <button v-if="!answered" @click="submit" :disabled="!allChosen"
              class="w-full mt-1 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">
              {{ allChosen ? '對答案' : '請選完每一項' }}
            </button>

            <!-- 答後回饋 -->
            <div v-else class="pt-1">
              <p class="text-sm" :class="allCorrect ? 'text-emerald-600' : 'text-rose-600'">
                {{ allCorrect ? '✅ 全對！' : '部分有誤，正解見上方綠色' }}
              </p>
              <p class="text-xs text-gray-500 mt-1">
                <span :dir="rtl ? 'rtl' : 'ltr'">{{ cur.surface }}</span> ← 原形 <span :dir="rtl ? 'rtl' : 'ltr'" class="font-semibold">{{ cur.lemma }}</span>
                <span v-if="cur.gloss" class="text-gray-400">（{{ cur.gloss }}）</span>
                <span class="text-gray-300"> · {{ cur.code }}</span>
              </p>
              <button @click="next" class="mt-3 w-full py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">
                {{ idx + 1 < items.length ? '下一題 →' : '看結果' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 結果 -->
        <div v-else class="bg-white rounded-2xl border border-gray-100 p-6 text-center space-y-4">
          <div class="text-4xl">{{ score === items.length ? '🎉' : score / items.length >= 0.7 ? '👍' : '💪' }}</div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ score }} / {{ items.length }}</div>
            <div class="text-xs text-gray-400 mt-1">全對率 {{ Math.round((score / items.length) * 100) }}%</div>
          </div>
          <div v-if="wrong.length" class="text-left">
            <div class="text-xs font-semibold text-rose-400 mb-1.5">答錯的字（再看一次）</div>
            <div class="space-y-1.5">
              <div v-for="(w, i) in wrong" :key="i" class="text-xs text-gray-600 flex flex-wrap gap-x-2">
                <span :dir="rtl ? 'rtl' : 'ltr'" class="font-semibold text-gray-800">{{ w.surface }}</span>
                <span class="text-gray-400">{{ w.ref }}</span>
                <span class="text-gray-500">{{ w.fields.map((f) => f.gold).join('‧') }}</span>
                <span class="text-gray-300">{{ w.code }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2 justify-center pt-1">
            <button @click="start" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">再來一輪</button>
            <button @click="reset" class="px-5 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">改題數</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

interface Field { k: string; gold: string }
interface Item { ref: string; verse_words: string[]; target_idx: number; surface: string; translit: string; lemma: string; gloss: string; pos: string; code: string; fields: Field[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const tracker = useActivityTracker();

const coach = ref<any>(null);
const loading = ref(true);
const available = ref(false);
const rtl = ref(false);
const total = ref(0);
const options = ref<Record<string, string[]>>({});
const dimLabels = ref<Record<string, string>>({});
const items = ref<Item[]>([]);

const started = ref(false);
const done = ref(false);
const idx = ref(0);
const score = ref(0);
const wrong = ref<Item[]>([]);
const qCount = ref(10);
const answered = ref(false);
const picks = reactive<Record<string, string>>({});

const cur = computed(() => items.value[idx.value] || ({ fields: [], verse_words: [], target_idx: -1 } as unknown as Item));
const verseWords = computed(() => cur.value.verse_words || []);
const answeredCount = computed(() => idx.value + (answered.value ? 1 : 0));
const allChosen = computed(() => cur.value.fields.every((f) => picks[f.k]));
const allCorrect = computed(() => cur.value.fields.every((f) => picks[f.k] === f.gold));

function cntClass(n: number) {
  return `text-xs px-4 py-1.5 rounded-lg border transition ${qCount.value === n ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}
function optClass(f: Field, opt: string) {
  if (!answered.value) return picks[f.k] === opt ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300";
  if (opt === f.gold) return "bg-emerald-50 border-emerald-400 text-emerald-700 font-semibold";
  if (picks[f.k] === opt) return "bg-rose-50 border-rose-400 text-rose-700";
  return "bg-white border-gray-200 text-gray-300";
}
function choose(k: string, opt: string) {
  if (answered.value) return;
  picks[k] = opt;
}
function clearPicks() {
  for (const k of Object.keys(picks)) delete picks[k];
}
function submit() {
  if (!allChosen.value || answered.value) return;
  answered.value = true;
  if (allCorrect.value) score.value++;
  else wrong.value.push(cur.value);
}
function next() {
  if (idx.value + 1 < items.value.length) {
    idx.value++; answered.value = false; clearPicks();
  } else {
    done.value = true;
  }
}

async function load(n: number) {
  const r = await authedFetch<any>(`/api/lang/parse?language=${lang.value}&n=${n}`);
  available.value = r.available;
  rtl.value = !!r.rtl;
  total.value = r.total || 0;
  options.value = r.options || {};
  dimLabels.value = r.dimLabels || {};
  items.value = r.items || [];
}
async function start() {
  await load(qCount.value);
  idx.value = 0; score.value = 0; wrong.value = []; clearPicks();
  answered.value = false; started.value = true; done.value = false;
}
function reset() {
  started.value = false; done.value = false;
}

onMounted(async () => {
  try {
    const [{ coaches }] = await Promise.all([$fetch<{ coaches: any[] }>("/api/lang/coaches"), load(qCount.value)]);
    coach.value = coaches.find((c) => c.language === lang.value);
  } finally {
    loading.value = false;
  }
  tracker.start(lang.value, "reading", "parse");
});
</script>
