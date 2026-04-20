<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition">書摘庫</NuxtLink>
            <span>›</span>
            <NuxtLink to="/excerpts?tab=書摘" class="hover:text-blue-600 transition">圖書館</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900 truncate max-w-xs">{{ book?.title ?? '載入中…' }}</span>
          </div>
          <button @click="handleLogout" class="text-gray-600 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 載入中 -->
      <div v-if="loading" class="space-y-4">
        <div class="bg-white rounded-2xl border border-gray-200 p-8 animate-pulse">
          <div class="h-8 bg-gray-200 rounded w-1/2 mb-3"></div>
          <div class="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>

      <div v-else-if="book">
        <!-- 書籍資訊卡 -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 mb-8 shadow-sm">
          <div class="flex items-start gap-5">
            <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0">📚</div>
            <div class="flex-1">
              <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ book.title }}</h1>
              <p class="text-gray-600 mb-3">{{ book.author }}</p>

              <!-- 書籍詳細資訊（供查詢）-->
              <div class="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-500">
                <span v-if="book.translator">譯者：{{ book.translator }}</span>
                <span v-if="book.publisher">出版社：{{ book.publisher }}</span>
                <span v-if="book.publish_place">出版地：{{ book.publish_place }}</span>
                <span v-if="book.publish_year">出版年：{{ book.publish_year }}</span>
                <span v-if="book.edition">版次：{{ book.edition }}</span>
              </div>

              <div class="mt-4 flex items-center gap-4">
                <span class="text-sm font-medium text-blue-600">{{ book.excerpts?.length ?? 0 }} 筆摘文</span>
                <span class="text-sm text-gray-400">·</span>
                <span class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">書摘</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 摘文列表 -->
        <h2 class="text-lg font-semibold text-gray-800 mb-4">所有摘文</h2>
        <div v-if="book.excerpts?.length === 0" class="text-center py-12 text-gray-400">
          <p>此書尚無摘文</p>
        </div>
        <div v-else class="space-y-3">
          <NuxtLink
            v-for="excerpt in book.excerpts" :key="excerpt.id"
            :to="`/excerpts/${excerpt.id}`"
            class="group block bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-300 hover:shadow-md transition-all duration-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1.5 flex-wrap">
                  <h3 class="font-semibold text-gray-900 group-hover:text-blue-700 transition text-sm">
                    {{ excerpt.title ?? '（無標題）' }}
                  </h3>
                  <span v-if="excerpt.chapter" class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">{{ excerpt.chapter }}</span>
                  <span v-if="excerpt.page_number" class="text-xs text-gray-400">p.{{ excerpt.page_number }}</span>
                </div>
                <p class="text-sm text-gray-600 line-clamp-2 leading-relaxed">{{ excerpt.content }}</p>
              </div>
              <svg class="w-4 h-4 text-gray-300 group-hover:text-blue-400 transition flex-shrink-0 ml-3 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </NuxtLink>
        </div>
      </div>

      <div v-else class="text-center py-20 text-gray-400">找不到此書</div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const bookId = route.params.bookId as string;

type Book = {
  id: string; title: string; author: string;
  translator?: string; publish_place?: string; publisher?: string;
  publish_year?: number; edition?: string;
  excerpts: { id: string; title: string | null; content: string; chapter: string | null; page_number: string | null }[];
};

const loading = ref(true);
const book = ref<Book | null>(null);

async function fetchBook() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return; }
  book.value = await $fetch<Book>(`/api/books/${bookId}`, {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => null);
  loading.value = false;
}

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(fetchBook);
useHead({ title: computed(() => book.value ? `${book.value.title} - 書摘` : "書摘") });
</script>
