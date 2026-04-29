-- ============================================================
-- 天主教大主教傳承——義大利補充（都靈、熱那亞、巴勒摩、拉文納）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 都靈（Turin）
-- 薩伏依王朝首都；聖殮布（Sindone）所在地
-- ==============================
('聖馬克西穆斯', 'Saint Maximus of Turin', '都靈', '天主教', 6, 390, 423, '逝世', '教宗達瑪索一世', '正統', 'Catholic Hierarchy; CCL 23', '早期教會最偉大的講道者之一；《佈道集》（Sermones）保存150篇；對巫術迷信的批評；北義大利基督化的重要推手'),
('阿達爾·克雷莫納', 'Claudio of Turin', '都靈', '天主教', 24, 820, 830, '逝世', '虔誠者路易', '爭議', 'MGH; Dümmler', '西班牙裔主教；以像破壞主義（iconoclasm）著稱——拆除教堂中的圖像；受阿戈巴爾德影響；不被羅馬承認的改革傾向'),
('蘭多爾福', 'Landulf I of Turin', '都靈', '天主教', 36, 1000, 1037, '逝世', '鄂圖三世', '正統', 'MGH', '都靈主教區確立於薩伏依邊區；神聖羅馬帝國的意大利控制'),
('喬萬尼·維森佐·拉維奇諾', 'Michele Beggiamo', '都靈', '天主教', 57, 1515, 1522, '逝世', '教宗利奧十世', '正統', 'Catholic Hierarchy', '都靈升格為大主教區（1515年）；薩伏依公國的政治庇護'),
('吉羅拉莫·德拉·羅維雷', 'Girolamo Della Rovere', '都靈', '天主教', 58, 1564, 1592, '逝世', '教宗庇護四世', '正統', 'Catholic Hierarchy', '樞機；特倫托後改革推動者；薩伏依公爵的宗教顧問'),
('卡洛·阿戈斯蒂諾·法維亞-薩沃利', 'Michele Beggiamo', '都靈', '天主教', 65, 1643, 1657, '逝世', '教宗烏爾班八世', '正統', 'Catholic Hierarchy', '薩伏依攝政王太后克里斯汀娜（路易十三之妹）時代；法國-薩伏依政治影響下的都靈'),
('維托里奧·科托·保·德席爾瓦', 'Vittorio Gaetano Costa', '都靈', '天主教', 76, 1946, 1967, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '二戰後都靈的天主教重建；聖殮布1946年後的保管'),
('米凱萊·佩列格里諾', 'Michele Pellegrino', '都靈', '天主教', 77, 1965, 1977, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；梵二後改革；工人牧養（汽車工業工人）；勞工運動關懷'),
('安娜斯塔西奧·巴列斯特雷羅', 'Anastasio Ballestrero', '都靈', '天主教', 78, 1977, 1989, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；1978年聖殮布首次科學研究；1988年碳14定年（13–14世紀，引發爭議）；嘉布遣方濟各會士'),
('喬萬尼·薩爾達里尼', 'Giovanni Saldarini', '都靈', '天主教', 79, 1989, 1999, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；聖殮布1998年展示（若望保祿二世親訪）'),
('塞韋里諾·波萊托', 'Severino Poletto', '都靈', '天主教', 80, 1999, 2010, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；2010年聖殮布展示（本篤十六世親訪）'),
('切薩雷·諾薩利亞', 'Cesare Nosiglia', '都靈', '天主教', 81, 2010, 2022, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '2015年及2022年聖殮布展示（方濟각親訪2015）'),
('羅貝爾托·雷波萊', 'Roberto Repole', '都靈', '天主教', 82, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '神學家；杜蘭-雷根斯堡大學背景；現任大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '都靈' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 熱那亞（Genoa）
-- 義大利最重要的港口；多位教宗候選人出自此地
-- ==============================
('聖敘魯斯', 'Saint Syrus of Genoa', '熱那亞', '天主教', 1, 250, 280, '逝世', '使徒傳承', '正統', 'Catholic Hierarchy', '熱那亞首任主教（傳統說法）；實際歷史記錄始於4世紀'),
('錫尼巴爾多·菲耶斯基（後為英諾森四世）', 'Sinibaldo Fieschi (later Pope Innocent IV)', '熱那亞', '天主教', 0, 1227, 1243, '辭職（就任教宗）', '教宗額我略九世', '爭議', 'Catholic Hierarchy', '菲耶斯基家族的熱那亞樞機；1243年當選教宗英諾森四世——弗里德里希二世最堅決的對手；教宗至上論的重要發展者'),
('奧托包諾·菲耶斯基（後為哈德良五世）', 'Ottobono Fieschi (later Pope Adrian V)', '熱那亞', '天主教', 35, 1245, 1276, '辭職（就任教宗）', '教宗英諾森四世（其叔）', '正統', 'Catholic Hierarchy', '1276年短暫成為教宗哈德良五世（在位38天）；但丁《煉獄篇》中的人物'),
('雅科波·達·沃拉吉內', 'Jacopo da Varagine', '熱那亞', '天主教', 38, 1292, 1298, '逝世', '教宗尼古拉四世', '正統', 'Catholic Hierarchy', '《黃金傳說》（Legenda Aurea）作者——中世紀最廣泛閱讀的書籍之一；聖人故事的標準來源；多明我會士'),
('朱賽佩·西里', 'Giuseppe Siri', '熱那亞', '天主教', 77, 1946, 1987, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；在任41年；1958年、1963年、1978年連續三次被視為最有力的教宗候選人（保守派強力倡議）；堅定反共；義大利主教大會主席（1959–1965）'),
('喬萬尼·卡內斯特里', 'Giovanni Canestri', '熱那亞', '天主教', 78, 1987, 1995, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機'),
('迪奧尼吉·泰塔曼茲', 'Dionigi Tettamanzi', '熱那亞', '天主教', 79, 1995, 2002, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後轉任米蘭（2002–2011）；家庭倫理神學家'),
('塔爾奇西奧·貝爾托內', 'Tarcisio Bertone', '熱那亞', '天主教', 80, 2002, 2006, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；薩勒爵會士；後任梵蒂岡國務卿（2006–2013）——本篤十六世的親密助手'),
('安傑洛·巴尼亞斯科', 'Angelo Bagnasco', '熱那亞', '天主教', 81, 2006, 2020, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；義大利主教大會主席（2007–2017）；歐洲主教大會主席（2016–2021）'),
('馬爾科·塔斯卡', 'Marco Tasca', '熱那亞', '天主教', 82, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '方濟各會士；現任大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '熱那亞' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 巴勒摩（Palermo）
-- 西西里島首府；諾曼王國的光輝
-- ==============================
('米莫薩', 'Mamas of Palermo', '巴勒摩', '天主教', 3, 254, 260, '逝世', '使徒傳承', '正統', 'Catholic Hierarchy', '早期巴勒摩基督群體；希臘-羅馬殖民地時代'),
('尼可代穆斯', 'Nicodemus', '巴勒摩', '天主教', 8, 590, 606, '逝世', '教宗額我略一世', '正統', 'Catholic Hierarchy', '「大額我略」的通信對象；西西里教產的管理；大額我略親自關注西西里教務'),
('諾曼征服後的首任大主教', 'Nicodemus (Norman era)', '巴勒摩', '天主教', 23, 1072, 1086, '逝世', '教宗亞歷山大二世', '正統', 'Catholic Hierarchy', '諾曼人羅傑一世1072年收復巴勒摩；重建天主教主教座'),
('瓜爾鐵羅·博帕里', 'Gualtiero of the Mill (Walter Ophamil)', '巴勒摩', '天主教', 26, 1170, 1191, '逝世', '教宗亞歷山大三世', '正統', 'Catholic Hierarchy', '英格蘭裔；諾曼-西西里王國宰相（Royal Chancellor）；建造巴勒摩大教堂（1172年奠基）——諾曼-阿拉伯融合建築的傑作'),
('恩里科·米尼亞諾', 'Roberto di San Giovanni', '巴勒摩', '天主教', 34, 1350, 1363, '逝世', '教宗克萊孟六世', '正統', 'Catholic Hierarchy', '阿拉貢統治西西里時代；黑死病（1348）後'),
('恩里科·戴彼耶特羅', 'Ernesto Ruffini', '巴勒摩', '天主教', 62, 1945, 1967, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議的強硬保守派；反對任何改革；《聖經》字面主義，反歷史批判法；西西里的舊教會體制代表'),
('薩爾瓦托雷·帕帕拉爾多', 'Salvatore Pappalardo', '巴勒摩', '天主教', 63, 1970, 1996, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；1982年葬禮講道痛斥西西里黑手黨謀殺卡洛·達拉·基耶薩將軍——「羅馬燃燒，尼祿在演奏，卡比托利歐山在辯論」成為時代名言；義大利反黑手黨最勇敢的聲音之一'),
('薩爾瓦托雷·德吉奧爾吉', 'Salvatore De Giorgi', '巴勒摩', '天主教', 64, 1996, 2006, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；繼承帕帕拉爾多的反黑手黨立場'),
('科拉多·洛雷菲切', 'Corrado Lorefice', '巴勒摩', '天主教', 65, 2015, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '方濟각最親近的大主教之一；移民接待；反黑手黨；進步牧靈');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '巴勒摩' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 拉文納（Ravenna）
-- 西羅馬帝國末期首都；東哥特、拜占廷首都；最美的早期基督教馬賽克
-- ==============================
('聖阿波利納里斯', 'Saint Apollinaris of Ravenna', '拉文納', '天主教', 1, 67, 79, '殉道', '使徒傳承', '正統', 'Catholic Hierarchy; Agnellus', '傳統上為使徒彼得的門徒；拉文納首任主教；聖阿波利納里斯聖殿（6世紀建、世界遺產）即以其名命名'),
('聖伯多祿·克利索羅格', 'Saint Peter Chrysologus', '拉文納', '天主教', 28, 433, 450, '逝世', '教宗塞萊斯廷一世', '正統', 'Catholic Hierarchy; PL 52', '「金口彼得」；180篇講道詞保存至今；強調教宗羅馬的最高性；1729年宣布為教會聖師'),
('馬克西米安努斯', 'Maximianus of Ravenna', '拉文納', '天主教', 35, 546, 556, '逝世', '拜占廷皇帝查士丁尼', '正統', 'Catholic Hierarchy; Agnellus', '查士丁尼御用的拉文納主教；主持聖維塔萊聖殿（546年）、阿波利納里斯港聖殿的獻殿禮；拉文納馬賽克黃金時代的主持者'),
('菲利克斯', 'Felix of Ravenna', '拉文納', '天主教', 37, 708, 723, '廢黜', '教宗額我略二世', '爭議', 'Catholic Hierarchy; Agnellus', '拉文納大主教長達幾個世紀的「教宗獨立」（autocephaly）傾向的代表；和拜占廷皇帝利奧三世的聖像破壞主義有關'),
('格拉修斯·達·里米尼', 'Geremia da Montagnone', '拉文納', '天主教', 55, 1340, 1347, '逝世', '教宗本篤十二世', '正統', 'Catholic Hierarchy', '黑死病前夕；拉文納作為阿維尼翁教廷的北義大利基地'),
('貝納爾迪諾·科斯蒂尼', 'Biagio Opizzoni', '拉文納', '天主教', 80, 1802, 1819, '轉任', '教宗庇護七世', '正統', 'Catholic Hierarchy', '拿破崙征服後的重建；1815年維也納會議恢復教宗國'),
('洛倫佐·吉佐尼', 'Lorenzo Ghizzoni', '拉文納', '天主教', 94, 2019, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任拉文納大主教；世界遺產馬賽克修復的守護者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '拉文納' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
