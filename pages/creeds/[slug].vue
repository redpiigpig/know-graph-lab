<template>
  <div v-if="creed" class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0">
      <NuxtLink to="/creeds" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <span class="text-sm font-semibold text-stone-900 truncate">{{ creed.nameZh }}</span>
      <span v-if="creed.nameLat" class="text-xs italic text-stone-400 truncate hidden sm:inline">{{ creed.nameLat }}</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap">{{ creed.year }}</span>
    </nav>

    <div class="flex-1 max-w-[1400px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="flex items-baseline flex-wrap gap-2 mb-3">
          <span v-if="creed.councilNo" class="font-mono text-xs px-2 py-0.5 rounded bg-stone-900 text-white">第 {{ creed.councilNo }} 次大公會議</span>
          <span v-if="creed.councilDocCode" class="font-mono text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">{{ creed.councilDocCode }}</span>
          <span class="text-[11px] text-stone-400">{{ CATEGORY_LABEL_ZH[creed.category] }}</span>
        </div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight tracking-tight">{{ creed.nameZh }}</h1>
        <div class="mt-1.5 text-base text-stone-600">{{ creed.nameEn }}</div>
        <div v-if="creed.nameLat" class="text-sm italic text-stone-500 mt-0.5">{{ creed.nameLat }}</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-6 text-sm">
          <div v-if="creed.location" class="flex gap-2"><span class="text-stone-400 shrink-0">地點：</span><span class="text-stone-800">{{ creed.location }}</span></div>
          <div class="flex gap-2"><span class="text-stone-400 shrink-0">年份：</span><span class="text-stone-800">{{ creed.year }}</span></div>
          <div v-if="creed.authors?.length" class="md:col-span-2 flex gap-2"><span class="text-stone-400 shrink-0">主筆／簽署：</span><span class="text-stone-800">{{ creed.authors.join('、') }}</span></div>
          <div class="md:col-span-2 flex gap-2"><span class="text-stone-400 shrink-0">主議題：</span><span class="text-stone-800 leading-relaxed">{{ creed.topic }}</span></div>
        </div>

        <!-- Traditions -->
        <div class="mt-6">
          <div class="text-[11px] uppercase tracking-wider text-stone-400 mb-2">接受傳統</div>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="t in creed.acceptedBy"
              :key="t"
              class="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200"
            >{{ TRADITION_LABEL_ZH[t] }}</span>
          </div>
          <div v-if="creed.rejectedBy?.length" class="mt-2">
            <div class="text-[11px] uppercase tracking-wider text-stone-400 mb-2">不接受</div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="t in creed.rejectedBy"
                :key="t"
                class="text-xs px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200"
              >{{ TRADITION_LABEL_ZH[t] }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Summary -->
      <section v-if="creed.summaryZh" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📌</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">摘要</h2>
        </div>
        <div
          class="text-sm text-stone-700 leading-loose bg-white px-5 py-4 rounded-xl border border-stone-200 shadow-sm whitespace-pre-wrap"
          style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
        >{{ creed.summaryZh }}</div>
      </section>

      <!-- ─── 逐段對照（梵二 / 有 textKey 的長文件） ─── -->
      <section v-if="paragraphMode" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3 flex-wrap">
          <span class="text-base">📜</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">逐段對照</h2>
          <span class="text-[11px] text-stone-400">每段 一 row × 中／英／拉 三欄並列（vatican.va 段號）</span>
          <span v-if="paragraphRows.length > 0" class="text-[11px] text-stone-500 ml-auto">共 {{ paragraphRows.length }} 段</span>
        </div>

        <!-- 版本選擇 bar -->
        <div class="grid gap-3 mb-3" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
          <div class="text-[10px] text-stone-400 uppercase tracking-wider self-center text-center">#</div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-stone-500">中文</span>
            <select v-if="zhVersions.length > 1" v-model="zhPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in zhVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ zhVersions[0]?.shortLabel || '—' }}</span>
          </div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-sky-700">EN</span>
            <select v-if="enVersions.length > 1" v-model="enPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in enVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ enVersions[0]?.shortLabel || '—' }}</span>
          </div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-amber-700">原文</span>
            <select v-if="origVersions.length > 1" v-model="origPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in origVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ origVersions[0]?.shortLabel || '—' }}</span>
          </div>
        </div>

        <div v-if="paragraphsLoading" class="text-center text-stone-400 py-12 text-sm">載入段落中…</div>
        <div v-else-if="paragraphRows.length === 0" class="text-center text-stone-400 py-12 text-sm">⚠ 無法解析段落，可能是 PDF 抽字失敗或文本格式特殊</div>

        <div v-else class="space-y-1.5">
          <article
            v-for="row in paragraphRows"
            :key="row.num"
            class="bg-white border border-stone-200 rounded-md overflow-hidden"
          >
            <div class="grid gap-px bg-stone-100" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
              <div class="bg-stone-50 px-2 py-3 text-xs font-mono font-bold text-stone-700 flex items-start justify-center">
                {{ row.num }}
              </div>
              <div class="bg-white px-3 py-3 text-[0.9rem] leading-loose text-stone-800 whitespace-pre-wrap"
                   style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
                <template v-if="row.byLang.zh">{{ row.byLang.zh }}</template>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div class="bg-white px-3 py-3 text-[0.85rem] leading-relaxed text-stone-800 font-sans whitespace-pre-wrap">
                <template v-if="row.byLang.en">{{ row.byLang.en }}</template>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div class="bg-white px-3 py-3 text-[0.9rem] leading-relaxed text-stone-800 whitespace-pre-wrap"
                   :class="origActiveClass">
                <template v-if="row.byLang.orig">{{ row.byLang.orig }}</template>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
            </div>
          </article>
        </div>

        <!-- 來源 footer -->
        <div class="mt-4 grid gap-2 text-[11px] text-stone-500 leading-relaxed" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
          <div></div>
          <div>
            <div v-if="zhActive?.source">📖 {{ zhActive.source }}</div>
            <div v-if="zhActive?.translator">✍ {{ zhActive.translator }}</div>
            <div v-if="zhActive?.placeholder" class="text-amber-700">⏳ 中文版本為 placeholder</div>
          </div>
          <div>
            <div v-if="enActive?.source">📖 {{ enActive.source }}</div>
          </div>
          <div>
            <div v-if="origActive?.source">📖 {{ origActive.source }}</div>
          </div>
        </div>
      </section>

      <!-- ─── 三欄並列（短信經 — 無 textKey） ─── -->
      <section v-else class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📜</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">三欄對照</h2>
          <span class="text-[11px] text-stone-400">中文 ／ 英文 ／ 原文 — 各欄獨立捲動</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- 中文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-stone-50 to-white">
              <span class="text-base">🀄</span>
              <span class="text-xs font-semibold text-stone-700 uppercase tracking-wider">中文</span>
              <select
                v-if="zhVersions.length > 1"
                v-model="zhPickIdx"
                class="ml-auto text-xs bg-stone-50 border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-stone-400"
              >
                <option v-for="(v, i) in zhVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ zhVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="zhActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="zhActive"
                   class="whitespace-pre-wrap break-words text-[0.9rem] leading-loose text-stone-800"
                   style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              >{{ zhActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">尚無中文版本</div>
              <div v-if="zhActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ 待補正文</div>
            </div>
            <div v-if="zhActive?.source || zhActive?.translator" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              <div v-if="zhActive.source">📖 {{ zhActive.source }}</div>
              <div v-if="zhActive.translator">✍ {{ zhActive.translator }}</div>
            </div>
          </div>

          <!-- 英文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-sky-50 to-white">
              <span class="text-base">🇬🇧</span>
              <span class="text-xs font-semibold text-sky-800 uppercase tracking-wider">English</span>
              <select
                v-if="enVersions.length > 1"
                v-model="enPickIdx"
                class="ml-auto text-xs bg-sky-50 border border-sky-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-sky-400"
              >
                <option v-for="(v, i) in enVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ enVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="enActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="enActive"
                   class="whitespace-pre-wrap break-words text-[0.875rem] leading-relaxed text-stone-800 font-sans"
              >{{ enActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">No English version</div>
              <div v-if="enActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ pending</div>
            </div>
            <div v-if="enActive?.source" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              📖 {{ enActive.source }}
            </div>
          </div>

          <!-- 原文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-amber-50 to-white">
              <span class="text-base">📜</span>
              <span class="text-xs font-semibold text-amber-800 uppercase tracking-wider">原文</span>
              <select
                v-if="origVersions.length > 1"
                v-model="origPickIdx"
                class="ml-auto text-xs bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-amber-400"
              >
                <option v-for="(v, i) in origVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ origVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="origActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="origActive"
                   class="whitespace-pre-wrap break-words text-[0.9rem] leading-relaxed text-stone-800"
                   :class="origActiveClass"
              >{{ origActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">尚無原文版本</div>
              <div v-if="origActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ 待補</div>
            </div>
            <div v-if="origActive?.source" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              📖 {{ origActive.source }}
            </div>
          </div>
        </div>
      </section>

      <!-- Notes -->
      <section v-if="creed.notes" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📝</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">歷史 Notes</h2>
        </div>
        <div
          class="text-sm text-stone-700 leading-loose bg-white px-5 py-4 rounded-xl border border-stone-200 shadow-sm whitespace-pre-wrap"
          style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
        >{{ creed.notes }}</div>
      </section>

      <!-- Related -->
      <section v-if="relatedCreeds.length > 0" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">🔗</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">相關信條</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <NuxtLink
            v-for="r in relatedCreeds"
            :key="r.slug"
            :to="`/creeds/${r.slug}`"
            class="block bg-white border border-stone-200 rounded-lg px-4 py-3 hover:border-stone-400 hover:shadow-md transition-all duration-150"
          >
            <div class="flex items-baseline gap-1.5 mb-0.5">
              <span v-if="r.councilDocCode" class="text-[10px] font-mono font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-100">{{ r.councilDocCode }}</span>
              <span class="text-[10px] text-stone-400">{{ r.year }}</span>
            </div>
            <div class="font-semibold text-stone-900 text-sm">{{ r.nameZh }}</div>
            <div class="text-xs text-stone-500 mt-0.5 line-clamp-1">{{ r.nameEn }}</div>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="min-h-dvh flex items-center justify-center text-stone-400">
    找不到此信條：{{ route.params.slug }}
    <NuxtLink to="/creeds" class="ml-3 text-blue-500 underline">回信條列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { findCreed, ALL_CREEDS, CATEGORY_LABEL_ZH, TRADITION_LABEL_ZH, type CreedLanguage, type CreedVersion } from '~/data/creeds'
import { loadCreedText, loadCreedParagraphs } from '~/data/creeds/textLoader'
import { alignParagraphs, type ParagraphRow } from '~/data/creeds/paragraphParser'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const creed = computed(() => findCreed(route.params.slug as string))

useHead(() => ({
  title: creed.value ? `${creed.value.nameZh} — 信條對照` : '找不到信條',
}))

// Bucket CreedVersion -> zh / en / orig
// - zh: lang.startsWith('zh-')
// - en: lang === 'en'
// - orig: others (grc, lat, lat-filioque, hye, cop, syr-east, syr-west, gez, arc, hbo, de, fr)
type Bucket = 'zh' | 'en' | 'orig'
function bucketOf(lang: CreedLanguage): Bucket {
  if (lang.startsWith('zh-')) return 'zh'
  if (lang === 'en') return 'en'
  return 'orig'
}

/** 短 label — 給 dropdown 用，避免太長 */
const SHORT_LABEL: Partial<Record<CreedLanguage, string>> = {
  'zh-Hant-Joint2019': '五宗派合一',
  'zh-Hant-Catholic': '思高（天主教）',
  'zh-Hant-Anglican': '聖公會',
  'zh-Hant-Lutheran': '信義會',
  'zh-Hant-Orthodox': '東正教',
  'zh-Hant-Reformed': '改革宗',
  'zh-Hant-Methodist': '衛理宗',
  'zh-Hant-Baptist': '浸信宗',
  'zh-Hant-Protestant': '新教通用',
  'zh-Hant': '繁體中文',
  en: 'English',
  lat: 'Latin',
  'lat-filioque': 'Latin (filioque)',
  grc: 'Greek',
  hye: 'Armenian',
  cop: 'Coptic',
  'cop-sa': 'Coptic (Sahidic)',
  'syr-east': 'Syriac (East)',
  'syr-west': 'Syriac (West)',
  gez: "Ge'ez",
  hbo: 'Hebrew',
  arc: 'Aramaic',
  de: 'German',
  fr: 'French',
}

interface EnrichedVersion extends CreedVersion {
  shortLabel: string
}

function enrich(v: CreedVersion): EnrichedVersion {
  return { ...v, shortLabel: SHORT_LABEL[v.lang] || v.label }
}

/** Lazy text cache — reactive, keyed by textKey. */
const lazyTextCache = reactive<Record<string, string | 'loading' | undefined>>({})

function ensureText(version: EnrichedVersion | undefined): EnrichedVersion | undefined {
  if (!version) return undefined
  if (!version.textKey) return version  // already inline
  const cached = lazyTextCache[version.textKey]
  if (cached === undefined) {
    lazyTextCache[version.textKey] = 'loading'
    loadCreedText(version.textKey)
      .then(text => { lazyTextCache[version.textKey!] = text })
      .catch(err => { lazyTextCache[version.textKey!] = `[載入失敗：${err.message}]` })
    return { ...version, text: '載入中...' }
  }
  if (cached === 'loading') return { ...version, text: '載入中...' }
  return { ...version, text: cached }
}

/** 中文版本排序：合一 → 聖公 → 信義 → 天主教 → 東正 → 改革 → 衛理 → 浸信 → 通用 */
const ZH_ORDER: CreedLanguage[] = [
  'zh-Hant-Joint2019',
  'zh-Hant-Anglican',
  'zh-Hant-Lutheran',
  'zh-Hant-Catholic',
  'zh-Hant-Orthodox',
  'zh-Hant-Reformed',
  'zh-Hant-Methodist',
  'zh-Hant-Baptist',
  'zh-Hant-Protestant',
  'zh-Hant',
]
function zhSubOrder(lang: CreedLanguage): number {
  const i = ZH_ORDER.indexOf(lang)
  return i === -1 ? 999 : i
}

/** 原文版本排序：lat → lat-filioque → grc → hbo → 其他 */
const ORIG_ORDER: CreedLanguage[] = [
  'lat',
  'lat-filioque',
  'grc',
  'hbo',
  'arc',
  'syr-east',
  'syr-west',
  'hye',
  'cop',
  'cop-sa',
  'gez',
  'de',
  'fr',
]
function origSubOrder(lang: CreedLanguage): number {
  const i = ORIG_ORDER.indexOf(lang)
  return i === -1 ? 999 : i
}

const zhVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions]
    .filter(v => bucketOf(v.lang) === 'zh')
    .sort((a, b) => zhSubOrder(a.lang) - zhSubOrder(b.lang))
    .map(enrich)
})
const enVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions].filter(v => bucketOf(v.lang) === 'en').map(enrich)
})
const origVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions]
    .filter(v => bucketOf(v.lang) === 'orig')
    .sort((a, b) => origSubOrder(a.lang) - origSubOrder(b.lang))
    .map(enrich)
})

const zhPickIdx = ref(0)
const enPickIdx = ref(0)
const origPickIdx = ref(0)

// 切換 creed 時重置
watch(() => creed.value?.slug, () => {
  zhPickIdx.value = 0
  enPickIdx.value = 0
  origPickIdx.value = 0
})

const zhActive = computed(() => ensureText(zhVersions.value[zhPickIdx.value]))
const enActive = computed(() => ensureText(enVersions.value[enPickIdx.value]))
const origActive = computed(() => ensureText(origVersions.value[origPickIdx.value]))

const origActiveClass = computed(() => {
  if (!origActive.value) return ''
  const lang = origActive.value.lang
  if (lang === 'lat' || lang === 'lat-filioque') return 'italic'
  if (lang === 'grc' || lang === 'cop' || lang === 'cop-sa') return ''
  return ''
})

const relatedCreeds = computed(() => {
  if (!creed.value?.related) return []
  return creed.value.related
    .map(slug => ALL_CREEDS.find(c => c.slug === slug))
    .filter((c): c is NonNullable<typeof c> => !!c)
})

// ── Paragraph mode（梵二 / 有 textKey 的長文件） ─────────────────
const paragraphMode = computed(() => {
  if (!creed.value) return false
  return creed.value.versions.some(v => !!v.textKey)
})

const paragraphRows = ref<ParagraphRow[]>([])
const paragraphsLoading = ref(false)

async function recomputeParagraphs() {
  if (!paragraphMode.value) {
    paragraphRows.value = []
    return
  }
  const zh = zhActive.value
  const en = enActive.value
  const orig = origActive.value
  const tasks: Array<Promise<['zh' | 'en' | 'orig', Awaited<ReturnType<typeof loadCreedParagraphs>>]>> = []
  if (zh?.textKey) tasks.push(loadCreedParagraphs(zh.textKey).then(p => ['zh', p] as const))
  if (en?.textKey) tasks.push(loadCreedParagraphs(en.textKey).then(p => ['en', p] as const))
  if (orig?.textKey) tasks.push(loadCreedParagraphs(orig.textKey).then(p => ['orig', p] as const))

  if (tasks.length === 0) {
    paragraphRows.value = []
    return
  }

  paragraphsLoading.value = true
  try {
    const results = await Promise.all(tasks)
    const byLang: Record<string, Awaited<ReturnType<typeof loadCreedParagraphs>>> = {}
    for (const [k, p] of results) byLang[k] = p
    paragraphRows.value = alignParagraphs(byLang)
  } catch (err) {
    console.error('[creed paragraph load]', err)
    paragraphRows.value = []
  } finally {
    paragraphsLoading.value = false
  }
}

watch([paragraphMode, zhActive, enActive, origActive], () => {
  recomputeParagraphs()
}, { immediate: true })
</script>
