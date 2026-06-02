<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">內容沉浸（YouTube / 文章）</span>
    </nav>

    <div class="flex-1 p-5 max-w-3xl mx-auto w-full space-y-5">
      <!-- 輸入 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex gap-2 mb-3">
          <button @click="mode = 'youtube'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'youtube' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">📺 YouTube 影片</button>
          <button @click="mode = 'article'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'article' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">📄 貼上文章</button>
        </div>

        <input v-if="mode === 'youtube'" v-model="url" placeholder="貼上 YouTube 網址（教練會直接看影片，最適合人文講座）" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
        <textarea v-else v-model="text" rows="6" placeholder="貼上一段英文文章 / 論文段落…" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />

        <button @click="analyze" :disabled="analyzing || (mode === 'youtube' ? !url.trim() : !text.trim())" class="mt-3 w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">
          {{ analyzing ? '教練分析中…（影片較長需稍候）' : '讓教練分析並出題' }}
        </button>
        <p v-if="err" class="text-xs text-rose-500 mt-2">{{ err }}</p>
      </div>

      <!-- 分析結果 -->
      <div v-if="content" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
        <div>
          <h2 class="font-bold text-gray-900">{{ content.title }}</h2>
          <p class="text-sm text-gray-600 mt-1.5">{{ content.summary }}</p>
        </div>

        <div v-if="content.analysis.outline?.length">
          <h3 class="text-xs font-semibold text-gray-400 uppercase mb-1.5">重點大綱</h3>
          <ul class="text-sm text-gray-700 space-y-1 list-disc list-inside">
            <li v-for="(o, i) in content.analysis.outline" :key="i">{{ o }}</li>
          </ul>
        </div>

        <div v-if="content.analysis.questions?.length">
          <h3 class="text-xs font-semibold text-gray-400 uppercase mb-1.5">理解測驗（選擇題）</h3>
          <div class="space-y-2">
            <div v-for="(q, i) in content.analysis.questions" :key="i" class="border border-gray-100 rounded-xl p-3">
              <div class="text-sm text-gray-800 mb-1.5">{{ i + 1 }}. {{ q.q }}</div>
              <template v-if="q.options?.length">
                <label v-for="(opt, oi) in q.options" :key="oi" class="flex items-center gap-2 text-sm px-1.5 py-0.5 rounded cursor-pointer" :class="qOptClass(i, opt)">
                  <input type="radio" :name="`q${i}`" :value="optLetter(opt)" v-model="qSel[i]" :disabled="qGraded" class="accent-indigo-600" />
                  <span>{{ opt }}</span>
                </label>
              </template>
              <template v-else>
                <button @click="q._show = !q._show" class="text-xs text-indigo-600 mt-1 hover:underline">{{ q._show ? '隱藏' : '看' }}參考答案</button>
                <div v-if="q._show" class="text-xs text-gray-500 mt-1 bg-gray-50 rounded-lg p-2">{{ q.answer }}</div>
              </template>
            </div>
            <button v-if="hasMcq && !qGraded" @click="gradeQuiz" class="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 text-white">對答案</button>
            <div v-if="qGraded" class="text-xs text-gray-500">答對 {{ qCorrect }}/{{ content.analysis.questions.length }}</div>
          </div>
        </div>

        <div v-if="content.analysis.vocab?.length" class="text-xs text-emerald-600">
          ✅ 已將 {{ content.analysis.vocab.length }} 個關鍵單字加入單字庫（含複習排程）
        </div>
        <div v-if="watchedMsg" class="text-xs text-sky-600">{{ watchedMsg }}</div>

        <!-- 討論 -->
        <div v-if="content.analysis.discussion?.length" class="border-t border-gray-100 pt-4">
          <h3 class="text-xs font-semibold text-gray-400 uppercase mb-2">與教練討論</h3>
          <div class="flex flex-wrap gap-1.5 mb-3">
            <button v-for="(d, i) in content.analysis.discussion" :key="i" @click="askDiscuss(d)" class="text-xs px-2.5 py-1 rounded-full border border-indigo-200 text-indigo-700 bg-indigo-50 hover:bg-indigo-100 transition text-left">{{ d }}</button>
          </div>

          <div class="space-y-3 max-h-96 overflow-y-auto">
            <div v-for="(m, i) in discussion" :key="i" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
              <div class="max-w-[85%] px-3 py-2 rounded-2xl text-sm whitespace-pre-wrap" :class="m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-800'">
                {{ m.content }}
                <div v-if="m.translation" class="text-[11px] opacity-70 mt-1">{{ m.translation }}</div>
              </div>
            </div>
            <div v-if="discussLoading" class="text-xs text-gray-400">教練思考中…</div>
          </div>

          <div class="flex gap-2 mt-3">
            <button v-if="sttSupported" @click="toggleMic" class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500'">🎤</button>
            <input v-model="discussInput" @keydown.enter="sendDiscuss" :placeholder="listening ? (interim || '聆聽中…') : `用${langLabel}回應教練（口說或打字）…`" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
            <button @click="sendDiscuss" :disabled="discussLoading || !discussInput.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40">送出</button>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <button @click="getFeedback" :disabled="scoring || !discussion.some(m=>m.role==='user')" class="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 disabled:opacity-40">{{ scoring ? '評分中…' : '結束給評分' }}</button>
          </div>
          <div v-if="fb" class="mt-2 bg-indigo-50/50 rounded-lg p-2.5">
            <div class="text-sm font-bold text-indigo-700">評分 {{ fb.overall }}/100</div>
            <p class="text-xs text-gray-700 mt-1">{{ fb.comment }}</p>
          </div>
        </div>
      </div>

      <!-- 歷史 -->
      <div v-if="history.length" class="bg-white rounded-2xl border border-gray-100 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-2">最近分析過的內容</h2>
        <div class="space-y-1.5">
          <div v-for="h in history" :key="h.id" class="flex items-center gap-2 text-sm">
            <span>{{ h.source_type === 'youtube' ? '📺' : '📄' }}</span>
            <span class="text-gray-700 truncate flex-1">{{ h.title }}</span>
            <span class="text-[11px] text-gray-300">{{ fmtDate(h.created_at) }}</span>
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
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch } = useCoachAi();

const LANG_LABEL: Record<string, string> = { en: "英文", ja: "日文" };
const TTS_LANG: Record<string, string> = { en: "en-US", ja: "ja-JP" };

const route = useRoute();
const language = computed(() => route.params.lang as string);
const mode = ref<"youtube" | "article">("youtube");
const url = ref("");
const text = ref("");
const analyzing = ref(false);
const err = ref("");
const content = ref<any>(null);
const watchedMsg = ref("");
const history = ref<any[]>([]);

const discussion = ref<any[]>([]);
const discussInput = ref("");
const discussLoading = ref(false);

const speech = useSpeech();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;
const tracker = useActivityTracker();
const langLabel = computed(() => LANG_LABEL[language.value] || "英文");

// 理解測驗（選擇題）
const qSel = ref<Record<number, string>>({});
const qGraded = ref(false);
const qCorrect = ref(0);
const hasMcq = computed(() => !!content.value?.analysis?.questions?.some((q: any) => q.options?.length));
function optLetter(opt: string) { return (opt.trim().match(/^([A-D])/i)?.[1] || "").toUpperCase(); }
function qOptClass(qi: number, opt: string) {
  if (!qGraded.value) return "hover:bg-gray-50";
  const ans = String(content.value.analysis.questions[qi].answer || "").toUpperCase();
  const letter = optLetter(opt);
  if (letter === ans) return "bg-emerald-50 text-emerald-700";
  if (letter === (qSel.value[qi] || "").toUpperCase()) return "bg-rose-50 text-rose-600";
  return "";
}
function gradeQuiz() {
  const qs = content.value.analysis.questions || [];
  let c = 0;
  qs.forEach((q: any, i: number) => { if (q.options?.length && (qSel.value[i] || "").toUpperCase() === String(q.answer).toUpperCase()) c++; });
  qCorrect.value = c;
  qGraded.value = true;
}

// 討論評分
const fb = ref<any>(null);
const scoring = ref(false);
function toggleMic() {
  if (listening.value) speech.stopListening();
  else speech.startListening(TTS_LANG[language.value] || "en-US", (t) => { discussInput.value = (discussInput.value ? discussInput.value + " " : "") + t; });
}
async function getFeedback() {
  if (!content.value?.session_id) return;
  scoring.value = true;
  try {
    const { feedback } = await aiFetch<any>("/api/lang/smalltalk/feedback", { method: "POST", body: { sessionId: content.value.session_id } });
    fb.value = feedback;
  } catch (e: any) {
    alert(e?.data?.message || "評分失敗");
  } finally {
    scoring.value = false;
  }
}

function fmtDate(s: string) {
  return s ? new Date(s).toLocaleDateString("zh-TW", { month: "numeric", day: "numeric" }) : "";
}

async function analyze() {
  analyzing.value = true;
  err.value = "";
  content.value = null;
  discussion.value = [];
  qSel.value = {};
  qGraded.value = false;
  qCorrect.value = 0;
  fb.value = null;
  try {
    const res = await aiFetch<any>("/api/lang/content/ingest", {
      method: "POST",
      body: {
        language: language.value,
        sourceType: mode.value,
        url: mode.value === "youtube" ? url.value.trim() : undefined,
        text: mode.value === "article" ? text.value : undefined,
      },
    });
    // 為每題加 _show 控制
    if (res.content.analysis?.questions) res.content.analysis.questions.forEach((q: any) => (q._show = false));
    content.value = res.content;
    // 影片→聽力，文章→閱讀
    tracker.start(language.value, mode.value === "youtube" ? "listening" : "reading", mode.value);
    if (res.watchedMinutes > 0) watchedMsg.value = `🎧 已將影片時長 ${res.watchedMinutes} 分鐘計入今日聽力時間`;
    else watchedMsg.value = "";
    loadHistory();
  } catch (e: any) {
    err.value = e?.data?.message || "分析失敗，請換一則內容";
  } finally {
    analyzing.value = false;
  }
}

function askDiscuss(d: string) {
  discussInput.value = d;
  sendDiscuss();
}

async function sendDiscuss() {
  const msg = discussInput.value.trim();
  if (!msg || discussLoading.value || !content.value?.session_id) return;
  speech.stopListening();
  discussInput.value = "";
  discussion.value.push({ role: "user", content: msg });
  discussLoading.value = true;
  try {
    const res = await aiFetch<any>("/api/lang/chat", {
      method: "POST",
      body: { language: language.value, sessionId: content.value.session_id, message: msg },
    });
    discussion.value.push({ role: "coach", content: res.reply, translation: res.translation });
    if (res.reply) speech.speak(res.reply, TTS_LANG[language.value] || "en-US");
  } catch (e: any) {
    discussion.value.push({ role: "coach", content: `⚠️ ${e?.data?.message || "討論失敗"}` });
  } finally {
    discussLoading.value = false;
  }
}

async function loadHistory() {
  const { content: c } = await authedFetch<any>(`/api/lang/content?language=${language.value}`);
  history.value = c;
}

onMounted(loadHistory);
</script>
