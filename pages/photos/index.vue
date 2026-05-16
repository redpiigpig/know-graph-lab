<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/" class="text-sm text-stone-500 hover:text-stone-900 transition">← 首頁</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-6xl mx-auto px-6 py-14">
      <!-- Hero -->
      <header class="mb-12 flex items-end justify-between flex-wrap gap-4 border-b border-stone-300/60 pb-6">
        <div>
          <p class="text-[11px] uppercase tracking-[0.25em] text-stone-500 mb-2">Photo Library</p>
          <h1 class="text-4xl font-serif text-stone-900 tracking-tight">辰瑋相片</h1>
          <p class="mt-2 text-stone-500 text-sm">依年份瀏覽 · 點任一年份進入月份</p>
        </div>
        <div v-if="!loading && years.length" class="text-right font-serif">
          <div class="text-4xl text-stone-800 leading-none">{{ totalPhotos.toLocaleString() }}</div>
          <div class="mt-2 text-[10px] uppercase tracking-[0.25em] text-stone-500">
            張 · {{ activeYears }}／{{ years.length }} 年有照片
          </div>
        </div>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>
      <div v-else-if="!years.length" class="text-stone-400 text-sm">尚無年份資料夾</div>

      <!-- Year grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <NuxtLink
          v-for="(y, i) in years"
          :key="y.year"
          :to="`/photos/${y.year}`"
          class="year-card group"
          :class="y.total === 0 && 'year-card--empty'"
        >
          <span class="year-card__index">{{ pad(i + 1) }} / {{ pad(years.length) }}</span>

          <div class="year-card__body">
            <div class="year-card__year">{{ y.year }}</div>
            <div class="year-card__rule"></div>
            <div class="year-card__stat">
              <span v-if="y.total > 0" class="font-serif text-stone-800 text-lg leading-none">
                {{ y.total.toLocaleString() }}
              </span>
              <span v-else class="text-stone-400 text-sm">—</span>
              <span class="text-[10px] uppercase tracking-widest text-stone-500 ml-1">張</span>
            </div>
            <div v-if="y.monthsWithPhotos > 0" class="text-[11px] text-stone-500 mt-1">
              {{ y.monthsWithPhotos }} 個月份
            </div>
            <div v-else class="text-[11px] text-stone-400 mt-1 italic">尚未整理</div>
          </div>

          <span class="year-card__arrow" aria-hidden="true">→</span>
        </NuxtLink>
      </div>

      <p class="mt-12 text-center text-[11px] text-stone-400 tracking-wider">
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
const pad = (n: number) => String(n).padStart(2, "0");

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
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  aspect-ratio: 4 / 5;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 22px;
  padding: 18px 20px 20px;
  text-decoration: none;
  color: inherit;
  transition: transform .35s ease, box-shadow .35s ease, border-color .35s ease;
  will-change: transform;
  overflow: hidden;
}
.year-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px -20px rgba(60, 30, 0, 0.18), 0 4px 12px -8px rgba(60, 30, 0, 0.1);
  border-color: rgb(168 162 158 / 0.9);
}
.year-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 100% 0%, rgba(217, 119, 6, 0.06), transparent 55%);
  pointer-events: none;
  opacity: 0;
  transition: opacity .4s ease;
}
.year-card:hover::before { opacity: 1; }

.year-card--empty {
  background: #f7f3eb;
  border-style: dashed;
}
.year-card--empty .year-card__year {
  color: rgb(168 162 158);
}

.year-card__index {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 10px;
  letter-spacing: 0.2em;
  color: rgb(168 162 158);
  font-variant-numeric: tabular-nums;
}

.year-card__body {
  margin-top: auto;
}

.year-card__year {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: clamp(2.8rem, 6vw, 4rem);
  line-height: 0.92;
  letter-spacing: -0.02em;
  color: rgb(41 37 36);
  font-weight: 500;
}

.year-card__rule {
  width: 28px;
  height: 1px;
  background: rgb(120 113 108);
  margin: 14px 0 12px;
  transition: width .35s ease;
}
.year-card:hover .year-card__rule { width: 48px; }

.year-card__stat {
  display: flex;
  align-items: baseline;
}

.year-card__arrow {
  position: absolute;
  bottom: 18px;
  right: 20px;
  color: rgb(120 113 108);
  font-size: 18px;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .3s ease, transform .3s ease;
}
.year-card:hover .year-card__arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
