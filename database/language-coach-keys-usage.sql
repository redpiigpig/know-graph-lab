-- ============================================================================
-- AI 語言教練 — 雙 key（免費/付費）偏好 + token 用量追蹤
-- ============================================================================

-- 1. 學習者是否已切換到付費 key（免費額度用完 → 確認後設 true）
alter table public.lang_profile add column if not exists use_paid_key boolean default false;

-- 2. Gemini token 用量（逐次累計，給網頁顯示用量與估計成本）
create table if not exists public.lang_api_usage (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  usage_date    date not null default current_date,
  tier          text not null default 'free',   -- free / paid
  model         text not null,
  requests      int  not null default 0,
  prompt_tokens bigint not null default 0,
  output_tokens bigint not null default 0,
  updated_at    timestamptz default now(),
  unique (user_id, usage_date, tier, model)
);
create index if not exists idx_lang_api_usage_user on public.lang_api_usage(user_id, usage_date);

-- RLS
alter table public.lang_api_usage enable row level security;
drop policy if exists own_all_lang_api_usage on public.lang_api_usage;
create policy own_all_lang_api_usage on public.lang_api_usage
  for all to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- 累加用量的 RPC（避免讀-改-寫競態；用 upsert + 累加）
create or replace function public.bump_lang_usage(
  p_user uuid, p_date date, p_tier text, p_model text,
  p_prompt bigint, p_output bigint
) returns void language sql security definer as $$
  insert into public.lang_api_usage (user_id, usage_date, tier, model, requests, prompt_tokens, output_tokens, updated_at)
  values (p_user, p_date, p_tier, p_model, 1, p_prompt, p_output, now())
  on conflict (user_id, usage_date, tier, model)
  do update set
    requests      = public.lang_api_usage.requests + 1,
    prompt_tokens = public.lang_api_usage.prompt_tokens + excluded.prompt_tokens,
    output_tokens = public.lang_api_usage.output_tokens + excluded.output_tokens,
    updated_at    = now();
$$;
