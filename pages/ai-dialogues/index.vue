<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col"
    @click="quickCatTarget = null"
  >
    <AppHeader title="AI 對話錄" :back="{ to: '/', label: '返回主頁' }" :editable="false">
      <template #actions>
        <button
          ref="lookupTrigger"
          type="button"
          class="whitespace-nowrap text-xs px-2.5 py-1 rounded border border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:text-blue-600 transition"
          aria-haspopup="dialog"
          @click="openLookup"
        >
          代碼查詢
        </button>
        <span class="hidden text-xs text-gray-400 sm:inline">{{ totalCount }} 筆對話</span>
      </template>
    </AppHeader>

    <div class="flex flex-1 max-w-7xl mx-auto w-full px-6 py-6 gap-6">
      <!-- Left sidebar -->
      <aside class="w-52 shrink-0">
        <!-- Source section -->
        <div class="mb-6">
          <span
            class="text-xs font-semibold text-gray-400 uppercase tracking-wide block mb-2"
            >來源</span
          >
          <button
            @click="selectFilter('source:all')"
            :class="[
              'w-full text-left px-3 py-1.5 rounded-lg text-sm transition',
              activeFilter === 'source:all'
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-gray-600 hover:bg-gray-100',
            ]"
          >
            全部
          </button>
          <button
            @click="selectFilter('source:gemini')"
            :class="[
              'w-full text-left px-3 py-1.5 rounded-lg text-sm transition flex items-center justify-between',
              activeFilter === 'source:gemini'
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-gray-600 hover:bg-gray-100',
            ]"
          >
            <span>Gemini</span>
            <span class="text-xs text-gray-400">{{
              sourceCount("gemini")
            }}</span>
          </button>
          <button
            @click="selectFilter('source:chatgpt')"
            :class="[
              'w-full text-left px-3 py-1.5 rounded-lg text-sm transition flex items-center justify-between',
              activeFilter === 'source:chatgpt'
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-gray-600 hover:bg-gray-100',
            ]"
          >
            <span>ChatGPT</span>
            <span class="text-xs text-gray-400">{{
              sourceCount("chatgpt")
            }}</span>
          </button>
        </div>

        <div class="my-2 border-t border-gray-100"></div>

        <!-- Categories section -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span
              class="text-xs font-semibold text-gray-400 uppercase tracking-wide"
              >分類</span
            >
            <button
              @click="showNewCategory = true"
              class="text-gray-400 hover:text-blue-600 transition text-lg leading-none"
            >
              +
            </button>
          </div>
          <button
            @click="selectFilter('all')"
            :class="[
              'w-full text-left px-3 py-1.5 rounded-lg text-sm transition flex items-center justify-between',
              activeFilter === 'all'
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-gray-600 hover:bg-gray-100',
            ]"
          >
            <span>全部</span>
          </button>

          <!-- Uncategorized / timeline -->
          <div class="group flex items-center gap-1">
            <button
              @click="selectFilter('uncategorized')"
              :class="[
                'flex-1 text-left px-3 py-1.5 rounded-lg text-sm transition flex items-center justify-between',
                activeFilter === 'uncategorized'
                  ? 'bg-slate-100 text-gray-900 font-medium'
                  : 'text-gray-500 hover:bg-gray-100',
              ]"
            >
              <span>純時間軸</span>
              <span class="text-xs text-gray-400">{{
                uncategorizedCount
              }}</span>
            </button>
            <button
              @click="clearUncategorized"
              class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs px-1"
              title="清空未分類"
            >
              ✕
            </button>
          </div>

          <div class="my-2 border-t border-gray-100"></div>

          <template v-for="cat in topLevelCategories" :key="cat.id">
            <div class="group flex items-center gap-0.5">
              <!-- expand chevron (only if has children) -->
              <button
                v-if="childrenOf(cat.id).length"
                @click="toggleCat(cat.id)"
                class="w-4 shrink-0 text-gray-400 hover:text-gray-600 transition text-xs"
              >
                {{ expandedCats.includes(cat.id) ? "▾" : "▸" }}
              </button>
              <span v-else class="w-4 shrink-0"></span>
              <button
                @click="selectFilter('cat:' + cat.id)"
                :class="[
                  'flex-1 text-left px-2 py-1.5 rounded-lg text-sm transition flex items-center gap-2 min-w-0',
                  activeFilter === 'cat:' + cat.id
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100',
                ]"
              >
                <span
                  :class="['w-2 h-2 rounded-full shrink-0', colorDot(cat.color)]"
                ></span>
                <span class="truncate">{{ cat.name }}</span>
              </button>
              <button
                @click="deleteCategory(cat)"
                class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs px-1"
              >
                ×
              </button>
            </div>
            <!-- children -->
            <div v-if="expandedCats.includes(cat.id)" class="ml-4">
              <div
                v-for="child in childrenOf(cat.id)"
                :key="child.id"
                class="group flex items-center gap-0.5"
              >
                <button
                  @click="selectFilter('cat:' + child.id)"
                  :class="[
                    'flex-1 text-left px-2 py-1 rounded-lg text-sm transition flex items-center gap-2 min-w-0',
                    activeFilter === 'cat:' + child.id
                      ? 'bg-blue-50 text-blue-700 font-medium'
                      : 'text-gray-500 hover:bg-gray-100',
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full shrink-0',
                      colorDot(child.color),
                    ]"
                  ></span>
                  <span class="truncate">{{ child.name }}</span>
                </button>
                <button
                  @click="deleteCategory(child)"
                  class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs px-1"
                >
                  ×
                </button>
              </div>
            </div>
          </template>
        </div>

        <!-- Month section -->
        <div>
          <span
            class="text-xs font-semibold text-gray-400 uppercase tracking-wide block mb-2"
            >月份</span
          >
          <div v-for="m in months" :key="m.month">
            <button
              @click="toggleMonth(m.month)"
              :class="[
                'w-full text-left px-3 py-1.5 rounded-lg text-sm transition flex items-center justify-between',
                activeFilter === 'month:' + m.month
                  ? 'bg-slate-100 text-gray-900 font-medium'
                  : 'text-gray-600 hover:bg-gray-100',
              ]"
            >
              <span>{{ formatMonth(m.month) }}</span>
              <span class="text-xs text-gray-400">{{ m.count }}</span>
            </button>
            <!-- Dates under expanded month -->
            <div v-if="expandedMonth === m.month" class="ml-3 mt-0.5 mb-1">
              <button
                v-for="d in datesForMonth(m.month)"
                :key="d.date"
                @click="selectFilter('date:' + d.date)"
                :class="[
                  'w-full text-left px-2 py-1 rounded text-xs transition flex items-center justify-between',
                  activeFilter === 'date:' + d.date
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-500 hover:bg-gray-100',
                ]"
              >
                <span>{{ d.date.slice(8) }} 日</span>
                <span class="text-gray-400">{{ d.count }}</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <main class="flex-1 min-w-0">
        <!-- Keyword search is the default search mode. Citation-code lookup lives behind the header button. -->
        <div class="mb-5 rounded-xl border border-gray-100 bg-white p-3 shadow-sm">
          <form class="flex flex-col gap-2 sm:flex-row sm:items-center" @submit.prevent="runKeywordSearch">
            <input
              v-model="keywordDraft"
              type="search"
              maxlength="160"
              autocomplete="off"
              placeholder="搜尋提問或回應的關鍵字"
              aria-label="搜尋對話關鍵字"
              class="w-full min-w-0 flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            />
            <div class="flex w-full gap-2 sm:w-auto">
              <button
                type="submit"
                :disabled="loading"
                class="flex-1 shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60 sm:flex-none"
              >
                搜尋
              </button>
              <button
                v-if="keywordQuery"
                type="button"
                :disabled="loading"
                class="flex-1 shrink-0 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-500 transition hover:bg-gray-50 disabled:cursor-wait disabled:opacity-60 sm:flex-none"
                @click="clearKeywordSearch"
              >
                清除
              </button>
            </div>
          </form>
          <p class="mt-2 text-xs text-gray-400">
            可輸入多個詞；任一詞出現在提問或回應中，就會列入結果。
          </p>
        </div>

        <!-- Filter breadcrumb -->
        <div class="mb-4 flex flex-wrap items-center gap-2 text-sm text-gray-500">
          <span>{{ filterLabel }}</span>
          <span v-if="keywordQuery" class="text-xs text-blue-600"
            >· 關鍵字「{{ keywordQuery }}」</span
          >
          <span v-if="activeFilter !== 'all' || keywordQuery" class="text-xs text-gray-400"
            >· {{ totalCount }} 筆</span
          >
          <span v-if="searchLimited" class="text-xs text-amber-600"
            >· 符合超過 1,000 筆，顯示最近 1,000 筆</span
          >
        </div>

        <!-- Loading -->
        <div v-if="loading" class="py-20 text-center text-gray-400 text-sm">
          載入中…
        </div>

        <!-- Error -->
        <div v-else-if="entriesError" class="py-20 text-center text-sm text-rose-600">
          <p>{{ entriesError }}</p>
          <button type="button" class="mt-3 text-blue-600 hover:underline" @click="loadEntries">
            再試一次
          </button>
        </div>

        <!-- Empty -->
        <div
          v-else-if="entries.length === 0"
          class="py-20 text-center text-gray-400 text-sm"
        >
          {{ keywordQuery ? `找不到含有「${keywordQuery}」的對話` : "沒有符合的對話" }}
        </div>

        <!-- Entries grouped by date -->
        <div v-else>
          <div v-for="group in groupedEntries" :key="group.date" class="mb-8">
            <div
              class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 sticky top-14 bg-slate-50 py-1"
            >
              {{ formatDate(group.date) }}
              <span class="ml-2 font-normal text-gray-400"
                >{{ group.entries.length }} 筆</span
              >
            </div>

            <div class="space-y-2">
              <div
                v-for="entry in group.entries"
                :key="entry.id"
                class="bg-white rounded-xl border border-gray-100 hover:border-gray-200 transition"
              >
                <!-- Entry header -->
                <div
                  class="flex items-start gap-3 px-4 py-3 cursor-pointer"
                  @click="toggleEntry(entry.id)"
                >
                  <div class="flex-1 min-w-0">
                    <p
                      :class="[
                        'text-sm text-gray-800 leading-relaxed',
                        expandedEntry !== entry.id ? 'line-clamp-2' : '',
                      ]"
                    >
                      {{ entry.prompt }}
                    </p>
                    <div
                      v-if="entryCategories(entry).length > 0"
                      class="flex flex-wrap gap-1 mt-2"
                    >
                      <span
                        v-for="cat in entryCategories(entry)"
                        :key="cat.id"
                        :class="[
                          'inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full',
                          colorChip(cat.color),
                        ]"
                      >
                        {{ cat.name }}
                        <button
                          @click.stop="removeCategoryFromEntry(entry, cat.id)"
                          class="opacity-60 hover:opacity-100 leading-none"
                        >
                          ×
                        </button>
                      </span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1.5 shrink-0">
                    <span v-if="entry.seq_label" class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-gray-100 text-gray-500" title="對話編號（可在書中引用查閱）">{{ entry.seq_label }}</span>
                    <span class="text-xs text-gray-400">{{
                      formatTime(entry.dialogue_time)
                    }}</span>

                    <!-- Quick category picker -->
                    <div class="relative" v-if="categories.length > 0">
                      <button
                        @click.stop="
                          quickCatTarget =
                            quickCatTarget === entry.id ? null : entry.id
                        "
                        class="text-gray-300 hover:text-blue-500 transition text-xs px-1 leading-none"
                        title="加入分類"
                      >
                        #
                      </button>
                      <div
                        v-if="quickCatTarget === entry.id"
                        class="absolute right-0 top-6 bg-white border border-gray-200 rounded-xl shadow-lg z-10 p-2 flex flex-col gap-1 min-w-28"
                        @click.stop
                      >
                        <button
                          v-for="cat in categories"
                          :key="cat.id"
                          @click.stop="quickAddCategory(entry, cat.id)"
                          :class="[
                            'flex items-center gap-1.5 text-xs px-2 py-1 rounded-lg transition text-left w-full',
                            entryCategories(entry).some(
                              (c: any) => c.id === cat.id,
                            )
                              ? 'opacity-40 cursor-default bg-gray-50'
                              : 'hover:bg-gray-50',
                          ]"
                        >
                          <span
                            :class="[
                              'w-2 h-2 rounded-full shrink-0',
                              colorDot(cat.color),
                            ]"
                          ></span>
                          {{ cat.name }}
                          <span
                            v-if="
                              entryCategories(entry).some(
                                (c: any) => c.id === cat.id,
                              )
                            "
                            class="ml-auto text-gray-400"
                            >✓</span
                          >
                        </button>
                      </div>
                    </div>

                    <button
                      @click.stop="confirmDelete(entry)"
                      class="text-gray-300 hover:text-red-400 transition text-base leading-none px-1"
                      title="刪除"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <!-- Expanded: response + category picker -->
                <div
                  v-if="expandedEntry === entry.id"
                  class="border-t border-gray-100 px-4 py-3"
                >
                  <div
                    v-if="entry.response"
                    class="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto mb-3"
                  >
                    {{ entry.response }}
                  </div>
                  <div v-else class="text-xs text-gray-400 mb-3">
                    （無回應記錄）
                  </div>

                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="text-xs text-gray-400">加入分類：</span>
                    <button
                      v-for="cat in categories"
                      :key="cat.id"
                      :disabled="
                        entryCategories(entry).some((c: any) => c.id === cat.id)
                      "
                      @click="addCategoryToEntry(entry, cat.id)"
                      :class="[
                        'text-xs px-2 py-0.5 rounded-full transition',
                        entryCategories(entry).some((c: any) => c.id === cat.id)
                          ? 'opacity-40 cursor-default ' + colorChip(cat.color)
                          : colorChip(cat.color) + ' hover:opacity-80',
                      ]"
                    >
                      {{ cat.name }}
                    </button>
                    <button
                      v-if="categories.length === 0"
                      @click="showNewCategory = true"
                      class="text-xs text-blue-500 hover:underline"
                    >
                      新增分類
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination — only for "all" / category views -->
          <div
            v-if="showPagination && totalPages > 1"
            class="flex justify-center gap-2 mt-8"
          >
            <button
              @click="goPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition"
            >
              上一頁
            </button>
            <span class="px-3 py-1.5 text-sm text-gray-500"
              >{{ currentPage }} / {{ totalPages }}</span
            >
            <button
              @click="goPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition"
            >
              下一頁
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- New category modal -->
    <div
      v-if="showNewCategory"
      class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center"
      @click.self="showNewCategory = false"
    >
      <div class="bg-white rounded-2xl p-6 w-80 shadow-xl">
        <h3 class="font-semibold text-gray-900 mb-4">新增分類</h3>
        <input
          v-model="newCatName"
          placeholder="分類名稱"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-200"
          @keydown.enter="createCategory"
        />
        <select
          v-model="newCatParent"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-200 text-gray-700"
        >
          <option :value="null">（頂層分類）</option>
          <option v-for="p in topLevelCategories" :key="p.id" :value="p.id">
            ↳ 歸入「{{ p.name }}」
          </option>
        </select>
        <div class="flex gap-2 mb-4">
          <button
            v-for="c in colorOptions"
            :key="c.value"
            @click="newCatColor = c.value"
            :class="[
              'w-6 h-6 rounded-full transition ring-offset-1',
              c.bg,
              newCatColor === c.value ? 'ring-2 ring-gray-400' : '',
            ]"
          ></button>
        </div>
        <div class="flex gap-2">
          <button
            @click="createCategory"
            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2 text-sm font-medium transition"
          >
            建立
          </button>
          <button
            @click="showNewCategory = false"
            class="flex-1 border border-gray-200 rounded-lg py-2 text-sm text-gray-600 hover:bg-gray-50 transition"
          >
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center"
      @click.self="deleteTarget = null"
    >
      <div class="bg-white rounded-2xl p-6 w-96 shadow-xl">
        <h3 class="font-semibold text-gray-900 mb-2">確認刪除</h3>
        <p class="text-sm text-gray-500 mb-1 line-clamp-3">
          {{ deleteTarget.prompt }}
        </p>
        <p class="text-xs text-gray-400 mb-5">刪除後無法復原。</p>
        <div class="flex gap-2">
          <button
            @click="doDelete"
            class="flex-1 bg-red-500 hover:bg-red-600 text-white rounded-lg py-2 text-sm font-medium transition"
          >
            刪除
          </button>
          <button
            @click="deleteTarget = null"
            class="flex-1 border border-gray-200 rounded-lg py-2 text-sm text-gray-600 hover:bg-gray-50 transition"
          >
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- Citation code lookup modal -->
    <div
      v-if="lookupOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="code-lookup-title"
      @click="closeLookup"
    >
      <div
        ref="lookupDialog"
        class="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-auto p-6 shadow-xl"
        @click.stop
        @keydown.esc.stop="closeLookup"
        @keydown.tab="trapLookupFocus"
      >
        <div class="flex items-center justify-between mb-2">
          <h3 id="code-lookup-title" class="font-semibold text-gray-900">代碼查詢</h3>
          <button type="button" aria-label="關閉代碼查詢" @click="closeLookup" class="text-gray-400 hover:text-gray-700">×</button>
        </div>
        <p class="mb-3 text-xs text-gray-400">輸入書中引用的 C- 或 G- 對話代碼。</p>
        <form class="mb-4 flex items-center gap-2" @submit.prevent="doLookup">
          <input
            ref="lookupInput"
            v-model="lookupSeq"
            autocomplete="off"
            placeholder="例如 C-00241 或 G-00789"
            aria-label="對話代碼"
            class="min-w-0 flex-1 rounded-lg border border-gray-200 px-3 py-2 font-mono text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
          <button
            type="submit"
            :disabled="lookupLoading || !lookupSeq.trim()"
            class="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ lookupLoading ? "查詢中…" : "查詢" }}
          </button>
        </form>
        <div v-if="lookupErr" class="text-sm text-rose-600">{{ lookupErr }}</div>
        <template v-else-if="lookupResult">
          <div class="mb-3 flex flex-wrap items-center gap-2">
            <span class="text-sm font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600">{{ lookupResult.seq_label }}</span>
            <span class="text-xs text-gray-400">{{ lookupResult.dialogue_date }} {{ lookupResult.source === 'chatgpt' ? 'ChatGPT' : 'Gemini' }}</span>
          </div>
          <h4 class="text-xs font-semibold text-gray-500 mb-1">提問</h4>
          <p class="text-sm text-gray-800 whitespace-pre-wrap mb-4">{{ lookupResult.prompt }}</p>
          <h4 class="text-xs font-semibold text-gray-500 mb-1">回應</h4>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ lookupResult.response }}</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ title: "AI 對話錄 — Know Graph Lab" });

const supabase = useSupabaseClient();

const LIMIT = 50;

// ── State ──────────────────────────────────────────────────────────
const activeFilter = ref("all");
const expandedMonth = ref<string | null>(null);
const expandedEntry = ref<string | null>(null);
const currentPage = ref(1);
const loading = ref(false);
const entriesError = ref("");
let loadEntriesRequestId = 0;

const months = ref<{ month: string; count: number }[]>([]);
const allDates = ref<{ date: string; count: number }[]>([]);
const categories = ref<any[]>([]);
const entries = ref<any[]>([]);
const totalCount = ref(0);
const searchLimited = ref(false);
const uncategorizedCount = ref(0);
const sourceCounts = ref<Record<string, number>>({});

const showNewCategory = ref(false);
const newCatName = ref("");
const newCatColor = ref("blue");
const newCatParent = ref<string | null>(null);
const expandedCats = ref<string[]>([]);
const deleteTarget = ref<any>(null);
const quickCatTarget = ref<string | null>(null);

// 寬鬆關鍵字搜尋：輸入與已送出的查詢分開，避免每次按鍵都掃描完整對話。
const keywordDraft = ref("");
const keywordQuery = ref("");

async function refreshFromFirstPage() {
  expandedEntry.value = null;
  if (currentPage.value === 1) await loadEntries();
  else currentPage.value = 1;
}

async function runKeywordSearch() {
  const nextQuery = keywordDraft.value.trim();
  if (!nextQuery) {
    await clearKeywordSearch();
    return;
  }
  keywordQuery.value = nextQuery;
  await refreshFromFirstPage();
}

async function clearKeywordSearch() {
  keywordDraft.value = "";
  if (!keywordQuery.value) return;
  keywordQuery.value = "";
  await refreshFromFirstPage();
}

// 編號查閱（書中引用 C-/G- 回查原始對話）
const lookupSeq = ref("");
const lookupOpen = ref(false);
const lookupErr = ref("");
const lookupResult = ref<any>(null);
const lookupLoading = ref(false);
const lookupTrigger = ref<HTMLButtonElement | null>(null);
const lookupDialog = ref<HTMLElement | null>(null);
const lookupInput = ref<HTMLInputElement | null>(null);

async function openLookup() {
  lookupOpen.value = true;
  lookupErr.value = "";
  lookupResult.value = null;
  await nextTick();
  lookupInput.value?.focus();
}

async function closeLookup() {
  lookupOpen.value = false;
  await nextTick();
  lookupTrigger.value?.focus();
}

function trapLookupFocus(event: KeyboardEvent) {
  const dialog = lookupDialog.value;
  if (!dialog) return;
  const focusable = Array.from(
    dialog.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
    ),
  ).filter((element) => !element.hasAttribute("hidden"));
  if (focusable.length === 0) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

async function doLookup() {
  const seq = lookupSeq.value.trim();
  if (!seq) return;
  lookupOpen.value = true;
  await nextTick();
  lookupInput.value?.focus();
  lookupErr.value = "";
  lookupResult.value = null;
  lookupLoading.value = true;
  try {
    const h = await authHeader();
    lookupResult.value = await $fetch("/api/ai-dialogues/by-seq", { query: { seq }, headers: h });
  } catch (e: any) {
    lookupErr.value = e?.data?.message ?? "查閱失敗";
  } finally {
    lookupLoading.value = false;
  }
}

// ── Auth helper ────────────────────────────────────────────────────
async function authHeader() {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return { Authorization: `Bearer ${session?.access_token ?? ""}` };
}

// ── Data loading ───────────────────────────────────────────────────
async function loadMeta() {
  const h = await authHeader();
  // Get source from current filter
  let source = "all";
  if (activeFilter.value.startsWith("source:")) {
    source = activeFilter.value.slice(7);
  }
  console.log("📡 Loading months with source:", source);
  try {
    const data = await $fetch<any>("/api/ai-dialogues/months", {
      headers: h,
      query: { source },
    });
    console.log(
      "📊 Months loaded:",
      data.months?.length ?? 0,
      "months,",
      data.dates?.length ?? 0,
      "dates",
    );
    months.value = data.months ?? [];
    allDates.value = data.dates ?? [];
  } catch (e) {
    console.error("❌ Error loading months:", e);
  }
}

async function loadCategories() {
  const h = await authHeader();
  categories.value = await $fetch<any[]>("/api/ai-dialogue-categories", {
    headers: h,
  });
  // expand parents that have children (so sub-categories are visible by default)
  const parentsWithKids = categories.value
    .filter((c: any) => c.parent_id)
    .map((c: any) => c.parent_id);
  for (const pid of parentsWithKids) {
    if (!expandedCats.value.includes(pid)) expandedCats.value.push(pid);
  }
}

async function loadEntries() {
  const requestId = ++loadEntriesRequestId;
  loading.value = true;
  entriesError.value = "";
  try {
    const h = await authHeader();
    const f = activeFilter.value;
    const isFull = f.startsWith("month:") || f.startsWith("date:");
    const params: Record<string, any> = isFull
      ? { source: "all" }
      : { source: "all", page: currentPage.value, limit: LIMIT };

    if (f === "all") params.source = "all";
    else if (f === "source:all") params.source = "all";
    else if (f.startsWith("source:")) params.source = f.slice(7);
    else if (f.startsWith("month:")) params.month = f.slice(6);
    else if (f.startsWith("date:")) params.date = f.slice(5);
    else if (f.startsWith("cat:")) params.category = f.slice(4);
    else if (f === "uncategorized") params.uncategorized = "1";
    if (keywordQuery.value) params.q = keywordQuery.value;

    console.log("📡 Loading entries with filter:", f, "params:", params);
    const data = await $fetch<any>("/api/ai-dialogues", {
      headers: h,
      query: params,
    });
    console.log(
      "✅ Entries loaded:",
      data.data?.length ?? 0,
      "entries, total:",
      data.count ?? 0,
    );
    if (requestId !== loadEntriesRequestId) return;
    entries.value = data.data ?? [];
    totalCount.value = data.count ?? 0;
    searchLimited.value = Boolean(data.limited);
  } catch (e) {
    console.error("❌ Error loading entries:", e);
    if (requestId !== loadEntriesRequestId) return;
    entries.value = [];
    totalCount.value = 0;
    searchLimited.value = false;
    entriesError.value = "對話載入失敗，請稍後再試。";
  } finally {
    if (requestId === loadEntriesRequestId) loading.value = false;
  }
}

async function loadUncategorizedCount() {
  const h = await authHeader();
  const data = await $fetch<any>("/api/ai-dialogues", {
    headers: h,
    query: { uncategorized: "1", limit: 1 },
  });
  uncategorizedCount.value = data.count ?? 0;
}

async function loadSourceCounts() {
  const h = await authHeader();
  sourceCounts.value = await $fetch<Record<string, number>>(
    "/api/ai-dialogues/sources",
    { headers: h },
  );
}

onMounted(async () => {
  await Promise.all([
    loadMeta(),
    loadCategories(),
    loadUncategorizedCount(),
    loadSourceCounts(),
  ]);
  await loadEntries();
  // 從書中引用連結（/ai-dialogues?seq=C-00241）進來時，自動開啟編號查閱
  const seqParam = (useRoute().query.seq as string | undefined)?.trim();
  if (seqParam) {
    lookupSeq.value = seqParam;
    await doLookup();
  }
});

// Reload months when source filter changes, reload entries when any filter changes
watch(activeFilter, async (newFilter) => {
  currentPage.value = 1;
  // Reload months if source filter changed
  if (newFilter.startsWith("source:") || newFilter === "all") {
    await loadMeta();
  }
  await loadEntries();
});

watch(currentPage, loadEntries);

// ── Computed ───────────────────────────────────────────────────────
const showPagination = computed(() => {
  const f = activeFilter.value;
  return !f.startsWith("month:") && !f.startsWith("date:");
});
const totalPages = computed(() => Math.ceil(totalCount.value / LIMIT));

const groupedEntries = computed(() => {
  const map: Record<string, any[]> = {};
  for (const e of entries.value) {
    const d = e.dialogue_date as string;
    if (!map[d]) map[d] = [];
    map[d].push(e);
  }
  return Object.entries(map)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, entries]) => ({ date, entries }));
});

const filterLabel = computed(() => {
  const f = activeFilter.value;
  if (f === "all") return "全部對話";
  if (f === "source:all") return "全部來源";
  if (f === "source:gemini") return "Gemini 對話";
  if (f === "source:chatgpt") return "ChatGPT 對話";
  if (f === "uncategorized") return "純時間軸（未分類）";
  if (f.startsWith("month:")) return formatMonth(f.slice(6));
  if (f.startsWith("date:")) return formatDate(f.slice(5));
  if (f.startsWith("cat:")) {
    const cat = categories.value.find((c: any) => c.id === f.slice(4));
    return cat ? `分類：${cat.name}` : "分類";
  }
  return "";
});

function sourceCount(src: string) {
  return sourceCounts.value[src] ?? 0;
}

const topLevelCategories = computed(() =>
  categories.value.filter((c: any) => !c.parent_id),
);
function childrenOf(id: string): any[] {
  return categories.value.filter((c: any) => c.parent_id === id);
}
function toggleCat(id: string) {
  expandedCats.value = expandedCats.value.includes(id)
    ? expandedCats.value.filter((x: string) => x !== id)
    : [...expandedCats.value, id];
}

function datesForMonth(month: string) {
  return allDates.value.filter((d) => d.date.startsWith(month));
}

function entryCategories(entry: any): any[] {
  return (entry.ai_dialogue_entry_categories ?? [])
    .map((ec: any) => ec.ai_dialogue_categories)
    .filter(Boolean);
}

// ── Actions ────────────────────────────────────────────────────────
function selectFilter(f: string) {
  activeFilter.value = f;
  currentPage.value = 1;
  expandedEntry.value = null;
}

function toggleMonth(month: string) {
  expandedMonth.value = expandedMonth.value === month ? null : month;
  selectFilter("month:" + month);
}

function toggleEntry(id: string) {
  expandedEntry.value = expandedEntry.value === id ? null : id;
}

function goPage(p: number) {
  currentPage.value = p;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function createCategory() {
  if (!newCatName.value.trim()) return;
  const h = await authHeader();
  await $fetch("/api/ai-dialogue-categories", {
    method: "POST",
    headers: h,
    body: {
      name: newCatName.value,
      color: newCatColor.value,
      parent_id: newCatParent.value,
    },
  });
  // keep parent expanded so the new child is visible
  if (newCatParent.value && !expandedCats.value.includes(newCatParent.value)) {
    expandedCats.value.push(newCatParent.value);
  }
  newCatName.value = "";
  newCatParent.value = null;
  showNewCategory.value = false;
  await loadCategories();
}

async function deleteCategory(cat: any) {
  if (!confirm(`刪除分類「${cat.name}」？`)) return;
  const h = await authHeader();
  await $fetch(`/api/ai-dialogue-categories/${cat.id}`, {
    method: "DELETE",
    headers: h,
  });
  if (activeFilter.value === "cat:" + cat.id) activeFilter.value = "all";
  await Promise.all([loadCategories(), loadEntries()]);
}

function confirmDelete(entry: any) {
  deleteTarget.value = entry;
}

async function doDelete() {
  if (!deleteTarget.value) return;
  const h = await authHeader();
  const source = deleteTarget.value.source ?? "gemini";
  await $fetch(`/api/ai-dialogues/${deleteTarget.value.id}?source=${source}`, {
    method: "DELETE",
    headers: h,
  });
  deleteTarget.value = null;
  await Promise.all([loadMeta(), loadEntries(), loadUncategorizedCount()]);
}

async function clearUncategorized() {
  if (
    !confirm(
      `確認清空所有未分類的對話？（${uncategorizedCount.value} 筆，無法復原）`,
    )
  )
    return;
  const h = await authHeader();
  // Determine which source to clear from
  let source = "all";
  if (activeFilter.value.startsWith("source:")) {
    source = activeFilter.value.slice(7);
  }
  await $fetch(`/api/ai-dialogues/clear-uncategorized?source=${source}`, {
    method: "DELETE",
    headers: h,
  });
  if (activeFilter.value === "uncategorized") activeFilter.value = "all";
  await Promise.all([loadMeta(), loadEntries(), loadUncategorizedCount()]);
}

async function quickAddCategory(entry: any, categoryId: string) {
  if (entryCategories(entry).some((c: any) => c.id === categoryId)) return;
  await addCategoryToEntry(entry, categoryId);
  quickCatTarget.value = null;
}

async function addCategoryToEntry(entry: any, categoryId: string) {
  const h = await authHeader();
  const source = entry.source ?? "gemini";
  await $fetch(`/api/ai-dialogues/${entry.id}/categories`, {
    method: "POST",
    headers: h,
    body: { category_id: categoryId, source },
  });
  await Promise.all([loadEntries(), loadUncategorizedCount()]);
}

async function removeCategoryFromEntry(entry: any, categoryId: string) {
  const h = await authHeader();
  const source = entry.source ?? "gemini";
  await $fetch(
    `/api/ai-dialogues/${entry.id}/categories/${categoryId}?source=${source}`,
    {
      method: "DELETE",
      headers: h,
    },
  );
  await Promise.all([loadEntries(), loadUncategorizedCount()]);
}

// ── Formatting ─────────────────────────────────────────────────────
function formatMonth(m: string) {
  const [y, mo] = m.split("-");
  return `${y} 年 ${parseInt(mo)} 月`;
}

function formatDate(d: string) {
  const [y, mo, da] = d.split("-");
  return `${y} 年 ${parseInt(mo)} 月 ${parseInt(da)} 日`;
}

function formatTime(ts: string | null) {
  if (!ts) return "";
  return new Date(ts).toLocaleTimeString("zh-TW", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Taipei",
  });
}

const colorOptions = [
  { value: "blue", bg: "bg-blue-400" },
  { value: "violet", bg: "bg-violet-400" },
  { value: "emerald", bg: "bg-emerald-400" },
  { value: "amber", bg: "bg-amber-400" },
  { value: "rose", bg: "bg-rose-400" },
  { value: "slate", bg: "bg-slate-400" },
];

function colorDot(c: string) {
  const map: Record<string, string> = {
    blue: "bg-blue-400",
    violet: "bg-violet-400",
    emerald: "bg-emerald-400",
    amber: "bg-amber-400",
    rose: "bg-rose-400",
    slate: "bg-slate-400",
  };
  return map[c] ?? "bg-gray-400";
}

function colorChip(c: string) {
  const map: Record<string, string> = {
    blue: "bg-blue-50 text-blue-700",
    violet: "bg-violet-50 text-violet-700",
    emerald: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700",
    rose: "bg-rose-50 text-rose-700",
    slate: "bg-slate-100 text-slate-700",
  };
  return map[c] ?? "bg-gray-100 text-gray-700";
}
</script>
