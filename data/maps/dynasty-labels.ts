/**
 * 朝代標籤：把跨多朝代的同名 polygon 改顯示「{朝代}（{國家}）」。
 *
 * 使用：dynastyLabelAt(name, year) → '金雀花王朝（英格蘭）' | null
 *   若回 null，由上層 fallback 到 nameZhOf(name)。
 *
 * 設計：geojson 的 polygon 名稱常常只是地理稱呼（如 "Egypt", "England", "Persia"），
 *      跨朝代不變；此表把這些通用名按年代切成朝代區段。
 *
 * 朝代為主、國家為輔，配合 user 偏好「金雀花王朝（英國）」格式。
 * 9999 = 至今。
 */

export interface DynastyEntry {
  from: number
  to: number
  dynasty_zh: string
  country_zh: string
}

export const DYNASTY_LABELS: Record<string, DynastyEntry[]> = {
  // ===== 埃及 =====
  // geojson 的 "Egypt" polygon 跨度 -4000 → 9999，需切朝代
  'Egypt': [
    { from: -4000, to: -2687, dynasty_zh: '前王朝／早王朝', country_zh: '埃及' },
    { from: -2686, to: -2161, dynasty_zh: '古王國', country_zh: '埃及' },
    { from: -2160, to: -2056, dynasty_zh: '第一中間期', country_zh: '埃及' },
    { from: -2055, to: -1651, dynasty_zh: '中王國', country_zh: '埃及' },
    { from: -1650, to: -1551, dynasty_zh: '第二中間期（西克索）', country_zh: '埃及' },
    { from: -1550, to: -1070, dynasty_zh: '新王國', country_zh: '埃及' },
    { from: -1069, to: -665, dynasty_zh: '第三中間期', country_zh: '埃及' },
    { from: -664, to: -333, dynasty_zh: '後期王朝', country_zh: '埃及' },
    { from: -332, to: -31, dynasty_zh: '托勒密', country_zh: '埃及' },
    { from: -30, to: 640, dynasty_zh: '羅馬／拜占庭', country_zh: '埃及' },
    { from: 641, to: 868, dynasty_zh: '阿拉伯哈里發', country_zh: '埃及' },
    { from: 868, to: 1171, dynasty_zh: '圖倫／伊赫希迪／法蒂瑪', country_zh: '埃及' },
    { from: 1171, to: 1250, dynasty_zh: '阿尤布', country_zh: '埃及' },
    { from: 1250, to: 1517, dynasty_zh: '馬木留克', country_zh: '埃及' },
    { from: 1517, to: 1798, dynasty_zh: '奧斯曼省', country_zh: '埃及' },
    { from: 1798, to: 1801, dynasty_zh: '拿破崙占領', country_zh: '埃及' },
    { from: 1805, to: 1882, dynasty_zh: '穆罕默德‧阿里王朝', country_zh: '埃及' },
    { from: 1882, to: 1922, dynasty_zh: '英屬保護國', country_zh: '埃及' },
    { from: 1922, to: 1952, dynasty_zh: '王國', country_zh: '埃及' },
    { from: 1953, to: 9999, dynasty_zh: '共和國', country_zh: '埃及' },
  ],

  // ===== 英國 =====
  'England': [
    { from: 871, to: 1066, dynasty_zh: '盎格魯-撒克遜', country_zh: '英格蘭' },
    { from: 1066, to: 1153, dynasty_zh: '諾曼王朝', country_zh: '英格蘭' },
    { from: 1154, to: 1485, dynasty_zh: '金雀花王朝', country_zh: '英格蘭' },
    { from: 1485, to: 1529, dynasty_zh: '都鐸王朝', country_zh: '英格蘭' },
  ],
  'England and Ireland': [
    { from: 1530, to: 1602, dynasty_zh: '都鐸王朝', country_zh: '英格蘭與愛爾蘭' },
    { from: 1603, to: 1648, dynasty_zh: '斯圖亞特王朝', country_zh: '英格蘭與愛爾蘭' },
    { from: 1649, to: 1659, dynasty_zh: '共和（克倫威爾）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1660, to: 1707, dynasty_zh: '斯圖亞特復辟', country_zh: '英格蘭與愛爾蘭' },
    { from: 1707, to: 1714, dynasty_zh: '斯圖亞特王朝末', country_zh: '聯合王國' },
  ],
  'United Kingdom': [
    { from: 1714, to: 1800, dynasty_zh: '漢諾威王朝', country_zh: '聯合王國' },
    { from: 1801, to: 1900, dynasty_zh: '漢諾威王朝', country_zh: '聯合王國' },
    { from: 1901, to: 1916, dynasty_zh: '薩克森-科堡-哥達', country_zh: '聯合王國' },
    { from: 1917, to: 9999, dynasty_zh: '溫莎王朝', country_zh: '聯合王國' },
  ],
  'United Kingdom of Great Britain and Ireland': [
    { from: 1815, to: 1900, dynasty_zh: '漢諾威王朝', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1901, to: 1916, dynasty_zh: '薩克森-科堡-哥達', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1917, to: 1937, dynasty_zh: '溫莎王朝', country_zh: '大不列顛及愛爾蘭聯合王國' },
  ],
  'Hanover': [
    // 1714-1837 為英王同時兼漢諾威選侯／王（人身聯合）
    { from: 1715, to: 1814, dynasty_zh: '漢諾威選侯（與英共主）', country_zh: '德意志' },
    { from: 1815, to: 1837, dynasty_zh: '漢諾威王國（與英共主）', country_zh: '德意志' },
    { from: 1837, to: 1866, dynasty_zh: '漢諾威王國', country_zh: '德意志' },
  ],

  // ===== 波斯／伊朗 =====
  'Persia': [
    { from: 400, to: 651, dynasty_zh: '薩珊', country_zh: '波斯' },
    { from: 651, to: 820, dynasty_zh: '阿拉伯統治', country_zh: '波斯' },
    { from: 821, to: 1037, dynasty_zh: '塔希爾／薩法爾／薩曼／白益', country_zh: '波斯' },
    { from: 1037, to: 1194, dynasty_zh: '塞爾柱', country_zh: '波斯' },
    { from: 1194, to: 1256, dynasty_zh: '花剌子模', country_zh: '波斯' },
    { from: 1256, to: 1335, dynasty_zh: '伊兒汗', country_zh: '波斯' },
    { from: 1370, to: 1500, dynasty_zh: '帖木兒', country_zh: '波斯' },
    { from: 1501, to: 1735, dynasty_zh: '薩法維', country_zh: '波斯' },
    { from: 1736, to: 1795, dynasty_zh: '阿夫沙爾／贊德', country_zh: '波斯' },
    { from: 1796, to: 1919, dynasty_zh: '卡扎爾', country_zh: '波斯' },
  ],
  'Iran': [
    { from: 1920, to: 1925, dynasty_zh: '卡扎爾末', country_zh: '伊朗' },
    { from: 1925, to: 1979, dynasty_zh: '巴勒維', country_zh: '伊朗' },
    { from: 1979, to: 9999, dynasty_zh: '伊斯蘭共和國', country_zh: '伊朗' },
  ],

  // ===== 中國 =====
  // Han/Tang/Song/Ming/Qing 已有獨立 polygon 名（Han Empire / Tang Empire 等）保留原名即可
  // "China" polygon 在 geojson 中只覆蓋 1945+
  'China': [
    { from: 1945, to: 1948, dynasty_zh: '中華民國', country_zh: '中國' },
    { from: 1949, to: 9999, dynasty_zh: '中華人民共和國', country_zh: '中國' },
  ],
  // Manchu Empire 是清的別名
  'Manchu Empire': [
    { from: 1644, to: 1911, dynasty_zh: '清', country_zh: '滿洲帝國' },
  ],
  'Post-Ming Warlords': [
    { from: 1650, to: 1714, dynasty_zh: '南明／三藩之亂', country_zh: '中國' },
  ],

  // ===== 法國 =====
  'France': [
    { from: 843, to: 987, dynasty_zh: '加洛林王朝', country_zh: '法國' },
    { from: 987, to: 1328, dynasty_zh: '卡佩王朝', country_zh: '法國' },
    { from: 1328, to: 1589, dynasty_zh: '瓦盧瓦王朝', country_zh: '法國' },
    { from: 1589, to: 1791, dynasty_zh: '波旁王朝', country_zh: '法國' },
    { from: 1792, to: 1804, dynasty_zh: '第一共和', country_zh: '法國' },
    { from: 1804, to: 1814, dynasty_zh: '第一帝國（拿破崙）', country_zh: '法國' },
    { from: 1815, to: 1830, dynasty_zh: '波旁復辟', country_zh: '法國' },
    { from: 1830, to: 1848, dynasty_zh: '七月王朝（奧爾良）', country_zh: '法國' },
    { from: 1848, to: 1852, dynasty_zh: '第二共和', country_zh: '法國' },
    { from: 1852, to: 1870, dynasty_zh: '第二帝國', country_zh: '法國' },
    { from: 1870, to: 1939, dynasty_zh: '第三共和', country_zh: '法國' },
    { from: 1940, to: 1944, dynasty_zh: '維琪政權', country_zh: '法國' },
    { from: 1944, to: 1958, dynasty_zh: '第四共和', country_zh: '法國' },
    { from: 1958, to: 9999, dynasty_zh: '第五共和', country_zh: '法國' },
  ],
  'Kingdom of France': [
    { from: 987, to: 1328, dynasty_zh: '卡佩王朝', country_zh: '法蘭西王國' },
    { from: 1328, to: 1589, dynasty_zh: '瓦盧瓦王朝', country_zh: '法蘭西王國' },
  ],

  // ===== 西班牙 =====
  'Spain': [
    { from: 1469, to: 1516, dynasty_zh: '特拉斯塔馬拉（雙王）', country_zh: '西班牙' },
    { from: 1516, to: 1700, dynasty_zh: '哈布斯堡', country_zh: '西班牙' },
    { from: 1700, to: 1808, dynasty_zh: '波旁', country_zh: '西班牙' },
    { from: 1808, to: 1813, dynasty_zh: '波拿巴（拿破崙弟）', country_zh: '西班牙' },
    { from: 1814, to: 1873, dynasty_zh: '波旁復辟', country_zh: '西班牙' },
    { from: 1873, to: 1874, dynasty_zh: '第一共和', country_zh: '西班牙' },
    { from: 1874, to: 1930, dynasty_zh: '波旁復辟', country_zh: '西班牙' },
    { from: 1931, to: 1938, dynasty_zh: '第二共和', country_zh: '西班牙' },
    { from: 1939, to: 1975, dynasty_zh: '佛朗哥獨裁', country_zh: '西班牙' },
    { from: 1975, to: 9999, dynasty_zh: '波旁復辟（民主）', country_zh: '西班牙' },
  ],

  // ===== 義大利 =====
  'Italy': [
    { from: 1861, to: 1922, dynasty_zh: '薩伏依王朝（王國）', country_zh: '義大利' },
    { from: 1922, to: 1943, dynasty_zh: '法西斯', country_zh: '義大利王國' },
    { from: 1943, to: 1946, dynasty_zh: '戰後過渡', country_zh: '義大利' },
    { from: 1946, to: 9999, dynasty_zh: '共和', country_zh: '義大利' },
  ],

  // ===== 德國 =====
  'Germany': [
    { from: 1871, to: 1918, dynasty_zh: '德意志帝國（霍亨索倫）', country_zh: '德國' },
    { from: 1919, to: 1932, dynasty_zh: '威瑪共和', country_zh: '德國' },
    { from: 1933, to: 1945, dynasty_zh: '納粹第三帝國', country_zh: '德國' },
    { from: 1949, to: 1989, dynasty_zh: '西德', country_zh: '德國' },
    { from: 1990, to: 9999, dynasty_zh: '聯邦共和', country_zh: '德國' },
  ],

  // ===== 俄羅斯 =====
  'Russia': [
    { from: 1991, to: 9999, dynasty_zh: '俄羅斯聯邦', country_zh: '俄羅斯' },
  ],
  'Tsardom of Muscovy': [
    { from: 1547, to: 1721, dynasty_zh: '留里克／羅曼諾夫', country_zh: '俄羅斯沙皇國' },
  ],

  // ===== 印度 =====
  'India': [
    { from: 1783, to: 1857, dynasty_zh: '英屬東印度公司', country_zh: '印度' },
    { from: 1858, to: 1947, dynasty_zh: '英屬印度', country_zh: '印度' },
    { from: 1947, to: 9999, dynasty_zh: '共和', country_zh: '印度' },
  ],

  // ===== 日本 =====
  'Japan': [
    { from: 800, to: 1184, dynasty_zh: '平安／攝關（藤原）', country_zh: '日本' },
    { from: 1185, to: 1332, dynasty_zh: '鎌倉幕府', country_zh: '日本' },
    { from: 1333, to: 1567, dynasty_zh: '室町幕府', country_zh: '日本' },
    { from: 1568, to: 1602, dynasty_zh: '安土桃山', country_zh: '日本' },
    { from: 1603, to: 1867, dynasty_zh: '德川幕府', country_zh: '日本' },
    { from: 1868, to: 1911, dynasty_zh: '明治', country_zh: '日本' },
    { from: 1912, to: 1925, dynasty_zh: '大正', country_zh: '日本' },
    { from: 1926, to: 1944, dynasty_zh: '昭和（戰前）', country_zh: '日本' },
    { from: 1947, to: 9999, dynasty_zh: '戰後民主', country_zh: '日本' },
  ],
  'Imperial Japan': [
    { from: 1868, to: 1911, dynasty_zh: '明治', country_zh: '大日本帝國' },
    { from: 1912, to: 1925, dynasty_zh: '大正', country_zh: '大日本帝國' },
    { from: 1926, to: 1945, dynasty_zh: '昭和（戰前）', country_zh: '大日本帝國' },
  ],

  // ===== 韓國 =====
  'Korea': [
    { from: 918, to: 1391, dynasty_zh: '高麗', country_zh: '朝鮮半島' },
    { from: 1392, to: 1896, dynasty_zh: '朝鮮（李氏）', country_zh: '朝鮮半島' },
    { from: 1897, to: 1909, dynasty_zh: '大韓帝國', country_zh: '朝鮮半島' },
    { from: 1910, to: 1944, dynasty_zh: '日治', country_zh: '朝鮮半島' },
  ],

  // ===== 土耳其 =====
  'Turkey': [
    { from: 1938, to: 9999, dynasty_zh: '共和', country_zh: '土耳其' },
  ],
  'Ottoman Sultanate': [
    { from: 1920, to: 1922, dynasty_zh: '奧斯曼末（蘇丹政權）', country_zh: '土耳其' },
    { from: 1923, to: 1937, dynasty_zh: '凱末爾共和', country_zh: '土耳其' },
  ],

  // ===== 神聖羅馬帝國 — 主要朝代 =====
  'Holy Roman Empire': [
    { from: 919, to: 1024, dynasty_zh: '奧托王朝', country_zh: '神聖羅馬帝國' },
    { from: 1024, to: 1125, dynasty_zh: '薩利安王朝', country_zh: '神聖羅馬帝國' },
    { from: 1138, to: 1254, dynasty_zh: '霍亨斯陶芬', country_zh: '神聖羅馬帝國' },
    { from: 1273, to: 1437, dynasty_zh: '哈布斯堡（早期）／盧森堡', country_zh: '神聖羅馬帝國' },
    { from: 1438, to: 1740, dynasty_zh: '哈布斯堡', country_zh: '神聖羅馬帝國' },
    { from: 1745, to: 1806, dynasty_zh: '哈布斯堡-洛林', country_zh: '神聖羅馬帝國' },
  ],

  // ===== 奧斯曼 =====
  'Ottoman Empire': [
    { from: 1299, to: 1402, dynasty_zh: '崛起期', country_zh: '奧斯曼帝國' },
    { from: 1413, to: 1566, dynasty_zh: '擴張期（蘇萊曼黃金時代）', country_zh: '奧斯曼帝國' },
    { from: 1566, to: 1683, dynasty_zh: '停滯期', country_zh: '奧斯曼帝國' },
    { from: 1683, to: 1839, dynasty_zh: '衰退期', country_zh: '奧斯曼帝國' },
    { from: 1839, to: 1908, dynasty_zh: '坦志麥特改革', country_zh: '奧斯曼帝國' },
    { from: 1908, to: 1919, dynasty_zh: '青年土耳其', country_zh: '奧斯曼帝國' },
  ],

  // ===== 拜占庭 =====
  'Byzantine Empire': [
    { from: 330, to: 717, dynasty_zh: '早期', country_zh: '東羅馬' },
    { from: 717, to: 867, dynasty_zh: '伊蘇里亞／阿摩里亞', country_zh: '拜占庭' },
    { from: 867, to: 1056, dynasty_zh: '馬其頓王朝', country_zh: '拜占庭' },
    { from: 1056, to: 1185, dynasty_zh: '科穆寧', country_zh: '拜占庭' },
    { from: 1185, to: 1261, dynasty_zh: '安格洛斯／流亡', country_zh: '拜占庭' },
    { from: 1261, to: 1453, dynasty_zh: '巴列奧略', country_zh: '拜占庭' },
  ],

  // ===== 羅馬 =====
  'Roman Empire': [
    { from: -27, to: 68, dynasty_zh: '朱里亞-克勞狄', country_zh: '羅馬帝國' },
    { from: 69, to: 96, dynasty_zh: '弗拉維', country_zh: '羅馬帝國' },
    { from: 96, to: 192, dynasty_zh: '涅爾瓦-安東尼（五賢帝）', country_zh: '羅馬帝國' },
    { from: 193, to: 235, dynasty_zh: '塞維魯', country_zh: '羅馬帝國' },
    { from: 235, to: 284, dynasty_zh: '三世紀危機', country_zh: '羅馬帝國' },
    { from: 284, to: 395, dynasty_zh: '戴克里先／君士坦丁', country_zh: '羅馬帝國' },
  ],
  'Eastern Roman Empire': [
    { from: 395, to: 717, dynasty_zh: '早期（東羅馬）', country_zh: '東羅馬' },
  ],
  'Western Roman Empire': [
    { from: 395, to: 476, dynasty_zh: '西羅馬', country_zh: '西羅馬' },
  ],

  // ===== 蒙兀兒 =====
  'Mughal Empire': [
    { from: 1526, to: 1605, dynasty_zh: '巴布爾-阿克巴', country_zh: '蒙兀兒帝國' },
    { from: 1605, to: 1707, dynasty_zh: '賈漢吉爾-奧朗則布（巔峰）', country_zh: '蒙兀兒帝國' },
    { from: 1707, to: 1857, dynasty_zh: '衰退期', country_zh: '蒙兀兒帝國' },
  ],

  // ===== 薩法維 =====
  'Safavid Empire': [
    { from: 1501, to: 1629, dynasty_zh: '伊斯瑪儀-阿巴斯（巔峰）', country_zh: '薩法維' },
    { from: 1629, to: 1736, dynasty_zh: '衰退期', country_zh: '薩法維' },
  ],

  // ===== 中國朝代細分（補在已單獨命名的 polygon 上）=====
  'Han': [
    { from: -202, to: 9, dynasty_zh: '西漢', country_zh: '中國' },
    { from: 25, to: 220, dynasty_zh: '東漢', country_zh: '中國' },
  ],
  'Han Empire': [
    { from: -202, to: 9, dynasty_zh: '西漢', country_zh: '中國' },
    { from: 25, to: 220, dynasty_zh: '東漢', country_zh: '中國' },
  ],
}

/**
 * 查詢某 polygon 名稱在某年的朝代標籤。
 * @returns '金雀花王朝（英格蘭）' | null
 */
export function dynastyLabelAt(name: string, year: number): string | null {
  const list = DYNASTY_LABELS[name]
  if (!list) return null
  for (const e of list) {
    if (year >= e.from && year <= e.to) {
      return `${e.dynasty_zh}（${e.country_zh}）`
    }
  }
  return null
}
