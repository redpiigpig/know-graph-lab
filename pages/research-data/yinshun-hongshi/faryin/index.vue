<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="法印學報" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-cyan-100 text-cyan-700">研究資料</span>
          <span class="text-xs text-gray-400">佛教弘誓學院</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">法印學報</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          佛教弘誓學院學術期刊，2011 年創刊。弘誓官網改版後舊連結已失效，此處收錄的是玄奘大學佛教學系網站現存的第九～十三期。
          <span v-if="issues.length" class="text-gray-400">共 {{ issues.length }} 期 {{ totalArticles }} 篇，其中 {{ withText }} 篇有全文。</span>
        </p>
        <p v-if="brokenCount" class="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 leading-relaxed">
          有 {{ brokenCount }} 篇站方連結誤植為編輯者的本機路徑，原檔從未上傳，目前只存得下目次；需另向學團索取原檔。
        </p>
      </div>

      <div v-if="issues.length" class="space-y-3">
        <details v-for="it in issues" :key="it.issue" class="group bg-white rounded-xl border border-gray-100 overflow-hidden">
          <summary class="flex items-center gap-2 px-4 py-3 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-bold text-gray-900">第 {{ it.issue }} 期</span>
            <span class="ml-auto text-xs text-gray-400">{{ it.articles.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50 space-y-1">
            <div v-for="(a, ai) in it.articles" :key="ai" class="py-1.5">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-1 text-gray-800 break-words">
                  {{ a.title }}<span v-if="a.author" class="text-gray-400 text-xs">　{{ a.author }}</span>
                </span>
                <span v-if="a.note" class="flex-shrink-0 text-[11px] text-amber-600">原檔未上傳</span>
                <button v-if="a.hasFulltext" @click="toggle(a, ai)" class="flex-shrink-0 text-xs text-gray-400 hover:text-cyan-600">
                  {{ states[key(a, ai)]?.open ? '收合' : '全文' }}
                </button>
                <button type="button" v-if="a.pdfKey" @click="dl(a.pdfKey)"
                  class="flex-shrink-0 text-xs font-medium text-cyan-700 hover:underline no-underline">⬇ PDF</button>
              </div>
              <div v-if="states[key(a, ai)]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[key(a, ai)].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[key(a, ai)].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[key(a, ai)].text }}</pre>
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
import { authedDownload } from '~/composables/useAuthedDownload';
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '法印學報 — 印順學派與弘誓研究資料' });

interface Article { title: string; author: string; pdfKey: string; hasFulltext: boolean; note: string; source: string }
interface Issue { issue: string; title: string; articles: Article[] }
const issues = ref<Issue[]>([]);
const loaded = ref(false);
const totalArticles = computed(() => issues.value.reduce((s, i) => s + i.articles.length, 0));
const withText = computed(() => issues.value.reduce((s, i) => s + i.articles.filter(a => a.hasFulltext).length, 0));
const brokenCount = computed(() => issues.value.reduce((s, i) => s + i.articles.filter(a => a.note).length, 0));

// 壞連結那批沒有 pdfKey，用期號＋序位當狀態鍵才不會互相蓋掉
const key = (a: Article, i: number) => a.pdfKey || `x-${i}-${a.title}`;

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(a: Article, i: number) {
  const k = key(a, i);
  let st = states[k];
  if (!st) st = states[k] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await authedFetch<{ available: boolean; text: string | null }>(
        '/api/research-data/yinshun-hongshi-text', { query: { key: a.pdfKey } });
      st.text = r.available ? (r.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/faryin-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
// 端點加了 requireAdmin，`<a href>` 帶不了 Authorization header，
// 所以下載改走 authedFetch 取 blob（見 useAuthedDownload）。
async function dl(key: string) {
  await authedDownload(`/api/research-data/yinshun-hongshi-file?key=${encodeURIComponent(key)}&download=1`,
    key.split('/').pop() || 'download.pdf');
}
</script>
