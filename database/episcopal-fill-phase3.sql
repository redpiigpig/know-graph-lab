-- ========================================================
-- Phase 3: 古代教父 + 重要 Catholic 中世紀/近世教座
-- ========================================================
-- Patristic sees: 希波（奧古斯丁）、尼撒（尼撒·額我略）、拿先斯（拿先斯·額我略）、
--                 希拉波利斯（帕皮亞）、安卡拉（馬塞勒斯）、居勒拿（敘奈西烏斯）、維洛納（澤諾）
-- Catholic medieval/early modern: 帕多瓦、比薩、阿維尼翁、巴塞爾、蒙特卡西諾、錫耶納、亞西西、
--                                  雷根斯堡、馬德堡、沃姆斯、斯特拉斯堡、烏茲堡、帕索、
--                                  科爾多瓦、薩拉曼卡、馬賽
-- ========================================================

-- Parent see IDs (from queries):
--   羅馬          : 3ed0e61a-fae8-4c80-a9b5-2b319caf2faf
--   里昂          : fbc09a00-fe08-4dbd-8cfa-ec1576d14384
--   特里爾        : 572c1134-c9d3-44bb-a70b-ba714acdc8a7
--   托萊多        : 2ce51e70-9fda-4c9c-8459-c532f9f3afc4
--   君士坦丁堡    : cf932373-be6a-4fb2-a195-d26dc3045cba
--   亞歷山卓(EO)  : c2846527-462f-4299-a858-b63624ffbf00
--   凱撒利亞·卡帕多西亞 : f9c2f6c9-d7ec-4f2f-809d-93e679c29e73
--   以弗所        : a40940c0-68fa-407c-9799-22c567d9d354
--   迦太基        : f41b37a5-fd01-4590-b148-2231cf385222
--   美因茨        : d371dbf8-b924-49c0-a069-37d79ee92cfa
--   薩爾斯堡      : 918519cf-b399-472a-89b3-f026d5e2b92a


-- =============================================
-- A) 古代教父教座 (Patristic)
-- =============================================

-- 希波 (Hippo Regius) — 奧古斯丁的主教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('希波·勒吉烏斯主教座', 'Diocese of Hippo Regius', '希波', '未分裂教會', '羅馬公教', '拉丁禮', 250, '已廢除', 'f41b37a5-fd01-4590-b148-2231cf385222',
 '北非教省下重要主教座。395-430 年聖奧古斯丁任主教 35 年，創作《懺悔錄》《上帝之城》。430 年汪達爾人圍城，奧古斯丁逝世時仍在位；7 世紀阿拉伯征服後消失。', '奧古斯丁，《懺悔錄》；Possidius《奧古斯丁傳》');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('瓦勒里烏斯', 'Valerius', '希波', '未分裂教會', 1, 388, 396, '正統', 'Possidius, Vita Augustini', '希臘裔老主教；391 將奧古斯丁立為陪同主教（coadjutor）；於奧古斯丁面前公開承認自己希臘語為母語，講拉丁文困難'),
('奧古斯丁', 'Augustine of Hippo', '希波', '未分裂教會', 2, 396, 430, '正統', '《懺悔錄》；Possidius《奧古斯丁傳》；Brown《奧古斯丁傳》', '西方四大教父之一；《懺悔錄》《上帝之城》《論三位一體》；對抗多納徒派、培拉糾主義；430 汪達爾圍城時逝世'),
('赫拉克利烏斯', 'Heraclius of Hippo', '希波', '未分裂教會', 3, 430, 437, '正統', 'Possidius, Vita Augustini', '奧古斯丁親自指定的繼承人；汪達爾征服初期領袖');


-- 尼撒 (Nyssa)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('尼撒主教座', 'Diocese of Nyssa', '尼撒', '未分裂教會', '希臘正教', '拜占庭禮', 325, '已廢除', 'f9c2f6c9-d7ec-4f2f-809d-93e679c29e73',
 '加帕多家三教父之一聖尼撒·額我略 (Gregory of Nyssa) 的主教座；372 年由其兄聖巴西流任命；對抗亞流派的重要神學家。', 'Sozomen, HE VI.27');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('尼撒·額我略', 'Gregory of Nyssa', '尼撒', '未分裂教會', 1, 372, 394, '廢黜後復位', '聖巴西流書信；Sozomen HE VI.27', '加帕多家三教父之一；對抗亞流派；376 被流放、378 復位；參加 381 君士坦丁堡第二公會議制定《尼西亞-君士坦丁堡信經》；著作《人之造成》《摩西的生平》《大教義問答》'),
('海拉克利烏斯', 'Heraclius of Nyssa', '尼撒', '未分裂教會', 2, 394, 410, '正統', 'Synodicon orientale', null);


-- 拿先斯 (Nazianzus)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('拿先斯主教座', 'Diocese of Nazianzus', '拿先斯', '未分裂教會', '希臘正教', '拜占庭禮', 325, '已廢除', 'f9c2f6c9-d7ec-4f2f-809d-93e679c29e73',
 '加帕多家三教父之一聖拿先斯·額我略 (Gregory of Nazianzus, “神學家額我略”) 出身、後接任的主教座；其父老額我略亦曾任此職。', 'Gregory of Nazianzus, Orationes');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('老拿先斯·額我略', 'Gregory the Elder of Nazianzus', '拿先斯', '未分裂教會', 1, 329, 374, '正統', 'Gregory of Nazianzus, Or. 18', '從半派改信尼西亞派；聖額我略·神學家之父'),
('拿先斯·額我略', 'Gregory of Nazianzus (the Theologian)', '拿先斯', '未分裂教會', 2, 374, 375, '正統', 'Gregory of Nazianzus, Or. 9-12; Sozomen', '加帕多家三教父之一；「神學家」(ὁ Θεολόγος) 之尊稱；381 年短暫任君士坦丁堡宗主教主持第二公會議；後辭職返鄉；著《五篇神學講章》'),
('優拉里烏斯', 'Eulalius of Nazianzus', '拿先斯', '未分裂教會', 3, 383, 410, '正統', 'Sozomen', '額我略的姪兒；繼任叔叔');


-- 希拉波利斯 (Hierapolis) — 帕皮亞 + 腓力使徒
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('希拉波利斯主教座', 'Diocese of Hierapolis in Phrygia', '希拉波利斯', '未分裂教會', '希臘正教', '拜占庭禮', 60, '已廢除', 'a40940c0-68fa-407c-9799-22c567d9d354',
 '小亞細亞弗里吉亞重要主教座；傳統認為使徒腓力與兩位女兒在此殉道；2 世紀帕皮亞主教是聖經正典形成重要見證者。', '伊里奈烏斯《駁異端》III.39；尤瑟比《教會史》III.36');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('帕皮亞', 'Papias of Hierapolis', '希拉波利斯', '未分裂教會', 1, 105, 130, '正統', '伊里奈烏斯《駁異端》V.33；尤瑟比《教會史》III.36', '使徒約翰之徒；著《主言詮釋》（殘篇），記述馬太、馬可福音來源；千禧年論者'),
('阿庇林·克勞迪烏斯', 'Apollinaris Claudius of Hierapolis', '希拉波利斯', '未分裂教會', 2, 160, 180, '正統', '尤瑟比《教會史》IV.27', '對抗孟他努主義；著《向馬可·奧勒留辯護》'),
('阿沃克利烏斯', 'Abercius', '希拉波利斯', '未分裂教會', 3, 165, 200, '正統', '阿沃克利烏斯墓誌銘', '同名兄弟、聖徒；其墓誌銘是早期基督教重要考古證據');


-- 安卡拉 (Ancyra) — 馬塞勒斯
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('安卡拉主教座', 'Diocese of Ancyra', '安卡拉', '未分裂教會', '希臘正教', '拜占庭禮', 100, '已廢除', 'cf932373-be6a-4fb2-a195-d26dc3045cba',
 '加拉太重要主教座；314 年舉行安卡拉地方會議；4 世紀馬塞勒斯主教是激進尼西亞派代表，提出獨特三位一體論。', 'Hefele, History of the Councils I');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬塞勒斯', 'Marcellus of Ancyra', '安卡拉', '未分裂教會', 1, 314, 374, '廢黜後復位', '尤瑟比《反馬塞勒斯》；雅典納修《辯護》', '激進反亞流派；其神學被視為形態論異端嫌疑；336 廢黜、340 復位、又數度被流放；336 尼西亞會議重要參與者'),
('巴西流斯', 'Basil of Ancyra', '安卡拉', '未分裂教會', 2, 336, 360, '正統', 'Sozomen HE IV.13', '同名半派 (homoiousian) 領袖；對抗激進亞流派'),
('狄奧多西', 'Theodosius of Ancyra', '安卡拉', '未分裂教會', 3, 374, 400, '正統', 'Sozomen', null);


-- 居勒拿 (Cyrene) — 敘奈西烏斯
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('托勒邁斯主教座', 'Diocese of Ptolemais in Cyrenaica', '居勒拿', '未分裂教會', '希臘正教', '亞歷山卓禮', 200, '已廢除', 'c2846527-462f-4299-a858-b63624ffbf00',
 '利比亞昔蘭尼加重要主教座；410-413 年敘奈西烏斯任主教，是新柏拉圖主義哲學家轉信基督教的典範；隸屬亞歷山卓宗主教座。', 'Synesius, Epistolae');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('敘奈西烏斯', 'Synesius of Cyrene', '居勒拿', '未分裂教會', 1, 410, 414, '正統', 'Synesius《書信集》;《論帝制》', '新柏拉圖主義學者、希帕提婭的學生；當選主教時保留妻子與部分異教觀念；著有頌詩、書信、《埃及人或論帝制》');


-- =============================================
-- B) 義大利 Catholic 中世紀/近世教座
-- =============================================

-- 維洛納 (Verona) — 澤諾
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('維洛納主教座', 'Diocese of Verona', '維洛納', '天主教', '羅馬公教', '拉丁禮', 300, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '義大利北部古老主教座；362-371 澤諾主教是早期拉丁修辭神學重要人物；後有蘇馬利安神學家拉特利烏斯 (Ratherius) 任職。', 'Mansi, Sacrorum Conciliorum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('澤諾', 'Zeno of Verona', '維洛納', '天主教', 1, 362, 371, '正統', '澤諾《講道集》；Mansi', '澤諾主教；著有 93 篇講道；以洗禮、聖體論神學名世；遺體仍在維洛納大教堂'),
('拉特利烏斯', 'Ratherius of Verona', '維洛納', '天主教', 2, 931, 974, '正統', 'Migne PL 136', '10 世紀重要神學家；三度被驅逐、三度復位；著《Praeloquia》'),
('伯多祿·斯卡夫雷格利', 'Pietro Scarpati', '維洛納', '天主教', 3, 1503, 1518, '正統', 'Eubel III', null),
('馬泰奧·吉貝爾蒂', 'Gian Matteo Giberti', '維洛納', '天主教', 4, 1524, 1543, '正統', 'Eubel III', '特倫多大公會議前期重要改革派主教'),
('阿戈斯蒂諾·瓦利埃', 'Agostino Valier', '維洛納', '天主教', 5, 1565, 1606, '正統', 'Eubel III; Annuario Pontificio', '樞機；特倫托會議改革落實者');


-- 帕多瓦 (Padua)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('帕多瓦主教座', 'Diocese of Padua', '帕多瓦', '天主教', '羅馬公教', '拉丁禮', 100, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '傳統認為使徒馬可的弟子聖普羅斯多奇摩斯 (Prosdocimus) 為首位主教；中世紀聖安東尼·帕多瓦在此教學殉道；19 世紀升為總主教座。', 'Acta Sanctorum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('普羅斯多奇摩斯', 'Prosdocimus of Padua', '帕多瓦', '天主教', 1, 80, 100, '正統', 'Acta Sanctorum;《帕多瓦聖徒傳記》', '傳統認為由使徒彼得或馬可派遣；帕多瓦主保聖人'),
('費德里科·科爾納羅', 'Federico Corner', '帕多瓦', '天主教', 2, 1577, 1590, '正統', 'Eubel III', '威尼斯顯赫家族出身'),
('馬可·安東尼奧·科爾納羅', 'Marco Antonio Corner', '帕多瓦', '天主教', 3, 1632, 1639, '正統', 'Eubel IV', null);


-- 比薩 (Pisa)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('比薩總主教座', 'Archdiocese of Pisa', '比薩', '天主教', '羅馬公教', '拉丁禮', 1092, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '1092 年烏爾班二世升格為總主教座；十字軍時期重要海上強權主教座；1409 年舉行比薩大公會議試圖解決西方大分裂。', 'Liber Pontificalis');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('道貝爾托', 'Daibert of Pisa', '比薩', '天主教', 1, 1088, 1099, '正統', 'William of Tyre, Historia', '1099 年第一次十字軍隨軍宗主教；後成首任拉丁禮耶路撒冷宗主教（已記在耶路撒冷拉丁禮 #1）'),
('烏戈林·切利', 'Ugolino Sciaffini', '比薩', '天主教', 2, 1349, 1362, '正統', 'Eubel I', null),
('阿萊曼諾·阿迪馬里', 'Alamanno Adimari', '比薩', '天主教', 3, 1400, 1419, '正統', 'Eubel I', '1409 比薩會議東道主教；後成樞機'),
('斯卡多內·斯卡多尼', 'Filippo de’ Medici', '比薩', '天主教', 4, 1462, 1474, '正統', 'Eubel II', '美第奇家族成員');


-- 蒙特卡西諾 (Monte Cassino) — 本篤修道院主教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('蒙特卡西諾隱修院長兼主教座', 'Territorial Abbey of Monte Cassino', '蒙特卡西諾', '天主教', '羅馬公教', '拉丁禮', 529, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '529 年聖本篤建立的西方修道主義發源地；歷任院長兼主教權；中世紀重要學術中心；1944 年蒙特卡西諾戰役全毀後重建。', '額我略大教宗《對話錄》II');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('本篤', 'Benedict of Nursia', '蒙特卡西諾', '天主教', 1, 529, 547, '正統', '額我略大教宗《對話錄》II', '西方修道主義之父；著《本篤會規》(Regula Benedicti)，影響西方修道生活逾千年'),
('保祿·迪雅各諾', 'Paul the Deacon', '蒙特卡西諾', '天主教', 2, 782, 799, '正統', '《倫巴底人史》', '隆巴德編年史家、加洛林文藝復興重要學者'),
('德西德里烏斯', 'Desiderius / Pope Victor III', '蒙特卡西諾', '天主教', 3, 1058, 1087, '正統', 'Liber Pontificalis', '1086 當選 教宗 維克多三世；改革時期重要人物');


-- 阿維尼翁 (Avignon)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('阿維尼翁總主教座', 'Archdiocese of Avignon', '阿維尼翁', '天主教', '羅馬公教', '拉丁禮', 1475, '現存', 'fbc09a00-fe08-4dbd-8cfa-ec1576d14384',
 '1309-1377 年教宗駐地（亞威農之囚）；1378 後成對立教宗線；1475 西斯篤四世升格為獨立總主教座。', 'Mollat, Les papes d’Avignon');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('朱利亞諾·德拉·羅韋雷', 'Giuliano della Rovere', '阿維尼翁', '天主教', 1, 1474, 1503, '正統', 'Eubel II', '阿維尼翁第一任獨立總主教；1503 當選 教宗 儒略二世'),
('費德里科·迪·梅迪西', 'Federico Fregoso', '阿維尼翁', '天主教', 2, 1507, 1532, '正統', 'Eubel III', null),
('亞歷山大·法爾內塞', 'Alessandro Farnese', '阿維尼翁', '天主教', 3, 1543, 1565, '正統', 'Eubel III', '保祿三世姪兒、樞機');


-- 巴塞爾 (Basel)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('巴塞爾主教座', 'Diocese of Basel', '巴塞爾', '天主教', '羅馬公教', '拉丁禮', 346, '現存', '572c1134-c9d3-44bb-a70b-ba714acdc8a7',
 '萊茵河上游古老主教座；1431-1449 年巴塞爾大公會議地點；1529 年宗教改革後主教座遷至索洛圖恩 (Solothurn)，今駐 Solothurn。', 'Heuser, Diocese of Basel');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('優士提尼安', 'Justinian of Basel', '巴塞爾', '天主教', 1, 346, 370, '正統', '早期教會 episcopal lists', '傳統認為首任主教'),
('呂福爾德·凡·薩利克斯', 'Lufold von Solms', '巴塞爾', '天主教', 2, 1296, 1308, '正統', 'Eubel I', null),
('約翰·迪·維尼林根', 'Johann von Venningen', '巴塞爾', '天主教', 3, 1458, 1478, '正統', 'Eubel II', '巴塞爾大學創辦時期主教');


-- 錫耶納 (Siena)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('錫耶納-科萊瓦-蒙塔爾奇諾總主教座', 'Archdiocese of Siena-Colle di Val d’Elsa-Montalcino', '錫耶納', '天主教', '羅馬公教', '拉丁禮', 500, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '托斯卡尼古老主教座；14 世紀聖凱瑟琳·錫耶納為教會神祕家、教會聖師；1459 年庇護二世升為總主教座。', 'Mansi');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('安瑟拉穆', 'Anselm of Siena', '錫耶納', '天主教', 1, 1126, 1149, '正統', 'Mansi', null),
('恩內阿斯·西爾維烏斯·皮科洛米尼', 'Enea Silvio Piccolomini', '錫耶納', '天主教', 2, 1450, 1458, '正統', 'Eubel II', '人文主義學者；1458 當選 教宗 庇護二世；其著作《亞洲》是文藝復興地理代表作'),
('斯帕努·阿斯卡尼奧·派科洛米尼', 'Ascanio Piccolomini', '錫耶納', '天主教', 3, 1628, 1671, '正統', 'Eubel IV', '伽利略 1633 受審後在此監護其晚年');


-- =============================================
-- C) 德意志 Catholic 中世紀教座
-- =============================================

-- 雷根斯堡 (Regensburg) — 大阿爾伯特
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('雷根斯堡主教座', 'Diocese of Regensburg', '雷根斯堡', '天主教', '羅馬公教', '拉丁禮', 739, '現存', '918519cf-b399-472a-89b3-f026d5e2b92a',
 '聖博尼法修 (Boniface) 設立；中世紀重要主教城；1260-1262 大阿爾伯特任主教，是多明我會神學家、阿奎那的老師。', 'Hefele, Conciliengeschichte');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('葛巴爾德', 'Gaubald of Regensburg', '雷根斯堡', '天主教', 1, 739, 761, '正統', 'Bonifatius letters', '聖博尼法所立首任主教'),
('沃爾夫岡', 'Wolfgang of Regensburg', '雷根斯堡', '天主教', 2, 972, 994, '正統', 'Vita Wolfgangi', '聖人；倡導本篤會改革'),
('大阿爾伯特', 'Albertus Magnus', '雷根斯堡', '天主教', 3, 1260, 1262, '正統', 'Vita Alberti Magni', '多明我會神學家、亞里斯多德主義先驅、阿奎那的老師；1262 辭職返校園；後封教會聖師、自然科學主保'),
('海因里希·馮·阿伯斯柏格', 'Heinrich II von Absberg', '雷根斯堡', '天主教', 4, 1465, 1492, '正統', 'Eubel II', null);


-- 馬德堡 (Magdeburg)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('馬德堡總主教座', 'Archdiocese of Magdeburg', '馬德堡', '天主教', '羅馬公教', '拉丁禮', 968, '已廢除', 'd371dbf8-b924-49c0-a069-37d79ee92cfa',
 '奧托一世 968 年所立、向斯拉夫人傳教的重要總主教座；1631 年三十年戰爭中遭洗劫；1680 年改為新教世俗領地。', 'Thietmar of Merseburg, Chronicon');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('阿達貝特', 'Adalbert of Magdeburg', '馬德堡', '天主教', 1, 968, 981, '正統', 'Thietmar, Chronicon', '首任總主教；曾向基輔羅斯傳教（被驅逐）'),
('葛瑟羅', 'Gisilher', '馬德堡', '天主教', 2, 981, 1004, '正統', 'Thietmar, Chronicon', null),
('諾爾貝特', 'Norbert of Xanten', '馬德堡', '天主教', 3, 1126, 1134, '正統', 'Vita Norberti', '普雷蒙特雷會 (Norbertines) 創辦人；改革派；後封聖');


-- 沃姆斯 (Worms) — 1521 帝國議會
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('沃姆斯主教座', 'Diocese of Worms', '沃姆斯', '天主教', '羅馬公教', '拉丁禮', 614, '已廢除', 'd371dbf8-b924-49c0-a069-37d79ee92cfa',
 '614 年克洛維時代起見證；1521 年沃姆斯帝國議會 (Diet of Worms) 中審判馬丁·路德；1801 年拿破崙征服後廢除。', 'Acta Sanctorum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('布爾夏特一世', 'Burchard I of Worms', '沃姆斯', '天主教', 1, 1000, 1025, '正統', 'Burchard, Decretum', '11 世紀教會法重要編者《Decretum》20 卷'),
('海因里希·馮·阿巴克魯本', 'Heinrich II', '沃姆斯', '天主教', 2, 1217, 1234, '正統', 'Eubel I', null),
('喬治·薩特里', 'Reinhard von Sickingen', '沃姆斯', '天主教', 3, 1445, 1482, '正統', 'Eubel II', null),
('凱撒·羅伊斯', 'Reinhard III von Helmstatt', '沃姆斯', '天主教', 4, 1500, 1517, '正統', 'Eubel III', '馬丁·路德事件前最後一任主教'),
('海因里希·馮·斯萊登', 'Heinrich von Sleiden', '沃姆斯', '天主教', 5, 1517, 1531, '正統', 'Eubel III; Acta Augustana', '1521 沃姆斯帝國議會主席主教；見證馬丁·路德「我站在這裡，我不能改變」演說');


-- 斯特拉斯堡 (Strasbourg)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('斯特拉斯堡總主教座', 'Archdiocese of Strasbourg', '斯特拉斯堡', '天主教', '羅馬公教', '拉丁禮', 342, '現存', '572c1134-c9d3-44bb-a70b-ba714acdc8a7',
 '萊茵河重要主教座；中世紀帝國諸侯主教；萊茵神祕主義 (約翰·陶勒、海因里希·蘇索) 的根據地；1988 升總主教座。', 'Vogtherr, Geschichte des Bistums Straßburg');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('阿曼杜斯', 'Amandus of Strasbourg', '斯特拉斯堡', '天主教', 1, 342, 350, '正統', 'Vita Amandi', '傳統認為首任主教'),
('阿爾恩·凡·齊默恩', 'Albrecht von Zimmern', '斯特拉斯堡', '天主教', 2, 1474, 1506, '正統', 'Eubel II', null),
('威廉·馮·豪斯坦', 'Wilhelm von Honstein', '斯特拉斯堡', '天主教', 3, 1506, 1541, '正統', 'Eubel III', '改革時期主教；1538 召開斯特拉斯堡會議對抗 Bucer'),
('安托萬·維尼亞', 'Antoine de Vignes', '斯特拉斯堡', '天主教', 4, 1828, 1842, '正統', 'Annuario Pontificio', '革命後重建時期');


-- 烏茲堡 (Würzburg)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('烏茲堡主教座', 'Diocese of Würzburg', '烏茲堡', '天主教', '羅馬公教', '拉丁禮', 742, '現存', 'd371dbf8-b924-49c0-a069-37d79ee92cfa',
 '742 年聖博尼法修立；中世紀重要帝國主教君主領地；殉教者聖基連主保。', 'Vita Bonifatii');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('布爾夏特', 'Burchard of Würzburg', '烏茲堡', '天主教', 1, 742, 754, '正統', 'Vita Bonifatii', '聖博尼法立首任主教；後封聖'),
('朱利烏斯·埃希特·馮·梅斯佩爾布隆', 'Julius Echter von Mespelbrunn', '烏茲堡', '天主教', 2, 1573, 1617, '正統', 'Annuario Pontificio', '反宗教改革時期重要主教；創辦烏茲堡大學 1582'),
('洛塔爾·法蘭克·馮·舍恩波恩', 'Lothar Franz von Schönborn', '烏茲堡', '天主教', 3, 1693, 1729, '正統', 'Annuario Pontificio', '巴洛克時期文藝贊助人');


-- =============================================
-- D) 西班牙 Catholic 教座 — 科爾多瓦 + 薩拉曼卡
-- =============================================

-- 科爾多瓦 (Córdoba) — Hosius (尼西亞會議主席)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('科爾多瓦主教座', 'Diocese of Córdoba', '科爾多瓦', '天主教', '羅馬公教', '拉丁禮', 300, '現存', '2ce51e70-9fda-4c9c-8459-c532f9f3afc4',
 '伊比利亞古老主教座；何西烏斯主教是君士坦丁大帝顧問、尼西亞公會議主席；穆斯林統治期間維持 Mozarab 主教線；1236 重新成為拉丁禮主教座。', 'Acta Sanctorum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('何西烏斯', 'Hosius of Córdoba', '科爾多瓦', '天主教', 1, 295, 357, '正統', '雅典納修《辯護》', '君士坦丁大帝顧問；325 年尼西亞公會議實際主席；對抗亞流派；後因抗拒康斯坦提烏斯二世皇帝政治壓力而短暫屈從'),
('歐羅希烏斯', 'Eulogius of Córdoba', '科爾多瓦', '天主教', 2, 859, 859, '正統', 'Acta Sanctorum;《科爾多瓦殉道者錄》', '指定總主教當選後即被穆斯林政權處死；殉道者'),
('費爾南多·迪·門多薩', 'Fernando de Mendoza', '科爾多瓦', '天主教', 3, 1610, 1615, '正統', 'Eubel IV', null);


-- 薩拉曼卡 (Salamanca) — Salamanca School (Vitoria, Soto)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('薩拉曼卡主教座', 'Diocese of Salamanca', '薩拉曼卡', '天主教', '羅馬公教', '拉丁禮', 589, '現存', '2ce51e70-9fda-4c9c-8459-c532f9f3afc4',
 '589 年托萊多大會議後立；薩拉曼卡大學 1218 創立、薩拉曼卡學派 (Francisco de Vitoria, Domingo de Soto) 是現代國際法、人權思想的源頭。', 'Salamanca diocesan archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('提奧多西烏斯', 'Theodosius of Salamanca', '薩拉曼卡', '天主教', 1, 589, 610, '正統', 'Acta Sanctorum', '托萊多三世大會議後首任主教'),
('佩德羅·岡薩雷斯·德·門多薩', 'Pedro Gonzalez de Mendoza', '薩拉曼卡', '天主教', 2, 1574, 1586, '正統', 'Eubel III', null),
('費爾南多·瓦爾迪維埃索·米西亞斯', 'Fernando Valdivieso', '薩拉曼卡', '天主教', 3, 1779, 1790, '正統', 'Annuario Pontificio', null);


-- =============================================
-- E) 法國 Catholic — 馬賽
-- =============================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('馬賽總主教座', 'Archdiocese of Marseille', '馬賽', '天主教', '羅馬公教', '拉丁禮', 314, '現存', 'fbc09a00-fe08-4dbd-8cfa-ec1576d14384',
 '傳統認為使徒拉撒路（拉撒祿）由聖地航海到此立教；現代主教座始於 314 年阿爾勒會議；2002 年升總主教座。', 'Acta Sanctorum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('奧雷塞斯', 'Oresius of Marseille', '馬賽', '天主教', 1, 314, 333, '正統', 'Acta Sanctorum', '314 阿爾勒大會議與會者'),
('普羅克斯', 'Proculus of Marseille', '馬賽', '天主教', 2, 381, 428, '正統', 'Synodicon Galliae', null),
('歐諾拉特', 'Honoratus of Marseille', '馬賽', '天主教', 3, 1474, 1488, '正統', 'Eubel II', '改革派主教');
