-- ================================================================
-- 手動補齊無法從亞當/夏娃樹推算的人物代數
-- 每次執行 autolink 後執行此腳本
-- ================================================================

-- 修正 比利亞 的 children 欄位，使用完整名稱以便 CTE 能匹配（CUV2010：希伯→希別）
UPDATE biblical_people SET children = '希別（亞設之孫）、瑪結（亞設之孫）'
  WHERE name_zh = '比利亞（亞設之子）';

-- 重新傳播一次（讓 瑪結（亞設之孫）從 比利亞 得到代數）
UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;

-- ── 拿鶴支族（與亞伯拉罕同代，第20代）────────────────────────────
UPDATE biblical_people SET generation = 20 WHERE name_zh = '流瑪';

-- ── 以掃支族人物（第23代左右）──────────────────────────────────────
UPDATE biblical_people SET generation = 23 WHERE name_zh = '亭納（以利法的妾）';

-- ── 以東王（創 36:31-43）無父子傳承紀錄，按在位順序估算代數 ────────
-- 比拉是以東第一王，應與雅各同代或稍晚（第22代）
UPDATE biblical_people SET generation = 22 WHERE name_zh = '比拉（比珥之子）'   AND generation IS NULL;
UPDATE biblical_people SET generation = 23 WHERE name_zh = '戶珊'               AND generation IS NULL;
UPDATE biblical_people SET generation = 23 WHERE name_zh = '哈達（比達之子）'   AND generation IS NULL;
UPDATE biblical_people SET generation = 24 WHERE name_zh = '桑拉'               AND generation IS NULL;
UPDATE biblical_people SET generation = 24 WHERE name_zh = '掃羅（河邊之人）'   AND generation IS NULL;
UPDATE biblical_people SET generation = 25 WHERE name_zh = '巴勒‧哈南（亞革波之子）' AND generation IS NULL;
UPDATE biblical_people SET generation = 25 WHERE name_zh = '哈達爾（以東末王）'   AND generation IS NULL;
UPDATE biblical_people SET generation = 25 WHERE name_zh = '米希他別'           AND generation IS NULL;

-- ── 米甸人（葉忒羅、何巴）──────────────────────────────────────────
-- 葉忒羅是摩西岳父，比摩西（第26代）長一輩
UPDATE biblical_people SET generation = 25 WHERE name_zh = '葉特羅' AND generation IS NULL;
-- 何巴是葉忒羅之子（摩西的妻兄）
UPDATE biblical_people SET generation = 26 WHERE name_zh = '何巴（摩西的內兄）' AND generation IS NULL;

-- ── 十二探子（與摩西同期，第27代）──────────────────────────────────
UPDATE biblical_people SET generation = 27 WHERE name_zh IN (
  '迦勒（耶孚尼之子）',
  '約書亞（嫩之子）',
  '沙母亞（沙刻之子）',
  '沙法（何利之子）',
  '以迦（約色之子）',
  '帕提（拉孚之子）',
  '迦疊（梭底之子）',
  '迦底（穌西之子）',
  '亞米利（基瑪利之子）',
  '西帖（米迦勒之子）',
  '拿比（縛西之子）',
  '臼利（瑪基之子）'
) AND generation IS NULL;

-- ── 約書亞記時代（第27-29代）────────────────────────────────────────
UPDATE biblical_people SET generation = 27 WHERE name_zh IN (
  '俄陀聶（基納斯之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 29 WHERE name_zh IN (
  '喇合',
  '以笏（基拉之子）',
  '沙姆迦（亞拿特之子）',
  '亞比挪庵',
  '約阿施（基甸之父）'
) AND generation IS NULL;

-- ── 士師時代（第30-32代）────────────────────────────────────────────
UPDATE biblical_people SET generation = 30 WHERE name_zh IN (
  '拉比多',
  '底波拉',
  '巴拉（亞比挪庵之子）',
  '西西拉',
  '希百（基尼族）',
  '雅億（希百之妻）',
  '基甸（約阿施之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 31 WHERE name_zh IN (
  '亞比米勒（基甸之子）',
  '約坦（基甸之子）',
  '耶弗他（基列人）',
  '瑪挪亞（但族）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 32 WHERE name_zh IN (
  '參孫（瑪挪亞之子）',
  '大利拉',
  '耶弗他之女'
) AND generation IS NULL;

-- ── 撒母耳記時代（第31-34代）────────────────────────────────────────
UPDATE biblical_people SET generation = 31 WHERE name_zh IN (
  '以利（祭司）',
  '以利加拿（撒母耳之父）',
  '哈拿',
  '毘尼拿',
  '基士（亞別之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 32 WHERE name_zh IN (
  '何弗尼（以利之子）',
  '非尼哈（以利之子）',
  '撒母耳',
  '掃羅（基士之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 33 WHERE name_zh IN (
  '以迦博（非尼哈之子）',
  '約拿單（掃羅之子）',
  '伊施毘設（掃羅之子）',
  '麥基書亞（掃羅之子）',
  '亞比拿達（掃羅之子）',
  '亞實哈（掃羅之子）',
  '米拉（掃羅之女）',
  '米甲（掃羅之女）',
  '洗魯雅',
  '烏利亞（赫人）',
  '拔示巴',
  '亞希暖（耶斯列人）',
  '亞比該（迦密人）',
  '瑪迦（基述王女）',
  '哈及',
  '亞比他',
  '以格拉'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 34 WHERE name_zh IN (
  '米非波設（約拿單之子）',
  '法老之女（所羅門之妻）',
  '拿瑪（亞捫女）',
  '耶羅波安（以色列王）'
) AND generation IS NULL;

-- ── 以色列北國列王（非大衛後裔，手動補齊）──────────────────────────
UPDATE biblical_people SET generation = 34 WHERE name_zh IN (
  '巴沙', '心利', '暗利', '耶戶'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 35 WHERE name_zh IN (
  '耶洗別',
  '拿伯（伊斯列人）',
  '以利沙（沙法之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 36 WHERE name_zh IN (
  '亞他利雅',
  '亞哈謝（亞哈之子）',
  '約蘭（亞哈之子）',
  '約哈斯（耶戶之子）',
  '沙龍（以色列王）',
  '米拿現',
  '比加'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 37 WHERE name_zh IN (
  '約阿施（約哈斯之子）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 38 WHERE name_zh IN (
  '耶羅波安二世（約阿施之子）',
  '比加轄（米拿現之子）',
  '何細亞（以色列末王）'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 39 WHERE name_zh IN (
  '撒迦利雅（耶羅波安二世之子）'
) AND generation IS NULL;

-- ── 猶大大祭司與其他人物 ─────────────────────────────────────────
UPDATE biblical_people SET generation = 40 WHERE name_zh IN (
  '耶何耶大（大祭司）'
) AND generation IS NULL;

-- ── 路得記人物（非大衛直系）──────────────────────────────────────────
UPDATE biblical_people SET generation = 30 WHERE name_zh IN (
  '以利米勒', '拿俄米'
) AND generation IS NULL;

UPDATE biblical_people SET generation = 31 WHERE name_zh IN (
  '俄珥巴', '路得'
) AND generation IS NULL;

-- ── 最後再傳播一次（補齊手動賦值父代的子女）──────────────────────────
-- 例：洗魯雅(33)→約押/亞比篩/亞撒黑、迦勒(27)→亞撒、以利米勒(30)→瑪倫/基連
UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;

-- 再傳播一層（覆蓋兩層深的子代）
UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;

-- ── 歷代志補充：無父名鏈可上溯的人物 ──────────────────────────────
-- 以法蓮族長：以利沙瑪（亞米候之子）在曠野普查時（民 1:10）屬第26代前後
UPDATE biblical_people SET generation = 25 WHERE name_zh = '以利沙瑪（亞米候之子）' AND generation IS NULL;
-- 嫩（以利沙瑪之子）為約書亞之父，在 以利沙瑪 的 children 欄，第26代
-- 此傳播會在下方三層傳播中自動補入，無需手動

-- 呂便後裔族長約珥：活躍於士師至君王時代前後，約第30代
UPDATE biblical_people SET generation = 30 WHERE name_zh = '約珥（呂便後裔）' AND generation IS NULL;

-- ── 歷代志先知（與列王時代同期，手動設定）────────────────────────
-- 以賽亞（亞摩斯之子）可從 亞摩斯 children 鏈傳播；
-- 亞摩斯 本身無父名，設為與烏西雅（gen=43）同代
UPDATE biblical_people SET generation = 43 WHERE name_zh = '亞摩斯（以賽亞之父）' AND generation IS NULL;

-- 耶利米（希勒家之子）可從 希勒家（耶利米之父）children 鏈傳播；
-- 希勒家（耶利米之父）設為與約西亞（gen=49）同代
UPDATE biblical_people SET generation = 49 WHERE name_zh = '希勒家（耶利米之父）' AND generation IS NULL;

-- ── 最終再傳播三層（覆蓋歷代志新增人物） ────────────────────────
UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;

UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;

UPDATE biblical_people child_p
SET generation = parent_p.generation + 1
FROM biblical_people parent_p
WHERE child_p.generation IS NULL
  AND parent_p.children IS NOT NULL
  AND parent_p.generation IS NOT NULL
  AND position(child_p.name_zh IN parent_p.children) > 0;
