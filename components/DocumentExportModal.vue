<template>
  <div v-if="open" class="fixed inset-0 z-[100] bg-black/40 flex items-center justify-center p-4" @click.self="close">
    <div class="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-4xl max-h-[92vh] overflow-hidden flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">引用編號 + 參考書目預覽</h3>
          <p class="text-xs text-gray-500 mt-0.5">解析 <code>[cite:uuid]</code> → 上標編號 + 自動產生 footnotes / bibliography</p>
        </div>
        <button class="text-gray-400 hover:text-gray-700 text-xl leading-none" @click="close">×</button>
      </div>

      <div class="px-6 py-3 border-b border-gray-100 bg-gray-50/60 flex items-center gap-3 text-sm">
        <span class="text-gray-500">引用格式</span>
        <select v-model="style" class="px-2 py-1 border border-gray-200 rounded text-sm bg-white">
          <option value="chicago-notes-bibliography">Chicago Notes-Bibliography（神學常用）</option>
          <option value="sbl">SBL Handbook of Style</option>
          <option value="chicago-author-date">Chicago 作者-年代</option>
          <option value="apa">APA 7</option>
        </select>
        <button class="ml-auto px-3 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-500"
                @click="render">重新產生</button>
      </div>

      <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">
        <div v-if="loading" class="text-center text-gray-400 py-8">解析中…</div>
        <template v-else-if="result">
          <section>
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-gray-700">內文（含上標編號）</h4>
              <button class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-blue-300"
                      @click="copy(result.html_with_footnotes, 'html')">複製 HTML</button>
            </div>
            <div class="prose-preview border border-gray-200 rounded-xl p-4 bg-white" v-html="result.html_with_footnotes"></div>
          </section>

          <section v-if="result.footnote_count">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-gray-700">註腳 ({{ result.footnote_count }})</h4>
              <button class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-blue-300"
                      @click="copy(result.footnotes_html, 'footnotes')">複製註腳</button>
            </div>
            <div class="border border-gray-200 rounded-xl p-4 bg-amber-50/30" v-html="result.footnotes_html"></div>
          </section>

          <section v-if="result.bibliography_markdown">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-gray-700">參考書目（Bibliography）</h4>
              <div class="flex gap-2">
                <button class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-blue-300"
                        @click="copy(result.bibliography_markdown, 'bibmd')">複製 Markdown</button>
                <button class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-blue-300"
                        @click="copy(result.bibliography_html, 'bibhtml')">複製 HTML</button>
              </div>
            </div>
            <div class="border border-gray-200 rounded-xl p-4 bg-emerald-50/30" v-html="result.bibliography_html"></div>
          </section>

          <p v-if="result.missing?.length" class="text-xs text-red-500">
            ⚠ 未對應的 cite UUID：{{ result.missing.join(', ') }}
          </p>

          <p v-if="copyToast" class="text-xs text-emerald-600 text-center">{{ copyToast }}</p>
        </template>
      </div>

      <div class="px-6 py-3 border-t border-gray-100 bg-gray-50/40 flex justify-end gap-2">
        <button class="px-3 py-1.5 text-xs rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300" @click="close">關閉</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

const props = defineProps<{
  open: boolean;
  sourceHtml: string;
}>();

const emit = defineEmits<{ (e: 'close'): void }>();

const style = ref<'chicago-notes-bibliography' | 'sbl' | 'chicago-author-date' | 'apa'>('chicago-notes-bibliography');
const loading = ref(false);
const result = ref<any>(null);
const copyToast = ref('');

async function render() {
  loading.value = true;
  try {
    result.value = await authedFetch('/api/citations/render-document', {
      method: 'POST',
      body: { html: props.sourceHtml, style: style.value },
    });
  } finally { loading.value = false; }
}

function copy(text: string, label: string) {
  navigator.clipboard.writeText(text);
  copyToast.value = `已複製：${label}`;
  setTimeout(() => copyToast.value = '', 1500);
}

function close() { emit('close'); }

watch(() => props.open, (v) => {
  if (v) {
    result.value = null;
    render();
  }
});
watch(style, () => { if (props.open) render(); });
</script>

<style scoped>
.prose-preview :deep(p)  { margin: 0 0 0.4em; line-height: 1.75; color: #374151; font-size: 14px; }
.prose-preview :deep(h1) { font-size: 1.5rem; font-weight: 700; margin: 0.6em 0 0.3em; color: #111827; }
.prose-preview :deep(h2) { font-size: 1.2rem; font-weight: 600; margin: 0.5em 0 0.25em; color: #1f2937; }
.prose-preview :deep(sup a) { text-decoration: none; }
.prose-preview :deep(ul) { list-style: disc; padding-left: 1.4em; }
.prose-preview :deep(ol) { list-style: decimal; padding-left: 1.4em; }
</style>
