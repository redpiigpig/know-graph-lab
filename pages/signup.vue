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

      <div
        class="bg-white rounded-2xl shadow-xl p-8 max-h-[80vh] overflow-y-auto"
      >
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

          <!-- 學術領域（複選） -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              學術專業領域 <span class="text-gray-500 text-xs">（可複選）</span>
            </label>

            <div
              class="grid grid-cols-2 gap-2 p-4 border border-gray-300 rounded-lg bg-gray-50 max-h-60 overflow-y-auto"
            >
              <label
                v-for="field in academicFields"
                :key="field.value"
                class="flex items-center space-x-2 p-2 hover:bg-white rounded cursor-pointer transition"
              >
                <input
                  type="checkbox"
                  :value="field.value"
                  v-model="formData.academicFields"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="text-sm text-gray-700">{{ field.label }}</span>
              </label>
            </div>

            <p class="text-xs text-gray-500 mt-2">
              已選擇 {{ formData.academicFields.length }} 個領域
            </p>
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
            <div class="relative">
              <input
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                required
                minlength="6"
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
            <p class="text-xs text-gray-500 mt-1">密碼必須至少 6 個字元</p>
          </div>

          <!-- 確認密碼 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              確認密碼 <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model="formData.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition pr-12"
                placeholder="再次輸入密碼"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <svg
                  v-if="showConfirmPassword"
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
// 學術領域選項
const academicFields = [
  { value: "computer_science", label: "資訊科學" },
  { value: "engineering", label: "工程學" },
  { value: "natural_sciences", label: "自然科學" },
  { value: "physics", label: "物理學" },
  { value: "chemistry", label: "化學" },
  { value: "biology", label: "生物學" },
  { value: "mathematics", label: "數學" },
  { value: "social_sciences", label: "社會科學" },
  { value: "psychology", label: "心理學" },
  { value: "sociology", label: "社會學" },
  { value: "economics", label: "經濟學" },
  { value: "political_science", label: "政治學" },
  { value: "humanities", label: "人文學科" },
  { value: "history", label: "歷史學" },
  { value: "philosophy", label: "哲學" },
  { value: "literature", label: "文學" },
  { value: "linguistics", label: "語言學" },
  { value: "medicine", label: "醫學" },
  { value: "nursing", label: "護理學" },
  { value: "pharmacy", label: "藥學" },
  { value: "business", label: "商學" },
  { value: "management", label: "管理學" },
  { value: "finance", label: "財務金融" },
  { value: "education", label: "教育學" },
  { value: "arts", label: "藝術" },
  { value: "design", label: "設計" },
  { value: "law", label: "法律" },
  { value: "architecture", label: "建築" },
  { value: "agriculture", label: "農業" },
  { value: "environmental_science", label: "環境科學" },
  { value: "other", label: "其他" },
];

const formData = ref({
  email: "",
  displayName: "",
  academicFields: [] as string[],
  ageRange: "",
  password: "",
  confirmPassword: "",
  agreedToTerms: false,
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);
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
        academicFields:
          formData.value.academicFields.length > 0
            ? formData.value.academicFields
            : null,
        ageRange: formData.value.ageRange || null,
      },
    });

    success.value =
      "註冊成功！我們已發送驗證郵件到你的信箱，請點擊郵件中的連結以啟用帳號。";

    // 清空表單
    formData.value = {
      email: "",
      displayName: "",
      academicFields: [],
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
