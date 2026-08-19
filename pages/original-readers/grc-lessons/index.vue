<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader title="新約希臘文50課讀本" :back="{ to: '/original-readers', label: '三冊總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入 50 課完整主資料…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="reader">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#1b2430] px-6 py-9 text-[#f4efe2] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-sky-300">PRIVATE · NEW TESTAMENT GREEK · 50 LESSONS</p>
          <h1 class="mt-3 max-w-4xl font-serif text-3xl font-semibold leading-tight sm:text-5xl">{{ reader.title }}</h1>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-stone-300">{{ reader.subtitle }}</p>
          <p class="mt-2 text-xs text-stone-400">課程依 {{ reader.textbook }}</p>
          <dl class="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <div v-for="stat in stats" :key="stat.label" class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">{{ stat.label }}</dt>
              <dd class="mt-1 text-xl font-semibold">{{ stat.value }}</dd>
            </div>
          </dl>
        </header>

        <section class="mt-6 grid gap-4 lg:grid-cols-[1fr_1fr]">
          <div class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-950">
            <p class="text-[10px] font-bold tracking-[0.2em] text-amber-700">RELEASE STATE</p>
            <p class="mt-2 font-semibold">{{ statusLabel }}</p>
            <p v-if="!reader.glossProgress.complete" class="mt-1 text-amber-900/80">
              繁體中文詞義已完成 {{ reader.glossProgress.glossed }}／{{ reader.glossProgress.target }} 詞；未補完前不進入排版。
            </p>
            <p class="mt-2 text-amber-900/80">{{ reader.audioStatus.label }}：{{ reader.audioStatus.policy }}</p>
            <ul v-if="reader.openProblems.length" class="mt-3 list-disc space-y-1 pl-5 text-amber-900/90">
              <li v-for="problem in reader.openProblems" :key="problem">{{ problem }}</li>
            </ul>
          </div>

          <NuxtLink :to="reader.liturgy.href" class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">APPENDIX · DIVINE LITURGY</p>
            <div class="mt-2 flex items-start justify-between gap-5">
              <div class="min-w-0">
                <h2 class="font-serif text-xl font-semibold break-words">{{ reader.liturgy.title }}</h2>
                <p class="greek mt-1 truncate text-sm text-stone-500">{{ reader.liturgy.titleGrc }}</p>
                <p class="mt-2 text-sm text-stone-600">{{ reader.liturgy.sectionCount }} 個禮儀段落・{{ reader.liturgy.stepCount }} 段全文</p>
              </div>
              <span class="mt-1 shrink-0 text-2xl text-stone-400 transition group-hover:translate-x-1">→</span>
            </div>
          </NuxtLink>
        </section>

        <section class="mt-8">
          <h2 class="font-serif text-2xl font-semibold">五十課</h2>
          <p class="mt-1 text-sm text-stone-600">
            第 1–30 課是 Mounce BBG 第 4–36 章本身的詞量，長短不齊；第 31–50 課平均攤完頻率延伸。
            第 1–25 課配完整經文一章，第 26–50 課配教父、信經與教令。
          </p>
          <ul class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="lesson in reader.lessons" :key="lesson.id">
              <NuxtLink :to="lesson.href" class="flex h-full flex-col rounded-2xl border border-stone-300 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-xs font-bold tracking-wider text-stone-400">第 {{ lesson.lesson }} 課</span>
                  <span class="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] text-stone-600">{{ lesson.reading.label }}</span>
                </div>
                <h3 class="mt-2 line-clamp-2 font-serif text-base font-semibold leading-6 break-words">{{ lesson.reading.titleZh }}</h3>
                <p class="greek mt-1 truncate text-xs text-stone-500">{{ lesson.reading.titleGrc }}</p>
                <dl class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-stone-500">
                  <div><dt class="inline">生詞 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.vocabularyCount }}</dd></div>
                  <div><dt class="inline">背誦 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.memoryVerseCount }}</dd></div>
                  <div><dt class="inline">讀文 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.reading.wordCount }} 詞</dd></div>
                  <div v-if="lesson.reading.completeness === 'excerpt'"><dd class="inline text-amber-700">節錄</dd></div>
                </dl>
                <p class="mt-2 truncate text-[11px] text-stone-400">{{ lesson.vocabularySource }}</p>
              </NuxtLink>
            </li>
          </ul>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
interface LessonSummary {
  lesson: number;
  id: string;
  title: string;
  vocabularySource: string;
  vocabularyCount: number;
  memoryVerseCount: number;
  glossedCount: number;
  reading: { kind: string; titleZh: string; titleGrc: string; difficulty: number; label: string; completeness: string; wordCount: number };
  href: string;
}
interface Overview {
  title: string;
  subtitle: string;
  textbook: string;
  releaseStatus: string;
  counts: Record<string, number>;
  audioStatus: { label: string; policy: string };
  glossProgress: { glossed: number; target: number; complete: boolean };
  openProblems: string[];
  liturgy: { title: string; titleGrc: string; stepCount: number; sectionCount: number; href: string };
  lessons: LessonSummary[];
}

const supabase = useSupabaseClient();
const reader = ref<Overview | null>(null);
const pending = ref(true);
const error = ref("");

const STATUS_LABELS: Record<string, string> = {
  planned: "規劃中",
  source_frozen: "來源已凍結，詞義層尚未補完",
  vocabulary_complete: "詞彙完成",
  content_complete_layout_pending: "內容完成，待排版",
  content_complete_audio_pending: "內容完成，待錄音",
  print_qa_passed_audio_pending: "印刷 QA 通過，待錄音",
  release_candidate: "候選版",
  complete_private_release: "私人版完成",
};

const statusLabel = computed(() =>
  reader.value ? STATUS_LABELS[reader.value.releaseStatus] || reader.value.releaseStatus : "",
);

const stats = computed(() => {
  const counts = reader.value?.counts || {};
  return [
    { label: "課次", value: counts.lessons ?? 0 },
    { label: "詞彙", value: counts.vocabulary ?? 0 },
    { label: "背誦節", value: counts.memoryVerses ?? 0 },
    { label: "經文章", value: counts.scriptureChapters ?? 0 },
    { label: "教父讀文", value: counts.patristicReadings ?? 0 },
    { label: "禮儀段", value: counts.liturgySteps ?? 0 },
  ];
});

async function load() {
  pending.value = true;
  error.value = "";
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    reader.value = await $fetch<Overview>("/api/original-readers/grc-lessons", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    useHead({ title: `${reader.value.title} — 私人讀本` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.greek {
  font-family: "SBL Greek", "New Athena Unicode", "Gentium Plus", "Noto Serif", serif;
}
</style>
