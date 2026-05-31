<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/coach" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">技能練習 / 考試模擬</span>
      <select v-model="language" class="ml-auto text-xs border border-gray-200 rounded-lg px-2 py-1">
        <option value="en">英文</option>
        <option value="ja">日文</option>
      </select>
    </nav>

    <div class="flex-1 p-5 max-w-3xl mx-auto w-full space-y-5">
      <!-- 設定 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex gap-2 mb-4">
          <button @click="mode = 'practice'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'practice' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">📝 一般練習</button>
          <button @click="mode = 'exam'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'exam' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">🎯 考試模擬</button>
        </div>

        <div v-if="mode === 'exam'" class="mb-3">
          <label class="text-xs font-semibold text-gray-500">考試</label>
          <div class="flex gap-2 mt-1">
            <button v-for="e in ['TOEFL','IELTS','GRE']" :key="e" @click="exam = e" class="text-xs px-3 py-1.5 rounded-lg border transition" :class="exam === e ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ e }}</button>
          </div>
        </div>

        <label class="text-xs font-semibold text-gray-500">技能</label>
        <div class="grid grid-cols-4 gap-2 mt-1">
          <button v-for="s in SKILLS" :key="s.key" @click="skill = s.key" class="py-2 rounded-xl border text-sm transition" :class="skill === s.key ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">
            {{ s.icon }} {{ s.label }}
          </button>
        </div>

        <input v-model="topic" placeholder="（選填）指定主題，如：康德的義務論 / 文藝復興" class="w-full mt-3 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />

        <button @click="generate" :disabled="generating || (mode === 'exam' && !exam)" class="mt-3 w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">
          {{ generating ? '出題中…' : '出一題' }}
        </button>
      </div>

      <!-- 題目 -->
      <div v-if="task" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
        <div class="flex items-center gap-2">
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700">{{ task.exam || '練習' }} · {{ skillLabel(task.skill) }}</span>
          <span class="text-[11px] text-gray-400">{{ task.topic }}</span>
        </div>

        <!-- 聽力：播放控制（不顯示聽稿） -->
        <div v-if="task.skill === 'listening'" class="bg-sky-50 rounded-xl p-4 text-center">
          <button @click="playAudio" class="px-5 py-2 rounded-xl bg-sky-600 text-white text-sm font-medium">{{ speech.speaking.value ? '⏸ 播放中…' : '▶ 播放聽力' }}</button>
          <p class="text-[11px] text-sky-700/70 mt-2">用系統語音朗讀，可重複播放</p>
        </div>

        <!-- 閱讀：顯示短文 -->
        <div v-if="task.skill === 'reading' && task.materials.passage" class="bg-amber-50/50 rounded-xl p-4 text-sm leading-relaxed text-gray-800 whitespace-pre-wrap">{{ task.materials.passage }}</div>

        <!-- 題目本體 -->
        <div class="text-sm text-gray-800 whitespace-pre-wrap font-medium">{{ task.prompt }}</div>
        <p v-if="task.materials.tip && task.status !== 'scored'" class="text-xs text-gray-400">💡 {{ task.materials.tip }}</p>

        <!-- 選擇題 -->
        <div v-if="task.materials.questions?.length" class="space-y-3">
          <div v-for="(q, i) in task.materials.questions" :key="i" class="border border-gray-100 rounded-xl p-3">
            <div class="text-sm text-gray-800 mb-2">{{ i + 1 }}. {{ q.q }}</div>
            <div class="space-y-1">
              <label v-for="(opt, oi) in q.options" :key="oi" class="flex items-center gap-2 text-sm px-2 py-1 rounded-lg cursor-pointer transition"
                :class="optionClass(i, opt)">
                <input type="radio" :name="`q${i}`" :value="optLetter(opt)" v-model="selected[i]" :disabled="task.status === 'scored'" class="accent-indigo-600" />
                <span>{{ opt }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 產出型作答 -->
        <div v-if="isProduction && task.status !== 'scored'">
          <div v-if="task.skill === 'speaking' && sttSupported" class="mb-2">
            <button @click="toggleMic" class="text-xs px-3 py-1.5 rounded-lg transition" :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-600'">🎤 {{ listening ? '停止錄音' : '口說作答（轉文字）' }}</button>
            <span v-if="interim" class="text-xs text-gray-400 ml-2">{{ interim }}</span>
          </div>
          <textarea v-model="response" rows="6" :placeholder="task.skill === 'speaking' ? '口說內容會轉成文字在此（也可直接打字）…' : '在此作答…'" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />
        </div>

        <!-- 提交 -->
        <button v-if="task.status !== 'scored'" @click="submit" :disabled="scoring" class="w-full py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-emerald-700 transition">
          {{ scoring ? '批改中…' : '提交批改' }}
        </button>

        <!-- 結果 -->
        <div v-if="task.status === 'scored'" class="border-t border-gray-100 pt-4 space-y-3">
          <div class="flex items-baseline gap-2">
            <span class="text-sm text-gray-500">分數</span>
            <span class="text-2xl font-bold text-indigo-600">{{ task.band }}</span>
            <span v-if="task.scores?.total" class="text-sm text-gray-400">/ {{ task.scores.total }} 題</span>
          </div>
          <div v-if="task.scores && !task.scores.total" class="flex flex-wrap gap-2">
            <span v-for="(v, k) in task.scores" :key="k" class="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ k }}: {{ v }}</span>
          </div>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ task.feedback }}</p>
          <div v-if="task.scores?.detail" class="space-y-1">
            <div v-for="(d, i) in task.scores.detail" :key="i" class="text-xs flex items-center gap-2">
              <span :class="d.correct ? 'text-emerald-600' : 'text-rose-500'">{{ d.correct ? '✓' : '✗' }}</span>
              <span class="text-gray-500">第 {{ i + 1 }} 題：你選 {{ d.your || '—' }}，正解 {{ d.answer }}</span>
            </div>
          </div>
          <button @click="reset" class="w-full py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">再來一題</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch } = useCoachAi();

const SKILLS = [
  { key: "listening", label: "聽", icon: "🎧" },
  { key: "speaking", label: "說", icon: "🗣️" },
  { key: "reading", label: "讀", icon: "📖" },
  { key: "writing", label: "寫", icon: "✍️" },
];
const TTS_LANG: Record<string, string> = { en: "en-US", ja: "ja-JP" };

const language = ref("en");
const mode = ref<"practice" | "exam">("practice");
const exam = ref("TOEFL");
const skill = ref("reading");
const topic = ref("");
const generating = ref(false);
const scoring = ref(false);
const task = ref<any>(null);
const selected = ref<string[]>([]);
const response = ref("");
let startedAt = 0;

const speech = useSpeech();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;

const isProduction = computed(() => task.value && (task.value.skill === "writing" || task.value.skill === "speaking"));

function skillLabel(k: string) {
  return SKILLS.find((s) => s.key === k)?.label || k;
}
function optLetter(opt: string) {
  return (opt.trim().match(/^([A-D])/i)?.[1] || opt.trim()[0] || "").toUpperCase();
}
function optionClass(qi: number, opt: string) {
  if (task.value?.status !== "scored") return "hover:bg-gray-50";
  const ans = String(task.value.materials.questions[qi].answer || "").toUpperCase();
  const letter = optLetter(opt);
  if (letter === ans) return "bg-emerald-50 text-emerald-700";
  if (letter === (selected.value[qi] || "").toUpperCase()) return "bg-rose-50 text-rose-600";
  return "";
}

async function generate() {
  generating.value = true;
  task.value = null;
  selected.value = [];
  response.value = "";
  try {
    const res = await aiFetch<any>("/api/lang/task/generate", {
      method: "POST",
      body: { language: language.value, mode: mode.value, exam: mode.value === "exam" ? exam.value : undefined, skill: skill.value, topic: topic.value || undefined },
    });
    task.value = res.task;
    startedAt = Date.now();
    if (task.value.skill === "listening") setTimeout(playAudio, 400);
  } catch (e: any) {
    alert(e?.data?.message || "出題失敗");
  } finally {
    generating.value = false;
  }
}

function playAudio() {
  const t = task.value?.materials?.audio_text;
  if (t) speech.speak(t, TTS_LANG[language.value] || "en-US");
}

function toggleMic() {
  if (listening.value) speech.stopListening();
  else speech.startListening(TTS_LANG[language.value] || "en-US", (txt) => { response.value = (response.value ? response.value + " " : "") + txt; });
}

async function submit() {
  scoring.value = true;
  const minutes = Math.max(0.5, (Date.now() - startedAt) / 60000);
  try {
    const body: any = { minutes };
    if (task.value.materials.questions?.length) body.answers = selected.value;
    else body.response = response.value;
    const res = await aiFetch<any>(`/api/lang/task/${task.value.id}/answer`, { method: "POST", body });
    task.value = { ...res.task, materials: task.value.materials };
  } catch (e: any) {
    alert(e?.data?.message || "批改失敗");
  } finally {
    scoring.value = false;
  }
}

function reset() {
  task.value = null;
  selected.value = [];
  response.value = "";
}
</script>
