<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center"
  >
    <div class="text-center">
      <div
        class="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
      ></div>
      <p class="text-gray-600">登入中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter();
const user = useSupabaseUser();

// 等待用戶資料載入
watchEffect(() => {
  if (user.value) {
    router.push("/settings");
  }
});
</script>
