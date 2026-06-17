<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="福嚴會訊" :back="{ to: '/research-data/yinshun-hongshi', label: '弘誓研究資料' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700">研究資料</span>
          <span class="text-xs text-gray-400">福嚴佛學院</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">福嚴會訊</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          福嚴佛學院（印順導師創辦）會訊，記錄印順學脈絡的僧伽教育、弘法與學術活動。
          <span v-if="issues.length" class="text-gray-400">收錄第 1–{{ issues.length }} 期，皆附全文轉錄。</span>
        </p>
      </div>

      <div v-if="issues.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="it in issues" :key="it.issue" class="bg-white rounded-xl border border-gray-100 p-4 hover:border-emerald-200 hover:shadow-sm transition-all">
          <div class="flex items-baseline justify-between gap-2 mb-2">
            <h3 class="text-sm font-bold text-gray-900">第 {{ it.issue }} 期</h3>
            <div class="flex items-center gap-2 flex-shrink-0">
              <button v-if="it.hasFulltext" @click="toggle(it)" class="text-xs text-gray-400 hover:text-emerald-600">
                {{ states[it.key]?.open ? '收合' : '全文' }}
              </button>
              <a :href="`/api/works/material?key=${encodeURIComponent(it.key)}`"
                class="text-xs font-medium text-emerald-700 hover:underline no-underline">⬇ PDF {{ fmtSize(it.size) }}</a>
            </div>
          </div>
          <div v-if="states[it.key]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
            <div v-if="states[it.key].loading" class="px-3 py-3 text-[11px] text-gray-400">載入全文⋯</div>
            <pre v-else-if="states[it.key].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-80 overflow-auto">{{ states[it.key].text }}</pre>
            <div v-else class="px-3 py-3 text-[11px] text-gray-400">全文尚未轉錄。</div>
          </div>
        </div>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '福嚴會訊 — 印順學派與弘誓研究資料' });

interface Issue { issue: number; name: string; key: string; size: number; hasFulltext: boolean }
interface State { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const issues = ref<Issue[]>([]);
const loaded = ref(false);
const states = reactive<Record<string, State>>({});

function fmtSize(b?: number) {
  if (!b) return '';
  return b >= 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(0)}MB` : `${Math.round(b / 1024)}KB`;
}

async function toggle(it: Issue) {
  let st = states[it.key];
  if (!st) st = states[it.key] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const r = await $fetch<{ available: boolean; text: string | null; zh: string | null }>(
        '/api/works/material-text', { query: { key: it.key } });
      st.text = r.zh || r.text || null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/fuyan-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>
