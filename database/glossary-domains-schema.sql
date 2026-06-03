-- ============================================================================
-- 「翻譯定名」(/translation-glossary, 升頂層卡) — 新增各領域表
--   philosophers / scientists / historical_rulers / place_names / deities
-- 保留既有 theologians + theological_terms（神學）；新領域各一表。
-- 共同核心欄 + name_root（名根一致性，密特/塞琉/亞歷山）+ 領域專屬欄。
-- RLS 比照神學表：anon SELECT + authenticated CRUD。
-- ============================================================================

-- 既有神學表補 name_root（名根一致性檢查跨全領域）
ALTER TABLE theologians       ADD COLUMN IF NOT EXISTS name_root VARCHAR(40);
ALTER TABLE theological_terms ADD COLUMN IF NOT EXISTS name_root VARCHAR(40);

-- ── philosophers 哲學家 ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS philosophers (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),
  name_original_lang    VARCHAR(20),                 -- grc / lat / de / fr / ar …
  name_romanized        VARCHAR(200),
  name_english          VARCHAR(200) NOT NULL,
  name_recommended      VARCHAR(200),                -- ★ 主譯
  name_variants         TEXT,                        -- ；分隔（古譯／大陸／台／港／學界）
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  school                VARCHAR(80),                 -- 蘇格拉底前／斯多噶／經院／啟蒙／分析…
  era                   VARCHAR(40),                 -- 古希臘／希臘化／中世紀／近代／現代
  nationality           VARCHAR(80),
  born_year             INT,                         -- 負數=BC
  died_year             INT,
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- ── scientists 科學家 ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scientists (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),
  name_original_lang    VARCHAR(20),
  name_romanized        VARCHAR(200),
  name_english          VARCHAR(200) NOT NULL,
  name_recommended      VARCHAR(200),
  name_variants         TEXT,
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  field                 VARCHAR(80),                 -- 物理／天文／化學／數學／醫學／博物
  era                   VARCHAR(40),
  nationality           VARCHAR(80),
  born_year             INT,
  died_year             INT,
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- ── historical_rulers 歷代帝王 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historical_rulers (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),
  name_original_lang    VARCHAR(20),
  name_romanized        VARCHAR(200),
  name_english          VARCHAR(200) NOT NULL,
  name_recommended      VARCHAR(200),
  name_variants         TEXT,
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  polity                VARCHAR(120),                -- 朝代／帝國（羅馬／塞琉古／薩珊／鄂圖曼…）
  title                 VARCHAR(60),                 -- 皇帝／國王／沙阿／法老／蘇丹／可汗
  region                VARCHAR(80),
  reign_start           INT,                         -- 負數=BC
  reign_end             INT,
  born_year             INT,
  died_year             INT,
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- ── place_names 國名與城市 ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS place_names (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),
  name_original_lang    VARCHAR(20),
  name_romanized        VARCHAR(200),
  name_english          VARCHAR(200) NOT NULL,
  name_recommended      VARCHAR(200),
  name_variants         TEXT,
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  place_type            VARCHAR(40),                 -- country／city／region／river／mountain／province
  modern_name           VARCHAR(160),                -- 今名（亞歷山卓 = 今 Alexandria）
  modern_country        VARCHAR(80),
  region                VARCHAR(80),
  period                VARCHAR(60),                 -- 古典／中世紀／近代／現代
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- ── deities 神祇與宗教名詞 ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS deities (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),
  name_original_lang    VARCHAR(20),
  name_romanized        VARCHAR(200),
  name_english          VARCHAR(200) NOT NULL,
  name_recommended      VARCHAR(200),
  name_variants         TEXT,
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  religion              VARCHAR(80),                 -- 希臘／羅馬／埃及／北歐／印度教／佛教／瑣羅亞斯德／米所波大米
  entity_type           VARCHAR(40),                 -- deity 神祇／concept 概念／term 名詞／title 稱號
  domain_of             VARCHAR(200),                -- 掌管（戰爭／智慧／豐饒…）
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- ── indexes ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS philosophers_name_english_lower ON philosophers (LOWER(name_english));
CREATE INDEX IF NOT EXISTS scientists_name_english_lower   ON scientists (LOWER(name_english));
CREATE INDEX IF NOT EXISTS rulers_name_english_lower       ON historical_rulers (LOWER(name_english));
CREATE INDEX IF NOT EXISTS places_name_english_lower       ON place_names (LOWER(name_english));
CREATE INDEX IF NOT EXISTS deities_name_english_lower       ON deities (LOWER(name_english));
CREATE INDEX IF NOT EXISTS philosophers_root ON philosophers (name_root);
CREATE INDEX IF NOT EXISTS scientists_root   ON scientists (name_root);
CREATE INDEX IF NOT EXISTS rulers_root       ON historical_rulers (name_root);
CREATE INDEX IF NOT EXISTS places_root       ON place_names (name_root);
CREATE INDEX IF NOT EXISTS deities_root      ON deities (name_root);

-- ── RLS: anon SELECT + authenticated CRUD (比照神學表) ──────────────────────
ALTER TABLE philosophers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_philosophers" ON philosophers;
CREATE POLICY "anon_read_philosophers" ON philosophers FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_philosophers" ON philosophers;
CREATE POLICY "auth_select_philosophers" ON philosophers FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_philosophers" ON philosophers;
CREATE POLICY "auth_insert_philosophers" ON philosophers FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_philosophers" ON philosophers;
CREATE POLICY "auth_update_philosophers" ON philosophers FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_philosophers" ON philosophers;
CREATE POLICY "auth_delete_philosophers" ON philosophers FOR DELETE TO authenticated USING (true);
ALTER TABLE scientists ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_scientists" ON scientists;
CREATE POLICY "anon_read_scientists" ON scientists FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_scientists" ON scientists;
CREATE POLICY "auth_select_scientists" ON scientists FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_scientists" ON scientists;
CREATE POLICY "auth_insert_scientists" ON scientists FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_scientists" ON scientists;
CREATE POLICY "auth_update_scientists" ON scientists FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_scientists" ON scientists;
CREATE POLICY "auth_delete_scientists" ON scientists FOR DELETE TO authenticated USING (true);
ALTER TABLE historical_rulers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_historical_rulers" ON historical_rulers;
CREATE POLICY "anon_read_historical_rulers" ON historical_rulers FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_historical_rulers" ON historical_rulers;
CREATE POLICY "auth_select_historical_rulers" ON historical_rulers FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_historical_rulers" ON historical_rulers;
CREATE POLICY "auth_insert_historical_rulers" ON historical_rulers FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_historical_rulers" ON historical_rulers;
CREATE POLICY "auth_update_historical_rulers" ON historical_rulers FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_historical_rulers" ON historical_rulers;
CREATE POLICY "auth_delete_historical_rulers" ON historical_rulers FOR DELETE TO authenticated USING (true);
ALTER TABLE place_names ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_place_names" ON place_names;
CREATE POLICY "anon_read_place_names" ON place_names FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_place_names" ON place_names;
CREATE POLICY "auth_select_place_names" ON place_names FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_place_names" ON place_names;
CREATE POLICY "auth_insert_place_names" ON place_names FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_place_names" ON place_names;
CREATE POLICY "auth_update_place_names" ON place_names FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_place_names" ON place_names;
CREATE POLICY "auth_delete_place_names" ON place_names FOR DELETE TO authenticated USING (true);
ALTER TABLE deities ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_deities" ON deities;
CREATE POLICY "anon_read_deities" ON deities FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_deities" ON deities;
CREATE POLICY "auth_select_deities" ON deities FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_deities" ON deities;
CREATE POLICY "auth_insert_deities" ON deities FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_deities" ON deities;
CREATE POLICY "auth_update_deities" ON deities FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_deities" ON deities;
CREATE POLICY "auth_delete_deities" ON deities FOR DELETE TO authenticated USING (true);
