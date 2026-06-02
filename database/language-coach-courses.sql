-- 主題教程：可選/自建的主題課程（宗教文獻閱讀、學術寫作、TOEFL口說…），
-- 每門課一套循序課表，每課含預估時間，逐課懶生成內容。
create table if not exists public.lang_courses (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  language   text not null,
  title      text not null,
  theme      text,
  level      text,
  syllabus   jsonb default '[]'::jsonb,  -- [{ id, title, summary, minutes, content(jsonb|null), done(bool) }]
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index if not exists idx_lang_courses_user on public.lang_courses(user_id, language, created_at desc);
alter table public.lang_courses enable row level security;
drop policy if exists own_all_lang_courses on public.lang_courses;
create policy own_all_lang_courses on public.lang_courses
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
