<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="祆教經典對照" :back="{ to: '/scripture-canon', label: '宗教選單' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">🔥 祆教經典對照</h1>
          <p class="text-sm text-gray-500">阿維斯陀語與中古波斯語原典的原文／英譯／繁中逐段對照</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <NuxtLink
            v-for="tool in tools"
            :key="tool.path"
            :to="tool.enabled ? tool.path : '#'"
            class="group relative flex flex-col gap-3 bg-white border rounded-2xl p-6 shadow-sm transition"
            :class="tool.enabled
              ? 'border-gray-200 hover:shadow-md hover:border-orange-300 cursor-pointer'
              : 'border-gray-100 opacity-60 cursor-not-allowed'"
          >
            <div class="text-3xl">{{ tool.icon }}</div>
            <div>
              <div class="font-semibold text-gray-900 text-base group-hover:text-orange-700 transition break-words">{{ tool.title }}</div>
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
            祆教的分部不是本站所立。耶斯那 72 章、維斯佩拉德 24 章、祓魔法典 22 章、耶什特 21 首，
            都是薩珊祭司傳下來的禮儀單位，帕西祭司今天仍照這個數目誦唸——與《希臘羅馬大藏經》由編者外加卷次的作法根本不同。
          </p>
          <p class="mt-1">
            原文欄取自 avesta.org（蓋爾德納轉寫）與法蘭克福 TITUS 語料庫；英譯欄以公有領域的《東方聖書》
            第 4、23、31 卷（阿維斯陀）與第 5、18、24、37、47 卷（巴列維文獻）為主。
            <b class="text-gray-500">繁中欄為本站自譯</b>——祆教經典的既有中譯僅有一部簡體選編本且在版權內，
            這一欄在華語世界近乎空白。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '祆教經典對照 — Know Graph Lab' })

const tools = [
  {
    path: '/avesta',
    icon: '🔥',
    title: '祆教經典四藏',
    desc: '阿維斯陀（正藏）／巴列維文獻（續典）／後期波斯語文獻（外典）／王室銘文（附錄）。按禮儀分部瀏覽，逐篇標注存世狀態與原文、英譯、繁中三欄的實際取源現況。',
    enabled: true,
  },
  {
    path: '/avesta/about',
    icon: '📖',
    title: '編纂凡例與取源說明',
    desc: '四藏的收錄準則、為何照傳統分部而不自立卷次、五級存世狀態的定義、阿維斯陀字母與拉丁轉寫的對照表，以及三欄各自的來源與缺口。',
    enabled: true,
  },
]
</script>
