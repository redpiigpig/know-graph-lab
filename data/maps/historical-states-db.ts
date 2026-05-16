/**
 * 歷史國家資料庫
 *
 * 兩層架構：
 * 1. **骨架（skeleton）** — 自動從 historical-states.geojson + sphere-fills 抽出。
 *    每個 NAME（不重複）一筆，含：英文名、最早起始年、最晚結束年、涵蓋的現代國家。
 *    來源：`scripts/generate_state_skeleton.mjs` 產出 `public/maps/state-skeleton.json`
 * 2. **詳細（details）** — 本檔人工撰寫的進階欄位：中文名、朝代、人口、面積、簡介等。
 *    依 NAME（英文）為 key 與骨架 merge。
 *
 * 用 `loadStatesDb()` 或 `useStatesDb()` 拿到合併後的完整清單。
 */

export interface StateSkeleton {
  /** 英文官方名稱（直接取自 historical-basemaps NAME） */
  name_en: string
  /** 最早出現年（天文年；多 snapshot 取最早） */
  earliest_from: number
  /** 最晚出現年（天文年；9999 = 至今） */
  latest_to: number
  /** 涵蓋的現代國家 ISO_A3 list（從 sphere-fills 交集統計） */
  modern_countries: string[]
  /** 出現於哪些 snapshot 年份 */
  snapshots: number[]
}

export interface StateDetail {
  /** 中文名稱 */
  name_zh?: string
  /** 統治家族／王朝（依時序） */
  dynasties?: string[]
  /** 巔峰時期人口（萬人單位；缺 = 未知） */
  population_peak_wan?: number
  /** 巔峰時期土地面積（萬平方公里） */
  area_peak_wan_km2?: number
  /** 主要首都／重要城市 */
  capitals?: string[]
  /** 主要宗教／信仰 */
  religions?: string[]
  /** 簡介（一段話） */
  intro?: string
  /** 後繼者（後續國家英文 NAME） */
  successors?: string[]
  /** 前身者（前個國家英文 NAME） */
  predecessors?: string[]
  /** 所屬文化界域 / sphere（若可歸類） */
  realm_id?: string
  sphere_id?: string
}

export interface WikidataState {
  qid: string
  name_en: string
  name_zh: string | null
  inception_year: number | null
  dissolved_year: number | null
  continents: string[]
}

export interface HistoricalState extends Partial<StateSkeleton>, StateDetail {
  /** Slug id（snake_case 化的英文名） */
  id: string
  /** 細節是否已填（false = 只有骨架資料） */
  has_detail: boolean
  /** 是否有歷史 polygon（historical-basemaps）— 可在地圖上看到 */
  has_polygon: boolean
  /** 英文名（必有） */
  name_en: string
  /** Wikidata QID（若來自 Wikidata） */
  qid?: string
  /** 來源所在大陸（Wikidata 提供） */
  continents?: string[]
  /** 起始年（合併 skeleton.earliest_from + wikidata.inception_year，取較早） */
  year_start: number | null
  /** 結束年 */
  year_end: number | null
  /** realm/sphere 是否來自自動推斷（true = inference；false = 人工填或無） */
  has_inferred_sphere?: boolean
}

/**
 * 人工撰寫的詳細資料表。Key = 英文 NAME（與 historical-states.geojson 對應）
 * 持續擴充中——目前已填 ~50 個重要國家，剩餘為骨架。
 */
export const STATE_DETAILS: Record<string, StateDetail> = {
  // ========== 早期文明 (-4000 ~ -2000 BCE) ==========
  'Ur': {
    name_zh: '烏爾',
    dynasties: ['烏爾第一王朝', '烏爾第二王朝', '烏爾第三王朝（-2112~-2004）'],
    capitals: ['烏爾'],
    religions: ['蘇美多神教（南那、辛、伊南娜）'],
    realm_id: 'central', sphere_id: 'sumerian',
    intro: '蘇美文明南部最重要的城邦之一，吉爾伽美什起源地周邊。烏爾第三王朝為蘇美最後的偉大王朝，亡於埃蘭人之手。',
    successors: ['Akkadian Empire', 'Sumero-Akkadian'],
  },
  'Hurrian Kingdoms': {
    name_zh: '胡里安諸邦',
    dynasties: ['Mitanni 米坦尼（後期，-1500~-1300）'],
    religions: ['胡里安多神教（特舒蔔暴風神）'],
    realm_id: 'central',
    intro: '北美索不達米亞與安納托利亞東部的胡里安語族城邦。後形成米坦尼帝國，與赫梯/埃及鼎立。',
  },
  'Elam': {
    name_zh: '埃蘭',
    dynasties: ['原始埃蘭（-3200）', 'Awan', 'Simashki', 'Sukkalmah', '中埃蘭', '新埃蘭'],
    capitals: ['蘇薩（Susa）', '安善（Anshan）'],
    religions: ['埃蘭多神教（Inshushinak、Pinikir）'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '伊朗高原西南部的非印歐文明。原始埃蘭文字 -3200，與蘇美並世發展。-539 被阿契美尼德波斯吞併。',
    successors: ['Achaemenid Empire'],
  },
  'Egypt': {
    name_zh: '埃及',
    dynasties: ['前王朝', '早王朝 1-2', '古王國 3-6', '中王國 11-12', '新王國 18-20', '後期王朝', 'Ptolemaic 托勒密'],
    capitals: ['孟菲斯', '底比斯', '亞歷山卓'],
    religions: ['埃及多神教', '基督教（科普特）', '伊斯蘭教（後期）'],
    realm_id: 'central', sphere_id: 'egyptian',
    intro: '尼羅河流域古老文明。-3100 上下埃及統一、聖書體成型。歷經 30+ 王朝，-30 BC 落入羅馬。',
    population_peak_wan: 500,
    area_peak_wan_km2: 100,
  },
  'Indus valley civilization': {
    name_zh: '印度河文明',
    capitals: ['哈拉帕', '摩亨佐達羅', '羅塔爾'],
    religions: ['原始達羅毗荼信仰（推測）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '南亞最早城市文明（-2600~-1900）。象形文字未解。約 -1900 神祕衰落，可能與氣候變化、雅利安遷徙有關。',
    population_peak_wan: 500,
    area_peak_wan_km2: 125,
  },
  'Minoan': {
    name_zh: '米諾斯',
    capitals: ['克諾索斯', '費斯托斯', '馬利亞'],
    religions: ['米諾斯多神教（蛇女神）'],
    realm_id: 'central', sphere_id: 'aegean-asia-minor',
    intro: '克里特島青銅時代文明（-2700~-1450）。線形文字 A 未解。可能毀於聖托里尼火山或邁錫尼入侵。',
  },
  'Norte Chico': {
    name_zh: '小北文明（卡拉爾）',
    capitals: ['卡拉爾'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '美洲最早城市文明（-3000~-1800）。秘魯中部沿海。無陶器但有複雜建築與量子記繩（Quipu 原型）。',
  },

  // ========== 青銅時代 (-2000 ~ -1200 BCE) ==========
  'Hittites': {
    name_zh: '赫梯',
    dynasties: ['古王國（-1750~-1500）', '新王國／帝國（-1500~-1180）'],
    capitals: ['哈圖薩（Hattusa）'],
    religions: ['赫梯多神教（千神之國）'],
    realm_id: 'central', sphere_id: 'anatolia',
    intro: '安納托利亞印歐語青銅時代帝國。-1595 攻陷古巴比倫。-1274 卡迭石戰役對抗埃及。-1180 海上民族入侵終結。',
    population_peak_wan: 200,
    area_peak_wan_km2: 60,
  },
  'Canaan': {
    name_zh: '迦南',
    capitals: ['烏加里特', '比布魯斯', '杰里科'],
    religions: ['迦南多神教（巴力、亞舍拉、阿納特）'],
    realm_id: 'central', sphere_id: 'canaan',
    intro: '黎凡特青銅時代諸城邦。烏加里特字母為腓尼基字母前身。',
  },
  'Xia': {
    name_zh: '夏',
    dynasties: ['夏（傳說 -2070~-1600）'],
    capitals: ['二里頭（推測）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '中國傳說中第一個朝代。考古上對應二里頭文化。文字未確定為甲骨文前身。',
    successors: ['Shang'],
  },

  // ========== 鐵器時代 (-1200 ~ -540 BCE) ==========
  'Assyria': {
    name_zh: '亞述',
    dynasties: ['古亞述', '中亞述', '新亞述帝國（-911~-609）'],
    capitals: ['亞述城', '尼姆魯德', '尼尼微', '霍爾薩巴德'],
    religions: ['亞述多神教（亞述爾國神）'],
    realm_id: 'central', sphere_id: 'assyrian',
    intro: '北美索不達米亞尚武帝國。新亞述為第一個跨地域大帝國。-612 巴比倫聯合米底攻陷尼尼微。',
    population_peak_wan: 2500,
    area_peak_wan_km2: 140,
  },
  'Babylonia': {
    name_zh: '巴比倫',
    dynasties: ['古巴比倫（漢摩拉比）', '加喜特巴比倫', '新巴比倫（迦勒底）'],
    capitals: ['巴比倫城'],
    religions: ['巴比倫多神教（馬爾杜克）'],
    realm_id: 'central', sphere_id: 'babylonian',
    intro: '南美索不達米亞宗教與學術中心。漢摩拉比法典 -1754。新巴比倫尼布甲尼撒二世毀第一聖殿。-539 落入波斯。',
    population_peak_wan: 1500,
    area_peak_wan_km2: 50,
  },
  'Saba': {
    name_zh: '示巴',
    capitals: ['馬里布（Marib）'],
    religions: ['南阿拉伯多神教（Almaqah 月神）'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '葉門古王國（-1200~ 275 CE）。有獨立的南阿拉伯字母與灌溉農業。聖經所羅門王時代示巴女王傳說背景。',
  },
  'Urartu': {
    name_zh: '烏拉爾圖',
    capitals: ['圖什帕（凡湖）'],
    realm_id: 'central', sphere_id: 'caucasus',
    intro: '亞美尼亞高地的鐵器王國（-860~-590）。常與新亞述交戰。可能是亞美尼亞文明的前身。',
  },
  'Olmec': {
    name_zh: '奧爾梅克',
    capitals: ['聖洛倫佐', '拉文塔'],
    religions: ['美洲虎崇拜', '羽蛇神原型'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '中美洲文明之母（-1500~-400）。巨石頭像聞名。',
  },
  'Chavin': {
    name_zh: '查文',
    capitals: ['查文德萬塔爾'],
    religions: ['林克斯神／蘭森神'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '安地斯山中部宗教文化（-900~-200）。複雜的石雕傳統。',
  },

  // ========== 古典帝國 (-500 BCE ~ 500 CE) ==========
  'Achaemenid Empire': {
    name_zh: '阿契美尼德波斯',
    dynasties: ['居魯士、岡比西斯、大流士、薛西斯'],
    capitals: ['波斯波利斯', '蘇薩', '帕薩爾加德', '巴比倫'],
    religions: ['瑣羅亞斯德教（官方）', '多元宗教寬容'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '世界第一個橫跨歐亞非的帝國（-559~-330）。-539 居魯士征服巴比倫。-330 亞歷山大滅之。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 550,
  },
  'Greek city-states': {
    name_zh: '希臘城邦',
    capitals: ['雅典', '斯巴達', '科林斯', '底比斯'],
    religions: ['奧林帕斯多神'],
    realm_id: 'central', sphere_id: 'aegean-asia-minor',
    intro: '古典希臘的政治形態。城邦競爭、民主萌芽、哲學黃金時代。',
  },
  'Rome': {
    name_zh: '羅馬',
    dynasties: ['王政（-753~-509）', '共和（-509~-27）', '帝國（-27~395）'],
    capitals: ['羅馬', '君士坦丁堡（東部）'],
    religions: ['羅馬多神教', '基督教（4 世紀後）'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '從拉丁部落擴張至橫跨地中海的帝國。布匿戰爭擊敗迦太基。-27 屋大維建帝國。476 西羅馬亡。',
    population_peak_wan: 7000,
    area_peak_wan_km2: 500,
  },
  'Carthaginian Empire': {
    name_zh: '迦太基帝國',
    capitals: ['迦太基（突尼斯外）'],
    religions: ['腓尼基多神教（巴力哈蒙、塔尼特）'],
    realm_id: 'western', sphere_id: 'carthaginian-maghreb',
    intro: '腓尼基殖民地發展成的海洋帝國。三次布匿戰爭（-264~-146）敗於羅馬。漢尼拔。',
  },
  'Maurya Empire': {
    name_zh: '孔雀王朝',
    dynasties: ['月護王、賓頭娑羅、阿育王'],
    capitals: ['華氏城（Pataliputra）'],
    religions: ['佛教（阿育王推廣）', '印度教', '耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度第一個統一帝國（-322~-185）。阿育王推廣佛教至東南亞與斯里蘭卡。',
    population_peak_wan: 1.5e4,
    area_peak_wan_km2: 500,
  },
  'Han Empire': {
    name_zh: '漢帝國',
    dynasties: ['西漢（-202~9）', '新莽', '東漢（25~220）'],
    capitals: ['長安', '洛陽'],
    religions: ['儒家國教', '黃老／早期道教', '佛教傳入'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '中國第二個大一統帝國。絲綢之路開通。獨尊儒術。',
    population_peak_wan: 6000,
    area_peak_wan_km2: 600,
  },
  'Roman Empire': {
    name_zh: '羅馬帝國',
    dynasties: ['朱里亞-克勞狄', '弗拉維', '安東尼', '塞維魯', '君士坦丁', '狄奧多西'],
    capitals: ['羅馬', '君士坦丁堡（330 CE 後）'],
    religions: ['羅馬多神教', '基督教（313 合法、380 國教）'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '橫跨三洲的古典帝國。圖拉真時代（98~117）達到巔峰。395 分為東西兩部。',
    population_peak_wan: 7000,
    area_peak_wan_km2: 500,
  },
  'Parthian Empire': {
    name_zh: '帕提亞（安息）',
    capitals: ['泰西封（Ctesiphon）', '尼薩'],
    religions: ['瑣羅亞斯德教', '希臘化-伊朗融合'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '伊朗游牧建立的帝國（-247~224）。與羅馬百年對抗，承接阿契美尼德傳統。被薩珊推翻。',
  },
  'Aksum': {
    name_zh: '阿克蘇姆',
    capitals: ['阿克蘇姆'],
    religions: ['衣索比亞正教（4 世紀皈依）'],
    realm_id: 'southern', sphere_id: 'ethiopian',
    intro: '衣索比亞高地的早期基督教王國（100~940 CE）。世界少數早期皈依基督教的國家。',
  },

  // ========== 古代晚期 / 中世紀 (500 ~ 1500 CE) ==========
  'Sasanian Empire': {
    name_zh: '薩珊波斯',
    dynasties: ['Ardashir 阿爾達希爾起'],
    capitals: ['泰西封'],
    religions: ['瑣羅亞斯德教國教', '景教/摩尼教存在'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '波斯第二帝國（224~651）。與拜占庭百年對抗。651 亡於阿拉伯。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 350,
  },
  'Byzantine Empire': {
    name_zh: '拜占庭帝國',
    capitals: ['君士坦丁堡'],
    religions: ['東正教'],
    realm_id: 'central', sphere_id: 'aegean-asia-minor',
    intro: '東羅馬帝國延續，正式國名「羅馬人帝國」（330~1453）。1453 君士坦丁堡陷落於奧斯曼。',
    population_peak_wan: 3000,
    area_peak_wan_km2: 270,
  },
  'Gupta Empire': {
    name_zh: '笈多帝國',
    dynasties: ['Chandragupta I', 'Samudragupta', 'Chandragupta II'],
    capitals: ['華氏城', '烏闍衍那'],
    religions: ['印度教（黃金時代）', '佛教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度古典時代帝國（320~550）。梵文古典文學高峰。那爛陀大學。',
    population_peak_wan: 1.2e4,
  },
  'Tang Empire': {
    name_zh: '唐',
    dynasties: ['李唐'],
    capitals: ['長安', '洛陽'],
    religions: ['佛教全盛', '景教/祆教/摩尼教傳入'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '中華文化的世界主義巔峰（618~907）。長安為當時世界最大都市。詩唐。',
    population_peak_wan: 8000,
    area_peak_wan_km2: 1240,
  },
  'Rashidun Caliphate': {
    name_zh: '正統哈里發',
    dynasties: ['Abu Bakr、Umar、Uthman、Ali'],
    capitals: ['麥地那', '庫法'],
    religions: ['伊斯蘭教'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '伊斯蘭教第一代哈里發（632~661）。穆罕默德四大繼任者統治。橫掃波斯與拜占庭東部。',
  },
  'Umayyad Caliphate': {
    name_zh: '伍麥亞哈里發',
    dynasties: ['伍麥亞家族'],
    capitals: ['大馬士革'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '阿拉伯帝國第一個世襲王朝（661~750）。版圖從伊比利至中亞，史上面積最大伊斯蘭帝國之一。',
    area_peak_wan_km2: 1100,
  },
  'Abbasid Caliphate': {
    name_zh: '阿巴斯哈里發',
    dynasties: ['阿巴斯家族'],
    capitals: ['巴格達'],
    religions: ['伊斯蘭遜尼派', '蘇非主義興起'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '伊斯蘭黃金時代（750~1258）。巴格達智慧之家。1258 蒙古滅之。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 1100,
  },
  'Carolingian Empire': {
    name_zh: '加洛林帝國',
    dynasties: ['查理曼、虔誠者路易'],
    capitals: ['亞琛'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'gallic-french',
    intro: '法蘭克人加洛林王朝建立的歐洲帝國（800~888）。800 年查理曼加冕為「羅馬人皇帝」。',
    area_peak_wan_km2: 110,
  },
  'Mongol Empire': {
    name_zh: '蒙古帝國',
    dynasties: ['成吉思汗、窩闊台、貴由、蒙哥、忽必烈'],
    capitals: ['哈拉和林', '大都（北京）'],
    religions: ['薩滿、藏傳佛教、伊斯蘭、景教等寬容'],
    realm_id: 'northern', sphere_id: 'mongolic-tungusic',
    intro: '人類歷史上最大的陸上帝國（1206~1368）。橫跨歐亞，分裂為四大汗國。',
    area_peak_wan_km2: 2400,
    population_peak_wan: 1.1e4,
  },
  'Song Empire': {
    name_zh: '宋',
    dynasties: ['北宋（960~1127）', '南宋（1127~1279）'],
    capitals: ['汴京（開封）', '臨安（杭州）'],
    religions: ['新儒學（理學）', '禪宗', '道教'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '宋朝以文治、商業、科技聞名。活字印刷、火藥、指南針。',
    population_peak_wan: 1.2e4,
  },
  'Yuan Empire': {
    name_zh: '元',
    dynasties: ['元世祖忽必烈起'],
    capitals: ['大都（北京）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '蒙古入主中原建立的王朝（1271~1368）。',
    population_peak_wan: 8500,
    area_peak_wan_km2: 1300,
  },
  'Holy Roman Empire': {
    name_zh: '神聖羅馬帝國',
    dynasties: ['奧托、薩利安、霍亨斯陶芬、哈布斯堡'],
    capitals: ['亞琛、布拉格、維也納（後期）'],
    religions: ['天主教', '新教（宗教改革後）'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '德意志-中歐帝國（962~1806）。「既不神聖也不羅馬，更不是帝國」。',
  },
  'Khmer Empire': {
    name_zh: '高棉帝國',
    capitals: ['吳哥（Angkor）'],
    religions: ['印度教 → 上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '東南亞中世紀大國（802~1431）。吳哥窟。最終被泰人推翻。',
  },

  // ========== 近世帝國 (1500 ~ 1800 CE) ==========
  'Ottoman Empire': {
    name_zh: '奧斯曼帝國',
    dynasties: ['奧斯曼家族'],
    capitals: ['伊斯坦堡（攻陷君士坦丁堡 1453）'],
    religions: ['伊斯蘭遜尼派', '東正教（米利特）'],
    realm_id: 'central', sphere_id: 'anatolia',
    intro: '橫跨歐亞非的伊斯蘭帝國（1299~1922）。終結拜占庭。最大時人口 3000 萬。',
    population_peak_wan: 3500,
    area_peak_wan_km2: 520,
  },
  'Ming Empire': {
    name_zh: '明',
    dynasties: ['朱明'],
    capitals: ['南京 → 北京（1421）'],
    religions: ['儒道佛三教', '天主教（利瑪竇 1583）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '明朝（1368~1644）。鄭和下西洋。長城修建。陽明心學。',
    population_peak_wan: 1.6e4,
    area_peak_wan_km2: 650,
  },
  'Aztec Empire': {
    name_zh: '阿茲特克',
    capitals: ['特諾奇蒂特蘭（今墨西哥城）'],
    religions: ['Huitzilopochtli、Tlaloc 等多神'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '前哥倫布墨西哥中部帝國（1428~1521）。1521 被科爾特斯與原住民聯軍滅。',
    population_peak_wan: 500,
  },
  'Inca Empire': {
    name_zh: '印加帝國',
    capitals: ['庫斯科', '馬丘比丘'],
    religions: ['Inti（太陽神）'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '南美最大的前哥倫布帝國（1438~1533）。庫斯科為「世界肚臍」。1533 被皮薩羅滅。',
    population_peak_wan: 1000,
    area_peak_wan_km2: 200,
  },
  'Mughal Empire': {
    name_zh: '蒙兀兒帝國',
    dynasties: ['Babur、Akbar、Aurangzeb 等'],
    capitals: ['德里、阿格拉'],
    religions: ['伊斯蘭遜尼派', '宗教融合（阿克巴的 Din-i Ilahi）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度伊斯蘭大帝國（1526~1857）。泰姬瑪哈陵。1857 英印起義後正式廢除。',
    population_peak_wan: 1.5e4,
    area_peak_wan_km2: 400,
  },
  'Qing Empire': {
    name_zh: '清',
    dynasties: ['愛新覺羅'],
    capitals: ['北京'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '滿洲入關（1644~1912）。康雍乾盛世。19 世紀屢敗於列強。',
    population_peak_wan: 4.5e4,
    area_peak_wan_km2: 1300,
  },
  'Russian Empire': {
    name_zh: '俄羅斯帝國',
    dynasties: ['羅曼諾夫'],
    capitals: ['莫斯科 → 聖彼得堡（1712）'],
    religions: ['東正教'],
    realm_id: 'northern', sphere_id: 'russian-tatar',
    intro: '橫跨歐亞的帝國（1721~1917）。彼得大帝西化。葉卡捷琳娜大擴張。1917 革命終結。',
    population_peak_wan: 1.8e4,
    area_peak_wan_km2: 2300,
  },
  'British Empire': {
    name_zh: '大英帝國',
    capitals: ['倫敦'],
    religions: ['英國國教'],
    realm_id: 'western', sphere_id: 'british-celtic',
    intro: '「日不落帝國」。19-20 世紀世界最大帝國，殖民全球四分之一陸地。',
    area_peak_wan_km2: 3550,
    population_peak_wan: 4.6e4,
  },

  // ========== 殖民帝國 ==========
  'Portugal': {
    name_zh: '葡萄牙',
    dynasties: ['勃艮第（1139-1383）', '阿維什（1385-1580）', '哈布斯堡（1580-1640）', '布拉甘薩（1640-1910）'],
    capitals: ['吉馬良斯', '科英布拉', '里斯本'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '海上探險先驅。1488 迪亞士抵好望角、1498 達伽馬到印度、1500 卡布拉爾發現巴西。曾統治巴西、安哥拉、莫三比克、澳門、東帝汶。1580-1640 與西班牙聯合。',
    area_peak_wan_km2: 1040,
    population_peak_wan: 6000,
  },
  'Dutch Republic': {
    name_zh: '荷蘭共和國',
    dynasties: ['七省聯合共和（奧蘭治家族執政）'],
    capitals: ['阿姆斯特丹', '海牙'],
    religions: ['加爾文宗', '天主教（少數）'],
    realm_id: 'western', sphere_id: 'low-countries',
    intro: '1581 從西班牙獨立。17 世紀黃金時代，東印度公司（VOC）為世界首家跨國公司。海外擁台灣／印尼／南非開普殖民地／新阿姆斯特丹（後紐約）。',
    area_peak_wan_km2: 250,
    population_peak_wan: 200,
  },

  // ========== 法蘭克／加洛林 ==========
  'Frankish Kingdom': {
    name_zh: '法蘭克王國',
    dynasties: ['墨洛溫（481-751）', '加洛林（751-初期）'],
    capitals: ['蘇瓦松', '巴黎', '亞琛'],
    religions: ['天主教（克洛維皈依 496）'],
    realm_id: 'western', sphere_id: 'gallic-french',
    intro: '481 克洛維建國。496 接受天主教，奠定西歐基督教王國模型。732 圖爾戰役查理‧馬特擊敗倭馬亞。751 丕平篡墨洛溫立加洛林。',
    successors: ['Carolingian Empire'],
  },

  // ========== 印度諸朝 ==========
  'Mauryan Empire': {
    name_zh: '孔雀王朝',
    dynasties: ['月護王（-322~-298）', '賓頭娑羅', '阿育王（-268~-232）'],
    capitals: ['華氏城（Pataliputra）'],
    religions: ['佛教（阿育王推廣）', '印度教', '耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度第一個統一帝國（-322~-185）。阿育王皈依佛教後派宣教士到斯里蘭卡、希臘化諸國。極盛覆蓋次大陸大部。',
    population_peak_wan: 1.5e4,
    area_peak_wan_km2: 500,
  },
  'Sultanate of Delhi': {
    name_zh: '德里蘇丹國',
    dynasties: ['奴隸（1206-1290）', '卡爾吉（1290-1320）', '圖格魯克（1320-1414）', '賽義德（1414-1451）', '洛迪（1451-1526）'],
    capitals: ['德里'],
    religions: ['伊斯蘭遜尼', '印度教（多數人口）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '北印度第一個伊斯蘭大帝國（1206-1526）。圖格魯克時期橫跨次大陸大部。1398 帖木兒劫德里為轉折。1526 巴布爾在帕尼帕特戰役推翻洛迪，蒙兀兒繼之。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 320,
    successors: ['Mughal Empire'],
  },
  'Chola state': {
    name_zh: '朱羅國',
    dynasties: ['帝國朱羅（羅闍羅闍 985-1014、羅貞陀羅 1014-1044）'],
    capitals: ['坦賈武爾'],
    religions: ['濕婆派印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '南印度與斯里蘭卡的海上帝國。1025 朱羅遠征蘇門答臘攻擊室利佛逝為印度史唯一大規模海外遠征。建築（布里哈迪斯瓦拉廟）、文學（坦米爾）、行政（地方議會制）皆有獨特成就。',
    population_peak_wan: 1500,
    area_peak_wan_km2: 100,
  },
  'Vijayanagara': {
    name_zh: '毗奢耶那伽羅',
    dynasties: ['桑伽馬（1336-1485）', '薩魯瓦（1485-1505）', '圖盧瓦（1505-1565）', '阿拉維杜（1565-1646）'],
    capitals: ['哈姆皮（Hampi）'],
    religions: ['印度教（薩魯瓦／毗濕奴派）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '南印度抵抗伊斯蘭蘇丹國的最大印度教帝國（1336-1646）。1565 塔利科塔戰役被德干蘇丹聯軍擊敗、哈姆皮被洗劫，從此衰退。',
    population_peak_wan: 2500,
    area_peak_wan_km2: 130,
  },
  'Maratha Confederacy': {
    name_zh: '馬拉塔聯盟',
    dynasties: ['希瓦吉（1674-1680）', '佩什瓦（巴拉吉‧維什瓦納特 1714 起）'],
    capitals: ['萊加德', '浦那'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '與蒙兀兒對抗的印度教聯邦（1674-1818）。1707 奧朗則布死後快速擴張，1761 第三次帕尼帕特戰役敗於阿富汗杜蘭尼為轉折。1818 三次英馬戰爭後被英印滅。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 250,
  },
  'Palas': {
    name_zh: '波羅王朝',
    dynasties: ['瞿波羅（750 立）', '達摩波羅', '提婆波羅（巔峰）'],
    capitals: ['超戒寺', '那爛陀附近'],
    religions: ['大乘佛教（密教興盛）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '東印度孟加拉／比哈爾的佛教王朝（750-1162）。超戒寺與那爛陀寺為當時世界佛教中心。藏傳佛教的後弘期傳承多由波羅學者完成。',
    area_peak_wan_km2: 60,
  },

  // ========== 東南亞 ==========
  'Srivijaya Empire': {
    name_zh: '室利佛逝',
    capitals: ['巨港（Palembang）'],
    religions: ['大乘佛教', '密教'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '蘇門答臘的海上貿易帝國（650-1290）。控制麻六甲與巽他海峽。義淨來印途中曾停留學梵文。1025 朱羅突襲後衰退，最終被滿者伯夷取代。',
    area_peak_wan_km2: 80,
  },
  'Bagan': {
    name_zh: '蒲甘王朝',
    dynasties: ['阿奴律陀（1044 立）'],
    capitals: ['蒲甘'],
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '緬甸第一個統一王朝（1044-1287）。1057 滅孟族直通國取得上座部佛教傳統。蒲甘古城有 3,800+ 座佛塔遺跡。1287 蒙古入侵後分裂。',
    area_peak_wan_km2: 90,
  },
  'Ayutthaya': {
    name_zh: '阿瑜陀耶王朝',
    dynasties: ['烏通王（1351 立）', '巴薩通'],
    capitals: ['阿瑜陀耶'],
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '泰國中世紀-近世王朝（1351-1767）。1431 攻陷吳哥。國際商業中心，與荷／英／法／日本通商。1767 緬甸貢榜王朝攻陷後遷都。',
    population_peak_wan: 200,
    area_peak_wan_km2: 50,
    successors: ['Rattanakosin Kingdom'],
  },
  'Đại Việt': {
    name_zh: '大越',
    dynasties: ['李（1009-1225）', '陳（1225-1400）', '胡（1400-1407）', '黎（1428-1789）', '莫', '鄭阮分治', '阮（1802-）'],
    capitals: ['昇龍（河內）', '富春（順化）'],
    religions: ['儒教', '上座部佛教', '本地祖先崇拜'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '越南中古-近世國號（968-1804）。三次抗蒙古入侵成功。15 世紀黎聖宗時統一現代越南範圍、納入占婆。1771 西山起義／1802 阮朝統一。',
    population_peak_wan: 800,
    area_peak_wan_km2: 30,
  },
  'Goryeo': {
    name_zh: '高麗王朝',
    dynasties: ['王氏（918-1392）'],
    capitals: ['開京（開城）'],
    religions: ['佛教國教', '儒學'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮半島中世紀王朝（918-1392）。1170 武人政權奪實權。1231 蒙古入侵後成元附庸近一個世紀。發明金屬活字印刷（13 世紀，比古騰堡早 200 年）。',
    population_peak_wan: 400,
    successors: ['Joseon'],
  },

  // ========== 蒙古後續：伊兒汗／帖木兒 ==========
  'Ilkhanate': {
    name_zh: '伊兒汗國',
    dynasties: ['旭烈兀（1256 立）', '合贊汗（1295-1304 皈依伊斯蘭）'],
    capitals: ['大不里士', '蘇丹尼耶'],
    religions: ['初期薩滿/景教/佛教', '1295 後伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '蒙古四大汗國之一（1256-1335）。旭烈兀 1258 滅阿巴斯。1260 艾因賈魯特被馬木留克擊敗為西進終結。合贊汗皈依伊斯蘭後波斯-蒙古融合。1335 不賽因死後分裂為札剌亦兒／穆扎法爾等。',
    area_peak_wan_km2: 380,
  },
  'Timurid Empire': {
    name_zh: '帖木兒帝國',
    dynasties: ['帖木兒（1370-1405）', '沙哈魯（1405-1447）', '兀魯伯（1447-1449）'],
    capitals: ['撒馬爾罕', '赫拉特'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '中亞-波斯帝國（1370-1507）。帖木兒以撒馬爾罕為基地、征服中亞-伊朗-小亞-印度（1398 劫德里）、1402 安卡拉之戰俘虜奧斯曼蘇丹巴耶塞特一世。沙哈魯時期文化巔峰（赫拉特畫派、烏魯伯天文台）。',
    area_peak_wan_km2: 440,
    successors: ['Mughal Empire'],
  },

  // ========== 西非／衣索比亞 ==========
  'Mali': {
    name_zh: '馬利帝國',
    dynasties: ['松迪亞塔‧凱塔（1235 立）', '曼薩‧穆薩（1312-1337 巔峰）'],
    capitals: ['尼亞尼', '廷巴克圖（學術中心）'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '西非薩赫勒大帝國（1235-1670）。曼薩‧穆薩 1324 赴麥加朝聖、沿途散金導致開羅黃金貶值十年。廷巴克圖桑科雷大學為當時非洲伊斯蘭學術重鎮。',
    population_peak_wan: 2000,
    area_peak_wan_km2: 110,
    successors: ['Songhai'],
  },
  'Songhai': {
    name_zh: '桑海帝國',
    dynasties: ['宋尼‧阿里（1464 起）', '阿斯基亞‧穆罕默德（1493 起）'],
    capitals: ['加奧'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '取代馬利的西非帝國（1464-1591）。阿斯基亞推動行政改革與伊斯蘭化。1591 通迪比戰役被摩洛哥薩阿德王朝以火槍擊敗，瞬間瓦解，西非陷入碎裂。',
    population_peak_wan: 1000,
    area_peak_wan_km2: 140,
  },
  'Bornu-Kanem': {
    name_zh: '博爾努-加涅姆',
    capitals: ['恩賈米納附近', '比爾尼‧加薩戈摩'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '查德湖周邊的中世紀-近世伊斯蘭王朝（700-1846）。原為加涅姆，13 世紀末東遷成博爾努。16 世紀末伊德里斯‧阿洛馬巔峰。19 世紀富拉尼聖戰／謝胡王朝接管。',
    area_peak_wan_km2: 50,
  },
  'Ethiopia': {
    name_zh: '衣索比亞',
    dynasties: ['所羅門王朝（1270-1974）'],
    capitals: ['貢德爾', '亞的斯亞貝巴（1886 起）'],
    religions: ['衣索比亞東正教'],
    realm_id: 'southern', sphere_id: 'ethiopian',
    intro: '非洲少數未被歐洲完全殖民的國家。1270 所羅門王朝復辟（自稱所羅門王與示巴女王後裔）。1896 阿杜瓦戰役大敗義大利為非洲少有對歐勝利。1935-41 義大利短暫占領後 1974 共產政變終結帝制。',
    population_peak_wan: 3000,
    area_peak_wan_km2: 110,
  },

  // ========== 近世／現代主要國家 ==========
  'France': {
    name_zh: '法國',
    dynasties: ['卡佩（987-1328）', '瓦盧瓦（1328-1589）', '波旁（1589-1792, 1814-1830）', '拿破崙波拿巴', '第三-第五共和'],
    capitals: ['巴黎'],
    religions: ['天主教', '世俗共和（1905 政教分離）'],
    realm_id: 'western', sphere_id: 'gallic-french',
    intro: '中古-近世歐陸首強。1789 大革命改寫世界政治語彙。拿破崙戰爭重塑歐洲版圖。19-20 世紀殖民帝國涵蓋非洲、印支、加勒比。',
    population_peak_wan: 6800,
    area_peak_wan_km2: 1280,
  },
  'Spain': {
    name_zh: '西班牙',
    dynasties: ['特拉斯塔馬拉（雙王 1469-1516）', '哈布斯堡（1516-1700）', '波旁（1700-）'],
    capitals: ['托雷多', '馬德里（1561 起）'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1469 卡斯提爾+亞拉岡聯姻。1492 收復格拉納達、哥倫布到美洲、驅逐猶太人三事同年。腓力二世時為「日不落帝國」（1580-1640 含葡）。1898 美西戰爭丟失菲律賓／古巴／波多黎各。',
    population_peak_wan: 5000,
    area_peak_wan_km2: 2000,
  },
  'Italy': {
    name_zh: '義大利',
    dynasties: ['薩伏依（1861-1946）', '共和（1946-）'],
    capitals: ['杜林（1861-1865）', '佛羅倫斯（1865-1871）', '羅馬（1871 起）'],
    religions: ['天主教', '世俗共和'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1861 加里波底＋加富爾完成統一。1870 羅馬納入。1922-1943 墨索里尼法西斯獨裁。1946 公投廢君主立共和。',
    population_peak_wan: 6000,
    area_peak_wan_km2: 30,
  },
  'Germany': {
    name_zh: '德國',
    dynasties: ['霍亨索倫（1871-1918）', '威瑪共和', '納粹', '聯邦共和（1949-）'],
    capitals: ['柏林', '波昂（1949-1990 西德）'],
    religions: ['新教＋天主教（路德傳統）'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1871 俾斯麥透過普法戰爭完成統一。1918 一戰敗。1933-1945 納粹獨裁。戰後分裂為東西德、1990 重新統一。',
    population_peak_wan: 8000,
    area_peak_wan_km2: 36,
  },
  'United Kingdom': {
    name_zh: '聯合王國',
    dynasties: ['漢諾威（1714-1901）', '薩克森-科堡-哥達（1901-1917）', '溫莎（1917-）'],
    capitals: ['倫敦'],
    religions: ['英國國教（聖公會）', '長老會（蘇格蘭）'],
    realm_id: 'western', sphere_id: 'british-celtic',
    intro: '1707 英格蘭+蘇格蘭合併。1801 加上愛爾蘭。19 世紀工業革命發源。維多利亞時代為大英帝國巔峰（占世界陸地 1/4）。',
    population_peak_wan: 6700,
    area_peak_wan_km2: 24,
  },
  'Japan': {
    name_zh: '日本',
    dynasties: ['天皇（不間斷）', '攝政（藤原）', '幕府（鎌倉／室町／德川）', '明治／大正／昭和／平成／令和'],
    capitals: ['平城京（奈良）', '平安京（京都）', '江戶／東京（1868 起）'],
    religions: ['神道', '佛教（飛鳥傳入）', '近代基督教'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '萬世一系的島國皇室。1185-1868 武家政權實控（鎌倉／室町／德川）。1868 明治維新後迅速近代化、躋身列強。二戰後成全球第二大經濟體（1968-2010）。',
    population_peak_wan: 1.28e4,
    area_peak_wan_km2: 38,
  },
  'Korea': {
    name_zh: '朝鮮半島',
    dynasties: ['新羅（676-935）', '高麗（918-1392）', '朝鮮／李氏（1392-1897）', '大韓帝國（1897-1910）'],
    capitals: ['慶州', '開城', '漢城（首爾）'],
    religions: ['佛教', '儒教（朝鮮王朝為國教）', '基督教（19 世紀末傳入）'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮半島統一政權的延續。1592 壬辰倭亂被秀吉軍入侵、明軍援朝擊退。1910 日本吞併、1945 解放後南北分治。',
    population_peak_wan: 1000,
  },
  'Persia': {
    name_zh: '波斯（近世）',
    dynasties: ['薩法維（1501-1736）', '阿夫沙爾／贊德', '卡扎爾（1796-1925）'],
    capitals: ['伊斯法罕', '德黑蘭'],
    religions: ['伊斯蘭什葉派十二伊瑪目派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '薩法維伊斯瑪儀一世強推什葉派為國教，使波斯成為遜尼派伊斯蘭世界的孤島。阿巴斯一世時（1588-1629）為伊斯法罕黃金時代。1828 與俄條約失高加索。',
    population_peak_wan: 1500,
    area_peak_wan_km2: 320,
  },
  'Iran': {
    name_zh: '伊朗',
    dynasties: ['卡扎爾末', '巴勒維（1925-1979）', '伊斯蘭共和國（1979-）'],
    capitals: ['德黑蘭'],
    religions: ['伊斯蘭什葉派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '1925 禮薩‧汗推翻卡扎爾、建巴勒維王朝。1953 美英政變推翻摩薩台。1979 霍梅尼伊斯蘭革命建神權共和。',
    population_peak_wan: 9000,
    area_peak_wan_km2: 165,
  },
  'Manchu Empire': {
    name_zh: '滿洲帝國（清）',
    dynasties: ['愛新覺羅'],
    capitals: ['盛京（瀋陽）→ 北京（1644 起）'],
    religions: ['薩滿', '藏傳佛教', '儒釋道', '伊斯蘭（新疆）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '清在地圖上常稱「滿洲帝國」。1644 入關。康熙（1662-1722）平三藩、收台灣、定俄界。乾隆（1736-1795）十全武功達巔峰。1840 後屢敗於西方。',
    population_peak_wan: 4.5e4,
    area_peak_wan_km2: 1300,
  },
  'Russia': {
    name_zh: '俄羅斯聯邦',
    dynasties: ['葉爾欽（1991-1999）', '普京（2000-）'],
    capitals: ['莫斯科'],
    religions: ['東正教', '伊斯蘭（韃靼／高加索）'],
    realm_id: 'northern', sphere_id: 'russian-tatar',
    intro: '1991 蘇聯解體後繼承核武與聯合國安理會席位。葉爾欽時代私有化伴隨經濟休克。2000 後普京強人政治。2014 吞併克里米亞、2022 全面入侵烏克蘭。',
    population_peak_wan: 1.45e4,
    area_peak_wan_km2: 1710,
  },
  'Funan': {
    name_zh: '扶南',
    capitals: ['俄厄（Óc Eo）'],
    religions: ['印度教', '佛教（傳入）'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '東南亞最早國家之一（68-627）。湄公河三角洲。中國史書詳載。海上貿易節點，俄厄遺址出土羅馬／印度／波斯／中國商品。7 世紀被真臘吸收。',
    successors: ['Khmer Empire'],
  },
}

// ===== 工具函數 =====

export function slugifyStateName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

/**
 * 自動推斷的 realm/sphere（由 scripts/infer_state_realm_sphere.mjs 產出）
 * Key = 英文 NAME，Value = { sphere_id, realm_id, confidence, ... }
 */
export interface SphereInferenceEntry {
  sphere_id: string | null
  realm_id: string | null
  confidence: number
  sources?: { iso: string; sphere: string }[]
  year_inferred_at?: number
  reason?: string
}

/**
 * 從 skeleton（historical-basemaps polygon）+ wikidata + details merge 成完整 list。
 * - 以 Wikidata 為主資料（~4000 國家），補上 polygon-only 的條目
 * - 同名 dedupe（不同 dataset 間以英文名為 key）
 * - polygon 提供 modern_countries + snapshots
 * - wikidata 提供 inception/dissolved 年份 + 中文名 + 大陸
 * - STATE_DETAILS 為人工撰寫的高品質詳細（覆蓋以上）
 * - sphereInference 為自動推斷補位（STATE_DETAILS 沒填時才用，標記 has_inferred_sphere=true）
 */
export function mergeStates(
  skeleton: StateSkeleton[],
  wikidata: WikidataState[],
  sphereInference: Record<string, SphereInferenceEntry> = {}
): HistoricalState[] {
  // 用英文名（小寫去空格）作為 key dedupe
  const norm = (s: string) => s.toLowerCase().replace(/\s+/g, '').replace(/[^\w]/g, '')

  const skMap = new Map<string, StateSkeleton>()
  for (const sk of skeleton) skMap.set(norm(sk.name_en), sk)

  // Wikidata 主名 + 別名 set
  const wdMap = new Map<string, WikidataState>()
  for (const w of wikidata) wdMap.set(norm(w.name_en), w)

  // 收集所有獨特英文名
  const allKeys = new Set([...skMap.keys(), ...wdMap.keys()])

  const result: HistoricalState[] = []
  for (const key of allKeys) {
    const sk = skMap.get(key)
    const wd = wdMap.get(key)
    const name_en = sk?.name_en || wd?.name_en || ''
    const detail = STATE_DETAILS[name_en] || {}
    const inferred = sphereInference[name_en]

    const year_start = sk?.earliest_from ?? wd?.inception_year ?? null
    const year_end = (sk?.latest_to !== undefined && sk.latest_to < 9999)
      ? sk.latest_to
      : wd?.dissolved_year
      ?? null

    // sphere/realm 來源優先序：STATE_DETAILS > inference
    const realm_id = detail.realm_id || inferred?.realm_id || undefined
    const sphere_id = detail.sphere_id || inferred?.sphere_id || undefined
    const has_inferred_sphere = !detail.realm_id && !!inferred?.realm_id

    result.push({
      id: slugifyStateName(name_en),
      name_en,
      name_zh: detail.name_zh || wd?.name_zh || undefined,
      earliest_from: sk?.earliest_from,
      latest_to: sk?.latest_to,
      modern_countries: sk?.modern_countries || [],
      snapshots: sk?.snapshots || [],
      qid: wd?.qid,
      continents: wd?.continents,
      year_start,
      year_end,
      ...detail,
      realm_id,
      sphere_id,
      has_detail: !!STATE_DETAILS[name_en],
      has_polygon: !!sk,
      has_inferred_sphere,
    })
  }

  return result.sort((a, b) => {
    const ay = a.year_start ?? 9999
    const by = b.year_start ?? 9999
    return ay - by || a.name_en.localeCompare(b.name_en)
  })
}

