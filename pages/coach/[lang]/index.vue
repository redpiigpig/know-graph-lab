<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/coach" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">{{ coach?.name }} · {{ coach?.langLabel }}</span>
      <NuxtLink :to="`/coach/${lang}/dashboard`" class="ml-auto text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 transition">📊 總儀表板</NuxtLink>
    </nav>

    <div class="flex-1 p-5 max-w-4xl mx-auto w-full space-y-5">
      <!-- 教練主動簡報 -->
      <div class="flex gap-3">
        <div class="text-4xl flex-shrink-0">{{ coach?.emoji }}</div>
        <div class="flex-1 bg-white rounded-2xl rounded-tl-md border border-gray-100 shadow-sm p-4">
          <div v-if="briefingLoading" class="text-sm text-gray-400">{{ coach?.name }} 正在看你的進度…</div>
          <template v-else-if="briefing">
            <div class="flex items-start justify-between gap-2">
              <p class="text-sm text-gray-800 font-medium">{{ briefing.greeting }}</p>
              <button @click="loadBriefing(true)" class="text-gray-300 hover:text-indigo-500 text-xs flex-shrink-0" title="重新生成今日簡報">↻</button>
            </div>
            <p class="text-sm text-indigo-700 mt-1.5">🎯 {{ briefing.focus }}</p>
            <div v-if="briefing.actions?.length" class="flex flex-wrap gap-1.5 mt-2.5">
              <NuxtLink v-for="(a, i) in briefing.actions" :key="i" :to="routeFor(a.route)" class="text-xs px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition">{{ a.label }} →</NuxtLink>
            </div>
            <p v-if="briefing.tip" class="text-xs text-gray-500 mt-2">💡 {{ briefing.tip }}</p>
          </template>
          <p v-else class="text-sm text-gray-400">先跟我聊幾句、做點練習，我就能依你的目標給每日建議。</p>
        </div>
      </div>

      <!-- 統計列 -->
      <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5">
          <div class="text-[11px] text-gray-400">等級 → 目標</div>
          <div class="text-lg font-bold text-gray-900">{{ stats.level }} <span class="text-xs text-gray-400 font-normal">→ {{ stats.goalLevel }}</span></div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5">
          <div class="text-[11px] text-gray-400">今日 / 目標</div>
          <div class="text-lg font-bold text-gray-900">{{ stats.todayMinutes }}<span class="text-xs text-gray-400 font-normal">/{{ stats.dailyGoal }}分</span></div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5">
          <div class="text-[11px] text-gray-400">連續天數</div>
          <div class="text-lg font-bold text-gray-900">🔥 {{ stats.streak }}</div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-3.5">
          <div class="text-[11px] text-gray-400">{{ stats.targetExam || '考試' }}倒數</div>
          <div class="text-lg font-bold text-gray-900">{{ stats.daysToExam !== null ? stats.daysToExam + '天' : '—' }}</div>
        </div>
      </div>

      <!-- 今日計畫（主入口）-->
      <NuxtLink :to="`/coach/${lang}/today`" class="block bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-5 text-white hover:shadow-lg transition">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-base font-bold">📅 今日計畫</div>
            <div class="text-xs text-white/80 mt-0.5">每日推薦單字 ‧ 5 篇閱讀 ‧ 5 段聽力 ‧ 口說題 ‧ 任務</div>
          </div>
          <span class="text-2xl">→</span>
        </div>
      </NuxtLink>

      <!-- 功能磚 -->
      <!-- 聊天區 -->
      <div>
        <div class="text-xs font-semibold text-gray-400 mb-1.5">跟教練聊</div>
        <div class="grid grid-cols-3 sm:grid-cols-5 gap-3">
          <NuxtLink :to="`/coach/${lang}/chat`" class="tile">⌨️<span>打字聊天</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/chat?voice=1`" class="tile">🎙️<span>口說聊天</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/chat?mode=qa`" class="tile">💡<span>問答・知識</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/chat?mode=scenario`" class="tile">🎭<span>情境角色</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/smalltalk`" class="tile">⏱️<span>主題限時聊</span></NuxtLink>
        </div>

        <!-- 今日推薦（每天輪替）：點了直接帶著話題/情境進聊天 -->
        <div v-if="coach" class="mt-3 space-y-2">
          <div class="text-[11px] font-semibold text-gray-400">今日推薦 · 每天換</div>
          <div v-if="todayChat.length" class="flex flex-wrap items-center gap-1.5">
            <span class="text-[11px] text-gray-400 w-14 flex-shrink-0">💬 聊話題</span>
            <NuxtLink v-for="(t, i) in todayChat" :key="'c' + i" :to="`/coach/${lang}/chat?topic=${encodeURIComponent(t)}`" class="chip">{{ t }}</NuxtLink>
          </div>
          <div v-if="todayQa.length" class="flex flex-wrap items-center gap-1.5">
            <span class="text-[11px] text-gray-400 w-14 flex-shrink-0">💡 問知識</span>
            <NuxtLink v-for="(t, i) in todayQa" :key="'q' + i" :to="`/coach/${lang}/chat?mode=qa&topic=${encodeURIComponent(t)}`" class="chip">{{ t }}</NuxtLink>
          </div>
          <div v-if="todayScenarios.length" class="flex flex-wrap items-center gap-1.5">
            <span class="text-[11px] text-gray-400 w-14 flex-shrink-0">🎭 演情境</span>
            <NuxtLink v-for="(t, i) in todayScenarios" :key="'s' + i" :to="`/coach/${lang}/chat?mode=scenario&scenario=${encodeURIComponent(t)}`" class="chip">{{ t }}</NuxtLink>
          </div>
        </div>
      </div>

      <!-- 學習區 -->
      <div>
        <div class="text-xs font-semibold text-gray-400 mb-1.5">練習與工具</div>
        <div class="grid grid-cols-3 sm:grid-cols-6 gap-3">
          <NuxtLink :to="`/coach/${lang}/courses`" class="tile">🎓<span>主題教程</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/grammar`" class="tile">📚<span>文法課</span></NuxtLink>
          <NuxtLink v-if="lang === 'en'" :to="`/coach/${lang}/grammar-map`" class="tile">🗺️<span>文法地圖</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/practice`" class="tile">🎯<span>技能/考試</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/review`" class="tile">🗂️<span>單字複習<small v-if="stats?.vocabDue">{{ stats.vocabDue }}</small></span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/immersion`" class="tile">📺<span>內容沉浸</span></NuxtLink>
          <NuxtLink :to="`/coach/${lang}/dashboard`" class="tile">📊<span>儀表板</span></NuxtLink>
        </div>
      </div>

      <div class="grid lg:grid-cols-2 gap-5">
        <!-- 日曆 + 教練日誌 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-baseline gap-2">
              <h2 class="text-sm font-semibold text-gray-800">學習日曆</h2>
              <span class="text-[11px] text-indigo-600 font-medium">今天 {{ todayLabel }}</span>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <button @click="shiftMonth(-1)" class="text-gray-400 hover:text-gray-700">‹</button>
              <span class="text-gray-600 tabular-nums">{{ month }}</span>
              <button @click="shiftMonth(1)" class="text-gray-400 hover:text-gray-700">›</button>
            </div>
          </div>
          <div class="grid grid-cols-7 gap-1 text-center">
            <div v-for="d in ['日','一','二','三','四','五','六']" :key="d" class="text-[10px] text-gray-300 py-1">{{ d }}</div>
            <div v-for="(cell, i) in calendarCells" :key="i" class="aspect-square">
              <button v-if="cell" @click="selectDay(cell)"
                class="w-full h-full rounded-lg text-[11px] flex items-center justify-center relative transition"
                :class="[dayClass(cell), cell.date === todayStr ? 'ring-2 ring-indigo-500 ring-offset-1 font-bold' : '']">
                {{ cell.day }}
                <span v-if="cell.date === todayStr" class="absolute -top-0.5 -right-0.5 text-[8px] px-1 rounded-full bg-indigo-600 text-white leading-tight">今</span>
                <span v-if="cell.hasJournal" class="absolute bottom-0.5 w-1 h-1 rounded-full bg-indigo-500" />
              </button>
            </div>
          </div>
          <!-- 選中日的教練日誌 -->
          <div v-if="selectedJournal" class="mt-3 pt-3 border-t border-gray-100">
            <div class="text-[11px] text-gray-400 mb-1">{{ selectedDate }} · {{ Math.round(selectedJournal.minutes || 0) }} 分</div>
            <p class="text-sm text-gray-700">{{ selectedJournal.summary }}</p>
            <p v-if="selectedJournal.direction" class="text-xs text-indigo-600 mt-1.5">➡️ {{ selectedJournal.direction }}</p>
          </div>
          <div v-else-if="selectedDate" class="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400">
            {{ selectedDate }}{{ selectedMinutes ? `：練習了 ${Math.round(selectedMinutes)} 分，但還沒有日誌` : '：這天沒有學習紀錄' }}
          </div>
        </div>

        <!-- 統整記憶庫 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-sm font-semibold text-gray-800">教練對你的了解</h2>
            <button @click="regenMemory" :disabled="memBusy" class="text-xs text-indigo-600 hover:underline disabled:opacity-50">{{ memBusy ? '更新中…' : '重新整理' }}</button>
          </div>
          <p v-if="memory?.memory" class="text-sm text-gray-700 leading-relaxed">{{ memory.memory }}</p>
          <p v-else class="text-xs text-gray-400">多聊幾次、做點練習後，這裡會出現教練對你的長期了解。</p>

          <div v-if="hl.weaknesses?.length" class="mt-3">
            <div class="text-[11px] font-semibold text-rose-400 uppercase mb-1">需加強</div>
            <div class="flex flex-wrap gap-1">
              <span v-for="(w, i) in hl.weaknesses" :key="i" class="text-[11px] px-2 py-0.5 rounded-full bg-rose-50 text-rose-600">{{ w }}</span>
            </div>
          </div>
          <div v-if="hl.strengths?.length" class="mt-2">
            <div class="text-[11px] font-semibold text-emerald-500 uppercase mb-1">強項</div>
            <div class="flex flex-wrap gap-1">
              <span v-for="(w, i) in hl.strengths" :key="i" class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">{{ w }}</span>
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

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();

const coach = ref<any>(null);
const briefing = ref<any>(null);
const stats = ref<any>(null);
const briefingLoading = ref(true);
const memory = ref<any>(null);
const memBusy = ref(false);

// 用瀏覽器本地時區（站長在台灣）算當月與今天，跟後端 Asia/Taipei 對齊
const todayStr = new Date().toLocaleDateString("en-CA");
const todayLabel = new Date().toLocaleDateString("zh-TW", { month: "long", day: "numeric", weekday: "short" });
const month = ref(todayStr.slice(0, 7));
const journals = ref<any[]>([]);
const days = ref<any[]>([]);
const selectedDate = ref<string | null>(null);

const hl = computed(() => (memory.value?.highlights ?? {}) as any);

// 今日推薦：以「今天是第幾天」當種子，每天輪替一組（同一天穩定、隔天就換）
const daySeed = (() => {
  const [y, m, d] = todayStr.split("-").map(Number);
  return Math.floor(Date.UTC(y, m - 1, d) / 86400000);
})();
function rotate(arr: any[] | undefined, count: number): string[] {
  if (!arr?.length) return [];
  const n = Math.min(count, arr.length);
  const start = daySeed % arr.length;
  return Array.from({ length: n }, (_, i) => arr[(start + i) % arr.length]);
}
const todayChat = computed(() => rotate(coach.value?.smalltalkTopics, 3));
const todayQa = computed(() => rotate(coach.value?.qaTopics, 3));
const todayScenarios = computed(() => rotate(coach.value?.scenarios, 3));

function routeFor(r: string) {
  if (r === "chat") return `/coach/${lang.value}/chat`;
  if (r === "smalltalk") return `/coach/${lang.value}/smalltalk`;
  if (["practice", "review", "immersion"].includes(r)) return `/coach/${lang.value}/${r}`;
  return `/coach/${lang.value}/chat`;
}

async function loadCoach() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === lang.value);
}
async function loadBriefing(force = false) {
  briefingLoading.value = true;
  try {
    const url = `/api/lang/briefing?language=${lang.value}${force ? "&force=1" : ""}`;
    const r = force ? await aiFetch<any>(url) : await authedFetch<any>(url);
    briefing.value = r.briefing;
    stats.value = r.stats;
  } finally {
    briefingLoading.value = false;
  }
}
async function loadMemory() {
  const { memory: m } = await authedFetch<any>(`/api/lang/memory?language=${lang.value}`);
  memory.value = m;
}
async function regenMemory() {
  memBusy.value = true;
  try {
    const { memory: m } = await aiFetch<any>("/api/lang/memory/regenerate", { method: "POST", body: { language: lang.value } });
    memory.value = m;
  } catch (e: any) {
    alert(e?.data?.message || "更新失敗");
  } finally {
    memBusy.value = false;
  }
}
async function loadCalendar() {
  const r = await authedFetch<any>(`/api/lang/journal?language=${lang.value}&month=${month.value}`);
  journals.value = r.journals;
  days.value = r.days;
}
function shiftMonth(delta: number) {
  const [y, m] = month.value.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  month.value = d.toISOString().slice(0, 7);
  selectedDate.value = null;
  loadCalendar();
}

const calendarCells = computed(() => {
  const [y, m] = month.value.split("-").map(Number);
  const first = new Date(y, m - 1, 1);
  const daysInMonth = new Date(y, m, 0).getDate();
  const lead = first.getDay();
  const cells: any[] = Array(lead).fill(null);
  for (let d = 1; d <= daysInMonth; d++) {
    const date = `${month.value}-${String(d).padStart(2, "0")}`;
    const act = days.value.find((x) => x.date === date);
    cells.push({ day: d, date, minutes: act?.minutes || 0, hasJournal: journals.value.some((j) => j.journal_date === date) });
  }
  return cells;
});
function dayClass(cell: any) {
  const sel = cell.date === selectedDate.value;
  if (sel) return "bg-indigo-600 text-white";
  if (cell.minutes >= 60) return "bg-emerald-400 text-white hover:bg-emerald-500";
  if (cell.minutes >= 20) return "bg-emerald-200 text-emerald-800 hover:bg-emerald-300";
  if (cell.minutes > 0) return "bg-emerald-50 text-emerald-600 hover:bg-emerald-100";
  return "text-gray-400 hover:bg-gray-50";
}
const selectedJournal = computed(() => journals.value.find((j) => j.journal_date === selectedDate.value) || null);
const selectedMinutes = computed(() => days.value.find((d) => d.date === selectedDate.value)?.minutes || 0);
function selectDay(cell: any) {
  selectedDate.value = cell.date;
}

onMounted(async () => {
  await Promise.all([loadCoach(), loadBriefing(), loadMemory(), loadCalendar()]);
  const today = todayStr; // 台北本地日期，跟後端 tzToday 對齊
  const todayAct = days.value.find((d) => d.date === today);
  const practicedToday = !!todayAct && todayAct.minutes >= 1;

  // 1) 今天練了但還沒日誌 → 背景產生一篇（每天一次）
  const hasJournalToday = journals.value.some((j) => j.journal_date === today);
  if (practicedToday && !hasJournalToday) {
    aiFetch("/api/lang/journal/generate", { method: "POST", body: { language: lang.value } })
      .then(() => loadCalendar())
      .catch(() => {});
  }

  // 2) 統整記憶每天最多自動刷新一次（今天有練、且記憶上次更新不是今天）
  const memDate = memory.value?.updated_at ? memory.value.updated_at.slice(0, 10) : null;
  if (practicedToday && memDate !== today) {
    aiFetch("/api/lang/memory/regenerate", { method: "POST", body: { language: lang.value } })
      .then((r: any) => { if (r?.memory) memory.value = r.memory; })
      .catch(() => {});
  }
});
</script>

<style scoped>
.tile {
  @apply flex flex-col items-center justify-center gap-1 bg-white border border-gray-200 rounded-2xl py-4 text-2xl hover:border-indigo-300 hover:shadow-sm transition;
}
.tile span { @apply text-xs font-medium text-gray-700; }
.chip { @apply text-[11px] px-2.5 py-1 rounded-full border border-gray-200 text-gray-600 bg-white hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 transition; }
.tile small { @apply ml-1 text-[10px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700; }
</style>
