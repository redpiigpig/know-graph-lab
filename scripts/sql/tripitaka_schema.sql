-- 佛教大藏經 /tripitaka —— 目錄與對照表。
-- 正文（9,788 萬字／101 萬段）不進 DB，走 Drive + R2（server/utils/tripitaka.ts）。
--
-- 2026-08-28：SUPABASE_ACCESS_TOKEN（Management API 那把）失效回 403，DDL 跑不了。
-- 請到 Supabase Dashboard → SQL Editor 貼上本檔執行一次，然後：
--   python scripts/tripitaka_db.py --push          # 灌 2,554 列目錄
--   python scripts/tripitaka_parallels.py --push   # 灌對照
-- 資料寫入走 PostgREST（service role key 正常），不需要那把 token。

create table if not exists tripitaka_works (
  id              text primary key,
  canon           text not null,
  vol             int  not null,
  work_no         int  not null,
  work_suffix     text default '',
  title_zh        text not null,
  series          text,
  byline          text,
  dynasty         text,
  translator      text,
  author          text,
  lost_translator boolean default false,
  extent          text,
  juan_count      int,
  division_key    text not null,
  -- X（卍續藏）另有第二層子類（宗派／經疏類目），共 109 個；T／N 為空字串。
  -- 權威來源是 CBETA 站方原書目錄，見 tripitaka_cbeta.XUZANG_SUBDIVISIONS。
  subdivision_key text default '',
  japanese        boolean default false,
  xml_path        text,
  seg_count       int default 0,
  char_count      int default 0,
  toc_count       int default 0,
  -- equiv_count：大正藏原註標出的巴利對應條數
  -- term_count / term_langs：CBETA <cb:tt> 漢梵巴詞條（全藏 29,930 組、142 部）
  equiv_count     int default 0,
  term_count      int default 0,
  term_langs      text[] default '{}',
  parallel_langs  text[] default '{}',
  pali_ref        text,
  sanskrit_ref    text,
  tibetan_toh     text,
  parallel_count  int default 0,
  display_order   int
);
create index if not exists tripitaka_works_div_idx
  on tripitaka_works (division_key, display_order);
create index if not exists tripitaka_works_canon_idx
  on tripitaka_works (canon, work_no);
create index if not exists tripitaka_works_title_idx
  on tripitaka_works using gin (to_tsvector('simple', title_zh));

-- 逐段的跨語對照。段本身在檔案裡，這裡只記「哪一段對到什麼」。
-- src: taisho-equiv（大正藏原註）/ suttacentral / gretil / 84000 / manual
create table if not exists tripitaka_parallels (
  id       bigserial primary key,
  work_id  text not null references tripitaka_works(id) on delete cascade,
  -- 段的**唯一鍵**（T02n0099_p0001a06 或同行第二段的 …a06.2）。
  -- 純行號不唯一：全藏 6.5% 的段與別的段同行起頭，拿行號當鍵會讓
  -- 對照掛到同一行的其他段上。引用式仍是行號，顯示時去掉 .n 後綴。
  -- 整部層級的列用空字串而非 NULL：唯一索引若寫成 coalesce(seg_uid,'')
  -- 是運算式索引，PostgREST 的 on_conflict 認不得，寫入會回 42P10。
  seg_uid  text not null default '',
  lang     text not null,
  ref      text not null,
  src      text not null,
  note     text
);
create index if not exists tripitaka_parallels_work_idx on tripitaka_parallels (work_id);
create unique index if not exists tripitaka_parallels_uniq
  on tripitaka_parallels (work_id, seg_uid, lang, ref, src);

alter table tripitaka_works    enable row level security;
alter table tripitaka_parallels enable row level security;
drop policy if exists tripitaka_works_read on tripitaka_works;
create policy tripitaka_works_read on tripitaka_works for select to authenticated using (true);
drop policy if exists tripitaka_parallels_read on tripitaka_parallels;
create policy tripitaka_parallels_read on tripitaka_parallels for select to authenticated using (true);
