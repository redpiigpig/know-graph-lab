-- ============================================================================
-- Happy English（國小英語教學網站）資料表
-- 學習時間追蹤 + 測驗分數。內容（課程/單字/課文/題目）走 public/content 靜態 JSON，
-- 故此處只存「使用者進度」。所有存取一律經 server/api/english/*（service role），
-- 因此啟用 RLS 但不開放 client 直連。
-- ============================================================================

-- 每段學習時間紀錄（一天可多筆）
CREATE TABLE IF NOT EXISTS english_activity (
  id            bigserial PRIMARY KEY,
  user_id       uuid NOT NULL,
  activity_date date NOT NULL,
  minutes       numeric NOT NULL DEFAULT 0,
  source        text,                       -- lesson / quiz:vocab / quiz:listening ...
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_english_activity_user_date
  ON english_activity (user_id, activity_date);

-- 每位使用者的累計進度（streak / 總分鐘 / 最後活躍）
CREATE TABLE IF NOT EXISTS english_progress (
  user_id       uuid PRIMARY KEY,
  total_minutes numeric NOT NULL DEFAULT 0,
  streak_days   int NOT NULL DEFAULT 0,
  last_active   date,
  updated_at    timestamptz NOT NULL DEFAULT now()
);

-- 測驗分數（可重複測驗 → 保留每次紀錄）
CREATE TABLE IF NOT EXISTS english_scores (
  id         bigserial PRIMARY KEY,
  user_id    uuid NOT NULL,
  lesson_no  int NOT NULL,
  quiz_type  text NOT NULL,                 -- vocab / listening / speaking / sentence / comprehensive
  score      int NOT NULL,
  total      int NOT NULL,
  taken_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_english_scores_user_lesson
  ON english_scores (user_id, lesson_no, quiz_type);

ALTER TABLE english_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE english_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE english_scores   ENABLE ROW LEVEL SECURITY;
