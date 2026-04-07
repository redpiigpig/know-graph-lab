<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航欄（保持不變）-->
    <nav class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <img src="/images/logo-icon.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold">Know Graph Lab</span>
          </div>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/" class="text-gray-600 hover:text-blue-600"
              >首頁</NuxtLink
            >
            <button
              @click="handleLogout"
              class="text-gray-600 hover:text-red-600"
            >
              登出
            </button>
            <NuxtLink
              to="/guide"
              class="text-gray-600 hover:text-blue-600 transition"
              >使用指南</NuxtLink
            >
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-4 py-12">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">API Key 管理</h1>
        <p class="text-gray-600">
          管理你的 AI API Keys，支援多個 Key 並自動切換
        </p>
      </div>

      <!-- 使用統計卡片 -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm border p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">本月使用次數</p>
              <p class="text-3xl font-bold text-blue-600">{{ totalUsage }}</p>
            </div>
            <div
              class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">可用 API Keys</p>
              <p class="text-3xl font-bold text-green-600">
                {{ activeKeysCount }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">剩餘額度</p>
              <p class="text-3xl font-bold text-purple-600">
                {{ remainingQuota }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 新增 API Key 按鈕 -->
      <div class="mb-6">
        <button
          @click="showAddKeyModal = true"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          + 新增 API Key
        </button>
      </div>

      <!-- API Keys 列表 -->
      <div class="space-y-4">
        <div
          v-for="key in apiKeys"
          :key="key.id"
          class="bg-white rounded-xl shadow-sm border p-6"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <!-- 標題行 -->
              <div class="flex items-center space-x-3 mb-3">
                <span
                  class="px-3 py-1 rounded-full text-xs font-semibold"
                  :class="
                    key.provider === 'gemini'
                      ? 'bg-blue-100 text-blue-700'
                      : key.provider === 'claude'
                        ? 'bg-purple-100 text-purple-700'
                        : 'bg-green-100 text-green-700'
                  "
                >
                  {{ key.provider.toUpperCase() }}
                </span>
                <span
                  class="px-3 py-1 rounded-full text-xs font-semibold"
                  :class="
                    key.key_type === 'free'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-amber-100 text-amber-700'
                  "
                >
                  {{ key.key_type === "free" ? "免費" : "付費" }}
                </span>
                <span
                  v-if="!key.is_active"
                  class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold"
                >
                  已停用
                </span>
                <span
                  v-if="key.is_exhausted"
                  class="px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-semibold"
                >
                  額度用盡
                </span>
              </div>

              <!-- Key 資訊 -->
              <h3 class="text-lg font-semibold text-gray-900 mb-2">
                {{ key.nickname || `${key.provider} API Key` }}
              </h3>
              <p class="text-sm text-gray-500 mb-3">
                優先級：{{ key.priority }} | 本月使用：{{ key.current_usage
                }}{{ key.usage_limit ? ` / ${key.usage_limit}` : "" }} 次
              </p>

              <!-- 進度條（如果有限制）-->
              <div v-if="key.usage_limit" class="mb-3">
                <div class="flex justify-between text-xs text-gray-600 mb-1">
                  <span>使用進度</span>
                  <span
                    >{{
                      Math.round((key.current_usage / key.usage_limit) * 100)
                    }}%</span
                  >
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all"
                    :class="
                      key.current_usage / key.usage_limit > 0.9
                        ? 'bg-red-500'
                        : key.current_usage / key.usage_limit > 0.7
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                    "
                    :style="{
                      width: `${Math.min((key.current_usage / key.usage_limit) * 100, 100)}%`,
                    }"
                  ></div>
                </div>
              </div>

              <!-- 上次使用 -->
              <p class="text-xs text-gray-500">
                {{
                  key.last_used_at
                    ? `上次使用：${formatDate(key.last_used_at)}`
                    : "尚未使用"
                }}
              </p>
            </div>

            <!-- 操作按鈕 -->
            <div class="flex items-center space-x-2 ml-4">
              <button
                @click="toggleKeyStatus(key)"
                class="p-2 hover:bg-gray-100 rounded-lg transition"
                :title="key.is_active ? '停用' : '啟用'"
              >
                <svg
                  v-if="key.is_active"
                  class="w-5 h-5 text-green-600"
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
                  class="w-5 h-5 text-gray-400"
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

              <button
                @click="editKey(key)"
                class="p-2 hover:bg-gray-100 rounded-lg transition"
                title="編輯"
              >
                <svg
                  class="w-5 h-5 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>

              <button
                @click="deleteKey(key)"
                class="p-2 hover:bg-red-50 rounded-lg transition"
                title="刪除"
              >
                <svg
                  class="w-5 h-5 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 空狀態 -->
        <div
          v-if="apiKeys.length === 0"
          class="bg-white rounded-xl shadow-sm border p-12 text-center"
        >
          <svg
            class="w-16 h-16 text-gray-300 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            尚未設定 API Key
          </h3>
          <p class="text-gray-600 mb-4">新增你的第一個 API Key 以開始使用</p>
          <button
            @click="showAddKeyModal = true"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            新增 API Key
          </button>
        </div>
      </div>

      <!-- 新增/編輯 Modal -->
      <div
        v-if="showAddKeyModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <div
          class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8"
        >
          <h2 class="text-2xl font-bold mb-6">
            {{ editingKey ? "編輯" : "新增" }} API Key
          </h2>

          <form @submit.prevent="saveKey" class="space-y-6">
            <!-- Provider -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >AI 提供商</label
              >
              <select
                v-model="formData.provider"
                required
                class="w-full px-4 py-3 border rounded-lg"
              >
                <option value="gemini">Google Gemini</option>
                <option value="claude">Anthropic Claude</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>

            <!-- API Key -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >API Key</label
              >
              <input
                v-model="formData.apiKey"
                type="password"
                required
                class="w-full px-4 py-3 border rounded-lg"
                placeholder="輸入你的 API Key"
              />
            </div>

            <!-- Nickname -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >暱稱（可選）</label
              >
              <input
                v-model="formData.nickname"
                type="text"
                class="w-full px-4 py-3 border rounded-lg"
                placeholder="例如：主要 Key、備用 Key"
              />
            </div>

            <!-- Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >類型</label
              >
              <div class="flex space-x-4">
                <label class="flex items-center">
                  <input
                    type="radio"
                    v-model="formData.keyType"
                    value="free"
                    class="mr-2"
                  />
                  <span>免費額度</span>
                </label>
                <label class="flex items-center">
                  <input
                    type="radio"
                    v-model="formData.keyType"
                    value="paid"
                    class="mr-2"
                  />
                  <span>付費帳號</span>
                </label>
              </div>
            </div>

            <!-- Priority -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                優先級（數字越小越優先）
              </label>
              <input
                v-model.number="formData.priority"
                type="number"
                min="0"
                class="w-full px-4 py-3 border rounded-lg"
              />
              <p class="text-xs text-gray-500 mt-1">
                系統會優先使用數字小的 Key
              </p>
            </div>

            <!-- Usage Limit -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                每月使用上限（次數）
              </label>
              <input
                v-model.number="formData.usageLimit"
                type="number"
                min="0"
                class="w-full px-4 py-3 border rounded-lg"
                placeholder="留空 = 無限制"
              />
              <p class="text-xs text-gray-500 mt-1">
                達到上限後會自動切換到下一個 Key
              </p>
            </div>

            <!-- 按鈕 -->
            <div class="flex space-x-4">
              <button
                type="submit"
                class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                :disabled="saving"
              >
                {{ saving ? "儲存中..." : "儲存" }}
              </button>
              <button
                type="button"
                @click="closeModal"
                class="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: "auth",
});

const supabase = useSupabaseClient();
const user = useSupabaseUser();
const router = useRouter();

// 狀態
const apiKeys = ref<any[]>([]);
const showAddKeyModal = ref(false);
const editingKey = ref<any>(null);
const saving = ref(false);

// 統計
const totalUsage = computed(() =>
  apiKeys.value.reduce((sum, key) => sum + (key.current_usage || 0), 0),
);
const activeKeysCount = computed(
  () =>
    apiKeys.value.filter((key) => key.is_active && !key.is_exhausted).length,
);
const remainingQuota = computed(() => {
  const limited = apiKeys.value.filter((key) => key.usage_limit);
  if (limited.length === 0) return "無限";
  return limited.reduce(
    (sum, key) => sum + (key.usage_limit - key.current_usage),
    0,
  );
});

// 表單資料
const formData = ref({
  provider: "gemini",
  apiKey: "",
  nickname: "",
  keyType: "free",
  priority: 0,
  usageLimit: null as number | null,
});

// 載入 API Keys
async function loadKeys() {
  const { data } = await supabase
    .from("api_keys")
    .select("*")
    .eq("user_id", user.value?.id)
    .order("priority", { ascending: true });

  if (data) {
    apiKeys.value = data;
  }
}

// 儲存 Key
async function saveKey() {
  saving.value = true;

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    await $fetch("/api/user/api-keys", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session?.access_token}`,
      },
      body: {
        id: editingKey.value?.id,
        provider: formData.value.provider,
        api_key: formData.value.apiKey,
        nickname: formData.value.nickname || null,
        key_type: formData.value.keyType,
        priority: formData.value.priority,
        usage_limit: formData.value.usageLimit || null,
      },
    });

    await loadKeys();
    closeModal();
  } catch (error: any) {
    alert("儲存失敗：" + error.message);
  } finally {
    saving.value = false;
  }
}

// 切換狀態
async function toggleKeyStatus(key: any) {
  await supabase
    .from("api_keys")
    .update({ is_active: !key.is_active })
    .eq("id", key.id);

  await loadKeys();
}

// 編輯
function editKey(key: any) {
  editingKey.value = key;
  formData.value = {
    provider: key.provider,
    apiKey: "",
    nickname: key.nickname || "",
    keyType: key.key_type,
    priority: key.priority,
    usageLimit: key.usage_limit,
  };
  showAddKeyModal.value = true;
}

// 刪除
async function deleteKey(key: any) {
  if (!confirm("確定要刪除這個 API Key？")) return;

  await supabase.from("api_keys").delete().eq("id", key.id);

  await loadKeys();
}

// 關閉 Modal
function closeModal() {
  showAddKeyModal.value = false;
  editingKey.value = null;
  formData.value = {
    provider: "gemini",
    apiKey: "",
    nickname: "",
    keyType: "free",
    priority: 0,
    usageLimit: null,
  };
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleString("zh-TW");
}

// 登出
async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/");
}

// 初始載入
onMounted(() => {
  loadKeys();
});
</script>
