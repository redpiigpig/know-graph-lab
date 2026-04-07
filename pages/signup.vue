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
        <p class="text-gray-600 mt-2">
          加入 Know Graph Lab，開始你的知識視覺化之旅
        </p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleSignup" class="space-y-5">
          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="your@email.com"
            />
          </div>

          <!-- 姓名/暱稱 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              姓名或暱稱 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.displayName"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="你的姓名或暱稱"
            />
          </div>

          <!-- 學術領域 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              學術專業領域
            </label>
            <select
              v-model="formData.academicField"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            >
              <option value="">請選擇...</option>
              <option value="computer_science">資訊科學</option>
              <option value="engineering">工程學</option>
              <option value="natural_sciences">自然科學</option>
              <option value="social_sciences">社會科學</option>
              <option value="humanities">人文學科</option>
              <option value="medicine">醫學</option>
              <option value="business">商學</option>
              <option value="education">教育學</option>
              <option value="arts">藝術</option>
              <option value="law">法律</option>
              <option value="other">其他</option>
            </select>
          </div>

          <!-- 年齡層 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              年齡層
            </label>
            <select
              v-model="formData.ageRange"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            >
              <option value="">請選擇...</option>
              <option value="18-24">18-24 歲</option>
              <option value="25-34">25-34 歲</option>
              <option value="35-44">35-44 歲</option>
              <option value="45-54">45-54 歲</option>
              <option value="55+">55 歲以上</option>
            </select>
          </div>

          <!-- 密碼 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              密碼 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.password"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="至少 6 個字元"
            />
            <p class="text-xs text-gray-500 mt-1">密碼必須至少 6 個字元</p>
          </div>

          <!-- 確認密碼 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              確認密碼 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.confirmPassword"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="再次輸入密碼"
            />
          </div>

          <!-- 同意條款 -->
          <div class="flex items-start">
            <input
              v-model="formData.agreedToTerms"
              type="checkbox"
              required
              class="mt-1 mr-2"
              id="terms"
            />
            <label for="terms" class="text-sm text-gray-600">
              我已閱讀並同意
              <a
                href="/terms"
                target="_blank"
                class="text-blue-600 hover:underline"
                >服務條款</a
              >
              和
              <a
                href="/privacy"
                target="_blank"
                class="text-blue-600 hover:underline"
                >隱私政策</a
              >
            </label>
          </div>

          <!-- 提交按鈕 -->
          <button
            type="submit"
            class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            :disabled="loading"
          >
            {{ loading ? "註冊中..." : "註冊" }}
          </button>
        </form>

        <!-- 登入連結 -->
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

        <!-- 錯誤訊息 -->
        <div
          v-if="error"
          class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- 成功訊息 -->
        <div
          v-if="success"
          class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <p class="text-sm text-green-700">{{ success }}</p>
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
const formData = ref({
  email: "",
  displayName: "",
  academicField: "",
  ageRange: "",
  password: "",
  confirmPassword: "",
  agreedToTerms: false,
});

const loading = ref(false);
const error = ref("");
const success = ref("");

async function handleSignup() {
  loading.value = true;
  error.value = "";
  success.value = "";

  // 驗證
  if (formData.value.password !== formData.value.confirmPassword) {
    error.value = "密碼不一致";
    loading.value = false;
    return;
  }

  if (formData.value.password.length < 6) {
    error.value = "密碼必須至少 6 個字元";
    loading.value = false;
    return;
  }

  if (!formData.value.agreedToTerms) {
    error.value = "請同意服務條款和隱私政策";
    loading.value = false;
    return;
  }

  try {
    // 呼叫自訂註冊 API
    const response = await $fetch("/api/auth/signup", {
      method: "POST",
      body: {
        email: formData.value.email,
        password: formData.value.password,
        displayName: formData.value.displayName,
        academicField: formData.value.academicField || null,
        ageRange: formData.value.ageRange || null,
      },
    });

    success.value =
      "註冊成功！請檢查您的 Email 收件匣，點擊驗證連結以啟用帳號。";

    // 清空表單
    formData.value = {
      email: "",
      displayName: "",
      academicField: "",
      ageRange: "",
      password: "",
      confirmPassword: "",
      agreedToTerms: false,
    };
  } catch (err: any) {
    error.value = err.data?.message || "註冊失敗，請稍後再試";
  } finally {
    loading.value = false;
  }
}

useHead({
  title: "註冊 - Know Graph Lab",
  meta: [
    {
      name: "description",
      content: "註冊 Know Graph Lab 帳號，開始使用 AI 驅動的知識圖表工具",
    },
  ],
});
</script>
