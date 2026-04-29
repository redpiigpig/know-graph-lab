-- ============================================================
-- 使徒統緒種子資料 — 五大宗主教座首任主教
-- 執行前請確保已建立 episcopal_succession table
-- 人名以天主教譯名為主（Protestant 括號備注）
-- 教會：未分裂教會 = 1054 年大分裂以前
-- 年份：主後正數；帶 * 之君士坦丁堡前任為傳統記載，歷史可考性低
-- ============================================================

-- ── 一、羅馬（Rome）──────────────────────────────────────────
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, sources, notes) VALUES
('聖伯多祿', 'Saint Peter', '羅馬', '未分裂教會', 1, 30, 64, '殉道', '耶穌基督', 'Irenaeus, AH III.3; Eusebius, HE II.14; Liber Pontificalis', '使徒之長，於尼祿迫害中倒釘十字架殉道'),
('聖利諾', 'Saint Linus', '羅馬', '未分裂教會', 2, 67, 76, '殉道', NULL, 'Irenaeus, AH III.3; Eusebius, HE III.2; 提後 4:21', '保羅書信（提後 4:21）中提及其名'),
('聖阿納克勒圖', 'Saint Anacletus', '羅馬', '未分裂教會', 3, 76, 88, '殉道', NULL, 'Irenaeus, AH III.3; Eusebius, HE III.13', '又稱 Cletus；愛任紐列為羅馬第三任主教'),
('聖克雷孟一世', 'Saint Clement I', '羅馬', '未分裂教會', 4, 88, 99, '殉道', NULL, 'Irenaeus, AH III.3; Eusebius, HE III.15', '著有《致科林多人書》，早期護教重要文獻'),
('聖艾瓦里斯圖', 'Saint Evaristus', '羅馬', '未分裂教會', 5, 99, 107, '殉道', NULL, 'Eusebius, HE III.34; Liber Pontificalis', NULL);

-- ── 二、君士坦丁堡（Constantinople）─────────────────────────
-- 第 1–4 任為傳統記載（Pseudo-Dorotheus 等來源），歷史可考性低
-- 第 16 任美特羅法內斯一世（306 年）起有較可靠史料
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, sources, notes) VALUES
('斯達基斯', 'Stachys', '君士坦丁堡', '未分裂教會', 1, 38, 54, '自然死亡', '使徒安德肋', 'Pseudo-Dorotheus; 羅馬書 16:9', '羅 16:9 保羅問候其名；傳統記載為安德肋所立'),
('阿尼西慕', 'Onesimus', '君士坦丁堡', '未分裂教會', 2, 54, 68, '殉道', NULL, 'Pseudo-Dorotheus', '傳統記載，歷史可考性低'),
('波利加坡一世', 'Polycarpus I', '君士坦丁堡', '未分裂教會', 3, 71, 89, '自然死亡', NULL, 'Pseudo-Dorotheus', '傳統記載；勿與士每拿的坡旅甲混淆'),
('普路塔克', 'Plutarch', '君士坦丁堡', '未分裂教會', 4, 89, 105, '殉道', NULL, 'Pseudo-Dorotheus', '傳統記載'),
('美特羅法內斯一世', 'Metrophanes I', '君士坦丁堡', '未分裂教會', 16, 306, 314, '自然死亡', NULL, 'Socrates Scholasticus, HE I.37; Sozomen, HE I.2', '最早有可靠史料記載的君士坦丁堡主教；據 Socrates，任次或為第 16 任');

-- ── 三、亞歷山大（Alexandria）────────────────────────────────
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, sources, notes) VALUES
('聖馬爾谷', 'Saint Mark the Evangelist', '亞歷山大', '未分裂教會', 1, 42, 68, '殉道', '使徒伯多祿', 'Eusebius, HE II.16; Clement of Alexandria apud Eusebius', '福音書作者，由伯多祿差遣至埃及，傳統上殉道於亞歷山大（4月25日）'),
('阿尼阿努斯', 'Anianus', '亞歷山大', '未分裂教會', 2, 68, 83, '自然死亡', NULL, 'Eusebius, HE II.24; III.14', '傳統上為馬爾谷所按立'),
('阿維里烏斯', 'Avilius', '亞歷山大', '未分裂教會', 3, 83, 95, '自然死亡', NULL, 'Eusebius, HE III.14', NULL),
('塞爾東', 'Cerdon', '亞歷山大', '未分裂教會', 4, 95, 106, '自然死亡', NULL, 'Eusebius, HE III.21', NULL),
('普理穆斯', 'Primus', '亞歷山大', '未分裂教會', 5, 106, 118, '自然死亡', NULL, 'Eusebius, HE III.21; IV.1', NULL);

-- ── 四、安提阿（Antioch）─────────────────────────────────────
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, sources, notes) VALUES
('聖伯多祿', 'Saint Peter', '安提阿', '未分裂教會', 1, 37, 53, '不明', '耶穌基督', 'Eusebius, HE III.36; Origen apud Eusebius HE VI.25', '使徒之長，傳統安提阿首任主教；後赴羅馬'),
('以沃迪烏斯', 'Evodius', '安提阿', '未分裂教會', 2, 53, 69, '殉道', NULL, 'Eusebius, HE III.22', '由使徒伯多祿按立'),
('聖依納爵', 'Saint Ignatius of Antioch', '安提阿', '未分裂教會', 3, 69, 107, '殉道', NULL, 'Eusebius, HE III.36; Ignatius 書信集（7封）', '著有七封書信；押解至羅馬被野獸撕裂殉道（約主後 107–115年）'),
('海羅', 'Heron', '安提阿', '未分裂教會', 4, 107, 127, '自然死亡', NULL, 'Eusebius, HE III.36; IV.20', NULL),
('科爾涅利烏斯', 'Cornelius of Antioch', '安提阿', '未分裂教會', 5, 127, 154, '自然死亡', NULL, 'Eusebius, HE IV.20', NULL);

-- ── 五、耶路撒冷（Jerusalem）─────────────────────────────────
-- 前 15 任均為猶太基督徒主教（135 年巴爾科赫巴起義前）
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, sources, notes) VALUES
('義人雅各伯', 'James the Just', '耶路撒冷', '未分裂教會', 1, 30, 62, '殉道', '使徒眾人', 'Eusebius, HE II.1; II.23; Josephus, Ant. XX.9; 加 1:19', '主的兄弟，耶路撒冷首任主教；62 年被推下聖殿後石擊殉道'),
('西默盎', 'Simeon of Jerusalem', '耶路撒冷', '未分裂教會', 2, 62, 107, '殉道', NULL, 'Eusebius, HE III.11; III.32', '克羅帕之子，主的親族；傳統於圖拉真年間被釘十字架，享壽甚高'),
('猶斯都一世', 'Justus I', '耶路撒冷', '未分裂教會', 3, 107, 111, '不明', NULL, 'Eusebius, HE IV.5', '猶太基督徒主教之一，年份不確定'),
('匝哈烏斯', 'Zacchaeus', '耶路撒冷', '未分裂教會', 4, 111, 113, '不明', NULL, 'Eusebius, HE IV.5', NULL),
('托比亞斯', 'Tobias', '耶路撒冷', '未分裂教會', 5, 113, 116, '不明', NULL, 'Eusebius, HE IV.5', NULL);


-- ── 設定 predecessor_id（前任關聯）────────────────────────────

-- 羅馬
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖伯多祿' AND see = '羅馬') WHERE name_zh = '聖利諾' AND see = '羅馬';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖利諾' AND see = '羅馬') WHERE name_zh = '聖阿納克勒圖' AND see = '羅馬';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖阿納克勒圖' AND see = '羅馬') WHERE name_zh = '聖克雷孟一世' AND see = '羅馬';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖克雷孟一世' AND see = '羅馬') WHERE name_zh = '聖艾瓦里斯圖' AND see = '羅馬';

-- 君士坦丁堡
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '斯達基斯' AND see = '君士坦丁堡') WHERE name_zh = '阿尼西慕' AND see = '君士坦丁堡';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '阿尼西慕' AND see = '君士坦丁堡') WHERE name_zh = '波利加坡一世' AND see = '君士坦丁堡';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '波利加坡一世' AND see = '君士坦丁堡') WHERE name_zh = '普路塔克' AND see = '君士坦丁堡';

-- 亞歷山大
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖馬爾谷' AND see = '亞歷山大') WHERE name_zh = '阿尼阿努斯' AND see = '亞歷山大';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '阿尼阿努斯' AND see = '亞歷山大') WHERE name_zh = '阿維里烏斯' AND see = '亞歷山大';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '阿維里烏斯' AND see = '亞歷山大') WHERE name_zh = '塞爾東' AND see = '亞歷山大';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '塞爾東' AND see = '亞歷山大') WHERE name_zh = '普理穆斯' AND see = '亞歷山大';

-- 安提阿
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖伯多祿' AND see = '安提阿') WHERE name_zh = '以沃迪烏斯' AND see = '安提阿';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '以沃迪烏斯' AND see = '安提阿') WHERE name_zh = '聖依納爵' AND see = '安提阿';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '聖依納爵' AND see = '安提阿') WHERE name_zh = '海羅' AND see = '安提阿';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '海羅' AND see = '安提阿') WHERE name_zh = '科爾涅利烏斯' AND see = '安提阿';

-- 耶路撒冷
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '義人雅各伯' AND see = '耶路撒冷') WHERE name_zh = '西默盎' AND see = '耶路撒冷';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '西默盎' AND see = '耶路撒冷') WHERE name_zh = '猶斯都一世' AND see = '耶路撒冷';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '猶斯都一世' AND see = '耶路撒冷') WHERE name_zh = '匝哈烏斯' AND see = '耶路撒冷';
UPDATE episcopal_succession SET predecessor_id = (SELECT id FROM episcopal_succession WHERE name_zh = '匝哈烏斯' AND see = '耶路撒冷') WHERE name_zh = '托比亞斯' AND see = '耶路撒冷';
