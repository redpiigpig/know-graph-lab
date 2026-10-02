// 古近東大藏經 — 型別定義
//
// 與 /hellenika（希臘羅馬）、/avesta（祆教）、/manichaean（摩尼教）並列於 /scripture-canon 宗教層。
// 體例刻意與三者都不同，動結構前先讀完這一段與 pages/near-east/about.vue 的凡例。
//
// ══════════ 一、這不是一個宗教，是七八個 ══════════
//
//   希臘羅馬大藏經替**一個**沒有正典的宗教補做正典；本藏經面對的是**一群**宗教——
//   埃及、蘇美、巴比倫與亞述、赫梯與胡里特、烏加里特、迦南與亞蘭、阿拉伯、埃蘭與高地。
//   它們彼此借神、借文類、借書吏學校，但各有自己的神廟體系與神譜，
//   **不調和、不比附、不編一套「近東神話」綜合版**。
//
//   所以分藏的單位是「文明」，判準是**文字與神廟體系**：
//     · 第一判準看寫經的語言與文字（古近東宗教的載體就是書吏與神廟，文字死，宗教就死）
//     · 最終判準看內容屬哪一套神廟體系——胡里特語的庫瑪比組詩出土於哈圖沙，歸赫梯與胡里特藏；
//       阿卡德語寫的烏加里特神表仍歸烏加里特藏。例外逐條寫在 about.vue。
//
// ══════════ 二、每一藏止於它的文字死亡 ══════════
//
//   古代宗教沒有「改宗的那一天」，只有最後一個會寫神名的書吏死去的那一天。
//   所以各藏的下限不是編者定的，而是那套文字最後一次被用來寫神的年代
//   （楔形文字最後一塊天文泥板約公元 75 年；菲萊島最後一則世俗體塗鴉 452 年）。
//
// ══════════ 三、泥板不是書 ══════════
//
//   「吉伽美什史詩」不是一部古人手上拿得到的書，是現代學者從兩千年間幾百塊泥板綴合出來的學術物件。
//   所以存世狀態多一級 `composite`（綴合本），並分兩個年代：`era`＝成書，`copies`＝現存抄本。
//   蘇美文學多半成書於烏爾第三王朝、抄本卻全是古巴比倫時代的學校習作——兩個年代差兩三百年，
//   混成一個會讓人以為我們讀的是原件。

/** 存世狀態 */
export type TextStatus =
  | 'whole' // 單一抄本大體完整（阿尼紙草、沙巴卡石）
  | 'composite' // 由多份抄本綴合成今日的讀本，仍有缺文（吉伽美什、埃努瑪‧埃利什）
  | 'fragment' // 僅存殘片，大段闕失
  | 'inscription' // 原地石刻、碑銘、牆面銘文（金字塔文、米沙碑）
  | 'lost-cited' // 原書已佚，僅存於他書引文或摘要（貝羅索斯）
  | 'lost-listed' // 原書已佚且無引文，只知其名見於書目（托特四十二書、尼普爾書目中未出土之篇）

export const STATUS_META: Record<TextStatus, { zh: string; desc: string; titleCls: string; dotCls: string; rowCls: string }> = {
  whole: {
    zh: '全本',
    desc: '單一抄本大體完整傳世。',
    titleCls: 'text-gray-900', dotCls: 'bg-emerald-500', rowCls: '',
  },
  composite: {
    zh: '綴合本',
    desc: '今日讀本由多份抄本、跨數百年的泥板綴合而成，仍有缺文。古近東大型文學作品的常態。',
    titleCls: 'text-teal-900', dotCls: 'bg-teal-500', rowCls: 'bg-teal-50/30',
  },
  fragment: {
    zh: '殘篇',
    desc: '僅存殘片，大段闕失。',
    titleCls: 'text-amber-800', dotCls: 'bg-amber-400', rowCls: 'bg-amber-50/40',
  },
  inscription: {
    zh: '銘文',
    desc: '刻在石碑、牆面、棺槨或金屬上的原地文本，不經抄寫傳承。',
    titleCls: 'text-sky-900', dotCls: 'bg-sky-500', rowCls: 'bg-sky-50/30',
  },
  'lost-cited': {
    zh: '佚存引文',
    desc: '原書已佚，今日所知來自他書的引錄或摘要。',
    titleCls: 'text-orange-800', dotCls: 'bg-orange-500', rowCls: 'bg-orange-50/40',
  },
  'lost-listed': {
    zh: '佚存目',
    desc: '原書已佚且無引文傳世，只知其名見於古代書目。',
    titleCls: 'text-rose-800', dotCls: 'bg-rose-500', rowCls: 'bg-rose-50/40',
  },
}

/** 三欄對照的取源狀態。🚨 說的是「線上找不找得到可用來源」，不是「本站已經有了」。 */
export type ColumnState = 'ready' | 'available' | 'copyright' | 'none'

export const COLUMN_META: Record<ColumnState, { zh: string; cls: string }> = {
  ready: { zh: '已上架', cls: 'bg-emerald-100 text-emerald-800' },
  available: { zh: '可取得', cls: 'bg-sky-100 text-sky-800' },
  copyright: { zh: '版權內', cls: 'bg-amber-100 text-amber-800' },
  none: { zh: '無來源', cls: 'bg-gray-100 text-gray-500' },
}

export interface ColumnStatus {
  /** 原文轉寫（埃及文／蘇美語／阿卡德語／赫梯語／烏加里特語…） */
  orig: ColumnState
  /** 英譯 */
  en: ColumnState
  /** 繁體中文（本站自譯） */
  zh: ColumnState
}

export interface NeText {
  /** 全藏唯一，路由用 */
  slug: string
  title_zh: string
  /** 原文題名或學界通用名（轉寫） */
  title_orig?: string
  /** 學界標準編號：ETCSL 1.1.1、CTH 344、KTU 1.2、KAI 181、BM EA 10470、SAA 9 1……
   *  🚨 只填查得到的標準編號，查不到就留空。自編號碼會讓這一條無法被外部引用，而版面看起來完全正常。 */
  siglum?: string
  author?: string
  /** 成書年代 */
  era?: string
  /** 現存抄本年代（與成書年代不同時才填）。蘇美文學的常態是兩者相差兩三百年。 */
  copies?: string
  language?: string
  /** 出土地／館藏地 */
  provenance?: string
  /** 篇幅 */
  extent?: string
  /** 一句簡述，顯示於標題下 */
  note?: string
  /** 100–200 字簡介（後補） */
  intro?: string
  /** 不設＝綴合本 */
  status?: TextStatus
  columns?: ColumnStatus
  /** 佚書的轉引來源。status 為 lost-cited／lost-listed 時必填，測試釘住。 */
  via?: string
  /** 希伯來聖經對位，如「箴 22:17–24:22」。
   *  🚨 只是互見，**不是**排序或收錄的理由：本藏經不把這些文本當「聖經的背景」。 */
  bible?: string
  /** 本藏經內的互見，填對方 slug */
  seealso?: string[]
  /** 站上其他典藏的互見（希臘羅馬大藏經、基督教大藏經前藏、祆教經典…），純文字 */
  xref?: string[]
}

export interface NeDivision {
  key: string
  label: string
  label_en?: string
  desc?: string
  /** 本部各篇預設三欄現況 */
  columns?: ColumnStatus
  texts: NeText[]
}

export interface NeVolume {
  key: string
  /** 卷次符號，如「埃一」 */
  sigil: string
  name: string
  name_en: string
  era?: string
  summary: string
  divisions: NeDivision[]
}

export interface NeCanon {
  key: string
  name: string
  name_en: string
  /** 版面上的方塊字 */
  glyph: string
  subtitle: string
  summary: string
  /** 是否為該文明自身的宗教文獻。附錄（希臘羅馬人的轉述）為 false。 */
  scriptural: boolean
  language: string
  /** 起訖。下限＝該文字最後一次被用來寫神的年代，見檔頭第二條。 */
  era: string
  /** 下限的依據，一句話 */
  terminus: string
  /** 本藏預設三欄現況 */
  columns: ColumnStatus
  volumes: NeVolume[]
}

export function volumeTextCount(v: NeVolume): number {
  return v.divisions.reduce((n, d) => n + d.texts.length, 0)
}

export function canonTextCount(c: NeCanon): number {
  return c.volumes.reduce((n, v) => n + volumeTextCount(v), 0)
}

export function columnsOf(text: NeText, division: NeDivision, canon: NeCanon): ColumnStatus {
  return text.columns ?? division.columns ?? canon.columns
}
