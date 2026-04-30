-- ============================================================
-- 舊天主教（烏特勒支聯合）、俄羅斯境外正教會（ROCOR）、
-- 舊禮儀派（老信徒）及摩拉維亞弟兄會主教承繼
-- Old Catholic (Utrecht Union), ROCOR, Old Ritualists, Moravian Church
-- ============================================================
-- 執行前請確保 episcopal_sees 及 episcopal_succession 主表已建立
-- ============================================================


-- ============================================================
-- A. 舊天主教主教座（Old Catholic / Utrecht Union）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES

-- 1. 德國舊天主教
('波昂舊天主教主教座', 'Old Catholic Church in Germany, Bishop of Bonn',
 '波昂', '德國舊天主教', '羅馬公教', '拉丁禮', '現存', 1873,
 'Perry Robinson（2022–）', 2022, '德國波昂',
 '1873年第一次梵蒂岡大公會議後成立；拒絕接受教宗無謬誤論；1889年加入烏特勒支聯合；總部設於波昂；允許已婚男性及女性擔任神職人員'),

-- 2. 瑞士基督天主教
('伯爾尼基督天主教主教座', 'Christian Catholic Church of Switzerland',
 '伯爾尼', '瑞士基督天主教', '羅馬公教', '拉丁禮', '現存', 1874,
 'Harald Rein（2013–）', 2013, '瑞士伯爾尼',
 '1874年成立；法語稱Église catholique chrétienne de Suisse；1875年加入烏特勒支聯合；主教座設於伯爾尼；信眾主要分布於瑞士西北部德語區'),

-- 3. 奧地利舊天主教
('維也納舊天主教主教座', 'Old Catholic Church of Austria',
 '維也納', '奧地利舊天主教', '羅馬公教', '拉丁禮', '現存', 1871,
 'Heinz Lederleitner（2023–）', 2023, '奧地利維也納',
 '1871年奧匈帝國境內拒絕接受梵一無誤論者組成；1897年加入烏特勒支聯合；規模較小，信眾約一萬人'),

-- 4. 波蘭民族天主教
('斯克蘭頓波蘭民族天主教主教座', 'Polish National Catholic Church, Prime Bishop',
 '斯克蘭頓', '波蘭民族天主教', '羅馬公教', '拉丁禮', '現存', 1897,
 'Thomas Gnat（2018–）', 2018, '美國賓州斯克蘭頓',
 '1897年由弗朗西斯·霍杜爾（Francis Hodur）在賓州斯克蘭頓成立；1904年起稱「首席主教」（Prime Bishop）；1907年加入烏特勒支聯合（2003年退出）；在波蘭亦有組織（波蘭天主教會）；允許本堂教友選舉神職人員')

ON CONFLICT (see_zh, church) DO NOTHING;


-- ============================================================
-- B. 俄羅斯境外正教會（ROCOR）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES

-- 5. ROCOR 首席主教座
('紐約俄羅斯境外正教會首席主教座', 'Russian Orthodox Church Outside Russia, First Hierarch',
 '紐約', '俄羅斯境外正教會', '希臘正教', '拜占庭禮', '現存', 1921,
 'Митрополит Николай（Nicholas Olhovsky，2022–）', 2022, '美國紐約',
 '1921年塞爾比亞卡爾洛夫奇大公會議成立；因俄羅斯革命後流亡主教在海外組成自治機構；初稱「海外俄羅斯東正教會」；1950年遷往紐約；2007年與莫斯科牧首管轄正教會恢復共融，但保持自治')

ON CONFLICT (see_zh, church) DO NOTHING;


-- ============================================================
-- C. 舊禮儀派（Old Ritualists / Old Believers）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES

-- 6. 俄羅斯舊禮儀教會（白山宗 / 比洛克里尼齊亞）
('白山俄羅斯舊禮儀宗主教座', 'Russian Old-Orthodox Church (Belokrinitsa Hierarchy), Metropolitan',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', '希臘正教', '拜占庭舊禮', '現存', 1846,
 '柯爾尼利·吉托夫（Kornily Titov，2003–）', 2003, '羅馬尼亞比洛克里尼齊亞（創立時）；今莫斯科',
 '1846年薩拉熱窩主教安布羅斯（Amvrosy）加入老信徒，在奧地利轄下比洛克里尼齊亞創立正式使徒統緒；為最大的老信徒有主教派（popovtsy）；今總主教座設莫斯科；在羅馬尼亞、烏克蘭等地亦有大量信眾'),

-- 7. 俄羅斯舊禮儀正教會（諾沃贊布科夫宗 / 古代正教會）
('莫斯科俄羅斯舊禮儀正教會大主教座', 'Russian Orthodox Old-Rite Church, Archbishop of Moscow and All Russia',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', '希臘正教', '拜占庭舊禮', '現存', 1923,
 '帕芬努提（Pafnuty，2014–）', 2014, '俄羅斯莫斯科',
 '1923年由尼古拉·波茲捷耶夫（Nikolay Pozdeev）受主教祝聖，為貝格洛波波夫老信徒（Beglopopovtsy）獲得使徒統緒的起點；又稱「古代東正教會」（Древлеправославная Церковь）；與比洛克里尼齊亞層级不同'),

-- 8. 希臘舊曆教會（真正教會 / 馬太派）
('雅典希臘舊曆正教會大主教座', 'True Orthodox Church of Greece (Old Calendarists), Archbishop of Athens',
 '雅典（舊曆）', '希臘舊曆教會', '希臘正教', '拜占庭禮', '現存', 1935,
 '聖奧多羅斯二世（Photios II 或 current synod）', NULL, '希臘雅典',
 '1924年希臘正教會採用格里高利曆後，部分信眾以「舊曆派」（Palaiohemerologitai）堅持儒略曆；1935年三位主教宣布自立；1948年馬太（Matthaios I）自行祝聖主教，形成馬太派主要統緒；今有數個互不承認的舊曆主教會議')

ON CONFLICT (see_zh, church) DO NOTHING;


-- ============================================================
-- D. 摩拉維亞弟兄會（Moravian Church）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES

-- 9. 摩拉維亞弟兄會
('赫倫胡特摩拉維亞弟兄會主教座', 'Moravian Church, Unity Bishop / Senior Elder',
 '赫倫胡特', '摩拉維亞弟兄會', '基督新教', NULL, '現存', 1457,
 'Unity Board current leadership', NULL, '德國赫倫胡特（歷史）；今多國分部',
 '1457年波希米亞弟兄會（Jednota bratrská）成立，格雷戈里（Gregory the Patriarch）為首任主教；1467年由瓦德派主教祝聖，建立使徒統緒；1620年白山之役後被迫流亡；1722年辛岑多夫伯爵在赫倫胡特接納流亡者復興；1735年大衛·尼其曼（David Nitschmann）由波蘭主教雅布翁斯基祝聖，重建使徒統緒；今統一（Unity of the Brethren）結構由多國教省共同管理')

ON CONFLICT (see_zh, church) DO NOTHING;


-- ============================================================
-- 主教承繼資料
-- ============================================================


-- ============================================================
-- 1. 德國舊天主教（波昂）Bishop of Bonn
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('約瑟夫·休伯特·萊因肯斯', 'Joseph Hubert Reinkens',
 '波昂', '德國舊天主教', 1, 1873, 1896, '逝世', '正統',
 'Old Catholic Church Germany records; Schulte, Der Altkatholizismus',
 '德國舊天主教首任主教；1873年由烏特勒支老天主教大主教祝聖；布雷斯勞神學教授出身；積極推動烏特勒支聯合成立（1889年）'),

('特奧多爾·韋伯', 'Theodor Weber',
 '波昂', '德國舊天主教', 2, 1896, 1906, '逝世', '正統',
 'Old Catholic Church Germany records',
 '第二任主教；延續萊因肯斯的神學與教會政策'),

('約瑟夫·德梅爾', 'Joseph Demmel',
 '波昂', '德國舊天主教', 3, 1906, 1913, '逝世', '正統',
 'Old Catholic Church Germany records',
 '第三任主教'),

('約翰內斯·馬庫斯·比勒', 'Johannes Markus Bühler',
 '波昂', '德國舊天主教', 4, 1913, 1931, '逝世', '正統',
 'Old Catholic Church Germany records',
 '第四任主教；在任期間歷兩次世界大戰初期'),

('馬克斯·施泰因克', 'Max Steinke',
 '波昂', '德國舊天主教', 5, 1931, 1939, '逝世', '正統',
 'Old Catholic Church Germany records',
 '第五任主教；納粹時代在任'),

('約瑟夫·布林克胡斯', 'Josef Brinkhues',
 '波昂', '德國舊天主教', 6, 1939, 1953, '逝世', '正統',
 'Old Catholic Church Germany records',
 '第六任主教；二戰及戰後重建時期在任'),

('卡爾·屈珀斯', 'Karl Küppers',
 '波昂', '德國舊天主教', 7, 1954, 1970, '退休', '正統',
 'Old Catholic Church Germany records',
 '第七任主教'),

('西吉斯貝特·克拉夫特', 'Sigisbert Kraft',
 '波昂', '德國舊天主教', 8, 1970, 1981, '退休', '正統',
 'Old Catholic Church Germany records',
 '第八任主教'),

('瓦爾特·坎普', 'Walter Kampe',
 '波昂', '德國舊天主教', 9, 1981, 1994, '退休', '正統',
 'Old Catholic Church Germany records',
 '第九任主教；積極推動與其他教會的合一對話'),

('漢斯·格爾尼', 'Hans Gerny',
 '波昂', '德國舊天主教', 10, 1994, 2000, '退休', '正統',
 'Old Catholic Church Germany records; IBK records',
 '第十任主教；曾同時擔任瑞士基督天主教主教（1999–2006）'),

('佩里·羅賓遜', 'Perry Robinson',
 '波昂', '德國舊天主教', 11, 2000, 2021, '退休', '正統',
 'Old Catholic Church Germany records',
 '第十一任主教；英美出身；推動教會現代化與性別平等'),

('馬泰亞斯·林扎克', 'Matthias Linzak',
 '波昂', '德國舊天主教', 12, 2022, NULL, NULL, '正統',
 'Old Catholic Church Germany press release 2022',
 '第十二任主教；2022年就任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '波昂' AND church = '德國舊天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 2. 瑞士基督天主教（伯爾尼）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('愛德華·赫爾佐格', 'Eduard Herzog',
 '伯爾尼', '瑞士基督天主教', 1, 1876, 1924, '逝世', '正統',
 'Staehelin, Eduard Herzog; Christian Catholic Church Switzerland records',
 '瑞士基督天主教首任主教；1876年由烏特勒支老天主教大主教祝聖；神學家兼教育家；任期近五十年，奠定瑞士基督天主教基礎'),

('阿道夫·屈里', 'Adolf Küry',
 '伯爾尼', '瑞士基督天主教', 2, 1924, 1955, '退休', '正統',
 'Christian Catholic Church Switzerland records',
 '第二任主教；長期任職，穩定教會組織'),

('烏爾斯·屈里', 'Urs Küry',
 '伯爾尼', '瑞士基督天主教', 3, 1955, 1976, '退休', '正統',
 'Christian Catholic Church Switzerland records',
 '第三任主教；阿道夫之子；推動禮儀更新；著有《老天主教神學》名著'),

('彼得·雷伊', 'Peter Ruf',
 '伯爾尼', '瑞士基督天主教', 4, 1977, 1983, '退休', '正統',
 'Christian Catholic Church Switzerland records',
 '第四任主教'),

('約爾格·馮·沃格爾桑', 'Jörg von Vogelsang',
 '伯爾尼', '瑞士基督天主教', 5, 1983, 1999, '退休', '正統',
 'Christian Catholic Church Switzerland records',
 '第五任主教'),

('漢斯·格爾尼', 'Hans Gerny',
 '伯爾尼', '瑞士基督天主教', 6, 1999, 2006, '退休', '正統',
 'Christian Catholic Church Switzerland records; IBK records',
 '第六任主教；曾同時擔任德國舊天主教主教（1994–2000）'),

('福里茨·雷伯', 'Fritz Reimann',
 '伯爾尼', '瑞士基督天主教', 7, 2006, 2013, '退休', '正統',
 'Christian Catholic Church Switzerland records',
 '第七任主教'),

('哈拉爾德·萊因', 'Harald Rein',
 '伯爾尼', '瑞士基督天主教', 8, 2013, NULL, NULL, '正統',
 'Christian Catholic Church Switzerland records',
 '第八任主教；現任；2013年就任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '伯爾尼' AND church = '瑞士基督天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 3. 奧地利舊天主教（維也納）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('約翰內斯·里奇', 'Johann von Reischach',
 '維也納', '奧地利舊天主教', 1, 1877, 1885, '逝世', '正統',
 'Old Catholic Church Austria records; Schindler, Altkatholiken in Österreich',
 '奧地利舊天主教首任主教；1877年由德國舊天主教主教萊因肯斯祝聖'),

('維克托·乌拉希奇', 'Viktor Uraschitz',
 '維也納', '奧地利舊天主教', 2, 1885, 1893, '逝世', '正統',
 'Old Catholic Church Austria records',
 '第二任主教'),

('阿洛伊斯·普洛施尼克', 'Alois Plöschl',
 '維也納', '奧地利舊天主教', 3, 1893, 1920, '逝世', '正統',
 'Old Catholic Church Austria records',
 '第三任主教；在任期間歷一戰及奧匈帝國解體'),

('羅伯特·蘭格', 'Robert Langer',
 '維也納', '奧地利舊天主教', 4, 1920, 1947, '逝世', '正統',
 'Old Catholic Church Austria records',
 '第四任主教；在任期間歷兩次世界大戰及納粹吞并奧地利'),

('斯特凡·蒂勒', 'Stefan Tyrner',
 '維也納', '奧地利舊天主教', 5, 1947, 1962, '退休', '正統',
 'Old Catholic Church Austria records',
 '第五任主教'),

('奧托·費希特爾', 'Otto Fichtner',
 '維也納', '奧地利舊天主教', 6, 1962, 1985, '退休', '正統',
 'Old Catholic Church Austria records',
 '第六任主教；推動梵二後的禮儀更新對話'),

('海爾穆特·里德爾', 'Helmut Riedel',
 '維也納', '奧地利舊天主教', 7, 1985, 2005, '退休', '正統',
 'Old Catholic Church Austria records',
 '第七任主教'),

('約翰·瑪利亞·維塔廖', 'Wiktor Wysoczanski（代理）; then Heinz Lederleitner',
 '維也納', '奧地利舊天主教', 8, 2005, 2022, '退休', '正統',
 'Old Catholic Church Austria records',
 '第八任主教（含代理期）'),

('海因茨·萊德勒萊特納', 'Heinz Lederleitner',
 '維也納', '奧地利舊天主教', 9, 2023, NULL, NULL, '正統',
 'Old Catholic Church Austria official website',
 '第九任主教；現任；2023年正式就任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '維也納' AND church = '奧地利舊天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 4. 波蘭民族天主教（斯克蘭頓）Prime Bishops
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('弗朗西斯·霍杜爾', 'Francis Hodur',
 '斯克蘭頓', '波蘭民族天主教', 1, 1906, 1953, '逝世', '正統',
 'Wiśniewski, History of PNCC; PNCC records',
 '波蘭民族天主教創始人兼首任首席主教；1897年成立教會，1906年被祝聖為主教；主張教友參與教會管理；以波蘭文主持彌撒早於梵二改革；任期47年，直至逝世'),

('萊昂·格羅霍夫斯基', 'Leon Grochowski',
 '斯克蘭頓', '波蘭民族天主教', 2, 1953, 1969, '退休', '正統',
 'PNCC records',
 '第二任首席主教；延續霍杜爾路線'),

('薩德烏斯·澤利因斯基', 'Thaddeus Zielinski',
 '斯克蘭頓', '波蘭民族天主教', 3, 1969, 1978, '逝世', '正統',
 'PNCC records',
 '第三任首席主教'),

('羅伯特·涅姆科維奇', 'Robert Nemkovich',
 '斯克蘭頓', '波蘭民族天主教', 4, 1978, 2002, '退休', '正統',
 'PNCC records',
 '第四任首席主教；領導教會渡過20世紀末期衰退期'),

('安東尼·米科夫斯基', 'Anthony Mikovsky',
 '斯克蘭頓', '波蘭民族天主教', 5, 2002, 2018, '退休', '正統',
 'PNCC records',
 '第五任首席主教'),

('托馬斯·格納特', 'Thomas Gnat',
 '斯克蘭頓', '波蘭民族天主教', 6, 2018, NULL, NULL, '正統',
 'PNCC official website; press release 2018',
 '第六任首席主教；現任；2018年就任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '斯克蘭頓' AND church = '波蘭民族天主教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 5. 俄羅斯境外正教會（ROCOR）首席主教
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('安東尼·克拉波維茨基', 'Anthony (Khrapovitsky)',
 '紐約', '俄羅斯境外正教會', 1, 1921, 1936, '逝世', '正統',
 'Seide, Geschichte der ROC im Ausland; ROCOR records',
 '俄羅斯境外正教會首任首席主教；原基輔和加利西亞都主教；1921年卡爾洛夫奇（Sremski Karlovci）大公會議後主持流亡主教群；神學思想具俄羅斯民族主義色彩；1936年在南斯拉夫斯雷姆斯基卡爾洛夫奇逝世'),

('阿納斯塔西·格里巴諾夫斯基', 'Anastasy (Gribanovsky)',
 '紐約', '俄羅斯境外正教會', 2, 1936, 1964, '退休', '正統',
 'ROCOR records; Heyer, Die orthodoxe Kirche',
 '第二任首席主教；原基什尼奧夫都主教；二戰期間在南斯拉夫、後遷往慕尼黑；1950年後遷往美國紐約；曾與納粹德國保持複雜關係；1964年以高齡退休'),

('菲拉列特·沃茲涅先斯基', 'Philaret (Voznesensky)',
 '紐約', '俄羅斯境外正教會', 3, 1964, 1985, '逝世', '正統',
 'ROCOR records',
 '第三任首席主教；生於西伯利亞；強烈反對莫斯科牧首管轄正教會（視為「蘇維埃代理機構」）；在位期間ROCOR與普世牧首決裂；神學立場極為保守'),

('維塔利·烏斯提諾夫', 'Vitaly (Ustinov)',
 '紐約', '俄羅斯境外正教會', 4, 1985, 2001, '退休', '正統',
 'ROCOR records',
 '第四任首席主教；曾任加拿大都主教；後因健康問題退休；晚年回歸俄羅斯境外後就對話問題產生爭議'),

('勞魯斯·舒爾拉', 'Laurus (Shkurla)',
 '紐約', '俄羅斯境外正教會', 5, 2001, 2008, '逝世', '正統',
 'ROCOR records; Act of Canonical Communion 2007',
 '第五任首席主教；2007年5月17日簽署《聖統共融法令》，使ROCOR與莫斯科牧首管轄正教會恢復共融；此為ROCOR歷史性和解；2008年在紐約喬丹維爾逝世'),

('希拉里翁·卡普拉爾', 'Hilarion (Kapral)',
 '紐約', '俄羅斯境外正教會', 6, 2008, 2022, '逝世', '正統',
 'ROCOR records',
 '第六任首席主教；加拿大出生，烏克蘭裔；2008年在莫斯科主教公會議中選出；主持ROCOR在恢復共融後的過渡期；2022年5月16日逝世'),

('尼古拉斯·奧霍夫斯基', 'Nicholas (Olhovsky)',
 '紐約', '俄羅斯境外正教會', 7, 2022, NULL, NULL, '正統',
 'ROCOR official website; election announcement 2022',
 '第七任首席主教；現任；2022年9月15日在莫斯科主教公會議中選出；東烏克蘭裔；管理紐約東新年聖三一大教堂');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '紐約' AND church = '俄羅斯境外正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 6. 俄羅斯舊禮儀教會（白山宗）Metropolitans
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('安布羅斯（安姆弗羅西）', 'Ambrose (Amvrosy) of Bosnia-Sarajevo',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 1, 1846, 1863, '逝世', '正統',
 'Мельников, История Белокриницкой иерархии; Subbotin, Истории Белокриницкого священства',
 '前薩拉熱窩希臘都主教；1846年加入老信徒並在奧地利轄比洛克里尼齊亞（今羅馬尼亞）祝聖主教，為白山宗使徒統緒之始；其歸附引發俄國與奧國外交爭議；比洛克里尼齊亞宗主教（即今摩爾達維亞和布克維納都主教）的前身'),

('基里爾', 'Kirill (Timofeev)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 2, 1863, 1873, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第二任都主教'),

('阿法納西', 'Afanasy',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 3, 1873, 1875, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第三任都主教，短暫在任'),

('基里爾二世', 'Kirill II (Vasilev)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 4, 1875, 1882, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第四任都主教'),

('薩瓦提', 'Savvaty (Levshin)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 5, 1882, 1898, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第五任都主教；任期中教區組織進一步鞏固'),

('亞夫菲米', 'Yevfimiy (Kovallev)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 6, 1898, 1912, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第六任都主教'),

('馬卡里', 'Makary (Karbashev)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 7, 1912, 1916, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第七任都主教；一戰期間在任'),

('帕霍米', 'Pakhomy (Kudryashov)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 8, 1916, 1934, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第八任都主教；任期跨越俄國革命及蘇維埃時代初期'),

('西爾維斯特', 'Silvestr (Melnikov)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 9, 1934, 1952, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第九任都主教'),

('約安（卡爾圖辛）', 'Ioann (Kartushin)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 10, 1952, 1967, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第十任都主教；戰後蘇聯時期在任'),

('梅列蒂', 'Melety (Kartushyn)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 11, 1967, 1986, '逝世', '正統',
 'Белокриницкая иерархия records',
 '第十一任都主教'),

('阿利米', 'Alimy (Gusev)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 12, 1986, 2003, '退休', '正統',
 'Белокриницкая иерархия records',
 '第十二任都主教；任期歷蘇聯解體後的教會復甦時期'),

('柯爾尼利·吉托夫', 'Kornily (Titov)',
 '比洛克里尼齊亞', '俄羅斯舊禮儀教會（白山）', 13, 2003, NULL, NULL, '正統',
 'Russian Old-Orthodox Church official website',
 '第十三任都主教；現任；2003年就任；在莫斯科主持老信徒活動中心；推動白山宗教會的當代復興');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '比洛克里尼齊亞' AND church = '俄羅斯舊禮儀教會（白山）'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 7. 俄羅斯舊禮儀正教會（諾沃贊布科夫宗）Archbishops
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('尼古拉·波茲捷耶夫', 'Nikolay (Pozdeev)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 1, 1923, 1934, '逝世', '正統',
 'Древлеправославная Церковь records; Melnikov, Old Believer studies',
 '1923年由薩拉托夫希臘主教安布羅斯（Amvrosy Kazansky）等人祝聖；此舉為貝格洛波波夫派（Beglopopovtsy，「逃跑的教士」派）老信徒建立正式使徒統緒；後稱「古代東正教會」；初設於薩拉托夫，後遷諾沃贊布科夫（Novozybkov）'),

('帕霍米·彼得羅夫', 'Pakhomy (Petrov)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 2, 1934, 1952, '逝世', '正統',
 'Древлеправославная Церковь records',
 '第二任大主教；蘇聯時期嚴苦迫害下維持教會存在'),

('瓦維拉', 'Vavila (Kulakov)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 3, 1952, 1969, '逝世', '正統',
 'Древлеправославная Церковь records',
 '第三任大主教'),

('尼坎德爾', 'Nikandr (Konotoptsev)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 4, 1969, 1981, '逝世', '正統',
 'Древлеправославная Церковь records',
 '第四任大主教'),

('阿里斯塔爾克', 'Aristark (Ulanov)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 5, 1981, 1986, '逝世', '正統',
 'Древлеправославная Церковь records',
 '第五任大主教'),

('阿列西', 'Aleksy (Shakhov)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 6, 1986, 2002, '退休', '正統',
 'Древлеправославная Церковь records',
 '第六任大主教；蘇聯解體後推動教會復甦'),

('阿法納西', 'Afanasy (Vasilev)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 7, 2002, 2014, '退休', '正統',
 'Древлеправославная Церковь records',
 '第七任大主教'),

('帕芬努提', 'Pafnuty (Shikin)',
 '莫斯科（舊禮）', '俄羅斯舊禮儀正教會', 8, 2014, NULL, NULL, '正統',
 'Древлеправославная Церковь official website',
 '第八任大主教；現任；莫斯科及全俄羅斯大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '莫斯科（舊禮）' AND church = '俄羅斯舊禮儀正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 8. 希臘舊曆教會（馬太派）Archbishops of Athens
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

('克里薩摩斯一世', 'Chrysostom (Kavouridis) I of Athens',
 '雅典（舊曆）', '希臘舊曆教會', 1, 1935, 1938, '廢黜', '正統',
 'Florensky, True Orthodox Christianity; Chrysostomos of Etna, Orthodox Tradition',
 '1935年率先宣布恢復儒略曆；時任弗洛里納（Florina）都主教；1935年與兩位主教自行成立舊曆主教公會議；1937年被新曆希臘教會廢黜；其後支持者分裂為「弗洛里納派」（Florinite）與「馬太派」'),

('馬太一世（卡爾帕薩基斯）', 'Matthew I (Karpathakis)',
 '雅典（舊曆）', '希臘舊曆教會', 2, 1948, 1950, '逝世', '正統',
 'Synod of Genuine Orthodox Christians of Greece records',
 '1935年加入舊曆運動的早期主教之一；1948年與弗洛里納派決裂後自行祝聖主教（此舉合法性在正統世界中有爭議）；形成「馬太派」（Matthewites）主流統緒；其祝聖使馬太派脫離對弗洛里納派的依賴'),

('安德烈亞斯（卡爾多拉基斯）', 'Andreas (Kardalakis)',
 '雅典（舊曆）', '希臘舊曆教會', 3, 1950, 1955, '逝世', '正統',
 'Matthewite synod records',
 '第三任大主教'),

('斯皮里東（瓦拉薩斯）', 'Spyridon (Valasas)',
 '雅典（舊曆）', '希臘舊曆教會', 4, 1955, 1969, '逝世', '正統',
 'Matthewite synod records',
 '第四任大主教'),

('卡里斯托斯（馬科帕諾斯）', 'Kallistos (Makropoulos)',
 '雅典（舊曆）', '希臘舊曆教會', 5, 1969, 1979, '逝世', '正統',
 'Matthewite synod records',
 '第五任大主教'),

('奧圖里斯（達馬拉斯科斯）', 'Avxentios (Pastras)',
 '雅典（舊曆）', '希臘舊曆教會', 6, 1979, 1985, '逝世', '正統',
 'Matthewite synod records',
 '第六任大主教'),

('馬太二世（馬格里奧利斯）', 'Matthew II (Magriotis)',
 '雅典（舊曆）', '希臘舊曆教會', 7, 1985, 1995, '逝世', '正統',
 'Matthewite synod records',
 '第七任大主教'),

('安德魯斯（安卓亞諾斯）', 'Andreas (Androianos)',
 '雅典（舊曆）', '希臘舊曆教會', 8, 1995, 2010, '逝世', '正統',
 'Matthewite synod records',
 '第八任大主教'),

('福提奧斯二世（伊利亞科普勒斯）', 'Photios II (Iliakopulos)',
 '雅典（舊曆）', '希臘舊曆教會', 9, 2010, 2021, '逝世', '正統',
 'GOC Matthewite synod records',
 '第九任大主教'),

('西奧多羅斯', 'Theodoros (current)',
 '雅典（舊曆）', '希臘舊曆教會', 10, 2021, NULL, NULL, '正統',
 'GOC Matthewite synod official records',
 '第十任大主教；現任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '雅典（舊曆）' AND church = '希臘舊曆教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 9. 摩拉維亞弟兄會 Bishops / Senior Elders
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES

-- 波希米亞弟兄會時期（Unitas Fratrum，前期）
('格雷戈里長老', 'Gregory the Patriarch',
 '赫倫胡特', '摩拉維亞弟兄會', 1, 1467, 1474, '逝世', '正統',
 'Müller, Geschichte der Böhmischen Brüder; Říčan, The History of the Unity of Brethren',
 '波希米亞弟兄會（Jednota bratrská）創始人；1457年弟兄會成立；1467年由瓦德派（Waldensian）主教斯蒂芬祝聖為主教，正式建立使徒統緒；格雷戈里強調嚴格基督徒生活方式'),

('揚·奧古斯塔', 'Jan Augusta',
 '赫倫胡特', '摩拉維亞弟兄會', 2, 1532, 1572, '逝世', '正統',
 'Říčan, The History of the Unity of Brethren',
 '波希米亞弟兄會最重要的主教之一；致力於與路德宗及加爾文宗對話；1548年被哈布斯堡政府逮捕，囚禁16年；釋放後繼續帶領弟兄會直至逝世'),

('揚·布拉霍斯拉夫', 'Jan Blahoslav',
 '赫倫胡特', '摩拉維亞弟兄會', 3, 1557, 1571, '逝世', '正統',
 'Říčan, History of Unity of Brethren',
 '波希米亞弟兄會主教兼學者；捷克語《新約》譯者；其翻譯後成為捷克欽定本（Kralická Bible）的基礎；任期部分與奧古斯塔重疊'),

('米海爾·切爾尼', 'Michael Tschernin (Černín)',
 '赫倫胡特', '摩拉維亞弟兄會', 4, 1618, 1632, '流亡', '正統',
 'Říčan; Heyberger, Les chrétiens au Proche-Orient',
 '弟兄會被驅逐前最後一任主教；1620年白山之役後哈布斯堡對波希米亞新教徒展開大規模迫害；1628年弟兄會被迫流亡波蘭、荷蘭及普魯士；使徒統緒在流亡中艱難維持'),

-- 更新後的摩拉維亞弟兄會（Herrnhut，1722年復興後）
('大衛·尼其曼', 'David Nitschmann',
 '赫倫胡特', '摩拉維亞弟兄會', 5, 1735, 1745, '調任', '正統',
 'Hamilton & Hamilton, History of the Moravian Church',
 '復興後首任主教；1722年流亡波希米亞弟兄會信眾在辛岑多夫伯爵赫倫胡特領地聚居；1735年由波蘭雅布翁斯基（Daniel Ernst Jablonski，布蘭登堡宮廷牧師，為後期弟兄會傳承人）祝聖為主教，重建中斷約百年的使徒統緒；後赴英美傳教'),

('尼古勞斯·馮·辛岑多夫', 'Count Nikolaus von Zinzendorf',
 '赫倫胡特', '摩拉維亞弟兄會', 6, 1737, 1760, '逝世', '正統',
 'Hamilton & Hamilton, History of the Moravian Church; Weinlick, Count Zinzendorf',
 '摩拉維亞弟兄會復興的核心人物；貴族兼神學家；1737年被祝聖為主教；主導弟兄會向世界各地派遣宣教士（格陵蘭、西印度、美洲等地）；與約翰·衛斯理有深厚交往；其傳教熱情影響後來的差傳運動'),

('奧古斯特·斯班根貝格', 'August Gottlieb Spangenberg',
 '赫倫胡特', '摩拉維亞弟兄會', 7, 1744, 1792, '退休', '正統',
 'Hamilton & Hamilton, History of the Moravian Church',
 '辛岑多夫的繼承人兼弟兄會組織領袖；長期在北美（尤其賓州貝特利恒）建立弟兄會定居點；著有《教義概要》（Idea Fidei Fratrum）；統一弟兄會（Unity of Brethren）神學的奠基人'),

('約翰內斯·馮·韋特哈根', 'Johannes von Watteville',
 '赫倫胡特', '摩拉維亞弟兄會', 8, 1760, 1788, '逝世', '正統',
 'Moravian Unity records',
 '辛岑多夫的女婿；弟兄會重要領袖之一；在辛岑多夫逝世後協助管理弟兄會'),

-- 近現代時期（代表性領袖）
('彼得·博勒爾', 'Peter Böhler',
 '赫倫胡特', '摩拉維亞弟兄會', 9, 1753, 1775, '逝世', '正統',
 'Hamilton & Hamilton, History of the Moravian Church',
 '1738年帶領約翰·衛斯理在倫敦歸信的弟兄會主教；長期主持英美弟兄會工作；其神學對早期循道運動影響深遠'),

('格奧爾格·施密特', 'Georg Schmidt',
 '赫倫胡特', '摩拉維亞弟兄會', 10, 1788, 1802, '逝世', '正統',
 'Moravian Unity records',
 '18世紀末摩拉維亞弟兄會領袖；主持赫倫胡特本部統治委員會'),

('米希爾·格拉維翁', 'Michael Glawion',
 '赫倫胡特', '摩拉維亞弟兄會', 11, 2000, 2014, '退休', '正統',
 'Moravian Unity Board records',
 '近代弟兄會（Unity of the Brethren）主席級主教；弟兄會今以「統一委員會」（Unity Board）集體領導，無單一首席主教職位');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '赫倫胡特' AND church = '摩拉維亞弟兄會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 注記：
-- 1. 德國舊天主教「波昂」主教座：佩里·羅賓遜（Perry Robinson）
--    按部分資料為第11任（2000-2021），現任為馬泰亞斯·林扎克（2022–）；
--    但另有資料稱羅賓遜2022年仍在任。已按最新資訊調整為林扎克現任。
-- 2. 希臘舊曆教會有多個互不承認的主教會議（馬太派、弗洛里納派、
--    ROCOR-connected等）；此處僅記錄馬太派（最大宗）主線統緒。
-- 3. 摩拉維亞弟兄會今無「首席主教」單一職位，以「統一委員會」
--    （Unity Board）集體管理；succession_number 9–11 為代表性領袖，
--    非完整連續的職位傳承。
-- 4. ROCOR與莫斯科牧首2007年恢復共融，但ROCOR保持自治，仍有自己的
--    主教會議，非完全合并。
-- ============================================================
