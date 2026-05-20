<template>
  <div v-if="open" class="fixed inset-0 z-[100] bg-black/40 flex items-center justify-center p-4" @click.self="close">
    <div class="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900">引用格式</h3>
        <button class="text-gray-400 hover:text-gray-700 text-xl leading-none" @click="close">×</button>
      </div>

      <!-- ISBN / DOI fetch row -->
      <div v-if="source === 'book'" class="px-6 py-3 border-b border-gray-100 bg-gray-50/60 space-y-2">
        <div class="flex gap-2 items-center">
          <span class="text-xs text-gray-500 w-12">ISBN</span>
          <input v-model="isbnInput" placeholder="9787100074216"
                 class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-300" />
          <button class="px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-40"
                  :disabled="fetching" @click="fetchByIsbn">抓取</button>
        </div>
        <div class="flex gap-2 items-center">
          <span class="text-xs text-gray-500 w-12">DOI</span>
          <input v-model="doiInput" placeholder="10.1093/oxfordhb/9780199588992.013.0001"
                 class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-300" />
          <button class="px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-40"
                  :disabled="fetching" @click="fetchByDoi">抓取</button>
        </div>
        <p v-if="fetchMsg" class="text-xs" :class="fetchMsgKind === 'err' ? 'text-red-500' : 'text-emerald-600'">{{ fetchMsg }}</p>
      </div>
      <div v-else-if="source === 'journal'" class="px-6 py-3 border-b border-gray-100 bg-gray-50/60">
        <div class="flex gap-2 items-center">
          <span class="text-xs text-gray-500 w-12">DOI</span>
          <input v-model="doiInput" placeholder="10.1086/715789"
                 class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-300" />
          <button class="px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-40"
                  :disabled="fetching" @click="fetchByDoi">抓取</button>
        </div>
        <p v-if="fetchMsg" class="mt-2 text-xs" :class="fetchMsgKind === 'err' ? 'text-red-500' : 'text-emerald-600'">{{ fetchMsg }}</p>
      </div>

      <div class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        <div v-if="loading" class="text-center text-gray-400 py-8">載入引用格式…</div>
        <template v-else>
          <div v-for="row in displayStyles" :key="row.key"
               class="border border-gray-100 rounded-xl p-4 bg-gray-50/40 hover:bg-gray-50 transition">
            <div class="flex items-start justify-between gap-3 mb-1.5">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ row.label }}</p>
              <button class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-blue-300 hover:text-blue-600"
                      @click="copy(row.value)">{{ copiedKey === row.key ? '已複製' : '複製' }}</button>
            </div>
            <pre class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-sans">{{ stripMarkdownItalics(row.value) }}</pre>
          </div>
          <div v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</div>
        </template>
      </div>

      <div class="flex items-center justify-between px-6 py-3 border-t border-gray-100 bg-gray-50/40">
        <a v-if="id"
           :href="`/api/citations/bibtex?source=${source}&id=${id}`"
           class="text-xs px-3 py-1.5 rounded-lg border border-emerald-300 text-emerald-700 hover:bg-emerald-50"
           target="_blank">下載 .bib</a>
        <button class="text-xs px-3 py-1.5 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300" @click="close">關閉</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

const props = defineProps<{
  open: boolean;
  source: 'book' | 'journal';
  id?: string | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'metadata-fetched', payload: Record<string, any>): void;
}>();

const loading = ref(false);
const errorMsg = ref('');
const styles = ref<Record<string, string>>({});
const copiedKey = ref('');

const isbnInput = ref('');
const doiInput = ref('');
const fetching = ref(false);
const fetchMsg = ref('');
const fetchMsgKind = ref<'ok' | 'err'>('ok');

const STYLE_LABELS: Array<[string, string]> = [
  ['chicago-notes-footnote',     'Chicago 注釋（首次）'],
  ['chicago-notes-bibliography', 'Chicago 參考書目'],
  ['chicago-author-date',        'Chicago 作者-年代'],
  ['chicago-author-date-intext', 'Chicago 文中引註'],
  ['sbl',                        'SBL Handbook of Style'],
  ['apa',                        'APA 7'],
  ['bibtex',                     'BibTeX'],
];

const displayStyles = computed(() =>
  STYLE_LABELS.map(([key, label]) => ({ key, label, value: styles.value[key] || '' }))
);

async function load() {
  if (!props.id || !props.open) return;
  loading.value = true;
  errorMsg.value = '';
  try {
    const data = await authedFetch<{ styles: Record<string, string> }>(
      `/api/citations/format?source=${props.source}&id=${props.id}`,
    );
    styles.value = data.styles || {};
  } catch (e: any) {
    errorMsg.value = e?.data?.message || e?.message || '載入失敗';
  } finally {
    loading.value = false;
  }
}

async function fetchByIsbn() {
  if (!isbnInput.value.trim()) return;
  fetching.value = true;
  fetchMsg.value = '';
  try {
    const data: any = await authedFetch(`/api/citations/fetch?isbn=${encodeURIComponent(isbnInput.value.trim())}`);
    emit('metadata-fetched', data);
    fetchMsgKind.value = 'ok';
    fetchMsg.value = `已抓到：${data.title || '(無標題)'}，請確認後儲存`;
  } catch (e: any) {
    fetchMsgKind.value = 'err';
    fetchMsg.value = e?.data?.message || '抓取失敗';
  } finally {
    fetching.value = false;
  }
}

async function fetchByDoi() {
  if (!doiInput.value.trim()) return;
  fetching.value = true;
  fetchMsg.value = '';
  try {
    const data: any = await authedFetch(`/api/citations/fetch?doi=${encodeURIComponent(doiInput.value.trim())}`);
    emit('metadata-fetched', data);
    fetchMsgKind.value = 'ok';
    fetchMsg.value = `已抓到：${data.title || '(無標題)'}，請確認後儲存`;
  } catch (e: any) {
    fetchMsgKind.value = 'err';
    fetchMsg.value = e?.data?.message || '抓取失敗';
  } finally {
    fetching.value = false;
  }
}

function copy(text: string) {
  if (!text) return;
  navigator.clipboard.writeText(stripMarkdownItalics(text));
  copiedKey.value = text;
  setTimeout(() => copiedKey.value = '', 1500);
}

// formatter outputs use *italic* markdown for journal/book titles; copy
// plain text without the asterisks so it pastes cleanly into Word/Pages.
function stripMarkdownItalics(s: string): string {
  return (s || '').replace(/\*([^*]+)\*/g, '$1');
}

function close() {
  fetchMsg.value = '';
  emit('close');
}

watch(() => [props.open, props.id], () => {
  if (props.open && props.id) load();
});
</script>
