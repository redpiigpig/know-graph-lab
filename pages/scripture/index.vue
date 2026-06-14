<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon/christianity" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">聖經對照</span>
      <span class="text-xs text-gray-400 ml-1">{{ filteredBooks.length }} 卷 / {{ versionCount }} 個版本</span>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📖 聖經對照</h1>
        <p class="text-sm text-gray-500">多版本平行對照（中文 / 英文 / 希伯來 / 希臘 / 拉丁）+ 各教會 canon 範圍標記</p>
      </div>

      <!-- Search box -->
      <div class="mb-8 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
        <form @submit.prevent="runSearch" class="flex items-center gap-2">
          <span class="text-stone-500 text-lg select-none">🔍</span>
          <input
            v-model="searchQ"
            type="text"
            placeholder="搜尋經文（中／英／希伯來／希臘／拉丁皆可，例：太初、In the beginning、ἐν ἀρχῇ、creavit）"
            class="flex-1 text-sm bg-transparent border-none focus:outline-none placeholder:text-gray-300"
          />
          <select v-model="searchVersion" class="text-xs text-gray-600 bg-transparent border-l border-gray-200 pl-2 cursor-pointer">
            <option value="">全部版本</option>
            <option v-for="v in versions" :key="v.code" :value="v.code">{{ v.name_zh }}</option>
          </select>
          <button
            type="submit"
            class="text-xs px-3 py-1 rounded bg-stone-900 text-white hover:bg-stone-700 transition"
            :disabled="!searchQ || searchQ.length < 2"
          >搜尋</button>
        </form>
      </div>

      <!-- Search results -->
      <div v-if="searchActive" class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-700">
            搜尋結果
            <span class="text-xs text-gray-400 font-normal">
              「{{ lastQ }}」 — {{ searchTotal }} 筆{{ searchTotal > searchResults.length ? `（顯示前 ${searchResults.length} 筆）` : '' }}
            </span>
          </h2>
          <button @click="clearSearch" class="text-xs text-gray-400 hover:text-gray-700 transition">✕ 清除</button>
        </div>
        <div v-if="searchPending" class="text-center text-gray-400 py-8 text-sm">搜尋中…</div>
        <div v-else-if="searchResults.length === 0" class="text-center text-gray-400 py-8 text-sm">沒有符合的經文</div>
        <div v-else class="space-y-1">
          <NuxtLink
            v-for="(r, i) in searchResults"
            :key="`${r.book_code}-${r.chapter}-${r.verse}-${r.version_code}-${i}`"
            :to="`/scripture/${r.book_code}/${r.chapter}`"
            class="block bg-white border border-gray-200 rounded px-3 py-2 hover:border-stone-400 hover:shadow-sm transition"
          >
            <div class="flex items-baseline gap-2 text-xs mb-1">
              <span class="font-mono font-semibold text-stone-700">
                {{ bookShortName(r.book_code) }} {{ r.chapter }}:{{ r.verse }}
              </span>
              <span class="text-gray-400">{{ versionLabel(r.version_code) }}</span>
            </div>
            <div class="text-sm text-gray-800 leading-relaxed" v-html="highlightMatch(r.text, lastQ)" />
          </NuxtLink>
        </div>
      </div>

      <!-- Canon filter -->
      <div v-if="!searchActive" class="flex flex-wrap items-center gap-2 mb-2 text-xs">
        <span class="text-gray-500 mr-1">Canon：</span>
        <button
          v-for="opt in canonOpts"
          :key="opt.key"
          @click="activeCanon = opt.key"
          class="px-3 py-1.5 rounded-full border transition"
          :class="activeCanon === opt.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ opt.label }} ({{ opt.count }})</button>
      </div>
      <p v-if="!searchActive && canonOrders[activeCanon]?.some(r => r.is_deutero)" class="text-[11px] text-emerald-600 mb-2">
        <span class="inline-block w-2.5 h-2.5 rounded-sm bg-emerald-100 border border-emerald-300 align-middle mr-1" />
        綠色 ＝ 該傳統的第二正典（次經），已依此傳統次序併入正典中
      </p>

      <!-- Loading -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>

      <!-- Error -->
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <!-- Books grouped by testament (hide while searching) -->
      <div v-else-if="!searchActive">
        <div v-for="group in groupedBooks" :key="group.key" class="mt-8">
          <h2 class="text-sm font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-1">
            {{ group.label }}
            <span class="text-xs text-gray-400 font-normal">{{ group.items.length }} 卷</span>
          </h2>
          <div class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-9 gap-2">
            <NuxtLink
              v-for="item in group.items"
              :key="item.book.code"
              :to="activeCanon === 'all' ? `/scripture/${item.book.code}/1` : `/scripture/${item.book.code}/1?canon=${activeCanon}`"
              class="block rounded-md px-2 py-2 hover:shadow-sm transition text-center border"
              :class="item.isDeutero
                ? 'bg-emerald-50 border-emerald-300 hover:border-emerald-500'
                : 'bg-white border-gray-200 hover:border-stone-400'"
              :title="(item.fullOverride || bookCardName(item.book).full) + (item.isDeutero ? '（第二正典）' : '')"
            >
              <div class="font-semibold text-sm leading-tight" :class="item.isDeutero ? 'text-emerald-800' : 'text-gray-900'">{{ item.shortOverride || bookCardName(item.book).short }}</div>
              <div class="text-[10px] mt-0.5" :class="item.isDeutero ? 'text-emerald-500' : 'text-gray-400'">{{ item.chapterCount }} 章</div>
            </NuxtLink>
          </div>
        </div>

        <div v-if="filteredBooks.length === 0" class="text-center text-gray-400 py-12 text-sm">
          所選 canon 範圍內沒有書卷
        </div>
      </div>

      <div v-if="!searchActive" class="mt-12 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>已匯入版本：<span v-for="(v, i) in versions" :key="v.code">{{ v.name_zh }}{{ i < versions.length - 1 ? '、' : '' }}</span></p>
        <p class="mt-1">部分中文版本（現代中文／召會／呂振中／牧靈）與英文東正教（OSB／EOB）版本仍在版權保護內，未開放收錄；可透過 YouVersion / 教會官網外連閱讀。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '聖經對照 — Know Graph Lab' })

type BibleBook = {
  code: string
  name_zh: string
  name_zh_short: string | null
  name_sigao: string | null
  abbr_sigao: string | null
  name_en: string
  testament: 'ot' | 'nt' | 'deutero' | 'apocrypha'
  canon_protestant: boolean
  canon_catholic: boolean
  canon_orthodox: boolean
  canon_ethiopian: boolean
  canon_syriac: boolean
  display_order: number
  chapter_count: number | null
}
type BibleVersion = {
  code: string
  name_zh: string
  category: string
  language: string
}
type SearchHit = {
  book_code: string
  chapter: number
  verse: number
  version_code: string
  text: string
}

type CanonOrderRow = {
  book_code: string
  testament: 'ot' | 'nt'
  sort_order: number
  is_deutero: boolean
  chapter_count: number | null
  name_override: string | null
  abbr_override: string | null
}

const supabase = useSupabaseClient()
const books = ref<BibleBook[]>([])
const versions = ref<BibleVersion[]>([])
const canonOrders = ref<Record<string, CanonOrderRow[]>>({})
const pending = ref(true)
const error = ref<string | null>(null)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load() {
  try {
    const headers = await authHeaders()
    if (!('Authorization' in headers)) { pending.value = false; return }
    const [b, v, co] = await Promise.all([
      $fetch<BibleBook[]>('/api/scripture/books', { headers }),
      $fetch<BibleVersion[]>('/api/scripture/versions', { headers }),
      $fetch<Record<string, CanonOrderRow[]>>('/api/scripture/canon-order', { headers }).catch(() => ({})),
    ])
    books.value = b
    versions.value = v
    canonOrders.value = co || {}
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}
onMounted(load)

// ── Canon filter ─────────────────────────────────────────────────────────
type CanonKey = 'all' | 'protestant' | 'catholic' | 'orthodox' | 'ethiopian' | 'syriac'
const activeCanon = ref<CanonKey>('all')

const canonOpts = computed(() => {
  const all = books.value
  return [
    { key: 'all' as const,        label: '全部',          count: all.length },
    { key: 'protestant' as const, label: '新教 66',       count: all.filter(b => b.canon_protestant).length },
    { key: 'catholic' as const,   label: '天主教',         count: all.filter(b => b.canon_catholic).length },
    { key: 'orthodox' as const,   label: '東正教',         count: all.filter(b => b.canon_orthodox).length },
    { key: 'syriac' as const,     label: '敘利亞 / 亞述',  count: all.filter(b => b.canon_syriac).length },
    { key: 'ethiopian' as const,  label: '衣索匹亞 81',    count: all.filter(b => b.canon_ethiopian).length },
  ]
})

const filteredBooks = computed(() => {
  if (activeCanon.value === 'all') return books.value
  const key = `canon_${activeCanon.value}` as keyof BibleBook
  return books.value.filter(b => Boolean(b[key]))
})

type CardItem = { book: BibleBook; isDeutero: boolean; chapterCount: number | null; shortOverride: string | null; fullOverride: string | null }

const groupedBooks = computed(() => {
  const byCode = new Map(books.value.map(b => [b.code, b]))
  const order = canonOrders.value[activeCanon.value]

  // 該傳統有自訂排序 → 用它（次經併回 OT、綠標、章數覆寫、無獨立次經組）
  if (order && order.length) {
    const groups: { key: string; label: string; items: CardItem[] }[] = [
      { key: 'ot', label: '舊約', items: [] },
      { key: 'nt', label: '新約', items: [] },
    ]
    for (const row of order) {
      const book = byCode.get(row.book_code)
      if (!book) continue
      const g = groups.find(g => g.key === row.testament)
      if (g) g.items.push({ book, isDeutero: row.is_deutero, chapterCount: row.chapter_count ?? book.chapter_count, shortOverride: row.abbr_override, fullOverride: row.name_override })
    }
    return groups.filter(g => g.items.length > 0)
  }

  // 其餘 canon（含 all / protestant）→ 沿用 bible_books 既有分類與排序
  const groups: { key: string; label: string; items: CardItem[] }[] = [
    { key: 'ot',        label: '舊約',             items: [] },
    { key: 'nt',        label: '新約',             items: [] },
    { key: 'deutero',   label: '次經 / 第二正典',  items: [] },
    { key: 'apocrypha', label: '衣索匹亞獨有書卷', items: [] },
  ]
  for (const b of filteredBooks.value) {
    const g = groups.find(g => g.key === b.testament)
    if (g) g.items.push({ book: b, isDeutero: b.testament === 'deutero' || b.testament === 'apocrypha', chapterCount: b.chapter_count, shortOverride: null, fullOverride: null })
  }
  return groups.filter(g => g.items.length > 0)
})

const versionCount = computed(() => versions.value.length)

// ── Search ───────────────────────────────────────────────────────────────
const searchQ = ref('')
const searchVersion = ref('')
const searchResults = ref<SearchHit[]>([])
const searchTotal = ref(0)
const searchPending = ref(false)
const lastQ = ref('')
const searchActive = computed(() => lastQ.value.length > 0)

async function runSearch() {
  if (!searchQ.value || searchQ.value.length < 2) return
  searchPending.value = true
  lastQ.value = searchQ.value
  try {
    const headers = await authHeaders()
    const res = await $fetch<{ q: string; total: number; results: SearchHit[] }>(
      '/api/scripture/search',
      {
        headers,
        query: {
          q: searchQ.value,
          version: searchVersion.value || undefined,
          limit: 100,
        },
      },
    )
    searchResults.value = res.results
    searchTotal.value = res.total
  } catch (e: any) {
    searchResults.value = []
    searchTotal.value = 0
    error.value = e?.message || String(e)
  } finally {
    searchPending.value = false
  }
}

function clearSearch() {
  searchQ.value = ''
  lastQ.value = ''
  searchResults.value = []
  searchTotal.value = 0
}

// 只有天主教用思高本名；其餘所有傳統（新教/東正教/敘利亞/衣索匹亞）一律用和合本。
function bookCardName(book: BibleBook): { short: string; full: string } {
  if (activeCanon.value === 'catholic' && book.abbr_sigao) {
    return { short: book.abbr_sigao, full: book.name_sigao || book.name_zh }
  }
  return { short: book.name_zh_short || book.name_zh, full: book.name_zh }
}

function bookShortName(code: string) {
  const b = books.value.find(x => x.code === code)
  return b ? (b.name_zh_short || b.name_zh) : code
}

function versionLabel(code: string) {
  const v = versions.value.find(x => x.code === code)
  return v ? v.name_zh.replace(/（[^）]*）/g, '').trim() : code
}

function highlightMatch(text: string, q: string) {
  if (!q) return text
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const re = new RegExp(`(${escaped})`, 'gi')
  return text.replace(re, '<mark class="bg-yellow-200 text-stone-900 rounded px-0.5">$1</mark>')
}
</script>
