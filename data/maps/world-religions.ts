/**
 * 全球八大人文宗教界域 — 主題地圖資料
 * 資料源：根目錄 全球八大人文宗教界域.docx
 * 8 大界域配色定案見 memory/project_maps_feature.md
 */

export type RealmId =
  | 'central'
  | 'eastern'
  | 'latin-america'
  | 'western'
  | 'asia-pacific'
  | 'southern'
  | 'northern'
  | 'north-america'

export interface Realm {
  id: RealmId
  index: number
  name_zh: string
  name_en: string
  color: string
  /** [lng, lat] — manually picked for stable label position on the map */
  label_lnglat: [number, number]
  intro?: string
}

export interface Member {
  iso_a3: string
  admin1?: string
  label: string
  order: number
  is_extension?: boolean
  note?: string
}

export interface CulturalSphere {
  id: string
  name_zh: string
  name_en: string
  realm_id: RealmId
  members: Member[]
}

export const REALMS: Realm[] = [
  { id: 'central',        index: 1, name_zh: '中央界域',   name_en: 'Central Realm',          color: '#16A34A', label_lnglat: [42, 26] },
  { id: 'eastern',        index: 2, name_zh: '東方界域',   name_en: 'Eastern Realm',          color: '#EAB308', label_lnglat: [95, 32] },
  { id: 'latin-america',  index: 3, name_zh: '拉美界域',   name_en: 'Latin American Realm',   color: '#DC2626', label_lnglat: [-58, -12],
    intro: '擁有獨立發明的原生文字（馬雅）與古老祭祀文明，儘管現代外觀由伊比利亞重塑，其文明底層極度古老。' },
  { id: 'western',        index: 4, name_zh: '西方界域',   name_en: 'Western Realm',          color: '#9333EA', label_lnglat: [12, 50],
    intro: '承襲希臘羅馬的火種，伴隨拉丁/西里爾字母與基督教會，從地中海向北歐與東歐荒野推進。' },
  { id: 'asia-pacific',   index: 5, name_zh: '亞太界域',   name_en: 'Asia-Pacific Realm',     color: '#2196F3', label_lnglat: [128, -8],
    intro: '位處東方與印度兩大母體邊緣，透過佛教、漢字與伊斯蘭季風貿易，逐步點亮信史。' },
  { id: 'southern',       index: 6, name_zh: '南方界域',   name_en: 'Southern Realm',         color: '#A0522D', label_lnglat: [22, 0],
    intro: '從古老的衣索比亞文字，一路隨跨撒哈拉貿易與大航海時代，向中南部無文字部落推進。' },
  { id: 'northern',       index: 7, name_zh: '北方界域',   name_en: 'Northern Realm',         color: '#7593B5', label_lnglat: [85, 62],
    intro: '游牧與森林的廣袤邊疆，文字與宗教（東正教/伊斯蘭教/藏傳佛教）多由外部勢力（羅斯人、阿拉伯人、漢人）自中世紀起強勢植入。' },
  { id: 'north-america',  index: 8, name_zh: '北美界域',   name_en: 'North American Realm',   color: '#2A9D8F', label_lnglat: [-100, 48],
    intro: '現代文明最強大的板塊，卻是全球最晚經歷「原生無文字部落被西歐近代文明徹底覆蓋」的最後邊疆。' },
]

export const SPHERES: CulturalSphere[] = [
  // ========== 中央界域 ==========
  {
    id: 'mesopotamian-levantine', name_zh: '兩河-黎凡特文化圈', name_en: 'Mesopotamian-Levantine', realm_id: 'central',
    members: [
      { iso_a3: 'IRQ', label: '伊拉克', order: 1, note: '蘇美/阿卡德發源地' },
      { iso_a3: 'SYR', label: '敘利亞', order: 2, note: '烏加里特' },
      { iso_a3: 'LBN', label: '黎巴嫩', order: 3, note: '腓尼基' },
      { iso_a3: 'PSE', label: '巴勒斯坦', order: 4, note: '迦南' },
      { iso_a3: 'ISR', label: '以色列', order: 5, note: '古猶太教核心' },
      { iso_a3: 'JOR', label: '約旦', order: 6, note: '納巴泰' },
    ],
  },
  {
    id: 'egyptian', name_zh: '埃及文化圈', name_en: 'Egyptian', realm_id: 'central',
    members: [
      { iso_a3: 'EGY', label: '埃及', order: 1, note: '聖書體發源地' },
      { iso_a3: 'SDN', label: '蘇丹', order: 2, note: '中北部與東部，庫施王國' },
      { iso_a3: 'LBY', label: '利比亞', order: 3, note: '昔蘭尼加地區' },
    ],
  },
  {
    id: 'aegean-asia-minor', name_zh: '愛琴-小亞細亞文化圈', name_en: 'Aegean-Asia Minor', realm_id: 'central',
    members: [
      { iso_a3: 'GRC', label: '希臘', order: 1, note: '米諾斯/邁錫尼文明' },
      { iso_a3: 'CYP', label: '賽普勒斯', order: 2 },
      { iso_a3: 'TUR', label: '土耳其', order: 3, note: '赫梯帝國至拜占庭' },
    ],
  },
  {
    id: 'persian', name_zh: '波斯文化圈', name_en: 'Persian', realm_id: 'central',
    members: [
      { iso_a3: 'IRN', label: '伊朗', order: 1, note: '埃蘭文明至波斯帝國' },
      { iso_a3: 'AFG', label: '阿富汗', order: 2, note: '西部與中部' },
      { iso_a3: 'TJK', label: '塔吉克', order: 3 },
    ],
  },
  {
    id: 'caucasus', name_zh: '高加索文化圈', name_en: 'Caucasus', realm_id: 'central',
    members: [
      { iso_a3: 'ARM', label: '亞美尼亞', order: 1, note: '烏拉爾圖，首個基督教國家' },
      { iso_a3: 'GEO', label: '喬治亞', order: 2 },
      { iso_a3: 'AZE', label: '亞塞拜然', order: 3 },
      { iso_a3: 'RUS', admin1: 'North Caucasus', label: '俄羅斯（北高加索地區）', order: 4 },
    ],
  },
  {
    id: 'arabian', name_zh: '阿拉伯文化圈', name_en: 'Arabian', realm_id: 'central',
    members: [
      { iso_a3: 'YEM', label: '葉門', order: 1, note: '示巴王國，古南阿拉伯文' },
      { iso_a3: 'SAU', label: '沙烏地阿拉伯', order: 2, note: '伊斯蘭教發源地' },
      { iso_a3: 'OMN', label: '阿曼', order: 3 },
      { iso_a3: 'BHR', label: '巴林', order: 4 },
      { iso_a3: 'QAT', label: '卡達', order: 5 },
      { iso_a3: 'ARE', label: '阿聯酋', order: 6 },
      { iso_a3: 'KWT', label: '科威特', order: 7 },
    ],
  },

  // ========== 東方界域 ==========
  {
    id: 'indian', name_zh: '印度文化圈', name_en: 'Indian', realm_id: 'eastern',
    members: [
      { iso_a3: 'PAK', label: '巴基斯坦', order: 1, note: '印度河文明' },
      { iso_a3: 'IND', label: '印度', order: 2, note: '吠陀宗教核心' },
      { iso_a3: 'NPL', label: '尼泊爾', order: 3, note: '佛教發源地' },
      { iso_a3: 'LKA', label: '斯里蘭卡', order: 4, note: '早期南傳佛教' },
      { iso_a3: 'AFG', admin1: 'South-East', label: '阿富汗（南部與東部）', order: 5, note: '犍陀羅' },
      { iso_a3: 'BGD', label: '孟加拉', order: 6 },
      { iso_a3: 'MDV', label: '馬爾地夫', order: 7 },
    ],
  },
  {
    id: 'han', name_zh: '漢地文化圈', name_en: 'Han', realm_id: 'eastern',
    members: [
      { iso_a3: 'CHN', admin1: 'Inner-18', label: '中國（關內 18 省）', order: 1, note: '甲骨文與華夏核心' },
      { iso_a3: 'TWN', label: '台灣', order: 2, is_extension: true, note: '17 世紀進入漢文信史' },
    ],
  },
  {
    id: 'tibetan', name_zh: '圖博文化圈', name_en: 'Tibetan', realm_id: 'eastern',
    members: [
      { iso_a3: 'CHN', admin1: 'Tibet', label: '中國（西藏自治區）', order: 1, note: '吐蕃帝國與藏文創制' },
      { iso_a3: 'CHN', admin1: 'Tibetan-4-Provinces', label: '中國（四省藏區）', order: 2 },
      { iso_a3: 'BTN', label: '不丹', order: 3 },
    ],
  },

  // ========== 拉美界域 ==========
  {
    id: 'mesoamerican', name_zh: '中美洲-墨西哥文化圈', name_en: 'Mesoamerican-Mexican', realm_id: 'latin-america',
    members: [
      { iso_a3: 'MEX', label: '墨西哥', order: 1, note: '奧爾梅克/阿茲特克' },
      { iso_a3: 'GTM', label: '瓜地馬拉', order: 2, note: '馬雅核心' },
      { iso_a3: 'BLZ', label: '貝里斯', order: 3 },
      { iso_a3: 'HND', label: '宏都拉斯', order: 4 },
      { iso_a3: 'SLV', label: '薩爾瓦多', order: 5 },
      { iso_a3: 'NIC', label: '尼加拉瓜', order: 6 },
      { iso_a3: 'CRI', label: '哥斯大黎加', order: 7 },
      { iso_a3: 'PAN', label: '巴拿馬', order: 8 },
      { iso_a3: 'USA', admin1: 'Southwest', label: '美國（西南部）', order: 9, is_extension: true },
    ],
  },
  {
    id: 'andean', name_zh: '安地斯文化圈', name_en: 'Andean', realm_id: 'latin-america',
    members: [
      { iso_a3: 'PER', label: '秘魯', order: 1, note: '卡拉爾/印加帝國' },
      { iso_a3: 'BOL', label: '玻利維亞', order: 2 },
      { iso_a3: 'ECU', label: '厄瓜多', order: 3 },
      { iso_a3: 'COL', label: '哥倫比亞', order: 4 },
    ],
  },
  {
    id: 'caribbean', name_zh: '加勒比文化圈', name_en: 'Caribbean', realm_id: 'latin-america',
    members: [
      { iso_a3: 'CUB', label: '古巴', order: 1, note: '哥倫布首批接觸區' },
      { iso_a3: 'DOM', label: '多明尼加', order: 2 },
      { iso_a3: 'HTI', label: '海地', order: 3 },
      { iso_a3: 'JAM', label: '牙買加', order: 4 },
      { iso_a3: 'BHS', label: '巴哈馬', order: 5 },
      { iso_a3: 'VEN', label: '委內瑞拉', order: 6 },
      { iso_a3: 'GUY', label: '蓋亞那', order: 7 },
      { iso_a3: 'SUR', label: '蘇利南', order: 8 },
      { iso_a3: 'GUF', label: '法屬圭亞那', order: 9 },
      { iso_a3: 'ATG', label: '安地卡', order: 10, is_extension: true },
      { iso_a3: 'BRB', label: '巴貝多', order: 11, is_extension: true },
      { iso_a3: 'DMA', label: '多米尼克', order: 12, is_extension: true },
      { iso_a3: 'GRD', label: '格瑞那達', order: 13, is_extension: true },
      { iso_a3: 'KNA', label: '聖克里斯多福及尼維斯', order: 14, is_extension: true },
      { iso_a3: 'LCA', label: '聖露西亞', order: 15, is_extension: true },
      { iso_a3: 'VCT', label: '聖文森', order: 16, is_extension: true },
      { iso_a3: 'TTO', label: '千里達及托巴哥', order: 17, is_extension: true },
    ],
  },
  {
    id: 'southern-cone', name_zh: '南錐文化圈', name_en: 'Southern Cone', realm_id: 'latin-america',
    members: [
      { iso_a3: 'CHL', label: '智利', order: 1 },
      { iso_a3: 'ARG', label: '阿根廷', order: 2 },
      { iso_a3: 'PRY', label: '巴拉圭', order: 3 },
      { iso_a3: 'URY', label: '烏拉圭', order: 4, note: '近代集約殖民化' },
    ],
  },
  {
    id: 'amazonian-brazilian', name_zh: '亞馬遜-巴西文化圈', name_en: 'Amazonian-Brazilian', realm_id: 'latin-america',
    members: [
      { iso_a3: 'BRA', label: '巴西', order: 1, note: '海岸線早於內陸雨林開發' },
    ],
  },

  // ========== 西方界域 ==========
  {
    id: 'latin-cultural', name_zh: '拉丁文化圈', name_en: 'Latin', realm_id: 'western',
    members: [
      { iso_a3: 'ITA', label: '義大利', order: 1, note: '羅馬帝國核心' },
      { iso_a3: 'VAT', label: '梵蒂岡', order: 2 },
      { iso_a3: 'SMR', label: '聖馬利諾', order: 3 },
      { iso_a3: 'ESP', label: '西班牙', order: 4 },
      { iso_a3: 'PRT', label: '葡萄牙', order: 5 },
      { iso_a3: 'MLT', label: '馬爾他', order: 6 },
      { iso_a3: 'MCO', label: '摩納哥', order: 7 },
      { iso_a3: 'AND', label: '安道爾', order: 8 },
    ],
  },
  {
    id: 'balkan', name_zh: '巴爾幹文化圈', name_en: 'Balkan', realm_id: 'western',
    members: [
      { iso_a3: 'MKD', label: '北馬其頓', order: 1 },
      { iso_a3: 'BGR', label: '保加利亞', order: 2, note: '西里爾字母發源地' },
      { iso_a3: 'SRB', label: '塞爾維亞', order: 3 },
      { iso_a3: 'ROU', label: '羅馬尼亞', order: 4 },
      { iso_a3: 'ALB', label: '阿爾巴尼亞', order: 5 },
      { iso_a3: 'BIH', label: '波士尼亞', order: 6, is_extension: true },
      { iso_a3: 'HRV', label: '克羅埃西亞', order: 7, is_extension: true },
      { iso_a3: 'MNE', label: '蒙特內哥羅', order: 8, is_extension: true },
      { iso_a3: 'SVN', label: '斯洛維尼亞', order: 9, is_extension: true },
      { iso_a3: 'KOS', label: '科索沃', order: 10, is_extension: true },
      { iso_a3: 'MDA', label: '摩爾多瓦', order: 11 },
    ],
  },
  {
    id: 'gallic-french', name_zh: '高盧-法蘭西文化圈', name_en: 'Gallic-French', realm_id: 'western',
    members: [
      { iso_a3: 'FRA', label: '法國', order: 1, note: '歐洲本土，羅馬化高盧' },
    ],
  },
  {
    id: 'british-celtic', name_zh: '不列顛-凱爾特文化圈', name_en: 'British-Celtic', realm_id: 'western',
    members: [
      { iso_a3: 'GBR', label: '英國', order: 1, note: '羅馬不列顛' },
      { iso_a3: 'IRL', label: '愛爾蘭', order: 2, note: '凱爾特基督教' },
      { iso_a3: 'FLK', label: '英國（福克蘭群島）', order: 3 },
    ],
  },
  {
    id: 'central-european', name_zh: '中歐文化圈', name_en: 'Central European', realm_id: 'western',
    members: [
      { iso_a3: 'DEU', label: '德國', order: 1, note: '神聖羅馬帝國' },
      { iso_a3: 'AUT', label: '奧地利', order: 2 },
      { iso_a3: 'CHE', label: '瑞士', order: 3 },
      { iso_a3: 'CZE', label: '捷克', order: 4 },
      { iso_a3: 'HUN', label: '匈牙利', order: 5 },
      { iso_a3: 'SVK', label: '斯洛伐克', order: 6 },
      { iso_a3: 'POL', admin1: 'East-Prussia', label: '波蘭（東普魯士地區）', order: 7, is_extension: true },
      { iso_a3: 'RUS', admin1: 'Kaliningrad', label: '俄國（加里寧格勒州）', order: 8, is_extension: true },
      { iso_a3: 'LIE', label: '列支敦斯登', order: 9 },
    ],
  },
  {
    id: 'low-countries', name_zh: '低地文化圈', name_en: 'Low Countries', realm_id: 'western',
    members: [
      { iso_a3: 'BEL', label: '比利時', order: 1, note: '法蘭克核心' },
      { iso_a3: 'NLD', label: '荷蘭', order: 2 },
      { iso_a3: 'LUX', label: '盧森堡', order: 3 },
    ],
  },
  {
    id: 'lublin', name_zh: '盧布林文化圈', name_en: 'Lublin', realm_id: 'western',
    members: [
      { iso_a3: 'POL', label: '波蘭', order: 1, note: '10 世紀天主教化' },
      { iso_a3: 'UKR', admin1: 'West', label: '烏克蘭（西部）', order: 2 },
      { iso_a3: 'LTU', label: '立陶宛', order: 3 },
      { iso_a3: 'LVA', admin1: 'Latgale', label: '拉脫維亞（拉特加爾地區）', order: 4 },
    ],
  },
  {
    id: 'nordic-livonian', name_zh: '北歐-立窩尼亞文化圈', name_en: 'Nordic-Livonian', realm_id: 'western',
    members: [
      { iso_a3: 'DNK', label: '丹麥', order: 1, note: '最早出現盧恩字母' },
      { iso_a3: 'SWE', label: '瑞典', order: 2 },
      { iso_a3: 'NOR', label: '挪威', order: 3 },
      { iso_a3: 'ISL', label: '冰島', order: 4 },
      { iso_a3: 'FIN', label: '芬蘭', order: 5 },
      { iso_a3: 'EST', label: '愛沙尼亞', order: 6 },
      { iso_a3: 'LVA', admin1: 'West-Central', label: '拉脫維亞（西部與中部）', order: 7 },
    ],
  },

  // ========== 亞太界域 ==========
  {
    id: 'mekong', name_zh: '眉公文化圈', name_en: 'Mekong', realm_id: 'asia-pacific',
    members: [
      { iso_a3: 'KHM', label: '柬埔寨', order: 1, note: '扶南/高棉帝國，早期印度化' },
      { iso_a3: 'VNM', label: '越南', order: 2, note: '交趾，早期漢化' },
      { iso_a3: 'MMR', label: '緬甸', order: 3, note: '驃國/蒲甘' },
      { iso_a3: 'THA', label: '泰國', order: 4, note: '素可泰' },
      { iso_a3: 'LAO', label: '寮國', order: 5 },
    ],
  },
  {
    id: 'kuroshio', name_zh: '黑潮文化圈', name_en: 'Kuroshio', realm_id: 'asia-pacific',
    members: [
      { iso_a3: 'PRK', label: '北韓', order: 1, note: '漢四郡遺址' },
      { iso_a3: 'KOR', label: '韓國', order: 2, note: '三韓與百濟' },
      { iso_a3: 'JPN', label: '日本', order: 3, note: '大和朝廷，漢字傳入' },
      { iso_a3: 'JPN', admin1: 'Ryukyu', label: '日本（琉球）', order: 4 },
      { iso_a3: 'TWN', label: '台灣', order: 5, is_extension: true, note: '南島原鄉，但最晚進入文字信史' },
    ],
  },
  {
    id: 'banua', name_zh: '班努亞文化圈', name_en: 'Banua', realm_id: 'asia-pacific',
    members: [
      { iso_a3: 'IDN', label: '印尼', order: 1, note: '三佛齊/室利佛逝，印度化與伊斯蘭化起點' },
      { iso_a3: 'MYS', label: '馬來西亞', order: 2 },
      { iso_a3: 'BRN', label: '汶萊', order: 3 },
      { iso_a3: 'SGP', label: '新加坡', order: 4 },
      { iso_a3: 'PHL', label: '菲律賓', order: 5 },
      { iso_a3: 'TLS', label: '東帝汶', order: 6 },
    ],
  },
  {
    id: 'pacific', name_zh: '太平洋文化圈', name_en: 'Pacific', realm_id: 'asia-pacific',
    members: [
      { iso_a3: 'VUT', label: '萬那杜', order: 1 },
      { iso_a3: 'FJI', label: '斐濟', order: 2 },
      { iso_a3: 'WSM', label: '薩摩亞', order: 3 },
      { iso_a3: 'TON', label: '東加', order: 4 },
      { iso_a3: 'PLW', label: '帛琉', order: 5, is_extension: true },
      { iso_a3: 'FSM', label: '密克羅尼西亞', order: 6, is_extension: true },
      { iso_a3: 'MHL', label: '馬紹爾群島', order: 7, is_extension: true },
      { iso_a3: 'KIR', label: '吉里巴斯', order: 8, is_extension: true },
      { iso_a3: 'NRU', label: '諾魯', order: 9, is_extension: true },
      { iso_a3: 'TUV', label: '吐瓦魯', order: 10, is_extension: true },
      { iso_a3: 'PNG', label: '巴布亞紐幾內亞', order: 11, is_extension: true },
      { iso_a3: 'SLB', label: '索羅門群島', order: 12, is_extension: true },
      { iso_a3: 'USA', admin1: 'Hawaii', label: '美國（夏威夷州）', order: 13, note: '最晚期南島拓殖' },
    ],
  },
  {
    id: 'australasian', name_zh: '紐奧文化圈', name_en: 'Australasian', realm_id: 'asia-pacific',
    members: [
      { iso_a3: 'AUS', label: '澳洲', order: 1 },
      { iso_a3: 'NZL', label: '紐西蘭', order: 2, note: '毛利人抵達晚於原住民，白人殖民信史更晚' },
    ],
  },

  // ========== 南方界域 ==========
  {
    id: 'ethiopian', name_zh: '衣索比亞文化圈', name_en: 'Ethiopian', realm_id: 'southern',
    members: [
      { iso_a3: 'ETH', label: '衣索比亞', order: 1, note: '中央高地與西北部，阿克蘇姆帝國與吉茲字母' },
      { iso_a3: 'ERI', label: '厄利垂亞', order: 2 },
    ],
  },
  {
    id: 'west-african-sahel', name_zh: '西非-薩赫爾文化圈', name_en: 'West African-Sahel', realm_id: 'southern',
    members: [
      { iso_a3: 'MLI', label: '馬利', order: 1, note: '南部，廷巴克圖學術中心' },
      { iso_a3: 'SEN', label: '塞內加爾', order: 2 },
      { iso_a3: 'NER', label: '尼日（南部）', order: 3 },
      { iso_a3: 'BFA', label: '布吉納法索', order: 4, is_extension: true },
      { iso_a3: 'GIN', label: '幾內亞', order: 5, is_extension: true },
      { iso_a3: 'GMB', label: '甘比亞', order: 6, is_extension: true },
      { iso_a3: 'GNB', label: '幾內亞比索', order: 7, is_extension: true },
      { iso_a3: 'MRT', label: '茅利塔尼亞', order: 8, is_extension: true },
      { iso_a3: 'TCD', label: '查德', order: 9, is_extension: true },
      { iso_a3: 'CPV', label: '維德角', order: 10 },
    ],
  },
  {
    id: 'east-african-swahili', name_zh: '東非-斯瓦希里文化圈', name_en: 'East African-Swahili', realm_id: 'southern',
    members: [
      { iso_a3: 'SOM', label: '索馬利亞', order: 1 },
      { iso_a3: 'KEN', label: '肯亞', order: 2 },
      { iso_a3: 'TZA', label: '坦尚尼亞', order: 3, note: '斯瓦希里城邦與阿拉伯貿易' },
      { iso_a3: 'MDG', label: '馬達加斯加', order: 4 },
      { iso_a3: 'UGA', label: '烏干達', order: 5, is_extension: true },
      { iso_a3: 'RWA', label: '盧安達', order: 6, is_extension: true },
      { iso_a3: 'BDI', label: '蒲隆地', order: 7, is_extension: true },
      { iso_a3: 'DJI', label: '吉布地', order: 8, is_extension: true },
      { iso_a3: 'COM', label: '葛摩', order: 9, is_extension: true },
      { iso_a3: 'SYC', label: '塞席爾', order: 10, is_extension: true },
      { iso_a3: 'SSD', label: '南蘇丹', order: 11 },
    ],
  },
  {
    id: 'gulf-of-guinea', name_zh: '幾內亞灣文化圈', name_en: 'Gulf of Guinea', realm_id: 'southern',
    members: [
      { iso_a3: 'NGA', label: '奈及利亞', order: 1, note: '南部，貝南帝國' },
      { iso_a3: 'GHA', label: '迦納（南部）', order: 2 },
      { iso_a3: 'BEN', label: '貝南', order: 3, is_extension: true },
      { iso_a3: 'TGO', label: '多哥', order: 4, is_extension: true },
      { iso_a3: 'CIV', label: '象牙海岸', order: 5, is_extension: true },
      { iso_a3: 'SLE', label: '獅子山', order: 6, is_extension: true },
      { iso_a3: 'LBR', label: '賴比瑞亞', order: 7 },
    ],
  },
  {
    id: 'central-african-congolese', name_zh: '中非-剛果文化圈', name_en: 'Central African-Congolese', realm_id: 'southern',
    members: [
      { iso_a3: 'COD', label: '剛果民主共和國', order: 1, note: '剛果王國，15 世紀天主教化' },
      { iso_a3: 'COG', label: '剛果共和國', order: 2 },
      { iso_a3: 'CMR', label: '喀麥隆', order: 3 },
      { iso_a3: 'GAB', label: '加彭', order: 4, is_extension: true },
      { iso_a3: 'GNQ', label: '赤道幾內亞', order: 5, is_extension: true },
      { iso_a3: 'STP', label: '聖多美普林西比', order: 6, is_extension: true },
      { iso_a3: 'CAF', label: '中非共和國', order: 7 },
    ],
  },
  {
    id: 'southern-african-bantu', name_zh: '南部非洲-班圖文化圈', name_en: 'Southern African-Bantu', realm_id: 'southern',
    members: [
      { iso_a3: 'ZWE', label: '辛巴威', order: 1, note: '大辛巴威遺址' },
      { iso_a3: 'MOZ', label: '莫三比克', order: 2 },
      { iso_a3: 'ZAF', label: '南非', order: 3 },
      { iso_a3: 'AGO', label: '安哥拉', order: 4 },
      { iso_a3: 'BWA', label: '波札那', order: 5, is_extension: true },
      { iso_a3: 'ZMB', label: '尚比亞', order: 6, is_extension: true },
      { iso_a3: 'MWI', label: '馬拉威', order: 7, is_extension: true },
      { iso_a3: 'LSO', label: '賴索托', order: 8, is_extension: true },
      { iso_a3: 'SWZ', label: '史瓦帝尼', order: 9, is_extension: true },
      { iso_a3: 'NAM', label: '納米比亞', order: 10 },
    ],
  },

  // ========== 北方界域 ==========
  {
    id: 'turanian-turkic', name_zh: '圖蘭-突厥文化圈', name_en: 'Turanian-Turkic', realm_id: 'northern',
    members: [
      { iso_a3: 'UZB', label: '烏茲別克', order: 1, note: '粟特/撒馬爾罕，絲路核心' },
      { iso_a3: 'AFG', admin1: 'North', label: '阿富汗（北部）', order: 2 },
      { iso_a3: 'TKM', label: '土庫曼', order: 3 },
      { iso_a3: 'CHN', admin1: 'Xinjiang', label: '中國（新疆維吾爾自治區）', order: 4 },
      { iso_a3: 'KGZ', label: '吉爾吉斯', order: 5 },
      { iso_a3: 'KAZ', label: '哈薩克', order: 6, note: '游牧腹地' },
    ],
  },
  {
    id: 'russian-tatar', name_zh: '羅斯-韃靼文化圈', name_en: 'Russian-Tatar', realm_id: 'northern',
    members: [
      { iso_a3: 'UKR', admin1: 'East', label: '烏克蘭（東部）', order: 1, note: '基輔羅斯發源地' },
      { iso_a3: 'UKR', admin1: 'West', label: '烏克蘭（西部）', order: 2, is_extension: true },
      { iso_a3: 'BLR', label: '白俄羅斯', order: 3 },
      { iso_a3: 'RUS', admin1: 'European', label: '俄羅斯（歐俄部分）', order: 4, note: '莫斯科公國崛起' },
    ],
  },
  {
    id: 'mongolic-manchurian', name_zh: '蒙古-滿洲文化圈', name_en: 'Mongolic-Manchurian', realm_id: 'northern',
    members: [
      { iso_a3: 'MNG', label: '蒙古', order: 1, note: '回鶻式蒙古文創制' },
      { iso_a3: 'CHN', admin1: 'Inner-Mongolia-Manchuria', label: '中國（內蒙古自治區與東北）', order: 2, note: '滿文創制' },
      { iso_a3: 'RUS', admin1: 'Buryatia', label: '俄羅斯（布里亞特共和國）', order: 3 },
      { iso_a3: 'RUS', admin1: 'Tuva', label: '俄羅斯（圖瓦共和國）', order: 4 },
      { iso_a3: 'RUS', admin1: 'Kalmykia', label: '俄羅斯（卡爾梅克共和國）', order: 5 },
      { iso_a3: 'RUS', admin1: 'Far-East-South', label: '俄羅斯（遠東南部）', order: 6, is_extension: true },
    ],
  },
  {
    id: 'siberian', name_zh: '西伯利亞文化圈', name_en: 'Siberian', realm_id: 'northern',
    members: [
      { iso_a3: 'RUS', admin1: 'Siberia-Arctic', label: '俄羅斯極地與北亞森林區', order: 1, note: '16 世紀後俄羅斯哥薩克東擴才全面進入信史' },
    ],
  },

  // ========== 北美界域 ==========
  {
    id: 'anglo-american', name_zh: '盎格魯美洲文化圈', name_en: 'Anglo-American', realm_id: 'north-america',
    members: [
      { iso_a3: 'USA', label: '美國（本土 48 州）', order: 1, note: '詹姆斯鎮/五月花號' },
      { iso_a3: 'CAN', admin1: 'South', label: '加拿大（南部定居區）', order: 2 },
    ],
  },
  {
    id: 'franco-american', name_zh: '法蘭西美洲文化圈', name_en: 'Franco-American', realm_id: 'north-america',
    members: [
      { iso_a3: 'CAN', admin1: 'Quebec-Acadia', label: '加拿大（魁北克與阿卡迪亞）', order: 1, note: '法語族裔大本營，新法蘭西殖民核心' },
      { iso_a3: 'USA', admin1: 'New-France', label: '美國（新法蘭西／路易斯安那）', order: 2, is_extension: true },
    ],
  },
  {
    id: 'arctic', name_zh: '北極文化圈', name_en: 'Arctic', realm_id: 'north-america',
    members: [
      { iso_a3: 'GRL', label: '丹麥（格陵蘭島）', order: 1, note: '維京人短暫接觸，近代重新殖民' },
      { iso_a3: 'CAN', admin1: 'North', label: '加拿大（北方領地）', order: 2 },
      { iso_a3: 'USA', admin1: 'Alaska', label: '美國（阿拉斯加州）', order: 3 },
      { iso_a3: 'RUS', admin1: 'Chukotka-Sakha', label: '俄羅斯（楚科奇/薩哈共和國北緣）', order: 4 },
    ],
  },
]

/**
 * 地圖上色用：每個 ISO_A3 國家對應的「主要」界域（country-level coloring）。
 * 多文化圈國家（中國/俄羅斯/美國/加拿大/法國/丹麥/阿富汗/烏克蘭）以面積或人口最大的文化圈為主。
 * 詳細多文化圈歸屬請看「資訊列表」視圖。
 */
export const COUNTRY_REALM: Record<string, RealmId> = {
  // 中央 (Green)
  IRQ: 'central', SYR: 'central', LBN: 'central', PSE: 'central', ISR: 'central', JOR: 'central',
  EGY: 'central', SDN: 'central', LBY: 'central',
  GRC: 'central', CYP: 'central', TUR: 'central',
  IRN: 'central', AFG: 'central', TJK: 'central',
  ARM: 'central', GEO: 'central', AZE: 'central',
  YEM: 'central', SAU: 'central', OMN: 'central', BHR: 'central', QAT: 'central', ARE: 'central', KWT: 'central',

  // 東方 (Yellow)
  PAK: 'eastern', IND: 'eastern', NPL: 'eastern', LKA: 'eastern', BGD: 'eastern', MDV: 'eastern',
  CHN: 'eastern',  // 漢地為主；西藏/青海→東方圖博、新疆/內蒙古/東北→北方，由 ADMIN1_SPHERE 細分
  BTN: 'eastern',
  // TWN: 'asia-pacific'（黑潮）— 在亞太區段定義

  // 拉美 (Red)
  MEX: 'latin-america', GTM: 'latin-america', BLZ: 'latin-america', HND: 'latin-america',
  SLV: 'latin-america', NIC: 'latin-america', CRI: 'latin-america', PAN: 'latin-america',
  PER: 'latin-america', BOL: 'latin-america', ECU: 'latin-america', COL: 'latin-america',
  CUB: 'latin-america', DOM: 'latin-america', HTI: 'latin-america', JAM: 'latin-america',
  BHS: 'latin-america', VEN: 'latin-america', GUY: 'latin-america', SUR: 'latin-america', GUF: 'latin-america',
  ATG: 'latin-america', BRB: 'latin-america', DMA: 'latin-america', GRD: 'latin-america',
  KNA: 'latin-america', LCA: 'latin-america', VCT: 'latin-america', TTO: 'latin-america',
  CHL: 'latin-america', ARG: 'latin-america', PRY: 'latin-america', URY: 'latin-america',
  BRA: 'latin-america',

  // 西方 (Purple)
  ITA: 'western', VAT: 'western', SMR: 'western', ESP: 'western', PRT: 'western',
  MLT: 'western', MCO: 'western', AND: 'western',
  MKD: 'western', BGR: 'western', SRB: 'western', ROU: 'western', ALB: 'western',
  BIH: 'western', HRV: 'western', MNE: 'western', SVN: 'western', KOS: 'western', MDA: 'western',
  FRA: 'western',
  GBR: 'western', IRL: 'western', FLK: 'western',
  DEU: 'western', AUT: 'western', CHE: 'western', CZE: 'western', HUN: 'western', SVK: 'western',
  POL: 'western', LIE: 'western',
  BEL: 'western', NLD: 'western', LUX: 'western',
  UKR: 'western',  // 烏克蘭以盧布林/西烏為主呈現（東烏在北方多文化圈列表）
  LTU: 'western', LVA: 'western',
  DNK: 'western', SWE: 'western', NOR: 'western', ISL: 'western', FIN: 'western', EST: 'western',
  // 馬格里布（文件未列為主，但圖示與西方羅馬-法殖民圈一致）
  TUN: 'western', DZA: 'western', MAR: 'western', ESH: 'western',

  // 亞太 (Blue)
  KHM: 'asia-pacific', VNM: 'asia-pacific', MMR: 'asia-pacific', THA: 'asia-pacific', LAO: 'asia-pacific',
  PRK: 'asia-pacific', KOR: 'asia-pacific', JPN: 'asia-pacific', TWN: 'asia-pacific',  // 台灣→黑潮文化圈
  IDN: 'asia-pacific', MYS: 'asia-pacific', BRN: 'asia-pacific', SGP: 'asia-pacific',
  PHL: 'asia-pacific', TLS: 'asia-pacific',
  VUT: 'asia-pacific', FJI: 'asia-pacific', WSM: 'asia-pacific', TON: 'asia-pacific',
  PLW: 'asia-pacific', FSM: 'asia-pacific', MHL: 'asia-pacific', KIR: 'asia-pacific',
  NRU: 'asia-pacific', TUV: 'asia-pacific', PNG: 'asia-pacific', SLB: 'asia-pacific',
  AUS: 'asia-pacific', NZL: 'asia-pacific',

  // 南方 (Brown)
  ETH: 'southern', ERI: 'southern',
  MLI: 'southern', SEN: 'southern', NER: 'southern', CPV: 'southern',
  BFA: 'southern', GIN: 'southern', GMB: 'southern', GNB: 'southern', MRT: 'southern', TCD: 'southern',
  SOM: 'southern', KEN: 'southern', TZA: 'southern', MDG: 'southern', SSD: 'southern',
  UGA: 'southern', RWA: 'southern', BDI: 'southern', DJI: 'southern', COM: 'southern', SYC: 'southern',
  NGA: 'southern', GHA: 'southern', LBR: 'southern',
  BEN: 'southern', TGO: 'southern', CIV: 'southern', SLE: 'southern',
  COD: 'southern', COG: 'southern', CMR: 'southern', CAF: 'southern',
  GAB: 'southern', GNQ: 'southern', STP: 'southern',
  ZWE: 'southern', MOZ: 'southern', ZAF: 'southern', AGO: 'southern', NAM: 'southern',
  BWA: 'southern', ZMB: 'southern', MWI: 'southern', LSO: 'southern', SWZ: 'southern',

  // 北方 (Slate Blue)
  UZB: 'northern', TKM: 'northern', KGZ: 'northern', KAZ: 'northern',
  BLR: 'northern', RUS: 'northern',
  MNG: 'northern',

  // 北美 (Teal) — USA/CAN 細分由 ADMIN1_SPHERE 處理（夏威夷→亞太、阿拉斯加/北加→北極、魁北克→西方法蘭西）
  USA: 'north-america', CAN: 'north-america', GRL: 'north-america',
}

/** 繁體中文國名對照（用於 tooltip，避免 NE 內建 NAME_ZH 是簡體+大陸用詞） */
export const COUNTRY_NAME_ZH: Record<string, string> = {
  IRQ: '伊拉克', SYR: '敘利亞', LBN: '黎巴嫩', PSE: '巴勒斯坦', ISR: '以色列', JOR: '約旦',
  EGY: '埃及', SDN: '蘇丹', LBY: '利比亞',
  GRC: '希臘', CYP: '賽普勒斯', TUR: '土耳其',
  IRN: '伊朗', AFG: '阿富汗', TJK: '塔吉克',
  ARM: '亞美尼亞', GEO: '喬治亞', AZE: '亞塞拜然',
  YEM: '葉門', SAU: '沙烏地阿拉伯', OMN: '阿曼', BHR: '巴林', QAT: '卡達', ARE: '阿拉伯聯合大公國', KWT: '科威特',
  PAK: '巴基斯坦', IND: '印度', NPL: '尼泊爾', LKA: '斯里蘭卡', BGD: '孟加拉', MDV: '馬爾地夫',
  CHN: '中國', TWN: '台灣', BTN: '不丹',
  MEX: '墨西哥', GTM: '瓜地馬拉', BLZ: '貝里斯', HND: '宏都拉斯', SLV: '薩爾瓦多',
  NIC: '尼加拉瓜', CRI: '哥斯大黎加', PAN: '巴拿馬',
  PER: '秘魯', BOL: '玻利維亞', ECU: '厄瓜多', COL: '哥倫比亞',
  CUB: '古巴', DOM: '多明尼加', HTI: '海地', JAM: '牙買加', BHS: '巴哈馬',
  VEN: '委內瑞拉', GUY: '蓋亞那', SUR: '蘇利南', GUF: '法屬圭亞那',
  ATG: '安地卡及巴布達', BRB: '巴貝多', DMA: '多米尼克', GRD: '格瑞那達',
  KNA: '聖克里斯多福及尼維斯', LCA: '聖露西亞', VCT: '聖文森及格瑞那丁', TTO: '千里達及托巴哥',
  CHL: '智利', ARG: '阿根廷', PRY: '巴拉圭', URY: '烏拉圭', BRA: '巴西',
  ITA: '義大利', VAT: '梵蒂岡', SMR: '聖馬利諾', ESP: '西班牙', PRT: '葡萄牙',
  MLT: '馬爾他', MCO: '摩納哥', AND: '安道爾',
  MKD: '北馬其頓', BGR: '保加利亞', SRB: '塞爾維亞', ROU: '羅馬尼亞', ALB: '阿爾巴尼亞',
  BIH: '波士尼亞與赫塞哥維納', HRV: '克羅埃西亞', MNE: '蒙特內哥羅', SVN: '斯洛維尼亞', KOS: '科索沃', MDA: '摩爾多瓦',
  FRA: '法國',
  GBR: '英國', IRL: '愛爾蘭', FLK: '福克蘭群島',
  DEU: '德國', AUT: '奧地利', CHE: '瑞士', CZE: '捷克', HUN: '匈牙利', SVK: '斯洛伐克', POL: '波蘭', LIE: '列支敦斯登',
  BEL: '比利時', NLD: '荷蘭', LUX: '盧森堡',
  UKR: '烏克蘭', LTU: '立陶宛', LVA: '拉脫維亞',
  DNK: '丹麥', SWE: '瑞典', NOR: '挪威', ISL: '冰島', FIN: '芬蘭', EST: '愛沙尼亞',
  TUN: '突尼西亞', DZA: '阿爾及利亞', MAR: '摩洛哥', ESH: '西撒哈拉',
  KHM: '柬埔寨', VNM: '越南', MMR: '緬甸', THA: '泰國', LAO: '寮國',
  PRK: '北韓', KOR: '韓國', JPN: '日本',
  IDN: '印尼', MYS: '馬來西亞', BRN: '汶萊', SGP: '新加坡', PHL: '菲律賓', TLS: '東帝汶',
  VUT: '萬那杜', FJI: '斐濟', WSM: '薩摩亞', TON: '東加',
  PLW: '帛琉', FSM: '密克羅尼西亞聯邦', MHL: '馬紹爾群島', KIR: '吉里巴斯',
  NRU: '諾魯', TUV: '吐瓦魯', PNG: '巴布亞紐幾內亞', SLB: '索羅門群島',
  AUS: '澳洲', NZL: '紐西蘭',
  ETH: '衣索比亞', ERI: '厄利垂亞',
  MLI: '馬利', SEN: '塞內加爾', NER: '尼日', CPV: '維德角',
  BFA: '布吉納法索', GIN: '幾內亞', GMB: '甘比亞', GNB: '幾內亞比索', MRT: '茅利塔尼亞', TCD: '查德',
  SOM: '索馬利亞', KEN: '肯亞', TZA: '坦尚尼亞', MDG: '馬達加斯加', SSD: '南蘇丹',
  UGA: '烏干達', RWA: '盧安達', BDI: '蒲隆地', DJI: '吉布地', COM: '葛摩', SYC: '塞席爾',
  NGA: '奈及利亞', GHA: '迦納', LBR: '賴比瑞亞',
  BEN: '貝南', TGO: '多哥', CIV: '象牙海岸', SLE: '獅子山',
  COD: '剛果民主共和國', COG: '剛果共和國', CMR: '喀麥隆', CAF: '中非共和國',
  GAB: '加彭', GNQ: '赤道幾內亞', STP: '聖多美普林西比',
  ZWE: '辛巴威', MOZ: '莫三比克', ZAF: '南非', AGO: '安哥拉', NAM: '納米比亞',
  BWA: '波札那', ZMB: '尚比亞', MWI: '馬拉威', LSO: '賴索托', SWZ: '史瓦帝尼',
  UZB: '烏茲別克', TKM: '土庫曼', KGZ: '吉爾吉斯', KAZ: '哈薩克',
  BLR: '白俄羅斯', RUS: '俄羅斯', MNG: '蒙古',
  USA: '美國', CAN: '加拿大', GRL: '格陵蘭',
}

/** 採用 admin_1 子國家行政區細分上色的國家
 *  CHN/RUS/USA/CAN 用 NE 50m admin_1（檔案：ne_50m_admin_1_subset.geojson）
 *  LBY/AFG/UKR 用 NE 10m admin_1（檔案：ne_10m_admin_1_extra.geojson）
 */
export const COUNTRIES_USING_ADMIN1 = new Set<string>([
  'CHN', 'RUS', 'USA', 'CAN',                 // NE 50m subset
  'LBY', 'AFG', 'UKR', 'SDN', 'ETH', 'NGA', 'GHA',  // NE 10m extra subset
])

/** iso_3166_2 → sphere id（次國家行政區歸屬）。文件未指定的省份依預設： */
export const ADMIN1_SPHERE: Record<string, string> = {
  // ---------- 中國 (CHN) ----------
  // 圖博文化圈（東方界域）
  'CN-XZ': 'tibetan',  // 西藏自治區
  'CN-QH': 'tibetan',  // 青海（藏族高原）
  // 圖蘭-突厥文化圈（北方界域）
  'CN-XJ': 'turanian-turkic',  // 新疆維吾爾自治區
  // 蒙古-滿洲文化圈（北方界域）
  'CN-NM': 'mongolic-manchurian',  // 內蒙古自治區
  'CN-HL': 'mongolic-manchurian',  // 黑龍江
  'CN-JL': 'mongolic-manchurian',  // 吉林
  'CN-LN': 'mongolic-manchurian',  // 遼寧
  // 漢地文化圈（東方界域）— 其餘 24 省 / 直轄市 / 自治區
  'CN-GS': 'han', 'CN-GX': 'han', 'CN-GZ': 'han', 'CN-CQ': 'han', 'CN-BJ': 'han',
  'CN-FJ': 'han', 'CN-AH': 'han', 'CN-GD': 'han', 'CN-HI': 'han', 'CN-NX': 'han',
  'CN-SN': 'han', 'CN-SX': 'han', 'CN-HB': 'han', 'CN-HN': 'han', 'CN-SC': 'han',
  'CN-YN': 'han', 'CN-HE': 'han', 'CN-HA': 'han', 'CN-SD': 'han', 'CN-TJ': 'han',
  'CN-JX': 'han', 'CN-JS': 'han', 'CN-SH': 'han', 'CN-ZJ': 'han',

  // ---------- 俄羅斯 (RUS) ----------
  // 高加索文化圈（中央界域）
  'RU-AD': 'caucasus', 'RU-KC': 'caucasus', 'RU-IN': 'caucasus', 'RU-KB': 'caucasus',
  'RU-SE': 'caucasus', 'RU-CE': 'caucasus', 'RU-DA': 'caucasus',
  'RU-STA': 'caucasus', 'RU-KDA': 'caucasus',
  // 中歐文化圈（西方界域）
  'RU-KGD': 'central-european',  // 加里寧格勒
  // 蒙古-滿洲文化圈（北方界域）
  'RU-BU': 'mongolic-manchurian', 'RU-TY': 'mongolic-manchurian', 'RU-KL': 'mongolic-manchurian',
  'RU-AMU': 'mongolic-manchurian', 'RU-ZAB': 'mongolic-manchurian', 'RU-PRI': 'mongolic-manchurian',
  'RU-YEV': 'mongolic-manchurian', 'RU-KHA': 'mongolic-manchurian',
  'RU-MAG': 'mongolic-manchurian', 'RU-SAK': 'mongolic-manchurian',
  // 北極文化圈（北美界域）
  'RU-CHU': 'arctic',  // 楚科奇
  'RU-SA': 'arctic',   // 薩哈/雅庫特
  // 羅斯-韃靼文化圈（北方界域）— 歐俄部分
  'RU-MUR': 'russian-tatar', 'RU-NGR': 'russian-tatar', 'RU-PSK': 'russian-tatar',
  'RU-LEN': 'russian-tatar', 'RU-SPE': 'russian-tatar', 'RU-BRY': 'russian-tatar',
  'RU-SMO': 'russian-tatar', 'RU-KR': 'russian-tatar', 'RU-ARK': 'russian-tatar',
  'RU-IVA': 'russian-tatar', 'RU-VLG': 'russian-tatar', 'RU-KOS': 'russian-tatar',
  'RU-NIZ': 'russian-tatar', 'RU-TVE': 'russian-tatar', 'RU-YAR': 'russian-tatar',
  'RU-KLU': 'russian-tatar', 'RU-KRS': 'russian-tatar', 'RU-LIP': 'russian-tatar',
  'RU-MOW': 'russian-tatar', 'RU-MOS': 'russian-tatar', 'RU-ORL': 'russian-tatar',
  'RU-ROS': 'russian-tatar', 'RU-TUL': 'russian-tatar', 'RU-VGG': 'russian-tatar',
  'RU-BEL': 'russian-tatar', 'RU-MO': 'russian-tatar', 'RU-PNZ': 'russian-tatar',
  'RU-RYA': 'russian-tatar', 'RU-TAM': 'russian-tatar', 'RU-VLA': 'russian-tatar',
  'RU-VOR': 'russian-tatar', 'RU-BA': 'russian-tatar', 'RU-KIR': 'russian-tatar',
  'RU-ME': 'russian-tatar', 'RU-UD': 'russian-tatar', 'RU-AST': 'russian-tatar',
  'RU-CU': 'russian-tatar', 'RU-SAM': 'russian-tatar', 'RU-ORE': 'russian-tatar',
  'RU-SAR': 'russian-tatar', 'RU-TA': 'russian-tatar', 'RU-ULY': 'russian-tatar',
  'RU-KO': 'russian-tatar', 'RU-NEN': 'russian-tatar', 'RU-PER': 'russian-tatar',
  'RU-CHE': 'russian-tatar', 'RU-KGN': 'russian-tatar', 'RU-SVE': 'russian-tatar',
  // 西伯利亞文化圈（北方界域）— 烏拉以東
  'RU-YAN': 'siberian', 'RU-KHM': 'siberian',
  'RU-OMS': 'siberian', 'RU-TYU': 'siberian', 'RU-TOM': 'siberian',
  'RU-NVS': 'siberian', 'RU-KEM': 'siberian', 'RU-ALT': 'siberian', 'RU-AL': 'siberian',
  'RU-KK': 'siberian', 'RU-IRK': 'siberian', 'RU-KYA': 'siberian', 'RU-KAM': 'siberian',

  // ---------- 美國 (USA) ----------
  // 太平洋文化圈（亞太界域）
  'US-HI': 'pacific',
  // 北極文化圈（北美界域）
  'US-AK': 'arctic',
  // 盎格魯美洲文化圈（北美界域）— 本土 48 州 + DC
  'US-AL': 'anglo-american', 'US-AR': 'anglo-american', 'US-AZ': 'anglo-american',
  'US-CA': 'anglo-american', 'US-CO': 'anglo-american', 'US-CT': 'anglo-american',
  'US-DC': 'anglo-american', 'US-DE': 'anglo-american', 'US-FL': 'anglo-american',
  'US-GA': 'anglo-american', 'US-IA': 'anglo-american', 'US-ID': 'anglo-american',
  'US-IL': 'anglo-american', 'US-IN': 'anglo-american', 'US-KS': 'anglo-american',
  'US-KY': 'anglo-american', 'US-LA': 'anglo-american', 'US-MA': 'anglo-american',
  'US-MD': 'anglo-american', 'US-ME': 'anglo-american', 'US-MI': 'anglo-american',
  'US-MN': 'anglo-american', 'US-MO': 'anglo-american', 'US-MS': 'anglo-american',
  'US-MT': 'anglo-american', 'US-NC': 'anglo-american', 'US-ND': 'anglo-american',
  'US-NE': 'anglo-american', 'US-NH': 'anglo-american', 'US-NJ': 'anglo-american',
  'US-NM': 'anglo-american', 'US-NV': 'anglo-american', 'US-NY': 'anglo-american',
  'US-OH': 'anglo-american', 'US-OK': 'anglo-american', 'US-OR': 'anglo-american',
  'US-PA': 'anglo-american', 'US-RI': 'anglo-american', 'US-SC': 'anglo-american',
  'US-SD': 'anglo-american', 'US-TN': 'anglo-american', 'US-TX': 'anglo-american',
  'US-UT': 'anglo-american', 'US-VA': 'anglo-american', 'US-VT': 'anglo-american',
  'US-WA': 'anglo-american', 'US-WI': 'anglo-american', 'US-WV': 'anglo-american',
  'US-WY': 'anglo-american',

  // ---------- 加拿大 (CAN) ----------
  // 法蘭西美洲文化圈（北美界域）
  'CA-QC': 'franco-american',  // 魁北克
  'CA-NB': 'franco-american',  // 新伯倫瑞克（阿卡迪亞核心，法語人口最高的英語區省）
  // 北極文化圈（北美界域）
  'CA-NT': 'arctic', 'CA-NU': 'arctic', 'CA-YT': 'arctic',
  // 盎格魯美洲文化圈（北美界域）— 南方各省（CA-NB 移到 franco-american）
  'CA-AB': 'anglo-american', 'CA-BC': 'anglo-american', 'CA-MB': 'anglo-american',
  'CA-NL': 'anglo-american', 'CA-NS': 'anglo-american',
  'CA-ON': 'anglo-american', 'CA-PE': 'anglo-american', 'CA-SK': 'anglo-american',

  // ---------- 利比亞 (LBY) ----------
  // 埃及文化圈（中央界域）— 昔蘭尼加（東部）
  'LY-BU': 'egyptian',  // 布特南省（圖卜魯格）
  'LY-AJ': 'egyptian',  // 艾季達比亞
  'LY-KF': 'egyptian',  // 庫夫拉
  'LY-BA': 'egyptian',  // 班加西
  'LY-MJ': 'egyptian',  // 邁爾季
  'LY-JA': 'egyptian',  // 綠山省（傑貝爾艾赫達爾）
  'LY-QB': 'egyptian',  // 古拜
  // 拉丁文化圈（西方界域）— 的黎波里塔尼亞 + 費贊（中西部，義屬殖民延伸）
  'LY-GD': 'latin-cultural', 'LY-NQ': 'latin-cultural', 'LY-MQ': 'latin-cultural',
  'LY-WS': 'latin-cultural', 'LY-GT': 'latin-cultural', 'LY-MI': 'latin-cultural',
  'LY-MB': 'latin-cultural', 'LY-TN': 'latin-cultural', 'LY-ZA': 'latin-cultural',
  'LY-JI': 'latin-cultural', 'LY-MZ': 'latin-cultural', 'LY-JU': 'latin-cultural',
  'LY-SB': 'latin-cultural', 'LY-WD': 'latin-cultural', 'LY-SR': 'latin-cultural',

  // ---------- 阿富汗 (AFG) ----------
  // 波斯文化圈（中央界域）— 西部與中部
  'AF-HER': 'persian', 'AF-FRA': 'persian', 'AF-NIM': 'persian', 'AF-BDG': 'persian',
  'AF-GHO': 'persian', 'AF-BAM': 'persian', 'AF-KAB': 'persian', 'AF-PAR': 'persian',
  'AF-WAR': 'persian', 'AF-LOG': 'persian', 'AF-KAP': 'persian',
  // 印度文化圈（東方界域）— 南部與東部，犍陀羅
  'AF-KAN': 'indian', 'AF-HEL': 'indian', 'AF-ZAB': 'indian', 'AF-URU': 'indian',
  'AF-GHA': 'indian', 'AF-PIA': 'indian', 'AF-PKA': 'indian', 'AF-KHO': 'indian',
  'AF-NAN': 'indian', 'AF-KNR': 'indian', 'AF-NUR': 'indian', 'AF-LAG': 'indian',
  // 圖蘭-突厥文化圈（北方界域）— 北部
  'AF-BAL': 'turanian-turkic', 'AF-JOW': 'turanian-turkic', 'AF-FYB': 'turanian-turkic',
  'AF-SAR': 'turanian-turkic', 'AF-SAM': 'turanian-turkic', 'AF-KDZ': 'turanian-turkic',
  'AF-TAK': 'turanian-turkic', 'AF-BGL': 'turanian-turkic', 'AF-BDS': 'turanian-turkic',

  // ---------- 烏克蘭 (UKR) ----------
  // 盧布林文化圈（西方界域）— 西烏 + 基輔以西
  'UA-07': 'lublin',   // 沃倫
  'UA-56': 'lublin',   // 羅夫諾
  'UA-46': 'lublin',   // 利沃夫
  'UA-26': 'lublin',   // 伊凡諾－弗蘭科夫斯克
  'UA-61': 'lublin',   // 捷爾諾波爾
  'UA-68': 'lublin',   // 赫梅利尼茨基
  'UA-21': 'lublin',   // 外喀爾巴阡
  'UA-77': 'lublin',   // 切爾諾夫策
  'UA-05': 'lublin',   // 文尼察
  'UA-32': 'lublin',   // 基輔州
  'UA-30': 'lublin',   // 基輔市
  'UA-18': 'lublin',   // 日托米爾
  'UA-71': 'lublin',   // 切爾卡瑟
  // 羅斯-韃靼文化圈（北方界域）— 東烏 + 南烏
  'UA-63': 'russian-tatar',  // 哈爾科夫
  'UA-09': 'russian-tatar',  // 盧甘斯克
  'UA-14': 'russian-tatar',  // 頓內次克
  'UA-12': 'russian-tatar',  // 第聶伯羅彼得羅夫斯克
  'UA-23': 'russian-tatar',  // 札波羅熱
  'UA-48': 'russian-tatar',  // 米科萊夫
  'UA-65': 'russian-tatar',  // 赫爾松
  'UA-51': 'russian-tatar',  // 奧德薩
  'UA-59': 'russian-tatar',  // 蘇梅
  'UA-53': 'russian-tatar',  // 波爾塔瓦
  'UA-74': 'russian-tatar',  // 切爾尼戈夫
  'UA-35': 'russian-tatar',  // 基洛夫格勒

  // ---------- 蘇丹 (SDN) ----------
  // 埃及文化圈（中央界域）— 尼羅河谷 + 中部 + 東部 (Funj 蘇丹國 + 鄂圖曼遺產)
  'SD-NO': 'egyptian',  // 北部省
  'SD-NR': 'egyptian',  // 尼羅省
  'SD-RS': 'egyptian',  // 紅海省
  'SD-KH': 'egyptian',  // 喀土穆
  'SD-GZ': 'egyptian',  // 杰濟拉
  'SD-NB': 'egyptian',  // 青尼羅
  'SD-SI': 'egyptian',  // 森納爾
  'SD-NW': 'egyptian',  // 白尼羅
  'SD-KA': 'egyptian',  // 卡薩拉
  'SD-GD': 'egyptian',  // 加達里夫
  // 西非-薩赫爾文化圈（南方界域）— 達富爾 + 科爾多凡（Bilad al-Sudan「黑人之地」西部延伸）
  'SD-DN': 'west-african-sahel',  // 北達富爾
  'SD-DS': 'west-african-sahel',  // 南達富爾 (NE 10m 以同代碼包含東達富爾)
  'SD-DE': 'west-african-sahel',  // 中達富爾 (NE 標記為 DE 但實 ISO 為 DC)
  'SD-DW': 'west-african-sahel',  // 西達富爾
  'SD-KS': 'west-african-sahel',  // 南科爾多凡
  'SD-KN': 'west-african-sahel',  // 北科爾多凡

  // ---------- 衣索比亞 (ETH) ----------
  // 衣索比亞文化圈（南方界域）— 高地基督徒 (Aksumite 後裔，正教東正教徒)
  'ET-TI': 'ethiopian',  // 提格雷
  'ET-AM': 'ethiopian',  // 阿姆哈拉
  'ET-BE': 'ethiopian',  // 本尚古勒-古馬茲
  'ET-DD': 'ethiopian',  // 德雷達瓦
  'ET-AA': 'ethiopian',  // 阿迪斯阿貝巴
  // 東非-斯瓦希里文化圈（南方界域）— 低地穆斯林 (Somali/Afar 為主)
  'ET-SO': 'east-african-swahili',  // 索馬利州
  'ET-AF': 'east-african-swahili',  // 阿法爾州
  'ET-OR': 'east-african-swahili',  // 奧羅米亞 (穆斯林過半)
  'ET-SN': 'east-african-swahili',  // 南方各族州
  'ET-GA': 'east-african-swahili',  // 甘貝拉
  'ET-HA': 'east-african-swahili',  // 哈勒爾

  // ---------- 奈及利亞 (NGA) ----------
  // 西非-薩赫爾文化圈（南方界域）— 北部 (Sokoto 哈里發遺產，豪薩-富拉尼穆斯林)
  'NG-SO': 'west-african-sahel', 'NG-ZA': 'west-african-sahel', 'NG-KE': 'west-african-sahel',
  'NG-NI': 'west-african-sahel', 'NG-KW': 'west-african-sahel', 'NG-KT': 'west-african-sahel',
  'NG-KN': 'west-african-sahel', 'NG-JI': 'west-african-sahel', 'NG-YO': 'west-african-sahel',
  'NG-BO': 'west-african-sahel', 'NG-AD': 'west-african-sahel', 'NG-TA': 'west-african-sahel',
  'NG-BA': 'west-african-sahel', 'NG-GO': 'west-african-sahel', 'NG-PL': 'west-african-sahel',
  'NG-NA': 'west-african-sahel', 'NG-KO': 'west-african-sahel', 'NG-FC': 'west-african-sahel',
  'NG-KD': 'west-african-sahel',
  // 幾內亞灣文化圈（南方界域）— 南部 (優魯巴/伊博基督徒、貝南帝國遺產)
  'NG-LA': 'gulf-of-guinea', 'NG-OG': 'gulf-of-guinea', 'NG-OY': 'gulf-of-guinea',
  'NG-OS': 'gulf-of-guinea', 'NG-EK': 'gulf-of-guinea', 'NG-ON': 'gulf-of-guinea',
  'NG-ED': 'gulf-of-guinea', 'NG-DE': 'gulf-of-guinea', 'NG-BY': 'gulf-of-guinea',
  'NG-RI': 'gulf-of-guinea', 'NG-AK': 'gulf-of-guinea', 'NG-CR': 'gulf-of-guinea',
  'NG-AB': 'gulf-of-guinea', 'NG-IM': 'gulf-of-guinea', 'NG-AN': 'gulf-of-guinea',
  'NG-EN': 'gulf-of-guinea', 'NG-EB': 'gulf-of-guinea', 'NG-BE': 'gulf-of-guinea',

  // ---------- 迦納 (GHA) ----------
  // 西非-薩赫爾文化圈（南方界域）— 北 3 州 (Zongo 穆斯林移民走廊)
  'GH-NP': 'west-african-sahel', 'GH-UE': 'west-african-sahel', 'GH-UW': 'west-african-sahel',
  // 幾內亞灣文化圈（南方界域）— 南 7 州 (Akan/Ashanti/Fante 海岸與森林)
  'GH-AH': 'gulf-of-guinea', 'GH-BA': 'gulf-of-guinea', 'GH-EP': 'gulf-of-guinea',
  'GH-CP': 'gulf-of-guinea', 'GH-WP': 'gulf-of-guinea', 'GH-AA': 'gulf-of-guinea',
  'GH-TV': 'gulf-of-guinea',
}

/** Admin_1 名稱對照（繁體中文，用於 tooltip 顯示） */
export const ADMIN1_NAME_ZH: Record<string, string> = {
  // CHN
  'CN-GS': '甘肅省', 'CN-QH': '青海省', 'CN-GX': '廣西壯族自治區', 'CN-GZ': '貴州省',
  'CN-CQ': '重慶市', 'CN-BJ': '北京市', 'CN-FJ': '福建省', 'CN-AH': '安徽省',
  'CN-GD': '廣東省', 'CN-XZ': '西藏自治區', 'CN-XJ': '新疆維吾爾自治區', 'CN-HI': '海南省',
  'CN-NX': '寧夏回族自治區', 'CN-SN': '陝西省', 'CN-SX': '山西省', 'CN-HB': '湖北省',
  'CN-HN': '湖南省', 'CN-SC': '四川省', 'CN-YN': '雲南省', 'CN-HE': '河北省',
  'CN-HA': '河南省', 'CN-LN': '遼寧省', 'CN-SD': '山東省', 'CN-TJ': '天津市',
  'CN-JX': '江西省', 'CN-JS': '江蘇省', 'CN-SH': '上海市', 'CN-ZJ': '浙江省',
  'CN-JL': '吉林省', 'CN-NM': '內蒙古自治區', 'CN-HL': '黑龍江省',
  // USA — 全 50 州 + DC，繁體中文
  'US-AK': '阿拉斯加州', 'US-AL': '阿拉巴馬州', 'US-AR': '阿肯色州', 'US-AZ': '亞利桑那州',
  'US-CA': '加利福尼亞州', 'US-CO': '科羅拉多州', 'US-CT': '康乃狄克州', 'US-DC': '華盛頓哥倫比亞特區',
  'US-DE': '德拉瓦州', 'US-FL': '佛羅里達州', 'US-GA': '喬治亞州', 'US-HI': '夏威夷州',
  'US-IA': '愛荷華州', 'US-ID': '愛達荷州', 'US-IL': '伊利諾州', 'US-IN': '印第安納州',
  'US-KS': '堪薩斯州', 'US-KY': '肯塔基州', 'US-LA': '路易斯安那州', 'US-MA': '麻薩諸塞州',
  'US-MD': '馬里蘭州', 'US-ME': '緬因州', 'US-MI': '密西根州', 'US-MN': '明尼蘇達州',
  'US-MO': '密蘇里州', 'US-MS': '密西西比州', 'US-MT': '蒙大拿州', 'US-NC': '北卡羅萊納州',
  'US-ND': '北達科他州', 'US-NE': '內布拉斯加州', 'US-NH': '新罕布夏州', 'US-NJ': '紐澤西州',
  'US-NM': '新墨西哥州', 'US-NV': '內華達州', 'US-NY': '紐約州', 'US-OH': '俄亥俄州',
  'US-OK': '奧克拉荷馬州', 'US-OR': '奧勒岡州', 'US-PA': '賓夕法尼亞州', 'US-RI': '羅德島州',
  'US-SC': '南卡羅萊納州', 'US-SD': '南達科他州', 'US-TN': '田納西州', 'US-TX': '德克薩斯州',
  'US-UT': '猶他州', 'US-VA': '維吉尼亞州', 'US-VT': '佛蒙特州', 'US-WA': '華盛頓州',
  'US-WI': '威斯康辛州', 'US-WV': '西維吉尼亞州', 'US-WY': '懷俄明州',
  // CAN
  'CA-AB': '亞伯達省', 'CA-BC': '不列顛哥倫比亞省', 'CA-MB': '曼尼托巴省', 'CA-NB': '新伯倫瑞克省',
  'CA-NL': '紐芬蘭與拉布拉多省', 'CA-NS': '新斯科細亞省', 'CA-NT': '西北地區', 'CA-NU': '努納武特地區',
  'CA-ON': '安大略省', 'CA-PE': '愛德華王子島省', 'CA-QC': '魁北克省', 'CA-SK': '薩克其萬省',
  'CA-YT': '育空地區',
  // RUS — 重點區域繁體中文（其他 fallback NE 簡體名稱）
  'RU-AD': '阿迪格共和國', 'RU-KC': '卡拉恰耶夫切爾克斯共和國', 'RU-IN': '印古什共和國',
  'RU-KB': '卡巴爾達巴爾卡爾共和國', 'RU-SE': '北奧塞梯共和國', 'RU-CE': '車臣共和國',
  'RU-DA': '達吉斯坦共和國', 'RU-STA': '斯塔夫羅波爾邊疆區', 'RU-KDA': '克拉斯諾達爾邊疆區',
  'RU-KGD': '加里寧格勒州', 'RU-CHU': '楚科奇自治區', 'RU-SA': '薩哈共和國（雅庫特）',
  'RU-BU': '布里亞特共和國', 'RU-TY': '圖瓦共和國', 'RU-KL': '卡爾梅克共和國',
  'RU-AMU': '阿穆爾州', 'RU-ZAB': '外貝加爾邊疆區', 'RU-PRI': '濱海邊疆區',
  'RU-YEV': '猶太自治州', 'RU-KHA': '哈巴羅夫斯克邊疆區',
  'RU-MAG': '馬加丹州', 'RU-SAK': '薩哈林州', 'RU-KAM': '堪察加邊疆區',
  'RU-MOW': '莫斯科州', 'RU-MOS': '莫斯科', 'RU-SPE': '聖彼得堡',
  'RU-LEN': '列寧格勒州', 'RU-MUR': '摩爾曼斯克州', 'RU-KR': '卡累利阿共和國',
  'RU-ARK': '阿爾漢格爾斯克州', 'RU-NEN': '涅涅茨自治區',
  'RU-KO': '科米共和國', 'RU-PER': '彼爾姆邊疆區', 'RU-SVE': '斯維爾德洛夫斯克州',
  'RU-CHE': '車里雅賓斯克州', 'RU-TA': '韃靼斯坦共和國', 'RU-BA': '巴什科爾托斯坦共和國',
  'RU-KYA': '克拉斯諾亞爾斯克邊疆區', 'RU-IRK': '伊爾庫茨克州',
  // LBY
  'LY-BU': '布特南（圖卜魯格）', 'LY-AJ': '艾季達比亞', 'LY-KF': '庫夫拉',
  'LY-BA': '班加西', 'LY-MJ': '邁爾季', 'LY-JA': '傑貝爾艾赫達爾（綠山）', 'LY-QB': '古拜',
  'LY-GD': '加達米斯', 'LY-NQ': '努加特海姆斯', 'LY-MQ': '穆爾祖格',
  'LY-WS': '什阿提', 'LY-GT': '加特', 'LY-MI': '米蘇拉塔',
  'LY-MB': '邁爾蓋卜', 'LY-TN': '塔朱拉', 'LY-ZA': '札維亞',
  'LY-JI': '吉法拉', 'LY-MZ': '米茲達', 'LY-JU': '朱夫拉',
  'LY-SB': '塞卜哈', 'LY-WD': '瓦迪哈耶特', 'LY-SR': '蘇爾特',
  // AFG
  'AF-BDS': '巴達赫尚', 'AF-TAK': '塔哈爾', 'AF-KDZ': '昆都士', 'AF-BAL': '巴爾赫',
  'AF-JOW': '朱茲詹', 'AF-FYB': '法利亞布', 'AF-BDG': '巴德吉斯', 'AF-HER': '赫拉特',
  'AF-NIM': '尼姆魯茲', 'AF-FRA': '法拉', 'AF-KNR': '庫納爾', 'AF-NUR': '努里斯坦',
  'AF-NAN': '楠格哈爾', 'AF-KHO': '霍斯特', 'AF-PKA': '帕克蒂亞', 'AF-PIA': '帕克蒂卡',
  'AF-ZAB': '扎布爾', 'AF-KAN': '坎大哈', 'AF-HEL': '赫爾曼德', 'AF-URU': '烏魯茲甘',
  'AF-GHA': '加茲尼', 'AF-PAR': '帕爾旺', 'AF-KAB': '喀布爾', 'AF-LAG': '拉格曼',
  'AF-LOG': '洛加爾', 'AF-KAP': '卡比薩', 'AF-WAR': '瓦爾達克', 'AF-BAM': '巴米揚',
  'AF-SAR': '薩爾普勒', 'AF-GHO': '古爾', 'AF-BGL': '巴格蘭', 'AF-SAM': '薩曼甘',
  // UKR
  'UA-74': '切爾尼戈夫州', 'UA-07': '沃倫州', 'UA-56': '羅夫諾州',
  'UA-18': '日托米爾州', 'UA-32': '基輔州', 'UA-30': '基輔市',
  'UA-21': '外喀爾巴阡州', 'UA-77': '切爾諾夫策州', 'UA-26': '伊凡諾－弗蘭科夫斯克州',
  'UA-51': '奧德薩州', 'UA-05': '文尼察州', 'UA-46': '利沃夫州',
  'UA-59': '蘇梅州', 'UA-63': '哈爾科夫州', 'UA-09': '盧甘斯克州',
  'UA-14': '頓內次克州', 'UA-65': '赫爾松州', 'UA-23': '札波羅熱州',
  'UA-48': '米科萊夫州', 'UA-53': '波爾塔瓦州', 'UA-68': '赫梅利尼茨基州',
  'UA-61': '捷爾諾波爾州', 'UA-12': '第聶伯羅彼得羅夫斯克州', 'UA-71': '切爾卡瑟州',
  'UA-35': '基洛夫格勒州',
  // SDN
  'SD-NO': '北部省', 'SD-NR': '尼羅省', 'SD-RS': '紅海省', 'SD-KH': '喀土穆省',
  'SD-GZ': '傑濟拉省', 'SD-NB': '青尼羅省', 'SD-SI': '森納爾省', 'SD-NW': '白尼羅省',
  'SD-KA': '卡薩拉省', 'SD-GD': '加達里夫省',
  'SD-DN': '北達富爾省', 'SD-DS': '南達富爾省', 'SD-DE': '中達富爾省', 'SD-DW': '西達富爾省',
  'SD-KS': '南科爾多凡省', 'SD-KN': '北科爾多凡省',
  // ETH
  'ET-TI': '提格雷州', 'ET-AM': '阿姆哈拉州', 'ET-BE': '本尚古勒-古馬茲州',
  'ET-DD': '德雷達瓦', 'ET-AA': '阿迪斯阿貝巴', 'ET-SO': '索馬利州',
  'ET-AF': '阿法爾州', 'ET-OR': '奧羅米亞州', 'ET-SN': '南方各族州',
  'ET-GA': '甘貝拉州', 'ET-HA': '哈勒爾州',
  // NGA
  'NG-SO': '索科托州', 'NG-ZA': '札姆法拉州', 'NG-KE': '凱比州', 'NG-NI': '尼日州',
  'NG-KW': '夸拉州', 'NG-KT': '卡齊納州', 'NG-KN': '卡諾州', 'NG-JI': '吉加瓦州',
  'NG-YO': '約貝州', 'NG-BO': '博爾諾州', 'NG-AD': '阿達馬瓦州', 'NG-TA': '塔拉巴州',
  'NG-BA': '包奇州', 'NG-GO': '貢貝州', 'NG-PL': '高原州', 'NG-NA': '納薩拉瓦州',
  'NG-KO': '科吉州', 'NG-FC': '聯邦首都區', 'NG-KD': '卡杜納州',
  'NG-LA': '拉哥斯州', 'NG-OG': '奧貢州', 'NG-OY': '奧約州', 'NG-OS': '奧孫州',
  'NG-EK': '埃基蒂州', 'NG-ON': '翁多州', 'NG-ED': '埃多州', 'NG-DE': '三角洲州',
  'NG-BY': '巴耶爾薩州', 'NG-RI': '河流州', 'NG-AK': '阿夸伊博姆州', 'NG-CR': '克羅斯河州',
  'NG-AB': '阿比亞州', 'NG-IM': '伊莫州', 'NG-AN': '阿南布拉州', 'NG-EN': '埃努古州',
  'NG-EB': '埃邦伊州', 'NG-BE': '貝努埃州',
  // GHA
  'GH-NP': '北部地區', 'GH-UE': '東北地區', 'GH-UW': '西北地區',
  'GH-AH': '阿散蒂地區', 'GH-BA': '布朗阿哈福地區', 'GH-EP': '東部地區',
  'GH-CP': '中部地區', 'GH-WP': '西部地區', 'GH-AA': '大阿克拉地區', 'GH-TV': '沃爾特地區',
}

/** 給一個 admin_1 iso_3166_2 代碼，回傳所屬文化圈與界域 */
export function sphereForAdmin1(iso_3166_2: string): CulturalSphere | undefined {
  const sphereId = ADMIN1_SPHERE[iso_3166_2]
  if (!sphereId) return undefined
  return SPHERES.find(s => s.id === sphereId)
}

export function realmForAdmin1(iso_3166_2: string): Realm | undefined {
  const sphere = sphereForAdmin1(iso_3166_2)
  return sphere ? realmById(sphere.realm_id) : undefined
}

export function realmById(id: RealmId): Realm {
  return REALMS.find(r => r.id === id)!
}

export function spheresByRealm(realmId: RealmId): CulturalSphere[] {
  return SPHERES.filter(s => s.realm_id === realmId)
}

export function realmForCountry(iso_a3: string): Realm | undefined {
  const id = COUNTRY_REALM[iso_a3]
  return id ? realmById(id) : undefined
}

/** Returns all cultural spheres a country participates in (across realms) */
export function spheresForCountry(iso_a3: string): { sphere: CulturalSphere; member: Member }[] {
  const out: { sphere: CulturalSphere; member: Member }[] = []
  for (const sphere of SPHERES) {
    for (const m of sphere.members) {
      if (m.iso_a3 === iso_a3) out.push({ sphere, member: m })
    }
  }
  return out
}

/**
 * Within a given realm, pick the country's "primary" sphere for drill-down coloring.
 * Prefer non-extension membership; fall back to first match.
 */
export function primarySphereForCountryInRealm(iso_a3: string, realm: RealmId): CulturalSphere | undefined {
  const realmSpheres = SPHERES.filter(s => s.realm_id === realm)
  for (const s of realmSpheres) {
    if (s.members.some(m => m.iso_a3 === iso_a3 && !m.is_extension)) return s
  }
  for (const s of realmSpheres) {
    if (s.members.some(m => m.iso_a3 === iso_a3)) return s
  }
  return undefined
}

// ---------- Sub-shade generator (same color family) ----------

function hexToHsl(hex: string): { h: number; s: number; l: number } {
  const v = hex.replace('#', '')
  const r = parseInt(v.slice(0, 2), 16) / 255
  const g = parseInt(v.slice(2, 4), 16) / 255
  const b = parseInt(v.slice(4, 6), 16) / 255
  const max = Math.max(r, g, b), min = Math.min(r, g, b)
  const l = (max + min) / 2
  let h = 0, s = 0
  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) * 60
    else if (max === g) h = ((b - r) / d + 2) * 60
    else h = ((r - g) / d + 4) * 60
  }
  return { h, s: s * 100, l: l * 100 }
}

function hslToHex(h: number, s: number, l: number): string {
  s /= 100
  l /= 100
  const k = (n: number) => (n + h / 30) % 12
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => {
    const c = l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))
    return Math.round(255 * Math.max(0, Math.min(1, c))).toString(16).padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`
}

/** Generate a sphere shade in the realm's color family.
 *  idx in 0..total-1 — varies lightness ±14% and a small hue shift ±10° around the realm hex. */
export function shadeForSphere(realmHex: string, idx: number, total: number): string {
  if (total <= 1) return realmHex
  const { h, s, l } = hexToHsl(realmHex)
  const t = idx / (total - 1)
  const newL = Math.max(28, Math.min(72, l - 14 + t * 28))
  const hueShift = -10 + t * 20
  const newH = (h + hueShift + 360) % 360
  return hslToHex(newH, s, newL)
}

/** Build a per-realm sphere->color map keyed by sphere id. */
export function sphereColorsByRealm(realm: RealmId): Record<string, string> {
  const r = realmById(realm)
  const list = SPHERES.filter(s => s.realm_id === realm)
  const out: Record<string, string> = {}
  list.forEach((s, i) => {
    out[s.id] = shadeForSphere(r.color, i, list.length)
  })
  return out
}
