<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${language}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">📦 FSI 離線練習</span>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-4">
      <!-- 說明 -->
      <div class="bg-emerald-50/60 rounded-2xl border border-emerald-100 p-4 text-sm text-gray-700 leading-relaxed">
        線上 API 不穩時，把「即時對話、寫作批改」這類重 AI 的練習搬到外面做：<b>① 下載練習包</b> → <b>② 上傳 NotebookLM / Gemini 照著練</b> → <b>③ 把 AI 的成果報告貼回來</b>，練習時間、單字、改錯自動入庫。練習包採 FSI（美國國務院外交學院）聽說教學法的 drill 循環，並已依華語母語者視角調整。簡單的單字複習、文法、字母測驗照舊在站上練即可。
      </div>

      <!-- ① 下載 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <h2 class="text-xs font-semibold text-gray-400 uppercase">① 下載練習包（Word）</h2>
        <div class="flex items-center gap-2 flex-wrap">
          <button @click="download('pack')" :disabled="downloading" class="px-5 py-2 rounded-xl bg-emerald-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-emerald-700 transition">{{ downloading === 'pack' ? '產生中…' : '📦 FSI 練習包 (.docx)' }}</button>
          <button @click="download('progress')" :disabled="downloading" class="px-4 py-2 rounded-xl bg-white border border-gray-300 text-gray-700 text-sm font-semibold disabled:opacity-40 hover:border-emerald-400 transition">{{ downloading === 'progress' ? '產生中…' : '📊 進度報告 (.docx)' }}</button>
        </div>
        <p class="text-[11px] text-gray-400 leading-relaxed">練習包內含：你目前的程度與弱項、到期複習單字、建議新字、今日主題、給 AI 的「FSI 教官指令」與成果報告模板——上傳後對 AI 說「請依這份練習包的教官指令帶我練習」即可。進度報告則是完整近況（給自己或另開的 AI 看）。</p>
      </div>

      <!-- ② 練習 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-2">
        <h2 class="text-xs font-semibold text-gray-400 uppercase">② 到 NotebookLM / Gemini 練習</h2>
        <p class="text-sm text-gray-600 leading-relaxed">把 .docx 上傳（NotebookLM 當來源、Gemini 直接附檔或貼內文），AI 會扮演 FSI 教官帶你跑：基礎對話背誦 → 替換／轉換／擴展／應答 drill → 文法短講 → 引導會話 → 寫作應用。練完請 AI 輸出「練習成果報告」。</p>
      </div>

      <!-- ③ 回傳 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <h2 class="text-xs font-semibold text-gray-400 uppercase">③ 貼回成果報告</h2>
        <textarea v-model="reportText" rows="9" placeholder="把 AI 輸出的【練習成果報告】整段貼上（含標題行；夾在整段對話裡也可以）…" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-emerald-400 font-mono" />
        <div class="flex items-center gap-2 flex-wrap">
          <button @click="submitReport" :disabled="importing || !reportText.trim()" class="px-5 py-2 rounded-xl bg-emerald-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-emerald-700 transition">{{ importing ? '入庫中…' : '✅ 送出入庫' }}</button>
          <label class="px-3 py-2 rounded-xl bg-white border border-gray-300 text-gray-600 text-xs font-semibold cursor-pointer hover:border-emerald-400 transition">
            📄 或選擇 .txt / .md 檔
            <input type="file" accept=".txt,.md,.text" class="hidden" @change="pickFile" />
          </label>
          <button @click="showTemplate = !showTemplate" class="ml-auto text-xs text-gray-400 hover:text-emerald-600 transition">{{ showTemplate ? '收起格式範本' : '看報告格式範本' }}</button>
        </div>
        <p v-if="err" class="text-xs text-rose-500 whitespace-pre-wrap">{{ err }}</p>

        <div v-if="showTemplate" class="bg-slate-50 rounded-xl border border-gray-200 p-3 space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-gray-400">AI 沒輸出報告時，把這段模板貼給它請它照填：</span>
            <button @click="copyTemplate" class="ml-auto text-xs text-emerald-600 hover:underline">{{ copied ? '已複製 ✓' : '複製模板' }}</button>
          </div>
          <pre class="text-[11px] text-gray-600 whitespace-pre-wrap leading-relaxed">{{ template }}</pre>
        </div>
      </div>

      <!-- 入庫結果 -->
      <div v-if="result" class="bg-white rounded-2xl border border-emerald-200 p-5 space-y-2">
        <h2 class="text-xs font-semibold text-emerald-600 uppercase">✅ 已入庫（{{ result.date }}）</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
          <div class="bg-emerald-50 rounded-xl p-2.5"><div class="text-lg font-bold text-gray-900">{{ Math.round(result.minutes) }}</div><div class="text-[11px] text-gray-400">練習分鐘</div></div>
          <div class="bg-emerald-50 rounded-xl p-2.5"><div class="text-lg font-bold text-gray-900">{{ result.wordsAdded }}</div><div class="text-[11px] text-gray-400">新單字</div></div>
          <div class="bg-emerald-50 rounded-xl p-2.5"><div class="text-lg font-bold text-gray-900">{{ result.reviewed }}</div><div class="text-[11px] text-gray-400">複習入 SRS</div></div>
          <div class="bg-emerald-50 rounded-xl p-2.5"><div class="text-lg font-bold text-gray-900">{{ result.corrections }}</div><div class="text-[11px] text-gray-400">改錯紀錄</div></div>
        </div>
        <div v-if="skillsLine" class="text-xs text-gray-500">技能時間：{{ skillsLine }}</div>
        <div v-if="result.overall !== null" class="text-xs text-gray-500">整體評分：<b :class="result.overall >= 80 ? 'text-emerald-600' : result.overall >= 60 ? 'text-amber-600' : 'text-rose-600'">{{ result.overall }}</b></div>
        <div v-if="result.reviewMisses?.length" class="text-[11px] text-amber-600">⚠️ 這些複習字在你的單字庫找不到、沒套排程：{{ result.reviewMisses.join('、') }}</div>
        <div class="text-[11px] text-gray-400 pt-1">
          <NuxtLink :to="`/coach/${language}/dashboard`" class="text-emerald-600 hover:underline">看儀表板</NuxtLink> ·
          <NuxtLink :to="`/coach/${language}/review`" class="text-emerald-600 hover:underline">複習單字</NuxtLink> ·
          <NuxtLink :to="`/coach/${language}`" class="text-emerald-600 hover:underline">回首頁</NuxtLink>
        </div>
      </div>

      <p class="text-center text-[11px] text-gray-400">單字、文法、字母這類輕量練習仍建議在 <NuxtLink :to="`/coach/${language}/review`" class="text-emerald-600 hover:underline">站上直接練</NuxtLink>（零 AI、即時反饋）</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { reportTemplate } from "~/utils/offlineReport";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);

const downloading = ref<string | null>(null);
const reportText = ref("");
const importing = ref(false);
const err = ref("");
const result = ref<any>(null);
const showTemplate = ref(false);
const copied = ref(false);
const langLabel = ref("");

const template = computed(() => reportTemplate(langLabel.value || "目標語言"));
const SKILL_ZH: Record<string, string> = { listening: "聽力", speaking: "口說", reading: "閱讀", writing: "寫作" };
const skillsLine = computed(() =>
  result.value ? Object.entries(result.value.skills || {}).map(([k, v]) => `${SKILL_ZH[k] ?? k} ${Math.round(Number(v))} 分`).join("、") : ""
);

async function download(kind: "pack" | "progress") {
  if (downloading.value) return;
  downloading.value = kind;
  err.value = "";
  try {
    const blob = await authedFetch<Blob>(`/api/lang/offline/export?language=${language.value}&kind=${kind}`, { responseType: "blob" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${kind === "pack" ? "FSI練習包" : "學習進度報告"}-${language.value}.docx`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e: any) {
    err.value = e?.data?.message || "下載失敗，請重試";
  } finally {
    downloading.value = null;
  }
}

function pickFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { reportText.value = String(reader.result || ""); };
  reader.readAsText(file);
  (e.target as HTMLInputElement).value = "";
}

async function submitReport() {
  if (!reportText.value.trim() || importing.value) return;
  importing.value = true;
  err.value = "";
  result.value = null;
  try {
    result.value = await authedFetch<any>("/api/lang/offline/import", {
      method: "POST",
      body: { language: language.value, text: reportText.value },
    });
    reportText.value = "";
  } catch (e: any) {
    err.value = e?.data?.message || "入庫失敗，請重試";
  } finally {
    importing.value = false;
  }
}

async function copyTemplate() {
  try {
    await navigator.clipboard.writeText(template.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  } catch { /* 剪貼簿不可用就算了 */ }
}

onMounted(async () => {
  try {
    const { coaches } = await authedFetch<any>("/api/lang/coaches");
    langLabel.value = (coaches ?? []).find((c: any) => c.language === language.value)?.langLabel || "";
  } catch { /* 標籤抓不到不影響功能 */ }
});
</script>
