<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="古近東大藏經" :back="{ to: '/scripture-canon/near-east', label: '古近東宗教' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ totalVolumes }} 卷 · {{ tally.total }} 種</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🏺 古近東大藏經</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          埃及、蘇美、巴比倫與亞述、赫梯與胡里特、烏加里特、迦南與亞蘭、阿拉伯、埃蘭與高地——
          文字發明以來最早的一批宗教文獻，按文明分八藏，另附希臘羅馬與後世作者的外部記述。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          <b>分藏原則</b>：這不是一個宗教，是七八個。分藏的第一判準是寫經的文字與語言，最終判準是它屬於哪一套神廟體系；
          不調和、不比附，不編一套「近東神話」綜合版。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-1">
          <b>斷限</b>：{{ TERMINUS.from }}起，<b>{{ TERMINUS.to }}</b>。{{ TERMINUS.note }}
        </p>

        <div class="flex items-center gap-2 mt-4">
          <input
            v-model="q"
            type="search"
            placeholder="🔍 搜尋篇名、編號、神名、出土地或經文對位…"
            class="min-w-0 flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-teal-400"
          />
          <NuxtLink
            to="/near-east/about"
            class="shrink-0 text-sm font-medium text-teal-800 bg-white border border-teal-200 hover:border-teal-400 rounded-xl px-4 py-2 transition"
          >📖 凡例</NuxtLink>
        </div>
      </div>

      <!-- 搜尋結果 -->
      <section v-if="q.trim()" class="mb-10">
        <h2 class="text-sm font-bold text-gray-700 mb-2">搜尋「{{ q }}」— {{ results.length }} 筆</h2>
        <div v-if="!results.length" class="text-sm text-gray-400 px-4 py-6 bg-white border border-gray-200 rounded-xl">查無此篇。</div>
        <div v-else class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <NuxtLink
            v-for="loc in results.slice(0, 80)"
            :key="loc.text.slug"
            :to="`/near-east/${loc.canon.key}/${loc.volume.key}#${loc.text.slug}`"
            class="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 transition"
          >
            <span class="shrink-0 inline-block w-2 h-2 rounded-full" :class="STATUS_META[loc.text.status ?? 'composite'].dotCls" />
            <span class="min-w-0 flex-1 text-sm text-gray-900 truncate">{{ loc.text.title_zh }}</span>
            <span class="hidden sm:inline shrink-0 text-[11px] font-mono text-gray-400 truncate max-w-[9rem]">{{ loc.text.siglum }}</span>
            <span class="shrink-0 text-[11px] text-gray-400 truncate max-w-[8rem]">{{ loc.volume.sigil }}‧{{ loc.volume.name }}</span>
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <!-- 存世狀態 -->
        <div class="mb-6 p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <div class="text-sm font-bold text-teal-300 mb-1">存世狀態一覽</div>
          <p class="text-[11px] text-slate-300 leading-relaxed mb-3">
            「吉伽美什史詩」不是一部古人手上拿得到的書，是現代學者從兩千年間幾百塊泥板綴合出來的學術物件。
            <b class="text-teal-300">綴合本</b>是古近東大型文學作品的常態；完整傳世的單一抄本反而少見。
          </p>
          <div class="flex flex-wrap gap-2">
            <div v-for="k in STATUS_ORDER" v-show="statusTally[k]" :key="k" class="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700">
              <span class="text-[11px] text-slate-300">{{ STATUS_META[k].zh }}</span>
              <span class="ml-1.5 text-sm font-bold tabular-nums text-teal-300">{{ statusTally[k] }}</span>
            </div>
          </div>
        </div>

        <!-- 三欄取源現況 -->
        <div class="mb-8 p-4 bg-white border border-gray-200 rounded-xl">
          <div class="text-sm font-bold text-gray-800 mb-1">三欄取源現況</div>
          <p class="text-[11px] text-gray-500 leading-relaxed mb-3">
            這張表說的是「線上找不找得到可用來源」，不是「本站已經有了」。目前本藏經只建了書目，三欄正文尚未上架。
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div v-for="col in COLUMN_ROWS" :key="col.key">
              <div class="text-xs font-semibold text-gray-700 mb-1.5">{{ col.label }}</div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="state in STATE_ORDER"
                  v-show="tally[col.key][state]"
                  :key="state"
                  class="text-[11px] px-1.5 py-0.5 rounded tabular-nums"
                  :class="COLUMN_META[state].cls"
                >{{ COLUMN_META[state].zh }} {{ tally[col.key][state] }}</span>
              </div>
              <p class="text-[10px] text-gray-400 leading-relaxed mt-1 break-words">{{ col.note }}</p>
            </div>
          </div>
        </div>

        <!-- 圖例 -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-8 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
          <span class="text-gray-500">存世狀態：</span>
          <span v-for="k in STATUS_ORDER" :key="k" class="flex items-center gap-1.5" :title="STATUS_META[k].desc">
            <span class="inline-block w-2.5 h-2.5 rounded-full" :class="STATUS_META[k].dotCls" />
            <span :class="STATUS_META[k].titleCls">{{ STATUS_META[k].zh }}</span>
          </span>
        </div>

        <!-- 藏目錄 -->
        <nav class="flex flex-wrap gap-1.5 mb-8">
          <a
            v-for="canon in CANONS"
            :key="canon.key"
            :href="`#${canon.key}`"
            class="text-xs px-2.5 py-1 rounded-lg border bg-white hover:border-teal-400 transition"
            :class="canon.scriptural ? 'border-gray-200 text-gray-700' : 'border-stone-200 text-stone-500'"
          >{{ canon.glyph }} {{ canon.name }}</a>
        </nav>

        <!-- 各藏 -->
        <section v-for="canon in CANONS" :id="canon.key" :key="canon.key" class="mb-12 scroll-mt-20">
          <div class="flex items-center gap-3 mb-2">
            <div
              class="shrink-0 w-11 h-11 rounded-xl flex items-center justify-center text-2xl font-serif"
              :class="canon.scriptural ? 'bg-slate-900 text-teal-300' : 'bg-stone-500 text-white'"
            >{{ canon.glyph }}</div>
            <div class="min-w-0">
              <h2 class="text-lg font-bold text-gray-900 leading-tight break-words">{{ canon.name }}</h2>
              <div class="text-[11px] text-gray-400 break-words">{{ canon.name_en }} · {{ canon.subtitle }}</div>
            </div>
            <span class="ml-auto shrink-0 text-[11px] px-2 py-0.5 rounded bg-teal-50 text-teal-800 tabular-nums">
              {{ canon.volumes.length }} 卷 · {{ canonTextCount(canon) }} 種
            </span>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed mb-1 break-words">{{ canon.summary }}</p>
          <p class="text-[11px] text-gray-400 mb-1 break-words">{{ canon.language }}　·　{{ canon.era }}</p>
          <p class="text-[11px] text-teal-700 mb-4 break-words">下限：{{ canon.terminus }}</p>

          <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
            <NuxtLink
              v-for="v in canon.volumes"
              :key="v.key"
              :to="`/near-east/${canon.key}/${v.key}`"
              class="flex items-center gap-3.5 px-4 py-3 hover:bg-slate-50 transition group"
            >
              <div class="shrink-0 min-w-[2.75rem] h-9 px-1.5 rounded-lg bg-slate-900 text-teal-300 flex items-center justify-center text-xs font-serif whitespace-nowrap">{{ v.sigil }}</div>
              <div class="min-w-0 flex-1">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <span class="font-semibold text-gray-900 group-hover:text-teal-800 transition break-words">{{ v.name }}</span>
                  <span class="text-[11px] text-gray-400 break-words">{{ v.name_en }}</span>
                </div>
                <p class="text-xs text-gray-500 leading-relaxed mt-0.5 line-clamp-2 break-words">{{ v.summary }}</p>
              </div>
              <div class="shrink-0 text-right text-[11px] text-gray-400 tabular-nums">
                <div>{{ volumeTextCount(v) }} 篇</div>
                <div v-if="v.era" class="hidden sm:block truncate max-w-[8rem]">{{ v.era }}</div>
              </div>
            </NuxtLink>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  CANONS,
  COLUMN_META,
  STATUS_META,
  TERMINUS,
  canonTextCount,
  searchTexts,
  tallyColumns,
  tallyStatus,
  volumeTextCount,
} from '~/data/near-east'
import type { ColumnState, TextStatus } from '~/data/near-east'

definePageMeta({ middleware: 'auth' })
useHead({ title: '古近東大藏經 — Know Graph Lab' })

const q = ref('')
const results = computed(() => (q.value.trim() ? searchTexts(q.value) : []))

const tally = tallyColumns()
const statusTally = tallyStatus() as Record<TextStatus, number>
const totalVolumes = CANONS.reduce((n, c) => n + c.volumes.length, 0)

const STATUS_ORDER: TextStatus[] = ['whole', 'composite', 'fragment', 'inscription', 'lost-cited', 'lost-listed']
const STATE_ORDER: ColumnState[] = ['ready', 'available', 'copyright', 'none']

const COLUMN_ROWS = [
  {
    key: 'orig' as const,
    label: '原文（轉寫）',
    note: '蘇美用牛津 ETCSL；阿卡德用 eBL 與 ORACC（CC BY-SA）；埃及用柏林《埃及語辭典》TLA（CC BY-SA）；赫梯用美因茲 Hethitologie-Portal。',
  },
  {
    key: 'en' as const,
    label: '英譯',
    note: '蘇美有 ETCSL 散文譯本；巴比倫與埃及有二十世紀初的公有領域譯本（King、Budge 等）；赫梯、烏加里特的現代英譯幾乎全在版權內。',
  },
  {
    key: 'zh' as const,
    label: '繁體中文',
    note: '本站自譯，逐篇補齊。譯名先過 /translation-glossary。',
  },
]
</script>
