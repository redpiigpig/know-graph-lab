-- 對話串「每天一頁」reader 用表（dialogues-to-writing skill）
-- 一條 writing_projects 卡片（project_slug）→ 多天，每天一筆 html。
-- 首案 project_slug='krishna-dialogues'（與克里希那對話）。
create table if not exists dialogue_days (
  id          uuid primary key default gen_random_uuid(),
  project_slug text not null,
  day_date    date not null,
  weekday     text,
  day_title   text,
  html        text,
  n_turns     int default 0,
  sort_order  int default 0,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  unique(project_slug, day_date)
);
create index if not exists dialogue_days_slug_date_idx on dialogue_days(project_slug, day_date);
