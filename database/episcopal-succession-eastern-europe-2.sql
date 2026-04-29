-- ============================================================
-- 天主教大主教傳承——東歐（薩格勒布、弗羅茨瓦夫、奧洛穆茨、維爾紐斯）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 薩格勒布（Zagreb）
-- 克羅埃西亞首都；反共鬥士斯特皮納茨的主教座
-- ==============================
('杜赫', 'Duh (Dueh)', '薩格勒布', '天主教', 1, 1094, 1095, '逝世', '匈牙利/克羅埃西亞王拉迪斯勞斯一世', '正統', 'Croatian Church History', '薩格勒布首任主教；1094年匈牙利王設立'),
('斯特凡二世', 'Stephen II', '薩格勒布', '天主教', 6, 1215, 1247, '逝世', '教宗霍諾留斯三世', '正統', 'Croatian Church History', '蒙古入侵克羅埃西亞（1241–1242）期間在任；重建受破壞的薩格勒布'),
('奧斯瓦爾德·特胡斯', 'Osvald Thuz', '薩格勒布', '天主教', 20, 1466, 1499, '逝世', '教宗庇護二世', '正統', 'Croatian Church History', '奧斯曼土耳其入侵威脅下的克羅埃西亞；重建薩格勒布大教堂'),
('尤拉伊·德拉什科維奇', 'Juraj Drašković', '薩格勒布', '天主教', 26, 1563, 1578, '轉任', '教宗庇護四世', '正統', 'Croatian Church History', '特倫托大公會議克羅埃西亞代表；反宗教改革推動者；後成匈牙利首席大主教'),
('馬克西米利安·弗爾霍瓦茨', 'Maksimilijan Vrhovec', '薩格勒布', '天主教', 40, 1787, 1827, '逝世', '教宗庇護六世', '正統', 'Croatian Church History', '啟蒙時代；克羅埃西亞民族覺醒（Illyrian Movement）的宗教支柱；為克羅埃西亞語言文化的保護者'),
('若望·朱拉伊·豪利克', 'Juraj Haulik de Varallya', '薩格勒布', '天主教', 41, 1837, 1869, '逝世', '教宗額我略十六世', '正統', 'Croatian Church History', '薩格勒布升格為大主教區首任大主教（1852年）；克羅埃西亞文化贊助人；薩格勒布大學重建'),
('阿洛伊西耶·斯特皮納茨', 'Alojzije Stepinac', '薩格勒布', '天主教', 45, 1937, 1960, '逝世（被囚）', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；二戰期間批評烏斯塔沙政權（克羅埃西亞法西斯）屠殺塞爾維亞人和猶太人；1946年被南斯拉夫共產政府以戰犯罪名審判（引發全球抗議）——被囚多年後軟禁；1952年獲樞機頭銜（在獄中）；1998年教宗若望保祿二世在薩格勒布親自主禮宣福典禮'),
('弗蘭約·謝佩爾', 'Franjo Šeper', '薩格勒布', '天主教', 46, 1960, 1969, '轉任', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議積極參與；後任聖座信理部部長（1968–1981）——本篤十六世的前任前任'),
('弗蘭約·庫哈里奇', 'Franjo Kuharić', '薩格勒布', '天主教', 47, 1970, 1997, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；南斯拉夫解體（1991）和克羅埃西亞戰爭期間；呼籲和平；保護薩格勒布免受戰火'),
('約瑟普·博扎尼奇', 'Josip Bozanić', '薩格勒布', '天主教', 48, 1997, NULL, NULL, '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後南戰爭時代的克羅埃西亞天主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '薩格勒布' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 弗羅茨瓦夫（Wrocław / Breslau）
-- 西里西亞首府；德波邊境歷史的縮影
-- ==============================
('若望一世', 'Johannes I', '弗羅茨瓦夫', '天主教', 1, 1000, 1004, '逝世', '教宗西爾維斯特二世', '正統', 'Polish historiography; Thietmar', '弗羅茨瓦夫主教區創立於格涅茲諾會議（1000年）；波蘭基督化的一環'),
('南科', 'Nanker', '弗羅茨瓦夫', '天主教', 17, 1326, 1341, '轉任', '教宗若望二十二世', '正統', 'Polish historiography', '衝突德意志騎士團侵占波蘭領土；捍衛波蘭主教區的獨立性'),
('若望三世·馮·羅特', 'John III of Roth', '弗羅茨瓦夫', '天主教', 27, 1482, 1506, '逝世', '教宗西斯都四世', '正統', 'Catholic Hierarchy', '文藝復興人文主義者；哈布斯堡統治西里西亞（1526前後）'),
('弗朗茨·馮·迪芬布羅克', 'Franz von Diepenbrock', '弗羅茨瓦夫', '天主教', 56, 1845, 1853, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '樞機；普魯士統治下的西里西亞天主教；德波民族矛盾'),
('格奧爾格·科普', 'Georg Kopp', '弗羅茨瓦夫', '天主教', 61, 1887, 1914, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；文化鬥爭後的復興；西里西亞波蘭裔與德裔的複雜關係'),
('阿道夫·貝特拉姆', 'Adolf Bertram', '弗羅茨瓦夫', '天主教', 64, 1914, 1945, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；納粹時代德國主教團主席；對納粹政策的妥協態度（批評者甚多）；西里西亞被波蘭接管前夕'),
('博列斯瓦夫·科明内克', 'Bolesław Kominek', '弗羅茨瓦夫', '天主教', 66, 1956, 1974, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；1965年波蘭主教致德國主教的「互相原諒書信」起草人——「我們原諒，也求原諒」——冷戰和解的重要姿態'),
('亨里克·古爾比諾維奇', 'Henryk Gulbinowicz', '弗羅茨瓦夫', '天主教', 67, 1976, 2004, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；支持團結工會；共產政府的對抗；晚年因性醜聞被剝奪樞機職銜（2020年）'),
('約瑟夫·庫普尼', 'Józef Kupny', '弗羅茨瓦夫', '天主教', 69, 2013, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任弗羅茨瓦夫大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '弗羅茨瓦夫' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 奧洛穆茨（Olomouc）
-- 摩拉維亞首府；馬赫利奇（Franz von Dietrichstein）強制反宗教改革
-- ==============================
('若望一世', 'Johannes I', '奧洛穆茨', '天主教', 1, 1063, 1085, '逝世', '波希米亞公爵弗拉提斯拉夫二世', '正統', 'Czech Church History', '奧洛穆茨主教區創立（1063年）；摩拉維亞基督化的深化'),
('羅伯特', 'Robert of Olomouc', '奧洛穆茨', '天主教', 8, 1201, 1240, '逝世', '教宗英諾森三世', '正統', 'Czech Church History', '第四次十字軍後的摩拉維亞；蒙古入侵前夕（1241）'),
('彼得·沃克', 'Petr Vok z Kravař', '奧洛穆茨', '天主教', 20, 1416, 1434, '逝世', '教宗馬丁五世', '正統', 'Czech Church History', '胡斯戰爭（1419–1434）時期；摩拉維亞的天主教防禦'),
('斯坦尼斯瓦夫·帕夫洛夫斯基', 'Stanislav Pavlovský', '奧洛穆茨', '天主教', 27, 1579, 1598, '逝世', '教宗額我略十三世', '正統', 'Catholic Hierarchy', '特倫托後反宗教改革的積極推動者；引入耶穌會；摩拉維亞重新天主教化'),
('弗朗茨·馮·迪特里希施坦', 'Franz von Dietrichstein', '奧洛穆茨', '天主教', 28, 1599, 1636, '逝世', '教宗克萊孟八世', '正統', 'Catholic Hierarchy', '樞機；白山之役（1620）後強制推行天主教——摩拉維亞最激烈的反宗教改革；大批新教徒流亡或改宗；馬赫利奇家族統治模式'),
('揚·格勞布納', 'Jan Graubner', '奧洛穆茨', '天主教', 56, 1992, 2022, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '任奧洛穆茨大主教30年（1992–2022）；後轉任布拉格（2022–）；捷克主教大會主席'),
('若塞夫·努吉克', 'Josef Nuzík', '奧洛穆茨', '天主教', 57, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任奧洛穆茨大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '奧洛穆茨' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 維爾紐斯（Vilnius）
-- 立陶宛首都；歷史上的波蘭、立陶宛、俄羅斯統治交替
-- ==============================
('安德烈·瓦斯科', 'Andrzej Jastrzębiec', '維爾紐斯', '天主教', 1, 1388, 1398, '轉任', '波蘭王弗拉迪斯拉夫二世（雅蓋洛）', '正統', 'Lithuanian Church History', '維爾紐斯主教區創立（1388年立陶宛基督化後）；第一任主教'),
('馬蒂亞斯·安德烈萊維奇', 'Matthias of Trakai', '維爾紐斯', '天主教', 5, 1453, 1461, '逝世', '教宗尼古拉五世', '正統', 'Lithuanian Church History', '立陶宛基督化深化期；卡西米爾四世統治下的立陶宛-波蘭聯合'),
('阿爾伯特·斯坦尼斯瓦夫·拉齊維烏', 'Albrycht Stanisław Radziwiłł', '維爾紐斯', '天主教', 21, 1616, 1623, '逝世', '教宗保羅五世', '正統', 'Lithuanian Church History', '拉齊維烏家族（波蘭-立陶宛最強大貴族）的主教；天主教立陶宛文化的象徵'),
('若望·克隆賽爾', 'Józef Arnulf Szembek', '維爾紐斯', '天主教', 33, 1732, 1795, '逝世', '教宗克萊孟十二世', '正統', 'Lithuanian Church History', '波蘭瓜分（1795）前的最後一任獨立主教；俄羅斯吞併後教區陷入困境'),
('斯坦尼斯瓦夫·澤林斯基', 'Karol Hryniewiecki', '維爾紐斯', '天主教', 41, 1883, 1890, '逝世', '教宗利奧十三世', '正統', 'Lithuanian Church History', '俄羅斯統治下；1863年起義失敗後的壓制'),
('若澤夫·揚科夫斯基', 'Jerzy Matulewicz', '維爾紐斯', '天主教', 45, 1918, 1925, '轉任', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '立陶宛獨立（1918）後的教區重建；馬里安傳教士會創始人；1987年真福品'),
('羅穆阿爾達斯·卡林斯卡斯', 'Romualdas Krikščiūnas', '維爾紐斯', '天主教', 52, 1990, 2013, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '蘇聯解體（1991）後立陶宛天主教的重建；維爾紐斯升格為大主教區（1993年）'),
('亞歷山大·卡什克利斯', 'Gintaras Grušas', '維爾紐斯', '天主教', 54, 2013, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '樞機（2024年）；歐洲主教大會主席（2021–）；立陶宛出生的美國公民背景');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '維爾紐斯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
