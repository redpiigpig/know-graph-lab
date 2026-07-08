-- 2026-07-08 DB 容量救援：free tier 500MB 被用到 1,313MB → REST 整個被鎖
-- (exceed_db_size_quota)。以下 5 支 GIN 全文索引 idx_scan 全為 0（pg_stat_user_indexes），
-- 全站程式碼只用 ilike 搜尋、無任何 textSearch/to_tsvector 查詢 → 純死重 ~598MB，拆除。
-- 若日後要改用 Postgres 全文搜尋，用下列定義重建即可：

-- 411 MB
-- CREATE INDEX idx_ebook_chunks_fts ON public.ebook_chunks USING gin (to_tsvector('simple'::regconfig, content));
-- 120 MB
-- CREATE INDEX bible_verses_fts ON public.bible_verses USING gin (to_tsvector('simple'::regconfig, text));
-- 35 MB
-- CREATE INDEX gnostic_sections_fts ON public.gnostic_sections USING gin (to_tsvector('simple'::regconfig, text));
-- 19 MB
-- CREATE INDEX apocrypha_sections_fts ON public.apocrypha_sections USING gin (to_tsvector('simple'::regconfig, text));
-- 13 MB
-- CREATE INDEX excerpts_content_idx ON public.excerpts USING gin (to_tsvector('simple'::regconfig, COALESCE(content, ''::text)));

DROP INDEX IF EXISTS idx_ebook_chunks_fts;
DROP INDEX IF EXISTS bible_verses_fts;
DROP INDEX IF EXISTS gnostic_sections_fts;
DROP INDEX IF EXISTS apocrypha_sections_fts;
DROP INDEX IF EXISTS excerpts_content_idx;

-- 第二輪（同日）：canon_law fts 同 pattern 零掃描；page_embeddings 是舊上傳流程遺留
-- （RAG 走 match_excerpts / excerpt_embeddings，該索引保留）。
-- CREATE INDEX canon_law_sections_fts ON public.canon_law_sections USING gin (to_tsvector('simple'::regconfig, text));
-- CREATE INDEX page_embeddings_idx ON public.page_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists='100');
DROP INDEX IF EXISTS canon_law_sections_fts;
DROP INDEX IF EXISTS page_embeddings_idx;
