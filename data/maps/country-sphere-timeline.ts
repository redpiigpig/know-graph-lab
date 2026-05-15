/**
 * 國家 × 年代 → 文化圈時序表
 *
 * 重點原則（依使用者「七階段分析」）：
 *   - 文化圈跟「地理區域」綁定，**不會被帝國覆寫**
 *   - 阿拉伯大征服／奧斯曼征服等，被征服地的「底層文化圈身分」不變
 *   - 阿拉伯帝國 polygon 橫跨多個文化圈：阿拉伯（半島）+ 兩河-黎凡特 + 埃及 + 波斯
 *   - 文化圈有出現時間，-4000 BCE 只有蘇美一個文化圈
 *
 * 年份：天文年（BCE 為負；9999 = 至今）
 *
 * 使用：sphereForCountryAtYear(iso, year) → sphere_id | null
 *   - null 表示該國該年「尚未進入文字／國家文化圈」（地圖顯示為灰底口傳部落）
 */

export interface SphereTimelineEntry {
  /** 起始年（天文年；BCE 為負） — 該 sphere 從此年起接手該國 */
  from: number
  /** 文化圈 id */
  sphere: string
  /** 補充說明 */
  note?: string
}

/**
 * 詳細時序表：以 ISO_A3 為 key，按時間順序排列的 sphere 變遷。
 * 中央界域國家有完整時序；其他界域國家以單一 sphere（從 valid_from 起）為主。
 *
 * 注意：admin_1 級的細分（如伊拉克南北 = 巴比倫 vs 亞述；利比亞東西）
 * 目前用整國代表性 sphere，犧牲精度換取簡單。下一輪可加 admin_1 細分。
 */
export const COUNTRY_SPHERE_TIMELINE: Record<string, SphereTimelineEntry[]> = {
  // ===== 中央界域：詳細時序 =====
  IRQ: [
    { from: -4000, sphere: 'sumerian', note: '蘇美城邦' },
    { from: -2334, sphere: 'sumero-akkadian', note: '阿卡德／烏爾三王朝／古巴比倫' },
    { from: -1200, sphere: 'assyrian', note: '新亞述帝國（-911 後達巔峰）' },
    { from: -626, sphere: 'babylonian', note: '新巴比倫帝國' },
    { from: -539, sphere: 'mesopotamian-levantine', note: '波斯大縫合' },
  ],
  SYR: [
    // 敘利亞主要是上美索不達米亞 + 北黎凡特，較複雜
    { from: -3000, sphere: 'canaan', note: '北部迦南（烏加里特）+ 美索不達米亞邊緣' },
    { from: -2334, sphere: 'sumero-akkadian', note: '埃布拉、馬里納入閃族圈' },
    { from: -1200, sphere: 'levant', note: '亞蘭城邦' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  LBN: [
    { from: -3000, sphere: 'canaan', note: '比布魯斯、推羅、西頓' },
    { from: -1200, sphere: 'levant', note: '腓尼基城邦' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  ISR: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant', note: '希伯來王國' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  PSE: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  JOR: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  EGY: [
    { from: -3500, sphere: 'egyptian', note: '前王朝；統一於 -3100' },
  ],
  SDN: [
    { from: -2500, sphere: 'egyptian', note: '庫施／努比亞納入埃及文化圈' },
  ],
  LBY: [
    // 西部（的黎波里塔尼亞-費贊）腓尼基；東部（昔蘭尼加）希臘/埃及
    // 簡化為迦太基-馬格里布
    { from: -1100, sphere: 'carthaginian-maghreb' },
  ],
  TUN: [{ from: -1100, sphere: 'carthaginian-maghreb', note: '腓尼基殖民' }],
  DZA: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  MAR: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  TUR: [
    { from: -2334, sphere: 'anatolia', note: '赫梯' },
    { from: -547, sphere: 'aegean-asia-minor', note: '波斯吞併呂底亞 → 希臘化／拜占庭縫合' },
    { from: 1071, sphere: 'anatolia', note: '曼齊克特戰役後突厥湧入' },
  ],
  GRC: [
    { from: -2700, sphere: 'aegean-asia-minor', note: '米諾斯 → 邁錫尼 → 希臘城邦 → 拜占庭' },
  ],
  CYP: [{ from: -2700, sphere: 'aegean-asia-minor' }],
  IRN: [
    { from: -3200, sphere: 'persian', note: '埃蘭原始文字' },
  ],
  AFG: [{ from: -2000, sphere: 'persian', note: '巴克特里亞（中西部）' }],
  TJK: [{ from: -2000, sphere: 'persian' }],
  ARM: [
    { from: -3400, sphere: 'caucasus', note: '庫拉-阿拉斯青銅' },
  ],
  GEO: [{ from: -3400, sphere: 'caucasus' }],
  AZE: [{ from: -3400, sphere: 'caucasus' }],
  YEM: [
    { from: -1200, sphere: 'arabian', note: '示巴等南阿拉伯王國' },
  ],
  // 沙烏地半島中北部：游牧期 → 622 CE 伊斯蘭擴張
  SAU: [
    { from: -1200, sphere: 'arabian', note: '南阿拉伯部落、納巴泰；伊斯蘭出現後全面整合' },
  ],
  OMN: [{ from: 622, sphere: 'arabian', note: '伊斯蘭擴張' }],
  BHR: [{ from: 622, sphere: 'arabian' }],
  QAT: [{ from: 622, sphere: 'arabian' }],
  ARE: [{ from: 622, sphere: 'arabian' }],
  KWT: [{ from: 622, sphere: 'arabian' }],

  // ===== 東方界域 =====
  CHN: [
    { from: -2070, sphere: 'han', note: '夏（傳說）' },
  ],
  PAK: [{ from: -2600, sphere: 'indian', note: '哈拉帕／印度河文明' }],
  IND: [{ from: -2600, sphere: 'indian' }],
  NPL: [{ from: -1500, sphere: 'indian' }],
  BGD: [{ from: -1500, sphere: 'indian' }],
  LKA: [{ from: -500, sphere: 'indian' }],
  MDV: [{ from: -500, sphere: 'indian' }],
  BTN: [{ from: -1000, sphere: 'tibetan' }],

  // ===== 亞太界域 =====
  TWN: [{ from: -3000, sphere: 'banua', note: '大坌坑、南島起源地' }],
  IDN: [{ from: -3000, sphere: 'banua', note: '南島擴散' }],
  MYS: [{ from: -2000, sphere: 'banua' }],
  SGP: [{ from: -2000, sphere: 'banua' }],
  BRN: [{ from: -2000, sphere: 'banua' }],
  PHL: [{ from: -3000, sphere: 'banua' }],
  TLS: [{ from: -3000, sphere: 'banua' }],
  KHM: [{ from: -200, sphere: 'mekong', note: '扶南/吳哥' }],
  VNM: [{ from: -200, sphere: 'mekong' }],
  THA: [{ from: -200, sphere: 'mekong' }],
  LAO: [{ from: -200, sphere: 'mekong' }],
  MMR: [{ from: -200, sphere: 'mekong', note: '緬甸（西部與印度文化圈相鄰）' }],
  KOR: [{ from: -1000, sphere: 'kuroshio', note: '韓國銅器時代' }],
  PRK: [{ from: -1000, sphere: 'kuroshio' }],
  JPN: [{ from: -1000, sphere: 'kuroshio', note: '繩文晚期到彌生' }],
  AUS: [{ from: -50000, sphere: 'australasian', note: '澳洲原住民' }],
  NZL: [{ from: 1280, sphere: 'australasian', note: '毛利' }],
  PNG: [{ from: -1500, sphere: 'pacific', note: '拉皮塔' }],
  FJI: [{ from: -1500, sphere: 'pacific' }],
  WSM: [{ from: -1500, sphere: 'pacific' }],
  TON: [{ from: -1500, sphere: 'pacific' }],
  VUT: [{ from: -1500, sphere: 'pacific' }],
  SLB: [{ from: -1500, sphere: 'pacific' }],
  PLW: [{ from: -1500, sphere: 'pacific' }],
  FSM: [{ from: -1500, sphere: 'pacific' }],
  MHL: [{ from: -1500, sphere: 'pacific' }],
  KIR: [{ from: 0, sphere: 'pacific' }],
  NRU: [{ from: 0, sphere: 'pacific' }],
  TUV: [{ from: 0, sphere: 'pacific' }],

  // ===== 拉美界域 =====
  MEX: [{ from: -1500, sphere: 'mesoamerican', note: '奧爾梅克' }],
  GTM: [{ from: -1500, sphere: 'mesoamerican' }],
  BLZ: [{ from: -1500, sphere: 'mesoamerican' }],
  HND: [{ from: -1500, sphere: 'mesoamerican' }],
  SLV: [{ from: -1500, sphere: 'mesoamerican' }],
  NIC: [{ from: -1500, sphere: 'mesoamerican' }],
  CRI: [{ from: -1500, sphere: 'mesoamerican' }],
  PAN: [{ from: -1500, sphere: 'mesoamerican' }],
  PER: [{ from: -3000, sphere: 'andean', note: '諾爾特奇科／卡拉爾' }],
  BOL: [{ from: -3000, sphere: 'andean' }],
  ECU: [{ from: -3000, sphere: 'andean' }],
  COL: [{ from: -3000, sphere: 'andean' }],
  CUB: [{ from: -2000, sphere: 'caribbean' }],
  DOM: [{ from: -2000, sphere: 'caribbean' }],
  HTI: [{ from: -2000, sphere: 'caribbean' }],
  JAM: [{ from: -2000, sphere: 'caribbean' }],
  BHS: [{ from: -2000, sphere: 'caribbean' }],
  VEN: [{ from: -2000, sphere: 'caribbean' }],
  GUY: [{ from: -2000, sphere: 'caribbean' }],
  SUR: [{ from: -2000, sphere: 'caribbean' }],
  CHL: [{ from: -2000, sphere: 'southern-cone' }],
  ARG: [{ from: -2000, sphere: 'southern-cone' }],
  PRY: [{ from: -2000, sphere: 'southern-cone' }],
  URY: [{ from: -2000, sphere: 'southern-cone' }],
  BRA: [{ from: -3000, sphere: 'amazonian-brazilian' }],

  // ===== 西方界域 =====
  ITA: [
    { from: -1000, sphere: 'latin-cultural', note: '伊特魯里亞 → 羅馬 → 拉丁中心' },
  ],
  VAT: [{ from: 754, sphere: 'latin-cultural' }],
  SMR: [{ from: 301, sphere: 'latin-cultural' }],
  ESP: [{ from: -1100, sphere: 'latin-cultural', note: '腓尼基殖民 → 羅馬西班牙 → 中世紀' }],
  PRT: [{ from: -1100, sphere: 'latin-cultural' }],
  MLT: [{ from: -800, sphere: 'latin-cultural' }],
  MCO: [{ from: -700, sphere: 'latin-cultural' }],
  AND: [{ from: 800, sphere: 'latin-cultural' }],
  MKD: [{ from: -1500, sphere: 'balkan' }],
  BGR: [{ from: -1500, sphere: 'balkan' }],
  SRB: [{ from: -1500, sphere: 'balkan' }],
  ROU: [{ from: -1500, sphere: 'balkan' }],
  ALB: [{ from: -1500, sphere: 'balkan' }],
  HRV: [{ from: 600, sphere: 'balkan' }],
  BIH: [{ from: 600, sphere: 'balkan' }],
  SVN: [{ from: 600, sphere: 'balkan' }],
  MNE: [{ from: 600, sphere: 'balkan' }],
  KOS: [{ from: 600, sphere: 'balkan' }],
  MDA: [{ from: 600, sphere: 'balkan' }],
  FRA: [{ from: -800, sphere: 'gallic-french', note: '凱爾特高盧' }],
  GBR: [{ from: -800, sphere: 'british-celtic', note: '凱爾特不列顛' }],
  IRL: [{ from: -800, sphere: 'british-celtic' }],
  DEU: [{ from: -500, sphere: 'central-european', note: '凱爾特/日耳曼' }],
  AUT: [{ from: -500, sphere: 'central-european' }],
  CHE: [{ from: -500, sphere: 'central-european' }],
  CZE: [{ from: -500, sphere: 'central-european' }],
  HUN: [{ from: -500, sphere: 'central-european', note: '匈牙利人 895 CE 入住，前期凱爾特/羅馬/斯拉夫' }],
  SVK: [{ from: -500, sphere: 'central-european' }],
  LIE: [{ from: 100, sphere: 'central-european' }],
  BEL: [{ from: -500, sphere: 'low-countries' }],
  NLD: [{ from: -500, sphere: 'low-countries' }],
  LUX: [{ from: -500, sphere: 'low-countries' }],
  POL: [{ from: 500, sphere: 'lublin', note: '西斯拉夫部落 → 波蘭王國' }],
  LTU: [{ from: 500, sphere: 'lublin' }],
  LVA: [{ from: 500, sphere: 'lublin' }],
  DNK: [{ from: -1000, sphere: 'nordic-livonian' }],
  SWE: [{ from: -1000, sphere: 'nordic-livonian' }],
  NOR: [{ from: -1000, sphere: 'nordic-livonian' }],
  FIN: [{ from: -1000, sphere: 'nordic-livonian' }],
  ISL: [{ from: 874, sphere: 'nordic-livonian', note: '維京殖民' }],
  EST: [{ from: -1000, sphere: 'nordic-livonian' }],

  // ===== 南方界域 =====
  ETH: [{ from: -1000, sphere: 'ethiopian', note: '達莫 → 阿克蘇姆' }],
  ERI: [{ from: -1000, sphere: 'ethiopian' }],
  MLI: [{ from: -1000, sphere: 'west-african-sahel' }],
  SEN: [{ from: -1000, sphere: 'west-african-sahel' }],
  NER: [{ from: -1000, sphere: 'west-african-sahel' }],
  CPV: [{ from: 1500, sphere: 'west-african-sahel' }],
  BFA: [{ from: -1000, sphere: 'west-african-sahel' }],
  GIN: [{ from: -1000, sphere: 'west-african-sahel' }],
  GMB: [{ from: -1000, sphere: 'west-african-sahel' }],
  GNB: [{ from: -1000, sphere: 'west-african-sahel' }],
  MRT: [{ from: -1000, sphere: 'west-african-sahel' }],
  TCD: [{ from: -1000, sphere: 'west-african-sahel' }],
  NGA: [{ from: 500, sphere: 'gulf-of-guinea', note: '伊費/貝寧/奧約等南部；北部薩赫爾' }],
  GHA: [{ from: 500, sphere: 'gulf-of-guinea' }],
  CIV: [{ from: 500, sphere: 'gulf-of-guinea' }],
  TGO: [{ from: 500, sphere: 'gulf-of-guinea' }],
  BEN: [{ from: 500, sphere: 'gulf-of-guinea' }],
  LBR: [{ from: 500, sphere: 'gulf-of-guinea' }],
  SLE: [{ from: 500, sphere: 'gulf-of-guinea' }],
  KEN: [{ from: 800, sphere: 'east-african-swahili', note: '斯瓦希里城邦' }],
  TZA: [{ from: 800, sphere: 'east-african-swahili' }],
  UGA: [{ from: 800, sphere: 'east-african-swahili' }],
  RWA: [{ from: 800, sphere: 'east-african-swahili' }],
  BDI: [{ from: 800, sphere: 'east-african-swahili' }],
  SOM: [{ from: 800, sphere: 'east-african-swahili' }],
  DJI: [{ from: 800, sphere: 'east-african-swahili' }],
  COM: [{ from: 800, sphere: 'east-african-swahili' }],
  MDG: [{ from: 500, sphere: 'east-african-swahili' }],
  SSD: [{ from: 800, sphere: 'east-african-swahili' }],
  COD: [{ from: 500, sphere: 'central-african-congolese', note: '班圖遷徙、剛果王國' }],
  COG: [{ from: 500, sphere: 'central-african-congolese' }],
  CMR: [{ from: 500, sphere: 'central-african-congolese' }],
  CAF: [{ from: 500, sphere: 'central-african-congolese' }],
  GAB: [{ from: 500, sphere: 'central-african-congolese' }],
  GNQ: [{ from: 500, sphere: 'central-african-congolese' }],
  STP: [{ from: 1500, sphere: 'central-african-congolese' }],
  ZWE: [{ from: 500, sphere: 'southern-african-bantu', note: '大津巴布韋／穆塔帕' }],
  MOZ: [{ from: 500, sphere: 'southern-african-bantu' }],
  ZAF: [{ from: 500, sphere: 'southern-african-bantu' }],
  AGO: [{ from: 500, sphere: 'southern-african-bantu' }],
  NAM: [{ from: 500, sphere: 'southern-african-bantu' }],
  BWA: [{ from: 500, sphere: 'southern-african-bantu' }],
  ZMB: [{ from: 500, sphere: 'southern-african-bantu' }],
  MWI: [{ from: 500, sphere: 'southern-african-bantu' }],
  LSO: [{ from: 500, sphere: 'southern-african-bantu' }],
  SWZ: [{ from: 500, sphere: 'southern-african-bantu' }],

  // ===== 北方界域 =====
  UZB: [{ from: -700, sphere: 'turanian-turkic', note: '斯基泰／粟特／突厥/帖木兒' }],
  TKM: [{ from: -700, sphere: 'turanian-turkic' }],
  KGZ: [{ from: -700, sphere: 'turanian-turkic' }],
  KAZ: [{ from: -700, sphere: 'turanian-turkic' }],
  UKR: [{ from: 862, sphere: 'russian-tatar', note: '基輔羅斯' }],
  BLR: [{ from: 862, sphere: 'russian-tatar' }],
  RUS: [{ from: 862, sphere: 'russian-tatar', note: '基輔羅斯 → 莫斯科 → 帝國' }],
  MNG: [{ from: -200, sphere: 'mongolic-tungusic', note: '匈奴' }],

  // ===== 北美界域 =====
  USA: [{ from: 1607, sphere: 'anglo-american', note: 'Jamestown' }],
  CAN: [{ from: 1534, sphere: 'franco-american', note: 'Cartier' }],
  GRL: [{ from: -2500, sphere: 'arctic', note: '多塞特、圖勒' }],
}

/**
 * 查找該國該年所屬的文化圈。
 * 若無對應 → null（地圖該國顯示為灰底「口傳部落／非文字社會」）
 */
export function sphereForCountryAtYear(iso: string, year: number): string | null {
  const tl = COUNTRY_SPHERE_TIMELINE[iso]
  if (!tl) return null
  let active: string | null = null
  for (const entry of tl) {
    if (entry.from <= year) active = entry.sphere
    else break
  }
  return active
}

/**
 * 找出該年該 sphere 涵蓋的所有國家（用於計算 sphere 標籤的 centroid）。
 */
export function countriesInSphereAtYear(sphereId: string, year: number): string[] {
  const out: string[] = []
  for (const [iso, tl] of Object.entries(COUNTRY_SPHERE_TIMELINE)) {
    let active: string | null = null
    for (const entry of tl) {
      if (entry.from <= year) active = entry.sphere
      else break
    }
    if (active === sphereId) out.push(iso)
  }
  return out
}
