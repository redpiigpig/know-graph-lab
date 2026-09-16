// 附錄 —— 敵證與外部記述
//
// 🚨 **本藏 scriptural = false。這一藏裡沒有一個字是摩尼教徒寫的。**
//
// 收它的理由有兩個，都很硬：
//
//   一、**1904 年之前，全世界對摩尼教的認識百分之百來自這一批。**
//     吐魯番探險隊挖出第一批殘卷以前，摩尼教在學術上是一個「只有敵人的宗教」。
//     今天我們讀得到教內文獻了，但整個領域的問題意識、術語與分期
//     仍有一大半是在這批材料上長出來的，繞不過去。
//
//   二、**七經裡好幾部的僅存內文，就卡在這些駁論的引文裡。**
//     《生命寶庫》最長的一段在奧古斯丁《論自然之善》，
//     《基要書信》的開頭在奧古斯丁《駁基要書信》，
//     《祕密之書》的十八章章名在阿爾—納迪姆《群書類述》。
//     不收這一藏，正藏那七卷就真的一個字都沒有了。
//
// ══════════ 引用前先看 hostile 等級 ══════════
//
//   verbatim（逐句引錄）  → 引文本身可當摩尼的原話用
//   paraphrase（轉述）    → 用語已經過駁論者的選擇，只能當大意
//   framed（敵意框架）    → 只能當「反對者如何理解摩尼教」的證據，不可當教義用
//
//   這個分級不是學術潔癖。奧古斯丁逐句抄《基要書信》再駁，那些抄錄句可靠；
//   但他轉述摩尼教徒「吃瓜果以解放光明分子」時已經隔了一層嘲諷，
//   而《阿基勞斯行傳》整本是一場虛構的辯論，連摩尼的出身都編造過。
//   三者混用，就會寫出把敵人的嘲諷當教義引的論文。
//
// ══════════ 取源：本藏是五藏中英譯條件最好的 ══════════
//
//   奧古斯丁反摩尼教諸書的英譯在《尼西亞前後期教父集》第一系列第四卷，
//   《阿基勞斯行傳》在《尼西亞前教父集》第六卷，
//   艾弗冷《駁謬論》有米契爾 1912／1921 年英譯，
//   比魯尼《古代遺跡》有薩豪 1879 年英譯——**全部公有領域**。
//   而且本站 /fathers 已收 ANF／NPNF 全套，奧古斯丁那六種可直接接既有語料。

import type { ManiCanon } from './types'

/** 公有領域英譯（ANF／NPNF／19 世紀校譯本），且多數已在本站 /fathers */
const PD = { orig: 'available', en: 'available', zh: 'none' } as const

export const TESTIMONIA_CANON: ManiCanon = {
  key: 'testimonia',
  name: '敵證與外部記述',
  name_en: 'Testimonia and Hostile Sources',
  glyph: '證',
  subtitle: '附錄 — 非摩尼教徒所記（本藏不是經）',
  scriptural: false,
  language: '拉丁語、希臘語、敘利亞語、阿拉伯語',
  era: '4–11 世紀',
  summary:
    '反對摩尼教的人所寫的東西：教父的駁論、辯論紀錄、帝國敕令、'
    + '入教者必須誦讀的棄絕式，以及伊斯蘭學者的著錄。'
    + '這一藏**不是摩尼教的經典**，收進來是因為兩件事：'
    + '在吐魯番與梅迪奈特馬迪出土之前，人類對摩尼教的全部知識都在這裡；'
    + '而且摩尼親撰七經今日僅存的若干段落，就夾在這些駁論的引文之中。'
    + '每一條都標了敵證等級——引用之前請先確認你讀到的是摩尼的話，'
    + '還是敵手轉述摩尼的話，還是敵手嘲諷摩尼的話。',
  parts: [
    {
      key: 'p-latin', label: '拉丁教父', label_en: 'The Latin Fathers',
      desc:
        '以奧古斯丁為主。他本人當過九年摩尼教聽者，'
        + '是古代唯一**既熟悉教內文獻又全力反對它**的作者，'
        + '因此他的駁論同時是最可靠的引文來源與最有敵意的框架。',
      volumes: ['augustine', 'latin-other'],
    },
    {
      key: 'p-greek-syriac', label: '希臘與敘利亞', label_en: 'Greek and Syriac Sources',
      desc: '希臘語的辯論文學與棄絕式，以及敘利亞語教父的駁論與神譜記述。',
      volumes: ['greek', 'syriac'],
    },
    {
      key: 'p-islamic', label: '伊斯蘭著錄', label_en: 'Islamic Sources',
      desc:
        '阿拉伯與波斯學者的著錄。與教父不同，這些作者多半沒有摧毀摩尼教的動機，'
        + '而是把它當作一個值得記錄的學派，因此往往更冷靜、也更完整。',
      volumes: ['islamic'],
    },
    {
      key: 'p-imperial', label: '帝國法令', label_en: 'Imperial Legislation',
      desc: '羅馬帝國查禁摩尼教的法令。摩尼教是羅馬史上第一個被明令處死刑的宗教。',
      volumes: ['imperial'],
    },
  ],
  volumes: [
    {
      key: 'augustine',
      sigil: '奧',
      name: '奧古斯丁駁摩尼教諸書',
      name_en: 'Augustine against the Manichaeans',
      provenance: '北非希波；拉丁文傳世',
      era: '388–405 年',
      extent: '六種',
      summary:
        '奧古斯丁十九歲成為摩尼教聽者，前後九年，三十歲後皈依大公教會並轉而全力反對它。'
        + '這個經歷使他成為古代最特別的證人：'
        + '他讀過《基要書信》的原本，見過摩尼教主教福斯圖斯，'
        + '知道教團內部聽者與選民的實際分別。'
        + '他的駁論因此保存了大量**逐句抄錄**的摩尼教原文——'
        + '為了駁得徹底，他得先把對方的話一字不差地擺出來。'
        + '🚨 但同一批文本也是最有敵意的：他要證明的是自己曾經有多愚蠢。',
      divisions: [
        {
          key: 'd-aug',
          label: '奧古斯丁',
          columns: PD,
          texts: [
            {
              slug: 'contra-epistulam-fundamenti',
              title_zh: '駁基要書信',
              title_orig: 'Contra epistulam Manichaei quam vocant fundamenti',
              title_en: 'Against the Fundamental Epistle of Mani',
              siglum: 'c. ep. fund.',
              author: '希波的奧古斯丁',
              era: '396 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '本書即引文載體',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '存《基要書信》開頭數段的逐句引錄',
              note: '🚨 七經之一《書信集》中最重要一封的僅存文本，就在這本駁論裡。',
              intro:
                '奧古斯丁逐句抄錄《基要書信》再逐句反駁，'
                + '於是這部駁論成了那封信的存本。'
                + '信的開頭「摩尼，耶穌基督的使徒，蒙父神揀選」保存於此，'
                + '與吐魯番殘卷 M 17 的《活福音》開卷語格式完全一致，'
                + '互相印證了摩尼書信的固定開場。'
                + '🚨 引用時務必記得：我們讀到的是奧古斯丁**選**來駁的部分，'
                + '他沒有義務抄完整封信，事實上他也沒有。',
              seealso: ['epistles'],
            },
            {
              slug: 'contra-faustum',
              title_zh: '駁摩尼教徒福斯圖斯',
              title_orig: 'Contra Faustum Manichaeum',
              title_en: 'Against Faustus the Manichaean',
              siglum: 'c. Faust.',
              author: '希波的奧古斯丁',
              era: '約 400 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '本書即引文載體',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '三十三卷，含福斯圖斯《章句》的整段引錄',
              note: '摩尼教主教福斯圖斯的著作靠這部駁論整段保存下來。',
              intro:
                '米勒維的福斯圖斯是北非摩尼教的主教，也是年輕的奧古斯丁一度極為仰慕的人。'
                + '他寫了一部《章句》攻擊大公教會的聖經觀，'
                + '奧古斯丁逐條抄錄再逐條反駁，共成三十三卷。'
                + '結果是：福斯圖斯的原作雖佚，卻**成段地活在敵手的書裡**，'
                + '成為西方摩尼教護教學僅存的完整樣本。'
                + '這裡可以清楚看見一個成熟的摩尼教徒如何論證——'
                + '不是靠神話，而是靠聖經批評。',
            },
            {
              slug: 'contra-fortunatum',
              title_zh: '駁福圖納圖斯辯論錄',
              title_orig: 'Acta contra Fortunatum Manichaeum',
              title_en: 'Acts of the Debate with Fortunatus the Manichaean',
              siglum: 'c. Fort.',
              author: '希波的奧古斯丁',
              era: '392 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '本書即引文載體（速記逐字稿）',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '兩日辯論的逐字紀錄',
              note: '🚨 速記逐字稿——古代唯一一份摩尼教徒當場說話的紀錄。',
              intro:
                '392 年，奧古斯丁與摩尼教長老福圖納圖斯在希波公開辯論兩天，'
                + '全程由速記員記下。這份文件因此獨一無二：'
                + '其他材料裡的摩尼教徒都是被人轉述的，'
                + '只有這裡能讀到一個摩尼教徒**當場、即席、用自己的話**'
                + '回應詰問、閃避、引經據典。'
                + '辯論以福圖納圖斯承認無法回答、隨後離開希波告終——'
                + '這個結局由勝方記錄，讀的時候要記得。',
              seealso: ['treasure-of-life'],
            },
            {
              slug: 'de-natura-boni',
              title_zh: '論自然之善',
              title_orig: 'De natura boni',
              title_en: 'On the Nature of the Good',
              siglum: 'nat. b.',
              author: '希波的奧古斯丁',
              era: '約 399 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '本書第 44 章引錄《生命寶庫》長段',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '末章含《生命寶庫》與《基要書信》引文',
              note: '🚨 七經之一《生命寶庫》最長的存世片段在這本書的第 44 章。',
              intro:
                '一部論惡之本質的哲學作品，末尾為了坐實摩尼教的荒謬，'
                + '奧古斯丁抄錄了《生命寶庫》裡光明使者以美色誘出黑暗魔君體內光明的一段。'
                + '他的目的是要讀者自己看看這有多淫穢；'
                + '結果是這段成了該書最長的存世片段。'
                + '🚨 這一條最能說明敵證的兩面性：'
                + '我們拿到了原文，但拿到的是一個敵人**專門挑出來敗壞名聲**的原文，'
                + '它在全書中的份量與脈絡，我們一無所知。',
              seealso: ['treasure-of-life'],
            },
            {
              slug: 'de-duabus-animabus',
              title_zh: '論二魂',
              title_orig: 'De duabus animabus',
              title_en: 'On the Two Souls',
              siglum: 'duab. an.',
              author: '希波的奧古斯丁',
              era: '約 392 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'paraphrase',
              via: '轉述摩尼教二元人性論',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '一卷',
              note: '駁「人有善惡二魂」之說。屬轉述而非逐句引錄。',
              intro:
                '摩尼教主張人身上有兩個靈魂——一個出於光明、一個出於黑暗，'
                + '兩者在同一個人裡爭戰。奧古斯丁針對這個主張寫了此書，'
                + '主要靠自己當年當聽者的記憶重述對方立場。'
                + '所以它是 paraphrase 而非 verbatim：'
                + '這裡的「摩尼教義」是一個離教者記憶中的版本，'
                + '未必是任何一部教內文獻的原話。',
            },
            {
              slug: 'de-genesi-contra-manichaeos',
              title_zh: '駁摩尼教論創世記',
              title_orig: 'De Genesi contra Manichaeos',
              title_en: 'On Genesis, against the Manichaeans',
              siglum: 'Gn. adv. Man.',
              author: '希波的奧古斯丁',
              era: '388–389 年',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'framed',
              via: '針對摩尼教對《創世記》的攻擊而作',
              provenance: '傳世；英譯見《尼西亞前後期教父集》第一系列第四卷',
              extent: '兩卷',
              note: '奧古斯丁皈依後最早的作品之一。敵意框架最重的一種。',
              intro:
                '摩尼教徒拒斥《舊約》，認為創造這個世界的神既無能又殘暴。'
                + '奧古斯丁剛皈依不久便寫此書回應，用寓意解經化解字面難處。'
                + '書中對摩尼教立場的呈現高度簡化且帶著新皈依者的激烈，'
                + '故列為 framed：'
                + '它能告訴我們大公教會如何理解摩尼教的聖經批評，'
                + '但不能拿來當摩尼教聖經觀的證據。',
            },
          ],
        },
      ],
    },
    {
      key: 'latin-other',
      sigil: '拉',
      name: '其他拉丁文獻',
      name_en: 'Other Latin Sources',
      provenance: '北非；拉丁文傳世與出土',
      era: '4–5 世紀',
      extent: '數種',
      summary:
        '奧古斯丁以外的拉丁材料，其中《特貝薩抄本》性質特殊：'
        + '它是**教內文獻**而非敵證，出土於今阿爾及利亞，'
        + '討論聽者與選民的分工，是西方摩尼教罕見的自述。'
        + '本卷把它與敵證並置而特別標明，'
        + '是因為拉丁文的摩尼教材料實在太少，分不出一卷來。',
      divisions: [
        {
          key: 'd-latin',
          label: '其他拉丁文獻',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'tebessa-codex',
              title_zh: '特貝薩抄本',
              title_orig: 'Codex Thevestinus',
              title_en: 'The Tebessa Codex',
              siglum: 'Cod. Thev.',
              era: '4 世紀',
              language: '拉丁語',
              provenance: '阿爾及利亞特貝薩附近出土',
              status: 'fragment',
              note: '🚨 本卷唯一的**教內**文獻：西方摩尼教徒自己寫的，不是敵證。',
              intro:
                '一份殘缺的拉丁文羊皮抄本，論聽者與選民兩級信徒的分工與義務，'
                + '並以保羅書信為據替這個雙層制度辯護。'
                + '它證明北非的摩尼教團不只是奧古斯丁筆下的影子，'
                + '而有自己的拉丁文神學論述。'
                + '因為是教內文獻，它沒有 hostile 等級——'
                + '本站把它放在這一卷純粹是因為拉丁文材料太少，'
                + '版面上會另作標示。',
            },
          ],
        },
      ],
    },
    {
      key: 'greek',
      sigil: '希',
      name: '希臘文獻',
      name_en: 'Greek Sources',
      provenance: '希臘語世界傳世',
      era: '4–9 世紀',
      extent: '數種',
      summary:
        '希臘語的反摩尼教文學，以《阿基勞斯行傳》影響最大——'
        + '中世紀西方關於摩尼生平的「常識」（他本名庫布里科斯、'
        + '是個買來的奴隸、從前人那裡偷了教義）全部出自這一本，'
        + '而這些說法今天已知**大半是編的**。'
        + '另收拜占庭教會要求入教者當眾誦讀的棄絕式，'
        + '那是一份逐條列舉摩尼教信條以供咒詛的清單，'
        + '意外地成為教義的條目式摘要。',
      divisions: [
        {
          key: 'd-greek',
          label: '希臘文獻',
          columns: PD,
          texts: [
            {
              slug: 'acta-archelai',
              title_zh: '阿基勞斯行傳',
              title_orig: 'Acta Archelai',
              title_en: 'The Acts of Archelaus',
              siglum: 'Acta Arch.',
              author: '赫格莫尼烏斯',
              era: '約 340 年',
              language: '希臘語（今全本僅存拉丁譯本）',
              status: 'hostile',
              hostile: 'framed',
              via: '本書即載體',
              provenance: '希臘文原本已佚，存拉丁譯本；英譯見《尼西亞前教父集》第六卷',
              extent: '全本',
              note: '🚨 中世紀關於摩尼生平的「常識」出自此書，而其中大半是虛構。',
              intro:
                '一場虛構的公開辯論：摩尼與主教阿基勞斯當眾對質，'
                + '摩尼理屈詞窮而遁走。'
                + '書中給了摩尼一套完整的身世——本名庫布里科斯、'
                + '是寡婦買來的奴隸、教義是從一個叫特爾賓圖斯的人那裡偷來的——'
                + '這套說法統治了西方一千多年，直到吐魯番與科隆的材料出土'
                + '才被證明大半是編造。'
                + '🚨 列為 framed：本書可以當「四世紀的人如何想像摩尼」的證據，'
                + '**不可**當摩尼生平的史料用。'
                + '但書中所引摩尼致馬爾凱路斯的一封信，另有學者認為出自真本，'
                + '那一段須個別判斷。',
              seealso: ['homily-crucifixion'],
            },
            {
              slug: 'abjuration-formula',
              title_zh: '棄絕式',
              title_orig: 'Formula abiurationis',
              title_en: 'The Greek Formula of Abjuration',
              siglum: 'Form. abiur.',
              era: '6–9 世紀',
              language: '希臘語',
              status: 'hostile',
              hostile: 'paraphrase',
              via: '拜占庭教會入教儀文',
              provenance: '傳世於希臘教父文獻集',
              extent: '長短兩式',
              note: '要求入教者逐條咒詛摩尼教信條。意外成為教義的條目式清單。',
              intro:
                '摩尼教徒改宗進入拜占庭教會時，必須當眾誦讀一份棄絕文，'
                + '逐條詛咒自己原先所信的每一項——'
                + '諸神的名字、二宗三際的架構、選民的戒律，一一列舉。'
                + '編寫者為了確保無一漏網，把教義整理得相當完整，'
                + '於是這份為了消滅一個宗教而寫的清單，'
                + '成了後世重建其信條的路標之一。'
                + '🚨 但條目經過敵手的取捨與排序，屬 paraphrase。',
            },
          ],
        },
      ],
    },
    {
      key: 'syriac',
      sigil: '敘',
      name: '敘利亞文獻',
      name_en: 'Syriac Sources',
      provenance: '敘利亞語世界傳世',
      era: '4–8 世紀',
      extent: '數種',
      summary:
        '敘利亞語的材料有一項別處沒有的優勢：'
        + '**它與摩尼用的是同一種語言**。'
        + '艾弗冷駁斥摩尼時讀的是敘利亞語原本，'
        + '巴爾‧科奈記錄摩尼教神譜時抄下的神名也是敘利亞語形式，'
        + '因此這批材料在術語與神名上最接近原貌，'
        + '常被用來校正科普特文與伊朗語譯本裡的音譯。',
      divisions: [
        {
          key: 'd-syriac',
          label: '敘利亞文獻',
          columns: PD,
          texts: [
            {
              slug: 'ephrem-refutations',
              title_zh: '駁謬論',
              title_orig: 'Prose Refutations',
              title_en: "Ephrem's Prose Refutations of Mani, Marcion and Bardaisan",
              siglum: 'Ephr. Ref.',
              author: '敘利亞的艾弗冷',
              era: '4 世紀',
              language: '敘利亞語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '逐句引錄摩尼教敘利亞語原文再駁',
              provenance: '傳世；米契爾 1912／1921 年校訂英譯，公有領域',
              extent: '數卷，含大量引文',
              note: '🚨 唯一用摩尼的母語直接駁斥他的古代作者。術語價值極高。',
              intro:
                '艾弗冷與摩尼同用敘利亞語，'
                + '他讀的是原本而非譯本，引的也是原詞。'
                + '因此他的駁論在術語上比任何譯本都可靠：'
                + '科普特文與中古波斯語的摩尼教神名多是音譯，'
                + '要還原敘利亞語原形，往往得靠艾弗冷這裡的拼法。'
                + '米契爾的校本把敘利亞文與英譯並刊，且已進入公有領域，'
                + '是本藏取源條件最好的條目之一。',
            },
            {
              slug: 'theodore-bar-konai',
              title_zh: '學者書',
              title_orig: 'Liber Scholiorum',
              title_en: 'The Book of Scholia',
              siglum: 'Lib. Schol. XI',
              author: '塞奧多爾‧巴爾‧科奈',
              era: '約 792 年',
              language: '敘利亞語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '第十一卷逐條記錄摩尼教神譜並引原文',
              provenance: '傳世；有校本與譯本',
              extent: '第十一卷之摩尼教章',
              note: '🚨 摩尼教神譜最完整的外部記述。研究其宇宙論必引。',
              intro:
                '一位東方教會主教所編的神學問答集，'
                + '第十一卷處理各種異端，其中摩尼教一章'
                + '把整套創世神話從頭到尾記了一遍：'
                + '光明之父與五種光明分子、初人下降、'
                + '活靈的呼喚與回應、日月二船、光明少女……'
                + '而且保留了敘利亞語的神名原形。'
                + '在科普特文《凱法萊亞》刊布之前，'
                + '這一章是重建摩尼教宇宙論的**主要依據**，'
                + '至今仍是不可繞過的一條。',
            },
          ],
        },
      ],
    },
    {
      key: 'islamic',
      sigil: '伊',
      name: '伊斯蘭著錄',
      name_en: 'Islamic Sources',
      provenance: '阿拉伯語與波斯語世界傳世',
      era: '10–11 世紀',
      extent: '數種',
      summary:
        '阿拉伯與波斯學者的著錄。這一卷與教父那幾卷性質不同：'
        + '阿爾—納迪姆與比魯尼多半沒有摧毀摩尼教的動機，'
        + '而是把它當作一個值得著錄的學派來處理——'
        + '列書名、記章數、抄教義、註明自己引用的是哪一本書。'
        + '結果是這些穆斯林作者提供的資訊，'
        + '在**準確度與完整度上往往勝過基督教教父**。'
        + '《群書類述》所記的七經書目與《祕密之書》十八章章名，'
        + '是正藏那一藏能夠成立的骨幹。',
      divisions: [
        {
          key: 'd-islamic',
          label: '伊斯蘭著錄',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'fihrist',
              title_zh: '群書類述',
              title_orig: 'Kitāb al-Fihrist',
              title_en: 'The Fihrist of al-Nadīm',
              siglum: 'Fihrist IX',
              author: '伊本‧納迪姆',
              era: '987 年',
              language: '阿拉伯語',
              status: 'hostile',
              hostile: 'paraphrase',
              via: '第九卷摩尼教章，逐部著錄正典書目',
              provenance: '傳世；弗呂格爾 1862 年阿拉伯文校本（公有領域）；道奇 1970 年英譯（版權內）',
              extent: '第九卷之摩尼教章',
              note: '🚨 七經書目、《祕密之書》十八章章名的出處。正藏的骨幹。',
              intro:
                '十世紀巴格達書商所編的一部書目總覽，'
                + '第九卷專論摩尼教，列出摩尼親撰各書的書名、'
                + '逐章章名與大致篇幅，並記錄教團的階序與分裂。'
                + '作者的態度接近目錄學家而非論敵，'
                + '因此資料的體例與細節極為可靠。'
                + '本站正藏之所以能按書目立卷，這一章是主要依據。'
                + '🚨 列為 paraphrase 而非 verbatim：'
                + '他著錄的是書名與內容提要，不是逐句抄錄原文。',
            },
            {
              slug: 'biruni-chronology',
              title_zh: '古代遺跡',
              title_orig: 'al-Āthār al-bāqiya',
              title_en: 'The Chronology of Ancient Nations',
              siglum: 'Bīrūnī',
              author: '比魯尼',
              era: '約 1000 年',
              language: '阿拉伯語',
              status: 'hostile',
              hostile: 'verbatim',
              via: '引錄《生命寶庫》《祕密之書》《沙卜爾干》數則',
              provenance: '傳世；薩豪 1879 年英譯，公有領域',
              extent: '摩尼教相關數節',
              note: '引錄七經原文數則，且註明出處。英譯公有領域。',
              intro:
                '中亞博學者比魯尼論各民族曆法與宗教的名著，'
                + '其中數處引錄摩尼親撰各書的段落，'
                + '而且**逐條註明引自哪一部**——'
                + '這在古代著錄裡罕見的嚴謹，使他的引文可以直接使用。'
                + '薩豪 1879 年的英譯早已進入公有領域，'
                + '是本卷可立即取用的條目。',
              seealso: ['treasure-of-life', 'sabuhragan'],
            },
          ],
        },
      ],
    },
    {
      key: 'imperial',
      sigil: '敕',
      name: '帝國法令',
      name_en: 'Imperial Legislation',
      provenance: '羅馬法律文獻傳世',
      era: '302–6 世紀',
      extent: '數條',
      summary:
        '摩尼教是羅馬帝國史上**第一個被明令處以死刑的宗教**，'
        + '而且這道敕令下在基督教自己還是非法宗教的時候。'
        + '戴克里先 302 年的敕令把摩尼教定為波斯來的敵國妖術，'
        + '命令焚燒經書、處決首領。'
        + '此後從君士坦丁到查士丁尼，歷代法典不斷加重刑度。'
        + '這批法令不含教義內容，'
        + '但它們解釋了為什麼這個宗教的文獻幾乎全是從沙裡挖出來的：'
        + '在地面上的那些，被有系統地燒光了。',
      divisions: [
        {
          key: 'd-imperial',
          label: '帝國法令',
          columns: PD,
          texts: [
            {
              slug: 'diocletian-edict',
              title_zh: '戴克里先反摩尼教敕令',
              title_orig: 'Edictum de Manichaeis',
              title_en: 'The Edict of Diocletian against the Manichaeans',
              siglum: 'Coll. 15.3',
              author: '戴克里先',
              era: '302 年（或 297 年）',
              language: '拉丁語',
              status: 'hostile',
              hostile: 'framed',
              via: '《摩西法與羅馬法對照集》15.3',
              provenance: '傳世於羅馬法律文獻集',
              extent: '一道敕令',
              note: '🚨 羅馬史上第一道判處某宗教死刑的法令，時在基督教合法化之前。',
              intro:
                '敕令把摩尼教定性為從波斯傳來的敵國邪術，'
                + '命令焚毀經書與首領、沒收財產、'
                + '身分高者流放礦場。'
                + '值得注意的是它的理由不是神學而是政治：'
                + '羅馬與薩珊正在交戰，一個來自敵國的宗教'
                + '被當成滲透。'
                + '這道敕令開了一個先例——'
                + '十年後，同一套機器轉過來對付基督徒，'
                + '再十年後，基督教合法，而摩尼教繼續被禁。',
            },
          ],
        },
      ],
    },
  ],
}
