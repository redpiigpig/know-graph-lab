<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="祆教經典" :back="{ to: '/scripture-canon/zoroastrianism', label: '祆教' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ totalVolumes }} 卷 · {{ tally.total }} 種</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🔥 祆教經典</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          現存最古老的一神—二元信仰的全部傳世文獻，分四藏收錄：阿維斯陀語的原典（正藏）、
          伊斯蘭征服後以中古波斯語寫成的經典化著述（續典）、帕西社群流散中的白話宗教書與族史（外典），
          以及波斯兩大王朝的王室石刻（附錄，非經典）。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          <b>分部原則</b>：照薩珊祭司傳下來的禮儀單位，本站不另立卷次。耶斯那 72 章、維斯佩拉德 24 章、
          祓魔法典 22 章、耶什特 21 首——這些數目今天仍在火廟裡被照著誦。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-1">
          <b>斷限</b>：{{ TERMINUS.from }} 起，<b>{{ TERMINUS.to }}</b>。{{ TERMINUS.note }}
        </p>

        <div class="flex items-center gap-2 mt-4">
          <input
            v-model="q"
            type="search"
            placeholder="🔍 搜尋篇章、編號或卷名（中／轉寫）…"
            class="flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400"
          />
          <NuxtLink
            to="/avesta/about"
            class="shrink-0 text-sm font-medium text-orange-800 bg-white border border-orange-200 hover:border-orange-400 rounded-xl px-4 py-2 transition"
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
            :to="`/avesta/text/${loc.text.slug}`"
            class="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 transition"
          >
            <span class="shrink-0 text-[11px] font-mono text-gray-400 w-16 truncate">{{ loc.text.siglum }}</span>
            <span class="min-w-0 flex-1 text-sm text-gray-900 truncate">{{ loc.text.title_zh }}</span>
            <span class="shrink-0 text-[11px] text-gray-400 truncate max-w-[10rem]">{{ loc.canon.name }}‧{{ loc.volume.name }}</span>
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <!-- 三欄取源現況：本藏經最誠實的一張表 -->
        <div class="mb-8 p-4 bg-white border border-gray-200 rounded-xl">
          <div class="text-sm font-bold text-gray-800 mb-1">三欄取源現況</div>
          <p class="text-[11px] text-gray-500 leading-relaxed mb-3">
            這張表說的是「哪一欄真的有東西」。祆教經典的中譯在華語世界近乎空白——
            唯一有份量的《阿維斯塔》中譯本是選編本、簡體且在版權內，不能作為對照欄底本，
            因此繁中欄一律為本站自譯，逐篇補齊。
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
          <span class="text-gray-400 ml-auto">傳世的阿維斯陀僅約原本的四分之一。</span>
        </div>

        <!-- 四藏 -->
        <section v-for="canon in CANONS" :key="canon.key" class="mb-12">
          <div class="flex items-center gap-3 mb-2">
            <div
              class="shrink-0 w-11 h-11 rounded-xl text-white flex items-center justify-center text-2xl font-serif"
              :class="canon.scriptural ? 'bg-orange-900' : 'bg-stone-500'"
            >{{ canon.glyph }}</div>
            <div class="min-w-0">
              <h2 class="text-lg font-bold text-gray-900 leading-tight break-words">{{ canon.name }}</h2>
              <div class="text-[11px] text-gray-400 break-words">{{ canon.name_en }} · {{ canon.subtitle }}</div>
            </div>
            <span class="ml-auto shrink-0 text-[11px] px-2 py-0.5 rounded bg-orange-50 text-orange-800 tabular-nums">
              {{ canon.volumes.length }} 卷 · {{ canonTextCount(canon) }} 種
            </span>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed mb-1 break-words">{{ canon.summary }}</p>
          <p class="text-[11px] text-gray-400 mb-5">{{ canon.language }}　·　{{ canon.era }}</p>

          <div v-for="part in canon.parts" :key="part.key" class="mb-5">
            <div class="flex items-baseline gap-2 mb-1 border-b border-orange-200 pb-1.5">
              <h3 class="text-sm font-bold text-orange-900">{{ part.label }}</h3>
              <span v-if="part.label_en" class="text-[11px] text-gray-400">{{ part.label_en }}</span>
            </div>
            <p v-if="part.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2 break-words">{{ part.desc }}</p>

            <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
              <NuxtLink
                v-for="v in volumesOf(canon, part)"
                :key="v.key"
                :to="`/avesta/${canon.key}/${v.key}`"
                class="flex items-center gap-3.5 px-4 py-3 hover:bg-slate-50 transition group"
              >
                <div class="shrink-0 w-9 h-9 rounded-lg bg-orange-800 text-white flex items-center justify-center text-base font-serif">{{ v.sigil }}</div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-baseline gap-2 flex-wrap">
                    <span class="font-semibold text-gray-900 group-hover:text-orange-800 transition">{{ v.name }}</span>
                    <span v-if="v.name_orig" class="text-[11px] text-gray-400 italic">{{ v.name_orig }}</span>
                  </div>
                  <p v-if="v.liturgy" class="text-[11px] text-orange-700 leading-relaxed mt-0.5 line-clamp-1 break-words">誦於：{{ v.liturgy }}</p>
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
  volumeTextCount,
  volumesOf,
} from '~/data/avesta'
import type { ColumnState } from '~/data/avesta'

definePageMeta({ middleware: 'auth' })
useHead({ title: '祆教經典 — Know Graph Lab' })

const q = ref('')
const results = computed(() => (q.value.trim() ? searchTexts(q.value) : []))

const tally = tallyColumns()
const totalVolumes = CANONS.reduce((n, c) => n + c.volumes.length, 0)

const STATE_ORDER: ColumnState[] = ['ready', 'available', 'copyright', 'none']

const COLUMN_ROWS = [
  { key: 'orig' as const, label: '原文（轉寫）', note: 'avesta.org 蓋爾德納轉寫、TITUS 語料庫；巴列維文獻的轉寫線上零散，缺口主要在此。' },
  { key: 'en' as const, label: '英譯', note: '《東方聖書》八卷，全部公有領域。缺口在《丹卡爾德》第 3、6 卷——韋斯特未譯，現代譯本仍在版權內。' },
  { key: 'zh' as const, label: '繁體中文', note: '本站自譯，以英譯為中介。既有中譯僅一部簡體選編本且在版權內，不採用。' },
]
</script>
