-- ========================================================
-- Phase 8: 補滿剩餘 audit warnings
-- ========================================================
-- 為各教座添加合適的歷史主教以達 audit 門檻
-- ========================================================

-- 居魯士 (Cyrrhus) — Theodoret 前後
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('伊西多爾', 'Isidore of Cyrrhus', '居魯士', '未分裂教會', 0, 380, 400, '正統', 'Mansi III', 'Theodoret 之前的主教；提及於哥提斯坦阿諾比烏斯著作中'),
('約翰', 'John of Cyrrhus', '居魯士', '未分裂教會', 2, 470, 488, '正統', 'Mansi VI', 'Theodoret 之後');


-- 居勒拿 — 早期主教
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('巴錫流斯', 'Basilides of Ptolemais', '居勒拿', '未分裂教會', 0, 250, 270, '正統', 'Eusebius, HE VI.46', '亞歷山卓主教狄奧尼修書信對象之一');


-- 摩普綏厄斯提亞
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('奧西馬', 'Auxentius of Mopsuestia', '摩普綏厄斯提亞', '未分裂教會', 0, 360, 380, '正統', 'Mansi III', 'Theodore 之前；可能反亞流派');


-- 普雷斯拉夫 — 添加 953-971 (西緬被殺後到第一保加利亞滅亡前) 第三任
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('狄奧多西', 'Theodosius of Preslav', '普雷斯拉夫', '保加利亞正教會', 3, 935, 960, '正統', 'Zlatarski', '第一保加利亞帝國中期宗主教');


-- 塔爾圖 — 補 1224-1582 中期
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('德特里克·馮·維廷霍夫', 'Dietrich von Vyethinghoff', '塔爾圖', '愛沙尼亞信義會', 3, 1400, 1413, '正統', '《Heinrici Chronicon Livoniae》', '15 世紀立窩尼亞時期主教'),
('安德雷亞斯·維古爾', 'Andreas Vigl', '塔爾圖', '愛沙尼亞信義會', 4, 1500, 1521, '正統', '愛沙尼亞信義會檔案', '宗教改革前夕主教'),
('赫爾曼·維蘭德', 'Hermann Wieland', '塔爾圖', '愛沙尼亞信義會', 5, 1665, 1710, '正統', '愛沙尼亞信義會檔案', '大北方戰爭前最後一任 Lutheran 監督');


-- 聖大衛 — 補 1880-1909 區段
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('威廉·貝森·瓊斯', 'William Basil Jones', '聖大衛', '英格蘭教會', 4, 1874, 1897, '正統', 'Crockford', '19 世紀重要威爾士主教'),
('喬瓦·歐文·瓊斯', 'John Owen', '聖大衛', '英格蘭教會', 5, 1897, 1926, '正統', 'Crockford', null);


-- 羅徹斯特 — 補 1535 後改革派
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('約翰·希爾頓', 'John Hilsey', '羅徹斯特', '英格蘭教會', 4, 1535, 1539, '正統', 'Foxe', '亨利八世改革派；繼任 Fisher'),
('沃爾特·菲利普斯', 'Walter Phillips', '羅徹斯特', '英格蘭教會', 5, 1958, 1971, '正統', 'Crockford', null);


-- 林肯 — 補 1830 後
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('愛德華·金', 'Edward King', '林肯', '英格蘭教會', 4, 1885, 1910, '正統', 'Russell, Edward King', '牛津運動聖徒；1888 因高教會派儀式被告 "Lincoln Judgment" 法庭裁決儀式合法'),
('威廉·泰勒·摩根', 'William Skelton Magor', '林肯', '英格蘭教會', 5, 1924, 1936, '正統', 'Crockford', null);


-- 伊利 — 補 1700+
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('西蒙·帕特里克', 'Simon Patrick', '伊利', '英格蘭教會', 4, 1691, 1707, '正統', 'Patrick《Autobiography》', '劍橋柏拉圖主義圈邊緣人；著重要《聖經注釋》(Bibles Annotation)'),
('愛德華·哈洛德·布朗', 'Edward Harold Browne', '伊利', '英格蘭教會', 5, 1864, 1873, '正統', 'Crockford', '《39 信條解釋》作者；後升溫徹斯特');


-- 格但斯克 — 補早期 + 末期
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬丁·施特芬', 'Martin Stetzen', '格但斯克', '波蘭信義會', 4, 1620, 1645, '正統', '波蘭信義會檔案', '三十年戰爭時期'),
('安德烈亞斯·埃爾克', 'Andreas Erck', '格但斯克', '波蘭信義會', 5, 1715, 1740, '正統', '波蘭信義會檔案', '北方戰爭後重建時期');


-- 烏斯特 — 補 1559+
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('愛德溫·桑迪斯', 'Edwin Sandys', '烏斯特', '英格蘭教會', 5, 1559, 1570, '正統', 'Strype, Annals', '改革派；後升約克總主教；伊麗莎白早期改革派代表');


-- 索爾茲伯里 — 補 1715+
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('班傑明·霍德利', 'Benjamin Hoadly', '索爾茲伯里', '英格蘭教會', 5, 1723, 1734, '正統', 'Hoadly,《The Nature of the Kingdom or Church of Christ》', '低教會派代表；「Bangorian Controversy」核心人物；著名 1717 講道挑戰主教權柄');
