<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="loc ? loc.text.title_zh : '祆教經典'"
      :back="{ to: backTo, label: backLabel }"
      container-class="max-w-6xl"
    >
      <template #actions>
        <span v-if="doc" class="text-xs text-gray-400">{{ doc.segments.length }} 段 · 已譯 {{ translated }}</span>
      </template>
    </AppHeader>

    <div v-if="!loc" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此篇。</div>

    <div v-else class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
      <!-- 篇首 -->
      <div class="mb-5">
        <div class="flex items-baseline gap-2 flex-wrap mb-1">
          <h1 class="text-xl font-bold text-gray-900 break-words">{{ loc.text.title_zh }}</h1>
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-orange-50 text-orange-800">{{ loc.text.siglum }}</span>
          <span
            class="text-[11px] px-2 py-0.5 rounded"
            :class="[status.rowCls ? 'bg-white' : '', status.titleCls]"
          >
            <span class="inline-block w-2 h-2 rounded-full mr-1 align-middle" :class="status.dotCls" />{{ status.zh }}
          </span>
        </div>
        <div v-if="loc.text.title_orig" class="text-xs text-gray-400 italic break-words mb-2">{{ loc.text.title_orig }}</div>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600 mb-3">
          <div class="flex gap-2 sm:col-span-2">
            <dt class="shrink-0 text-gray-400">所屬</dt>
            <dd class="break-words">{{ loc.canon.name }}‧{{ loc.volume.name }}‧{{ loc.division.label }}</dd>
          </div>
          <div v-if="loc.text.author" class="flex gap-2"><dt class="shrink-0 text-gray-400">作者</dt><dd class="break-words">{{ loc.text.author }}</dd></div>
          <div v-if="loc.text.era" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ loc.text.era }}</dd></div>
          <div v-if="loc.text.language" class="flex gap-2"><dt class="shrink-0 text-gray-400">語言</dt><dd class="break-words">{{ loc.text.language }}</dd></div>
          <div v-if="loc.text.extent" class="flex gap-2"><dt class="shrink-0 text-gray-400">篇幅</dt><dd class="break-words">{{ loc.text.extent }}</dd></div>
        </dl>

        <p v-if="loc.text.note" class="text-sm text-gray-600 leading-relaxed break-words mb-2">{{ loc.text.note }}</p>
        <p v-if="loc.text.intro" class="text-sm text-gray-700 leading-relaxed break-words bg-white border border-gray-200 rounded-xl p-4">{{ loc.text.intro }}</p>

        <!-- 佚書：讀者看到的不是原書而是撮要，這件事必須先講 -->
        <div v-if="loc.text.status === 'lost-summary'" class="mt-3 px-3 py-2.5 bg-rose-50 border border-rose-200 rounded-lg">
          <div class="text-[11px] font-semibold text-rose-900 mb-0.5">原書已佚 —— 以下不是原文</div>
          <p class="text-[11px] text-rose-800 leading-relaxed break-words">
            本部納斯克無一字傳世。此處所收為<b>{{ loc.text.via }}</b>對它的內容撮要，
            是後人的轉述而非原書文字。引用時必須標明轉引，不可當作納斯克本身的文句。
          </p>
        </div>
        <p v-else-if="loc.text.via" class="mt-3 text-[11px] text-rose-700 break-words">僅存於：{{ loc.text.via }}</p>

        <NuxtLink
          v-if="loc.text.seealso"
          :to="'/avesta'"
          class="inline-block mt-2 text-[11px] text-orange-800 hover:underline break-words"
        >互見：{{ loc.text.seealso }}</NuxtLink>
      </div>

      <!-- ───── 正文未上架：說清楚現況與可取之處，而不是給一個空頁 ───── -->
      <div v-if="!doc" class="bg-white border border-gray-200 rounded-xl p-5">
        <h2 class="text-sm font-bold text-gray-800 mb-2">正文尚未上架</h2>
        <p class="text-xs text-gray-500 leading-relaxed mb-4">
          本篇的書目已建立，逐段對照尚未抓取。下表是三欄各自的取源現況——
          它說的是「線上找不找得到」，不是「本站有沒有」。
        </p>
        <div class="space-y-2">
          <div v-for="c in COLS" :key="c.key" class="flex items-start gap-3">
            <span class="shrink-0 w-20 text-xs font-medium text-gray-700">{{ c.label }}</span>
            <span class="shrink-0 text-[11px] px-1.5 py-0.5 rounded" :class="COLUMN_META[cols[c.key]].cls">
              {{ COLUMN_META[cols[c.key]].zh }}
            </span>
            <span class="min-w-0 flex-1 text-[11px] text-gray-500 leading-relaxed break-words">{{ SOURCE_NOTE[c.key][cols[c.key]] }}</span>
          </div>
        </div>
      </div>

      <!-- ───── 三欄逐段對照 ───── -->
      <template v-else>
        <!-- 繁中的來源鏈：直譯自原文的可信度低於經由學術英譯，讀者有權知道 -->
        <div v-if="doc.pivot === 'none'" class="mb-4 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="text-[11px] font-semibold text-amber-900 mb-0.5">繁中直接譯自原文轉寫</div>
          <p class="text-[11px] text-amber-800 leading-relaxed break-words">
            本篇無可用的公有領域英譯，繁中係直接譯自阿維斯陀語／中古波斯語轉寫，
            未經學術英譯中介，可信度低於其他各篇。{{ doc.pivot_note }}
          </p>
        </div>
        <p
          v-else-if="doc.pivot_note"
          class="mb-4 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px] text-gray-500 leading-relaxed break-words"
        >{{ doc.pivot_note }}</p>

        <!-- 欄位切換 -->
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <button
            v-for="c in visibleCols"
            :key="c.key"
            class="text-xs px-2.5 py-1 rounded-lg border transition"
            :class="shown.includes(c.key)
              ? 'bg-orange-800 text-white border-orange-800'
              : 'bg-white text-gray-500 border-gray-300 hover:border-orange-400'"
            @click="toggle(c.key)"
          >{{ c.label }}</button>

          <!-- 阿維斯陀字母切換：只在整篇都轉得乾淨時才給，免得半篇是字母半篇是拉丁 -->
          <button
            v-if="shown.includes('orig') && scriptConvertible"
            class="text-xs px-2.5 py-1 rounded-lg border transition ml-2"
            :class="useScript
              ? 'bg-stone-800 text-white border-stone-800'
              : 'bg-white text-gray-500 border-gray-300 hover:border-stone-400'"
            @click="useScript = !useScript"
          >𐬀 阿維斯陀字母</button>
          <span
            v-else-if="shown.includes('orig') && doc.segments.some(s => s.orig)"
            class="text-[11px] text-gray-400 break-words"
          >{{ noScriptReason }}</span>
        </div>

        <!-- 逐段 -->
        <div class="space-y-2">
          <div
            v-for="(seg, i) in doc.segments"
            :key="i"
            class="bg-white border border-gray-200 rounded-xl overflow-hidden"
          >
            <div class="px-3 py-1 bg-slate-50 border-b border-gray-100 text-[11px] font-mono text-gray-500">
              {{ seg.ref }}
            </div>
            <div class="grid" :class="gridCls">
              <div
                v-for="c in visibleCols.filter(x => shown.includes(x.key))"
                :key="c.key"
                class="px-4 py-3 border-gray-100 [&:not(:last-child)]:border-b md:[&:not(:last-child)]:border-b-0 md:[&:not(:last-child)]:border-r"
              >
                <div class="text-[10px] text-gray-400 mb-1 md:hidden">{{ c.label }}</div>
                <p
                  v-if="cellText(seg, c.key)"
                  class="text-sm leading-relaxed break-words whitespace-pre-line"
                  :class="c.key === 'orig'
                    ? (useScript ? 'text-gray-800 text-lg leading-loose' : 'text-gray-800 italic')
                    : 'text-gray-700'"
                  :dir="c.key === 'orig' && useScript ? 'rtl' : 'ltr'"
                >{{ cellText(seg, c.key) }}</p>
                <p v-else class="text-sm text-gray-300">—</p>
              </div>
            </div>
            <p v-if="seg.note" class="px-4 py-1.5 text-[11px] text-gray-500 bg-slate-50 border-t border-gray-100 break-words">{{ seg.note }}</p>
          </div>
        </div>

        <!-- 取源與體例 -->
        <div class="mt-8 text-[11px] text-gray-400 leading-relaxed border-t border-gray-200 pt-4 space-y-1">
          <p v-if="doc.orig_source"><b class="text-gray-500">原文</b>　{{ doc.orig_source }}<a v-if="doc.orig_url" :href="doc.orig_url" target="_blank" rel="noopener" class="ml-1 text-orange-700 hover:underline">↗</a></p>
          <p v-if="doc.en_source"><b class="text-gray-500">英譯</b>　{{ doc.en_translator ? `${doc.en_translator}，` : '' }}{{ doc.en_source }}<a v-if="doc.en_url" :href="doc.en_url" target="_blank" rel="noopener" class="ml-1 text-orange-700 hover:underline">↗</a></p>
          <p><b class="text-gray-500">授權</b>　{{ doc.licence }}</p>
          <p>
            <b class="text-gray-500">體例</b>
            段號一律沿用經文自身的章節編號（{{ doc.siglum }}.N），不自編。原文欄為霍夫曼式拉丁轉寫；
            阿維斯陀字母欄（若有）由轉寫程式轉換而得，非抄本影像，僅供辨識字形之用，引用請以轉寫為準。繁中為本站逐段翻譯。
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { COLUMN_META, STATUS_META, columnsOf, findText } from '~/data/avesta'
import { loadText } from '~/data/avesta/sources'
import type { AvestaSegment } from '~/data/avesta/sources'
import { toAvestanScript } from '~/utils/avestanScript'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const loc = computed(() => findText(slug.value))

// 正文按需載入；全部上架後這個目錄會很大，不可在建置期一次打包。
const { data: doc } = await useAsyncData(
  () => `avesta-text-${slug.value}`,
  () => loadText(slug.value).then(d => d ?? null),
  { watch: [slug] },
)

useHead(() => ({ title: `${loc.value?.text.title_zh ?? '祆教經典'} — 祆教經典` }))

const status = computed(() => STATUS_META[loc.value?.text.status ?? 'whole'])
const cols = computed(() => (loc.value ? columnsOf(loc.value.text, loc.value.division) : { orig: 'none', en: 'none', zh: 'none' } as const))
const backTo = computed(() => (loc.value ? `/avesta/${loc.value.canon.key}/${loc.value.volume.key}` : '/avesta'))
const backLabel = computed(() => loc.value?.volume.name ?? '祆教經典')
const translated = computed(() => doc.value?.segments.filter(s => (s.zh ?? '').trim()).length ?? 0)

const COLS = [
  { key: 'orig' as const, label: '原文轉寫' },
  { key: 'en' as const, label: '英譯' },
  { key: 'zh' as const, label: '繁體中文' },
]

// 空欄不出，免得整欄都是「—」
const visibleCols = computed(() =>
  COLS.filter(c => doc.value?.segments.some(s => (s[c.key] ?? '').trim().length > 0)))
const shown = ref<Array<'orig' | 'en' | 'zh'>>(['orig', 'en', 'zh'])
watchEffect(() => { shown.value = visibleCols.value.map(c => c.key) })

function toggle(key: 'orig' | 'en' | 'zh') {
  if (shown.value.includes(key)) {
    if (shown.value.length > 1) shown.value = shown.value.filter(c => c !== key)
  } else {
    shown.value = visibleCols.value.map(c => c.key).filter(k => shown.value.includes(k) || k === key)
  }
}

const gridCls = computed(() => ({
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-3',
}[shown.value.length] ?? 'grid-cols-1'))

// ── 阿維斯陀字母 ──
// 只有整篇都轉得乾淨才給切換鈕。半篇字母半篇拉丁比全部拉丁更難讀，
// 而且會讓拼寫錯誤混在裡面看不出來。
const useScript = ref(false)
const conversions = computed(() =>
  (doc.value?.segments ?? []).map(s => (s.orig ? toAvestanScript(s.orig) : null)))
const unmappedChars = computed(() =>
  [...new Set(conversions.value.flatMap(c => c?.unmapped ?? []))])

// 兩道閘，缺一不可：
//   一、轉寫方案必須是霍夫曼式。舊式羅馬轉寫的 sh／ng 有歧義，硬轉會拼錯，
//       而錯了之後畫面仍是一串漂亮的阿維斯陀字——沒有人看得出來。
//   二、整篇都要轉得乾淨。半篇字母半篇拉丁比全部拉丁更難讀。
const scriptConvertible = computed(() =>
  doc.value?.orig_scheme === 'hoffmann'
  && conversions.value.some(Boolean)
  && unmappedChars.value.length === 0)

const noScriptReason = computed(() => {
  if (doc.value?.orig_scheme === 'geldner-roman') {
    return '（本篇原文為蓋爾德納舊式羅馬轉寫，sh／ng 一類二合字母需語音學判斷才拆得開，'
      + '機器轉寫會拼錯，故不提供字母切換）'
  }
  if (doc.value?.orig_scheme && doc.value.orig_scheme !== 'hoffmann') {
    return '（本篇原文非阿維斯陀語，無字母欄）'
  }
  return `（本篇轉寫含 ${unmappedChars.value.join(' ')} 等表外字元，不提供字母切換）`
})

function cellText(seg: AvestaSegment, key: 'orig' | 'en' | 'zh'): string {
  if (key !== 'orig') return seg[key] ?? ''
  if (!seg.orig) return ''
  return useScript.value ? toAvestanScript(seg.orig).script : seg.orig
}

// 未上架時，逐欄說明「線上找不找得到」
const SOURCE_NOTE: Record<'orig' | 'en' | 'zh', Record<string, string>> = {
  orig: {
    ready: '已抓取並逐段對齊。',
    available: 'avesta.org（蓋爾德納轉寫）或法蘭克福 TITUS 語料庫有全文，待抓取。',
    copyright: '僅有版權內的現代校訂本，不能使用。',
    none: '線上查無可用的轉寫；巴列維文獻的原文轉寫多數屬於此類。',
  },
  en: {
    ready: '已抓取並逐段對齊。',
    available: '《東方聖書》有公有領域英譯（阿維斯陀為第 4、23、31 卷，巴列維文獻為第 5、18、24、37、47 卷），待抓取。',
    copyright: '韋斯特的《東方聖書》未收本篇，通行譯本仍在版權內，不能作為對照欄底本。',
    none: '查無可用的公有領域英譯。',
  },
  zh: {
    ready: '已逐段翻譯上架。',
    available: '待翻譯。',
    copyright: '既有中譯在版權內，不採用；本站另行自譯。',
    none: '無既有中譯。本站以英譯為中介自譯，尚未排入。',
  },
}
</script>
