-- ========================================================
-- Phase 7: 台灣全教派主教
-- ========================================================
-- 天主教: 台北總教區 + 高雄教區 + 台中教區 + 台南教區 + 嘉義教區 + 新竹教區 + 花蓮教區
-- 聖公宗: 台灣教區
-- 衛理公會: 台北年議會 (已完整 9 任)
-- ========================================================

-- Parent see IDs:
--   羅馬                : 3ed0e61a-fae8-4c80-a9b5-2b319caf2faf
--   日本聖公宗          : dc08b78f-6967-4e89-b200-eba101a924b0


-- =============================================
-- 天主教 7 個教區
-- =============================================

-- 台北總教區 (Archdiocese of Taipei) — 1952 升總主教區
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('台北總教區', 'Archdiocese of Taipei', '台北', '天主教', '羅馬公教', '拉丁禮', 1952, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣台北市',
 '1949 國共內戰後教廷將大陸數位主教遣台；1952 教廷宣布台北為總教區，原屬日本長崎教省脫離；中華民國天主教主教團駐節地。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('郭若石', 'Joseph Kuo Jo-shih', '台北', '天主教', 1, 1952, 1959, '正統', 'Annuario Pontificio', '首任台北總主教；1952 從上海來台'),
('田耕莘', 'Cardinal Thomas Tien Ken-sin', '台北', '天主教', 2, 1959, 1967, '正統', 'Annuario Pontificio', '聖言會會士；1946 升樞機（華人首位）；1959 任台北總主教；1967 逝世'),
('羅光', 'Stanislaus Lo Kuang', '台北', '天主教', 3, 1966, 1992, '正統', 'Annuario Pontificio；輔仁大學檔案', '前台南主教 1961-1966；1966 升台北總主教（與田耕莘期間部分重疊）；輔仁大學在台復校首任校長；天主教華人神學家'),
('狄剛', 'Joseph Ti-Kang', '台北', '天主教', 4, 1992, 2007, '正統', 'Annuario Pontificio', '前花蓮主教 1986-1989；1989 任台北 coadjutor；1992 接任正權總主教'),
('鄭再發', 'Joseph Cheng Tsai-fa', '台北', '天主教', 5, 2004, 2007, '正統', 'Annuario Pontificio', '前台南主教 1990-2004；2004 任 coadjutor；2007 退休'),
('洪山川', 'John Hung Shan-Chuan', '台北', '天主教', 6, 2007, 2020, '正統', 'Annuario Pontificio', '聖母聖心會會士；前嘉義主教 2003-2006；2007-2020 任台北總主教'),
('鍾安住', 'Thomas Chung An-zu', '台北', '天主教', 7, 2020, NULL, '正統', 'Annuario Pontificio', '前嘉義主教 2007-2020；2020 起任台北總主教；現任');


-- 高雄教區 (Diocese of Kaohsiung)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('高雄教區', 'Diocese of Kaohsiung', '高雄', '天主教', '羅馬公教', '拉丁禮', 1961, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣高雄市',
 '1961 從台南教區分出；高雄、屏東、澎湖管轄區；單國璽樞機任期內為台灣天主教國際對話重要時期。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('鄭天祥', 'Joseph Cheng Tien-shiang', '高雄', '天主教', 1, 1961, 1990, '正統', 'Annuario Pontificio', '首任高雄主教；29 年任期'),
('單國璽', 'Cardinal Paul Shan Kuo-hsi', '高雄', '天主教', 2, 1991, 2006, '正統', 'Annuario Pontificio；耶穌會檔案', '耶穌會士；前花蓮主教 1979-1991；1991 任高雄主教；1998 升樞機（華人第二位）；2008-2012 末期帶癌講道生命教育聞名'),
('劉振忠', 'Peter Liu Cheng-chung', '高雄', '天主教', 3, 2006, NULL, '正統', 'Annuario Pontificio', '本地台灣籍主教；2006 任高雄總主教（高雄 2003 升總教區）；現任');


-- 台中教區 (Diocese of Taichung)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('台中教區', 'Diocese of Taichung', '台中', '天主教', '羅馬公教', '拉丁禮', 1962, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣台中市',
 '1962 立教區；管轄台中市、彰化縣、南投縣；中部地區天主教中心。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('蔡文興', 'William Francis Kupfer', '台中', '天主教', 1, 1962, 1986, '正統', 'Annuario Pontificio', '美籍瑪利諾會士；首任台中主教；中文名「蔡文興」'),
('王愈榮', 'Joseph Wang Yu-jung', '台中', '天主教', 2, 1986, 2007, '正統', 'Annuario Pontificio', '前嘉義主教 1979-1986；1986 調台中'),
('蘇耀文', 'Martin Su Yao-wen', '台中', '天主教', 3, 2007, NULL, '正統', 'Annuario Pontificio', '本地台灣籍主教；現任');


-- 台南教區 (Diocese of Tainan)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('台南教區', 'Diocese of Tainan', '台南', '天主教', '羅馬公教', '拉丁禮', 1961, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣台南市',
 '1961 從台北教區分出；台南古都地區天主教中心；管轄台南市、嘉義縣市初期亦含。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('羅光', 'Stanislaus Lo Kuang', '台南', '天主教', 1, 1961, 1966, '正統', 'Annuario Pontificio', '首任台南主教；1966 升台北總主教'),
('成世光', 'Joseph Cheng Shih-kuang', '台南', '天主教', 2, 1966, 1990, '正統', 'Annuario Pontificio', '24 年任期；本地教會建設'),
('鄭再發', 'Joseph Cheng Tsai-fa', '台南', '天主教', 3, 1990, 2004, '正統', 'Annuario Pontificio', '2004 調台北任 coadjutor'),
('林吉男', 'Bosco Lin Ji-Nan', '台南', '天主教', 4, 2004, 2018, '正統', 'Annuario Pontificio', null),
('李若望', 'John Baptist Lee Jung-Funn', '台南', '天主教', 5, 2018, NULL, '正統', 'Annuario Pontificio', '現任；本地台灣籍');


-- 嘉義教區 (Diocese of Chiayi)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('嘉義教區', 'Diocese of Chiayi', '嘉義', '天主教', '羅馬公教', '拉丁禮', 1962, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣嘉義市',
 '1962 立教區；管轄嘉義市縣、雲林縣；中部南端地區天主教中心。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('牛會卿', 'Thomas Niu Hui-ching', '嘉義', '天主教', 1, 1962, 1979, '正統', 'Annuario Pontificio', '首任嘉義主教'),
('王愈榮', 'Joseph Wang Yu-jung', '嘉義', '天主教', 2, 1979, 1986, '正統', 'Annuario Pontificio', '後調台中'),
('林天助', 'Joseph Lin Tien-chu', '嘉義', '天主教', 3, 1986, 2003, '正統', 'Annuario Pontificio', null),
('洪山川', 'John Hung Shan-Chuan', '嘉義', '天主教', 4, 2003, 2006, '正統', 'Annuario Pontificio', '聖母聖心會；2007 升台北總主教'),
('鍾安住', 'Thomas Chung An-zu', '嘉義', '天主教', 5, 2007, 2020, '正統', 'Annuario Pontificio', '2020 升台北總主教'),
('浦英雄', 'John Baptist Pu Ying-hsiung', '嘉義', '天主教', 6, 2020, NULL, '正統', 'Annuario Pontificio', '現任；本地教會出身');


-- 新竹教區 (Diocese of Hsinchu)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('新竹教區', 'Diocese of Hsinchu', '新竹', '天主教', '羅馬公教', '拉丁禮', 1961, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣新竹市',
 '1961 立教區；管轄新竹、桃園、苗栗、宜蘭、金門、馬祖；北部西部地區天主教中心。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('杜寶晉', 'Paul Tu Pao-tsin', '新竹', '天主教', 1, 1961, 1986, '正統', 'Annuario Pontificio', '聖言會會士；首任新竹主教；25 年任期'),
('劉献堂', 'John Lawrence Liu Hsien-tang', '新竹', '天主教', 2, 1986, 2004, '正統', 'Annuario Pontificio', null),
('李克勉', 'Paul Lee Kuo-mien', '新竹', '天主教', 3, 2004, 2024, '正統', 'Annuario Pontificio', '本地教會出身；20 年任期'),
('李若望', 'John Baptist Lee Jung-Funn', '新竹', '天主教', 4, 2024, NULL, '正統', 'Annuario Pontificio', '兼任，現任');


-- 花蓮教區 (Diocese of Hualien)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('花蓮教區', 'Diocese of Hualien', '花蓮', '天主教', '羅馬公教', '拉丁禮', 1952, '現存', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '台灣花蓮縣',
 '1952 立宗座代牧區，1963 升正式教區；管轄花蓮縣、台東縣；台灣原住民教會大本營，原住民信徒比例最高。', '中華民國天主教主教團；Annuario Pontificio');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('費聲遠', 'André-Jean Vérineux', '花蓮', '天主教', 1, 1952, 1973, '正統', 'Annuario Pontificio；瑪利諾會檔案', '法國瑪利諾會士；首任花蓮代牧、1963 升正權主教；20 年原住民傳教先驅'),
('賈彥文', 'Joseph Chia Yan-wen', '花蓮', '天主教', 2, 1973, 1979, '正統', 'Annuario Pontificio', '後調嘉義 1979-1986'),
('單國璽', 'Cardinal Paul Shan Kuo-hsi', '花蓮', '天主教', 3, 1979, 1991, '正統', 'Annuario Pontificio', '耶穌會士；後調高雄'),
('狄剛', 'Joseph Ti-Kang', '花蓮', '天主教', 4, 1986, 1989, '正統', 'Annuario Pontificio', '後調台北 coadjutor'),
('黃兆明', 'Philip Huang Chao-ming', '花蓮', '天主教', 5, 2001, 2025, '正統', 'Annuario Pontificio', '本地原住民出身主教；24 年任期；2025 退休'),
('卓世益', 'Daniel Cho Shih-yi', '花蓮', '天主教', 6, 2025, NULL, '正統', 'Annuario Pontificio', '現任');


-- =============================================
-- 聖公宗 台灣教區
-- =============================================

-- 台灣聖公會 — 1954 立宗座代牧、1965 立教區；屬美國聖公會第 8 教省
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, location, notes, sources) VALUES
('台灣聖公會教區', 'Episcopal Diocese of Taiwan', '台灣（聖公宗）', '台灣聖公會', '基督新教', '英國國教禮', 1965, '現存', '526e7e6e-70d0-47f2-8553-8e9ebb1c4ef7',
 '台灣台北市',
 '1954 由美國聖公會立宗座代牧；1965 升教區；現屬美國聖公會第 8 教省 (Province VIII / Pacific)；台灣聖公會主教座設於台北和平基督教會。', '台灣聖公會檔案；ECUSA Archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('龐德明', 'James C.L. Pong', '台灣（聖公宗）', '台灣聖公會', 1, 1965, 1971, '正統', '台灣聖公會檔案', '首任台灣教區主教；中華人；前美國 ECUSA 神職轉任'),
('鄭克勤', 'Pui-Yeung Cheung', '台灣（聖公宗）', '台灣聖公會', 2, 1971, 1988, '正統', '台灣聖公會檔案', null),
('賴榮信', 'David Jung-Hsin Lai', '台灣（聖公宗）', '台灣聖公會', 3, 1988, 2000, '正統', '台灣聖公會檔案', '本地台灣籍主教；任內推動教會本地化'),
('賴俊明', 'John Jung-Ming Lai', '台灣（聖公宗）', '台灣聖公會', 4, 2001, 2014, '正統', '台灣聖公會檔案', '13 年任期'),
('張員榮', 'David J.H. Lai', '台灣（聖公宗）', '台灣聖公會', 5, 2014, NULL, '正統', '台灣聖公會檔案', '現任；前 archdeacon');
