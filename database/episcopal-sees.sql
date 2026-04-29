-- ============================================================
-- 宗主教座總表 Schema
-- 執行前請確保已執行 episcopal-succession.sql（需要 set_updated_at function）
-- ============================================================

create table if not exists episcopal_sees (
  id                    uuid primary key default gen_random_uuid(),
  name_zh               text not null unique,    -- 完整中文名（如「科普特東正教亞歷山大宗主教座」）
  name_en               text,                    -- 完整英文名
  see_zh                text not null,           -- 主教座城市（對應 episcopal_succession.see，如「亞歷山大」）
  church                text,                    -- 教會傳統（對應 episcopal_succession.church）
  tradition             text check (tradition in (
                          '東正教', '東方正教', '東方教會', '東儀天主教', '天主教（拉丁禮）'
                        )),
  rite                  text,                    -- 禮儀傳統（拜占庭禮、科普特禮、西敘利亞禮…）
  founded_year          int,                     -- 建立年份（主前為負數）
  abolished_year        int,                     -- 廢除年份（NULL = 現存）
  status                text not null default '現存'
                          check (status in ('現存', '已廢除', '名義')),
  current_patriarch_zh  text,                    -- 現任宗主教（中文）
  current_patriarch_en  text,                    -- 現任宗主教（英文）
  incumbent_since       int,                     -- 現任就任年
  location              text,                    -- 現址
  parent_see_id         uuid references episcopal_sees(id) on delete set null,  -- 分裂自哪個宗主教座
  split_year            int,                     -- 分裂年份
  notes                 text,
  sources               text,
  created_at            timestamptz default now(),
  updated_at            timestamptz default now(),

  unique (see_zh, church)
);

-- updated_at trigger
drop trigger if exists episcopal_sees_updated_at on episcopal_sees;
create trigger episcopal_sees_updated_at
  before update on episcopal_sees
  for each row execute function set_updated_at();

-- 查詢加速
create index if not exists episcopal_sees_tradition_idx on episcopal_sees (tradition, status);
create index if not exists episcopal_sees_see_zh_idx    on episcopal_sees (see_zh);

-- RLS
alter table episcopal_sees enable row level security;

create policy "episcopal_sees_select" on episcopal_sees
  for select using (auth.role() = 'authenticated');

create policy "episcopal_sees_all" on episcopal_sees
  for all using (auth.role() = 'authenticated');
