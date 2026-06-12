<template>
  <div class="min-h-screen bg-stone-100 text-stone-900 flex flex-col">
    <!-- Topbar -->
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink :to="`/ebook/${id}?text=1`" class="text-stone-500 hover:text-stone-900 text-sm flex-shrink-0">← 文字版</NuxtLink>
          <span class="text-stone-300">·</span>
          <button @click="tocOpen = !tocOpen"
            :class="['flex items-center gap-1 px-2 py-1 rounded-md text-xs border flex-shrink-0',
              tocOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400']">
            <span>📑</span><span class="hidden sm:inline">目錄</span>
            <span v-if="toc.length" class="text-[10px] opacity-60">({{ toc.length }})</span>
          </button>
          <span class="text-sm font-medium truncate">{{ title }}</span>
          <span class="text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-1.5 py-0.5 flex-shrink-0">原版模式</span>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <span class="text-xs text-stone-400 hidden sm:inline w-12 text-right">{{ percent }}</span>
          <div class="hidden md:flex items-center gap-1 ml-1 pl-2 border-l border-stone-200">
            <button @click="setFont(fontSize - 10)" class="w-7 h-7 rounded bg-stone-100 hover:bg-stone-200 text-xs">A−</button>
            <span class="text-xs text-stone-400 w-10 text-center">{{ fontSize }}%</span>
            <button @click="setFont(fontSize + 10)" class="w-7 h-7 rounded bg-stone-100 hover:bg-stone-200 text-xs">A+</button>
          </div>
          <a :href="`/api/ebooks/${id}/original?download=1`"
            class="hidden md:flex items-center gap-1 px-2 py-1 rounded-md text-xs border bg-white text-stone-600 border-stone-200 hover:border-emerald-400 hover:text-emerald-700">
            <span>⬇️</span><span>原檔</span>
          </a>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 min-h-0">
      <!-- TOC sidebar -->
      <aside v-if="tocOpen" class="w-64 border-r border-stone-200 bg-white overflow-y-auto flex-shrink-0">
        <div v-if="!toc.length" class="p-4 text-xs text-stone-400">此 EPUB 無目錄。</div>
        <ul v-else class="py-2">
          <li v-for="(item, i) in toc" :key="i">
            <button @click="gotoHref(item.href)"
              :class="['w-full text-left px-3 py-1.5 text-xs hover:bg-stone-50 text-stone-700']"
              :style="{ paddingLeft: (12 + item._depth * 12) + 'px' }">
              {{ item.label }}
            </button>
          </li>
        </ul>
      </aside>

      <!-- EPUB rendition — flipbook: big side arrows flank the page -->
      <main class="flex-1 relative overflow-hidden bg-stone-200/50">
        <button @click="prev" :disabled="atStart"
          class="group absolute left-0 top-0 bottom-0 w-16 md:w-24 z-20 flex items-center justify-center
                 disabled:opacity-0 disabled:pointer-events-none transition" aria-label="上一頁">
          <span class="w-10 h-10 rounded-full bg-white/70 group-hover:bg-white shadow flex items-center justify-center text-stone-700 text-xl">‹</span>
        </button>
        <button @click="next" :disabled="atEnd"
          class="group absolute right-0 top-0 bottom-0 w-16 md:w-24 z-20 flex items-center justify-center
                 disabled:opacity-0 disabled:pointer-events-none transition" aria-label="下一頁">
          <span class="w-10 h-10 rounded-full bg-white/70 group-hover:bg-white shadow flex items-center justify-center text-stone-700 text-xl">›</span>
        </button>

        <ClientOnly>
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-stone-500 text-sm z-10">載入中…</div>
          <div v-if="error" class="absolute inset-0 flex items-center justify-center p-6">
            <div class="max-w-md text-center text-rose-600 text-sm bg-white border border-rose-200 rounded-lg p-6">{{ error }}</div>
          </div>
          <!-- epub.js renders its iframe into this element -->
          <div ref="viewerEl" class="absolute inset-0 mx-auto max-w-4xl px-6 md:px-20 py-6"></div>
          <template #fallback>
            <div class="text-stone-500 text-sm pt-10 text-center">準備 EPUB 檢視器…</div>
          </template>
        </ClientOnly>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;

const title = ref("");
const loading = ref(true);
const error = ref("");
const tocOpen = ref(true);
const toc = ref<any[]>([]);
const percent = ref("");
const atStart = ref(true);
const atEnd = ref(false);
const fontSize = ref(110);

const viewerEl = ref<HTMLElement | null>(null);
let book: any = null;
let rendition: any = null;

// API auth is Bearer-token (not cookie). epub.js's own fetch can't carry the
// header, so we fetch the whole EPUB ourselves as an ArrayBuffer and hand the
// binary straight to ePub() — bypassing its internal request entirely.
const supabase = useSupabaseClient();
async function getToken(): Promise<string> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token ?? "";
}

async function loadEpub() {
  try {
    const token = await getToken();
    try {
      const m: any = await authedFetch(`/api/ebooks/${id}?page=1`);
      if (m) title.value = m.title;
    } catch { /* non-fatal */ }

    const resp = await fetch(`/api/ebooks/${id}/original`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) throw new Error(`原檔載入失敗 (${resp.status})`);
    const buf = await resp.arrayBuffer();

    const ePub = (await import("epubjs")).default;
    book = ePub(buf as any);
    await book.ready;

    // Flatten the navigation TOC (depth for indentation).
    const flat: any[] = [];
    const walk = (items: any[], depth: number) => {
      for (const it of items) {
        flat.push({ label: (it.label || "").trim(), href: it.href, _depth: depth });
        if (it.subitems?.length) walk(it.subitems, depth + 1);
      }
    };
    walk(book.navigation?.toc ?? [], 0);
    toc.value = flat;

    rendition = book.renderTo(viewerEl.value!, {
      width: "100%",
      height: "100%",
      flow: "paginated",
      spread: "auto",
      manager: "default",
    });
    applyFont();
    await rendition.display();
    loading.value = false;

    rendition.on("relocated", (loc: any) => {
      atStart.value = !!loc.atStart;
      atEnd.value = !!loc.atEnd;
      const p = loc.start?.percentage;
      if (typeof p === "number") percent.value = Math.round(p * 100) + "%";
    });
    // Keyboard nav also when focus is inside the rendition iframe.
    rendition.on("keyup", onKey);
  } catch (e: any) {
    error.value = "無法載入 EPUB：" + (e?.message || e);
    loading.value = false;
  }
}

function applyFont() {
  rendition?.themes?.fontSize?.(fontSize.value + "%");
}
function setFont(s: number) {
  fontSize.value = Math.max(70, Math.min(220, s));
  applyFont();
}

function next() { rendition?.next(); }
function prev() { rendition?.prev(); }
function gotoHref(href: string) { rendition?.display(href); }

function onKey(e: KeyboardEvent) {
  const tag = (e.target as HTMLElement)?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA") return;
  if (e.key === "ArrowLeft") prev();
  else if (e.key === "ArrowRight") next();
}

onMounted(() => {
  loadEpub();
  window.addEventListener("keyup", onKey);
});
onUnmounted(() => {
  window.removeEventListener("keyup", onKey);
  try { rendition?.destroy(); book?.destroy(); } catch { /* noop */ }
});
</script>
