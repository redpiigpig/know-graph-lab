-- ============================================================
-- 天主教大主教傳承——美洲（布宜諾斯艾利斯、紐約、芝加哥、聖保羅）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 布宜諾斯艾利斯（Buenos Aires）
-- 阿根廷首都；現任教宗方濟各曾任大主教
-- ==============================
('馬里諾·馬裡尼', 'Mariano Medrano y Cabrera', '布宜諾斯艾利斯', '天主教', 1, 1829, 1851, '逝世', '教宗庇護八世', '正統', 'Catholic Hierarchy', '布宜諾斯艾利斯首任主教（後升大主教）；阿根廷獨立（1816）後的教會重建'),
('里昂·費德里科·安扎多', 'León Federico Aneiros', '布宜諾斯艾利斯', '天主教', 4, 1873, 1894, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '首任大主教（1865年升格大主教區）；阿根廷移民潮時代的教會組織'),
('路易·科帕洛', 'Luis Copello', '布宜諾斯艾利斯', '天主教', 7, 1932, 1959, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；庇隆主義（Perón）時代；1955年庇隆政府與教會破裂後的困難局面'),
('胡安·卡洛斯·阿隆索', 'Juan Carlos Aramburu', '布宜諾斯艾利斯', '天主教', 9, 1975, 1990, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；阿根廷軍政府（1976–1983）期間；被批評對於失蹤者（desaparecidos）沉默'),
('安東尼奧·夸拉其諾', 'Antonio Quarracino', '布宜諾斯艾利斯', '天主教', 10, 1990, 1998, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；引薦豪爾赫·馬里奧·貝爾格里奧（方濟各）為輔理主教'),
('豪爾赫·馬里奧·貝爾格里奧（後為教宗方濟各）', 'Jorge Mario Bergoglio (later Pope Francis)', '布宜諾斯艾利斯', '天主教', 11, 1998, 2013, '辭職（就任教宗）', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；耶穌會士；2013年當選教宗方濟각——首位美洲裔、首位耶穌會士教宗；第一位南半球出生的教宗'),
('馬里奧·奧雷利奧·波利', 'Mario Aurelio Poli', '布宜諾斯艾利斯', '天主教', 12, 2013, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '樞機；貝爾格里奧的繼任者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '布宜諾斯艾利斯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 紐約（New York）
-- 美國最大城市；美國天主教的主要發聲地
-- ==============================
('約翰·休斯', 'John Hughes', '紐約', '天主教', 1, 1842, 1864, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '紐約首任大主教（1850年升格）；推動興建聖派翠克大教堂（St. Patrick''s Cathedral, 1858–1879）；南北戰爭期間反對紐約徵兵暴動（1863）；英裔愛爾蘭移民的靈魂人物'),
('約翰·卡迪納爾·麥克洛斯基', 'John McCloskey', '紐約', '天主教', 2, 1864, 1885, '退休', '教宗庇護九世', '正統', 'Catholic Hierarchy', '美國第一位樞機（1875年）；完成聖派翠克大教堂建造'),
('邁克爾·奧古斯丁·科里根', 'Michael Augustine Corrigan', '紐約', '天主教', 3, 1885, 1902, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '愛爾蘭裔；與麥格林神父的勞工爭議（Henry George競選市長1886）；保守派立場'),
('約翰·法利', 'John Farley', '紐約', '天主教', 4, 1902, 1918, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；一戰期間；愛爾蘭移民社區的持續整合'),
('帕特里克·海斯', 'Patrick Hayes', '紐約', '天主教', 5, 1919, 1938, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機；「窮人的樞機主教」；大蕭條期間積極慈善工作；推動天主教慈善事業組織化'),
('弗朗西斯·斯佩爾曼', 'Francis Spellman', '紐約', '天主教', 6, 1939, 1967, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；二戰、韓戰、越戰期間美國軍隊宗座行政長官（Military Vicar）；冷戰反共立場；美國最具政治影響力的樞機；「美國天主教的教宗」之稱'),
('泰倫斯·庫克', 'Terence Cooke', '紐約', '天主教', 7, 1968, 1983, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；越戰期間；反墮胎立場；列真福品進行中（「天主教的軍人樞機」）'),
('約翰·奧康納', 'John O''Connor', '紐約', '天主教', 8, 1984, 2000, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；強烈反墮胎；與紐約市長科赫和丁金斯的緊張關係；艾滋危機期間'),
('愛德華·伊根', 'Edward Egan', '紐約', '天主教', 9, 2000, 2009, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；9/11恐怖攻擊（2001）期間的精神支柱'),
('蒂莫西·多蘭', 'Timothy Dolan', '紐約', '天主教', 10, 2009, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；美國主教大會主席（2010–2013）；奧巴馬醫療改革宗教自由爭議的核心人物');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '紐約' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 芝加哥（Chicago）
-- 美國最大天主教教區之一；波蘭裔和拉丁裔眾多
-- ==============================
('威廉·夸爾特', 'William Quarter', '芝加哥', '天主教', 1, 1844, 1848, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '芝加哥首任主教；愛爾蘭裔；移民時代教會建設'),
('詹姆斯·奎格利', 'James Quigley', '芝加哥', '天主教', 5, 1903, 1915, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '首任芝加哥大主教（1880年升大主教區）不是，實際是1913年），鋼鐵工人移民的牧養'),
('喬治·明德勒因', 'George Mundelein', '芝加哥', '天主教', 6, 1915, 1939, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機；小羅斯福新政的天主教支持者；1926年主辦國際聖體大會（芝加哥）；公開批評希特勒（1937）——美國首位樞機公開批評納粹'),
('塞繆爾·斯特里奇', 'Samuel Stritch', '芝加哥', '天主教', 7, 1940, 1958, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；黑人天主教徒的融合推動者；1958年任命為羅馬教廷職務後逝世'),
('阿爾伯特·邁耶', 'Albert Meyer', '芝加哥', '天主教', 8, 1958, 1965, '逝世', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議積極參與者；民權運動支持者'),
('約翰·柯定', 'John Cody', '芝加哥', '天主教', 9, 1965, 1982, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；教區財務管理爭議'),
('約瑟夫·伯納丁', 'Joseph Bernardin', '芝加哥', '天主教', 10, 1982, 1996, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；美國主教大會主席（1974–1977）；「共同基礎」（Common Ground）倡議——推動天主教內部不同派系對話；《一致的生命倫理》（Seamless Garment）思想；面對癌症末期的平靜典範'),
('弗朗西斯·喬治', 'Francis George', '芝加哥', '天主教', 11, 1997, 2014, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；方濟各重整（Oblates of Mary Immaculate）；保守立場；性醜聞問題'),
('布萊斯·庫皮奇', 'Blase Cupich', '芝加哥', '天主教', 12, 2014, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '樞機；方濟각教宗的盟友；進步立場；移民保護政策倡導者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '芝加哥' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 聖保羅（São Paulo）
-- 巴西最大城市；拉美最大天主教城市之一
-- ==============================
('若阿金·阿紹維爾·費雷拉·布羅加', 'Joaquim Arcoverde de Albuquerque Cavalcanti', '聖保羅', '天主教', 1, 1894, 1897, '轉任', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '聖保羅首任主教（1745年設立教區）的現代主教；後轉任里約熱內盧——巴西第一位樞機'),
('杜阿爾特·勒奧波爾多·埃席爾瓦', 'Duarte Leopoldo e Silva', '聖保羅', '天主教', 2, 1907, 1938, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '首任大主教（1908年升格）；巴西共和國時代教會重建'),
('若阿金·阿爾維斯·科雷亞', 'Carlos Carmelo de Vasconcellos Motta', '聖保羅', '天主教', 3, 1944, 1964, '轉任', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議前的巴西天主教發展'),
('阿格努斯·卡塞姆', 'Agnelo Rossi', '聖保羅', '天主教', 4, 1964, 1970, '轉任', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；後轉任羅馬（聖座人員部）'),
('保羅·埃瓦里斯托·阿恩斯', 'Paulo Evaristo Arns', '聖保羅', '天主教', 5, 1970, 1998, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；巴西軍事獨裁（1964–1985）時代最勇敢的人權捍衛者；「巴西人民的監護人」；教區分拆引發爭議（梵蒂岡削減其龐大教區）'),
('克勞迪奧·洪布雷托·薛雷爾', 'Cláudio Hummes', '聖保羅', '天主教', 6, 1998, 2006, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後任聖座神職部部長；2013年坐在貝爾格里奧旁、低語「不要忘記窮人」——貝爾格里奧後選擇「方濟각」之名的直接原因'),
('奧迪洛·帕德羅·謝雷爾', 'Odilo Pedro Scherer', '聖保羅', '天主教', 7, 2007, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；德裔巴西人；保守路線；2013年曾被視為可能的教宗候選人');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '聖保羅' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 里約熱內盧（Rio de Janeiro）
-- 巴西舊首都；首個巴西大主教區
-- ==============================
('若阿金·阿爾科韋爾德', 'Joaquim Arcoverde de Albuquerque Cavalcanti', '里約熱內盧', '天主教', 6, 1897, 1930, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；巴西第一位樞機（1905年）；里約熱內盧首任大主教（1892年升格）；共和國時代教會-國家關係'),
('塞巴斯蒂昂·萊梅', 'Sebastião Leme da Silveira Cintra', '里約熱內盧', '天主教', 7, 1930, 1942, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機；科帕卡巴納海邊的基督像（Cristo Redentor）主持落成典禮（1931）；推動巴西天主教復興；社會問題關注者'),
('賈伊梅·德巴羅斯·卡馬拉', 'Jaime de Barros Câmara', '里約熱內盧', '天主教', 8, 1943, 1971, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議參與者；保守立場'),
('奧盧·洛沙達', 'Eugênio Sales', '里約熱內盧', '天主教', 9, 1971, 2001, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；軍政府時代不同於阿恩斯的溫和路線'),
('埃烏塞比奧·斯卡蘭班扎尼', 'Eusébio Oscar Scheid', '里約熱內盧', '天主教', 10, 2001, 2009, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；2002年世界青年節（里約）的主辦人'),
('奧拉尼·喬奧·滕佩斯特', 'Orani João Tempesta', '里約熱內盧', '天主教', 11, 2009, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；2013年世界青年節（WYD Rio）——教宗方濟각首次國際出訪；里約奧運（2016）宗教活動主持');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '里約熱內盧' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
