<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="人間佛教論爭" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700">研究資料</span>
          <span class="text-xs text-gray-400">印順學派與現代禪、西方入世佛教</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">人間佛教論爭</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          印順導師《我有明珠一顆》讀後引發的現代禪論辯，及其後中文學界、西方「入世佛教」研究與原始佛教復原主義的相關論著。
          全文逐頁轉錄，頁首【頁 N】為原書印刷頁碼，讀不到印刷頁碼者標【PDF 頁 N】。
          <span v-if="rows.length" class="text-gray-400">共 {{ rows.length }} 件，已轉錄 {{ doneCount }} 件<template v-if="pendingCount">，{{ pendingCount }} 件待 OCR</template>。</span>
        </p>
      </div>

      <div v-if="groups.length" class="mb-6 flex flex-wrap gap-1.5">
        <button v-for="g in groups" :key="g.label"
          @click="activeGroup = activeGroup === g.label ? '' : g.label"
          :class="['px-2.5 py-1 rounded-full text-xs border transition max-w-full truncate',
                   activeGroup === g.label ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300']">
          {{ g.label }}（{{ g.items.length }}）
        </button>
      </div>

      <div v-if="rows.length" class="space-y-8">
        <section v-for="g in shownGroups" :key="g.label">
          <h2 class="text-sm font-bold text-gray-700 mb-3 truncate">{{ g.label }}<span class="ml-2 text-xs font-normal text-gray-400">{{ g.items.length }} 件</span></h2>
          <div class="space-y-2">
            <div v-for="r in g.items" :key="r.key" class="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div class="px-4 py-3 flex items-start gap-2">
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-gray-900 break-words line-clamp-2">
                    <span v-if="r.author || r.year" class="text-gray-500">{{ r.author }}<template v-if="r.year">（{{ r.year }}）</template></span>{{ r.title }}
                  </div>
                  <div class="mt-0.5 flex flex-wrap gap-x-2 text-[11px] text-gray-400">
                    <span class="uppercase">{{ r.format }}</span>
                    <span v-if="r.pages">{{ r.pages }} 頁</span>
                    <span v-if="r.chars">{{ r.chars.toLocaleString() }} 字</span>
                    <span v-if="r.status === 'ocr_pending'" class="text-amber-600">待 OCR</span>
                    <span v-else-if="r.status === 'error'" class="text-red-500">轉錄失敗</span>
                    <span v-else-if="r.method.startsWith('ocr')" class="text-gray-400">OCR</span>
                  </div>
                </div>
                <div class="flex-shrink-0 flex items-center gap-2">
                  <button v-if="r.status === 'done'" @click="toggle(r)"
                    class="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 hover:bg-indigo-100">
                    {{ states[r.key]?.open ? '收合' : '全文' }}
                  </button>
                  <button type="button" @click="dl(r.key)" class="text-xs text-gray-400 hover:text-indigo-600">⬇ 原檔</button>
                </div>
              </div>
              <div v-if="states[r.key]?.open" class="border-t border-gray-100 bg-gray-50/70">
                <div v-if="states[r.key].loading" class="px-4 py-3 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[r.key].text" class="px-4 py-3 text-xs leading-relaxed text-gray-700 whitespace-pre-wrap break-words font-sans max-h-[70vh] overflow-auto">{{ states[r.key].text }}</pre>
                <div v-else class="px-4 py-3 text-[11px] text-gray-400">全文尚未轉錄。</div>
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
import { authedDownload } from '~/composables/useAuthedDownload';
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '人間佛教論爭 — 印順學派與弘誓研究資料' });

interface Row {
  key: string; title: string; author: string; year: string; group: string; format: string;
  pages: number; chars: number; status: string; method: string; printedPages: number; r2Source: boolean;
}
const GROUP_ORDER = ['論爭核心文獻', '西方與中文學界', '復原主義比較'];
const rows = ref<Row[]>([]);
const loaded = ref(false);
const activeGroup = ref('');

const doneCount = computed(() => rows.value.filter(r => r.status === 'done').length);
const pendingCount = computed(() => rows.value.filter(r => r.status !== 'done').length);
const groups = computed(() => {
  const labels = [...GROUP_ORDER, ...new Set(rows.value.map(r => r.group).filter(g => !GROUP_ORDER.includes(g)))];
  return labels
    .map(label => ({
      label,
      items: rows.value.filter(r => r.group === label)
        .sort((a, b) => (a.year || '9999').localeCompare(b.year || '9999') || a.key.localeCompare(b.key)),
    }))
    .filter(g => g.items.length);
});
const shownGroups = computed(() => activeGroup.value ? groups.value.filter(g => g.label === activeGroup.value) : groups.value);

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(r: Row) {
  let st = states[r.key];
  if (!st) st = states[r.key] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const res = await authedFetch<{ available: boolean; text: string | null }>(
        '/api/research-data/yinshun-hongshi-text', { query: { key: r.key } });
      st.text = res.available ? (res.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

async function dl(key: string) {
  await authedDownload(`/api/research-data/yinshun-hongshi-file?key=${encodeURIComponent(key)}&download=1`,
    key.split('/').pop() || 'download');
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/debate-index.json');
    if (r.ok) rows.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
