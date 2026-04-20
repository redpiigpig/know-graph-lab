<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <img src="/images/logo-icon.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold text-gray-900">Know Graph Lab</span>
          </div>
          <div class="flex items-center space-x-6">
            <NuxtLink to="/settings" class="text-gray-600 hover:text-blue-600 transition text-sm">API Keys</NuxtLink>
            <NuxtLink to="/" class="text-gray-600 hover:text-blue-600 transition text-sm">首頁</NuxtLink>
            <button @click="handleLogout" class="text-gray-600 hover:text-red-600 transition text-sm">登出</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 頁首 -->
      <div class="mb-6 flex items-end justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">書摘庫</h1>
          <p class="text-gray-500 mt-1">管理你的書摘與寫作素材</p>
        </div>
      </div>

      <!-- Tab 列 -->
      <div class="flex space-x-1 mb-8 bg-white border border-gray-200 rounded-xl p-1 w-fit shadow-sm">
        <button
          v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'px-5 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2',
            activeTab === tab.key ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          ]"
        >
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- ===== 待寫著作 ===== -->
      <div v-if="activeTab === '待寫著作'">
        <div v-if="writingLoading" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="i in 2" :key="i" class="bg-white rounded-2xl border border-gray-200 p-6 animate-pulse">
            <div class="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div class="space-y-2"><div class="h-4 bg-gray-200 rounded w-full"></div><div class="h-4 bg-gray-200 rounded w-3/4"></div></div>
          </div>
        </div>
        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 千面上帝 書卡 -->
          <NuxtLink
            v-if="writingOverview"
            to="/excerpts/writing"
            class="group bg-white rounded-2xl border border-gray-200 p-6 hover:border-purple-300 hover:shadow-lg transition-all duration-200 flex flex-col"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl">📖</div>
              <span class="text-xs bg-purple-50 text-purple-600 font-medium px-2 py-1 rounded-full">待寫著作</span>
            </div>
            <h2 class="text-xl font-bold text-gray-900 mb-2 group-hover:text-purple-700 transition">
              {{ writingOverview.title }}
            </h2>
            <p class="text-sm text-gray-500 mb-4">{{ writingOverview.total }} 筆素材 · {{ writingOverview.chapters.length }} 個章節</p>
            <!-- 章節預覽 -->
            <div class="flex flex-wrap gap-1.5 mt-auto">
              <span
                v-for="ch in writingOverview.chapters.slice(0, 6)" :key="ch.name"
                class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
              >{{ ch.name }} ({{ ch.count }})</span>
              <span v-if="writingOverview.chapters.length > 6" class="text-xs text-gray-400">+{{ writingOverview.chapters.length - 6 }} 章</span>
            </div>
          </NuxtLink>

          <!-- 空狀態 -->
          <div v-if="!writingOverview" class="col-span-3 text-center py-20 text-gray-400">
            <p class="text-lg">尚無待寫著作素材</p>
          </div>
        </div>
      </div>

      <!-- ===== 書摘（圖書館）===== -->
      <div v-else-if="activeTab === '書摘'">

        <!-- 搜尋列 -->
        <div class="relative mb-6">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input v-model="bookSearch" type="text" placeholder="搜尋書名或作者…（搜尋時顯示全部結果）"
            class="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
          <button v-if="bookSearch" @click="bookSearch = ''" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <!-- 搜尋結果模式 -->
        <template v-if="bookSearch.trim()">
          <p class="text-sm text-gray-500 mb-4">搜尋「{{ bookSearch }}」：共 {{ filteredBooks.length }} 本</p>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <NuxtLink v-for="book in filteredBooks" :key="book.id" :to="`/excerpts/source/${book.id}`"
              class="group bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-300 hover:shadow-md transition-all">
              <BookCard :book="book" />
            </NuxtLink>
          </div>
          <p v-if="filteredBooks.length === 0" class="text-center py-12 text-gray-400">找不到符合的書籍</p>
        </template>

        <!-- 分類瀏覽模式 -->
        <template v-else>
          <div v-if="catsLoading" class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-3 mb-6">
            <div v-for="i in 9" :key="i" class="h-20 bg-white rounded-xl border border-gray-200 animate-pulse"></div>
          </div>

          <!-- 頂層分類橫向捲動列 -->
          <div v-else class="flex flex-wrap gap-2 mb-6">
            <button
              @click="selectTopCat(null)"
              :class="[
                'px-4 py-2 rounded-xl text-sm font-medium border transition',
                !selectedTopCat ? 'bg-blue-600 text-white border-blue-600 shadow' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-700'
              ]"
            >全部（{{ allBooks.length }}）</button>
            <button
              v-for="cat in categoryTree" :key="cat.id"
              @click="selectTopCat(cat)"
              :class="[
                'px-4 py-2 rounded-xl text-sm font-medium border transition',
                selectedTopCat?.id === cat.id ? 'bg-blue-600 text-white border-blue-600 shadow' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-700'
              ]"
            >
              {{ cat.name }}
              <span class="ml-1 text-xs opacity-70">({{ totalBooks(cat) }})</span>
            </button>
          </div>

          <!-- 子分類（若有） -->
          <div v-if="selectedTopCat && selectedTopCat.children.length > 0" class="flex flex-wrap gap-2 mb-6 pl-1 border-l-2 border-blue-200">
            <button
              @click="selectedSubCat = null; loadBooks(selectedTopCat?.id)"
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium border transition',
                !selectedSubCat ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-white text-gray-500 border-gray-200 hover:border-blue-200'
              ]"
            >全部 {{ selectedTopCat.name }}</button>
            <button
              v-for="sub in selectedTopCat.children" :key="sub.id"
              @click="selectSubCat(sub)"
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium border transition',
                selectedSubCat?.id === sub.id ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-white text-gray-500 border-gray-200 hover:border-blue-200'
              ]"
            >{{ sub.name }} ({{ sub.book_count }})</button>
          </div>

          <!-- 書籍格 -->
          <div v-if="booksLoading" class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div v-for="i in 8" :key="i" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse h-24"></div>
          </div>
          <template v-else>
            <p class="text-sm text-gray-500 mb-4">
              {{ selectedSubCat ? selectedSubCat.name : (selectedTopCat ? selectedTopCat.name : '全部') }}
              ・共 {{ displayedBooks.length }} 本
            </p>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <NuxtLink v-for="book in displayedBooks" :key="book.id" :to="`/excerpts/source/${book.id}`"
                class="group bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-300 hover:shadow-md transition-all">
                <BookCard :book="book" />
              </NuxtLink>
            </div>
            <p v-if="displayedBooks.length === 0" class="text-center py-12 text-gray-400">此分類尚無書籍</p>
          </template>
        </template>
      </div>

      <!-- ===== 待寫文章 ===== -->
      <div v-else-if="activeTab === '待寫文章'" class="text-center py-20 text-gray-400">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <p class="text-lg font-medium text-gray-500">尚無待寫文章素材</p>
        <p class="text-sm text-gray-400 mt-1">日後可在此管理文章寫作素材</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();

// ── Auth helper ──
async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

const activeTab = ref("待寫著作");
const tabs = [
  { key: "待寫著作", label: "📖 待寫著作" },
  { key: "書摘",   label: "📚 書摘圖書館" },
  { key: "待寫文章", label: "✍️ 待寫文章" },
];

// ── 待寫著作 ──
const writingLoading = ref(false);
const writingOverview = ref<{ title: string; total: number; chapters: { name: string; count: number }[] } | null>(null);

async function fetchWritingOverview() {
  writingLoading.value = true;
  const token = await getToken(); if (!token) return;
  writingOverview.value = await $fetch("/api/writing/overview", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null) as any;
  writingLoading.value = false;
}

// ── 書摘圖書館 ──
interface Category { id: string; name: string; parent_id: string | null; book_count: number; children: Category[] }
const catsLoading = ref(false);
const booksLoading = ref(false);
const categoryTree = ref<Category[]>([]);
const allBooks = ref<any[]>([]);       // ALL books (for search)
const displayedBooks = ref<any[]>([]);  // books in selected category
const bookSearch = ref("");
const selectedTopCat = ref<Category | null>(null);
const selectedSubCat = ref<Category | null>(null);

const filteredBooks = computed(() => {
  if (!bookSearch.value.trim()) return allBooks.value;
  const q = bookSearch.value.trim().toLowerCase();
  return allBooks.value.filter(
    (b) => b.title?.toLowerCase().includes(q) || b.author?.toLowerCase().includes(q)
  );
});

function totalBooks(cat: Category): number {
  return cat.book_count + cat.children.reduce((s, c) => s + c.book_count, 0);
}

async function fetchCategories() {
  catsLoading.value = true;
  const token = await getToken(); if (!token) return;
  categoryTree.value = await $fetch<Category[]>("/api/books/categories", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  catsLoading.value = false;
}

async function loadBooks(catId?: string) {
  booksLoading.value = true;
  const token = await getToken(); if (!token) return;
  displayedBooks.value = await $fetch<any[]>("/api/books" + (catId ? `?categoryId=${catId}` : ""), {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  booksLoading.value = false;
}

async function fetchAllBooks() {
  const token = await getToken(); if (!token) return;
  allBooks.value = await $fetch<any[]>("/api/books", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
}

function selectTopCat(cat: Category | null) {
  selectedTopCat.value = cat;
  selectedSubCat.value = null;
  loadBooks(cat?.id);
}
function selectSubCat(sub: Category) {
  selectedSubCat.value = sub;
  loadBooks(sub.id);
}

async function initLibrary() {
  await Promise.all([fetchCategories(), fetchAllBooks()]);
  displayedBooks.value = allBooks.value;
}

// ── Tab 切換載入 ──
watch(activeTab, async (tab) => {
  if (tab === "待寫著作" && !writingOverview.value) await fetchWritingOverview();
  if (tab === "書摘" && allBooks.value.length === 0) await initLibrary();
});

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(fetchWritingOverview);
useHead({ title: "書摘庫 - Know Graph Lab" });
</script>
