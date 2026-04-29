-- ============================================================
-- 東方教會主要宗主教座繼承列表
-- GROUP A: 古代東方教會（塞琉西亞—泰西封）、亞克蘇姆
-- GROUP B: 莫斯科東正教、羅馬尼亞東正教
-- ============================================================

-- ============================================================
-- 1. 塞琉西亞—泰西封 / 古代東方教會（Church of the East）
-- 從帕帕·巴爾·阿加伊（約280年）至示孟二十一世（1975年）
-- 注意：1558年後分為以利亞系與示孟系；以利亞系為較古老的傳承
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
-- 早期主教（稱「教長」，papa，非正式宗主教名號）
('帕帕·巴爾·阿加伊', 'Papa bar Aggai', '塞琉西亞—泰西封', '古代東方教會', 1, 280, 329, '自然死亡', '正統', 'Synodicon Orientale; Chronicle of Seert', '東方教會首位最高領袖；確立塞琉西亞—泰西封的首席地位'),
('示孟·巴爾·薩巴厄', 'Shemon bar Sabbae', '塞琉西亞—泰西封', '古代東方教會', 2, 329, 341, '殉道', '正統', 'Martyrdom of Shemon bar Sabbae; Synodicon Orientale', '拒絕為沙普爾二世向基督徒徵收雙倍稅款；被斬首，與數千名基督徒同殉（約341或344年）；後被封聖'),
('沙赫多斯特', 'Shahdost', '塞琉西亞—泰西封', '古代東方教會', 3, 341, 342, '殉道', '正統', 'Synodicon Orientale; Chronicle of Seert', '偕同128位主教、神父及平信徒被捕；沙普爾二世大迫害（339–379）期間殉道'),
('巴爾巴蕭明', 'Barba''shmin', '塞琉西亞—泰西封', '古代東方教會', 4, 343, 346, '殉道', '正統', 'Synodicon Orientale', '示孟·巴爾·薩巴厄之甥；沙普爾二世大迫害期間殉道'),
-- 空位346–363後
('托馬薩', 'Tomarsa', '塞琉西亞—泰西封', '古代東方教會', 5, 363, 371, '自然死亡', '正統', 'Synodicon Orientale', '大迫害末期後繼任（346–363年空位期後）'),
('卡伊約瑪', 'Qayyoma', '塞琉西亞—泰西封', '古代東方教會', 6, 377, 399, '自然死亡', '正統', 'Synodicon Orientale', NULL),
-- 399年後提升為都主教區
('以撒', 'Isaac', '塞琉西亞—泰西封', '古代東方教會', 7, 399, 410, '自然死亡', '正統', 'Synodicon Orientale; Council of Seleucia-Ctesiphon 410', '主持410年塞琉西亞公會議；確立塞琉西亞—泰西封在東方的首席地位'),
('阿哈', 'Ahha', '塞琉西亞—泰西封', '古代東方教會', 8, 410, 414, '自然死亡', '正統', 'Synodicon Orientale', NULL),
('雅赫巴拉哈一世', 'Yahballaha I', '塞琉西亞—泰西封', '古代東方教會', 9, 415, 420, '自然死亡', '正統', 'Synodicon Orientale', NULL),
('瑪納', 'Mana', '塞琉西亞—泰西封', '古代東方教會', 10, 420, 420, '自然死亡', '正統', 'Synodicon Orientale', '在位極短'),
('法爾博赫特', 'Farbokht', '塞琉西亞—泰西封', '古代東方教會', 11, 421, 421, '自然死亡', '正統', 'Synodicon Orientale', '首位獲授「公教宗主教」（Catholicos）頭銜者'),
-- 正式公教宗主教時期
('達迪修', 'Dadisho', '塞琉西亞—泰西封', '古代東方教會', 12, 421, 456, '自然死亡', '正統', 'Synodicon Orientale; Council of 424', '424年公會議宣告東方教會獨立於西方（安提阿）；首位以「公教宗主教」全銜正式治理者'),
('巴博瓦伊', 'Babowai', '塞琉西亞—泰西封', '古代東方教會', 13, 457, 484, '殉道', '正統', 'Chronicle of Seert', '被薩珊波斯王處死'),
('阿卡西烏斯', 'Acacius', '塞琉西亞—泰西封', '古代東方教會', 14, 485, 496, '自然死亡', '正統', 'Chronicle of Seert; Synodicon Orientale', '486年公會議確立東方教會奈斯托里派神學立場；正式脫離羅馬/拜占廷神學'),
('巴拜', 'Babai', '塞琉西亞—泰西封', '古代東方教會', 15, 497, 503, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('西拉', 'Shila', '塞琉西亞—泰西封', '古代東方教會', 16, 503, 523, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('以利沙', 'Elisha', '塞琉西亞—泰西封', '古代東方教會', 17, 524, 537, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('阿巴一世', 'Aba I (Mar Aba I)', '塞琉西亞—泰西封', '古代東方教會', 18, 540, 552, '自然死亡', '正統', 'Chronicle of Seert; Barhebraeus', '重要神學改革者；曾受迫害入獄；後被封聖'),
('若瑟', 'Joseph', '塞琉西亞—泰西封', '古代東方教會', 19, 552, 567, '廢黜', '正統', 'Chronicle of Seert', '被公會議廢黜'),
('以西結', 'Ezekiel', '塞琉西亞—泰西封', '古代東方教會', 20, 570, 581, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依舍雅哈布一世', 'Ishoyahb I', '塞琉西亞—泰西封', '古代東方教會', 21, 582, 595, '自然死亡', '正統', 'Chronicle of Seert', '585年派代表出席君士坦丁堡第三次公會議'),
('薩布里修一世', 'Sabrisho I', '塞琉西亞—泰西封', '古代東方教會', 22, 596, 604, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('額我略', 'Gregory of Kaskar', '塞琉西亞—泰西封', '古代東方教會', 23, 605, 608, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依舍雅哈布二世', 'Ishoyahb II', '塞琉西亞—泰西封', '古代東方教會', 24, 628, 645, '自然死亡', '正統', 'Chronicle of Seert', '阿拉伯征服初期；與穆罕默德據稱有外交往來'),
('瑪雷梅', 'Maremmeh', '塞琉西亞—泰西封', '古代東方教會', 25, 646, 649, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依舍雅哈布三世', 'Ishoyahb III', '塞琉西亞—泰西封', '古代東方教會', 26, 649, 659, '自然死亡', '正統', 'Chronicle of Seert; Thomas of Marga', '重要神學家和禮儀編訂者'),
('吉瓦吉斯一世', 'Giwargis I', '塞琉西亞—泰西封', '古代東方教會', 27, 661, 680, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南一世', 'Yohannan I', '塞琉西亞—泰西封', '古代東方教會', 28, 680, 683, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('赫南尼修一世', 'Hnanisho I', '塞琉西亞—泰西封', '古代東方教會', 29, 686, 698, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('斯利巴—紮哈', 'Sliba-zkha', '塞琉西亞—泰西封', '古代東方教會', 30, 714, 728, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('裴提翁', 'Pethion', '塞琉西亞—泰西封', '古代東方教會', 31, 731, 740, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('阿巴二世', 'Aba II', '塞琉西亞—泰西封', '古代東方教會', 32, 741, 751, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('雅各二世', 'Yaqob II', '塞琉西亞—泰西封', '古代東方教會', 33, 754, 773, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('赫南尼修二世', 'Hnanisho II', '塞琉西亞—泰西封', '古代東方教會', 34, 773, 780, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('提摩太一世', 'Timothy I', '塞琉西亞—泰西封', '古代東方教會', 35, 780, 823, '自然死亡', '正統', 'Chronicle of Seert; Timothy I correspondence', '最重要的公教宗主教之一；著名神學家；曾與阿拔斯哈里發馬赫迪辯論；傳教擴展至中國、印度、蒙古、西藏'),
('依舍·巴爾·農', 'Isho bar Nun', '塞琉西亞—泰西封', '古代東方教會', 36, 823, 828, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('吉瓦吉斯二世', 'Giwargis II', '塞琉西亞—泰西封', '古代東方教會', 37, 828, 831, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('薩布里修二世', 'Sabrisho II', '塞琉西亞—泰西封', '古代東方教會', 38, 831, 835, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('亞伯拉罕二世', 'Abraham II', '塞琉西亞—泰西封', '古代東方教會', 39, 837, 850, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('西奧多西烏斯', 'Theodosius', '塞琉西亞—泰西封', '古代東方教會', 40, 853, 858, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('薩爾吉斯', 'Sargis', '塞琉西亞—泰西封', '古代東方教會', 41, 860, 872, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('埃諾什', 'Enosh', '塞琉西亞—泰西封', '古代東方教會', 42, 877, 884, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南二世', 'Yohannan II', '塞琉西亞—泰西封', '古代東方教會', 43, 884, 892, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南三世', 'Yohannan III', '塞琉西亞—泰西封', '古代東方教會', 44, 893, 899, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南四世', 'Yohannan IV', '塞琉西亞—泰西封', '古代東方教會', 45, 900, 905, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('亞伯拉罕三世', 'Abraham III', '塞琉西亞—泰西封', '古代東方教會', 46, 906, 937, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依瑪努伊一世', 'Emmanuel I', '塞琉西亞—泰西封', '古代東方教會', 47, 937, 960, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('阿布迪修一世', 'Abdisho I', '塞琉西亞—泰西封', '古代東方教會', 48, 963, 986, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('瑪里二世', 'Mari II', '塞琉西亞—泰西封', '古代東方教會', 49, 987, 999, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南五世', 'Yohannan V', '塞琉西亞—泰西封', '古代東方教會', 50, 1000, 1011, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南六世', 'Yohannan VI', '塞琉西亞—泰西封', '古代東方教會', 51, 1012, 1020, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依舍雅哈布四世', 'Ishoyahb IV', '塞琉西亞—泰西封', '古代東方教會', 52, 1020, 1025, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('以利亞一世', 'Eliya I', '塞琉西亞—泰西封', '古代東方教會', 53, 1028, 1049, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('約哈南七世', 'Yohannan VII', '塞琉西亞—泰西封', '古代東方教會', 54, 1049, 1057, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('薩布里修三世', 'Sabrisho III', '塞琉西亞—泰西封', '古代東方教會', 55, 1064, 1072, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('阿布迪修二世', 'Abdisho II', '塞琉西亞—泰西封', '古代東方教會', 56, 1074, 1090, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('瑪基卡一世', 'Makkikha I', '塞琉西亞—泰西封', '古代東方教會', 57, 1092, 1110, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('以利亞二世', 'Eliya II', '塞琉西亞—泰西封', '古代東方教會', 58, 1111, 1132, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('阿布迪修三世', 'Abdisho III', '塞琉西亞—泰西封', '古代東方教會', 59, 1139, 1148, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('依舍雅哈布五世', 'Ishoyahb V', '塞琉西亞—泰西封', '古代東方教會', 60, 1149, 1175, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('以利亞三世', 'Eliya III', '塞琉西亞—泰西封', '古代東方教會', 61, 1176, 1190, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('雅赫巴拉哈二世', 'Yahballaha II', '塞琉西亞—泰西封', '古代東方教會', 62, 1190, 1222, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('薩布里修四世', 'Sabrisho IV', '塞琉西亞—泰西封', '古代東方教會', 63, 1222, 1224, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('薩布里修五世', 'Sabrisho V', '塞琉西亞—泰西封', '古代東方教會', 64, 1226, 1256, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('瑪基卡二世', 'Makkikha II', '塞琉西亞—泰西封', '古代東方教會', 65, 1257, 1265, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('德恩哈一世', 'Denha I', '塞琉西亞—泰西封', '古代東方教會', 66, 1265, 1281, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('雅赫巴拉哈三世', 'Yahballaha III', '塞琉西亞—泰西封', '古代東方教會', 67, 1281, 1317, '自然死亡', '正統', 'Bar Hebraeus; Chronicle of Seert; Raban Sauma narrative', '原名馬古斯；蒙古族（維吾爾裔）；曾出使西方尋求反伊斯蘭同盟；教會在蒙古統治下達到最廣佈道範圍'),
('提摩太二世', 'Timothy II', '塞琉西亞—泰西封', '古代東方教會', 68, 1318, 1332, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('德恩哈二世', 'Denha II', '塞琉西亞—泰西封', '古代東方教會', 69, 1336, 1381, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('示孟二世', 'Shemon II', '塞琉西亞—泰西封', '古代東方教會', 70, 1385, 1405, '自然死亡', '正統', 'Chronicle of Seert', '帖木兒征服後的混亂時期'),
('以利亞四世', 'Eliya IV', '塞琉西亞—泰西封', '古代東方教會', 71, 1405, 1425, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('示孟三世', 'Shemon III', '塞琉西亞—泰西封', '古代東方教會', 72, 1425, 1450, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('示孟四世', 'Shemon IV', '塞琉西亞—泰西封', '古代東方教會', 73, 1450, 1497, '自然死亡', '正統', 'Chronicle of Seert', '確立公教宗主教職位叔傳姪的世襲制'),
('示孟五世', 'Shemon V', '塞琉西亞—泰西封', '古代東方教會', 74, 1497, 1502, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('以利亞五世', 'Eliya V', '塞琉西亞—泰西封', '古代東方教會', 75, 1502, 1503, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('示孟六世', 'Shemon VI', '塞琉西亞—泰西封', '古代東方教會', 76, 1504, 1538, '自然死亡', '正統', 'Chronicle of Seert', NULL),
('示孟七世·依舍雅哈布', 'Shemon VII Ishoyahb', '塞琉西亞—泰西封', '古代東方教會', 77, 1538, 1558, '自然死亡', '正統', 'Chronicle of Seert', '末代統一公教宗主教；1552年示孟八世蘇拉卡出走羅馬導致教會分裂為以利亞系和示孟系（後者成為迦勒底天主教）'),
-- 以利亞系（舊曆派，留在阿爾庫什）
('以利亞六世', 'Eliya VI', '塞琉西亞—泰西封', '古代東方教會', 78, 1558, 1591, '自然死亡', '正統', 'Assemani, BO III', '以利亞系；居阿爾庫什（Alqosh）；反對羅馬合一'),
('以利亞七世', 'Eliya VII', '塞琉西亞—泰西封', '古代東方教會', 79, 1591, 1617, '自然死亡', '正統', 'Assemani, BO III', '以利亞系'),
('以利亞八世', 'Eliya VIII', '塞琉西亞—泰西封', '古代東方教會', 80, 1617, 1660, '自然死亡', '正統', 'Assemani, BO III', '以利亞系'),
('以利亞九世', 'Eliya IX', '塞琉西亞—泰西封', '古代東方教會', 81, 1660, 1700, '自然死亡', '正統', 'Assemani, BO III', '以利亞系'),
('以利亞十世', 'Eliya X', '塞琉西亞—泰西封', '古代東方教會', 82, 1700, 1722, '自然死亡', '正統', 'Assemani, BO III', '以利亞系'),
('以利亞十一世', 'Eliya XI', '塞琉西亞—泰西封', '古代東方教會', 83, 1722, 1778, '自然死亡', '正統', 'Assemani, BO III', '以利亞系；在位最長（56年）'),
('以利亞十二世', 'Eliya XII', '塞琉西亞—泰西封', '古代東方教會', 84, 1778, 1804, '自然死亡', '正統', 'Assemani, BO III', '以利亞系末代；其繼任者霍爾米茲德最終帶領信眾並入迦勒底天主教'),
('約哈南八世·霍爾米茲德', 'Yohannan VIII Hormizd', '塞琉西亞—泰西封', '古代東方教會', 85, 1780, 1830, '自然死亡', '正統', 'Assemani, BO III', '示孟—以利亞兩系合流後的最後宗主教；1830年正式帶領信眾歸入迦勒底天主教教會'),
-- 示孟系（舊曆）繼承
('示孟十八世·盧比爾', 'Shimun XVIII Rubil', '塞琉西亞—泰西封', '古代東方教會', 86, 1861, 1903, '自然死亡', '正統', 'Wigram, The Assyrians and their Neighbours', '示孟系；居哈卡里山區（今土耳其東南部）'),
('示孟十九世·本雅明', 'Shimun XIX Benyamin', '塞琉西亞—泰西封', '古代東方教會', 87, 1903, 1918, '殉道', '正統', 'Wigram, The Assyrians; Naayem, Shall this Nation die?', '一戰期間帶領亞述人抵抗奧斯曼土耳其；1918年3月3日被庫爾德酋長西米特科（Simko Shikak）暗殺'),
('示孟二十世·保羅', 'Shimun XX Paulos', '塞琉西亞—泰西封', '古代東方教會', 88, 1918, 1920, '自然死亡', '正統', 'Assyrian records', '在位僅兩年；教會流離失所時期'),
('示孟二十一世·以賽', 'Shimun XXI Eshai', '塞琉西亞—泰西封', '古代東方教會', 89, 1920, 1975, '殉道', '正統', 'Assyrian records; Chicago Tribune 1975', '7歲繼位；流亡伊拉克、塞浦路斯、美國；在其任內（1976年）教會決定脫離世襲制選舉宗主教；1975年11月6日在舊金山被刺殺');

-- 設定前任關聯
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '塞琉西亞—泰西封' AND church = '古代東方教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 2. 塞琉西亞—泰西封 / 東方教會（亞述）
-- 1976年起不再世襲，公會議選舉
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('馬爾·丁哈四世', 'Mar Dinkha IV', '塞琉西亞—泰西封', '東方教會（亞述）', 1, 1976, 2015, '逝世', '正統', 'Assyrian Church of the East official records', '首位非示孟家族出身的宗主教；1976年10月17日在倫敦祝聖；居美國伊利諾伊州莫頓格羅夫；1994年與羅馬公教會簽署《亞述—迦勒底基督論公告》（Common Christological Declaration）；2015年3月26日逝世'),
('馬爾·吉瓦吉斯三世', 'Mar Gewargis III Sliwa', '塞琉西亞—泰西封', '東方教會（亞述）', 2, 2015, 2021, '退休', '正統', 'Assyrian Church of the East official records', '2015年9月27日祝聖；任內遷宗主教座回伊拉克（亞爾比勒）；2021年9月辭職讓位'),
('馬爾·阿瓦三世', 'Mar Awa III (Awa Royel)', '塞琉西亞—泰西封', '東方教會（亞述）', 3, 2021, NULL, NULL, '正統', 'Assyrian Church News 2021', '第122任公教宗主教；2021年9月8日當選，13日於亞爾比勒祝聖；曾任加利福尼亞主教及聖公會秘書');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '塞琉西亞—泰西封' AND church = '東方教會（亞述）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 3. 亞克蘇姆 / 衣索比亞正統特瓦赫多教會
-- 1959年宣告自主（autocephalous）後歷任宗主教
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('巴西琉斯', 'Abune Basilios', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 1, 1959, 1970, '逝世', '正統', 'Ethiopian Orthodox Church records; Wikipedia: Pope Basilios', '首任宗主教；1948年由亞歷山大科普特教宗授予大主教職，1959年升為宗主教；海勒·塞拉西皇帝支持'),
('德奧菲洛斯', 'Abune Theophilos', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 2, 1971, 1976, '廢黜', '正統', 'Ethiopian Orthodox Church records; Amnesty International', '1976年被德爾格馬克思主義軍政府逮捕廢黜；1979年在獄中秘密被勒死殉道；2021年遺體重新安葬，官方承認其殉道'),
('德克萊·海馬諾特', 'Abune Takla Haymanot', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 3, 1976, 1988, '逝世', '正統', 'Ethiopian Orthodox Church records', '德爾格政府任命；在任期間教會受共產政權嚴格管控'),
('默科里歐斯', 'Abune Merkorios', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 4, 1988, 1991, '廢黜', '正統', 'Ethiopian Orthodox Church records', '1991年德爾格政府倒台後被廢黜；流亡美國，建立流亡教會（1991–2018）；2018年與宗主教馬提亞斯達成和解，同意雙重宗主教安排直至2022年逝世'),
('保羅斯', 'Abune Paulos', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 5, 1992, 2012, '逝世', '正統', 'Ethiopian Orthodox Church records; WCC records', '德爾格倒台後由EPRDF政府支持選出；任內積極推動國際宗教對話；其合法性長期受默科里歐斯流亡派質疑；2012年8月16日猝逝'),
('馬提亞斯', 'Abune Mathias', '亞克蘇姆', '衣索比亞正統特瓦赫多教會', 6, 2013, NULL, NULL, '正統', 'Ethiopian Orthodox Church records', '2013年2月27日就任；2018年默科里歐斯回國，雙方同意共擔宗主教頭銜直至默科里歐斯2022年逝世');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '亞克蘇姆' AND church = '衣索比亞正統特瓦赫多教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 4. 莫斯科 / 東正教（俄羅斯）
-- 莫斯科宗主教——1589年設立，1700–1917年彼得大帝廢置改設最高宗教委員會，1917年恢復
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('約伯', 'Job (Hiob) of Moscow', '莫斯科', '東正教（俄羅斯）', 1, 1589, 1605, '廢黜', '正統', 'Russian Orthodox Church records; Karamzin, History of Russia', '首任莫斯科宗主教；1605年被偽德米特里一世（False Dmitry I）廢黜流放；後被封聖'),
('赫爾莫根', 'Hermogenes of Moscow', '莫斯科', '東正教（俄羅斯）', 2, 1606, 1612, '殉道', '正統', 'Russian Orthodox Church records; Solovyev, History of Russia', '波蘭入侵（混亂時代）期間拒絕承認波蘭人佔領俄羅斯；被囚禁於奇跡修道院後絕食殉道；後被封聖'),
('費拉列特', 'Filaret (Fyodor Romanov)', '莫斯科', '東正教（俄羅斯）', 3, 1619, 1633, '逝世', '正統', 'Russian Orthodox Church records', '沙皇米哈伊爾·羅曼諾夫之父；曾被波蘭人俘虜（1610–1619）；復位後實為共治沙皇'),
('約亞薩夫一世', 'Joasaph I of Moscow', '莫斯科', '東正教（俄羅斯）', 4, 1634, 1640, '逝世', '正統', 'Russian Orthodox Church records', NULL),
('若瑟', 'Joseph of Moscow', '莫斯科', '東正教（俄羅斯）', 5, 1642, 1652, '逝世', '正統', 'Russian Orthodox Church records', NULL),
('尼孔', 'Nikon of Moscow', '莫斯科', '東正教（俄羅斯）', 6, 1652, 1666, '廢黜', '正統', 'Russian Orthodox Church records; Palmer, Patriarch and Tsar', '推行重大禮儀改革引發「舊禮派」（Raskolniki）分裂；與沙皇阿列克謝衝突出走後；1666年大公會議廢黜並流放至費拉邦托夫修道院'),
('約亞薩夫二世', 'Joasaph II of Moscow', '莫斯科', '東正教（俄羅斯）', 7, 1667, 1672, '逝世', '正統', 'Russian Orthodox Church records', NULL),
('皮提里姆', 'Pitirim of Moscow', '莫斯科', '東正教（俄羅斯）', 8, 1672, 1673, '逝世', '正統', 'Russian Orthodox Church records', '在位不足一年'),
('約阿欽', 'Joachim of Moscow', '莫斯科', '東正教（俄羅斯）', 9, 1674, 1690, '逝世', '正統', 'Russian Orthodox Church records', NULL),
('阿德里安', 'Adrian of Moscow', '莫斯科', '東正教（俄羅斯）', 10, 1690, 1700, '逝世', '正統', 'Russian Orthodox Church records', '末代宗主教（彼得大帝改革前）；1700年逝世後彼得一世不再任命繼任人；宗主教職位空缺至1917年'),
-- 1700–1917年空缺（最高宗教委員會/聖公會制時期）
('季洪', 'Tikhon (Vasily Bellavin)', '莫斯科', '東正教（俄羅斯）', 11, 1917, 1925, '逝世', '正統', 'Russian Orthodox Church records; Bourdeaux, Patriarch and Prophets', '宗主教制恢復後首任（1917年10月28日選出）；1922年被蘇聯政府以「反蘇」罪逮捕；後被迫發表聲明承認蘇維埃政府；於軟禁中逝世；1989年被封聖'),
('謝爾基', 'Sergius (Sergiy Stragorodsky)', '莫斯科', '東正教（俄羅斯）', 12, 1943, 1944, '逝世', '正統', 'Russian Orthodox Church records', '1927年「謝爾基宣言」承認蘇聯政府合法性；1943年史達林為獲教會支持抗德允許重選宗主教；在任僅一年'),
('阿列克謝一世', 'Alexy I (Sergei Simansky)', '莫斯科', '東正教（俄羅斯）', 13, 1945, 1970, '逝世', '正統', 'Russian Orthodox Church records', '在位25年；蘇聯統治下維持教會存續'),
('皮門', 'Pimen (Sergei Izvekov)', '莫斯科', '東正教（俄羅斯）', 14, 1971, 1990, '逝世', '正統', 'Russian Orthodox Church records', '蘇聯晚期宗主教；見證教會復興初期'),
('阿列克謝二世', 'Alexy II (Alexei Ridiger)', '莫斯科', '東正教（俄羅斯）', 15, 1990, 2008, '逝世', '正統', 'Russian Orthodox Church records', '蘇聯解體後主導俄羅斯正教會大規模復興；愛沙尼亞裔'),
('基里爾', 'Kirill (Vladimir Gundyaev)', '莫斯科', '東正教（俄羅斯）', 16, 2009, NULL, NULL, '正統', 'Russian Orthodox Church records', '2009年1月27日當選；2022年俄烏戰爭期間支持普丁的侵烏戰爭，引發廣泛批評；被多個教會暫停共融');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '莫斯科' AND church = '東正教（俄羅斯）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 5. 羅馬尼亞 / 東正教（羅馬尼亞）
-- 羅馬尼亞正統宗主教——1925年設立宗主教座
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('米隆·克里斯泰亞', 'Miron Cristea', '羅馬尼亞', '東正教（羅馬尼亞）', 1, 1925, 1939, '逝世', '正統', 'Romanian Orthodox Church records', '首任宗主教；1938–1939年同時擔任羅馬尼亞首相；卡羅爾二世王朝威權統治時期'),
('尼科迪姆·穆恩泰亞努', 'Nicodim Munteanu', '羅馬尼亞', '東正教（羅馬尼亞）', 2, 1939, 1948, '逝世', '正統', 'Romanian Orthodox Church records', '任內歷經第二次世界大戰及共產黨接管（1947–1948）'),
('尤斯蒂尼安·瑪律利納', 'Justinian Marina', '羅馬尼亞', '東正教（羅馬尼亞）', 3, 1948, 1977, '逝世', '正統', 'Romanian Orthodox Church records', '在位最長（29年）；共產黨統治下與政府合作以保教會存續；同時推動修道院復興'),
('尤斯廷·莫伊塞斯庫', 'Iustin Moisescu', '羅馬尼亞', '東正教（羅馬尼亞）', 4, 1977, 1986, '逝世', '正統', 'Romanian Orthodox Church records', '西奧塞斯庫時代'),
('特奧克提斯特·阿拉帕蘇', 'Teoctist Arăpaşu', '羅馬尼亞', '東正教（羅馬尼亞）', 5, 1986, 2007, '逝世', '正統', 'Romanian Orthodox Church records', '1989年革命後短暫辭職（1990年1–4月），後復位；1999年親自迎接教宗若望保祿二世訪羅；羅馬尼亞史上首次教宗訪問東正教國家'),
('達尼爾·齊亞博格', 'Daniel Ciobotea', '羅馬尼亞', '東正教（羅馬尼亞）', 6, 2007, NULL, NULL, '正統', 'Romanian Orthodox Church records', '現任；積極推動建造布加勒斯特民族救贖大教堂（2018年正式落成）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '羅馬尼亞' AND church = '東正教（羅馬尼亞）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
