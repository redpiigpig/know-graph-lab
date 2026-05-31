<template>
  <div class="flex flex-col h-dvh bg-slate-50">
    <!-- 頂列 -->
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 flex-shrink-0">
      <NuxtLink to="/coach" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <div>
        <div class="text-sm font-semibold text-gray-900 leading-tight">{{ coach?.name }} <span class="text-xs text-gray-400 font-normal">{{ coach?.langLabel }}教練</span></div>
        <div class="text-[11px] text-gray-400 leading-tight">{{ coach?.accent }}</div>
      </div>

      <div class="ml-auto flex items-center gap-2">
        <button
          v-if="!coach?.voiceless"
          @click="autoSpeak = !autoSpeak"
          class="text-xs px-2.5 py-1 rounded-lg border transition flex items-center gap-1"
          :class="autoSpeak ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-gray-200 text-gray-400'"
          title="教練回覆自動語音播放"
        >
          🔊 自動朗讀
        </button>
        <NuxtLink to="/coach/dashboard" class="text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 transition">📊 儀表板</NuxtLink>
        <button @click="newSession" class="text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 transition">＋ 新對話</button>
      </div>
    </nav>

    <div class="flex-1 flex min-h-0">
      <!-- 左：對話清單 -->
      <aside class="hidden md:flex flex-col w-52 bg-white border-r border-gray-100 flex-shrink-0">
        <div class="px-3 py-2 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">對話紀錄</div>
        <div class="flex-1 overflow-y-auto px-2 pb-2 space-y-1">
          <button
            v-for="s in sessions"
            :key="s.id"
            @click="loadSession(s.id)"
            class="w-full text-left px-2.5 py-2 rounded-lg text-xs transition truncate"
            :class="s.id === sessionId ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50'"
          >
            {{ s.title || '未命名對話' }}
            <span class="block text-[10px] text-gray-400">{{ s.message_count }} 則 · {{ fmtDate(s.updated_at) }}</span>
          </button>
          <div v-if="!sessions.length" class="text-[11px] text-gray-300 px-2 py-3">尚無對話，開始聊天吧</div>
        </div>
      </aside>

      <!-- 中：對話區 -->
      <section class="flex-1 flex flex-col min-w-0">
        <div ref="msgArea" class="flex-1 overflow-y-auto px-4 py-5 space-y-4">
          <!-- 歡迎 -->
          <div v-if="!messages.length && !sending" class="max-w-md mx-auto text-center mt-10">
            <div class="text-5xl mb-3">{{ coach?.emoji }}</div>
            <div class="font-semibold text-gray-800">{{ coach?.name }}</div>
            <p class="text-sm text-gray-500 mt-2">{{ coach?.blurb }}</p>
            <p class="text-xs text-gray-400 mt-3">用文字或麥克風跟我打招呼，我會用{{ coach?.langLabel }}陪你練習、隨時改錯、記新單字、出作業。</p>
          </div>

          <div v-for="(m, i) in messages" :key="m.id || i" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
            <div class="max-w-[80%]">
              <div
                class="px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap"
                :class="m.role === 'user' ? 'bg-indigo-600 text-white rounded-br-md' : 'bg-white border border-gray-100 text-gray-800 rounded-bl-md shadow-sm'"
              >
                {{ m.content }}
                <button
                  v-if="m.role === 'coach' && !coach?.voiceless"
                  @click="replay(m.content)"
                  class="ml-1 text-gray-300 hover:text-indigo-500 transition align-middle"
                  title="再聽一次"
                >🔊</button>
              </div>
              <!-- 繁中對照 -->
              <div v-if="m.role === 'coach' && m.translation" class="text-[11px] text-gray-400 mt-1 px-1">{{ m.translation }}</div>
              <!-- 改錯卡 -->
              <div v-if="m.corrections && m.corrections.length" class="mt-1.5 space-y-1">
                <div v-for="(c, ci) in m.corrections" :key="ci" class="text-xs bg-rose-50 border border-rose-100 rounded-lg px-2.5 py-1.5">
                  <span class="line-through text-rose-400">{{ c.original }}</span>
                  <span class="mx-1 text-gray-300">→</span>
                  <span class="text-emerald-700 font-medium">{{ c.fixed }}</span>
                  <span v-if="c.note" class="block text-gray-500 mt-0.5">💡 {{ c.note }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="sending" class="flex justify-start">
            <div class="px-3.5 py-2.5 rounded-2xl bg-white border border-gray-100 shadow-sm text-gray-400 text-sm">{{ coach?.name }} 正在輸入…</div>
          </div>
        </div>

        <!-- 輸入列 -->
        <div class="border-t border-gray-100 bg-white px-3 py-2.5 flex-shrink-0">
          <div v-if="speechErr" class="text-[11px] text-rose-500 mb-1.5 px-1">{{ speechErr }}</div>
          <div class="flex items-end gap-2">
            <button
              v-if="!coach?.voiceless && sttSupported"
              @click="toggleMic"
              class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition"
              :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'"
              :title="listening ? '停止錄音' : '按住說話'"
            >🎤</button>
            <textarea
              v-model="input"
              @keydown.enter.exact.prevent="send"
              :placeholder="listening ? (interim || '聆聽中…') : `用${coach?.langLabel}輸入…`"
              rows="1"
              class="flex-1 resize-none px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 max-h-32"
            />
            <button
              @click="send"
              :disabled="sending || (!input.trim())"
              class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 disabled:opacity-40 hover:bg-indigo-700 transition"
            >➤</button>
          </div>
        </div>
      </section>

      <!-- 右：單字庫 / 作業 -->
      <aside class="hidden lg:flex flex-col w-72 bg-white border-l border-gray-100 flex-shrink-0">
        <div class="flex border-b border-gray-100">
          <button @click="panel = 'vocab'" class="flex-1 py-2.5 text-xs font-medium transition" :class="panel === 'vocab' ? 'text-indigo-700 border-b-2 border-indigo-600' : 'text-gray-400'">📚 單字庫 ({{ vocab.length }})</button>
          <button @click="panel = 'homework'" class="flex-1 py-2.5 text-xs font-medium transition" :class="panel === 'homework' ? 'text-indigo-700 border-b-2 border-indigo-600' : 'text-gray-400'">✍️ 作業 ({{ homework.length }})</button>
        </div>

        <!-- 單字庫 -->
        <div v-if="panel === 'vocab'" class="flex-1 overflow-y-auto p-2.5 space-y-2">
          <div v-for="v in vocab" :key="v.id" class="border border-gray-100 rounded-xl p-2.5 group">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-semibold text-gray-800 text-sm">{{ v.word }}</span>
                <span v-if="v.reading" class="text-[11px] text-gray-400 ml-1">{{ v.reading }}</span>
              </div>
              <button @click="delVocab(v)" class="text-gray-200 group-hover:text-rose-400 text-xs transition">✕</button>
            </div>
            <div class="text-xs text-gray-600 mt-0.5">{{ v.meaning }}</div>
            <div v-if="v.example" class="text-[11px] text-gray-400 mt-1 italic">{{ v.example }}</div>
            <div class="flex gap-0.5 mt-1.5">
              <button v-for="n in 5" :key="n" @click="setMastery(v, n)" class="text-xs" :title="`熟練度 ${n}`">
                <span :class="n <= v.mastery_level ? 'text-amber-400' : 'text-gray-200'">★</span>
              </button>
            </div>
          </div>
          <div v-if="!vocab.length" class="text-[11px] text-gray-300 text-center py-6">對話中學到的新單字會自動收進這裡</div>
        </div>

        <!-- 作業 -->
        <div v-if="panel === 'homework'" class="flex-1 overflow-y-auto p-2.5 space-y-2.5">
          <div v-for="h in homework" :key="h.id" class="border border-gray-100 rounded-xl p-3">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-800">{{ h.topic }}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded-full"
                :class="h.status === 'graded' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
                {{ h.status === 'graded' ? `已批改 ${h.score ?? ''}` : '待繳交' }}
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1.5 whitespace-pre-wrap">{{ h.prompt }}</p>

            <template v-if="h.status !== 'graded'">
              <textarea v-model="h._draft" rows="3" placeholder="在此作答…" class="w-full mt-2 resize-none px-2.5 py-2 rounded-lg border border-gray-200 text-xs focus:outline-none focus:border-indigo-400" />
              <button @click="submitHw(h)" :disabled="h._grading || !h._draft?.trim()" class="mt-1.5 w-full py-1.5 rounded-lg bg-indigo-600 text-white text-xs disabled:opacity-40 hover:bg-indigo-700 transition">
                {{ h._grading ? '批改中…' : '繳交給' + (coach?.name || '教練') + '批改' }}
              </button>
            </template>

            <div v-else class="mt-2 space-y-1.5">
              <div class="text-[11px] text-gray-500 bg-gray-50 rounded-lg p-2 whitespace-pre-wrap">{{ h.feedback }}</div>
              <div v-for="(c, ci) in (h.corrections || [])" :key="ci" class="text-[11px] bg-rose-50 rounded-lg px-2 py-1">
                <span class="line-through text-rose-400">{{ c.original }}</span> → <span class="text-emerald-700">{{ c.fixed }}</span>
                <span v-if="c.note" class="block text-gray-500">{{ c.note }}</span>
              </div>
            </div>
          </div>
          <div v-if="!homework.length" class="text-[11px] text-gray-300 text-center py-6">請教練「出個作業」，題目會出現在這裡</div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const tracker = useActivityTracker();
const { aiFetch } = useCoachAi();
const route = useRoute();
const lang = computed(() => route.params.lang as string);

const coach = ref<any>(null);
const sessions = ref<any[]>([]);
const sessionId = ref<string | null>(null);
const messages = ref<any[]>([]);
const vocab = ref<any[]>([]);
const homework = ref<any[]>([]);
const input = ref("");
const sending = ref(false);
const panel = ref<"vocab" | "homework">("vocab");
const autoSpeak = ref(true);
const msgArea = ref<HTMLElement | null>(null);

const speech = useSpeech();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;
const speechErr = speech.error;

function fmtDate(s: string) {
  if (!s) return "";
  return new Date(s).toLocaleDateString("zh-TW", { month: "numeric", day: "numeric" });
}

async function scrollDown() {
  await nextTick();
  if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight;
}

async function loadCoachMeta() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === lang.value);
}

async function loadSessions() {
  const { sessions: s } = await authedFetch<{ sessions: any[] }>(`/api/lang/sessions?language=${lang.value}`);
  sessions.value = s;
}

async function loadSession(id: string) {
  sessionId.value = id;
  const { messages: m } = await authedFetch<{ messages: any[] }>(`/api/lang/messages?sessionId=${id}`);
  messages.value = m;
  scrollDown();
}

function newSession() {
  sessionId.value = null;
  messages.value = [];
}

async function loadVocab() {
  const { vocab: v } = await authedFetch<{ vocab: any[] }>(`/api/lang/vocab?language=${lang.value}`);
  vocab.value = v;
}

async function loadHomework() {
  const { homework: h } = await authedFetch<{ homework: any[] }>(`/api/lang/homework?language=${lang.value}`);
  homework.value = h.map((x) => ({ ...x, _draft: x.submission || "", _grading: false }));
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
    const res = await aiFetch<any>("/api/lang/chat", {
      method: "POST",
      body: { language: lang.value, sessionId: sessionId.value, message: text },
    });
    sessionId.value = res.sessionId;
    messages.value.push({
      role: "coach",
      content: res.reply,
      translation: res.translation,
      corrections: [],
    });
    // 把改錯掛到剛剛那則 user 訊息
    if (res.corrections?.length) {
      const lastUser = [...messages.value].reverse().find((m) => m.role === "user");
      if (lastUser) lastUser.corrections = res.corrections;
    }
    scrollDown();
    if (autoSpeak.value && !coach.value?.voiceless && res.reply) {
      speech.speak(res.reply, coach.value.ttsLang);
    }
    // 刷新側欄
    if (res.new_vocab?.length) loadVocab();
    if (res.homework) loadHomework();
    loadSessions();
  } catch (e: any) {
    messages.value.push({ role: "coach", content: `⚠️ ${e?.data?.message || e?.message || "對話失敗"}`, corrections: [] });
    scrollDown();
  } finally {
    sending.value = false;
  }
}

function toggleMic() {
  if (listening.value) {
    speech.stopListening();
  } else {
    speech.startListening(coach.value?.bcp47 || "en-US", (finalText) => {
      input.value = (input.value ? input.value + " " : "") + finalText;
    });
  }
}

function replay(text: string) {
  if (coach.value) speech.speak(text, coach.value.ttsLang);
}

async function setMastery(v: any, n: number) {
  const level = v.mastery_level === n ? n - 1 : n;
  v.mastery_level = level;
  await authedFetch(`/api/lang/vocab/${v.id}`, { method: "PATCH", body: { mastery_level: level } });
}

async function delVocab(v: any) {
  await authedFetch(`/api/lang/vocab/${v.id}`, { method: "DELETE" });
  vocab.value = vocab.value.filter((x) => x.id !== v.id);
}

async function submitHw(h: any) {
  if (!h._draft?.trim()) return;
  h._grading = true;
  try {
    const { homework: updated } = await authedFetch<any>(`/api/lang/homework/${h.id}/submit`, {
      method: "POST",
      body: { submission: h._draft },
    });
    Object.assign(h, updated, { _grading: false });
  } catch (e: any) {
    h._grading = false;
    alert(e?.data?.message || "批改失敗");
  }
}

watch(lang, async () => {
  newSession();
  await tracker.stop();
  tracker.start(lang.value, "speaking", "chat");
  await Promise.all([loadCoachMeta(), loadSessions(), loadVocab(), loadHomework()]);
});

onMounted(async () => {
  // 對話練習時間記為「說」技能（會話練習）
  tracker.start(lang.value, "speaking", "chat");
  await Promise.all([loadCoachMeta(), loadSessions(), loadVocab(), loadHomework()]);
});
</script>
