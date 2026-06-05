-- ============================================================================
-- Canon Law (教會法規) — schema for /canon-law portal card
--   canon_law_documents — 一部法規 (CIC 1983 / CCC / Apostolic Canons / Pedalion)
--   canon_law_versions  — 拉丁/希臘原文 (la/grc) / 英文 (en) / 繁中 (zh) 版本 metadata
--   canon_law_sections  — 每部 × 每版本 = 多筆 section text，order_index = 條號/段號 對齊
-- Mirrors gnostic_{documents,versions,sections} + 3 階層欄位（book_label /
-- chapter_label / is_heading）給 reader 側欄樹 (卷/題/章)。
-- la↔en↔zh align by order_index (= 條號；CIC 1..1752 / CCC 1..2865 / Apost 1..85).
-- Primary 繁中 source = vatican.va official (/chinese/cic/, /chinese/ccc/).
-- ============================================================================

CREATE TABLE IF NOT EXISTS canon_law_documents (
  slug              VARCHAR(120) PRIMARY KEY,    -- 'cic-1983' / 'ccc' / 'apostolic-canons-85' / 'pedalion'
  title_zh          VARCHAR(200) NOT NULL,
  title_zh_short    VARCHAR(24),
  title_en          VARCHAR(200) NOT NULL,
  title_lat         VARCHAR(200),
  tradition         VARCHAR(20)  NOT NULL,       -- 'catholic' / 'orthodox' / 'protestant' / 'anglican'
  corpus            VARCHAR(30)  NOT NULL,       -- 'code' / 'catechism' / 'ancient-canons' / 'church-order'
  structure_note    VARCHAR(200),                -- '7 卷 / 1752 條'
  promulgated_year  INT,
  summary_zh        TEXT,
  source_url        TEXT,
  display_order     INT NOT NULL DEFAULT 0,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS canon_law_documents_tradition ON canon_law_documents (tradition);
CREATE INDEX IF NOT EXISTS canon_law_documents_display_order ON canon_law_documents (display_order);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS canon_law_versions (
  code              VARCHAR(30) PRIMARY KEY,     -- 'la' / 'grc' / 'en' / 'zh'
  name_zh           VARCHAR(80) NOT NULL,
  name_en           VARCHAR(160) NOT NULL,
  language          VARCHAR(20) NOT NULL,        -- 'la' / 'grc' / 'en' / 'zh-Hant'
  language_zh       VARCHAR(20),
  category          VARCHAR(20) NOT NULL,        -- 'source' / 'english' / 'chinese'
  public_domain     BOOLEAN NOT NULL DEFAULT FALSE,
  copyright_notice  TEXT,
  source_url        TEXT,
  display_order     INT NOT NULL DEFAULT 0,
  is_default_orig   BOOLEAN DEFAULT FALSE,
  is_default_en     BOOLEAN DEFAULT FALSE,
  is_default_zh     BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS canon_law_versions_category ON canon_law_versions (category);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS canon_law_sections (
  id                BIGSERIAL PRIMARY KEY,
  doc_slug          VARCHAR(120) NOT NULL REFERENCES canon_law_documents (slug) ON DELETE CASCADE,
  version_code      VARCHAR(30)  NOT NULL REFERENCES canon_law_versions (code) ON DELETE CASCADE,
  order_index       INT NOT NULL,                -- la↔en↔zh 對齊鍵 = 條號/段號
  section_label     VARCHAR(80),                 -- 'Can. 1' / '第 1 條' / '748'
  book_label        VARCHAR(160),                -- 所屬卷/題 → reader 側欄樹一層 ('第一卷 總則')
  chapter_label     VARCHAR(160),                -- 所屬編/題/章 → 側欄樹二層
  is_heading        BOOLEAN NOT NULL DEFAULT FALSE,  -- 預留：純標題列 (MVP 不用，樹由 label 分組導出)
  text              TEXT NOT NULL,
  char_count        INT,
  UNIQUE (doc_slug, version_code, order_index)
);
CREATE INDEX IF NOT EXISTS canon_law_sections_doc_ver
  ON canon_law_sections (doc_slug, version_code, order_index);
CREATE INDEX IF NOT EXISTS canon_law_sections_fts
  ON canon_law_sections USING GIN (to_tsvector('simple', text));

-- ----------------------------------------------------------------------------
-- RLS: public read (same posture as gnostic / apocrypha)

ALTER TABLE canon_law_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE canon_law_versions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE canon_law_sections  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "canon_law_documents_read" ON canon_law_documents;
DROP POLICY IF EXISTS "canon_law_versions_read"  ON canon_law_versions;
DROP POLICY IF EXISTS "canon_law_sections_read"  ON canon_law_sections;

CREATE POLICY "canon_law_documents_read" ON canon_law_documents FOR SELECT USING (true);
CREATE POLICY "canon_law_versions_read"  ON canon_law_versions  FOR SELECT USING (true);
CREATE POLICY "canon_law_sections_read"  ON canon_law_sections  FOR SELECT USING (true);

-- ----------------------------------------------------------------------------
-- Seed the baseline versions (拉丁/希臘原文 / 英文 / 官方繁中)

INSERT INTO canon_law_versions
  (code, name_zh, name_en, language, language_zh, category, public_domain, source_url, display_order, is_default_orig, is_default_en, is_default_zh)
VALUES
  ('zh',  '官方繁體中文',  'Official Traditional Chinese', 'zh-Hant', '繁體中文', 'chinese', TRUE,  'https://www.vatican.va/chinese/', 10, FALSE, FALSE, TRUE),
  ('en',  '英文',          'English',                      'en',      '英文',     'english', TRUE,  'https://www.vatican.va/archive/', 20, FALSE, TRUE,  FALSE),
  ('la',  '拉丁原文',      'Latin (original)',             'la',      '拉丁文',   'source',  TRUE,  'https://www.vatican.va/archive/', 30, TRUE,  FALSE, FALSE),
  ('grc', '希臘原文',      'Greek (original)',             'grc',     '希臘文',   'source',  TRUE,  NULL, 40, TRUE,  FALSE, FALSE)
ON CONFLICT (code) DO UPDATE SET
  name_zh = EXCLUDED.name_zh, name_en = EXCLUDED.name_en, language = EXCLUDED.language,
  language_zh = EXCLUDED.language_zh, category = EXCLUDED.category,
  public_domain = EXCLUDED.public_domain, source_url = EXCLUDED.source_url,
  display_order = EXCLUDED.display_order, is_default_orig = EXCLUDED.is_default_orig,
  is_default_en = EXCLUDED.is_default_en, is_default_zh = EXCLUDED.is_default_zh;
