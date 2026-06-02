-- 信任裝置管理：控制哪些機台能登入；第一台自動核准（管理機），新機台需核准
create table if not exists public.trusted_devices (
  user_id    uuid not null references auth.users(id) on delete cascade,
  device_id  text not null,                 -- 前端產生並存 localStorage 的 uuid
  name       text,                          -- 裝置名稱（瀏覽器 + 系統）
  user_agent text,
  status     text not null default 'pending', -- approved / pending / revoked
  created_at timestamptz default now(),
  last_seen  timestamptz default now(),
  primary key (user_id, device_id)
);
alter table public.trusted_devices enable row level security;
drop policy if exists own_all_trusted_devices on public.trusted_devices;
create policy own_all_trusted_devices on public.trusted_devices
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
