-- ============================================================================
-- 研究回顧：補上「可引用」所需的定位欄位（2026-09-09）
--
-- 為什麼要有這一支：lit_review 這條管線的用途就是把期刊論文全文抓下來逐段中譯，
-- 供論文寫作引用——結果 schema 裡連一個頁碼欄位都沒有。**期刊論文沒有卷期頁碼
-- 就不能引**。這是設計時就漏掉的，不是資料沒填。
-- 見 [[feedback_transcribe_page_numbers]]。
--
-- 兩層都要：
--   書目層  引整篇文章：刊名（venue，已有）＋卷＋期＋起訖頁
--   段落層  引某一句話：該段落在原刊的頁碼（只有 PDF 來源有，HTML 來源留 NULL）
--
-- 跑法：Supabase Management API（見 [[reference_supabase_management_api]]），
--       psycopg2 直連是 IPv6-only 跑不通的。
-- ============================================================================

-- ── 書目層 ──────────────────────────────────────────────────────────────────
ALTER TABLE lit_review_entries
  ADD COLUMN IF NOT EXISTS volume TEXT,   -- 卷（'43' / '第五輯'；用 TEXT 因為有非數字寫法）
  ADD COLUMN IF NOT EXISTS issue  TEXT,   -- 期／號（'1' / '25' / '3-4' 合刊）
  ADD COLUMN IF NOT EXISTS pages  TEXT;   -- 起訖頁（'45-72' / '288-291' / 'e12345'）

COMMENT ON COLUMN lit_review_entries.volume IS '卷。引期刊論文的必要欄位之一';
COMMENT ON COLUMN lit_review_entries.issue  IS '期／號';
COMMENT ON COLUMN lit_review_entries.pages  IS '起訖頁。TEXT 而非 INT，因為有 45-72、288-291、e12345 等寫法';

-- ── 段落層 ──────────────────────────────────────────────────────────────────
ALTER TABLE lit_review_sections
  ADD COLUMN IF NOT EXISTS page_number INT;   -- 該段所在的原刊印刷頁

COMMENT ON COLUMN lit_review_sections.page_number IS
  '該段落在原刊的印刷頁。🚨 只能填真頁碼；沒有（HTML 來源）就留 NULL，絕不可用段序頂替';
