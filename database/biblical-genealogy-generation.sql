-- ================================================================
-- 聖經人物代數自動計算
-- 以亞當 / 夏娃 = 第 1 代為根，沿 children 欄位向下遞迴
-- ================================================================

-- 步驟一：新增欄位（若已存在則跳過）
ALTER TABLE biblical_people ADD COLUMN IF NOT EXISTS generation INT;

-- 步驟二：修正 children 欄位中模糊或缺漏的名稱，確保遞迴能正確追蹤

-- 瑪土撒拉：原「拉麥」無法區分兩個拉麥，改為全名
UPDATE biblical_people
  SET children = REPLACE(children, '拉麥', '拉麥（挪亞之父）')
  WHERE name_zh = '瑪土撒拉'
    AND children LIKE '%拉麥%'
    AND children NOT LIKE '%拉麥（挪亞之父）%';

-- 雅列：原「以諾」無法區分兩個以諾，改為全名
UPDATE biblical_people
  SET children = '以諾（雅列之子）'
  WHERE name_zh = '雅列' AND children = '以諾';

-- 閃後裔（創 11 章）：亞法撒→沙拉→希伯→法勒 的 children 欄位補齊
UPDATE biblical_people SET children = '沙拉'      WHERE name_zh = '亞法撒' AND (children IS NULL OR children = '');
UPDATE biblical_people SET children = '希伯'      WHERE name_zh = '沙拉'   AND (children IS NULL OR children = '');
UPDATE biblical_people SET children = '法勒、約坍' WHERE name_zh = '希伯'   AND (children IS NULL OR children = '');
UPDATE biblical_people SET children = '拉吳'      WHERE name_zh = '法勒'   AND (children IS NULL OR children = '');

-- 步驟三：清空舊代數，重新計算
UPDATE biblical_people SET generation = NULL;

-- 步驟四：遞迴計算代數
--   從亞當/夏娃 = 第 1 代出發，每下一層 + 1
--   visited 陣列用來防止迴圈（創世記中無循環，但以防萬一）
WITH RECURSIVE gen_tree AS (

  -- 根節點
  SELECT
    id,
    1 AS generation,
    ARRAY[id] AS visited
  FROM biblical_people
  WHERE name_zh IN ('亞當', '夏娃')

  UNION ALL

  -- 遞迴：從每一代的 children 欄位找出子代
  SELECT
    child.id,
    parent.generation + 1,
    parent.visited || child.id
  FROM gen_tree parent
  JOIN biblical_people parent_row ON parent_row.id = parent.id
  CROSS JOIN LATERAL (
    SELECT trim(c) AS child_name
    FROM regexp_split_to_table(
      COALESCE(parent_row.children, ''),
      '[,，、]'
    ) AS c
    WHERE trim(c) <> ''
  ) split
  JOIN biblical_people child ON child.name_zh = split.child_name
  WHERE child.id <> ALL(parent.visited)   -- 防迴圈

)
-- 若某人出現在多個父母的 children 中，取最小代數
UPDATE biblical_people
SET generation = agg.min_gen
FROM (
  SELECT id, MIN(generation) AS min_gen
  FROM gen_tree
  GROUP BY id
) agg
WHERE biblical_people.id = agg.id;

-- 步驟五：配偶若無代數，以配偶之代數填補
--   （配偶通常不出現在任何人的 children 欄位，這步補齊撒拉、利百加等人）
UPDATE biblical_people main
SET generation = spouse_gen.gen
FROM (
  SELECT
    p.id,
    MIN(s.generation) AS gen
  FROM biblical_people p
  CROSS JOIN LATERAL (
    SELECT trim(c) AS sp_name
    FROM regexp_split_to_table(COALESCE(p.spouse, ''), '[,，、]') AS c
    WHERE trim(c) <> ''
  ) split
  JOIN biblical_people s ON s.name_zh = split.sp_name
  WHERE p.generation IS NULL
    AND s.generation IS NOT NULL
  GROUP BY p.id
) spouse_gen
WHERE main.id = spouse_gen.id;
