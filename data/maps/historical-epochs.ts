/**
 * 全球八大人文宗教界域 — 歷時功能：歷史時期定義
 *
 * 時間軸範圍：4000 BCE（-4000）→ 2026 CE。
 * 採用 600 年制人類史分期（使用者偏好）：
 *   ≤ -1200       新石器／青銅器（按器物時代分）
 *   -1200 ~ -600  古風時代
 *   -600  ~ 0     軸心時代
 *   0     ~ 600   古典時代
 *   600   ~ 1200  中古時代
 *   1200  ~ 1800  近世
 *   1800+         近現代
 *
 * 內部統一以「天文年」表示，即 `1 BCE = 0`、`2 BCE = -1` …
 * 顯示時用 `formatYear()` 轉回慣用人類年表。
 */

export interface HistoricalEpoch {
  /** 該時代起始年（含 0 年的天文年表示） */
  year: number
  /** 標題（如「軸心時代」「古典時代」） */
  label_zh: string
  label_en?: string
  /** 簡述（出現在 tooltip） */
  note?: string
  /** 是否為 600 年制大時代分界（在 UI 中強調） */
  is_major?: boolean
}

/**
 * 主要 epoch（依 600 年制）+ 次要關鍵年份（重要轉折）
 * 用於：時間軸刻度標籤、快捷跳轉按鈕、tooltip 提示。
 */
export const EPOCHS: HistoricalEpoch[] = [
  // === 史前 / 石器-金屬器時代 ===
  { year: -4000, label_zh: '新石器晚期', label_en: 'Late Neolithic', note: '蘇美聚落、古埃及前王朝、印度河前期、馬家窯', is_major: true },
  { year: -3000, label_zh: '早期青銅', label_en: 'Early Bronze Age', note: '蘇美城邦、古王國埃及、哈拉帕、龍山' },
  { year: -2000, label_zh: '中期青銅', label_en: 'Middle Bronze Age', note: '巴比倫、中王國埃及、米諾斯、商' },
  { year: -1500, label_zh: '晚期青銅', label_en: 'Late Bronze Age', note: '赫梯、新王國埃及、邁錫尼、商末' },

  // === 古風時代 (-1200 ~ -600) ===
  { year: -1200, label_zh: '古風時代', label_en: 'Archaic Age', note: '鐵器開端、新亞述、希伯來王國、腓尼基殖民', is_major: true },
  { year: -1000, label_zh: '鐵器初興', label_en: 'Iron Age Begins', note: '亞述、腓尼基、希伯來、希臘城邦、周' },

  // === 軸心時代 (-600 ~ 0) ===
  { year: -600, label_zh: '軸心時代', label_en: 'Axial Age', note: '波斯、希臘、孔子、佛陀、先知傳統並起', is_major: true },
  { year: -500, label_zh: '軸心高峰', label_en: 'Peak of Axial Age', note: '阿契美尼德、希臘黃金期、釋迦、孔子' },
  { year: -322, label_zh: '希臘化開端', label_en: 'Hellenistic Begins', note: '亞歷山大死、塞琉古、托勒密、孔雀王朝' },
  { year: -200, label_zh: '帝國時代興起', label_en: 'Rise of Empires', note: '羅馬共和、漢、孔雀王朝、安息' },

  // === 古典時代 (0 ~ 600) ===
  { year: 0, label_zh: '古典時代', label_en: 'Classical Age', note: '羅馬、漢、孔雀後繼、絲綢之路、佛教東傳、基督教萌芽', is_major: true },
  { year: 200, label_zh: '帝國盛期', label_en: 'Imperial Peak', note: '羅馬鼎盛、東漢、貴霜、薩珊前夕' },
  { year: 500, label_zh: '古代晚期', label_en: 'Late Antiquity', note: '拜占庭、薩珊、笈多、教會擴張、北朝' },

  // === 中古時代 (600 ~ 1200) ===
  { year: 600, label_zh: '中古開端', label_en: 'Early Middle Ages', note: '伊斯蘭興起、唐、查理曼前夕', is_major: true },
  { year: 800, label_zh: '伊斯蘭與唐', label_en: 'Islamic & Tang', note: '阿巴斯黃金時代、唐、查理曼' },
  { year: 1000, label_zh: '中古盛期', label_en: 'High Middle Ages', note: '宋、塞爾柱、神聖羅馬、十字軍前夕' },

  // === 近世 (1200 ~ 1800) ===
  { year: 1200, label_zh: '近世開端', label_en: 'Early Modern Begins', note: '蒙古崛起、宋亡、馬木留克', is_major: true },
  { year: 1279, label_zh: '蒙古巔峰', label_en: 'Mongol Peak', note: '元朝、伊兒、欽察、察合台四汗國' },
  { year: 1500, label_zh: '大航海', label_en: 'Age of Exploration', note: '哥倫布、明、奧斯曼、蒙兀兒興起' },
  { year: 1700, label_zh: '近世盛期', label_en: 'Late Early Modern', note: '清盛世、英印貿易、奧斯曼衰退、工業革命前夕' },

  // === 近現代 (1800+) ===
  { year: 1800, label_zh: '近現代開端', label_en: 'Modern Begins', note: '工業革命、民族國家興起', is_major: true },
  { year: 1815, label_zh: '拿破崙戰後', label_en: 'Post-Napoleonic', note: '維也納體系、英帝國巔峰前夕' },
  { year: 1914, label_zh: '帝國主義巔峰', label_en: 'Peak Imperialism', note: '一戰前夕、晚清、奧匈、奧斯曼末期' },
  { year: 1950, label_zh: '戰後與去殖民', label_en: 'Post-War', note: '冷戰、新興民族國家' },
  { year: 2000, label_zh: '當代', label_en: 'Contemporary', note: '全球化、資訊時代' },
  { year: 2026, label_zh: '現代', label_en: 'Modern', note: '當前邊界' },
]

export const YEAR_MIN = -4000
export const YEAR_MAX = 2026

/** 600 年制大分期段（用於上下文識別） */
export interface MajorEra {
  start: number
  end: number
  label_zh: string
  label_en: string
}
export const MAJOR_ERAS: MajorEra[] = [
  { start: -4000, end: -1201, label_zh: '石器-青銅時代', label_en: 'Stone & Bronze Age' },
  { start: -1200, end: -601,  label_zh: '古風時代',     label_en: 'Archaic Age' },
  { start: -600,  end: -1,    label_zh: '軸心時代',     label_en: 'Axial Age' },
  { start: 0,     end: 599,   label_zh: '古典時代',     label_en: 'Classical Age' },
  { start: 600,   end: 1199,  label_zh: '中古時代',     label_en: 'Medieval Age' },
  { start: 1200,  end: 1799,  label_zh: '近世',         label_en: 'Early Modern' },
  { start: 1800,  end: 2026,  label_zh: '近現代',       label_en: 'Modern' },
]

export function majorEraAt(year: number): MajorEra {
  return MAJOR_ERAS.find(e => year >= e.start && year <= e.end) || MAJOR_ERAS[MAJOR_ERAS.length - 1]
}

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
