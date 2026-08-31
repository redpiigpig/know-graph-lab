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
   *  為中介；'taylor-eng' = 以 Taylor 1792《俄耳甫斯讚歌》英譯為中介；
   *  'none' = 無英譯可依據，直接譯自希臘原文（可信度較低，版面須標明） */
  pivot: 'cgrn' | 'perseus-eng' | 'taylor-eng' | 'none'
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

// 🚨 **不可用 `{ eager: true }`。** 這三個目錄現在有 5.9 MB（光荷馬兩部史詩就
// 4.2 MB），eager 會把全部 JSON 打進 /hellenika/text 這條路由的 chunk，讀者點開
// 任何一首詩頌都得先下載整套藏經。改成惰性：**篇目清單只從檔名推導**（不載內容），
// 正文按 slug 現載一份。
const MODS: Record<string, () => Promise<{ default: RawDoc }>> = {
  ...import.meta.glob('./cgrn/*.aligned.json'),
  ...import.meta.glob('./phi/*.aligned.json'),
  // 文獻。檔名不帶 .aligned——取源與翻譯寫同一個檔，沒有兩階段產物。
  ...import.meta.glob('./text/*.json'),
} as Record<string, () => Promise<{ default: RawDoc }>>

/** 篇目清單的一列。只有路由定位所需的資訊，都是從檔名推得，不必載入正文。 */
export interface AlignedRef {
  source: 'cgrn' | 'phi' | 'perseus'
  /** 路由 slug：銘文為「庫-編號」，文獻為檔名 */
  slug: string
  path: string
}

function refOf(path: string): AlignedRef {
  const file = path.split('/').pop()!.replace(/\.aligned\.json$|\.json$/, '')
  const source = path.includes('/cgrn/') ? 'cgrn' : path.includes('/phi/') ? 'phi' : 'perseus'
  // 銘文的檔名本身就是「庫-編號」，文獻的檔名本身就是 slug——兩者都直接當 slug 用。
  return { source, slug: file, path }
}

/** 全部篇目，依「來源、再依 slug」排序。**不含正文**。 */
export const ALIGNED_REFS: AlignedRef[] = Object.keys(MODS)
  .map(refOf)
  .sort((a, b) => (a.source === b.source
    ? a.slug.localeCompare(b.slug, undefined, { numeric: true })
    : a.source < b.source ? -1 : 1))

export function alignedSlug(t: AlignedRef): string {
  return t.slug
}

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
    pivot: d.pivot === 'none' || d.pivot === 'perseus-eng' || d.pivot === 'taylor-eng'
      ? d.pivot
      : 'cgrn',
    pivot_note: d.pivot_note,
    names: d.names ?? {},
    segments: d.segments,
  }
}

/** 載入一篇的正文。找不到回 undefined。 */
export async function loadAligned(slug: string): Promise<AlignedText | undefined> {
  const ref = ALIGNED_REFS.find(r => r.slug === slug)
  if (!ref) return undefined
  return normalise((await MODS[ref.path]!()).default, ref.source)
}

/** 本篇是否提供英譯欄 */
export function hasEnglish(t: AlignedText): boolean {
  return t.segments.some(s => (s.en ?? '').trim().length > 0)
}
