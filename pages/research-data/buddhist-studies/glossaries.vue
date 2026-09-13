<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="佛學辭典查詢" :back="{ to: '/research-data/buddhist-studies', label: '當代佛學研究' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">佛學辭典查詢</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          法鼓文理學院佛學術語字辭典十二部，加上佛光山《佛光大辭典》增訂版，合計 {{ glossaries.length }} 部、{{ totalEntries.toLocaleString() }} 條詞目。
          先比詞目、再比釋義——查「般若」要的是詞目叫般若的那幾條，不是釋義裡提過般若的幾千條。
        </p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-100 p-5 mb-5">
        <div class="flex flex-wrap gap-3 items-center">
          <input v-model="q" @keyup.enter="run" type="search" placeholder="輸入詞目，如 般若、如來藏、eka⋯"
                 class="flex-1 min-w-[220px] text-sm px-3 py-2 rounded-lg border border-gray-200" />
          <select v-model="code" class="text-sm px-3 py-2 rounded-lg border border-gray-200 bg-white">
            <option value="">全部辭典</option>
            <option v-for="g in glossaries" :key="g.code" :value="g.code">
              {{ g.name }}（{{ g.entries.toLocaleString() }}）
            </option>
          </select>
          <label class="text-xs text-gray-500 flex items-center gap-1.5">
            <input v-model="inDef" type="checkbox" class="rounded" /> 連釋義一起找
          </label>
          <button @click="run" class="text-sm px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-700">
            查詢
          </button>
        </div>
        <p v-if="searched" class="mt-3 text-xs text-gray-400">
          「{{ searched }}」命中 {{ total.toLocaleString() }} 條<span v-if="total > hits.length">，以下顯示前 {{ hits.length }} 條</span>
        </p>
      </div>

      <div v-if="pending" class="text-sm text-gray-400 py-10 text-center">查詢中⋯</div>
      <div v-else-if="searched && !hits.length" class="text-sm text-gray-400 py-10 text-center">
        查不到「{{ searched }}」
      </div>

      <div v-else-if="hits.length" class="space-y-3">
        <article v-for="(h, i) in hits" :key="i" class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-baseline gap-3 flex-wrap mb-1.5">
            <h2 class="text-base font-bold text-gray-900 break-words">{{ h.term }}</h2>
            <span class="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">{{ nameOf(h.code) }}</span>
            <span v-for="d in h.domain || []" :key="d" class="text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-500">{{ d }}</span>
            <span v-if="h.page" class="text-xs px-2 py-0.5 rounded bg-sky-50 text-sky-700 whitespace-nowrap">原書 p{{ h.page }}</span>
          </div>
          <div v-if="h.langs" class="mb-2 flex flex-wrap gap-x-4 gap-y-1">
            <span v-for="(v, k) in h.langs" :key="k" class="text-xs text-gray-600">
              <span class="text-gray-400">{{ k }}</span> {{ v }}
            </span>
          </div>
          <p v-if="h.definition" class="text-sm text-gray-700 leading-relaxed break-words whitespace-pre-line">{{ h.definition }}</p>
          <p v-if="h.variants?.length" class="mt-1.5 text-xs text-gray-400 break-words">
            異形／對應：{{ h.variants.join('、') }}
          </p>
          <div v-if="h.images?.length" class="mt-3 flex flex-wrap gap-3">
            <a v-for="n in h.images" :key="n" :href="imgUrl(n)" target="_blank" rel="noopener"
               class="block border border-gray-100 rounded-lg overflow-hidden bg-gray-50">
              <img :src="imgUrl(n)" :alt="h.term + ' 插圖'" loading="lazy"
                   class="max-h-64 w-auto max-w-full block" />
            </a>
          </div>
          <p v-if="h.glyphs?.length" class="mt-2 text-xs text-gray-400 break-words flex items-center gap-1.5 flex-wrap">
            <span>釋義中的 ▢ 是原書的缺字，以圖代字：</span>
            <img v-for="n in h.glyphs" :key="n" :src="imgUrl(n)" :alt="'缺字 ' + n"
                 loading="lazy" class="inline-block h-4 w-auto align-text-bottom" />
          </p>
        </article>
      </div>

      <div v-else class="bg-white rounded-2xl border border-gray-100 p-6">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">收錄的辭典</h2>
        <p class="text-xs text-gray-500 leading-relaxed mb-3 break-words">
          《佛光大辭典》增訂版全十冊，三萬餘條、近千萬言。本站所收版本
          <strong>每條保留原書頁碼</strong>（94.5% 有，缺的是「參見條」本來就沒有自己的頁），
          可直接作註腳；另收原書插圖 2,968 張與缺字圖 284 張——釋義裡的
          <strong>▢</strong> 就是原書以圖代字的罕用字，圖附在條目下方。
          ⚠️ 授權狀態見 <code>data/research-data/dila-glossaries.json</code> 的 license 欄，
          與法鼓那十二部不同，對外開放前須另行確認。
        </p>
        <ul class="space-y-1.5">
          <li v-for="g in glossaries" :key="g.code" class="text-xs text-gray-600 flex gap-3">
            <span class="text-gray-400 tabular-nums w-16 text-right flex-shrink-0">{{ g.entries.toLocaleString() }}</span>
            <span class="break-words">{{ g.name }}</span>
          </li>
        </ul>
      </div>

      <p class="mt-8 text-xs text-gray-400 leading-relaxed">
        ⚠️ 各部授權不同，<strong>不可一體看待</strong>：丁福保《佛學大辭典》與《翻譯名義大集》原文為公有領域；
        辛嶋靜志四部、霍普金斯辭典是「經作者同意由法鼓文理學院數位化」——那是授權法鼓建資料庫，
        不等於授權再散布；其餘幾部頁面未載授權。本頁僅供研究檢索之用，逐部的授權狀態記在
        <code>data/research-data/dila-glossaries.json</code>。
      </p>
      <p class="mt-3 text-xs text-gray-400 leading-relaxed">
        另可查：漢傳古代辭書（《一切經音義》《翻譯名義集》《翻梵語》《釋氏要覽》等）本來就在
        <NuxtLink to="/tripitaka" class="text-amber-700 hover:underline">大藏經</NuxtLink>
        事彙部，約四點九萬段，走那邊查。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Hit {
  code: string; term: string; variants?: string[]
  domain?: string[]; definition?: string; langs?: Record<string, string>
  page?: number; images?: string[]; glyphs?: string[]
}
interface Gl { code: string; name: string; entries: number }

const q = ref('')
const code = ref('')
const inDef = ref(false)
const searched = ref('')
const total = ref(0)
const hits = ref<Hit[]>([])
const glossaries = ref<Gl[]>([])
const pending = ref(false)

const totalEntries = computed(() => glossaries.value.reduce((s, g) => s + g.entries, 0))
const nameOf = (c: string) => glossaries.value.find(g => g.code === c)?.name ?? c
const imgUrl = (n: string) => `/api/glossary/image/${encodeURIComponent(n)}`

async function run() {
  const term = q.value.trim()
  if (!term) return
  pending.value = true
  try {
    const d = await $fetch<{ total: number; hits: Hit[]; glossaries: Gl[] }>('/api/glossary/search', {
      params: { q: term, code: code.value || undefined, def: inDef.value ? 1 : undefined },
    })
    total.value = d.total; hits.value = d.hits; glossaries.value = d.glossaries
    searched.value = term
  } catch { hits.value = []; total.value = 0; searched.value = term } finally { pending.value = false }
}

onMounted(async () => {
  try {
    const d = await $fetch<{ glossaries: Gl[] }>('/api/glossary/search')
    glossaries.value = d.glossaries ?? []
  } catch { glossaries.value = [] }
})

useHead({ title: '佛學辭典查詢 — Know Graph Lab' })
</script>
