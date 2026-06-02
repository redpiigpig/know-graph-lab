<template>
  <PhotoFolderBrowser />
</template>

<script setup lang="ts">
// 巢狀資料夾：/photos/training/<event>/<sub>...（required catch-all，至少一段）
// 與同層 index.vue 一起涵蓋「相簿根 + 任意深度子資料夾」。
definePageMeta({ middleware: 'auth' });
</script>
