<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="摩尼教經典對照" :back="{ to: '/scripture-canon', label: '宗教選單' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">☀️ 摩尼教經典對照</h1>
          <p class="text-sm text-gray-500">科普特文、中古伊朗語、回鶻語與漢文殘卷的原文／英譯／繁中逐段對照</p>
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
              <div class="font-semibold text-gray-900 text-base group-hover:text-amber-700 transition break-words">{{ tool.title }}</div>
              <div class="text-xs text-gray-500 mt-1 leading-relaxed break-words">{{ tool.desc }}</div>
            </div>
            <span
              v-if="!tool.enabled"
              class="absolute top-3 right-3 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
            >待實作</span>
          </NuxtLink>
        </div>

        <div class="mt-10 text-xs text-gray-400 leading-relaxed">
          <p>
            摩尼是宗教史上第一個親手寫下並封定正典的創教者，他明白地說前面的使徒都因為沒有親筆寫下教導
            而讓教會走樣，他的不會。<b class="text-gray-500">結果他親撰的七部大經，今天沒有一部傳世。</b>
            本區仍照那份書目立卷，即使卷是空的——不列等於接受一個由勝利者寫下的假象。
          </p>
          <p class="mt-1">
            續藏按出土語言與地點分（埃及科普特文與希臘文／吐魯番中古伊朗語與回鶻語／敦煌與福建漢文），
            因為摩尼教文獻的存世形態本來就是語言群：一部《巨人書》在四種語言裡是四份殘缺程度不同的殘卷。
            第五藏收反對者所記，<b class="text-gray-500">非經典</b>，每條標明敵證等級。
          </p>
          <p class="mt-1">
            取源：吐魯番各語言用國際摩尼教研究學會開放取用的《東方摩尼教選輯》四冊（原文轉寫與英譯逐行並排）；
            漢文三經用《大正藏》第 54 冊（公有領域）；教父駁論用 ANF／NPNF。
            科普特文抄本的校本與英譯幾乎全在版權內，是本區最大的缺口。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '摩尼教經典對照 — Know Graph Lab' })

const tools = [
  {
    path: '/manichaean',
    icon: '☀️',
    title: '摩尼教經典五藏',
    desc: '摩尼親撰（正藏）／地中海文獻／東方語文獻／漢文文獻／敵證與外部記述（附錄）。按藏卷瀏覽，逐篇標注存世狀態、出土地與原文、英譯、繁中三欄的實際取源現況。',
    enabled: true,
  },
  {
    path: '/manichaean/about',
    icon: '📖',
    title: '編纂凡例與取源說明',
    desc: '五藏的收錄準則、為何正藏空著也要立卷、續藏為何按語言分、敵證三級的定義與使用限制、段號照抄不自編的規矩，以及各欄的來源與缺口。',
    enabled: true,
  },
]
</script>
