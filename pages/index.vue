<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader :editable="false" />

    <div class="max-w-7xl mx-auto px-6 py-10">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-0.5">知識圖工作室</h1>
        <p class="text-gray-500 text-sm">個人學術研究工具集</p>
      </div>

      <!-- 群組：閱讀與典籍 -->
      <section class="mb-9">
        <h2 class="group-label">📚 閱讀與典籍</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- 電子圖書館 -->
          <NuxtLink :to="user ? '/ebook' : '/login'" class="tool-card group border-violet-100 hover:border-violet-300 hover:shadow-violet-100">
            <div class="tool-icon bg-violet-50 text-violet-600">🏛️</div>
            <div class="flex-1">
              <h2 class="tool-title">電子圖書館</h2>
              <p class="tool-desc">分類瀏覽與線上閱讀藏書</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 全集 -->
          <NuxtLink :to="user ? '/collected-works' : '/login'" class="tool-card group border-cyan-100 hover:border-cyan-300 hover:shadow-cyan-100">
            <div class="tool-icon bg-cyan-50 text-cyan-600">📚</div>
            <div class="flex-1">
              <h2 class="tool-title">全集</h2>
              <p class="tool-desc">經典學者全集，多欄逐段對照</p>
            </div>
            <span class="tool-badge tool-badge--wip">建置中</span>
          </NuxtLink>

          <!-- 書摘庫 -->
          <NuxtLink :to="user ? '/excerpts' : '/login'" class="tool-card group border-blue-100 hover:border-blue-300 hover:shadow-blue-100">
            <div class="tool-icon bg-blue-50 text-blue-600">📖</div>
            <div class="flex-1">
              <h2 class="tool-title">書摘庫</h2>
              <p class="tool-desc">整理書籍摘文，建立寫作素材庫</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 經典對照與註釋 -->
          <NuxtLink :to="user ? '/scripture-canon' : '/login'" class="tool-card group border-stone-200 hover:border-stone-400 hover:shadow-stone-100">
            <div class="tool-icon bg-stone-50 text-stone-700">📜</div>
            <div class="flex-1">
              <h2 class="tool-title">經典對照與註釋</h2>
              <p class="tool-desc">基督宗教經典的多版本對照與註釋</p>
            </div>
            <span class="tool-badge tool-badge--wip">建置中</span>
          </NuxtLink>

          <!-- 翻譯定名 -->
          <NuxtLink :to="user ? '/translation-glossary' : '/login'" class="tool-card group border-amber-200 hover:border-amber-400 hover:shadow-amber-100">
            <div class="tool-icon bg-amber-50 text-amber-700">🔤</div>
            <div class="flex-1">
              <h2 class="tool-title">翻譯定名</h2>
              <p class="tool-desc">各領域名物的中譯定名與翻譯原則</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

        </div>
      </section>

      <!-- 群組：研究與寫作 -->
      <section class="mb-9">
        <h2 class="group-label">✍️ 研究與寫作</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- 論文資料整理 -->
          <NuxtLink :to="user ? '/research-data' : '/login'" class="tool-card group border-teal-100 hover:border-teal-300 hover:shadow-teal-100">
            <div class="tool-icon bg-teal-50 text-teal-600">📂</div>
            <div class="flex-1">
              <h2 class="tool-title">論文資料整理</h2>
              <p class="tool-desc">彙整研究主題的文獻與史料</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 寫作計畫 -->
          <NuxtLink :to="user ? '/works' : '/login'" class="tool-card group border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
            <div class="tool-icon bg-rose-50 text-rose-600">✒️</div>
            <div class="flex-1">
              <h2 class="tool-title">寫作計畫</h2>
              <p class="tool-desc">管理書寫計畫與章節草稿</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 學術活動紀錄 -->
          <NuxtLink :to="user ? '/writing' : '/login'" class="tool-card group border-purple-100 hover:border-purple-300 hover:shadow-purple-100">
            <div class="tool-icon bg-purple-50 text-purple-600">✍️</div>
            <div class="flex-1">
              <h2 class="tool-title">學術活動紀錄</h2>
              <p class="tool-desc">彙整學術著作與活動，生成學術履歷</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- AI 對話錄 -->
          <NuxtLink :to="user ? '/ai-dialogues' : '/login'" class="tool-card group border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
            <div class="tool-icon bg-indigo-50 text-indigo-600">💬</div>
            <div class="flex-1">
              <h2 class="tool-title">AI 對話錄</h2>
              <p class="tool-desc">AI 思想對話的存檔與回顧</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

        </div>
      </section>

      <!-- 群組：視覺化工具 -->
      <section class="mb-9">
        <h2 class="group-label">🗺️ 視覺化工具</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- 族譜繪製 -->
          <NuxtLink :to="user ? '/genealogy' : '/login'" class="tool-card group border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
            <div class="tool-icon bg-amber-50 text-amber-600">🌳</div>
            <div class="flex-1">
              <h2 class="tool-title">族譜繪製</h2>
              <p class="tool-desc">AI 解析譜系文字，自動生成樹狀族譜</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 地圖繪製 -->
          <NuxtLink :to="user ? '/maps' : '/login'" class="tool-card group border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100">
            <div class="tool-icon bg-emerald-50 text-emerald-600">🗺️</div>
            <div class="flex-1">
              <h2 class="tool-title">地圖繪製</h2>
              <p class="tool-desc">繪製世界主題與歷史地圖</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

        </div>
      </section>

      <!-- 群組：語言與其他 -->
      <section class="mb-9">
        <h2 class="group-label">🛠️ 語言與其他</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- AI 語言教練 -->
          <NuxtLink :to="user ? '/coach' : '/login'" class="tool-card group border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
            <div class="tool-icon bg-indigo-50 text-indigo-600">🗣️</div>
            <div class="flex-1">
              <h2 class="tool-title">AI 語言教練</h2>
              <p class="tool-desc">外語 VTuber 即時語音對話與練習</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 照片管理 -->
          <NuxtLink :to="user ? '/photos' : '/login'" class="tool-card group border-pink-100 hover:border-pink-300 hover:shadow-pink-100">
            <div class="tool-icon bg-pink-50 text-pink-600">📷</div>
            <div class="flex-1">
              <h2 class="tool-title">照片管理</h2>
              <p class="tool-desc">從雲端硬碟瀏覽與整理相簿</p>
            </div>
            <span class="tool-badge tool-badge--ready">可用</span>
          </NuxtLink>

          <!-- 實驗網站 -->
          <NuxtLink to="/experiments" class="tool-card group border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
            <div class="tool-icon bg-orange-50 text-orange-500">🧪</div>
            <div class="flex-1">
              <h2 class="tool-title">實驗網站</h2>
              <p class="tool-desc">客製專屬研究網站的展示模板</p>
            </div>
            <span class="tool-badge tool-badge--demo">示範</span>
          </NuxtLink>

        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
const user = useSupabaseUser();
useHead({ title: "Workspace" });
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
.tool-badge--ready {
  @apply bg-emerald-50 text-emerald-600;
}
.tool-badge--wip {
  @apply bg-amber-50 text-amber-600;
}
.tool-badge--demo {
  @apply bg-gray-100 text-gray-500;
}
.group-label {
  @apply text-xs font-semibold text-gray-400 mb-3 tracking-wide;
}
</style>
