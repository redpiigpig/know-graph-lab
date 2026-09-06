// 祆教經典 — 已取得原文並逐段對齊的篇章。
//
// 一篇一個 JSON，檔名即路由 slug，且**必須**對得上 data/avesta 書目裡的 slug；
// 對不上的檔案 reader 走不到，而書目頁照樣顯示、完全看不出少了東西。
// test/avesta.spec.ts 釘住這條對應。
//
// 切段單位：
//   阿維斯陀語各篇  — 按經文自身的**節號**（Y 28.1、Vd 3.24、Yt 10.4），
//                     那既是禮儀單位也是學界唯一的引用式，不可自編。
//   巴列維文獻      — 按章節號（Dk 8.44.1、Bd 3.7）。
//   銘文            — 按欄與行（DB I.1–8）。
//
// 三欄：
//   orig ＝ 霍夫曼式拉丁轉寫（阿維斯陀字母由 utils/avestanScript.ts 現場轉，不入檔）
//   en   ＝ 公有領域英譯，多為《東方聖書》
//   zh   ＝ 本站逐段繁中
//
// 🚨 **不可用 `{ eager: true }`。** 亞斯納與萬迪達德全本上架後這個目錄會很大，
//    eager 會把全部 JSON 打進 /avesta/text 這條路由的 chunk。惰性載入，
//    清單只從檔名推導。

/** 一段。段號是引用基礎，一律沿用經文自身的編號，不重編。 */
export interface AvestaSegment {
  /** 章／法爾迦爾德／首 的編號，如 28（Y 28）、3（Vd 3） */
  chapter: number | string
  /** 節號，如 1、'1-3'。銘文用行號區間。 */
  verse: number | string
  /** 完整引用式，如 'Y 28.1'。頁面直接顯示這個，不自行拼。 */
  ref: string
  /** 原文轉寫；無原文可得時留空 */
  orig?: string
  /** 英譯 */
  en?: string
  /** 繁體中文（本站逐段翻） */
  zh?: string
  note?: string
}

/**
 * 原文轉寫用的是哪一套方案。**這一欄決定阿維斯陀字母欄能不能開。**
 *
 * 🚨 avesta.org 用的是蓋爾德納舊式羅馬轉寫（mraot ahurô mazdå），
 *    以 sh／zh／kh／th／dh／gh／ng 表 š／ž／x／θ／δ／γ／ŋ。這套方案在
 *    「ŋ 還是 n+g」這類位置上需要語音學判斷才拆得開，機器硬轉會拼錯——
 *    而且錯了以後畫面照樣是一串漂亮的阿維斯陀字，沒有人看得出來。
 *    所以本站只對霍夫曼式轉寫開放字母切換，舊式一律不轉，並在頁面說明原因。
 *    要讓全藏都能切字母，得另尋霍夫曼式的取源（TITUS 詞級表格或柏林 CAB）。
 */
export type TranslitScheme =
  /** 霍夫曼式學術轉寫（ā š θ ə）——utils/avestanScript.ts 能安全轉成字母 */
  | 'hoffmann'
  /** 蓋爾德納舊式羅馬轉寫（â sh th ô）——忠實保留，但不轉字母 */
  | 'geldner-roman'
  /** 中古波斯語／古波斯語轉寫——與阿維斯陀字母無關 */
  | 'middle-persian'
  | 'old-persian'

/** 繁中是怎麼來的——可信度差很多，版面上必須標明 */
export type PivotKind =
  /** 以《東方聖書》的公有領域英譯為中介 */
  | 'sbe-eng'
  /** 以其他公有領域英譯為中介 */
  | 'other-eng'
  /** 無英譯可依據，直接譯自原文轉寫（可信度較低） */
  | 'none'

export interface AvestaText {
  /** 路由 slug，必須對得上書目 */
  slug: string
  /** 學術編號，如 'Y 28' */
  siglum: string
  title_zh: string
  title_en?: string
  /** 所屬藏與卷的 key，供 reader 走回上一層 */
  canon: string
  volume: string
  /** 原文轉寫用的方案。決定能否提供阿維斯陀字母欄。 */
  orig_scheme?: TranslitScheme
  /** 原文轉寫的取源 */
  orig_source?: string
  orig_url?: string
  /** 英譯的取源與譯者 */
  en_source?: string
  en_translator?: string
  en_url?: string
  licence: string
  pivot: PivotKind
  pivot_note?: string
  /** 本篇專名定譯表（過 /translation-glossary） */
  names?: Record<string, string>
  segments: AvestaSegment[]
}

const MODS: Record<string, () => Promise<{ default: AvestaText }>> = {
  ...import.meta.glob('./text/*.json'),
} as Record<string, () => Promise<{ default: AvestaText }>>

/** 篇目清單的一列。只有定位所需，不載正文。 */
export interface AvestaTextRef {
  slug: string
  path: string
}

export const TEXT_REFS: AvestaTextRef[] = Object.keys(MODS)
  .map(path => ({ slug: path.split('/').pop()!.replace(/\.json$/, ''), path }))
  .sort((a, b) => a.slug.localeCompare(b.slug))

/** 這一篇有沒有正文可讀？書目頁據此決定連結是否可點。 */
export function hasText(slug: string): boolean {
  return TEXT_REFS.some(r => r.slug === slug)
}

/** 載入一篇的正文。找不到回 undefined。 */
export async function loadText(slug: string): Promise<AvestaText | undefined> {
  const ref = TEXT_REFS.find(r => r.slug === slug)
  if (!ref) return undefined
  return (await MODS[ref.path]!()).default
}

/** 某一欄實際有幾段有內容——空欄不出，免得整欄都是「—」 */
export function filledCount(t: AvestaText, col: 'orig' | 'en' | 'zh'): number {
  return t.segments.filter(s => (s[col] ?? '').trim().length > 0).length
}
