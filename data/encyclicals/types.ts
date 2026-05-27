/**
 * Papal Magisterium type definitions
 *
 * 個別教宗頒布的訓導文獻（通諭／勸諭／憲令／自動詔書／使徒書信／演說／講道）。
 * 與 [[scripture-canon-portal]] 的 /creeds（大公會議產出的集體文件）分工。
 *
 * 三欄逐段對照（中／英／拉）— UI 邏輯直接複用 data/creeds/paragraphParser.ts 的
 * parseDoc() + alignDocs()。
 */

export type PapalDocCategory =
  | 'encyclical'        // 通諭 Litterae Encyclicae
  | 'apostolic-const'   // 使徒憲令 Constitutio Apostolica
  | 'apostolic-exhort'  // 使徒勸諭 Exhortatio Apostolica
  | 'apostolic-letter'  // 使徒書信 Litterae Apostolicae
  | 'motu-proprio'      // 自動詔書 Motu Proprio
  | 'bull'              // 中世紀詔書 Bulla
  | 'brief'             // 教宗短札 Breve
  | 'allocution'        // 演說 Allocutio
  | 'homily'            // 講道 Homilia
  | 'message'           // 訊息 Nuntius
  | 'epistola'          // 教宗書信 Epistola

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
  /** 對應 Pope.slug */
  popeSlug: string
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
  encyclical: '通諭',
  'apostolic-const': '使徒憲令',
  'apostolic-exhort': '使徒勸諭',
  'apostolic-letter': '使徒書信',
  'motu-proprio': '自動詔書',
  bull: '詔書',
  brief: '教宗短札',
  allocution: '演說',
  homily: '講道',
  message: '訊息',
  epistola: '教宗書信',
}

export const CATEGORY_LABEL_LAT: Record<PapalDocCategory, string> = {
  encyclical: 'Litterae Encyclicae',
  'apostolic-const': 'Constitutio Apostolica',
  'apostolic-exhort': 'Exhortatio Apostolica',
  'apostolic-letter': 'Litterae Apostolicae',
  'motu-proprio': 'Motu Proprio',
  bull: 'Bulla',
  brief: 'Breve',
  allocution: 'Allocutio',
  homily: 'Homilia',
  message: 'Nuntius',
  epistola: 'Epistola',
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
