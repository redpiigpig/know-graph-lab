-- Tags：跨類別、跨書本的網狀組織
-- 執行：Supabase Dashboard > SQL Editor

-- ============================================================
-- tags：所有 tag 的集合（全域共用，單人系統）
-- ============================================================
CREATE TABLE IF NOT EXISTS tags (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL UNIQUE,
  color      TEXT,                          -- 選填，用於 UI 顯示（hex 或 tailwind palette key）
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tags_name_lower ON tags (LOWER(name));

-- ============================================================
-- 三個 junction table — books / excerpts 各自帶 tag
-- ebooks 暫不開（書 = 學術單位；ebook 只是檔案）
-- ============================================================
CREATE TABLE IF NOT EXISTS book_tags (
  book_id UUID NOT NULL REFERENCES books(id)    ON DELETE CASCADE,
  tag_id  UUID NOT NULL REFERENCES tags(id)     ON DELETE CASCADE,
  PRIMARY KEY (book_id, tag_id)
);
CREATE INDEX IF NOT EXISTS idx_book_tags_tag ON book_tags(tag_id);

CREATE TABLE IF NOT EXISTS excerpt_tags (
  excerpt_id UUID NOT NULL REFERENCES excerpts(id) ON DELETE CASCADE,
  tag_id     UUID NOT NULL REFERENCES tags(id)     ON DELETE CASCADE,
  PRIMARY KEY (excerpt_id, tag_id)
);
CREATE INDEX IF NOT EXISTS idx_excerpt_tags_tag ON excerpt_tags(tag_id);
