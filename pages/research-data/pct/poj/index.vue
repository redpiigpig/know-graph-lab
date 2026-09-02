<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="白話字教會公報" :back="{ to: '/research-data/pct', label: '台灣基督長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣白話字文獻館（師大台文所）</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">白話字教會公報（1885–1969）</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          1885 年巴克禮創辦《台灣府城教會報》，歷經《台灣教會報》至《台灣教會公報》，
          八十四年間全以白話字書寫，1969 年改出華文。這一段補的是新聞網（2010-12 起）之前的空白，
          也是黃彰輝那一代之前長老教會公共發言的唯一底本。
          <span v-if="index.length" class="text-gray-400">
            收錄 {{ totalCount.toLocaleString() }} 篇、漢羅共 {{ totalChars.toLocaleString() }} 字。</span>
        </p>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed bg-amber-50/60 border border-amber-100 rounded-lg px-3 py-2">
          🚨 這是<strong>選輯，不是全份</strong>。中央研究院語言學研究所另有 1885–1969 逐頁掃描並輸入的
          完整閩語資料庫（數位典藏編號 LAMINTX0008），須另洽授權。
          本批文字採 CC 授權；原件圖片另屬台灣教會公報社等單位，故<strong>只收文字不收影像</strong>。
        </p>
      </div>

      <div class="flex flex-wrap gap-1.5 mb-6">
        <button v-for="d in index" :key="d.decade" @click="select(d.decade)"
          :class="['px-3 py-1.5 rounded-lg text-xs border transition',
                   active === d.decade ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300']">
          {{ d.decade === '未詳' ? '未詳' : `${d.decade}s` }}<span class="ml-1 opacity-60">{{ d.count }}</span>
        </button>
      </div>

      <div v-if="active" class="mb-4">
        <input v-model="q" type="search" placeholder="在本年代的篇名、白話字題名、作者、刊名中搜尋"
          class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-amber-400" />
        <p class="mt-1.5 text-xs text-gray-400">{{ active }} 年代 {{ filtered.length.toLocaleString() }} 篇{{ q ? '符合' : '' }}</p>
      </div>

      <div v-if="filtered.length" class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
        <div v-for="a in paged" :key="a.id" class="px-4 py-2.5">
          <div class="flex items-baseline gap-2 text-sm">
            <span class="flex-shrink-0 text-xs text-gray-400 font-mono">{{ a.date }}</span>
            <span class="flex-1 text-gray-800 break-words">
              {{ a.title }}
              <span v-if="a.titlePoj" class="text-xs text-gray-400 italic break-words">{{ a.titlePoj }}</span>
            </span>
            <span v-if="a.author" class="flex-shrink-0 text-xs text-gray-400 break-words">{{ a.author }}</span>
            <button @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-amber-600">
              {{ states[a.id]?.open ? '收合' : '全文' }}
            </button>
          </div>
          <div class="mt-0.5 text-[11px] text-gray-400">
            {{ a.mag }}<template v-if="a.issue">　{{ a.issue }}</template><template v-if="a.page">　頁 {{ a.page }}</template>
          </div>

          <div v-if="states[a.id]?.open" class="mt-1.5 rounded-lg border border-gray-100 bg-gray-50/70">
            <div v-if="states[a.id].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
            <template v-else-if="states[a.id].hanlo || states[a.id].tailo">
              <div class="flex gap-1.5 px-3 pt-2">
                <button v-for="m in modes" :key="m.key" @click="states[a.id].mode = m.key"
                  :class="['px-2 py-0.5 rounded text-[11px] border transition',
                           states[a.id].mode === m.key ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-gray-500 border-gray-200']">
                  {{ m.label }}
                </button>
              </div>
              <div v-if="states[a.id].mode === 'both'" class="grid grid-cols-1 md:grid-cols-2 gap-3 px-3 py-2">
                <pre class="text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.id].hanlo }}</pre>
                <pre class="text-[11px] leading-relaxed text-gray-600 whitespace-pre-wrap font-sans max-h-96 overflow-auto border-l border-gray-100 md:pl-3">{{ states[a.id].tailo }}</pre>
              </div>
              <pre v-else class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.id].mode === 'tailo' ? states[a.id].tailo : states[a.id].hanlo }}</pre>
            </template>
            <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
          </div>
        </div>

        <div v-if="paged.length < filtered.length" class="px-4 py-3 text-center">
          <button @click="limit += 200" class="text-xs text-amber-600 hover:underline">
            顯示更多（已顯示 {{ paged.length }} / {{ filtered.length }}）
          </button>
        </div>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ active ? '此年代沒有符合的篇目。' : (loaded ? '請選擇年代。' : '載入中…') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, reactive, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '白話字教會公報（1885–1969） — 台灣基督長老教會研究資料' });

interface DecadeRow { decade: string; count: number; chars: number }
interface Article {
  id: string; mag: string; date: string; issue: string; page: string;
  author: string; title: string; titlePoj: string; decade: string; chars: number;
}

const modes = [
  { key: 'hanlo', label: '漢羅' },
  { key: 'tailo', label: '台羅' },
  { key: 'both', label: '對照' },
] as const;

const index = ref<DecadeRow[]>([]);
const all = ref<Article[]>([]);
const loaded = ref(false);
const active = ref('');
const q = ref('');
const limit = ref(200);

const totalCount = computed(() => index.value.reduce((s, d) => s + d.count, 0));
const totalChars = computed(() => index.value.reduce((s, d) => s + d.chars, 0));

const filtered = computed(() => {
  if (!active.value) return [];
  const inDecade = all.value.filter(a => a.decade === active.value);
  const term = q.value.trim();
  if (!term) return inDecade;
  return inDecade.filter(a =>
    a.title.includes(term) || a.titlePoj.includes(term)
    || a.author.includes(term) || a.mag.includes(term));
});
const paged = computed(() => filtered.value.slice(0, limit.value));
watch([active, q], () => { limit.value = 200; });

function select(d: string) {
  active.value = active.value === d ? '' : d;
}

interface TextState { open: boolean; loading: boolean; loaded: boolean; hanlo: string; tailo: string; mode: string }
const states = reactive<Record<string, TextState>>({});
async function toggle(a: Article) {
  // 🚨 一定要「先寫入、再從 states 讀回來」。`st = states[id] = {...}` 這個賦值運算式
  //    回傳的是**原始物件**而不是 reactive 的 proxy，改它不會觸發重繪——
  //    症狀是按「全文」前兩下毫無反應、第三下才出現。
  if (!states[a.id]) states[a.id] = { open: false, loading: false, loaded: false, hanlo: '', tailo: '', mode: 'hanlo' };
  const st = states[a.id];
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await authedFetch<{ available: boolean; hanlo?: string; tailo?: string }>(
        '/api/research-data/pct-poj-text', { query: { decade: a.decade, id: a.id } });
      st.hanlo = r.available ? (r.hanlo ?? '') : '';
      st.tailo = r.available ? (r.tailo ?? '') : '';
    } catch { st.hanlo = ''; st.tailo = ''; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  const base = '/content/research-data/pct';
  try {
    const [i, a] = await Promise.all([fetch(`${base}/poj-index.json`), fetch(`${base}/poj-articles.json`)]);
    if (i.ok) index.value = await i.json();
    if (a.ok) all.value = await a.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
