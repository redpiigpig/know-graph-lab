<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition">書摘庫</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900">千面上帝</span>
          </div>
          <button @click="handleLogout" class="text-gray-600 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 書名標題 -->
      <div class="mb-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl">📖</div>
          <div>
            <h1 class="text-3xl font-bold text-gray-900">千面上帝</h1>
            <p class="text-gray-500 text-sm mt-0.5">待寫著作 · {{ overview?.total ?? 0 }} 筆素材</p>
          </div>
        </div>
      </div>

      <!-- 章節 Tab 列 -->
      <div v-if="overview" class="flex flex-wrap gap-2 mb-8">
        <button
          v-for="ch in overview.chapters" :key="ch.name"
          @click="selectChapter(ch.name)"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition border',
            activeChapter === ch.name
              ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
              : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:text-purple-700'
          ]"
        >
          {{ ch.name }}
          <span :class="activeChapter === ch.name ? 'text-purple-200' : 'text-gray-400'" class="ml-1 text-xs">({{ ch.count }})</span>
        </button>
      </div>

      <!-- 章節內容 -->
      <div v-if="chapLoading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
          <div class="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
          <div class="space-y-2"><div class="h-3 bg-gray-200 rounded w-full"></div><div class="h-3 bg-gray-200 rounded w-4/5"></div></div>
        </div>
      </div>

      <div v-else-if="excerpts.length === 0 && activeChapter" class="text-center py-20 text-gray-400">
        <p>此章節尚無摘文</p>
      </div>

      <div v-else class="space-y-3">
        <!-- 章節名稱大標題 -->
        <div v-if="activeChapter" class="flex items-center gap-3 mb-4">
          <h2 class="text-2xl font-bold text-gray-900">{{ activeChapter }}</h2>
          <span class="text-gray-400 text-sm">{{ excerpts.length }} 筆</span>
        </div>

        <NuxtLink
          v-for="excerpt in excerpts" :key="excerpt.id"
          :to="`/excerpts/${excerpt.id}`"
          class="group block bg-white rounded-xl border border-gray-200 p-5 hover:border-purple-300 hover:shadow-md transition-all duration-200"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <!-- 主題標題（第一行）-->
              <h3 class="font-semibold text-gray-900 mb-2 group-hover:text-purple-700 transition text-base">
                {{ excerpt.title ?? '（無標題）' }}
              </h3>
              <!-- 書籍來源 -->
              <p class="text-xs text-blue-600 mb-2">
                {{ excerpt.books?.title ?? '' }}
                <span v-if="excerpt.books?.author" class="text-gray-400"> · {{ excerpt.books.author }}</span>
                <span v-if="excerpt.page_number" class="text-gray-400"> · p.{{ excerpt.page_number }}</span>
              </p>
              <!-- 內文預覽 -->
              <p class="text-sm text-gray-600 line-clamp-3 leading-relaxed">{{ excerpt.content }}</p>
            </div>
            <svg class="w-4 h-4 text-gray-300 group-hover:text-purple-400 transition flex-shrink-0 ml-3 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();

type ChapterInfo = { name: string; count: number };
type Overview = { title: string; total: number; chapters: ChapterInfo[] };
type Excerpt = {
  id: string; title: string | null; content: string;
  chapter: string | null; page_number: string | null;
  books: { id: string; title: string; author: string } | null;
};

const overview = ref<Overview | null>(null);
const activeChapter = ref<string | null>(null);
const excerpts = ref<Excerpt[]>([]);
const chapLoading = ref(false);

async function getSession() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session;
}

async function fetchOverview() {
  const session = await getSession(); if (!session) return;
  overview.value = await $fetch<Overview>("/api/writing/overview", {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => null);
  if (overview.value?.chapters?.[0]) {
    selectChapter(overview.value.chapters[0].name);
  }
}

async function selectChapter(name: string) {
  const session = await getSession(); if (!session) return;
  activeChapter.value = name;
  chapLoading.value = true;
  const data = await $fetch<Excerpt[]>(`/api/excerpts?type=待寫著作&chapter=${encodeURIComponent(name)}`, {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => []);
  excerpts.value = data as Excerpt[];
  chapLoading.value = false;
}

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(fetchOverview);
useHead({ title: "千面上帝 - Know Graph Lab" });
</script>
