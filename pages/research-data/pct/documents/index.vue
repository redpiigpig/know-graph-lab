<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="總會重要文獻" :back="{ to: '/research-data/pct', label: '長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-rose-100 text-rose-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣基督長老教會總會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">總會重要文獻</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          三大聲明——1971〈對國是的聲明與建議〉、1975〈我們的呼籲〉、1977〈人權宣言〉——以及 1985 年〈信仰告白〉
          與歷年總會的牧函、宣言、請願書。博士論文第四章第一節「從自立到實況：公共性的體制條件」的直接文本。
          <span v-if="rows.length" class="text-gray-400">共 {{ rows.length }} 件，{{ minYear }}–{{ maxYear }}。</span>
        </p>
      </div>

      <div class="mb-5 flex flex-wrap gap-1.5">
        <button v-for="d in decades" :key="d" @click="activeDecade = activeDecade === d ? '' : d"
          :class="['px-2.5 py-1 rounded-full text-xs border transition',
                   activeDecade === d ? 'bg-rose-600 text-white border-rose-600' : 'bg-white text-gray-600 border-gray-200 hover:border-rose-300']">
          {{ d }}0 年代<span class="ml-1 opacity-60">{{ countIn(d) }}</span>
        </button>
      </div>

      <div v-if="shown.length" class="space-y-2">
        <article v-for="r in shown" :key="r.docId" class="bg-white rounded-xl border border-gray-100 px-4 py-3">
          <div class="flex items-baseline gap-2 text-sm">
            <span class="flex-shrink-0 text-xs text-gray-400 font-mono w-10">{{ r.year || '—' }}</span>
            <span class="flex-1 text-gray-800 break-words">{{ r.title }}</span>
            <span class="flex-shrink-0 text-xs text-gray-400">{{ r.chars.toLocaleString() }} 字</span>
            <button @click="toggle(r)" class="flex-shrink-0 text-xs text-gray-500 hover:text-rose-700">
              {{ states[r.docId]?.open ? '收合' : '全文' }}
            </button>
            <a :href="r.source" target="_blank" rel="noopener" class="flex-shrink-0 text-xs font-medium text-rose-700 hover:underline no-underline">原頁 ↗</a>
          </div>
          <div v-if="states[r.docId]?.open" class="mt-2 rounded-lg border border-gray-100 bg-gray-50/70">
            <div v-if="states[r.docId].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
            <pre v-else-if="states[r.docId].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-[32rem] overflow-auto">{{ states[r.docId].text }}</pre>
            <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
          </div>
        </article>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '總會重要文獻 — 台灣基督長老教會研究資料' });

interface Row { docId: string; title: string; year: string; chars: number; source: string; textKey: string }

const rows = ref<Row[]>([]);
const loaded = ref(false);
const activeDecade = ref('');

const years = computed(() => rows.value.map(r => r.year).filter(Boolean).sort());
const minYear = computed(() => years.value[0] ?? '');
const maxYear = computed(() => years.value[years.value.length - 1] ?? '');
const decadeOf = (r: Row) => (r.year ? r.year.slice(0, 3) : '');
const decades = computed(() => [...new Set(rows.value.map(decadeOf).filter(Boolean))].sort());
const countIn = (d: string) => rows.value.filter(r => decadeOf(r) === d).length;
const shown = computed(() => activeDecade.value ? rows.value.filter(r => decadeOf(r) === activeDecade.value) : rows.value);

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(r: Row) {
  let st = states[r.docId];
  if (!st) st = states[r.docId] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const res = await $fetch<{ available: boolean; text: string | null }>(
        '/api/research-data/pct-text', { query: { key: r.textKey } });
      st.text = res.available ? (res.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/pct/documents-index.json');
    if (r.ok) rows.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
