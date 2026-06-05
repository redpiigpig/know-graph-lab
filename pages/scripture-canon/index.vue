<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="經典對照與註釋" :back="{ to: '/', label: '返回主頁' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-3xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">📜 經典對照與註釋</h1>
          <p class="text-sm text-gray-500">依宗教傳統選擇：各宗教聖典／教義／法規／註釋的多版本逐段對照工具</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <NuxtLink
            v-for="rel in religions"
            :key="rel.path"
            :to="rel.enabled ? rel.path : '#'"
            class="group relative flex flex-col gap-3 bg-white border rounded-2xl p-6 shadow-sm transition"
            :class="rel.enabled
              ? 'border-gray-200 hover:shadow-md hover:border-stone-300 cursor-pointer'
              : 'border-gray-100 opacity-60 cursor-not-allowed'"
          >
            <div class="text-4xl">{{ rel.icon }}</div>
            <div>
              <div class="font-semibold text-gray-900 text-lg group-hover:text-stone-700 transition">{{ rel.title }}</div>
              <div class="text-xs text-gray-500 mt-1 leading-relaxed">{{ rel.desc }}</div>
            </div>
            <span
              v-if="!rel.enabled"
              class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
            >待建置</span>
          </NuxtLink>
        </div>

        <div class="mt-10 text-xs text-gray-400 leading-relaxed text-center">
          <p>每個傳統下收該宗教的聖典多版本、教義／信條、法規與經典註釋等對照工具。基督教部分已上線七個子工具。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '經典對照與註釋 — Know Graph Lab' })

const religions = [
  {
    path: '/scripture-canon/christianity',
    icon: '✝️',
    title: '基督教',
    desc: '聖經多版本平行 ＋ 教父逐節註釋 / 信條（21 次大公會議＋新教全譜）/ 教會法規 / 教父著作 / 典外文獻 / 諾斯底主義文獻 / 教宗訓導文獻 — 七大子工具',
    enabled: true,
  },
  {
    path: '/scripture-canon/buddhism',
    icon: '☸️',
    title: '佛教',
    desc: '佛典多版本對照（大正藏／巴利三藏／藏譯）、宗派教義、經論註疏 —— 規劃中',
    enabled: false,
  },
  {
    path: '/scripture-canon/islam',
    icon: '☪️',
    title: '伊斯蘭教',
    desc: '古蘭經多譯本對照、聖訓（Hadith）彙編、教法（Fiqh／Sharia）文獻 —— 規劃中',
    enabled: false,
  },
  {
    path: '/scripture-canon/judaism',
    icon: '✡️',
    title: '猶太教',
    desc: '希伯來聖經（塔納赫）、塔木德、米德拉什、拉比律法（Halakha）對照 —— 規劃中',
    enabled: false,
  },
]
</script>
