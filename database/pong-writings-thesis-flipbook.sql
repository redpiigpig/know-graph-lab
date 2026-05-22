-- ═══════════════════════════════════════════════════════════════════════════
-- pong_writings — 學位論文翻頁電子書欄位
-- 建立時間：2026-05-22
-- 說明：把龐牧師的 BD / MTh 論文做成翻頁電子書 reader
--      PDF + 結構化 OCR JSONL 都存 R2，DB 只記 key
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE pong_writings
  ADD COLUMN IF NOT EXISTS pdf_r2_key   TEXT,     -- R2 key, e.g. 'pong-writings/12.pdf'
  ADD COLUMN IF NOT EXISTS pages_r2_key TEXT,     -- R2 key, e.g. 'pong-writings-pages/12.jsonl.gz'
  ADD COLUMN IF NOT EXISTS outline      JSONB DEFAULT '[]'::jsonb,
                                                  -- [{level, text, page}] 自動從 OCR 抽出的章節目錄
  ADD COLUMN IF NOT EXISTS total_pages  INTEGER;  -- PDF 總頁數

COMMENT ON COLUMN pong_writings.pdf_r2_key   IS 'R2 key for original PDF (served via /api/pong-writing/{id}/pdf)';
COMMENT ON COLUMN pong_writings.pages_r2_key IS 'R2 key for structured pages JSONL (one line per page, blocks array)';
COMMENT ON COLUMN pong_writings.outline      IS '[{level:1-4, text, page}] auto-extracted章節目錄';
COMMENT ON COLUMN pong_writings.total_pages  IS 'PDF total page count, mirrors len(JSONL)';

CREATE INDEX IF NOT EXISTS idx_pong_writings_has_pdf
  ON pong_writings ((pdf_r2_key IS NOT NULL));
