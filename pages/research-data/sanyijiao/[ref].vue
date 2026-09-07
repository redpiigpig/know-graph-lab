<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader
      :title="entry ? (entry.title_zh || entry.title) : '三夷教研究資料'"
      :back="{ to: '/research-data/sanyijiao', label: '三夷教研究資料' }"
      container-class="max-w-6xl"
    >
      <template #actions>
        <span v-if="doc" class="text-xs text-gray-400">{{ doc.segments.length }} 段 · 已譯 {{ translated }}</span>
      </template>
    </AppHeader>

    <div v-if="!entry" class="flex items-center justify-center py-24 text-gray-400 text-sm">找不到這一筆。</div>

    <div v-else class="max-w-6xl mx-auto px-6 py-8">
      <!-- 書目 -->
      <div class="mb-6">
        <div class="flex items-baseline gap-2 flex-wrap mb-1">
          <h1 class="text-xl font-bold text-gray-900 break-words">{{ entry.title }}</h1>
          <span class="text-[11px] px-2 py-0.5 rounded" :class="RELIGION_META[entry.religion].cls">
            {{ RELIGION_META[entry.religion].glyph }} {{ RELIGION_META[entry.religion].label }}
          </span>
          <span class="text-[11px] px-2 py-0.5 rounded" :class="FULLTEXT_LABEL[entry.fulltext].cls">
            {{ FULLTEXT_LABEL[entry.fulltext].zh }}
          </span>
        </div>
        <div v-if="entry.title_zh" class="text-sm text-gray-500 break-words mb-2">{{ entry.title_zh }}</div>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-[11px] text-gray-600 mb-3">
          <div class="flex gap-2 sm:col-span-2"><dt class="shrink-0 text-gray-400">作者</dt><dd class="break-words">{{ entry.authors }}</dd></div>
          <div v-if="entry.year" class="flex gap-2"><dt class="shrink-0 text-gray-400">年份</dt><dd>{{ entry.year }}</dd></div>
          <div v-if="entry.venue" class="flex gap-2"><dt class="shrink-0 text-gray-400">出處</dt><dd class="break-words">{{ entry.venue }}</dd></div>
          <div class="flex gap-2"><dt class="shrink-0 text-gray-400">類型</dt><dd>{{ KIND_LABEL[entry.kind] }}</dd></div>
          <div class="flex gap-2"><dt class="shrink-0 text-gray-400">語言</dt><dd>{{ LANG_LABEL[entry.lang] ?? entry.lang }}</dd></div>
        </dl>

        <p v-if="entry.note" class="text-sm text-gray-700 leading-relaxed break-words bg-white border border-gray-200 rounded-xl p-4">{{ entry.note }}</p>

        <!-- 互見：必須並讀者（如大明國號之爭的兩造） -->
        <NuxtLink
          v-if="seealso"
          :to="`/research-data/sanyijiao/${seealso.ref}`"
          class="inline-flex items-baseline gap-1.5 mt-3 text-[11px] px-3 py-1.5 rounded-full border border-stone-300 hover:border-stone-500 transition break-words"
        >
          <span class="text-stone-500">必須並讀 →</span>
          <span class="font-medium text-stone-800">{{ seealso.title }}</span>
          <span class="text-stone-500">{{ seealso.authors }}</span>
        </NuxtLink>

        <a
          v-if="entry.url"
          :href="entry.url" target="_blank" rel="noopener"
          class="inline-block mt-3 ml-2 text-[11px] text-stone-700 hover:underline"
        >取源連結 ↗</a>
      </div>

      <!-- ───── 全文未上架 ───── -->
      <div v-if="!doc" class="bg-white border border-gray-200 rounded-xl p-5">
        <h2 class="text-sm font-bold text-gray-800 mb-2">全文尚未上架</h2>
        <p class="text-xs text-gray-500 leading-relaxed break-words">{{ PENDING_NOTE[entry.fulltext] }}</p>
      </div>

      <!-- ───── 逐段對照 ───── -->
      <template v-else>
        <!-- 🚨 欄數由原文語言決定，不可只出中譯欄 -->
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <button
            v-for="c in columns"
            :key="c.key"
            class="text-xs px-2.5 py-1 rounded-lg border transition"
            :class="shown.includes(c.key)
              ? 'bg-stone-800 text-white border-stone-800'
              : 'bg-white text-gray-500 border-gray-300 hover:border-stone-400'"
            @click="toggle(c.key)"
          >{{ c.label }}</button>
          <span v-if="columns.length === 1" class="text-[11px] text-gray-400">
            中文原著，原樣呈現（無翻譯）
          </span>
          <span v-else-if="columns.length === 3" class="text-[11px] text-gray-400">
            原文非英文，故作三欄：原文／英譯／繁中
          </span>
        </div>

        <div class="space-y-2">
          <div
            v-for="(seg, i) in doc.segments"
            :key="i"
            class="bg-white border border-gray-200 rounded-xl overflow-hidden"
          >
            <div v-if="seg.ref" class="px-3 py-1 bg-slate-50 border-b border-gray-100 text-[11px] font-mono text-gray-500">
              {{ seg.ref }}
            </div>
            <div class="grid" :class="gridCls">
              <div
                v-for="c in columns.filter(x => shown.includes(x.key))"
                :key="c.key"
                class="px-4 py-3 border-gray-100 [&:not(:last-child)]:border-b md:[&:not(:last-child)]:border-b-0 md:[&:not(:last-child)]:border-r"
              >
                <div class="text-[10px] text-gray-400 mb-1 md:hidden">{{ c.label }}</div>
                <p
                  v-if="(seg as any)[c.key]"
                  class="text-sm leading-relaxed break-words whitespace-pre-line"
                  :class="c.key === 'zh' ? 'text-gray-800' : 'text-gray-700'"
                >{{ (seg as any)[c.key] }}</p>
                <p v-else class="text-sm text-gray-300">—</p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-8 text-[11px] text-gray-400 leading-relaxed border-t border-gray-200 pt-4 space-y-1">
          <p v-if="doc.source"><b class="text-gray-500">取源</b>　{{ doc.source }}</p>
          <p><b class="text-gray-500">體例</b>　繁中為本站逐段翻譯，以原文為底。原文欄一律並排顯示——只有中譯的對照無從查證。</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  FULLTEXT_LABEL, KIND_LABEL, LANG_LABEL, RELIGION_META,
  columnsFor, findEntry,
} from '~/data/sanyijiao'
import type { ZsFulltext } from '~/data/sanyijiao'

definePageMeta({ middleware: 'auth' })

interface Seg { ref?: string; orig?: string; en?: string; zh?: string }
interface Doc { source?: string; segments: Seg[] }

const route = useRoute()
const refKey = computed(() => String(route.params.ref))
const entry = computed(() => findEntry(refKey.value))
const seealso = computed(() => (entry.value?.seealso ? findEntry(entry.value.seealso) : undefined))

useHead(() => ({ title: `${entry.value?.title_zh || entry.value?.title || '三夷教研究資料'} — 三夷教研究資料` }))

// 全文按需載入。目錄可能整個不存在（尚無任何全文），glob 空集合是合法的。
const TEXTS = import.meta.glob('~/public/content/research-data/sanyijiao/texts/*.json') as
  Record<string, () => Promise<{ default: Doc }>>

const { data: doc } = await useAsyncData(
  () => `sanyijiao-${refKey.value}`,
  async () => {
    const hit = Object.keys(TEXTS).find(p => p.endsWith(`/${refKey.value}.json`))
    if (!hit) return null
    return (await TEXTS[hit]!()).default
  },
  { watch: [refKey] },
)

const translated = computed(() => doc.value?.segments.filter(s => (s.zh ?? '').trim()).length ?? 0)

// 🚨 欄數由原文語言決定（user 2026-09-06 定）：英文→兩欄；非英文→三欄；中文→一欄。
const columns = computed(() => columnsFor(entry.value?.lang ?? 'en'))
const shown = ref<string[]>([])
watchEffect(() => { shown.value = columns.value.map(c => c.key) })

function toggle(key: string) {
  if (shown.value.includes(key)) {
    if (shown.value.length > 1) shown.value = shown.value.filter(c => c !== key)
  } else {
    shown.value = columns.value.map(c => c.key).filter(k => shown.value.includes(k) || k === key)
  }
}

const gridCls = computed(() => ({
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-3',
}[shown.value.length] ?? 'grid-cols-1'))

const PENDING_NOTE: Record<ZsFulltext, string> = {
  ready: '已上架但載入不到——這代表全文檔的檔名與書目的 ref 對不上，請檢查。',
  held: '**書已在 Drive 電子圖書館**，尚未轉錄切段。轉錄後即成逐段對照。',
  open: '網路有開放取用的全文，尚未抓取。',
  library: '需館藏或付費資料庫。多數已列入 z-lib 獵表，由每日排程逐步取得；取得後轉為逐段對照。',
  print: '僅有紙本，須掃描後 OCR。',
  none: '查無電子全文。',
}
</script>
