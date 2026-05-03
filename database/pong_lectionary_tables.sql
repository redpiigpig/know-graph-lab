-- 三讀三禱 (Daily Office) 資料表
-- 請在 Supabase Dashboard → SQL Editor 執行此檔案

CREATE TABLE IF NOT EXISTS pong_lectionary_weeks (
  id SERIAL PRIMARY KEY,
  lectionary_year CHAR(1) NOT NULL CHECK (lectionary_year IN ('A','B','C')),
  season VARCHAR(20) NOT NULL,
  week_num SMALLINT NOT NULL,
  title VARCHAR(100),
  date_range VARCHAR(50),
  intro_letter TEXT,
  theme_essay_title VARCHAR(200),
  theme_essay TEXT,
  appendices JSONB DEFAULT '[]',
  discussion_guide JSONB DEFAULT '[]',
  is_published BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (lectionary_year, season, week_num)
);

CREATE TABLE IF NOT EXISTS pong_lectionary_days (
  id SERIAL PRIMARY KEY,
  week_id INTEGER REFERENCES pong_lectionary_weeks(id) ON DELETE CASCADE,
  day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sun, 1=Mon, ..., 6=Sat
  day_label VARCHAR(30),
  readings JSONB NOT NULL DEFAULT '[]',
  -- readings 格式：[{ book, passage, title, text, meditation, key_verse }]
  UNIQUE (week_id, day_of_week)
);

-- RLS
ALTER TABLE pong_lectionary_weeks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_lectionary_days ENABLE ROW LEVEL SECURITY;

-- 公開可讀（已發布）
CREATE POLICY "public read published weeks"
  ON pong_lectionary_weeks FOR SELECT
  USING (is_published = true);

CREATE POLICY "public read days of published weeks"
  ON pong_lectionary_days FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM pong_lectionary_weeks w
      WHERE w.id = pong_lectionary_days.week_id AND w.is_published = true
    )
  );

-- 確認建立成功
SELECT 'pong_lectionary_weeks' AS table_name, COUNT(*) FROM pong_lectionary_weeks
UNION ALL
SELECT 'pong_lectionary_days', COUNT(*) FROM pong_lectionary_days;
