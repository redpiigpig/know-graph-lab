<template>
  <PhotoFolderBrowser />
</template>

<script setup lang="ts">
// 相簿根：/photos/training、/photos/hongshi
// （取代原本 [[...path]].vue —— optional catch-all 在 [lib]/ 下不會產生路由，導致 404）
definePageMeta({ middleware: 'auth' });
</script>
