<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center p-4"
  >
    <div class="max-w-md w-full">
      <div class="bg-white rounded-2xl shadow-xl p-8 text-center">
        <!-- Loading 狀態 -->
        <div v-if="loading" class="py-8">
          <div
            class="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
          ></div>
          <p class="text-gray-600">驗證中...</p>
        </div>

        <!-- 成功 -->
        <div v-else-if="success" class="py-8">
          <div
            class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-8 h-8 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">驗證成功！</h2>
          <p class="text-gray-600 mb-6">
            你的 Email 已成功驗證，現在可以登入了。
          </p>
          <NuxtLink
            to="/login"
            class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            前往登入
          </NuxtLink>
        </div>

        <!-- 錯誤 -->
        <div v-else-if="error" class="py-8">
          <div
            class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-8 h-8 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">驗證失敗</h2>
          <p class="text-gray-600 mb-6">{{ error }}</p>
          <div class="space-y-3">
            <NuxtLink
              to="/signup"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              重新註冊
            </NuxtLink>
            <br />
            <NuxtLink to="/login" class="text-sm text-blue-600 hover:underline">
              已有帳號？直接登入
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- 返回首頁 -->
      <div class="text-center mt-6">
        <NuxtLink
          to="/"
          class="text-sm text-gray-600 hover:text-blue-600 transition"
        >
          ← 返回首頁
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const loading = ref(true);
const success = ref(false);
const error = ref("");

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    error.value = "缺少驗證 token，請檢查 Email 中的連結是否完整";
    loading.value = false;
    return;
  }

  try {
    await $fetch("/api/auth/verify", {
      method: "POST",
      body: { token },
    });

    success.value = true;
  } catch (err: any) {
    error.value = err.data?.message || "驗證失敗，請聯絡客服或重新註冊";
  } finally {
    loading.value = false;
  }
});

useHead({
  title: "驗證 Email - Know Graph Lab",
});
</script>
