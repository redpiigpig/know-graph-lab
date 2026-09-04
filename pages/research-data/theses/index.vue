<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="學位論文全文" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">研究資料</span>
          <span class="text-xs text-gray-400">各校機構典藏</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">學位論文全文</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          與本論文題目相關的碩博士學位論文，由各校機構典藏取得授權公開的 PDF，逐頁轉錄後供檢索。
          僅供研究參閱，引用請以各校典藏的原件為準。
        </p>
      </div>

      <div class="mb-4 flex flex-wrap gap-2 items-center">
        <input v-model="q" type="search" placeholder="在題名、作者、指導教授、校院中搜尋"
          class="flex-1 min-w-[16rem] px-3 py-1.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-teal-400" />
        <span class="text-xs text-gray-400">
          {{ shown.length }} / {{ index.count }} 本　{{ (index.chars || 0).toLocaleString() }} 字
        </span>
      </div>

      <div v-if="!index.items?.length" class="py-10 text-center text-sm text-gray-400">
        {{ loaded ? '尚未產出。' : '載入中…' }}
      </div>

      <div v-else class="space-y-3">
        <div v-for="t in shown" :key="t.id" class="bg-white rounded-xl border border-gray-100 p-4">
          <div class="flex flex-wrap items-baseline gap-2 mb-1">
            <h2 class="flex-1 text-sm font-semibold text-gray-900 break-words">{{ t.title }}</h2>
            <span v-if="t.scanned" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">
              疑為掃描版
            </span>
            <span class="flex-shrink-0 text-xs text-gray-400">{{ t.pages }} 頁 / {{ t.chars.toLocaleString() }} 字</span>
          </div>
          <div class="text-[11px] text-gray-400 break-words">
            {{ t.author }}<template v-if="t.advisor">　指導 {{ t.advisor }}</template>
            <template v-if="t.school">　{{ t.school }}{{ t.dept ? ' ' + t.dept : '' }}</template>
            <template v-if="t.year">　{{ t.year }}</template><template v-if="t.degree">　{{ t.degree }}</template>
          </div>
          <div class="mt-2 flex flex-wrap gap-3 items-center">
            <button @click="toggle(t.id)" class="text-xs text-teal-600 hover:underline">
              {{ open === t.id ? '收合全文' : '展開全文' }}
            </button>
            <a v-if="t.repoUrl" :href="t.repoUrl" target="_blank" rel="noopener"
              class="text-xs text-gray-400 hover:text-gray-600 hover:underline">機構典藏原件 ↗</a>
          </div>

          <div v-if="open === t.id" class="mt-3">
            <div v-if="loading" class="text-[11px] text-gray-400">載入全文⋯</div>
            <template v-else-if="pages.length">
              <input v-model="pq" type="search" placeholder="在本篇全文中找字"
                class="mb-2 w-full px-3 py-1.5 rounded-lg border border-gray-200 text-xs focus:outline-none focus:border-teal-400" />
              <div class="max-h-[36rem] overflow-auto rounded-lg bg-gray-50/70 border border-gray-100 divide-y divide-gray-100">
                <div v-for="p in pagesShown" :key="p.page" class="px-3 py-2">
                  <div class="text-[10px] text-gray-400 mb-0.5">第 {{ p.page }} 頁</div>
                  <pre class="text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans break-words">{{ p.text }}</pre>
                </div>
                <div v-if="!pagesShown.length" class="px-3 py-4 text-[11px] text-gray-400 text-center">
                  這篇裡找不到「{{ pq }}」。
                </div>
              </div>
            </template>
            <div v-else class="text-[11px] text-gray-400">取不到全文（需登入）。</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '學位論文全文 — 論文資料整理' });

interface Row {
  id: string; title: string; school: string; dept: string; author: string;
  advisor: string; year: string; degree: string; repoUrl: string;
  pages: number; chars: number; perPage: number; scanned: boolean;
}
const index = ref<{ count?: number; chars?: number; items?: Row[] }>({});
const loaded = ref(false);
const q = ref('');
const pq = ref('');
const open = ref('');
const pages = ref<{ page: number; text: string }[]>([]);
const loading = ref(false);

const shown = computed(() => {
  const rows = index.value.items ?? [];
  const t = q.value.trim();
  if (!t) return rows;
  return rows.filter(r => [r.title, r.author, r.advisor, r.school, r.dept]
    .some(v => (v || '').includes(t)));
});
const pagesShown = computed(() => {
  const t = pq.value.trim();
  return t ? pages.value.filter(p => p.text.includes(t)) : pages.value;
});

async function toggle(id: string) {
  if (open.value === id) { open.value = ''; return; }
  open.value = id; pages.value = []; pq.value = ''; loading.value = true;
  try {
    const r = await authedFetch<{ available: boolean; pages?: { page: number; text: string }[] }>(
      '/api/research-data/thesis-text', { query: { id } });
    pages.value = r.available ? (r.pages ?? []) : [];
  } catch { pages.value = []; } finally { loading.value = false; }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/pct/thesis-fulltext-index.json');
    if (r.ok) index.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
