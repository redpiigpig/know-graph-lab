<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/yinshun-hongshi" class="text-gray-400 hover:text-gray-700 transition text-sm">← 印順學派與弘誓研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">弘誓雙月刊</span>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-rose-100 text-rose-700">研究資料</span>
          <span class="text-xs text-gray-400">佛教弘誓學院</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">弘誓雙月刊</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          佛教弘誓學院機關刊物，收錄昭慧法師、性廣法師之佛法論述、戒律與性別議題專文，及學團弘法、社運紀實。每期為官網整本掃描 PDF。
          <span v-if="issues.length" class="text-gray-400">目前收錄第 {{ minIssue }}–{{ maxIssue }} 期，共 {{ issues.length }} 期。</span>
        </p>
      </div>

      <div v-if="issues.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="it in issues" :key="it.issue" class="bg-white rounded-xl border border-gray-100 p-4 hover:border-rose-200 hover:shadow-sm transition-all">
          <div class="flex items-baseline justify-between gap-2 mb-1">
            <h3 class="text-sm font-bold text-gray-900">第 {{ it.issue }} 期</h3>
            <span v-if="pubDate(it)" class="text-xs text-gray-400 flex-shrink-0">{{ pubDate(it) }}</span>
          </div>
          <p v-if="cleanTitle(it.title)" class="text-xs text-gray-600 leading-relaxed line-clamp-2 mb-2 break-words">{{ cleanTitle(it.title) }}</p>
          <div class="flex flex-wrap items-center gap-2">
            <a v-for="p in it.parts" :key="p.part"
              :href="`/api/research-data/yinshun-hongshi-file?key=${encodeURIComponent(p.key)}&download=1`"
              class="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-50 no-underline">
              ⬇ {{ it.parts.length > 1 ? `第${p.part}冊 PDF` : 'PDF 全本' }}
              <span class="text-rose-300">{{ fmtSize(p.size) }}</span>
            </a>
          </div>
        </div>
      </div>

      <div v-else class="py-20 text-center text-sm text-gray-400">{{ loaded ? '尚未收錄。' : '載入中…' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '弘誓雙月刊 — 印順學派與弘誓研究資料' });

interface Part { part: number; key: string; size: number }
interface Issue { issue: number; date: string; title: string; parts: Part[] }
const issues = ref<Issue[]>([]);
const loaded = ref(false);

const minIssue = computed(() => issues.value.length ? Math.min(...issues.value.map(i => i.issue)) : 0);
const maxIssue = computed(() => issues.value.length ? Math.max(...issues.value.map(i => i.issue)) : 0);

function fmtSize(b?: number) {
  if (!b) return '';
  return b >= 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(0)}MB` : `${Math.round(b / 1024)}KB`;
}
// the harvested title often begins with "YYYY/MM發行 整本PDF檔" or "封面說明│…"
function pubDate(it: Issue): string {
  const m = (it.title || '').match(/(\d{4})\s*[/.]\s*(\d{1,2})\s*發行/);
  if (m) return `${m[1]}/${m[2].padStart(2, '0')}`;
  if (it.date && it.date.length === 8) return `${it.date.slice(0, 4)}/${it.date.slice(4, 6)}`;
  return '';
}
function cleanTitle(t: string): string {
  if (!t) return '';
  return t
    .replace(/^\d{4}\s*[/.]\s*\d{1,2}\s*發行\s*整本PDF檔\s*/, '')
    .replace(/^封面說明│?\s*/, '')
    .replace(/整本PDF檔/g, '')
    .trim()
    .slice(0, 110);
}

onMounted(async () => {
  try {
    const r = await fetch('/content/research-data/yinshun-hongshi/magazine-index.json');
    if (r.ok) issues.value = await r.json();
  } catch { /* keep empty */ } finally { loaded.value = true; }
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
