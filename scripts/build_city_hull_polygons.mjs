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
  // 漢朝擴張據點
  'Jiuquan':        [98.49, 39.75],    // 酒泉郡（武帝河西四郡）
  'Wuwei2':         [102.64, 37.93],   // 武威郡
  'Zhangye2':       [100.46, 38.94],   // 張掖郡
  'Dunhuang2':      [94.66, 40.14],    // 敦煌郡
  'Nanyue':         [113.27, 23.13],   // 番禺（南越）
  'Lelang':         [125.75, 39.04],   // 樂浪郡（朝鮮平壤）
  'Xiyu_DH':        [88.99, 41.86],    // 西域都護府（烏壘城）
  'Jiaozhi':        [105.85, 21.03],   // 交趾郡
  'Yelang':         [106.71, 26.58],   // 夜郎（貴州貴陽）
  // 唐朝擴張據點
  'Khocho':         [89.51, 42.95],    // 高昌（吐魯番）
  'Anxi':           [82.97, 41.72],    // 安西大都護府（龜茲）
  // 元朝行省據點
  'Tibet_Yuan':     [91.13, 29.65],    // 烏思藏宣慰司
  'Korea_Yuan':     [126.98, 37.57],   // 高麗（征東行省）
  // 明清邊疆
  'Hami':           [93.51, 42.83],    // 哈密（明嘉峪關外、清初）
  'Jiayuguan':      [98.28, 39.79],    // 嘉峪關（明清西界）
  'Aigun':          [127.50, 50.25],   // 璦琿（清北界）
  'Heilongjiang':   [126.66, 45.74],   // 黑龍江
  'Vladivostok':    [131.89, 43.12],   // 海參崴（1860 失俄）
  'Sakhalin':       [142.74, 47.32],   // 庫頁島
  'Taiwan':         [120.96, 23.69],   // 台灣（1683 收）
  'Xining':         [101.78, 36.62],   // 西寧（青海）
  'Ili':            [81.32, 43.91],    // 伊犁（清征準噶爾）
  'Urumqi':         [87.62, 43.83],    // 烏魯木齊（迪化）
  'Kaxgar':         [75.99, 39.47],    // 喀什噶爾（清回部）
  'Macao':          [113.55, 22.20],   // 澳門（1557 葡據）
  'HKisland':       [114.17, 22.30],   // 香港（1842 割英）
  'Khotan_Q':       [79.92, 37.11],    // 和闐
  'Yarkand_Q':      [77.24, 38.42],    // 葉爾羌
  // 北朝補
  'Yecheng2':       [114.55, 36.32],   // 鄴城（東魏／北齊都）
  'Xianyang2':      [108.71, 34.33],   // 長安（西魏／北周都）
  // 羅馬／拜占庭擴張
  'Cordoba2':       [-4.78, 37.89],    // Hispalis 羅馬西班牙
  'Mainz':          [8.27, 50.00],     // Mogontiacum 萊茵防線
  'Trier':          [6.64, 49.75],     // Augusta Treverorum
  'Cologne':        [6.96, 50.94],     // Colonia
  'Vienna2':        [16.37, 48.21],    // Vindobona
  'Aquileia':       [13.37, 45.77],    // 亞奎雷亞
  'Sirmium':        [19.61, 44.97],    // 賽爾彌烏姆（多瑙河）
  'Petra':          [35.44, 30.32],    // 佩特拉（阿拉伯）
  'Palmyra':        [38.27, 34.55],    // 帕米拉
  'Dura':           [40.73, 34.75],    // 杜拉歐羅普斯
  'Pergamon':       [27.18, 39.13],    // 帕加馬
  'Cyrene':         [21.86, 32.82],    // 昔蘭尼
  'Hippo':          [7.75, 36.90],     // 希波（聖奧古斯丁主教座）
  'Lugdunum':       [4.83, 45.76],     // 里昂（羅馬高盧首府）
  'Londinium':      [-0.13, 51.51],    // 倫敦
  'Eboracum':       [-1.08, 53.96],    // 約克
  'Tarraco':        [1.25, 41.12],     // 塔拉戈納（西班牙）
  'Caesaraugusta':  [-0.88, 41.65],    // 撒拉戈薩
  // 拜占庭補
  'Adrianople':     [26.56, 41.68],    // 阿德里亞諾堡
  'Sardis':         [28.04, 38.49],    // 撒第斯
  'Bari':           [16.87, 41.13],    // 巴里（拜占庭意南據點）
  'Naples2':        [14.27, 40.85],    // 那不勒斯
  'Iconium':        [32.49, 37.87],    // 伊科尼姆（科尼亞）
  'Caesarea_Cap':   [35.49, 38.72],    // 凱撒利亞（卡帕多西亞）
  'Ankyra':         [32.85, 39.93],    // 安卡拉
  // 鄂圖曼擴張
  'Bursa':          [29.06, 40.18],    // 布爾薩（鄂圖曼前期都）
  'Edirne':         [26.56, 41.68],    // 埃迪爾內＝阿德里亞諾堡
  'Sofia':          [23.32, 42.70],    // 索菲亞
  'Belgrade':       [20.45, 44.79],    // 貝爾格勒
  'Buda':           [19.04, 47.50],    // 布達（匈牙利）
  'Algiers':        [3.06, 36.75],     // 阿爾及爾
  'Tripoli2':       [13.18, 32.89],    // 的黎波里
  'Basra2':         [47.78, 30.50],    // 巴斯拉
  'Mosul2':         [43.13, 36.34],    // 摩蘇爾
  'Jeddah':         [39.20, 21.49],    // 吉達
  'Crete_Hera':     [25.13, 35.34],    // 克里特島（伊拉克利翁）
  'Cyprus_Nic':     [33.36, 35.17],    // 賽普勒斯（尼科西亞）
  'Aleppo2':        [37.16, 36.20],    // 阿勒坡
  'Erzurum':        [41.27, 39.91],    // 埃爾祖魯姆（東部）
  'Trabzon':        [39.72, 41.00],    // 特拉布宗
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
  // ===== 古波斯（阿契美尼德／帕提亞／薩珊）=====
  'Persepolis':     [52.89, 29.93],    // 波斯波利斯（阿契美尼德禮儀首都）
  'Pasargadae':     [53.18, 30.19],    // 帕薩爾加德（居魯士建）
  'Susa':           [48.27, 32.18],    // 蘇薩（冬都）
  'Ecbatana':       [48.51, 34.80],    // 埃克巴坦那＝Hamadan（夏都）
  'Babylon':        [44.42, 32.54],    // 巴比倫
  'Memphis':        [31.25, 29.85],    // 孟菲斯（埃及舊都）
  'Pelusium':       [32.55, 31.04],    // 佩魯希烏姆（尼羅河東岸口）
  'Sidon':          [35.38, 33.56],    // 西頓
  'Behistun':       [47.43, 34.39],    // 貝希斯敦（大流士銘文）
  'Halicarnassus':  [27.42, 37.04],    // 哈利卡爾納索斯（小亞細亞 satrapy）
  'Ctesiphon':      [44.58, 33.09],    // 泰西封（帕提亞／薩珊首都）
  'Hatra':          [42.72, 35.59],    // 哈特拉（帕提亞據點）
  'Nisibis':        [41.21, 37.07],    // 尼西比斯（薩珊／羅馬邊界）
  'Bishapur':       [51.57, 29.79],    // 比沙普爾（薩珊 Shapur I 建）
  'Gundeshapur':    [48.55, 32.30],    // 詹迪沙普爾（薩珊學術中心）
  'Gor':            [52.55, 28.97],    // Ardashir-Khurra（薩珊發祥）
  'Estakhr':        [52.92, 29.98],    // 伊斯塔赫爾（波斯本土）
  'Taxila':         [72.83, 33.74],    // 塔克西拉（阿契美尼德印度河 satrapy／孔雀）
  'Maracanda':      [66.97, 39.65],    // 馬拉坎大＝Samarkand（已有 Samarkand）
  // ===== 古印度 =====
  'Pataliputra':    [85.14, 25.61],    // 巴連弗邑（孔雀／笈多都，今 Patna）
  'Ujjain':         [75.78, 23.18],    // 烏賈因
  'Mathura':        [77.67, 27.49],    // 馬圖拉
  'Sanchi':         [77.74, 23.48],    // 桑奇
  'Kalinga':        [85.83, 20.30],    // 羯陵伽（今 Bhubaneswar）
  'Bharuch':        [72.99, 21.71],    // 婆魯羯車（古港）
  'Sopara':         [72.82, 19.41],    // 蘇帕拉
  'Vidisha':        [77.81, 23.52],    // 維迪沙
  'Kannauj':        [79.92, 27.06],    // 曲女城（笈多後／戒日王都）
  'Vallabhi':       [71.88, 21.89],    // 伐臘毗（Maitraka 都）
  'Pundravardhana': [88.65, 25.03],    // 笈多孟加拉據點
  'Tamralipti':     [87.92, 22.04],    // 達摩立底港
  'Devagiri':       [75.21, 19.93],    // 德瓦吉里（Tughluq 短期遷都＝Daulatabad）
  'Lakhnauti':      [88.13, 24.86],    // 拉克瑙提（孟加拉蘇丹）
  'Madurai':        [78.12, 9.93],     // 馬杜賴（Tughluq 南界）
  'Surat':          [72.83, 21.17],    // 蘇拉特（Mughal 港）
  'Hyderabad':      [78.49, 17.39],    // 海德拉巴（Mughal 德干）
  'Dhaka':          [90.41, 23.81],    // 達卡（Mughal 孟加拉）
  'Kandahar':       [65.71, 31.62],    // 坎大哈（Mughal 西界）
  'Ahmedabad':      [72.59, 23.03],    // 阿默達巴德
  'Bijapur':        [75.71, 16.83],    // 比賈普爾（Mughal 德干征服）
  'Golconda':       [78.40, 17.38],    // 戈爾康達（Mughal 1687 滅）
  'Sind':           [68.37, 25.39],    // 信德（卡拉奇北）
  'Agra':           [78.02, 27.18],    // 阿格拉（Mughal 主都）
  'Ajmer':          [74.64, 26.45],    // 阿傑梅爾（拉吉普坦那）
  // ===== 神聖羅馬帝國 =====
  'Aachen':         [6.08, 50.78],     // 亞琛（查理曼／Otto 加冕地）
  'Frankfurt':      [8.68, 50.11],     // 法蘭克福（選帝侯選舉）
  'Nuremberg':      [11.08, 49.45],    // 紐倫堡（帝國自由市）
  'Regensburg':     [12.10, 49.01],    // 雷根斯堡（帝國議會）
  'Augsburg':       [10.90, 48.37],    // 奧格斯堡（富格家族）
  'Prague':         [14.42, 50.08],    // 布拉格（盧森堡查理四世都）
  'Munich':         [11.58, 48.14],    // 慕尼黑（巴伐利亞）
  'Strasbourg':     [7.75, 48.58],     // 斯特拉斯堡（萊茵帝國市）
  'Hamburg':        [10.00, 53.55],    // 漢堡（漢薩自由市）
  'Bremen':         [8.81, 53.08],     // 不萊梅
  'Lubeck':         [10.69, 53.87],    // 呂北克（漢薩盟首）
  'Magdeburg':      [11.63, 52.13],    // 馬格德堡（薩克森）
  'Worms':          [8.36, 49.63],     // 沃姆斯（帝國議會 1521）
  'Speyer':         [8.43, 49.32],     // 施派爾（皇陵）
  'Brussels':       [4.36, 50.85],     // 布魯塞爾（哈布斯堡尼德蘭都）
  'Utrecht':        [5.12, 52.09],     // 烏特勒支
  'Basel':          [7.59, 47.56],     // 巴塞爾（瑞士 1499 脫離）
  'Bern':           [7.45, 46.95],     // 伯恩
  'Zurich':         [8.55, 47.37],     // 蘇黎世
  'Florence':       [11.26, 43.77],    // 佛羅倫斯
  'Venice':         [12.33, 45.44],    // 威尼斯
  'Genoa':          [8.95, 44.41],     // 熱那亞
  'Bologna':        [11.34, 44.49],    // 波隆那
  'Innsbruck':      [11.40, 47.27],    // 因斯布魯克（哈布斯堡蒂羅爾）
  'Salzburg':       [13.05, 47.81],    // 薩爾茨堡（采邑大主教區）
  'Dresden':        [13.74, 51.05],    // 德勒斯登（薩克森）
  'Leipzig':        [12.37, 51.34],    // 萊比錫
  'Pavia':          [9.16, 45.18],     // 帕維亞（倫巴底／義大利王國舊都）
  'Verona':         [10.99, 45.44],    // 維羅納
  'Trento':         [11.12, 46.07],    // 特倫托
  'Antwerp':        [4.40, 51.22],     // 安特衛普
  // ===== 中美洲（阿茲特克）=====
  'Tenochtitlan':   [-99.13, 19.43],   // 特諾奇蒂特蘭（阿茲特克都）
  'Texcoco':        [-98.88, 19.50],   // 特斯科科（三方聯盟）
  'Tlacopan':       [-99.20, 19.45],   // 特拉科潘（三方聯盟）
  'Cholula':        [-98.30, 19.06],   // 喬盧拉
  'Tlaxcala':       [-98.24, 19.32],   // 特拉斯卡拉（反阿茲特克盟、後助西班牙）
  'Cempoala':       [-96.41, 19.45],   // 森波瓦拉（灣岸 Totonac）
  'Xochimilco':     [-99.10, 19.26],   // 霍奇米爾科
  'Tula':           [-99.34, 20.06],   // 圖拉（托爾特克舊都）
  'Tehuantepec':    [-95.24, 16.32],   // 特萬特佩克（地峽）
  'Oaxaca':         [-96.73, 17.06],   // 瓦哈卡
  'Soconusco':      [-92.13, 14.79],   // 索科努斯科（阿茲特克南界）
  'Tuxpan':         [-97.41, 20.96],   // 圖斯潘（灣岸北）
  'Cuetlaxtla':     [-96.50, 18.90],   // 庫埃特拉斯特蘭
  'Mixquiahuala':   [-99.21, 20.23],   // Otomí 區
  'TepicMex':       [-104.89, 21.51],  // 特皮克（阿茲特克西界）
  // ===== 安第斯（印加）=====
  'Cuzco':          [-71.97, -13.53],  // 庫斯科（印加首都）
  'Quito':          [-78.52, -0.18],   // 基多（北印加副都）
  'Cajamarca':      [-78.50, -7.16],   // 卡哈馬卡（Atahualpa 被擒處）
  'Pachacamac':     [-76.90, -12.26],  // 帕查卡馬克（沿海聖所）
  'Tomebamba':      [-79.00, -2.90],   // 托梅班巴＝Cuenca（北副都）
  'ChanChan':       [-79.07, -8.10],   // 昌昌（Chimu 都、被印加征）
  'Vilcabamba':     [-72.94, -13.10],  // 比爾卡班巴（印加殘餘）
  'MendozaInca':    [-68.85, -32.89],  // 門多薩（南界）
  'TalcaInca':      [-71.66, -35.43],  // 塔爾卡（智利南界）
  'SantiagoInca':   [-70.65, -33.45],  // 聖地牙哥（智利中部）
  'TrujilloAndes':  [-79.03, -8.11],   // 特魯希略
  'Arequipa':       [-71.54, -16.41],  // 阿雷基帕
  'PotosiInca':     [-65.75, -19.59],  // 波托西
  'LaPaz':          [-68.15, -16.50],  // 拉巴斯
  'SucreInca':      [-65.26, -19.04],  // 蘇克雷
  'Huancayo':       [-75.21, -12.07],  // 萬卡約（中央高原）
  'TucumanInca':    [-65.21, -26.83],  // 圖庫曼（南界）
  'Pasto':          [-77.28, 1.21],    // 帕斯托（北界）
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
      // 630 太宗破東突厥、頡利可汗被擒
      [630]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Beshbalik'],
      // 640 滅高昌、設安西都護府
      [640]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Beshbalik', 'Khocho', 'Anxi'],
      // 657 平西突厥、設濛池都督府
      [657]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Beshbalik', 'Khocho', 'Anxi', 'Kashgar', 'Khotan', 'Tashkent'],
      // 668 滅高句麗、設安東都護府
      [668]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Beshbalik', 'Khocho', 'Anxi', 'Kashgar', 'Khotan', 'Pyongyang'],
      // 690 武則天稱帝、神都洛陽
      [690]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Beshbalik', 'Khocho', 'Anxi', 'Kashgar', 'Khotan'],
      // 713 玄宗開元盛世（疆域極盛）
      [713]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Liaodong', 'Yangzhou2', 'Kucha', 'Khotan', 'Kashgar', 'Beshbalik', 'Anxi', 'Khocho'],
      // 755 安史之亂、玄宗西奔
      [755]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 763 吐蕃陷長安、唐軍收復
      [763]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 781 安西四鎮陷於吐蕃／回鶻
      [781]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 805 元和中興前夕
      [805]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 840 武宗滅佛、宣宗大中之治
      [840]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 874 黃巢之亂起
      [874]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 884 黃巢敗於朱溫
      [884]: ['Daxing', 'Luoyang2', 'Taiyuan', 'Zhengzhou', 'Chengdu', 'Yanying', 'Yangzhou2'],
      // 904 朱溫脅遷昭宗於洛陽、唐將亡
      [904]: ['Luoyang2', 'Daxing', 'Zhengzhou', 'Chengdu', 'Yanying'],
    },
  },
  {
    // 明朝實際範圍 — 用 fine 抑制源 Ming Chinese Empire (lon 跨 141 太誇張)
    polygon_name: 'Ming Chinese Empire',
    name_zh: '明',
    end_year: 1644,
    years: {
      // 1368 朱元璋建明（南京為都，遼東陝甘未平）
      [1368]: ['Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2'],
      // 1372 馮勝平河西、徐達平西北
      [1372]: ['Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Jiayuguan'],
      // 1387 平遼東、納哈出降
      [1387]: ['Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Jiayuguan', 'Liaodong', 'Mukden'],
      // 1405 鄭和首下西洋；安南內附（1407）後加
      [1405]: ['Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan', 'Lhasa', 'Hanoi2'],
      // 1421 永樂遷都北京
      [1421]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan', 'Lhasa', 'Hanoi2', 'Hami'],
      // 1428 棄交趾、安南獨立
      [1428]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan', 'Lhasa', 'Hami'],
      // 1449 土木堡之變，明英宗被瓦剌俘
      [1449]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan'],
      // 1500 弘治中興後期
      [1500]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan'],
      // 1550 嘉靖庚戌之變、倭寇登陸
      [1550]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan'],
      // 1583 努爾哈赤起兵
      [1583]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan'],
      // 1592 援朝戰爭爆發
      [1592]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Mukden', 'Yunnan'],
      // 1619 薩爾滸大敗、明軍失遼河以東
      [1619]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Liaodong', 'Yunnan'],
      // 1630 失廣寧／遼東
      [1630]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Jiayuguan', 'Yunnan'],
      // 1640 崇禎末，李自成張獻忠起義
      [1640]: ['Beiping', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Daxing', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan'],
    },
  },
  {
    // 清朝實際範圍 — 用 fine 抑制源 Manchu Empire / Qing Empire 的範圍誇大
    polygon_name: 'Manchu Empire',
    name_zh: '清',
    end_year: 1912,
    years: {
      // 1644 入關、占北京
      [1644]: ['Beiping', 'Mukden', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Liaodong', 'Heilongjiang'],
      // 1645 滅弘光、揚州十日／嘉定三屠
      [1645]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Hangzhou', 'Yangzhou2', 'Liaodong', 'Heilongjiang'],
      // 1662 永曆亡（南明結束）
      [1662]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang'],
      // 1683 平台灣
      [1683]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan'],
      // 1689 尼布楚條約、確定俄清北界
      [1689]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2'],
      // 1696 康熙親征噶爾丹、漠北蒙古歸附
      [1696]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin'],
      // 1720 平西藏，達賴喇嘛護送回藏
      [1720]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining'],
      // 1755 平準噶爾汗國（伊犁河流域）
      [1755]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining', 'Ili', 'Urumqi'],
      // 1759 平回部（南疆塔里木盆地）
      [1759]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Khotan_Q', 'Yarkand_Q', 'Hami'],
      // 1800 嘉慶前期、白蓮教鎮壓
      [1800]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1840 鴉片戰爭爆發
      [1840]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1842 南京條約失香港
      [1842]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Heilongjiang', 'Taiwan', 'Aigun', 'Karakorum2', 'Sakhalin', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1860 北京條約失外興安嶺以南（俄）／加九龍
      [1860]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Taiwan', 'Karakorum2', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1881 伊犁條約收回部分新疆領土
      [1881]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Taiwan', 'Karakorum2', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1895 馬關條約失台灣／澎湖
      [1895]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Karakorum2', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami', 'Macao'],
      // 1900 庚子之亂、八國聯軍
      [1900]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Chengdu', 'Yanying', 'Hangzhou', 'Guangzhou', 'Yangzhou2', 'Yunnan', 'Liaodong', 'Karakorum2', 'Lhasa', 'Xining', 'Ili', 'Urumqi', 'Kaxgar', 'Hami'],
      // 1911 武昌起義、辛亥革命
      [1911]: ['Beiping', 'Mukden', 'Yingtian', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Chengdu', 'Yanying', 'Hangzhou', 'Yangzhou2', 'Yunnan', 'Lhasa', 'Urumqi'],
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
      // 1271 忽必烈定國號元（仍與南宋對峙）
      [1271]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang'],
      // 1279 崖山之戰滅南宋，統一全境
      [1279]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Jianye', 'Hangzhou', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Yanying', 'Lhasa', 'Beshbalik', 'Korea_Yuan', 'Tibet_Yuan'],
      // 1300 元成宗大德之治（疆域極盛）
      [1300]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Hangzhou', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Yanying', 'Lhasa', 'Beshbalik', 'Korea_Yuan', 'Tibet_Yuan'],
      // 1320 元仁宗推行漢化、各汗國分裂明顯
      [1320]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Hangzhou', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Yanying', 'Lhasa', 'Korea_Yuan'],
      // 1351 紅巾起義
      [1351]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Xianyang', 'Yan', 'Linzi', 'Liaodong', 'Pyongyang', 'Hangzhou', 'Guangzhou', 'Chengdu2', 'Yunnan', 'Lhasa', 'Korea_Yuan'],
      // 1360 朱元璋崛起、南方各地起義
      [1360]: ['Dadu', 'Shangdu', 'Karakorum2', 'Pingcheng', 'Luoyang2', 'Zhengzhou', 'Yan', 'Linzi', 'Liaodong'],
    },
  },
  {
    // 北朝（北魏分裂後）— 西魏 535-557 / 北周 557-581
    polygon_name: 'Northern Zhou',
    name_zh: '北周',
    end_year: 581,
    years: {
      // 535 拓跋寶炬建西魏（前身），557 宇文覺廢西魏建北周
      [535]: ['Xianyang2', 'Daxing', 'Linfen', 'Pingyang', 'Hancheng', 'Wuwei2', 'Zhangye2', 'Liangzhou', 'Chengdu2'],
      // 577 北周武帝滅北齊
      [577]: ['Xianyang2', 'Daxing', 'Linfen', 'Pingyang', 'Hancheng', 'Wuwei2', 'Zhangye2', 'Liangzhou', 'Chengdu2', 'Yecheng2', 'Anyang', 'Zhengzhou', 'Linzi', 'Qufu', 'Handan'],
    },
  },
  {
    polygon_name: 'Northern Qi',
    name_zh: '北齊',
    end_year: 577,
    years: {
      // 550 高洋廢東魏建北齊（黃河下游+山東）
      [550]: ['Yecheng2', 'Anyang', 'Zhengzhou', 'Luoyang2', 'Linzi', 'Qufu', 'Handan', 'Liaodong', 'Yan'],
    },
  },
  {
    // 北魏 — 用 polygon_name='Toba Wei' 補充並抑制源 polygon
    polygon_name: 'Toba Wei',
    name_zh: '北魏',
    end_year: 534,
    years: {
      // 386 拓跋珪建魏（鮮卑）
      [386]: ['Pingcheng', 'Datong', 'Yan', 'Linfen'],
      // 439 太武帝滅北涼統一華北
      [439]: ['Pingcheng', 'Datong', 'Yan', 'Linfen', 'Anyang', 'Zhengzhou', 'Luoyang2', 'Linzi', 'Qufu', 'Hancheng', 'Pingyang', 'Wuwei2', 'Zhangye2', 'Liangzhou', 'Dunhuang2'],
      // 493 孝文帝遷洛陽（漢化）
      [493]: ['Luoyang2', 'Pingcheng', 'Datong', 'Yan', 'Anyang', 'Zhengzhou', 'Linzi', 'Qufu', 'Hancheng', 'Pingyang', 'Wuwei2', 'Zhangye2', 'Liangzhou', 'Dunhuang2'],
      // 523 六鎮之亂後分裂前夕
      [523]: ['Luoyang2', 'Pingcheng', 'Datong', 'Yan', 'Anyang', 'Zhengzhou', 'Linzi', 'Qufu', 'Hancheng', 'Pingyang', 'Wuwei2', 'Zhangye2'],
    },
  },
  {
    // 羅馬帝國 — 用 polygon_name='Roman Empire' 抑制源（範圍可能不準）
    // 395 後分東西，由 OHM Western/Eastern Roman 接手，此處 fine 只到 395
    polygon_name: 'Roman Empire',
    name_zh: '羅馬',
    end_year: 395,
    years: {
      // -27 屋大維建元首制
      [-27]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon'],
      // 14 奧古斯都駕崩
      [14]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon', 'Mainz', 'Cologne', 'Aquileia', 'Vienna2'],
      // 117 圖拉真極盛（含達契亞、亞美尼亞、美索不達米亞）
      [117]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon', 'Mainz', 'Cologne', 'Trier', 'Aquileia', 'Vienna2', 'Sirmium', 'Londinium', 'Eboracum', 'Edessa', 'Palmyra', 'Petra', 'Dura', 'Ankyra', 'Sardis', 'Caesarea_Cap'],
      // 138 哈德良後（已棄美索不達米亞）
      [138]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon', 'Mainz', 'Cologne', 'Trier', 'Aquileia', 'Vienna2', 'Sirmium', 'Londinium', 'Eboracum', 'Edessa', 'Palmyra', 'Petra', 'Ankyra', 'Sardis'],
      // 235 三世紀危機開始（軍人皇帝）
      [235]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon', 'Mainz', 'Cologne', 'Trier', 'Aquileia', 'Vienna2', 'Sirmium', 'Londinium', 'Eboracum', 'Edessa', 'Ankyra', 'Sardis'],
      // 285 戴克里先四帝共治、東西分治起源
      [285]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Pergamon', 'Mainz', 'Cologne', 'Trier', 'Aquileia', 'Vienna2', 'Sirmium', 'Londinium', 'Constantinople', 'Edessa', 'Ankyra', 'Sardis'],
      // 330 君士坦丁定都君士坦丁堡
      [330]: ['Rome', 'Naples2', 'Carthage', 'Massalia', 'Lugdunum', 'Tarraco', 'Cordoba2', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Cyrene', 'Mainz', 'Trier', 'Aquileia', 'Sirmium', 'Londinium', 'Constantinople', 'Thessalonica', 'Edessa', 'Ankyra'],
      // 395 狄奧多西死、帝國正式分東西（fine 終止；後 395 改由 OHM Western/Eastern Roman 提供準確邊界）
    },
  },
  {
    // 拜占庭（東羅馬）— 用 polygon_name='Byzantine Empire' 抑制源
    polygon_name: 'Byzantine Empire',
    name_zh: '拜占庭',
    end_year: 1453,
    years: {
      // 395 帝國分裂後東部
      [395]: ['Constantinople', 'Thessalonica', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Edessa', 'Ankyra', 'Sardis', 'Adrianople', 'Pergamon'],
      // 527 查士丁尼即位前
      [527]: ['Constantinople', 'Thessalonica', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Edessa', 'Ankyra', 'Sardis', 'Adrianople', 'Pergamon', 'Cyprus_Nic'],
      // 565 查士丁尼末（收復義大利、北非、西班牙東南）
      [565]: ['Constantinople', 'Thessalonica', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Edessa', 'Ankyra', 'Sardis', 'Adrianople', 'Pergamon', 'Cyprus_Nic', 'Rome', 'Ravenna', 'Naples2', 'Bari', 'Carthage', 'Cordoba2', 'Crete_Hera', 'Cyrene'],
      // 630 希拉克略勝薩珊
      [630]: ['Constantinople', 'Thessalonica', 'Athens', 'Alexandria', 'Antioch', 'Jerusalem', 'Edessa', 'Ankyra', 'Sardis', 'Adrianople', 'Pergamon', 'Cyprus_Nic', 'Rome', 'Ravenna', 'Naples2', 'Bari', 'Carthage', 'Crete_Hera'],
      // 700 阿拉伯失敘利亞埃及北非
      [700]: ['Constantinople', 'Thessalonica', 'Athens', 'Adrianople', 'Pergamon', 'Sardis', 'Ankyra', 'Caesarea_Cap', 'Trebizond', 'Cyprus_Nic', 'Naples2', 'Bari', 'Ravenna', 'Crete_Hera'],
      // 843 聖像破壞結束、復起時代
      [843]: ['Constantinople', 'Thessalonica', 'Athens', 'Adrianople', 'Pergamon', 'Sardis', 'Ankyra', 'Caesarea_Cap', 'Trebizond', 'Naples2', 'Bari'],
      // 1025 巴西爾二世末（疆域復興）
      [1025]: ['Constantinople', 'Thessalonica', 'Athens', 'Adrianople', 'Pergamon', 'Sardis', 'Ankyra', 'Caesarea_Cap', 'Trebizond', 'Naples2', 'Bari', 'Sofia', 'Antioch', 'Edessa', 'Cyprus_Nic', 'Crete_Hera'],
      // 1071 曼齊刻爾特戰役、失安納托利亞
      [1071]: ['Constantinople', 'Thessalonica', 'Athens', 'Adrianople', 'Trebizond', 'Naples2', 'Bari', 'Cyprus_Nic', 'Crete_Hera', 'Sofia'],
      // 1180 科穆寧復興末
      [1180]: ['Constantinople', 'Thessalonica', 'Athens', 'Adrianople', 'Trebizond', 'Cyprus_Nic', 'Crete_Hera', 'Pergamon', 'Sardis'],
      // 1204 第四次十字軍劫
      [1204]: ['Nicaea', 'Trebizond'],
      // 1261 巴里奧略復辟
      [1261]: ['Constantinople', 'Thessalonica', 'Adrianople', 'Nicaea', 'Trebizond'],
      // 1350 末期偏安
      [1350]: ['Constantinople', 'Thessalonica', 'Adrianople'],
      // 1430 帖薩羅尼基陷
      [1430]: ['Constantinople'],
    },
  },
  {
    // 鄂圖曼帝國 — 用 polygon_name='Ottoman Empire' 抑制源
    polygon_name: 'Ottoman Empire',
    name_zh: '鄂圖曼',
    end_year: 1922,
    years: {
      // 1326 奧斯曼一世末、奧爾汗取布爾薩
      [1326]: ['Bursa', 'Nicaea'],
      // 1361 取阿德里亞諾堡（埃迪爾內）
      [1361]: ['Bursa', 'Nicaea', 'Edirne', 'Adrianople'],
      // 1389 科索沃戰役
      [1389]: ['Bursa', 'Edirne', 'Adrianople', 'Sofia', 'Thessalonica'],
      // 1453 攻陷君士坦丁堡
      [1453]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Thessalonica', 'Athens', 'Adrianople', 'Ankyra'],
      // 1517 塞利姆一世征馬木留克（取敘利亞、埃及、聖地）
      [1517]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Thessalonica', 'Athens', 'Adrianople', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Cairo', 'Alexandria', 'Mecca', 'Medina', 'Jeddah', 'Erzurum', 'Trabzon'],
      // 1566 蘇萊曼末（極盛）
      [1566]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Belgrade', 'Buda', 'Thessalonica', 'Athens', 'Adrianople', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Cairo', 'Alexandria', 'Mecca', 'Medina', 'Jeddah', 'Erzurum', 'Trabzon', 'Mosul2', 'Baghdad', 'Basra2', 'Algiers', 'Tunis', 'Tripoli2', 'Crete_Hera', 'Cyprus_Nic'],
      // 1683 維也納之圍敗
      [1683]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Belgrade', 'Buda', 'Thessalonica', 'Athens', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Cairo', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2', 'Algiers', 'Tunis', 'Tripoli2', 'Crete_Hera', 'Cyprus_Nic'],
      // 1699 卡洛維茨和約（失匈牙利）
      [1699]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Belgrade', 'Thessalonica', 'Athens', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Cairo', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2', 'Algiers', 'Tunis', 'Tripoli2', 'Crete_Hera', 'Cyprus_Nic'],
      // 1798 拿破崙入埃及
      [1798]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Belgrade', 'Thessalonica', 'Athens', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2', 'Tunis', 'Tripoli2', 'Crete_Hera', 'Cyprus_Nic'],
      // 1830 失阿爾及爾（法）/ 希臘獨立
      [1830]: ['Constantinople', 'Bursa', 'Edirne', 'Sofia', 'Thessalonica', 'Adrianople', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Cairo', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2', 'Tunis', 'Tripoli2', 'Crete_Hera', 'Cyprus_Nic'],
      // 1878 柏林條約（失巴爾幹大半）
      [1878]: ['Constantinople', 'Bursa', 'Edirne', 'Thessalonica', 'Adrianople', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2', 'Tripoli2'],
      // 1912 巴爾幹戰爭失歐洲領土
      [1912]: ['Constantinople', 'Bursa', 'Edirne', 'Ankyra', 'Damascus', 'Aleppo2', 'Jerusalem', 'Mecca', 'Medina', 'Erzurum', 'Mosul2', 'Baghdad', 'Basra2'],
      // 1918 一戰戰敗
      [1918]: ['Constantinople', 'Bursa', 'Edirne', 'Ankyra', 'Erzurum', 'Trabzon'],
    },
  },
  {
    // 西漢 — 用 polygon_name='Han Empire' 抑制源（-200~-2 BCE）
    // 加事件級 keyframes：高祖／文景／武帝擴張／昭宣／元成哀平／王莽
    polygon_name: 'Han Empire',
    name_zh: '西漢',
    end_year: 9,
    years: {
      // -202 高祖建漢、初平諸侯王
      [-202]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu'],
      // -154 七國之亂後中央集權加強
      [-154]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan'],
      // -127 武帝出擊匈奴前的核心領土
      [-127]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou'],
      // -121 河西之戰：取河西走廊
      [-121]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2'],
      // -111 平南越設九郡
      [-111]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Nanyue', 'Jiaozhi', 'Yelang'],
      // -108 滅衛氏朝鮮設四郡（極盛）
      [-108]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Nanyue', 'Jiaozhi', 'Yelang', 'Lelang'],
      // -60 設西域都護府
      [-60]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Nanyue', 'Jiaozhi', 'Yelang', 'Lelang', 'Xiyu_DH'],
      // -33 元帝後期穩定
      [-33]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Nanyue', 'Jiaozhi', 'Yelang', 'Lelang', 'Xiyu_DH'],
      // -7 哀帝末，王莽攝政前
      [-7]: ['Xianyang', 'Luoyang2', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Jiuquan', 'Wuwei2', 'Zhangye2', 'Dunhuang2', 'Nanyue', 'Jiaozhi', 'Yelang', 'Lelang'],
    },
  },
  {
    // 東漢 — 用 polygon_name='Han' 抑制源（-1~299）
    polygon_name: 'Han',
    name_zh: '東漢',
    end_year: 220,
    years: {
      // 25 光武中興、洛陽建都
      [25]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou'],
      // 36 平公孫述、滅蜀統一
      [36]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi'],
      // 73 班超出使西域，恢復河西
      [73]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi', 'Wuwei2', 'Zhangye2', 'Jiuquan', 'Dunhuang2'],
      // 91 北匈奴亡，恢復西域都護
      [91]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi', 'Wuwei2', 'Zhangye2', 'Jiuquan', 'Dunhuang2', 'Xiyu_DH', 'Lelang'],
      // 105 蔡倫造紙，永元之治後期
      [105]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi', 'Wuwei2', 'Zhangye2', 'Jiuquan', 'Dunhuang2', 'Xiyu_DH', 'Lelang'],
      // 160 桓帝末，已現衰象（西羌亂）
      [160]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi', 'Wuwei2', 'Zhangye2', 'Lelang'],
      // 184 黃巾起義、地方割據開始
      [184]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi'],
      // 200 官渡之戰、曹操北方稱雄
      [200]: ['Luoyang2', 'Xianyang', 'Zhengzhou', 'Linzi', 'Yan', 'Yanying', 'Chengdu', 'Hancheng', 'Pingyang', 'Daliang', 'Qufu', 'Handan', 'Hangzhou', 'Guangzhou', 'Yelang', 'Jiaozhi'],
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
  // ============================================================
  // 古波斯三朝
  // ============================================================
  {
    // 阿契美尼德波斯 -550~-330（源 polygon 只到 -400~-324）
    polygon_name: 'Achaemenid Empire',
    name_zh: '阿契美尼德',
    end_year: -330,
    years: {
      // -550 居魯士滅米底
      [-550]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr'],
      // -546 滅呂底亞、取小亞細亞
      [-546]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus'],
      // -539 滅新巴比倫
      [-539]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus'],
      // -525 岡比西斯滅埃及
      [-525]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Memphis', 'Pelusium', 'Alexandria', 'Cyrene'],
      // -518 大流士征東邊（中亞／印度河）
      [-518]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Memphis', 'Pelusium', 'Alexandria', 'Cyrene', 'Behistun', 'Balkh', 'Merv', 'Samarkand', 'Bukhara', 'Taxila', 'Multan'],
      // -486 大流士末（極盛：色雷斯到印度河）
      [-486]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Memphis', 'Pelusium', 'Alexandria', 'Cyrene', 'Behistun', 'Balkh', 'Merv', 'Samarkand', 'Bukhara', 'Taxila', 'Multan', 'Adrianople', 'Ankyra'],
      // -404 埃及叛離（阿米爾塔尤斯）
      [-404]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Behistun', 'Balkh', 'Merv', 'Samarkand', 'Bukhara', 'Taxila', 'Multan', 'Ankyra'],
      // -343 阿爾塔薛西斯三世復征埃及
      [-343]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Memphis', 'Alexandria', 'Behistun', 'Balkh', 'Merv', 'Samarkand', 'Bukhara', 'Taxila', 'Multan', 'Ankyra'],
      // -334 亞歷山大東征前
      [-334]: ['Pasargadae', 'Persepolis', 'Ecbatana', 'Susa', 'Estakhr', 'Sardis', 'Halicarnassus', 'Ephesus', 'Babylon', 'Tyre', 'Sidon', 'Jerusalem', 'Damascus', 'Memphis', 'Behistun', 'Balkh', 'Merv', 'Samarkand', 'Bukhara', 'Taxila', 'Multan', 'Ankyra'],
    },
  },
  {
    // 帕提亞早期 -247~-130（源 'Parthia' polygon -200~-2）
    polygon_name: 'Parthia',
    name_zh: '帕提亞',
    end_year: -130,
    years: {
      // -247 阿薩息斯一世建國於帕提亞（伊朗東北）
      [-247]: ['Nishapur', 'Merv', 'Hatra'],
      // -209 安條克三世征討、暫時臣屬
      [-209]: ['Nishapur', 'Merv', 'Hatra', 'Balkh', 'Herat'],
      // -171 米特里達梯一世擴張至米底
      [-171]: ['Nishapur', 'Merv', 'Hatra', 'Balkh', 'Herat', 'Ecbatana', 'Estakhr', 'Susa'],
    },
  },
  {
    // 帕提亞極盛 -129~224
    polygon_name: 'Parthian Empire',
    name_zh: '帕提亞',
    end_year: 224,
    years: {
      // -129 米特里達梯一世取美索不達米亞
      [-129]: ['Ctesiphon', 'Babylon', 'Hatra', 'Nisibis', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // -69 提格蘭時期失亞美尼亞
      [-69]: ['Ctesiphon', 'Babylon', 'Hatra', 'Nisibis', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // -53 卡萊戰役大勝克拉蘇
      [-53]: ['Ctesiphon', 'Babylon', 'Hatra', 'Nisibis', 'Edessa', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Yerevan'],
      // 1 奧古斯都和議、亞美尼亞共管
      [1]: ['Ctesiphon', 'Babylon', 'Hatra', 'Nisibis', 'Edessa', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 63 提里達特斯加冕為亞美尼亞王（羅馬保護）
      [63]: ['Ctesiphon', 'Babylon', 'Hatra', 'Nisibis', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 117 圖拉真攻入泰西封
      [117]: ['Ctesiphon', 'Hatra', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 165 羅馬再侵
      [165]: ['Ctesiphon', 'Babylon', 'Hatra', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 198 塞普蒂米烏斯洗劫泰西封
      [198]: ['Ctesiphon', 'Hatra', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 224 亡於 Ardashir 薩珊
      [224]: ['Ctesiphon', 'Ecbatana', 'Susa', 'Estakhr', 'Persepolis'],
    },
  },
  {
    // 薩珊波斯 224~651（源 polygon 只 500~799）
    polygon_name: 'Sasanian Empire',
    name_zh: '薩珊',
    end_year: 651,
    years: {
      // 224 Ardashir I 建國於 Estakhr，滅帕提亞
      [224]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Hatra', 'Nisibis', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat'],
      // 260 Shapur I 擒羅馬皇帝瓦勒良於 Edessa
      [260]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Hatra', 'Nisibis', 'Edessa', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur', 'Antioch'],
      // 309 Shapur II 即位（70 年穩定期前夕）
      [309]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Nisibis', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur'],
      // 387 與羅馬瓜分亞美尼亞
      [387]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Nisibis', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur', 'Yerevan'],
      // 484 Peroz I 戰死於匈那
      [484]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Nisibis', 'Babylon', 'Nishapur', 'Merv', 'Gundeshapur'],
      // 531 Khosrow I 即位（最盛之治）
      [531]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Hatra', 'Nisibis', 'Edessa', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur', 'Yerevan'],
      // 614 Khosrow II 攻陷耶路撒冷
      [614]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Nisibis', 'Edessa', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur', 'Yerevan', 'Antioch', 'Damascus', 'Jerusalem', 'Alexandria', 'Memphis'],
      // 628 希拉克略反攻、和議
      [628]: ['Gor', 'Estakhr', 'Persepolis', 'Bishapur', 'Ctesiphon', 'Susa', 'Ecbatana', 'Nisibis', 'Babylon', 'Nishapur', 'Merv', 'Balkh', 'Herat', 'Gundeshapur'],
      // 651 末王 Yazdgerd III 死於 Merv，亡於阿拉伯
      [651]: ['Estakhr', 'Persepolis', 'Bishapur', 'Nishapur', 'Merv', 'Herat', 'Balkh'],
    },
  },
  // ============================================================
  // 古印度
  // ============================================================
  {
    // 孔雀王朝 -322~-185（源 polygon -300~-2 不準到末）
    polygon_name: 'Mauryan Empire',
    name_zh: '孔雀',
    end_year: -185,
    years: {
      // -322 旃陀羅笈多滅難陀、建孔雀
      [-322]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha'],
      // -305 戰勝塞琉古、取阿富汗東南
      [-305]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha', 'Taxila', 'Kandahar', 'Multan', 'Sind', 'Bharuch'],
      // -268 阿育王即位
      [-268]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha', 'Taxila', 'Kandahar', 'Multan', 'Sind', 'Bharuch', 'Sopara', 'Sanchi'],
      // -260 羯陵伽戰爭後（極盛、皈依佛教）
      [-260]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha', 'Taxila', 'Kandahar', 'Multan', 'Sind', 'Bharuch', 'Sopara', 'Sanchi', 'Kalinga', 'Tamralipti', 'Pundravardhana', 'Madurai'],
      // -232 阿育王崩
      [-232]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha', 'Taxila', 'Multan', 'Sind', 'Bharuch', 'Sopara', 'Sanchi', 'Kalinga', 'Tamralipti', 'Pundravardhana'],
      // -200 衰落期，西北已失
      [-200]: ['Pataliputra','Kannauj', 'Mathura', 'Ujjain', 'Vidisha', 'Bharuch', 'Sopara', 'Sanchi', 'Kalinga', 'Tamralipti', 'Pundravardhana'],
    },
  },
  {
    // 笈多王朝 320~550（源 polygon 300~599 含前後過寬）
    polygon_name: 'Gupta Empire',
    name_zh: '笈多',
    end_year: 550,
    years: {
      // 320 旃陀羅笈多一世建國，恆河中游
      [320]: ['Pataliputra','Kannauj', 'Mathura', 'Tamralipti'],
      // 350 海護王（Samudragupta）南征北討
      [350]: ['Pataliputra','Kannauj', 'Mathura', 'Vidisha', 'Sanchi', 'Tamralipti', 'Pundravardhana', 'Ujjain', 'Bharuch'],
      // 380 旃陀羅笈多二世滅西塞迦（極盛）
      [380]: ['Pataliputra','Kannauj', 'Mathura', 'Vidisha', 'Sanchi', 'Ujjain', 'Bharuch', 'Sopara', 'Tamralipti', 'Pundravardhana', 'Vallabhi', 'Ahmedabad', 'Multan'],
      // 415 鳩摩羅笈多時穩定
      [415]: ['Pataliputra','Kannauj', 'Mathura', 'Vidisha', 'Sanchi', 'Ujjain', 'Bharuch', 'Sopara', 'Tamralipti', 'Pundravardhana', 'Vallabhi', 'Ahmedabad'],
      // 480 匈那入侵
      [480]: ['Pataliputra','Kannauj', 'Mathura', 'Vidisha', 'Sanchi', 'Tamralipti', 'Pundravardhana'],
      // 530 末期分裂
      [530]: ['Pataliputra','Kannauj', 'Tamralipti', 'Pundravardhana'],
    },
  },
  {
    // 德里蘇丹國 1206~1526（源 polygon 1200~1529）
    polygon_name: 'Sultanate of Delhi',
    name_zh: '德里蘇丹國',
    end_year: 1526,
    years: {
      // 1206 古爾人 Qutb al-Din Aibak 建奴隸王朝
      [1206]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Ajmer','Kannauj', 'Mathura'],
      // 1236 伊勒圖什密末（已穩固北印度）
      [1236]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lakhnauti', 'Ujjain', 'Bharuch'],
      // 1296 阿拉烏丁哈勒吉即位
      [1296]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lakhnauti', 'Ujjain', 'Bharuch', 'Vidisha', 'Devagiri'],
      // 1320 圖格魯克即位
      [1320]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lakhnauti', 'Ujjain', 'Bharuch', 'Vidisha', 'Devagiri', 'Hyderabad', 'Bijapur'],
      // 1330 穆罕默德‧賓‧圖格魯克遷都德瓦吉里（極盛）
      [1330]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lakhnauti', 'Ujjain', 'Bharuch', 'Vidisha', 'Devagiri', 'Hyderabad', 'Bijapur', 'Madurai', 'Kandahar'],
      // 1351 菲魯茲沙時退守北印度
      [1351]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lakhnauti', 'Ujjain', 'Vidisha', 'Bharuch'],
      // 1398 帖木兒劫德里
      [1398]: ['Delhi', 'Multan', 'Sind', 'Kannauj', 'Mathura'],
      // 1414 賽義德王朝
      [1414]: ['Delhi', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lahore'],
      // 1500 洛迪王朝
      [1500]: ['Delhi', 'Multan', 'Sind', 'Kannauj', 'Mathura', 'Lahore', 'Ujjain'],
    },
  },
  {
    // 蒙兀兒帝國 1526~1707 極盛（源 polygon 1530~1782）
    polygon_name: 'Mughal Empire',
    name_zh: '蒙兀兒',
    end_year: 1707,
    years: {
      // 1526 巴布爾敗洛迪、立蒙兀兒於德里
      [1526]: ['Delhi', 'Agra', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kannauj'],
      // 1540 蘇爾人舍爾沙暫篡（中斷期，1540-55）
      [1540]: ['Kabul', 'Kandahar', 'Lahore'],
      // 1556 阿克巴即位、收復北印度
      [1556]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kannauj', 'Mathura'],
      // 1576 阿克巴併孟加拉
      [1576]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kandahar', 'Kannauj', 'Mathura', 'Ujjain', 'Bharuch', 'Ahmedabad', 'Lakhnauti', 'Dhaka', 'Vidisha', 'Vallabhi'],
      // 1605 阿克巴崩
      [1605]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kandahar', 'Kannauj', 'Mathura', 'Ujjain', 'Bharuch', 'Ahmedabad', 'Lakhnauti', 'Dhaka', 'Vidisha', 'Vallabhi', 'Surat'],
      // 1659 奧朗則布即位
      [1659]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kandahar', 'Kannauj', 'Mathura', 'Ujjain', 'Bharuch', 'Ahmedabad', 'Lakhnauti', 'Dhaka', 'Vidisha', 'Vallabhi', 'Surat', 'Devagiri'],
      // 1687 滅戈爾康達（南征極盛）
      [1687]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kandahar', 'Kannauj', 'Mathura', 'Ujjain', 'Bharuch', 'Ahmedabad', 'Lakhnauti', 'Dhaka', 'Vidisha', 'Vallabhi', 'Surat', 'Devagiri', 'Bijapur', 'Golconda', 'Hyderabad'],
      // 1700 奧朗則布暮年（疆域含整個次大陸）
      [1700]: ['Delhi', 'Lahore', 'Multan', 'Sind', 'Kabul', 'Kandahar', 'Kannauj', 'Mathura', 'Ujjain', 'Bharuch', 'Ahmedabad', 'Lakhnauti', 'Dhaka', 'Vidisha', 'Vallabhi', 'Surat', 'Devagiri', 'Bijapur', 'Golconda', 'Hyderabad', 'Madurai'],
    },
  },
  // ============================================================
  // 神聖羅馬帝國 962~1806
  // ============================================================
  {
    polygon_name: 'Holy Roman Empire',
    name_zh: '神聖羅馬',
    end_year: 1806,
    years: {
      // 962 鄂圖一世加冕（薩克森＋巴伐利亞＋義大利北）
      [962]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Magdeburg', 'Bremen', 'Hamburg', 'Rome', 'Ravenna', 'Pavia', 'Milan', 'Verona'],
      // 1024 薩利安王朝即位
      [1024]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Rome', 'Ravenna', 'Pavia', 'Milan', 'Verona', 'Florence', 'Strasbourg', 'Basel', 'Zurich', 'Bern', 'Prague'],
      // 1077 卡諾莎之辱（敘任權鬥爭）
      [1077]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Ravenna', 'Pavia', 'Milan', 'Verona', 'Florence', 'Genoa', 'Bologna', 'Strasbourg', 'Basel', 'Zurich', 'Bern', 'Prague'],
      // 1155 巴巴羅薩加冕、義大利政策
      [1155]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Ravenna', 'Pavia', 'Milan', 'Verona', 'Florence', 'Genoa', 'Bologna', 'Strasbourg', 'Basel', 'Zurich', 'Bern', 'Prague', 'Vienna', 'Trento'],
      // 1250 腓特烈二世崩、大空位期
      [1250]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Strasbourg', 'Basel', 'Zurich', 'Bern', 'Prague', 'Vienna', 'Trento'],
      // 1356 金璽詔書（七選帝侯）
      [1356]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Strasbourg', 'Basel', 'Zurich', 'Bern', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg'],
      // 1453 哈布斯堡掌帝位
      [1453]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Strasbourg', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck', 'Brussels', 'Antwerp', 'Utrecht'],
      // 1556 查理五世退位、奧西分家
      [1556]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Strasbourg', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck', 'Brussels', 'Antwerp', 'Utrecht'],
      // 1648 西發里亞和約（瑞士/荷蘭正式脫離）
      [1648]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Strasbourg', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck'],
      // 1681 法併斯特拉斯堡
      [1681]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck'],
      // 1740 瑪麗亞‧特蕾莎即位（西里西亞戰爭前）
      [1740]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck'],
      // 1789 法國大革命前夕
      [1789]: ['Aachen', 'Frankfurt', 'Mainz', 'Cologne', 'Trier', 'Worms', 'Speyer', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck'],
      // 1803 帝國代表重要決議（俗世化）
      [1803]: ['Frankfurt', 'Regensburg', 'Augsburg', 'Munich', 'Nuremberg', 'Magdeburg', 'Bremen', 'Hamburg', 'Lubeck', 'Prague', 'Vienna', 'Trento', 'Dresden', 'Leipzig', 'Salzburg', 'Innsbruck'],
    },
  },
  // ============================================================
  // 美洲（阿茲特克 + 印加）
  // ============================================================
  {
    // 阿茲特克 1428~1521（源 polygon 只 1500~1529 一格）
    polygon_name: 'Aztec Empire',
    name_zh: '阿茲特克',
    end_year: 1521,
    years: {
      // 1428 三方聯盟成立（Tenochtitlan + Texcoco + Tlacopan 滅 Azcapotzalco）
      [1428]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula'],
      // 1440 蒙特蘇馬一世擴張
      [1440]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula', 'Cempoala', 'Cuetlaxtla', 'Mixquiahuala'],
      // 1469 阿薩亞卡特即位
      [1469]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula', 'Cempoala', 'Cuetlaxtla', 'Tula', 'Mixquiahuala', 'Oaxaca'],
      // 1486 阿維索托即位（南擴 Soconusco）
      [1486]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula', 'Cempoala', 'Cuetlaxtla', 'Tula', 'Mixquiahuala', 'Oaxaca', 'Tehuantepec', 'Soconusco'],
      // 1502 蒙特蘇馬二世即位（極盛、含灣岸與南境）
      [1502]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula', 'Cempoala', 'Cuetlaxtla', 'Tula', 'Mixquiahuala', 'Oaxaca', 'Tehuantepec', 'Soconusco', 'Tuxpan'],
      // 1519 科爾特斯登陸
      [1519]: ['Tenochtitlan', 'Texcoco', 'Tlacopan', 'Xochimilco', 'Cholula', 'Cempoala', 'Cuetlaxtla', 'Tula', 'Mixquiahuala', 'Oaxaca', 'Tehuantepec', 'Soconusco', 'Tuxpan'],
    },
  },
  {
    // 印加 1438~1533（源 polygon 1500~1649 過晚——印加 1533 已亡）
    polygon_name: 'Inca Empire',
    name_zh: '印加',
    end_year: 1533,
    years: {
      // 1438 帕查庫特克擊敗昌卡（建塔萬廷蘇尤）
      [1438]: ['Cuzco', 'Pachacamac'],
      // 1463 征服 Chimu（北沿海）
      [1463]: ['Cuzco', 'Pachacamac', 'ChanChan', 'TrujilloAndes', 'Huancayo'],
      // 1471 圖帕克‧印加即位（南北擴張）
      [1471]: ['Cuzco', 'Pachacamac', 'ChanChan', 'TrujilloAndes', 'Huancayo', 'Cajamarca', 'Tomebamba', 'Quito', 'Arequipa', 'LaPaz'],
      // 1493 瓦伊納‧卡帕克即位（北至 Pasto）
      [1493]: ['Cuzco', 'Pachacamac', 'ChanChan', 'TrujilloAndes', 'Huancayo', 'Cajamarca', 'Tomebamba', 'Quito', 'Pasto', 'Arequipa', 'LaPaz', 'SucreInca', 'PotosiInca', 'SantiagoInca'],
      // 1525 瓦伊納‧卡帕克死於天花、南北分裂前極盛
      [1525]: ['Cuzco', 'Pachacamac', 'ChanChan', 'TrujilloAndes', 'Huancayo', 'Cajamarca', 'Tomebamba', 'Quito', 'Pasto', 'Arequipa', 'LaPaz', 'SucreInca', 'PotosiInca', 'SantiagoInca', 'TalcaInca', 'MendozaInca', 'TucumanInca'],
      // 1532 皮薩羅擒阿塔瓦爾帕於 Cajamarca
      [1532]: ['Cuzco', 'Pachacamac', 'ChanChan', 'TrujilloAndes', 'Huancayo', 'Cajamarca', 'Tomebamba', 'Quito', 'Arequipa', 'LaPaz', 'SucreInca', 'PotosiInca', 'SantiagoInca', 'TalcaInca'],
      // 1533 阿塔瓦爾帕被殺、印加亡
      [1533]: ['Cuzco', 'Vilcabamba', 'Pachacamac', 'Huancayo', 'Cajamarca'],
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
      // 單點：畫一個小方塊（~50 km 邊）— CW（d3-geo 球面慣例：CW = 內部小區域）
      const [lon, lat] = coords[0]
      const d = 0.5
      ring = [[lon - d, lat - d], [lon - d, lat + d], [lon + d, lat + d], [lon + d, lat - d], [lon - d, lat - d]]
    } else if (coords.length === 2) {
      // 兩點：畫一個長方形包圍 — CW
      const [lon1, lat1] = coords[0]
      const [lon2, lat2] = coords[1]
      const minLon = Math.min(lon1, lon2) - 0.5, maxLon = Math.max(lon1, lon2) + 0.5
      const minLat = Math.min(lat1, lat2) - 0.5, maxLat = Math.max(lat1, lat2) + 0.5
      ring = [[minLon, minLat], [minLon, maxLat], [maxLon, maxLat], [maxLon, minLat], [minLon, minLat]]
    } else {
      // d3-geo spherical winding: CW (in geographic coords) = interior small region.
      // Graham scan outputs mathematical CCW → reverse for d3-geo.
      const hull = convexHull(coords).reverse()
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
