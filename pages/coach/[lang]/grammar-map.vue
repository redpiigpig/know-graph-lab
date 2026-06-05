<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">🗺️ 文法地圖</span>
      <NuxtLink :to="`/coach/${language}/grammar`" class="ml-auto text-xs text-indigo-600 hover:underline">前往文法課 →</NuxtLink>
    </nav>

    <div class="flex-1 p-5 max-w-3xl mx-auto w-full space-y-5">
      <!-- 非英文 -->
      <div v-if="!available && !loading" class="bg-white rounded-2xl border border-gray-100 p-8 text-center text-sm text-gray-500">
        文法地圖目前只有英文版。
      </div>

      <template v-else>
        <!-- 查詢 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <h1 class="text-sm font-semibold text-gray-800">打字發問 / 查文法</h1>
          <p class="text-xs text-gray-400 mt-0.5 mb-3">用中文或英文問（例：「什麼時候用現在完成式？」「it is said that 是什麼」），或直接貼一個句子，幫你定位到對應的文法點。</p>
          <div class="flex gap-2">
            <input v-model="q" @keydown.enter="lookup" placeholder="例：present perfect vs past simple / 名詞化 / Not only did he…"
              class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
            <button @click="lookup" :disabled="looking || !q.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40 hover:bg-indigo-700 transition whitespace-nowrap">{{ looking ? '查詢中…' : '查詢' }}</button>
          </div>

          <!-- 查詢結果 -->
          <div v-if="result" class="mt-4 border-t border-gray-100 pt-4">
            <p class="text-sm text-gray-700">{{ result.answer }}</p>
            <div v-if="result.matches?.length" class="mt-3 space-y-1.5">
              <button v-for="m in result.matches" :key="m.id" @click="reveal(m.id)"
                class="w-full flex items-center gap-2 text-left px-3 py-2 rounded-xl border border-indigo-100 bg-indigo-50/50 hover:bg-indigo-50 transition">
                <span class="text-[11px] text-gray-400 flex-shrink-0">{{ m.category }}</span>
                <span class="text-sm font-medium text-indigo-700 flex-1">{{ m.title }} <span class="text-gray-400 font-normal">{{ m.en }}</span></span>
                <span class="text-indigo-400 text-xs">看 →</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 即時關鍵字過濾 -->
        <div class="flex items-center gap-2">
          <input v-model="filter" placeholder="🔍 即時篩選文法點（中英關鍵字）"
            class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white focus:outline-none focus:border-indigo-400" />
          <span class="text-xs text-gray-400">{{ shownCount }} / {{ totalCount }}</span>
        </div>

        <!-- 分類瀏覽 -->
        <div v-for="cat in filteredCategories" :key="cat.key" class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div class="px-5 py-3 bg-gradient-to-r from-indigo-50/60 to-transparent border-b border-gray-50">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ cat.icon }}</span>
              <h2 class="text-sm font-bold text-gray-900">{{ cat.label }}</h2>
            </div>
            <p class="text-[11px] text-gray-400 mt-0.5">{{ cat.blurb }}</p>
          </div>
          <div class="divide-y divide-gray-50">
            <div v-for="t in cat.topics" :key="t.id" :ref="(el) => setRef(t.id, el)">
              <button @click="reveal(t.id)" class="w-full flex items-center gap-2 px-5 py-2.5 text-left hover:bg-gray-50 transition">
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-800">{{ t.title }} <span class="text-[11px] text-gray-400 font-normal">{{ t.en }}</span></div>
                  <div class="text-[11px] text-gray-400 truncate">{{ t.summary }}</div>
                </div>
                <span class="text-[10px] text-gray-400 flex-shrink-0">{{ t.levels.join('·') }}</span>
                <span class="text-gray-300 text-xs">{{ openId === t.id ? '▲' : '▼' }}</span>
              </button>
              <div v-if="openId === t.id" class="px-5 pb-4 bg-slate-50/50">
                <div class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed pt-2">{{ t.explanation }}</div>
                <div v-if="t.examples?.length" class="mt-3 space-y-1.5">
                  <div v-for="(ex, ei) in t.examples" :key="ei" class="bg-white rounded-lg px-3 py-2 border border-gray-100">
                    <div class="text-sm text-gray-800 flex items-center gap-1">
                      {{ ex.target }}
                      <button @click="speak(ex.target)" class="text-gray-300 hover:text-indigo-500 text-xs">🔊</button>
                    </div>
                    <div class="text-xs text-gray-500">{{ ex.translation }}</div>
                    <div v-if="ex.note" class="text-[11px] text-indigo-500 mt-0.5">💡 {{ ex.note }}</div>
                  </div>
                </div>
                <NuxtLink :to="`/coach/${language}/grammar?open=${t.id}`" class="inline-block mt-3 text-xs text-indigo-600 hover:underline">到文法課練這一課（含練習）→</NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useCoachAi } from "~/composables/useCoachAi";
import { useSpeech } from "~/composables/useSpeech";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const TTS: Record<string, string> = { en: "en-US" };

const loading = ref(true);
const available = ref(false);
const categories = ref<any[]>([]);
const q = ref("");
const looking = ref(false);
const result = ref<any>(null);
const filter = ref("");
const openId = ref<string | null>(null);
const refs: Record<string, any> = {};

function setRef(id: string, el: any) { if (el) refs[id] = el; }
function speak(t: string) { speech.speak(t, TTS[language.value] || "en-US"); }

const totalCount = computed(() => categories.value.reduce((n, c) => n + c.topics.length, 0));

// 即時關鍵字過濾（比對中英標題、摘要、keywords）
const filteredCategories = computed(() => {
  const f = filter.value.trim().toLowerCase();
  if (!f) return categories.value;
  return categories.value
    .map((c) => ({
      ...c,
      topics: c.topics.filter((t: any) =>
        t.title.toLowerCase().includes(f) ||
        t.en.toLowerCase().includes(f) ||
        t.summary.toLowerCase().includes(f) ||
        (t.keywords || []).some((k: string) => k.toLowerCase().includes(f))
      ),
    }))
    .filter((c) => c.topics.length);
});
const shownCount = computed(() => filteredCategories.value.reduce((n, c) => n + c.topics.length, 0));

async function lookup() {
  if (!q.value.trim() || looking.value) return;
  looking.value = true;
  result.value = null;
  try {
    result.value = await aiFetch<any>("/api/lang/grammar/lookup", {
      method: "POST",
      body: { language: language.value, query: q.value.trim() },
    });
  } catch (e: any) {
    result.value = { answer: e?.data?.message || "查詢失敗，請重試", matches: [] };
  } finally {
    looking.value = false;
  }
}

// 展開某 topic 並捲動到它
async function reveal(id: string) {
  openId.value = openId.value === id ? null : id;
  if (openId.value) {
    filter.value = ""; // 清過濾確保該卡片在畫面上
    await nextTick();
    refs[id]?.scrollIntoView?.({ behavior: "smooth", block: "center" });
  }
}

onMounted(async () => {
  try {
    const r = await authedFetch<any>(`/api/lang/grammar/map?language=${language.value}`);
    available.value = !!r.available;
    categories.value = r.categories || [];
  } finally {
    loading.value = false;
  }
});
</script>
