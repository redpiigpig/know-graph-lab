<template>
  <div v-if="open" class="fixed inset-0 z-[100] bg-black/40 flex items-center justify-center p-4" @click.self="close">
    <div class="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
      <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
        <div>
          <h3 class="text-base font-semibold text-gray-900">批次匯入 ISBN / DOI</h3>
          <p class="text-xs text-gray-500 mt-0.5">一行一筆。ISBN 進書本表；DOI 自動判斷期刊文章或書本</p>
        </div>
        <button class="text-gray-400 hover:text-gray-700 text-xl leading-none" @click="close">×</button>
      </div>

      <div class="px-5 py-3 border-b border-gray-100 space-y-2">
        <textarea v-model="raw" rows="8"
          placeholder="9780199588992&#10;10.1086/715789&#10;978-9570525823&#10;10.1093/oxfordhb/9780199588992.013.0001"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono outline-none focus:ring-2 focus:ring-purple-400" />
        <div class="flex items-center justify-between text-xs">
          <span class="text-gray-500">總共 {{ lineCount }} 行</span>
          <button class="px-3 py-1.5 rounded bg-purple-600 text-white hover:bg-purple-500 disabled:opacity-40"
                  :disabled="!lineCount || importing" @click="run">
            {{ importing ? `匯入中… (${doneCount}/${lineCount})` : '開始匯入' }}
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto px-5 py-3">
        <div v-if="result" class="mb-3 text-xs text-gray-600">
          <span class="text-emerald-600">✔ 新增 {{ result.created }}</span>
          ·
          <span class="text-amber-600">⊙ 已存在 {{ result.exists }}</span>
          ·
          <span class="text-red-500">✗ 失敗 {{ result.errors }}</span>
        </div>
        <div v-if="result?.results?.length" class="space-y-1.5">
          <div v-for="(r, i) in result.results" :key="i"
            class="border border-gray-100 rounded-lg px-3 py-2 text-xs flex items-start gap-2"
            :class="{
              'bg-emerald-50/40 border-emerald-100': r.status === 'created',
              'bg-amber-50/40 border-amber-100':    r.status === 'exists',
              'bg-red-50/40 border-red-100':        r.status === 'error',
            }">
            <span class="font-mono text-[10px] text-gray-400 w-4 text-right pt-0.5">{{ i + 1 }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-gray-700 truncate">
                <code class="text-[11px] text-gray-500">{{ r.input }}</code>
                <span v-if="r.status === 'created'" class="ml-2 text-emerald-600">新增</span>
                <span v-else-if="r.status === 'exists'" class="ml-2 text-amber-600">已存在</span>
                <span v-else class="ml-2 text-red-500">錯誤</span>
              </p>
              <p v-if="r.title" class="text-gray-700 text-[12px] mt-0.5">
                <NuxtLink v-if="r.id && r.kind === 'book'" :to="`/excerpts/library/${r.id}`" class="hover:underline">
                  《{{ r.title }}》
                </NuxtLink>
                <NuxtLink v-else-if="r.id && r.kind === 'journal'" :to="`/excerpts/journal/${r.id}`" class="hover:underline">
                  {{ r.title }}
                </NuxtLink>
                <span v-else>{{ r.title }}</span>
              </p>
              <p v-if="r.error" class="text-red-500 text-[11px] mt-0.5">{{ r.error }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="px-5 py-3 border-t border-gray-100 bg-gray-50/40 flex justify-end gap-2">
        <button class="px-3 py-1.5 text-xs rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300" @click="close">關閉</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'done'): void;
}>();

const raw = ref('');
const importing = ref(false);
const result = ref<any>(null);
const doneCount = ref(0);

const lineCount = computed(() =>
  raw.value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean).length
);

async function run() {
  const items = raw.value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
  if (!items.length) return;
  importing.value = true;
  doneCount.value = 0;
  result.value = null;
  try {
    result.value = await authedFetch('/api/citations/bulk-import', {
      method: 'POST',
      body: { items },
    });
    doneCount.value = items.length;
    emit('done');
  } catch (e: any) {
    alert(e?.data?.message || '匯入失敗');
  } finally {
    importing.value = false;
  }
}

function close() { emit('close'); }

watch(() => props.open, (v) => {
  if (v) { raw.value = ''; result.value = null; }
});
</script>
