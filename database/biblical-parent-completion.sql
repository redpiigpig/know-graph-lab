-- ================================================================
-- 從名稱括號（X之子）/（X之女）反向補全缺漏的父母
-- 若 DB 中找不到 X，則自動插入 X
-- ================================================================

DO $$
DECLARE
  rec        RECORD;
  phint      TEXT;
  parent_id  UUID;
  new_gen    INT;
  cnt        INT := 0;
  max_so     INT;
BEGIN
  -- 取得目前最大 sort_order，讓新插入的人排在最後
  SELECT COALESCE(MAX(sort_order), 90000) INTO max_so FROM biblical_people;

  FOR rec IN
    SELECT id, name_zh, generation, sort_order
    FROM biblical_people
    WHERE name_zh ~ '（.+之[子女]）$'
    ORDER BY COALESCE(generation, 999), COALESCE(sort_order, 99999)
  LOOP
    -- 擷取父/母名稱，例：「謝拉」from「（謝拉之子）」
    phint := regexp_replace(rec.name_zh, '^.+（(.+)之[子女]）$', '\1');

    -- 若父母已存在（完全比對或前綴比對），跳過
    SELECT id INTO parent_id
    FROM biblical_people
    WHERE name_zh = phint OR name_zh LIKE phint || '（%'
    ORDER BY CASE WHEN name_zh = phint THEN 0 ELSE 1 END
    LIMIT 1;

    CONTINUE WHEN parent_id IS NOT NULL;

    -- 估算父母世代 = 子女世代 - 1（若子女世代為 NULL 則不設定）
    new_gen := CASE
      WHEN rec.generation IS NOT NULL THEN GREATEST(1, rec.generation - 1)
      ELSE NULL
    END;

    max_so := max_so + 1;

    INSERT INTO biblical_people (name_zh, generation, sort_order, notes)
    VALUES (
      phint,
      new_gen,
      max_so,
      '自動補全：由「' || rec.name_zh || '」名稱推斷其父母'
    );

    cnt := cnt + 1;
    RAISE NOTICE '已新增：% （第 % 代）', phint, new_gen;
  END LOOP;

  RAISE NOTICE '=== 共新增 % 位缺漏父母 ===', cnt;
END $$;
