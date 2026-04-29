-- ============================================================
-- 使徒統緒：教座分裂與對立主教資料
-- 執行前請確保已執行 episcopal-succession.sql 及 episcopal-succession-seed.sql
-- ============================================================
-- 分裂類型說明：
--   status = '對立'   → 同時期爭奪同一主教座的非公認者
--   不同 church 值    → 教會永久分裂後各自延續的獨立統緒線
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- 一、羅馬（Rome）— 對立教宗與多重統緒
-- ════════════════════════════════════════════════════════════
-- 羅馬主要對立教宗（歷史上共有約 40 位對立教宗）
-- 此處列出早期及大分裂時期最具代表性者

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

-- 最早有紀錄的對立教宗
('聖依玻里圖', 'Saint Hippolytus of Rome', '羅馬', '未分裂教會', NULL, 217, 235, '殉道', '對立',
 'Eusebius, HE VI.20; Liber Pontificalis',
 '教會史上第一位有紀錄的對立教宗；後與正統教宗卡利斯圖一世和解，最終以殉道者身份受尊崇'),

-- 西方大分裂（1378–1417）期間，一度有三位聲稱合法的教宗
('對立教宗克肋孟七世', 'Antipope Clement VII', '羅馬', '天主教（亞維農系）', NULL, 1378, 1394, '自然死亡', '對立',
 'Conciliarist sources; Valois, La France et le Grand Schisme d''Occident',
 '西方大分裂起點；烏爾巴諾六世當選後，部分樞機主教另立其於亞維農，形成雙教宗局面'),
('對立教宗本篤十三世', 'Antipope Benedict XIII', '羅馬', '天主教（亞維農系）', NULL, 1394, 1423, '自然死亡', '對立',
 'Valois; Crowder, Unity, Heresy and Reform',
 '亞維農系最後一位對立教宗；被康士坦斯大公會議廢黜後仍拒絕退位'),
('對立教宗若望二十三世', 'Antipope John XXIII', '羅馬', '天主教（比薩系）', NULL, 1410, 1415, '廢黜', '對立',
 'Crowder; Finke & Fink, Councils and Ecclesiastical Reform',
 '比薩公會議另立第三系，形成三教宗並立；後被康士坦斯大公會議廢黜，退位後獲赦');

-- 設定西方大分裂對立關聯（rival_of 指向同期正統教宗）
UPDATE episcopal_succession
  SET rival_of = (SELECT id FROM episcopal_succession WHERE name_en = 'Pope Urban VI' AND see = '羅馬' AND status = '正統' LIMIT 1)
  WHERE name_zh = '對立教宗克肋孟七世';

-- 注意：烏爾巴諾六世若尚未加入資料，rival_of 暫為 NULL，待補入後再執行上述 UPDATE


-- ════════════════════════════════════════════════════════════
-- 二、亞歷山大（Alexandria）— 三至四條統緒線
-- ════════════════════════════════════════════════════════════
-- 451 年迦克敦公會議後分裂為：
--   (A) 東正教（希臘禮，迦克敦派）
--   (B) 科普特正教（米亞非西特派，Oriental Orthodox）
-- 後來再分出：
--   (C) 科普特天主教（與羅馬共融，1895 年正式建立）

-- (A) 東正教亞歷山大宗主教（迦克敦派，延續至今）
-- 前五任（馬爾谷至普理穆斯）已在 seed 檔以 church='未分裂教會' 列入
-- 分裂點附近的關鍵人物：
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('聖濟利祿一世', 'Saint Cyril I of Alexandria', '亞歷山大', '東正教', 24, 412, 444, '自然死亡', '正統',
 'ACO I; Eusebius Hist. Eccl.; Cyril''s own writings',
 '迦克敦前最重要的亞歷山大主教；主導 431 年以弗所公會議，確立聖母為天主之母'),
('狄奧斯科魯一世', 'Dioscorus I of Alexandria', '亞歷山大', '科普特正教', 25, 444, 454, '廢黜', '爭議',
 'ACO II; Price & Gaddis, Acts of Chalcedon',
 '451 年迦克敦公會議廢黜其職；東正教視其為對立，科普特正教視其為殉道者——此為兩統緒分裂的起點'),

-- (B) 科普特正教（Oriental Orthodox，以開羅為中心，傳承至今）
('聖馬爾谷', 'Saint Mark the Evangelist', '亞歷山大', '科普特正教', 1, 42, 68, '殉道', '正統',
 'Eusebius, HE II.16; Coptic Synaxarion',
 '科普特正教視馬爾谷為其統緒之源，與東正教共享同一早期傳承'),
('班亞明一世', 'Benjamin I of Alexandria', '亞歷山大', '科普特正教', 38, 622, 661, '自然死亡', '正統',
 'History of the Patriarchs of Alexandria',
 '阿拉伯征服埃及（642年）時在位；此後科普特正教在伊斯蘭統治下延續'),

-- (C) 科普特天主教宗主教（1895 年正式確立，與羅馬共融）
('西里爾八世·瑪喀里烏斯二世', 'Cyril VIII Macarius II', '亞歷山大', '科普特天主教', 1, 1895, 1908, '自然死亡', '正統',
 'Catholic Encyclopedia; Annuario Pontificio',
 '1895 年教宗良十三世正式設立科普特天主教宗主教區，為首任宗主教');


-- ════════════════════════════════════════════════════════════
-- 三、安提阿（Antioch）— 五條統緒線
-- ════════════════════════════════════════════════════════════
-- 451 年後陸續分裂為：
--   (A) 東正教安提阿宗主教（迦克敦派，總部現在大馬士革）
--   (B) 敘利亞正教宗主教（米亞非西特，雅各派，總部現在大馬士革/達木爾）
--   (C) 馬龍尼特禮宗主教（始終與羅馬共融，總部在貝科法亞）
--   (D) 希臘天主教麥勒基特禮宗主教（1724 年部分東正教主教轉向羅馬）
--   (E) 敘利亞天主教宗主教（1782 年部分敘利亞正教轉向羅馬）

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- (A) 東正教安提阿宗主教（總部今大馬士革）
('聖伯多祿', 'Saint Peter', '安提阿', '東正教', 1, 37, 53, '不明', '耶穌基督', '正統',
 'Eusebius, HE III.36',
 '與安提阿天主教公用同一早期傳承；451年迦克敦後分為兩線'),

-- (B) 敘利亞正教安提阿宗主教（雅各派，Oriental Orthodox）
('塞維魯', 'Severus of Antioch', '安提阿', '敘利亞正教', 34, 512, 518, '廢黜', NULL, '正統',
 'Eusebius (later sources)',
 '敘利亞正教最重要的早期神學家；被查士丁尼一世廢黜，流亡埃及，死後仍受敘利亞正教尊為聖人'),
('塞奧多西安一世', 'Theodosius I of Antioch', '安提阿', '敘利亞正教', 35, 519, 521, '廢黜', NULL, '正統',
 NULL,
 '廢黜後敘利亞正教宗主教座長期懸缺'),

-- (C) 馬龍尼特禮宗主教（始終與羅馬共融）
('聖瑪朗', 'Saint Maron', '安提阿', '馬龍尼特禮天主教', NULL, NULL, 410, '自然死亡', NULL, '正統',
 'Theodoret, Historia Religiosa; John Maron sources',
 '馬龍尼特禮名稱來源；修道士，非宗主教職，但為其神學傳承之祖'),
('若望·瑪朗', 'John Maron', '安提阿', '馬龍尼特禮天主教', 1, 685, 707, '自然死亡', '使徒伯多祿（間接）', '正統',
 'Maronite Patriarchal sources; Dau, History of the Maronites',
 '馬龍尼特禮首位宗主教；確立與羅馬的共融關係'),

-- (D) 希臘天主教麥勒基特禮宗主教（1724年分立）
('濟利祿六世·塔納斯', 'Cyril VI Tanas', '安提阿', '希臘天主教麥勒基特禮', 1, 1724, 1759, '自然死亡', NULL, '正統',
 'Hajjar, Les chrétiens uniates du Proche-Orient',
 '1724 年東正教安提阿宗主教選舉後，部分主教轉向羅馬，另立麥勒基特禮統緒'),

-- (E) 敘利亞天主教宗主教（1782年分立）
('米迦勒·賈爾韋', 'Michael Jarweh', '安提阿', '敘利亞天主教', 1, 1782, 1800, '自然死亡', NULL, '正統',
 'Anatolios, Chalcedon in Context',
 '1782 年從敘利亞正教分出，承認羅馬教宗權威');


-- ════════════════════════════════════════════════════════════
-- 四、君士坦丁堡（Constantinople）— 拉丁宗主教（1204–1964）
-- ════════════════════════════════════════════════════════════
-- 1054 大分裂後，1204 年第四次十字軍東征攻陷君士坦丁堡，
-- 天主教另立拉丁宗主教；1261 年拜占庭光復後成為流亡/名義職位，
-- 1964 年教宗保祿六世與普世宗主教雅典納哥拉一世和解後廢除。

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('湯瑪斯·莫羅辛尼', 'Thomas Morosini', '君士坦丁堡', '天主教（拉丁禮）', 1, 1204, 1211, '自然死亡', '對立',
 'Longnon, L''Empire latin de Constantinople; Wolff, Latin Empire',
 '第四次十字軍後第一任拉丁宗主教；東正教普世宗主教系視其為非法'),
('雅典納哥拉一世', 'Athenagoras I', '君士坦丁堡', '東正教', 268, 1948, 1972, '自然死亡', '正統',
 'Ecumenical Patriarchate records',
 '1964 年與教宗保祿六世在耶路撒冷歷史性會面，撤回 1054 年雙方互相的破門令');


-- ════════════════════════════════════════════════════════════
-- 五、耶路撒冷（Jerusalem）— 三至四條統緒線
-- ════════════════════════════════════════════════════════════
-- 現存主要統緒：
--   (A) 東正教耶路撒冷宗主教（希臘禮，迦克敦派）
--   (B) 拉丁禮宗主教（十字軍建立，1291 年成為名義職，1847 年實際復設）
--   (C) 亞美尼亞耶路撒冷宗主教（獨立統緒，非源自亞歷山大或安提阿）

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- (B) 拉丁禮耶路撒冷宗主教
('戈弗雷德·布永', 'Godfrey of Bouillon', '耶路撒冷', '天主教（拉丁禮）', NULL, 1099, 1100, '自然死亡', '十字軍諸侯', '正統',
 'William of Tyre, Historia rerum in partibus transmarinis gestarum',
 '第一次十字軍攻克耶路撒冷後拒絕稱王，以「聖墓守護者」頭銜治城；傳統列為拉丁統緒之始'),
('達戈伯特·德·比薩', 'Daimbert of Pisa', '耶路撒冷', '天主教（拉丁禮）', 1, 1099, 1102, '廢黜', NULL, '正統',
 'William of Tyre; Albert of Aix',
 '耶路撒冷拉丁宗主教座首任正式宗主教；後被廢黜'),

-- (C) 亞美尼亞耶路撒冷宗主教（自 638 年阿拉伯征服後逐漸獨立成型）
('亞伯拉罕一世', 'Abraham I of Jerusalem', '耶路撒冷', '亞美尼亞正教', 1, 638, 669, '自然死亡', NULL, '正統',
 'Armenian Patriarchate of Jerusalem archives',
 '亞美尼亞正教耶路撒冷宗主教座傳統上首任；阿拉伯征服後確立其地位');
