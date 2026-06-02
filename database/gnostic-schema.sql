-- ============================================================================
-- Gnostic Library (諾斯底主義文獻) — schema for /gnostic portal card
--   gnostic_documents — 一篇文獻 (Gospel of Thomas / Pistis Sophia / Poimandres …)
--   gnostic_versions  — 英文 (gnosis.org 公有領域英譯) / 繁中 (我逐段翻) 版本 metadata
--   gnostic_sections  — 每篇 × 每版本 = 多筆 section text，order_index 逐段對齊
-- Mirrors apocrypha_{documents,versions,sections}. Source = gnosis.org.
-- EN↔ZH align by order_index (same order_index = 對照同一段).
-- ============================================================================

CREATE TABLE IF NOT EXISTS gnostic_documents (
  slug              VARCHAR(48) PRIMARY KEY,    -- 'gospel-of-thomas' / 'pistis-sophia' / 'poimandres'
  title_zh          VARCHAR(80) NOT NULL,
  title_zh_short    VARCHAR(24),
  title_en          VARCHAR(160) NOT NULL,
  title_orig        VARCHAR(160),               -- 古典語原名 (若已知)
  category          VARCHAR(30) NOT NULL,       -- = gnostic_library.CATEGORIES[].key
  language_orig     VARCHAR(20),                -- 'coptic' / 'greek' / 'syriac' / 'mandaic' / 'latin'
  composition_low   INT,                        -- 寫作年下界 (負數=BCE)
  composition_high  INT,
  summary_zh        TEXT,
  source_url        TEXT,                       -- gnosis.org 該篇 URL
  display_order     INT NOT NULL DEFAULT 0,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS gnostic_documents_category ON gnostic_documents (category);
CREATE INDEX IF NOT EXISTS gnostic_documents_display_order ON gnostic_documents (display_order);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS gnostic_versions (
  code              VARCHAR(30) PRIMARY KEY,    -- 'gnosis_en' / 'zh' / (預留) 'coptic_orig'
  name_zh           VARCHAR(80) NOT NULL,
  name_en           VARCHAR(160) NOT NULL,
  language          VARCHAR(20) NOT NULL,       -- 'en' / 'zh-Hant' / 'cop' / 'grc' …
  language_zh       VARCHAR(20),
  category          VARCHAR(20) NOT NULL,       -- 'english' / 'chinese' / 'source'
  public_domain     BOOLEAN NOT NULL DEFAULT FALSE,
  copyright_notice  TEXT,
  source_url        TEXT,
  display_order     INT NOT NULL DEFAULT 0,
  is_default_en     BOOLEAN DEFAULT FALSE,
  is_default_zh     BOOLEAN DEFAULT FALSE,
  is_default_orig   BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS gnostic_versions_category ON gnostic_versions (category);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS gnostic_sections (
  id                BIGSERIAL PRIMARY KEY,
  doc_slug          VARCHAR(48) NOT NULL REFERENCES gnostic_documents (slug) ON DELETE CASCADE,
  version_code      VARCHAR(30) NOT NULL REFERENCES gnostic_versions (code) ON DELETE CASCADE,
  order_index       INT NOT NULL,               -- EN↔ZH 對齊鍵 (0,1,2,…)
  section_label     VARCHAR(80),                -- 'saying 12' / '§3' / '第三章'
  text              TEXT NOT NULL,
  char_count        INT,
  UNIQUE (doc_slug, version_code, order_index)
);
CREATE INDEX IF NOT EXISTS gnostic_sections_doc_ver
  ON gnostic_sections (doc_slug, version_code, order_index);
CREATE INDEX IF NOT EXISTS gnostic_sections_fts
  ON gnostic_sections USING GIN (to_tsvector('simple', text));

-- ----------------------------------------------------------------------------
-- RLS: public read (same posture as apocrypha)

ALTER TABLE gnostic_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE gnostic_versions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE gnostic_sections  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "gnostic_documents_read" ON gnostic_documents;
DROP POLICY IF EXISTS "gnostic_versions_read"  ON gnostic_versions;
DROP POLICY IF EXISTS "gnostic_sections_read"  ON gnostic_sections;

CREATE POLICY "gnostic_documents_read" ON gnostic_documents FOR SELECT USING (true);
CREATE POLICY "gnostic_versions_read"  ON gnostic_versions  FOR SELECT USING (true);
CREATE POLICY "gnostic_sections_read"  ON gnostic_sections  FOR SELECT USING (true);

-- ----------------------------------------------------------------------------
-- Seed the two baseline versions (英文 gnosis.org 公有領域英譯 / 我的逐段繁中)

INSERT INTO gnostic_versions
  (code, name_zh, name_en, language, language_zh, category, public_domain, source_url, display_order, is_default_en, is_default_zh, is_default_orig)
VALUES
  ('gnosis_en', 'The Gnostic Society Library 英譯', 'The Gnostic Society Library (gnosis.org)', 'en', '英文', 'english', TRUE, 'http://gnosis.org/library.html', 10, TRUE, FALSE, FALSE),
  ('zh',        '逐段繁體中譯',                       'Per-paragraph Traditional Chinese translation', 'zh-Hant', '繁體中文', 'chinese', FALSE, NULL, 20, FALSE, TRUE, FALSE)
ON CONFLICT (code) DO UPDATE SET
  name_zh = EXCLUDED.name_zh, name_en = EXCLUDED.name_en, language = EXCLUDED.language,
  language_zh = EXCLUDED.language_zh, category = EXCLUDED.category,
  public_domain = EXCLUDED.public_domain, source_url = EXCLUDED.source_url,
  display_order = EXCLUDED.display_order, is_default_en = EXCLUDED.is_default_en,
  is_default_zh = EXCLUDED.is_default_zh;
