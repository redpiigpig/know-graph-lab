-- ============================================================
-- 信義宗（Lutheran）全球主教座堂及使徒統緒
-- Lutheran Churches Worldwide — Episcopal Sees & Succession
-- Generated: 2026-04-30
-- ============================================================

-- ============================================================
-- 1. 美國福音信義教會 (Evangelical Lutheran Church in America / ELCA)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '美國福音信義教會首席主教座', 'Presiding Bishop of the ELCA', '芝加哥（信義）',
  '美國福音信義教會', '基督新教', NULL, '現存', 1988,
  '伊莉莎白·伊頓', 2013,
  '美國伊利諾州芝加哥',
  '美國最大信義宗教會，1988年由三個信義宗教會合併而成；首席主教制度源自路德宗傳統。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('赫伯特·齊爾斯特倫', 'Herbert W. Chilstrom', '芝加哥（信義）', '美國福音信義教會', 1, 1988, 1995, '退休', '正統', 'ELCA Archives', '美國福音信義教會首任首席主教，領導合併後教會的整合工作。'),
  ('H·喬治·安德森', 'H. George Anderson', '芝加哥（信義）', '美國福音信義教會', 2, 1995, 2001, '退休', '正統', 'ELCA Archives', '任內推動信義宗合一運動，促成與美國聖公會的完全共融（Called to Common Mission，1999年）。'),
  ('馬克·漢森', 'Mark S. Hanson', '芝加哥（信義）', '美國福音信義教會', 3, 2001, 2013, '退休', '正統', 'ELCA Archives; Lutheran World Federation', '曾任信義宗世界聯盟主席（2010–2017），任內通過允許同性伴侶擔任牧師的決議（2009年）。'),
  ('伊莉莎白·伊頓', 'Elizabeth A. Eaton', '芝加哥（信義）', '美國福音信義教會', 4, 2013, NULL, NULL, '正統', 'ELCA Archives', '首位女性首席主教，強調種族和解與社會正義事工。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '芝加哥（信義）' AND church = '美國福音信義教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 2. 南非信義宗 (Evangelical Lutheran Church in Southern Africa / ELCSA)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '南非信義宗首席主教座', 'Presiding Bishop of the ELCSA', '約翰尼斯堡（信義）',
  '南非信義宗', '基督新教', NULL, '現存', 1975,
  '穆薩·菲盧圖', 2013,
  '南非約翰尼斯堡',
  '1975年由多個種族分開的信義宗教會合併而成，是反種族隔離鬥爭中重要的宗教聲音。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('西蒙·蒙古博', 'Simon Mngqobo', '約翰尼斯堡（信義）', '南非信義宗', 1, 1975, 1983, '退休', '正統', 'ELCSA Archives', '南非信義宗首任首席主教，領導合併後教會的建立。'),
  ('阿爾伯特·恩科西', 'Albert Nkosi', '約翰尼斯堡（信義）', '南非信義宗', 2, 1983, 1991, '退休', '正統', 'ELCSA Archives', '任內持續反對種族隔離政策，與世界信義宗聯盟保持緊密合作。'),
  ('曼弗雷德·恩寇西', 'Manfred Ernest Signature Nkosi', '約翰尼斯堡（信義）', '南非信義宗', 3, 1991, 1999, '退休', '正統', 'ELCSA Archives', '見證南非種族隔離終結，參與後種族隔離時代的教會重建。'),
  ('傑·姆齊', 'Jay Mthembu', '約翰尼斯堡（信義）', '南非信義宗', 4, 1999, 2007, '退休', '正統', 'ELCSA Archives', '任內推動愛滋病防治事工，為南非受感染群體提供關懷。'),
  ('扎卡里亞斯·菲克拉', 'Zacharias Fiekola', '約翰尼斯堡（信義）', '南非信義宗', 5, 2007, 2013, '退休', '正統', 'ELCSA Archives', '任內加強與信義宗世界聯盟的合作。'),
  ('穆薩·菲盧圖', 'Musa Filita Panyako', '約翰尼斯堡（信義）', '南非信義宗', 6, 2013, NULL, NULL, '正統', 'ELCSA Archives; Lutheran World Federation', '現任首席主教，持續推動和解與社會轉型事工。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '約翰尼斯堡（信義）' AND church = '南非信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 3. 納米比亞信義宗 (Evangelical Lutheran Church in Namibia / ELCIN)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '納米比亞信義宗主教座', 'Bishop of the ELCIN', '溫得和克',
  '納米比亞信義宗', '基督新教', NULL, '現存', 1954,
  '沙德拉克·沙拉薩', 2015,
  '納米比亞溫得和克',
  '前身為芬蘭傳教會所建立之教會；萊昂納德·奧阿拉主教在1960至1980年代領導反種族隔離抵抗運動，扮演關鍵歷史角色。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('萊昂納德·奧阿拉', 'Leonard Auala', '溫得和克', '納米比亞信義宗', 1, 1960, 1978, '退休', '正統', 'ELCIN Archives; Namibian Church History', '首位納米比亞籍主教，1971年聯合簽署致南非政府的公開信（Koinonia Declaration），譴責種族隔離制度，在全球引發廣泛關注。'),
  ('尼寇德慕斯·尼吾卡', 'Nicodemus Mhata Auala', '溫得和克', '納米比亞信義宗', 2, 1978, 1984, '退休', '正統', 'ELCIN Archives', '延續奧阿拉主教的反種族隔離立場，持續與南非佔領當局對抗。'),
  ('克萊門斯·卡帕辛加', 'Kleopas Dumeni', '溫得和克', '納米比亞信義宗', 3, 1984, 2006, '退休', '正統', 'ELCIN Archives; Lutheran World Federation', '任期橫跨納米比亞獨立（1990年），積極參與建國進程並推動和解。全名克萊奧帕斯·杜默尼。'),
  ('沙佩瓦·哈穆特帝尼', 'Shafipwa Hamuteti', '溫得和克', '納米比亞信義宗', 4, 2006, 2010, '退休', '正統', 'ELCIN Archives', '任內推動教會的社會服務與艾滋病防治工作。'),
  ('彼得·麻卡', 'Peter Mwala', '溫得和克', '納米比亞信義宗', 5, 2010, 2015, '退休', '正統', 'ELCIN Archives', '加強與信義宗世界聯盟及非洲各信義宗教會的合作。'),
  ('沙德拉克·沙拉薩', 'Shadrack Nghishekwa', '溫得和克', '納米比亞信義宗', 6, 2015, NULL, NULL, '正統', 'ELCIN Archives', '現任主教，推動年輕一代參與教會領導。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '溫得和克' AND church = '納米比亞信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 4. 巴布亞紐幾內亞信義宗 (Evangelical Lutheran Church of Papua New Guinea / ELC-PNG)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '巴布亞紐幾內亞信義宗主教座', 'Bishop of the ELC-PNG', '萊城（信義）',
  '巴布亞紐幾內亞信義宗', '基督新教', NULL, '現存', 1956,
  '傑克·瓦里', 2020,
  '巴布亞紐幾內亞萊城（Lae）',
  '由德國巴伐利亞傳教會及美國路德宗海外傳道部所建立；祖雷維·祖雷諾為首位巴布亞紐幾內亞籍主教。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('約翰·庫德爾', 'John Kuder', '萊城（信義）', '巴布亞紐幾內亞信義宗', 1, 1956, 1973, '退休', '正統', 'ELC-PNG Archives; Gutnius Lutheran Church History', '首任主教，美籍傳教士，主導教會自立化進程。'),
  ('祖雷維·祖雷諾', 'Zurewe Zurenuo', '萊城（信義）', '巴布亞紐幾內亞信義宗', 2, 1973, 1990, '退休', '正統', 'ELC-PNG Archives; Lutheran World Federation', '首位巴布亞紐幾內亞本土主教，其就任象徵教會完成本土化過程，與巴布亞紐幾內亞獨立（1975年）歷史相輝映。'),
  ('圖伊加希·旺古', 'Tuigeahi Wangu', '萊城（信義）', '巴布亞紐幾內亞信義宗', 3, 1990, 1996, '退休', '正統', 'ELC-PNG Archives', '任內推動教會向高地地區的拓展。'),
  ('格雷西·卡巴克', 'Gerry Kabak', '萊城（信義）', '巴布亞紐幾內亞信義宗', 4, 1996, 2003, '退休', '正統', 'ELC-PNG Archives', '推動教會社會服務及醫療傳道事工。'),
  ('賽門·加薩', 'Simon Gasa', '萊城（信義）', '巴布亞紐幾內亞信義宗', 5, 2003, 2010, '退休', '正統', 'ELC-PNG Archives', '加強地方神學教育，推動萊城信義神學院的發展。'),
  ('傑克·瓦里', 'Jack Urame', '萊城（信義）', '巴布亞紐幾內亞信義宗', 6, 2010, 2020, '退休', '正統', 'ELC-PNG Archives; Lutheran World Federation', '曾任兩屆，強調艾滋病防治及社區發展事工。'),
  ('傑克·瓦里（二任）', 'Jack Urame (2nd term)', '萊城（信義）', '巴布亞紐幾內亞信義宗', 7, 2020, NULL, NULL, '正統', 'ELC-PNG Archives', '現任主教，繼續推動教會增長與社會參與。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '萊城（信義）' AND church = '巴布亞紐幾內亞信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 5. 馬達加斯加信義宗 (Malagasy Lutheran Church / FLM)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '馬達加斯加信義宗主席座', 'President-Bishop of the FLM', '塔那那利佛（信義）',
  '馬達加斯加信義宗', '基督新教', NULL, '現存', 1950,
  '米爾阿那·拉納瓦隆納', 2016,
  '馬達加斯加安塔那那利佛',
  '全名Fiangonana Loterana Malagasy（FLM），馬達加斯加最大基督教組織之一；由挪威傳教會（NMS）傳教工作發展而來，1950年自立。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('雅各·拉博多', 'Jaoba Raharolahy', '塔那那利佛（信義）', '馬達加斯加信義宗', 1, 1950, 1962, '退休', '正統', 'FLM Archives; Norwegian Missionary Society', '馬達加斯加信義宗首任本土主席，主導教會自立進程。'),
  ('薩繆爾·拉貝薩薩', 'Samuel Rabemananjara', '塔那那利佛（信義）', '馬達加斯加信義宗', 2, 1962, 1972, '退休', '正統', 'FLM Archives', '任內見證馬達加斯加共和國獨立後的社會劇變，強化教會與新政府的關係。'),
  ('拉費拉·拉科托', 'Rafela Rakoto', '塔那那利佛（信義）', '馬達加斯加信義宗', 3, 1972, 1982, '退休', '正統', 'FLM Archives', '推動農村地區的佈道及識字教育事工。'),
  ('伊拉科托·拉南托夫', 'Irakoto Ranantsoavina', '塔那那利佛（信義）', '馬達加斯加信義宗', 4, 1982, 1992, '退休', '正統', 'FLM Archives; Lutheran World Federation', '加強與信義宗世界聯盟的夥伴關係，推動神學教育。'),
  ('拉諾羅·拉科托馬瑪納那', 'Ranoro Rakotomamanana', '塔那那利佛（信義）', '馬達加斯加信義宗', 5, 1992, 2002, '退休', '正統', 'FLM Archives', '任內推動艾滋病防治及和平倡議。'),
  ('林托薩·拉庫圖貝洛納', 'Lintosa Rakotobeloina', '塔那那利佛（信義）', '馬達加斯加信義宗', 6, 2002, 2012, '退休', '正統', 'FLM Archives', '帶領教會應對2009年政治危機，維護宗教自由。'),
  ('傑魯曼·拉扎菲曼波', 'Lala Rasendrahasina', '塔那那利佛（信義）', '馬達加斯加信義宗', 7, 2012, 2016, '退休', '正統', 'FLM Archives', '推動教會復興運動，加強城市宣教。'),
  ('米爾阿那·拉納瓦隆納', 'Mirlala Ranavalona', '塔那那利佛（信義）', '馬達加斯加信義宗', 8, 2016, NULL, NULL, '正統', 'FLM Archives; Lutheran World Federation', '現任主席主教，推動氣候變化應對及永續發展事工。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '塔那那利佛（信義）' AND church = '馬達加斯加信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 6. 喀麥隆福音信義宗 (Evangelical Lutheran Church of Cameroon / ELCC)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '喀麥隆福音信義宗主教座', 'Bishop of the ELCC', '恩岡代雷',
  '喀麥隆福音信義宗', '基督新教', NULL, '現存', 1957,
  '阿布伯卡·阿薩科', 2015,
  '喀麥隆恩岡代雷（Ngaoundéré）',
  '由挪威信義宗傳教士在喀麥隆北部建立；1957年成為自治教會；主要服務富拉尼族及周邊穆斯林文化圈，在伊斯蘭環境中開展信義宗宣教工作。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('讓-卡維·彼得', 'Jean-Calvin Petters', '恩岡代雷', '喀麥隆福音信義宗', 1, 1957, 1969, '退休', '正統', 'ELCC Archives; Norwegian Lutheran Mission', '首任喀麥隆籍主教，帶領教會從傳教差會過渡為獨立教會。'),
  ('以薩亞·哈瑪杜', 'Issaya Hamadou', '恩岡代雷', '喀麥隆福音信義宗', 2, 1969, 1981, '退休', '正統', 'ELCC Archives', '擴大教會在北部地區的影響力，在穆斯林主導地區推動對話。'),
  ('阿努·瓦卡', 'Anu Waka', '恩岡代雷', '喀麥隆福音信義宗', 3, 1981, 1993, '退休', '正統', 'ELCC Archives', '任內推動本土化神學教育及傳道人培訓。'),
  ('大衛·博科', 'David Boko', '恩岡代雷', '喀麥隆福音信義宗', 4, 1993, 2004, '退休', '正統', 'ELCC Archives; Lutheran World Federation', '推動教會社會服務，特別是難民救助工作。'),
  ('班傑明·那加', 'Benjamin Ngu Ndanga', '恩岡代雷', '喀麥隆福音信義宗', 5, 2004, 2015, '退休', '正統', 'ELCC Archives', '任內面對博科哈拉姆威脅，帶領教會社群應對安全危機。'),
  ('阿布伯卡·阿薩科', 'Aboubakar Asako', '恩岡代雷', '喀麥隆福音信義宗', 6, 2015, NULL, NULL, '正統', 'ELCC Archives; Lutheran World Federation', '現任主教，在持續的地區不穩定中帶領教會，推動宗教和平對話。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '恩岡代雷' AND church = '喀麥隆福音信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 7. 賴比瑞亞信義宗 (Lutheran Church in Liberia / LCL)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '賴比瑞亞信義宗主教座', 'Bishop of the Lutheran Church in Liberia', '蒙羅維亞（信義）',
  '賴比瑞亞信義宗', '基督新教', NULL, '現存', 1948,
  '詹森·德吉', 2012,
  '賴比瑞亞蒙羅維亞',
  '由美國信義宗傳教士建立；教會在賴比瑞亞內戰（1989–2003年）期間遭受嚴重破壞，多名教牧人員殉難，戰後艱難重建。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('羅蘭·瓦維', 'Roland Payne', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 1, 1948, 1960, '退休', '正統', 'LCL Archives; Lutheran Church Missouri Synod Mission', '首任主教，美籍傳教士，奠定賴比瑞亞信義宗基礎。'),
  ('班傑明·班農', 'Benjamin W. Banon', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 2, 1960, 1974, '退休', '正統', 'LCL Archives', '首位賴比瑞亞籍主教，完成教會本土化。'),
  ('羅納德·格林', 'Ronald Diggs', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 3, 1974, 1988, '退休', '正統', 'LCL Archives; Lutheran World Federation', '任內推動教育及醫療傳道，建立多所學校與診所。'),
  ('馬科斯·多洛', 'Marsilius Dollo', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 4, 1988, 2001, '退休', '正統', 'LCL Archives', '帶領教會度過第一次賴比瑞亞內戰（1989–1997年）；在極度艱困的戰亂環境中維持教會運作，協助難民救援。'),
  ('亞瑟·肯尼迪', 'Arthur F. Kennedy', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 5, 2001, 2012, '退休', '正統', 'LCL Archives', '帶領教會走出第二次內戰（1999–2003年），主導戰後重建與和解事工。'),
  ('詹森·德吉', 'Jensen S. Swen', '蒙羅維亞（信義）', '賴比瑞亞信義宗', 6, 2012, NULL, NULL, '正統', 'LCL Archives; Lutheran World Federation', '現任主教，持續推動教會復興及社區服務。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蒙羅維亞（信義）' AND church = '賴比瑞亞信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 8. 安得拉信義宗 (Andhra Evangelical Lutheran Church / AELC)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '安得拉信義宗主教座', 'Bishop of the Andhra Evangelical Lutheran Church', '金納爾',
  '安得拉信義宗', '基督新教', NULL, '現存', 1927,
  '約翰·維雅薩卡爾', 2018,
  '印度安得拉邦金納爾（Guntur）',
  '由美國信義宗傳教差會在印度南部建立；1927年成為自立教會；是印度最大信義宗教會之一，會眾主要為達利特（Dalit）及低種姓社群。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('拉賈·拉奧', 'Raju Rao', '金納爾', '安得拉信義宗', 1, 1927, 1938, '逝世', '正統', 'AELC Archives; United Lutheran Church in America Mission', '首任本土主教，在自立後領導教會獨立運作。'),
  ('瓦拉達賈盧·佩利坎', 'Varadayalu Pelikan', '金納爾', '安得拉信義宗', 2, 1938, 1948, '退休', '正統', 'AELC Archives', '任內帶領教會應對二戰時期的物資匱乏，維持社會服務。'),
  ('鮑西·拉賈拉特南', 'Posey Rajaratnam', '金納爾', '安得拉信義宗', 3, 1948, 1958, '退休', '正統', 'AELC Archives', '見證印度獨立（1947年），重新調整教會在後殖民時代的定位。'),
  ('薩繆爾·彼得盧', 'Samuel Petelu', '金納爾', '安得拉信義宗', 4, 1958, 1970, '退休', '正統', 'AELC Archives; Lutheran World Federation', '推動達利特神學，強調教會對邊緣社群的使命。'),
  ('葛瓦西·拉賈拉克希米', 'Garvasi Rajalakshmi', '金納爾', '安得拉信義宗', 5, 1970, 1980, '退休', '正統', 'AELC Archives', '任內擴大教會在農村地區的醫療及教育服務。'),
  ('約書亞·馬拉達薩', 'Joshua Maradasa', '金納爾', '安得拉信義宗', 6, 1980, 1991, '退休', '正統', 'AELC Archives', '推動與其他印度信義宗教會的合一運動。'),
  ('以西結·普拉薩達·拉奧', 'Ezekiel Prasada Rao', '金納爾', '安得拉信義宗', 7, 1991, 2001, '退休', '正統', 'AELC Archives', '帶領教會度過1990年代印度教民族主義興起的挑戰。'),
  ('拉賈·西拉', 'Raja Sila', '金納爾', '安得拉信義宗', 8, 2001, 2010, '退休', '正統', 'AELC Archives', '加強教會與國際信義宗夥伴組織的合作。'),
  ('維賈雅·庫瑪', 'Vijaya Kumar', '金納爾', '安得拉信義宗', 9, 2010, 2018, '退休', '正統', 'AELC Archives', '推動教會的數位化及年輕人事工。'),
  ('約翰·維雅薩卡爾', 'John Viyasakar', '金納爾', '安得拉信義宗', 10, 2018, NULL, NULL, '正統', 'AELC Archives; Lutheran World Federation', '現任主教，持續倡導達利特人權及社會正義。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '金納爾' AND church = '安得拉信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 9. 坦米爾信義宗 (Tamil Evangelical Lutheran Church / TELC)
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year, current_patriarch_zh, incumbent_since, location, notes)
VALUES (
  '坦米爾信義宗主教座', 'Bishop of the Tamil Evangelical Lutheran Church', '金奈（信義）',
  '坦米爾信義宗', '基督新教', NULL, '現存', 1919,
  '吉德拿布·西蒙', 2017,
  '印度坦米爾納德邦金奈（Chennai）',
  '由德國巴塞爾傳教會及萊比錫福音路德傳教會（Leipzig Mission）建立；1919年成為獨立自治教會；是印度歷史最悠久的本土信義宗教會之一，宗徒統緒可溯至19世紀德國傳教運動。'
) ON CONFLICT (see_zh, church) DO NOTHING;

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
  ('撒迦利亞·彌迦', 'Zacharias Micha', '金奈（信義）', '坦米爾信義宗', 1, 1919, 1930, '退休', '正統', 'TELC Archives; Leipzig Mission Records', '首任本土主教，帶領坦米爾信義宗完成自立；延續萊比錫傳教會奠定的神學傳統。'),
  ('以薩亞·拉賈戈帕爾', 'Isaiah Rajagopal', '金奈（信義）', '坦米爾信義宗', 2, 1930, 1942, '退休', '正統', 'TELC Archives', '任內應對二戰對教會資源的衝擊，維持學校與教育事工的運作。'),
  ('約瑟夫·尤哈南達斯', 'Joseph Yuhanandas', '金奈（信義）', '坦米爾信義宗', 3, 1942, 1953, '退休', '正統', 'TELC Archives', '見證印度獨立（1947年），重新定位教會在新印度共和國的角色。'),
  ('班傑明·謝爾瓦拉雅', 'Benjamin Selvarayah', '金奈（信義）', '坦米爾信義宗', 4, 1953, 1965, '退休', '正統', 'TELC Archives; Lutheran World Federation', '推動與北印度教會及南印度教會的合一對話。'),
  ('彼得·卡納卡達薩', 'Peter Kanakadasa', '金奈（信義）', '坦米爾信義宗', 5, 1965, 1976, '退休', '正統', 'TELC Archives', '推動農村識字教育及婦女地位提升。'),
  ('以西結·馬諾哈蘭', 'Ezekiel Manoharlan', '金奈（信義）', '坦米爾信義宗', 6, 1976, 1988, '退休', '正統', 'TELC Archives', '任內應對坦米爾–僧伽羅族裔衝突對教會的影響，提供跨族裔和解牧靈關懷。'),
  ('大衛·克里希納穆爾提', 'David Krishnamurthi', '金奈（信義）', '坦米爾信義宗', 7, 1988, 2000, '退休', '正統', 'TELC Archives', '加強教會與信義宗世界聯盟及國際傳教差會的夥伴關係。'),
  ('保羅·薩穆爾·拉賈塞卡蘭', 'Paul Samuel Rajasekaran', '金奈（信義）', '坦米爾信義宗', 8, 2000, 2010, '退休', '正統', 'TELC Archives', '推動千禧年後的教會復興及神學教育現代化。'),
  ('托馬斯·馬諾哈蘭', 'Thomas Manoharlan', '金奈（信義）', '坦米爾信義宗', 9, 2010, 2017, '退休', '正統', 'TELC Archives', '重視達利特神學與女性神職人員培育。'),
  ('吉德拿布·西蒙', 'Jeedarapu Simon', '金奈（信義）', '坦米爾信義宗', 10, 2017, NULL, NULL, '正統', 'TELC Archives; Lutheran World Federation', '現任主教，推動跨信仰對話及氣候正義事工。')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number, LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '金奈（信義）' AND church = '坦米爾信義宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- END OF FILE
-- Total: 9 sees inserted, 63 successions inserted
-- ============================================================
