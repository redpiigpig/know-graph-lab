<template>
  <div class="min-h-screen bg-slate-50">

    <!-- 頂部導航 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-2.5 hover:opacity-80 transition">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-sm font-bold text-white">K</div>
          <span class="font-semibold text-gray-900">Know Graph Lab</span>
        </NuxtLink>
        <div class="flex items-center gap-4">
          <NuxtLink v-if="user" to="/settings" class="text-sm text-gray-500 hover:text-gray-900 transition">設定</NuxtLink>
          <NuxtLink v-if="!user" to="/login" class="text-sm px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition">登入</NuxtLink>
          <span v-else class="text-xs text-gray-400">{{ user.email }}</span>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-6 py-10">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-0.5">知識圖工作室</h1>
        <p class="text-gray-500 text-sm">個人學術研究工具集</p>
      </div>

      <!-- 工具格 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

        <!-- 書摘庫 -->
        <NuxtLink :to="user ? '/excerpts' : '/login'" class="tool-card group border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
          <div class="tool-icon bg-blue-50 text-blue-600">📖</div>
          <div class="flex-1">
            <h2 class="tool-title">書摘庫</h2>
            <p class="tool-desc">管理書籍摘文、按章節和寫作專案組織素材</p>
          </div>
          <span class="tool-badge bg-blue-50 text-blue-600">可用</span>
        </NuxtLink>

        <!-- 電子圖書館 -->
        <NuxtLink :to="user ? '/ebook' : '/login'" class="tool-card group border-violet-100 hover:border-violet-300 hover:shadow-violet-100">
          <div class="tool-icon bg-violet-50 text-violet-600">🏛️</div>
          <div class="flex-1">
            <h2 class="tool-title">電子圖書館</h2>
            <p class="tool-desc">依分類瀏覽書籍，宗教、歷史、哲學等多領域分類</p>
          </div>
          <span class="tool-badge bg-violet-50 text-violet-600">可用</span>
        </NuxtLink>

        <!-- AI 研究助理 -->
        <NuxtLink :to="user ? '/ai' : '/login'" class="tool-card group border-cyan-100 hover:border-cyan-300 hover:shadow-cyan-100">
          <div class="tool-icon bg-cyan-50 text-cyan-600">🤖</div>
          <div class="flex-1">
            <h2 class="tool-title">AI 研究助理</h2>
            <p class="tool-desc">書摘 RAG 問答、拍照 OCR 建摘文，本地 Ollama 驅動</p>
          </div>
          <span class="tool-badge bg-cyan-50 text-cyan-600">可用</span>
        </NuxtLink>

        <!-- 論文寫作系統 -->
        <div class="tool-card border-gray-100 opacity-50 cursor-not-allowed">
          <div class="tool-icon bg-gray-100 text-gray-400">✍️</div>
          <div class="flex-1">
            <h2 class="tool-title text-gray-400">論文寫作系統</h2>
            <p class="tool-desc">整合書摘素材，AI 輔助論文大綱生成與引用管理</p>
          </div>
          <span class="tool-badge bg-gray-100 text-gray-400">開發中</span>
        </div>

        <!-- 流程圖編輯器 -->
        <NuxtLink :to="user ? '/canvas?type=flowchart' : '/login'" class="tool-card group border-sky-100 hover:border-sky-300 hover:shadow-sky-100">
          <div class="tool-icon bg-sky-50 text-sky-600">🔀</div>
          <div class="flex-1">
            <h2 class="tool-title">流程圖編輯器</h2>
            <p class="tool-desc">AI 驅動的智能流程圖，自動佈局，拖拽編輯</p>
          </div>
          <span class="tool-badge bg-sky-50 text-sky-600">可用</span>
        </NuxtLink>

        <!-- 心智圖工具 -->
        <NuxtLink :to="user ? '/canvas?type=mindmap' : '/login'" class="tool-card group border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100">
          <div class="tool-icon bg-emerald-50 text-emerald-600">🧠</div>
          <div class="flex-1">
            <h2 class="tool-title">心智圖工具</h2>
            <p class="tool-desc">整理思緒，AI 智能展開分支，快速建構知識體系</p>
          </div>
          <span class="tool-badge bg-emerald-50 text-emerald-600">可用</span>
        </NuxtLink>

        <!-- 族譜繪製 -->
        <NuxtLink :to="user ? '/genealogy' : '/login'" class="tool-card group border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
          <div class="tool-icon bg-amber-50 text-amber-600">🌳</div>
          <div class="flex-1">
            <h2 class="tool-title">族譜繪製</h2>
            <p class="tool-desc">AI 解析譜系文字，自動生成樹狀族譜，支援手動連線、16 色標注與匯出</p>
          </div>
          <span class="tool-badge bg-amber-50 text-amber-600">可用</span>
        </NuxtLink>

        <!-- 實驗網站 -->
        <NuxtLink :to="user ? '/Hsuan_Chuang_Studies' : '/login'" class="tool-card group border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
          <div class="tool-icon bg-orange-50 text-orange-500">🧪</div>
          <div class="flex-1">
            <h2 class="tool-title">實驗網站</h2>
            <p class="tool-desc">客製化專屬研究網站的展示模板，可依需求替換主題與內容</p>
          </div>
          <span class="tool-badge bg-orange-50 text-orange-500">示範</span>
        </NuxtLink>

        <!-- 架構層級表 -->
        <div class="tool-card border-orange-100 opacity-50 cursor-not-allowed">
          <div class="tool-icon bg-orange-50 text-orange-400">🗂️</div>
          <div class="flex-1">
            <h2 class="tool-title text-gray-400">架構層級表</h2>
            <p class="tool-desc">組織架構、制度層級視覺化，支援多維度關係與自訂群組</p>
          </div>
          <span class="tool-badge bg-orange-50 text-orange-400">開發中</span>
        </div>

        <!-- 智能表格 -->
        <NuxtLink :to="user ? '/canvas?type=table' : '/login'" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="tool-icon bg-rose-50 text-rose-600">📊</div>
          <div class="flex-1">
            <h2 class="tool-title">智能表格</h2>
            <p class="tool-desc">快速生成專業表格，支援資料視覺化與統計分析</p>
          </div>
          <span class="tool-badge bg-rose-50 text-rose-600">可用</span>
        </NuxtLink>

        <!-- AI 生成簡報 -->
        <NuxtLink :to="user ? '/presentation' : '/login'" class="tool-card group border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
          <div class="tool-icon bg-indigo-50 text-indigo-600">🎞️</div>
          <div class="flex-1">
            <h2 class="tool-title">AI 生成簡報</h2>
            <p class="tool-desc">一鍵生成專業簡報，支援 PPT 格式導出</p>
          </div>
          <span class="tool-badge bg-indigo-50 text-indigo-600">可用</span>
        </NuxtLink>

      </div>

      <div class="mt-12 text-center text-gray-400 text-xs">
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
  @apply relative flex items-start gap-4 p-5 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline;
}
.tool-icon {
  @apply w-11 h-11 rounded-xl flex items-center justify-center text-xl select-none flex-shrink-0;
}
.tool-title {
  @apply text-sm font-semibold text-gray-900 mb-0.5;
}
.tool-desc {
  @apply text-xs text-gray-500 leading-relaxed;
}
.tool-badge {
  @apply self-start text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0;
}
</style>
