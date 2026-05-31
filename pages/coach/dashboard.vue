<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/coach" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">學習儀表板</span>
      <select v-model="language" @change="load" class="ml-auto text-xs border border-gray-200 rounded-lg px-2 py-1">
        <option value="en">英文</option>
        <option value="ja">日文</option>
      </select>
    </nav>

    <!-- Onboarding -->
    <div v-if="showOnboard" class="flex-1 flex items-center justify-center p-6">
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-7 max-w-lg w-full">
        <h1 class="text-xl font-bold text-gray-900">設定你的學習目標</h1>
        <p class="text-sm text-gray-500 mt-1">教練會依此為你客製內容（考試題型、學術詞庫、討論主題）。</p>

        <div class="mt-5 space-y-4">
          <div>
            <label class="text-xs font-semibold text-gray-600">目前程度 → 目標程度</label>
            <div class="flex items-center gap-2 mt-1">
              <select v-model="form.current_level" class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm">
                <option v-for="l in CEFR" :key="l" :value="l">{{ l }}</option>
              </select>
              <span class="text-gray-400">→</span>
              <select v-model="form.goal_level" class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm">
                <option v-for="l in CEFR" :key="l" :value="l">{{ l }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-gray-600">目標考試</label>
              <select v-model="form.target_exam" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1">
                <option :value="null">無</option>
                <option value="TOEFL">TOEFL</option>
                <option value="IELTS">IELTS</option>
                <option value="GRE">GRE</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-semibold text-gray-600">預計考試日</label>
              <input v-model="form.exam_date" type="date" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1" />
            </div>
          </div>

          <div>
            <label class="text-xs font-semibold text-gray-600">每日目標（分鐘）</label>
            <input v-model.number="form.daily_goal_minutes" type="number" min="10" step="10" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>

          <div>
            <label class="text-xs font-semibold text-gray-600">興趣領域（人文為主，可多選）</label>
            <div class="flex flex-wrap gap-1.5 mt-1.5">
              <button
                v-for="t in INTEREST_PRESETS"
                :key="t"
                @click="toggleInterest(t)"
                class="text-xs px-2.5 py-1 rounded-full border transition"
                :class="form.interests.includes(t) ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'"
              >{{ t }}</button>
            </div>
          </div>
        </div>

        <button @click="saveOnboard" :disabled="saving" class="mt-6 w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-50 hover:bg-indigo-700 transition">
          {{ saving ? '儲存中…' : '開始學習' }}
        </button>
      </div>
    </div>

    <!-- Dashboard -->
    <div v-else-if="dash" class="flex-1 p-5 max-w-5xl mx-auto w-full space-y-5">
      <!-- 頂部統計卡 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <div class="text-xs text-gray-400">連續天數</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">🔥 {{ dash.progress.streak_days || 0 }}</div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <div class="text-xs text-gray-400">今日 / 目標（分鐘）</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">{{ dash.todayMinutes }} <span class="text-sm text-gray-400 font-normal">/ {{ dash.dailyGoal }}</span></div>
          <div class="h-1.5 bg-gray-100 rounded-full mt-2 overflow-hidden">
            <div class="h-full bg-emerald-500 rounded-full" :style="{ width: Math.min(100, (dash.todayMinutes / dash.dailyGoal) * 100) + '%' }" />
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <div class="text-xs text-gray-400">目前等級 → 目標</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">{{ dash.progress.level || 'B2' }} <span class="text-sm text-gray-400 font-normal">→ {{ dash.profile?.goal_level || 'C2' }}</span></div>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <div class="text-xs text-gray-400">{{ dash.profile?.target_exam || '考試' }}倒數</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">
            <template v-if="dash.daysToExam !== null">{{ dash.daysToExam }} <span class="text-sm text-gray-400 font-normal">天</span></template>
            <span v-else class="text-sm text-gray-300 font-normal">未設定</span>
          </div>
        </div>
      </div>

      <!-- 四技能本週時間 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-800">四技能練習時間（本週）</h2>
          <span class="text-xs text-gray-400">單位：分鐘</span>
        </div>
        <div class="space-y-2.5">
          <div v-for="s in SKILL_META" :key="s.key" class="flex items-center gap-3">
            <span class="text-xs w-12 text-gray-500">{{ s.label }}</span>
            <div class="flex-1 h-5 bg-gray-50 rounded-lg overflow-hidden">
              <div class="h-full rounded-lg flex items-center justify-end px-2" :class="s.color" :style="{ width: skillBarWidth(s.key) }">
                <span class="text-[10px] text-white font-medium" v-if="dash.bySkill[s.key].week > 0">{{ Math.round(dash.bySkill[s.key].week) }}</span>
              </div>
            </div>
            <span class="text-[10px] text-gray-400 w-16 text-right">今日 {{ Math.round(dash.bySkill[s.key].today) }}</span>
          </div>
        </div>
      </div>

      <div class="grid lg:grid-cols-2 gap-5">
        <!-- 近 30 天每日時間 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">近 30 天每日學習時間</h2>
          <svg :viewBox="`0 0 ${dash.dailySeries.length * 11} 80`" class="w-full h-24">
            <rect
              v-for="(d, i) in dash.dailySeries"
              :key="i"
              :x="i * 11"
              :y="80 - barH(d.minutes)"
              width="8"
              :height="barH(d.minutes)"
              rx="2"
              :class="d.date === todayStr ? 'fill-indigo-500' : 'fill-indigo-200'"
            >
              <title>{{ d.date }}：{{ d.minutes }} 分</title>
            </rect>
          </svg>
          <div class="flex justify-between text-[10px] text-gray-300 mt-1">
            <span>30 天前</span><span>今天</span>
          </div>
        </div>

        <!-- CEFR 等級曲線 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-800">CEFR 等級曲線</h2>
            <button @click="runAssess" :disabled="assessing" class="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition disabled:opacity-50">
              {{ assessing ? '評估中…' : '測一下程度' }}
            </button>
          </div>
          <div v-if="dash.levelHistory.length" class="relative">
            <svg viewBox="0 0 300 110" class="w-full h-28">
              <line v-for="(lbl, i) in ['C2','C1','B2','B1']" :key="lbl" :y1="i*30+10" :y2="i*30+10" x1="20" x2="300" class="stroke-gray-100" />
              <text v-for="(lbl, i) in ['C2','C1','B2','B1']" :key="'t'+lbl" x="0" :y="i*30+13" class="fill-gray-300 text-[8px]">{{ lbl }}</text>
              <polyline :points="cefrPoints" fill="none" class="stroke-indigo-500" stroke-width="2" />
              <circle v-for="(p, i) in cefrCoords" :key="i" :cx="p.x" :cy="p.y" r="3" class="fill-indigo-500" />
            </svg>
            <p v-if="lastAssessNote" class="text-[11px] text-gray-500 mt-1">💡 {{ lastAssessNote }}</p>
          </div>
          <p v-else class="text-xs text-gray-300 py-8 text-center">尚無評估紀錄，點「測一下程度」讓教練評你的 CEFR 等級</p>
        </div>
      </div>

      <!-- 單字統計 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-800">單字庫</h2>
          <div class="flex items-center gap-4 text-xs">
            <span class="text-gray-500">總計 <b class="text-gray-800">{{ dash.vocab.total }}</b></span>
            <NuxtLink to="/coach/review" class="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 transition">今日待複習 <b>{{ dash.vocab.dueToday }}</b> →</NuxtLink>
          </div>
        </div>
        <div class="flex items-end gap-1.5 h-16">
          <div v-for="n in 6" :key="n" class="flex-1 flex flex-col items-center justify-end">
            <div class="w-full rounded-t bg-amber-400" :style="{ height: masteryBarH(n - 1) }" :class="n - 1 === 5 ? 'bg-emerald-500' : 'bg-amber-400'" />
            <span class="text-[9px] text-gray-400 mt-1">L{{ n - 1 }}</span>
          </div>
        </div>
        <p class="text-[11px] text-gray-400 mt-2">L0 新詞 → L5 精熟（間隔複習依此排程）</p>
      </div>

      <!-- API 用量 / 成本 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-800">Gemini 用量與估計成本</h2>
          <button @click="toggleTier" class="text-xs px-3 py-1 rounded-full border transition"
            :class="usePaid ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'bg-gray-50 border-gray-200 text-gray-500'">
            目前：{{ usePaid ? '付費 key' : '免費 key' }}（點此切換）
          </button>
        </div>
        <div v-if="usage" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="bg-gray-50 rounded-xl p-3">
            <div class="text-[11px] text-gray-400">今日請求數</div>
            <div class="text-lg font-bold text-gray-800">{{ usage.today.all.requests }}</div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3">
            <div class="text-[11px] text-gray-400">今日 token</div>
            <div class="text-lg font-bold text-gray-800">{{ fmtTok(usage.today.all.totalTokens) }}</div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3">
            <div class="text-[11px] text-gray-400">今日估計成本</div>
            <div class="text-lg font-bold text-gray-800">NT${{ usage.today.all.costTwd.toFixed(2) }}</div>
            <div class="text-[10px] text-gray-400">免費部分計 0</div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3">
            <div class="text-[11px] text-gray-400">近 30 天付費成本</div>
            <div class="text-lg font-bold text-gray-800">NT${{ usage.last30Paid.costTwd.toFixed(2) }}</div>
          </div>
        </div>
        <p class="text-[11px] text-gray-400 mt-2">
          成本為「token × 公開單價」的估計值（免費層計 0）；實際帳單以 Google Cloud Billing 為準。免費額度用完時會跳出提示，確認後改用付費 key。
        </p>
      </div>

      <div class="flex gap-3">
        <NuxtLink :to="`/coach/${language}`" class="flex-1 text-center py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">繼續對話練習 →</NuxtLink>
        <button @click="showOnboard = true; loadFormFromProfile()" class="px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">調整目標</button>
      </div>
    </div>

    <div v-else class="flex-1 flex items-center justify-center text-gray-400 text-sm">載入中…</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch, usePaid, ensureLoaded, setUsePaid } = useCoachAi();

const CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"];
const INTEREST_PRESETS = ["哲學", "歷史", "神學", "文學", "語言學", "社會學", "政治學", "藝術史", "宗教研究", "古典學", "人類學", "心理學"];
const SKILL_META = [
  { key: "listening", label: "聽", color: "bg-sky-400" },
  { key: "speaking", label: "說", color: "bg-rose-400" },
  { key: "reading", label: "讀", color: "bg-amber-400" },
  { key: "writing", label: "寫", color: "bg-emerald-400" },
];
const CEFR_NUM: Record<string, number> = { A1: 20, A2: 35, B1: 50, B2: 65, C1: 80, C2: 95 };

const language = ref("en");
const dash = ref<any>(null);
const showOnboard = ref(false);
const saving = ref(false);
const assessing = ref(false);
const todayStr = new Date().toISOString().slice(0, 10);
const lastAssessNote = ref("");

const form = ref({
  current_level: "B2",
  goal_level: "C2",
  target_exam: "TOEFL" as string | null,
  exam_date: "",
  daily_goal_minutes: 90,
  interests: [] as string[],
});

function toggleInterest(t: string) {
  const i = form.value.interests.indexOf(t);
  if (i >= 0) form.value.interests.splice(i, 1);
  else form.value.interests.push(t);
}

function loadFormFromProfile() {
  const p = dash.value?.profile;
  if (!p) return;
  form.value.goal_level = p.goal_level || "C2";
  form.value.current_level = dash.value?.progress?.level || "B2";
  form.value.target_exam = p.target_exam ?? "TOEFL";
  form.value.exam_date = p.exam_date || "";
  form.value.daily_goal_minutes = p.daily_goal_minutes || 90;
  form.value.interests = Array.isArray(p.interests) ? [...p.interests] : [];
}

const usage = ref<any>(null);

async function load() {
  dash.value = null;
  await ensureLoaded();
  const [d, u] = await Promise.all([
    authedFetch<any>(`/api/lang/dashboard?language=${language.value}`),
    authedFetch<any>("/api/lang/usage").catch(() => null),
  ]);
  dash.value = d;
  usage.value = u;
  lastAssessNote.value = d.levelHistory?.length ? d.levelHistory[d.levelHistory.length - 1].note || "" : "";
  if (!d.profile?.onboarded) {
    loadFormFromProfile();
    showOnboard.value = true;
  }
}

async function toggleTier() {
  await setUsePaid(!usePaid.value);
}

function fmtTok(n: number) {
  if (!n) return "0";
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}

async function saveOnboard() {
  saving.value = true;
  try {
    await authedFetch("/api/lang/profile", {
      method: "PUT",
      body: {
        goal_level: form.value.goal_level,
        target_exam: form.value.target_exam,
        exam_date: form.value.exam_date || null,
        daily_goal_minutes: form.value.daily_goal_minutes,
        interests: form.value.interests,
        primary_language: language.value,
        onboarded: true,
      },
    });
    // 把「目前程度」記成一筆等級歷史起點
    showOnboard.value = false;
    await load();
  } finally {
    saving.value = false;
  }
}

async function runAssess() {
  assessing.value = true;
  try {
    const { assessment } = await aiFetch<any>("/api/lang/assess", {
      method: "POST",
      body: { language: language.value },
    });
    lastAssessNote.value = assessment?.note || "";
    await load();
  } catch (e: any) {
    alert(e?.data?.message || "評估失敗");
  } finally {
    assessing.value = false;
  }
}

// 圖表計算
const maxDaily = computed(() => Math.max(30, ...(dash.value?.dailySeries?.map((d: any) => d.minutes) || [0])));
function barH(min: number) {
  return Math.max(2, (min / maxDaily.value) * 70);
}
function skillBarWidth(key: string) {
  const weeks = SKILL_META.map((s) => dash.value.bySkill[s.key].week);
  const max = Math.max(10, ...weeks);
  return Math.max(2, (dash.value.bySkill[key].week / max) * 100) + "%";
}
function masteryBarH(level: number) {
  const dist = dash.value?.vocab?.masteryDist || [];
  const max = Math.max(1, ...dist);
  return Math.max(3, (dist[level] / max) * 56) + "px";
}

const cefrCoords = computed(() => {
  const h = dash.value?.levelHistory || [];
  if (!h.length) return [];
  const n = h.length;
  return h.map((row: any, i: number) => {
    const score = row.cefr_score ?? CEFR_NUM[row.level] ?? 65;
    // y: B1(50)→100, C2(95)→10 線性映射
    const x = 20 + (i / Math.max(1, n - 1)) * 270;
    const y = 110 - ((score - 40) / 60) * 100;
    return { x, y: Math.max(8, Math.min(105, y)) };
  });
});
const cefrPoints = computed(() => cefrCoords.value.map((p: any) => `${p.x},${p.y}`).join(" "));

onMounted(load);
</script>
