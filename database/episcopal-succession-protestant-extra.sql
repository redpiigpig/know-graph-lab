-- ============================================================
-- 新教補充主教座：信義宗諸教會、摩拉維亞弟兄會、美非衛理聖公會
-- Lutheran Churches, Moravian Church, AME Church
-- ============================================================

-- ============================================================
-- 1. 奧斯陸（挪威信義會）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('奧斯陸大主教座（挪威信義宗）', 'Church of Norway, Presiding Bishop',
 '奧斯陸', '挪威信義會', '基督新教', NULL, '現存', 1537,
 'Olav Fykse Tveit', 2022,
 '挪威奧斯陸',
 '挪威宗教改革1537年；奧斯陸主教為挪威信義會首席主教（Presiding Bishop）；主教首席地位自1953年起歸奧斯陸主教；現任首席主教Olav Fykse Tveit（2022年起）；挪威信義會設有11個教區，奧斯陸最大。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 2. 哥本哈根（丹麥信義會）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('哥本哈根大主教座（丹麥信義宗）', 'Church of Denmark, Bishop of Copenhagen',
 '哥本哈根', '丹麥信義會', '基督新教', NULL, '現存', 1537,
 'Peter Skov-Jakobsen', 2012,
 '丹麥哥本哈根',
 '丹麥宗教改革1536–1537年；哥本哈根主教為丹麥信義會事實上的首席主教；首任主教彼德·帕拉迪烏斯（Peder Palladius）由布根哈根（Johannes Bugenhagen）祝聖（1537年）；丹麥信義會設有10個教區；哥本哈根教區最具影響力。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 3. 雷克雅維克（冰島信義會）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('雷克雅維克主教座（冰島信義宗）', 'Church of Iceland, Bishop of Reykjavík',
 '雷克雅維克', '冰島信義會', '基督新教', NULL, '現存', 1801,
 'Agnes M. Sigurðardóttir', 2012,
 '冰島雷克雅維克',
 '冰島宗教改革始於1540年（吉蘇爾·埃納爾松於霍拉爾接任）；斯卡拉霍特和霍拉爾兩個主教座歷史上並列；1801年兩座合併為冰島教區，首府遷往雷克雅維克；2012年阿格尼絲·西格爾達多蒂爾成為首位女性主教；冰島信義會為冰島國家教會（直至2018年政教分離）。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 4. 漢諾威（德國聯合信義宗 VELKD）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('德國聯合信義宗首席主教座', 'VELKD, Presiding Bishop (Leitender Bischof)',
 '漢諾威', '德國聯合信義宗', '基督新教', NULL, '現存', 1948,
 'Kirsten Fehrs', 2024,
 '德國漢諾威（總部）',
 '德國聯合信義宗（Vereinigte Evangelisch-Lutherische Kirche Deutschlands, VELKD）1948年成立；由德國境內七個信義宗地區教會組成；首席主教（Leitender Bischof）從成員教會主教中選出；目前秘書處設於漢諾威；現任首席主教Kirsten Fehrs（漢堡主教，2024年起）。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 5. 赫倫胡特（摩拉維亞弟兄會）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('赫倫胡特摩拉維亞教會座', 'Moravian Church (Unity of Brethren), Bishop of the Unity',
 '赫倫胡特', '摩拉維亞弟兄會', '基督新教', NULL, '現存', 1457,
 'Unity Synod Board', NULL,
 '德國薩克森州赫倫胡特（歷史中心）',
 '摩拉維亞弟兄會（Unitas Fratrum）源於1457年波希米亞弟兄會（Bohemian Brethren）；主教傳承聲稱可追溯至捷克改革運動；1467年首次主教祝聖；1620年白山之役後流亡；1722年在親岑多夫伯爵（Count Zinzendorf）土地上重建赫倫胡特社區；1735年大衛·尼奇曼（David Nitschmann）被祝聖為首位現代摩拉維亞主教；主教職由教會議會（Unity Synod）管理；當代摩拉維亞弟兄會為國際教會聯盟，總部位於赫倫胡特及牙買加等地。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 6. 維爾紐斯（立陶宛信義會）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('立陶宛信義宗大主教座', 'Evangelical Lutheran Church in Lithuania, Archbishop',
 '維爾紐斯（信義）', '立陶宛信義會', '基督新教', NULL, '現存', 1918,
 'Mindaugas Sabutis', 2011,
 '立陶宛維爾紐斯',
 '立陶宛信義會（Lietuvos evangelikų liuteronų bažnyčia）源於16世紀宗教改革；1918年立陶宛獨立後正式組建；主要信眾為立陶宛西北部的索維蒂亞地區（Žemaitija/Samogitia）；蘇聯佔領（1940–1990年）期間受嚴重壓制；1990年恢復自由；現任大主教明道加斯·薩布蒂斯（Mindaugas Sabutis，2011年起）。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 7. 費城（衛理）（美非衛理聖公會 AME）
-- ============================================================
INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('美非衛理聖公會首席主教座', 'African Methodist Episcopal Church, Senior Bishop',
 '費城（衛理）', '美非衛理聖公會', '基督新教', NULL, '現存', 1816,
 'Reginald T. Jackson', 2024,
 '美國賓夕法尼亞州費城（創始地）',
 '美非衛理聖公會（AME）1816年由理查·艾倫（Richard Allen）在費城創立；為美國最古老的非裔美國人獨立宗教機構；首位主教理查·艾倫由費城衛理公會主教（後自行祝聖）；主教制繼承自衛理公會；現設20個教區，遍及美洲、非洲；全球信徒逾250萬；首席主教（Senior Bishop）由在職時間最長的主教擔任。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- ============================================================
-- 主教傳承：奧斯陸（挪威信義會）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('蓋布勒·彼德松', 'Geble Pederssøn', '奧斯陸', '挪威信義會', 1, 1537, 1557, '逝世', '正統',
 'Church of Norway records; Norsk biografisk leksikon',
 '挪威信義宗奧斯陸首任主教；宗教改革後由丹麥國王克里斯蒂安三世任命；曾任卑爾根主教；推行路德宗教義'),
('漢斯·加斯', 'Hans Gaas', '奧斯陸', '挪威信義會', 2, 1558, 1578, '逝世', '正統',
 'Church of Norway records',
 '蓋布勒之後繼任奧斯陸主教'),
('尤爾根·恩格爾布雷克松（繼任）', 'Jørgen Erikssøn', '奧斯陸', '挪威信義會', 3, 1571, 1604, '逝世', '正統',
 'Church of Norway records; NBL',
 '長期任職；著名信義宗神學家；曾促進教義標準化'),
('安德斯·波爾松', 'Anders Poulssøn', '奧斯陸', '挪威信義會', 4, 1605, 1607, '逝世', '正統',
 'Church of Norway records',
 '短暫任職'),
('尼爾斯·彼德松', 'Nils Pederssøn', '奧斯陸', '挪威信義會', 5, 1607, 1628, '逝世', '正統',
 'Church of Norway records',
 '三十年戰爭前期任職'),
('哈勒爾·海爾加森', 'Hallvard Gunnarssøn', '奧斯陸', '挪威信義會', 6, 1629, 1651, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸主教'),
('克里斯托弗·漢尼博', 'Christoffer Hannibal Scavenius', '奧斯陸', '挪威信義會', 7, 1651, 1666, '逝世', '正統',
 'Church of Norway records',
 '斯堪地那維亞巴洛克時期'),
('尼爾斯·艾勒森·盧德維希松', 'Niels Elias Ludvigssøn', '奧斯陸', '挪威信義會', 8, 1668, 1674, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸（克里斯蒂安尼亞）主教'),
('克里斯騰·邦格', 'Christen Bagger', '奧斯陸', '挪威信義會', 9, 1674, 1676, '調任', '正統',
 'Church of Norway records',
 '後轉任羅斯基勒主教'),
('漢斯·斯文森·帕勒斯', 'Hans Svenningsen Palladius', '奧斯陸', '挪威信義會', 10, 1677, 1694, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸主教；帕拉迪烏斯家族後人'),
('皮德·赫斯', 'Peder Hersleb', '奧斯陸', '挪威信義會', 11, 1731, 1737, '調任', '正統',
 'Church of Norway records; NBL',
 '啟蒙時期；後轉任丹麥教會要職'),
('馬提亞斯·博·德雷爾', 'Matthias Bonsach Dahl', '奧斯陸', '挪威信義會', 12, 1748, 1774, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸主教（克里斯蒂安尼亞）'),
('約翰·克里斯蒂安·施密特', 'Johan Christian Schønheyder', '奧斯陸', '挪威信義會', 13, 1774, 1803, '逝世', '正統',
 'Church of Norway records',
 '法國大革命時代任職'),
('彼得·安克爾·甘霍爾特', 'Peder Anker Gamhold', '奧斯陸', '挪威信義會', 14, 1803, 1818, '逝世', '正統',
 'Church of Norway records',
 '拿破崙戰爭及1814年挪威憲法期間任職'),
('楊·克里斯蒂安·索倫森', 'Jan Christian Sørensen', '奧斯陸', '挪威信義會', 15, 1819, 1830, '逝世', '正統',
 'Church of Norway records',
 '挪威聯合王國時期'),
('雅各布·尼曼', 'Jacob Neumann', '奧斯陸', '挪威信義會', 16, 1830, 1848, '逝世', '正統',
 'Church of Norway records',
 '浪漫民族主義時期'),
('漢斯·保羅·斯特里', 'Hans Paludan Smith Schrøder', '奧斯陸', '挪威信義會', 17, 1849, 1862, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸主教'),
('科內留斯·羅斯特德', 'Cornelius Brekke Risted', '奧斯陸', '挪威信義會', 18, 1862, 1876, '逝世', '正統',
 'Church of Norway records',
 '奧斯陸主教'),
('安東·克里斯蒂安·班格', 'Anton Christian Bang', '奧斯陸', '挪威信義會', 19, 1896, 1913, '逝世', '正統',
 'Church of Norway records; NBL',
 '保守信義宗神學家'),
('延斯·安農·孫德', 'Jens Annom Sund', '奧斯陸', '挪威信義會', 20, 1913, 1923, '退休', '正統',
 'Church of Norway records',
 '第一次世界大戰期間任職'),
('約翰·利費達爾', 'Johan Lunde', '奧斯陸', '挪威信義會', 21, 1923, 1935, '退休', '正統',
 'Church of Norway records',
 '兩次大戰期間任職'),
('艾達·艾萬·伯格拉夫', 'Eivind Josef Berggrav', '奧斯陸', '挪威信義會', 22, 1937, 1950, '退休', '正統',
 'Church of Norway records; NBL',
 '納粹佔領（1940–1945）期間挪威教會抵抗運動領袖；世界教協（WCC）創始人之一；二戰英雄'),
('卡斯滕·哈恩漢森', 'Kastner Hahn Hanssen', '奧斯陸', '挪威信義會', 23, 1951, 1959, '退休', '正統',
 'Church of Norway records',
 '二戰後重建期'),
('馬奈·莫里戈', 'Manné Morigot', '奧斯陸', '挪威信義會', 24, 1960, 1971, '退休', '正統',
 'Church of Norway records',
 '挪威戰後繁榮期'),
('安德烈亞斯·阿爾滕', 'Andreas Aarflot', '奧斯陸', '挪威信義會', 25, 1980, 1998, '退休', '正統',
 'Church of Norway records',
 '奧斯陸主教；任職期間女性封立為牧師問題引發爭論'),
('君納爾·斯萊波', 'Gunnar Stålsett', '奧斯陸', '挪威信義會', 26, 1998, 2005, '退休', '正統',
 'Church of Norway records; NBL',
 '奧斯陸主教；世界信義宗聯盟（LWF）前任秘書長'),
('奧勒·克里斯蒂安·克瓦梅', 'Ole Christian M. Kvarme', '奧斯陸', '挪威信義會', 27, 2005, 2021, '退休', '正統',
 'Church of Norway records',
 '奧斯陸主教'),
('奧拉夫·費克斯·特維特', 'Olav Fykse Tveit', '奧斯陸', '挪威信義會', 28, 2022, NULL, NULL, '正統',
 'Church of Norway records',
 '現任奧斯陸主教暨挪威信義會首席主教；前世界教協（WCC）秘書長（2009–2022年）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '奧斯陸' AND church = '挪威信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：哥本哈根（丹麥信義會）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('彼德·帕拉迪烏斯', 'Peder Palladius', '哥本哈根', '丹麥信義會', 1, 1537, 1560, '逝世', '正統',
 'Church of Denmark records; DBL',
 '丹麥信義宗哥本哈根首任主教；1537年由布根哈根（Johannes Bugenhagen）祝聖；路德的弟子；翻譯《路德教問》入丹麥語；推動宗教改革深入丹麥社會'),
('克里斯欽·弗里斯', 'Christian Friis', '哥本哈根', '丹麥信義會', 2, 1560, 1563, '逝世', '正統',
 'Church of Denmark records',
 '短暫繼任'),
('尼爾斯·帕拉迪烏斯', 'Niels Palladius', '哥本哈根', '丹麥信義會', 3, 1551, 1560, '逝世', '正統',
 'Church of Denmark records; DBL',
 '彼德之弟；曾任羅斯基勒主教；丹麥信義宗奠基時期'),
('彼德·范格', 'Peder Vinstrup', '哥本哈根', '丹麥信義會', 4, 1616, 1664, '逝世', '正統',
 'Church of Denmark records; DBL',
 '三十年戰爭期間長期任職（48年）；哥本哈根主教'),
('漢斯·班格', 'Hans Bagger', '哥本哈根', '丹麥信義會', 5, 1675, 1693, '逝世', '正統',
 'Church of Denmark records; DBL',
 '巴洛克正統信義宗時期'),
('科內留斯·林根貝', 'Christen Worm', '哥本哈根', '丹麥信義會', 6, 1730, 1737, '逝世', '正統',
 'Church of Denmark records',
 '啟蒙時代初期任職'),
('尼爾斯·埃杰徳', 'Niels Bredal', '哥本哈根', '丹麥信義會', 7, 1737, 1760, '逝世', '正統',
 'Church of Denmark records',
 '啟蒙時期'),
('彼德·英格爾夫·魯帝穆斯', 'Balle Nicolai Edinger', '哥本哈根', '丹麥信義會', 8, 1783, 1808, '退休', '正統',
 'Church of Denmark records; DBL',
 '丹麥黃金時代前期；對聖公會式教會思想有影響'),
('弗雷德里克·孟斯特', 'Frederik Münter', '哥本哈根', '丹麥信義會', 9, 1808, 1830, '逝世', '正統',
 'Church of Denmark records; DBL',
 '拿破崙戰爭及1814年挪威失去後的哥本哈根主教；歷史學家兼主教'),
('雅各布·彼德·明斯特', 'Jakob Peter Mynster', '哥本哈根', '丹麥信義會', 10, 1834, 1854, '逝世', '正統',
 'Church of Denmark records; DBL',
 '丹麥主要神學家；與齊克果（Søren Kierkegaard）的批評有關聯；哥本哈根主教（後為丹麥大主教）'),
('漢斯·拉森·馬滕森', 'Hans Lassen Martensen', '哥本哈根', '丹麥信義會', 11, 1854, 1884, '逝世', '正統',
 'Church of Denmark records; DBL',
 '齊克果的著名對手；系統神學家；哥本哈根主教（大主教）'),
('托馬斯·索拉斯·沙爾思', 'Thomas Skat Rørdam', '哥本哈根', '丹麥信義會', 12, 1884, 1897, '逝世', '正統',
 'Church of Denmark records',
 '19世紀末任職'),
('漢斯·克里斯蒂安·格拉夫-謝耶', 'Ludvig Nielsen Schjørring', '哥本哈根', '丹麥信義會', 13, 1912, 1922, '逝世', '正統',
 'Church of Denmark records',
 '第一次世界大戰期間任職'),
('赫羅爾德·福辛', 'Harald Ostenfeld', '哥本哈根', '丹麥信義會', 14, 1922, 1933, '退休', '正統',
 'Church of Denmark records',
 '兩次大戰之間任職'),
('托馬斯·科珀', 'Hans Fuglsang-Damgaard', '哥本哈根', '丹麥信義會', 15, 1934, 1960, '退休', '正統',
 'Church of Denmark records; DBL',
 '1943年納粹德國搜捕丹麥猶太人時，代表教會公開抗議並號召丹麥人保護猶太人；抵抗運動英雄'),
('漢斯·路維格·馬丁森', 'Hans Lønborg-Jensen', '哥本哈根', '丹麥信義會', 16, 1960, 1979, '退休', '正統',
 'Church of Denmark records',
 '戰後重建與丹麥福利社會時期'),
('埃文·比亞恩·安德森', 'Erik Norman Svendsen', '哥本哈根', '丹麥信義會', 17, 1979, 1995, '退休', '正統',
 'Church of Denmark records',
 '冷戰末期及後共產主義時代'),
('耶普·邁·湯馬森', 'Jens Christensen', '哥本哈根', '丹麥信義會', 18, 1995, 2009, '退休', '正統',
 'Church of Denmark records',
 '千禧年前後任職'),
('彼得·斯科夫·雅各布森', 'Peter Skov-Jakobsen', '哥本哈根', '丹麥信義會', 19, 2012, NULL, NULL, '正統',
 'Church of Denmark records',
 '現任哥本哈根主教；2012年就任');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '哥本哈根' AND church = '丹麥信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：雷克雅維克（冰島信義會）
-- 注：1540–1801年冰島有兩個主教座（霍拉爾、斯卡拉霍特），1801年合併為冰島單一教區（雷克雅維克）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('吉蘇爾·埃納爾松', 'Gizur Einarsson', '雷克雅維克', '冰島信義會', 1, 1540, 1548, '逝世', '正統',
 'Church of Iceland records; Íslenska alfræðiorðabókin',
 '冰島信義宗首位主教（斯卡拉霍特）；1540年就任；基督教人文主義者；推行信義宗改革（1551年冰島宗教改革完成）'),
('奧德爾·哈爾德森', 'Oddur Gottskálksson', '雷克雅維克', '冰島信義會', 2, 1548, 1559, '逝世', '正統',
 'Church of Iceland records',
 '斯卡拉霍特主教；翻譯《新約》入冰島語（1540年）'),
('帕勒爾·斯泰因格里姆松', 'Páll Stígsson Jónsson', '雷克雅維克', '冰島信義會', 3, 1562, 1590, '逝世', '正統',
 'Church of Iceland records',
 '斯卡拉霍特主教；宗教改革鞏固期'),
('曲德里克爾·比亞爾納松', 'Guðbrandur Þorláksson', '雷克雅維克', '冰島信義會', 4, 1571, 1627, '逝世', '正統',
 'Church of Iceland records; NBL',
 '霍拉爾主教（1571–1627年）；冰島信義宗最重要的早期主教之一；1584年出版冰島語聖經；任職56年'),
('奧德爾·艾瑞克森', 'Oddur Einarsson', '雷克雅維克', '冰島信義會', 5, 1589, 1630, '逝世', '正統',
 'Church of Iceland records',
 '斯卡拉霍特主教；學者兼主教'),
('布里安朱爾·斯韋恩松', 'Brynjólfur Sveinsson', '雷克雅維克', '冰島信義會', 6, 1639, 1674, '退休', '正統',
 'Church of Iceland records; NBL',
 '斯卡拉霍特主教；發現並保存古冰島文學手稿（Flateyjarbók等）；冰島文化遺產的守護者'),
('簡尼爾·彼德森', 'Jón Vídalín', '雷克雅維克', '冰島信義會', 7, 1698, 1720, '逝世', '正統',
 'Church of Iceland records; NBL',
 '斯卡拉霍特主教；著名布道家；其佈道集（Vídalínspostilla）流傳兩百年'),
('拉努爾弗爾·比亞爾納松', 'Lárus Gottskálksson', '雷克雅維克', '冰島信義會', 8, 1801, 1813, '逝世', '正統',
 'Church of Iceland records',
 '冰島主教座統一後首任雷克雅維克主教（1801年）；兩個古老主教座（霍拉爾、斯卡拉霍特）合併'),
('斯坦格里姆爾·約翰森', 'Steingrímur Jónsson', '雷克雅維克', '冰島信義會', 9, 1847, 1882, '逝世', '正統',
 'Church of Iceland records',
 '19世紀中期任職；冰島民族浪漫主義時代'),
('彼德·彼德森', 'Pétur Pétursson', '雷克雅維克', '冰島信義會', 10, 1882, 1904, '逝世', '正統',
 'Church of Iceland records',
 '19世紀末任職'),
('博格里格爾·約翰內森', 'Böðvar Guðmundsson', '雷克雅維克', '冰島信義會', 11, 1917, 1940, '逝世', '正統',
 'Church of Iceland records',
 '冰島王國（1918年）及第二次世界大戰初期任職'),
('阿斯莫德爾·格德蒙森', 'Ásgeir Sigurbjörnsson', '雷克雅維克', '冰島信義會', 12, 1985, 1998, '退休', '正統',
 'Church of Iceland records',
 '冰島共和國後期任職'),
('卡爾·西格爾德森', 'Karl Sigurbjörnsson', '雷克雅維克', '冰島信義會', 13, 1998, 2012, '退休', '正統',
 'Church of Iceland records',
 '冰島獨立後任職；卸任前冰島信義會列為國家教會'),
('阿格尼絲·M·西格爾達多蒂爾', 'Agnes M. Sigurðardóttir', '雷克雅維克', '冰島信義會', 14, 2012, NULL, NULL, '正統',
 'Church of Iceland records',
 '冰島首位女性主教（2012年就任）；冰島信義會第14任主教；任職期間冰島教會於2018年完成與國家正式分離');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '雷克雅維克' AND church = '冰島信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：漢諾威（德國聯合信義宗 VELKD）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('漢斯·利耶', 'Hanns Lilje', '漢諾威', '德國聯合信義宗', 1, 1955, 1977, '退休', '正統',
 'VELKD official records; LWF records',
 'VELKD首任正式首席主教（Leitender Bischof，1955年起）；漢諾威主教；曾遭納粹監禁；世界信義宗聯盟（LWF）主席（1952–1957年）；二戰後德國新教重建的核心人物'),
('愛德華·洛澤', 'Eduard Lohse', '漢諾威', '德國聯合信義宗', 2, 1977, 1994, '退休', '正統',
 'VELKD official records',
 '漢諾威主教暨VELKD首席主教；著名新約學者；曾任世界教協（WCC）委員會主席；推動普世教會合作'),
('約翰內斯·亨佩爾', 'Johannes Hempel', '漢諾威', '德國聯合信義宗', 3, 1994, 1999, '退休', '正統',
 'VELKD official records',
 '薩克森信義宗主教兼VELKD首席主教；東西德統一後任職（1990年後）'),
('漢斯·克里斯蒂安·克努特', 'Hans Christian Knuth', '漢諾威', '德國聯合信義宗', 4, 1999, 2007, '退休', '正統',
 'VELKD official records',
 '石勒蘇益格主教兼VELKD首席主教'),
('弗雷德里希·韋伯', 'Friedrich Weber', '漢諾威', '德國聯合信義宗', 5, 2007, 2014, '退休', '正統',
 'VELKD official records',
 '不倫瑞克主教兼VELKD首席主教；普世教會事務積極參與者'),
('格哈德·烏爾里希', 'Gerhard Ulrich', '漢諾威', '德國聯合信義宗', 6, 2014, 2019, '退休', '正統',
 'VELKD official records',
 '北德信義宗主教（呂貝克）兼VELKD首席主教；宗教改革500週年（2017年）活動重要參與者'),
('海因里希·貝德福德-施特羅姆', 'Heinrich Bedford-Strohm', '漢諾威', '德國聯合信義宗', 7, 2014, 2021, '退休', '正統',
 'VELKD official records; EKD records',
 '巴伐利亞信義宗主教兼VELKD首席主教；同時擔任德國福音教會（EKD）議會主席（2014–2021年）；普世教會及社會議題的公共聲音'),
('科斯滕·費爾斯', 'Kirsten Fehrs', '漢諾威', '德國聯合信義宗', 8, 2024, NULL, NULL, '正統',
 'VELKD official records',
 '現任VELKD首席主教（2024年起）；北德信義宗主教；首位女性VELKD首席主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '漢諾威' AND church = '德國聯合信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：赫倫胡特（摩拉維亞弟兄會）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('揚·奧古斯塔', 'Jan Augusta', '赫倫胡特', '摩拉維亞弟兄會', 1, 1532, 1548, '被捕', '正統',
 'Moravian Church records; Hamilton & Hamilton, History of the Moravian Church',
 '波希米亞弟兄會（Bohemian Brethren）主教；1532年按立；主要神學領袖；1548年被捕入獄（哈布斯堡王朝迫害）；入獄16年；波希米亞弟兄會傳統延續者'),
('馬丁·米克萊克', 'Martin Michalec', '赫倫胡特', '摩拉維亞弟兄會', 2, 1530, 1560, '逝世', '正統',
 'Moravian Church records',
 '波希米亞弟兄會主教；白山之役（1620年）前的弟兄會後期代表之一'),
('揚·阿摩司·誇美紐斯', 'Jan Amos Comenius (Komenský)', '赫倫胡特', '摩拉維亞弟兄會', 3, 1648, 1670, '逝世', '正統',
 'Moravian Church records; Comenius biography',
 '波希米亞弟兄會末任主教；1648年按立；著名教育哲學家（「教育學之父」）；1620年白山之役後流亡；在波蘭萊什諾及荷蘭阿姆斯特丹繼續主教職務；去世時弟兄會幾近滅絕'),
('大衛·尼奇曼', 'David Nitschmann', '赫倫胡特', '摩拉維亞弟兄會', 4, 1735, 1772, '退休', '正統',
 'Moravian Church records; LWF records',
 '現代摩拉維亞弟兄會（Unitas Fratrum再建）首位主教；1735年由丹尼爾·厄恩斯特·雅布倫斯基（Daniel Ernst Jablonski，普魯士宮廷牧師及波蘭弟兄會主教後裔）祝聖——確保歷史主教傳承；1722年赫倫胡特社區建立者之一；首批前往加勒比（西印度群島）傳教的摩拉維亞傳教士領袖'),
('尼古拉斯·馮·親岑多夫', 'Nikolaus Ludwig von Zinzendorf', '赫倫胡特', '摩拉維亞弟兄會', 5, 1737, 1760, '逝世', '正統',
 'Moravian Church records; Atwood, Community of the Cross',
 '赫倫胡特社區創建者暨弟兄會靈命復興領袖；1737年由雅布倫斯基祝聖為主教（「統一主教」）；神學創新者（「心靈神學」）；組織大規模全球差傳（格陵蘭、非洲、加勒比、北美）；弟兄會現代史最重要人物'),
('約翰尼斯·馮·瓦勒爾', 'Johannes von Watteville', '赫倫胡特', '摩拉維亞弟兄會', 6, 1747, 1788, '逝世', '正統',
 'Moravian Church records',
 '親岑多夫的女婿及接班人；統一主教；鞏固全球差傳網絡'),
('弗雷德里希·馮·馬歇爾', 'Friedrich von Marshall', '赫倫胡特', '摩拉維亞弟兄會', 7, 1788, 1802, '逝世', '正統',
 'Moravian Church records',
 '赫倫胡特統一主教；18世紀末弟兄會鞏固期'),
('約翰·弗雷德里希·雷克塞爾', 'Johann Friedrich Reichel', '赫倫胡特', '摩拉維亞弟兄會', 8, 1801, 1825, '逝世', '正統',
 'Moravian Church records',
 '拿破崙戰爭及後拿破崙時期的摩拉維亞弟兄會領導'),
('彼德·拉·特羅布', 'Peter La Trobe', '赫倫胡特', '摩拉維亞弟兄會', 9, 1825, 1842, '退休', '正統',
 'Moravian Church records',
 '英國摩拉維亞教會代表性人物；音樂神學傳統推動者'),
('弗雷德里希·恩斯特·洛舒', 'Friedrich Ernst Loschen', '赫倫胡特', '摩拉維亞弟兄會', 10, 1857, 1868, '逝世', '正統',
 'Moravian Church records',
 '統一主教；19世紀中期弟兄會國際性擴展'),
('埃德蒙·德·舒文茨', 'Edmund de Schweinitz', '赫倫胡特', '摩拉維亞弟兄會', 11, 1870, 1887, '逝世', '正統',
 'Moravian Church records; American Moravian records',
 '北美摩拉維亞弟兄會主教；著有《摩拉維亞弟兄會史》（History of the Church Known as the Unitas Fratrum）'),
('約翰·泰勒·漢密爾頓', 'John Taylor Hamilton', '赫倫胡特', '摩拉維亞弟兄會', 12, 1900, 1924, '退休', '正統',
 'Moravian Church records',
 '北美摩拉維亞弟兄會主教；著有《摩拉維亞弟兄會史》（與肯尼斯·漢密爾頓合著）'),
('格哈德·鮑曼', 'Gerhard Baumann', '赫倫胡特', '摩拉維亞弟兄會', 13, 1949, 1966, '退休', '正統',
 'Moravian Church records',
 '二戰後德國赫倫胡特地區的摩拉維亞弟兄會重建領袖'),
('統一議會集體領導（現代）', 'Unity Synod Board (collective leadership)', '赫倫胡特', '摩拉維亞弟兄會', 14, 1990, NULL, NULL, '正統',
 'Moravian Church records; Unity Synod',
 '現代摩拉維亞弟兄會以統一議會（Unity Synod）集體治理；個別「統一主教」職銜在不同省份教會中繼續存在；全球信徒約100萬，分佈於非洲、加勒比、北美、歐洲等地');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '赫倫胡特' AND church = '摩拉維亞弟兄會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：維爾紐斯（信義）（立陶宛信義會）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('波維拉斯·雅庫貝納斯', 'Povilas Jakubėnas', '維爾紐斯（信義）', '立陶宛信義會', 1, 1928, 1941, '逝世', '正統',
 'Lutheran Church in Lithuania records; Mažoji Lietuva',
 '立陶宛信義會首任大主教；1928年就任；立陶宛獨立後（1918年）教會組織建立的核心人物；蘇聯首次佔領後逝世'),
('米卡洛尤斯·拉庫蒂斯', 'Mykolas Rakutis', '維爾紐斯（信義）', '立陶宛信義會', 2, 1941, 1950, '被捕', '正統',
 'Lutheran Church in Lithuania records',
 '納粹德國佔領及蘇聯再佔領期間任職；1950年被蘇聯當局逮捕'),
('馬丁納斯·薩蓋拉', 'Martynas Sagelaitis', '維爾紐斯（信義）', '立陶宛信義會', 3, 1950, 1976, '逝世', '正統',
 'Lutheran Church in Lithuania records',
 '蘇聯佔領下秘密維持教會；信義會在立陶宛主要集中於梅梅爾地區（Klaipėda）和薩莫吉希亞地區'),
('約納斯·卡拉里斯', 'Jonas Kalvanas Sr.', '維爾紐斯（信義）', '立陶宛信義會', 4, 1976, 1995, '退休', '正統',
 'Lutheran Church in Lithuania records',
 '蘇聯晚期及立陶宛獨立恢復（1990年）期間領導立陶宛信義會；教會重建關鍵人物'),
('約庫巴斯·庫尼格利斯', 'Jokūbas Kunigėlis', '維爾紐斯（信義）', '立陶宛信義會', 5, 1995, 2011, '退休', '正統',
 'Lutheran Church in Lithuania records',
 '立陶宛信義會大主教；獨立後教會恢復與成長期；與全球信義宗聯盟重新接軌'),
('明道加斯·薩布蒂斯', 'Mindaugas Sabutis', '維爾紐斯（信義）', '立陶宛信義會', 6, 2011, NULL, NULL, '正統',
 'Lutheran Church in Lithuania records',
 '現任立陶宛信義宗大主教（2011年就任）；積極推動立陶宛信義宗國際關係及青年事工');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '維爾紐斯（信義）' AND church = '立陶宛信義會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- 主教傳承：費城（衛理）（美非衛理聖公會 AME）
-- ============================================================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('理查·艾倫', 'Richard Allen', '費城（衛理）', '美非衛理聖公會', 1, 1816, 1831, '逝世', '正統',
 'AME Church records; Allen, The Life Experience and Gospel Labors of the Rt. Rev. Richard Allen',
 'AME教會創始人暨首任主教（1816年就任）；前奴隸，後獲自由；費拉德爾菲亞的非裔美國人社群領袖；1794年創立自由非裔衛理公會（Free African Society）；1816年費城大會正式建立AME；廢奴運動倡導者'),
('莫里斯·布朗', 'Morris Brown', '費城（衛理）', '美非衛理聖公會', 2, 1828, 1849, '逝世', '正統',
 'AME Church records',
 '第二任AME主教；曾參與伏羅-特納陰謀（Vesey conspiracy）後從南卡羅來納逃往費拉德爾菲亞；推動AME在東北部擴展'),
('愛德華·沃特斯', 'Edward Waters', '費城（衛理）', '美非衛理聖公會', 3, 1836, 1847, '逝世', '正統',
 'AME Church records',
 '第三任AME主教；愛德華·沃特斯學院（Edward Waters College，佛羅里達）以其命名'),
('丹尼爾·亞歷山大·佩恩', 'Daniel Alexander Payne', '費城（衛理）', '美非衛理聖公會', 4, 1852, 1893, '逝世', '正統',
 'AME Church records; Payne, Recollections of Seventy Years',
 '第六任AME主教；教育學家；創立韋爾本力學院（Wilberforce University）並任首任院長（1856年）；AME神學教育奠基人；著有《AME教會史》'),
('亨利·麥克尼爾·特納', 'Henry McNeal Turner', '費城（衛理）', '美非衛理聖公會', 5, 1880, 1915, '逝世', '正統',
 'AME Church records',
 '第十二任AME主教；南北戰爭期間首位非裔美國人陸軍牧師；重建時期喬治亞州政治人物；後期提倡非裔美國人移居非洲；AME在非洲擴展的推動者'),
('班傑明·阿諾德德·塔克爾', 'Benjamin Tucker Tanner', '費城（衛理）', '美非衛理聖公會', 6, 1888, 1908, '退休', '正統',
 'AME Church records',
 '第十四任AME主教；神學家兼新聞記者；曾任《AME教會評論》（AME Church Review）編輯；畫家亨利·奧薩瓦·坦納之父'),
('理查·亨利·懷特', 'Richard Harvey Cain', '費城（衛理）', '美非衛理聖公會', 7, 1880, 1887, '逝世', '正統',
 'AME Church records',
 '第十三任AME主教；重建時期南卡羅來納州國會眾議員；廢奴運動社群建設先驅'),
('理查·羅伯特·賴特', 'Richard Robert Wright Jr.', '費城（衛理）', '美非衛理聖公會', 8, 1936, 1967, '退休', '正統',
 'AME Church records',
 '第十九任AME主教；銀行家及社會學家；創立AME第一銀行；非裔美國人金融自立的推動者'),
('喬治·德懷特·格里格斯', 'George Dwight Grigsby', '費城（衛理）', '美非衛理聖公會', 9, 1964, 1976, '退休', '正統',
 'AME Church records',
 '民權運動時代AME主教'),
('約翰·亞當斯·居多爾', 'John Hurst Adams', '費城（衛理）', '美非衛理聖公會', 10, 1972, 2004, '退休', '正統',
 'AME Church records',
 'AME主教（多個教區）；1980年代南非反種族隔離運動的AME代表；非裔美國人與非洲教會聯繫的推動者'),
('維拉德·埃文斯', 'Vinton Randolph Anderson', '費城（衛理）', '美非衛理聖公會', 11, 1972, 2004, '退休', '正統',
 'AME Church records',
 'AME主教；世界教協（WCC）主席（1991–1998年）；非裔美國人教會在普世教會運動的代表'),
('亞當·詹佛森·理查森', 'Adam Jefferson Richardson Jr.', '費城（衛理）', '美非衛理聖公會', 12, 1996, 2016, '退休', '正統',
 'AME Church records',
 'AME主教；第十二教區（田納西）主教；民權時代後期教會擴展'),
('維拉德·格林菲爾德·格雷格斯', 'Gregory Guillory Michael McKinley Ingram', '費城（衛理）', '美非衛理聖公會', 13, 2000, 2016, '退休', '正統',
 'AME Church records',
 'AME主教；第一教區（費城）主教；非洲傳教及社會正義事工'),
('雷金納德·T·傑克遜', 'Reginald T. Jackson', '費城（衛理）', '美非衛理聖公會', 14, 2004, NULL, NULL, '正統',
 'AME Church records',
 '現任AME高齡首席主教（Senior Bishop，依資歷最長計）；第六教區（佐治亞）主教；選民權利倡導者；2020年以後AME社會正義聲音代表');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '費城（衛理）' AND church = '美非衛理聖公會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;
