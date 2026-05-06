<template>
  <div class="min-h-screen bg-gray-950 text-white">
    <nav class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/ebook" class="text-gray-400 hover:text-white text-sm transition">← 電子圖書館</NuxtLink>
          <span class="text-gray-600">·</span>
          <span class="font-semibold text-sm">使用說明</span>
        </div>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-12">
      <header class="mb-16">
        <div class="text-6xl mb-4">📚</div>
        <h1 class="text-4xl font-bold tracking-tight mb-3">電子圖書館</h1>
        <p class="text-lg text-gray-400 leading-relaxed">
          收藏、閱讀、整理你的 EPUB 與 PDF。<br />
          標記閱讀進度，劃重點，自動產出書摘。
        </p>
      </header>

      <!-- Feature cards -->
      <section class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-400">✦</span> 功能總覽
        </h2>
        <div class="grid sm:grid-cols-2 gap-4">
          <div v-for="f in features" :key="f.title"
            class="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-blue-700 transition">
            <div class="text-3xl mb-2">{{ f.icon }}</div>
            <h3 class="font-semibold text-base mb-1.5">{{ f.title }}</h3>
            <p class="text-sm text-gray-400 leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </section>

      <!-- Walkthroughs -->
      <section v-for="(walk, idx) in walkthroughs" :key="walk.title" class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-400">{{ ['①','②','③','④'][idx] }}</span> {{ walk.title }}
        </h2>
        <ol class="space-y-3">
          <li v-for="step in walk.steps" :key="step.title"
            class="flex gap-4 bg-gray-900/50 border border-gray-800 rounded-xl p-4">
            <div class="w-8 h-8 rounded-full bg-blue-900 text-blue-300 flex items-center justify-center font-bold text-sm flex-shrink-0">
              {{ step.n }}
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-sm mb-0.5">{{ step.title }}</h4>
              <p class="text-sm text-gray-400 leading-relaxed">{{ step.body }}</p>
            </div>
          </li>
        </ol>
      </section>

      <!-- Tips -->
      <section class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-400">✦</span> 實用小撇步
        </h2>
        <div class="space-y-3">
          <div v-for="tip in tips" :key="tip.title"
            class="flex gap-3 bg-blue-950/30 border border-blue-900/50 rounded-xl p-4">
            <div class="text-2xl flex-shrink-0">{{ tip.icon }}</div>
            <div class="flex-1">
              <h4 class="font-semibold text-sm text-blue-200 mb-0.5">{{ tip.title }}</h4>
              <p class="text-sm text-gray-400 leading-relaxed">{{ tip.body }}</p>
            </div>
          </div>
        </div>
      </section>

      <p class="text-center text-xs text-gray-600 pt-8">
        有疑問或想加功能？直接跟工程師說。
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ title: "電子圖書館使用說明" });

const features = [
  { icon: "📤", title: "上傳電子書",
    desc: "拖放 PDF 或 EPUB 即可加入。系統會自動標準化（s2tw、章節抽取、出版資訊）。" },
  { icon: "🗂️", title: "分類瀏覽",
    desc: "左側 9 大分類 + 子分類；按分類點擊就會切換 URL，可以加書籤分享。" },
  { icon: "🏷️", title: "標籤",
    desc: "跨分類的網狀組織。一本書可貼多個 tag，例如「博論用」「待查證」。" },
  { icon: "📖", title: "我的書櫃",
    desc: "把書標為「閱讀中」或「已讀」，快速回到正在讀的書。" },
  { icon: "📅", title: "今日讀到這裡",
    desc: "閱讀中時可以戳當天的進度書籤。下次重開書會自動跳到那一段。" },
  { icon: "✏️", title: "畫線 + 註記",
    desc: "4 色螢光筆 + 文字註記，直接在書頁上保留。" },
  { icon: "📥", title: "存為書摘",
    desc: "畫線後點「+ 書摘」一鍵存入書摘庫，自動建書、帶章節、帶頁數。" },
  { icon: "🔍", title: "全文搜尋",
    desc: "跨書搜尋書名、作者、或書中內文。命中段落直接點進閱讀。" },
];

const walkthroughs = [
  {
    title: "閱讀工作流",
    steps: [
      { n: "1", title: "從書庫挑一本書點進去", body: "左側分類過濾、上方搜尋、或直接點封面。" },
      { n: "2", title: "加入書櫃",            body: "工具列右上 📚 按鈕點一下變 📖 閱讀中。" },
      { n: "3", title: "一邊讀一邊畫線",       body: "選文字 → 4 色螢光筆任挑、或加註記。" },
      { n: "4", title: "把重點存為書摘",       body: "選文字後點藍色「+ 書摘」→ 命名標題 → 自動入書摘庫。" },
      { n: "5", title: "今天讀完戳個書籤",     body: "工具列「📅 今日讀到這裡」按一下。下次開書自動跳回來。" },
      { n: "6", title: "讀完標已讀",           body: "工具列 📖 點到 ✅ 已讀。書櫃會分流。下次開不再自動跳轉。" },
    ],
  },
  {
    title: "組織書籍",
    steps: [
      { n: "A", title: "按分類過濾",   body: "左欄點任一個分類 → URL 變成 ?category=哲學 → 可分享連結。" },
      { n: "B", title: "按子分類過濾", body: "展開分類後點子分類，URL 跟過濾同步。" },
      { n: "C", title: "按標籤過濾",   body: "先到 /excerpts/library 給書貼上 tag，回 /ebook 左欄會自動出現「標籤」section。" },
      { n: "D", title: "按閱讀狀態過濾", body: "左欄「我的書櫃」下的「📖 閱讀中」「✅ 已讀」即是。" },
    ],
  },
];

const tips = [
  { icon: "↩️", title: "瀏覽器上一頁不會跳到頂",
    body: "從書頁按上一頁回 /ebook 會自動回到剛才滑到的位置。" },
  { icon: "🔗", title: "任一視圖都可加書籤分享",
    body: "?category=哲學、?subcategory=哲學/近代哲學、?tag=xxx、?shelf=reading 全部都是 stable URL。" },
  { icon: "🏷️", title: "Tag 自動建立",
    body: "在書摘頁的標籤輸入框打字 + Enter，沒有的 tag 直接創。" },
  { icon: "📅", title: "紫色日期條",
    body: "閱讀器目錄裡，標過書籤的章節會出現 📅 5/6 標記。滑鼠移過去顯示 × 可以刪。" },
];
</script>
