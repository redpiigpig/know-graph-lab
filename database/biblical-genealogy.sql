-- ============================================================
-- 聖經人物族譜 Schema
-- 在 Supabase SQL Editor 執行此檔案
-- ============================================================

create table if not exists biblical_people (
  id              uuid primary key default gen_random_uuid(),
  name_zh         text not null,                        -- 中文姓名
  name_en         text,                                 -- 英文姓名
  gender          text check (gender in ('男', '女', '不明')),  -- 性別
  nationality     text,                                 -- 國別／族別（例：猶大人、以色列人、埃及人）
  birth_year      int,                                  -- 出生年（主前為負數，例：-2000）
  death_year      int,                                  -- 死亡年
  child_year      int,                                  -- 生子年（生第一個孩子時的年份）
  age             int,                                  -- 歲數（聖經記載，可與 death-birth 不同）
  spouse          text,                                 -- 配偶姓名（逗號分隔）
  children        text,                                 -- 兒女姓名（逗號分隔）
  sources         text,                                 -- 出處（如「創世記 5:1-5; 歷代志上 1:1」）
  notes           text,                                 -- 備注
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- 正規化關聯表（可選，用於精確查詢配偶／親子關係）
create table if not exists biblical_relationships (
  id              uuid primary key default gen_random_uuid(),
  person_id       uuid not null references biblical_people(id) on delete cascade,
  related_id      uuid not null references biblical_people(id) on delete cascade,
  -- spouse: 配偶  parent: person 是 related 的父/母  child: person 是 related 的子女  sibling: 兄弟姊妹
  relationship    text not null check (relationship in ('spouse', 'parent', 'child', 'sibling')),
  created_at      timestamptz default now(),
  unique (person_id, related_id, relationship)
);

-- updated_at 自動更新 trigger
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists biblical_people_updated_at on biblical_people;
create trigger biblical_people_updated_at
  before update on biblical_people
  for each row execute function set_updated_at();

-- RLS（Row Level Security）— 開啟後僅允許已登入用戶讀寫
alter table biblical_people       enable row level security;
alter table biblical_relationships enable row level security;

-- 任何已登入用戶可讀取
create policy "biblical_people_select" on biblical_people
  for select using (auth.role() = 'authenticated');

-- 任何已登入用戶可新增／修改／刪除
create policy "biblical_people_all" on biblical_people
  for all using (auth.role() = 'authenticated');

create policy "biblical_relationships_select" on biblical_relationships
  for select using (auth.role() = 'authenticated');

create policy "biblical_relationships_all" on biblical_relationships
  for all using (auth.role() = 'authenticated');
