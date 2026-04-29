-- ============================================================
-- 天主教大主教傳承——美洲補充（波士頓、洛杉磯、多倫多、哈瓦那）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 波士頓（Boston）
-- 美國新英格蘭天主教中心；愛爾蘭移民最密集之地
-- ==============================
('約翰·菲茨帕特里克', 'John Fitzpatrick', '波士頓', '天主教', 2, 1846, 1866, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '愛爾蘭大飢荒（1845–1852）移民潮期間；波士頓天主教的奠基者之一；南北戰爭時支持北軍'),
('約翰·威廉姆斯', 'John Williams', '波士頓', '天主教', 3, 1866, 1907, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '首任波士頓大主教（1875年升格）；建聖十字大教堂（Holy Cross Cathedral）'),
('威廉·奧康奈爾', 'William O''Connell', '波士頓', '天主教', 4, 1907, 1944, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；波士頓愛爾蘭裔天主教的黃金時代；教育和社會影響力達顛峰'),
('理查·庫欣', 'Richard Cushing', '波士頓', '天主教', 5, 1944, 1970, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；主持甘迺迪總統就職典禮（1961年）和葬禮（1963年）；美國最有名的樞機之一；梵二大公會議'),
('昂布羅斯·莫爾丁', 'Humberto Medeiros', '波士頓', '天主教', 6, 1970, 1983, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；葡萄牙裔——波士頓多元族裔天主教的轉型'),
('伯納德·勞', 'Bernard Law', '波士頓', '天主教', 7, 1984, 2002, '辭職', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；《波士頓環球報》揭露其系統性包庇神父性騷擾事件（2002年）——觸發全球天主教性醜聞危機；辭職後赴羅馬'),
('法蘭茨·布迪奇', 'Sean O''Malley', '波士頓', '天主教', 8, 2003, NULL, NULL, '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；嘉布遣方濟各會士；教宗方濟各C9成員；性醜聞後重建波士頓教區信任；兒童保護政策推動');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '波士頓' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 洛杉磯（Los Angeles）
-- 美國最大天主教教區；西語裔為主體
-- ==============================
('若翰·約翰·胡根', 'Thaddeus Amat', '洛杉磯', '天主教', 1, 1859, 1878, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '首任洛杉磯主教（1859年）；墨西哥時代後的美國時期；西語裔天主教傳統的維護'),
('弗朗西斯·鮑爾默', 'Francis Mora', '洛杉磯', '天主教', 2, 1878, 1896, '退休', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '西班牙裔；加州早期西語裔天主教群體的代表'),
('托馬斯·康菲', 'Thomas Conaty', '洛杉磯', '天主教', 3, 1903, 1915, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '愛爾蘭裔；移民增長；首任大主教（1936年升格大主教區）'),
('約翰·卡農漢', 'John Cantwell', '洛杉磯', '天主教', 5, 1917, 1947, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '首任洛杉磯大主教（1936年升格）；好萊塢電影道德規範（Legion of Decency）的強硬推行者'),
('詹姆斯·麥金泰爾', 'James McIntyre', '洛杉磯', '天主教', 6, 1948, 1970, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；強烈保守派；反梵二後改革；批評民權運動（對Martin Luther King態度負面）'),
('蒂莫西·曼寧', 'Timothy Manning', '洛杉磯', '天主教', 7, 1970, 1985, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；麥金泰爾後的和解；加州西語裔天主教徒的增長'),
('羅傑·馬霍尼', 'Roger Mahony', '洛杉磯', '天主教', 8, 1985, 2011, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；建造洛杉磯天使之后大教堂（2002年）；農業工人組織（合作César Chávez）的支持者；晚年因包庇性醜聞神父受嚴重批評（2013年文件公開）'),
('何塞·戈麥斯', 'José Gomez', '洛杉磯', '天主教', 9, 2011, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '墨西哥裔；美國主教大會主席（2019–2022）；反對拜登總統以天主教身份支持墮胎政策');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '洛杉磯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 多倫多（Toronto）
-- 加拿大最大城市；多元移民天主教
-- ==============================
('邁克爾·鮑爾斯', 'Michael Power', '多倫多', '天主教', 1, 1842, 1847, '逝世（照護移民）', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '多倫多首任主教；愛爾蘭飢荒移民（1847年「船熱」Typhus）期間親赴照護而染病逝世；多倫多天主教奠基者'),
('若翰·約瑟夫·林奇', 'John Joseph Lynch', '多倫多', '天主教', 2, 1860, 1888, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '首任多倫多大主教（1870年升格）；愛爾蘭移民社群的整合'),
('詹姆斯·查爾斯·麥克吉根', 'James Charles McGuigan', '多倫多', '天主教', 5, 1934, 1971, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；加拿大第一位本土樞機（1946年）；梵二大公會議'),
('菲利克斯·德羅因', 'Philip Pocock', '多倫多', '天主教', 6, 1971, 1978, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '梵二後改革推動者'),
('阿隆佐·布洛格', 'Aloysius Ambrozic', '多倫多', '天主教', 7, 1990, 2006, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；克羅埃西亞裔加拿大人；移民天主教群體的代表'),
('托馬斯·科林斯', 'Thomas Collins', '多倫多', '天主教', 8, 2007, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；宗教自由倡議者；加拿大輔助死亡立法期間的強烈反對聲音');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '多倫多' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 哈瓦那（Havana）
-- 古巴首都；教宗約望保祿二世、本篤十六世、方濟各均曾訪問
-- ==============================
('格雷戈里奧·迪亞斯·托里雷斯', 'Jerónimo de Valdés', '哈瓦那', '天主教', 1, 1730, 1729, '逝世', '教宗本篤十三世', '正統', 'Catholic Hierarchy', '哈瓦那主教區創立（1787年升格大主教區前身）；殖民地時代古巴教會組織'),
('曼努埃爾·亞當斯', 'Dionisio González García', '哈瓦那', '天主教', 6, 1851, 1859, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '西班牙殖民地古巴；廢奴運動萌芽'),
('恩里克·佩雷斯·塞倫特斯', 'Enrique Pérez Serantes', '哈瓦那', '天主教', 11, 1948, 1969, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '1959年古巴革命（卡斯楚）；共產政府沒收教會財產（1961年）；神父被驅逐；此位大主教曾在1953年救下年輕的菲德爾·卡斯楚的性命（梅達河起義失敗後）'),
('傑羅尼莫·里維羅·卡洛斯', 'Francisco Ricardo Oves Fernández', '哈瓦那', '天主教', 12, 1969, 1981, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '共產古巴時代的艱難牧養；教會處於嚴格限制下'),
('賈伊梅·奧爾特加·阿拉米諾', 'Jaime Ortega y Alamino', '哈瓦那', '天主教', 13, 1981, 2016, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；1979–1980年曾被關入強制勞動營；古巴教會生存策略的主要設計者；1998年若望保祿二世訪問古巴（歷史性）；2012年本篤十六世訪問；古巴-美國關係正常化（2015年）的祕密仲介'),
('胡安·德拉卡里達·加西亞·羅德里格斯', 'Juan de la Caridad García Rodríguez', '哈瓦那', '天主教', 14, 2016, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '樞機（2019年）；卡斯楚主義古巴下的天主教新生代；2015年教宗方濟각訪問古巴的精神遺產');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '哈瓦那' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
