<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="玄奘佛學研究學報" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-violet-100 text-violet-700">研究資料</span>
          <span class="text-xs text-gray-400">玄奘大學宗教與文化學系</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">玄奘佛學研究學報</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          玄奘大學宗教與文化學系暨臺灣佛教研究中心發行之學術期刊，人間佛教與臺灣佛教研究重鎮，昭慧法師、性廣法師等學者於此發表。每篇論文提供 PDF 與全文。
          <span v-if="issues.length" class="text-gray-400">收錄第 {{ minIssue }}–{{ maxIssue }} 期，共 {{ issues.length }} 期 {{ totalArticles }} 篇。</span>
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
                <span class="flex-1 text-gray-800 break-words">{{ a.title }}<span v-if="a.author" class="text-gray-400 text-xs">　{{ a.author }}</span></span>
                <button v-if="a.hasFulltext" @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-violet-600">{{ states[a.pdfKey]?.open ? '收合' : '全文' }}</button>
                <a :href="`/api/research-data/yinshun-hongshi-file?key=${encodeURIComponent(a.pdfKey)}&download=1`" class="flex-shrink-0 text-xs font-medium text-violet-700 hover:underline no-underline">⬇ PDF</a>
              </div>
              <div v-if="states[a.pdfKey]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[a.pdfKey].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[a.pdfKey].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.pdfKey].text }}</pre>
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
useHead({ title: '玄奘佛學研究學報 — 印順學派與弘誓研究資料' });

interface Article { title: string; author: string; pdfKey: string; hasFulltext: boolean }
interface Issue { issue: number; title: string; articles: Article[] }
const issues = ref<Issue[]>([]);
const loaded = ref(false);
const minIssue = computed(() => issues.value.length ? Math.min(...issues.value.map(i => i.issue)) : 0);
const maxIssue = computed(() => issues.value.length ? Math.max(...issues.value.map(i => i.issue)) : 0);
const totalArticles = computed(() => issues.value.reduce((s, i) => s + i.articles.length, 0));

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(a: Article) {
  let st = states[a.pdfKey];
  if (!st) st = states[a.pdfKey] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await $fetch<{ available: boolean; text: string | null }>(
        '/api/research-data/yinshun-hongshi-text', { query: { key: a.pdfKey } });
      st.text = r.available ? (r.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/xuanzang-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
