<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader :title="rec?.date || slug" :back="{ to: '/research-data/taiwan-methodist/chengzhong-bulletins', label: '城中週報' }" container-class="max-w-4xl" />

    <div v-if="rec" class="max-w-4xl mx-auto px-6 py-8">

      <!-- header -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 mb-5">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-mono text-gray-500">{{ rec.date }}</span>
          <span v-if="rec.service !== '主日崇拜'" class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">{{ rec.service }}</span>
          <span v-if="rec.color" class="ml-auto flex items-center gap-1.5 text-xs text-gray-500">
            <span class="w-3.5 h-3.5 rounded-full border" :style="{ background: colorHex(rec.color) }"></span>{{ rec.color }}色（禮儀顏色）
          </span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 leading-snug">{{ rec.season || '主日崇拜' }}</h1>
        <p v-if="rec.date_text" class="text-sm text-gray-500 mt-1">{{ rec.date_text }}</p>
        <div v-if="rec.sermon_title" class="mt-4 p-3 rounded-xl bg-amber-50 border border-amber-100">
          <div class="text-xs text-amber-600 mb-0.5">證道題目</div>
          <div class="text-base font-semibold text-amber-900">{{ rec.sermon_title }}</div>
          <div v-if="rec.preacher" class="text-xs text-amber-700 mt-1">講員：{{ rec.preacher }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

        <!-- roles -->
        <section v-if="roleEntries.length" class="bg-white rounded-2xl border border-gray-100 p-5">
          <h2 class="text-sm font-semibold text-gray-900 mb-3">服事人員</h2>
          <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
            <div v-for="[k, v] in roleEntries" :key="k" class="flex gap-2">
              <dt class="text-gray-400 whitespace-nowrap">{{ k }}</dt>
              <dd class="text-gray-800 font-medium">{{ v }}</dd>
            </div>
          </dl>
        </section>

        <div class="space-y-5">
          <!-- scriptures -->
          <section v-if="rec.scriptures?.length" class="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 class="text-sm font-semibold text-gray-900 mb-3">經課</h2>
            <ul class="space-y-1 text-sm text-gray-700">
              <li v-for="(s, i) in rec.scriptures" :key="i" class="font-mono">{{ s }}</li>
            </ul>
          </section>
          <!-- hymns -->
          <section v-if="rec.hymns?.length" class="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 class="text-sm font-semibold text-gray-900 mb-3">聖詩</h2>
            <ul class="space-y-1 text-sm text-gray-700">
              <li v-for="(h, i) in rec.hymns" :key="i">
                <span class="text-gray-400">{{ h.book }} {{ h.no }}首</span>
                <span v-if="h.title" class="ml-1">「{{ h.title }}」</span>
              </li>
            </ul>
          </section>
        </div>
      </div>

      <!-- full text -->
      <section class="bg-white rounded-2xl border border-gray-100 p-5 mt-5">
        <button @click="showFull = !showFull" class="flex items-center gap-2 text-sm font-semibold text-gray-900">
          <span>崇拜程序全文</span>
          <span class="text-xs text-gray-400">{{ showFull ? '收合' : '展開' }}（{{ rec.full_text?.length || 0 }} 字）</span>
        </button>
        <pre v-if="showFull" class="mt-4 whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">{{ rec.full_text }}</pre>
      </section>

      <p class="text-xs text-gray-400 mt-5">原始檔案：{{ rec.source_file }}</p>
    </div>

    <div v-else class="max-w-4xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
      {{ pending ? '載入中…' : '找不到這份週報' }}
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
const route = useRoute();
const slug = route.params.slug as string;
const year = slug.slice(0, 4);

interface Hymn { book: string; no: string; title: string }
interface Rec {
  date: string; service: string; season: string | null; date_text: string | null;
  color: string | null; preacher: string | null; presider: string | null;
  sermon_title: string | null; roles: Record<string, string>;
  scriptures: string[]; hymns: Hymn[]; full_text: string; source_file: string;
}

const { data: rec, pending } = await useFetch<Rec>(
  () => `/content/chengzhong-bulletins/${year}/${slug}.json`
);
useHead(() => ({ title: `${rec.value?.date || slug} ${rec.value?.season || ''} — 城中週報` }));

const showFull = ref(false);
const ROLE_ORDER = ['主禮', '主理', '證道', '講員', '主席', '司會', '司獻', '招待', '司琴',
  '領唱', '領詩', '領會', '讀經', '獻詩', '獻花', '獻刊', '兒童主日學', '青少年主日學', '愛筵庶務', '值週'];
const roleEntries = computed<[string, string][]>(() => {
  const r = rec.value?.roles || {};
  const keys = Object.keys(r);
  keys.sort((a, b) => {
    const ia = ROLE_ORDER.indexOf(a), ib = ROLE_ORDER.indexOf(b);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
  });
  return keys.map((k) => [k, r[k]]);
});

const COLOR_HEX: Record<string, string> = {
  白: '#f8fafc', 紫: '#7c3aed', 綠: '#16a34a', 紅: '#dc2626',
  藍: '#2563eb', 金: '#d97706', 黑: '#1f2937',
};
function colorHex(c: string) { return COLOR_HEX[c] || '#e5e7eb'; }
</script>
