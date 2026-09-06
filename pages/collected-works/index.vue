<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="全集" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" :editable="false" />

    <div class="max-w-5xl mx-auto px-6 pt-12 pb-4">
      <!-- hero -->
      <div class="text-center mb-8">
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
    </div>

    <!-- 三層篩選：學科分頁 → 年代 → 地域。捲動時黏在頂端，才不必為了換學科捲回最上面 -->
    <div class="sticky top-0 z-20 bg-slate-50/95 backdrop-blur border-b border-slate-200">
      <div class="max-w-5xl mx-auto px-6 py-3">
        <!-- 第一層：學科 -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="t in disciplineTabs"
            :key="t.key"
            @click="selectDiscipline(t.key)"
            class="px-3 py-1.5 rounded-lg text-sm transition border"
            :class="t.key === activeDiscipline
              ? 'bg-gray-900 text-white border-gray-900 font-medium'
              : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'"
          >
            {{ t.key }}
            <span class="ml-1 text-xs" :class="t.key === activeDiscipline ? 'text-gray-300' : 'text-gray-400'">{{ t.count }}</span>
          </button>
        </div>

        <!-- 第二層：年代（只有該學科真的分年代時才出現） -->
        <div v-if="eraChips.length > 1" class="flex flex-wrap items-center gap-1.5 mt-2">
          <span class="text-[11px] text-gray-400 w-8 shrink-0">年代</span>
          <button
            v-for="c in eraChips"
            :key="c.key"
            @click="selectEra(c.key)"
            class="px-2.5 py-1 rounded-full text-xs transition border"
            :class="c.key === activeEra
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'"
          >{{ c.label }} <span class="opacity-60">{{ c.count }}</span></button>
        </div>

        <!-- 第三層：地域 -->
        <div v-if="regionChips.length > 1" class="flex flex-wrap items-center gap-1.5 mt-2">
          <span class="text-[11px] text-gray-400 w-8 shrink-0">地域</span>
          <button
            v-for="c in regionChips"
            :key="c.key"
            @click="activeRegion = c.key"
            class="px-2.5 py-1 rounded-full text-xs transition border"
            :class="c.key === activeRegion
              ? 'bg-emerald-600 text-white border-emerald-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-300'"
          >{{ c.label }} <span class="opacity-60">{{ c.count }}</span></button>
        </div>
      </div>
    </div>

    <div class="max-w-5xl mx-auto px-6 py-8">
      <p class="text-xs text-gray-400 mb-6">
        共 {{ visibleCount }} 位學者<span v-if="activeDiscipline !== ALL">（{{ activeDiscipline }}）</span>
      </p>

      <div v-for="grp in visibleGroups" :key="grp.discipline" class="mb-12 last:mb-0">
        <!-- 選定單一學科時不必再印學科大標（分頁列已經顯示） -->
        <h2 v-if="activeDiscipline === ALL" class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <span class="inline-block w-1.5 h-4 rounded-full bg-gray-300"></span>
          {{ grp.discipline }}
          <span class="text-xs font-normal text-gray-400">（{{ grp.total }} 位）</span>
        </h2>

        <div v-for="sec in grp.sections" :key="sec.key" :class="sec.era ? 'mb-6 last:mb-0' : ''">
          <h3
            v-if="sec.showEra && sec.era"
            class="text-xs font-bold text-gray-500 mb-3 mt-2 flex items-center gap-2 uppercase tracking-wide"
          >
            <span class="inline-block w-1 h-3 rounded-full bg-gray-400"></span>{{ sec.era }}
          </h3>
          <p v-if="sec.region" class="text-[11px] text-gray-400 mb-2 ml-3 font-medium">{{ sec.region }}</p>

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

      <p v-if="!visibleCount" class="text-center text-sm text-gray-400 py-12">這個篩選下沒有學者。</p>

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
const DISCIPLINE_ORDER = ['哲學', '宗教學', '宗教社會學', '神學', '基督宗教研究', '佛學', '心理學', '社會學', '人類學']
// 某些傘狀學科的次領域（era 層）要固定順序，不依生年（如基督宗教研究：新約→舊約→教會史）
const ERA_ORDER: Record<string, string[]> = {
  基督宗教研究: ['新約研究', '舊約研究', '教會史'],
}

const ALL = '全部'
const ANY = ''  // 晶片的「全」＝不篩

// ── 三層篩選狀態 ──
const activeDiscipline = ref(ALL)
const activeEra = ref(ANY)
const activeRegion = ref(ANY)

function selectDiscipline(k: string) {
  activeDiscipline.value = k
  activeEra.value = ANY      // 換學科時下兩層要歸零，否則會篩出空清單
  activeRegion.value = ANY
}
function selectEra(k: string) {
  activeEra.value = k
  activeRegion.value = ANY   // 地域是年代的下一層
}

// ── 排序與分組 helpers ──
function byYear(list: CwAuthor[]) {
  return list
    .map((a, i) => ({ a, i }))
    .sort((x, y) => (x.a.sortYear ?? Infinity) - (y.a.sortYear ?? Infinity) || x.i - y.i)
    .map((o) => o.a)
}
function minYear(list: CwAuthor[]) {
  return Math.min(...list.map((a) => a.sortYear ?? Infinity))
}
function groupSorted(list: CwAuthor[], keyOf: (a: CwAuthor) => string) {
  const m = new Map<string, CwAuthor[]>()
  for (const a of list) {
    const k = keyOf(a)
    if (!m.has(k)) m.set(k, [])
    m.get(k)!.push(a)
  }
  return [...m.entries()].sort((x, y) => minYear(x[1]) - minYear(y[1]))
}
function disciplineRank(x: string) {
  const i = DISCIPLINE_ORDER.indexOf(x)
  return i === -1 ? DISCIPLINE_ORDER.length : i
}

interface CwSection {
  key: string
  showEra: boolean // 該年代區塊的第一個地域小組才印年代大標
  era: string
  region: string
  authors: CwAuthor[]
}

/** 學科 → 作家（依 DISCIPLINE_ORDER 排序）。分頁列與分組都吃這一份。 */
const byDiscipline = computed(() => {
  const m = new Map<string, CwAuthor[]>()
  for (const a of store.authors) {
    const k = a.disciplineGroup || '其他'
    if (!m.has(k)) m.set(k, [])
    m.get(k)!.push(a)
  }
  return [...m.entries()].sort(
    (x, y) => disciplineRank(x[0]) - disciplineRank(y[0]) || x[0].localeCompare(y[0]),
  )
})

const disciplineTabs = computed(() => [
  { key: ALL, count: store.authors.length },
  ...byDiscipline.value.map(([k, v]) => ({ key: k, count: v.length })),
])

/** 目前學科底下的作家（未套年代／地域篩選）。 */
const inDiscipline = computed<CwAuthor[]>(() =>
  activeDiscipline.value === ALL
    ? store.authors
    : (byDiscipline.value.find(([k]) => k === activeDiscipline.value)?.[1] ?? []),
)

/** 第二層晶片：年代。只在選定單一學科時才有意義（全部視圖已按學科分區）。 */
const eraChips = computed(() => {
  if (activeDiscipline.value === ALL) return []
  const counts = new Map<string, number>()
  for (const a of inDiscipline.value) {
    const k = a.era || ''
    if (!k) continue
    counts.set(k, (counts.get(k) ?? 0) + 1)
  }
  if (!counts.size) return []
  let keys = [...counts.keys()]
  const order = ERA_ORDER[activeDiscipline.value]
  if (order) {
    keys.sort((x, y) => (order.indexOf(x) < 0 ? 99 : order.indexOf(x)) - (order.indexOf(y) < 0 ? 99 : order.indexOf(y)))
  } else {
    const first = new Map<string, number>()
    for (const a of inDiscipline.value) {
      const k = a.era || ''
      if (!k) continue
      first.set(k, Math.min(first.get(k) ?? Infinity, a.sortYear ?? Infinity))
    }
    keys.sort((x, y) => (first.get(x) ?? Infinity) - (first.get(y) ?? Infinity))
  }
  return [
    { key: ANY, label: '全', count: inDiscipline.value.length },
    ...keys.map((k) => ({ key: k, label: k, count: counts.get(k)! })),
  ]
})

/** 第三層晶片：地域。跟著年代選擇一起收窄。 */
const regionChips = computed(() => {
  if (activeDiscipline.value === ALL) return []
  const pool = activeEra.value ? inDiscipline.value.filter((a) => a.era === activeEra.value) : inDiscipline.value
  const counts = new Map<string, number>()
  for (const a of pool) {
    const k = a.region || ''
    if (!k) continue
    counts.set(k, (counts.get(k) ?? 0) + 1)
  }
  if (!counts.size) return []
  const first = new Map<string, number>()
  for (const a of pool) {
    const k = a.region || ''
    if (!k) continue
    first.set(k, Math.min(first.get(k) ?? Infinity, a.sortYear ?? Infinity))
  }
  const keys = [...counts.keys()].sort((x, y) => (first.get(x) ?? Infinity) - (first.get(y) ?? Infinity))
  return [
    { key: ANY, label: '全', count: pool.length },
    ...keys.map((k) => ({ key: k, label: k, count: counts.get(k)! })),
  ]
})

/** 一個學科的作家 → 年代／地域小節（沿用原本「年代大標印一次、地域小標縮排」的版面）。 */
function sectionsFor(discipline: string, list: CwAuthor[]): CwSection[] {
  const hasEra = list.some((a) => a.era)
  if (!hasEra) {
    return [{ key: discipline, showEra: false, era: '', region: '', authors: byYear(list) }]
  }
  let eraEntries = groupSorted(list, (a) => a.era || '其他')
  const eraOrder = ERA_ORDER[discipline]
  if (eraOrder)
    eraEntries = eraEntries.sort(
      (x, y) =>
        (eraOrder.indexOf(x[0]) < 0 ? 99 : eraOrder.indexOf(x[0])) -
        (eraOrder.indexOf(y[0]) < 0 ? 99 : eraOrder.indexOf(y[0])),
    )
  const sections: CwSection[] = []
  for (const [era, eraList] of eraEntries) {
    let first = true
    for (const [region, regionList] of groupSorted(eraList, (a) => a.region || '其他')) {
      const regionLabel = region === '其他' ? '' : region
      sections.push({
        key: `${era}|${region}`,
        // 年代已由晶片選定時不必再印年代大標
        showEra: first && !activeEra.value,
        era,
        region: regionLabel,
        authors: byYear(regionList),
      })
      first = false
    }
  }
  return sections
}

const visibleGroups = computed(() => {
  if (activeDiscipline.value === ALL) {
    return byDiscipline.value.map(([discipline, list]) => ({
      discipline,
      total: list.length,
      sections: sectionsFor(discipline, list),
    }))
  }
  let list = inDiscipline.value
  if (activeEra.value) list = list.filter((a) => a.era === activeEra.value)
  if (activeRegion.value) list = list.filter((a) => a.region === activeRegion.value)
  return [{ discipline: activeDiscipline.value, total: list.length, sections: sectionsFor(activeDiscipline.value, list) }]
})

const visibleCount = computed(() =>
  visibleGroups.value.reduce((n, g) => n + g.sections.reduce((m, s) => m + s.authors.length, 0), 0),
)

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
