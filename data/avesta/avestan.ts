import type { ZoroCanon, ZoroText } from './types'
import { series } from './types'

// 阿維斯陀（正藏）— 阿維斯陀語原典
//
// 🚨 分部一律照薩珊祭司傳下來的禮儀單位，不重編。亞斯納 72 章、維斯帕拉德 24 章、
//    萬迪達德 22 章、亞什特 21 首，這些數目帕西祭司今天仍照著誦。
//
// 🚨 逐章的**英文標題**刻意留空，由 scripts/avesta_fetch.py 連同內文一起帶回填。
//    avesta.org 的 yasna.htm 目錄裡，米爾斯的章題 caption 掛在**前一個**編號的
//    heading 上（H 標題序列錯位一格），照抓會整份偏移一章而頁面完全正常——
//    見 [[feedback_reader_silent_failures]]。所以本檔只寫「確定」的那一層：
//    禮儀分部與已定名的著名篇章，其餘章題等真內容回來再補。

const AE = '阿維斯陀語'

/** 亞斯納 72 章。名稱只在傳統有專名者給專名，其餘作「第 N 章」，待管線回填。 */
function yasna(from: number, to: number, named: Record<number, [string, string?]> = {}): ZoroText[] {
  const rows: Array<[number, string, string?]> = []
  for (let n = from; n <= to; n++) {
    const hit = named[n]
    rows.push([n, hit ? hit[0] : `亞斯納 第 ${n} 章`, hit?.[1]])
  }
  return series({ slug: 'yasna', siglum: 'Y', orig: 'Yasna', language: AE }, rows)
}

export const AVESTAN_CANON: ZoroCanon = {
  key: 'avestan',
  name: '阿維斯陀',
  name_en: 'The Avesta',
  glyph: '阿',
  subtitle: '正藏 — 阿維斯陀語原典',
  scriptural: true,
  language: '阿維斯陀語（古／新兩層）',
  era: '約前 1500 – 公元 4 世紀（口傳），約 6 世紀寫定',
  summary:
    '祆教唯一的原典層，以阿維斯陀語傳世。薩珊時代編成二十一部「納斯克」，據《丹卡爾德》所記約有三十四萬五千字；今日僅存約四分之一，且傳世的這一部分之所以能活下來，幾乎全靠它在祭典裡被誦唸——不誦的就佚失了。因此本藏一律按禮儀單位分部，不按主題重編：亞斯納、維斯帕拉德、萬迪達德三者合誦為「長祭典」，亞什特與小阿維斯陀為日常與節期用，殘篇與佚失納斯克另立兩部。全藏最古的一層是查拉圖斯特拉本人的十七首伽薩，語言古於其餘各篇數百年。',
  parts: [
    {
      key: 'p-liturgy', label: '長祭典部', label_en: 'The Long Liturgy',
      desc: '亞斯納、維斯帕拉德、萬迪達德三書。三者不是三本獨立的書，而是同一場通宵祭典的三層誦本——維斯帕拉德的各章插入亞斯納之間，萬迪達德各章再插入其間。單獨閱讀任何一本都看不出這個結構。',
      volumes: ['yasna', 'visperad', 'vendidad'],
    },
    {
      key: 'p-hymn', label: '讚歌部', label_en: 'Hymns',
      desc: '獻給各神祇（亞扎塔）的讚歌，保存了最多前查拉圖斯特拉的印度－伊朗神話層。',
      volumes: ['yasht'],
    },
    {
      key: 'p-daily', label: '日課部', label_en: 'Daily Prayer',
      desc: '在家信眾與祭司每日誦唸的短禱集，是今日帕西社群實際最常用的一部。',
      volumes: ['khordeh'],
    },
    {
      key: 'p-remnant', label: '殘餘部', label_en: 'Fragments and Lost Nasks',
      desc: '僅存殘篇者，與已全佚、只在《丹卡爾德》第八九卷留下撮要者。祆教正典的四分之三在這一部裡——以「目錄」的形式。',
      volumes: ['fragment', 'nask'],
    },
  ],
  volumes: [
    // ───────────────────────── 亞斯納 ─────────────────────────
    {
      key: 'yasna', sigil: '耶', name: '亞斯納', name_orig: 'Yasna', name_en: 'Yasna',
      liturgy: '長祭典的主誦本，於晨禱時段（Hāwan Gāh）全本誦唸，約需兩小時',
      era: '伽薩約前 1500–1000；其餘約前 900–400', extent: '72 章',
      summary:
        '「亞斯納」意為「敬拜、獻祭」，是祆教最核心的祭典書，全書 72 章對應祭司腰帶（庫斯提）的 72 縷線。全書以豪麻榨汁禮為軸，中段嵌入全教最古老的兩塊文本——查拉圖斯特拉本人的十七首伽薩，與散文體的七章禱。這兩塊的語言（古阿維斯陀語）比周圍章節古數百年，等於一部祭典書把自己的創教文獻整個包在裡面。',
      divisions: [
        {
          key: 'y-open', label: '開祭段（1–8）', label_en: 'Opening of the Sacrifice',
          desc: '呼名、奠獻、進食祝禱。祭司逐一唱名所要祭獻的對象，再獻上餅與肉。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(1, 8, { 1: ['呼名獻祭'], 8: ['肉供與信眾分食'] }),
        },
        {
          key: 'y-hom', label: '豪麻讚（9–11）', label_en: 'Hōm Yasht',
          desc: '獻給豪麻（榨汁飲用的神聖植物，即印度的蘇摩）。豪麻現身向查拉圖斯特拉自陳來歷，是全書敘事性最強的段落之一。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(9, 11, {
            9: ['豪麻讚（上）', '豪麻現身，自述歷代榨汁者及其所得之子。'],
            10: ['豪麻讚（中）'],
            11: ['豪麻讚（下）'],
          }),
        },
        {
          key: 'y-creed', label: '信仰宣示（12）', label_en: 'The Zoroastrian Creed',
          desc: '祆教的信經。入教與日常均誦，開頭一句「我宣認自己為敬拜馬茲達者、查拉圖斯特拉的信徒，棄絕迭瓦、奉阿胡拉之教」。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(12, 12, { 12: ['信仰宣示', '祆教的信經（Frauuarānē）；比尼西亞信經早約九百年。'] }),
        },
        {
          key: 'y-prelim', label: '前段誦文（13–18）', label_en: 'Preliminary Invocations',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(13, 18),
        },
        {
          key: 'y-bagan', label: '三禱詞釋義（19–21）', label_en: 'Bagān Yasht',
          desc: '對全教三句最短禱詞——阿胡納‧瓦伊里亞、阿舍姆‧沃胡、燕赫‧哈坦——的逐句解說。這三句在祆教的地位相當於主禱文，而這三章是阿維斯陀語文本裡罕見的自我註釋。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(19, 21, {
            19: ['阿胡納‧瓦伊里亞釋義', '解說全教第一禱詞；文中稱此禱在創世之前即已存在。'],
            20: ['阿舍姆‧沃胡釋義'],
            21: ['燕赫‧哈坦釋義'],
          }),
        },
        {
          key: 'y-prep', label: '獻祭續段（22–27）', label_en: 'The Sacrifice Continues',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(22, 27),
        },
        {
          key: 'y-gatha1', label: '阿胡納瓦提伽薩（28–34）', label_en: 'Ahunavaitī Gāthā',
          desc: '五組伽薩的第一組，七章。查拉圖斯特拉自述蒙召、詰問阿胡拉‧馬茲達、宣告二元抉擇。第 30 章「兩靈」是全教教義的源頭。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(28, 34, {
            28: ['伽薩‧祈求聆聽', '查拉圖斯特拉舉手祈禱，求見善念之靈。'],
            29: ['伽薩‧牛魂的哀訴', '被虐待的牛之魂向天控訴，天庭指派查拉圖斯特拉為其牧者。'],
            30: ['伽薩‧兩靈', '善惡二靈太初自擇其道；祆教二元論的根本文本。'],
            31: ['伽薩‧道路的詰問'],
            32: ['伽薩‧斥迭瓦與其祭司'],
            33: ['伽薩‧先知的獻身'],
            34: ['伽薩‧求得永生'],
          }),
        },
        {
          key: 'y-hapt', label: '七章禱（35–42）', label_en: 'Yasna Haptaŋhāiti',
          desc: '古阿維斯陀語的散文體祈禱，語言與伽薩同層而文體全異。學界多認為它出自查拉圖斯特拉的直系門徒團體，是現存最古老的祆教集體禮拜文。第 42 章為後補。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(35, 42, {
            35: ['七章禱‧讚阿胡拉與不朽聖者'],
            36: ['七章禱‧向阿胡拉與火'],
            37: ['七章禱‧向聖造與弗拉瓦希'],
            38: ['七章禱‧向大地與聖水'],
            39: ['七章禱‧向牛魂'],
            40: ['七章禱‧求助佑'],
            41: ['七章禱‧向阿胡拉為王'],
            42: ['七章禱補遺', '後世增補，不屬古阿維斯陀語層。'],
          }),
        },
        {
          key: 'y-gatha2', label: '烏什塔瓦提伽薩（43–46）', label_en: 'Uštavaitī Gāthā',
          desc: '第二組伽薩，四章。第 44 章連續以「這我要問你，請據實告我，阿胡拉」開頭發問二十次，是宗教文獻裡罕見的詰問體。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(43, 46, {
            43: ['伽薩‧幸福歸於'],
            44: ['伽薩‧二十問', '連續二十次「這我要問你，請據實告我」——誰立定大地？誰使日月行走？'],
            45: ['伽薩‧我要宣講'],
            46: ['伽薩‧我往何處去', '先知被逐、走投無路的自述：「我往何地去？何處可容我棲身？」'],
          }),
        },
        {
          key: 'y-gatha3', label: '斯彭塔‧曼紐伽薩（47–50）', label_en: 'Spəntā.mainyū Gāthā',
          desc: '第三組伽薩，四章。以「豐饒之靈」（斯彭塔‧曼紐）為名。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(47, 50, {
            47: ['伽薩‧豐饒之靈'],
            48: ['伽薩‧真理勝虛妄'],
            49: ['伽薩‧斥敵者'],
            50: ['伽薩‧我魂何依'],
          }),
        },
        {
          key: 'y-gatha4', label: '沃胡‧赫沙特拉伽薩（51）', label_en: 'Vohu.xšaθrā Gāthā',
          desc: '第四組伽薩，僅一章。以「善的王權」為名。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(51, 51, { 51: ['伽薩‧善的王權'] }),
        },
        {
          key: 'y-bless', label: '祝聖（52）', label_en: 'A Prayer for Sanctity',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(52, 52, { 52: ['求聖潔與其果報'] }),
        },
        {
          key: 'y-gatha5', label: '瓦希什托‧伊什提伽薩（53）', label_en: 'Vahištōišti Gāthā',
          desc: '第五組伽薩，僅一章，為查拉圖斯特拉之女普魯查絲塔的婚禮致辭。是否出自先知本人，學界有爭議。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(53, 53, { 53: ['伽薩‧最好的願望', '先知幼女的婚禮致辭；祆教的婚姻觀出自此章。'] }),
        },
        {
          key: 'y-airyaman', label: '艾里亞曼禱（54）', label_en: 'Airyaman Išya',
          desc: '古阿維斯陀語的第四塊——與伽薩、七章禱同層。全教最有力的驅病與祝福禱詞，末世時將由救世主誦唸以完成復活。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(54, 54, { 54: ['艾里亞曼禱', '古阿維斯陀語四塊之一；末世復活時所誦。'] }),
        },
        {
          key: 'y-staota', label: '讚頌段（55–61）', label_en: 'Staota Yesnya',
          desc: '伽薩誦畢後的讚頌，含斯勞沙讚與繁盛頌詞。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(55, 61, {
            56: ['斯勞沙讚前引'],
            57: ['斯勞沙讚', '獻給聽禱之神斯勞沙；亞什特第 11 首之外的另一篇。'],
            58: ['繁盛頌詞'],
            59: ['互祝'],
          }),
        },
        {
          key: 'y-fire', label: '火讚（62）', label_en: 'Ātaš Niyāyišn',
          desc: '向聖火祝禱。同一篇亦收入小阿維斯陀的五讚頌，是祆教最廣為人知的段落。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(62, 62, { 62: ['火讚', '亦見於小阿維斯陀‧火讚頌。'] }),
        },
        {
          key: 'y-water', label: '水奠段（63–69）', label_en: 'Āb-Zōhr',
          desc: '長祭典的高潮：祭司將豪麻汁奠入水中，象徵把祭典的功效交還給諸水。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(63, 69, {
            65: ['向阿爾德維‧蘇拉‧阿娜希塔與諸水'],
            66: ['向阿胡拉之女（水）'],
          }),
        },
        {
          key: 'y-close', label: '結祭（70–72）', label_en: 'Concluding',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: yasna(70, 72, { 70: ['向不朽聖者與教制'], 71: ['祭典將畢'], 72: ['結祭'] }),
        },
      ],
    },

    // ───────────────────────── 維斯帕拉德 ─────────────────────────
    {
      key: 'visperad', sigil: '維', name: '維斯帕拉德', name_orig: 'Visperad', name_en: 'Visperad',
      liturgy: '不單獨誦唸。其 24 章分插於亞斯納各章之間，僅在六大節期（伽罕巴爾）的擴充祭典中使用',
      era: '約前 500 – 公元 300', extent: '24 章',
      summary:
        '名稱意為「向一切主宰者」（vīspe ratavō）。本身沒有獨立的敘事或教義，全書是為節期祭典而作的擴充誦段——把亞斯納的呼名對象再擴大一輪，遍及一切等級的「主宰者」。**它不能單獨讀**：脫離亞斯納之後，維斯帕拉德只是一串沒有主體的插入句。本站雖依慣例單列一卷，版面上須標明其插入位置。',
      divisions: [
        {
          key: 'vr-all', label: '全書（1–24）', label_en: 'Visperad 1–24',
          desc: '各章的插入位置依帕西祭司傳統固定，本站於篇首標注其對應的亞斯納章次。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: series(
            { slug: 'visperad', siglum: 'Vr', orig: 'Visperad', language: AE },
            Array.from({ length: 24 }, (_, i) => [i + 1, `維斯帕拉德 第 ${i + 1} 章`] as [number, string]),
          ),
        },
      ],
    },

    // ───────────────────────── 萬迪達德 ─────────────────────────
    {
      key: 'vendidad', sigil: '祓', name: '萬迪達德', name_orig: 'Vīdēvdād', name_en: 'Vendidad / Videvdad',
      liturgy: '長祭典的午夜擴充本，於 Ušahin Gāh 誦唸；唯一保存了完整巴列維語逐句註釋（贊德）的納斯克',
      era: '約前 400 – 公元 300（材料更早）', extent: '22 章（法爾迦爾德）',
      summary:
        '名稱意為「驅逐迭瓦之法」。二十一納斯克裡唯一完整傳世的一部，因此地位特殊——它是我們對薩珊祆教「一部完整的經」長什麼樣子的唯一直接證據。內容以潔淨法與屍體處理為主體，兼收創世地理、伊瑪的地窖、狗的律法、醫術起源。文體枯燥而重複，卻是了解祆教實際生活規範最重要的一本；十九世紀歐洲學界對祆教的印象大半由此書形成，而那個印象相當不公平。',
      divisions: [
        {
          key: 'vd-myth', label: '神話段（1–2）', label_en: 'Mythical Geography and Yima',
          desc: '全書僅有的兩章敘事文，也是最常被引用的兩章。',
          columns: { orig: 'ready', en: 'ready', zh: 'available' },
          texts: series({ slug: 'vendidad', siglum: 'Vd', orig: 'Vendidad', language: AE }, [
            [1, '十六邦國', '阿胡拉‧馬茲達造十六片良土，安格拉‧曼紐逐一造出災殃相對——祆教的歷史地理總綱。'],
            [2, '伊瑪的地窖', '首王伊瑪奉命造地下方城以避大寒，攜各類生靈之種入內。與挪亞方舟的關係聚訟已久。'],
          ]),
        },
        {
          key: 'vd-purity', label: '潔淨法（3–17）', label_en: 'Purity Law',
          desc: '本書主體。屍體污染（納蘇）的處理、犬類的地位、婦女經期與產後、罪與贖。',
          columns: { orig: 'ready', en: 'ready', zh: 'available' },
          texts: series({ slug: 'vendidad', siglum: 'Vd', orig: 'Vendidad', language: AE }, [
            [3, '大地的悅與不悅', '大地最喜與最厭之事各五；耕作被列為最高的宗教行為之一。'],
            [4, '契約與傷害', '六等契約與違約之罰；祆教法律思想的核心章。'],
            [5, '屍體污染（一）'],
            [6, '屍體污染（二）與寂靜之塔'],
            [7, '屍體污染（三）與醫者'],
            [8, '屍體的搬運與淨火'],
            [9, '九夜大淨禮（巴爾什農）'],
            [10, '驅魔誦詞'],
            [11, '各處所的潔淨'],
            [12, '喪期'],
            [13, '犬（上）', '狗在祆教的地位近於人；傷犬之罰極重。'],
            [14, '犬（下）與贖罪'],
            [15, '重罪與棄嬰'],
            [16, '經期婦女'],
            [17, '髮與甲的處置'],
          ]),
        },
        {
          key: 'vd-misc', label: '雜篇（18–22）', label_en: 'Miscellaneous',
          columns: { orig: 'ready', en: 'ready', zh: 'available' },
          texts: series({ slug: 'vendidad', siglum: 'Vd', orig: 'Vendidad', language: AE }, [
            [18, '假祭司與公雞'],
            [19, '誘惑查拉圖斯特拉', '安格拉‧曼紐遣魔誘先知棄教未果；全書最具戲劇性的一章。'],
            [20, '特里塔與醫術之始'],
            [21, '雲、雨與諸水'],
            [22, '阿胡拉求治於曼特拉‧斯彭塔'],
          ]),
        },
      ],
    },

    // ───────────────────────── 亞什特 ─────────────────────────
    {
      key: 'yasht', sigil: '讚', name: '亞什特', name_orig: 'Yašt', name_en: 'The Yashts',
      liturgy: '按當日所屬的神祇擇誦；節期與還願時另有專誦',
      era: '約前 700 – 公元 100（神話材料遠早）', extent: '21 首',
      summary:
        '獻給各亞扎塔（值得敬拜者）的讚歌集，共 21 首，篇幅與價值極不平均——第 5、10、13、19 首各長逾百節且保存大量印度－伊朗共有的古神話，其餘數首僅存數節。**這是全阿維斯陀最不「查拉圖斯特拉」的一部分**：密特拉、阿娜希塔、韋雷特拉格納這些神在伽薩裡不見蹤影，卻在亞什特裡佔據中心；它們是先知改革之前的舊神，後來被重新納入體系。要研究前祆教的伊朗宗教，材料幾乎全在這裡。',
      divisions: [
        {
          key: 'yt-all', label: '二十一讚', label_en: 'Yashts 1–21',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: series({ slug: 'yasht', siglum: 'Yt', orig: 'Yasht', language: AE }, [
            [1, '阿胡拉‧馬茲達讚', '主神的二十個名號。'],
            [2, '七不朽聖者讚'],
            [3, '阿沙‧瓦希什塔讚', '至上真理／最勝之義。'],
            [4, '豪爾瓦塔特讚', '圓滿（水的守護者）。'],
            [5, '阿娜希塔讚（水神讚）', '長篇。阿爾德維‧蘇拉‧阿娜希塔駕四馬之車而來，歷代英雄向她獻祭求願——祆教女神信仰的主文本。'],
            [6, '太陽讚'],
            [7, '月讚'],
            [8, '提什特里亞讚（天狼星讚）', '長篇。星神化白馬與旱魔阿波沙化黑馬相鬥，勝則降雨——印歐鬥龍神話的伊朗形態。'],
            [9, '德爾瓦斯帕讚（牲畜守護讚）'],
            [10, '密特拉讚', '全書最長。契約之神密特拉巡行天下、明察背約者；羅馬密特拉教的遠源，也是研究印歐契約神觀最重要的單篇文獻。'],
            [11, '斯勞沙讚'],
            [12, '拉什努讚', '審判之神；末日靈魂過橋時執秤者。'],
            [13, '弗拉瓦希讚', '長篇。獻給列祖的守護靈（弗拉瓦希），逐一唱出數百位先賢之名——祆教最重要的人名庫。'],
            [14, '韋雷特拉格納讚（勝利神讚）', '戰神以十種化身現形：風、公牛、白馬、駱駝、野豬、少年、鷙鳥、羚羊、山羊、武士。'],
            [15, '瓦尤讚（風神讚）', '風神兼具生死兩面，是祆教二元體系裡罕見的曖昧神格。'],
            [16, '奇斯塔讚（宗教女神讚）'],
            [17, '阿希讚（福運女神讚）'],
            [18, '阿什塔德讚'],
            [19, '扎姆亞德讚（王者神光讚）', '長篇。敘「赫瓦雷納」（王者神光）在歷代君王與英雄間的轉移與逃逸——伊朗王權神授觀的根本文本，末段預告救世主的降臨。'],
            [20, '瓦南特讚'],
            [21, '豪麻讚（亞什特本）'],
          ]),
        },
      ],
    },

    // ───────────────────────── 小阿維斯陀 ─────────────────────────
    {
      key: 'khordeh', sigil: '小', name: '小阿維斯陀', name_orig: 'Khordeh Avesta', name_en: 'Khordeh Avesta',
      liturgy: '在家信眾每日五時誦唸；今日帕西社群實際最常用的一部',
      era: '編成於薩珊末期（材料多取自亞斯納與亞什特）', extent: '約 25 篇',
      summary:
        '「小阿維斯陀」是薩珊祭司阿杜爾巴德‧馬赫拉斯潘丹為在家信眾所編的日課本，內容多半是從亞斯納與亞什特裡摘出的段落，加上一批專為日課而作的短禱。**這一部的宗教生命力遠高於它的原創性**——一個祆教徒一生誦唸最多次的文字都在這裡。今日仍在印刷、仍在使用，各版本收錄篇目略有出入。',
      divisions: [
        {
          key: 'ka-core', label: '基本禱詞', label_en: 'Core Prayers',
          desc: '最短、誦唸最頻的幾句，多數祆教徒自幼背誦。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'ahuna-vairya', title_zh: '阿胡納‧瓦伊里亞', title_orig: 'Ahuna Vairya', siglum: 'Y 27.13', language: AE, note: '全教第一禱詞，僅一節；經文稱其在創世之前即已存在。' },
            { slug: 'ashem-vohu', title_zh: '阿舍姆‧沃胡', title_orig: 'Ashem Vohū', siglum: 'Y 27.14', language: AE, note: '讚頌「真理」的三行禱；誦唸次數最多的一句。' },
            { slug: 'yenghe-hatam', title_zh: '燕赫‧哈坦', title_orig: 'Yeŋ́hē Hātąm', siglum: 'Y 27.15', language: AE },
            { slug: 'kem-na-mazda', title_zh: '克姆‧納‧馬茲達', title_orig: 'Kəm.nā.mazdā', siglum: 'Y 46.7 等', language: AE, note: '驅邪禱，集自伽薩諸句。' },
            { slug: 'hoshbam', title_zh: '黎明禱', title_orig: 'Hōšbām', siglum: 'KA', language: AE },
          ],
        },
        {
          key: 'ka-niyayishn', label: '五讚頌', label_en: 'The Five Niyāyišns',
          desc: '向五種可見的神聖對象致敬，於相應時刻誦唸。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'niyayishn-khwarshed', title_zh: '太陽讚頌', title_orig: 'Xᵛaršēd Niyāyišn', siglum: 'Ny 1', language: AE, note: '每日三次，面向太陽誦。' },
            { slug: 'niyayishn-mihr', title_zh: '密特拉讚頌', title_orig: 'Mihr Niyāyišn', siglum: 'Ny 2', language: AE },
            { slug: 'niyayishn-mah', title_zh: '月讚頌', title_orig: 'Māh Niyāyišn', siglum: 'Ny 3', language: AE },
            { slug: 'niyayishn-aban', title_zh: '水讚頌', title_orig: 'Ābān Niyāyišn', siglum: 'Ny 4', language: AE },
            { slug: 'niyayishn-atash', title_zh: '火讚頌', title_orig: 'Ātaš Niyāyišn', siglum: 'Ny 5', language: AE, note: '於火廟中面向聖火誦；祆教最廣為人知的一篇。' },
          ],
        },
        {
          key: 'ka-gah', label: '五時禱', label_en: 'The Five Gāhs',
          desc: '一晝夜分五時段，各有專禱。這個時間結構規定了祆教徒的一天。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'gah-havan', title_zh: '晨時禱', title_orig: 'Hāwan Gāh', siglum: 'G 1', language: AE, note: '日出至正午。' },
            { slug: 'gah-rapithwin', title_zh: '午時禱', title_orig: 'Rapiθwin Gāh', siglum: 'G 2', language: AE, note: '正午至午後三時；冬季不誦（傳說此時段被寒冬逼入地下）。' },
            { slug: 'gah-uzerin', title_zh: '晡時禱', title_orig: 'Uzayeirin Gāh', siglum: 'G 3', language: AE },
            { slug: 'gah-aiwisruthrem', title_zh: '夜時禱', title_orig: 'Aiwisrūθrima Gāh', siglum: 'G 4', language: AE },
            { slug: 'gah-ushahin', title_zh: '子時禱', title_orig: 'Ušahin Gāh', siglum: 'G 5', language: AE, note: '午夜至日出；萬迪達德於此時段誦唸。' },
          ],
        },
        {
          key: 'ka-sirozah', label: '三十日誦', label_en: 'Sīrōzah',
          desc: '祆教曆一月三十日，每日各有一位守護神；本篇逐日唱名。祆教曆法的骨架即在此。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'sirozah-1', title_zh: '三十日誦（小本）', title_orig: 'Sīrōzah I', siglum: 'S 1', language: AE },
            { slug: 'sirozah-2', title_zh: '三十日誦（大本）', title_orig: 'Sīrōzah II', siglum: 'S 2', language: AE },
          ],
        },
        {
          key: 'ka-afrinagan', label: '四祝禱', label_en: 'Āfrīnagāns',
          desc: '為亡者、節期與季節所作的祝禱，配合供品行禮。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'afrinagan-dahman', title_zh: '善者祝禱', title_orig: 'Āfrīnagān i Dahmān', siglum: 'A 1', language: AE },
            { slug: 'afrinagan-gatha', title_zh: '伽薩五日祝禱', title_orig: 'Āfrīnagān i Gāhānbār', siglum: 'A 2', language: AE, note: '歲末五日（伽薩日）追念亡者所誦。' },
            { slug: 'afrinagan-gahanbar', title_zh: '六節期祝禱', title_orig: 'Āfrīnagān i Gāhānbār', siglum: 'A 3', language: AE },
            { slug: 'afrinagan-rapithwin', title_zh: '午時神祝禱', title_orig: 'Āfrīnagān i Rapiθwin', siglum: 'A 4', language: AE },
          ],
        },
      ],
    },

    // ───────────────────────── 殘篇 ─────────────────────────
    {
      key: 'fragment', sigil: '殘', name: '阿維斯陀殘篇', name_orig: 'Avestan Fragments', name_en: 'Avestan Fragments',
      era: '各篇不一', extent: '約 12 種',
      summary:
        '不屬於上述任何一部傳世祭典書、但確為阿維斯陀語的零散文本。其中兩部（《儀軌書》《修學書》）篇幅可觀且極重要——它們是薩珊祭司法規僅存的直接證據；其餘多為單葉或引文。這一卷的存在本身說明了一件事：傳世的阿維斯陀不是一部書的殘餘，而是一座圖書館燒剩的幾個書架。',
      divisions: [
        {
          key: 'fr-law', label: '祭司法規', label_en: 'Priestly Law',
          desc: '法類納斯克僅存的兩部大殘篇，附巴列維語逐句註釋。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'nirangistan', title_zh: '儀軌書', title_orig: 'Nīrangistān', title_en: 'Nirangistan', siglum: 'N', language: `${AE}＋中古波斯語註`, status: 'fragment', extent: '約 110 節', note: '祭典執行的細則：誦錯了怎麼辦、誰有資格主祭、器具如何處置。薩珊祭司實務的唯一直接材料。' },
            { slug: 'herbedestan', title_zh: '修學書', title_orig: 'Hērbedestān', title_en: 'Herbedestan', siglum: 'H', language: `${AE}＋中古波斯語註`, status: 'fragment', extent: '約 20 節', note: '論宗教教育：誰該去求學、去多久、家業與學業如何權衡。含女性受教的規定。' },
            { slug: 'pursishniha', title_zh: '問答書', title_orig: 'Pursišnīhā', siglum: 'P', language: `${AE}＋中古波斯語註`, status: 'fragment', note: '五十九條問答形式的法規殘篇。' },
          ],
        },
        {
          key: 'fr-eschat', label: '末世與靈魂', label_en: 'Eschatology',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'hadhokht-nask', title_zh: '哈多赫特納斯克', title_orig: 'Hāδōxt Nask', siglum: 'HN', language: AE, status: 'fragment', extent: '3 章', note: '義人與惡人死後三日的靈魂經歷；祆教來世觀最重要的原典段落，「自己的宗教」化為少女前來相迎即出於此。' },
            { slug: 'aogemadaecha', title_zh: '我等奉行', title_orig: 'Aogəmadaēčā', siglum: 'Aog', language: `${AE}＋巴列維語`, status: 'fragment', extent: '29 節', note: '喪禮誦本，論死之必然。篇名取自首句「我等奉行」。' },
            { slug: 'vishtasp-yasht', title_zh: '維什塔斯帕讚', title_orig: 'Vištāsp Yašt', siglum: 'Vyt', language: AE, status: 'fragment', extent: '8 章', note: '查拉圖斯特拉向護法王維什塔斯帕宣教。' },
          ],
        },
        {
          key: 'fr-misc', label: '零散殘葉', label_en: 'Scattered Fragments',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'frahang-i-oim', title_zh: '詞義彙編', title_orig: 'Frahang ī Ōīm', siglum: 'FiO', language: `${AE}／中古波斯語`, status: 'fragment', note: '阿維斯陀語—中古波斯語對譯詞表；不是經文而是字典，卻因此保存了大量今已無出處的阿維斯陀語詞。' },
            { slug: 'westergaard-fragments', title_zh: '韋斯特加德殘篇', title_orig: 'Westergaard Fragments', siglum: 'FrW', language: AE, status: 'fragment', note: '韋斯特加德所輯，編號 1–10。' },
            { slug: 'darmesteter-fragments', title_zh: '達梅斯特殘篇', title_orig: 'Darmesteter Fragments', siglum: 'FrD', language: AE, status: 'fragment' },
            { slug: 'anklesaria-fragments', title_zh: '安克萊薩里亞殘篇', title_orig: 'Anklesaria Fragments', siglum: 'FrA', language: AE, status: 'fragment' },
            { slug: 'vaethanask', title_zh: '維坦納斯克', title_orig: 'Vaēθā Nask', siglum: 'Vn', language: AE, status: 'fragment', note: '真偽有爭議，部分學者視為晚期偽作。' },
          ],
        },
      ],
    },

    // ───────────────────────── 佚失納斯克 ─────────────────────────
    {
      key: 'nask', sigil: '佚', name: '二十一納斯克', name_orig: 'Nasks', name_en: 'The Twenty-One Nasks',
      era: '薩珊時代編定（材料更早）', extent: '21 部，存 1 部半',
      summary:
        '薩珊祆教的完整正典目錄，按全教第一禱詞「阿胡納‧瓦伊里亞」的二十一個詞分為二十一部，三組各七部。今日僅《萬迪達德》完整傳世、《讚頌書》大致等同亞斯納的核心段落，其餘十九部全佚——**我們對它們的全部認識來自《丹卡爾德》第八、九卷的逐部撮要**。因此本卷各條的「原文欄」與「英文欄」指的都是丹卡爾德的撮要，不是納斯克本身；版面必須標明這一點，否則讀者會以為讀到了原書。',
      divisions: [
        {
          key: 'nask-gasanig', label: '伽薩類（1–7）', label_en: 'Gāsānīg Nasks',
          desc: '教義與靈修類，以伽薩為核心。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'nask-stod-yasn', title_zh: '讚頌書', title_orig: 'Stōd Yasn', siglum: 'Nask 1', status: 'partial', via: '《丹卡爾德》9.1 以下', note: '大致等同今亞斯納的伽薩與讚頌段，是唯一實質傳世的伽薩類納斯克。' },
            { slug: 'nask-sudgar', title_zh: '益世書', title_orig: 'Sūdgar', siglum: 'Nask 2', status: 'lost-summary', via: '《丹卡爾德》9.1–9.23' },
            { slug: 'nask-warshtmansr', title_zh: '聖言功效書', title_orig: 'Warštmānsr', siglum: 'Nask 3', status: 'lost-summary', via: '《丹卡爾德》9.24–9.46' },
            { slug: 'nask-bag', title_zh: '分授書', title_orig: 'Bag', siglum: 'Nask 4', status: 'lost-summary', via: '《丹卡爾德》9.47–9.68' },
            { slug: 'nask-wastag', title_zh: '瓦斯塔格', title_orig: 'Wastag', siglum: 'Nask 5', status: 'lost-summary', via: '——', note: '連撮要都已不存，僅知其名。' },
            { slug: 'nask-hadoxt', title_zh: '誦讚書', title_orig: 'Hādōxt', siglum: 'Nask 6', status: 'lost-summary', via: '《丹卡爾德》8.45', seealso: '殘篇卷‧哈多赫特納斯克' },
            { slug: 'nask-spand', title_zh: '聖行書', title_orig: 'Spand', siglum: 'Nask 7', status: 'lost-summary', via: '《丹卡爾德》8.14', note: '查拉圖斯特拉傳記所本；後世一切先知生平材料的源頭。' },
          ],
        },
        {
          key: 'nask-hadag', label: '中類（8–14）', label_en: 'Hadag-mānsrīg Nasks',
          desc: '兼涉教義與世務，含天文、醫學、法律與王統。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'nask-damdad', title_zh: '創造書', title_orig: 'Dāmdād', siglum: 'Nask 8', status: 'lost-summary', via: '《丹卡爾德》8.5', note: '祆教宇宙論的原典；《本達希什》大量取材於此。' },
            { slug: 'nask-nadar', title_zh: '星占書', title_orig: 'Nādar', siglum: 'Nask 9', status: 'lost-summary', via: '——' },
            { slug: 'nask-pajag', title_zh: '節期書', title_orig: 'Pāzag', siglum: 'Nask 10', status: 'lost-summary', via: '《丹卡爾德》8.7' },
            { slug: 'nask-ratustaiti', title_zh: '職司書', title_orig: 'Raθwištāiti', siglum: 'Nask 11', status: 'lost-summary', via: '《丹卡爾德》8.8' },
            { slug: 'nask-baris', title_zh: '巴里什', title_orig: 'Bariš', siglum: 'Nask 12', status: 'lost-summary', via: '《丹卡爾德》8.9' },
            { slug: 'nask-kaskisrobang', title_zh: '教誨書', title_orig: 'Kaškaysrōb', siglum: 'Nask 13', status: 'lost-summary', via: '《丹卡爾德》8.10' },
            { slug: 'nask-vishtasp-sast', title_zh: '維什塔斯帕教誨書', title_orig: 'Wištāsp-sāst', siglum: 'Nask 14', status: 'lost-summary', via: '《丹卡爾德》8.11' },
          ],
        },
        {
          key: 'nask-dadig', label: '法類（15–21）', label_en: 'Dādīg Nasks',
          desc: '律法類。祆教法制的主體，佚失最為可惜——薩珊法律思想因此只能靠《宗教判例》等後出書間接推知。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'nask-nikadum', title_zh: '尼卡杜姆', title_orig: 'Nīkādūm', siglum: 'Nask 15', status: 'lost-summary', via: '《丹卡爾德》8.16–8.20' },
            { slug: 'nask-ganaba-sar-nizad', title_zh: '盜賊律', title_orig: 'Ganabā-sar-nizad', siglum: 'Nask 16', status: 'lost-summary', via: '《丹卡爾德》8.21' },
            { slug: 'nask-huspram', title_zh: '胡斯帕拉姆', title_orig: 'Huspāram', siglum: 'Nask 17', status: 'lost-summary', via: '《丹卡爾德》8.28–8.37', seealso: '殘篇卷‧儀軌書、修學書', note: '《儀軌書》與《修學書》原屬本納斯克，是法類僅存的實體殘餘。' },
            { slug: 'nask-sakadum', title_zh: '薩卡杜姆', title_orig: 'Sagādūm', siglum: 'Nask 18', status: 'lost-summary', via: '《丹卡爾德》8.38–8.43' },
            { slug: 'nask-videvdad', title_zh: '萬迪達德', title_orig: 'Widēwdād', siglum: 'Nask 19', status: 'whole', seealso: '長祭典部‧萬迪達德', note: '二十一納斯克中唯一完整傳世者。' },
            { slug: 'nask-chihrdad', title_zh: '族裔書', title_orig: 'Čihrdād', siglum: 'Nask 20', status: 'lost-summary', via: '《丹卡爾德》8.13', note: '自伽約馬爾特以下的人類世系與伊朗諸族起源；伊朗民族史詩傳統的遠源。' },
            { slug: 'nask-bagan-yasht', title_zh: '諸神讚', title_orig: 'Bayān Yasn', siglum: 'Nask 21', status: 'lost-summary', via: '《丹卡爾德》8.15', seealso: '讚歌部‧亞什特', note: '今傳亞什特多出於此。' },
          ],
        },
      ],
    },
  ],
}
