<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition">書摘庫</NuxtLink>
            <span>›</span>
            <span class="font-semibold text-green-700">待寫文章</span>
          </div>
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="flex items-center gap-4 mb-8">
        <div class="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center text-3xl">✍️</div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">待寫文章</h1>
          <p class="text-sm text-gray-500 mt-0.5">管理各篇文章的寫作素材</p>
        </div>
      </div>

      <!-- 載入骨架 -->
      <div v-if="loading" class="grid sm:grid-cols-2 gap-5">
        <div v-for="i in 2" :key="i" class="bg-white rounded-2xl border border-gray-200 p-6 animate-pulse h-40"></div>
      </div>

      <!-- 文章項目卡 -->
      <div v-else-if="projects.length" class="grid sm:grid-cols-2 gap-5">
        <NuxtLink
          v-for="proj in projects" :key="proj.id"
          :to="`/excerpts/article/${proj.id}`"
          class="group bg-white rounded-2xl border border-gray-200 hover:border-green-300 hover:shadow-lg transition-all duration-200 p-6 flex flex-col"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl">✍️</div>
            <span class="text-xs bg-green-50 text-green-600 font-medium px-2.5 py-1 rounded-full">待寫文章</span>
          </div>
          <h2 class="text-xl font-bold text-gray-900 mb-1 group-hover:text-green-700 transition">{{ proj.name }}</h2>
          <p v-if="proj.description" class="text-sm text-gray-400 mb-3 line-clamp-2">{{ proj.description }}</p>
          <div class="mt-auto flex items-center gap-4 text-sm text-gray-500">
            <span class="text-green-600 font-semibold">{{ proj.excerpt_count }} 筆素材</span>
            <span v-if="proj.book_count">· {{ proj.book_count }} 本來源書</span>
          </div>
        </NuxtLink>
      </div>

      <!-- 空狀態 -->
      <div v-else class="text-center py-24 text-gray-400">
        <div class="text-5xl mb-4">✍️</div>
        <p class="text-lg font-medium text-gray-500">尚無待寫文章項目</p>
        <p class="text-sm mt-1">可在資料庫中新增 book_projects（type=待寫文章）</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
const supabase = useSupabaseClient();
const router = useRouter();

type Project = { id: string; name: string; type: string; description: string | null; excerpt_count: number; book_count: number };
const loading = ref(true);
const projects = ref<Project[]>([]);

async function fetchProjects() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return; }
  projects.value = await $fetch<Project[]>("/api/projects?type=待寫文章", {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => []);
  loading.value = false;
}

async function handleLogout() { await supabase.auth.signOut(); router.push("/login"); }

onMounted(fetchProjects);
useHead({ title: "待寫文章 — 書摘庫" });
</script>
