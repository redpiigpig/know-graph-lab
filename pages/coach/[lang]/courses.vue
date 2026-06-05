<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">主題教程</span>
      <div class="ml-auto flex items-center gap-3">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
        <NuxtLink v-if="active" :to="''" @click.prevent="active = null" class="text-xs text-indigo-600 hover:underline">← 回課程清單</NuxtLink>
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <!-- 課程清單 + 建立 -->
      <template v-if="!active">
        <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>
        <template v-else>
          <div v-if="courses.length" class="space-y-2 mb-5">
            <button v-for="c in courses" :key="c.id" @click="openCourse(c.id)" class="w-full text-left bg-white rounded-2xl border border-gray-100 p-4 hover:border-indigo-300 transition">
              <div class="flex items-center justify-between">
                <div class="text-sm font-semibold text-gray-800">{{ c.title }}</div>
                <span class="text-[11px] text-gray-400">約 {{ c.minutes }} 分鐘</span>
              </div>
              <div class="flex items-center gap-2 mt-2">
                <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-500 rounded-full" :style="{ width: (c.total ? (c.done / c.total * 100) : 0) + '%' }" />
                </div>
                <span class="text-[11px] text-gray-400">{{ c.done }}/{{ c.total }}</span>
              </div>
            </button>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-1">建立新課程</h2>
            <p class="text-xs text-gray-400 mb-3">挑一個主題或自訂；依你目前程度生成循序課表，每課標示預估時間。</p>
            <div class="flex flex-wrap gap-1.5 mb-3">
              <button v-for="p in presets" :key="p" @click="theme = p" class="text-xs px-2.5 py-1 rounded-full border transition" :class="theme === p ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ p }}</button>
            </div>
            <div class="flex gap-2">
              <input v-model="theme" placeholder="主題，如：宗教文獻英文精讀 / 學術寫作" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
              <button @click="create" :disabled="creating || !theme.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40 whitespace-nowrap">{{ creating ? '生成中…' : '建立' }}</button>
            </div>
          </div>
        </template>
      </template>

      <!-- 課程內容 -->
      <template v-else>
        <h1 class="text-lg font-bold text-gray-900">{{ active.title }}</h1>
        <p class="text-xs text-gray-400 mb-3">{{ active.level }} 程度 · {{ active.syllabus.length }} 課 · 已完成 {{ doneCount }}</p>
        <div class="space-y-2">
          <div v-for="(l, i) in active.syllabus" :key="l.id" class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            <button @click="openLesson(l)" class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition">
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0" :class="l.done ? 'bg-emerald-500 text-white' : 'bg-gray-100 text-gray-500'">{{ l.done ? '✓' : i + 1 }}</span>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-800">{{ l.title }}</div>
                <div class="text-[11px] text-gray-400 truncate">{{ l.summary }} · 約 {{ l.minutes }} 分</div>
              </div>
              <span class="text-gray-300 text-xs">{{ openId === l.id ? '▲' : '▼' }}</span>
            </button>
            <div v-if="openId === l.id" class="px-4 pb-4 border-t border-gray-50">
              <div v-if="l._loading" class="text-xs text-gray-400 py-3">教練備課中…</div>
              <template v-else-if="l.content">
                <div class="text-sm text-gray-700 whitespace-pre-wrap mt-3 leading-relaxed">{{ l.content.explanation }}</div>
                <div v-if="l.content.examples?.length" class="mt-3 space-y-1.5">
                  <div v-for="(ex, ei) in l.content.examples" :key="ei" class="bg-indigo-50/40 rounded-lg px-3 py-2">
                    <div class="text-sm text-gray-800 flex items-center gap-1">{{ ex.target }}<button v-if="!coach?.voiceless" @click="speak(ex.target)" class="text-gray-300 hover:text-indigo-500 text-xs">🔊</button></div>
                    <div class="text-xs text-gray-500">{{ ex.translation }}</div>
                    <div v-if="ex.note" class="text-[11px] text-indigo-500 mt-0.5">💡 {{ ex.note }}</div>
                  </div>
                </div>
                <div v-if="l.content.practice?.length" class="mt-3 space-y-1.5">
                  <div v-for="(pr, pi) in l.content.practice" :key="pi" class="border border-gray-100 rounded-lg px-3 py-2">
                    <div class="text-sm text-gray-800">{{ pi + 1 }}. {{ pr.q }}</div>
                    <button @click="pr._show = !pr._show" class="text-[11px] text-indigo-600 mt-1 hover:underline">{{ pr._show ? '隱藏' : '看' }}答案</button>
                    <div v-if="pr._show" class="text-xs text-emerald-700 mt-1">{{ pr.answer }}</div>
                  </div>
                </div>
                <button @click="toggleDone(l)" class="mt-4 w-full py-2 rounded-xl text-sm font-medium transition" :class="l.done ? 'bg-gray-100 text-gray-500' : 'bg-emerald-600 text-white hover:bg-emerald-700'">{{ l.done ? '✓ 已完成（取消）' : '標記為已完成' }}</button>
              </template>
            </div>
          </div>
        </div>
      </template>
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
const courses = ref<any[]>([]);
const presets = ref<string[]>([]);
const loading = ref(true);
const theme = ref("");
const creating = ref(false);
const active = ref<any>(null);
const openId = ref<string | null>(null);

const doneCount = computed(() => active.value?.syllabus.filter((l: any) => l.done).length || 0);
function speak(t: string) { speech.speak(t, TTS[language.value] || "en-US"); }

async function loadCoach() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === language.value);
}
async function loadList() {
  loading.value = true;
  try {
    const r = await authedFetch<any>(`/api/lang/courses?language=${language.value}`);
    courses.value = r.courses;
    presets.value = r.presets;
  } finally {
    loading.value = false;
  }
}
async function create() {
  creating.value = true;
  try {
    const { course } = await aiFetch<any>("/api/lang/courses/create", { method: "POST", body: { language: language.value, theme: theme.value } });
    theme.value = "";
    active.value = { ...course, syllabus: course.syllabus.map((s: any) => ({ ...s, _loading: false })) };
    await loadList();
  } catch (e: any) {
    alert(e?.data?.message || "建立失敗");
  } finally {
    creating.value = false;
  }
}
async function openCourse(id: string) {
  const { course } = await authedFetch<any>(`/api/lang/courses/${id}`);
  active.value = { ...course, syllabus: course.syllabus.map((s: any) => ({ ...s, _loading: false })) };
  openId.value = null;
}
async function openLesson(l: any) {
  if (openId.value === l.id) { openId.value = null; return; }
  openId.value = l.id;
  if (!l.content) {
    l._loading = true;
    try {
      const { lesson } = await aiFetch<any>("/api/lang/courses/lesson", { method: "POST", body: { courseId: active.value.id, lessonId: l.id } });
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
  await authedFetch("/api/lang/courses/done", { method: "POST", body: { courseId: active.value.id, lessonId: l.id, done: l.done } });
}

onMounted(async () => {
  tracker.start(language.value, "reading", "course"); // 主題教程計入「讀」時間
  await Promise.all([loadCoach(), loadList()]);
});
</script>
