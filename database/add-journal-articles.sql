-- 期刊／論文篇目（書摘圖書館以外的「期刊書摘」來源）
create table if not exists journal_articles (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  venue text,
  author text,
  publish_year int,
  issue_label text,
  created_at timestamptz default now()
);

alter table excerpts
  add column if not exists journal_article_id uuid references journal_articles(id) on delete set null;

create index if not exists excerpts_journal_article_id_idx on excerpts(journal_article_id);
