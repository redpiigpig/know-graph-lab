-- ============================================================================
-- 加 3 個版本：KJVA / 思高 / Brenton LXX 英譯
-- 目的：補次經與第二正典的中英文欄
-- ============================================================================

INSERT INTO bible_versions
  (code, name_zh, name_en, language, language_zh, category, scope,
   public_domain, is_redistributable, copyright_notice, source_url,
   display_order, is_default_zh, is_default_en, is_default_orig)
VALUES
  -- 英文：KJV 1611 含次經
  ('kjva', 'KJV 1611 含次經', 'King James Version with Apocrypha (1611)',
    'en', '英文', 'english', 'full',
    TRUE, TRUE,
    '公版（KJV 1611）。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    21, FALSE, FALSE, FALSE),

  -- 中文：思高聖經（含次經第二正典）
  ('sigao', '思高聖經', 'Studium Biblicum (Sigao) Chinese Bible',
    'zh-Hant', '繁體中文', 'chinese', 'catholic_only',
    FALSE, FALSE,
    '© 思高聖經學會；資料源 scrollmapper/bible_databases (MIT) — 法律灰色，僅作站內研究對照用，未開放再散佈。',
    'https://github.com/scrollmapper/bible_databases',
    11, FALSE, FALSE, FALSE),

  -- 英文：Brenton LXX 英譯（1851，含 LXX 全本+次經）
  ('brenton', 'Brenton LXX 英譯', 'Brenton''s English Translation of the Septuagint (1851)',
    'en', '英文', 'english', 'ot_only',
    TRUE, TRUE,
    '公版（Brenton 1851）。資料源 eBible.org/eng-Brenton。',
    'https://ebible.org/eng-Brenton/',
    22, FALSE, FALSE, FALSE)

ON CONFLICT (code) DO UPDATE
SET
  name_zh = EXCLUDED.name_zh, name_en = EXCLUDED.name_en,
  language = EXCLUDED.language, language_zh = EXCLUDED.language_zh,
  category = EXCLUDED.category, scope = EXCLUDED.scope,
  public_domain = EXCLUDED.public_domain,
  is_redistributable = EXCLUDED.is_redistributable,
  copyright_notice = EXCLUDED.copyright_notice,
  source_url = EXCLUDED.source_url,
  display_order = EXCLUDED.display_order;
