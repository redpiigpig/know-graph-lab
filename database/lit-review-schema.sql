-- ============================================================================
-- 研究回顧 / 文獻綜述 (Literature Review) — schema for the /works 論文計畫
--   lit_review_entries  — 一筆書目（作者/年/題/刊/語言/所屬面向/立場/摘要/連結）
--   lit_review_sections — 開放取用外文文獻的全文，原文(orig)↔中譯(zh) 逐段對齊
-- Mirrors gnostic_{documents,sections}. orig↔zh align by order_index.
-- 綁在 writing_projects(slug) 底下（kind='paper' 的論文計畫）。
-- 跑法：Supabase Management API（見 reference_supabase_management_api.md）
-- ============================================================================

CREATE TABLE IF NOT EXISTS lit_review_entries (
  id              BIGSERIAL PRIMARY KEY,
  project_slug    TEXT NOT NULL REFERENCES writing_projects (slug) ON DELETE CASCADE ON UPDATE CASCADE,
  book_id         TEXT NOT NULL DEFAULT '',   -- per-volume scope within a 叢書 project（創生哲學 卷 'M1'…）；'' for normal projects
  ref_key         TEXT NOT NULL,              -- make_ref_key()：'analayo-2016-the-foundation-history'
  authors         TEXT NOT NULL DEFAULT '',
  year            INT,
  title           TEXT NOT NULL,
  venue           TEXT,                        -- 刊名 / 出版社
  language        TEXT,                        -- 'en' / 'zh' / 'de' / …（detect_language）
  theme           TEXT,                        -- 4 大脈絡之一（report `#` 主題標題）
  dimension       TEXT,                        -- 所屬面向（文本考證 / 詮釋爭論 …）
  stance          TEXT,                        -- 立場（可空）
  abstract_zh     TEXT,                        -- 摘要（繁中）
  fulltext_url    TEXT,
  fulltext_status TEXT NOT NULL DEFAULT 'pending',  -- pending / fetched / translated / unavailable
  display_order   INT NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT lit_review_entries_project_book_ref_key UNIQUE (project_slug, book_id, ref_key)
);
CREATE INDEX IF NOT EXISTS lit_review_entries_project ON lit_review_entries (project_slug, display_order);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS lit_review_sections (
  id            BIGSERIAL PRIMARY KEY,
  entry_id      BIGINT NOT NULL REFERENCES lit_review_entries (id) ON DELETE CASCADE,
  version_code  TEXT NOT NULL,                 -- 'orig'（原文）/ 'zh'（逐段中譯）
  order_index   INT NOT NULL,                  -- 原文↔中譯 對齊鍵（同 order_index = 對照同一段）
  text          TEXT NOT NULL,
  char_count    INT,
  UNIQUE (entry_id, version_code, order_index)
);
CREATE INDEX IF NOT EXISTS lit_review_sections_entry_ver
  ON lit_review_sections (entry_id, version_code, order_index);

-- ----------------------------------------------------------------------------
-- RLS: public read（書目 + 全文都公開；寫入限 service_role）

ALTER TABLE lit_review_entries  ENABLE ROW LEVEL SECURITY;
ALTER TABLE lit_review_sections ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "lit_review_entries_read"  ON lit_review_entries;
DROP POLICY IF EXISTS "lit_review_sections_read" ON lit_review_sections;
CREATE POLICY "lit_review_entries_read"  ON lit_review_entries  FOR SELECT USING (true);
CREATE POLICY "lit_review_sections_read" ON lit_review_sections FOR SELECT USING (true);

DROP POLICY IF EXISTS "lit_review_entries_write"  ON lit_review_entries;
DROP POLICY IF EXISTS "lit_review_sections_write" ON lit_review_sections;
CREATE POLICY "lit_review_entries_write"  ON lit_review_entries  FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "lit_review_sections_write" ON lit_review_sections FOR ALL TO service_role USING (true) WITH CHECK (true);
