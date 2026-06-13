-- ============================================================================
-- 各教會傳統的「書卷排序」— 把次經/第二正典**併回該傳統原本的次序**（不再獨立分組），
-- 並標記哪些是該傳統的第二正典（UI 用綠色標註）。每傳統可覆寫 chapter_count
-- （如天主教但以理書 14 章 vs 新教 12 章）。
--   testament 為「該傳統的」分類（天主教把多俾亞/友弟德/智慧/德訓/巴路克歸 OT）。
--   未在本表的 canon（如 protestant / all）→ /scripture index 沿用 bible_books 既有
--   display_order + testament（新教本就無第二正典，無需併入）。
-- ============================================================================

CREATE TABLE IF NOT EXISTS bible_canon_books (
  canon          VARCHAR(20) NOT NULL,                       -- 'catholic' / 'orthodox' / ...
  book_code      VARCHAR(10) NOT NULL REFERENCES bible_books (code),
  testament      VARCHAR(10) NOT NULL,                       -- 'ot' | 'nt'（該傳統分類）
  sort_order     INT NOT NULL,                               -- 該傳統內排序
  is_deutero     BOOLEAN NOT NULL DEFAULT FALSE,             -- 該傳統視為第二正典 → 綠標
  chapter_count  INT,                                        -- 該傳統章數覆寫；NULL→用 bible_books
  PRIMARY KEY (canon, book_code)
);
CREATE INDEX IF NOT EXISTS bible_canon_books_canon ON bible_canon_books (canon, sort_order);

ALTER TABLE bible_canon_books ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "bible_canon_books_read" ON bible_canon_books;
CREATE POLICY "bible_canon_books_read" ON bible_canon_books FOR SELECT USING (true);

-- ── 天主教（思高／拉丁通行本次序；第二正典 7 卷 interleaved + 綠標；但 14 章）──────
-- 達尼爾增補（蘇撒納/貝耳與大龍/阿匝黎雅）與耶肋米亞書信在思高本併入 達/巴，
-- 故不列為獨立書卡（sus/bel/aza/epj 不入天主教排序）。
INSERT INTO bible_canon_books (canon, book_code, testament, sort_order, is_deutero, chapter_count) VALUES
  ('catholic','gen','ot', 1,false,NULL),('catholic','exo','ot', 2,false,NULL),
  ('catholic','lev','ot', 3,false,NULL),('catholic','num','ot', 4,false,NULL),
  ('catholic','deu','ot', 5,false,NULL),
  ('catholic','jos','ot', 6,false,NULL),('catholic','jdg','ot', 7,false,NULL),
  ('catholic','rut','ot', 8,false,NULL),('catholic','1sa','ot', 9,false,NULL),
  ('catholic','2sa','ot',10,false,NULL),('catholic','1ki','ot',11,false,NULL),
  ('catholic','2ki','ot',12,false,NULL),('catholic','1ch','ot',13,false,NULL),
  ('catholic','2ch','ot',14,false,NULL),('catholic','ezr','ot',15,false,NULL),
  ('catholic','neh','ot',16,false,NULL),
  ('catholic','tob','ot',17,true ,NULL),('catholic','jdt','ot',18,true ,NULL),
  ('catholic','est','ot',19,false,NULL),
  ('catholic','1ma','ot',20,true ,NULL),('catholic','2ma','ot',21,true ,NULL),
  ('catholic','job','ot',22,false,NULL),('catholic','psa','ot',23,false,150),
  ('catholic','pro','ot',24,false,NULL),('catholic','ecc','ot',25,false,NULL),
  ('catholic','sng','ot',26,false,NULL),
  ('catholic','wis','ot',27,true ,NULL),('catholic','sir','ot',28,true ,NULL),
  ('catholic','isa','ot',29,false,NULL),('catholic','jer','ot',30,false,NULL),
  ('catholic','lam','ot',31,false,NULL),('catholic','bar','ot',32,true ,6),
  ('catholic','ezk','ot',33,false,NULL),('catholic','dan','ot',34,false,14),
  ('catholic','hos','ot',35,false,NULL),('catholic','jol','ot',36,false,NULL),
  ('catholic','amo','ot',37,false,NULL),('catholic','oba','ot',38,false,NULL),
  ('catholic','jon','ot',39,false,NULL),('catholic','mic','ot',40,false,NULL),
  ('catholic','nam','ot',41,false,NULL),('catholic','hab','ot',42,false,NULL),
  ('catholic','zep','ot',43,false,NULL),('catholic','hag','ot',44,false,NULL),
  ('catholic','zec','ot',45,false,NULL),('catholic','mal','ot',46,false,NULL),
  ('catholic','mat','nt',47,false,NULL),('catholic','mrk','nt',48,false,NULL),
  ('catholic','luk','nt',49,false,NULL),('catholic','jhn','nt',50,false,NULL),
  ('catholic','act','nt',51,false,NULL),('catholic','rom','nt',52,false,NULL),
  ('catholic','1co','nt',53,false,NULL),('catholic','2co','nt',54,false,NULL),
  ('catholic','gal','nt',55,false,NULL),('catholic','eph','nt',56,false,NULL),
  ('catholic','php','nt',57,false,NULL),('catholic','col','nt',58,false,NULL),
  ('catholic','1th','nt',59,false,NULL),('catholic','2th','nt',60,false,NULL),
  ('catholic','1ti','nt',61,false,NULL),('catholic','2ti','nt',62,false,NULL),
  ('catholic','tit','nt',63,false,NULL),('catholic','phm','nt',64,false,NULL),
  ('catholic','heb','nt',65,false,NULL),('catholic','jas','nt',66,false,NULL),
  ('catholic','1pe','nt',67,false,NULL),('catholic','2pe','nt',68,false,NULL),
  ('catholic','1jn','nt',69,false,NULL),('catholic','2jn','nt',70,false,NULL),
  ('catholic','3jn','nt',71,false,NULL),('catholic','jud','nt',72,false,NULL),
  ('catholic','rev','nt',73,false,NULL)
ON CONFLICT (canon, book_code) DO UPDATE SET
  testament = EXCLUDED.testament, sort_order = EXCLUDED.sort_order,
  is_deutero = EXCLUDED.is_deutero, chapter_count = EXCLUDED.chapter_count;
