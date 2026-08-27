<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="妙心雜誌" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-orange-100 text-orange-700">研究資料</span>
          <span class="text-xs text-gray-400">台南妙心寺</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">妙心雜誌</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          台南妙心寺雙月刊，民國85年（1996）創刊。傳道法師以此為人間佛教在地實踐的發聲處：《法句經講記》全篇連載於此，
          另有台灣佛教、自然生態、專題報導與傳道長老追思專輯等欄。全篇原為網站 HTML，此處收其全文。
          <span v-if="issues.length" class="text-gray-400">收錄第 {{ minIssue }}–{{ maxIssue }} 期，共 {{ issues.length }} 期 {{ totalArticles }} 篇。</span>
        </p>
      </div>

      <div v-if="columns.length" class="mb-6 flex flex-wrap gap-1.5">
        <button v-for="c in columns" :key="c"
          @click="activeColumn = activeColumn === c ? '' : c"
          :class="['px-2.5 py-1 rounded-full text-xs border transition',
                   activeColumn === c ? 'bg-orange-600 text-white border-orange-600' : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300']">
          {{ c }}
        </button>
      </div>

      <div v-if="shown.length" class="space-y-3">
        <details v-for="it in shown" :key="it.issue" class="group bg-white rounded-xl border border-gray-100 overflow-hidden">
          <summary class="flex items-center gap-2 px-4 py-3 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-bold text-gray-900">第 {{ it.issue }} 期</span>
            <span class="ml-auto text-xs text-gray-400">{{ it.articles.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50 space-y-1">
            <div v-for="a in it.articles" :key="a.srcKey" class="py-1.5">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-1 text-gray-800 break-words">
                  {{ a.title }}
                  <span v-if="a.column" class="text-gray-400 text-xs">　{{ a.column }}</span>
                </span>
                <button @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-orange-600">
                  {{ states[a.srcKey]?.open ? '收合' : '全文' }}
                </button>
                <a v-if="a.source" :href="a.source" target="_blank" rel="noopener"
                  class="flex-shrink-0 text-xs font-medium text-orange-700 hover:underline no-underline">原頁 ↗</a>
              </div>
              <div v-if="states[a.srcKey]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[a.srcKey].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[a.srcKey].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.srcKey].text }}</pre>
                <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
              </div>
            </div>
          </div>
        </details>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '妙心雜誌 — 印順學派與弘誓研究資料' });

interface Article { title: string; column: string; srcKey: string; source: string }
interface Issue { issue: string; articles: Article[] }
const issues = ref<Issue[]>([]);
const loaded = ref(false);
const activeColumn = ref('');

const issueNo = (i: Issue) => Number(i.issue) || 0;
const minIssue = computed(() => issues.value.length ? Math.min(...issues.value.map(issueNo)) : 0);
const maxIssue = computed(() => issues.value.length ? Math.max(...issues.value.map(issueNo)) : 0);
const totalArticles = computed(() => issues.value.reduce((s, i) => s + i.articles.length, 0));

// 欄目清單依篇數多寡排，只留有名字的（舊期目次頁抓來的篇目沒有欄目）
const columns = computed(() => {
  const n: Record<string, number> = {};
  for (const it of issues.value) for (const a of it.articles) if (a.column) n[a.column] = (n[a.column] ?? 0) + 1;
  return Object.keys(n).sort((a, b) => n[b] - n[a]);
});

const shown = computed(() => {
  if (!activeColumn.value) return issues.value;
  return issues.value
    .map(it => ({ ...it, articles: it.articles.filter(a => a.column === activeColumn.value) }))
    .filter(it => it.articles.length);
});

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(a: Article) {
  let st = states[a.srcKey];
  if (!st) st = states[a.srcKey] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await $fetch<{ available: boolean; text: string | null }>(
        '/api/research-data/yinshun-hongshi-text', { query: { key: a.srcKey } });
      st.text = r.available ? (r.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/miaoxin-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
