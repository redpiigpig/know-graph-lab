export interface TravelActivity {
  time: string
  title: string
  detail: string
  kind: 'flight' | 'food' | 'sight' | 'hotel' | 'transfer' | 'free'
  mapQuery?: string
}

export interface TravelDay {
  date: string
  weekday: string
  city: string
  country: string
  flag: string
  theme: string
  accent: 'emerald' | 'amber' | 'rose' | 'slate'
  highlights: string[]
  budgetTwd: string
  activities: TravelActivity[]
  transport: string[]
  reminder?: string
}

export interface TravelFlight {
  route: string
  airline: string
  flightNo: string
  depart: string
  departAirport: string
  arrive: string
  arriveAirport: string
}

export interface TravelHotel {
  city: string
  nights: string
  nameZh: string
  nameLocal: string
  address: string
  phone: string
  mapQuery: string
  paidTwd: number
}

export interface TravelEntryTask {
  country: string
  flag: string
  title: string
  openDate: string
  note: string
  href: string
}

export interface TravelCostItem {
  label: string
  totalTwd: number
  perPersonTwd: number
  detail: string
}

export interface TravelMovieSpot {
  city: string
  work: string
  location: string
  day: string
  status: '主行程' | '順路短停' | '備選'
  photoTip: string
  mapQuery: string
  href: string
}

export interface TravelChecklistGroup {
  id: string
  owner: string
  title: string
  items: string[]
}

export interface TravelTransitGuide {
  city: string
  flag: string
  modes: string
  itineraryUse: string
  payment: string
  recommendation: string
  caution: string
  href: string
}

export interface TravelFriendRecommendation {
  place: string
  status: '已排入' | '原本已有' | '半日備選'
  timing: string
  detail: string
  tradeoff: string
  mapQuery: string
  href: string
}

export interface TravelInsurancePerson {
  role: string
  name: string
  englishName: string
  birth: string
  rocBirth: string
  idMasked: string
}

export interface TravelBilingualScheduleItem {
  time: string
  zh: string
  en: string
}

export interface TravelProgramDay {
  date: string
  weekdayZh: string
  weekdayEn: string
  themeZh: string
  themeEn: string
  locationZh: string
  locationEn: string
  items: TravelBilingualScheduleItem[]
  personalNoteZh?: string
  personalNoteEn?: string
}

export interface TravelProgramNotice {
  level: 'duplicate' | 'conflict' | 'budget'
  titleZh: string
  titleEn: string
  detailZh: string
  detailEn: string
}

export const southeastAsiaTrip2026 = {
  slug: 'singapore-malaysia-thailand-2026',
  title: '星馬泰家庭旅行',
  eyebrow: 'Singapore · Malaysia · Thailand',
  startDate: '2026-07-17',
  endDate: '2026-07-24',
  dateLabel: '2026.07.17 — 07.24',
  duration: '8 天 7 夜',
  route: ['台北', '新加坡', '吉隆坡', '曼谷', '台北'],
  countries: ['🇸🇬 新加坡', '🇲🇾 馬來西亞', '🇹🇭 泰國'],
  originalPlanUrl: 'https://app.notion.com/p/39c83250cfb7802493cff48eaf243664',
  sourceLinks: {
    singaporeConan: 'https://asean.or.jp.yucca-works.jp/en/wp-content/uploads/sites/3/20200323_Press-Release_ASEAN_tourism_awardPR.pdf',
    kualaLumpurCharter: 'https://tw.trip.com/things-to-do/detail/58748051/',
    malaysiaMovies: 'https://www.tatlerasia.com/lifestyle/travel/merdeka-118-blue-mansion-malaysian-destinations-in-international-films',
    bangkokMovies: 'https://filmthailand.org/locations/streets-and-roads/',
  },
  flights: [
    {
      route: '台北 → 新加坡', airline: '酷航', flightNo: 'TR875',
      depart: '07/17 00:55', departAirport: '桃園機場 T1',
      arrive: '07/17 05:20', arriveAirport: '樟宜機場 T1',
    },
    {
      route: '新加坡 → 吉隆坡', airline: '酷航', flightNo: 'TR472',
      depart: '07/18 16:00', departAirport: '樟宜機場 T1',
      arrive: '07/18 17:25', arriveAirport: '吉隆坡國際機場 T2',
    },
    {
      route: '吉隆坡 → 曼谷', airline: '馬來西亞航空', flightNo: 'MH774',
      depart: '07/21 16:00', departAirport: '吉隆坡國際機場 T1',
      arrive: '07/21 17:20', arriveAirport: '素萬那普機場',
    },
    {
      route: '曼谷 → 台北', airline: '泰國越捷航空', flightNo: 'VZ566',
      depart: '07/24 01:45', departAirport: '素萬那普機場',
      arrive: '07/24 06:35', arriveAirport: '桃園機場 T1',
    },
  ] satisfies TravelFlight[],
  hotels: [
    {
      city: '新加坡', nights: '07/17 · 1 晚', nameZh: '宜必思快捷新加坡水晶飯店',
      nameLocal: 'ibis budget Singapore Crystal', address: '50 Lor 18 Geylang, Singapore 398824',
      phone: '+65 6844 7888', mapQuery: 'ibis budget Singapore Crystal', paidTwd: 2978,
    },
    {
      city: '吉隆坡', nights: '07/18–07/21 · 3 晚', nameZh: 'WP 飯店',
      nameLocal: 'WP Hotel', address: '362 Jalan Tuanku Abdul Rahman, Chow Kit, Kuala Lumpur 50100',
      phone: '+60 3 2618 1188', mapQuery: 'WP Hotel Kuala Lumpur', paidTwd: 4588,
    },
    {
      city: '曼谷', nights: '07/21–07/23 · 2 晚', nameZh: '雙子塔飯店',
      nameLocal: 'The Twin Towers Hotel Bangkok', address: '88 Rama VI Rd, Rong Muang, Pathum Wan, Bangkok 10330',
      phone: '+66 2 216 9555', mapQuery: 'The Twin Towers Hotel Bangkok', paidTwd: 4122,
    },
  ] satisfies TravelHotel[],
  entryTasks: [
    {
      country: '新加坡', flag: '🇸🇬', title: 'SG Arrival Card', openDate: '07/15 起可填',
      note: '預計 07/17 入境；只走官方免費網站，三位成人皆需資料。',
      href: 'https://www.ica.gov.sg/enter-transit-depart/entering-singapore/sg-arrival-card',
    },
    {
      country: '馬來西亞', flag: '🇲🇾', title: 'Malaysia Digital Arrival Card', openDate: '07/16 起留意',
      note: '預計 07/18 入境；依官方系統開放時間完成 MDAC。',
      href: 'https://imigresen-online.imi.gov.my/mdac/main',
    },
    {
      country: '泰國', flag: '🇹🇭', title: 'Thailand Digital Arrival Card', openDate: '07/19 起可填',
      note: '預計 07/21 入境；可用 group submission，最晚應在入境前完成。',
      href: 'https://tdac.immigration.go.th/',
    },
  ] satisfies TravelEntryTask[],
  transitGuides: [
    {
      city: '新加坡', flag: '🇸🇬', modes: 'MRT＋公共巴士＋Grab',
      itineraryUse: 'Day 1 機場／飯店／市中心與濱海灣；Day 2 飯店前往樟宜。',
      payment: '三人各用一張支援感應的 Visa／Mastercard 或各自的手機錢包；MRT 進出站、巴士上下車都要用同一張卡感應。',
      recommendation: '不用買 Singapore Tourist Pass。行程只有約 1.5 天且多段會搭 Grab，單程感應付款較省。',
      caution: '外國發行的 Visa／Mastercard 每張卡每天另收 S$0.60；一張卡不能同時替三人進站，三人需各自一張。',
      href: 'https://www.simplygo.com.sg/faqs/cards-and-charms/simplygo/contactless-bank-cards/',
    },
    {
      city: '吉隆坡', flag: '🇲🇾', modes: 'KLIA Ekspres＋Grab＋私人包車；少量 MRT／LRT',
      itineraryUse: 'Day 2、5 使用 KLIA Ekspres；Day 3 全日包車；Day 4 市區多以 Grab 串接。',
      payment: 'KLIA Ekspres 使用手機電子票；Rapid KL 少量搭乘時在車站售票機買單程 Token。若臨時搭公車，需 Touch ’n Go 卡。',
      recommendation: '事先在官網／App 買 Group Saver 來回票：3 成人同筆交易，每人 RM80，三人共 RM240。',
      caution: 'Group Saver 需三人同行並選定 07/18、07/21；不可改期或退款。Rapid Kembara 對本行程不划算。',
      href: 'https://www.kliaekspres.com/offers/our-offers/group-saver/',
    },
    {
      city: '曼谷', flag: '🇹🇭', modes: 'Grab＋BTS＋渡輪；Airport Rail Link／MRT 為備用',
      itineraryUse: 'Day 6 舊城與河岸以 Grab、渡輪為主；Day 7 主要搭 BTS；機場移動視行李與塞車決定。',
      payment: 'BTS 在售票機買單程票，準備泰銖硬幣／紙鈔；MRT 可用各自的感應 Visa／Mastercard 刷進刷出；渡輪準備小額現金。',
      recommendation: '不用買 Rabbit Card 或 BTS 一日券；本行程 BTS 次數不多，單程票最簡單。',
      caution: 'BTS 與 MRT 是不同系統，Rabbit Card 不能當作 MRT 藍線／紫線票。刷卡進出必須使用同一張卡。',
      href: 'https://www.bts.co.th/eng/library/system-tickets.html',
    },
  ] satisfies TravelTransitGuide[],
  checklistGroups: [
    {
      id: 'packing-family',
      owner: '三人共同',
      title: '攜帶物品',
      items: [
        '衣服', '梳子', '化妝品', '卸妝乳', '卸妝棉', '牙刷', '牙尖刷',
        '充電器', '插頭／轉接頭', '水壺', '毛巾', '泳裝', '護手霜', '洗臉巾',
        '夾子', '雨傘', '相機', '護照', '網卡', '杯麵',
      ],
    },
    {
      id: 'todo-family',
      owner: '三人共同',
      title: '待辦事項',
      items: [
        '整理完整行程',
        '確認三人護照效期與各國入境資格',
        '完成 SGAC、MDAC、TDAC 並截圖',
        '訂購線上網卡／eSIM',
        '去銀行確認信用卡已開啟海外交易',
        '兌換 SGD／MYR／THB 現金',
        '出發前安裝並確認網卡可啟用',
        '購買吉隆坡包車團與必要行程票券',
        '購買 KLIA Ekspres Group Saver 三人來回票（07/18、07/21）',
        '購買三人旅遊平安險／海外醫療保險',
        '四段航班與三間住宿訂單離線保存',
        '保單、海外醫療與緊急聯絡資料離線保存',
        'Grab 綁卡並確認全家聯絡方式',
        '完成需要訂位的午晚餐',
      ],
    },
  ] satisfies TravelChecklistGroup[],
  bookingAlerts: [
    '回程分流已確認：爸媽於 07/24 01:45 搭 VZ566 返台；CHEN WEI CHANG 於送機後參加 INEB，07/30 01:35 再返台。',
    '本頁只計算 07/17–07/24 家庭旅遊；07/24 之後的 INEB 住宿、交通與活動費用不列入。',
  ],
  insuranceSummary: {
    notionUrl: 'https://app.notion.com/p/39d83250cfb78126ab52ce29ef32b314',
    cardholder: {
      name: '張辰瑋', birth: '1995-10-19', rocBirth: '民國 84-10-19',
      idMasked: 'A1••••••12', phoneMasked: '0909•••095', emailMasked: 'red•••@gmail.com',
    },
    people: [
      { role: '爸爸', name: '張國純', englishName: 'KUOCHUN CHANG', birth: '1961-06-01', rocBirth: '民國 50-06-01', idMasked: 'Y1••••••18' },
      { role: '媽媽', name: '林瑜雯', englishName: 'YUWEN LIN', birth: '1969-02-01', rocBirth: '民國 58-02-01', idMasked: 'V2••••••23' },
      { role: '本人／刷卡人', name: '張辰瑋', englishName: 'CHEN WEI CHANG', birth: '1995-10-19', rocBirth: '民國 84-10-19', idMasked: 'A1••••••12' },
    ] satisfies TravelInsurancePerson[],
    flights: [
      { label: '三人共同出發', flight: '酷航 TR875', route: 'TPE T1 → SIN T1', time: '07/17 00:55 → 05:20' },
      { label: '爸媽回程', flight: '泰國越捷 VZ566', route: 'BKK → TPE T1', time: '07/24 01:45 → 06:35' },
      { label: '張辰瑋回程', flight: '泰國越捷 VZ566', route: 'BKK → TPE T1', time: '07/30 01:35 → 06:25' },
    ],
  },
  costs: {
    travelers: 3,
    flightTotalTwd: 48422,
    hotelTotalTwd: 11688,
    fixedTotalTwd: 60110,
    localBudgetMinTwd: 52000,
    localBudgetMaxTwd: 72000,
    projectedMinTwd: 112110,
    projectedMaxTwd: 132110,
    items: [
      { label: '機票｜CHEN WEI CHANG', totalTwd: 17878, perPersonTwd: 17878, detail: '1 成人；INEB 結束後於 07/30 01:35 返台' },
      { label: '機票｜爸媽', totalTwd: 30544, perPersonTwd: 15272, detail: '2 成人；07/24 01:45 返台' },
      { label: '新加坡飯店', totalTwd: 2978, perPersonTwd: 993, detail: 'ibis budget Singapore Crystal，1 晚' },
      { label: '吉隆坡飯店', totalTwd: 4588, perPersonTwd: 1529, detail: 'WP Hotel，3 晚' },
      { label: '曼谷飯店', totalTwd: 4122, perPersonTwd: 1374, detail: 'The Twin Towers Hotel Bangkok，2 晚' },
    ] satisfies TravelCostItem[],
  },
  movieSpots: [
    {
      city: '新加坡', work: '《名偵探柯南：紺青之拳》', location: '魚尾獅公園＋濱海灣金沙',
      day: 'Day 1', status: '主行程', photoTip: '在魚尾獅側面取景，讓噴泉、金沙三塔與灣區一起入鏡。',
      mapQuery: 'Merlion Park Singapore', href: 'https://conan-map.com/en/spots/dc6f72',
    },
    {
      city: '新加坡', work: '《名偵探柯南：紺青之拳》', location: '濱海灣花園＋新加坡摩天輪＋財富之泉',
      day: 'Day 1', status: '主行程', photoTip: '傍晚拍擎天樹，入夜後補摩天輪及財富之泉；三處都在原本路線上。',
      mapQuery: 'Fountain of Wealth Singapore', href: 'https://asean.or.jp.yucca-works.jp/en/wp-content/uploads/sites/3/20200323_Press-Release_ASEAN_tourism_awardPR.pdf',
    },
    {
      city: '新加坡', work: '《瘋狂亞洲富豪》', location: 'CHIJMES',
      day: 'Day 1', status: '順路短停', photoTip: '亞洲文明博物館往午餐途中繞到白色歌德式禮拜堂外觀，停留約 15–20 分鐘。',
      mapQuery: 'CHIJMES Singapore', href: 'https://www.visitsingapore.com/see-do-singapore/architecture/historical/chijmes/',
    },
    {
      city: '吉隆坡', work: '《偷天陷阱 Entrapment》', location: '國油雙子塔',
      day: 'Day 3／4', status: '主行程', photoTip: '從 KLCC Park 低角度拍雙塔與天橋，傍晚和夜景各拍一組。',
      mapQuery: 'Petronas Twin Towers', href: 'https://www.tatlerasia.com/lifestyle/travel/merdeka-118-blue-mansion-malaysian-destinations-in-international-films',
    },
    {
      city: '吉隆坡', work: '《警察故事3：超級警察》', location: '蘇丹阿都沙末大廈／獨立廣場',
      day: 'Day 4', status: '主行程', photoTip: '站在獨立廣場草地側拍整排摩爾式立面與鐘樓。',
      mapQuery: 'Sultan Abdul Samad Building', href: 'https://www.tatlerasia.com/lifestyle/travel/merdeka-118-blue-mansion-malaysian-destinations-in-international-films',
    },
    {
      city: '吉隆坡', work: '《瘋狂亞洲富豪》', location: 'Carcosa Seri Negara',
      day: 'Day 4', status: '備選', photoTip: '只建議在伊斯蘭藝術博物館附近順路看外觀；建築可能不開放，出發前再確認。',
      mapQuery: 'Carcosa Seri Negara', href: 'https://www.tatlerasia.com/lifestyle/travel/merdeka-118-blue-mansion-malaysian-destinations-in-international-films',
    },
    {
      city: '曼谷', work: '《醉後大丈夫2》', location: '昭披耶河＋Lebua State Tower 外觀',
      day: 'Day 6', status: '順路短停', photoTip: '搭船或到 Asiatique 時找金色圓頂入鏡；不必進高空酒吧，也較適合家庭節奏。',
      mapQuery: 'Lebua at State Tower Bangkok', href: 'https://filmthailand.org/locations/streets-and-roads/',
    },
    {
      city: '曼谷', work: '《海灘 The Beach》／《醉後大丈夫2》', location: '考山路 Khao San Road',
      day: 'Day 6', status: '備選', photoTip: '若跳過 Museum Siam 才加排；大皇宮搭車約 10–20 分，白天拍招牌即可。',
      mapQuery: 'Khao San Road Bangkok', href: 'https://filmthailand.org/locations/streets-and-roads/',
    },
  ] satisfies TravelMovieSpot[],
  friendRecommendations: [
    {
      place: 'Asiatique 河濱夜市', status: '原本已有', timing: 'Day 6｜07/22 17:15–20:30',
      detail: '鄭王廟後前往河岸，安排昭披耶河景、晚餐與夜市散步。',
      tradeoff: '不需要再挪動行程。', mapQuery: 'Asiatique The Riverfront Bangkok',
      href: 'https://www.asiatiquethailand.com/',
    },
    {
      place: 'Song Wat Road 宋越路', status: '已排入', timing: 'Day 7｜07/23 12:10–13:20',
      detail: '百年華人商業街、老店屋、倉庫、街頭藝術與新咖啡店；改成當天午餐與歷史街區短停。',
      tradeoff: '不列為大型景點，停留約 70 分鐘，保留原本 Terminal 21 與 Big C。', mapQuery: 'Song Wat Road Bangkok',
      href: 'https://www.songwat.net/',
    },
    {
      place: 'Ancient City 暹羅古城（Muang Boran）', status: '半日備選', timing: '至少 5–7 小時',
      detail: '位於 Samut Prakan 的大型戶外建築文化博物館；09:00–19:00，外國成人 700 THB，三人門票 2,100 THB。',
      tradeoff: '市中心單程約 1–1.5 小時，不能當作順路短停；若一定要去，需用它替換 Day 7 的 Jim Thompson House、Terminal 21 與 Big C。',
      mapQuery: 'Muang Boran Ancient City Samut Prakan', href: 'https://www.muangboran.co.th/en/',
    },
  ] satisfies TravelFriendRecommendation[],
  inebProgram: {
    titleZh: '危機中的菩薩：學習建構包容社會',
    titleEn: 'Bodhisattva in Crisis: Learning to Build an Inclusive Society',
    subtitleZh: '參與佛教：泰國學習之旅｜INEB × 弘誓佛學院國際青年菩薩培育計畫',
    subtitleEn: 'Engaged Buddhism: Learning Journey in Thailand | INEB × HongShi Buddhist College International Young Bodhisattva Program',
    dateLabel: '2026.07.24 — 07.30',
    sourceUrl: 'https://docs.google.com/document/d/1dGIhbxp6bSk_wBWW3gY0TrwCmDXgxWFC/edit',
    summaryZh: '以佛教觀點探討性別正義、女性與 LGBTQ+ 社群、僧侶及草根行動者的社會參與，也透過生態寺院、政治生態與實作課程理解環境及生態生活。預計 10–20 人參與。',
    summaryEn: 'A learning journey on gender justice from Buddhist perspectives, women and LGBTQ+ communities, monastics and grassroots activists, together with eco-temples, political ecology and hands-on ecological living. The program expects 10–20 participants.',
    accommodationZh: '全程與室友同住。INEB Office：一房兩張單人床，公共全性別衛浴；Wongsanit Ashram：一房兩張單人床，兩房共用一間大型全性別衛浴。',
    accommodationEn: 'A roommate is assigned throughout. INEB Office: one room with two single beds and a shared all-gender bathroom/shower. Wongsanit Ashram: one room with two single beds; two rooms share one large all-gender bathroom/shower.',
    costZh: '文件估算總額約 NT$14,000，其中 NT$8,000 為 INEB 課程費（接駁、4 晚 INEB Office、餐費補助、Wongsanit Ashram 2 晚與餐食），約 NT$6,000 為來回機票估算。你的多城市機票已另行實付並列入原訂單，這 NT$6,000 不可再加一次。',
    costEn: 'The document estimates about NT$14,000: NT$8,000 for the INEB program (transfers, four nights at the INEB Office, food allowance, and two nights with meals at Wongsanit Ashram) plus about NT$6,000 for round-trip airfare. Your actual multi-city ticket is already paid and recorded, so the NT$6,000 airfare estimate must not be counted again.',
    notices: [
      {
        level: 'duplicate',
        titleZh: '重複景點｜曼谷大皇宮',
        titleEn: 'Repeated place | The Grand Palace',
        detailZh: '家庭行程已於 7/22 08:30–11:30 參觀，INEB 又安排 7/27 08:00–12:00。這是唯一完全重複的大型景點；第二次屬團體學習，建議保留並以不同導覽脈絡參與。',
        detailEn: 'The family itinerary visits on 22 July, 08:30–11:30, and INEB visits again on 27 July, 08:00–12:00. This is the only exact repeat among the major attractions. Keep the second visit for its group-learning context.',
      },
      {
        level: 'conflict',
        titleZh: '時間衝突｜7/30 離營與 01:35 航班',
        titleEn: 'Schedule conflict | 30 July departure vs. 01:35 flight',
        detailZh: '課表寫 7/30 07:00 早餐、08:00 起離營，但 VZ566 在 7/30 01:35 起飛。規劃在 7/29 金山寺儀式 19:00 結束後直接離隊，晚餐改到 BKK 機場吃；並先向主辦方確認行李、接駁起點及叫車安排。',
        detailEn: 'The program lists breakfast at 07:00 and departure from 08:00 on 30 July, but VZ566 leaves at 01:35. Plan to leave directly after the Golden Mount ceremony ends at 19:00 on 29 July and have dinner at BKK; confirm luggage, the pickup point and transport with the organizer in advance.',
      },
      {
        level: 'budget',
        titleZh: '費用提醒｜機票估算勿重複計算',
        titleEn: 'Budget note | Do not double-count airfare',
        detailZh: '另加到個人行程預算的基準是 NT$8,000 課程費與未涵蓋的個人支出；文件中的 NT$6,000 僅是一般來回機票估算。',
        detailEn: 'Add the NT$8,000 program fee and uncovered personal expenses to the personal-phase budget. The document\'s NT$6,000 is only a generic airfare estimate.',
      },
    ] satisfies TravelProgramNotice[],
    days: [
      {
        date: '07/24', weekdayZh: '星期五', weekdayEn: 'Friday',
        themeZh: '抵達與報到', themeEn: 'Arrival Day', locationZh: 'INEB Office', locationEn: 'INEB Office',
        items: [
          { time: '08:00–17:00', zh: '參與者抵達與報到', en: 'Participants arrive and register' },
          { time: '18:00–19:00', zh: '晚餐', en: 'Dinner' },
          { time: '19:30–21:00', zh: '課程導入與說明', en: 'Program Orientation' },
        ],
        personalNoteZh: '送爸媽搭機後銜接報到；自己的入住、行李寄放及機場到 INEB 交通須和主辦方確認。',
        personalNoteEn: 'After seeing your parents off, continue to registration. Confirm check-in, luggage storage and the transfer from BKK to INEB with the organizer.',
      },
      {
        date: '07/25', weekdayZh: '星期六', weekdayEn: 'Saturday',
        themeZh: '社群建立與曼谷彩虹僧伽', themeEn: 'Community Building and Rainbow Sangha Bangkok', locationZh: 'INEB Office', locationEn: 'INEB Office',
        items: [
          { time: '07:00–08:45', zh: '早餐', en: 'Breakfast' },
          { time: '08:45–09:00', zh: '社群晨間報到', en: 'Community Check-In' },
          { time: '09:00–10:30', zh: '社群建立', en: 'Community Building' },
          { time: '10:30–10:45', zh: '休息', en: 'Break' },
          { time: '10:45–12:00', zh: '認識內在自我', en: 'Knowing Inner-Self' },
          { time: '12:00–13:30', zh: '午餐', en: 'Lunch' },
          { time: '13:30–14:00', zh: '深度放鬆', en: 'Deep Relaxation' },
          { time: '14:00–17:00', zh: '午後交流：曼谷彩虹僧伽團體', en: 'Afternoon Exchange: Rainbow Sangha Bangkok Group' },
          { time: '17:00–22:00', zh: '晚餐與自由時間', en: 'Dinner and Free Time' },
          { time: '22:00–', zh: '神聖靜默與休息', en: 'Noble Silence and Rest' },
        ],
      },
      {
        date: '07/26', weekdayZh: '星期日', weekdayEn: 'Sunday',
        themeZh: '權力分析工作坊', themeEn: 'Power Analysis Workshop', locationZh: 'INEB Office｜講師 Hua Boonyapisomparn', locationEn: 'INEB Office | Facilitator: Hua Boonyapisomparn',
        items: [
          { time: '07:00–08:45', zh: '早餐', en: 'Breakfast' },
          { time: '08:45–09:00', zh: '社群晨間報到', en: 'Community Check-In' },
          { time: '09:00–10:30', zh: '權力分析（一）', en: 'Power Analysis, Part 1' },
          { time: '10:30–10:45', zh: '休息', en: 'Break' },
          { time: '10:45–12:00', zh: '權力分析（二）', en: 'Power Analysis, Part 2' },
          { time: '12:00–13:30', zh: '午餐', en: 'Lunch' },
          { time: '13:30–14:00', zh: '深度放鬆', en: 'Deep Relaxation' },
          { time: '14:00–17:00', zh: '權力分析（三）', en: 'Power Analysis, Part 3' },
          { time: '17:00–22:00', zh: '晚餐與自由時間', en: 'Dinner and Free Time' },
          { time: '22:00–', zh: '神聖靜默與休息', en: 'Noble Silence and Rest' },
        ],
      },
      {
        date: '07/27', weekdayZh: '星期一', weekdayEn: 'Monday',
        themeZh: '生態寺院參訪', themeEn: 'Eco-Temple Site Visits', locationZh: '曼谷 → Wongsanit Ashram', locationEn: 'Bangkok → Wongsanit Ashram',
        items: [
          { time: '08:00–12:00', zh: '上午參訪：曼谷大皇宮（與 7/22 家庭行程重複）', en: 'Morning Visit: The Grand Palace (repeats the family visit on 22 July)' },
          { time: '12:00–13:00', zh: '午餐', en: 'Lunch' },
          { time: '13:00–15:00', zh: '午後參訪：Santi Asoke', en: 'Afternoon Visit: Santi Asoke' },
          { time: '15:00–17:00', zh: '前往 Wongsanit Ashram', en: 'Travel to Wongsanit Ashram' },
          { time: '18:00–19:00', zh: '晚餐', en: 'Dinner' },
          { time: '19:00–22:00', zh: '自由時間', en: 'Free Time' },
          { time: '22:00–', zh: '神聖靜默與休息', en: 'Noble Silence and Rest' },
        ],
      },
      {
        date: '07/28', weekdayZh: '星期二', weekdayEn: 'Tuesday',
        themeZh: '生態寺院學習與實作', themeEn: 'Eco-Temple Learning and Practice', locationZh: 'Wongsanit Ashram', locationEn: 'Wongsanit Ashram',
        items: [
          { time: '07:00–08:45', zh: '早餐', en: 'Breakfast' },
          { time: '08:45–09:00', zh: '社群晨間報到', en: 'Community Check-In' },
          { time: '09:00–10:30', zh: '生態寺院概念與模式', en: 'Eco Temple Concept and Models' },
          { time: '10:30–10:45', zh: '休息', en: 'Break' },
          { time: '10:45–12:00', zh: '政治生態學', en: 'Political Ecology' },
          { time: '12:00–13:30', zh: '午餐', en: 'Lunch' },
          { time: '13:30–14:00', zh: '深度放鬆', en: 'Deep Relaxation' },
          { time: '14:00–17:00', zh: '實作工作坊：天然染色與泥屋彩繪', en: 'Hands-On Workshop: Natural Dye and Mud House Painting' },
          { time: '17:00–22:00', zh: '晚餐與自由時間（草藥桑拿開放）', en: 'Dinner and Free Time (Herbal Sauna Open)' },
          { time: '22:00–', zh: '神聖靜默與休息', en: 'Noble Silence and Rest' },
        ],
      },
      {
        date: '07/29', weekdayZh: '星期三', weekdayEn: 'Wednesday',
        themeZh: '最終反思、蘇拉克老師問答與金山寺滿月儀式', themeEn: 'Final Reflection, Q&A with Ajahn Sulak and Full Moon Ceremony', locationZh: 'Wongsanit Ashram → INEB Office／金山寺', locationEn: 'Wongsanit Ashram → INEB Office / Golden Mount',
        items: [
          { time: '07:00–08:30', zh: '早餐與整理行李', en: 'Breakfast and Packing' },
          { time: '08:30–10:30', zh: '返回 Ajahn Sulak House', en: 'Travel back to Ajahn Sulak House' },
          { time: '10:30–12:00', zh: '與 Ajahn Sulak 問答', en: 'Q&A with Ajahn Sulak' },
          { time: '12:00–13:30', zh: '午餐', en: 'Lunch' },
          { time: '13:30–14:00', zh: '深度放鬆', en: 'Deep Relaxation' },
          { time: '14:00–16:00', zh: '反思與評估', en: 'Reflection and Evaluation' },
          { time: '16:00–16:45', zh: '前往金山寺（Wat Saket／Golden Mount）', en: 'Travel to Wat Saket Ratchawora Mahawihan (Golden Mount)' },
          { time: '17:00–19:00', zh: '金山寺夕陽與滿月儀式', en: 'Sunset and Full Moon Ceremony at Golden Mount' },
          { time: '19:00', zh: '你的個人安排：離營前往 BKK，晚餐改在機場', en: 'Your plan: leave for BKK and have dinner at the airport' },
          { time: '19:00–22:00', zh: '課表原訂晚餐與自由時間（你不參加）', en: 'Scheduled Dinner and Free Time (you will not attend)' },
          { time: '22:00–', zh: '神聖靜默與休息', en: 'Noble Silence and Rest' },
        ],
        personalNoteZh: '你的班機是 7/30 01:35；規劃 7/29 19:00 儀式結束就離營，晚餐在機場解決。目標不晚於 22:35 抵達，實際叫車時間仍須由主辦方依行李位置、集合點與車程確認。',
        personalNoteEn: 'Your flight departs at 01:35 on 30 July. Leave when the ceremony ends at 19:00 on 29 July and eat at the airport. Reach BKK no later than about 22:35; the organizer still needs to confirm luggage access, pickup point and travel time.',
      },
      {
        date: '07/30', weekdayZh: '星期四', weekdayEn: 'Thursday',
        themeZh: '離營日（你已在凌晨返台）', themeEn: 'Departure Day (you depart overnight)', locationZh: 'INEB Office／BKK → TPE', locationEn: 'INEB Office / BKK → TPE',
        items: [
          { time: '01:35–06:25', zh: '你的 VZ566：曼谷 BKK → 桃園 TPE T1', en: 'Your VZ566 flight: Bangkok BKK → Taipei TPE Terminal 1' },
          { time: '07:00–08:00', zh: '課表原訂早餐（你無法參加）', en: 'Scheduled breakfast (you cannot attend)' },
          { time: '08:00–全日', zh: '課表原訂參與者離營', en: 'Scheduled participant departures throughout the day' },
        ],
        personalNoteZh: '請在 7/24 報到時主動說明提早離營，避免最後一晚住宿、門禁與送機資訊落差。',
        personalNoteEn: 'Tell the organizer about your early departure during registration on 24 July to avoid problems with the final night, access and airport transfer.',
      },
    ] satisfies TravelProgramDay[],
  },
  days: [
    {
      date: '07/17', weekday: '星期五', city: '新加坡', country: 'Singapore', flag: '🇸🇬',
      theme: '柯南聖地巡禮＋亞洲文明', accent: 'emerald',
      highlights: ['亞洲文明博物館', '魚尾獅＋金沙', '濱海灣花園', '摩天輪＋財富之泉'],
      budgetTwd: 'NT$13,000–17,000／三人',
      activities: [
        { time: '05:20', title: '抵達樟宜機場 T1', detail: '入境、領行李；全家行李多可直接搭 Grab，較省轉乘與步行。', kind: 'flight' },
        { time: '07:30', title: '飯店寄放行李、Geylang 早餐', detail: '紅眼航班後保留緩衝，不急著塞景點。', kind: 'hotel', mapQuery: 'ibis budget Singapore Crystal' },
        { time: '10:00', title: '亞洲文明博物館', detail: '從亞洲宗教藝術與海上交流理解新加坡；Raffles Place 站步行約 5–10 分鐘。', kind: 'sight', mapQuery: 'Asian Civilisations Museum' },
        { time: '11:50', title: 'CHIJMES 電影場景短停', detail: '《瘋狂亞洲富豪》婚禮場景；只拍禮拜堂外觀，停留 15–20 分鐘。', kind: 'sight', mapQuery: 'CHIJMES Singapore' },
        { time: '12:20', title: '午餐｜National Kitchen by Violet Oon', detail: '位於 National Gallery 歷史建築內的新加坡／娘惹料理，建議訂位。', kind: 'food', mapQuery: 'National Kitchen by Violet Oon' },
        { time: '13:50', title: '魚尾獅公園＋濱海灣金沙', detail: '《紺青之拳》核心場景；沿灣步行拍魚尾獅、金沙與 Helix Bridge 視角。', kind: 'sight', mapQuery: 'Merlion Park Singapore' },
        { time: '15:30', title: '回飯店入住、休息', detail: '保留約 1.5 小時恢復體力，再出發看傍晚景色。', kind: 'hotel' },
        { time: '17:15', title: '濱海灣花園', detail: '先走戶外花園及擎天樹；若要進冷室，需另加 1.5–2 小時與票價。', kind: 'sight', mapQuery: 'Gardens by the Bay Singapore' },
        { time: '19:30', title: '新加坡摩天觀景輪', detail: '拍《紺青之拳》灣區夜景；預留排隊與一圈約 30 分鐘。', kind: 'sight', mapQuery: 'Singapore Flyer' },
        { time: '20:40', title: '晚餐｜PUTIEN Suntec City', detail: '福建莆田菜，三人方便分食；飯後步行到財富之泉。', kind: 'food', mapQuery: 'PUTIEN Suntec City' },
        { time: '21:45', title: '財富之泉拍照 → 回飯店', detail: '完成柯南一日巡禮；體力不足時可直接從晚餐地點叫 Grab 回飯店。', kind: 'sight', mapQuery: 'Fountain of Wealth Singapore' },
      ],
      transport: ['機場 → 飯店：Grab；若行李少可搭 MRT', '飯店 → 市中心：Aljunied MRT → Raffles Place', '博物館 → CHIJMES → 午餐：步行＋短程 Grab', '濱海灣傍晚路線：Grab＋步行；晚間回程 Grab'],
      reminder: '第一天是紅眼航班後的長日；15:30 的飯店休息不可省。若延誤，優先保留柯南場景，博物館可縮短。',
    },
    {
      date: '07/18', weekday: '星期六', city: '新加坡 → 吉隆坡', country: 'Singapore / Malaysia', flag: '🇸🇬 🇲🇾',
      theme: 'Jewel 與移動日', accent: 'amber', highlights: ['Jewel Changi'], budgetTwd: 'NT$8,000–11,000／三人',
      activities: [
        { time: '08:30', title: '早餐、整理行李', detail: '睡飽後在飯店周邊簡單活動，不再安排遠距離景點。', kind: 'food' },
        { time: '11:00', title: '退房前往樟宜機場', detail: 'MRT 原路返回或全家搭 Grab；目標 12:15–12:30 抵達。', kind: 'transfer' },
        { time: '12:15', title: 'Jewel 雨漩渦＋午餐', detail: '午餐選 JUMBO Seafood Jewel，建議訂位；13:20 前前往 T1 報到。', kind: 'sight', mapQuery: 'Jewel Changi Airport' },
        { time: '16:00', title: 'TR472 飛往吉隆坡', detail: '17:25 抵達吉隆坡國際機場 T2。', kind: 'flight' },
        { time: '18:30', title: 'KLIA Ekspres → KL Sentral', detail: '直達約 33 分鐘；查看 3 成人 Group Saver 當期票價。', kind: 'transfer' },
        { time: '19:30', title: 'Grab 前往 WP Hotel', detail: '入住後就近吃 Restoran Kudu nasi kandar；太累就改飯店附近簡餐。', kind: 'hotel', mapQuery: 'WP Hotel Kuala Lumpur' },
      ],
      transport: ['飯店 → 樟宜：MRT 或 Grab', '酷航 TR472', 'KLIA T2 → KL Sentral：KLIA Ekspres', 'KL Sentral → WP Hotel：Grab'],
      reminder: '16:00 起飛，建議最晚 13:20 離開 Jewel 前往 T1 報到。',
    },
    {
      date: '07/19', weekday: '星期日', city: '吉隆坡', country: 'Malaysia', flag: '🇲🇾',
      theme: '宗教建築包車團＋雙子塔電影場景', accent: 'amber',
      highlights: ['黑風洞', '粉紅清真寺＋布城', '雙子塔夜景'], budgetTwd: 'NT$5,000–7,000／三人',
      activities: [
        { time: '08:00', title: 'Trip.com 獨立包車團出發', detail: '保留原規劃的黑風洞＋粉紅清真寺團；下訂前確認 3 成人、中文司機、飯店接送、8 小時、過路費與停車費。', kind: 'transfer' },
        { time: '08:45', title: '黑風洞 Batu Caves', detail: '早上先走階梯避開高溫；穿止滑鞋，留意猴群及隨身物。', kind: 'sight', mapQuery: 'Batu Caves Malaysia' },
        { time: '11:45', title: '布特拉清真寺（粉紅清真寺）', detail: '非穆斯林時段可能因禮拜調整；服裝遮肩、過膝，現場通常可借罩袍。', kind: 'sight', mapQuery: 'Putra Mosque Putrajaya' },
        { time: '13:00', title: '午餐｜Umai Cafe Putrajaya', detail: '湖畔本地料理，靠近清真寺與布城行政區。', kind: 'food', mapQuery: 'Umai Cafe Putrajaya' },
        { time: '14:15', title: '布城行政建築＋湖區短停', detail: '與清真寺合成同一組，不另加遠距離景點。', kind: 'sight', mapQuery: 'Perdana Putra Putrajaya' },
        { time: '16:30', title: '返回飯店休息', detail: '保留塞車緩衝，晚間再出發。', kind: 'hotel' },
        { time: '18:30', title: '雙子塔／KLCC 電影夜景', detail: '《偷天陷阱》代表性地標；從 KLCC Park 拍雙塔與天橋。', kind: 'sight', mapQuery: 'Petronas Twin Towers' },
        { time: '19:30', title: '晚餐｜Madam Kwan’s Suria KLCC', detail: '品嘗 nasi lemak、rendang 等馬來西亞代表料理。', kind: 'food', mapQuery: 'Madam Kwans Suria KLCC' },
      ],
      transport: ['08:00–16:30：Trip.com 私人包車團', '飯店 ↔ KLCC：Grab', 'KLCC 區內：步行'],
      reminder: '包車頁面僅顯示起價；三人私人車實價要進入日期與車型選項確認後才下訂。',
    },
    {
      date: '07/20', weekday: '星期一', city: '吉隆坡', country: 'Malaysia', flag: '🇲🇾',
      theme: '伊斯蘭藝術、華人舊城與電影地標', accent: 'amber',
      highlights: ['伊斯蘭藝術博物館', 'REXKL＋茨廠街', '獨立廣場', 'KLCC'], budgetTwd: 'NT$5,000–7,000／三人',
      activities: [
        { time: '09:30', title: '伊斯蘭藝術博物館', detail: '東南亞重要伊斯蘭藝術收藏；從飯店搭 Grab 最順。', kind: 'sight', mapQuery: 'Islamic Arts Museum Malaysia' },
        { time: '11:40', title: 'Carcosa Seri Negara 外觀備選', detail: '《瘋狂亞洲富豪》場景；只在確認可接近且不影響午餐時順路短停。', kind: 'free', mapQuery: 'Carcosa Seri Negara' },
        { time: '12:15', title: '午餐｜Old China Cafe', detail: '老會館空間中的娘惹與馬來菜，也帶有吉隆坡華人移民史氛圍。', kind: 'food', mapQuery: 'Old China Cafe Kuala Lumpur' },
        { time: '13:30', title: 'REXKL＋茨廠街／中央市場', detail: '保留原規劃的迷宮書店，把周邊歷史街區合成同一組。', kind: 'sight', mapQuery: 'BookXcess RexKL' },
        { time: '15:50', title: '獨立廣場＋蘇丹阿都沙末大廈', detail: '《警察故事3》電影場景；從草地側拍摩爾式立面與鐘樓。', kind: 'sight', mapQuery: 'Sultan Abdul Samad Building' },
        { time: '17:20', title: '雙子塔與 KLCC 公園', detail: '補拍白天／藍調時刻；若要登塔，須另預約並刪減前一站。', kind: 'sight', mapQuery: 'Petronas Twin Towers' },
        { time: '19:30', title: '晚餐｜Bijan Bar & Restaurant', detail: '精緻馬來料理，建議訂位；從 KLCC 搭 Grab 約 10–20 分。', kind: 'food', mapQuery: 'Bijan Bar Restaurant Kuala Lumpur' },
      ],
      transport: ['飯店 → 博物館：Grab', '博物館 → 舊城：Grab', 'REXKL → 獨立廣場：步行／短程 Grab', '獨立廣場 → KLCC → 晚餐：Grab'],
      reminder: 'Carcosa Seri Negara 不保證開放，因此只列備選；今天仍以四組主景點為上限。',
    },
    {
      date: '07/21', weekday: '星期二', city: '吉隆坡 → 曼谷', country: 'Malaysia / Thailand', flag: '🇲🇾 🇹🇭',
      theme: '飛行與入住', accent: 'rose', highlights: [], budgetTwd: 'NT$4,000–6,000／三人',
      activities: [
        { time: '08:30', title: '早餐、收拾行李', detail: '確認 TDAC QR code、MH774 航班與吉隆坡機場 T1。', kind: 'free' },
        { time: '11:15', title: '退房前往 KL Sentral', detail: '飯店搭 Grab，保留市區塞車與找月台時間。', kind: 'transfer' },
        { time: '12:00', title: 'KLIA Ekspres → KLIA T1', detail: '抵達後完成報到，再到 Oriental Kopi KLIA T1 午餐。', kind: 'transfer' },
        { time: '16:00', title: 'MH774 飛往曼谷', detail: '17:20 抵達素萬那普機場。', kind: 'flight' },
        { time: '18:30', title: '前往雙子塔飯店', detail: '行李少可搭 Airport Rail Link 到 Phaya Thai 再 Grab；行李多直接叫車。', kind: 'transfer' },
        { time: '20:15', title: '晚餐｜Somboon Seafood Bantadthong', detail: '飯店附近的泰式海鮮與咖哩螃蟹，適合三人分食。', kind: 'food', mapQuery: 'Somboon Seafood Bantadthong' },
      ],
      transport: ['WP Hotel → KL Sentral：Grab', 'KLIA Ekspres', '馬航 MH774', 'BKK → 飯店：Airport Rail Link＋Grab 或直接叫車'],
      reminder: '純移動日，不再加景點；曼谷晚間塞車需保留 60–90 分鐘。',
    },
    {
      date: '07/22', weekday: '星期三', city: '曼谷', country: 'Thailand', flag: '🇹🇭',
      theme: '王室佛教、泰國文化與河岸電影場景', accent: 'rose',
      highlights: ['大皇宮＋玉佛寺', 'Museum Siam', '鄭王廟', 'Asiatique'], budgetTwd: 'NT$7,000–9,000／三人',
      activities: [
        { time: '07:45', title: '飯店出發', detail: 'Grab／計程車直達大皇宮，避開中午高溫與團客高峰。', kind: 'transfer' },
        { time: '08:30', title: '曼谷大皇宮＋玉佛寺', detail: '穿長褲／長裙並遮肩；王室活動可能臨時調整開放。', kind: 'sight', mapQuery: 'The Grand Palace Bangkok' },
        { time: '11:45', title: '午餐｜Supanniga Eating Room Tha Tien', detail: '泰國家常菜與鄭王廟河景，強烈建議訂位。', kind: 'food', mapQuery: 'Supanniga Eating Room Tha Tien' },
        { time: '13:15', title: 'Museum Siam', detail: '互動展理解「泰國性」與暹羅歷史；週一休館，本日可排。', kind: 'sight', mapQuery: 'Museum Siam Bangkok' },
        { time: '14:50', title: '渡輪前往鄭王廟', detail: '由 Tha Tien 搭短程跨河船，依現場碼頭標示為準。', kind: 'transfer' },
        { time: '15:05', title: '鄭王廟 Wat Arun', detail: '石階較陡，午後炎熱要補水；拍攝河岸與佛塔。', kind: 'sight', mapQuery: 'Wat Arun Bangkok' },
        { time: '17:15', title: '昭披耶河電影景觀 → Asiatique', detail: '途中找 Lebua 金色圓頂入鏡，作為《醉後大丈夫2》順路短停，不進高空酒吧。', kind: 'sight', mapQuery: 'Asiatique The Riverfront Bangkok' },
        { time: '18:30', title: '晚餐｜Baan Khanitha by the River', detail: 'Asiatique 河畔傳統泰菜，建議訂位。', kind: 'food', mapQuery: 'Baan Khanitha by the River' },
      ],
      transport: ['飯店 → 大皇宮：Grab', '舊城區：步行＋Tha Tien 渡輪', '鄭王廟 → Asiatique：Grab；若水路班次合適再改船', 'Asiatique → 飯店：Grab'],
      reminder: '考山路只列備選；若一定要拍《海灘》，就刪掉 Museum Siam，不把兩者都硬塞。',
    },
    {
      date: '07/23', weekday: '星期四', city: '曼谷', country: 'Thailand', flag: '🇹🇭',
      theme: '絲綢文化、印度廟與採買', accent: 'rose',
      highlights: ['Jim Thompson House', '馬里安曼興都廟', 'Terminal 21', 'Big C'], budgetTwd: 'NT$5,500–8,000／三人（不含購物）',
      activities: [
        { time: '09:00', title: '退房、寄放行李', detail: '護照、貴重物品與登機用品隨身攜帶。', kind: 'hotel' },
        { time: '10:00', title: 'Jim Thompson House Museum', detail: '泰式傳統住宅、東南亞藝術與絲綢史；主屋需跟導覽。', kind: 'sight', mapQuery: 'Jim Thompson House Museum' },
        { time: '12:10', title: 'Song Wat Road 歷史街區＋午餐', detail: '朋友推薦的新興文化街區；走百年店屋、舊倉庫與街頭藝術，午餐依現場候位選老店或咖啡店。', kind: 'sight', mapQuery: 'Song Wat Road Bangkok' },
        { time: '13:45', title: '馬里安曼興都廟', detail: '從 Song Wat 搭 Grab 前往 Silom；尊重現場儀式與攝影規定。', kind: 'sight', mapQuery: 'Sri Maha Mariamman Temple Bangkok' },
        { time: '14:40', title: 'Terminal 21 Asok', detail: '短程 Grab 或前往 BTS 後到 Asok，逛街、休息並補充飲水。', kind: 'sight', mapQuery: 'Terminal 21 Asok' },
        { time: '17:00', title: 'Big C Ratchadamri 採買', detail: '注意托運重量與液體限制。', kind: 'sight', mapQuery: 'Big C Supercenter Ratchadamri' },
        { time: '18:30', title: '晚餐｜Nara Thai Cuisine CentralWorld', detail: 'Big C 對面商圈，適合家庭分享泰菜。', kind: 'food', mapQuery: 'Nara Thai Cuisine CentralWorld' },
        { time: '20:00', title: '回飯店取行李', detail: '重新整理托運／手提行李，預留洗漱與叫車時間。', kind: 'hotel' },
        { time: '21:15', title: '陪爸媽前往素萬那普機場', detail: '爸媽搭 07/24 01:45 班機；建議約 22:15 抵達。送機後銜接自己的 INEB 安排。', kind: 'transfer' },
      ],
      transport: ['Jim Thompson House → Song Wat → Silom：Grab', 'Silom → Asok → Chit Lom：BTS', '飯店 → BKK：Grab／排班計程車'],
      reminder: '回程分流已確認：爸媽先返台，CHEN WEI CHANG 留在曼谷參加 INEB。',
    },
    {
      date: '07/24', weekday: '星期五', city: '曼谷 → 台北', country: 'Thailand / Taiwan', flag: '🇹🇭 🇹🇼',
      theme: '爸媽返台；INEB 行程交接', accent: 'slate', highlights: [], budgetTwd: '已含於前一日交通預算',
      activities: [
        { time: '01:45', title: '爸媽搭 VZ566 起飛', detail: '07/24 06:35 抵達桃園機場 T1。', kind: 'flight' },
        { time: '08:00–17:00', title: 'CHEN WEI CHANG 銜接 INEB 報到', detail: '家庭旅遊在此交接至個人行程；完整中英對照課表接在本頁家庭行程後方。', kind: 'free' },
        { time: '07/30 01:35', title: 'CHEN WEI CHANG 返台', detail: 'VZ566 於 06:25 抵達桃園 T1；須在 7/29 晚間提早離開活動前往 BKK。', kind: 'flight' },
      ],
      transport: ['爸媽：泰國越捷 VZ566 → 桃園', 'CHEN WEI CHANG：機場 → INEB 活動地點（依主辦方接駁）'],
      reminder: 'INEB 為個人第二階段，不計入家庭旅行的 NT$52,000–72,000 當地預算；課程費與課表另列於後方中英對照區。',
    },
  ] satisfies TravelDay[],
  officialLinks: [
    { label: '新加坡 SG Arrival Card', href: 'https://www.ica.gov.sg/enter-transit-depart/entering-singapore/sg-arrival-card' },
    { label: '樟宜機場交通', href: 'https://www.changiairport.com/en/at-changi/transport-and-directions.html' },
    { label: 'KLIA Ekspres 票價', href: 'https://www.kliaekspres.com/products-fares/klia-ekspres/' },
    { label: '馬來西亞 MDAC', href: 'https://imigresen-online.imi.gov.my/mdac/main' },
    { label: '泰國 TDAC', href: 'https://tdac.immigration.go.th/' },
    { label: '素萬那普機場交通', href: 'https://suvarnabhumi.airportthai.co.th/service/transportation' },
    { label: '曼谷大皇宮參觀資訊', href: 'https://www.royalgrandpalace.th/en/visit/faq' },
    { label: 'Song Wat Road 街區資訊', href: 'https://www.songwat.net/' },
    { label: 'Ancient City 官方資訊', href: 'https://www.muangboran.co.th/en/' },
  ],
}

export type SoutheastAsiaTrip2026 = typeof southeastAsiaTrip2026
