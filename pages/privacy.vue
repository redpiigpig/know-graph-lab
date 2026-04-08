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
      <h1 class="text-4xl font-bold text-gray-900 mb-8">隱私政策</h1>

      <div
        class="bg-white rounded-xl shadow-sm border p-8 prose prose-blue max-w-none"
      >
        <p class="text-sm text-gray-500 mb-6">
          最後更新日期：{{ new Date().toLocaleDateString("zh-TW") }}
        </p>

        <h2>1. 資料收集</h2>
        <p>我們收集以下類型的資料：</p>

        <h3>1.1 您主動提供的資料</h3>
        <ul>
          <li>
            <strong>帳號資訊：</strong>Email、姓名或暱稱、學術領域、年齡層
          </li>
          <li>
            <strong>API Keys：</strong>您提供的 AI 服務商 API Key（加密儲存）
          </li>
          <li><strong>使用者內容：</strong>您建立的圖表、專案資料</li>
        </ul>

        <h3>1.2 自動收集的資料</h3>
        <ul>
          <li><strong>使用記錄：</strong>API 呼叫次數、時間、功能使用情況</li>
          <li><strong>技術資訊：</strong>IP 位址、瀏覽器類型、作業系統</li>
        </ul>

        <h2>2. 資料使用</h2>
        <p>我們使用收集的資料用於：</p>
        <ul>
          <li>提供和改善服務功能</li>
          <li>處理您的請求和交易</li>
          <li>發送重要通知（如驗證郵件、服務更新）</li>
          <li>分析使用趨勢以改善使用者體驗</li>
          <li>預防詐欺和濫用行為</li>
        </ul>

        <h2>3. API Key 安全</h2>
        <p>關於您的 API Key，我們採取以下措施：</p>
        <ul>
          <li><strong>加密儲存：</strong>使用 AES-256 加密演算法</li>
          <li><strong>傳輸加密：</strong>所有資料傳輸均使用 HTTPS/TLS</li>
          <li>
            <strong>存取控制：</strong>您的 API Key
            只有您能使用，其他使用者無法存取
          </li>
          <li>
            <strong>不對外暴露：</strong>API Key
            永遠不會傳送到前端或暴露給第三方
          </li>
          <li><strong>您的控制權：</strong>您可以隨時刪除或更換 API Key</li>
        </ul>

        <h2>4. 資料分享</h2>
        <p>
          我們<strong>不會</strong>出售您的個人資料。我們只在以下情況分享資料：
        </p>
        <ul>
          <li>
            <strong>服務提供商：</strong
            >Supabase（資料庫）、Zeabur（託管）、Resend（郵件服務）
          </li>
          <li><strong>法律要求：</strong>當法律要求我們揭露資料時</li>
          <li><strong>經您同意：</strong>在獲得您明確同意的情況下</li>
        </ul>

        <h2>5. 第三方服務</h2>
        <p>本服務整合以下第三方服務：</p>
        <ul>
          <li><strong>Supabase：</strong>資料庫和身份驗證服務</li>
          <li>
            <strong>Google Gemini API：</strong>AI 生成功能（使用您自己的 API
            Key）
          </li>
          <li><strong>Resend：</strong>郵件發送服務</li>
        </ul>
        <p>這些服務提供商有各自的隱私政策，建議您查閱了解。</p>

        <h2>6. 您的權利</h2>
        <p>您有以下權利：</p>
        <ul>
          <li><strong>存取權：</strong>查看我們持有的您的個人資料</li>
          <li><strong>修改權：</strong>更新或修正您的個人資料</li>
          <li><strong>刪除權：</strong>要求刪除您的帳號和所有相關資料</li>
          <li><strong>匯出權：</strong>要求匯出您的資料</li>
          <li><strong>反對權：</strong>反對某些資料處理方式</li>
        </ul>

        <h2>7. 資料保留</h2>
        <p>我們會保留您的資料直到：</p>
        <ul>
          <li>您刪除帳號</li>
          <li>服務終止</li>
          <li>法律要求的最短保留期限結束</li>
        </ul>
        <p>
          當您刪除帳號時，我們會在 30
          天內永久刪除您的所有個人資料（法律要求保留的除外）。
        </p>

        <h2>8. Cookies 和追蹤技術</h2>
        <p>我們使用以下技術：</p>
        <ul>
          <li><strong>必要 Cookies：</strong>用於身份驗證和基本功能</li>
          <li><strong>功能性 Cookies：</strong>記住您的偏好設定</li>
          <li><strong>分析工具：</strong>了解服務使用情況（匿名化）</li>
        </ul>

        <h2>9. 兒童隱私</h2>
        <p>
          本服務不針對 18 歲以下的兒童。如果我們發現收集了兒童的個人資料，
          會立即刪除。
        </p>

        <h2>10. 國際資料傳輸</h2>
        <p>
          您的資料可能會儲存和處理在不同國家/地區的伺服器上。
          我們會確保這些資料傳輸符合適用的資料保護法規。
        </p>

        <h2>11. 隱私政策更新</h2>
        <p>
          我們可能會不時更新本隱私政策。重大變更會透過 Email 或網站公告通知您。
          繼續使用服務即表示您接受更新後的隱私政策。
        </p>

        <h2>12. 聯絡我們</h2>
        <p>
          如對本隱私政策有任何疑問或要行使您的權利，請透過以下方式聯絡我們：
        </p>
        <ul>
          <li>
            GitHub Issues:
            <a
              href="https://github.com/redpiigpig/know-graph-lab/issues"
              target="_blank"
              class="text-blue-600 hover:underline"
            >
              https://github.com/redpiigpig/know-graph-lab/issues
            </a>
          </li>
        </ul>
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
  title: "隱私政策 - Know Graph Lab",
  meta: [
    {
      name: "description",
      content:
        "Know Graph Lab 隱私政策。了解我們如何收集、使用和保護您的個人資料。",
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

.prose h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #374151;
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
