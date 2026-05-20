-- ───────────────────────────────────────────────────────────
-- Citation fields for books + journal_articles
-- (so we can emit Chicago/SBL/APA + BibTeX without guessing)
-- ───────────────────────────────────────────────────────────

ALTER TABLE books
  ADD COLUMN IF NOT EXISTS isbn               TEXT,
  ADD COLUMN IF NOT EXISTS doi                TEXT,
  ADD COLUMN IF NOT EXISTS editor             TEXT,
  ADD COLUMN IF NOT EXISTS edition_number     TEXT,
  ADD COLUMN IF NOT EXISTS series_title       TEXT,
  ADD COLUMN IF NOT EXISTS series_number      TEXT,
  ADD COLUMN IF NOT EXISTS container_title    TEXT,   -- 收錄於某論文集時
  ADD COLUMN IF NOT EXISTS container_editor   TEXT,
  ADD COLUMN IF NOT EXISTS pages              TEXT,
  ADD COLUMN IF NOT EXISTS url                TEXT,
  ADD COLUMN IF NOT EXISTS accessed_date      DATE,
  ADD COLUMN IF NOT EXISTS language           TEXT,
  ADD COLUMN IF NOT EXISTS citation_key       TEXT;   -- BibTeX key

CREATE INDEX IF NOT EXISTS books_isbn_idx        ON books (isbn);
CREATE INDEX IF NOT EXISTS books_doi_idx         ON books (doi);
CREATE UNIQUE INDEX IF NOT EXISTS books_citation_key_idx ON books (citation_key) WHERE citation_key IS NOT NULL;

ALTER TABLE journal_articles
  ADD COLUMN IF NOT EXISTS doi                TEXT,
  ADD COLUMN IF NOT EXISTS volume             TEXT,
  ADD COLUMN IF NOT EXISTS issue              TEXT,
  ADD COLUMN IF NOT EXISTS pages              TEXT,
  ADD COLUMN IF NOT EXISTS url                TEXT,
  ADD COLUMN IF NOT EXISTS accessed_date      DATE,
  ADD COLUMN IF NOT EXISTS publisher          TEXT,
  ADD COLUMN IF NOT EXISTS language           TEXT,
  ADD COLUMN IF NOT EXISTS citation_key       TEXT;

CREATE INDEX IF NOT EXISTS journal_articles_doi_idx ON journal_articles (doi);
CREATE UNIQUE INDEX IF NOT EXISTS journal_articles_citation_key_idx
  ON journal_articles (citation_key) WHERE citation_key IS NOT NULL;

-- ───────────────────────────────────────────────────────────
-- Concept notes (Zettelkasten) with bidirectional [[wiki]] links
-- ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS concepts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,                  -- 顯示名稱（中文 OK）
  slug        TEXT NOT NULL UNIQUE,           -- 連結 key（kebab-case 或拼音/中文皆可）
  aliases     TEXT[] DEFAULT '{}',            -- 別名，[[A]] 也能連到此概念
  body        TEXT DEFAULT '',                -- markdown，內含 [[wiki link]]
  summary     TEXT,                           -- 一句話摘要
  color       TEXT,                           -- 視覺分類
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS concepts_name_idx    ON concepts (name);
CREATE INDEX IF NOT EXISTS concepts_aliases_idx ON concepts USING GIN (aliases);

-- 解析 body 內 [[wiki link]] 後落地的有向邊
CREATE TABLE IF NOT EXISTS concept_links (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  to_concept_id   UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  raw_link_text   TEXT,                      -- 原 [[...]] 內字串（可能是別名）
  context         TEXT,                      -- 連結附近 ±60 字
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (from_concept_id, to_concept_id, raw_link_text)
);

CREATE INDEX IF NOT EXISTS concept_links_to_idx   ON concept_links (to_concept_id);
CREATE INDEX IF NOT EXISTS concept_links_from_idx ON concept_links (from_concept_id);

-- 把書摘 / 期刊 / 訪談連到概念（多對多）
CREATE TABLE IF NOT EXISTS excerpt_concepts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  excerpt_id  UUID NOT NULL REFERENCES excerpts(id) ON DELETE CASCADE,
  concept_id  UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (excerpt_id, concept_id)
);

CREATE INDEX IF NOT EXISTS excerpt_concepts_excerpt_idx ON excerpt_concepts (excerpt_id);
CREATE INDEX IF NOT EXISTS excerpt_concepts_concept_idx ON excerpt_concepts (concept_id);
