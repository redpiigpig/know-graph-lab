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
  /** 一句簡述（短，顯示於標題下） */
  note?: string
  /** 100–200 字簡介（顯示於右欄） */
  intro?: string
  /** 站內對照工具連結（該作品可在此閱讀） */
  link?: string
  /** 正典層級（僅經藏正藏塗色用；正典不設則不塗色） */
  tier?: CanonTier
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

export const CANON_LABEL: Record<CanonKey, { zh: string; en: string; desc: string }> = {
  zheng: { zh: '正藏', en: 'Canonical', desc: '尼西亞教會（大公傳統）接受的文獻' },
  wai: { zh: '外藏', en: 'Extra-Canonical', desc: '分類與正藏對照、但不被尼西亞教會接受（偽典／異端／猶太教／外教見證）' },
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
