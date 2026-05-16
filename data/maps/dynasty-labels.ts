/**
 * 朝代標籤：把跨多朝代的同名 polygon 改顯示「{朝代}（{國家}）」。
 *
 * 使用：dynastyLabelAt(name, year) → '安史之亂前夕（唐）' | null
 *   若回 null，由上層 fallback 到 nameZhOf(name)。
 *
 * 設計：geojson 的 polygon 名稱常常只是地理稱呼（如 "Egypt", "England", "Persia"），
 *      跨朝代不變；此表把這些通用名按年代切成朝代區段。
 *
 * 粒度策略（user-defined）：
 *   - 平穩期 50-100 年一段
 *   - 擴張／衰退／分裂期 5-30 年一段（看密度需求）
 *   - 戰爭／轉折年單獨成段（如安史之亂、靖康之變、奧斯曼維也納之圍）
 *
 * 9999 = 至今。
 */

export interface DynastyEntry {
  from: number
  to: number
  dynasty_zh: string
  country_zh: string
}

export const DYNASTY_LABELS: Record<string, DynastyEntry[]> = {
  // ============================================================
  // 中國
  // ============================================================
  // Han Empire / Han polygon — 西漢 / 新莽 / 東漢
  'Han Empire': [
    { from: -202, to: -195, dynasty_zh: '高祖建漢', country_zh: '西漢' },
    { from: -195, to: -157, dynasty_zh: '惠／呂后／文帝休養生息', country_zh: '西漢' },
    { from: -156, to: -141, dynasty_zh: '景帝（七國之亂）', country_zh: '西漢' },
    { from: -140, to: -87, dynasty_zh: '武帝擴張（漠北之戰／絲路）', country_zh: '西漢' },
    { from: -86, to: -49, dynasty_zh: '昭宣中興', country_zh: '西漢' },
    { from: -48, to: 8, dynasty_zh: '元成哀平（衰退）', country_zh: '西漢' },
    { from: 9, to: 23, dynasty_zh: '王莽新朝', country_zh: '中國' },
    { from: 25, to: 57, dynasty_zh: '光武中興', country_zh: '東漢' },
    { from: 58, to: 88, dynasty_zh: '明章之治', country_zh: '東漢' },
    { from: 89, to: 167, dynasty_zh: '外戚宦官鬥爭', country_zh: '東漢' },
    { from: 168, to: 184, dynasty_zh: '黨錮之禍', country_zh: '東漢' },
    { from: 184, to: 220, dynasty_zh: '黃巾之亂到三國前夕', country_zh: '東漢' },
  ],
  'Han': [
    // 'Han' polygon 是另一條，同樣標
    { from: -202, to: -141, dynasty_zh: '初建恢復期', country_zh: '西漢' },
    { from: -140, to: -87, dynasty_zh: '武帝擴張', country_zh: '西漢' },
    { from: -86, to: 8, dynasty_zh: '昭宣中興到衰退', country_zh: '西漢' },
    { from: 9, to: 23, dynasty_zh: '王莽新朝', country_zh: '中國' },
    { from: 25, to: 220, dynasty_zh: '東漢', country_zh: '中國' },
    { from: 220, to: 299, dynasty_zh: '三國／西晉初', country_zh: '中國' },
  ],

  // Tang Empire — 安史之亂前後變化最大
  'Tang Empire': [
    { from: 618, to: 626, dynasty_zh: '武德（高祖）', country_zh: '唐' },
    { from: 627, to: 649, dynasty_zh: '貞觀之治（太宗擴張）', country_zh: '唐' },
    { from: 650, to: 683, dynasty_zh: '高宗（西突厥滅、永徽之治）', country_zh: '唐' },
    { from: 684, to: 704, dynasty_zh: '武則天', country_zh: '武周' },
    { from: 705, to: 712, dynasty_zh: '中宗／睿宗', country_zh: '唐' },
    { from: 713, to: 741, dynasty_zh: '玄宗開元盛世', country_zh: '唐' },
    { from: 742, to: 754, dynasty_zh: '天寶巔峰前夕', country_zh: '唐' },
    { from: 755, to: 763, dynasty_zh: '安史之亂', country_zh: '唐' },
    { from: 763, to: 805, dynasty_zh: '中唐藩鎮分裂', country_zh: '唐' },
    { from: 805, to: 859, dynasty_zh: '元和中興到大中之治', country_zh: '唐' },
    { from: 860, to: 873, dynasty_zh: '懿宗（裘甫／龐勛之亂）', country_zh: '唐' },
    { from: 874, to: 884, dynasty_zh: '黃巢之亂', country_zh: '唐' },
    { from: 884, to: 907, dynasty_zh: '晚唐藩鎮割據', country_zh: '唐' },
  ],

  // Song Empire — 北宋／靖康之變／南宋
  'Song Empire': [
    { from: 960, to: 1003, dynasty_zh: '北宋建國', country_zh: '北宋' },
    { from: 1004, to: 1004, dynasty_zh: '澶淵之盟', country_zh: '北宋' },
    { from: 1005, to: 1066, dynasty_zh: '北宋鼎盛（仁宗治世）', country_zh: '北宋' },
    { from: 1067, to: 1085, dynasty_zh: '王安石變法', country_zh: '北宋' },
    { from: 1086, to: 1125, dynasty_zh: '北宋末（新舊黨爭、徽宗）', country_zh: '北宋' },
    { from: 1126, to: 1127, dynasty_zh: '靖康之變', country_zh: '宋' },
    { from: 1127, to: 1141, dynasty_zh: '南宋建立（紹興和議前）', country_zh: '南宋' },
    { from: 1142, to: 1206, dynasty_zh: '南宋中期（孝宗中興）', country_zh: '南宋' },
    { from: 1207, to: 1234, dynasty_zh: '聯蒙滅金前後', country_zh: '南宋' },
    { from: 1235, to: 1275, dynasty_zh: '蒙古攻宋四十年', country_zh: '南宋' },
    { from: 1276, to: 1279, dynasty_zh: '崖山之戰（亡國）', country_zh: '南宋' },
  ],

  // Yuan Empire — 忽必烈到紅巾軍
  'Yuan Empire': [
    { from: 1271, to: 1279, dynasty_zh: '忽必烈滅宋', country_zh: '元' },
    { from: 1280, to: 1294, dynasty_zh: '忽必烈晚年（征日／征越南）', country_zh: '元' },
    { from: 1295, to: 1320, dynasty_zh: '中期穩定', country_zh: '元' },
    { from: 1321, to: 1351, dynasty_zh: '頻繁宮廷政變', country_zh: '元' },
    { from: 1351, to: 1368, dynasty_zh: '紅巾軍起義到順帝北逃', country_zh: '元' },
  ],

  // Ming Empire — 永樂下西洋／土木堡／萬曆三大征／明末
  'Ming Empire': [
    { from: 1368, to: 1398, dynasty_zh: '洪武（建國／藍玉案）', country_zh: '明' },
    { from: 1399, to: 1402, dynasty_zh: '靖難之役', country_zh: '明' },
    { from: 1403, to: 1424, dynasty_zh: '永樂（鄭和下西洋／遷都北京）', country_zh: '明' },
    { from: 1425, to: 1435, dynasty_zh: '仁宣之治', country_zh: '明' },
    { from: 1436, to: 1449, dynasty_zh: '正統（土木堡之變前）', country_zh: '明' },
    { from: 1450, to: 1505, dynasty_zh: '景泰／成化／弘治中興', country_zh: '明' },
    { from: 1506, to: 1521, dynasty_zh: '正德（劉瑾／寧王之亂）', country_zh: '明' },
    { from: 1522, to: 1572, dynasty_zh: '嘉靖／隆慶（大禮議、倭寇、隆慶開關）', country_zh: '明' },
    { from: 1573, to: 1620, dynasty_zh: '萬曆（張居正、三大征、礦稅）', country_zh: '明' },
    { from: 1621, to: 1627, dynasty_zh: '天啟（魏忠賢）', country_zh: '明' },
    { from: 1628, to: 1644, dynasty_zh: '崇禎（農民起義／李自成入北京）', country_zh: '明' },
  ],
  'Ming Chinese Empire': [
    { from: 1500, to: 1505, dynasty_zh: '弘治中興', country_zh: '明' },
    { from: 1506, to: 1572, dynasty_zh: '嘉靖／隆慶', country_zh: '明' },
    { from: 1573, to: 1620, dynasty_zh: '萬曆三大征', country_zh: '明' },
    { from: 1621, to: 1644, dynasty_zh: '明末天啟／崇禎', country_zh: '明' },
    { from: 1645, to: 1649, dynasty_zh: '南明殘餘', country_zh: '明' },
  ],

  // Qing Empire — 三藩／康雍乾／鴉片戰爭／太平天國／甲午
  'Qing Empire': [
    { from: 1636, to: 1643, dynasty_zh: '皇太極建大清', country_zh: '清' },
    { from: 1644, to: 1661, dynasty_zh: '順治入關', country_zh: '清' },
    { from: 1662, to: 1683, dynasty_zh: '康熙前期（平三藩、收台灣）', country_zh: '清' },
    { from: 1684, to: 1722, dynasty_zh: '康熙盛世（征準噶爾、雅克薩）', country_zh: '清' },
    { from: 1723, to: 1735, dynasty_zh: '雍正改革', country_zh: '清' },
    { from: 1736, to: 1795, dynasty_zh: '乾隆盛世（十全武功／文字獄）', country_zh: '清' },
    { from: 1796, to: 1820, dynasty_zh: '嘉慶（白蓮教之亂）', country_zh: '清' },
    { from: 1821, to: 1839, dynasty_zh: '道光前期（衰退）', country_zh: '清' },
    { from: 1840, to: 1842, dynasty_zh: '第一次鴉片戰爭', country_zh: '清' },
    { from: 1843, to: 1850, dynasty_zh: '道光末（拜上帝會起）', country_zh: '清' },
    { from: 1851, to: 1864, dynasty_zh: '太平天國', country_zh: '清' },
    { from: 1856, to: 1860, dynasty_zh: '第二次鴉片戰爭', country_zh: '清' },
    { from: 1861, to: 1874, dynasty_zh: '同治中興（洋務運動初）', country_zh: '清' },
    { from: 1875, to: 1894, dynasty_zh: '光緒前期（洋務運動）', country_zh: '清' },
    { from: 1894, to: 1895, dynasty_zh: '甲午戰爭', country_zh: '清' },
    { from: 1896, to: 1898, dynasty_zh: '戊戌變法', country_zh: '清' },
    { from: 1899, to: 1901, dynasty_zh: '義和團／八國聯軍', country_zh: '清' },
    { from: 1901, to: 1911, dynasty_zh: '清末新政到辛亥革命', country_zh: '清' },
  ],
  'Manchu Empire': [
    { from: 1700, to: 1722, dynasty_zh: '康熙', country_zh: '清' },
    { from: 1723, to: 1735, dynasty_zh: '雍正', country_zh: '清' },
    { from: 1736, to: 1795, dynasty_zh: '乾隆', country_zh: '清' },
  ],
  'Post-Ming Warlords': [
    { from: 1644, to: 1662, dynasty_zh: '南明（弘光／隆武／永曆）', country_zh: '中國' },
    { from: 1673, to: 1681, dynasty_zh: '三藩之亂', country_zh: '中國' },
  ],

  // China (1945+)
  'China': [
    { from: 1945, to: 1949, dynasty_zh: '國共內戰', country_zh: '中華民國／中華人民共和國' },
    { from: 1949, to: 1957, dynasty_zh: '建國初（土改／一五計劃）', country_zh: '中華人民共和國' },
    { from: 1958, to: 1961, dynasty_zh: '大躍進', country_zh: '中華人民共和國' },
    { from: 1962, to: 1965, dynasty_zh: '七千人大會調整期', country_zh: '中華人民共和國' },
    { from: 1966, to: 1976, dynasty_zh: '文化大革命', country_zh: '中華人民共和國' },
    { from: 1977, to: 1989, dynasty_zh: '改革開放初（鄧小平／六四前）', country_zh: '中華人民共和國' },
    { from: 1990, to: 2001, dynasty_zh: '南巡到入 WTO', country_zh: '中華人民共和國' },
    { from: 2002, to: 2012, dynasty_zh: '胡溫黃金十年', country_zh: '中華人民共和國' },
    { from: 2013, to: 9999, dynasty_zh: '習近平時代', country_zh: '中華人民共和國' },
  ],

  // ============================================================
  // 阿拉伯／伊斯蘭
  // ============================================================
  // Umayyad Caliphate — 短但變化大
  'Umayyad Caliphate': [
    { from: 661, to: 680, dynasty_zh: '建立（穆阿維葉）', country_zh: '伍麥亞' },
    { from: 680, to: 692, dynasty_zh: '第二次內戰（賓‧祖拜爾）', country_zh: '伍麥亞' },
    { from: 692, to: 715, dynasty_zh: '阿卜杜‧麥利克／瓦利德擴張（征西／中亞／信德）', country_zh: '伍麥亞' },
    { from: 716, to: 740, dynasty_zh: '希沙姆（巔峰／突厥前線）', country_zh: '伍麥亞' },
    { from: 741, to: 750, dynasty_zh: '第三次內戰／阿巴斯革命', country_zh: '伍麥亞' },
  ],

  // Abbasid Caliphate — 用戶提的範例，切超細
  'Abbasid Caliphate': [
    { from: 750, to: 762, dynasty_zh: '建立（阿布勒‧阿巴斯／曼蘇爾）', country_zh: '阿巴斯' },
    { from: 762, to: 786, dynasty_zh: '巴格達建都到馬赫迪', country_zh: '阿巴斯' },
    { from: 786, to: 809, dynasty_zh: '哈倫‧拉希德黃金時代', country_zh: '阿巴斯' },
    { from: 809, to: 813, dynasty_zh: '第四次內戰（阿明 vs 馬蒙）', country_zh: '阿巴斯' },
    { from: 813, to: 833, dynasty_zh: '馬蒙（智慧之家全盛）', country_zh: '阿巴斯' },
    { from: 833, to: 861, dynasty_zh: '薩瑪拉時期（圖耳其禁衛軍）', country_zh: '阿巴斯' },
    { from: 861, to: 870, dynasty_zh: '薩瑪拉混亂（4 哈里發 9 年）', country_zh: '阿巴斯' },
    { from: 870, to: 892, dynasty_zh: '形式恢復（穆塔米德／實際為穆瓦法克）', country_zh: '阿巴斯' },
    { from: 892, to: 945, dynasty_zh: '丟省（伊朗／埃及／馬格里布相繼獨立）', country_zh: '阿巴斯' },
    { from: 945, to: 1055, dynasty_zh: '白益王朝實控巴格達', country_zh: '阿巴斯' },
    { from: 1055, to: 1118, dynasty_zh: '塞爾柱實控', country_zh: '阿巴斯' },
    { from: 1118, to: 1180, dynasty_zh: '哈里發短暫獨立', country_zh: '阿巴斯' },
    { from: 1180, to: 1225, dynasty_zh: '納西爾中興', country_zh: '阿巴斯' },
    { from: 1225, to: 1258, dynasty_zh: '末期到蒙古滅亡', country_zh: '阿巴斯' },
  ],

  // ============================================================
  // 蒙古
  // ============================================================
  'Mongol Empire': [
    { from: 1206, to: 1218, dynasty_zh: '成吉思汗統一蒙古／征西夏／金', country_zh: '蒙古' },
    { from: 1219, to: 1225, dynasty_zh: '第一次西征（花剌子模）', country_zh: '蒙古' },
    { from: 1227, to: 1241, dynasty_zh: '窩闊台（征金／第二次西征拔都征歐）', country_zh: '蒙古' },
    { from: 1241, to: 1246, dynasty_zh: '攝政期（脫列哥那）', country_zh: '蒙古' },
    { from: 1246, to: 1248, dynasty_zh: '貴由', country_zh: '蒙古' },
    { from: 1248, to: 1251, dynasty_zh: '攝政（斡兀立海迷失）', country_zh: '蒙古' },
    { from: 1251, to: 1259, dynasty_zh: '蒙哥（征大理／第三次西征旭烈兀征阿巴斯）', country_zh: '蒙古' },
    { from: 1260, to: 1264, dynasty_zh: '忽必烈／阿里不哥內戰', country_zh: '蒙古' },
    { from: 1264, to: 1271, dynasty_zh: '忽必烈勝出', country_zh: '蒙古' },
    { from: 1271, to: 1294, dynasty_zh: '元建立／四大汗國分立', country_zh: '蒙古' },
  ],

  // ============================================================
  // 羅馬
  // ============================================================
  'Roman Empire': [
    { from: -27, to: 14, dynasty_zh: '奧古斯都（建立元首制）', country_zh: '羅馬帝國' },
    { from: 14, to: 37, dynasty_zh: '提比略', country_zh: '羅馬帝國' },
    { from: 37, to: 68, dynasty_zh: '卡利古拉／克勞狄／尼祿', country_zh: '羅馬帝國' },
    { from: 68, to: 69, dynasty_zh: '四帝之年', country_zh: '羅馬帝國' },
    { from: 69, to: 96, dynasty_zh: '弗拉維（征不列顛／滅猶太）', country_zh: '羅馬帝國' },
    { from: 96, to: 117, dynasty_zh: '涅爾瓦／圖拉真（帝國巔峰）', country_zh: '羅馬帝國' },
    { from: 117, to: 180, dynasty_zh: '哈德良／安東尼／奧勒留（五賢帝晚期）', country_zh: '羅馬帝國' },
    { from: 180, to: 192, dynasty_zh: '康茂德', country_zh: '羅馬帝國' },
    { from: 193, to: 235, dynasty_zh: '塞維魯王朝', country_zh: '羅馬帝國' },
    { from: 235, to: 284, dynasty_zh: '三世紀危機', country_zh: '羅馬帝國' },
    { from: 284, to: 305, dynasty_zh: '戴克里先（四帝共治）', country_zh: '羅馬帝國' },
    { from: 306, to: 337, dynasty_zh: '君士坦丁（基督教合法／遷都）', country_zh: '羅馬帝國' },
    { from: 337, to: 379, dynasty_zh: '君士坦丁諸子／背教者尤利安', country_zh: '羅馬帝國' },
    { from: 379, to: 395, dynasty_zh: '狄奧多西（最後統一）', country_zh: '羅馬帝國' },
  ],
  'Roman Republic': [
    { from: -509, to: -390, dynasty_zh: '早期共和（高盧人攻陷羅馬）', country_zh: '羅馬共和' },
    { from: -390, to: -264, dynasty_zh: '征服義大利', country_zh: '羅馬共和' },
    { from: -264, to: -146, dynasty_zh: '布匿戰爭（三次）', country_zh: '羅馬共和' },
    { from: -146, to: -88, dynasty_zh: '征服希臘化世界', country_zh: '羅馬共和' },
    { from: -88, to: -31, dynasty_zh: '內戰時期（馬略-蘇拉／凱撒／屋大維）', country_zh: '羅馬共和' },
  ],
  'Eastern Roman Empire': [
    { from: 395, to: 476, dynasty_zh: '東羅馬（西羅馬未亡前）', country_zh: '東羅馬' },
    { from: 476, to: 565, dynasty_zh: '查士丁尼（收復西部）', country_zh: '東羅馬' },
    { from: 565, to: 610, dynasty_zh: '波斯戰爭', country_zh: '東羅馬' },
    { from: 610, to: 717, dynasty_zh: '希拉克略到伊蘇里亞前夕', country_zh: '東羅馬' },
  ],
  'Western Roman Empire': [
    { from: 395, to: 410, dynasty_zh: '霍諾留／阿拉里克洗劫羅馬', country_zh: '西羅馬' },
    { from: 410, to: 455, dynasty_zh: '汪達爾／匈人入侵', country_zh: '西羅馬' },
    { from: 455, to: 476, dynasty_zh: '末期（最後西部皇帝）', country_zh: '西羅馬' },
  ],

  // ============================================================
  // 拜占庭
  // ============================================================
  'Byzantine Empire': [
    { from: 330, to: 565, dynasty_zh: '查士丁尼前後', country_zh: '東羅馬' },
    { from: 565, to: 717, dynasty_zh: '希拉克略到伊蘇里亞', country_zh: '東羅馬' },
    { from: 717, to: 802, dynasty_zh: '伊蘇里亞王朝（聖像破壞）', country_zh: '拜占庭' },
    { from: 802, to: 867, dynasty_zh: '阿摩里亞王朝', country_zh: '拜占庭' },
    { from: 867, to: 1025, dynasty_zh: '馬其頓王朝（巴西爾二世巔峰）', country_zh: '拜占庭' },
    { from: 1025, to: 1071, dynasty_zh: '馬其頓末（曼齊克特戰役）', country_zh: '拜占庭' },
    { from: 1071, to: 1081, dynasty_zh: '曼齊克特後混亂', country_zh: '拜占庭' },
    { from: 1081, to: 1180, dynasty_zh: '科穆寧（阿萊克修斯／曼努埃爾）', country_zh: '拜占庭' },
    { from: 1180, to: 1204, dynasty_zh: '安格洛斯（第四次十字軍前）', country_zh: '拜占庭' },
    { from: 1204, to: 1261, dynasty_zh: '尼西亞流亡（拉丁帝國占據君堡）', country_zh: '拜占庭' },
    { from: 1261, to: 1341, dynasty_zh: '巴列奧略前期（米海爾八世收復）', country_zh: '拜占庭' },
    { from: 1341, to: 1453, dynasty_zh: '巴列奧略末期到陷落', country_zh: '拜占庭' },
  ],

  // ============================================================
  // 奧斯曼
  // ============================================================
  'Ottoman Empire': [
    { from: 1299, to: 1389, dynasty_zh: '崛起（科索沃戰役）', country_zh: '奧斯曼' },
    { from: 1389, to: 1402, dynasty_zh: '巴耶塞特一世（帖木兒擊敗）', country_zh: '奧斯曼' },
    { from: 1402, to: 1413, dynasty_zh: '空位期內戰', country_zh: '奧斯曼' },
    { from: 1413, to: 1451, dynasty_zh: '穆罕默德一世／穆拉德二世復興', country_zh: '奧斯曼' },
    { from: 1451, to: 1453, dynasty_zh: '攻陷君士坦丁堡', country_zh: '奧斯曼' },
    { from: 1453, to: 1481, dynasty_zh: '穆罕默德二世擴張', country_zh: '奧斯曼' },
    { from: 1481, to: 1520, dynasty_zh: '巴耶塞特二世／塞利姆一世（征馬木留克）', country_zh: '奧斯曼' },
    { from: 1520, to: 1566, dynasty_zh: '蘇萊曼大帝（黃金時代）', country_zh: '奧斯曼' },
    { from: 1566, to: 1683, dynasty_zh: '停滯期', country_zh: '奧斯曼' },
    { from: 1683, to: 1699, dynasty_zh: '維也納之圍到卡洛維茨和約', country_zh: '奧斯曼' },
    { from: 1699, to: 1768, dynasty_zh: '早期衰退', country_zh: '奧斯曼' },
    { from: 1768, to: 1839, dynasty_zh: '俄土戰爭頻繁／改革前夜', country_zh: '奧斯曼' },
    { from: 1839, to: 1876, dynasty_zh: '坦志麥特改革', country_zh: '奧斯曼' },
    { from: 1876, to: 1908, dynasty_zh: '阿卜杜哈米德二世', country_zh: '奧斯曼' },
    { from: 1908, to: 1918, dynasty_zh: '青年土耳其／一戰', country_zh: '奧斯曼' },
    { from: 1918, to: 1919, dynasty_zh: '末期占領', country_zh: '奧斯曼' },
  ],

  // ============================================================
  // 波斯／伊朗
  // ============================================================
  'Persia': [
    { from: 400, to: 531, dynasty_zh: '薩珊（卑路斯／喀瓦德／霍斯勞一世）', country_zh: '波斯' },
    { from: 531, to: 579, dynasty_zh: '霍斯勞一世（薩珊巔峰）', country_zh: '波斯' },
    { from: 579, to: 651, dynasty_zh: '薩珊末（阿拉伯征服）', country_zh: '波斯' },
    { from: 651, to: 750, dynasty_zh: '伍麥亞統治', country_zh: '波斯' },
    { from: 750, to: 820, dynasty_zh: '阿巴斯統治', country_zh: '波斯' },
    { from: 821, to: 873, dynasty_zh: '塔希爾／薩法爾', country_zh: '波斯' },
    { from: 874, to: 999, dynasty_zh: '薩曼王朝', country_zh: '波斯' },
    { from: 945, to: 1055, dynasty_zh: '白益（同時控巴格達）', country_zh: '波斯' },
    { from: 1037, to: 1194, dynasty_zh: '塞爾柱', country_zh: '波斯' },
    { from: 1194, to: 1220, dynasty_zh: '花剌子模', country_zh: '波斯' },
    { from: 1220, to: 1256, dynasty_zh: '蒙古入侵', country_zh: '波斯' },
    { from: 1256, to: 1335, dynasty_zh: '伊兒汗', country_zh: '波斯' },
    { from: 1335, to: 1370, dynasty_zh: '分裂期（札剌亦兒／穆扎法爾）', country_zh: '波斯' },
    { from: 1370, to: 1405, dynasty_zh: '帖木兒帝國', country_zh: '波斯' },
    { from: 1405, to: 1500, dynasty_zh: '黑羊／白羊王朝', country_zh: '波斯' },
    { from: 1501, to: 1524, dynasty_zh: '伊斯瑪儀一世（薩法維建國）', country_zh: '波斯' },
    { from: 1524, to: 1588, dynasty_zh: '塔赫馬斯普一世到動盪', country_zh: '波斯' },
    { from: 1588, to: 1629, dynasty_zh: '阿巴斯一世（薩法維巔峰）', country_zh: '波斯' },
    { from: 1629, to: 1722, dynasty_zh: '薩法維衰退', country_zh: '波斯' },
    { from: 1722, to: 1736, dynasty_zh: '霍塔克阿富汗入侵', country_zh: '波斯' },
    { from: 1736, to: 1747, dynasty_zh: '納迪爾沙（阿夫沙爾）', country_zh: '波斯' },
    { from: 1747, to: 1796, dynasty_zh: '贊德王朝', country_zh: '波斯' },
    { from: 1796, to: 1828, dynasty_zh: '卡扎爾前期（俄波戰爭）', country_zh: '波斯' },
    { from: 1828, to: 1906, dynasty_zh: '卡扎爾中期（喪失高加索）', country_zh: '波斯' },
    { from: 1906, to: 1919, dynasty_zh: '立憲革命到一戰末', country_zh: '波斯' },
  ],
  'Iran': [
    { from: 1920, to: 1925, dynasty_zh: '卡扎爾末', country_zh: '伊朗' },
    { from: 1925, to: 1941, dynasty_zh: '禮薩‧巴勒維', country_zh: '伊朗' },
    { from: 1941, to: 1979, dynasty_zh: '穆罕默德‧禮薩‧巴勒維', country_zh: '伊朗' },
    { from: 1979, to: 1989, dynasty_zh: '霍梅尼伊斯蘭革命', country_zh: '伊朗' },
    { from: 1989, to: 9999, dynasty_zh: '伊斯蘭共和國（哈梅內伊）', country_zh: '伊朗' },
  ],
  'Sasanian Empire': [
    { from: 224, to: 309, dynasty_zh: '建立（阿爾達希爾／沙普爾一世）', country_zh: '薩珊' },
    { from: 309, to: 379, dynasty_zh: '沙普爾二世', country_zh: '薩珊' },
    { from: 379, to: 488, dynasty_zh: '中期', country_zh: '薩珊' },
    { from: 488, to: 531, dynasty_zh: '卡瓦德一世（馬茲達克教爭議）', country_zh: '薩珊' },
    { from: 531, to: 579, dynasty_zh: '霍斯勞一世（巔峰）', country_zh: '薩珊' },
    { from: 579, to: 628, dynasty_zh: '霍斯勞二世（與拜占庭大戰）', country_zh: '薩珊' },
    { from: 628, to: 651, dynasty_zh: '阿拉伯滅亡前', country_zh: '薩珊' },
  ],
  'Parthian Empire': [
    { from: -247, to: -141, dynasty_zh: '建立到征服美索不達米亞', country_zh: '帕提亞' },
    { from: -141, to: -53, dynasty_zh: '密特里達梯二世（巔峰）', country_zh: '帕提亞' },
    { from: -53, to: -53, dynasty_zh: '卡萊戰役（擊敗克拉蘇）', country_zh: '帕提亞' },
    { from: -53, to: 114, dynasty_zh: '與羅馬對抗期', country_zh: '帕提亞' },
    { from: 114, to: 224, dynasty_zh: '晚期（衰退到薩珊取代）', country_zh: '帕提亞' },
  ],
  'Achaemenid Empire': [
    { from: -550, to: -530, dynasty_zh: '居魯士大帝', country_zh: '阿契美尼德' },
    { from: -530, to: -522, dynasty_zh: '岡比西斯（征埃及）', country_zh: '阿契美尼德' },
    { from: -522, to: -486, dynasty_zh: '大流士一世（巔峰／希波戰爭）', country_zh: '阿契美尼德' },
    { from: -486, to: -465, dynasty_zh: '薛西斯一世（薩拉米戰役）', country_zh: '阿契美尼德' },
    { from: -465, to: -404, dynasty_zh: '阿爾塔薛西斯一世到第二次內戰', country_zh: '阿契美尼德' },
    { from: -404, to: -358, dynasty_zh: '阿爾塔薛西斯二世', country_zh: '阿契美尼德' },
    { from: -358, to: -330, dynasty_zh: '末期（亞歷山大滅亡）', country_zh: '阿契美尼德' },
  ],

  // ============================================================
  // 埃及
  // ============================================================
  'Egypt': [
    { from: -4000, to: -3100, dynasty_zh: '前王朝', country_zh: '埃及' },
    { from: -3100, to: -2687, dynasty_zh: '早王朝', country_zh: '埃及' },
    { from: -2686, to: -2161, dynasty_zh: '古王國（金字塔時代）', country_zh: '埃及' },
    { from: -2160, to: -2056, dynasty_zh: '第一中間期', country_zh: '埃及' },
    { from: -2055, to: -1651, dynasty_zh: '中王國', country_zh: '埃及' },
    { from: -1650, to: -1551, dynasty_zh: '第二中間期（西克索）', country_zh: '埃及' },
    { from: -1550, to: -1295, dynasty_zh: '新王國 18 王朝（圖特摩斯／哈特謝普蘇特／阿肯那頓）', country_zh: '埃及' },
    { from: -1294, to: -1186, dynasty_zh: '新王國 19 王朝（拉美西斯二世）', country_zh: '埃及' },
    { from: -1185, to: -1070, dynasty_zh: '新王國 20 王朝（海上民族入侵）', country_zh: '埃及' },
    { from: -1069, to: -664, dynasty_zh: '第三中間期', country_zh: '埃及' },
    { from: -664, to: -525, dynasty_zh: '後期王朝 26 王朝（賽易斯）', country_zh: '埃及' },
    { from: -525, to: -404, dynasty_zh: '第一次波斯統治', country_zh: '埃及' },
    { from: -404, to: -343, dynasty_zh: '末期本土王朝（28-30 王朝）', country_zh: '埃及' },
    { from: -343, to: -332, dynasty_zh: '第二次波斯統治', country_zh: '埃及' },
    { from: -332, to: -305, dynasty_zh: '亞歷山大／繼業者', country_zh: '埃及' },
    { from: -305, to: -200, dynasty_zh: '托勒密前期（亞歷山卓巔峰）', country_zh: '埃及' },
    { from: -200, to: -31, dynasty_zh: '托勒密後期（克麗奧帕特拉七世）', country_zh: '埃及' },
    { from: -30, to: 395, dynasty_zh: '羅馬', country_zh: '埃及' },
    { from: 395, to: 640, dynasty_zh: '拜占庭', country_zh: '埃及' },
    { from: 641, to: 750, dynasty_zh: '阿拉伯（拉希頓／伍麥亞）', country_zh: '埃及' },
    { from: 750, to: 868, dynasty_zh: '阿巴斯', country_zh: '埃及' },
    { from: 868, to: 905, dynasty_zh: '圖倫', country_zh: '埃及' },
    { from: 905, to: 935, dynasty_zh: '阿巴斯回歸', country_zh: '埃及' },
    { from: 935, to: 969, dynasty_zh: '伊赫希迪', country_zh: '埃及' },
    { from: 969, to: 1171, dynasty_zh: '法蒂瑪', country_zh: '埃及' },
    { from: 1171, to: 1250, dynasty_zh: '阿尤布（薩拉丁）', country_zh: '埃及' },
    { from: 1250, to: 1382, dynasty_zh: '巴赫里馬木留克', country_zh: '埃及' },
    { from: 1382, to: 1517, dynasty_zh: '布爾吉馬木留克', country_zh: '埃及' },
    { from: 1517, to: 1798, dynasty_zh: '奧斯曼省', country_zh: '埃及' },
    { from: 1798, to: 1801, dynasty_zh: '拿破崙占領', country_zh: '埃及' },
    { from: 1805, to: 1848, dynasty_zh: '穆罕默德‧阿里改革', country_zh: '埃及' },
    { from: 1848, to: 1882, dynasty_zh: '海迪夫王朝', country_zh: '埃及' },
    { from: 1882, to: 1914, dynasty_zh: '英占（奧斯曼名義下）', country_zh: '埃及' },
    { from: 1914, to: 1922, dynasty_zh: '英屬保護國', country_zh: '埃及' },
    { from: 1922, to: 1952, dynasty_zh: '王國（福阿德／法魯克）', country_zh: '埃及' },
    { from: 1952, to: 1970, dynasty_zh: '納賽爾', country_zh: '埃及' },
    { from: 1970, to: 1981, dynasty_zh: '沙達特', country_zh: '埃及' },
    { from: 1981, to: 2011, dynasty_zh: '穆巴拉克', country_zh: '埃及' },
    { from: 2011, to: 2014, dynasty_zh: '阿拉伯之春／穆兄會', country_zh: '埃及' },
    { from: 2014, to: 9999, dynasty_zh: '塞西', country_zh: '埃及' },
  ],

  // ============================================================
  // 英國
  // ============================================================
  'England': [
    { from: 871, to: 924, dynasty_zh: '阿弗烈大帝／長者愛德華', country_zh: '英格蘭' },
    { from: 924, to: 1066, dynasty_zh: '盎格魯-撒克遜後期', country_zh: '英格蘭' },
    { from: 1066, to: 1100, dynasty_zh: '征服者威廉／威廉二世', country_zh: '英格蘭' },
    { from: 1100, to: 1135, dynasty_zh: '亨利一世（諾曼）', country_zh: '英格蘭' },
    { from: 1135, to: 1154, dynasty_zh: '無政府時期（斯蒂芬）', country_zh: '英格蘭' },
    { from: 1154, to: 1189, dynasty_zh: '亨利二世（金雀花建立／安茹帝國）', country_zh: '英格蘭' },
    { from: 1189, to: 1216, dynasty_zh: '獅心王／約翰王（大憲章）', country_zh: '英格蘭' },
    { from: 1216, to: 1272, dynasty_zh: '亨利三世', country_zh: '英格蘭' },
    { from: 1272, to: 1307, dynasty_zh: '愛德華一世（征威爾斯／蘇格蘭）', country_zh: '英格蘭' },
    { from: 1307, to: 1327, dynasty_zh: '愛德華二世', country_zh: '英格蘭' },
    { from: 1327, to: 1377, dynasty_zh: '愛德華三世（百年戰爭起）', country_zh: '英格蘭' },
    { from: 1377, to: 1399, dynasty_zh: '理查二世', country_zh: '英格蘭' },
    { from: 1399, to: 1461, dynasty_zh: '蘭開斯特王朝', country_zh: '英格蘭' },
    { from: 1455, to: 1485, dynasty_zh: '玫瑰戰爭', country_zh: '英格蘭' },
    { from: 1485, to: 1509, dynasty_zh: '亨利七世（都鐸建立）', country_zh: '英格蘭' },
    { from: 1509, to: 1529, dynasty_zh: '亨利八世前期', country_zh: '英格蘭' },
  ],
  'England and Ireland': [
    { from: 1530, to: 1547, dynasty_zh: '亨利八世（宗教改革）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1547, to: 1558, dynasty_zh: '愛德華六世／瑪麗一世', country_zh: '英格蘭與愛爾蘭' },
    { from: 1558, to: 1603, dynasty_zh: '伊麗莎白一世', country_zh: '英格蘭與愛爾蘭' },
    { from: 1603, to: 1625, dynasty_zh: '詹姆斯一世（斯圖亞特）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1625, to: 1649, dynasty_zh: '查理一世（內戰／處決）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1649, to: 1659, dynasty_zh: '共和（克倫威爾）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1660, to: 1685, dynasty_zh: '查理二世（復辟）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1685, to: 1688, dynasty_zh: '詹姆斯二世（光榮革命）', country_zh: '英格蘭與愛爾蘭' },
    { from: 1688, to: 1702, dynasty_zh: '威廉三世與瑪麗二世', country_zh: '英格蘭與愛爾蘭' },
    { from: 1702, to: 1714, dynasty_zh: '安妮女王', country_zh: '英格蘭與愛爾蘭' },
  ],
  'United Kingdom': [
    { from: 1714, to: 1760, dynasty_zh: '喬治一世／二世（漢諾威）', country_zh: '聯合王國' },
    { from: 1760, to: 1820, dynasty_zh: '喬治三世（美獨／拿破崙戰爭）', country_zh: '聯合王國' },
    { from: 1820, to: 1837, dynasty_zh: '喬治四世／威廉四世', country_zh: '聯合王國' },
    { from: 1837, to: 1901, dynasty_zh: '維多利亞時代', country_zh: '聯合王國' },
    { from: 1901, to: 1910, dynasty_zh: '愛德華七世', country_zh: '聯合王國' },
    { from: 1910, to: 1936, dynasty_zh: '喬治五世（一戰／戰後）', country_zh: '聯合王國' },
    { from: 1936, to: 1936, dynasty_zh: '愛德華八世（退位）', country_zh: '聯合王國' },
    { from: 1936, to: 1952, dynasty_zh: '喬治六世（二戰）', country_zh: '聯合王國' },
    { from: 1952, to: 2022, dynasty_zh: '伊麗莎白二世', country_zh: '聯合王國' },
    { from: 2022, to: 9999, dynasty_zh: '查爾斯三世', country_zh: '聯合王國' },
  ],
  'United Kingdom of Great Britain and Ireland': [
    { from: 1815, to: 1837, dynasty_zh: '攝政－威廉四世', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1837, to: 1901, dynasty_zh: '維多利亞時代', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1901, to: 1910, dynasty_zh: '愛德華七世', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1910, to: 1922, dynasty_zh: '喬治五世前期', country_zh: '大不列顛及愛爾蘭聯合王國' },
    { from: 1922, to: 1937, dynasty_zh: '愛爾蘭獨立後', country_zh: '大不列顛及愛爾蘭聯合王國' },
  ],
  'Hanover': [
    { from: 1715, to: 1814, dynasty_zh: '漢諾威選侯（與英共主）', country_zh: '德意志' },
    { from: 1815, to: 1837, dynasty_zh: '漢諾威王國（與英共主）', country_zh: '德意志' },
    { from: 1837, to: 1866, dynasty_zh: '漢諾威王國（普奧戰爭被滅）', country_zh: '德意志' },
  ],

  // ============================================================
  // 法國
  // ============================================================
  'France': [
    { from: 843, to: 987, dynasty_zh: '加洛林（西法蘭克）', country_zh: '法國' },
    { from: 987, to: 1108, dynasty_zh: '卡佩前期（虛位君主）', country_zh: '法國' },
    { from: 1108, to: 1180, dynasty_zh: '路易六／七世', country_zh: '法國' },
    { from: 1180, to: 1223, dynasty_zh: '腓力二世（與英爭奪）', country_zh: '法國' },
    { from: 1223, to: 1270, dynasty_zh: '聖路易九世', country_zh: '法國' },
    { from: 1270, to: 1328, dynasty_zh: '腓力四世到卡佩絕嗣', country_zh: '法國' },
    { from: 1328, to: 1364, dynasty_zh: '瓦盧瓦／百年戰爭前期', country_zh: '法國' },
    { from: 1364, to: 1422, dynasty_zh: '查理五世／六世（百年戰爭）', country_zh: '法國' },
    { from: 1422, to: 1461, dynasty_zh: '查理七世（聖女貞德）', country_zh: '法國' },
    { from: 1461, to: 1483, dynasty_zh: '路易十一', country_zh: '法國' },
    { from: 1483, to: 1547, dynasty_zh: '查理八／路易十二／法蘭索瓦一世（義大利戰爭）', country_zh: '法國' },
    { from: 1547, to: 1589, dynasty_zh: '宗教戰爭', country_zh: '法國' },
    { from: 1589, to: 1610, dynasty_zh: '亨利四世（南特敕令）', country_zh: '法國' },
    { from: 1610, to: 1643, dynasty_zh: '路易十三（黎希留）', country_zh: '法國' },
    { from: 1643, to: 1715, dynasty_zh: '路易十四（太陽王）', country_zh: '法國' },
    { from: 1715, to: 1774, dynasty_zh: '路易十五', country_zh: '法國' },
    { from: 1774, to: 1791, dynasty_zh: '路易十六（大革命前）', country_zh: '法國' },
    { from: 1792, to: 1795, dynasty_zh: '第一共和（恐怖時期）', country_zh: '法國' },
    { from: 1795, to: 1799, dynasty_zh: '督政府', country_zh: '法國' },
    { from: 1799, to: 1804, dynasty_zh: '執政府（拿破崙）', country_zh: '法國' },
    { from: 1804, to: 1814, dynasty_zh: '第一帝國（拿破崙）', country_zh: '法國' },
    { from: 1814, to: 1830, dynasty_zh: '波旁復辟', country_zh: '法國' },
    { from: 1830, to: 1848, dynasty_zh: '七月王朝（路易‧腓力）', country_zh: '法國' },
    { from: 1848, to: 1852, dynasty_zh: '第二共和', country_zh: '法國' },
    { from: 1852, to: 1870, dynasty_zh: '第二帝國（拿破崙三世）', country_zh: '法國' },
    { from: 1870, to: 1914, dynasty_zh: '第三共和前期', country_zh: '法國' },
    { from: 1914, to: 1918, dynasty_zh: '一戰', country_zh: '法國' },
    { from: 1919, to: 1939, dynasty_zh: '戰間期', country_zh: '法國' },
    { from: 1940, to: 1944, dynasty_zh: '維琪政權／自由法國', country_zh: '法國' },
    { from: 1944, to: 1958, dynasty_zh: '第四共和（去殖民化戰爭）', country_zh: '法國' },
    { from: 1958, to: 1969, dynasty_zh: '第五共和（戴高樂）', country_zh: '法國' },
    { from: 1969, to: 9999, dynasty_zh: '第五共和', country_zh: '法國' },
  ],
  'Kingdom of France': [
    { from: 987, to: 1328, dynasty_zh: '卡佩王朝', country_zh: '法蘭西王國' },
    { from: 1328, to: 1589, dynasty_zh: '瓦盧瓦王朝', country_zh: '法蘭西王國' },
  ],

  // ============================================================
  // 神聖羅馬帝國
  // ============================================================
  'Holy Roman Empire': [
    { from: 919, to: 1024, dynasty_zh: '奧托王朝', country_zh: '神聖羅馬帝國' },
    { from: 1024, to: 1125, dynasty_zh: '薩利安王朝（敘任權鬥爭）', country_zh: '神聖羅馬帝國' },
    { from: 1138, to: 1190, dynasty_zh: '腓特烈一世（紅鬍子）', country_zh: '神聖羅馬帝國' },
    { from: 1190, to: 1254, dynasty_zh: '霍亨斯陶芬末期', country_zh: '神聖羅馬帝國' },
    { from: 1254, to: 1273, dynasty_zh: '大空位時期', country_zh: '神聖羅馬帝國' },
    { from: 1273, to: 1356, dynasty_zh: '哈布斯堡早期到黃金詔書', country_zh: '神聖羅馬帝國' },
    { from: 1356, to: 1438, dynasty_zh: '盧森堡王朝', country_zh: '神聖羅馬帝國' },
    { from: 1438, to: 1517, dynasty_zh: '哈布斯堡（馬克西米連）', country_zh: '神聖羅馬帝國' },
    { from: 1517, to: 1555, dynasty_zh: '查理五世（宗教改革）', country_zh: '神聖羅馬帝國' },
    { from: 1555, to: 1618, dynasty_zh: '奧格斯堡和約後', country_zh: '神聖羅馬帝國' },
    { from: 1618, to: 1648, dynasty_zh: '三十年戰爭', country_zh: '神聖羅馬帝國' },
    { from: 1648, to: 1740, dynasty_zh: '威斯特伐利亞後', country_zh: '神聖羅馬帝國' },
    { from: 1740, to: 1763, dynasty_zh: '奧地利王位繼承／七年戰爭', country_zh: '神聖羅馬帝國' },
    { from: 1763, to: 1806, dynasty_zh: '末期（拿破崙終結）', country_zh: '神聖羅馬帝國' },
  ],

  // ============================================================
  // 蒙兀兒
  // ============================================================
  'Mughal Empire': [
    { from: 1526, to: 1530, dynasty_zh: '巴布爾建國', country_zh: '蒙兀兒' },
    { from: 1530, to: 1556, dynasty_zh: '胡馬雍（蘇爾王朝中斷）', country_zh: '蒙兀兒' },
    { from: 1556, to: 1605, dynasty_zh: '阿克巴擴張', country_zh: '蒙兀兒' },
    { from: 1605, to: 1627, dynasty_zh: '賈漢吉爾', country_zh: '蒙兀兒' },
    { from: 1628, to: 1658, dynasty_zh: '沙賈漢（泰姬陵）', country_zh: '蒙兀兒' },
    { from: 1658, to: 1707, dynasty_zh: '奧朗則布（巔峰，南征德干）', country_zh: '蒙兀兒' },
    { from: 1707, to: 1739, dynasty_zh: '衰退（馬拉塔崛起）', country_zh: '蒙兀兒' },
    { from: 1739, to: 1761, dynasty_zh: '納迪爾沙洗劫德里', country_zh: '蒙兀兒' },
    { from: 1761, to: 1857, dynasty_zh: '末期（英印逐步控制）', country_zh: '蒙兀兒' },
  ],

  // ============================================================
  // 薩法維
  // ============================================================
  'Safavid Empire': [
    { from: 1501, to: 1524, dynasty_zh: '伊斯瑪儀一世建國', country_zh: '薩法維' },
    { from: 1524, to: 1576, dynasty_zh: '塔赫馬斯普一世', country_zh: '薩法維' },
    { from: 1576, to: 1588, dynasty_zh: '動盪期', country_zh: '薩法維' },
    { from: 1588, to: 1629, dynasty_zh: '阿巴斯一世（巔峰）', country_zh: '薩法維' },
    { from: 1629, to: 1666, dynasty_zh: '薩菲／阿巴斯二世', country_zh: '薩法維' },
    { from: 1666, to: 1722, dynasty_zh: '衰退（霍塔克入侵滅亡）', country_zh: '薩法維' },
  ],

  // ============================================================
  // 日本
  // ============================================================
  'Japan': [
    { from: 800, to: 1068, dynasty_zh: '平安／藤原攝關', country_zh: '日本' },
    { from: 1068, to: 1185, dynasty_zh: '院政／平氏', country_zh: '日本' },
    { from: 1185, to: 1333, dynasty_zh: '鎌倉幕府', country_zh: '日本' },
    { from: 1333, to: 1336, dynasty_zh: '建武新政', country_zh: '日本' },
    { from: 1336, to: 1467, dynasty_zh: '室町幕府', country_zh: '日本' },
    { from: 1467, to: 1568, dynasty_zh: '戰國時代', country_zh: '日本' },
    { from: 1568, to: 1603, dynasty_zh: '安土桃山（信長／秀吉）', country_zh: '日本' },
    { from: 1603, to: 1867, dynasty_zh: '德川幕府', country_zh: '日本' },
    { from: 1868, to: 1889, dynasty_zh: '明治維新', country_zh: '日本' },
    { from: 1889, to: 1911, dynasty_zh: '明治後期（甲午、日俄）', country_zh: '日本' },
    { from: 1912, to: 1925, dynasty_zh: '大正民主', country_zh: '日本' },
    { from: 1926, to: 1944, dynasty_zh: '昭和（軍國／太平洋戰爭）', country_zh: '日本' },
    { from: 1947, to: 1989, dynasty_zh: '戰後昭和（經濟成長）', country_zh: '日本' },
    { from: 1989, to: 2019, dynasty_zh: '平成（泡沫破裂／失落 30 年）', country_zh: '日本' },
    { from: 2019, to: 9999, dynasty_zh: '令和', country_zh: '日本' },
  ],
  'Imperial Japan': [
    { from: 1868, to: 1894, dynasty_zh: '明治前期', country_zh: '大日本帝國' },
    { from: 1894, to: 1905, dynasty_zh: '甲午到日俄', country_zh: '大日本帝國' },
    { from: 1905, to: 1925, dynasty_zh: '日俄後到大正末', country_zh: '大日本帝國' },
    { from: 1926, to: 1937, dynasty_zh: '昭和前期', country_zh: '大日本帝國' },
    { from: 1937, to: 1941, dynasty_zh: '中日戰爭', country_zh: '大日本帝國' },
    { from: 1941, to: 1945, dynasty_zh: '太平洋戰爭', country_zh: '大日本帝國' },
  ],

  // ============================================================
  // 韓國／朝鮮
  // ============================================================
  'Korea': [
    { from: 918, to: 1170, dynasty_zh: '高麗前期', country_zh: '朝鮮半島' },
    { from: 1170, to: 1270, dynasty_zh: '高麗武人政權／蒙古入侵', country_zh: '朝鮮半島' },
    { from: 1270, to: 1392, dynasty_zh: '高麗末（元附庸）', country_zh: '朝鮮半島' },
    { from: 1392, to: 1592, dynasty_zh: '朝鮮前期（世宗）', country_zh: '朝鮮半島' },
    { from: 1592, to: 1598, dynasty_zh: '壬辰倭亂', country_zh: '朝鮮半島' },
    { from: 1599, to: 1894, dynasty_zh: '朝鮮中後期', country_zh: '朝鮮半島' },
    { from: 1897, to: 1909, dynasty_zh: '大韓帝國', country_zh: '朝鮮半島' },
    { from: 1910, to: 1913, dynasty_zh: '日治', country_zh: '朝鮮半島' },
  ],

  // ============================================================
  // 西班牙
  // ============================================================
  'Spain': [
    { from: 1469, to: 1516, dynasty_zh: '雙王時代（斐迪南／伊莎貝拉）', country_zh: '西班牙' },
    { from: 1516, to: 1556, dynasty_zh: '查理一世（神羅查理五世）', country_zh: '西班牙' },
    { from: 1556, to: 1598, dynasty_zh: '腓力二世（黃金時代）', country_zh: '西班牙' },
    { from: 1598, to: 1665, dynasty_zh: '腓力三世／四世（衰退）', country_zh: '西班牙' },
    { from: 1665, to: 1700, dynasty_zh: '卡洛斯二世（哈布斯堡末）', country_zh: '西班牙' },
    { from: 1700, to: 1714, dynasty_zh: '王位繼承戰爭', country_zh: '西班牙' },
    { from: 1714, to: 1808, dynasty_zh: '波旁前期', country_zh: '西班牙' },
    { from: 1808, to: 1814, dynasty_zh: '半島戰爭（拿破崙侵）', country_zh: '西班牙' },
    { from: 1814, to: 1833, dynasty_zh: '斐迪南七世', country_zh: '西班牙' },
    { from: 1833, to: 1868, dynasty_zh: '伊莎貝拉二世', country_zh: '西班牙' },
    { from: 1868, to: 1874, dynasty_zh: '革命到第一共和', country_zh: '西班牙' },
    { from: 1874, to: 1923, dynasty_zh: '波旁復辟', country_zh: '西班牙' },
    { from: 1923, to: 1930, dynasty_zh: '里維拉獨裁', country_zh: '西班牙' },
    { from: 1931, to: 1936, dynasty_zh: '第二共和', country_zh: '西班牙' },
    { from: 1936, to: 1939, dynasty_zh: '內戰', country_zh: '西班牙' },
    { from: 1939, to: 1975, dynasty_zh: '佛朗哥', country_zh: '西班牙' },
    { from: 1975, to: 9999, dynasty_zh: '波旁復辟（民主）', country_zh: '西班牙' },
  ],

  // ============================================================
  // 義大利
  // ============================================================
  'Italy': [
    { from: 1861, to: 1900, dynasty_zh: '統一後（薩伏依王國）', country_zh: '義大利' },
    { from: 1901, to: 1914, dynasty_zh: '自由派時代', country_zh: '義大利' },
    { from: 1914, to: 1918, dynasty_zh: '一戰', country_zh: '義大利' },
    { from: 1922, to: 1943, dynasty_zh: '法西斯（墨索里尼）', country_zh: '義大利王國' },
    { from: 1943, to: 1946, dynasty_zh: '戰後過渡', country_zh: '義大利' },
    { from: 1946, to: 9999, dynasty_zh: '共和', country_zh: '義大利' },
  ],

  // ============================================================
  // 德國
  // ============================================================
  'Germany': [
    { from: 1871, to: 1890, dynasty_zh: '俾斯麥（德意志帝國）', country_zh: '德國' },
    { from: 1890, to: 1914, dynasty_zh: '威廉二世前期', country_zh: '德國' },
    { from: 1914, to: 1918, dynasty_zh: '一戰', country_zh: '德國' },
    { from: 1919, to: 1932, dynasty_zh: '威瑪共和', country_zh: '德國' },
    { from: 1933, to: 1939, dynasty_zh: '納粹前期', country_zh: '德國' },
    { from: 1939, to: 1945, dynasty_zh: '二戰', country_zh: '德國' },
    { from: 1949, to: 1989, dynasty_zh: '西德', country_zh: '德國' },
    { from: 1990, to: 9999, dynasty_zh: '兩德統一後', country_zh: '德國' },
  ],

  // ============================================================
  // 俄羅斯
  // ============================================================
  'Russia': [
    { from: 1991, to: 1999, dynasty_zh: '葉爾欽（休克療法）', country_zh: '俄羅斯聯邦' },
    { from: 2000, to: 9999, dynasty_zh: '普京時代', country_zh: '俄羅斯聯邦' },
  ],
  'Tsardom of Muscovy': [
    { from: 1547, to: 1584, dynasty_zh: '伊凡四世（雷帝）', country_zh: '俄羅斯沙皇國' },
    { from: 1584, to: 1613, dynasty_zh: '混亂時代', country_zh: '俄羅斯沙皇國' },
    { from: 1613, to: 1682, dynasty_zh: '羅曼諾夫早期', country_zh: '俄羅斯沙皇國' },
    { from: 1682, to: 1721, dynasty_zh: '彼得大帝（改革）', country_zh: '俄羅斯沙皇國' },
  ],
  'Russian Empire': [
    { from: 1721, to: 1762, dynasty_zh: '彼得到伊麗莎白', country_zh: '俄羅斯帝國' },
    { from: 1762, to: 1796, dynasty_zh: '葉卡捷琳娜二世', country_zh: '俄羅斯帝國' },
    { from: 1796, to: 1825, dynasty_zh: '保羅／亞歷山大一世（拿破崙戰爭）', country_zh: '俄羅斯帝國' },
    { from: 1825, to: 1855, dynasty_zh: '尼古拉一世', country_zh: '俄羅斯帝國' },
    { from: 1855, to: 1881, dynasty_zh: '亞歷山大二世（廢農奴）', country_zh: '俄羅斯帝國' },
    { from: 1881, to: 1894, dynasty_zh: '亞歷山大三世', country_zh: '俄羅斯帝國' },
    { from: 1894, to: 1917, dynasty_zh: '尼古拉二世（日俄／一戰／革命）', country_zh: '俄羅斯帝國' },
  ],

  // ============================================================
  // 印度
  // ============================================================
  'India': [
    { from: 1783, to: 1857, dynasty_zh: '英屬東印度公司', country_zh: '印度' },
    { from: 1858, to: 1947, dynasty_zh: '英屬印度（直轄）', country_zh: '印度' },
    { from: 1947, to: 1964, dynasty_zh: '尼赫魯時代', country_zh: '印度' },
    { from: 1964, to: 1991, dynasty_zh: '英迪拉‧甘地家族時代', country_zh: '印度' },
    { from: 1991, to: 9999, dynasty_zh: '經濟改革時代', country_zh: '印度' },
  ],

  // ============================================================
  // 土耳其
  // ============================================================
  'Turkey': [
    { from: 1938, to: 1950, dynasty_zh: '凱末爾末期／伊諾努', country_zh: '土耳其' },
    { from: 1950, to: 1980, dynasty_zh: '多黨制（屢次政變）', country_zh: '土耳其' },
    { from: 1980, to: 2002, dynasty_zh: '軍人主導', country_zh: '土耳其' },
    { from: 2002, to: 9999, dynasty_zh: '艾爾段時代（AKP）', country_zh: '土耳其' },
  ],
  'Ottoman Sultanate': [
    { from: 1920, to: 1922, dynasty_zh: '奧斯曼末（蘇丹政權）', country_zh: '土耳其' },
    { from: 1923, to: 1937, dynasty_zh: '凱末爾共和', country_zh: '土耳其' },
  ],

  // ============================================================
  // 葡萄牙 — 海上帝國
  // ============================================================
  'Portugal': [
    { from: 1139, to: 1279, dynasty_zh: '勃艮第王朝（建國／收復失地）', country_zh: '葡萄牙' },
    { from: 1279, to: 1383, dynasty_zh: '勃艮第晚期', country_zh: '葡萄牙' },
    { from: 1385, to: 1415, dynasty_zh: '阿維什前期（若昂一世）', country_zh: '葡萄牙' },
    { from: 1415, to: 1495, dynasty_zh: '海上探險（亨利王子／好望角）', country_zh: '葡萄牙' },
    { from: 1495, to: 1521, dynasty_zh: '曼努埃爾一世（達伽馬／巴西）', country_zh: '葡萄牙' },
    { from: 1521, to: 1580, dynasty_zh: '海上帝國巔峰', country_zh: '葡萄牙' },
    { from: 1580, to: 1640, dynasty_zh: '伊比利亞聯合（哈布斯堡）', country_zh: '葡萄牙' },
    { from: 1640, to: 1668, dynasty_zh: '復國戰爭（布拉甘薩）', country_zh: '葡萄牙' },
    { from: 1668, to: 1750, dynasty_zh: '巴西金礦時代', country_zh: '葡萄牙' },
    { from: 1750, to: 1777, dynasty_zh: '龐巴爾改革', country_zh: '葡萄牙' },
    { from: 1777, to: 1807, dynasty_zh: '末期君主', country_zh: '葡萄牙' },
    { from: 1807, to: 1820, dynasty_zh: '半島戰爭／王室遷巴西', country_zh: '葡萄牙' },
    { from: 1820, to: 1834, dynasty_zh: '自由派革命', country_zh: '葡萄牙' },
    { from: 1834, to: 1910, dynasty_zh: '立憲君主', country_zh: '葡萄牙' },
    { from: 1910, to: 1926, dynasty_zh: '第一共和（混亂）', country_zh: '葡萄牙' },
    { from: 1926, to: 1974, dynasty_zh: '薩拉查獨裁', country_zh: '葡萄牙' },
    { from: 1974, to: 9999, dynasty_zh: '康乃馨革命後', country_zh: '葡萄牙' },
  ],

  // ============================================================
  // 法蘭克／加洛林
  // ============================================================
  'Frankish Kingdom': [
    { from: 481, to: 511, dynasty_zh: '克洛維一世（建國／皈依）', country_zh: '法蘭克' },
    { from: 511, to: 561, dynasty_zh: '克洛泰爾一世（再統一）', country_zh: '法蘭克' },
    { from: 561, to: 687, dynasty_zh: '墨洛溫分裂（紐斯特里亞／奧斯特拉西亞／勃艮第）', country_zh: '法蘭克' },
    { from: 687, to: 751, dynasty_zh: '宮相實控（查理‧馬特擊敗阿拉伯）', country_zh: '法蘭克' },
    { from: 751, to: 799, dynasty_zh: '加洛林（丕平／早期查理曼）', country_zh: '法蘭克' },
  ],
  'Carolingian Empire': [
    { from: 800, to: 814, dynasty_zh: '查理曼加冕（西方皇帝）', country_zh: '加洛林' },
    { from: 814, to: 840, dynasty_zh: '虔誠者路易', country_zh: '加洛林' },
    { from: 840, to: 843, dynasty_zh: '繼承戰爭', country_zh: '加洛林' },
    { from: 843, to: 887, dynasty_zh: '凡爾登條約後（三分）', country_zh: '加洛林' },
    { from: 887, to: 999, dynasty_zh: '末期分裂', country_zh: '加洛林' },
  ],

  // ============================================================
  // 荷蘭
  // ============================================================
  'Dutch Republic': [
    { from: 1568, to: 1609, dynasty_zh: '八十年戰爭前期', country_zh: '荷蘭共和' },
    { from: 1609, to: 1648, dynasty_zh: '十二年休戰到威斯特伐利亞獨立', country_zh: '荷蘭共和' },
    { from: 1648, to: 1672, dynasty_zh: '黃金時代', country_zh: '荷蘭共和' },
    { from: 1672, to: 1713, dynasty_zh: '災年到西班牙王位繼承戰', country_zh: '荷蘭共和' },
    { from: 1713, to: 1780, dynasty_zh: '衰退期', country_zh: '荷蘭共和' },
    { from: 1780, to: 1795, dynasty_zh: '第四次英荷戰爭到滅亡', country_zh: '荷蘭共和' },
  ],
  'Netherlands': [
    { from: 1715, to: 1795, dynasty_zh: '共和末期', country_zh: '荷蘭' },
    { from: 1795, to: 1806, dynasty_zh: '巴達維亞共和', country_zh: '荷蘭' },
    { from: 1806, to: 1810, dynasty_zh: '荷蘭王國（拿破崙弟）', country_zh: '荷蘭' },
    { from: 1815, to: 1830, dynasty_zh: '尼德蘭聯合王國（含比利時）', country_zh: '荷蘭' },
    { from: 1830, to: 1914, dynasty_zh: '比利時獨立後', country_zh: '荷蘭' },
    { from: 1914, to: 1940, dynasty_zh: '中立（一戰／戰間期）', country_zh: '荷蘭' },
    { from: 1940, to: 1945, dynasty_zh: '德占', country_zh: '荷蘭' },
    { from: 1945, to: 9999, dynasty_zh: '戰後', country_zh: '荷蘭' },
  ],

  // ============================================================
  // 西非帝國
  // ============================================================
  'Mali': [
    { from: 1235, to: 1255, dynasty_zh: '松迪亞塔建國', country_zh: '馬利' },
    { from: 1255, to: 1312, dynasty_zh: '早期擴張', country_zh: '馬利' },
    { from: 1312, to: 1337, dynasty_zh: '曼薩‧穆薩黃金時代', country_zh: '馬利' },
    { from: 1337, to: 1464, dynasty_zh: '衰退（桑海崛起）', country_zh: '馬利' },
    { from: 1464, to: 1599, dynasty_zh: '桑海取代（小馬利殘餘）', country_zh: '馬利' },
    { from: 1880, to: 1959, dynasty_zh: '法屬蘇丹', country_zh: '馬利' },
    { from: 1960, to: 1991, dynasty_zh: '獨立／一黨制', country_zh: '馬利' },
    { from: 1991, to: 9999, dynasty_zh: '多黨制（薩赫勒衝突）', country_zh: '馬利' },
  ],
  'Songhai': [
    { from: 1492, to: 1528, dynasty_zh: '宋尼‧阿里建國', country_zh: '桑海' },
    { from: 1492, to: 1492, dynasty_zh: '阿斯基亞‧穆罕默德篡位', country_zh: '桑海' },
    { from: 1493, to: 1528, dynasty_zh: '阿斯基亞改革', country_zh: '桑海' },
    { from: 1528, to: 1591, dynasty_zh: '中期擴張', country_zh: '桑海' },
    { from: 1591, to: 1591, dynasty_zh: '通迪比戰役（摩洛哥滅）', country_zh: '桑海' },
    { from: 1591, to: 1700, dynasty_zh: '殘餘小國', country_zh: '桑海' },
    { from: 1700, to: 1814, dynasty_zh: '邊緣化', country_zh: '桑海' },
  ],
  'Kanem': [
    { from: 800, to: 1075, dynasty_zh: '建立（薩伊夫王朝）', country_zh: '加涅姆' },
    { from: 1075, to: 1085, dynasty_zh: '杜納馬‧迪巴萊米（皈依伊斯蘭）', country_zh: '加涅姆' },
    { from: 1085, to: 1259, dynasty_zh: '中世紀擴張', country_zh: '加涅姆' },
    { from: 1259, to: 1278, dynasty_zh: '末期（被布拉拉人逐出）', country_zh: '加涅姆' },
  ],
  'Bornu-Kanem': [
    { from: 1279, to: 1380, dynasty_zh: '重建博爾努（卡涅姆東遷）', country_zh: '博爾努-加涅姆' },
    { from: 1380, to: 1571, dynasty_zh: '中期', country_zh: '博爾努-加涅姆' },
    { from: 1571, to: 1603, dynasty_zh: '伊德里斯‧阿洛馬巔峰', country_zh: '博爾努-加涅姆' },
    { from: 1603, to: 1808, dynasty_zh: '衰退期', country_zh: '博爾努-加涅姆' },
    { from: 1808, to: 1846, dynasty_zh: '富拉尼聖戰／重建', country_zh: '博爾努-加涅姆' },
    { from: 1846, to: 1879, dynasty_zh: '謝胡末期', country_zh: '博爾努-加涅姆' },
  ],

  // ============================================================
  // 衣索比亞
  // ============================================================
  'Ethiopia': [
    { from: 1270, to: 1434, dynasty_zh: '所羅門王朝復辟', country_zh: '衣索比亞' },
    { from: 1434, to: 1543, dynasty_zh: '紮拉‧雅各布到阿達爾戰爭', country_zh: '衣索比亞' },
    { from: 1543, to: 1632, dynasty_zh: '紮拉‧雅各布後／葡萄牙耶穌會', country_zh: '衣索比亞' },
    { from: 1632, to: 1769, dynasty_zh: '貢德爾時期', country_zh: '衣索比亞' },
    { from: 1769, to: 1855, dynasty_zh: '王公時代（分裂）', country_zh: '衣索比亞' },
    { from: 1855, to: 1868, dynasty_zh: '特沃德羅斯二世（重新統一）', country_zh: '衣索比亞' },
    { from: 1868, to: 1889, dynasty_zh: '約翰尼斯四世', country_zh: '衣索比亞' },
    { from: 1889, to: 1913, dynasty_zh: '孟尼利克二世（阿杜瓦勝義）', country_zh: '衣索比亞' },
    { from: 1913, to: 1935, dynasty_zh: '海爾‧塞拉西攝政／登基', country_zh: '衣索比亞' },
    { from: 1935, to: 1941, dynasty_zh: '義大利占領', country_zh: '衣索比亞' },
    { from: 1941, to: 1974, dynasty_zh: '海爾‧塞拉西復辟', country_zh: '衣索比亞' },
    { from: 1974, to: 1991, dynasty_zh: '德爾格軍政府', country_zh: '衣索比亞' },
    { from: 1991, to: 9999, dynasty_zh: 'EPRDF／後 EPRDF', country_zh: '衣索比亞' },
  ],

  // ============================================================
  // 蒙古後續：伊兒汗／帖木兒
  // ============================================================
  'Ilkhanate': [
    { from: 1256, to: 1265, dynasty_zh: '旭烈兀建立（滅阿巴斯）', country_zh: '伊兒汗' },
    { from: 1265, to: 1295, dynasty_zh: '阿八哈到阿魯渾', country_zh: '伊兒汗' },
    { from: 1295, to: 1304, dynasty_zh: '合贊汗（皈依伊斯蘭）', country_zh: '伊兒汗' },
    { from: 1304, to: 1335, dynasty_zh: '完者都／不賽因', country_zh: '伊兒汗' },
    { from: 1335, to: 1399, dynasty_zh: '分裂（札剌亦兒／穆扎法爾／丘班）', country_zh: '伊兒汗' },
  ],
  'Timurid Empire': [
    { from: 1370, to: 1405, dynasty_zh: '帖木兒（征服）', country_zh: '帖木兒' },
    { from: 1405, to: 1447, dynasty_zh: '沙哈魯（穩定／文化巔峰）', country_zh: '帖木兒' },
    { from: 1447, to: 1469, dynasty_zh: '兀魯伯／烏茲別克擴張', country_zh: '帖木兒' },
    { from: 1469, to: 1491, dynasty_zh: '末期（白羊崛起）', country_zh: '帖木兒' },
  ],
  'Timurid Emirates': [
    { from: 1492, to: 1500, dynasty_zh: '分裂諸埃米爾', country_zh: '帖木兒' },
    { from: 1500, to: 1529, dynasty_zh: '巴布爾流亡到建蒙兀兒', country_zh: '帖木兒' },
  ],

  // ============================================================
  // 印度諸朝代
  // ============================================================
  'Mauryan Empire': [
    { from: -322, to: -298, dynasty_zh: '月護王建國', country_zh: '孔雀' },
    { from: -298, to: -272, dynasty_zh: '賓頭娑羅', country_zh: '孔雀' },
    { from: -268, to: -232, dynasty_zh: '阿育王（佛教推廣）', country_zh: '孔雀' },
    { from: -232, to: -185, dynasty_zh: '衰退到滅亡', country_zh: '孔雀' },
  ],
  'Gupta Empire': [
    { from: 320, to: 350, dynasty_zh: '旃陀羅笈多一世', country_zh: '笈多' },
    { from: 350, to: 375, dynasty_zh: '海護王（征服）', country_zh: '笈多' },
    { from: 375, to: 415, dynasty_zh: '旃陀羅笈多二世（黃金時代）', country_zh: '笈多' },
    { from: 415, to: 467, dynasty_zh: '鳩摩羅笈多／塞犍陀笈多（抗匈那）', country_zh: '笈多' },
    { from: 467, to: 599, dynasty_zh: '衰退（匈那入侵）', country_zh: '笈多' },
  ],
  'Sultanate of Delhi': [
    { from: 1206, to: 1290, dynasty_zh: '奴隸王朝', country_zh: '德里蘇丹' },
    { from: 1290, to: 1320, dynasty_zh: '卡爾吉王朝', country_zh: '德里蘇丹' },
    { from: 1320, to: 1414, dynasty_zh: '圖格魯克王朝', country_zh: '德里蘇丹' },
    { from: 1414, to: 1451, dynasty_zh: '賽義德王朝（帖木兒劫後）', country_zh: '德里蘇丹' },
    { from: 1451, to: 1526, dynasty_zh: '洛迪王朝（被巴布爾滅）', country_zh: '德里蘇丹' },
  ],
  'Chola state': [
    { from: 1000, to: 1014, dynasty_zh: '羅闍羅闍一世', country_zh: '朱羅' },
    { from: 1014, to: 1044, dynasty_zh: '羅貞陀羅一世（征東南亞）', country_zh: '朱羅' },
    { from: 1044, to: 1118, dynasty_zh: '中期擴張', country_zh: '朱羅' },
    { from: 1118, to: 1279, dynasty_zh: '衰退（潘地亞崛起）', country_zh: '朱羅' },
  ],
  'Cholas': [
    { from: 500, to: 850, dynasty_zh: '早期（中朱羅）', country_zh: '朱羅' },
    { from: 850, to: 1199, dynasty_zh: '帝國朱羅', country_zh: '朱羅' },
  ],
  'Pallavas': [
    { from: 500, to: 728, dynasty_zh: '中期', country_zh: '帕拉瓦' },
    { from: 728, to: 799, dynasty_zh: '末期（朱羅崛起）', country_zh: '帕拉瓦' },
  ],
  'Pallava state': [
    { from: 500, to: 799, dynasty_zh: '帕拉瓦', country_zh: '帕拉瓦' },
  ],
  'Palas': [
    { from: 750, to: 850, dynasty_zh: '建立（瞿波羅／達摩波羅）', country_zh: '波羅' },
    { from: 850, to: 950, dynasty_zh: '提婆波羅巔峰', country_zh: '波羅' },
    { from: 950, to: 1071, dynasty_zh: '衰退', country_zh: '波羅' },
    { from: 1071, to: 1162, dynasty_zh: '羅摩波羅復興', country_zh: '波羅' },
    { from: 1162, to: 1199, dynasty_zh: '末期（被斯那滅）', country_zh: '波羅' },
  ],
  'Vijayanagara': [
    { from: 1336, to: 1485, dynasty_zh: '建立（桑伽馬王朝）', country_zh: '毗奢耶那伽羅' },
    { from: 1485, to: 1505, dynasty_zh: '薩魯瓦王朝', country_zh: '毗奢耶那伽羅' },
    { from: 1505, to: 1565, dynasty_zh: '圖盧瓦王朝（克里希納提婆‧拉亞巔峰）', country_zh: '毗奢耶那伽羅' },
    { from: 1565, to: 1565, dynasty_zh: '塔利科塔戰役（決定性敗）', country_zh: '毗奢耶那伽羅' },
    { from: 1565, to: 1699, dynasty_zh: '阿拉維杜末期', country_zh: '毗奢耶那伽羅' },
  ],
  'Maratha Confederacy': [
    { from: 1674, to: 1707, dynasty_zh: '希瓦吉建國／與蒙兀兒對抗', country_zh: '馬拉塔' },
    { from: 1707, to: 1761, dynasty_zh: '佩什瓦時代（巔峰）', country_zh: '馬拉塔' },
    { from: 1761, to: 1761, dynasty_zh: '第三次帕尼帕特戰役（敗於阿富汗）', country_zh: '馬拉塔' },
    { from: 1761, to: 1818, dynasty_zh: '聯邦衰退到英印滅', country_zh: '馬拉塔' },
    { from: 1818, to: 1879, dynasty_zh: '英印統治', country_zh: '馬拉塔' },
  ],
  'Sikhs': [
    { from: 1799, to: 1801, dynasty_zh: '蘭吉特‧辛格起', country_zh: '錫克' },
    { from: 1801, to: 1814, dynasty_zh: '錫克帝國早期', country_zh: '錫克' },
  ],

  // ============================================================
  // 東南亞
  // ============================================================
  'Khmer Empire': [
    { from: 802, to: 889, dynasty_zh: '闍耶跋摩二世（建國）', country_zh: '高棉' },
    { from: 889, to: 1010, dynasty_zh: '早期（耶輸跋摩）', country_zh: '高棉' },
    { from: 1010, to: 1080, dynasty_zh: '蘇耶跋摩一世', country_zh: '高棉' },
    { from: 1113, to: 1150, dynasty_zh: '蘇耶跋摩二世（吳哥窟）', country_zh: '高棉' },
    { from: 1181, to: 1218, dynasty_zh: '闍耶跋摩七世（巔峰／大乘佛教）', country_zh: '高棉' },
    { from: 1218, to: 1431, dynasty_zh: '衰退（被泰人攻陷吳哥）', country_zh: '高棉' },
    { from: 1431, to: 1491, dynasty_zh: '末期遷都金邊', country_zh: '高棉' },
  ],
  'Srivijaya Empire': [
    { from: 800, to: 900, dynasty_zh: '早期', country_zh: '室利佛逝' },
    { from: 900, to: 1025, dynasty_zh: '貿易帝國巔峰', country_zh: '室利佛逝' },
    { from: 1025, to: 1025, dynasty_zh: '朱羅海上突襲', country_zh: '室利佛逝' },
    { from: 1025, to: 1290, dynasty_zh: '衰退', country_zh: '室利佛逝' },
    { from: 1290, to: 1491, dynasty_zh: '滿者伯夷取代', country_zh: '室利佛逝' },
  ],
  'Bagan': [
    { from: 1044, to: 1112, dynasty_zh: '阿奴律陀（建國）', country_zh: '蒲甘' },
    { from: 1112, to: 1167, dynasty_zh: '中期', country_zh: '蒲甘' },
    { from: 1167, to: 1287, dynasty_zh: '巔峰到蒙古入侵滅亡', country_zh: '蒲甘' },
  ],
  'Ayutthaya': [
    { from: 1351, to: 1438, dynasty_zh: '烏通王建國', country_zh: '阿瑜陀耶' },
    { from: 1438, to: 1569, dynasty_zh: '擴張期', country_zh: '阿瑜陀耶' },
    { from: 1569, to: 1593, dynasty_zh: '東吁占領／納黎萱獨立', country_zh: '阿瑜陀耶' },
    { from: 1593, to: 1688, dynasty_zh: '巴薩通／那萊（中興）', country_zh: '阿瑜陀耶' },
    { from: 1688, to: 1767, dynasty_zh: '末期（緬甸滅）', country_zh: '阿瑜陀耶' },
    { from: 1767, to: 1782, dynasty_zh: '吞武里王朝（達信）', country_zh: '阿瑜陀耶' },
  ],
  'Đại Việt': [
    { from: 1009, to: 1225, dynasty_zh: '李朝', country_zh: '大越' },
    { from: 1225, to: 1400, dynasty_zh: '陳朝（抗蒙）', country_zh: '大越' },
    { from: 1400, to: 1407, dynasty_zh: '胡朝', country_zh: '大越' },
    { from: 1407, to: 1428, dynasty_zh: '明朝占領', country_zh: '大越' },
    { from: 1428, to: 1527, dynasty_zh: '黎朝前期（黎利／聖宗黃金時代）', country_zh: '大越' },
    { from: 1527, to: 1592, dynasty_zh: '莫朝篡位', country_zh: '大越' },
    { from: 1592, to: 1771, dynasty_zh: '黎朝後期（鄭阮分治）', country_zh: '大越' },
    { from: 1771, to: 1802, dynasty_zh: '西山起義', country_zh: '大越' },
    { from: 1802, to: 1814, dynasty_zh: '阮朝建立', country_zh: '大越' },
  ],
  'Goryeo': [
    { from: 1200, to: 1270, dynasty_zh: '武人政權／抗蒙', country_zh: '高麗' },
    { from: 1270, to: 1278, dynasty_zh: '元附庸', country_zh: '高麗' },
  ],
  'Funan': [
    { from: 500, to: 627, dynasty_zh: '末期（真臘崛起）', country_zh: '扶南' },
    { from: 627, to: 699, dynasty_zh: '被真臘吸收', country_zh: '扶南' },
  ],
  'Pyu state': [
    { from: 800, to: 832, dynasty_zh: '驃國末期', country_zh: '驃國' },
    { from: 832, to: 1044, dynasty_zh: '南詔毀後緬族崛起', country_zh: '驃國' },
    { from: 1044, to: 1278, dynasty_zh: '蒲甘王朝時期', country_zh: '驃國' },
  ],

  // ============================================================
  // 美洲
  // ============================================================
  'Inca Empire': [
    { from: 1438, to: 1471, dynasty_zh: '帕查庫蒂（建國／擴張）', country_zh: '印加' },
    { from: 1471, to: 1493, dynasty_zh: '圖帕克‧印加（巔峰）', country_zh: '印加' },
    { from: 1493, to: 1525, dynasty_zh: '瓦伊納‧卡帕克', country_zh: '印加' },
    { from: 1525, to: 1532, dynasty_zh: '內戰（瓦斯卡爾 vs 阿塔瓦爾帕）', country_zh: '印加' },
    { from: 1532, to: 1533, dynasty_zh: '皮薩羅征服', country_zh: '印加' },
    { from: 1533, to: 1572, dynasty_zh: '比爾卡班巴殘餘王國', country_zh: '印加' },
  ],
  'Aztec Empire': [
    { from: 1428, to: 1440, dynasty_zh: '三方聯盟建立（伊茨科亞特爾）', country_zh: '阿茲特克' },
    { from: 1440, to: 1469, dynasty_zh: '蒙特蘇馬一世', country_zh: '阿茲特克' },
    { from: 1469, to: 1502, dynasty_zh: '阿沙亞卡特爾／提佐克／阿維特索特爾', country_zh: '阿茲特克' },
    { from: 1502, to: 1520, dynasty_zh: '蒙特蘇馬二世（巔峰）', country_zh: '阿茲特克' },
    { from: 1520, to: 1521, dynasty_zh: '科爾特斯征服（特諾奇蒂特蘭陷落）', country_zh: '阿茲特克' },
    { from: 1521, to: 1529, dynasty_zh: '殘存附庸期', country_zh: '阿茲特克' },
  ],
}

/**
 * 查詢某 polygon 名稱在某年的朝代標籤。
 * @returns '安史之亂（唐）' | null
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
