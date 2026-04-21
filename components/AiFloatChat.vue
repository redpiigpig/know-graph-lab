<template>
  <!-- 浮動按鈕 -->
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">

    <!-- 快速提示（只在關閉狀態顯示，且首次出現） -->
    <Transition name="fade">
      <div v-if="!open && showHint" class="bg-gray-900 text-white text-xs px-3 py-1.5 rounded-lg shadow-lg whitespace-nowrap">
        AI 書摘問答
        <button @click="showHint = false" class="ml-2 opacity-60 hover:opacity-100">✕</button>
      </div>
    </Transition>

    <!-- 浮動按鈕 -->
    <button
      @click="togglePanel"
      class="w-14 h-14 rounded-2xl shadow-xl flex items-center justify-center text-2xl transition-all duration-300 hover:scale-110 active:scale-95"
      :class="open ? 'bg-gray-800 text-white rotate-0' : 'bg-blue-600 text-white'"
      :title="open ? '關閉 AI 助理' : '開啟 AI 助理'"
    >
      <span v-if="!open">🤖</span>
      <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <!-- 側邊聊天面板 -->
  <Transition name="slide">
    <div v-if="open"
      class="fixed top-0 right-0 h-full z-40 flex flex-col bg-white shadow-2xl border-l border-gray-200"
      :style="{ width: panelWidth }"
    >
      <!-- 面板頭部 -->
      <div class="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 bg-white">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-sm">🤖</div>
          <div>
            <h2 class="text-sm font-semibold text-gray-900">AI 研究助理</h2>
            <p class="text-xs text-gray-400">書摘語意搜尋 · Qwen2.5</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- 半畫面 / 全寬 切換 -->
          <button @click="toggleWidth" class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition" :title="isHalf ? '擴展為全寬' : '縮回半寬'">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="isHalf" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
            </svg>
          </button>
          <button @click="open = false" class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 聊天訊息區 -->
      <div ref="msgArea" class="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-gray-50">
        <!-- 歡迎訊息 -->
        <div v-if="messages.length === 0" class="text-center py-10">
          <div class="text-4xl mb-3">🔍</div>
          <p class="text-sm font-medium text-gray-700 mb-1">書摘語意問答</p>
          <p class="text-xs text-gray-400 leading-relaxed">輸入問題，AI 會從你的 1932 筆書摘中<br>找出相關段落並整合作答</p>
          <!-- 範例問題 -->
          <div class="mt-5 flex flex-col gap-2">
            <button v-for="q in exampleQuestions" :key="q" @click="askQuestion(q)"
              class="text-xs px-3 py-2 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:text-blue-700 transition text-gray-600 text-left">
              {{ q }}
            </button>
          </div>
        </div>

        <!-- 訊息泡泡 -->
        <template v-for="(msg, i) in messages" :key="i">
          <!-- 用戶訊息 -->
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="max-w-[85%] bg-blue-600 text-white text-sm rounded-2xl rounded-tr-sm px-4 py-2.5 leading-relaxed">
              {{ msg.content }}
            </div>
          </div>

          <!-- AI 回答 -->
          <div v-else class="flex flex-col gap-2">
            <div class="max-w-[95%] bg-white border border-gray-200 text-gray-800 text-sm rounded-2xl rounded-tl-sm px-4 py-3 leading-relaxed shadow-sm whitespace-pre-wrap">
              <div v-if="msg.loading" class="flex items-center gap-2 text-gray-400">
                <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style="animation-delay:0ms"></span>
                <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style="animation-delay:150ms"></span>
                <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style="animation-delay:300ms"></span>
              </div>
              <span v-else>{{ msg.content }}</span>
            </div>
            <!-- 來源書摘 -->
            <div v-if="msg.sources?.length" class="flex flex-wrap gap-1.5 max-w-[95%]">
              <span class="text-xs text-gray-400">引用來源：</span>
              <NuxtLink
                v-for="s in msg.sources.slice(0, 4)" :key="s.id"
                :to="`/excerpts/${s.id}`"
                @click="open = false"
                class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-0.5 rounded-full transition truncate max-w-[120px]"
                :title="s.bookTitle || s.title"
              >
                {{ s.bookTitle ?? s.title ?? '摘文' }}
              </NuxtLink>
            </div>
          </div>
        </template>
      </div>

      <!-- Ollama 離線提示 -->
      <div v-if="ollamaOffline" class="mx-4 mb-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700 flex items-center gap-2">
        <span>⚠️</span>
        <span>Ollama 未啟動，請在本機執行 <code class="bg-amber-100 px-1 rounded">ollama serve</code></span>
      </div>

      <!-- 輸入區 -->
      <div class="border-t border-gray-100 px-4 py-3 bg-white">
        <div class="flex items-end gap-2">
          <textarea
            v-model="inputText"
            @keydown.enter.exact.prevent="send"
            rows="1"
            placeholder="問問題… (Enter 送出, Shift+Enter 換行)"
            class="flex-1 resize-none text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none transition leading-relaxed max-h-32 overflow-y-auto"
            style="field-sizing: content"
          ></textarea>
          <button @click="send" :disabled="!inputText.trim() || aiLoading"
            class="w-10 h-10 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white flex items-center justify-center transition flex-shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-1.5 text-right">基於你的書摘資料庫回答</p>
      </div>
    </div>
  </Transition>

  <!-- 半透明背景遮罩（行動版） -->
  <Transition name="fade">
    <div v-if="open && !isHalf" @click="open = false"
      class="fixed inset-0 bg-black/20 z-30 md:hidden"></div>
  </Transition>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient();
const user = useSupabaseUser();

const open = ref(false);
const isHalf = ref(true);
const showHint = ref(true);
const inputText = ref("");
const aiLoading = ref(false);
const ollamaOffline = ref(false);
const msgArea = ref<HTMLElement | null>(null);

const panelWidth = computed(() => {
  if (!isHalf.value) return "100%";
  return "min(480px, 90vw)";
});

const exampleQuestions = [
  "伊斯蘭教的核心神學概念是什麼？",
  "請整理書中關於歷史方法論的觀點",
  "有哪些關於宗教與政治關係的摘文？",
];

type Message = {
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
  sources?: any[];
};

const messages = ref<Message[]>([]);

function togglePanel() {
  open.value = !open.value;
  showHint.value = false;
}

function toggleWidth() {
  isHalf.value = !isHalf.value;
}

async function scrollBottom() {
  await nextTick();
  if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight;
}

async function askQuestion(q: string) {
  inputText.value = q;
  await send();
}

async function send() {
  const q = inputText.value.trim();
  if (!q || aiLoading.value) return;
  inputText.value = "";
  aiLoading.value = true;
  ollamaOffline.value = false;

  messages.value.push({ role: "user", content: q });
  messages.value.push({ role: "assistant", content: "", loading: true });
  await scrollBottom();

  try {
    const { data: { session } } = await supabase.auth.getSession();
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (session?.access_token) headers.Authorization = `Bearer ${session.access_token}`;

    const res = await $fetch<{ answer: string; sources: any[] }>("/api/ai/rag", {
      method: "POST",
      headers,
      body: { question: q },
    });

    const last = messages.value[messages.value.length - 1];
    last.loading = false;
    last.content = res.answer;
    last.sources = res.sources;
  } catch (e: any) {
    const last = messages.value[messages.value.length - 1];
    last.loading = false;
    if (e?.message?.includes("Ollama") || e?.statusCode === 503) {
      ollamaOffline.value = true;
      last.content = "❌ Ollama 未啟動，請在本機執行 `ollama serve` 後再試。";
    } else {
      last.content = "❌ 發生錯誤：" + (e?.message ?? "未知錯誤");
    }
  }

  aiLoading.value = false;
  await scrollBottom();
}
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
