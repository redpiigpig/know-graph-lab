-- ============================================================
-- 聖公會及拉丁禮歷史宗主教座繼承列表
-- GROUP C: 都柏林（愛爾蘭教會）、蘇格蘭聖公會首席主教、香港聖公宗
-- GROUP D: 阿奎萊亞、格拉多、迦太基、西印度群島
-- ============================================================

-- ============================================================
-- 6. 都柏林 / 愛爾蘭教會（Church of Ireland）
-- 宗教改革後（1536年起）都柏林大主教列表
-- 1650–1661年空位（清教徒共和國時期）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('喬治·布朗尼', 'George Browne', '都柏林', '愛爾蘭教會', 1, 1536, 1554, '廢黜', '正統', 'DNB; Cotton, Fasti Ecclesiae Hibernicae', '宗教改革首位都柏林大主教；由坎特伯里大主教克蘭默祝聖；瑪麗一世復辟天主教後被廢黜'),
('休·科文', 'Hugh Curwen', '都柏林', '愛爾蘭教會', 2, 1555, 1567, '調任', '正統', 'DNB; Cotton, Fasti Ecclesiae Hibernicae', '瑪麗女王任命；伊利莎白即位後改信新教繼續任職；1567年調任牛津主教'),
('亞當·洛夫特斯', 'Adam Loftus', '都柏林', '愛爾蘭教會', 3, 1567, 1605, '逝世', '正統', 'DNB; Cotton, Fasti', '伊莉莎白時代最重要的愛爾蘭教會人物；三一學院都柏林首任院長（1592年）；兼任愛爾蘭大法官'),
('托馬斯·瓊斯', 'Thomas Jones', '都柏林', '愛爾蘭教會', 4, 1605, 1619, '逝世', '正統', 'Cotton, Fasti', NULL),
('蘭斯洛特·巴爾克利', 'Lancelot Bulkeley', '都柏林', '愛爾蘭教會', 5, 1619, 1650, '逝世', '正統', 'Cotton, Fasti', '任內歷經愛爾蘭1641年天主教起義'),
-- 1650–1661 空位（克倫威爾共和國時期）
('詹姆斯·馬爾傑森', 'James Margetson', '都柏林', '愛爾蘭教會', 6, 1661, 1663, '調任', '正統', 'Cotton, Fasti', '王政復辟後首任；調任阿瑪大主教'),
('邁克爾·博伊爾', 'Michael Boyle', '都柏林', '愛爾蘭教會', 7, 1663, 1679, '調任', '正統', 'Cotton, Fasti', '調任阿瑪大主教'),
('約翰·帕克', 'John Parker', '都柏林', '愛爾蘭教會', 8, 1679, 1681, '逝世', '正統', 'Cotton, Fasti', NULL),
('弗朗西斯·馬什', 'Francis Marsh', '都柏林', '愛爾蘭教會', 9, 1682, 1693, '逝世', '正統', 'Cotton, Fasti', NULL),
('納西索斯·馬什', 'Narcissus Marsh', '都柏林', '愛爾蘭教會', 10, 1694, 1703, '調任', '正統', 'Cotton, Fasti', '著名學者；創建馬什圖書館（都柏林最古老公共圖書館，1707年）；調任阿瑪大主教'),
('威廉·金', 'William King', '都柏林', '愛爾蘭教會', 11, 1703, 1729, '逝世', '正統', 'Cotton, Fasti', NULL),
('約翰·霍德利', 'John Hoadly', '都柏林', '愛爾蘭教會', 12, 1730, 1742, '調任', '正統', 'Cotton, Fasti', '調任阿瑪大主教'),
('查爾斯·科比', 'Charles Cobbe', '都柏林', '愛爾蘭教會', 13, 1743, 1765, '逝世', '正統', 'Cotton, Fasti', NULL),
('威廉·卡邁克爾', 'William Carmichael', '都柏林', '愛爾蘭教會', 14, 1765, 1765, '逝世', '正統', 'Cotton, Fasti', '在位僅數月'),
('阿瑟·史密斯', 'Arthur Smyth', '都柏林', '愛爾蘭教會', 15, 1766, 1771, '逝世', '正統', 'Cotton, Fasti', NULL),
('約翰·克拉多克', 'John Cradock', '都柏林', '愛爾蘭教會', 16, 1772, 1778, '逝世', '正統', 'Cotton, Fasti', NULL),
('羅伯特·福勒', 'Robert Fowler', '都柏林', '愛爾蘭教會', 17, 1779, 1801, '逝世', '正統', 'Cotton, Fasti', NULL),
('查爾斯·阿加爾', 'Charles Agar', '都柏林', '愛爾蘭教會', 18, 1801, 1809, '逝世', '正統', 'Cotton, Fasti', NULL),
('尤西比·克利弗', 'Euseby Cleaver', '都柏林', '愛爾蘭教會', 19, 1809, 1819, '逝世', '正統', 'Cotton, Fasti', NULL),
('約翰·貝雷斯福德勛爵', 'Lord John Beresford', '都柏林', '愛爾蘭教會', 20, 1820, 1822, '調任', '正統', 'Cotton, Fasti', '調任阿瑪大主教'),
('威廉·馬基', 'William Magee', '都柏林', '愛爾蘭教會', 21, 1822, 1831, '逝世', '正統', 'Cotton, Fasti', NULL),
('理查德·惠特利', 'Richard Whately', '都柏林', '愛爾蘭教會', 22, 1831, 1863, '逝世', '正統', 'DNB; Cotton, Fasti', '著名邏輯學家和政治經濟學家'),
('理查德·謝尼維克斯·特倫奇', 'Richard Chenevix Trench', '都柏林', '愛爾蘭教會', 23, 1864, 1884, '辭職', '正統', 'DNB', '著名語言學家；倡議編撰《牛津英語詞典》；因健康原因辭職'),
('威廉·普朗基特', 'William Conyngham Plunket', '都柏林', '愛爾蘭教會', 24, 1885, 1897, '逝世', '正統', 'Cotton, Fasti', NULL),
('約瑟夫·皮科克', 'Joseph Ferguson Peacocke', '都柏林', '愛爾蘭教會', 25, 1897, 1915, '辭職', '正統', 'Church of Ireland records', NULL),
('約翰·貝爾納德', 'John Henry Bernard', '都柏林', '愛爾蘭教會', 26, 1915, 1919, '辭職', '正統', 'DNB', '著名神學家和愛爾蘭研究者；出任都柏林三一學院院長後辭職'),
('查爾斯·達西', 'Charles Frederick D''Arcy', '都柏林', '愛爾蘭教會', 27, 1919, 1920, '調任', '正統', 'Church of Ireland records', '調任阿瑪大主教'),
('約翰·格雷格', 'John Allen Fitzgerald Gregg', '都柏林', '愛爾蘭教會', 28, 1920, 1939, '調任', '正統', 'Church of Ireland records', '調任阿瑪大主教'),
('亞瑟·巴頓', 'Arthur William Barton', '都柏林', '愛爾蘭教會', 29, 1939, 1956, '退休', '正統', 'Church of Ireland records', NULL),
('喬治·西姆斯', 'George Otto Simms', '都柏林', '愛爾蘭教會', 30, 1956, 1969, '調任', '正統', 'Church of Ireland records', '調任阿瑪大主教；著名《凱爾斯書》（Book of Kells）研究者'),
('艾倫·布坎南', 'Alan Alexander Buchanan', '都柏林', '愛爾蘭教會', 31, 1969, 1977, '退休', '正統', 'Church of Ireland records', NULL),
('亨利·麥卡杜', 'Henry Robert McAdoo', '都柏林', '愛爾蘭教會', 32, 1977, 1985, '退休', '正統', 'Church of Ireland records', '著名合一運動神學家；聖公會—羅馬天主教國際委員會（ARCIC）共同主席'),
('唐納德·凱爾德', 'Donald Isaac Caird', '都柏林', '愛爾蘭教會', 33, 1985, 1996, '退休', '正統', 'Church of Ireland records', NULL),
('沃爾頓·恩佩', 'Walton Newcombe Francis Empey', '都柏林', '愛爾蘭教會', 34, 1996, 2002, '退休', '正統', 'Church of Ireland records', NULL),
('約翰·尼爾', 'John Robert Winder Neill', '都柏林', '愛爾蘭教會', 35, 2002, 2011, '退休', '正統', 'Church of Ireland records', NULL),
('邁克爾·傑克遜', 'Michael Geoffrey St Aubyn Jackson', '都柏林', '愛爾蘭教會', 36, 2011, NULL, NULL, '正統', 'Church of Ireland records', '現任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '都柏林' AND church = '愛爾蘭教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 7. 蘇格蘭聖公會 / 首席主教（Primus）
-- 1720年設立此職至今；Primus無都主教管轄權，為禮儀上的首席
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('約翰·富勒頓', 'John Fullarton', '蘇格蘭聖公會', '蘇格蘭聖公會', 1, 1720, 1727, '逝世', '正統', 'Scottish Episcopal Church records', '愛丁堡主教；首任Primus'),
('阿瑟·米勒', 'Arthur Millar', '蘇格蘭聖公會', '蘇格蘭聖公會', 2, 1727, 1727, '逝世', '正統', 'Scottish Episcopal Church records', '愛丁堡主教；在任僅數月'),
('安德魯·盧姆斯登', 'Andrew Lumsden', '蘇格蘭聖公會', '蘇格蘭聖公會', 3, 1727, 1731, '逝世', '正統', 'Scottish Episcopal Church records', '愛丁堡主教'),
('大衛·弗里貝恩', 'David Freebairn', '蘇格蘭聖公會', '蘇格蘭聖公會', 4, 1731, 1738, '逝世', '正統', 'Scottish Episcopal Church records', '加洛韋主教，後任愛丁堡主教'),
('托馬斯·拉特雷', 'Thomas Rattray', '蘇格蘭聖公會', '蘇格蘭聖公會', 5, 1738, 1743, '逝世', '正統', 'Scottish Episcopal Church records', '鄧凱爾德主教；重要的禮儀神學家，著有研究早期禮儀的重要著作'),
('羅伯特·基思', 'Robert Keith', '蘇格蘭聖公會', '蘇格蘭聖公會', 6, 1743, 1757, '逝世', '正統', 'Scottish Episcopal Church records', '凱斯尼斯、奧克尼及群島主教；重要教會歷史學家'),
('羅伯特·懷特', 'Robert White', '蘇格蘭聖公會', '蘇格蘭聖公會', 7, 1757, 1761, '逝世', '正統', 'Scottish Episcopal Church records', '法夫主教'),
('威廉·福爾科納', 'William Falconer', '蘇格蘭聖公會', '蘇格蘭聖公會', 8, 1762, 1782, '逝世', '正統', 'Scottish Episcopal Church records', '莫里主教，後任愛丁堡主教'),
('羅伯特·基爾古爾', 'Robert Kilgour', '蘇格蘭聖公會', '蘇格蘭聖公會', 9, 1782, 1788, '退休', '正統', 'Scottish Episcopal Church records', '阿伯丁主教；1784年按立美國聖公會首任主教塞繆爾·錫伯里（Samuel Seabury）——重要的聖公宗歷史'),
('約翰·斯金納（父）', 'John Skinner the Elder', '蘇格蘭聖公會', '蘇格蘭聖公會', 10, 1788, 1816, '逝世', '正統', 'Scottish Episcopal Church records', '阿伯丁主教；1792年解禁法後推動蘇格蘭聖公會公開復興'),
('喬治·格利格', 'George Gleig', '蘇格蘭聖公會', '蘇格蘭聖公會', 11, 1816, 1837, '逝世', '正統', 'Scottish Episcopal Church records', '佈雷欽主教'),
('詹姆斯·沃克', 'James Walker', '蘇格蘭聖公會', '蘇格蘭聖公會', 12, 1837, 1841, '逝世', '正統', 'Scottish Episcopal Church records', '愛丁堡主教'),
('威廉·斯金納（子）', 'William Skinner the Younger', '蘇格蘭聖公會', '蘇格蘭聖公會', 13, 1841, 1857, '逝世', '正統', 'Scottish Episcopal Church records', '阿伯丁主教'),
('查爾斯·特羅特', 'Charles Hughes Terrot', '蘇格蘭聖公會', '蘇格蘭聖公會', 14, 1857, 1862, '逝世', '正統', 'Scottish Episcopal Church records', '愛丁堡主教；著名數學家'),
('羅伯特·伊登', 'Robert John Eden', '蘇格蘭聖公會', '蘇格蘭聖公會', 15, 1862, 1886, '退休', '正統', 'Scottish Episcopal Church records', '莫里、羅斯及凱斯尼斯主教'),
('休·傑明', 'Hugh Willoughby Jermyn', '蘇格蘭聖公會', '蘇格蘭聖公會', 16, 1886, 1901, '逝世', '正統', 'Scottish Episcopal Church records', '佈雷欽主教'),
('詹姆斯·凱利', 'James Francis Kelly', '蘇格蘭聖公會', '蘇格蘭聖公會', 17, 1901, 1904, '逝世', '正統', 'Scottish Episcopal Church records', '莫里、羅斯及凱斯尼斯主教'),
('喬治·威爾金森', 'George Howard Wilkinson', '蘇格蘭聖公會', '蘇格蘭聖公會', 18, 1904, 1907, '退休', '正統', 'Scottish Episcopal Church records', '聖安德魯斯、鄧凱爾德及鄧布蘭主教'),
('沃爾特·羅伯茨', 'Walter John Forbes Robberds', '蘇格蘭聖公會', '蘇格蘭聖公會', 19, 1908, 1934, '退休', '正統', 'Scottish Episcopal Church records', '佈雷欽主教；在任最長（26年）'),
('阿瑟·麥克萊恩', 'Arthur John Maclean', '蘇格蘭聖公會', '蘇格蘭聖公會', 20, 1935, 1943, '逝世', '正統', 'Scottish Episcopal Church records', '莫里、羅斯及凱斯尼斯主教'),
('洛吉·丹森', 'Ernest Dobrée Logie Danson', '蘇格蘭聖公會', '蘇格蘭聖公會', 21, 1943, 1946, '退休', '正統', 'Scottish Episcopal Church records', '愛丁堡主教'),
('約翰·豪', 'John William Charles Wand', '蘇格蘭聖公會', '蘇格蘭聖公會', 22, 1946, 1952, '退休', '正統', 'Scottish Episcopal Church records', '格拉斯哥及加洛韋主教'),
('托馬斯·漢納', 'Thomas Hannay', '蘇格蘭聖公會', '蘇格蘭聖公會', 23, 1952, 1962, '退休', '正統', 'Scottish Episcopal Church records', '阿蓋爾及群島主教'),
('弗朗西斯·蒙克里夫', 'Francis Halliday Moncreiff', '蘇格蘭聖公會', '蘇格蘭聖公會', 24, 1962, 1973, '退休', '正統', 'Scottish Episcopal Church records', '格拉斯哥及加洛韋主教'),
('理查德·溫布什', 'Richard Knyvet Wimbush', '蘇格蘭聖公會', '蘇格蘭聖公會', 25, 1974, 1977, '退休', '正統', 'Scottish Episcopal Church records', '阿蓋爾及群島主教'),
('阿拉斯泰爾·哈格特', 'Alastair Iain Macdonald Haggart', '蘇格蘭聖公會', '蘇格蘭聖公會', 26, 1977, 1985, '退休', '正統', 'Scottish Episcopal Church records', '愛丁堡主教'),
('特德·拉斯科姆', 'Frederick Goldie (Ted) Luscombe', '蘇格蘭聖公會', '蘇格蘭聖公會', 27, 1985, 1990, '退休', '正統', 'Scottish Episcopal Church records', '佈雷欽主教'),
('喬治·亨德森', 'George Kennedy Buchanan Henderson', '蘇格蘭聖公會', '蘇格蘭聖公會', 28, 1990, 1992, '退休', '正統', 'Scottish Episcopal Church records', '阿蓋爾及群島主教'),
('理查德·霍洛韋', 'Richard Frederick Holloway', '蘇格蘭聖公會', '蘇格蘭聖公會', 29, 1992, 2000, '辭職', '正統', 'Scottish Episcopal Church records', '愛丁堡主教；引發爭議的自由神學立場（支持同性戀關係等）；2000年辭去Primus及主教職'),
('布魯斯·卡梅倫', 'Andrew Bruce Cameron', '蘇格蘭聖公會', '蘇格蘭聖公會', 30, 2000, 2006, '退休', '正統', 'Scottish Episcopal Church records', '阿伯丁及奧克尼主教'),
('伊德里斯·瓊斯', 'Idris Jones', '蘇格蘭聖公會', '蘇格蘭聖公會', 31, 2006, 2009, '退休', '正統', 'Scottish Episcopal Church records', '格拉斯哥及加洛韋主教'),
('大衛·奇林沃思', 'David Robert Chillingworth', '蘇格蘭聖公會', '蘇格蘭聖公會', 32, 2009, 2016, '退休', '正統', 'Scottish Episcopal Church records', '聖安德魯斯、鄧凱爾德及鄧布蘭主教'),
('馬克·斯特蘭奇', 'Mark Jeremy Strange', '蘇格蘭聖公會', '蘇格蘭聖公會', 33, 2017, NULL, NULL, '正統', 'Scottish Episcopal Church records', '現任；莫里、羅斯及凱斯尼斯主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '蘇格蘭聖公會' AND church = '蘇格蘭聖公會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 8. 香港聖公宗 / 香港聖公宗（HKSKH）
-- 先列維多利亞教區（1849–1951）及香港澳門教區（1951–1998）主教，
-- 後列香港聖公宗省（1998年成立）歷任大主教。
-- 任次連貫計算（省成立前後視同一統緒）。
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('佐治·史密夫', 'George Smith', '香港聖公宗', '香港聖公宗', 1, 1849, 1865, '退休', '正統', 'Church Missionary Society records; Lambeth Palace records', '維多利亞教區（Diocese of Victoria）首任主教；管轄香港及華南地區'),
('查理士·阿爾福德', 'Charles Richard Alford', '香港聖公宗', '香港聖公宗', 2, 1867, 1872, '辭職', '正統', 'Lambeth Palace records', NULL),
('約翰·柏頓', 'John Shaw Burdon', '香港聖公宗', '香港聖公宗', 3, 1874, 1897, '退休', '正統', 'Church Missionary Society records', '著名傳教士和漢學家；曾在中國多年傳教'),
('約瑟·霍爾', 'Joseph Charles Hoare', '香港聖公宗', '香港聖公宗', 4, 1898, 1906, '逝世', '正統', 'Lambeth Palace records', NULL),
('嘉輔利·蘭達爾', 'Gerard Heath Lander', '香港聖公宗', '香港聖公宗', 5, 1907, 1920, '辭職', '正統', 'Lambeth Palace records', NULL),
('李道普', 'Llewellyn Ridley Duppuy', '香港聖公宗', '香港聖公宗', 6, 1920, 1932, '辭職', '正統', 'Lambeth Palace records', NULL),
('何明華', 'Ronald Owen Hall', '香港聖公宗', '香港聖公宗', 7, 1932, 1966, '退休', '正統', 'HKU Press; HKSKH Archives', '1932年任維多利亞主教，1951年改任香港澳門教區首任主教；著名社會改革者；1944年祝立李添嬡（Florence Li Tim-Oi）為司鐸——聖公宗史上首位女性司鐸；教座改稱「香港澳門」（1951年）'),
('貝克爾', 'John Gilbert Hindley Baker', '香港聖公宗', '香港聖公宗', 8, 1966, 1980, '退休', '正統', 'HKSKH Archives', NULL),
('鄺廣傑', 'Peter Kwong Kong-kit', '香港聖公宗', '香港聖公宗', 9, 1981, 2006, '退休', '正統', 'HKSKH official records', '1981年任香港澳門主教；1998年香港聖公宗省成立後出任首任大主教（1998–2006）'),
('鄺保羅', 'Paul Kwong Kin-ho', '香港聖公宗', '香港聖公宗', 10, 2007, 2021, '退休', '正統', 'HKSKH official records', '2007年升任大主教；任內同時兼任香港島主教；2020年宣佈退休，2021年1月正式離任'),
('陳謳明', 'Andrew Chan Au-ming', '香港聖公宗', '香港聖公宗', 11, 2021, NULL, NULL, '正統', 'HKSKH official records; Anglican Ink 2020', '現任大主教（2021年1月就任）；同時兼任西九龍主教；被評為立場較非政治化的主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '香港聖公宗' AND church = '香港聖公宗'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 9. 阿奎萊亞 / 天主教（拉丁禮）
-- 539年首任宗主教至1751年廢除
-- 606年後三章爭議分裂為舊阿奎萊亞（本表）和格拉多（新阿奎萊亞）兩線
-- 698/700年恢復羅馬共融，結束分裂
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('馬其頓烏斯', 'Macedonius of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 1, 539, 556, '逝世', '正統', 'Paulus Diaconus, Historia Langobardorum; Jaffé, Regesta', '首任冠用「宗主教」頭銜者；因反對第五次公會議（553年）譴責三章而脫離羅馬共融'),
('保利努斯一世', 'Paulinus I of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 2, 557, 569, '逝世', '正統', 'Paulus Diaconus', '568年倫巴底人入侵後攜寶物遷往格拉多島；「宗主教」頭銜正式使用確立'),
('普羅比努斯', 'Probinus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 3, 569, 570, '逝世', '正統', 'Paulus Diaconus', NULL),
('以利亞', 'Elia of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 4, 571, 586, '逝世', '正統', 'Paulus Diaconus', '三章分裂期間護衛立場'),
('塞維魯斯', 'Severus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 5, 586, 606, '逝世', '正統', 'Paulus Diaconus', '606年逝世後教區分裂：親拜占廷派在格拉多另立坎迪代亞努斯（恢復羅馬共融）；親倫巴底派在舊阿奎萊亞另立約翰一世（繼續分裂）'),
('約翰一世', 'John I of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 6, 606, 623, '逝世', '正統', 'Paulus Diaconus', '舊阿奎萊亞（倫巴底系）；拒絕羅馬共融；在大陸（後遷科爾莫納斯）'),
('馬爾基亞努斯', 'Marcianus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 7, 623, 628, '逝世', '正統', 'Paulus Diaconus', NULL),
('福爾圖納圖斯', 'Fortunatus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 8, 628, 663, '逝世', '正統', 'Paulus Diaconus', NULL),
('彼得一世', 'Petrus I of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 9, 698, 700, '逝世', '正統', 'Jaffé, Regesta', '恢復與羅馬教宗共融——三章分裂（606–698）正式結束'),
('謝雷努斯', 'Serenus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 10, 711, 723, '逝世', '正統', 'Jaffé, Regesta', NULL),
('卡利克斯圖斯', 'Calixtus of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 11, 726, 734, '逝世', '正統', 'Jaffé, Regesta', '將宗主教座遷往奇維達萊（Cividale del Friuli）'),
('西瓜爾德', 'Siguald of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 12, 762, 776, '逝世', '正統', 'Jaffé, Regesta', NULL),
('保利努斯二世', 'Paulinus II of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 13, 776, 802, '逝世', '正統', 'MGH; Jaffé, Regesta', '查理大帝的重要神學顧問；796年弗里烏利公會議；後被封聖'),
('烏爾蘇斯一世', 'Ursus I of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 14, 802, 811, '逝世', '正統', 'Jaffé, Regesta', NULL),
('馬克森提烏斯', 'Maxentius of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 15, 811, 833, '逝世', '正統', 'Jaffé, Regesta', NULL),
('安德里亞斯', 'Andreas of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 16, 834, 844, '逝世', '正統', 'Jaffé, Regesta', NULL),
('瓦爾佩特', 'Valpert of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 17, 875, 899, '逝世', '正統', 'Jaffé, Regesta', NULL),
('弗雷德里克一世', 'Frederick I of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 18, 901, 922, '逝世', '正統', 'Jaffé, Regesta', NULL),
('烏爾蘇斯二世', 'Ursus II of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 19, 928, 931, '逝世', '正統', 'Jaffé, Regesta', NULL),
('恩格爾弗雷德', 'Engelfred of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 20, 944, 963, '逝世', '正統', 'Jaffé, Regesta', NULL),
('羅多阿爾德', 'Rodoald of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 21, 963, 984, '逝世', '正統', 'Jaffé, Regesta', NULL),
('約翰四世', 'John IV of Ravenna (Aquileia)', '阿奎萊亞', '天主教（拉丁禮）', 22, 984, 1017, '逝世', '正統', 'Jaffé, Regesta', NULL),
('波波', 'Poppo (Wolfgang) of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 23, 1019, 1042, '逝世', '正統', 'Jaffé, Regesta', '重要的中世紀藝術贊助者'),
('埃伯哈德', 'Eberhard of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 24, 1045, 1049, '逝世', '正統', 'Jaffé, Regesta', NULL),
('哥特博爾德', 'Gotebald of Aquileia', '阿奎萊亞', '天主教（拉丁禮）', 25, 1049, 1063, '逝世', '正統', 'Jaffé, Regesta', NULL),
('烏爾里希一世', 'Ulrich I of Eppenstein', '阿奎萊亞', '天主教（拉丁禮）', 26, 1086, 1121, '逝世', '正統', 'Jaffé, Regesta', NULL),
('佩萊格里諾一世', 'Pellegrino I of Ortenbourg', '阿奎萊亞', '天主教（拉丁禮）', 27, 1130, 1161, '逝世', '正統', 'Jaffé, Regesta', '阿奎萊亞政治力量最強盛時期'),
('烏爾里希二世', 'Ulrich II of Treven', '阿奎萊亞', '天主教（拉丁禮）', 28, 1161, 1181, '逝世', '正統', 'Jaffé, Regesta', NULL),
('佩萊格里諾二世', 'Pellegrino II of Ortenburg-Sponheim', '阿奎萊亞', '天主教（拉丁禮）', 29, 1195, 1204, '逝世', '正統', 'Jaffé, Regesta', NULL),
('貝托爾德', 'Berthold of Merania', '阿奎萊亞', '天主教（拉丁禮）', 30, 1218, 1251, '逝世', '正統', 'Jaffé, Regesta', '將宗主教座遷往烏迪內（Udine）'),
('格雷戈里奧·蒙泰隆戈', 'Gregorio of Montelongo', '阿奎萊亞', '天主教（拉丁禮）', 31, 1251, 1269, '逝世', '正統', 'Jaffé, Regesta', NULL),
('雷蒙多·德拉托雷', 'Raimondo della Torre', '阿奎萊亞', '天主教（拉丁禮）', 32, 1273, 1299, '逝世', '正統', 'Jaffé, Regesta', NULL),
('帕加諾·德拉托雷', 'Pagano della Torre', '阿奎萊亞', '天主教（拉丁禮）', 33, 1319, 1332, '逝世', '正統', 'Jaffé, Regesta', NULL),
('貝特朗·德聖日內修斯', 'Bertram of St. Genesius', '阿奎萊亞', '天主教（拉丁禮）', 34, 1334, 1350, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('盧多維科·德拉托雷', 'Lodovico della Torre', '阿奎萊亞', '天主教（拉丁禮）', 35, 1359, 1365, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('馬夸德·馮·蘭德克', 'Marquard of Randeck', '阿奎萊亞', '天主教（拉丁禮）', 36, 1365, 1381, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('約翰·德莫拉維亞', 'John of Moravia', '阿奎萊亞', '天主教（拉丁禮）', 37, 1387, 1394, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('安托尼奧一世·蓋塔尼', 'Antonio I Caetani', '阿奎萊亞', '天主教（拉丁禮）', 38, 1394, 1402, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('安托尼奧二世·潘奇埃拉', 'Antonio II Panciera', '阿奎萊亞', '天主教（拉丁禮）', 39, 1402, 1412, '調任', '正統', 'Eubel, Hierarchia Catholica', '升任樞機；1409–1412年另有對立宗主教安托尼奧三世'),
('盧多維科·德·特克', 'Louis of Teck', '阿奎萊亞', '天主教（拉丁禮）', 40, 1412, 1435, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('盧多維科·特雷維桑', 'Ludovico Trevisan', '阿奎萊亞', '天主教（拉丁禮）', 41, 1439, 1465, '逝世', '正統', 'Eubel, Hierarchia Catholica', '樞機；著名人文主義者'),
('馬可一世·巴爾博', 'Marco I Barbo', '阿奎萊亞', '天主教（拉丁禮）', 42, 1465, 1491, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('多明我·格里馬尼', 'Domenico Grimani', '阿奎萊亞', '天主教（拉丁禮）', 43, 1498, 1517, '辭職', '正統', 'Eubel, Hierarchia Catholica', '樞機；著名人文主義者和藝術品收藏家'),
('馬里諾·格里馬尼', 'Marino Grimani', '阿奎萊亞', '天主教（拉丁禮）', 44, 1517, 1529, '辭職', '正統', 'Eubel, Hierarchia Catholica', NULL),
('馬可二世·格里馬尼', 'Marco II Grimani', '阿奎萊亞', '天主教（拉丁禮）', 45, 1529, 1533, '辭職', '正統', 'Eubel, Hierarchia Catholica', NULL),
('馬里諾·格里馬尼（第二任期）', 'Marino Grimani (2nd tenure)', '阿奎萊亞', '天主教（拉丁禮）', 46, 1533, 1545, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('喬凡尼六世·格里馬尼', 'Giovanni VI Grimani', '阿奎萊亞', '天主教（拉丁禮）', 47, 1545, 1593, '逝世', '正統', 'Eubel, Hierarchia Catholica', '在位近50年；1570–1585年間曾短暫讓位，後復位'),
('弗朗切斯科·巴爾巴羅', 'Francesco Barbaro', '阿奎萊亞', '天主教（拉丁禮）', 48, 1593, 1616, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('馬可·格拉代尼戈', 'Marco Gradenigo', '阿奎萊亞', '天主教（拉丁禮）', 49, 1629, 1656, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('喬凡尼七世·多爾芬諾', 'Giovanni VII Dolfino', '阿奎萊亞', '天主教（拉丁禮）', 50, 1657, 1699, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('狄俄尼修斯·多爾芬諾', 'Dionisio Dolfino', '阿奎萊亞', '天主教（拉丁禮）', 51, 1699, 1734, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('達尼埃萊二世·多爾芬諾樞機', 'Daniel II Cardinal Dolfino', '阿奎萊亞', '天主教（拉丁禮）', 52, 1734, 1751, '不明', '正統', 'Eubel, Hierarchia Catholica', '末任阿奎萊亞宗主教；1751年教宗本篤十四世廢除阿奎萊亞宗主教區，分為戈里齊亞和烏迪內兩個總主教區；本人繼任烏迪內總主教（1752–1762）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '阿奎萊亞' AND church = '天主教（拉丁禮）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 10. 格拉多 / 天主教（拉丁禮）
-- 606年三章分裂後由親拜占廷一支成立的新阿奎萊亞宗主教座
-- 宗主教座先在格拉多島，後遷威尼斯
-- 1451年廢除，與卡斯泰洛教區合併為威尼斯大主教區
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('坎迪代亞努斯', 'Candidianus of Grado', '格拉多', '天主教（拉丁禮）', 1, 606, 612, '逝世', '正統', 'Paulus Diaconus; Jaffé, Regesta', '塞維魯斯逝世後由拜占廷支持的派別選出；立即恢復與羅馬共融；「新阿奎萊亞」宗主教座正式成立'),
('埃皮法尼烏斯', 'Epiphanius of Grado', '格拉多', '天主教（拉丁禮）', 2, 612, 613, '逝世', '正統', 'Jaffé, Regesta', NULL),
('基布里亞努斯', 'Cyprianus of Grado', '格拉多', '天主教（拉丁禮）', 3, 613, 627, '逝世', '正統', 'Jaffé, Regesta', NULL),
('福爾圖納圖斯一世', 'Fortunatus I of Grado', '格拉多', '天主教（拉丁禮）', 4, 627, 628, '逝世', '正統', 'Jaffé, Regesta', NULL),
('普里莫根尼烏斯', 'Primogenius of Grado', '格拉多', '天主教（拉丁禮）', 5, 630, 647, '逝世', '正統', 'Jaffé, Regesta', NULL),
('斯特凡努斯二世', 'Stephanus II of Grado', '格拉多', '天主教（拉丁禮）', 6, 670, 672, '逝世', '正統', 'Jaffé, Regesta', NULL),
('克里斯托福魯斯', 'Christophorus of Grado', '格拉多', '天主教（拉丁禮）', 7, 682, 717, '逝世', '正統', 'Jaffé, Regesta', NULL),
('多納圖斯', 'Donatus of Grado', '格拉多', '天主教（拉丁禮）', 8, 717, 725, '逝世', '正統', 'Jaffé, Regesta', NULL),
('安托尼努斯', 'Antoninus of Grado', '格拉多', '天主教（拉丁禮）', 9, 725, 747, '逝世', '正統', 'Jaffé, Regesta', NULL),
('維塔利亞努斯', 'Vitalianus of Grado', '格拉多', '天主教（拉丁禮）', 10, 755, 767, '逝世', '正統', 'Jaffé, Regesta', NULL),
('喬凡尼四世', 'Giovanni IV of Grado', '格拉多', '天主教（拉丁禮）', 11, 767, 802, '逝世', '正統', 'Jaffé, Regesta', NULL),
('福爾圖納圖斯二世', 'Fortunatus II of Grado', '格拉多', '天主教（拉丁禮）', 12, 802, 820, '流亡', '正統', 'Jaffé, Regesta', '813年被拜占廷皇帝放逐；逃往法蘭克宮廷（查理大帝廷）後流亡'),
('喬凡尼五世', 'Giovanni V of Grado', '格拉多', '天主教（拉丁禮）', 13, 820, 825, '逝世', '正統', 'Jaffé, Regesta', NULL),
('維內里烏斯·特拉斯蒙多', 'Venerius Trasmondo', '格拉多', '天主教（拉丁禮）', 14, 825, 851, '逝世', '正統', 'Jaffé, Regesta', NULL),
('維塔利斯四世·坎迪亞諾', 'Vitalis IV Candiano', '格拉多', '天主教（拉丁禮）', 15, 976, 1017, '逝世', '正統', 'Jaffé, Regesta', NULL),
('歐爾索·奧爾謝奧洛', 'Orso Orseolo', '格拉多', '天主教（拉丁禮）', 16, 1018, 1049, '逝世', '正統', 'Jaffé, Regesta', '遷居威尼斯時期；開始在威尼斯實際居住'),
('彼得羅二世·巴多爾', 'Petrus II Badoer', '格拉多', '天主教（拉丁禮）', 17, 1092, 1105, '逝世', '正統', 'Jaffé, Regesta', NULL),
('恩里科·丹多洛', 'Enrico Dandolo of Grado', '格拉多', '天主教（拉丁禮）', 18, 1134, 1182, '逝世', '正統', 'Jaffé, Regesta', '注意：此人與第四次十字軍東征（1204年）威尼斯總督恩里科·丹多洛同名但非同一人'),
('喬凡尼·塞尼亞萊', 'Giovanni Segnale', '格拉多', '天主教（拉丁禮）', 19, 1182, 1201, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('貝內代托·法利埃爾', 'Benedetto Falier', '格拉多', '天主教（拉丁禮）', 20, 1201, 1207, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('安傑洛·巴羅齊', 'Angelo Barozzi', '格拉多', '天主教（拉丁禮）', 21, 1211, 1238, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('萊昂納多·奎里尼', 'Leonardo Querini', '格拉多', '天主教（拉丁禮）', 22, 1238, 1244, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('安傑洛·馬爾特拉維爾索', 'Angelo Maltraverso', '格拉多', '天主教（拉丁禮）', 23, 1255, 1272, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('奧爾索·德爾菲諾', 'Orso Delfino', '格拉多', '天主教（拉丁禮）', 24, 1355, 1361, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('托馬斯·德弗里尼亞諾', 'Thomas of Frignano', '格拉多', '天主教（拉丁禮）', 25, 1372, 1383, '晉升', '正統', 'Eubel, Hierarchia Catholica', '升任樞機'),
('萊昂納多·德爾菲諾', 'Leonardo Delfino', '格拉多', '天主教（拉丁禮）', 26, 1409, 1427, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('比亞焦·莫利諾', 'Biagio Molino', '格拉多', '天主教（拉丁禮）', 27, 1427, 1439, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('馬可·孔杜爾梅爾', 'Marco Condulmer', '格拉多', '天主教（拉丁禮）', 28, 1439, 1445, '逝世', '正統', 'Eubel, Hierarchia Catholica', NULL),
('多明我·米凱爾', 'Domenico Michiel', '格拉多', '天主教（拉丁禮）', 29, 1445, 1451, '不明', '正統', 'Eubel, Hierarchia Catholica', '末任格拉多宗主教；1451年教宗尼古拉五世頒佈《永恆王的詔書》（Regis aeterni），格拉多宗主教區與卡斯泰洛主教區合併，成立威尼斯大主教區');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '格拉多' AND church = '天主教（拉丁禮）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 11. 迦太基 / 天主教（拉丁禮）
-- 早期基督教非洲的首席主教座
-- 698年阿拉伯人攻克迦太基後主教區實際中斷
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿格里皮努斯', 'Agrippinus of Carthage', '迦太基', '天主教（拉丁禮）', 1, 230, 240, '不明', '正統', 'Cyprian, Ep. 71; 73', '有史可查的第一位確定無疑的迦太基主教；主持地方公會議討論洗禮問題'),
('多納圖斯一世', 'Donatus I of Carthage', '迦太基', '天主教（拉丁禮）', 2, 240, 248, '不明', '正統', 'Cyprian, Ep. 59', NULL),
('喀普里亞努斯', 'Cyprian of Carthage', '迦太基', '天主教（拉丁禮）', 3, 249, 258, '殉道', '正統', 'Pontius Diaconus, Vita Cypriani; Eusebius, HE VII.3', '北非教父；著名神學家；德西烏斯迫害（250年）期間領導教會；258年9月14日被斬首；非洲教會史上最偉大的主教'),
('路卡努斯', 'Lucianus of Carthage', '迦太基', '天主教（拉丁禮）', 4, 258, 265, '不明', '正統', 'Pseudo-Cyprian', NULL),
('卡爾波福魯斯', 'Carpophorus of Carthage', '迦太基', '天主教（拉丁禮）', 5, 265, 295, '不明', '正統', 'Pseudo-Cyprian', NULL),
('門蘇里烏斯', 'Mensurius of Carthage', '迦太基', '天主教（拉丁禮）', 6, 296, 311, '逝世', '正統', 'Augustine, De Unico Baptismo; Optatus', NULL),
('凱希連諾', 'Caecilianus of Carthage', '迦太基', '天主教（拉丁禮）', 7, 311, 325, '不明', '正統', 'Augustine, Contra Litteras Petiliani; Optatus, De Schismate', '其按立合法性受質疑，引發多納徒主義大分裂；出席325年尼西亞公會議'),
('魯富斯', 'Rufus of Carthage', '迦太基', '天主教（拉丁禮）', 8, 337, 340, '不明', '正統', 'Optatus', NULL),
('格拉圖斯', 'Gratus of Carthage', '迦太基', '天主教（拉丁禮）', 9, 343, 348, '不明', '正統', 'Optatus; Council of Sardica', '出席薩迪卡公會議（344年）'),
('勒斯提圖斯', 'Restitutus of Carthage', '迦太基', '天主教（拉丁禮）', 10, 359, 370, '不明', '正統', 'Optatus', NULL),
('熱尼克利烏斯', 'Geneclius of Carthage', '迦太基', '天主教（拉丁禮）', 11, 370, 393, '逝世', '正統', 'Augustine', NULL),
('奧勒利烏斯', 'Aurelius of Carthage', '迦太基', '天主教（拉丁禮）', 12, 393, 426, '逝世', '正統', 'Augustine, Epistulae; Council of Carthage records', '與奧古斯丁合作鎮壓多納徒主義；主持迦太基公會議系列（397–419年）；後被封聖'),
('卡普里奧盧斯', 'Capreolus of Carthage', '迦太基', '天主教（拉丁禮）', 13, 431, 435, '逝世', '正統', 'ACO I; Jaffé', '出席以弗所公會議（431年）'),
('誇德伏爾德烏斯', 'Quodvultdeus of Carthage', '迦太基', '天主教（拉丁禮）', 14, 437, 454, '流亡', '正統', 'PL 40; Ferrandus, Vita Fulgentii', '439年汪達爾王蓋塞里克攻占迦太基後被流放至那不勒斯；在流亡中逝世；後被封聖'),
('德奧格拉提亞斯', 'Deogratias of Carthage', '迦太基', '天主教（拉丁禮）', 15, 454, 457, '逝世', '正統', 'Victor of Vita, Historia Persecutionis', '455年羅馬遭洗劫後積極贖回奴隸；後被封聖'),
('歐金尼烏斯', 'Eugenius of Carthage', '迦太基', '天主教（拉丁禮）', 16, 481, 505, '流亡', '正統', 'Victor of Vita; Ferrandus', '484年被汪達爾王胡內里克流放至高盧；505年在流亡中逝世；後被封聖'),
('博尼法爵一世', 'Boniface I of Carthage', '迦太基', '天主教（拉丁禮）', 17, 523, 535, '逝世', '正統', 'Jaffé, Regesta', '拜占廷帝國收復北非後首任主教'),
('勒帕拉圖斯', 'Reparatus of Carthage', '迦太基', '天主教（拉丁禮）', 18, 535, 552, '流亡', '正統', 'Liberatus, Breviarium; ACO IV', '因反對查士丁尼一世的三章政策被流放至本都（Pontus）'),
('普里莫蘇斯', 'Primosus (Primasius) of Carthage', '迦太基', '天主教（拉丁禮）', 19, 552, 565, '逝世', '正統', 'PL 68', '重要的聖經注釋家（啟示錄注釋）'),
('普布利亞努斯', 'Publianus of Carthage', '迦太基', '天主教（拉丁禮）', 20, 565, 581, '逝世', '正統', 'Gregory I, Registrum Epistularum', NULL),
('多明我', 'Dominicus of Carthage', '迦太基', '天主教（拉丁禮）', 21, 592, 601, '逝世', '正統', 'Gregory I, Registrum Epistularum', '與教宗格列高利一世多有往來'),
('利奇尼亞努斯', 'Licinianus of Carthage', '迦太基', '天主教（拉丁禮）', 22, 601, 602, '逝世', '正統', 'Gregory I, Registrum', NULL),
('維克托爾', 'Victor of Carthage', '迦太基', '天主教（拉丁禮）', 23, 646, 655, '不明', '正統', 'Mansi, Concilia', '阿拉伯征服初期（646年征服北非起）'),
('額我略', 'Gregory of Carthage', '迦太基', '天主教（拉丁禮）', 24, 655, 668, '不明', '正統', 'Mansi, Concilia', NULL),
('費利克斯', 'Felix of Carthage', '迦太基', '天主教（拉丁禮）', 25, 680, 698, '不明', '正統', 'Mansi, Concilia', '698年阿拉伯人攻陷迦太基；主教座中斷；此後迦太基基督教社群逐漸消亡'),
('基里亞科斯', 'Cyriacus of Carthage', '迦太基', '天主教（拉丁禮）', 26, 1076, 1076, '不明', '正統', 'Mansi, Concilia', '有記錄的最後一位（名義）迦太基主教；在阿拉伯統治下被囚禁；此後主教座完全中斷');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '迦太基' AND church = '天主教（拉丁禮）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 12. 西印度群島 / 天主教（拉丁禮）
-- 西班牙王室榮譽宗主教銜（Patriarca de las Indias Occidentales）
-- 1524年設立，1963年空缺
-- 1705/1762年起兼任西班牙軍隊宗座代牧
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('安東尼奧·德·羅哈斯·曼里克', 'Antonio de Rojas Manrique', '西印度群島', '天主教（拉丁禮）', 1, 1524, 1527, '逝世', '正統', 'Eubel, Hierarchia Catholica IV; Catholic-Hierarchy.org', '首任；在位僅3年'),
('埃斯特班·加夫里埃爾·梅里諾', 'Esteban Gabriel Merino', '西印度群島', '天主教（拉丁禮）', 2, 1530, 1535, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('費爾南多·尼尼奧·德·格瓦拉', 'Fernando Niño de Guevara', '西印度群島', '天主教（拉丁禮）', 3, 1546, 1552, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('佩德羅·德·莫亞·伊·孔特雷拉斯', 'Pedro de Moya y Contreras', '西印度群島', '天主教（拉丁禮）', 4, 1591, 1591, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', '在位極短；曾任墨西哥城大主教及新西班牙副王'),
('胡安·古斯曼', 'Juan Guzmán', '西印度群島', '天主教（拉丁禮）', 5, 1602, 1605, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('胡安·包蒂斯塔·阿塞韋多', 'Juan Bautista Acevedo Muñoz', '西印度群島', '天主教（拉丁禮）', 6, 1606, 1608, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', '曾任西班牙宗教裁判所大法官'),
('迭戈·古斯曼·德·阿羅斯', 'Diego Guzmán de Haros', '西印度群島', '天主教（拉丁禮）', 7, 1616, 1625, '晉升', '正統', 'Eubel, Hierarchia Catholica IV', '升任塞維亞大主教'),
('安德烈斯·帕切科', 'Andrés Pacheco', '西印度群島', '天主教（拉丁禮）', 8, 1625, 1626, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('阿方索·佩雷斯·德·古斯曼', 'Alfonso Pérez de Guzmán', '西印度群島', '天主教（拉丁禮）', 9, 1627, 1670, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', '在任43年；在位最長'),
('安東尼奧·曼里克·德·古斯曼', 'Antonio Manrique de Guzmán', '西印度群島', '天主教（拉丁禮）', 10, 1670, 1679, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('安東尼奧·德·貝納維德斯', 'Antonio de Benavides y Bazán', '西印度群島', '天主教（拉丁禮）', 11, 1679, 1691, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('佩德羅·波托卡雷羅', 'Pedro Portocarrero y Guzmán', '西印度群島', '天主教（拉丁禮）', 12, 1691, 1705, '逝世', '正統', 'Eubel, Hierarchia Catholica IV', NULL),
('卡洛斯·博爾哈·森特拉斯', 'Carlos Borja Centellas y Ponce de León', '西印度群島', '天主教（拉丁禮）', 13, 1708, 1733, '逝世', '正統', 'Eubel, Hierarchia Catholica V', '1705年同時被教宗克勉十一世任命為西班牙軍隊宗座代牧——開創宗主教與軍隊主教合一之制'),
('阿爾瓦羅·尤金尼奧·德·門多薩', 'Álvaro Eugenio de Mendoza Caamaño y Sotomayor', '西印度群島', '天主教（拉丁禮）', 14, 1734, 1761, '逝世', '正統', 'Eubel, Hierarchia Catholica V', '1736年教宗克勉十二世正式將西印度群島宗主教與軍隊宗座代牧兩職合併'),
('布埃納文圖拉·科爾多瓦·埃斯皮諾薩', 'Buenaventura Córdoba Espinosa de la Cerda', '西印度群島', '天主教（拉丁禮）', 15, 1761, 1777, '逝世', '正統', 'Eubel, Hierarchia Catholica V', NULL),
('弗朗西斯科·哈維爾·德爾加多', 'Francisco Javier Delgado y Venegas', '西印度群島', '天主教（拉丁禮）', 16, 1778, 1781, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', NULL),
('卡耶塔諾·阿索爾·帕雷德斯', 'Cayetano Adsor Paredes', '西印度群島', '天主教（拉丁禮）', 17, 1782, 1782, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', '在位不足一年'),
('曼努埃爾·菲格羅亞·巴雷羅', 'Manuel Buenaventura Figueroa Barrero', '西印度群島', '天主教（拉丁禮）', 18, 1782, 1783, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', NULL),
('安東尼奧·森特馬納特', 'Antonio Sentmenat y Castelló', '西印度群島', '天主教（拉丁禮）', 19, 1784, 1806, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', NULL),
('拉蒙·何塞·德·阿爾塞', 'Ramón José de Arce', '西印度群島', '天主教（拉丁禮）', 20, 1806, 1815, '流亡', '正統', 'Eubel, Hierarchia Catholica VI', '拿破崙入侵西班牙（1808年）期間；流亡法國；後辭職'),
('弗朗西斯科·安東尼奧·謝布里安', 'Francisco Antonio Cebrián y Valdé', '西印度群島', '天主教（拉丁禮）', 21, 1815, 1820, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', NULL),
('安東尼奧·阿呂埃·塞塞', 'Antonio Allué y Sesse', '西印度群島', '天主教（拉丁禮）', 22, 1821, 1842, '逝世', '正統', 'Eubel, Hierarchia Catholica VI', NULL),
('安東尼奧·波薩達·魯賓', 'Antonio Posada Rubín de Celis', '西印度群島', '天主教（拉丁禮）', 23, 1847, 1851, '逝世', '正統', 'Eubel, Hierarchia Catholica VII', NULL),
('托馬斯·伊格萊西亞斯·巴爾科內斯', 'Tomás Iglesias y Bárcones', '西印度群島', '天主教（拉丁禮）', 24, 1852, 1874, '逝世', '正統', 'Eubel, Hierarchia Catholica VII', NULL),
('弗朗西斯科·保拉·貝納維德斯', 'Francisco de Paula Benavides y Navarrete O.S.', '西印度群島', '天主教（拉丁禮）', 25, 1875, 1881, '晉升', '正統', 'Eubel, Hierarchia Catholica VII', '升任格拉納達大主教'),
('何塞·莫雷諾·伊·馬松', 'José Moreno y Mazón', '西印度群島', '天主教（拉丁禮）', 26, 1881, 1885, '晉升', '正統', 'Eubel, Hierarchia Catholica VII', '升任塞維亞大主教'),
('塞費里諾·岡薩雷斯', 'Zeferino González y Díaz Tuñón O.P.', '西印度群島', '天主教（拉丁禮）', 27, 1885, 1886, '晉升', '正統', 'Eubel, Hierarchia Catholica VIII', '著名托馬斯哲學家；升任塞維亞大主教'),
('米格爾·帕亞·伊·里科', 'Miguel Payá y Rico', '西印度群島', '天主教（拉丁禮）', 28, 1886, 1891, '逝世', '正統', 'Eubel, Hierarchia Catholica VIII', NULL),
('安托林·莫內西略·伊·維索', 'Antolín Monescillo y Viso', '西印度群島', '天主教（拉丁禮）', 29, 1892, 1897, '逝世', '正統', 'Eubel, Hierarchia Catholica VIII', NULL),
('塞萊斯蒂諾·馬里亞·桑查·埃爾瓦斯', 'Bl. Ciriaco María Sancha y Hervás', '西印度群島', '天主教（拉丁禮）', 30, 1898, 1909, '逝世', '正統', 'Eubel, Hierarchia Catholica VIII', '真福品'),
('格雷戈里奧·馬里亞·阿吉雷', 'Gregorio María Aguirre y García O.F.M.', '西印度群島', '天主教（拉丁禮）', 31, 1909, 1913, '逝世', '正統', 'Eubel, Hierarchia Catholica VIII', '樞機'),
('維克托里亞諾·吉薩索拉', 'Victoriano Guisasola y Menéndez', '西印度群島', '天主教（拉丁禮）', 32, 1914, 1920, '逝世', '正統', 'Eubel, Hierarchia Catholica IX', NULL),
('海梅·卡爾多納·圖爾', 'Jaime Cardona y Tur', '西印度群島', '天主教（拉丁禮）', 33, 1920, 1923, '逝世', '正統', 'Eubel, Hierarchia Catholica IX', NULL),
('胡利安·德·迭戈·伊·加西亞·阿爾科萊亞', 'Julián de Diego y García Alcolea', '西印度群島', '天主教（拉丁禮）', 34, 1923, 1925, '晉升', '正統', 'Eubel, Hierarchia Catholica IX', '升任薩拉曼卡大主教'),
('弗朗西斯科·穆尼奧斯·伊斯基耶多', 'Francisco Muñoz e Izquierdo', '西印度群島', '天主教（拉丁禮）', 35, 1925, 1930, '逝世', '正統', 'Eubel, Hierarchia Catholica IX', NULL),
('拉蒙·佩雷斯·伊·羅德里格斯', 'Ramón Pérez y Rodríguez', '西印度群島', '天主教（拉丁禮）', 36, 1930, 1937, '逝世', '正統', 'Eubel, Hierarchia Catholica IX', NULL),
('萊奧波爾多·埃霍·伊·加雷', 'Leopoldo Eijo y Garay', '西印度群島', '天主教（拉丁禮）', 37, 1946, 1963, '逝世', '正統', 'Eubel, Hierarchia Catholica IX; Catholic-Hierarchy.org', '末任；1963年逝世後職位懸空至今；同時任馬德里—阿爾卡拉主教（1923–1963）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '西印度群島' AND church = '天主教（拉丁禮）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
