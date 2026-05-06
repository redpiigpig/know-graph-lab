<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>書摘庫</span>
            </NuxtLink>
            <span>›</span>
            <NuxtLink to="/excerpts/library" class="hover:text-blue-600 transition">書摘圖書館</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900 truncate max-w-xs">{{ book?.title ?? '載入中…' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-500" @click="showCreate = true">+ 新增文摘</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50" @click="showOCR = true">上傳照片</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50" @click="showCSV = true">上傳 CSV</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-emerald-300 text-emerald-700 hover:bg-emerald-50"
              :disabled="!book?.excerpts?.length" @click="exportMarkdown">📋 匯出 Markdown</button>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <!-- 載入骨架 -->
      <div v-if="loading" class="space-y-4 animate-pulse">
        <div class="bg-white rounded-2xl p-8 h-36"></div>
        <div class="bg-white rounded-xl p-6 h-24"></div>
      </div>

      <template v-else-if="book">
        <!-- ── 書籍資訊卡 ── -->
        <div class="bg-white rounded-2xl border border-gray-200 p-6 mb-8 shadow-sm">
          <div class="flex items-start gap-5">
            <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 select-none">📚</div>
            <div class="flex-1">
              <!-- 書名（可編輯） -->
              <h1 class="text-2xl font-bold text-gray-900 leading-tight mb-0.5">
                <InlineEdit :value="book.title" placeholder="書名" @save="(v) => saveBookField('title', v)" />
              </h1>
              <!-- 作者（可編輯） -->
              <p class="text-base text-gray-600 mb-3">
                <InlineEdit :value="book.author ?? ''" placeholder="作者" @save="(v) => saveBookField('author', v)" />
              </p>

              <!-- 中文版資訊 -->
              <div class="flex flex-wrap gap-x-5 gap-y-1 text-sm text-gray-500 mb-3">
                <span v-if="book.translator">譯者：{{ book.translator }}</span>
                <span v-if="book.publisher">中文出版社：{{ book.publisher }}</span>
                <span v-if="book.publish_year">中文出版年：{{ book.publish_year }}</span>
                <span v-if="book.edition">{{ book.edition }}</span>
              </div>

              <!-- 原書資訊（翻譯書才顯示） -->
              <div v-if="book.translator" class="border-t border-dashed border-gray-200 pt-3 mt-1">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">原書資訊</p>
                <div class="flex flex-wrap gap-x-5 gap-y-1 text-sm text-gray-600">
                  <span class="flex items-center gap-1">
                    <span class="text-gray-400 text-xs">原作者：</span>
                    <InlineEdit
                      :value="book.original_author ?? ''"
                      placeholder="待填寫"
                      class="text-gray-700"
                      @save="(v) => saveBookField('original_author', v)"
                    />
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="text-gray-400 text-xs">原書名：</span>
                    <InlineEdit
                      :value="book.original_title ?? ''"
                      placeholder="待填寫"
                      class="text-gray-700"
                      @save="(v) => saveBookField('original_title', v)"
                    />
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="text-gray-400 text-xs">原出版社：</span>
                    <InlineEdit
                      :value="book.original_publisher ?? ''"
                      placeholder="待填寫"
                      class="text-gray-700"
                      @save="(v) => saveBookField('original_publisher', v)"
                    />
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="text-gray-400 text-xs">原出版年：</span>
                    <InlineEdit
                      :value="book.original_publish_year ? String(book.original_publish_year) : ''"
                      placeholder="待填寫"
                      class="text-gray-700"
                      @save="(v) => saveBookField('original_publish_year', Number(v) || null)"
                    />
                  </span>
                </div>
              </div>

              <p class="mt-3 text-sm text-blue-600 font-medium">共 {{ book.excerpts?.length ?? 0 }} 筆摘文</p>
              <div class="mt-3">
                <TagPicker :model-value="bookTagIds" @update:model-value="saveBookTags" />
              </div>
            </div>
          </div>
        </div>

        <!-- ── 空狀態 ── -->
        <div v-if="!book.excerpts?.length" class="text-center py-16 text-gray-400">
          <p class="text-lg">此書尚無摘文</p>
        </div>

        <!-- ── 按章節分組顯示 ── -->
        <template v-else>
          <div class="mb-4 flex gap-2 max-w-xl">
            <select v-model="searchField" class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:ring-2 focus:ring-blue-400">
              <option value="all">全部</option>
              <option value="content">內容</option>
              <option value="title">標題</option>
            </select>
            <input
              v-model="searchQ"
              placeholder="搜尋此書"
              class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <template v-for="group in chapterGroups" :key="group.chapter ?? '__none__'">
            <!-- 章節 h3 標題 + 分隔線 -->
            <div class="relative flex items-center justify-center my-8 first:mt-0">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full h-px bg-gray-200"></div>
              </div>
              <h3 class="relative bg-gray-50 px-4 text-center text-sm font-semibold text-gray-600">
                <span v-if="group.chapter" class="text-purple-600 font-bold">{{ group.chapter }}</span>
                <span v-if="group.chapter && group.chapterName" class="text-gray-400 mx-1">·</span>
                <span v-if="group.chapterName">{{ group.chapterName }}</span>
                <span v-if="!group.chapter" class="text-gray-400">未分章</span>
              </h3>
            </div>

            <!-- 章節內摘文 -->
            <div class="space-y-3 mb-2">
              <template v-for="excerpt in group.items" :key="excerpt.id">
                <div
                  :data-excerpt-card-id="excerpt.id"
                  class="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-all duration-150 cursor-pointer relative"
                  @click="toggleExpand(excerpt.id)"
                >
                  <div class="absolute right-3 top-3 z-10" @click.stop>
                    <button
                      class="w-8 h-8 rounded-full border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 text-sm"
                      title="匯入到著作/文章"
                      @click="toggleImportPanel(excerpt.id)"
                    >📥</button>
                    <div
                      v-if="importPanelByExcerpt[excerpt.id]"
                      class="mt-1 w-72 bg-white border border-gray-200 rounded-lg shadow-lg p-2"
                    >
                      <input
                        v-model="importQueryByExcerpt[excerpt.id]"
                        type="text"
                        placeholder="搜尋待寫著作 / 待寫文章"
                        class="w-full px-2 py-1.5 border border-gray-200 rounded text-xs mb-2 outline-none focus:ring-2 focus:ring-indigo-300"
                      />
                      <select
                        v-model="importTargetByExcerpt[excerpt.id]"
                        class="w-full px-2 py-1.5 border border-gray-200 rounded text-xs bg-white mb-2"
                      >
                        <option value="">請選擇匯入目標</option>
                        <option v-for="p in filteredProjectTargets(excerpt.id)" :key="p.id" :value="p.id">
                          {{ p.type }}｜{{ p.name }}
                        </option>
                      </select>
                      <button
                        class="w-full px-2 py-1.5 text-xs rounded bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-40"
                        :disabled="!importTargetByExcerpt[excerpt.id]"
                        @click="importToProject(excerpt.id)"
                      >匯入</button>
                    </div>
                  </div>
                  <div class="flex items-start gap-2 mb-2">
                    <h4 class="font-semibold text-base text-gray-900 flex-1 min-w-0 leading-snug">
                      <InlineEdit
                        :value="excerpt.title ?? ''"
                        placeholder="（無標題）"
                        @save="(v) => saveExcerptField(excerpt.id, 'title', v)"
                      />
                      <p
                        v-if="searchQ.trim()"
                        class="text-xs text-gray-700 mt-1"
                        v-html="highlightText(excerpt.title || '（無標題）')"
                      ></p>
                    </h4>
                  </div>

                  <p class="text-xs text-gray-400 mb-3">
                    <span v-if="book?.author">{{ book.author }}</span>
                    <span v-if="book?.author && (book?.original_publish_year ?? book?.publish_year)">
                      （{{ book.original_publish_year ?? book.publish_year }}）
                    </span>
                    <span v-if="book?.title" class="mx-1">·</span>
                    <span v-if="book?.title">《{{ book.title }}》</span>
                    <span v-if="excerpt.page_number" class="ml-1">
                      · {{ formatPageLabel(excerpt.page_number, excerpt.content || excerpt.title || "") }}
                    </span>
                  </p>
                  <div class="mb-2" @click.stop>
                    <TagPicker :model-value="excerptTagIds[excerpt.id] ?? []"
                      @update:model-value="(ids) => saveExcerptTags(excerpt.id, ids)" />
                  </div>

                  <div
                    class="overflow-hidden transition-all duration-200 relative"
                    :class="expandedExcerptId === excerpt.id ? 'max-h-[1000px]' : 'max-h-[9.75rem]'"
                    :ref="(el) => setContentBoxRef(excerpt.id, el as HTMLElement | null)"
                  >
                    <InlineEdit
                      :value="excerpt.content"
                      placeholder="（無內容）"
                      multiline
                      class="text-sm text-gray-700 leading-relaxed [text-indent:2em]"
                      @save="(v) => saveExcerptField(excerpt.id, 'content', v)"
                    />
                    <div
                      v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                      class="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"
                    ></div>
                    <div
                      v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                      class="absolute bottom-0 right-1 text-gray-400 text-sm pointer-events-none"
                    >...</div>
                  </div>
                  <p
                    v-if="searchQ.trim()"
                    class="text-sm text-gray-700 leading-relaxed mt-1 whitespace-pre-wrap [text-indent:2em]"
                    v-html="highlightText(excerpt.content || '')"
                  ></p>

                  <div v-if="excerpt.projects?.length" class="flex flex-wrap gap-1.5 mt-2">
                    <span
                      v-for="p in excerpt.projects" :key="p.id"
                      :class="projectBadge(p.type)"
                      class="text-xs px-2 py-0.5 rounded-full"
                    >{{ p.name }}</span>
                  </div>
                </div>

              </template>
            </div>
          </template>
        </template>
      </template>

      <div v-else class="text-center py-20 text-gray-400">找不到此書</div>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-xl bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">新增文摘</h3>
        <input v-model="form.title" placeholder="標題" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" />
        <div class="grid grid-cols-2 gap-2 mb-2">
          <input v-model="form.chapter" placeholder="章節" class="px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.page_number" placeholder="頁碼" class="px-3 py-2 border rounded-lg text-sm" />
        </div>
        <textarea v-model="form.content" rows="6" placeholder="內文" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCreate=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg" @click="createExcerpt">建立</button>
        </div>
      </div>
    </div>

    <div v-if="showOCR" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">上傳照片 OCR</h3>
        <input type="file" accept="image/*" @change="onPickImage" class="w-full text-sm mb-2" />
        <input v-model="ocrStartPage" placeholder="起始頁碼（預設1）" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showOCR=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg" @click="uploadOCR">送出</button>
        </div>
      </div>
    </div>

    <div v-if="showCSV" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">上傳 CSV 匯入文摘</h3>
        <input type="file" accept=".csv,text/csv" @change="onPickCSV" class="w-full text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCSV=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg" @click="uploadCSV">送出</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const bookId = route.params.bookId as string;

type Excerpt = {
  id: string; title: string | null; content: string;
  chapter: string | null; chapterName: string; page_number: string | null; created_at: string;
  projects: { id: string; name: string; type: string }[];
};
type Book = {
  id: string; title: string; author: string;
  translator?: string; publish_place?: string; publisher?: string;
  publish_year?: number; edition?: string; category_id?: string;
  original_author?: string; original_title?: string; original_publisher?: string; original_publish_year?: number;
  excerpts: Excerpt[];
  chapterNameMap: Record<string, string>;
};

const loading = ref(true);
const book = ref<Book | null>(null);
const searchQ = ref("");
const searchField = ref<"all" | "content" | "title">("all");
const showCreate = ref(false);
const showOCR = ref(false);
const showCSV = ref(false);
const ocrFile = ref<File | null>(null);
const csvFile = ref<File | null>(null);
const ocrStartPage = ref("1");
const form = ref({ title: "", chapter: "", page_number: "", content: "" });
const projectTargets = ref<{ id: string; name: string; type: string }[]>([]);
const importTargetByExcerpt = ref<Record<string, string>>({});
const importPanelByExcerpt = ref<Record<string, boolean>>({});
const importQueryByExcerpt = ref<Record<string, string>>({});
const expandedExcerptId = ref<string | null>(null);
const overflowById = ref<Record<string, boolean>>({});
const contentBoxRefs = new Map<string, HTMLElement>();

// Chapter ordering helper
const CHAPTER_ORDER = Array.from({ length: 30 }, (_, i) => {
  const nums = ["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十"];
  return `第${nums[i]}章`;
});

// Group excerpts by chapter, ordered by chapter code
const chapterGroups = computed(() => {
  if (!book.value?.excerpts) return [];
  const map = new Map<string, { chapter: string | null; chapterName: string; items: Excerpt[] }>();
  const NONE = "__none__";

  const q = searchQ.value.trim().toLowerCase();
  const source = !q
    ? book.value.excerpts
    : book.value.excerpts.filter((e) =>
      searchField.value === "title"
        ? (e.title || "").toLowerCase().includes(q)
        : searchField.value === "content"
        ? (e.content || "").toLowerCase().includes(q)
        : (e.title || "").toLowerCase().includes(q) || (e.content || "").toLowerCase().includes(q)
    );

  for (const ex of source) {
    const key = ex.chapter ?? NONE;
    if (!map.has(key)) {
      map.set(key, {
        chapter: ex.chapter,
        chapterName: ex.chapterName ?? (ex.chapter ? (book.value.chapterNameMap?.[ex.chapter] ?? "") : ""),
        items: [],
      });
    }
    map.get(key)!.items.push(ex);
  }

  return [...map.entries()]
    .sort(([a], [b]) => {
      const ai = CHAPTER_ORDER.indexOf(a);
      const bi = CHAPTER_ORDER.indexOf(b);
      if (a === NONE) return 1;
      if (b === NONE) return -1;
      if (ai === -1 && bi === -1) return a.localeCompare(b);
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
    })
    .map(([, g]) => ({
      ...g,
      items: [...g.items].sort(compareExcerptByPage),
    }));
});

function pageSortValue(raw: string | null | undefined): number {
  const s = (raw || "").trim().toLowerCase();
  if (!s) return Number.MAX_SAFE_INTEGER;
  const cleaned = s
    .replace(/^p(?:age)?\.?\s*/i, "")
    .replace(/^頁\s*/i, "");
  const m = cleaned.match(/\d+/);
  return m ? Number(m[0]) : Number.MAX_SAFE_INTEGER;
}

function compareExcerptByPage(a: Excerpt, b: Excerpt): number {
  const pa = pageSortValue(a.page_number);
  const pb = pageSortValue(b.page_number);
  if (pa !== pb) return pa - pb;
  return (a.created_at || "").localeCompare(b.created_at || "");
}
function toggleExpand(id: string) {
  expandedExcerptId.value = expandedExcerptId.value === id ? null : id;
  nextTick(recomputeOverflow);
}
function setContentBoxRef(id: string, el: HTMLElement | null) {
  if (!el) {
    contentBoxRefs.delete(id);
    return;
  }
  contentBoxRefs.set(id, el);
}
function recomputeOverflow() {
  const next: Record<string, boolean> = {};
  for (const [id, el] of contentBoxRefs.entries()) {
    next[id] = el.scrollHeight > el.clientHeight + 1;
  }
  overflowById.value = next;
}
function onGlobalClick(e: MouseEvent) {
  const target = e.target as HTMLElement | null;
  if (!target) return;
  if (target.closest("[title='匯入到著作/文章']")) return;
  if (target.closest("[data-excerpt-card-id]")) return;
  expandedExcerptId.value = null;
  importPanelByExcerpt.value = {};
  nextTick(recomputeOverflow);
}

function projectBadge(type: string) {
  const map: Record<string, string> = {
    "待寫著作": "bg-purple-100 text-purple-700",
    "待寫文章": "bg-green-100 text-green-700",
    "書摘":     "bg-blue-100 text-blue-700",
  };
  return map[type] ?? "bg-gray-100 text-gray-600";
}

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

async function fetchBook() {
  const token = await getToken(); if (!token) return;
  book.value = await $fetch<Book>(`/api/books/${bookId}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);
  projectTargets.value = await $fetch<any[]>("/api/projects", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  loading.value = false;
  // Tags load in parallel — separate endpoints per entity, kept out of the
  // main /api/books/:id payload so they refresh independently when changed.
  loadBookTags();
  loadAllExcerptTags();
}

// ── Tags ──
const bookTagIds = ref<string[]>([]);
const excerptTagIds = ref<Record<string, string[]>>({});

async function loadBookTags() {
  const token = await getToken(); if (!token) return;
  const tags = await $fetch<{ id: string }[]>(`/api/books/${bookId}/tags`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  bookTagIds.value = tags.map((t) => t.id);
}

async function saveBookTags(ids: string[]) {
  const token = await getToken(); if (!token) return;
  bookTagIds.value = ids; // optimistic
  await $fetch(`/api/books/${bookId}/tags`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: { tag_ids: ids },
  }).catch(() => null);
}

async function loadAllExcerptTags() {
  const ids = (book.value?.excerpts ?? []).map((e: any) => e.id);
  if (!ids.length) return;
  const token = await getToken(); if (!token) return;
  // N small calls — fine for typical books (< ~50 excerpts). If this gets
  // hot, swap for one bulk endpoint.
  const results = await Promise.all(ids.map(async (id: string) => {
    const tags = await $fetch<{ id: string }[]>(`/api/excerpts/${id}/tags`, {
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => []);
    return [id, tags.map((t) => t.id)] as const;
  }));
  excerptTagIds.value = Object.fromEntries(results);
}

async function saveExcerptTags(excerptId: string, ids: string[]) {
  const token = await getToken(); if (!token) return;
  excerptTagIds.value = { ...excerptTagIds.value, [excerptId]: ids };
  await $fetch(`/api/excerpts/${excerptId}/tags`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: { tag_ids: ids },
  }).catch(() => null);
}

// ── Markdown citation export ──
function buildMarkdown(): string {
  const b = book.value as any;
  if (!b) return "";
  const lines: string[] = [];

  // Header — full bibliographic record
  lines.push(`# ${b.title}`);
  if (b.author) lines.push("");
  const ch = [
    b.author,
    b.translator ? `${b.translator} 譯` : null,
    b.publish_year ? `(${b.publish_year})` : null,
  ].filter(Boolean).join(", ");
  const tail = [b.publisher, b.publish_place].filter(Boolean).join("：");
  if (ch || tail) lines.push(`**${ch}${tail ? `. ${tail}` : ""}.**`);

  // Original publication line — only when this is a translation
  const orig = [
    b.original_author,
    b.original_title ? `*${b.original_title}*` : null,
    b.original_publish_year ? `(${b.original_publish_year})` : null,
    b.original_publisher,
  ].filter(Boolean);
  if (orig.length) {
    lines.push("");
    lines.push(`> 原書：${orig.join(", ")}`);
  }

  // Excerpts grouped by chapter (reuse the existing chapterGroups computation)
  for (const group of chapterGroups.value as any[]) {
    lines.push("");
    lines.push("");
    const chapHeader = group.chapter
      ? (group.chapterName ? `${group.chapter} · ${group.chapterName}` : group.chapter)
      : "未分章";
    lines.push(`## ${chapHeader}`);

    for (const ex of group.items) {
      lines.push("");
      if (ex.title) lines.push(`### ${ex.title}`);
      lines.push("");
      // Quote the body — prefix every line with > so multi-paragraph
      // content stays a blockquote.
      for (const line of (ex.content || "").split("\n")) {
        lines.push(`> ${line}`);
      }
      // Citation tail
      const cite: string[] = [];
      cite.push(`《${b.title}》`);
      if (group.chapter) cite.push(group.chapter);
      if (ex.page_number) cite.push(formatPageLabel(ex.page_number, ex.content || ex.title || ""));
      lines.push("");
      lines.push(`> ——${cite.join("，")}`);
    }
  }

  lines.push("");
  return lines.join("\n");
}

async function exportMarkdown() {
  const md = buildMarkdown();
  if (!md) return;
  // Try clipboard first; fall back to a download trigger if blocked
  // (some browsers refuse clipboard writes outside user gestures even
  // though we ARE in one — better to ALSO offer the download).
  try {
    await navigator.clipboard.writeText(md);
    alert(`已複製到剪貼簿（${md.length} 字元）。同時下載為 .md 檔。`);
  } catch {
    alert(`下載 .md 檔（${md.length} 字元）`);
  }
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(book.value as any)?.title ?? "book"}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
async function importToProject(excerptId: string) {
  const projectId = importTargetByExcerpt.value[excerptId];
  if (!projectId) return;
  const token = await getToken(); if (!token) return;
  await $fetch(`/api/projects/${projectId}/attach`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: { excerptIds: [excerptId] },
  }).catch(() => null);
  importTargetByExcerpt.value[excerptId] = "";
  importPanelByExcerpt.value[excerptId] = false;
  importQueryByExcerpt.value[excerptId] = "";
  await fetchBook();
}
function toggleImportPanel(excerptId: string) {
  importPanelByExcerpt.value[excerptId] = !importPanelByExcerpt.value[excerptId];
  if (!importPanelByExcerpt.value[excerptId]) {
    importQueryByExcerpt.value[excerptId] = "";
  }
}
function filteredProjectTargets(excerptId: string) {
  const q = (importQueryByExcerpt.value[excerptId] || "").trim().toLowerCase();
  const base = projectTargets.value.filter((p) => p.type === "待寫著作" || p.type === "待寫文章");
  if (!q) return base;
  return base.filter((p) => `${p.type} ${p.name}`.toLowerCase().includes(q));
}

async function saveExcerptField(id: string, field: "title" | "content", value: string) {
  const token = await getToken(); if (!token) return;
  await $fetch(`/api/excerpts/${id}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: { [field]: value },
  }).catch(console.error);
  const ex = book.value?.excerpts.find((e) => e.id === id);
  if (ex) (ex as any)[field] = value;
}
function onPickImage(e: Event) {
  ocrFile.value = (e.target as HTMLInputElement).files?.[0] || null;
}
function onPickCSV(e: Event) {
  csvFile.value = (e.target as HTMLInputElement).files?.[0] || null;
}
async function createExcerpt() {
  const token = await getToken(); if (!token || !form.value.content.trim()) return;
  await $fetch("/api/excerpts", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: { ...form.value, book_id: bookId },
  }).catch(() => null);
  showCreate.value = false;
  form.value = { title: "", chapter: "", page_number: "", content: "" };
  await fetchBook();
}
async function uploadOCR() {
  const token = await getToken(); if (!token || !ocrFile.value) return;
  const fd = new FormData();
  fd.append("image", ocrFile.value);
  fd.append("bookId", bookId);
  fd.append("startPage", ocrStartPage.value || "1");
  await $fetch("/api/ai/ocr", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  }).catch(() => null);
  showOCR.value = false;
  ocrFile.value = null;
  await fetchBook();
}
async function uploadCSV() {
  const token = await getToken(); if (!token || !csvFile.value) return;
  const fd = new FormData();
  fd.append("file", csvFile.value);
  fd.append("bookId", bookId);
  await $fetch("/api/excerpts/import-csv", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  }).catch(() => null);
  showCSV.value = false;
  csvFile.value = null;
  await fetchBook();
}
function highlightText(text: string): string {
  const q = searchQ.value.trim();
  if (!q) return escapeHtml(text);
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const reg = new RegExp(`(${escaped})`, "gi");
  return escapeHtml(text).replace(reg, '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>');
}
function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
function formatPageLabel(rawPage: string, contextText: string): string {
  const raw = (rawPage || "").trim();
  if (!raw) return "";
  const cleaned = raw
    .replace(/^p\.?\s*/i, "")
    .replace(/^page\s*/i, "")
    .replace(/^頁\s*/i, "")
    .trim();
  const isChinese = /[\u4E00-\u9FFF]/.test(contextText);
  return isChinese ? `頁${cleaned}` : `p. ${cleaned}`;
}

async function saveBookField(field: string, value: unknown) {
  const token = await getToken(); if (!token) return;
  await $fetch(`/api/books/${bookId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: { [field]: value },
  }).catch(console.error);
  if (book.value) (book.value as any)[field] = value;
}

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(() => {
  const saved = localStorage.getItem("excerpts-library-search-field");
  if (saved && ["all", "content", "title"].includes(saved)) {
    searchField.value = saved as any;
  }
  fetchBook();
  document.addEventListener("click", onGlobalClick);
  window.addEventListener("resize", recomputeOverflow);
  nextTick(recomputeOverflow);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onGlobalClick);
  window.removeEventListener("resize", recomputeOverflow);
});
watch([chapterGroups, expandedExcerptId], () => nextTick(recomputeOverflow));
watch(searchField, (v) => {
  localStorage.setItem("excerpts-library-search-field", v);
});
useHead({ title: computed(() => book.value ? `${book.value.title} — 書摘` : "書摘") });
</script>
