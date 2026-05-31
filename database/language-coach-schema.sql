-- ============================================================================
-- AI 語言教練（外語 VTuber）schema
-- 多語言（en/de/fr/la/grc/ja…），每語言一位專屬教練人設、獨立記憶庫、單字庫、作業
-- 比照 enable-rls-public-tables.sql 的 RLS 慣例：authenticated 可全權操作，依 user_id 隔離
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. 每語言學習進度（等級、連續天數）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_progress (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  language     text not null,                 -- en / de / fr / la / grc / ja
  level        text default 'A1',             -- CEFR：A1 A2 B1 B2 C1 C2（古典語可自訂）
  streak_days  int  default 0,
  last_active  date,
  total_minutes int default 0,
  created_at   timestamptz default now(),
  updated_at   timestamptz default now(),
  unique (user_id, language)
);

-- ---------------------------------------------------------------------------
-- 2. 對話 session（記憶隔離：每語言獨立；長期記憶摘要存在這裡，控制 token 成本）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_sessions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  language      text not null,
  title         text,                          -- 課程主題（教練擬定或使用者命名）
  summary       text,                          -- 滾動式長期記憶摘要（舊對話壓縮）
  message_count int default 0,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);
create index if not exists idx_lang_sessions_user_lang on public.lang_sessions(user_id, language, updated_at desc);

-- ---------------------------------------------------------------------------
-- 3. 對話訊息（含改錯 / 新單字 結構化資料，前端直接渲染）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_messages (
  id          uuid primary key default gen_random_uuid(),
  session_id  uuid not null references public.lang_sessions(id) on delete cascade,
  user_id     uuid not null references auth.users(id) on delete cascade,
  role        text not null,                   -- user / coach
  content     text not null,                   -- 對話文字（外語）
  translation text,                            -- 教練回覆的繁中對照（可選）
  corrections jsonb default '[]'::jsonb,        -- [{ original, fixed, note }]
  created_at  timestamptz default now()
);
create index if not exists idx_lang_messages_session on public.lang_messages(session_id, created_at);

-- ---------------------------------------------------------------------------
-- 4. 單字庫（每語言獨立；含 SRS 間隔複習欄位）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_vocab (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  language      text not null,
  word          text not null,
  reading       text,                          -- 假名 / 音標 / 羅馬拼音
  meaning       text not null,                 -- 繁中釋義
  example       text,                          -- 例句（外語）
  part_of_speech text,
  mastery_level int default 0,                 -- 0=新詞 … 5=精熟
  next_review   date default current_date,     -- SRS 下次複習日
  source        text default 'chat',           -- chat / homework / manual
  created_at    timestamptz default now(),
  updated_at    timestamptz default now(),
  unique (user_id, language, word)
);
create index if not exists idx_lang_vocab_user_lang on public.lang_vocab(user_id, language, next_review);

-- ---------------------------------------------------------------------------
-- 5. 作業（教練出題 → 使用者繳交 → 教練批改）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_homework (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  language    text not null,
  topic       text not null,                   -- 主題
  prompt      text not null,                   -- 題目 / 指示
  hw_type     text default 'writing',          -- writing / translation / dialogue / vocab
  submission  text,                            -- 使用者繳交內容
  feedback    text,                            -- 教練批改回饋（繁中＋外語）
  corrections jsonb default '[]'::jsonb,        -- [{ original, fixed, note }]
  score       int,                             -- 0–100（可選）
  status      text default 'assigned',         -- assigned / submitted / graded
  due_date    date,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);
create index if not exists idx_lang_homework_user_lang on public.lang_homework(user_id, language, status);

-- ============================================================================
-- RLS：authenticated 依 user_id 全權操作（單人站，比照既有慣例）
-- ============================================================================
do $$
declare
  t text;
  tbls text[] := array['lang_progress','lang_sessions','lang_messages','lang_vocab','lang_homework'];
begin
  foreach t in array tbls loop
    execute format('alter table public.%I enable row level security', t);

    execute format($f$
      drop policy if exists own_all_%1$s on public.%1$I;
      create policy own_all_%1$s on public.%1$I
        for all to authenticated
        using (user_id = auth.uid())
        with check (user_id = auth.uid());
    $f$, t);
  end loop;
end $$;
