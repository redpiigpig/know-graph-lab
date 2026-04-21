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
          <NuxtLink to="/" class="flex items-center gap-2">
            <img src="/logo_image.jpg" alt="Know Graph Lab" class="w-7 h-7 rounded-md object-cover" />
            <span class="text-xl font-bold text-gray-900">書摘庫</span>
          </NuxtLink>
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="mb-8 text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">書摘庫</h1>
        <p class="text-gray-500">管理寫作素材、圖書館藏書與全文搜尋</p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 p-4 mb-8">
        <div class="flex gap-3">
          <select
            v-model="globalField"
            class="px-3 py-2.5 border border-gray-200 rounded-xl text-sm bg-white outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="all">全部</option>
            <option value="content">內容</option>
            <option value="title">標題</option>
            <option value="book">書名</option>
            <option value="author">作者</option>
          </select>
          <input
            v-model="globalSearch"
            type="text"
            placeholder="全庫全文搜尋（摘文內容、標題、書名／期刊、作者）"
            class="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-400"
            @keyup.enter="runGlobalSearch"
          />
          <button
            class="px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-500 transition"
            @click="runGlobalSearch"
          >搜尋</button>
        </div>
        <p v-if="searched && !globalResults.length" class="mt-3 text-sm text-gray-400">找不到符合結果</p>
        <div v-if="globalResults.length" class="mt-3 max-h-72 overflow-auto space-y-2">
          <NuxtLink
            v-for="r in globalResults"
            :key="r.id"
            :to="`/excerpts/${r.id}`"
            class="block p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40 transition"
          >
            <div class="flex items-start justify-between gap-3">
              <p class="text-sm font-semibold text-gray-900 flex-1 min-w-0" v-html="highlightText(r.title || '（無標題）', globalSearch)"></p>
              <p class="text-[11px] text-gray-400 whitespace-nowrap">
                <template v-if="r.books?.id">
                  {{ r.books?.author || '未知作者' }} · 《{{ r.books?.title || '未指定來源書' }}》
                </template>
                <template v-else-if="r.journal_articles?.id">
                  {{ r.journal_articles?.author || '未知作者' }} · 《{{ r.journal_articles?.venue || r.journal_articles?.title || '期刊' }}》
                </template>
                <template v-else>未知來源</template>
              </p>
            </div>
            <p class="text-xs text-gray-600 mt-1 line-clamp-2" v-html="highlightText(r.content || '', globalSearch)"></p>
          </NuxtLink>
        </div>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- 著作書摘 -->
        <NuxtLink to="/excerpts/writing"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-purple-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-purple-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">📖</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-purple-700 transition">著作書摘</h2>
          <p class="text-sm text-gray-500 leading-relaxed">管理各部著作的寫作素材，按章節瀏覽引用摘文</p>
          <div class="mt-6 flex items-center gap-1.5 text-purple-600 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
            <span>進入</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </NuxtLink>

        <!-- 文章書摘（在書摘圖書館左側） -->
        <NuxtLink to="/excerpts/article"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-green-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-green-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">✍️</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-green-700 transition">文章書摘</h2>
          <p class="text-sm text-gray-500 leading-relaxed">管理各篇文章的參考素材，整理論點與引文</p>
          <div class="mt-6 flex items-center gap-1.5 text-green-600 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
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

        <!-- 期刊書摘 -->
        <NuxtLink to="/excerpts/journal"
          class="group bg-white rounded-2xl border-2 border-transparent hover:border-amber-300 shadow-sm hover:shadow-xl transition-all duration-300 p-8 flex flex-col items-center text-center cursor-pointer">
          <div class="w-20 h-20 bg-amber-100 rounded-2xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition-transform duration-300">📰</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-amber-800 transition">期刊書摘</h2>
          <p class="text-sm text-gray-500 leading-relaxed">學報、期刊與雜誌篇目，版面與書摘圖書館相同</p>
          <div class="mt-6 flex items-center gap-1.5 text-amber-700 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
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
const globalSearch = ref("");
const globalField = ref<"all" | "content" | "title" | "book" | "author">("all");
const searched = ref(false);
const globalResults = ref<any[]>([]);
async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}
async function runGlobalSearch() {
  const q = globalSearch.value.trim();
  searched.value = true;
  if (!q) { globalResults.value = []; return; }
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return;
  const qs = new URLSearchParams({ search: q });
  if (globalField.value !== "all") qs.set("searchField", globalField.value);
  globalResults.value = await $fetch<any[]>(`/api/excerpts?${qs.toString()}`, {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => []);
}
function highlightText(text: string, keyword: string): string {
  const q = keyword.trim();
  if (!q) return escapeHtml(text);
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const reg = new RegExp(`(${escaped})`, "gi");
  return escapeHtml(text).replace(reg, '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>');
}
function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
onMounted(() => {
  const saved = localStorage.getItem("excerpts-global-search-field");
  if (saved && ["all", "content", "title", "book", "author"].includes(saved)) {
    globalField.value = saved as any;
  }
});
watch(globalField, (v) => {
  localStorage.setItem("excerpts-global-search-field", v);
});
useHead({ title: "書摘庫 - Know Graph Lab" });
</script>
