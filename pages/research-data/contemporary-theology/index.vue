<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="當代神學研究" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">當代神學研究</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          二十世紀以來的神學研究書目與材料，十二個策展分區——神學方法論、二十世紀神學史、
          聖經神學、系統神學經典、實踐神學、自由神學、世俗神學、敘事神學、解放神學、
          性別神學、各地的神學、全球神學的嘗試——另加吉福德講座歷屆名單與館藏盤點。
        </p>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed">
          與
          <NuxtLink to="/research-data/christian-studies" class="text-indigo-700 hover:underline">基督教研究</NuxtLink>
          那張卡片的分工：那一張按時期與運動收<strong>教會史</strong>材料（教父、宗教改革、普世運動、洛桑），
          這一張按學科收<strong>神學本身</strong>。
        </p>
      </div>

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
              <template v-else-if="a.source === 'gifford'">
                <div class="text-base font-semibold text-gray-700">{{ a.count }} 場</div>
                <div>{{ a.speakers }} 位講者</div>
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
                  class="text-xs px-2.5 py-1 rounded-lg bg-gray-50 text-gray-600 border border-gray-100">
              {{ p.name }} <span class="text-gray-400">{{ p.books }} 本</span>
            </span>
          </div>

          <!-- 吉福德：連到專頁 -->
          <div v-else-if="a.source === 'gifford'" class="mt-4">
            <NuxtLink to="/research-data/contemporary-theology/gifford"
                      class="text-xs text-indigo-700 hover:underline">列出歷屆講者與講題 →</NuxtLink>
          </div>

          <!-- 書目區 -->
          <div v-else class="mt-4">
            <div v-if="a.regions?.length" class="flex flex-wrap gap-1.5 mb-3">
              <span v-for="r in a.regions" :key="r"
                    class="text-xs px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">{{ r }}</span>
            </div>
            <div class="flex gap-4 flex-wrap">
              <button @click="toggle(a.slug, 'bib')" class="text-xs text-indigo-700 hover:underline">
                {{ open === a.slug + ':bib' ? '收合書目' : `列出 ${a.count} 筆書目` }}
              </button>
              <button v-if="arts[a.slug]?.count" @click="toggle(a.slug, 'art')"
                      class="text-xs text-sky-700 hover:underline">
                {{ open === a.slug + ':art' ? '收合論文' : `華語期刊論文 ${arts[a.slug].count} 篇` }}
              </button>
            </div>

            <ul v-if="open === a.slug + ':art'" class="mt-3 space-y-2">
              <li v-for="(t, j) in arts[a.slug].items" :key="j" class="text-xs text-gray-600 leading-relaxed">
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
            <ul v-if="open === a.slug + ':bib'" class="mt-3 space-y-2.5">
              <li v-for="(b, i) in a.items" :key="i" class="text-xs text-gray-600 leading-relaxed">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <span class="text-gray-400 tabular-nums">{{ b.year }}</span>
                  <span class="font-semibold text-gray-800 break-words">{{ b.author_zh }}《{{ b.title_zh }}》</span>
                  <span v-if="b.region" class="text-indigo-600">{{ b.region }}</span>
                  <span class="px-1.5 rounded" :class="b.in_library ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-50 text-gray-400'">
                    {{ b.in_library ? '已入館' : '缺' }}
                  </span>
                  <span v-if="b.zh" class="text-amber-700">中譯：{{ b.zh }}</span>
                </div>
                <div class="text-gray-400 break-words">{{ b.author }}, <em>{{ b.title }}</em>（{{ b.lang }}）</div>
                <div v-if="b.note" class="text-gray-500 break-words">{{ b.note }}</div>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <p class="mt-8 text-xs text-gray-400 leading-relaxed">
        ⚠️「已入館／缺」是把書目題名（原文與中譯都比）拿去對電子圖書館的比對結果，
        取寧可漏報不可誤報的一側：館內 13% 的書把書名誤填在作者欄、11% 作者欄空白，
        靠作者佐證會失準，因此標為「缺」的未必真的沒有。缺書清單會倒進
        <code>data/zlib-wanted/contemporary-theology.jsonl</code> 交每日排程去找。
      </p>
      <p class="mt-3 text-xs text-gray-400 leading-relaxed">
        ⚠️ 各區的「華語期刊論文」是拿關鍵詞掃
        <NuxtLink to="/research-data/press" class="text-sky-700 hover:underline">華藝篇目索引</NuxtLink>
        十二份神學期刊（11,111 篇）篩出來的<strong>候選清單，未經人工複核</strong>：
        一篇可以同時落在多區，也必然有假命中（篇名裡有「敘事」不等於敘事神學）。
        卷期與起訖頁照華藝原樣保留，可直接做註腳。
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
interface Part { name: string; books: number; chunks: number }
interface Area {
  slug: string; name: string; icon: string; desc: string
  source: 'bibliography' | 'gifford' | 'library'
  count?: number; in_library?: number; regions?: string[]; items?: Item[]
  speakers?: number; books?: number; chunks?: number; parts?: Part[]
}

interface Art {
  journal: string; title: string; authors: string[]
  issue: string; date: string; pages: string; fulltext: boolean
}
const areas = ref<Area[]>([])
const arts = ref<Record<string, { count: number; items: Art[] }>>({})
const pending = ref(true)
const open = ref('')
const toggle = (slug: string, kind: 'bib' | 'art') => {
  const k = `${slug}:${kind}`
  open.value = open.value === k ? '' : k
}

const badgeClass = (s: string) => s === 'library'
  ? 'bg-amber-50 text-amber-700'
  : s === 'gifford' ? 'bg-violet-50 text-violet-700' : 'bg-indigo-50 text-indigo-700'
const badgeLabel = (s: string) => s === 'library'
  ? '電子圖書館館藏' : s === 'gifford' ? '歷屆名單' : '策展書目'

onMounted(async () => {
  try {
    const d = await $fetch<{ areas: Area[] }>(
      '/content/research-data/contemporary-theology/index.json', { responseType: 'json' })
    areas.value = d?.areas ?? []
    try {
      const a = await $fetch<{ areas: Record<string, { count: number; items: Art[] }> }>(
        '/content/research-data/contemporary-theology/articles.json', { responseType: 'json' })
      arts.value = a?.areas ?? {}
    } catch { arts.value = {} }
  } catch { areas.value = [] } finally { pending.value = false }
})

useHead({ title: '當代神學研究 — Know Graph Lab' })
</script>
