<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="古近東宗教經典" :back="{ to: '/scripture-canon', label: '宗教選單' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-12">
      <div class="w-full max-w-4xl">
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">🏺 古近東宗教經典</h1>
          <p class="text-sm text-gray-500">埃及、蘇美、巴比倫與亞述、赫梯、烏加里特、迦南、阿拉伯、埃蘭的宗教文獻</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <NuxtLink
            v-for="tool in tools"
            :key="tool.path"
            :to="tool.path"
            class="group relative flex flex-col gap-3 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm transition hover:shadow-md hover:border-teal-300"
          >
            <div class="text-3xl">{{ tool.icon }}</div>
            <div>
              <div class="font-semibold text-gray-900 text-base group-hover:text-teal-700 transition break-words">{{ tool.title }}</div>
              <div class="text-xs text-gray-500 mt-1 leading-relaxed break-words">{{ tool.desc }}</div>
            </div>
          </NuxtLink>
        </div>

        <div class="mt-10 text-xs text-gray-400 leading-relaxed space-y-1">
          <p>
            這不是一個宗教，是七八個——它們彼此借神、借文類、借書吏學校，但各有自己的神廟與神譜。
            本區按文明分藏，<b class="text-gray-500">不調和、不比附、不編一套「近東神話」綜合版</b>。
          </p>
          <p>
            古代宗教沒有「改宗的那一天」，只有最後一個會寫神名的書吏死去的那一天。
            所以每一藏止於它的文字死亡：楔形文字約公元 75–80 年，菲萊島的世俗體 452 年。
          </p>
          <p>
            波斯宗教見祆教經典；希臘羅馬宗教見希臘羅馬大藏經；希伯來聖經屬猶太教（規劃中），本區只收以色列與猶大出土的銘文。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '古近東宗教經典 — Know Graph Lab' })

const tools = [
  {
    path: '/near-east',
    icon: '🏺',
    title: '古近東大藏經',
    desc: '埃及／蘇美／阿卡德（巴比倫與亞述）／赫梯與胡里特／烏加里特／迦南與亞蘭／阿拉伯／埃蘭與高地八藏＋外部記述附錄。按藏卷瀏覽，逐篇標存世狀態、學界編號、成書與抄本年代、聖經對位。',
  },
  {
    path: '/near-east/about',
    icon: '📖',
    title: '編纂凡例與取源說明',
    desc: '為何按文明分藏、各藏下限怎麼定、「綴合本」與兩個年代、編號只用學界標準、聖經對位只是互見，以及三欄對照各自的來源與缺口。',
  },
]
</script>
