<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>書摘庫</span>
            </NuxtLink>
            <span>›</span>
            <span class="font-semibold text-blue-700">書摘圖書館</span>
          </div>
          <div class="flex items-center gap-2">
            <button @click="showCreateBook = true" class="text-xs px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition">+ 新增書籍</button>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 標題 -->
      <div class="flex items-center gap-4 mb-8">
        <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl">📚</div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">書摘圖書館</h1>
          <p class="text-sm text-gray-500 mt-0.5">按分類瀏覽藏書，查閱書中摘文</p>
        </div>
      </div>

      <!-- 搜尋列 -->
      <div class="relative mb-6">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input v-model="bookSearch" type="text" placeholder="搜尋書名或作者…"
          class="w-full pl-12 pr-10 py-3 bg-white border border-gray-200 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
        <button v-if="bookSearch" @click="bookSearch = ''" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">✕</button>
      </div>

      <!-- 搜尋結果 -->
      <template v-if="bookSearch.trim()">
        <p class="text-sm text-gray-500 mb-4">搜尋「{{ bookSearch }}」：共 {{ filteredBooks.length }} 本</p>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <NuxtLink v-for="book in filteredBooks" :key="book.id" :to="`/excerpts/library/${book.id}`"
            class="group bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-300 hover:shadow-md transition-all">
            <BookCard :book="book" />
          </NuxtLink>
        </div>
        <p v-if="filteredBooks.length === 0" class="text-center py-12 text-gray-400">找不到符合的書籍</p>
      </template>

      <!-- 分類瀏覽 -->
      <template v-else>
        <div v-if="catsLoading" class="flex flex-wrap gap-3 mb-6">
          <div v-for="i in 8" :key="i" class="h-9 w-24 bg-white rounded-xl border border-gray-200 animate-pulse"></div>
        </div>

        <!-- 頂層分類 -->
        <div v-else class="flex flex-wrap gap-2 mb-5">
          <button @click="selectTopCat(null)"
            :class="['px-4 py-2 rounded-xl text-sm font-medium border transition',
              !selectedTopCat ? 'bg-blue-600 text-white border-blue-600 shadow' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-700']">
            全部（{{ allBooks.length }}）
          </button>
          <button v-for="cat in categoryTree" :key="cat.id" @click="selectTopCat(cat)"
            :class="['px-4 py-2 rounded-xl text-sm font-medium border transition',
              selectedTopCat?.id === cat.id ? 'bg-blue-600 text-white border-blue-600 shadow' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-700']">
            {{ cat.name }}
            <span class="ml-1 text-xs opacity-70">({{ totalBooks(cat) }})</span>
          </button>
        </div>

        <!-- 子分類 -->
        <div v-if="selectedTopCat?.children?.length" class="flex flex-wrap gap-2 mb-5 pl-2 border-l-2 border-blue-200">
          <button @click="selectedSubCat = null; loadBooks(selectedTopCat?.id)"
            :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition',
              !selectedSubCat ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-white text-gray-500 border-gray-200 hover:border-blue-200']">
            全部 {{ selectedTopCat.name }}
          </button>
          <button v-for="sub in selectedTopCat.children" :key="sub.id" @click="selectSubCat(sub)"
            :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition',
              selectedSubCat?.id === sub.id ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-white text-gray-500 border-gray-200 hover:border-blue-200']">
            {{ sub.name }} ({{ sub.book_count }})
          </button>
        </div>

        <!-- 書籍格 -->
        <div v-if="booksLoading" class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div v-for="i in 8" :key="i" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse h-24"></div>
        </div>
        <template v-else>
          <p class="text-sm text-gray-500 mb-4">
            {{ selectedSubCat?.name ?? selectedTopCat?.name ?? '全部' }} ・共 {{ displayedBooks.length }} 本
          </p>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <NuxtLink v-for="book in displayedBooks" :key="book.id" :to="`/excerpts/library/${book.id}`"
              class="group bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-300 hover:shadow-md transition-all">
              <BookCard :book="book" />
            </NuxtLink>
          </div>
          <p v-if="displayedBooks.length === 0" class="text-center py-12 text-gray-400">此分類尚無書籍</p>
        </template>
      </template>
    </div>

    <div v-if="showCreateBook" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold text-gray-900 mb-3">新增書籍</h3>
        <input v-model="newBook.title" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" placeholder="書名（必填）" />
        <input v-model="newBook.author" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" placeholder="作者" />
        <input v-model="newBook.publisher" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" placeholder="出版社" />
        <input v-model.number="newBook.publish_year" type="number" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-3" placeholder="出版年份" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCreateBook=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg" @click="createBook">建立</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
const supabase = useSupabaseClient();
const router = useRouter();

interface Category { id: string; name: string; parent_id: string | null; book_count: number; children: Category[] }

const catsLoading = ref(true);
const booksLoading = ref(false);
const categoryTree = ref<Category[]>([]);
const allBooks = ref<any[]>([]);
const displayedBooks = ref<any[]>([]);
const bookSearch = ref("");
const selectedTopCat = ref<Category | null>(null);
const selectedSubCat = ref<Category | null>(null);
const showCreateBook = ref(false);
const newBook = ref<{ title: string; author: string; publisher: string; publish_year: number | null }>({
  title: "", author: "", publisher: "", publish_year: null,
});

const filteredBooks = computed(() => {
  const q = bookSearch.value.trim().toLowerCase();
  if (!q) return allBooks.value;
  return allBooks.value.filter(b => b.title?.toLowerCase().includes(q) || b.author?.toLowerCase().includes(q));
});

function totalBooks(cat: Category): number {
  return cat.book_count + (cat.children ?? []).reduce((s, c) => s + c.book_count, 0);
}

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

async function fetchCategories() {
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

async function handleLogout() { await supabase.auth.signOut(); router.push("/login"); }
async function createBook() {
  if (!newBook.value.title.trim()) return;
  const token = await getToken(); if (!token) return;
  const created = await $fetch<any>("/api/books", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: newBook.value,
  }).catch(() => null);
  if (!created) return;
  showCreateBook.value = false;
  newBook.value = { title: "", author: "", publisher: "", publish_year: null };
  await Promise.all([fetchAllBooks(), loadBooks(selectedSubCat.value?.id || selectedTopCat.value?.id)]);
}

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchAllBooks()]);
  displayedBooks.value = allBooks.value;
});
useHead({ title: "書摘圖書館 — 書摘庫" });
</script>
