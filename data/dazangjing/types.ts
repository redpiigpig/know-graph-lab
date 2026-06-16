// 基督教大藏經 — 型別定義
// 仿佛教《大藏經》的「經律論」彙編體例，為古代→中世紀→近代→現代基督教文獻
// 建立一套漢語藏經分類矩陣。
//
// 每一藏都分「正藏」與「外藏」兩套平行目錄：
//   正藏 = 尼西亞教會（大公傳統）接受的文獻。
//   外藏 = 目錄分類與正藏對照、但不被尼西亞教會接受者
//          （偽典／異端／猶太教／外教見證等「影子」文獻）。
// 兩者用相同的「部」分類對照；某些部僅外藏才有（如經藏的「史傳」「遺訓」）。

/**
 * 正典層級（僅經藏正藏使用，用於塗色）。
 *   undefined = 正典（新教 66 卷），不塗色
 *   'lxx'       = 七十士譯本次經（天主教／東正教第二正典）
 *   'eastern'   = 亞美尼亞／衣索比亞等東方教會次經
 *   'patristic' = 因重要古抄本收錄與教父推薦而入選者
 */
export type CanonTier = 'lxx' | 'eastern' | 'patristic'

export const TIER_LABEL: Record<CanonTier, { zh: string; titleCls: string; dotCls: string; rowCls: string }> = {
  lxx: { zh: '七十士譯本次經', titleCls: 'text-amber-800', dotCls: 'bg-amber-400', rowCls: 'bg-amber-50/50' },
  eastern: { zh: '亞美尼亞／衣索比亞次經', titleCls: 'text-violet-800', dotCls: 'bg-violet-400', rowCls: 'bg-violet-50/50' },
  patristic: { zh: '古抄本／教父推薦入選', titleCls: 'text-sky-800', dotCls: 'bg-sky-500', rowCls: 'bg-sky-50/50' },
}

/** 外藏文獻來源（按傳統塗色） */
export const SOURCE_META: Record<string, { zh: string; titleCls: string; dotCls: string }> = {
  'second-temple':     { zh: '第二聖殿猶太（偽典）', titleCls: 'text-lime-700',    dotCls: 'bg-lime-500' },
  'qumran':            { zh: '死海古卷',           titleCls: 'text-teal-700',    dotCls: 'bg-teal-500' },
  'rabbinic':          { zh: '拉比猶太',           titleCls: 'text-emerald-700', dotCls: 'bg-emerald-500' },
  'jewish-christian':  { zh: '猶太基督派',         titleCls: 'text-amber-700',   dotCls: 'bg-amber-500' },
  'gnostic':           { zh: '諾斯底主義',         titleCls: 'text-rose-700',    dotCls: 'bg-rose-500' },
  'marcionite':        { zh: '馬吉安派',           titleCls: 'text-fuchsia-700', dotCls: 'bg-fuchsia-500' },
  'manichaean':        { zh: '摩尼教',             titleCls: 'text-orange-700',  dotCls: 'bg-orange-500' },
  'mandaean':          { zh: '曼達教',             titleCls: 'text-cyan-700',    dotCls: 'bg-cyan-500' },
  'heresy':            { zh: '基督教異端教派',     titleCls: 'text-red-700',     dotCls: 'bg-red-500' },
  'pagan':             { zh: '外教與希臘化',       titleCls: 'text-violet-700',  dotCls: 'bg-violet-500' },
  'orthodox-apocrypha':{ zh: '大公旁支偽典',       titleCls: 'text-sky-700',     dotCls: 'bg-sky-500' },
}
export const SOURCE_ORDER = ['second-temple','qumran','rabbinic','jewish-christian','gnostic','marcionite','manichaean','mandaean','heresy','pagan','orthodox-apocrypha']

/** 單一作品（書目條目） */
export interface DazangWork {
  /** 漢語定名 */
  title_zh: string
  /** 原文／西方通用名 */
  title_orig?: string
  /** 作者／教父／來源社群 */
  author?: string
  /** 大約寫作日期（世紀或年份） */
  era?: string
  /** 寫作地點 */
  place?: string
  /** 寫作語言 */
  language?: string
  /** 該作品「自身」的內容規模（非在藏中的排序卷號），如「全 18 卷」「63 篇」「四部」「約 2 萬字」 */
  extent?: string
  /** 一句簡述（短，顯示於標題下） */
  note?: string
  /** 100–200 字簡介（顯示於右欄） */
  intro?: string
  /** 站內對照工具連結（該作品可在此閱讀） */
  link?: string
  /** 正典層級（僅經藏正藏塗色用；正典不設則不塗色） */
  tier?: CanonTier
  /** 文獻來源／傳統（外藏塗色用；對應 SOURCE_META 的 key） */
  source?: string
}

/** 藏內的「部」（子分類） */
export interface DazangDivision {
  key: string
  /** 部名，如「律法書」「護教詞部」 */
  label: string
  label_en?: string
  /** 部的說明 */
  desc?: string
  works: DazangWork[]
}

/** 一套目錄（正藏 或 外藏） */
export interface DazangCanon {
  /** 此目錄的說明 */
  summary?: string
  divisions: DazangDivision[]
}

/** 一藏（如 經藏 / 律藏 / 論藏…），含正藏與外藏兩套平行目錄 */
export interface DazangCollection {
  key: string
  /** 藏名，如「經藏」 */
  name: string
  name_en: string
  /** 單字徽記，如「經」 */
  glyph: string
  /** 體裁矩陣（漢語定名法則），如「論‧辯‧駁‧註‧疏‧釋」 */
  genres?: string
  /** 該藏的定位說明 */
  summary: string
  /** 站內主要對照工具 */
  portal?: { to: string; label: string }
  /**
   * 單一目錄標籤。設定後此藏不分正藏／外藏，只有一套以此名稱呈現的目錄
   * （內容放 zheng 槽）。用於前基督教大藏經——基督教之前無正／外之分，只有「前藏」。
   */
  soleCanonLabel?: string
  /** 正藏（尼西亞教會接受） */
  zheng: DazangCanon
  /** 外藏（對照分類，不被尼西亞教會接受） */
  wai: DazangCanon
}

export type CanonKey = 'zheng' | 'wai'

// 三軌定義（user 2026-06-16 神學重構，奠基於「隱密的上帝」與「社會學邊界」）：
//   正藏不代表啟示壟斷或絕對無誤，僅是群體為維繫認同所劃下的「教會論邊界之內」的家族記憶；
//   外藏無貶義，僅標示「社會學邊界之外」——隱密的上帝按其自由所開展的平行啟示與神聖見證。
export const CANON_LABEL: Record<CanonKey, { zh: string; en: string; desc: string }> = {
  zheng: { zh: '正藏', en: 'Within the Boundary', desc: '基督教群體為維繫自身認同所劃下的「教會論與社會學邊界」之內的歷史紀錄——群體的家族記憶與自我建構，並非啟示的壟斷或絕對無誤。' },
  wai: { zh: '外藏', en: 'Beyond the Boundary', desc: '隱密的上帝在群體邊界之外、按其絕對自由所開展的平行啟示與神聖見證；「外」僅標示社會學邊界之外，並無貶義。' },
}

/** 一個時代（古代／中世紀／近代／現代） */
export interface DazangEra {
  key: string
  /** 如「古代基督教大藏經」 */
  name: string
  name_en: string
  glyph: string
  subtitle: string
  /** 年代結界說明 */
  boundary?: string
  enabled: boolean
  collections: DazangCollection[]
}

/** 計算一套目錄的卷數 */
export function canonWorkCount(c: DazangCanon): number {
  return c.divisions.reduce((n, d) => n + d.works.length, 0)
}
