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
            <NuxtLink to="/excerpts/journal" class="hover:text-amber-600 transition">期刊書摘</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900 truncate max-w-xs">{{ ja?.title ?? '載入中…' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 text-xs rounded-lg bg-amber-600 text-white hover:bg-amber-500" @click="showCreate = true">+ 新增文摘</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-amber-300 text-amber-800 hover:bg-amber-50" @click="showCSV = true">上傳 CSV</button>
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

      <template v-else-if="ja">
        <!-- ── 篇目資訊卡 ── -->
        <div class="bg-white rounded-2xl border border-gray-200 p-6 mb-8 shadow-sm">
          <div class="flex items-start gap-5">
            <div class="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 select-none">📰</div>
            <div class="flex-1">
              <h1 class="text-2xl font-bold text-gray-900 leading-tight mb-0.5">
                <InlineEdit :value="ja.title" placeholder="篇名" @save="(v) => saveJournalField('title', v)" />
              </h1>
              <p class="text-base text-gray-600 mb-2">
                <InlineEdit :value="ja.author ?? ''" placeholder="作者" @save="(v) => saveJournalField('author', v)" />
              </p>
              <div class="flex flex-wrap gap-x-5 gap-y-1 text-sm text-gray-500">
                <span v-if="ja.venue">刊名：{{ ja.venue }}</span>
                <span v-if="ja.issue_label">{{ ja.issue_label }}</span>
                <span v-if="ja.publish_year">年份：{{ ja.publish_year }}</span>
              </div>
              <p class="mt-3 text-sm text-amber-700 font-medium">共 {{ ja.excerpts?.length ?? 0 }} 筆摘文</p>
            </div>
          </div>
        </div>

        <!-- ── 空狀態 ── -->
        <div v-if="!ja.excerpts?.length" class="text-center py-16 text-gray-400">
          <p class="text-lg">此篇目尚無摘文</p>
        </div>

        <!-- ── 按章節分組顯示 ── -->
        <template v-else>
          <div class="mb-4 flex gap-2 max-w-xl">
            <select v-model="searchField" class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:ring-2 focus:ring-amber-400">
              <option value="all">全部</option>
              <option value="content">內容</option>
              <option value="title">標題</option>
            </select>
            <input
              v-model="searchQ"
              placeholder="搜尋此篇目"
              class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-amber-400"
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
                  class="bg-white rounded-xl border border-gray-200 p-5 hover:border-amber-200 transition-all duration-150 cursor-pointer relative"
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
                    <span v-if="ja?.author">{{ ja.author }}</span>
                    <span v-if="ja?.publish_year">（{{ ja.publish_year }}）</span>
                    <span v-if="ja?.venue" class="mx-1">·</span>
                    <span v-if="ja?.venue">《{{ ja.venue }}》</span>
                    <span v-if="ja?.issue_label" class="ml-1">· {{ ja.issue_label }}</span>
                    <span v-if="excerpt.page_number" class="ml-1">
                      · {{ formatPageLabel(excerpt.page_number, excerpt.content || excerpt.title || "") }}
                    </span>
                  </p>

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

      <div v-else class="text-center py-20 text-gray-400">找不到此篇目</div>
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
          <button class="px-3 py-1.5 text-sm bg-amber-600 text-white rounded-lg" @click="createExcerpt">建立</button>
        </div>
      </div>
    </div>

    <div v-if="showCSV" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">上傳 CSV 匯入文摘</h3>
        <input type="file" accept=".csv,text/csv" @change="onPickCSV" class="w-full text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCSV=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-amber-600 text-white rounded-lg" @click="uploadCSV">送出</button>
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
const journalId = route.params.id as string;

type Excerpt = {
  id: string; title: string | null; content: string;
  chapter: string | null; chapterName: string; page_number: string | null; created_at: string;
  projects: { id: string; name: string; type: string }[];
};
type JournalArt = {
  id: string;
  title: string;
  venue: string | null;
  author: string | null;
  publish_year: number | null;
  issue_label: string | null;
  excerpts: Excerpt[];
  chapterNameMap: Record<string, string>;
};

const loading = ref(true);
const ja = ref<JournalArt | null>(null);
const searchQ = ref("");
const searchField = ref<"all" | "content" | "title">("all");
const showCreate = ref(false);
const showCSV = ref(false);
const csvFile = ref<File | null>(null);
const form = ref({ title: "", chapter: "", page_number: "", content: "" });
const projectTargets = ref<{ id: string; name: string; type: string }[]>([]);
const importTargetByExcerpt = ref<Record<string, string>>({});
const importPanelByExcerpt = ref<Record<string, boolean>>({});
const importQueryByExcerpt = ref<Record<string, string>>({});
const expandedExcerptId = ref<string | null>(null);
const overflowById = ref<Record<string, boolean>>({});
const contentBoxRefs = new Map<string, HTMLElement>();

const TOPIC_ORDER = [
  "人間佛教",
  "印順學",
  "星雲法師與佛光山",
  "聖嚴法師與法鼓山",
  "證嚴法師與慈濟",
  "趙樸初居士",
];

// Group excerpts by chapter, ordered by topic
const chapterGroups = computed(() => {
  if (!ja.value?.excerpts) return [];
  const map = new Map<string, { chapter: string | null; chapterName: string; items: Excerpt[] }>();
  const NONE = "__none__";

  const q = searchQ.value.trim().toLowerCase();
  const source = !q
    ? ja.value.excerpts
    : ja.value.excerpts.filter((e) =>
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
        chapterName: ex.chapterName ?? (ex.chapter ? (ja.value.chapterNameMap?.[ex.chapter] ?? "") : ""),
        items: [],
      });
    }
    map.get(key)!.items.push(ex);
  }

  return [...map.entries()]
    .sort(([a], [b]) => {
      const ai = TOPIC_ORDER.indexOf(a);
      const bi = TOPIC_ORDER.indexOf(b);
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

async function fetchJournal() {
  const token = await getToken(); if (!token) return;
  ja.value = await $fetch<JournalArt>(`/api/journal-articles/${journalId}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);
  projectTargets.value = await $fetch<any[]>("/api/projects", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  loading.value = false;
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
  await fetchJournal();
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
  const ex = ja.value?.excerpts.find((e) => e.id === id);
  if (ex) (ex as any)[field] = value;
}
function onPickCSV(e: Event) {
  csvFile.value = (e.target as HTMLInputElement).files?.[0] || null;
}
async function createExcerpt() {
  const token = await getToken(); if (!token || !form.value.content.trim()) return;
  await $fetch("/api/excerpts", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: { ...form.value, book_id: null, journal_article_id: journalId },
  }).catch(() => null);
  showCreate.value = false;
  form.value = { title: "", chapter: "", page_number: "", content: "" };
  await fetchJournal();
}
async function uploadCSV() {
  const token = await getToken(); if (!token || !csvFile.value) return;
  const fd = new FormData();
  fd.append("file", csvFile.value);
  fd.append("journalArticleId", journalId);
  await $fetch("/api/excerpts/import-csv", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  }).catch(() => null);
  showCSV.value = false;
  csvFile.value = null;
  await fetchJournal();
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

async function saveJournalField(field: string, value: unknown) {
  const token = await getToken(); if (!token) return;
  await $fetch(`/api/journal-articles/${journalId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: { [field]: value },
  }).catch(console.error);
  if (ja.value) (ja.value as any)[field] = value;
}

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(() => {
  const saved = localStorage.getItem("excerpts-journal-search-field");
  if (saved && ["all", "content", "title"].includes(saved)) {
    searchField.value = saved as any;
  }
  fetchJournal();
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
  localStorage.setItem("excerpts-journal-search-field", v);
});
useHead({ title: computed(() => ja.value ? `${ja.value.title} — 期刊書摘` : "期刊書摘") });
</script>
