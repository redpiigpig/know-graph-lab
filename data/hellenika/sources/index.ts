// 希臘羅馬大藏經 — 已取得原文並逐段對齊的銘文／紙草。
//
// 兩種來源，切段單位不同、對照欄數也不同：
//
//   CGRN（祭儀規範）— scripts/hellenika_cgrn.py + hellenika_align.py
//     希臘原文與英譯**都帶石面行號**，故以行號對齊，三欄（希／英／中）。
//
//   PHI（其餘各類銘文）— scripts/hellenika_phi.py + hellenika_iamata.py
//     以文本自身的**案例編號**切段（治癒銘文本身即逐案編號，也是學界引用單位）。
//     🚨 無第三方英譯可依據者只有兩欄（希／中），且必須在頁面標明繁中是直接
//     譯自希臘原文——那是比經由學術英譯更高的風險，讀者有權知道。

export interface AlignedSegment {
  /** 面／欄，如「Face A」；PHI 案例式來源留空 */
  face?: string
  /** 案號，如 'I'、'XII'；CGRN 行號式來源留空 */
  case?: string
  /** 本段起始的石面行號；0 表示需人工對齊 */
  line_from: number
  /** 本段結束行號（案例式來源才有） */
  line_to?: number
  /** 希臘原文，保留 Leiden 補字符號 */
  greek: string
  /** 英譯（CGRN 提供）；無英譯中介時為空 */
  en?: string
  /** 繁體中文（本站逐段翻） */
  zh: string
  note?: string
}

export interface AlignedText {
  /** 來源庫。perseus ＝ 傳世文獻（Perseus 標準 TEI），其餘兩者為銘文 */
  source: 'cgrn' | 'phi' | 'perseus'
  /** 該庫的編號；perseus 無編號，一律 0，改以 slug 定位 */
  ref: number
  /** perseus 專用：檔名即路由 slug */
  slug?: string
  /** 作者（文獻才有；銘文多為佚名或城邦） */
  author?: string
  /** 詩行總數（文獻才有） */
  lines_total?: number
  /** 學術編號，如 'IG IV²,1 121'；CGRN 用 'CGRN 13' */
  siglum: string
  url: string
  title_zh: string
  title_en: string
  /** 所屬卷次 key，如 'K'、'Ch' */
  volume: string
  date?: string
  provenance?: string
  support?: string
  bibliography?: string
  licence: string
  /** 'cgrn' = 以 CGRN 英譯為中介；'perseus-eng' = 以 Perseus 收錄的公有領域英譯
   *  為中介；'none' = 無英譯可依據，直接譯自希臘原文（可信度較低，版面須標明） */
  pivot: 'cgrn' | 'perseus-eng' | 'none'
  pivot_note?: string
  /** 本篇專名定譯表 */
  names: Record<string, string>
  segments: AlignedSegment[]
}

interface RawDoc {
  cgrn?: number
  phi?: number
  slug?: string
  author?: string
  lines_total?: number
  siglum?: string
  url: string
  title_zh: string
  title_en: string
  volume: string
  date?: string
  provenance?: string
  support?: string
  bibliography?: string
  licence: string
  pivot?: string
  pivot_note?: string
  names?: Record<string, string>
  segments: AlignedSegment[]
}

const cgrnMods = import.meta.glob('./cgrn/*.aligned.json', { eager: true }) as
  Record<string, { default: RawDoc }>
const phiMods = import.meta.glob('./phi/*.aligned.json', { eager: true }) as
  Record<string, { default: RawDoc }>
// 文獻（Perseus TEI）。檔名不帶 .aligned——取源與翻譯寫同一個檔，沒有兩階段產物。
const textMods = import.meta.glob('./text/*.json', { eager: true }) as
  Record<string, { default: RawDoc }>

function normalise(d: RawDoc, source: 'cgrn' | 'phi' | 'perseus'): AlignedText {
  const ref = (source === 'cgrn' ? d.cgrn : source === 'phi' ? d.phi : 0) ?? 0
  return {
    source,
    ref,
    slug: d.slug,
    author: d.author,
    lines_total: d.lines_total,
    siglum: d.siglum ?? `CGRN ${ref}`,
    url: d.url,
    title_zh: d.title_zh,
    title_en: d.title_en,
    volume: d.volume,
    date: d.date,
    provenance: d.provenance,
    support: d.support,
    bibliography: d.bibliography,
    licence: d.licence,
    pivot: d.pivot === 'none' ? 'none' : d.pivot === 'perseus-eng' ? 'perseus-eng' : 'cgrn',
    pivot_note: d.pivot_note,
    names: d.names ?? {},
    segments: d.segments,
  }
}

export const ALIGNED_TEXTS: AlignedText[] = [
  ...Object.values(cgrnMods).map(m => normalise(m.default, 'cgrn')),
  ...Object.values(phiMods).map(m => normalise(m.default, 'phi')),
  ...Object.values(textMods).map(m => normalise(m.default, 'perseus')),
].sort((a, b) => (a.source === b.source
  ? (a.slug && b.slug ? a.slug.localeCompare(b.slug) : a.ref - b.ref)
  : a.source < b.source ? -1 : 1))

export function alignedSlug(t: AlignedText): string {
  // 銘文以「庫-編號」定位；文獻沒有庫編號，改用檔名 slug（theogony、
  // homeric-hymn-04…），路由才讀得懂也才看得懂。
  return t.source === 'perseus' ? (t.slug ?? `perseus-${t.ref}`) : `${t.source}-${t.ref}`
}

export function findAligned(slug: string): AlignedText | undefined {
  return ALIGNED_TEXTS.find(t => alignedSlug(t) === slug)
}

/** 某一卷底下已有原文對照的篇目 */
export function alignedInVolume(volumeKey: string): AlignedText[] {
  return ALIGNED_TEXTS.filter(t => t.volume === volumeKey)
}

/** 本篇是否提供英譯欄 */
export function hasEnglish(t: AlignedText): boolean {
  return t.segments.some(s => (s.en ?? '').trim().length > 0)
}
