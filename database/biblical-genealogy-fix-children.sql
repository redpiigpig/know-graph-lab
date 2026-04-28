-- ================================================================
-- 修正 children 欄位中簡稱不符全名、以及補充缺漏的親子欄位
-- 執行後請重新執行 biblical-genealogy-generation.sql 重算代數
-- ================================================================

-- ── 1. 修正已存在但名稱不符的 children ──────────────────────────

-- 以掃：三個兒子在 DB 中有括號後綴，需更新為全名
UPDATE biblical_people
SET children = '以利法（以掃之子）、流珥（以掃之子）、耶烏施、雅蘭、可拉（以掃之子）'
WHERE name_zh = '以掃';

-- 以實瑪利：哈大 → 哈大（以實瑪利之子）
UPDATE biblical_people
SET children = REPLACE(children, '哈大', '哈大（以實瑪利之子）')
WHERE name_zh = '以實瑪利'
  AND children LIKE '%哈大%'
  AND children NOT LIKE '%哈大（%';

-- 流珥（以掃之子）：謝拉 → 謝拉（流珥之子）
UPDATE biblical_people
SET children = REPLACE(children, '謝拉', '謝拉（流珥之子）')
WHERE name_zh = '流珥（以掃之子）'
  AND children LIKE '%謝拉%'
  AND children NOT LIKE '%謝拉（%';

-- 拿鶴（他拉之子）：密迦與流瑪所生合併，烏斯 → 烏斯（拿鶴之子），瑪迦 → 瑪迦（拿鶴之子）
UPDATE biblical_people
SET children = '烏斯（拿鶴之子）、布斯、基慕利、基薛、哈瑣、必達、益拉弗、彼土利、提巴、迦含、他轄、瑪迦（拿鶴之子）'
WHERE name_zh = '拿鶴（他拉之子）';

-- ── 2. 補充缺漏的 children 欄位 ─────────────────────────────────

-- 雅弗子孫（創 10:3-4）
UPDATE biblical_people SET children = '亞實基拿、利法、陀迦瑪'
  WHERE name_zh = '歌篾' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '以利沙、他施、基提、多單'
  WHERE name_zh = '雅完' AND (children IS NULL OR children = '');

-- 含子孫（創 10:7,15）
UPDATE biblical_people SET children = '西巴（古實之子）、哈腓拉（古實之子）、撒弗他、拉瑪、撒弗提迦、寧錄'
  WHERE name_zh = '古實' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '示巴（拉瑪之子）、底但（拉瑪之子）'
  WHERE name_zh = '拉瑪' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '西頓、赫'
  WHERE name_zh = '迦南' AND (children IS NULL OR children = '');

-- 閃子孫：亞蘭（創 10:23）
UPDATE biblical_people SET children = '烏斯（亞蘭之子）、戶勒、基帖、瑪施'
  WHERE name_zh = '亞蘭' AND (children IS NULL OR children = '');

-- 閃子孫：約坍（創 10:26-29）
UPDATE biblical_people SET children = '亞摩達、沙列、哈薩瑪非、雅拉、哈多蘭、烏薩、德拉、俄巴、亞比瑪利、示巴（約坍之子）、阿斐、哈腓拉（約坍之子）、約巴'
  WHERE name_zh = '約坍' AND (children IS NULL OR children = '');

-- 基土拉後裔（創 25:2-4）
UPDATE biblical_people SET children = '示巴（約珊之子）、底但（約珊之子）'
  WHERE name_zh = '約珊' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '以法（米甸之子）、以弗、哈諾（米甸之子）、亞比大、以勒大'
  WHERE name_zh = '米甸' AND (children IS NULL OR children = '');

-- 彼土利（創 22:23；24:15）
UPDATE biblical_people SET children = '利百加、拉班'
  WHERE name_zh = '彼土利' AND (children IS NULL OR children = '');

-- 西珥族（創 36:20-28）
UPDATE biblical_people SET children = '羅單、朔巴（西珥之子）、祭便、亞拿（西珥之子）、底順（西珥之子）、以謝、底珊'
  WHERE name_zh = '西珥' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '何里（羅單之子）、黑幔'
  WHERE name_zh = '羅單' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '阿勒完、瑪拿哈、以巴、示弗、俄南（朔巴之子）'
  WHERE name_zh = '朔巴（西珥之子）' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '亞雅、亞拿（祭便之子）'
  WHERE name_zh = '祭便' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '阿何利巴瑪'
  WHERE name_zh = '亞拿（祭便之子）' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '黑慕丹、以實班、益蘭、基蘭'
  WHERE name_zh = '底順（西珥之子）' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '比利罕、撒雲、亞干（以謝之子）'
  WHERE name_zh = '以謝' AND (children IS NULL OR children = '');

UPDATE biblical_people SET children = '烏斯（底珊之子）、亞蘭（底珊之子）'
  WHERE name_zh = '底珊' AND (children IS NULL OR children = '');
