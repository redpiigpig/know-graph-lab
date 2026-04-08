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
        <h1 class="text-3xl font-bold text-gray-900">忘記密碼</h1>
        <p class="text-gray-600 mt-2">輸入你的 Email，我們會發送重設連結給你</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form
          v-if="!sent"
          @submit.prevent="handleForgotPassword"
          class="space-y-5"
        >
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

          <button
            type="submit"
            class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            :disabled="loading"
          >
            {{ loading ? "發送中..." : "發送重設連結" }}
          </button>
        </form>

        <!-- 成功訊息 -->
        <div v-if="sent" class="text-center py-8">
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
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">郵件已發送！</h3>
          <p class="text-gray-600 mb-6">
            請檢查你的 Email 收件匣（{{ email }}），點擊重設密碼連結。
          </p>
          <p class="text-sm text-gray-500 mb-4">沒收到郵件？</p>
          <button
            @click="sent = false"
            class="text-blue-600 hover:underline text-sm"
          >
            重新發送
          </button>
        </div>

        <!-- 返回登入 -->
        <div class="mt-6 text-center">
          <NuxtLink
            to="/login"
            class="text-sm text-gray-600 hover:text-blue-600 transition"
          >
            ← 返回登入
          </NuxtLink>
        </div>

        <!-- 錯誤訊息 -->
        <div
          v-if="error"
          class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const email = ref("");
const loading = ref(false);
const error = ref("");
const sent = ref(false);

const supabase = useSupabaseClient();
const config = useRuntimeConfig();

async function handleForgotPassword() {
  loading.value = true;
  error.value = "";

  const { error: resetError } = await supabase.auth.resetPasswordForEmail(
    email.value,
    {
      redirectTo: `${config.public.appUrl}/reset-password`,
    },
  );

  loading.value = false;

  if (resetError) {
    error.value = resetError.message;
  } else {
    sent.value = true;
  }
}

useHead({
  title: "忘記密碼 - Know Graph Lab",
});
</script>
