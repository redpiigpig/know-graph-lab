<template>
  <div class="min-h-screen bg-[#f4f7f5] text-slate-900">
    <AppHeader title="旅遊日誌" :back="{ to: '/', label: '返回主頁' }" />

    <main class="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
      <header class="mb-9 sm:mb-12">
        <p class="mb-3 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-700">Travel Journal</p>
        <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 class="font-serif text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">旅遊日誌</h1>
            <p class="mt-3 max-w-xl text-sm leading-7 text-slate-500 sm:text-base">
              把出發前的路線、途中需要的資訊，和回家後想留下的記憶放在一起。
            </p>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-400">
            <span class="h-2 w-2 rounded-full bg-emerald-500" />
            {{ tripCount }} 趟旅程
          </div>
        </div>
      </header>

      <section aria-label="旅程列表" class="grid gap-6 lg:grid-cols-2">
        <NuxtLink
          :to="`/travel/${trip.slug}`"
          class="trip-card group overflow-hidden rounded-[28px] border border-white/70 bg-white no-underline shadow-sm"
        >
          <div class="relative min-h-[260px] overflow-hidden bg-[#123c35] p-7 text-white sm:p-9">
            <div class="absolute inset-0 opacity-70" aria-hidden="true">
              <div class="absolute -right-16 -top-20 h-56 w-56 rounded-full border-[42px] border-emerald-300/20" />
              <div class="absolute -bottom-24 left-1/3 h-60 w-60 rounded-full bg-amber-200/10 blur-2xl" />
              <svg viewBox="0 0 560 260" class="absolute inset-0 h-full w-full" preserveAspectRatio="none">
                <path d="M-20 230 C 80 140, 135 210, 215 125 S 390 70, 590 12" fill="none" stroke="rgba(255,255,255,.13)" stroke-width="2" stroke-dasharray="7 8" />
              </svg>
            </div>

            <div class="relative flex h-full min-h-[204px] flex-col justify-between">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-100/75">{{ trip.eyebrow }}</div>
                  <h2 class="mt-3 font-serif text-3xl font-semibold tracking-tight sm:text-4xl">{{ trip.title }}</h2>
                </div>
                <span class="rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur">
                  {{ tripStatus }}
                </span>
              </div>

              <div>
                <div class="mb-5 flex items-center gap-2 text-2xl" aria-label="新加坡、馬來西亞、泰國">
                  <span>🇸🇬</span><span class="text-white/30">·</span><span>🇲🇾</span><span class="text-white/30">·</span><span>🇹🇭</span>
                </div>
                <div class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-emerald-50/80">
                  <span>{{ trip.dateLabel }}</span>
                  <span class="hidden h-3 w-px bg-white/25 sm:block" />
                  <span>{{ trip.duration }}</span>
                  <span class="ml-auto flex items-center gap-2 font-medium text-white transition group-hover:translate-x-1">
                    打開旅程 <span aria-hidden="true">→</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="grid gap-5 p-6 sm:grid-cols-[1fr_auto] sm:items-center sm:px-8">
            <div>
              <div class="mb-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Route</div>
              <div class="flex flex-wrap items-center gap-1.5 text-sm font-medium text-slate-700">
                <template v-for="(stop, index) in trip.route" :key="`${stop}-${index}`">
                  <span>{{ stop }}</span>
                  <span v-if="index < trip.route.length - 1" class="text-slate-300">→</span>
                </template>
              </div>
            </div>
            <div class="flex gap-2 sm:justify-end">
              <span class="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700">8 日行程</span>
              <span class="rounded-full bg-sky-50 px-3 py-1.5 text-xs font-medium text-sky-700">交通整理</span>
            </div>
          </div>
        </NuxtLink>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { southeastAsiaTrip2026 as trip } from '~/data/travel'

definePageMeta({ middleware: 'auth' })
useHead({ title: '旅遊日誌 — Know Graph Lab' })

const tripCount = 1
const tripStatus = computed(() => {
  const today = new Date()
  const start = new Date(`${trip.startDate}T00:00:00+08:00`)
  const end = new Date(`${trip.endDate}T23:59:59+08:00`)
  if (today > end) return '旅程完成'
  if (today >= start) return '旅途中'
  const days = Math.ceil((start.getTime() - today.getTime()) / 86_400_000)
  return days > 0 ? `還有 ${days} 天` : '即將出發'
})
</script>

<style scoped>
.trip-card {
  color: inherit;
  transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
}
.trip-card:hover {
  transform: translateY(-4px);
  border-color: rgb(167 243 208 / .8);
  box-shadow: 0 28px 60px -34px rgba(6, 78, 59, .5);
}
</style>
