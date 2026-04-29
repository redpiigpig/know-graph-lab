-- ============================================================
-- 天主教大主教傳承——西班牙（聖地亞哥-德孔波斯特拉、薩拉戈薩、瓦倫西亞、布爾戈斯、格拉納達）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 聖地亞哥-德孔波斯特拉（Santiago de Compostela）
-- 中世紀三大朝聖地之一
-- ==============================
('西奧德米爾', 'Sisnand I (Sisnando)', '聖地亞哥-德孔波斯特拉', '天主教', 2, 880, 920, '逝世', '阿方索三世', '正統', 'Historia Compostelana; Flórez', '聖地亞哥第一位具史可考的主教；確立朝聖路線與聖雅各墓室崇拜'),
('聖盧帕科', 'Sisnand II', '聖地亞哥-德孔波斯特拉', '天主教', 5, 952, 968, '殉道', '教會傳承', '正統', 'Historia Compostelana', '被維京人（諾曼人）入侵時殉道'),
('聖彼德', 'Pedro de Mezonzo', '聖地亞哥-德孔波斯特拉', '天主教', 10, 985, 1003, '逝世', '教會傳承', '正統', 'Historia Compostelana', '摩爾人領袖曼蘇爾（Al-Mansur）1001年洗劫聖地亞哥期間鼓勵重建；作者聖歌《聖母憐憫我》（Salve Regina）有時歸於其名'),
('迭戈·赫爾米雷斯', 'Diego Gelmírez', '聖地亞哥-德孔波斯特拉', '天主教', 18, 1100, 1140, '逝世', '教宗帕斯卡二世', '正統', 'Historia Compostelana (主要史料為其本人委托撰寫)', '聖地亞哥最重要的大主教（1120年升格）；建立聖地亞哥大教堂的現貌；創建朝聖基礎設施；推動卡斯提爾-萊昂政治中的教會獨立'),
('佩拉約·吉拉爾德斯', 'Bernardo II', '聖地亞哥-德孔波斯特拉', '天主教', 24, 1224, 1237, '逝世', '教宗霍諾留斯三世', '正統', 'Flórez', '朝聖時代高峰；卡斯提爾王國鞏固'),
('胡安·阿里亞斯·達維拉', 'Juan García Manrique', '聖地亞哥-德孔波斯特拉', '天主教', 32, 1370, 1398, '逝世', '教宗額我略十一世', '正統', 'Flórez', '西方大分裂期間；卡斯提爾服從阿維尼翁；政治外交主教'),
('阿方索·福恩薩二世', 'Alonso II de Fonseca', '聖地亞哥-德孔波斯特拉', '天主教', 40, 1460, 1507, '逝世', '教宗庇護二世', '正統', 'Flórez', '人文主義者；聖地亞哥大教堂Platerest式入口的贊助者；伊比利亞大航海時代'),
('阿方索·福恩薩三世', 'Alonso III de Fonseca', '聖地亞哥-德孔波斯特拉', '天主教', 42, 1523, 1534, '逝世', '教宗哈德良六世', '正統', 'Flórez', '薩拉曼卡大學的「聖地亞哥學院」贊助者；文藝復興盛期藝術贊助最高峰'),
('胡安·德聖克萊孟特', 'Juan de San Clemente', '聖地亞哥-德孔波斯特拉', '天主教', 46, 1587, 1602, '逝世', '教宗西斯都五世', '正統', 'Flórez', '特倫托改革推動者；建聖地亞哥神學院'),
('若澤·帕亞·伊·里科', 'Rafael Múñoz y Reyes', '聖地亞哥-德孔波斯特拉', '天主教', 56, 1851, 1861, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '西班牙自由主義革命後的教會重建'),
('唐·帕布羅·里瓦斯', 'Julián Barrio Barrio', '聖地亞哥-德孔波斯特拉', '天主教', 75, 1996, 2021, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '聖年（Compostelan Holy Year）多次主持；教宗方濟각2019年到訪'),
('弗朗西斯科·何塞·普列托·費爾南德斯', 'Francisco José Prieto Fernández', '聖地亞哥-德孔波斯特拉', '天主教', 76, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '聖地亞哥-德孔波斯特拉' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 薩拉戈薩（Zaragoza）
-- 伊比利亞古都；聖母柱聖殿所在地
-- ==============================
('聖比森特', 'Saint Valerius of Zaragoza', '薩拉戈薩', '天主教', 8, 290, 315, '流亡', '教會傳承', '正統', 'Flórez; Prudentius', '在任期間聖維森特（Vincent of Saragossa）殉道（304）；薩拉戈薩最著名的殉道者'),
('聖布雷卡里烏斯', 'Braulio of Zaragoza', '薩拉戈薩', '天主教', 14, 631, 651, '逝世', '西哥特王', '正統', 'Flórez; PL 80', '伊西多爾的弟子；西哥特西班牙最偉大的神學家之一；「聖人書信」（Epistolarium）留存；636年托雷多第四次公會議'),
('塞達後主教間斷（摩爾人統治）', 'Bishops under Moorish rule', '薩拉戈薩', '天主教', 0, 714, 1118, '摩爾人統治期', NULL, '正統', 'Flórez', '711年倭馬亞人征服伊比利亞；薩拉戈薩1118年被阿拉貢王阿方索一世收復——後重建主教座'),
('佩德羅·德·科雷拉', 'Pedro de Librana', '薩拉戈薩', '天主教', 35, 1118, 1128, '逝世', '阿拉貢王阿方索一世', '正統', 'Flórez', '收復後第一任主教；重建薩拉戈薩教會組織'),
('安德烈亞·德·卡夫雷拉', 'Hernando de Aragón', '薩拉戈薩', '天主教', 58, 1539, 1575, '逝世', '教宗保羅三世', '正統', 'Flórez', '阿拉貢王室後裔；特倫托大公會議時代；人文主義者'),
('安東尼奧·佩內特·帕拉達', 'Antonio Ibáñez de la Riva Herrera', '薩拉戈薩', '天主教', 67, 1687, 1710, '逝世', '教宗英諾森十一世', '正統', 'Catholic Hierarchy', '西班牙王位繼承戰爭期間；推動聖母柱大殿（Basílica del Pilar）重建'),
('卡洛斯·卡米洛·赫雷斯', 'Carlos Amigo Vallejo', '薩拉戈薩', '天主教', 82, 2004, 2014, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；薩拉戈薩世博（Expo 2008）宗教活動'),
('比森特·希門内斯·薩馬里科', 'Vicente Jiménez Zamora', '薩拉戈薩', '天主教', 83, 2014, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '薩拉戈薩' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 瓦倫西亞（Valencia）
-- 西班牙東岸重要大主教座
-- ==============================
('聖文森特費勒（先驅者非主教）', 'Domingo Peres de Sancho', '瓦倫西亞', '天主教', 1, 1239, 1248, '逝世', '教宗額我略九世', '正統', 'Flórez', '1238年阿拉貢王阿方索收復瓦倫西亞後設立主教區；首任主教'),
('羅德里戈·博爾吉亞（後為亞歷山大六世）', 'Rodrigo de Borja (later Pope Alexander VI)', '瓦倫西亞', '天主教', 10, 1458, 1492, '辭職（就任教宗）', '教宗卡利斯都三世（其舅）', '正統', 'Flórez', '1492年成為教宗亞歷山大六世——文藝復興最具爭議的教宗；哥倫布航行贊助者；博爾吉亞家族'),
('切薩雷·博爾吉亞（短暫）', 'Juan de Borja Lanzol de Romaní', '瓦倫西亞', '天主教', 11, 1492, 1500, '辭職', '教宗亞歷山大六世（其父）', '正統', 'Flórez', '切薩雷·博爾吉亞的親屬；博爾吉亞對瓦倫西亞的把持'),
('聖若望·德·里韋拉', 'Juan de Ribera', '瓦倫西亞', '天主教', 17, 1568, 1611, '逝世', '教宗庇護五世', '正統', 'Catholic Hierarchy', '樞機；在任43年；反宗教改革堅定推行者；1609年主導驅逐摩里斯科人（Moriscos）——西班牙最後一批摩爾裔基督徒；1960年封聖'),
('帕布羅·加西亞·德·拉奧達', 'Andrés Mayoral', '瓦倫西亞', '天主教', 26, 1738, 1769, '逝世', '教宗克萊孟十二世', '正統', 'Catholic Hierarchy', '啟蒙時代；推動耶穌會與多明我會爭議的調停'),
('卡洛斯·博爾邦-帕爾馬', 'Agustín Moran y Alcaraz', '瓦倫西亞', '天主教', 35, 1875, 1901, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '第一次西班牙共和國至復辟時代'),
('安托尼奧·孔卡', 'Marcelino Olaechea Loizaga', '瓦倫西亞', '天主教', 42, 1946, 1966, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；佛朗哥時代；梵二大公會議'),
('安東尼奧·卡尼薩雷斯·略維拉', 'Antonio Cañizares Llovera', '瓦倫西亞', '天主教', 49, 2008, 2014, '轉任', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；後任聖座敬禮與聖事部部長；後重返瓦倫西亞'),
('卡洛斯·奧索羅·莫拉萊斯', 'Carlos Osoro Sierra', '瓦倫西亞', '天主教', 50, 2009, 2014, '轉任', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；後轉任馬德里大主教'),
('安東尼奧·卡尼薩雷斯（再次就任）', 'Antonio Cañizares Llovera (restored)', '瓦倫西亞', '天主教', 51, 2014, 2022, '退休', '教宗方濟각', '正統', 'Catholic Hierarchy', '重返瓦倫西亞；2024年瓦倫西亞洪災後的教會角色'),
('恩里克·本拉赫', 'Enrique Benavent Vidal', '瓦倫西亞', '天主教', 52, 2023, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任大主教；2024年10月瓦倫西亞嚴重洪災期間的救災協調');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '瓦倫西亞' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 格拉納達（Granada）
-- 伊比利亞最後收復的摩爾人首都
-- ==============================
('埃爾南多·德·塔拉維拉', 'Hernando de Talavera', '格拉納達', '天主教', 1, 1493, 1507, '逝世', '教宗英諾森八世', '正統', 'Flórez; Catholic Hierarchy', '伊莎貝拉女王的告解司鐸；1492年收復格拉納達後設立主教區；首任大主教（1493年升格）；以和平方式向摩爾人傳教（與西門內斯方式相反）；被宗教裁判所調查（後獲清白）'),
('弗朗西斯科·西門內斯·德·西斯內羅斯', 'Francisco Jiménez de Cisneros', '格拉納達', '天主教', 2, 1507, 1517, '轉任（逝世前）', '教宗尤利烏斯二世', '正統', 'Flórez', '同時任托雷多大主教（1495–1517）；此處為兼任；1502年強制摩爾人改宗或驅逐'),
('佩德羅·德·帕切科', 'Gaspar de Ávalos', '格拉納達', '天主教', 4, 1528, 1542, '逝世', '教宗克萊孟七世', '正統', 'Flórez', '摩里斯科人（改宗摩爾人）的教育問題'),
('胡安·德阿爾亞里利亞', 'Pedro Guerrero', '格拉納達', '天主教', 7, 1546, 1576, '逝世', '教宗保羅三世', '正統', 'Flórez; Tellechea Idígoras', '特倫托大公會議西班牙最重要的主教（三個時段全程參與）；大公會議神學最積極的塑造者之一；1568年摩里斯科人起義後的處理'),
('佩德羅·德·卡斯特羅·卡貝薩', 'Pedro de Castro y Quiñones', '格拉納達', '天主教', 11, 1610, 1623, '逝世', '教宗保羅五世', '正統', 'Catholic Hierarchy', '薩克羅蒙特聖物（鉛片書，Lead Books）捍衛者——後被梵蒂岡認定為偽造（1682）'),
('若瑟·梅西亞·若梅羅', 'Bienvenido Comín Moya', '格拉納達', '天主教', 43, 1958, 1969, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '佛朗哥時代；格拉納達的現代天主教重建'),
('弗朗西斯科·希門內斯·莫利納', 'Francisco Javier Martínez Fernández', '格拉納達', '天主教', 50, 1996, 2021, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '保守立場；伊斯蘭-基督教關係（格拉納達的特殊歷史脈絡）'),
('何塞·加夫內·加西亞', 'José Gabriel Hinojosa Counts', '格拉納達', '天主教', 51, 2021, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '現任大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '格拉納達' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
