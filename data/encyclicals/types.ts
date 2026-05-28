/**
 * Papal Magisterium type definitions
 *
 * 個別教宗頒布的訓導文獻（通諭／勸諭／憲令／自動詔書／使徒書信／演說／講道）。
 * 與 [[scripture-canon-portal]] 的 /creeds（大公會議產出的集體文件）分工。
 *
 * 三欄逐段對照（中／英／拉）— UI 邏輯直接複用 data/creeds/paragraphParser.ts 的
 * parseDoc() + alignDocs()。
 */

/**
 * 訓導位階 (Magisterium tier) — pope 個人頁面 3-tab 分組依據。
 *
 * - 'teaching'：B 位階教宗訓導（通諭／勸諭／憲令／牧函／自動詔書／詔書／短札）
 * - 'curia'：C 位階教廷部會文件（訓令／宣言／法令／通告／答覆）— 由 dicastery 頒布
 * - 'message'：D 位階一般文告（年度文告／講道／演說／致詞／非正式書信）
 */
export type PapalDocTier = 'teaching' | 'curia' | 'message'

export type PapalDocCategory =
  // ─── B 位階：教宗訓導 (tier='teaching') ───
  | 'encyclical'        // 通諭 Litterae Encyclicae
  | 'apostolic-const'   // 使徒憲令 Constitutio Apostolica
  | 'apostolic-exhort'  // 使徒勸諭 Exhortatio Apostolica
  | 'apostolic-letter'  // 使徒書信 Litterae Apostolicae
  | 'motu-proprio'      // 自動詔書 Motu Proprio
  | 'bull'              // 中世紀詔書 Bulla
  | 'brief'             // 教宗短札 Breve
  | 'epistola'          // 教宗書信 Epistola
  // ─── C 位階：教廷部會 (tier='curia') ───
  | 'instruction'       // 訓令 Instructio
  | 'declaration'       // 宣言 Declaratio
  | 'decree'            // 法令 Decretum
  | 'notification'      // 通告 Notificatio
  | 'responsum'         // 答覆 Responsum
  | 'curia-document'    // 其他部會文件（一般類）
  // ─── D 位階：一般文告 (tier='message') ───
  | 'allocution'        // 演說 Allocutio
  | 'homily'            // 講道 Homilia
  | 'message'           // 訊息 Nuntius
  | 'letter-informal'   // 非正式書信（致個別群體）

export type PapalDocLanguage =
  | 'lat'
  | 'en'
  | 'zh-Hant'
  | 'it'
  | 'fr'
  | 'es'
  | 'de'
  | 'pt'
  | 'grc'

export interface PapalDocumentVersion {
  lang: PapalDocLanguage
  /** 顯示用版本名稱，例：「拉丁原文 (vatican.va)」「中文 (主教團 2015 譯本)」 */
  label: string
  /** 對齊用 textKey；對應 data/encyclicals/{NNc-pope-slug}/{textKey}.txt */
  textKey: string
  /** 來源 URL 或紙本書目 */
  source?: string
  /** 譯者 / 採稿單位（中譯版必填） */
  translator?: string
  /** 若仍待補（待下載 / 待翻譯），標 true */
  placeholder?: boolean
}

export interface PapalDocument {
  /** URL slug，全域唯一 */
  slug: string
  /** 對應 Pope.slug；curia 文件可能為空（issuer 為部會） */
  popeSlug: string
  /**
   * 訓導位階分組。預設 'teaching'（既有所有 PapalDocument 都歸此）。
   * - 'teaching'：教宗訓導（通諭等 B 位階）
   * - 'curia'：教廷部會文件（C 位階）
   * - 'message'：一般文告（D 位階）
   */
  tier?: PapalDocTier
  /**
   * 頒布單位（中文）— 用於 'curia' tier 時必填，標明 issuing dicastery。
   * 例：「信理部」「禮儀及聖事部」「宗座聖赦院」
   * 'teaching' / 'message' tier 此欄留空（由 popeSlug 對應教宗即可）。
   */
  issuer?: string
  category: PapalDocCategory
  /** 拉丁正式名稱 — Rerum Novarum / Laudato Si' / Fratelli Tutti */
  titleLat: string
  /** 英文標題 — On Care for Our Common Home */
  titleEn: string
  /** 中文標題 — 《願祢受讚頌》通諭 */
  titleZh: string
  /** 頒布日期 YYYY-MM-DD */
  promulgationDate: string
  /** 主要落在哪個世紀（4-21） */
  century: number
  /** 中文摘要 1-2 段 */
  summaryZh: string
  /** 主議題標籤，列表 chip 顯示 */
  topics: string[]
  /** 中文 → 英文 → 拉丁 排序 */
  versions: PapalDocumentVersion[]
  /** 'simple' = 三欄並列整段；'paragraph-aligned' = 用 parseDoc 段號對齊 */
  displayMode: 'simple' | 'paragraph-aligned'
  /** 相關文件 slug */
  related?: string[]
  /** 原 vatican.va URL（如有） */
  vaticanUrl?: string
  notes?: string
}

export interface Pope {
  slug: string
  /** 中文教宗名（依教廷官方譯名）— 例：方濟各 / 本篤十六世 / 良十三世 */
  nameZh: string
  /** 英文教宗名 — Francis / Benedict XVI / Leo XIII */
  nameEn: string
  /** 拉丁教宗名 — Franciscus / Benedictus PP. XVI */
  nameLat: string
  /** 出生時的世俗姓名 */
  birthName?: string
  /** 在位起 YYYY-MM-DD */
  pontificateStart: string
  /** 在位迄 YYYY-MM-DD；在位中填空字串 */
  pontificateEnd: string
  /** 主要在位世紀 */
  century: number
  /** 國籍 */
  nationality: string
  /** 簡介（1-2 段繁中） */
  notesZh?: string
}

export const CATEGORY_LABEL_ZH: Record<PapalDocCategory, string> = {
  // teaching
  encyclical: '通諭',
  'apostolic-const': '使徒憲令',
  'apostolic-exhort': '使徒勸諭',
  'apostolic-letter': '使徒書信',
  'motu-proprio': '自動詔書',
  bull: '詔書',
  brief: '教宗短札',
  epistola: '教宗書信',
  // curia
  instruction: '訓令',
  declaration: '宣言',
  decree: '法令',
  notification: '通告',
  responsum: '答覆',
  'curia-document': '部會文件',
  // message
  allocution: '演說',
  homily: '講道',
  message: '文告',
  'letter-informal': '致函',
}

export const CATEGORY_LABEL_LAT: Record<PapalDocCategory, string> = {
  // teaching
  encyclical: 'Litterae Encyclicae',
  'apostolic-const': 'Constitutio Apostolica',
  'apostolic-exhort': 'Exhortatio Apostolica',
  'apostolic-letter': 'Litterae Apostolicae',
  'motu-proprio': 'Motu Proprio',
  bull: 'Bulla',
  brief: 'Breve',
  epistola: 'Epistola',
  // curia
  instruction: 'Instructio',
  declaration: 'Declaratio',
  decree: 'Decretum',
  notification: 'Notificatio',
  responsum: 'Responsum',
  'curia-document': 'Documentum Dicasterii',
  // message
  allocution: 'Allocutio',
  homily: 'Homilia',
  message: 'Nuntius',
  'letter-informal': 'Epistula',
}

/** category → tier 對映表（schema 預設值；個別 doc 可覆寫 .tier 欄位） */
export const CATEGORY_TIER: Record<PapalDocCategory, PapalDocTier> = {
  encyclical: 'teaching',
  'apostolic-const': 'teaching',
  'apostolic-exhort': 'teaching',
  'apostolic-letter': 'teaching',
  'motu-proprio': 'teaching',
  bull: 'teaching',
  brief: 'teaching',
  epistola: 'teaching',
  instruction: 'curia',
  declaration: 'curia',
  decree: 'curia',
  notification: 'curia',
  responsum: 'curia',
  'curia-document': 'curia',
  allocution: 'message',
  homily: 'message',
  message: 'message',
  'letter-informal': 'message',
}

/** Tier 顯示用 — UI 3-tab labels */
export const TIER_LABEL_ZH: Record<PapalDocTier, string> = {
  teaching: '教宗訓導',
  curia: '部會文件',
  message: '一般文告',
}

export const TIER_DESC_ZH: Record<PapalDocTier, string> = {
  teaching: '通諭 / 勸諭 / 憲令 / 牧函 / 自動詔書 — 教宗個人頒布的正式訓導文件',
  curia: '訓令 / 宣言 / 法令 — 教廷部會（信理部／禮儀部等）頒布',
  message: '文告 / 演說 / 講道 — 牧靈性文件（世界和平日／青年日等年度系列）',
}

/** 取得文件的有效 tier（優先用 doc.tier，否則依 category 推斷） */
export function docTier(d: PapalDocument): PapalDocTier {
  return d.tier ?? CATEGORY_TIER[d.category] ?? 'teaching'
}

export const LANG_LABEL_ZH: Record<PapalDocLanguage, string> = {
  lat: '拉丁文',
  en: '英文',
  'zh-Hant': '繁體中文',
  it: '義大利文',
  fr: '法文',
  es: '西班牙文',
  de: '德文',
  pt: '葡萄牙文',
  grc: '希臘文',
}

/** 世紀數字 → 顯示字串 */
export function centuryLabel(n: number): string {
  return `${n} 世紀`
}
