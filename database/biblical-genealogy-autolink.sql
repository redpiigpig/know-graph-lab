-- ================================================================
-- 自動從名稱括號 （X之子）/（X之女） 推斷親子關係
-- 並補齊所有代數
-- ================================================================

-- ── 步驟一：從名稱括號自動連結親子 ────────────────────────────────
-- 例：約巴（謝拉之子）→ 找出 DB 中名稱為「謝拉」或「謝拉（...）」的人
-- 並將此人加入其 children 欄位（不重複加入）

DO $$
DECLARE
  rec        RECORD;
  phint      TEXT;
  parent_id  UUID;
  cur_ch     TEXT;
BEGIN
  FOR rec IN
    SELECT id, name_zh, sort_order
    FROM biblical_people
    WHERE name_zh ~ '（.+之[子女]）$'
  LOOP
    -- 擷取父母名稱，例：「謝拉」from「（謝拉之子）」
    phint := regexp_replace(rec.name_zh, '^.+（(.+)之[子女]）$', '\1');

    -- 優先完全比對，其次前綴比對（父名帶有括號後綴的情況）
    -- 同名多人時，優先選取 sort_order 最接近子代的（通常是同一批次插入的父代）
    SELECT id INTO parent_id
    FROM biblical_people
    WHERE name_zh = phint
       OR name_zh LIKE phint || '（%'
    ORDER BY
      CASE WHEN name_zh = phint THEN 0 ELSE 1 END,
      ABS(sort_order - rec.sort_order) ASC
    LIMIT 1;

    CONTINUE WHEN parent_id IS NULL;
    CONTINUE WHEN parent_id = rec.id;  -- 防止自參照

    SELECT children INTO cur_ch
    FROM biblical_people WHERE id = parent_id;

    IF cur_ch IS NULL OR cur_ch = '' THEN
      UPDATE biblical_people SET children = rec.name_zh WHERE id = parent_id;
    ELSIF position(rec.name_zh IN cur_ch) = 0 THEN
      UPDATE biblical_people SET children = cur_ch || '、' || rec.name_zh WHERE id = parent_id;
    END IF;
  END LOOP;
END $$;

-- ── 步驟二：重算代數（清空後從亞當/夏娃遞迴） ──────────────────────

UPDATE biblical_people SET generation = NULL;

WITH RECURSIVE gen_tree AS (
  SELECT id, 1 AS generation, ARRAY[id] AS visited
  FROM biblical_people
  WHERE name_zh IN ('亞當', '夏娃')

  UNION ALL

  SELECT child.id,
         parent.generation + 1,
         parent.visited || child.id
  FROM gen_tree parent
  JOIN biblical_people parent_row ON parent_row.id = parent.id
  CROSS JOIN LATERAL (
    SELECT trim(c) AS child_name
    FROM regexp_split_to_table(COALESCE(parent_row.children, ''), '[,，、]') AS c
    WHERE trim(c) <> ''
  ) split
  JOIN biblical_people child ON child.name_zh = split.child_name
  WHERE child.id <> ALL(parent.visited)
)
UPDATE biblical_people
SET generation = agg.min_gen
FROM (
  SELECT id, MIN(generation) AS min_gen FROM gen_tree GROUP BY id
) agg
WHERE biblical_people.id = agg.id;

-- ── 步驟三：配偶填補 ────────────────────────────────────────────────
UPDATE biblical_people main
SET generation = spouse_gen.gen
FROM (
  SELECT p.id, MIN(s.generation) AS gen
  FROM biblical_people p
  CROSS JOIN LATERAL (
    SELECT trim(c) AS sp_name
    FROM regexp_split_to_table(COALESCE(p.spouse, ''), '[,，、]') AS c
    WHERE trim(c) <> ''
  ) split
  JOIN biblical_people s ON s.name_zh = split.sp_name
  WHERE p.generation IS NULL AND s.generation IS NOT NULL
  GROUP BY p.id
) spouse_gen
WHERE main.id = spouse_gen.id;

-- ── 步驟四：手動設定西珥族根節點，再向下傳播 ──────────────────────
-- 西珥是以東地原住民族長，與以撒同代（約第 21 代）
UPDATE biblical_people SET generation = 21 WHERE name_zh = '西珥' AND generation IS NULL;

-- 傳播三層（西珥→子→孫→曾孫）
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
