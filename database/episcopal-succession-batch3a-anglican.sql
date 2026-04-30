-- ============================================================
-- 聖公宗及信義宗主教繼承列表——第三批 A
-- Anglican & Lutheran Episcopal Successions — Batch 3A
-- 涵蓋：亞歷山卓、中非、南蘇丹、蘇丹、蒲隆地、盧安達、
--        北美、南美南錐、古巴、西印度群島、巴西、墨西哥、
--        紐西蘭、巴紐、美拉尼西亞、印度洋、耶路撒冷中東、
--        北印度、南印度、孟加拉、巴基斯坦、錫蘭、
--        東南亞、菲律賓、緬甸、塔林（愛沙尼亞信義會）、里加（拉脫維亞信義會）
-- ============================================================

-- ============================================================
-- 1. 亞歷山卓聖公宗（Anglican Province of Alexandria）
--    前身：埃及暨蘇丹教區（1920–1945）、埃及教區（1947–2020）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('盧埃林·格文', 'Llewellyn Gwynne', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 1, 1920, 1946, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', '首任埃及暨蘇丹教區主教；威爾斯籍傳教士'),
('傑弗里·艾倫', 'Geoffrey Allen', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 2, 1947, 1952, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', '1945年教區一分為二後首任埃及教區主教'),
('法蘭西斯·強斯頓', 'Francis Johnston', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 3, 1952, 1958, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', NULL),
('肯尼斯·克拉格', 'Kenneth Cragg', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 4, 1969, 1974, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', '著名伊斯蘭神學家'),
('伊沙克·穆薩德', 'Ishaq Musaad', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 5, 1974, 1984, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', NULL),
('蓋斯·阿卜杜·馬利克', 'Ghais Abdel Malik', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 6, 1985, 2000, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria', '亦任耶路撒冷及中東聖公宗主席（1995–2000）'),
('穆尼爾·安尼斯', 'Mouneer Anis', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 7, 2000, 2021, '退休', '正統', 'Wikipedia: Episcopal/Anglican Province of Alexandria; Anglican News 2021', '2020年6月29日升格為省份首任大主教；2021年退休'),
('薩米·法齊', 'Samy Fawzy', '亞歷山卓聖公宗', '亞歷山卓聖公宗', 8, 2021, NULL, NULL, '正統', 'Anglican News 2021', '現任亞歷山卓大主教及埃及教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '亞歷山卓聖公宗' AND church = '亞歷山卓聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 2. 中非聖公宗（Church of the Province of Central Africa）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('愛德華·佩吉特', 'Edward Paget', '中非聖公宗', '中非聖公宗', 1, 1954, 1956, '調任', '正統', 'Wikipedia: Archbishop of Central Africa', '馬紹納蘭教區主教；首任都主教'),
('詹姆斯·休斯', 'James Hughes', '中非聖公宗', '中非聖公宗', 2, 1956, 1961, '調任', '正統', 'Wikipedia: Archbishop of Central Africa', '調任千里達及多巴哥'),
('奧利弗·格林-威爾金森', 'Oliver Green-Wilkinson', '中非聖公宗', '中非聖公宗', 3, 1961, 1969, '逝世', '正統', 'Wikipedia: Archbishop of Central Africa', '在任期間去世'),
('唐納德·阿登', 'Donald Arden', '中非聖公宗', '中非聖公宗', 4, 1969, 1980, '退休', '正統', 'Wikipedia: Archbishop of Central Africa', '退休後返回英國'),
('沃爾特·科索·馬庫盧', 'Walter Khotso Makhulu', '中非聖公宗', '中非聖公宗', 5, 1980, 2001, '退休', '正統', 'Wikipedia: Archbishop of Central Africa', '亦任博茨瓦納主教至1988年；著名反種族隔離活動家'),
('伯納德·馬蘭戈', 'Bernard Malango', '中非聖公宗', '中非聖公宗', 6, 2001, 2006, '辭職', '正統', 'Wikipedia: Archbishop of Central Africa', '因省內爭議辭職；2007年正式離任'),
('艾伯特·查馬', 'Albert Chama', '中非聖公宗', '中非聖公宗', 7, 2011, NULL, NULL, '正統', 'Wikipedia: Archbishop of Central Africa; Anglican Communion', '2011年3月20日就任；此前2007–2010年任代理大主教；盧薩卡教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '中非聖公宗' AND church = '中非聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 3. 南蘇丹聖公宗（Episcopal Church of South Sudan）
--    2011年自蘇丹聖公宗分立
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('埃利納納·恩加拉穆', 'Elinana Ja''bi Ngalamu', '南蘇丹聖公宗', '南蘇丹聖公宗', 1, 1976, 1988, '退休', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan; DACB', '1976年10月11日由坎特伯里大主教唐納德·科根就任首任大主教；1992年在喀土穆逝世'),
('本傑明·瓦尼·尤古蘇克', 'Benjamin Wani Yugusuk', '南蘇丹聖公宗', '南蘇丹聖公宗', 2, 1988, 1998, '退休', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '第二任大主教'),
('約瑟夫·馬羅納', 'Joseph Marona', '南蘇丹聖公宗', '南蘇丹聖公宗', 3, 2000, 2007, '逝世', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '任內去世'),
('丹尼爾·登·布爾', 'Daniel Deng Bul', '南蘇丹聖公宗', '南蘇丹聖公宗', 4, 2008, 2018, '退休', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '主導2011年南蘇丹獨立省份分立；服務逾十年後退休'),
('賈斯廷·巴迪·阿拉馬', 'Justin Badi Arama', '南蘇丹聖公宗', '南蘇丹聖公宗', 5, 2018, NULL, NULL, '正統', 'Wikipedia: Justin Badi Arama; anglicannews.org 2018', '2018年1月20日當選、4月22日就任；第五任大主教；前馬里迪教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '南蘇丹聖公宗' AND church = '南蘇丹聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 4. 蘇丹聖公宗（Episcopal Church of Sudan）
--    1976年建省；2011年南蘇丹分立後縮小
--    注：前四任同時列入南蘇丹聖公宗，此處以蘇丹教會延續記錄
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('埃利納納·恩加拉穆', 'Elinana Ja''bi Ngalamu', '蘇丹聖公宗', '蘇丹聖公宗', 1, 1976, 1988, '退休', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan; DACB', '首任大主教；坎特伯里大主教科根親自就任'),
('本傑明·瓦尼·尤古蘇克', 'Benjamin Wani Yugusuk', '蘇丹聖公宗', '蘇丹聖公宗', 2, 1988, 1998, '退休', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '第二任大主教'),
('約瑟夫·馬羅納', 'Joseph Marona', '蘇丹聖公宗', '蘇丹聖公宗', 3, 2000, 2007, '逝世', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '任內去世'),
('丹尼爾·登·布爾', 'Daniel Deng Bul', '蘇丹聖公宗', '蘇丹聖公宗', 4, 2008, 2011, '調任', '正統', 'Wikipedia: Province of the Episcopal Church of South Sudan', '2011年南蘇丹建立獨立省份後轉任南蘇丹聖公宗大主教至2018年')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蘇丹聖公宗' AND church = '蘇丹聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 5. 蒲隆地聖公宗（Anglican Church of Burundi）
--    1992年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('塞繆爾·辛達穆卡', 'Samuel Sindamuka', '蒲隆地聖公宗', '蒲隆地聖公宗', 1, 1992, 1998, '退休', '正統', 'Wikipedia: Province of the Anglican Church of Burundi', '首任大主教；此前任盧安達、蒲隆地及博加-扎伊爾教會首牧'),
('塞繆爾·恩達伊森加', 'Samuel Ndayisenga', '蒲隆地聖公宗', '蒲隆地聖公宗', 2, 1998, 2005, '退休', '正統', 'Wikipedia: Province of the Anglican Church of Burundi', '第二任大主教'),
('伯納德·恩塔霍圖里', 'Bernard Ntahoturi', '蒲隆地聖公宗', '蒲隆地聖公宗', 3, 2005, 2016, '退休', '正統', 'Wikipedia: Bernard Ntahoturi', '第三任大主教；2016年後赴任安德烈會中心總監'),
('馬丁·布萊斯·尼亞博霍', 'Martin Blaise Nyaboho', '蒲隆地聖公宗', '蒲隆地聖公宗', 4, 2016, 2021, '退休', '正統', 'Wikipedia: Martin Nyaboho', '第四任大主教'),
('西克斯貝特·馬庫米', 'Sixbert Macumi', '蒲隆地聖公宗', '蒲隆地聖公宗', 5, 2021, NULL, NULL, '正統', 'Episcopal News Service 2021; Anglican Church of Burundi website', '2021年5月24日當選、8月21日就任；第五任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蒲隆地聖公宗' AND church = '蒲隆地聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 6. 盧安達聖公宗（Anglican Church of Rwanda）
--    1992年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('奧古斯丁·恩沙米希戈', 'Augustin Nshamihigo', '盧安達聖公宗', '盧安達聖公宗', 1, 1992, 1998, '退休', '正統', 'Wikipedia: Anglican Church of Rwanda', '1992年6月7日在基加利阿馬霍羅體育場就任首任大主教'),
('伊曼紐爾·科利尼', 'Emmanuel Kolini', '盧安達聖公宗', '盧安達聖公宗', 2, 1998, 2011, '退休', '正統', 'Wikipedia: Emmanuel Kolini', '第二任大主教；積極參與全球保守聖公宗運動'),
('奧納福雷·魯瓦傑', 'Onesphore Rwaje', '盧安達聖公宗', '盧安達聖公宗', 3, 2011, 2018, '退休', '正統', 'Wikipedia: Anglican Church of Rwanda', '2011年1月23日就任第三任大主教'),
('洛朗·姆班達', 'Laurent Mbanda', '盧安達聖公宗', '盧安達聖公宗', 4, 2018, 2025, '退休', '正統', 'Wikipedia: Laurent Mbanda; Anglican News 2018', '2018年1月17日當選、6月10日就任；2023年當選GAFCON首牧委員會主席；2025年10月退休')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '盧安達聖公宗' AND church = '盧安達聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 7. 北美聖公宗（Anglican Church in North America, ACNA）
--    2009年建立，為保守派分裂自美國聖公宗
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('羅伯特·鄧肯', 'Robert William Duncan', '北美聖公宗', '北美聖公宗教會', 1, 2009, 2014, '退休', '正統', 'Wikipedia: Foley Beach; ACNA website', '首任大主教；2009年6月就任；前匹茲堡教區主教'),
('福利·比奇', 'Foley Beach', '北美聖公宗', '北美聖公宗教會', 2, 2014, 2024, '退休', '正統', 'Wikipedia: Foley Beach', '2014年6月21日當選、10月9日就任；服務兩屆五年任期'),
('史蒂夫·伍德', 'Stephen D. Wood', '北美聖公宗', '北美聖公宗教會', 3, 2024, NULL, NULL, '正統', 'The Living Church 2024; Gulf Atlantic Diocese 2024', '2024年6月22日當選；第三任大主教；前墨灣大西洋教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '北美聖公宗' AND church = '北美聖公宗教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 8. 南美南錐聖公宗（Anglican Church of the Southern Cone of America）
--    1981年建省；2014年更名南美聖公宗
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('理查德·卡茨', 'Richard Cutts', '南美南錐聖公宗', '南錐聖公宗', 1, 1981, 1989, '退休', '正統', 'Wikipedia: Richard Cutts; Anglican Church of South America', '1981年建省時首任首牧；阿根廷教區主教（1975–1989）'),
('大衛·利克', 'David Leake', '南美南錐聖公宗', '南錐聖公宗', 2, 1989, 2001, '退休', '正統', 'Wikipedia: David Leake; Anglican Church of South America', '首位南美洲本地人出任首牧；阿根廷教區主教'),
('格雷戈里·維納布爾斯', 'Gregory Venables', '南美南錐聖公宗', '南錐聖公宗', 3, 2001, 2010, '退休', '正統', 'Wikipedia: Gregory Venables; Anglican Church of South America', '英籍主教；積極支持全球聖公宗保守運動'),
('赫克托·「蒂托」·薩瓦拉', 'Héctor ''Tito'' Zavala', '南美南錐聖公宗', '南錐聖公宗', 4, 2010, 2016, '退休', '正統', 'Anglican Journal; Episcopal Cafe 2010', '2010年11月當選；智利教區主教；第二位南美洲本地人出任首牧'),
('格雷戈里·維納布爾斯', 'Gregory Venables', '南美南錐聖公宗', '南錐聖公宗', 5, 2016, 2020, '退休', '正統', 'Wikipedia: Gregory Venables; Anglican News 2016', '二度出任首牧；2016年省級大會再選'),
('布萊恩·威廉斯', 'Brian Williams', '南美南錐聖公宗', '南錐聖公宗', 6, 2020, NULL, NULL, '正統', 'Wikipedia: Anglican Church of South America', '現任首牧；阿根廷教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '南美南錐聖公宗' AND church = '南錐聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 9. 古巴聖公宗（Episcopal Church of Cuba）
--    1966年起為額外省教區
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('羅穆阿爾多·岡薩雷斯', 'Romualdo González Agüeros', '古巴聖公宗', '古巴聖公宗', 1, 1961, 1966, '調任', '正統', 'Wikipedia: Episcopal Church of Cuba', '最後一位歸屬美國聖公宗的古巴主教；1966年與美國聖公宗切割'),
('何塞·奧古斯丁·岡薩雷斯', 'José Agustín González', '古巴聖公宗', '古巴聖公宗', 2, 1967, 1982, '退休', '正統', 'Wikipedia: Episcopal Church of Cuba', '首任古巴本地出身主教；古巴獨立後首任主教'),
('埃米利奧·埃爾南德斯', 'Emilio Hernández', '古巴聖公宗', '古巴聖公宗', 3, 1982, 1992, '退休', '正統', 'Wikipedia: Episcopal Church of Cuba', NULL),
('豪爾赫·佩雷拉·烏爾塔多', 'Jorge Perera Hurtado', '古巴聖公宗', '古巴聖公宗', 4, 1994, 2003, '退休', '正統', 'Wikipedia: Episcopal Church of Cuba', NULL),
('格里塞爾達·德爾加多·德爾·卡皮奧', 'Griselda Delgado del Carpio', '古巴聖公宗', '古巴聖公宗', 5, 2010, 2023, '退休', '正統', 'Wikipedia: Episcopal Church of Cuba', '拉丁美洲首位女性主教'),
('天使·里維拉', 'Angel Rivera', '古巴聖公宗', '古巴聖公宗', 6, 2025, NULL, NULL, '正統', 'Wikipedia: Episcopal Church of Cuba', '2025年就任；古巴教會重返美國聖公宗後首任主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '古巴聖公宗' AND church = '古巴聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 10. 西印度群島聖公宗（Church in the Province of the West Indies）
--     1883年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('威廉·珀西·奧斯丁', 'William Piercy Austin', '西印度群島聖公宗', '西印度群島聖公宗', 1, 1884, 1891, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '首任首牧（Primate）；圭亞那主教'),
('埃諾斯·納托爾', 'Enos Nuttall', '西印度群島聖公宗', '西印度群島聖公宗', 2, 1892, 1915, '逝世', '正統', 'Wikipedia: Archbishop of the West Indies', '1897年稱號改為大主教；牙買加主教；任內去世'),
('愛德華·帕里', 'Edward Parry', '西印度群島聖公宗', '西印度群島聖公宗', 3, 1916, 1921, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '圭亞那主教'),
('愛德華·哈特森', 'Edward Hutson', '西印度群島聖公宗', '西印度群島聖公宗', 4, 1921, 1936, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '安地卡主教'),
('愛德華·亞瑟·鄧恩', 'Edward Arthur Dunn', '西印度群島聖公宗', '西印度群島聖公宗', 5, 1936, 1943, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '宏都拉斯主教'),
('亞瑟·亨利·安斯蒂', 'Arthur Henry Anstey', '西印度群島聖公宗', '西印度群島聖公宗', 6, 1943, 1945, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '千里達主教'),
('威廉·喬治·哈迪', 'William George Hardie', '西印度群島聖公宗', '西印度群島聖公宗', 7, 1945, 1950, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '牙買加主教'),
('阿蘭·約翰·奈特', 'Alan John Knight', '西印度群島聖公宗', '西印度群島聖公宗', 8, 1951, 1979, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '圭亞那主教；任期長達28年'),
('喬治·卡斯伯特·曼寧·伍德羅夫', 'George Cuthbert Manning Woodroffe', '西印度群島聖公宗', '西印度群島聖公宗', 9, 1979, 1986, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '向風群島主教'),
('奧蘭多·烏加姆·林賽', 'Orland Ugham Lindsay', '西印度群島聖公宗', '西印度群島聖公宗', 10, 1986, 1996, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '東北加勒比海及阿魯巴（前稱安地卡）主教'),
('德雷克塞爾·威靈頓·戈麥斯', 'Drexel Wellington Gomez', '西印度群島聖公宗', '西印度群島聖公宗', 11, 1996, 2009, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '巴哈馬主教；積極參與全球聖公宗保守運動'),
('約翰·沃爾德·鄧洛普·霍爾德', 'John Walder Dunlop Holder', '西印度群島聖公宗', '西印度群島聖公宗', 12, 2009, 2018, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '巴貝多主教'),
('霍華德·格雷戈里', 'Howard Gregory', '西印度群島聖公宗', '西印度群島聖公宗', 13, 2019, 2024, '退休', '正統', 'Wikipedia: Archbishop of the West Indies', '牙買加主教'),
('菲利普·賴特', 'Philip S. Wright', '西印度群島聖公宗', '西印度群島聖公宗', 14, 2025, NULL, NULL, '正統', 'Wikipedia: Archbishop of the West Indies', '現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '西印度群島聖公宗' AND church = '西印度群島聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 11. 巴西聖公宗（Anglican Episcopal Church of Brazil, IEAB）
--     1965年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('埃格蒙特·馬查多·克里施克', 'Egmont Machado Krischke', '巴西聖公宗', '巴西聖公宗', 1, 1965, 1971, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', '建省首任首牧；傳教士之子'),
('阿瑟·魯道夫·克拉茨', 'Arthur Rodolpho Kratz', '巴西聖公宗', '巴西聖公宗', 2, 1972, 1984, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('奧拉沃·芬圖拉·路易斯', 'Olavo Ventura Luiz', '巴西聖公宗', '巴西聖公宗', 3, 1986, 1992, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('格拉烏科·索亞雷斯·德利馬', 'Glauco Soares de Lima', '巴西聖公宗', '巴西聖公宗', 4, 1993, 2003, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', '聖保羅主教'),
('奧蘭多·桑托斯·德奧利維拉', 'Orlando Santos de Oliveira', '巴西聖公宗', '巴西聖公宗', 5, 2003, 2006, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('毛里西奧·何塞·阿勞霍·德安德拉德', 'Maurício José Araújo de Andrade', '巴西聖公宗', '巴西聖公宗', 6, 2006, 2013, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('弗朗西斯科·德阿西斯·達席爾瓦', 'Francisco de Assis da Silva', '巴西聖公宗', '巴西聖公宗', 7, 2013, 2018, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('諾達爾·阿爾韋斯·戈麥斯', 'Naudal Alves Gomes', '巴西聖公宗', '巴西聖公宗', 8, 2018, 2022, '退休', '正統', 'Wikipedia: Anglican Episcopal Church of Brazil', NULL),
('馬里內斯·羅薩·多斯桑托斯·巴索托', 'Marinez Rosa dos Santos Bassotto', '巴西聖公宗', '巴西聖公宗', 9, 2023, NULL, NULL, '正統', 'The Living Church 2022; Wikipedia: Anglican Episcopal Church of Brazil', '拉丁美洲首位女性首牧；2022年11月13日當選')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '巴西聖公宗' AND church = '巴西聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 12. 墨西哥聖公宗（Anglican Church of Mexico）
--     1995年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('何塞·薩塞多', 'José G. Saucedo', '墨西哥聖公宗', '墨西哥聖公宗', 1, 1995, 1997, '退休', '正統', 'Wikipedia: Anglican Church of Mexico', '建省首任首牧；1995年1月1日建省'),
('薩繆爾·埃斯皮諾薩', 'Samuel Espinoza', '墨西哥聖公宗', '墨西哥聖公宗', 2, 1999, 2002, '退休', '正統', 'Wikipedia: Anglican Church of Mexico', NULL),
('卡洛斯·圖什·波特', 'Carlos Touché Porter', '墨西哥聖公宗', '墨西哥聖公宗', 3, 2004, 2014, '退休', '正統', 'Wikipedia: Anglican Church of Mexico', NULL),
('弗朗西斯科·莫雷諾', 'Francisco Manuel Moreno', '墨西哥聖公宗', '墨西哥聖公宗', 4, 2014, 2020, '退休', '正統', 'Wikipedia: Anglican Church of Mexico; The Living Church 2022', NULL),
('恩里克·特雷維諾·克魯茲', 'Enrique Treviño Cruz', '墨西哥聖公宗', '墨西哥聖公宗', 5, 2022, 2026, '退休', '正統', 'The Living Church 2022', '2020–2022年任代理首牧；2022年6月11日正式就任'),
('阿爾巴·薩利·蘇·埃爾南德斯·加西亞', 'Alba Sally Sue Hernández García', '墨西哥聖公宗', '墨西哥聖公宗', 6, 2026, NULL, NULL, '正統', 'The Living Church 2026; Anglican Communion Office 2026', '2026年3月當選；坎特伯里公認首牧；墨西哥首位女性大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '墨西哥聖公宗' AND church = '墨西哥聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 13. 紐西蘭聖公宗（Anglican Church in Aotearoa, New Zealand and Polynesia）
--     1858年設立都主教；1992年後三人共同首牧制
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('喬治·奧古斯塔斯·塞爾溫', 'George Augustus Selwyn', '紐西蘭聖公宗', '紐西蘭聖公宗', 1, 1858, 1869, '調任', '正統', 'Wikipedia: Primate of New Zealand', '1858年依授權書成為大都會主教；1841年起任紐西蘭主教；1869年調任英國利希菲爾德'),
('亨利·約翰·奇蒂·哈珀', 'Henry John Chitty Harper', '紐西蘭聖公宗', '紐西蘭聖公宗', 2, 1869, 1890, '退休', '正統', 'Wikipedia: Primate of New Zealand', '克萊斯特徹奇主教'),
('奧克塔維烏斯·哈德菲爾德', 'Octavius Hadfield', '紐西蘭聖公宗', '紐西蘭聖公宗', 3, 1890, 1893, '退休', '正統', 'Wikipedia: Primate of New Zealand', '惠靈頓主教'),
('威廉·加登·科維', 'William Garden Cowie', '紐西蘭聖公宗', '紐西蘭聖公宗', 4, 1893, 1902, '退休', '正統', 'Wikipedia: Primate of New Zealand', '奧克蘭主教'),
('塞繆爾·塔拉特·尼維爾', 'Samuel Tarratt Nevill', '紐西蘭聖公宗', '紐西蘭聖公宗', 5, 1902, 1919, '退休', '正統', 'Wikipedia: Primate of New Zealand', '但尼丁主教'),
('邱吉爾·朱利葉斯', 'Churchill Julius', '紐西蘭聖公宗', '紐西蘭聖公宗', 6, 1920, 1925, '退休', '正統', 'Wikipedia: Primate of New Zealand; Te Ara', '克萊斯特徹奇主教'),
('阿爾弗雷德·沃爾特·阿弗里爾', 'Alfred Walter Averill', '紐西蘭聖公宗', '紐西蘭聖公宗', 7, 1925, 1940, '退休', '正統', 'Wikipedia: Primate of New Zealand', '奧克蘭主教'),
('坎貝爾·韋斯特-沃森', 'Campbell West-Watson', '紐西蘭聖公宗', '紐西蘭聖公宗', 8, 1940, 1952, '退休', '正統', 'Wikipedia: Primate of New Zealand', '克萊斯特徹奇主教'),
('雷金納德·赫伯特·歐文', 'Reginald Herbert Owen', '紐西蘭聖公宗', '紐西蘭聖公宗', 9, 1952, 1960, '退休', '正統', 'Wikipedia: Primate of New Zealand', '惠靈頓主教'),
('諾曼·阿爾弗雷德·萊瑟', 'Norman Alfred Lesser', '紐西蘭聖公宗', '紐西蘭聖公宗', 10, 1961, 1971, '退休', '正統', 'Wikipedia: Primate of New Zealand', '懷奧普主教'),
('艾倫·霍華德·約翰斯頓', 'Allen Howard Johnston', '紐西蘭聖公宗', '紐西蘭聖公宗', 11, 1972, 1980, '退休', '正統', 'Wikipedia: Primate of New Zealand', '懷卡托主教'),
('保羅·阿爾弗雷德·里夫斯', 'Paul Alfred Reeves', '紐西蘭聖公宗', '紐西蘭聖公宗', 12, 1980, 1985, '調任', '正統', 'Wikipedia: Primate of New Zealand', '奧克蘭主教；後任紐西蘭總督'),
('布萊恩·牛頓·戴維斯', 'Brian Newton Davis', '紐西蘭聖公宗', '紐西蘭聖公宗', 13, 1986, 1992, '退休', '正統', 'Wikipedia: Primate of New Zealand', '懷卡托及惠靈頓主教；1992年後實施三人共同首牧制')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '紐西蘭聖公宗' AND church = '紐西蘭聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 14. 巴紐聖公宗（Anglican Church of Papua New Guinea）
--     1977年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('大衛·漢德', 'David Hand', '巴紐聖公宗', '巴紐聖公宗', 1, 1977, 1983, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '首任大主教；澳大利亞籍；建省時任莫爾斯比港主教'),
('喬治·阿姆博', 'George Ambo', '巴紐聖公宗', '巴紐聖公宗', 2, 1983, 1989, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '首位巴紐本地人大主教'),
('貝文·梅雷迪思', 'Bevan Meredith', '巴紐聖公宗', '巴紐聖公宗', 3, 1989, 1995, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '新幾內亞島教區主教'),
('詹姆斯·阿永', 'James Ayong', '巴紐聖公宗', '巴紐聖公宗', 4, 1996, 2009, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '艾波-容戈教區主教'),
('約瑟夫·科帕帕', 'Joseph Kopapa', '巴紐聖公宗', '巴紐聖公宗', 5, 2010, 2012, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '首位非教區大主教職位'),
('克萊德·伊加拉', 'Clyde Igara', '巴紐聖公宗', '巴紐聖公宗', 6, 2013, 2017, '退休', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', NULL),
('艾倫·米吉', 'Allan Migi', '巴紐聖公宗', '巴紐聖公宗', 7, 2017, 2020, '辭職', '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '因健康原因辭職'),
('納森·因根', 'Nathan Ingen', '巴紐聖公宗', '巴紐聖公宗', 8, 2022, NULL, NULL, '正統', 'Wikipedia: Anglican Church of Papua New Guinea', '現任代理首牧')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '巴紐聖公宗' AND church = '巴紐聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 15. 美拉尼西亞聖公宗（Church of Melanesia）
--     1975年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('約翰·奇澤姆', 'John Chisholm', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 1, 1975, 1975, '逝世', '正統', 'Wikipedia: Archbishop of Melanesia', '建省首任大主教；數月後因喉癌逝世'),
('諾曼·帕爾默', 'Norman Palmer', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 2, 1975, 1987, '退休', '正統', 'Wikipedia: Archbishop of Melanesia', NULL),
('阿莫斯·懷阿魯', 'Amos Waiaru', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 3, 1988, 1993, '退休', '正統', 'Wikipedia: Archbishop of Melanesia', NULL),
('埃利森·萊斯利·波戈', 'Ellison Leslie Pogo', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 4, 1994, 2008, '退休', '正統', 'Wikipedia: Archbishop of Melanesia', NULL),
('大衛·武納吉', 'David Vunagi', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 5, 2009, 2015, '退休', '正統', 'Wikipedia: Archbishop of Melanesia', NULL),
('喬治·塔克利', 'George Takeli', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 6, 2016, 2019, '退休', '正統', 'Wikipedia: Archbishop of Melanesia; Anglican Ink 2019', NULL),
('萊昂納德·達維亞', 'Leonard Dawea', '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', 7, 2019, NULL, NULL, '正統', 'Wikipedia: Archbishop of Melanesia', '現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '美拉尼西亞聖公宗' AND church = '美拉尼西亞聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 16. 印度洋聖公宗（Church of the Province of the Indian Ocean）
--     1973年建省；涵蓋馬達加斯加、模里西斯、塞席爾
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('埃德溫·柯蒂斯', 'Edwin Curtis', '印度洋聖公宗', '印度洋聖公宗', 1, 1973, 1976, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '建省首任大主教'),
('特雷弗·哈德爾斯頓', 'Trevor Huddleston', '印度洋聖公宗', '印度洋聖公宗', 2, 1978, 1983, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '著名反種族隔離活動家；後返英任主教'),
('法蘭奇·常-欣', 'French Chang-Him', '印度洋聖公宗', '印度洋聖公宗', 3, 1984, 1995, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '塞席爾主教'),
('雷米·拉貝尼里納', 'Remi Rabenirina', '印度洋聖公宗', '印度洋聖公宗', 4, 1995, 2005, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '馬達加斯加主教'),
('伊恩·歐內斯特', 'Ian Ernest', '印度洋聖公宗', '印度洋聖公宗', 5, 2006, 2017, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '模里西斯主教'),
('詹姆斯·黃', 'James Wong', '印度洋聖公宗', '印度洋聖公宗', 6, 2017, 2024, '退休', '正統', 'Wikipedia: Church of the Province of the Indian Ocean', '模里西斯主教'),
('吉爾貝特·拉特隆德拉維洛', 'Gilbert Rateloson Rakotondravelo', '印度洋聖公宗', '印度洋聖公宗', 7, 2024, NULL, NULL, '正統', 'Episcopal News Service 2025; Anglican News 2025', '2025年1月21日就任；第二位馬達加斯加籍大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '印度洋聖公宗' AND church = '印度洋聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 17. 耶路撒冷聖公宗（Episcopal Church in Jerusalem and the Middle East）
--     1976年建省；採輪值主席主教制
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('哈桑·德赫卡尼-塔夫提', 'Hassan Dehqani-Tafti', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 1, 1977, 1985, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '首任主席主教；伊朗主教；曾遭暗殺未遂，其子被殺'),
('薩米爾·卡菲蒂', 'Samir Kafity', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 2, 1985, 1995, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '耶路撒冷主教；第二位巴勒斯坦籍主席主教'),
('蓋斯·馬利克', 'Ghais Malik', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 3, 1995, 2000, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '埃及主教；即前任亞歷山卓聖公宗主教'),
('伊拉傑·穆塔赫代赫', 'Iraj Mottahedeh', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 4, 2000, 2002, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '伊朗主教'),
('克萊夫·漢德福德', 'Clive Handford', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 5, 2002, 2007, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '賽浦路斯及海灣主教'),
('穆尼爾·安尼斯', 'Mouneer Anis', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 6, 2007, 2017, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '埃及主教；同時任亞歷山卓省主席'),
('蘇海爾·道瓦尼', 'Suheil Dawani', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 7, 2017, 2019, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East; Wikipedia: Suheil Dawani', '耶路撒冷大主教'),
('麥克·劉易斯', 'Michael Lewis', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 8, 2019, 2023, '退休', '正統', 'Wikipedia: Episcopal Church in Jerusalem and the Middle East', '賽浦路斯及海灣主教'),
('霍薩姆·瑙姆', 'Hosam Naoum', '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', 9, 2023, NULL, NULL, '正統', 'Anglican News 2023; Episcopal News Service 2023', '2023年5月就任；耶路撒冷大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '耶路撒冷聖公宗' AND church = '耶路撒冷及中東聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 18. 北印度教會（Church of North India, CNI）
--     1970年聯合教會成立；主持人每三年輪選
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('埃里克·納西爾', 'Eric Nasir', '北印度教會', '北印度教會', 1, 1971, 1974, '退休', '正統', 'Wikipedia: Church of North India; United Church of Canada Archives', '首任主持人；德里教區主教'),
('拉姆昌德拉·班達雷', 'Ramchandra Bhandare', '北印度教會', '北印度教會', 2, 1980, 1983, '退休', '正統', 'Wikipedia: Church of North India', '那格浦爾教區主教'),
('迪内什·昌德拉·戈賴', 'Dinesh Chandra Gorai', '北印度教會', '北印度教會', 3, 1983, 1986, '退休', '正統', 'Wikipedia: Church of North India', '加爾各答教區主教'),
('丁·達亞爾', 'Din Dayal', '北印度教會', '北印度教會', 4, 1986, 1989, '退休', '正統', 'Wikipedia: Church of North India', '勒克瑙教區主教'),
('約翰·戈什', 'John Ghosh', '北印度教會', '北印度教會', 5, 1989, 1992, '退休', '正統', 'Wikipedia: Church of North India', '大吉嶺教區主教'),
('阿南德·昌杜·拉爾', 'Anand Chandu Lal', '北印度教會', '北印度教會', 6, 1992, 1995, '退休', '正統', 'Wikipedia: Church of North India', '阿姆利則教區主教'),
('迪倫德拉·莫漢蒂', 'Dhirendra Mohanty', '北印度教會', '北印度教會', 7, 1995, 1998, '退休', '正統', 'Wikipedia: Church of North India', '卡塔克教區主教'),
('維諾德·彼得', 'Vinod Peter', '北印度教會', '北印度教會', 8, 1998, 2001, '退休', '正統', 'Wikipedia: Church of North India', '那格浦爾教區主教'),
('詹姆斯·特羅姆', 'James Terom', '北印度教會', '北印度教會', 9, 2001, 2004, '退休', '正統', 'Wikipedia: Church of North India', '喬塔那格普爾教區主教'),
('喬爾·馬爾', 'Joel Mal', '北印度教會', '北印度教會', 10, 2005, 2008, '退休', '正統', 'Wikipedia: Church of North India', '昌迪加爾教區主教'),
('普里利·林多', 'Purely Lyngdoh', '北印度教會', '北印度教會', 11, 2008, 2011, '退休', '正統', 'Wikipedia: Church of North India', '東北印度教區主教'),
('菲利普·馬蘭迪', 'Philip Marandih', '北印度教會', '北印度教會', 12, 2011, 2014, '退休', '正統', 'Wikipedia: Church of North India', '巴特那教區主教'),
('普拉迪普·薩曼塔羅伊', 'Pradeep Samantaroy', '北印度教會', '北印度教會', 13, 2014, 2017, '退休', '正統', 'Wikipedia: Church of North India', '阿姆利則教區主教'),
('普雷姆·辛格', 'Prem Singh', '北印度教會', '北印度教會', 14, 2017, 2019, '退休', '正統', 'Wikipedia: Church of North India; Anglican News 2017', '賈巴爾普爾教區主教'),
('比賈伊·庫馬爾·納亞克', 'Bijay Kumar Nayak', '北印度教會', '北印度教會', 15, 2019, 2025, '退休', '正統', 'Wikipedia: Church of North India', '普爾巴尼教區主教；2022年因挪用指控被廢除但後恢復'),
('帕里托什·坎寧', 'Paritosh Canning', '北印度教會', '北印度教會', 16, 2025, NULL, NULL, '正統', 'Anglican Ink 2022; Anglican News 2025', '現任主持人；加爾各答教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '北印度教會' AND church = '北印度教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 19. 南印度教會（Church of South India, CSI）
--     1947年成立；首個聯合教會；主持人每三年輪選
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('邁克爾·霍利斯', 'Michael Hollis', '南印度教會', '南印度教會', 1, 1948, 1954, '退休', '正統', 'Wikipedia: Church of South India Synod', '首任主持人；馬德拉斯主教；英國籍'),
('霍斯佩特·蘇米特拉', 'Hospet Sumitra', '南印度教會', '南印度教會', 2, 1954, 1962, '退休', '正統', 'Wikipedia: Church of South India Synod', '拉亞拉西馬主教'),
('佩雷吉·所羅門', 'Pereji Solomon', '南印度教會', '南印度教會', 3, 1962, 1971, '退休', '正統', 'Wikipedia: Church of South India Synod; Wikipedia: Pereji Solomon', '多爾納卡爾教區主教；任期最長'),
('阿南達·拉奧·塞繆爾', 'Ananda Rao Samuel', '南印度教會', '南印度教會', 4, 1972, 1978, '退休', '正統', 'Wikipedia: Church of South India Synod', '克里希納-戈達瓦里主教'),
('所羅門·多萊斯瓦米', 'Solomon Doraiswamy', '南印度教會', '南印度教會', 5, 1978, 1982, '退休', '正統', 'Wikipedia: Church of South India Synod', '特里奇-坦賈武爾主教'),
('以賽亞·耶穌達松', 'Isaiah Jesudason', '南印度教會', '南印度教會', 6, 1982, 1986, '退休', '正統', 'Wikipedia: Church of South India Synod', '南喀拉拉主教'),
('維克托·普雷馬薩加', 'Victor Premasagar', '南印度教會', '南印度教會', 7, 1986, 1992, '退休', '正統', 'Wikipedia: Victor Premasagar', '梅達克主教；兩屆任期'),
('萊德·德瓦普里亞姆', 'Ryder Devapriam', '南印度教會', '南印度教會', 8, 1992, 1996, '退休', '正統', 'Wikipedia: Church of South India Synod', NULL),
('瓦桑特·P·丹丁', 'Vasant P. Dandin', '南印度教會', '南印度教會', 9, 1996, 2000, '退休', '正統', 'Wikipedia: Church of South India Synod', NULL),
('威廉·摩西', 'William Moses', '南印度教會', '南印度教會', 10, 2000, 2004, '退休', '正統', 'Wikipedia: Church of South India Synod', '哥印拜陀主教'),
('孔農姆普拉圖·塞繆爾', 'Kunnumpurathu Samuel', '南印度教會', '南印度教會', 11, 2004, 2006, '退休', '正統', 'Wikipedia: Church of South India Synod', '東喀拉拉主教'),
('彼得·蘇甘達爾', 'Peter Sugandhar', '南印度教會', '南印度教會', 12, 2006, 2012, '退休', '正統', 'Wikipedia: Church of South India Synod', '梅達克主教'),
('格納納西加莫尼·德瓦卡達沙姆', 'Gnanasigamony Devakadasham', '南印度教會', '南印度教會', 13, 2012, 2016, '退休', '正統', 'Wikipedia: Church of South India Synod', '坎亞庫馬里主教'),
('戈瓦達·迪亞西爾瓦達姆', 'Govada Dyvasirvadam', '南印度教會', '南印度教會', 14, 2016, 2020, '退休', '正統', 'Wikipedia: Church of South India Synod', '克里希納-戈達瓦里主教'),
('达摩拉吉·拉薩拉姆', 'Dharmaraj Rasalam', '南印度教會', '南印度教會', 15, 2020, 2023, '退休', '正統', 'Wikipedia: Church of South India Synod', '南喀拉拉主教'),
('魯本·馬克', 'K. Reuben Mark', '南印度教會', '南印度教會', 16, 2023, NULL, NULL, '正統', 'Anglican Ink 2025', '現任主持人；印度最高法院裁定選舉有效後確認')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '南印度教會' AND church = '南印度教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 20. 孟加拉教會（Church of Bangladesh）
--     1971年成立；達卡教區
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('詹姆斯·D·布萊爾', 'James D. Blair', '孟加拉教會', '孟加拉教會', 1, 1971, 1975, '退休', '正統', 'Wikipedia: Church of Bangladesh', '建國後首任主教；前加爾各答輔理主教（東孟加拉）'),
('巴爾納巴斯·德真·蒙達爾', 'Barnabas Dejen Mondal', '孟加拉教會', '孟加拉教會', 2, 1975, 2003, '退休', '正統', 'Wikipedia: Church of Bangladesh', '1975年2月16日由牛津傳教士教會主教座堂祝聖；首任主持人；任期最長'),
('米迦勒·S·巴羅伊', 'Michael S. Baroi', '孟加拉教會', '孟加拉教會', 3, 2003, 2009, '退休', '正統', 'Wikipedia: Church of Bangladesh', '2003年1月24日就任'),
('保羅·希希爾·薩克爾', 'Paul Shishir Sarker', '孟加拉教會', '孟加拉教會', 4, 2009, 2019, '退休', '正統', 'Wikipedia: Church of Bangladesh', '2018年11月19日卸任主持人職'),
('薩繆爾·蘇尼爾·曼欽', 'Samuel Sunil Mankhin', '孟加拉教會', '孟加拉教會', 5, 2019, NULL, NULL, '正統', 'Wikipedia: Church of Bangladesh', '現任主持人及達卡主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '孟加拉教會' AND church = '孟加拉教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 21. 巴基斯坦教會（Church of Pakistan）
--     1970年聯合教會成立；主持人輪選
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('扎希爾-烏丁·米爾扎', 'Zahir-Ud-Din Mirza', '巴基斯坦教會', '巴基斯坦教會', 1, 1990, 1994, '退休', '正統', 'Wikipedia: Church of Pakistan', '費薩拉巴德首任主教；曾任主持人'),
('薩繆爾·阿扎里亞', 'Samuel Azariah', '巴基斯坦教會', '巴基斯坦教會', 2, 1997, 2002, '退休', '正統', 'Wikipedia: Church of Pakistan; Pakistan Christian Post', '首屆任期1997–2002；萊瓦爾品第–費薩拉巴德主教'),
('亞歷山大·約翰·馬利克', 'Alexander John Malik', '巴基斯坦教會', '巴基斯坦教會', 3, 2002, 2009, '退休', '正統', 'Pakistan Christian Post; Jahangir''s World Times', '拉合爾主教；任職三十餘年'),
('薩繆爾·阿扎里亞', 'Samuel Azariah', '巴基斯坦教會', '巴基斯坦教會', 4, 2009, 2017, '退休', '正統', 'Wikipedia: Church of Pakistan', '二度出任主持人2009–2017'),
('韓弗里·彼得斯', 'Humphrey Peters', '巴基斯坦教會', '巴基斯坦教會', 5, 2017, 2021, '退休', '正統', 'Wikipedia: Humphrey Peters; Daily Times', '白沙瓦主教；2011年起任主教'),
('阿扎德·馬歇爾', 'Azad Marshall', '巴基斯坦教會', '巴基斯坦教會', 6, 2021, NULL, NULL, '正統', 'Wikipedia: Azad Marshall; Anglican Ink 2021', '2021年5月14日全票當選；現任主持人及首牧')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '巴基斯坦教會' AND church = '巴基斯坦教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 22. 錫蘭教會（Church of Ceylon / Sri Lanka）
--     以科倫坡主教為主要列表；另設庫魯納卡拉教區（1950年起）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('羅洛·格雷厄姆·坎貝爾', 'Rollo Graham Campbell', '錫蘭教會', '錫蘭教會', 1, 1948, 1964, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', '科倫坡第十任主教'),
('哈羅德·德索薩', 'Harold de Soysa', '錫蘭教會', '錫蘭教會', 2, 1964, 1971, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', '首任錫蘭本地籍科倫坡主教'),
('西里爾·阿貝耶納依克', 'Cyril Abeynaike', '錫蘭教會', '錫蘭教會', 3, 1971, 1977, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('斯維欽·費爾南多', 'Swithin Fernando', '錫蘭教會', '錫蘭教會', 4, 1978, 1987, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('賈貝斯·格納那普拉加薩姆', 'Jabez Gnanapragasam', '錫蘭教會', '錫蘭教會', 5, 1987, 1992, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('肯尼斯·費爾南多', 'Kenneth Fernando', '錫蘭教會', '錫蘭教會', 6, 1992, 2001, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('杜利普·德·奇克拉', 'Duleep De Chickera', '錫蘭教會', '錫蘭教會', 7, 2001, 2010, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('迪洛拉吉·卡納加薩貝', 'Dhiloraj Canagasabey', '錫蘭教會', '錫蘭教會', 8, 2011, 2020, '退休', '正統', 'Wikipedia: Anglican Bishop of Colombo', NULL),
('杜尚塔·拉克什曼·羅德里戈', 'Dushantha Lakshman Rodrigio', '錫蘭教會', '錫蘭教會', 9, 2020, NULL, NULL, '正統', 'Wikipedia: Anglican Bishop of Colombo', '2020年10月28日就任第十六任科倫坡主教；現任')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '錫蘭教會' AND church = '錫蘭教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 23. 東南亞聖公宗（Church of the Province of South East Asia）
--     1996年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('摩西·戴', 'Moses Tay', '東南亞聖公宗', '東南亞聖公宗', 1, 1996, 2000, '退休', '正統', 'Wikipedia: Church of the Province of South East Asia', '建省首任大主教；新加坡教區主教'),
('楊平忠', 'Yong Ping Chung', '東南亞聖公宗', '東南亞聖公宗', 2, 2000, 2006, '退休', '正統', 'Wikipedia: Church of the Province of South East Asia', '砂拉越教區主教'),
('鄒約翰', 'John Chew', '東南亞聖公宗', '東南亞聖公宗', 3, 2006, 2012, '退休', '正統', 'Wikipedia: John Chew', '新加坡教區主教；達退休年齡卸任'),
('波利·拉波克', 'Bolly Lapok', '東南亞聖公宗', '東南亞聖公宗', 4, 2012, 2016, '退休', '正統', 'Wikipedia: Church of the Province of South East Asia', '古晉教區主教；第四任大主教'),
('吳文望', 'Ng Moon Hing', '東南亞聖公宗', '東南亞聖公宗', 5, 2016, 2020, '退休', '正統', 'Wikipedia: Church of the Province of South East Asia', '西馬來西亞教區主教'),
('梅爾特·泰斯', 'Melter Tais', '東南亞聖公宗', '東南亞聖公宗', 6, 2020, 2024, '退休', '正統', 'Wikipedia: Church of the Province of South East Asia', '沙巴教區主教'),
('鄭偉翔', 'Titus Chung', '東南亞聖公宗', '東南亞聖公宗', 7, 2024, NULL, NULL, '正統', 'The Living Church 2023; Wikipedia: Church of the Province of South East Asia', '2023年9月當選、2024年1月23日就任；新加坡教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '東南亞聖公宗' AND church = '東南亞聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 24. 菲律賓聖公宗（Episcopal Church in the Philippines）
--     1990年建省；稱號為「首席主教」(Prime Bishop)
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('貝尼托·卡班班', 'Benito C. Cabanban', '菲律賓聖公宗', '菲律賓聖公宗', 1, 1967, 1978, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', '建省前首任主持主教；第一任首席主教'),
('孔斯坦西奧·曼古拉馬斯', 'Constancio Buanda Manguramas', '菲律賓聖公宗', '菲律賓聖公宗', 2, 1978, 1982, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('理查德·阿貝隆', 'Richard Abelardo Abellon', '菲律賓聖公宗', '菲律賓聖公宗', 3, 1982, 1986, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('曼努埃爾·盧姆皮亞斯', 'Manuel Capuyan Lumpias', '菲律賓聖公宗', '菲律賓聖公宗', 4, 1986, 1990, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', '建省時任首席主教；1990年自主'),
('納西索·蒂科拜', 'Narciso Valentin Ticobay', '菲律賓聖公宗', '菲律賓聖公宗', 5, 1993, 1997, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('伊格納西奧·索利巴', 'Ignacio Capuyan Soliba', '菲律賓聖公宗', '菲律賓聖公宗', 6, 1997, 2009, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('愛德華·馬萊坎丹', 'Edward Pacyaya Malecdan', '菲律賓聖公宗', '菲律賓聖公宗', 7, 2009, 2014, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('雷納托·阿比比科', 'Renato Mag-gay Abibico', '菲律賓聖公宗', '菲律賓聖公宗', 8, 2014, 2017, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('喬爾·帕喬', 'Joel Atiwag Pachao', '菲律賓聖公宗', '菲律賓聖公宗', 9, 2017, 2021, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('布倫特·哈里·阿拉瓦斯', 'Brent Harry Wanas Alawas', '菲律賓聖公宗', '菲律賓聖公宗', 10, 2021, 2025, '退休', '正統', 'Wikipedia: Episcopal Church in the Philippines', NULL),
('奈斯托·波爾蒂克', 'Nestor Dagas Poltic Sr.', '菲律賓聖公宗', '菲律賓聖公宗', 11, 2025, NULL, NULL, '正統', 'The Living Church 2024; Wikipedia: Episcopal Church in the Philippines', '2024年5月14日當選；現任首席主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '菲律賓聖公宗' AND church = '菲律賓聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 25. 緬甸聖公宗（Church of the Province of Myanmar）
--     1970年建省
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('弗朗西斯·阿彌亞', 'Francis Ah Mya', '緬甸聖公宗', '緬甸聖公宗', 1, 1970, 1973, '退休', '正統', 'Wikipedia: Francis Ah Mya; Wikipedia: Church of the Province of Myanmar', '建省首任大主教；仰光教區主教'),
('約翰·昂拉', 'John Aung Hla', '緬甸聖公宗', '緬甸聖公宗', 2, 1973, 1979, '退休', '正統', 'Wikipedia: Church of the Province of Myanmar', NULL),
('格雷戈里·拉覺', 'Gregory Hla Kyaw', '緬甸聖公宗', '緬甸聖公宗', 3, 1979, 1987, '退休', '正統', 'Wikipedia: Church of the Province of Myanmar', NULL),
('安德魯·謀漢', 'Andrew Mya Han', '緬甸聖公宗', '緬甸聖公宗', 4, 1988, 2001, '退休', '正統', 'Wikipedia: Church of the Province of Myanmar', NULL),
('塞繆爾·桑·西·泰', 'Samuel San Si Htay', '緬甸聖公宗', '緬甸聖公宗', 5, 2001, 2008, '退休', '正統', 'Wikipedia: Church of the Province of Myanmar', NULL),
('斯蒂芬·丹·明·烏', 'Stephen Than Myint Oo', '緬甸聖公宗', '緬甸聖公宗', 6, 2008, NULL, NULL, '正統', 'Wikipedia: Stephen Than Myint Oo; Anglican Myanmar website', '2008年1月15日當選；第六任大主教；仰光教區主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '緬甸聖公宗' AND church = '緬甸聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 26. 塔林（愛沙尼亞信義會，Estonian Evangelical Lutheran Church, EELK）
--     1917年建立；設主教/大主教職位
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('雅科布·庫克', 'Jakob Kukk', '塔林', '愛沙尼亞信義會', 1, 1919, 1933, '逝世', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church; EELK History', '首任主教；1917年信義會建立後1919年祝聖；由瑞典大主教索德布倫祝聖；1933年去世'),
('胡戈·伯恩哈德·拉哈馬吉', 'Hugo Bernhard Rahamägi', '塔林', '愛沙尼亞信義會', 2, 1934, 1939, '廢黜', '正統', 'Wikipedia: Hugo Bernhard Rahamägi', '1934年9月16日祝聖；1939年因醜聞被廢黜'),
('約翰·科普', 'Johan Kõpp', '塔林', '愛沙尼亞信義會', 3, 1939, 1944, '流亡', '正統', 'Wikipedia: Johan Kõpp; EELK History', '1939年民主選舉；蘇佔與德佔期間繼續任職；1944年流亡瑞典；1970年代流亡教會主教'),
('雅安·基維特（父）', 'Jaan Kiivit Sr.', '塔林', '愛沙尼亞信義會', 4, 1949, 1967, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', '蘇聯當局扶持下就任；首任大主教稱號；蘇占時期在任'),
('阿爾弗雷德·圖明', 'Alfred Tooming', '塔林', '愛沙尼亞信義會', 5, 1967, 1977, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', NULL),
('埃德加·哈爾克', 'Edgar Hark', '塔林', '愛沙尼亞信義會', 6, 1978, 1986, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', NULL),
('庫諾·帕尤拉', 'Kuno Pajula', '塔林', '愛沙尼亞信義會', 7, 1987, 1994, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', '愛沙尼亞恢復獨立期間任職'),
('雅安·基維特（子）', 'Jaan Kiivit Jr.', '塔林', '愛沙尼亞信義會', 8, 1994, 2005, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', NULL),
('安德雷斯·波德爾', 'Andres Põder', '塔林', '愛沙尼亞信義會', 9, 2005, 2014, '退休', '正統', 'Wikipedia: Estonian Evangelical Lutheran Church', NULL),
('烏爾馬斯·維爾馬', 'Urmas Viilma', '塔林', '愛沙尼亞信義會', 10, 2015, NULL, NULL, '正統', 'Wikipedia: Estonian Evangelical Lutheran Church; EELK website', '現任大主教；2015年就任')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '塔林' AND church = '愛沙尼亞信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 27. 里加（拉脫維亞信義會，Evangelical Lutheran Church of Latvia, LELB）
--     1922年正式建立；設里加大主教職位
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('卡爾利斯·伊爾貝', 'Kārlis Irbe', '里加', '拉脫維亞信義會', 1, 1922, 1933, '退休', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', '首任主教（後升大主教）；1922年建立統一拉脫維亞語信義會時當選'),
('特奧多爾斯·格林貝格斯', 'Teodors Grīnbergs', '里加', '拉脫維亞信義會', 2, 1933, 1944, '流亡', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', '1944年蘇聯再次佔領後流亡西方；繼續在流亡政府服務'),
('古斯塔夫斯·圖爾斯', 'Gustavs Tūrs', '里加', '拉脫維亞信義會', 3, 1948, 1968, '逝世', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', '人稱「紅色大主教」；蘇占期間任職；1968年去世'),
('亞尼斯·馬圖利斯', 'Jānis Matulis', '里加', '拉脫維亞信義會', 4, 1969, 1985, '退休', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', NULL),
('埃里克斯·梅斯特斯', 'Ēriks Mesters', '里加', '拉脫維亞信義會', 5, 1986, 1989, '退休', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', NULL),
('卡爾利斯·蓋利蒂斯', 'Kārlis Gailītis', '里加', '拉脫維亞信義會', 6, 1989, 1992, '逝世', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia', '車禍身亡'),
('亞尼斯·瓦納格斯', 'Jānis Vanags', '里加', '拉脫維亞信義會', 7, 1993, 2025, '退休', '正統', 'Wikipedia: Evangelical Lutheran Church of Latvia; ILC 2025', '1993年8月29日祝聖；任期逾三十年；保守神學立場；2025年退休'),
('里納爾德斯·格蘭茨', 'Rinalds Grants', '里加', '拉脫維亞信義會', 8, 2025, NULL, NULL, '正統', 'WCC Congratulations 2025; LWF 2025; ILC 2025', '2025年6月當選；2025年9月就任；現任大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '里加' AND church = '拉脫維亞信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;
