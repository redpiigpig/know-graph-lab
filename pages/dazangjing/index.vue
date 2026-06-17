<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="基督教大藏經" :back="{ to: '/scripture-canon/christianity', label: '經典對照' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ ERAS.length }} 個時代</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">📚 基督教大藏經</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          仿佛教《大藏經》的「經律論」彙編體例，為基督教文獻建立一套漢語藏經分類矩陣。
          按「時代精神」分為前、古代、中世紀、近代、現代五部，每部各立十藏；每藏再分正藏、外藏兩套平行目錄。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          三軌奠基於「隱密的上帝」與「社會學邊界」：<b>前藏</b>＝邊界劃分之前的原始啟示母體；
          <b>正藏</b>＝群體教會論邊界之內的家族記憶（非啟示壟斷）；<b>外藏</b>＝邊界之外、隱密上帝的平行啟示與神聖見證（「外」無貶義）。
        </p>
        <div class="flex items-center gap-2 mt-4">
          <input
            v-model="q"
            type="search"
            placeholder="🔍 搜尋書卷或作者（中英文）…"
            class="flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400 focus:border-stone-400"
            @keyup.enter="goSearch"
          />
          <button
            class="shrink-0 text-sm font-medium text-white bg-stone-900 hover:bg-stone-700 rounded-xl px-4 py-2 transition"
            @click="goSearch"
          >搜尋</button>
        </div>
        <NuxtLink
          to="/dazangjing/about"
          class="inline-flex items-center gap-1.5 mt-3 text-xs font-medium text-stone-700 hover:text-stone-900 border border-stone-300 hover:border-stone-400 rounded-full px-3 py-1.5 transition"
        >📖 編纂凡例與分類標準 →</NuxtLink>
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

const q = ref('')
const goSearch = () => {
  const k = q.value.trim()
  navigateTo(k ? `/dazangjing/search?q=${encodeURIComponent(k)}` : '/dazangjing/search')
}

definePageMeta({ middleware: 'auth' })
useHead({ title: '基督教大藏經 — Know Graph Lab' })
</script>
