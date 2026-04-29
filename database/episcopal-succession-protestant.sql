-- ============================================================
-- 信義宗大主教座傳承：烏普薩拉、圖爾庫、老天主教烏特勒支
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources) VALUES

-- ==============================
-- 烏普薩拉（瑞典信義會）
-- ==============================
-- 天主教主教時期（1164年以前為主教，未設大主教座）
('斯特凡', 'Stefan of Uppsala', '烏普薩拉', '天主教', 1, 1164, 1185, '逝世', '教宗亞歷山大三世（設大主教座）', '正統', 'Uppsala archdiocese records; first Archbishop'),
('約恩·比爾格松', 'Jon Birgerson', '烏普薩拉', '天主教', 2, 1185, 1187, '逝世', '教宗', '正統', 'Uppsala records'),
('彼得盧斯', 'Petrus of Uppsala', '烏普薩拉', '天主教', 3, 1187, 1190, '逝世', '教宗', '正統', 'Uppsala records'),
('奧洛夫·比約恩松', 'Olof Björnsson', '烏普薩拉', '天主教', 4, 1190, 1200, '逝世', '教宗', '正統', 'Uppsala records'),
('瓦萊里烏斯', 'Valerius', '烏普薩拉', '天主教', 5, 1200, 1207, '逝世', '教宗', '正統', 'Uppsala records'),
('奧洛夫', 'Olof of Uppsala', '烏普薩拉', '天主教', 6, 1207, 1224, '逝世', '教宗霍諾里烏斯三世', '正統', 'Uppsala records'),
('雅爾勒爾', 'Jarler', '烏普薩拉', '天主教', 7, 1232, 1255, '逝世', '教宗額我略九世', '正統', 'Uppsala records; first Dominican Archbishop'),
('勞倫提烏斯', 'Laurentius of Uppsala', '烏普薩拉', '天主教', 8, 1258, 1267, '逝世', '教宗', '正統', 'Uppsala records'),
('亨里克', 'Henrik of Uppsala', '烏普薩拉', '天主教', 9, 1268, 1291, '逝世', '教宗克萊孟四世', '正統', 'Uppsala records'),
('尼科拉斯·阿萊松', 'Niklas Allesson', '烏普薩拉', '天主教', 10, 1291, 1314, '逝世', '教宗', '正統', 'Uppsala records'),
('彼得盧斯·阿爾戈松', 'Petrus Algotsson', '烏普薩拉', '天主教', 11, 1310, 1351, '逝世', '教宗克萊孟五世', '正統', 'Uppsala records'),
('赫明·尼爾松', 'Hemming Nilsson', '烏普薩拉', '天主教', 12, 1342, 1366, '逝世', '教宗', '正統', 'Uppsala records'),
('比爾格爾·格列戈松', 'Birger Gregorsson', '烏普薩拉', '天主教', 13, 1366, 1383, '逝世', '教宗烏爾班五世', '正統', 'Uppsala records'),
('亨里克·哈特曼松', 'Henrik Hartmansson', '烏普薩拉', '天主教', 14, 1383, 1408, '逝世', '教宗克萊孟七世', '正統', 'Uppsala records'),
('延斯·格雷克松', 'Jens Gereksson', '烏普薩拉', '天主教', 15, 1408, 1421, '逝世', '教宗若望二十三世', '正統', 'Uppsala records'),
('約翰內斯·哈坎松', 'Johannes Håkansson', '烏普薩拉', '天主教', 16, 1421, 1432, '退休', '教宗馬丁五世', '正統', 'Uppsala records'),
('尼爾斯·拉格瓦爾松', 'Nils Ragvaldsson', '烏普薩拉', '天主教', 17, 1438, 1448, '逝世', '教宗歐仁四世', '正統', 'Uppsala records'),
('約翰內斯·貝內迪克蒂', 'Johannes Benedicti', '烏普薩拉', '天主教', 18, 1448, 1467, '退休', '教宗', '正統', 'Uppsala records'),
('雅各布·烏爾夫松', 'Jakob Ulvsson', '烏普薩拉', '天主教', 19, 1469, 1515, '退休', '教宗庇護二世', '正統', 'Uppsala records; longest-serving medieval Archbishop; 46 years'),
('古斯塔夫·特羅勒', 'Gustav Trolle', '烏普薩拉', '天主教', 20, 1515, 1521, '廢黜', '教宗利奧十世', '正統', 'Uppsala records; Stockholm Bloodbath 1520; expelled by reformers'),
('約翰內斯·馬格努斯', 'Johannes Magnus', '烏普薩拉', '天主教', 21, 1523, 1526, '流亡', '教宗克萊孟七世', '正統', 'Uppsala records; in exile; wrote Historia de omnibus gothorum sveonumque regibus'),

-- 信義宗時期
('勞倫蒂烏斯·彼特里', 'Laurentius Petri', '烏普薩拉', '瑞典信義會', 1, 1531, 1573, '逝世', '瑞典國王古斯塔夫一世', '正統', 'Uppsala records; first Lutheran Archbishop; ordained by foreign bishops; preserved episcopal succession'),
('勞倫蒂烏斯·彼特里·哥圖斯', 'Laurentius Petri Gothus', '烏普薩拉', '瑞典信義會', 2, 1575, 1579, '逝世', '瑞典國王約翰三世', '正統', 'Uppsala records'),
('安德烈亞斯·勞倫蒂', 'Andreas Laurentii Björnram', '烏普薩拉', '瑞典信義會', 3, 1580, 1590, '逝世', '瑞典國王', '正統', 'Uppsala records'),
('約翰內斯·彼特里·安格曼努斯', 'Johannes Petri Angermannus', '烏普薩拉', '瑞典信義會', 4, 1593, 1599, '廢黜', '西吉斯蒙德（被攝政王驅逐）', '正統', 'Uppsala records'),
('奧勞斯·馬蒂尼', 'Olaus Martini', '烏普薩拉', '瑞典信義會', 5, 1601, 1609, '逝世', '瑞典國王查理九世', '正統', 'Uppsala records'),
('彼德魯斯·坎尼修斯', 'Petrus Kenicius', '烏普薩拉', '瑞典信義會', 6, 1614, 1636, '逝世', '瑞典國王古斯塔夫二世阿道夫', '正統', 'Uppsala records; Thirty Years War era'),
('勞倫蒂烏斯·保利努斯·哥圖斯', 'Laurentius Paulinus Gothus', '烏普薩拉', '瑞典信義會', 7, 1637, 1646, '逝世', '克莉絲蒂娜女王', '正統', 'Uppsala records'),
('約翰內斯·勒奈烏斯', 'Johannes Lenaeus', '烏普薩拉', '瑞典信義會', 8, 1647, 1669, '逝世', '克莉絲蒂娜女王', '正統', 'Uppsala records'),
('奧洛夫·斯維比利烏斯', 'Olof Swebilius', '烏普薩拉', '瑞典信義會', 9, 1681, 1700, '逝世', '查理十一世', '正統', 'Uppsala records; high point of Lutheran orthodoxy'),
('哈昆·施佩格爾', 'Haquin Spegel', '烏普薩拉', '瑞典信義會', 10, 1711, 1714, '逝世', '查理十二世', '正統', 'Uppsala records; hymn writer'),
('馬蒂亞斯·史托奇烏斯', 'Matthias Steuchius', '烏普薩拉', '瑞典信義會', 11, 1714, 1730, '逝世', '烏爾里卡·埃萊奧諾拉女王', '正統', 'Uppsala records'),
('亨里克·本澤利烏斯', 'Henric Benzelius', '烏普薩拉', '瑞典信義會', 12, 1742, 1747, '逝世', '腓特烈一世', '正統', 'Uppsala records'),
('亨里克·貝格松·勒奈烏斯', 'Henrik Bengttson Lenaeus', '烏普薩拉', '瑞典信義會', 13, 1751, 1764, '逝世', '阿道夫·弗雷德里克', '正統', 'Uppsala records'),
('卡爾·弗雷德里克·門南德', 'Carl Fredrik Mennander', '烏普薩拉', '瑞典信義會', 14, 1775, 1786, '逝世', '古斯塔夫三世', '正統', 'Uppsala records'),
('亞伯拉罕·法爾克', 'Abraham Falck', '烏普薩拉', '瑞典信義會', 15, 1787, 1795, '逝世', '古斯塔夫三世', '正統', 'Uppsala records'),
('雅各布·林德布洛姆', 'Jacob Axelsson Lindblom', '烏普薩拉', '瑞典信義會', 16, 1805, 1819, '逝世', '古斯塔夫四世阿道夫', '正統', 'Uppsala records'),
('卡爾·馮·羅森斯坦', 'Carl von Rosenstein', '烏普薩拉', '瑞典信義會', 17, 1819, 1836, '逝世', '查理十三世', '正統', 'Uppsala records'),
('約翰·奧洛夫·瓦林', 'Johan Olof Wallin', '烏普薩拉', '瑞典信義會', 18, 1837, 1839, '逝世', '查理十四世約翰', '正統', 'Uppsala records; hymn writer; "Angel of Death" sermon'),
('卡爾·弗雷德里克·阿夫·溫加德', 'Carl Fredrik af Wingård', '烏普薩拉', '瑞典信義會', 19, 1839, 1851, '逝世', '奧斯卡一世', '正統', 'Uppsala records'),
('亨里克·羅伊特達爾', 'Henrik Reuterdahl', '烏普薩拉', '瑞典信義會', 20, 1856, 1870, '逝世', '查理十五世', '正統', 'Uppsala records; church historian'),
('安東·尼克拉斯·孫德堡', 'Anton Niklas Sundberg', '烏普薩拉', '瑞典信義會', 21, 1870, 1900, '退休', '查理十五世', '正統', 'Uppsala records'),
('約翰·奧古斯特·埃克曼', 'Johan August Ekman', '烏普薩拉', '瑞典信義會', 22, 1900, 1913, '逝世', '奧斯卡二世', '正統', 'Uppsala records'),
('納坦·索德布洛姆', 'Nathan Söderblom', '烏普薩拉', '瑞典信義會', 23, 1914, 1931, '逝世', '古斯塔夫五世', '正統', 'Uppsala records; Nobel Peace Prize 1930; ecumenism pioneer'),
('埃林·艾德姆', 'Erling Eidem', '烏普薩拉', '瑞典信義會', 24, 1931, 1950, '退休', '古斯塔夫五世', '正統', 'Uppsala records'),
('英格韋·布里利奧', 'Yngve Brilioth', '烏普薩拉', '瑞典信義會', 25, 1950, 1958, '退休', '古斯塔夫六世阿道夫', '正統', 'Uppsala records; eucharist theologian'),
('根納爾·胡爾特格倫', 'Gunnar Hultgren', '烏普薩拉', '瑞典信義會', 26, 1958, 1967, '退休', '古斯塔夫六世阿道夫', '正統', 'Uppsala records'),
('魯本·約瑟夫森', 'Ruben Josefson', '烏普薩拉', '瑞典信義會', 27, 1967, 1972, '退休', '古斯塔夫六世阿道夫', '正統', 'Uppsala records'),
('奧洛夫·孫德比', 'Olof Sundby', '烏普薩拉', '瑞典信義會', 28, 1972, 1983, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records'),
('貝蒂爾·韋克斯特倫', 'Bertil Werkström', '烏普薩拉', '瑞典信義會', 29, 1983, 1993, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records'),
('根納爾·韋曼', 'Gunnar Weman', '烏普薩拉', '瑞典信義會', 30, 1993, 1997, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records'),
('卡爾·古斯塔夫·哈馬爾', 'Karl-Gustaf (KG) Hammar', '烏普薩拉', '瑞典信義會', 31, 1997, 2006, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records; liberal theology'),
('安德斯·韋利德', 'Anders Wejryd', '烏普薩拉', '瑞典信義會', 32, 2006, 2014, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records'),
('安特耶·雅克倫', 'Antje Jackelén', '烏普薩拉', '瑞典信義會', 33, 2014, 2022, '退休', '卡爾十六世古斯塔夫', '正統', 'Uppsala records; first woman Archbishop of Uppsala'),
('馬丁·莫迪烏斯', 'Martin Modéus', '烏普薩拉', '瑞典信義會', 34, 2022, NULL, NULL, '卡爾十六世古斯塔夫', '正統', 'Uppsala records'),

-- ==============================
-- 圖爾庫（芬蘭信義會）
-- ==============================
-- 天主教主教時期
('托馬斯', 'Thomas of Finland', '圖爾庫', '天主教', 1, 1220, 1245, '廢黜', '教宗霍諾里烏斯三世', '正統', 'Turku records; first Bishop of Finland'),
('拜耶', 'Bero of Turku', '圖爾庫', '天主教', 2, 1248, 1258, '逝世', '教宗英諾森四世', '正統', 'Turku records'),
('雷金納爾都斯', 'Ragvald of Turku', '圖爾庫', '天主教', 3, 1266, 1278, '逝世', '教宗克萊孟四世', '正統', 'Turku records'),
('喬萬尼', 'Johannes of Turku', '圖爾庫', '天主教', 4, 1286, 1300, '逝世', '教宗霍諾里烏斯四世', '正統', 'Turku records'),
('馬格努斯一世', 'Magnus I of Turku', '圖爾庫', '天主教', 5, 1291, 1308, '逝世', '教宗尼古拉四世', '正統', 'Turku records'),
('波爾達', 'Porvoo/Birger of Turku', '圖爾庫', '天主教', 7, 1313, 1338, '逝世', '教宗克萊孟五世', '正統', 'Turku records'),
('赫明·亨里克松', 'Hemming Henrikkinen', '圖爾庫', '天主教', 8, 1338, 1366, '逝世', '教宗本篤十二世', '正統', 'Turku records; beatified 1514'),
('霍爾姆格爾', 'Hemming Niklisson', '圖爾庫', '天主教', 10, 1369, 1366, '逝世', '教宗烏爾班五世', '正統', 'Turku records'),
('托馬斯·詹克斯', 'Thomas Jacobi', '圖爾庫', '天主教', 12, 1413, 1422, '逝世', '教宗若望二十三世', '正統', 'Turku records'),
('馬格努斯二世·斯皮特', 'Maunu Speet', '圖爾庫', '天主教', 14, 1460, 1474, '退休', '教宗庇護二世', '正統', 'Turku records'),
('孔拉德·比特', 'Conrad Bitz', '圖爾庫', '天主教', 15, 1460, 1489, '逝世', '教宗', '正統', 'Turku records'),
('馬格努斯三世·斯特拉倫', 'Maunu III Särkilahti', '圖爾庫', '天主教', 16, 1489, 1500, '逝世', '教宗英諾森八世', '正統', 'Turku records'),
('雅各布·烏爾費爾特', 'Jakob Ulfsson（兼任）', '圖爾庫', '天主教', 17, 1500, 1510, '辭職', '教宗亞歷山大六世', '正統', 'Turku records; also Archbishop of Uppsala'),
('阿爾維德·庫爾克', 'Arvid Kurck', '圖爾庫', '天主教', 18, 1510, 1522, '逝世', '教宗尤利烏斯二世', '正統', 'Turku records; last Catholic Bishop of Turku active'),
('馬丁·斯克特', 'Martti Skytte', '圖爾庫', '天主教', 19, 1528, 1550, '逝世（路德派）', '瑞典國王古斯塔夫一世', '正統', 'Turku records; transition bishop; accepted Reformation'),

-- 信義宗時期
('米卡埃爾·阿格里科拉', 'Mikael Agricola', '圖爾庫', '芬蘭信義會', 1, 1554, 1557, '逝世', '瑞典國王古斯塔夫一世', '正統', 'Turku records; "Father of Finnish literacy"; Finnish Bible translation'),
('保盧斯·尤斯坦', 'Paavali Juusten', '圖爾庫', '芬蘭信義會', 2, 1563, 1576, '逝世', '瑞典國王', '正統', 'Turku records'),
('埃里克·索羅萊寧', 'Eerikki Sorolainen', '圖爾庫', '芬蘭信義會', 3, 1583, 1625, '逝世', '瑞典國王', '正統', 'Turku records; Finnish post-Reformation church'),
('以撒·洛托維烏斯', 'Isak Rothovius', '圖爾庫', '芬蘭信義會', 4, 1627, 1652, '逝世', '古斯塔夫二世阿道夫', '正統', 'Turku records; founded Turku Academy 1640'),
('亨里克·霍夫曼', 'Henrik Hoffman', '圖爾庫', '芬蘭信義會', 5, 1654, 1675, '逝世', '克莉絲蒂娜', '正統', 'Turku records'),
('約翰·格澤里烏斯一世', 'Johannes Gezelius the Elder', '圖爾庫', '芬蘭信義會', 6, 1664, 1690, '逝世', '查理十世', '正統', 'Turku records; promoted literacy; Finnish Bible'),
('約翰·格澤里烏斯二世', 'Johannes Gezelius the Younger', '圖爾庫', '芬蘭信義會', 7, 1690, 1718, '逝世', '查理十一世', '正統', 'Turku records'),
('大衛·卡斯特倫', 'David Lund', '圖爾庫', '芬蘭信義會', 8, 1721, 1737, '逝世', '查理十二世', '正統', 'Turku records'),
('亨里克·奧斯特羅', 'Herman Hassel', '圖爾庫', '芬蘭信義會', 9, 1739, 1751, '逝世', '弗雷德里克一世', '正統', 'Turku records'),
('卡爾·費雷德里克·門南德', 'Carl Fredrik Mennander', '圖爾庫', '芬蘭信義會', 10, 1757, 1775, '轉任烏普薩拉', '弗雷德里克一世', '正統', 'Turku records; later Uppsala Archbishop'),
('保盧斯·加德', 'Magnus Jacob Alopaeus', '圖爾庫', '芬蘭信義會', 11, 1775, 1802, '逝世', '古斯塔夫三世', '正統', 'Turku records'),
('雅各布·騰格斯特倫', 'Jakob Tengström', '圖爾庫', '芬蘭信義會', 12, 1803, 1832, '逝世', '俄羅斯沙皇亞歷山大一世', '正統', 'Turku records; first Archbishop (1817) after elevation; Finnish autonomy'),
('愛德華·福爾斯坦', 'Edward Forsman (Böök)', '圖爾庫', '芬蘭信義會', 13, 1832, 1845, '逝世', '沙皇尼古拉一世', '正統', 'Turku records'),
('伯恩哈德·奥托·利利', 'Bernt Otto Lille', '圖爾庫', '芬蘭信義會', 14, 1845, 1857, '逝世', '沙皇尼古拉一世', '正統', 'Turku records'),
('伊曼努爾·帕爾門', 'Emanuel Paimen', '圖爾庫', '芬蘭信義會', 15, 1858, 1878, '退休', '沙皇亞歷山大二世', '正統', 'Turku records'),
('托爾斯滕·托馬斯·罗倫', 'Torsten Thorsten Renvall', '圖爾庫', '芬蘭信義會', 16, 1878, 1893, '逝世', '沙皇亞歷山大三世', '正統', 'Turku records'),
('亞爾馬·恰斯達爾', 'Johansson Gustaf', '圖爾庫', '芬蘭信義會', 17, 1899, 1930, '逝世', '沙皇尼古拉二世', '正統', 'Turku records; Finnish independence 1917'),
('埃爾科·里薩寧', 'Erkki Kaila', '圖爾庫', '芬蘭信義會', 18, 1935, 1944, '逝世', '芬蘭共和國', '正統', 'Turku records; WWII Winter War era'),
('阿萊克西斯·雷科', 'Aleksi Lehtonen', '圖爾庫', '芬蘭信義會', 19, 1945, 1951, '逝世', '芬蘭共和國', '正統', 'Turku records'),
('伊爾馬里·索拉', 'Ilmari Salomies', '圖爾庫', '芬蘭信義會', 20, 1951, 1964, '退休', '芬蘭共和國', '正統', 'Turku records'),
('馬蒂·西馬拉', 'Martti Simojoki', '圖爾庫', '芬蘭信義會', 21, 1964, 1978, '退休', '芬蘭共和國', '正統', 'Turku records'),
('約翰·維克斯滕', 'John Vikström', '圖爾庫', '芬蘭信義會', 22, 1982, 1998, '退休', '芬蘭共和國', '正統', 'Turku records; Porvoo Communion'),
('尤卡·帕爾馬', 'Jukka Paarma', '圖爾庫', '芬蘭信義會', 23, 1998, 2010, '退休', '芬蘭共和國', '正統', 'Turku records'),
('卡里·曼斯凱拉', 'Kari Mäkinen', '圖爾庫', '芬蘭信義會', 24, 2010, 2018, '退休', '芬蘭共和國', '正統', 'Turku records'),
('塔皮奧·盧奧馬', 'Tapio Luoma', '圖爾庫', '芬蘭信義會', 25, 2018, NULL, NULL, '芬蘭共和國', '正統', 'Turku records'),

-- ==============================
-- 烏特勒支（老天主教）
-- ==============================
('威利布羅德', 'Willibrord', '烏特勒支', '天主教', 1, 695, 739, '逝世', '教宗塞爾吉烏斯一世', '正統', 'Utrecht records; Apostle to the Frisians; founded see'),
('彼得', 'Boniface of Dokkum（代理）', '烏特勒支', '天主教', 2, 739, 754, '殉道', '坎特伯里', '正統', 'Utrecht records; martyred by Frisians 754'),
('格列高里', 'Gregory of Utrecht', '烏特勒支', '天主教', 3, 754, 775, '逝世', '教宗斯蒂芬二世', '正統', 'Utrecht records'),
('阿爾布里希特', 'Alberic of Utrecht', '烏特勒支', '天主教', 4, 775, 784, '逝世', '教宗', '正統', 'Utrecht records'),
('希爾德博爾德', 'Hildebold of Utrecht', '烏特勒支', '天主教', 5, 790, 818, '逝世', '查理曼大帝', '正統', 'Utrecht records; also Archbishop of Cologne after 787'),
('弗雷德里克一世', 'Frederick I of Utrecht', '烏特勒支', '天主教', 6, 820, 838, '殉道', '路易一世虔誠者', '正統', 'Utrecht records; murdered 838'),
('利烏佩特', 'Liutbert of Utrecht', '烏特勒支', '天主教', 7, 854, 870, '逝世', '路易二世德意志人', '正統', 'Utrecht records'),
('阿德里安', 'Odilbald', '烏特勒支', '天主教', 8, 870, 899, '逝世', '教宗阿德里安二世', '正統', 'Utrecht records'),
('波波', 'Baldo of Utrecht', '烏特勒支', '天主教', 9, 899, 918, '逝世', '神聖羅馬帝國', '正統', 'Utrecht records'),
('奧托', 'Hungier', '烏特勒支', '天主教', 10, 900, 900, '逝世', '神聖羅馬帝國', '正統', 'Utrecht records'),
('烏多', 'Balderic of Utrecht', '烏特勒支', '天主教', 12, 918, 976, '逝世', '奧托一世', '正統', 'Utrecht records'),
('福爾科爾德', 'Folcmar', '烏特勒支', '天主教', 15, 976, 990, '逝世', '奧托二世', '正統', 'Utrecht records'),
('安斯弗里德', 'Ansfried of Utrecht', '烏特勒支', '天主教', 16, 995, 1010, '逝世', '奧托三世', '正統', 'Utrecht records; beatified'),
('阿達爾博爾德', 'Adalbold of Utrecht', '烏特勒支', '天主教', 17, 1010, 1026, '逝世', '亨利二世', '正統', 'Utrecht records; wrote Life of Henry II'),
('伯恩烏爾夫', 'Bernold of Utrecht', '烏特勒支', '天主教', 18, 1027, 1054, '逝世', '康拉德二世', '正統', 'Utrecht records'),
('威廉', 'William of Utrecht', '烏特勒支', '天主教', 19, 1054, 1076, '逝世', '亨利三世', '正統', 'Utrecht records; Investiture Controversy'),
('洛巴爾杜斯', 'Conrad of Utrecht', '烏特勒支', '天主教', 22, 1076, 1099, '逝世', '亨利四世', '正統', 'Utrecht records; imperial bishop'),
('哥特弗里德', 'Godfrey of Rhenen', '烏特勒支', '天主教', 23, 1100, 1127, '逝世', '亨利五世', '正統', 'Utrecht records'),
('安德烈亞斯', 'Andreas of Utrecht', '烏特勒支', '天主教', 24, 1128, 1139, '逝世', '洛泰爾三世', '正統', 'Utrecht records'),
('哈特貝爾特', 'Hartbert', '烏特勒支', '天主教', 25, 1139, 1150, '逝世', '康拉德三世', '正統', 'Utrecht records'),
('赫爾曼二世', 'Herman II of Utrecht', '烏特勒支', '天主教', 26, 1150, 1156, '逝世', '腓特烈一世巴巴羅薩', '正統', 'Utrecht records'),
('安德烈·範庫伊克', 'Godfried van Rhenen', '烏特勒支', '天主教', 27, 1156, 1178, '逝世', '腓特烈巴巴羅薩', '正統', 'Utrecht records'),
('巴爾杜安', 'Baldwin of Utrecht', '烏特勒支', '天主教', 28, 1178, 1196, '逝世', '腓特烈巴巴羅薩', '正統', 'Utrecht records'),
('迪爾里克二世', 'Dirk II of Are', '烏特勒支', '天主教', 29, 1196, 1212, '逝世', '奧托四世', '正統', 'Utrecht records'),
('奧托一世·範格爾德', 'Otto I of Utrecht', '烏特勒支', '天主教', 30, 1215, 1227, '逝世', '腓特烈二世', '正統', 'Utrecht records'),
('威廉隆', 'Wilbrand of Oldenburg', '烏特勒支', '天主教', 31, 1227, 1233, '逝世', '腓特烈二世', '正統', 'Utrecht records'),
('奧托二世', 'Otto II of Utrecht', '烏特勒支', '天主教', 32, 1234, 1249, '逝世', '腓特烈二世', '正統', 'Utrecht records'),
('亨里克·範維安登', 'Henry of Vianden', '烏特勒支', '天主教', 33, 1249, 1267, '逝世', '康拉德四世', '正統', 'Utrecht records'),
('約翰一世·範拿薩', 'John I of Nassau', '烏特勒支', '天主教', 34, 1267, 1290, '逝世', '魯道夫一世哈布斯堡', '正統', 'Utrecht records'),
('約翰二世·範滕格梅倫', 'John II of Utrecht', '烏特勒支', '天主教', 35, 1292, 1296, '逝世', '阿道夫', '正統', 'Utrecht records'),
('威廉·博爾特勒斯勞特', 'Guillaume Bertrand', '烏特勒支', '天主教', 36, 1296, 1301, '逝世', '阿爾伯特一世', '正統', 'Utrecht records'),
('古伊多·達維尼翁', 'Guido of Avesnes', '烏特勒支', '天主教', 37, 1301, 1317, '逝世', '阿爾伯特一世', '正統', 'Utrecht records'),
('弗雷德里克三世·範西爾克', 'Frederick III', '烏特勒支', '天主教', 38, 1317, 1322, '逝世', '路易四世巴伐利亞', '正統', 'Utrecht records'),
('弗雷德里克四世', 'Frederick IV', '烏特勒支', '天主教', 39, 1323, 1340, '逝世', '路易四世巴伐利亞', '正統', 'Utrecht records'),
('揚·達克', 'Jan van Arkel', '烏特勒支', '天主教', 40, 1342, 1364, '逝世', '查理四世', '正統', 'Utrecht records'),
('阿諾德·凡·霍恩', 'Arnold van Hoorne', '烏特勒支', '天主教', 41, 1371, 1378, '逝世', '查理四世', '正統', 'Utrecht records'),
('弗洛倫蒂烏斯', 'Florentius Radewijns', '烏特勒支', '天主教', 42, 1379, 1393, '逝世', '溫切斯勞斯', '正統', 'Utrecht records; Devotio Moderna movement'),
('弗雷德里克·範布蘭肯海姆', 'Frederick of Blankenheim', '烏特勒支', '天主教', 43, 1393, 1423, '逝世', '魯佩爾特', '正統', 'Utrecht records; Western Schism era'),
('茨維德爾特·範屈伊倫堡', 'Zweder van Culemborg', '烏特勒支', '天主教', 44, 1423, 1433, '廢黜', '教宗馬丁五世', '爭議', 'Utrecht records; basis of later Utrecht schism — Rome deposed him, Utrecht chapter resisted'),
('魯道夫·凡·迪芬霍爾特', 'Rudolf of Diepholt', '烏特勒支', '天主教', 45, 1433, 1455, '逝世', '教宗歐仁四世', '正統', 'Utrecht records'),
('吉斯博特·範布雷德羅德', 'Gijsbrecht van Brederode', '烏特勒支', '天主教', 46, 1455, 1456, '逝世', '教宗尼古拉五世', '正統', 'Utrecht records'),
('戴維·凡·勃良第', 'David of Burgundy', '烏特勒支', '天主教', 47, 1456, 1496, '逝世', '教宗卡利克斯圖斯三世', '正統', 'Utrecht records; Burgundian era'),
('弗雷德里克·凡·巴登', 'Frederick of Baden', '烏特勒支', '天主教', 48, 1496, 1517, '逝世', '教宗亞歷山大六世', '正統', 'Utrecht records'),
('菲利普·凡·勃良第', 'Philip of Burgundy', '烏特勒支', '天主教', 49, 1517, 1524, '逝世', '教宗利奧十世', '正統', 'Utrecht records; patron of Erasmus'),
('亨德里克·凡·巴伐利亞', 'Henry of Bavaria', '烏特勒支', '天主教', 50, 1524, 1528, '逝世', '教宗克萊孟七世', '正統', 'Utrecht records'),
('亨德里克·凡·維克', 'Hendrik of Wijk', '烏特勒支', '天主教', 51, 1529, 1561, '退休', '卡爾五世（查理五世）', '正統', 'Utrecht records; Reformation era'),
('弗雷德里克·斯侯滕', 'Frederick Schenk van Toutenburg', '烏特勒支', '天主教', 52, 1561, 1580, '逝世', '教宗庇護四世', '正統', 'Utrecht records'),
('薩比努斯·沃比烏斯', 'Sasbout Vosmeer', '烏特勒支', '天主教', 53, 1592, 1614, '逝世', '教宗克萊孟八世', '正統', 'Utrecht records; Apostolic Vicar during Dutch Republic'),
('菲利普斯·隆貝爾茨', 'Philippus Rovenius', '烏特勒支', '天主教', 54, 1614, 1651, '逝世', '教宗保羅五世', '正統', 'Utrecht records; Apostolic Vicar'),
('雅各布斯·凡·巴爾肯施泰因', 'Joannes van Neercassel', '烏特勒支', '天主教', 55, 1662, 1686, '逝世', '教宗亞歷山大七世', '正統', 'Utrecht records; Jansenist sympathies; Apostolic Vicar'),
('彼得·科多米烏斯', 'Petrus Codde', '烏特勒支', '天主教', 56, 1688, 1704, '廢黜（揚森主義爭議）', '教宗克萊孟十一世', '爭議', 'Utrecht records; Apostolic Vicar; Rome suspended him for Jansenism'),

-- 老天主教時期（烏特勒支聯合，1724年起）
('亨德里克·巴赫曼·沃伊蒂爾斯', 'Hendrick Barchman Wuytiers', '烏特勒支', '老天主教', 1, 1724, 1733, '逝世', '烏特勒支教省會議自選', '正統', 'Utrecht records; first Archbishop of Old Catholic Utrecht Union; consecrated by Dominique Marie Varlet'),
('科尼利斯·斯圖凡', 'Cornelis Steenoven', '烏特勒支', '老天主教', 2, 1723, 1725, '逝世', '烏特勒支教省', '正統', 'Utrecht records; first modern Old Catholic Archbishop'),
('科尼利斯·揚·巴伊', 'Cornelis Joan Barchman Wuytiers', '烏特勒支', '老天主教', 3, 1733, 1733, '逝世（任內）', '烏特勒支教省', '正統', 'Utrecht records'),
('西奧多·克魯克拉特', 'Theodorus van der Croon', '烏特勒支', '老天主教', 4, 1734, 1739, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('彼得·約翰內斯·梅因德茨', 'Petrus Johannes Meindaerts', '烏特勒支', '老天主教', 5, 1739, 1767, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('約翰內斯·甘布弗爾特', 'Johannes van Rhijn', '烏特勒支', '老天主教', 6, 1768, 1793, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('瓦爾特魯斯·德·博克', 'Walterus de Bock', '烏特勒支', '老天主教', 7, 1797, 1797, '逝世（任內）', '烏特勒支教省', '正統', 'Utrecht records'),
('雅各布斯·德·許爾特', 'Jacobus de Burtin', '烏特勒支', '老天主教', 8, 1797, 1825, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('維廉姆斯·凡·奇姆珀爾', 'Wilhelmus van Sonsbeeck', '烏特勒支', '老天主教', 9, 1825, 1841, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('約翰內斯·洛爾特茲', 'Johannes Bon', '烏特勒支', '老天主教', 10, 1842, 1868, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('赫爾曼·海坎普', 'Hermann Heykamp', '烏特勒支', '老天主教', 11, 1869, 1892, '逝世', '烏特勒支教省', '正統', 'Utrecht records; First Vatican Council protest; expanded Union'),
('格拉提亞努斯·揚森', 'Gerardus Gul', '烏特勒支', '老天主教', 12, 1892, 1920, '逝世', '烏特勒支教省', '正統', 'Utrecht records'),
('約翰內斯·奧爾拉普', 'François Kenninck', '烏特勒支', '老天主教', 13, 1920, 1945, '逝世', '烏特勒支教省', '正統', 'Utrecht records; WWII'),
('安德烈亞斯·林赫茨', 'Andreas Rinkel', '烏特勒支', '老天主教', 14, 1945, 1970, '退休', '烏特勒支教省', '正統', 'Utrecht records'),
('馬里努斯·科克', 'Marinus Kok', '烏特勒支', '老天主教', 15, 1970, 1982, '退休', '烏特勒支教省', '正統', 'Utrecht records'),
('安東尼烏斯·揚·斯加勒拉', 'Antonius Jan Glazemaker', '烏特勒支', '老天主教', 16, 1982, 2000, '退休', '烏特勒支教省', '正統', 'Utrecht records'),
('約里斯·維廉姆·沙頓', 'Joris Vercammen', '烏特勒支', '老天主教', 17, 2000, 2020, '退休', '烏特勒支教省', '正統', 'Utrecht records'),
('貝恩德·沃利特', 'Bernd Wallet', '烏特勒支', '老天主教', 18, 2020, NULL, NULL, '烏特勒支教省', '正統', 'Utrecht records');

-- 設定 predecessor_id（各 see 內連鏈）
UPDATE episcopal_succession es
SET predecessor_id = prev.id
FROM (
  SELECT id,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see IN ('烏普薩拉', '圖爾庫', '烏特勒支')
) prev
WHERE es.id = prev.id AND prev.prev_id IS NOT NULL;

-- 修正跨 church 邊界（Uppsala: Trolle 天主教 → Petri 信義宗）
UPDATE episcopal_succession
SET predecessor_id = (SELECT id FROM episcopal_succession WHERE see='烏普薩拉' AND church='天主教' AND succession_number=21)
WHERE see='烏普薩拉' AND church='瑞典信義會' AND succession_number=1;

-- 修正 Turku 跨 church 邊界（Skytte 天主教 → Agricola 信義宗）
UPDATE episcopal_succession
SET predecessor_id = (SELECT id FROM episcopal_succession WHERE see='圖爾庫' AND church='天主教' AND succession_number=19)
WHERE see='圖爾庫' AND church='芬蘭信義會' AND succession_number=1;

-- Utrecht 老天主教 rival_of (Codde 廢黜為 Barchman Wuytiers 的起點)
UPDATE episcopal_succession
SET predecessor_id = (SELECT id FROM episcopal_succession WHERE see='烏特勒支' AND church='天主教' AND succession_number=56)
WHERE see='烏特勒支' AND church='老天主教' AND succession_number=1;
