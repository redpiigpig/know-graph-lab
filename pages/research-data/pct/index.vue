<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="台灣基督長老教會研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">台灣基督長老教會研究資料</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          長老教會系統的報刊與史料典藏，作為博士論文「台灣長老教會的公共神學發展」一章的史料底本：
          黃彰輝的實況化、宋泉盛的故事神學、王憲治的鄉土神學、黃伯和的出頭天神學，以及三大聲明以降的公共介入。
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <NuxtLink to="/research-data/pct/tcnn" class="tool-card group border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
          <div class="tool-icon bg-blue-50 text-blue-600">📰</div>
          <div class="flex-1">
            <h2 class="tool-title">台灣教會公報新聞網</h2>
            <p class="tool-desc">公報社新聞網逐篇全文，2010 年 12 月起至今；教會決議、社會議題發言與各中會動態的當代報導底本</p>
          </div>
          <span class="tool-badge bg-blue-50 text-blue-600">{{ tcnnCount ? `${tcnnCount} 篇` : '…' }}</span>
        </NuxtLink>

        <NuxtLink to="/research-data/pct/new-messenger" class="tool-card group border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
          <div class="tool-icon bg-indigo-50 text-indigo-600">📖</div>
          <div class="flex-1">
            <h2 class="tool-title">新使者雜誌</h2>
            <p class="tool-desc">長老教會青年刊物，1990 年創刊；黃彰輝小傳、宋泉盛專題、王憲治與鄉土神學等本土神學論述多刊於此</p>
          </div>
          <span class="tool-badge bg-indigo-50 text-indigo-600">{{ nmCount ? `${nmCount} 篇` : '…' }}</span>
        </NuxtLink>

        <NuxtLink to="/research-data/pct/documents" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="tool-icon bg-rose-50 text-rose-600">📜</div>
          <div class="flex-1">
            <h2 class="tool-title">總會重要文獻</h2>
            <p class="tool-desc">三大聲明（1971國是聲明、1975我們的呼籲、1977人權宣言）、1985 信仰告白，及歷年牧函、宣言、請願書</p>
          </div>
          <span class="tool-badge bg-rose-50 text-rose-600">{{ docCount ? `${docCount} 件` : '…' }}</span>
        </NuxtLink>

        <NuxtLink to="/research-data/pct/laijohn" class="tool-card group border-teal-100 hover:border-teal-300 hover:shadow-teal-100">
          <div class="tool-icon bg-teal-50 text-teal-600">👤</div>
          <div class="flex-1">
            <h2 class="tool-title">本土信徒傳記</h2>
            <p class="tool-desc">賴永祥長老史料庫「本土信徒」一區：台灣本土基督徒的略歷、訪問記、告別禮拜與回憶錄</p>
          </div>
          <span class="tool-badge bg-teal-50 text-teal-600">{{ ljCount ? `${ljCount} 人` : '…' }}</span>
        </NuxtLink>

        <NuxtLink to="/research-data/pct/biblio" class="tool-card group border-sky-100 hover:border-sky-300 hover:shadow-sky-100">
          <div class="tool-icon bg-sky-50 text-sky-600">🔖</div>
          <div class="flex-1">
            <h2 class="tool-title">參考書目與館藏清單</h2>
            <p class="tool-desc">華藝檢索的參考書目，與臺灣記憶的長老教會文獻館藏目錄；到館調閱前用來選件</p>
          </div>
        </NuxtLink>

      </div>

      <p class="mt-6 text-xs text-gray-400 leading-relaxed">
        待補：事工說明書（同站）。女宣雜誌經評估不收。
        《使者》（1963–1990，新使者前身）線上無全文典藏。
        《台灣教會公報》1885–2007 掃描檔須向公報社去信索取；2008 至 2010 年間的期別目前無免費線上來源。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣基督長老教會研究資料 — 論文資料整理' });

const tcnnCount = ref(0);
const nmCount = ref(0);
const docCount = ref(0);
const ljCount = ref(0);

// 各刊的計數彼此獨立：任一份 index 還沒產出，不該讓其他張卡也跟著空著
async function total(url: string, pick: (row: any) => number): Promise<number> {
  try {
    const r = await fetch(url);
    if (!r.ok) return 0;
    return ((await r.json()) as any[]).reduce((s, x) => s + pick(x), 0);
  } catch { return 0; }
}

onMounted(async () => {
  const base = '/content/research-data/pct';
  tcnnCount.value = await total(`${base}/tcnn-index.json`, x => x.count ?? 0);
  nmCount.value = await total(`${base}/new-messenger-index.json`, x => x.articles?.length ?? 0);
  docCount.value = await total(`${base}/documents-index.json`, () => 1);
  ljCount.value = await total(`${base}/laijohn-index.json`, () => 1);
});
</script>

<style scoped>
.tool-card {
  @apply relative flex items-start gap-4 p-5 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline;
}
.tool-icon {
  @apply w-11 h-11 rounded-xl flex items-center justify-center text-xl select-none flex-shrink-0;
}
.tool-title {
  @apply text-sm font-semibold text-gray-900 mb-0.5;
}
.tool-desc {
  @apply text-xs text-gray-500 leading-relaxed;
}
.tool-badge {
  @apply self-start text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0;
}
</style>
