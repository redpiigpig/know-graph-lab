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
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition pr-12"
                placeholder="至少 6 個字元"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <!-- 顯示圖示（眼睛開） -->
                <svg
                  v-if="showPassword"
                  class="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <!-- 隱藏圖示（眼睛關） -->
                <svg
                  v-else
                  class="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            {{ loading ? "登入中..." : "登入" }}
          </button>
        </form>

        <!-- 忘記密碼連結 -->
        <div class="mt-4 text-center">
          <NuxtLink
            to="/forgot-password"
            class="text-sm text-blue-600 hover:underline"
          >
            忘記密碼？
          </NuxtLink>
        </div>

        <!-- 分隔線 -->
        <div class="my-6 flex items-center">
          <div class="flex-1 border-t border-gray-300"></div>
          <span class="px-4 text-sm text-gray-500">或</span>
          <div class="flex-1 border-t border-gray-300"></div>
        </div>

        <!-- 第三方登入按鈕 -->
        <div class="space-y-3">
          <button
            @click="signInWithGoogle"
            type="button"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center justify-center space-x-3"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span class="font-medium text-gray-700">使用 Google 登入</span>
          </button>

          <button
            @click="signInWithFacebook"
            type="button"
            class="w-full px-4 py-3 bg-[#1877F2] text-white rounded-lg hover:bg-[#166FE5] transition flex items-center justify-center space-x-3"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
              />
            </svg>
            <span class="font-medium">使用 Facebook 登入</span>
          </button>
        </div>

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
const showPassword = ref(false);
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

// Email 登入
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

// Google 登入
async function signInWithGoogle() {
  const { error: oauthError } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  });

  if (oauthError) {
    error.value = "Google 登入失敗：" + oauthError.message;
  }
}

// Facebook 登入
async function signInWithFacebook() {
  const { error: oauthError } = await supabase.auth.signInWithOAuth({
    provider: "facebook",
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  });

  if (oauthError) {
    error.value = "Facebook 登入失敗：" + oauthError.message;
  }
}
</script>
