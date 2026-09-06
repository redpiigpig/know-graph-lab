// 祆教經典 — 型別定義
//
// 與《希臘羅馬大藏經》（data/hellenika）為姊妹結構，但體例刻意不同：
//
//   希臘羅馬大藏經 ＝ 替一個從未有過正典的宗教「外加」一部正典（Α–Ω 廿四卷是編者所立）
//   祆教經典       ＝ 祆教**自己有**祭典分部，本站照抄不另立卷次（user 定，2026-09-06）
//
// 這個差別是根本的，動結構前務必回讀：希臘那邊分卷是編者的判斷，可以辯論；
// 這邊「亞斯納 72 章／維斯帕拉德 24 章／萬迪達德 22 章」是薩珊祭司傳下來的
// 禮儀單位，帕西祭司今天仍照這個數目誦唸。**擅自重編＝把活的禮儀改成書架分類。**
//
// 四藏：
//   avestan   阿維斯陀（正藏）— 阿維斯陀語，公元前二千紀末至薩珊；傳世僅約原本四分之一
//   pahlavi   巴列維文獻（續典）— 中古波斯語，9–10 世紀伊斯蘭征服後的經典化著述
//   later     後期文獻（外典）— 波斯語／古吉拉特語，帕西社群的晚期宗教書與族群史
//   epigraphy 銘文附錄 — 阿契美尼德古波斯語與薩珊中古波斯語王室／祭司銘文
//
// 🚨 銘文附錄不是經典。阿契美尼德王室銘文是否算祆教文獻，學界至今無定論
//    （大流士拜阿胡拉‧馬茲達，但銘文裡沒有查拉圖斯特拉、沒有伽薩用語）。
//    收進來是因為它是同一信仰世界最早的**有年代可考**的文字證據，
//    但 canon.scriptural = false，版面上必須與前三藏區分。

/** 文本存世狀態 —— 祆教的殘缺程度比希臘更嚴重，狀態必須在版面上看得見 */
export type TextStatus =
  | 'whole' // 完整傳世（禮儀中仍在使用者多屬此類）
  | 'partial' // 大部傳世但有闕章
  | 'fragment' // 僅存殘篇、引文或單葉
  | 'lost-summary' // 原書已佚，僅存於《丹卡爾德》等書的內容撮要
  | 'inscription' // 石刻／金石，非書籍傳抄

export const STATUS_META: Record<TextStatus, { zh: string; desc: string; titleCls: string; dotCls: string; rowCls: string }> = {
  whole: {
    zh: '全本',
    desc: '完整傳世。',
    titleCls: 'text-gray-900', dotCls: 'bg-emerald-500', rowCls: '',
  },
  partial: {
    zh: '闕本',
    desc: '大部傳世，但有整章或整卷闕失。',
    titleCls: 'text-lime-800', dotCls: 'bg-lime-500', rowCls: 'bg-lime-50/40',
  },
  fragment: {
    zh: '殘篇',
    desc: '僅存引文、單葉或後人綴輯。',
    titleCls: 'text-amber-800', dotCls: 'bg-amber-400', rowCls: 'bg-amber-50/40',
  },
  'lost-summary': {
    zh: '佚存目',
    desc: '原書已佚。今日所知全部來自《丹卡爾德》第八、九卷的逐部撮要——那兩卷等於失傳正典的目錄。',
    titleCls: 'text-rose-800', dotCls: 'bg-rose-500', rowCls: 'bg-rose-50/40',
  },
  inscription: {
    zh: '銘文',
    desc: '出自岩壁、石柱或印章的現場刻文，非書籍傳抄。',
    titleCls: 'text-sky-800', dotCls: 'bg-sky-500', rowCls: 'bg-sky-50/40',
  },
}

/** 三欄對照的取得狀態 —— 這部藏經最誠實的一欄：哪些欄目真的有東西 */
export type ColumnState =
  | 'ready' // 已取得並逐段對齊上架
  | 'available' // 線上有可用來源，尚未抓取
  | 'copyright' // 有現代譯本但在版權內，不能用
  | 'none' // 查無可用來源

export const COLUMN_META: Record<ColumnState, { zh: string; cls: string }> = {
  ready: { zh: '已上架', cls: 'bg-emerald-100 text-emerald-800' },
  available: { zh: '可取得', cls: 'bg-sky-100 text-sky-800' },
  copyright: { zh: '版權內', cls: 'bg-amber-100 text-amber-800' },
  none: { zh: '無來源', cls: 'bg-gray-100 text-gray-500' },
}

/** 三欄各自的取源現況。中文欄幾乎全是 'none'——祆教經典的中譯是華語世界最大的空白之一 */
export interface ColumnStatus {
  /** 原文（阿維斯陀語／中古波斯語／古波斯語）轉寫 */
  orig: ColumnState
  /** 英譯（以公有領域的 SBE 為主） */
  en: ColumnState
  /** 繁體中文（本站自譯為主） */
  zh: ColumnState
}

/** 單一篇章（＝三欄 reader 的一頁） */
export interface ZoroText {
  /** 路由 slug，如 'yasna-28'、'bundahishn-01' */
  slug: string
  /** 漢語定名（先過 /translation-glossary） */
  title_zh: string
  /** 原文題名轉寫，如 'Yasna 28'、'Bundahišn' */
  title_orig?: string
  /** 學界通用英文題名 */
  title_en?: string
  /** 禮儀／學術編號，如 'Y 28'、'Vd 3'、'Yt 10'、'Dk 3' */
  siglum: string
  /** 作者／傳統歸屬；絕大多數為佚名或託名 */
  author?: string
  /** 成書／定型年代 */
  era?: string
  /** 語言 */
  language?: string
  /** 篇幅，如「全 22 節」「約 145 節」 */
  extent?: string
  /** 一句簡述（顯示於標題下） */
  note?: string
  /** 100–200 字簡介（顯示於詳情） */
  intro?: string
  /** 存世狀態；不設＝全本 */
  status?: TextStatus
  /** 三欄取源現況；不設＝沿用所屬 division 的預設 */
  columns?: ColumnStatus
  /** 殘篇／佚書的轉引來源，如「《丹卡爾德》8.44」 */
  via?: string
  /** 與另一藏／另一篇互見 */
  seealso?: string
}

/** 卷內的「部」（子分類），如亞斯納卷內的「伽薩」 */
export interface ZoroDivision {
  key: string
  label: string
  label_en?: string
  desc?: string
  /** 本部各篇的預設三欄現況（個別篇可覆寫） */
  columns?: ColumnStatus
  texts: ZoroText[]
}

/** 一卷（＝一部祭典書或一組同類文獻） */
export interface ZoroVolume {
  key: string
  /** 卷次符號，版面上的方塊字，如「耶」「祓」「丹」 */
  sigil: string
  name: string
  name_orig?: string
  name_en: string
  /** 禮儀用途；祆教經典的第一屬性是「在什麼場合誦唸」，不是「講什麼」 */
  liturgy?: string
  era?: string
  /** 規模，如「72 章」 */
  extent?: string
  summary: string
  divisions: ZoroDivision[]
}

/** 卷群（部）——把卷分組，供索引頁瀏覽 */
export interface ZoroPart {
  key: string
  label: string
  label_en?: string
  desc?: string
  /** 本部所轄卷次 key */
  volumes: string[]
}

/** 一藏 */
export interface ZoroCanon {
  key: string
  name: string
  name_en: string
  glyph: string
  subtitle: string
  /** 該藏的定位與收錄準則 */
  summary: string
  /** 是否為本教的宗教文獻。
   *  🚨 這一欄問的**不是**「是不是正典」——後期文獻列為外典但仍是祆教徒寫給
   *  祆教徒的宗教書，故為 true；只有王室銘文為 false，因為它連是不是祆教的
   *  都沒有定論（見 epigraphy.ts 檔首）。正典位階由各藏的 subtitle 表述。 */
  scriptural: boolean
  language: string
  era: string
  parts: ZoroPart[]
  volumes: ZoroVolume[]
}

export function volumeTextCount(v: ZoroVolume): number {
  return v.divisions.reduce((n, d) => n + d.texts.length, 0)
}

export function canonTextCount(c: ZoroCanon): number {
  return c.volumes.reduce((n, v) => n + volumeTextCount(v), 0)
}

/** 篇章的實際三欄現況：自身設定優先，否則沿用所屬 division 的預設 */
export function columnsOf(text: ZoroText, division: ZoroDivision): ColumnStatus {
  return text.columns ?? division.columns ?? { orig: 'none', en: 'none', zh: 'none' }
}

/** 建 division 用的小工具：把 [siglum 尾碼, 中文名, 註] 的緊湊表展開成 ZoroText[]。
 *  亞斯納 72 章、萬迪達德 22 章這類規則序列用它，避免手打 72 個物件字面量出錯。 */
export function series(
  opts: {
    /** slug 前綴，如 'yasna' → yasna-01 */
    slug: string
    /** siglum 前綴，如 'Y' → 'Y 1' */
    siglum: string
    /** 原文題名前綴，如 'Yasna' → 'Yasna 1' */
    orig?: string
    language: string
    era?: string
    status?: TextStatus
  },
  rows: Array<[n: number, title: string, note?: string]>,
): ZoroText[] {
  return rows.map(([n, title, note]) => ({
    slug: `${opts.slug}-${String(n).padStart(2, '0')}`,
    title_zh: title,
    title_orig: opts.orig ? `${opts.orig} ${n}` : undefined,
    siglum: `${opts.siglum} ${n}`,
    language: opts.language,
    era: opts.era,
    status: opts.status,
    note,
  }))
}
