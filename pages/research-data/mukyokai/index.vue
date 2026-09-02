<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="無教會主義研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">無教會主義研究資料</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          內村鑑三所開創、經矢內原忠雄一代傳衍的無教會主義，其研究文獻與史料。
          博士論文第二章「東亞近代宗教變革」的日本線，與台灣日治時期教會經驗都用得上。
          日文論著保留原題，另附中譯。
          <span class="text-gray-400">無教會依其主張本無教會組織，故此處以「運動」而非機構為收錄單位。</span>
        </p>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed">
          內村鑑三、矢內原忠雄本人的著作屬原典，收在
          <NuxtLink to="/collected-works/uchimura" class="text-emerald-700 hover:underline">全集的無教會 hub</NuxtLink>，不在此處。
        </p>
      </div>

      <div v-if="rows.length" class="space-y-3">
        <article v-for="r in rows" :key="r.stem" class="bg-white rounded-xl border border-gray-100 p-5">
          <div class="flex items-baseline gap-2 flex-wrap mb-1">
            <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">{{ r.kindLabel }}</span>
            <span class="text-xs text-gray-400">{{ r.year }}</span>
            <span class="text-sm font-semibold text-gray-900 break-words">{{ r.author }}</span>
            <span v-if="r.lang === 'ja'" class="text-[11px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">日文</span>
          </div>
          <h2 class="text-sm text-gray-800 leading-relaxed break-words">《{{ r.titleOriginal || r.title }}》</h2>
          <p v-if="r.titleOriginal" class="text-xs text-gray-500 leading-relaxed break-words">中譯：《{{ r.title }}》</p>
          <p v-if="r.publisher" class="mt-0.5 text-xs text-gray-500 break-words">{{ r.publisher }}</p>
          <p v-if="r.note" class="mt-1.5 text-xs text-gray-500 leading-relaxed break-words">{{ r.note }}</p>

          <div class="mt-3 flex items-center gap-3 text-xs">
            <span class="text-gray-400">{{ r.pages ? `${r.pages} 頁 · ` : '' }}{{ r.chars.toLocaleString() }} 字</span>
            <button @click="toggle(r)" class="text-gray-500 hover:text-emerald-700">
              {{ states[r.stem]?.open ? '收合全文' : '全文' }}
            </button>
            <button type="button" @click="dl(r.pdfKey)"
              class="font-medium text-emerald-700 hover:underline no-underline">⬇ {{ r.pdfKey.endsWith('.docx') ? 'Word' : 'PDF' }}</button>
          </div>

          <div v-if="states[r.stem]?.open" class="mt-2 rounded-lg border border-gray-100 bg-gray-50/70">
            <div v-if="states[r.stem].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
            <pre v-else-if="states[r.stem].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-[32rem] overflow-auto">{{ states[r.stem].text }}</pre>
            <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
          </div>
        </article>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>

      <!-- 《無境界者》：篇數多、性質與研究文獻不同，另立一區依期別收合 -->
      <section v-if="mag.length" class="mt-10">
        <h2 class="text-base font-semibold text-gray-900 mb-1">《無境界者》雜誌</h2>
        <p class="text-xs text-gray-500 mb-4 leading-relaxed">
          2024 年創刊的線上雜誌，雙數月發刊，「不以教會為本位的自由信仰論述平台」——
          台灣無教會運動當代這一端的一手語料，與廖本恩那本百年運動史接續。
          共 {{ magIssues.length }} 期 {{ mag.length }} 篇（正文 {{ magArticles }}）。
        </p>
        <details v-for="g in magIssues" :key="g.issue" class="group bg-white rounded-xl border border-gray-100 overflow-hidden mb-2">
          <summary class="flex items-center gap-2 px-4 py-2.5 cursor-pointer select-none hover:bg-gray-50">
            <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
            <span class="text-sm font-bold text-gray-900">第 {{ g.issue }} 期</span>
            <span class="ml-auto text-xs text-gray-400">{{ g.items.length }} 篇</span>
          </summary>
          <div class="px-4 pb-3 pt-1 border-t border-gray-50 space-y-1">
            <div v-for="a in g.items" :key="a.textKey" class="py-1">
              <div class="flex items-baseline gap-2 text-sm">
                <span class="flex-1 text-gray-800 break-words">
                  {{ a.title }}
                  <span v-if="a.kind === 'front'" class="text-[11px] text-gray-400">前置</span>
                </span>
                <span class="flex-shrink-0 text-xs text-gray-400">{{ a.chars.toLocaleString() }} 字</span>
                <button @click="toggleMag(a)" class="flex-shrink-0 text-xs text-gray-400 hover:text-emerald-600">
                  {{ states[a.textKey]?.open ? '收合' : '全文' }}
                </button>
              </div>
              <div v-if="states[a.textKey]?.open" class="mt-1 rounded-lg border border-gray-100 bg-gray-50/70">
                <div v-if="states[a.textKey].loading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="states[a.textKey].text" class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-96 overflow-auto">{{ states[a.textKey].text }}</pre>
                <div v-else class="px-3 py-2 text-[11px] text-gray-400">全文尚未轉錄。</div>
              </div>
            </div>
          </div>
        </details>
      </section>

      <p class="mt-6 text-xs text-gray-400 leading-relaxed">
        待補：矢內原忠雄與台灣的相關研究、塚本虎二／藤井武／金教臣等第二代無教會人物的研究文獻、
        台灣無教會集會的口述與紀錄。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authedDownload } from '~/composables/useAuthedDownload';
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, reactive, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '無教會主義研究資料 — 論文資料整理' });

interface Row {
  stem: string; title: string; titleOriginal?: string; lang?: string; author: string; year: string;
  kindLabel: string; publisher: string; note: string;
  pages: number; chars: number; pdfKey: string; textKey: string;
}

const rows = ref<Row[]>([]);
const loaded = ref(false);

interface MagRow { issue: number; seq: number; title: string; kind: string; chars: number; textKey: string }
const mag = ref<MagRow[]>([]);
const magArticles = computed(() => mag.value.filter(r => r.kind === 'article').length);
const magIssues = computed(() => {
  const by = new Map<number, MagRow[]>();
  for (const r of mag.value) by.set(r.issue, [...(by.get(r.issue) ?? []), r]);
  return [...by.entries()].sort((a, b) => b[0] - a[0])
    .map(([issue, items]) => ({ issue, items: items.sort((a, b) => a.seq - b.seq) }));
});
async function toggleMag(a: MagRow) {
  let st = states[a.textKey];
  if (!st) st = states[a.textKey] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const res = await authedFetch<{ available: boolean; text: string | null }>(
        '/api/research-data/mukyokai-text', { query: { key: a.textKey } });
      st.text = res.available ? (res.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

interface TextState { open: boolean; loading: boolean; loaded: boolean; text: string | null }
const states = reactive<Record<string, TextState>>({});
async function toggle(r: Row) {
  let st = states[r.stem];
  if (!st) st = states[r.stem] = { open: false, loading: false, loaded: false, text: null };
  st.open = !st.open;
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true;
    try {
      const res = await authedFetch<{ available: boolean; text: string | null }>(
        '/api/research-data/mukyokai-text', { query: { key: r.textKey } });
      st.text = res.available ? (res.text ?? null) : null;
    } catch { st.text = null; } finally { st.loading = false; st.loaded = true; }
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/mukyokai/index.json');
    if (r.ok) rows.value = await r.json();
  } catch { /* keep empty */ }
  try {
    const r = await fetch('/content/research-data/mukyokai/nonchurch-index.json');
    if (r.ok) mag.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
// 端點加了 requireAdmin，`<a href>` 帶不了 Authorization header，
// 所以下載改走 authedFetch 取 blob（見 useAuthedDownload）。
async function dl(key: string) {
  await authedDownload(`/api/research-data/mukyokai-file?key=${encodeURIComponent(key)}&download=1`,
    key.split('/').pop() || 'download.pdf');
}
</script>
