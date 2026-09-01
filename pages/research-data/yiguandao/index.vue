<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="一貫道研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-700">研究資料</span>
          <span class="text-xs text-gray-400">政教關係史的對照案例</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">一貫道研究資料</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          一貫道自 1930 年代起在中國被國民政府以「敵偽、附匪、邪教」取締，遷台後續遭查禁，
          直到 1987 年解嚴才合法化。它是「國家如何取締一個宗教」最完整的一條案例，
          與長老教會（被監控但未被查禁）恰成對照——兩者並置，政教關係的光譜才完整。
        </p>
      </div>

      <!-- 檔案局 -->
      <section class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <h2 class="text-base font-bold text-gray-900">國家檔案</h2>
          <span class="text-xs text-gray-400">檔案管理局‧國家檔案資訊網</span>
          <span v-if="archive.total" class="ml-auto text-xs text-gray-500">
            {{ archive.count }} 筆書目，其中 {{ archive.online }} 筆可線上閱覽
          </span>
        </div>

        <p class="mb-3 text-xs text-gray-500 bg-purple-50/60 border border-purple-100 rounded-lg px-3 py-2 leading-relaxed">
          🚨 <strong>「已數位化」不等於「可以下載」</strong>。多數條目標示「須提出申請」，
          須向檔案局申請調閱；只有標「可線上閱覽」的那一批能直接看。本站只收書目與提供方式，不取影像。
        </p>

        <div v-if="!archive.items.length" class="py-10 text-center text-sm text-gray-400">
          {{ loaded ? '尚未產出。' : '載入中…' }}
        </div>
        <div v-else>
          <div class="mb-3 flex flex-wrap gap-2 items-center">
            <button @click="onlyOnline = !onlyOnline"
              :class="['px-3 py-1.5 rounded-lg text-xs border transition',
                       onlyOnline ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200']">
              只看可線上閱覽
            </button>
            <input v-model="q" type="search" placeholder="在案由、全宗、摘要中搜尋（例：取締、邪教、考管）"
              class="flex-1 min-w-[16rem] px-3 py-1.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-purple-400" />
            <span class="text-xs text-gray-400">{{ shown.length.toLocaleString() }} 筆</span>
          </div>

          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div v-for="(a, i) in paged" :key="i" class="px-4 py-3">
              <div class="flex flex-wrap items-baseline gap-2">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded"
                  :class="a.level === '案' ? 'bg-emerald-50 text-emerald-700' : 'bg-sky-50 text-sky-700'">{{ a.level || '—' }}</span>
                <span class="flex-1 text-sm text-gray-800 break-words">{{ a.title }}</span>
                <span v-if="a.online" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-purple-50 text-purple-700">
                  可線上閱覽{{ a.pages ? ` ${a.pages} 頁` : '' }}
                </span>
                <span v-else class="flex-shrink-0 text-[11px] text-gray-400">須提出申請</span>
              </div>
              <div class="mt-0.5 text-[11px] text-gray-400 break-words">
                {{ a.fonds }}<template v-if="a.archiveNo">　檔號 {{ a.archiveNo }}</template>
              </div>
              <p v-if="a.summary" class="mt-1 text-xs text-gray-600 leading-relaxed break-words line-clamp-3">{{ a.summary }}</p>
            </div>
            <div v-if="paged.length < shown.length" class="px-4 py-3 text-center">
              <button @click="limit += 100" class="text-xs text-purple-600 hover:underline">
                顯示更多（已顯示 {{ paged.length }} / {{ shown.length }}）
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 引用書目 -->
      <section class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <h2 class="text-base font-bold text-gray-900">研究文獻</h2>
          <span v-if="biblio.count" class="ml-auto text-xs text-gray-500">{{ biblio.count }} 筆</span>
        </div>
        <p v-if="biblio.source" class="mb-3 text-xs text-gray-500 leading-relaxed">
          {{ biblio.source }}
          <span class="text-amber-700">標「待核」者為書頁照片判讀不確定的欄位，須核對原件。</span>
        </p>
        <div v-if="biblio.items?.length" class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
          <div v-for="(b, i) in biblio.items" :key="i" class="px-4 py-2.5">
            <div class="flex flex-wrap items-baseline gap-2 text-sm">
              <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ b.kind }}</span>
              <span class="flex-shrink-0 text-xs text-gray-400 font-mono">{{ b.year }}</span>
              <span class="flex-1 text-gray-800 break-words">{{ b.title }}</span>
              <span v-if="b.verify" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">待核</span>
            </div>
            <div class="mt-0.5 text-[11px] text-gray-400 break-words">
              {{ b.author }}<template v-if="b.container">　收於《{{ b.container }}》</template><template
                v-if="b.journal">　《{{ b.journal }}》{{ b.vol }}</template><template
                v-if="b.pub">　{{ b.pub }}</template><template v-if="b.pages">　{{ b.pages }}</template>
            </div>
            <p v-if="b.note" class="mt-0.5 text-[11px] text-amber-700 break-words">{{ b.note }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '一貫道研究資料 — 論文資料整理' });

interface ArchiveRow {
  level: string; title: string; fonds: string; archiveNo: string;
  access: string; online: boolean; pages: number; summary: string; subjects: string[];
}
interface BiblioRow {
  author: string; year: string; title: string; kind: string;
  container?: string; journal?: string; vol?: string; pub?: string;
  pages?: string; editor?: string; verify?: boolean; note?: string;
}

const archive = ref<{ total: number; count: number; online: number; items: ArchiveRow[] }>(
  { total: 0, count: 0, online: 0, items: [] });
const biblio = ref<{ source?: string; count?: number; items?: BiblioRow[] }>({});
const loaded = ref(false);
const onlyOnline = ref(false);
const q = ref('');
const limit = ref(100);

const shown = computed(() => {
  let rows = archive.value.items;
  if (onlyOnline.value) rows = rows.filter(a => a.online);
  const term = q.value.trim();
  if (!term) return rows;
  return rows.filter(a =>
    a.title.includes(term) || a.fonds.includes(term) || (a.summary || '').includes(term));
});
const paged = computed(() => shown.value.slice(0, limit.value));
watch([onlyOnline, q], () => { limit.value = 100; });

onMounted(async () => {
  const base = '/content/research-data/yiguandao';
  try {
    const [a, b] = await Promise.all([
      fetch(`${base}/archives-index.json`), fetch(`${base}/biblio-zhong.json`)]);
    if (a.ok) archive.value = await a.json();
    if (b.ok) biblio.value = await b.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
