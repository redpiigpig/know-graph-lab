-- ============================================================================
-- AI 語言教練 — 支柱 B/C/D/E
-- B: 單字 SM-2 間隔複習欄位 + 學術詞庫參考表
-- C: 考試任務（TOEFL/IELTS/GRE）+ E: 四技能練習任務（共用 lang_tasks）
-- D: 內容沉浸（YouTube / 文章）lang_content
-- ============================================================================

-- ---------------------------------------------------------------------------
-- B1. lang_vocab 加 SM-2 欄位
-- ---------------------------------------------------------------------------
alter table public.lang_vocab add column if not exists ease_factor  numeric(4,2) default 2.5;
alter table public.lang_vocab add column if not exists interval_days int default 0;
alter table public.lang_vocab add column if not exists repetitions   int default 0;
alter table public.lang_vocab add column if not exists last_reviewed date;
alter table public.lang_vocab add column if not exists list_key      text;   -- 來源詞庫（awl1.. / gre / 主題）

-- ---------------------------------------------------------------------------
-- B2. 學術詞庫參考表（共享，非使用者私有；用來「匯入學習」）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_word_lists (
  id        uuid primary key default gen_random_uuid(),
  list_key  text not null,            -- awl1..awl10 / gre / humanities
  language  text not null default 'en',
  word      text not null,
  meaning   text,                     -- 繁中釋義（可後補）
  reading   text,
  example   text,
  sublist   int,
  created_at timestamptz default now(),
  unique (list_key, word)
);
create index if not exists idx_word_lists_key on public.lang_word_lists(list_key, language);

-- ---------------------------------------------------------------------------
-- C+E. 練習/考試任務（聽說讀寫四技能 + 考試題）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_tasks (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  language    text not null,
  mode        text not null default 'practice',   -- practice / exam
  exam        text,                                -- TOEFL / IELTS / GRE / null
  skill       text not null,                       -- listening/speaking/reading/writing
  task_type   text,                                -- 如 toefl_independent_writing / reading_comprehension / monologue
  level       text,                                -- 出題時鎖定的 CEFR
  topic       text,
  prompt      text,                                -- 題目/指示
  materials   jsonb default '{}'::jsonb,           -- { passage, audio_text, questions:[{q,options,answer}], ... }
  response    text,                                -- 使用者作答（文字或語音轉文字）
  scores      jsonb default '{}'::jsonb,           -- rubric 分項 + correct_count 等
  band        numeric(5,1),                         -- 預測分數/級分
  feedback    text,
  status      text default 'generated',            -- generated / answered / scored
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);
create index if not exists idx_lang_tasks_user on public.lang_tasks(user_id, language, created_at desc);

-- ---------------------------------------------------------------------------
-- D. 內容沉浸（YouTube / 文章）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_content (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  language    text not null,
  source_type text not null,                       -- youtube / article
  url         text,
  title       text,
  summary     text,
  analysis    jsonb default '{}'::jsonb,           -- { questions:[], vocab:[], discussion:[], outline:[] }
  session_id  uuid,                                -- 連到 lang_sessions 以便延伸討論
  created_at  timestamptz default now()
);
create index if not exists idx_lang_content_user on public.lang_content(user_id, language, created_at desc);

-- ============================================================================
-- RLS
-- ============================================================================
do $$
declare
  t text;
  tbls text[] := array['lang_tasks','lang_content'];
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

-- 詞庫參考表：任何登入者可讀，僅站長可寫（用 service role 從後端 seed，故只開 read）
alter table public.lang_word_lists enable row level security;
drop policy if exists read_word_lists on public.lang_word_lists;
create policy read_word_lists on public.lang_word_lists
  for select to authenticated using (true);
