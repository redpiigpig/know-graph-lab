<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition">書摘庫</NuxtLink>
            <span>›</span>
            <NuxtLink to="/excerpts/article" class="hover:text-green-600 transition">待寫文章</NuxtLink>
            <span>›</span>
            <span class="font-semibold text-gray-900 truncate max-w-xs">{{ overview?.project?.name ?? '載入中…' }}</span>
          </div>
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div v-if="loading" class="space-y-6 animate-pulse">
        <div class="bg-white rounded-2xl p-6 h-24"></div>
        <div class="space-y-3">
          <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-200 p-5 h-28"></div>
        </div>
      </div>

      <template v-else-if="overview">
        <!-- 文章項目標題 -->
        <div class="mb-8 flex items-center gap-4">
          <div class="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0">✍️</div>
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ overview.project.name }}</h1>
            <p class="text-gray-500 text-sm mt-0.5">待寫文章 · {{ overview.total }} 筆素材</p>
            <p v-if="overview.project.description" class="text-gray-400 text-sm mt-1">{{ overview.project.description }}</p>
          </div>
        </div>

        <!-- 篩選工具列：依來源書或搜尋 -->
        <div class="flex flex-wrap gap-3 mb-6">
          <div class="relative flex-1 min-w-48 max-w-xs">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input v-model="searchQ" type="text" placeholder="搜尋摘文內容…"
              class="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-green-400 transition" />
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-if="!filteredExcerpts.length" class="text-center py-16 text-gray-400">
          <p>{{ searchQ ? '找不到符合的摘文' : '此文章尚無摘文素材' }}</p>
        </div>

        <!-- 摘文列表（依來源書分組） -->
        <div v-else>
          <template v-for="group in groupedExcerpts" :key="group.bookTitle">
            <div class="flex items-center gap-3 pt-4 pb-2 first:pt-0">
              <span class="text-xs font-semibold text-green-700 bg-green-50 px-2.5 py-0.5 rounded-full">{{ group.bookTitle }}</span>
              <div class="flex-1 h-px bg-gray-200"></div>
              <span class="text-xs text-gray-400">{{ group.items.length }} 筆</span>
            </div>
            <div class="space-y-2 mb-2">
              <NuxtLink
                v-for="excerpt in group.items" :key="excerpt.id"
                :to="`/excerpts/${excerpt.id}`"
                class="group block bg-white rounded-xl border border-gray-200 p-4 hover:border-green-300 hover:shadow-md transition-all duration-200"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1.5 flex-wrap">
                      <h3 class="font-semibold text-sm text-gray-900 group-hover:text-green-700 transition">{{ excerpt.title ?? '（無標題）' }}</h3>
                      <span v-if="excerpt.chapter" class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">{{ excerpt.chapter }}</span>
                      <span v-if="excerpt.page_number" class="text-xs text-gray-400">p.{{ excerpt.page_number }}</span>
                    </div>
                    <p class="text-sm text-gray-600 line-clamp-2 leading-relaxed">{{ excerpt.content }}</p>
                  </div>
                  <svg class="w-4 h-4 text-gray-300 group-hover:text-green-400 transition flex-shrink-0 ml-3 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </NuxtLink>
            </div>
          </template>
        </div>
      </template>

      <div v-else class="text-center py-20 text-gray-400">找不到此文章項目</div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const projectId = route.params.id as string;

type Excerpt = { id: string; title: string | null; content: string; chapter: string | null; page_number: string | null; book: { id: string; title: string; author: string } | null };
type Overview = { project: { id: string; name: string; type: string; description: string | null }; total: number; chapters: { name: string; count: number }[] };

const loading = ref(true);
const overview = ref<Overview | null>(null);
const allExcerpts = ref<Excerpt[]>([]);
const searchQ = ref("");

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

// For article page, load all excerpts at once (no chapter filter needed typically)
async function fetchAll() {
  const token = await getToken(); if (!token) return;

  // Get overview
  overview.value = await $fetch<Overview>(`/api/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);

  if (!overview.value) { loading.value = false; return; }

  // Get all excerpts by loading each chapter
  const excerptList: Excerpt[] = [];
  for (const ch of overview.value.chapters) {
    const data = await $fetch<{ project: any; excerpts: Excerpt[] }>(`/api/projects/${projectId}?chapter=${encodeURIComponent(ch.name)}`, {
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => null);
    if (data?.excerpts) excerptList.push(...data.excerpts);
  }
  allExcerpts.value = excerptList;
  loading.value = false;
}

const filteredExcerpts = computed(() => {
  const q = searchQ.value.trim().toLowerCase();
  if (!q) return allExcerpts.value;
  return allExcerpts.value.filter(e =>
    e.title?.toLowerCase().includes(q) || e.content?.toLowerCase().includes(q)
  );
});

const groupedExcerpts = computed(() => {
  const map = new Map<string, Excerpt[]>();
  for (const e of filteredExcerpts.value) {
    const key = e.book?.title ?? '（未指定來源書）';
    map.set(key, [...(map.get(key) ?? []), e]);
  }
  return [...map.entries()].map(([bookTitle, items]) => ({ bookTitle, items }));
});

async function handleLogout() { await supabase.auth.signOut(); router.push("/login"); }

onMounted(fetchAll);
useHead({ title: computed(() => overview.value ? `${overview.value.project.name} — 待寫文章` : "待寫文章") });
</script>
