-- 系統性文法課程：每「程度」一套循序大綱（英文 B2/C1/C2、日文 N5–N1…）
-- 每人每語言每程度一列；各課內容依需求生成並快取。
drop table if exists public.lang_grammar;
create table public.lang_grammar (
  user_id    uuid not null references auth.users(id) on delete cascade,
  language   text not null,
  level      text not null,                 -- 這套課對應的程度
  syllabus   jsonb default '[]'::jsonb,      -- [{ id, title, summary, content(jsonb|null), done(bool) }]
  updated_at timestamptz default now(),
  primary key (user_id, language, level)
);
alter table public.lang_grammar enable row level security;
drop policy if exists own_all_lang_grammar on public.lang_grammar;
create policy own_all_lang_grammar on public.lang_grammar
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
