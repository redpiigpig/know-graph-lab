<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="希伯來文50課讀本" :back="{ to: '/original-readers/hbo-lessons', label: '50課總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-4 py-7 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入本課真實主資料…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="lessonData">
        <header class="rounded-[2rem] border border-stone-300 bg-[#fffdf7] p-6 shadow-sm sm:p-8">
          <div class="flex flex-col justify-between gap-6 md:flex-row md:items-start">
            <div>
              <p class="text-xs font-bold tracking-[0.22em] text-stone-400">LESSON {{ String(lessonData.lesson).padStart(2, "0") }} · {{ trackLabel }}</p>
              <h1 class="mt-3 font-serif text-3xl font-semibold sm:text-4xl">{{ lessonData.titleZh }}</h1>
              <p class="hebrew-title mt-2 text-2xl text-stone-600" dir="rtl" lang="hbo">{{ lessonData.titleHe }}</p>
              <p class="mt-2 text-xs text-stone-500">{{ lessonData.ref }}<template v-if="lessonData.difficulty"> · 難度 {{ lessonData.difficulty }}</template> · {{ lessonData.readingSegmentCount }}段</p>
            </div>
            <button type="button" class="shrink-0 rounded-full border px-4 py-2 text-xs font-semibold" :class="completed ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-stone-300 bg-white text-stone-700'" @click="toggleComplete">
              {{ completed ? "✓ 已讀完本課" : "標記已讀" }}
            </button>
          </div>

          <div class="mt-6 grid gap-3 border-t border-stone-200 pt-5 md:grid-cols-[1fr_auto] md:items-center">
            <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-6 text-amber-950">
              <strong>{{ lessonData.audioStatus.label }}</strong>
              <span class="ml-2">{{ lessonData.audioStatus.policy }}</span>
            </div>
            <a
              v-for="reference in lessonData.pronunciationReferences"
              :key="reference.id"
              :href="reference.url"
              target="_blank"
              rel="noopener noreferrer"
              class="rounded-full border border-stone-300 bg-white px-4 py-2 text-center text-xs font-semibold text-stone-700 hover:border-stone-500"
            >{{ reference.label }} ↗</a>
          </div>
        </header>

        <section class="mt-6 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
          <header class="flex flex-col gap-2 border-b border-stone-200 p-5 sm:flex-row sm:items-end sm:justify-between sm:p-7">
            <div>
              <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">VOCABULARY · BBH ORDER</p>
              <h2 class="mt-1 font-serif text-2xl font-semibold">本課{{ lessonData.vocabulary.length }}詞</h2>
              <p class="mt-1 text-xs leading-5 text-stone-500">完整母音、BBH課本式音標（學術轉寫，非 IPA）、繁中義與專名類型。</p>
            </div>
            <span class="w-fit rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-800">{{ lessonData.properNameCount }} 個專名／神名</span>
          </header>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[64rem] border-collapse text-left text-sm">
              <thead class="bg-stone-100/80 text-[11px] font-semibold tracking-wider text-stone-500">
                <tr>
                  <th class="w-16 px-4 py-3">序</th>
                  <th class="w-56 px-4 py-3 text-right">附點詞形</th>
                  <th class="w-52 px-4 py-3">BBH音標</th>
                  <th class="min-w-64 px-4 py-3">繁中義</th>
                  <th class="w-44 px-4 py-3">詞類／專名</th>
                  <th class="w-40 px-4 py-3">來源</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-stone-200">
                <tr v-for="word in lessonData.vocabulary" :key="word.ordinal" class="align-top hover:bg-amber-50/40">
                  <td class="px-4 py-4 font-mono text-xs text-stone-400">{{ word.ordinal }}</td>
                  <td class="px-4 py-3 text-right">
                    <p class="hebrew-word text-2xl" dir="rtl" lang="hbo">{{ word.pointed }}</p>
                    <p class="mt-1 text-[11px] text-stone-400" dir="ltr">{{ strongLabel(word) }}</p>
                  </td>
                  <td class="px-4 py-4 font-medium text-stone-800" dir="ltr">
                    {{ word.textbookTransliteration }}
                    <p class="mt-1 text-[10px] font-normal text-stone-400">{{ word.transliterationSystem }}</p>
                  </td>
                  <td class="px-4 py-4 leading-6 text-stone-700">{{ word.glossZh }}</td>
                  <td class="px-4 py-4">
                    <p class="text-xs text-stone-600">{{ partOfSpeechLabel(word.partOfSpeech) }}</p>
                    <span v-if="word.isProperName" class="mt-2 inline-flex rounded-full bg-violet-100 px-2.5 py-1 text-[11px] text-violet-800">{{ properNameLabel(word.properNameTypes) }}</span>
                  </td>
                  <td class="px-4 py-4 text-[11px] leading-5 text-stone-500">{{ vocabularySourceLabel(word) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="mt-6 rounded-3xl border border-stone-300 bg-white/80 p-5 shadow-sm sm:p-7">
          <header class="mb-4">
            <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">MEMORY · 2 VERSES</p>
            <h2 class="mt-1 font-serif text-2xl font-semibold">本課背誦經文</h2>
          </header>
          <div class="grid gap-4 lg:grid-cols-2">
            <article v-for="verse in lessonData.memoryVerses" :key="verse.ref" class="rounded-2xl border border-stone-200 bg-[#fffdf7] p-5">
              <div class="flex items-center justify-between gap-3">
                <span class="font-mono text-xs font-semibold text-stone-500">{{ verse.ref }}</span>
                <span class="text-[11px] text-stone-400">第{{ verse.slot }}節</span>
              </div>
              <HebrewInterlinear class="mt-4" :tokens="verse.tokens" :sense="verse.translationZh" :fallback-text="verse.text" />
              <p class="mt-3 text-[11px] leading-5 text-stone-400">本課新詞命中 {{ verse.matchedCount }}；累積詞彙覆蓋 {{ percent(verse.knownCoverage) }}</p>
            </article>
          </div>
        </section>

        <section class="mt-6 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
          <header class="border-b border-stone-200 p-5 sm:p-7">
            <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
              <div>
                <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">FULL PRIMARY READING</p>
                <h2 class="mt-1 font-serif text-2xl font-semibold">{{ lessonData.reading.titleZh }}</h2>
                <p class="hebrew-title mt-1 text-xl text-stone-600" dir="rtl" lang="hbo">{{ lessonData.reading.titleHe }}</p>
                <p class="mt-2 text-xs text-stone-500">{{ lessonData.reading.ref }} · {{ lessonData.reading.segmentCount }}段<template v-if="lessonData.reading.wordCount"> · {{ lessonData.reading.wordCount }}詞</template></p>
              </div>
              <span class="w-fit rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">全文附點已核</span>
            </div>
            <div class="mt-5 flex flex-wrap items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <button
                type="button"
                class="rounded-full bg-amber-700 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-800 disabled:opacity-40"
                :disabled="!audio.deviceSupported.value"
                @click="toggleReading"
              >{{ audio.playing.value ? "■ 停止朗讀" : "▶ 朗讀全文" }}</button>
              <button
                v-if="audio.playing.value"
                type="button"
                class="rounded-full border border-amber-300 bg-white px-4 py-2 text-sm font-semibold text-amber-900"
                @click="audio.togglePause()"
              >{{ audio.paused.value ? "▶ 繼續" : "❚❚ 暫停" }}</button>
              <p class="text-xs leading-5 text-amber-950">
                <strong>現代以色列語音</strong>，僅供聽出斷句與節奏；發音一律以 BBH2 課本音標為準，勿以此語音為發音範本。
              </p>
            </div>

            <div v-if="lessonData.reading.summaryZh" class="mt-5 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm leading-7 text-sky-950">
              <strong>內容摘要（不是逐段翻譯）：</strong>{{ lessonData.reading.summaryZh }}
            </div>
          </header>

          <article class="divide-y divide-stone-200">
            <section
              v-for="segment in lessonData.reading.segments"
              :id="segment.id"
              :key="segment.id"
              class="p-5 transition-colors sm:p-7"
              :class="audio.currentSegmentId.value === segment.id ? 'bg-amber-50' : ''"
            >
              <p class="mb-3 font-mono text-[11px] text-stone-400">{{ segment.ref }}</p>
              <HebrewInterlinear
                :tokens="segment.tokens"
                :sense="segment.translationContinuation ? '' : segment.translationZh"
                :fallback-text="segment.text"
              />
              <p v-if="segment.translationContinuation" class="mt-4 border-r-2 border-stone-200 pr-4 text-xs leading-6 text-stone-500">RCUV {{ segment.translationRange }} 合併節；譯文見上一節。</p>
            </section>
          </article>

          <footer class="border-t border-stone-200 bg-stone-50 px-5 py-4 text-xs leading-6 text-stone-500 sm:px-7">
            <strong>來源：</strong>{{ lessonData.reading.source.edition }}<template v-if="lessonData.reading.source.version"> · {{ lessonData.reading.source.version }}</template>。{{ lessonData.reading.source.license }}
            <a :href="lessonData.reading.source.sourceUrl" target="_blank" rel="noopener noreferrer" class="ml-2 font-semibold text-sky-800 underline decoration-sky-300 underline-offset-2">來源頁 ↗</a>
            <template v-if="lessonData.track === 'scripture'"><br><strong>繁中對照：</strong>{{ lessonData.chineseBible.titleZh }} · {{ lessonData.chineseBible.variant }}（私人授權使用）</template>
          </footer>
        </section>

        <nav class="mt-7 grid grid-cols-3 items-center gap-3 text-sm">
          <NuxtLink v-if="lessonData.previousLesson" :to="`/original-readers/hbo-lessons/${lessonData.previousLesson}`" class="justify-self-start rounded-full border border-stone-300 bg-white px-4 py-2 hover:border-stone-500">← 第{{ lessonData.previousLesson }}課</NuxtLink><span v-else />
          <NuxtLink to="/original-readers/hbo-lessons/haggadah" class="justify-self-center text-center text-xs font-semibold text-stone-600 underline decoration-stone-300 underline-offset-4">完整 Haggadah</NuxtLink>
          <NuxtLink v-if="lessonData.nextLesson" :to="`/original-readers/hbo-lessons/${lessonData.nextLesson}`" class="justify-self-end rounded-full border border-stone-300 bg-white px-4 py-2 text-right hover:border-stone-500">第{{ lessonData.nextLesson }}課 →</NuxtLink>
        </nav>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }] });

interface AudioStatus { status: "not_recorded"; label: string; recordedTrackCount: 0; policy: string }
interface PronunciationReference { id: string; label: string; description: string; url: string }
interface VocabularyEntry {
  ordinal: number;
  lessonSlot: number;
  pointed: string;
  textbookTransliteration: string;
  transliterationSystem: string;
  glossZh: string;
  sourceType: string;
  sourceChapter: number | null;
  frequency: number | null;
  strong: string;
  strongs: string[];
  partOfSpeech: string;
  isProperName: boolean;
  properNameTypes: string[];
}
interface InterlinearToken { word: string; trailing: string; glossZh: string }
interface MemoryVerse {
  slot: number;
  ref: string;
  text: string;
  tokens: InterlinearToken[];
  translationZh: string;
  matchedCount: number;
  knownCoverage: number;
}
interface ReadingSegment { id: string; ordinal: number; ref: string; text: string; sourceText: string; translationZh: string; tokens: InterlinearToken[]; translationContinuation?: boolean; translationRange?: string }
interface ChineseBibleSource { versionCode: string; titleZh: string; variant: string; publisher: string; sourceUrl: string; rights: string }
interface Reading {
  kind: "scripture_chapter" | "prayer_article";
  titleZh: string;
  titleHe: string;
  ref: string;
  summaryZh: string;
  segmentCount: number;
  wordCount: number | null;
  source: { edition: string; version?: string; sourceUrl: string; license: string };
  segments: ReadingSegment[];
}
interface LessonDetail {
  lesson: number;
  track: "scripture" | "prayer_article";
  titleZh: string;
  titleHe: string;
  ref: string;
  difficulty: number | null;
  properNameCount: number;
  readingSegmentCount: number;
  audioStatus: AudioStatus;
  chineseBible: ChineseBibleSource;
  pronunciationReferences: PronunciationReference[];
  vocabulary: VocabularyEntry[];
  memoryVerses: MemoryVerse[];
  vocabularyCount: number;
  reading: Reading;
  previousLesson: number | null;
  nextLesson: number | null;
}

const route = useRoute();
const supabase = useSupabaseClient();
const audio = useOriginalReaderAudio();

function toggleReading() {
  if (audio.playing.value) {
    audio.stop();
    return;
  }
  const segments = (lessonData.value?.reading.segments || []).map((segment) => ({
    id: segment.id,
    ordinal: segment.ordinal,
    ref: segment.ref,
    // Read the printed pointed text, not the source layer: the reader hears
    // exactly the line it is looking at.
    sourceText: segment.text,
    translationZh: segment.translationZh,
  }));
  audio.playDevice("hbo", segments as never);
}
const lessonData = ref<LessonDetail | null>(null);
const pending = ref(true);
const error = ref("");
const completed = ref(false);
const trackLabel = computed(() => lessonData.value?.track === "scripture" ? "完整聖經章" : "禱文／拉比文章");

function progressKey(lesson: number) {
  return `hbo-full-reader-progress:${lesson}`;
}
function toggleComplete() {
  if (!lessonData.value) return;
  completed.value = !completed.value;
  try { localStorage.setItem(progressKey(lessonData.value.lesson), completed.value ? "complete" : ""); } catch { /* private mode */ }
}
function strongLabel(word: VocabularyEntry) {
  return word.strongs?.length ? word.strongs.join(" / ") : word.strong || "—";
}
function properNameLabel(types: string[]) {
  const labels: Record<string, string> = {
    divine_name_or_title: "神名／神聖稱號",
    people_or_nation: "民族／國族名",
    person: "人名",
    place: "地名",
    proper_name: "其他專名",
  };
  return types.map((type) => labels[type] || type).join("、") || "專名";
}
function partOfSpeechLabel(value: string) {
  const labels: Record<string, string> = {
    noun: "名詞", verb: "動詞", adjective: "形容詞", adverb: "副詞",
    preposition: "介系詞", conjunction: "連接詞", pronoun: "代名詞",
    particle: "助詞", proper_noun: "專有名詞",
  };
  return labels[value] || value;
}
function vocabularySourceLabel(word: VocabularyEntry) {
  if (word.sourceType === "bbh2_order") return `BBH2 第${word.sourceChapter || "—"}章序`;
  if (word.sourceType === "reader_frequency_extension") return `WLC／OSHB 詞頻延伸${word.frequency ? ` · ${word.frequency}次` : ""}`;
  return word.sourceType.replaceAll("_", " ");
}
function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

async function loadLesson() {
  pending.value = true;
  error.value = "";
  lessonData.value = null;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    const lesson = String(route.params.lesson);
    lessonData.value = await $fetch<LessonDetail>(`/api/original-readers/hbo-lessons/${lesson}`, {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    try { completed.value = localStorage.getItem(progressKey(lessonData.value.lesson)) === "complete"; } catch { completed.value = false; }
    useHead({ title: `第${lessonData.value.lesson}課・${lessonData.value.titleZh} — 希伯來文讀本` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
}

onMounted(loadLesson);
watch(() => route.params.lesson, () => {
  audio.stop();
  loadLesson();
});
</script>

<style scoped>
.hebrew-title,
.hebrew-word,
.hebrew-reading {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
}
.hebrew-title,
.hebrew-word { line-height: 1.9; }
.hebrew-reading {
  font-size: clamp(1.35rem, 2.4vw, 1.75rem);
  line-height: 2.15;
  text-wrap: pretty;
}
</style>
