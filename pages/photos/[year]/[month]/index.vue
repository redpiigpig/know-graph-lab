<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader>
      <template #actions>
        <NuxtLink :to="`/photos/${year}`" class="text-sm text-gray-500 hover:text-gray-900 transition">← {{ year }} 年</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-7xl mx-auto px-6 py-10">
      <nav class="text-xs text-gray-500 mb-3">
        <NuxtLink to="/photos" class="hover:text-gray-900">照片管理</NuxtLink>
        <span class="mx-1">/</span>
        <NuxtLink :to="`/photos/${year}`" class="hover:text-gray-900">{{ year }}</NuxtLink>
        <span class="mx-1">/</span>
        <span class="text-gray-900">{{ Number(month) }} 月</span>
      </nav>
      <div class="mb-6 flex items-baseline gap-3">
        <h1 class="text-2xl font-bold text-gray-900">{{ year }} 年 {{ Number(month) }} 月</h1>
        <p class="text-gray-500 text-sm" v-if="!loading">{{ files.length }} 個檔案</p>
      </div>

      <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>
      <div v-else-if="!files.length" class="text-gray-400 text-sm">這個月還沒有照片</div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
        <button
          v-for="(f, i) in files"
          :key="f.name"
          @click="viewerIndex = i"
          class="group relative bg-white rounded-lg overflow-hidden border border-gray-100 hover:border-pink-300 transition aspect-square focus:outline-none focus:ring-2 focus:ring-pink-400"
        >
          <img
            v-if="f.kind === 'image' && renderableImage(f.ext)"
            :src="f.url"
            :alt="f.name"
            loading="lazy"
            decoding="async"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400 p-2">
            <div class="text-3xl">{{ f.kind === 'video' ? '🎬' : '📄' }}</div>
            <div class="mt-1 text-[10px] uppercase">{{ f.ext.replace('.', '') }}</div>
          </div>
          <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent text-white text-[10px] px-1.5 py-1 truncate text-left opacity-0 group-hover:opacity-100 transition">
            {{ f.name }}
          </div>
        </button>
      </div>
    </div>

    <!-- Lightbox -->
    <div
      v-if="viewerIndex !== null && current"
      class="fixed inset-0 bg-black/90 z-50 flex flex-col"
      @click.self="viewerIndex = null"
      @keydown.esc="viewerIndex = null"
      tabindex="0"
    >
      <div class="flex items-center justify-between px-4 py-3 text-white">
        <div class="text-sm truncate max-w-[60%]">{{ current.name }}</div>
        <div class="flex items-center gap-4 text-sm">
          <span class="text-gray-400">{{ (viewerIndex ?? 0) + 1 }} / {{ files.length }}</span>
          <a :href="current.url" :download="current.name" class="hover:text-pink-300" @click.stop>下載</a>
          <button @click="viewerIndex = null" class="hover:text-pink-300">關閉 ✕</button>
        </div>
      </div>
      <div class="flex-1 flex items-center justify-between min-h-0">
        <button @click.stop="prev" class="text-white text-3xl px-4 hover:text-pink-300" aria-label="prev">‹</button>
        <div class="flex-1 h-full flex items-center justify-center min-h-0" @click.self="viewerIndex = null">
          <img
            v-if="current.kind === 'image' && renderableImage(current.ext)"
            :src="current.url"
            :alt="current.name"
            class="max-h-full max-w-full object-contain select-none"
            draggable="false"
          />
          <video
            v-else-if="current.kind === 'video'"
            :src="current.url"
            controls
            autoplay
            class="max-h-full max-w-full"
          />
          <div v-else class="text-gray-400 text-center p-8">
            <div class="text-5xl mb-2">📄</div>
            <div class="text-sm">{{ current.name }}</div>
            <div class="text-xs mt-2">無法在瀏覽器預覽此格式</div>
            <a :href="current.url" :download="current.name" class="mt-4 inline-block px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded text-xs">下載原檔</a>
          </div>
        </div>
        <button @click.stop="next" class="text-white text-3xl px-4 hover:text-pink-300" aria-label="next">›</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });

interface PhotoFile {
  name: string;
  kind: "image" | "video";
  ext: string;
  size: number;
  mtime: number;
  url: string;
}

const route = useRoute();
const year = computed(() => String(route.params.year || ""));
const month = computed(() => String(route.params.month || ""));
useHead({ title: () => `${year.value}.${month.value} — 照片管理` });

const loading = ref(true);
const errMsg = ref("");
const files = ref<PhotoFile[]>([]);
const viewerIndex = ref<number | null>(null);
const current = computed(() => (viewerIndex.value === null ? null : files.value[viewerIndex.value] ?? null));

function renderableImage(ext: string) {
  return [".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp"].includes(ext);
}
function prev() {
  if (viewerIndex.value === null) return;
  viewerIndex.value = (viewerIndex.value - 1 + files.value.length) % files.value.length;
}
function next() {
  if (viewerIndex.value === null) return;
  viewerIndex.value = (viewerIndex.value + 1) % files.value.length;
}

function onKey(e: KeyboardEvent) {
  if (viewerIndex.value === null) return;
  if (e.key === "Escape") viewerIndex.value = null;
  else if (e.key === "ArrowLeft") prev();
  else if (e.key === "ArrowRight") next();
}

onMounted(async () => {
  window.addEventListener("keydown", onKey);
  try {
    const r = await authedFetch<{ files: PhotoFile[] }>(`/api/photos/${year.value}/${month.value}/files`);
    files.value = r.files || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>
