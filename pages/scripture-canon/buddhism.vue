<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="佛教經典對照" :back="{ to: '/scripture-canon', label: '宗教選單' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">☸️ 佛教經典對照與註釋</h1>
          <p class="text-sm text-gray-500">漢文佛典全文與梵、巴利、藏文原典的逐段對照</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <NuxtLink
            v-for="tool in tools"
            :key="tool.path"
            :to="tool.enabled ? tool.path : '#'"
            class="group relative flex flex-col gap-3 bg-white border rounded-2xl p-6 shadow-sm transition"
            :class="tool.enabled
              ? 'border-gray-200 hover:shadow-md hover:border-amber-300 cursor-pointer'
              : 'border-gray-100 opacity-60 cursor-not-allowed'"
          >
            <div class="text-3xl">{{ tool.icon }}</div>
            <div>
              <div class="font-semibold text-gray-900 text-base group-hover:text-amber-700 transition">{{ tool.title }}</div>
              <div class="text-xs text-gray-500 mt-1 leading-relaxed">{{ tool.desc }}</div>
            </div>
            <span
              v-if="!tool.enabled"
              class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
            >待實作</span>
          </NuxtLink>
        </div>

        <div class="mt-10 text-xs text-gray-400 leading-relaxed">
          <p>
            佛典沒有聖經那樣一套通行的章節制。本區以卷與品為跨語言對齊層，段的識別碼採大正藏頁欄行；
            阿含類另可對到「經」、論頌類對到「頌」、律部對到「條」。詳見大藏經頁的凡例。
          </p>
          <p class="mt-1">
            文本來源：中華電子佛典協會（CBETA）TEI P5 XML（大正藏 T、漢譯南傳 N），非商業用途。
            原文對照另取自大正藏原註、CBETA 詞條、SuttaCentral 平行經目與各語系公開校本。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '佛教經典對照 — Know Graph Lab' })

const tools = [
  {
    path: '/tripitaka',
    icon: '☸️',
    title: '佛教大藏經',
    desc: '《大正新脩大藏經》2,471 部＋《漢譯南傳大藏經》83 冊，共 9,788 萬字、101 萬段全文。按大正藏三十一部門與南傳八分部瀏覽，逐段附大正藏頁欄行引用式，並掛梵／巴／藏原典對照與 CBETA 漢梵巴詞條。',
    enabled: true,
  },
  {
    path: '/tripitaka/parallels',
    icon: '🔀',
    title: '漢巴平行經目',
    desc: '四阿含與五尼柯耶的逐經對應表：大正藏原註 ＋ SuttaCentral 平行經目，一部漢譯阿含經可查其巴利、梵文殘卷與藏譯的對應。',
    enabled: false,
  },
]
</script>
