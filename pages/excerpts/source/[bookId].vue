<script setup lang="ts">
// Redirect old /excerpts/source/:bookId → /excerpts/library/:bookId
const route = useRoute();
const router = useRouter();
onMounted(() => {
  router.replace(`/excerpts/library/${route.params.bookId}`);
});
</script>
<template><div></div></template>
