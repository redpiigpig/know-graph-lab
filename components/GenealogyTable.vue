<!--
  〈從使徒到大公〉譜系歸屬表 — /works/christian-genealogy 的「譜系歸屬」分頁。
  資料來自 data/christian-genealogy/web-summary.json（由 scripts/genealogy_export_web.py 產生）。
  完整資料（逐段 sources、逐份 rationale 全文）留在各原始檔，不進 client bundle。
-->
<template>
  <div class="space-y-10">
    <!-- 概覽 -->
    <section>
      <div class="flex items-start justify-between gap-3 flex-wrap mb-3">
        <div>
          <h2 class="text-base font-semibold text-gray-900">譜系歸屬</h2>
          <p class="text-xs text-gray-500 mt-0.5 max-w-3xl leading-relaxed">
            把新約每一節與每一份一二世紀文獻，逐筆掛回它所出自的群體。四層代號：地方見證群體、使徒軌跡、城市傳統、獨立分支。
            每一條歸屬都要說得出憑什麼——有學者支持的引書目，沒有的標明是本表判斷並寫出可被反駁的理由。
          </p>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-px bg-gray-200 border border-gray-200 rounded-xl overflow-hidden">
        <div v-for="s in stats" :key="s.l" class="bg-white px-4 py-3">
          <div class="text-2xl font-serif tabular-nums text-gray-900">{{ s.n }}</div>
          <div class="text-[11px] text-gray-500 mt-0.5">{{ s.l }}</div>
        </div>
      </div>
    </section>

    <!-- 代號樹 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-1">代號樹</h3>
      <p class="text-xs text-gray-500 mb-4 leading-relaxed">
        小寫希臘＝前使徒的地方群體，字母取自該群體在文獻裡的那個希臘字（<code class="font-mono">Συνέδριον</code> 是公會的本字、<code class="font-mono">ὑπερῷον</code> 是徒 1:13 稱那間樓房的本字）；
        大寫拉丁＝使徒軌跡，後代沿同一字母延伸而不另立異端碼；G＝不掛任何使徒、自有文獻者。
      </p>
      <div v-for="grp in treeGroups" :key="grp.label" class="mb-4">
        <div class="text-[11px] font-mono uppercase tracking-widest text-gray-400 mb-2">{{ grp.label }}</div>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-gray-200 border border-gray-200 rounded-xl overflow-hidden">
          <div v-for="n in grp.nodes" :key="n.code" class="bg-white px-4 py-3 flex gap-3">
            <div class="font-serif text-2xl leading-none w-8 text-center flex-shrink-0" :class="grp.color">{{ n.code }}</div>
            <div class="min-w-0">
              <div class="text-sm font-semibold text-gray-900 leading-snug">{{ n.name }}</div>
              <div v-if="n.etymon" class="text-[11px] font-mono text-gray-400 mt-0.5">{{ n.etymon }}</div>
              <div v-if="n.sub?.length" class="text-xs text-gray-500 mt-1.5 leading-relaxed break-words">
                {{ n.sub.map((s) => s.code + ' ' + s.name).join('　·　') }}
              </div>
              <div v-if="n.character" class="text-xs text-gray-600 mt-1.5 leading-relaxed">{{ n.character }}</div>
            </div>
          </div>
        </div>
      </div>
      <p class="text-xs text-amber-800 bg-amber-50 border-l-2 border-amber-400 px-4 py-3 rounded-r leading-relaxed">
        <b>立節點的條件是有存世的自產文獻。</b>{{ data.tree.inclusionRule }}——馬吉安、孟他努、巴西里底、尼哥拉派據此都不立。
      </p>
    </section>

    <!-- 逐節分佈 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-1">逐節來源分佈</h3>
      <p class="text-xs text-gray-500 mb-3">{{ data.counts.verses.toLocaleString() }} 節 · {{ data.counts.segments.toLocaleString() }} 段 · 一段多來源者按等分攤</p>
      <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-[11px] uppercase tracking-wide text-gray-500">
            <tr><th class="text-left px-4 py-2 font-medium">代號</th><th class="text-left px-4 py-2 font-medium">群體</th>
              <th class="text-right px-4 py-2 font-medium">節數</th><th class="text-left px-4 py-2 font-medium w-2/5">占比</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in data.tally" :key="t.code" class="border-t border-gray-100">
              <td class="px-4 py-2"><span class="font-mono text-xs bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded">{{ t.code }}</span></td>
              <td class="px-4 py-2 text-gray-700">{{ t.name }}</td>
              <td class="px-4 py-2 text-right tabular-nums text-gray-600">{{ t.verses }}</td>
              <td class="px-4 py-2">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden min-w-[3rem]">
                    <div class="h-full bg-emerald-600 rounded-full" :style="{ width: (t.pct / data.tally[0].pct * 100) + '%' }"></div>
                  </div>
                  <span class="text-xs tabular-nums text-gray-500 w-11 text-right">{{ t.pct }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="text-xs text-gray-600 mt-3 leading-relaxed">
        <b>保羅一條線合計約 35%</b>（U1＋U2＋U3＋U4＋U5＋U5a＋U5b）——一個沒跟過地上耶穌的人，在正典裡佔的篇幅最大。
        第一層六個地方群體合計不到 8%，但撐住的是最關鍵的幾段：埋葬地點、空墳、議會內情、樓房。
      </p>
    </section>

    <!-- 新約二十七卷 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-2">新約二十七卷</h3>
      <div class="flex flex-wrap gap-1.5 mb-3">
        <button v-for="f in bookFilters" :key="f.k" @click="bookFilter = f.k"
          class="text-xs px-3 py-1.5 rounded-lg border transition"
          :class="bookFilter === f.k ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'">
          {{ f.l }}
        </button>
      </div>
      <div class="border border-gray-200 rounded-xl overflow-hidden bg-white divide-y divide-gray-100">
        <details v-for="b in filteredBooks" :key="b.code" class="group" :class="b.own ? 'border-l-2 border-amber-500' : ''">
          <summary class="px-4 py-3 cursor-pointer flex items-baseline justify-between gap-3 flex-wrap hover:bg-gray-50">
            <span class="font-semibold text-gray-900">{{ b.name }}
              <span class="ml-2 text-xs font-normal text-gray-400 tabular-nums">{{ b.verses }} 節 · {{ b.segments }} 段</span></span>
            <span class="text-xs text-gray-600">
              <span class="font-mono bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded">{{ b.editor }}</span>
              {{ b.editorName }}
              <span v-if="b.own" class="ml-1 font-mono bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">自行判斷</span>
              <span v-if="b.divergence" class="ml-1 font-mono bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">⚠ 年代分歧</span>
            </span>
          </summary>
          <div class="px-4 pb-4 text-sm space-y-1.5">
            <div><span class="text-[11px] font-mono uppercase text-gray-400 mr-2">年代</span>{{ b.date }}</div>
            <div><span class="text-[11px] font-mono uppercase text-gray-400 mr-2">寫作地</span>{{ b.place }}</div>
            <div v-if="b.divergence" class="text-gray-500">
              <span class="text-[11px] font-mono uppercase text-gray-400 mr-2">大藏經</span>{{ b.dateTraditional }}　{{ b.placeTraditional }}
            </div>
            <div><span class="text-[11px] font-mono uppercase text-gray-400 mr-2">依據</span>
              <span v-for="s in b.support" :key="s" class="inline-block font-mono text-[11px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded mr-1">{{ s }}</span>
            </div>
            <p class="text-gray-600 leading-relaxed pt-1">{{ b.rationale }}</p>

            <!-- 逐段清單：幾節到幾節 · 主題 · 來源 -->
            <div v-if="segs(b.code)" class="mt-4">
              <div class="text-[11px] font-mono uppercase tracking-wide text-gray-400 mb-1.5">
                逐段來源　{{ segs(b.code).rows.length }} 段
              </div>
              <p v-if="segs(b.code).meta.layers" class="text-xs text-gray-500 mb-2 leading-relaxed">
                {{ segs(b.code).meta.layers }}
              </p>
              <div class="border border-gray-200 rounded-lg overflow-hidden bg-white">
                <table class="w-full text-[13px]">
                  <thead class="bg-gray-50 text-[10.5px] uppercase tracking-wide text-gray-500">
                    <tr>
                      <th class="text-left px-3 py-1.5 font-medium whitespace-nowrap">節</th>
                      <th class="text-left px-3 py-1.5 font-medium">主題</th>
                      <th class="text-left px-3 py-1.5 font-medium whitespace-nowrap">來源</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="r in segs(b.code).rows" :key="r.ref" class="border-t border-gray-100 align-top">
                      <td class="px-3 py-1.5 font-mono text-[12px] text-gray-500 whitespace-nowrap">{{ r.ref }}</td>
                      <td class="px-3 py-1.5 text-gray-800">
                        {{ r.title }}
                        <div v-if="r.note" class="text-xs text-gray-500 mt-0.5 leading-relaxed">{{ r.note }}</div>
                      </td>
                      <td class="px-3 py-1.5 whitespace-nowrap">
                        <span v-for="c in r.src" :key="c"
                          class="inline-block font-mono text-[11px] bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded mr-1">{{ c }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </details>
      </div>
    </section>

    <!-- 典外文獻 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-1">典外文獻</h3>
      <p class="text-xs text-gray-500 mb-3 leading-relaxed">
        學界分類與譜系歸屬分兩欄：分類問「這是哪一類文本」，譜系問「這保存了誰的記憶、由誰傳下」。兩欄可以完全不對稱——
        《腓力福音》掛腓力之名、實為瓦倫廷派。<b>借名本身就是譜系資料</b>。
      </p>
      <div class="flex flex-wrap gap-1.5 mb-3">
        <button v-for="f in apocFilters" :key="f.k" @click="apocFilter = f.k"
          class="text-xs px-3 py-1.5 rounded-lg border transition"
          :class="apocFilter === f.k ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'">
          {{ f.l }}
        </button>
      </div>
      <div class="border border-gray-200 rounded-xl overflow-hidden bg-white divide-y divide-gray-100">
        <details v-for="a in filteredApoc" :key="a.slug" class="group" :class="a.own ? 'border-l-2 border-amber-500' : ''">
          <summary class="px-4 py-3 cursor-pointer flex items-baseline justify-between gap-3 flex-wrap hover:bg-gray-50">
            <span class="font-semibold text-gray-900">{{ a.title }}
              <span class="ml-2 text-xs font-normal text-gray-400 tabular-nums">{{ a.date[0] }}–{{ a.date[1] }}　{{ a.sections ? a.sections + ' 節' : '站上無全文' }}</span></span>
            <span class="text-xs text-gray-600">
              <template v-if="a.actual.length">
                <span v-for="c in a.actual" :key="c" class="font-mono bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded mr-1">{{ c }}</span>
              </template>
              <span v-else class="font-mono bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">無傳承</span>
              <span v-if="a.attributed.length" class="text-gray-400 ml-1">掛名 {{ a.attributed.join('／') }}</span>
              <span v-if="a.beyond" class="ml-1 font-mono bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">逾325</span>
            </span>
          </summary>
          <div class="px-4 pb-4 text-sm space-y-1.5">
            <div><span class="text-[11px] font-mono uppercase text-gray-400 mr-2">分類</span>{{ a.group }}　·　{{ a.nta }}</div>
            <div><span class="text-[11px] font-mono uppercase text-gray-400 mr-2">寫作地</span>{{ a.place }}
              <span v-if="a.placeKind === 'findspot'" class="ml-1 font-mono text-[11px] bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">僅知出土地</span>
              <span v-else-if="a.placeKind === 'claimed'" class="ml-1 font-mono text-[11px] bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">文獻自稱</span>
            </div>
            <p class="text-gray-600 leading-relaxed pt-1">{{ a.rationale }}</p>
          </div>
        </details>
      </div>
    </section>

    <!-- 諾斯底文庫 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-2">諾斯底文庫</h3>
      <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-[11px] uppercase tracking-wide text-gray-500">
            <tr><th class="text-left px-4 py-2 font-medium">類</th><th class="text-right px-4 py-2 font-medium">種數</th>
              <th class="text-left px-4 py-2 font-medium">歸屬</th><th class="text-left px-4 py-2 font-medium">說明</th></tr>
          </thead>
          <tbody>
            <tr v-for="g in data.gnosticRules" :key="g.key" class="border-t border-gray-100 align-top">
              <td class="px-4 py-2 font-mono text-xs">{{ g.key }}</td>
              <td class="px-4 py-2 text-right tabular-nums text-gray-600">{{ g.n }}</td>
              <td class="px-4 py-2">
                <span v-if="g.excluded" class="font-mono text-xs bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded">排除</span>
                <template v-else-if="g.actual.length">
                  <span v-for="c in g.actual" :key="c" class="font-mono text-xs bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded mr-1">{{ c }}</span>
                </template>
                <span v-else class="font-mono text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">證據非節點</span>
              </td>
              <td class="px-4 py-2 text-gray-600 leading-relaxed">{{ g.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="text-xs text-amber-800 bg-amber-50 border-l-2 border-amber-400 px-4 py-3 rounded-r leading-relaxed mt-3">{{ data.gnosticWarning }}</p>
    </section>

    <!-- 書目 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-1">書目</h3>
      <p class="text-xs text-gray-500 mb-3">{{ data.bibliography.length }} 筆。標「原文註釋」者直接取自〈從使徒到大公〉自己的 35 條註釋。</p>
      <div class="border border-gray-200 rounded-xl overflow-hidden bg-white divide-y divide-gray-100 text-sm">
        <div v-for="e in data.bibliography" :key="e.key" class="px-4 py-2.5 grid sm:grid-cols-[8rem_1fr] gap-x-4 gap-y-1">
          <div class="font-mono text-xs text-gray-900">{{ e.key }}</div>
          <div>
            <div class="text-gray-700 leading-relaxed">{{ e.ref }}</div>
            <div class="text-xs text-gray-400 mt-0.5">
              {{ e.supports }}
              <span class="ml-1 font-mono" :class="e.provenance === 'article-footnote' ? 'text-emerald-700' : 'text-gray-400'">
                {{ e.provenance === 'article-footnote' ? '· 原文註釋' : '· 本表另補' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <p class="text-xs text-gray-400 leading-relaxed">
      資料層在 <code class="font-mono">data/christian-genealogy/</code>；本頁摘要由
      <code class="font-mono">scripts/genealogy_export_web.py</code> 產生。段落界線取自 ACCS 的段落總論，
      節次骨架取自站上經文資料。雜誌第十二期原文未經本表改動。
    </p>
  </div>
</template>

<script setup lang="ts">
import raw from '~/data/christian-genealogy/web-summary.json'

const data = raw as any

const stats = computed(() => [
  { n: data.counts.verses.toLocaleString(), l: '新約節數（逐節皆已歸屬）' },
  { n: data.counts.segments.toLocaleString(), l: '段落' },
  { n: data.counts.books, l: '卷全部完成' },
  { n: data.counts.apocrypha, l: '典外文獻' },
  { n: data.counts.gnostic, l: '諾斯底文庫' },
  { n: data.counts.bibliography, l: '書目' },
])

const treeGroups = computed(() => [
  { label: '第一層　地方見證群體 · 北方', color: 'text-sky-700', nodes: data.tree.layer1.filter((n: any) => n.region === 'north') },
  { label: '第一層　地方見證群體 · 南方', color: 'text-violet-700', nodes: data.tree.layer1.filter((n: any) => n.region === 'south') },
  { label: '第二層　使徒軌跡', color: 'text-emerald-700', nodes: data.tree.layer2 },
  { label: '第三層　獨立分支（有自產文獻、不掛任何使徒）', color: 'text-emerald-700', nodes: data.tree.layer3 },
])

const bookFilter = ref('all')
const bookFilters = computed(() => [
  { k: 'all', l: `全部 ${data.books.length} 卷` },
  { k: 'own', l: `自行判斷 ${data.books.filter((b: any) => b.own).length} 卷` },
  { k: 'div', l: `年代分歧 ${data.books.filter((b: any) => b.divergence).length} 卷` },
  ...[...new Set(data.books.map((b: any) => b.editor))].map((e) => ({ k: e as string, l: e as string })),
])
const segs = (code: string) => data.segments?.[code] || null

const filteredBooks = computed(() => data.books.filter((b: any) =>
  bookFilter.value === 'all' ? true : bookFilter.value === 'own' ? b.own : bookFilter.value === 'div' ? b.divergence : b.editor === bookFilter.value))

const apocFilter = ref('all')
const apocFilters = computed(() => [
  { k: 'all', l: `全部 ${data.apocrypha.length} 種` },
  { k: 'own', l: '自行判斷' },
  { k: 'borrowed', l: '只有借名、無傳承' },
  { k: '福音書', l: '福音書' },
  { k: '非福音', l: '非福音' },
])
const filteredApoc = computed(() => data.apocrypha.filter((a: any) =>
  apocFilter.value === 'all' ? true
    : apocFilter.value === 'own' ? a.own
    : apocFilter.value === 'borrowed' ? (a.attributed.length && !a.actual.length)
    : a.group === apocFilter.value))
</script>
