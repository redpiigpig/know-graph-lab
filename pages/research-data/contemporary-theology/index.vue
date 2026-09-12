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

            <div v-if="open === a.slug + ':art'" class="mt-3">
              <p v-if="arts[a.slug].precision != null"
                 class="text-xs mb-3 px-3 py-2 rounded-lg leading-relaxed break-words"
                 :class="precClass(arts[a.slug].precision)">
                抽樣複核：隨機抽 {{ arts[a.slug].sample }} 筆逐筆判讀，<strong>其中
                {{ Math.round(arts[a.slug].precision * 100) }}% 真的屬於本區</strong>。
                <span v-if="arts[a.slug].weak_terms?.length">
                  假命中集中在「{{ arts[a.slug].weak_terms.join('」「') }}」這幾個詞上，
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

      <section v-if="doaj.journals" class="mt-5 bg-white rounded-2xl border border-gray-100 p-6">
        <div class="flex items-start gap-4 mb-3">
          <div class="text-2xl leading-none mt-0.5">🔓</div>
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2 flex-wrap">
              <h2 class="text-lg font-bold text-gray-900">開放取用期刊（DOAJ）</h2>
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">全文開放</span>
            </div>
            <p class="text-sm text-gray-500 leading-relaxed mt-1 break-words">
              DOAJ 收錄的宗教與神學期刊，按 LCC 十類取得。<strong>不綁機構 IP</strong>，
              是唯一能無條件排程更新的一批；語言重心也不在英語世界。
            </p>
          </div>
          <div class="text-right flex-shrink-0 text-xs text-gray-400 leading-relaxed">
            <div class="text-base font-semibold text-gray-700">{{ doaj.journals }} 種</div>
            <div>{{ doaj.articles.toLocaleString() }} 篇</div>
          </div>
        </div>
        <button @click="open = open === 'doaj' ? '' : 'doaj'" class="text-xs text-emerald-700 hover:underline">
          {{ open === 'doaj' ? '收合' : '列出篇目最多的四十種' }}
        </button>
        <ul v-if="open === 'doaj'" class="mt-3 space-y-1.5">
          <li v-for="(r, i) in doaj.rows.slice(0, 40)" :key="i" class="text-xs text-gray-600 flex gap-3">
            <span class="text-gray-400 tabular-nums w-14 text-right flex-shrink-0">{{ r.articles }}</span>
            <span class="break-words">
              {{ r.title }}
              <span class="text-gray-400">{{ r.country }}．{{ (r.language || []).join('/') }}</span>
            </span>
          </li>
        </ul>
      </section>


      <section v-if="cref.journals" class="mt-5 bg-white rounded-2xl border border-gray-100 p-6">
        <div class="flex items-start gap-4 mb-3">
          <div class="text-2xl leading-none mt-0.5">🔗</div>
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2 flex-wrap">
              <h2 class="text-lg font-bold text-gray-900">期刊篇目（Crossref）</h2>
              <span class="text-xs px-2 py-0.5 rounded-full bg-violet-50 text-violet-700">中繼資料 CC0</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">卷期頁碼齊全</span>
            </div>
            <p class="text-sm text-gray-500 leading-relaxed mt-1 break-words">
              收 Crossref 上宗教與神學類期刊的篇目。它與 DOAJ 的差別是<strong>帶卷、期與起訖頁</strong>——
              做註腳非有不可的三個欄位，華藝之外只有它有。
              原訂補這個缺口的是圖賓根的 Index Theologicus，但該站整站（連
              <code>robots.txt</code> 與 OAI-PMH）都擋在一道 proof-of-work 瀏覽器驗證後面，
              底層的 K10plus 公開介面又只有書刊層沒有單篇層，因此改走 Crossref。
            </p>
          </div>
          <div class="text-right flex-shrink-0 text-xs text-gray-400 leading-relaxed">
            <div class="text-base font-semibold text-gray-700">{{ cref.journals }} 種</div>
            <div>{{ cref.articles.toLocaleString() }} 篇</div>
          </div>
        </div>
        <p class="text-xs text-amber-700 leading-relaxed break-words mb-3">
          ⚠️ <strong>不要拿篇目的 language 欄算語言分布。</strong>那一欄由出版社自行登記，實測大量誤標：
          《Praktische Theologie》3,489 篇中 3,145 篇標成英文、《Zeitschrift für Pädagogik und Theologie》
          606 篇全標英文、《Archiv für katholisches Kirchenrecht》8,828 篇全部未標。
          按刊名判斷的非英語刊有 {{ cref.nonenglish_journals }} 種／{{ cref.nonenglish_articles.toLocaleString() }} 篇，
          這是下界而不是實數。
        </p>
        <button @click="open = open === 'cref' ? '' : 'cref'" class="text-xs text-violet-700 hover:underline">
          {{ open === 'cref' ? '收合' : '列出篇目最多的四十種' }}
        </button>
        <ul v-if="open === 'cref'" class="mt-3 space-y-1.5">
          <li v-for="(r, i) in cref.rows.slice(0, 40)" :key="i" class="text-xs text-gray-600 flex gap-3">
            <span class="text-gray-400 tabular-nums w-16 text-right flex-shrink-0">{{ r.articles.toLocaleString() }}</span>
            <span class="break-words">
              {{ r.title }}
              <span class="text-gray-400">{{ r.publisher }}</span>
              <span v-if="r.in_doaj" class="text-emerald-600">．DOAJ 也收</span>
            </span>
          </li>
        </ul>
      </section>

      <p class="mt-8 text-xs text-gray-400 leading-relaxed">
        ⚠️「已入館／缺」是把書目題名（原文與中譯都比）拿去對電子圖書館的比對結果，
        取寧可漏報不可誤報的一側：館內 13% 的書把書名誤填在作者欄、11% 作者欄空白，
        靠作者佐證會失準，因此標為「缺」的未必真的沒有。缺書清單會倒進
        <code>data/zlib-wanted/contemporary-theology.jsonl</code> 交每日排程去找。
      </p>
      <p class="mt-3 text-xs text-gray-400 leading-relaxed">
        ⚠️ 各區的「華語期刊論文」是拿關鍵詞掃
        <NuxtLink to="/research-data/press" class="text-sky-700 hover:underline">華藝篇目索引</NuxtLink>
        十二份神學期刊（11,111 篇）篩出來的<strong>候選清單</strong>：
        一篇可以同時落在多區，也必然有假命中（篇名裡有「敘事」不等於敘事神學）。
        2026-09-12 已逐區隨機抽 20 筆複核並把<strong>抽樣精確率印在各區的論文清單上</strong>，
        範圍從 35%（各地的神學、敘事神學）到 100%（神學史、性別神學、解放神學、世俗神學）。
        假命中沒有被刪掉——刪掉會一併犧牲召回率而且看不出來漏了什麼，
        改成把只靠低精確率的詞命中的篇目另列一區。
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
  hit?: string[]; weak?: boolean
}
interface ArtArea {
  count: number; items: Art[]
  weak_terms?: string[]; weak_count?: number
  sample?: number; precision?: number | null
}
const areas = ref<Area[]>([])
const arts = ref<Record<string, ArtArea>>({})
const doaj = ref<{ journals: number; articles: number; rows: any[] }>(
  { journals: 0, articles: 0, rows: [] })
const cref = ref<{ journals: number; articles: number
                   nonenglish_journals: number; nonenglish_articles: number
                   rows: any[] }>(
  { journals: 0, articles: 0, nonenglish_journals: 0, nonenglish_articles: 0, rows: [] })
const pending = ref(true)
const open = ref('')
const toggle = (slug: string, kind: 'bib' | 'art') => {
  const k = `${slug}:${kind}`
  open.value = open.value === k ? '' : k
}

const strongOf = (slug: string) => (arts.value[slug]?.items ?? []).filter(t => !t.weak)
const weakOf = (slug: string) => (arts.value[slug]?.items ?? []).filter(t => t.weak)
const precClass = (p: number) => p >= 0.9
  ? 'bg-emerald-50 text-emerald-800'
  : p >= 0.7 ? 'bg-amber-50 text-amber-800' : 'bg-rose-50 text-rose-800'

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
      const a = await $fetch<{ areas: Record<string, ArtArea> }>(
        '/content/research-data/contemporary-theology/articles.json', { responseType: 'json' })
      arts.value = a?.areas ?? {}
    } catch { arts.value = {} }
    try {
      doaj.value = await $fetch('/content/research-data/contemporary-theology/doaj.json',
                                { responseType: 'json' })
    } catch { /* 沒抓過就不顯示這一區 */ }
    try {
      cref.value = await $fetch('/content/research-data/contemporary-theology/crossref.json',
                                { responseType: 'json' })
    } catch { /* 沒抓過就不顯示這一區 */ }
  } catch { areas.value = [] } finally { pending.value = false }
})

useHead({ title: '當代神學研究 — Know Graph Lab' })
</script>
