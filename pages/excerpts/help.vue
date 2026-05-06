<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/excerpts" class="text-gray-500 hover:text-blue-600 text-sm transition">← 書摘庫</NuxtLink>
          <span class="text-gray-300">·</span>
          <span class="font-semibold text-sm">使用說明</span>
        </div>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-12">
      <header class="mb-16">
        <div class="text-6xl mb-4">📑</div>
        <h1 class="text-4xl font-bold tracking-tight mb-3">書摘庫</h1>
        <p class="text-lg text-gray-600 leading-relaxed">
          從電子書直接畫線存進來，自動建書、按章節分組、產出引用 markdown。<br />
          也可以手動新增、批次匯入 CSV、上傳照片 OCR。
        </p>
      </header>

      <!-- Feature cards -->
      <section class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-600">✦</span> 功能總覽
        </h2>
        <div class="grid sm:grid-cols-2 gap-4">
          <div v-for="f in features" :key="f.title"
            class="bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-sm transition">
            <div class="text-3xl mb-2">{{ f.icon }}</div>
            <h3 class="font-semibold text-base mb-1.5">{{ f.title }}</h3>
            <p class="text-sm text-gray-500 leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </section>

      <!-- Walkthroughs -->
      <section v-for="(walk, idx) in walkthroughs" :key="walk.title" class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-600">{{ ['①','②','③','④'][idx] }}</span> {{ walk.title }}
        </h2>
        <ol class="space-y-3">
          <li v-for="step in walk.steps" :key="step.title"
            class="flex gap-4 bg-white border border-gray-200 rounded-xl p-4">
            <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm flex-shrink-0">
              {{ step.n }}
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-sm mb-0.5">{{ step.title }}</h4>
              <p class="text-sm text-gray-500 leading-relaxed">{{ step.body }}</p>
            </div>
          </li>
        </ol>
      </section>

      <!-- Markdown export sample -->
      <section class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-600">✦</span> Markdown 匯出長這樣
        </h2>
        <div class="bg-white border border-gray-200 rounded-xl p-5 text-sm">
          <p class="text-gray-500 mb-3">點 /excerpts/library/[bookId] 工具列「📋 匯出 Markdown」會得到（同時複製到剪貼簿 + 下載 .md）：</p>
          <pre class="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto leading-relaxed text-xs">
# 希臘羅馬神話

**伊迪絲．漢彌敦, 餘淑慧 譯, (2015). 漫遊者文化**

> 原書：Edith Hamilton, *Mythology*, (1942), Little, Brown


## 第一部 · 眾神、創世、早期英雄

### 開場引言

> 神話世界並不是一個美麗的世界，而是一個充滿恐怖的世界。
>
> ——《希臘羅馬神話》，第一部，第 12 段</pre>
        </div>
      </section>

      <!-- Tips -->
      <section class="mb-16">
        <h2 class="text-xl font-semibold mb-5 flex items-center gap-2">
          <span class="text-blue-600">✦</span> 實用小撇步
        </h2>
        <div class="space-y-3">
          <div v-for="tip in tips" :key="tip.title"
            class="flex gap-3 bg-blue-50 border border-blue-100 rounded-xl p-4">
            <div class="text-2xl flex-shrink-0">{{ tip.icon }}</div>
            <div class="flex-1">
              <h4 class="font-semibold text-sm text-blue-900 mb-0.5">{{ tip.title }}</h4>
              <p class="text-sm text-gray-600 leading-relaxed">{{ tip.body }}</p>
            </div>
          </div>
        </div>
      </section>

      <p class="text-center text-xs text-gray-400 pt-8">
        有疑問或想加功能？直接跟工程師說。
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ title: "書摘庫使用說明" });

const features = [
  { icon: "📥", title: "從電子書一鍵存",
    desc: "在 /ebook 讀書時選文字 → 點藍色「+ 書摘」→ 自動建書 + 入庫，帶章節 + 頁數。" },
  { icon: "📚", title: "按書本分類",
    desc: "/excerpts/library 按書分頁。每本書有完整 metadata + 章節分組。" },
  { icon: "🏷️", title: "標籤組織",
    desc: "書本層 + 書摘層都可貼 tag。Sidebar / chip 過濾跨書找書摘。" },
  { icon: "📋", title: "Markdown 匯出",
    desc: "完整書目資料 + 章節分組 + 引用尾巴。寫論文直接貼。" },
  { icon: "📷", title: "照片 OCR",
    desc: "拍書頁上傳，自動 OCR 為書摘。" },
  { icon: "📊", title: "CSV 批次匯入",
    desc: "舊筆記從 Notion / Excel 匯出後一次塞進來。" },
  { icon: "🔍", title: "全書內搜尋",
    desc: "在單本書頁面有獨立搜尋，可按欄位（標題／內容）篩選。" },
  { icon: "📥", title: "匯入寫作計畫",
    desc: "每筆書摘旁有 📥 鈕，可推到指定的「待寫著作」或「待寫文章」。" },
];

const walkthroughs = [
  {
    title: "從電子書到書摘庫（最常用）",
    steps: [
      { n: "1", title: "在 /ebook 開一本書",      body: "左欄選書、上方搜尋、或從「閱讀中」清單。" },
      { n: "2", title: "選一段想存的文字",         body: "正常的滑鼠選字。" },
      { n: "3", title: "點藍色「+ 書摘」按鈕",     body: "選字工具列右邊那個。" },
      { n: "4", title: "命名標題（必填）",         body: "Modal 打開後輸入一個短標題；可挑螢光色。" },
      { n: "5", title: "送出",                     body: "後端自動：建書（如果沒建過）→ 插書摘 → 連 annotation。" },
      { n: "6", title: "回 /excerpts/library 看",  body: "書會自動出現，書摘按章節分組。" },
    ],
  },
  {
    title: "手動新增書摘 / 批次",
    steps: [
      { n: "A", title: "+ 新增書籍",   body: "右上「+ 新增書籍」填基本欄位（標題、作者、出版社、年份）。" },
      { n: "B", title: "+ 新增文摘",   body: "進入書頁後右上「+ 新增文摘」。可填章節 + 頁碼。" },
      { n: "C", title: "上傳照片",     body: "拍書頁 → OCR 為書摘文字。" },
      { n: "D", title: "上傳 CSV",     body: "從舊筆記平台匯出 → 規格按 import-csv API 文件。" },
    ],
  },
  {
    title: "用標籤跨書整理",
    steps: [
      { n: "1", title: "進入任一本書頁",    body: "/excerpts/library/[bookId]。" },
      { n: "2", title: "在書本卡片下加 tag", body: "點「+ 標籤」→ 打字 → Enter 自動建。" },
      { n: "3", title: "在每筆書摘上加 tag", body: "書摘卡片內也有獨立的 picker。" },
      { n: "4", title: "回 /excerpts/library 用 tag chip 過濾", body: "或在 /ebook 左欄「標籤」section 直接點。" },
    ],
  },
];

const tips = [
  { icon: "🔄", title: "頁面回到前景會自動更新",
    body: "在 /ebook 新增書摘後切回 /excerpts/library，書摘數會自動 refresh，不用 reload。" },
  { icon: "📝", title: "點任一欄位都可以直接改",
    body: "書名、作者、譯者、出版社等所有欄位都是 InlineEdit — 點兩下進入編輯。" },
  { icon: "📌", title: "未分章 = 章節欄沒填",
    body: "從電子書帶進來的書摘已自動帶章節；手動新增的記得填，否則會落到「未分章」。" },
  { icon: "🎨", title: "tag 顏色尚未支援",
    body: "schema 已留 color 欄，未來可在 picker 加色票。目前統一藍色。" },
];
</script>
