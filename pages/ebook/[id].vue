<template>
  <div class="min-h-screen bg-gray-950 text-white flex flex-col">
    <!-- 頂部導航 -->
    <nav class="border-b border-gray-800 bg-gray-950/90 backdrop-blur sticky top-0 z-50 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink to="/ebook" class="text-gray-400 hover:text-white text-sm transition flex-shrink-0">← 書架</NuxtLink>
          <span class="text-gray-600">·</span>
          <span class="text-sm font-medium text-white truncate">{{ ebook?.title }}</span>
        </div>

        <!-- 頁碼控制 -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-30 transition text-sm">‹</button>
          <div class="flex items-center gap-1">
            <input v-model.number="jumpPage" @keyup.enter="goPage(jumpPage)" type="number" :min="1" :max="ebook?.total_pages ?? 1"
              class="w-14 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-center text-sm focus:outline-none focus:border-blue-500" />
            <span class="text-xs text-gray-500">/ {{ ebook?.total_pages }}</span>
          </div>
          <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-30 transition text-sm">›</button>
        </div>

        <!-- 頁內搜尋 -->
        <div class="hidden sm:flex items-center gap-2">
          <input v-model="pageSearch" type="text" placeholder="頁內搜尋…"
            class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm w-36 focus:outline-none focus:border-blue-500" />
        </div>

        <!-- 建立摘文 -->
        <button @click="createExcerptFromSelection" title="將選取文字建立摘文"
          class="flex-shrink-0 px-3 py-1.5 bg-blue-700 hover:bg-blue-600 rounded-lg text-xs font-medium transition">
          + 建摘文
        </button>
      </div>
    </nav>

    <!-- 主體：閱讀區 -->
    <div class="flex flex-1 overflow-hidden">

      <!-- 側欄：縮圖/章節 -->
      <div class="w-48 border-r border-gray-800 overflow-y-auto flex-shrink-0 hidden lg:block">
        <div class="p-3 space-y-1">
          <button v-for="p in quickPages" :key="p"
            @click="goPage(p)"
            :class="['w-full text-left px-3 py-2 rounded-lg text-xs transition',
              p === currentPage ? 'bg-blue-900 text-blue-300' : 'text-gray-400 hover:bg-gray-800']">
            第 {{ p }} 頁
          </button>
        </div>
      </div>

      <!-- 閱讀主區 -->
      <div class="flex-1 overflow-y-auto p-8">
        <div v-if="pageLoading" class="max-w-2xl mx-auto space-y-3 animate-pulse">
          <div v-for="i in 8" :key="i" :class="['h-4 bg-gray-800 rounded', i % 3 === 0 ? 'w-3/4' : 'w-full']"></div>
        </div>

        <div v-else-if="pageContent" class="max-w-2xl mx-auto">
          <div class="text-xs text-gray-600 mb-6 flex items-center gap-2">
            <span>第 {{ currentPage }} 頁</span>
            <span>·</span>
            <span>{{ ebook?.title }}</span>
          </div>

          <div
            ref="contentEl"
            class="text-gray-200 leading-8 text-[15px] whitespace-pre-wrap selection:bg-blue-900"
            v-html="highlightedContent"
          ></div>

          <!-- 翻頁 -->
          <div class="flex justify-between mt-12 pt-6 border-t border-gray-800">
            <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
              class="px-5 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 rounded-lg text-sm transition">← 上一頁</button>
            <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
              class="px-5 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 rounded-lg text-sm transition">下一頁 →</button>
          </div>
        </div>

        <div v-else class="text-center py-20 text-gray-500">此頁無內容</div>
      </div>
    </div>

    <!-- 建立摘文 Modal -->
    <div v-if="showExcerptModal" class="fixed inset-0 bg-black/70 flex items-end sm:items-center justify-center z-50 p-4">
      <div class="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-lg space-y-4">
        <h3 class="font-semibold">建立摘文</h3>
        <textarea v-model="excerptContent" rows="5"
          class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white resize-none focus:outline-none focus:border-blue-500" />
        <input v-model="excerptTitle" placeholder="摘文標題（選填）"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500" />
        <div class="flex gap-3">
          <button @click="saveExcerpt" :disabled="savingExcerpt || !excerptContent.trim()"
            class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-xl text-sm font-medium transition">
            {{ savingExcerpt ? '儲存中…' : '儲存摘文' }}
          </button>
          <button @click="showExcerptModal = false" class="px-4 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-sm transition">取消</button>
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
const ebookId = route.params.id as string;

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

const ebook = ref<any>(null);
const currentPage = ref(parseInt(route.query.page as string ?? "1") || 1);
const jumpPage = ref(currentPage.value);
const pageContent = ref("");
const pageLoading = ref(false);
const pageSearch = ref("");
const contentEl = ref<HTMLDivElement | null>(null);

const highlightedContent = computed(() => {
  if (!pageSearch.value.trim()) return pageContent.value;
  const escaped = pageSearch.value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return pageContent.value.replace(
    new RegExp(escaped, "gi"),
    (m) => `<mark class="bg-yellow-400 text-gray-900 rounded px-0.5">${m}</mark>`
  );
});

const quickPages = computed(() => {
  if (!ebook.value?.total_pages) return [];
  const total = ebook.value.total_pages;
  const pages: number[] = [];
  for (let p = Math.max(1, currentPage.value - 5); p <= Math.min(total, currentPage.value + 20); p++) {
    pages.push(p);
  }
  return pages;
});

async function loadPage(page: number) {
  pageLoading.value = true;
  const token = await getToken(); if (!token) return;
  const data = await $fetch<any>(`/api/ebooks/${ebookId}?page=${page}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);

  if (!ebook.value && data) ebook.value = data;
  pageContent.value = data?.currentPage?.content ?? "";
  pageLoading.value = false;
  jumpPage.value = page;
}

function goPage(p: number) {
  if (!ebook.value) return;
  const clamped = Math.max(1, Math.min(p, ebook.value.total_pages));
  currentPage.value = clamped;
  router.replace({ query: { page: String(clamped) } });
  loadPage(clamped);
}

// ── 建立摘文 ──
const showExcerptModal = ref(false);
const excerptContent = ref("");
const excerptTitle = ref("");
const savingExcerpt = ref(false);

function createExcerptFromSelection() {
  const selection = window.getSelection()?.toString().trim();
  excerptContent.value = selection || pageContent.value.slice(0, 500);
  excerptTitle.value = "";
  showExcerptModal.value = true;
}

async function saveExcerpt() {
  savingExcerpt.value = true;
  const token = await getToken(); if (!token) return;
  const bookId = ebook.value?.book_id ?? null;

  await $fetch("/api/excerpts", {
    method: "POST",
    body: {
      content: excerptContent.value,
      title: excerptTitle.value || null,
      book_id: bookId,
      page_number: String(currentPage.value),
    },
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);

  showExcerptModal.value = false;
  savingExcerpt.value = false;
}

onMounted(() => loadPage(currentPage.value));
useHead({ title: computed(() => ebook.value ? `${ebook.value.title} — 閱讀` : "閱讀") });
</script>
