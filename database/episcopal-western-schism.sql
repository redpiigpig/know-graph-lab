-- ============================================================
-- 西方教會大分裂（1378-1417）對立教宗整理
-- ============================================================
-- 1) 去重：每位亞威農/比薩對立教宗原本有兩筆 record（一筆無編號「對立教宗XXX」、
--    一筆有編號「XXX（對立）」）。刪掉無編號的重複筆。
-- 2) 連續編號（對等分裂、繼續往下算，而非從 1 重來）：
--    額我略十一世 #199 死後，羅馬主線與亞威農線「對等」分出，編號平行往下算：
--      羅馬主線：烏爾班六世 #200 → 博尼法九世 #201 → 依諾增爵七世 #202 → 額我略十二世 #203 → 瑪爾定五世 #204
--      亞威農線：克勉七世 #200 → 本篤十三世 #201 → 克勉八世 #202 → 本篤十四世 #203
--      比薩線（1409 第三支）：亞歷山大五世 #203 → 若望二十三世 #204
-- 3) 分叉點（端點 splitMode）：對立支線一律錨在「分裂前最後一位未爭議在位者」
--    （strict start_year < split_year）——亞威農 1378 → 額我略十一世 #199（非同年上任的烏爾班六世），
--    比薩 1409 → 額我略十二世 #203。兩三支由共同祖先對等分出，末端紅虛線匯流回瑪爾定五世主軸。
--
-- 執行：Supabase Management API（2026-06-03 套用至 production）。
-- ============================================================

-- 1) 去重（刪 3 筆無編號重複）
DELETE FROM episcopal_succession
WHERE see = '羅馬' AND succession_number IS NULL AND status = '對立'
  AND name_zh IN ('對立教宗克肋孟七世', '對立教宗本篤十三世', '對立教宗若望二十三世');

-- 2) 亞威農線連續編號 200-203
UPDATE episcopal_succession SET succession_number = 200, status = '對立' WHERE name_zh = '克勉七世（對立）'   AND church = '對立教宗（亞威農）';
UPDATE episcopal_succession SET succession_number = 201, status = '對立' WHERE name_zh = '本篤十三世（對立）' AND church = '對立教宗（亞威農）';
UPDATE episcopal_succession SET succession_number = 202, status = '對立' WHERE name_zh = '克勉八世（對立）'   AND church = '對立教宗（亞威農）';
UPDATE episcopal_succession SET succession_number = 203, status = '對立' WHERE name_zh = '本篤十四世（對立）' AND church = '對立教宗（亞威農）';

-- 3) 比薩線（第三支）連續編號 203-204
UPDATE episcopal_succession SET succession_number = 203, status = '對立' WHERE name_zh = '亞歷山大五世（對立）' AND church = '對立教宗（比薩）';
UPDATE episcopal_succession SET succession_number = 204, status = '對立' WHERE name_zh = '若望二十三世（對立）' AND church = '對立教宗（比薩）';
