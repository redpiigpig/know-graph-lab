<template>
  <div class="min-h-screen bg-[#f5f1ea]">
    <AppHeader>
      <template #actions>
        <NuxtLink :to="`/photos/chenwei/${year}`" class="text-sm text-stone-500 hover:text-stone-900 transition">← {{ year }}</NuxtLink>
      </template>
    </AppHeader>

    <div class="max-w-7xl mx-auto px-6 py-14">
      <nav class="hidden sm:flex text-[10px] uppercase tracking-[0.2em] text-stone-500 mb-3 flex-wrap items-center">
        <NuxtLink to="/photos" class="hover:text-stone-900">照片庫</NuxtLink>
        <span class="mx-2">/</span>
        <NuxtLink to="/photos/chenwei" class="hover:text-stone-900">辰瑋相片</NuxtLink>
        <span class="mx-2">/</span>
        <NuxtLink :to="`/photos/chenwei/${year}`" class="hover:text-stone-900">{{ year }}</NuxtLink>
        <span class="mx-2">/</span>
        <span class="text-stone-700">{{ headerLabel }}</span>
      </nav>

      <header class="mb-10 flex items-end justify-between flex-wrap gap-4 border-b border-stone-300/60 pb-6">
        <div class="flex items-end gap-3">
          <h1 v-if="isMonth" class="font-serif text-6xl text-stone-900 leading-none tracking-tight">
            {{ Number(segment) }}<span class="text-2xl text-stone-500 ml-1">月</span>
          </h1>
          <h1 v-else class="font-serif text-5xl text-stone-900 leading-none tracking-tight flex items-center gap-3">
            <span class="text-4xl">{{ sourceIcon }}</span>{{ headerLabel }}
          </h1>
          <p v-if="isMonth" class="text-stone-500 text-sm pb-2">{{ year }} ／ {{ monthName }}</p>
          <p v-else class="text-stone-500 text-sm pb-2">{{ year }} 年</p>
        </div>
        <div v-if="!loading" class="flex items-center gap-4 flex-wrap justify-end">
          <div class="text-right font-serif">
            <div class="text-3xl text-stone-800 leading-none">{{ files.length.toLocaleString() }}</div>
            <div class="mt-2 text-[10px] uppercase tracking-[0.25em] text-stone-500">張</div>
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
      <div v-else-if="!files.length" class="py-20 text-center">
        <div class="font-serif text-2xl text-stone-300 mb-2">— 空 —</div>
        <div class="text-stone-500 text-sm">這裡沒有檔案</div>
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
        <button
          v-for="(f, i) in files"
          :key="f.name"
          @click="onTileClick(i)"
          class="photo-tile group"
          :class="{ 'photo-tile--selected': selectMode && selected.has(f.name) }"
        >
          <img
            v-if="f.kind === 'image' && renderableImage(f.ext)"
            :src="f.url"
            :alt="f.name"
            loading="lazy"
            decoding="async"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <video
            v-else-if="f.kind === 'video'"
            :src="`${f.url}#t=0.1`"
            preload="metadata"
            muted
            playsinline
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex flex-col items-center justify-center text-stone-400 bg-stone-100 p-3">
            <div class="text-3xl">📄</div>
            <div class="mt-1 text-[10px] uppercase tracking-widest">{{ f.ext.replace('.', '') }}</div>
          </div>
          <span v-if="f.kind === 'video'" class="photo-tile__play" aria-hidden="true">▶</span>
          <span class="photo-tile__badge" :title="sourceTitle(f.source)">
            {{ tileIcon(f.kind, f.source) }}
          </span>
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
  source: "photo" | "screenshot" | "download" | "event";
  ext: string;
  size: number;
  mtime: number;
  url: string;
}

const route = useRoute();
const year = computed(() => String(route.params.year || ""));
const segment = computed(() => String(route.params.month || ""));
const isMonth = computed(() => /^(0[1-9]|1[0-2])$/.test(segment.value));
const isEvent = computed(() =>
  !isMonth.value && segment.value !== "screenshots" && segment.value !== "downloads"
);
const headerLabel = computed(() =>
  isMonth.value ? `${Number(segment.value)} 月`
  : segment.value === "screenshots" ? "截圖"
  : segment.value === "downloads" ? "下載"
  : decodeURIComponent(segment.value)
);
const sourceIcon = computed(() =>
  segment.value === "screenshots" ? "📸"
  : segment.value === "downloads" ? "🌐"
  : isEvent.value ? "📁"
  : ""
);

useHead({ title: () => `${year.value} ${headerLabel.value} — 辰瑋相片` });

const MONTH_NAMES = ["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"];
const monthName = computed(() =>
  isMonth.value ? (MONTH_NAMES[Number(segment.value) - 1] || "") : ""
);

const loading = ref(true);
const errMsg = ref("");
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
    const items = Array.from(selected.value).map((name) => ({
      year: year.value, segment: segment.value, name,
    }));
    const r = await authedFetch<{ deleted: number; errors: { item: unknown; error: string }[] }>(
      "/api/photos/delete",
      { method: "POST", body: { items } }
    );
    const removedNames = new Set(
      items.slice(0, r.deleted).map((it) => it.name)
    );
    // 簡單作法：移除所有「沒在 errors 裡」的 name；errors 中的留下
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
function tileIcon(kind: string, source: string) {
  if (source === "screenshot") return "📸";
  if (source === "download") return "🌐";
  if (source === "event") return "📁";
  if (kind === "video") return "🎬";
  return "📱";
}
function sourceTitle(source: string) {
  if (source === "screenshot") return "螢幕截圖";
  if (source === "download") return "網路下載";
  if (source === "event") return "事件資料夾";
  return "手機／相機拍攝";
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
  // 水平滑超過 50px、時間 < 600ms、水平 > 垂直 → 視為滑動
  if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && dt < 600) {
    if (dx < 0) next(); else prev();
  }
}

onMounted(async () => {
  window.addEventListener("keydown", onKey);
  try {
    const r = await authedFetch<{ files: PhotoFile[] }>(
      `/api/photos/${year.value}/${encodeURIComponent(segment.value)}/files`
    );
    files.value = r.files || [];
  } catch (e: unknown) {
    errMsg.value = (e as { message?: string })?.message ?? String(e);
  } finally {
    loading.value = false;
  }
});
onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>

<style scoped>
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
.photo-tile__badge {
  position: absolute;
  top: 6px;
  right: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  border-radius: 8px;
  z-index: 2;
  pointer-events: none;
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
