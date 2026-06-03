-- writing_projects v3: 把「寫作計畫」分成 書籍寫作 / 論文寫作 兩區
--   kind      = 'book'（預設，原有計畫都是書）/ 'paper'（論文寫作）
--   paper_ref = 連到 /papers 的 id（如 'c1'），標記這個 paper 計畫是哪篇研討會/期刊論文
-- 跑法：Supabase Management API（見 reference_supabase_management_api.md）

BEGIN;

ALTER TABLE writing_projects
  ADD COLUMN IF NOT EXISTS kind      TEXT NOT NULL DEFAULT 'book',
  ADD COLUMN IF NOT EXISTS paper_ref TEXT;

-- kind 只允許 book / paper
ALTER TABLE writing_projects
  DROP CONSTRAINT IF EXISTS writing_projects_kind_check;
ALTER TABLE writing_projects
  ADD CONSTRAINT writing_projects_kind_check CHECK (kind IN ('book', 'paper'));

-- 既有計畫（千面上帝等）維持 book
UPDATE writing_projects SET kind = 'book' WHERE kind IS NULL;

COMMIT;
