<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄 -->
    <nav class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <NuxtLink to="/" class="flex items-center space-x-3">
            <img src="/images/logo-icon.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold">Know Graph Lab</span>
          </NuxtLink>
          <NuxtLink to="/" class="text-gray-600 hover:text-blue-600">
            返回首頁
          </NuxtLink>
        </div>
      </div>
    </nav>

    <!-- 內容 -->
    <div class="max-w-4xl mx-auto px-4 py-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-8">服務條款</h1>

      <div
        class="bg-white rounded-xl shadow-sm border p-8 prose prose-blue max-w-none"
      >
        <p class="text-sm text-gray-500 mb-6">
          最後更新日期：{{ new Date().toLocaleDateString("zh-TW") }}
        </p>

        <h2>1. 服務說明</h2>
        <p>
          Know Graph Lab（以下簡稱「本服務」）是一個 AI
          驅動的知識視覺化工具平台，
          提供流程圖、心智圖、地圖標記、譜系圖等多種圖表生成服務。
        </p>

        <h2>2. 使用者帳號</h2>
        <p>使用本服務需要註冊帳號。您同意：</p>
        <ul>
          <li>提供真實、準確的註冊資訊</li>
          <li>妥善保管您的帳號密碼</li>
          <li>對您帳號下的所有活動負責</li>
          <li>如發現帳號遭未授權使用，應立即通知我們</li>
        </ul>

        <h2>3. API Key 使用</h2>
        <p>本服務採用「使用者自備 API Key」模式：</p>
        <ul>
          <li>您需要提供自己的 AI 服務提供商（如 Google Gemini）API Key</li>
          <li>您的 API Key 會經過加密後儲存</li>
          <li>您自行負責 API Key 的使用費用和額度管理</li>
          <li>我們不對您的 API Key 使用產生的費用負責</li>
        </ul>

        <h2>4. 資料隱私</h2>
        <p>
          我們重視您的隱私。關於資料收集和使用的詳細資訊， 請參閱我們的<NuxtLink
            to="/privacy"
            class="text-blue-600 hover:underline"
            >隱私政策</NuxtLink
          >。
        </p>

        <h2>5. 使用限制</h2>
        <p>您同意不會：</p>
        <ul>
          <li>使用本服務進行非法活動</li>
          <li>侵犯他人的智慧財產權</li>
          <li>散布惡意軟體或進行網路攻擊</li>
          <li>濫用或試圖破壞本服務的運作</li>
          <li>未經授權存取其他使用者的帳號或資料</li>
        </ul>

        <h2>6. 智慧財產權</h2>
        <p>
          您使用本服務生成的內容歸您所有。本服務的程式碼、設計、商標等智慧財產權歸
          Know Graph Lab 所有。
        </p>

        <h2>7. 免責聲明</h2>
        <p>本服務按「現狀」提供，不保證：</p>
        <ul>
          <li>服務不會中斷或無錯誤</li>
          <li>AI 生成的內容完全準確或適用於您的特定用途</li>
          <li>資料不會遺失（建議您自行備份重要資料）</li>
        </ul>

        <h2>8. 服務變更與終止</h2>
        <p>
          我們保留隨時修改、暫停或終止本服務的權利。
          我們會盡力提前通知重大變更，但不保證一定會通知。
        </p>

        <h2>9. 條款修訂</h2>
        <p>
          我們可能會不時更新這些條款。更新後的條款將在本頁面發布，
          並在頁首標註最後更新日期。繼續使用本服務即表示您接受修訂後的條款。
        </p>

        <h2>10. 聯絡方式</h2>
        <p>
          如對本服務條款有任何疑問，請透過
          <a
            href="https://github.com/redpiigpig/know-graph-lab/issues"
            target="_blank"
            class="text-blue-600 hover:underline"
          >
            GitHub Issues
          </a>
          聯絡我們。
        </p>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-8 mt-12">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <p>&copy; 2026 Know Graph Lab. Made with ❤️ by the community.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: "服務條款 - Know Graph Lab",
  meta: [
    {
      name: "description",
      content: "Know Graph Lab 服務條款。了解使用本服務的規範和權利義務。",
    },
  ],
});
</script>

<style scoped>
.prose h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #1f2937;
}

.prose p {
  margin-bottom: 1rem;
  line-height: 1.75;
  color: #4b5563;
}

.prose ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
  list-style-type: disc;
}

.prose li {
  margin-bottom: 0.5rem;
  color: #4b5563;
}
</style>
