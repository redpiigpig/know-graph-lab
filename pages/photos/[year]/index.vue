<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/photos" class="text-sm text-gray-500 hover:text-gray-900 transition">← 全部年份</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-6xl mx-auto px-6 py-10">
      <nav class="text-xs text-gray-500 mb-3">
        <NuxtLink to="/photos" class="hover:text-gray-900">照片管理</NuxtLink>
        <span class="mx-1">/</span>
        <span class="text-gray-900">{{ year }}</span>
      </nav>
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-0.5">{{ year }} 年</h1>
        <p class="text-gray-500 text-sm">選擇月份</p>
      </div>

      <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>

      <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
        <NuxtLink
          v-for="m in MONTHS"
          :key="m"
          :to="`/photos/${year}/${m}`"
          class="block bg-white border-2 rounded-xl px-3 py-5 text-center transition-all hover:shadow-md hover:-translate-y-0.5"
          :class="countOf(m) > 0
            ? 'border-pink-100 hover:border-pink-300'
            : 'border-gray-100 hover:border-gray-300 opacity-70'"
        >
          <div class="text-lg font-semibold text-gray-800">{{ Number(m) }} 月</div>
          <div class="mt-0.5 text-xs"
               :class="countOf(m) > 0 ? 'text-pink-600' : 'text-gray-400'">
            {{ countOf(m) }} 張
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
useHead({ title: () => `${year.value} 年 — 照片管理` });

const MONTHS = ["01","02","03","04","05","06","07","08","09","10","11","12"] as const;

const loading = ref(true);
const errMsg = ref("");
const months = ref<{ month: string; count: number }[]>([]);
const countOf = (m: string) => months.value.find((x) => x.month === m)?.count ?? 0;

onMounted(async () => {
  try {
    const r = await authedFetch<{ months: { month: string; count: number }[] }>(`/api/photos/${year.value}/months`);
    months.value = r.months || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
</script>
