<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/" class="text-sm text-gray-500 hover:text-gray-900 transition">← 首頁</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-6xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-0.5">照片管理</h1>
        <p class="text-gray-500 text-sm">辰瑋相片 — 依年份／月份瀏覽</p>
      </div>

      <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>
      <div v-else-if="!years.length" class="text-gray-400 text-sm">尚無年份資料夾</div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        <NuxtLink
          v-for="y in years"
          :key="y.year"
          :to="`/photos/${y.year}`"
          class="block bg-white border-2 border-gray-100 hover:border-pink-300 rounded-2xl px-4 py-6 text-center transition-all hover:shadow-md hover:-translate-y-0.5"
        >
          <div class="text-2xl font-bold text-gray-800">{{ y.year }}</div>
          <div class="mt-1 text-xs text-gray-500">{{ y.total }} 張</div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: "照片管理 — 知識圖工作室" });

const loading = ref(true);
const errMsg = ref("");
const years = ref<{ year: string; total: number }[]>([]);

onMounted(async () => {
  try {
    const r = await authedFetch<{ years: { year: string; total: number }[] }>("/api/photos/years");
    years.value = r.years || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
</script>
