<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="當代佛學研究" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">當代佛學研究</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          二十世紀以來的佛學研究書目，七個策展分區——佛學研究方法論、經典批判與詮釋、教史研究、
          性別研究、社會研究、制度研究、教理研究——另加電子圖書館的館藏盤點。
        </p>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed">
          與
          <NuxtLink to="/tripitaka" class="text-amber-700 hover:underline">佛教大藏經</NuxtLink>
          的分工：那邊收<strong>原典</strong>（大正藏、卍續藏、漢譯南傳全文），這一張收<strong>研究</strong>。
          與
          <NuxtLink to="/research-data/yinshun-hongshi" class="text-amber-700 hover:underline">印順學派與弘誓研究資料</NuxtLink>
          的分工：那邊收刊物典藏（弘誓雙月刊、玄奘佛學研究學報），這一張收學術專著書目。
        </p>
        <div v-if="langs" class="mt-3 flex flex-wrap gap-1.5">
          <span v-for="(n, k) in langs" :key="k"
                class="text-xs px-2 py-0.5 rounded bg-white border border-amber-100 text-amber-800">
            {{ langLabel(k) }} <span class="text-gray-400 tabular-nums">{{ n }}</span>
          </span>
        </div>
      </div>

      <NuxtLink to="/research-data/buddhist-studies/glossaries"
                class="block mb-5 bg-white rounded-2xl border border-amber-100 hover:border-amber-300 p-5 transition-colors no-underline">
        <div class="flex items-start gap-4">
          <div class="text-2xl leading-none mt-0.5">📖</div>
          <div class="flex-1 min-w-0">
            <h2 class="text-base font-bold text-gray-900">佛學辭典查詢</h2>
            <p class="text-xs text-gray-500 leading-relaxed mt-1 break-words">
              法鼓文理學院佛學術語字辭典十二部、10.3 萬條詞目——丁福保《佛學大辭典》、
              蘇慧廉—何樂益、霍普金斯藏梵英、巴漢辭典、《翻譯名義大集》、辛嶋靜志四部譯經詞典。
              漢傳古代辭書（《一切經音義》等）另在大藏經事彙部。
            </p>
          </div>
          <span class="text-xs text-amber-700 flex-shrink-0">查詞 →</span>
        </div>
      </NuxtLink>

      <div v-if="pending" class="text-sm text-gray-400 py-10 text-center">載入中⋯</div>
      <div v-else-if="!areas.length" class="text-sm text-gray-400 py-10 text-center">尚無資料</div>

      <div v-else class="space-y-5">
        <section v-for="a in areas" :key="a.slug" class="bg-white rounded-2xl border border-gray-100 p-6">
          <div class="flex items-start gap-4 mb-3">
            <div class="text-2xl leading-none mt-0.5">{{ a.icon }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline gap-2 flex-wrap">
                <h2 class="text-lg font-bold text-gray-900">{{ a.name }}</h2>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="badgeClass(a.source)">
                  {{ badgeLabel(a.source) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 leading-relaxed mt-1 break-words">{{ a.desc }}</p>
            </div>
            <div class="text-right flex-shrink-0 text-xs text-gray-400 leading-relaxed">
              <template v-if="a.source === 'library'">
                <div class="text-base font-semibold text-gray-700">{{ (a.books || 0).toLocaleString() }} 本</div>
                <div>{{ (a.chunks || 0).toLocaleString() }} 段</div>
              </template>
              <template v-else>
                <div class="text-base font-semibold text-gray-700">{{ a.count }} 筆</div>
                <div>已入館 {{ a.in_library }}</div>
              </template>
            </div>
          </div>

          <!-- 館藏區：分類明細 -->
          <div v-if="a.source === 'library' && a.parts?.length" class="mt-4 flex flex-wrap gap-2">
            <span v-for="p in a.parts" :key="p.name"
                  class="text-xs px-2.5 py-1 rounded-lg border"
                  :class="p.works ? 'bg-violet-50 text-violet-700 border-violet-100' : 'bg-gray-50 text-gray-600 border-gray-100'">
              {{ p.name }} <span class="opacity-60">{{ p.books }} 本</span>
            </span>
          </div>

          <!-- 書目區 -->
          <div v-else class="mt-4">
            <div v-if="a.regions?.length" class="flex flex-wrap gap-1.5 mb-3">
              <span v-for="r in a.regions" :key="r"
                    class="text-xs px-2 py-0.5 rounded bg-amber-50 text-amber-700">{{ r }}</span>
            </div>
            <div v-if="a.langs" class="flex flex-wrap gap-1.5 mb-3">
              <span v-for="(n, k) in a.langs" :key="k" class="text-xs text-gray-400">
                {{ langLabel(k) }} {{ n }}
              </span>
            </div>
            <div class="flex gap-4 flex-wrap">
              <button @click="toggle(a.slug, 'bib')" class="text-xs text-amber-700 hover:underline">
                {{ open === a.slug + ':bib' ? '收合書目' : `列出 ${a.count} 筆書目` }}
              </button>
              <button v-if="arts[a.slug]?.count" @click="toggle(a.slug, 'art')"
                      class="text-xs text-sky-700 hover:underline">
                {{ open === a.slug + ':art' ? '收合論文' : `華語期刊論文 ${arts[a.slug].count} 篇` }}
              </button>
            </div>

            <div v-if="open === a.slug + ':art'" class="mt-3">
              <p v-if="arts[a.slug].precision != null"
                 class="text-xs mb-3 px-3 py-2 rounded-lg leading-relaxed break-words"
                 :class="precClass(arts[a.slug].precision!)">
                抽樣複核：隨機抽 {{ arts[a.slug].sample }} 筆逐筆判讀，<strong>其中
                {{ Math.round(arts[a.slug].precision! * 100) }}% 真的屬於本區</strong>。
                <span v-if="arts[a.slug].weak_terms?.length">
                  假命中集中在「{{ arts[a.slug].weak_terms!.join('」「') }}」這幾個詞上，
                  只靠這些詞命中的 {{ arts[a.slug].weak_count }} 筆另列於下方。
                </span>
              </p>
              <ul class="space-y-2">
                <li v-for="(t, j) in strongOf(a.slug)" :key="'s' + j" class="text-xs text-gray-600 leading-relaxed">
                  <div class="flex items-baseline gap-2 flex-wrap">
                    <span class="text-gray-400 tabular-nums whitespace-nowrap">{{ t.date }}</span>
                    <span class="text-sky-700 whitespace-nowrap">{{ t.journal }}</span>
                    <span class="text-gray-400">{{ t.issue }}，頁 {{ t.pages }}</span>
                    <span v-if="t.fulltext" class="px-1.5 rounded bg-sky-50 text-sky-700">華藝有全文</span>
                  </div>
                  <div class="text-gray-800 break-words">{{ t.title }}</div>
                  <div v-if="t.authors?.length" class="text-gray-400">{{ t.authors.join('、') }}</div>
                </li>
              </ul>
              <div v-if="weakOf(a.slug).length" class="mt-5 pt-4 border-t border-dashed border-amber-200">
                <p class="text-xs text-amber-700 mb-2 break-words">
                  以下 {{ weakOf(a.slug).length }} 筆<strong>只靠低精確率的詞命中</strong>，
                  假命中多半落在這裡。保留而不刪除，是因為刪掉會一併犧牲召回率，而且看不出來漏了什麼。
                </p>
                <ul class="space-y-2 opacity-70">
                  <li v-for="(t, j) in weakOf(a.slug)" :key="'w' + j" class="text-xs text-gray-600 leading-relaxed">
                    <div class="flex items-baseline gap-2 flex-wrap">
                      <span class="text-gray-400 tabular-nums whitespace-nowrap">{{ t.date }}</span>
                      <span class="text-sky-700 whitespace-nowrap">{{ t.journal }}</span>
                      <span class="text-gray-400">{{ t.issue }}，頁 {{ t.pages }}</span>
                      <span v-if="t.hit?.length" class="px-1.5 rounded bg-amber-50 text-amber-700">
                        命中「{{ t.hit.join('」「') }}」</span>
                    </div>
                    <div class="text-gray-800 break-words">{{ t.title }}</div>
                    <div v-if="t.authors?.length" class="text-gray-400">{{ t.authors.join('、') }}</div>
                  </li>
                </ul>
              </div>
            </div>
            <ul v-if="open === a.slug + ':bib'" class="mt-3 space-y-2.5">
              <li v-for="(b, i) in a.items" :key="i" class="text-xs text-gray-600 leading-relaxed">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <span class="text-gray-400 tabular-nums">{{ b.year }}</span>
                  <span class="font-semibold text-gray-800 break-words">{{ b.author_zh }}《{{ b.title_zh }}》</span>
                  <span v-if="b.region" class="text-amber-600">{{ b.region }}</span>
                  <span class="px-1.5 rounded" :class="b.in_library ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-50 text-gray-400'">
                    {{ b.in_library ? '已入館' : '缺' }}
                  </span>
                  <span v-if="b.zh" class="text-orange-700">中譯：{{ b.zh }}</span>
                </div>
                <div class="text-gray-400 break-words">{{ b.author }}, <em>{{ b.title }}</em>（{{ langLabel(b.lang) }}）</div>
                <div v-if="b.note" class="text-gray-500 break-words">{{ b.note }}</div>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <p class="mt-8 text-xs text-gray-400 leading-relaxed">
        ⚠️「已入館／缺」是把書目題名（原文與中譯都比、破折號副標先切掉）拿去對電子圖書館，
        再要求作者對得上才算數——館裡《印度佛教史》就有拉莫特、沃德爾、聖嚴三種，光比題名會誤判。
        取寧可漏報不可誤報的一側，因此標為「缺」的未必真的沒有。本卡片命中率偏低是實情而非故障：
        館內佛教類三百餘本有九成是印順、太虛、聖嚴三套<strong>全集</strong>的個別卷，那是原著不是研究。
        缺書清單會倒進 <code>data/zlib-wanted/buddhist-studies.jsonl</code> 交每日排程去找。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Item {
  area: string; region?: string; author: string; author_zh: string
  year: number; title: string; title_zh: string; lang: string
  note?: string; zh?: string; in_library: boolean
}
interface Part { name: string; books: number; chunks: number; works: boolean }
interface Area {
  slug: string; name: string; icon: string; desc: string
  source: 'bibliography' | 'library'
  count?: number; in_library?: number; regions?: string[]
  langs?: Record<string, number>; items?: Item[]
  books?: number; chunks?: number; works_books?: number; parts?: Part[]
}

interface Art {
  journal: string; title: string; authors: string[]
  issue: string; date: string; pages: string; fulltext: boolean
  hit?: string[]; weak?: boolean
}
interface ArtArea {
  count: number; items: Art[]
  weak_terms?: string[]; weak_count?: number
  sample?: number; precision?: number | null
}
const areas = ref<Area[]>([])
const langs = ref<Record<string, number> | null>(null)
const arts = ref<Record<string, ArtArea>>({})
const pending = ref(true)
const open = ref('')
const toggle = (slug: string, kind: 'bib' | 'art') => {
  const k = `${slug}:${kind}`
  open.value = open.value === k ? '' : k
}

const LANGS: Record<string, string> = {
  en: '英', ja: '日', zh: '中', fr: '法', de: '德', ko: '韓',
}
const langLabel = (k: string) => LANGS[k] ?? k

const strongOf = (slug: string) => (arts.value[slug]?.items ?? []).filter(t => !t.weak)
const weakOf = (slug: string) => (arts.value[slug]?.items ?? []).filter(t => t.weak)
const precClass = (p: number) => p >= 0.9
  ? 'bg-emerald-50 text-emerald-800'
  : p >= 0.7 ? 'bg-amber-50 text-amber-800' : 'bg-rose-50 text-rose-800'

const badgeClass = (s: string) => s === 'library'
  ? 'bg-violet-50 text-violet-700' : 'bg-amber-50 text-amber-700'
const badgeLabel = (s: string) => s === 'library'
  ? '電子圖書館館藏' : '策展書目'

onMounted(async () => {
  try {
    const d = await $fetch<{ areas: Area[]; langs: Record<string, number> }>(
      '/content/research-data/buddhist-studies/index.json', { responseType: 'json' })
    areas.value = d?.areas ?? []
    langs.value = d?.langs ?? null
    try {
      const a = await $fetch<{ areas: Record<string, ArtArea> }>(
        '/content/research-data/buddhist-studies/articles.json', { responseType: 'json' })
      arts.value = a?.areas ?? {}
    } catch { arts.value = {} }
  } catch { areas.value = [] } finally { pending.value = false }
})

useHead({ title: '當代佛學研究 — Know Graph Lab' })
</script>
