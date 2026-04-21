<template>
  <div class="min-h-screen bg-gray-950 text-white">

    <!-- 頂部導航 -->
    <nav class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-sm font-bold">K</div>
          <span class="font-semibold text-white">Know Graph Lab</span>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink v-if="user" to="/settings" class="text-sm text-gray-400 hover:text-white transition">設定</NuxtLink>
          <NuxtLink v-if="!user" to="/login" class="text-sm px-4 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg transition">登入</NuxtLink>
          <span v-else class="text-xs text-gray-500">{{ user.email }}</span>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-6 py-12">
      <!-- 標題 -->
      <div class="mb-10">
        <h1 class="text-3xl font-bold text-white mb-1">知識圖工作室</h1>
        <p class="text-gray-400">個人學術研究工具集</p>
      </div>

      <!-- 工具格 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

        <!-- 書摘庫 -->
        <NuxtLink :to="user ? '/excerpts' : '/login'" class="tool-card group bg-gradient-to-br from-blue-950 to-blue-900 border border-blue-800 hover:border-blue-500">
          <div class="tool-icon bg-blue-800 text-blue-300">📖</div>
          <div class="tool-body">
            <h2 class="tool-title">書摘庫</h2>
            <p class="tool-desc">管理書籍摘文、按章節和寫作專案組織素材</p>
          </div>
          <span class="tool-badge bg-blue-800 text-blue-300">可用</span>
        </NuxtLink>

        <!-- 電子圖書館 -->
        <NuxtLink :to="user ? '/ebook' : '/login'" class="tool-card group bg-gradient-to-br from-violet-950 to-violet-900 border border-violet-800 hover:border-violet-500">
          <div class="tool-icon bg-violet-800 text-violet-300">🏛️</div>
          <div class="tool-body">
            <h2 class="tool-title">電子圖書館</h2>
            <p class="tool-desc">依分類瀏覽書籍，宗教、歷史、哲學等多領域分類</p>
          </div>
          <span class="tool-badge bg-violet-800 text-violet-300">可用</span>
        </NuxtLink>

        <!-- AI 研究助理 -->
        <NuxtLink :to="user ? '/ai' : '/login'" class="tool-card group bg-gradient-to-br from-cyan-950 to-cyan-900 border border-cyan-800 hover:border-cyan-500">
          <div class="tool-icon bg-cyan-800 text-cyan-300">🤖</div>
          <div class="tool-body">
            <h2 class="tool-title">AI 研究助理</h2>
            <p class="tool-desc">書摘 RAG 問答、拍照 OCR 建摘文，本地 Ollama 驅動</p>
          </div>
          <span class="tool-badge bg-cyan-800 text-cyan-300">可用</span>
        </NuxtLink>

        <!-- 論文寫作系統 -->
        <div class="tool-card group bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 opacity-60 cursor-not-allowed">
          <div class="tool-icon bg-gray-700 text-gray-400">✍️</div>
          <div class="tool-body">
            <h2 class="tool-title text-gray-300">論文寫作系統</h2>
            <p class="tool-desc text-gray-500">整合書摘素材，AI 輔助論文大綱生成與引用管理</p>
          </div>
          <span class="tool-badge bg-gray-700 text-gray-400">開發中</span>
        </div>

        <!-- 流程圖編輯器 -->
        <NuxtLink :to="user ? '/canvas?type=flowchart' : '/login'" class="tool-card group bg-gradient-to-br from-sky-950 to-sky-900 border border-sky-800 hover:border-sky-500">
          <div class="tool-icon bg-sky-800 text-sky-300">🔀</div>
          <div class="tool-body">
            <h2 class="tool-title">流程圖編輯器</h2>
            <p class="tool-desc">AI 驅動的智能流程圖，自動佈局，拖拽編輯</p>
          </div>
          <span class="tool-badge bg-sky-800 text-sky-300">可用</span>
        </NuxtLink>

        <!-- 心智圖工具 -->
        <NuxtLink :to="user ? '/canvas?type=mindmap' : '/login'" class="tool-card group bg-gradient-to-br from-emerald-950 to-emerald-900 border border-emerald-800 hover:border-emerald-500">
          <div class="tool-icon bg-emerald-800 text-emerald-300">🧠</div>
          <div class="tool-body">
            <h2 class="tool-title">心智圖工具</h2>
            <p class="tool-desc">整理思緒，AI 智能展開分支，快速建構知識體系</p>
          </div>
          <span class="tool-badge bg-emerald-800 text-emerald-300">可用</span>
        </NuxtLink>

        <!-- 互動地圖 -->
        <NuxtLink :to="user ? '/map' : '/login'" class="tool-card group bg-gradient-to-br from-teal-950 to-teal-900 border border-teal-800 hover:border-teal-500">
          <div class="tool-icon bg-teal-800 text-teal-300">🗺️</div>
          <div class="tool-body">
            <h2 class="tool-title">互動地圖</h2>
            <p class="tool-desc">AI 識別地理區域，精確到縣級，自訂標記與圖層</p>
          </div>
          <span class="tool-badge bg-teal-800 text-teal-300">可用</span>
        </NuxtLink>

        <!-- 譜系圖繪製 -->
        <NuxtLink :to="user ? '/canvas?type=genealogy' : '/login'" class="tool-card group bg-gradient-to-br from-amber-950 to-amber-900 border border-amber-800 hover:border-amber-500">
          <div class="tool-icon bg-amber-800 text-amber-300">🌳</div>
          <div class="tool-body">
            <h2 class="tool-title">譜系圖繪製</h2>
            <p class="tool-desc">層級關係視覺化，適合組織架構、家族譜系</p>
          </div>
          <span class="tool-badge bg-amber-800 text-amber-300">可用</span>
        </NuxtLink>

        <!-- 智能表格 -->
        <NuxtLink :to="user ? '/canvas?type=table' : '/login'" class="tool-card group bg-gradient-to-br from-rose-950 to-rose-900 border border-rose-800 hover:border-rose-500">
          <div class="tool-icon bg-rose-800 text-rose-300">📊</div>
          <div class="tool-body">
            <h2 class="tool-title">智能表格</h2>
            <p class="tool-desc">快速生成專業表格，支援資料視覺化與統計分析</p>
          </div>
          <span class="tool-badge bg-rose-800 text-rose-300">可用</span>
        </NuxtLink>

        <!-- AI 生成簡報 -->
        <NuxtLink :to="user ? '/presentation' : '/login'" class="tool-card group bg-gradient-to-br from-indigo-950 to-indigo-900 border border-indigo-800 hover:border-indigo-500">
          <div class="tool-icon bg-indigo-800 text-indigo-300">🎞️</div>
          <div class="tool-body">
            <h2 class="tool-title">AI 生成簡報</h2>
            <p class="tool-desc">一鍵生成專業簡報，支援 PPT 格式導出</p>
          </div>
          <span class="tool-badge bg-indigo-800 text-indigo-300">可用</span>
        </NuxtLink>

      </div>

      <!-- 底部資訊 -->
      <div class="mt-16 pt-8 border-t border-gray-800 text-center text-gray-600 text-xs">
        Know Graph Lab &nbsp;·&nbsp; 個人版 &nbsp;·&nbsp; 2026
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const user = useSupabaseUser();
useHead({ title: "Know Graph Lab — 知識圖工作室" });
</script>

<style scoped>
.tool-card {
  @apply relative flex flex-col gap-4 p-6 rounded-2xl border transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5 cursor-pointer no-underline;
}
.tool-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-2xl select-none flex-shrink-0;
}
.tool-body {
  @apply flex-1;
}
.tool-title {
  @apply text-base font-semibold text-white mb-1;
}
.tool-desc {
  @apply text-sm text-gray-400 leading-relaxed;
}
.tool-badge {
  @apply self-start text-xs font-medium px-2.5 py-0.5 rounded-full;
}
</style>
