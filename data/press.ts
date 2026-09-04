/**
 * 期刊與報紙 —— 刊物本位的一層，與教派／運動本位的「論文資料整理」平行且互相指涉。
 *
 * 同一份刊物在兩邊各出現一次：那邊按它屬於哪個教派或運動歸戶（做章節史料），
 * 這邊按它是什麼刊物排列（做政教關係史的媒體軸）。兩邊互指，不搬家。
 *
 * 🚨 `tier` 一定要顯示在卡片上。三級的差別很大，不標的話「1,232 篇」看起來
 *    會像全文都在——跟博碩士論文那欄漏標截斷是同一類錯（讓人以為拿到的比實際多）。
 */

/** 收錄層級。差別在「能不能進語料層」與「能不能引內文」。 */
export type PressTier =
  | 'full'      // 逐篇內文可讀，可進語料層
  | 'index'     // 只有篇名／日期／分類，可排年表可挑件，不進語料層
  | 'guide'     // 只記「在哪查、涵蓋範圍、怎麼進」，站內不存內容

export const TIER_LABEL: Record<PressTier, string> = {
  full: '全文',
  index: '篇目索引',
  guide: '檢索指引',
}

export const TIER_DESC: Record<PressTier, string> = {
  full: '逐篇內文已收錄，可全文檢索、可進語料層做逐年詞頻',
  index: '只收篇名、日期與分類，用來排年表與到館挑件；內文不在站內',
  guide: '授權不允許收錄，僅記錄查得到的地方與涵蓋範圍',
}

export type PressSide = '基督教' | '佛教' | '一般'

export interface PressTitle {
  slug: string
  name: string
  /** 沿革中的舊刊名，或並稱 */
  aka?: string[]
  side: PressSide
  /** 創刊—停刊；仍發行者留空 end。查不到確切創刊年就整個留空，不要拿收錄起始冒充 */
  start?: string
  end?: string
  publisher: string
  tier: PressTier
  /**
   * 資料庫的收錄斷限，跟創刊停刊是兩件事。
   * 例：《校園》1957 創刊，華藝只從 2005 年的 47 卷 1 期收起。
   * 兩者混為一談，就會在論文裡把「資料庫沒有」寫成「那些年沒出刊」。
   */
  coverage?: string
  /** 站內收錄量，給卡片顯示；guide 級留空 */
  holdings?: string
  /** 站內對應子頁（刊物本位 → 教派本位的互指） */
  to?: string
  /**
   * 這份刊在華藝有篇目索引（/research-data/press/<slug>）。
   * 跟 `to` 並存而不是取代它：全文那一份多半來自刊物自家網站，缺卷期與頁碼；
   * 華藝那一份有卷期頁碼但沒內文。做註腳要的是後者，讀內容要的是前者。
   */
  airiti?: boolean
  /** 站外檢索入口 */
  external?: { label: string; url: string }
  /** 為什麼這份刊物對論文有用；也寫清楚拿不到的部分 */
  note: string
}

/** 基督教三大報：長老教會、福音派、靈恩／復興系統各一，剛好是台灣新教的三條主線。 */
export const CHRISTIAN_PRESS: PressTitle[] = [
  {
    slug: 'tcnn',
    name: '台灣教會公報（新聞網）',
    side: '基督教',
    start: '2010-12',
    publisher: '台灣教會公報社',
    tier: 'full',
    holdings: '38,451 篇 / 4,730 萬字',
    to: '/research-data/pct/tcnn',
    note: '長老教會機關報的當代段。教會決議、社會議題發言與各中會動態的報導底本。',
  },
  {
    slug: 'poj',
    name: '白話字教會公報',
    aka: ['台南府城教會報', '台灣教會報'],
    side: '基督教',
    start: '1885-06',
    end: '1969-03',
    publisher: '台灣教會公報社',
    tier: 'full',
    holdings: '2,735 篇 / 344 萬字（漢羅）',
    to: '/research-data/pct/poj',
    note: '同一份機關報的白話字段，1969 年才改出華文。黃彰輝那一代之前，長老教會'
      + '公共發言的唯一底本。🚨 這是師大台文所的選輯不是全份；中研院語言所另有'
      + '逐頁掃描輸入的完整閩語資料庫（數位典藏 LAMINTX0008），須另洽授權。',
  },
  {
    slug: 'ct',
    name: '基督教論壇報',
    side: '基督教',
    start: '1965',
    publisher: '基督教論壇基金會',
    tier: 'full',
    holdings: '23,231 篇 / 4,658 萬字',
    to: '/research-data/evangelical/ct',
    note: '福音派系統最主要的教派報紙，與公報同文類，可在語料層並排看基督教內部'
      + '對同一議題的分裂。🚨 站上實際可用的斷限是 2019 年以後。',
  },
  {
    slug: 'krt',
    name: '國度復興報',
    side: '基督教',
    start: '2002',
    publisher: '財團法人國度復興傳播基金會（楊寧亞牧師創辦）',
    tier: 'index',
    external: { label: '國度復興報', url: 'https://www.krtnews.com.tw/' },
    note: '靈恩／復興系統，護家與同志運動議題上最積極發聲的一家，是議題結盟那一章的'
      + '對照組。🚨 兩個網域都取不到內文：舊站 krtnews.tw 只吐標題與日期，'
      + '現行站 www.krtnews.com.tw 的單篇頁連真瀏覽器都回空白 404。故只能做篇目索引。',
  },
]

/**
 * 基督教期刊 —— 報紙之外的另一半：教會的青年刊物與神學院的學報。
 *
 * 這一批的取源跟報紙那一批完全不同。教會刊物自家網站多半只掛當期或近幾年，
 * 舊刊要嘛沒有、要嘛只有內文而沒有卷期頁碼；**華藝線上圖書館反而整份收著**，
 * 而且帶著做註腳非有不可的三個欄位：卷期、起訖頁、正式作者署名。
 * 所以這一區的篇目一律走華藝（`airiti: true` → /research-data/press/<slug>），
 * 全文另循玄奘圖書館的訂閱。
 *
 * 🚨 華藝的收錄起始 ≠ 創刊。《校園》1957 年就創刊了，華藝從 2005 年起收；
 *    《神學與教會》1957 年創刊，華藝從 2015 年起收。`coverage` 記的是後者。
 */
export const CHRISTIAN_JOURNALS: PressTitle[] = [
  {
    slug: 'campus',
    name: '校園',
    aka: ['校園雜誌雙月刊', '校園團契（1957–1969 舊名）'],
    side: '基督教',
    start: '1957',
    end: '2026-04',
    publisher: '校園書房出版社（校園福音團契）',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/campus',
    external: { label: '校園書房出版社', url: 'https://shop.campus.org.tw/cm/' },
    note: '學園團契系統的旗艦刊物，1957 年隨校園福音團契一起創辦，原名《校園團契》，'
      + '1969 年改今名，2026 年 4 月出完最後一期停刊，前後近七十年。台灣福音派'
      + '知識青年的言論場，與長老教會的《新使者》恰成一對。'
      + '🚨 這是**校園書房出版社**的《校園》，不是任何一份校刊或學生刊物。',
  },
  {
    slug: 'new-messenger',
    name: '新使者',
    side: '基督教',
    start: '1990-12',
    publisher: '台灣基督長老教會總會（大專事工委員會系統）',
    tier: 'full',
    airiti: true,
    to: '/research-data/pct/new-messenger',
    note: '長老教會青年刊物。全文那一份取自教會的「焚而不燬」信仰資源網，'
      + '有內文但沒有卷期頁碼；華藝那一份反過來。兩份併看才引得動註腳。',
  },
  {
    slug: 'messenger',
    name: '使者',
    side: '基督教',
    start: '1963-02',
    end: '1990',
    publisher: '台灣基督長老教會總會（青年團契 TKC 系統）',
    tier: 'guide',
    external: { label: '臺灣期刊論文索引系統', url: 'https://tpl.ncl.edu.tw/NclService/JournalQuery' },
    note: '《新使者》的前身，1963 年 2 月創刊的月刊，1990 年 12 月起易名為《新使者》。'
      + '🚨 華藝沒有這一份（2026-09 以刊名查過，只命中《新使者》）；長老教會自家網站'
      + '也沒有回溯典藏。篇目要走國圖的臺灣期刊論文索引，或到台南神學院、'
      + '長老教會歷史檔案館調紙本。'
      + '🚨 另有一份美國「基督使者協會」（AFC）發行的《使者》雜誌，是**不同的刊物**，'
      + '別在書目裡混成一筆。',
  },
  {
    slug: 'wilderness',
    name: '曠野',
    side: '基督教',
    publisher: '基文社',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/wilderness',
    note: '解嚴前後知識分子取向的基督教評論刊物，社會關懷與政教議題的發言密度高，'
      + '立場既不在長老教會體制內、也不在福音派主流內，是第六章難得的第三個座標。',
  },
  {
    slug: 'theology-church',
    name: '神學與教會',
    side: '基督教',
    publisher: '南神出版社（台南神學院）',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/theology-church',
    note: '台南神學院學報。黃彰輝、宋泉盛、王憲治、黃伯和這條本土神學系譜的'
      + '學術發表主場，第四章的核心刊物。',
  },
  {
    slug: 'taiwan-theology',
    name: '台灣神學論刊',
    side: '基督教',
    publisher: '台灣神學院',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/taiwan-theology',
    note: '台灣神學院（台北）學報，與南神的《神學與教會》並為長老教會兩大神學學報；'
      + '北神南神的路線差異在這兩份刊物的選題上看得最清楚。',
  },
  {
    slug: 'ces-journal',
    name: '華神期刊',
    side: '基督教',
    publisher: '中華福音神學院',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/ces-journal',
    note: '福音派神學教育的代表學報，對照長老教會兩所神學院的學報最有用。'
      + '（台灣福音派那一區原先列為待補，現以華藝篇目補上。）',
  },
  {
    slug: 'sino-christian',
    name: '漢語基督教學術論評',
    side: '基督教',
    publisher: '中原大學宗教研究所',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/sino-christian',
    note: '漢語神學運動在台灣的學術據點，與香港《道風》同一問題意識而在台出版。',
  },
  {
    slug: 'logos-pneuma',
    name: '道風：基督教文化評論',
    side: '基督教',
    publisher: '漢語基督教文化研究所（香港）',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/logos-pneuma',
    note: '漢語神學的旗艦刊物。台灣的本土神學與香港的漢語神學是兩條不同的路，'
      + '這份刊物是後者的主場，收它是為了讓論文的對照組不只有台灣島內。',
  },
  {
    slug: 'jiandao',
    name: '建道學刊',
    side: '基督教',
    publisher: '建道神學院（香港）',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/jiandao',
    note: '香港福音派神學院學報，是香港教會在九七與反修例前後公共議題轉向的紀錄。',
  },
  {
    slug: 'collectanea',
    name: '神學論集',
    side: '基督教',
    publisher: '天主教輔仁聖博敏神學院',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/collectanea',
    note: '天主教在台的神學學報。本論文的基督教軸幾乎全是新教，收這一份是為了'
      + '在同婚與生命議題上，看得到天主教與新教福音派的立場其實不是同一套推理。',
  },
  {
    slug: 'dao-magazine',
    name: '道雜誌',
    side: '基督教',
    publisher: '台灣神學雜誌社',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/dao-magazine',
    note: '2001–2005 的短命刊物，只出了 24 期，但正好落在同志神學、性別議題'
      + '進入台灣教會論述的那幾年，密度高。',
  },
  {
    slug: 'baptist-annual',
    name: '浸神學刊',
    side: '基督教',
    publisher: '台灣浸信會神學院',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/baptist-annual',
    note: '浸信會系統的神學院學報。（華藝另有其舊刊名《臺灣浸信會神學院學術年刊》。）',
  },
]

/**
 * 佛學與宗教學學報 —— 與上面的基督教期刊平行，走同一條華藝管道。
 *
 * 跟下面 BUDDHIST_PRESS 那四份老雜誌的差別是：那四份是**教內言論刊物**
 * （海潮音、人生、菩提樹、獅子吼），這幾份是**學報**。前者是史料，後者是研究。
 * 兩邊都要，但不要混在同一組看。
 */
export const BUDDHIST_JOURNALS: PressTitle[] = [
  {
    slug: 'hongshi',
    name: '弘誓雙月刊',
    side: '佛教',
    publisher: '財團法人弘誓文教基金會',
    tier: 'index',
    airiti: true,
    to: '/research-data/yinshun-hongshi',
    note: '昭慧法師一系的機關刊物。站內另有從弘誓官網抓下來的全文那一份；'
      + '華藝這一份補的是卷期與頁碼。',
  },
  {
    slug: 'dharma-seals',
    name: '法印學報',
    side: '佛教',
    publisher: '財團法人弘誓文教基金會',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/dharma-seals',
    note: '弘誓的學術刊物，與《弘誓雙月刊》一教內一學術，第三章第四節（昭慧）主用。',
  },
  {
    slug: 'hcu-buddhist',
    name: '玄奘佛學研究',
    side: '佛教',
    publisher: '玄奘大學',
    tier: 'index',
    airiti: true,
    to: '/research-data/yinshun-hongshi/xuanzang',
    note: '站內另有從玄奘校網抓下來的全文那一份；華藝這一份補卷期頁碼。',
  },
  {
    slug: 'chbs-journal',
    name: '中華佛學學報',
    side: '佛教',
    publisher: '財團法人中華佛學研究所',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/chbs-journal',
    note: '聖嚴法師創辦的研究所學報，台灣佛學研究學術化的起點之一。'
      + '🚨 華藝把它拆成兩筆：舊刊名（至 26 期／2013）與現名 Journal of Chinese '
      + 'Buddhist Studies（27 期起）。要看完整年表兩筆都得看。',
  },
  {
    slug: 'chbs-studies',
    name: '中華佛學研究',
    side: '佛教',
    publisher: '財團法人中華佛學研究所',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/chbs-studies',
    note: '同一研究所的另一份，收研究生與年輕研究者的論文，與上面那份分工。',
  },
  {
    slug: 'ddbj',
    name: '法鼓佛學學報',
    side: '佛教',
    publisher: '法鼓文理學院',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/ddbj',
    note: '法鼓山系統的學報，聖嚴一系從研究所到學院的延伸。',
  },
  {
    slug: 'ntu-buddhist',
    name: '臺大佛學研究',
    side: '佛教',
    publisher: '《臺大佛學研究》編輯委員會',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/ntu-buddhist',
    note: '國立大學體制內的佛學研究，與教團辦的學報是兩種學術位置。'
      + '舊刊名《佛學研究中心學報》（至 13 期／2007）華藝另立一筆。',
  },
  {
    slug: 'fgu-journal',
    name: '佛光學報',
    side: '佛教',
    publisher: '佛光大學',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/fgu-journal',
    note: '星雲一系的學術刊物；人間佛教在佛光山這一支的論述基地。',
  },
  {
    slug: 'humanistic-buddhism',
    name: '人間佛教研究',
    side: '佛教',
    publisher: '香港中文大學人間佛教研究中心',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/humanistic-buddhism',
    note: '「人間佛教」四個字直接進刊名的學報，第三章的關鍵詞史看這一份最直接。',
  },
  {
    slug: 'huayen',
    name: '華嚴學報',
    side: '佛教',
    publisher: '社團法人中華民國佛教華嚴學會',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/huayen',
    note: '宗派型學報，收它是為了讓佛教側的取樣不要全是人間佛教一系。',
  },
]

/** 宗教學（跨教）學術期刊。做「宗教」這個概念本身在台灣怎麼被說的那一層。 */
export const RELIGIOUS_STUDIES_JOURNALS: PressTitle[] = [
  {
    slug: 'taiwan-religion',
    name: '臺灣宗教研究',
    side: '一般',
    publisher: '台灣宗教學會',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/taiwan-religion',
    note: '台灣宗教學會的會刊，本地宗教學制度化的主場。',
  },
  {
    slug: 'fujen-religious',
    name: '輔仁宗教研究',
    side: '一般',
    publisher: '輔仁大學宗教學系',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/fujen-religious',
    note: '台灣第一個宗教學系的學報，天主教背景而收跨宗教研究。',
  },
  {
    slug: 'new-century',
    name: '新世紀宗教研究',
    side: '一般',
    publisher: '世界宗教博物館發展基金會附設出版社',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/new-century',
    note: '靈鷲山系統辦的宗教學刊物，跨宗教對話的題目佔比高，第六章可用。',
  },
  {
    slug: 'religious-philosophy',
    name: '宗教哲學',
    side: '一般',
    publisher: '中華民國宗教哲學研究社',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/religious-philosophy',
    note: '出刊已逾百期，橫跨的年代長，適合看「宗教」一詞的用法怎麼變。',
  },
  {
    slug: 'chinese-religions',
    name: '華人宗教研究',
    side: '一般',
    publisher: '新文豐出版公司＆政治大學華人宗教研究中心',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/chinese-religions',
    note: '把台灣放回華人宗教場域來看的一份，民間信仰與新興宗教的題目多。',
  },
  {
    slug: 'folk-arts',
    name: '民俗曲藝',
    side: '一般',
    publisher: '財團法人施合鄭民俗文化基金會',
    // 創刊年查不到確切數字（華藝的刊物頁沒寫），照本檔規矩整個留空，不拿收錄起始冒充
    coverage: '華藝自 151 期（2006 年 3 月）起，至 232 期（2026 年 6 月），82 期 479 篇',
    tier: 'index',
    airiti: true,
    to: '/research-data/press/folk-arts',
    note: '一貫道、鸞堂與地方祭儀研究的主要園地；鍾雲鶯談國民政府查禁一貫道那篇在 231 期。'
      + '華藝把它歸在民俗類而非宗教學，所以學科分類的普查掃不到，是按刊名另外找出來的。',
  },
]

/**
 * 台灣五大報。戒嚴時期的三大報是中央日報、聯合報、中國時報（黨報＋兩大民營），
 * 解嚴後自由時報與蘋果日報加入而成五大報的格局。
 *
 * 🚨 全部只能做檢索指引。這些是商業資料庫，授權是「逐篇檢索閱讀」，
 *    不是「整批灌進自己的語料庫」。批次抓取違反授權條款，不做。
 */
export const GENERAL_PRESS: PressTitle[] = [
  {
    slug: 'udn',
    name: '聯合報',
    aka: ['經濟日報', '民生報', '聯合晚報', '星報'],
    side: '一般',
    start: '1951',
    publisher: '聯合報系',
    tier: 'guide',
    external: { label: '聯合知識庫', url: 'http://udndata.com/library/' },
    note: '聯合報系五報自創刊日起全數位化，逾 1,197 萬則。戒嚴時期三大報之一。'
      + '玄奘圖書館應有訂閱，校外連線可用。',
  },
  {
    slug: 'chinatimes',
    name: '中國時報',
    side: '一般',
    start: '1950',
    publisher: '中國時報社',
    tier: 'guide',
    external: { label: '台灣新聞智慧網', url: 'https://tnsw.infolinker.com.tw/' },
    note: '戒嚴時期三大報之一。2025-12 以前可查全文，之後僅標題摘要。',
  },
  {
    slug: 'cdn',
    name: '中央日報',
    side: '一般',
    start: '1928',
    end: '2006',
    publisher: '中國國民黨',
    tier: 'guide',
    external: { label: '中央日報全文影像資料庫', url: 'https://tbmc.ncl.edu.tw/' },
    note: '黨報，戒嚴時期三大報之一。要看官方立場如何論述宗教與教會，這份最直接。',
  },
  {
    slug: 'ltn',
    name: '自由時報',
    side: '一般',
    start: '1980',
    publisher: '自由時報企業',
    tier: 'guide',
    external: { label: '自由時報電子報', url: 'https://news.ltn.com.tw/' },
    note: '解嚴後崛起，本土派立場。網站有免費新聞庫，但早年（1980–1990 年代）不在線上。',
  },
  {
    slug: 'appledaily',
    name: '蘋果日報',
    side: '一般',
    start: '2003',
    end: '2021',
    publisher: '壹傳媒',
    tier: 'guide',
    external: { label: '台灣新聞智慧網', url: 'https://tnsw.infolinker.com.tw/' },
    note: '2021 年停刊，網站已關。社會議題（同婚、廢死）的報導量大，但取得管道最不穩定。',
  },
]

/**
 * 佛教期刊。四份合起來就是台灣佛教從民國佛教接續、到人間佛教成形的言論史，
 * 對應論文第三章太虛→印順→傳道→昭慧那條系譜。
 *
 * 取源尚在調查，先立目；`tier` 待各刊確認後再改。
 */
export const BUDDHIST_PRESS: PressTitle[] = [
  {
    slug: 'haichaoyin',
    name: '海潮音',
    side: '佛教',
    start: '1920-01',
    publisher: '太虛大師創辦；1950 年隨大醒法師遷台續刊',
    tier: 'index',
    note: '中國佛教史上發行最久的佛教刊物，太虛親自編第一卷。人間佛教這條線的'
      + '源頭文獻，第三章第一節（太虛）最需要的就是這份。優先級最高。',
  },
  {
    slug: 'rensheng',
    name: '人生雜誌',
    side: '佛教',
    start: '1949',
    publisher: '東初老人創辦於北投法藏寺；今法鼓文化發行',
    tier: 'index',
    note: '台灣第一份本土佛教期刊，戰後台灣佛教在地化的起點。',
  },
  {
    slug: 'putishu',
    name: '菩提樹',
    side: '佛教',
    start: '1952',
    end: '1989',
    publisher: '朱斐主編，台中',
    tier: 'index',
    note: '印順在台灣活動期的主要發表園地之一，第三章第二節（印順）的同時代刊物。',
  },
  {
    slug: 'shizihou',
    name: '獅子吼',
    side: '佛教',
    start: '1961',
    end: '1996',
    publisher: '中華佛教護僧協會',
    tier: 'index',
    note: '橫跨戒嚴到解嚴，護教與教團事務的言論記錄。',
  },
]

export const PRESS_GROUPS = [
  {
    key: 'christian',
    title: '基督教三大報',
    desc: '長老教會、福音派、靈恩／復興系統各一，是台灣新教的三條主線',
    items: CHRISTIAN_PRESS,
  },
  {
    key: 'christian-journals',
    title: '基督教期刊',
    desc: '教會青年刊物與神學院學報；篇目走華藝，卷期與頁碼才齊',
    items: CHRISTIAN_JOURNALS,
  },
  {
    key: 'buddhist',
    title: '佛教期刊',
    desc: '從民國佛教接續到人間佛教成形的言論史，對應太虛→印順→傳道→昭慧那條系譜',
    items: BUDDHIST_PRESS,
  },
  {
    key: 'buddhist-journals',
    title: '佛學學報',
    desc: '上面四份是教內言論刊物（史料），這一組是學報（研究）；兩邊不要混著讀',
    items: BUDDHIST_JOURNALS,
  },
  {
    key: 'religious-studies',
    title: '宗教學期刊',
    desc: '跨教的學術刊物，做「宗教」這個概念本身在台灣怎麼被說的那一層',
    items: RELIGIOUS_STUDIES_JOURNALS,
  },
  {
    key: 'general',
    title: '台灣五大報',
    desc: '戒嚴時期三大報（中央日報、聯合報、中國時報）加上解嚴後的自由時報與蘋果日報',
    items: GENERAL_PRESS,
  },
] as const
