<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="參考書目與館藏清單" :back="{ to: '/research-data/pct', label: '長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">參考書目與館藏清單</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          三份清單：華藝的期刊論文書目、國家圖書館「臺灣博碩士論文加值系統」的學位論文，
          以及「臺灣記憶」的臺灣基督長老教會文獻館藏目錄。最後一份對應長老教會歷史檔案館
          （與南神黃彰輝紀念圖書館共構）——庫房閉架、須 2 個工作天前申請、每人每次限 10 件，
          所以到館前必須先用目次選好件。
        </p>
      </div>

      <div class="flex gap-1 mb-6 border-b border-gray-200">
        <button v-for="t in tabs" :key="t.key" @click="tab = t.key"
          class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition"
          :class="tab === t.key ? 'border-sky-500 text-sky-700' : 'border-transparent text-gray-500 hover:text-gray-800'">
          {{ t.label }}<span class="ml-1.5 text-xs text-gray-400">{{ t.count }}</span>
        </button>
      </div>

      <!-- 華藝書目 -->
      <div v-show="tab === 'biblio'">
        <div v-if="!biblio.length" class="py-16 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中…' }}</div>
        <section v-for="g in biblio" :key="g.query" class="mb-6">
          <div class="flex items-baseline gap-2 mb-2">
            <h2 class="text-sm font-bold text-gray-900">{{ g.query }}</h2>
            <span class="text-xs text-gray-400">{{ g.note }}</span>
            <span v-if="g.truncated" class="text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">已達抓取上限，站上還有更多</span>
            <span class="ml-auto text-xs text-gray-400">{{ g.count }} 筆</span>
          </div>
          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div v-for="(it, i) in g.items" :key="i" class="px-4 py-2.5">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded"
                  :class="it.kind === '學位論文' ? 'bg-violet-50 text-violet-700' : 'bg-sky-50 text-sky-700'">{{ it.kind }}</span>
                <span class="flex-1 text-gray-800 break-words">{{ it.title }}</span>
              </div>
              <div class="mt-0.5 text-xs text-gray-500 break-words">{{ it.author }}　{{ it.source }}</div>
            </div>
          </div>
        </section>
      </div>

      <!-- 臺灣博碩士論文 -->
      <div v-show="tab === 'ndltd'">
        <p class="mb-3 text-xs text-gray-500 bg-gray-50 border border-gray-100 rounded-lg px-3 py-2 leading-relaxed">
          國家圖書館「臺灣博碩士論文加值系統」。系統的記錄連結帶 session 代碼會過期，故此處只留書目；
          要調閱時以論文名稱回站上重查即可。標「電子全文」者站上可直接下載。
        </p>
        <div v-if="!ndltd.length" class="py-16 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中…' }}</div>
        <section v-for="g in ndltd" :key="g.query" class="mb-6">
          <div class="flex items-baseline gap-2 mb-2">
            <h2 class="text-sm font-bold text-gray-900">{{ g.query }}</h2>
            <span class="text-xs text-gray-400">{{ g.note }}</span>
            <span v-if="g.truncated && g.total" class="text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">已達抓取上限，站上共 {{ g.total }} 筆</span>
            <span class="ml-auto text-xs text-gray-400">{{ g.count }} 筆</span>
          </div>
          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div v-for="(it, i) in g.items" :key="i" class="px-4 py-2.5">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded"
                  :class="it.degree === '博士' ? 'bg-rose-50 text-rose-700' : 'bg-violet-50 text-violet-700'">{{ it.degree || '學位論文' }}</span>
                <span class="flex-1 text-gray-800 break-words">{{ it.title }}</span>
                <span v-if="it.fulltext" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700">電子全文</span>
              </div>
              <div class="mt-0.5 text-xs text-gray-500 break-words">
                {{ it.author }}<template v-if="it.advisor">　指導：{{ it.advisor }}</template>　{{ it.school }}／{{ it.dept }}／{{ it.year }}
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 臺灣記憶館藏 -->
      <div v-show="tab === 'tm'">
        <p class="mb-3 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 leading-relaxed">
          444 件全部標記「不開放授權」，此處只收書目與目次、未取數位影像。目次帶原書頁碼，
          實體調閱請循歷史檔案館的申請程序（06-2356360，週一至五 9:00–12:00、13:00–17:00）。
        </p>
        <div class="mb-4 flex flex-wrap gap-2 items-center">
          <input v-model="q" type="search" placeholder="搜尋題名（例：議事錄、南部大會、聖詩、白話字）"
            class="flex-1 min-w-[16rem] px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-sky-400" />
          <button v-for="c in cats" :key="c.key" @click="cat = cat === c.key ? '' : c.key"
            :class="['px-2.5 py-1 rounded-full text-xs border transition',
                     cat === c.key ? 'bg-sky-600 text-white border-sky-600' : 'bg-white text-gray-600 border-gray-200 hover:border-sky-300']">
            {{ c.label }}<span class="ml-1 opacity-60">{{ c.n }}</span>
          </button>
        </div>
        <p class="mb-2 text-xs text-gray-400">{{ shownTm.length.toLocaleString() }} / {{ tm.length.toLocaleString() }} 件</p>
        <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
          <div v-for="r in pagedTm" :key="r.uniID" class="px-4 py-2.5">
            <div class="flex items-baseline gap-2 text-sm">
              <span class="flex-1 text-gray-800 break-words">{{ r.title }}</span>
              <span class="flex-shrink-0 text-xs text-gray-400 font-mono">{{ r.accessionNo }}</span>
              <a :href="r.url" target="_blank" rel="noopener"
                class="flex-shrink-0 text-xs font-medium text-sky-700 hover:underline no-underline">臺灣記憶 ↗</a>
            </div>
            <div v-if="r.toc?.length" class="mt-1">
              <button @click="openToc = openToc === r.uniID ? '' : r.uniID"
                class="text-xs text-gray-500 hover:text-sky-700">
                目次 {{ r.toc.length }} 條<span v-if="r.imageCount"> ‧ 影像 {{ r.imageCount }} 張</span>
                <span class="ml-1">{{ openToc === r.uniID ? '▲' : '▼' }}</span>
              </button>
              <ol v-if="openToc === r.uniID"
                class="mt-1.5 pl-4 space-y-0.5 text-xs text-gray-600 list-decimal marker:text-gray-300">
                <li v-for="(t, i) in r.toc" :key="i" class="break-words">{{ t }}</li>
              </ol>
            </div>
          </div>
          <div v-if="pagedTm.length < shownTm.length" class="px-4 py-3 text-center">
            <button @click="limit += 100" class="text-xs text-sky-600 hover:underline">
              顯示更多（{{ pagedTm.length }} / {{ shownTm.length }}）
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '參考書目與館藏清單 — 台灣基督長老教會研究資料' });

interface BiblioItem { kind: string; title: string; author: string; source: string }
interface BiblioGroup { query: string; note: string; url: string; count: number; truncated?: boolean; items: BiblioItem[] }
interface TmRow { uniID: string; title: string; accessionNo: string; url: string; toc?: string[]; imageCount?: number }
interface NdltdItem { title: string; author: string; advisor: string; school: string; dept: string; year: string; degree: string; fulltext: boolean }
interface NdltdGroup { query: string; note: string; count: number; total?: number; truncated?: boolean; items: NdltdItem[] }

const biblio = ref<BiblioGroup[]>([]);
const ndltd = ref<NdltdGroup[]>([]);
const tm = ref<TmRow[]>([]);
const loaded = ref(false);
const tab = ref<'biblio' | 'ndltd' | 'tm'>('biblio');
const q = ref('');
const cat = ref('');
const limit = ref(100);
const openToc = ref('');

// 依題名關鍵字分類——臺灣記憶的後設資料沒有細分類，只有「圖書／刊物」
const CATS: { key: string; label: string; re: RegExp }[] = [
  { key: 'minutes', label: '議事錄', re: /議事錄|記錄|會議|大會|中會|小會/ },
  { key: 'history', label: '教會史', re: /紀念|沿革|史|百年|設教/ },
  { key: 'hymn', label: '聖詩聖經', re: /聖詩|詩|聖經|神詩|琴譜/ },
  { key: 'roster', label: '名冊', re: /名冊|洗禮|信徒|會員/ },
  { key: 'press', label: '報刊', re: /公報|報|月刊|雜誌/ },
];
const cats = computed(() => CATS.map(c => ({ ...c, n: tm.value.filter(r => c.re.test(r.title)).length })));

const shownTm = computed(() => {
  const term = q.value.trim();
  const c = CATS.find(x => x.key === cat.value);
  return tm.value.filter(r =>
    (!term || r.title.includes(term)) && (!c || c.re.test(r.title)));
});
const pagedTm = computed(() => shownTm.value.slice(0, limit.value));
watch([q, cat], () => { limit.value = 100; });

const tabs = computed(() => [
  { key: 'biblio' as const, label: '華藝期刊書目', count: biblio.value.reduce((s, g) => s + g.count, 0) },
  { key: 'ndltd' as const, label: '臺灣博碩士論文', count: ndltd.value.reduce((s, g) => s + g.count, 0) },
  { key: 'tm' as const, label: '臺灣記憶館藏', count: tm.value.length },
]);

onMounted(async () => {
  const load = async (url: string) => {
    try { const r = await fetch(url); return r.ok ? await r.json() : []; } catch { return []; }
  };
  biblio.value = await load('/content/research-data/pct/biblio-airiti.json');
  ndltd.value = await load('/content/research-data/pct/biblio-ndltd.json');
  tm.value = await load('/content/research-data/pct/tm-presbyterian-index.json');
  loaded.value = true;
});
</script>
