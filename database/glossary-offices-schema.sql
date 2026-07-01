-- ============================================================================
-- 「翻譯定名」/translation-glossary — 官制與行政區 (offices & admin divisions)
--   official_titles：外國政權的官名／職務名／行政區名 → 依「朝代 register」的中譯。
-- 新增一表，比照 philosophers/scientists/... 的共同核心欄 + 領域專屬欄。
-- 核心新欄：register（所屬朝代官制）、admin_level（層級，捕捉大區→州→郡的層次感）。
-- RLS 比照他表：anon SELECT + authenticated CRUD。
-- 見 .claude/skills/translation-glossary/offices_register_blueprint.md
-- ============================================================================

CREATE TABLE IF NOT EXISTS official_titles (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_original         VARCHAR(200),                -- 原文（拉丁/希臘/波斯/阿拉伯…）
  name_original_lang    VARCHAR(20),                 -- la / grc / peo / ar / akk / he …
  name_romanized        VARCHAR(200),                -- Satrap / Provincia / Strategos
  name_english          VARCHAR(200) NOT NULL,       -- 英文常用形 — lookup key
  name_recommended      VARCHAR(200),                -- ★ register 對應建議中譯（郡守/州牧/節度使）
  name_variants         TEXT,                        -- ；分隔；把「舊的扁平譯」（總督/行省）降為變體對照
  recommendation_reason TEXT,
  name_root             VARCHAR(40),
  entity_type           VARCHAR(20),                 -- 官職 office ／ 行政區 division ／ 封爵 rank ／ 機構 organ
  polity                VARCHAR(120),                -- 所屬政權（對齊 place_names / historical_rulers 命名）
  register              VARCHAR(40),                 -- ★所屬朝代 register（商周制/戰國秦制/漢制/魏晉制/唐制/明清制/周封建五等爵…）
  admin_level           VARCHAR(20),                 -- 中央 ／ 一級 ／ 二級 ／ 三級 ／ 羈縻 ／ 特區（捕捉層次感）
  rank_tier             VARCHAR(20),                 -- 中央 ／ 地方 ／ 軍事 ／ 封爵（性質）
  notes                 TEXT,
  sort_order            INT,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- name_english 可能跨政權撞名（Governor/Prefect 到處都是）→ unique 用 (name_english, polity)。
-- 用具名 constraint（非 expression index）才能供 PostgREST on_conflict=name_english,polity。
ALTER TABLE official_titles DROP CONSTRAINT IF EXISTS official_titles_en_polity_uq;
ALTER TABLE official_titles ADD CONSTRAINT official_titles_en_polity_uq UNIQUE (name_english, polity);
CREATE INDEX IF NOT EXISTS official_titles_register  ON official_titles (register);
CREATE INDEX IF NOT EXISTS official_titles_polity    ON official_titles (polity);
CREATE INDEX IF NOT EXISTS official_titles_root      ON official_titles (name_root);
CREATE INDEX IF NOT EXISTS official_titles_en_lower  ON official_titles (LOWER(name_english));

-- ── RLS: anon SELECT + authenticated CRUD (比照神學表 / 其他領域表) ─────────────
ALTER TABLE official_titles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_read_official_titles" ON official_titles;
CREATE POLICY "anon_read_official_titles" ON official_titles FOR SELECT TO anon USING (true);
DROP POLICY IF EXISTS "auth_select_official_titles" ON official_titles;
CREATE POLICY "auth_select_official_titles" ON official_titles FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "auth_insert_official_titles" ON official_titles;
CREATE POLICY "auth_insert_official_titles" ON official_titles FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "auth_update_official_titles" ON official_titles;
CREATE POLICY "auth_update_official_titles" ON official_titles FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "auth_delete_official_titles" ON official_titles;
CREATE POLICY "auth_delete_official_titles" ON official_titles FOR DELETE TO authenticated USING (true);
