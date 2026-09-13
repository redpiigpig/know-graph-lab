<!--
  佛學辭典查詢的共用元件。/tripitaka 的目錄頁（卡片）與閱讀頁（面板）都用它。

  ⚠️ 呈現的重點是**同一個詞目在幾部辭典各說了什麼**——查「般若」時，丁福保、
  佛光、Soothill-Hodous 會各給一條，那正是對照的價值所在。所以結果一律
  **按詞目分組**，不要平鋪成一條一條，否則同一個詞的三部解釋會被別的詞隔開。

  完整版（含辭典篩選、搜釋義）在 /research-data/buddhist-studies/glossaries。
-->
<template>
  <div>
    <div class="flex flex-wrap gap-2">
      <input
        v-model="q"
        type="search"
        :placeholder="placeholder"
        class="flex-1 min-w-[180px] px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300"
        @keyup.enter="run"
      />
      <button
        class="px-4 py-2 text-sm rounded-lg bg-amber-600 text-white hover:bg-amber-700 transition disabled:opacity-50"
        :disabled="pending || !q.trim()"
        @click="run"
      >{{ pending ? '查詢中⋯' : '查辭典' }}</button>
    </div>

    <p v-if="searched" class="mt-2.5 text-xs text-gray-400 break-words">
      「{{ searched }}」在 {{ groups.length }} 個詞目、{{ hits.length }} 條釋義中命中<span
        v-if="total > hits.length">（全站共 {{ total.toLocaleString() }} 條，以下為前 {{ hits.length }} 條）</span>
    </p>

    <div v-if="searched && !hits.length && !pending" class="mt-3 text-sm text-gray-400">
      查不到「{{ searched }}」
    </div>

    <div v-if="groups.length" class="mt-3 space-y-3" :class="scroll ? 'max-h-[60vh] overflow-y-auto pr-1' : ''">
      <section v-for="g in groups" :key="g.term" class="border border-gray-100 rounded-xl overflow-hidden">
        <header class="px-4 py-2 bg-gray-50 flex items-baseline gap-2 flex-wrap">
          <h3 class="text-sm font-bold text-gray-900 break-words">{{ g.term }}</h3>
          <span class="text-xs text-gray-400">{{ g.entries.length }} 部辭典收錄</span>
        </header>
        <div class="divide-y divide-gray-100">
          <article v-for="(h, i) in g.entries" :key="i" class="px-4 py-3">
            <div class="flex items-baseline gap-2 flex-wrap mb-1">
              <span class="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 break-words">{{ nameOf(h.code) }}</span>
              <span v-for="d in h.domain || []" :key="d"
                    class="text-xs px-1.5 py-0.5 rounded bg-gray-50 text-gray-500">{{ d }}</span>
              <span v-if="h.page" class="text-xs px-2 py-0.5 rounded bg-sky-50 text-sky-700 whitespace-nowrap">原書 p{{ h.page }}</span>
            </div>
            <div v-if="h.langs" class="mb-1 flex flex-wrap gap-x-4 gap-y-0.5">
              <span v-for="(v, k) in h.langs" :key="k" class="text-xs text-gray-600">
                <span class="text-gray-400">{{ k }}</span> {{ v }}
              </span>
            </div>
            <p v-if="h.definition" class="text-sm text-gray-700 leading-relaxed break-words whitespace-pre-line">{{ clip(h.definition) }}</p>
            <div v-if="h.images?.length" class="mt-2 flex flex-wrap gap-2">
              <a v-for="n in h.images" :key="n" :href="imgUrl(n)" target="_blank" rel="noopener">
                <img :src="imgUrl(n)" :alt="g.term + ' 插圖'" loading="lazy"
                     class="max-h-40 w-auto max-w-full block border border-gray-100 rounded-lg" />
              </a>
            </div>
          </article>
        </div>
      </section>
    </div>

    <p v-if="searched" class="mt-3 text-xs text-gray-400">
      <NuxtLink to="/research-data/buddhist-studies/glossaries" class="text-amber-700 hover:underline">
        到辭典查詢頁做完整搜尋 →
      </NuxtLink>
      <span class="ml-2">（可指定辭典、可搜釋義內文）</span>
    </p>
  </div>
</template>

<script setup lang="ts">
interface Hit {
  code: string; term: string; variants?: string[]
  domain?: string[]; definition?: string; langs?: Record<string, string>
  page?: number; images?: string[]; glyphs?: string[]
}
interface Gl { code: string; name: string; entries: number }

const props = withDefaults(defineProps<{
  /** 預帶的查詢字（例如閱讀頁把選取的文字帶進來） */
  initial?: string
  placeholder?: string
  /** 每條釋義最多顯示幾字，0 為不截斷 */
  clamp?: number
  /** 結果區是否自己捲動（面板裡要，卡片裡不要） */
  scroll?: boolean
}>(), {
  initial: '',
  placeholder: '查佛學辭典，如 般若、如來藏、阿賴耶識⋯',
  clamp: 260,
  scroll: false,
})

const q = ref(props.initial)
const searched = ref('')
const total = ref(0)
const hits = ref<Hit[]>([])
const glossaries = ref<Gl[]>([])
const pending = ref(false)

const nameOf = (c: string) => glossaries.value.find((g) => g.code === c)?.name ?? c
const imgUrl = (n: string) => `/api/glossary/image/${encodeURIComponent(n)}`
const clip = (s: string) =>
  props.clamp && s.length > props.clamp ? s.slice(0, props.clamp) + '⋯' : s

/**
 * 按詞目分組，保持 API 回來的順序（完全相符 → 前綴 → 詞目內 → 釋義內），
 * 所以最相關的詞目自然排在最前面。
 */
const groups = computed(() => {
  const m = new Map<string, Hit[]>()
  for (const h of hits.value) {
    const list = m.get(h.term)
    if (list) list.push(h)
    else m.set(h.term, [h])
  }
  return [...m.entries()].map(([term, entries]) => ({ term, entries }))
})

async function run() {
  const term = q.value.trim()
  if (!term) return
  pending.value = true
  try {
    const d = await $fetch<{ total: number; hits: Hit[]; glossaries: Gl[] }>(
      '/api/glossary/search', { params: { q: term, limit: 40 } },
    )
    total.value = d.total
    hits.value = d.hits ?? []
    glossaries.value = d.glossaries ?? glossaries.value
    searched.value = term
  } catch {
    hits.value = []
    total.value = 0
    searched.value = term
  } finally {
    pending.value = false
  }
}

watch(() => props.initial, (v) => {
  if (v && v !== q.value) { q.value = v; run() }
})

onMounted(async () => {
  if (q.value.trim()) return run()
  try {
    const d = await $fetch<{ glossaries: Gl[] }>('/api/glossary/search')
    glossaries.value = d.glossaries ?? []
  } catch { /* 查不到辭典清單時，命中後仍會用 code 當名稱 */ }
})

defineExpose({ lookup: (t: string) => { q.value = t; run() } })
</script>
