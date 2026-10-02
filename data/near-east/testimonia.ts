// 附錄 —— 外部記述（非經典）
//
// 🚨 scriptural = false。這一藏沒有一條是古近東宗教的信徒為自己的神寫的。
//   收的是兩類外人的記述：
//   ① 希臘化時代用希臘文替自己的傳統作傳的本地祭司（貝羅索斯、曼涅托）——人是內部的，
//      語言與讀者是外部的，原書已佚、只剩引文；
//   ② 希臘羅馬、基督教與伊斯蘭作者的轉述——在楔形與聖書體被重新解讀之前，
//      歐洲人對古近東宗教的全部認識都來自這一批。
//
// 與希臘羅馬大藏經的關係：其中幾部（普魯塔克、琉善、達馬斯基烏斯、楊布里科斯）在那邊是**本經**，
//   在這裡是**外部證詞**。同一部書在兩座圖書館各有位置，互見不合併（同 hellenika-canon §6）。

import type { NeCanon } from './types'

const GRK = '古希臘文'

export const TESTIMONIA_CANON: NeCanon = {
  key: 'testimonia',
  name: '附錄：外部記述',
  name_en: 'Appendix: External Testimonia',
  glyph: '附',
  subtitle: '希臘、羅馬、教父與伊斯蘭作者眼中的古近東宗教',
  scriptural: false,
  language: '古希臘文、拉丁文、阿拉伯文',
  era: '約前 450 – 公元 11 世紀',
  terminus: '收至哈蘭薩比教的最後記載（11 世紀）——古近東多神信仰最晚的倖存者。',
  columns: { orig: 'available', en: 'available', zh: 'none' },
  summary:
    '十九世紀解讀楔形文字與聖書體之前，歐洲人知道的「巴比倫宗教」「埃及宗教」全部來自這一藏：'
    + '希羅多德的遊記、普魯塔克的哲學詮釋、教父為駁斥異教而保存的引文。'
    + '它們不是古近東宗教的經典，而是它的回聲——有時是忠實的轉述，有時是希臘人自己的投射。'
    + '引用前要先問：作者讀得懂原文嗎？他是在描述，還是在詮釋？',
  volumes: [
    {
      key: 'native-greek',
      sigil: '附一',
      name: '本地祭司的希臘文著作',
      name_en: 'Native Priests Writing in Greek',
      era: '前 3 世紀；殘篇經後世轉引',
      summary: '亞歷山大之後，巴比倫與埃及的祭司各自用希臘文替本國的歷史與宗教寫了一部書，獻給新的希臘君主。兩部原書都已佚失。',
      divisions: [
        {
          key: 'priests',
          label: '祭司史家',
          label_en: 'Priest-Historians',
          texts: [
            { slug: 'berossus', title_zh: '貝羅索斯《巴比倫尼亞志》', title_orig: 'Βαβυλωνιακά', author: '貝羅索斯（巴比倫貝勒—馬杜克神廟祭司）', era: '約前 290–278', language: GRK, status: 'lost-cited', extent: '原三卷', via: '約瑟夫《駁阿皮翁》、優西比烏《編年史》（經亞歷山大‧波利希斯托轉引）、辛凱洛斯', note: '魚身人首的智者俄安涅斯從海中上岸教人文明；洪水英雄克西蘇特羅斯——即蘇美的吉烏蘇德拉。一位讀得懂楔形泥板的祭司寫給希臘讀者的版本。', seealso: ['sumerian-flood', 'enuma-elish'] },
            { slug: 'manetho', title_zh: '曼涅托《埃及志》', title_orig: 'Αἰγυπτιακά', author: '曼涅托（塞本尼托斯祭司）', era: '約前 280', language: GRK, status: 'lost-cited', extent: '原三卷', via: '約瑟夫《駁阿皮翁》、阿非利加努斯與優西比烏（經辛凱洛斯）', note: '今日埃及學仍沿用的「三十王朝」分法出自此書。另著有《聖書》論埃及宗教，全佚。曼涅托也參與了薩拉皮斯崇拜的設立。', xref: ['希臘羅馬大藏經 Ν 城邦紀年（薩拉皮斯之立）'] },
          ],
        },
      ],
    },
    {
      key: 'classical',
      sigil: '附二',
      name: '希臘羅馬作者',
      name_en: 'Greek and Roman Authors',
      era: '前 5 世紀 – 公元 6 世紀',
      summary: '旅人、哲學家與最後的新柏拉圖主義者。他們把近東的神翻譯成希臘的神（「詮釋為希臘」），這個翻譯本身就是一份宗教史材料。',
      divisions: [
        {
          key: 'greek-roman',
          label: '轉述與詮釋',
          label_en: 'Report and Interpretation',
          texts: [
            { slug: 'herodotus-2', title_zh: '希羅多德《歷史》卷二（埃及）與卷一（巴比倫）', title_orig: 'Ἱστορίαι II; I.178–200', author: '希羅多德', era: '約前 430', language: GRK, status: 'whole', note: '埃及人是最敬神的民族；希臘的神名大多來自埃及。巴比倫塔廟頂上有一張床，神夜裡來與選定的女子同寢。耳聞與目睹混雜，引用時要分。', xref: ['希臘羅馬大藏經 Ν 城邦紀年（希羅多德《歷史》）'] },
            { slug: 'diodorus-1', title_zh: '狄奧多羅斯《歷史叢書》卷一至二', title_orig: 'Βιβλιοθήκη ἱστορική I–II', author: '西西里的狄奧多羅斯', era: '約前 60–30', language: GRK, status: 'whole', note: '卷一埃及、卷二亞述與迦勒底人的占星術。多轉抄已佚的前人。', xref: ['希臘羅馬大藏經 Ξ 聖所志（歷史叢書）'] },
            { slug: 'plutarch-isis', title_zh: '普魯塔克《論伊西斯與奧西里斯》', title_orig: 'Περὶ Ἴσιδος καὶ Ὀσίριδος', author: '普魯塔克', era: '約公元 120', language: GRK, status: 'whole', note: '古代唯一完整講述奧西里斯被弒、肢解、伊西斯尋屍的連貫敘事——埃及本土文獻從不明說的故事，由一位希臘祭司兼哲學家寫成。', seealso: ['great-hymn-osiris'], xref: ['希臘羅馬大藏經 Φ 論神書（本經）'] },
            { slug: 'lucian-syrian-goddess', title_zh: '琉善《論敘利亞女神》', title_orig: 'Περὶ τῆς Συρίης θεοῦ', author: '薩莫薩塔的琉善（署名）', era: '公元 2 世紀', language: '古希臘文（仿伊奧尼亞方言）', status: 'whole', note: '希拉波利斯阿塔加提斯大神廟的實地報導：聖池聖魚、登柱苦行、自宮的祭司，以及一則與丟卡利翁合流的洪水故事。', xref: ['希臘羅馬大藏經 Ξ 聖所志（本經）'] },
            { slug: 'philo-byblos', title_zh: '比布魯斯的斐洛《腓尼基史》', title_orig: 'Φοινικικὴ ἱστορία', author: '比布魯斯的斐洛（譯自託名桑丘尼亞頓）', era: '約公元 100–140', language: GRK, status: 'lost-cited', extent: '原九卷', via: '優西比烏《福音的預備》卷一‧9–10', note: '腓尼基神譜：伊勒（克洛諾斯）閹割其父天神。1929 年烏加里特出土後，學界才確認書中的神名有真實的古代根據。', seealso: ['kumarbi-kingship', 'baal-cycle'], xref: ['基督教大藏經‧前藏（腓尼基史）'] },
            { slug: 'damascius-principles', title_zh: '達馬斯基烏斯《論第一原理》125', title_orig: 'Ἀπορίαι καὶ λύσεις περὶ τῶν πρώτων ἀρχῶν §125', author: '達馬斯基烏斯（雅典學園末任主持）', era: '約公元 530', language: GRK, status: 'whole', note: '最後一位雅典新柏拉圖主義者轉述「巴比倫人」的宇宙生成：Tauthe（提阿瑪特）與 Apason（阿普蘇）、Moymis、Lache 與 Lachos、Kissare 與 Assoros……與《埃努瑪‧埃利什》開頭逐名相合——楔形泥板解讀前，這是西方唯一保存這份神譜的文本。', seealso: ['enuma-elish'], xref: ['希臘羅馬大藏經 Ω 終卷'] },
            { slug: 'iamblichus-mysteries', title_zh: '楊布里科斯《論埃及人的祕儀》', title_orig: 'De Mysteriis Aegyptiorum', author: '楊布里科斯（託名埃及祭司阿巴蒙）', era: '約公元 300', language: GRK, status: 'whole', note: '假託埃及祭司之口為神通術辯護——希臘哲學借用「埃及」作權威的典型。', xref: ['希臘羅馬大藏經 Φ 論神書'] },
            { slug: 'horapollo', title_zh: '赫拉波羅《象形文字》', title_orig: 'Hieroglyphica', author: '赫拉波羅（託名）', era: '約公元 5 世紀', language: GRK, status: 'whole', extent: '兩卷', note: '以寓意解釋聖書體符號（「鷹表示神」），部分正確、大半臆測。文藝復興時被奉為解讀象形文字的鑰匙，誤導歐洲三百年，直到商博良。' },
          ],
        },
      ],
    },
    {
      key: 'later',
      sigil: '附三',
      name: '教父與伊斯蘭作者',
      name_en: 'Church Fathers and Islamic Authors',
      era: '公元 2 – 11 世紀',
      summary: '最後見到古近東多神信仰活著的人。他們記錄的目的是駁斥或是好奇，但他們看見了。',
      divisions: [
        {
          key: 'later-witnesses',
          label: '最後的見證',
          label_en: 'The Last Witnesses',
          texts: [
            { slug: 'clement-hermetic', title_zh: '克萊門《雜記》六‧4 埃及祭司遊行', title_orig: 'Stromata VI.4.35–37', author: '亞歷山卓的克萊門', era: '約公元 200', language: GRK, status: 'whole', note: '目睹埃及祭司遊行時各職司所捧的神廟聖書，記下四十二書的分類。', seealso: ['books-of-thoth'] },
            { slug: 'harran-sabians', title_zh: '阿爾—納迪姆論哈蘭的薩比教', title_orig: 'al-Fihrist, chapter on the Ḥarrānian Ṣābians', author: '阿爾—納迪姆', era: '987', language: '阿拉伯文', status: 'whole', note: '哈蘭人到伊斯蘭時代仍拜月神辛與行星諸神、每年舉行祕密祭禮，以「薩比人」的名義取得「有經者」地位。月神廟約 1032 年被毀——古近東多神信仰最晚的倖存者。', seealso: ['nabonidus-harran', 'sumatar'], xref: ['摩尼教經典‧附錄（群書類述）'] },
            { slug: 'ibn-kalbi-idols', title_zh: '伊本‧卡勒比《偶像書》', title_orig: 'Kitāb al-Aṣnām', author: '希沙姆‧伊本‧卡勒比', era: '約公元 819 前', language: '阿拉伯文', status: 'whole', note: '前伊斯蘭阿拉伯諸部族的偶像與聖所：拉特、歐薩、默納……伊斯蘭學者以保存「蒙昧時代」記憶的立場寫成。', seealso: ['nabataean-dushara', 'safaitic'] },
          ],
        },
      ],
    },
  ],
}
