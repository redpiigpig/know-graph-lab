<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon/christianity" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">基督教大藏經</span>
      <span class="text-xs text-gray-400 ml-1">{{ ERAS.length }} 個時代</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📚 基督教大藏經</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          仿佛教《大藏經》的「經律論」彙編體例，為基督教文獻建立一套漢語藏經分類矩陣。
          按時代分為古代、中世紀、近代、現代四部；古代基督教大藏經以經‧律‧論等十藏收錄 800 年前
          基督教文獻、400 年前猶太教文獻、古代異端文獻，以及外教提及基督教的見證。
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <NuxtLink
          v-for="era in ERAS"
          :key="era.key"
          :to="era.enabled ? `/dazangjing/${era.key}` : '#'"
          class="group relative flex gap-4 bg-white border rounded-2xl p-6 shadow-sm transition"
          :class="era.enabled
            ? 'border-gray-200 hover:shadow-md hover:border-stone-300 cursor-pointer'
            : 'border-gray-100 opacity-60 cursor-not-allowed'"
        >
          <div class="shrink-0 w-12 h-12 rounded-xl bg-stone-900 text-white flex items-center justify-center text-2xl font-serif">{{ era.glyph }}</div>
          <div class="min-w-0">
            <div class="font-semibold text-gray-900 text-base group-hover:text-stone-700 transition">{{ era.name }}</div>
            <div class="text-[11px] text-gray-400 mb-1">{{ era.name_en }}</div>
            <div class="text-xs text-gray-600 leading-relaxed">{{ era.subtitle }}</div>
            <div v-if="era.boundary" class="text-[11px] text-gray-400 mt-1.5 leading-relaxed">{{ era.boundary }}</div>
          </div>
          <span
            v-if="!era.enabled"
            class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
          >待建置</span>
          <span
            v-else
            class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700"
          >{{ era.collections.length }} 藏</span>
        </NuxtLink>
      </div>

      <div class="mt-10 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>本分類以「八百／四百」雙軌年代結界為古代部的收錄界線（基督教 800 年、猶太教 400 年）。</p>
        <p class="mt-1">多數書目跨連到站內既有對照工具：聖經（/scripture）、信條（/creeds）、教父著作（/fathers）、典外文獻（/apocrypha）、諾斯底文獻（/gnostic）、教會法規（/canon-law）、教宗訓導（/encyclicals）。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ERAS } from '~/data/dazangjing'

definePageMeta({ middleware: 'auth' })
useHead({ title: '基督教大藏經 — Know Graph Lab' })
</script>
