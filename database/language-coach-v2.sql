-- ============================================================================
-- AI 語言教練 v2：統整記憶庫 + small-talk 限時模式 + 人格切換
-- ============================================================================

-- 1. 統整記憶庫（每人每語言一筆；跨 session 的長期了解，注入每次對話）
create table if not exists public.lang_memory (
  user_id    uuid not null references auth.users(id) on delete cascade,
  language   text not null,
  memory     text,                          -- 統整的長期記憶（教練對你的了解）
  highlights jsonb default '{}'::jsonb,       -- { strengths:[], weaknesses:[], topics:[], goals_note }
  updated_at timestamptz default now(),
  primary key (user_id, language)
);
alter table public.lang_memory enable row level security;
drop policy if exists own_all_lang_memory on public.lang_memory;
create policy own_all_lang_memory on public.lang_memory
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

-- 2. lang_sessions 擴充：人格 / 模式 / 主題 / 限時 / 結束反饋
alter table public.lang_sessions add column if not exists persona         text;
alter table public.lang_sessions add column if not exists mode            text default 'chat';   -- chat / smalltalk
alter table public.lang_sessions add column if not exists topic           text;
alter table public.lang_sessions add column if not exists duration_target int;                   -- 目標分鐘（3/5/10）
alter table public.lang_sessions add column if not exists feedback        jsonb;                 -- 結束評分卡
