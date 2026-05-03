-- ═══════════════════════════════════════════════════════════════════════════
-- 龐君華會督數位典藏 — Supabase 資料表 DDL
-- 建立時間：2026-04-26
-- 說明：所有 pong_* 表與主站 articles/issues 等完全分離，不互相 JOIN
-- ═══════════════════════════════════════════════════════════════════════════


-- ── 1. 訪談與演講 ────────────────────────────────────────────────────────────
-- 儲存影音訪談、廣播節目、公開演講的 metadata 及逐字稿
-- YouTube 可用 youtube_id 內嵌播放；podcast/廣播用 audio_url 或外連 url

CREATE TABLE pong_media (
  id            SERIAL PRIMARY KEY,
  title         TEXT NOT NULL,
  title_en      TEXT,
  source        TEXT,                  -- 來源機構，例如「救恩之聲」
  source_en     TEXT,                  -- 來源英文名，例如「Voice of Salvation」
  program_name  TEXT,                  -- 節目名稱，例如「雲彩飛揚」
  program_en    TEXT,                  -- 節目英文名
  interviewer   TEXT,                  -- 主持人 / 訪問者
  media_type    TEXT NOT NULL          -- 'interview' | 'talk' | 'sermon_audio' | 'documentary'
                  DEFAULT 'interview',
  platform      TEXT NOT NULL          -- 'youtube' | 'podcast' | 'broadcast' | 'other'
                  DEFAULT 'youtube',
  youtube_id    TEXT,                  -- YouTube 影片 ID（例如 zmILDCQePLk）
  youtube_start INTEGER,               -- 開始秒數（對應 ?t= 參數，例如 2260）
  audio_url     TEXT,                  -- 廣播 / podcast 音檔 URL（非 YouTube 時用）
  url           TEXT,                  -- 原始連結
  broadcast_date DATE,                 -- 播出 / 錄製日期
  duration_sec  INTEGER,               -- 時長（秒）
  transcript    TEXT,                  -- 逐字稿（純文字）
  description   TEXT,                  -- 節目簡介
  thumbnail_url TEXT,                  -- 縮圖（留空則前端自動用 YouTube 縮圖）
  tags          TEXT[]  DEFAULT '{}',  -- 自由標籤，例如 '{生命故事,信仰見證}'
  is_published  BOOLEAN DEFAULT true,
  sort_order    INTEGER DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE  pong_media IS '訪談與演講：影音 metadata + 逐字稿';
COMMENT ON COLUMN pong_media.youtube_id    IS 'YouTube 影片 ID，配合 https://www.youtube.com/embed/{id}?start={start} 內嵌';
COMMENT ON COLUMN pong_media.youtube_start IS '影片開始秒數（URL ?t= 的值）';


-- ── 2. 講道集 ─────────────────────────────────────────────────────────────────
-- 依教會年（church_year = Advent 起始年，例如 2000 代表 2000-2001 教會年）

CREATE TABLE pong_sermons (
  id               SERIAL PRIMARY KEY,
  title            TEXT,                 -- 講道標題（可空，部分資料無題）
  title_en         TEXT,
  scripture_ref    TEXT,                 -- 主題經文，例如「哥林多後書 4:5」
  church_year      SMALLINT NOT NULL,    -- Advent 起始年，2000–2025
  liturgical_season TEXT NOT NULL        -- 'advent'|'christmas'|'epiphany'|'lent'|'easter'|'pentecost'
                     DEFAULT 'pentecost',
  sermon_date      DATE,                 -- 講道日期
  occasion         TEXT,                 -- 場合，例如「主日崇拜」「退修會」「奮興會」
  location         TEXT,                 -- 地點，例如「成中教會」
  media_id         INTEGER REFERENCES pong_media(id) ON DELETE SET NULL,
  content          TEXT,                 -- 講道全文（HTML 或純文字）
  footnotes        JSONB   DEFAULT '[]', -- 腳注（沿用主站格式 [{id,text}]）
  has_recording    BOOLEAN DEFAULT false,
  is_published     BOOLEAN DEFAULT true,
  sort_order       INTEGER DEFAULT 0,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE  pong_sermons IS '講道集：依教會年與節期組織';
COMMENT ON COLUMN pong_sermons.church_year IS 'Advent 起始年，例如 2000 = 2000-2001 教會年';


-- ── 3. 著作與專文 ─────────────────────────────────────────────────────────────

CREATE TABLE pong_writings (
  id               SERIAL PRIMARY KEY,
  title            TEXT NOT NULL,
  title_en         TEXT,
  category         TEXT NOT NULL          -- 'book'|'book_chapter'|'essay'|'column'|'devotional'|'other'
                     DEFAULT 'essay',
  publication      TEXT,                  -- 發表刊物 / 書名
  publication_en   TEXT,
  published_date   DATE,
  date_approximate BOOLEAN DEFAULT false, -- 日期為估計值時標記
  content          TEXT,                  -- 全文
  footnotes        JSONB   DEFAULT '[]',
  source_url       TEXT,                  -- 原始連結（如有）
  cloudinary_urls  TEXT[]  DEFAULT '{}',  -- 掃描圖片（如為手抄/剪報）
  tags             TEXT[]  DEFAULT '{}',
  is_published     BOOLEAN DEFAULT true,
  sort_order       INTEGER DEFAULT 0,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE pong_writings IS '著作與專文：書章、論文、專欄、靈修文章';


-- ── 4. 手稿與書信 ─────────────────────────────────────────────────────────────

CREATE TABLE pong_manuscripts (
  id               SERIAL PRIMARY KEY,
  title            TEXT,                  -- 標題（可空，書信常以摘要替代）
  ms_type          TEXT NOT NULL          -- 'handwritten'|'letter'|'annotation'|'note'|'other'
                     DEFAULT 'handwritten',
  correspondent    TEXT,                  -- 書信對象（寄給誰 / 誰寄來）
  ms_date          DATE,                  -- 文件日期
  date_approximate BOOLEAN DEFAULT false,
  description      TEXT,                  -- 內容簡介
  transcript       TEXT,                  -- 文字轉錄（手寫稿）
  cloudinary_urls  TEXT[]  DEFAULT '{}',  -- 掃描圖片 URL 陣列（依頁序排列）
  tags             TEXT[]  DEFAULT '{}',
  is_published     BOOLEAN DEFAULT true,
  sort_order       INTEGER DEFAULT 0,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE pong_manuscripts IS '手稿與書信：親筆原稿掃描及文字轉錄';


-- ── 5. 三讀三禱（Daily Office） ───────────────────────────────────────────────

CREATE TABLE pong_daily_office (
  id           SERIAL PRIMARY KEY,
  entry_date   DATE NOT NULL UNIQUE,   -- 日期（每天一筆）
  -- 三段讀經 + 禱文
  reading_1    TEXT,                   -- 第一段讀經正文
  ref_1        TEXT,                   -- 第一段出處，例如「詩篇 23:1-6」
  prayer_1     TEXT,                   -- 第一段禱文
  reading_2    TEXT,
  ref_2        TEXT,
  prayer_2     TEXT,
  reading_3    TEXT,
  ref_3        TEXT,
  prayer_3     TEXT,
  notes        TEXT,                   -- 附注 / 日記式的個人反省
  is_published BOOLEAN DEFAULT true,
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE pong_daily_office IS '三讀三禱：龐會督日課讀經靈修反省';


-- ── 6. 照片錦集 ───────────────────────────────────────────────────────────────

CREATE TABLE pong_photos (
  id               SERIAL PRIMARY KEY,
  caption          TEXT,                  -- 圖說（中文）
  caption_en       TEXT,                  -- 圖說（英文）
  photo_date       DATE,
  date_approximate BOOLEAN DEFAULT false,
  occasion         TEXT,                  -- 場合，例如「就任禮拜」「退修會」
  location         TEXT,
  cloudinary_url   TEXT NOT NULL,         -- 主圖 URL
  cloudinary_id    TEXT,                  -- Cloudinary public_id（刪除 / 改名用）
  album_tag        TEXT,                  -- 相簿分類，例如「ministry」「ordination」「family」
  tags             TEXT[]  DEFAULT '{}',
  sort_order       INTEGER DEFAULT 0,
  is_published     BOOLEAN DEFAULT true,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE pong_photos IS '照片錦集：龐會督歷年影像';


-- ── 7. 回憶與緬懷 ─────────────────────────────────────────────────────────────

CREATE TABLE pong_remembrance (
  id                  SERIAL PRIMARY KEY,
  title               TEXT NOT NULL,
  author              TEXT,              -- 撰文者
  author_relationship TEXT,              -- 與龐會督的關係，例如「門生」「同工」「家屬」
  content_type        TEXT NOT NULL      -- 'memoir'|'eulogy'|'research'|'tribute'
                        DEFAULT 'tribute',
  published_date      DATE,
  publication         TEXT,              -- 刊登刊物（如有）
  content             TEXT,              -- 全文
  footnotes           JSONB DEFAULT '[]',
  media_id            INTEGER REFERENCES pong_media(id) ON DELETE SET NULL,
  is_published        BOOLEAN DEFAULT true,
  sort_order          INTEGER DEFAULT 0,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE pong_remembrance IS '回憶與緬懷：訪談錄、回憶錄、悼詞、研究文章';


-- ═══════════════════════════════════════════════════════════════════════════
-- Row Level Security（RLS）
-- 公開瀏覽者（anon）只能讀 is_published = true 的資料
-- 已登入管理員（authenticated）完整存取
-- ═══════════════════════════════════════════════════════════════════════════

-- 啟用 RLS
ALTER TABLE pong_media        ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_sermons      ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_writings     ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_manuscripts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_daily_office ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_photos       ENABLE ROW LEVEL SECURITY;
ALTER TABLE pong_remembrance  ENABLE ROW LEVEL SECURITY;

-- pong_media
CREATE POLICY "anon read published media"   ON pong_media        FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access media"      ON pong_media        FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_sermons
CREATE POLICY "anon read published sermons" ON pong_sermons      FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access sermons"    ON pong_sermons      FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_writings
CREATE POLICY "anon read published writings" ON pong_writings    FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access writings"    ON pong_writings    FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_manuscripts
CREATE POLICY "anon read published ms"      ON pong_manuscripts  FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access ms"         ON pong_manuscripts  FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_daily_office
CREATE POLICY "anon read published daily"   ON pong_daily_office FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access daily"      ON pong_daily_office FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_photos
CREATE POLICY "anon read published photos"  ON pong_photos       FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access photos"     ON pong_photos       FOR ALL    TO authenticated USING (true) WITH CHECK (true);

-- pong_remembrance
CREATE POLICY "anon read published rem"     ON pong_remembrance  FOR SELECT TO anon        USING (is_published = true);
CREATE POLICY "auth full access rem"        ON pong_remembrance  FOR ALL    TO authenticated USING (true) WITH CHECK (true);


-- ═══════════════════════════════════════════════════════════════════════════
-- 索引（查詢效能）
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX idx_pong_media_broadcast_date  ON pong_media        (broadcast_date DESC);
CREATE INDEX idx_pong_media_youtube_id      ON pong_media        (youtube_id) WHERE youtube_id IS NOT NULL;
CREATE INDEX idx_pong_sermons_church_year   ON pong_sermons      (church_year, liturgical_season);
CREATE INDEX idx_pong_sermons_date          ON pong_sermons      (sermon_date DESC);
CREATE INDEX idx_pong_writings_date         ON pong_writings     (published_date DESC);
CREATE INDEX idx_pong_manuscripts_date      ON pong_manuscripts  (ms_date DESC);
CREATE INDEX idx_pong_daily_office_date     ON pong_daily_office (entry_date DESC);
CREATE INDEX idx_pong_photos_date           ON pong_photos       (photo_date DESC);
CREATE INDEX idx_pong_photos_album          ON pong_photos       (album_tag);
CREATE INDEX idx_pong_remembrance_date      ON pong_remembrance  (published_date DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- 種子資料：第一筆 pong_media（救恩之聲訪談，2026-01-25）
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO pong_media (
  title, title_en,
  source, source_en,
  program_name, program_en,
  interviewer,
  media_type, platform,
  youtube_id, youtube_start,
  url,
  broadcast_date,
  description,
  tags
) VALUES (
  '龐君華牧師——生命故事',
  'Pastor Pong Kwan-wah — Life Story',
  '救恩之聲',
  'Voice of Salvation',
  '雲彩飛揚生命故事集',
  'The Story of Life',
  'Luca',
  'interview',
  'youtube',
  'zmILDCQePLk',
  2260,
  'https://www.youtube.com/watch?v=zmILDCQePLk&t=2260s',
  '2026-01-25',
  '龐會督錄製完本集節目後兩週蒙主恩召。訪談涵蓋其童年於香港與台灣的成長、信仰啟蒙、決志、全職服侍歷程，以及 2013 年中風後的靈命轉化。',
  '{生命故事,信仰見證,救恩之聲,雲彩飛揚}'
);
