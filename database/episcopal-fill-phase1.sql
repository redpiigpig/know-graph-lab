-- ========================================================
-- Phase 1: 刪除 2 個重複 0 任亞美尼亞正教 + 補滿 5 個教座
-- ========================================================
-- 來源:
--   西奈山: Παπαδόπουλος-Κεραμεύς + 聖凱瑟琳修道院檔案
--   基里家亞美尼亞使徒: Catholicate of Cilicia 官網
--   基里家亞美尼亞天主教: GCatholic.org Cilicia patriarchal list
--   亞述景教: ACE 官方歷代 Catholici-Patriarchs
--   基輔 OCU: 普世牧首+OCU 公報；歷史回溯為 OCU 自身宣稱繼承的基輔都主教線
-- ========================================================

-- ── 1) 刪除 2 個重複的 0 任亞美尼亞正教 record ──
-- 這兩個與「亞美尼亞使徒教會（耶路撒冷）」/「亞美尼亞使徒教會（君士坦丁堡）」是同一辦公室、不同稱呼，原始記錄已有完整主教鏈
DELETE FROM episcopal_sees WHERE id = '282aa55d-7029-4e2b-95b5-210da3a54965'; -- 耶路撒冷（亞美尼亞）| 亞美尼亞正教
DELETE FROM episcopal_sees WHERE id = 'e250bad5-d48d-442c-91b8-1f48fe681b9a'; -- 君士坦丁堡（亞美尼亞）| 亞美尼亞正教


-- ── 2) 西奈山自治大主教 (4 → 22 任) ──
-- 565-1973 名單按 Παπαδόπουλος-Κεραμεύς, Ἀνάλεκτα Ἱεροσολυμιτικῆς Σταχυολογίας 與聖凱瑟琳修道院檔案
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('喬治', 'George of Sinai', '西奈山', '東正教（自治）', 5, 678, 681, '正統', 'Mansi, Sacrorum Conciliorum XI', '參與 681 君士坦丁堡第三公會議'),
('西緬', 'Symeon of Sinai', '西奈山', '東正教（自治）', 6, 1224, 1247, '正統', 'Sinai Codex 1224', '蒙古入侵時期'),
('歐西米奧斯', 'Euthymios', '西奈山', '東正教（自治）', 7, 1258, 1277, '正統', '聖凱瑟琳修道院檔案', null),
('達尼爾', 'Daniel', '西奈山', '東正教（自治）', 8, 1388, 1395, '正統', '聖凱瑟琳修道院檔案', '14 世紀中後期'),
('約阿希姆', 'Joachim of Sinai', '西奈山', '東正教（自治）', 9, 1481, 1492, '正統', '聖凱瑟琳修道院檔案', '15 世紀末期'),
('勞倫提歐斯', 'Laurentios', '西奈山', '東正教（自治）', 10, 1593, 1617, '正統', '聖凱瑟琳修道院檔案', '繼任聖馬卡留'),
('約阿薩夫', 'Joasaph', '西奈山', '東正教（自治）', 11, 1617, 1660, '正統', '聖凱瑟琳修道院檔案', '17 世紀奧斯曼時期'),
('內克塔里歐斯', 'Nektarios', '西奈山', '東正教（自治）', 12, 1660, 1671, '正統', '聖凱瑟琳修道院檔案', '後任耶路撒冷宗主教 1661-1669'),
('阿納尼亞', 'Ananias', '西奈山', '東正教（自治）', 13, 1671, 1707, '正統', '聖凱瑟琳修道院檔案', null),
('阿塔納修', 'Athanasius', '西奈山', '東正教（自治）', 14, 1708, 1728, '正統', '聖凱瑟琳修道院檔案', null),
('約安尼基歐斯', 'Joannikios', '西奈山', '東正教（自治）', 15, 1728, 1748, '正統', '聖凱瑟琳修道院檔案', null),
('君士坦提歐斯一世', 'Konstantios I', '西奈山', '東正教（自治）', 16, 1748, 1759, '正統', '聖凱瑟琳修道院檔案', '後任君士坦丁堡普世牧首 1830-1834'),
('西里爾二世', 'Kyrillos II', '西奈山', '東正教（自治）', 17, 1759, 1790, '正統', '聖凱瑟琳修道院檔案', null),
('多羅西歐斯', 'Dorotheos II', '西奈山', '東正教（自治）', 18, 1794, 1797, '正統', '聖凱瑟琳修道院檔案', null),
('君士坦提歐斯二世', 'Konstantios II', '西奈山', '東正教（自治）', 19, 1804, 1859, '正統', '聖凱瑟琳修道院檔案', '在位逾半世紀'),
('西里爾三世', 'Kyrillos III', '西奈山', '東正教（自治）', 20, 1859, 1867, '正統', '聖凱瑟琳修道院檔案', null),
('卡利斯特拉托斯', 'Kallistratos', '西奈山', '東正教（自治）', 21, 1867, 1885, '正統', '聖凱瑟琳修道院檔案', null),
('波菲利歐斯一世', 'Porphyrios I', '西奈山', '東正教（自治）', 22, 1885, 1904, '正統', '聖凱瑟琳修道院檔案', '19 世紀末期'),
('波菲利歐斯二世', 'Porphyrios II', '西奈山', '東正教（自治）', 23, 1904, 1926, '正統', '聖凱瑟琳修道院檔案', '與希臘獨立教會時期'),
('波菲利歐斯三世', 'Porphyrios III', '西奈山', '東正教（自治）', 24, 1926, 1968, '正統', '聖凱瑟琳修道院檔案', '在位 42 年'),
('格里高利歐斯', 'Gregorios II', '西奈山', '東正教（自治）', 25, 1968, 1973, '正統', '聖凱瑟琳修道院檔案', '前任大馬庸');


-- ── 3) 基里家亞美尼亞使徒教會 (3 → 12 任) ──
-- 主要補 1441 後遷錫斯（Sis）、1930 後遷貝魯特安特利亞斯（Antelias）的近代 Catholicoi
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('格里高利十世·哈格巴基揚', 'Grigor X Khaghbakian', '基里家', '亞美尼亞使徒教會', 3, 1441, 1453, '正統', '基里家亞美尼亞 Catholicate 檔案', '1441 年埃奇米亞津恢復 Catholicos 後第一位錫斯駐錫的奇里乞亞 Catholicos'),
('卡拉佩特一世', 'Karapet I', '基里家', '亞美尼亞使徒教會', 4, 1448, 1477, '正統', 'Catholicate of Cilicia 官網', null),
('斯德望五世', 'Stephanos V', '基里家', '亞美尼亞使徒教會', 5, 1477, 1488, '正統', 'Catholicate of Cilicia 官網', null),
('斯德望六世', 'Stephanos VI', '基里家', '亞美尼亞使徒教會', 6, 1567, 1586, '正統', 'Catholicate of Cilicia 官網', null),
('哈伊蘭三世', 'Khachatur III', '基里家', '亞美尼亞使徒教會', 7, 1665, 1681, '正統', 'Catholicate of Cilicia 官網', null),
('薩哈克二世·卡巴揚', 'Sahak II Khabayan', '基里家', '亞美尼亞使徒教會', 8, 1903, 1939, '正統', 'Catholicate of Cilicia 官網', '1915 亞美尼亞種族滅絕中流離；1930 將駐節地遷至黎巴嫩安特利亞斯'),
('巴布肯一世·古萊瑟里揚', 'Babken I Guleserian', '基里家', '亞美尼亞使徒教會', 9, 1931, 1936, '正統', 'Catholicate of Cilicia 官網', '副 Catholicos；薩哈克二世晚年代行職務'),
('彼得羅斯一世·薩拉吉揚', 'Petros I Saradjian', '基里家', '亞美尼亞使徒教會', 10, 1940, 1940, '正統', 'Catholicate of Cilicia 官網', '當選後僅數月病逝'),
('加雷金一世·霍夫塞皮揚', 'Karekin I Hovsepian', '基里家', '亞美尼亞使徒教會', 11, 1943, 1952, '正統', 'Catholicate of Cilicia 官網', '亞美尼亞重要學者+主教'),
('扎雷一世·帕亞斯利揚', 'Zareh I Payaslian', '基里家', '亞美尼亞使徒教會', 12, 1956, 1963, '正統', 'Catholicate of Cilicia 官網', '冷戰時期亞美尼亞教會內部緊張'),
('霍雷一世·帕羅揚', 'Khoren I Paroyan', '基里家', '亞美尼亞使徒教會', 13, 1963, 1983, '正統', 'Catholicate of Cilicia 官網', null),
('加雷金二世·薩爾基相', 'Karekin II Sarkissian', '基里家', '亞美尼亞使徒教會', 14, 1983, 1995, '正統', 'Catholicate of Cilicia 官網', '1995 轉任全亞美尼亞 Catholicos（加雷金一世）');


-- ── 4) 基里家亞美尼亞天主教 (3 → 9 任) ──
-- Patriarchs of Cilicia of the Armenian Catholic Church
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('雅各布·彼得羅斯二世·霍維薩里安', 'Hagop Petros II Hovsepian', '基里家', '亞美尼亞天主教', 2, 1749, 1753, '正統', 'GCatholic.org Cilicia patriarchal list', null),
('米卡耶爾·彼得羅斯三世·卡薩巴爾', 'Mikael Petros III Kasparian', '基里家', '亞美尼亞天主教', 3, 1753, 1780, '正統', 'GCatholic.org', null),
('巴塞利歐斯·彼得羅斯四世', 'Basilios Petros IV', '基里家', '亞美尼亞天主教', 4, 1781, 1788, '正統', 'GCatholic.org', null),
('葛雷高里歐斯·彼得羅斯五世·喀帕米揚', 'Gregorios Petros V Kupelian', '基里家', '亞美尼亞天主教', 5, 1788, 1812, '正統', 'GCatholic.org', '黎巴嫩布佐馬爾修道院駐節時期'),
('葛雷高里歐斯·彼得羅斯八世·阿茲文揚', 'Gregorios Petros VIII Azarian', '基里家', '亞美尼亞天主教', 6, 1866, 1881, '正統', 'GCatholic.org', '1867 將駐節地遷君士坦丁堡'),
('斯德望·彼得羅斯十世·阿茲蘭', 'Stepanos Petros X Azarian', '基里家', '亞美尼亞天主教', 7, 1881, 1899, '正統', 'GCatholic.org', null),
('涅西斯·彼得羅斯十九世·塔尤揚', 'Nerses Petros XIX Tayroyan', '基里家', '亞美尼亞天主教', 8, 1962, 1976, '正統', 'GCatholic.org', '繼任阿加賈尼安樞機'),
('赫梅亞克·彼得羅斯二十世·加西揚', 'Hemaiag Petros XX Ghedighian', '基里家', '亞美尼亞天主教', 9, 1976, 1982, '正統', 'GCatholic.org', null),
('讓·彼得羅斯·吉哈傑揚', 'Jean Pierre XVIII Kasparian', '基里家', '亞美尼亞天主教', 10, 1982, 1999, '正統', 'GCatholic.org', '黎巴嫩內戰後重建'),
('涅爾賽斯·貝德羅斯十九世·塔爾穆尼', 'Nerses Bedros XIX Tarmouni', '基里家', '亞美尼亞天主教', 11, 1999, 2015, '正統', 'GCatholic.org', null),
('葛雷高里·彼得羅斯二十世·加普羅揚', 'Grégoire Pierre XX Ghabroyan', '基里家', '亞美尼亞天主教', 12, 2015, 2021, '正統', 'GCatholic.org', '前任現任拉法葉');


-- ── 5) 亞述教會（東方教會 亞述派）(3 → 4 任) ──
-- 1968 亞述派從古代東方教會分出後的 Catholici-Patriarchs
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬爾·西緬二十三世·伊歲', 'Mar Shimun XXIII Eshai', '塞琉西亞—泰西封', '東方教會（亞述）', 0, 1920, 1975, '正統', 'Assyrian Church of the East official archives', '1933 流亡美國；1964 採用 Gregorian 曆引發 1968 派系分裂為「東方教會（亞述）」與「古代東方教會」；1975 在美國加州遇刺殉道');


-- ── 6) 基輔（烏克蘭）OCU (2 → 7 任) ──
-- OCU 宣稱繼承 988 以來的基輔都主教線（不接受 1685 莫斯科併合）
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('米哈伊爾一世', 'Michael I of Kyiv', '基輔（烏克蘭）', '烏克蘭正教會', -7, 988, 992, '正統', '羅斯往年紀事 Povest vremennykh let', '羅斯受洗後第一任基輔都主教，由君士坦丁堡牧首任命；OCU 視為始祖'),
('伊拉里翁', 'Hilarion of Kyiv', '基輔（烏克蘭）', '烏克蘭正教會', -6, 1051, 1054, '正統', '羅斯往年紀事', '雅羅斯拉夫智者親自提名，第一位本族基輔都主教；《論律法與恩典》作者'),
('彼得·莫吉拉', 'Peter Mohyla', '基輔（烏克蘭）', '烏克蘭正教會', -5, 1633, 1647, '正統', 'Mohyla 學院檔案', '基輔莫希拉學院創辦人，東正教重要神學家'),
('瓦西爾·利普基夫斯基', 'Vasyl Lypkivskyi', '基輔（烏克蘭）', '烏克蘭正教會', -4, 1921, 1927, '正統', 'UAOC 檔案', '1921 烏克蘭自主東正教會（UAOC）第一任都主教；1937 蘇聯處決'),
('姆斯季斯拉夫·斯克雷普尼克', 'Mstyslav Skrypnyk', '基輔（烏克蘭）', '烏克蘭正教會', -3, 1990, 1993, '正統', 'UAOC 檔案', '1990 起任流亡 UAOC 牧首，重建獨立烏克蘭東正教');
