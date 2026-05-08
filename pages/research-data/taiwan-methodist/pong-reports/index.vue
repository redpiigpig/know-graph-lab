<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist" class="text-gray-400 hover:text-gray-700 transition text-sm">← 台灣衛理公會研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">龐君華牧師歷年事工報告</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">

      <div class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-rose-100 text-rose-700">研究資料</span>
          <span class="text-xs text-gray-400">龐君華 牧師</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">龐君華牧師歷年事工報告</h1>
        <p class="text-sm text-gray-500">
          摘錄自年議會大會會議紀錄；按屆次分組（一屆可有多份報告）。共 {{ totalReports }} 份報告，{{ sessions.length }} 屆。
        </p>
      </div>

      <div class="space-y-8">
        <section v-for="s in sessions" :key="s.number">
          <div class="flex items-baseline gap-3 mb-3 pb-2 border-b border-gray-200">
            <h2 class="text-base font-semibold text-gray-900">第 {{ s.number }} 屆</h2>
            <span class="text-xs text-gray-500">{{ s.year }}</span>
            <span class="text-xs text-gray-400">{{ s.meetingTitle }}</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <NuxtLink
              v-for="r in s.reports" :key="r.id"
              :to="`/research-data/taiwan-methodist/pong-reports/${r.id}`"
              class="block p-4 bg-white rounded-2xl border border-gray-100 hover:border-rose-300 hover:shadow-md transition no-underline"
            >
              <div class="flex items-start justify-between gap-2 mb-1.5">
                <h3 class="text-sm font-semibold text-gray-900 leading-snug">{{ r.title }}</h3>
                <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-rose-50 text-rose-600 whitespace-nowrap">{{ r.authorRole }}</span>
              </div>
              <p v-if="r.unit" class="text-xs text-gray-500 mb-2">{{ r.unit }}</p>
              <p class="text-xs text-gray-400">頁 {{ r.sourcePages }}</p>
            </NuxtLink>
          </div>
        </section>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '龐君華牧師歷年事工報告 — Know Graph Lab' });

const { sessions } = usePongReports();
const totalReports = computed(() => sessions.reduce((n, s) => n + s.reports.length, 0));
</script>
