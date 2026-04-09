<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50"
  >
    <!-- 導航欄 -->
    <nav
      class="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <img src="/images/logo-icon.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold text-gray-900">Know Graph Lab</span>
          </div>
          <div class="flex items-center space-x-6">
            <a
              href="#features"
              class="text-gray-600 hover:text-blue-600 transition"
              >功能</a
            >
            <a
              href="https://github.com/redpiigpig/know-graph-lab"
              target="_blank"
              class="text-gray-600 hover:text-blue-600 transition"
              >GitHub</a
            >
            <NuxtLink
              v-if="user"
              to="/settings"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              進入工作室
            </NuxtLink>
            <NuxtLink
              v-else
              to="/login"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              登入
            </NuxtLink>
            <NuxtLink
              to="/guide"
              class="text-gray-600 hover:text-blue-600 transition"
              >使用指南</NuxtLink
            >
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero 區塊 -->
    <section class="py-20 sm:py-32">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <!-- Logo -->
          <div class="flex justify-center mb-8">
            <img
              src="/images/logo-icon.svg"
              alt="Know Graph Lab Logo"
              class="w-24 h-24 sm:w-32 sm:h-32"
            />
          </div>

          <!-- 標題 -->
          <h1
            class="text-5xl sm:text-6xl md:text-7xl font-bold text-gray-900 mb-6"
          >
            Know Graph Lab
          </h1>
          <p class="text-2xl sm:text-3xl text-gray-600 mb-3">知識圖工作室</p>
          <p class="text-lg sm:text-xl text-gray-500 mb-10">
            Where Knowledge Takes Shape
          </p>

          <!-- 標籤 -->
          <div class="flex flex-wrap gap-3 justify-center mb-10">
            <span
              class="px-5 py-2.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
            >
              🤖 AI Powered
            </span>
            <span
              class="px-5 py-2.5 bg-green-100 text-green-700 rounded-full text-sm font-medium"
            >
              📊 多種圖表
            </span>
            <span
              class="px-5 py-2.5 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
            >
              🎨 專業設計
            </span>
            <span
              class="px-5 py-2.5 bg-amber-100 text-amber-700 rounded-full text-sm font-medium"
            >
              🆓 完全免費
            </span>
          </div>

          <!-- CTA 按鈕 -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink
              :to="user ? '/settings' : '/signup'"
              class="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transform hover:scale-105 transition shadow-lg text-center"
            >
              {{ user ? '進入工作室' : '立即開始' }}
            </NuxtLink>
            <a
              href="https://github.com/redpiigpig/know-graph-lab"
              target="_blank"
              class="px-8 py-4 border-2 border-gray-300 bg-white text-gray-700 font-semibold rounded-lg hover:border-blue-600 hover:text-blue-600 transform hover:scale-105 transition text-center"
            >
              查看 GitHub
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能介紹 -->
    <section id="features" class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">強大的功能</h2>
          <p class="text-xl text-gray-600">
            AI 驅動的學術視覺化工具，讓知識呈現更簡單
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- 流程圖 -->
          <div
            class="group p-8 bg-gradient-to-br from-blue-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-blue-100"
          >
            <div
              class="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">
              流程圖編輯器
            </h3>
            <p class="text-gray-600 leading-relaxed">
              AI
              驅動的智能流程圖，自動佈局優化，支援拖拽編輯，讓複雜流程一目了然。
            </p>
          </div>

          <!-- 心智圖 -->
          <div
            class="group p-8 bg-gradient-to-br from-green-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-green-100"
          >
            <div
              class="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">
              心智圖工具
            </h3>
            <p class="text-gray-600 leading-relaxed">
              輕鬆整理思緒，AI 智能展開分支，幫助你快速構建知識體系。
            </p>
          </div>

          <!-- 地圖標記 -->
          <div
            class="group p-8 bg-gradient-to-br from-purple-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-purple-100"
          >
            <div
              class="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-purple-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">互動地圖</h3>
            <p class="text-gray-600 leading-relaxed">
              AI 智能識別地理區域，精確到縣級，支援自訂標記和圖層管理。
            </p>
          </div>

          <!-- 譜系圖 -->
          <div
            class="group p-8 bg-gradient-to-br from-amber-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-amber-100"
          >
            <div
              class="w-14 h-14 bg-amber-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-amber-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">
              譜系圖繪製
            </h3>
            <p class="text-gray-600 leading-relaxed">
              清晰展示層級關係，適合組織架構、家族譜系等場景。
            </p>
          </div>

          <!-- 智能表格 -->
          <div
            class="group p-8 bg-gradient-to-br from-pink-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-pink-100"
          >
            <div
              class="w-14 h-14 bg-pink-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-pink-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">智能表格</h3>
            <p class="text-gray-600 leading-relaxed">
              快速生成專業表格，支援資料視覺化和統計分析。
            </p>
          </div>

          <!-- PPT 生成 -->
          <div
            class="group p-8 bg-gradient-to-br from-indigo-50 to-white rounded-2xl hover:shadow-2xl transition-all duration-300 border border-indigo-100"
          >
            <div
              class="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition"
            >
              <svg
                class="w-8 h-8 text-indigo-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-3 text-gray-900">
              AI 生成簡報
            </h3>
            <p class="text-gray-600 leading-relaxed">
              一鍵生成專業簡報，支援 PPT 格式導出，節省製作時間。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用說明區塊 -->
    <section class="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">如何開始使用</h2>
          <p class="text-xl text-gray-600">
            只需三個步驟，立即體驗 AI 圖表工具
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div class="text-center">
            <div
              class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4"
            >
              1
            </div>
            <h3 class="text-xl font-semibold mb-2">註冊帳號</h3>
            <p class="text-gray-600">完全免費，只需 Email 即可註冊</p>
          </div>
          <div class="text-center">
            <div
              class="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4"
            >
              2
            </div>
            <h3 class="text-xl font-semibold mb-2">設定 API Key</h3>
            <p class="text-gray-600">使用你自己的 Gemini API Key，永久免費</p>
          </div>
          <div class="text-center">
            <div
              class="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4"
            >
              3
            </div>
            <h3 class="text-xl font-semibold mb-2">開始創作</h3>
            <p class="text-gray-600">輸入需求，AI 自動生成專業圖表</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 技術特色 -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">為什麼選擇我們</h2>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="text-5xl mb-4">🚀</div>
            <h3 class="text-xl font-semibold mb-2">快速高效</h3>
            <p class="text-gray-600">AI 驅動，秒級生成專業圖表</p>
          </div>
          <div class="text-center">
            <div class="text-5xl mb-4">🎯</div>
            <h3 class="text-xl font-semibold mb-2">精準智能</h3>
            <p class="text-gray-600">理解需求，自動優化佈局</p>
          </div>
          <div class="text-center">
            <div class="text-5xl mb-4">💎</div>
            <h3 class="text-xl font-semibold mb-2">完全免費</h3>
            <p class="text-gray-600">開源專案，永久免費使用</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 區塊 -->
    <section class="py-20 bg-gradient-to-r from-blue-600 to-blue-700">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-4xl font-bold text-white mb-6">準備好開始了嗎？</h2>
        <p class="text-xl text-blue-100 mb-10">
          免費註冊，設定你的 API Key，立即體驗 AI 驅動的圖表工具
        </p>
        <NuxtLink
          :to="user ? '/settings' : '/signup'"
          class="inline-block px-10 py-4 bg-white text-blue-600 font-bold text-lg rounded-lg hover:bg-gray-100 transform hover:scale-105 transition shadow-2xl"
        >
          {{ user ? '進入工作室 →' : '開始創作 →' }}
        </NuxtLink>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-3 gap-8">
          <div>
            <div class="flex items-center space-x-2 mb-4">
              <img src="/images/logo-icon.svg" alt="Logo" class="w-8 h-8" />
              <span class="text-xl font-bold text-white">Know Graph Lab</span>
            </div>
            <p class="text-gray-400">讓知識以最美的方式呈現</p>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">連結</h4>
            <ul class="space-y-2">
              <li>
                <NuxtLink to="/login" class="hover:text-white transition"
                  >登入</NuxtLink
                >
              </li>
              <li>
                <NuxtLink to="/signup" class="hover:text-white transition"
                  >註冊</NuxtLink
                >
              </li>
              <li>
                <a href="#features" class="hover:text-white transition"
                  >功能介紹</a
                >
              </li>
              <li>
                <a
                  href="https://github.com/redpiigpig/know-graph-lab"
                  class="hover:text-white transition"
                  >GitHub</a
                >
              </li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">關於</h4>
            <p class="text-gray-400">開源專案，歡迎貢獻與回饋</p>
          </div>
        </div>
        <div
          class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500"
        >
          <p>&copy; 2026 Know Graph Lab. Made with ❤️ by the community.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const user = useSupabaseUser();

useHead({
  title: "Know Graph Lab - AI 驅動的知識圖表工具",
  meta: [
    {
      name: "description",
      content:
        "專為學術研究設計的智能圖表工具。支援流程圖、心智圖、地圖、譜系圖，整合 AI 自動生成簡報。完全免費，使用你自己的 API Key。",
    },
  ],
});
</script>
