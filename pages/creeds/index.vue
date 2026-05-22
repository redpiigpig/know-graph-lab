<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">信條對照</span>
      <span class="text-xs text-gray-400 ml-1">{{ ALL_CREEDS.length }} 份</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">⛪ 信條對照</h1>
        <p class="text-sm text-gray-500">三區：信經 ／ 歷代大公會議文獻 ／ 各宗派信條與要理問答 — 多語言版本平行列表</p>
      </div>

      <!-- Section filter -->
      <div class="flex flex-wrap items-center gap-2 mb-6">
        <button
          @click="activeSection = null"
          class="text-xs px-3 py-1.5 rounded-full border transition"
          :class="activeSection === null
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >全部 ({{ totalCount }})</button>
        <button
          v-for="s in sections"
          :key="s.key"
          @click="activeSection = s.key"
          class="text-xs px-3 py-1.5 rounded-full border transition"
          :class="activeSection === s.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ s.label }} ({{ s.count }})</button>
      </div>

      <!-- Section content -->
      <div v-for="s in visibleSections" :key="s.key" class="mb-10">
        <h2 class="text-sm font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-1.5 flex items-baseline gap-2">
          <span>{{ s.icon }} {{ s.label }}</span>
          <span class="text-xs text-gray-400 font-normal">{{ s.count }} 份</span>
          <span v-if="s.subDesc" class="text-[11px] text-gray-400 font-normal ml-auto">{{ s.subDesc }}</span>
        </h2>

        <!-- 大公會議文獻：以 councilNo 為主排序，同 councilNo 多份 group 成單卡片 -->
        <div v-if="s.key === 'councils'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <template v-for="g in councilGroups" :key="`council-${g.councilNo}`">
            <!-- 單份文件：直接連到 detail -->
            <NuxtLink
              v-if="g.items.length === 1"
              :to="`/creeds/${g.items[0].slug}`"
              class="block bg-white border border-gray-200 rounded-lg p-4 hover:border-stone-300 hover:shadow-sm transition"
            >
              <div class="flex items-baseline gap-2 mb-1">
                <span class="text-xs font-mono text-stone-500">#{{ g.councilNo }}</span>
                <span class="text-xs text-gray-400">{{ g.items[0].year }}</span>
              </div>
              <div class="font-semibold text-gray-900 text-sm">{{ g.items[0].nameZh }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ g.items[0].nameEn }}</div>
              <div class="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">{{ g.items[0].topic }}</div>
            </NuxtLink>

            <!-- 多份文件：可展開的 group card -->
            <details
              v-else
              class="bg-white border border-gray-200 rounded-lg overflow-hidden md:col-span-2"
              :open="g.councilNo === 21"
            >
              <summary class="cursor-pointer p-4 hover:bg-stone-50 select-none">
                <div class="flex items-baseline gap-2 mb-1">
                  <span class="text-xs font-mono text-stone-500">#{{ g.councilNo }}</span>
                  <span class="text-xs text-gray-400">{{ g.year }}</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-600 ml-2">{{ g.items.length }} 份文件</span>
                </div>
                <div class="font-semibold text-gray-900 text-sm">{{ g.councilNameZh }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ g.councilNameEn }}</div>
                <div class="text-xs text-gray-600 mt-2 leading-relaxed">{{ g.councilTopic }}</div>
              </summary>
              <div class="border-t border-gray-100 bg-stone-50/40 px-2 py-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                <NuxtLink
                  v-for="doc in g.items"
                  :key="doc.slug"
                  :to="`/creeds/${doc.slug}`"
                  class="block bg-white border border-gray-200 rounded p-3 hover:border-stone-300 hover:shadow-sm transition"
                >
                  <div class="flex items-baseline gap-2 mb-0.5">
                    <span v-if="doc.councilDocCode" class="text-[10px] font-mono font-semibold text-stone-700 bg-stone-100 px-1.5 py-0.5 rounded">{{ doc.councilDocCode }}</span>
                    <span class="text-[10px] text-gray-400">{{ doc.year }}</span>
                  </div>
                  <div class="font-semibold text-gray-900 text-sm">{{ doc.nameZh }}</div>
                  <div class="text-[11px] text-gray-500 mt-0.5">{{ doc.nameEn }}</div>
                  <div class="text-[11px] text-gray-600 mt-1.5 line-clamp-2 leading-relaxed">{{ doc.topic }}</div>
                </NuxtLink>
              </div>
            </details>
          </template>
        </div>

        <!-- 信經 / 宗派信條：標準卡片 -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <NuxtLink
            v-for="creed in s.items"
            :key="creed.slug"
            :to="`/creeds/${creed.slug}`"
            class="block bg-white border border-gray-200 rounded-lg p-4 hover:border-stone-300 hover:shadow-sm transition"
          >
            <div class="flex items-baseline gap-2 mb-1">
              <span v-if="creed.councilNo" class="text-xs font-mono text-stone-500">#{{ creed.councilNo }}</span>
              <span class="text-xs text-gray-400">{{ creed.year }}</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm">{{ creed.nameZh }}</div>
            <div class="text-xs text-gray-500 mt-0.5">{{ creed.nameEn }}</div>
            <div class="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">{{ creed.topic }}</div>
            <div class="flex flex-wrap gap-1 mt-2">
              <span
                v-for="t in creed.acceptedBy.slice(0, 4)"
                :key="t"
                class="text-[10px] px-1.5 py-0.5 rounded bg-stone-50 text-stone-600 border border-stone-100"
              >{{ TRADITION_LABEL_ZH[t] }}</span>
              <span
                v-if="creed.acceptedBy.length > 4"
                class="text-[10px] px-1.5 py-0.5 rounded bg-gray-50 text-gray-500"
              >+{{ creed.acceptedBy.length - 4 }}</span>
            </div>
          </NuxtLink>
        </div>

        <div v-if="s.count === 0" class="text-center text-gray-400 py-8 text-sm">
          此區尚無資料
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ALL_CREEDS, TRADITION_LABEL_ZH, type Creed } from '~/data/creeds'

definePageMeta({ middleware: 'auth' })
useHead({ title: '信條對照 — Know Graph Lab' })

type SectionKey = 'creeds' | 'councils' | 'confessions'

/**
 * 「會議信經」白名單 — 雖屬 ecumenical-council category，但歷代視為「信經」短文與
 * 使徒信經 / 亞他那修信經並列。在 list 上顯示在「信經」區。
 */
const CREED_LIKE_SLUGS = new Set([
  'nicaea-325',
  'constantinople-381',
  'chalcedonian-451',
])

function sectionOf(creed: Creed): SectionKey {
  if (creed.category === 'apostolic-creed') return 'creeds'
  if (creed.category === 'ecumenical-council') {
    return CREED_LIKE_SLUGS.has(creed.slug) ? 'creeds' : 'councils'
  }
  // protestant / orthodox / ecumenical-dialogue
  return 'confessions'
}

const activeSection = ref<SectionKey | null>(null)

const creedsItems = computed(() =>
  ALL_CREEDS.filter(c => sectionOf(c) === 'creeds')
    .sort((a, b) => a.order - b.order)
)

const councilsItems = computed(() =>
  ALL_CREEDS.filter(c => sectionOf(c) === 'councils')
    .sort((a, b) => (a.councilNo ?? 0) - (b.councilNo ?? 0) || (a.councilDocOrder ?? 0) - (b.councilDocOrder ?? 0))
)

const confessionsItems = computed(() =>
  ALL_CREEDS.filter(c => sectionOf(c) === 'confessions')
    .sort((a, b) => a.order - b.order)
)

/** 同 councilNo group 在一起；只有 councils 區用 */
interface CouncilGroup {
  councilNo: number
  year: number | string
  councilNameZh: string
  councilNameEn: string
  councilTopic: string
  items: Creed[]
}

const councilGroups = computed<CouncilGroup[]>(() => {
  const map = new Map<number, Creed[]>()
  councilsItems.value.forEach(c => {
    if (c.councilNo == null) return
    if (!map.has(c.councilNo)) map.set(c.councilNo, [])
    map.get(c.councilNo)!.push(c)
  })
  const groups: CouncilGroup[] = []
  Array.from(map.entries()).sort(([a], [b]) => a - b).forEach(([no, items]) => {
    items.sort((a, b) => (a.councilDocOrder ?? 0) - (b.councilDocOrder ?? 0))
    const first = items[0]
    // 多份文件時的會議標題：拿掉 sub-doc 名稱，用通用會議名
    const isMulti = items.length > 1
    groups.push({
      councilNo: no,
      year: first.year,
      councilNameZh: isMulti ? COUNCIL_TITLES_ZH[no] ?? first.nameZh : first.nameZh,
      councilNameEn: isMulti ? COUNCIL_TITLES_EN[no] ?? first.nameEn : first.nameEn,
      councilTopic: isMulti ? COUNCIL_TOPICS[no] ?? first.topic : first.topic,
      items,
    })
  })
  return groups
})

/** 多份文件會議的「主卡片」標題（梵一 2 份／梵二 16 份等） */
const COUNCIL_TITLES_ZH: Record<number, string> = {
  20: '第一次梵蒂岡大公會議',
  21: '第二次梵蒂岡大公會議',
}
const COUNCIL_TITLES_EN: Record<number, string> = {
  20: 'First Vatican Council',
  21: 'Second Vatican Council',
}
const COUNCIL_TOPICS: Record<number, string> = {
  20: '回應啟蒙運動以來理性主義與唯物論對信仰的挑戰 ／ 定義教宗首席權與不可錯謬論 — 共產出 2 份教義憲章（Dei Filius + Pastor Aeternus）',
  21: '禮儀改革 ／ 教會本質 ／ 啟示論 ／ 普世合一 ／ 宗教自由 ／ 教會與現代世界 — 共產出 4 份憲章 + 9 份法令 + 3 份宣言',
}

const sections = computed(() => [
  {
    key: 'creeds' as SectionKey,
    icon: '📿',
    label: '信經',
    subDesc: '使徒信經 / 亞他那修信經 / 尼西亞-君士坦丁堡 / 迦克墩信經',
    items: creedsItems.value,
    count: creedsItems.value.length,
  },
  {
    key: 'councils' as SectionKey,
    icon: '⛪',
    label: '歷代大公會議文獻',
    subDesc: '21 次大公會議（含梵二 16 份文件）',
    items: councilsItems.value,
    count: councilsItems.value.length,
  },
  {
    key: 'confessions' as SectionKey,
    icon: '📜',
    label: '各宗派信條與要理問答',
    subDesc: '新教信條全譜（信義／改革宗／聖公／衛理／浸信／重洗禮）／東正教信條／普世合一對話',
    items: confessionsItems.value,
    count: confessionsItems.value.length,
  },
])

const totalCount = computed(() => sections.value.reduce((s, x) => s + x.count, 0))

const visibleSections = computed(() =>
  activeSection.value === null
    ? sections.value
    : sections.value.filter(s => s.key === activeSection.value)
)
</script>
