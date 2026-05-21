-- ============================================================================
-- bible_versions seed — 6 個版本元資料
--   中文：和合本2010（RCUV — HKBS 版權，站內研究用）
--   英文：NIV
--   原文：WLC（希伯來 OT）/ LXX Rahlfs（希臘 OT）/ SBLGNT（希臘 NT）/ Vulgate（拉丁全）
-- ============================================================================

INSERT INTO bible_versions
  (code, name_zh, name_en, language, language_zh, category, scope,
   public_domain, is_redistributable, copyright_notice, source_url,
   display_order, is_default_zh, is_default_en, is_default_orig)
VALUES
  -- 中文
  ('cuv2010', '和合本2010', 'Revised Chinese Union Version (RCUV) 2010',
    'zh-Hant', '繁體中文', 'chinese', 'full',
    FALSE, FALSE,
    '© 香港聖經公會 2010；本站僅作個人研究/對照用途，未開放再散佈或匯出。',
    'https://rcuv.hkbs.org.hk/',
    10, TRUE, FALSE, FALSE),

  -- 英文
  ('niv', 'NIV 新國際譯本', 'New International Version (NIV)',
    'en', '英文', 'english', 'full',
    FALSE, FALSE,
    '© Biblica/Zondervan；本站僅作個人研究/對照用途，未開放再散佈或匯出。',
    'https://www.biblica.com/bible/niv/',
    20, FALSE, TRUE, FALSE),

  -- 原文：希伯來 OT
  ('wlc', 'WLC 西敏士-列寧格勒抄本（希伯來原文）', 'Westminster Leningrad Codex',
    'hbo', '希伯來文', 'source', 'ot_only',
    TRUE, TRUE,
    '文字屬公版；morph/lemma 標記 CC-BY 4.0 — openscriptures/morphhb',
    'https://github.com/openscriptures/morphhb',
    30, FALSE, FALSE, TRUE),

  -- 原文：希臘 OT (LXX)
  ('lxx', 'LXX 七十士譯本（Rahlfs 1935）', 'Septuagint (Rahlfs 1935)',
    'grc', '希臘文', 'source', 'ot_only',
    TRUE, FALSE,
    '文字公版；parsed 資料 CC BY-NC-SA 4.0 — eliranwong/LXX-Rahlfs-1935（非商業用）',
    'https://github.com/eliranwong/LXX-Rahlfs-1935',
    40, FALSE, FALSE, FALSE),

  -- 原文：希臘 NT (SBL GNT)
  ('sblgnt', 'SBLGNT 希臘文新約', 'SBL Greek New Testament',
    'grc', '希臘文', 'source', 'nt_only',
    TRUE, TRUE,
    'CC BY 4.0 — LogosBible/SBLGNT',
    'https://github.com/LogosBible/SBLGNT',
    41, FALSE, FALSE, TRUE),

  -- 原文：拉丁全本 (Clementine Vulgate)
  ('vul', 'Vulgate 拉丁通行本（Clementine 1592/1979）', 'Clementine Vulgate',
    'lat', '拉丁文', 'source', 'full',
    TRUE, TRUE,
    '公版（Clementine Vulgate 1592 / Nova Vulgata 1979 base）',
    'https://github.com/BibleGet-I-O/Clementine-Vulgate',
    50, FALSE, FALSE, FALSE)
ON CONFLICT (code) DO UPDATE
SET
  name_zh = EXCLUDED.name_zh,
  name_en = EXCLUDED.name_en,
  language = EXCLUDED.language,
  language_zh = EXCLUDED.language_zh,
  category = EXCLUDED.category,
  scope = EXCLUDED.scope,
  public_domain = EXCLUDED.public_domain,
  is_redistributable = EXCLUDED.is_redistributable,
  copyright_notice = EXCLUDED.copyright_notice,
  source_url = EXCLUDED.source_url,
  display_order = EXCLUDED.display_order,
  is_default_zh = EXCLUDED.is_default_zh,
  is_default_en = EXCLUDED.is_default_en,
  is_default_orig = EXCLUDED.is_default_orig;
