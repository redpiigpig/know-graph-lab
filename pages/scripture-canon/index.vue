<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">經典對照與註釋</span>
    </nav>

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">📜 經典對照與註釋</h1>
          <p class="text-sm text-gray-500">七個子工具：聖經多版本平行 / 信條 / 教會法規 / 教父著作 / 典外文獻 / 諾斯底主義文獻 / 教宗訓導文獻</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <NuxtLink
            v-for="tool in tools"
            :key="tool.path"
            :to="tool.enabled ? tool.path : '#'"
            class="group relative flex flex-col gap-3 bg-white border rounded-2xl p-6 shadow-sm transition"
            :class="tool.enabled
              ? 'border-gray-200 hover:shadow-md hover:border-stone-300 cursor-pointer'
              : 'border-gray-100 opacity-60 cursor-not-allowed'"
          >
            <div class="text-3xl">{{ tool.icon }}</div>
            <div>
              <div class="font-semibold text-gray-900 text-base group-hover:text-stone-700 transition">{{ tool.title }}</div>
              <div class="text-xs text-gray-500 mt-1 leading-relaxed">{{ tool.desc }}</div>
            </div>
            <span
              v-if="!tool.enabled"
              class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
            >待實作</span>
          </NuxtLink>
        </div>

        <div class="mt-10 text-xs text-gray-400 leading-relaxed">
          <p>本入口集合與基督教聖典／信條／法規／教父／典外文獻相關的五個對照工具。</p>
          <p class="mt-1">資料源：Schaff《教父著作集 38 卷》／《Creeds of Christendom 3 卷》／IVP《古代基督信仰聖經註釋叢書 27 卷》／基督教典外文獻 10 卷／梵蒂岡公開檔案 等公開出版物。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '經典對照與註釋 — Know Graph Lab' })

const tools = [
  {
    path: '/creeds',
    icon: '⛪',
    title: '信條對照',
    desc: '三區：① 信經（使徒／亞他那修／尼西亞-君士坦丁堡／迦克墩）② 歷代大公會議文獻（21 次／梵二 16 份）③ 各宗派信條與要理問答（新教信條全譜＋普世合一對話）',
    enabled: true,
  },
  {
    path: '/canon-law',
    icon: '⚖️',
    title: '教會法規',
    desc: '天主教 CIC 1983 / CCEO 1990 / 教理 CCC、東正教 Pedalion + 使徒教規 85 條、新教章程',
    enabled: false,
  },
  {
    path: '/fathers',
    icon: '✝️',
    title: '教父著作',
    desc: 'Schaff 全集 38 卷（ANF 10 + NPNF1 14 + NPNF2 14）+ 中譯。按系列／卷號瀏覽，連 ebook reader 閱讀。已精修狀態標記。',
    enabled: true,
  },
  {
    path: '/apocrypha',
    icon: '📜',
    title: '典外文獻搜索',
    desc: 'OT 偽典 / 第二正典、NT 偽典、死海古卷、Nag Hammadi 諾斯底文獻全文檢索；中文（基督教典外文獻 10 卷）／英文／原文三欄對照',
    enabled: true,
  },
  {
    path: '/scripture',
    icon: '📖',
    title: '聖經對照 + 教父註釋',
    desc: '多版本平行對照（中／英／拉／希／敘／科普特／亞美尼亞／衣索匹亞）+ 教父逐節註釋 + 各教會 OT/NT canon 標記',
    enabled: true,
  },
  {
    path: '/gnostic',
    icon: '🜍',
    title: '諾斯底主義文獻',
    desc: 'The Gnostic Society Library (gnosis.org) — 拿戈瑪第經集／古典諾斯底經典／瓦倫廷／赫密士文集／摩尼教／曼達教／卡特里派 等 13 類；英文（公有領域英譯）／繁中逐段對照',
    enabled: true,
  },
  {
    path: '/encyclicals',
    icon: '🕊️',
    title: '教宗訓導文獻',
    desc: '個別教宗頒布的通諭／使徒勸諭／使徒憲令／自動詔書／演說；按世紀分組瀏覽，每篇拉丁／英文／中文三欄逐段對照。從 21 世紀方濟各往回做',
    enabled: true,
  },
]
</script>
