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
        <p class="text-sm text-center text-gray-600">輸入授權 Email，寄一鍵登入連結到信箱</p>

        <!-- ── 一鍵登入（Magic Link，唯一登入方式）── -->
        <div v-if="!magicSent" class="space-y-3">
          <input
            v-model="magicEmail"
            type="email"
            @keydown.enter="sendMagicLink"
            class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 focus:border-transparent outline-none transition"
            placeholder="your@email.com"
          />
          <button @click="sendMagicLink"
            class="w-full py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            :disabled="magicLoading">
            {{ magicLoading ? "寄送中…" : "✉️  寄送登入連結" }}
          </button>
        </div>
        <div v-else class="text-center py-3 px-4 bg-green-50 rounded-xl border border-green-100">
          <p class="text-sm font-medium text-green-700">✅ 連結已寄出！</p>
          <p class="text-xs text-green-600 mt-0.5">請查看 {{ magicEmail }} 的信箱，點擊連結即可登入</p>
          <button @click="magicSent = false" class="mt-2 text-xs text-green-500 hover:underline">重新寄送</button>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-100 rounded-lg">
          <p class="text-xs text-red-600">{{ error }}</p>
        </div>

        <p class="text-center text-[11px] text-gray-400 pt-1">
          私人網站，僅限授權 Email 登入。每次登入都需點擊信箱中的連結驗證——即使知道帳密，沒有信箱也無法進入。
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

// Magic Link（唯一登入方式）
const magicEmail = ref("");
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

async function sendMagicLink() {
  if (!magicEmail.value.trim()) { error.value = "請輸入 Email"; return; }
  magicLoading.value = true;
  error.value = "";
  // shouldCreateUser:false → 只有已存在的授權帳號能收到連結，不會建立新帳號
  const { error: e } = await supabase.auth.signInWithOtp({
    email: magicEmail.value.trim(),
    options: { emailRedirectTo: `${config.public.appUrl}/`, shouldCreateUser: false },
  });
  magicLoading.value = false;
  if (e) {
    error.value = e.message;
  } else {
    magicSent.value = true;
  }
}
</script>
