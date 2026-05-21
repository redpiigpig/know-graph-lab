<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">聖經對照</span>
      <span class="text-xs text-gray-400 ml-1">{{ filteredBooks.length }} 卷</span>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📖 聖經對照</h1>
        <p class="text-sm text-gray-500">多版本平行對照（中文 / 英文 / 希伯來 / 希臘 / 拉丁）+ 各教會 canon 範圍標記</p>
      </div>

      <!-- Canon filter -->
      <div class="flex flex-wrap items-center gap-2 mb-2 text-xs">
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

      <!-- Loading -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>

      <!-- Error -->
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <!-- Books grouped by testament -->
      <div v-else>
        <div v-for="group in groupedBooks" :key="group.key" class="mt-8">
          <h2 class="text-sm font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-1">
            {{ group.label }}
            <span class="text-xs text-gray-400 font-normal">{{ group.items.length }} 卷</span>
          </h2>
          <div class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-9 gap-2">
            <NuxtLink
              v-for="book in group.items"
              :key="book.code"
              :to="`/scripture/${book.code}/1`"
              class="block bg-white border border-gray-200 rounded-md px-2 py-2 hover:border-stone-400 hover:shadow-sm transition text-center"
            >
              <div class="font-semibold text-gray-900 text-sm leading-tight">{{ book.name_zh_short || book.name_zh }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ book.chapter_count }} 章</div>
            </NuxtLink>
          </div>
        </div>

        <div v-if="filteredBooks.length === 0" class="text-center text-gray-400 py-12 text-sm">
          所選 canon 範圍內沒有書卷
        </div>
      </div>

      <div class="mt-12 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>目前已匯入 4 個公版/開放版本：SBLGNT（希臘 NT）、Vulgate（拉丁全本）、WLC（希伯來 OT）、LXX Rahlfs（希臘 OT + 第二正典）。</p>
        <p class="mt-1">和合本2010 與 NIV 為版權版本，計畫透過合法來源逐步補入。</p>
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

const supabase = useSupabaseClient()
const books = ref<BibleBook[]>([])
const pending = ref(true)
const error = ref<string | null>(null)

async function load() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { pending.value = false; return }
  try {
    books.value = await $fetch<BibleBook[]>('/api/scripture/books', {
      headers: { Authorization: `Bearer ${session.access_token}` },
    })
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}
onMounted(load)

type CanonKey = 'all' | 'protestant' | 'catholic' | 'orthodox' | 'ethiopian' | 'syriac'
const activeCanon = ref<CanonKey>('all')

const canonOpts = computed(() => {
  const all = books.value ?? []
  return [
    { key: 'all' as const,        label: '全部',        count: all.length },
    { key: 'protestant' as const, label: '新教 66',     count: all.filter(b => b.canon_protestant).length },
    { key: 'catholic' as const,   label: '天主教',      count: all.filter(b => b.canon_catholic).length },
    { key: 'orthodox' as const,   label: '東正教',      count: all.filter(b => b.canon_orthodox).length },
    { key: 'syriac' as const,     label: '敘利亞 / 亞述', count: all.filter(b => b.canon_syriac).length },
    { key: 'ethiopian' as const,  label: '衣索匹亞 81', count: all.filter(b => b.canon_ethiopian).length },
  ]
})

const filteredBooks = computed(() => {
  const all = books.value ?? []
  if (activeCanon.value === 'all') return all
  const key = `canon_${activeCanon.value}` as keyof BibleBook
  return all.filter(b => Boolean(b[key]))
})

const groupedBooks = computed(() => {
  const groups: { key: string; label: string; items: BibleBook[] }[] = [
    { key: 'ot',        label: '舊約',             items: [] },
    { key: 'nt',        label: '新約',             items: [] },
    { key: 'deutero',   label: '次經 / 第二正典',  items: [] },
    { key: 'apocrypha', label: '衣索匹亞獨有書卷', items: [] },
  ]
  for (const b of filteredBooks.value) {
    const g = groups.find(g => g.key === b.testament)
    if (g) g.items.push(b)
  }
  return groups.filter(g => g.items.length > 0)
})
</script>
