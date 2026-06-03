-- ============================================================
-- 宗主教座「升格 / 撤銷」期間 → 線條粗細隨之變化
-- ============================================================
-- 7 大主軸 spine 用 SPINE_DEFS.patriarchateYear（某年「之後」一律變粗，單向）。
-- 但旁支教座（branch）也可能「中途升為宗主教座、後來又被撤銷」——例如阿奎萊亞
-- （Aquileia）：6 世紀（三章爭議時）主教自稱宗主教，1751 年本篤十四世撤銷宗主教座，
-- 分割為烏迪內（Udine）與戈里齊亞（Gorizia）兩總教區。
--
-- 為支援「升格→變粗、撤銷→再變細」的區間粗細，episcopal_sees 新增兩欄：
--   patriarchate_start_year / patriarchate_end_year
-- 渲染端（EpiscopalSpineTree）對該支主教鏈：start_year 落在 [start, end] 區間的段加粗(6)，
-- 區間外維持細(2)。end 為 NULL 表示至今仍是宗主教座。
--
-- 執行：Supabase Management API（2026-06-03 套用至 production）。
-- ============================================================

ALTER TABLE episcopal_sees
  ADD COLUMN IF NOT EXISTS patriarchate_start_year int,
  ADD COLUMN IF NOT EXISTS patriarchate_end_year   int;

-- 阿奎萊亞宗主教座 557–1751（之後撤銷）
UPDATE episcopal_sees
SET patriarchate_start_year = 557, patriarchate_end_year = 1751
WHERE see_zh = '阿奎萊亞';

-- TODO（教座合併 / 撤銷後繼座，待補資料）：
--   阿奎萊亞 1751 撤銷後分為「烏迪內」「戈里齊亞」兩總教區，目前 DB 尚無此兩座。
--   若要在圖上顯示「合併/分割繼承」，需新增此二 see（parent 接阿奎萊亞末任主教或羅馬），
--   並比照需求決定是否畫匯流/分流線。
