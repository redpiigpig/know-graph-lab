-- 共用學習單字庫（站長專屬私站，非 per-user）
-- 每語言一份權威策展字庫：頻率表 / 語料庫詞元 + LLM 補繁中釋義+例句。
-- review / vocab.generate 缺題時先抽這裡（全語言），抽不到才呼叫 AI。
-- 解決「希臘文等非英語只能即時生成、AI 一掛就斷糧」的結構性問題。
create table if not exists public.lang_vocab_bank (
  id             uuid primary key default gen_random_uuid(),
  language       text not null,                 -- en/de/fr/ja/grc/la/hbo
  word           text not null,                 -- 單字（外語）
  reading        text,                          -- 假名/音標/轉寫/詞元形
  meaning        text,                          -- 繁中釋義（LLM 補；補完前可 null）
  example        text,                          -- 例句（外語）
  part_of_speech text,
  category       text not null,                 -- 分類標籤（新約高頻字 / AWL Sublist 1 / 高頻 1–1000…）
  level          text,                          -- CEFR/JLPT/古語量表 band（可空）
  freq_rank      int,                           -- 該語言整體頻率排名（可空）
  source         text not null default 'llm',   -- freqwords/morphgnt/stepbible/jlpt/goethe/vulgate/llm
  glossed        boolean not null default false,-- 是否已補繁中釋義
  created_at     timestamptz default now(),
  updated_at     timestamptz default now(),
  unique (language, word)
);

-- 語意主題（神/聖經人物/敬拜/家庭/食物/自然…）— 字典「主題」分頁用；由 LLM 一次性批次分類
alter table public.lang_vocab_bank add column if not exists theme text;

create index if not exists idx_vocab_bank_lang_cat   on public.lang_vocab_bank(language, category);
create index if not exists idx_vocab_bank_lang_glos  on public.lang_vocab_bank(language, glossed);
create index if not exists idx_vocab_bank_lang_freq  on public.lang_vocab_bank(language, freq_rank);
create index if not exists idx_vocab_bank_lang_theme on public.lang_vocab_bank(language, theme);

alter table public.lang_vocab_bank enable row level security;

-- 私站：已登入者可讀（站長本人）；寫入只走 service role（後端 admin client / 批次腳本）
drop policy if exists vocab_bank_read on public.lang_vocab_bank;
create policy vocab_bank_read on public.lang_vocab_bank
  for select to authenticated using (true);
