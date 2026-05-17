#!/usr/bin/env node
/**
 * Stage 1 — City-Hull Fine Polygon Builder（多帝國通用版）
 *
 * 接續 city_hull_abbasid.mjs 的 POC。把多個帝國的密集年份 polygon
 * 合併輸出到 public/maps/fine-polygons.geojson，供 HistoricalBordersMap
 * 在歷史邊圖上以細粒度覆蓋 historical-basemaps 的粗粒度 snapshots。
 *
 * 做法：
 *   - CITIES：共享城市 lat/lon 資料庫
 *   - EMPIRES：每帝國的 polygon_name + CONTROL_BY_YEAR + 中文名
 *   - Graham scan convex hull → GeoJSON Polygon
 *   - properties.name 必須對齊 historical-states.geojson 的 polygon name
 *     （runtime 用 name 比對排除粗 polygon）
 *
 * Run: node scripts/build_city_hull_polygons.mjs
 * Output: public/maps/fine-polygons.geojson
 */

import { writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

// ===== 共享城市 lat/lon（lon, lat for GeoJSON）=====
const CITIES = {
  // 中東／伊斯蘭核心
  'Baghdad':        [44.42, 33.34],
  'Kufa':           [44.40, 32.03],
  'Basra':          [47.78, 30.50],
  'Mosul':          [43.13, 36.34],
  'Tikrit':         [43.69, 34.61],
  'Hilla':          [44.43, 32.46],
  'Samarra':        [43.88, 34.20],
  'Damascus':       [36.30, 33.51],
  'Aleppo':         [37.16, 36.20],
  'Homs':           [36.71, 34.73],
  'Jerusalem':      [35.23, 31.78],
  'Tyre':           [35.20, 33.27],
  'Antioch':        [36.16, 36.20],
  'Edessa':         [38.80, 37.16],
  // 埃及／北非
  'Cairo':          [31.24, 30.04],
  'Fustat':         [31.23, 30.01],
  'Alexandria':     [29.92, 31.20],
  'Aswan':          [32.90, 24.09],
  'Tripoli (Libya)':[13.18, 32.89],
  'Kairouan':       [10.10, 35.68],
  'Tunis':          [10.18, 36.81],
  'Fez':            [-5.00, 34.03],
  'Marrakesh':      [-7.99, 31.63],
  // 阿拉伯半島
  'Mecca':          [39.83, 21.43],
  'Medina':         [39.61, 24.47],
  "Sana'a":         [44.21, 15.37],
  'Aden':           [45.03, 12.79],
  'Muscat':         [58.59, 23.59],
  // 伊比利
  'Cordoba':        [-4.78, 37.89],
  'Granada':        [-3.60, 37.18],
  'Seville':        [-5.99, 37.39],
  'Toledo':         [-4.02, 39.86],
  // 中亞／東伊朗
  'Nishapur':       [58.81, 36.21],
  'Merv':           [61.83, 37.60],
  'Bukhara':        [64.43, 39.77],
  'Samarkand':      [66.97, 39.65],
  'Tashkent':       [69.27, 41.32],
  'Ghazni':         [68.42, 33.55],
  'Kabul':          [69.21, 34.53],
  'Balkh':          [66.90, 36.76],
  'Herat':          [62.20, 34.34],
  'Multan':         [71.51, 30.20],
  'Lahore':         [74.36, 31.55],
  'Delhi':          [77.21, 28.65],
  // 波斯本土
  'Rayy':           [51.43, 35.59],
  'Isfahan':        [51.67, 32.65],
  'Shiraz':         [52.53, 29.59],
  'Hamadan':        [48.51, 34.80],
  'Tabriz':         [46.27, 38.07],
  // 高加索
  'Yerevan':        [44.51, 40.18],
  'Tbilisi':        [44.83, 41.72],
  'Derbent':        [48.29, 42.05],
  // 蒙古／中國／東亞
  'Karakorum':      [102.85, 47.43],
  'Khanbaliq':      [116.40, 39.91],   // 元大都＝北京
  'Beijing':        [116.40, 39.91],
  'Kaifeng':        [114.34, 34.80],
  'Xi\'an':         [108.94, 34.34],
  'Chang\'an':      [108.94, 34.34],
  'Luoyang':        [112.45, 34.62],
  'Nanjing':        [118.78, 32.06],
  'Hangzhou':       [120.16, 30.27],
  'Guangzhou':      [113.27, 23.13],
  'Yangzhou':       [119.42, 32.39],
  'Xinjing':        [125.32, 43.82],   // 滿洲國新京
  'Mukden':         [123.43, 41.80],   // 瀋陽
  'Hanseong':       [126.98, 37.57],   // 漢城（首爾舊名）
  'Kyoto':          [135.77, 35.01],
  'Tokyo':          [139.69, 35.69],
  'Hanoi':          [105.85, 21.03],
  'Pingcheng':      [113.30, 40.08],   // 北魏前期都城（大同）
  'Yecheng':        [114.55, 36.32],   // 鄴城
  // 蒙古擴張帶
  'Otrar':          [68.30, 42.85],
  'Urgench':        [60.63, 41.55],
  'Tabriz':         [46.27, 38.07],
  'Tehran':         [51.39, 35.69],
  'Aleppo':         [37.16, 36.20],
  'Sarai':          [45.73, 47.50],    // 金帳汗國首都
  'Vladimir':       [40.42, 56.13],
  'Kiev':           [30.52, 50.45],
  'Ryazan':         [39.74, 54.62],
  'Krakow':         [19.94, 50.06],
  'Legnica':        [16.16, 51.21],
  'Pest':           [19.07, 47.50],
  'Yanjing':        [116.40, 39.91],   // 燕京 = 北京
  'Lin\'an':        [120.16, 30.27],   // 南宋臨安 = 杭州
  // 商朝（殷商）核心都邑
  'Yanshi':         [112.79, 34.72],   // 偃師（早商）
  'Zhengzhou':      [113.62, 34.75],   // 鄭州商城
  'Anyang':         [114.39, 36.10],   // 安陽（殷墟、晚商）
  'Chaoge':         [114.20, 35.74],   // 朝歌（紂王末都）
  'Shangqiu':       [115.65, 34.41],   // 商丘（商部族起源）
  'Xingtai':        [114.49, 37.06],   // 邢台（中商盤庚前）
  // 西周核心都邑
  'Haojing':        [108.88, 34.20],   // 鎬京（西周首都，西安西）
  'Luoyi':          [112.45, 34.62],   // 洛邑（成周）
  'Qishan':         [107.62, 34.45],   // 岐山（周原）
  'Yan':            [116.40, 39.91],   // 燕（北京）
  'Qufu':           [116.99, 35.60],   // 魯（曲阜）
  'Linzi':          [118.30, 36.85],   // 齊（臨淄）
  'Hancheng':       [110.45, 35.48],   // 韓城（晉舊地）
  'Jiang':          [111.57, 35.99],   // 絳（晉都）
  // 春秋戰國列國新增
  'Yongcheng':      [107.16, 34.62],   // 雍（秦舊都）
  'Yanying':        [112.20, 30.62],   // 楚郢都
  'Suzhou':         [120.59, 31.30],   // 吳都姑蘇
  'Shaoxing':       [120.58, 30.03],   // 越都會稽
  'Handan':         [114.49, 36.62],   // 趙都邯鄲
  'Daliang':        [114.34, 34.80],   // 魏都大梁
  'Xinzheng':       [113.74, 34.40],   // 韓都新鄭
  // 羅馬／拜占庭範疇
  'Rome':           [12.50, 41.90],
  'Ravenna':        [12.20, 44.42],
  'Milan':          [9.19, 45.46],
  'Constantinople': [28.98, 41.02],
  'Athens':         [23.73, 37.98],
  'Thessalonica':   [22.94, 40.64],
  'Carthage':       [10.32, 36.85],
  'Caesarea':       [34.89, 32.50],
  'Trebizond':      [39.72, 41.00],
  'Nicaea':         [29.72, 40.43],
  'Smyrna':         [27.14, 38.42],
  'Ephesus':        [27.34, 37.95],
  'London':         [-0.13, 51.51],
  'York':           [-1.08, 53.96],
  'Lyon':           [4.83, 45.76],
  'Massalia':       [5.37, 43.30],     // 馬賽
  'Vienna':         [16.37, 48.21],
  'Hispalis':       [-5.99, 37.39],    // 塞維利亞舊名
  'Tingis':         [-5.81, 35.78],    // 丹吉爾舊名
}

// ===== 帝國控制資料 =====
// 每 entry: { polygon_name: 必須對齊 historical-states.geojson 的 name,
//             name_zh, years: { year: [cities] } }
const EMPIRES = [
  {
    polygon_name: 'Abbasid Caliphate',
    name_zh: '阿巴斯哈里發',
    end_year: 1260,
    years: {
      750: [
        'Baghdad','Kufa','Basra','Mosul','Tikrit','Hilla',
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Cairo','Fustat','Alexandria','Aswan',
        'Mecca','Medina',"Sana'a",'Aden',
        'Tripoli (Libya)','Kairouan','Tunis',
        'Nishapur','Merv','Bukhara','Samarkand',
        'Ghazni','Kabul','Balkh','Herat','Multan',
        'Rayy','Isfahan','Shiraz','Hamadan','Tabriz',
        'Yerevan','Tbilisi',
      ],
      800: [
        'Baghdad','Kufa','Basra','Mosul','Tikrit','Hilla','Samarra',
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Cairo','Fustat','Alexandria','Aswan',
        'Mecca','Medina',"Sana'a",'Aden',
        'Tripoli (Libya)','Kairouan',
        'Nishapur','Merv','Bukhara','Samarkand','Tashkent',
        'Ghazni','Kabul','Balkh','Herat','Multan',
        'Rayy','Isfahan','Shiraz','Hamadan','Tabriz',
        'Yerevan','Tbilisi',
      ],
      900: [
        'Baghdad','Kufa','Basra','Mosul','Tikrit','Hilla','Samarra',
        'Damascus','Aleppo','Homs','Jerusalem','Edessa',
        'Mecca','Medina',
        'Rayy','Isfahan','Hamadan',
        'Tabriz','Yerevan',
      ],
      1000: [
        'Baghdad','Kufa','Basra','Mosul','Tikrit','Hilla','Samarra','Hamadan',
      ],
      1100: [
        'Baghdad','Kufa','Hilla','Samarra','Tikrit',
      ],
      1200: [
        'Baghdad','Kufa','Basra','Hilla','Samarra','Tikrit','Mosul',
      ],
    },
  },
  {
    // 伍麥亞早於阿巴斯，661-750
    polygon_name: 'Umayyad Caliphate',
    name_zh: '伍麥亞哈里發',
    end_year: 750,
    years: {
      661: [
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch',
        'Kufa','Basra','Mosul',
        'Mecca','Medina',
        'Cairo','Fustat','Alexandria',
        'Tripoli (Libya)',
      ],
      680: [
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Kufa','Basra','Mosul','Tikrit',
        'Mecca','Medina',"Sana'a",
        'Cairo','Fustat','Alexandria','Aswan',
        'Tripoli (Libya)','Kairouan',
      ],
      700: [
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Kufa','Basra','Mosul','Tikrit',
        'Mecca','Medina',"Sana'a",'Aden',
        'Cairo','Fustat','Alexandria','Aswan',
        'Tripoli (Libya)','Kairouan','Tunis',
        'Nishapur','Merv','Bukhara',
        'Multan',
      ],
      720: [
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Kufa','Basra','Mosul','Tikrit',
        'Mecca','Medina',"Sana'a",'Aden',
        'Cairo','Fustat','Alexandria','Aswan',
        'Tripoli (Libya)','Kairouan','Tunis','Fez','Marrakesh',
        'Cordoba','Granada','Seville','Toledo',
        'Nishapur','Merv','Bukhara','Samarkand',
        'Ghazni','Multan','Kabul',
        'Rayy','Isfahan','Shiraz','Hamadan',
      ],
      745: [
        'Damascus','Aleppo','Homs','Jerusalem','Tyre','Antioch','Edessa',
        'Kufa','Basra','Mosul','Tikrit',
        'Mecca','Medina',"Sana'a",'Aden',
        'Cairo','Fustat','Alexandria','Aswan',
        'Tripoli (Libya)','Kairouan','Tunis','Fez',
        'Cordoba','Granada','Seville','Toledo',
        'Nishapur','Merv','Bukhara','Samarkand','Tashkent',
        'Ghazni','Multan','Kabul','Balkh',
        'Rayy','Isfahan','Shiraz','Hamadan','Tabriz',
      ],
    },
  },
  {
    // 商朝 — 用實際考古證據的核心都邑而非 historical-basemaps 的超大 Sinic 範圍
    polygon_name: 'Sinic',
    name_zh: '商',
    end_year: -1046,
    years: {
      // 早商：偃師 → 鄭州二里崗
      [-1500]: ['Yanshi', 'Zhengzhou', 'Shangqiu', 'Luoyi'],
      // 中商：盤庚遷殷前後
      [-1300]: ['Zhengzhou', 'Anyang', 'Xingtai', 'Shangqiu', 'Luoyi'],
      // 晚商：殷墟＋朝歌＋擴張到河北/山東
      [-1200]: ['Anyang', 'Chaoge', 'Xingtai', 'Shangqiu', 'Zhengzhou', 'Yanshi', 'Qufu'],
      // 商末：紂王朝歌＋武王伐紂前
      [-1100]: ['Anyang', 'Chaoge', 'Xingtai', 'Shangqiu', 'Zhengzhou', 'Yanshi', 'Qufu', 'Luoyi'],
    },
  },
  {
    // 西周 — 鎬京＋洛邑＋諸侯封地
    polygon_name: 'Zhoa',
    name_zh: '周',
    end_year: -256,
    years: {
      // 西周早期：周公分封
      [-1046]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi'],
      // 西周中期：穆王西征／昭王南征
      [-950]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang'],
      // 西周晚期：宣王中興
      [-820]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng'],
      // 東周春秋：王室東遷洛邑、諸侯坐大
      [-770]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng', 'Yanying'],
      [-650]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng', 'Yanying', 'Shaoxing'],
      // 春秋末：吳越爭霸
      [-550]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Yongcheng', 'Yanying', 'Suzhou', 'Shaoxing'],
      // 戰國七雄
      [-400]: ['Luoyi', 'Yan', 'Qufu', 'Linzi', 'Yongcheng', 'Yanying', 'Handan', 'Daliang', 'Xinzheng'],
      // 戰國末：秦逐並
      [-300]: ['Luoyi', 'Yan', 'Linzi', 'Yongcheng', 'Yanying', 'Handan', 'Daliang', 'Xinzheng'],
    },
  },
  {
    // 蒙古帝國 1206-1259（後分裂為四汗）
    polygon_name: 'Mongol Empire',
    name_zh: '蒙古帝國',
    end_year: 1260,
    years: {
      1206: [
        'Karakorum',
      ],
      1215: [
        'Karakorum','Yanjing',
        'Khanbaliq','Pingcheng',
      ],
      1220: [
        'Karakorum','Yanjing','Khanbaliq','Pingcheng',
        'Otrar','Bukhara','Samarkand','Merv','Urgench','Nishapur',
        'Balkh','Herat',
      ],
      1230: [
        'Karakorum','Yanjing','Khanbaliq','Pingcheng','Kaifeng',
        'Bukhara','Samarkand','Merv','Urgench','Nishapur','Otrar',
        'Balkh','Herat','Ghazni','Kabul',
        'Tabriz','Hamadan','Rayy','Isfahan',
      ],
      1240: [
        'Karakorum','Yanjing','Khanbaliq','Pingcheng','Kaifeng',
        'Bukhara','Samarkand','Merv','Urgench','Nishapur','Otrar',
        'Balkh','Herat','Ghazni','Kabul','Multan',
        'Tabriz','Hamadan','Rayy','Isfahan','Tashkent',
        'Sarai','Vladimir','Kiev','Ryazan',
      ],
      1250: [
        'Karakorum','Yanjing','Khanbaliq','Pingcheng','Kaifeng','Beijing',
        'Bukhara','Samarkand','Merv','Urgench','Nishapur','Otrar','Tashkent',
        'Balkh','Herat','Ghazni','Kabul','Multan',
        'Tabriz','Hamadan','Rayy','Isfahan','Yerevan','Tbilisi','Derbent',
        'Sarai','Vladimir','Kiev','Ryazan','Krakow','Legnica','Pest',
      ],
      1259: [
        'Karakorum','Yanjing','Khanbaliq','Pingcheng','Kaifeng','Beijing',
        'Bukhara','Samarkand','Merv','Urgench','Nishapur','Otrar','Tashkent',
        'Balkh','Herat','Ghazni','Kabul','Multan','Lahore','Delhi',
        'Baghdad','Mosul','Aleppo','Damascus',
        'Tabriz','Hamadan','Rayy','Isfahan','Yerevan','Tbilisi','Derbent',
        'Sarai','Vladimir','Kiev','Ryazan',
      ],
    },
  },
]

// ===== Convex hull (Graham scan) =====
function cross(o, a, b) {
  return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
}
function convexHull(points) {
  const sorted = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1])
  const n = sorted.length
  if (n < 3) return sorted
  const lower = []
  for (const p of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop()
    lower.push(p)
  }
  const upper = []
  for (let i = n - 1; i >= 0; i--) {
    const p = sorted[i]
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop()
    upper.push(p)
  }
  upper.pop(); lower.pop()
  return lower.concat(upper)
}

// ===== Build per empire =====
const features = []
let totalCities = 0
let missingCities = new Set()

for (const emp of EMPIRES) {
  const years = Object.keys(emp.years).map(Number).sort((a, b) => a - b)
  for (let i = 0; i < years.length; i++) {
    const year = years[i]
    const nextYear = years[i + 1] ?? emp.end_year
    const cityNames = emp.years[year]
    const coords = []
    for (const n of cityNames) {
      const c = CITIES[n]
      if (!c) { missingCities.add(n); continue }
      coords.push(c)
      totalCities++
    }

    if (coords.length < 1) {
      console.warn(`[${emp.polygon_name}] ${year}: no valid cities`)
      continue
    }
    // 1-2 個城市無法 hull，做點／線；3+ 用 convex hull
    let ring
    if (coords.length === 1) {
      // 單點：畫一個小方塊（~50 km 邊）
      const [lon, lat] = coords[0]
      const d = 0.5
      ring = [[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]
    } else if (coords.length === 2) {
      // 兩點：畫一個長方形包圍
      const [lon1, lat1] = coords[0]
      const [lon2, lat2] = coords[1]
      const minLon = Math.min(lon1, lon2) - 0.5, maxLon = Math.max(lon1, lon2) + 0.5
      const minLat = Math.min(lat1, lat2) - 0.5, maxLat = Math.max(lat1, lat2) + 0.5
      ring = [[minLon, minLat], [maxLon, minLat], [maxLon, maxLat], [minLon, maxLat], [minLon, minLat]]
    } else {
      const hull = convexHull(coords)
      ring = [...hull, hull[0]]
    }

    features.push({
      type: 'Feature',
      geometry: { type: 'Polygon', coordinates: [ring] },
      properties: {
        name: emp.polygon_name,
        name_zh: emp.name_zh,
        year_from: year,
        year_to: nextYear - 1,
        city_count: coords.length,
        source: 'city-hull (manual city list)',
      },
    })
  }
  console.log(`[${emp.polygon_name}] ${years.length} years`)
}

if (missingCities.size > 0) {
  console.warn('Missing city coords:', [...missingCities].join(', '))
}

const geojson = { type: 'FeatureCollection', features }
const out = resolve(ROOT, 'public/maps/fine-polygons.geojson')
writeFileSync(out, JSON.stringify(geojson, null, 2))
console.log(`\n✅ ${features.length} polygons / ${EMPIRES.length} empires → ${out}`)
console.log(`Total bytes: ${JSON.stringify(geojson).length}`)
