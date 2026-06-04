<template>
  <div class="flex flex-col h-dvh bg-slate-50">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 flex-shrink-0">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">限時主題聊（small talk）</span>
      <span v-if="started && persona" class="text-[11px] px-1.5 py-0.5 rounded-full bg-violet-50 text-violet-700">{{ persona.emoji }} {{ persona.label }}</span>
      <div v-if="started" class="ml-auto flex items-center gap-2">
        <span class="text-sm font-bold tabular-nums" :class="remaining <= 30 ? 'text-rose-500' : 'text-gray-700'">⏱ {{ mmss(remaining) }}</span>
        <button @click="endNow" class="text-xs px-2.5 py-1 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition">結束看反饋</button>
      </div>
    </nav>

    <!-- 設定 -->
    <div v-if="!started" class="flex-1 overflow-y-auto p-5 max-w-2xl mx-auto w-full">
      <h1 class="text-lg font-bold text-gray-900">選一個議題，限時開聊</h1>
      <p class="text-sm text-gray-500 mt-1">教練會主動破題，時間到自動給你口語評分（流暢／文法／詞彙／論述）。</p>

      <div class="mt-4">
        <label class="text-xs font-semibold text-gray-500">時長</label>
        <div class="flex gap-2 mt-1">
          <button v-for="d in [3,5,10]" :key="d" @click="duration = d" class="text-sm px-4 py-1.5 rounded-lg border transition" :class="duration === d ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ d }} 分鐘</button>
        </div>
      </div>

      <div class="mt-4">
        <label class="text-xs font-semibold text-gray-500">議題（點選或自訂）</label>
        <div class="flex flex-wrap gap-1.5 mt-1.5">
          <button v-for="t in topics" :key="t" @click="topic = t" class="text-xs px-2.5 py-1 rounded-full border text-left transition" :class="topic === t ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ t }}</button>
        </div>
        <input v-model="topic" placeholder="或自己輸入一個議題…" class="w-full mt-2 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
      </div>

      <button @click="start" :disabled="starting || !topic.trim()" class="mt-5 w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">
        {{ starting ? '教練準備中…' : '開始限時聊' }}
      </button>
    </div>

    <!-- 對話 -->
    <template v-else>
      <div ref="msgArea" class="flex-1 overflow-y-auto px-4 py-5 space-y-4 max-w-2xl mx-auto w-full">
        <div v-for="(m, i) in messages" :key="i" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
          <div class="max-w-[85%]">
            <div class="px-3.5 py-2.5 rounded-2xl text-sm whitespace-pre-wrap" :class="m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-100 text-gray-800 shadow-sm'">
              {{ m.content }}
              <button v-if="m.role === 'coach' && !coach?.voiceless" @click="speak(m.content)" class="ml-1 text-gray-300 hover:text-indigo-500">🔊</button>
            </div>
            <div v-if="m.translation" class="text-[11px] text-gray-400 mt-1 px-1">{{ m.translation }}</div>
            <div v-if="m.corrections?.length" class="mt-1 space-y-1">
              <div v-for="(c, ci) in m.corrections" :key="ci" class="text-xs bg-rose-50 border border-rose-100 rounded-lg px-2 py-1">
                <span class="line-through text-rose-400">{{ c.original }}</span> → <span class="text-emerald-700">{{ c.fixed }}</span>
                <span v-if="c.note" class="block text-gray-500">{{ c.note }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="sending" class="text-xs text-gray-400">教練回覆中…</div>

        <!-- 反饋卡 -->
        <div v-if="feedback" class="bg-white rounded-2xl border-2 border-indigo-100 p-5">
          <h3 class="font-bold text-gray-900 mb-2">⏱ 限時聊結束 — 口語評分</h3>
          <div class="flex items-baseline gap-2 mb-3">
            <span class="text-3xl font-bold text-indigo-600">{{ feedback.overall }}</span><span class="text-sm text-gray-400">/ 100</span>
          </div>
          <div class="grid grid-cols-4 gap-2 mb-3">
            <div v-for="(v, k) in feedback.scores" :key="k" class="text-center bg-gray-50 rounded-lg py-2">
              <div class="text-sm font-bold text-gray-800">{{ v }}</div>
              <div class="text-[10px] text-gray-400">{{ scoreLabel(k) }}</div>
            </div>
          </div>
          <p class="text-sm text-gray-700">{{ feedback.comment }}</p>
          <div v-if="feedback.improvements?.length" class="mt-2 space-y-1">
            <div v-for="(im, i) in feedback.improvements" :key="i" class="text-xs text-rose-600">• {{ im }}</div>
          </div>
          <div class="flex gap-2 mt-4">
            <NuxtLink :to="`/coach/${lang}`" class="flex-1 text-center py-2 rounded-xl bg-indigo-600 text-white text-sm">回首頁</NuxtLink>
            <button @click="reset" class="flex-1 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm">再聊一題</button>
          </div>
        </div>
      </div>

      <!-- 輸入 -->
      <div v-if="!feedback" class="border-t border-gray-100 bg-white px-3 py-2.5 flex-shrink-0">
        <div class="flex items-end gap-2 max-w-2xl mx-auto">
          <button v-if="!coach?.voiceless && sttSupported" @click="toggleMic" class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500'">🎤</button>
          <textarea v-model="input" @keydown.enter.exact.prevent="send" rows="1" :placeholder="listening ? (interim || '聆聽中…') : `用${coach?.langLabel}回應…`" class="flex-1 resize-none px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 max-h-28" />
          <button @click="send" :disabled="sending || !input.trim()" class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 disabled:opacity-40">➤</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const tracker = useActivityTracker();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;

const coach = ref<any>(null);
const topics = ref<string[]>([]);
const topic = ref("");
const duration = ref(5);
const started = ref(false);
const starting = ref(false);
const sessionId = ref<string | null>(null);
const persona = ref<any>(null);
const messages = ref<any[]>([]);
const input = ref("");
const sending = ref(false);
const remaining = ref(0);
const feedback = ref<any>(null);
const msgArea = ref<HTMLElement | null>(null);
let timer: any = null;

const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };
function mmss(s: number) { const m = Math.floor(s / 60); return `${m}:${String(Math.max(0, s % 60)).padStart(2, "0")}`; }
function scoreLabel(k: string) { return ({ fluency: "流暢", grammar: "文法", vocabulary: "詞彙", topic_development: "論述" } as any)[k] || k; }

async function scrollDown() { await nextTick(); if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight; }
function speak(t: string) { speech.speak(t, TTS[lang.value] || "en-US"); }

async function start() {
  starting.value = true;
  try {
    const res = await aiFetch<any>("/api/lang/smalltalk/start", { method: "POST", body: { language: lang.value, topic: topic.value, duration: duration.value } });
    sessionId.value = res.sessionId;
    persona.value = res.persona;
    messages.value = [{ role: "coach", content: res.opening.reply, translation: res.opening.translation }];
    started.value = true;
    remaining.value = duration.value * 60;
    tracker.start(lang.value, "speaking", "smalltalk");
    speak(res.opening.reply);
    timer = setInterval(() => { remaining.value--; if (remaining.value <= 0) endNow(); }, 1000);
    scrollDown();
  } catch (e: any) {
    alert(e?.data?.message || "開始失敗");
  } finally {
    starting.value = false;
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || sending.value) return;
  speech.stopListening();
  input.value = "";
  messages.value.push({ role: "user", content: text, corrections: [] });
  scrollDown();
  sending.value = true;
  try {
    const res = await aiFetch<any>("/api/lang/chat", { method: "POST", body: { language: lang.value, sessionId: sessionId.value, message: text } });
    if (res.corrections?.length) {
      const lu = [...messages.value].reverse().find((m) => m.role === "user");
      if (lu) lu.corrections = res.corrections;
    }
    messages.value.push({ role: "coach", content: res.reply, translation: res.translation });
    speak(res.reply);
    scrollDown();
  } catch (e: any) {
    messages.value.push({ role: "coach", content: `⚠️ ${e?.data?.message || "失敗"}` });
  } finally {
    sending.value = false;
  }
}

function toggleMic() {
  if (listening.value) speech.stopListening();
  else speech.startListening(TTS[lang.value] || "en-US", (t) => { input.value = (input.value ? input.value + " " : "") + t; });
}

async function endNow() {
  if (timer) { clearInterval(timer); timer = null; }
  speech.stopListening();
  await tracker.stop();
  if (!sessionId.value) return;
  try {
    const { feedback: fb } = await aiFetch<any>("/api/lang/smalltalk/feedback", { method: "POST", body: { sessionId: sessionId.value } });
    feedback.value = fb;
    scrollDown();
  } catch (e: any) {
    alert(e?.data?.message || "評分失敗");
  }
}

function reset() {
  started.value = false;
  feedback.value = null;
  messages.value = [];
  sessionId.value = null;
  topic.value = "";
}

async function loadCoach() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === lang.value);
  topics.value = coach.value?.smalltalkTopics || [];
}

onMounted(loadCoach);
onUnmounted(() => { if (timer) clearInterval(timer); });
</script>
