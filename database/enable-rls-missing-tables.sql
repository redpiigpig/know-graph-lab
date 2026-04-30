-- ============================================================
-- 為 schema.sql 和 add-journal-articles.sql 的表格啟用 RLS
-- 在 Supabase SQL Editor 執行此檔案
-- 注意：server 使用 service_role key，不受 RLS 影響
-- ============================================================

-- book_categories
alter table book_categories enable row level security;
create policy "book_categories_select" on book_categories
  for select using (auth.role() = 'authenticated');
create policy "book_categories_all" on book_categories
  for all using (auth.role() = 'authenticated');

-- books
alter table books enable row level security;
create policy "books_select" on books
  for select using (auth.role() = 'authenticated');
create policy "books_all" on books
  for all using (auth.role() = 'authenticated');

-- book_projects
alter table book_projects enable row level security;
create policy "book_projects_select" on book_projects
  for select using (auth.role() = 'authenticated');
create policy "book_projects_all" on book_projects
  for all using (auth.role() = 'authenticated');

-- excerpts
alter table excerpts enable row level security;
create policy "excerpts_select" on excerpts
  for select using (auth.role() = 'authenticated');
create policy "excerpts_all" on excerpts
  for all using (auth.role() = 'authenticated');

-- excerpt_book_projects
alter table excerpt_book_projects enable row level security;
create policy "excerpt_book_projects_select" on excerpt_book_projects
  for select using (auth.role() = 'authenticated');
create policy "excerpt_book_projects_all" on excerpt_book_projects
  for all using (auth.role() = 'authenticated');

-- journal_articles
alter table journal_articles enable row level security;
create policy "journal_articles_select" on journal_articles
  for select using (auth.role() = 'authenticated');
create policy "journal_articles_all" on journal_articles
  for all using (auth.role() = 'authenticated');
