-- 寫作計畫系統
-- 執行方式：在 Supabase Dashboard > SQL Editor 貼上執行

-- 寫作計畫總表
CREATE TABLE IF NOT EXISTS writing_projects (
  id          UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
  slug        TEXT    UNIQUE NOT NULL,
  title       TEXT    NOT NULL,
  description TEXT,
  emoji       TEXT    DEFAULT '📝',
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 影音逐字稿（千面上帝宗教史讀書會等）
CREATE TABLE IF NOT EXISTS video_transcripts (
  id           UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
  project_slug TEXT    NOT NULL REFERENCES writing_projects(slug) ON DELETE CASCADE,
  episode      INTEGER NOT NULL,
  title        TEXT    NOT NULL,
  content      TEXT    NOT NULL,
  video_date   TEXT,
  youtube_id   TEXT,
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE(project_slug, episode)
);

-- 啟用 RLS
ALTER TABLE writing_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcripts ENABLE ROW LEVEL SECURITY;

-- 讀取公開（登入用戶可讀）
CREATE POLICY "authenticated read writing_projects"
  ON writing_projects FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated read video_transcripts"
  ON video_transcripts FOR SELECT TO authenticated USING (true);

-- 寫入限 service_role（由後端腳本負責）
CREATE POLICY "service insert writing_projects"
  ON writing_projects FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "service insert video_transcripts"
  ON video_transcripts FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "service update video_transcripts"
  ON video_transcripts FOR UPDATE TO service_role USING (true);

-- 預先插入千面上帝計畫
INSERT INTO writing_projects (slug, title, description, emoji)
VALUES (
  'qiangmian',
  '千面上帝',
  '探討世界宗教中神明概念的多元面貌，橫跨印度教、佛教、基督宗教、伊斯蘭教等傳統',
  '🌐'
) ON CONFLICT (slug) DO NOTHING;
