<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/photos" class="text-sm text-stone-500 hover:text-stone-900 transition">← 全部年份</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-6xl mx-auto px-6 py-14">
      <nav class="text-[11px] uppercase tracking-[0.2em] text-stone-500 mb-3">
        <NuxtLink to="/photos" class="hover:text-stone-900">照片庫</NuxtLink>
        <span class="mx-2">/</span>
        <span class="text-stone-700">{{ year }}</span>
      </nav>

      <header class="mb-12 flex items-end justify-between flex-wrap gap-4 border-b border-stone-300/60 pb-6">
        <div>
          <h1 class="font-serif text-6xl text-stone-900 leading-none tracking-tight">{{ year }}</h1>
          <p class="mt-3 text-stone-500 text-sm">選擇月份進入照片視圖</p>
        </div>
        <div v-if="!loading" class="text-right font-serif">
          <div class="text-3xl text-stone-800 leading-none">{{ yearTotal.toLocaleString() }}</div>
          <div class="mt-2 text-[10px] uppercase tracking-[0.25em] text-stone-500">
            張 · {{ activeMonths }}／12 月有照片
          </div>
        </div>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        <NuxtLink
          v-for="m in MONTHS"
          :key="m.key"
          :to="`/photos/${year}/${m.key}`"
          class="month-card"
          :class="countOf(m.key) === 0 && 'month-card--empty'"
        >
          <div class="month-card__top">
            <span class="month-card__num">{{ Number(m.key) }}</span>
            <span class="month-card__suffix">月</span>
          </div>
          <div class="month-card__name">{{ m.zh }}</div>
          <div class="month-card__rule"></div>
          <div class="month-card__stat">
            <span v-if="countOf(m.key) > 0" class="font-serif text-stone-800">
              {{ countOf(m.key).toLocaleString() }}
            </span>
            <span v-else class="text-stone-400">—</span>
            <span class="text-[10px] uppercase tracking-widest text-stone-500 ml-1">張</span>
          </div>
          <span class="month-card__arrow" aria-hidden="true">→</span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });

const route = useRoute();
const year = computed(() => String(route.params.year || ""));
useHead({ title: () => `${year.value} — 辰瑋相片` });

const MONTHS = [
  { key: "01", zh: "一月" }, { key: "02", zh: "二月" }, { key: "03", zh: "三月" },
  { key: "04", zh: "四月" }, { key: "05", zh: "五月" }, { key: "06", zh: "六月" },
  { key: "07", zh: "七月" }, { key: "08", zh: "八月" }, { key: "09", zh: "九月" },
  { key: "10", zh: "十月" }, { key: "11", zh: "十一月" }, { key: "12", zh: "十二月" },
];

const loading = ref(true);
const errMsg = ref("");
const months = ref<{ month: string; count: number }[]>([]);
const countOf = (m: string) => months.value.find((x) => x.month === m)?.count ?? 0;
const yearTotal = computed(() => months.value.reduce((a, b) => a + b.count, 0));
const activeMonths = computed(() => months.value.filter((m) => m.count > 0).length);

onMounted(async () => {
  try {
    const r = await authedFetch<{ months: { month: string; count: number }[] }>(
      `/api/photos/${year.value}/months`
    );
    months.value = r.months || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.month-card {
  position: relative;
  display: flex;
  flex-direction: column;
  aspect-ratio: 5 / 6;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 20px;
  padding: 18px 20px 20px;
  text-decoration: none;
  color: inherit;
  transition: transform .35s ease, box-shadow .35s ease, border-color .35s ease;
  overflow: hidden;
}
.month-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px -20px rgba(60, 30, 0, 0.18), 0 4px 12px -8px rgba(60, 30, 0, 0.1);
  border-color: rgb(168 162 158 / 0.9);
}
.month-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 100% 0%, rgba(217, 119, 6, 0.06), transparent 55%);
  pointer-events: none;
  opacity: 0;
  transition: opacity .4s ease;
}
.month-card:hover::before { opacity: 1; }

.month-card--empty {
  background: #f7f3eb;
  border-style: dashed;
}
.month-card--empty .month-card__num,
.month-card--empty .month-card__suffix {
  color: rgb(168 162 158);
}

.month-card__top {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.month-card__num {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: clamp(3rem, 7vw, 4.5rem);
  font-weight: 500;
  color: rgb(41 37 36);
  line-height: 0.85;
  letter-spacing: -0.03em;
}
.month-card__suffix {
  font-family: ui-serif, Georgia, serif;
  font-size: 1.05rem;
  color: rgb(87 83 78);
}
.month-card__name {
  margin-top: 4px;
  font-size: 11px;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgb(120 113 108);
}
.month-card__rule {
  width: 24px;
  height: 1px;
  background: rgb(120 113 108);
  margin: 14px 0 12px;
  transition: width .35s ease;
}
.month-card:hover .month-card__rule { width: 44px; }
.month-card__stat {
  display: flex;
  align-items: baseline;
  margin-top: auto;
  font-size: 1.05rem;
}
.month-card__arrow {
  position: absolute;
  bottom: 18px;
  right: 20px;
  color: rgb(120 113 108);
  font-size: 18px;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .3s ease, transform .3s ease;
}
.month-card:hover .month-card__arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
