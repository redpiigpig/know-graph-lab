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
        <!-- 只有漢文時不必顯示語言切換（原文是可展開區塊，不佔欄） -->
        <div v-if="availableLangs.length > 1" class="flex items-center gap-1.5">
          <button
            v-for="l in availableLangs"
            :key="l"
            class="px-2.5 py-1 text-[11px] rounded-lg border transition"
            :class="shown.has(l)
              ? 'bg-amber-600 text-white border-amber-600'
              : 'bg-white text-gray-500 border-gray-200 hover:border-amber-300'"
            :title="PARALLEL_LANGS[l]?.label || l"
            @click="toggle(l)"
          >{{ PARALLEL_LANGS[l]?.short || l }}</button>
        </div>
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
            :href="`#${n.uid}`"
            class="block py-1 text-xs text-gray-600 hover:text-amber-700 truncate"
            :style="{ paddingLeft: `${n.depth * 10}px` }"
            :title="n.head"
          >{{ n.head }}</a>
        </nav>
      </aside>

      <!-- 正文 -->
      <main class="flex-1 min-w-0 px-6 py-8">
        <div class="max-w-4xl mx-auto">
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

          <div class="space-y-5">
            <div v-for="s in segments" :id="s.uid" :key="s.uid" class="group scroll-mt-20">
              <!-- 段首：大正藏行號（可引用、可複製） -->
              <button
                class="font-mono text-[10px] text-gray-300 group-hover:text-amber-600 transition mb-0.5"
                :title="`複製引用式 ${s.seg}`"
                @click="copy(s.seg)"
              >{{ segCite(s) }}</button>

              <div v-if="s.kind === 'head'" class="text-base font-semibold text-gray-800 pt-2">
                {{ s.sources.lzh }}
              </div>
              <div v-else-if="s.kind === 'byline'" class="text-xs text-gray-400">
                {{ s.sources.lzh }}
              </div>

              <!-- 逐段對照：每一語言一欄 -->
              <div v-else :class="cols.length > 1 ? 'grid gap-4' : ''" :style="gridStyle">
                <div v-for="l in cols" :key="l">
                  <div
                    v-if="cols.length > 1"
                    class="text-[10px] text-gray-400 mb-1 uppercase tracking-wide"
                  >{{ PARALLEL_LANGS[l]?.short || l }}</div>
                  <p
                    v-if="s.sources[l]"
                    class="leading-loose text-gray-800"
                    :class="[
                      s.kind === 'verse' ? 'whitespace-pre-line pl-6 text-[15px]' : 'text-[15px]',
                      l === 'lzh' || l.startsWith('zh') ? 'tracking-wide' : 'font-serif text-[14px]',
                    ]"
                    v-html="highlight(s, l)"
                  />
                  <p v-else class="text-xs text-gray-300 italic">（無對應）</p>
                </div>
              </div>

              <!-- 該段的平行經目：巴／梵／藏／中期印度語 -->
              <div v-if="parallelsOf(s.uid).length" class="mt-2 flex flex-wrap items-center gap-1.5">
                <span class="text-[10px] text-gray-400">原文對應</span>
                <span
                  v-for="(p, pi) in parallelsOf(s.uid)"
                  :key="pi"
                  class="px-1.5 py-0.5 rounded border text-[11px]"
                  :class="[
                    PARALLEL_SOURCES[p.src]?.cls || 'bg-gray-50 text-gray-600 border-gray-200',
                    p.note === '部分平行' ? 'opacity-70' : '',
                  ]"
                  :title="`${PARALLEL_SOURCES[p.src]?.label || p.src}：${PARALLEL_SOURCES[p.src]?.desc || ''}${p.note ? '（' + p.note + '）' : ''}`"
                >
                  <span class="font-medium">{{ PARALLEL_LANGS[p.lang]?.short || p.lang }}</span>
                  {{ p.ref }}<span v-if="p.note === '部分平行'"> ～</span>
                </span>
              </div>

              <!-- 該段對應的原典全文（巴／梵／藏）。
                   刻意做成可展開，而非左右並排：原文那一側是「一整部經」，
                   漢文這一側只是該經的起首段。並排會讓人誤以為逐句對得上。 -->
              <details
                v-for="(o, oi) in originalsOf(s.uid)"
                :key="`o${oi}`"
                class="mt-2 rounded-lg border border-indigo-200 bg-indigo-50/40 overflow-hidden"
              >
                <summary class="px-3 py-1.5 text-[11px] text-indigo-800 cursor-pointer hover:bg-indigo-50 flex items-center gap-2">
                  <span class="font-medium">{{ PARALLEL_LANGS[o.lang]?.label || o.lang }}原文</span>
                  <span class="text-indigo-600">{{ o.ref }}</span>
                  <span class="text-indigo-400">{{ o.lines.length }} 段</span>
                  <span v-if="o.partial" class="text-amber-700">部分平行</span>
                </summary>
                <div class="px-3 py-2 border-t border-indigo-100 bg-white/60 max-h-96 overflow-y-auto">
                  <p class="text-[10px] text-gray-400 mb-2 leading-relaxed">
                    以下為{{ PARALLEL_LANGS[o.lang]?.label || o.lang }}該經全文，段號為該語言自身的引用座標；
                    與左側漢文為<strong>同源異流的兩個本子</strong>，段落並非一一對應。
                  </p>
                  <div
                    v-for="(ln, li) in o.lines"
                    :key="li"
                    class="flex gap-2 py-0.5 text-[13px]"
                  >
                    <span class="font-mono text-[9px] text-gray-300 w-20 flex-shrink-0 pt-1">{{ segLabel(ln[0]) }}</span>
                    <span class="font-serif text-gray-700 leading-relaxed">{{ ln[1] }}</span>
                  </div>
                </div>
              </details>

              <!-- 該段的漢梵巴詞條 -->
              <div v-if="termsOf(s.uid).length" class="mt-1.5 flex flex-wrap gap-1.5">
                <span
                  v-for="(t, ti) in termsOf(s.uid)"
                  :key="ti"
                  class="px-1.5 py-0.5 rounded border border-sky-200 bg-sky-50 text-[11px] text-sky-800"
                  title="CBETA 詞條對照"
                >
                  {{ t.zh }}
                  <span class="text-sky-600 font-serif">
                    {{ Object.entries(t.forms).map(([k, v]) => `${k === 'sa' ? '梵' : k === 'pi' ? '巴' : k}: ${v}`).join('　') }}
                  </span>
                </span>
              </div>

              <!-- 校勘註 -->
              <details v-if="s.notes?.length" class="mt-1">
                <summary class="text-[11px] text-gray-400 cursor-pointer hover:text-gray-600">
                  校勘 {{ s.notes.length }} 條
                </summary>
                <ul class="mt-1 pl-4 text-[11px] text-gray-500 space-y-0.5">
                  <li v-for="(n, ni) in s.notes" :key="ni">{{ n.text }}</li>
                </ul>
              </details>
            </div>
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

// 漢文永遠在最左；其餘語言按實際有資料的出現
const availableLangs = computed(() => {
  const s = new Set<string>()
  for (const seg of segments.value) for (const k of Object.keys(seg.sources || {})) s.add(k)
  const order = ['lzh', 'zh-nan', 'zh-mod', 'pi', 'sa', 'bo', 'en']
  return order.filter(l => s.has(l))
})
const shown = ref<Set<string>>(new Set(['lzh']))
// 有白話就預設打開 —— 文言與白話並排正是這一欄存在的理由，
// 不該讓使用者自己去點才看得到。
//
// 🚨 預設欄不能寫死 'lzh'。甘珠爾只有 bo 一欄，硬寫 lzh 會讓 cols 算出空陣列，
//    於是整部經一個字都不顯示——而且頁面框架、段號、側欄全都正常出得來，
//    看起來像「這部經是空的」而不是「欄位選錯了」。
watch(availableLangs, (langs) => {
  const next = new Set([...shown.value].filter(l => langs.includes(l)))
  if (langs.includes('zh-mod')) next.add('zh-mod')
  if (!next.size && langs.length) next.add(langs[0])
  shown.value = next
}, { immediate: true })
const cols = computed(() => availableLangs.value.filter(l => shown.value.has(l)))
const gridStyle = computed(() =>
  cols.value.length > 1 ? { gridTemplateColumns: `repeat(${cols.value.length}, minmax(0, 1fr))` } : {},
)
function toggle(l: string) {
  const next = new Set(shown.value)
  if (next.has(l) && next.size > 1) next.delete(l)
  else next.add(l)
  shown.value = next
}

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
}
onMounted(load)
watch(() => [route.params.id, route.query.juan, route.query.page], load)
</script>
