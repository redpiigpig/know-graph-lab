<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="新使者雜誌" :back="{ to: '/research-data/pct', label: '長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣基督長老教會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">新使者雜誌</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          長老教會青年刊物，1990 年創刊，逐篇全文取自教會「焚而不燬」信仰資源網。
          黃彰輝小傳、宋泉盛專題、王憲治與鄉土神學等本土神學論述多刊於此。
          <span v-if="issues.length" class="text-gray-400">收錄 {{ issues.length }} 期、共 {{ totalArticles.toLocaleString() }} 篇。</span>
        </p>
      </div>

      <div class="mb-5">
        <input v-model="q" type="search" placeholder="搜尋篇名或作者（例：黃彰輝、宋泉盛、鄉土神學）"
          class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
        <p v-if="q" class="mt-1.5 text-xs text-gray-400">{{ matchCount.toLocaleString() }} 篇符合</p>
      </div>

      <div v-if="shown.length" class="space-y-3">
        <details v-for="it in shown" :key="it.issue" :open="!!q" class="group bg-white rounded-xl border border-gray-100 overflow-hidden">
          <summary class="flex items-center gap-2 px-4 py-3 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-bold text-gray-900">第 {{ it.issue }} 期</span>
            <span class="text-xs text-gray-400 break-words">{{ issueSubtitle(it) }}</span>
            <span class="ml-auto text-xs text-gray-400 flex-shrink-0">{{ it.articles.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50 space-y-1">
            <div v-for="a in it.articles" :key="a.textKey" class="py-1.5">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-1 text-gray-800 break-words">
                  {{ a.title }}
                  <span v-if="a.author" class="text-gray-400 text-xs">　{{ shortAuthor(a.author) }}</span>
                  <span v-if="a.column" class="ml-1 text-[11px] text-indigo-400">{{ a.column }}</span>
                </span>
                <button @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-indigo-600">
                  {{ states[a.textKey]?.open ? '收合' : '全文' }}
                </button>
                <a :href="a.source" target="_blank" rel="noopener" class="flex-shrink-0 text-xs font-medium text-indigo-700 hover:underline no-underline">原文 ↗</a>
              </div>
              <div v-if="states[a.textKey]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[a.textKey].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[a.textKey].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.textKey].text }}</pre>
                <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
              </div>
            </div>
          </div>
        </details>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ loaded ? (q ? '沒有符合的篇目。' : '尚未收錄。') : '載入中…' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '新使者雜誌 — 台灣基督長老教會研究資料' });

interface Article { title: string; author: string; column: string; textKey: string; source: string }
interface Issue { issue: string; title: string; articles: Article[] }

const issues = ref<Issue[]>([]);
const loaded = ref(false);
const q = ref('');

const totalArticles = computed(() => issues.value.reduce((s, i) => s + i.articles.length, 0));

// 期名存的是「第43期 世紀末的文化現象」，期號已另外顯示，這裡只留後半的專題名
function issueSubtitle(it: Issue) {
  return (it.title || '').replace(/^第\s*\d+\s*期\s*/, '');
}
// 作者欄含「作者/莊雅棠 (現為…)」整串簡介，列表只留名字
function shortAuthor(a: string) {
  return a.replace(/^作者\s*[/／]\s*/, '').split(/[（(]/)[0].trim();
}

const shown = computed(() => {
  const term = q.value.trim();
  if (!term) return issues.value;
  return issues.value
    .map(it => ({ ...it, articles: it.articles.filter(a => a.title.includes(term) || a.author.includes(term)) }))
    .filter(it => it.articles.length);
});
const matchCount = computed(() => shown.value.reduce((s, i) => s + i.articles.length, 0));

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(a: Article) {
  let st = states[a.textKey];
  if (!st) st = states[a.textKey] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await $fetch<{ available: boolean; text: string | null }>(
        '/api/research-data/pct-text', { query: { key: a.textKey } });
      st.text = r.available ? (r.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/pct/new-messenger-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
