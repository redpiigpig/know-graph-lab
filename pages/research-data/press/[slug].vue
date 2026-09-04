<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader :title="title" :back="{ to: '/research-data/press', label: '期刊與報紙' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex flex-wrap items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-violet-100 text-violet-700">篇目索引</span>
          <span v-if="meta?.publisher" class="text-xs text-gray-400 break-words">{{ meta.publisher }}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ title }}</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          {{ meta?.note }}
        </p>
        <p v-if="data" class="mt-2 text-xs text-gray-400 leading-relaxed">
          華藝線上圖書館收錄 {{ data.counts.卷期.toLocaleString() }} 期、{{ data.counts.篇目.toLocaleString() }} 篇，
          其中 {{ data.counts.有電子全文.toLocaleString() }} 篇有電子全文。
          🚨 這一層只有篇名、作者、卷期與頁碼，內文不在站內——要看全文請走玄奘圖書館的華藝訂閱。
        </p>
      </div>

      <div class="mb-5 flex flex-col sm:flex-row gap-3">
        <input v-model="q" type="search" placeholder="搜尋篇名或作者"
          class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-violet-400" />
        <select v-model="year" class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
          <option value="">全部年份</option>
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <p v-if="q || year" class="-mt-3 mb-4 text-xs text-gray-400">{{ matchCount.toLocaleString() }} 篇符合</p>

      <div v-if="shown.length" class="space-y-3">
        <details v-for="g in shown" :key="g.issueID" :open="!!q || shown.length === 1"
          class="group bg-white rounded-xl border border-gray-100 overflow-hidden">
          <summary class="flex items-center gap-2 px-4 py-3 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-bold text-gray-900 break-words">{{ g.label }}</span>
            <span class="ml-auto text-xs text-gray-400 flex-shrink-0">{{ g.articles.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50">
            <div v-for="a in g.articles" :key="a.docId" class="flex items-baseline gap-2 py-1.5 text-sm">
              <span class="flex-1 text-gray-800 break-words">
                {{ a.title }}
                <span v-if="a.authors.length" class="text-gray-400 text-xs">　{{ shortAuthors(a.authors) }}</span>
              </span>
              <span v-if="a.pages" class="flex-shrink-0 text-[11px] text-gray-400 font-mono">頁 {{ a.pages }}</span>
              <span v-if="a.fulltext" class="flex-shrink-0 text-[11px] text-emerald-600" title="華藝有電子全文">全文</span>
            </div>
          </div>
        </details>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ loaded ? (q || year ? '沒有符合的篇目。' : '尚未收錄篇目。') : '載入中…' }}
      </div>

      <p v-if="data" class="mt-8 text-xs text-gray-400">
        來源：<a :href="data.source" target="_blank" rel="noopener"
          class="text-violet-600 hover:underline no-underline">華藝線上圖書館 · {{ data.name }} ↗</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { PRESS_GROUPS } from '~/data/press';

definePageMeta({ middleware: 'auth' });

interface Article {
  docId: string; title: string; authors: string[];
  volIssue: string; date: string; pages: string;
  fulltext: boolean; issueLabel: string; issueID: string;
}
interface Toc {
  slug: string; pid: string; name: string; source: string;
  counts: { 卷期: number; 篇目: number; 有電子全文: number };
  issues: { issueID: string; label: string; year: string; count: number }[];
  articles: Article[];
}

const route = useRoute();
const slug = String(route.params.slug);
const meta = PRESS_GROUPS.flatMap(g => g.items).find(p => p.slug === slug);

const data = ref<Toc | null>(null);
const loaded = ref(false);
const q = ref('');
const year = ref('');

const title = computed(() => data.value?.name || meta?.name || '期刊篇目');
useHead(() => ({ title: `${title.value} — 期刊與報紙` }));

// 華藝的作者欄是「孫一信(I-Shin Shun)」，列表只留中文名，英文轉寫塞在括號裡佔位太兇
function shortAuthors(list: string[]) {
  return list.map(a => a.split('(')[0].trim()).filter(Boolean).join('、');
}

const years = computed(() => [...new Set((data.value?.issues ?? []).map(i => i.year))]);

const shown = computed(() => {
  const d = data.value;
  if (!d) return [];
  const term = q.value.trim();
  const byIssue = new Map<string, Article[]>();
  for (const a of d.articles) {
    if (term && !a.title.includes(term) && !a.authors.some(x => x.includes(term))) continue;
    if (!byIssue.has(a.issueID)) byIssue.set(a.issueID, []);
    byIssue.get(a.issueID)!.push(a);
  }
  // 卷期順序照華藝原序（新 → 舊），不自己重排：卷期標籤格式各刊不一，排序會排錯
  return d.issues
    .filter(i => !year.value || i.year === year.value)
    .map(i => ({ issueID: i.issueID, label: i.label, articles: byIssue.get(i.issueID) ?? [] }))
    .filter(g => g.articles.length);
});
const matchCount = computed(() => shown.value.reduce((s, g) => s + g.articles.length, 0));

onMounted(async () => {
  try {
    const r = await fetch(`/content/research-data/press/airiti/${slug}.json`);
    if (r.ok) data.value = await r.json();
  } catch { /* 讀不到就顯示「尚未收錄」，不要讓整頁掛掉 */ } finally { loaded.value = true; }
});
</script>
