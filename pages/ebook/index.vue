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

    <div class="max-w-6xl mx-auto px-6 py-8 flex gap-6">

      <!-- 分類側欄 -->
      <aside class="w-56 flex-shrink-0 sticky top-20 self-start max-h-[calc(100vh-5rem)] overflow-y-auto">
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-2 px-2">分類</p>
        <nav class="space-y-0.5 pb-8">
          <!-- 全部 -->
          <button @click="selectAll"
            :class="['w-full text-left px-2 py-1.5 rounded-lg text-sm transition flex items-center gap-2',
              !activeCategory ? 'bg-blue-900/60 text-blue-200' : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
            <span>📚</span><span>全部</span>
          </button>

          <div v-for="cat in CATEGORY_TREE" :key="cat.value">
            <!-- 分類標題 -->
            <button @click="clickCategory(cat)"
              :class="['w-full text-left px-2 py-1.5 rounded-lg text-sm transition flex items-center gap-1.5',
                activeCategory === cat.value && !activeSubcategory
                  ? 'bg-blue-900/60 text-blue-200'
                  : activeCategory === cat.value
                    ? 'text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
              <span>{{ cat.icon }}</span>
              <span class="flex-1 truncate">{{ cat.value }}</span>
              <span v-if="cat.children.length" class="text-gray-600 text-xs flex-shrink-0">
                {{ expandedCategory === cat.value ? '▾' : '▸' }}
              </span>
            </button>

            <!-- 子分類 -->
            <div v-if="expandedCategory === cat.value && cat.children.length"
              class="ml-2 mt-0.5 space-y-0.5 border-l border-gray-800 pl-2">
              <template v-for="child in cat.children" :key="typeof child === 'string' ? child : child.group">

                <!-- leaf 子分類 -->
                <button v-if="typeof child === 'string'"
                  @click="selectSub(cat.value, child)"
                  :class="['w-full text-left px-2 py-1 rounded text-xs transition truncate',
                    activeCategory === cat.value && activeSubcategory === child
                      ? 'bg-blue-900/50 text-blue-300'
                      : 'text-gray-500 hover:bg-gray-800 hover:text-white']">
                  {{ child }}
                </button>

                <!-- 有子群的分類 (基督教) -->
                <div v-else>
                  <button @click="clickGroup(cat.value, child)"
                    :class="['w-full text-left px-2 py-1 rounded text-xs transition flex items-center gap-1',
                      activeCategory === cat.value && activeSubcategory.startsWith(child.group)
                        ? 'bg-blue-900/50 text-blue-300'
                        : 'text-gray-500 hover:bg-gray-800 hover:text-white']">
                    <span class="flex-1 truncate">{{ child.group }}</span>
                    <span class="text-gray-600 flex-shrink-0">{{ expandedGroup === child.group ? '▾' : '▸' }}</span>
                  </button>
                  <div v-if="expandedGroup === child.group"
                    class="ml-2 mt-0.5 space-y-0.5 border-l border-gray-700 pl-2">
                    <button v-for="sub in child.children" :key="sub"
                      @click="selectSub(cat.value, `${child.group}/${sub}`)"
                      :class="['w-full text-left px-2 py-1 rounded text-xs transition truncate',
                        activeSubcategory === `${child.group}/${sub}`
                          ? 'bg-blue-900/50 text-blue-300'
                          : 'text-gray-500 hover:bg-gray-800 hover:text-white']">
                      {{ sub }}
                    </button>
                  </div>
                </div>

              </template>
            </div>
          </div>
        </nav>
      </aside>

      <!-- 主內容 -->
      <div class="flex-1 min-w-0">
        <!-- 搜尋列 -->
        <div class="flex gap-3 mb-6">
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
          <div class="flex items-center justify-between mb-4">
            <p class="text-sm text-gray-400">
              {{ activeLabel }}
              <span v-if="!loading" class="text-gray-600">（{{ ebooks.length }} 本）</span>
            </p>
          </div>

          <div v-if="loading" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="i in 6" :key="i" class="bg-gray-900 rounded-xl border border-gray-800 p-5 h-28 animate-pulse"></div>
          </div>

          <div v-else-if="ebooks.length === 0" class="text-center py-20 text-gray-500">
            <p class="text-4xl mb-4">📚</p>
            <p class="text-lg mb-2">{{ activeCategory ? '此分類尚無書籍' : '書架還是空的' }}</p>
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
                  <div class="flex items-center gap-2 mt-2 flex-wrap">
                    <span v-if="ebook.subcategory || ebook.category"
                      class="text-xs bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded">
                      {{ ebook.subcategory ? ebook.subcategory.split('/').pop() : ebook.category }}
                    </span>
                    <span class="text-xs text-gray-600">{{ ebook.total_pages }} 頁</span>
                    <span class="text-xs uppercase text-gray-700">{{ ebook.file_type }}</span>
                  </div>
                </div>
              </div>
            </NuxtLink>
          </div>
        </template>
      </div>
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

        <!-- 大分類 -->
        <select v-model="uploadCategory" @change="uploadSubcategory = ''; uploadSubSubcategory = ''"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500">
          <option value="">選擇大分類（選填）</option>
          <option v-for="cat in CATEGORY_TREE" :key="cat.value" :value="cat.value">
            {{ cat.icon }} {{ cat.value }}
          </option>
        </select>

        <!-- 子分類 -->
        <select v-if="uploadSubcategoryOptions.length" v-model="uploadSubcategory" @change="uploadSubSubcategory = ''"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500">
          <option value="">選擇子分類</option>
          <option v-for="opt in uploadSubcategoryOptions" :key="opt" :value="opt">{{ opt }}</option>
        </select>

        <!-- 細分類（僅基督教等有三層的情況） -->
        <select v-if="uploadSubSubcategoryOptions.length" v-model="uploadSubSubcategory"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500">
          <option value="">選擇細分類</option>
          <option v-for="opt in uploadSubSubcategoryOptions" :key="opt" :value="opt">{{ opt }}</option>
        </select>

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

interface SubGroup { group: string; children: string[] }
type SubItem = string | SubGroup
interface CategoryDef { value: string; icon: string; children: SubItem[] }

const CATEGORY_TREE: CategoryDef[] = [
  { value: "哲學", icon: "🔭", children: [
    "黎明，西洋哲學史", "近代哲學", "經典與解釋輯刊", "當代哲學", "哲學通史", "哲學原典", "中國思想史",
  ]},
  { value: "宗教學", icon: "📖", children: [
    "神話學", "宗教對話", "宗教史", "World Religions系列",
  ]},
  { value: "世界宗教", icon: "🕌", children: [
    "猶太教", "波斯宗教", "東亞宗教", "摩門教",
    { group: "基督教", children: ["聖經研究", "神學原典", "神學", "教會史"] },
    "其他宗教", "佛教", "伊斯蘭教",
  ]},
  { value: "心理學", icon: "🧠", children: ["生死學"] },
  { value: "人類生物學", icon: "🧬", children: [
    "生物學", "人類起源與進化史", "人類文化-語言學", "人類大歷史",
  ]},
  { value: "自然科學", icon: "🔬", children: [] },
  { value: "歷史學", icon: "📜", children: [
    "近代史", "西方界域史", "美州界域史", "東方界域史",
    "史料原典", "史學理論", "全球通史", "亞太界域史", "中央界域史",
  ]},
  { value: "文學", icon: "✍️", children: [] },
  { value: "社會政治學", icon: "🏛️", children: [
    "資本主義-社會主義", "知識社會學", "政治學", "性學", "名家作品",
  ]},
]

const supabase = useSupabaseClient();
const router = useRouter();

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

// ── 側欄導航狀態 ──
const expandedCategory = ref("")
const expandedGroup = ref("")
const activeCategory = ref("")
const activeSubcategory = ref("")

const activeLabel = computed(() => {
  if (!activeCategory.value) return "📚 全部"
  const cat = CATEGORY_TREE.find(c => c.value === activeCategory.value)
  if (!activeSubcategory.value) return `${cat?.icon} ${activeCategory.value}`
  return `${cat?.icon} ${activeCategory.value} › ${activeSubcategory.value.split("/").join(" › ")}`
})

function selectAll() {
  activeCategory.value = ""
  activeSubcategory.value = ""
  expandedCategory.value = ""
  expandedGroup.value = ""
  searchResults.value = []
  loadEbooks()
}

function clickCategory(cat: CategoryDef) {
  activeCategory.value = cat.value
  activeSubcategory.value = ""
  expandedCategory.value = expandedCategory.value === cat.value ? "" : cat.value
  expandedGroup.value = ""
  searchResults.value = []
  loadEbooks()
}

function clickGroup(catValue: string, child: SubGroup) {
  activeCategory.value = catValue
  activeSubcategory.value = child.group
  expandedGroup.value = expandedGroup.value === child.group ? "" : child.group
  searchResults.value = []
  loadEbooks()
}

function selectSub(catValue: string, sub: string) {
  activeCategory.value = catValue
  activeSubcategory.value = sub
  searchResults.value = []
  loadEbooks()
}

// ── 資料 ──
const loading = ref(true);
const ebooks = ref<any[]>([]);
const searchQ = ref("");
const searchResults = ref<any[]>([]);

async function loadEbooks() {
  loading.value = true;
  const token = await getToken(); if (!token) return;
  const params = new URLSearchParams()
  if (activeCategory.value) params.set("category", activeCategory.value)
  if (activeSubcategory.value) params.set("subcategory", activeSubcategory.value)
  const qs = params.size ? "?" + params.toString() : ""
  ebooks.value = await $fetch<any[]>(`/api/ebooks${qs}`, {
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

// ── 上傳 ──
const showUpload = ref(false);
const uploadFile = ref<File | null>(null);
const uploadTitle = ref("");
const uploadAuthor = ref("");
const uploadCategory = ref("");
const uploadSubcategory = ref("");
const uploadSubSubcategory = ref("");
const uploading = ref(false);
const uploadProgress = ref("");
const uploadError = ref("");
const fileInput = ref<HTMLInputElement | null>(null);

const uploadSubcategoryOptions = computed(() => {
  if (!uploadCategory.value) return []
  const cat = CATEGORY_TREE.find(c => c.value === uploadCategory.value)
  return (cat?.children ?? []).map(c => typeof c === "string" ? c : c.group)
})

const uploadSubSubcategoryOptions = computed(() => {
  if (!uploadSubcategory.value || !uploadCategory.value) return []
  const cat = CATEGORY_TREE.find(c => c.value === uploadCategory.value)
  const sub = cat?.children.find(c => typeof c === "object" && c.group === uploadSubcategory.value)
  return typeof sub === "object" ? (sub as SubGroup).children : []
})

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
  if (uploadCategory.value) fd.append("category", uploadCategory.value);
  const finalSub = uploadSubSubcategory.value
    ? `${uploadSubcategory.value}/${uploadSubSubcategory.value}`
    : uploadSubcategory.value
  if (finalSub) fd.append("subcategory", finalSub);

  try {
    uploadProgress.value = "（解析中…）";
    const result = await $fetch<any>("/api/ebooks/upload", {
      method: "POST", body: fd,
      headers: { Authorization: `Bearer ${token}` },
    });
    showUpload.value = false;
    uploadFile.value = null; uploadTitle.value = ""; uploadAuthor.value = "";
    uploadCategory.value = ""; uploadSubcategory.value = ""; uploadSubSubcategory.value = "";
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
