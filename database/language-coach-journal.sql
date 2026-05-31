-- 教練每日日誌：每天一篇教練視角的學習紀錄 + 方向建議（顯示在日曆）
create table if not exists public.lang_journal (
  user_id      uuid not null references auth.users(id) on delete cascade,
  language     text not null,
  journal_date date not null,
  summary      text,                          -- 今天做了什麼（教練語氣，繁中）
  direction    text,                          -- 接下來該往哪走的一句建議
  minutes      numeric(7,2) default 0,        -- 當天總時間（快照）
  generated_at timestamptz default now(),
  primary key (user_id, language, journal_date)
);
alter table public.lang_journal enable row level security;
drop policy if exists own_all_lang_journal on public.lang_journal;
create policy own_all_lang_journal on public.lang_journal
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
