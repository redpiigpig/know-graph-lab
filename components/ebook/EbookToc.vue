<template>
  <div class="p-3">
    <div class="text-xs uppercase text-stone-400 mb-2 px-2 tracking-wider">目錄</div>
    <div v-if="!hasAnyGroup && loading" class="text-stone-400 text-sm px-2 py-2">載入中…</div>

    <!-- ── 退化模式：逐頁書（chunk_type='page'、無章節結構）──
         群組資料全空時，改為「每 10 頁一節」的自動骨架 + 頁碼跳轉輸入框，
         讓 37% 沒有目錄的藏書側欄不再一片空白。 -->
    <template v-else-if="!hasAnyGroup && totalPages > 0">
      <div class="mb-3 px-1">
        <label class="block text-xs font-medium text-stone-600 mb-1">跳至頁碼</label>
        <div class="flex gap-1.5">
          <input v-model.number="quickJumpPage" @keyup.enter="onQuickJump" type="number" :min="1" :max="totalPages"
            :placeholder="`1–${totalPages}`"
            class="flex-1 min-w-0 bg-white border-2 border-blue-300 rounded-lg px-2 py-1.5 text-sm text-center focus:outline-none focus:border-blue-500" />
          <button @click="onQuickJump"
            class="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs hover:bg-blue-500 transition flex-shrink-0">跳頁</button>
        </div>
        <p class="text-[11px] text-stone-400 mt-1.5 leading-relaxed">本書無章節目錄，以下每 10 頁一節</p>
      </div>
      <div class="space-y-0.5">
        <a v-for="b in pageBuckets" :key="b.start"
          :href="`?page=${b.start}`"
          @click.prevent="emit('jump', b.start)"
          :class="['w-full flex items-center gap-1.5 px-2 py-1.5 rounded text-sm transition no-underline',
            currentPage >= b.start && currentPage <= b.end
              ? 'bg-blue-50 text-blue-700 font-medium' : 'text-stone-600 hover:bg-stone-50']">
          <span class="flex-1 text-left truncate">第 {{ b.start }}–{{ b.end }} 頁</span>
          <span v-if="bucketBookmark(b)"
            class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
            📅 {{ fmtBookmarkDate(bucketBookmark(b)!.created_at) }}
          </span>
        </a>
      </div>
    </template>

    <template v-else>
      <!-- 卷首（無 volume 的 chunk：封面／序言／索引）。索引類條目折成
           單一「索引」折疊群組，避免佔滿列表頂部。 -->
      <div v-if="frontMatterMain.length || indexEntries.length" class="space-y-0.5 mb-3">
        <template v-for="entry in frontMatterMain" :key="entry.chunk_index">
          <div class="group relative">
            <a :href="`?page=${entry.chunk_index + 1}`"
              @click.prevent="emit('jump', entry.chunk_index + 1)"
              :title="entry.title"
              :class="[entryCls(entry), 'w-full flex items-center gap-1.5 no-underline']">
              <span class="flex-1 text-left truncate">{{ entry.title }}</span>
              <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
              </span>
            </a>
            <button v-if="bookmarkByChunk.get(entry.chunk_index)"
              @click.stop="emit('delete-bookmark', bookmarkByChunk.get(entry.chunk_index)!.id)"
              title="移除書籤"
              class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
          </div>
          <!-- 目前開啟章節內的小節錨點 -->
          <div v-if="entry.chunk_index === currentPage - 1 && entry.sections?.length"
            class="space-y-px ml-1 border-l border-stone-200 pl-2 pb-1 mb-1">
            <a v-for="sec in entry.sections" :key="sec.anchor_id"
              :href="`#${sec.anchor_id}`"
              @click.prevent="emit('jump-section', sec.anchor_id)"
              :title="sec.title"
              :class="['block w-full text-left py-1 rounded text-xs text-stone-500 hover:bg-stone-50 hover:text-stone-900 truncate no-underline',
                sec.level === 3 ? 'pl-2' : 'pl-5 text-[11px] text-stone-400']">
              <span class="text-stone-300 mr-1">›</span>{{ sec.title }}
            </a>
          </div>
        </template>

        <!-- 「索引」折疊群組 -->
        <div v-if="indexEntries.length" class="mt-1">
          <button @click="indexExpanded = !indexExpanded"
            class="w-full flex items-center gap-1 px-2 py-2 rounded text-sm font-medium text-stone-700 hover:bg-stone-50 transition">
            <span class="text-stone-400 text-xs w-3 inline-block">{{ indexExpanded ? '▾' : '▸' }}</span>
            <span class="flex-1 text-left">索引</span>
            <span class="text-xs text-stone-400">{{ indexEntries.length }}</span>
          </button>
          <div v-if="indexExpanded" class="space-y-0.5 mt-0.5 ml-1 border-l border-stone-200 pl-2">
            <div v-for="entry in indexEntries" :key="entry.chunk_index" class="group relative">
              <a :href="`?page=${entry.chunk_index + 1}`"
                @click.prevent="emit('jump', entry.chunk_index + 1)"
                :title="entry.title"
                :class="[entryCls(entry), 'w-full flex items-center gap-1.5 no-underline']">
                <span class="flex-1 text-left truncate">{{ entry.title }}</span>
                <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                  class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                  📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                </span>
              </a>
              <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                @click.stop="emit('delete-bookmark', bookmarkByChunk.get(entry.chunk_index)!.id)"
                title="移除書籤"
                class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 卷列表：三層（parent → volume → entry）或兩層（volume → entry）
           共用同一份 markup — 無 parent 的書合成單一匿名群組攤平呈現。 -->
      <div v-for="p in normalizedGroups" :key="p.name ?? '__none__'" :class="p.name ? 'mb-2' : ''">
        <button v-if="p.name" @click="toggleParent(p.name)"
          class="w-full flex items-center gap-1 px-2 py-2 rounded text-[15px] font-semibold text-stone-900 hover:bg-stone-100 transition">
          <span class="text-stone-500 text-xs w-3 inline-block">{{ expandedParents.has(p.name) ? '▾' : '▸' }}</span>
          <span class="flex-1 text-left truncate">{{ p.name }}</span>
          <span class="text-[11px] text-stone-400">{{ p.volumes.length }}</span>
        </button>
        <div v-if="!p.name || expandedParents.has(p.name)"
          :class="p.name ? 'ml-3 mt-0.5 space-y-0.5 border-l border-stone-200 pl-1' : ''">
          <div v-for="v in p.volumes" :key="v.name" class="mb-1">
            <!-- 單頁卷 → 直接連結；多頁卷 → ▸ 折疊按鈕 + 巢狀條目 -->
            <a v-if="v.entries.length === 1"
              :href="`?page=${v.entries[0].chunk_index + 1}`"
              @click.prevent="emit('jump', v.entries[0].chunk_index + 1)"
              :title="v.name"
              :class="[
                'w-full flex items-center gap-1 px-2 rounded hover:bg-stone-50 transition no-underline',
                p.name ? 'py-1.5 text-sm' : 'py-2 text-sm font-medium',
                currentPage - 1 === v.entries[0].chunk_index
                  ? (p.name ? 'bg-blue-50 text-blue-700 font-medium' : 'bg-blue-50 text-blue-700')
                  : (p.name ? 'text-stone-800' : 'text-stone-900')
              ]">
              <span class="text-stone-300 text-xs w-3 inline-block">·</span>
              <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
            </a>
            <button v-else @click="toggleVolume(v.name)"
              :class="['w-full flex items-center gap-1 px-2 rounded hover:bg-stone-50 transition',
                p.name ? 'py-1.5 text-sm text-stone-800' : 'py-2 text-sm font-medium text-stone-900']">
              <span class="text-stone-400 text-xs w-3 inline-block">{{ expandedVolumes.has(v.name) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
              <span class="text-xs text-stone-400">{{ v.entries.length }}</span>
            </button>
            <div v-if="v.entries.length > 1 && expandedVolumes.has(v.name)" class="space-y-0.5 mt-0.5">
              <template v-for="entry in v.entries" :key="entry.chunk_index">
                <div class="group relative">
                  <a :href="`?page=${entry.chunk_index + 1}`"
                    @click.prevent="emit('jump', entry.chunk_index + 1)"
                    :title="entry.title"
                    :class="[entryCls(entry), 'w-full flex items-center gap-1.5 no-underline']">
                    <span class="flex-1 text-left truncate">{{ stripVolumePrefix(entry.title, v.name) }}</span>
                    <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                      class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                      📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                    </span>
                  </a>
                  <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                    @click.stop="emit('delete-bookmark', bookmarkByChunk.get(entry.chunk_index)!.id)"
                    title="移除書籤"
                    class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
                </div>
                <div v-if="entry.chunk_index === currentPage - 1 && entry.sections?.length"
                  class="space-y-px ml-1 border-l border-stone-200 pl-2 pb-1">
                  <a v-for="sec in entry.sections" :key="sec.anchor_id"
                    :href="`#${sec.anchor_id}`"
                    @click.prevent="emit('jump-section', sec.anchor_id)"
                    :title="sec.title"
                    :class="['block w-full text-left py-1 rounded text-xs text-stone-500 hover:bg-stone-50 hover:text-stone-900 truncate no-underline',
                      sec.level === 3 ? 'pl-2' : 'pl-5 text-[11px] text-stone-400']">
                    <span class="text-stone-300 mr-1">›</span>{{ sec.title }}
                  </a>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
// ── EbookToc — ebook reader 左側目錄側欄 ──
// 把 pages/ebook/[id].vue 原本三段幾乎相同的折疊 markup（卷首群組／
// parent→volume→entry 三層／legacy 兩層攤平）收成單一元件。
// State 契約：群組資料由頁面正規化後 props down；點擊行為 emits up
// （jump / jump-section / delete-bookmark），handler 本體留在頁面。
// 展開狀態（expandedParents / expandedVolumes / indexExpanded）屬純
// UI 狀態，收在元件內部；初始展開邏輯與原頁面一致 —— parent 預設全
// 收合、目前 chunk 所在的卷與 parent 自動展開、展開紀錄跨換頁累積。

// 型別與頁面內的宣告結構相同（structural typing，頁面物件可直接傳入）。
interface TocSection { anchor_id: string; title: string; level: number }
interface TocEntry {
  chunk_index: number;
  title: string;
  level: number;
  volume?: string | null;
  parent_volume?: string | null;
  sections?: TocSection[];
}
interface VolumeGroup { name: string; entries: TocEntry[] }
interface ParentGroup { name: string | null; volumes: VolumeGroup[] }
interface Bookmark { id: string; chunk_index: number; created_at: string }

const props = defineProps<{
  /** 卷首條目（無 volume、非索引：封面／序言等） */
  frontMatterMain: TocEntry[];
  /** 索引類條目（折成單一「索引」群組） */
  indexEntries: TocEntry[];
  /** 三層群組（parent_volume → volumes → entries） */
  parentGroups: ParentGroup[];
  /** 兩層群組（volume → entries；無 parent 的舊書用） */
  volumes: VolumeGroup[];
  /** 本書是否有 parent_volume 層 */
  hasParentLevel: boolean;
  /** 目前頁碼（1-indexed；chunk_index = currentPage - 1） */
  currentPage: number;
  /** 總頁數（退化模式的骨架用） */
  totalPages: number;
  /** 頁面載入中 */
  loading: boolean;
  /** 書名（縮短卷名的前綴剝除用） */
  bookTitle: string;
  /** chunk_index → 最新書籤（📅 徽章） */
  bookmarkByChunk: Map<number, Bookmark>;
}>();

const emit = defineEmits<{
  (e: "jump", page: number): void;
  (e: "jump-section", anchorId: string): void;
  (e: "delete-bookmark", id: string): void;
}>();

// ── 展開狀態（元件內部 UI 狀態） ──
const expandedVolumes = ref<Set<string>>(new Set());
const expandedParents = ref<Set<string>>(new Set());
const indexExpanded = ref(false);

function toggleVolume(name: string) {
  const next = new Set(expandedVolumes.value);
  if (next.has(name)) next.delete(name);
  else next.add(name);
  expandedVolumes.value = next;
}
function toggleParent(name: string) {
  const next = new Set(expandedParents.value);
  if (next.has(name)) next.delete(name);
  else next.add(name);
  expandedParents.value = next;
}

// 目前 chunk 所在的卷 + parent 自動展開（原頁面在 loadPage 後做同一件事；
// 這裡改成 watch，換頁時觸發，展開紀錄跨換頁累積、不重設）。
watch(
  () => [props.currentPage, props.volumes] as const,
  () => {
    const idx = props.currentPage - 1;
    for (const v of props.volumes) {
      const hit = v.entries.find((e) => e.chunk_index === idx);
      if (!hit) continue;
      if (!expandedVolumes.value.has(v.name)) {
        expandedVolumes.value = new Set([...expandedVolumes.value, v.name]);
      }
      if (hit.parent_volume && !expandedParents.value.has(hit.parent_volume)) {
        expandedParents.value = new Set([...expandedParents.value, hit.parent_volume]);
      }
      break;
    }
  },
  { immediate: true }
);

// ── 群組正規化 ──
// 三層書直接用 parentGroups；兩層書合成單一匿名群組（name=null → 攤平），
// 讓模板只需要一份卷列表 markup。
const normalizedGroups = computed<ParentGroup[]>(() =>
  props.hasParentLevel ? props.parentGroups : [{ name: null, volumes: props.volumes }]
);

const hasAnyGroup = computed(
  () => props.frontMatterMain.length > 0 || props.indexEntries.length > 0 || props.volumes.length > 0
);

// ── 退化模式（逐頁書）──
const quickJumpPage = ref<number | null>(null);
function onQuickJump() {
  const p = quickJumpPage.value;
  if (typeof p === "number" && Number.isFinite(p)) emit("jump", p);
}
// 每 10 頁一節的自動骨架。
const pageBuckets = computed(() => {
  const out: { start: number; end: number }[] = [];
  for (let s = 1; s <= props.totalPages; s += 10) {
    out.push({ start: s, end: Math.min(s + 9, props.totalPages) });
  }
  return out;
});
// 該 10 頁區間內最新的書籤（退化模式也保留 📅 徽章視覺）。
function bucketBookmark(b: { start: number; end: number }): Bookmark | null {
  for (let i = b.start - 1; i < b.end; i++) {
    const bm = props.bookmarkByChunk.get(i);
    if (bm) return bm;
  }
  return null;
}

// ── 顯示輔助（與原頁面同邏輯） ──
function fmtBookmarkDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}
// 剝掉卷名前面的書名前綴，側欄顯示較精簡。
function shortVolumeName(name: string): string {
  const t = props.bookTitle;
  if (t && name.startsWith(t + "：")) return name.slice(t.length + 1);
  if (t && name.startsWith(t + ":")) return name.slice(t.length + 1);
  return name;
}
// 剝掉條目標題裡重複的卷名前綴（卷名已在上一列顯示過）。
function stripVolumePrefix(entryTitle: string, volumeName: string): string {
  if (entryTitle.startsWith(volumeName)) {
    return entryTitle.slice(volumeName.length).trim().replace(/^[—－·,，:：]+\s*/, "");
  }
  return entryTitle;
}
// 條目列樣式（依層級縮排；目前頁高亮）。
function entryCls(entry: TocEntry) {
  const isActive = entry.chunk_index === props.currentPage - 1;
  return [
    "w-full text-left py-1.5 rounded text-sm transition truncate block",
    isActive ? "bg-blue-50 text-blue-700 font-medium" : "text-stone-600 hover:bg-stone-50",
    entry.level === 2 ? "pl-3" : entry.level === 3 ? "pl-7" : "pl-11 text-xs",
  ];
}
</script>
