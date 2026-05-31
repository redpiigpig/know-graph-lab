-- 今日簡報每日快取：存進 lang_memory，避免每次進首頁都呼叫 Gemini
alter table public.lang_memory add column if not exists briefing      jsonb;
alter table public.lang_memory add column if not exists briefing_date date;
