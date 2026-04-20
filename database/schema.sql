-- ============================================================
-- Know Graph Lab - 書摘管理系統 Schema
-- 在 Supabase SQL Editor 執行此檔案
-- ============================================================

-- 書籍
create table if not exists books (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  author text not null,
  translator text,          -- 譯者（選填）
  publish_place text,       -- 出版地，例如「臺北」
  publisher text,           -- 出版社，例如「聯經」
  publish_year int,         -- 出版年份，例如 2021
  edition text,             -- 版次，例如「第二版」（選填）
  created_at timestamptz default now()
);

-- 書摘分類（待寫著作 / 待寫文章 / 書摘）
-- 注意：不使用 "projects" 以避免與圖表功能的 projects 表衝突
create table if not exists book_projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type text not null check (type in ('待寫著作', '待寫文章', '書摘')),
  description text,
  created_at timestamptz default now()
);

-- 摘文
create table if not exists excerpts (
  id uuid primary key default gen_random_uuid(),
  title text,
  content text not null,
  book_id uuid references books(id) on delete set null,
  chapter text,
  page_number text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 多對多：摘文 ↔ 書摘分類
create table if not exists excerpt_book_projects (
  excerpt_id uuid references excerpts(id) on delete cascade,
  book_project_id uuid references book_projects(id) on delete cascade,
  primary key (excerpt_id, book_project_id)
);

-- 全文搜尋索引（加速 content / title 搜尋）
create index if not exists excerpts_content_idx on excerpts using gin(to_tsvector('simple', coalesce(content, '')));
create index if not exists excerpts_title_idx on excerpts using gin(to_tsvector('simple', coalesce(title, '')));

-- 預設建立三種書摘分類
insert into book_projects (name, type, description) values
  ('書摘收藏', '書摘', '純粹收集書中值得記錄的段落'),
  ('待寫文章素材', '待寫文章', '未來寫文章時可以引用的摘文'),
  ('待寫著作素材', '待寫著作', '未來寫書時可以引用的摘文')
on conflict do nothing;
