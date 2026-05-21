-- ============================================================================
-- 加 5 個經典 PD 版本：
--   中文：和合本1919 (ChiUn) / 文理和合本 (ChiUnL)
--   英文：Douay-Rheims (Catholic) / ASV 1901 / YLT (Young's Literal)
-- 來源：scrollmapper/bible_databases (MIT)
-- ============================================================================

INSERT INTO bible_versions
  (code, name_zh, name_en, language, language_zh, category, scope,
   public_domain, is_redistributable, copyright_notice, source_url,
   display_order, is_default_zh, is_default_en, is_default_orig)
VALUES
  ('cuv1919', '和合本1919', 'Chinese Union Version (1919, Mandarin)',
    'zh-Hant', '繁體中文', 'chinese', 'full',
    TRUE, TRUE,
    '公版（1919）。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    12, FALSE, FALSE, FALSE),

  ('cuv1919w', '文理和合本1919', 'Chinese Union Version (1919, Classical / Wenli)',
    'zh-Hant', '文言文', 'chinese', 'full',
    TRUE, TRUE,
    '公版（1919）。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    13, FALSE, FALSE, FALSE),

  ('drc', '杜雷-蘭斯英文聖經（天主教）', 'Douay-Rheims Catholic Bible (Challoner 1899)',
    'en', '英文', 'english', 'full',
    TRUE, TRUE,
    '公版（1899）。天主教傳統英譯，譯自 Vulgate。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    23, FALSE, FALSE, FALSE),

  ('asv', 'ASV 美國標準譯本', 'American Standard Version (1901)',
    'en', '英文', 'english', 'full',
    TRUE, TRUE,
    '公版（1901）。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    24, FALSE, FALSE, FALSE),

  ('ylt', 'YLT 楊氏直譯本', 'Young''s Literal Translation (1862/1898)',
    'en', '英文', 'english', 'full',
    TRUE, TRUE,
    '公版。極度直譯，逐字對應希伯來/希臘文。資料源 scrollmapper/bible_databases (MIT)。',
    'https://github.com/scrollmapper/bible_databases',
    25, FALSE, FALSE, FALSE)

ON CONFLICT (code) DO UPDATE
SET name_zh = EXCLUDED.name_zh, name_en = EXCLUDED.name_en,
    language = EXCLUDED.language, language_zh = EXCLUDED.language_zh,
    category = EXCLUDED.category, scope = EXCLUDED.scope,
    public_domain = EXCLUDED.public_domain,
    is_redistributable = EXCLUDED.is_redistributable,
    copyright_notice = EXCLUDED.copyright_notice,
    source_url = EXCLUDED.source_url,
    display_order = EXCLUDED.display_order;
