<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="希臘羅馬宗教經典對照" :back="{ to: '/scripture-canon', label: '宗教選單' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">🏛️ 希臘羅馬宗教經典對照</h1>
          <p class="text-sm text-gray-500">地中海傳統多神信仰的文獻整編：自公元前 8 世紀至公元 529 年基督教全面取代為止</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
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
          <p>希臘傳統宗教從未有過正典，這正是它輸給基督教的原因之一。本區替一個已死的宗教補做它從未做過的編纂工程。</p>
          <p class="mt-1">與基督教區的《基督教大藏經》平行並列、互不從屬；少數重疊條目（赫西俄德《神譜》、德爾菲神諭等）以互見標記串連，不作合併。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '希臘羅馬宗教經典對照 — Know Graph Lab' })

const tools = [
  {
    path: '/hellenika',
    icon: '🏛️',
    title: '希臘羅馬大藏經',
    desc: '以希臘字母 Α–Ω 立廿四卷，仿聖經的文類光譜編次——神譜、列祖、祭儀法、祕儀、詩頌、箴言、神諭、啟示、論神、聖徒傳、爭辯；羅馬宗教自成一系，另立六卷 I–VI 為續典。全書止於公元 529 年',
    enabled: true,
  },
]
</script>
