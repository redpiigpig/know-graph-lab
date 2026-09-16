<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader title="日文宗教學讀本（第一、二冊）" :back="{ to: '/original-readers', label: '原文讀本總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入兩冊一百課完整主資料…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="reader">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#231d17] px-6 py-9 text-[#f6efe3] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-emerald-300">PRIVATE · JAPANESE · 2 VOLUMES · 100 LESSONS</p>
          <h1 class="mt-3 max-w-4xl font-serif text-3xl font-semibold leading-tight sm:text-5xl">{{ reader.title }}</h1>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-stone-300">{{ reader.subtitle }}</p>
          <dl class="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            <div v-for="stat in stats" :key="stat.label" class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">{{ stat.label }}</dt>
              <dd class="mt-1 text-xl font-semibold">{{ stat.value }}</dd>
            </div>
          </dl>
        </header>

        <section class="mt-6 grid gap-4 lg:grid-cols-2">
          <div class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-950">
            <p class="text-[10px] font-bold tracking-[0.2em] text-amber-700">RELEASE STATE</p>
            <p class="mt-2 font-semibold">
              繁體中文詞義 {{ reader.glossProgress.glossed }}／{{ reader.glossProgress.target }} 詞
              <span v-if="reader.glossProgress.complete">（已補完）</span>
            </p>
            <p class="mt-2 text-amber-900/80">{{ print.note }}</p>
          </div>

          <div class="rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 text-sm leading-6 text-stone-600">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">體例與來源</p>
            <ul class="mt-2 list-disc space-y-1 pl-5">
              <li v-for="line in reader.textPolicy" :key="line" class="break-words">{{ line }}</li>
            </ul>
          </div>
        </section>

        <section v-for="volume in reader.volumes" :key="volume.volume" class="mt-8">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="font-serif text-2xl font-semibold">{{ volume.label }}</h2>
            <p class="text-xs text-stone-500">{{ volume.register }}・{{ volume.lessons.length }} 課</p>
          </div>
          <ul class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="lesson in volume.lessons" :key="lesson.key">
              <NuxtLink
                :to="lesson.href"
                class="group block h-full rounded-2xl border border-stone-300 bg-[#fffdf7] px-5 py-4 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-500 hover:shadow-md"
              >
                <div class="flex items-center justify-between gap-3">
                  <span class="font-mono text-xs font-semibold text-emerald-800">{{ String(lesson.lesson).padStart(2, "0") }}</span>
                  <span class="truncate text-[11px] text-stone-400">{{ lesson.orthography }}</span>
                </div>
                <h3 class="mt-2 line-clamp-2 font-serif text-base font-semibold leading-6 break-words">{{ lesson.title }}</h3>
                <p class="mt-1 truncate text-xs text-stone-500">{{ lesson.author }}</p>
                <dl class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-stone-500">
                  <div><dt class="inline">生詞 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.vocabularyCount }}</dd></div>
                  <div><dt class="inline">練習 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.exerciseCount }}</dd></div>
                  <div><dt class="inline">背誦 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.memoryUnitCount }}</dd></div>
                  <div><dt class="inline">讀文 </dt><dd class="inline font-semibold text-stone-700">{{ lesson.chars }} 字</dd></div>
                </dl>
                <p class="mt-2 truncate text-[11px] text-stone-400">{{ lesson.extent }}</p>
              </NuxtLink>
            </li>
          </ul>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ meta: [{ name: "robots", content: "noindex, nofollow, noarchive" }] });

interface LessonSummary {
  volume: number;
  lesson: number;
  key: string;
  title: string;
  author: string;
  orthography: string;
  extent: string;
  chars: number;
  vocabularyCount: number;
  memoryUnitCount: number;
  exerciseCount: number;
  glossedCount: number;
  href: string;
}
interface Reader {
  title: string;
  subtitle: string;
  counts: { volumes: number; lessons: number; vocabulary: number; exercises: number; chars: number };
  glossProgress: { glossed: number; target: number; complete: boolean };
  textPolicy: string[];
  volumes: { volume: number; label: string; register: string; lessons: LessonSummary[] }[];
}

const reader = ref<Reader | null>(null);
const pending = ref(true);
const error = ref("");

// 紙本分冊只是印刷單位，寫在這裡是為了讓線上讀者知道哪一課印在哪一冊；
// 課次編號兩邊一致，不因分冊而改。
const print = {
  note: "紙本分四冊（第一冊 1–30、31–50 課，第二冊 1–32、33–50 課），一冊不超過 500 頁；分冊只是印刷單位，不改變課次。",
};

const stats = computed(() => {
  if (!reader.value) return [];
  const counts = reader.value.counts;
  return [
    { label: "冊數", value: counts.volumes },
    { label: "課數", value: counts.lessons },
    { label: "生詞", value: counts.vocabulary.toLocaleString() },
    { label: "翻譯練習", value: counts.exercises.toLocaleString() },
    { label: "讀文字數", value: counts.chars.toLocaleString() },
  ];
});

onMounted(async () => {
  try {
    reader.value = await $fetch<Reader>("/api/original-readers/ja-lessons");
  } catch (err) {
    error.value = err instanceof Error ? err.message : "載入失敗";
  } finally {
    pending.value = false;
  }
});
</script>
