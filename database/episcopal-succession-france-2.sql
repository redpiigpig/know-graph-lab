-- ============================================================
-- 天主教大主教傳承——法國補充（盧昂、圖盧茲、都爾、波爾多）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 盧昂（Rouen）
-- 諾曼底首府；聖女貞德殉道之地
-- ==============================
('聖尼卡修斯', 'Saint Nicaise of Rouen', '盧昂', '天主教', 1, 260, 285, '逝世', '使徒傳承', '正統', 'Gallia Christiana', '盧昂首任主教；傳統上由教宗法比安派遣'),
('聖維克特里修斯', 'Saint Victricius of Rouen', '盧昂', '天主教', 9, 386, 409, '逝世', '教宗西里修斯', '正統', 'Gallia Christiana; Victricius, De Laude Sanctorum', '從軍脫逃後受洗；《讚頌聖人》（De Laude Sanctorum）作者；將英格蘭、蘇格蘭帶入其傳教圈；聖馬丁的友人；聖奧古斯丁與之通信'),
('聖羅曼努斯', 'Saint Romanus of Rouen', '盧昂', '天主教', 22, 631, 639, '逝世', '教宗霍諾留斯一世', '正統', 'Gallia Christiana', '馴服龍（la Gargouille）傳說的主角——中世紀最著名的主教民間故事之一；盧昂的主保聖人；每年「特赦」（Fierte Saint-Romain）儀式延續至18世紀'),
('蒂博達約', 'William Bona Anima (Guillaume Bonne-Âme)', '盧昂', '天主教', 34, 1079, 1110, '逝世', '教宗額我略七世', '正統', 'Gallia Christiana', '威廉征服者的摯友和懺悔神父；1087年主持威廉一世葬禮；諾曼底征服英格蘭後的關鍵教會人物'),
('若望·德貝爾梅', 'Geoffrey of York', '盧昂', '天主教', 38, 1207, 1222, '逝世', '教宗英諾森三世', '正統', 'Gallia Christiana', '諾曼底被卡佩王朝奪取（1204）後的第一任主教；管轄盧昂的政治鉅變'),
('路易二世·德奧爾良', 'Louis d''Harcourt', '盧昂', '天主教', 48, 1423, 1479, '逝世', '教宗馬丁五世', '正統', 'Gallia Christiana', '聖女貞德（1431年）在盧昂被裁判、處決期間在任的大主教；主教彼得·科雄（Cauchon）是異端審判官，但仍在盧昂大主教管轄下'),
('喬治·德安布瓦斯', 'Georges d''Amboise', '盧昂', '天主教', 54, 1493, 1510, '逝世', '教宗亞歷山大六世', '正統', 'Gallia Christiana', '路易十二的首席大臣；法國最有權勢的人之一；兩度競選教宗（1503年）；推動法國政教和諧；盧昂大主教宮重建'),
('皮埃爾·卡穆', 'Pierre Camus', '盧昂', '天主教', 61, 1628, 1631, '轉任', '教宗烏爾班八世', '正統', 'Gallia Christiana', '），著名小說家和靈修作家——《精神的樂趣》（L''Esprit de Saint François de Sales）'),
('弗朗索瓦·哈爾萊·德尚帕龍（任巴黎前）', 'Hardouin Fortin de la Hoguette', '盧昂', '天主教', 64, 1641, 1671, '轉任', '教宗烏爾班八世', '正統', 'Gallia Christiana', '轉任後繼任者弗朗索瓦·哈爾萊後來成為巴黎大主教；盧昂大教堂的修建'),
('弗朗索瓦-保羅·德奈勒', 'Dominique Lebrun', '盧昂', '天主教', 85, 2015, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任盧昂大主教；2024年盧昂教堂人員謀殺案期間的牧養');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '盧昂' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 圖盧茲（Toulouse）
-- 南法朗格多克首府；卡特里派爭端中心
-- ==============================
('聖薩圖爾尼努斯（塞爾南）', 'Saint Saturninus (Sernin) of Toulouse', '圖盧茲', '天主教', 1, 245, 257, '殉道', '使徒傳承', '正統', 'Gallia Christiana; Prudentius', '圖盧茲首任主教；綁在公牛尾後被拖死殉道；聖塞爾南聖殿（朝聖地）即以其名命名；傳統上由教宗法比安派遣'),
('聖埃克希珀留斯', 'Saint Exuperius', '圖盧茲', '天主教', 7, 390, 412, '逝世', '教宗達瑪索一世', '正統', 'Gallia Christiana; St. Jerome Ep. 125', '聖傑羅姆的友人；在高盧入侵（407年汪達爾人）時救助窮人；建造聖薩圖爾尼努斯聖殿'),
('弗爾克·馮·馬賽', 'Foulque de Marseille', '圖盧茲', '天主教', 47, 1205, 1231, '逝世', '教宗英諾森三世', '正統', 'Gallia Christiana; Chanson de la Croisade', '原為普羅旺斯吟遊詩人（troubadour）後成主教；阿爾比派十字軍（1209–1229）的主要支持者；但丁在《神曲》天堂篇提及他'),
('艾蒂安·奧貝爾（後為英諾森六世）', 'Étienne Aubert (later Pope Innocent VI)', '圖盧茲', '天主教', 55, 1357, 1361, '辭職（就任教宗）', '教宗克萊孟六世', '正統', 'Gallia Christiana', '1352年已任教宗英諾森六世；1357年被任命圖盧茲大主教為榮銜；阿維尼翁教廷重整教會紀律的教宗'),
('若望·德·拉格朗日', 'Pierre de Monteruc', '圖盧茲', '天主教', 59, 1371, 1388, '轉任', '教宗額我略十一世', '正統', 'Gallia Christiana', '西方大分裂期間；法國服從阿維尼翁'),
('若望·德·蒙托班', 'Bernard de Rosier', '圖盧茲', '天主教', 64, 1452, 1475, '逝世', '教宗尼古拉五世', '正統', 'Gallia Christiana', '推動人文主義教育；圖盧茲大學教會法學院的發展'),
('若望·德·拉羅什福科', 'Pierre de Bonsy', '圖盧茲', '天主教', 75, 1669, 1697, '逝世', '教宗克萊孟九世', '正統', 'Gallia Christiana', '路易十四絕對主義時代；南特敕令廢除（1685）後圖盧茲的胡格諾派改宗'),
('若望·丹尼爾-帕蒂埃', 'Robert Le Gall', '圖盧茲', '天主教', 92, 2006, 2022, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '本篤會士；法國主教團禮儀委員會主席'),
('德尼·賈謝', 'Denis Jachiet', '圖盧茲', '天主教', 93, 2023, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任圖盧茲大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '圖盧茲' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 都爾（Tours）
-- 聖馬丁的主教座；中世紀最重要的朝聖地之一
-- ==============================
('聖加蒂安努斯', 'Saint Gatianus', '都爾', '天主教', 1, 250, 301, '逝世', '使徒傳承', '正統', 'Gallia Christiana', '都爾首任主教；傳統上由教宗克萊孟一世派遣'),
('聖馬丁', 'Saint Martin of Tours', '都爾', '天主教', 4, 371, 397, '逝世', '教會選舉', '正統', 'Gallia Christiana; Sulpicius Severus, Vita Martini', '「我是基督的士兵」——脫下半件外套給乞丐的傳說；前羅馬軍人；建立西歐最早的修道院（利奇尼亞克）；西歐修道運動之父；法蘭西最重要的守護聖人'),
('聖格列高里（都爾的格里高里）', 'Gregory of Tours', '都爾', '天主教', 19, 573, 594, '逝世', '法蘭克貴族選舉', '正統', 'Gallia Christiana; Gregory, Historia Francorum', '《法蘭克人史》（Historia Francorum）作者——法蘭克早期歷史最重要的史料；中世紀拉丁文學的代表；梅羅文加時代的見證者'),
('勒伯托', 'Adelard I', '都爾', '天主教', 30, 823, 834, '廢黜', '路易虔誠者', '正統', 'Gallia Christiana', '加洛林時代改革；投石黨（Fronde）之前另一個政治主教故事'),
('阿爾奴爾·馮·圖爾斯', 'Hardouin I', '都爾', '天主教', 36, 968, 993, '逝世', '教會傳承', '正統', 'Gallia Christiana', '卡佩王朝確立後的都爾；聖馬丁聖殿的政治化'),
('若望·德·博熱阿特', 'Jean de Beaune', '都爾', '天主教', 57, 1535, 1546, '逝世', '教宗保羅三世', '正統', 'Gallia Christiana', '法國宗教改革（加爾文主義初入法國）時期的反應'),
('赫克托爾·多里亞格', 'Vincent Jordy', '都爾', '天主教', 88, 2017, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任都爾大主教；聖馬丁誕生1700週年（2016年）後的牧養');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '都爾' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 波爾多（Bordeaux）
-- 阿基坦首府；安菊主義（Gallicanism）的根據地
-- ==============================
('聖迪爾菲烏斯', 'Saint Delphinus', '波爾多', '天主教', 9, 380, 404, '逝世', '教宗達瑪索一世', '正統', 'Gallia Christiana', '波里諾聖旁日（Paulin de Nole）的洗禮施洗者；聖安布羅斯時代的高盧教會代表'),
('聖保利努斯', 'Paulinus of Nola', '波爾多', '天主教', 10, 409, 431, '逝世（在諾拉）', '教宗英諾森一世', '正統', 'Gallia Christiana', '阿基坦最富有的貴族——變賣一切財產照顧貧苦人；後成諾拉主教；最優美的早期基督教詩人之一；聖奧古斯丁的友人'),
('讓·德盧普特', 'Bertrand de Goth (later Pope Clement V)', '波爾多', '天主教', 40, 1299, 1305, '辭職（就任教宗）', '教宗本篤八世', '正統', 'Gallia Christiana', '1305年成為教宗克萊孟五世；將教廷遷往阿維尼翁（1309）——「巴比倫之囚」的開始（見里昂條目同人物）'),
('皮里·迪阿勒特', 'Pierre de la Trau', '波爾多', '天主教', 43, 1348, 1361, '逝世（黑死病）', '教宗克萊孟六世', '正統', 'Gallia Christiana', '1348年黑死病大爆發（歐洲三分之一人口死亡）；波爾多的牧養危機'),
('弗朗索瓦·德索迪亞克', 'François de Sourdis', '波爾多', '天主教', 53, 1599, 1628, '逝世', '教宗克萊孟八世', '正統', 'Gallia Christiana', '樞機；特倫托改革推行者；與黎塞留（Richelieu）關係密切；波爾多大主教宮建設推手'),
('若望·弗朗索瓦·保羅·德若迪', 'Cardinal de Sourdis (François)', '波爾多', '天主教', 54, 1628, 1645, '逝世', '教宗烏爾班八世', '正統', 'Gallia Christiana', '樞機；黎塞留的政治競爭對手（但波爾多遠離巴黎政治漩渦）'),
('費利克斯-朱利安-讓·勒博讓蒂利', 'Victor Lucien Lécot', '波爾多', '天主教', 74, 1890, 1908, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；法國政教分離法（1905年）前的最後輝煌天主教時代'),
('讓-保羅·詹姆斯', 'Jean-Paul James', '波爾多', '天主教', 86, 2019, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任波爾多大主教；年輕一代法國主教的代表');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '波爾多' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
