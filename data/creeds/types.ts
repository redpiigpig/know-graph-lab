/**
 * Creeds & Confessions type definitions
 *
 * 統一 schema：每份信條 = 一個 Creed object
 *  - 信經（尼西亞 325/381）：versions 塞多語言（grc/lat/hye/cop/syr-east/syr-west/gez/zh-*）
 *  - 其他大公會議信條 / 宗派信條 / 教會法規 / Ecumenical Dialogue：versions 三欄（原文 + 英 + 中）
 */

export type CreedCategory =
  | 'apostolic-creed'        // 使徒信經（無大公會議 source）
  | 'ecumenical-council'     // 21 次大公會議
  | 'protestant-confession'  // 新教信條
  | 'orthodox-confession'    // 東正教正面信條
  | 'ecumenical-dialogue'    // 20-21 世紀普世合一對話文件

export type CreedTradition =
  | 'catholic'
  | 'orthodox'           // Eastern Orthodox (Byzantine / Greek / Russian / 中華東正教)
  | 'oriental-orthodox'  // 反迦克墩派（Coptic / Armenian / Syriac-west / Tewahedo / Malankara）
  | 'assyrian'           // 亞述東方教會（聶斯托利傳統，東敘利亞）
  | 'protestant'
  | 'anglican'
  | 'methodist'
  | 'baptist'
  | 'reformed'
  | 'lutheran'
  | 'anabaptist'
  | 'quaker'

export type CreedLanguage =
  | 'grc'                       // Koine / Byzantine Greek
  | 'lat'                       // Latin
  | 'lat-filioque'              // 拉丁含 filioque 西方版
  | 'hye'                       // 古典亞美尼亞文 grabar
  | 'cop'                       // Bohairic Coptic
  | 'cop-sa'                    // Sahidic Coptic
  | 'syr-east'                  // 東敘利亞傳統（亞述東方）
  | 'syr-west'                  // 西敘利亞傳統（敘利亞正教）
  | 'gez'                       // 衣索匹亞 Ge'ez 古典文
  | 'arc'                       // 亞蘭文 / Targum
  | 'hbo'                       // Biblical Hebrew
  | 'de'                        // German（如 Augsburg / Heidelberg 原文）
  | 'en'                        // English
  | 'fr'                        // French
  | 'zh-Hant'                   // 繁體中文（通用）
  | 'zh-Hant-Joint2019'         // 2019 香港合一譯本（五宗派禮儀統一版）
  | 'zh-Hant-Catholic'          // 思高中譯（天主教）
  | 'zh-Hant-Lutheran'          // 中華信義會禮儀本
  | 'zh-Hant-Anglican'          // 香港聖公會 / 中華聖公會禮儀本
  | 'zh-Hant-Orthodox'          // 中華東正教會禮儀本
  | 'zh-Hant-Protestant'        // 新教通用譯本（信義 / 聖經公會）
  | 'zh-Hant-Reformed'          // 改革宗中譯
  | 'zh-Hant-Methodist'         // 衛理宗中譯
  | 'zh-Hant-Baptist'           // 浸信宗中譯

export interface CreedVersion {
  lang: CreedLanguage
  /** 顯示用版本名稱，例如「原文希臘（325 版）」「思高中譯」 */
  label: string
  /** 信條/文件正文。長文以換行分段 */
  text: string
  /**
   * 句對齊版本：陣列長度必須等於該 creed 的 anchor version 的 lines.length；
   * 用於 detail page 的 3-column hover 對照視圖（每 index 一 row，跨欄高亮）。
   * 若不需句對齊，省略本欄；UI 退回單區塊 accordion 顯示。
   */
  lines?: string[]
  /** 來源資料書 / 網站 / 禮儀文本出處 */
  source?: string
  /** 譯者 / 採稿單位（中譯版常需） */
  translator?: string
  /** 若仍待補（待下載 / 待翻譯），標 true，UI 灰底「待補」標籤 */
  placeholder?: boolean
}

export interface Creed {
  slug: string
  category: CreedCategory
  /** 大公會議信條才有 council_no（1-21）；其他類別不填 */
  councilNo?: number
  /**
   * 同一場會議產出多份文件時的子文件代號（梵二有 16 份 SC/LG/DV/GS/...）。
   * 1-20 次大公會議只產出 1 份主要信條，可省略本欄。
   */
  councilDocCode?: string
  /** 同 councilNo 內的子文件排序（梵二 SC=1, LG=2, DV=3, ...） */
  councilDocOrder?: number
  /** 顯示順序（同類別內排序） */
  order: number
  nameZh: string
  nameEn: string
  /** 拉丁正式名稱（如 Symbolum Nicaenum / Confessio Augustana） */
  nameLat?: string
  year: number | string  // 1545-63 等跨年區間
  /** 召集地點 / 文件簽署地 */
  location?: string
  /** 主要主議題（單行摘要） */
  topic: string
  /** 主要起草者 / 簽署者 */
  authors?: string[]
  /** 接受本信條的傳統（接受度差異很大，1054 後分裂得更厲害） */
  acceptedBy: CreedTradition[]
  /** 不接受本信條的主要傳統（顯式排除，避免歧義） */
  rejectedBy?: CreedTradition[]
  versions: CreedVersion[]
  /** 摘要：中文一兩段，介紹 context / 重要性 */
  summaryZh: string
  /** 歷史 notes：bullet points，markdown 字串 */
  notes?: string
  /** 相關信條的 slug（用於前後串連） */
  related?: string[]
  /**
   * 啟用 3-column 句對齊視圖時的 anchor 語言。
   *  - 該 lang 的 version 必須有 lines:string[]，定義 row 數量
   *  - 同 lines.length 的其他 versions 自動加入對齊視圖（按欄類型 中 / 英 / 原文 分類）
   *  - 不設則退回單區塊 accordion 顯示
   *  範例：'zh-Hant-Joint2019'（尼西亞-君士坦丁堡 381 用 2019 五宗派合一譯本作 anchor）
   */
  anchorLang?: CreedLanguage
}

export interface CanonLawDoc {
  slug: string
  tradition: 'catholic' | 'orthodox' | 'protestant' | 'anglican'
  order: number
  nameZh: string
  nameEn: string
  nameLat?: string
  year: number | string
  topic: string
  authors?: string[]
  /** 結構：卷／章／條 ， 「7 books / 1752 canons」這種 */
  structureNote?: string
  versions: CreedVersion[]
  summaryZh: string
  notes?: string
  related?: string[]
}

export const TRADITION_LABEL_ZH: Record<CreedTradition, string> = {
  catholic: '羅馬天主教',
  orthodox: '東正教',
  'oriental-orthodox': '東方東正教（科普特/亞美尼亞/敘利亞/衣索匹亞）',
  assyrian: '亞述東方教會',
  protestant: '新教（通用）',
  anglican: '聖公宗',
  methodist: '衛理宗',
  baptist: '浸信宗',
  reformed: '改革宗',
  lutheran: '信義宗',
  anabaptist: '重洗禮派',
  quaker: '公誼會',
}

export const CATEGORY_LABEL_ZH: Record<CreedCategory, string> = {
  'apostolic-creed': '使徒信經',
  'ecumenical-council': '大公會議信條',
  'protestant-confession': '新教信條',
  'orthodox-confession': '東正教信條',
  'ecumenical-dialogue': '普世合一對話',
}

export const LANG_LABEL_ZH: Record<CreedLanguage, string> = {
  grc: '希臘文（原文）',
  lat: '拉丁文',
  'lat-filioque': '拉丁文（含 filioque 西方版）',
  hye: '古典亞美尼亞文（grabar）',
  cop: '科普特文（Bohairic）',
  'cop-sa': '科普特文（Sahidic）',
  'syr-east': '敘利亞文（東敘利亞傳統）',
  'syr-west': '敘利亞文（西敘利亞傳統）',
  gez: '衣索匹亞 Ge\'ez 古典文',
  arc: '亞蘭文',
  hbo: '聖經希伯來文',
  de: '德文',
  en: '英文',
  fr: '法文',
  'zh-Hant': '繁體中文',
  'zh-Hant-Joint2019': '繁體中文（2019 香港五宗派合一譯本）',
  'zh-Hant-Catholic': '繁體中文（思高‧天主教譯本）',
  'zh-Hant-Lutheran': '繁體中文（中華信義會禮儀本）',
  'zh-Hant-Anglican': '繁體中文（香港聖公會／中華聖公會禮儀本）',
  'zh-Hant-Orthodox': '繁體中文（中華東正教會禮儀本）',
  'zh-Hant-Protestant': '繁體中文（新教‧信義／聖經公會譯本）',
  'zh-Hant-Reformed': '繁體中文（改革宗譯本）',
  'zh-Hant-Methodist': '繁體中文（衛理宗譯本）',
  'zh-Hant-Baptist': '繁體中文（浸信宗譯本）',
}
