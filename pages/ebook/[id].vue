<template>
  <div class="min-h-screen bg-stone-50 text-stone-900 flex flex-col">
    <!-- Topbar -->
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink to="/ebook" class="text-stone-500 hover:text-stone-900 text-sm transition flex-shrink-0">← 書架</NuxtLink>
          <span class="text-stone-300">·</span>
          <span class="text-sm font-medium text-stone-900 truncate">{{ ebook?.title }}</span>
          <span v-if="ebook?.author" class="text-stone-400 text-sm hidden md:inline truncate">／{{ ebook.author }}</span>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">‹</button>
          <input v-model.number="jumpPage" @keyup.enter="goPage(jumpPage)" type="number" :min="1" :max="ebook?.total_pages ?? 1"
            class="w-14 bg-white border border-stone-200 rounded-lg px-2 py-1 text-center text-sm focus:outline-none focus:border-blue-500" />
          <span class="text-xs text-stone-400">/ {{ ebook?.total_pages }}</span>
          <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">›</button>
        </div>

        <div class="flex items-center gap-2 flex-1 justify-end">
          <input v-model="pageSearch" type="text" placeholder="頁內搜尋…"
            class="hidden sm:block bg-white border border-stone-200 rounded-lg px-3 py-1.5 text-sm w-40 focus:outline-none focus:border-blue-500" />
          <button @click="cycleReadingStatus"
            :title="readingStatus === 'reading' ? '點擊：標記已讀'
                  : readingStatus === 'read'    ? '點擊：從書櫃移除'
                  :                                '點擊：加入閱讀中'"
            :class="['hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border',
              readingStatus === 'reading' ? 'bg-blue-100 border-blue-300 text-blue-800'
              : readingStatus === 'read'  ? 'bg-emerald-100 border-emerald-300 text-emerald-800'
              :                              'bg-white border-stone-200 hover:border-blue-300 text-stone-600']">
            <span>{{ readingStatus === 'reading' ? '📖' : readingStatus === 'read' ? '✅' : '📚' }}</span>
            <span>{{ readingStatus === 'reading' ? '閱讀中' : readingStatus === 'read' ? '已讀' : '加入書櫃' }}</span>
          </button>
          <button v-if="readingStatus === 'reading'" @click="addTodayBookmark"
            title="標記今日讀到這裡"
            class="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border bg-white border-stone-200 hover:border-purple-400 text-stone-600">
            <span>📅</span><span>今日讀到這裡</span>
          </button>
          <button @click="annotationsPanelOpen = !annotationsPanelOpen"
            :class="['hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border',
              annotationsPanelOpen ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-white border-stone-200 hover:border-amber-300 text-stone-600']">
            <span>📝</span><span>標記 {{ bookAnnotations.length }}</span>
          </button>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 overflow-hidden">
      <!-- Left TOC sidebar -->
      <aside class="w-64 border-r border-stone-200 bg-white overflow-y-auto flex-shrink-0 hidden lg:block">
        <div class="p-3">
          <div class="text-xs uppercase text-stone-400 mb-2 px-2 tracking-wider">目錄</div>
          <div v-if="!toc.length && pageLoading" class="text-stone-400 text-sm px-2 py-2">載入中…</div>

          <!-- Front matter (no volume) -->
          <div v-if="frontMatter.length" class="space-y-0.5 mb-3">
            <div v-for="entry in frontMatter" :key="entry.chunk_index" class="group relative">
              <button @click="goPage(entry.chunk_index + 1)"
                :class="[tocBtnCls(entry), 'w-full flex items-center gap-1.5']">
                <span class="flex-1 text-left truncate">{{ entry.title }}</span>
                <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                  class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                  📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                </span>
              </button>
              <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                @click.stop="deleteBookmark(bookmarkByChunk.get(entry.chunk_index)!.id)"
                title="移除書籤"
                class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
            </div>
          </div>

          <!-- Volumes (collapsible) -->
          <div v-for="v in volumes" :key="v.name" class="mb-1">
            <button @click="toggleVolume(v.name)"
              class="w-full flex items-center gap-1 px-2 py-2 rounded text-sm font-medium text-stone-900 hover:bg-stone-50 transition">
              <span class="text-stone-400 text-xs w-3 inline-block">{{ expandedVolumes.has(v.name) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
              <span class="text-xs text-stone-400">{{ v.entries.length }}</span>
            </button>
            <div v-if="expandedVolumes.has(v.name)" class="space-y-0.5 mt-0.5">
              <div v-for="entry in v.entries" :key="entry.chunk_index" class="group relative">
                <button @click="goPage(entry.chunk_index + 1)"
                  :class="[tocBtnCls(entry), 'w-full flex items-center gap-1.5']">
                  <span class="flex-1 text-left truncate">{{ entry.title }}</span>
                  <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                    class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                    📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                  </span>
                </button>
                <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                  @click.stop="deleteBookmark(bookmarkByChunk.get(entry.chunk_index)!.id)"
                  title="移除書籤"
                  class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Reading area -->
      <div class="flex-1 overflow-y-auto bg-stone-50" ref="scrollEl">
        <article class="max-w-4xl mx-auto px-12 py-14 bg-white shadow-sm rounded-lg my-8 border border-stone-200">
          <div v-if="pageLoading" class="space-y-3 animate-pulse">
            <div v-for="i in 8" :key="i" :class="['h-4 bg-stone-200 rounded', i % 3 === 0 ? 'w-3/4' : 'w-full']"></div>
          </div>

          <template v-else-if="pageContent">
            <div class="text-xs text-stone-400 mb-10 flex items-center gap-2 uppercase tracking-wider">
              <span v-if="pageChapter">{{ pageChapter }}</span>
              <span v-else>第 {{ currentPage }} 段</span>
              <span>·</span>
              <span class="normal-case tracking-normal">{{ ebook?.title }}</span>
            </div>

            <div ref="contentEl"
              class="ebook-prose"
              v-html="markdownHtml"
              @mouseup="onTextSelectionEnd"
              @click="onContentClick"></div>

            <div class="flex justify-between mt-16 pt-6 border-t border-stone-200">
              <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
                class="px-5 py-2 bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 rounded-lg text-sm transition">← 上一段</button>
              <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
                class="px-5 py-2 bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 rounded-lg text-sm transition">下一段 →</button>
            </div>
          </template>

          <div v-else class="text-center py-20 text-stone-400">此段無內容</div>
        </article>
      </div>

      <!-- Right annotations panel -->
      <aside v-if="annotationsPanelOpen"
        class="w-80 border-l border-stone-200 bg-white overflow-y-auto flex-shrink-0 hidden lg:block">
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="text-sm font-semibold text-stone-900">📝 我的標記</div>
            <span class="text-xs text-stone-400">{{ bookAnnotations.length }} 條</span>
          </div>
          <p v-if="!bookAnnotations.length" class="text-stone-400 text-sm py-8 text-center">
            選一段文字標螢光，就會出現在這裡
          </p>
          <div class="space-y-2.5">
            <div v-for="a in sortedBookAnnotations" :key="a.id"
              class="group bg-stone-50 hover:bg-amber-50 border border-stone-200 hover:border-amber-300 rounded-lg p-3 transition">
              <button @click="jumpToAnnotation(a)"
                class="w-full text-left">
                <div class="flex items-start gap-2 mb-1.5">
                  <span class="w-3 h-3 rounded-full mt-1 flex-shrink-0 border border-stone-300"
                    :style="{ background: COLOR_BG[a.color] || COLOR_BG.yellow }"></span>
                  <p class="text-sm text-stone-800 leading-snug line-clamp-3 flex-1">{{ a.selected_text }}</p>
                </div>
                <p v-if="a.note" class="text-xs text-stone-600 italic mb-1.5 pl-5">📌 {{ a.note }}</p>
                <p class="text-xs text-stone-400 pl-5">{{ chunkLabel(a.chunk_index) }}<span v-if="a.excerpt_id" class="text-blue-500">　·　已存書摘</span></p>
              </button>
              <div class="flex gap-1 mt-2 pt-2 border-t border-stone-100 opacity-0 group-hover:opacity-100 transition">
                <button @click="openNoteEditor(a)" class="text-xs px-2 py-1 hover:bg-stone-200 rounded text-stone-600">註記</button>
                <button @click="deleteAnnotation(a.id)" class="text-xs px-2 py-1 hover:bg-red-100 text-red-600 rounded">刪除</button>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Selection popup (when text selected in reader) -->
    <div v-if="selectionPopup.show"
      data-selection-popup
      class="fixed bg-white shadow-xl border border-stone-200 rounded-xl px-2 py-2 flex items-center gap-1 z-50"
      :style="{ top: selectionPopup.y + 'px', left: selectionPopup.x + 'px' }">
      <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
        @click="saveAnnotationFromSelection(c.name)"
        :title="c.label"
        class="w-7 h-7 rounded-full border border-stone-300 hover:scale-110 transition"
        :style="{ background: c.bg }"></button>
      <div class="w-px h-6 bg-stone-200 mx-1"></div>
      <button @click="openNewNoteFromSelection"
        class="px-2.5 py-1.5 text-xs bg-stone-100 hover:bg-stone-200 rounded-lg transition whitespace-nowrap">+ 註記</button>
      <button @click="openExcerptModalFromSelection"
        class="px-2.5 py-1.5 text-xs bg-blue-600 text-white hover:bg-blue-500 rounded-lg transition whitespace-nowrap">+ 書摘</button>
    </div>

    <!-- Mark click popup (when clicking an existing highlight) -->
    <div v-if="markPopup.show"
      data-mark-popup
      class="fixed bg-white shadow-xl border border-stone-200 rounded-xl px-2 py-2 flex items-center gap-1 z-50"
      :style="{ top: markPopup.y + 'px', left: markPopup.x + 'px' }">
      <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
        @click="changeAnnotationColor(c.name)"
        :title="`改為${c.label}`"
        class="w-6 h-6 rounded-full border border-stone-300 hover:scale-110 transition"
        :style="{ background: c.bg }"></button>
      <div class="w-px h-5 bg-stone-200 mx-1"></div>
      <button @click="openNoteEditorForMark" class="px-2.5 py-1 text-xs hover:bg-stone-100 rounded">註記</button>
      <button @click="deleteCurrentMark" class="px-2.5 py-1 text-xs text-red-600 hover:bg-red-50 rounded">刪除</button>
    </div>

    <!-- Note editor modal (auto-save) -->
    <div v-if="noteEditor.show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md space-y-4 border border-stone-200 shadow-xl">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-lg text-stone-900">{{ noteEditor.editingExisting ? '編輯註記' : '新增註記' }}</h3>
          <span class="text-xs flex items-center gap-1.5"
            :class="{
              'text-stone-400': noteEditor.status === '' || noteEditor.status === 'saved',
              'text-blue-600': noteEditor.status === 'saving',
              'text-red-600': noteEditor.status === 'error',
            }">
            <span v-if="noteEditor.status === 'saving'">● 儲存中…</span>
            <span v-else-if="noteEditor.status === 'saved'">✓ 已儲存</span>
            <span v-else-if="noteEditor.status === 'error'">⚠ {{ noteEditor.errorMsg || '儲存失敗' }}</span>
            <span v-else class="text-stone-300">未變更</span>
          </span>
        </div>
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-stone-700 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">{{ noteEditor.text }}</div>
        <textarea v-model="noteEditor.note" placeholder="寫下你的想法…（自動儲存）" rows="4"
          class="w-full border border-stone-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 resize-none"></textarea>
        <div class="flex justify-end">
          <button @click="closeNoteEditor"
            class="px-5 py-2 bg-stone-900 hover:bg-stone-700 text-white rounded-lg text-sm transition">完成</button>
        </div>
      </div>
    </div>

    <!-- Toast (errors / status) -->
    <Transition name="fade">
      <div v-if="toast.show" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] pointer-events-none">
        <div :class="['px-4 py-3 rounded-lg shadow-xl text-sm font-medium pointer-events-auto',
          toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-stone-900 text-white']">
          {{ toast.message }}
        </div>
      </div>
    </Transition>

    <!-- Save excerpt modal -->
    <div v-if="excerptModal.show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg space-y-4 border border-stone-200 shadow-xl">
        <h3 class="font-semibold text-lg text-stone-900">存到書摘圖書館</h3>
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-stone-700 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">{{ excerptModal.content }}</div>
        <input v-model="excerptModal.title" placeholder="為這段書摘命名（必填）"
          class="w-full border border-stone-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
        <div class="flex items-center gap-2">
          <span class="text-xs text-stone-500">螢光顏色：</span>
          <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
            @click="excerptModal.color = c.name"
            :class="['w-6 h-6 rounded-full border-2 transition',
              excerptModal.color === c.name ? 'border-stone-700 scale-110' : 'border-stone-300 hover:scale-110']"
            :style="{ background: c.bg }" :title="c.label"></button>
        </div>
        <p class="text-xs text-stone-400">將連結至《{{ ebook?.title }}》· {{ pageChapter || `第 ${currentPage} 段` }}</p>
        <div class="flex gap-3">
          <button @click="confirmSaveExcerpt"
            :disabled="!excerptModal.title.trim() || excerptModal.saving"
            class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 rounded-xl text-sm font-medium transition">
            {{ excerptModal.saving ? '儲存中…' : '儲存到書摘圖書館' }}
          </button>
          <button @click="excerptModal.show = false"
            class="px-4 py-2.5 bg-stone-100 hover:bg-stone-200 rounded-xl text-sm transition">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

interface TocEntry { chunk_index: number; title: string; level: number; volume?: string | null }
interface VolumeGroup { name: string; entries: TocEntry[] }
interface Annotation {
  id: string;
  ebook_id: string;
  chunk_index: number;
  selected_text: string;
  context_before?: string | null;
  context_after?: string | null;
  note?: string | null;
  color: string;
  excerpt_id?: string | null;
  created_at?: string;
}
interface Bookmark { id: string; chunk_index: number; created_at: string }
type ReadingStatus = "reading" | "read" | null;

const HIGHLIGHT_COLORS = [
  { name: "yellow", label: "黃", bg: "#FEF08A" },
  { name: "green",  label: "綠", bg: "#BBF7D0" },
  { name: "blue",   label: "藍", bg: "#BFDBFE" },
  { name: "pink",   label: "粉", bg: "#FBCFE8" },
];
const COLOR_BG: Record<string, string> = Object.fromEntries(HIGHLIGHT_COLORS.map(c => [c.name, c.bg]));

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const ebookId = route.params.id as string;

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

// ── State ──
const ebook = ref<any>(null);
const toc = ref<TocEntry[]>([]);
const currentPage = ref(parseInt(route.query.page as string ?? "1") || 1);
const jumpPage = ref(currentPage.value);
const pageContent = ref("");
const pageChapter = ref<string | null>(null);
const pageLoading = ref(false);
const pageSearch = ref("");
const annotations = ref<Annotation[]>([]);
const bookAnnotations = ref<Annotation[]>([]);
const expandedVolumes = ref<Set<string>>(new Set());
const annotationsPanelOpen = ref(false);
const lastUsedColor = ref<string>("yellow");
const contentEl = ref<HTMLDivElement | null>(null);
const scrollEl = ref<HTMLElement | null>(null);

// Bookshelf state — user's reading status for this book + their date bookmarks.
const readingStatus = ref<ReadingStatus>(null);
const bookmarks = ref<Bookmark[]>([]);
// Quick chunk_index → date map for the TOC sidebar badges.
const bookmarkByChunk = computed(() => {
  const m = new Map<number, Bookmark>();
  // bookmarks are pre-sorted desc by created_at server-side; keep latest per chunk.
  for (const b of bookmarks.value) {
    if (!m.has(b.chunk_index)) m.set(b.chunk_index, b);
  }
  return m;
});
function fmtBookmarkDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

// ── Toast for errors / status ──
const toast = ref({ show: false, message: "", type: "info" as "info" | "error" });
let toastTimer: any = null;
function showToast(message: string, type: "info" | "error" = "info") {
  toast.value = { show: true, message, type };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value.show = false; }, type === "error" ? 5000 : 2500);
}

// ── TOC grouping ──
const frontMatter = computed(() => toc.value.filter(e => !e.volume));
const volumes = computed<VolumeGroup[]>(() => {
  const map = new Map<string, TocEntry[]>();
  for (const e of toc.value) {
    if (!e.volume) continue;
    if (!map.has(e.volume)) map.set(e.volume, []);
    map.get(e.volume)!.push(e);
  }
  return [...map].map(([name, entries]) => ({ name, entries }));
});

function shortVolumeName(name: string): string {
  // Strip the book title prefix from volume name for compact display
  const t = ebook.value?.title;
  if (t && name.startsWith(t + "：")) return name.slice(t.length + 1);
  if (t && name.startsWith(t + ":")) return name.slice(t.length + 1);
  return name;
}

function toggleVolume(name: string) {
  const next = new Set(expandedVolumes.value);
  if (next.has(name)) next.delete(name);
  else next.add(name);
  expandedVolumes.value = next;
}

function tocBtnCls(entry: TocEntry) {
  const isActive = entry.chunk_index === currentPage.value - 1;
  return [
    "w-full text-left py-1.5 rounded text-sm transition truncate block",
    isActive ? "bg-blue-50 text-blue-700 font-medium" : "text-stone-600 hover:bg-stone-50",
    entry.level === 2 ? "pl-3" : entry.level === 3 ? "pl-7" : "pl-11 text-xs",
  ];
}

// ── Markdown render ──
function escapeHtml(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function inlineFmt(s: string) {
  return s.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
          .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>")
          // <u>X</u> survives escapeHtml as &lt;u&gt;X&lt;/u&gt; — restore the tag here
          .replace(/&lt;u&gt;([^<]+?)&lt;\/u&gt;/g, "<u>$1</u>");
}
function renderMarkdown(md: string): string {
  const blocks = md.split(/\n{2,}/);
  const out: string[] = [];
  for (let block of blocks) {
    block = block.trim();
    if (!block) continue;
    if (/^-{3,}$/.test(block)) { out.push("<hr>"); continue; }
    const escaped = escapeHtml(block);
    let h: RegExpMatchArray | null;
    if ((h = escaped.match(/^####\s+(.+)$/))) out.push(`<h4>${inlineFmt(h[1])}</h4>`);
    else if ((h = escaped.match(/^###\s+(.+)$/))) out.push(`<h3>${inlineFmt(h[1])}</h3>`);
    else if ((h = escaped.match(/^##\s+(.+)$/))) out.push(`<h2>${inlineFmt(h[1])}</h2>`);
    else if ((h = escaped.match(/^#\s+(.+)$/))) out.push(`<h1>${inlineFmt(h[1])}</h1>`);
    else if (/^&gt;\s/.test(escaped)) {
      const lines = escaped.split(/\n/).map(ln => ln.replace(/^&gt;\s?/, "")).join("<br>");
      out.push(`<blockquote>${inlineFmt(lines)}</blockquote>`);
    } else {
      out.push(`<p>${inlineFmt(escaped).replace(/\n/g, "<br>")}</p>`);
    }
  }
  return out.join("\n");
}

const markdownHtml = computed(() => renderMarkdown(pageContent.value));

// ── DOM-based highlight applier (handles cross-paragraph + multi-occurrence) ──
function isInsideMark(node: Node, container: HTMLElement): boolean {
  let p: Node | null = node.parentNode;
  while (p && p !== container) {
    if ((p as Element).tagName === "MARK") return true;
    p = p.parentNode;
  }
  return false;
}

function gatherTextNodes(container: HTMLElement): { node: Text; start: number; end: number }[] {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => isInsideMark(n, container) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
  });
  const nodes: { node: Text; start: number; end: number }[] = [];
  let total = 0;
  let n = walker.nextNode() as Text | null;
  while (n) {
    const t = n.textContent || "";
    nodes.push({ node: n, start: total, end: total + t.length });
    total += t.length;
    n = walker.nextNode() as Text | null;
  }
  return nodes;
}

function wrapTextNodeSlice(node: Text, startOff: number, endOff: number, attrs: Record<string, string>): HTMLElement {
  const text = node.textContent || "";
  const before = text.slice(0, startOff);
  const middle = text.slice(startOff, endOff);
  const after = text.slice(endOff);

  const mark = document.createElement("mark");
  mark.textContent = middle;
  for (const [k, v] of Object.entries(attrs)) mark.setAttribute(k, v);

  const parent = node.parentNode;
  if (!parent) return mark;
  if (before) parent.insertBefore(document.createTextNode(before), node);
  parent.insertBefore(mark, node);
  if (after) parent.insertBefore(document.createTextNode(after), node);
  parent.removeChild(node);
  return mark;
}

function highlightOne(container: HTMLElement, text: string, attrs: Record<string, string>): number {
  if (!text || text.length < 2) return 0;
  let wrapped = 0;
  // Cap iterations defensively in case mark filter fails to advance.
  for (let iter = 0; iter < 200; iter++) {
    const nodes = gatherTextNodes(container);
    let total = "";
    for (const n of nodes) total += n.node.textContent || "";
    const idx = total.indexOf(text);
    if (idx === -1) break;
    const matchEnd = idx + text.length;
    let didWrap = false;
    // Wrap each text node touched by this match (handles cross-paragraph).
    for (const np of nodes) {
      if (matchEnd <= np.start || idx >= np.end) continue;
      const localStart = Math.max(0, idx - np.start);
      const localEnd = Math.min(np.end - np.start, matchEnd - np.start);
      if (localEnd > localStart) {
        wrapTextNodeSlice(np.node, localStart, localEnd, attrs);
        didWrap = true;
      }
    }
    if (!didWrap) break;
    wrapped++;
  }
  return wrapped;
}

function applyHighlights() {
  if (!contentEl.value) return;
  // Apply each annotation. acceptNode rejects already-marked text, so this is
  // idempotent — calling twice doesn't double-wrap.
  for (const a of annotations.value) {
    const bg = COLOR_BG[a.color] || COLOR_BG.yellow;
    const style = `background:${bg};padding:0 2px;border-radius:2px;cursor:pointer;`;
    const noteAttr = a.note ? `; box-shadow: 0 0 0 1px ${bg}; outline: 1px dashed #f59e0b; outline-offset: 1px;` : "";
    highlightOne(contentEl.value, a.selected_text, {
      "data-anno-id": a.id,
      "style": style + noteAttr,
      "title": a.note ? `📌 ${a.note}` : "",
    });
  }
  // Apply page search (separate styling, not persistent)
  if (pageSearch.value.trim()) {
    highlightOne(contentEl.value, pageSearch.value.trim(), {
      "data-search": "1",
      "style": "background:#FCD34D;padding:0 2px;border-radius:2px;",
    });
  }
}

function unwrapMarksByAnnoId(annoId: string) {
  if (!contentEl.value) return;
  const marks = contentEl.value.querySelectorAll(`mark[data-anno-id="${annoId}"]`);
  for (const m of marks) {
    const parent = m.parentNode;
    if (!parent) continue;
    while (m.firstChild) parent.insertBefore(m.firstChild, m);
    parent.removeChild(m);
    parent.normalize();
  }
}

// Re-apply highlights whenever the rendered HTML or annotations change.
watch([markdownHtml, annotations], async () => {
  await nextTick();
  applyHighlights();
});

// ── Loaders ──
async function loadPage(page: number) {
  pageLoading.value = true;
  const token = await getToken(); if (!token) return;
  const isFirstLoad = !ebook.value;
  const url = `/api/ebooks/${ebookId}?page=${page}${isFirstLoad ? "&includeToc=1" : ""}`;
  const data = await $fetch<any>(url, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);

  if (data) {
    if (!ebook.value) ebook.value = data;
    if (data.toc) toc.value = data.toc;
  }
  pageContent.value = data?.currentPage?.content ?? "";
  pageChapter.value = data?.currentPage?.chapter_path ?? null;
  pageLoading.value = false;
  jumpPage.value = page;

  // Auto-expand the volume containing the current chunk
  const here = toc.value.find(e => e.chunk_index === page - 1);
  if (here?.volume) expandedVolumes.value = new Set([...expandedVolumes.value, here.volume]);

  await loadAnnotations(page - 1);

  await nextTick();
  scrollEl.value?.scrollTo({ top: 0, behavior: "auto" });
}

async function loadAnnotations(chunkIndex: number) {
  const token = await getToken(); if (!token) return;
  annotations.value = await $fetch<Annotation[]>(
    `/api/annotations?ebookId=${ebookId}&chunkIndex=${chunkIndex}`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

async function loadBookAnnotations() {
  const token = await getToken(); if (!token) return;
  bookAnnotations.value = await $fetch<Annotation[]>(
    `/api/annotations?ebookId=${ebookId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

// ── Bookshelf + bookmarks ──
async function loadReadingStatus() {
  const token = await getToken(); if (!token) return;
  const data = await $fetch<{ status: ReadingStatus }>(
    `/api/ebooks/${ebookId}/reading-status`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => ({ status: null }));
  readingStatus.value = data?.status ?? null;
}

async function loadBookmarks() {
  const token = await getToken(); if (!token) return;
  bookmarks.value = await $fetch<Bookmark[]>(
    `/api/ebooks/${ebookId}/bookmarks`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

// Cycle: null → reading → read → null. Each transition is a single PUT.
async function cycleReadingStatus() {
  const next: ReadingStatus =
    readingStatus.value === null ? "reading" :
    readingStatus.value === "reading" ? "read" : null;
  const token = await getToken(); if (!token) return;
  try {
    await $fetch(`/api/ebooks/${ebookId}/reading-status`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: { status: next },
    });
    readingStatus.value = next;
    showToast(
      next === "reading" ? "已加入閱讀中"
      : next === "read"  ? "已標記為已讀"
      :                    "已從書櫃移除"
    );
  } catch (e: any) {
    showToast(`狀態更新失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

async function addTodayBookmark() {
  const token = await getToken(); if (!token) return;
  try {
    const created = await $fetch<Bookmark>(`/api/ebooks/${ebookId}/bookmarks`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: { chunk_index: currentPage.value - 1 },
    });
    // newest-first ordering matches server response
    bookmarks.value = [created, ...bookmarks.value];
    showToast(`已標記今日讀到第 ${currentPage.value} 段`);
  } catch (e: any) {
    showToast(`書籤建立失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

async function deleteBookmark(id: string) {
  const token = await getToken(); if (!token) return;
  try {
    await $fetch(`/api/bookmarks/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    bookmarks.value = bookmarks.value.filter(b => b.id !== id);
    showToast("已移除書籤");
  } catch (e: any) {
    showToast(`刪除失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

const sortedBookAnnotations = computed(() =>
  [...bookAnnotations.value].sort((a, b) => a.chunk_index - b.chunk_index ||
    (a.created_at ?? "").localeCompare(b.created_at ?? ""))
);

function chunkLabel(idx: number): string {
  const e = toc.value.find(t => t.chunk_index === idx);
  if (!e) return `第 ${idx + 1} 段`;
  return e.volume ? `${shortVolumeName(e.volume)} · ${e.title}` : e.title;
}

function goPage(p: number) {
  if (!ebook.value) return;
  const clamped = Math.max(1, Math.min(p, ebook.value.total_pages));
  if (clamped === currentPage.value) return;
  currentPage.value = clamped;
  router.replace({ query: { page: String(clamped) } });
  loadPage(clamped);
}

async function jumpToAnnotation(a: Annotation) {
  if (a.chunk_index !== currentPage.value - 1) {
    goPage(a.chunk_index + 1);
    // Wait for content + highlights to render, then scroll to mark.
    await new Promise(r => setTimeout(r, 400));
  }
  await nextTick();
  const mark = contentEl.value?.querySelector(`mark[data-anno-id="${a.id}"]`);
  if (mark) {
    (mark as HTMLElement).scrollIntoView({ behavior: "smooth", block: "center" });
    // brief flash
    (mark as HTMLElement).animate(
      [{ filter: "brightness(1.5)" }, { filter: "brightness(1)" }],
      { duration: 800 }
    );
  }
}

// ── Selection toolbar ──
const selectionPopup = ref({ show: false, x: 0, y: 0 });
const lastSelection = ref<{ text: string; before: string; after: string } | null>(null);

function captureSelection() {
  const sel = window.getSelection?.();
  if (!sel || sel.rangeCount === 0) return null;
  const text = sel.toString().trim();
  if (text.length < 2) return null;
  const range = sel.getRangeAt(0);
  if (!contentEl.value || !contentEl.value.contains(range.commonAncestorContainer)) return null;
  const containerText = contentEl.value.innerText || "";
  const idx = containerText.indexOf(text);
  const before = idx > 0 ? containerText.slice(Math.max(0, idx - 30), idx) : "";
  const after = idx >= 0 ? containerText.slice(idx + text.length, idx + text.length + 30) : "";
  return { text, before, after, range };
}

function onTextSelectionEnd() {
  setTimeout(() => {
    const captured = captureSelection();
    if (!captured) {
      selectionPopup.value.show = false;
      return;
    }
    lastSelection.value = { text: captured.text, before: captured.before, after: captured.after };
    const rect = captured.range.getBoundingClientRect();
    const popupWidth = 340;
    selectionPopup.value = {
      show: true,
      x: Math.max(8, Math.min(window.innerWidth - popupWidth - 8, rect.left + rect.width / 2 - popupWidth / 2)),
      y: Math.max(8, rect.top - 56),
    };
    markPopup.value.show = false;
  }, 1);
}

// ── Click on existing mark ──
const markPopup = ref({ show: false, x: 0, y: 0, annoId: "" });

function onContentClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  const mark = target.closest("mark[data-anno-id]") as HTMLElement | null;
  if (!mark) {
    markPopup.value.show = false;
    return;
  }
  e.stopPropagation();
  const annoId = mark.dataset.annoId!;
  const rect = mark.getBoundingClientRect();
  markPopup.value = {
    show: true,
    x: Math.max(8, Math.min(window.innerWidth - 280, rect.left)),
    y: Math.max(8, rect.bottom + 6),
    annoId,
  };
  selectionPopup.value.show = false;
}

function hidePopupsOnOutsideClick(e: MouseEvent) {
  const t = e.target as HTMLElement;
  if (t.closest("[data-selection-popup]") || t.closest("[data-mark-popup]")) return;
  if (t.closest("mark[data-anno-id]")) return;
  if (t.closest(".ebook-prose")) return;
  selectionPopup.value.show = false;
  markPopup.value.show = false;
}

// ── Save annotation from selection ──
async function postAnnotation(body: any): Promise<Annotation | null> {
  const token = await getToken(); if (!token) return null;
  try {
    return await $fetch<Annotation>("/api/annotations", {
      method: "POST", body,
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`儲存失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return null;
  }
}

async function saveAnnotationFromSelection(color: string) {
  const sel = lastSelection.value;
  if (!sel) return;
  selectionPopup.value.show = false;
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color,
  });
  // Only push to UI state if save succeeded — avoids the "looks saved but isn't" trap.
  if (newAnno) {
    lastUsedColor.value = color;
    annotations.value = [...annotations.value, newAnno];
    bookAnnotations.value = [...bookAnnotations.value, newAnno];
    window.getSelection?.()?.removeAllRanges();
  }
}

// ── Note editor (auto-save with 1s debounce) ──
const noteEditor = ref({
  show: false,
  annoId: "",            // empty until first save creates the annotation
  editingExisting: false,
  text: "",
  note: "",
  color: "yellow",
  status: "" as "" | "saving" | "saved" | "error",
  errorMsg: "",
  // Snapshot the selection at open time so it survives loss of window selection.
  pendingSel: null as { text: string; before: string; after: string } | null,
});
let noteSaveTimer: any = null;

async function openNewNoteFromSelection() {
  const sel = lastSelection.value;
  if (!sel) return;
  selectionPopup.value.show = false;
  // Create the annotation up front (with empty note + last color) so the
  // highlight appears immediately. Note edits then PATCH this row.
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color: lastUsedColor.value,
    note: null,
  });
  if (!newAnno) return;  // toast already shown by postAnnotation
  annotations.value = [...annotations.value, newAnno];
  bookAnnotations.value = [...bookAnnotations.value, newAnno];
  noteEditor.value = {
    show: true, annoId: newAnno.id, editingExisting: false,
    text: newAnno.selected_text, note: "",
    color: newAnno.color, status: "saved", errorMsg: "",
    pendingSel: null,
  };
  window.getSelection?.()?.removeAllRanges();
}

function openNoteEditor(a: Annotation) {
  noteEditor.value = {
    show: true, annoId: a.id, editingExisting: true,
    text: a.selected_text, note: a.note ?? "",
    color: a.color, status: a.note ? "saved" : "", errorMsg: "",
    pendingSel: null,
  };
}

function openNoteEditorForMark() {
  const a = bookAnnotations.value.find(x => x.id === markPopup.value.annoId);
  if (!a) return;
  openNoteEditor(a);
  markPopup.value.show = false;
}

function closeNoteEditor() {
  // If a save is in flight, let it finish. Otherwise just close.
  if (noteSaveTimer) {
    clearTimeout(noteSaveTimer);
    noteSaveTimer = null;
    // Flush a final save synchronously so closing doesn't lose the last keystroke.
    autoSaveNote();
  }
  noteEditor.value.show = false;
}

async function autoSaveNote() {
  if (!noteEditor.value.annoId) return;  // nothing to PATCH
  const token = await getToken();
  if (!token) {
    noteEditor.value.status = "error";
    noteEditor.value.errorMsg = "未登入";
    return;
  }
  noteEditor.value.status = "saving";
  try {
    const updated = await $fetch<Annotation>(`/api/annotations/${noteEditor.value.annoId}`, {
      method: "PATCH",
      body: { note: noteEditor.value.note || null },
      headers: { Authorization: `Bearer ${token}` },
    });
    annotations.value = annotations.value.map(a => a.id === updated.id ? { ...a, note: updated.note } : a);
    bookAnnotations.value = bookAnnotations.value.map(a => a.id === updated.id ? { ...a, note: updated.note } : a);
    unwrapMarksByAnnoId(updated.id);
    await nextTick();
    applyHighlights();
    noteEditor.value.status = "saved";
    noteEditor.value.errorMsg = "";
  } catch (e: any) {
    noteEditor.value.status = "error";
    noteEditor.value.errorMsg = e?.data?.message || e?.message || "網路錯誤";
    showToast(`註記儲存失敗：${noteEditor.value.errorMsg}`, "error");
  }
}

// Watch the note text and auto-save with 1s debounce.
watch(() => noteEditor.value.note, (newV, oldV) => {
  if (!noteEditor.value.show) return;
  if (newV === oldV) return;
  noteEditor.value.status = "";
  if (noteSaveTimer) clearTimeout(noteSaveTimer);
  noteSaveTimer = setTimeout(() => {
    noteSaveTimer = null;
    autoSaveNote();
  }, 1000);
});

// ── Delete / change color ──
async function deleteAnnotation(id: string) {
  const token = await getToken(); if (!token) return;
  try {
    await $fetch<{ ok: boolean }>(`/api/annotations/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`刪除失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return;
  }
  annotations.value = annotations.value.filter(a => a.id !== id);
  bookAnnotations.value = bookAnnotations.value.filter(a => a.id !== id);
  unwrapMarksByAnnoId(id);
}

function deleteCurrentMark() {
  const id = markPopup.value.annoId;
  markPopup.value.show = false;
  if (id) deleteAnnotation(id);
}

async function changeAnnotationColor(color: string) {
  const id = markPopup.value.annoId;
  markPopup.value.show = false;
  if (!id) return;
  const token = await getToken(); if (!token) return;
  try {
    await $fetch<Annotation>(`/api/annotations/${id}`, {
      method: "PATCH",
      body: { color },
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`換色失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return;
  }
  lastUsedColor.value = color;
  annotations.value = annotations.value.map(a => a.id === id ? { ...a, color } : a);
  bookAnnotations.value = bookAnnotations.value.map(a => a.id === id ? { ...a, color } : a);
  unwrapMarksByAnnoId(id);
  await nextTick();
  applyHighlights();
}

// ── Save excerpt ──
const excerptModal = ref({ show: false, title: "", content: "", color: "yellow", saving: false });

function openExcerptModalFromSelection() {
  const sel = lastSelection.value;
  if (!sel) return;
  excerptModal.value = {
    show: true, title: "", content: sel.text,
    color: lastUsedColor.value, saving: false,
  };
  selectionPopup.value.show = false;
}

async function confirmSaveExcerpt() {
  const sel = lastSelection.value;
  if (!sel || !excerptModal.value.title.trim()) return;
  excerptModal.value.saving = true;
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color: excerptModal.value.color,
    save_as_excerpt: true,
    excerpt_title: excerptModal.value.title.trim(),
    // chapter goes to excerpts.chapter so the book page groups by it;
    // page_label is human-readable section reference for the citation line.
    chapter: pageChapter.value ?? null,
    page_label: `第 ${currentPage.value} 段`,
  });
  excerptModal.value.saving = false;
  if (newAnno) {
    lastUsedColor.value = newAnno.color;
    annotations.value = [...annotations.value, newAnno];
    bookAnnotations.value = [...bookAnnotations.value, newAnno];
    excerptModal.value.show = false;
    window.getSelection?.()?.removeAllRanges();
    showToast("已存到書摘圖書館");
  }
  // On error, postAnnotation showed the toast and modal stays open so user can retry.
}

// ── Lifecycle ──
onMounted(async () => {
  document.addEventListener("mousedown", hidePopupsOnOutsideClick);

  // Fetch shelf state + bookmarks first so we can decide whether to auto-jump.
  await Promise.all([loadReadingStatus(), loadBookmarks()]);

  // Auto-jump rule: only when (a) status === 'reading', (b) at least one
  // bookmark exists, and (c) the user did NOT explicitly request a page via
  // ?page= in the URL. 'read' books and ad-hoc visits behave normally.
  const hasExplicitPage = !!route.query.page;
  if (!hasExplicitPage && readingStatus.value === "reading" && bookmarks.value.length > 0) {
    const target = bookmarks.value[0].chunk_index + 1;
    currentPage.value = target;
    jumpPage.value = target;
    router.replace({ query: { page: String(target) } });
    showToast(`接續 ${fmtBookmarkDate(bookmarks.value[0].created_at)} 閱讀進度，第 ${target} 段`);
  }

  loadPage(currentPage.value);
  loadBookAnnotations();
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", hidePopupsOnOutsideClick);
});
useHead({ title: computed(() => ebook.value ? `${ebook.value.title} — 閱讀` : "閱讀") });
</script>

<style scoped>
.ebook-prose {
  color: #1c1917;
  font-size: 17px;
  line-height: 2;
  font-family: "Noto Serif TC", "Source Han Serif TC", "PingFang TC", "Microsoft JhengHei", Georgia, serif;
}
.ebook-prose :deep(h1) {
  font-size: 2rem;
  font-weight: 700;
  margin: 2.5rem 0 1.5rem;
  color: #0c0a09;
  letter-spacing: 0.02em;
  text-align: center;
}
.ebook-prose :deep(h2) {
  font-size: 1.625rem;
  font-weight: 700;
  margin: 2.5rem 0 1.25rem;
  color: #0c0a09;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e7e5e4;
  text-align: center;
  letter-spacing: 0.01em;
}
.ebook-prose :deep(h3) {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 2.25rem 0 1rem;
  color: #1c1917;
}
.ebook-prose :deep(h4) {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 1.5rem 0 0.75rem;
  color: #292524;
}
.ebook-prose :deep(p) {
  margin: 1rem 0;
  text-indent: 2em;
  text-align: justify;
}
.ebook-prose :deep(strong) { font-weight: 700; color: #0c0a09; }
.ebook-prose :deep(em) { font-style: italic; }
.ebook-prose :deep(blockquote) {
  border-left: 3px solid #93c5fd;
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin: 1.5rem 0;
  color: #57534e;
  font-style: italic;
  background: #fffbeb;
}
.ebook-prose :deep(hr) {
  margin: 2rem 0;
  border: 0;
  border-top: 1px solid #e7e5e4;
}
.ebook-prose :deep(mark) {
  cursor: pointer;
  transition: filter 0.15s;
}
.ebook-prose :deep(mark:hover) { filter: brightness(0.95); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }
</style>
