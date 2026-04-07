<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center p-4"
  >
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <img
          src="/images/logo-icon.svg"
          alt="Logo"
          class="w-20 h-20 mx-auto mb-4"
        />
        <h1 class="text-3xl font-bold text-gray-900">建立帳號</h1>
        <p class="text-gray-600 mt-2">免費註冊，立即開始使用</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleSignup" class="space-y-5">
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
              minlength="6"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="至少 6 個字元"
            />
            <p class="text-xs text-gray-500 mt-1">密碼必須至少 6 個字元</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              確認密碼
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="再次輸入密碼"
            />
          </div>

          <button
            type="submit"
            class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            :disabled="loading"
          >
            {{ loading ? "註冊中..." : "註冊" }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            已經有帳號？
            <NuxtLink
              to="/login"
              class="text-blue-600 hover:underline font-medium"
            >
              立即登入
            </NuxtLink>
          </p>
        </div>

        <div
          v-if="error"
          class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div
          v-if="success"
          class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <p class="text-sm text-green-700">{{ success }}</p>
        </div>
      </div>

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
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

const supabase = useSupabaseClient();
const router = useRouter();

async function handleSignup() {
  loading.value = true;
  error.value = "";
  success.value = "";

  // 驗證密碼
  if (password.value !== confirmPassword.value) {
    error.value = "密碼不一致";
    loading.value = false;
    return;
  }

  if (password.value.length < 6) {
    error.value = "密碼必須至少 6 個字元";
    loading.value = false;
    return;
  }

  const { error: signupError } = await supabase.auth.signUp({
    email: email.value,
    password: password.value,
  });

  loading.value = false;

  if (signupError) {
    error.value = signupError.message;
  } else {
    success.value = "註冊成功！請檢查您的 Email 以驗證帳號。";
    setTimeout(() => {
      router.push("/login");
    }, 2000);
  }
}
</script>
