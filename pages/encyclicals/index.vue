<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0">
      <NuxtLink to="/scripture-canon" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <span class="text-sm font-semibold text-stone-900">🕊️ 教宗訓導文獻</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap">{{ ALL_DOCUMENTS.length }} 篇</span>
    </nav>

    <div class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="mb-8 pb-6 border-b border-stone-200">
        <h1 class="text-2xl font-bold text-stone-900 mb-1">教宗訓導文獻對照</h1>
        <p class="text-sm text-stone-500 leading-relaxed">
          個別教宗頒布的通諭／使徒勸諭／使徒憲令／自動詔書／演說，按世紀分組瀏覽；
          每篇提供拉丁／英文／中文三欄逐段對照（依 vatican.va 段號對齊）。
        </p>
        <p class="text-xs text-stone-400 mt-3">
          範圍說明：本工具收個別教宗以個人身分頒布之文件。大公會議產出（如梵二 16 份）請見
          <NuxtLink to="/creeds" class="underline hover:text-stone-700">信條對照</NuxtLink>。
          資料源：vatican.va + papalencyclicals.net + 主教團官方譯本。
        </p>
      </header>

      <div v-for="group in groups" :key="group.century" class="mb-10">
        <div class="flex items-baseline gap-3 mb-4">
          <h2 class="text-lg font-bold text-stone-900">{{ group.century }} 世紀</h2>
          <span class="text-xs text-stone-400">{{ group.docs.length }} 篇</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <NuxtLink
            v-for="doc in group.docs"
            :key="doc.slug"
            :to="`/encyclicals/${doc.slug}`"
            class="block bg-white border border-stone-200 rounded-lg px-5 py-4 hover:border-stone-400 hover:shadow-md transition-all duration-150"
          >
            <div class="flex items-baseline gap-2 mb-1">
              <span class="text-[10px] font-semibold uppercase tracking-wider text-stone-500 bg-stone-100 px-1.5 py-0.5 rounded">
                {{ CATEGORY_LABEL_ZH[doc.category] }}
              </span>
              <span class="text-[11px] text-stone-400 font-mono">{{ doc.promulgationDate }}</span>
              <span class="text-[11px] text-stone-500 ml-auto">{{ findPope(doc.popeSlug)?.nameZh }}</span>
            </div>
            <div class="font-semibold text-stone-900 text-sm leading-snug">{{ doc.titleZh }}</div>
            <div class="text-xs italic text-stone-500 mt-0.5">{{ doc.titleLat }}</div>
            <div v-if="doc.topics?.length" class="flex flex-wrap gap-1 mt-2">
              <span
                v-for="t in doc.topics.slice(0, 4)"
                :key="t"
                class="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100"
              >{{ t }}</span>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Roadmap card -->
      <div class="mt-12 bg-amber-50/60 border border-amber-200 rounded-xl px-6 py-5">
        <div class="text-sm font-semibold text-amber-900 mb-2">📋 建置計畫（2026-05-27）</div>
        <div class="text-xs text-stone-700 leading-relaxed space-y-1.5">
          <p>策略：21 世紀往回做。已上線 {{ ALL_DOCUMENTS.length }} 篇；下一批：</p>
          <ul class="list-disc list-inside pl-2 space-y-0.5">
            <li>方濟各 — Fratelli Tutti 2020、Dilexit Nos 2024、Lumen Fidei 2013</li>
            <li>本篤十六世 — Deus Caritas Est 2005、Spe Salvi 2007、Caritas in Veritate 2009</li>
            <li>若望保祿二世 — Veritatis Splendor 1993、Evangelium Vitae 1995、Fides et Ratio 1998、Ut Unum Sint 1995</li>
          </ul>
          <p class="mt-2 text-stone-500">
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
  documentsByCentury,
  findPope,
  CATEGORY_LABEL_ZH,
} from '~/data/encyclicals'

definePageMeta({ middleware: 'auth' })
useHead({ title: '教宗訓導文獻 — 知識圖工作室' })

const groups = computed(() => documentsByCentury())
</script>
