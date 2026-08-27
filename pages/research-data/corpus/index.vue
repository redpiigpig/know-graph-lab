<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="語料層：關鍵詞年表" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">語料層：關鍵詞年表</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          跨刊物比對同一個詞的出現年代與消長。左欄佛教刊物、右欄基督教刊物，
          用來看「人生佛教→人間佛教」與「本色化→實況化→鄉土→出頭天」兩組概念各自何時成形、
          以及兩邊在哪些議題上同時出現。
          <span v-if="corpusList.length" class="text-gray-400">
            涵蓋 {{ corpusList.length }} 個語料、{{ totalDocs.toLocaleString() }} 篇。
          </span>
        </p>
        <p class="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 leading-relaxed">
          玄奘佛學研究、法印學報、新使者的篇目沒有逐篇日期，計入總數但不進年表；妙心雜誌僅 2000 年以後的期別帶日期。
          刊期不規則，故一律不做年份內插。
        </p>
      </div>

      <div v-if="!loaded" class="py-20 text-center text-sm text-gray-400">載入計數表⋯</div>
      <div v-else-if="!available" class="py-20 text-center text-sm text-gray-400">
        計數表尚未建立。請先跑 <code class="font-mono">scripts/corpus_terms.py --build</code>。
      </div>

      <template v-else>
        <!-- 詞表 -->
        <div v-for="(terms, group) in groups" :key="group" class="mb-4">
          <div class="text-xs font-semibold text-gray-400 mb-1.5">{{ group }}</div>
          <div class="flex flex-wrap gap-1.5">
            <button v-for="t in terms" :key="t" @click="toggleTerm(t)"
              :class="['px-2.5 py-1 rounded-full text-xs border transition',
                       selected.includes(t) ? 'bg-gray-900 text-white border-gray-900'
                                            : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400',
                       hasData(t) ? '' : 'opacity-40']">
              {{ t }}<span class="ml-1 opacity-60">{{ totalFor(t).toLocaleString() }}</span>
            </button>
          </div>
        </div>

        <p v-if="!selected.length" class="py-16 text-center text-sm text-gray-400">選一個以上的詞，看它在各語料的逐年分布。</p>

        <!-- 年表 -->
        <section v-for="t in selected" :key="t" class="mt-8 bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-baseline gap-3 mb-4">
            <h2 class="text-base font-bold text-gray-900">{{ t }}</h2>
            <span class="text-xs text-gray-400">共 {{ totalFor(t).toLocaleString() }} 次 / {{ docsFor(t).toLocaleString() }} 篇</span>
          </div>

          <div v-if="years(t).length" class="overflow-x-auto">
            <svg :width="Math.max(640, years(t).length * 34)" height="180" class="block">
              <g v-for="(y, i) in years(t)" :key="y">
                <g v-for="(c, ci) in corporaWithData(t)" :key="c">
                  <rect :x="i * 34 + 6 + ci * (26 / corporaWithData(t).length)"
                    :y="170 - barH(t, c, y)"
                    :width="26 / corporaWithData(t).length" :height="barH(t, c, y)"
                    :fill="sideColor(c)" :opacity="0.55 + 0.45 * (ci % 2)">
                    <title>{{ corpora[c].name }} {{ y }}：{{ count(t, c, y) }} 次</title>
                  </rect>
                </g>
                <text :x="i * 34 + 19" y="179" text-anchor="middle" class="fill-gray-400" style="font-size:9px">
                  {{ y.slice(2) }}
                </text>
              </g>
            </svg>
          </div>
          <p v-else class="text-xs text-gray-400 py-6 text-center">此詞命中的篇目都沒有日期，無法排年表。</p>

          <!-- 各語料計數 -->
          <div class="mt-4 flex flex-wrap gap-2">
            <span v-for="c in corporaWithData(t)" :key="c"
              class="text-xs px-2 py-1 rounded-lg border" :style="{ borderColor: sideColor(c) }">
              <span :style="{ color: sideColor(c) }">{{ corpora[c].name }}</span>
              <span class="text-gray-500 ml-1">{{ corpusTotal(t, c).toLocaleString() }} 次</span>
            </span>
          </div>

          <!-- 脈絡 -->
          <details v-if="samples[t]" class="mt-4">
            <summary class="text-xs text-gray-500 cursor-pointer hover:text-gray-800">脈絡取樣</summary>
            <div class="mt-2 space-y-2">
              <template v-for="(rows, c) in samples[t]" :key="c">
                <div v-for="(s, si) in rows" :key="si" class="text-[11px] leading-relaxed">
                  <span class="text-gray-400">{{ corpora[c].name }}{{ s.year ? ' ' + s.year : '' }}　{{ s.title }}</span>
                  <div class="text-gray-700" v-html="highlight(s.text, t)"></div>
                </div>
              </template>
            </div>
          </details>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '語料層：關鍵詞年表 — 論文資料整理' });

interface CorpusMeta { name: string; side: string; docs: number }
interface Sample { docId: string; year: string; title: string; text: string }
type ByCorpusYear = Record<string, Record<string, number>>;

const loaded = ref(false);
const available = ref(false);
const groups = ref<Record<string, string[]>>({});
const corpora = ref<Record<string, CorpusMeta>>({});
const counts = ref<Record<string, ByCorpusYear>>({});
const docCounts = ref<Record<string, ByCorpusYear>>({});
const samples = ref<Record<string, Record<string, Sample[]>>>({});
const selected = ref<string[]>([]);

const corpusList = computed(() => Object.keys(corpora.value));
const totalDocs = computed(() => Object.values(corpora.value).reduce((s, c) => s + c.docs, 0));

function toggleTerm(t: string) {
  selected.value = selected.value.includes(t)
    ? selected.value.filter(x => x !== t)
    : [...selected.value, t];
}

const sum = (o?: Record<string, number>) => Object.values(o ?? {}).reduce((s, n) => s + n, 0);
const totalFor = (t: string) => Object.values(counts.value[t] ?? {}).reduce((s, y) => s + sum(y), 0);
const docsFor = (t: string) => Object.values(docCounts.value[t] ?? {}).reduce((s, y) => s + sum(y), 0);
const hasData = (t: string) => totalFor(t) > 0;
const corpusTotal = (t: string, c: string) => sum(counts.value[t]?.[c]);
const corporaWithData = (t: string) => Object.keys(counts.value[t] ?? {}).filter(c => corpusTotal(t, c) > 0);
const count = (t: string, c: string, y: string) => counts.value[t]?.[c]?.[y] ?? 0;

// 沒有年份的篇目歸在 "" 桶，年表不畫它
function years(t: string) {
  const set = new Set<string>();
  for (const y of Object.values(counts.value[t] ?? {})) {
    for (const k of Object.keys(y)) if (k) set.add(k);
  }
  return [...set].sort();
}
function maxCount(t: string) {
  let m = 0;
  for (const c of corporaWithData(t)) for (const y of years(t)) m = Math.max(m, count(t, c, y));
  return m || 1;
}
const barH = (t: string, c: string, y: string) => Math.round((count(t, c, y) / maxCount(t)) * 150);

const sideColor = (c: string) => (corpora.value[c]?.side === '佛教' ? '#c2410c' : '#1d4ed8');

function highlight(text: string, term: string) {
  const esc = (s: string) => s.replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch] as string));
  return esc(text).split(esc(term)).join(`<mark class="bg-amber-100">${esc(term)}</mark>`);
}

onMounted(async () => {
  try {
    const d = await $fetch<any>('/api/research-data/corpus-terms');
    if (d?.available) {
      groups.value = d.groups ?? {};
      corpora.value = d.corpora ?? {};
      counts.value = d.counts ?? {};
      docCounts.value = d.docs ?? {};
      samples.value = d.samples ?? {};
      available.value = true;
    }
  } catch { available.value = false; } finally { loaded.value = true; }
});
</script>
