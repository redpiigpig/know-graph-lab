-- writing_projects v2: 為「寫作計畫」加上 Notion-like 編輯所需欄位 + 公開讀取
-- 同時把舊 slug 'qiangmian' → 'million-masks'（連動 video_transcripts）
-- 跑法：Supabase Management API（見 reference_supabase_management_api.md）

BEGIN;

-- 1) 新增欄位
ALTER TABLE writing_projects
  ADD COLUMN IF NOT EXISTS subtitle     TEXT,
  ADD COLUMN IF NOT EXISTS color        TEXT        DEFAULT 'amber',
  ADD COLUMN IF NOT EXISTS status       TEXT,
  ADD COLUMN IF NOT EXISTS sort_order   INTEGER     DEFAULT 0,
  ADD COLUMN IF NOT EXISTS content_json JSONB,
  ADD COLUMN IF NOT EXISTS updated_at   TIMESTAMPTZ DEFAULT now();

-- 2) FK 加 ON UPDATE CASCADE，這樣之後改 slug 會自動連動
ALTER TABLE video_transcripts
  DROP CONSTRAINT IF EXISTS video_transcripts_project_slug_fkey;

ALTER TABLE video_transcripts
  ADD CONSTRAINT video_transcripts_project_slug_fkey
  FOREIGN KEY (project_slug)
  REFERENCES writing_projects(slug)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 3) 改 slug + 補新欄位內容
UPDATE writing_projects
SET slug        = 'million-masks',
    subtitle    = 'The Million Masks of God',
    status      = '構思中',
    color       = 'amber',
    sort_order  = 0,
    updated_at  = now()
WHERE slug = 'qiangmian';

-- 4) RLS 政策：開放匿名讀取（取代原本的 authenticated-only）
DROP POLICY IF EXISTS "authenticated read writing_projects"   ON writing_projects;
DROP POLICY IF EXISTS "authenticated read video_transcripts"  ON video_transcripts;

CREATE POLICY "public read writing_projects"
  ON writing_projects FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "public read video_transcripts"
  ON video_transcripts FOR SELECT TO anon, authenticated USING (true);

-- service_role 已經有 INSERT/UPDATE 政策；補 DELETE
DROP POLICY IF EXISTS "service delete writing_projects"  ON writing_projects;
CREATE POLICY "service delete writing_projects"
  ON writing_projects FOR DELETE TO service_role USING (true);

DROP POLICY IF EXISTS "service update writing_projects"  ON writing_projects;
CREATE POLICY "service update writing_projects"
  ON writing_projects FOR UPDATE TO service_role USING (true);

COMMIT;
