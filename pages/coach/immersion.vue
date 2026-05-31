<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/coach" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">內容沉浸（YouTube / 文章）</span>
      <select v-model="language" class="ml-auto text-xs border border-gray-200 rounded-lg px-2 py-1">
        <option value="en">英文</option>
        <option value="ja">日文</option>
      </select>
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
          <h3 class="text-xs font-semibold text-gray-400 uppercase mb-1.5">理解測驗</h3>
          <div class="space-y-2">
            <div v-for="(q, i) in content.analysis.questions" :key="i" class="border border-gray-100 rounded-xl p-3">
              <div class="text-sm text-gray-800">{{ i + 1 }}. {{ q.q }}</div>
              <button @click="q._show = !q._show" class="text-xs text-indigo-600 mt-1.5 hover:underline">{{ q._show ? '隱藏' : '看' }}參考答案</button>
              <div v-if="q._show" class="text-xs text-gray-500 mt-1.5 bg-gray-50 rounded-lg p-2">{{ q.answer }}</div>
            </div>
          </div>
        </div>

        <div v-if="content.analysis.vocab?.length" class="text-xs text-emerald-600">
          ✅ 已將 {{ content.analysis.vocab.length }} 個關鍵單字加入單字庫（含複習排程）
        </div>

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
            <input v-model="discussInput" @keydown.enter="sendDiscuss" :placeholder="`用${langLabel}回應教練…`" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
            <button @click="sendDiscuss" :disabled="discussLoading || !discussInput.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40">送出</button>
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
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const LANG_LABEL: Record<string, string> = { en: "英文", ja: "日文" };
const TTS_LANG: Record<string, string> = { en: "en-US", ja: "ja-JP" };

const language = ref("en");
const mode = ref<"youtube" | "article">("youtube");
const url = ref("");
const text = ref("");
const analyzing = ref(false);
const err = ref("");
const content = ref<any>(null);
const history = ref<any[]>([]);

const discussion = ref<any[]>([]);
const discussInput = ref("");
const discussLoading = ref(false);

const speech = useSpeech();
const tracker = useActivityTracker();
const langLabel = computed(() => LANG_LABEL[language.value] || "英文");

function fmtDate(s: string) {
  return s ? new Date(s).toLocaleDateString("zh-TW", { month: "numeric", day: "numeric" }) : "";
}

async function analyze() {
  analyzing.value = true;
  err.value = "";
  content.value = null;
  discussion.value = [];
  try {
    const res = await authedFetch<any>("/api/lang/content/ingest", {
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
  discussInput.value = "";
  discussion.value.push({ role: "user", content: msg });
  discussLoading.value = true;
  try {
    const res = await authedFetch<any>("/api/lang/chat", {
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
