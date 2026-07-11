-- v4: kind 新增 'lecture'（講義寫作）——大學課程講義/教科書類計畫，與專書(book)、論文(paper)並列
ALTER TABLE writing_projects DROP CONSTRAINT IF EXISTS writing_projects_kind_check;
ALTER TABLE writing_projects ADD CONSTRAINT writing_projects_kind_check CHECK (kind IN ('book', 'paper', 'lecture'));
