// 基督教大藏經 — 型別定義
// 仿佛教《大藏經》的「經律論」彙編體例，為古代→中世紀→近代→現代基督教文獻
// 建立一套漢語藏經分類矩陣。資料為策展式書目骨架（仿 /creeds file-based），
// 多數書目跨連到站內既有工具（/scripture /fathers /apocrypha /gnostic /creeds
// /canon-law /encyclicals）。

/** 單一作品（書目條目） */
export interface DazangWork {
  /** 漢語定名（依藏經體裁正名，如《三位一體論》《駁異端論》） */
  title_zh: string
  /** 原文／西方通用名（拉丁／希臘／英文） */
  title_orig?: string
  /** 作者／教父／來源社群 */
  author?: string
  /** 年代（世紀或年份） */
  era?: string
  /** 一句簡述 */
  note?: string
  /** 站內對照工具連結（該作品可在此閱讀） */
  link?: string
}

/** 藏內的「部」（子分類） */
export interface DazangDivision {
  key: string
  /** 部名，如「護教詞部」 */
  label: string
  label_en?: string
  /** 部的說明 */
  desc?: string
  works: DazangWork[]
}

/** 一藏（如 經藏 / 律藏 / 論藏…） */
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
  /** 站內主要對照工具（此藏文獻多可在此瀏覽） */
  portal?: { to: string; label: string }
  divisions: DazangDivision[]
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
