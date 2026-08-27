<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="原文讀本" :back="{ to: '/original-readers', label: '原文讀本總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入本冊目錄…</div>
      <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="volume">
        <header class="rounded-[2rem] border border-stone-300 bg-[#fffdf7] p-7 shadow-sm sm:p-9">
          <div class="flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <div>
              <p class="text-xs font-bold tracking-[0.25em] text-stone-500">{{ languageName }} · JIS B5</p>
              <h1 class="mt-3 font-serif text-3xl font-semibold sm:text-4xl">{{ volume.title }}</h1>
              <p class="mt-3 max-w-3xl text-sm leading-7 text-stone-600">{{ volume.subtitle }}</p>
            </div>
            <div class="shrink-0 rounded-2xl bg-stone-900 px-5 py-4 text-[#f7f0df]">
              <div class="text-2xl font-semibold">{{ volume.selections.length }}</div>
              <div class="text-xs text-stone-400">個讀本單元</div>
            </div>
          </div>

          <div v-if="volume.vocabularyCurriculum" class="mt-6 rounded-2xl border border-stone-200 bg-stone-50 p-4 text-sm leading-6">
            <div class="flex flex-wrap items-center gap-2">
              <strong>詞彙課程：</strong>
              <span>{{ volume.vocabularyCurriculum.lessonCount }} 課</span>
              <span v-if="volume.vocabularyCurriculum.wordsPerLesson">× 每課 {{ volume.vocabularyCurriculum.wordsPerLesson }} 字</span>
              <span class="rounded-full px-2 py-0.5 text-[11px]" :class="volume.vocabularyCurriculum.exactOrderingStatus === 'verified' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'">
                {{ volume.vocabularyCurriculum.exactOrderingStatus === "verified" ? "順序已核對" : "等待授權逐課詞表" }}
              </span>
            </div>
            <p class="mt-1 text-stone-600">{{ volume.vocabularyCurriculum.orderingRule }}</p>
            <p class="mt-1 text-xs text-stone-500">依據：{{ volume.vocabularyCurriculum.primarySources.join("；") }}</p>
          </div>

          <div v-if="volume.textPolicy" class="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950">
            <strong>正文規格：</strong>{{ volume.textPolicy.notes }}
          </div>
        </header>

        <div class="mt-6 flex flex-wrap gap-2">
          <button v-for="option in filters" :key="option.id" type="button" class="rounded-full border px-3 py-1.5 text-xs transition" :class="filter === option.id ? 'border-stone-900 bg-stone-900 text-white' : 'border-stone-300 bg-white text-stone-600 hover:border-stone-500'" @click="filter = option.id">{{ option.label }}</button>
        </div>

        <section v-for="part in visibleParts" :key="part.id" class="mt-8">
          <div class="mb-3 flex items-end justify-between gap-4 border-b border-stone-300 pb-2">
            <div>
              <p class="text-[11px] font-bold tracking-[0.22em] text-stone-400">PART {{ part.ordinal }}</p>
              <h2 class="mt-1 font-serif text-xl font-semibold">{{ part.title }}</h2>
            </div>
            <span class="text-xs text-stone-400">{{ selectionsForPart(part.id).length }} 篇</span>
          </div>
          <p class="mb-4 text-sm leading-6 text-stone-500">{{ part.description }}</p>

          <div class="overflow-hidden rounded-2xl border border-stone-300 bg-[#fffdf7]">
            <NuxtLink
              v-for="selection in selectionsForPart(part.id)"
              :key="selection.id"
              :to="`/original-readers/${volume.slug}/${selection.id}`"
              class="grid gap-2 border-b border-stone-200 px-4 py-4 transition last:border-b-0 hover:bg-white sm:grid-cols-[3.2rem_1fr_auto] sm:items-center sm:gap-4"
            >
              <span class="font-mono text-xs text-stone-400">{{ String(selection.ordinal).padStart(2, "0") }}</span>
              <span>
                <span class="font-medium text-stone-900">{{ selection.title }}</span>
                <span v-if="selection.titleOriginal" class="ml-2 font-reader text-sm text-stone-500" :dir="volume.rtl ? 'rtl' : 'ltr'">{{ selection.titleOriginal }}</span>
                <span class="mt-1 flex flex-wrap gap-1.5 text-[11px] text-stone-400">
                  <span>{{ kindLabel(selection.kind) }}</span><span>·</span><span>難度 {{ selection.difficulty }}</span><span>·</span><span>約 {{ selection.estimatedPages }} 頁</span>
                </span>
              </span>
              <span class="justify-self-start rounded-full px-2.5 py-1 text-[11px] sm:justify-self-end" :class="statusClass(selection.status)">{{ statusLabel(selection.status) }}</span>
            </NuxtLink>
          </div>
        </section>

        <div v-if="!visibleParts.length" class="mt-8 rounded-2xl border border-stone-300 bg-white p-8 text-center text-sm text-stone-500">這個篩選目前沒有單元。</div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import type {
  OriginalReaderPart,
  OriginalReaderSelection,
  OriginalReaderVolume,
} from "~/data/originalReaders/types";

definePageMeta({ middleware: "auth" });
useHead({ meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }] });

const route = useRoute();
const supabase = useSupabaseClient();
const volume = ref<OriginalReaderVolume | null>(null);
const pending = ref(true);
const error = ref("");
const filter = ref<"all" | "core" | "advanced" | "ready">("all");
const filters = [
  { id: "all" as const, label: "全部" },
  { id: "core" as const, label: "核心課程" },
  { id: "advanced" as const, label: "進階選讀" },
  { id: "ready" as const, label: "已有正文" },
];

onMounted(async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    volume.value = await $fetch<OriginalReaderVolume>(
      `/api/original-readers/${String(route.params.language)}`,
      { headers: { Authorization: `Bearer ${session.access_token}` } },
    );
    useHead({ title: `${volume.value.title} — Know Graph Lab` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
});

const languageName = computed(() => ({ hbo: "聖經希伯來文", grc: "聖經／通用希臘文", la: "教會拉丁文" }[volume.value?.slug || "hbo"]));
const readyStatuses = new Set(["sample_ready", "edited", "audio_ready", "complete"]);

function filteredSelections(): OriginalReaderSelection[] {
  if (!volume.value) return [];
  return volume.value.selections.filter((selection) => {
    if (filter.value === "all") return true;
    if (filter.value === "ready") return readyStatuses.has(selection.status);
    return selection.track === filter.value;
  });
}

const visibleParts = computed<OriginalReaderPart[]>(() =>
  (volume.value?.parts || []).filter((part) => selectionsForPart(part.id).length),
);

function selectionsForPart(partId: string) {
  return filteredSelections().filter((selection) => selection.partId === partId);
}

function kindLabel(kind: OriginalReaderSelection["kind"]) {
  return {
    orientation: "導讀",
    vocabulary: "詞彙",
    memory_unit: "背誦",
    bible_chapter: "聖經",
    prayer: "禱文",
    creed: "信經",
    liturgy: "禮儀",
    haggadah: "哈加達",
    rabbinic: "拉比文獻",
    patristic: "教父文獻",
    bridge_text: "橋接文獻",
    appendix: "附錄",
  }[kind];
}

function statusLabel(status: OriginalReaderSelection["status"]) {
  return {
    planned: "已排入",
    source_ready: "來源就緒",
    sample_ready: "可試讀",
    edited: "已校訂",
    audio_ready: "含音訊",
    complete: "完成",
  }[status];
}

function statusClass(status: OriginalReaderSelection["status"]) {
  return readyStatuses.has(status)
    ? "bg-emerald-100 text-emerald-800"
    : status === "source_ready"
      ? "bg-sky-100 text-sky-800"
      : "bg-stone-100 text-stone-500";
}
</script>

<style scoped>
.font-reader { font-family: "Gentium Plus", "Noto Serif", "Noto Serif Hebrew", serif; }
</style>
