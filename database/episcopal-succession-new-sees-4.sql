-- ============================================================
-- 天主教大主教傳承——新增主教座（第四批）
-- 亞的斯亞貝巴、費城、布里斯本、墨爾本、達累斯薩拉姆
-- ============================================================

-- ==============================
-- 11. 亞的斯亞貝巴（Addis Ababa）天主教
-- 1961年設立大主教區；衣索比亞天主教中心
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('里納爾多·齊貝利', 'Asrate Yemane Berhan', '亞的斯亞貝巴', '天主教', 1, 1961, 1977, '逝世', '教宗若望二十三世', '正統', 'Catholic Hierarchy; Molony, The Church in Ethiopia', '亞的斯亞貝巴首任天主教大主教（1961年升格）；在任期間衣索比亞帝制（海勒·塞拉西）到共產政府（德爾格）的劇烈轉型；1974年革命後的迫害'),
('帕利奧斯·沃爾德-薩馬亞特', 'Paulos Tzadua', '亞的斯亞貝巴', '天主教', 2, 1977, 1998, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機（1985年）；德爾格共產政府（1977-1991）統治下的天主教；1984-1985年衣索比亞大饑荒期間的教會救援工作；1991年衣索比亞解放後的天主教復興'),
('貝爾哈內耶蘇斯·德梅魯·索拉菲耶爾', 'Berhaneyesus Demerew Souraphiel', '亞的斯亞貝巴', '天主教', 3, 1999, NULL, NULL, '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機（2016年）；現任亞的斯亞貝巴大主教；非洲天主教主教代表會議（SECAM）積極參與者；衣索比亞提格雷戰爭（2020-2022）期間的和平倡議')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '亞的斯亞貝巴' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 12. 費城（Philadelphia）
-- 1875年設立大主教區至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('詹姆斯·弗雷德里克·伍德', 'James Frederick Wood', '費城', '天主教', 1, 1875, 1883, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy; Connelly, The History of the Archdiocese of Philadelphia', '費城首任大主教（1875年升格）；此前已任費城主教（1860-1875）；美國內戰後重建時代；推動教區學校建立'),
('帕特里克·約翰·瑞安', 'Patrick John Ryan', '費城', '天主教', 2, 1884, 1911, '逝世', '教宗良十三世', '正統', 'Catholic Hierarchy', '愛爾蘭裔移民大主教；建立費城天主教教育體系；著名演說家；費城工人階級天主教社區的精神領袖'),
('埃德蒙·弗朗西斯·佩倫達', 'Edmond Francis Prendergast', '費城', '天主教', 3, 1911, 1918, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '第一次世界大戰期間；費城天主教繼續擴張'),
('丹尼斯·卡迪納爾·多赫提', 'Dennis Cardinal Dougherty', '費城', '天主教', 4, 1918, 1951, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機（1921年）；禁酒令時代；大蕭條；二戰；美國天主教人口鼎盛期；建立大量教區學校；在位33年'),
('約翰·弗朗西斯·奧哈拉', 'John Francis O''Hara', '費城', '天主教', 5, 1951, 1960, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機（1958年）；聖母大學前校長；冷戰時代美國天主教反共立場'),
('約翰·喬治福雷', 'John Joseph Krol', '費城', '天主教', 6, 1961, 1988, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機（1967年）；梵二大公會議代表；波蘭裔美國人；1979年教宗若望保祿二世訪美（費城）；1984年共和黨全國大會祈禱'),
('安東尼·約瑟夫·貝維拉夸', 'Anthony Joseph Bevilacqua', '費城', '天主教', 7, 1988, 2003, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機（1991年）；任內費城神職人員性醜聞開始曝光'),
('賈斯廷·弗朗西斯·裡加利', 'Justin Francis Rigali', '費城', '天主教', 8, 2003, 2011, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機（2003年）；任內費城大陪審團報告（2011年）揭露神職人員性醜聞和教區掩蓋行為——震驚全美'),
('查爾斯·約瑟夫·夏布特', 'Charles Joseph Chaput', '費城', '天主教', 9, 2011, 2020, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '方濟각會士；保守派倫理觀；性醜聞問責改革；2015年世界家庭大會（費城）教宗方濟각訪問'),
('尼爾森·佩雷斯', 'Nelson J. Perez', '費城', '天主教', 10, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任費城大主教；拉丁裔大主教；古巴裔美國人；費城首位拉丁裔大主教')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '費城' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 13. 布里斯本（Brisbane）
-- 1859年設立大主教區至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('詹姆斯·奎因', 'James Quinn', '布里斯本', '天主教', 1, 1859, 1881, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy; O''Donoghue, Priests and People in Australia', '布里斯本首任天主教主教（1859年設立）；愛爾蘭聖科倫邦會士；昆士蘭殖民地天主教奠基者；建聖斯蒂芬大教堂'),
('若望·道斯', 'Robert Dunne', '布里斯本', '天主教', 2, 1882, 1917, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '1905年升格為大主教區；昆士蘭聯邦化（1901）；天主教學校系統建立'),
('詹姆斯·達西', 'James Duhig', '布里斯本', '天主教', 3, 1917, 1965, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '在位48年；外號「建設達西」（Duhig the Builder）；建造大量教堂學校；第一次和第二次世界大戰；昆士蘭天主教教育史上最重要人物'),
('帕特里克·羅蘭·費拉羅', 'Patrick Boyle', '布里斯本', '天主教', 4, 1966, 1973, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '梵二後改革實施'),
('弗朗西斯·羅伯特·拉什', 'Francis Rush', '布里斯本', '天主教', 5, 1973, 1991, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '1982年教宗若望保祿二世訪問布里斯本；澳洲天主教主教代表會議領袖'),
('約翰·巴蒂', 'John Bathersby', '布里斯本', '天主教', 6, 1992, 2012, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '澳洲天主教性醜聞調查初步期；2008年世界青年節（雪梨）支持'),
('馬克·科爾里奇', 'Mark Coleridge', '布里斯本', '天主教', 7, 2012, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '現任布里斯本大主教；梵蒂岡皇家通訊辦公室前工作經歷；澳洲主教代表會議主席（2018-）；2023年澳洲原住民之聲公投期間的教會立場')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '布里斯本' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 14. 墨爾本（Melbourne）
-- 1874年設立大主教區至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('若望·伊利亞斯·高爾丁', 'James Goold', '墨爾本', '天主教', 1, 1848, 1886, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy; Annals of the Diocese of Melbourne', '墨爾本首任天主教主教（1848年設立）；1874年升格為大主教；奧古斯丁會士；淘金熱時代（1850年代）昆士蘭殖民地；建聖帕特里克大教堂（始建1858）'),
('托馬斯·約瑟夫·哈特尼特', 'Thomas Carr', '墨爾本', '天主教', 2, 1886, 1917, '逝世', '教宗良十三世', '正統', 'Catholic Hierarchy', '澳大利亞聯邦（1901）；墨爾本聖帕特里克大教堂竣工（1897）；愛爾蘭裔天主教移民群體發展'),
('丹尼爾·曼尼克斯', 'Daniel Mannix', '墨爾本', '天主教', 3, 1917, 1963, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '澳大利亞最具影響力的天主教大主教；反徵兵（1916-1917）；與愛爾蘭獨立運動同情；反共產主義；天主教工人運動；在位46年；梵二大公會議最年長代表（91歲）'),
('詹姆斯·諾克斯', 'James Knox', '墨爾本', '天主教', 4, 1967, 1974, '調任', '教宗保羅六世', '正統', 'Catholic Hierarchy', '梵二後改革；後調任羅馬任傳信部官員'),
('弗蘭克·利特爾', 'Frank Little', '墨爾本', '天主教', 5, 1974, 1996, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '墨爾本天主教社會正義工作；1986年教宗若望保祿二世訪問墨爾本'),
('喬治·佩爾', 'George Pell', '墨爾本', '天主教', 6, 1996, 2001, '調任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '後調任雪梨；2001年任樞機；2014年調梵蒂岡任財政秘書長；2018年被澳洲法院定罪（2020年高等法院撤銷）；墨爾本性醜聞調查（Royal Commission）關鍵人物'),
('丹尼斯·哈特', 'Denis Hart', '墨爾本', '天主教', 7, 2001, 2018, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '皇家委員會（Royal Commission into Institutional Responses to Child Sexual Abuse, 2013-2017）期間；澳洲主教代表會議主席'),
('彼得·科門索利', 'Peter Comensoli', '墨爾本', '天主教', 8, 2018, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任墨爾本大主教；性醜聞後改革；澳洲原住民和解議題；2023年澳洲之聲公投期間的教會立場')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '墨爾本' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 15. 達累斯薩拉姆（Dar es Salaam）
-- 1953年設立大主教區至今
-- ==============================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
VALUES
('埃德加·伊拉里烏斯·佩雷茲', 'Edgar Hilary Pereira', '達累斯薩拉姆', '天主教', 1, 1953, 1960, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy; Rweyemamu, A History of the Catholic Church in Tanzania', '達累斯薩拉姆首任天主教大主教（1953年升格）；坦干伊喀英屬統治末期；坦尚尼亞獨立（1961）前夕'),
('拉烏爾·鮑威爾', 'Laurean Rugambwa', '達累斯薩拉姆', '天主教', 2, 1960, 1968, '調任', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '第一位非洲裔樞機（1960年）——非洲天主教歷史里程碑；坦干伊喀獨立（1961）；坦尚尼亞聯合共和國成立（1964）；後調任布科巴（Bukoba）'),
('波利卡普·佩內哈利', 'Polycarp Pengo', '達累斯薩拉姆', '天主教', 3, 1969, 1992, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '尼雷爾（Nyerere）烏賈馬（Ujamaa）社會主義時代；坦尚尼亞天主教本地化（Africanization）'),
('博納文圖拉·物倫古', 'Polycarp Pengo', '達累斯薩拉姆', '天主教', 4, 1992, 2019, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機（1998年）；坦尚尼亞多黨民主化（1992年後）；非洲天主教主教代表會議（SECAM）領袖；在任27年'),
('若望·達達烏斯·魯瓦依奇', 'Jude Thaddeus Ruwa ichi', '達累斯薩拉姆', '天主教', 5, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任達累斯薩拉姆大主教；坦尚尼亞天主教社會發展工作')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '達累斯薩拉姆' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
