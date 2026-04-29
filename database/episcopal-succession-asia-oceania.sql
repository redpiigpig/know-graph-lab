-- ============================================================
-- 天主教大主教傳承——亞洲（東京、孟買、河內）及大洋洲（雪梨）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 東京（Tokyo）
-- 日本天主教首席大主教區
-- ==============================
('若望·瑪麗·歐吉耶', 'Jean Marie Osouf', '東京', '天主教', 1, 1891, 1906, '退休', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '東京大主教區首任大主教（1891年設立）；明治日本；法國巴黎外方傳教會（MEP）'),
('亞歷山大·貝尼耶', 'Alexandre Berlioz', '東京', '天主教', 2, 1906, 1927, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '巴黎外方傳教會；關東大地震（1923）期間的牧養'),
('帕斯卡·奧博納', 'Pascal Robin', '東京', '天主教', 3, 1927, 1937, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '日本軍國主義興起時代'),
('保羅·勝野恒夫', 'Mgr. Paul Yoshigoro Taguchi', '東京', '天主教', 4, 1937, 1941, '轉任', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '首位日本籍大阪主教；東京暫代'),
('保羅·鐸斐', 'Paul Marella', '東京', '天主教', 5, 1941, 1948, '轉任', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '義大利裔；二戰期間（1941–1945）的困難牧養；日本戰敗後的重建'),
('彼得·德納', 'Peter Doi Tatsuo', '東京', '天主教', 6, 1948, 1970, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；日本第一位本土樞機（1960年）；梵二大公會議日本代表'),
('若望·沙卡夫', 'Joseph Asajiro Satowaki', '東京', '天主教', 8, 1970, 2000, '退休（2000）', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；長崎大主教（1968–2000）暨東京輔理；後任東京大主教——待查'),
('岡田武夫', 'Peter Takeo Okada', '東京', '天主教', 9, 2000, 2017, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '日本天主教主教會議主席；福島核災（2011）後的社會倫理發言'),
('菊地功', 'Tarcisius Isao Kikuchi', '東京', '天主教', 10, 2017, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '日本天主教主教會議主席；方濟각托缽修會（OFM Cap）；亞洲主教會議（FABC）積極參與者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '東京' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 孟買（Mumbai/Bombay）
-- 印度最大天主教城市；羅馬禮（與西里爾-瑪拉巴爾禮并存）
-- ==============================
('納波萊昂·布魯諾·亞西瑟', 'Napolean Cardoso', '孟買', '天主教', 1, 1886, 1904, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '孟買首任大主教（1886年設立大主教區）；英屬印度時代；與果阿帕德羅亞多（Padroado）分歧'),
('若望·喬瑟夫·黑基', 'John Joseph Hicky', '孟買', '天主教', 3, 1920, 1936, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '英屬印度晚期；甘地獨立運動期間'),
('托馬斯·羅伯茨', 'Thomas Roberts', '孟買', '天主教', 5, 1937, 1950, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '耶穌會士；提前退休以使印度人接任；核武器道德問題（反對英美核試）的大膽發言者'),
('瓦萊里安·格拉西亞斯', 'Valerian Gracias', '孟買', '天主教', 6, 1950, 1978, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；印度第一位樞機（1953年）；梵二大公會議主持委員之一；印度獨立（1947）後的教會本土化'),
('賽蒙·皮門塔', 'Simon Pimenta', '孟買', '天主教', 7, 1978, 2006, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；印度緊急狀態（1975–1977）後的民主恢復時代；本土化推進'),
('伊万·迪亞斯', 'Ivan Dias', '孟買', '天主教', 8, 1996, 2006, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後任聖座萬民福音部部長；外交官背景'),
('奧斯瓦爾德·格拉西亞斯', 'Oswald Gracias', '孟買', '天主教', 9, 2006, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；教宗方濟각樞機顧問委員會（C9）成員；亞洲主教會議積極參與者；印度天主教最有影響力的主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '孟買' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 河內（Hanoi）
-- 越南北部天主教大主教區
-- ==============================
('保祿-弗朗索瓦·普呂歇', 'Paul-François Puginier', '河內', '天主教', 3, 1868, 1892, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '法國殖民時期（1883年法越簽約）；河內（東京教區）的福傳發展；巴黎外方傳教會（MEP）'),
('弗朗索瓦·拉尤厄', 'François Laumonier', '河內', '天主教', 4, 1892, 1906, '退休', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '河內設立大主教區（1924年）的前身；法屬印度支那時代'),
('路易·德克維蘭', 'Louis de Cooman', '河內', '天主教', 6, 1935, 1950, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '二戰日本佔領（1940–1945）；越盟（Việt Minh）興起；第一次印度支那戰爭開始'),
('約瑟夫·瑪麗亞·鄭如峰', 'Joseph Maria Trịnh Như Khuê', '河內', '天主教', 7, 1950, 1978, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；越南首位樞機；越南分裂（1954）後在北越共產政府管轄下維持教會；河內大主教區在無神論政策壓力下的生存'),
('若瑟夫·瑪麗·鄭文康', 'Joseph Maria Trịnh Văn Căn', '河內', '天主教', 8, 1978, 1990, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；越南戰後統一（1975）後的教會存活；越共政府的宗教政策'),
('保祿·若瑟·范廷藻', 'Paul Josef Phạm Đình Tụng', '河內', '天主教', 9, 1994, 2010, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；越南教會的正常化外交；梵蒂岡-越南關係的改善'),
('彼得·阮文仁', 'Peter Nguyễn Văn Nhơn', '河內', '天主教', 10, 2010, 2018, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '越南天主教主教會議主席'),
('若瑟·武文提恩', 'Joseph Vũ Văn Thiên', '河內', '天主教', 11, 2018, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '越南-梵蒂岡外交關係進一步正常化期間');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '河內' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 雪梨（Sydney）
-- 澳大利亞天主教首席大主教區
-- ==============================
('若翰·鮑爾', 'John Bede Polding', '雪梨', '天主教', 1, 1835, 1877, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '澳大利亞首任主教（1835）及大主教（1842年升格）；本篤會士；英格蘭裔；對原住民抱持同情態度；服務囚犯移民社區'),
('羅傑·莫利根', 'Roger Bede Vaughan', '雪梨', '天主教', 2, 1877, 1883, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '本篤會士；反對義務公立教育（主張天主教學校系統）'),
('帕特里克·莫蘭', 'Patrick Moran', '雪梨', '天主教', 3, 1884, 1911, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；澳大利亞第一位樞機；愛爾蘭裔；推動澳大利亞聯邦（1901）；勞工權利支持者'),
('邁克爾·凱利', 'Michael Kelly', '雪梨', '天主教', 4, 1911, 1940, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '一戰、大蕭條期間；推動天主教學校系統擴張'),
('諾曼·湯馬斯·吉爾羅伊', 'Norman Thomas Gilroy', '雪梨', '天主教', 5, 1940, 1971, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議參與者；澳大利亞工黨天主教移民社區的橋梁'),
('詹姆斯·弗里曼', 'James Freeman', '雪梨', '天主教', 6, 1971, 1983, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；梵二後改革推動者'),
('愛德華·克利夫頓·班奈', 'Edward Clancy', '雪梨', '天主教', 7, 1983, 2001, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；2008年世界青年節（雪梨）的奠基準備工作'),
('喬治·佩爾', 'George Pell', '雪梨', '天主教', 8, 2001, 2014, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；2008年世界青年節（WYD Sydney）；後任聖座財政秘書處部長（C9成員）；2018年因性醜聞被定罪、2020年上訴得直後獲釋；2023年逝世'),
('安東尼·菲舍爾', 'Anthony Fisher', '雪梨', '天主教', 9, 2014, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '多明我會士；生命倫理學家；澳大利亞天主教主教會議主席（2018–）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '雪梨' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
