<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="佛教大藏經" :back="{ to: '/scripture-canon/buddhism', label: '佛教' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-10">
      <div class="w-full max-w-5xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">☸️ 佛教大藏經</h1>
          <p class="text-sm text-gray-500">
            《大正新脩大藏經》與《漢譯南傳大藏經》全文，附梵／巴／藏原典對照
          </p>
          <div v-if="!pending" class="mt-4 flex flex-wrap justify-center gap-x-6 gap-y-1 text-xs text-gray-400">
            <span>{{ fmt(total.works) }} 部</span>
            <span>{{ fmt(total.chars) }} 字</span>
            <span>{{ fmt(total.segs) }} 段</span>
            <span>{{ fmt(total.parallel) }} 部有原文對照</span>
          </div>
        </div>

        <div class="mb-5 flex gap-2">
          <input
            v-model="q"
            type="search"
            placeholder="搜尋經名、譯者或經號（法華 / 鳩摩羅什 / T0262）"
            class="flex-1 px-4 py-2.5 text-sm border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300"
            @keyup.enter="runSearch"
          />
          <button
            class="px-4 py-2.5 text-sm rounded-xl bg-amber-600 text-white hover:bg-amber-700 transition"
            @click="runSearch"
          >搜尋</button>
        </div>

        <!-- 搜尋結果 -->
        <div v-if="hits !== null" class="mb-8 bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
            <span class="text-sm text-gray-600">找到 {{ fmt(hitTotal) }} 部</span>
            <button class="text-xs text-gray-400 hover:text-gray-700" @click="hits = null; q = ''">清除</button>
          </div>
          <p v-if="!hits.length" class="px-5 py-6 text-sm text-gray-400">沒有符合的經。</p>
          <ul v-else class="divide-y divide-gray-50 max-h-[26rem] overflow-y-auto">
            <li v-for="w in hits" :key="w.id">
              <NuxtLink :to="`/tripitaka/w/${w.id}`" class="flex items-baseline gap-3 px-5 py-2.5 hover:bg-amber-50/50 transition">
                <span class="font-mono text-[11px] text-gray-400 w-20 flex-shrink-0">{{ w.id }}</span>
                <span class="text-sm text-gray-800 truncate">{{ w.title_zh }}</span>
                <span class="text-xs text-gray-400 ml-auto flex-shrink-0 truncate max-w-[10rem]">{{ w.byline }}</span>
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- 部類 -->
        <template v-for="group in groups" :key="group.title">
          <div class="mb-3 mt-8 first:mt-0">
            <h2 class="text-sm font-semibold text-gray-700">{{ group.title }}</h2>
            <p class="text-xs text-gray-400 mt-0.5">{{ group.desc }}</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <NuxtLink
              v-for="d in group.divisions"
              :key="d.key"
              :to="`/tripitaka/${d.key}`"
              class="group relative bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition overflow-hidden"
              :class="COLOR_CLASS[d.color]?.hover"
            >
              <div class="absolute left-0 top-0 bottom-0 w-1" :class="COLOR_CLASS[d.color]?.bar" />
              <div class="pl-2">
                <div class="flex items-baseline gap-2">
                  <span class="font-semibold text-gray-900 text-sm">{{ d.label }}</span>
                  <span class="text-[10px] text-gray-400 font-mono">{{ d.vols }}</span>
                </div>
                <div v-if="d.label_alt" class="text-[11px] text-gray-400 italic mt-0.5">{{ d.label_alt }}</div>
                <p class="text-xs text-gray-500 mt-1.5 leading-relaxed line-clamp-2">{{ d.desc }}</p>
                <div class="mt-2.5 flex items-center gap-2 text-[11px] text-gray-400">
                  <span>{{ stat(d.key).works }} 部</span>
                  <span v-if="stat(d.key).chars">· {{ fmt(stat(d.key).chars) }} 字</span>
                  <span
                    v-if="stat(d.key).with_parallel"
                    class="ml-auto px-1.5 py-0.5 rounded border text-[10px]"
                    :class="COLOR_CLASS[d.color]?.chip"
                  >{{ stat(d.key).with_parallel }} 部有原文</span>
                </div>
              </div>
            </NuxtLink>
          </div>
        </template>

        <!-- 凡例 -->
        <div class="mt-12 bg-white border border-gray-200 rounded-2xl p-6 text-xs text-gray-500 leading-relaxed space-y-2">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">凡例</h3>
          <p>
            <strong class="text-gray-700">段的編號。</strong>
            漢文佛典沒有聖經那樣的章節制。本站以<strong class="text-gray-700">大正藏頁欄行</strong>為段的識別碼與引用式（<code class="font-mono">T09n0262_p0008a13</code> ＝ 大正藏第 9 冊第 262 經第 8 頁 a 欄第 13 行），不另編號。段的<em>邊界</em>取自 CBETA 新式標點本的分段，屬編輯判斷，非原典自帶。
          </p>
          <p>
            <strong class="text-gray-700">對照的層級。</strong>
            卷與品（梵 parivarta／藏 le'u）是跨語言唯一可靠的對齊層。品以下，阿含類可對到「經」、論頌類可對到「頌」、律部可對到「條」；其餘大乘經在品以下並無學界通行的切分共識。
          </p>
          <p>
            <strong class="text-gray-700">對照的來源分三級</strong>，UI 分色標示，不混為一談：<span class="text-emerald-700">大正藏原註</span>（1924–34 年編者所加的巴利對應）、<span class="text-sky-700">CBETA 詞條</span>（專名旁的梵巴原語形）、<span class="text-amber-700">本站對齊</span>（無現成資料時自行切分，屬編輯判斷）。
          </p>
          <p>
            <strong class="text-gray-700">存世的實情。</strong>
            大正藏兩千餘部中，梵本存世不到一成，巴利對應集中於四阿含，藏譯對應主要在般若、密教與論部。沒有對照欄不代表本站漏做，而是該經的原典已佚。
          </p>
          <p>
            <strong class="text-gray-700">未收部分。</strong>
            大正藏第 56–84 冊（日本撰述部）CBETA 未提供 XML，故續經疏部、續諸宗部、悉曇部等不在此處。
          </p>
          <p class="pt-1 text-gray-400">
            文本來源：中華電子佛典協會（CBETA）TEI P5 XML，非商業用途。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  TAISHO_TRANSLATED, TAISHO_CHINESE, NANCHUAN, XUZANG, COLOR_CLASS,
} from '~/data/tripitaka/divisions'

definePageMeta({ middleware: 'auth' })
useHead({ title: '佛教大藏經 — Know Graph Lab' })

const groups = [
  { title: '大正藏 · 漢譯經律論', desc: '自印度傳入、譯成漢文的經律論本體（T01–T32）', divisions: TAISHO_TRANSLATED },
  { title: '大正藏 · 中土撰述', desc: '漢地祖師的注疏、宗論、史傳與經錄（T33–T55、T85）', divisions: TAISHO_CHINESE },
  { title: '卍新纂續藏經 · 中土撰述補遺', desc: '大正藏略掉的那一半：宋元明清的疏鈔、各宗語錄、禮懺儀軌與寺志僧傳（X01–X88）', divisions: XUZANG },
  { title: '漢譯南傳大藏經 · 元亨寺版', desc: '巴利三藏的完整現代漢譯，與上列漢譯阿含互為對照（N01–N70）', divisions: NANCHUAN },
]

const supabase = useSupabaseClient()
const pending = ref(true)
const stats = ref<Record<string, { works: number; chars: number; segs: number; with_parallel: number }>>({})
const q = ref('')
const hits = ref<any[] | null>(null)
const hitTotal = ref(0)

const total = computed(() => {
  const vals = Object.values(stats.value)
  return {
    works: vals.reduce((a, b) => a + b.works, 0),
    chars: vals.reduce((a, b) => a + b.chars, 0),
    segs: vals.reduce((a, b) => a + b.segs, 0),
    parallel: vals.reduce((a, b) => a + b.with_parallel, 0),
  }
})

function stat(key: string) {
  return stats.value[key] ?? { works: 0, chars: 0, segs: 0, with_parallel: 0 }
}
function fmt(n: number) {
  return (n ?? 0).toLocaleString('en-US')
}

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function runSearch() {
  const term = q.value.trim()
  if (!term) { hits.value = null; return }
  const headers = await authHeaders()
  const r: any = await $fetch('/api/tripitaka/works', { headers, query: { q: term, limit: 200 } })
  hits.value = r.works
  hitTotal.value = r.total
}

onMounted(async () => {
  try {
    const headers = await authHeaders()
    const r: any = await $fetch('/api/tripitaka/stats', { headers })
    for (const d of r.divisions) stats.value[d.division_key] = d
  } finally {
    pending.value = false
  }
})
</script>
