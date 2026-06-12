-- ============================================================================
-- ACCS patristic-commentary layer for the /scripture reader
--   accs_commentary — 古代基督信仰聖經註釋叢書 (Ancient Christian Commentary on
--   Scripture) 逐「段落（pericope）」教父註釋。掛在 bible_books / bible_verses
--   旁邊：經文逐節對照不動，註釋以 verse_start..verse_end 對齊到段落。
--
-- ACCS 體例 = catena：每個經文段落先一段「總論（overview，編者導語）」，
-- 再一串「教父引文（comment）」，每則掛 教父名 + 作品名 + 主題小標。
-- 故一列 = 一個 overview 或一則 comment。
-- 來源：校園書房繁體中文版（auth-gated 個人研究站，與電子書庫同政策）。
-- ============================================================================

CREATE TABLE IF NOT EXISTS accs_commentary (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  book_code       VARCHAR(10) NOT NULL REFERENCES bible_books (code),
  chapter         INT NOT NULL,
  verse_start     INT NOT NULL,            -- 段落涵蓋的起節
  verse_end       INT NOT NULL,            -- 段落涵蓋的迄節（單節時 == verse_start）
  pericope_order  INT NOT NULL,            -- 段落在該章內的排序（依 verse_start）
  entry_order     INT NOT NULL,            -- 該段落內部排序（overview 在前，comments 依書序）
  section_kind    VARCHAR(20) NOT NULL,    -- 'overview' | 'comment'
  heading         TEXT,                    -- ACCS 主題小標（可空；overview 常為段落標題）
  father_name     TEXT,                    -- 教父名（繁中，對齊 theologians 詞庫；overview 為 NULL）
  father_name_en  TEXT,                    -- 教父英文名（可空，給對齊/詞庫 backfill）
  work_title      TEXT,                    -- 作品名（繁中；overview 為 NULL）
  body_zh         TEXT NOT NULL,           -- 繁中正文
  source_vol      VARCHAR(60) NOT NULL,    -- 'ACCS OT I（創 1–11）' 等
  created_at      TIMESTAMPTZ DEFAULT now(),
  -- 同一書/章/段落/內序唯一 → ingest 可冪等 upsert
  UNIQUE (book_code, chapter, verse_start, verse_end, entry_order)
);

CREATE INDEX IF NOT EXISTS accs_commentary_book_chapter
  ON accs_commentary (book_code, chapter);
CREATE INDEX IF NOT EXISTS accs_commentary_pericope
  ON accs_commentary (book_code, chapter, pericope_order, entry_order);
CREATE INDEX IF NOT EXISTS accs_commentary_father
  ON accs_commentary (father_name);

-- 公共讀 / authenticated 寫（對齊 bible_verses）
ALTER TABLE accs_commentary ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "accs_commentary_read"  ON accs_commentary;
DROP POLICY IF EXISTS "accs_commentary_write" ON accs_commentary;

CREATE POLICY "accs_commentary_read"  ON accs_commentary FOR SELECT USING (true);
CREATE POLICY "accs_commentary_write" ON accs_commentary FOR ALL
  USING (auth.role() = 'authenticated') WITH CHECK (auth.role() = 'authenticated');
