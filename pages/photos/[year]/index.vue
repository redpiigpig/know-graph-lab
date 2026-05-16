<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/photos" class="text-sm text-stone-500 hover:text-stone-900 transition">← 全部年份</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <nav class="text-[10px] uppercase tracking-[0.2em] text-stone-500 mb-2">
        <NuxtLink to="/photos" class="hover:text-stone-900">照片庫</NuxtLink>
        <span class="mx-2">/</span>
        <span class="text-stone-700">{{ year }}</span>
      </nav>

      <header class="mb-8 flex items-end justify-between flex-wrap gap-3 border-b border-stone-300/60 pb-4">
        <h1 class="font-serif text-4xl text-stone-900 leading-none tracking-tight">{{ year }}</h1>
        <div v-if="!loading" class="text-right font-serif">
          <div class="text-2xl text-stone-800 leading-none">{{ yearTotal.toLocaleString() }}</div>
          <div class="mt-1 text-[10px] uppercase tracking-[0.25em] text-stone-500">
            張 · {{ activeMonths }}／12 月
          </div>
        </div>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>

      <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
        <NuxtLink
          v-for="m in MONTHS"
          :key="m.key"
          :to="`/photos/${year}/${m.key}`"
          class="month-card"
          :class="countOf(m.key) === 0 && 'month-card--empty'"
        >
          <div class="flex items-baseline gap-1">
            <span class="month-card__num">{{ Number(m.key) }}</span>
            <span class="month-card__suffix">月</span>
          </div>
          <div class="mt-1 text-[10px] tracking-widest uppercase text-stone-500">
            <span v-if="countOf(m.key) > 0" class="text-stone-700">
              {{ countOf(m.key).toLocaleString() }}<span class="ml-1">張</span>
            </span>
            <span v-else>—</span>
          </div>
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
  { key: "01" }, { key: "02" }, { key: "03" }, { key: "04" },
  { key: "05" }, { key: "06" }, { key: "07" }, { key: "08" },
  { key: "09" }, { key: "10" }, { key: "11" }, { key: "12" },
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
  display: block;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 12px;
  padding: 10px 14px 12px;
  text-decoration: none;
  color: inherit;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.month-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px -14px rgba(60, 30, 0, 0.18);
  border-color: rgb(168 162 158 / 0.9);
}
.month-card--empty {
  background: #f7f3eb;
  border-style: dashed;
}
.month-card--empty .month-card__num,
.month-card--empty .month-card__suffix {
  color: rgb(168 162 158);
}
.month-card__num {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: 1.85rem;
  font-weight: 500;
  color: rgb(41 37 36);
  line-height: 1;
  letter-spacing: -0.02em;
}
.month-card__suffix {
  font-family: ui-serif, Georgia, serif;
  font-size: 0.85rem;
  color: rgb(87 83 78);
}
</style>
