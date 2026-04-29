-- ============================================================
-- 使徒統緒：主教任次表 Schema
-- 在 Supabase SQL Editor 執行此檔案
-- ============================================================

create table if not exists episcopal_succession (
  id                uuid primary key default gen_random_uuid(),
  name_zh           text not null,                        -- 中文名
  name_en           text,                                 -- 英文／拉丁名
  see               text not null,                        -- 主教座（如「羅馬」「亞歷山大」「安提阿」）
  church            text,                                 -- 教會傳統（如「天主教」「東正教」「科普特」）
  succession_number int,                                  -- 第幾任（1、2、3…，NULL 表示不確定）
  start_year        int,                                  -- 就任年（主前為負數）
  end_year          int,                                  -- 卸任年
  end_reason        text check (end_reason in ('殉道', '自然死亡', '逝世', '辭職', '廢黜', '退休', '調任', '晉升', '流亡', '不明')),
  appointed_by      text,                                 -- 任命者（主要用於第一任，如「使徒彼得」）
  predecessor_id    uuid references episcopal_succession(id) on delete set null,  -- 前任（同一統緒線內）
  status            text not null default '正統'
                      check (status in ('正統', '對立', '廢黜後復位', '爭議')),
  rival_of          uuid references episcopal_succession(id) on delete set null,  -- 對立的正統主教
  sources           text,                                 -- 出處（如「Eusebius, HE III.4」）
  notes             text,                                 -- 備注
  created_at        timestamptz default now(),
  updated_at        timestamptz default now(),

  -- 同一主教座、同一教會傳統內不能有兩個相同任次
  -- 分裂後各統緒獨立計算（如科普特與東正教都從馬爾谷算第一任）
  unique (see, church, succession_number)
);

-- updated_at 自動更新 trigger（複用 set_updated_at，已在 biblical-genealogy.sql 建立）
drop trigger if exists episcopal_succession_updated_at on episcopal_succession;
create trigger episcopal_succession_updated_at
  before update on episcopal_succession
  for each row execute function set_updated_at();

-- 加速按主教座查詢
create index if not exists episcopal_succession_see_idx
  on episcopal_succession (see, church, succession_number);

-- RLS
alter table episcopal_succession enable row level security;

drop policy if exists "episcopal_succession_select" on episcopal_succession;
drop policy if exists "episcopal_succession_all"    on episcopal_succession;

create policy "episcopal_succession_select" on episcopal_succession
  for select using (auth.role() = 'authenticated');

create policy "episcopal_succession_all" on episcopal_succession
  for all using (auth.role() = 'authenticated');
