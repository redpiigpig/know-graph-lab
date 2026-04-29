-- ============================================================
-- 東方基督教自主教會歷任首牧列表
-- 涵蓋：東正教各自主教會（含非宗主教座者）
-- 執行前請確保已執行：
--   episcopal-succession.sql
--   episcopal-sees.sql
--   episcopal-sees-seed.sql
--   episcopal-sees-autocephalous.sql
-- ============================================================
-- 欄位說明：
--   see    = 對應 episcopal_sees.see_zh
--   church = 對應 episcopal_sees.church
--   status = 正統（預設）
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- 一、塞浦路斯自主教會（Church of Cyprus）
--     自主地位：431 年以弗所大公會議確認
--     see = '尼科西亞'，church = '東正教（塞浦路斯）'
-- ════════════════════════════════════════════════════════════
-- 完整歷任列表逾 115 任，此處列關鍵人物及現代全列
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('聖巴拿巴', 'Saint Barnabas', '尼科西亞', '東正教（塞浦路斯）', 1, 45, 61, '殉道', '使徒眾人', '正統',
 'Acts 4:36; Eusebius, HE; Cypriot Synaxarion',
 '使徒巴拿巴，猶太人，生於塞浦路斯；傳統首任大主教，約 61 年殉道。其遺骸於 478 年被發現，鞏固塞浦路斯教會的自主主張'),

('聖以巴弗羅底圖', 'Saint Epaphroditus', '尼科西亞', '東正教（塞浦路斯）', 2, 61, 90, '自然死亡', NULL, '正統',
 'Cypriot Synaxarion; local tradition',
 '傳統上為巴拿巴所立，保羅書信中提及其名（腓 2:25）'),

('薩拉米的以彼法紐', 'Epiphanius of Salamis', '尼科西亞', '東正教（塞浦路斯）', NULL, 367, 403, '自然死亡', NULL, '正統',
 'Epiphanius, Panarion; Jerome, De viris illustribus',
 '古代教父中最重要的塞浦路斯大主教；著有《藥匣》（Panarion），駁斥 80 種異端，任大主教達 36 年'),

('安提阿的亞歷山大', 'Alexander of Antioch', '尼科西亞', '東正教（塞浦路斯）', NULL, 488, 490, '不明', NULL, '正統',
 'Council records',
 '490 年君士坦丁堡大公會議上塞浦路斯發現巴拿巴遺骸，確保自主地位的關鍵人物'),

('馬卡里奧斯三世', 'Makarios III', '尼科西亞', '東正教（塞浦路斯）', 111, 1950, 1977, '自然死亡', NULL, '正統',
 'Church of Cyprus records; Crawshaw, The Cyprus Revolt',
 '同時兼任賽普勒斯共和國首任總統（1960–1977）；1974 年土耳其入侵後短暫流亡'),

('赫里索斯托莫斯一世', 'Chrysostomos I', '尼科西亞', '東正教（塞浦路斯）', 112, 1977, 2006, '自然死亡', NULL, '正統',
 'Church of Cyprus records', NULL),

('赫里索斯托莫斯二世', 'Chrysostomos II', '尼科西亞', '東正教（塞浦路斯）', 113, 2006, 2022, '自然死亡', NULL, '正統',
 'Church of Cyprus records',
 '2022 年底去世前，在俄烏戰爭中支持烏克蘭正教會立場，引發部分主教的異見'),

('喬治三世', 'George III', '尼科西亞', '東正教（塞浦路斯）', 114, 2022, NULL, NULL, NULL, '正統',
 'Church of Cyprus Synod records', '2022 年當選，現任大主教');


-- ════════════════════════════════════════════════════════════
-- 二、希臘自主教會（Church of Greece）
--     自主地位：1833 宣布；1850 君士坦丁堡承認
--     see = '雅典'，church = '東正教（希臘）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('赫里索斯托莫斯一世（雅典）', 'Chrysostomos I of Athens', '雅典', '東正教（希臘）', 1, 1923, 1938, '自然死亡', '正統',
 'Church of Greece records',
 '1923 年從土耳其大批希臘人交換後，重組現代希臘教會；第一任以「全希臘大主教」頭銜的大主教'),

('克里桑托斯', 'Chrysanthos of Athens', '雅典', '東正教（希臘）', 2, 1938, 1941, '廢黜', '正統',
 'Church of Greece records',
 '德軍占領期間（1941年）拒絕向德國占領當局宣誓效忠，被迫辭職'),

('達馬斯基諾斯', 'Damaskinos of Athens', '雅典', '東正教（希臘）', 3, 1941, 1949, '自然死亡', '正統',
 'Church of Greece records',
 '二戰占領期間公開護衛猶太人，1944–1945 年兼任希臘攝政；首任與第三任大主教（1938 年短暫被選，1941 年正式就任）'),

('斯比里東', 'Spyridon of Athens', '雅典', '東正教（希臘）', 4, 1949, 1956, '辭職', '正統',
 'Church of Greece records', NULL),

('多羅西奧斯三世', 'Dorotheos III of Athens', '雅典', '東正教（希臘）', 5, 1956, 1957, '自然死亡', '正統',
 'Church of Greece records', NULL),

('泰奧克利托斯二世', 'Theocletos II of Athens', '雅典', '東正教（希臘）', 6, 1957, 1962, '自然死亡', '正統',
 'Church of Greece records', NULL),

('雅各布三世', 'Jacob III of Athens', '雅典', '東正教（希臘）', 7, 1962, 1962, '自然死亡', '正統',
 'Church of Greece records', '任期甚短，數月即去世'),

('赫里索斯托莫斯二世（雅典）', 'Chrysostomos II of Athens', '雅典', '東正教（希臘）', 8, 1962, 1967, '廢黜', '正統',
 'Church of Greece records', '1967 年軍事政變後被軍政府解除職務'),

('耶羅尼莫斯一世', 'Ieronymos I of Athens', '雅典', '東正教（希臘）', 9, 1967, 1973, '辭職', '廢黜後復位',
 'Church of Greece records', '軍政府倒台後辭職'),

('塞拉費姆', 'Seraphim of Athens', '雅典', '東正教（希臘）', 10, 1974, 1998, '辭職', '正統',
 'Church of Greece records', '任期長達 24 年，見證希臘民主恢復至後冷戰時代'),

('赫里斯托杜盧斯', 'Christodoulos of Athens', '雅典', '東正教（希臘）', 11, 1998, 2008, '自然死亡', '正統',
 'Church of Greece records',
 '積極推動東正教在歐盟框架下的地位；任內與教宗若望保祿二世會面'),

('耶羅尼莫斯二世', 'Ieronymos II of Athens', '雅典', '東正教（希臘）', 12, 2008, NULL, NULL, '正統',
 'Church of Greece records', '現任大主教；任內積極參與社會救濟，並維護希臘-土耳其教會關係');


-- ════════════════════════════════════════════════════════════
-- 三、波蘭自主正教會（Polish Autocephalous Orthodox Church）
--     自主地位：1924 年（君士坦丁堡 Tomos）
--     see = '華沙'，church = '東正教（波蘭）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('格奧爾基·雅羅謝夫斯基', 'Metropolitan George (Jaroszewski)', '華沙', '東正教（波蘭）', 1, 1921, 1923, '殉道', '正統',
 'Polish Orthodox Church records',
 '首任大主教，1923 年被刺身亡'),

('狄奧尼修斯·瓦列金斯基', 'Metropolitan Dionysius (Waledyński)', '華沙', '東正教（波蘭）', 2, 1923, 1948, '廢黜', '正統',
 'Polish Orthodox Church records',
 '獲得 1924 年君士坦丁堡自主地位 Tomos；二戰後被蘇聯支持的派系廢黜'),

('提摩太·謝萊斯基（代理）', 'Bishop Timothy (locum tenens)', '華沙', '東正教（波蘭）', NULL, 1948, 1951, NULL, '正統',
 'Polish Orthodox Church records', '代理期間，莫斯科宗主教座於 1948 年授予新的自主地位 Tomos'),

('馬卡里奧斯·奧克修克', 'Metropolitan Macarius (Oksijuk)', '華沙', '東正教（波蘭）', 3, 1951, 1959, '辭職', '正統',
 'Polish Orthodox Church records', NULL),

('提摩太·施萊特爾', 'Metropolitan Timotheus (Szretter)', '華沙', '東正教（波蘭）', 4, 1961, 1962, '自然死亡', '正統',
 'Polish Orthodox Church records', NULL),

('斯蒂凡·魯迪克', 'Metropolitan Stefan (Rudyk)', '華沙', '東正教（波蘭）', 5, 1965, 1969, '自然死亡', '正統',
 'Polish Orthodox Church records', NULL),

('巴西利·多羅什科維奇', 'Metropolitan Basil (Doroszkiewicz)', '華沙', '東正教（波蘭）', 6, 1970, 1998, '辭職', '正統',
 'Polish Orthodox Church records', '任期長達 28 年'),

('薩瓦·赫里楚尼亞克', 'Metropolitan Sawa (Hrycuniak)', '華沙', '東正教（波蘭）', 7, 1998, NULL, NULL, '正統',
 'Polish Orthodox Church records', '現任都主教');


-- ════════════════════════════════════════════════════════════
-- 四、阿爾巴尼亞自主正教會（Albanian Orthodox Church）
--     自主地位：1937（君士坦丁堡正式承認）
--     see = '地拉那'，church = '東正教（阿爾巴尼亞）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('赫里斯托佛·基西', 'Archbishop Kristofor (Kisi)', '地拉那', '東正教（阿爾巴尼亞）', 1, 1937, 1948, '廢黜', '正統',
 'Albanian Orthodox Church records; Vickers, The Albanians',
 '獲君士坦丁堡 Tomos 後首任大主教；1948 年被共產政府廢黜'),

('帕伊西', 'Archbishop Paisi', '地拉那', '東正教（阿爾巴尼亞）', 2, 1948, 1966, '廢黜', '正統',
 'Albanian Orthodox Church records',
 '共產政府逐步管控宗教，最終於 1967 年宣布阿爾巴尼亞為無神論國家'),

('達米安', 'Archbishop Damian', '地拉那', '東正教（阿爾巴尼亞）', 3, 1966, 1973, '廢黜', '正統',
 'Albanian Orthodox Church records', '1967–1990 年教會被迫中斷，主教座懸缺近 20 年'),

('安納斯塔修斯·雅納拉托斯', 'Archbishop Anastasios (Yannoulatos)', '地拉那', '東正教（阿爾巴尼亞）', 4, 1992, 2025, '辭職', '正統',
 'Church records; Anastasios, Facing the World',
 '1991 年共產政府崩潰後，以希臘籍大主教身份重建阿爾巴尼亞教會；任期長達 33 年，成為阿爾巴尼亞公民；2025 年 3 月因健康原因辭職'),

('約亞尼', 'Archbishop Joani', '地拉那', '東正教（阿爾巴尼亞）', 5, 2025, NULL, NULL, '正統',
 'Albanian Orthodox Church Synod records', '現任大主教；2025 年當選');


-- ════════════════════════════════════════════════════════════
-- 五、捷克及斯洛伐克正教會
--     自主地位：1951（莫斯科）
--     see = '布拉格'，church = '東正教（捷克斯洛伐克）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('聖戈拉茲德·帕夫利克', 'Saint Gorazd (Pavlík)', '布拉格', '東正教（捷克斯洛伐克）', 1, 1921, 1942, '殉道', '正統',
 'Orthodox Church of Czech Lands records; Vasiliev, Bishop Gorazd',
 '波西米亞及摩拉維亞首任正教主教；1942 年協助藏匿刺殺納粹官員海德里希的傘兵，被捕後殉道。2012 年被列為新殉道者'),

('多羅修斯', 'Metropolitan Dorotheus', '布拉格', '東正教（捷克斯洛伐克）', 2, 1945, 1999, '自然死亡', '正統',
 'Church records', '獲 1951 年莫斯科自主地位 Tomos；任期橫跨共產主義時代'),

('尼古拉', 'Metropolitan Nicholas of Prešov', '布拉格', '東正教（捷克斯洛伐克）', 3, 1999, 2006, '自然死亡', '正統',
 'Church records', NULL),

('赫里斯托佛', 'Metropolitan Christopher of Prague', '布拉格', '東正教（捷克斯洛伐克）', 4, 2006, 2013, '辭職', '正統',
 'Church records', '因醜聞辭職'),

('拉斯提斯拉夫', 'Metropolitan Rastislav of Prešov', '布拉格', '東正教（捷克斯洛伐克）', 5, 2014, NULL, NULL, '正統',
 'Church records', '現任都主教');


-- ════════════════════════════════════════════════════════════
-- 六、美洲正教會（Orthodox Church in America, OCA）
--     源自 1794 年俄羅斯在阿拉斯加的傳教；1970 年莫斯科授予自主
--     see = '北美'，church = '東正教（美洲）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('約薩法·博羅托夫', 'Bishop Joasaph (Bolotov)', '北美', '東正教（美洲）', 1, 1799, 1799, '殉道', '俄羅斯東正教', '正統',
 'Barsukov, Life of Innocent Veniaminov',
 '首任北美主教，航行途中遇難，從未抵達教區'),

('依納爵·波德莫申斯基', 'Bishop Innocent (Podmosensky)', '北美', '東正教（美洲）', 2, 1804, 1840, '辭職', NULL, '正統',
 'OCA records', NULL),

('依諾肯提·韋尼亞米諾夫', 'Bishop Innocent (Veniaminov)', '北美', '東正教（美洲）', 3, 1840, 1868, '晉升', '俄羅斯東正教', '正統',
 'OCA records; Oleksa, Orthodox Alaska',
 '後升任莫斯科都主教（1868-1879）；翻譯聖經為阿留申語，是北美最重要的傳教士，已被封聖'),

('彼得·葉卡捷林諾夫斯基', 'Bishop Peter (Ekaterinovsky)', '北美', '東正教（美洲）', 4, 1859, 1866, '辭職', NULL, '正統',
 'OCA records', NULL),

('保羅·波波夫', 'Bishop Paul (Popov)', '北美', '東正教（美洲）', 5, 1866, 1870, '辭職', NULL, '正統',
 'OCA records', NULL),

('約翰·米特羅波爾斯基', 'Bishop John (Mitropolsky)', '北美', '東正教（美洲）', 6, 1870, 1877, '辭職', NULL, '正統',
 'OCA records', NULL),

('聶斯托爾·扎斯', 'Bishop Nestor (Zass)', '北美', '東正教（美洲）', 7, 1878, 1882, '辭職', NULL, '正統',
 'OCA records', NULL),

('弗拉基米爾·索科羅夫斯基', 'Bishop Vladimir (Sokolovsky-Avtonomov)', '北美', '東正教（美洲）', 8, 1887, 1891, '辭職', NULL, '正統',
 'OCA records', NULL),

('尼古拉·齊奧羅夫', 'Bishop Nicholas (Ziorov)', '北美', '東正教（美洲）', 9, 1891, 1898, '調任', NULL, '正統',
 'OCA records', NULL),

('提洪·別拉文', 'Archbishop Tikhon (Bellavin)', '北美', '東正教（美洲）', 10, 1898, 1907, '調任', NULL, '正統',
 'OCA records; Cunningham, A Vanquished Hope',
 '後升任莫斯科宗主教（1917-1925），任內反對共產主義；已被封聖'),

('普拉東·羅日傑斯特文斯基', 'Metropolitan Platon (Rozhdestvensky)', '北美', '東正教（美洲）', 11, 1907, 1934, '自然死亡', NULL, '正統',
 'OCA records', '因俄羅斯革命後的混亂，北美教會實際上在此期間高度自治'),

('泰奧菲盧斯·帕什科夫斯基', 'Metropolitan Theophilus (Pashkovsky)', '北美', '東正教（美洲）', 12, 1934, 1950, '辭職', NULL, '正統',
 'OCA records', NULL),

('列昂提·圖爾克維奇', 'Metropolitan Leonty (Turkevich)', '北美', '東正教（美洲）', 13, 1950, 1965, '自然死亡', NULL, '正統',
 'OCA records', NULL),

('依雷尼厄斯·貝基什', 'Metropolitan Irenaeus (Bekish)', '北美', '東正教（美洲）', 14, 1965, 1977, '辭職', NULL, '正統',
 'OCA records', NULL),

('泰奧多修斯·拉佐爾', 'Metropolitan Theodosius (Lazor)', '北美', '東正教（美洲）', 15, 1977, 2002, '辭職', NULL, '正統',
 'OCA records',
 '任內（1970年）正式獲得莫斯科自主地位 Tomos，完成教會正式獨立'),

('赫爾曼·斯韋科', 'Metropolitan Herman (Swaiko)', '北美', '東正教（美洲）', 16, 2002, 2008, '辭職', NULL, '正統',
 'OCA records', '因教會財務醜聞辭職'),

('約拿·帕夫豪森', 'Metropolitan Jonah (Paffhausen)', '北美', '東正教（美洲）', 17, 2008, 2012, '辭職', NULL, '正統',
 'OCA records', '因教會治理問題辭職'),

('提洪·莫拉德', 'Metropolitan Tikhon (Mollard)', '北美', '東正教（美洲）', 18, 2012, NULL, NULL, NULL, '正統',
 'OCA records', '現任都主教');


-- ════════════════════════════════════════════════════════════
-- 七、烏克蘭正教會（Orthodox Church of Ukraine, OCU）
--     自主地位：2019 年 1 月 6 日君士坦丁堡 Tomos
--     see = '基輔'，church = '東正教（烏克蘭）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('葉皮法尼·杜門科', 'Metropolitan Epifaniy (Serhii Petrovych Dumenko)', '基輔', '東正教（烏克蘭）', 1, 2019, NULL, NULL, '正統',
 'Ecumenical Patriarchate Tomos (2019-01-06)',
 '2018 年 12 月 15 日合一公會議選出；2019 年 1 月 6 日由普世宗主教巴爾多祿茂一世頒授 Tomos。現任首牧');


-- ════════════════════════════════════════════════════════════
-- 八、北馬其頓正教會（Macedonian Orthodox Church–Ohrid Archbishopric）
--     自主宣布：1967；塞爾維亞承認：2022
--     see = '奧赫里德'，church = '東正教（北馬其頓）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('多西修斯二世·斯托伊科維奇', 'Archbishop Dositheus II (Stojković)', '奧赫里德', '東正教（北馬其頓）', 1, 1967, 1981, '自然死亡', '正統',
 'Macedonian Orthodox Church records',
 '1967 年宣布從塞爾維亞正教會獨立；宣告獨立後長期不被任何教會承認'),

('安格拉里奧斯·克雷斯特斯基', 'Archbishop Angelarios (Krsteski)', '奧赫里德', '東正教（北馬其頓）', 2, 1981, 1986, '自然死亡', '正統',
 'Macedonian Orthodox Church records', NULL),

('加布里埃爾二世·米洛舍夫', 'Archbishop Gabriel II (Milošev)', '奧赫里德', '東正教（北馬其頓）', 3, 1986, 1993, '辭職', '正統',
 'Macedonian Orthodox Church records', NULL),

('米迦勒·戈戈夫', 'Archbishop Michael (Metodi Gogov)', '奧赫里德', '東正教（北馬其頓）', 4, 1993, 1999, '辭職', '正統',
 'Macedonian Orthodox Church records', NULL),

('斯蒂凡·維利亞諾夫斯基', 'Archbishop Stefan (Veljanovski)', '奧赫里德', '東正教（北馬其頓）', 5, 1999, NULL, NULL, '正統',
 'Macedonian Orthodox Church records; Serbian Orthodox Church recognition (2022)',
 '現任大主教；任內於 2022 年獲塞爾維亞及多個東正教會承認，結束 55 年的孤立狀態');


-- ════════════════════════════════════════════════════════════
-- 九、塞爾維亞東正教宗主教座
--     首任大主教：1219；首任宗主教：1346
--     see = '塞爾維亞'，church = '東正教（塞爾維亞）'
-- ════════════════════════════════════════════════════════════
-- 大主教時期（1219–1346）
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('聖薩瓦一世', 'Saint Sava I', '塞爾維亞', '東正教（塞爾維亞）', 1, 1219, 1233, '辭職', '君士坦丁堡普世宗主教', '正統',
 'Domentijan, Life of Saint Sava; Theodosius, Life of Saint Sava',
 '獲君士坦丁堡授予自主大主教地位；塞爾維亞教會之父，創立彼奇宗主教座，制定教會法規，已被封聖'),

('聖亞森尼一世', 'Saint Arsenije I', '塞爾維亞', '東正教（塞爾維亞）', 2, 1233, 1263, '辭職', NULL, '正統',
 'Serbian church chronicles', '薩瓦一世的學生；已被封聖'),

('薩瓦二世', 'Sava II', '塞爾維亞', '東正教（塞爾維亞）', 3, 1263, 1271, '辭職', NULL, '正統',
 'Serbian church chronicles', NULL),

('達尼洛一世', 'Danilo I', '塞爾維亞', '東正教（塞爾維亞）', 4, 1271, 1272, '辭職', NULL, '正統',
 'Serbian church chronicles', NULL),

('約阿尼基耶一世', 'Joanikije I', '塞爾維亞', '東正教（塞爾維亞）', 5, 1272, 1276, '自然死亡', NULL, '正統',
 'Serbian church chronicles', NULL),

('耶夫斯塔提耶一世', 'Jevstatije I', '塞爾維亞', '東正教（塞爾維亞）', 6, 1279, 1286, '辭職', NULL, '正統',
 'Serbian church chronicles', NULL),

('雅科夫', 'Jakov', '塞爾維亞', '東正教（塞爾維亞）', 7, 1286, 1292, '自然死亡', NULL, '正統',
 'Serbian church chronicles', NULL),

('耶夫斯塔提耶二世', 'Jevstatije II', '塞爾維亞', '東正教（塞爾維亞）', 8, 1292, 1309, '自然死亡', NULL, '正統',
 'Serbian church chronicles', NULL),

('薩瓦三世', 'Sava III', '塞爾維亞', '東正教（塞爾維亞）', 9, 1309, 1316, '辭職', NULL, '正統',
 'Serbian church chronicles', NULL),

('尼科季姆一世', 'Nikodim I', '塞爾維亞', '東正教（塞爾維亞）', 10, 1316, 1324, '自然死亡', NULL, '正統',
 'Serbian church chronicles', NULL),

('達尼洛二世', 'Danilo II', '塞爾維亞', '東正教（塞爾維亞）', 11, 1324, 1337, '自然死亡', NULL, '正統',
 'Serbian church chronicles; Danilo II, Lives of Serbian Kings and Archbishops',
 '重要史學家，著有《塞爾維亞列王與大主教傳記》'),

-- 宗主教時期（1346–1766，1557年起為恢復後的彼奇宗主教座）
('約阿尼基耶二世', 'Joanikije II', '塞爾維亞', '東正教（塞爾維亞）', 12, 1338, 1354, '自然死亡', NULL, '正統',
 'Serbian church chronicles',
 '1346 年被斯特凡·杜尚皇帝升格為宗主教，為塞爾維亞首任宗主教'),

('薩瓦四世', 'Sava IV', '塞爾維亞', '東正教（塞爾維亞）', 13, 1354, 1375, '辭職', NULL, '正統',
 'Serbian church chronicles', NULL),

-- 現代時期（1920年代至今）
('迪米特里耶', 'Patriarch Dimitrije', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1920, 1930, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records',
 '1920 年現代塞爾維亞東正教會統一後的第一任宗主教'),

('瓦爾納瓦', 'Patriarch Varnava', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1930, 1937, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records', '抵制南斯拉夫政府與梵蒂岡的協議，去世情況有爭議'),

('加夫里洛五世', 'Patriarch Gavrilo V', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1938, 1950, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records', '二戰期間被納粹關押於達豪集中營'),

('維肯提耶二世', 'Patriarch Vikentije II', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1950, 1958, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records', NULL),

('日爾曼', 'Patriarch German', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1958, 1990, '辭職', NULL, '正統',
 'Serbian Orthodox Church records', '任期長達 32 年，為塞爾維亞歷任宗主教中最長'),

('帕夫列', 'Patriarch Pavle', '塞爾維亞', '東正教（塞爾維亞）', NULL, 1990, 2009, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records',
 '以個人清廉和禁慾生活著稱；南斯拉夫解體期間多次呼籲和平'),

('依里聶伊', 'Patriarch Irinej', '塞爾維亞', '東正教（塞爾維亞）', NULL, 2010, 2020, '自然死亡', NULL, '正統',
 'Serbian Orthodox Church records', '2020 年死於新冠肺炎'),

('波爾菲里耶', 'Patriarch Porfirije', '塞爾維亞', '東正教（塞爾維亞）', NULL, 2021, NULL, NULL, NULL, '正統',
 'Serbian Orthodox Church records', '現任宗主教；2022 年承認北馬其頓教會自主地位');


-- ════════════════════════════════════════════════════════════
-- 十、保加利亞東正教宗主教座
--     首度建立：927/919；現代宗主教座恢復：1953
--     see = '索菲亞'，church = '東正教（保加利亞）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('達馬斯庫斯', 'Damsascus of Dorostol', '索菲亞', '東正教（保加利亞）', 1, 870, 877, '自然死亡', '君士坦丁堡普世宗主教', '正統',
 'Dvornik, The Slavs in European History',
 '870 年保加利亞第一帝國大公鮑里斯一世受洗後，君士坦丁堡設立保加利亞教會，此為首任大主教'),

('約瑟夫', 'Joseph', '索菲亞', '東正教（保加利亞）', NULL, 919, 927, '自然死亡', NULL, '正統',
 'Bulgarian church chronicles',
 '919 年宣布升格為宗主教；927 年君士坦丁堡正式承認'),

-- 現代宗主教（1953 年恢復）
('基里爾（康斯坦丁諾夫）', 'Patriarch Cyril (Konstantinov)', '索菲亞', '東正教（保加利亞）', NULL, 1953, 1971, '自然死亡', NULL, '正統',
 'Bulgarian Orthodox Church records',
 '1953 年宗主教座恢復後首任宗主教；在共產政府框架下維護教會運作'),

('馬克西姆', 'Patriarch Maxim', '索菲亞', '東正教（保加利亞）', NULL, 1971, 2012, '自然死亡', NULL, '正統',
 'Bulgarian Orthodox Church records',
 '任期長達 41 年；1992–1998 年間，部分主教另立對立宗主教比薩里昂（後和解）'),

('新腓特', 'Patriarch Neophyte', '索菲亞', '東正教（保加利亞）', NULL, 2013, 2024, '自然死亡', NULL, '正統',
 'Bulgarian Orthodox Church records', NULL),

('達尼伊爾', 'Patriarch Daniil', '索菲亞', '東正教（保加利亞）', NULL, 2024, NULL, NULL, NULL, '正統',
 'Bulgarian Orthodox Church Synod records', '現任宗主教；2024 年 7 月當選');


-- ════════════════════════════════════════════════════════════
-- 十一、格魯吉亞東正教宗主教座
--       自主地位：約 466 年；恢復：1917
--       see = '第比利斯'，church = '東正教（格魯吉亞）'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('彼得一世', 'Catholicos Peter I', '第比利斯', '東正教（格魯吉亞）', 1, 466, 491, '自然死亡', '安提阿宗主教', '正統',
 'Georgian church chronicles; Metreveli, History of the Georgian Church',
 '格魯吉亞教會脫離安提阿管轄獲得自主後的首位公教主教'),

('梅爾基塞德克一世', 'Catholicos-Patriarch Melkisedek I', '第比利斯', '東正教（格魯吉亞）', NULL, 1010, 1033, '自然死亡', NULL, '正統',
 'Georgian church chronicles',
 '首位同時持有「公教主教兼宗主教」雙銜者，格魯吉亞教會最高職位制度確立'),

('基里昂二世·薩扎格利什維利', 'Catholicos-Patriarch Kyrion II', '第比利斯', '東正教（格魯吉亞）', NULL, 1917, 1918, '殉道', NULL, '正統',
 'Georgian church records',
 '1917 年俄羅斯革命後宣布恢復自主地位的首任公教主教兼宗主教；翌年神秘死亡'),

('里奧尼德', 'Catholicos-Patriarch Leonid', '第比利斯', '東正教（格魯吉亞）', NULL, 1918, 1921, '廢黜', NULL, '正統',
 'Georgian church records', '蘇聯入侵格魯吉亞（1921）後被廢黜'),

('安布羅西', 'Catholicos-Patriarch Ambrose', '第比利斯', '東正教（格魯吉亞）', NULL, 1921, 1927, '自然死亡', NULL, '正統',
 'Georgian church records',
 '1922 年致函熱那亞會議抗議蘇聯占領，遭蘇聯當局審判入獄'),

('克里斯托佛三世', 'Catholicos-Patriarch Christopher III', '第比利斯', '東正教（格魯吉亞）', NULL, 1927, 1932, '自然死亡', NULL, '正統',
 'Georgian church records', NULL),

('卡利斯特拉圖斯', 'Catholicos-Patriarch Kalistrat', '第比利斯', '東正教（格魯吉亞）', NULL, 1932, 1952, '自然死亡', NULL, '正統',
 'Georgian church records', '蘇聯統治最嚴酷時期在位'),

('梅爾基塞德克三世', 'Catholicos-Patriarch Melkisedek III', '第比利斯', '東正教（格魯吉亞）', NULL, 1952, 1960, '自然死亡', NULL, '正統',
 'Georgian church records', NULL),

('葉弗雷姆二世', 'Catholicos-Patriarch Ephraim II', '第比利斯', '東正教（格魯吉亞）', NULL, 1960, 1972, '自然死亡', NULL, '正統',
 'Georgian church records', NULL),

('大衛五世', 'Catholicos-Patriarch David V', '第比利斯', '東正教（格魯吉亞）', NULL, 1972, 1977, '自然死亡', NULL, '正統',
 'Georgian church records', NULL),

('伊利亞二世', 'Catholicos-Patriarch Ilia II', '第比利斯', '東正教（格魯吉亞）', NULL, 1977, 2026, '自然死亡', NULL, '正統',
 'Georgian church records; Parsons, Georgia: A Political History',
 '任期長達 49 年，為格魯吉亞歷任最長；見證蘇聯解體、獨立建國、南奧塞梯戰爭；2026 年 3 月 17 日辭世，享年 91 歲');
