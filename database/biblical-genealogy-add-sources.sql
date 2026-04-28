-- 新增出處欄位（已建立 biblical_people table 後執行此 migration）
ALTER TABLE biblical_people ADD COLUMN IF NOT EXISTS sources text;
