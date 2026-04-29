-- ============================================================
-- 天主教大主教傳承——非洲（金夏沙、奈洛比、坎帕拉、開普敦）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 金夏沙（Kinshasa / Léopoldville）
-- 撒哈拉以南非洲最大天主教城市
-- ==============================
('費利西安·凱尼法西烏斯', 'Félicien Keniface', '金夏沙', '天主教', 1, 1959, 1964, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '金夏沙（雷奧波德維爾）首任大主教；剛果獨立（1960年6月30日）前後的設立；比利時傳教遺產的過渡'),
('雅辛特·馬魯拉', 'Hyacinthe (Joseph-Albert) Malula', '金夏沙', '天主教', 2, 1964, 1989, '逝世', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；剛果第一位樞機（1969年）；剛果語彌撒（扎伊爾禮儀）的先驅；與蒙博托政權的衝突（1972年遭驅逐，後獲准返回）；非洲天主教本土化最重要的推動者'),
('弗雷德里克·埃措', 'Frédéric Etsou-Nzabi-Bamungwabi', '金夏沙', '天主教', 3, 1990, 2007, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；扎伊爾／民主剛果內戰期間；人道危機中的教會聲音'),
('洛朗·蒙森戈·帕辛亞', 'Laurent Monsengwo Pasinya', '金夏沙', '天主教', 4, 2007, 2018, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；聖經學者；剛果政治危機（2016–2018卡比拉延長任期爭議）中的調停聲音；教宗方濟각的C9顧問委員'),
('弗里多蘭·安邦戈·貝桑古', 'Fridolin Ambongo Besungu', '金夏沙', '天主教', 5, 2018, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '樞機；嘉布遣方濟各會士；教宗方濟각C9成員；非洲主教會議主席（SECAM）；批評《天主教義宣言》（Fiducia Supplicans）在非洲文化脈絡下的適用');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '金夏沙' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 奈洛比（Nairobi）
-- 東非天主教重心
-- ==============================
('約翰·江森', 'John Joseph McCarthy', '奈洛比', '天主教', 1, 1953, 1971, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '奈洛比首任大主教（1953年設立）；愛爾蘭傳教士；肯亞獨立（1963年）前後的過渡'),
('馬丁斯·奧孔杰', 'Raphael Ndingi Mwana a''Nzeki', '奈洛比', '天主教', 4, 1997, 2007, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '肯亞天主教主教會議主席；人權倡導者；批評政府腐敗'),
('約翰·恩洞奎奇', 'John Njue', '奈洛比', '天主教', 5, 2007, 2021, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；肯亞天主教主教會議主席；非洲主教大會積極參與者'),
('菲利普·納帕利', 'Philip Anyolo', '奈洛比', '天主教', 6, 2021, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任奈洛比大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '奈洛比' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 坎帕拉（Kampala）
-- 烏干達天主教中心；烏干達殉道者故鄉
-- ==============================
('約瑟夫·卡格瓦', 'Joseph Kiwánuka', '坎帕拉', '天主教', 1, 1939, 1961, '轉任', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '烏干達首任本土天主教主教（1939年，非洲最早本土化之一）；坎帕拉大主教區設立（1961年）前身'),
('愛彌爾·比安吉', 'Emmanuel Kiwanuka Nsubuga', '坎帕拉', '天主教', 2, 1966, 1990, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；烏干達首位樞機；阿明獨裁（1971–1979）時期的艱困牧養；阿明下令殺害聖公會大主教亞努班（1977）——天主教也面臨壓力'),
('伊曼紐爾·瓦莫拉', 'Emmanuel Wamala', '坎帕拉', '天主教', 3, 1990, 2006, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後愛滋時代；烏干達天主教的社會服務擴展'),
('西普里安·基岡奇', 'Cyprian Kizito Lwanga', '坎帕拉', '天主教', 4, 2006, 2021, '逝世', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '穆塞維尼政府關係緊張；批評同性戀立法同時批評過度嚴苛的處罰；2021年逝世'),
('保羅·森尼葛', 'Paul Ssemogerere', '坎帕拉', '天主教', 5, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任坎帕拉大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '坎帕拉' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 開普敦（Cape Town）
-- 南非天主教大主教座
-- ==============================
('格雷戈里奧·雷格', 'Gregorius Ricards', '開普敦', '天主教', 1, 1872, 1891, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '開普敦首任主教及大主教（1886年升格）；英國殖民地時代；爾後成為南非首席大主教傳統'),
('威廉·斯滕斯特拉', 'William Leonard', '開普敦', '天主教', 4, 1952, 1958, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '南非種族隔離（Apartheid, 1948–）開始；天主教對種族隔離的早期態度模糊'),
('歐文·麥肯', 'Owen McCann', '開普敦', '天主教', 5, 1958, 1984, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；1966年南非天主教主教會議聲明批評種族隔離；與德斯蒙德·屠圖（聖公會）的合作'),
('斯蒂芬·諾蘭', 'Stephen Naidoo', '開普敦', '天主教', 6, 1984, 1989, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '南非本土主教；強烈反對種族隔離；過早逝世'),
('勞倫斯·亨利', 'Lawrence Henry', '開普敦', '天主教', 7, 1990, 2019, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '種族隔離結束（1994）後的南非天主教重建；多元種族教區的整合；後天主教教育問題'),
('史蒂芬·莫利', 'Stephen Brislin', '開普敦', '天主教', 8, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任大主教；南非天主教主教會議主席');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '開普敦' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
