// 元文琪譯《阿維斯塔》—— reader 的「既有中譯」對照欄。
//
// 一篇一檔，檔名即 slug，必須對得上書目（test/avesta.spec.ts 釘住）。
// 由 scripts/avesta_yuan_reference.py 從電子圖書館那本的 OCR 全文切出來。
//
// 🚨 **這一欄與 zh 欄不是同一回事，版面上必須分得開。**
//    zh   ＝ 本站以公有領域英譯為中介的自譯，專名一律照 /translation-glossary 的定名
//    yuan ＝ 元文琪譯本，譯自杜斯特哈赫的**波斯文選編本**，專名用**波斯語形式**
//           （巴赫曼＝沃胡‧馬納、奧爾迪貝赫什特＝阿沙‧瓦希什塔、梅赫爾＝密特拉）
//    兩套譯名不可混用，也不可把元譯當成「正確答案」去改自譯——
//    它譯的是另一個底本，連收錄範圍都不一樣。
//
// 🚨 **只有 30 篇有**（伽薩 17＋亞斯納 3＋亞什特 6＋萬迪達德 2＋維斯帕拉德 2）。
//    那是選編本的範圍，其餘各篇這一欄是空的——**不是漏抓**。

/** 一篇的元文琪譯文。verses 的鍵是節號（沿用阿維斯陀原典編號，有跳號）。 */
export interface YuanText {
  slug: string
  translator: string
  source: string
  note: string
  /** 章首在第一個節號出現之前的文字。該頁的節號還原不可靠時，前幾節會落在這裡。 */
  head: string
  head_label: string
  verses: Record<string, string>
}

const MODS: Record<string, () => Promise<{ default: YuanText }>> = {
  ...import.meta.glob('./*.json'),
} as Record<string, () => Promise<{ default: YuanText }>>

export const YUAN_SLUGS: string[] = Object.keys(MODS)
  .map(p => p.split('/').pop()!.replace(/\.json$/, ''))
  .sort()

/** 這一篇有沒有元文琪的譯文？ */
export function hasYuan(slug: string): boolean {
  return YUAN_SLUGS.includes(slug)
}

/** 載入一篇的元文琪譯文。沒有就回 undefined。 */
export async function loadYuan(slug: string): Promise<YuanText | undefined> {
  const path = `./${slug}.json`
  if (!(path in MODS)) return undefined
  return (await MODS[path]!()).default
}

/** 從 reader 的段落引用式取出它涵蓋的**所有**節號。
 *
 *  🚨 兩邊的切段粒度不同，所以不能只取起始節：
 *     本站沿用蓋爾德納校本，會把數節併成一段（`Yt 8.26-28`、`Vd 12.3-4`）；
 *     元文琪那邊是逐節分開的（26、27、28 各一條）。
 *     只取 26 的話，27 與 28 的中譯永遠不會出現在任何一段裡——
 *     而版面完全正常，只是那一段的中譯短了三分之二。
 *
 *  >>> versesOfRef('Y 30.3')      → ['3']
 *  >>> versesOfRef('Yt 8.26-28')  → ['26', '27', '28']
 */
export function versesOfRef(ref: string): string[] {
  const m = /\.(\d+)(?:-(\d+))?/.exec(ref)
  if (!m) return []
  const from = Number(m[1])
  const to = m[2] ? Number(m[2]) : from
  if (!Number.isFinite(from) || !Number.isFinite(to) || to < from || to - from > 40) return [String(from)]
  return Array.from({ length: to - from + 1 }, (_, i) => String(from + i))
}

/** 這一段在元文琪譯本裡對應的文字（涵蓋數節時接起來）。沒有就回空字串。 */
export function yuanForRef(y: YuanText | null | undefined, ref: string): string {
  if (!y) return ''
  return versesOfRef(ref).map(v => y.verses[v]).filter(Boolean).join('')
}
