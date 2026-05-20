<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/" class="hover:text-blue-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>知識圖工作室</span>
            </NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900">概念筆記</span>
          </div>
          <div class="flex items-center gap-2">
            <NuxtLink to="/concepts/graph"
              class="px-3 py-1.5 text-xs rounded-lg border border-cyan-300 text-cyan-700 hover:bg-cyan-50">🕸 概念圖</NuxtLink>
            <button class="px-3 py-1.5 text-xs rounded-lg bg-cyan-600 text-white hover:bg-cyan-500"
              @click="showCreate = true">+ 新概念</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-1">概念筆記</h1>
        <p class="text-gray-500 text-sm">原子化筆記 + <code>[[雙向連結]]</code>，建立跨文獻概念網路</p>
      </div>

      <input v-model="q" placeholder="搜尋概念名稱 / 摘要"
        class="w-full px-4 py-2.5 mb-6 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-cyan-400" />

      <div v-if="loading" class="text-center text-gray-400 py-12">載入中…</div>
      <div v-else-if="!filtered.length" class="text-center text-gray-400 py-12">尚無概念，從右上角「+ 新概念」開始</div>

      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <NuxtLink v-for="c in filtered" :key="c.id" :to="`/concepts/${c.slug}`"
          class="block bg-white border border-gray-200 rounded-xl p-4 hover:border-cyan-300 hover:shadow-sm transition">
          <div class="flex items-start justify-between gap-2 mb-1">
            <h3 class="text-base font-semibold text-gray-900 truncate" :style="c.color ? { color: c.color } : undefined">{{ c.name }}</h3>
            <span class="text-[10px] text-gray-400 whitespace-nowrap">
              ← {{ c.in_count }}  → {{ c.out_count }}
            </span>
          </div>
          <p v-if="c.summary" class="text-xs text-gray-500 line-clamp-2">{{ c.summary }}</p>
          <p v-if="c.aliases?.length" class="mt-1.5 text-[11px] text-gray-400">別名：{{ c.aliases.join('、') }}</p>
        </NuxtLink>
      </div>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" @click.self="showCreate = false">
      <div class="w-full max-w-lg bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">新概念</h3>
        <input v-model="form.name" placeholder="概念名稱（中文 OK）"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" />
        <input v-model="form.aliasesRaw" placeholder="別名，逗號分隔（可省略）"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" />
        <input v-model="form.summary" placeholder="一句話摘要（可省略）"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-3" />
        <textarea v-model="form.body" rows="5" placeholder="markdown 內文，可用 [[其他概念]] 雙向連結"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-3 font-mono" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCreate = false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-cyan-600 text-white rounded-lg" :disabled="!form.name.trim()" @click="create">建立</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

definePageMeta({ middleware: 'auth' });

interface ConceptRow {
  id: string; name: string; slug: string;
  aliases?: string[]; summary?: string | null; color?: string | null;
  out_count: number; in_count: number;
}

const concepts = ref<ConceptRow[]>([]);
const loading = ref(true);
const q = ref('');
const showCreate = ref(false);
const form = ref({ name: '', aliasesRaw: '', summary: '', body: '' });
const router = useRouter();

const filtered = computed(() => {
  const needle = q.value.trim().toLowerCase();
  if (!needle) return concepts.value;
  return concepts.value.filter((c) =>
    c.name.toLowerCase().includes(needle) ||
    (c.summary || '').toLowerCase().includes(needle) ||
    (c.aliases ?? []).some((a) => a.toLowerCase().includes(needle))
  );
});

async function load() {
  loading.value = true;
  try {
    concepts.value = await authedFetch<ConceptRow[]>('/api/concepts');
  } finally { loading.value = false; }
}

async function create() {
  const aliases = form.value.aliasesRaw
    .split(/,|，|、/).map((s) => s.trim()).filter(Boolean);
  const data: any = await authedFetch('/api/concepts', {
    method: 'POST',
    body: {
      name: form.value.name.trim(),
      aliases,
      summary: form.value.summary.trim() || null,
      body: form.value.body,
    },
  });
  showCreate.value = false;
  router.push(`/concepts/${data.slug}`);
}

onMounted(load);
</script>
