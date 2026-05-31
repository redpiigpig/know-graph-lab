-- ============================================================================
-- AI 語言教練 — 支柱 A：個人化檔案 + 四技能時間追蹤 + CEFR 等級歷史
-- 比照 language-coach-schema.sql 的 RLS 慣例（authenticated 依 user_id 全權）
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. 學習者檔案（每人一筆；跨語言共用基本資料 + 目標）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_profile (
  user_id            uuid primary key references auth.users(id) on delete cascade,
  display_name       text,
  native_lang        text default 'zh-TW',
  primary_language   text default 'en',           -- 目前主修語言
  goal_level         text default 'C2',           -- 目標 CEFR
  target_exam        text,                         -- TOEFL / IELTS / GRE / null
  exam_date          date,                         -- 預計考試日
  interests          jsonb default '[]'::jsonb,    -- ["哲學","歷史","神學",...] 人文領域
  daily_goal_minutes int default 90,               -- 每日目標分鐘
  onboarded          boolean default false,
  created_at         timestamptz default now(),
  updated_at         timestamptz default now()
);

-- ---------------------------------------------------------------------------
-- 2. 每日活動記錄（聽/說/讀/寫四技能時間；每筆活動一列，dashboard 聚合）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_activity (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  language      text not null,
  activity_date date not null default current_date,
  skill         text not null,                     -- listening / speaking / reading / writing
  minutes       numeric(6,2) not null default 0,
  source        text default 'chat',               -- chat / youtube / reading / exam / vocab / manual
  detail        text,
  created_at    timestamptz default now()
);
create index if not exists idx_lang_activity_user on public.lang_activity(user_id, language, activity_date);

-- ---------------------------------------------------------------------------
-- 3. CEFR 等級評估歷史（追蹤 B2→C2 曲線）
-- ---------------------------------------------------------------------------
create table if not exists public.lang_level_history (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  language    text not null,
  level       text not null,                       -- A1..C2
  cefr_score  numeric(4,1),                         -- 數值化（如 B2=70, C1=85）便於畫曲線
  scores      jsonb default '{}'::jsonb,            -- { fluency, grammar, vocabulary, coherence, ... }
  method      text default 'ai',                   -- ai / exam / self
  note        text,
  assessed_at timestamptz default now()
);
create index if not exists idx_lang_level_history_user on public.lang_level_history(user_id, language, assessed_at);

-- ============================================================================
-- RLS
-- ============================================================================
do $$
declare
  t text;
  tbls text[] := array['lang_profile','lang_activity','lang_level_history'];
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
