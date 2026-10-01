<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="displayTitle"
      :back="{ to: backTo, label: divLabel }"
      :editable="false"
    >
      <template #actions>
        <button
          class="px-2.5 py-1 text-[11px] rounded-lg border transition mr-1.5"
          :class="dictOpen
            ? 'bg-amber-600 text-white border-amber-600'
            : 'bg-white text-gray-500 border-gray-200 hover:border-amber-300'"
          title="查佛學辭典（先選取經文可直接帶入）"
          @click="openDict()"
        >📖 辭典</button>
      </template>
    </AppHeader>

    <!--
      讀經時的辭典面板。⚠️ 佛典最常見的需求是「這個詞是什麼意思」，
      而讀者多半是先用滑鼠選起那個詞——所以開啟時先吃 window.getSelection()，
      選了就直接查，沒選才要自己打。
    -->
    <div v-if="dictOpen" class="border-b border-gray-200 bg-white">
      <div class="max-w-5xl mx-auto px-6 py-4">
        <div class="flex items-baseline justify-between gap-3 mb-3">
          <h2 class="text-sm font-semibold text-gray-700">佛學辭典查詢</h2>
          <button class="text-xs text-gray-400 hover:text-gray-700" @click="dictOpen = false">關閉</button>
        </div>
        <GlossaryLookup :initial="dictTerm" :scroll="true"
                        placeholder="選取經文後按「辭典」可直接帶入，或在此輸入" />
      </div>
    </div>

    <div v-if="pending" class="flex-1 flex items-center justify-center text-sm text-gray-400">載入中…</div>
    <div v-else-if="err" class="flex-1 flex items-center justify-center px-6">
      <p class="max-w-lg text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl p-5 leading-relaxed">{{ err }}</p>
    </div>

    <div v-else class="flex-1 flex">
      <!-- 側欄：卷 + 目錄樹 -->
      <aside class="hidden lg:block w-64 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto max-h-[calc(100dvh-3.5rem)] sticky top-14">
        <div class="p-4 border-b border-gray-100">
          <div class="text-sm font-semibold text-gray-800 leading-snug"
               :class="work.canon === 'DK' ? 'font-serif' : ''">{{ displayTitle }}</div>
          <div v-if="work.canon === 'DK' && work.title_en"
               class="text-[11px] text-gray-500 italic mt-1 leading-snug">{{ work.title_en }}</div>
          <div v-if="work.canon === 'DK' && work.title_sa"
               class="text-[11px] text-gray-400 italic mt-0.5 leading-snug">{{ work.title_sa }}</div>
          <!-- 漢譯對照本。標題寫「對照」不寫「漢譯書名」——它不是這部經的名字，
               是同一部印度原典另外譯成漢文的那幾部經。 -->
          <div v-if="zhParallels.length" class="mt-2 pt-2 border-t border-gray-100">
            <div class="text-[10px] text-gray-400 mb-1">漢譯對照（東北目錄）</div>
            <NuxtLink
              v-for="pl in zhParallels"
              :key="pl.id"
              :to="`/tripitaka/w/${pl.id}`"
              class="block text-[11px] text-amber-700 hover:underline truncate"
              :title="pl.checked === false ? '東北目錄的書名與經號對不上，待判讀' : ''"
            >{{ pl.title }}<span class="text-gray-400 font-mono"> {{ pl.id }}</span><span
              v-if="pl.checked === false" class="text-gray-400"> ⚠</span></NuxtLink>
          </div>
          <div class="text-[11px] text-gray-400 mt-1 leading-relaxed">
            <div v-if="work.byline">{{ work.byline }}</div>
            <!-- 🚨 這是 84000 的**現代英譯者**，不是把它譯成藏文的九世紀譯師。
                 標籤一定要寫清楚，否則等於在一部藏文經旁邊掛錯譯者。 -->
            <div v-if="work.canon === 'DK' && work.translator_en" class="mt-0.5">
              84000 英譯：{{ work.translator_en }}
            </div>
            <div class="font-mono mt-0.5">
              <span v-if="work.canon === 'DK' && work.toh">Toh {{ work.toh }} · </span>{{ work.id }} · {{ work.extent }}
            </div>
          </div>
        </div>

        <!-- 甘珠爾：函 ＋ 函內葉碼區段。藏文佛典沒有「卷」。 -->
        <div v-if="pages.length > 1" class="p-3 border-b border-gray-100">
          <div class="text-[11px] text-gray-400 mb-1.5">函・葉</div>
          <div v-for="v in pageVols" :key="v.vol" class="mb-2 last:mb-0">
            <div class="text-[10px] text-gray-400 mb-0.5">第 {{ v.vol }} 函</div>
            <div class="flex flex-wrap gap-1">
              <NuxtLink
                v-for="pg in v.items"
                :key="pg.key"
                :to="`/tripitaka/w/${id}?page=${pg.key}`"
                class="px-2 py-0.5 text-[11px] rounded border transition font-mono"
                :class="pg.key === page
                  ? 'bg-amber-600 text-white border-amber-600'
                  : 'border-gray-200 text-gray-600 hover:border-amber-300'"
              >{{ pg.label }}</NuxtLink>
            </div>
          </div>
        </div>

        <div v-if="juans.length > 1" class="p-3 border-b border-gray-100">
          <div class="text-[11px] text-gray-400 mb-1.5">卷</div>
          <div class="flex flex-wrap gap-1">
            <NuxtLink
              v-for="j in juans"
              :key="j"
              :to="`/tripitaka/w/${id}?juan=${j}`"
              class="px-2 py-0.5 text-[11px] rounded border transition"
              :class="j === juan
                ? 'bg-amber-600 text-white border-amber-600'
                : 'border-gray-200 text-gray-600 hover:border-amber-300'"
            >{{ j }}</NuxtLink>
          </div>
        </div>

        <nav v-if="tocInJuan.length" class="p-3">
          <div class="text-[11px] text-gray-400 mb-1.5">本卷目次</div>
          <a
            v-for="n in tocInJuan"
            :key="n.i"
            :href="`#${nodeUid(n)}`"
            class="block py-1 text-xs text-gray-600 hover:text-amber-700 truncate"
            :style="{ paddingLeft: `${n.depth * 10}px` }"
            :title="n.head"
          >{{ n.head }}</a>
        </nav>
      </aside>

      <!-- 正文 -->
      <main class="flex-1 min-w-0 px-4 sm:px-6 py-6">
        <div class="max-w-7xl mx-auto">
          <div class="mb-6 pb-4 border-b border-gray-200">
            <h1 class="text-xl font-bold text-gray-900" :class="work.canon === 'DK' ? 'font-serif' : ''">
              {{ displayTitle }}
              <span v-if="juan" class="text-base font-normal text-gray-400">卷第 {{ juan }}</span>
              <span v-else-if="curPage" class="text-base font-normal text-gray-400 font-sans">
                第 {{ curPage.vol }} 函 {{ curPage.label }}
              </span>
            </h1>
            <div v-if="work.canon === 'DK' && work.title_zh"
                 class="mt-1 text-sm text-amber-800">漢譯對照《{{ work.title_zh }}》<span
                   v-if="zhParallels.length > 1" class="text-gray-400"> 等 {{ zhParallels.length }} 部</span></div>
            <div class="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-400">
              <span class="font-mono">{{ work.id }}</span>
              <span v-if="work.byline">{{ work.byline }}</span>
              <span>{{ segments.length }} 段</span>
              <ParallelChips :w="work" class="ml-auto" />
            </div>
          </div>

          <!-- 欄位選擇：照聖經對照頁，一欄一個下拉，同一語言在下拉裡選版本 -->
          <div class="grid gap-2 mb-4" :style="{ gridTemplateColumns: colGrid }">
            <div
              v-for="(k, ci) in columns" :key="ci"
              class="bg-white border border-gray-200 rounded-md px-2 py-1.5 flex items-center gap-1 min-w-0"
            >
              <span class="text-[10px] tracking-wide text-gray-400 mr-1 flex-shrink-0">{{ LANG_NAME[langOfKey(k)] || '' }}</span>
              <select
                :value="k"
                class="flex-1 min-w-0 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer truncate"
                @change="setColumn(ci, ($event.target as HTMLSelectElement).value)"
              >
                <optgroup v-for="g in keyGroups" :key="g.lang" :label="LANG_NAME[g.lang] || g.lang">
                  <option v-for="o in g.keys" :key="o" :value="o">{{ keyLabel(o) }}</option>
                </optgroup>
              </select>
              <button
                v-if="columns.length > 1"
                class="text-gray-300 hover:text-red-500 text-xs px-1 flex-shrink-0"
                title="移除此欄"
                @click="columns.splice(ci, 1)"
              >✕</button>
            </div>
            <button
              v-if="columns.length < allKeys.length"
              class="bg-white border border-dashed border-gray-300 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:border-amber-400 hover:text-amber-700"
              @click="addColumn"
            >+ 對照欄</button>
          </div>

          <div class="space-y-1.5">
            <template v-for="(r, ri) in rows" :key="ri">
              <!-- 品題／經題 -->
              <h3 v-if="r.type === 'seg' && r.s.kind === 'head'" :id="r.s.uid"
                  class="scroll-mt-28 pt-4 pb-1 text-base font-semibold text-gray-800">{{ r.s.sources.lzh }}</h3>
              <p v-else-if="r.type === 'seg' && r.s.kind === 'byline'" :id="r.s.uid"
                 class="scroll-mt-28 text-xs text-gray-400 pb-1">{{ r.s.sources.lzh }}</p>

              <!-- 多譯本段落的開頭說明 -->
              <div v-if="r.type === 'unit' && r.first"
                   class="mt-3 mb-1 px-3 py-2 rounded-md border text-[11px] leading-relaxed"
                   :class="r.b.set.auto ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-emerald-50 border-emerald-200 text-emerald-900'">
                <span class="font-semibold">多譯本對照・{{ r.b.set.title }}</span>
                <span class="ml-1">（{{ r.b.set.versions.length }} 本，以義段為一節；佛典無跨語言通用的節號，義段為本站編訂{{ r.b.set.auto ? '；自動對齊、未經人工校讀，標 ? 者複核存疑' : '' }}）</span>
                <div class="mt-0.5 text-gray-500">
                  <span v-for="(k, ci) in columns" :key="ci" class="mr-3">
                    {{ LANG_NAME[langOfKey(k)] }}：{{ r.b.keys.get(k)?.label || (k === 'zh-mod' ? '（白話無此段落對應）' : '此本未收') }}
                  </span>
                </div>
              </div>

              <!-- 一節：左邊節號，右邊各欄（聖經對照頁同款） -->
              <article
                v-if="r.type === 'unit' || (r.s.kind !== 'head' && r.s.kind !== 'byline')"
                :id="r.type === 'seg' ? r.s.uid : `${r.b.set.slug}-${r.u.id}`"
                class="scroll-mt-28 bg-white border border-gray-200 rounded-md overflow-hidden"
              >
                <div v-if="r.type === 'unit'" class="px-3 pt-1.5 text-[11px] text-indigo-700 bg-stone-50 border-b border-gray-100">
                  {{ r.u.label }}<span v-if="r.u.doubt" class="ml-1 font-semibold text-amber-600" title="複核時被標為可能錯位">?</span>
                </div>
                <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: `auto ${colGrid}` }">
                  <div class="bg-stone-50 px-2 py-2 flex items-start">
                    <button v-if="r.type === 'seg'"
                            class="font-mono text-[10px] text-stone-500 hover:text-amber-600"
                            :title="`複製引用式 ${r.s.seg}`" @click="copy(r.s.seg)">{{ segCite(r.s) }}</button>
                    <span v-else class="font-mono text-sm font-semibold text-stone-700">{{ r.k + 1 }}</span>
                  </div>
                  <div v-for="(k, ci) in columns" :key="ci" class="bg-white px-3 py-2 min-w-0">
                    <p v-if="cellText(r, k)"
                       class="leading-loose text-gray-800 break-words"
                       :class="cellClass(r, k)"
                       v-html="cellHtml(r, k)" />
                    <span v-else class="text-gray-300 italic text-xs">—</span>
                  </div>
                </div>

                <!-- 段落層的附加資訊（只有一般段落有） -->
                <div v-if="r.type === 'seg' && (parallelsOf(r.s.uid).length || originalsOf(r.s.uid).length || termsOf(r.s.uid).length || r.s.notes?.length)"
                     class="px-3 py-2 border-t border-gray-100 space-y-1.5">
                  <div v-if="parallelsOf(r.s.uid).length" class="flex flex-wrap items-center gap-1.5">
                    <span class="text-[10px] text-gray-400">原文對應</span>
                    <span
                      v-for="(p, pi) in parallelsOf(r.s.uid)" :key="pi"
                      class="px-1.5 py-0.5 rounded border text-[11px]"
                      :class="[PARALLEL_SOURCES[p.src]?.cls || 'bg-gray-50 text-gray-600 border-gray-200', p.note === '部分平行' ? 'opacity-70' : '']"
                      :title="`${PARALLEL_SOURCES[p.src]?.label || p.src}：${PARALLEL_SOURCES[p.src]?.desc || ''}${p.note ? '（' + p.note + '）' : ''}`"
                    ><span class="font-medium">{{ PARALLEL_LANGS[p.lang]?.short || p.lang }}</span> {{ p.ref }}<span v-if="p.note === '部分平行'"> ～</span></span>
                  </div>
                  <!-- 整經原典（尚未切成義段的）：可展開，不與左側逐段並排 -->
                  <details v-for="(o, oi) in originalsOf(r.s.uid)" :key="`o${oi}`"
                           class="rounded-lg border border-indigo-200 bg-indigo-50/40 overflow-hidden">
                    <summary class="px-3 py-1.5 text-[11px] text-indigo-800 cursor-pointer hover:bg-indigo-50 flex items-center gap-2">
                      <span class="font-medium">{{ PARALLEL_LANGS[o.lang]?.label || o.lang }}原文</span>
                      <span class="text-indigo-600">{{ o.ref }}</span>
                      <span class="text-indigo-400">{{ o.lines.length }} 段</span>
                      <span v-if="o.partial" class="text-amber-700">部分平行</span>
                    </summary>
                    <div class="px-3 py-2 border-t border-indigo-100 bg-white/60 max-h-96 overflow-y-auto">
                      <p class="text-[10px] text-gray-400 mb-2 leading-relaxed">
                        以下為{{ PARALLEL_LANGS[o.lang]?.label || o.lang }}該經全文，段號為該語言自身的引用座標；
                        與漢文為<strong>同源異流的兩個本子</strong>，段落並非一一對應。
                      </p>
                      <div v-for="(ln, li) in o.lines" :key="li" class="flex gap-2 py-0.5 text-[13px]">
                        <span class="font-mono text-[9px] text-gray-300 w-20 flex-shrink-0 pt-1">{{ segLabel(ln[0]) }}</span>
                        <span class="font-serif text-gray-700 leading-relaxed">{{ ln[1] }}</span>
                      </div>
                    </div>
                  </details>
                  <div v-if="termsOf(r.s.uid).length" class="flex flex-wrap gap-1.5">
                    <span v-for="(t, ti) in termsOf(r.s.uid)" :key="ti"
                          class="px-1.5 py-0.5 rounded border border-sky-200 bg-sky-50 text-[11px] text-sky-800" title="CBETA 詞條對照">
                      {{ t.zh }}
                      <span class="text-sky-600 font-serif">{{ Object.entries(t.forms).map(([k, v]) => `${k === 'sa' ? '梵' : k === 'pi' ? '巴' : k}: ${v}`).join('　') }}</span>
                    </span>
                  </div>
                  <details v-if="r.s.notes?.length">
                    <summary class="text-[11px] text-gray-400 cursor-pointer hover:text-gray-600">校勘 {{ r.s.notes.length }} 條</summary>
                    <ul class="mt-1 pl-4 text-[11px] text-gray-500 space-y-0.5">
                      <li v-for="(n, ni) in r.s.notes" :key="ni">{{ n.text }}</li>
                    </ul>
                  </details>
                </div>
              </article>
            </template>
          </div>

          <div v-if="juans.length > 1" class="mt-10 pt-5 border-t border-gray-200 flex justify-between text-sm">
            <NuxtLink v-if="prevJuan" :to="`/tripitaka/w/${id}?juan=${prevJuan}`" class="text-amber-700 hover:underline">← 卷第 {{ prevJuan }}</NuxtLink><span v-else />
            <NuxtLink v-if="nextJuan" :to="`/tripitaka/w/${id}?juan=${nextJuan}`" class="text-amber-700 hover:underline">卷第 {{ nextJuan }} →</NuxtLink>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const dictOpen = ref(false)
const dictTerm = ref('')

/** 開啟辭典面板；若讀者已選取經文就直接拿去查。 */
function openDict() {
  if (dictOpen.value) { dictOpen.value = false; return }
  const sel = (typeof window !== 'undefined' ? window.getSelection()?.toString() : '') || ''
  // 只取前 12 字：選到一整段時拿整段去查一定落空
  const t = sel.trim().replace(/\s+/g, '').slice(0, 12)
  if (t) dictTerm.value = t
  dictOpen.value = true
}

import { PARALLEL_LANGS, PARALLEL_SOURCES, divisionByKey } from '~/data/tripitaka/divisions'

definePageMeta({ middleware: 'auth' })
const route = useRoute()
const router = useRouter()
const id = computed(() => String(route.params.id))

const supabase = useSupabaseClient()
const work = ref<any>(null)
const toc = ref<any[]>([])
const segments = ref<any[]>([])
const terms = ref<any[]>([])
const parallels = ref<any[]>([])
const originals = ref<Record<string, any[]>>({})
const juans = ref<number[]>([])
const juan = ref<number | null>(null)
const pages = ref<any[]>([])
const page = ref<string | null>(null)
const pending = ref(true)
const err = ref<string | null>(null)

/** 甘珠爾的 `title_zh` 是「漢譯對照本的書名」而不是這部經自己的名字，
 *  而且 677 部是空的。標題一律退到藏文題名。 */
const displayTitle = computed(() => {
  const w = work.value
  if (!w) return id.value
  if (w.canon === 'DK') return w.title_bo || w.title_en || w.id
  return w.title_zh || w.id
})
useHead(() => ({ title: `${displayTitle.value} — 佛教大藏經` }))

const divLabel = computed(() => divisionByKey(work.value?.division_key)?.label ?? '佛教大藏經')
const backTo = computed(() => work.value ? `/tripitaka/${work.value.division_key}` : '/tripitaka')


/** 分頁按鈕按函分組。Toh 8 有 12 函 55 段，攤平成一排認不出在哪一函。 */
const pageVols = computed(() => {
  const out: { vol: number; items: any[] }[] = []
  for (const pg of pages.value) {
    const last = out[out.length - 1]
    if (last && last.vol === pg.vol) last.items.push(pg)
    else out.push({ vol: pg.vol, items: [pg] })
  }
  return out
})
const curPage = computed(() => pages.value.find(p => p.key === page.value) ?? null)
const zhParallels = computed<any[]>(() => work.value?.zh_parallels ?? [])

const tocInJuan = computed(() =>
  toc.value.filter(n => juan.value == null || n.juan === juan.value),
)
const prevJuan = computed(() => {
  const i = juans.value.indexOf(juan.value as number)
  return i > 0 ? juans.value[i - 1] : null
})
const nextJuan = computed(() => {
  const i = juans.value.indexOf(juan.value as number)
  return i >= 0 && i < juans.value.length - 1 ? juans.value[i + 1] : null
})

const termsBySeg = computed(() => {
  const m = new Map<string, any[]>()
  for (const t of terms.value) {
    if (!t.uid) continue
    if (!m.has(t.uid)) m.set(t.uid, [])
    m.get(t.uid)!.push(t)
  }
  return m
})
function termsOf(uid: string) { return termsBySeg.value.get(uid) ?? [] }

const parallelsBySeg = computed(() => {
  const m = new Map<string, any[]>()
  for (const p of parallels.value) {
    if (!p.seg_uid) continue
    if (!m.has(p.seg_uid)) m.set(p.seg_uid, [])
    m.get(p.seg_uid)!.push(p)
  }
  // 大正藏原註排最前（權威度最高），本站對齊排最後
  const rank: Record<string, number> = { 'taisho-equiv': 0, suttacentral: 1, 'cbeta-term': 2, site: 3 }
  for (const list of m.values()) list.sort((a, b) => (rank[a.src] ?? 9) - (rank[b.src] ?? 9))
  return m
})
function parallelsOf(uid: string) { return parallelsBySeg.value.get(uid) ?? [] }
function originalsOf(uid: string) { return originals.value[uid] ?? [] }

// ── 多譯本對照（原「異譯對讀」頁，併入閱讀器）────────────────────────────
// 資料是 scripts/tripitaka_compare*.py 產的 public/content/tripitaka/compare/*.json：
// 同一部經的多個漢譯本＋梵／巴／藏原典，按義段（本站編訂，佛典沒有跨語言節號）切好。
// 本頁某些段落若被某一組涵蓋，就在那個位置改以「義段」為一節多欄並排，其餘段落照常。
interface CmpVer { id: string; lang: string; label: string; who?: string; work?: string; reorder?: boolean }
interface CmpSet {
  slug: string; title: string; auto?: boolean; units: { id: string; label: string; doubt?: boolean }[]
  versions: CmpVer[]; works: string[]; anchors?: any[]; cells: Record<string, Record<string, string>>
}
const cmpIndex = ref<any[]>([])
const cmpSets = ref<CmpSet[]>([])

// 目錄節點的首段：本機新格式叫 uid，Drive／R2 舊檔叫 seg（兩種都要認）
const nodeUid = (n: any) => n?.uid ?? n?.seg
const tocByI = computed(() => new Map(toc.value.map((n: any) => [n.i, n])))

async function loadCompare() {
  cmpSets.value = []
  try {
    if (!cmpIndex.value.length) cmpIndex.value = await $fetch<any[]>('/content/tripitaka/compare/index.json')
  } catch { return }
  // 本頁有段落的節點（含祖先）：阿含一部有上百組，只載這一卷碰得到的
  const onPage = new Set<string>()
  for (const d of new Set(segments.value.map((s: any) => s.d))) {
    let n: any = tocByI.value.get(d)
    while (n) { onPage.add(`u:${nodeUid(n)}`); onPage.add(`h:${n.head}`); n = tocByI.value.get(n.parent) }
  }
  const want = cmpIndex.value.filter((c: any) => {
    if (!c.works.includes(id.value)) return false
    const mine = (c.anchors || []).filter((a: any) => a.work === id.value)
    return !mine.length || mine.some((a: any) => onPage.has(a.uid ? `u:${a.uid}` : `h:${a.node}`))
  })
  const got = await Promise.all(want.slice(0, 80).map((c: any) =>
    $fetch<CmpSet>(`/content/tripitaka/compare/${c.slug}.json`).catch(() => null)))
  cmpSets.value = got.filter(Boolean) as CmpSet[]
}

/** 版本屬於哪一部漢文經：新資料有 work；舊資料從 id 前綴推（T0099-sa379 → T0099）。 */
const vWork = (v: CmpVer) => v.work ?? (v.id.match(/^[TX]\d{4}[A-Za-z]?/)?.[0] ?? null)

/** 一組裡的各版本 → 欄位鍵。本經＝self；其他漢譯＝alt1, alt2…；原典按語言（同語言多本加 #2）。 */
function keyMap(set: CmpSet): Map<string, CmpVer> {
  const m = new Map<string, CmpVer>()
  const self = set.versions.find(v => vWork(v) === id.value)
  let alt = 0
  const cnt: Record<string, number> = {}
  for (const v of set.versions) {
    let k: string
    if (v === self) k = 'self'
    else if (/漢譯南傳/.test(v.label) || v.id.startsWith('nan-') || v.id === 'zh-nan') k = 'zh-nan'
    else if (v.lang === 'lzh') k = `alt${++alt}`
    else k = v.lang
    if (k !== 'self' && !k.startsWith('alt')) {
      cnt[k] = (cnt[k] || 0) + 1
      if (cnt[k] > 1) k = `${k}#${cnt[k]}`
    }
    m.set(k, v)
  }
  return m
}

function descendants(roots: number[]): Set<number> {
  const out = new Set<number>(roots)
  let grew = true
  while (grew) {
    grew = false
    for (const n of toc.value) if (!out.has(n.i) && out.has(n.parent)) { out.add(n.i); grew = true }
  }
  return out
}

/** 每一組在本頁涵蓋哪些段：有錨點（阿含的一經、長經的一品）照目錄子樹；整部的就比對文字。 */
const blocks = computed(() => cmpSets.value.map(set => {
  const keys = keyMap(set)
  const self = keys.get('self')
  const covered = new Set<string>()
  const mine = (set.anchors || []).filter((a: any) => a.work === id.value)
  if (mine.length) {
    const roots = toc.value.filter((n: any) => mine.some((a: any) => a.uid ? nodeUid(n) === a.uid : n.head === a.node))
      .map((n: any) => n.i)
    const ids = descendants(roots)
    for (const s of segments.value) if (ids.has(s.d) && s.kind !== 'head' && s.kind !== 'byline') covered.add(s.uid)
  } else if (self) {
    const txt = set.units.map(u => set.cells[u.id]?.[self.id] ?? '').join('')
    for (const s of segments.value) {
      if (s.kind === 'head' || s.kind === 'byline') continue
      const t = String(s.sources?.lzh ?? '').trim()
      if (t.length >= 2 && txt.includes(t)) covered.add(s.uid)
    }
  }
  return { set, keys, covered }
}).filter(b => b.covered.size))

type Row = { type: 'seg'; s: any } | { type: 'unit'; b: any; u: any; k: number; first: boolean }
/** 頁面的一列一列：一般段落一列；被某組涵蓋的段落換成該組的各義段。 */
const rows = computed<Row[]>(() => {
  const out: Row[] = []
  const owner = new Map<string, any>()
  for (const b of blocks.value) for (const u of b.covered) if (!owner.has(u)) owner.set(u, b)
  const done = new Set<any>()
  for (const s of segments.value) {
    const b = owner.get(s.uid)
    if (!b) { out.push({ type: 'seg', s }); continue }
    if (done.has(b)) continue
    done.add(b)
    b.set.units.forEach((u: any, k: number) => out.push({ type: 'unit', b, u, k, first: k === 0 }))
  }
  return out
})

// ── 欄位（聖經對照頁同款：一欄一個下拉，同一語言在下拉裡選版本）──────────
const LANG_NAME: Record<string, string> = { lzh: '漢文', sa: '梵文', pi: '巴利', bo: '藏文', en: '英譯' }
/** 本經自己的語言：漢文藏是 lzh；德格甘珠爾只有 bo */
const selfLang = computed(() => segments.value.some((s: any) => s.sources?.lzh) ? 'lzh'
  : (Object.keys(segments.value[0]?.sources || {})[0] || 'lzh'))
const segLangs = computed(() => {
  const s = new Set<string>()
  for (const seg of segments.value) for (const k of Object.keys(seg.sources || {})) s.add(k)
  return s
})
function langOfKey(k: string) {
  if (k === 'self') return selfLang.value
  if (k.startsWith('alt') || k === 'zh-nan' || k === 'zh-mod') return 'lzh'
  return k.split('#')[0]
}
/** 本頁可選的欄位鍵 → 它在各組裡的實際名稱（只有一種名稱時下拉直接顯示該名） */
const keyNames = computed(() => {
  const m = new Map<string, Set<string>>()
  const add = (k: string, name: string) => { if (!m.has(k)) m.set(k, new Set()); m.get(k)!.add(name) }
  add('self', work.value?.title_zh || work.value?.title_bo || '本經')
  for (const l of segLangs.value) if (l !== selfLang.value) add(l === 'zh-mod' ? 'zh-mod' : l, l === 'zh-mod' ? '白話（本站自譯）' : (PARALLEL_LANGS[l]?.label || l))
  for (const b of blocks.value) for (const [k, v] of b.keys) if (k !== 'self') add(k, v.label)
  return m
})
const KEY_ORDER = (k: string) => {
  const base: Record<string, number> = { self: 0, 'zh-mod': 1, alt: 2, 'zh-nan': 3, sa: 4, pi: 5, bo: 6, en: 7 }
  const head = k.startsWith('alt') ? 'alt' : k.split('#')[0]
  return (base[head] ?? 9) * 100 + (parseInt(k.replace(/\D/g, '') || '0'))
}
const allKeys = computed(() => [...keyNames.value.keys()].sort((a, b) => KEY_ORDER(a) - KEY_ORDER(b)))
const keyGroups = computed(() => {
  const g = new Map<string, string[]>()
  for (const k of allKeys.value) { const l = langOfKey(k); if (!g.has(l)) g.set(l, []); g.get(l)!.push(k) }
  return [...g.entries()].map(([lang, keys]) => ({ lang, keys }))
})
function keyLabel(k: string) {
  const names = [...(keyNames.value.get(k) ?? [])]
  if (names.length === 1) return names[0]
  if (k === 'self') return '本經'
  if (k.startsWith('alt')) return `異譯 ${k.slice(3)}`
  return `${PARALLEL_LANGS[k.split('#')[0]]?.label || k}${k.includes('#') ? ' ' + k.split('#')[1] : ''}（各段不同本）`
}

const columns = ref<string[]>([])
// 預設：本經＋白話＋每種原典語言各一欄，最多四欄。
// 🚨 預設欄不能寫死 'lzh'：甘珠爾只有藏文，寫死會整部經一個字都不顯示而頁面看起來正常。
watch(allKeys, (keys) => {
  const keep = columns.value.filter(k => keys.includes(k))
  if (keep.length) { columns.value = keep; return }
  const pick = ['self', 'zh-mod', 'sa', 'pi', 'bo', 'alt1', 'zh-nan', 'en'].filter(k => keys.includes(k))
  columns.value = pick.slice(0, 4)
}, { immediate: true })
function setColumn(i: number, k: string) { columns.value.splice(i, 1, k) }
function addColumn() {
  const next = allKeys.value.find(k => !columns.value.includes(k))
  if (next) columns.value.push(next)
}
const colGrid = computed(() => `repeat(${Math.max(1, columns.value.length)}, minmax(0, 1fr))`)

function cellText(r: Row, k: string): string {
  if (r.type === 'seg') {
    const l = k === 'self' ? selfLang.value : k
    return k.startsWith('alt') || k.includes('#') ? '' : String(r.s.sources?.[l] ?? '')
  }
  const v = r.b.keys.get(k)
  return v ? String(r.b.set.cells[r.u.id]?.[v.id] ?? '') : ''
}
function cellHtml(r: Row, k: string) {
  if (r.type === 'seg' && k === 'self') return highlight(r.s, selfLang.value)
  return cellText(r, k).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' } as any)[c])
}
function cellClass(r: Row, k: string) {
  const l = langOfKey(k)
  const verse = r.type === 'seg' && r.s.kind === 'verse'
  return [
    verse ? 'whitespace-pre-line' : '',
    l === 'lzh' ? 'text-[16px] tracking-wide' : l === 'bo' ? 'text-[17px]' : 'font-serif text-[15px]',
  ]
}

/** 段首的引用式。漢文是大正藏頁欄行（`…_p0008a13` → `0008a13`）；
 *  甘珠爾是函．葉．行（`DKtoh0113_v51_1b1` → `51.1b1`）——藏學界的定址就是
 *  這個，不要套漢文那一套。 */
function segCite(s: any) {
  const id = String(s.seg ?? '')
  if (id.includes('_p')) return id.replace(/^.*_p/, '')
  const m = id.match(/_v(\d+)_(.+)$/)
  return m ? `${m[1]}.${m[2]}` : id
}

/** 原文的行號標籤。SuttaCentral 是 `sn22.12:1.3`（取冒號後），
 *  GRETIL 是 `MMK 1.1`（原書頌號，整串就是引用式）；抓不到頌號的行留空 ——
 *  寧可沒有標籤，也不要顯示看起來像引用式的自編序號。 */
function segLabel(id: string) {
  if (!id) return ''
  return id.includes(':') ? id.split(':')[1] : id
}

/** 把該段有詞條對照的漢字標底線，讀者一眼看見哪些詞查得到原語。 */
function highlight(s: any, lang: string) {
  const raw = String(s.sources[lang] ?? '')
  const esc = raw.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' } as any)[c])
  if (lang !== 'lzh') return esc
  const words = termsOf(s.uid).map(t => t.zh).filter(w => w && w.length > 1)
  if (!words.length) return esc
  const re = new RegExp(`(${words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'g')
  return esc.replace(re, '<span class="border-b border-dotted border-sky-400">$1</span>')
}

async function copy(text: string) {
  try { await navigator.clipboard.writeText(text) } catch { /* 剪貼簿被擋就算了 */ }
}

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load() {
  pending.value = true
  err.value = null
  try {
    const headers = await authHeaders()
    const r: any = await $fetch('/api/tripitaka/work', {
      headers, query: { id: id.value, juan: route.query.juan || undefined },
    })
    work.value = r.work
    toc.value = r.toc
    segments.value = r.segments
    terms.value = r.terms
    parallels.value = r.parallels ?? []
    originals.value = r.originals ?? {}
    juans.value = r.juans
    juan.value = r.juan
    pages.value = r.pages ?? []
    page.value = r.page ?? null
  } catch (e: any) {
    err.value = e?.data?.message || e?.message || '載入失敗'
  } finally {
    pending.value = false
  }
  await loadCompare()
  await goToHash()
}

/** 網址帶 #段落或經首 uid（例如從多譯本對照目錄點進來）：
 *  目標不在這一卷就換到它所在的卷，再捲過去。 */
async function goToHash() {
  const h = decodeURIComponent((typeof window !== 'undefined' ? window.location.hash : '').slice(1))
  if (!h) return
  await nextTick()
  const el = document.getElementById(h)
  if (el) { el.scrollIntoView({ block: 'start' }); return }
  const n: any = toc.value.find((x: any) => nodeUid(x) === h)
  if (n?.juan && n.juan !== juan.value) await router.replace({ query: { ...route.query, juan: n.juan }, hash: `#${h}` })
}
onMounted(load)
watch(() => [route.params.id, route.query.juan, route.query.page], load)
</script>
