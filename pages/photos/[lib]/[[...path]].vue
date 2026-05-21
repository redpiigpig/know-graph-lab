<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink :to="backUrl" class="text-sm text-stone-500 hover:text-stone-900 transition">
          ← {{ backLabel }}
        </NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-7xl mx-auto px-6 py-10">
      <nav class="hidden sm:flex text-[10px] uppercase tracking-[0.2em] text-stone-500 mb-3 flex-wrap items-center gap-y-1">
        <NuxtLink to="/photos" class="hover:text-stone-900">照片庫</NuxtLink>
        <span class="mx-2">/</span>
        <NuxtLink :to="`/photos/${lib}`" class="hover:text-stone-900">{{ libName }}</NuxtLink>
        <template v-for="(seg, i) in pathSegs" :key="i">
          <span class="mx-2">/</span>
          <NuxtLink
            v-if="i < pathSegs.length - 1"
            :to="urlForDepth(i + 1)"
            class="hover:text-stone-900 normal-case"
          >{{ seg }}</NuxtLink>
          <span v-else class="text-stone-700 normal-case">{{ seg }}</span>
        </template>
      </nav>

      <header class="mb-8 flex items-end justify-between flex-wrap gap-3 border-b border-stone-300/60 pb-4">
        <div class="flex items-end gap-3 min-w-0">
          <span class="text-4xl">{{ libIcon }}</span>
          <div class="min-w-0">
            <h1 class="font-serif text-3xl text-stone-900 leading-none tracking-tight truncate">
              {{ headerTitle }}
            </h1>
            <p v-if="pathSegs.length === 0" class="mt-1 text-[10px] uppercase tracking-[0.25em] text-stone-500">
              事件資料夾
            </p>
          </div>
        </div>
        <div v-if="!loading" class="flex items-center gap-4 flex-wrap justify-end">
          <div class="text-right font-serif">
            <div class="text-2xl text-stone-800 leading-none">
              {{ (folders.length + files.length).toLocaleString() }}
            </div>
            <div class="mt-1 text-[10px] uppercase tracking-[0.25em] text-stone-500">
              {{ folders.length }} 資料夾 · {{ files.length }} 張
            </div>
          </div>
          <div v-if="files.length" class="flex items-center gap-2 flex-wrap">
            <button
              v-if="!selectMode"
              @click="enterSelect"
              class="text-[11px] uppercase tracking-widest px-3 py-1.5 border border-stone-300 rounded hover:bg-stone-100 transition"
            >選取</button>
            <template v-else>
              <span class="text-[11px] uppercase tracking-widest text-stone-500">{{ selected.size }} 張</span>
              <button
                @click="deleteSelected"
                :disabled="selected.size === 0 || deleting"
                class="text-[11px] uppercase tracking-widest px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-40"
              >{{ deleting ? '刪除中…' : `刪除 ${selected.size}` }}</button>
              <button
                @click="exitSelect"
                class="text-[11px] uppercase tracking-widest px-3 py-1.5 border border-stone-300 rounded hover:bg-stone-100 transition"
              >取消</button>
            </template>
          </div>
        </div>
      </header>

      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="errMsg" class="text-red-500 text-sm">{{ errMsg }}</div>
      <div v-else-if="!folders.length && !files.length" class="py-20 text-center">
        <div class="font-serif text-2xl text-stone-300 mb-2">— 空 —</div>
        <div class="text-stone-500 text-sm">這個資料夾裡沒有東西</div>
      </div>

      <template v-else>
        <section v-if="folders.length" class="mb-10">
          <p class="text-[10px] uppercase tracking-[0.25em] text-stone-500 mb-3">資料夾</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            <NuxtLink
              v-for="f in folders"
              :key="f.name"
              :to="folderUrl(f.name)"
              class="folder-card"
              :title="f.name"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="text-xl shrink-0">📁</span>
                <span class="folder-card__name truncate">{{ f.name }}</span>
              </div>
              <div class="mt-1 text-[10px] tracking-widest uppercase text-stone-500">
                <span v-if="f.fileCount > 0" class="text-stone-700">
                  {{ f.fileCount.toLocaleString() }}<span class="ml-1">張</span>
                </span>
                <span v-if="f.subfolderCount > 0" class="ml-2">
                  · {{ f.subfolderCount }} 子資料夾
                </span>
                <span v-if="f.fileCount === 0 && f.subfolderCount === 0">—</span>
              </div>
            </NuxtLink>
          </div>
        </section>

        <section v-if="files.length">
          <p v-if="folders.length" class="text-[10px] uppercase tracking-[0.25em] text-stone-500 mb-3">照片</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            <button
              v-for="(f, i) in files"
              :key="f.name"
              @click="onTileClick(i)"
              class="photo-tile group"
              :class="{ 'photo-tile--selected': selectMode && selected.has(f.name) }"
            >
              <img
                v-if="f.kind === 'image' && renderableImage(f.ext)"
                :src="thumbUrl(f.url, 480)"
                :alt="f.name"
                loading="lazy"
                decoding="async"
                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <LazyVideoTile
                v-else-if="f.kind === 'video'"
                :src="f.url"
                cls="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex flex-col items-center justify-center text-stone-400 bg-stone-100 p-3">
                <div class="text-3xl">📄</div>
                <div class="mt-1 text-[10px] uppercase tracking-widest">{{ f.ext.replace('.', '') }}</div>
              </div>
              <span v-if="f.kind === 'video'" class="photo-tile__play" aria-hidden="true">▶</span>
              <span
                v-if="selectMode"
                class="photo-tile__check"
                :class="{ 'photo-tile__check--on': selected.has(f.name) }"
              >{{ selected.has(f.name) ? '✓' : '' }}</span>
              <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent text-white text-[10px] px-2 py-1.5 truncate text-left opacity-0 group-hover:opacity-100 transition">
                {{ f.name }}
              </div>
            </button>
          </div>
        </section>
      </template>
    </div>

    <div
      v-if="viewerIndex !== null && current"
      class="fixed inset-0 bg-black/95 z-50 flex flex-col"
      @click.self="viewerIndex = null"
      @touchstart.passive="onTouchStart"
      @touchend="onTouchEnd"
      tabindex="0"
    >
      <div class="flex items-center justify-between px-6 py-4 text-white border-b border-white/10">
        <div class="text-sm truncate max-w-[55%] font-mono text-white/80">{{ current.name }}</div>
        <div class="flex items-center gap-5 text-sm">
          <span class="text-white/50 font-mono">{{ (viewerIndex ?? 0) + 1 }} / {{ files.length }}</span>
          <a :href="current.url" :download="current.name" class="hover:text-amber-300 transition" @click.stop>下載</a>
          <button @click="viewerIndex = null" class="hover:text-amber-300 transition">關閉 ✕</button>
        </div>
      </div>
      <div class="flex-1 flex items-center justify-between min-h-0">
        <button @click.stop="prev" class="text-white/60 hover:text-white text-4xl px-6 transition" aria-label="prev">‹</button>
        <div class="flex-1 h-full flex items-center justify-center min-h-0 p-4" @click.self="viewerIndex = null">
          <img
            v-if="current.kind === 'image' && renderableImage(current.ext)"
            :src="thumbUrl(current.url, 1600)"
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
          <div v-else class="text-stone-400 text-center p-8">
            <div class="text-5xl mb-2">📄</div>
            <div class="text-sm">{{ current.name }}</div>
            <div class="text-xs mt-2">無法在瀏覽器預覽此格式</div>
            <a :href="current.url" :download="current.name" class="mt-4 inline-block px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded text-xs">下載原檔</a>
          </div>
        </div>
        <button @click.stop="next" class="text-white/60 hover:text-white text-4xl px-6 transition" aria-label="next">›</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });

interface PhotoFile {
  name: string;
  kind: "image" | "video";
  source: string;
  ext: string;
  size: number;
  mtime: number;
  url: string;
}
interface FolderNode {
  name: string;
  fileCount: number;
  subfolderCount: number;
}

const LIB_META: Record<string, { name: string; icon: string }> = {
  chenwei: { name: '辰瑋相片', icon: '📷' },
  training: { name: '訓練相片', icon: '💪' },
  hongshi: { name: '弘誓相片', icon: '🪷' },
};

const route = useRoute();
const lib = computed(() => String(route.params.lib || ""));
const pathSegs = computed<string[]>(() => {
  const p = route.params.path;
  if (!p) return [];
  return (Array.isArray(p) ? p : [p]).map((s) => decodeURIComponent(String(s)));
});

const libName = computed(() => LIB_META[lib.value]?.name ?? lib.value);
const libIcon = computed(() => LIB_META[lib.value]?.icon ?? '📁');
const headerTitle = computed(() =>
  pathSegs.value.length ? pathSegs.value[pathSegs.value.length - 1] : libName.value
);
const backLabel = computed(() => pathSegs.value.length ? '上一層' : '照片庫');
const backUrl = computed(() => {
  if (pathSegs.value.length === 0) return '/photos';
  if (pathSegs.value.length === 1) return `/photos/${lib.value}`;
  return urlForDepth(pathSegs.value.length - 1);
});

useHead({ title: () => `${headerTitle.value} — ${libName.value}` });

function urlForDepth(d: number) {
  const segs = pathSegs.value.slice(0, d).map(encodeURIComponent);
  return `/photos/${lib.value}/${segs.join('/')}`;
}
function folderUrl(name: string) {
  const segs = [...pathSegs.value, name].map(encodeURIComponent);
  return `/photos/${lib.value}/${segs.join('/')}`;
}

const loading = ref(true);
const errMsg = ref("");
const folders = ref<FolderNode[]>([]);
const files = ref<PhotoFile[]>([]);
const viewerIndex = ref<number | null>(null);
const current = computed(() => (viewerIndex.value === null ? null : files.value[viewerIndex.value] ?? null));

const selectMode = ref(false);
const selected = ref<Set<string>>(new Set());
const deleting = ref(false);

function enterSelect() {
  selectMode.value = true;
  selected.value = new Set();
  viewerIndex.value = null;
}
function exitSelect() {
  selectMode.value = false;
  selected.value = new Set();
}
function onTileClick(i: number) {
  if (selectMode.value) {
    const n = files.value[i]?.name;
    if (!n) return;
    const s = new Set(selected.value);
    if (s.has(n)) s.delete(n); else s.add(n);
    selected.value = s;
  } else {
    viewerIndex.value = i;
  }
}
async function deleteSelected() {
  if (!selected.value.size || deleting.value) return;
  deleting.value = true;
  try {
    const subpath = pathSegs.value.join('/');
    const items = Array.from(selected.value).map((name) => ({ path: subpath, name }));
    const r = await authedFetch<{ deleted: number; errors: { item: unknown; error: string }[] }>(
      `/api/photos/lib/${lib.value}/delete`,
      { method: "POST", body: { items } }
    );
    const errorNames = new Set((r.errors || []).map((e) => (e.item as { name: string }).name));
    files.value = files.value.filter((f) => !(selected.value.has(f.name) && !errorNames.has(f.name)));
    exitSelect();
    if (r.errors?.length) {
      errMsg.value = `刪除 ${r.deleted} 張；${r.errors.length} 張失敗：${r.errors[0]?.error || ''}`;
    }
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    deleting.value = false;
  }
}

function renderableImage(ext: string) {
  return [".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp"].includes(ext);
}
function thumbUrl(url: string, width: number): string {
  return url.replace(/\/file\?/, "/thumb?") + `&w=${width}`;
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

const touchStart = { x: 0, y: 0, t: 0 };
function onTouchStart(e: TouchEvent) {
  const t = e.touches[0];
  if (!t) return;
  touchStart.x = t.clientX;
  touchStart.y = t.clientY;
  touchStart.t = Date.now();
}
function onTouchEnd(e: TouchEvent) {
  const t = e.changedTouches[0];
  if (!t) return;
  const dx = t.clientX - touchStart.x;
  const dy = t.clientY - touchStart.y;
  const dt = Date.now() - touchStart.t;
  if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && dt < 600) {
    if (dx < 0) next(); else prev();
  }
}

async function load() {
  loading.value = true;
  errMsg.value = "";
  folders.value = [];
  files.value = [];
  viewerIndex.value = null;
  try {
    if (!(lib.value in LIB_META)) {
      throw new Error(`未知的相簿：${lib.value}`);
    }
    const subpath = pathSegs.value.join('/');
    const r = await authedFetch<{ folders: FolderNode[]; files: PhotoFile[] }>(
      `/api/photos/lib/${lib.value}/list?path=${encodeURIComponent(subpath)}`
    );
    folders.value = r.folders || [];
    files.value = r.files || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  window.addEventListener("keydown", onKey);
  load();
});
onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
watch(() => route.fullPath, load);
</script>

<style scoped>
.folder-card {
  display: block;
  background: #fdfbf6;
  border: 1px solid rgb(214 211 209 / 0.7);
  border-radius: 12px;
  padding: 12px 14px;
  text-decoration: none;
  color: inherit;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.folder-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px -14px rgba(60, 30, 0, 0.18);
  border-color: rgb(168 162 158 / 0.9);
}
.folder-card__name {
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: 1.1rem;
  color: rgb(41 37 36);
  letter-spacing: -0.005em;
}

.photo-tile {
  position: relative;
  display: block;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: 14px;
  background: rgb(245 241 234);
  border: 1px solid rgb(214 211 209 / 0.6);
  cursor: pointer;
  transition: transform .35s ease, box-shadow .35s ease, border-color .35s ease;
}
.photo-tile:hover {
  border-color: rgb(168 162 158 / 0.9);
  box-shadow: 0 14px 30px -16px rgba(60, 30, 0, 0.25);
}
.photo-tile:focus-visible {
  outline: 2px solid rgb(217 119 6);
  outline-offset: 2px;
}
.photo-tile--selected {
  outline: 3px solid rgb(217 119 6);
  outline-offset: -3px;
}
.photo-tile__check {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  border: 1.5px solid rgb(168 162 158);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: rgb(168 162 158);
  z-index: 3;
  pointer-events: none;
}
.photo-tile__check--on {
  background: rgb(217 119 6);
  border-color: rgb(217 119 6);
  color: white;
}
.photo-tile__play {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  padding-left: 2px;
  z-index: 2;
  pointer-events: none;
}
</style>
