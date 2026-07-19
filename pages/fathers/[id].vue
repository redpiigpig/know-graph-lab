<template>
  <div class="fathers-reader min-h-dvh flex flex-col">
    <!-- Topbar — patristic parchment identity, independent of the library reader -->
    <nav class="fathers-topbar sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink to="/fathers" class="fathers-back flex-shrink-0">← 教父著作</NuxtLink>
          <span class="fathers-sep">·</span>
          <button @click="tocDrawerOpen = !tocDrawerOpen"
            :class="['fathers-tocbtn flex-shrink-0', tocDrawerOpen ? 'is-on' : '']" title="目錄">
            <span>❦</span><span class="hidden sm:inline">目錄</span>
          </button>
          <span v-if="seriesVol" class="fathers-chip hidden sm:inline-flex">{{ seriesVol.series }}·卷{{ seriesVol.vol }}</span>
          <span class="text-sm font-semibold truncate fathers-title-text">{{ ebook?.title }}</span>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1" class="fathers-navbtn">‹</button>
          <input v-model.number="jumpPage" @keyup.enter="goPage(jumpPage)" type="number" :min="1" :max="ebook?.total_pages ?? 1"
            class="fathers-pageinput" />
          <span class="text-xs fathers-muted">/ {{ ebook?.total_pages }}</span>
          <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)" class="fathers-navbtn">›</button>
        </div>

        <div class="flex items-center gap-2 flex-1 justify-end">
          <EbookDisplaySettings v-model="displaySettings" />
          <button @click="toggleReadAloud" :disabled="!tts.supported.value"
            :title="!tts.supported.value ? '此瀏覽器不支援語音合成' : tts.playing.value ? '停止朗讀' : '朗讀本頁'"
            :class="['fathers-tool hidden md:inline-flex', tts.playing.value ? 'is-active' : '']">
            <span>{{ tts.playing.value ? '⏹' : '🔊' }}</span><span>{{ tts.playing.value ? '停止' : '朗讀' }}</span>
          </button>
          <div v-if="pageSourceOrder.length" class="fathers-modeswitch">
            <button @click="setViewMode('zh')" :class="modeBtnClass('zh')">中</button>
            <button @click="setViewMode('parallel')" :class="modeBtnClass('parallel')">對照</button>
            <button v-for="lang in pageSourceOrder" :key="lang"
              @click="setViewMode('src:' + lang)" :class="modeBtnClass('src:' + lang)">{{ langLabel(lang) }}</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 overflow-hidden relative">
      <div v-if="tocDrawerOpen" @click="tocDrawerOpen = false" class="lg:hidden fixed inset-0 bg-stone-900/40 z-30"></div>

      <!-- TOC sidebar (parchment, parent → volume → entry tree) -->
      <aside :class="['fathers-toc overflow-y-auto flex-shrink-0 transition-transform duration-200',
          tocDrawerOpen
            ? 'fixed lg:relative inset-y-0 left-0 top-14 lg:top-0 w-72 lg:w-72 z-40 translate-x-0 shadow-xl lg:shadow-none'
            : 'fixed lg:relative -translate-x-full w-0 lg:w-0 lg:opacity-0 lg:overflow-hidden']">
        <div class="p-3">
          <div class="fathers-toc-label">目　錄</div>

          <!-- Front matter (cover / preface, minus index entries) -->
          <div v-if="frontMatterMain.length" class="mb-3 space-y-0.5">
            <NuxtLink v-for="e in frontMatterMain" :key="e.chunk_index"
              :to="`/fathers/${ebookId}?page=${e.chunk_index + 1}`" @click="onTocClick"
              :class="['fathers-toc-item', e.chunk_index === currentPage - 1 ? 'is-current' : '']">
              {{ e.title }}
            </NuxtLink>
          </div>

          <!-- Volume tree -->
          <div v-for="(pg, pi) in parentGroups" :key="pi" class="mb-2">
            <button v-if="pg.name" @click="toggleParent(pg.name)"
              class="fathers-toc-parent">
              <span class="fathers-tri">{{ expandedParents.has(pg.name) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left truncate">{{ pg.name }}</span>
            </button>
            <div v-if="!pg.name || expandedParents.has(pg.name)" :class="pg.name ? 'ml-2 border-l border-[#d8c9a8] pl-1.5' : ''">
              <div v-for="(v, vi) in pg.volumes" :key="vi" class="mb-1">
                <button @click="toggleVol(v.name)" class="fathers-toc-vol">
                  <span class="fathers-tri">{{ expandedVols.has(v.name) ? '▾' : '▸' }}</span>
                  <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
                  <span class="fathers-toc-count">{{ v.entries.length }}</span>
                </button>
                <div v-if="expandedVols.has(v.name)" class="ml-3 border-l border-[#e0d4b8] pl-1.5 space-y-px">
                  <NuxtLink v-for="e in v.entries" :key="e.chunk_index"
                    :to="`/fathers/${ebookId}?page=${e.chunk_index + 1}`" @click="onTocClick"
                    :class="['fathers-toc-item', e.chunk_index === currentPage - 1 ? 'is-current' : '']">
                    {{ e.title }}
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Index entries collapsed -->
          <div v-if="indexEntries.length" class="mt-2">
            <button @click="indexOpen = !indexOpen" class="fathers-toc-parent">
              <span class="fathers-tri">{{ indexOpen ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left">索引</span>
              <span class="fathers-toc-count">{{ indexEntries.length }}</span>
            </button>
            <div v-if="indexOpen" class="ml-2 border-l border-[#d8c9a8] pl-1.5 space-y-px">
              <NuxtLink v-for="e in indexEntries" :key="e.chunk_index"
                :to="`/fathers/${ebookId}?page=${e.chunk_index + 1}`" @click="onTocClick"
                :class="['fathers-toc-item', e.chunk_index === currentPage - 1 ? 'is-current' : '']">
                {{ e.title }}
              </NuxtLink>
            </div>
          </div>
        </div>
      </aside>

      <!-- Reading area -->
      <div :class="['flex-1 overflow-y-auto fathers-scroll',
          displaySettings.theme === 'dark' ? 'ebook-theme-dark'
          : displaySettings.theme === 'sepia' ? 'ebook-theme-sepia' : '']"
        :style="{ '--ebook-font-scale': displaySettings.fontScale, '--ebook-line-height': displaySettings.lineHeight }"
        ref="scrollEl">
        <article :class="['fathers-article mx-auto px-8 sm:px-14 py-14 my-8',
          effectiveViewMode === 'parallel' && pageSourceOrder.length ? 'max-w-7xl' : 'max-w-3xl']">
          <div v-if="pageLoading" class="space-y-3 animate-pulse">
            <div v-for="i in 8" :key="i" :class="['h-4 bg-[#e3d7bd] rounded', i % 3 === 0 ? 'w-3/4' : 'w-full']"></div>
          </div>

          <template v-else-if="pageContent || pageSourceText">
            <!-- Cover page -->
            <div v-if="isCoverPage" class="fathers-cover">
              <div v-if="ebook?.cover_url" class="fathers-cover-img-wrap">
                <img :src="ebook.cover_url" :alt="ebook?.title" class="fathers-cover-img" />
              </div>
              <div class="fathers-cover-divider"><span>❦</span></div>
              <h1 class="fathers-cover-title">{{ ebook?.title }}</h1>
              <p v-if="ebook?.original_title" class="fathers-cover-orig"><em>{{ ebook.original_title }}</em></p>
              <div class="fathers-cover-authors">
                <p class="fathers-cover-author">
                  <span class="fathers-cover-tag">著</span>{{ ebook?.original_author || ebook?.author }}
                  <span v-if="ebook?.author_en" class="fathers-cover-en"> ({{ ebook.author_en }})</span>
                </p>
                <p v-if="ebook?.translator" class="fathers-cover-author">
                  <span class="fathers-cover-tag">譯</span>{{ ebook.translator }}
                </p>
              </div>
              <div v-if="ebook?.publisher || ebook?.publication_year" class="fathers-cover-imprint">
                <span v-if="ebook?.publisher">{{ ebook.publisher }}</span>
                <span v-if="ebook?.publisher && ebook?.publication_year"> · </span>
                <span v-if="ebook?.publication_year">{{ ebook.publication_year }}</span>
              </div>
            </div>

            <!-- Normal page -->
            <template v-else>
              <div class="fathers-crumb">
                <span v-if="pageVolume" class="fathers-crumb-vol">{{ pageVolume }}</span>
                <span v-if="pageVolume && cleanChapterLabel" class="fathers-crumb-arrow">›</span>
                <span class="fathers-crumb-ch">{{ cleanChapterLabel || `第 ${currentPage} 段` }}</span>
              </div>

              <!-- 中文（單欄）-->
              <div v-if="effectiveViewMode === 'zh'" class="ebook-prose" v-html="markdownHtml"></div>

              <!-- 單一來源語言 -->
              <div v-else-if="currentSourceLang" class="ebook-prose ebook-prose-en" v-html="currentSourceHtml"></div>

              <!-- 對照 -->
              <div v-else class="bilingual-rows">
                <div v-for="(row, idx) in parallelColumns.rows" :key="idx" class="flex flex-col lg:flex-row gap-x-8 gap-y-1 py-1">
                  <div class="ebook-prose lg:flex-[2]" v-html="row.zh"></div>
                  <div v-for="lang in parallelColumns.langs" :key="lang"
                    class="ebook-prose ebook-prose-en lg:flex-[3] lg:border-l lg:border-[#e0d4b8] lg:pl-8" v-html="row.cols[lang]"></div>
                </div>
                <section v-if="parallelColumns.footnotes.length" class="bilingual-footnotes ebook-prose">
                  <div class="footnotes-label">註　釋</div>
                  <div v-for="fn in parallelColumns.footnotes" :key="fn.num" class="flex flex-col lg:flex-row gap-x-8 footnote-row">
                    <div class="lg:flex-[2]" v-html="fn.zh || '&nbsp;'"></div>
                    <div v-for="lang in parallelColumns.langs" :key="lang"
                      class="ebook-prose-en lg:flex-[3] lg:border-l lg:border-[#e0d4b8] lg:pl-8" v-html="fn.cols[lang] || '&nbsp;'"></div>
                  </div>
                </section>
              </div>
            </template>

            <div class="flex justify-between mt-16 pt-6 border-t border-[#d8c9a8]">
              <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1" class="fathers-pagebtn">← 上一段</button>
              <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)" class="fathers-pagebtn">下一段 →</button>
            </div>
          </template>

          <div v-else class="text-center py-20 fathers-muted">此段無內容</div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  renderMarkdown, renderTocPage, normChapterKey,
  buildParallelColumns, renderSourceHtmlByLang,
} from "~/lib/ebook-render";
import {
  normalizeSources, resolveViewMode, migrateLegacyViewMode, langLabel,
} from "~/lib/multilang-sources";

definePageMeta({ middleware: "auth" });

interface TocSection { anchor_id: string; title: string; level: number }
interface TocEntry {
  chunk_index: number; title: string; level: number;
  volume?: string | null; parent_volume?: string | null; sections?: TocSection[];
}
interface VolumeGroup { name: string; entries: TocEntry[] }
interface ParentGroup { name: string | null; volumes: VolumeGroup[] }

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
const pageSourceText = ref<string | null>(null);
const pageSources = ref<Record<string, string>>({});
const pageSourceOrder = ref<string[]>([]);
const pageChapter = ref<string | null>(null);
const pageLoading = ref(false);
const scrollEl = ref<HTMLElement | null>(null);
const tocDrawerOpen = ref(true);

const displaySettings = ref<{ fontScale: number; lineHeight: number; theme: "light" | "sepia" | "dark" }>({
  fontScale: 1, lineHeight: 2, theme: "light",
});

// 🔊 朗讀（裝置語音）
const tts = useReaderTts();
let ttsEls: HTMLElement[] = [];
function clearTtsHighlight() { for (const el of ttsEls) el.classList.remove("tts-reading"); }
function toggleReadAloud() {
  if (tts.playing.value) { tts.stop(); clearTtsHighlight(); return; }
  const roots = Array.from(document.querySelectorAll(".fathers-article .ebook-prose:not(.ebook-prose-en)")) as HTMLElement[];
  ttsEls = [];
  const texts: string[] = [];
  for (const root of roots) {
    for (const el of Array.from(root.children) as HTMLElement[]) {
      const t = (el.innerText || "").trim();
      if (!t) continue;
      ttsEls.push(el); texts.push(t);
    }
  }
  tts.speakQueue(texts);
}
watch(tts.currentIdx, (i, prev) => {
  if (prev !== undefined && prev >= 0 && ttsEls[prev]) ttsEls[prev].classList.remove("tts-reading");
  if (i >= 0 && ttsEls[i]) { ttsEls[i].classList.add("tts-reading"); ttsEls[i].scrollIntoView({ block: "center", behavior: "smooth" }); }
});

// ── View mode (中 / 對照 / 單一來源) ──
type ViewMode = string;
const viewMode = ref<ViewMode>("zh");
const viewModeUserChosen = ref(false);
const savedViewMode = ref<string | null>(null);
const effectiveViewMode = computed(() => resolveViewMode(viewMode.value, pageSourceOrder.value));
const currentSourceLang = computed(() =>
  effectiveViewMode.value.startsWith("src:") ? effectiveViewMode.value.slice(4) : null
);
function setViewMode(m: ViewMode) {
  viewMode.value = m; viewModeUserChosen.value = true;
  try { localStorage.setItem("fathers-viewMode", m); } catch { /* private mode */ }
}
function modeBtnClass(m: ViewMode) {
  return ["fathers-mode", effectiveViewMode.value === m ? "is-on" : ""];
}
watch(pageSourceOrder, (order) => {
  if (savedViewMode.value && !viewModeUserChosen.value) {
    viewMode.value = migrateLegacyViewMode(savedViewMode.value, order);
    viewModeUserChosen.value = true;
  }
  if (order.length && !viewModeUserChosen.value && viewMode.value === "zh") {
    viewMode.value = "parallel"; // bilingual chunk → default to 對照
  }
});

// ── Chapter / volume context ──
const cleanChapterLabel = computed(() => (pageChapter.value || "").replace(/\[\^\d+\]/g, "").trim());
const pageVolume = computed<string | null>(() => {
  const here = toc.value.find(e => e.chunk_index === currentPage.value - 1);
  return here?.volume ?? null;
});
const isCoverPage = computed(() =>
  currentPage.value === 1 || pageChapter.value === "封面"
);

// ── TOC grouping (front matter / volumes / parent tree) ──
const frontMatter = computed(() => toc.value.filter(e => !e.volume));
function isIndexEntry(e: TocEntry): boolean {
  const t = (e.title || "").trim();
  return /索引$|^索引/.test(t)
      || /Index(?:es|ices)?(?: of|:|$)/i.test(t)
      || /(Scripture|Greek|Hebrew|Latin|French)\s+(?:Index|Words?\s*Index|Words?\s*and\s*Phrases?)/i.test(t);
}
const indexEntries = computed(() => frontMatter.value.filter(isIndexEntry));
const frontMatterMain = computed(() => frontMatter.value.filter(e => !isIndexEntry(e)));
const volumes = computed<VolumeGroup[]>(() => {
  const map = new Map<string, TocEntry[]>();
  for (const e of toc.value) {
    if (!e.volume) continue;
    if (!map.has(e.volume)) map.set(e.volume, []);
    map.get(e.volume)!.push(e);
  }
  return [...map].map(([name, entries]) => ({ name, entries }));
});
const parentGroups = computed<ParentGroup[]>(() => {
  const order: (string | null)[] = [];
  const map = new Map<string | null, VolumeGroup[]>();
  for (const v of volumes.value) {
    const parent = v.entries[0]?.parent_volume ?? null;
    if (!map.has(parent)) { map.set(parent, []); order.push(parent); }
    map.get(parent)!.push(v);
  }
  return order.map(name => ({ name, volumes: map.get(name)! }));
});
function shortVolumeName(name: string): string {
  const t = ebook.value?.title;
  if (t && name.startsWith(t + "：")) return name.slice(t.length + 1);
  if (t && name.startsWith(t + ":")) return name.slice(t.length + 1);
  return name;
}

// TOC expand/collapse state
const expandedParents = ref(new Set<string>());
const expandedVols = ref(new Set<string>());
const indexOpen = ref(false);
function toggleParent(name: string) {
  expandedParents.value.has(name) ? expandedParents.value.delete(name) : expandedParents.value.add(name);
  expandedParents.value = new Set(expandedParents.value);
}
function toggleVol(name: string) {
  expandedVols.value.has(name) ? expandedVols.value.delete(name) : expandedVols.value.add(name);
  expandedVols.value = new Set(expandedVols.value);
}
// Auto-expand the current chunk's parent + volume when TOC or page changes.
watch([toc, currentPage], () => {
  const here = toc.value.find(e => e.chunk_index === currentPage.value - 1);
  if (!here) return;
  if (here.parent_volume) { expandedParents.value.add(here.parent_volume); expandedParents.value = new Set(expandedParents.value); }
  if (here.volume) { expandedVols.value.add(here.volume); expandedVols.value = new Set(expandedVols.value); }
});
function onTocClick() { if (window.innerWidth < 1024) tocDrawerOpen.value = false; }

// ── Rendered HTML ──
const isTocPage = computed(() =>
  pageChapter.value === "目錄" || pageChapter.value === "目　錄" || pageChapter.value === "目　　錄"
);
const chapterIndexByTitle = computed(() => {
  const m = new Map<string, number>();
  for (const e of toc.value) m.set(normChapterKey(e.title), e.chunk_index);
  return m;
});
const markdownHtml = computed(() =>
  isTocPage.value
    ? renderTocPage(pageContent.value, chapterIndexByTitle.value)
    : renderMarkdown(pageContent.value, currentPage.value - 1)
);
const sourceHtmlByLang = computed(() =>
  renderSourceHtmlByLang(pageSources.value, pageSourceOrder.value, currentPage.value - 1)
);
const currentSourceHtml = computed(() =>
  currentSourceLang.value ? (sourceHtmlByLang.value[currentSourceLang.value] ?? "") : ""
);
const parallelColumns = computed(() =>
  buildParallelColumns(pageContent.value, pageSources.value, pageSourceOrder.value, currentPage.value - 1)
);

// ── Header series/vol chip ──
const seriesVol = computed<{ series: string; vol: number } | null>(() => {
  const src = `${ebook.value?.title ?? ""} ${ebook.value?.original_title ?? ""}`;
  const m = src.match(/(ANF|NPNF1|NPNF2|ACCS)\s*(?:on Scripture\s*)?vol\.?\s*(\d+)/i);
  return m ? { series: m[1].toUpperCase(), vol: parseInt(m[2]) } : null;
});

// ── Load ──
async function loadPage(page: number) {
  pageLoading.value = true;
  tts.stop(); clearTtsHighlight(); ttsEls = [];
  const token = await getToken(); if (!token) return;
  const isFirstLoad = !ebook.value;
  const url = `/api/ebooks/${ebookId}?page=${page}${isFirstLoad ? "&includeToc=1" : ""}`;
  const data = await $fetch<any>(url, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);

  if (data) {
    if (!ebook.value) ebook.value = data;
    if (data.toc) toc.value = data.toc;
  }
  pageContent.value = data?.currentPage?.content ?? "";
  const cp = data?.currentPage;
  const norm = normalizeSources({
    sources: cp?.sources ?? null,
    source_order: cp?.source_order ?? null,
    source_text: cp?.source_text ?? null,
    source_lang: cp?.source_lang ?? null,
  });
  pageSources.value = norm.sources;
  pageSourceOrder.value = norm.source_order;
  pageSourceText.value = norm.source_order.length ? norm.sources[norm.source_order[0]] : null;
  pageChapter.value = data?.currentPage?.chapter_path ?? null;
  pageLoading.value = false;
  jumpPage.value = page;

  await nextTick();
  scrollEl.value?.scrollTo({ top: 0, behavior: "auto" });
}

function goPage(p: number) {
  const max = ebook.value?.total_pages ?? 1;
  if (p < 1 || p > max) return;
  currentPage.value = p;
  router.push(`/fathers/${ebookId}?page=${p}`);
}

watch(currentPage, (p) => loadPage(p));
watch(() => route.query.page, (q) => {
  const p = parseInt(q as string ?? "1") || 1;
  if (p !== currentPage.value) currentPage.value = p;
});

onMounted(() => {
  try { savedViewMode.value = localStorage.getItem("fathers-viewMode"); } catch { /* private mode */ }
  loadPage(currentPage.value);
});

useHead({ title: () => ebook.value ? `${ebook.value.title} — 教父著作` : "教父著作" });
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&family=ZCOOL+XiaoWei&display=swap');
</style>

<style scoped>
/* ── Parchment palette ──
   紙面暖米、赭石點綴、宋體正文。與灰白電子圖書館 reader 明確區隔。 */
.fathers-reader {
  background:
    radial-gradient(circle at 20% 10%, rgba(196,163,90,0.05), transparent 40%),
    #e7dcc4;
  color: #35291a;
}
.fathers-topbar {
  background: linear-gradient(#f3ead4, #ece0c6);
  border-bottom: 1px solid #cbb98f;
  box-shadow: 0 1px 3px rgba(120,90,40,0.08);
}
.fathers-back { color: #7a5c2e; font-size: 0.875rem; transition: color .15s; }
.fathers-back:hover { color: #4a3717; }
.fathers-sep { color: #c4a35a; }
.fathers-title-text { color: #2a2013; }
.fathers-muted { color: #9c8a63; }
.fathers-chip {
  align-items: center; font-size: 11px; padding: 2px 8px; border-radius: 9999px;
  background: #6b4f27; color: #f3ead4; letter-spacing: .05em; font-weight: 600; flex-shrink: 0;
}
.fathers-tocbtn, .fathers-tool {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px;
  font-size: 12px; border: 1px solid #cbb98f; background: #f8f1de; color: #6b4f27; transition: all .15s;
}
.fathers-tocbtn:hover, .fathers-tool:hover { border-color: #a9884a; color: #4a3717; }
.fathers-tocbtn.is-on { background: #6b4f27; color: #f3ead4; border-color: #6b4f27; }
.fathers-tool.is-active { background: #b45309; color: #fff5e6; border-color: #b45309; }
.fathers-tool:disabled { opacity: .4; }
.fathers-navbtn {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border-radius: 8px; background: #e4d6b6; color: #6b4f27; transition: background .15s;
}
.fathers-navbtn:hover:not(:disabled) { background: #d8c398; }
.fathers-navbtn:disabled { opacity: .3; }
.fathers-pageinput {
  width: 56px; text-align: center; font-size: 14px; padding: 4px 8px; border-radius: 8px;
  background: #fbf6e9; border: 1px solid #cbb98f; color: #35291a;
}
.fathers-pageinput:focus { outline: none; border-color: #a9884a; }
.fathers-modeswitch {
  display: inline-flex; background: #e4d6b6; border-radius: 8px; padding: 2px; gap: 2px; font-size: 12px;
}
.fathers-mode { padding: 3px 10px; border-radius: 6px; color: #6b4f27; transition: all .15s; }
.fathers-mode:hover { color: #4a3717; }
.fathers-mode.is-on { background: #6b4f27; color: #f3ead4; font-weight: 600; }

/* ── TOC sidebar ── */
.fathers-toc {
  background: #efe4cb;
  border-right: 1px solid #cbb98f;
}
.fathers-toc-label {
  font-size: 11px; letter-spacing: .5em; text-indent: .5em; color: #a08a5c;
  text-align: center; margin: .25rem 0 1rem; font-weight: 600;
}
.fathers-toc-item {
  display: block; padding: 5px 8px; border-radius: 5px; font-size: 12.5px; color: #4a3a22;
  text-decoration: none; line-height: 1.4; transition: background .12s;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.fathers-toc-item:hover { background: #e2d3af; }
.fathers-toc-item.is-current { background: #6b4f27; color: #f3ead4; font-weight: 600; }
.fathers-toc-parent {
  width: 100%; display: flex; align-items: center; gap: 4px; padding: 5px 6px; border-radius: 5px;
  font-size: 13px; font-weight: 700; color: #3a2c17; transition: background .12s;
}
.fathers-toc-parent:hover { background: #e2d3af; }
.fathers-toc-vol {
  width: 100%; display: flex; align-items: center; gap: 4px; padding: 4px 6px; border-radius: 5px;
  font-size: 12.5px; font-weight: 600; color: #55432a; transition: background .12s;
}
.fathers-toc-vol:hover { background: #e2d3af; }
.fathers-tri { color: #a9884a; font-size: 11px; width: 12px; flex-shrink: 0; }
.fathers-toc-count { font-size: 10px; color: #a08a5c; font-weight: 400; flex-shrink: 0; }

/* ── Reading area ── */
.fathers-scroll { background: transparent; }
.fathers-article {
  background: #fbf6e9;
  border: 1px solid #d8c9a8;
  border-radius: 6px;
  box-shadow: 0 6px 28px -12px rgba(90,64,20,0.28), 0 2px 8px -3px rgba(90,64,20,0.12);
  position: relative;
}
.fathers-article::before {
  content: ""; position: absolute; inset: 0; border-radius: 6px; pointer-events: none;
  box-shadow: inset 0 0 60px rgba(180,140,70,0.06);
}
.fathers-pagebtn {
  padding: 8px 20px; background: #f3ead4; border: 1px solid #cbb98f; border-radius: 8px;
  font-size: 14px; color: #6b4f27; transition: all .15s;
}
.fathers-pagebtn:hover:not(:disabled) { border-color: #a9884a; color: #4a3717; background: #eaddc0; }
.fathers-pagebtn:disabled { opacity: .3; }

/* ── Breadcrumb ── */
.fathers-crumb { margin-bottom: 2.5rem; display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }
.fathers-crumb-vol { font-size: .95rem; font-weight: 600; color: #6b4f27; letter-spacing: .02em;
  font-family: "Noto Serif TC", serif; }
.fathers-crumb-arrow { color: #c4a35a; }
.fathers-crumb-ch { font-size: .75rem; text-transform: uppercase; letter-spacing: .1em; color: #9c8a63; }

/* ── Cover ── */
.fathers-cover { text-align: center; padding: 2rem 1rem 1rem;
  font-family: "Noto Serif TC", "Source Han Serif TC", serif; }
.fathers-cover-img-wrap {
  display: inline-block; width: min(300px, 58vw); aspect-ratio: 2/3; margin-bottom: 2rem;
  border-radius: 6px; overflow: hidden; border: 1px solid #cbb98f;
  box-shadow: 0 14px 40px -12px rgba(90,64,20,0.35);
}
.fathers-cover-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.fathers-cover-divider { color: #c4a35a; font-size: 1.4rem; margin: 1rem 0; }
.fathers-cover-title { font-size: 2rem; font-weight: 700; color: #2a2013; letter-spacing: .04em; line-height: 1.4; }
.fathers-cover-orig { margin-top: .5rem; color: #8a7145; font-size: 1rem; font-family: Georgia, serif; }
.fathers-cover-authors { margin-top: 1.75rem; }
.fathers-cover-author { color: #4a3a22; font-size: 1.05rem; margin: .35rem 0; }
.fathers-cover-tag {
  display: inline-block; font-size: .7rem; background: #6b4f27; color: #f3ead4;
  padding: 1px 6px; border-radius: 3px; margin-right: .5rem; vertical-align: middle; letter-spacing: .1em;
}
.fathers-cover-en { color: #9c8a63; font-family: Georgia, serif; font-size: .95rem; }
.fathers-cover-imprint { margin-top: 1.5rem; color: #9c8a63; font-size: .85rem; }

/* ── Prose (patristic parchment tuning of the shared render output) ── */
.ebook-prose {
  color: #2f2413;
  font-size: calc(17.5px * var(--ebook-font-scale, 1));
  line-height: var(--ebook-line-height, 2);
  font-family: "Noto Serif TC", "Source Han Serif TC", "PingFang TC", "Microsoft JhengHei", Georgia, serif;
}
.ebook-prose :deep(h1) { font-size: 2.1rem; font-weight: 700; margin: 2.5rem 0 1.75rem; color: #241a0d; text-align: center; letter-spacing: .03em; }
.ebook-prose :deep(h2) {
  font-size: 1.75rem; font-weight: 700; margin: 1rem 0 2.5rem; color: #241a0d; padding: 1.15rem 0 .9rem;
  border-top: 1px solid #d8c9a8; border-bottom: 3px double #a9884a; text-align: center; letter-spacing: .06em; line-height: 1.55;
}
.ebook-prose :deep(h2.section-notes-divider) {
  font-size: 13px; font-weight: 500; color: #b09a6c; margin: 4.5rem 0 2rem; padding: 0; border: 0;
  text-align: center; letter-spacing: .8em; text-indent: .8em; display: flex; align-items: center; justify-content: center; gap: 1.25rem;
}
.ebook-prose :deep(h2.section-notes-divider)::before,
.ebook-prose :deep(h2.section-notes-divider)::after { content: ""; flex: 0 0 6rem; height: 1px; background: #d8c9a8; }
.ebook-prose :deep(h3) { font-size: 1.35rem; font-weight: 600; margin: 2.5rem 0 1rem; color: #35291a;
  padding-left: .75rem; border-left: 4px solid #a9884a; letter-spacing: .02em; scroll-margin-top: 4rem; }
.ebook-prose :deep(h4) { font-size: 1.12rem; font-weight: 600; margin: 1.75rem 0 .75rem; color: #55432a; scroll-margin-top: 4rem; }
.ebook-prose :deep(p) { margin: 1.1rem 0; text-indent: 2em; text-align: justify; }
.ebook-prose :deep(strong) { font-weight: 700; color: #241a0d; }
.ebook-prose :deep(em) { font-style: italic; }
.ebook-prose :deep(em.book-title-en) { font-family: Georgia, "Times New Roman", serif; font-style: italic; font-weight: 500; color: #35291a; }
.ebook-prose :deep(blockquote) {
  border-left: 3px solid #c4a35a; padding: .75rem 1rem .75rem 1.5rem; margin: 1.75rem 0; color: #55432a;
  background: #f5ecd3; border-radius: 0 4px 4px 0;
  font-family: "ZCOOL XiaoWei", "DFKai-SB", "BiauKai", "標楷體", "Noto Serif TC", serif; font-size: 16.5px; line-height: 1.95;
}
.ebook-prose :deep(blockquote p) { text-indent: 0; }
.ebook-prose :deep(hr) { margin: 2rem 0; border: 0; border-top: 1px solid #e0d4b8; }
.ebook-prose :deep(.tts-reading) { background: rgba(180,83,9,.08); box-shadow: 0 0 0 6px rgba(180,83,9,.08); border-radius: .25rem; }

/* Footnotes */
.ebook-prose :deep(section.footnotes), .bilingual-footnotes {
  margin-top: 4rem; font-size: 12.5px; line-height: 1.85; color: #6b573a; position: relative;
}
.bilingual-footnotes { border-top: 1px solid #e0d4b8; padding-top: 2rem; }
.bilingual-footnotes .footnote-row { padding: .25rem 0; }
.ebook-prose :deep(.footnotes-label), .bilingual-footnotes .footnotes-label {
  font-size: 11px; letter-spacing: .4em; color: #b09a6c; text-align: center; margin: 0 auto 1.5rem;
  text-indent: .4em; display: flex; align-items: center; justify-content: center; gap: 1rem; font-weight: 500;
}
.ebook-prose :deep(.footnotes-label)::before, .ebook-prose :deep(.footnotes-label)::after {
  content: ""; flex: 0 0 5rem; height: 1px; background: #d8c9a8;
}
.ebook-prose :deep(.footnote-item) { margin: .6rem 0; text-indent: -2.2em; padding-left: 2.2em; text-align: justify; }
.ebook-prose :deep(.footnote-item:target) { background: #f5e6bf; border-left: 3px solid #b45309; padding-left: 2em; margin-left: -.5rem; padding-right: .5rem; border-radius: 0 4px 4px 0; scroll-margin-top: 4rem; }
.ebook-prose :deep(a.footnote-num) { color: #b45309; font-weight: 700; text-decoration: none; font-variant-numeric: tabular-nums; }
.ebook-prose :deep(a.footnote-num:hover) { text-decoration: underline; }
.ebook-prose :deep(sup.footnote-ref) { font-size: .75em; line-height: 0; margin: 0 1px; vertical-align: super; scroll-margin-top: 6rem; }
.ebook-prose :deep(sup.footnote-ref a) { color: #b45309; text-decoration: none; font-weight: 700; font-variant-numeric: tabular-nums; }
.ebook-prose :deep(sup.footnote-ref a:hover) { text-decoration: underline; }
.ebook-prose :deep(a.footnote-back) { color: #b09a6c; text-decoration: none; margin-left: .25rem; font-size: .95em; }
.ebook-prose :deep(a.footnote-back:hover) { color: #b45309; }

/* Page marker */
.ebook-prose :deep(.page-marker) {
  font-size: .65em; color: #a08a5c; background: #efe4cb; padding: 1px 5px; border-radius: 3px; margin: 0 3px;
  font-weight: 500; font-variant-numeric: tabular-nums; letter-spacing: .5px; vertical-align: 1px; white-space: nowrap; cursor: help; user-select: none;
}

/* 目錄 page render */
.ebook-prose :deep(.toc-page-title) { font-size: 1.75rem; font-weight: 700; margin: 1rem 0 2rem; text-align: center; letter-spacing: .6em; text-indent: .6em; color: #241a0d; padding: 1rem 0; border-top: 1px solid #d8c9a8; border-bottom: 3px double #a9884a; }
.ebook-prose :deep(.toc-volume) { font-size: 1.2rem; font-weight: 700; color: #241a0d; margin: 2rem 0 .5rem; letter-spacing: .15em; padding-bottom: .25rem; border-bottom: 1px solid #d8c9a8; }
.ebook-prose :deep(.toc-chapter) { margin: .4rem 0; padding-left: 1.5rem; line-height: 1.7; }
.ebook-prose :deep(.toc-chapter a) { display: flex; align-items: baseline; gap: .75rem; color: #35291a; text-decoration: none; padding: .3rem .5rem; border-radius: 4px; transition: background .15s; }
.ebook-prose :deep(.toc-chapter a:hover) { background: #f5e6bf; color: #241a0d; }
.ebook-prose :deep(.toc-ch-num) { flex: 0 0 4em; font-weight: 600; color: #6b573a; font-variant-numeric: tabular-nums; }
.ebook-prose :deep(.toc-ch-title) { flex: 1; font-weight: 500; }
.ebook-prose :deep(.toc-ch-title-solo) { flex: 1; font-weight: 600; color: #35291a; }
.ebook-prose :deep(.toc-chapter-orphan) { color: #b09a6c; }
.ebook-prose :deep(.toc-section) { padding-left: 4.5rem; margin: .15rem 0; font-size: .92em; color: #8a7145; line-height: 1.6; }

/* English/source column — Latin typography */
.ebook-prose-en { font-family: Georgia, "Times New Roman", "Source Serif Pro", serif; font-size: 16px; line-height: 1.75; }
.ebook-prose-en :deep(p) { text-indent: 0; margin: .9rem 0; }
.ebook-prose-en :deep(h1), .ebook-prose-en :deep(h2), .ebook-prose-en :deep(h3), .ebook-prose-en :deep(h4) { letter-spacing: 0; }
.ebook-prose-en :deep(blockquote) { font-style: italic; font-family: Georgia, "Times New Roman", serif; }

/* Sepia / dark theme overrides for the parchment reader */
.ebook-theme-sepia .fathers-article { background: #f7edd3; }
.ebook-theme-dark .fathers-article { background: #2b2416; border-color: #4a3f28; }
.ebook-theme-dark .fathers-article::before { box-shadow: none; }
.ebook-theme-dark .ebook-prose { color: #e6dcc4; }
.ebook-theme-dark .ebook-prose :deep(h1), .ebook-theme-dark .ebook-prose :deep(h2),
.ebook-theme-dark .ebook-prose :deep(h3), .ebook-theme-dark .ebook-prose :deep(h4) { color: #f3ead4; }
.ebook-theme-dark .ebook-prose :deep(blockquote) { color: #d8c9a8; background: #35291a; }
</style>
