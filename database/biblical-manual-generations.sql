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

-- ── 舊約剩餘族譜：手動設定根節點代數 ─────────────────────────────

-- 以斯拉/尼希米（被擄後歸回，gen 53-55）
UPDATE biblical_people SET generation = 53 WHERE name_zh = '哈迦利雅'            AND generation IS NULL;
-- 以斯拉（祭司文士）名稱無「之子/女」，無法被 autolink；主前 458 年回歸，約 gen 55
UPDATE biblical_people SET generation = 55 WHERE name_zh = '以斯拉（祭司文士）'  AND generation IS NULL;
-- 散巴拉/多比雅/迦善與尼希米同期（gen 54）
UPDATE biblical_people SET generation = 54 WHERE name_zh IN (
  '散巴拉（撒瑪利亞長官）', '多比雅（亞捫人）', '迦善（阿拉伯人）'
) AND generation IS NULL;

-- 何西阿書（北國，約主前 760-720）
UPDATE biblical_people SET generation = 39 WHERE name_zh = '比利（何西阿之父）'  AND generation IS NULL;
-- 歌篾之父底比連不在 DB，歌篾無法透過 autolink 或 CTE 取得代數，手動補同期（gen 40）
UPDATE biblical_people SET generation = 40 WHERE name_zh = '歌篾（底比連之女）'  AND generation IS NULL;

-- 約珥書（時代不確定，置於亞摩司前後）
UPDATE biblical_people SET generation = 38 WHERE name_zh = '毗土利（約珥之父）'  AND generation IS NULL;

-- 阿摩司書（北國，約主前 760）
UPDATE biblical_people SET generation = 39 WHERE name_zh = '阿摩司（提哥亞牧人）' AND generation IS NULL;

-- 俄巴底亞書（時代不確定，估算約主前 845-840，約西法王時代前後）
UPDATE biblical_people SET generation = 45 WHERE name_zh = '俄巴底亞（先知）'    AND generation IS NULL;

-- 約拿書（北國，耶羅波安二世時代，約主前 780）
UPDATE biblical_people SET generation = 42 WHERE name_zh = '亞米太（約拿之父）'  AND generation IS NULL;

-- 彌迦書（猶大，約主前 730-700）
UPDATE biblical_people SET generation = 44 WHERE name_zh = '彌迦（摩利沙人）'    AND generation IS NULL;

-- 那鴻書（約主前 660-630）
UPDATE biblical_people SET generation = 47 WHERE name_zh = '那鴻（伊勒歌斯人）'  AND generation IS NULL;

-- 哈巴谷書（約主前 609-598）
UPDATE biblical_people SET generation = 49 WHERE name_zh = '哈巴谷（先知）'      AND generation IS NULL;

-- 以西結書（布西為以西結之父，與約西亞同代前後）
UPDATE biblical_people SET generation = 48 WHERE name_zh = '布西（以西結之父）'  AND generation IS NULL;

-- 但以理書（被擄至巴比倫，約主前 605）
UPDATE biblical_people SET generation = 50 WHERE name_zh IN (
  '但以理（先知）',
  '哈拿尼雅（但以理之友）',
  '米沙利（但以理之友）',
  '亞撒利雅（但以理之友）'
) AND generation IS NULL;

-- 哈該書（被擄後，約主前 520）
UPDATE biblical_people SET generation = 54 WHERE name_zh = '哈該（先知）'        AND generation IS NULL;

-- 撒迦利亞書（易多為撒迦利亞之祖父，被擄後歸回，gen 54）
UPDATE biblical_people SET generation = 54 WHERE name_zh = '易多（先知/祭司）'   AND generation IS NULL;

-- 瑪拉基書（約主前 450）
UPDATE biblical_people SET generation = 56 WHERE name_zh = '瑪拉基（先知）'      AND generation IS NULL;

-- 巴路克（耶利米的書記，被擄時代，gen 51）
-- 馬西雅為乃利亞之父（gen 49），乃利亞（gen 50），巴路克/西萊雅（gen 51）
UPDATE biblical_people SET generation = 49 WHERE name_zh = '馬西雅（乃利亞之父）' AND generation IS NULL;

-- 約伯記（傳統列祖時代，約亞伯拉罕/以撒同期）
UPDATE biblical_people SET generation = 22 WHERE name_zh IN (
  '約伯（烏斯人）',
  '以利法（帖曼人）',
  '比勒達（書亞人）',
  '瑣法（拿阿瑪人）',
  '巴拿基勒（以利戶之父）'
) AND generation IS NULL;

-- ── 次經/第二正典：手動設定根節點代數 ─────────────────────────────

-- 多比傳（北國被擄時期，約主前 722-700）
UPDATE biblical_people SET generation = 45 WHERE name_zh = '托彼爾（多比之父）'  AND generation IS NULL;
UPDATE biblical_people SET generation = 46 WHERE name_zh = '辣古耳（撒拉之父）'  AND generation IS NULL;
-- 亞娜（多比之妻）、厄德納（辣古耳之妻）無子女名稱模式，無法被 autolink/CTE，手動補同期
UPDATE biblical_people SET generation = 46 WHERE name_zh IN (
  '亞娜（多比之妻）', '厄德納（辣古耳之妻）'
) AND generation IS NULL;
-- 辣法耳天使不屬人類世代，指定同期以便資料完整
UPDATE biblical_people SET generation = 46 WHERE name_zh = '辣法耳（天使）'      AND generation IS NULL;

-- 友弟德傳（波斯/希臘時代，估算約主前 450 前後）
UPDATE biblical_people SET generation = 49 WHERE name_zh = '默辣黎（友弟德之父）' AND generation IS NULL;
UPDATE biblical_people SET generation = 50 WHERE name_zh IN (
  '瑪拿西（友弟德之夫）', '敖羅斐乃'
) AND generation IS NULL;

-- 德訓篇（約主前 180 年）
UPDATE biblical_people SET generation = 58 WHERE name_zh IN (
  '耶穌·本·西拉', '西門（耶路撒冷大祭司）'
) AND generation IS NULL;

-- 哈斯蒙王朝根節點（其餘可從名稱括號自動傳播）
UPDATE biblical_people SET generation = 63 WHERE name_zh = '西默盎（哈斯蒙族長）' AND generation IS NULL;

-- 瑪加比二書補充人物（與猶大瑪加比同期，gen 66-67）
UPDATE biblical_people SET generation = 67 WHERE name_zh IN (
  '耶松（大祭司）', '默乃勞斯（大祭司）', '以利亞匝爾（書記）', '撒羅默（七子之母）'
) AND generation IS NULL;

-- ── 偽經與拉比傳統：手動設定代數 ────────────────────────────────

-- 禧年書：亞哇/亞士拉（亞當之女，gen 2）和挪亞姆（塞特之女，gen 3）、
--   慕阿利拉（以挪士之女，gen 4）可由 autolink 自動取得，無需手動
-- 以下為父名不在 DB、或使用「之妻」命名無法被 autolink 的人物：
UPDATE biblical_people SET generation = 5 WHERE name_zh IN (
  '底娜斯（瑪哈拉列之妻）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 6 WHERE name_zh IN (
  '以斯尼（雅列之妻）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 7 WHERE name_zh IN (
  '以底尼（以諾之妻）'
) AND generation IS NULL;
-- 拉忽雅（以諾之女）可 autolink 到以諾（gen 7），得 gen 8，無需手動
UPDATE biblical_people SET generation = 10 WHERE name_zh IN (
  '以墨拉（挪亞之妻）',
  '塞達（閃之妻）', '娜阿利瑪圖（含之妻）', '亞達達奈斯（雅弗之妻）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 23 WHERE name_zh IN (
  '巴特書亞（猶大之妻）'
) AND generation IS NULL;

-- 以諾書：守望者下降在以諾時代前後（gen 7-9）
UPDATE biblical_people SET generation = 7 WHERE name_zh IN (
  '示米哈匝（守望者之首）', '亞薩谷（守望者）',
  '可加別（守望者）', '巴拉基雅勒（守望者）', '撒姆雅匝（守望者）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 8 WHERE name_zh = '拿非利人' AND generation IS NULL;

-- 死海古卷（馬加比時代前後）
UPDATE biblical_people SET generation = 66 WHERE name_zh IN (
  '義師（公義教師）', '邪惡祭司'
) AND generation IS NULL;

-- 先賢篇：五對傳道師（Zugot，主前 250-30 年）
UPDATE biblical_people SET generation = 62 WHERE name_zh = '安提哥努斯（科霍人）'           AND generation IS NULL;
UPDATE biblical_people SET generation = 65 WHERE name_zh IN (
  '約西·本·約珥（以祿得）', '約西·本·約哈南（耶路撒冷）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 67 WHERE name_zh IN (
  '約書亞·本·比利加', '尼太（亞拉比利人）'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 68 WHERE name_zh IN (
  '猶大·本·他比', '西緬·本·沙他'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 69 WHERE name_zh IN (
  '示瑪雅', '亞伯他雍'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 70 WHERE name_zh = '沙買'                         AND generation IS NULL;

-- 希勒家系根節點（其後代可從名稱括號 autolink 逐代傳播）
UPDATE biblical_people SET generation = 71 WHERE name_zh = '希勒（長者）'                  AND generation IS NULL;

-- 重要塔納伊姆（非希勒家系）
UPDATE biblical_people SET generation = 72 WHERE name_zh = '拉比·約哈南·本·匝凱'          AND generation IS NULL;
UPDATE biblical_people SET generation = 73 WHERE name_zh IN (
  '拉比·以利以謝·本·許爾加諾', '拉比·約書亞·本·哈拿尼雅'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 74 WHERE name_zh IN (
  '拉比·亞基瓦·本·約瑟', '拉比·以實瑪利·本·以利沙'
) AND generation IS NULL;
UPDATE biblical_people SET generation = 75 WHERE name_zh IN (
  '拉比·米厄爾', '拉比·西緬·巴約哈', '拉比·猶大·本·以萊'
) AND generation IS NULL;

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
