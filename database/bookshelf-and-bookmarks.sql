-- 書櫃 + 閱讀進度書籤
-- 執行方式：在 Supabase Dashboard > SQL Editor 貼上執行

-- ============================================================
-- 1. user_reading_status — 一人一書一筆，記錄閱讀中 / 已讀過
-- ============================================================
CREATE TABLE IF NOT EXISTS user_reading_status (
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  ebook_id   UUID NOT NULL REFERENCES ebooks(id)     ON DELETE CASCADE,
  status     TEXT NOT NULL CHECK (status IN ('reading', 'read')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, ebook_id)
);

CREATE INDEX IF NOT EXISTS idx_user_reading_status_user_updated
  ON user_reading_status (user_id, updated_at DESC);

-- ============================================================
-- 2. reading_bookmarks — 「📅 今日讀到這裡」標記，可多筆
-- ============================================================
CREATE TABLE IF NOT EXISTS reading_bookmarks (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  ebook_id    UUID NOT NULL REFERENCES ebooks(id)     ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reading_bookmarks_user_book_created
  ON reading_bookmarks (user_id, ebook_id, created_at DESC);

-- ============================================================
-- RLS — 只允許登入者操作自己的列；server-side service_role 跳過 RLS
-- ============================================================
ALTER TABLE user_reading_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading_bookmarks   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own status read"   ON user_reading_status
  FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "own status write"  ON user_reading_status
  FOR ALL    TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "own bookmarks read"  ON reading_bookmarks
  FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "own bookmarks write" ON reading_bookmarks
  FOR ALL    TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
