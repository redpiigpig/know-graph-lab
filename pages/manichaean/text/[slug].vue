<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="loc ? loc.text.title_zh : '摩尼教經典'"
      :back="{ to: backTo, label: backLabel }"
      container-class="max-w-6xl"
    >
      <template #actions>
        <span v-if="doc" class="text-xs text-gray-400">{{ doc.segments.length }} 段<template v-if="!isChinese"> · 已譯 {{ translated }}</template></span>
      </template>
    </AppHeader>

    <div v-if="!loc" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此篇。</div>

    <div v-else class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
      <!-- 篇首 -->
      <div class="mb-5">
        <div class="flex items-baseline gap-2 flex-wrap mb-1">
          <h1 class="text-xl font-bold text-gray-900 break-words">{{ loc.text.title_zh }}</h1>
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-amber-300">{{ loc.text.siglum }}</span>
          <span class="text-[11px] px-2 py-0.5 rounded bg-white" :class="status.titleCls">
            <span class="inline-block w-2 h-2 rounded-full mr-1 align-middle" :class="status.dotCls" />{{ status.zh }}
          </span>
          <span
            v-if="loc.text.hostile"
            class="text-[11px] px-2 py-0.5 rounded"
            :class="HOSTILE_META[loc.text.hostile].cls"
          >{{ HOSTILE_META[loc.text.hostile].zh }}</span>
        </div>
        <div v-if="loc.text.title_orig" class="text-xs text-gray-400 italic break-words mb-2">{{ loc.text.title_orig }}</div>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600 mb-3">
          <div class="flex gap-2 sm:col-span-2">
            <dt class="shrink-0 text-gray-400">所屬</dt>
            <dd class="break-words">{{ loc.canon.name }}‧{{ loc.volume.name }}‧{{ loc.division.label }}</dd>
          </div>
          <div v-if="loc.text.provenance" class="flex gap-2 sm:col-span-2">
            <dt class="shrink-0 text-gray-400">出土／館藏</dt><dd class="break-words text-amber-800">{{ loc.text.provenance }}</dd>
          </div>
          <div v-if="loc.text.author" class="flex gap-2"><dt class="shrink-0 text-gray-400">作者</dt><dd class="break-words">{{ loc.text.author }}</dd></div>
          <div v-if="loc.text.era" class="flex gap-2"><dt class="shrink-0 text-gray-400">年代</dt><dd class="break-words">{{ loc.text.era }}</dd></div>
          <div v-if="loc.text.language" class="flex gap-2"><dt class="shrink-0 text-gray-400">語言</dt><dd class="break-words">{{ loc.text.language }}</dd></div>
          <div v-if="loc.text.extent" class="flex gap-2"><dt class="shrink-0 text-gray-400">篇幅</dt><dd class="break-words">{{ loc.text.extent }}</dd></div>
        </dl>

        <p v-if="loc.text.note" class="text-sm text-gray-600 leading-relaxed break-words mb-2">{{ loc.text.note }}</p>
        <p v-if="loc.text.intro" class="text-sm text-gray-700 leading-relaxed break-words bg-white border border-gray-200 rounded-xl p-4">{{ loc.text.intro }}</p>

        <!-- 佚書：讀者看到的不是原書。這件事必須先講。 -->
        <div
          v-if="loc.text.status === 'lost-listed' || loc.text.status === 'lost-cited'"
          class="mt-3 px-3 py-2.5 border rounded-lg"
          :class="loc.text.status === 'lost-listed' ? 'bg-rose-50 border-rose-200' : 'bg-orange-50 border-orange-200'"
        >
          <div class="text-[11px] font-semibold mb-0.5" :class="loc.text.status === 'lost-listed' ? 'text-rose-900' : 'text-orange-900'">
            原書已佚 —— 以下不是原文
          </div>
          <p class="text-[11px] leading-relaxed break-words" :class="loc.text.status === 'lost-listed' ? 'text-rose-800' : 'text-orange-800'">
            <template v-if="loc.text.status === 'lost-listed'">
              本書無一字傳世，今日所知僅有書名，出處為<b>{{ loc.text.via }}</b>。
              本頁列出的是書目資訊與學界對它的討論，<b>不是</b>該書的內容。
            </template>
            <template v-else>
              本書原本已佚。此處所收出自<b>{{ loc.text.via }}</b>，
              是他書的引錄或內容提要。引用時必須標明轉引，不可逕作原書文句。
            </template>
          </p>
        </div>

        <!-- 敵證：引用限制寫在讀之前，不寫在註腳裡 -->
        <div v-else-if="loc.text.hostile" class="mt-3 px-3 py-2.5 bg-red-50 border border-red-200 rounded-lg">
          <div class="text-[11px] font-semibold text-red-900 mb-0.5">
            敵證 —— {{ HOSTILE_META[loc.text.hostile].zh }}
          </div>
          <p class="text-[11px] text-red-800 leading-relaxed break-words">
            {{ HOSTILE_META[loc.text.hostile].desc }}
            本篇作者<b>不是</b>摩尼教徒，寫作目的是反駁或查禁這個宗教。
            <template v-if="loc.text.via">所涉引文見：{{ loc.text.via }}。</template>
          </p>
        </div>
        <p v-else-if="loc.text.via" class="mt-3 text-[11px] text-rose-700 break-words">僅存於：{{ loc.text.via }}</p>

        <!-- 互見：摩尼教的互見不是「參看」，是同一本書的另一塊碎片 -->
        <div v-if="related.length" class="mt-3">
          <div class="text-[11px] text-gray-400 mb-1">同一部書的其他殘卷／相關條目</div>
          <div class="flex flex-wrap gap-1.5">
            <NuxtLink
              v-for="r in related"
              :key="r.text.slug"
              :to="`/manichaean/text/${r.text.slug}`"
              class="text-[11px] px-2 py-1 rounded-lg bg-white border border-gray-200 hover:border-amber-400 transition break-words"
            >
              <span class="text-gray-900">{{ r.text.title_zh }}</span>
              <span class="text-gray-400 ml-1">{{ r.canon.name }}</span>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- ───── 正文未上架：說清楚現況與可取之處，而不是給一個空頁 ───── -->
      <div v-if="!doc" class="bg-white border border-gray-200 rounded-xl p-5">
        <h2 class="text-sm font-bold text-gray-800 mb-2">正文尚未上架</h2>
        <p class="text-xs text-gray-500 leading-relaxed mb-4">
          本篇的書目已建立，逐段對照尚未抓取。下表是各欄的取源現況——
          它說的是「線上找不找得到可用來源」，不是「本站有沒有」。
        </p>
        <div class="space-y-2">
          <div v-for="c in COLS.filter(x => !isChinese || x.key !== 'zh')" :key="c.key" class="flex items-start gap-3">
            <span class="shrink-0 w-20 text-xs font-medium text-gray-700">{{ c.label }}</span>
            <span class="shrink-0 text-[11px] px-1.5 py-0.5 rounded" :class="COLUMN_META[cols[c.key]].cls">
              {{ COLUMN_META[cols[c.key]].zh }}
            </span>
            <span class="min-w-0 flex-1 text-[11px] text-gray-500 leading-relaxed break-words">{{ SOURCE_NOTE[c.key][cols[c.key]] }}</span>
          </div>
        </div>
      </div>

      <!-- ───── 逐段對照 ───── -->
      <template v-else>
        <div v-if="doc.pivot === 'none'" class="mb-4 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="text-[11px] font-semibold text-amber-900 mb-0.5">繁中直接譯自原文轉寫</div>
          <p class="text-[11px] text-amber-800 leading-relaxed break-words">
            本篇無可用的學術英譯，繁中係直接譯自原文轉寫，未經英譯中介，可信度低於其他各篇。{{ doc.pivot_note }}
          </p>
        </div>
        <p
          v-else-if="doc.pivot_note"
          class="mb-4 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px] text-gray-500 leading-relaxed break-words"
        >{{ doc.pivot_note }}</p>

        <!-- 欄位切換 -->
        <div v-if="visibleCols.length > 1" class="flex flex-wrap items-center gap-2 mb-4">
          <button
            v-for="c in visibleCols"
            :key="c.key"
            class="text-xs px-2.5 py-1 rounded-lg border transition"
            :class="shown.includes(c.key)
              ? 'bg-slate-900 text-amber-300 border-slate-900'
              : 'bg-white text-gray-500 border-gray-300 hover:border-amber-400'"
            @click="toggle(c.key)"
          >{{ c.label }}</button>
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
                  v-if="seg[c.key]"
                  class="text-sm leading-relaxed break-words whitespace-pre-line"
                  :class="c.key === 'orig'
                    ? (isChinese ? 'text-gray-800 text-base leading-loose' : 'text-gray-800 italic')
                    : 'text-gray-700'"
                >{{ seg[c.key] }}</p>
                <p v-else class="text-sm text-gray-300">—</p>
              </div>
            </div>
            <p v-if="seg.note" class="px-4 py-1.5 text-[11px] text-gray-500 bg-slate-50 border-t border-gray-100 break-words">{{ seg.note }}</p>
          </div>
        </div>

        <!-- 取源與體例 -->
        <div class="mt-8 text-[11px] text-gray-400 leading-relaxed border-t border-gray-200 pt-4 space-y-1">
          <p v-if="doc.orig_source"><b class="text-gray-500">原文</b>　{{ doc.orig_source }}<a v-if="doc.orig_url" :href="doc.orig_url" target="_blank" rel="noopener" class="ml-1 text-amber-700 hover:underline">↗</a></p>
          <p v-if="doc.en_source"><b class="text-gray-500">英譯</b>　{{ doc.en_translator ? `${doc.en_translator}，` : '' }}{{ doc.en_source }}<a v-if="doc.en_url" :href="doc.en_url" target="_blank" rel="noopener" class="ml-1 text-amber-700 hover:underline">↗</a></p>
          <p><b class="text-gray-500">授權</b>　{{ doc.licence }}</p>
          <p>
            <b class="text-gray-500">體例</b>
            段號一律沿用學界既有的引用式（科普特抄本用頁行號、吐魯番殘卷用館藏編號＋葉面＋行、
            漢文用《大正藏》冊頁欄行），本站不自編段號。
            <template v-if="isChinese">本藏原文即中文，單欄原樣呈現，不另譯成現代中文。</template>
            <template v-else>繁中為本站逐段翻譯。</template>
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { COLUMN_META, HOSTILE_META, STATUS_META, columnsOf, findText, relatedOf } from '~/data/manichaean'
import { loadText, SINGLE_COLUMN_CANON } from '~/data/manichaean/sources'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const loc = computed(() => findText(slug.value))

const { data: doc } = await useAsyncData(
  () => `mani-text-${slug.value}`,
  () => loadText(slug.value).then(d => d ?? null),
  { watch: [slug] },
)

useHead(() => ({ title: `${loc.value?.text.title_zh ?? '摩尼教經典'} — 摩尼教經典` }))

// 本藏經的常態不是全本：不設 status 時預設殘篇。
const status = computed(() => STATUS_META[loc.value?.text.status ?? 'fragment'])
const cols = computed(() => (loc.value ? columnsOf(loc.value.text, loc.value.division) : { orig: 'none', en: 'none', zh: 'none' } as const))
const backTo = computed(() => (loc.value ? `/manichaean/${loc.value.canon.key}/${loc.value.volume.key}` : '/manichaean'))
const backLabel = computed(() => loc.value?.volume.name ?? '摩尼教經典')
const translated = computed(() => doc.value?.segments.filter(s => (s.zh ?? '').trim()).length ?? 0)
const related = computed(() => (loc.value ? relatedOf(loc.value.text) : []))

/** 🚨 漢文藏原文即中文：不出繁中欄。為版面整齊而把唐代漢文再「翻譯」一次，
 *  那不是對照，是改寫。見 data/manichaean/chinese.ts 檔首。 */
const isChinese = computed(() => loc.value?.canon.key === SINGLE_COLUMN_CANON)

const COLS = [
  { key: 'orig' as const, label: '原文' },
  { key: 'en' as const, label: '英譯' },
  { key: 'zh' as const, label: '繁體中文' },
]

// 空欄不出，免得整欄都是「—」；漢文藏額外排除繁中欄。
const visibleCols = computed(() =>
  COLS.filter(c => !(isChinese.value && c.key === 'zh'))
    .filter(c => doc.value?.segments.some(s => (s[c.key] ?? '').trim().length > 0)))

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

// 未上架時，逐欄說明「線上找不找得到」
const SOURCE_NOTE: Record<'orig' | 'en' | 'zh', Record<string, string>> = {
  orig: {
    ready: '已抓取並逐段對齊。',
    available: '線上有可用來源：吐魯番各語言見 IAMS《東方摩尼教選輯》與柏林數位吐魯番檔案；漢文三經見《大正藏》第 54 冊與維基文庫。待抓取。',
    copyright: '僅有版權內的現代校訂本（如波洛茨基、奧爾伯里、加德納諸家），不能使用。',
    none: '線上查無可用的原文或轉寫。',
  },
  en: {
    ready: '已抓取並逐段對齊。',
    available: '線上有可用英譯：IAMS《東方摩尼教選輯》四冊與斯克耶爾沃《摩尼教文獻譯注》為開放取用；教父駁論見 ANF／NPNF，屬公有領域。待抓取。',
    copyright: '通行英譯仍在版權內（加德納的《凱法萊亞》、道奇的《群書類述》等），不能作為對照欄底本。',
    none: '查無可用的英譯。',
  },
  zh: {
    ready: '已逐段翻譯上架。',
    available: '待翻譯。',
    copyright: '既有中譯在版權內，不採用；本站另行自譯。',
    none: '無既有中譯。本站以英譯為中介自譯，尚未排入。',
  },
}
</script>
