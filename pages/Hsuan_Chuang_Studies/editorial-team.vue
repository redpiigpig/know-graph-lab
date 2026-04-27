<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '編輯委員' : 'Editorial Board' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <h2 class="text-2xl font-bold mb-1">{{ lang === 'zh' ? '編輯委員' : 'Editorial Board' }}</h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-24 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <div class="space-y-8 text-[15px] leading-relaxed">

        <!-- Editor-in-Chief -->
        <div>
          <p class="font-bold text-base mb-3">{{ lang === 'zh' ? '總編輯' : 'Editor-in-Chief' }}</p>
          <table class="w-full border-collapse text-sm" style="font-family: Arial, '新細明體', sans-serif;">
            <tbody>
              <tr class="border border-gray-300">
                <td class="border border-gray-300 px-4 py-2 bg-gray-50 font-semibold w-32">
                  {{ lang === 'zh' ? '釋昭慧' : 'Ven. Chao-hwei Shih' }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ lang === 'zh' ? '玄奘大學宗教與文化學系' : 'Dept. of Religion and Culture, Hsuan Chuang University' }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-gray-600">
                  {{ lang === 'zh' ? '倫理學、佛教戒律學、原始佛教、唯識學' : 'Ethics, Buddhist Precepts, Early Buddhism, Yogācāra' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Editorial Board -->
        <div>
          <p class="font-bold text-base mb-3">
            {{ lang === 'zh' ? '編輯委員（依姓氏筆畫排序）' : 'Editorial Board Members (in stroke order)' }}
          </p>
          <table class="w-full border-collapse text-sm" style="font-family: Arial, '新細明體', sans-serif;">
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-400 px-4 py-2 text-left w-36">{{ lang === 'zh' ? '姓名' : 'Name' }}</th>
                <th class="border border-gray-400 px-4 py-2 text-left">{{ lang === 'zh' ? '服務機構' : 'Institution' }}</th>
                <th class="border border-gray-400 px-4 py-2 text-left">{{ lang === 'zh' ? '學術專長' : 'Specialization' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.zhName" class="odd:bg-white even:bg-gray-50">
                <td class="border border-gray-300 px-4 py-2 font-medium">
                  {{ lang === 'zh' ? m.zhName : m.enName }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ lang === 'zh' ? m.zhInst : m.enInst }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-gray-600 text-xs">
                  {{ lang === 'zh' ? m.zhSpec : m.enSpec }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: Arial, sans-serif;">
        <a href="/api/xuanzang/download?file=editorial" download
          class="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-500 text-sm text-gray-700 hover:bg-gray-100 transition">
          ↓ {{ lang === 'zh' ? '下載編輯團隊資訊（Word）' : 'Download Editorial Board Info (Word)' }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "編輯委員 — 玄奘佛學研究", link: [{ rel: 'icon', type: 'image/png', href: '/api/xuanzang/logo-icon' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const members = [
  { zhName: '王三慶', enName: 'Wang San-ching',   zhInst: '成功大學中國文學系',           enInst: 'Dept. of Chinese Literature, National Cheng Kung University',         zhSpec: '敦煌學、聲韻學、古典小說',              enSpec: 'Dunhuang Studies, Phonology, Classical Fiction' },
  { zhName: '何日生', enName: 'Ho Jih-sheng',      zhInst: '慈濟大學宗教與文化研究所',     enInst: 'Graduate Inst. of Religion and Culture, Tzu Chi University',           zhSpec: '應用佛學、慈善組織',                    enSpec: 'Applied Buddhism, Philanthropic Organizations' },
  { zhName: '李玉珍', enName: 'Li Yu-chen',        zhInst: '政治大學宗教研究所',           enInst: 'Graduate Inst. of Religious Studies, National Chengchi University',    zhSpec: '佛教文學、臺灣佛教、宗教與性別',        enSpec: 'Buddhist Literature, Taiwanese Buddhism, Religion & Gender' },
  { zhName: '李瑞全', enName: 'Lee Shui-chuen',    zhInst: '中央大學哲學研究所',           enInst: 'Dept. of Philosophy, National Central University',                     zhSpec: '儒學、生命倫理學、康德哲學',            enSpec: 'Confucianism, Bioethics, Kantian Philosophy' },
  { zhName: '林保堯', enName: 'Lin Bao-yao',       zhInst: '臺北藝術大學文化資源學院',     enInst: 'College of Cultural Resources, Taipei National Univ. of the Arts',     zhSpec: '佛教藝術、文化資產',                    enSpec: 'Buddhist Art, Cultural Heritage' },
  { zhName: '林朝成', enName: 'Lin Chao-cheng',    zhInst: '成功大學（兼任）',             enInst: 'National Cheng Kung University (adjunct)',                             zhSpec: '應用倫理學、佛教哲學、佛教生態學',      enSpec: 'Applied Ethics, Buddhist Philosophy, Buddhist Ecology' },
  { zhName: '邱敏捷', enName: 'Chiu Min-chieh',    zhInst: '臺南大學國語文學系',           enInst: 'Dept. of Chinese Language and Literature, National Univ. of Tainan',   zhSpec: '佛學研究、佛教文學、臺灣佛教',          enSpec: 'Buddhist Studies, Buddhist Literature, Taiwanese Buddhism' },
  { zhName: '侯坤宏', enName: 'Hou Kun-hung',      zhInst: '玄奘大學宗教與文化學系',       enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',               zhSpec: '近代漢傳佛教史、戰後臺灣史',            enSpec: 'Modern Chinese Buddhism History, Post-war Taiwan History' },
  { zhName: '張瓈文', enName: 'Chang Li-wen',      zhInst: '輔仁大學英國語文學系',         enInst: 'Dept. of English Language & Literature, Fu Jen Catholic University',    zhSpec: '英語教學、翻譯、比較文學、佛教文學',    enSpec: 'English Teaching, Translation, Comparative Literature, Buddhist Literature' },
  { zhName: '黃運喜', enName: 'Huang Yun-hsi',     zhInst: '玄奘大學宗教與文化學系',       enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',               zhSpec: '宗教史、宗教事務管理',                  enSpec: 'Religious History, Religious Administration' },
  { zhName: '葉海煙', enName: 'Yeh Hai-yen',       zhInst: '成功大學通識教育中心（兼任）', enInst: 'General Education Center, National Cheng Kung University (adjunct)',    zhSpec: '道家哲學、倫理學',                      enSpec: 'Taoist Philosophy, Ethics' },
  { zhName: '蕭麗華', enName: 'Hsiao Li-hua',      zhInst: '佛光大學中國文學與應用學系',   enInst: 'Dept. of Chinese Literature, Fo Guang University',                     zhSpec: '東亞漢詩、中國詩學、佛教文學',          enSpec: 'East Asian Sinitic Poetry, Chinese Poetics, Buddhist Literature' },
  { zhName: '嚴瑋泓', enName: 'Yen Wei-hung',      zhInst: '成功大學中國文學系',           enInst: 'Dept. of Chinese Literature, National Cheng Kung University',          zhSpec: '儒家哲學、生命倫理學、應用倫理學',      enSpec: 'Confucian Philosophy, Bioethics, Applied Ethics' },
  { zhName: 'Marcus Günzel', enName: 'Marcus Günzel', zhInst: '玄奘大學宗教與文化學系', enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',               zhSpec: '漢傳佛教、德語佛學文獻',                enSpec: 'Chinese Buddhism, German-language Buddhist Scholarship' },
]
</script>
