<template>
  <div class="min-h-screen bg-white text-gray-800" style="font-family: 'DFKai-SB','標楷體','KaiTi','Times New Roman',serif;">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main class="max-w-5xl mx-auto px-10 py-8">
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '首頁' : 'Home' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '資料庫' : 'Archive' }}</span>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <h2 class="text-2xl font-bold mb-1">
        {{ lang === 'zh' ? '玄奘佛學研究' : 'Hsuan Chuang Journal of Buddhism Studies' }}
      </h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-36 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-px bg-gray-300 border border-gray-300">
        <a v-for="issue in issues" :key="issue.zh" href="#"
          class="block p-4 bg-white text-sm text-gray-700 hover:bg-gray-50 transition text-center leading-snug">
          {{ lang === 'zh' ? issue.zh : issue.en }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "玄奘佛學研究 — 期刊總覽" })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const issues = [
  { zh: '第四十三期玄奘佛學研究', en: 'HCJBS Vol. 43' },
  { zh: '第四十二期玄奘佛學研究', en: 'HCJBS Vol. 42' },
  { zh: '第四十一期玄奘佛學研究', en: 'HCJBS Vol. 41' },
  { zh: '第四十期玄奘佛學研究',   en: 'HCJBS Vol. 40' },
  { zh: '第三十九期玄奘佛學研究', en: 'HCJBS Vol. 39' },
  { zh: '第三十八期玄奘佛學研究', en: 'HCJBS Vol. 38' },
  { zh: '第三十七期玄奘佛學研究', en: 'HCJBS Vol. 37' },
  { zh: '第三十六期玄奘佛學研究', en: 'HCJBS Vol. 36' },
  { zh: '第三十五期玄奘佛學研究', en: 'HCJBS Vol. 35' },
  { zh: '第三十四期玄奘佛學研究', en: 'HCJBS Vol. 34' },
  { zh: '第三十三期玄奘佛學研究', en: 'HCJBS Vol. 33' },
  { zh: '第三十二期玄奘佛學研究', en: 'HCJBS Vol. 32' },
]
</script>
