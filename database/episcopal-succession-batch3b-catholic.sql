-- ============================================================
-- 主教傳承批次3B：天主教總主教區（歐洲、拉美、亞洲、非洲、大洋洲）
-- Batch 3B: Catholic Archdioceses — Europe, Latin America, Asia, Africa, Oceania
-- Sees: 桑斯、弗賴堡、帕德博恩、卡洛察、埃格爾、格拉茨、埃武拉、巴塞羅那、布爾戈斯、
--        里加、布拉提斯拉瓦、科希策、莫斯科、加拉加斯、蒙特維的亞、瓜亞基爾、基多、
--        聖安東尼奧、邁阿密、胡志明市、北京、上海、雅加達、科倫坡、阿爾及爾、
--        阿比尚、達喀爾、盧沙卡、威靈頓、蘇瓦、德班
-- Generated: 2026-04-30
-- ============================================================

-- 1. 桑斯（天主教，法國）— 古老主教座，c.290–1801年廢除
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('薩維尼烏斯', 'Savinianus', '桑斯', '天主教', 1, 290, 310, '殉道', '正統', 'Catholic Encyclopedia: Sens; New Advent', '傳統上桑斯首任主教；約290–310年；早期殉道者傳統'),
('波滕提亞努斯', 'Potentianus', '桑斯', '天主教', 2, 310, 340, '逝世', '正統', 'Catholic Encyclopedia: Sens', '早期主教；桑斯教會鞏固時期'),
('安塞吉蘇斯', 'Ansegisus', '桑斯', '天主教', 15, 871, 883, '逝世', '正統', 'Catholic Encyclopedia: Sens; New Advent', '大主教；教宗若望八世授予「高盧及日耳曼首席大主教和教廷代表」頭銜；為查理二世（禿頭）出使羅馬'),
('于格·德·圖西', 'Hugues de Toucy', '桑斯', '天主教', 25, 1142, 1168, '逝世', '正統', 'Catholic Encyclopedia: Sens', '1152年在奧爾良為路易七世之妻康斯坦丁加冕；與蘭斯大主教就首席地位有爭議'),
('特里斯坦·德·薩盧斯', 'Tristan de Salazar', '桑斯', '天主教', 50, 1474, 1519, '逝世', '正統', 'Catholic Encyclopedia: Sens', '長期在任大主教；文藝復興人文主義影響；1594年教省縮減'),
('路易·波旁', 'Louis de Bourbon-Vendôme', '桑斯', '天主教', 55, 1557, 1569, '逝世', '正統', 'Catholic Encyclopedia: Sens', '宗教戰爭（胡格諾戰爭，1562–）期間大主教；桑斯天主教中心'),
('夏爾·德·諾阿耶', 'Charles de Noailles', '桑斯', '天主教', 65, 1679, 1707, '逝世', '正統', 'Catholic Encyclopedia: Sens', '路易十四時代；高盧主義（Gallicanism）爭議'),
('保羅·達爾貝爾·德·呂尼', 'Paul d''Albert de Luynes', '桑斯', '天主教', 70, 1753, 1788, '逝世', '正統', 'Catholic Encyclopedia: Sens', '舊制度末期大主教；法國大革命前夕'),
('讓-巴蒂斯特·德·西瑟', 'Jean-Baptiste de Cicé', '桑斯', '天主教', 71, 1788, 1801, '廢黜', '正統', 'Catholic Encyclopedia: Sens; Concordat 1801', '桑斯最後一任大主教；1801年拿破崙政教協議廢除桑斯教區，合併入特魯瓦及奧塞爾；今為名義主教座（Titular See）')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '桑斯' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 2. 弗賴堡（天主教，德國）— 1827年至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('貝恩哈德·博爾', 'Bernhard Boll', '弗賴堡', '天主教', 1, 1827, 1836, '逝世', '正統', 'List of archbishops of Freiburg Wikipedia; Catholic-Hierarchy', '1821年弗賴堡教區從康士坦茨等教區組建；博爾1827年按立首任主教'),
('伊格納茨·德梅特爾', 'Ignaz Demeter', '弗賴堡', '天主教', 2, 1836, 1842, '逝世', '正統', 'Catholic-Hierarchy', '1836年11月21日確認'),
('赫爾曼·馮·維卡里', 'Hermann von Vicari', '弗賴堡', '天主教', 3, 1843, 1868, '逝世', '正統', 'Catholic-Hierarchy', '長任；文化鬥爭前奏的德意志教會政治衝突'),
('托馬斯·諾貝爾', 'Thomas Nörber', '弗賴堡', '天主教', 5, 1898, 1920, '逝世', '正統', 'Catholic-Hierarchy', '第一次世界大戰大主教'),
('卡爾·弗里茨', 'Karl Fritz', '弗賴堡', '天主教', 6, 1920, 1931, '逝世', '正統', 'Catholic-Hierarchy', '威瑪共和國時期'),
('康拉德·格羅貝爾', 'Conrad Gröber', '弗賴堡', '天主教', 7, 1932, 1948, '逝世', '正統', 'Catholic-Hierarchy', '納粹時代大主教；立場複雜，初部分支持政權後批評'),
('溫德林·拉烏赫', 'Wendelin Rauch', '弗賴堡', '天主教', 8, 1948, 1954, '逝世', '正統', 'Catholic-Hierarchy', '戰後重建'),
('赫爾曼·約瑟夫·舍費勒', 'Hermann Josef Schäufele', '弗賴堡', '天主教', 9, 1958, 1977, '逝世', '正統', 'Catholic-Hierarchy', '梵二大公會議（1962–1965）期間'),
('奧斯卡·賽特里希', 'Oskar Saier', '弗賴堡', '天主教', 10, 1978, 2002, '辭職', '正統', 'Catholic-Hierarchy', '長任大主教'),
('羅伯特·佐利茨', 'Robert Zollitsch', '弗賴堡', '天主教', 11, 2003, 2013, '退休', '正統', 'Catholic-Hierarchy', '德國主教團主席（2008–2014）'),
('斯蒂芬·布爾格爾', 'Stephan Burger', '弗賴堡', '天主教', 12, 2014, NULL, NULL, '正統', 'Catholic-Hierarchy', '2014年6月29日按立；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '弗賴堡' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 3. 帕德博恩（天主教，德國）— 799年至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('哈特里希', 'Hathurich', '帕德博恩', '天主教', 1, 799, 815, '逝世', '正統', 'Roman Catholic Archdiocese of Paderborn Wikipedia; Catholic Encyclopedia', '799年教宗良三世冊立帕德博恩教區；查理曼大帝799年在此接待教宗；哈特里希首任主教'),
('百格諾', 'Badurad', '帕德博恩', '天主教', 3, 815, 862, '逝世', '正統', 'Catholic Encyclopedia: Paderborn', '卡洛林王朝下教區鞏固'),
('本諾一世', 'Benno I', '帕德博恩', '天主教', 8, 1036, 1068, '逝世', '正統', 'Catholic Encyclopedia: Paderborn', '薩利安王朝；帝國教會；主教敘任權鬥爭前夕'),
('迪特里希四世·馮·富斯滕貝格', 'Dietrich IV von Fürstenberg', '帕德博恩', '天主教', 28, 1585, 1618, '逝世', '正統', 'Catholic Encyclopedia: Paderborn', '反宗教改革；耶穌會教育；帕德博恩大學（1614年）創立'),
('卡斯帕·克萊因', 'Kaspar Klein', '帕德博恩', '天主教', 50, 1920, 1941, '逝世', '正統', 'Roman Catholic Archdiocese of Paderborn Wikipedia', '1930年帕德博恩升格為總主教區；首任大主教'),
('洛倫茨·耶格爾', 'Lorenz Jaeger', '帕德博恩', '天主教', 51, 1941, 1973, '退休', '正統', 'Roman Catholic Archdiocese of Paderborn Wikipedia', '梵二大公會議重要人物；推動普世合一'),
('約翰內斯·德根哈特', 'Johannes Joachim Degenhardt', '帕德博恩', '天主教', 52, 1974, 2002, '逝世', '正統', 'Roman Catholic Archdiocese of Paderborn Wikipedia', '在任近三十年；德國統一（1990年）後整合'),
('漢斯-約瑟夫·貝克爾', 'Hans-Josef Becker', '帕德博恩', '天主教', 53, 2003, 2022, '退休', '正統', 'Roman Catholic Archdiocese of Paderborn Wikipedia', '2003–2022年'),
('烏韋·賴因施', 'Uwe Renz', '帕德博恩', '天主教', 54, 2023, NULL, NULL, '正統', 'Catholic-Hierarchy', '2023年按立；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '帕德博恩' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 4. 卡洛察（天主教，匈牙利）— c.1000年至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿斯特里克', 'Astrik (Anastasius)', '卡洛察', '天主教', 1, 1000, 1030, '逝世', '正統', 'Catholic Encyclopedia: Kalocsa-Bacs; Roman Catholic Archdiocese of Kalocsa Wikipedia', '匈牙利王國建立（1000年）；聖伊什特萬（斯蒂芬）一世設立卡洛察大主教區；阿斯特里克首任大主教'),
('德西德里烏斯', 'Desiderius', '卡洛察', '天主教', 3, 1064, 1090, '逝世', '正統', 'Catholic Encyclopedia: Kalocsa-Bacs', '早期匈牙利教會鞏固'),
('于格林一世', 'Ugrin I', '卡洛察', '天主教', 12, 1219, 1241, '殉道', '正統', 'Catholic Encyclopedia: Kalocsa-Bacs', '1241年蒙古入侵匈牙利（莫希戰役）；于格林一世在戰役中陣亡'),
('路德維希·海納爾德', 'Lajos Haynald', '卡洛察', '天主教', 30, 1867, 1891, '逝世', '正統', 'Roman Catholic Archdiocese of Kalocsa Wikipedia', '梵一大公會議反教宗無誤論派領袖；1879年樞機；著名植物學家'),
('亞諾什·切爾諾赫', 'János Csernoch', '卡洛察', '天主教', 32, 1911, 1912, '調任', '正統', 'Catholic-Hierarchy', '後調任埃斯泰爾戈姆大主教（1912年）'),
('約瑟夫·格羅斯', 'József Grósz', '卡洛察', '天主教', 35, 1943, 1961, '逝世', '正統', 'Roman Catholic Archdiocese of Kalocsa Wikipedia', '二戰及共產政府（1948年）；1951年被捕審判'),
('約瑟夫·伊亞什', 'József Ijjas', '卡洛察', '天主教', 36, 1969, 1987, '逝世', '正統', 'Roman Catholic Archdiocese of Kalocsa Wikipedia', '匈牙利共產主義晚期'),
('拉斯洛·丹科', 'László Dankó', '卡洛察', '天主教', 37, 1987, 1999, '逝世', '正統', 'Catholic-Hierarchy', '1989年匈牙利政治轉型'),
('巴拉日·巴貝爾', 'Balázs Bábel', '卡洛察', '天主教', 38, 1999, NULL, NULL, '正統', 'Catholic-Hierarchy', '1999年6月25日任命；現任大主教；卡洛察-克奇凱梅特')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '卡洛察' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 5. 埃格爾（天主教，匈牙利）— 1804年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('費倫茨·富克斯', 'Ferenc Fuchs', '埃格爾', '天主教', 1, 1804, 1807, '逝世', '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Eger Wikipedia', '1804年8月9日埃格爾升格為總主教區；富克斯首任大主教'),
('伊什特萬·費舍爾', 'István Fischer de Nagy', '埃格爾', '天主教', 2, 1807, 1822, '逝世', '正統', 'Catholic-Hierarchy', '拿破崙戰爭時期'),
('拉迪斯拉夫·皮爾克爾', 'Ján Krstitel Ladislav Pyrker', '埃格爾', '天主教', 3, 1827, 1847, '逝世', '正統', 'Catholic-Hierarchy', '詩人大主教；斯洛伐克裔'),
('亞諾什·薩馬沙', 'József Samassa', '埃格爾', '天主教', 5, 1873, 1912, '逝世', '正統', 'Catholic-Hierarchy', '在任近40年；奧匈帝國時期'),
('拉約什·斯姆雷恰尼', 'Lajos Szmrecsányi', '埃格爾', '天主教', 6, 1912, 1943, '逝世', '正統', 'Catholic-Hierarchy', '兩次世界大戰；特里亞農條約（1920年）'),
('朱利奧·恰皮克', 'Gyula Czapik', '埃格爾', '天主教', 7, 1943, 1956, '逝世', '正統', 'Catholic-Hierarchy', '二戰及共產政府奪權（1948年）'),
('帕沃爾·布雷扎諾茨基', 'Pavol Brezanóczy', '埃格爾', '天主教', 8, 1969, 1972, '逝世', '正統', 'Catholic-Hierarchy', '共產統治下梵二後過渡'),
('塞列格里·伊什特萬', 'István Seregély', '埃格爾', '天主教', 9, 1987, 2010, '退休', '正統', 'Catholic-Hierarchy', '1989年匈牙利政治轉型；在任23年'),
('泰爾尼亞克·切斯托米爾', 'Csaba Ternyák', '埃格爾', '天主教', 10, 2010, NULL, NULL, '正統', 'Catholic-Hierarchy', '2010年任命；前梵蒂岡官員；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '埃格爾' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 6. 格拉茨（天主教，奧地利）— 1786年至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('約瑟夫·亞當·馮·阿爾科', 'Joseph Adam Graf Arco', '格拉茨', '天主教', 1, 1780, 1802, '逝世', '正統', 'Roman Catholic Diocese of Graz-Seckau Wikipedia; Catholic-Hierarchy', '1786年主教座由塞考遷格拉茨；約瑟夫主義（啟蒙改革）下的奧地利天主教'),
('約瑟夫·奧托馬爾·馮·勞舍爾', 'Joseph Othmar von Rauscher', '格拉茨', '天主教', 3, 1849, 1853, '調任', '正統', 'Catholic-Hierarchy', '後調維也納樞機大主教'),
('約翰·巴普蒂斯特·茨維格爾', 'Johann Baptist Zwerger', '格拉茨', '天主教', 5, 1867, 1893, '逝世', '正統', 'Catholic-Hierarchy', '梵一大公會議（1869–1870）；文化鬥爭時期'),
('利奧波德·舒斯特', 'Leopold Schuster', '格拉茨', '天主教', 6, 1893, 1927, '逝世', '正統', 'Catholic-Hierarchy', '第一次世界大戰及奧匈帝國瓦解（1918年）'),
('費迪南德·帕夫利科夫斯基', 'Ferdinand Pawlikowski', '格拉茨', '天主教', 7, 1927, 1953, '逝世', '正統', 'Catholic-Hierarchy', '奧地利法西斯（1934–1938）、納粹吞併及戰後重建'),
('約瑟夫·舒瓦斯沃爾', 'Josef Schoiswohl', '格拉茨', '天主教', 8, 1954, 1969, '退休', '正統', 'Catholic-Hierarchy', '梵二大公會議奧地利代表'),
('約翰·韋伯', 'Johann Weber', '格拉茨', '天主教', 9, 1969, 2001, '退休', '正統', 'Roman Catholic Diocese of Graz-Seckau Wikipedia', '在任32年；梵二後教會革新'),
('埃貢·卡珀拉里', 'Egon Kapellari', '格拉茨', '天主教', 10, 2001, 2015, '退休', '正統', 'Catholic-Hierarchy', '2001–2015年'),
('威廉·克拉特瓦施爾', 'Wilhelm Krautwaschl', '格拉茨', '天主教', 11, 2015, NULL, NULL, '正統', 'Catholic-Hierarchy', '2015年任命；現任主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '格拉茨' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 7. 埃武拉（天主教，葡萄牙）— 1540年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('恩里克親王', 'Henrique de Portugal (Cardinal-Infante)', '埃武拉', '天主教', 1, 1540, 1564, '晉升', '正統', 'Roman Catholic Archdiocese of Évora Wikipedia; Catholic-Hierarchy', '1540年9月24日教宗保祿三世設立埃武拉大主教區；葡萄牙王子恩里克首任大主教；後成葡萄牙國王（1578–1580）'),
('泰奧托尼奧·德·布拉甘薩', 'Teotónio de Bragança, S.J.', '埃武拉', '天主教', 3, 1578, 1602, '逝世', '正統', 'Catholic-Hierarchy', '耶穌會培訓；葡萄牙被西班牙兼併（1580–1640）時期'),
('若昂·科斯達·德·阿爾梅達', 'João de Melo e Castro', '埃武拉', '天主教', 12, 1789, 1818, '逝世', '正統', 'Catholic-Hierarchy', '拿破崙入侵（1807年）及王室遷巴西期間'),
('曼努埃爾·門德斯', 'Manuel Mendes da Conceição Santos', '埃武拉', '天主教', 18, 1920, 1955, '逝世', '正統', 'Catholic-Hierarchy', '葡萄牙共和國及薩拉查政權（1926–1974）'),
('曼努埃爾·費雷拉-卡布拉爾', 'Manuel Ferreira Cabral', '埃武拉', '天主教', 20, 1977, 2008, '退休', '正統', 'Catholic-Hierarchy', '葡萄牙卡內馨革命後（1974年）民主轉型'),
('何塞·桑塞斯·阿爾弗斯', 'José Sanches Alves', '埃武拉', '天主教', 21, 2008, 2018, '退休', '正統', 'Catholic-Hierarchy', '2008–2018年'),
('弗朗西斯科·塞恩拉-科埃略', 'Francisco Senra Coelho', '埃武拉', '天主教', 22, 2018, NULL, NULL, '正統', 'Catholic-Hierarchy', '2018年任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '埃武拉' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 8. 巴塞羅那（天主教，西班牙）— 1964年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('格雷戈里奧·莫德雷戈', 'Gregorio Modrego y Casaus', '巴塞羅那', '天主教', 1, 1964, 1967, '退休', '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Barcelona Wikipedia', '1964年3月25日升格非都市總主教區；莫德雷戈首任大主教'),
('馬塞洛·岡薩雷斯·馬丁', 'Marcelo González Martín', '巴塞羅那', '天主教', 2, 1967, 1971, '調任', '正統', 'Catholic-Hierarchy', '後調任托萊多大主教'),
('納西索·朱巴尼', 'Narciso Jubany Arnau', '巴塞羅那', '天主教', 3, 1971, 1992, '退休', '正統', 'Catholic-Hierarchy', '在任21年；西班牙民主轉型（1975年後）；1973年樞機'),
('里卡多·卡萊斯', 'Ricardo María Carles Gordó', '巴塞羅那', '天主教', 4, 1992, 2004, '退休', '正統', 'Catholic-Hierarchy', '1994年樞機'),
('呂斯·馬丁內斯·西斯達赫', 'Lluís Martínez Sistach', '巴塞羅那', '天主教', 5, 2004, 2015, '退休', '正統', 'Catholic-Hierarchy', '2004年都市總主教區確立；2007年樞機'),
('胡安·何塞·奧梅拉', 'Juan José Omella', '巴塞羅那', '天主教', 6, 2015, NULL, NULL, '正統', 'Catholic-Hierarchy', '2015年任命；2017年樞機；現任；西班牙主教團主席')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '巴塞羅那' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 9. 布爾戈斯（天主教，西班牙）— 1075年建立
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('西蒙·德·比爾維斯卡', 'Simeon de Burgos', '布爾戈斯', '天主教', 1, 1075, 1082, '逝世', '正統', 'Catholic Encyclopedia: Archdiocese of Burgos; Roman Catholic Archdiocese of Burgos Wikipedia', '1075年阿方索六世設立布爾戈斯主教區；西蒙首任主教'),
('帕布洛·德·桑塔馬麗婭', 'Pablo de Santa María (Solomon ha-Levi)', '布爾戈斯', '天主教', 10, 1415, 1435, '逝世', '正統', 'Catholic Encyclopedia: Burgos; Paul of Burgos Wikipedia', '出生為猶太拉比（所羅門·哈·萊維），1390年代改信；西班牙最博學的主教之一；巴塞爾大公會議顧問'),
('阿方索·德·卡塔赫納', 'Alfonso de Cartagena', '布爾戈斯', '天主教', 11, 1435, 1456, '逝世', '正統', 'Catholic Encyclopedia: Burgos', '帕布洛之子；巴塞爾大公會議代表；西班牙早期人文主義'),
('克里斯托瓦爾·貝拉', 'Cristóbal Vela y Acuña', '布爾戈斯', '天主教', 20, 1580, 1599, '逝世', '正統', 'Catholic-Hierarchy', '1574年布爾戈斯升格都主教區後早期大主教；西班牙黃金時代'),
('胡安·維克托里亞諾·里瓦斯', 'Juan Victoriano Rivas Dávila', '布爾戈斯', '天主教', 35, 1889, 1901, '逝世', '正統', 'Catholic-Hierarchy', '西班牙美西戰爭（1898年）失去殖民地時期'),
('弗朗西斯科·卡薩斯', 'Francisco Cases García', '布爾戈斯', '天主教', 44, 2002, 2024, '退休', '正統', 'Catholic-Hierarchy', '在任22年'),
('胡利奧·加林多', 'Julio Galindo Aguilar', '布爾戈斯', '天主教', 45, 2024, NULL, NULL, '正統', 'Catholic-Hierarchy', '2024年任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '布爾戈斯' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 10. 里加（天主教）— 1918年至今；注：與信義宗里加大主教不同
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('愛德華·奧魯爾克', 'Edward O''Rourke', '里加', '天主教', 1, 1918, 1920, '調任', '正統', 'Roman Catholic Archdiocese of Riga Wikipedia; Catholic-Hierarchy', '1918年拉脫維亞獨立後恢復天主教里加教區；奧魯爾克首任主教'),
('安托尼斯·斯普林戈維奇斯', 'Antonijs Springovičs', '里加', '天主教', 2, 1920, 1958, '逝世', '正統', 'Catholic-Hierarchy', '1920年4月14日按立；1923年10月25日升格大主教；在任38年；蘇聯兩次佔領（1940、1944年）下仍在拉脫維亞牧養'),
('尤利亞尼斯·瓦伊沃茲', 'Julijans Vaivods', '里加', '天主教', 3, 1964, 1990, '退休', '正統', 'Catholic-Hierarchy', '1964–1990年宗座代牧；蘇聯時代最長任期；1983年保密樞機'),
('約翰·普賈茨', 'Jānis Pujats', '里加', '天主教', 4, 1991, 2010, '退休', '正統', 'Catholic-Hierarchy', '1991年拉脫維亞獨立恢復；2001年樞機'),
('茲比格涅夫斯·斯坦克維奇斯', 'Zbigņevs Stankevičs', '里加', '天主教', 5, 2010, NULL, NULL, '正統', 'Catholic-Hierarchy', '2010年6月19日任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '里加' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 11. 布拉提斯拉瓦（天主教，斯洛伐克）— 1977年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('尤利烏斯·加布里什', 'Julius Gábriš', '布拉提斯拉瓦', '天主教', 1, 1973, 1987, '逝世', '正統', 'Archdiocese of Bratislava Wikipedia; Catholic-Hierarchy', '1977年12月30日升格為大主教區；加布里什1973年起任主教升格後成首任大主教；捷克斯洛伐克共產政府下'),
('揚·索科爾', 'Ján Sokol', '布拉提斯拉瓦', '天主教', 2, 1989, 2008, '調任', '正統', 'Catholic-Hierarchy', '1989年任命；天鵝絨革命後自由恢復；1993年捷克斯洛伐克分裂'),
('斯塔尼斯拉夫·茲沃倫斯基', 'Stanislav Zvolenský', '布拉提斯拉瓦', '天主教', 3, 2008, NULL, NULL, '正統', 'Catholic-Hierarchy', '2008年2月14日任命；現任；斯洛伐克主教團主席')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '布拉提斯拉瓦' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 12. 科希策（天主教，斯洛伐克）— 1995年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿洛伊茲·特卡奇', 'Alojz Tkáč', '科希策', '天主教', 1, 1990, 2010, '退休', '正統', 'Archdiocese of Košice Wikipedia; Catholic-Hierarchy', '1990年2月14日任命；1995年3月31日升格都市大主教區；特卡奇首任大主教；斯洛伐克民主轉型後'),
('貝爾納德·博貝爾', 'Bernard Bober', '科希策', '天主教', 2, 2010, NULL, NULL, '正統', 'Catholic-Hierarchy', '2010年6月4日任命；曾任特卡奇助理主教；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '科希策' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 13. 莫斯科（天主教）— 1991年宗座代牧至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('塔德烏什·孔德魯謝維奇', 'Tadeusz Kondrusiewicz', '莫斯科', '天主教', 1, 1991, 2007, '調任', '正統', 'Tadeusz Kondrusiewicz Wikipedia; Archdiocese of Moscow Wikipedia', '1991年4月13日設立歐洲俄羅斯宗座代牧；2002年升格為莫斯科聖母大教堂大主教區（拉丁禮）；後調任明斯克-馬依洛夫大主教'),
('保羅·佩齊', 'Paolo Pezzi', '莫斯科', '天主教', 2, 2007, NULL, NULL, '正統', 'Paolo Pezzi Wikipedia; Catholic-Hierarchy', '2007年9月21日本篤十六世任命；義大利人；管轄俄羅斯約10萬拉丁禮天主教徒；2022年俄烏戰爭後局勢複雜')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '莫斯科' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 14. 加拉加斯（天主教，委內瑞拉）— 1803年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('弗朗西斯科·德·伊瓦拉', 'Francisco de Ibarra y Herrera', '加拉加斯', '天主教', 1, 1803, 1806, '逝世', '正統', 'Roman Catholic Archdiocese of Caracas Wikipedia; Catholic-Hierarchy', '1803年11月27日加拉加斯升格為都主教區；伊瓦拉首任大主教'),
('拉蒙·伊格納西奧·門德斯', 'Ramón Ignacio Méndez', '加拉加斯', '天主教', 3, 1828, 1839, '逝世', '正統', 'Catholic-Hierarchy', '委內瑞拉獨立（1821年）後；玻利瓦爾時代'),
('西爾韋斯特雷·格瓦拉', 'Silvestre Guevara y Lira', '加拉加斯', '天主教', 6, 1852, 1891, '逝世', '正統', 'Catholic-Hierarchy', '長任大主教；委內瑞拉政治動盪及自由主義改革期'),
('胡安·巴蒂斯塔·卡斯特羅', 'Juan Bautista Castro', '加拉加斯', '天主教', 8, 1904, 1915, '逝世', '正統', 'Catholic-Hierarchy', '委內瑞拉卡斯特羅及戈麥斯獨裁時期'),
('盧卡斯·卡斯蒂略', 'Lucas Guillermo Castillo Hernández', '加拉加斯', '天主教', 10, 1933, 1963, '退休', '正統', 'Catholic-Hierarchy', '胡安·比森特·戈麥斯逝世（1935年）後委內瑞拉政治轉型'),
('何塞·溫貝托·金特羅', 'José Humberto Quintero', '加拉加斯', '天主教', 11, 1963, 1980, '退休', '正統', 'Catholic-Hierarchy', '委內瑞拉石油繁榮期；1960年代社會改革；1961年樞機'),
('何塞·阿里·萊布倫·莫拉托斯', 'José Alí Lebrún Moratinos', '加拉加斯', '天主教', 12, 1980, 1995, '退休', '正統', 'Catholic-Hierarchy', '委內瑞拉民主鞏固時期'),
('伊格納西奧·韋拉斯科', 'Ignacio Antonio Velasco García, S.D.B.', '加拉加斯', '天主教', 13, 1995, 2003, '逝世', '正統', 'Catholic-Hierarchy', '委內瑞拉查韋斯政府（1999年起）；2002年政治危機期間任大主教'),
('豪爾赫·烏羅薩·薩維諾', 'Jorge Liberato Urosa Savino', '加拉加斯', '天主教', 14, 2005, 2018, '退休', '正統', 'Catholic-Hierarchy', '2005年任命；2006年樞機；委內瑞拉社會主義體制下捍衛教會自由；2021年逝世'),
('赫蘇斯·岡薩雷斯·德·薩拉特', 'Jesús González de Zarate, O.A.R.', '加拉加斯', '天主教', 15, 2018, 2024, '退休', '正統', 'Catholic-Hierarchy', '馬杜羅政府下牧養教會'),
('勞爾·比奧爾德·卡斯蒂略', 'Raúl Biord Castillo', '加拉加斯', '天主教', 16, 2024, NULL, NULL, '正統', 'Catholic News Agency 2024', '2024年6月28日教宗方濟各任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '加拉加斯' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 15. 蒙特維的亞（天主教，烏拉圭）— 1878年建立，1897年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('哈辛托·維拉·阿爾蘇阿', 'Jacinto Vera y Alsúa', '蒙特維的亞', '天主教', 1, 1878, 1881, '逝世', '正統', 'Archdiocese of Montevideo Wikipedia; Catholic-Hierarchy', '1878年7月13日設立蒙特維的亞教區；維拉·阿爾蘇阿首任主教；1881年逝世'),
('馬里亞諾·索萊爾·比達爾', 'Mariano Soler Vidal', '蒙特維的亞', '天主教', 2, 1897, 1908, '逝世', '正統', 'Archdiocese of Montevideo Wikipedia; Catholic-Hierarchy', '1897年4月14日升格都主教區；索萊爾·比達爾首任大主教；烏拉圭現代化時期'),
('胡安·弗朗西斯科·阿拉貢', 'Juan Francisco Aragone', '蒙特維的亞', '天主教', 3, 1919, 1940, '逝世', '正統', 'Catholic-Hierarchy', '兩次世界大戰；烏拉圭巴特勒改革（社會民主化）'),
('安東尼奧·巴比耶里', 'Antonio María Barbieri, O.F.M.Cap.', '蒙特維的亞', '天主教', 4, 1940, 1976, '退休', '正統', 'Catholic-Hierarchy', '1940–1976年；在任36年；1958年樞機；烏拉圭世俗化社會中的教會角色'),
('卡洛斯·帕爾托利', 'Carlos Parteli', '蒙特維的亞', '天主教', 5, 1976, 1985, '退休', '正統', 'Catholic-Hierarchy', '烏拉圭軍事獨裁（1973–1985）期間；人權聲援'),
('尼古拉斯·科通尼奧', 'Nicolás Cotugno Fanizzi, S.D.B.', '蒙特維的亞', '天主教', 6, 1998, 2014, '退休', '正統', 'Archdiocese of Montevideo Wikipedia', '1998–2014年'),
('達尼埃爾·斯圖爾拉', 'Daniel Fernando Sturla Berhouet, S.D.B.', '蒙特維的亞', '天主教', 7, 2014, NULL, NULL, '正統', 'Archdiocese of Montevideo Wikipedia; Catholic-Hierarchy', '2014年2月11日任命；2015年樞機；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蒙特維的亞' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 16. 瓜亞基爾（天主教，厄瓜多）— 1838年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('弗朗西斯科·加賴科阿', 'Francisco Xavier de Garaycoa Llaguno', '瓜亞基爾', '天主教', 1, 1838, 1851, '晉升', '正統', 'Catholic-Hierarchy', '1838年1月29日設立瓜亞基爾主教區；加賴科阿首任主教；後調任基多大主教'),
('托馬斯·阿吉雷', 'Tomás Aguirre', '瓜亞基爾', '天主教', 2, 1861, 1868, '逝世', '正統', 'Catholic-Hierarchy', '第二任主教'),
('羅伯托·德爾·波佐', 'Roberto Maria del Pozo, S.J.', '瓜亞基爾', '天主教', 4, 1884, 1912, '逝世', '正統', 'Catholic-Hierarchy', '在任28年；厄瓜多自由主義革命（1895年）及教會-國家衝突'),
('卡洛斯·瑪麗婭·德拉托雷', 'Carlos María de la Torre', '瓜亞基爾', '天主教', 7, 1926, 1933, '調任', '正統', 'Catholic-Hierarchy', '後調任基多大主教'),
('何塞·費利克斯·埃雷迪亞', 'José Félix Heredia Zurita, S.J.', '瓜亞基爾', '天主教', 8, 1937, 1954, '逝世', '正統', 'Catholic-Hierarchy', '厄瓜多政治動盪（1940年代多次政變）'),
('塞薩爾·莫斯克拉·科拉爾', 'César Mosquera Corral', '瓜亞基爾', '天主教', 9, 1954, 1969, '退休', '正統', 'Catholic-Hierarchy', '梵二大公會議期間；厄瓜多現代化'),
('貝爾納迪諾·埃切維里亞·魯伊斯', 'Bernardino Echeverría Ruiz, O.F.M.', '瓜亞基爾', '天主教', 10, 1969, 1989, '退休', '正統', 'Catholic-Hierarchy', '在任20年；梵二後牧靈更新；1978年拉丁美洲主教團（CELAM）普埃布拉大會'),
('胡安·拉雷阿·霍爾金', 'Juan Ignacio Larrea Holguín', '瓜亞基爾', '天主教', 11, 1989, 2003, '退休', '正統', 'Catholic-Hierarchy', '1989–2003年；都市升格後首任大主教'),
('安東尼奧·阿雷基·亞爾薩', 'Antonio Arregui Yarza', '瓜亞基爾', '天主教', 12, 2003, 2015, '退休', '正統', 'Catholic-Hierarchy', '厄瓜多科雷亞政府（2007–2017年）期間'),
('路易斯·卡布雷拉·埃雷拉', 'Luis Gerardo Cabrera Herrera, O.F.M.', '瓜亞基爾', '天主教', 13, 2015, NULL, NULL, '正統', 'Catholic-Hierarchy', '2015年9月24日任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '瓜亞基爾' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 17. 基多（天主教，厄瓜多）— 1848年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('尼古拉斯·德·阿爾特塔', 'Nicolás Joaquín de Arteta y Calisto', '基多', '天主教', 1, 1848, 1849, '逝世', '正統', 'Roman Catholic Archdiocese of Quito Wikipedia; Catholic-Hierarchy', '1848年1月13日基多升格為都主教區；阿爾特塔首任大主教；任期甚短'),
('弗朗西斯科·德·加賴科阿（再任）', 'Francisco de Garaycoa (transferred)', '基多', '天主教', 2, 1851, 1851, '逝世', '正統', 'Catholic-Hierarchy', '從瓜亞基爾調任；同年逝世'),
('何塞·伊格納西奧·切卡·巴爾巴', 'José Ignacio Checa y Barba', '基多', '天主教', 4, 1868, 1877, '殉道', '正統', 'Catholic-Hierarchy', '1877年3月30日彌撒中毒殉道；著名案例；厄瓜多自由主義與天主教衝突時期'),
('何塞·伊格納西奧·奧爾多涅斯', 'José Ignacio Ordóñez', '基多', '天主教', 5, 1882, 1893, '逝世', '正統', 'Catholic-Hierarchy', '自由派勝利（1895年）前夕'),
('費德里科·岡薩雷斯·蘇阿雷斯', 'Federico González y Suárez', '基多', '天主教', 7, 1906, 1917, '逝世', '正統', 'Catholic-Hierarchy', '厄瓜多偉大歷史學家；著有《厄瓜多通史》'),
('卡洛斯·瑪麗婭·德拉托雷（基多）', 'Carlos María de la Torre (Quito)', '基多', '天主教', 8, 1933, 1967, '退休', '正統', 'Catholic-Hierarchy', '從瓜亞基爾調任；在任34年；梵二大公會議參與'),
('帕布洛·穆尼奧斯·維加', 'Pablo Muñoz Vega, S.J.', '基多', '天主教', 9, 1967, 1985, '退休', '正統', 'Catholic-Hierarchy', '梵二後拉丁美洲解放神學討論；1969年樞機'),
('安東尼奧·岡薩雷斯·苏馬拉加', 'Antonio González Zumárraga', '基多', '天主教', 10, 1985, 2010, '退休', '正統', 'Catholic-Hierarchy', '1985–2010年；推動印第安人及農村牧靈'),
('福斯托·特拉維茲', 'Fausto Gabriel Trávez Trávez, O.F.M.', '基多', '天主教', 11, 2010, 2019, '退休', '正統', 'Catholic-Hierarchy', '2010–2019年'),
('阿爾弗雷多·埃斯皮諾薩·馬特烏斯', 'Alfredo José Espinoza Mateus, S.D.B.', '基多', '天主教', 12, 2019, NULL, NULL, '正統', 'Catholic-Hierarchy', '2019年任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '基多' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 18. 聖安東尼奧（天主教，美國）— 1926年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('亞瑟·傑羅姆·德羅薩茨', 'Arthur Jerome Drossaerts', '聖安東尼奧', '天主教', 1, 1926, 1940, '逝世', '正統', 'Archdiocese of San Antonio Wikipedia; Catholic-Hierarchy', '1926年8月3日聖安東尼奧升格都主教區；德羅薩茨首任大主教'),
('羅伯特·盧西', 'Robert E. Lucey', '聖安東尼奧', '天主教', 2, 1941, 1969, '退休', '正統', 'Archdiocese of San Antonio Wikipedia', '在任28年；民權運動支持者；關注農場工人及移民權益'),
('弗朗西斯·富雷', 'Francis James Furey', '聖安東尼奧', '天主教', 3, 1969, 1979, '逝世', '正統', 'Catholic-Hierarchy', '梵二後牧靈更新；德克薩斯拉丁裔天主教徒增長'),
('帕特里克·弗洛雷斯', 'Patrick Fernández Flores', '聖安東尼奧', '天主教', 4, 1979, 2004, '退休', '正統', 'Archdiocese of San Antonio Wikipedia', '首位墨西哥裔美國天主教大主教；在任25年；拉丁裔權益倡導者'),
('何塞·戈麥斯', 'José Horacio Gómez Velasco', '聖安東尼奧', '天主教', 5, 2004, 2010, '調任', '正統', 'Catholic-Hierarchy', '後調任洛杉磯大主教（2010年起）；美國主教團主席（2019–2022年）'),
('古斯塔沃·加西亞-西勒', 'Gustavo García-Siller, M.Sp.S.', '聖安東尼奧', '天主教', 6, 2010, NULL, NULL, '正統', 'Gustavo García-Siller Wikipedia; Catholic-Hierarchy', '2010年11月23日就任；現任大主教；宣道聖靈傳教會成員')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '聖安東尼奧' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 19. 邁阿密（天主教，美國）— 1968年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('科爾曼·卡羅爾', 'Coleman Francis Carroll', '邁阿密', '天主教', 1, 1968, 1977, '逝世', '正統', 'Roman Catholic Archdiocese of Miami Wikipedia; Catholic-Hierarchy', '1968年3月2日邁阿密升格都主教區；卡羅爾首任大主教；古巴流亡者社群的精神支柱'),
('愛德華·麥卡錫', 'Edward Anthony McCarthy', '邁阿密', '天主教', 2, 1977, 1994, '退休', '正統', 'Archdiocese of Miami records', '在任17年；拉丁裔天主教徒快速增長'),
('約翰·法瓦洛拉', 'John C. Favalora', '邁阿密', '天主教', 3, 1994, 2010, '退休', '正統', 'Archdiocese of Miami records; Catholic-Hierarchy', '1994–2010年；海地移民天主教社群'),
('托馬斯·文斯基', 'Thomas Gerard Wenski', '邁阿密', '天主教', 4, 2010, NULL, NULL, '正統', 'Roman Catholic Archdiocese of Miami Wikipedia; Catholic-Hierarchy', '2010年4月20日就任；現任大主教；波蘭裔；拉丁裔及海地裔天主教徒牧靈')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '邁阿密' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 20. 胡志明市（天主教，越南）— 1960年建立至今（原西貢）
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('保祿·阮文平', 'Paul Nguyễn Văn Bình', '胡志明市', '天主教', 1, 1960, 1995, '逝世', '正統', 'Roman Catholic Archdiocese of Ho Chi Minh City Wikipedia; Catholic-Hierarchy', '1960年11月24日西貢升格都主教區；阮文平首任大主教；首位越南籍主教；越戰（1955–1975）及1975年南越淪陷後繼續牧養；1995年7月1日逝世'),
('若望·巴蒂斯特·范明曼', 'Jean-Baptiste Phạm Minh Mẫn', '胡志明市', '天主教', 2, 1998, 2014, '退休', '正統', 'Catholic-Hierarchy', '1998年3月1日任命；2003年樞機；越南共產黨政府下的教會領袖'),
('保祿·裴文獨', 'Paul Bùi Văn Ðọc', '胡志明市', '天主教', 3, 2014, 2018, '逝世', '正統', 'Catholic-Hierarchy', '2014年3月22日任命；2018年3月6日突然在羅馬逝世'),
('約瑟夫·阮年', 'Joseph Nguyễn Năng', '胡志明市', '天主教', 4, 2019, NULL, NULL, '正統', 'Catholic-Hierarchy', '2019年10月19日任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '胡志明市' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 21. 北京（天主教）— 1946年建立；含官方CPA及梵蒂岡承認之主教
-- 注：status='爭議' 用於僅獲CPA承認、梵蒂岡未（或事後）承認者
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('托馬斯·田耕莘', 'Thomas Tien Ken-hsin, S.V.D.', '北京', '天主教', 1, 1946, 1967, '逝世', '正統', 'Roman Catholic Archdiocese of Beijing Wikipedia; Catholic-Hierarchy', '1946年5月10日北京升格都主教區；田耕莘首任大主教；中國首位天主教樞機（1946年）；1949年被迫離開中國大陸'),
('方濟各·付鐵山', 'Michael Fu Tie-shan', '北京', '天主教', 2, 1979, 2007, '逝世', '爭議', 'Catholic-Hierarchy; Catholic Church in China Wikipedia', '1979年12月21日中國天主教愛國會（CPA）祝聖；未獲梵蒂岡承認；北京CPA主教；2007年4月20日逝世'),
('馬修斯·裴向德', 'Matthias Leo Pei Xiangde', '北京', '天主教', 3, 1989, 2001, '逝世', '爭議', 'Catholic-Hierarchy', '1989年6月29日CPA祝聖；2001年12月24日逝世'),
('約瑟夫·李山', 'Joseph Li Shan', '北京', '天主教', 4, 2007, NULL, NULL, '正統', 'Joseph Li Shan Wikipedia; Catholic-Hierarchy', '2007年9月21日CPA祝聖；2018年中梵協議後梵蒂岡正式承認；北京大主教兼CPA主席；負責管轄北京約30萬天主教徒')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '北京' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 22. 上海（天主教）— 1946年建立；含CPA、地下教會及複雜情況
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('伊格納修·龔品梅', 'Ignatius Kung Pin-Mei', '上海', '天主教', 1, 1950, 2000, '逝世', '正統', 'Roman Catholic Diocese of Shanghai Wikipedia; Catholic-Hierarchy', '1950年教宗庇護十二世任命；1955年被捕；1960年判無期徒刑；1985年獲釋後軟禁；1988年在羅馬秘密擢升樞機（1991年公開）；2000年3月12日在美逝世'),
('阿洛伊修斯·張家樹', 'Aloysius Zhang Jiashu, S.J.', '上海', '天主教', 2, 1960, 1988, '逝世', '爭議', 'Roman Catholic Diocese of Shanghai Wikipedia', '1960年CPA非法祝聖；上海第一任CPA主教；1988年逝世'),
('阿洛伊修斯·金魯賢', 'Aloysius Jin Luxian, S.J.', '上海', '天主教', 3, 1988, 2013, '逝世', '爭議', 'Roman Catholic Diocese of Shanghai Wikipedia; Asian News 2013', '1985年CPA非法祝聖為助理主教；1988年繼任上海主教；與梵蒂岡關係複雜；部分被承認；2013年逝世'),
('達太·馬達欽', 'Thaddeus Ma Daqin', '上海', '天主教', 4, 2012, NULL, NULL, '爭議', 'Thaddeus Ma Daqin Wikipedia; Catholic-Hierarchy', '2012年7月7日祝聖（梵蒂岡批准）；就任禮上宣布退出CPA；立即被軟禁於佘山神學院；2013年被CPA撤銷；2022年回歸CPA立場後重獲部分自由；處境持續複雜'),
('沈斌', 'Joseph Shen Bin', '上海', '天主教', 5, 2023, NULL, NULL, '正統', 'Catholic-Hierarchy; ChinaAid 2023', '2023年4月中國政府單方面任命（未經梵蒂岡事先批准）；2023年7月梵蒂岡事後承認；引發爭議')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '上海' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 23. 雅加達（天主教，印度尼西亞）— 1961年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿德里阿努斯·賈亞塞普特拉', 'Adrianus Djajasepoetra, S.J.', '雅加達', '天主教', 1, 1961, 1970, '退休', '正統', 'Roman Catholic Archdiocese of Jakarta Wikipedia; Catholic-Hierarchy', '1961年1月3日雅加達升格都主教區；賈亞塞普特拉首任大主教；印度尼西亞首位本地籍天主教大主教'),
('利奧·蘇科托', 'Leo Soekoto, S.J.', '雅加達', '天主教', 2, 1970, 1995, '逝世', '正統', 'Catholic-Hierarchy', '1970–1995年；在任25年；印度尼西亞天主教發展'),
('尤利烏斯·達爾馬阿特馬賈', 'Julius Cardinal Darmaatmadja, S.J.', '雅加達', '天主教', 3, 1995, 2010, '退休', '正統', 'Julius Darmaatmadja Wikipedia; Catholic-Hierarchy', '1995–2010年；1994年樞機；亞洲天主教領袖'),
('伊格納修斯·蘇哈爾約', 'Ignatius Suharyo Hardjoatmodjo', '雅加達', '天主教', 4, 2010, NULL, NULL, '正統', 'Ignatius Suharyo Hardjoatmodjo Wikipedia; Catholic-Hierarchy', '2010年6月29日就任；2019年10月5日教宗方濟各擢升樞機；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '雅加達' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 24. 科倫坡（天主教，斯里蘭卡）— 1886年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('克里斯托夫-艾爾內斯特·邦讓', 'Christophe-Ernest Bonjean, O.M.I.', '科倫坡', '天主教', 1, 1886, 1892, '逝世', '正統', 'Roman Catholic Archdiocese of Colombo Wikipedia; Catholic-Hierarchy', '1886年9月1日教宗良十三世升格科倫坡為都主教區；邦讓首任大主教'),
('安德烈-泰奧菲勒·梅利贊', 'André-Théophile Mélizan, O.M.I.', '科倫坡', '天主教', 2, 1893, 1905, '逝世', '正統', 'Catholic-Hierarchy', '第二任大主教'),
('安托萬·庫德爾', 'Antoine Coudert, O.M.I.', '科倫坡', '天主教', 3, 1905, 1929, '退休', '正統', 'Catholic-Hierarchy', '在任24年；斯里蘭卡民族主義興起時期'),
('托馬斯·庫雷', 'Thomas Cooray, O.M.I.', '科倫坡', '天主教', 5, 1947, 1976, '退休', '正統', 'Roman Catholic Archdiocese of Colombo Wikipedia', '首位斯里蘭卡本地籍大主教；1947–1976年；1965年樞機；1948年斯里蘭卡獨立後教會領袖'),
('尼古拉斯·馬科斯·費爾南多', 'Nicholas Marcus Fernando', '科倫坡', '天主教', 6, 1977, 2002, '退休', '正統', 'Catholic-Hierarchy', '斯里蘭卡內戰（1983–2009年）開始時期'),
('奧斯瓦爾德·戈米斯', 'Oswald Gomis', '科倫坡', '天主教', 7, 2002, 2009, '退休', '正統', 'Catholic-Hierarchy', '2002–2009年'),
('馬爾科姆·蘭吉思', 'Malcolm Ranjith Patabendige Don', '科倫坡', '天主教', 8, 2009, NULL, NULL, '正統', 'Malcolm Ranjith Wikipedia; Catholic-Hierarchy', '2009年6月16日本篤十六世任命；2010年樞機；積極倡導真相與和解（2019年復活節爆炸案後）；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '科倫坡' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 25. 阿爾及爾（天主教，阿爾及利亞）— 1838年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('安托萬-路易-阿道夫·杜普什', 'Antoine-Louis-Adolphe Dupuch', '阿爾及爾', '天主教', 1, 1838, 1846, '辭職', '正統', 'Roman Catholic Archdiocese of Algiers Wikipedia; Catholic-Hierarchy', '1838年8月10日設立阿爾及爾主教區；杜普什首任主教；法國殖民統治初期'),
('路易-安托萬-奧古斯丁·帕維', 'Louis-Antoine-Augustin Pavy', '阿爾及爾', '天主教', 2, 1846, 1866, '逝世', '正統', 'Catholic-Hierarchy', '1866年7月25日升格都主教區'),
('夏爾-馬蒂亞爾-阿勒芒·拉維熱里', 'Charles-Martial-Allemand Lavigerie', '阿爾及爾', '天主教', 3, 1867, 1892, '逝世', '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Algiers Wikipedia', '1867年任命；1882年樞機；創立白袍神父（非洲傳教士）會；廢除奴隸制的積極倡導者'),
('奧古斯丁-費爾南多·萊諾', 'Augustin-Fernand Leynaud', '阿爾及爾', '天主教', 6, 1917, 1953, '退休', '正統', 'Catholic-Hierarchy', '在任36年；兩次世界大戰；阿爾及利亞民族意識興起'),
('萊昂-艾蒂安·杜瓦爾', 'Léon-Etienne Duval', '阿爾及爾', '天主教', 7, 1954, 1988, '退休', '正統', 'Catholic-Hierarchy', '在任34年；支持阿爾及利亞獨立（1962年）；1962年後在穆斯林多數社會中牧養少數天主教徒；1965年樞機；人稱「穆罕默德之友」'),
('昂利-泰奧菲勒·泰西耶', 'Henri-Teophile Teissier', '阿爾及爾', '天主教', 8, 1988, 2008, '退休', '正統', 'Catholic-Hierarchy', '阿爾及利亞內戰（黑色十年，1991–2002年）期間；多位天主教傳教士殉道（1996年提比希里納神父遇難）'),
('保羅·德斯法熱', 'Paul Jacques Marie Desfarges, S.J.', '阿爾及爾', '天主教', 9, 2016, 2021, '退休', '正統', 'Catholic-Hierarchy', '2016–2021年'),
('讓-保羅·韋斯科', 'Jean-Paul Vesco, O.P.', '阿爾及爾', '天主教', 10, 2021, NULL, NULL, '正統', 'Catholic-Hierarchy; SECAM 2022', '2021年12月27日任命；道明會士；2022年樞機；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '阿爾及爾' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 26. 阿比尚（天主教，科特迪瓦）— 1960年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('貝爾納·亞戈', 'Bernard Yago', '阿比尚', '天主教', 1, 1960, 1994, '逝世', '正統', 'Roman Catholic Archdiocese of Abidjan Wikipedia; Catholic-Hierarchy', '1960年4月5日設立大主教區；亞戈首任大主教；科特迪瓦首位本地籍天主教主教；1983年樞機；在任34年'),
('貝爾納·阿格雷', 'Bernard Agré', '阿比尚', '天主教', 2, 1994, 2006, '退休', '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Abidjan Wikipedia', '1994–2006年；2001年樞機；科特迪瓦內戰（2002–2007年）期間'),
('讓-皮埃爾·庫特瓦', 'Jean-Pierre Kutwa', '阿比尚', '天主教', 3, 2006, 2024, '退休', '正統', 'Catholic-Hierarchy', '2006–2024年；2014年樞機；科特迪瓦2010–2011年後選舉危機中呼籲和平'),
('伊格納斯·貝西·多格博', 'Ignace Bessi Dogbo, O.P.', '阿比尚', '天主教', 4, 2024, NULL, NULL, '正統', 'Catholic-Hierarchy; SECAM 2022', '2024年5月20日任命；道明會士；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '阿比尚' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 27. 達喀爾（天主教，塞內加爾）— 1955年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('馬塞爾-弗朗索瓦·勒費弗爾', 'Marcel-François Lefebvre, C.S.Sp.', '達喀爾', '天主教', 1, 1955, 1962, '辭職', '正統', 'Roman Catholic Archdiocese of Dakar Wikipedia; Catholic-Hierarchy', '1955年9月14日達喀爾升格都主教區；勒費弗爾首任大主教；後成傳統主義運動的核心人物（聖庇護十世兄弟會）；1962年辭去達喀爾職務'),
('海辛特·蒂安杜姆', 'Hyacinthe Thiandoum', '達喀爾', '天主教', 2, 1962, 2000, '退休', '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Dakar Wikipedia', '1962–2000年；在任38年；1976年樞機；塞內加爾及西非天主教的重要人物'),
('泰奧多爾-阿德里安·薩爾', 'Théodore-Adrien Sarr', '達喀爾', '天主教', 3, 2000, 2014, '退休', '正統', 'Catholic-Hierarchy', '2000–2014年；2007年樞機'),
('本傑明·恩迪亞耶', 'Benjamin Ndiaye', '達喀爾', '天主教', 4, 2014, 2025, '逝世', '正統', 'Catholic-Hierarchy; Archbishop Benjamin Ndiaye', '2014年12月22日任命；2025年2月22日逝世'),
('安德烈·蓋', 'André Guèye', '達喀爾', '天主教', 5, 2025, NULL, NULL, '正統', 'Catholic-Hierarchy; André Guèye Wikipedia', '2025年2月22日任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '達喀爾' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 28. 盧沙卡（天主教，尚比亞）— 1959年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('亞當·科茲沃維茨基', 'Adam Kozłowiecki, S.J.', '盧沙卡', '天主教', 1, 1959, 1969, '退休', '正統', 'Roman Catholic Archdiocese of Lusaka Wikipedia; Catholic-Hierarchy', '1959年4月25日設立盧沙卡大主教區；科茲沃維茨基首任大主教；波蘭耶穌會士；納粹集中營倖存者；尚比亞獨立（1964年）見證者'),
('伊曼紐爾·米林戈', 'Emmanuel Milingo', '盧沙卡', '天主教', 2, 1969, 1983, '調任', '正統', 'Catholic-Hierarchy', '1969–1983年；後因非傳統治癒活動被調往梵蒂岡；2001年與統一教成員結婚後被除名；戲劇性教會爭議人物'),
('阿德里安·芒甘杜', 'Adrian Mung''andu', '盧沙卡', '天主教', 3, 1984, 1996, '退休', '正統', 'Roman Catholic Archdiocese of Lusaka Wikipedia', '1984–1996年'),
('梅達多·馬宗布韋', 'Medardo Joseph Mazombwe', '盧沙卡', '天主教', 4, 1996, 2006, '退休', '正統', 'Roman Catholic Archdiocese of Lusaka Wikipedia', '1996–2006年；尚比亞主教團主席（1999–2002年）'),
('特萊斯福雷·姆蓬杜', 'Telesphore George Mpundu', '盧沙卡', '天主教', 5, 2006, 2018, '退休', '正統', 'Roman Catholic Archdiocese of Lusaka Wikipedia', '2006–2018年'),
('阿利克·班達', 'Alick Banda', '盧沙卡', '天主教', 6, 2018, NULL, NULL, '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Lusaka Wikipedia', '2018年1月30日任命；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '盧沙卡' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 29. 威靈頓（天主教，紐西蘭）— 1887年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('弗朗西斯·雷德伍德', 'Francis Mary Redwood, S.M.', '威靈頓', '天主教', 1, 1887, 1935, '逝世', '正統', 'Roman Catholic Archdiocese of Wellington Wikipedia; Catholic-Hierarchy', '1887年大主教區設立；雷德伍德首任大主教；在任48年；紐西蘭天主教奠基者'),
('托馬斯·奧謝', 'Thomas O''Shea, S.M.', '威靈頓', '天主教', 2, 1935, 1954, '退休', '正統', 'Catholic-Hierarchy', '1913年任副大主教；1935年雷德伍德逝世後繼任'),
('彼得·麥基夫里', 'Peter McKeefry, S.M.', '威靈頓', '天主教', 3, 1954, 1979, '退休', '正統', 'Roman Catholic Archdiocese of Wellington Wikipedia', '1947年任命；1969年紐西蘭首位樞機'),
('雷金納德·德拉吉', 'Reginald John Delargey', '威靈頓', '天主教', 4, 1974, 1979, '逝世', '正統', 'Roman Catholic Archdiocese of Wellington Wikipedia', '1974–1979年；任內逝世'),
('托馬斯·威廉斯', 'Thomas Stafford Williams', '威靈頓', '天主教', 5, 1979, 2005, '退休', '正統', 'Catholic-Hierarchy', '1979–2005年；1983年樞機；梵二後牧靈更新'),
('約翰·阿切利·杜', 'John Atcherley Dew', '威靈頓', '天主教', 6, 2005, 2023, '退休', '正統', 'Roman Catholic Archdiocese of Wellington Wikipedia', '2005–2023年；2015年樞機'),
('保羅·馬丁', 'Paul Gerard Martin, S.M.', '威靈頓', '天主教', 7, 2023, NULL, NULL, '正統', 'Roman Catholic Archdiocese of Wellington Wikipedia; Catholic-Hierarchy', '2021年1月1日任副大主教；2023年5月5日繼任；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '威靈頓' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 30. 蘇瓦（天主教，斐濟）— 1966年升格至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('維克托·弗利', 'Victor Frederick Foley, S.M.', '蘇瓦', '天主教', 1, 1966, 1967, '辭職', '正統', 'Roman Catholic Archdiocese of Suva Wikipedia; Catholic-Hierarchy', '1966年6月21日蘇瓦升格都主教區（前身為斐濟宗座代牧）；弗利首任大主教；1967年1月1日辭職'),
('喬治·皮爾斯', 'George Hamilton Pearce, S.M.', '蘇瓦', '天主教', 2, 1967, 1976, '辭職', '正統', 'Catholic-Hierarchy', '1967–1976年；斐濟獨立（1970年）見證者'),
('佩特羅·馬塔卡', 'Petero Mataca', '蘇瓦', '天主教', 3, 1976, 2012, '退休', '正統', 'Catholic-Hierarchy', '1976–2012年；在任36年；首位太平洋島嶼人大主教；斐濟政變（1987、2000、2006年）期間牧養教會'),
('彼得·羅伊·鍾', 'Peter Loy Chong', '蘇瓦', '天主教', 4, 2012, NULL, NULL, '正統', 'Peter Loy Chong Wikipedia; Catholic-Hierarchy', '2012年12月19日任命；現任大主教；斐濟族裔')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蘇瓦' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- 31. 德班（天主教，南非）— 1951年建立至今
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('丹尼斯·赫利', 'Denis Eugene Hurley, O.M.I.', '德班', '天主教', 1, 1951, 1992, '退休', '正統', 'Roman Catholic Archdiocese of Durban Wikipedia; Catholic-Hierarchy', '1951年1月11日設立德班大主教區；赫利首任大主教；在任41年；1948年起任納塔爾代牧；反種族隔離制度的最積極天主教聲音之一；梵二大公會議活躍參與者'),
('威爾弗雷德·納皮爾', 'Wilfrid Fox Napier, O.F.M.', '德班', '天主教', 2, 1992, 2021, '退休', '正統', 'Roman Catholic Archdiocese of Durban Wikipedia; Catholic-Hierarchy', '1992–2021年；在任近三十年；1999年樞機；後種族隔離時代南非天主教領袖；真相與和解委員會（TRC）期間'),
('西格弗里德·曼德拉·朱瓦拉', 'Siegfried Mandla Jwara', '德班', '天主教', 3, 2021, NULL, NULL, '正統', 'Catholic-Hierarchy; Roman Catholic Archdiocese of Durban Wikipedia', '2021年6月9日任命；現任大主教；首位班圖族出生的德班大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '德班' AND church = '天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- END OF BATCH 3B — 31 Catholic archdioceses, all church='天主教'
-- ============================================================
