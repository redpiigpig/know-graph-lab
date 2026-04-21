<template>
  <div class="min-h-screen bg-gray-950 text-white">
    <nav class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/" class="text-gray-400 hover:text-white transition text-sm">← 工作台</NuxtLink>
        <span class="text-gray-600">·</span>
        <span class="text-white font-semibold text-sm">AI 研究助理</span>
        <div class="ml-auto flex items-center gap-2">
          <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', ollamaOk ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400']">
            {{ ollamaOk ? `● Ollama (${activeModel})` : '● Ollama 離線' }}
          </span>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-8 space-y-8">

      <!-- Tab 切換 -->
      <div class="flex gap-2 bg-gray-900 rounded-xl p-1 w-fit">
        <button v-for="t in tabs" :key="t.key" @click="activeTab = t.key"
          :class="['px-5 py-2 rounded-lg text-sm font-medium transition', activeTab === t.key ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white']">
          {{ t.label }}
        </button>
      </div>

      <!-- ── RAG 問答 ── -->
      <div v-if="activeTab === 'rag'" class="space-y-4">
        <div>
          <h2 class="text-xl font-semibold mb-1">書摘問答（RAG）</h2>
          <p class="text-gray-400 text-sm">根據你的書摘資料庫回答問題，自動引用來源</p>
        </div>

        <div class="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">
          <textarea v-model="ragQuestion" rows="3"
            placeholder="例如：薩滿教和佛教對靈魂的看法有何差異？"
            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500 text-sm" />
          <div class="flex items-center gap-3">
            <button @click="askRag" :disabled="ragLoading || !ragQuestion.trim()"
              class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition">
              {{ ragLoading ? '思考中…' : '提問' }}
            </button>
            <span class="text-xs text-gray-500">使用 {{ activeModel }}</span>
          </div>
        </div>

        <!-- 答案 -->
        <div v-if="ragAnswer" class="space-y-4">
          <div class="bg-gray-900 border border-gray-700 rounded-2xl p-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span class="text-xs text-gray-400 font-medium">AI 回答</span>
            </div>
            <p class="text-gray-100 leading-relaxed whitespace-pre-wrap text-sm">{{ ragAnswer }}</p>
          </div>

          <div v-if="ragSources.length" class="space-y-2">
            <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">引用來源</p>
            <NuxtLink v-for="s in ragSources" :key="s.id" :to="`/excerpts/${s.id}`"
              class="block bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-4 transition">
              <div class="flex items-start gap-3">
                <span class="text-lg">📄</span>
                <div>
                  <p class="text-sm font-medium text-gray-200">{{ s.title ?? '（無標題）' }}</p>
                  <p class="text-xs text-gray-500">
                    {{ s.bookTitle }}{{ s.chapter ? ` · ${s.chapter}` : '' }}{{ s.page_number ? ` · p.${s.page_number}` : '' }}
                  </p>
                  <p class="text-xs text-gray-400 mt-1 line-clamp-2">{{ s.snippet }}</p>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>

        <p v-if="ragError" class="text-red-400 text-sm bg-red-950 rounded-xl p-4">{{ ragError }}</p>
      </div>

      <!-- ── OCR 上傳 ── -->
      <div v-if="activeTab === 'ocr'" class="space-y-4">
        <div>
          <h2 class="text-xl font-semibold mb-1">拍照建摘文</h2>
          <p class="text-gray-400 text-sm">上傳書頁照片，AI 自動識別文字並按頁建立摘文</p>
        </div>

        <div v-if="!ollamaHasVision" class="bg-amber-950 border border-amber-800 rounded-xl p-4 text-amber-300 text-sm">
          ⚠ 需要視覺模型才能 OCR。請在終端機執行：
          <code class="block mt-2 bg-gray-900 rounded px-3 py-2 text-amber-200 text-xs">ollama pull qwen2.5vl:7b</code>
          <p class="mt-2 text-xs text-amber-400">下載約 4.9GB，完成後重新整理頁面</p>
        </div>

        <div class="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">
          <!-- 圖片上傳 -->
          <div
            @dragover.prevent @drop.prevent="handleImageDrop"
            @click="imageInput?.click()"
            class="border-2 border-dashed border-gray-700 hover:border-blue-500 rounded-xl p-8 text-center cursor-pointer transition">
            <div v-if="ocrPreview">
              <img :src="ocrPreview" class="max-h-64 mx-auto rounded-lg object-contain" />
              <p class="text-xs text-gray-400 mt-2">點擊更換圖片</p>
            </div>
            <div v-else class="text-gray-500">
              <p class="text-3xl mb-2">📷</p>
              <p class="text-sm">點擊或拖曳書頁照片（JPG / PNG）</p>
            </div>
          </div>
          <input ref="imageInput" type="file" accept="image/*" class="hidden" @change="handleImageSelect" />

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-400 mb-1 block">起始頁碼</label>
              <input v-model.number="ocrStartPage" type="number" min="1"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="text-xs text-gray-400 mb-1 block">關聯書籍（選填）</label>
              <select v-model="ocrBookId" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500">
                <option value="">不指定</option>
                <option v-for="b in books" :key="b.id" :value="b.id">{{ b.author }} — {{ b.title }}</option>
              </select>
            </div>
          </div>

          <button @click="runOCR" :disabled="!ocrFile || ocrLoading || !ollamaHasVision"
            class="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition">
            {{ ocrLoading ? 'AI 識別中…' : '開始 OCR 建立摘文' }}
          </button>
        </div>

        <div v-if="ocrResult" class="bg-gray-900 border border-green-800 rounded-2xl p-6">
          <p class="text-green-400 font-medium mb-2">✓ 成功建立 {{ ocrResult.excerptsSaved }} 筆摘文（共偵測 {{ ocrResult.pagesDetected }} 頁）</p>
          <NuxtLink v-for="e in ocrResult.excerpts" :key="e.id" :to="`/excerpts/${e.id}`"
            class="block text-sm text-blue-400 hover:underline mt-1">→ {{ e.title ?? `第 ${e.page_number} 頁摘文` }}</NuxtLink>
        </div>

        <p v-if="ocrError" class="text-red-400 text-sm bg-red-950 rounded-xl p-4">{{ ocrError }}</p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();

const tabs = [
  { key: "rag", label: "📚 書摘問答" },
  { key: "ocr", label: "📷 拍照建摘文" },
];
const activeTab = ref("rag");

// ── Ollama status ──
const ollamaOk = ref(false);
const activeModel = ref("");
const ollamaHasVision = ref(false);

async function checkOllama() {
  const token = await getToken(); if (!token) return;
  // Check via a simple fetch to avoid CORS (via server)
  try {
    const res = await $fetch<any>("/api/ai/rag", {
      method: "POST",
      body: { question: "_ping_", topK: 1 },
      headers: { Authorization: `Bearer ${token}` },
    }).catch((e: any) => e.data ?? null);
    ollamaOk.value = true;
    activeModel.value = res?.model ?? "qwen2.5:7b";
  } catch { ollamaOk.value = false; }
}

// ── Auth helper ──
async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

// ── RAG ──
const ragQuestion = ref("");
const ragLoading = ref(false);
const ragAnswer = ref("");
const ragSources = ref<any[]>([]);
const ragError = ref("");

async function askRag() {
  if (!ragQuestion.value.trim()) return;
  ragLoading.value = true; ragAnswer.value = ""; ragSources.value = []; ragError.value = "";
  const token = await getToken(); if (!token) return;
  try {
    const data = await $fetch<any>("/api/ai/rag", {
      method: "POST",
      body: { question: ragQuestion.value, topK: 8 },
      headers: { Authorization: `Bearer ${token}` },
    });
    ragAnswer.value = data.answer;
    ragSources.value = data.sources ?? [];
    activeModel.value = data.model ?? activeModel.value;
    ollamaOk.value = true;
  } catch (e: any) {
    ragError.value = e.data?.message ?? e.message ?? "發生錯誤";
    ollamaOk.value = false;
  }
  ragLoading.value = false;
}

// ── OCR ──
const books = ref<any[]>([]);
const ocrFile = ref<File | null>(null);
const ocrPreview = ref("");
const ocrStartPage = ref(1);
const ocrBookId = ref("");
const ocrLoading = ref(false);
const ocrResult = ref<any>(null);
const ocrError = ref("");
const imageInput = ref<HTMLInputElement | null>(null);

function handleImageSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) setOcrFile(file);
}
function handleImageDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0];
  if (file) setOcrFile(file);
}
function setOcrFile(file: File) {
  ocrFile.value = file;
  const reader = new FileReader();
  reader.onload = (e) => { ocrPreview.value = e.target?.result as string; };
  reader.readAsDataURL(file);
}

async function runOCR() {
  if (!ocrFile.value) return;
  ocrLoading.value = true; ocrResult.value = null; ocrError.value = "";
  const token = await getToken(); if (!token) return;

  const fd = new FormData();
  fd.append("image", ocrFile.value);
  fd.append("startPage", String(ocrStartPage.value));
  if (ocrBookId.value) fd.append("bookId", ocrBookId.value);

  try {
    ocrResult.value = await $fetch<any>("/api/ai/ocr", {
      method: "POST",
      body: fd,
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    ocrError.value = e.data?.message ?? e.message ?? "OCR 失敗";
  }
  ocrLoading.value = false;
}

async function loadBooks() {
  const token = await getToken(); if (!token) return;
  books.value = await $fetch<any[]>("/api/books", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
}

onMounted(async () => {
  await loadBooks();
  await checkOllama();
});

useHead({ title: "AI 研究助理 — Know Graph Lab" });
</script>
