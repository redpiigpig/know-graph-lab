-- ================================================================
-- 出埃及記至申命記族譜人物
-- 包含：創46章雅各子孫、出6章利未族譜、民13章探子、民26-27章
-- 代數基準：亞當=1 … 亞伯拉罕=20 … 雅各=22 … 雅各之子=23
-- 注意：此腳本只能執行一次，重複執行會產生重複記錄
-- ================================================================

-- 防止重複執行
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM biblical_people WHERE sort_order = 214) THEN
    RAISE EXCEPTION '此 seed 已執行過 (sort_order 214 已存在)，中止以防止重複資料。';
  END IF;
END $$;

-- ──────────────────────────────────────────────────────────────
-- 第一節：雅各的子孫（創 46章；出 1:1-5）
--   雅各之子=第23代；其子=第24代
-- ──────────────────────────────────────────────────────────────

-- 更新雅各各子的 children 欄位（補齊各支派宗族名）
UPDATE biblical_people SET children = '哈諾各、法路、希斯崙（流便之子）、迦米'
  WHERE name_zh = '流便';
UPDATE biblical_people SET children = '耶母利、雅憫、俄哈得、雅斤、瑣轄、掃羅（西緬之子）'
  WHERE name_zh = '西緬';
UPDATE biblical_people SET children = '革順、哥轄、米拉利'
  WHERE name_zh = '利未';
UPDATE biblical_people SET children = '珥（猶大之子）、俄南（猶大之子）、示拉（猶大之子）、法勒斯、謝拉（猶大之子）'
  WHERE name_zh = '猶大';
UPDATE biblical_people SET children = '陀拉、普瓦、雅書比、伸崙'
  WHERE name_zh = '以薩迦';
UPDATE biblical_people SET children = '西烈、以倫（西布倫之子）、雅利勒'
  WHERE name_zh = '西布倫';
UPDATE biblical_people SET children = '瑪拿西、以法蓮'
  WHERE name_zh = '約瑟';
UPDATE biblical_people SET children = '比拉（便雅憫之子）、比結（便雅憫之子）、亞實別、基拉（便雅憫之子）、拿艾、亞希、羅示、母辟、戶平、亞珥得'
  WHERE name_zh = '便雅憫';
UPDATE biblical_people SET children = '戶心（但之子）'
  WHERE name_zh = '但';
UPDATE biblical_people SET children = '音拿、亦施瓦、比利亞（亞設之子）、西拉（亞設之女）'
  WHERE name_zh = '亞設';
UPDATE biblical_people SET children = '雅薛、沽尼、以謝（拿弗他利之子）、示稜'
  WHERE name_zh = '拿弗他利';
UPDATE biblical_people SET children = '洗奉、哈基、書尼、以斯本（迦得之子）、以利（迦得之子）、亞羅德、亞列利'
  WHERE name_zh = '迦得';

-- ── 流便之子（創 46:9；出 6:14；民 26:5-11）────────────────────
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('哈諾各（流便之子）', 'Hanoch son of Reuben', '男', NULL, '創世記 46:9; 出埃及記 6:14; 民數記 26:5', NULL, 24, 214),
('法路', 'Pallu', '男', '以利押', '創世記 46:9; 出埃及記 6:14; 民數記 26:5,8', NULL, 24, 215),
('希斯崙（流便之子）', 'Hezron son of Reuben', '男', NULL, '創世記 46:9; 出埃及記 6:14; 民數記 26:6', NULL, 24, 216),
('迦米（流便之子）', 'Carmi son of Reuben', '男', NULL, '創世記 46:9; 出埃及記 6:14; 民數記 26:6', NULL, 24, 217);

-- 法路之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('以利押（法路之子）', 'Eliab son of Pallu', '男', '民數記 26:8-9; 民數記 16:1', '大坍、亞比蘭、以羅之父', 25, 218);

UPDATE biblical_people SET children = '以利押（法路之子）' WHERE name_zh = '法路';

-- 以利押之子（在可拉事件中被吞滅）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('大坍', 'Dathan', '男', '民數記 16:1,12,24-27; 申命記 11:6', '參與可拉叛亂，被地吞滅', 26, 219),
('亞比蘭（流便後裔）', 'Abiram son of Eliab', '男', '民數記 16:1,12,24-27; 申命記 11:6', '參與可拉叛亂，被地吞滅', 26, 220),
('以羅', 'On son of Peleth', '男', '民數記 16:1', '參與可拉叛亂', 26, 221);

UPDATE biblical_people SET children = '大坍、亞比蘭（流便後裔）、以羅' WHERE name_zh = '以利押（法路之子）';

-- ── 西緬之子（創 46:10；出 6:15；民 26:12-14）──────────────────
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('耶母利', 'Jemuel', '男', '創世記 46:10; 出埃及記 6:15', '民 26:12 作「尼母利」', 24, 222),
('雅憫（西緬之子）', 'Jamin son of Simeon', '男', '創世記 46:10; 出埃及記 6:15; 民數記 26:12', NULL, 24, 223),
('俄哈得', 'Ohad', '男', '創世記 46:10; 出埃及記 6:15', '民數記 26章未列，可能早逝', 24, 224),
('雅斤（西緬之子）', 'Jachin son of Simeon', '男', '創世記 46:10; 出埃及記 6:15; 民數記 26:12', NULL, 24, 225),
('瑣轄（西緬之子）', 'Zohar son of Simeon', '男', '創世記 46:10; 出埃及記 6:15', '民 26:13 作「謝拉」', 24, 226),
('掃羅（西緬之子）', 'Shaul son of Simeon', '男', '創世記 46:10; 出埃及記 6:15; 民數記 26:13', '迦南女人所生', 24, 227);

-- ── 利未之子（創 46:11；出 6:16-19；民 26:57-62）───────────────
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('革順（利未之子）', 'Gershon son of Levi', '男', '利比尼（革順之子）、示每（革順之子）', '創世記 46:11; 出埃及記 6:16-17; 民數記 3:17-21; 26:57', '又作革雄', 24, 228),
('哥轄', 'Kohath', '男', '暗蘭、以斯哈、希伯崙（哥轄之子）、烏薛', '創世記 46:11; 出埃及記 6:16,18; 民數記 3:17-19; 26:57-58', '摩西與亞倫之祖父', 24, 229),
('米拉利（利未之子）', 'Merari son of Levi', '男', '瑪利（米拉利之子）、母示', '創世記 46:11; 出埃及記 6:16,19; 民數記 3:17,20; 26:57', NULL, 24, 230);

UPDATE biblical_people SET children = '革順（利未之子）、哥轄、米拉利（利未之子）' WHERE name_zh = '利未';

-- 革順之子（出 6:17；民 3:18,21）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('利比尼（革順之子）', 'Libni son of Gershon', '男', '出埃及記 6:17; 民數記 3:18,21; 26:58', NULL, 25, 231),
('示每（革順之子）', 'Shimei son of Gershon', '男', '出埃及記 6:17; 民數記 3:18,21', NULL, 25, 232);

-- 哥轄之子（出 6:18；民 3:19,27；26:58）
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('暗蘭', 'Amram', '男', '亞倫、摩西、米利暗', '出埃及記 6:18,20; 民數記 3:19,27; 26:58-59', '娶姑母約基別為妻', 25, 233),
('以斯哈', 'Izhar', '男', '可拉（以斯哈之子）、尼法、細基利', '出埃及記 6:18,21; 民數記 3:19,27; 16:1', NULL, 25, 234),
('希伯崙（哥轄之子）', 'Hebron son of Kohath', '男', NULL, '出埃及記 6:18; 民數記 3:19,27', NULL, 25, 235),
('烏薛', 'Uzziel', '男', '米沙利（烏薛之子）、以利撒反、西斯利', '出埃及記 6:18,22; 民數記 3:19,27', NULL, 25, 236);

-- 米拉利之子（出 6:19；民 3:20,33）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('瑪利（米拉利之子）', 'Mahli son of Merari', '男', '出埃及記 6:19; 民數記 3:20,33; 26:58', NULL, 25, 237),
('母示', 'Mushi', '男', '出埃及記 6:19; 民數記 3:20,33; 26:58', NULL, 25, 238);

-- ── 暗蘭的家族（出 6:20；民 26:59）─────────────────────────────
INSERT INTO biblical_people (name_zh, name_en, gender, spouse, sources, notes, generation, sort_order) VALUES
('約基別', 'Jochebed', '女', '暗蘭', '出埃及記 6:20; 民數記 26:59', '利未之女（或後裔），嫁給侄兒暗蘭；摩西、亞倫、米利暗之母', 24, 239);

INSERT INTO biblical_people (name_zh, name_en, gender, spouse, children, sources, notes, generation, sort_order) VALUES
('亞倫', 'Aaron', '男', '以利沙巴', '拿答、亞比戶、以利亞撒、以他瑪', '出埃及記 6:20,23; 7:7; 民數記 26:59-60', '摩西之兄，以色列首位大祭司', 26, 240),
('摩西', 'Moses', '男', '西坡拉', '革舜（摩西之子）、以利以謝（摩西之子）', '出埃及記 2:1-2; 6:20; 申命記 34:5-7', '以色列民族領袖，帶領出埃及，享壽120歲', 26, 241),
('米利暗', 'Miriam', '女', NULL, NULL, '出埃及記 15:20-21; 民數記 12:1-15; 20:1', '女先知，摩西與亞倫之姊，在加低斯死亡', 26, 242);

-- 亞倫之妻（出 6:23）
INSERT INTO biblical_people (name_zh, name_en, gender, spouse, sources, notes, generation, sort_order) VALUES
('以利沙巴', 'Elisheba', '女', '亞倫', '出埃及記 6:23', '亞米拿達之女，拿順之妹', 26, 243);

-- 亞倫之子（出 6:23；利 10:1-2；民 3:2-4）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('拿答', 'Nadab', '男', '利未記 10:1-2; 民數記 3:2-4; 26:61', '亞倫長子，獻凡火被耶和華擊殺，無子', 27, 244),
('亞比戶', 'Abihu', '男', '利未記 10:1-2; 民數記 3:2-4; 26:61', '亞倫次子，與拿答同獻凡火被擊殺，無子', 27, 245),
('以利亞撒', 'Eleazar', '男', '民數記 3:2-4; 20:25-28; 26:1; 約書亞記 24:33', '亞倫三子，繼父為大祭司', 27, 246),
('以他瑪', 'Ithamar', '男', '出埃及記 6:23; 民數記 3:2-4; 4:28,33', '亞倫四子，負責監管幕布等物', 27, 247);

-- 以利亞撒之子（出 6:25；民 25:7-13）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('非尼哈', 'Phinehas', '男', '出埃及記 6:25; 民數記 25:7-13; 31:6', '以利亞撒之子，因熱心維護聖約刺殺行淫者，神與他立平安之約', 28, 248);

INSERT INTO biblical_people (name_zh, name_en, gender, spouse, sources, notes, generation, sort_order) VALUES
('普提的女兒', 'Daughter of Putiel', '女', '以利亞撒', '出埃及記 6:25', '普提的女兒，以利亞撒之妻，非尼哈之母', 27, 249);

-- 以斯哈之子（出 6:21；民 16:1）
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('可拉（以斯哈之子）', 'Korah son of Izhar', '男', '亞西、以利加拿（可拉之子）、亞比亞撒', '出埃及記 6:21,24; 民數記 16:1,32; 26:11', '領導叛亂，被地吞滅；其子未死（民 26:11）', 26, 250),
('尼法（以斯哈之子）', 'Nepheg son of Izhar', '男', NULL, '出埃及記 6:21', NULL, 26, 251),
('細基利', 'Zichri', '男', NULL, '出埃及記 6:21', NULL, 26, 252);

-- 可拉之子（出 6:24；民 26:11）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('亞西（可拉之子）', 'Assir son of Korah', '男', '出埃及記 6:24; 民數記 26:11', '可拉之子，未隨父受審判', 27, 253),
('以利加拿（可拉之子）', 'Elkanah son of Korah', '男', '出埃及記 6:24; 民數記 26:11', NULL, 27, 254),
('亞比亞撒', 'Abiasaph', '男', '出埃及記 6:24; 民數記 26:11', NULL, 27, 255);

-- 烏薛之子（出 6:22）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('米沙利（烏薛之子）', 'Mishael son of Uzziel', '男', '出埃及記 6:22; 利未記 10:4', '搬運拿答亞比戶的屍體', 26, 256),
('以利撒反', 'Elzaphan', '男', '出埃及記 6:22; 利未記 10:4; 民數記 3:30', '烏薛長子，哥轄族宗族長', 26, 257),
('西斯利', 'Sithri', '男', '出埃及記 6:22', NULL, 26, 258);

-- ── 摩西的家族（出 2:21-22；18:3-4）────────────────────────────
INSERT INTO biblical_people (name_zh, name_en, gender, spouse, children, sources, notes, generation, sort_order) VALUES
('西坡拉', 'Zipporah', '女', '摩西', '革舜（摩西之子）、以利以謝（摩西之子）', '出埃及記 2:21-22; 4:24-26; 18:2-5', '米甸祭司葉忒羅之女，摩西之妻', 26, 259);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('葉忒羅', 'Jethro', '男', '西坡拉', '出埃及記 3:1; 18:1-12', '米甸祭司，摩西岳父，又名流珥（出 2:18）', 26, 260);

INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('革舜（摩西之子）', 'Gershom son of Moses', '男', '出埃及記 2:22; 18:3', '摩西長子，名意「我在異鄉作了寄居的」', 27, 261),
('以利以謝（摩西之子）', 'Eliezer son of Moses', '男', '出埃及記 18:4; 歷代志上 23:15-17', '摩西次子，名意「我父的神幫助我」', 27, 262);

-- ──────────────────────────────────────────────────────────────
-- 第二節：猶大支派族譜（創 38, 46:12；民 26:19-22）
-- ──────────────────────────────────────────────────────────────

INSERT INTO biblical_people (name_zh, name_en, gender, spouse, sources, notes, generation, sort_order) VALUES
('他瑪', 'Tamar', '女', '猶大', '創世記 38:6-30; 路得記 4:12; 歷代志上 2:4', '猶大長媳，先嫁珥後嫁俄南；假扮妓女生法勒斯與謝拉', 24, 263);

INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('珥（猶大之子）', 'Er son of Judah', '男', '創世記 38:3,6-7; 民數記 26:19', '猶大長子，在耶和華眼中是惡人被擊殺，無後', 24, 264),
('俄南（猶大之子）', 'Onan son of Judah', '男', '創世記 38:4,8-10; 民數記 26:19', '猶大次子，不盡兄終弟及之責被擊殺，無後', 24, 265),
('示拉（猶大之子）', 'Shelah son of Judah', '男', '創世記 38:5,11,14,26; 民數記 26:20', '猶大三子，亞杜蘭人所生', 24, 266),
('謝拉（猶大之子）', 'Zerah son of Judah', '男', '創世記 38:30; 46:12; 民數記 26:20; 歷代志上 2:4', '他瑪所生，出生時手上有紅線', 24, 268);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('法勒斯', 'Perez', '男', '希斯崙（法勒斯之子）、哈母勒', '創世記 38:29; 46:12; 路得記 4:18; 民數記 26:20-21; 歷代志上 2:4-5', '他瑪所生，是大衛王及彌賽亞祖先之一', 24, 267);

-- 法勒斯之子（創 46:12；民 26:21；路 4:18）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('希斯崙（法勒斯之子）', 'Hezron son of Perez', '男', '創世記 46:12; 民數記 26:21; 路得記 4:18-19; 歷代志上 2:5,9', '大衛王族譜中的重要先祖', 25, 269),
('哈母勒', 'Hamul', '男', '創世記 46:12; 民數記 26:21; 歷代志上 2:5', NULL, 25, 270);

UPDATE biblical_people SET children = '法勒斯、謝拉（猶大之子）' WHERE name_zh = '猶大'
  AND (children IS NULL OR children NOT LIKE '%法勒斯%');

-- ──────────────────────────────────────────────────────────────
-- 第三節：其他支派之子（創 46；民 26）
-- ──────────────────────────────────────────────────────────────

-- 以薩迦之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('陀拉（以薩迦之子）', 'Tola son of Issachar', '男', '創世記 46:13; 民數記 26:23', NULL, 24, 271),
('普瓦', 'Puah', '男', '創世記 46:13; 民數記 26:23', '又作「法瓦」', 24, 272),
('雅書比', 'Jashub', '男', '創世記 46:13; 民數記 26:24', '創 46:13 作「約」', 24, 273),
('伸崙（以薩迦之子）', 'Shimron son of Issachar', '男', '創世記 46:13; 民數記 26:24', NULL, 24, 274);

-- 西布倫之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('西烈（西布倫之子）', 'Sered son of Zebulun', '男', '創世記 46:14; 民數記 26:26', NULL, 24, 275),
('以倫（西布倫之子）', 'Elon son of Zebulun', '男', '創世記 46:14; 民數記 26:26', NULL, 24, 276),
('雅利勒', 'Jahleel', '男', '創世記 46:14; 民數記 26:27', NULL, 24, 277);

-- 迦得之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('洗奉（迦得之子）', 'Zephon son of Gad', '男', '創世記 46:16; 民數記 26:15', '創 46:16 作「洗非云」', 24, 278),
('哈基', 'Haggi', '男', '創世記 46:16; 民數記 26:15', NULL, 24, 279),
('書尼（迦得之子）', 'Shuni son of Gad', '男', '創世記 46:16; 民數記 26:15', NULL, 24, 280),
('以斯本（迦得之子）', 'Ezbon son of Gad', '男', '創世記 46:16; 民數記 26:16', '民 26:16 作「阿斯尼」', 24, 281),
('以利（迦得之子）', 'Eri son of Gad', '男', '創世記 46:16; 民數記 26:16', NULL, 24, 282),
('亞羅德', 'Arod', '男', '創世記 46:16; 民數記 26:17', '民 26:17 作「亞羅得」', 24, 283),
('亞列利（迦得之子）', 'Areli son of Gad', '男', '創世記 46:16; 民數記 26:17', NULL, 24, 284);

-- 亞設之子
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('音拿（亞設之子）', 'Imnah son of Asher', '男', NULL, '創世記 46:17; 民數記 26:44', NULL, 24, 285),
('亦施瓦', 'Ishvi', '男', NULL, '創世記 46:17; 民數記 26:44', NULL, 24, 286),
('比利亞（亞設之子）', 'Beriah son of Asher', '男', '希伯（亞設之孫）、瑪結', '創世記 46:17; 民數記 26:44-45', NULL, 24, 287),
('西拉（亞設之女）', 'Serah daughter of Asher', '女', NULL, '創世記 46:17; 民數記 26:46', '亞設之女，傳說中長壽，告知以色列人約瑟仍在世', 24, 288);

-- 比利亞之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('希伯（亞設之孫）', 'Heber son of Beriah', '男', '民數記 26:45', NULL, 25, 289),
('瑪結（亞設之孫）', 'Malchiel son of Beriah', '男', '民數記 26:45', NULL, 25, 290);

-- 拿弗他利之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('雅薛（拿弗他利之子）', 'Jahzeel son of Naphtali', '男', '創世記 46:24; 民數記 26:48', NULL, 24, 291),
('沽尼（拿弗他利之子）', 'Guni son of Naphtali', '男', '創世記 46:24; 民數記 26:48', NULL, 24, 292),
('以謝（拿弗他利之子）', 'Jezer son of Naphtali', '男', '創世記 46:24; 民數記 26:49', NULL, 24, 293),
('示稜（拿弗他利之子）', 'Shillem son of Naphtali', '男', '創世記 46:24; 民數記 26:49', '又作「沙倫」', 24, 294);

-- 但之子
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('戶心（但之子）', 'Hushim son of Dan', '男', '創世記 46:23; 民數記 26:42', '民 26:42 作「書含」', 24, 295);

-- 便雅憫之子
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('比拉（便雅憫之子）', 'Bela son of Benjamin', '男', '亞珥得（比拉之子）、拿艾（比拉之子）', '創世記 46:21; 民數記 26:38,40', '便雅憫長子', 24, 296),
('比結（便雅憫之子）', 'Becher son of Benjamin', '男', NULL, '創世記 46:21', NULL, 24, 297),
('亞實別（便雅憫之子）', 'Ashbel son of Benjamin', '男', NULL, '創世記 46:21; 民數記 26:38', NULL, 24, 298),
('基拉（便雅憫之子）', 'Gera son of Benjamin', '男', NULL, '創世記 46:21', NULL, 24, 299),
('拿艾（便雅憫之子）', 'Naaman son of Benjamin', '男', NULL, '創世記 46:21; 民數記 26:40', NULL, 24, 300),
('亞希（便雅憫之子）', 'Ehi son of Benjamin', '男', NULL, '創世記 46:21', NULL, 24, 301),
('羅示', 'Rosh', '男', NULL, '創世記 46:21', NULL, 24, 302),
('母辟（便雅憫之子）', 'Muppim son of Benjamin', '男', NULL, '創世記 46:21', '又作「書番」（民 26:39）', 24, 303),
('戶平（便雅憫之子）', 'Huppim son of Benjamin', '男', NULL, '創世記 46:21; 民數記 26:39', NULL, 24, 304),
('亞珥得（比拉之子）', 'Ard son of Bela', '男', NULL, '創世記 46:21; 民數記 26:40', NULL, 25, 305);

-- ── 約瑟之子（創 41:50-52；46:20；民 26:28-37）─────────────────
INSERT INTO biblical_people (name_zh, name_en, gender, spouse, sources, notes, generation, sort_order) VALUES
('亞西納', 'Asenath', '女', '約瑟', '創世記 41:45,50; 46:20', '安城（希利阿坡里）祭司普提非拉之女，約瑟之妻', 24, 306);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('瑪拿西（約瑟之子）', 'Manasseh son of Joseph', '男', '瑪吉（瑪拿西之子）', '創世記 41:51; 46:20; 48:1-20; 民數記 26:28-34', '約瑟長子，雅各收為嗣子；瑪拿西半支派祖先', 24, 307),
('以法蓮（約瑟之子）', 'Ephraim son of Joseph', '男', '書鐵拉、比結（以法蓮之子）、大罕', '創世記 41:52; 46:20; 48:1-20; 民數記 26:35-37', '約瑟次子，雅各為其祝福超越長兄；以法蓮支派祖先', 24, 308);

-- 瑪拿西後代（民 26:29-34；27:1）
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('瑪吉（瑪拿西之子）', 'Machir son of Manasseh', '男', '基列（瑪吉之子）', '民數記 26:29; 27:1; 32:39-40; 申命記 3:15', '瑪拿西長子，征服基列地；基列人之父', 25, 309);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('基列（瑪吉之子）', 'Gilead son of Machir', '男', '以謝珥、希勒、亞斯列、示劍（基列之子）、示米大、希弗（基列之子）', '民數記 26:29-30; 27:1; 36:1; 約書亞記 17:3', '基列地名祖', 26, 310);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('希弗（基列之子）', 'Hepher son of Gilead', '男', '洗羅非哈', '民數記 26:32-33; 27:1', '洗羅非哈之父，只有女兒', 27, 311);

INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('洗羅非哈', 'Zelophehad', '男', '瑪拉、挪阿（洗羅非哈之女）、曷拉、米迦（洗羅非哈之女）、得撒', '民數記 26:33; 27:1-11; 36:1-12', '無子只有五女，因女兒申訴而立繼承土地之例', 28, 312);

-- 洗羅非哈之女（民 27:1；36:11）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('瑪拉（洗羅非哈之女）', 'Mahlah daughter of Zelophehad', '女', '民數記 27:1; 36:11; 約書亞記 17:3', NULL, 29, 313),
('挪阿（洗羅非哈之女）', 'Noah daughter of Zelophehad', '女', '民數記 27:1; 36:11; 約書亞記 17:3', '注意：此挪阿非諾亞（挪亞）', 29, 314),
('曷拉', 'Hoglah', '女', '民數記 27:1; 36:11; 約書亞記 17:3', NULL, 29, 315),
('米迦（洗羅非哈之女）', 'Milcah daughter of Zelophehad', '女', '民數記 27:1; 36:11; 約書亞記 17:3', '注意：此米迦非拿鶴之妻密迦', 29, 316),
('得撒（洗羅非哈之女）', 'Tirzah daughter of Zelophehad', '女', '民數記 27:1; 36:11; 約書亞記 17:3', NULL, 29, 317);

-- 以法蓮後代（民 26:35-37）
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('書鐵拉（以法蓮之子）', 'Shuthelah son of Ephraim', '男', '以蘭（書鐵拉之子）', '民數記 26:35-36', NULL, 25, 318);
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('比結（以法蓮之子）', 'Becher son of Ephraim', '男', '民數記 26:35', NULL, 25, 319),
('大罕（以法蓮之子）', 'Tahan son of Ephraim', '男', '民數記 26:35', NULL, 25, 320),
('以蘭（書鐵拉之子）', 'Eran son of Shuthelah', '男', '民數記 26:36', NULL, 26, 321);

-- 基列的其他兒子（民 26:30-32）
INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('以謝珥', 'Iezer', '男', '民數記 26:30', '又作亞比以謝（士師記 6:34）', 27, 322),
('希勒（基列之子）', 'Helek son of Gilead', '男', '民數記 26:30', NULL, 27, 323),
('亞斯列（基列之子）', 'Asriel son of Gilead', '男', '民數記 26:31', NULL, 27, 324),
('示劍（基列之子）', 'Shechem son of Gilead', '男', '民數記 26:31', NULL, 27, 325),
('示米大（基列之子）', 'Shemida son of Gilead', '男', '民數記 26:32', NULL, 27, 326);

-- ──────────────────────────────────────────────────────────────
-- 第四節：十二探子（民 13:1-16）
-- ──────────────────────────────────────────────────────────────

INSERT INTO biblical_people (name_zh, name_en, gender, sources, notes, generation, sort_order) VALUES
('迦勒（耶孚尼之子）', 'Caleb son of Jephunneh', '男', '民數記 13:6; 14:6,30; 申命記 1:36; 約書亞記 14:6-15', '猶大支派探子，與約書亞同心相信神，得以進入迦南', 27, 327),
('約書亞（嫩之子）', 'Joshua son of Nun', '男', '民數記 13:8,16; 14:6,30; 申命記 34:9; 約書亞記 1:1-2', '以法蓮支派探子，摩西的助手，繼承摩西帶領以色列進入迦南', 27, 328),
('撒母亞（撒刻之子）', 'Shammua son of Zaccur', '男', '民數記 13:4', '流便支派探子', 27, 329),
('沙法（何利之子）', 'Shaphat son of Hori', '男', '民數記 13:5', '西緬支派探子', 27, 330),
('以迦勒（約瑟之子）', 'Igal son of Joseph', '男', '民數記 13:7', '以薩迦支派探子', 27, 331),
('帕提（拉孚之子）', 'Palti son of Raphu', '男', '民數記 13:9', '便雅憫支派探子', 27, 332),
('迦底業（索底之子）', 'Gaddiel son of Sodi', '男', '民數記 13:10', '西布倫支派探子', 27, 333),
('迦底（書西之子）', 'Gaddi son of Susi', '男', '民數記 13:11', '瑪拿西支派探子', 27, 334),
('亞米利（基瑪利之子）', 'Ammiel son of Gemalli', '男', '民數記 13:12', '但支派探子', 27, 335),
('西突（米迦勒之子）', 'Sethur son of Michael', '男', '民數記 13:13', '亞設支派探子', 27, 336),
('拿比（沃甫西之子）', 'Nahbi son of Vophsi', '男', '民數記 13:14', '拿弗他利支派探子', 27, 337),
('基利勒（瑪基之子）', 'Geuel son of Machi', '男', '民數記 13:15', '迦得支派探子', 27, 338);

-- ──────────────────────────────────────────────────────────────
-- 第五節：其他重要人物
-- ──────────────────────────────────────────────────────────────

-- 摩西岳父（出 3:1；民 10:29）
INSERT INTO biblical_people (name_zh, name_en, gender, children, sources, notes, generation, sort_order) VALUES
('何巴（摩西的內兄）', 'Hobab son of Reuel', '男', NULL, '民數記 10:29; 士師記 4:11', '米甸人，摩西的妻兄（或岳父），曾被邀同行進迦南', 27, 339);

-- 亞倫之孫（民 25:7）
UPDATE biblical_people SET children = '非尼哈' WHERE name_zh = '以利亞撒';
