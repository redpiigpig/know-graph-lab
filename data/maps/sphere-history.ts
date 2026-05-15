/**
 * 全球八大人文宗教界域 — 各文化圈的歷史時期資料
 *
 * 用於：
 *   - 資訊列表（RealmInfoList.vue）「歷史期間」展開區
 *   - 未來：地圖在不同年份時，根據 sphere_id + valid_from/valid_to 過濾與上色
 *
 * 年份規則：天文年（含 0 年）；BCE = 負數，CE = 正數。
 *   -3500 → 公元前 3501 年
 *   1     → 公元 1 年
 *   2026  → 至今
 * 9999 用作「至今／持續中」哨兵值。
 */

export interface SphereHistoryEntry {
  /** 時期標籤（如「蘇美時代」「漢帝國」「奧斯曼時期」） */
  period_label: string
  period_label_en?: string
  /** 起始年（天文年；BCE 為負） */
  year_from: number
  /** 結束年（天文年；9999 = 持續至今） */
  year_to: number
  /** 該時期主要政治體 / 朝代 */
  states?: string[]
  /** 該時期主要城市 / 地名 */
  places?: string[]
  /** 該時期主要宗教 / 信仰系統 */
  faiths?: string[]
  /** 補充說明 */
  note?: string
}

/** sphere.id → 該文化圈的歷史時期序列（按時間順序） */
export const SPHERE_HISTORY: Record<string, SphereHistoryEntry[]> = {
  // ========== 中央界域 ==========
  'mesopotamian-levantine': [
    { period_label: '蘇美城邦', period_label_en: 'Sumerian City-States', year_from: -3500, year_to: -2334,
      states: ['烏魯克', '烏爾', '拉格什', '基什', '尼普爾', '艾比哈', '埃利都'],
      places: ['美索不達米亞南部', '幼發拉底-底格里斯河三角洲'],
      faiths: ['蘇美多神教（安、恩利爾、伊南娜）'],
      note: '楔形文字發明、城邦競爭、《吉爾伽美什史詩》原型', },
    { period_label: '阿卡德帝國', period_label_en: 'Akkadian Empire', year_from: -2334, year_to: -2154,
      states: ['阿卡德'], places: ['阿卡德城', '蘇美故地'],
      faiths: ['蘇美-阿卡德融合多神教'], note: '第一個閃族統一帝國', },
    { period_label: '烏爾第三王朝', period_label_en: 'Ur III', year_from: -2112, year_to: -2004,
      states: ['烏爾'], places: ['烏爾'], note: '蘇美復興、巨型階梯神塔（ziggurat）建立', },
    { period_label: '古巴比倫', period_label_en: 'Old Babylonian', year_from: -1900, year_to: -1595,
      states: ['古巴比倫', '馬里', '埃什嫩納', '亞述'], places: ['巴比倫城', '馬里'],
      faiths: ['馬爾杜克崇拜', '希伯來族長傳說起源'],
      note: '《漢摩拉比法典》、亞伯拉罕傳說背景', },
    { period_label: '青銅時代晚期', period_label_en: 'Late Bronze Age', year_from: -1595, year_to: -1200,
      states: ['加喜特巴比倫', '中亞述', '米坦尼', '赫梯（敘北）'],
      places: ['亞述城', '尼尼微', '阿馬爾納外交圈'], note: '青銅時代列國體系', },
    { period_label: '鐵器時代列國', period_label_en: 'Iron Age Levant', year_from: -1200, year_to: -911,
      states: ['新赫梯', '亞蘭', '腓尼基城邦', '希伯來王國', '非利士', '迦南', '烏拉爾圖'],
      places: ['推羅', '西頓', '比布魯斯', '耶路撒冷', '大馬士革'],
      faiths: ['以色列雅威信仰', '腓尼基巴力'], note: '腓尼基字母散播、希伯來王國形成', },
    { period_label: '新亞述帝國', period_label_en: 'Neo-Assyrian Empire', year_from: -911, year_to: -609,
      states: ['新亞述'], places: ['尼尼微', '尼姆魯德', '阿淑爾'], note: '第一個跨地域大帝國', },
    { period_label: '新巴比倫與米底', period_label_en: 'Neo-Babylonian & Median', year_from: -626, year_to: -539,
      states: ['新巴比倫', '米底'], places: ['巴比倫城（空中花園）'],
      note: '尼布甲尼撒二世、猶太人巴比倫之囚', },
    { period_label: '波斯帝國時期', period_label_en: 'Persian Era', year_from: -539, year_to: -330,
      states: ['阿契美尼德波斯（轄區）'], faiths: ['瑣羅亞斯德教官方', '猶太教第二聖殿時期'],
      note: '居魯士詔書、第二聖殿建立', },
    { period_label: '希臘化時期', period_label_en: 'Hellenistic', year_from: -330, year_to: -64,
      states: ['塞琉古帝國', '哈斯蒙尼猶太'], places: ['安條克', '塞琉西亞', '巴比倫'],
      faiths: ['希臘化多神教', '猶太教馬加比起義'], },
    { period_label: '羅馬與帕提亞/薩珊', period_label_en: 'Roman vs Parthian/Sassanid', year_from: -64, year_to: 636,
      states: ['羅馬敘利亞行省', '帕提亞', '薩珊（東部）', '加薩尼', '拉赫姆'],
      places: ['安條克', '帕米拉', '泰西封'],
      faiths: ['基督教興起', '景教東傳', '摩尼教', '猶太教拉比化'], },
    { period_label: '伊斯蘭哈里發', period_label_en: 'Islamic Caliphates', year_from: 636, year_to: 1258,
      states: ['正統哈里發', '伍麥亞', '阿巴斯', '法蒂瑪'],
      places: ['大馬士革', '巴格達', '耶路撒冷'],
      faiths: ['伊斯蘭教（遜尼/什葉分裂）', '東方基督教存續'], note: '阿拉伯化、伊斯蘭化巔峰', },
    { period_label: '蒙古至馬木留克', period_label_en: 'Mongol to Mamluk', year_from: 1258, year_to: 1517,
      states: ['伊兒汗國', '馬木留克'], places: ['巴格達陷落', '開羅'], note: '阿巴斯哈里發終結', },
    { period_label: '奧斯曼時期', period_label_en: 'Ottoman Era', year_from: 1517, year_to: 1918,
      states: ['奧斯曼帝國'], places: ['伊斯坦堡（行政中心）', '大馬士革', '巴格達省', '耶路撒冷'],
      note: '長期穩定統治四百年', },
    { period_label: '現代國家', period_label_en: 'Modern States', year_from: 1918, year_to: 9999,
      states: ['伊拉克', '敘利亞', '黎巴嫩', '以色列', '巴勒斯坦', '約旦'],
      note: '英法委任統治後形成的民族國家', },
  ],

  // ========== 東方界域 ==========
  'han': [
    { period_label: '夏（傳說）', period_label_en: 'Xia (Legendary)', year_from: -2070, year_to: -1600,
      states: ['夏'], places: ['二里頭'], note: '考古上對應二里頭文化', },
    { period_label: '商', period_label_en: 'Shang Dynasty', year_from: -1600, year_to: -1046,
      states: ['商'], places: ['殷墟（安陽）', '鄭州', '偃師'],
      faiths: ['上帝崇拜', '祖先祭祀', '甲骨占卜'], note: '甲骨文成熟、青銅禮器', },
    { period_label: '西周', period_label_en: 'Western Zhou', year_from: -1046, year_to: -771,
      states: ['西周'], places: ['鎬京', '洛邑'], faiths: ['天命觀', '宗周禮樂'], },
    { period_label: '春秋', period_label_en: 'Spring and Autumn', year_from: -771, year_to: -476,
      states: ['周王室', '齊', '晉', '楚', '秦', '吳', '越', '鄭', '宋', '魯'],
      places: ['洛邑（東周）'], faiths: ['百家爭鳴前夕、孔子'], },
    { period_label: '戰國', period_label_en: 'Warring States', year_from: -475, year_to: -221,
      states: ['秦', '楚', '齊', '燕', '趙', '魏', '韓'],
      faiths: ['儒、墨、道、法、名、陰陽諸子百家'], },
    { period_label: '秦', period_label_en: 'Qin Dynasty', year_from: -221, year_to: -206,
      states: ['秦帝國'], places: ['咸陽'], note: '統一文字、度量衡；焚書坑儒', },
    { period_label: '漢', period_label_en: 'Han Dynasty', year_from: -206, year_to: 220,
      states: ['西漢', '新莽', '東漢'], places: ['長安', '洛陽'],
      faiths: ['獨尊儒術', '佛教傳入', '黃老／早期道教'], note: '絲綢之路、儒家國教化', },
    { period_label: '三國兩晉南北朝', period_label_en: 'Three Kingdoms to Southern-Northern', year_from: 220, year_to: 589,
      states: ['魏', '蜀', '吳', '西晉', '東晉', '十六國', '南朝', '北朝'],
      faiths: ['佛教漢化深入', '道教教團化', '玄學'], },
    { period_label: '隋唐', period_label_en: 'Sui-Tang', year_from: 589, year_to: 907,
      states: ['隋', '唐'], places: ['長安', '洛陽'],
      faiths: ['佛教全盛（八宗）', '景教/祆教/摩尼教入唐'], note: '中華文化的世界主義巔峰', },
    { period_label: '五代十國', period_label_en: 'Five Dynasties Ten Kingdoms', year_from: 907, year_to: 960, },
    { period_label: '宋', period_label_en: 'Song Dynasty', year_from: 960, year_to: 1279,
      states: ['北宋', '南宋'], places: ['開封', '臨安（杭州）'],
      faiths: ['新儒學（理學）'], note: '商業革命、印刷術普及', },
    { period_label: '元', period_label_en: 'Yuan Dynasty', year_from: 1271, year_to: 1368,
      states: ['元'], places: ['大都（北京）'], note: '蒙古統治下的漢地', },
    { period_label: '明', period_label_en: 'Ming Dynasty', year_from: 1368, year_to: 1644,
      states: ['明'], places: ['南京', '北京'],
      faiths: ['陽明心學', '天主教利瑪竇'], },
    { period_label: '清', period_label_en: 'Qing Dynasty', year_from: 1644, year_to: 1912,
      states: ['清'], places: ['北京'], note: '滿洲統治、晚期被迫開放', },
    { period_label: '民國與當代', period_label_en: 'Republican & Contemporary', year_from: 1912, year_to: 9999,
      states: ['中華民國', '中華人民共和國'], },
  ],
}

/** 拿一個 sphere 的歷史時期，若無資料回 [] */
export function historyForSphere(sphereId: string): SphereHistoryEntry[] {
  return SPHERE_HISTORY[sphereId] || []
}

/** 找出某 sphere 在指定年份「當下」的時期（若年份在某時期內則回傳） */
export function periodAt(sphereId: string, year: number): SphereHistoryEntry | undefined {
  const hist = SPHERE_HISTORY[sphereId]
  if (!hist) return undefined
  return hist.find(e => year >= e.year_from && year <= e.year_to)
}
