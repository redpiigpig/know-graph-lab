<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${language}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">今日計畫</span>
      <span class="ml-auto text-xs text-gray-400">{{ todayStr }}</span>
    </nav>

    <div v-if="loading" class="flex-1 flex items-center justify-center text-gray-400 text-sm">教練正在排今天的內容…</div>

    <div v-else-if="daily" class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-5">
      <!-- 進度 -->
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5 text-center">
          <div class="text-2xl font-bold text-emerald-600">{{ daily.vocab.memorized }}</div>
          <div class="text-[11px] text-gray-400">已記住單字</div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5 text-center">
          <div class="text-2xl font-bold text-amber-600">{{ daily.vocab.due }}</div>
          <div class="text-[11px] text-gray-400">待複習</div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5 text-center">
          <div class="text-2xl font-bold text-indigo-600">{{ daily.vocab.pctOfGoal }}%</div>
          <div class="text-[11px] text-gray-400">{{ daily.goalLevel }} 詞彙進度</div>
        </div>
      </div>

      <!-- 今日任務 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-4">
        <h2 class="text-sm font-semibold text-gray-800 mb-2">✅ 今日任務</h2>
        <div class="space-y-1.5">
          <label v-for="t in daily.plan.tasks" :key="t.id" class="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" :checked="t.done" @change="toggle('task', t)" class="accent-emerald-600" />
            <span :class="t.done ? 'line-through text-gray-300' : 'text-gray-700'">{{ t.label }}</span>
          </label>
        </div>
      </div>

      <!-- 今日單字 -->
      <NuxtLink :to="`/coach/${language}/review`" class="block bg-white rounded-2xl border border-gray-100 p-4 hover:border-amber-300 transition">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-semibold text-gray-800">🗂️ 今日單字</div>
            <div class="text-xs text-gray-400">背過 {{ daily.vocab.memorized }} / 共 {{ daily.vocab.total }} 字</div>
          </div>
          <span class="text-sm px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700">{{ daily.vocab.due }} 個待複習 →</span>
        </div>
      </NuxtLink>

      <!-- 閱讀 / 聽力 / 口說 -->
      <div v-for="sec in sections" :key="sec.kind" class="bg-white rounded-2xl border border-gray-100 p-4">
        <h2 class="text-sm font-semibold text-gray-800 mb-2">{{ sec.icon }} {{ sec.label }}</h2>
        <div class="space-y-2">
          <div v-for="item in daily.plan[sec.kind]" :key="item.id" class="border border-gray-100 rounded-xl overflow-hidden">
            <button @click="openItem(sec.kind, item)" class="w-full flex items-center gap-2 px-3 py-2.5 text-left hover:bg-gray-50 transition">
              <span class="text-xs" :class="item.done ? 'text-emerald-500' : 'text-gray-300'">{{ item.done ? '✓' : '○' }}</span>
              <span class="flex-1 text-sm text-gray-700">{{ item.topic || item.prompt }}</span>
              <span class="text-gray-300 text-xs">{{ open === item.id ? '▲' : '▼' }}</span>
            </button>

            <div v-if="open === item.id" class="px-3 pb-3 border-t border-gray-50">
              <div v-if="item._loading" class="text-xs text-gray-400 py-3">生成中…</div>
              <template v-else-if="item.content">
                <!-- 聽力播放 -->
                <div v-if="sec.kind === 'listening'" class="bg-sky-50 rounded-lg p-3 text-center my-2">
                  <button @click="play(item.content.audio_text)" class="px-4 py-1.5 rounded-lg bg-sky-600 text-white text-sm">▶ 播放聽力</button>
                </div>
                <!-- 閱讀短文 -->
                <div v-if="sec.kind === 'reading' && item.content.passage" class="bg-amber-50/40 rounded-lg p-3 text-sm leading-relaxed text-gray-800 whitespace-pre-wrap my-2">{{ item.content.passage }}</div>
                <!-- 口說題 -->
                <div v-if="sec.kind === 'speaking'" class="text-sm text-gray-800 my-2">{{ item.content.prompt }}</div>

                <!-- 選擇題（閱讀/聽力）-->
                <div v-if="item.content.questions?.length" class="space-y-2 my-2">
                  <div v-for="(q, qi) in item.content.questions" :key="qi" class="border border-gray-100 rounded-lg p-2.5">
                    <div class="text-sm text-gray-800 mb-1">{{ qi + 1 }}. {{ q.q }}</div>
                    <label v-for="(opt, oi) in q.options" :key="oi" class="flex items-center gap-2 text-sm px-1.5 py-0.5 rounded cursor-pointer" :class="optClass(item, qi, opt)">
                      <input type="radio" :name="`${item.id}q${qi}`" :value="optLetter(opt)" v-model="item._sel[qi]" :disabled="item._graded" class="accent-indigo-600" />
                      <span>{{ opt }}</span>
                    </label>
                  </div>
                  <button v-if="!item._graded" @click="grade(sec.kind, item)" class="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 text-white">對答案</button>
                  <div v-else class="text-xs text-gray-500">答對 {{ item._correct }}/{{ item.content.questions.length }}</div>
                </div>

                <!-- 討論（口說/打字）+ 即時回饋 -->
                <div class="mt-2 border-t border-gray-50 pt-2">
                  <div class="text-[11px] text-gray-400 mb-1">與教練討論（口說或打字）</div>
                  <div v-if="item._msgs.length" class="space-y-2 max-h-60 overflow-y-auto mb-2">
                    <div v-for="(m, mi) in item._msgs" :key="mi" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
                      <div class="max-w-[85%] px-2.5 py-1.5 rounded-xl text-sm whitespace-pre-wrap" :class="m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-800'">
                        {{ m.content }}
                        <div v-if="m.translation" class="text-[11px] opacity-70">{{ m.translation }}</div>
                        <div v-if="m.corrections?.length" class="mt-1">
                          <div v-for="(c, ci) in m.corrections" :key="ci" class="text-[11px] bg-rose-50 text-rose-600 rounded px-1.5 py-0.5 mt-0.5">{{ c.original }} → {{ c.fixed }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="flex gap-1.5">
                    <button v-if="sttSupported" @click="mic(item)" class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500'">🎤</button>
                    <input v-model="item._input" @keydown.enter="discuss(item)" :placeholder="listening ? (interim || '聆聽中…') : '打字回應…'" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
                    <button @click="discuss(item)" :disabled="item._sending || !item._input?.trim()" class="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40">送</button>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <button @click="getFeedback(item)" :disabled="item._scoring || !item._msgs.some((m:any)=>m.role==='user')" class="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 disabled:opacity-40">{{ item._scoring ? '評分中…' : '結束給評分' }}</button>
                    <button v-if="!item.done" @click="toggle(sec.kind, item)" class="text-xs px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700">標記完成</button>
                  </div>
                  <div v-if="item._fb" class="mt-2 bg-indigo-50/50 rounded-lg p-2.5">
                    <div class="text-sm font-bold text-indigo-700">評分 {{ item._fb.overall }}/100</div>
                    <p class="text-xs text-gray-700 mt-1">{{ item._fb.comment }}</p>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useCoachAi } from "~/composables/useCoachAi";
import { useSpeech } from "~/composables/useSpeech";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const sections = [
  { kind: "reading", label: "今日閱讀（5）", icon: "📖" },
  { kind: "listening", label: "今日聽力（5）", icon: "🎧" },
  { kind: "speaking", label: "今日口說（5）", icon: "🗣️" },
];
const todayStr = new Date().toLocaleDateString("zh-TW", { month: "numeric", day: "numeric" });

const daily = ref<any>(null);
const loading = ref(true);
const open = ref<string | null>(null);

function optLetter(opt: string) { return (opt.trim().match(/^([A-D])/i)?.[1] || "").toUpperCase(); }
function optClass(item: any, qi: number, opt: string) {
  if (!item._graded) return "hover:bg-gray-50";
  const ans = String(item.content.questions[qi].answer || "").toUpperCase();
  const letter = optLetter(opt);
  if (letter === ans) return "bg-emerald-50 text-emerald-700";
  if (letter === (item._sel[qi] || "").toUpperCase()) return "bg-rose-50 text-rose-600";
  return "";
}
function play(t: string) { if (t) speech.speak(t, TTS[language.value] || "en-US"); }

async function load() {
  loading.value = true;
  try {
    const d = await aiFetch<any>(`/api/lang/daily?language=${language.value}`);
    // 初始化每個項目的 UI 狀態
    for (const k of ["reading", "listening", "speaking"]) {
      for (const it of d.plan[k]) Object.assign(it, { _loading: false, _sel: {}, _graded: false, _correct: 0, _msgs: [], _input: "", _sending: false, _scoring: false, _fb: null });
    }
    daily.value = d;
  } finally {
    loading.value = false;
  }
}

async function openItem(kind: string, item: any) {
  if (open.value === item.id) { open.value = null; return; }
  open.value = item.id;
  if (!item.content) {
    item._loading = true;
    try {
      const { item: full } = await aiFetch<any>("/api/lang/daily/item", { method: "POST", body: { language: language.value, kind, id: item.id } });
      item.content = full.content;
      item.session_id = full.session_id;
    } catch (e: any) {
      alert(e?.data?.message || "生成失敗");
    } finally {
      item._loading = false;
    }
  }
}

async function grade(kind: string, item: any) {
  const qs = item.content.questions || [];
  let correct = 0;
  qs.forEach((q: any, i: number) => { if ((item._sel[i] || "").toUpperCase() === String(q.answer).toUpperCase()) correct++; });
  item._correct = correct;
  item._graded = true;
  // 記錄閱讀/聽力時間
  authedFetch("/api/lang/activity", { method: "POST", body: { language: language.value, skill: kind, minutes: 3, source: "daily" } }).catch(() => {});
}

function mic(item: any) {
  if (listening.value) speech.stopListening();
  else speech.startListening(TTS[language.value] || "en-US", (t) => { item._input = (item._input ? item._input + " " : "") + t; });
}

async function discuss(item: any) {
  const text = (item._input || "").trim();
  if (!text || item._sending || !item.session_id) return;
  speech.stopListening();
  item._input = "";
  item._msgs.push({ role: "user", content: text });
  item._sending = true;
  try {
    const res = await aiFetch<any>("/api/lang/chat", { method: "POST", body: { language: language.value, sessionId: item.session_id, message: text } });
    if (res.corrections?.length) { const lu = [...item._msgs].reverse().find((m: any) => m.role === "user"); if (lu) lu.corrections = res.corrections; }
    item._msgs.push({ role: "coach", content: res.reply, translation: res.translation });
    speech.speak(res.reply, TTS[language.value] || "en-US");
  } catch (e: any) {
    item._msgs.push({ role: "coach", content: `⚠️ ${e?.data?.message || "失敗"}` });
  } finally {
    item._sending = false;
  }
}

async function getFeedback(item: any) {
  if (!item.session_id) return;
  item._scoring = true;
  try {
    const { feedback } = await aiFetch<any>("/api/lang/smalltalk/feedback", { method: "POST", body: { sessionId: item.session_id } });
    item._fb = feedback;
  } catch (e: any) {
    alert(e?.data?.message || "評分失敗");
  } finally {
    item._scoring = false;
  }
}

async function toggle(kind: string, item: any) {
  item.done = !item.done;
  await authedFetch("/api/lang/daily/done", { method: "POST", body: { language: language.value, kind, id: item.id, done: item.done } });
}

onMounted(load);
</script>
