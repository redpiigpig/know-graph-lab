<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="全集" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" :editable="false" />

    <div class="max-w-5xl mx-auto px-6 py-12">
      <!-- hero -->
      <div class="text-center mb-12">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">經典學者全集</h1>
        <p class="text-sm text-gray-500 max-w-2xl mx-auto leading-relaxed">
          依學科收錄哲學、宗教學、神學、佛學、心理學等領域奠基學者的全集，每位學者一份學術小傳、生平年表與按年編排的完整著作目錄；
          各部著作以原文‧（譯本）‧繁中多欄逐段對照閱讀。
        </p>
        <NuxtLink to="/transcription-progress"
          class="inline-flex items-center gap-1.5 mt-4 text-xs text-blue-600 hover:underline">
          🛰 轉錄與翻譯進度
        </NuxtLink>
      </div>

      <!-- 依學科分組 -->
      <div v-for="grp in grouped" :key="grp.discipline" class="mb-12 last:mb-0">
        <h2 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <span class="inline-block w-1.5 h-4 rounded-full bg-gray-300"></span>
          {{ grp.discipline }}
          <span class="text-xs font-normal text-gray-400">（{{ grp.total }} 位）</span>
        </h2>

        <!-- 年代→地域小組（單層學科則只有一個無標題 section）-->
        <div v-for="sec in grp.sections" :key="sec.key" :class="sec.era ? 'mb-6 last:mb-0' : ''">
          <!-- 年代大標（每個年代區塊只印一次）-->
          <h3
            v-if="sec.showEra"
            class="text-xs font-bold text-gray-500 mb-3 mt-2 flex items-center gap-2 uppercase tracking-wide"
          >
            <span class="inline-block w-1 h-3 rounded-full bg-gray-400"></span>{{ sec.era }}
          </h3>
          <!-- 地域小標 -->
          <p v-if="sec.region" class="text-[11px] text-gray-400 mb-2 ml-3 font-medium">{{ sec.region }}</p>

          <!-- 作家卡片 -->
          <div class="grid gap-5 sm:grid-cols-2" :class="sec.region ? 'ml-3' : ''">
            <NuxtLink
              v-for="a in sec.authors"
              :key="a.slug"
              :to="`/collected-works/${a.slug}`"
              class="author-card no-underline"
              :class="`border-${a.color}-100 hover:border-${a.color}-300 hover:shadow-${a.color}-100`"
            >
              <img
                v-if="a.portraitUrl"
                :src="a.portraitUrl"
                :alt="a.name"
                class="w-20 h-20 rounded-xl object-cover object-top flex-shrink-0 bg-gray-100 ring-1 ring-gray-200"
                loading="lazy"
              />
              <div
                v-else
                class="w-20 h-20 rounded-xl flex-shrink-0 bg-gray-100 ring-1 ring-gray-200 flex items-center justify-center text-3xl"
              >{{ a.emoji }}</div>
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <h3 class="text-base font-bold text-gray-900">{{ a.name }}</h3>
                  <span class="text-xs text-gray-400 font-mono">{{ a.lifespan }}</span>
                </div>
                <p v-if="a.nameEn" class="text-xs text-gray-400 italic mb-1">{{ a.nameEn }}</p>
                <p class="text-xs text-gray-600 leading-relaxed line-clamp-2">{{ a.discipline }}</p>
                <div class="mt-2 flex items-center gap-1.5 flex-wrap">
                  <span
                    v-for="f in a.fields.slice(0, 4)"
                    :key="f"
                    class="text-[11px] px-1.5 py-0.5 rounded-full"
                    :class="`bg-${a.color}-50 text-${a.color}-700`"
                  >{{ f }}</span>
                </div>
                <div class="mt-2 text-[11px] text-gray-400">
                  {{ progress(a).done }}／{{ progress(a).total }} 卷已轉錄
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>

      <p class="mt-12 text-center text-xs text-gray-400">
        全集原檔多取自公有領域來源；繁體中譯與多欄對照為本站自製。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CwAuthor } from '~/stores/collectedWorks'

definePageMeta({ middleware: 'auth' })
useHead({ title: '全集 — Know Graph Lab' })

const store = useCollectedWorksStore()

// 學科顯示順序；未列出的學科接在最後（按字母序），空組不顯示。
const DISCIPLINE_ORDER = ['哲學', '社會學', '宗教學', '神學', '佛學', '心理學', '人類學']

// 依 sortYear（生年，BCE 為負）排序；缺者維持插入序、排在有值者之後
function byYear(list: CwAuthor[]) {
  return list
    .map((a, i) => ({ a, i }))
    .sort((x, y) => (x.a.sortYear ?? Infinity) - (y.a.sortYear ?? Infinity) || x.i - y.i)
    .map((o) => o.a)
}
// 一組作家中最早的生年（用來把年代／地域小組依時序排列）
function minYear(list: CwAuthor[]) {
  return Math.min(...list.map((a) => a.sortYear ?? Infinity))
}
// 依某鍵分組，回傳「依組內最早生年排序」的 [鍵, 作家[]] 陣列
function groupSorted(list: CwAuthor[], keyOf: (a: CwAuthor) => string) {
  const m = new Map<string, CwAuthor[]>()
  for (const a of list) {
    const k = keyOf(a)
    if (!m.has(k)) m.set(k, [])
    m.get(k)!.push(a)
  }
  return [...m.entries()].sort((x, y) => minYear(x[1]) - minYear(y[1]))
}

interface CwSection {
  key: string
  showEra: boolean // 該年代區塊的第一個地域小組才印年代大標
  era: string
  region: string
  authors: CwAuthor[]
}

const grouped = computed(() => {
  const map = new Map<string, CwAuthor[]>()
  for (const a of store.authors) {
    const key = a.disciplineGroup || '其他'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(a)
  }
  const keys = [...map.keys()].sort((x, y) => {
    const ix = DISCIPLINE_ORDER.indexOf(x)
    const iy = DISCIPLINE_ORDER.indexOf(y)
    if (ix === -1 && iy === -1) return x.localeCompare(y)
    if (ix === -1) return 1
    if (iy === -1) return -1
    return ix - iy
  })
  return keys.map((discipline) => {
    const list = map.get(discipline)!
    const hasEra = list.some((a) => a.era)
    const sections: CwSection[] = []
    if (!hasEra) {
      // 單層：整個學科依生年排一個 grid
      sections.push({ key: discipline, showEra: false, era: '', region: '', authors: byYear(list) })
    } else {
      // 兩層：先分年代（依組內最早生年），年代內再分地域
      for (const [era, eraList] of groupSorted(list, (a) => a.era || '其他')) {
        let first = true
        for (const [region, regionList] of groupSorted(eraList, (a) => a.region || '其他')) {
          sections.push({ key: `${era}|${region}`, showEra: first, era, region, authors: byYear(regionList) })
          first = false
        }
      }
    }
    return { discipline, total: list.length, sections }
  })
})

function progress(a: CwAuthor) {
  return {
    done: a.works.filter((w) => w.status === 'done').length,
    total: a.works.length,
  }
}
</script>

<style scoped>
.author-card {
  @apply flex items-start gap-4 p-5 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer;
}
</style>

<!-- Dynamic Tailwind colors (bg-${color}-*, text-${color}-*, border-${color}-*) are safelisted in tailwind.config.ts -->
