-- ============================================================
-- 天主教主教座——歐洲補充（巴黎、蘭斯、科隆、美因茨、漢堡、威尼斯等）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, founded_year, abolished_year, status,
   current_patriarch, location, notes, sources)
VALUES

-- 法國
('巴黎天主教大主教區', 'Archdiocese of Paris', '巴黎', '天主教', '天主教', '羅馬禮',
 250, NULL, 'current', 'Laurent Ulrich（2022–）', '法國巴黎',
 '聖德尼（~250）為第一任主教；1622年升為總主教區；聖母院所在地；法國大革命後多位大主教遇難', 'Catholic Hierarchy; GCatholic'),

('蘭斯天主教大主教區', 'Archdiocese of Reims', '蘭斯', '天主教', '天主教', '羅馬禮',
 260, NULL, 'current', 'Éric de Moulins-Beaufort（2018–）', '法國蘭斯',
 '法蘭克王國及法蘭西王國歷代國王加冕地；聖雷米（459–533）為克洛維一世施洗（496）；日爾貝（991–998）後成教宗西爾維斯特二世', 'Catholic Hierarchy; GCatholic'),

-- 德國
('科隆天主教大主教區', 'Archdiocese of Cologne', '科隆', '天主教', '天主教', '羅馬禮',
 313, NULL, 'current', 'Rainer Maria Woelki（2014–）', '德國科隆',
 '德國最古老主教區之一；科隆大教堂藏有東方三博士遺物；歷代大主教為神聖羅馬帝國七大選侯之一', 'Catholic Hierarchy; GCatholic'),

('美因茨天主教大主教區', 'Archdiocese of Mainz', '美因茨', '天主教', '天主教', '羅馬禮',
 346, NULL, 'current', 'Peter Kohlgraf（2017–）', '德國美因茨',
 '德意志首席大主教（Primas Germaniae）；聖卜尼法斯為傳統守護聖人；歷代大主教為帝國選侯；古騰堡印刷術發源地', 'Catholic Hierarchy; GCatholic'),

('漢堡天主教大主教區', 'Archdiocese of Hamburg', '漢堡', '天主教', '天主教', '羅馬禮',
 831, NULL, 'current', 'Stefan Heße（2015–）', '德國漢堡',
 '831年為北歐傳教而設；安斯加（Ansgar）為第一任主教；848年合併為漢堡-不萊梅大主教區；1994年重新獨立', 'Catholic Hierarchy; GCatholic'),

-- 義大利
('威尼斯天主教宗主教區', 'Patriarchate of Venice', '威尼斯', '天主教', '天主教', '羅馬禮',
 775, NULL, 'current', 'Francesco Moraglia（2012–）', '義大利威尼斯',
 '1451年設立宗主教區（儀典性頭銜）；教宗庇護十世（薩托）、若望二十三世（龍卡利）、若望保祿一世均曾任威尼斯宗主教', 'Catholic Hierarchy; GCatholic'),

('那不勒斯天主教大主教區', 'Archdiocese of Naples', '那不勒斯', '天主教', '天主教', '羅馬禮',
 300, NULL, 'current', 'Domenico Battaglia（2020–）', '義大利那不勒斯',
 '義大利南部首席大主教座；聖真納羅（Gennaro）為主保聖人；諾曼王國、兩西西里王國首都', 'Catholic Hierarchy; GCatholic'),

('佛羅倫薩天主教大主教區', 'Archdiocese of Florence', '佛羅倫薩', '天主教', '天主教', '羅馬禮',
 313, NULL, 'current', 'Giorgio Betori（2008–）', '義大利佛羅倫薩',
 '文藝復興中心；1439年佛羅倫薩公會議嘗試東西方合一；聖安東尼諾（1446–1459）為著名大主教', 'Catholic Hierarchy; GCatholic'),

('波隆那天主教大主教區', 'Archdiocese of Bologna', '波隆那', '天主教', '天主教', '羅馬禮',
 300, NULL, 'current', 'Matteo Zuppi（2015–）', '義大利波隆那',
 '最古老大學所在地；多位大主教後任教宗；蘭伯托尼（Lambertini）任大主教後為本篤十四世（1740–1758）', 'Catholic Hierarchy; GCatholic'),

-- 葡萄牙
('布拉加天主教大主教區', 'Archdiocese of Braga', '布拉加', '天主教', '天主教', '羅馬禮',
 45, NULL, 'current', 'José Tolentino Calaça de Mendonça（2023–）', '葡萄牙布拉加',
 '傳說為使徒彼得的弟子佩多（Pedro de Rates）所創；葡萄牙最古老的主教座；歷史上的葡萄牙首席大主教', 'Catholic Hierarchy; GCatholic'),

('里斯本天主教宗主教區', 'Patriarchate of Lisbon', '里斯本', '天主教', '天主教', '羅馬禮',
 1150, NULL, 'current', 'Manuel Clemente（2013–）', '葡萄牙里斯本',
 '1150年自聖塔倫主教遷至里斯本；1716年升格為宗主教區（儀典性）；葡萄牙首都', 'Catholic Hierarchy; GCatholic'),

-- 比利時
('梅赫倫-布魯塞爾天主教大主教區', 'Archdiocese of Mechelen-Brussels', '梅赫倫-布魯塞爾', '天主教', '天主教', '羅馬禮',
 1559, NULL, 'current', 'Luc Terlinden（2024–）', '比利時梅赫倫',
 '比利時首席大主教；1559年設立；梅西爾樞機（1907–1926）為比利時民族英雄；2010年改名加入布魯塞爾', 'Catholic Hierarchy; GCatholic'),

-- 荷蘭
('烏得勒支天主教大主教區', 'Archdiocese of Utrecht (Catholic)', '烏得勒支（天主教）', '天主教', '天主教', '羅馬禮',
 1853, NULL, 'current', 'Willem Jacobus Eijk（2008–）', '荷蘭烏得勒支',
 '1853年恢復荷蘭教會位階；與老公教教會（1724年分裂）共存於同一城市；首任大主教宗薩勒塞（Zwijsen）', 'Catholic Hierarchy; GCatholic');
