-- ============================================================
-- 天主教大主教傳承——拉丁美洲（波哥大、聖地亞哥、蒙特利爾、聖多明哥）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 波哥大（Bogotá / Santa Fe de Bogotá）
-- 哥倫比亞首都；1564年設立大主教區
-- ==============================
('路易斯·薩帕塔·德·卡爾德納斯', 'Luis Zapata de Cárdenas', '波哥大', '天主教', 1, 1571, 1590, '逝世', '教宗庇護五世', '正統', 'Catholic Hierarchy', '方濟各會士；首任大主教（1564年設立大主教區）；推動印第安人牧靈教育；反對恩科米恩達（encomienda）剝削制度'),
('巴托洛梅·洛沃·格雷羅', 'Bartolomé Lobo Guerrero', '波哥大', '天主教', 3, 1599, 1609, '轉任', '教宗克萊孟八世', '正統', 'Catholic Hierarchy', '宗教裁判所在新格拉納達的組織化；後轉任利馬'),
('費爾南多·阿里亞斯·德烏加爾特', 'Fernando Arias de Ugarte', '波哥大', '天主教', 4, 1618, 1625, '轉任', '教宗保羅五世', '正統', 'Catholic Hierarchy', '先後任波哥大、查爾卡斯、利馬大主教；西屬美洲最有影響力的主教之一'),
('弗雷亞斯·曼努埃爾·索薩·帕迪利亞', 'Manuel José Mosquera', '波哥大', '天主教', 18, 1835, 1853, '流亡', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '哥倫比亞獨立後最重要的大主教；自由主義革命期間被驅逐（1853）；教會財產世俗化的受害者'),
('伊格納西奧·安托利內斯', 'Bernardo Herrera Restrepo', '波哥大', '天主教', 22, 1891, 1928, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機（1914年）；哥倫比亞首位樞機；1887年政教協議的遺澤；再生黨（Regeneración）天主教共和國的象徵'),
('伊斯馬埃爾·佩爾多莫', 'Ismael Perdomo', '波哥大', '天主教', 23, 1928, 1950, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；保守黨時代與自由黨宗教衝突（La Violencia 1948前後）'),
('克里桑托·盧克·桑切斯', 'Crisanto Luque Sánchez', '波哥大', '天主教', 24, 1950, 1959, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；哥倫比亞第一位本土樞機（1953年）；軍政府羅哈斯·皮尼利亞（1953–1957）期間'),
('阿方索·洛佩斯·特魯希略', 'Alfonso López Trujillo', '波哥大', '天主教', 26, 1979, 1994, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；解放神學的主要批評者；後任聖座家庭委員會主席（1990–2008）；反避孕、反安慰套的強硬立場'),
('佩德羅·魯維亞諾·薩恩斯', 'Pedro Rubiano Sáenz', '波哥大', '天主教', 27, 1994, 2010, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；哥倫比亞內戰（FARC/ELN）期間的和平調停者'),
('魯本·薩拉薩爾·戈梅斯', 'Rubén Salazar Gómez', '波哥大', '天主教', 28, 2010, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；拉美主教大會（CELAM）主席；哥倫比亞和平協議（2016年FARC和談）的教會支持');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '波哥大' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 聖地亞哥（Santiago de Chile）
-- 智利首都大主教區
-- ==============================
('羅德里格·貢薩雷斯·馬莫萊霍', 'Rodrigo González Marmolejo', '聖地亞哥', '天主教', 1, 1561, 1564, '逝世', '教宗庇護四世', '正統', 'Catholic Hierarchy', '智利首任主教（1561年設立）；征服者時代'),
('貢薩洛·德奧坎波', 'Gonzalo de Ocampo', '聖地亞哥', '天主教', 6, 1650, 1668, '逝世', '教宗英諾森十世', '正統', 'Catholic Hierarchy', '聖地亞哥地震（1647）後的重建牧養'),
('曼努埃爾·維拉洛博斯', 'Manuel Vicuña Larraín', '聖地亞哥', '天主教', 16, 1832, 1843, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '智利獨立後首位本土大主教（1840年升格大主教區）；教育改革推動者'),
('拉斐爾·瓦倫廷·巴萊納達斯', 'Rafael Valentín Valdivieso', '聖地亞哥', '天主教', 17, 1845, 1878, '逝世', '教宗格列高里十六世', '正統', 'Catholic Hierarchy', '智利天主教最長任大主教之一；自由派政府衝突；捍衛教育和民法中的教會地位'),
('後胡里奧·多尼索·費爾南德斯', 'Crescente Errázuriz Valdivieso', '聖地亞哥', '天主教', 20, 1919, 1931, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機；智利首位樞機；多明我會士；政教分離（1925年智利憲法）和平談判者'),
('若塞·瑪麗亞·卡若·薩拉維亞', 'José María Caro Rodríguez', '聖地亞哥', '天主教', 21, 1939, 1958, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；智利第二位樞機；勞工議題；後被宣福進行中'),
('拉烏爾·席爾瓦·恩里奎斯', 'Raúl Silva Henríquez', '聖地亞哥', '天主教', 22, 1961, 1983, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；皮諾切特軍政府（1973–1990）的主要批評者；創立「合作委員會」（Vicaría de la Solidaridad）記錄人權侵害——為反獨裁最重要的制度性抵抗之一'),
('胡安·弗朗西斯科·弗雷斯諾·拉拉因', 'Juan Francisco Fresno Larraín', '聖地亞哥', '天主教', 23, 1983, 1990, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；過渡民主的調停者；「國家協議」（Acuerdo Nacional, 1985）推動者'),
('卡洛斯·奧維埃多·卡瓦達', 'Carlos Oviedo Cavada', '聖地亞哥', '天主教', 24, 1990, 1998, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後皮諾切特時代；奧古斯托·皮諾切特英國逮捕事件（1998）的教會立場'),
('弗朗西斯科·哈維爾·埃拉蘇里斯·奧薩', 'Francisco Javier Errázuriz Ossa', '聖地亞哥', '天主教', 25, 1998, 2010, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；教宗方濟각C9成員；後因智利教會性醜聞退出顧問委員'),
('里卡多·埃扎蒂·安德雷洛', 'Ricardo Ezzati Andrello', '聖地亞哥', '天主教', 26, 2010, 2019, '辭職', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；智利天主教性醜聞（2018）核心人物；辭職；2019年被訴'),
('塞爾希奧·埃爾南德斯', 'Celestino Aós Braco', '聖地亞哥', '天主教', 27, 2019, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '嘉布遣方濟각會士；危機後接手；智利教會重建時期');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '聖地亞哥' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 蒙特利爾（Montréal）
-- 加拿大法語區最大城市；北美洲重要天主教中心
-- ==============================
('伊格納斯·布爾熱', 'Ignace Bourget', '蒙特利爾', '天主教', 2, 1840, 1876, '退休', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '蒙特利爾最重要的大主教；超過百所教堂建設；蒙特利爾聖若瑟聖堂（Saint Joseph''s Oratory）前身的奠定；引入多個修道會；法裔加拿大天主教認同的奠基者'),
('埃德華·查爾斯·法伯', 'Édouard-Charles Fabre', '蒙特利爾', '天主教', 3, 1876, 1896, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '首任大主教（1886年升格）；蒙特利爾大學建立（1878年）'),
('保羅-埃米爾·萊熱', 'Paul-Émile Léger', '蒙特利爾', '天主教', 7, 1950, 1967, '辭職（赴非洲服務）', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議積極參與者；1967年辭職前往非洲（喀麥隆）服務痲瘋病人——罕見的主動棄位服務行動'),
('若望·吉格賴', 'Jean-Claude Turcotte', '蒙特利爾', '天主教', 9, 1990, 2012, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；魁北克靜默革命（Révolution tranquille）後宗教式微時代的牧養；多元文化移民融合'),
('克里斯蒂安·勒皮納', 'Christian Lépine', '蒙特利爾', '天主教', 10, 2012, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '現任大主教；魁北克宗教自由與世俗主義辯論');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '蒙特利爾' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 聖多明哥（Santo Domingo）
-- 美洲最古老的天主教大主教座（1511年）
-- ==============================
('亞歷山德羅·傑拉爾迪尼', 'Alessandro Geraldini', '聖多明哥', '天主教', 1, 1516, 1524, '逝世', '教宗利奧十世', '正統', 'Catholic Hierarchy', '新世界第一位常駐大主教；曾為哥倫布遠航計劃辯護；聖多明哥大教堂（建於1512年）的完善推動者'),
('阿隆索·德富恩馬約爾', 'Alonso de Fuenmayor', '聖多明哥', '天主教', 8, 1539, 1554, '逝世', '教宗保羅三世', '正統', 'Catholic Hierarchy', '海地島殖民地的天主教鞏固；印第安人問題（拉斯·卡薩斯爭論的背景）'),
('卡洛斯·諾瓦爾·達伊', 'Carlos de la Torre y Espinosa', '聖多明哥', '天主教', 20, 1920, 1935, '轉任', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '多明尼加共和國現代化時代'),
('若澤·弗朗西斯科·皮塔烏', 'Octavio Antonio Beras Rojas', '聖多明哥', '天主教', 24, 1961, 1981, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；特魯希略獨裁政府（1930–1961）結束後；1984年若望保祿二世訪問聖多明哥'),
('尼古拉斯·德赫蘇斯·洛佩斯·羅德里格斯', 'Nicolás de Jesús López Rodríguez', '聖多明哥', '天主教', 25, 1981, 2019, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；在任38年；1992年哥倫布發現美洲五百週年紀念暨世界青年節（聖多明哥）主辦；多次爭議性言論（歧視同性戀）'),
('弗朗西斯科·霍奎斯·費羅', 'Francisco Ozoria Acosta', '聖多明哥', '天主教', 26, 2019, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任大主教；多明尼加天主教現代化推動');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '聖多明哥' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
