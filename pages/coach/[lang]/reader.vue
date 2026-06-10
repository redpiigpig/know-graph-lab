<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">📖 點讀閱讀器</span>
      <div class="ml-auto flex items-center gap-3">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
        <button v-if="started" @click="started = false" class="text-xs text-indigo-600 hover:underline">換一篇</button>
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full pb-40">
      <!-- 貼上文字 -->
      <div v-if="!started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <h1 class="text-sm font-semibold text-gray-800">貼上要閱讀的文字</h1>
        <p class="text-xs text-gray-400">逐字可點查義；點過的詞會被標成「學習中」（自動進複習）或「已知」，下次遇到自動著色。適合讀原典、論文、文章。</p>
        <textarea v-model="raw" rows="8" placeholder="貼上英文/外語段落…" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />
        <button @click="start" :disabled="!raw.trim()" class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">開始閱讀</button>
      </div>

      <template v-else>
        <!-- 統計 -->
        <div class="flex items-center gap-3 text-[11px] text-gray-500 mb-3">
          <span>共 {{ wordCount }} 詞</span>
          <span class="text-amber-600">● 學習中 {{ counts.learning }}</span>
          <span class="text-gray-400">● 已知 {{ counts.known }}</span>
          <span class="text-indigo-500">● 未標 {{ counts.unknown }}</span>
        </div>

        <!-- 閱讀區 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5 leading-loose text-[15px] text-gray-800 reader">
          <template v-for="(t, i) in tokens" :key="i">
            <span v-if="t.word" @click="selectWord(i)" class="cursor-pointer rounded px-0.5 transition" :class="wordClass(t.text, i)">{{ t.text }}</span>
            <span v-else style="white-space: pre-wrap">{{ t.text }}</span>
          </template>
        </div>
      </template>
    </div>

    <!-- 釋義面板 -->
    <Transition name="slide">
      <div v-if="selected" class="fixed bottom-0 inset-x-0 z-40 bg-white border-t border-gray-200 shadow-2xl">
        <div class="max-w-2xl mx-auto p-4">
          <div class="flex items-center gap-2">
            <div class="text-lg font-bold text-gray-900">{{ selected.text }}</div>
            <span v-if="def?.reading" class="text-xs text-gray-400">{{ def.reading }}</span>
            <button v-if="ttsSupported" @click="speak(def?.lemma || selected.text)" class="text-gray-300 hover:text-indigo-600 text-sm">🔊</button>
            <button @click="selected = null" class="ml-auto text-gray-300 hover:text-gray-600">✕</button>
          </div>
          <div class="mt-1 min-h-[2.5rem]">
            <div v-if="defLoading" class="text-xs text-gray-400">查詢中…</div>
            <template v-else-if="def">
              <div class="text-sm text-gray-800">{{ def.meaning }} <span v-if="def.pos" class="text-[11px] text-gray-400">({{ def.pos }})</span></div>
              <div v-if="def.lemma && def.lemma.toLowerCase() !== selected.text.toLowerCase()" class="text-[11px] text-gray-400 mt-0.5">原形：{{ def.lemma }}</div>
              <div v-if="def.example" class="text-xs text-gray-400 italic mt-0.5">{{ def.example }}</div>
            </template>
          </div>
          <div class="mt-3 flex items-center gap-2">
            <button @click="setStatus('learning')" class="flex-1 py-2 rounded-lg text-sm font-medium transition" :class="curStatus === 'learning' ? 'bg-amber-500 text-white' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'">📒 學習中（加入複習）</button>
            <button @click="setStatus('known')" class="flex-1 py-2 rounded-lg text-sm font-medium transition" :class="curStatus === 'known' ? 'bg-gray-400 text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'">✓ 已知</button>
            <button v-if="curStatus !== 'none'" @click="setStatus('none')" class="px-3 py-2 rounded-lg text-xs text-gray-400 hover:text-rose-500">清除</button>
          </div>
        </div>
      </div>
    </Transition>
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
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const raw = ref("");
const started = ref(false);
const statuses = ref<Record<string, string>>({});
const selectedIdx = ref<number | null>(null);
const def = ref<any>(null);
const defLoading = ref(false);
const defCache = new Map<string, any>();

// 切詞：保留空白/標點，word=true 為可點的詞
const tokens = computed(() => {
  const out: { text: string; word: boolean }[] = [];
  const re = /(\p{L}[\p{L}'’\-]*)|(\s+)|([^\p{L}\s]+)/gu;
  let m: RegExpExecArray | null;
  const text = raw.value;
  while ((m = re.exec(text))) {
    if (m[1]) out.push({ text: m[1], word: true });
    else out.push({ text: m[0], word: false });
  }
  return out;
});
const wordCount = computed(() => tokens.value.filter((t) => t.word).length);
const counts = computed(() => {
  const uniq = new Set<string>();
  let learning = 0, known = 0;
  for (const t of tokens.value) if (t.word) uniq.add(t.text.toLowerCase());
  uniq.forEach((w) => { const s = statuses.value[w]; if (s === "learning") learning++; else if (s === "known") known++; });
  return { learning, known, unknown: uniq.size - learning - known };
});

const selected = computed(() => (selectedIdx.value != null ? tokens.value[selectedIdx.value] : null));
const curStatus = computed(() => (selected.value ? statuses.value[selected.value.text.toLowerCase()] || "none" : "none"));

function wordClass(text: string, i: number) {
  const s = statuses.value[text.toLowerCase()];
  const sel = selectedIdx.value === i ? " ring-2 ring-indigo-300" : "";
  if (s === "learning") return "bg-amber-100 text-amber-900 hover:bg-amber-200" + sel;
  if (s === "known") return "text-gray-400 hover:bg-gray-100" + sel;
  return "hover:bg-indigo-50 underline decoration-dotted decoration-gray-300 underline-offset-2" + sel;
}

// 找出該詞所在句子（往左右走到句末標點）
function sentenceOf(idx: number): string {
  let l = idx, r = idx;
  const isEnd = (s: string) => /[.!?。！？]/.test(s);
  while (l > 0 && !(!tokens.value[l - 1].word && isEnd(tokens.value[l - 1].text))) l--;
  while (r < tokens.value.length - 1 && !(!tokens.value[r].word && isEnd(tokens.value[r].text))) r++;
  return tokens.value.slice(l, r + 1).map((t) => t.text).join("").trim();
}

async function selectWord(i: number) {
  selectedIdx.value = i;
  const word = tokens.value[i].text;
  const key = word.toLowerCase();
  def.value = defCache.get(key) || null;
  if (def.value) return;
  defLoading.value = true;
  try {
    const d = await aiFetch<any>("/api/lang/words/define", { method: "POST", body: { language: language.value, word, sentence: sentenceOf(i) } });
    def.value = d;
    defCache.set(key, d);
  } catch { def.value = { lemma: word, meaning: "查詢失敗，請重試", reading: "", pos: "", example: "" }; }
  finally { defLoading.value = false; }
}

async function setStatus(status: "known" | "learning" | "none") {
  if (!selected.value) return;
  const word = selected.value.text.toLowerCase();
  if (status === "none") delete statuses.value[word];
  else statuses.value[word] = status;
  statuses.value = { ...statuses.value };
  try {
    await authedFetch("/api/lang/words/status", {
      method: "POST",
      body: {
        language: language.value,
        word,
        status,
        lemma: def.value?.lemma || selected.value.text,
        meaning: def.value?.meaning || "",
        reading: def.value?.reading || "",
        sentence: selectedIdx.value != null ? sentenceOf(selectedIdx.value) : "",
      },
    });
  } catch { /* ignore */ }
  if (status !== "none") selected.value && (selectedIdx.value = null);
}

function speak(t: string) { speech.speak(t, TTS[language.value] || "en-US"); }

async function loadStatuses() {
  try {
    const { statuses: s } = await authedFetch<any>(`/api/lang/words/status?language=${language.value}`);
    statuses.value = s || {};
  } catch { /* ignore */ }
}

function start() { started.value = true; selectedIdx.value = null; }

onMounted(() => {
  tracker.start(language.value, "reading", "reader");
  loadStatuses();
});
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.2s ease; }
.slide-enter-from, .slide-leave-to { transform: translateY(100%); }
</style>
