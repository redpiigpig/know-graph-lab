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
  'Xianyang':       [108.71, 34.33],   // 秦都咸陽
  'Linfen':         [111.52, 36.10],   // 平陽（晉舊都）
  'Tongguan':       [110.39, 34.55],   // 潼關（關中東鎖）
  'Pingyang':       [111.52, 36.10],   // 平陽
  // 秦統一後郡縣
  'Chengdu':        [104.07, 30.67],   // 蜀郡
  'Lingnan':        [113.27, 23.13],   // 嶺南（番禺）
  'Liaodong':       [123.43, 41.80],   // 遼東郡（瀋陽）
  'Jiangnan':       [118.78, 32.06],   // 江南
  // 三國魏蜀吳都城
  'Luoyang2':       [112.45, 34.62],   // 洛陽（曹魏／西晉都）
  'Chengdu2':       [104.07, 30.67],   // 成都（蜀漢都）
  'Jianye':         [118.78, 32.06],   // 建業（孫吳都）
  // 西晉南遷東晉
  'Jiankang':       [118.78, 32.06],   // 建康（東晉都）
  // 隋唐都城／節度使治所
  'Daxing':         [108.94, 34.34],   // 大興＝隋唐長安
  'Yangzhou2':      [119.42, 32.39],   // 揚州
  'Lhasa':          [91.13, 29.65],    // 拉薩（吐蕃／西藏）
  'Kucha':          [82.97, 41.72],    // 龜茲（安西四鎮）
  'Khotan':         [79.92, 37.11],    // 于闐
  'Kashgar':        [75.99, 39.47],    // 疏勒
  'Beshbalik':      [89.20, 43.92],    // 北庭都護府
  'Pyongyang':      [125.75, 39.04],   // 平壤
  // 五代十國
  'Kaifeng2':       [114.34, 34.80],   // 後梁／後晉／後漢／後周＋北宋都
  'Taiyuan':        [112.55, 37.87],   // 太原（北漢＋後唐）
  'Fuzhou':         [119.30, 26.08],   // 福州（閩）
  'Changsha':       [112.94, 28.23],   // 長沙（楚）
  'Jiangling':      [112.24, 30.34],   // 江陵（荊南／南平）
  'Chengdu3':       [104.07, 30.67],   // 成都（前蜀／後蜀）
  // 元朝大都／行省
  'Dadu':           [116.40, 39.91],   // 元大都 = 北京
  'Shangdu':        [116.18, 42.36],   // 上都（金蓮川／開平）
  'Karakorum2':     [102.85, 47.43],   // 哈拉和林
  'Yunnan':         [102.71, 25.04],   // 雲南行省
  // 明清北京
  'Beiping':        [116.40, 39.91],   // 明初北平＝後遷都
  'Yingtian':       [118.78, 32.06],   // 應天府＝南京（明初都）
  // 西夏
  'Xingqing':       [106.27, 38.49],   // 興慶府（銀川）
  'Liangzhou':      [102.64, 37.93],   // 涼州（武威）
  'Ganzhou':        [100.46, 38.94],   // 甘州（張掖）
  // 遼五京
  'Liaoyang':       [123.18, 41.27],   // 遼東京遼陽
  'Linhuang':       [119.41, 43.99],   // 上京臨潢（巴林左旗）
  'Datong':         [113.30, 40.08],   // 西京大同
  // 金五京
  'Huining':        [126.10, 45.78],   // 上京會寧（哈爾濱阿城）
  'Zhongdu':        [116.40, 39.91],   // 中都（北京）
  // 西藏吐蕃
  'Lhotse':         [91.13, 29.65],    // 邏些＝拉薩
  // 越南北部
  'Hanoi2':         [105.85, 21.03],   // 河內
  // 南朝補
  'Jiaozhou':       [105.85, 21.03],   // 交州（越南北部）
  'Jiangzhou':      [115.99, 28.68],   // 江州（江西南昌）
  'Xiangzhou':      [112.94, 28.23],   // 湘州（長沙）
  'Yongjia':        [120.65, 28.00],   // 永嘉（溫州）
  'Jingzhou':       [112.18, 30.34],   // 荊州（江陵）
  // 五代十國補
  'Bianliang':      [114.34, 34.80],   // 汴梁（後梁／後晉／後漢／後周＋北宋都）
  'Luoyang3':       [112.45, 34.62],   // 洛陽（後唐都）
  'Ganzhou2':       [115.00, 25.83],   // 贛州
  'Qionghai':       [110.47, 19.24],   // 瓊海（南漢南端）
  // 西夏五州
  'Yinchuan':       [106.27, 38.49],   // 興慶＝銀川（西夏都）
  'Wuwei':          [102.64, 37.93],   // 涼州武威
  'Zhangye':        [100.46, 38.94],   // 甘州張掖
  'Dunhuang':       [94.66, 40.14],    // 沙州敦煌
  'Yulin':          [109.74, 38.29],   // 銀州榆林
  'Ordos':          [109.78, 39.61],   // 鄂爾多斯（橫山）
  // 西遼（喀喇契丹）核心都邑
  'Balasaghun':     [75.18, 42.85],    // 八剌沙袞（虎思斡耳朵，吉爾吉斯）
  'Yarkand':        [77.24, 38.42],    // 葉爾羌
  'Aksu':           [80.27, 41.17],    // 阿克蘇
  'Almaliq':        [80.95, 44.05],    // 阿力麻里（伊犁地區）
  'Talas':          [71.41, 42.52],    // 怛邏斯
  // 北宋／南宋核心
  'Yongzhou':       [108.32, 22.82],   // 邕州南寧
  'Tanzhou':        [112.94, 28.23],   // 潭州（北宋稱長沙）
  'Quanzhou':       [118.68, 24.87],   // 泉州（南宋海港）
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
      // 早商：偃師 → 鄭州二里崗（黃河中游核心）
      [-1500]: ['Yanshi', 'Zhengzhou', 'Shangqiu', 'Luoyi'],
      // 中商：盤庚遷殷前後，勢力北擴到河北邢台
      [-1300]: ['Zhengzhou', 'Anyang', 'Xingtai', 'Shangqiu', 'Luoyi', 'Yanshi'],
      // 晚商武丁中興：殷墟＋朝歌＋大規模東擴到山東
      [-1200]: ['Anyang', 'Chaoge', 'Xingtai', 'Shangqiu', 'Zhengzhou', 'Yanshi', 'Qufu', 'Luoyi'],
      // 商末：紂王朝歌、武王伐紂前夕
      [-1100]: ['Anyang', 'Chaoge', 'Xingtai', 'Shangqiu', 'Zhengzhou', 'Yanshi', 'Qufu', 'Luoyi', 'Linzi'],
    },
  },
  {
    // 西周 — 鎬京＋洛邑＋諸侯封地
    polygon_name: 'Zhoa',
    name_zh: '周',
    end_year: -256,
    years: {
      // 西周早期：周公分封，東至齊魯西至涇渭
      [-1046]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi'],
      // 西周中期：穆王西征／昭王南征到江漢
      [-950]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Yanying'],
      // 西周晚期：宣王中興
      [-820]: ['Haojing', 'Qishan', 'Luoyi', 'Yanshi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng', 'Yanying'],
      // 東周春秋：王室東遷洛邑，諸侯坐大（齊桓晉文）
      [-770]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng', 'Yanying'],
      // 春秋中期：晉楚爭霸
      [-650]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Hancheng', 'Yongcheng', 'Yanying', 'Shaoxing', 'Suzhou'],
      // 春秋末：吳越爭霸
      [-550]: ['Luoyi', 'Zhengzhou', 'Anyang', 'Yan', 'Qufu', 'Linzi', 'Jiang', 'Yongcheng', 'Yanying', 'Suzhou', 'Shaoxing'],
      // 戰國七雄
      [-400]: ['Luoyi', 'Yan', 'Qufu', 'Linzi', 'Yongcheng', 'Yanying', 'Handan', 'Daliang', 'Xinzheng'],
      // 戰國末：秦東出函谷
      [-300]: ['Luoyi', 'Yan', 'Linzi', 'Yongcheng', 'Yanying', 'Handan', 'Daliang', 'Xinzheng', 'Xianyang'],
    },
  },
  {
    // 大秦統一 — 用 polygon_name='Qin' 抑制源 Qin polygon（戰國秦狹小範圍）在 -221 後
    // 源 coarse Qin -323~-201 是戰國秦，fine Qin 在 -221~-207 顯示統一範圍
    polygon_name: 'Qin',
    name_zh: '秦',
    end_year: -206,
    years: {
      // -221 秦始皇統一六國：北抵長城、南至嶺南、西到隴右
      [-221]: ['Xianyang', 'Haojing', 'Luoyang2', 'Yanshi', 'Zhengzhou', 'Anyang', 'Qufu', 'Linzi', 'Yan', 'Handan', 'Daliang', 'Yanying', 'Suzhou', 'Shaoxing', 'Chengdu', 'Lingnan', 'Liaodong', 'Pingyang'],
      // -210 秦始皇崩於沙丘
      [-210]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Qufu', 'Linzi', 'Yan', 'Handan', 'Daliang', 'Yanying', 'Suzhou', 'Chengdu', 'Lingnan', 'Liaodong'],
    },
  },
  {
    // 三國時期 — historical-basemaps 沒有獨立 Cao Wei / Shu Han / Eastern Wu polygon
    // 用 fine polygon 補三國鼎立 220-280
    polygon_name: 'Cao Wei',
    name_zh: '曹魏',
    end_year: 266,
    years: {
      // 220 曹丕受禪建魏：黃河流域＋關中＋幽州
      [220]: ['Luoyang2', 'Zhengzhou', 'Anyang', 'Xianyang', 'Yan', 'Handan', 'Linzi', 'Qufu', 'Daliang', 'Hancheng', 'Pingyang', 'Liaodong', 'Tongguan'],
      // 263 滅蜀漢
      [263]: ['Luoyang2', 'Zhengzhou', 'Anyang', 'Xianyang', 'Yan', 'Handan', 'Linzi', 'Qufu', 'Daliang', 'Hancheng', 'Pingyang', 'Liaodong', 'Tongguan', 'Chengdu2'],
    },
  },
  {
    polygon_name: 'Shu Han',
    name_zh: '蜀漢',
    end_year: 263,
    years: {
      // 221 劉備稱帝於成都：益州（蜀＋漢中）
      [221]: ['Chengdu2', 'Jiangling', 'Tongguan'],
    },
  },
  {
    polygon_name: 'Eastern Wu',
    name_zh: '東吳',
    end_year: 280,
    years: {
      // 222 孫權稱吳王、229 稱帝：揚州＋荊州南＋交州
      [222]: ['Jianye', 'Suzhou', 'Hangzhou', 'Shaoxing', 'Yanying', 'Changsha', 'Jiangling', 'Lingnan', 'Hanoi2'],
    },
  },
  {
    // 西晉 — 用 polygon_name='Jin' 抑制源 Jin polygon（300~499）在 266~316
    polygon_name: 'Jin',
    name_zh: '西晉',
    end_year: 316,
    years: {
      // 266 司馬炎建晉
      [266]: ['Luoyang2', 'Zhengzhou', 'Anyang', 'Xianyang', 'Yan', 'Handan', 'Linzi', 'Qufu', 'Daliang', 'Pingyang', 'Liaodong', 'Tongguan', 'Chengdu2'],
      // 280 滅吳統一
      [280]: ['Luoyang2', 'Zhengzhou', 'Anyang', 'Xianyang', 'Yan', 'Handan', 'Linzi', 'Qufu', 'Daliang', 'Pingyang', 'Liaodong', 'Tongguan', 'Chengdu2', 'Jianye', 'Suzhou', 'Hangzhou', 'Yanying', 'Changsha', 'Lingnan', 'Hanoi2'],
    },
  },
  {
    // 東晉 — polygon_name='Jin' 繼續抑制源 Jin 至 420
    polygon_name: 'Jin',
    name_zh: '東晉',
    end_year: 420,
    years: {
      // 317 司馬睿在建康稱帝，南渡偏安
      [317]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jiangling', 'Changsha', 'Chengdu2', 'Lingnan', 'Hanoi2'],
    },
  },
  {
    // 南朝 — source 完全沒有劉宋／南齊／梁／陳 polygons
    // 用 polygon_name='Liu Song' 是源資料的命名（但只到 479）— 之後 polygon 缺
    // 此處用 source 完全沒有的名字，避免衝突
    polygon_name: 'Southern Dynasties (Liu Song)',
    name_zh: '劉宋',
    end_year: 479,
    years: {
      // 420 劉裕代晉建宋（南朝最盛時 — 收復河南）
      [420]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Chengdu2', 'Lingnan', 'Jiaozhou', 'Luoyang2', 'Zhengzhou'],
      // 450 元嘉之治後北伐失敗、失河南
      [450]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Chengdu2', 'Lingnan', 'Jiaozhou'],
    },
  },
  {
    polygon_name: 'Southern Dynasties (Southern Qi)',
    name_zh: '南齊',
    end_year: 502,
    years: {
      // 479 蕭道成建齊
      [479]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Chengdu2', 'Lingnan', 'Jiaozhou'],
    },
  },
  {
    polygon_name: 'Southern Dynasties (Liang)',
    name_zh: '梁',
    end_year: 557,
    years: {
      // 502 蕭衍建梁
      [502]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Chengdu2', 'Lingnan', 'Jiaozhou'],
      // 548 侯景之亂後分崩
      [548]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Lingnan', 'Jiaozhou'],
    },
  },
  {
    polygon_name: 'Southern Dynasties (Chen)',
    name_zh: '陳',
    end_year: 589,
    years: {
      // 557 陳霸先建陳（已失江北蜀地）
      [557]: ['Jiankang', 'Suzhou', 'Hangzhou', 'Yanying', 'Jingzhou', 'Jiangzhou', 'Xiangzhou', 'Lingnan', 'Jiaozhou'],
    },
  },
  {
    // 唐朝 — 補 618-799（源 Tang Empire 只 800-999），用 polygon_name='Tang Empire' 抑制源
    polygon_name: 'Tang Empire',
    name_zh: '唐',
    end_year: 907,
    years: {
      // 618 高祖建唐
      [618]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong'],
      // 660 高宗滅百濟、668 滅高句麗
      [660]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Pyongyang', 'Yangzhou2'],
      // 690 武則天稱帝、神都洛陽
      [690]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Kucha', 'Khotan'],
      // 713 玄宗開元盛世（疆域極盛）
      [713]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Kucha', 'Khotan', 'Kashgar', 'Beshbalik'],
      // 755 安史之亂後失西域
      [755]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2'],
      // 800 中唐藩鎮割據（與源 Tang Empire 800 銜接）
      [800]: ['Daxing', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 870 黃巢之亂後縮減
      [870]: ['Daxing', 'Luoyang2', 'Zhengzhou', 'Chengdu', 'Yanying', 'Yangzhou2'],
    },
  },
  {
    // 明朝實際範圍 — 用 fine 抑制源 Ming Chinese Empire (lon 跨 141 太誇張)
    polygon_name: 'Ming Chinese Empire',
    name_zh: '明',
    end_year: 1644,
    years: {
      // 1368 朱元璋建明（南京為都）
      [1368]: ['Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Pingcheng', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Lhasa', 'Hanoi2'],
      // 1421 永樂遷都北京
      [1421]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Pingcheng', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Lhasa', 'Hanoi2', 'Yunnan'],
      // 1500 中期
      [1500]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Pingcheng', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan'],
      // 1600 萬曆末，努爾哈赤崛起前
      [1600]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Pingcheng', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan'],
      // 1630 失遼東給後金
      [1630]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Pingcheng', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan'],
    },
  },
  {
    // 清朝實際範圍 — 用 fine 抑制源 Manchu Empire / Qing Empire 的範圍誇大
    polygon_name: 'Manchu Empire',
    name_zh: '清',
    end_year: 1912,
    years: {
      // 1644 入關
      [1644]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan'],
      // 1683 平台灣
      [1683]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan', 'Karakorum2'],
      // 1759 十全武功（疆域極盛）
      [1759]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan', 'Karakorum2', 'Lhasa', 'Kashgar', 'Khotan', 'Beshbalik', 'Hanoi2'],
      // 1840 鴉片戰爭前
      [1840]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan', 'Karakorum2', 'Lhasa', 'Kashgar', 'Khotan', 'Beshbalik'],
      // 1900 義和團
      [1900]: ['Beiping', 'Mukden', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Yunnan', 'Lhasa', 'Kashgar', 'Beshbalik'],
    },
  },
  {
    // 五代 907-960 — source 完全沒有後梁/後唐/後晉/後漢/後周 polygons
    polygon_name: 'Five Dynasties',
    name_zh: '五代',
    end_year: 960,
    years: {
      // 907 朱溫滅唐建後梁
      [907]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan'],
      // 923 李存勖建後唐（都洛陽）
      [923]: ['Luoyang3', 'Bianliang', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Taiyuan'],
      // 936 石敬瑭建後晉、割燕雲十六州予契丹
      [936]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan'],
      // 947 劉知遠建後漢
      [947]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan'],
      // 951 郭威建後周（柴榮北伐有成）
      [951]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan'],
    },
  },
  {
    // 十國 — 南方諸國（源有 Wuyue / Southern Tang 兩個）
    // 此處補後蜀（成都）／南漢（廣州）／楚（長沙）／閩（福州）／南平（江陵）
    polygon_name: 'Later Shu',
    name_zh: '後蜀',
    end_year: 965,
    years: {
      [934]: ['Chengdu3', 'Jiangling', 'Tongguan'],
    },
  },
  {
    polygon_name: 'Southern Han',
    name_zh: '南漢',
    end_year: 971,
    years: {
      [917]: ['Guangzhou', 'Qionghai', 'Yongzhou', 'Ganzhou2', 'Hanoi2'],
    },
  },
  {
    polygon_name: 'Chu (Ten Kingdoms)',
    name_zh: '楚',
    end_year: 951,
    years: {
      [907]: ['Tanzhou', 'Xiangzhou', 'Ganzhou2', 'Jiangling'],
    },
  },
  {
    polygon_name: 'Min',
    name_zh: '閩',
    end_year: 945,
    years: {
      [909]: ['Fuzhou', 'Quanzhou'],
    },
  },
  {
    polygon_name: 'Nanping (Ten Kingdoms)',
    name_zh: '南平',
    end_year: 963,
    years: {
      [924]: ['Jiangling'],
    },
  },
  {
    polygon_name: 'Former Shu',
    name_zh: '前蜀',
    end_year: 925,
    years: {
      [907]: ['Chengdu3', 'Jiangling', 'Tongguan'],
    },
  },
  {
    polygon_name: 'Northern Han',
    name_zh: '北漢',
    end_year: 979,
    years: {
      [951]: ['Taiyuan'],
    },
  },
  {
    // 北宋 — 用 polygon_name='Song Empire' 抑制源（含燕雲十六州被遼）
    polygon_name: 'Song Empire',
    name_zh: '北宋',
    end_year: 1127,
    years: {
      // 960 趙匡胤陳橋兵變建宋（中原）
      [960]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan'],
      // 979 滅北漢統一中原（仍缺燕雲）
      [979]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Quanzhou'],
      // 1004 澶淵之盟後穩定
      [1004]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Quanzhou', 'Tanzhou', 'Fuzhou'],
      // 1100 徽宗末（北宋極盛文化但軍事衰）
      [1100]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Quanzhou', 'Tanzhou', 'Fuzhou'],
      // 1126 靖康之變
      [1126]: ['Bianliang', 'Hangzhou', 'Yanying', 'Chengdu', 'Guangzhou', 'Quanzhou', 'Fuzhou'],
    },
  },
  {
    // 南宋 — 失中原偏安江南
    polygon_name: 'Southern Song',
    name_zh: '南宋',
    end_year: 1279,
    years: {
      // 1127 高宗建炎南渡
      [1127]: ['Hangzhou', 'Yanying', 'Chengdu', 'Guangzhou', 'Quanzhou', 'Fuzhou', 'Tanzhou', 'Yangzhou2'],
      // 1141 紹興和議後界以淮河
      [1141]: ['Hangzhou', 'Yanying', 'Chengdu', 'Guangzhou', 'Quanzhou', 'Fuzhou', 'Tanzhou', 'Yangzhou2', 'Lingnan'],
      // 1234 蒙古滅金與宋共擊
      [1234]: ['Hangzhou', 'Yanying', 'Chengdu', 'Guangzhou', 'Quanzhou', 'Fuzhou', 'Tanzhou', 'Yangzhou2', 'Lingnan'],
      // 1276 元軍入臨安
      [1276]: ['Quanzhou', 'Fuzhou', 'Guangzhou'],
    },
  },
  {
    // 吳越 — source 沒有 polygon
    polygon_name: 'Wuyue',
    name_zh: '吳越',
    end_year: 978,
    years: {
      [907]: ['Hangzhou', 'Suzhou', 'Quanzhou', 'Fuzhou'],
    },
  },
  {
    // 南唐 — source 沒有 polygon
    polygon_name: 'Southern Tang',
    name_zh: '南唐',
    end_year: 976,
    years: {
      [937]: ['Nanjing', 'Hangzhou', 'Yangzhou2', 'Quanzhou', 'Fuzhou', 'Jiangzhou', 'Tanzhou', 'Ganzhou2'],
      // 958 失江北十四州予後周
      [958]: ['Nanjing', 'Hangzhou', 'Yangzhou2', 'Jiangzhou', 'Tanzhou', 'Ganzhou2'],
    },
  },
  {
    // 金朝（女真）— source 沒有對應 polygon（500-599 polygon 是命名錯誤）
    polygon_name: 'Jin Empire',
    name_zh: '金',
    end_year: 1234,
    years: {
      // 1115 完顏阿骨打稱帝
      [1115]: ['Huining', 'Liaoyang', 'Liaodong'],
      // 1127 滅北宋、取中原
      [1127]: ['Huining', 'Zhongdu', 'Liaoyang', 'Liaodong', 'Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan', 'Pyongyang'],
      // 1153 海陵王遷都中都
      [1153]: ['Zhongdu', 'Huining', 'Liaoyang', 'Liaodong', 'Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan', 'Pyongyang'],
      // 1214 蒙古攻陷中都、宣宗南遷汴京
      [1214]: ['Bianliang', 'Luoyang3', 'Zhengzhou', 'Daxing', 'Linzi', 'Taiyuan'],
    },
  },
  {
    // 遼朝補早期 916-999（source Liao 只 1000 起）
    polygon_name: 'Liao',
    name_zh: '遼',
    end_year: 999,
    years: {
      // 916 耶律阿保機建契丹國
      [916]: ['Linhuang', 'Liaoyang', 'Liaodong', 'Karakorum2'],
      // 936 取燕雲十六州
      [936]: ['Linhuang', 'Liaoyang', 'Liaodong', 'Karakorum2', 'Zhongdu', 'Datong', 'Yan'],
      // 947 改名遼、入侵中原
      [947]: ['Linhuang', 'Liaoyang', 'Liaodong', 'Karakorum2', 'Zhongdu', 'Datong', 'Yan'],
    },
  },
  {
    // 西夏 — source 完全沒有 Western Xia / Tangut polygon
    polygon_name: 'Western Xia',
    name_zh: '西夏',
    end_year: 1227,
    years: {
      // 1038 李元昊稱帝
      [1038]: ['Yinchuan', 'Wuwei', 'Zhangye', 'Dunhuang', 'Yulin', 'Ordos', 'Liangzhou', 'Ganzhou'],
      // 1100 中期穩定
      [1100]: ['Yinchuan', 'Wuwei', 'Zhangye', 'Dunhuang', 'Yulin', 'Ordos', 'Liangzhou', 'Ganzhou'],
      // 1200 蒙古崛起前夕
      [1200]: ['Yinchuan', 'Wuwei', 'Zhangye', 'Dunhuang', 'Yulin', 'Ordos', 'Liangzhou', 'Ganzhou'],
    },
  },
  {
    // 西遼（喀喇契丹）— source 沒有
    polygon_name: 'Qara Khitai',
    name_zh: '西遼',
    end_year: 1218,
    years: {
      // 1124 耶律大石西遷
      [1124]: ['Balasaghun', 'Almaliq', 'Talas', 'Beshbalik', 'Kucha'],
      // 1141 卡特萬戰役大勝塞爾柱
      [1141]: ['Balasaghun', 'Almaliq', 'Talas', 'Beshbalik', 'Kucha', 'Khotan', 'Kashgar', 'Yarkand', 'Aksu', 'Samarkand', 'Bukhara'],
      // 1200 末期
      [1200]: ['Balasaghun', 'Almaliq', 'Talas', 'Beshbalik', 'Kucha', 'Khotan', 'Kashgar', 'Yarkand', 'Aksu'],
    },
  },
  {
    // 元朝 — source 完全沒有 Yuan Empire polygon！
    polygon_name: 'Yuan Empire',
    name_zh: '元',
    end_year: 1368,
    years: {
      // 1271 忽必烈定國號元
      [1271]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang'],
      // 1279 崖山之戰滅南宋，統一全境
      [1279]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Jianye', 'Hangzhou', 'Lin\'an', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Yanying', 'Lhasa', 'Beshbalik'],
      // 1351 紅巾起義
      [1351]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Hangzhou', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Lhasa', 'Beshbalik'],
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
