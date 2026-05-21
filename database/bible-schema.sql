-- ============================================================================
-- Bible parallel-comparison schema
--   bible_books    — 各教會 canon 書卷對照（含次經/第二正典/衣索匹亞獨有書卷）
--   bible_versions — 6 個版本元資料（CUV2010 / NIV / WLC / LXX / SBLGNT / Vulgate）
--   bible_verses   — 主表，逐節文字（PK: book + chapter + verse + version）
-- Source list & licensing see SKILL.md (scripture-canon-portal).
-- ============================================================================

CREATE TABLE IF NOT EXISTS bible_books (
  code              VARCHAR(10) PRIMARY KEY,    -- 'gen' / 'exo' / '1sa' / 'tob' / 'sus' / 'eno'
  name_zh           VARCHAR(40) NOT NULL,
  name_zh_short     VARCHAR(10),                -- 簡稱 '創' '出' '太' '林前'（給 UI 緊湊顯示）
  name_en           VARCHAR(60) NOT NULL,
  name_lat          VARCHAR(60),
  name_grc          VARCHAR(60),
  name_heb          VARCHAR(60),
  testament         VARCHAR(20) NOT NULL,       -- 'ot' / 'nt' / 'deutero' / 'apocrypha'
  canon_protestant  BOOLEAN NOT NULL DEFAULT FALSE,
  canon_catholic    BOOLEAN NOT NULL DEFAULT FALSE,
  canon_orthodox    BOOLEAN NOT NULL DEFAULT FALSE,
  canon_ethiopian   BOOLEAN NOT NULL DEFAULT FALSE,
  canon_syriac      BOOLEAN NOT NULL DEFAULT FALSE,
  canon_armenian    BOOLEAN NOT NULL DEFAULT FALSE,
  canon_coptic      BOOLEAN NOT NULL DEFAULT FALSE,
  canon_assyrian    BOOLEAN NOT NULL DEFAULT FALSE,
  display_order     INT NOT NULL,               -- 全域排序（OT 先 NT 次 deutero 最後）
  chapter_count     INT,                        -- 章數（基督新教 KJV 章數為準；可後續修）
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS bible_books_testament ON bible_books (testament);
CREATE INDEX IF NOT EXISTS bible_books_display_order ON bible_books (display_order);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bible_versions (
  code              VARCHAR(20) PRIMARY KEY,    -- 'cuv2010' / 'niv' / 'wlc' / 'lxx' / 'sblgnt' / 'vul'
  name_zh           VARCHAR(60) NOT NULL,
  name_en           VARCHAR(120) NOT NULL,
  language          VARCHAR(20) NOT NULL,       -- 'zh-Hant' / 'en' / 'hbo' / 'grc' / 'lat'
  language_zh       VARCHAR(20),                -- '繁體中文' / '英文' / '希伯來文' / '希臘文' / '拉丁文'
  category          VARCHAR(20) NOT NULL,       -- 'chinese' / 'english' / 'source' / 'ancient'
  scope             VARCHAR(20) NOT NULL DEFAULT 'full',  -- 'ot_only' / 'nt_only' / 'full' / 'catholic_only'
  public_domain     BOOLEAN NOT NULL DEFAULT FALSE,
  is_redistributable BOOLEAN NOT NULL DEFAULT FALSE,      -- false → 站內展示但不開放 export/api
  copyright_notice  TEXT,
  source_url        TEXT,
  display_order     INT NOT NULL,
  is_default_zh     BOOLEAN DEFAULT FALSE,      -- UI 預設展示的中文版本
  is_default_en     BOOLEAN DEFAULT FALSE,      -- UI 預設展示的英文版本
  is_default_orig   BOOLEAN DEFAULT FALSE,      -- UI 預設展示的原文版本
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS bible_versions_category ON bible_versions (category);

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bible_verses (
  book_code         VARCHAR(10) NOT NULL REFERENCES bible_books (code),
  chapter           INT NOT NULL,
  verse             INT NOT NULL,
  version_code      VARCHAR(20) NOT NULL REFERENCES bible_versions (code),
  text              TEXT NOT NULL,
  PRIMARY KEY (book_code, chapter, verse, version_code)
);
CREATE INDEX IF NOT EXISTS bible_verses_book_chapter
  ON bible_verses (book_code, chapter);
CREATE INDEX IF NOT EXISTS bible_verses_version
  ON bible_verses (version_code);
-- 全文搜尋索引（多語 — 用 'simple' 不做 stemming，中／英／希／拉統一處理）
CREATE INDEX IF NOT EXISTS bible_verses_fts
  ON bible_verses USING GIN (to_tsvector('simple', text));

-- ----------------------------------------------------------------------------

-- 公共讀 / authenticated 寫（其他表都這樣 — 跟現有 episcopal_succession / creeds 對齊）
ALTER TABLE bible_books    ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible_verses   ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "bible_books_read"    ON bible_books;
DROP POLICY IF EXISTS "bible_versions_read" ON bible_versions;
DROP POLICY IF EXISTS "bible_verses_read"   ON bible_verses;

CREATE POLICY "bible_books_read"    ON bible_books    FOR SELECT USING (true);
CREATE POLICY "bible_versions_read" ON bible_versions FOR SELECT USING (true);
CREATE POLICY "bible_verses_read"   ON bible_verses   FOR SELECT USING (true);
