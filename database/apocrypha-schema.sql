-- ============================================================================
-- Apocrypha (典外文獻) — schema for /apocrypha portal
--   apocrypha_documents  — 一份文獻 (1 Enoch / Jubilees / Gospel of Thomas …)
--   apocrypha_versions   — 中文 / 英文 / 原文 各種版本 metadata
--   apocrypha_sections   — 每份文獻 × 每版本 = 多筆 section text
-- Pattern mirrors bible_books / bible_versions / bible_verses 但放鬆
-- chapter:verse 結構 (典外文獻通常無清晰 ch:v) 改用 order_index + section_label。
-- ============================================================================

CREATE TABLE IF NOT EXISTS apocrypha_documents (
  slug              VARCHAR(40) PRIMARY KEY,    -- '1-enoch' / 'jubilees' / 'gthom' / 'aristeas' …
  title_zh          VARCHAR(80) NOT NULL,       -- '以諾一書' / '禧年書' / '多馬福音'
  title_zh_short    VARCHAR(20),                -- '以諾一'   / '禧年'   / '多馬'
  title_en          VARCHAR(120) NOT NULL,      -- '1 Enoch' / 'Jubilees' / 'Gospel of Thomas'
  title_orig        VARCHAR(160),               -- 古典語原名 (若已知)
  category          VARCHAR(30) NOT NULL,       -- 'ot_apocrypha' (次經/第二正典) / 'ot_pseudepigrapha' (偽典) /
                                                -- 'nt_apocrypha' (NT 偽典) / 'qumran' / 'nag_hammadi' / 'lost_gospel'
  testament         VARCHAR(20) NOT NULL,       -- 'ot' / 'nt' / 'mixed'
  language_orig     VARCHAR(20),                -- 'greek' / 'hebrew' / 'aramaic' / 'coptic' / 'syriac' / 'ethiopic' / 'latin'
  composition_low   INT,                        -- 寫作年下界 (負數=BCE)
  composition_high  INT,                        -- 寫作年上界
  canon_status_jsonb JSONB,                     -- {protestant:false, catholic:true, orthodox:true, ethiopian:true, …}
  summary_zh        TEXT,                       -- 1-3 句中文簡介
  intro_zh          TEXT,                       -- 黃根春該卷「簡介／導論」全文 (reader 預設摺疊、可點開)
  display_order     INT NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS apocrypha_documents_category ON apocrypha_documents (category);
CREATE INDEX IF NOT EXISTS apocrypha_documents_testament ON apocrypha_documents (testament);
CREATE INDEX IF NOT EXISTS apocrypha_documents_display_order ON apocrypha_documents (display_order);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS apocrypha_versions (
  code              VARCHAR(30) PRIMARY KEY,    -- 'cct_zh' (基督教典外文獻) / 'charles_apot' / 'jbnh' (Robinson NH) /
                                                -- 'mrjames' / 'greek_orig' / 'coptic_orig' / 'ethiopic_orig'
  name_zh           VARCHAR(80) NOT NULL,       -- '基督教典外文獻 (黃根春)' / 'Charles APOT 1913' / 'Robinson Nag Hammadi 1977'
  name_en           VARCHAR(160) NOT NULL,
  language          VARCHAR(20) NOT NULL,       -- 'zh-Hant' / 'en' / 'grc' / 'cop' / 'syr' / 'gez' / 'heb' / 'arc' / 'lat'
  language_zh       VARCHAR(20),                -- '繁體中文' / '英文' / '希臘文' / '科普特文' / '敘利亞文' / 'Ge''ez' / '希伯來文'
  category          VARCHAR(20) NOT NULL,       -- 'chinese' / 'english' / 'source' / 'ancient'
  public_domain     BOOLEAN NOT NULL DEFAULT FALSE,
  is_redistributable BOOLEAN NOT NULL DEFAULT FALSE,
  copyright_notice  TEXT,
  source_url        TEXT,
  display_order     INT NOT NULL,
  is_default_zh     BOOLEAN DEFAULT FALSE,
  is_default_en     BOOLEAN DEFAULT FALSE,
  is_default_orig   BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS apocrypha_versions_category ON apocrypha_versions (category);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS apocrypha_sections (
  id                BIGSERIAL PRIMARY KEY,
  doc_slug          VARCHAR(40) NOT NULL REFERENCES apocrypha_documents (slug) ON DELETE CASCADE,
  version_code      VARCHAR(30) NOT NULL REFERENCES apocrypha_versions (code) ON DELETE CASCADE,
  order_index       INT NOT NULL,               -- 排序/對齊鍵。逐節重建後 = chapter*1000 + verse (中英共用 → 同列對照)
  section_label     VARCHAR(80),                -- 顯示用 label，例 '1:1' / 'saying 12' / '卷一 引言' / '第三章'
  chapter           INT,                        -- 章 (逐節重建後填)
  verse             INT,                        -- 節 (逐節重建後填)
  source_chunk_id   UUID,                       -- 來自哪個 ebook_chunk (可選)
  page_number       INT,                        -- 來源頁碼 (中文 PDF)
  footnote_defs     JSONB,                      -- {marker: definition} per section
  text              TEXT NOT NULL,
  char_count        INT,
  UNIQUE (doc_slug, version_code, order_index)
);
CREATE INDEX IF NOT EXISTS apocrypha_sections_doc_ver
  ON apocrypha_sections (doc_slug, version_code, order_index);
CREATE INDEX IF NOT EXISTS apocrypha_sections_fts
  ON apocrypha_sections USING GIN (to_tsvector('simple', text));

-- ----------------------------------------------------------------------------

ALTER TABLE apocrypha_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE apocrypha_versions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE apocrypha_sections  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "apocrypha_documents_read" ON apocrypha_documents;
DROP POLICY IF EXISTS "apocrypha_versions_read"  ON apocrypha_versions;
DROP POLICY IF EXISTS "apocrypha_sections_read"  ON apocrypha_sections;

CREATE POLICY "apocrypha_documents_read" ON apocrypha_documents FOR SELECT USING (true);
CREATE POLICY "apocrypha_versions_read"  ON apocrypha_versions  FOR SELECT USING (true);
CREATE POLICY "apocrypha_sections_read"  ON apocrypha_sections  FOR SELECT USING (true);
