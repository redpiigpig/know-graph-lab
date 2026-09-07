<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="跨來源刊物對照" :back="{ to: '/research-data/press', label: '期刊與報紙' }" container-class="max-w-6xl" />

    <div class="max-w-6xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">跨來源刊物對照</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          同一份刊在三個資料庫各收多少篇目。做這張表的理由很實際：找《海潮音》的時候，
          華藝一筆都沒有、國圖 4,995 筆、臺大 26,220 筆——不並排看，
          就會在只有一個來源的地方翻半天，或者把「查不到」當成「不存在」。
        </p>
      </div>

      <div v-if="data" class="mb-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div v-for="(v, k) in data.counts" :key="k" class="rounded-xl border border-gray-100 bg-white p-3">
          <div class="text-lg font-bold text-gray-900">{{ v.toLocaleString() }}</div>
          <div class="text-[11px] text-gray-400 leading-tight break-words">{{ k }}</div>
        </div>
      </div>

      <!-- 三個來源補的洞不一樣，講在前面；不講的話會誤以為它們是重複的 -->
      <div class="mb-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div v-for="s in SOURCES" :key="s.key" class="rounded-xl border p-3" :class="s.box">
          <div class="flex items-center gap-1.5 mb-1">
            <span class="text-xs font-bold px-1.5 py-0.5 rounded" :class="s.badge">{{ s.label }}</span>
          </div>
          <p class="text-[11px] text-gray-500 leading-relaxed">{{ s.note }}</p>
        </div>
      </div>

      <div class="mb-4 flex flex-col sm:flex-row gap-3">
        <input v-model="q" type="search" placeholder="搜尋刊名（例：海潮音、南瀛、菩提樹）"
          class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-violet-400" />
        <select v-model="only" class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
          <option value="">全部來源</option>
          <option value="airiti">只看華藝有的</option>
          <option value="ncl">只看國圖有的</option>
          <option value="dlbs">只看臺大有的</option>
          <option value="multi">兩個以上來源都有</option>
        </select>
      </div>
      <p class="-mt-2 mb-4 text-xs text-gray-400">{{ shown.length.toLocaleString() }} 份刊</p>

      <div v-if="shown.length" class="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-[11px] text-gray-500">
              <tr>
                <th class="text-left font-medium px-4 py-2">刊名</th>
                <th class="text-right font-medium px-3 py-2 whitespace-nowrap">華藝</th>
                <th class="text-right font-medium px-3 py-2 whitespace-nowrap">國圖</th>
                <th class="text-right font-medium px-3 py-2 whitespace-nowrap">臺大佛圖</th>
                <th class="text-left font-medium px-3 py-2 whitespace-nowrap">年代</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="j in visible" :key="j.key" class="border-t border-gray-50">
                <td class="px-4 py-2">
                  <NuxtLink v-if="j.sources.airiti?.to" :to="j.sources.airiti.to"
                    class="text-violet-700 hover:underline no-underline break-words">{{ j.name }}</NuxtLink>
                  <span v-else class="text-gray-800 break-words">{{ j.name }}</span>
                </td>
                <td v-for="k in (['airiti', 'ncl', 'dlbs'] as const)" :key="k"
                  class="px-3 py-2 text-right tabular-nums"
                  :class="j.sources[k] ? 'text-gray-800' : 'text-gray-300'">
                  <template v-if="j.sources[k]">
                    {{ j.sources[k]!.articles.toLocaleString() }}
                    <span v-if="j.sources[k]!.fulltext" class="text-[10px] text-emerald-600">
                      /{{ j.sources[k]!.fulltext.toLocaleString() }}全文
                    </span>
                  </template>
                  <template v-else>—</template>
                </td>
                <td class="px-3 py-2 text-[11px] text-gray-400 whitespace-nowrap">
                  {{ span(j) }}
                  <!-- 來源端的年份筆誤：標出來但不改資料，否則逐年詞頻會被拉長幾十年 -->
                  <span v-if="outlierOf(j)" class="text-amber-600" :title="`來源端筆誤：${outlierOf(j)}`">⚠</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <button v-if="visible.length < shown.length" @click="limit += 100"
          class="w-full py-2.5 text-xs text-gray-500 hover:bg-gray-50 border-t border-gray-100">
          再顯示 100 份（還有 {{ (shown.length - visible.length).toLocaleString() }} 份）
        </button>
      </div>
      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ loaded ? '沒有符合的刊物。' : '載入中…' }}
      </div>

      <p v-if="data?.yearOutliers?.length" class="mt-6 text-xs text-gray-400 leading-relaxed">
        ⚠ 標記代表該刊的年代區間受來源端筆誤影響（{{ data.yearOutliers.length }} 份）。
        例：《人生》索引起始寫 1858，實際最早是 1935——1858 那一年只有 1 筆，
        下一個有資料的年份差了 77 年。**原始資料未修改**，只是標出來，
        免得逐年詞頻被一筆髒資料把橫軸拉長。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '跨來源刊物對照 — 期刊與報紙' });

interface Src { name: string; articles: number; fulltext: number; start: number | null; end: number | null; to?: string; realStart?: number }
interface Row { key: string; name: string; total: number; inSources: number; sources: Partial<Record<'airiti' | 'ncl' | 'dlbs', Src>> }
interface Data { counts: Record<string, number>; yearOutliers: { journal: string }[]; journals: Row[] }

const SOURCES = [
  { key: 'airiti', label: '華藝', badge: 'bg-violet-100 text-violet-700', box: 'bg-violet-50/50 border-violet-100',
    note: '有全文可下載，卷期頁碼齊；但綁玄奘機構 IP，且完全沒有戰後那批佛教老雜誌。' },
  { key: 'ncl', label: '國圖', badge: 'bg-sky-100 text-sky-700', box: 'bg-sky-50/50 border-sky-100',
    note: '卷期與頁碼零缺漏，部分 PDF 匿名可下載、不綁 IP；基督教側幾乎不收。' },
  { key: 'dlbs', label: '臺大佛圖', badge: 'bg-emerald-100 text-emerald-700', box: 'bg-emerald-50/50 border-emerald-100',
    note: '量最大（33 萬筆），開放取用；全文多半是掃描版，逐筆篇目存在 R2。' },
];

const data = ref<Data | null>(null);
const loaded = ref(false);
const q = ref('');
const only = ref('');
const limit = ref(100);

const shown = computed(() => {
  const rows = data.value?.journals ?? [];
  const term = q.value.trim();
  return rows.filter(r => {
    if (term && !r.name.includes(term) && !r.key.includes(term)) return false;
    if (only.value === 'multi') return r.inSources > 1;
    if (only.value) return !!r.sources[only.value as 'airiti'];
    return true;
  });
});
const visible = computed(() => shown.value.slice(0, limit.value));

// 年代取三邊的聯集；有離群的那一邊改用實際起始，不用被筆誤污染的那個
function span(j: Row) {
  const ss: number[] = [], es: number[] = [];
  for (const v of Object.values(j.sources)) {
    const s = v.realStart ?? v.start;
    if (typeof s === 'number') ss.push(s);
    if (typeof v.end === 'number') es.push(v.end);
  }
  if (!ss.length || !es.length) return '';
  return `${Math.min(...ss)}–${Math.max(...es)}`;
}
function outlierOf(j: Row) {
  const v = Object.values(j.sources).find(x => x.realStart);
  return v ? `索引寫 ${v.start}，實際 ${v.realStart}` : '';
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/press/sources-index.json');
    if (r.ok) data.value = await r.json();
  } catch { /* 讀不到就顯示載入中→無資料，不要讓整頁掛掉 */ } finally { loaded.value = true; }
});
</script>
