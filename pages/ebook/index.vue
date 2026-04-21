<template>
  <div class="min-h-screen bg-gray-950 text-white">
    <nav class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="text-gray-400 hover:text-white text-sm transition">← 工作台</NuxtLink>
          <span class="text-gray-600">·</span>
          <span class="font-semibold text-sm">電子圖書館</span>
        </div>
        <button @click="showUpload = true"
          class="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition">
          + 上傳電子書
        </button>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8">

      <!-- 搜尋列 -->
      <div class="flex gap-3 mb-8">
        <div class="relative flex-1">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input v-model="searchQ" @keyup.enter="runSearch" type="text"
            placeholder="全文搜尋電子書內容…"
            class="w-full bg-gray-900 border border-gray-700 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm" />
        </div>
        <button @click="runSearch" :disabled="!searchQ.trim()"
          class="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-xl text-sm transition">搜尋</button>
      </div>

      <!-- 搜尋結果 -->
      <template v-if="searchResults.length">
        <div class="mb-6">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm text-gray-400">找到 {{ searchResults.length }} 個相關段落</p>
            <button @click="searchResults = []; searchQ = ''" class="text-xs text-gray-500 hover:text-white transition">清除</button>
          </div>
          <div class="space-y-3">
            <NuxtLink v-for="r in searchResults" :key="r.id"
              :to="`/ebook/${r.ebook_id}?page=${r.page_number}`"
              class="block bg-gray-900 border border-gray-800 hover:border-blue-600 rounded-xl p-4 transition">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded">第 {{ r.page_number }} 頁</span>
                <span class="text-xs text-gray-500">{{ r.ebooks?.title }}</span>
                <span v-if="r.matchType === 'semantic'" class="text-xs bg-purple-900 text-purple-300 px-1.5 rounded">語義</span>
              </div>
              <p class="text-sm text-gray-300 line-clamp-3 leading-relaxed">{{ r.content }}</p>
            </NuxtLink>
          </div>
        </div>
      </template>

      <!-- 書架 -->
      <template v-else>
        <div v-if="loading" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="i in 6" :key="i" class="bg-gray-900 rounded-xl border border-gray-800 p-5 h-28 animate-pulse"></div>
        </div>

        <div v-else-if="ebooks.length === 0" class="text-center py-20 text-gray-500">
          <p class="text-4xl mb-4">📚</p>
          <p class="text-lg mb-2">書架還是空的</p>
          <p class="text-sm mb-6">上傳 PDF 或 EPUB 開始建立你的電子圖書館</p>
          <button @click="showUpload = true" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm transition">
            上傳第一本書
          </button>
        </div>

        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <NuxtLink v-for="ebook in ebooks" :key="ebook.id" :to="`/ebook/${ebook.id}`"
            class="group bg-gray-900 border border-gray-800 hover:border-blue-600 rounded-xl p-5 transition">
            <div class="flex items-start gap-4">
              <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0',
                ebook.file_type === 'pdf' ? 'bg-red-950' : 'bg-emerald-950']">
                {{ ebook.file_type === 'pdf' ? '📕' : '📗' }}
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-medium text-sm text-white group-hover:text-blue-400 transition line-clamp-2 leading-snug">{{ ebook.title }}</h3>
                <p class="text-xs text-gray-500 mt-0.5">{{ ebook.author }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="text-xs text-gray-600">{{ ebook.total_pages }} 頁</span>
                  <span class="text-xs uppercase text-gray-700">{{ ebook.file_type }}</span>
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>
      </template>
    </div>

    <!-- 上傳 Modal -->
    <div v-if="showUpload" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div class="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold">上傳電子書</h3>
          <button @click="showUpload = false" class="text-gray-400 hover:text-white text-xl leading-none">×</button>
        </div>

        <div
          @dragover.prevent @drop.prevent="handleFileDrop"
          @click="fileInput?.click()"
          class="border-2 border-dashed border-gray-700 hover:border-blue-500 rounded-xl p-8 text-center cursor-pointer transition">
          <p v-if="uploadFile" class="text-green-400 text-sm">✓ {{ uploadFile.name }}</p>
          <div v-else class="text-gray-500">
            <p class="text-3xl mb-2">📂</p>
            <p class="text-sm">點擊或拖曳 PDF / EPUB</p>
          </div>
        </div>
        <input ref="fileInput" type="file" accept=".pdf,.epub" class="hidden" @change="handleFileSelect" />

        <input v-model="uploadTitle" placeholder="書名（可自動從檔名讀取）"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500" />
        <input v-model="uploadAuthor" placeholder="作者（選填）"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500" />

        <button @click="doUpload" :disabled="!uploadFile || uploading"
          class="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-xl text-sm font-medium transition">
          {{ uploading ? `上傳解析中… ${uploadProgress}` : '開始上傳' }}
        </button>

        <p v-if="uploadError" class="text-red-400 text-xs">{{ uploadError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

const loading = ref(true);
const ebooks = ref<any[]>([]);
const searchQ = ref("");
const searchResults = ref<any[]>([]);

async function loadEbooks() {
  loading.value = true;
  const token = await getToken(); if (!token) return;
  ebooks.value = await $fetch<any[]>("/api/ebooks", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  loading.value = false;
}

async function runSearch() {
  if (!searchQ.value.trim()) return;
  const token = await getToken(); if (!token) return;
  searchResults.value = await $fetch<any[]>(`/api/ebooks/search?q=${encodeURIComponent(searchQ.value)}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
}

// ── Upload ──
const showUpload = ref(false);
const uploadFile = ref<File | null>(null);
const uploadTitle = ref("");
const uploadAuthor = ref("");
const uploading = ref(false);
const uploadProgress = ref("");
const uploadError = ref("");
const fileInput = ref<HTMLInputElement | null>(null);

function handleFileSelect(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0];
  if (f) setUploadFile(f);
}
function handleFileDrop(e: DragEvent) {
  const f = e.dataTransfer?.files?.[0];
  if (f) setUploadFile(f);
}
function setUploadFile(f: File) {
  uploadFile.value = f;
  if (!uploadTitle.value) uploadTitle.value = f.name.replace(/\.(pdf|epub)$/i, "");
}

async function doUpload() {
  if (!uploadFile.value) return;
  uploading.value = true; uploadError.value = ""; uploadProgress.value = "";
  const token = await getToken(); if (!token) return;

  const fd = new FormData();
  fd.append("file", uploadFile.value);
  fd.append("title", uploadTitle.value || uploadFile.value.name);
  if (uploadAuthor.value) fd.append("author", uploadAuthor.value);

  try {
    uploadProgress.value = "（解析中…）";
    const result = await $fetch<any>("/api/ebooks/upload", {
      method: "POST", body: fd,
      headers: { Authorization: `Bearer ${token}` },
    });
    showUpload.value = false;
    uploadFile.value = null; uploadTitle.value = ""; uploadAuthor.value = "";
    await loadEbooks();
    router.push(`/ebook/${result.ebook_id}`);
  } catch (e: any) {
    uploadError.value = e.data?.message ?? e.message ?? "上傳失敗";
  }
  uploading.value = false;
}

onMounted(loadEbooks);
useHead({ title: "電子圖書館 — Know Graph Lab" });
</script>
