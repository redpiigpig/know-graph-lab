<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">🗣️ 發音跟讀</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-4">
      <!-- 目標句 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-2">
          <h1 class="text-sm font-semibold text-gray-800">跟讀目標句</h1>
          <button v-if="language === 'en'" @click="randomTarget" class="text-xs text-indigo-600 hover:underline">🎲 隨機句</button>
        </div>
        <textarea v-model="target" rows="2" placeholder="貼上要練的句子，或按「隨機句」…" class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />

        <div class="flex items-center gap-2 mt-3">
          <button v-if="ttsSupported" @click="speak(target)" :disabled="!target.trim()" class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 disabled:opacity-40">🔊 聽範例</button>
          <button v-if="ttsSupported" @click="speak(target, 0.7)" :disabled="!target.trim()" class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 disabled:opacity-40">🐢 慢速</button>
          <button v-if="sttSupported" @click="toggleMic" :disabled="!target.trim()" class="ml-auto text-xs px-4 py-1.5 rounded-lg text-white disabled:opacity-40" :class="listening ? 'bg-rose-500 animate-pulse' : 'bg-violet-600'">{{ listening ? '🎤 聆聽中…點此停' : '🎤 跟讀錄音' }}</button>
        </div>
        <p v-if="!sttSupported" class="text-[11px] text-amber-600 mt-2">此瀏覽器不支援語音辨識，跟讀比對需用 Chrome。</p>
      </div>

      <!-- 結果 -->
      <div v-if="heard || listening" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-400">你的跟讀</span>
          <span v-if="score !== null" class="ml-auto text-sm font-bold" :class="score >= 80 ? 'text-emerald-600' : score >= 60 ? 'text-amber-600' : 'text-rose-600'">吻合 {{ score }}%</span>
        </div>

        <!-- 逐詞 diff（目標句著色：綠=唸到、紅=漏/不準）-->
        <div class="text-[15px] leading-loose">
          <template v-for="(w, i) in targetWords" :key="i">
            <span class="rounded px-0.5" :class="matched.has(i) ? 'text-emerald-700 bg-emerald-50' : 'text-rose-600 bg-rose-50 line-through decoration-rose-300'">{{ w }}</span>
            <span> </span>
          </template>
        </div>
        <div class="text-xs text-gray-400">辨識聽到：「{{ heard || interim || '…' }}」</div>

        <button @click="critique" :disabled="critiquing || !heard" class="text-xs px-3 py-1.5 rounded-lg bg-white border border-indigo-200 text-indigo-700 disabled:opacity-40">{{ critiquing ? '點評中…' : '🧑‍🏫 AI 點評發音' }}</button>
        <div v-if="fb" class="bg-indigo-50/50 rounded-xl p-3">
          <div class="text-sm text-gray-800">{{ fb.comment }}<span v-if="fb.score !== null" class="text-xs text-gray-400">（AI 評 {{ fb.score }}）</span></div>
          <ul v-if="fb.issues?.length" class="mt-1.5 space-y-1">
            <li v-for="(it, i) in fb.issues" :key="i" class="text-xs text-gray-600"><span class="font-medium text-rose-600">{{ it.word }}</span>：{{ it.tip }}</li>
          </ul>
        </div>
      </div>

      <p class="text-center text-[11px] text-gray-400">跟讀＝聽範例→模仿→比對；古典語（希臘/拉丁/希伯來）誦讀也適用。與 <NuxtLink :to="`/coach/${language}/sentences`" class="text-indigo-500 hover:underline">情境實用句</NuxtLink> 一起練</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useCoachAi } from "~/composables/useCoachAi";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const tracker = useActivityTracker();
const ttsSupported = speech.ttsSupported;
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const target = ref("");
const heard = ref("");
const critiquing = ref(false);
const fb = ref<any>(null);
let pool: string[] = [];

function normWords(s: string): string[] {
  return (s.toLowerCase().match(/\p{L}[\p{L}'’\-]*/gu) || []);
}
const targetWords = computed(() => target.value.match(/\p{L}[\p{L}'’\-]*|[^\p{L}\s]+/gu) || []);

// LCS 比對：回傳「目標可點詞」中有被唸到的索引集合
const matched = computed(() => {
  const set = new Set<number>();
  if (!heard.value) return set;
  const T = normWords(target.value), H = normWords(heard.value);
  const dp = Array.from({ length: T.length + 1 }, () => new Array(H.length + 1).fill(0));
  for (let i = 1; i <= T.length; i++) for (let j = 1; j <= H.length; j++)
    dp[i][j] = T[i - 1] === H[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
  const matchedNorm = new Set<number>();
  let i = T.length, j = H.length;
  while (i > 0 && j > 0) {
    if (T[i - 1] === H[j - 1]) { matchedNorm.add(i - 1); i--; j--; }
    else if (dp[i - 1][j] >= dp[i][j - 1]) i--; else j--;
  }
  // 把 normWord 索引映射回 targetWords 裡的「可點詞」位置
  let wi = 0;
  targetWords.value.forEach((w, idx) => {
    if (/\p{L}/u.test(w)) { if (matchedNorm.has(wi)) set.add(idx); wi++; }
  });
  return set;
});
const score = computed(() => {
  if (!heard.value) return null;
  const total = normWords(target.value).length;
  if (!total) return null;
  let m = 0;
  targetWords.value.forEach((w, idx) => { if (/\p{L}/u.test(w) && matched.value.has(idx)) m++; });
  return Math.round((m / total) * 100);
});

function speak(t: string, rate = 1) { if (t.trim()) speech.speak(t, TTS[language.value] || "en-US", rate); }
function toggleMic() {
  if (listening.value) { speech.stopListening(); return; }
  heard.value = ""; fb.value = null;
  speech.startListening(TTS[language.value] || "en-US", (t) => { heard.value = (heard.value ? heard.value + " " : "") + t; });
}

async function critique() {
  if (!heard.value) return;
  critiquing.value = true;
  try {
    fb.value = await aiFetch<any>("/api/lang/pronunciation", { method: "POST", body: { language: language.value, target: target.value, heard: heard.value } });
  } catch (e: any) { fb.value = { comment: e?.data?.message || "點評失敗", score: null, issues: [] }; }
  finally { critiquing.value = false; }
}

async function randomTarget() {
  if (!pool.length) {
    try {
      const r = await authedFetch<any>(`/api/lang/sentences?language=${language.value}`);
      pool = (r.scenarios || []).flatMap((s: any) => s.items.map((it: any) => it.en));
    } catch { /* ignore */ }
  }
  if (pool.length) { target.value = pool[Math.floor(Math.random() * pool.length)]; heard.value = ""; fb.value = null; }
}

onMounted(() => { tracker.start(language.value, "speaking", "shadowing"); });
</script>
