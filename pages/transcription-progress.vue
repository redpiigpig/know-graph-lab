<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader title="轉錄與翻譯進度" :back="{ to: '/', label: '返回主頁' }" />
    <div class="max-w-5xl mx-auto px-4 py-8">
      <!-- 面板本體共用 /ebook 圖書館頁嵌入的同一元件 -->
      <EbookTranscriptionProgressPanel />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ title: "轉錄與翻譯進度" });
</script>
