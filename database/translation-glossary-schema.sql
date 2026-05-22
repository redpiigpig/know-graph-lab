-- ============================================================================
-- 「神學家／神學名詞中譯對照」工具 (/translation-glossary)
--   theologians         — 教父／神學家基本資料 + 多傳統中譯 + 建議譯名
--   theological_terms   — 重要神學名詞 + 多傳統中譯 + 建議譯名
-- 七種傳統中譯欄位：新教 / 思高 / 東正教 / 香港 / 台灣 / 中國學界
-- ============================================================================

CREATE TABLE IF NOT EXISTS theologians (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 原文 / 拉丁化標準
  name_original            VARCHAR(160),               -- 希臘 Ἰουστῖνος / 拉丁 Augustinus / 敘利亞 / 希伯來
  name_original_lang       VARCHAR(20),                -- 'grc' / 'lat' / 'syc' / 'cop' / 'arm' / 'heb'
  name_latin_std           VARCHAR(160) NOT NULL,      -- 拉丁化標準名 Iustinus Martyr — lookup/sort key
  name_english             VARCHAR(160) NOT NULL,      -- 英文常用名 Justin Martyr

  -- 基本資料
  nationality              VARCHAR(80),                -- Samaria / Numidia / Cappadocia / Britain
  born_year                INT,                        -- 負數 = BC
  died_year                INT,
  century                  VARCHAR(20),                -- '2c' / '4c' / '4-5c'
  school                   VARCHAR(80),                -- 亞歷山大 / 安提阿 / 拉丁西方 / 加帕多家 / 經院
  role                     VARCHAR(40),                -- 使徒教父 / 護教士 / 教父 / 經院神學家

  -- 多傳統中譯（每欄可串多變體 用「；」分隔）
  name_protestant          VARCHAR(240),               -- 新教（華聯／證主／校園／改革宗）
  name_catholic_sgs        VARCHAR(240),               -- 思高（教廷／思高聖經學會）
  name_orthodox            VARCHAR(240),               -- 東正教（東亞主教教區）
  name_hk                  VARCHAR(240),               -- 香港（基文／道風）
  name_tw                  VARCHAR(240),               -- 台灣（光啟／輔大）
  name_china_academic      VARCHAR(240),               -- 中國學界

  -- 建議
  name_recommended         VARCHAR(160),
  recommendation_reason    TEXT,

  -- 元資料
  notes                    TEXT,
  sort_order               INT,                        -- 年代排序
  created_at               TIMESTAMPTZ DEFAULT now(),
  updated_at               TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS theologians_century ON theologians (century);
CREATE INDEX IF NOT EXISTS theologians_school ON theologians (school);
CREATE INDEX IF NOT EXISTS theologians_sort_order ON theologians (sort_order);
CREATE INDEX IF NOT EXISTS theologians_name_english_lower ON theologians (LOWER(name_english));

-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS theological_terms (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 原文 / 英文
  term_original            VARCHAR(160),               -- ὁμοούσιος / hypostasis / pneuma
  term_original_lang       VARCHAR(20),                -- grc / lat / heb / syc
  term_latin_translit      VARCHAR(160),               -- 'homoousios' 給檢索
  term_english             VARCHAR(200) NOT NULL,      -- 'consubstantial / of one substance'

  -- 分類
  category                 VARCHAR(60),                -- 三一論 / 基督論 / 救恩論 / 教會學 / 聖事 / 末世論 / 解經 / 制度
  era                      VARCHAR(40),                -- 使徒教父期 / 尼西亞前 / 尼西亞後 / 經院 / 宗教改革

  -- 多傳統中譯
  zh_protestant            VARCHAR(240),
  zh_catholic_sgs          VARCHAR(240),
  zh_orthodox              VARCHAR(240),
  zh_hk                    VARCHAR(240),
  zh_tw                    VARCHAR(240),
  zh_china_academic        VARCHAR(240),

  -- 建議
  zh_recommended           VARCHAR(200),
  recommendation_reason    TEXT,

  -- 元資料
  definition_zh            TEXT,
  notes                    TEXT,
  sort_order               INT,
  created_at               TIMESTAMPTZ DEFAULT now(),
  updated_at               TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS theological_terms_category ON theological_terms (category);
CREATE INDEX IF NOT EXISTS theological_terms_era ON theological_terms (era);
CREATE INDEX IF NOT EXISTS theological_terms_term_english_lower ON theological_terms (LOWER(term_english));
