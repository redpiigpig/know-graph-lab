// 希臘羅馬大藏經 — 已取得原文並逐段對齊的銘文／紙草。
//
// 來源檔由 scripts/hellenika_cgrn.py 抓取、scripts/hellenika_align.py 對齊並翻譯。
// 對齊鍵是**石面行號**：CGRN 的希臘原文與英譯都帶行號標記，因此三欄天然對得上，
// 不必按語意重排（見 hellenika-epigraphy skill §4）。

export interface AlignedSegment {
  /** 面／欄，如「Face A」 */
  face: string
  /** 本段起始的石面行號；0 表示需人工對齊 */
  line_from: number
  /** 希臘原文，保留 Leiden 補字符號 */
  greek: string
  /** 英譯（CGRN） */
  en: string
  /** 繁體中文（本站逐段翻） */
  zh: string
  note?: string
}

export interface AlignedText {
  cgrn: number
  url: string
  title_zh: string
  title_en: string
  /** 所屬卷次 key，如 'K' */
  volume: string
  date: string
  provenance: string
  support: string
  bibliography: string
  licence: string
  /** 本篇專名定譯表，逐篇先定名再逐批沿用 */
  names: Record<string, string>
  segments: AlignedSegment[]
}

const modules = import.meta.glob('./cgrn/*.aligned.json', { eager: true }) as
  Record<string, { default: AlignedText }>

export const ALIGNED_TEXTS: AlignedText[] = Object.values(modules)
  .map(m => m.default)
  .sort((a, b) => a.cgrn - b.cgrn)

export function alignedSlug(t: AlignedText): string {
  return `cgrn-${t.cgrn}`
}

export function findAligned(slug: string): AlignedText | undefined {
  return ALIGNED_TEXTS.find(t => alignedSlug(t) === slug)
}

/** 某一卷底下已有原文對照的篇目 */
export function alignedInVolume(volumeKey: string): AlignedText[] {
  return ALIGNED_TEXTS.filter(t => t.volume === volumeKey)
}
