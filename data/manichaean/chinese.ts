// 續藏三 —— 漢文藏（敦煌、霞浦）
//
// 摩尼教於武則天延載元年（694）正式傳入中國，唐代稱「摩尼教」，
// 會昌毀佛（843）後轉入民間，宋代以降稱「明教」，在福建一帶一直存續到明清。
// 本藏收兩批材料：唐代的敦煌三經，與 2008 年在福建霞浦發現的科儀抄本。
//
// ══════════ 🚨 本藏只出一欄，不出三欄 ══════════
//
//   前三藏的 reader 是「原文轉寫／英譯／繁中」三欄。本藏**原文就是中文**，
//   所以只出一欄，原樣呈現。不可為了版面整齊而把唐代漢文再「翻譯」成現代中文——
//   那不是對照，那是改寫。需要幫助的地方用註解處理，不動正文。
//   （同一條規矩見 /research-data/sanyijiao 的 columnsFor()，user 2026-09-06 定。）
//
// ══════════ 取源：敦煌三經是本藏經取源條件最好的一批 ══════════
//
//   三經都收在《大正藏》第五十四冊（T2140《下部讚》、T2141A《儀略》、T2141B《殘經》），
//   公有領域，維基文庫另有錄文。本站 /tripitaka 已有大正藏全文，
//   故本藏的漢文欄直接接既有語料，不必另抓。
//   **2026-09-16 已上架**（scripts/manichaean_fetch.py --chinese）：
//     下部讚 83 段 11,878 字／儀略 40 段 1,790 字／殘經 32 段 8,632 字，
//     段號一律用大正藏行號（T54n2140_p1270b23），缺字 □ 原樣保留。
//   英譯的處境分兩種，別一律標 copyright（2026-09-16 實查）：
//     《下部讚》—— IAMS 開放取用的《東方摩尼教選輯》第四冊已收，
//        而且是**漢文原文＋帕提亞語／粟特語／回鶻語對照＋英譯**四欄並排刊出
//        （該冊 pp.100–116，英譯部分本於崔志 1943 年 BSOAS 本再校）。故標 available。
//     《儀略》《殘經》—— 劉南強等人的英譯仍在版權內，故標 copyright。

import type { ManiCanon } from './types'

const ZH_TANG = '漢文（唐）'

/** 敦煌三經：2026-09-16 已由 CBETA 大正藏語料建置上架，原文即中文（一欄呈現）。
 *  🚨 orig 與 zh 必須同步——這一藏兩欄指的是同一份東西，打架就是 bug（測試釘住）。 */
const CHINESE_COLS = { orig: 'ready', en: 'copyright', zh: 'ready' } as const

export const CHINESE_CANON: ManiCanon = {
  key: 'chinese',
  name: '漢文文獻',
  name_en: 'The Chinese Texts',
  glyph: '漢',
  subtitle: '續藏 — 敦煌三經與福建科儀抄本',
  scriptural: true,
  language: '漢文',
  era: '唐代（8 世紀）至明清',
  summary:
    '摩尼教是唯一一個**同時在羅馬帝國與中國留下大量文獻**的古代宗教，'
    + '漢文藏就是東端的那一半。敦煌所出三經皆為唐代譯本或撰述，'
    + '其中《摩尼光佛教法儀略》是拂多誕於開元十九年（731）奉唐玄宗詔所撰的'
    + '教義與制度綱要——一份**由皇帝要求、由教士書寫**的官方說明書，'
    + '這種文件在摩尼教文獻裡絕無僅有。'
    + '會昌毀佛後摩尼教轉入民間成為「明教」，在福建延續了近千年；'
    + '2008 年霞浦發現的科儀抄本，讓這條下半段第一次有了文本。',
  parts: [
    {
      key: 'p-dunhuang', label: '敦煌三經', label_en: 'The Three Dunhuang Texts',
      desc:
        '二十世紀初出自敦煌藏經洞的三件唐代摩尼教寫卷，'
        + '今分藏倫敦、巴黎與北京，均收入《大正藏》第五十四冊。',
      volumes: ['dunhuang'],
    },
    {
      key: 'p-mingjiao', label: '明教遺文', label_en: 'The Later Chinese Manichaean Tradition',
      desc:
        '唐末以降轉入民間的摩尼教（明教）留下的材料：'
        + '宋代典籍所記已佚經名，以及 2008 年霞浦發現的科儀抄本。',
      volumes: ['xiapu', 'song-lost'],
    },
  ],
  volumes: [
    {
      key: 'dunhuang',
      sigil: '敦',
      name: '敦煌三經',
      name_en: 'The Three Dunhuang Texts',
      provenance: '敦煌莫高窟藏經洞；今藏倫敦大英圖書館、巴黎法國國家圖書館、北京中國國家圖書館',
      era: '唐代，8 世紀',
      extent: '三件寫卷',
      summary:
        '二十世紀初斯坦因與伯希和自敦煌取走的寫卷中，有三件是摩尼教文獻。'
        + '三件的性質互不相同：《儀略》是官方說明書，'
        + '《下部讚》是實際唱的讚詩集，《殘經》是教義論述。'
        + '三者合起來，讓漢地摩尼教成為除埃及與吐魯番之外'
        + '第三個有整本書可讀的傳統。'
        + '三經皆已收入《大正藏》第五十四冊，屬公有領域。',
      divisions: [
        {
          key: 'd-dunhuang',
          label: '敦煌三經',
          columns: CHINESE_COLS,
          texts: [
            {
              slug: 'yilue',
              title_zh: '摩尼光佛教法儀略',
              title_orig: '摩尼光佛教法儀略',
              title_en: 'Compendium of the Doctrines and Styles of the Teaching of Mani, the Buddha of Light',
              siglum: 'T2141A（S.3969＋P.3884）',
              author: '拂多誕',
              era: '唐開元十九年（731）',
              language: ZH_TANG,
              provenance: '敦煌藏經洞；前半藏倫敦、後半藏巴黎',
              status: 'whole',
              extent: '兩殘卷可綴合，首尾大致完整',
              note: '奉唐玄宗詔所撰。摩尼教文獻中唯一由帝王要求寫成的官方說明書。',
              intro:
                '開元十九年，唐玄宗下詔要摩尼教說明自己究竟是什麼教，'
                + '教中法師拂多誕於是撰成此書：摩尼的生平、七部大經與圖經的名目、'
                + '寺院的五堂制度、教團的五級階序（慕闍、拂多誕、默奚悉德、阿羅緩、耨沙喭）。'
                + '一份為了應付官方查問而寫的文件，反而成了今日最有條理的摩尼教制度史料——'
                + '**七部大經的漢文名目就出自這裡**，'
                + '也因此成為比對敘利亞語書名與科普特文書目的關鍵一環。',
              seealso: ['living-gospel', 'book-of-giants'],
            },
            {
              slug: 'xiabuzan',
              title_zh: '下部讚',
              title_orig: '摩尼教下部讚',
              title_en: 'The Lower Section of the Manichaean Hymns',
              siglum: 'T2140（S.2659）',
              era: '唐代，8 世紀',
              language: ZH_TANG,
              provenance: '敦煌藏經洞；今藏倫敦大英圖書館',
              status: 'whole',
              extent: '一卷，三十餘首讚',
              columns: { orig: 'ready', en: 'available', zh: 'ready' },
              note: '漢地摩尼教團實際詠唱的讚詩集，完整傳世。IAMS 選輯第四冊已刊英譯與多語對照。',
              intro:
                '一卷完整的漢文摩尼教讚詩集，收讚三十餘首，'
                + '包括歎明界文、歎五明文、收食單偈、嘆無上明尊偈等。'
                + '其中若干首可與帕提亞語讚詩循環、科普特《詩篇集》逐段對讀——'
                + '同一首詩在三種語言裡的三個版本。'
                + '譯者刻意大量借用佛教詞彙（明尊、法身、清淨、光明），'
                + '這既是傳教策略，也是後來摩尼教被官方與佛教徒'
                + '同時指為「偽佛」的原因之一。',
              seealso: ['huyadagman', 'psalms-and-prayers'],
            },
            {
              slug: 'canjing',
              title_zh: '摩尼教殘經',
              title_orig: '摩尼教殘經（波斯教殘經）',
              title_en: 'The Chinese Manichaean Treatise (fragment)',
              siglum: 'T2141B（北 8470／BD00256）',
              era: '唐代，8 世紀',
              language: ZH_TANG,
              provenance: '敦煌藏經洞；今藏北京中國國家圖書館',
              status: 'partial',
              extent: '存三百餘行，首尾俱缺',
              note: '又稱《波斯教殘經》。原題已佚，學界或比定為七經之一的漢譯。',
              intro:
                '一件首尾俱缺的寫卷，存三百餘行，'
                + '內容是以問答體展開的教義論述：'
                + '明性與暗性、淨風與五明子、惠明使如何喚醒困於肉身的光明。'
                + '因為首題已佚，它究竟是七部大經中哪一部的漢譯，各家意見不一，'
                + '較多學者傾向與《證明過去教經》有關。'
                + '本站不替學界下判斷，仍以「殘經」立目——'
                + '這也是它在《大正藏》裡的名字。',
            },
          ],
        },
      ],
    },
    {
      key: 'xiapu',
      sigil: '霞',
      name: '霞浦文書',
      name_en: 'The Xiapu Manuscripts',
      provenance: '福建省霞浦縣柏洋鄉；2008 年發現',
      era: '抄本明清；所承傳統上溯宋元',
      extent: '數十種科儀抄本，陸續刊布',
      summary:
        '2008 年在福建霞浦一個法師世家中發現的一批科儀抄本，'
        + '包括《摩尼光佛》《興福祖慶誕科》《貞明開正文科》《點燈七層科冊》等。'
        + '這批材料**重開了整個領域的新局**：'
        + '在此之前，漢地摩尼教的文獻只到唐代為止，之後只能靠官方史料與方志推測；'
        + '霞浦文書證明這個傳統一路活到明清，而且保存了'
        + '可與敦煌三經對讀的讚詞與神名。'
        + '🚨 這批抄本仍在整理刊布中，校錄本多在版權內。',
      divisions: [
        {
          key: 'd-xiapu',
          label: '霞浦科儀抄本',
          columns: { orig: 'copyright', en: 'none', zh: 'copyright' },
          texts: [
            {
              slug: 'xiapu-moni-guangfo',
              title_zh: '摩尼光佛',
              title_orig: '摩尼光佛',
              title_en: 'Moni Guangfo (Mani the Buddha of Light)',
              siglum: '霞浦文書',
              era: '抄本明清',
              language: '漢文（閩地科儀體）',
              provenance: '福建霞浦柏洋鄉',
              status: 'partial',
              extent: '一冊',
              note: '霞浦文書中最重要的一種，保存大量可與敦煌三經對讀的讚詞。',
              intro:
                '一部法事用的科儀本，內容是奉請摩尼光佛及諸神的儀節與讚詞。'
                + '其中若干段落與敦煌《下部讚》的用語高度重合，'
                + '有些神名甚至保留了中古伊朗語音譯的痕跡——'
                + '在一份明清抄本裡，隔著七八百年，'
                + '還讀得到粟特語與帕提亞語的迴音。'
                + '這種連續性是霞浦文書最震撼的地方。',
              seealso: ['xiabuzan'],
            },
            {
              slug: 'xiapu-xingfu',
              title_zh: '興福祖慶誕科',
              title_orig: '興福祖慶誕科',
              title_en: 'Xingfu Zu Qingdan Ke',
              siglum: '霞浦文書',
              era: '抄本明清',
              language: '漢文（閩地科儀體）',
              provenance: '福建霞浦柏洋鄉',
              status: 'partial',
              extent: '一冊',
              note: '慶賀「興福祖」誕辰的科儀。所祀之祖或即摩尼教入閩的傳教者。',
              intro:
                '一部慶誕科儀，所奉的「興福祖」據考即五代入閩傳教的呼祿法師。'
                + '文本把一位外來傳教者納進了地方祖師信仰的格式裡——'
                + '這正是摩尼教在中國最終的存在方式：'
                + '不是作為一個獨立宗教活下來，'
                + '而是溶進民間法事的神譜與科儀之中，'
                + '連奉行的人都未必知道自己念的是什麼教的經。',
            },
          ],
        },
      ],
    },
    {
      key: 'song-lost',
      sigil: '宋',
      name: '宋代明教佚經',
      name_en: 'Lost Song-dynasty Mingjiao Texts',
      provenance: '原書全佚；書名見於宋代典籍與官府文書',
      era: '宋代',
      extent: '全佚',
      summary:
        '宋代官府查禁「喫菜事魔」時，把搜出的明教經書名目記進了公文與僧史，'
        + '《佛祖統紀》等書因而保存了一批已佚經名。'
        + '這些書一字不存，但書名本身是證據：'
        + '它們顯示宋代明教仍有成套的經典，而非僅存零星科儀。',
      divisions: [
        {
          key: 'd-song',
          label: '宋代佚經',
          columns: { orig: 'none', en: 'none', zh: 'none' },
          texts: [
            {
              slug: 'song-lost-sutras',
              title_zh: '宋代明教經目',
              title_en: 'The Lost Mingjiao Scriptures',
              siglum: '宋',
              era: '宋代',
              language: '漢文',
              provenance: '原書全佚',
              status: 'lost-listed',
              via: '《佛祖統紀》卷四十八所記查禁書目；宋代官府文書',
              extent: '全佚，僅存書名',
              note: '含《證明經》《佛性經》等，均一字不存。',
              intro:
                '宋代官府以「喫菜事魔」為名查禁明教，'
                + '僧史與公文因而記下了被搜出的經書名目，'
                + '如《證明經》《佛性經》《日光偈》《月光偈》等。'
                + '這些書全部不存。'
                + '但書目本身說明了兩件事：宋代明教仍有成套經典，'
                + '而且這些經名沿用的是唐代摩尼教的用語系統——'
                + '一個被查禁的教團，在地下維持了數百年的文本傳承。',
            },
          ],
        },
      ],
    },
  ],
}
