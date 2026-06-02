-- ============================================================
-- 聖依玻里圖（Hippolytus）改建為對立教宗支線（短暫分裂 → 回歸）
-- ============================================================
-- 原本依玻里圖以 church='未分裂教會'（羅馬主線）+ succession_number=NULL 直接插在羅馬主軸上，
-- 不被當成對立教宗。他其實是教會史上第一位對立教宗（217-235，反對加里斯都一世），
-- 235 年與正統教宗彭謙一同流放並和好歸回、殉道——典型的短暫分裂。
--
-- 改成：建一個 '對立教宗（依玻里圖）' 分支座（同 see_zh 羅馬、split_year 217 → is_split），
-- 把依玻里圖的主教 record 移進該 church。端點即把他分叉於加里斯都一世（217），
-- 並由「對立教宗匯流線」邏輯在 235 年併回羅馬主軸。
--
-- ⚠ 同時需端點修正（episcopal-graph.get.ts）：旁支主教蒐集的 fallback 不可吞併
--   SPINE_PRIMARY_CHURCHES（未分裂教會/天主教/東正教…）的主教，否則 split_year=217 太早，
--   會把整條教宗主線都吸進依玻里圖支線。已加 SPINE_PRIMARY_CHURCHES 排除。
--
-- 執行：Supabase Management API（2026-06-03 套用至 production）。
-- ============================================================

INSERT INTO episcopal_sees
  (see_zh, name_zh, name_en, church, tradition, founded_year, split_year, parent_see_id, status, notes)
VALUES
  ('羅馬', '羅馬（對立教宗 依玻里圖）', 'Rome (Antipope Hippolytus)', '對立教宗（依玻里圖）', '羅馬公教',
   217, 217,
   '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',  -- 羅馬 spine see id（與亞威農/比薩對立教宗支線同 parent）
   '已廢除',
   '教會史上第一位對立教宗（217-235），反對加里斯都一世；235 年與正統教宗彭謙一同流放薩丁尼亞並和好歸回，殉道後受尊為聖人——短暫分裂、裂痕癒合的典型。')
ON CONFLICT (see_zh, church) DO NOTHING;

UPDATE episcopal_succession
SET church = '對立教宗（依玻里圖）'
WHERE name_zh = '聖依玻里圖' AND see = '羅馬';
