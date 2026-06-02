-- 每日計畫：每人每語言每天一份（推薦閱讀/聽力/口說 + 任務），生成一次快取
create table if not exists public.lang_daily (
  user_id    uuid not null references auth.users(id) on delete cascade,
  language   text not null,
  plan_date  date not null,
  plan       jsonb default '{}'::jsonb,   -- { tasks:[{id,label,done}], reading:[{id,topic,content,session_id,done}], listening:[...], speaking:[{id,prompt,done}] }
  created_at timestamptz default now(),
  primary key (user_id, language, plan_date)
);
alter table public.lang_daily enable row level security;
drop policy if exists own_all_lang_daily on public.lang_daily;
create policy own_all_lang_daily on public.lang_daily
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
