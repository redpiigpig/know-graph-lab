-- ============================================================================
-- 5 個版權版本 — scrape 自公開閱讀網站，個人研究用
--   NABRE   © USCCB        → nirmalben/bible-nabre-json-dataset
--   呂振中  © HKBS         → bible.fhl.net (lcc)
--   TCV    © UBS          → bible.fhl.net (tcv2019)
--   恢復本  © LSM          → text.recoveryversion.bible
--   Knox   © Westminster  → catholicbible.online
-- ============================================================================

INSERT INTO bible_versions
  (code, name_zh, name_en, language, language_zh, category, scope,
   public_domain, is_redistributable, copyright_notice, source_url,
   display_order, is_default_zh, is_default_en, is_default_orig)
VALUES
  ('lzz', '呂振中譯本', 'Lu Zhenzhong Translation (1970)',
    'zh-Hant', '繁體中文', 'chinese', 'full',
    FALSE, FALSE,
    '© 香港聖經公會；本站僅作個人研究／對照用途，未開放再散佈或匯出。資料源 bible.fhl.net。',
    'https://bible.fhl.net/',
    14, FALSE, FALSE, FALSE),

  ('tcv', '現代中文譯本', 'Today''s Chinese Version (TCV 2019)',
    'zh-Hant', '繁體中文', 'chinese', 'full',
    FALSE, FALSE,
    '© 聯合聖經公會；本站僅作個人研究／對照用途，未開放再散佈或匯出。資料源 bible.fhl.net。',
    'https://bible.fhl.net/',
    15, FALSE, FALSE, FALSE),

  ('rcv', '恢復本', 'Recovery Version (1987/2003)',
    'zh-Hant', '繁體中文', 'chinese', 'full',
    FALSE, FALSE,
    '© Living Stream Ministry / 召會出版社；本站僅作個人研究／對照用途，未開放再散佈或匯出。',
    'https://text.recoveryversion.bible/',
    16, FALSE, FALSE, FALSE),

  ('nabre', 'NABRE 天主教標準英譯', 'New American Bible Revised Edition (NABRE, 2011)',
    'en', '英文', 'english', 'full',
    FALSE, FALSE,
    '© Confraternity of Christian Doctrine (USCCB)；本站僅作個人研究／對照用途，未開放再散佈或匯出。',
    'https://nabre.usccb.org/',
    26, FALSE, FALSE, FALSE),

  ('knox', 'Knox 1949 天主教英譯', 'Knox Bible (Ronald Knox 1949)',
    'en', '英文', 'english', 'full',
    FALSE, FALSE,
    '© Westminster Diocese / Baronius Press（將於 2028 進入公版）；本站僅作個人研究／對照用途。',
    'https://catholicbible.online/knox/',
    27, FALSE, FALSE, FALSE)

ON CONFLICT (code) DO UPDATE
SET name_zh = EXCLUDED.name_zh, name_en = EXCLUDED.name_en,
    language = EXCLUDED.language, language_zh = EXCLUDED.language_zh,
    category = EXCLUDED.category, scope = EXCLUDED.scope,
    public_domain = EXCLUDED.public_domain,
    is_redistributable = EXCLUDED.is_redistributable,
    copyright_notice = EXCLUDED.copyright_notice,
    source_url = EXCLUDED.source_url,
    display_order = EXCLUDED.display_order;
