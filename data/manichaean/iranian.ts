// 續藏二 —— 東方語文藏（吐魯番）
//
// 1902–1914 年，德國四次吐魯番探險隊在高昌故城一帶挖出數以萬計的寫本殘片，
// 其中約四五千件是摩尼教文獻，用中古波斯語、帕提亞語、粟特語、回鶻語與
// 摩尼字母書寫。這批材料一舉改變了整個領域：在此之前摩尼教只是教父書裡的一個異端名字，
// 在此之後它成為一個有自己的語言、詩歌、教曆與教團制度的世界宗教。
//
// ══════════ 為什麼這一藏的編號比書名重要 ══════════
//
//   吐魯番殘片絕大多數沒有書名，也沒有首尾。學界用館藏編號指稱它們：
//   M 開頭是柏林所藏摩尼字母寫本（M 1、M 470…），So 是粟特語，U 是回鶻語。
//   **編號就是這一頁的身分證**：說「M 1」比說「大讚美詩目錄」精確，
//   因為後者是現代學者取的名字，前者是這張紙本身。
//   所以本藏每一條的 siglum 一律填館藏編號，題名反而是輔助。
//
// ══════════ 取源：這一藏是四藏中最好辦的 ══════════
//
//   國際摩尼教研究學會（IAMS, manichaeism.de）開放取用的
//   《東方摩尼教選輯》(Anthologia Manichaica Orientalia) 四冊，
//   把主要殘卷的**原文轉寫與英譯並列**刊出，可直接取用：
//     第一冊 摩尼生平與東方教史 ／ 第二冊 正典 ／ 第三冊 沙卜爾干 ／ 第四冊 讚詩與祈禱
//   故本藏多數條目的 orig 與 en 兩欄都標 available（線上有、待抓），
//   這在摩尼教文獻裡是難得的好處境——科普特藏那邊兩欄幾乎全是 copyright。

import type { ManiCanon } from './types'

const MP = '中古波斯語'
const PA = '帕提亞語'
const SOG = '粟特語'
const UIG = '回鶻語'

/** 本藏多數條目共用：IAMS 選輯已刊原文轉寫與英譯，可取得但尚未抓 */
const IAMS = { orig: 'available', en: 'available', zh: 'none' } as const

export const IRANIAN_CANON: ManiCanon = {
  key: 'iranian',
  name: '東方語文獻',
  name_en: 'The Eastern Iranian and Turkic Texts',
  glyph: '東',
  subtitle: '續藏 — 吐魯番出土的中亞教團寫本',
  scriptural: true,
  language: '中古波斯語、帕提亞語、粟特語、回鶻語（多以摩尼字母書寫）',
  era: '寫本約 8–11 世紀；所譯內容 3 世紀以降',
  summary:
    '摩尼教東傳中亞後，在回鶻汗國一度成為**國教**——'
    + '這是這個宗教在歷史上唯一一次取得國家地位（762 年前後）。'
    + '吐魯番的寫本就是那段時期及其前後留下的：'
    + '讚詩、教曆、懺悔文、教團書信、正典殘葉、乃至寫在華麗細密畫旁的禮儀文。'
    + '它們用摩尼自己設計的字母書寫——一套從敘利亞字母改造而來、'
    + '刻意與祆教和佛教的書寫傳統區別開的文字。'
    + '本藏是四藏中材料最多、取源條件最好的一藏。',
  parts: [
    {
      key: 'p-canon-frag', label: '正典殘卷', label_en: 'Canonical Fragments',
      desc: '七經與《沙卜爾干》在東方語言中的譯本殘葉。正藏那些空著的卷，內容主要靠這一部填。',
      volumes: ['canonical-fragments'],
    },
    {
      key: 'p-hymns', label: '讚詩', label_en: 'Hymn Cycles',
      desc: '帕提亞語的兩大讚詩循環與各類節期讚詩。摩尼教詩歌藝術的高峰。',
      volumes: ['hymn-cycles'],
    },
    {
      key: 'p-church', label: '教團文書', label_en: 'Church Documents',
      desc: '懺悔文、教曆、教團書信、寺院帳目——一個實際運作的宗教組織留下的紙。',
      volumes: ['church-documents'],
    },
  ],
  volumes: [
    {
      key: 'canonical-fragments',
      sigil: '殘',
      name: '正典殘卷',
      name_en: 'Canonical Fragments',
      provenance: '柏林吐魯番藏品（高昌故城、吐峪溝等）',
      era: '寫本 8–11 世紀',
      extent: '數百件殘片',
      summary:
        '七經與《沙卜爾干》譯成東方語言後的殘葉。'
        + '這一卷與正藏是同一批書的兩種看法：'
        + '正藏問「摩尼寫了哪些書」，本卷問「這些書今天還剩哪幾頁、在誰手裡」。'
        + '《巨人書》是其中復原得最好的一部——'
        + '亨寧 1943 年把散在中古波斯語、帕提亞語、粟特語、回鶻語裡的殘片'
        + '綴輯成可讀的敘事，是摩尼教文獻學的經典之作。',
      divisions: [
        {
          key: 'd-canfrag',
          label: '正典殘卷',
          columns: IAMS,
          texts: [
            {
              slug: 'giants-iranian',
              title_zh: '巨人書（伊朗語殘卷）',
              title_orig: 'Kawān',
              title_en: 'The Book of Giants (Iranian fragments)',
              siglum: 'M 101, M 911 等',
              era: '寫本 8–10 世紀',
              language: `${MP}、${PA}、${SOG}、${UIG}`,
              provenance: '柏林吐魯番藏品',
              status: 'fragment',
              extent: '數十件殘片，可綴輯成成段敘事',
              note: '亨寧 1943 年綴輯刊布。摩尼教文獻學的經典個案。',
              intro:
                '巡視者（墮落天使）與人間女子所生的巨人，在地上行暴，終被剿滅——'
                + '這個出自《以諾書》傳統的故事，經摩尼改寫成敘利亞語正典，'
                + '再譯入中古波斯語、帕提亞語、粟特語與回鶻語。'
                + '亨寧把分散在不同語言、不同編號下的殘片辨認出來並排好次序，'
                + '使這部書成為七經中唯一能讀到連續情節的一部。'
                + '一個第二聖殿猶太故事的碎片，最後是在新疆的沙裡被找回來的。',
              seealso: ['book-of-giants'],
            },
            {
              slug: 'sabuhragan-turfan',
              title_zh: '沙卜爾干（吐魯番殘卷）',
              title_orig: 'Šābuhragān',
              title_en: 'The Šābuhragān (Turfan fragments)',
              siglum: 'M 470, M 472, M 473 等',
              era: '寫本 8–10 世紀',
              language: MP,
              provenance: '柏林吐魯番藏品',
              status: 'fragment',
              extent: '存末世論部分成段文字',
              note: 'IAMS《東方摩尼教選輯》第三冊全冊處理此書。',
              intro:
                '摩尼獻給沙普爾一世那部書的實際殘片。'
                + '現存最完整的一段是末世論：大審判如何進行、'
                + '末日之火將燃燒多久、光明分子如何最終脫離物質。'
                + '這些殘片讓《沙卜爾干》成為七經之外**復原程度最高**的摩尼親撰作品，'
                + '也讓我們看見摩尼如何用伊朗語彙重述一套原本用敘利亞語構思的體系。',
              seealso: ['sabuhragan'],
            },
            {
              slug: 'm17-living-gospel',
              title_zh: '活福音（殘葉）',
              title_orig: 'Evangelion',
              title_en: 'The Living Gospel (fragments)',
              siglum: 'M 17, M 172',
              era: '寫本 8–10 世紀',
              language: MP,
              provenance: '柏林吐魯番藏品',
              status: 'fragment',
              extent: '存開卷數句與零星段落',
              note: '七經之首僅存的東方語言殘葉。',
              intro:
                '《活福音》全書二十二章，今日在吐魯番只剩幾張殘葉，'
                + '其中 M 17 保存了開卷的自我宣告：「我摩尼，耶穌基督的使徒……」'
                + '——與《科隆摩尼古卷》所引的希臘文開卷語互相印證。'
                + '兩份材料一在埃及、一在新疆，隔著整個亞洲互相證明同一句話，'
                + '這種印證在摩尼教文獻裡極為罕見，因而格外重要。',
              seealso: ['living-gospel'],
            },
          ],
        },
      ],
    },
    {
      key: 'hymn-cycles',
      sigil: '讚',
      name: '讚詩',
      name_en: 'Hymn Cycles',
      provenance: '柏林吐魯番藏品',
      era: '寫本 8–11 世紀；所譯內容 3–4 世紀',
      extent: '兩大循環與數百首單篇',
      summary:
        '帕提亞語的《胡雅達格曼》與《安加德‧羅什南》是摩尼教詩歌的高峰，'
        + '兩者都以「被囚的靈魂呼求救援、救主降臨接引」為主題，'
        + '層層鋪敘、反覆詠歎，篇幅長達數百行。'
        + '它們與科普特《詩篇集》、漢文《下部讚》處理的是同一批主題，'
        + '有些甚至可以逐段對讀——一首詩在三種語言裡的三個版本，'
        + '是研究摩尼教如何跨文化傳播最直接的樣本。',
      divisions: [
        {
          key: 'd-hymns',
          label: '讚詩',
          columns: IAMS,
          texts: [
            {
              slug: 'huyadagman',
              title_zh: '胡雅達格曼',
              title_orig: 'Huyadagmān',
              title_en: 'Huyadagmān',
              siglum: 'M 4a, M 77 等',
              era: '寫本 8–10 世紀',
              language: PA,
              provenance: '柏林吐魯番藏品',
              status: 'partial',
              extent: '分五段，各段存缺不一',
              note: '帕提亞語兩大讚詩循環之一。',
              intro:
                '一首關於「被囚的光明靈魂」的長篇組詩。'
                + '靈魂在物質世界裡呼喊、迷失、遺忘自己的來歷，'
                + '直到救主從光明國度下來喚醒它——'
                + '這個「呼喚與甦醒」的母題與諾斯底《珍珠之歌》幾乎同構。'
                + '全詩分五段，在吐魯番以多份抄本流傳，'
                + '顯示它在中亞教團的日常禮儀中使用極廣。',
              seealso: ['xiabuzan', 'psalm-book'],
            },
            {
              slug: 'angad-rosnan',
              title_zh: '安加德‧羅什南',
              title_orig: 'Angad Rōšnān',
              title_en: 'Angad Rōšnān',
              siglum: 'M 33, M 233 等',
              era: '寫本 8–10 世紀',
              language: PA,
              provenance: '柏林吐魯番藏品',
              status: 'partial',
              extent: '分六段，各段存缺不一',
              note: '帕提亞語兩大讚詩循環之一。題名意為「富於光明者」。',
              intro:
                '與《胡雅達格曼》並列的長篇讚詩循環，題旨相近而語氣更為悲愴：'
                + '靈魂細數自己在肉身中所受的每一種苦，'
                + '而後救主的應許逐層降下。'
                + '這兩部循環一同構成摩尼教禮儀詩歌的主幹，'
                + '其抒情強度在古代宗教詩歌裡罕有其匹——'
                + '這也是為什麼奧古斯丁承認自己年輕時被這個宗教吸引。',
              seealso: ['huyadagman'],
            },
            {
              slug: 'mahrnamag',
              title_zh: '大讚美詩目錄',
              title_orig: 'Mahrnāmag',
              title_en: 'The Mahrnāmag (Hymn-book colophon)',
              siglum: 'M 1',
              era: '約 825–832 年',
              language: `${MP}、${PA}（跋為${UIG}）`,
              provenance: '柏林吐魯番藏品',
              status: 'partial',
              extent: '一卷，含長篇題記',
              note: '🚨 本藏最重要的單一文書：它的題記記下了整個中亞教團的名冊與紀年。',
              intro:
                '一部讚美詩集的目錄，價值卻不在詩而在**跋文**：'
                + '抄成之日的紀年、贊助者的名字與頭銜、'
                + '從回鶻可汗以下各級教團職事的名冊，逐一列出。'
                + '這份名單使我們得以重建九世紀高昌摩尼教團的組織與社會位置——'
                + '它與國家的關係、它的財源、它的階序。'
                + '摩尼教史上絕大多數斷代都靠這一件文書校準。',
            },
          ],
        },
      ],
    },
    {
      key: 'church-documents',
      sigil: '團',
      name: '教團文書',
      name_en: 'Church Documents',
      provenance: '柏林吐魯番藏品；部分在聖彼得堡、倫敦',
      era: '寫本 8–11 世紀',
      extent: '數百件',
      summary:
        '一個實際運作的宗教組織留下的紙：懺悔文、教曆、書信、帳目、戒律。'
        + '這一卷與教義無關而與制度有關，卻常常更能回答「摩尼教是什麼樣子」'
        + '——選民不能自己摘食物，所以聽者得替他們摘；'
        + '選民一年守多少齋、聽者一週守幾天；'
        + '犯了哪一類過失要在什麼場合懺悔。'
        + '《懺悔文》(Xwāstwānīft) 因回鶻語本流傳極廣，是其中最著名的一篇。',
      divisions: [
        {
          key: 'd-church',
          label: '教團文書',
          columns: IAMS,
          texts: [
            {
              slug: 'xwastwanift',
              title_zh: '懺悔文',
              title_orig: 'Xwāstwānīft',
              title_en: 'The Xwāstwānīft (Confession)',
              siglum: 'U 1, Or. 8212 等',
              era: '寫本 9–11 世紀',
              language: `${UIG}（另有${SOG}本）`,
              provenance: '柏林吐魯番藏品；倫敦大英圖書館（敦煌所出）',
              status: 'whole',
              extent: '十五節，完整傳世',
              note: '摩尼教文獻中少數完整傳世者。聽者用的定期懺悔文。',
              intro:
                '供「聽者」（在家信徒）定期誦念的認罪文，分十五節，'
                + '逐項列舉可能犯下的過失：對光明諸神不敬、'
                + '傷害光明分子（包括無意間踩踏植物與昆蟲）、'
                + '對選民供養不周、齋期不守、言語妄誕……'
                + '每一節以「若我如此犯了，今我懺悔，求赦免」收束。'
                + '這是理解摩尼教倫理實際如何規範日常行為最直接的文本，'
                + '而且它完整傳世——在這個領域裡是罕見的奢侈。',
            },
            {
              slug: 'bema-liturgy',
              title_zh: '貝馬節禮儀文',
              title_orig: 'Bēma',
              title_en: 'Bema Festival Liturgy',
              siglum: 'M 801 等',
              era: '寫本 8–10 世紀',
              language: `${MP}、${PA}`,
              provenance: '柏林吐魯番藏品',
              status: 'partial',
              extent: '數件，含長篇禮儀書 M 801',
              note: '與科普特《貝馬詩篇》為同一節期的東方版本，可對讀。',
              intro:
                'M 801 是一部相當完整的貝馬節禮儀書，'
                + '記錄了節期中誦念與詠唱的次序。'
                + '把它與埃及的《貝馬詩篇》並讀，'
                + '可以看見同一個節日在相隔數千公里的兩個教團裡'
                + '如何保持一致、又如何各自在地化。'
                + '這種跨地域的禮儀比對，是摩尼教研究少數能做得很紮實的題目。',
              seealso: ['bema-psalms'],
            },
            {
              slug: 'sogdian-letters',
              title_zh: '粟特語教團書信',
              title_orig: 'Sogdian church letters',
              title_en: 'Sogdian Manichaean Letters',
              siglum: 'So 18220 等',
              era: '寫本 9–10 世紀',
              language: SOG,
              provenance: '柏林吐魯番藏品',
              status: 'fragment',
              extent: '數十件',
              note: '教團領袖之間的通信。粟特商人網絡與傳教路線的一手證據。',
              intro:
                '摩尼教沿著粟特商人的商路東傳，'
                + '這批書信就是那個網絡的紙上痕跡：'
                + '某地教團向上級請示、報告人事、談論供養與差旅。'
                + '粟特語在八到十世紀是絲路的通用語，'
                + '摩尼教文獻大量使用它，正說明這個宗教的傳播'
                + '不靠武力也不靠國家，而是搭著貿易網走的。',
            },
          ],
        },
      ],
    },
  ],
}
