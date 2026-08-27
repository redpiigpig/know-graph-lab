<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="完整逾越節禮文" :back="{ to: '/original-readers/hbo-lessons', label: '讀本目錄' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-4 py-7 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入完整十五步禮文…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="haggadah">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-9 text-[#f7f0df] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-amber-300">PRIVATE APPENDIX · COMPLETE 15-STEP ORDER</p>
          <h1 class="mt-3 font-serif text-3xl font-semibold sm:text-5xl">{{ haggadah.titleZh }}</h1>
          <p class="hebrew-title mt-2 text-3xl text-stone-200" dir="rtl" lang="hbo">{{ haggadah.titleHe }}</p>
          <div class="mt-6 flex flex-wrap gap-2 text-xs">
            <span class="rounded-full border border-stone-500 px-3 py-1.5">{{ haggadah.stepCount }}步</span>
            <span class="rounded-full border border-stone-500 px-3 py-1.5">{{ haggadah.segmentCount }}段完整正文</span>
            <span class="rounded-full border border-emerald-700 bg-emerald-950/40 px-3 py-1.5 text-emerald-200">全文附點已核</span>
          </div>
        </header>

        <section class="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
          <div class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-xs leading-6 text-amber-950">
            <strong>{{ haggadah.audioStatus.label }}</strong>
            <p class="mt-1">{{ haggadah.audioStatus.policy }}</p>
            <a v-for="reference in haggadah.pronunciationReferences" :key="reference.id" :href="reference.url" target="_blank" rel="noopener noreferrer" class="mt-2 inline-flex font-semibold underline decoration-amber-400 underline-offset-4">{{ reference.label }} ↗</a>
          </div>
          <div class="rounded-3xl border border-stone-300 bg-white p-5 text-xs leading-6 text-stone-600">
            <p class="font-semibold text-stone-900">正文來源</p>
            <p class="mt-1">{{ haggadah.source.edition }}</p>
            <p class="mt-1">{{ haggadah.source.license }} · 私人授權已確認</p>
            <a :href="haggadah.source.sourceUrl" target="_blank" rel="noopener noreferrer" class="mt-2 inline-flex font-semibold text-sky-800 underline decoration-sky-300 underline-offset-4">資料來源 ↗</a>
          </div>
        </section>

        <nav class="mt-6 rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm" aria-label="Haggadah十五步">
          <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">FIFTEEN STEPS</p>
          <ol class="mt-3 grid gap-2 sm:grid-cols-3 lg:grid-cols-5">
            <li v-for="step in haggadah.steps" :key="step.key">
              <a :href="`#step-${step.ordinal}`" class="flex h-full items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 transition hover:border-amber-300 hover:bg-amber-50">
                <span class="font-mono text-[10px] text-stone-400">{{ String(step.ordinal).padStart(2, "0") }}</span>
                <span>
                  <strong class="block text-xs">{{ step.titleZh }}</strong>
                  <span class="hebrew-title block text-sm text-stone-500" dir="rtl" lang="hbo">{{ step.titleHe }}</span>
                </span>
              </a>
            </li>
          </ol>
        </nav>

        <p class="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-6 text-amber-950">
          每一步可單獨朗讀。使用的是<strong>裝置的現代以色列語音</strong>，僅供聽出斷句與節奏；發音一律以 BBH2 課本音標為準，勿以此語音為發音範本。
        </p>

        <article class="mt-6 space-y-6">
          <section v-for="step in haggadah.steps" :id="`step-${step.ordinal}`" :key="step.key" class="scroll-mt-5 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
            <header class="border-b border-stone-200 bg-stone-50 px-5 py-5 sm:px-7">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="font-mono text-[11px] text-stone-400">STEP {{ String(step.ordinal).padStart(2, "0") }} · {{ step.key }}</p>
                  <h2 class="mt-1 font-serif text-2xl font-semibold">{{ step.titleZh }}</h2>
                  <p class="hebrew-title mt-1 text-2xl text-stone-600" dir="rtl" lang="hbo">{{ step.titleHe }}</p>
                </div>
                <div class="flex shrink-0 items-center gap-2">
                  <button
                    type="button"
                    class="rounded-full bg-amber-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-800 disabled:opacity-40"
                    :disabled="!audio.deviceSupported.value"
                    @click="toggleStep(step)"
                  >{{ readingStep === step.key ? "■ 停止" : "▶ 朗讀本步" }}</button>
                  <span class="rounded-full bg-stone-200 px-2.5 py-1 text-[11px] text-stone-600">{{ step.segments.length }}段</span>
                </div>
              </div>
            </header>

            <div class="divide-y divide-stone-200">
              <section
                v-for="segment in step.segments"
                :id="segment.id"
                :key="segment.id"
                class="p-5 transition-colors sm:p-7"
                :class="audio.currentSegmentId.value === segment.id ? 'bg-amber-50' : ''"
              >
                <p class="mb-3 font-mono text-[10px] text-stone-400">{{ segment.ref }}</p>
                <HebrewInterlinear :tokens="segment.tokens" :sense="segment.translationZh" :fallback-text="segment.text" />
              </section>
            </div>
            <a href="#top" class="block border-t border-stone-200 bg-stone-50 px-5 py-3 text-right text-[11px] font-semibold text-stone-500 hover:text-stone-900 sm:px-7">回十五步目錄 ↑</a>
          </section>
        </article>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({
  title: "完整逾越節 Haggadah — 希伯來文私人讀本",
  meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }],
  bodyAttrs: { id: "top" },
});

interface AudioStatus { status: "not_recorded"; label: string; recordedTrackCount: 0; policy: string }
interface PronunciationReference { id: string; label: string; description: string; url: string }
interface InterlinearToken { word: string; trailing: string; glossZh: string }
interface Segment { id: string; ordinal: number; ref: string; text: string; sourceText: string; translationZh: string; tokens: InterlinearToken[] }
interface Step {
  ordinal: number;
  key: string;
  titleZh: string;
  titleHe: string;
  ref: string;
  text: string;
  sourceText: string;
  pointingStatus: string;
  segments: Segment[];
}
interface Haggadah {
  titleZh: string;
  titleHe: string;
  ref: string;
  stepCount: number;
  segmentCount: number;
  pointingStatus: string;
  source: { edition: string; sourceUrl: string; versionSource: string; license: string; privateAuthorization: string };
  audioStatus: AudioStatus;
  pronunciationReferences: PronunciationReference[];
  steps: Step[];
}

const supabase = useSupabaseClient();
const audio = useOriginalReaderAudio();
const readingStep = ref("");

function toggleStep(step: Step) {
  if (readingStep.value === step.key) {
    audio.stop();
    readingStep.value = "";
    return;
  }
  readingStep.value = step.key;
  audio.playDevice(
    "hbo",
    step.segments.map((segment) => ({
      id: segment.id,
      ordinal: segment.ordinal,
      ref: segment.ref,
      sourceText: segment.text,
      translationZh: segment.translationZh,
    })) as never,
  );
}

watch(() => audio.playing.value, (playing) => {
  if (!playing) readingStep.value = "";
});
const haggadah = ref<Haggadah | null>(null);
const pending = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    haggadah.value = await $fetch<Haggadah>("/api/original-readers/hbo-lessons/haggadah", {
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
.hebrew-title,
.hebrew-reading {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
}
.hebrew-title { line-height: 1.9; }
.hebrew-reading {
  font-size: clamp(1.3rem, 2.3vw, 1.7rem);
  line-height: 2.15;
  text-wrap: pretty;
}
</style>
