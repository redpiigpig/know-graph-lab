<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="本土信徒傳記" :back="{ to: '/research-data/pct', label: '長老教會研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">研究資料</span>
          <span class="text-xs text-gray-400">賴永祥長老史料庫</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">本土信徒傳記</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          取自賴永祥長老史料庫「本土信徒」一區：台灣本土基督徒的略歷、訪問記、告別禮拜與回憶錄。
          王憲治、黃彰輝、宋泉盛等人的傳記文章都在此。
          <span v-if="people.length" class="text-gray-400">收錄 {{ people.length.toLocaleString() }} 人、{{ totalArticles.toLocaleString() }} 篇。</span>
        </p>
      </div>

      <div class="mb-5">
        <input v-model="q" type="search" placeholder="搜尋人名代碼或篇名（例：Ong,HTi、黃彰輝、鄉土神學）"
          class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-teal-400" />
        <p class="mt-1.5 text-xs text-gray-400">
          {{ q ? `${shown.length.toLocaleString()} 人符合` : '站方以「姓,名」的羅馬字代碼歸戶，例如王憲治為 Ong,HTi' }}
        </p>
      </div>

      <div v-if="shown.length" class="space-y-2">
        <details v-for="p in paged" :key="p.person" :open="!!q && shown.length < 12"
          class="group bg-white rounded-xl border border-gray-100 overflow-hidden">
          <summary class="flex items-center gap-2 px-4 py-2.5 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-mono text-gray-800">{{ p.person }}</span>
            <span class="text-xs text-gray-500 flex-1 break-words">{{ p.articles[0].title.slice(0, 40) }}</span>
            <span class="text-xs text-gray-400 flex-shrink-0">{{ p.articles.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50 space-y-1">
            <div v-for="a in p.articles" :key="a.textKey" class="py-1">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-1 text-gray-800 break-words">{{ a.title }}</span>
                <button @click="toggle(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-teal-600">
                  {{ states[a.textKey]?.open ? '收合' : '全文' }}
                </button>
                <a :href="a.source" target="_blank" rel="noopener" class="flex-shrink-0 text-xs font-medium text-teal-700 hover:underline no-underline">原頁 ↗</a>
              </div>
              <div v-if="states[a.textKey]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[a.textKey].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[a.textKey].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.textKey].text }}</pre>
                <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
              </div>
            </div>
          </div>
        </details>

        <div v-if="paged.length < shown.length" class="pt-3 text-center">
          <button @click="limit += 100" class="text-xs text-teal-600 hover:underline">
            顯示更多（已顯示 {{ paged.length }} / {{ shown.length }} 人）
          </button>
        </div>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">
        {{ loaded ? (q ? '沒有符合的人物。' : '尚未收錄。') : '載入中…' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '本土信徒傳記 — 台灣基督長老教會研究資料' });

interface Article { title: string; label: string; textKey: string; source: string }
interface Person { person: string; articles: Article[] }

const people = ref<Person[]>([]);
const loaded = ref(false);
const q = ref('');
const limit = ref(100);

const totalArticles = computed(() => people.value.reduce((s, p) => s + p.articles.length, 0));
const shown = computed(() => {
  const term = q.value.trim();
  if (!term) return people.value;
  return people.value.filter(p =>
    p.person.toLowerCase().includes(term.toLowerCase()) ||
    p.articles.some(a => a.title.includes(term)));
});
const paged = computed(() => shown.value.slice(0, limit.value));
watch(q, () => { limit.value = 100; });

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
    const r = await fetch('/content/research-data/pct/laijohn-index.json');
    if (r.ok) people.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
