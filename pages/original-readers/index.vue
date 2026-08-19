<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="原文讀本" :back="{ to: '/', label: '首頁' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-5 py-10 sm:px-8">
      <section class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-10 text-[#f7f0df] shadow-xl sm:px-10">
        <p class="mb-3 text-xs font-semibold tracking-[0.28em] text-amber-300">PRIVATE ORIGINAL-LANGUAGE LIBRARY</p>
        <h1 class="max-w-3xl font-serif text-3xl font-semibold leading-tight sm:text-5xl">希伯來文・希臘文・拉丁文<br>三冊 B5 原文讀本</h1>
        <p class="mt-5 max-w-2xl text-sm leading-7 text-stone-300">紙本採 JIS B5 直式鏡像邊界；線上版逐段對照原文、中文、詞形與校訂音訊。此區只供登入後私人使用，搜尋引擎不收錄。</p>
        <div class="mt-6 flex flex-wrap gap-2 text-xs">
          <span class="rounded-full border border-stone-500 px-3 py-1.5">182 × 257 mm</span>
          <span class="rounded-full border border-stone-500 px-3 py-1.5">逐段／逐字音訊對齊</span>
          <span class="rounded-full border border-stone-500 px-3 py-1.5">核心＋進階選讀</span>
        </div>
      </section>

      <div v-if="pending" class="py-16 text-center text-sm text-stone-500">載入三冊目錄…</div>
      <div v-else-if="error" class="my-8 rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>
      <section v-else class="mt-8 grid gap-5 lg:grid-cols-3">
        <article
          v-for="volume in volumes"
          :key="volume.slug"
          class="group rounded-3xl border border-stone-300 bg-[#fffdf7] p-6 shadow-sm transition hover:-translate-y-1 hover:border-stone-500 hover:shadow-lg"
        >
          <NuxtLink :to="`/original-readers/${volume.slug}`" class="block">
            <div class="flex items-start justify-between gap-4">
              <span class="rounded-full px-3 py-1 text-xs font-bold tracking-widest" :class="accentClass(volume.slug)">{{ languageLabel(volume.slug) }}</span>
              <span class="text-xs text-stone-400">約 {{ volume.estimatedPages }} 頁</span>
            </div>
            <h2 class="mt-6 font-serif text-2xl font-semibold">{{ volume.title }}</h2>
            <p class="mt-2 min-h-12 text-sm leading-6 text-stone-600">{{ volume.subtitle }}</p>
            <dl class="mt-6 grid grid-cols-2 gap-3 border-t border-stone-200 pt-5 text-sm">
              <div><dt class="text-xs text-stone-400">目錄單元</dt><dd class="mt-1 font-semibold">{{ volume.selectionCount }}</dd></div>
              <div><dt class="text-xs text-stone-400">已可閱讀</dt><dd class="mt-1 font-semibold">{{ volume.readyCount }}</dd></div>
            </dl>
            <p class="mt-6 text-sm font-semibold text-stone-700 group-hover:text-stone-950">開啟本冊目錄 →</p>
          </NuxtLink>

          <NuxtLink
            v-if="volume.slug === 'hbo'"
            to="/original-readers/hbo-lessons"
            class="mt-5 flex items-center justify-between rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-950 transition hover:border-amber-500 hover:bg-amber-100"
          >
            <span>開啟50課完整私人讀本</span>
            <span aria-hidden="true">→</span>
          </NuxtLink>

          <NuxtLink
            v-if="volume.slug === 'grc'"
            to="/original-readers/grc-lessons"
            class="mt-5 flex items-center justify-between rounded-2xl border border-sky-300 bg-sky-50 px-4 py-3 text-sm font-semibold text-sky-950 transition hover:border-sky-500 hover:bg-sky-100"
          >
            <span>開啟50課完整私人讀本</span>
            <span aria-hidden="true">→</span>
          </NuxtLink>

          <div v-if="referenceProfiles(volume).length" class="mt-5 border-t border-stone-200 pt-4">
            <p class="text-[11px] font-bold tracking-wider text-stone-400">官方發音參考</p>
            <a
              v-for="profile in referenceProfiles(volume)"
              :key="profile.id"
              :href="profile.referenceUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-2 flex items-start justify-between gap-3 rounded-xl bg-stone-100 px-3 py-2 text-xs text-stone-700 transition hover:bg-amber-50 hover:text-stone-950"
            >
              <span><strong>{{ profile.label }}</strong><span class="mt-0.5 block font-normal leading-5 text-stone-500">{{ profile.description }}</span></span>
              <span aria-hidden="true">↗</span>
            </a>
          </div>
        </article>
      </section>

      <section class="mt-8 rounded-3xl border border-stone-300 bg-white/70 p-6 text-sm leading-7 text-stone-600">
        <h2 class="font-serif text-lg font-semibold text-stone-900">製作原則</h2>
        <p class="mt-2">三冊正文保持各語言的歷史字形與校訂本標記。希伯來文完整保留馬所拉母音點，不以現代無母音拼法代替；希伯來文與希臘文以官方參考及校訂音軌承擔正式發音，拉丁文裝置語音也只作明確標示的臨時試聽。</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({
  title: "三語原文讀本 — Know Graph Lab",
  meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }],
});

interface PronunciationProfileSummary {
  id: string;
  label: string;
  description: string;
  referenceUrl?: string;
}

interface ReferencePronunciationProfile extends PronunciationProfileSummary {
  referenceUrl: string;
}

interface VolumeSummary {
  slug: "hbo" | "grc" | "la";
  title: string;
  subtitle: string;
  selectionCount: number;
  readyCount: number;
  estimatedPages: number;
  pronunciationProfiles: PronunciationProfileSummary[];
}

const supabase = useSupabaseClient();
const volumes = ref<VolumeSummary[]>([]);
const pending = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    volumes.value = await $fetch<VolumeSummary[]>("/api/original-readers", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
});

function languageLabel(slug: VolumeSummary["slug"]) {
  return { hbo: "HEBREW", grc: "GREEK", la: "LATIN" }[slug];
}

function accentClass(slug: VolumeSummary["slug"]) {
  return {
    hbo: "bg-amber-100 text-amber-900",
    grc: "bg-sky-100 text-sky-900",
    la: "bg-rose-100 text-rose-900",
  }[slug];
}

function referenceProfiles(volume: VolumeSummary): ReferencePronunciationProfile[] {
  return volume.pronunciationProfiles.filter(
    (profile): profile is ReferencePronunciationProfile =>
      typeof profile.referenceUrl === "string" && profile.referenceUrl.length > 0,
  );
}
</script>
