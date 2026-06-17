<template>
  <div v-if="pope" class="flex flex-col bg-stone-50 min-h-dvh">
    <AppHeader :title="pope.nameZh" :back="{ to: '/encyclicals', label: '🕊️ 教宗訓導文獻' }" container-class="max-w-5xl">
      <template #actions>
        <NuxtLink
          :to="`/encyclicals/century/${primaryCentury}`"
          class="text-sm text-stone-500 hover:text-stone-900 transition"
        >{{ primaryCentury }} 世紀</NuxtLink>
        <span class="text-xs text-stone-400 whitespace-nowrap">{{ docs.length }} 篇</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Pope header -->
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="flex items-baseline flex-wrap gap-2 mb-2">
          <span class="font-mono text-xs px-2 py-0.5 rounded bg-stone-900 text-white">第 {{ popeNoLabel }} 任</span>
          <span
            v-for="c in centuriesOfPope(pope)"
            :key="c"
            class="text-[11px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-700 border border-stone-200"
          >{{ c }} 世紀</span>
          <span class="text-xs text-stone-400">{{ pope.nationality }}</span>
        </div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight">{{ pope.nameZh }}</h1>
        <div class="mt-1 text-base text-stone-600">{{ pope.nameEn }}</div>
        <div class="text-sm italic text-stone-500 mt-0.5">{{ pope.nameLat }}</div>
        <div v-if="pope.birthName" class="text-xs text-stone-400 mt-1">俗名 {{ pope.birthName }}</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-5 text-sm">
          <div class="flex gap-2">
            <span class="text-stone-400 shrink-0">在位：</span>
            <span class="text-stone-800 font-mono">
              {{ pope.pontificateStart.slice(0, 10) }} – {{ pope.pontificateEnd ? pope.pontificateEnd.slice(0, 10) : '在位中' }}
            </span>
          </div>
        </div>

        <p v-if="pope.notesZh" class="mt-5 text-[14px] text-stone-700 leading-loose"
           style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
          {{ pope.notesZh }}
        </p>
      </header>

      <!-- Documents — 3-tab tier 分組 -->
      <div v-if="docs.length === 0" class="text-center text-stone-400 py-12">
        <p class="text-sm">尚未錄入此教宗的訓導文件。</p>
        <p class="text-xs text-stone-300 mt-2">資料源排程：依世紀新→舊；本教宗待辦。</p>
      </div>

      <div v-else>
        <!-- Tier tabs -->
        <div class="flex border-b border-stone-200 mb-4 -mx-1">
          <button
            v-for="t in TIER_ORDER"
            :key="t"
            type="button"
            class="px-4 py-2.5 mx-1 text-sm font-semibold border-b-2 transition-colors"
            :class="activeTier === t
              ? 'border-stone-900 text-stone-900'
              : 'border-transparent text-stone-400 hover:text-stone-700'"
            @click="activeTier = t"
          >
            {{ TIER_LABEL_ZH[t] }}
            <span class="ml-1.5 text-[11px] font-normal text-stone-500">
              {{ docsByTier.get(t)?.length || 0 }}
            </span>
          </button>
        </div>

        <!-- Active tier description -->
        <p class="text-xs text-stone-500 mb-4 leading-relaxed">
          {{ TIER_DESC_ZH[activeTier] }}
        </p>

        <!-- Tier content -->
        <div v-if="(docsByTier.get(activeTier)?.length || 0) === 0" class="text-center text-stone-400 py-12 border border-stone-200 rounded-lg bg-stone-50/50">
          <p class="text-sm">此教宗暫無「{{ TIER_LABEL_ZH[activeTier] }}」類型文件入庫。</p>
          <p class="text-xs text-stone-300 mt-2">
            <template v-if="activeTier === 'curia'">
              部會文件（信理部／禮儀部等頒布）資料層待下輪 batch 入庫。
            </template>
            <template v-else-if="activeTier === 'message'">
              一般文告（年度世界和平日／青年日等系列）資料層待下輪 batch 入庫。
            </template>
            <template v-else>
              敬請期待後續資料補入。
            </template>
          </p>
        </div>

        <div v-else>
          <div v-for="group in docsByCategoryInActiveTier" :key="group.category" class="mb-6">
            <div class="text-xs font-semibold text-stone-600 mb-2 flex items-baseline gap-2">
              <span>{{ CATEGORY_LABEL_ZH[group.category] }}</span>
              <span class="text-[10px] italic text-stone-400">{{ CATEGORY_LABEL_LAT[group.category] }}</span>
              <span class="text-[10px] text-stone-400 ml-auto">{{ group.docs.length }} 篇</span>
            </div>

            <div class="grid grid-cols-1 gap-2.5">
              <NuxtLink
                v-for="doc in group.docs"
                :key="doc.slug"
                :to="`/encyclicals/${doc.slug}`"
                class="block bg-white border border-stone-200 rounded-lg px-5 py-4 hover:border-stone-400 hover:shadow-md transition-all duration-150"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-baseline gap-2 mb-1 flex-wrap">
                      <span class="text-[11px] font-mono text-stone-400">{{ doc.promulgationDate }}</span>
                      <span class="text-[10px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-600 border border-stone-200">
                        {{ doc.century }}c
                      </span>
                      <span
                        v-if="doc.issuer"
                        class="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100"
                      >{{ doc.issuer }}</span>
                    </div>
                    <div class="font-semibold text-stone-900 text-base leading-snug">{{ doc.titleZh }}</div>
                    <div class="text-sm italic text-stone-500 mt-0.5">{{ doc.titleLat }}</div>
                    <div v-if="doc.titleEn" class="text-xs text-stone-400 mt-0.5">{{ doc.titleEn }}</div>
                    <div v-if="doc.topics?.length" class="flex flex-wrap gap-1 mt-2">
                      <span
                        v-for="t in doc.topics.slice(0, 5)"
                        :key="t"
                        class="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100"
                      >{{ t }}</span>
                    </div>
                  </div>
                  <div class="text-stone-300 group-hover:text-stone-500 self-center text-xl">→</div>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="min-h-dvh flex items-center justify-center text-stone-400">
    找不到此教宗：{{ route.params.slug }}
    <NuxtLink to="/encyclicals" class="ml-3 text-blue-500 underline">回列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import {
  findPope,
  centuriesOfPope,
  documentsByPope,
  CATEGORY_LABEL_ZH,
  CATEGORY_LABEL_LAT,
  TIER_LABEL_ZH,
  TIER_DESC_ZH,
  docTier,
  POPES,
  type PapalDocCategory,
  type PapalDocTier,
} from '~/data/encyclicals'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const pope = computed(() => findPope(route.params.slug as string))

useHead(() => ({
  title: pope.value ? `${pope.value.nameZh} — 教宗訓導文獻` : '找不到教宗',
}))

const docs = computed(() => (pope.value ? documentsByPope(pope.value.slug) : []))

/** breadcrumb 用：取教宗任期最晚的世紀作主世紀 */
const primaryCentury = computed(() => {
  if (!pope.value) return 21
  const cs = centuriesOfPope(pope.value)
  return cs[cs.length - 1]
})

/** 取此教宗的序號（POPES 表內倒推位置；UI 顯示用） */
const popeNoLabel = computed(() => {
  // popes-catalog 已在 notesZh 第一句寫了序號，這裡只當 fallback
  if (!pope.value?.notesZh) return '—'
  const m = pope.value.notesZh.match(/第\s*(\d+)\s*任/)
  return m ? m[1] : '—'
})

/** Tier 顯示順序：訓導 → 部會 → 文告 */
const TIER_ORDER: PapalDocTier[] = ['teaching', 'curia', 'message']

/** 依文件類別分組（通諭 / 勸諭 / 憲令 / 自動詔書 ...） */
const CATEGORY_ORDER: PapalDocCategory[] = [
  // teaching
  'encyclical',
  'apostolic-exhort',
  'apostolic-const',
  'apostolic-letter',
  'motu-proprio',
  'bull',
  'brief',
  'epistola',
  // curia
  'instruction',
  'declaration',
  'decree',
  'notification',
  'responsum',
  'curia-document',
  // message
  'allocution',
  'homily',
  'message',
  'letter-informal',
]

/** Active tier — 預設 'teaching' */
const activeTier = ref<PapalDocTier>('teaching')

/** 將 docs 按 tier 分組 */
const docsByTier = computed(() => {
  const map = new Map<PapalDocTier, typeof docs.value>()
  for (const t of TIER_ORDER) map.set(t, [])
  for (const d of docs.value) {
    map.get(docTier(d))!.push(d)
  }
  return map
})

/** 當前 tier 內，再按 category 分組 */
const docsByCategoryInActiveTier = computed(() => {
  const tierDocs = docsByTier.value.get(activeTier.value) || []
  const map = new Map<PapalDocCategory, typeof docs.value>()
  for (const d of tierDocs) {
    if (!map.has(d.category)) map.set(d.category, [])
    map.get(d.category)!.push(d)
  }
  return CATEGORY_ORDER
    .filter(c => map.has(c))
    .map(c => ({ category: c, docs: map.get(c)! }))
})
</script>
