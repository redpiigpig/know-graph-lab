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
          <span v-if="heard" class="ml-auto text-sm font-bold" :class="result.score >= 80 ? 'text-emerald-600' : result.score >= 60 ? 'text-amber-600' : 'text-rose-600'">吻合 {{ result.score }}%</span>
        </div>

        <!-- 逐詞 diff（綠=唸對、琥珀=近似(附聽成什麼)、紅=漏/錯）-->
        <div class="text-[15px] leading-loose" :dir="rtl ? 'rtl' : 'ltr'">
          <template v-for="(t, i) in result.tokens" :key="i">
            <span v-if="!t.isWord" class="text-gray-400">{{ t.text }}</span>
            <span v-else class="rounded px-0.5"
              :class="{
                'text-emerald-700 bg-emerald-50': t.status === 'hit',
                'text-amber-700 bg-amber-50': t.status === 'near',
                'text-rose-600 bg-rose-50 line-through decoration-rose-300': t.status === 'miss',
              }">{{ t.text }}<sup v-if="t.status === 'near' && t.heardAs" class="text-[9px] text-amber-500 no-underline">聽成 {{ t.heardAs }}</sup></span>
            <span> </span>
          </template>
        </div>
        <div v-if="heard" class="flex flex-wrap gap-2 text-[11px]">
          <span class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">✅ 唸對 {{ result.hits }}</span>
          <span v-if="result.near" class="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">🟡 近似 {{ result.near }}</span>
          <span v-if="result.miss" class="px-2 py-0.5 rounded-full bg-rose-50 text-rose-600">❌ 漏/錯 {{ result.miss }}</span>
          <span class="px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">共 {{ result.total }} 詞</span>
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
import { scorePronunciation } from "~/composables/usePronunciationScore";

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
const rtl = computed(() => language.value === "hbo");

const target = ref("");
const heard = ref("");
const critiquing = ref(false);
const fb = ref<any>(null);
let pool: string[] = [];

// 零服務確定性評分：詞級對齊 → 每詞 hit/near/miss + 加權吻合%
const result = computed(() => scorePronunciation(target.value, heard.value));

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
