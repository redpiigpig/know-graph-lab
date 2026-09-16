// 摩尼教經典 — 型別定義
//
// 與 data/avesta（祆教經典）為姊妹結構，共用三欄 reader 的資料形狀，
// 但**分藏原則相反**，動結構前務必讀完這一段：
//
//   祆教   ＝ 正典還活著。火廟今天仍照亞斯納 72 章誦唸，故照抄禮儀單位，不另立卷次。
//   摩尼教 ＝ 正典死透了。摩尼親撰的七部經**沒有一部傳世**，一個完整的教團也不存在，
//            傳世的每一頁都是從埋在沙裡的抄本、敵手的駁論、和不同語言的譯本裡撿回來的。
//
// 所以本藏經分兩層，這是本區唯一的體例決定：
//
//   **正藏按「書目」立卷** —— 摩尼自己定過一份正典書目（七經＋沙卜爾干＋圖經），
//     這份書目由《群書類述》《凱法萊亞》與吐魯番殘卷多方互證，是可靠的。
//     所以正藏的卷次照這份書目立，即使那些卷**幾乎都是空的**。
//     空著比不列好：不列等於接受「摩尼教沒有正典」這個由勝利者寫下的假象。
//
//   **續藏按「出土語言與地點」立卷** —— 科普特文（埃及）／東方伊朗語與回鶻文（吐魯番）／
//     漢文（敦煌、霞浦）。不按主題重編，因為摩尼教文獻的存世形態本來就是語言群，
//     一份《巨人書》在科普特、帕提亞語、回鶻文與漢文裡是四份不同程度的殘卷，
//     硬併成一條會抹掉「哪一群人在哪裡讀到什麼」這個最要緊的事實。互見靠 seealso。
//
// 🚨 第五藏（敵證與外部記述）scriptural = false。奧古斯丁、《阿基勞斯行傳》、
//    阿爾—納迪姆寫的**不是**摩尼教文獻，是反摩尼教文獻。收進來是因為在 1904 年
//    吐魯番探險隊挖出第一批殘卷之前，全世界對摩尼教的認識**百分之百**來自這一批;
//    而且七經裡好幾部的僅存內文就卡在這些駁論的引文裡。收但必須與前四藏在版面上分開，
//    每一條都要標使用限制（見 HostileLevel）。

/** 文本存世狀態 —— 摩尼教的殘缺程度比祆教更嚴重，狀態必須在版面上看得見 */
export type TextStatus =
  | 'whole' // 完整傳世（本藏經極少，漢文《下部讚》《儀略》屬之）
  | 'partial' // 大部傳世但有闕葉
  | 'fragment' // 僅存殘葉或綴輯
  | 'lost-cited' // 原書已佚，僅存於他書引文或章目
  | 'lost-listed' // 原書已佚且無引文傳世，僅知書名見於正典書目
  | 'hostile' // 僅存於反對者的駁論之中

export const STATUS_META: Record<TextStatus, { zh: string; desc: string; titleCls: string; dotCls: string; rowCls: string }> = {
  whole: {
    zh: '全本',
    desc: '完整傳世。本藏經只有漢文兩種與少數禮儀文書屬此。',
    titleCls: 'text-gray-900', dotCls: 'bg-emerald-500', rowCls: '',
  },
  partial: {
    zh: '闕本',
    desc: '大部傳世，但有整章或整葉闕失。',
    titleCls: 'text-lime-800', dotCls: 'bg-lime-500', rowCls: 'bg-lime-50/40',
  },
  fragment: {
    zh: '殘篇',
    desc: '僅存殘葉、單頁或後人綴輯。吐魯番所出的絕大多數屬此。',
    titleCls: 'text-amber-800', dotCls: 'bg-amber-400', rowCls: 'bg-amber-50/40',
  },
  'lost-cited': {
    zh: '佚存引文',
    desc: '原書已佚。今日所知來自他書的引文或章目——摩尼親撰七經多屬此級。',
    titleCls: 'text-orange-800', dotCls: 'bg-orange-500', rowCls: 'bg-orange-50/40',
  },
  'lost-listed': {
    zh: '佚存目',
    desc: '原書已佚且無一字引文傳世，僅知書名見於正典書目。',
    titleCls: 'text-rose-800', dotCls: 'bg-rose-500', rowCls: 'bg-rose-50/40',
  },
  hostile: {
    zh: '敵證',
    desc: '僅存於反對者的駁論中。引用前必須先讀該條的使用限制。',
    titleCls: 'text-red-800', dotCls: 'bg-red-500', rowCls: 'bg-red-50/40',
  },
}

/** 敵證的三級可信度 —— 摘自 [[hellenika-fragments]] 的作法，摩尼教這邊用得更兇。
 *
 *  這三級的差別不是學術潔癖，是會不會引錯話的差別：
 *  奧古斯丁逐句抄錄《基要書信》再駁，那些抄錄句可以當摩尼的原話用；
 *  但他轉述「摩尼教徒相信吃瓜果能解放光明分子」時，已經過了一層嘲諷。
 */
export type HostileLevel =
  | 'verbatim' // 逐句引錄後再駁；引文本身可當原話用
  | 'paraphrase' // 轉述教義，未宣稱逐字
  | 'framed' // 整段包在敵意框架裡（斥為淫邪、瘋狂、蠻族妖術）

export const HOSTILE_META: Record<HostileLevel, { zh: string; desc: string; cls: string }> = {
  verbatim: {
    zh: '逐句引錄',
    desc: '駁論者逐句抄錄原文再加反駁，引文本身可作原話使用。',
    cls: 'bg-emerald-100 text-emerald-800',
  },
  paraphrase: {
    zh: '轉述',
    desc: '轉述教義而未宣稱逐字，用語已經過駁論者的選擇。',
    cls: 'bg-amber-100 text-amber-800',
  },
  framed: {
    zh: '敵意框架',
    desc: '整段包在指控裡（淫祀、瘋狂、波斯妖術）。只能當「反對者如何理解」的證據。',
    cls: 'bg-red-100 text-red-800',
  },
}

/** 三欄對照的取得狀態 —— 本藏經最誠實的一欄：哪些欄目真的有東西。
 *  🚨 它說的是「線上找不找得到可用來源」，**不是**「本站有沒有」。 */
export type ColumnState =
  | 'ready' // 已取得並逐段對齊上架
  | 'available' // 線上有可用來源（公有領域或開放取用），尚未抓取
  | 'copyright' // 有現代校本／譯本但在版權內，不能用
  | 'none' // 查無可用來源

export const COLUMN_META: Record<ColumnState, { zh: string; cls: string }> = {
  ready: { zh: '已上架', cls: 'bg-emerald-100 text-emerald-800' },
  available: { zh: '可取得', cls: 'bg-sky-100 text-sky-800' },
  copyright: { zh: '版權內', cls: 'bg-amber-100 text-amber-800' },
  none: { zh: '無來源', cls: 'bg-gray-100 text-gray-500' },
}

/** 三欄各自的取源現況。
 *
 *  🚨 漢文藏的特例：那一藏的「原文」就是中文，orig 與 zh 指同一份東西。
 *     版面上只出一欄，不可為了湊三欄而把漢文再「翻譯」成中文。
 *     這條規矩與 /research-data/sanyijiao 的 columnsFor() 同源（user 2026-09-06 定）。
 */
export interface ColumnStatus {
  /** 原文轉寫（科普特文／中古波斯語／帕提亞語／粟特語／回鶻語／漢文） */
  orig: ColumnState
  /** 英譯 */
  en: ColumnState
  /** 繁體中文（本站自譯為主；漢文藏不適用，見上） */
  zh: ColumnState
}

/** 單一篇章（＝三欄 reader 的一頁） */
export interface ManiText {
  /** 路由 slug，如 'living-gospel'、'kephalaia-001'、'xiabuzan' */
  slug: string
  /** 漢語定名（先過 /translation-glossary） */
  title_zh: string
  /** 原文題名轉寫，如 'Evangelion'、'Šābuhragān'、'下部讚' */
  title_orig?: string
  /** 學界通用英文題名 */
  title_en?: string
  /** 學術編號。摩尼教殘卷的編號就是它的身分證：
   *  柏林吐魯番藏品 M 470、科普特抄本 1 Ke 38、敦煌 S.2659、大正藏 T2140 */
  siglum: string
  /** 作者／傳統歸屬 */
  author?: string
  /** 成書／抄寫年代 */
  era?: string
  /** 語言 */
  language?: string
  /** 出土地／館藏地 —— 本藏經的第一屬性。同一部書在四個地方各存一塊殘片。 */
  provenance?: string
  /** 篇幅，如「存 122 章中之 76 章」 */
  extent?: string
  /** 一句簡述（顯示於標題下） */
  note?: string
  /** 100–200 字簡介（顯示於詳情） */
  intro?: string
  /** 存世狀態；不設＝殘篇（本藏經的常態不是全本） */
  status?: TextStatus
  /** 敵證等級。status === 'hostile' 時必填，測試會釘住。 */
  hostile?: HostileLevel
  /** 三欄取源現況；不設＝沿用所屬 division 的預設 */
  columns?: ColumnStatus
  /** 佚書／殘篇的轉引來源，如「《群書類述》摩尼教章」「奧古斯丁《駁基要書信》5」。
   *  status 為 lost-cited／lost-listed／hostile 時必填，測試會釘住。 */
  via?: string
  /** 同一部書在別藏的另一份殘卷，填對方 slug。摩尼教的互見不是「參看」，
   *  而是「這是同一本書的另一塊碎片」。 */
  seealso?: string[]
}

/** 卷內的「部」（子分類） */
export interface ManiDivision {
  key: string
  label: string
  label_en?: string
  desc?: string
  /** 本部各篇的預設三欄現況（個別篇可覆寫） */
  columns?: ColumnStatus
  texts: ManiText[]
}

/** 一卷 */
export interface ManiVolume {
  key: string
  /** 卷次符號，版面上的方塊字 */
  sigil: string
  name: string
  name_orig?: string
  name_en: string
  /** 出土地與館藏。摩尼教文獻的第一屬性是「從哪裡挖出來的」。 */
  provenance?: string
  era?: string
  /** 規模，如「存 122 章中之 76 章」 */
  extent?: string
  summary: string
  divisions: ManiDivision[]
}

/** 卷群（部）——把卷分組，供索引頁瀏覽 */
export interface ManiPart {
  key: string
  label: string
  label_en?: string
  desc?: string
  volumes: string[]
}

/** 一藏 */
export interface ManiCanon {
  key: string
  name: string
  name_en: string
  glyph: string
  subtitle: string
  summary: string
  /** 是否為摩尼教自身的宗教文獻。
   *  🚨 前四藏 true，第五藏（敵證與外部記述）false——那一藏是反摩尼教文獻。 */
  scriptural: boolean
  language: string
  era: string
  parts: ManiPart[]
  volumes: ManiVolume[]
}

export function volumeTextCount(v: ManiVolume): number {
  return v.divisions.reduce((n, d) => n + d.texts.length, 0)
}

export function canonTextCount(c: ManiCanon): number {
  return c.volumes.reduce((n, v) => n + volumeTextCount(v), 0)
}

/** 篇章的實際三欄現況：自身設定優先，否則沿用所屬 division 的預設 */
export function columnsOf(text: ManiText, division: ManiDivision): ColumnStatus {
  return text.columns ?? division.columns ?? { orig: 'none', en: 'none', zh: 'none' }
}

/** 建 division 用的小工具：把 [編號, 中文名, 註] 的緊湊表展開成 ManiText[]。
 *  《凱法萊亞》122 章、《下部讚》30 首這類規則序列用它。 */
export function series(
  opts: {
    slug: string
    siglum: string
    orig?: string
    language: string
    era?: string
    provenance?: string
    status?: TextStatus
  },
  rows: Array<[n: number, title: string, note?: string]>,
): ManiText[] {
  return rows.map(([n, title, note]) => ({
    slug: `${opts.slug}-${String(n).padStart(3, '0')}`,
    title_zh: title,
    title_orig: opts.orig ? `${opts.orig} ${n}` : undefined,
    siglum: `${opts.siglum} ${n}`,
    language: opts.language,
    era: opts.era,
    provenance: opts.provenance,
    status: opts.status,
    note,
  }))
}
