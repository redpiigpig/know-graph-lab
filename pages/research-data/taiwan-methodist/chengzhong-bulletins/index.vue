<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist" class="text-gray-400 hover:text-gray-700 transition text-sm">← 台灣衛理公會研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">城中教會主日崇拜週報</span>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8">
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">研究資料</span>
          <span class="text-xs text-gray-400">中華基督教衛理公會城中教會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">城中教會主日崇拜週報</h1>
        <p class="text-sm text-gray-500">
          台北城中教會（城中牧區）歷年主日崇拜程序電子化整理，收錄節期、禮儀顏色、服事人員、證道題目、經課與聖詩。
          <span v-if="meta">共 {{ meta.total }} 份，{{ meta.years.length }} 個年度（{{ meta.years[0] }}–{{ meta.years[meta.years.length-1] }}）。</span>
        </p>
      </div>

      <!-- controls -->
      <div class="bg-white rounded-2xl border border-gray-100 p-4 mb-5 flex flex-col gap-3">
        <input v-model="q" type="text" placeholder="搜尋節期、證道題目、講員、日期…"
               class="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-400" />
        <div class="flex flex-wrap gap-1.5">
          <button @click="activeYear = null"
                  :class="['px-2.5 py-1 text-xs font-medium rounded-full border transition', activeYear === null ? 'bg-amber-600 border-amber-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-amber-300']">
            全部
          </button>
          <button v-for="y in (meta?.years || [])" :key="y" @click="activeYear = y"
                  :class="['px-2.5 py-1 text-xs font-medium rounded-full border transition', activeYear === y ? 'bg-amber-600 border-amber-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-amber-300']">
            {{ y }}
          </button>
        </div>
      </div>

      <div class="text-xs text-gray-400 mb-3">顯示 {{ filtered.length }} 份</div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <NuxtLink v-for="b in filtered" :key="b.slug"
                  :to="`/research-data/taiwan-methodist/chengzhong-bulletins/${b.slug}`"
                  class="block p-4 bg-white rounded-2xl border border-gray-100 hover:border-amber-300 hover:shadow-md transition no-underline">
          <div class="flex items-center justify-between gap-2 mb-1.5">
            <span class="text-xs font-mono text-gray-500">{{ b.date }}</span>
            <span class="flex items-center gap-1.5">
              <span v-if="b.service !== '主日崇拜'" class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">{{ b.service }}</span>
              <span v-if="b.color" class="w-3 h-3 rounded-full border" :style="{ background: colorHex(b.color) }" :title="b.color + '色'"></span>
            </span>
          </div>
          <div v-if="b.season" class="text-sm font-semibold text-gray-900 leading-snug mb-1">{{ b.season }}</div>
          <div v-if="b.sermon_title" class="text-xs text-amber-700 mb-1">講題：{{ b.sermon_title }}</div>
          <div v-if="b.preacher" class="text-xs text-gray-500">證道：{{ b.preacher }}</div>
        </NuxtLink>
      </div>

      <div v-if="!filtered.length" class="text-center text-gray-400 text-sm py-16">沒有符合的週報</div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '城中教會主日崇拜週報 — 台灣衛理公會研究資料' });

interface Item {
  date: string; service: string; season: string | null; color: string | null;
  preacher: string | null; presider: string | null; sermon_title: string | null;
  slug: string; year: string; n_scrip: number; n_hymn: number;
}
interface Meta { total: number; years: string[]; preachers: string[]; coverage: Record<string, number>; }

const { data } = await useFetch<{ meta: Meta; items: Item[] }>('/content/chengzhong-bulletins/index.json');
const meta = computed(() => data.value?.meta);
const items = computed<Item[]>(() => data.value?.items || []);

const q = ref('');
const activeYear = ref<string | null>(null);

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase();
  return items.value.filter((b) => {
    if (activeYear.value && b.year !== activeYear.value) return false;
    if (!kw) return true;
    return [b.date, b.season, b.sermon_title, b.preacher, b.presider, b.service]
      .filter(Boolean).join(' ').toLowerCase().includes(kw);
  });
});

const COLOR_HEX: Record<string, string> = {
  白: '#f8fafc', 紫: '#7c3aed', 綠: '#16a34a', 紅: '#dc2626',
  藍: '#2563eb', 金: '#d97706', 黑: '#1f2937',
};
function colorHex(c: string) { return COLOR_HEX[c] || '#e5e7eb'; }
</script>
