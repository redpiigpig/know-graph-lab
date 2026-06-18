<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${lang}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">字典 · {{ coach?.langLabel }}</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-4xl mx-auto w-full space-y-4">
      <!-- 排序方式 + 搜尋 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-4 space-y-3">
        <div class="flex items-center gap-2">
          <button @click="setSort('alpha')" :class="tabClass('alpha')">🔤 字母順序</button>
          <button @click="setSort('theme')" :class="tabClass('theme')">🎯 主題</button>
          <button @click="setSort('level')" :class="tabClass('level')">📊 分級</button>
          <button @click="setSort('category')" :class="tabClass('category')">🗂️ 頻率分類</button>
          <span class="ml-auto text-[11px] text-gray-400">共 {{ total.toLocaleString() }} 字</span>
        </div>

        <input v-model="search" @input="onSearchInput" type="text"
          :placeholder="`搜尋單字或中文釋義…`"
          class="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm focus:border-indigo-400 focus:outline-none" />

        <!-- facet chips：主題/分級/分類 -->
        <div v-if="sort === 'theme'" class="flex flex-wrap items-center gap-1.5">
          <template v-if="themes.length">
            <button @click="pickFilter('')" :class="chipClass(activeFilter === '')">全部</button>
            <button v-for="t in themes" :key="t.theme" @click="pickFilter(t.theme)" :class="chipClass(activeFilter === t.theme)">
              {{ t.theme }}<span class="opacity-60"> · {{ t.count }}</span>
            </button>
          </template>
          <span v-else class="text-[11px] text-amber-600">語意主題分類建置中…（背景批次跑完即顯示）</span>
        </div>
        <div v-else-if="sort === 'level' && levels.length" class="flex flex-wrap items-center gap-1.5">
          <button @click="pickFilter('')" :class="chipClass(activeFilter === '')">全部</button>
          <button v-for="l in levels" :key="l.level" @click="pickFilter(l.level)" :class="chipClass(activeFilter === l.level)">
            {{ l.level }}<span class="opacity-60"> · {{ l.count }}</span>
          </button>
        </div>
        <div v-else-if="sort === 'category' && categories.length" class="flex flex-wrap items-center gap-1.5">
          <button @click="pickFilter('')" :class="chipClass(activeFilter === '')">全部</button>
          <button v-for="c in categories" :key="c.category" @click="pickFilter(c.category)" :class="chipClass(activeFilter === c.category)">
            {{ c.category }}<span class="opacity-60"> · {{ c.count }}</span>
          </button>
        </div>
      </div>

      <!-- 字表 -->
      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入中…</div>
      <div v-else-if="!rows.length" class="text-sm text-gray-500 py-10 text-center">沒有符合的字。</div>
      <div v-else class="space-y-2">
        <div v-for="(w, i) in rows" :key="i" class="bg-white rounded-xl border border-gray-100 p-3.5">
          <div class="flex items-baseline gap-2">
            <span class="text-xl font-semibold text-gray-900 leading-tight" :dir="rtl ? 'rtl' : 'ltr'">{{ w.word }}</span>
            <span v-if="w.reading" class="text-xs text-gray-400">{{ w.reading }}</span>
            <span v-if="w.part_of_speech" class="text-[11px] px-1.5 py-0.5 rounded bg-slate-100 text-gray-500">{{ w.part_of_speech }}</span>
            <button @click="speak(w)" class="ml-auto text-gray-300 hover:text-indigo-500 text-sm" title="朗讀">🔊</button>
          </div>
          <div class="text-sm text-gray-700 mt-1">{{ w.meaning }}</div>
          <div v-if="w.example" class="text-[12px] text-gray-400 mt-1 leading-relaxed" :dir="rtl ? 'rtl' : 'ltr'">{{ w.example }}</div>
          <div class="mt-1 flex gap-1.5">
            <span v-if="w.level" class="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-500">{{ w.level }}</span>
            <span v-if="w.category" class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-50 text-gray-400">{{ w.category }}</span>
          </div>
        </div>

        <button v-if="rows.length < total" @click="loadMore" :disabled="loadingMore"
          class="w-full py-2.5 rounded-xl bg-white border border-gray-200 text-sm text-gray-600 hover:border-indigo-300 disabled:opacity-50 transition">
          {{ loadingMore ? "載入中…" : `載入更多（已顯示 ${rows.length} / ${total.toLocaleString()}）` }}
        </button>
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

definePageMeta({ middleware: "coach-auth" });

interface Word { word: string; reading?: string; meaning?: string; example?: string; part_of_speech?: string; category?: string; level?: string }
interface Resp { rows: Word[]; total: number; page: number; limit: number; sort: string; levels: { level: string; count: number }[]; categories: { category: string; count: number }[]; themes: { theme: string; count: number }[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const speech = useSpeech();
const tracker = useActivityTracker();
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const coach = ref<any>(null);
const rtl = computed(() => lang.value === "hbo");
const sort = ref<"alpha" | "level" | "category" | "theme">("alpha");
const activeFilter = ref("");
const search = ref("");
const rows = ref<Word[]>([]);
const total = ref(0);
const page = ref(0);
const levels = ref<Resp["levels"]>([]);
const categories = ref<Resp["categories"]>([]);
const themes = ref<Resp["themes"]>([]);
const loading = ref(true);
const loadingMore = ref(false);

function tabClass(s: string) {
  return `text-sm px-3 py-1.5 rounded-lg font-medium transition ${sort.value === s ? "bg-indigo-600 text-white" : "bg-slate-100 text-gray-500 hover:bg-slate-200"}`;
}
function chipClass(active: boolean) {
  return `text-xs px-2.5 py-1 rounded-full border transition ${active ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-500 hover:border-indigo-300"}`;
}

function speak(w: Word) {
  speech.speak(w.example || w.word, coach.value?.ttsLang || TTS[lang.value] || "en-US");
}

function buildUrl(p: number) {
  const params = new URLSearchParams({ language: lang.value, sort: sort.value, page: String(p) });
  if (sort.value !== "alpha" && activeFilter.value) params.set(sort.value, activeFilter.value);
  if (search.value.trim()) params.set("q", search.value.trim());
  return `/api/lang/dictionary?${params.toString()}`;
}

async function fetchPage(p: number, append: boolean) {
  const r = await authedFetch<Resp>(buildUrl(p));
  total.value = r.total;
  if (p === 0) { levels.value = r.levels; categories.value = r.categories; themes.value = r.themes || []; }
  rows.value = append ? [...rows.value, ...r.rows] : r.rows;
  page.value = p;
}

async function reload() {
  loading.value = true;
  try { await fetchPage(0, false); } finally { loading.value = false; }
}
async function loadMore() {
  loadingMore.value = true;
  try { await fetchPage(page.value + 1, true); } finally { loadingMore.value = false; }
}
function setSort(s: "alpha" | "level" | "category" | "theme") {
  if (sort.value === s) return;
  sort.value = s; activeFilter.value = ""; reload();
}
function pickFilter(v: string) {
  activeFilter.value = v; reload();
}

let searchTimer: any = null;
function onSearchInput() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(reload, 350);
}

onMounted(async () => {
  try {
    const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
    coach.value = coaches.find((c) => c.language === lang.value);
  } catch { /* ignore */ }
  await reload();
  tracker.start(lang.value, "reading", "dictionary");
});
</script>
