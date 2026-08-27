<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader
      :title="lesson ? `第 ${lesson.lesson} 課` : '教會拉丁文讀本'"
      :back="{ to: '/original-readers/lat-lessons', label: '讀本目錄' }"
      container-class="max-w-4xl"
    />

    <main class="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入本課…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="lesson">
        <header class="rounded-3xl border border-stone-300 bg-[#241d18] px-6 py-7 text-[#f4efe2]">
          <p class="text-[11px] font-semibold tracking-[0.24em] text-amber-300">
            {{ lesson.volume === 1 ? "上冊 · 武加大譯本" : "下冊 · 從教父到教廷" }}　第 {{ lesson.lesson }} 課
          </p>
          <h1 class="mt-2 font-serif text-2xl font-semibold leading-snug break-words sm:text-3xl">{{ lesson.title || "（無讀本）" }}</h1>
          <p v-if="lesson.note" class="mt-2 text-xs leading-6 text-stone-300 break-words">{{ lesson.note }}</p>
        </header>

        <section class="mt-6">
          <h2 class="font-serif text-xl font-semibold">本課生詞（{{ lesson.vocabulary.length }}）</h2>
          <div class="mt-3 overflow-x-auto rounded-2xl border border-stone-300 bg-white/80">
            <table class="w-full min-w-[38rem] border-collapse text-sm">
              <thead class="bg-stone-100 text-left text-[11px] tracking-widest text-stone-500">
                <tr>
                  <th class="px-3 py-2 font-semibold">#</th>
                  <th class="px-4 py-2 font-semibold">詞條</th>
                  <th class="px-3 py-2 font-semibold">詞類</th>
                  <th class="px-4 py-2 font-semibold">繁中詞義</th>
                  <th class="px-3 py-2 font-semibold">英文</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(word, index) in lesson.vocabulary" :key="word.headword" class="border-t border-stone-200 align-top">
                  <td class="px-3 py-2 text-xs text-stone-400">{{ index + 1 }}</td>
                  <td class="px-4 py-2 font-serif break-words">
                    <button
                      v-if="audio.deviceSupported.value"
                      type="button"
                      class="mr-1 align-middle text-stone-400 transition hover:text-stone-800"
                      :aria-label="`朗讀 ${word.headword}`"
                      @click="audio.speakOne('la', word.forms || word.headword)"
                    >🔊</button>
                    {{ word.forms || word.headword }}
                    <span v-if="word.ecclesiastical" class="ml-1 rounded bg-amber-100 px-1 text-[10px] text-amber-800">教會</span>
                    <span v-if="!word.attested" class="ml-1 rounded bg-rose-100 px-1 text-[10px] text-rose-700">待覆核</span>
                  </td>
                  <td class="px-3 py-2 text-xs text-stone-500">{{ word.pos || "—" }}</td>
                  <td class="px-4 py-2 break-words">{{ word.glossZh || "〔待補〕" }}</td>
                  <td class="px-3 py-2 text-xs text-stone-500 break-words">{{ word.glossEn || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="lesson.memoryUnits.length" class="mt-8">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="font-serif text-xl font-semibold">背誦單元（{{ lesson.memoryUnits.length }}）</h2>
            <button
              v-if="audio.deviceSupported.value"
              type="button"
              class="rounded-full border border-stone-400 px-4 py-1.5 text-xs text-stone-600 transition hover:border-stone-700 hover:text-stone-900"
              @click="toggleMemory"
            >{{ audio.playing.value ? "停止" : "逐句朗讀" }}</button>
          </div>
          <ul class="mt-3 space-y-3">
            <li
              v-for="(unit, index) in lesson.memoryUnits"
              :key="index"
              class="rounded-2xl border px-5 py-4 transition"
              :class="audio.currentSegmentId.value === `memory-${index}`
                ? 'border-amber-400 bg-amber-50'
                : 'border-stone-300 bg-white/80'"
            >
              <p class="font-serif text-[17px] leading-8 break-words">
                <button
                  v-if="audio.deviceSupported.value"
                  type="button"
                  class="mr-1 align-middle text-sm text-stone-400 transition hover:text-stone-800"
                  aria-label="朗讀這一句"
                  @click="audio.speakOne('la', unit.text)"
                >🔊</button>{{ unit.text }}</p>
              <p v-if="unit.zh" class="mt-1 text-sm leading-7 text-stone-600 break-words">{{ unit.zh }}</p>
              <p class="mt-2 text-[11px] text-stone-400">{{ unit.ref }}</p>
            </li>
          </ul>
        </section>

        <section v-if="lesson.reading.length" class="mt-8">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="font-serif text-xl font-semibold">讀文</h2>
            <div v-if="audio.deviceSupported.value" class="flex flex-wrap items-center gap-2">
              <label class="flex items-center gap-1 text-[11px] text-stone-500">
                語速
                <input
                  v-model.number="audio.rate.value"
                  type="range"
                  min="0.5"
                  max="1.1"
                  step="0.02"
                  class="w-24 accent-stone-700"
                >
              </label>
              <button
                v-if="audio.playing.value"
                type="button"
                class="rounded-full border border-stone-400 px-3 py-1.5 text-xs text-stone-600 transition hover:border-stone-700"
                @click="audio.togglePause()"
              >{{ audio.paused.value ? "繼續" : "暫停" }}</button>
              <button
                type="button"
                class="rounded-full border border-stone-400 px-4 py-1.5 text-xs text-stone-600 transition hover:border-stone-700 hover:text-stone-900"
                @click="toggleReading"
              >{{ audio.playing.value ? "停止朗讀" : "朗讀拉丁文" }}</button>
            </div>
          </div>
          <p v-if="audio.warning.value" class="mt-2 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-6 text-amber-900 break-words">{{ audio.warning.value }}</p>
          <ol class="mt-3 space-y-4">
            <li
              v-for="(row, index) in lesson.reading"
              :key="index"
              class="rounded-2xl border px-5 py-4 transition"
              :class="audio.currentSegmentId.value === `reading-${index}`
                ? 'border-amber-400 bg-amber-50'
                : 'border-stone-200 bg-white/70'"
            >
              <p class="font-serif text-[17px] leading-8 break-words">
                <button
                  v-if="audio.deviceSupported.value"
                  type="button"
                  class="mr-1 align-middle text-sm text-stone-400 transition hover:text-stone-800"
                  aria-label="朗讀這一行"
                  @click="audio.speakOne('la', row.latin)"
                >🔊</button>{{ row.latin }}</p>
              <p class="mt-1 text-sm leading-7 text-stone-600 break-words">{{ row.zh || "〔中譯待補〕" }}</p>
            </li>
          </ol>
        </section>

        <nav class="mt-10 flex justify-between gap-3 text-sm">
          <NuxtLink v-if="previous" :to="previous" class="rounded-full border border-stone-400 px-4 py-2 hover:border-stone-700">← 上一課</NuxtLink>
          <span v-else />
          <NuxtLink v-if="next" :to="next" class="rounded-full border border-stone-400 px-4 py-2 hover:border-stone-700">下一課 →</NuxtLink>
        </nav>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const key = computed(() => String(route.params.lesson || ""));

const { data: lesson, pending, error } = await useFetch(
  () => `/api/original-readers/lat-lessons/${key.value}`,
);

useHead(() => ({
  title: lesson.value ? `第 ${lesson.value.lesson} 課 · 教會拉丁文讀本` : "教會拉丁文讀本",
  meta: [{ name: "robots", content: "noindex, nofollow" }],
}));

// 音訊走裝置語音，不預先合成檔案：羅馬式教會發音本來就是照義大利語音韻讀拉丁文，
// 所以拼寫先經 toEcclesiasticalSpeech() 改寫，再交給義大利語聲線唸。改寫規則與
// 測試在 utils/ecclesiasticalLatin.ts 與 test/ecclesiastical-latin-speech.spec.ts。
const audio = useOriginalReaderAudio();

const readingSegments = computed(() =>
  (lesson.value?.reading || [])
    .map((row, index) => ({
      id: `reading-${index}`,
      ordinal: index,
      ref: "",
      sourceText: row.latin,
      translationZh: row.zh || "",
    }))
    .filter((row) => row.sourceText.trim()),
);

const memorySegments = computed(() =>
  (lesson.value?.memoryUnits || []).map((unit, index) => ({
    id: `memory-${index}`,
    ordinal: index,
    ref: unit.ref || "",
    sourceText: unit.text,
    translationZh: unit.zh || "",
  })),
);

function toggleReading() {
  if (audio.playing.value) audio.stop();
  else audio.playDevice("la", readingSegments.value);
}

function toggleMemory() {
  if (audio.playing.value) audio.stop();
  else audio.playDevice("la", memorySegments.value);
}

// 換課時停掉還在唸的上一課
watch(() => key.value, () => audio.stop());

const parsed = computed(() => {
  const compound = /^v(\d)-(\d{1,2})$/u.exec(key.value);
  if (compound) return { volume: Number(compound[1]), lesson: Number(compound[2]) };
  if (/^\d{1,2}$/u.test(key.value)) return { volume: 1, lesson: Number(key.value) };
  return null;
});

function href(volume: number, lessonNumber: number) {
  return `/original-readers/lat-lessons/v${volume}-${lessonNumber}`;
}

const previous = computed(() => {
  const at = parsed.value;
  if (!at) return null;
  if (at.lesson > 1) return href(at.volume, at.lesson - 1);
  return at.volume > 1 ? href(at.volume - 1, 50) : null;
});

const next = computed(() => {
  const at = parsed.value;
  if (!at) return null;
  if (at.lesson < 50) return href(at.volume, at.lesson + 1);
  return at.volume < 2 ? href(at.volume + 1, 1) : null;
});
</script>
