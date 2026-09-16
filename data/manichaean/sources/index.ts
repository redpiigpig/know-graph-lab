// 摩尼教經典 — 已取得原文並逐段對齊的篇章。
//
// 一篇一個 JSON，檔名即路由 slug，且**必須**對得上 data/manichaean 書目裡的 slug；
// 對不上的檔案 reader 走不到，而書目頁照樣顯示、完全看不出少了東西。
// test/manichaean.spec.ts 釘住這條對應。
//
// ══════════ 切段單位：摩尼教沒有統一的引用式，所以規矩要寫死 ══════════
//
//   這是本區與 /avesta 最大的不同。祆教有現成的禮儀節號（Y 28.1、Vd 3.24），
//   全世界都照著引。摩尼教**沒有**——因為絕大多數文獻是殘片，
//   原書的章節結構早就斷了。學界的引用方式依材料而異：
//
//     科普特抄本   — 抄本頁行號（1 Ke 38, 89.18–24）。頁行號是抄本的物理位置，
//                    不是原書的章節，所以不能跨抄本比對。
//     吐魯番殘卷   — 館藏編號＋葉面＋行號（M 470 R/ii/1–8）。
//                    R/V 是正背面，ii 是欄。**這三者缺一不可**，
//                    只寫 M 470 指的是整張紙，不是某一段。
//     漢文寫卷     — 《大正藏》冊．頁．欄．行（T54, 1270b12–18）。
//                    🚨 這一條與 [[feedback_pdf_page_number]] 同理：頁碼照抄，不重編。
//     敵證引文     — 駁論本身的章節（c. ep. fund. 5；Fihrist IX.1）。
//
//   共通規矩只有一條：**ref 欄照抄學界的引用式，一個字都不要自己發明。**
//   自編段號會讓這一頁的每一段都無法被外部引用，而版面看起來完全正常。

/** 一段。ref 是引用基礎，一律沿用學界既有的引用式，不重編。 */
export interface ManiSegment {
  /** 大單位：科普特抄本的頁碼、吐魯番殘卷的編號、漢文的大正藏頁欄 */
  chapter: number | string
  /** 小單位：行號或節號，如 18、'18-24' */
  verse: number | string
  /** 完整引用式，如 '1 Ke 89.18–24'、'M 470 R/ii/1–8'、'T54, 1270b12'。
   *  頁面直接顯示這個，不自行拼。 */
  ref: string
  /** 原文轉寫（或漢文原文） */
  orig?: string
  /** 英譯 */
  en?: string
  /** 繁體中文（本站逐段翻；漢文藏不填，見 SINGLE_COLUMN_CANON） */
  zh?: string
  note?: string
}

/** 原文欄是什麼東西。摩尼教牽涉的語言比祆教多，標明才知道該怎麼排版。 */
export type ScriptKind =
  /** 科普特文（希臘字母＋七個俗體字母） */
  | 'coptic'
  /** 摩尼字母書寫的中古伊朗語，以拉丁轉寫呈現 */
  | 'manichaean-translit'
  /** 回鶻語拉丁轉寫 */
  | 'uighur-translit'
  /** 希臘文 */
  | 'greek'
  /** 拉丁文 */
  | 'latin'
  /** 敘利亞文轉寫 */
  | 'syriac-translit'
  /** 漢文（本身即正文，不是轉寫） */
  | 'chinese'

/** 繁中是怎麼來的——可信度差很多，版面上必須標明 */
export type PivotKind =
  /** 以開放取用的學術英譯為中介（IAMS 選輯、斯克耶爾沃譯注） */
  | 'iams-eng'
  /** 以公有領域英譯為中介（ANF／NPNF／19 世紀校譯本） */
  | 'pd-eng'
  /** 無英譯可依據，直接譯自原文轉寫（可信度較低） */
  | 'none'
  /** 不適用：本篇原文即中文，無翻譯問題 */
  | 'native-chinese'

export interface ManiTextDoc {
  /** 路由 slug，必須對得上書目 */
  slug: string
  /** 學術編號 */
  siglum: string
  title_zh: string
  title_en?: string
  /** 所屬藏與卷的 key，供 reader 走回上一層 */
  canon: string
  volume: string
  script?: ScriptKind
  orig_source?: string
  orig_url?: string
  en_source?: string
  en_translator?: string
  en_url?: string
  licence: string
  pivot: PivotKind
  pivot_note?: string
  /** 本篇專名定譯表（過 /translation-glossary） */
  names?: Record<string, string>
  segments: ManiSegment[]
}

// 🚨 不可用 `{ eager: true }`：正文全部上架後這個目錄會很大，
//    eager 會把全部 JSON 打進 /manichaean/text 這條路由的 chunk。
const MODS: Record<string, () => Promise<{ default: ManiTextDoc }>> = {
  ...import.meta.glob('./text/*.json'),
} as Record<string, () => Promise<{ default: ManiTextDoc }>>

export interface ManiTextRef {
  slug: string
  path: string
}

export const TEXT_REFS: ManiTextRef[] = Object.keys(MODS)
  .map(path => ({ slug: path.split('/').pop()!.replace(/\.json$/, ''), path }))
  .sort((a, b) => a.slug.localeCompare(b.slug))

/** 這一篇有沒有正文可讀？ */
export function hasText(slug: string): boolean {
  return TEXT_REFS.some(r => r.slug === slug)
}

/** 載入一篇的正文。找不到回 undefined。 */
export async function loadText(slug: string): Promise<ManiTextDoc | undefined> {
  const ref = TEXT_REFS.find(r => r.slug === slug)
  if (!ref) return undefined
  return (await MODS[ref.path]!()).default
}

/** 某一欄實際有幾段有內容——空欄不出，免得整欄都是「—」 */
export function filledCount(t: ManiTextDoc, col: 'orig' | 'en' | 'zh'): number {
  return t.segments.filter(s => (s[col] ?? '').trim().length > 0).length
}

/** 🚨 漢文藏只出一欄：原文即中文，不可再「翻譯」成現代中文。
 *  reader 依此決定欄數，見 data/manichaean/chinese.ts 檔首。 */
export const SINGLE_COLUMN_CANON = 'chinese'
