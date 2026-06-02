<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-sm w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <img src="/images/logo-icon.svg" alt="Logo" class="w-16 h-16 mx-auto mb-4" />
        <h1 class="text-2xl font-bold text-gray-900">Know Graph Lab</h1>
        <p class="text-gray-500 text-sm mt-1">個人學術研究工具集</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8 space-y-5">
        <!-- 步驟 1：輸入 email 寄驗證碼 -->
        <div v-if="!codeSent" class="space-y-3">
          <p class="text-sm text-center text-gray-600">輸入授權 Email，寄 6 位數驗證碼到信箱</p>
          <input
            v-model="email"
            type="email"
            @keydown.enter="sendCode"
            class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 focus:border-transparent outline-none transition"
            placeholder="your@email.com"
          />
          <button @click="sendCode"
            class="w-full py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            :disabled="sending">
            {{ sending ? "寄送中…" : "✉️  寄送驗證碼" }}
          </button>
        </div>

        <!-- 步驟 2：輸入驗證碼 -->
        <div v-else class="space-y-3">
          <p class="text-sm text-center text-gray-600">驗證碼已寄到 <b>{{ email }}</b>，請輸入</p>
          <input
            v-model="code"
            inputmode="numeric"
            maxlength="6"
            @keydown.enter="verifyCode"
            class="w-full px-3 py-3 border border-gray-200 rounded-lg text-center text-2xl tracking-[0.4em] font-mono focus:ring-2 focus:ring-indigo-400 outline-none transition"
            placeholder="000000"
          />
          <button @click="verifyCode"
            class="w-full py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            :disabled="verifying || code.length < 6">
            {{ verifying ? "驗證中…" : "登入" }}
          </button>
          <div class="flex justify-between text-xs">
            <button @click="codeSent = false; code = ''" class="text-gray-400 hover:underline">← 改 Email</button>
            <button @click="sendCode" :disabled="sending" class="text-indigo-500 hover:underline disabled:opacity-50">重新寄送</button>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-100 rounded-lg">
          <p class="text-xs text-red-600">{{ error }}</p>
        </div>

        <p class="text-center text-[11px] text-gray-400 pt-1">
          私人網站，僅限授權 Email 登入。每次新裝置都需 email 驗證碼——即使知道帳密，沒有信箱也無法進入。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient();
const user = useSupabaseUser();
const router = useRouter();
const config = useRuntimeConfig();

const error = ref("");

// Email OTP 驗證碼（唯一登入方式；手機也能用）
const email = ref("");
const code = ref("");
const sending = ref(false);
const verifying = ref(false);
const codeSent = ref(false);

// 已登入就導回（優先用 ?redirect=...，否則回首頁）
const route = useRoute();
const redirectTo = computed(() => {
  const r = route.query.redirect;
  return typeof r === "string" && r.startsWith("/") ? r : "/";
});
watchEffect(() => {
  if (user.value) router.push(redirectTo.value);
});

async function sendCode() {
  if (!email.value.trim()) { error.value = "請輸入 Email"; return; }
  sending.value = true;
  error.value = "";
  // shouldCreateUser:false → 只有已存在的授權帳號能收到驗證碼，不建立新帳號
  const { error: e } = await supabase.auth.signInWithOtp({
    email: email.value.trim(),
    options: { shouldCreateUser: false },
  });
  sending.value = false;
  if (e) {
    error.value = e.message;
  } else {
    codeSent.value = true;
  }
}

async function verifyCode() {
  if (code.value.length < 6) return;
  verifying.value = true;
  error.value = "";
  const { error: e } = await supabase.auth.verifyOtp({
    email: email.value.trim(),
    token: code.value.trim(),
    type: "email",
  });
  verifying.value = false;
  if (e) {
    error.value = e.message === "Token has expired or is invalid" ? "驗證碼錯誤或已過期" : e.message;
  } else {
    router.push(redirectTo.value);
  }
}
</script>
