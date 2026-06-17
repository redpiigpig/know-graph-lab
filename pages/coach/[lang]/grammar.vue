<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${language}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">文法課</span>
      <div class="ml-auto flex items-center gap-3">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
        <NuxtLink v-if="language === 'en'" :to="`/coach/${language}/grammar-map`" class="text-xs text-indigo-600 hover:underline">🗺️ 文法地圖</NuxtLink>
        <span v-if="syllabus.length" class="text-xs text-gray-400">{{ doneCount }}/{{ syllabus.length }} 完成</span>
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <!-- 程度切換（英文 B2/C1/C2、日文 N5–N1…）-->
      <div v-if="levelScale.length" class="flex flex-wrap gap-1.5 mb-4">
        <button v-for="lv in levelScale" :key="lv" @click="selectLevel(lv)"
          class="text-xs px-3 py-1.5 rounded-lg border transition"
          :class="lv === level ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-500 hover:border-indigo-300'">
          {{ lv }}<span v-if="lv === currentLevel" class="ml-1 text-[10px]">（目前）</span>
        </button>
      </div>

      <div v-if="loading" class="text-gray-400 text-sm">教練正在排課…（第一次需稍候）</div>

      <div v-else class="space-y-2">
        <p class="text-xs text-gray-400 mb-2">依你目前程度循序排課；點開每一課有解說、例句與練習。難度會隨你升級調整。</p>
        <div v-for="(l, i) in syllabus" :key="l.id" class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <button @click="open(l)" class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition">
            <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0" :class="l.done ? 'bg-emerald-500 text-white' : 'bg-gray-100 text-gray-500'">{{ l.done ? '✓' : i + 1 }}</span>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-800">{{ l.title }}</div>
              <div class="text-[11px] text-gray-400 truncate">{{ l.summary }}</div>
            </div>
            <span class="text-gray-300 text-xs">{{ openId === l.id ? '▲' : '▼' }}</span>
          </button>

          <!-- 課程內容 -->
          <div v-if="openId === l.id" class="px-4 pb-4 border-t border-gray-50">
            <div v-if="l._loading" class="text-xs text-gray-400 py-3">教練備課中…</div>
            <template v-else-if="l.content">
              <div class="text-sm text-gray-700 whitespace-pre-wrap mt-3 leading-relaxed">{{ l.content.explanation }}</div>

              <div v-if="l.content.examples?.length" class="mt-3">
                <div class="text-[11px] font-semibold text-gray-400 uppercase mb-1">例句</div>
                <div class="space-y-1.5">
                  <div v-for="(ex, ei) in l.content.examples" :key="ei" class="bg-indigo-50/40 rounded-lg px-3 py-2">
                    <div class="text-sm text-gray-800 flex items-center gap-1">
                      {{ ex.target }}
                      <button v-if="!coach?.voiceless" @click="speak(ex.target)" class="text-gray-300 hover:text-indigo-500 text-xs">🔊</button>
                    </div>
                    <div class="text-xs text-gray-500">{{ ex.translation }}</div>
                    <div v-if="ex.note" class="text-[11px] text-indigo-500 mt-0.5">💡 {{ ex.note }}</div>
                  </div>
                </div>
              </div>

              <div v-if="l.content.practice?.length" class="mt-3">
                <div class="text-[11px] font-semibold text-gray-400 uppercase mb-1">練習</div>
                <div class="space-y-1.5">
                  <div v-for="(pr, pi) in l.content.practice" :key="pi" class="border border-gray-100 rounded-lg px-3 py-2">
                    <div class="text-sm text-gray-800">{{ pi + 1 }}. {{ pr.q }}</div>
                    <button @click="pr._show = !pr._show" class="text-[11px] text-indigo-600 mt-1 hover:underline">{{ pr._show ? '隱藏' : '看' }}答案</button>
                    <div v-if="pr._show" class="text-xs text-emerald-700 mt-1">{{ pr.answer }}</div>
                  </div>
                </div>
              </div>

              <button @click="toggleDone(l)" class="mt-4 w-full py-2 rounded-xl text-sm font-medium transition"
                :class="l.done ? 'bg-gray-100 text-gray-500' : 'bg-emerald-600 text-white hover:bg-emerald-700'">
                {{ l.done ? '✓ 已完成（點此取消）' : '標記為已完成' }}
              </button>
            </template>
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
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const tracker = useActivityTracker();
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const coach = ref<any>(null);
const level = ref("");
const currentLevel = ref("");
const levelScale = ref<string[]>([]);
const syllabus = ref<any[]>([]);
const loading = ref(true);
const openId = ref<string | null>(null);

const doneCount = computed(() => syllabus.value.filter((l) => l.done).length);

function speak(t: string) { speech.speak(t, TTS[language.value] || "en-US"); }

async function loadCoach() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === language.value);
}

async function load(lv?: string) {
  loading.value = true;
  openId.value = null;
  try {
    const r = await aiFetch<any>(`/api/lang/grammar?language=${language.value}${lv ? `&level=${encodeURIComponent(lv)}` : ""}`);
    level.value = r.level;
    currentLevel.value = r.currentLevel;
    levelScale.value = r.levelScale || [];
    syllabus.value = r.syllabus.map((s: any) => ({ ...s, _loading: false }));
  } finally {
    loading.value = false;
  }
}

function selectLevel(lv: string) {
  if (lv === level.value) return;
  load(lv);
}

async function open(l: any) {
  if (openId.value === l.id) { openId.value = null; return; }
  openId.value = l.id;
  if (!l.content) {
    l._loading = true;
    try {
      const { lesson } = await aiFetch<any>("/api/lang/grammar/lesson", { method: "POST", body: { language: language.value, level: level.value, lessonId: l.id } });
      l.content = lesson.content;
      if (l.content?.practice) l.content.practice.forEach((p: any) => (p._show = false));
    } catch (e: any) {
      alert(e?.data?.message || "備課失敗");
    } finally {
      l._loading = false;
    }
  }
}

async function toggleDone(l: any) {
  l.done = !l.done;
  await authedFetch("/api/lang/grammar/done", { method: "POST", body: { language: language.value, level: level.value, lessonId: l.id, done: l.done } });
}

onMounted(async () => {
  tracker.start(language.value, "reading", "grammar"); // 文法課計入「讀」時間
  await Promise.all([loadCoach(), load()]);
  // 從文法地圖深連結 ?open=<lessonId> 自動展開該課
  const openParam = route.query.open as string | undefined;
  if (openParam) {
    const l = syllabus.value.find((s) => s.id === openParam);
    if (l) open(l);
  }
});
</script>
