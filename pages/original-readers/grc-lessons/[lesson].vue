<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader
      :title="lesson ? `第 ${lesson.lesson} 課` : '新約希臘文讀本'"
      :back="{ to: '/original-readers/grc-lessons', label: '50 課總覽' }"
      container-class="max-w-5xl"
    />

    <main class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入這一課…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="lesson">
        <header class="rounded-[2rem] border border-stone-300 bg-[#1b2430] px-6 py-8 text-[#f4efe2] shadow-xl sm:px-9">
          <div class="flex flex-wrap items-center gap-3">
            <span class="rounded-full bg-white/10 px-3 py-1 text-[11px] tracking-wider">第 {{ lesson.lesson }} 課</span>
            <span class="rounded-full bg-white/10 px-3 py-1 text-[11px]">{{ readingLabel }}</span>
            <span v-if="lesson.reading.completeness === 'excerpt'" class="rounded-full bg-amber-300/20 px-3 py-1 text-[11px] text-amber-200">
              節錄・{{ lesson.reading.extent }}
            </span>
          </div>
          <h1 class="mt-4 font-serif text-2xl font-semibold leading-snug break-words sm:text-4xl">{{ lesson.reading.titleZh }}</h1>
          <p class="greek mt-2 break-words text-base text-stone-300">{{ lesson.reading.titleGrc }}</p>
          <p class="mt-4 text-xs text-stone-400">生詞來源：{{ lesson.vocabularySource }}</p>
          <ul v-if="lesson.reading.learningGoals?.length" class="mt-3 flex flex-wrap gap-2">
            <li v-for="goal in lesson.reading.learningGoals" :key="goal" class="rounded-full border border-stone-600 px-3 py-1 text-[11px] text-stone-300">
              {{ goal }}
            </li>
          </ul>
        </header>

        <section class="mt-7">
          <h2 class="font-serif text-xl font-semibold">生詞（{{ lesson.vocabularyCount }}）</h2>
          <div class="mt-3 overflow-x-auto rounded-2xl border border-stone-300 bg-white">
            <table class="w-full min-w-[38rem] text-left text-sm">
              <thead class="bg-stone-100 text-[11px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th class="px-3 py-2">#</th>
                  <th class="px-3 py-2">詞條</th>
                  <th class="px-3 py-2">音譯</th>
                  <th class="px-3 py-2">繁中詞義</th>
                  <th class="px-3 py-2">英文</th>
                  <th class="px-3 py-2">Strong</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="word in lesson.vocabulary" :key="word.id" class="border-t border-stone-200 align-top">
                  <td class="px-3 py-2 text-xs text-stone-400">{{ word.ordinal }}</td>
                  <td class="greek px-3 py-2 text-base font-medium break-words">
                    {{ word.printedEntry }}
                    <span v-if="word.isProperName" class="ml-1 rounded bg-stone-100 px-1.5 py-0.5 text-[10px] text-stone-600">
                      {{ properNameLabel(word.properNameTypes) }}
                    </span>
                  </td>
                  <td class="px-3 py-2 text-xs text-stone-500">{{ word.textbookTransliteration }}</td>
                  <td class="px-3 py-2 break-words">
                    <span v-if="word.glossZh">{{ word.glossZh }}</span>
                    <span v-else class="text-amber-700">待補</span>
                  </td>
                  <td class="px-3 py-2 text-xs text-stone-500 break-words">{{ word.glossEn || "—" }}</td>
                  <td class="px-3 py-2 text-xs text-stone-400">{{ word.strong || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="mt-8">
          <h2 class="font-serif text-xl font-semibold">背誦（2 節）</h2>
          <ul class="mt-3 space-y-3">
            <li v-for="verse in lesson.memoryVerses" :key="verse.ref" class="rounded-2xl border border-stone-300 bg-white p-4">
              <div class="flex flex-wrap items-center gap-2 text-[11px] text-stone-500">
                <span class="rounded-full bg-stone-100 px-2 py-0.5 font-semibold">{{ verse.ref }}</span>
                <span>{{ corpusLabel(verse.corpus) }}</span>
                <span>命中 {{ verse.matchCount }} 個本課生詞</span>
                <span>比對方式：{{ verse.matchMethod === "lemma" ? "詞位" : "字形" }}</span>
                <span v-if="verse.reviewStatus !== 'reviewed'" class="rounded-full bg-amber-100 px-2 py-0.5 text-amber-800">待人工複核</span>
                <button
                  v-if="audio.deviceSupported.value"
                  type="button"
                  class="rounded-full border border-stone-300 px-2 py-0.5 text-[11px] hover:border-stone-500"
                  @click="speak([{ id: verse.ref, sourceText: verse.text }])"
                >朗讀</button>
              </div>
              <p v-if="!verse.tokens?.length" class="greek mt-2 text-lg leading-9 break-words">{{ verse.text }}</p>
              <p v-else class="mt-2 flex flex-wrap items-end gap-x-3 gap-y-2">
                <span v-for="(token, i) in verse.tokens" :key="i" class="inline-flex flex-col items-center">
                  <span class="greek text-lg leading-8">{{ token.word }}{{ token.trailing }}</span>
                  <span class="text-[11px] leading-4 text-stone-500">{{ token.glossZh }}</span>
                </span>
              </p>
              <p v-if="verse.translationZh" class="mt-2 text-sm leading-7 text-stone-700 break-words">{{ verse.translationZh }}</p>
              <p v-else class="mt-2 text-sm text-amber-700">中譯待補</p>
            </li>
          </ul>
        </section>

        <section class="mt-8">
          <h2 class="font-serif text-xl font-semibold">讀文</h2>
          <p class="mt-1 text-xs text-stone-500 break-words">
            {{ lesson.reading.source }}
            <span v-if="lesson.reading.wordCount"> ・{{ lesson.reading.wordCount }} 詞</span>
          </p>
          <div v-if="audio.deviceSupported.value" class="mt-2 flex flex-wrap items-center gap-2">
            <button type="button" class="rounded-full border border-stone-300 px-3 py-1 text-xs hover:border-stone-500" @click="speakReading">朗讀全篇</button>
            <button v-if="audio.playing.value" type="button" class="rounded-full border border-stone-300 px-3 py-1 text-xs hover:border-stone-500" @click="audio.togglePause()">{{ audio.paused.value ? "繼續" : "暫停" }}</button>
            <button v-if="audio.playing.value" type="button" class="rounded-full border border-stone-300 px-3 py-1 text-xs hover:border-stone-500" @click="audio.stop()">停止</button>
            <span class="text-[11px] text-amber-700">{{ audio.warning.value || "裝置語音為現代希臘語讀音，只供定位，不是本讀本採用的 Mounce Erasmian 發音。" }}</span>
          </div>
          <p v-if="lesson.reading.numberingNote" class="mt-1 text-xs text-stone-500 break-words">{{ lesson.reading.numberingNote }}</p>
          <p v-if="lesson.reading.verseNumberingNote" class="mt-1 text-xs text-stone-500 break-words">{{ lesson.reading.verseNumberingNote }}</p>

          <ol class="mt-4 space-y-3">
            <li v-for="segment in readingSegments" :key="segment.key" class="rounded-2xl border border-stone-200 bg-white p-4">
              <p class="text-[11px] font-semibold text-stone-400">{{ segment.label }}</p>
              <p v-if="!segment.tokens.length" class="greek mt-1 text-lg leading-9 break-words">{{ segment.greek }}</p>
              <p v-else class="mt-1 flex flex-wrap items-end gap-x-3 gap-y-2">
                <span v-for="(token, i) in segment.tokens" :key="i" class="inline-flex flex-col items-center">
                  <span class="greek text-lg leading-8">{{ token.word }}{{ token.trailing }}</span>
                  <span class="text-[11px] leading-4 text-stone-500">{{ token.glossZh }}</span>
                </span>
              </p>
              <p v-if="segment.chinese" class="mt-2 text-sm leading-7 text-stone-700 break-words">{{ segment.chinese }}</p>
              <p v-else-if="segment.note" class="mt-2 text-xs text-stone-500">{{ segment.note }}</p>
            </li>
          </ol>

          <p v-if="lesson.reading.absentVerses?.length" class="mt-4 rounded-2xl border border-stone-300 bg-stone-50 p-4 text-xs leading-6 text-stone-600">
            <span class="font-semibold">此版本缺節：</span>
            <span v-for="absent in lesson.reading.absentVerses" :key="absent.ref">{{ absent.ref }}（{{ absent.note }}）</span>
          </p>
        </section>

        <nav class="mt-10 flex items-center justify-between gap-4 text-sm">
          <NuxtLink v-if="lesson.lesson > 1" :to="`/original-readers/grc-lessons/${lesson.lesson - 1}`" class="rounded-full border border-stone-300 px-4 py-2 hover:border-stone-500">← 第 {{ lesson.lesson - 1 }} 課</NuxtLink>
          <span v-else />
          <NuxtLink v-if="lesson.lesson < 50" :to="`/original-readers/grc-lessons/${lesson.lesson + 1}`" class="rounded-full border border-stone-300 px-4 py-2 hover:border-stone-500">第 {{ lesson.lesson + 1 }} 課 →</NuxtLink>
        </nav>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
interface VocabularyEntry {
  id: string; ordinal: number; printedEntry: string; textbookTransliteration: string;
  glossZh: string; glossEn: string; strong: string; isProperName: boolean; properNameTypes: string[];
}
interface MemoryVerse {
  ref: string; corpus: string; matchMethod: string; matchCount: number;
  text: string; translationZh: string; reviewStatus: string; tokens?: Token[];
}
interface Token { word: string; trailing: string; glossZh: string }
interface Segment {
  ref?: string; verse?: number; displayText?: string; sourceText?: string;
  text?: string; translationZh?: string; translationNote?: string;
  tokens?: Token[];
}
interface Reading {
  kind: string; titleZh: string; titleGrc: string; source: string; wordCount: number;
  completeness?: string; extent?: string; corpusLabel?: string; categoryLabel?: string;
  learningGoals?: string[]; verses?: Segment[]; segments?: Segment[];
  absentVerses?: { ref: string; note: string }[];
  numberingNote?: string; verseNumberingNote?: string;
}
interface Lesson {
  lesson: number; id: string; vocabularySource: string; vocabularyCount: number;
  vocabulary: VocabularyEntry[]; memoryVerses: MemoryVerse[]; reading: Reading;
}

const route = useRoute();
const supabase = useSupabaseClient();
// Device speech reads Modern Greek, not the reader's Mounce Erasmian profile,
// so it is offered as orientation only and always carries that warning.  It is
// never presented as the reader's pronunciation track, which stays unrecorded.
const audio = useOriginalReaderAudio();

function speak(segments: { id: string; sourceText: string }[]) {
  audio.playDevice("grc", segments as any);
}

function speakReading() {
  speak(readingSegments.value.map((segment) => ({ id: segment.key, sourceText: segment.greek })));
}
const lesson = ref<Lesson | null>(null);
const pending = ref(true);
const error = ref("");

const readingLabel = computed(
  () => lesson.value?.reading.corpusLabel || lesson.value?.reading.categoryLabel || "",
);

const CORPUS_LABELS: Record<string, string> = {
  "new-testament": "新約",
  septuagint: "七十士譯本",
  deuterocanonical: "次經",
  pseudepigrapha: "偽經",
};
function corpusLabel(corpus: string) {
  return CORPUS_LABELS[corpus] || corpus;
}

const PROPER_NAME_LABELS: Record<string, string> = {
  person: "人名", place: "地名",
  people_or_nation: "民族／國族名", divine_name_or_title: "神名／神聖稱號",
};
function properNameLabel(types: string[]) {
  return types.map((type) => PROPER_NAME_LABELS[type] || type).join("、") || "專名";
}

// Scripture chapters carry verses, patristic readings carry segments; both are
// shown the same way, with whichever reference the source actually has.
const readingSegments = computed(() => {
  const reading = lesson.value?.reading;
  if (!reading) return [];
  const rows = reading.verses || reading.segments || [];
  return rows.map((segment, index) => ({
    key: segment.ref || `${index}`,
    label: segment.ref || (segment.verse ? String(segment.verse) : `${index + 1}`),
    greek: segment.displayText || segment.text || segment.sourceText || "",
    tokens: segment.tokens || [],
    chinese: segment.translationZh || "",
    note: segment.translationNote || "",
  }));
});

async function load() {
  pending.value = true;
  error.value = "";
  lesson.value = null;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    const number = String(route.params.lesson);
    lesson.value = await $fetch<Lesson>(`/api/original-readers/grc-lessons/${number}`, {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    useHead({ title: `第${lesson.value.lesson}課・${lesson.value.reading.titleZh} — 希臘文讀本` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
}

onMounted(load);
watch(() => route.params.lesson, load);
</script>

<style scoped>
.greek {
  font-family: "SBL Greek", "New Athena Unicode", "Gentium Plus", "Noto Serif", serif;
  text-wrap: pretty;
}
</style>
