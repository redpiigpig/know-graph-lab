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
          <NuxtLink to="/" class="flex items-center space-x-3">
            <img src="/images/logo-icon.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold text-gray-900">Know Graph Lab</span>
          </NuxtLink>
          <div class="flex items-center space-x-6">
            <NuxtLink
              to="/"
              class="text-gray-600 hover:text-blue-600 transition"
              >首頁</NuxtLink
            >
            <NuxtLink
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

    <!-- Hero -->
    <section
      class="py-16 bg-gradient-to-r from-blue-600 to-blue-700 text-white"
    >
      <div class="max-w-5xl mx-auto px-4 text-center">
        <h1 class="text-5xl font-bold mb-4">使用指南</h1>
        <p class="text-xl text-blue-100">
          從註冊到開始使用，完整教學與資安說明
        </p>
      </div>
    </section>

    <!-- 目錄 -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="bg-white rounded-xl shadow-sm border p-6 mb-12">
        <h2 class="text-xl font-semibold mb-4">📑 快速導航</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <a href="#getting-started" class="text-blue-600 hover:underline"
            >→ 快速開始</a
          >
          <a href="#api-key-guide" class="text-blue-600 hover:underline"
            >→ 如何取得 API Key</a
          >
          <a href="#security" class="text-blue-600 hover:underline"
            >→ 資安保護措施</a
          >
          <a href="#features" class="text-blue-600 hover:underline"
            >→ 進階功能</a
          >
          <a href="#faq" class="text-blue-600 hover:underline">→ 常見問題</a>
          <a href="#contact" class="text-blue-600 hover:underline"
            >→ 聯絡我們</a
          >
        </div>
      </div>
    </div>

    <!-- 主要內容 -->
    <div class="max-w-5xl mx-auto px-4 pb-20">
      <!-- 快速開始 -->
      <section id="getting-started" class="mb-16 scroll-mt-20">
        <div
          class="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden"
        >
          <div
            class="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white"
          >
            <h2 class="text-3xl font-bold">🚀 快速開始</h2>
            <p class="mt-2 text-blue-100">三個步驟，立即開始使用</p>
          </div>

          <div class="p-8">
            <!-- 步驟 1 -->
            <div class="flex items-start space-x-6 mb-12">
              <div
                class="flex-shrink-0 w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg"
              >
                1
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-3">註冊帳號</h3>
                <p class="text-gray-600 mb-4 leading-relaxed">
                  使用你的 Email
                  註冊一個免費帳號。我們不會向你收取任何費用，也不會分享你的個人資訊。
                </p>
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p class="text-sm text-gray-700 font-medium mb-2">
                    📌 注意事項：
                  </p>
                  <ul class="text-sm text-gray-600 space-y-1 ml-4">
                    <li>• 密碼至少 6 個字元</li>
                    <li>• 註冊後請至 Email 信箱驗證</li>
                    <li>• 建議使用常用的 Email 帳號</li>
                  </ul>
                </div>
                <NuxtLink
                  to="/signup"
                  class="inline-block mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
                >
                  立即註冊 →
                </NuxtLink>
              </div>
            </div>

            <!-- 步驟 2 -->
            <div class="flex items-start space-x-6 mb-12">
              <div
                class="flex-shrink-0 w-16 h-16 bg-green-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg"
              >
                2
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-3">
                  取得並設定 API Key
                </h3>
                <p class="text-gray-600 mb-4 leading-relaxed">
                  登入後，前往「設定」頁面，新增你的 Gemini API Key。我們會將
                  API Key <strong>加密儲存</strong>，只有你能使用。
                </p>
                <div
                  class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4"
                >
                  <p class="text-sm font-semibold text-blue-900 mb-2">
                    💡 為什麼需要你自己的 API Key？
                  </p>
                  <ul class="text-sm text-blue-800 space-y-2">
                    <li>
                      <strong>✓ 完全免費：</strong>Google 提供免費的 Gemini API
                      額度，每天可使用數百次
                    </li>
                    <li>
                      <strong>✓ 資料隱私：</strong>你的請求直接發送到
                      Google，我們看不到內容
                    </li>
                    <li>
                      <strong>✓ 無限制：</strong>不需要擔心共用額度用盡的問題
                    </li>
                  </ul>
                </div>
                <a
                  href="#api-key-guide"
                  class="inline-block px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition font-semibold"
                >
                  查看詳細教學 →
                </a>
              </div>
            </div>

            <!-- 步驟 3 -->
            <div class="flex items-start space-x-6">
              <div
                class="flex-shrink-0 w-16 h-16 bg-purple-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg"
              >
                3
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-3">開始創作</h3>
                <p class="text-gray-600 mb-4 leading-relaxed">
                  設定完成後，你就可以開始使用所有功能：AI
                  生成流程圖、心智圖、地圖標記、簡報製作等。
                </p>
                <div class="grid sm:grid-cols-2 gap-4">
                  <div class="border border-gray-200 rounded-lg p-4">
                    <div
                      class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3"
                    >
                      <svg
                        class="w-6 h-6 text-blue-600"
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
                    <h4 class="font-semibold text-gray-900 mb-1">流程圖</h4>
                    <p class="text-sm text-gray-600">輸入描述，AI 自動生成</p>
                  </div>
                  <div class="border border-gray-200 rounded-lg p-4">
                    <div
                      class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3"
                    >
                      <svg
                        class="w-6 h-6 text-green-600"
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
                    <h4 class="font-semibold text-gray-900 mb-1">地圖標記</h4>
                    <p class="text-sm text-gray-600">AI 智能識別地理區域</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- API Key 取得教學 -->
      <section id="api-key-guide" class="mb-16 scroll-mt-20">
        <div
          class="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden"
        >
          <div
            class="bg-gradient-to-r from-green-600 to-green-700 p-6 text-white"
          >
            <h2 class="text-3xl font-bold">🔑 如何取得 Gemini API Key</h2>
            <p class="mt-2 text-green-100">完全免費，只需 5 分鐘</p>
          </div>

          <div class="p-8">
            <div class="space-y-8">
              <!-- 步驟詳解 -->
              <div class="border-l-4 border-green-500 pl-6">
                <div class="flex items-center space-x-3 mb-3">
                  <span
                    class="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center font-bold text-sm"
                    >1</span
                  >
                  <h3 class="text-xl font-bold text-gray-900">
                    前往 Google AI Studio
                  </h3>
                </div>
                <p class="text-gray-600 mb-3">在瀏覽器中開啟以下網址：</p>
                <a
                  href="https://aistudio.google.com/app/apikey"
                  target="_blank"
                  class="inline-flex items-center px-4 py-2 bg-green-50 border border-green-300 rounded-lg text-green-700 hover:bg-green-100 transition font-mono text-sm"
                >
                  https://aistudio.google.com/app/apikey
                  <svg
                    class="w-4 h-4 ml-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
              </div>

              <div class="border-l-4 border-green-500 pl-6">
                <div class="flex items-center space-x-3 mb-3">
                  <span
                    class="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center font-bold text-sm"
                    >2</span
                  >
                  <h3 class="text-xl font-bold text-gray-900">
                    登入 Google 帳號
                  </h3>
                </div>
                <p class="text-gray-600">
                  使用你的 Google 帳號登入（Gmail 帳號）。如果你還沒有 Google
                  帳號，需要先註冊一個。
                </p>
              </div>

              <div class="border-l-4 border-green-500 pl-6">
                <div class="flex items-center space-x-3 mb-3">
                  <span
                    class="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center font-bold text-sm"
                    >3</span
                  >
                  <h3 class="text-xl font-bold text-gray-900">建立 API Key</h3>
                </div>
                <p class="text-gray-600 mb-3">
                  點擊頁面上的 <strong>「Get API key」</strong> 或
                  <strong>「Create API key」</strong> 按鈕。
                </p>
                <div
                  class="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                >
                  <p class="text-sm text-yellow-800">
                    <strong>💡 提示：</strong>
                    如果是第一次使用，系統可能會要求你建立或選擇一個 Google
                    Cloud 專案。選擇「Create API key in new
                    project」即可，這不會收費。
                  </p>
                </div>
              </div>

              <div class="border-l-4 border-green-500 pl-6">
                <div class="flex items-center space-x-3 mb-3">
                  <span
                    class="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center font-bold text-sm"
                    >4</span
                  >
                  <h3 class="text-xl font-bold text-gray-900">複製 API Key</h3>
                </div>
                <p class="text-gray-600 mb-3">
                  建立完成後，系統會顯示你的 API Key（格式類似
                  <code class="px-2 py-1 bg-gray-100 rounded font-mono text-sm"
                    >AIzaSyABC123...</code
                  >）。點擊「Copy」按鈕複製。
                </p>
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p class="text-sm text-red-800">
                    <strong>⚠️ 重要：</strong> 不要將 API Key
                    分享給任何人！這就像你的密碼一樣重要。
                  </p>
                </div>
              </div>

              <div class="border-l-4 border-green-500 pl-6">
                <div class="flex items-center space-x-3 mb-3">
                  <span
                    class="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center font-bold text-sm"
                    >5</span
                  >
                  <h3 class="text-xl font-bold text-gray-900">
                    貼到 Know Graph Lab
                  </h3>
                </div>
                <p class="text-gray-600">
                  回到 Know Graph Lab，前往「設定」頁面，將 API Key
                  貼到輸入框中，點擊「儲存」。完成！
                </p>
              </div>
            </div>

            <!-- 免費額度說明 -->
            <div
              class="mt-8 bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6"
            >
              <h4 class="text-lg font-bold text-gray-900 mb-3">
                💰 關於免費額度
              </h4>
              <div class="space-y-2 text-sm text-gray-700">
                <p>
                  • <strong>完全免費：</strong>Google Gemini API
                  提供慷慨的免費額度
                </p>
                <p>
                  • <strong>每分鐘請求數：</strong>最多 15
                  次（對個人使用綽綽有餘）
                </p>
                <p>• <strong>每日請求數：</strong>最多 1,500 次</p>
                <p>• <strong>每月請求數：</strong>最多 50,000 次</p>
                <p class="pt-2 border-t border-blue-300">
                  <strong>👉 結論：</strong
                  >除非你每天生成數百個圖表，否則免費額度完全夠用！
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 資安保護措施 -->
      <section id="security" class="mb-16 scroll-mt-20">
        <div
          class="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden"
        >
          <div
            class="bg-gradient-to-r from-purple-600 to-purple-700 p-6 text-white"
          >
            <h2 class="text-3xl font-bold">🔒 資安保護措施</h2>
            <p class="mt-2 text-purple-100">
              你的 API Key 安全是我們的首要任務
            </p>
          </div>

          <div class="p-8">
            <!-- 保護層級圖 -->
            <div
              class="mb-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200"
            >
              <h3 class="text-xl font-bold text-gray-900 mb-4 text-center">
                🛡️ 多層保護機制
              </h3>
              <div class="grid md:grid-cols-3 gap-4">
                <div class="bg-white rounded-lg p-4 shadow-sm">
                  <div
                    class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3 mx-auto"
                  >
                    <svg
                      class="w-6 h-6 text-purple-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                      />
                    </svg>
                  </div>
                  <h4 class="font-bold text-center mb-2">傳輸加密</h4>
                  <p class="text-sm text-gray-600 text-center">
                    HTTPS/TLS 加密傳輸
                  </p>
                </div>
                <div class="bg-white rounded-lg p-4 shadow-sm">
                  <div
                    class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3 mx-auto"
                  >
                    <svg
                      class="w-6 h-6 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                      />
                    </svg>
                  </div>
                  <h4 class="font-bold text-center mb-2">儲存加密</h4>
                  <p class="text-sm text-gray-600 text-center">
                    AES-256 軍規加密
                  </p>
                </div>
                <div class="bg-white rounded-lg p-4 shadow-sm">
                  <div
                    class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-3 mx-auto"
                  >
                    <svg
                      class="w-6 h-6 text-green-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  </div>
                  <h4 class="font-bold text-center mb-2">隔離訪問</h4>
                  <p class="text-sm text-gray-600 text-center">
                    只有你能解密使用
                  </p>
                </div>
              </div>
            </div>

            <!-- 詳細說明 -->
            <div class="space-y-6">
              <div class="border-l-4 border-purple-500 pl-6">
                <h3 class="text-xl font-bold text-gray-900 mb-3">
                  🔐 1. AES-256 加密儲存
                </h3>
                <p class="text-gray-600 mb-3">
                  你的 API Key 在儲存到資料庫之前，會先經過
                  <strong>AES-256 加密演算法</strong
                  >處理。這是銀行和軍事等級使用的加密標準。
                </p>
                <div class="bg-gray-50 rounded-lg p-4 font-mono text-sm">
                  <p class="text-gray-500 mb-1">你輸入的 API Key：</p>
                  <p class="text-green-600 mb-3">AIzaSyABC123XYZ...</p>
                  <p class="text-gray-500 mb-1">資料庫中儲存的（加密後）：</p>
                  <p class="text-purple-600">8f7e6d5c4b3a2f1e9d8c7b6a5...</p>
                </div>
                <p class="text-sm text-gray-600 mt-3">
                  即使有人非法取得資料庫，看到的也只是無法解讀的亂碼。
                </p>
              </div>

              <div class="border-l-4 border-purple-500 pl-6">
                <h3 class="text-xl font-bold text-gray-900 mb-3">
                  🚫 2. 前端完全看不到
                </h3>
                <p class="text-gray-600 mb-3">
                  <strong>你的 API Key 永遠不會傳送到瀏覽器。</strong> 所有 AI
                  請求都是：
                </p>
                <div
                  class="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2 text-sm"
                >
                  <p>
                    1️⃣ 你的瀏覽器 →
                    我們的後端（<strong>只傳送你的請求內容</strong>）
                  </p>
                  <p>2️⃣ 我們的後端 → 解密 API Key → 呼叫 Gemini API</p>
                  <p>
                    3️⃣ Gemini API → 我們的後端 →
                    你的瀏覽器（<strong>只回傳結果</strong>）
                  </p>
                </div>
                <p class="text-sm text-gray-600 mt-3">
                  這代表：即使有人打開瀏覽器開發者工具（F12），也<strong>完全看不到</strong>你的
                  API Key。
                </p>
              </div>

              <div class="border-l-4 border-purple-500 pl-6">
                <h3 class="text-xl font-bold text-gray-900 mb-3">
                  👤 3. 嚴格的用戶隔離
                </h3>
                <p class="text-gray-600 mb-3">
                  資料庫設定了 <strong>Row Level Security (RLS)</strong>，確保：
                </p>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-start">
                    <span class="text-green-500 mr-2">✓</span>
                    <span
                      >每個用戶只能看到和使用<strong>自己的</strong> API
                      Keys</span
                    >
                  </li>
                  <li class="flex items-start">
                    <span class="text-green-500 mr-2">✓</span>
                    <span
                      >即使是網站管理員，也<strong>無法解密</strong>你的 API
                      Key（需要加密密鑰）</span
                    >
                  </li>
                  <li class="flex items-start">
                    <span class="text-green-500 mr-2">✓</span>
                    <span
                      >當你刪除帳號時，所有相關資料<strong
                        >自動永久刪除</strong
                      ></span
                    >
                  </li>
                </ul>
              </div>

              <div class="border-l-4 border-purple-500 pl-6">
                <h3 class="text-xl font-bold text-gray-900 mb-3">
                  🌐 4. HTTPS 加密傳輸
                </h3>
                <p class="text-gray-600">
                  所有資料傳輸都使用
                  <strong>HTTPS (TLS 1.3)</strong>
                  加密，防止中間人攻擊。你可以在瀏覽器網址列看到 🔒 鎖頭圖示。
                </p>
              </div>

              <div class="border-l-4 border-purple-500 pl-6">
                <h3 class="text-xl font-bold text-gray-900 mb-3">
                  📊 5. 透明的使用記錄
                </h3>
                <p class="text-gray-600 mb-3">
                  我們記錄每次 API
                  使用（時間、功能、是否成功），你可以隨時查看：
                </p>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-start">
                    <span class="text-blue-500 mr-2">•</span>
                    <span>偵測異常使用（如突然大量請求）</span>
                  </li>
                  <li class="flex items-start">
                    <span class="text-blue-500 mr-2">•</span>
                    <span>監控 API Key 使用量和剩餘額度</span>
                  </li>
                  <li class="flex items-start">
                    <span class="text-blue-500 mr-2">•</span>
                    <span>提供完整的使用統計</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 我們看不到什麼 -->
            <div class="mt-8 bg-red-50 border border-red-200 rounded-xl p-6">
              <h4 class="text-lg font-bold text-red-900 mb-3">
                ❌ 我們（開發者）看不到：
              </h4>
              <ul class="space-y-2 text-sm text-red-800">
                <li>• 你的 API Key 明文（資料庫只有加密後的亂碼）</li>
                <li>• 你輸入給 AI 的內容（我們不記錄請求內容）</li>
                <li>• AI 回覆給你的內容（我們不儲存回應資料）</li>
              </ul>
            </div>

            <!-- 我們能看到什麼 -->
            <div
              class="mt-4 bg-green-50 border border-green-200 rounded-xl p-6"
            >
              <h4 class="text-lg font-bold text-green-900 mb-3">
                ✓ 我們（開發者）能看到：
              </h4>
              <ul class="space-y-2 text-sm text-green-800">
                <li>• 你的 Email 和註冊時間（用於登入驗證）</li>
                <li>• API 使用次數和時間（用於統計和監控）</li>
                <li>• 你使用了哪些功能（如流程圖、地圖等）</li>
                <li>• 錯誤記錄（用於改善系統）</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 進階功能 -->
      <section id="features" class="mb-16 scroll-mt-20">
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-6">⚡ 進階功能</h2>

          <div class="space-y-6">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                多 API Key 管理
              </h3>
              <p class="text-gray-600">
                你可以新增多個 API Keys，系統會自動選擇最佳的 Key 來使用。當一個
                Key 的免費額度用盡時，會自動切換到下一個。
              </p>
            </div>

            <div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                使用額度監控
              </h3>
              <p class="text-gray-600">
                設定每個 API Key
                的每月使用上限，系統會顯示進度條提醒你。達到上限前會發出警告，避免超出預算。
              </p>
            </div>

            <div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                優先級設定
              </h3>
              <p class="text-gray-600">
                為不同的 API Keys 設定優先級，系統會優先使用數字小的
                Key。例如：優先用免費 Key，付費 Key 當備用。
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section id="faq" class="mb-16 scroll-mt-20">
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-8">❓ 常見問題</h2>

          <div class="space-y-6">
            <details class="group">
              <summary
                class="flex justify-between items-center cursor-pointer list-none p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span class="font-semibold text-gray-900"
                  >為什麼不直接提供 API Key，還要我自己申請？</span
                >
                <svg
                  class="w-5 h-5 text-gray-500 group-open:rotate-180 transition"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div class="p-4 text-gray-600">
                <p class="mb-2">主要有三個原因：</p>
                <ol class="list-decimal ml-6 space-y-1">
                  <li>
                    <strong>完全免費：</strong>如果使用我們的
                    Key，所有用戶共用額度，很快就會用完，我們需要收費才能維持
                  </li>
                  <li>
                    <strong>隱私保護：</strong>使用你自己的 Key，請求直接發送到
                    Google，我們看不到內容
                  </li>
                  <li>
                    <strong>無限制：</strong
                    >每個人都有自己的免費額度，不用擔心用不到
                  </li>
                </ol>
              </div>
            </details>

            <details class="group">
              <summary
                class="flex justify-between items-center cursor-pointer list-none p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span class="font-semibold text-gray-900"
                  >免費額度夠用嗎？</span
                >
                <svg
                  class="w-5 h-5 text-gray-500 group-open:rotate-180 transition"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div class="p-4 text-gray-600">
                <p>對大部分用戶來說，完全夠用！Gemini API 的免費額度是：</p>
                <ul class="list-disc ml-6 mt-2 space-y-1">
                  <li>每分鐘 15 次請求</li>
                  <li>每天 1,500 次請求</li>
                  <li>每月 50,000 次請求</li>
                </ul>
                <p class="mt-2">
                  除非你每天生成數百個圖表，否則免費額度綽綽有餘。
                </p>
              </div>
            </details>

            <details class="group">
              <summary
                class="flex justify-between items-center cursor-pointer list-none p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span class="font-semibold text-gray-900"
                  >你們會看到我的 API Key 嗎？</span
                >
                <svg
                  class="w-5 h-5 text-gray-500 group-open:rotate-180 transition"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div class="p-4 text-gray-600">
                <p>
                  <strong>看不到！</strong> 你的 API Key 會被 AES-256
                  加密後才儲存到資料庫。我們在資料庫看到的只是無法解讀的亂碼。只有在你使用功能時，系統才會在後端暫時解密來呼叫
                  API，用完立即銷毀，不會記錄明文。
                </p>
              </div>
            </details>

            <details class="group">
              <summary
                class="flex justify-between items-center cursor-pointer list-none p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span class="font-semibold text-gray-900"
                  >如果我不想用了，可以刪除 API Key 嗎？</span
                >
                <svg
                  class="w-5 h-5 text-gray-500 group-open:rotate-180 transition"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div class="p-4 text-gray-600">
                <p>
                  當然可以！前往「設定」頁面，點擊刪除按鈕即可。資料會立即從資料庫永久刪除。如果你刪除整個帳號，所有相關資料也會自動永久刪除。
                </p>
              </div>
            </details>

            <details class="group">
              <summary
                class="flex justify-between items-center cursor-pointer list-none p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span class="font-semibold text-gray-900"
                  >可以在多台電腦使用嗎？</span
                >
                <svg
                  class="w-5 h-5 text-gray-500 group-open:rotate-180 transition"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div class="p-4 text-gray-600">
                <p>
                  可以！只要登入同一個帳號，你的 API Keys
                  和所有設定都會自動同步。在家裡設定好，到辦公室或學校登入就能直接使用。
                </p>
              </div>
            </details>
          </div>
        </div>
      </section>

      <!-- 聯絡資訊 -->
      <section id="contact" class="scroll-mt-20">
        <div
          class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white text-center"
        >
          <h2 class="text-3xl font-bold mb-4">還有問題？</h2>
          <p class="text-blue-100 mb-6">
            我們很樂意幫助你！歡迎透過以下方式聯絡我們
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://github.com/redpiigpig/know-graph-lab/issues"
              target="_blank"
              class="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition font-semibold"
            >
              GitHub Issues
            </a>
            <a
              href="https://github.com/redpiigpig/know-graph-lab"
              target="_blank"
              class="px-6 py-3 border-2 border-white text-white rounded-lg hover:bg-white/10 transition font-semibold"
            >
              查看文檔
            </a>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-8">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <p>&copy; 2026 Know Graph Lab. Made with ❤️ by the community.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: "使用指南 - Know Graph Lab",
  meta: [
    {
      name: "description",
      content:
        "完整的使用教學與資安說明。了解如何取得 Gemini API Key、我們如何保護你的資料，以及常見問題解答。",
    },
  ],
});
</script>
