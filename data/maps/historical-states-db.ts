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
    name_zh: '小北文明',
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
    name_zh: '漢',
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
    name_zh: '帕提亞',
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
    name_zh: '波斯',
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
    name_zh: '滿洲帝國',
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

  // ========== 北美 / 拉美 ==========
  'United States': {
    name_zh: '美國',
    capitals: ['費城（臨時）', '華盛頓特區（1800 起）'],
    religions: ['新教多數', '天主教', '世俗政教分離'],
    realm_id: 'north-america', sphere_id: 'anglo-american',
    intro: '1776 獨立。1803 路易斯安那購買倍增領土。1861-1865 南北戰爭。1898 美西戰爭起殖民帝國。20 世紀兩次世界大戰崛起為超級強權。',
    population_peak_wan: 3.3e4,
    area_peak_wan_km2: 980,
  },
  'Canada': {
    name_zh: '加拿大',
    capitals: ['渥太華'],
    religions: ['天主教＋新教＋世俗'],
    realm_id: 'north-america', sphere_id: 'anglo-american',
    intro: '1867 自治領（Dominion）成立。1931 西敏法令獨立。1949 紐芬蘭加入。世界第二大國土面積（998 萬 km²）。',
    population_peak_wan: 3900,
    area_peak_wan_km2: 998,
  },
  'Haiti': {
    name_zh: '海地',
    religions: ['天主教＋伏都教（融合）'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1804 拉美第一個獨立的黑人共和國（奴隸起義）。獨立後屢遭法國／美國干預。20 世紀經濟長期低迷。',
  },
  'Dominican Republic': {
    name_zh: '多明尼加',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1844 從海地獨立。歷經西班牙短期回歸（1861-1865）。20 世紀特魯希略獨裁。',
  },
  'Argentina': {
    name_zh: '阿根廷',
    capitals: ['布宜諾斯艾利斯'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'southern-cone',
    intro: '1816 獨立。20 世紀初為世界 10 大富國。庇隆主義（1946-）塑造現代政治。1976-1983 軍政府「骯髒戰爭」。',
    population_peak_wan: 4600,
  },
  'Paraguay': {
    name_zh: '巴拉圭',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'southern-cone',
    intro: '1811 獨立。1864-1870 三國同盟戰爭損失過半人口（巴西／阿根廷／烏拉圭聯軍）。',
  },
  'Uruguay': {
    name_zh: '烏拉圭',
    religions: ['天主教（最世俗化拉美國家）'],
    realm_id: 'latin-america', sphere_id: 'southern-cone',
    intro: '1825 獨立。20 世紀初為「南美瑞士」。2013 全球首個合法化大麻。',
  },
  'Venezuela': {
    name_zh: '委內瑞拉',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1811 第一個拉美獨立宣告。玻利瓦領導獨立戰爭。1922 發現大油田。21 世紀查維茲—馬杜羅左派威權。',
  },
  'Ecuador': {
    name_zh: '厄瓜多',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '1830 從大哥倫比亞獨立。20 世紀加拉巴哥群島為達爾文研究地。',
  },
  'Guatemala': {
    name_zh: '瓜地馬拉',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1821 獨立。1960-1996 內戰致 20 萬人喪生。馬雅後裔人口比例高（40%+）。',
  },
  'Nicaragua': {
    name_zh: '尼加拉瓜',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1821 獨立。1979 桑迪諾解放陣線推翻索摩查獨裁。1980 年代美國資助康特拉內戰。',
  },
  'Costa Rica': {
    name_zh: '哥斯大黎加',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1821 獨立。1948 廢除軍隊（罕見）。中美洲最穩定民主國家。',
  },
  'Honduras': {
    name_zh: '宏都拉斯',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1821 獨立。20 世紀「香蕉共和國」稱號發源地。',
  },
  'El Salvador': {
    name_zh: '薩爾瓦多',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1821 獨立。1980-1992 內戰。2021 全球首個比特幣法定貨幣國。',
  },

  // ========== 歐洲：諾曼底/法蘭西分裂後 ==========
  'Sweden': {
    name_zh: '瑞典',
    dynasties: ['福爾孔（中世紀）', '瓦薩（1523-1654）', '帕拉丁（1654-1720）', '貝爾納多特（1818-）'],
    capitals: ['斯德哥爾摩'],
    religions: ['路德宗（國教 1527 起）'],
    realm_id: 'western', sphere_id: 'nordic-livonian',
    intro: '1523 瓦薩王朝古斯塔夫一世獨立離卡爾馬聯盟。古斯塔夫二世（1611-1632）三十年戰爭成歐洲強權。1709 波爾塔瓦敗於彼得大帝。1814 與挪威人身聯合至 1905。',
    population_peak_wan: 1000,
  },
  'Denmark': {
    name_zh: '丹麥',
    dynasties: ['克努特大帝', '奧爾登堡（1448-1863）', '格呂克斯堡（1863-）'],
    capitals: ['哥本哈根'],
    religions: ['路德宗'],
    realm_id: 'western', sphere_id: 'nordic-livonian',
    intro: '11 世紀克努特大帝統治英／丹／挪。1397-1523 卡爾馬聯盟主導北歐。1864 普丹戰爭失什列斯威。',
  },
  'Norway': {
    name_zh: '挪威',
    capitals: ['奧斯陸'],
    religions: ['路德宗'],
    realm_id: 'western', sphere_id: 'nordic-livonian',
    intro: '中世紀維京發源地。1397-1523 卡爾馬聯盟。1523-1814 丹麥統治。1814-1905 瑞典人身聯合。1905 公投獨立。',
  },
  'Poland': {
    name_zh: '波蘭',
    dynasties: ['皮亞斯特（966-1370）', '雅蓋洛（1386-1572）', '選舉君主（1572-1795）', '共和'],
    capitals: ['克拉科夫', '華沙（1596 起）'],
    religions: ['天主教（966 皈依）'],
    realm_id: 'western', sphere_id: 'lublin',
    intro: '966 梅什科一世皈依天主教建國。1386 與立陶宛聯姻成歐洲大國。1772/1793/1795 三次被瓜分。1918 復國、1939 再被德蘇瓜分、1989 民主化。',
    population_peak_wan: 4000,
  },
  'Prussia': {
    name_zh: '普魯士',
    dynasties: ['霍亨索倫'],
    capitals: ['柏林'],
    religions: ['路德宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1701 升格王國。腓特烈大帝（1740-1786）擴張。1871 統一德意志後普魯士國王兼任德皇。1947 同盟國正式廢除普魯士邦。',
    area_peak_wan_km2: 35,
  },
  'Hungary': {
    name_zh: '匈牙利',
    dynasties: ['阿爾帕德（1000-1301）', '安茹', '雅蓋洛', '哈布斯堡（1526-1918）'],
    capitals: ['布達佩斯'],
    religions: ['天主教＋少數新教'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1000 聖伊什特萬建國皈依天主教。1526 莫哈赤戰役大敗於奧斯曼、被分為三。1867 奧匈帝國。1920 特里阿農條約丟 2/3 領土。',
  },
  'Luxembourg': {
    name_zh: '盧森堡',
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'low-countries',
    intro: '963 西格弗里德建堡。14 世紀盧森堡王朝（卡爾四世）出三位神羅皇帝。1815 大公國至今。',
  },
  'Belgium': {
    name_zh: '比利時',
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'low-countries',
    intro: '1830 從尼德蘭聯合王國獨立。歐盟首都布魯塞爾所在。19 世紀末利奧波德二世剛果自由邦帶來慘烈殖民暴行。',
  },
  'Switzerland': {
    name_zh: '瑞士',
    capitals: ['伯恩'],
    religions: ['新教＋天主教'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1291 三州聯盟。1648 威斯特伐利亞和約正式脫離神羅。1815 起永久中立。聯邦制 26 個 canton。',
  },
  'Cyprus': {
    name_zh: '賽普勒斯',
    religions: ['東正教＋伊斯蘭遜尼'],
    realm_id: 'central', sphere_id: 'aegean-asia-minor',
    intro: '拜占庭→十字軍諸國→威尼斯→奧斯曼→英→1960 獨立。1974 土耳其入侵後分裂北南至今。',
  },
  'Venice': {
    name_zh: '威尼斯共和國',
    capitals: ['威尼斯'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '697-1797 千年商業共和國。1204 第四次十字軍洗劫君士坦丁堡為其商業手段。1797 拿破崙終結。',
  },
  'Sardinia': {
    name_zh: '撒丁王國',
    dynasties: ['薩伏依（1720-1861）'],
    capitals: ['杜林'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1720 薩伏依公爵獲撒丁島成王國。19 世紀加里波底＋加富爾以撒丁為核心統一義大利。',
  },
  'Papal States': {
    name_zh: '教皇國',
    dynasties: ['歷任教宗'],
    capitals: ['羅馬', '阿維儂（1309-1377）'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '756 丕平獻土到 1870 義大利統一終結。教宗世俗領地。1929 拉特蘭條約建立梵蒂岡。',
  },
  'Britany': {
    name_zh: '布列塔尼',
    capitals: ['雷恩'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'british-celtic',
    intro: '法國西北凱爾特公國。9 世紀獨立王國。15 世紀末併入法國（1532 正式）。',
  },

  // ========== 非洲 ==========
  'Morocco': {
    name_zh: '摩洛哥',
    dynasties: ['伊德里斯', '阿穆瓦希德', '梅里尼德', '薩阿德', '阿拉維（1666-）'],
    capitals: ['非斯', '馬拉喀什', '拉巴特'],
    religions: ['伊斯蘭遜尼（馬利基派）'],
    realm_id: 'western', sphere_id: 'carthaginian-maghreb',
    intro: '788 伊德里斯一世建立穆斯林王朝。1591 通迪比戰役火槍滅桑海。1912-1956 法國保護國。',
  },
  'Congo': {
    name_zh: '剛果王國',
    capitals: ['姆班扎剛果（聖薩爾瓦多）'],
    religions: ['基督教（15 世紀皈依天主教）'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '14 世紀建國。1483 葡萄牙人接觸後王室皈依天主教。19 世紀末葉利奧波德二世剛果自由邦帶來慘烈剝削。',
  },
  'Madagascar': {
    name_zh: '馬達加斯加',
    religions: ['本地泛靈信仰＋基督教'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '南島語系最西端（祖先來自婆羅洲）。19 世紀梅里納王國統一全島。1896-1960 法國殖民。',
  },
  'Expansionist Kingdom of Merina': {
    name_zh: '梅里納擴張王國',
    capitals: ['塔那那利佛'],
    religions: ['本地泛靈→ 1869 新教（拉達二世女王皈依）'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '馬達加斯加中部高地王國（1540-1897）。19 世紀拉達一世(Radama I)征服全島。1896 法軍滅。',
  },
  'Benin': {
    name_zh: '貝南王國',
    capitals: ['貝南城（Edo）'],
    religions: ['本地多神'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '西非沿海王國（13 世紀-1897）。以青銅藝術聞名。1897 英軍懲罰性遠征劫掠貝南銅版。今奈及利亞境內。',
  },
  'Oyo': {
    name_zh: '奧約帝國',
    religions: ['約魯巴多神'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '約魯巴族大帝國（1300-1896）。18 世紀控制達荷美與部分豪薩邦國。19 世紀內亂衰退。',
  },
  'Mossi States': {
    name_zh: '莫西諸國',
    religions: ['本地多神＋伊斯蘭'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '今布吉納法索的莫西族諸王國（1100-1896）。瓦加杜古／亞滕加為主邦。長期抵抗伊斯蘭化。',
  },
  'Ghana': {
    name_zh: '迦納帝國',
    religions: ['本地多神→伊斯蘭'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '西非第一個大帝國（300-1240）。今天的茅利塔尼亞／馬利交界。控制撒哈拉黃金貿易。1240 被馬利取代。',
  },
  'Senegal': {
    name_zh: '塞內加爾',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '中世紀屬迦納／馬利帝國邊緣。1659 法人建聖路易堡為法屬西非起點。1960 獨立。',
  },
  'Makkura': {
    name_zh: '馬庫拉',
    religions: ['基督教（科普特一性論）'],
    realm_id: 'central', sphere_id: 'egyptian',
    intro: '6 世紀皈依基督教的努比亞王國（今蘇丹北部，540-1312）。對抗伊斯蘭擴張長達 700 年。',
  },
  'Alwa': {
    name_zh: '阿爾瓦',
    capitals: ['索巴'],
    religions: ['基督教（科普特一性論）'],
    realm_id: 'central', sphere_id: 'egyptian',
    intro: '努比亞最南的基督教王國（6 世紀-1504）。今天的喀土穆周邊。1504 被芬吉蘇丹國滅。',
  },

  // ========== 中亞／中東 ==========
  'Yemen': {
    name_zh: '葉門',
    religions: ['伊斯蘭遜尼派＋什葉派栽德派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '南阿拉伯古文明發源（示巴、希木葉爾）。9 世紀栽德派建伊瑪目國。1962-1990 北葉門共和。1990 南北統一。2014-內戰。',
  },
  'Hadramaut': {
    name_zh: '哈德拉毛',
    religions: ['伊斯蘭遜尼／伊巴德派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '南阿拉伯古王國（-300 起）。乳香與沒藥貿易節點。中世紀分裂為諸蘇丹國。',
  },
  'Oman': {
    name_zh: '阿曼',
    dynasties: ['亞里巴（17 世紀）', '布塞德（1749-）'],
    capitals: ['馬斯喀特'],
    religions: ['伊斯蘭伊巴德派（特殊）'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '阿拉伯半島東南。17 世紀亞里巴王朝驅逐葡人、建海上帝國（東非桑吉巴／印度／巴基斯坦海岸）。1856 桑吉巴與本土分立。',
  },
  'Armenia': {
    name_zh: '亞美尼亞',
    religions: ['亞美尼亞使徒教會（301 全球首個基督教國家）'],
    realm_id: 'central', sphere_id: 'caucasus',
    intro: '301 蒂里達特三世皈依基督教，為人類第一個基督教國家。橫跨拜占庭／薩珊／阿拉伯／拜占庭／塞爾柱／蒙古／奧斯曼。1991 從蘇聯獨立。',
  },
  'Georgia': {
    name_zh: '喬治亞',
    religions: ['東正教（喬治亞使徒教會）'],
    realm_id: 'central', sphere_id: 'caucasus',
    intro: '337 米里安三世皈依基督教（早於羅馬國教化）。12-13 世紀塔瑪爾女王時期巔峰。1801 併入俄羅斯。1991 獨立。',
  },
  'Afghanistan': {
    name_zh: '阿富汗',
    dynasties: ['杜蘭尼（1747-1823）', '巴拉克扎伊（1823-1973）'],
    capitals: ['坎大哈', '喀布爾'],
    religions: ['伊斯蘭遜尼派＋少數什葉派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '1747 艾哈邁德‧沙‧杜蘭尼建現代阿富汗。19 世紀「大博弈」英俄角力場。1979 蘇侵、2001 美侵、2021 美撤後塔利班重掌。',
  },
  'central Asian khanates': {
    name_zh: '中亞諸汗國',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'northern', sphere_id: 'turanian-turkic',
    intro: '帖木兒後中亞分裂為布哈拉／希瓦／浩罕／喀什噶爾等汗國。19 世紀逐一被俄羅斯帝國併吞。',
  },

  // ========== 南亞／東南亞 ==========
  'Tibet': {
    name_zh: '吐蕃／西藏',
    dynasties: ['吐蕃王朝（618-842）', '薩迦', '帕木竹巴', '甘丹頗章（達賴喇嘛 1642-1959）'],
    capitals: ['拉薩'],
    religions: ['藏傳佛教'],
    realm_id: 'eastern', sphere_id: 'tibetan',
    intro: '7 世紀松贊干布建吐蕃帝國。842 達磨贊普滅佛被弒、帝國解體。13 世紀薩迦派與蒙古結盟。1642 五世達賴建甘丹頗章。1959 流亡印度。',
    population_peak_wan: 600,
    area_peak_wan_km2: 230,
  },
  'Bhutan': {
    name_zh: '不丹',
    capitals: ['廷布'],
    religions: ['藏傳佛教（竹巴噶舉）'],
    realm_id: 'eastern', sphere_id: 'tibetan',
    intro: '17 世紀夏宗法王統一。2008 君主立憲民主化。GNH（國民幸福指數）提倡國。',
  },
  'Nepal': {
    name_zh: '尼泊爾',
    dynasties: ['沙阿（1768-2008）'],
    capitals: ['加德滿都'],
    religions: ['印度教（國教至 2008）＋藏傳佛教（北部）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '1768 普利特維‧納拉揚‧沙阿統一。1816 英尼戰爭後簽蘇高利條約成英保護國。2008 廢君主立共和。',
  },
  'Cambodia': {
    name_zh: '柬埔寨',
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '高棉帝國（吳哥）的後繼。15 世紀遷都金邊。1863 法保護國。1975-1979 紅色高棉屠殺 1/4 人口。',
  },
  'Brunei': {
    name_zh: '汶萊',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '15-17 世紀蘇丹國巔峰時統治整個婆羅洲＋菲律賓南部。19 世紀領土被分予英屬北婆羅洲／砂拉越。1984 獨立。',
  },
  'Philippines': {
    name_zh: '菲律賓',
    religions: ['天主教（西班牙傳入）＋伊斯蘭（南部）'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '1521 麥哲倫抵達。1565-1898 西屬。1898-1946 美屬。亞洲僅有的天主教多數國家之一。',
  },
  'Champa': {
    name_zh: '占婆',
    religions: ['印度教（濕婆）→ 伊斯蘭（晚期）'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '今越南中南部的印度化王國（192-1832）。長期與越南大越對抗。1471 黎聖宗占婆滅國戰爭後僅剩殘餘。',
  },
  'Arakan': {
    name_zh: '若開王國',
    capitals: ['謬杭'],
    religions: ['上座部佛教＋伊斯蘭（沿海）'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '今緬甸西部的獨立王國（1430-1785）。受孟加拉伊斯蘭文化影響。1785 被緬甸貢榜王朝吞併。',
  },
  'Laos': {
    name_zh: '寮國',
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '14 世紀法昂建瀾滄王國。1893 法保護國。1975 巴特寮（共產）建寮人民民主共和國。',
  },
  'Ceylon': {
    name_zh: '錫蘭',
    religions: ['上座部佛教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '葡（1505）→ 荷（1656）→ 英（1796-1948）。1948 獨立、1972 改名斯里蘭卡。1983-2009 內戰（坦米爾之虎）。',
  },
  'Simhala': {
    name_zh: '僧伽羅',
    capitals: ['阿努拉達普勒', '波羅那魯沃'],
    religions: ['上座部佛教（公元前 3 世紀阿育王傳入）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '斯里蘭卡僧伽羅古王國（-543 起）。-3 世紀阿育王使團傳入佛教。20+ 王朝延續 2000 年。',
  },

  // ========== 太平洋 ==========
  'Fiji': {
    name_zh: '斐濟',
    religions: ['新教衛理會（多數）＋印度教（印度裔）'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '美拉尼西亞-玻里尼西亞交界。1874 卡考鮑簽署割讓條約成英屬。1879 起英國引入印度契約勞工。1970 獨立。',
  },
  'Tonga': {
    name_zh: '東加',
    dynasties: ['圖普家族（1845-）'],
    capitals: ['努庫阿洛法'],
    religions: ['新教衛理會'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '玻里尼西亞唯一從未被殖民的主權王國。1900-1970 英保護國（自治）。',
  },
  'Samoa': {
    name_zh: '薩摩亞',
    religions: ['新教＋天主教'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '玻里尼西亞酋邦群。1899-1914 德屬西薩摩亞。1914-1962 紐西蘭託管。1962 獨立（南太平洋首個獨立國）。',
  },
  'American Samoa': {
    name_zh: '美屬薩摩亞',
    religions: ['新教＋天主教'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '1899 美德分薩摩亞、東部歸美。1900 起為美國非建制屬地至今。帕果帕果天然港。',
  },
  'Wallis and Futuna Islands': {
    name_zh: '瓦利斯及富圖納',
    religions: ['天主教（瑪麗會傳教士 1837 傳入）'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '1888 法保護國。1959 公投留法。3 個傳統王國（瓦利斯／西加／阿洛）保留至今。',
  },
  'Niue': {
    name_zh: '紐埃',
    religions: ['新教'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '世界最大珊瑚礁島之一。1900 英占、1901 移交紐西蘭。1974 自由聯合國（紐西蘭防務）。',
  },

  // ========== 加勒比＋附近 ==========
  'Belize': {
    name_zh: '貝里斯',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '17 世紀英國伐木工建殖民地（英屬宏都拉斯）。1981 獨立。中美洲唯一英語官方國家。',
  },
  'Dominica': {
    name_zh: '多米尼克',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '加勒比小安地列斯群島。17-18 世紀英法爭奪。1978 獨立。原住民加勒比人保留區是加勒比少見。',
  },
  'Antigua and Barbuda': {
    name_zh: '安地卡及巴布達',
    religions: ['英國國教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1632 英屬。1981 獨立。納爾遜造船廠（18 世紀英海軍基地）為世界遺產。',
  },
  'Saint Kitts and Nevis': {
    name_zh: '聖克里斯多福及尼維斯',
    religions: ['英國國教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1623 英人在西半球首個永久殖民地。1983 獨立。美洲最小主權國家。',
  },
  'Anguilla': {
    name_zh: '安圭拉',
    religions: ['英國國教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '英屬海外領地。1967 拒絕與聖克里斯多福合併、武裝起義要求留英。',
  },
  'Montserrat': {
    name_zh: '蒙特塞拉特',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '英屬海外領地。1995-1997 蘇弗里耶爾火山噴發毀首都普利茅斯，逾半人口外移。',
  },
  'Guadeloupe': {
    name_zh: '瓜地洛普',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '法國海外省（自 1946）。歐元區。原住民加勒比人 17 世紀被滅。',
  },
  'Saint Martin': {
    name_zh: '聖馬丁',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '世界最小同時為兩主權國共管的島：北法／南荷。1648 條約劃分至今。',
  },
  'Saint Barthelemy': {
    name_zh: '聖巴瑟米',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '小安地列斯。1784-1878 為瑞典殖民地（瑞典少見的加勒比領地）。今為法海外集體。',
  },
  'Netherlands Antilles': {
    name_zh: '荷屬安地列斯',
    religions: ['天主教＋新教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '1954-2010 荷王國組成國，含 6 島（古拉索／阿魯巴／聖馬丁等）。2010 解散，各島分別取得新地位。',
  },
  'French Guiana': {
    name_zh: '法屬圭亞那',
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'caribbean',
    intro: '南美的法國海外省。著名的庫魯太空中心（歐洲太空局發射場）。',
  },

  // ========== 中世紀義大利諸城邦 ==========
  'Mamluke Sultanate': {
    name_zh: '馬木留克蘇丹國',
    dynasties: ['巴赫里（1250-1382）', '布爾吉（1382-1517）'],
    capitals: ['開羅'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '埃及／黎凡特奴隸兵建立的蘇丹國。1260 艾因賈魯特擊退蒙古、保住伊斯蘭世界免於蒙古吞噬。1517 被奧斯曼塞利姆一世滅。',
    area_peak_wan_km2: 220,
  },
  'Fatimid Caliphate': {
    name_zh: '法蒂瑪哈里發',
    capitals: ['馬赫迪耶', '開羅（969 建）'],
    religions: ['什葉派伊斯瑪儀'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '什葉派伊斯瑪儀派建立的哈里發（909-1171）。969 征服埃及、建開羅、創艾資哈爾大學（迄今最古的伊斯蘭大學）。1171 薩拉丁滅之、轉回遜尼。',
    area_peak_wan_km2: 410,
  },
  'Seljuk Caliphate': {
    name_zh: '塞爾柱蘇丹國',
    capitals: ['伊斯法罕', '梅爾夫'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '突厥遊牧建立的伊斯蘭大帝國（1037-1194）。1071 曼齊克特戰役擊敗拜占庭、開突厥化小亞細亞之門。1095 觸發第一次十字軍。1194 被花剌子模滅。',
  },
  'Sicily': {
    name_zh: '西西里王國',
    dynasties: ['諾曼（1130-1194）', '霍亨斯陶芬', '安茹', '亞拉岡'],
    capitals: ['巴勒摩'],
    religions: ['天主教＋少數伊斯蘭／東正教（諾曼時期寬容）'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1130 諾曼羅傑二世建王國。多元文化（拉丁＋希臘＋阿拉伯）。1282 西西里晚禱起義後南北分立。',
  },
  'Naples': {
    name_zh: '那不勒斯王國',
    capitals: ['那不勒斯'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1282 西西里晚禱後從西西里分立。後與西西里合為「兩西西里王國」（1816-1860）。1861 併入義大利。',
  },
  'Genoa': {
    name_zh: '熱那亞共和國',
    capitals: ['熱那亞'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '中世紀-近世商業共和國（11-1797）。曾控黑海／克里米亞貿易站。哥倫布故鄉。1797 拿破崙終結。',
  },
  'Milan': {
    name_zh: '米蘭公國',
    dynasties: ['維斯孔蒂（1395-1447）', '斯福爾扎（1450-1535）'],
    capitals: ['米蘭'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1395 升公國。文藝復興重鎮（達文西最後晚餐）。1535 哈布斯堡統治。',
  },
  'Florence': {
    name_zh: '佛羅倫斯',
    dynasties: ['麥地奇（15-18 世紀）'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '文藝復興發源地。麥地奇家族贊助米開朗基羅／達文西。1569 升為托斯卡尼大公國。',
  },
  'Tuscany': {
    name_zh: '托斯卡尼大公國',
    dynasties: ['麥地奇（1569-1737）', '哈布斯堡-洛林'],
    capitals: ['佛羅倫斯'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1569 由佛羅倫斯共和國升格。1737 麥地奇絕嗣後落入哈布斯堡-洛林。1861 併入義大利。',
  },
  'Modena': {
    name_zh: '摩德納',
    dynasties: ['埃斯特（1452-1796）'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '埃斯特家族公國。1452 設立。1796 拿破崙併入內阿爾卑斯共和國。1859 義大利統一前夕被併。',
  },
  'Lucca': {
    name_zh: '盧卡共和國',
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '中世紀絲綢與銀行業中心。1369-1799 獨立共和國。1805 拿破崙妹妹埃莉薩任公爵。1847 併托斯卡尼。',
  },

  // ========== 中國北方／三國／早期 ==========
  'Liao': {
    name_zh: '遼',
    dynasties: ['耶律氏'],
    capitals: ['上京臨潢府', '中京大定府'],
    religions: ['薩滿', '佛教（中後期盛）'],
    realm_id: 'eastern', sphere_id: 'mongolic-tungusic',
    intro: '契丹遊牧建立的征服王朝（907-1125）。與北宋對峙、簽 1004 澶淵之盟（宋稱兄）。1125 被金滅。耶律大石西遷建西遼。',
    area_peak_wan_km2: 489,
  },
  'Jin': {
    name_zh: '金',
    dynasties: ['完顏氏'],
    capitals: ['上京會寧府', '中都（北京）'],
    religions: ['薩滿＋佛教＋儒'],
    realm_id: 'eastern', sphere_id: 'mongolic-tungusic',
    intro: '女真建立的征服王朝（1115-1234）。1125 滅遼、1127 滅北宋（靖康之變）。1234 蒙古滅之。',
    area_peak_wan_km2: 360,
  },

  // ========== 朝鮮三國 ==========
  'Silla': {
    name_zh: '新羅',
    capitals: ['慶州'],
    religions: ['佛教（5 世紀傳入）＋本地'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮三國之一（-57~935）。676 統一新羅完成半島南部統一（含百濟、大部分高句麗）。935 王建滅之立高麗。',
  },
  'Paekche': {
    name_zh: '百濟',
    capitals: ['慰禮城', '熊津', '泗沘'],
    religions: ['佛教'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮三國之一（-18~660）。與倭國交流密切、為佛教傳入日本之橋樑。660 被新羅唐聯軍滅。',
  },

  // ========== 中世紀伊比利亞 ==========
  'Castile': {
    name_zh: '卡斯提爾',
    capitals: ['托雷多', '布爾戈斯'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '收復失地戰爭的主力王國（1037-1469）。1469 伊莎貝拉與斐迪南聯姻成為西班牙王國的核心。',
  },
  'Granada': {
    name_zh: '格拉納達酋長國',
    dynasties: ['納斯爾（1232-1492）'],
    capitals: ['格拉納達'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '伊比利亞最後的伊斯蘭政權（1238-1492）。阿罕布拉宮為高峰建築。1492 雙王收復，西班牙統一。',
  },

  // ========== 非洲 ==========
  'Hausa States': {
    name_zh: '豪薩諸城邦',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '今奈及利亞北部 7 個豪薩族城邦（卡諾、卡齊納、扎里亞、坎、戈比爾、達烏拉、比拉姆）。1804 被富拉尼聖戰吞併立索科托哈里發。',
  },
  'Adal': {
    name_zh: '阿達爾蘇丹國',
    capitals: ['哈拉爾'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'ethiopian',
    intro: '索馬利／衣索比亞東部蘇丹國（1415-1577）。1529 艾哈邁德‧伊本‧易卜拉欣（左手）幾乎征服衣索比亞、葡萄牙援助才扭轉。1577 衰退。',
  },
  'Bunyoro': {
    name_zh: '布尼奧羅',
    religions: ['本地多神＋基督教＋伊斯蘭'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '今烏干達中部王國（14-19 世紀）。19 世紀末對抗布甘達與英國同時。1894 英征服。',
  },
  'Tukular Caliphate': {
    name_zh: '圖庫勒爾哈里發國',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '烏馬爾‧塔爾（圖庫勒爾人）建立的伊斯蘭聖戰國（1850-1893）。今馬利／塞內加爾／幾內亞。1893 法國征服。',
  },

  // ========== 殖民督統 ==========
  'Hong Kong': {
    name_zh: '香港',
    religions: ['佛道民間信仰＋基督教'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '1842 南京條約割英。1898 新界 99 年租約。1941-1945 日占。1997 主權移交、一國兩制。',
  },
  'Qatar': {
    name_zh: '卡達',
    dynasties: ['塔尼家族（1850-）'],
    capitals: ['杜哈'],
    religions: ['伊斯蘭遜尼派（瓦哈比影響）'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '1850 塔尼家族統一。1916-1971 英保護國。1995 翁主政變後現代化、半島電視台 1996 創立。2022 主辦世足。',
  },
  'Burundi': {
    name_zh: '蒲隆地',
    religions: ['天主教＋新教'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '16 世紀圖西王國。1916 比屬。1962 獨立。圖西／胡圖族裔衝突、1993-2005 內戰。',
  },
  'Sierra Leone': {
    name_zh: '獅子山',
    religions: ['伊斯蘭＋基督教'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '1787 英國解放黑奴定居地（自由城）。1961 獨立。1991-2002 內戰（血鑽石）。',
  },

  // ========== A1. 印度土邦（Princely States）==========
  'Sikkim (Indian princely state)': {
    name_zh: '錫金土邦',
    dynasties: ['南嘉爾王朝（1642-1975）'],
    capitals: ['岡托克'],
    religions: ['藏傳佛教＋印度教'],
    realm_id: 'eastern', sphere_id: 'tibetan',
    intro: '1642 蓬措‧南嘉建國。1890 英保護國。1947 印獨後英印移交、1975 公投併入印度成為錫金邦。',
  },
  'Kingdom of Kashmir': {
    name_zh: '克什米爾王國',
    dynasties: ['多格拉王朝（1846-1947）'],
    capitals: ['查謨', '斯利那加'],
    religions: ['印度教（王室）＋伊斯蘭遜尼（多數）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '1846 古拉布‧辛格買下克什米爾建查謨-克什米爾土邦。1947 印巴分治時王公猶豫，部族入侵促其簽署加入印度，引發第一次印巴戰爭。',
  },
  'Kashmir and Ladakh': {
    name_zh: '克什米爾與拉達克',
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '1834 多格拉軍征服拉達克。1846 阿姆利則條約後查謨王公兼領克什米爾與拉達克，組成查謨-克什米爾土邦。',
  },
  'Rajastan': {
    name_zh: '拉賈斯坦諸土邦',
    capitals: ['烏代浦', '齋浦爾', '焦特浦爾'],
    religions: ['印度教（拉吉普特）＋耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度西北部 22 個拉吉普特王公土邦群（齋浦爾／焦特浦爾／烏代浦／賓迪／珀勒德布爾等）。1947 後合併為拉賈斯坦邦。',
  },
  'Bahawalpur': {
    name_zh: '巴哈瓦爾布爾',
    dynasties: ['阿巴斯家族（1748-1955）'],
    capitals: ['巴哈瓦爾布爾'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'indian',
    intro: '1748 阿巴斯家族脫離德里建邦。1838 英保護國。1947 加入巴基斯坦、1955 併入西巴基斯坦。',
  },
  'Travancore': {
    name_zh: '特拉凡科爾',
    dynasties: ['瓦爾馬家族（1729-1949）'],
    capitals: ['特里凡得琅'],
    religions: ['印度教（皇室）＋敘利亞基督徒（顯著少數）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '南印度馬拉雅拉姆人邦。1729 馬爾坦達‧瓦爾馬統一。獨立識字率與社會福利印度第一。1949 與柯欽合併為特拉凡-柯欽邦。',
  },
  'Cochin': {
    name_zh: '柯欽',
    dynasties: ['Perumpadappu Swarupam（早期-1949）'],
    capitals: ['特里普尼圖拉'],
    religions: ['印度教＋敘利亞基督徒＋猶太教（柯欽猶太人）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '中喀拉拉古老王國。1503 葡，1663 荷，1814 英三度殖民。猶太人社區可追至 1 世紀。1949 併入特拉凡-柯欽。',
  },
  'Oudh': {
    name_zh: '奧德',
    dynasties: ['Nawabs of Awadh／納瓦布王朝（1722-1856）'],
    capitals: ['法扎巴德', '勒克瑙'],
    religions: ['伊斯蘭什葉派（王室）＋印度教（多數）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '蒙兀兒衰落後納瓦布薩達特‧汗 1722 立國。勒克瑙烏爾都-波斯文化高峰。1856 英直接吞併，引爆 1857 印度大叛亂。',
  },
  'Mysore': {
    name_zh: '邁索爾',
    dynasties: ['沃迪雅王朝（1399-1947）', '海德爾‧阿里／提普蘇丹（1761-1799）'],
    capitals: ['邁索爾', '塞林伽巴丹'],
    religions: ['印度教（王室）＋伊斯蘭遜尼（提普時期）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '南印度王國。18 世紀海德爾‧阿里與提普蘇丹四度對抗英東印度公司。1799 塞林伽巴丹之戰提普戰死、沃迪雅復位為英保護土邦。',
    population_peak_wan: 800,
  },
  'Bhopal State': {
    name_zh: '博帕爾土邦',
    dynasties: ['Bhopal Begums（多代女性統治者）'],
    capitals: ['博帕爾'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '1723 阿富汗將領 Dost Mohammad 建國。19 世紀起連續四位 Begum（女酋長）統治，印度史罕見。1947 後遲至 1949 加入印度。',
  },
  'Hyderabad State': {
    name_zh: '海得拉巴土邦',
    dynasties: ['阿薩夫‧賈希王朝（1724-1948）'],
    capitals: ['海得拉巴'],
    religions: ['伊斯蘭遜尼派（王室）＋印度教（多數）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '蒙兀兒衰落後最大土邦，南印度尼贊統治。1947 印獨時尼贊欲獨立或加巴，1948 印度「波羅作戰」武力併入。',
    population_peak_wan: 1600,
    area_peak_wan_km2: 21,
  },
  'Jaipur State': {
    name_zh: '齋浦爾土邦',
    dynasties: ['Kachwaha 王朝'],
    capitals: ['安伯', '齋浦爾（1727 遷）'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '拉吉普特最大邦之一。1727 馬哈拉賈‧傑‧辛格二世建粉紅城。1949 併入拉賈斯坦。',
  },
  'Udaipur State': {
    name_zh: '烏代浦土邦',
    dynasties: ['Sisodia 王朝（西索迪亞）'],
    capitals: ['奇陶加爾', '烏代浦（1559）'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '拉吉普特最古老王室、梅瓦爾的核心。歷代拒絕承認蒙兀兒宗主權，馬哈拉納‧普拉塔普對抗阿克巴最為著名。1818 英保護國。',
  },
  'Indore State': {
    name_zh: '印多爾土邦',
    dynasties: ['Holkar 王朝（1731-1948）'],
    capitals: ['印多爾'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: 'Malhar Rao Holkar 從馬拉塔聯盟分立。Ahilyabai Holkar（1767-1795）為印度史名君。1818 英保護國。1948 併入中央邦。',
  },
  'Gwalior State': {
    name_zh: '瓜廖爾土邦',
    dynasties: ['Scindia 王朝（1731-1948）'],
    capitals: ['瓜廖爾'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '馬拉塔大將 Ranoji Scindia 建邦。19 世紀為中印度最強土邦之一。1858 起義時 Rani of Jhansi 借兵瓜廖爾。1948 併中央邦。',
  },
  'Baroda State': {
    name_zh: '巴羅達土邦',
    dynasties: ['Gaekwad 王朝（1721-1949）'],
    capitals: ['巴羅達（瓦多達拉）'],
    religions: ['印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '馬拉塔系王公邦，1721 從馬拉塔分立。Sayajirao Gaekwad III（1875-1939）大力推動社會改革、義務教育、賤民解放。1949 併孟買邦。',
  },
  'Patiala State': {
    name_zh: '伯蒂亞拉土邦',
    dynasties: ['Phulkian Sidhu-Jat 王朝（1763-1948）'],
    capitals: ['伯蒂亞拉'],
    religions: ['錫克教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '旁遮普錫克王公邦。1763 Ala Singh 建國。19 世紀英保護國，一戰二戰均派兵助英。1948 與其他錫克邦合組 PEPSU。',
  },
  'Khanate of Kalat': {
    name_zh: '卡拉特汗國',
    dynasties: ['Ahmadzai 部族（1666-1955）'],
    capitals: ['卡拉特'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'indian',
    intro: '俾路支斯坦的部族邦。1666 米爾‧阿赫邁德建國。1876 英印簽約成保護國。1948 武力併入巴基斯坦、1955 解散。',
  },
  'Khairpur State': {
    name_zh: '凱爾布林土邦',
    dynasties: ['Talpur 王朝（1775-1955）'],
    capitals: ['凱爾布林'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'indian',
    intro: '信德地區 Talpur 家族支系。1842 英征服信德時保留凱爾布林為土邦。1947 加巴、1955 併入西巴基斯坦。',
  },
  'Manipur State': {
    name_zh: '曼尼普爾王國',
    dynasties: ['Ningthouja 王朝（傳說 33 CE 起）'],
    capitals: ['因帕爾'],
    religions: ['Sanamahism（本土）＋印度教（毗濕奴派 1714 起）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '緬甸與印度間的山地王國。1891 英緬戰爭後英保護國。1944 二戰因帕爾戰役日軍與英印軍在此決戰。1949 併入印度。',
  },

  // ========== A2. 神聖羅馬／德意志小邦 ==========
  'Baden': {
    name_zh: '巴登',
    dynasties: ['Zähringen 家族（1112-1918）'],
    capitals: ['卡爾斯魯爾'],
    religions: ['天主教＋新教路德／改革宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1112 邊伯國。1806 拿破崙提升為大公國。1918 共和。1952 併入巴登-符騰堡邦。',
  },
  'Bavaria': {
    name_zh: '巴伐利亞',
    dynasties: ['維特爾斯巴赫家族（1180-1918）'],
    capitals: ['慕尼黑'],
    religions: ['天主教'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '907 公國。1180 維特爾斯巴赫獲封。1806 拿破崙升王國。1871 加入德意志帝國保留王號。路德維希二世造新天鵝堡。1918 共和。',
    population_peak_wan: 700,
  },
  'Saxony': {
    name_zh: '薩克森',
    dynasties: ['Wettin 家族（1089-1918）'],
    capitals: ['德勒斯登'],
    religions: ['新教路德派（1539 改宗）'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '中世紀公國，1356 七選帝侯之一。1697 強腓特烈奧古斯特兼波蘭王。1806 升王國加入萊茵聯邦。1871 入德意志帝國。',
  },
  'Grand Duchy of Hesse': {
    name_zh: '黑森大公國',
    dynasties: ['黑森-達姆施塔特家族'],
    capitals: ['達姆施塔特'],
    religions: ['新教路德派＋天主教'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1806 拿破崙從黑森-達姆施塔特方伯國升為大公國。1871 入德意志帝國。1918 共和。',
  },
  'Electoral Hesse': {
    name_zh: '黑森選帝侯國',
    capitals: ['卡塞爾'],
    religions: ['新教改革宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1803 黑森-卡塞爾方伯升為選帝侯國（神羅最後一批選侯）。1866 普奧戰爭普魯士併吞。',
  },
  'Anhalt': {
    name_zh: '安哈特',
    dynasties: ['Ascanian 家族（1212-1918）'],
    capitals: ['德紹'],
    religions: ['新教路德／改革宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '阿斯堪尼亞家族領地。1863 各支合一為安哈特公國。1918 自由邦、1947 併入薩克森-安哈特。',
  },
  'Hanover': {
    name_zh: '漢諾威',
    dynasties: ['Brunswick-Lüneburg 家族（1714-1837 兼英王）'],
    capitals: ['漢諾威'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1692 選帝侯國。1714 喬治一世兼英王，英漢共主邦聯持續到 1837 維多利亞繼英位（漢諾威只傳男）。1814 升王國。1866 普魯士併吞。',
  },
  'Württemberg': {
    name_zh: '符騰堡',
    dynasties: ['Württemberg 家族（1083-1918）'],
    capitals: ['斯圖加特'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1083 伯國。1495 升公國。1806 拿破崙升王國。1871 入德意志帝國。1918 共和。1952 併入巴登-符騰堡邦。',
  },
  'Mecklenburg-Strelitz': {
    name_zh: '梅克倫堡-施特雷利茨',
    capitals: ['新施特雷利茨'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1701 從梅克倫堡分出的小支系大公國。1918 共和、1934 併入梅克倫堡邦。',
  },
  'Mecklenburg-Schwerin': {
    name_zh: '梅克倫堡-什未林',
    capitals: ['什未林'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1701 從梅克倫堡分出的較大支系大公國。1918 自由邦、1934 與施特雷利茨合併為梅克倫堡邦。',
  },
  'Brunswick': {
    name_zh: '布倫瑞克',
    dynasties: ['Welf 家族（韋爾夫）'],
    capitals: ['布倫瑞克'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: 'Welf 家族封地。1815 升公國，1918 自由邦。1946 併入下薩克森邦。',
  },
  'Holstein': {
    name_zh: '霍爾斯坦',
    capitals: ['基爾'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '北德與丹麥邊境的公國。1815 入德意志邦聯但屬丹麥王兼領。1864 普奧聯軍奪、1866 入普魯士。',
  },
  'Nassau': {
    name_zh: '拿騷',
    dynasties: ['Nassau 家族（奧蘭治-拿騷亦此系）'],
    capitals: ['威斯巴登'],
    religions: ['新教＋天主教'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '11 世紀伯國，1806 升公國。1866 普奧戰爭中支持奧地利、戰後被普魯士併吞。奧蘭治-拿騷支系為荷蘭王室。',
  },
  'Oldenburg': {
    name_zh: '奧爾登堡',
    dynasties: ['Oldenburg 家族（兼丹麥王、俄羅斯沙皇系統）'],
    capitals: ['奧爾登堡'],
    religions: ['新教路德派'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '中世紀伯國。1448 家族支系獲丹麥王位、彼得三世（俄）後成俄沙皇祖系。1815 大公國、1918 自由邦、1946 併入下薩克森。',
  },
  'Schaumburg-Lippe': {
    name_zh: '紹姆堡-利珀',
    capitals: ['比克堡'],
    religions: ['新教改革宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '神羅最小親王國之一（340 km²）。1640 從紹姆堡-荷爾斯泰因分出。1918 自由邦、1946 併入下薩克森。',
  },
  'Lippe-Detmold': {
    name_zh: '利珀-德特摩德',
    capitals: ['德特摩德'],
    religions: ['新教改革宗'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '神羅小親王國。1789 從利珀升公國。1918 自由邦、1947 併入北萊茵-西伐利亞。',
  },

  // ========== A3. 太平洋小島國 ==========
  'New Caledonia': {
    name_zh: '新喀里多尼亞',
    religions: ['天主教＋新教（美拉尼西亞）'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '1853 法國併吞、原為流放殖民地。鎳礦豐富。卡納克原住民獨立運動 1980s 起。2018-2021 三次公投皆否決獨立。',
  },
  'Rapa Nui': {
    name_zh: '拉帕努伊',
    religions: ['玻里尼西亞傳統＋天主教'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '玻里尼西亞最東。9-17 世紀 Moai 巨石像文明。內戰與歐人帶來疾病使 1877 人口跌至 111 人。1888 智利併吞。',
  },
  'Kingdom of Samoa': {
    name_zh: '薩摩亞王國',
    capitals: ['阿皮亞'],
    religions: ['玻里尼西亞傳統 → 基督教'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '1899 三方協議前的玻里尼西亞王國。Tafa\'ifa 四王號制度。1899 美德瓜分（東薩摩亞給美、西給德）、1914 紐西蘭託管。',
  },
  'Trust Territory of Nauru': {
    name_zh: '諾魯託管地',
    religions: ['基督教（公理會）'],
    realm_id: 'asia-pacific', sphere_id: 'pacific',
    intro: '一戰後國聯託管予澳紐英。二戰日佔。1947 聯合國託管恢復澳紐英。1968 獨立。磷礦曾使人均收入世界最高，1990s 礦盡破產。',
  },

  // ========== A4. 19-20 世紀短命邦／殖民督統 ==========
  'Vice Royalty of New Spain': {
    name_zh: '新西班牙總督轄區',
    dynasties: ['哈布斯堡-波旁西班牙王室'],
    capitals: ['墨西哥城（特諾奇蒂特蘭舊址）'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1535-1821 涵蓋墨西哥、中美洲、加勒比、菲律賓的西班牙最大殖民體。馬尼拉大帆船貿易連接東亞與美洲白銀。1810-1821 墨西哥獨立戰爭結束。',
    population_peak_wan: 600,
    area_peak_wan_km2: 600,
  },
  'Vice-Royalty of New Spain': {
    name_zh: '新西班牙總督轄區',
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '同 "Vice Royalty of New Spain" — historical-basemaps 的另一拼寫。',
  },
  'Vice Royalty of Peru': {
    name_zh: '秘魯總督轄區',
    capitals: ['利馬'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '1542-1824 西班牙在南美的最早與最大殖民體。波托西銀礦支撐世界貨幣體系。1717 分出新格拉納達、1776 分出拉普拉塔。1824 阿亞庫喬戰役結束。',
  },
  'Vice-Royalty of Peru': {
    name_zh: '秘魯總督轄區',
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '同 "Vice Royalty of Peru" — historical-basemaps 的另一拼寫。',
  },
  'Viceroyalty of the Río de la Plata': {
    name_zh: '拉普拉塔總督轄區',
    capitals: ['布宜諾斯艾利斯'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'southern-cone',
    intro: '1776 從秘魯總督轄區分出。涵蓋阿根廷、烏拉圭、巴拉圭、玻利維亞。1810 五月革命起義、1814-1825 各地獨立。',
  },
  'Empire of Brazil': {
    name_zh: '巴西帝國',
    dynasties: ['布拉甘薩家族（1822-1889）'],
    capitals: ['里約熱內盧'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'southern-cone',
    intro: '1822 佩德羅一世自葡萄牙獨立稱帝。佩德羅二世（1831-1889）長期穩定統治。1888 廢奴。1889 軍人政變共和。',
    population_peak_wan: 1400,
  },
  'Gran Colombia': {
    name_zh: '大哥倫比亞共和國',
    dynasties: ['玻利瓦爾總統（1819-1830）'],
    capitals: ['波哥大'],
    religions: ['天主教'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '1819 玻利瓦爾建國，涵蓋哥倫比亞、委內瑞拉、厄瓜多、巴拿馬。1830 玻利瓦爾去世前夕解體為三國。',
  },
  'Manchukuo': {
    name_zh: '滿洲國',
    dynasties: ['溥儀（清廢帝，1932-1945）'],
    capitals: ['新京（長春）'],
    religions: ['佛道民間信仰＋日本神道（強加）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '1931 九一八事變後日本扶植溥儀建國。1934 改稱滿洲帝國。國聯不承認。1945 蘇軍進攻、溥儀被俘終結。',
    population_peak_wan: 4300,
  },
  'Wang Jingwei regime': {
    name_zh: '汪精衛國民政府',
    capitals: ['南京'],
    religions: ['佛道民間信仰'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '1940-1945 汪精衛在南京建立的日本扶植傀儡國民政府。沿用青天白日旗。1944 汪死於日本、1945 日降結束。',
  },
  'Bavarian Soviet Republic': {
    name_zh: '巴伐利亞蘇維埃共和國',
    capitals: ['慕尼黑'],
    realm_id: 'western', sphere_id: 'central-european',
    intro: '1919 4-5 月巴伐利亞短命共產政權。受俄革命影響、Erich Mühsam／Eugen Leviné 領導。被自由團（Freikorps）血腥鎮壓。',
  },
  'Free Territory of Trieste': {
    name_zh: '的里雅斯特自由區',
    capitals: ['的里雅斯特'],
    realm_id: 'western', sphere_id: 'latin-cultural',
    intro: '1947 對義和約所設、聯合國保證地位。冷戰時義南爭議地。1954 倫敦備忘錄：A 區（含市）歸義、B 區歸南斯拉夫。',
  },
  'Saar Protectorate': {
    name_zh: '薩爾保護領',
    capitals: ['薩爾布呂肯'],
    realm_id: 'western', sphere_id: 'gallic-french',
    intro: '二戰後 1947 法國脫離德管建立的薩爾保護領（事實上法國經濟附庸）。1955 公投否決歐洲法、1957 經濟整合後 1959 併入西德。',
  },
  'Republic of Texas': {
    name_zh: '德克薩斯共和國',
    capitals: ['奧斯丁'],
    realm_id: 'north-america', sphere_id: 'anglo-american',
    intro: '1836 從墨西哥獨立（阿拉莫之戰、聖哈辛托）。Sam Houston 首任總統。1845 加入美國成為第 28 州、引爆美墨戰爭。',
  },
  'California Republic': {
    name_zh: '加利福尼亞共和國',
    realm_id: 'north-america', sphere_id: 'anglo-american',
    intro: '1846 6 月 14 日美墨戰爭爆發後、北加州移民在索諾馬建熊旗共和國。僅持續 25 天、7 月 9 日 John Frémont 接管後併入美國。',
  },
  'Republic of Yucatán': {
    name_zh: '猶加敦共和國',
    capitals: ['梅里達'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '1841-1848 兩度從墨西哥獨立。1847 起 Caste War（瑪雅人起義）、馬雅人佔據半島東部。1848 為求墨援助鎮壓馬雅而重歸墨西哥。',
  },

  // ========== A5. 阿拉伯諸邦 ==========
  'Hejaz': {
    name_zh: '漢志',
    capitals: ['麥加', '麥地那'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '阿拉伯半島西岸聖地區。鄂圖曼長期治理。1916 哈希姆家族謝里夫胡賽因領導阿拉伯起義獨立。1925 沙烏地征服併入沙烏地阿拉伯。',
  },
  'Kingdom of Hejaz': {
    name_zh: '漢志王國',
    dynasties: ['哈希姆家族（1916-1925）'],
    capitals: ['麥加'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '1916 阿拉伯起義後謝里夫胡賽因稱王。1924 廢哈里發後胡賽因稱哈里發、引沙烏地不滿。1925 內志（沙烏地）攻陷麥加滅國。',
  },
  'Kingdom of Nejd and Hejaz': {
    name_zh: '內志與漢志王國',
    dynasties: ['紹德家族（1926-1932）'],
    capitals: ['利雅德'],
    religions: ['伊斯蘭遜尼派瓦哈比'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '1926 伊本紹德兼漢志王。1927 英承認為獨立國。1932 改名沙烏地阿拉伯王國。',
  },
  'Hail': {
    name_zh: '哈伊勒',
    dynasties: ['Rashidi 拉希迪家族（1836-1921）'],
    capitals: ['哈伊勒'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '阿拉伯北部沙馬爾部族邦。19 世紀末逐第二沙烏地國（1891）成為半島強權。1921 伊本紹德反攻征服、併入沙烏地。',
  },
  'Trucial Oman': {
    name_zh: '停戰阿曼',
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '波斯灣南岸七酋長國群（阿布達比／杜拜／沙迦／阿吉曼／烏姆蓋萬／拉斯海瑪／富吉拉）。1820 英簽永久停戰、1892 英保護國。1971 獨立組成阿聯。',
  },
  'Trucial States': {
    name_zh: '停戰諸國',
    realm_id: 'central', sphere_id: 'arabian',
    intro: '同 "Trucial Oman"。1820-1971 波斯灣英保護下七酋長國。',
  },
  'Muscat and Oman': {
    name_zh: '馬斯喀特與阿曼蘇丹國',
    dynasties: ['Al Bu Sa\'id 王朝（1744-）'],
    capitals: ['馬斯喀特'],
    religions: ['伊斯蘭伊巴德派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '1820 起馬斯喀特蘇丹兼領阿曼內陸。19 世紀掌東非桑吉巴帝國。1970 卡布斯政變改名阿曼蘇丹國、開啟現代化。',
  },
  'Emirate of Asir': {
    name_zh: '阿西爾酋長國',
    dynasties: ['伊德里西家族'],
    capitals: ['薩布亞'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '紅海岸阿拉伯半島西南。1909 起伊德里西家族建邦。1926 加入沙烏地、1934 完全併入。',
  },
  'Kingdom of Yemen': {
    name_zh: '葉門穆塔瓦基利亞王國',
    dynasties: ['Hamid al-Din／哈米德丁家族（1918-1962）'],
    capitals: ['薩那'],
    religions: ['伊斯蘭什葉派宰德派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '1918 鄂圖曼撤後伊瑪目葉海亞建國。宰德派伊瑪目政教合一。1962 共和派軍人政變、內戰至 1970。',
  },
  'Yemeni Zaidi State': {
    name_zh: '葉門宰德伊瑪目國',
    dynasties: ['Rassid／Qasimid 等伊瑪目世系'],
    capitals: ['薩那'],
    religions: ['伊斯蘭什葉派宰德派'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '897 起阿里‧本‧侯賽因建宰德派伊瑪目國。歷經 Qasimid 王朝（1597-1872）。鄂圖曼斷續統治後 1918 重立。',
  },

  // ========== A6. 早期國家／小帝國 ==========
  'Seleucid Kingdom': {
    name_zh: '塞琉古王國',
    dynasties: ['塞琉古家族（-312~-63）'],
    capitals: ['塞琉西亞', '安條克'],
    religions: ['希臘多神＋當地多神'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '亞歷山大繼業者塞琉古一世建立。最大時東至印度河、西至安納托利亞。後逐失東方領、限敘利亞-西亞。-63 龐培收為羅馬行省。',
    population_peak_wan: 3000,
    area_peak_wan_km2: 400,
  },
  'Seleucid Empire': {
    name_zh: '塞琉古帝國',
    realm_id: 'central', sphere_id: 'persian',
    intro: '同 "Seleucid Kingdom" — wikidata 用名。',
  },
  'Ptolemaic Kingdom': {
    name_zh: '托勒密王國',
    dynasties: ['托勒密家族（-305~-30）'],
    capitals: ['亞歷山卓'],
    religions: ['希臘多神＋埃及多神（融合）'],
    realm_id: 'central', sphere_id: 'egyptian',
    intro: '亞歷山大繼業者托勒密一世建立。亞歷山卓圖書館、繆斯館為古地中海學術中心。-30 克麗奧佩脫拉七世亡於屋大維。',
    population_peak_wan: 700,
  },
  'Bactria': {
    name_zh: '巴克特里亞',
    capitals: ['巴克特拉'],
    religions: ['瑣羅亞斯德＋希臘多神＋佛教'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '阿姆河上游的古老地區。波斯帝國行省。亞歷山大東征後與大夏交融。-250 起希臘-巴克特里亞王國獨立。後為塞種與貴霜取代。',
  },
  'Greco-Bactrian Kingdom': {
    name_zh: '希臘-巴克特里亞王國',
    dynasties: ['狄奧多托斯／歐西德摩斯／米南德等支系'],
    capitals: ['巴克特拉', '阿伊哈努姆'],
    religions: ['希臘多神＋佛教（影響後續犍陀羅）'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '-250 狄奧多托斯脫離塞琉古獨立。最盛跨阿姆河至印度河。米南德一世（彌蘭王）為佛教護持者。-130 月氏入侵滅國。',
    population_peak_wan: 300,
  },
  'Kushan Principalities': {
    name_zh: '貴霜諸侯國',
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '貴霜帝國衰落後分裂的諸侯國（3 世紀末-4 世紀）。後為薩珊與寄多羅匈人取代。',
  },
  'Liu Song dynasty': {
    name_zh: '劉宋',
    dynasties: ['劉氏（420-479）'],
    capitals: ['建康（南京）'],
    religions: ['佛道＋本土巫術'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '南朝第一朝。劉裕滅東晉建宋。宋武帝劉裕、文帝劉義隆「元嘉之治」為南朝盛世。479 蕭道成廢帝建齊。',
    population_peak_wan: 2000,
  },
  'Northern Wei': {
    name_zh: '北魏',
    dynasties: ['拓跋／元氏（386-535）'],
    capitals: ['平城', '洛陽（493 遷）'],
    religions: ['佛教（雲岡、龍門石窟）＋天師道'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '鮮卑拓跋部建。439 太武帝統一華北。493 孝文帝遷洛陽全面漢化。534-535 分裂為東魏／西魏。',
    population_peak_wan: 3200,
    area_peak_wan_km2: 290,
  },
  'Toba Wei': {
    name_zh: '北魏',
    realm_id: 'eastern', sphere_id: 'han',
    intro: 'historical-basemaps 對北魏的另一稱呼（拓跋部）。',
  },
  'Northern Zhou': {
    name_zh: '北周',
    dynasties: ['宇文家族（557-581）'],
    capitals: ['長安'],
    religions: ['佛教＋道教（武帝滅佛 574-578）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '宇文泰子覺廢西魏帝建周。武帝宇文邕 577 滅北齊統華北。581 楊堅篡建隋。',
  },
  'Northern Qi': {
    name_zh: '北齊',
    dynasties: ['高氏（550-577）'],
    capitals: ['鄴城'],
    religions: ['佛教鼎盛'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '高歡子高洋 550 廢東魏建齊。國勢一度為北朝最盛。後主高緯昏聵、577 為北周所滅。',
  },
  'Cao Wei': {
    name_zh: '曹魏',
    dynasties: ['曹氏（220-265）'],
    capitals: ['洛陽'],
    religions: ['佛道初興＋玄學'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '三國之首。220 曹丕廢漢獻帝建魏。九品中正制、屯田制。249 司馬懿高平陵之變、265 司馬炎篡建晉。',
    population_peak_wan: 4400,
  },
  'Eastern Wu': {
    name_zh: '東吳',
    dynasties: ['孫氏（222-280）'],
    capitals: ['建業（南京）'],
    religions: ['江南民間信仰＋早期佛教'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '孫權於 222 稱吳王、229 稱帝。長江水師強盛、開發江南。280 西晉王濬樓船破吳、三國終。',
    population_peak_wan: 2300,
  },
  'Shu Han': {
    name_zh: '蜀漢',
    dynasties: ['劉氏（221-263）'],
    capitals: ['成都'],
    religions: ['天師道（張陵巴蜀起源）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '劉備 221 稱帝以續漢統。諸葛亮七出岐山。263 鄧艾偷渡陰平、後主劉禪降魏。',
    population_peak_wan: 940,
  },
  'Wuyue': {
    name_zh: '吳越國',
    dynasties: ['錢氏（907-978）'],
    capitals: ['杭州'],
    religions: ['佛教（吳越法藏宗）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '五代十國最和平政權。錢鏐建國、保境安民。978 末代錢俶納土歸宋、杭州得以保全。',
  },
  'Southern Tang': {
    name_zh: '南唐',
    dynasties: ['李氏（937-976）'],
    capitals: ['金陵（南京）'],
    religions: ['佛道並重'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '李昪建。後主李煜詞冠絕古今。975 趙匡胤遣曹彬攻金陵、976 滅國。',
  },
  'Goguryeo': {
    name_zh: '高句麗',
    dynasties: ['高氏（-37~668）'],
    capitals: ['卒本', '集安（國內城）', '平壤（427 遷）'],
    religions: ['佛教（372 傳入）＋祖靈信仰'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '朱蒙建國。廣開土王、長壽王盛世跨遼東與半島北部。612 隋煬帝四征皆敗。668 唐麗聯軍滅國、半島歸新羅。',
    population_peak_wan: 350,
    area_peak_wan_km2: 130,
  },

  // ========== A7. 非洲未補 ==========
  'Kingdom of Kongo': {
    name_zh: '剛果王國',
    dynasties: ['Lukeni 家族（c.1390-1888）'],
    capitals: ['姆班扎-剛果（聖薩爾瓦多）'],
    religions: ['本土＋天主教（1491 起王室改宗）'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '14 世紀末建。1483 葡萄牙人到、王 Nzinga a Nkuwu 1491 受洗。1665 安布伊拉戰役戰敗後分裂。1888 葡保護國。',
    population_peak_wan: 50,
  },
  'Ndongo': {
    name_zh: '恩東戈王國',
    dynasties: ['Ngola 王號（16-17 世紀）'],
    capitals: ['卡邦巴'],
    religions: ['本土＋天主教（部分）'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '安哥拉內陸 Mbundu 王國。Nzinga 女王（1583-1663）抵抗葡萄牙與卡薩奇族聯盟著名。1671 為葡所滅。',
  },
  'Luba': {
    name_zh: '盧巴王國',
    capitals: ['Mwibele'],
    religions: ['Bulopwe 神聖王權'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '剛果東南部班圖人王國（c.1585-1889）。發展 Bulopwe（神聖王權）制度，影響鄰邦盧旺達、布隆迪、隆達。1889 比利時剛果自由邦征服。',
  },
  'Lunda': {
    name_zh: '隆達帝國',
    dynasties: ['Mwata Yamvo 王號（c.1665-1887）'],
    capitals: ['Musumba'],
    religions: ['本土＋部分伊斯蘭'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '剛果南部至贊比亞的中非大帝國。經奴隸貿易與斯瓦希里商網繁榮。1887 為奇奧科族與比屬剛果擠壓而解體。',
  },
  'Asante': {
    name_zh: '阿散蒂帝國',
    dynasties: ['Oyoko 家族（c.1701-1957）'],
    capitals: ['庫馬西'],
    religions: ['本土 Akan 信仰＋黃金凳（Sika Dwa）王權'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '1701 Osei Tutu 建國。黃金凳象徵國魂。19 世紀四度抗英（1824/1873/1896/1900 黃金凳之戰）皆敗。1957 加納獨立納入。',
    population_peak_wan: 300,
  },
  'Dahomey': {
    name_zh: '達荷美王國',
    dynasties: ['Houégbadja 王朝（c.1600-1904）'],
    capitals: ['阿波美'],
    religions: ['Vodun（巫毒）'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '今貝南西非王國。「Mino」女兵團（達荷美亞馬遜）著名。19 世紀以奴隸與棕櫚油貿易繁榮。1894 法國第二次達荷美戰爭後吞併。',
  },
  'Buganda': {
    name_zh: '布干達王國',
    dynasties: ['Kabaka 王號（14 世紀-至今禮儀性）'],
    capitals: ['坎帕拉'],
    religions: ['本土＋伊斯蘭（1844）＋基督教（1877 英聖公會、1879 法白衣會）'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '維多利亞湖北岸班圖人王國。19 世紀王 Muteesa I 與 Mwanga II 時期三教競傳。1894 英保護國。1966 廢黜、1993 復辟為禮儀性王國。',
    population_peak_wan: 300,
  },
  'Rwanda': {
    name_zh: '盧安達王國',
    dynasties: ['Nyiginya 王朝'],
    capitals: ['尼揚扎'],
    religions: ['本土 Imana 信仰＋天主教（後期）'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '中非大湖區圖西／胡圖混居王國。19 世紀 Kigeli IV Rwabugiri 擴張。1899 德屬東非、1916 比屬。1959 胡圖革命廢君主、1962 獨立。',
    population_peak_wan: 200,
  },
  'Funj': {
    name_zh: '豐吉蘇丹國',
    dynasties: ['Unsab／Funj 家族（1504-1821）'],
    capitals: ['森納爾'],
    religions: ['伊斯蘭遜尼派蘇菲'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '蘇丹中部尼羅河上游伊斯蘭蘇丹國。1504 Amara Dunqas 建。17-18 世紀蘇菲傳教影響深遠。1821 埃及穆罕默德‧阿里征服。',
  },
  'Zaire': {
    name_zh: '薩伊',
    dynasties: ['蒙博托‧塞塞‧塞科（1965-1997）'],
    capitals: ['金夏沙'],
    religions: ['天主教＋金邦古教等獨立教會'],
    realm_id: 'southern', sphere_id: 'central-african-congolese',
    intro: '1965 蒙博托政變上台。1971 改名薩伊推「真實性」政策。冷戰美法盟友。1997 第一次剛果戰爭被卡比拉推翻、改回剛果民主共和國。',
    population_peak_wan: 4000,
  },
  'Yorubaland': {
    name_zh: '約魯巴地區',
    capitals: ['伊費', '奧約', '伊巴丹'],
    religions: ['Orisha 本土信仰（後輸出至加勒比 Santería／Candomblé）'],
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    intro: '西非奈及利亞西南部約魯巴人諸城邦群。伊費為神話起源中心、奧約為政治帝國（17-19 世紀）。19 世紀奴隸戰爭與富拉尼聖戰後 1893 英保護。',
    population_peak_wan: 500,
  },
  'Bornu Empire': {
    name_zh: '博爾努帝國',
    dynasties: ['Sayfawa 王朝（1380-1893）'],
    capitals: ['Ngazargamu', '庫卡瓦'],
    religions: ['伊斯蘭遜尼派'],
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    intro: '加涅姆-博爾努帝國的後繼，1380 從查德湖東岸遷至西岸博爾努。Idris Alooma（c.1571-1603）為盛期。1893 蘇丹奴隸販子拉比赫攻陷。',
  },

  // ========== 中國春秋戰國諸侯 ==========
  'Wu': {
    name_zh: '吳',
    dynasties: ['吳氏（傳 -1100 起，史可考 -585~-473）'],
    capitals: ['梅里', '姑蘇（蘇州）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '春秋末年姑蘇強國。闔閭採孫武為將，伍子胥相，破楚入郢（-506）。-473 夫差敗於越王勾踐，吳亡。',
  },
  'Yue': {
    name_zh: '越',
    dynasties: ['越氏（傳少康後裔，史可考 -555~-222）'],
    capitals: ['會稽（紹興）', '琅琊'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '春秋末年勾踐臥薪嘗膽滅吳（-473）。戰國時被楚滅（-222）。',
  },
  'Yuezhi': {
    name_zh: '月氏',
    capitals: ['敦煌', '巴克特拉（大月氏西遷後）'],
    realm_id: 'central', sphere_id: 'turanian-turkic',
    intro: '河西走廊遊牧民族。-176 為匈奴所敗西遷，分大月氏（中亞 → 後形成貴霜）／小月氏（青海）。',
  },
  'Zhoa': {
    name_zh: '周',
    dynasties: ['姬氏（-1100~-256）'],
    capitals: ['鎬京', '洛邑（東遷後）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: 'historical-basemaps polygon 拼字錯誤（應為 Zhou）。涵蓋早期周部族／西周／東周／春秋戰國時期。',
    successors: ['Qin'],
  },
  'Qin': {
    name_zh: '秦',
    dynasties: ['嬴氏（-905~-207）'],
    capitals: ['雍', '咸陽（-350 遷）'],
    realm_id: 'eastern', sphere_id: 'han',
    intro: '西周封贏非子，世居西陲。商鞅變法 -356 富強。-221 秦始皇統一六國。-210 始皇崩，二世胡亥被趙高弒。-207 子嬰降劉邦。',
    population_peak_wan: 3000,
    area_peak_wan_km2: 360,
    successors: ['Han Empire'],
  },
  'Wu (Three Kingdoms)': {
    name_zh: '東吳',
    realm_id: 'eastern', sphere_id: 'han',
    intro: '三國時期吳國（222-280），孫權建立。詳見 Eastern Wu。',
  },

  // ========== 2026-07-11 第六輪擴充：歐非中東 40 ==========
  // ========== 歐洲／中東／非洲組（40 條，2026-07-11 批次） ==========

  // ---------- 中東／波斯 ----------
  'Safavid Empire': {
    name_zh: '薩法維帝國',
    dynasties: ['薩法維王朝'],
    capitals: ['大不里士', '加茲溫', '伊斯法罕'],
    religions: ['什葉派伊斯蘭（十二伊瑪目派）'],
    population_peak_wan: 800,
    area_peak_wan_km2: 350,
    intro: '1501 年伊斯瑪儀一世建立，首度以什葉派為國教統一伊朗高原，與鄂圖曼、蒙兀兒並列近世三大伊斯蘭帝國。阿拔斯一世時遷都伊斯法罕，達於極盛，1722 年阿富汗人攻陷伊斯法罕後衰亡。',
    realm_id: 'central', sphere_id: 'persian',
    predecessors: ['Timurid Empire'],
    successors: ['Persia'],
  },
  'Eastern Roman Empire': {
    name_zh: '東羅馬帝國',
    dynasties: ['狄奧多西王朝', '利奧王朝', '查士丁尼王朝', '希拉克略王朝', '伊蘇里亞王朝'],
    capitals: ['君士坦丁堡'],
    religions: ['基督教（迦克墩正統）'],
    population_peak_wan: 2600,
    area_peak_wan_km2: 280,
    intro: '395 年羅馬帝國東西分治後的東半部（本段涵蓋 400-799 早中期）。查士丁尼一世頒《民法大全》、建聖索菲亞大教堂並收復北非義大利；7 世紀失敘利亞埃及於阿拉伯人後轉型為希臘語的中古帝國。',
    realm_id: 'central', sphere_id: 'aegean-asia-minor',
    predecessors: ['Roman Empire'],
    successors: ['Byzantine Empire'],
  },

  // ---------- 歐洲：北歐／東歐 ----------
  'Tsardom of Muscovy': {
    name_zh: '莫斯科沙皇國',
    dynasties: ['留里克王朝', '羅曼諾夫王朝（1613 起）'],
    capitals: ['莫斯科'],
    religions: ['東正教'],
    population_peak_wan: 1500,
    area_peak_wan_km2: 1400,
    intro: '1547 年伊凡四世（雷帝）加冕「沙皇」，繼「第三羅馬」意識形態自居東正教護持者。征服喀山、阿斯特拉罕並東拓西伯利亞至太平洋；1721 年彼得一世改號俄羅斯帝國。',
    realm_id: 'northern', sphere_id: 'russian-tatar',
    predecessors: ['Grand Duchy of Moscow'],
    successors: ['Russian Empire'],
  },
  'Denmark-Norway': {
    name_zh: '丹麥-挪威',
    dynasties: ['奧登堡王朝'],
    capitals: ['哥本哈根'],
    religions: ['天主教（前期）', '路德宗（1536 宗教改革後）'],
    intro: '丹麥與挪威的共主聯邦（1524/1537-1814），承卡爾馬聯合餘緒，領有冰島、格陵蘭與法羅群島。1536 年推行路德宗國教；1814 年《基爾條約》割挪威予瑞典而解體。',
    realm_id: 'western', sphere_id: 'nordic-livonian',
    predecessors: ['Denmark', 'Norway'],
    successors: ['Denmark', 'Sweden'],
  },
  'Teutonic Knights': {
    name_zh: '條頓騎士團國',
    capitals: ['馬爾堡（馬林堡）', '柯尼斯堡'],
    religions: ['天主教'],
    intro: '十字軍軍事修會在波羅的海建立的騎士團國家，13 世紀起征服並基督教化普魯士與立窩尼亞。1410 年坦能堡（格倫瓦德）之戰慘敗於波蘭-立陶宛；1525 年大團長改宗路德宗、世俗化為普魯士公國。',
    realm_id: 'western', sphere_id: 'nordic-livonian',
    successors: ['Prussia'],
  },

  // ---------- 歐洲：不列顛／伊比利 ----------
  'Scotland': {
    name_zh: '蘇格蘭王國',
    dynasties: ['鄧凱爾德王朝', '布魯斯王朝', '斯圖亞特王朝'],
    capitals: ['斯昆', '愛丁堡'],
    religions: ['天主教', '長老宗（1560 宗教改革後）'],
    population_peak_wan: 100,
    intro: '中世紀不列顛北部王國，傳統以 843 年肯尼思一世統一皮克特與蓋爾人為起點。1314 年班諾克本之戰確保獨立於英格蘭；1603 年詹姆士六世入繼英格蘭王位成共主，1707 年合併為大不列顛。',
    realm_id: 'western', sphere_id: 'british-celtic',
    successors: ['United Kingdom'],
  },
  'England': {
    name_zh: '英格蘭王國',
    dynasties: ['威塞克斯王朝', '諾曼王朝', '金雀花王朝', '蘭開斯特王朝', '約克王朝', '都鐸王朝'],
    capitals: ['溫徹斯特', '倫敦'],
    religions: ['天主教'],
    population_peak_wan: 500,
    intro: '中世紀不列顛南部王國，927 年埃塞爾斯坦統一諸盎格魯-撒克遜王國。1066 年諾曼征服重塑貴族與語言；1215 年《大憲章》開議會傳統；百年戰爭與玫瑰戰爭後由都鐸王朝開啟近世。',
    realm_id: 'western', sphere_id: 'british-celtic',
    successors: ['United Kingdom'],
  },
  'Aragón': {
    name_zh: '阿拉貢王國',
    dynasties: ['希梅內斯王朝', '巴塞隆納王朝', '特拉斯塔馬拉王朝'],
    capitals: ['薩拉戈薩'],
    religions: ['天主教'],
    intro: '1035 年立國的伊比利王國，1137 年與巴塞隆納伯國聯合後向地中海擴張，先後領有西西里、薩丁尼亞與那不勒斯。1469 年斐迪南二世與卡斯提亞的伊莎貝拉聯姻，催生統一的西班牙。',
    realm_id: 'western', sphere_id: 'latin-cultural',
    successors: ['Spain'],
  },
  'Navarre': {
    name_zh: '納瓦拉王國',
    dynasties: ['希梅內斯王朝', '香檳王朝', '埃夫勒王朝', '阿爾布雷王朝'],
    capitals: ['潘普洛納'],
    religions: ['天主教'],
    intro: '庇里牛斯山麓的巴斯克人王國，源於 824 年的潘普洛納王國，桑喬三世時一度號令基督教西班牙。1512 年南部被亞拉岡-卡斯提亞兼併，北部 1589 年隨亨利四世入繼法國王位。',
    realm_id: 'western', sphere_id: 'latin-cultural',
    successors: ['Spain', 'France'],
  },

  // ---------- 歐洲：中歐／義大利 ----------
  'Swiss Confederation': {
    name_zh: '瑞士邦聯',
    capitals: ['伯恩', '蘇黎世', '琉森'],
    religions: ['天主教', '新教（茲文利、喀爾文改革）'],
    intro: '以 1291 年烏里、施維茨、下瓦爾登三州永久同盟為傳統起點的山地共和同盟。1499 年士瓦本戰爭後實質脫離神聖羅馬帝國，1648 年《西發里亞和約》正式承認獨立；1798 年法軍入侵改組為赫爾維蒂共和國。',
    realm_id: 'western', sphere_id: 'central-european',
    predecessors: ['Holy Roman Empire'],
    successors: ['Switzerland'],
  },
  'Republic of the Seven Zenden': {
    name_zh: '瓦萊七區共和國',
    religions: ['天主教'],
    intro: '上瓦萊七個自治區（Zenden）組成的山地共和政體，逐步架空錫永主教的世俗權力並與瑞士邦聯結盟；1798 年被法國吞併，後成為瑞士瓦萊州。',
    realm_id: 'western', sphere_id: 'central-european',
    successors: ['Switzerland'],
  },
  'Austrian Empire': {
    name_zh: '奧地利帝國',
    dynasties: ['哈布斯堡王朝', '哈布斯堡-洛林王朝'],
    capitals: ['維也納'],
    religions: ['天主教'],
    population_peak_wan: 3600,
    area_peak_wan_km2: 70,
    intro: '哈布斯堡君主國的中歐多民族帝國，1804 年法蘭茲一世正式稱奧地利皇帝。梅特涅主導的維也納體系中樞；1848 革命動搖後，1867 年折衷改組為奧匈二元帝國。',
    realm_id: 'western', sphere_id: 'central-european',
    predecessors: ['Holy Roman Empire'],
    successors: ['Austria Hungary'],
  },
  'Lombardy': {
    name_zh: '倫巴底',
    capitals: ['米蘭'],
    religions: ['天主教'],
    intro: '波河平原以米蘭為中心的富庶地區，近世先後受西班牙、奧地利哈布斯堡統治，1815 年編入奧屬倫巴底-威尼西亞王國；1859 年隨義大利統一運動併入薩丁尼亞-義大利。',
    realm_id: 'western', sphere_id: 'latin-cultural',
    successors: ['Italy'],
  },
  'Parma': {
    name_zh: '帕爾馬公國',
    dynasties: ['法爾內塞王朝', '波旁-帕爾馬王朝'],
    capitals: ['帕爾馬'],
    religions: ['天主教'],
    intro: '1545 年教宗保祿三世為其子建立的義大利公國，法爾內塞家族統治至 1731 年，後歸西班牙波旁支系；拿破崙時期一度由前皇后瑪麗‧路易絲領有，1860 年併入義大利。',
    realm_id: 'western', sphere_id: 'latin-cultural',
    successors: ['Italy'],
  },
  'Massa': {
    name_zh: '馬薩',
    capitals: ['馬薩'],
    intro: '托斯卡納西北濱海的馬薩與卡拉拉小公國，馬拉斯皮納-奇博家族世襲統治，以卡拉拉大理石聞名；1829 年併入摩德納公國。',
    realm_id: 'western', sphere_id: 'latin-cultural',
  },
  'Fivizzano': {
    name_zh: '菲維扎諾',
    intro: '托斯卡納盧尼賈納山區小邦，長期為佛羅倫斯（托斯卡納大公國）在盧尼賈納的治所與飛地。',
    realm_id: 'western', sphere_id: 'latin-cultural',
  },
  'Pontremoli': {
    name_zh: '蓬特雷莫利',
    intro: '盧尼賈納谷地要衝小邦，扼亞平寧山口商路，曾屬米蘭與西班牙，1650 年售予托斯卡納大公國。',
    realm_id: 'western', sphere_id: 'latin-cultural',
  },

  // ---------- 草原諸汗國 ----------
  'Crimean Khanate': {
    name_zh: '克里米亞汗國',
    dynasties: ['格來王朝（朮赤系）'],
    capitals: ['巴赫奇薩賴'],
    religions: ['伊斯蘭遜尼派'],
    intro: '1441 年金帳汗國分裂中由哈吉‧格來建立，1475 年起臣屬奧斯曼帝國，以對東歐草原的騎兵襲掠與奴隸貿易著稱，1571 年一度焚莫斯科；1783 年被葉卡捷琳娜二世吞併。',
    realm_id: 'northern', sphere_id: 'russian-tatar',
    predecessors: ['Golden Horde'],
    successors: ['Russian Empire'],
  },
  'Nogai Horde': {
    name_zh: '諾蓋汗國',
    religions: ['伊斯蘭遜尼派'],
    intro: '金帳汗國崩解後活躍於裏海北岸至烏拉爾草原的遊牧政權（15-17 世紀），統領出自權臣埃迪古後裔而非成吉思汗系；17 世紀被東來的卡爾梅克人擊潰而離散。',
    realm_id: 'northern', sphere_id: 'turanian-turkic',
    predecessors: ['Golden Horde'],
  },
  'Khiva Khanate': {
    name_zh: '希瓦汗國',
    dynasties: ['阿拉布沙王朝（昔班尼系）', '貢格拉特王朝（後期）'],
    capitals: ['舊烏爾根奇', '希瓦'],
    religions: ['伊斯蘭遜尼派'],
    intro: '1511 年昔班尼系烏茲別克人在花剌子模綠洲建立的汗國，以希瓦為都，靠綠洲農業與商隊（含奴隸）貿易立國；1873 年淪為俄羅斯保護國，1920 年亡。',
    realm_id: 'northern', sphere_id: 'turanian-turkic',
    successors: ['Russian Empire'],
  },
  'Quazaq Khanate': {
    name_zh: '哈薩克汗國',
    dynasties: ['朮赤系（克烈汗與賈尼別克汗後裔）'],
    capitals: ['突厥斯坦'],
    religions: ['伊斯蘭遜尼派'],
    intro: '1465 年前後克烈與賈尼別克率部脫離烏茲別克汗國，在七河與欽察草原建立的遊牧汗國，後分大、中、小三玉茲；18 世紀受準噶爾重創，19 世紀漸次併入俄羅斯。',
    realm_id: 'northern', sphere_id: 'turanian-turkic',
    predecessors: ['Golden Horde'],
    successors: ['Russian Empire'],
  },
  'Chagatai Khanate': {
    name_zh: '察合台汗國',
    dynasties: ['察合台系（成吉思汗次子後裔）'],
    capitals: ['阿力麻里'],
    religions: ['騰格里信仰／薩滿（前期）', '伊斯蘭遜尼派（14 世紀後）'],
    area_peak_wan_km2: 350,
    intro: '蒙古四大汗國之一，領有中亞河中地區與塔里木盆地。14 世紀分裂為西察合台與東察合台（蒙兀兒斯坦），西部政權 1370 年為帖木兒取代。',
    realm_id: 'northern', sphere_id: 'turanian-turkic',
    predecessors: ['Mongol Empire'],
    successors: ['Timurid Empire'],
  },
  'Bulgar Khanate': {
    name_zh: '伏爾加保加利亞',
    capitals: ['保加爾', '比利亞爾'],
    religions: ['伊斯蘭遜尼派（922 年皈依）'],
    intro: '伏爾加河與卡馬河匯流處的突厥語穆斯林國家，922 年在阿拔斯使團（伊本‧法德蘭隨行記述）見證下皈依伊斯蘭，為歐洲最北的伊斯蘭政權，靠毛皮與河運貿易繁榮；1236 年被蒙古征服後併入金帳汗國。',
    realm_id: 'northern', sphere_id: 'russian-tatar',
    successors: ['Golden Horde'],
  },

  // ---------- 馬格里布 ----------
  'Hafsid Caliphate': {
    name_zh: '哈夫斯王朝',
    capitals: ['突尼斯'],
    religions: ['伊斯蘭遜尼（馬利基派）'],
    intro: '1229 年脫離穆瓦希德（阿穆瓦希德）自立，統治伊夫里基亞（今突尼西亞一帶）三百餘年，一度獲麥加謝里夫承認稱哈里發，突尼斯成馬格里布學術與商業重鎮；1574 年亡於奧斯曼。',
    realm_id: 'western', sphere_id: 'carthaginian-maghreb',
    predecessors: ['Almohad Caliphate'],
    successors: ['Ottoman Empire'],
  },
  'Algiers': {
    name_zh: '阿爾及爾',
    capitals: ['阿爾及爾'],
    religions: ['伊斯蘭遜尼派'],
    intro: '1516 年巴巴羅薩兄弟建立、名義臣屬奧斯曼的阿爾及爾攝政國，以私掠海軍（巴巴里海盜）稱雄西地中海三個世紀，實際由當地德伊自治；1830 年法國入侵滅亡。',
    realm_id: 'western', sphere_id: 'carthaginian-maghreb',
    predecessors: ['Ottoman Empire'],
    successors: ['France'],
  },
  'Tunis': {
    name_zh: '突尼斯',
    dynasties: ['穆拉德王朝', '侯賽因王朝（1705 起）'],
    capitals: ['突尼斯'],
    religions: ['伊斯蘭遜尼派'],
    intro: '1574 年奧斯曼滅哈夫斯王朝後設立的突尼斯攝政國，1705 年起侯賽因家族世襲貝伊、實質自治；1881 年《巴爾杜條約》淪為法國保護國。',
    realm_id: 'western', sphere_id: 'carthaginian-maghreb',
    predecessors: ['Hafsid Caliphate'],
    successors: ['France'],
  },

  // ---------- 尼羅河中游／東非 ----------
  'Axum': {
    name_zh: '阿克蘇姆',
    capitals: ['阿克蘇姆', '阿杜利斯'],
    religions: ['多神教（前期）', '基督教（4 世紀埃扎納王皈依）'],
    area_peak_wan_km2: 125,
    intro: '衣索比亞高原與紅海沿岸的貿易帝國，鑄幣並豎立巨型石碑。4 世紀埃扎納王皈依基督教，為世界最早的基督教國家之一；6 世紀一度跨海征服葉門，7 世紀後因伊斯蘭興起與商路改道而衰落。',
    realm_id: 'southern', sphere_id: 'ethiopian',
    successors: ['Ethiopia'],
  },
  'Meroe': {
    name_zh: '麥羅埃',
    capitals: ['麥羅埃'],
    religions: ['努比亞化的埃及多神教（阿蒙、獅神阿佩德馬克）'],
    intro: '庫施王國約於前 6 世紀南遷麥羅埃後的階段，以冶鐵業與獨特的窄型金字塔群聞名，並發展出尚未完全解讀的麥羅埃文字；約 350 年被阿克蘇姆擊潰後消亡。',
    realm_id: 'central', sphere_id: 'egyptian',
    predecessors: ['Kush'],
    successors: ['Axum'],
  },
  'Kush': {
    name_zh: '庫施',
    capitals: ['凱爾邁', '納帕塔'],
    religions: ['埃及多神教（阿蒙崇拜）與努比亞在地信仰'],
    intro: '尼羅河中游努比亞古國，先後以凱爾邁與納帕塔為中心。前 8 世紀皮耶北征建立埃及第二十五王朝「黑法老」，後被亞述逐回努比亞，王統南遷麥羅埃延續。',
    realm_id: 'central', sphere_id: 'egyptian',
    successors: ['Meroe'],
  },

  // ---------- 西非／薩赫勒 ----------
  'Empire of Ghana': {
    name_zh: '迦納帝國',
    capitals: ['昆比薩利赫（推測）'],
    religions: ['傳統信仰（王室）', '伊斯蘭（商人社群）'],
    intro: '索寧克人建立的西非最早有紀錄的大國，控制撒哈拉縱貫的黃金與鹽貿易，阿拉伯地理學家譽為「黃金之地」；11 世紀後因商路轉移與外患衰落，勢力範圍後為馬利帝國承繼。',
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    successors: ['Mali'],
  },
  'Kanem': {
    name_zh: '加涅姆',
    dynasties: ['杜古瓦王朝', '賽法瓦王朝'],
    capitals: ['恩吉米'],
    religions: ['傳統信仰（前期）', '伊斯蘭遜尼派（11 世紀後）'],
    intro: '查德湖東北的薩赫勒王國（約 8 世紀起），賽法瓦王朝為非洲最長壽王統之一；11 世紀胡梅王皈依伊斯蘭，盛時商路北通費贊；14 世紀因內亂西遷博爾努。',
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    successors: ['Bornu-Kanem'],
  },
  'Darfur': {
    name_zh: '達爾富爾蘇丹國',
    dynasties: ['凱拉王朝'],
    capitals: ['法希爾'],
    religions: ['伊斯蘭遜尼派'],
    intro: '17 世紀凱拉王朝在蘇丹西部富爾人地區建立的伊斯蘭蘇丹國，控制通往埃及的「四十日路」商道。1874 年亡於埃及勢力，1898 年短暫復國，1916 年併入英埃蘇丹。',
    realm_id: 'southern', sphere_id: 'west-african-sahel',
  },
  'Wadai': {
    name_zh: '瓦達伊蘇丹國',
    capitals: ['瓦拉', '阿貝歇'],
    religions: ['伊斯蘭遜尼派'],
    intro: '17 世紀初在今查德東部建立的伊斯蘭蘇丹國，倚跨撒哈拉商路致富，長期與達爾富爾、博爾努爭衡；1909 年被法國征服。',
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    successors: ['France'],
  },
  'Bagirmi': {
    name_zh: '巴吉爾米蘇丹國',
    capitals: ['馬森亞'],
    religions: ['伊斯蘭遜尼派'],
    intro: '16 世紀在查德湖東南建立的蘇丹國，時而臣屬博爾努或瓦達伊之間求存；1897 年接受法國保護。',
    realm_id: 'southern', sphere_id: 'west-african-sahel',
    successors: ['France'],
  },

  // ---------- 中南部非洲／幾內亞灣 ----------
  'Rozwi': {
    name_zh: '羅茲維',
    capitals: ['丹南貢貝'],
    religions: ['姆瓦里（Mwari）信仰'],
    intro: '約 1660 年昌加米雷‧東博驅逐葡萄牙人後在辛巴威高原建立的紹納人國家，承繼大辛巴威的石造建築傳統，壟斷內陸黃金與象牙貿易；19 世紀初姆非卡尼動亂中被恩古尼人擊滅。',
    realm_id: 'southern', sphere_id: 'southern-african-bantu',
  },
  'Lozi': {
    name_zh: '洛齊王國',
    capitals: ['利亞盧伊'],
    religions: ['傳統信仰（尼揚貝至上神）'],
    intro: '尚比西河上游氾濫平原的王國（巴洛策蘭），以隨洪水季節遷都的雙都制著稱；19 世紀中一度被南來的科洛洛人征服後復國，1890 年代與英國南非公司立約成為保護地。',
    realm_id: 'southern', sphere_id: 'southern-african-bantu',
  },
  'Akan': {
    name_zh: '阿坎諸邦',
    religions: ['阿坎傳統信仰（尼揚科朋至上神與祖靈）'],
    intro: '黃金海岸內陸阿坎語族諸國（博諾、登基拉、阿克瓦穆等），以金礦與可拉果貿易繁榮，並與葡、荷、英沿海商站往來；18 世紀初為新興的阿散蒂帝國整併。',
    realm_id: 'southern', sphere_id: 'gulf-of-guinea',
    successors: ['Asante'],
  },

  // ---------- 古南阿拉伯／黎凡特 ----------
  'Himyarite Kingdom': {
    name_zh: '希木葉爾王國',
    capitals: ['扎法爾'],
    religions: ['南阿拉伯多神教', '猶太教（4 世紀末王室改宗）'],
    intro: '葉門高地王國（約前 110 年起），兼併示巴與哈德拉毛統一南阿拉伯，扼紅海-印度洋商路。4 世紀末王室改宗猶太教；525 年因末王迫害納季蘭基督徒，引來阿克蘇姆跨海征服。',
    realm_id: 'central', sphere_id: 'arabian',
    predecessors: ['Saba'],
    successors: ['Axum'],
  },
  'Nabatean Kingdom': {
    name_zh: '納巴泰王國',
    capitals: ['佩特拉'],
    religions: ['納巴泰多神教（杜莎拉神、烏扎女神）'],
    intro: '以鑿岩之城佩特拉為都的阿拉伯商隊王國，壟斷乳香沒藥商路，沙漠集水工程冠絕古代近東；106 年被羅馬圖拉真兼併為阿拉伯行省。',
    realm_id: 'central', sphere_id: 'arabian',
    successors: ['Roman Empire'],
  },
  'Qataban': {
    name_zh: '卡塔班',
    capitals: ['廷納'],
    religions: ['南阿拉伯多神教（安姆月神）'],
    intro: '南阿拉伯古王國之一，以廷納為都，扼「乳香之路」中段而富庶，與示巴、哈德拉毛長期爭衡；西元前後領土為哈德拉毛與希木葉爾瓜分。',
    realm_id: 'central', sphere_id: 'arabian',
    successors: ['Himyarite Kingdom', 'Hadramaut'],
  },
  // ========== 2026-07-11 第六輪擴充：亞洲美洲 40 ==========
  // ========== 古代印度 ==========
  'Hindu kingdoms': {
    name_zh: '印度教諸王國',
    religions: ['婆羅門教／印度教', '佛教', '耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '源圖對 -500~799 年間北印度未逐一標示的諸王國之集體標示，涵蓋十六大國之外的列國與笈多帝國前後的區域諸邦。此期婆羅門教逐步轉型為印度教，與佛教、耆那教並立競逐。',
  },
  'Kalinga': {
    name_zh: '羯陵伽',
    religions: ['耆那教', '佛教', '印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度東海岸（今奧里薩一帶）古國，-261 年阿育王的羯陵伽戰爭以慘烈聞名，促使其皈依佛教。孔雀帝國崩解後在卡拉維拉王領導下復興，尊崇耆那教。',
    successors: ['Orissa'],
  },
  'Magadha': {
    name_zh: '摩揭陀',
    dynasties: ['訶黎央伽王朝', '希蘇那伽王朝', '難陀王朝'],
    capitals: ['王舍城', '華氏城'],
    religions: ['婆羅門教', '佛教', '耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '恆河中游平原的古印度十六大國之首，佛陀與大雄傳道的核心舞台，王舍城與華氏城先後為都。難陀王朝統一恆河流域，奠定孔雀帝國之基礎。',
    successors: ['Mauryan Empire'],
  },
  'Pandya state': {
    name_zh: '潘地亞',
    capitals: ['馬杜賴'],
    religions: ['印度教（濕婆派）', '耆那教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '泰米爾三王國中最南端者，桑加姆文學時代即已存在；源圖 polygon 標示其中世紀復興期。13 世紀後期一度為南印度最強，1311 年德里蘇丹國入侵後衰落。',
  },
  'Saka Kingdom': {
    name_zh: '塞迦王國',
    capitals: ['烏賈因'],
    religions: ['印度教', '佛教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '中亞塞迦（斯基泰）人南下印度西部建立的政權，史稱西薩特拉普，據有古吉拉特與摩臘婆。與百乘王朝長期爭戰，約 395 年亡於笈多帝國。',
    successors: ['Gupta Empire'],
  },
  'Suren Kingdom': {
    name_zh: '蘇倫王國',
    capitals: ['呾叉始羅'],
    religions: ['瑣羅亞斯德教', '佛教'],
    realm_id: 'central', sphere_id: 'persian',
    intro: '帕提亞七大貴族之首蘇倫家族在錫斯坦至犍陀羅一帶的半獨立王國（印度-帕提亞王國）。最著名的君主貢多法勒斯，即基督教傳統中使徒多馬曾造訪的印度王。',
    successors: ['Kushan Empire'],
  },

  // ========== 德干蘇丹國與中世紀印度 ==========
  'Ahmadnagar': {
    name_zh: '艾哈邁德納格爾蘇丹國',
    dynasties: ['尼扎姆‧沙希王朝'],
    capitals: ['艾哈邁德納格爾'],
    religions: ['伊斯蘭教（什葉派宮廷）', '印度教（民間多數）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '德干五蘇丹國之一（1490-1636），自巴赫曼尼蘇丹國分裂而出。1565 年與盟邦聯手於塔利科塔之役擊潰毗奢耶那伽羅；17 世紀雖有名相馬利克‧安巴爾力抗，終為蒙兀兒吞併。',
    predecessors: ['Bahmani Kingdom'],
    successors: ['Mughal Empire'],
  },
  'Bengal': {
    name_zh: '孟加拉',
    dynasties: ['伊利亞斯‧沙希王朝', '侯賽因‧沙希王朝', '蒙兀兒省督與納瓦卜'],
    capitals: ['高爾（Gaur）', '達卡', '穆爾希達巴德'],
    religions: ['伊斯蘭教（遜尼派）', '印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '孟加拉蘇丹國（1352 立）為南亞最富庶的貿易政權之一；1576 年併入蒙兀兒為孟加拉省，18 世紀納瓦卜實質自立。1757 年普拉西戰役後漸入英國東印度公司之手。',
  },
  'Bidar': {
    name_zh: '比達爾蘇丹國',
    dynasties: ['巴里德‧沙希王朝'],
    capitals: ['比達爾'],
    religions: ['伊斯蘭教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '德干五蘇丹國中最小者（1492-1619），據有巴赫曼尼蘇丹國末代都城比達爾。1619 年被比賈普爾蘇丹國兼併。',
    predecessors: ['Bahmani Kingdom'],
    successors: ['Bijapur'],
  },
  'Bijapur': {
    name_zh: '比賈普爾蘇丹國',
    dynasties: ['阿迪勒‧沙希王朝'],
    capitals: ['比賈普爾'],
    religions: ['伊斯蘭教', '印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '德干五蘇丹國之一（1490-1686），以果爾‧貢巴茲巨型圓頂陵等印度-伊斯蘭建築著稱。與馬拉塔的希瓦吉纏鬥多年，1686 年被奧朗則布攻滅。',
    predecessors: ['Bahmani Kingdom'],
    successors: ['Mughal Empire'],
  },
  'Golkonda': {
    name_zh: '戈爾孔達蘇丹國',
    dynasties: ['庫特布‧沙希王朝'],
    capitals: ['戈爾孔達', '海得拉巴'],
    religions: ['伊斯蘭教（什葉派）', '印度教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '德干五蘇丹國之一（1518-1687），以戈爾孔達鑽石礦（光之山鑽石產地）富甲一方，並建新都海得拉巴。1687 年被奧朗則布攻滅。',
    predecessors: ['Bahmani Kingdom'],
    successors: ['Mughal Empire'],
  },
  'Orissa': {
    name_zh: '奧里薩',
    dynasties: ['東恆伽王朝', '迦闍帕提王朝'],
    capitals: ['卡塔克'],
    religions: ['印度教（闍格納特崇拜）'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '印度東海岸羯陵伽故地的中世紀王國。東恆伽王朝建普里闍格納特神廟與科納拉克太陽神廟；迦闍帕提王朝盛時北抵恆河、南及克里希納河。',
    predecessors: ['Kalinga'],
  },

  // ========== 內亞與東北亞 ==========
  'Zhangzhung Kingdom': {
    name_zh: '象雄',
    capitals: ['穹隆銀城'],
    religions: ['苯教'],
    realm_id: 'eastern', sphere_id: 'tibetan',
    intro: '青藏高原西部的古國，以岡仁波齊神山一帶為中心，苯教傳統尊之為發源地。7 世紀為吐蕃松贊干布所併。',
    successors: ['Tibetan Empire'],
  },
  'Xiongnu': {
    name_zh: '匈奴',
    dynasties: ['攣鞮氏（單于王族）'],
    capitals: ['龍城'],
    religions: ['騰格里信仰', '薩滿信仰'],
    realm_id: 'northern', sphere_id: 'mongolic-tungusic',
    intro: '蒙古高原第一個游牧帝國，-209 年冒頓單于統一諸部後與漢朝纏鬥兩百年。-54 年分裂為南北，南匈奴附漢、北匈奴西遁；語系歸屬至今未定。',
  },
  'Koguryo': {
    name_zh: '高句麗',
    dynasties: ['高氏'],
    capitals: ['國內城', '平壤'],
    religions: ['佛教', '薩滿信仰'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮三國之一，據有滿洲東部與朝鮮半島北部，屢抗隋唐大軍，668 年亡於唐與新羅聯軍。',
    successors: ['Balhae'],
  },
  'Gaya': {
    name_zh: '伽倻',
    capitals: ['金官（金海）'],
    religions: ['薩滿信仰', '佛教'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '朝鮮半島南端洛東江流域的城邦聯盟（1-6 世紀），以鐵器生產與對倭貿易著稱，始終未成中央集權國家。562 年為新羅所併。',
    successors: ['Silla'],
  },
  'Yamato': {
    name_zh: '大和',
    capitals: ['飛鳥', '平城京（奈良）', '平安京（京都）'],
    religions: ['神道', '佛教（6 世紀傳入）'],
    realm_id: 'asia-pacific', sphere_id: 'kuroshio',
    intro: '日本列島最早的統一王權，以大和盆地為核心，藉巨大古墳與氏姓制度整合列島。7 世紀大化改新引入唐制律令，逐步轉型為「日本」國號下的律令國家。',
    successors: ['Japan'],
  },

  // ========== 東南亞 ==========
  'Mataram': {
    name_zh: '馬打蘭',
    dynasties: ['珊闍耶王朝', '夏連特拉王朝'],
    religions: ['印度教（濕婆派）', '大乘佛教'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '中古爪哇的印度教-佛教王國（又稱 Medang），婆羅浮屠與普蘭巴南兩大建築群皆其治下所建。10 世紀重心東移爪哇東部；與 16 世紀末的伊斯蘭馬打蘭蘇丹國同名異代。',
  },
  'Pagan': {
    name_zh: '蒲甘王朝',
    capitals: ['蒲甘'],
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '緬甸第一個統一王朝，1044 年阿奴律陀立國後自孟族取得上座部佛教傳統，蒲甘平原留下三千餘座佛塔。1287 年蒙古入侵後解體。',
    successors: ['Ava'],
  },
  'Aceh': {
    name_zh: '亞齊蘇丹國',
    capitals: ['班達亞齊'],
    religions: ['伊斯蘭教（遜尼派）'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '蘇門答臘北端的伊斯蘭強權，17 世紀初伊斯坎達‧穆達治下控制麻六甲海峽兩岸胡椒貿易，號稱「麥加走廊」。1873-1904 年亞齊戰爭後才被荷蘭征服。',
    successors: ['Dutch East Indies'],
  },
  'Malacca': {
    name_zh: '麻六甲蘇丹國',
    capitals: ['麻六甲'],
    religions: ['伊斯蘭教（遜尼派）'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '15 世紀控制麻六甲海峽的貿易國家，鄭和下西洋的重要基地，東南亞伊斯蘭化的樞紐。1511 年被葡萄牙攻陷，王室南遷柔佛。',
  },
  'Shan states': {
    name_zh: '撣邦諸國',
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '源圖對緬甸東北高原撣族土司諸邦的集體標示，涵蓋孟養、孟拱、木邦、孟密等。蒲甘崩解後長期半自立，週旋於緬甸諸王朝與明清之間。',
  },
  'Rattanakosin Kingdom': {
    name_zh: '拉達那哥欣王國',
    dynasties: ['卻克里王朝'],
    capitals: ['曼谷'],
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '1782 年拉瑪一世遷都曼谷後的暹羅王朝，即今泰國卻克里王朝之開端。19 世紀在英法夾縫中以外交與現代化改革維持獨立，為東南亞唯一未被殖民的國家。',
    predecessors: ['Ayutthaya'],
    successors: ['Thailand'],
  },
  'Burmese kingdoms': {
    name_zh: '緬甸諸王國',
    religions: ['上座部佛教'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '源圖對 15-17 世紀緬甸分立政權的集體標示，涵蓋上緬甸的阿瓦、下緬甸的勃固（漢達瓦底）與若開的妙烏等王國。16 世紀中葉為東吁王朝所統一。',
  },

  // ========== 中美洲 ==========
  'Maya chiefdoms and states': {
    name_zh: '馬雅諸邦',
    religions: ['馬雅多神教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '源圖對前古典晚期至古典早期馬雅政體的集體標示，涵蓋米拉多爾盆地的納克貝、艾爾米拉多與早期蒂卡爾等。此期馬雅文字與長紀曆已然成形。',
  },
  'Maya city-states': {
    name_zh: '馬雅城邦',
    religions: ['馬雅多神教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '源圖對後古典期馬雅諸政體的集體標示，涵蓋猶加敦的奇琴伊察、瑪雅潘與高地的基切、卡克奇克爾等王國。馬雅文字為新大陸唯一成熟的原生文字系統。',
  },
  'Maya': {
    name_zh: '馬雅',
    religions: ['馬雅多神教', '天主教（表層）'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '西班牙征服後仍未臣服的馬雅殘存政體之集體標示：佩滕湖區的伊察王國遲至 1697 年才陷落，猶加敦階級戰爭（1847 起）中的查恩聖克魯斯馬雅則自立至 1901 年。',
  },
  'Monte Albán': {
    name_zh: '蒙特阿爾班',
    capitals: ['蒙特阿爾班'],
    religions: ['薩波特克多神教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '瓦哈卡谷地薩波特克文明的山頂都城，約 -500 年建城。薩波特克文字為中美洲最早的文字系統之一，符合本站「新大陸有文字才算政權」的標準。約 8-9 世紀廢棄。',
  },
  'Teotihuacán': {
    name_zh: '特奧蒂瓦坎',
    capitals: ['特奧蒂瓦坎'],
    religions: ['羽蛇神與雨神特拉洛克崇拜'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '墨西哥盆地的巨型都市國家，太陽金字塔與亡靈大道所在，盛期為美洲最大城市，影響力遠及馬雅地區。有記號系統但文字化程度仍有爭議；約 6 世紀中衰落焚毀。',
  },
  'Toltec Empire': {
    name_zh: '托爾特克',
    capitals: ['圖拉'],
    religions: ['羽蛇神崇拜'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '10-12 世紀以圖拉為中心的中墨西哥政權，阿茲特克人尊其為文明典範並自稱其後裔。未留下成熟文字，事蹟多賴後世傳說重構——依本站標準本不列為政權，此 polygon 為源資料既存分類。',
    successors: ['Aztec Empire'],
  },
  'Mixtec Empire': {
    name_zh: '米斯特克',
    capitals: ['蒂蘭通戈', '圖圖特佩克'],
    religions: ['米斯特克多神教'],
    realm_id: 'latin-america', sphere_id: 'mesoamerican',
    intro: '瓦哈卡山地的米斯特克諸王國，以金工與《努塔爾抄本》等圖畫文字抄本聞名，貴族系譜可上溯數百年。16 世紀初部分臣服阿茲特克，旋為西班牙征服。',
  },

  // ========== 安地斯 ==========
  'Chimú Empire': {
    name_zh: '奇穆帝國',
    capitals: ['昌昌'],
    religions: ['月神信仰（Si）'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '秘魯北海岸的安地斯強權，泥磚巨城昌昌為前哥倫布美洲最大城市之一。無文字系統（依本站標準本不列為政權，此 polygon 為源資料既存分類），約 1470 年為印加帝國所併。',
    successors: ['Inca Empire'],
  },
  'Huari Empire': {
    name_zh: '瓦里帝國',
    capitals: ['瓦里'],
    religions: ['杖神崇拜'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '中地平線時期（約 600-1000）安地斯中部高原的擴張性政權，道路網與行政聚落為印加制度之先聲。無文字，僅有結繩記事的早期形態。',
  },
  'Tiahuanaco Empire': {
    name_zh: '蒂亞瓦納科',
    capitals: ['蒂亞瓦納科'],
    religions: ['杖神（太陽門神像）崇拜'],
    realm_id: 'latin-america', sphere_id: 'andean',
    intro: '的的喀喀湖南岸的高原祭祀都城與政權（約 600-1000），以太陽門與巨石建築著稱，影響及於南安地斯。無文字系統，與瓦里並立為中地平線兩大中心。',
  },

  // ========== 殖民政體與印度洋 ==========
  'Dutch East Indies': {
    name_zh: '荷屬東印度',
    capitals: ['巴達維亞（今雅加達）'],
    religions: ['伊斯蘭教', '基督新教', '印度教（峇里）'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '荷蘭東印度公司 1799 年解散後由荷蘭政府接管的殖民地，經爪哇戰爭與亞齊戰爭至 20 世紀初才控制全群島。1942 年日軍佔領，1945 年印尼宣布獨立、1949 年荷蘭承認。',
    population_peak_wan: 7000,
    area_peak_wan_km2: 190,
    successors: ['Indonesia'],
  },
  'Malaya': {
    name_zh: '英屬馬來亞',
    capitals: ['新加坡（海峽殖民地）', '吉隆坡（馬來聯邦）'],
    religions: ['伊斯蘭教', '佛教與民間信仰（華人）', '印度教（印度移民）'],
    realm_id: 'asia-pacific', sphere_id: 'banua',
    intro: '英國在馬來半島的殖民體系總稱，含海峽殖民地、馬來聯邦與非聯邦土邦。錫礦與橡膠經濟引入大量華人與印度移民，形塑今日馬來西亞的多元族群結構。',
    successors: ['Malaysia'],
  },
  'Ceylon (Dutch)': {
    name_zh: '荷屬錫蘭',
    capitals: ['可倫坡'],
    religions: ['上座部佛教', '印度教', '基督新教（歸正會）', '天主教'],
    realm_id: 'eastern', sphere_id: 'indian',
    intro: '荷蘭東印度公司 1658 年逐走葡萄牙人後控制的錫蘭沿海地帶，以肉桂貿易為命脈；內陸康提王國始終未服。1796 年為英國奪取。',
    successors: ['Ceylon'],
  },
  'Cochin China': {
    name_zh: '交趾支那',
    capitals: ['西貢'],
    religions: ['大乘佛教', '天主教', '高台教（1926 起）'],
    realm_id: 'asia-pacific', sphere_id: 'mekong',
    intro: '法國 1862 年起在越南南部建立的直轄殖民地，以西貢為中心開發湄公河三角洲稻米出口。不同於保護國安南與東京採直接統治，1949 年併回越南國。',
    successors: ['Vietnam'],
  },
  'Islamic city-states': {
    name_zh: '伊斯蘭城邦',
    religions: ['伊斯蘭教（遜尼派）'],
    realm_id: 'southern', sphere_id: 'east-african-swahili',
    intro: '源圖對東非斯瓦希里海岸貿易城邦的集體標示，涵蓋基爾瓦、蒙巴薩、摩加迪休、帕泰等。以印度洋季風貿易輸出黃金與象牙，斯瓦希里語文化於此成形；16 世紀起先後受葡萄牙與阿曼支配。',
  },
  'Muscat': {
    name_zh: '馬斯喀特',
    capitals: ['馬斯喀特'],
    religions: ['伊斯蘭教（伊巴德派）'],
    realm_id: 'central', sphere_id: 'arabian',
    intro: '阿曼海岸的港市政權，中世紀為印度洋航路要衝。1507 年被葡萄牙佔領為東方航線據點，17 世紀中阿曼亞里巴王朝逐走葡人，其後發展為馬斯喀特與阿曼蘇丹國。',
    successors: ['Muscat and Oman'],
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

