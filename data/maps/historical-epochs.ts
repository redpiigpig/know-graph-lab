/**
 * 全球八大人文宗教界域 — 歷時功能：歷史時期定義
 *
 * 時間軸範圍：4000 BCE（-4000）→ 2026 CE。
 * 內部統一以「公元年（CE 為正、BCE 為負、無 0 年）」表示，但程式運算
 * 為簡化處理採天文年（含 0 年），即 `1 BCE = 0`、`2 BCE = -1` …
 * 顯示時用 `formatYear()` 轉回慣用人類年表。
 */

export interface HistoricalEpoch {
  /** 該時代起始年（含 0 年的天文年表示） */
  year: number
  /** 標題（如「青銅時代早期」「希臘化時期」「現代」） */
  label_zh: string
  label_en?: string
  /** 簡述（出現在 tooltip） */
  note?: string
}

/**
 * 預設快照／時間軸關鍵節點
 * 用於：時間軸刻度標籤、快捷跳轉按鈕、tooltip 提示。
 * 注意：滑桿是連續的，這只是視覺參照點，不是離散選項。
 */
export const EPOCHS: HistoricalEpoch[] = [
  { year: -4000, label_zh: '青銅時代曙光', label_en: 'Dawn of Bronze Age', note: '蘇美聚落、古埃及前王朝、印度河前期、馬家窯' },
  { year: -3000, label_zh: '早期文明', label_en: 'Early Civilizations', note: '蘇美城邦、古王國埃及、哈拉帕、龍山' },
  { year: -2000, label_zh: '青銅時代鼎盛', label_en: 'Bronze Age Peak', note: '巴比倫、中王國埃及、米諾斯、商' },
  { year: -1500, label_zh: '青銅時代晚期', label_en: 'Late Bronze Age', note: '赫梯、新王國埃及、邁錫尼、商末' },
  { year: -1000, label_zh: '鐵器時代開端', label_en: 'Iron Age Begins', note: '亞述、腓尼基、希伯來、希臘城邦、周' },
  { year: -500, label_zh: '軸心時代', label_en: 'Axial Age', note: '波斯、希臘、孔子、佛陀、先知' },
  { year: -200, label_zh: '帝國時代興起', label_en: 'Rise of Empires', note: '羅馬共和、漢、孔雀王朝、安息' },
  { year: 0, label_zh: '羅馬與漢', label_en: 'Rome & Han', note: '兩大帝國、絲綢之路初開、佛教東傳、基督教萌芽' },
  { year: 500, label_zh: '古代晚期', label_en: 'Late Antiquity', note: '拜占庭、薩珊、隋唐前夕、笈多、教會擴張' },
  { year: 750, label_zh: '伊斯蘭擴張', label_en: 'Islamic Expansion', note: '阿巴斯哈里發、唐、查理曼前夕' },
  { year: 1000, label_zh: '中世紀盛期', label_en: 'High Middle Ages', note: '宋、塞爾柱、神聖羅馬、十字軍前夕' },
  { year: 1250, label_zh: '蒙古時代', label_en: 'Mongol Era', note: '蒙古帝國、宋亡、馬木留克、十字軍末期' },
  { year: 1500, label_zh: '大航海時代', label_en: 'Age of Exploration', note: '哥倫布、明、奧斯曼、蒙兀兒興起' },
  { year: 1750, label_zh: '近代早期末', label_en: 'Late Early Modern', note: '清盛世、英印貿易、奧斯曼衰退、工業革命前夕' },
  { year: 1900, label_zh: '帝國主義巔峰', label_en: 'Peak Imperialism', note: '殖民體系、晚清、奧匈、奧斯曼末期' },
  { year: 1950, label_zh: '戰後與去殖民', label_en: 'Post-War', note: '去殖民、冷戰、新興民族國家' },
  { year: 2000, label_zh: '當代', label_en: 'Contemporary', note: '全球化、資訊時代' },
  { year: 2026, label_zh: '現代', label_en: 'Modern', note: '當前邊界' },
]

export const YEAR_MIN = -4000
export const YEAR_MAX = 2026

/**
 * 把天文年（含 0）顯示為人類年表（BCE / CE）。
 * 滑桿用天文年，但顯示給使用者時要轉回。
 */
export function formatYear(year: number): string {
  if (year === 0) return '公元前 1 年'
  if (year < 0) return `公元前 ${-year + 1} 年`
  return `公元 ${year} 年`
}

/** 短版（給刻度／徽章用） */
export function formatYearShort(year: number): string {
  if (year === 0) return '1 BCE'
  if (year < 0) return `${-year + 1} BCE`
  return `${year} CE`
}

/** 找出最接近且不晚於 year 的 epoch（給「當前時代」徽章用） */
export function epochAt(year: number): HistoricalEpoch {
  let chosen = EPOCHS[0]
  for (const e of EPOCHS) {
    if (e.year <= year) chosen = e
    else break
  }
  return chosen
}
