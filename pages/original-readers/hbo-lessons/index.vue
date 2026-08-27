<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="希伯來文50課讀本" :back="{ to: '/original-readers', label: '原文讀本總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入50課完整主資料…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="reader">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-9 text-[#f7f0df] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-amber-300">PRIVATE · BIBLICAL HEBREW · 50 LESSONS</p>
          <h1 class="mt-3 max-w-4xl font-serif text-3xl font-semibold leading-tight sm:text-5xl">{{ reader.title }}</h1>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-stone-300">{{ reader.subtitle }}</p>
          <dl class="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <div v-for="stat in stats" :key="stat.label" class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">{{ stat.label }}</dt>
              <dd class="mt-1 text-xl font-semibold">{{ stat.value }}</dd>
            </div>
          </dl>
        </header>

        <section class="mt-6 grid gap-4 lg:grid-cols-[1fr_1fr]">
          <div class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-950">
            <div class="flex items-start gap-3">
              <span class="mt-0.5 rounded-full bg-amber-200 px-2 py-1 text-[10px] font-bold tracking-wider">AUDIO</span>
              <div>
                <p class="font-semibold">{{ reader.audioStatus.label }}</p>
                <p class="mt-1 text-amber-900/80">{{ reader.audioStatus.policy }}</p>
                <a
                  v-for="reference in reader.pronunciationReferences"
                  :key="reference.id"
                  :href="reference.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="mt-3 inline-flex font-semibold underline decoration-amber-400 underline-offset-4"
                >{{ reference.label }} ↗</a>
              </div>
            </div>
          </div>

          <NuxtLink :to="reader.haggadah.href" class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">FULL HAGGADAH APPENDIX</p>
            <div class="mt-2 flex items-start justify-between gap-5">
              <div>
                <h2 class="font-serif text-xl font-semibold">完整逾越節禮文</h2>
                <p class="hebrew-title mt-1 text-xl text-stone-600" dir="rtl" lang="hbo">{{ reader.haggadah.titleHe }}</p>
                <p class="mt-2 text-xs text-stone-500">傳統15步 · {{ reader.haggadah.segmentCount }}段 · 全文附點</p>
              </div>
              <span class="text-xl transition group-hover:translate-x-1">→</span>
            </div>
          </NuxtLink>

          <NuxtLink to="/original-readers/hbo-lessons/tables" class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">APPENDIX · REFERENCE TABLES</p>
            <div class="mt-2 flex items-start justify-between gap-5">
              <div class="min-w-0">
                <h2 class="font-serif text-xl font-semibold">附錄參考表</h2>
                <p class="mt-1 text-sm text-stone-500 break-words">專名按類分節，數字、親屬與曆法各一張</p>
                <p class="mt-2 text-sm text-stone-600">{{ reader.referenceTables.length }} 張表・{{ referenceEntryCount }} 條</p>
              </div>
              <span class="mt-1 shrink-0 text-xl transition group-hover:translate-x-1">→</span>
            </div>
          </NuxtLink>
        </section>

        <nav class="mt-7 flex flex-wrap gap-2" aria-label="課程分部">
          <button type="button" class="rounded-full border px-4 py-2 text-xs font-semibold transition" :class="track === 'all' ? activeFilter : idleFilter" @click="track = 'all'">全部50課</button>
          <button type="button" class="rounded-full border px-4 py-2 text-xs font-semibold transition" :class="track === 'scripture' ? activeFilter : idleFilter" @click="track = 'scripture'">1–25 · 完整章</button>
          <button type="button" class="rounded-full border px-4 py-2 text-xs font-semibold transition" :class="track === 'prayer_article' ? activeFilter : idleFilter" @click="track = 'prayer_article'">26–50 · 禱文／文章</button>
        </nav>

        <section v-for="section in visibleSections" :key="section.id" class="mt-8">
          <header class="mb-4 border-b border-stone-300 pb-3">
            <p class="text-[11px] font-bold tracking-[0.22em] text-stone-400">{{ section.eyebrow }}</p>
            <h2 class="mt-1 font-serif text-2xl font-semibold">{{ section.title }}</h2>
            <p class="mt-1 text-sm leading-6 text-stone-500">{{ section.description }}</p>
          </header>

          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <NuxtLink
              v-for="lesson in lessonsFor(section.id)"
              :key="lesson.lesson"
              :to="`/original-readers/hbo-lessons/${lesson.lesson}`"
              class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md"
            >
              <div class="flex items-center justify-between gap-3">
                <span class="font-mono text-xs font-semibold text-stone-500">LESSON {{ String(lesson.lesson).padStart(2, '0') }}</span>
                <span class="rounded-full bg-stone-100 px-2.5 py-1 text-[11px] text-stone-500">{{ lesson.readingSegmentCount }}段</span>
              </div>
              <h3 class="mt-4 font-serif text-lg font-semibold leading-7">{{ lesson.titleZh }}</h3>
              <p class="hebrew-title mt-1 text-lg text-stone-600" dir="rtl" lang="hbo">{{ lesson.titleHe }}</p>
              <p class="mt-3 text-xs text-stone-500">{{ lesson.ref }}<template v-if="lesson.difficulty"> · 難度 {{ lesson.difficulty }}</template></p>
              <dl class="mt-4 grid grid-cols-3 gap-2 border-t border-stone-200 pt-4 text-center text-xs">
                <div><dt class="text-stone-400">詞彙</dt><dd class="mt-1 font-semibold">20</dd></div>
                <div><dt class="text-stone-400">專名</dt><dd class="mt-1 font-semibold">{{ lesson.properNameCount }}</dd></div>
                <div><dt class="text-stone-400">背誦</dt><dd class="mt-1 font-semibold">2節</dd></div>
              </dl>
              <p class="mt-4 text-[11px] leading-5 text-stone-400">{{ lesson.memoryRefs.join(' · ') }}</p>
              <p class="mt-4 text-xs font-semibold text-stone-700 group-hover:text-stone-950">開啟本課完整讀本 →</p>
            </NuxtLink>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({
  title: "希伯來文50課私人讀本 — Know Graph Lab",
  meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }],
});

interface AudioStatus {
  status: "not_recorded";
  label: string;
  recordedTrackCount: 0;
  policy: string;
}
interface PronunciationReference {
  id: string;
  label: string;
  description: string;
  url: string;
}
interface LessonSummary {
  lesson: number;
  track: "scripture" | "prayer_article";
  titleZh: string;
  titleHe: string;
  ref: string;
  difficulty: number | null;
  genre: string;
  vocabularyCount: number;
  properNameCount: number;
  memoryRefs: string[];
  readingSegmentCount: number;
  audioStatus: AudioStatus;
}
interface ReaderOverview {
  title: string;
  subtitle: string;
  counts: {
    lessons: number;
    vocabulary: number;
    memoryVerses: number;
    scriptureChapters: number;
    prayersArticles: number;
    haggadahSteps: number;
    haggadahSegments: number;
  };
  audioStatus: AudioStatus;
  pronunciationReferences: PronunciationReference[];
  haggadah: {
    titleHe: string;
    href: string;
    stepCount: number;
    segmentCount: number;
  };
  referenceTables: {
    id: string;
    titleZh: string;
    titleHe: string;
    groupCount: number;
    entryCount: number;
    href: string;
  }[];
  lessons: LessonSummary[];
}

const supabase = useSupabaseClient();
const reader = ref<ReaderOverview | null>(null);
const pending = ref(true);
const error = ref("");
const track = ref<"all" | "scripture" | "prayer_article">("all");
const activeFilter = "border-stone-900 bg-stone-900 text-white";
const idleFilter = "border-stone-300 bg-white text-stone-600 hover:border-stone-500";

const sections = [
  {
    id: "scripture" as const,
    eyebrow: "PART I · LESSONS 01–25",
    title: "25章完整經文",
    description: "由重複性高的禮儀詩篇進至古歌與智慧詩；每課正文是一整章，不是節選摘要。",
  },
  {
    id: "prayer_article" as const,
    eyebrow: "PART II · LESSONS 26–50",
    title: "25篇禱文與拉比文章",
    description: "排印正文採完整附點校訂層；來源原貌另由伺服器主資料保存。",
  },
];

const stats = computed(() => reader.value ? [
  { label: "課程", value: reader.value.counts.lessons },
  { label: "核心詞", value: reader.value.counts.vocabulary },
  { label: "背誦經節", value: reader.value.counts.memoryVerses },
  { label: "完整章", value: reader.value.counts.scriptureChapters },
  { label: "禱文／文章", value: reader.value.counts.prayersArticles },
  { label: "Haggadah", value: `${reader.value.counts.haggadahSteps}步` },
] : []);
const visibleSections = computed(() => sections.filter((section) => track.value === "all" || track.value === section.id));

const referenceEntryCount = computed(() =>
  (reader.value?.referenceTables ?? []).reduce((total, table) => total + table.entryCount, 0),
);

function lessonsFor(section: "scripture" | "prayer_article") {
  return reader.value?.lessons.filter((lesson) => lesson.track === section) || [];
}

onMounted(async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    reader.value = await $fetch<ReaderOverview>("/api/original-readers/hbo-lessons", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
});
</script>

<style scoped>
.hebrew-title {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
  line-height: 1.8;
}
</style>
