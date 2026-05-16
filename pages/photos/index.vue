<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/" class="text-sm text-stone-500 hover:text-stone-900 transition">← 首頁</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <!-- Hero -->
      <header class="mb-8 flex items-end justify-between flex-wrap gap-3 border-b border-stone-300/60 pb-4">
        <div>
          <p class="text-[10px] uppercase tracking-[0.25em] text-stone-500 mb-1">Photo Library</p>
          <h1 class="text-3xl font-serif text-stone-900 tracking-tight">辰瑋相片</h1>
        </div>
        <div v-if="!loading && years.length" class="text-right font-serif">
          <div class="text-2xl text-stone-800 leading-none">{{ totalPhotos.toLocaleString() }}</div>
          <div class="mt-1 text-[10px] uppercase tracking-[0.25em] text-stone-500">
            張 · {{ activeYears }}／{{ years.length }} 年
          </div>
        </div>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>
      <div v-else-if="!years.length" class="text-stone-400 text-sm">尚無年份資料夾</div>

      <!-- Year grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <NuxtLink
          v-for="y in years"
          :key="y.year"
          :to="`/photos/${y.year}`"
          class="year-card group"
          :class="y.total === 0 && 'year-card--empty'"
        >
          <div class="flex items-baseline gap-2">
            <span class="year-card__year">{{ y.year }}</span>
            <span class="year-card__arrow" aria-hidden="true">→</span>
          </div>
          <div class="mt-1 flex items-baseline justify-between gap-2">
            <span v-if="y.total > 0" class="text-stone-700 font-serif text-base leading-none">
              {{ y.total.toLocaleString() }}<span class="text-[10px] tracking-widest uppercase text-stone-500 ml-1">張</span>
            </span>
            <span v-else class="text-stone-400 text-[11px] italic">尚未整理</span>
            <span v-if="y.monthsWithPhotos > 0" class="text-[10px] tracking-widest uppercase text-stone-500">
              {{ y.monthsWithPhotos }}／12 月
            </span>
          </div>
        </NuxtLink>
      </div>

      <p class="mt-10 text-center text-[11px] text-stone-400 tracking-wider">
        照片直接從 Google Drive 讀取
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: "辰瑋相片 — 知識圖工作室" });

interface YearItem {
  year: string;
  total: number;
  monthsWithPhotos: number;
}

const loading = ref(true);
const errMsg = ref("");
const years = ref<YearItem[]>([]);
const totalPhotos = computed(() => years.value.reduce((a, b) => a + b.total, 0));
const activeYears = computed(() => years.value.filter((y) => y.total > 0).length);

onMounted(async () => {
  try {
    const r = await authedFetch<{ years: YearItem[] }>("/api/photos/years");
    years.value = r.years || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.year-card {
  position: relative;
  display: block;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 14px;
  padding: 12px 16px 14px;
  text-decoration: none;
  color: inherit;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.year-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px -14px rgba(60, 30, 0, 0.18);
  border-color: rgb(168 162 158 / 0.9);
}

.year-card--empty {
  background: #f7f3eb;
  border-style: dashed;
}
.year-card--empty .year-card__year { color: rgb(168 162 158); }

.year-card__year {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: 1.85rem;
  font-weight: 500;
  color: rgb(41 37 36);
  line-height: 1;
  letter-spacing: -0.02em;
}

.year-card__arrow {
  color: rgb(168 162 158);
  font-size: 14px;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .25s ease, transform .25s ease;
}
.year-card:hover .year-card__arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
