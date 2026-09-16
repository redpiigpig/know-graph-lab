<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="摩尼教經典" :back="{ to: '/scripture-canon/manichaeism', label: '摩尼教' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ totalVolumes }} 卷 · {{ tally.total }} 種</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">☀️ 摩尼教經典</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          一個**死透了的宗教**留下的全部文獻，分五藏收錄：摩尼親撰的正典書目（正藏）、
          埃及與北非出土的科普特文與希臘文抄本、吐魯番出土的中古伊朗語與回鶻語寫本、
          敦煌與福建的漢文文獻，以及反對者所記（附錄，非經典）。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          <b>分藏原則</b>：正藏按<b>書目</b>立卷——摩尼自訂的七部大經雖無一部傳世，仍照書目列出，
          空著比不列好；續藏按<b>出土語言與地點</b>立卷，因為摩尼教文獻的存世形態本來就是語言群。
          同一部書在四個地方各存一塊殘片，以互見相連，不強行併條。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-1">
          <b>斷限</b>：{{ TERMINUS.from }} 起，止於<b>{{ TERMINUS.to }}</b>。{{ TERMINUS.note }}
        </p>

        <div class="flex items-center gap-2 mt-4">
          <input
            v-model="q"
            type="search"
            placeholder="🔍 搜尋篇章、抄本編號、出土地或卷名…"
            class="flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400"
          />
          <NuxtLink
            to="/manichaean/about"
            class="shrink-0 text-sm font-medium text-amber-800 bg-white border border-amber-200 hover:border-amber-400 rounded-xl px-4 py-2 transition"
          >📖 凡例</NuxtLink>
        </div>
      </div>

      <!-- 搜尋結果 -->
      <section v-if="q.trim()" class="mb-10">
        <h2 class="text-sm font-bold text-gray-700 mb-2">搜尋「{{ q }}」— {{ results.length }} 筆</h2>
        <div v-if="!results.length" class="text-sm text-gray-400 px-4 py-6 bg-white border border-gray-200 rounded-xl">
          查無此篇。
        </div>
        <div v-else class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <NuxtLink
            v-for="loc in results.slice(0, 60)"
            :key="loc.text.slug"
            :to="`/manichaean/text/${loc.text.slug}`"
            class="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 transition"
          >
            <span class="shrink-0 text-[11px] font-mono text-gray-400 w-24 truncate">{{ loc.text.siglum }}</span>
            <span class="min-w-0 flex-1 text-sm text-gray-900 truncate">{{ loc.text.title_zh }}</span>
            <span class="shrink-0 text-[11px] text-gray-400 truncate max-w-[10rem]">{{ loc.canon.name }}‧{{ loc.volume.name }}</span>
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <!-- 存世狀態：本藏經的核心事實 -->
        <div class="mb-6 p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <div class="text-sm font-bold text-amber-300 mb-1">存世狀態一覽</div>
          <p class="text-[11px] text-slate-300 leading-relaxed mb-3">
            摩尼是宗教史上第一個親手寫下並封定正典的創教者。他明白地說，前面的使徒都沒有親筆寫下教導，
            所以他們的教會都走樣了，而他的不會。<b class="text-amber-300">結果是他親撰的七部大經，今天沒有一部傳世。</b>
            這張表就是那句話的結局。
          </p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(n, k) in statusTally"
              :key="k"
              class="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700"
            >
              <span class="text-[11px] text-slate-300">{{ STATUS_META[k].zh }}</span>
              <span class="ml-1.5 text-sm font-bold tabular-nums text-amber-300">{{ n }}</span>
            </div>
          </div>
        </div>

        <!-- 三欄取源現況 -->
        <div class="mb-8 p-4 bg-white border border-gray-200 rounded-xl">
          <div class="text-sm font-bold text-gray-800 mb-1">三欄取源現況</div>
          <p class="text-[11px] text-gray-500 leading-relaxed mb-3">
            這張表說的是「線上找不找得到可用來源」，不是「本站已經有了」。
            摩尼教文獻的取源條件兩極：吐魯番那一藏有國際摩尼教研究學會開放取用的選輯，原文與英譯並排可直接用；
            科普特那一藏的校本與英譯幾乎全在版權內。
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div v-for="col in COLUMN_ROWS" :key="col.key">
              <div class="text-xs font-semibold text-gray-700 mb-1.5">{{ col.label }}</div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="state in STATE_ORDER"
                  :key="state"
                  v-show="tally[col.key][state]"
                  class="text-[11px] px-1.5 py-0.5 rounded tabular-nums"
                  :class="COLUMN_META[state].cls"
                >{{ COLUMN_META[state].zh }} {{ tally[col.key][state] }}</span>
              </div>
              <p class="text-[10px] text-gray-400 leading-relaxed mt-1 break-words">{{ col.note }}</p>
            </div>
          </div>
        </div>

        <!-- 存世狀態圖例 -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-8 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
          <span class="text-gray-500">存世狀態：</span>
          <span v-for="(m, k) in STATUS_META" :key="k" class="flex items-center gap-1.5">
            <span class="inline-block w-2.5 h-2.5 rounded-full" :class="m.dotCls" />
            <span :class="m.titleCls">{{ m.zh }}</span>
          </span>
        </div>

        <!-- 五藏 -->
        <section v-for="canon in CANONS" :id="canon.key" :key="canon.key" class="mb-12 scroll-mt-20">
          <div class="flex items-center gap-3 mb-2">
            <div
              class="shrink-0 w-11 h-11 rounded-xl flex items-center justify-center text-2xl font-serif"
              :class="canon.scriptural ? 'bg-slate-900 text-amber-300' : 'bg-stone-500 text-white'"
            >{{ canon.glyph }}</div>
            <div class="min-w-0">
              <h2 class="text-lg font-bold text-gray-900 leading-tight break-words">{{ canon.name }}</h2>
              <div class="text-[11px] text-gray-400 break-words">{{ canon.name_en }} · {{ canon.subtitle }}</div>
            </div>
            <span class="ml-auto shrink-0 text-[11px] px-2 py-0.5 rounded bg-amber-50 text-amber-800 tabular-nums">
              {{ canon.volumes.length }} 卷 · {{ canonTextCount(canon) }} 種
            </span>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed mb-1 break-words">{{ canon.summary }}</p>
          <p class="text-[11px] text-gray-400 mb-5">{{ canon.language }}　·　{{ canon.era }}</p>

          <div v-for="part in canon.parts" :key="part.key" class="mb-5">
            <div class="flex items-baseline gap-2 mb-1 border-b border-amber-200 pb-1.5">
              <h3 class="text-sm font-bold text-amber-900">{{ part.label }}</h3>
              <span v-if="part.label_en" class="text-[11px] text-gray-400">{{ part.label_en }}</span>
            </div>
            <p v-if="part.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 break-words">{{ part.desc }}</p>

            <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
              <NuxtLink
                v-for="v in volumesOf(canon, part)"
                :key="v.key"
                :to="`/manichaean/${canon.key}/${v.key}`"
                class="flex items-center gap-3.5 px-4 py-3 hover:bg-slate-50 transition group"
              >
                <div class="shrink-0 w-9 h-9 rounded-lg bg-slate-900 text-amber-300 flex items-center justify-center text-sm font-serif">{{ v.sigil }}</div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-baseline gap-2 flex-wrap">
                    <span class="font-semibold text-gray-900 group-hover:text-amber-800 transition">{{ v.name }}</span>
                    <span v-if="v.name_orig" class="text-[11px] text-gray-400 italic">{{ v.name_orig }}</span>
                  </div>
                  <p v-if="v.provenance" class="text-[11px] text-amber-700 leading-relaxed mt-0.5 line-clamp-1 break-words">出土／館藏：{{ v.provenance }}</p>
                  <p class="text-xs text-gray-500 leading-relaxed mt-0.5 line-clamp-2 break-words">{{ v.summary }}</p>
                </div>
                <div class="shrink-0 text-right text-[11px] text-gray-400 tabular-nums">
                  <div>{{ volumeTextCount(v) }} 篇</div>
                  <div v-if="v.extent" class="truncate max-w-[6rem]">{{ v.extent }}</div>
                </div>
              </NuxtLink>
            </div>
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
  volumesOf,
} from '~/data/manichaean'
import type { ColumnState, TextStatus } from '~/data/manichaean'

definePageMeta({ middleware: 'auth' })
useHead({ title: '摩尼教經典 — Know Graph Lab' })

const q = ref('')
const results = computed(() => (q.value.trim() ? searchTexts(q.value) : []))

const tally = tallyColumns()
const statusTally = tallyStatus() as Record<TextStatus, number>
const totalVolumes = CANONS.reduce((n, c) => n + c.volumes.length, 0)

const STATE_ORDER: ColumnState[] = ['ready', 'available', 'copyright', 'none']

const COLUMN_ROWS = [
  {
    key: 'orig' as const,
    label: '原文（轉寫）',
    note: '吐魯番各語言有 IAMS《東方摩尼教選輯》開放取用；漢文三經在《大正藏》第 54 冊，公有領域；科普特文校本多在版權內。',
  },
  {
    key: 'en' as const,
    label: '英譯',
    note: 'IAMS 選輯四冊與斯克耶爾沃《摩尼教文獻譯注》可用；教父駁論走 ANF／NPNF 公有領域；加德納的《凱法萊亞》英譯在版權內。',
  },
  {
    key: 'zh' as const,
    label: '繁體中文',
    note: '漢文藏本身即中文（單欄呈現，不另翻）。其餘各藏為本站自譯，以英譯為中介，逐篇補齊。',
  },
]
</script>
