// 希臘羅馬大藏經 — 型別定義
//
// 與《基督教大藏經》（data/dazangjing）並列的第二部藏經。體例刻意不同：
//   基督教大藏經＝時代 × 十藏 × 正藏／外藏
//   希臘羅馬大藏經＝兩藏 × 九部 × 卷（Α–Ω／I–VI）
//
// 全書斷限：起自可考的最早文本（約前 8 世紀），終於公元 529 年——
// 東邊查士丁尼關閉雅典學園、達馬斯基烏斯等七哲東走波斯；
// 西邊本篤在卡西諾山砸毀阿波羅像、伐倒聖林、就地建院。兩端同年合攏。
//
// 編排原則（user 定，2026-08-18）：
//   前十四卷按「文本在希臘宗教中的權威位階與成書早晚」排，不按所敘事件先後——
//   荷馬與赫西奧德是希臘人真正當經在讀的東西，故居首（希羅多德 2.53）。
//   後十卷按成書年代排，卷內亦由早到晚，數卷因此自成一部衰亡史。
//
// 歸卷準則：按材料所屬的宗教系統歸卷，不按語言，也不按作者。
//   普魯塔克《努瑪傳》雖希臘文，歸羅馬卷；西塞羅《論神性》雖拉丁文，留希臘卷。

/** 文本存世狀態 —— 這部藏經大量文獻僅存殘篇或敵證，狀態必須在版面上看得見 */
export type WorkStatus = 'whole' | 'fragment' | 'inscription' | 'hostile'

export const STATUS_META: Record<WorkStatus, { zh: string; desc: string; titleCls: string; dotCls: string; rowCls: string }> = {
  whole: {
    zh: '全本',
    desc: '完整傳世。',
    titleCls: 'text-gray-900', dotCls: 'bg-emerald-500', rowCls: '',
  },
  fragment: {
    zh: '殘篇',
    desc: '原書已佚，僅存引文、摘要或紙草殘葉綴輯而成。',
    titleCls: 'text-amber-800', dotCls: 'bg-amber-400', rowCls: 'bg-amber-50/40',
  },
  inscription: {
    zh: '銘文／紙草',
    desc: '非書籍傳抄，出自石刻、鉛片、金葉或紙草的儀式現場文本。',
    titleCls: 'text-sky-800', dotCls: 'bg-sky-500', rowCls: 'bg-sky-50/40',
  },
  hostile: {
    zh: '敵證',
    desc: '僅存於基督教作家為駁斥而作的引用；敘述框架受敵手支配，不可當中性紀錄使用。',
    titleCls: 'text-rose-800', dotCls: 'bg-rose-500', rowCls: 'bg-rose-50/40',
  },
}

/** 收錄軌道：正文 或 續典（拉丁對照） */
export type WorkTrack = 'main' | 'latin'

export const TRACK_LABEL: Record<WorkTrack, { zh: string; cls: string }> = {
  main: { zh: '正文', cls: '' },
  latin: { zh: '續', cls: 'bg-stone-200 text-stone-700' },
}

/** 單一作品（書目條目） */
export interface HellenWork {
  /** 漢語定名（先過 /translation-glossary 神祇與人名表） */
  title_zh: string
  /** 原文題名（希臘文／拉丁文），或學界通用英文題名 */
  title_orig?: string
  /** 作者；佚名者標傳統或社群 */
  author?: string
  /** 成書／定型年代 */
  era?: string
  /** 所敘年代（神話內敘時間）。設此欄後，站上可切「按成書／按所敘」兩種讀序 */
  era_narrated?: string
  /** 出土／寫作地點 */
  place?: string
  /** 語言 */
  language?: string
  /** 作品自身規模，如「全 24 卷」「87 首」「約 200 行」 */
  extent?: string
  /** 母合集名（依卷拆分時以此歸群），如「史詩循環」「希臘魔法紙草」 */
  parent?: string
  /** 一句簡述（顯示於標題下） */
  note?: string
  /** 100–200 字簡介（顯示於右欄） */
  intro?: string
  /** 站內對照工具連結 */
  link?: string
  /** 存世狀態；不設＝全本 */
  status?: WorkStatus
  /** 收錄軌道；不設＝正文 */
  track?: WorkTrack
  /** 殘篇／敵證的轉引來源，如「普羅克洛斯《文選》摘要」「奧利金《駁塞爾蘇斯》」 */
  via?: string
  /** 與另一藏經／另一卷互見，如「基督教大藏經‧前藏經藏」 */
  seealso?: string
}

/** 卷內的「部」（子分類） */
export interface HellenDivision {
  key: string
  label: string
  label_en?: string
  desc?: string
  works: HellenWork[]
}

/** 一卷 */
export interface HellenVolume {
  key: string
  /** 卷次符號：希臘卷用 Α–Ω，羅馬卷用 I–VI */
  sigil: string
  name: string
  name_en: string
  /** 聖經對位，如「創世記 1–2」 */
  parallel?: string
  /** 時鐘：神話內敘時間 或 成書年代 */
  clock?: 'mythic' | 'historical'
  /** 年代跨度，如「700 BCE–450 CE」 */
  span?: string
  summary: string
  divisions: HellenDivision[]
}

/** 卷群（部）——把卷分組，供索引頁瀏覽 */
export interface HellenPart {
  key: string
  label: string
  label_en?: string
  desc?: string
  /** 本部所轄卷次符號 */
  volumes: string[]
}

/** 一藏（希臘卷 或 羅馬卷） */
export interface HellenCanon {
  key: string
  name: string
  name_en: string
  glyph: string
  subtitle: string
  /** 該藏的定位與收錄準則 */
  summary: string
  enabled: boolean
  parts: HellenPart[]
  volumes: HellenVolume[]
}

export function volumeWorkCount(v: HellenVolume): number {
  return v.divisions.reduce((n, d) => n + d.works.length, 0)
}

export function canonWorkCount(c: HellenCanon): number {
  return c.volumes.reduce((n, v) => n + volumeWorkCount(v), 0)
}
