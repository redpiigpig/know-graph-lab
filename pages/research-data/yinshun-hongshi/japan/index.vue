<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="日本學者論印順" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-6xl" />

    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-red-100 text-red-700">研究資料</span>
          <span class="text-xs text-gray-400">日文學界的印順研究</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">日本學者論印順</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          日本學者評介、研究印順導師思想與學術貢獻的論文、書評與學位審查報告。能取得全文者逐段譯為中文，左欄中譯、右欄原文對照；
          原文本即中文或英文者只轉錄原文；其餘列書目與出處。
          <span v-if="entries.length" class="text-gray-400">共 {{ entries.length }} 筆，其中 {{ withText }} 筆有逐段對照。</span>
        </p>
      </div>

      <div v-if="entries.length" class="space-y-8">
        <section v-for="g in grouped" :key="g.label">
          <h2 class="text-sm font-bold text-gray-700 mb-3">{{ g.label }}<span class="ml-2 text-xs font-normal text-gray-400">{{ g.items.length }} 筆</span></h2>
          <div class="space-y-2">
            <div v-for="e in g.items" :key="e.id" class="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div class="px-4 py-3">
                <div class="flex items-start gap-2">
                  <div class="flex-1 min-w-0">
                    <div class="text-sm text-gray-900 break-words">
                      <span class="text-gray-500">{{ e.author }}（{{ e.year }}）</span>〈{{ e.title }}〉
                    </div>
                    <div v-if="e.titleZh" class="text-xs text-gray-500 break-words mt-0.5">中譯題名：{{ e.titleZh }}</div>
                    <div class="text-xs text-gray-400 break-words mt-0.5">{{ citation(e) }}</div>
                    <p v-if="e.abstract" class="text-xs text-gray-600 leading-relaxed mt-1.5 line-clamp-3 break-words">{{ e.abstract }}</p>
                  </div>
                  <div class="flex-shrink-0 flex flex-col items-end gap-1">
                    <button v-if="e.paras" @click="toggle(e)"
                      class="text-xs font-medium px-2 py-0.5 rounded-full bg-red-50 text-red-700 hover:bg-red-100">
                      {{ states[e.id]?.open ? '收合' : (e.transcribeOnly ? `全文 ${e.paras} 段` : `對照 ${e.translated}/${e.paras} 段`) }}
                    </button>
                    <a v-if="e.url" :href="e.url" target="_blank" rel="noopener" class="text-xs text-gray-400 hover:text-red-600 no-underline">原文出處 ↗</a>
                  </div>
                </div>
              </div>

              <div v-if="states[e.id]?.open" class="border-t border-gray-100 bg-gray-50/60">
                <div v-if="states[e.id].loading" class="px-4 py-3 text-xs text-gray-400">載入全文⋯</div>
                <div v-else-if="states[e.id].paras?.length && e.transcribeOnly" class="divide-y divide-gray-100">
                  <div class="px-4 py-2 text-[11px] font-medium text-gray-400">原文（{{ e.lang }}，只轉錄不譯）</div>
                  <div v-for="(p, i) in states[e.id].paras" :key="i" class="px-4 py-3 text-sm leading-relaxed text-gray-800 break-words"
                    :lang="e.lang?.startsWith('英') ? 'en' : 'zh-Hant'">
                    <span v-if="p.page" class="mr-1 text-[10px] text-gray-400">p.{{ p.page }}</span>{{ p.orig }}
                  </div>
                </div>
                <div v-else-if="states[e.id].paras?.length" class="divide-y divide-gray-100">
                  <div class="hidden md:grid grid-cols-2 gap-6 px-4 py-2 text-[11px] font-medium text-gray-400">
                    <div>中譯</div><div>原文</div>
                  </div>
                  <div v-for="(p, i) in states[e.id].paras" :key="i" class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-6 px-4 py-3">
                    <div class="text-sm leading-relaxed text-gray-800 break-words">
                      <span v-if="p.page" class="mr-1 text-[10px] text-gray-400">p.{{ p.page }}</span>{{ p.zh || '—' }}
                    </div>
                    <div class="text-sm leading-relaxed text-gray-500 break-words" :lang="e.zhSame ? 'zh-Hant' : 'ja'">{{ p.orig }}</div>
                  </div>
                </div>
                <div v-else class="px-4 py-3 text-xs text-gray-400">全文尚未轉錄。</div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '日本學者論印順 — 印順學派與弘誓研究資料' });

interface Entry {
  id: string; group: string; author: string; year: string; title: string; titleZh?: string;
  venue?: string; volume?: string; issue?: string; pages?: string; kind?: string;
  url?: string; abstract?: string; paras: number; translated: number; zhSame?: boolean;
  transcribeOnly?: boolean; lang?: string;
}
interface Para { page: number | null; orig: string; zh: string }

const GROUP_ORDER = ['專論', '部分論及', '僅提及', '日本機構之非日籍作者'];
const entries = ref<Entry[]>([]);
const loaded = ref(false);

const withText = computed(() => entries.value.filter(e => e.paras).length);
const grouped = computed(() => {
  const labels = [...GROUP_ORDER, ...new Set(entries.value.map(e => e.group).filter(g => !GROUP_ORDER.includes(g)))];
  return labels
    .map(label => ({ label, items: entries.value.filter(e => e.group === label).sort((a, b) => String(a.year).localeCompare(String(b.year))) }))
    .filter(g => g.items.length);
});

function citation(e: Entry) {
  const parts = [e.venue && `《${e.venue}》`, e.volume && `${e.volume}`, e.issue && `(${e.issue})`, e.pages && `頁 ${e.pages}`, e.kind];
  return parts.filter(Boolean).join('　');
}

interface State { open: boolean; loading: boolean; loaded: boolean; paras: Para[] | null }
const states = reactive<Record<string, State>>({});
async function toggle(e: Entry) {
  let st = states[e.id];
  if (!st) st = states[e.id] = { open: false, loading: false, loaded: false, paras: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await authedFetch<{ available: boolean; paras?: Para[] }>(
        '/api/research-data/yinshun-hongshi-bilingual', { query: { id: e.id } });
      st.paras = r.available ? (r.paras ?? null) : null;
    } catch { st.paras = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/japan-index.json');
    if (r.ok) entries.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
