<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader title="日文宗教學讀本" :back="{ to: '/original-readers/ja-lessons', label: '課次總覽' }" container-class="max-w-5xl" />

    <main class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入本課…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="lesson">
        <header class="rounded-[2rem] border border-stone-300 bg-[#fffdf7] px-6 py-7 shadow-sm sm:px-9">
          <p class="text-[11px] font-bold tracking-[0.24em] text-emerald-800">
            {{ lesson.volume === 1 ? "第一冊" : "第二冊" }}　第 {{ String(lesson.lesson).padStart(2, "0") }} 課
          </p>
          <h1 class="mt-2 font-serif text-3xl font-semibold leading-tight break-words">{{ lesson.title }}</h1>
          <p class="mt-2 text-sm text-stone-600 break-words">
            {{ lesson.author }}　{{ lesson.extent }}　{{ lesson.orthography }}　{{ lesson.chars }} 字
          </p>
          <a
            v-if="lesson.sourceUrl"
            :href="lesson.sourceUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-3 inline-block text-xs text-stone-500 underline decoration-dotted underline-offset-4 hover:text-stone-800 break-all"
          >取源 ↗</a>
        </header>

        <section class="mt-7">
          <h2 class="font-serif text-xl font-semibold">本課生詞（{{ lesson.vocabulary.length }}）</h2>
          <div class="mt-3 overflow-x-auto rounded-2xl border border-stone-300 bg-[#fffdf7]">
            <table class="w-full min-w-[40rem] text-left text-sm">
              <thead class="bg-stone-100 text-xs text-stone-500">
                <tr>
                  <th class="px-3 py-2 font-semibold">#</th>
                  <th class="px-4 py-2 font-semibold">詞</th>
                  <th class="px-4 py-2 font-semibold">假名</th>
                  <th class="px-3 py-2 font-semibold">詞類</th>
                  <th class="px-4 py-2 font-semibold">繁體中文</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="word in lesson.vocabulary" :key="word.ordinal" class="border-t border-stone-200 align-top">
                  <td class="px-3 py-2 text-xs text-stone-400">{{ word.ordinal }}</td>
                  <td class="px-4 py-2 font-serif text-base break-words">{{ word.kanji || word.kana }}</td>
                  <td class="px-4 py-2 text-stone-600 break-words">{{ word.kana }}</td>
                  <td class="px-3 py-2 text-xs text-stone-500">{{ word.pos || "—" }}</td>
                  <td class="px-4 py-2 break-words">{{ word.glossZh || "〔待補〕" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="lesson.exercises" class="mt-8">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="font-serif text-xl font-semibold">翻譯練習（{{ lesson.exercises.itemCount }} 題）</h2>
            <span class="rounded-full bg-stone-100 px-3 py-1 text-[11px] text-stone-500">
              引用 {{ lesson.exercises.quotedCount }}／自撰 {{ lesson.exercises.composedCount }}
            </span>
          </div>
          <p class="mt-2 text-xs leading-6 text-stone-500 break-words">
            把每一句譯成繁體中文。題目只印日文——標出處的是引用題，出處是青空文庫或文語訳聖書；標「自撰」的句子都經過語料驗證。
          </p>
          <p class="mt-1 text-xs leading-6 text-stone-500 break-words">
            本課
            <template v-if="lesson.exercises.coverage.practised === lesson.exercises.coverage.lessonWords">
              {{ lesson.exercises.coverage.lessonWords }} 詞全數入題
            </template>
            <template v-else>
              {{ lesson.exercises.coverage.practised }}／{{ lesson.exercises.coverage.lessonWords }} 詞入題
            </template>
            <template v-if="lesson.exercises.note">；{{ lesson.exercises.note }}</template>。
          </p>
          <ol class="mt-3 grid gap-3 lg:grid-cols-2">
            <li
              v-for="item in lesson.exercises.items"
              :key="item.no"
              class="rounded-2xl border border-stone-300 bg-white/80 px-5 py-4"
            >
              <div class="flex items-baseline justify-between gap-3">
                <span class="font-mono text-xs font-semibold text-emerald-800">{{ String(item.no).padStart(2, "0") }}</span>
                <span v-if="item.kind === 'quoted'" class="text-[11px] text-stone-500 break-words text-right">{{ item.ref }}</span>
                <span v-else class="shrink-0 rounded-full bg-stone-100 px-2 py-0.5 text-[11px] text-stone-500">自撰</span>
              </div>
              <p class="mt-2 font-serif text-[17px] leading-8 break-words">{{ item.text }}</p>
            </li>
          </ol>
          <p class="mt-3 text-[11px] leading-5 text-stone-400">中譯不附在題旁；引用題的出處可據以查對原作。</p>
        </section>

        <section v-if="lesson.memoryUnits.length" class="mt-8">
          <h2 class="font-serif text-xl font-semibold">背誦句（{{ lesson.memoryUnits.length }}）</h2>
          <ul class="mt-3 space-y-3">
            <li v-for="unit in lesson.memoryUnits" :key="unit.id" class="rounded-2xl border border-stone-300 bg-white/80 px-5 py-4">
              <p v-if="unit.label" class="text-[11px] font-semibold text-stone-400">{{ unit.label }}</p>
              <p v-if="!unit.tokens.length" class="mt-1 font-serif text-lg leading-9 break-words">{{ unit.text }}</p>
              <p v-else class="mt-1 flex flex-wrap items-end gap-x-3 gap-y-2">
                <span v-for="(token, i) in unit.tokens" :key="i" class="inline-flex flex-col items-center">
                  <span class="font-serif text-lg leading-8">{{ token.word }}{{ token.trailing }}</span>
                  <span class="text-[11px] leading-4 text-stone-500">{{ token.glossZh }}</span>
                </span>
              </p>
              <p v-if="unit.senseZh" class="mt-2 text-sm leading-7 text-stone-700 break-words">{{ unit.senseZh }}</p>
              <p v-else class="mt-2 text-sm text-amber-700">整句中譯待補</p>
            </li>
          </ul>
        </section>

        <section class="mt-8">
          <h2 class="font-serif text-xl font-semibold">讀本</h2>
          <div class="mt-3 space-y-4">
            <div v-for="unit in lesson.reading" :key="unit.id" class="rounded-2xl border border-stone-300 bg-[#fffdf7] px-5 py-4">
              <p v-if="unit.label" class="text-[11px] font-semibold text-stone-400">{{ unit.label }}</p>
              <p v-if="!unit.tokens.length" class="mt-1 font-serif text-lg leading-9 break-words">{{ unit.text }}</p>
              <p v-else class="mt-1 flex flex-wrap items-end gap-x-3 gap-y-2">
                <span v-for="(token, i) in unit.tokens" :key="i" class="inline-flex flex-col items-center">
                  <span class="font-serif text-lg leading-8">{{ token.word }}{{ token.trailing }}</span>
                  <span class="text-[11px] leading-4 text-stone-500">{{ token.glossZh }}</span>
                </span>
              </p>
              <p v-if="unit.senseZh" class="mt-2 text-sm leading-7 text-stone-700 break-words">{{ unit.senseZh }}</p>
              <p v-else class="mt-2 text-sm text-amber-700">整句中譯待補</p>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ meta: [{ name: "robots", content: "noindex, nofollow, noarchive" }] });

interface Token { word: string; trailing: string; glossZh: string }
interface Unit { id: string; label: string; text: string; senseZh: string; tokens: Token[] }
interface ExerciseItem {
  no: number; kind: "quoted" | "composed"; text: string; ref: string | null;
  targetWords: { ordinal: number; headword: string }[];
}
interface Exercises {
  itemCount: number; quotedCount: number; composedCount: number; note: string;
  coverage: { lessonWords: number; practised: number; notAttested: number };
  items: ExerciseItem[];
}
interface Word {
  ordinal: number; kanji: string; kana: string; pos: string; glossZh: string;
}
interface Lesson {
  volume: number; lesson: number; key: string; title: string; author: string;
  orthography: string; extent: string; sourceUrl: string; chars: number;
  vocabulary: Word[]; memoryUnits: Unit[]; exercises?: Exercises; reading: Unit[];
}

const route = useRoute();
const lesson = ref<Lesson | null>(null);
const pending = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    lesson.value = await $fetch<Lesson>(
      `/api/original-readers/ja-lessons/${route.params.lesson}`,
    );
  } catch (err) {
    error.value = err instanceof Error ? err.message : "載入失敗";
  } finally {
    pending.value = false;
  }
});
</script>
