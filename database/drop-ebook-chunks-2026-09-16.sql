-- ebook_chunks 退場（2026-09-16）
--
-- 為什麼：Supabase 免費層上限 500 MB，而資料庫已經漲到 872 MB，這張表獨自佔
-- 503 MB（1,005,032 列）。而它存的只是每個 chunk 的**前 100 字** preview。
--
-- 為什麼不能只瘦身：per-chunk 的表在 Postgres 有硬成本 ——
--   固定欄位（uuid×2＋整數＋時間戳）  87 MB
--   兩個索引（都高頻使用，不能砍）    114 MB
-- 光這兩項就 200 MB，跟存不存文字無關。100 萬列就是這個價。
-- 實測各種瘦身組合最好也只降到 640 MB，仍然超標。
--
-- 資料有沒有遺失：沒有。全文早就在 Drive `_chunks/{id}.jsonl`（正本）＋ R2（鏡像），
-- reader 本來就只讀那一份（server/utils/ebook-chunks.ts）。這張表**只**服務三個地方，
-- 都已改讀 JSONL：
--   server/api/ebooks/search.get.ts          全文搜尋
--   server/api/ebooks/[id]/page-map.get.ts   實體頁對照
--   server/api/ebooks/[id]/chunks/[index].put.ts  編輯後同步 preview
--
-- 搜尋順帶變強：舊版 ilike 只打在那 100 字 preview 上（每段中後段搜不到），
-- 而且沒有支援索引，每查一次就是百萬列全表掃描。改讀 JSONL 之後搜的是全文。
--
-- 🚨 執行前確認：`ls G:\我的雲端硬碟\資料\知識圖工作室\_chunks\*.jsonl | wc -l`
--    要有約 4,800 個檔。JSONL 不在就沒有退路。

begin;

-- 留一份列數與大小的快照，日後對帳用
create table if not exists _dropped_table_notes (
  table_name   text primary key,
  dropped_at   timestamptz not null default now(),
  row_count    bigint,
  total_bytes  bigint,
  note         text
);

insert into _dropped_table_notes (table_name, row_count, total_bytes, note)
select 'ebook_chunks',
       (select count(*) from ebook_chunks),
       pg_total_relation_size('ebook_chunks'),
       '全文在 Drive _chunks/*.jsonl ＋ R2；此表只存前 100 字 preview。'
       || '三個使用端（search／page-map／chunks.put）已改讀 JSONL。'
on conflict (table_name) do update
  set dropped_at = now(), row_count = excluded.row_count,
      total_bytes = excluded.total_bytes, note = excluded.note;

drop table if exists ebook_chunks;

commit;

-- drop 之後空間不會馬上還給作業系統，要 VACUUM FULL 才會縮檔。
-- 這會鎖表，挑沒人用的時候跑。分開執行（VACUUM 不能在交易裡）：
--   vacuum full analyze;
