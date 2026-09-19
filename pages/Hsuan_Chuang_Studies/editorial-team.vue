<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: 'Times New Roman,Times,DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: 'Times New Roman', Times, sans-serif;">
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
          <p class="font-bold text-lg mb-3">{{ lang === 'zh' ? '總編輯' : 'Editor-in-Chief' }}</p>
          <table class="w-full border-collapse text-sm" style="font-family: 'Times New Roman', Times, '新細明體', sans-serif;">
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

          <details v-if="lang === 'zh'" class="mt-3 border border-gray-200 bg-gray-50">
            <summary class="cursor-pointer px-4 py-2 text-sm text-gray-700 select-none" style="font-family: 'Times New Roman', Times, '新細明體', sans-serif;">
              簡歷
            </summary>
            <div class="px-5 py-4 bg-white border-t border-gray-200 space-y-3 text-[15px]">
              <div>
                <p class="font-semibold mb-1">一、教育、學術經歷</p>
                <ul class="list-none ml-3 space-y-0.5 text-gray-700">
                  <li>1997 迄今，玄奘大學宗教與文化學系教授。</li>
                  <li>2009 迄今，玄奘大學宗教與文化學系主任。</li>
                  <li>2022，創建臺灣佛教研究中心（玄奘大學臺灣佛教研究中心主任，2022.10～）。</li>
                  <li>玄奘大學藏傳佛教研究中心主任（2019.7～）、應用倫理研究中心主任（2004.6～）。</li>
                  <li>佛教弘誓學院研究部暨專修部教師（1993.10～）。</li>
                  <li>學術專長：倫理學、佛教戒律學、原始佛教、部派佛教、中觀學、唯識學、天台學、華嚴學。</li>
                  <li>截至 2025 年 12 月為止，已出版之著作有專書 35 冊、期刊論文 88 篇、研究計畫與官學合作計畫共 27 項。</li>
                </ul>
              </div>
              <div>
                <p class="font-semibold mb-1">二、社會運動經歷</p>
                <p class="ml-3 text-gray-700">常就動物保護、環境生態、維護人權、性別平權與反賭博合法化相關議題著書立說，並主導或參與各種社會運動行列；現為「反賭博合法化聯盟」召集人（2009.1～）、國際入世佛教協會（INEB）精神導師（patron，2007～）、內政部第 12 屆宗教事務諮詢委員（2023.12～）。</p>
              </div>
              <div>
                <p class="font-semibold mb-1">三、編輯經歷</p>
                <p class="ml-3 text-gray-700">《玄奘佛學研究》編輯委員（2004.1～）兼總編輯（2017.9～）、《弘誓雙月刊》編輯顧問（1992.10～）、《佛學與科學》期刊編輯委員（2002.7～）、玄奘大學《教學實務研究論叢》編輯委員（2021.2～）。</p>
              </div>
              <div>
                <p class="font-semibold mb-1">四、獲頒獎項</p>
                <ul class="list-none ml-3 space-y-0.5 text-gray-700">
                  <li>2012 年 10 月至 2024 年 10 月，連續獲頒十二次教育部「銀質獎章」。</li>
                  <li>2021 年 6 月 2 日，獲第 38 屆庭野和平獎（Niwano Peace Prize）。</li>
                  <li>2025 年 3 月 17 日，獲頒 2025 台灣環境保護終身成就獎。</li>
                  <li>玄奘大學「一一○年度研究優良教師－學術著作獎」、「一一三學年度研究優良教師－研究計畫獎」。</li>
                </ul>
              </div>
            </div>
          </details>
        </div>

        <!-- Editorial Board -->
        <div>
          <p class="font-bold text-lg mb-3">
            {{ lang === 'zh' ? '編輯委員（依姓氏筆畫排序）' : 'Editorial Board Members (in stroke order)' }}
          </p>
          <table class="w-full border-collapse text-sm" style="font-family: 'Times New Roman', Times, '新細明體', sans-serif;">
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
                <td class="border border-gray-300 px-4 py-2 text-gray-600 text-sm">
                  {{ lang === 'zh' ? m.zhSpec : m.enSpec }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Member profiles (ZH only) -->
        <div v-if="lang === 'zh'">
          <p class="font-bold text-lg mb-3">編輯委員簡歷</p>
          <div class="border border-gray-200 divide-y divide-gray-200">
            <details v-for="m in members" :key="`bio-${m.zhName}`" class="bg-white">
              <summary class="cursor-pointer px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 select-none" style="font-family: 'Times New Roman', Times, '新細明體', sans-serif;">
                {{ m.zhName }}<span class="text-gray-400 mx-2">｜</span><span class="text-gray-500">{{ m.zhInst }}</span>
              </summary>
              <div class="px-5 py-4 bg-gray-50 border-t border-gray-200 space-y-2 text-[15px] leading-relaxed">
                <p v-for="(para, i) in m.bio" :key="i" :class="para.startsWith('【') ? 'font-semibold' : 'text-gray-700'">
                  {{ para }}
                </p>
              </div>
            </details>
          </div>
        </div>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: 'Times New Roman', Times, sans-serif;">
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
useHead({ title: "玄奘大學 - 編輯委員", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const members = [
  {
    zhName: '王三慶', enName: 'Wang San-ching',
    zhInst: '成功大學中國文學系', enInst: 'Dept. of Chinese Literature, National Cheng Kung University',
    zhSpec: '敦煌學、聲韻學、古典小說', enSpec: 'Dunhuang Studies, Phonology, Classical Fiction',
    bio: [
      '【學歷】文化大學中國文學系學士、臺灣師範大學國文學系碩士、文化大學中國文學系國家文學博士。',
      '【經歷】文化大學中國文學系教授、系主任；日本天理大學中文學科交換教授；成功大學文學院院長；日本東京大學東洋文化研究所訪問教授；成功大學研究總中心臺灣文化中心主任；成功大學通識中心主任。',
      '【專長】敦煌學、聲韻學、古典小說。',
    ],
  },
  {
    zhName: '何日生', enName: 'Ho Jih-sheng',
    zhInst: '慈濟大學宗教與文化研究所', enInst: 'Graduate Inst. of Religion and Culture, Tzu Chi University',
    zhSpec: '應用佛學、慈善組織', enSpec: 'Applied Buddhism, Philanthropic Organizations',
    bio: [
      '【現職】慈濟慈善事業基金會副執行長；慈濟基金會學術諮詢委員會主席；美國哈佛大學文理學院 CAMLab 特聘學者；美國加州大學柏克萊分校商學院資深顧問；慈濟大學人文社會學院兼任副教授；政治大學社會科學學院兼任副教授；浙江大學歷史學院善文明研究中心聯席主任；南京大學哲學院客座教授；深圳國際公益研究院特聘教授；中國人民大學宗教高等研究院研究員；中華佛典基金會（CBETA）董事；《印證佛學》期刊中、英文版共同主編。',
      '【學歷】2016 年北京大學哲學系哲學博士；1995 年美國南加州大學安納堡傳播學院傳播管理暨傳播政策碩士；1993 年美國加州大學傅樂頓分校廣播電視暨電影學院學士；1984 年台灣藝術專科學校廣播電視科。',
    ],
  },
  {
    zhName: '李玉珍', enName: 'Li Yu-chen',
    zhInst: '政治大學宗教研究所', enInst: 'Graduate Inst. of Religious Studies, National Chengchi University',
    zhSpec: '佛教文學、臺灣佛教、宗教與性別', enSpec: 'Buddhist Literature, Taiwanese Buddhism, Religion & Gender',
    bio: [
      '【學歷】2000 年美國康乃爾大學東亞文學所博士，清華大學歷史所碩士。',
      '【現職】國立政治大學宗教研究所教授兼所長，華人文化元宇宙中心副主任。',
      '【專長】佛教文學、臺灣佛教、宗教與性別、觀音研究。',
      '【著作】《唐代的比丘尼》、《佛教文學裡的聖凡男女》、《戰後台灣佛教與婦女》，主編《跨領域的宗教與性別研究》、《台灣佛教的人物與寺院》等書，以及中英文論文數十篇。',
      '【學術服務】曾任國科會哲學學門與人類學門召集人與審查委員；現擔任佛光大學、法鼓文理學院、慈濟基金會、臺灣佛教研究中心、唯心聖教、政治大學華人宗教研究中心等單位校外學術諮詢委員。',
    ],
  },
  {
    zhName: '李瑞全', enName: 'Lee Shui-chuen',
    zhInst: '中央大學哲學研究所', enInst: 'Dept. of Philosophy, National Central University',
    zhSpec: '儒學、生命倫理學、康德哲學', enSpec: 'Confucianism, Bioethics, Kantian Philosophy',
    bio: [
      '師從唐君毅先生、牟宗三先生。',
      '【學歷】香港新亞書院哲學系文學士（一級榮譽）、香港中文大學哲學碩士、美國南依利諾大學哲學博士。',
      '【經歷】東海大學副教授；中央大學哲學研究所教授、所長、中國哲學研究中心主任；嶺南大學訪問教授（2017）；北京大學醫學部醫學人文研究院訪問教授（2017）；山東大學齊魯醫學院醫學人文研究所博士導師（2008 迄今）；香港新亞研究所榮譽教授。曾任《鵝湖月刊》社長、《應用倫理研究通訊》創刊主編、中央大學文學院人文學報主編、《鵝湖學誌》主編、台灣生命倫理學會創會理事長。',
      '【專長】儒學、生命倫理學、英美哲學、康德哲學。',
      '【著作】《當代新儒學之哲學開拓》（文津，1993）、《休謨》（三民，1993）、《儒家生命倫理學》（鵝湖，1999）、《應用倫理與現代社會》（合著，空中大學，2006）、《醫療倫理諮詢——理論與實務》（合著，五南，2008）、《儒家道德規範根源論》（鵝湖，2013），並編有 The Family, Medical Decision-Making, and Biotechnology: Critical Reflections on Asian Moral Perspectives（Springer, 2007）等書；出版中英文論文二百多篇。',
    ],
  },
  {
    zhName: '林保堯', enName: 'Lin Bao-yao',
    zhInst: '臺北藝術大學文化資源學院', enInst: 'College of Cultural Resources, Taipei National Univ. of the Arts',
    zhSpec: '佛教藝術、文化資產', enSpec: 'Buddhist Art, Cultural Heritage',
    bio: [
      '【現職】國立臺北藝術大學名譽教授（2014.01～）；建築與文化資產研究所兼任教授（2013.02～）。',
      '【學歷】日本國立筑波大學藝術學研究科博士、地域研究研究科碩士。',
      '【經歷】（1985.09–2013.01）國立臺北藝術大學建築與文化資產研究所、傳統藝術研究所、美術史研究所專任教授；傳統藝術研究中心主任；總務長兼代文化資源學院院長。',
    ],
  },
  {
    zhName: '林朝成', enName: 'Lin Chao-cheng',
    zhInst: '成功大學中國文學系', enInst: 'Dept. of Chinese Literature, National Cheng Kung University',
    zhSpec: '應用倫理學、佛教哲學、佛教生態學', enSpec: 'Applied Ethics, Buddhist Philosophy, Buddhist Ecology',
    bio: [
      '【學歷】1992 年台灣大學哲學博士。',
      '【現職】國立成功大學兼任教授、台南社區大學校長。',
      '【經歷】曾任國立成功大學佛學研究中心主任、健康城市研究中心主任、推廣教育中心主任、中國文學系主任。',
      '【專長】應用倫理學、佛教哲學、佛教生態學、魏晉思想與成人教育哲學。',
      '【著作】《魏晉玄學的自然觀與自然美學研究》；〈人間佛教的環境關懷與深層生態學的銜接與對話〉、〈佛教護生、放生與功德的傳統思維及其面向當代社會的相關考察〉、〈台灣人間佛教環境論述的面向與省思〉等佛教生態學論著十餘篇；譯有《佛教與生態學：佛教的環境倫理與環保實踐》、《禪宗心理學》、《食農社會學》；並出版《佛學概論》、《曾文溪流域綜論》等教學用書。',
      '【編輯經歷】曾任《佛學研究中心學報》編委、《成大宗教與文化學報》主編、《成大中文學報》主編，現任《玄奘佛學研究》編輯委員。',
    ],
  },
  {
    zhName: '邱敏捷', enName: 'Chiu Min-chieh',
    zhInst: '臺南大學國語文學系', enInst: 'Dept. of Chinese Language and Literature, National Univ. of Tainan',
    zhSpec: '佛學研究、佛教文學、臺灣佛教', enSpec: 'Buddhist Studies, Buddhist Literature, Taiwanese Buddhism',
    bio: [
      '【學歷】國立中山大學中國文學研究所文學博士。',
      '【現職】國立臺南大學國語文學系專任教授。',
      '【專長】佛學研究、佛教文學、臺灣佛教。',
      '【著作】《以佛解莊——以《莊子》註為線索之考察》、《印順《中國禪宗史》之考察——兼與胡適及日本學者相關研究的比較》、《《肇論》研究的衍進與開展》、《文學與佛經》、《留住蓮音》、《印順導師的佛教思想》等書，以及期刊論文數十餘篇。',
    ],
  },
  {
    zhName: '侯坤宏', enName: 'Hou Kun-hung',
    zhInst: '玄奘大學宗教與文化學系', enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',
    zhSpec: '近代漢傳佛教史、戰後臺灣史', enSpec: 'Modern Chinese Buddhism History, Post-war Taiwan History',
    bio: [
      '【學歷】國立政治大學歷史學博士。',
      '【經歷】1986 年起任職國史館，2015 年 2 月自國史館退休；2020 年 2 月起於玄奘大學宗教與文化學系擔任教授，目前已退休。',
      '【專長】近代中國財經史、戰後臺灣史（二二八史、臺灣白色恐怖史）、近代漢傳佛教史。',
      '【著作】《抗戰時期的中央財政與地方財政》、《研究二二八》、《印順法師年譜》、《真實與方便：印順思想研究》、《仁俊法師學譜》、《浩劫與重生：一九四九年以來的大陸佛教》、《流動的女神——觀音與媽祖》、《太虛時代：多維視角下的民國佛教（1912–1949）》、《論戰後臺灣佛教》、《論近代香港佛教》、《論馬來西亞近代漢傳佛教：一個局外人的觀察》、《印順導師年譜》（一套四冊）等書；並主持《臺灣佛教一甲子：吳老擇先生訪談錄》、《浩蕩赴前程：昭慧法師訪談錄》、《無悔前行：佛教藝術澱積者釋寬謙口述史》、《法燈薪傳：傳證法師訪談錄》等 22 冊口述歷史叢書。',
    ],
  },
  {
    zhName: '張瓈文', enName: 'Chang Li-wen',
    zhInst: '輔仁大學英國語文學系', enInst: 'Dept. of English Language & Literature, Fu Jen Catholic University',
    zhSpec: '英語教學、翻譯、比較文學、佛教文學', enSpec: 'English Teaching, Translation, Comparative Literature, Buddhist Literature',
    bio: [
      '【學歷】輔仁大學比較文學研究所博士（1995–2007）、英國語文學研究所碩士（1988–1992）、英國語文學系學士（1984–1988）。',
      '【經歷】輔仁大學英國語文學系講師、專任副教授（2007 迄今）；英國語文學系進修學士班主任（2008.08–2013.07）。',
      '【專長】英語教學、翻譯、比較文學（比較戲劇、文學與宗教、佛教文學與跨藝術研究、精神分析與佛教對話研究）。',
    ],
  },
  {
    zhName: '黃運喜', enName: 'Huang Yun-hsi',
    zhInst: '玄奘大學宗教與文化學系', enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',
    zhSpec: '宗教史、宗教事務管理', enSpec: 'Religious History, Religious Administration',
    bio: [
      '【專長】宗教史及宗教實務類課程；宗教事務管理（含宗教法規、宗教財產管理、宗教行政管理等）。',
      '【經歷】玄奘大學宗教學系教授（2006.08～），2007.05–2009.02 兼文理學院院長、2007.08–2009.02 兼系主任；歷史系教授兼主任（2007.02–2007.07）；宗教學系副教授（1997.08–2006.07），1999–2002 兼主任；2011 年擔任「生命禮儀學位學程」系主任；玄奘大學第一、二屆董事，第一任學務長、第二任總務長；玄奘大學籌備處行政組組長（1993–1997）。',
      '【學術與社會服務】台灣宗教學會理事；新竹市政府客家事務委員會委員；慈恩地政士事務所所長（1998.08～）；新竹地方法院榮譽觀護人、調解委員；台北市文山社區大學、新竹市青草湖社區大學發起人；新竹市社區大學促進會第一任理事長；印順佛教基金會董事（2007.03～）；覺風佛教藝術文化基金會董事（2007.05～）；新竹市政府傳統民俗藝術及有關文物、古物類審議委員會委員（2008.06–2010.05）。',
      '【編輯經歷】《玄奘佛學研究》主編；《竹塹文獻》、《新竹文獻》主編（不定期）；《獅子吼》月刊主編（1985）；《新竹青年》主編（1986–1987）。',
    ],
  },
  {
    zhName: '葉海煙', enName: 'Yeh Hai-yen',
    zhInst: '成功大學中國文學系', enInst: 'Dept. of Chinese Literature, National Cheng Kung University',
    zhSpec: '道家哲學、倫理學', enSpec: 'Taoist Philosophy, Ethics',
    bio: [
      '【學歷】輔仁大學哲學研究所博士。',
      '【現職】國立成功大學通識教育中心兼任教授。',
      '【學術經歷】美國哈佛大學訪問學者（1994–1995）；東吳大學哲學系專任教授（1996–2008）、教授兼系主任（1996–2002）；長榮大學哲學與宗教學系教授兼系主任（2008–2011）；國立成功大學中國文學系專任教授（2011–2017）、教授兼系主任（2012–2015）；國立臺灣大學人文社會高等研究院訪問學者（2015.08）；英國威爾斯大學漢學院兼任講座（2025）。',
      '【服務經歷】臺北市文化局錢穆故居執行長（2002–2008）；臺灣哲學學會理事長（2004–2005）；中國哲學學會常務理事（2004–2010）；臺南市哲學學會理事長（2013–2015）；財團法人臺南市至善教育基金會漢學顧問（2023.12–2025.11）。',
      '【著作】《莊子的生命哲學》（2021 年第三版修訂印行）、《道德、理性與人文的向度》（1996）、《老莊哲學新論》（1997）、《人文與哲學的對話》（1999）、《中國哲學的倫理觀》（2005 初版二刷）、《哲學與人生》（2008 初版二刷）、《傳統倫理的現代挑戰》（2008）、《道家倫理學：理論與實踐》（2016）、《哲學現場》（2020）、《跨領域的道家哲學》（2022）、《儒家倫理與文化交談》（2026）。',
    ],
  },
  {
    zhName: '蕭麗華', enName: 'Hsiao Li-hua',
    zhInst: '佛光大學中國文學與應用學系', enInst: 'Dept. of Chinese Literature, Fo Guang University',
    zhSpec: '東亞漢詩、中國詩學、佛教文學', enSpec: 'East Asian Sinitic Poetry, Chinese Poetics, Buddhist Literature',
    bio: [
      '【學歷】1992 年臺灣大學中文所博士。',
      '【現職】佛光大學語文學榮譽教授；國語日報《古今文選》主編。',
      '【經歷】元智大學通識教育中心副教授、心理輔導中心主任；臺大中文系教授、臺灣大學佛學研究中心主任、臺大中文系副主任、《臺大佛學研究中心學報》主編、《臺大中文學報》主編；現代佛教學會第四屆理事長；中國唐代學會第九屆理事長；2005 年中央研究院文哲所短期訪問學人，2009 年捷克查理士大學短期訪問學人，2012 年京都大學短期訪問學人，2015 年京都立命館大學短期訪問學人；2018–2025 年佛光大學中國文學與應用學系教授兼人文學院院長。',
      '【專長】東亞漢詩、中國詩學、佛教文學、文學理論、教育等；主要研究領域為詩歌與禪學。',
      '【著作】師大碩士論文《論杜詩沈鬱頓挫之風格》（1986）、臺大博士論文《元詩之社會性與藝術性研究》（1992）；《古今詩史第一人——杜甫》、《道心禪悅一詩佛——王維》、《唐代詩歌與禪學》、《「文字禪」詩學發展的軌跡》、《從王維到蘇軾——詩歌與禪學交會的黃金時代》、《東亞漢詩與佛教文化之傳播》、《走進禪詩——禪詩中的禪史》、《從中古到臺灣本土的觀音信仰》、《詩·茶·禪——東坡詩禪與茶禪》；散文集《佛光，文學之道》；編撰《佛光中文吟社詩草》、《蘭陽飲食文學食單》、《中國佛教文學史》、《四藝三昧茶道展演》。',
    ],
  },
  {
    zhName: '嚴瑋泓', enName: 'Yen Wei-hung',
    zhInst: '成功大學中國文學系', enInst: 'Dept. of Chinese Literature, National Cheng Kung University',
    zhSpec: '儒家哲學、生命倫理學、應用倫理學', enSpec: 'Confucian Philosophy, Bioethics, Applied Ethics',
    bio: [
      '【學歷】國立臺灣大學哲學系博士。',
      '【現職】國立成功大學中國文學系教授兼系主任（2026.02～）。',
      '【經歷】國立成功大學中國文學系教授兼代理系主任（2025.10–2026.01）、教授（2023.08 迄今）；東海大學哲學系教授（2021.02–2023.07）、副教授（2016.02–2021.01）、助理教授（2011.02–2016.01）；中央研究院中國文哲研究所科技部國內訪問學人（2018.08–2019.07）；國科會人文學研究中心博士後研究員（2010.08–2011.01）；中央研究院中國文哲研究所博士候選人（中央研究院 98 年度人文社會科學博士候選人培育計畫，2009.08–2010.07）；德州大學奧斯汀分校哲學系訪問學人（國科會 96 年度補助博士生赴國外研究，2008.07–2009.08）。',
    ],
  },
  {
    zhName: '根瑟·馬庫斯', enName: 'Marcus Günzel',
    zhInst: '玄奘大學宗教與文化學系', enInst: 'Dept. of Religion and Culture, Hsuan Chuang University',
    zhSpec: '漢傳佛教、德語佛學文獻', enSpec: 'Chinese Buddhism, German-language Buddhist Scholarship',
    bio: [
      '【學歷】Ph.D., Universität Göttingen。',
      '【經歷】玄奘大學宗教學研究所副教授。',
      '【專書與翻譯】Die Morgen- und Abendliturgie der chinesischen Buddhisten, Göttingen 1994；Die Taiwan-Erfahrung des chinesischen Sangha – Zur Entwicklung des buddhistischen Mönchs- und Nonnenordens in der Republik China nach 1949, Göttingen 1998；（譯）Zhenhua, Lehr- und Wanderjahre eines chinesischen Mönches, Norderstedt 2000；（譯）Fritz Stolz，《宗教學概論》，2001，台北：華泰；（譯）瓦鄧布葛，《宗教學入門》，2003，台北：東大；Der Geist weilt nirgends – Drei Texte zur Meditationspraxis des Chan und der Lehre vom Reinen Land, Berlin 2007；Das Sutra von den acht Einsichten der erhabenen Menschen, Berlin 2008；Das allumfassende Tor zur Befreiung – Das Guanyin-Kapitel aus dem Lotossutra mit einem Kommentar des Dharmameisters Daoyuan, Berlin 2010；尼古拉·哈特曼著，根瑟·馬庫斯、劉貴傑譯，《哲學概論》，2011，臺北：巨流；Das Sutra von der Vollkommenen Erleuchtung (Yuanjuejing): Übersetzung und Kommentar, Berlin 2023。',
    ],
  },
]
</script>
