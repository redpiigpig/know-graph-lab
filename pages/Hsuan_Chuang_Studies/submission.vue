<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <!-- Breadcrumb -->
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '投稿指引' : 'Submission Guidelines' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <!-- Section title -->
      <h2 class="text-2xl font-bold mb-1">{{ lang === 'zh' ? '投稿指引' : 'Submission Guidelines' }}</h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-24 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <!-- ZH Content -->
      <div v-if="lang === 'zh'" class="space-y-6 text-[15px] leading-relaxed">
        <p class="text-center font-bold text-base">玄奘大學《玄奘佛學研究》徵稿啟事</p>

        <p>本學報主要刊載有關佛學相關領域之原創性論文，包括與佛教有關之義理、教史、藝術、文學、心理、社會、教育等，歡迎各界投稿，來稿應未曾以任何文字形式出版。本學報每年出版兩期，上半年出刊日為三月三十日，下半年為九月三十日。</p>

        <p>本刊全年徵稿，不設期限。若有針對特別主題，請於投稿時說明投稿專輯，茲將近期預定專輯名稱及專輯總編輯列表於後：</p>

        <!-- Issues table -->
        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-sm text-center" style="font-family: Arial, '新細明體', sans-serif;">
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-400 px-3 py-2">期　數</th>
                <th class="border border-gray-400 px-3 py-2">專輯主編</th>
                <th class="border border-gray-400 px-3 py-2">專輯名稱</th>
                <th class="border border-gray-400 px-3 py-2">截稿日期</th>
                <th class="border border-gray-400 px-3 py-2">出刊日期</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in issuesZh" :key="r[0]" class="odd:bg-white even:bg-gray-50">
                <td v-for="cell in r" class="border border-gray-300 px-3 py-1.5">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p>本學報徵稿，請將惠稿電子檔傳至 <a href="mailto:hcu10@hcu.edu.tw" class="text-blue-700 hover:underline">hcu10@hcu.edu.tw</a>，玄奘大學玄奘佛學研究堅意法師收。為了避免傳送信件因被攔截而收不到，敬請同步將論文傳到 <a href="mailto:part55410@gmail.com" class="text-blue-700 hover:underline">part55410@gmail.com</a>。所有惠稿均經編輯委員會送請專家學者評審，通過後始予刊登。作者慎勿一稿兩投，以免違背學術倫理。</p>

        <p>作者來稿請依本學報之【學術性論文撰寫格式要點】撰寫，並以 WORD／A4 規格／直式橫書／11pt 新細明體繕打，除特邀稿外，字數以八千至一萬五千字為原則。</p>

        <p class="text-sm text-gray-600">＊聯絡人：0982-215-945　堅意法師</p>

        <div class="border-t border-gray-200 pt-6">
          <p class="font-bold mb-3">學術性論文撰寫格式要點</p>
          <ol class="list-none space-y-2 text-sm">
            <li><span class="font-semibold">一、論文篇名（Article Title）</span>：具備中、英文篇名，扼要反應論文內容，包含主要關鍵詞。</li>
            <li><span class="font-semibold">二、作者（Author）</span>：具備作者中、英文姓名及服務機構、職稱。</li>
            <li><span class="font-semibold">三、摘要（Abstracts）</span>：具備中、英文摘要，字數不超過一頁，內容涵蓋研究目的、方法、結果與結論。</li>
            <li><span class="font-semibold">四、關鍵詞（Keywords）</span>：中、英文各以五個為限，分別列於摘要之下。</li>
            <li><span class="font-semibold">五、正文（Text）</span>：以 Chicago 格式撰寫，章節標號依「一、（一）1.（1）」順序排列。</li>
            <li><span class="font-semibold">六、誌謝（Acknowledgement）</span>：載明協助完成論文之個人、機構及經費來源。</li>
            <li><span class="font-semibold">七、註釋（Notes）</span>：附在當頁末，以阿拉伯數字編號。</li>
            <li><span class="font-semibold">八、參考書目（References）</span>：所列書目必須與註解引用相符，格式參見 Chicago Manual of Style。</li>
            <li><span class="font-semibold">九、附圖、附表</span>：須注意縮版後仍能完整清晰，本學報為黑白印刷。</li>
          </ol>
        </div>
      </div>

      <!-- EN Content -->
      <div v-else class="space-y-6 text-[15px] leading-relaxed">
        <p class="text-center font-bold text-base">Call for Papers — Hsuan Chuang Journal of Buddhism Studies</p>

        <p>The <em>Hsuan Chuang Journal of Buddhism Studies</em> (HCJBS) publishes original scholarly articles in Buddhist studies, including Buddhist doctrine, history, art, literature, psychology, sociology, and education. Submissions must not have been previously published in any form. The journal is published twice a year: March 30 (spring) and September 30 (fall).</p>

        <p>Submissions are accepted year-round without deadlines. For thematic issues, please indicate the relevant theme when submitting. Upcoming thematic issues are listed below:</p>

        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-sm text-center" style="font-family: Arial, sans-serif;">
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-400 px-3 py-2">Issue</th>
                <th class="border border-gray-400 px-3 py-2">Guest Editor</th>
                <th class="border border-gray-400 px-3 py-2">Theme</th>
                <th class="border border-gray-400 px-3 py-2">Deadline</th>
                <th class="border border-gray-400 px-3 py-2">Publication</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in issuesEn" :key="r[0]" class="odd:bg-white even:bg-gray-50">
                <td v-for="cell in r" class="border border-gray-300 px-3 py-1.5">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p>Please submit manuscripts as email attachments to <a href="mailto:hcu10@hcu.edu.tw" class="text-blue-700 hover:underline">hcu10@hcu.edu.tw</a> (Ven. Jianyi, HCJBS). To ensure receipt, please also send a copy to <a href="mailto:part55410@gmail.com" class="text-blue-700 hover:underline">part55410@gmail.com</a>. All submissions undergo blind peer review. Authors must not submit the same manuscript to multiple journals simultaneously.</p>

        <p>Manuscripts should conform to HCJBS formatting guidelines, prepared in Microsoft Word, A4, vertical layout, 11pt font. Manuscripts should be 8,000–15,000 characters (Chinese) or equivalent in English.</p>

        <p class="text-sm text-gray-600">* Contact: Ven. Jianyi, Tel. 0982-215-945</p>

        <div class="border-t border-gray-200 pt-6">
          <p class="font-bold mb-3">Manuscript Format Guidelines</p>
          <ol class="list-none space-y-2 text-sm">
            <li><span class="font-semibold">I. Article Title:</span> Provide both Chinese and English titles; include key terms.</li>
            <li><span class="font-semibold">II. Author:</span> Full name, institutional affiliation, and title in both Chinese and English.</li>
            <li><span class="font-semibold">III. Abstract:</span> Both Chinese and English abstracts, max. one page, covering objectives, methods, results, and conclusions.</li>
            <li><span class="font-semibold">IV. Keywords:</span> Up to five keywords in each language, placed after respective abstracts.</li>
            <li><span class="font-semibold">V. Text:</span> Chicago citation style. Section numbering follows the pattern I. (I) 1. (1).</li>
            <li><span class="font-semibold">VI. Acknowledgements:</span> List individuals, institutions, and funding sources that contributed to the research.</li>
            <li><span class="font-semibold">VII. Notes:</span> Footnotes at the bottom of each page, numbered consecutively in Arabic numerals.</li>
            <li><span class="font-semibold">VIII. References:</span> Must correspond to all cited works; follow Chicago Manual of Style.</li>
            <li><span class="font-semibold">IX. Figures and Tables:</span> Must remain legible after reduction to B5 format; black-and-white printing only.</li>
          </ol>
        </div>
      </div>

      <!-- Download button -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: Arial, sans-serif;">
        <a href="/api/xuanzang/download?file=submission" download
          class="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-500 text-sm text-gray-700 hover:bg-gray-100 transition">
          ↓ {{ lang === 'zh' ? '下載投稿指引（Word）' : 'Download Submission Guidelines (Word)' }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "投稿指引 — 玄奘佛學研究", link: [{ rel: 'icon', type: 'image/png', href: '/api/xuanzang/logo-icon' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const issuesZh = [
  ['第45期', '邱敏捷教授', '臺灣佛教',               '114年10月', '115年3月'],
  ['第46期', '王三慶教授', '敦煌吐魯番文獻與佛教',   '115年4月',  '115年9月'],
  ['第47期', '劉宇光教授', '梵漢藏佛典翻譯',         '115年10月', '116年3月'],
  ['第48期', '蕭麗華教授', '佛教文學',               '116年4月',  '116年9月'],
  ['第49期', '何日生教授', '應用佛學',               '116年10月', '117年3月'],
  ['第50期', '侯坤宏教授', '東亞佛教',               '117年4月',  '117年9月'],
  ['第51期', '李玉珍教授', '跨境越界的比丘尼',       '117年10月', '118年3月'],
  ['第52期', '林朝成教授', '佛教心理學',             '118年4月',  '118年9月'],
  ['第53期', '侯坤宏教授', '佛教文獻學',             '118年10月', '119年3月'],
  ['第54期', '何日生教授', '佛教組織研究',           '119年4月',  '119年9月'],
  ['第55期', '嚴瑋泓教授', 'AI的研究倫理與應用倫理', '119年10月', '120年3月'],
]

const issuesEn = [
  ['Vol. 45', 'Prof. Chiu Min-chieh',  'Taiwanese Buddhism',                   'Oct. 2025', 'Mar. 2026'],
  ['Vol. 46', 'Prof. Wang San-ching',  'Dunhuang-Turfan Documents & Buddhism', 'Apr. 2026', 'Sep. 2026'],
  ['Vol. 47', 'Prof. Liu Yu-guang',    'Sanskrit–Chinese–Tibetan Translation', 'Oct. 2026', 'Mar. 2027'],
  ['Vol. 48', 'Prof. Hsiao Li-hua',    'Buddhist Literature',                  'Apr. 2027', 'Sep. 2027'],
  ['Vol. 49', 'Prof. Ho Jih-sheng',    'Applied Buddhism',                     'Oct. 2027', 'Mar. 2028'],
  ['Vol. 50', 'Prof. Hou Kun-hung',    'East Asian Buddhism',                  'Apr. 2028', 'Sep. 2028'],
  ['Vol. 51', 'Prof. Li Yu-chen',      'Crossing Borders: Buddhist Nuns',      'Oct. 2028', 'Mar. 2029'],
  ['Vol. 52', 'Prof. Lin Chao-cheng',  'Buddhist Psychology',                  'Apr. 2029', 'Sep. 2029'],
  ['Vol. 53', 'Prof. Hou Kun-hung',    'Buddhist Philology',                   'Oct. 2029', 'Mar. 2030'],
  ['Vol. 54', 'Prof. Ho Jih-sheng',    'Buddhist Organizational Studies',      'Apr. 2030', 'Sep. 2030'],
  ['Vol. 55', 'Prof. Yen Wei-hung',    'Research Ethics & Applied Ethics of AI', 'Oct. 2030', 'Mar. 2031'],
]
</script>
