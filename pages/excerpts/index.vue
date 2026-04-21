<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <NuxtLink to="/" class="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition text-sm">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
              首頁
            </NuxtLink>
          </div>
          <span class="text-xl font-bold text-gray-900">書摘庫</span>
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="mb-10 text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">書摘庫</h1>
        <p class="text-gray-500">管理寫作素材、圖書館藏書與書摘</p>
      </div>

      <div class="grid md:grid-cols-3 gap-6">
        <!-- 待寫著作 -->
        <NuxtLink to="/excerpts/writing"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-purple-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-purple-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">📖</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-purple-700 transition">待寫著作</h2>
          <p class="text-sm text-gray-500 leading-relaxed">管理各部著作的寫作素材，按章節瀏覽引用摘文</p>
          <div class="mt-6 flex items-center gap-1.5 text-purple-600 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
            <span>進入</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </NuxtLink>

        <!-- 書摘圖書館 -->
        <NuxtLink to="/excerpts/library"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-blue-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">📚</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-blue-700 transition">書摘圖書館</h2>
          <p class="text-sm text-gray-500 leading-relaxed">按分類瀏覽藏書，查閱各書的摘文與書目資訊</p>
          <div class="mt-6 flex items-center gap-1.5 text-blue-600 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
            <span>進入</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </NuxtLink>

        <!-- 待寫文章 -->
        <NuxtLink to="/excerpts/article"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-green-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-green-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">✍️</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-green-700 transition">待寫文章</h2>
          <p class="text-sm text-gray-500 leading-relaxed">管理各篇文章的參考素材，整理論點與引文</p>
          <div class="mt-6 flex items-center gap-1.5 text-green-600 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
            <span>進入</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
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
async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}
useHead({ title: "書摘庫 - Know Graph Lab" });
</script>
