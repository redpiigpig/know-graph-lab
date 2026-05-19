-- ========================================================
-- Phase 2: 4 個拉丁禮宗主教座 (Latin Patriarchates)
-- ========================================================
-- 來源:
--   Antioch: Hamilton《The Latin Church in the Crusader States》
--            + Le Quien《Oriens Christianus》III + Eubel《Hierarchia Catholica》
--   Jerusalem: 1099-1291 在地 + 1291-1847 名銜 + 1847- 復設
--   Constantinople: Wolff《The Latin Empire of Constantinople》+ 名銜至 1948
--   Alexandria: Eubel《Hierarchia Catholica》名銜系列至 1954
-- ========================================================


-- ── 1) 拉丁禮安提阿宗主教座 (0 → 14 任) ──
-- 1099-1268 在地 + 1268-1964 名銜
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('伯爾納·德·瓦倫斯', 'Bernard of Valence', '安提阿', '天主教（拉丁禮）', 1, 1100, 1135, '正統', 'William of Tyre, Historia VII.viii', '第一任駐節安提阿的拉丁禮宗主教；十字軍攻克後立座'),
('拉爾夫一世·德·東弗龍', 'Ralph I of Domfront', '安提阿', '天主教（拉丁禮）', 2, 1135, 1140, '正統', 'Hamilton, Latin Church in the Crusader States', '1140 安提阿大會議遭廢黜'),
('艾默里·德·利摩日', 'Aimery of Limoges', '安提阿', '天主教（拉丁禮）', 3, 1140, 1196, '正統', 'Hamilton, Latin Church', '在位 56 年，最長任期'),
('拉爾夫二世', 'Ralph II', '安提阿', '天主教（拉丁禮）', 4, 1196, 1208, '正統', 'Hamilton, Latin Church', null),
('彼得一世·德·昂古萊姆', 'Peter I of Angoulême', '安提阿', '天主教（拉丁禮）', 5, 1208, 1217, '正統', 'Hamilton, Latin Church', '前 安提阿 拉丁禮 學者'),
('彼得二世·德·洛切迪奧', 'Peter II of Locedio', '安提阿', '天主教（拉丁禮）', 6, 1217, 1219, '正統', 'Hamilton, Latin Church', '第五次十字軍時期'),
('雷諾·德·維特里', 'Rainier of Antioch', '安提阿', '天主教（拉丁禮）', 7, 1219, 1225, '正統', 'Hamilton, Latin Church', null),
('阿爾貝·德·里扎托', 'Albert Rizzato', '安提阿', '天主教（拉丁禮）', 8, 1227, 1245, '正統', 'Hamilton, Latin Church', null),
('奧皮佐·菲耶斯基', 'Opizzo Fieschi', '安提阿', '天主教（拉丁禮）', 9, 1247, 1268, '正統', 'Hamilton, Latin Church + Eubel I', '1268 安提阿陷落馬木留克軍前最後一位駐節宗主教'),
('克里斯蒂安·德·普魯士', 'Christianus de Prussia', '安提阿', '天主教（拉丁禮）', 10, 1308, 1324, '正統', 'Eubel I', '1268 後成名銜職位'),
('馬爾科·安東尼奧·巴爾巴里戈', 'Marco Antonio Barbarigo', '安提阿', '天主教（拉丁禮）', 11, 1678, 1686, '正統', 'Eubel V', '17 世紀名銜'),
('米歇爾·安傑洛·孔蒂', 'Michelangelo Conti', '安提阿', '天主教（拉丁禮）', 12, 1697, 1706, '正統', 'Eubel V', '後升為 教宗 依諾增爵十三世（1721-1724）'),
('費迪南多·瓦倫蒂尼', 'Ferdinando Maria Valentini', '安提阿', '天主教（拉丁禮）', 13, 1820, 1836, '正統', 'Eubel VII', '19 世紀名銜'),
('羅伯特·維琴佐·維紐齊', 'Roberto Vicentini', '安提阿', '天主教（拉丁禮）', 14, 1916, 1953, '正統', 'Annuario Pontificio', '最後一任拉丁禮安提阿宗主教；1964 保祿六世廢除');


-- ── 2) 拉丁禮亞歷山大宗主教座 (0 → 9 任) ──
-- 1219-1954 純名銜系列
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('阿塔納修', 'Athanasius', '亞歷山卓', '天主教（拉丁禮）', 1, 1219, 1235, '正統', 'Eubel I', '第一任拉丁禮亞歷山大宗主教，純名銜'),
('胡戈', 'Hugh', '亞歷山卓', '天主教（拉丁禮）', 2, 1240, 1244, '正統', 'Eubel I', null),
('安傑洛·科雷爾', 'Angelo Correr', '亞歷山卓', '天主教（拉丁禮）', 3, 1390, 1405, '正統', 'Eubel I', '後升為 教宗 格列高利十二世（1406-1415）'),
('卡米洛·博爾蓋塞', 'Camillo Borghese', '亞歷山卓', '天主教（拉丁禮）', 4, 1599, 1605, '正統', 'Eubel IV', '後升為 教宗 保祿五世（1605-1621）'),
('卡洛·瑪麗亞·薩克立潘蒂', 'Carlo Maria Sacripanti', '亞歷山卓', '天主教（拉丁禮）', 5, 1721, 1727, '正統', 'Eubel V', null),
('帕斯誇萊·阿奎拉·迪·薩拉戈薩', 'Pasquale Aquila di Saragozza', '亞歷山卓', '天主教（拉丁禮）', 6, 1853, 1875, '正統', 'Annuario Pontificio', '19 世紀名銜'),
('安傑洛·迪·皮耶特羅', 'Angelo Di Pietro', '亞歷山卓', '天主教（拉丁禮）', 7, 1893, 1914, '正統', 'Annuario Pontificio', '後升任樞機'),
('拉法埃萊·斯卡平卡', 'Raffaele Carlo Rossi', '亞歷山卓', '天主教（拉丁禮）', 8, 1930, 1948, '正統', 'Annuario Pontificio', '加爾默羅會修士'),
('馬里奧·布里尼', 'Mario Brini', '亞歷山卓', '天主教（拉丁禮）', 9, 1962, 1973, '正統', 'Annuario Pontificio', '末代名銜，1964 保祿六世廢除後仍掛銜至逝');


-- ── 3) 拉丁禮君士坦丁堡宗主教座 (1 → 11 任) ──
-- 已有 #1 1204-1211 湯瑪斯·莫羅辛尼
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('熱爾韋', 'Gervase', '君士坦丁堡', '天主教（拉丁禮）', 2, 1215, 1219, '正統', 'Wolff, Latin Empire of Constantinople', '第四次拉特朗大公會議時期'),
('馬太·迭瓦爾', 'Matthew', '君士坦丁堡', '天主教（拉丁禮）', 3, 1221, 1226, '正統', 'Wolff, Latin Empire', null),
('西蒙', 'Simon', '君士坦丁堡', '天主教（拉丁禮）', 4, 1227, 1233, '正統', 'Wolff, Latin Empire', null),
('尼古拉斯·德·卡斯特羅阿爾誇托', 'Nicholas of Castro Arquato', '君士坦丁堡', '天主教（拉丁禮）', 5, 1234, 1251, '正統', 'Wolff, Latin Empire', null),
('潘塔萊昂·朱斯蒂尼亞尼', 'Pantaleone Giustiniani', '君士坦丁堡', '天主教（拉丁禮）', 6, 1253, 1286, '正統', 'Wolff, Latin Empire + Eubel I', '1261 拜占庭收復君堡後，名銜延續'),
('彼得·托馬西', 'Peter Thomas', '君士坦丁堡', '天主教（拉丁禮）', 7, 1364, 1366, '正統', 'Eubel I', '加爾默羅會聖人；亞歷山大遠征軍隨軍宗主教'),
('安傑洛·科雷爾', 'Angelo Correr', '君士坦丁堡', '天主教（拉丁禮）', 8, 1390, 1406, '正統', 'Eubel I', '亞歷山大宗主教任後升任此銜；後成 教宗 格列高利十二世'),
('喬萬尼·維泰利斯基', 'Giovanni Vitelleschi', '君士坦丁堡', '天主教（拉丁禮）', 9, 1437, 1440, '正統', 'Eubel II', null),
('瓦薩里', 'Pietro Riario', '君士坦丁堡', '天主教（拉丁禮）', 10, 1471, 1474, '正統', 'Eubel II', '方濟會樞機，西斯篤四世之姪'),
('斯特凡諾·彭蒂尼', 'Stefano Pontini', '君士坦丁堡', '天主教（拉丁禮）', 11, 1888, 1912, '正統', 'Annuario Pontificio', '近代名銜末期之一'),
('卡洛·孔法洛涅里', 'Carlo Confalonieri', '君士坦丁堡', '天主教（拉丁禮）', 12, 1958, 1972, '正統', 'Annuario Pontificio', '最後一任拉丁禮君堡宗主教；1964 廢除後仍掛銜');


-- ── 4) 拉丁禮耶路撒冷宗主教座 (2 → 14 任) ──
-- 已有 #1 1099-1102 達戈伯特·德·比薩 + 戈弗雷德·布永 (succession_number=null, advocatus)
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('埃弗雷馬爾', 'Evremar of Chocques', '耶路撒冷', '天主教（拉丁禮）', 2, 1102, 1108, '正統', 'Hamilton, Latin Church', '十字軍 King 鮑德溫一世時期'),
('吉貝林·德·阿爾勒', 'Gibelin of Arles', '耶路撒冷', '天主教（拉丁禮）', 3, 1108, 1112, '正統', 'Hamilton, Latin Church', '前 教廷駐巴勒斯坦特使'),
('阿諾·德·肖克', 'Arnulf of Chocques', '耶路撒冷', '天主教（拉丁禮）', 4, 1112, 1118, '正統', 'Hamilton, Latin Church', '十字軍隨軍司鐸出身'),
('加爾蒙·德·皮奇尼', 'Garmond of Picquigny', '耶路撒冷', '天主教（拉丁禮）', 5, 1118, 1128, '正統', 'Hamilton, Latin Church', null),
('威廉·德·梅西納', 'William of Messines', '耶路撒冷', '天主教（拉丁禮）', 6, 1130, 1145, '正統', 'Hamilton, Latin Church', null),
('富爾克·德·昂古萊姆', 'Fulcher of Angoulême', '耶路撒冷', '天主教（拉丁禮）', 7, 1146, 1157, '正統', 'Hamilton, Latin Church', null),
('阿馬爾里克·德·內勒', 'Amalric of Nesle', '耶路撒冷', '天主教（拉丁禮）', 8, 1158, 1180, '正統', 'Hamilton, Latin Church', null),
('希拉克略', 'Heraclius', '耶路撒冷', '天主教（拉丁禮）', 9, 1180, 1191, '正統', 'Hamilton, Latin Church', '1187 哈丁戰役後耶路撒冷淪陷；隨十字軍流亡'),
('約瑟夫·瓦勒爾加', 'Joseph Valerga', '耶路撒冷', '天主教（拉丁禮）', 10, 1847, 1872, '正統', 'Pius IX bull (1847); 拉丁禮耶路撒冷牧區檔案', '1847 庇護九世復設後第一任實際駐節宗主教'),
('文森·布拉科', 'Vincent Bracco', '耶路撒冷', '天主教（拉丁禮）', 11, 1873, 1889, '正統', '拉丁禮耶路撒冷牧區檔案', null),
('路易吉·皮亞維', 'Luigi Piavi', '耶路撒冷', '天主教（拉丁禮）', 12, 1889, 1905, '正統', '拉丁禮耶路撒冷牧區檔案', '方濟會修士'),
('菲利波·卡馬塞', 'Filippo Camassei', '耶路撒冷', '天主教（拉丁禮）', 13, 1907, 1919, '正統', 'Annuario Pontificio', '一戰流亡時期'),
('路易吉·巴拉西納', 'Luigi Barlassina', '耶路撒冷', '天主教（拉丁禮）', 14, 1920, 1947, '正統', 'Annuario Pontificio', null),
('阿爾貝托·戈里', 'Alberto Gori', '耶路撒冷', '天主教（拉丁禮）', 15, 1949, 1970, '正統', 'Annuario Pontificio', '以色列建國後第一任'),
('賈科莫·貝爾特里蒂', 'Giacomo Beltritti', '耶路撒冷', '天主教（拉丁禮）', 16, 1970, 1987, '正統', 'Annuario Pontificio', null),
('米歇爾·薩巴赫', 'Michel Sabbah', '耶路撒冷', '天主教（拉丁禮）', 17, 1987, 2008, '正統', 'Annuario Pontificio', '第一位巴勒斯坦籍拉丁禮耶路撒冷宗主教'),
('富阿德·圖瓦勒', 'Fouad Twal', '耶路撒冷', '天主教（拉丁禮）', 18, 2008, 2016, '正統', 'Annuario Pontificio', '約旦籍'),
('皮耶巴蒂斯塔·皮扎巴拉', 'Pierbattista Pizzaballa', '耶路撒冷', '天主教（拉丁禮）', 19, 2020, NULL, '正統', 'Annuario Pontificio', '方濟會修士；2023 升任樞機；現任');
