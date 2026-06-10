<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">單字複習</span>
      <div class="ml-auto flex items-center gap-1">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
        <button @click="endless = !endless" class="text-xs px-2.5 py-1 rounded-lg transition mr-1" :class="endless ? 'bg-violet-600 text-white' : 'bg-gray-50 text-gray-500'" title="刷完到期單字後自動生成新學術單字，永不停">♾️ 無限</button>
        <button @click="mode = 'flip'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'flip' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">翻卡</button>
        <button @click="mode = 'quiz'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'quiz' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">選擇題</button>
        <button @click="mode = 'cloze'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'cloze' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">克漏字</button>
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <!-- 複習卡 -->
      <div v-if="current" class="bg-white rounded-3xl border border-gray-100 shadow-sm p-8 text-center">
        <div class="text-xs text-gray-400 mb-4">剩餘 {{ queue.length }} 張 · 今日已複習 {{ reviewed }}</div>
        <div v-if="mode !== 'cloze'" class="text-3xl font-bold text-gray-900">{{ current.word }}</div>
        <div v-if="mode !== 'cloze' && current.reading" class="text-sm text-gray-400 mt-1">{{ current.reading }}</div>
        <button v-if="mode !== 'cloze' && speech.ttsSupported.value" @click="speak" class="mt-2 text-gray-300 hover:text-indigo-500 transition">🔊 發音</button>

        <!-- 克漏字模式：看中文＋挖空例句，打出單字 -->
        <template v-if="mode === 'cloze'">
          <div class="text-base text-gray-700 mt-1">{{ current.meaning }}</div>
          <div v-if="clozeSentence" class="text-sm text-gray-500 mt-3 italic">{{ clozeSentence }}</div>
          <input v-model="clozeInput" :disabled="clozeChecked" @keydown.enter="checkCloze" placeholder="打出這個單字…" class="mt-4 w-full text-center px-4 py-3 rounded-xl border text-lg focus:outline-none" :class="clozeChecked ? (clozeCorrect ? 'border-emerald-300 bg-emerald-50' : 'border-rose-300 bg-rose-50') : 'border-gray-200 focus:border-indigo-400'" />
          <button v-if="!clozeChecked" @click="checkCloze" :disabled="!clozeInput.trim()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">檢查</button>
          <div v-else class="mt-4">
            <p v-if="clozeCorrect" class="text-sm text-emerald-600 font-medium">✓ 答對了！</p>
            <p v-else class="text-sm text-rose-600 font-medium">✗ 正解：{{ current.word }}</p>
            <div v-if="current.example" class="text-xs text-gray-400 mt-1 italic">{{ current.example }}</div>
            <button @click="next()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">下一張 →</button>
          </div>
        </template>

        <!-- 選擇題模式：選意思 -->
        <template v-else-if="mode === 'quiz'">
          <div class="mt-5 space-y-2">
            <button v-for="(opt, oi) in current.options" :key="oi" @click="answer(opt)" :disabled="picked !== null"
              class="w-full text-left px-4 py-3 rounded-xl border text-sm transition"
              :class="optionClass(opt)">
              {{ opt }}
            </button>
          </div>
          <div v-if="picked !== null" class="mt-4">
            <p v-if="picked === current.meaning" class="text-sm text-emerald-600 font-medium">✓ 答對了！</p>
            <p v-else class="text-sm text-rose-600 font-medium">✗ 答錯了，已排進複習。正解：{{ current.meaning }}</p>
            <div v-if="current.example" class="text-xs text-gray-400 mt-1 italic">{{ current.example }}</div>
            <button @click="next()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">下一張 →</button>
          </div>
        </template>

        <!-- 翻卡模式 -->
        <template v-else>
          <Transition name="fade">
            <div v-if="revealed" class="mt-5 pt-5 border-t border-gray-100">
              <div class="text-lg text-gray-800">{{ current.meaning }}</div>
              <div v-if="current.example" class="text-sm text-gray-400 mt-2 italic">{{ current.example }}</div>
            </div>
          </Transition>
          <div class="mt-7">
            <button v-if="!revealed" @click="revealed = true" class="px-8 py-3 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">顯示答案</button>
            <div v-else class="grid grid-cols-4 gap-2">
              <button @click="grade(2)" class="py-3 rounded-xl bg-rose-50 text-rose-700 text-sm font-medium hover:bg-rose-100 transition">再來一次<span class="block text-[10px] opacity-60">1天</span></button>
              <button @click="grade(3)" class="py-3 rounded-xl bg-amber-50 text-amber-700 text-sm font-medium hover:bg-amber-100 transition">困難</button>
              <button @click="grade(4)" class="py-3 rounded-xl bg-sky-50 text-sky-700 text-sm font-medium hover:bg-sky-100 transition">良好</button>
              <button @click="grade(5)" class="py-3 rounded-xl bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition">簡單</button>
            </div>
          </div>
        </template>
      </div>

      <!-- 無限模式：正在生成新題 -->
      <div v-else-if="topping" class="bg-white rounded-3xl border border-gray-100 p-10 text-center">
        <div class="text-4xl mb-3 animate-pulse">♾️</div>
        <div class="font-semibold text-gray-800">正在生成新的學術單字…</div>
        <p class="text-sm text-gray-400 mt-1">教練在幫你出新題，馬上回來。</p>
      </div>

      <!-- 沒有到期單字（非無限模式，或生成失敗）-->
      <div v-else-if="!loading" class="bg-white rounded-3xl border border-gray-100 p-10 text-center">
        <div class="text-4xl mb-3">🎉</div>
        <div class="font-semibold text-gray-800">今日複習完成！</div>
        <p class="text-sm text-gray-400 mt-1">沒有到期的單字了。{{ endless ? "（無限模式找不到新題，可手動指定主題生成）" : "可以生成新的學術單字組繼續學，或開啟右上「♾️ 無限」自動出題。" }}</p>
      </div>

      <!-- 生成新單字組 -->
      <div class="mt-6 bg-white rounded-2xl border border-gray-100 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-1">生成學術單字組</h2>
        <p class="text-xs text-gray-400 mb-3">依你的程度與人文興趣生成；自動加入複習排程。</p>
        <div class="flex flex-wrap gap-1.5 mb-3">
          <button v-for="p in PRESETS" :key="p" @click="theme = p" class="text-xs px-2.5 py-1 rounded-full border transition" :class="theme === p ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ p }}</button>
        </div>
        <div class="flex gap-2">
          <input v-model="theme" placeholder="主題，如：GRE 哲學高頻字 / AWL Sublist 1 / 歷史學術用語" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
          <button @click="generate" :disabled="generating || !theme.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40 hover:bg-indigo-700 transition whitespace-nowrap">{{ generating ? '生成中…' : '生成' }}</button>
        </div>
        <p v-if="genMsg" class="text-xs text-emerald-600 mt-2">{{ genMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useCoachAi } from "~/composables/useCoachAi";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch } = useCoachAi();
const tracker = useActivityTracker();

// 主題池依語言不同：英文走學術/考試；日文走 N5→N4 初學（簡單、文化/宗教淺白）
const THEME_POOLS: Record<string, { presets: string[]; auto: string[] }> = {
  en: {
    presets: ["AWL Sublist 1", "GRE 高頻字", "哲學學術用語", "歷史學術用語", "神學術語", "文學批評術語", "學術寫作連接詞"],
    // 無限模式用：全為「手工策展」主題（後端直接插策展單字、不走 AI）→ 永遠秒出題、不卡頓
    auto: [
      "AWL Sublist 1", "GRE 高頻字", "哲學學術用語", "歷史學術用語",
      "神學術語", "文學批評術語", "學術寫作連接詞",
    ],
  },
  ja: {
    presets: ["N5 基礎單字", "N4 常用單字", "日常生活單字", "神社・お寺の基礎語", "祭りと行事", "食べ物と飲み物"],
    auto: [
      "N5 基礎單字", "N4 常用單字", "日常生活の動詞", "形容詞（い・な形）", "家族と人",
      "食べ物と飲み物", "時間と日付", "場所と方向", "体と健康", "天気と季節",
      "あいさつと丁寧表現", "神社・お寺の基礎語", "日本の祭りと行事", "数と助数詞", "学校と仕事",
    ],
  },
  // 德文（A1 初學）：A1 高頻字＋日常生活，隨程度再帶宗教／神話題材
  de: {
    presets: ["A1 高頻字", "日常生活名詞", "規則動詞現在式", "der/die/das 常見名詞", "數字與時間", "家庭與人"],
    auto: [
      "A1 高頻字（前 100）", "常用規則動詞", "sein／haben 與情態動詞", "家庭與人",
      "食物與飲料", "數字・時間・日期", "城市與方向", "身體與健康", "天氣與季節",
      "問候與禮貌用語", "der/die/das 常見名詞（含複數）", "形容詞與顏色",
      "教堂與節慶基礎字", "宗教改革與神學基礎詞", "旅遊與交通",
    ],
  },
  // 法文（A1 初學）：A1 高頻字＋日常生活，隨程度再帶宗教／神話題材
  fr: {
    presets: ["A1 高頻字", "日常生活名詞", "-er 動詞現在式", "le/la/un/une 常見名詞", "數字與時間", "家庭與人"],
    auto: [
      "A1 高頻字（前 100）", "常用 -er 動詞", "être／avoir 與基本動詞", "家庭與人",
      "食物與飲料", "數字・時間・日期", "城市與方向", "身體與健康", "天氣與季節",
      "問候與禮貌用語", "陰陽性常見名詞（含冠詞）", "形容詞與顏色",
      "大教堂與節慶基礎字", "天主教與神學基礎詞", "旅遊與交通",
    ],
  },
  // 通用希臘文（Koine，入門）：題材＝新約／LXX／教父／信經／希臘化猶太／哲學家／拜占庭
  grc: {
    presets: ["新約高頻字", "約翰福音核心字", "希臘文冠詞與代名詞", "信經關鍵詞", "七十士譯本基礎字", "教父文獻常用字"],
    auto: [
      "新約高頻字（前 100）", "新約高頻動詞", "希臘文冠詞・代名詞・連接詞", "介系詞與小品詞",
      "約翰福音核心字彙", "馬可福音核心字彙", "七十士譯本（LXX）創世記基礎字", "詩篇（LXX）常用字",
      "使徒教父常用字", "尼西亞信經關鍵詞", "大公會議神學術語（οὐσία／ὑπόστασις…）",
      "斐羅與希臘化猶太文獻常用字", "希臘化哲學常用字（斯多噶／柏拉圖）", "拜占庭教會與官方文獻常用字",
      "基督教禮儀與敬拜詞彙",
    ],
  },
  // 教會拉丁文（Ecclesiastical，入門）：武加大／拉丁教父 → 經院神哲學 → 中世紀各學科
  la: {
    presets: ["武加大高頻字", "福音書常用字", "拉丁文代名詞與介系詞", "信經與禮儀關鍵詞", "拉丁教父常用字", "經院神學術語"],
    auto: [
      "武加大（Vulgata）高頻字", "武加大高頻動詞", "拉丁文代名詞・連接詞・介系詞",
      "福音書核心字彙", "詩篇（武加大）常用字", "使徒信經與尼西亞信經關鍵詞",
      "拉丁教父常用字（奧古斯丁／耶柔米）", "禮儀與彌撒常用字", "大公會議與教令術語",
      "經院神學術語（ens／esse／essentia／substantia…）", "阿奎那《神學大全》常見詞",
      "經院哲學邏輯術語（quaestio／ratio／accidens…）", "教會法（canon law）常用字",
      "中世紀大學與七藝常用字", "聖徒傳與編年史常用字",
    ],
  },
  // 聖經希伯來文（Biblical，入門）：以舊約為起點，擴及昆蘭／拉比／中世紀註釋
  hbo: {
    presets: ["創世記常用字", "舊約高頻字", "希伯來文代名詞與介係詞", "詩篇常用字", "動詞 binyanim 入門", "聖經人名與地名"],
    auto: [
      "舊約（Tanakh）高頻字（前 100）", "創世記核心字彙", "出埃及記核心字彙", "詩篇常用字",
      "希伯來文代名詞・介係詞・冠詞", "連接詞 vav 與敘述式", "常用三母音字根",
      "動詞詞幹 binyanim（Qal／Niphal／Piel…）入門", "先知書常用字", "智慧文學（箴言／約伯）常用字",
      "聖殿與禮儀詞彙", "死海古卷（昆蘭）常用字", "米示拿／拉比希伯來文入門字",
      "中世紀希伯來文聖經註釋常用字", "聖經人名與地名",
    ],
  },
};
const pool = computed(() => THEME_POOLS[language.value] || THEME_POOLS.en);
const PRESETS = computed(() => pool.value.presets);
const TTS_LANG: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const route = useRoute();
const language = computed(() => route.params.lang as string);
const queue = ref<any[]>([]);
const revealed = ref(false);
const reviewed = ref(0);
const loading = ref(true);
const theme = ref("");
const generating = ref(false);
const genMsg = ref("");
const speech = useSpeech();
const mode = ref<"quiz" | "flip" | "cloze">("quiz"); // 預設選擇題
const picked = ref<string | null>(null);

// ── 克漏字模式 ──
const clozeInput = ref("");
const clozeChecked = ref(false);
const clozeCorrect = ref(false);
const normWord = (s: string) => (s || "").toLowerCase().trim().replace(/[^\p{L}\p{N}'’\- ]/gu, "");
// 例句中把目標字挖空（不分大小寫、整詞）
const clozeSentence = computed(() => {
  const c = current.value;
  if (!c?.example || !c?.word) return "";
  const re = new RegExp(`\\b${c.word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "gi");
  return c.example.replace(re, "_____");
});
async function checkCloze() {
  if (clozeChecked.value || !clozeInput.value.trim()) return;
  const c = current.value;
  clozeChecked.value = true;
  clozeCorrect.value = normWord(clozeInput.value) === normWord(c.word);
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: c.id, quality: clozeCorrect.value ? 4 : 2 } });
  } catch { /* ignore */ }
}
function resetCloze() {
  clozeInput.value = "";
  clozeChecked.value = false;
  clozeCorrect.value = false;
}

// ── 無限刷題模式 ──
const endless = ref(true);          // 預設開：刷完自動生成新單字
const topping = ref(false);         // 正在背景補題
const seen = new Set<string>();     // 本次 session 已出現過的卡片 id（避免馬上重複）
let themeIdx = 0;
const LOW_WATER = 4;                 // 佇列剩這麼少就先補題（預抓，藏延遲）

const current = computed(() => queue.value[0] || null);

function optionClass(opt: string) {
  if (picked.value === null) return "border-gray-200 text-gray-700 hover:border-indigo-300";
  if (opt === current.value.meaning) return "border-emerald-300 bg-emerald-50 text-emerald-700";
  if (opt === picked.value) return "border-rose-300 bg-rose-50 text-rose-600";
  return "border-gray-100 text-gray-400";
}

// 選擇題作答：對→good(4)、錯→again(2，排進複習)
async function answer(opt: string) {
  if (picked.value !== null) return;
  picked.value = opt;
  const card = current.value;
  const q = opt === card.meaning ? 4 : 2;
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: card.id, quality: q } });
  } catch { /* ignore */ }
}

function next() {
  queue.value.shift();
  picked.value = null;
  resetCloze();
  reviewed.value++;
  maybeTopUp();
}

// 抓佇列；append=true 只把「沒出現過的」新卡接到尾端（無限模式用），保留進度
async function loadQueue(append = false) {
  const { due } = await authedFetch<{ due: any[] }>(`/api/lang/vocab/review?language=${language.value}&limit=40`);
  const fresh = (due || []).filter((c) => !seen.has(c.id));
  for (const c of fresh) seen.add(c.id);
  if (append) queue.value.push(...fresh);
  else queue.value = fresh;
  return fresh.length;
}

async function reload() {
  loading.value = true;
  revealed.value = false;
  picked.value = null;
  reviewed.value = 0;
  seen.clear();
  await loadQueue(false);
  loading.value = false;
}

// 無限模式核心：佇列見底就自動生成一批新學術單字（走 NVIDIA，免費）接上去
async function replenish() {
  if (!endless.value || topping.value) return;
  topping.value = true;
  try {
    const themes = pool.value.auto;
    const theme = themes[themeIdx % themes.length];
    themeIdx++;
    await aiFetch("/api/lang/vocab/generate", {
      method: "POST",
      body: { language: language.value, theme, count: 15 },
    });
    await loadQueue(true); // 把新生成的（未出現過的）接到佇列尾
  } catch {
    /* 生成失敗就算了，next 次再試 */
  } finally {
    topping.value = false;
  }
}

// 佇列偏低就預先補題（藏住生成延遲，讓刷題不中斷）
function maybeTopUp() {
  if (endless.value && !topping.value && queue.value.length <= LOW_WATER) replenish();
}

async function grade(q: number) {
  const card = current.value;
  if (!card) return;
  queue.value.shift();
  revealed.value = false;
  resetCloze();
  reviewed.value++;
  maybeTopUp();
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: card.id, quality: q } });
  } catch {
    /* 失敗就算了，下次到期再複習 */
  }
}

function speak() {
  if (current.value) speech.speak(current.value.word, TTS_LANG[language.value] || "en-US");
}

async function generate() {
  generating.value = true;
  genMsg.value = "";
  try {
    const res = await aiFetch<any>("/api/lang/vocab/generate", {
      method: "POST",
      body: { language: language.value, theme: theme.value, count: 15 },
    });
    genMsg.value = `已加入 ${res.added} 個新單字（${res.theme}），開始複習吧！`;
    await reload();
  } catch (e: any) {
    genMsg.value = e?.data?.message || "生成失敗";
  } finally {
    generating.value = false;
  }
}

// 佇列被刷空時（預抓沒跟上）→ 立刻補題；開啟無限開關時若正好空了也補
watch([current, endless], ([cur, on]) => {
  if (on && !cur && !loading.value && !topping.value) replenish();
});

// 進到新單字卡 → 自動念一次（翻卡＋選擇題都套用；瀏覽器不支援 TTS 則略過）
// 只在卡片真的「換成另一張」時觸發（比對 id），翻卡顯示答案不會重念。
watch(current, (cur, prev) => {
  if (mode.value === "cloze") return; // 克漏字不自動念（會洩漏答案）
  if (cur?.word && cur.id !== prev?.id && speech.ttsSupported.value) speak();
});

onMounted(() => {
  tracker.start(language.value, "reading", "vocab"); // 複習計入「讀」時間，從進頁開始算
  reload();
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
