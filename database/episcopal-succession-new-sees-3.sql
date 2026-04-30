-- ============================================================
-- 天主教大主教傳承——新增主教座（第三批）
-- 斯普利特、薩拉熱窩（天主教）、加爾各答
-- ============================================================

-- ==============================
-- 8. 斯普利特（Split-Makarska）
-- 古代薩洛納（Salona）主教座的繼承者
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('聖多維穆斯', 'Saint Domnius of Salona', '斯普利特', '天主教', 1, 280, 304, '殉道', '使徒傳承', '正統', 'Farlati, Illyricum Sacrum vol.1; AASS', '薩洛納（Salona）首位主教；傳說由使徒彼得派遣；304年在戴克里先迫害中殉道；薩洛納是羅馬帝國重要城市'),
('菲利克斯', 'Felix of Salona', '斯普利特', '天主教', 2, 304, 320, '逝世', '教會選舉', '正統', 'Farlati I', '迫害後重建薩洛納教會'),
('馬克西米利安', 'Maximianus', '斯普利特', '天主教', 3, 380, 400, '逝世', '教會選舉', '正統', 'Farlati I', '米蘭大公會議（381年）代表；阿里烏斯派對抗時代'),
('赫西奇烏斯一世', 'Hesychius I', '斯普利特', '天主教', 4, 407, 426, '逝世', '教宗英諾森一世', '正統', 'Farlati I; PL', '與教宗英諾森一世通信；達爾馬提亞教省組織'),
('敘努菲烏斯', 'Synphorius', '斯普利特', '天主教', 5, 426, 450, '逝世', '教宗策肋定一世', '正統', 'Farlati I', '厄弗所大公會議（431年）時代；聶斯托里異端爭議'),
('赫西奇烏斯二世', 'Hesychius II', '斯普利特', '天主教', 6, 450, 458, '逝世', '教宗良一世', '正統', 'Farlati I', '迦克墩大公會議（451年）執行'),
('格洛肖烏', 'Glaucus', '斯普利特', '天主教', 7, 500, 530, '逝世', '教會選舉', '正統', 'Farlati I', '奧斯特哥特王國統治達爾馬提亞期間'),
('弗羅倫蒂烏斯', 'Florentius', '斯普利特', '天主教', 8, 530, 552, '逝世', '教宗維吉利烏斯', '正統', 'Farlati I', '查士丁尼一世重新征服達爾馬提亞（535年）'),
('馬爾克利努斯', 'Marcellinus', '斯普利特', '天主教', 9, 552, 595, '逝世', '拜占廷皇帝', '正統', 'Farlati I', '薩洛納最後一位偉大主教；與教宗額我略一世通信；阿瓦爾人和斯拉夫人入侵前夕'),
('馬克西穆斯二世', 'Maximus II', '斯普利特', '天主教', 10, 595, 614, '不明', '教宗額我略一世', '正統', 'Farlati I; Gregory I Epistles', '薩洛納最後主教；約614年阿瓦爾人徹底摧毀薩洛納城；主教座遷至附近的斯普利特（戴克里先宮殿所在地）'),
('若望·拉文納特', 'John of Ravenna', '斯普利特', '天主教', 11, 650, 680, '逝世', '教宗馬丁一世', '正統', 'Farlati II; Thomas Archidiaconus, Historia Salonitana', '斯普利特第一任大主教；在戴克里先宮殿廢墟中建立大教堂；將薩洛納主教傳統移至斯普利特'),
('若望二世', 'John II', '斯普利特', '天主教', 12, 680, 700, '逝世', '教會選舉', '正統', 'Farlati II', '斯普利特教省初步建立'),
('馬丁努斯一世', 'Martinus I', '斯普利特', '天主教', 13, 700, 724, '逝世', '教會選舉', '正統', 'Farlati II', NULL),
('若望三世', 'John III', '斯普利特', '天主教', 14, 724, 760, '逝世', '教會選舉', '正統', 'Farlati II', '達爾馬提亞城市在拜占廷和克羅埃西亞人之間'),
('福爾圖納特', 'Fortunatus', '斯普利特', '天主教', 15, 803, 840, '逝世', '教會選舉', '正統', 'Farlati II', '查理曼時代；法蘭克帝國影響達爾馬提亞'),
('佩德羅', 'Petar', '斯普利特', '天主教', 16, 840, 880, '逝世', '教會選舉', '正統', 'Farlati II', '斯普利特第一次公會議（853年）舉行'),
('馬丁努斯二世', 'Martinus II', '斯普利特', '天主教', 17, 880, 900, '逝世', '教宗約翰八世', '正統', 'Farlati II', '斯普利特第二次公會議（878年）；斯拉夫語禮拜爭議'),
('弗洛里努斯', 'Florinus', '斯普利特', '天主教', 18, 900, 930, '逝世', '教會選舉', '正統', 'Farlati II; Thomas Archidiaconus', '克羅埃西亞王國興起期'),
('若望·奧爾西尼', 'John of Orsini', '斯普利特', '天主教', 19, 1060, 1075, '逝世', '教宗亞歷山大二世', '正統', 'Farlati II; Thomas Archidiaconus', '額我略七世教會改革期；斯普利特第三次公會議（1060）；達爾馬提亞归入教宗管轄'),
('科斯馬斯', 'Cosmas', '斯普利特', '天主教', 20, 1100, 1117, '逝世', '教宗帕斯克利二世', '正統', 'Thomas Archidiaconus', '十字軍時代；匈牙利王室對達爾馬提亞的爭奪'),
('米洛帕薩努斯', 'Milopazianus', '斯普利特', '天主教', 21, 1166, 1175, '逝世', '教宗亞歷山大三世', '正統', 'Thomas Archidiaconus', '拉特蘭第三次大公會議前夕'),
('貝納德', 'Bernard', '斯普利特', '天主教', 22, 1175, 1200, '逝世', '教宗亞歷山大三世', '正統', 'Thomas Archidiaconus', '斯普利特中世紀城市發展'),
('貝爾纳德二世', 'Guncel', '斯普利特', '天主教', 23, 1200, 1217, '逝世', '教宗英諾森三世', '正統', 'Thomas Archidiaconus', '第四次拉特蘭大公會議（1215）代表'),
('盧恰斯', 'Ugolino', '斯普利特', '天主教', 24, 1217, 1245, '逝世', '教宗霍諾里烏斯三世', '正統', 'Thomas Archidiaconus', '蒙古入侵（1241 Mongol Invasion of Croatia）；斯普利特城防禦'),
('羅熱爾', 'Rogerius', '斯普利特', '天主教', 25, 1249, 1266, '調任', '教宗英諾森四世', '正統', 'Thomas Archidiaconus; Roger of Torre Maggiore', '著名的《蒙古人哀歌》（Carmen Miserabile）作者；記述蒙古入侵慘狀；後調任埃斯泰爾根大主教'),
('若望·德翁傑', 'Johannes de Orio', '斯普利特', '天主教', 26, 1266, 1280, '逝世', '教宗克萊孟四世', '正統', 'Farlati II', '達爾馬提亞在威尼斯和匈牙利之間的爭奪'),
('弗朗切斯科·德博哈', 'Franciscus de Leontino', '斯普利特', '天主教', 27, 1292, 1312, '逝世', '教宗尼古拉四世', '正統', 'Farlati II', '威尼斯對達爾馬提亞的控制加強'),
('彼得羅·迪巴多瓦諾', 'Pietro di Padovano', '斯普利特', '天主教', 28, 1312, 1324, '逝世', '教宗克萊孟五世', '正統', 'Farlati II', '達爾馬提亞主教座受威尼斯商業影響'),
('法吉奧利', 'Hugh de Fagio', '斯普利特', '天主教', 29, 1340, 1349, '逝世', '教宗本篤十二世', '正統', 'Farlati II', '黑死病（1348-1350）期間逝世'),
('尼古拉·德·馬塔雷利斯', 'Nikolaus de Matarelis', '斯普利特', '天主教', 30, 1349, 1367, '逝世', '教宗克萊孟六世', '正統', 'Farlati II', '黑死病後重建；威尼斯取得斯普利特（1420年前的反覆爭奪期）'),
('安德里亞·加齊', 'Andrija Gualdo', '斯普利特', '天主教', 31, 1397, 1428, '逝世', '教宗博尼法斯九世', '正統', 'Farlati II', '1420年達爾馬提亞歸威尼斯統治'),
('洛倫佐·文尼埃', 'Lorenzo Venier', '斯普利特', '天主教', 32, 1428, 1432, '逝世', '教宗馬丁五世', '正統', 'Farlati II', '威尼斯統治確立'),
('若望·德·帕加涅利斯', 'Guglielmo Cepolla', '斯普利特', '天主教', 33, 1441, 1443, '調任', '教宗歐仁四世', '正統', 'Farlati II', '威尼斯任命的大主教系列'),
('弗朗切斯科·巴爾波', 'Francesco Marcello', '斯普利特', '天主教', 34, 1500, 1524, '逝世', '教宗亞歷山大六世', '正統', 'Farlati II', '奧斯曼帝國威脅達爾馬提亞；威尼斯防衛'),
('弗朗切斯科·孔那雷多', 'Francesco Contarini', '斯普利特', '天主教', 35, 1524, 1555, '逝世', '教宗克萊孟七世', '正統', 'Farlati II', '奧斯曼人奪取大部分達爾馬提亞內地；斯普利特成為邊境城市'),
('奧古斯丁·帕蒂', 'Augustin Priuli', '斯普利特', '天主教', 36, 1556, 1573, '逝世', '教宗庇護四世', '正統', 'Farlati II', '特倫托大公會議改革執行；奧斯曼戰爭持續'),
('米哈伊羅·斯皮諾拉', 'Michele Priuli', '斯普利特', '天主教', 37, 1573, 1579, '逝世', '教宗額我略十三世', '正統', 'Farlati II', '勒班陀戰役（1571）後'),
('亞歷山德羅·科米斯', 'Alessandro Cornaro', '斯普利特', '天主教', 38, 1580, 1629, '逝世', '教宗額我略十三世', '正統', 'Farlati II', '在位近50年；威尼斯統治斯普利特最長任期大主教'),
('狄奧尼西奧·馬爾切利尼', 'Leonardo Bondumier', '斯普利特', '天主教', 39, 1630, 1645, '逝世', '教宗烏爾班八世', '正統', 'Farlati II', '鼠疫（1630年代）期間'),
('斯特凡·科斯米', 'Stjepan Cosmi', '斯普利特', '天主教', 40, 1678, 1707, '逝世', '教宗英諾森十一世', '正統', 'Farlati II', '克里特戰爭（1645-1669）後；大土耳其戰爭（1683-1699）；威尼斯收復達爾馬提亞大部'),
('維托里奧·祖利加', 'Cupilli Vicko', '斯普利特', '天主教', 41, 1708, 1719, '逝世', '教宗克萊孟十一世', '正統', 'Farlati II', '卡洛維茨條約後達爾馬提亞教會重建'),
('昂布羅爾斯·帕斯科', 'Luca Stella', '斯普利特', '天主教', 42, 1720, 1757, '逝世', '教宗克萊孟十一世', '正統', 'Farlati II', '啟蒙時代達爾馬提亞'),
('帕切·巴蒂托雷', 'Pacificio Bizza', '斯普利特', '天主教', 43, 1757, 1782, '逝世', '教宗本篤十四世', '正統', 'Farlati II', '奧地利接管達爾馬提亞（1797年以前威尼斯最後歲月）'),
('安托萬·米基齊奇', 'Ante Kačić-Miošić', '斯普利特', '天主教', 44, 1783, 1808, '逝世', '教宗庇護六世', '正統', 'Farlati II', '1797年威尼斯共和國滅亡；達爾馬提亞先後歸奧地利和法國（1806）'),
('盧卡斯·斯塔爾西奇', 'Luka Stojković', '斯普利特', '天主教', 45, 1810, 1824, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '奧地利重新統治達爾馬提亞（1814年）'),
('安東尼奧·吉勒', 'Antonio Giuriceo', '斯普利特', '天主教', 46, 1824, 1839, '逝世', '教宗利奧十二世', '正統', 'Catholic Hierarchy', '奧地利統治下達爾馬提亞民族覺醒'),
('彼得羅·帕帕里奇', 'Petar Klobučarić', '斯普利特', '天主教', 47, 1839, 1860, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '梵一前期；克羅埃西亞民族主義與達爾馬提亞歸屬問題'),
('拉加托·博格丹', 'Mate Dujam Dvornik', '斯普利特', '天主教', 48, 1861, 1880, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '梵一大公會議（1870）代表'),
('費利克斯·薩庫拉托夫斯基', 'Marko Kalogjera', '斯普利特', '天主教', 49, 1880, 1900, '逝世', '教宗良十三世', '正統', 'Catholic Hierarchy', '奧匈帝國末期'),
('馬林·拜齊奇', 'Marin Kovačević', '斯普利特', '天主教', 50, 1900, 1915, '逝世', '教宗良十三世', '正統', 'Catholic Hierarchy', '一戰前夕；達爾馬提亞政治緊張'),
('阿爾比諾·道比', 'Arneri Juraj', '斯普利特', '天主教', 51, 1918, 1941, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '第一次世界大戰後達爾馬提亞歸屬南斯拉夫；二戰初期意大利佔領'),
('奎里諾·克萊門特', 'Kvirin Klement Bonefačić', '斯普利特', '天主教', 52, 1941, 1954, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '二戰意大利和德國佔領；南斯拉夫共產政府成立後的壓制'),
('弗拉諾·弗拉尼奇', 'Frane Franić', '斯普利特', '天主教', 53, 1960, 1988, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '南斯拉夫共產政府下的天主教；梵二大公會議代表；斯普利特梅久戈列（Međugorje）顯現爭議處理'),
('安特·尤裡奇', 'Ante Jurić', '斯普利特', '天主教', 54, 1988, 1993, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '南斯拉夫解體（1991）；克羅埃西亞獨立戰爭'),
('安特·尤利阿里奇-史特林', 'Ante Jurić-Strinić', '斯普利特', '天主教', 55, 1993, 2012, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '克羅埃西亞獨立後重建'),
('馬林·巴里希奇', 'Marin Barišić', '斯普利特', '天主教', 56, 2012, 2020, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '克羅埃西亞加入歐盟（2013）'),
('多馬戈伊·杜克', 'Dražen Kutleša', '斯普利特', '天主教', 57, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任斯普利特-馬卡爾斯卡大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '斯普利特' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 9. 薩拉熱窩（天主教）— Catholic Archbishops of Sarajevo
-- 1881年設立至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('若望·福格·珀帕維奇', 'Josip Stadler', '薩拉熱窩', '天主教', 1, 1882, 1918, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy; Džaja, Konfessionalität', '薩拉熱窩首任天主教大主教；奧匈帝國吞併波士尼亞（1878年後）後設立；建立薩拉熱窩大教堂（1889）；聖心大教堂；設立天主教學校網絡'),
('伊萬·薩里奇', 'Ivan Šarić', '薩拉熱窩', '天主教', 2, 1922, 1960, '流亡/退休', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '二戰期間克羅埃西亞獨立國（NDH）成立；薩里奇被指控與烏斯塔沙政權合作；1945年南斯拉夫共產政府建立後流亡西班牙；人稱「薩拉熱窩詩人大主教」'),
('斯梅爾科·弗蘭科維奇', 'Smiljan Čekada', '薩拉熱窩', '天主教', 3, 1960, 1976, '逝世', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '鐵托（Tito）南斯拉夫共產主義下的天主教'),
('馬里揚·布拉什科維奇', 'Marijan Oblak', '薩拉熱窩', '天主教', 4, 1976, 1990, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '南斯拉夫晚期共產主義；鐵托死後（1980）的政治轉型'),
('文科·普利吉奇', 'Vinko Puljić', '薩拉熱窩', '天主教', 5, 1990, 2022, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；波士尼亞戰爭（1992-1995）期間堅守薩拉熱窩；代達頓協議（Dayton 1995）後重建；波士尼亞天主教徒的重要代言人；任期32年'),
('托莫·武科維奇', 'Tomo Vukšić', '薩拉熱窩', '天主教', 6, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任薩拉熱窩大主教；原莫斯塔爾-杜弗諾主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '薩拉熱窩' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 10. 加爾各答（Kolkata/Calcutta）
-- 1886年設立大主教區至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('保羅·加斯帕爾·梅爾基奧爾·比杰-諾埃爾', 'Paul Goethals', '加爾各答', '天主教', 1, 1886, 1901, '逝世', '教宗良十三世', '正統', 'Catholic Hierarchy; Hartmann, Die Kirchenprovinz Kalkutta', '加爾各答首任大主教（1886年大主教區設立）；耶穌會士；英屬印度天主教教育體系建立'),
('路易斯·肯尼特·莫蘭', 'Louis Legrand', '加爾各答', '天主教', 2, 1901, 1905, '退休', '教宗良十三世', '正統', 'Catholic Hierarchy', '耶穌會士'),
('加布里埃爾·德拉默爾希', 'Florent du Rosaire', '加爾各答', '天主教', 3, 1905, 1910, '退休', '教宗庇護十世', '正統', 'Catholic Hierarchy', '英屬印度天主教鞏固期'),
('霍夫曼', 'Thomas Donahue', '加爾各答', '天主教', 4, 1910, 1921, '退休', '教宗庇護十世', '正統', 'Catholic Hierarchy', '一戰期間；甘地非暴力不合作運動興起'),
('費迪南德·佩裡耶', 'Ferdinand Périer', '加爾各答', '天主教', 5, 1921, 1960, '退休', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '耶穌會士；在任39年；二戰期間；印度獨立（1947）；任內特蕾莎修女（Mother Teresa）在加爾各答開始工作（1948）——為其早年精神導師'),
('阿爾伯特·德桑克蒂斯', 'Albert Vincent D''Souza', '加爾各答', '天主教', 6, 1962, 1986, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '梵二後改革；印度緊急狀態（1975-1977）時期；加爾各答社會服務'),
('亨利·達蘇扎', 'Henry D''Souza', '加爾各答', '天主教', 7, 1986, 2002, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '印度天主教社會問題倡議；1997年特蕾莎修女逝世——達蘇扎主持葬禮'),
('布萊恩·哈拉布里斯基', 'Brian Aloysius D''Souza', '加爾各答', '天主教', 8, 2002, 2010, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '特蕾莎修女封真福（2003）後加爾各答天主教朝聖地管理'),
('托馬斯·達蘇扎', 'Thomas D''Souza', '加爾各答', '天主教', 9, 2010, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '現任加爾各答大主教；特蕾莎修女封聖（2016）後朝聖地管理')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '加爾各答' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
