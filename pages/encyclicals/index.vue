<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0">
      <NuxtLink to="/scripture-canon" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <span class="text-sm font-semibold text-stone-900">🕊️ 教宗訓導文獻</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap">
        {{ ALL_DOCUMENTS.length }} 篇 / {{ POPES.length }} 位教宗
      </span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="mb-8 pb-6 border-b border-stone-200">
        <h1 class="text-2xl font-bold text-stone-900 mb-1">教宗訓導文獻對照</h1>
        <p class="text-sm text-stone-500 leading-relaxed">
          個別教宗頒布的通諭／使徒勸諭／使徒憲令／自動詔書／演說；按世紀分組瀏覽。
          每篇提供拉丁／英文／中文三欄逐段對照（vatican.va 段號）。
        </p>
        <p class="text-xs text-stone-400 mt-3">
          範圍：本工具收個別教宗以個人身分頒布之文件。大公會議產出（如梵二 16 份）請見
          <NuxtLink to="/creeds" class="underline hover:text-stone-700">信條對照</NuxtLink>。
          資料源：vatican.va + papalencyclicals.net + 主教團官方譯本。
        </p>
      </header>

      <!-- 選擇世紀（每個世紀一張長型卡片，由上到下） -->
      <div class="mb-6">
        <div class="text-xs uppercase tracking-widest text-stone-500 font-semibold mb-3">選擇世紀</div>
        <div class="space-y-3">
          <NuxtLink
            v-for="c in centuries"
            :key="c.century"
            :to="`/encyclicals/century/${c.century}`"
            class="group block bg-white border-2 rounded-xl px-6 py-5 transition-all duration-150"
            :class="c.docCount > 0
              ? 'border-stone-200 hover:border-stone-500 hover:shadow-md cursor-pointer'
              : 'border-stone-100 hover:border-stone-300'"
          >
            <div class="flex items-baseline gap-4 mb-2">
              <div class="text-3xl font-bold text-stone-900 shrink-0">
                {{ c.century }}<span class="text-base font-normal text-stone-400 ml-0.5">世紀</span>
              </div>
              <div class="text-xs text-stone-400 font-mono">{{ c.yearRange }}</div>
              <div v-if="c.docCount > 0" class="ml-auto text-xs font-mono font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                {{ c.docCount }} 篇
              </div>
              <div v-else class="ml-auto text-[10px] text-stone-300 uppercase tracking-wider">待補</div>
            </div>
            <div class="flex flex-wrap gap-x-2 gap-y-1 text-[13px] text-stone-700 leading-relaxed"
                 style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
              <template v-for="(name, i) in c.popeNames" :key="name">
                <span>{{ name }}</span>
                <span v-if="i < c.popeNames.length - 1" class="text-stone-300">·</span>
              </template>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Roadmap -->
      <div class="mt-12 bg-amber-50/60 border border-amber-200 rounded-xl px-6 py-5">
        <div class="text-sm font-semibold text-amber-900 mb-2">📋 建置策略（2026-05-27）</div>
        <div class="text-xs text-stone-700 leading-relaxed space-y-1.5">
          <p>從 21 世紀方濟各往回做，逐步往 19 世紀 Pius IX / Leo XIII 推進。</p>
          <p class="text-stone-500">
            良十四世（Leo XIV, 2025-）：缺官方中譯，待主教團發布後再行 ingest。<br />
            4-15 世紀早期教宗文件：依賴教父原典中譯成熟度，將在後續 Phase 5 回頭補充。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ALL_DOCUMENTS,
  POPES,
  documentsInCentury,
  popesInCentury,
} from '~/data/encyclicals'

definePageMeta({ middleware: 'auth' })
useHead({ title: '教宗訓導文獻 — 知識圖工作室' })

/** 21c→4c（含尼西亞會議 325 時的 Sylvester I）顯示順序 */
const CENTURY_RANGE = [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4] as const

const centuries = computed(() =>
  CENTURY_RANGE.map(c => ({
    century: c,
    yearRange: `${(c - 1) * 100 + 1}–${c * 100}`,
    docCount: documentsInCentury(c).length,
    popeCount: popesInCentury(c).length,
    popeNames: popesInCentury(c).map(p => p.nameZh),
  })),
)
</script>
