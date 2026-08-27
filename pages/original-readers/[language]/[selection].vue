<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="原文讀本" :back="{ to: `/original-readers/${language}`, label: '本冊目錄' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-4 py-7 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入讀文…</div>
      <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="selection && volume">
        <header class="rounded-3xl border border-stone-300 bg-[#fffdf7] p-6 shadow-sm sm:p-8">
          <div class="flex flex-col justify-between gap-5 md:flex-row md:items-start">
            <div>
              <div class="flex flex-wrap items-center gap-2 text-[11px] font-semibold tracking-wider text-stone-500">
                <span>{{ trackLabel(selection.track) }}</span><span>·</span><span>難度 {{ selection.difficulty }}</span><span>·</span><span>{{ sourceLabel }}</span>
              </div>
              <h1 class="mt-3 font-serif text-2xl font-semibold sm:text-3xl">{{ selection.title }}</h1>
              <p v-if="selection.titleOriginal" class="reader-title mt-2 text-xl text-stone-600" :lang="language" :dir="volume.rtl ? 'rtl' : 'ltr'">{{ selection.titleOriginal }}</p>
              <p v-if="selection.subtitle" class="mt-3 text-sm leading-6 text-stone-500">{{ selection.subtitle }}</p>
            </div>
            <button type="button" class="shrink-0 rounded-full border px-4 py-2 text-xs font-semibold" :class="completed ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-stone-300 bg-white text-stone-700'" @click="toggleComplete">
              {{ completed ? "✓ 已讀" : "標記已讀" }}
            </button>
          </div>

          <div class="mt-6 flex flex-wrap items-center gap-2 border-t border-stone-200 pt-5">
            <button v-for="track in audioTracks" :key="track.id" type="button" class="rounded-full bg-stone-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-40" :disabled="!track.src" @click="audio.playRecorded(track)">▶ {{ track.label }} · {{ speedLabel(track.speed) }}</button>
            <button v-if="!audioTracks.length && language === 'la'" type="button" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700" @click="audio.playDevice(language, segments)">裝置試聽（非校訂）</button>
            <button v-if="audio.playing" type="button" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs" @click="audio.togglePause">{{ audio.paused ? "繼續" : "暫停" }}</button>
            <button v-if="audio.playing" type="button" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs" @click="audio.stop">停止</button>
            <label v-if="!isVocabularySelection" class="ml-auto flex items-center gap-2 text-xs text-stone-500"><input v-model="showTranslation" type="checkbox" class="accent-stone-900"> 顯示中文對照</label>
          </div>
          <p v-if="language === 'hbo' && !audioTracks.length" class="mt-3 text-xs leading-5 text-amber-800">聖經希伯來文不使用現代以色列語裝置音色替代；校訂音軌匯入後才啟用播放。</p>
          <p v-if="language === 'grc' && !audioTracks.length" class="mt-3 text-xs leading-5 text-amber-800">希臘文不以 el-GR 現代裝置語音冒充 Mounce／Erasmian 或重建通用希臘語；請使用下方官方參考入口，校訂音軌匯入後才啟用正式播放。</p>
          <p v-if="audio.warning" class="mt-3 text-xs leading-5 text-amber-800">{{ audio.warning }}</p>
          <p v-if="materialization?.warning" class="mt-3 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-900">{{ materialization.warning }}</p>
        </header>

        <section v-if="isVocabularySelection" class="mt-6 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
          <header class="flex flex-col gap-3 border-b border-stone-200 p-5 sm:flex-row sm:items-end sm:justify-between sm:p-7">
            <div>
              <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">VOCABULARY SOURCE TABLE</p>
              <h2 class="mt-2 font-serif text-xl font-semibold">本單元 {{ vocabularyTokens.length }} 詞</h2>
              <p class="mt-1 text-xs leading-5 text-stone-500">原文、課本式音標（學術音譯，非 IPA）、英文釋義、專名類型、Strong 與逐詞來源／核驗狀態並列；空缺一律標明待核。</p>
            </div>
            <span class="w-fit rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-800">來源已接入</span>
          </header>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[72rem] border-collapse text-left text-sm">
              <thead class="bg-stone-100/80 text-[11px] font-semibold tracking-wider text-stone-500">
                <tr>
                  <th class="w-[18rem] px-5 py-3">原文</th>
                  <th class="w-[15rem] px-4 py-3">課本式音標<br><span class="font-normal tracking-normal">學術音譯，非 IPA</span></th>
                  <th class="min-w-[22rem] px-4 py-3">英文釋義</th>
                  <th class="w-[11rem] px-4 py-3">專名類型</th>
                  <th class="w-[8rem] px-4 py-3">Strong</th>
                  <th class="w-[21rem] px-4 py-3">來源／核驗</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-stone-200">
                <tr v-for="token in vocabularyTokens" :key="token.id" class="align-top transition hover:bg-amber-50/50">
                  <td class="px-5 py-4">
                    <div class="flex items-start gap-3">
                      <span class="mt-1 min-w-8 font-mono text-[11px] text-stone-400">#{{ vocabularyOrdinal(token) }}</span>
                      <div>
                        <p class="reader-token text-xl leading-8" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ token.printedEntry || token.surface }}</p>
                        <p v-if="token.printedEntry && token.surface !== token.printedEntry" class="reader-token mt-1 text-xs text-stone-500" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">詞頭：{{ token.surface }}</p>
                        <p v-if="token.lemmaUnpointed" class="mt-1 text-[11px] text-stone-400" dir="ltr">索引形：<span class="reader-token" lang="hbo" dir="rtl">{{ token.lemmaUnpointed }}</span></p>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-4" dir="ltr">
                    <p class="font-medium text-stone-800">{{ token.textbookTransliteration || token.reading || "—" }}</p>
                    <p v-if="token.transliterationSystem" class="mt-1 text-[11px] leading-4 text-stone-400">{{ token.transliterationSystem }}</p>
                    <p v-if="token.transliterationStatus" class="mt-1 text-[11px] leading-4 text-amber-700">{{ transliterationStatusLabel(token.transliterationStatus) }}</p>
                  </td>
                  <td class="px-4 py-4 leading-6 text-stone-700" dir="ltr">
                    <span v-if="token.glossEn">{{ token.glossEn }}</span>
                    <span v-else class="text-amber-700">待詞典核對</span>
                  </td>
                  <td class="px-4 py-4">
                    <span class="rounded-full px-2.5 py-1 text-xs" :class="token.isProperName ? 'bg-violet-100 text-violet-800' : 'bg-stone-100 text-stone-500'">{{ properNameLabel(token) }}</span>
                  </td>
                  <td class="px-4 py-4 font-mono text-xs text-stone-700" dir="ltr">{{ strongLabel(token) }}</td>
                  <td class="px-4 py-4">
                    <p class="text-xs leading-5 text-stone-600">{{ vocabularySourceLabel(token) }}</p>
                    <span class="mt-2 inline-flex rounded-full px-2 py-1 text-[11px]" :class="verificationClass(token.verification)">{{ verificationLabel(token.verification) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <footer class="border-t border-stone-200 bg-stone-50 px-5 py-4 text-xs leading-5 text-stone-500 sm:px-7">
            {{ selection.source.licenseNote }}
            <a v-if="selection.source.sourceUrl" :href="selection.source.sourceUrl" target="_blank" rel="noopener noreferrer" class="ml-2 font-semibold text-sky-800 underline decoration-sky-300 underline-offset-2">來源／發音參考 ↗</a>
          </footer>
        </section>

        <div v-else-if="segments.length" class="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem] lg:items-start">
          <article class="overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
            <section
              v-for="segment in segments"
              :id="segment.id"
              :key="segment.id"
              class="reader-segment border-b border-stone-200 p-5 transition last:border-b-0 sm:p-7"
              :class="audio.currentSegmentId === segment.id ? 'bg-amber-50 ring-2 ring-inset ring-amber-300' : ''"
            >
              <div class="mb-3 flex items-center justify-between gap-3 text-[11px] text-stone-400">
                <span class="font-mono">{{ segment.ref }}</span>
                <button v-if="segment.tokens?.length" type="button" class="hover:text-stone-800" @click="selectedToken = segment.tokens?.[0] || null">查看 {{ segment.tokens.length }} 個關鍵詞</button>
              </div>

              <p class="reader-source whitespace-pre-wrap" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ segment.sourceText }}</p>

              <div v-if="segment.tokens?.length" class="mt-4 rounded-2xl border border-stone-200 bg-stone-50/80 p-3">
                <p class="mb-2 text-[11px] font-semibold tracking-wider text-stone-500" dir="ltr">關鍵詞（另列分析；不取代或重建正文）</p>
                <div class="flex flex-wrap gap-2" :class="volume.rtl ? 'justify-end' : ''" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">
                  <button v-for="token in segment.tokens" :key="token.id" type="button" class="reader-token rounded-lg border border-stone-200 bg-white px-2.5 py-1 text-lg transition hover:border-amber-300 hover:bg-amber-50" :class="audio.currentTokenId === token.id ? 'border-amber-400 bg-amber-100' : ''" @click="selectedToken = token">{{ token.surface }}</button>
                </div>
              </div>

              <p v-if="segment.transliteration" class="mt-3 text-sm italic leading-6 text-stone-500" dir="ltr">{{ segment.transliteration }}</p>
              <p v-if="showTranslation && segment.translationZh" class="mt-4 border-l-2 border-stone-300 pl-4 text-sm leading-7 text-stone-700" dir="ltr">{{ segment.translationZh }}</p>
              <p v-if="segment.literalGloss" class="mt-2 text-xs leading-6 text-stone-500" dir="ltr">直譯：{{ segment.literalGloss }}</p>
              <ul v-if="segment.grammarNotes?.length" class="mt-4 space-y-1 text-xs leading-5 text-stone-500" dir="ltr">
                <li v-for="note in segment.grammarNotes" :key="note">• {{ note }}</li>
              </ul>
              <div v-if="segment.textualNotes?.length" class="mt-4 rounded-xl border border-sky-200 bg-sky-50/70 p-3 text-xs leading-5 text-sky-950" dir="ltr">
                <p class="font-semibold">文本／校勘註記</p>
                <ul class="mt-1 space-y-1">
                  <li v-for="note in segment.textualNotes" :key="note">• {{ note }}</li>
                </ul>
              </div>
            </section>
          </article>

          <aside class="lg:sticky lg:top-5">
            <div class="rounded-3xl border border-stone-300 bg-white p-5 shadow-sm">
              <template v-if="selectedToken">
                <p class="text-[11px] font-bold tracking-widest text-stone-400">WORD STUDY</p>
                <p class="reader-token mt-3 text-3xl" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ selectedToken.surface }}</p>
                <dl class="mt-5 space-y-3 text-sm">
                  <div><dt class="text-xs text-stone-400">詞典形</dt><dd class="reader-token mt-1 text-lg" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ selectedToken.lemmaPointed || selectedToken.lemma }}</dd></div>
                  <div v-if="selectedToken.lemmaUnpointed"><dt class="text-xs text-stone-400">無標點索引形</dt><dd class="reader-token mt-1" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ selectedToken.lemmaUnpointed }}</dd></div>
                  <div v-if="selectedToken.reading"><dt class="text-xs text-stone-400">讀音／轉寫</dt><dd class="mt-1" dir="ltr">{{ selectedToken.reading }}</dd></div>
                  <div><dt class="text-xs text-stone-400">中文義</dt><dd class="mt-1">{{ selectedToken.glossZh }}</dd></div>
                  <div v-if="selectedToken.partOfSpeech"><dt class="text-xs text-stone-400">詞類</dt><dd class="mt-1">{{ selectedToken.partOfSpeech }}</dd></div>
                  <div v-if="selectedToken.root"><dt class="text-xs text-stone-400">字根</dt><dd class="reader-token mt-1" :dir="volume.rtl ? 'rtl' : 'ltr'" :lang="language">{{ selectedToken.root }}</dd></div>
                </dl>
                <div v-if="selectedToken.morphology" class="mt-5 flex flex-wrap gap-1.5">
                  <span v-for="(value, key) in selectedToken.morphology" :key="key" class="rounded-full bg-stone-100 px-2 py-1 text-[11px] text-stone-600">{{ key }}: {{ value }}</span>
                </div>
                <div v-if="selectedToken.syntaxNote" class="mt-5 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-950" dir="ltr">
                  <p class="font-semibold">句法／編輯註記</p>
                  <p class="mt-1">{{ selectedToken.syntaxNote }}</p>
                </div>
              </template>
              <p v-else class="text-sm leading-6 text-stone-500">點選正文下方的關鍵詞，這裡會顯示詞典形、讀音、字根、詞類、形態與句法分析。</p>
            </div>

            <div class="mt-4 rounded-3xl border border-stone-300 bg-[#17231f] p-5 text-xs leading-6 text-stone-300">
              <p class="font-semibold text-white">來源紀錄</p>
              <p class="mt-2">{{ selection.source.edition }}</p>
              <p v-if="selection.source.editor">{{ selection.source.editor }}</p>
              <a v-if="selection.source.sourceUrl" :href="selection.source.sourceUrl" target="_blank" rel="noopener noreferrer" class="mt-2 inline-flex font-semibold text-amber-300 underline decoration-amber-700 underline-offset-2">來源／發音參考 ↗</a>
              <p class="mt-2 text-stone-400">{{ selection.source.licenseNote }}</p>
            </div>
          </aside>
        </div>

        <div v-else class="mt-6 rounded-3xl border border-dashed border-stone-400 bg-white/60 p-10 text-center">
          <p class="font-serif text-xl font-semibold">本篇已列入完整目錄</p>
          <p class="mt-2 text-sm leading-6 text-stone-500">授權原文、詞形資料與校訂音軌尚待匯入；目前不以替代文字冒充完成。</p>
        </div>

        <nav class="mt-7 flex items-center justify-between gap-4 text-sm">
          <NuxtLink v-if="previous" :to="`/original-readers/${language}/${previous.id}`" class="rounded-full border border-stone-300 bg-white px-4 py-2 hover:border-stone-500">← {{ previous.title }}</NuxtLink><span v-else />
          <NuxtLink v-if="next" :to="`/original-readers/${language}/${next.id}`" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-right hover:border-stone-500">{{ next.title }} →</NuxtLink>
        </nav>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import type {
  OriginalReaderAudioTrack,
  OriginalReaderLanguage,
  OriginalReaderSelection,
  OriginalReaderToken,
  OriginalReaderVolume,
} from "~/data/originalReaders/types";

definePageMeta({ middleware: "auth" });
useHead({ meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }] });

const route = useRoute();
const supabase = useSupabaseClient();
const audio = useOriginalReaderAudio();
const language = computed(() => String(route.params.language) as OriginalReaderLanguage);
const volume = ref<OriginalReaderVolume | null>(null);
const selection = ref<OriginalReaderSelection | null>(null);
const materialization = ref<{ source: string; warning?: string } | null>(null);
const pending = ref(true);
const error = ref("");
const showTranslation = ref(true);
const completed = ref(false);
const selectedToken = ref<OriginalReaderToken | null>(null);

const segments = computed(() => selection.value?.segments || []);
const vocabularyTokens = computed<OriginalReaderToken[]>(() =>
  segments.value.flatMap((segment) => segment.tokens || []),
);
const isVocabularySelection = computed(() =>
  selection.value?.kind === "vocabulary" && vocabularyTokens.value.length > 0,
);
const audioTracks = computed<OriginalReaderAudioTrack[]>(() => {
  const seen = new Set<string>();
  return segments.value.flatMap((segment) => segment.audio || []).filter((track) => {
    if (seen.has(track.id)) return false;
    seen.add(track.id);
    return true;
  });
});

const currentIndex = computed(() => volume.value?.selections.findIndex((item) => item.id === selection.value?.id) ?? -1);
const previous = computed(() => currentIndex.value > 0 ? volume.value?.selections[currentIndex.value - 1] : null);
const next = computed(() => currentIndex.value >= 0 && currentIndex.value < (volume.value?.selections.length || 0) - 1 ? volume.value?.selections[currentIndex.value + 1] : null);
const sourceLabel = computed(() => {
  if (isVocabularySelection.value) return "私人授權詞表";
  if (materialization.value?.source === "bible-corpus") return "私人聖經語料庫";
  if (materialization.value?.source === "manifest") return "編訂樣本";
  return "目錄已建";
});

function progressKey() {
  return `original-reader-progress:${language.value}:${String(route.params.selection)}`;
}

function toggleComplete() {
  completed.value = !completed.value;
  try { localStorage.setItem(progressKey(), completed.value ? "complete" : ""); } catch { /* private browsing */ }
}

async function load() {
  pending.value = true;
  error.value = "";
  audio.stop();
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    const result = await $fetch<{ volume: OriginalReaderVolume; selection: OriginalReaderSelection; materialization: { source: string; warning?: string } }>(
      `/api/original-readers/${language.value}/${String(route.params.selection)}`,
      { headers: { Authorization: `Bearer ${session.access_token}` } },
    );
    volume.value = result.volume;
    selection.value = result.selection;
    materialization.value = result.materialization;
    selectedToken.value = result.selection.segments?.find((item) => item.tokens?.length)?.tokens?.[0] || null;
    try { completed.value = localStorage.getItem(progressKey()) === "complete"; } catch { completed.value = false; }
    useHead({ title: `${result.selection.title} — ${result.volume.title}` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
}

onMounted(load);
watch(() => route.params.selection, load);

function trackLabel(track: OriginalReaderSelection["track"]) {
  return { core: "核心課程", advanced: "進階選讀", reference: "參考單元" }[track];
}
function speedLabel(speed: OriginalReaderAudioTrack["speed"]) {
  return { slow: "慢速", natural: "自然速", chant: "吟誦" }[speed];
}

function vocabularyOrdinal(token: OriginalReaderToken) {
  if (token.lesson && token.lessonSlot) {
    return (token.lesson - 1) * 20 + token.lessonSlot;
  }
  if (token.productionGroup && token.groupSlot) {
    return (token.productionGroup - 1) * 50 + token.groupSlot;
  }
  return token.sourceOrder || token.ordinal;
}

const transliterationStatusLabels: Record<string, string> = {
  rule_generated_exception_review: "規則產生・例外仍需審讀",
  rule_generated_from_official_table: "依官方轉寫表規則產生",
};

function transliterationStatusLabel(status: string) {
  return transliterationStatusLabels[status] || status.replaceAll("_", " ");
}

const properNameTypeLabels: Record<string, string> = {
  divine_name_or_title: "神名／神聖稱號",
  people_or_nation: "民族／國族名",
  person: "人名",
  place: "地名",
  proper_name: "其他專名",
};

function properNameLabel(token: OriginalReaderToken) {
  if (!token.isProperName) return "非專名";
  const types = (token.properNameTypes || []).map(
    (type) => properNameTypeLabels[type] || type.replaceAll("_", " "),
  );
  return types.length ? types.join("、") : "專名（類型待核）";
}

function strongLabel(token: OriginalReaderToken) {
  const values = token.strongs?.filter(Boolean) || [];
  if (!values.length && token.strong) values.push(token.strong);
  return values.length ? values.join(" / ") : "待核";
}

function vocabularySourceLabel(token: OriginalReaderToken) {
  if (token.sourceType === "bbh2_order") {
    const sourceOrders = token.sourceOrders?.length
      ? token.sourceOrders.join(" / ")
      : token.sourceOrder;
    return [
      "BBH2 教材次序",
      token.sourceChapter ? `第 ${token.sourceChapter} 章` : "",
      sourceOrders ? `原表位 ${sourceOrders}` : "",
    ].filter(Boolean).join(" · ");
  }
  if (token.sourceType === "reader_frequency_extension") {
    return [
      "WLC／OSHB 讀本詞頻延伸",
      token.frequency ? `語料頻次 ${token.frequency}` : "",
    ].filter(Boolean).join(" · ");
  }
  if (token.sourceType === "mounce_bbg_chapter_order") {
    return [
      "Mounce BBG 章序",
      token.bbgChapter ? `第 ${token.bbgChapter} 章` : "",
      token.sourcePage ? `來源頁 ${token.sourcePage}` : "",
    ].filter(Boolean).join(" · ");
  }
  if (token.sourceType === "mounce_official_frequency_extension") {
    return [
      "Mounce 官方頻率延伸",
      token.sourcePage ? `來源頁 ${token.sourcePage}` : "",
    ].filter(Boolean).join(" · ");
  }
  return token.sourceType?.replaceAll("_", " ") || "來源待核";
}

const verificationLabels: Record<string, string> = {
  source_and_lexicon_matched: "來源與詞典吻合",
  source_verified: "來源已核；詞典資料待補",
  lemma_frequency_verified: "詞元與語料頻率已核",
  source_verified_lexicon_pending: "來源已核；詞典配對待核",
};

function verificationLabel(status?: string) {
  if (!status) return "核驗狀態待補";
  return verificationLabels[status] || status.replaceAll("_", " ");
}

function verificationClass(status?: string) {
  if (status === "source_and_lexicon_matched") return "bg-emerald-100 text-emerald-800";
  if (status === "lemma_frequency_verified") return "bg-sky-100 text-sky-800";
  return "bg-amber-100 text-amber-800";
}
</script>

<style scoped>
.reader-title,
.reader-source,
.reader-token {
  font-family: "Gentium Plus", "SBL Greek", "Noto Serif", "Noto Serif Hebrew", "SBL Hebrew", "Ezra SIL", serif;
}
.reader-source {
  font-size: clamp(1.35rem, 2.4vw, 1.75rem);
  line-height: 2;
  text-wrap: pretty;
}
.reader-source[lang="hbo"],
.reader-token[lang="hbo"],
.reader-title[lang="hbo"] {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
  line-height: 2.15;
}
</style>
