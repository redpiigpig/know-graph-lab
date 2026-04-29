-- ============================================================
-- 聖公宗各省首牧傳承（除坎特伯里、約克外）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources) VALUES

-- ==============================
-- 愛爾蘭教會 (Church of Ireland) — 阿馬
-- ==============================
('乔治·唐納爾', 'George Dowdall', '阿馬', '愛爾蘭教會', 1, 1543, 1552, '辭職（反宗教改革）', '英格蘭國王亨利八世', '正統', 'Church of Ireland records'),
('休·格雷達爾', 'Hugh Goodacre', '阿馬', '愛爾蘭教會', 2, 1553, 1553, '逝世（任內）', '英格蘭國王愛德華六世', '正統', 'Church of Ireland records'),
('亞當·洛夫特斯', 'Adam Loftus', '阿馬', '愛爾蘭教會', 5, 1562, 1567, '轉任都柏林', '伊麗莎白一世', '正統', 'Church of Ireland records'),
('托馬斯·彼特', 'Thomas Lancaster', '阿馬', '愛爾蘭教會', 6, 1568, 1584, '逝世', '伊麗莎白一世', '正統', 'Church of Ireland records'),
('約翰·洛夫特斯', 'John Alen', '阿馬', '愛爾蘭教會', 9, 1625, 1626, '逝世', '查理一世', '正統', 'Church of Ireland records'),
('詹姆斯·厄謝爾', 'James Ussher', '阿馬', '愛爾蘭教會', 10, 1625, 1656, '逝世', '查理一世', '正統', 'Church of Ireland records; biblical chronology; 4004 BC creation date'),
('詹姆斯·麥克唐奈', 'Michael Boyle', '阿馬', '愛爾蘭教會', 11, 1679, 1702, '逝世', '查理二世', '正統', 'Church of Ireland records'),
('威廉·金', 'William King', '阿馬', '愛爾蘭教會', 12, 1703, 1729, '逝世', '威廉三世', '正統', 'Church of Ireland records'),
('休·伯恩', 'Hugh Boulter', '阿馬', '愛爾蘭教會', 13, 1724, 1742, '逝世', '喬治一世', '正統', 'Church of Ireland records; English-born Primate'),
('理查德·羅賓遜', 'Richard Robinson', '阿馬', '愛爾蘭教會', 15, 1765, 1794, '逝世', '喬治三世', '正統', 'Church of Ireland records'),
('威廉·斯圖爾特', 'William Stuart', '阿馬', '愛爾蘭教會', 17, 1800, 1822, '逝世', '英格蘭國王喬治三世', '正統', 'Church of Ireland records'),
('約翰·乔治·貝雷斯福特', 'John George Beresford', '阿馬', '愛爾蘭教會', 18, 1822, 1862, '逝世', '喬治四世', '正統', 'Church of Ireland records'),
('馬庫斯·格貝丁斯', 'Marcus Gervais Beresford', '阿馬', '愛爾蘭教會', 19, 1862, 1885, '逝世', '維多利亞女王', '正統', 'Church of Ireland records'),
('威廉·亞歷山大', 'William Alexander', '阿馬', '愛爾蘭教會', 20, 1896, 1911, '退休', '維多利亞女王', '正統', 'Church of Ireland records; poet; Mrs Cecil Frances Alexander''s husband'),
('查爾斯·達西', 'Charles Frederick D''Arcy', '阿馬', '愛爾蘭教會', 22, 1920, 1938, '逝世', '喬治五世', '正統', 'Church of Ireland records'),
('約翰·阿倫·格羅根', 'John Allen Fitzgerald Gregg', '阿馬', '愛爾蘭教會', 23, 1938, 1959, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records'),
('詹姆斯·麥坎恩', 'James McCann', '阿馬', '愛爾蘭教會', 24, 1959, 1969, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records'),
('喬治·奧托·西姆斯', 'George Otto Simms', '阿馬', '愛爾蘭教會', 25, 1969, 1980, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records; Celtic Church scholar'),
('約翰·沃德·阿姆斯特朗', 'John Ward Armstrong', '阿馬', '愛爾蘭教會', 26, 1980, 1986, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records'),
('羅伯特·亨利·艾卡特', 'Robert Henry Alexander Eames', '阿馬', '愛爾蘭教會', 27, 1986, 2006, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records; Lord Eames; international ecumenism'),
('艾倫·哈珀', 'Alan Harper', '阿馬', '愛爾蘭教會', 28, 2007, 2012, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records'),
('理查德·克拉克', 'Richard Clarke', '阿馬', '愛爾蘭教會', 29, 2012, 2020, '退休', '愛爾蘭教會', '正統', 'Church of Ireland records'),
('約翰·麥克道爾', 'John McDowell', '阿馬', '愛爾蘭教會', 30, 2020, NULL, NULL, '愛爾蘭教會', '正統', 'Church of Ireland records'),

-- ==============================
-- 威爾士教會大主教
-- ==============================
('艾佛裡德·喬治·愛德華茲', 'Alfred George Edwards', '威爾士', '威爾士教會', 1, 1920, 1934, '退休', '威爾士教會', '正統', 'Church in Wales records; first Archbishop'),
('查爾斯·格林', 'Charles Green', '威爾士', '威爾士教會', 2, 1934, 1944, '逝世', '威爾士教會', '正統', 'Church in Wales records'),
('大衛·盧埃林·沃特金-威廉斯', 'David Watkin Williams', '威爾士', '威爾士教會', 3, 1945, 1957, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('埃文·科里斯·盧埃林', 'Edwin Morris', '威爾士', '威爾士教會', 4, 1957, 1968, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('ウィルフレッド·萬斯坦利·彼德斯·托馬斯', 'Glyn Simon', '威爾士', '威爾士教會', 5, 1968, 1971, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('格溫·歐文·威廉斯', 'Gwilym Owen Williams', '威爾士', '威爾士教會', 6, 1971, 1982, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('德雷克·利物普', 'Derrick Childs', '威爾士', '威爾士教會', 7, 1983, 1991, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('阿爾文·瓊斯', 'Alwyn Rice Jones', '威爾士', '威爾士教會', 8, 1991, 1999, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('羅恩·威廉斯', 'Rowan Williams', '威爾士', '威爾士教會', 9, 1999, 2002, '轉任坎特伯里', '威爾士教會', '正統', 'Church in Wales records; later Archbishop of Canterbury'),
('배리·摩根', 'Barry Morgan', '威爾士', '威爾士教會', 10, 2003, 2017, '退休', '威爾士教會', '正統', 'Church in Wales records; Welsh language champion'),
('約翰·戴維斯', 'John Davies', '威爾士', '威爾士教會', 11, 2017, 2021, '退休', '威爾士教會', '正統', 'Church in Wales records'),
('安德魯·約翰', 'Andrew John', '威爾士', '威爾士教會', 12, 2023, NULL, NULL, '威爾士教會', '正統', 'Church in Wales records'),

-- ==============================
-- 美國聖公會 (TEC) 首牧主教
-- ==============================
('薩繆爾·普羅沃斯特', 'Samuel Provoost', '美國聖公會', '美國聖公會', 1, 1789, 1801, '退休', '美國聖公會全國大會', '正統', 'TEC records; first Presiding Bishop'),
('威廉·懷特', 'William White', '美國聖公會', '美國聖公會', 2, 1795, 1836, '逝世', '美國聖公會', '正統', 'TEC records; also Bishop of Pennsylvania'),
('亞歷山大·格里格', 'Alexander Griswold', '美國聖公會', '美國聖公會', 3, 1836, 1843, '逝世', '美國聖公會', '正統', 'TEC records'),
('菲利普·格里斯伍德', 'Philander Chase', '美國聖公會', '美國聖公會', 4, 1843, 1852, '逝世', '美國聖公會', '正統', 'TEC records; founded Kenyon College'),
('托馬斯·克拉克', 'Thomas Clark', '美國聖公會', '美國聖公會', 5, 1852, 1866, '逝世', '美國聖公會', '正統', 'TEC records'),
('約翰·亨利·霍普金斯', 'John Henry Hopkins', '美國聖公會', '美國聖公會', 6, 1865, 1868, '逝世', '美國聖公會', '正統', 'TEC records; Civil War era'),
('班傑明·博格思', 'Benjamin Bosworth Smith', '美國聖公會', '美國聖公會', 7, 1868, 1884, '退休', '美國聖公會', '正統', 'TEC records'),
('亞歷山大·懷特馬什', 'Alfred Lee', '美國聖公會', '美國聖公會', 8, 1884, 1887, '逝世', '美國聖公會', '正統', 'TEC records'),
('威廉·佩特森', 'John Williams', '美國聖公會', '美國聖公會', 9, 1887, 1899, '逝世', '美國聖公會', '正統', 'TEC records'),
('托馬斯·加洛韋', 'Thomas Gallaudet', '美國聖公會', '美國聖公會', 10, 1899, 1902, '逝世', '美國聖公會', '正統', 'TEC records'),
('大衛·波辛格', 'Daniel Starr Tuttle', '美國聖公會', '美國聖公會', 11, 1903, 1923, '逝世', '美國聖公會', '正統', 'TEC records'),
('亞歷山大·曼', 'Alexander Mann', '美國聖公會', '美國聖公會', 12, 1924, 1925, '逝世', '美國聖公會', '正統', 'TEC records'),
('詹姆斯·德沃爾夫·佩里', 'James DeWolf Perry', '美國聖公會', '美國聖公會', 13, 1926, 1937, '退休', '美國聖公會', '正統', 'TEC records'),
('亨利·聖喬治·塔克', 'Henry St. George Tucker', '美國聖公會', '美國聖公會', 14, 1938, 1946, '退休', '美國聖公會', '正統', 'TEC records'),
('亨利·諾克斯·謝里爾', 'Henry Knox Sherrill', '美國聖公會', '美國聖公會', 15, 1947, 1958, '退休', '美國聖公會', '正統', 'TEC records; WCC founding president'),
('亞瑟·利奇頓伯格', 'Arthur Lichtenberger', '美國聖公會', '美國聖公會', 16, 1958, 1964, '退休（病）', '美國聖公會', '正統', 'TEC records'),
('約翰·哈爾科', 'John Elbridge Hines', '美國聖公會', '美國聖公會', 17, 1964, 1974, '退休', '美國聖公會', '正統', 'TEC records; civil rights; General Convention Special Program'),
('約翰·阿林', 'John Maury Allin', '美國聖公會', '美國聖公會', 18, 1974, 1985, '退休', '美國聖公會', '正統', 'TEC records; opposed women''s ordination'),
('埃德蒙·布朗寧', 'Edmond Lee Browning', '美國聖公會', '美國聖公會', 19, 1985, 1997, '退休', '美國聖公會', '正統', 'TEC records; "no outcasts" motto'),
('弗蘭克·格里斯沃爾德', 'Frank Tracy Griswold III', '美國聖公會', '美國聖公會', 20, 1997, 2006, '退休', '美國聖公會', '正統', 'TEC records; officiated Gene Robinson consecration'),
('凱瑟琳·傑弗茨·薩里', 'Katharine Jefferts Schori', '美國聖公會', '美國聖公會', 21, 2006, 2015, '退休', '美國聖公會', '正統', 'TEC records; first woman Presiding Bishop'),
('邁克爾·柯里', 'Michael Bruce Curry', '美國聖公會', '美國聖公會', 22, 2015, 2024, '退休', '美國聖公會', '正統', 'TEC records; first Black Presiding Bishop; royal wedding sermon'),
('肖恩·羅', 'Sean Rowe', '美國聖公會', '美國聖公會', 23, 2024, NULL, NULL, '美國聖公會', '正統', 'TEC records'),

-- ==============================
-- 加拿大聖公宗首席大主教
-- ==============================
('本傑明·奈特比', 'Benjamin Cronyn', '加拿大聖公宗', '加拿大聖公宗', 1, 1893, 1896, '逝世', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('湯瑪斯·富勒', 'Thomas Fuller', '加拿大聖公宗', '加拿大聖公宗', 2, 1893, 1902, '逝世', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('亞瑟·斯韋廷', 'Arthur Sweatman', '加拿大聖公宗', '加拿大聖公宗', 3, 1896, 1907, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('斯特拉坦·哈拉格', 'Elihu Stewart', '加拿大聖公宗', '加拿大聖公宗', 4, 1907, 1910, '逝世', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('卡明斯·約翰斯', 'Samuel Pritchard Matheson', '加拿大聖公宗', '加拿大聖公宗', 5, 1909, 1931, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('克勞德·卡森格登', 'Clarendon Lamb Worrell', '加拿大聖公宗', '加拿大聖公宗', 6, 1931, 1934, '逝世', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('大衛·平奇貝克', 'Derwyn Trevor Owen', '加拿大聖公宗', '加拿大聖公宗', 7, 1934, 1947, '逝世', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('諾曼·塔克', 'Beverley Tucker', '加拿大聖公宗', '加拿大聖公宗', 8, 1947, 1952, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('沃爾特·巴格納爾', 'Walter Foster Barfoot', '加拿大聖公宗', '加拿大聖公宗', 9, 1952, 1959, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('霍華德·塔特', 'Howard Clark', '加拿大聖公宗', '加拿大聖公宗', 10, 1959, 1971, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('愛德華·斯科特', 'Edward Walter Scott', '加拿大聖公宗', '加拿大聖公宗', 11, 1971, 1986, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records; WCC Moderator 1975-83'),
('邁克爾·彼得', 'Michael Geoffrey Peers', '加拿大聖公宗', '加拿大聖公宗', 12, 1986, 2004, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records; apology to Indigenous peoples'),
('安德魯·霍珀', 'Andrew Sandford Hutchison', '加拿大聖公宗', '加拿大聖公宗', 13, 2004, 2007, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('弗雷德·希爾杜', 'Fred Hiltz', '加拿大聖公宗', '加拿大聖公宗', 14, 2007, 2019, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),
('琳達·尼科爾斯', 'Linda Nicholls', '加拿大聖公宗', '加拿大聖公宗', 15, 2019, 2023, '退休', '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records; first woman Primate'),
('克里斯多夫·哈珀', 'Christopher Harper', '加拿大聖公宗', '加拿大聖公宗', 16, 2023, NULL, NULL, '加拿大聖公宗大會', '正統', 'Anglican Church of Canada records'),

-- ==============================
-- 澳洲聖公宗首席大主教（輪任制，列主要任期）
-- ==============================
('羅素·多拉蒂', 'Reginald Charles Owen Goodwin', '澳洲聖公宗', '澳洲聖公宗', 1, 1962, 1966, '任期屆滿', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records; first Primate'),
('佛蘭克·費爾斯', 'Frank Woods', '澳洲聖公宗', '澳洲聖公宗', 2, 1966, 1977, '退休', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records'),
('馬庫斯·貝恩', 'Marcus Loane', '澳洲聖公宗', '澳洲聖公宗', 3, 1977, 1982, '退休', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records; first Australian-born Primate'),
('唐納德·羅賓遜', 'Donald Robinson', '澳洲聖公宗', '澳洲聖公宗', 4, 1982, 1993, '退休', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records'),
('基斯·雷德福', 'Keith Rayner', '澳洲聖公宗', '澳洲聖公宗', 5, 1991, 2000, '退休', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records'),
('彼得·詹森', 'Peter Jensen', '澳洲聖公宗', '澳洲聖公宗', 6, 2001, 2013, '退休', '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records'),
('杰弗里·史密斯', 'Geoffrey Smith', '澳洲聖公宗', '澳洲聖公宗', 7, 2014, NULL, NULL, '澳洲聖公宗大會', '正統', 'Anglican Church of Australia records');

-- 設定 predecessor_id（各 see 內連鏈）
UPDATE episcopal_succession es
SET predecessor_id = prev.id
FROM (
  SELECT id,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see IN ('阿馬', '威爾士', '美國聖公會', '加拿大聖公宗', '澳洲聖公宗')
    AND church IN ('愛爾蘭教會', '威爾士教會', '美國聖公會', '加拿大聖公宗', '澳洲聖公宗')
) prev
WHERE es.id = prev.id AND prev.prev_id IS NOT NULL;
