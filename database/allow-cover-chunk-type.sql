-- ebook_chunks.chunk_type 加上 'cover'
--
-- 為什麼：/collected-works 的 reader 本來就寫了封面的處理
--   pages/collected-works/[slug]/[work].vue:207  const isCover = cur.chunk_type === 'cover'
--   pages/collected-works/[slug]/[work].vue:299  目錄時 if (e.chunk_type === 'cover') continue
-- 但 CHECK 只允許 page/chapter/section，所以封面列一律被拒（錯誤碼 23514）。
-- 阿奎那《神學大全》每冊第 0 筆就是封面，被拒之後**連同一批的 24 筆正文一起沒寫進去**
-- （PostgREST 一批＝一句 SQL），17 冊共漏 425 列，站上每冊都少了開頭一段。
--
-- 這是純粹放寬、可回溯相容：現有 page/chapter/section 不受影響。
-- 套用：走 Management API（見 memory reference_supabase_management_api）。
alter table ebook_chunks drop constraint ebook_chunks_chunk_type_check;
alter table ebook_chunks add constraint ebook_chunks_chunk_type_check
  check (chunk_type = any (array['page', 'chapter', 'section', 'cover']));
