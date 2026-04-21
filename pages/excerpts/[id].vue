<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <button
            @click="router.back()"
            class="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="font-medium">返回書摘庫</span>
          </button>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/excerpts" class="text-gray-600 hover:text-blue-600 transition text-sm flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>書摘庫</span>
            </NuxtLink>
            <NuxtLink to="/settings" class="text-gray-600 hover:text-blue-600 transition text-sm">API Keys</NuxtLink>
          </div>
        </div>
      </div>
    </nav>

    <!-- 載入中 -->
    <div v-if="loading" class="max-w-4xl mx-auto px-4 py-12">
      <div class="bg-white rounded-2xl border border-gray-200 p-8 animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div class="h-7 bg-gray-200 rounded w-3/4 mb-6"></div>
        <div class="space-y-3">
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    </div>

    <!-- 找不到 -->
    <div v-else-if="!excerpt" class="max-w-4xl mx-auto px-4 py-20 text-center text-gray-400">
      <p class="text-xl">找不到這筆摘文</p>
      <NuxtLink to="/excerpts" class="mt-4 inline-block text-blue-600 hover:underline">返回書摘庫</NuxtLink>
    </div>

    <!-- 內容 -->
    <div v-else class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 書籍資訊卡 -->
      <div class="bg-white rounded-2xl border border-gray-200 px-6 py-5 mb-6 flex items-center space-x-4">
        <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-gray-900 truncate text-lg">{{ excerpt.books?.title ?? '（未知書名）' }}</p>
          <p class="text-sm text-gray-500">
            {{ excerpt.books?.author ?? '（未知作者）' }}
            <span v-if="excerpt.chapter" class="ml-2 text-gray-400">{{ excerpt.chapter }}</span>
            <span v-if="startPage" class="ml-2 text-gray-400">起始頁 {{ startPage }}</span>
          </p>
        </div>
        <div class="flex flex-wrap gap-1.5 justify-end">
          <span
            v-for="ep in excerpt.excerpt_book_projects"
            :key="ep.book_project_id"
            :class="projectTagClass(ep.book_projects?.type)"
            class="px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap"
          >
            {{ ep.book_projects?.type }}
          </span>
        </div>
      </div>

      <!-- 摘文主體 -->
      <div class="bg-white rounded-2xl border border-gray-200 p-8">
        <h1 v-if="excerpt.title" class="text-2xl font-bold text-gray-900 mb-6 leading-snug">
          {{ excerpt.title }}
        </h1>

        <!-- 複製提示 -->
        <div class="flex items-center justify-between mb-5 pb-4 border-b border-gray-100">
          <p class="text-xs text-gray-400">選取文字後複製，會自動附上標準引用</p>
          <!-- 複製成功 toast -->
          <transition name="fade">
            <span v-if="copyToastVisible" class="text-xs text-green-600 font-medium flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
              已複製（含引用）
            </span>
          </transition>
        </div>

        <!-- 多頁內文（用 --- 分頁） -->
        <div ref="contentEl" @copy.capture.prevent="handleCopy">
          <template v-for="(section, index) in contentSections" :key="index">
            <!-- 頁碼標記區塊 -->
            <div :data-page="pageForSection(index)">
              <div class="space-y-1.5">
                <div
                  v-for="(line, li) in renderSection(section)"
                  :key="`${index}-${li}`"
                  :class="line.className"
                  v-html="line.html"
                ></div>
              </div>
            </div>

            <!-- 虛線分頁線（除了最後一頁） -->
            <div
              v-if="index < contentSections.length - 1"
              class="flex items-center gap-3 my-5 select-none"
            >
              <div class="flex-1 border-t border-dashed border-gray-300"></div>
              <span class="text-xs font-mono text-gray-400 px-2 py-0.5 border border-dashed border-gray-300 rounded">
                頁 {{ pageForSection(index + 1) }}
              </span>
              <div class="flex-1 border-t border-dashed border-gray-300"></div>
            </div>
          </template>
        </div>

        <!-- 底部 meta -->
        <div class="mt-8 pt-6 border-t border-gray-100 flex items-center justify-between text-sm text-gray-400">
          <span>加入於 {{ formatDate(excerpt.created_at) }}</span>
          <span v-if="excerpt.updated_at !== excerpt.created_at">更新於 {{ formatDate(excerpt.updated_at) }}</span>
        </div>
      </div>

      <!-- 引用格式說明 -->
      <div class="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100 text-xs text-blue-700">
        <p class="font-medium mb-1">引用格式</p>
        <p class="font-mono">
          {{ exampleCitation }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

type BookProject = { id: string; name: string; type: string };
type ExcerptBookProject = { book_project_id: string; book_projects: BookProject };
type Book = {
  id: string;
  title: string;
  author: string;
  translator: string | null;
  publish_place: string | null;
  publisher: string | null;
  publish_year: number | null;
  edition: string | null;
};
type ExcerptDetail = {
  id: string;
  title: string | null;
  content: string;
  chapter: string | null;
  page_number: string | null;
  created_at: string;
  updated_at: string;
  books: Book | null;
  excerpt_book_projects: ExcerptBookProject[];
};

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();

const loading = ref(true);
const excerpt = ref<ExcerptDetail | null>(null);
const contentEl = ref<HTMLElement | null>(null);
const copyToastVisible = ref(false);
let toastTimer: ReturnType<typeof setTimeout>;

// 將 content 依 \n---\n 切分為多個頁面段落
const contentSections = computed(() => {
  if (!excerpt.value?.content) return [];
  return excerpt.value.content.split(/\n---\n|\n-{3,}\n/);
});

type RenderLine = { html: string; className: string };

function renderSection(section: string): RenderLine[] {
  return section
    .split(/\r?\n/)
    .map((raw) => raw ?? "")
    .map((line) => renderLine(line));
}

function renderLine(rawLine: string): RenderLine {
  const t = rawLine.trim();
  if (!t) return { html: "&nbsp;", className: "text-gray-700 leading-relaxed min-h-[1.2em]" };

  // Quote block: > 引用文字
  if (/^>\s+/.test(t)) {
    const body = t.replace(/^>\s+/, "");
    return {
      html: formatInline(body),
      className: "text-gray-700 italic leading-relaxed text-[1.03rem] border-l-4 border-gray-300 pl-3 py-1 bg-gray-50 rounded-r",
    };
  }

  // Bullet list
  if (/^[-*•]\s+/.test(t)) {
    const body = t.replace(/^[-*•]\s+/, "");
    return {
      html: `• ${formatInline(body)}`,
      className: "text-gray-700 leading-relaxed text-[1.05rem] pl-4",
    };
  }

  // Number list
  const num = t.match(/^(\d+)[.)、]\s+(.*)$/);
  if (num) {
    return {
      html: `${num[1]}. ${formatInline(num[2])}`,
      className: "text-gray-700 leading-relaxed text-[1.05rem] pl-4",
    };
  }

  // Heading line: no first-line indent
  if (isHeadingLine(t)) {
    return {
      html: formatInline(t),
      className: "text-gray-900 font-semibold leading-relaxed text-[1.06rem] mt-1",
    };
  }

  // Normal paragraph: first line indent 2 chars
  return {
    html: formatInline(t),
    className: "text-gray-700 leading-relaxed text-[1.05rem] [text-indent:2em]",
  };
}

function isHeadingLine(t: string): boolean {
  if (/^第[一二三四五六七八九十百千0-9]+[章節回部卷篇]/.test(t)) return true;
  if (/^[一二三四五六七八九十]+[、.．]/.test(t)) return true;
  if (/^[（(][一二三四五六七八九十0-9]+[)）]/.test(t)) return true;
  if (/^#{1,6}\s+/.test(t)) return true;
  if ((t.endsWith("：") || t.endsWith(":")) && t.length <= 30) return true;
  return false;
}

function formatInline(text: string): string {
  let s = escapeHtml(text);
  // **bold**
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  // *italic*
  s = s.replace(/(^|[^*])\*(?!\s)(.+?)(?<!\s)\*(?!\*)/g, "$1<em>$2</em>");
  // [kai]標楷體[/kai]
  s = s.replace(
    /\[kai\]([\s\S]+?)\[\/kai\]/gi,
    "<span style=\"font-family:'DFKai-SB','BiauKai',serif;\">$1</span>"
  );
  return s;
}

function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

// 起始頁碼（預設 1）
const startPage = computed(() => {
  const n = parseInt(excerpt.value?.page_number ?? "");
  return isNaN(n) ? null : n;
});

function pageForSection(index: number): string {
  if (startPage.value === null) return "?";
  return String(startPage.value + index);
}

// 組合 Chicago 格式引用
// 格式（中文學術慣用）：
//   作者，《書名》（出版地：出版社，年份），頁碼。
//   若有譯者：作者著，譯者譯，《書名》（出版地：出版社，年份），頁碼。
//   若有版次：…，年份，版次），頁碼。
function buildChicagoCitation(book: Book, pageNum: string, chapter?: string | null): string {
  if (!book) return "";

  // 作者段
  const authorPart = book.translator
    ? `${book.author}著，${book.translator}譯`
    : book.author;

  // 書名
  const titlePart = `《${book.title}》`;

  // 出版資訊段（括號內）
  const pubParts: string[] = [];
  if (book.publish_place) pubParts.push(book.publish_place);
  if (book.publisher) pubParts.push(book.publisher);
  if (book.publish_year) pubParts.push(`${book.publish_year}`);
  if (book.edition) pubParts.push(book.edition);
  const pubInfo = pubParts.length
    ? `（${pubParts.slice(0, 2).join("：")}${pubParts.length >= 3 ? "，" + pubParts.slice(2).join("，") : ""}）`
    : "";

  // 章節
  const chapterPart = chapter ? `，〈${chapter}〉` : "";

  // 頁碼
  const pagePart = pageNum !== "?" ? `，頁 ${pageNum}` : "";

  return `${authorPart}${chapterPart}，${titlePart}${pubInfo}${pagePart}。`;
}

// 底部顯示的引用範例
const exampleCitation = computed(() => {
  const book = excerpt.value?.books;
  const chapter = excerpt.value?.chapter;
  if (!book) return "作者，《書名》（出版地：出版社，年份），頁碼。";
  const page = pageForSection(0);
  return buildChicagoCitation(book, page, chapter);
});

// 攔截複製事件，自動附加 Chicago 完整引用
function handleCopy(e: ClipboardEvent) {
  const selection = window.getSelection();
  const selectedText = selection?.toString() ?? "";
  if (!selectedText.trim()) return;

  // 找出選取起始點所在的 [data-page] 區塊
  const anchorNode = selection?.anchorNode;
  const pageEl =
    anchorNode instanceof Element
      ? anchorNode.closest("[data-page]")
      : anchorNode?.parentElement?.closest("[data-page]");

  const pageNum = pageEl?.getAttribute("data-page") ?? pageForSection(0);

  const book = excerpt.value?.books;
  const chapter = excerpt.value?.chapter;
  const citation = book
    ? `\n\n${buildChicagoCitation(book, pageNum, chapter)}`
    : "";

  e.clipboardData?.setData("text/plain", selectedText + citation);

  // 顯示 toast
  clearTimeout(toastTimer);
  copyToastVisible.value = true;
  toastTimer = setTimeout(() => (copyToastVisible.value = false), 2000);
}

async function fetchExcerpt() {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) {
    router.push("/login");
    return;
  }

  const data = await $fetch<ExcerptDetail>(`/api/excerpts/${route.params.id}`, {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => null);

  excerpt.value = data;
  loading.value = false;
}

function projectTagClass(type?: string) {
  const map: Record<string, string> = {
    書摘: "bg-blue-50 text-blue-700",
    待寫文章: "bg-amber-50 text-amber-700",
    待寫著作: "bg-purple-50 text-purple-700",
  };
  return map[type ?? ""] ?? "bg-gray-100 text-gray-600";
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("zh-TW", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

onMounted(fetchExcerpt);

useHead({
  title: computed(() =>
    excerpt.value?.title ? `${excerpt.value.title} - 書摘庫` : "書摘詳細 - Know Graph Lab"
  ),
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
