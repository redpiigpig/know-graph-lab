-- ============================================================================
-- bible_books seed — 全 canon 含次經第二正典 + 衣索匹亞獨有書卷
--   39 (新教 OT) + 27 (NT) + 17 (次經/第二正典 + Daniel 加增) + 3 (衣索匹亞獨有)
--   共 86 卷
-- 各教會 canon 接受度欄位準則：
--   protestant: 新教 39+27（不含次經）
--   catholic:   天主教 46+27（多 Tobit/Judith/Wisdom/Sirach/Baruch+Letter of Jeremiah/1-2 Macc + Daniel 加增）
--   orthodox:   東正教 = 天主教 + 1 Esdras / 3 Macc / Prayer of Manasseh / Psalm 151（4 Macc 為 appendix）
--   ethiopian:  衣索匹亞 Tewahedo = 東正教 + Jubilees / 1 Enoch / 4 Baruch（最廣）
--   armenian:   亞美尼亞 = 天主教次經 + 2 Esdras + 3 Cor（3 Cor 不在此表，因爲屬偽書）
--   coptic:     科普特正教 ≈ 東正教
--   syriac:     敘利亞 Peshitta = OT 39 + NT 22（缺 2 Pet/2-3 John/Jude/Revelation）
--   assyrian:   亞述東方 = 同 Peshitta
-- ============================================================================

INSERT INTO bible_books
  (code, name_zh, name_zh_short, name_en, name_lat, name_grc, name_heb,
   testament, canon_protestant, canon_catholic, canon_orthodox, canon_ethiopian,
   canon_syriac, canon_armenian, canon_coptic, canon_assyrian,
   display_order, chapter_count)
VALUES
  -- ── 舊約 39 卷（所有 canon 都接受）────────────────────────────────────
  ('gen', '創世記',       '創', 'Genesis',        'Genesis',        'Γένεσις',       'בְּרֵאשִׁית',     'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  1, 50),
  ('exo', '出埃及記',     '出', 'Exodus',         'Exodus',         'Ἔξοδος',        'שְׁמוֹת',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  2, 40),
  ('lev', '利未記',       '利', 'Leviticus',      'Leviticus',      'Λευϊτικόν',     'וַיִּקְרָא',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  3, 27),
  ('num', '民數記',       '民', 'Numbers',        'Numeri',         'Ἀριθμοί',       'בְּמִדְבַּר',     'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  4, 36),
  ('deu', '申命記',       '申', 'Deuteronomy',    'Deuteronomium',  'Δευτερονόμιον', 'דְּבָרִים',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  5, 34),
  ('jos', '約書亞記',     '書', 'Joshua',         'Iosue',          'Ἰησοῦς',        'יְהוֹשֻׁעַ',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  6, 24),
  ('jdg', '士師記',       '士', 'Judges',         'Iudicum',        'Κριταί',        'שׁוֹפְטִים',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  7, 21),
  ('rut', '路得記',       '得', 'Ruth',           'Ruth',           'Ῥούθ',          'רוּת',            'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  8,  4),
  ('1sa', '撒母耳記上',   '撒上','1 Samuel',      'I Samuelis',     'Σαμουὴλ Αʹ',    'שְׁמוּאֵל א',     'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  9, 31),
  ('2sa', '撒母耳記下',   '撒下','2 Samuel',      'II Samuelis',    'Σαμουὴλ Βʹ',    'שְׁמוּאֵל ב',     'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 10, 24),
  ('1ki', '列王紀上',     '王上','1 Kings',       'I Regum',        'Βασιλειῶν Γʹ',  'מְלָכִים א',      'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 11, 22),
  ('2ki', '列王紀下',     '王下','2 Kings',       'II Regum',       'Βασιλειῶν Δʹ',  'מְלָכִים ב',      'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 12, 25),
  ('1ch', '歷代志上',     '代上','1 Chronicles',  'I Paralipomenon','Παραλειπομένων Αʹ','דִּבְרֵי הַיָּמִים א','ot',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,13, 29),
  ('2ch', '歷代志下',     '代下','2 Chronicles',  'II Paralipomenon','Παραλειπομένων Βʹ','דִּבְרֵי הַיָּמִים ב','ot',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,14, 36),
  ('ezr', '以斯拉記',     '拉', 'Ezra',           'Esdrae',         'Ἔσδρας Βʹ',     'עֶזְרָא',         'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 15, 10),
  ('neh', '尼希米記',     '尼', 'Nehemiah',       'Nehemiae',       'Νεεμίας',       'נְחֶמְיָה',        'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 16, 13),
  ('est', '以斯帖記',     '斯', 'Esther',         'Esther',         'Ἐσθήρ',         'אֶסְתֵּר',         'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 17, 10),
  ('job', '約伯記',       '伯', 'Job',            'Iob',            'Ἰώβ',           'אִיּוֹב',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 18, 42),
  ('psa', '詩篇',         '詩', 'Psalms',         'Psalmi',         'Ψαλμοί',        'תְּהִלִּים',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 19, 150),
  ('pro', '箴言',         '箴', 'Proverbs',       'Proverbia',      'Παροιμίαι',     'מִשְׁלֵי',         'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 20, 31),
  ('ecc', '傳道書',       '傳', 'Ecclesiastes',   'Ecclesiastes',   'Ἐκκλησιαστής',  'קֹהֶלֶת',         'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 21, 12),
  ('sng', '雅歌',         '歌', 'Song of Songs',  'Canticum',       'Ἆσμα Ἀσμάτων',  'שִׁיר הַשִּׁירִים','ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 22,  8),
  ('isa', '以賽亞書',     '賽', 'Isaiah',         'Isaias',         'Ἠσαΐας',        'יְשַׁעְיָהוּ',     'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 23, 66),
  ('jer', '耶利米書',     '耶', 'Jeremiah',       'Ieremias',       'Ἱερεμίας',      'יִרְמְיָהוּ',      'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 24, 52),
  ('lam', '耶利米哀歌',   '哀', 'Lamentations',   'Lamentationes',  'Θρῆνοι',        'אֵיכָה',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 25,  5),
  ('ezk', '以西結書',     '結', 'Ezekiel',        'Ezechiel',       'Ἰεζεκιήλ',      'יְחֶזְקֵאל',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 26, 48),
  ('dan', '但以理書',     '但', 'Daniel',         'Daniel',         'Δανιήλ',        'דָּנִיֵּאל',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 27, 12),
  ('hos', '何西阿書',     '何', 'Hosea',          'Osee',           'Ὡσηέ',          'הוֹשֵׁעַ',         'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 28, 14),
  ('jol', '約珥書',       '珥', 'Joel',           'Ioel',           'Ἰωήλ',          'יוֹאֵל',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 29,  3),
  ('amo', '阿摩司書',     '摩', 'Amos',           'Amos',           'Ἀμώς',          'עָמוֹס',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 30,  9),
  ('oba', '俄巴底亞書',   '俄', 'Obadiah',        'Abdias',         'Ὀβδιού',        'עֹבַדְיָה',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 31,  1),
  ('jon', '約拿書',       '拿', 'Jonah',          'Ionas',          'Ἰωνᾶς',         'יוֹנָה',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 32,  4),
  ('mic', '彌迦書',       '彌', 'Micah',          'Michaeas',       'Μιχαίας',       'מִיכָה',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 33,  7),
  ('nam', '那鴻書',       '鴻', 'Nahum',          'Nahum',          'Ναούμ',         'נַחוּם',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 34,  3),
  ('hab', '哈巴谷書',     '哈', 'Habakkuk',       'Habacuc',        'Ἀμβακούμ',      'חֲבַקּוּק',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 35,  3),
  ('zep', '西番雅書',     '番', 'Zephaniah',      'Sophonias',      'Σοφονίας',      'צְפַנְיָה',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 36,  3),
  ('hag', '哈該書',       '該', 'Haggai',         'Aggaeus',        'Ἀγγαῖος',       'חַגַּי',          'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 37,  2),
  ('zec', '撒迦利亞書',   '亞', 'Zechariah',      'Zacharias',      'Ζαχαρίας',      'זְכַרְיָה',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 38, 14),
  ('mal', '瑪拉基書',     '瑪', 'Malachi',        'Malachias',      'Μαλαχίας',      'מַלְאָכִי',       'ot', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 39,  4),

  -- ── 新約 27 卷 ──────────────────────────────────────────────────────
  -- 注意：敘利亞 Peshitta 與 亞述東方教會 缺 2 Peter / 2 John / 3 John / Jude / Revelation
  ('mat', '馬太福音',     '太', 'Matthew',        'Matthaeus',      'Κατὰ Ματθαῖον', NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  40, 28),
  ('mrk', '馬可福音',     '可', 'Mark',           'Marcus',         'Κατὰ Μᾶρκον',   NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  41, 16),
  ('luk', '路加福音',     '路', 'Luke',           'Lucas',          'Κατὰ Λουκᾶν',   NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  42, 24),
  ('jhn', '約翰福音',     '約', 'John',           'Iohannes',       'Κατὰ Ἰωάννην',  NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  43, 21),
  ('act', '使徒行傳',     '徒', 'Acts',           'Actus',          'Πράξεις',       NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  44, 28),
  ('rom', '羅馬書',       '羅', 'Romans',         'Romanos',        'Πρὸς Ῥωμαίους', NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  45, 16),
  ('1co', '哥林多前書',   '林前','1 Corinthians', 'I Corinthios',   'Α Κορινθίους',  NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  46, 16),
  ('2co', '哥林多後書',   '林後','2 Corinthians', 'II Corinthios',  'Β Κορινθίους',  NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  47, 13),
  ('gal', '加拉太書',     '加', 'Galatians',      'Galatas',        'Πρὸς Γαλάτας',  NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  48,  6),
  ('eph', '以弗所書',     '弗', 'Ephesians',      'Ephesios',       'Πρὸς Ἐφεσίους', NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  49,  6),
  ('php', '腓立比書',     '腓', 'Philippians',    'Philippenses',   'Πρὸς Φιλιππησίους',NULL,'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  50,  4),
  ('col', '歌羅西書',     '西', 'Colossians',     'Colossenses',    'Πρὸς Κολασσαεῖς',NULL,'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  51,  4),
  ('1th', '帖撒羅尼迦前書','帖前','1 Thessalonians','I Thessalonicenses','Α Θεσσαλονικεῖς',NULL,'nt',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,52,5),
  ('2th', '帖撒羅尼迦後書','帖後','2 Thessalonians','II Thessalonicenses','Β Θεσσαλονικεῖς',NULL,'nt',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,53,3),
  ('1ti', '提摩太前書',   '提前','1 Timothy',     'I Timotheum',    'Α Τιμόθεον',    NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  54,  6),
  ('2ti', '提摩太後書',   '提後','2 Timothy',     'II Timotheum',   'Β Τιμόθεον',    NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  55,  4),
  ('tit', '提多書',       '多', 'Titus',          'Titum',          'Πρὸς Τίτον',    NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  56,  3),
  ('phm', '腓利門書',     '門', 'Philemon',       'Philemonem',     'Πρὸς Φιλήμονα', NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  57,  1),
  ('heb', '希伯來書',     '來', 'Hebrews',        'Hebraeos',       'Πρὸς Ἑβραίους', NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  58, 13),
  ('jas', '雅各書',       '雅', 'James',          'Iacobi',         'Ἰακώβου',       NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  59,  5),
  ('1pe', '彼得前書',     '彼前','1 Peter',       'I Petri',        'Α Πέτρου',      NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  60,  5),
  ('2pe', '彼得後書',     '彼後','2 Peter',       'II Petri',       'Β Πέτρου',      NULL, 'nt', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 61,  3),
  ('1jn', '約翰一書',     '約一','1 John',        'I Iohannis',     'Α Ἰωάννου',     NULL, 'nt', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  62,  5),
  ('2jn', '約翰二書',     '約二','2 John',        'II Iohannis',    'Β Ἰωάννου',     NULL, 'nt', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 63,  1),
  ('3jn', '約翰三書',     '約三','3 John',        'III Iohannis',   'Γ Ἰωάννου',     NULL, 'nt', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 64,  1),
  ('jud', '猶大書',       '猶', 'Jude',           'Iudae',          'Ἰούδα',         NULL, 'nt', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 65,  1),
  ('rev', '啟示錄',       '啟', 'Revelation',     'Apocalypsis',    'Ἀποκάλυψις',    NULL, 'nt', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 66, 22),

  -- ── 次經 / 第二正典（天主教 + 東正教 + 東方教會接受）─────────────────────
  ('tob', '多比傳',       '多比','Tobit',         'Tobias',         'Τωβίτ',         NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  67, 14),
  ('jdt', '友弟德傳',     '友', 'Judith',         'Iudith',         'Ἰουδίθ',        NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  68, 16),
  ('wis', '智慧篇',       '智', 'Wisdom of Solomon','Sapientia',    'Σοφία Σαλωμῶνος',NULL,'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  69, 19),
  ('sir', '德訓篇',       '德訓','Sirach',        'Ecclesiasticus', 'Σοφία Σιράχ',   NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  70, 51),
  ('bar', '巴錄書',       '巴', 'Baruch',         'Baruch',         'Βαρούχ',        NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  71,  5),
  ('epj', '耶利米書信',   '耶書','Letter of Jeremiah','Epistula Ieremiae','Ἐπιστολή Ἰερεμίου',NULL,'deutero',FALSE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,72,1),
  ('1ma', '馬加比一書',   '加上','1 Maccabees',   'I Macchabaeorum','Α Μακκαβαίων',  NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  73, 16),
  ('2ma', '馬加比二書',   '加下','2 Maccabees',   'II Macchabaeorum','Β Μακκαβαίων', NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  74, 15),
  ('3ma', '馬加比三書',   '加三','3 Maccabees',   'III Macchabaeorum','Γ Μακκαβαίων',NULL,'deutero', FALSE, FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 75,  7),
  ('4ma', '馬加比四書',   '加四','4 Maccabees',   'IV Macchabaeorum','Δ Μακκαβαίων',NULL,'deutero', FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, 76, 18),
  ('1es', '厄斯德拉一書', '厄一','1 Esdras',      'III Esdrae',     'Ἔσδρας Αʹ',     NULL, 'deutero', FALSE, FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 77,  9),
  ('2es', '厄斯德拉二書', '厄二','2 Esdras',      'IV Esdrae',      NULL,            NULL, 'deutero', FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, 78, 16),
  ('man', '默拿舍禱詞',   '默禱','Prayer of Manasseh','Oratio Manassae','Προσευχὴ Μανασσῆ',NULL,'deutero',FALSE,FALSE,TRUE,TRUE,FALSE,TRUE,TRUE,FALSE,79,1),
  ('ps2', '詩篇 151',     '詩151','Psalm 151',   'Psalmus CLI',    'Ψαλμὸς ΡΝΑʹ',  NULL, 'deutero', FALSE, FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, 80,  1),
  ('sus', '蘇撒納傳',     '蘇', 'Susanna',        'Susanna',        'Σωσάννα',       NULL, 'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  81,  1),
  ('bel', '比勒與大龍',   '比', 'Bel and the Dragon','Bel et Draco','Βὴλ καὶ Δράκων',NULL,'deutero', FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,  82,  1),
  ('aza', '阿撒里雅禱詞', '阿禱','Prayer of Azariah','Azariae Oratio','Προσευχὴ Ἀζαρίου',NULL,'deutero',FALSE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,83,1),

  -- ── 衣索匹亞 Tewahedo 獨有書卷（最廣 canon）─────────────────────────────
  ('jub', '禧年書',       '禧', 'Jubilees',       'Liber Iubilaeorum',NULL,          NULL, 'apocrypha', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, 84, 50),
  ('eno', '以諾一書',     '諾', '1 Enoch',        'Liber Enochi',   'Ἐνώχ',          NULL, 'apocrypha', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, 85, 108),
  ('4ba', '巴錄四書',     '巴四','4 Baruch',      'Paralipomena Ieremiae',NULL,     NULL, 'apocrypha', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, 86,  9)

ON CONFLICT (code) DO UPDATE
SET
  name_zh = EXCLUDED.name_zh,
  name_zh_short = EXCLUDED.name_zh_short,
  name_en = EXCLUDED.name_en,
  name_lat = EXCLUDED.name_lat,
  name_grc = EXCLUDED.name_grc,
  name_heb = EXCLUDED.name_heb,
  testament = EXCLUDED.testament,
  canon_protestant = EXCLUDED.canon_protestant,
  canon_catholic = EXCLUDED.canon_catholic,
  canon_orthodox = EXCLUDED.canon_orthodox,
  canon_ethiopian = EXCLUDED.canon_ethiopian,
  canon_syriac = EXCLUDED.canon_syriac,
  canon_armenian = EXCLUDED.canon_armenian,
  canon_coptic = EXCLUDED.canon_coptic,
  canon_assyrian = EXCLUDED.canon_assyrian,
  display_order = EXCLUDED.display_order,
  chapter_count = EXCLUDED.chapter_count;
