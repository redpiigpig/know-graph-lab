-- ============================================================
-- 天主教大主教傳承——伊比利亞半島（布拉加、里斯本、塔拉戈納）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 布拉加（Braga）
-- 葡萄牙最古老主教座；歷史上的葡萄牙首席大主教
-- ==============================
('聖佩多·德拉特斯', 'Saint Pedro de Rates', '布拉加', '天主教', 1, 50, 60, '殉道', '使徒傳承', '正統', 'Gallia Christiana; Flórez, España Sagrada', '傳統上由使徒雅各的弟子所創；葡萄牙天主教信仰的源頭'),
('普羅夫圖羅斯', 'Profuturus', '布拉加', '天主教', 18, 538, 538, '逝世', '教宗維吉利烏斯', '正統', 'Flórez; PL 69', '538年特倫托前的神學討論中得到教宗維吉利烏斯回覆——現存最早布拉加主教的確實記錄'),
('聖瑪爾丁·布拉加', 'Martin of Braga', '布拉加', '天主教', 19, 561, 580, '逝世', '教會選舉', '正統', 'Flórez; Martin of Braga Opera omnia', '「布拉加的聖馬丁」；斯維比人（Suebians）的宗徒；著《關於傲慢的矯正》等；使西北伊比利亞脫離阿里烏斯派'),
('弗魯克圖奧蘇斯', 'Fructuosus of Braga', '布拉加', '天主教', 25, 656, 665, '逝世', '教會選舉', '正統', 'Flórez; MGH', '「伊比利亞的修道之父」；在西北伊比利亞建立大量修道院；著《修道院規章》'),
('若阿金一世（第一任葡萄牙首席大主教稱號）', 'Paio Mendes', '布拉加', '天主教', 60, 1118, 1137, '逝世', '教宗加里斯都二世', '正統', 'PMH; Erdmann, Origins of the Idea of Crusade', '恢復後的布拉加首席大主教地位；支持葡萄牙獨立（阿方索·恩里克斯）'),
('若阿金·德布拉加', 'D. Afonso I, first king''s support see', '布拉加', '天主教', 63, 1147, 1175, '逝世', '教宗尤金尼烏斯三世', '正統', 'PMH', '葡萄牙王國創建（1139）後的主要宗教支柱；與第一任葡萄牙國王阿方索一世關係密切'),
('佩德羅·德弗裡亞斯', 'Pedro de Frias', '布拉加', '天主教', 78, 1382, 1395, '逝世', '教宗克萊孟七世（阿維尼翁）', '爭議', 'PMH', '西方大分裂期間；阿維尼翁服從的葡萄牙主教；而葡萄牙政府忠於羅馬——複雜的分裂期'),
('迪奧戈·德蘇薩', 'Diogo de Sousa', '布拉加', '天主教', 88, 1505, 1532, '逝世', '教宗尤利烏斯二世', '正統', 'PMH; Flórez', '人文主義者；重建布拉加市容；葡萄牙最重要的文藝復興型主教；布拉加大教堂裝飾的推動者'),
('若澤·達科斯塔·努內斯·達席爾瓦', 'Gaspar de Bragança', '布拉加', '天主教', 97, 1758, 1789, '逝世', '教宗克萊孟十三世', '正統', 'Catholic Hierarchy', '布拉干薩王室的王子；啟蒙時代的大主教；龐巴爾侯爵（首相）改革的配合者'),
('曼努埃爾·馬丁斯·馬努埃爾·卡爾多索', 'Américo Ferreira dos Santos Silva', '布拉加', '天主教', 105, 1871, 1884, '退休', '教宗庇護九世', '正統', 'Catholic Hierarchy', '在任期間葡萄牙共和運動興起；反對世俗化浪潮'),
('曼努埃爾·若澤·馬丁斯·巴羅斯', 'Jorge Ortiga', '布拉加', '天主教', 116, 2000, 2022, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '法蒂瑪百年紀念期間的布拉加首席大主教'),
('荷塞·托倫蒂諾·卡拉薩·德梅登薩', 'José Tolentino Calaça de Mendonça', '布拉加', '天主教', 117, 2023, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '詩人暨神學家；曾任梵蒂岡圖書館館長；教宗方濟각的親信顧問');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '布拉加' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 里斯本（Lisbon）
-- 葡萄牙首都；1716年升格為宗主教區（儀典性頭銜）
-- ==============================
('聖維森特·德薩拉戈薩', 'Verissimus of Lisbon', '里斯本', '天主教', 1, 303, 304, '殉道', '使徒傳承', '正統', 'Flórez; España Sagrada', '里斯本最早的殉道者之一；西班牙·葡萄牙最著名的早期殉道者維森特（Vincent of Saragossa）為同時期'),
('伊爾德方索斯', 'Hildephonsus', '里斯本', '天主教', 10, 525, 535, '逝世', '西哥特王', '正統', 'Flórez', '西哥特統治時期里斯本主教；614年伊西多爾時代的伊比利亞教會組織'),
('索埃羅·韋耶加斯', 'Soeiro Viegas', '里斯本', '天主教', 48, 1210, 1232, '逝世', '教宗英諾森三世', '正統', 'PMH', '葡萄牙王國鞏固時期；支持門迪卡特（托缽修會）在里斯本建立'),
('費爾南多·達格那爾', 'Fernando da Guerra', '里斯本', '天主教', 58, 1417, 1467, '逝世', '教宗馬丁五世', '正統', 'PMH', '航海王子亨利時代；里斯本主教座堂擴建；葡萄牙探索非洲的宗教中心'),
('若爾熱·達科斯塔', 'Jorge da Costa', '里斯本', '天主教', 60, 1480, 1501, '辭職', '教宗西斯都四世', '正統', 'PMH', '樞機；大航海時代初期；主持麥哲倫遠航的背景教會人物'),
('米格爾·達席爾瓦', 'Miguel da Silva', '里斯本', '天主教', 61, 1515, 1525, '轉任', '教宗利奧十世', '正統', 'PMH', '人文主義者；馬努埃爾一世的外交使節；後因與約翰三世衝突流亡至羅馬'),
('阿方索·達科斯塔', 'Afonso de Castelo Branco', '里斯本', '天主教', 70, 1604, 1615, '逝世', '教宗保祿五世', '正統', 'Catholic Hierarchy', '葡萄牙被哈布斯堡統治（1580–1640）時期；維護葡萄牙教會傳統'),
('努諾·達库尼亞·阿蒂亞德', 'Nuno da Cunha e Ataíde', '里斯本', '天主教', 77, 1716, 1750, '逝世', '教宗克萊孟十一世', '正統', 'Catholic Hierarchy', '首位里斯本宗主教（1716年升格）；若昂五世（「最忠信的國王」）時代'),
('葡京彭波薩爾·梅洛', 'José Manuel de Melo', '里斯本', '天主教', 81, 1788, 1808, '逝世', '教宗庇護六世', '正統', 'Catholic Hierarchy', '1755年里斯本大地震後的重建時代（龐巴爾改革）；法軍入侵（1807–1808）前夕'),
('帕特里亞卡·雷科雷', 'Manuel Clemente', '里斯本', '天主教', 88, 2013, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '樞機；第88任里斯本宗主教；世界青年節（WYD 2023）主辦大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '里斯本' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 塔拉戈納（Tarragona）
-- 西班牙最古老的主教座；伊比利亞首席大主教（Primas Hispaniarum 稱號有爭議）
-- ==============================
('聖弗魯克圖奧蘇斯', 'Saint Fructuosus of Tarragona', '塔拉戈納', '天主教', 6, 259, 259, '殉道', '教會傳承', '正統', 'Prudentius, Peristephanon; Flórez', '259年戴克里先迫害前的殉道主教；羅馬最重要的早期殉道者之一；奧古斯丁和普魯登提烏斯均有讚頌'),
('若翰·達拉貢一世', 'Benet de Rocabertí', '塔拉戈納', '天主教', 35, 1286, 1291, '辭職', '教宗尼古拉四世', '正統', 'Flórez', '阿拉貢王國的鼎盛時代'),
('佩雷·迪克拉蒙特', 'Pere d''Urrea i de Cardona', '塔拉戈納', '天主教', 45, 1445, 1489, '逝世', '教宗尤金尼烏斯四世', '正統', 'Flórez', '阿拉貢-卡斯提爾合併（1469）前的最後幾任大主教之一'),
('安東尼奧·阿古斯丁', 'Antonio Agustín', '塔拉戈納', '天主教', 52, 1576, 1586, '逝世', '教宗額我略十三世', '正統', 'Flórez; DSB', '歐洲最偉大的法律史學家之一；《對話錄》（Diálogos）奠定西班牙法律人文主義；特倫托後宗教改革實踐'),
('胡安·德阿斯佩', 'Juan de Asprer', '塔拉戈納', '天主教', 67, 1794, 1811, '逝世（戰爭中）', '教宗庇護六世', '正統', 'Catholic Hierarchy', '拿破崙入侵西班牙期間（1808–1814）；半島戰爭時大主教'),
('胡安·熱瑪·伊·奧利瓦斯', 'Joan Enric Vives i Sicília', '塔拉戈納', '天主教', 82, 2004, 2022, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '任安道爾大主教兼塔拉戈納大主教；加泰羅尼亞民族主義的宗教立場表態'),
('斯特法諾·加林多·加里多', 'Sergio Fenoy', '塔拉戈納', '天主教', 83, 2022, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '現任塔拉戈納大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '塔拉戈納' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
