<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center p-4"
  >
    <div class="max-w-md w-full">
      <!-- Logo 區 -->
      <div class="text-center mb-8">
        <img
          src="/images/logo-icon.svg"
          alt="Logo"
          class="w-20 h-20 mx-auto mb-4"
        />
        <h1 class="text-3xl font-bold text-gray-900">Know Graph Lab</h1>
        <p class="text-gray-600 mt-2">登入以開始使用 AI 圖表工具</p>
      </div>

      <!-- 登入表單 -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              密碼
            </label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="至少 6 個字元"
            />
          </div>

          <button
            type="submit"
            class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            {{ loading ? "登入中..." : "登入" }}
          </button>
        </form>

        <!-- 註冊連結 -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            還沒有帳號？
            <NuxtLink
              to="/signup"
              class="text-blue-600 hover:underline font-medium"
            >
              立即註冊
            </NuxtLink>
          </p>
        </div>

        <!-- 錯誤訊息 -->
        <div
          v-if="error"
          class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-sm text-red-600">{{ error }}</p>
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
const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const supabase = useSupabaseClient();
const user = useSupabaseUser();
const router = useRouter();

// 如果已登入，重導向到設定頁
watchEffect(() => {
  if (user.value) {
    router.push("/settings");
  }
});

async function handleLogin() {
  loading.value = true;
  error.value = "";

  const { error: loginError } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  });

  loading.value = false;

  if (loginError) {
    error.value =
      loginError.message === "Invalid login credentials"
        ? "Email 或密碼錯誤"
        : loginError.message;
  } else {
    router.push("/settings");
  }
}
</script>
