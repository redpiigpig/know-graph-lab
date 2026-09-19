<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: 'Times New Roman,Times,DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <!-- Breadcrumb -->
      <nav class="text-sm mb-3" style="font-family: 'Times New Roman', Times, sans-serif;">
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
      <div v-if="lang === 'zh'" class="space-y-6 text-[17px] leading-relaxed">
        <p class="text-center font-bold text-xl">玄奘大學《玄奘佛學研究》徵稿啟事</p>

        <p>本學報主要刊載有關佛學相關領域之原創性論文，包括與佛教有關之義理、教史、藝術、文學、心理、社會、教育等，歡迎各界投稿，來稿應未曾以任何文字形式出版。本學報每年出版兩期，上半年出刊日為三月三十日，下半年為九月三十日。</p>

        <p>本刊全年徵稿，不設期限。若有針對特別主題，請於投稿時說明投稿專輯，茲將近期預定專輯名稱及專輯總編輯列表於後：</p>

        <!-- Issues table -->
        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-base text-center" style="font-family: 'Times New Roman', Times, '新細明體', sans-serif;">
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

        <p>作者來稿請依本學報之【學術性論文撰寫格式要點】撰寫，並以 WORD／A4 規格／直式橫書／11pt 新細明體繕打，除特邀稿外，字數以八千至一萬五千字為原則。來稿如經審查通過並獲刊登，由作者校對並自負文責，版權則歸本學報所有，作者可免費獲得學報五冊；由於外國航空郵資昂貴，自 2025 年起，刊登外國來稿，將提供一本當期學報，並傳送作者論文全份之 PDF 檔（含封面、版權頁、目次與論文）。</p>

        <p>投稿於本刊經收錄後，同意授權本刊得再授權國家圖書館「台灣期刊論文索引系統」或其他資料庫業者，進行重製、透過網路提供服務、授權用戶下載、列印、瀏覽等行為。並得為符合「台灣期刊論文索引系統」或其他資料庫之需求，酌作格式之修改。</p>

        <p class="text-base text-gray-600 text-left">＊聯絡人：0982-215-945　堅意法師</p>

        <div class="border-t border-gray-200 pt-6">
          <p class="font-bold mb-4">學術性論文撰寫格式要點</p>
          <p class="text-base mb-3">論文請依下列次序撰寫：</p>
          <ol class="list-none space-y-4 text-base">
            <li>
              <p class="font-semibold">一、論文篇名（Article Title）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 具備中、英文篇名。</li>
                <li>2. 扼要反應論文內容。</li>
                <li>3. 包含主要關鍵詞。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">二、作者（Author）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 具備作者中、英文姓名。</li>
                <li>2. 載明作者中、英文服務機構、職稱。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">三、摘要（Abstracts）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 具備中文、英文摘要。</li>
                <li>2. 中文內容則中文摘要在文前，英文摘要在其後；英文內容則英文摘要在文前，中文摘要在其後。</li>
                <li>3. 內容力求涵蓋研究目的、方法、結果與結論，撰寫時盡量包含關鍵詞以凸顯論文主題。</li>
                <li>4. 字數不超過一頁。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">四、關鍵詞（Keywords）</p>
              <p class="ml-4 mt-1 text-gray-700">具有中、英文關鍵詞，以五個為限，分別列於中、英文摘要之下。</p>
            </li>
            <li>
              <p class="font-semibold">五、正文（Text）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 以 Chicago 格式撰寫。章節之標號及圖表之標號，中文之章節款，請按「一、（一）1.（1）」等順序排列。英文稿件請將章節標題置於正文中央，小標題則由稿左緣向右寫。</li>
                <li>2. 本文及段落內引文採「11pt 新細明體」，英文採 Times New Roman。梵巴文採用 Times New Roman、Foreign1。</li>
                <li>3. 中英紀元年代、頁數，及文字敘述中之數字，請以阿拉伯數字書寫。</li>
                <li>4. 短引文可用引號直接引入正文。長引文可作獨立引文，不加引號，採「11pt 標楷體」、內縮三格編排。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">六、誌謝（Acknowledgement）</p>
              <p class="ml-4 mt-1 text-gray-700">載明協助完成論文之個人姓名、服務機構與協助事項，以及提供經費、設備等之單位名稱，以便讀者進一步追蹤研究。</p>
            </li>
            <li>
              <p class="font-semibold">七、註釋（Notes）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 註釋附在當頁之末；每註另起一行，其編號以每篇論文為單位，依序排列。</li>
                <li>2. 註釋號碼請用阿拉伯數字。如在正文中，置於正文右上角、標點符號之後；如係引文，則置於引文末之右上角。</li>
                <li>3. 請勿於正文中直接列出出處（如：張春興（1992：10-25）），請於註釋中詳列出處。</li>
                <li>4. 註釋採「10pt 細明體」編排。</li>
                <li>5. 第一次引用專書或文章時應註明全名及出版項，第二次以後則可使用簡稱。</li>
                <li>6. 註釋內引用文獻與正文同，惟須在全篇論文之後的參考文獻詳細列出。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">八、參考書目（References）</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 所列出的書目，必須與註解引用之書目相符。</li>
                <li>2. 單篇論文依「作者，〈論文篇名〉，《期刊名稱》卷號或期號，出版地：出版者，出版年」次序書寫。例：張春興，〈社會變遷與青少年問題——台灣地區事實的觀察與分析〉，《教育心理學報》第25期，台北：台灣師大，2006年。Post, John F., “Infinite Regresses of Justification and of Explanation”, <em>Philosophical Studies</em> 38, Chicago: The University of Chicago Press, 1987.</li>
                <li>3. 專書依「作者，《書名》，出版地：出版者，出版年」次序書寫。例：王文俊，《人文主義與教育》，台北：五南，1980年。Simon During (ed.), <em>Three Faces of Desire</em>, 3rd edition, translated by Brian Massumi, London: Verso, 1998.</li>
                <li>4. 西文書名、期刊名請用斜體字，單篇論文名請用正體加上「“ ”」。其他未規定之格式，請採用美國芝加哥大學出版 The Manual of Style 1993 年第 14 版有關人文學門之規範。</li>
                <li>5. 參考書目之書寫請全篇一致，切勿將不同之書寫方法混合使用。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">九、附圖、附表</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. 圖表須注意縮版印刷後（例如 A4 縮成 B5），仍能完整清晰。</li>
                <li>2. 圖表之說明須清楚，所使用之文字、數字及符號須與文中一致。</li>
                <li>3. 本學報為黑白印刷，建請勿用彩色之圖表，以免轉檔後影響圖表內涵。</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">十、特定規格</p>
              <p class="ml-4 mt-1 text-gray-700">以上為一般性之參考格式，但論文因領域不同而有其特定規格者，依其特定規格處理。</p>
            </li>
          </ol>

          <div class="mt-6 bg-gray-50 border border-gray-200 px-5 py-4">
            <p class="font-semibold mb-1">【稿件編排】</p>
            <p class="text-base text-gray-700">第一頁列印中文題目、作者中文姓名及職稱、中文摘要、中文關鍵詞；第二頁列印英文題目、作者英文姓名及職稱、英文摘要、英文關鍵詞。內文則由第三頁開始列印，以每頁二十五行、每行三十一字為原則；註釋附在當頁下緣，參考書目列於論文後面。</p>
          </div>
        </div>
      </div>

      <!-- EN Content -->
      <div v-else class="space-y-6 text-[17px] leading-relaxed">
        <p class="text-center font-bold text-xl">Call for Papers — Hsuan Chuang Journal of Buddhism Studies</p>

        <p>The <em>Hsuan Chuang Journal of Buddhism Studies</em> (HCJBS) publishes original scholarly articles in Buddhist studies, including Buddhist doctrine, history, art, literature, psychology, sociology, and education. Submissions must not have been previously published in any form. The journal is published twice a year: March 30 (spring) and September 30 (fall).</p>

        <p>Submissions are accepted year-round without deadlines. For thematic issues, please indicate the relevant theme when submitting. Upcoming thematic issues are listed below:</p>

        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-base text-center" style="font-family: 'Times New Roman', Times, sans-serif;">
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

        <p>Manuscripts should conform to HCJBS formatting guidelines, prepared in Microsoft Word, A4, vertical layout, 11pt font. Manuscripts should be 8,000–15,000 characters (Chinese) or equivalent in English. Authors are responsible for proofreading and for the content of accepted articles; copyright is transferred to the journal. Authors receive five complimentary copies of the issue. Owing to the cost of international airmail, from 2025 onward authors based outside Taiwan receive one printed copy together with a complete PDF of the article (cover, imprint page, table of contents, and article).</p>

        <p>Upon acceptance, authors grant the journal the right to sublicense the article to the National Central Library's “Taiwan Periodical Literature Index System” and other database providers for reproduction, online delivery, downloading, printing, and browsing, and to make minor formatting adjustments as such databases require.</p>

        <p class="text-sm text-gray-600">* Contact: Ven. Jianyi, Tel. 0982-215-945</p>

        <div class="border-t border-gray-200 pt-6">
          <p class="font-bold mb-4">Manuscript Format Guidelines</p>
          <p class="text-base mb-3">Manuscripts should be arranged in the following order:</p>
          <ol class="list-none space-y-4 text-base">
            <li>
              <p class="font-semibold">I. Article Title</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Provide both Chinese and English titles.</li>
                <li>2. The title should concisely reflect the content of the article.</li>
                <li>3. The title should contain the principal keywords.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">II. Author</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Provide the author's name in both Chinese and English.</li>
                <li>2. State the author's institutional affiliation and academic title in both Chinese and English.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">III. Abstracts</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Provide both a Chinese and an English abstract.</li>
                <li>2. For a Chinese article, the Chinese abstract precedes the English one; for an English article, the English abstract comes first.</li>
                <li>3. Abstracts should cover the aims, methods, results, and conclusions of the research, and should incorporate the keywords.</li>
                <li>4. Abstracts must not exceed one page.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">IV. Keywords</p>
              <p class="ml-4 mt-1 text-gray-700">Up to five keywords in each language, placed below the respective abstracts.</p>
            </li>
            <li>
              <p class="font-semibold">V. Text</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Follow the Chicago style. Chinese section numbering follows the sequence 一、（一）1.（1）. In English manuscripts, section headings are centered and subheadings are flush left.</li>
                <li>2. Chinese body text and block quotations use 11pt MingLiU; English uses Times New Roman; Sanskrit and Pāli use Times New Roman or Foreign1.</li>
                <li>3. Dates, page numbers, and numerals in the text are given in Arabic numerals.</li>
                <li>4. Short quotations may be run into the text within quotation marks. Long quotations are set as block quotations without quotation marks, in 11pt KaiU, indented three spaces.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">VI. Acknowledgements</p>
              <p class="ml-4 mt-1 text-gray-700">Name the individuals and institutions that assisted the research and the nature of their assistance, as well as sources of funding and equipment, so that readers may follow up the research.</p>
            </li>
            <li>
              <p class="font-semibold">VII. Notes</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Notes appear as footnotes at the bottom of the page, each on a new line, numbered consecutively within the article.</li>
                <li>2. Note numbers use Arabic numerals, placed as superscripts after punctuation in the text, or at the end of a quotation.</li>
                <li>3. Do not give sources in the running text (e.g. “Chang 1992: 10-25”); give full sources in the notes.</li>
                <li>4. Notes are set in 10pt MingLiU.</li>
                <li>5. Give the full title and publication details at first citation; short titles may be used thereafter.</li>
                <li>6. Works cited in the notes must also be listed in full in the references at the end of the article.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">VIII. References</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. The reference list must correspond to the works cited in the notes.</li>
                <li>2. Journal articles: Author, “Article Title”, <em>Journal</em> volume or issue number, Place: Publisher, Year. E.g. Post, John F., “Infinite Regresses of Justification and of Explanation”, <em>Philosophical Studies</em> 38, Chicago: The University of Chicago Press, 1987.</li>
                <li>3. Books: Author, <em>Title</em>, Place: Publisher, Year. E.g. Simon During (ed.), <em>Three Faces of Desire</em>, 3rd edition, translated by Brian Massumi, London: Verso, 1998.</li>
                <li>4. Western book and journal titles are italicized; article titles are set in roman within quotation marks. For matters not specified here, follow the humanities conventions of <em>The Chicago Manual of Style</em>, 14th edition (1993).</li>
                <li>5. Use one consistent citation format throughout the article.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">IX. Figures and Tables</p>
              <ul class="list-none ml-4 mt-1 space-y-0.5 text-gray-700">
                <li>1. Figures and tables must remain complete and legible after reduction in printing (e.g. A4 reduced to B5).</li>
                <li>2. Captions must be clear, and the text, numerals, and symbols used must agree with those in the article.</li>
                <li>3. The journal is printed in black and white; please avoid color figures and tables.</li>
              </ul>
            </li>
            <li>
              <p class="font-semibold">X. Field-specific formats</p>
              <p class="ml-4 mt-1 text-gray-700">The above are general guidelines; where a field has its own established conventions, those conventions may be followed.</p>
            </li>
          </ol>

          <div class="mt-6 bg-gray-50 border border-gray-200 px-5 py-4">
            <p class="font-semibold mb-1">[Manuscript Layout]</p>
            <p class="text-base text-gray-700">Page 1: Chinese title, author's Chinese name and title, Chinese abstract, and Chinese keywords. Page 2: English title, author's English name and title, English abstract, and English keywords. The body text begins on page 3, set at 25 lines per page and 31 characters per line; notes appear at the foot of each page, and the references follow the article.</p>
          </div>
        </div>
      </div>

      <!-- Download button -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: 'Times New Roman', Times, sans-serif;">
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
useHead({ title: "玄奘大學 - 投稿指引", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const issuesZh = [
  ['第47期', '劉宇光教授', '梵漢藏佛典翻譯',         '115年10月', '116年3月'],
  ['第48期', '蕭麗華教授', '佛教文學',               '116年4月',  '116年9月'],
  ['第49期', '何日生教授', '應用佛學',               '116年10月', '117年3月'],
  ['第50期', '侯坤宏教授', '東亞佛教',               '117年4月',  '117年9月'],
  ['第51期', '李玉珍教授', '跨境越界的比丘尼',       '117年10月', '118年3月'],
  ['第52期', '林朝成教授', '佛教心理學',             '118年4月',  '118年9月'],
  ['第53期', '侯坤宏教授', '佛教文獻學',             '118年10月', '119年3月'],
  ['第54期', '何日生教授', '佛教組織研究',           '119年4月',  '119年9月'],
  ['第55期', '嚴瑋泓教授', 'AI的研究倫理與應用倫理', '119年10月', '120年3月'],
  ['第56期', '劉宇光教授', '當代東南亞上座部佛教',   '120年4月',  '120年9月'],
]

const issuesEn = [
  ['Vol. 47', 'Prof. Liu Yu-guang',    'Sanskrit–Chinese–Tibetan Translation', 'Oct. 2026', 'Mar. 2027'],
  ['Vol. 48', 'Prof. Hsiao Li-hua',    'Buddhist Literature',                  'Apr. 2027', 'Sep. 2027'],
  ['Vol. 49', 'Prof. Ho Jih-sheng',    'Applied Buddhism',                     'Oct. 2027', 'Mar. 2028'],
  ['Vol. 50', 'Prof. Hou Kun-hung',    'East Asian Buddhism',                  'Apr. 2028', 'Sep. 2028'],
  ['Vol. 51', 'Prof. Li Yu-chen',      'Crossing Borders: Buddhist Nuns',      'Oct. 2028', 'Mar. 2029'],
  ['Vol. 52', 'Prof. Lin Chao-cheng',  'Buddhist Psychology',                  'Apr. 2029', 'Sep. 2029'],
  ['Vol. 53', 'Prof. Hou Kun-hung',    'Buddhist Philology',                   'Oct. 2029', 'Mar. 2030'],
  ['Vol. 54', 'Prof. Ho Jih-sheng',    'Buddhist Organizational Studies',      'Apr. 2030', 'Sep. 2030'],
  ['Vol. 55', 'Prof. Yen Wei-hung',    'Research Ethics & Applied Ethics of AI', 'Oct. 2030', 'Mar. 2031'],
  ['Vol. 56', 'Prof. Liu Yu-guang',    'Contemporary Southeast Asian Theravāda', 'Apr. 2031', 'Sep. 2031'],
]
</script>
