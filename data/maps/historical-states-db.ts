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

export interface HistoricalState extends StateSkeleton, StateDetail {
  /** Slug id（snake_case 化的英文名） */
  id: string
  /** 細節是否已填（false = 只有骨架資料） */
  has_detail: boolean
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
}

// ===== 工具函數 =====

export function slugifyStateName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

/**
 * 從 skeleton + details merge 成完整 HistoricalState list
 */
export function mergeStates(skeleton: StateSkeleton[]): HistoricalState[] {
  return skeleton.map(sk => {
    const detail = STATE_DETAILS[sk.name_en] || {}
    return {
      ...sk,
      ...detail,
      id: slugifyStateName(sk.name_en),
      has_detail: !!STATE_DETAILS[sk.name_en],
    }
  })
}
