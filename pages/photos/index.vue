<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink to="/" class="text-sm text-stone-500 hover:text-stone-900 transition">← 首頁</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-4xl mx-auto px-6 py-10">
      <header class="mb-8 border-b border-stone-300/60 pb-4">
        <p class="text-[10px] uppercase tracking-[0.25em] text-stone-500 mb-1">Photo Library</p>
        <h1 class="text-3xl font-serif text-stone-900 tracking-tight">照片庫</h1>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <NuxtLink
          v-for="lib in libraries"
          :key="lib.slug"
          :to="libUrl(lib.slug)"
          class="lib-card group"
        >
          <div class="lib-card__icon">{{ libIcon(lib.slug) }}</div>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="lib-card__name">{{ lib.name }}</span>
            <span class="lib-card__arrow" aria-hidden="true">→</span>
          </div>
          <div class="mt-1 text-[11px] tracking-widest uppercase text-stone-500">
            {{ lib.layout === 'year-month' ? '年／月／事件' : '事件資料夾' }}
          </div>
          <div class="mt-3 flex items-baseline justify-between gap-2 border-t border-stone-200/80 pt-3">
            <span class="text-stone-800 font-serif text-2xl leading-none">
              {{ lib.totalFiles.toLocaleString() }}
            </span>
            <span class="text-[10px] tracking-widest uppercase text-stone-500">
              張 · {{ lib.topFolders }} 個資料夾
            </span>
          </div>
        </NuxtLink>
      </div>

      <p class="mt-10 text-center text-[11px] text-stone-400 tracking-wider">
        全部從 Google Drive 本機鏡像直接讀取
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: "照片庫 — 知識圖工作室" });

interface LibraryItem {
  slug: 'chenwei' | 'training' | 'hongshi';
  name: string;
  layout: 'year-month' | 'folders';
  totalFiles: number;
  topFolders: number;
}

const loading = ref(true);
const errMsg = ref("");
const libraries = ref<LibraryItem[]>([]);

function libUrl(slug: string) {
  return slug === 'chenwei' ? '/photos/chenwei' : `/photos/${slug}`;
}
function libIcon(slug: string) {
  if (slug === 'chenwei') return '📷';
  if (slug === 'training') return '💪';
  if (slug === 'hongshi') return '🪷';
  return '📁';
}

onMounted(async () => {
  try {
    const r = await authedFetch<{ libraries: LibraryItem[] }>("/api/photos/libraries");
    libraries.value = r.libraries || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.lib-card {
  position: relative;
  display: block;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 16px;
  padding: 18px 20px 16px;
  text-decoration: none;
  color: inherit;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.lib-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px -16px rgba(60, 30, 0, 0.2);
  border-color: rgb(168 162 158 / 0.9);
}
.lib-card__icon {
  font-size: 28px;
  line-height: 1;
}
.lib-card__name {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: 1.4rem;
  font-weight: 500;
  color: rgb(41 37 36);
  letter-spacing: -0.01em;
}
.lib-card__arrow {
  color: rgb(168 162 158);
  font-size: 14px;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .25s ease, transform .25s ease;
}
.lib-card:hover .lib-card__arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
