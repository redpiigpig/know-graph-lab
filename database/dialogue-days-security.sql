-- Security migration for the existing dialogue_days table.
-- The table contains private dialogue content and is read through server-only
-- routes backed by the Supabase service role.

begin;

alter table public.dialogue_days enable row level security;

-- Defense in depth: no browser role receives direct table access, and no RLS
-- policy is created for either role. The backend retains only the DML it uses.
revoke all privileges on table public.dialogue_days from anon, authenticated;
revoke all privileges on table public.dialogue_days from service_role;
grant select, insert, update, delete on table public.dialogue_days to service_role;

commit;
