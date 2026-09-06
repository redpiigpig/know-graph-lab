<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="三夷教研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🜂 三夷教研究資料</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          祆教、摩尼教、（日後）景教的二手研究：專書、期刊論文、學位論文與工具書條目。
          一手經典不在此，在
          <NuxtLink to="/avesta" class="text-orange-800 hover:underline">《祆教經典》</NuxtLink>。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          <b>為什麼研究合成一卡、經典卻分卡</b>：三教是三個獨立宗教，經典的編纂問題也根本不同
          （祆教的正典還活著，摩尼教的七部大經全佚、只能綴輯），故經典區分立；
          但研究文獻本來就大量跨教——林悟殊《中古三夷教辨證》一本涵蓋三教，林悟殊本人同時是
          祆教與摩尼教兩條線的權威——硬按教別拆開會把同一本書切成兩半。
        </p>
      </div>

      <!-- 取源現況：這一區最該說清楚的是「哪些真的拿得到」 -->
      <div class="mb-8 p-4 bg-white border border-gray-200 rounded-xl">
        <div class="flex items-baseline gap-2 mb-2">
          <span class="text-sm font-bold text-gray-800">全文取得現況</span>
          <span class="text-[11px] text-gray-400">共 {{ ENTRIES.length }} 筆書目</span>
        </div>
        <div class="flex flex-wrap gap-1.5 mb-2">
          <span
            v-for="k in FULLTEXT_ORDER"
            :key="k"
            v-show="tally[k]"
            class="text-[11px] px-2 py-0.5 rounded tabular-nums"
            :class="FULLTEXT_LABEL[k].cls"
          >{{ FULLTEXT_LABEL[k].zh }} {{ tally[k] }}</span>
        </div>
        <p class="text-[11px] text-gray-500 leading-relaxed break-words">
          「需館藏」多數已列入 z-lib 獵表，由每日排程逐步取得；
          <b class="text-gray-600">說的是「拿不拿得到」，不是「本站有沒有」</b>。
        </p>
      </div>

      <!-- 依宗教分區 -->
      <section v-for="rel in RELIGION_ORDER" :key="rel" class="mb-10">
        <div class="flex items-center gap-2.5 mb-1.5 border-b border-stone-300 pb-2">
          <span class="text-2xl">{{ RELIGION_META[rel].glyph }}</span>
          <h2 class="text-lg font-bold text-gray-900">{{ RELIGION_META[rel].label }}</h2>
          <span class="text-[11px] px-2 py-0.5 rounded tabular-nums" :class="RELIGION_META[rel].cls">
            {{ byReligion(rel).length }} 筆
          </span>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed mb-3 break-words">{{ RELIGION_META[rel].desc }}</p>

        <div v-for="theme in themesIn(rel)" :key="theme" class="mb-4">
          <div class="flex items-baseline gap-2 mb-1">
            <h3 class="text-sm font-bold text-stone-800">{{ THEME_META[theme].label }}</h3>
            <span class="text-[11px] text-gray-400">{{ byReligionTheme(rel, theme).length }}</span>
          </div>

          <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
            <NuxtLink
              v-for="e in byReligionTheme(rel, theme)"
              :key="e.ref"
              :to="`/research-data/sanyijiao/${e.ref}`"
              class="block px-4 py-3 hover:bg-slate-50 transition group"
            >
              <div class="flex items-start gap-3">
                <div class="min-w-0 flex-1">
                  <div class="flex items-baseline gap-2 flex-wrap">
                    <span class="text-sm font-medium text-gray-900 group-hover:underline break-words">{{ e.title }}</span>
                    <span v-if="e.title_zh" class="text-[11px] text-gray-500 break-words">{{ e.title_zh }}</span>
                  </div>
                  <div class="text-[11px] text-gray-500 mt-0.5 break-words">
                    {{ e.authors }}<span v-if="e.year">　{{ e.year }}</span><span v-if="e.venue">　{{ e.venue }}</span>
                  </div>
                  <p v-if="e.note" class="text-[11px] text-gray-500 leading-relaxed mt-1 line-clamp-2 break-words">{{ e.note }}</p>
                </div>
                <div class="shrink-0 flex flex-col items-end gap-1">
                  <span class="text-[10px] px-1.5 py-0.5 rounded" :class="FULLTEXT_LABEL[e.fulltext].cls">
                    {{ FULLTEXT_LABEL[e.fulltext].zh }}
                  </span>
                  <span class="text-[10px] text-gray-400">{{ KIND_LABEL[e.kind] }}　{{ LANG_LABEL[e.lang] ?? e.lang }}</span>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>

      <div class="text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>
          <b class="text-gray-500">語言呈現</b>　原文是英文者作英／繁中兩欄對照；原文非英文者作原文／英譯／繁中三欄。
          中文原著不譯，原樣呈現。<b class="text-gray-500">不出現只有中譯而無原文的頁面</b>——那種對照沒有查證價值。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ENTRIES, FULLTEXT_LABEL, KIND_LABEL, LANG_LABEL,
  RELIGION_META, THEME_META, tallyFulltext,
} from '~/data/sanyijiao'
import type { ZsFulltext, ZsReligion, ZsTheme } from '~/data/sanyijiao'

definePageMeta({ middleware: 'auth' })
useHead({ title: '三夷教研究資料 — Know Graph Lab' })

// 景教尚未收錄，不出空區
const RELIGION_ORDER: ZsReligion[] = ['zoroastrian', 'manichaean', 'cross']
const THEME_ORDER: ZsTheme[] = ['scripture', 'homeland', 'china', 'modern']
const FULLTEXT_ORDER: ZsFulltext[] = ['ready', 'open', 'library', 'print', 'none']

const tally = tallyFulltext()

function byReligion(rel: ZsReligion) {
  return ENTRIES.filter(e => e.religion === rel)
}
function byReligionTheme(rel: ZsReligion, theme: ZsTheme) {
  return ENTRIES.filter(e => e.religion === rel && e.theme === theme)
}
/** 只出實際有條目的面向，免得畫出一排空標題 */
function themesIn(rel: ZsReligion) {
  return THEME_ORDER.filter(t => byReligionTheme(rel, t).length > 0)
}
</script>
