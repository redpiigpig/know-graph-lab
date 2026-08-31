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
  /** 創刊—停刊；仍發行者留空 end */
  start: string
  end?: string
  publisher: string
  tier: PressTier
  /** 站內收錄量，給卡片顯示；guide 級留空 */
  holdings?: string
  /** 站內對應子頁（刊物本位 → 教派本位的互指） */
  to?: string
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
    key: 'buddhist',
    title: '佛教期刊',
    desc: '從民國佛教接續到人間佛教成形的言論史，對應太虛→印順→傳道→昭慧那條系譜',
    items: BUDDHIST_PRESS,
  },
  {
    key: 'general',
    title: '台灣五大報',
    desc: '戒嚴時期三大報（中央日報、聯合報、中國時報）加上解嚴後的自由時報與蘋果日報',
    items: GENERAL_PRESS,
  },
] as const
