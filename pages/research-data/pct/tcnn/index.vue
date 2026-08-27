<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="台灣教會公報新聞網" :back="{ to: '/research-data/pct', label: '長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣教會公報社</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣教會公報新聞網</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          公報社新聞網（TCNN）逐篇全文。站上最早一篇為 2010 年 12 月；1885–2007 年的紙本掃描須向公報社索取，
          2008 至 2010 年間目前無免費線上來源。
          <span v-if="years.length" class="text-gray-400">收錄 {{ years.length }} 個年度、共 {{ totalCount.toLocaleString() }} 篇。</span>
        </p>
      </div>

      <!-- 年度 -->
      <div class="flex flex-wrap gap-1.5 mb-6">
        <button v-for="y in years" :key="y.year" @click="select(y.year)"
          :class="['px-3 py-1.5 rounded-lg text-xs border transition',
                   activeYear === y.year ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300']">
          {{ y.year }}<span class="ml-1 opacity-60">{{ y.count }}</span>
        </button>
      </div>

      <div v-if="activeYear" class="mb-4">
        <input v-model="q" type="search" placeholder="在本年度篇名中搜尋（例：昭慧、廢死、同志、核四）"
          class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-blue-400" />
        <p class="mt-1.5 text-xs text-gray-400">{{ activeYear }} 年 {{ filtered.length.toLocaleString() }} 篇{{ q ? '符合' : '' }}</p>
      </div>

      <div v-if="listLoading" class="py-16 text-center text-sm text-gray-400">載入 {{ activeYear }} 年篇目⋯</div>

      <div v-else-if="filtered.length" class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
        <div v-for="a in paged" :key="a.id" class="px-4 py-2.5">
          <div class="flex items-baseline gap-2 text-sm">
            <span class="flex-shrink-0 text-xs text-gray-400 font-mono">{{ a.date.slice(5) }}</span>
            <span class="flex-1 text-gray-800 break-words">{{ a.title }}</span>
            <button @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-blue-600">
              {{ states[a.id]?.open ? '收合' : '全文' }}
            </button>
            <a :href="a.link" target="_blank" rel="noopener" class="flex-shrink-0 text-xs font-medium text-blue-700 hover:underline no-underline">原文 ↗</a>
          </div>
          <div v-if="states[a.id]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
            <div v-if="states[a.id].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
            <pre v-else-if="states[a.id].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.id].text }}</pre>
            <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
          </div>
        </div>

        <div v-if="paged.length < filtered.length" class="px-4 py-3 text-center">
          <button @click="limit += 200" class="text-xs text-blue-600 hover:underline">
            顯示更多（已顯示 {{ paged.length }} / {{ filtered.length }}）
          </button>
        </div>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ activeYear ? '此年度沒有符合的篇目。' : (loaded ? '請選擇年度。' : '載入中…') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣教會公報新聞網 — 台灣基督長老教會研究資料' });

interface YearRow { year: string; count: number; chars: number }
interface Article { id: number; date: string; title: string; link: string }

const years = ref<YearRow[]>([]);
const loaded = ref(false);
const activeYear = ref('');
const list = ref<Article[]>([]);
const listLoading = ref(false);
const q = ref('');
const limit = ref(200);

const totalCount = computed(() => years.value.reduce((s, y) => s + y.count, 0));
const filtered = computed(() => {
  const term = q.value.trim();
  return term ? list.value.filter(a => a.title.includes(term)) : list.value;
});
const paged = computed(() => filtered.value.slice(0, limit.value));
watch([activeYear, q], () => { limit.value = 200; });

async function select(year: string) {
  if (activeYear.value === year) { activeYear.value = ''; list.value = []; return; }
  activeYear.value = year;
  listLoading.value = true;
  try {
    const r = await $fetch<{ available: boolean; articles: Article[] }>(
      '/api/research-data/pct-tcnn-text', { query: { year } });
    list.value = r.available ? r.articles : [];
  } catch { list.value = []; } finally { listLoading.value = false; }
}

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<number, TextState>>({});
async function toggle(a: Article) {
  let st = states[a.id];
  if (!st) st = states[a.id] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await $fetch<{ available: boolean; text: string | null }>(
        '/api/research-data/pct-tcnn-text', { query: { year: activeYear.value, id: a.id } });
      st.text = r.available ? (r.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/pct/tcnn-index.json');
    if (r.ok) years.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
