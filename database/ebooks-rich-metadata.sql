-- 為 ebooks 加上 standardize 抽取出來的書目元資料欄位
-- 執行：Supabase Dashboard > SQL Editor

ALTER TABLE ebooks
  ADD COLUMN IF NOT EXISTS subtitle              text,
  ADD COLUMN IF NOT EXISTS original_title        text,
  ADD COLUMN IF NOT EXISTS original_author       text,
  ADD COLUMN IF NOT EXISTS author_en             text,
  ADD COLUMN IF NOT EXISTS translator            text,
  ADD COLUMN IF NOT EXISTS original_publish_year integer;

-- 沒有對應 books.publish_year 的 ebooks 欄位 → ebooks 已有 publication_year，
-- 用同名映射即可（annotations.post.ts 會 publication_year → books.publish_year）。
