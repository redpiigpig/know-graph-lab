<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="期刊與報紙" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">期刊與報紙</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          刊物本位的一層，與教派／運動本位的「論文資料整理」平行且互相指涉：
          那邊按刊物屬於哪個教派或運動歸戶，這邊按它是什麼刊物排列，做政教關係史的媒體軸。
          同一份刊物兩邊各出現一次，互相連結，不搬家。
        </p>
      </div>

      <!-- 三級的差別很大，講在最前面：不標的話「N 篇」看起來會像全文都在 -->
      <div class="mb-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div v-for="t in (['full', 'index', 'guide'] as PressTier[])" :key="t"
          class="rounded-xl border p-3" :class="tierBox[t]">
          <div class="flex items-center gap-1.5 mb-1">
            <span class="text-xs font-bold px-1.5 py-0.5 rounded" :class="tierBadge[t]">{{ TIER_LABEL[t] }}</span>
            <span class="text-[11px] text-gray-400">{{ countOf(t) }} 份</span>
          </div>
          <p class="text-[11px] text-gray-500 leading-relaxed">{{ TIER_DESC[t] }}</p>
        </div>
      </div>

      <section v-for="g in PRESS_GROUPS" :key="g.key" class="mb-10">
        <div class="mb-3">
          <h2 class="text-base font-bold text-gray-900">{{ g.title }}</h2>
          <p class="text-xs text-gray-400 mt-0.5">{{ g.desc }}</p>
        </div>

        <div class="space-y-3">
          <!-- 卡片本身是 div：外部連結是 <a>，包在 NuxtLink 裡會變成連結包連結（HTML 不合法） -->
          <div v-for="p in g.items" :key="p.slug"
            class="bg-white rounded-xl border border-gray-100 p-4">

            <div class="flex flex-wrap items-baseline gap-2 mb-1">
              <h3 class="text-sm font-semibold text-gray-900">{{ p.name }}</h3>
              <span class="text-xs font-bold px-1.5 py-0.5 rounded" :class="tierBadge[p.tier]">{{ TIER_LABEL[p.tier] }}</span>
              <span class="text-[11px] text-gray-400 font-mono">{{ p.start }}–{{ p.end ?? '' }}</span>
              <span v-if="p.holdings" class="ml-auto text-xs font-medium text-gray-600">{{ p.holdings }}</span>
            </div>

            <p v-if="p.aka?.length" class="text-[11px] text-gray-400 mb-1">
              並稱／舊名：{{ p.aka.join('、') }}
            </p>
            <p class="text-[11px] text-gray-400 mb-1.5">{{ p.publisher }}</p>
            <p class="text-xs text-gray-600 leading-relaxed break-words">{{ p.note }}</p>

            <div class="mt-2 flex flex-wrap gap-3 text-xs">
              <NuxtLink v-if="p.to" :to="p.to" class="text-blue-600 hover:underline no-underline">
                {{ p.tier === 'full' ? '站內全文' : '站內篇目' }} →
              </NuxtLink>
              <a v-if="p.external" :href="p.external.url" target="_blank" rel="noopener"
                class="text-gray-500 hover:underline no-underline">{{ p.external.label }} ↗</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PRESS_GROUPS, TIER_LABEL, TIER_DESC, type PressTier } from '~/data/press';

definePageMeta({ middleware: 'auth' });
useHead({ title: '期刊與報紙 — 論文資料整理' });

const tierBadge: Record<PressTier, string> = {
  full: 'bg-emerald-100 text-emerald-700',
  index: 'bg-amber-100 text-amber-700',
  guide: 'bg-gray-100 text-gray-500',
};
const tierBox: Record<PressTier, string> = {
  full: 'bg-emerald-50/50 border-emerald-100',
  index: 'bg-amber-50/50 border-amber-100',
  guide: 'bg-gray-50 border-gray-200',
};

const countOf = (t: PressTier) =>
  PRESS_GROUPS.reduce((s, g) => s + g.items.filter(p => p.tier === t).length, 0);
</script>
