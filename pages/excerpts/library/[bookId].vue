<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition">書摘庫</NuxtLink>
            <span>›</span>
            <NuxtLink to="/excerpts/library" class="hover:text-blue-600 transition">書摘圖書館</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900 truncate max-w-xs">{{ book?.title ?? '載入中…' }}</span>
          </div>
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <!-- 載入骨架 -->
      <div v-if="loading" class="space-y-4 animate-pulse">
        <div class="bg-white rounded-2xl p-8 h-36"></div>
        <div class="bg-white rounded-xl p-6 h-24"></div>
        <div class="bg-white rounded-xl p-6 h-24"></div>
      </div>

      <template v-else-if="book">
        <!-- ── 書籍資訊卡 ── -->
        <div class="bg-white rounded-2xl border border-gray-200 p-6 mb-8 shadow-sm">
          <div class="flex items-start gap-5">
            <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 select-none">📚</div>
            <div class="flex-1">
              <h1 class="text-2xl font-bold text-gray-900 leading-tight">{{ book.title }}</h1>
              <p class="text-base text-gray-600 mt-0.5 mb-3">{{ book.author }}</p>
              <div class="flex flex-wrap gap-x-5 gap-y-1 text-sm text-gray-500">
                <span v-if="book.translator">譯者：{{ book.translator }}</span>
                <span v-if="book.publish_place">出版地：{{ book.publish_place }}</span>
                <span v-if="book.publisher">出版社：{{ book.publisher }}</span>
                <span v-if="book.publish_year">{{ book.publish_year }}</span>
                <span v-if="book.edition">{{ book.edition }}</span>
              </div>
              <p class="mt-3 text-sm text-blue-600 font-medium">共 {{ book.excerpts?.length ?? 0 }} 筆摘文</p>
            </div>
          </div>
        </div>

        <!-- ── 空狀態 ── -->
        <div v-if="!book.excerpts?.length" class="text-center py-16 text-gray-400">
          <p class="text-lg">此書尚無摘文</p>
        </div>

        <!-- ── 按項目分組顯示 ── -->
        <template v-else>
          <!-- 項目分組 tabs -->
          <div class="flex flex-wrap gap-2 mb-6">
            <button
              @click="activeProject = null"
              :class="['px-4 py-1.5 rounded-full text-sm font-medium border transition',
                !activeProject ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400']"
            >全部（{{ book.excerpts.length }}）</button>
            <button
              v-for="proj in projectGroups" :key="proj.name"
              @click="activeProject = proj.name"
              :class="['px-4 py-1.5 rounded-full text-sm font-medium border transition',
                activeProject === proj.name ? projStyle(proj.name).active : projStyle(proj.name).idle]"
            >{{ proj.name }}（{{ proj.items.length }}）</button>
          </div>

          <!-- 摘文列表 -->
          <div class="space-y-3">
            <template v-for="proj in visibleGroups" :key="proj.name">
              <!-- 分組標題（全部模式才顯示） -->
              <div v-if="!activeProject" class="flex items-center gap-3 pt-2 pb-1">
                <span :class="['text-xs font-semibold px-2.5 py-0.5 rounded-full', projStyle(proj.name).badge]">{{ proj.name }}</span>
                <div class="flex-1 h-px bg-gray-200"></div>
              </div>

              <NuxtLink
                v-for="excerpt in proj.items" :key="excerpt.id"
                :to="`/excerpts/${excerpt.id}`"
                class="group block bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-300 hover:shadow-md transition-all duration-200"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1.5 flex-wrap">
                      <h3 class="font-semibold text-sm text-gray-900 group-hover:text-blue-700 transition leading-snug">
                        {{ excerpt.title ?? '（無標題）' }}
                      </h3>
                      <span v-if="excerpt.chapter" class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">{{ excerpt.chapter }}</span>
                      <span v-if="excerpt.page_number" class="text-xs text-gray-400">p.{{ excerpt.page_number }}</span>
                    </div>
                    <p class="text-sm text-gray-600 line-clamp-2 leading-relaxed">{{ excerpt.content }}</p>
                  </div>
                  <svg class="w-4 h-4 text-gray-300 group-hover:text-blue-400 transition flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </NuxtLink>
            </template>
          </div>
        </template>
      </template>

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

type Excerpt = {
  id: string; title: string | null; content: string;
  chapter: string | null; page_number: string | null; created_at: string;
  projects: { id: string; name: string; type: string }[];
};
type Book = {
  id: string; title: string; author: string;
  translator?: string; publish_place?: string; publisher?: string;
  publish_year?: number; edition?: string; category_id?: string;
  excerpts: Excerpt[];
};

const loading = ref(true);
const book = ref<Book | null>(null);
const activeProject = ref<string | null>(null);

// Group excerpts by project name
const projectGroups = computed(() => {
  if (!book.value?.excerpts) return [];
  const map = new Map<string, Excerpt[]>();

  for (const ex of book.value.excerpts) {
    if (ex.projects.length === 0) {
      const key = "書摘";
      map.set(key, [...(map.get(key) ?? []), ex]);
    } else {
      for (const p of ex.projects) {
        map.set(p.name, [...(map.get(p.name) ?? []), ex]);
      }
    }
  }

  const order = ["待寫著作", "待寫文章", "書摘"];
  return [...map.entries()]
    .sort(([a], [b]) => (order.indexOf(a) ?? 99) - (order.indexOf(b) ?? 99))
    .map(([name, items]) => ({ name, items }));
});

const visibleGroups = computed(() => {
  if (!activeProject.value) return projectGroups.value;
  return projectGroups.value.filter((g) => g.name === activeProject.value);
});

function projStyle(name: string) {
  const styles: Record<string, { active: string; idle: string; badge: string }> = {
    "待寫著作": {
      active: "bg-purple-600 text-white border-purple-600",
      idle: "bg-white text-purple-600 border-purple-200 hover:border-purple-400",
      badge: "bg-purple-100 text-purple-700",
    },
    "待寫文章": {
      active: "bg-green-600 text-white border-green-600",
      idle: "bg-white text-green-600 border-green-200 hover:border-green-400",
      badge: "bg-green-100 text-green-700",
    },
    "書摘": {
      active: "bg-blue-600 text-white border-blue-600",
      idle: "bg-white text-blue-600 border-blue-200 hover:border-blue-400",
      badge: "bg-blue-100 text-blue-700",
    },
  };
  return styles[name] ?? {
    active: "bg-gray-600 text-white border-gray-600",
    idle: "bg-white text-gray-600 border-gray-200 hover:border-gray-400",
    badge: "bg-gray-100 text-gray-700",
  };
}

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
useHead({ title: computed(() => book.value ? `${book.value.title} — 書摘` : "書摘") });
</script>
