<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader
      :title="lesson ? `第 ${lesson.lesson} 課` : '教會拉丁文讀本'"
      :back="{ to: '/original-readers/lat-lessons', label: '兩冊總覽' }"
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
          <h2 class="font-serif text-xl font-semibold">本課詞彙（{{ lesson.vocabulary.length }}）</h2>
          <div class="mt-3 overflow-x-auto rounded-2xl border border-stone-300 bg-white/80">
            <table class="w-full min-w-[36rem] border-collapse text-sm">
              <thead class="bg-stone-100 text-left text-[11px] tracking-widest text-stone-500">
                <tr>
                  <th class="px-4 py-2 font-semibold">拉丁文</th>
                  <th class="px-3 py-2 font-semibold">詞類</th>
                  <th class="px-4 py-2 font-semibold">繁體中文</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="word in lesson.vocabulary" :key="word.headword" class="border-t border-stone-200 align-top">
                  <td class="px-4 py-2 font-serif break-words">
                    {{ word.forms || word.headword }}
                    <span v-if="word.ecclesiastical" class="ml-1 rounded bg-amber-100 px-1 text-[10px] text-amber-800">教會</span>
                    <span v-if="!word.attested" class="ml-1 rounded bg-rose-100 px-1 text-[10px] text-rose-700">待覆核</span>
                  </td>
                  <td class="px-3 py-2 text-stone-500">{{ word.pos }}</td>
                  <td class="px-4 py-2 break-words">{{ word.glossZh || "〔待補〕" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="lesson.memoryUnits.length" class="mt-8">
          <h2 class="font-serif text-xl font-semibold">記憶單元</h2>
          <ul class="mt-3 space-y-3">
            <li v-for="(unit, index) in lesson.memoryUnits" :key="index" class="rounded-2xl border border-stone-300 bg-white/80 px-5 py-4">
              <p class="font-serif text-[17px] leading-8 break-words">{{ unit.text }}</p>
              <p v-if="unit.zh" class="mt-1 text-sm leading-7 text-stone-600 break-words">{{ unit.zh }}</p>
              <p class="mt-2 text-[11px] text-stone-400">{{ unit.ref }}</p>
            </li>
          </ul>
        </section>

        <section v-if="lesson.reading.length" class="mt-8">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h2 class="font-serif text-xl font-semibold">讀本</h2>
            <button
              type="button"
              class="rounded-full border border-stone-400 px-4 py-1.5 text-xs text-stone-600 transition hover:border-stone-700 hover:text-stone-900"
              @click="toggleSpeech"
            >
              {{ speaking ? "停止朗讀" : "朗讀拉丁文" }}
            </button>
          </div>
          <ol class="mt-3 space-y-4">
            <li v-for="(row, index) in lesson.reading" :key="index" class="rounded-2xl border border-stone-200 bg-white/70 px-5 py-4">
              <p class="font-serif text-[17px] leading-8 break-words">{{ row.latin }}</p>
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

// Browser speech is a study aid, not the release audio track: the recorded
// Ecclesiastical pronunciation is a separate deliverable and this is explicitly
// not it. Voices vary by device, so the nearest Italian voice is preferred and
// the browser default is accepted when none is installed.
const speaking = ref(false);

function toggleSpeech() {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  if (speaking.value) {
    window.speechSynthesis.cancel();
    speaking.value = false;
    return;
  }
  const text = (lesson.value?.reading || []).map((row) => row.latin).join(" ");
  if (!text) return;
  const utterance = new SpeechSynthesisUtterance(text);
  const italian = window.speechSynthesis.getVoices().find((voice) => voice.lang.startsWith("it"));
  if (italian) utterance.voice = italian;
  utterance.lang = italian?.lang || "it-IT";
  utterance.rate = 0.85;
  utterance.onend = () => { speaking.value = false; };
  window.speechSynthesis.speak(utterance);
  speaking.value = true;
}

onBeforeUnmount(() => {
  if (typeof window !== "undefined" && window.speechSynthesis) window.speechSynthesis.cancel();
});

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
