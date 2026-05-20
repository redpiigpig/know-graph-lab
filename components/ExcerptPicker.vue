<template>
  <div v-if="open" class="fixed inset-0 z-[100] bg-black/40 flex items-center justify-center p-4" @click.self="close">
    <div class="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col">
      <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
        <h3 class="text-base font-semibold text-gray-900">挑選書摘以插入引用</h3>
        <button class="text-gray-400 hover:text-gray-700 text-xl leading-none" @click="close">×</button>
      </div>

      <div class="px-5 py-3 border-b border-gray-100">
        <input v-model="q" placeholder="搜尋摘文內容 / 書名 / 作者 / 標題"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-400"
          @keyup.enter="search" />
      </div>

      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="text-center text-gray-400 py-8">搜尋中…</div>
        <div v-else-if="!results.length" class="text-center text-gray-400 py-8 text-sm">輸入關鍵字後按 Enter 搜尋</div>
        <button v-for="r in results" :key="r.id"
          class="w-full text-left px-5 py-3 border-b border-gray-100 hover:bg-blue-50 transition"
          @click="pick(r)">
          <p class="text-sm font-medium text-gray-900 line-clamp-1">
            {{ r.title || '(無標題)' }}
          </p>
          <p class="text-xs text-gray-500 mt-0.5">
            <span v-if="r.books">
              {{ r.books.author || '?' }} ·《{{ r.books.title || '?' }}》
            </span>
            <span v-else-if="r.journal_articles">
              {{ r.journal_articles.author || '?' }} ·《{{ r.journal_articles.venue || r.journal_articles.title || '?' }}》
            </span>
            <span v-else class="text-gray-400">未指定來源</span>
            <span v-if="r.page_number" class="ml-2 text-gray-400">頁 {{ r.page_number }}</span>
          </p>
          <p class="text-xs text-gray-600 mt-1 line-clamp-2">{{ r.content }}</p>
        </button>
      </div>

      <div class="px-5 py-3 border-t border-gray-100 text-xs text-gray-500 bg-gray-50/40 flex items-center justify-between">
        <span>選一筆後，<code class="px-1 bg-white border border-gray-200 rounded">[cite:&lt;id&gt;]</code> 會複製到剪貼簿，貼到編輯器游標處即可</span>
        <button class="px-3 py-1 rounded border border-gray-300 text-gray-600 hover:bg-gray-100" @click="close">關閉</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'picked', payload: { id: string; marker: string; toastMsg: string }): void;
}>();

interface ExcerptResult {
  id: string;
  title?: string | null;
  content?: string | null;
  page_number?: string | null;
  books?: { id: string; title: string; author: string } | null;
  journal_articles?: { id: string; title: string; venue: string; author: string } | null;
}

const q = ref('');
const loading = ref(false);
const results = ref<ExcerptResult[]>([]);

async function search() {
  if (!q.value.trim()) { results.value = []; return; }
  loading.value = true;
  try {
    results.value = await authedFetch<ExcerptResult[]>(`/api/excerpts?search=${encodeURIComponent(q.value.trim())}`);
  } finally { loading.value = false; }
}

function pick(r: ExcerptResult) {
  const marker = `[cite:${r.id}]`;
  navigator.clipboard.writeText(marker);
  emit('picked', {
    id: r.id,
    marker,
    toastMsg: `已複製 ${marker}，貼到游標處即可`,
  });
  close();
}

function close() { emit('close'); }

watch(() => props.open, (v) => {
  if (v) {
    q.value = '';
    results.value = [];
    setTimeout(() => {
      (document.querySelector('input[placeholder*="搜尋摘文"]') as HTMLInputElement | null)?.focus();
    }, 50);
  }
});
</script>
