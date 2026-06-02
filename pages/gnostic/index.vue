<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">諾斯底主義文獻</span>
      <span class="text-xs text-gray-400 ml-1">{{ docs.length }} 篇 / {{ CATEGORY_ORDER.length }} 類</span>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🜍 諾斯底主義文獻</h1>
        <p class="text-sm text-gray-500">The Gnostic Society Library (gnosis.org) — 拿戈瑪第經集／古典諾斯底經典／瓦倫廷／赫密士文集／摩尼教／曼達教／卡特里派…；英文（公有領域英譯）／繁中逐段對照</p>
      </div>

      <!-- Search box -->
      <div class="mb-6 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
        <form @submit.prevent="runSearch" class="flex items-center gap-2">
          <span class="text-stone-500 text-lg select-none">🔍</span>
          <input v-model="searchQ" type="text" placeholder="搜尋諾斯底文獻內文（中／英皆可）"
            class="flex-1 text-sm bg-transparent border-none focus:outline-none placeholder:text-gray-300" />
          <select v-model="searchVersion" class="text-xs text-gray-600 bg-transparent border-l border-gray-200 pl-2 cursor-pointer">
            <option value="">全部版本</option>
            <option v-for="v in versions" :key="v.code" :value="v.code">{{ v.name_zh }}</option>
          </select>
          <button type="submit" class="text-xs px-3 py-1 rounded bg-stone-900 text-white hover:bg-stone-700 transition" :disabled="!searchQ || searchQ.length < 2">搜尋</button>
        </form>
      </div>

      <!-- Search results -->
      <div v-if="searchActive" class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-700">搜尋結果
            <span class="text-xs text-gray-400 font-normal">「{{ lastQ }}」 — {{ searchTotal }} 筆{{ searchTotal > searchResults.length ? `（顯示前 ${searchResults.length} 筆）` : '' }}</span>
          </h2>
          <button @click="clearSearch" class="text-xs text-gray-400 hover:text-gray-700 transition">✕ 清除</button>
        </div>
        <div v-if="searchPending" class="text-center text-gray-400 py-8 text-sm">搜尋中…</div>
        <div v-else-if="searchResults.length === 0" class="text-center text-gray-400 py-8 text-sm">沒有符合的段落</div>
        <div v-else class="space-y-1">
          <NuxtLink v-for="(r, i) in searchResults" :key="`${r.doc_slug}-${r.version_code}-${r.order_index}-${i}`"
            :to="`/gnostic/${r.doc_slug}#section-${r.order_index}`"
            class="block bg-white border border-gray-200 rounded px-3 py-2 hover:border-stone-400 hover:shadow-sm transition">
            <div class="flex items-baseline gap-2 text-xs mb-1">
              <span class="font-mono font-semibold text-stone-700">{{ docTitle(r.doc_slug) }} <span class="text-gray-400">#{{ r.order_index }}</span></span>
              <span class="text-gray-400">{{ versionLabel(r.version_code) }}</span>
            </div>
            <div class="text-sm text-gray-800 leading-relaxed" v-html="highlightMatch(snip(r.text, lastQ), lastQ)" />
          </NuxtLink>
        </div>
      </div>

      <!-- Category tabs -->
      <div v-if="!searchActive" class="flex flex-wrap items-center gap-1.5 mb-6 text-xs">
        <button @click="activeCat = 'all'" class="px-3 py-1 rounded-full border transition"
          :class="activeCat === 'all' ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'">全部 <span class="opacity-70">({{ docs.length }})</span></button>
        <button v-for="c in categoryChips" :key="c.key" @click="activeCat = c.key" class="px-3 py-1 rounded-full border transition"
          :class="activeCat === c.key ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'">{{ c.label }} <span class="opacity-70">({{ c.count }})</span></button>
      </div>

      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <div v-else-if="!searchActive">
        <div v-for="group in groupedDocs" :key="group.key" class="mt-2 mb-8">
          <h2 class="text-sm font-semibold text-stone-700 mb-3 border-b border-gray-200 pb-1.5 flex items-baseline gap-2">
            <span>{{ group.label }}</span>
            <span class="text-[10px] text-gray-400 font-normal">{{ group.label_en }}</span>
            <span class="text-xs text-gray-400 font-normal ml-auto">{{ group.items.length }} 篇</span>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <NuxtLink v-for="doc in group.items" :key="doc.slug" :to="`/gnostic/${doc.slug}`"
              class="block bg-white border border-gray-200 rounded-md px-3 py-2.5 hover:border-stone-400 hover:shadow-sm transition"
              :class="doc.total_sections === 0 ? 'opacity-60' : ''">
              <div class="font-semibold text-gray-900 text-sm leading-tight">{{ doc.title_zh }}
                <span v-if="doc.title_zh_short && doc.title_zh_short !== doc.title_zh" class="text-[10px] text-gray-400 ml-1">({{ doc.title_zh_short }})</span>
              </div>
              <div class="text-[11px] text-gray-500 mt-0.5 leading-tight">{{ doc.title_en }}</div>
              <div class="flex items-center gap-2 mt-1.5 text-[10px]">
                <span v-if="doc.section_counts?.zh" class="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700">中 {{ doc.section_counts.zh }}</span>
                <span v-if="doc.section_counts?.gnosis_en" class="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">英 {{ doc.section_counts.gnosis_en }}</span>
                <span v-else class="text-gray-400 italic">未轉錄</span>
                <span v-if="doc.composition_low !== null || doc.composition_high !== null" class="text-gray-400 ml-auto">{{ formatPeriod(doc.composition_low, doc.composition_high) }}</span>
              </div>
            </NuxtLink>
          </div>
        </div>
        <div v-if="docs.length === 0" class="text-center text-gray-400 py-12 text-sm">尚未轉錄任何文獻。用 <code>scripts/ingest_gnostic.py</code> 開始。</div>
      </div>

      <div v-if="!searchActive" class="mt-12 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>來源：The Gnostic Society Library（gnosis.org）。英譯多為 G.R.S. Mead（1900s）等公有領域譯本；繁中為逐段自譯。</p>
        <p class="mt-1">教父駁斥／基督教偽典／死海古卷與 <NuxtLink to="/fathers" class="underline">教父著作</NuxtLink>、<NuxtLink to="/apocrypha" class="underline">典外文獻</NuxtLink> 重疊者不重複收錄。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CATEGORY_ORDER } from '~/lib/gnostic-meta'

definePageMeta({ middleware: 'auth' })
useHead({ title: '諾斯底主義文獻 — Know Graph Lab' })

type GDoc = { slug: string; title_zh: string; title_zh_short: string | null; title_en: string; category: string; composition_low: number | null; composition_high: number | null; section_counts: Record<string, number>; total_sections: number }
type GVersion = { code: string; name_zh: string; name_en: string; category: string }
type SearchHit = { doc_slug: string; version_code: string; order_index: number; text: string }

const supabase = useSupabaseClient()
const docs = ref<GDoc[]>([])
const versions = ref<GVersion[]>([])
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
    const [d, v] = await Promise.all([
      $fetch<GDoc[]>('/api/gnostic/documents', { headers }),
      $fetch<GVersion[]>('/api/gnostic/versions', { headers }),
    ])
    docs.value = d; versions.value = v
  } catch (e: any) { error.value = e?.message || String(e) } finally { pending.value = false }
}
onMounted(load)

const activeCat = ref<string>('all')
const categoryChips = computed(() =>
  CATEGORY_ORDER.map(c => ({ key: c.key, label: c.label, count: docs.value.filter(d => d.category === c.key).length }))
    .filter(c => c.count > 0))
const groupedDocs = computed(() => {
  const cats = activeCat.value === 'all' ? CATEGORY_ORDER : CATEGORY_ORDER.filter(c => c.key === activeCat.value)
  return cats.map(c => ({ ...c, items: docs.value.filter(d => d.category === c.key) })).filter(g => g.items.length > 0)
})

function formatPeriod(low: number | null, high: number | null) {
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
}

// ── Search ───────────────────────────────────────────────────────
const searchQ = ref(''); const searchVersion = ref('')
const searchResults = ref<SearchHit[]>([]); const searchTotal = ref(0)
const searchPending = ref(false); const lastQ = ref('')
const searchActive = computed(() => lastQ.value.length > 0)
async function runSearch() {
  if (!searchQ.value || searchQ.value.length < 2) return
  searchPending.value = true; lastQ.value = searchQ.value
  try {
    const headers = await authHeaders()
    const res = await $fetch<{ q: string; total: number; results: SearchHit[] }>('/api/gnostic/search', { headers, query: { q: searchQ.value, version: searchVersion.value || undefined, limit: 100 } })
    searchResults.value = res.results; searchTotal.value = res.total
  } catch (e: any) { searchResults.value = []; searchTotal.value = 0; error.value = e?.message || String(e) } finally { searchPending.value = false }
}
function clearSearch() { searchQ.value = ''; lastQ.value = ''; searchResults.value = []; searchTotal.value = 0 }
function docTitle(slug: string) { return docs.value.find(x => x.slug === slug)?.title_zh ?? slug }
function versionLabel(code: string) { return versions.value.find(x => x.code === code)?.name_zh ?? code }
function snip(text: string, q: string, win = 140) {
  const idx = text.toLowerCase().indexOf(q.toLowerCase())
  if (idx < 0) return text.slice(0, win * 2)
  return (idx - win > 0 ? '…' : '') + text.slice(Math.max(0, idx - win), Math.min(text.length, idx + q.length + win)) + (idx + q.length + win < text.length ? '…' : '')
}
function highlightMatch(text: string, q: string) {
  if (!q) return text
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(re, '<mark class="bg-yellow-200 text-stone-900 rounded px-0.5">$1</mark>')
}
</script>
