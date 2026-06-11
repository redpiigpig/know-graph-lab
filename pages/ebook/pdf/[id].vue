<template>
  <div class="min-h-screen bg-stone-100 text-stone-900 flex flex-col">
    <!-- Topbar -->
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink :to="`/ebook/${id}`" class="text-stone-500 hover:text-stone-900 text-sm flex-shrink-0">← 文字版</NuxtLink>
          <span class="text-stone-300">·</span>
          <button @click="tocOpen = !tocOpen"
            :class="['flex items-center gap-1 px-2 py-1 rounded-md text-xs border flex-shrink-0',
              tocOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400']">
            <span>📑</span><span class="hidden sm:inline">目錄</span>
            <span v-if="outline.length" class="text-[10px] opacity-60">({{ outline.length }})</span>
          </button>
          <span class="text-sm font-medium truncate">{{ title }}</span>
          <span class="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 flex-shrink-0">原頁模式（原型）</span>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="go(currentPage - 1)" :disabled="currentPage <= 1"
            class="w-8 h-8 rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30">‹</button>
          <input v-model.number="jump" @keyup.enter="go(jump)" type="number" :min="1" :max="numPages || 1"
            class="w-16 bg-white border border-stone-200 rounded-lg px-2 py-1 text-center text-sm" />
          <span class="text-xs text-stone-400">/ {{ numPages || '…' }}</span>
          <button @click="go(currentPage + 1)" :disabled="currentPage >= numPages"
            class="w-8 h-8 rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30">›</button>
          <div class="hidden md:flex items-center gap-1 ml-1 pl-2 border-l border-stone-200">
            <button @click="setScale(scale - 0.2)" class="w-7 h-7 rounded bg-stone-100 hover:bg-stone-200 text-xs">−</button>
            <span class="text-xs text-stone-400 w-10 text-center">{{ Math.round(scale * 100) }}%</span>
            <button @click="setScale(scale + 0.2)" class="w-7 h-7 rounded bg-stone-100 hover:bg-stone-200 text-xs">+</button>
          </div>
          <a :href="`/api/ebooks/${id}/original?download=1`"
            class="hidden md:flex items-center gap-1 px-2 py-1 rounded-md text-xs border bg-white text-stone-600 border-stone-200 hover:border-emerald-400 hover:text-emerald-700">
            <span>⬇️</span><span>原檔</span>
          </a>
          <button @click="showText = !showText"
            :class="['flex items-center gap-1 px-2 py-1 rounded-md text-xs border',
              showText ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-600 border-stone-200 hover:border-stone-400']">
            <span>📝</span><span class="hidden sm:inline">文字</span>
          </button>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 min-h-0">
      <!-- TOC sidebar -->
      <aside v-if="tocOpen" class="w-64 border-r border-stone-200 bg-white overflow-y-auto flex-shrink-0">
        <div v-if="!outline.length" class="p-4 text-xs text-stone-400">此 PDF 無內嵌書籤目錄。<br />可用上方頁碼直接翻頁。</div>
        <ul v-else class="py-2">
          <li v-for="(item, i) in outline" :key="i">
            <button @click="gotoOutline(item)"
              :class="['w-full text-left px-3 py-1.5 text-xs hover:bg-stone-50',
                item._page === currentPage ? 'text-blue-700 font-medium bg-blue-50' : 'text-stone-700']"
              :style="{ paddingLeft: (12 + item._depth * 12) + 'px' }">
              {{ item.title }}
              <span v-if="item._page" class="text-stone-300 ml-1">p{{ item._page }}</span>
            </button>
          </li>
        </ul>
      </aside>

      <!-- PDF page — flipbook: big side arrows flank the page -->
      <main class="flex-1 relative overflow-hidden bg-stone-300/60">
        <!-- left / right flip zones -->
        <button @click="go(currentPage - 1)" :disabled="currentPage <= 1"
          class="group absolute left-0 top-0 bottom-0 w-16 md:w-24 z-20 flex items-center justify-center
                 disabled:opacity-0 disabled:pointer-events-none transition"
          aria-label="上一頁">
          <span class="w-10 h-10 rounded-full bg-white/70 group-hover:bg-white shadow flex items-center justify-center text-stone-700 text-xl">‹</span>
        </button>
        <button @click="go(currentPage + 1)" :disabled="currentPage >= numPages"
          class="group absolute right-0 top-0 bottom-0 w-16 md:w-24 z-20 flex items-center justify-center
                 disabled:opacity-0 disabled:pointer-events-none transition"
          aria-label="下一頁">
          <span class="w-10 h-10 rounded-full bg-white/70 group-hover:bg-white shadow flex items-center justify-center text-stone-700 text-xl">›</span>
        </button>

        <div class="absolute inset-0 overflow-auto flex justify-center items-start p-6 md:px-28">
          <ClientOnly>
            <div class="relative" :class="flipping ? 'flip-anim' : ''">
              <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-stone-500 text-sm">載入中…</div>
              <div v-if="error" class="max-w-md text-center text-rose-600 text-sm bg-white border border-rose-200 rounded-lg p-6">{{ error }}</div>
              <canvas ref="canvasEl" class="shadow-xl bg-white rounded-sm" :class="{ 'opacity-30': loading }" />
            </div>
            <template #fallback>
              <div class="text-stone-500 text-sm pt-10">準備 PDF 檢視器…</div>
            </template>
          </ClientOnly>
        </div>
      </main>

      <!-- OCR text pane -->
      <aside v-if="showText" class="w-[34%] max-w-md border-l border-stone-200 bg-white overflow-y-auto flex-shrink-0">
        <div class="px-4 py-3 border-b border-stone-100 flex items-center justify-between sticky top-0 bg-white">
          <span class="text-xs font-medium text-stone-500">第 {{ currentPage }} 頁文字（OCR，可複製引用）</span>
          <button @click="copyText" class="text-xs text-stone-400 hover:text-stone-700">{{ copied ? '已複製' : '複製' }}</button>
        </div>
        <div class="p-4 text-sm leading-relaxed whitespace-pre-wrap text-stone-800 selection:bg-amber-200">{{ ocrText || '（此頁無 OCR 文字）' }}</div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;

const title = ref("");
const numPages = ref(0);
const currentPage = ref(Number(route.query.page) || 1);
const jump = ref(currentPage.value);
const scale = ref(1.3);
const loading = ref(true);
const error = ref("");
const tocOpen = ref(true);
const showText = ref(false); // OCR text collapsed by default — open on demand
const ocrText = ref("");
const copied = ref(false);
const outline = ref<any[]>([]);
const flipping = ref(false);

const canvasEl = ref<HTMLCanvasElement | null>(null);
let pdfDoc: any = null;
let pdfjsLib: any = null;
let rendering = false;
// physical PDF page_number → OCR chunk_index (OCR skips blank/cover pages, so
// chunk_index drifts from the physical page pdf.js renders).
const pageToIdx = new Map<number, number>();

// API auth is Bearer-token (not cookie), so every call — including pdf.js's
// own fetch of the original file — must carry the Supabase access token.
const supabase = useSupabaseClient();
async function getToken(): Promise<string> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token ?? "";
}

async function loadPdf() {
  try {
    const token = await getToken();
    // Book title via the existing reader API.
    try {
      const m: any = await authedFetch(`/api/ebooks/${id}?page=1`);
      if (m) title.value = m.title;
    } catch { /* non-fatal */ }

    pdfjsLib = await import("pdfjs-dist");
    const workerUrl = (await import("pdfjs-dist/build/pdf.worker.min.mjs?url")).default;
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;
    const task = pdfjsLib.getDocument({
      url: `/api/ebooks/${id}/original`,
      httpHeaders: { Authorization: `Bearer ${token}` },
      withCredentials: true,
    });
    pdfDoc = await task.promise;
    numPages.value = pdfDoc.numPages;
    // page_number → chunk_index map for OCR-text alignment.
    try {
      const map: any[] = await authedFetch(`/api/ebooks/${id}/page-map`);
      for (const m of map) {
        if (m.page_number != null) pageToIdx.set(m.page_number, m.chunk_index);
      }
    } catch { /* fall back to index==page below */ }
    await buildOutline();
    await renderPage(currentPage.value);
  } catch (e: any) {
    error.value = "無法載入 PDF：" + (e?.message || e);
    loading.value = false;
  }
}

async function buildOutline() {
  try {
    const raw = await pdfDoc.getOutline();
    if (!raw) return;
    const flat: any[] = [];
    const walk = async (items: any[], depth: number) => {
      for (const it of items) {
        let page: number | null = null;
        try {
          let dest = it.dest;
          if (typeof dest === "string") dest = await pdfDoc.getDestination(dest);
          if (Array.isArray(dest) && dest[0]) {
            const idx = await pdfDoc.getPageIndex(dest[0]);
            page = idx + 1;
          }
        } catch { /* unresolved dest */ }
        flat.push({ title: it.title, _depth: depth, _page: page });
        if (it.items?.length) await walk(it.items, depth + 1);
      }
    };
    await walk(raw, 0);
    outline.value = flat;
  } catch { /* no outline */ }
}

async function renderPage(n: number) {
  if (!pdfDoc || rendering) return;
  rendering = true;
  loading.value = true;
  try {
    const page = await pdfDoc.getPage(n);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const viewport = page.getViewport({ scale: scale.value * dpr });
    const canvas = canvasEl.value!;
    const ctx = canvas.getContext("2d")!;
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    canvas.style.width = viewport.width / dpr + "px";
    canvas.style.height = viewport.height / dpr + "px";
    await page.render({ canvasContext: ctx, viewport }).promise;
  } finally {
    rendering = false;
    loading.value = false;
  }
  fetchOcr(n);
}

async function fetchOcr(physicalPage: number) {
  // Translate the physical PDF page to the OCR chunk that covers it. The
  // reader API addresses chunks by 1-based position (page = chunk_index + 1).
  let idx: number;
  if (pageToIdx.size > 0) {
    if (!pageToIdx.has(physicalPage)) { ocrText.value = ""; return; } // blank/cover, no OCR
    idx = pageToIdx.get(physicalPage)!;
  } else {
    idx = physicalPage - 1; // no map available — assume index==page
  }
  if (idx < 0) { ocrText.value = ""; return; }
  try {
    const d: any = await authedFetch(`/api/ebooks/${id}?page=${idx + 1}`);
    ocrText.value = d?.currentPage?.content || "";
  } catch {
    ocrText.value = "";
  }
}

function go(n: number) {
  n = Math.max(1, Math.min(n, numPages.value || 1));
  if (n === currentPage.value) return;
  flipping.value = true;
  setTimeout(() => (flipping.value = false), 260);
  currentPage.value = n;
  jump.value = n;
}

function onKey(e: KeyboardEvent) {
  const tag = (e.target as HTMLElement)?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA") return;
  if (e.key === "ArrowLeft") go(currentPage.value - 1);
  else if (e.key === "ArrowRight") go(currentPage.value + 1);
}

function gotoOutline(item: any) {
  if (item._page) go(item._page);
}

function setScale(s: number) {
  scale.value = Math.max(0.6, Math.min(3, Math.round(s * 10) / 10));
  renderPage(currentPage.value);
}

async function copyText() {
  if (!ocrText.value) return;
  await navigator.clipboard.writeText(ocrText.value);
  copied.value = true;
  setTimeout(() => (copied.value = false), 1500);
}

watch(currentPage, (n) => renderPage(n));

onMounted(() => {
  loadPdf();
  window.addEventListener("keydown", onKey);
});
onUnmounted(() => window.removeEventListener("keydown", onKey));
</script>

<style scoped>
.flip-anim {
  animation: pageflip 0.26s ease;
  transform-origin: left center;
}
@keyframes pageflip {
  0% { transform: perspective(1600px) rotateY(-8deg); opacity: 0.55; }
  100% { transform: perspective(1600px) rotateY(0deg); opacity: 1; }
}
</style>
