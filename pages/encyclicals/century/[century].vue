<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0">
      <NuxtLink to="/encyclicals" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <span class="text-sm font-semibold text-stone-900">🕊️ 教宗訓導文獻</span>
      <span class="text-stone-300">/</span>
      <span class="text-sm text-stone-700">{{ century }} 世紀</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap">{{ popes.length }} 位教宗 / {{ docCount }} 篇</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="text-xs text-stone-400 mb-1">{{ centuryYearRange }}</div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight">{{ century }} 世紀</h1>
        <p class="text-sm text-stone-500 leading-relaxed mt-2">{{ centuryBlurb }}</p>
      </header>

      <div v-if="popes.length === 0" class="text-center text-stone-400 py-16 text-sm">
        此世紀尚未錄入教宗。
      </div>

      <div v-else class="space-y-3">
        <NuxtLink
          v-for="pope in popes"
          :key="pope.slug"
          :to="`/encyclicals/pope/${pope.slug}`"
          class="block bg-white border border-stone-200 rounded-xl px-6 py-5 hover:border-stone-400 hover:shadow-md transition-all duration-150"
        >
          <div class="flex items-start gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline flex-wrap gap-2 mb-1">
                <h3 class="font-bold text-stone-900 text-lg">{{ pope.nameZh }}</h3>
                <span class="text-xs italic text-stone-500">{{ pope.nameLat }}</span>
                <span class="text-[11px] font-mono text-stone-400">
                  {{ pope.pontificateStart.slice(0, 4) }}–{{ pope.pontificateEnd ? pope.pontificateEnd.slice(0, 4) : '今' }}
                </span>
                <span
                  v-if="centuriesOfPope(pope).length > 1"
                  class="text-[10px] px-1.5 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200"
                  :title="`此教宗任期跨 ${centuriesOfPope(pope).map(c => c + 'c').join(' + ')}`"
                >跨世紀</span>
              </div>
              <div class="text-xs text-stone-500 mb-2">
                {{ pope.nationality }}
                <span v-if="pope.birthName" class="text-stone-400">
                  · 俗名 {{ pope.birthName }}
                </span>
              </div>
              <div v-if="pope.notesZh" class="text-[13px] text-stone-700 leading-relaxed line-clamp-2">
                {{ pope.notesZh }}
              </div>
            </div>
            <div class="flex-shrink-0 text-right">
              <div v-if="docCountInThisCentury(pope.slug) > 0" class="text-2xl font-bold text-amber-700">
                {{ docCountInThisCentury(pope.slug) }}
              </div>
              <div v-else class="text-2xl font-bold text-stone-300">—</div>
              <div class="text-[10px] uppercase tracking-wider text-stone-400 mt-0.5">
                本世紀篇數
              </div>
              <div v-if="documentsByPope(pope.slug).length > docCountInThisCentury(pope.slug)" class="text-[10px] text-stone-400 mt-1">
                全教宗 {{ documentsByPope(pope.slug).length }} 篇
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  POPES,
  popesInCentury,
  centuriesOfPope,
  documentsInCentury,
  documentsByPope,
  documentCountForPopeInCentury,
} from '~/data/encyclicals'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const century = computed(() => parseInt(route.params.century as string, 10))

useHead(() => ({
  title: `${century.value} 世紀教宗 — 教宗訓導文獻`,
}))

const popes = computed(() => popesInCentury(century.value))
const docCount = computed(() => documentsInCentury(century.value).length)

function docCountInThisCentury(popeSlug: string): number {
  return documentCountForPopeInCentury(popeSlug, century.value)
}

const centuryYearRange = computed(() => {
  const start = (century.value - 1) * 100 + 1
  const end = century.value * 100
  return `${start}–${end}`
})

const CENTURY_BLURB: Record<number, string> = {
  21: '梵二後第二代教宗群：本篤十六世延續若望保祿二世神學遺產；方濟各以「整體生態學」與「對話」為主軸開啟新典範；2025 良十四世接任。',
  20: '梵二召開（1962-65）與其後續詮釋的世紀。社會訓導從《新事》接力寫到《在真理中實踐愛德》。若望保祿二世任內頒布 14 道通諭，是 19-21c 訓導文獻最豐沛的教宗。',
  19: '現代教廷通諭體裁奠基期。碧岳九世定義聖母無染原罪信理並召開梵一；良十三世《新事》1891 開啟近代天主教社會訓導傳統。',
  18: '啟蒙運動衝擊下的教廷。本篤十四世奠定現代通諭體裁；克勉十四世 1773 解散耶穌會（至 1814 由碧岳七世恢復）。',
  17: '反宗教改革延續期。Galileo 第二次審判（伍朋八世）；Jansenism 爭議在諾森十世、克勉十一世處連續譴責；額我略十五世 1622 創立傳信部統籌全球傳教。',
  16: '宗教改革與反宗教改革。良十世 1520 譴責路德；保祿三世 1545 召開 Trent 大公會議；碧岳五世 1568 頒布 Tridentine 經本統一拉丁禮 400 年；額我略十三世 1582 頒布額我略曆。',
  15: '文藝復興教廷。西方大分裂（1378-1417）由 Constance 大公會議終結。Borgia 與 Medici 等貴族家族出身的教宗大力贊助文藝復興藝術。亞歷山大六世 1493 劃分新世界。',
  14: '亞維儂遷都期（1309-1377）— 七位教宗連續在法國亞維儂駐錫；後續引發 1378-1417 西方大分裂。鮑尼法八世 1302《Unam Sanctam》為最高度教宗權威聲明。',
  13: '中世紀盛期教權頂峰。諾森三世 1215 召開拉特朗四大公會議；額我略九世 1234 編《Decretales》奠定中世紀教會法；批准道明會、方濟會、加爾默羅會等托缽修會。',
  12: '十字軍世紀。加禮多二世 1122 Worms 協約終結敘任權之爭；亞歷山大三世 1179 拉特朗三大公會議；伍朋三世直至格里高利八世號召第三次十字軍。',
  11: '教會大改革（Gregorian Reform）與東西教會大分裂。良九世 1054 與君士坦丁堡互擲絕罰；額我略七世與神羅皇帝亨利四世敘任權之爭、Canossa 之辱；伍朋二世 1095 號召第一次十字軍。',
  10: '「黑暗世紀」(Saeculum Obscurum) — 教廷被羅馬貴族派系（Crescentii、Tusculani）操控；多位教宗短命且爭議；末有西爾物斯德二世（999-1003）為首位法國籍學者教宗。',
  9: '加洛林王朝與教廷合作期。良三世 800 為查理曼加冕奠定神羅帝國；尼閣一世「大尼閣」對抗 Photian 分裂；末期進入黑暗世紀（897 Cadaver Synod 為標誌）。',
  8: '聖像爭議與教宗國誕生。斯德望二世 754 為法蘭克王 Pippin 加冕奠定教宗國基礎；末期希臘／敘利亞籍教宗最後一波；良三世（795-）為查理曼加冕（800）開啟下世紀。',
  7: '拜占庭與教廷張力期。馬定一世 649 拉特朗會議譴責 Monothelitism 後遭拜占庭逮捕殉道；何諾理一世遭君士坦丁堡三大公會議（681）譴責 — 梵一教宗無謬論辯論的歷史 case。',
  6: '大額我略時代。鮑尼法二世為首位日耳曼裔教宗；何彌斯達 515 終結 Acacian 分裂；末有額我略一世（590-604，西方四大教父之一）派 Augustine of Canterbury 至英格蘭傳教。',
  5: '東西方共識教父期。良一世「大良」440-461 為西方四大教父之一，《Tome of Leo》449 奠定迦克墩 451 基督論正統；哲拉削一世 494《兩權說》論教會權與帝國權分立。',
  4: '尼西亞與君士坦丁堡時代。西爾物斯德一世（314-335）為尼西亞第一次大公會議在位教宗；達瑪穌一世 382 委託熱羅尼莫翻譯 Vulgate 拉丁聖經；西利修 385《Directa》為首封正式 Decretal。',
}
const centuryBlurb = computed(() => CENTURY_BLURB[century.value] || '（待補）')
</script>
