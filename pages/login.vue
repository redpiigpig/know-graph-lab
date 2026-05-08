<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-sm w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <img src="/images/logo-icon.svg" alt="Logo" class="w-16 h-16 mx-auto mb-4" />
        <h1 class="text-2xl font-bold text-gray-900">Know Graph Lab</h1>
        <p class="text-gray-500 text-sm mt-1">個人學術研究工具集</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8 space-y-6">

        <!-- ── 密碼登入 ── -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1.5">Email</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1.5">密碼</label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                placeholder="輸入密碼"
              />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <svg v-if="showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <button type="submit"
            class="w-full py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loginLoading">
            {{ loginLoading ? "登入中…" : "登入" }}
          </button>
        </form>

        <!-- 分隔線 -->
        <div class="flex items-center gap-3">
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-400">或</span>
          <div class="flex-1 h-px bg-gray-100"></div>
        </div>

        <!-- ── 一鍵登入（Magic Link）── -->
        <div class="space-y-3">
          <p class="text-xs text-center text-gray-500">忘記密碼？寄一鍵登入連結到信箱</p>
          <div v-if="!magicSent">
            <input
              v-model="magicEmail"
              type="email"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-400 focus:border-transparent outline-none transition mb-2"
              placeholder="your@email.com"
            />
            <button @click="sendMagicLink"
              class="w-full py-2.5 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 hover:border-gray-300 transition disabled:opacity-50"
              :disabled="magicLoading">
              {{ magicLoading ? "寄送中…" : "✉️  寄送一鍵登入連結" }}
            </button>
          </div>
          <div v-else class="text-center py-3 px-4 bg-green-50 rounded-xl border border-green-100">
            <p class="text-sm font-medium text-green-700">✅ 連結已寄出！</p>
            <p class="text-xs text-green-600 mt-0.5">請查看 {{ magicEmail }} 的信箱，點擊連結即可登入</p>
            <button @click="magicSent = false" class="mt-2 text-xs text-green-500 hover:underline">重新寄送</button>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-100 rounded-lg">
          <p class="text-xs text-red-600">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient();
const user = useSupabaseUser();
const router = useRouter();
const config = useRuntimeConfig();

const allowedEmail = config.public.allowedEmail as string;

// 密碼登入
const email = ref(allowedEmail || "");
const password = ref("");
const showPassword = ref(false);
const loginLoading = ref(false);
const error = ref("");

// Magic Link
const magicEmail = ref(allowedEmail || "");
const magicLoading = ref(false);
const magicSent = ref(false);

// 已登入就導回（優先用 ?redirect=...，否則回首頁）
const route = useRoute();
const redirectTo = computed(() => {
  const r = route.query.redirect;
  return typeof r === "string" && r.startsWith("/") ? r : "/";
});
watchEffect(() => {
  if (user.value) router.push(redirectTo.value);
});

async function handleLogin() {
  loginLoading.value = true;
  error.value = "";
  const { error: e } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  });
  loginLoading.value = false;
  if (e) {
    error.value = e.message === "Invalid login credentials" ? "Email 或密碼錯誤" : e.message;
  } else {
    router.push(redirectTo.value);
  }
}

async function sendMagicLink() {
  if (!magicEmail.value.trim()) { error.value = "請輸入 Email"; return; }
  magicLoading.value = true;
  error.value = "";
  const { error: e } = await supabase.auth.signInWithOtp({
    email: magicEmail.value.trim(),
    options: { emailRedirectTo: `${config.public.appUrl}/` },
  });
  magicLoading.value = false;
  if (e) {
    error.value = e.message;
  } else {
    magicSent.value = true;
  }
}
</script>
