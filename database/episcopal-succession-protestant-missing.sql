-- ============================================================
-- 新教主要教會主教傳承（缺漏補充）
-- Missing Protestant Churches: Episcopal Succession
-- Churches: 剛果聖公宗, 坦尚尼亞信義宗, 衣索比亞福音教會,
--           印尼巴塔克基督教, 中美洲聖公宗, 莫三比克聖公宗
-- ============================================================

-- ============================================================
-- 1. 剛果聖公宗（Province de l'Eglise Anglicane du Congo / PEAC）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('剛果聖公宗大主教座（金沙薩）',
 'Province of the Anglican Church of the Congo (PEAC)',
 '金沙薩（聖公宗）',
 '剛果聖公宗',
 '基督新教', NULL, '現存', 1992,
 'Georges Titre Ande（2022–）', 2022,
 '剛果民主共和國（DRC）金沙薩',
 '剛果聖公宗（PEAC / Province de l''Eglise Anglicane du Congo）1992年從中非聖公宗省分立，成為獨立省份；前身為1885年英國聖公宗傳教士進入剛果盆地建立的傳教區；1971年與贊比亞、馬拉威共同組成中非聖公宗省；1992年三國各自獨立成省；1997年隨國家更名為「剛果民主共和國」，教會亦同步更名；現設12個教區；首席主教（大主教）兼任阿魯教區主教；GAFCON成員；在東部剛果衝突地區（基伍等省）積極從事人道主義工作。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承：剛果聖公宗（金沙薩）
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('帕特里斯·恩喬喬',
 'Patrice Njojo',
 '金沙薩（聖公宗）', '剛果聖公宗',
 1, 1992, 2003, '退休', '正統',
 'Province of the Anglican Church of Congo; Anglican Communion records',
 '剛果聖公宗建省後首任大主教（1992年）；曾在薩伊（後更名剛果民主共和國）服事；1997年國家更名後教會亦隨之更名；任期至2003年'),

('迪羅克帕·巴盧富加·菲德爾',
 'Dirokpa Balufuga Fidèle',
 '金沙薩（聖公宗）', '剛果聖公宗',
 2, 2003, 2009, '退休', '正統',
 'Anglican Communion records; PEAC official sources',
 '第二任大主教；2003年2月16日登基就職；在任期間積極推動剛果東部衝突地區的和平工作'),

('亨利·伊辛戈馬',
 'Henri Isingoma Kahwa',
 '金沙薩（聖公宗）', '剛果聖公宗',
 3, 2009, 2016, '退休', '正統',
 'PEAC; Anglican Communion; GAFCON records',
 '第三任大主教；2009年4月28日當選；曾就讀布殊爾大學（Bushire University）及國際神學院；在任期間代表PEAC出席GAFCON大會；積極倡導非洲保守聖公宗立場'),

('撒迦利亞·馬西曼戈·卡坦達',
 'Zacharie Masimango Katanda',
 '金沙薩（聖公宗）', '剛果聖公宗',
 4, 2016, 2022, '退休', '正統',
 'Anglican Communion; GAFCON; Anglican Ink 2022',
 '第四任大主教；2016年9月12日祝聖就職；曾任布卡武（Bukavu）教區主教；任期間見證PEAC擴展至12個教區；東部剛果武裝衝突期間積極為平民發聲'),

('喬治·蒂特爾·安德',
 'Georges Titre Ande',
 '金沙薩（聖公宗）', '剛果聖公宗',
 5, 2022, NULL, NULL, '正統',
 'Anglican Communion; Anglican Ink 2022; GAFCON 2022',
 '第五任大主教；2006年祝聖為阿魯（Aru）教區主教；2022年當選並就任PEAC大主教；GAFCON理事會成員；繼續推動剛果東部人道救援工作');

-- predecessor_id 鏈結：剛果聖公宗
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '金沙薩（聖公宗）' AND church = '剛果聖公宗'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 2. 坦尚尼亞信義宗（Evangelical Lutheran Church in Tanzania / ELCT）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('坦尚尼亞信義宗首席主教座（達累斯薩拉姆）',
 'Evangelical Lutheran Church in Tanzania (ELCT), Presiding Bishop',
 '達累斯薩拉姆（信義）',
 '坦尚尼亞信義宗',
 '基督新教', NULL, '現存', 1963,
 'Alex Malasusa（2024–）', 2024,
 '坦尚尼亞達累斯薩拉姆',
 '坦尚尼亞信義宗（ELCT）1963年成立，整合德國萊茵傳道會、奧古斯塔拿傳道會、柏林傳道會等在坦尚尼亞的信義宗傳教區；非洲最大的信義宗教會之一，約有600萬信徒；1977年約西亞·奇比拉（Josiah Kibira）當選世界信義宗聯盟（LWF）主席（1977–1984年），為LWF史上首位非裔主席；現設30多個教區，首席主教（Presiding Bishop）為全教會領袖；為世界信義宗聯盟（LWF）及坦尚尼亞基督教協會（CCT）成員；與非洲其他信義宗教會保持密切合作。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承：坦尚尼亞信義宗
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('斯特凡諾·莫西',
 'Stefano Reuben Moshi',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 1, 1963, 1971, '逝世', '正統',
 'LWF records; Evangelical Lutheran Church in Tanzania, Wikipedia; LWF 50th anniversary report',
 'ELCT首任首席主教（1963年教會成立時選出，1964年正式祝聖）；出身北部基利馬扎羅（Kilimanjaro）地區；早期在德國傳道會學習神學；帶領坦尚尼亞信義宗從殖民地傳教區轉型為獨立本土教會；在任期間ELCT加入LWF；1971年8月14日逝世，信眾達80萬'),

('約西亞·奇比拉',
 'Josiah Mutabuzi Isaya Kibira',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 2, 1971, 1984, '退休', '正統',
 'LWF; DACB (Dictionary of African Christian Biography); Kibira biography, BU Missiology',
 '第二任首席主教（1971年繼任）；1925年生於坦尚尼亞布科巴（Bukoba）；1977至1984年擔任世界信義宗聯盟（LWF）主席，為非洲第一位LWF主席；積極推動非洲神學本色化與坦尚尼亞教會的社會工作；1988年辭世；約西亞·奇比拉大學（Josiah Kibira University College）以其命名'),

('塞巴斯蒂安·科洛瓦',
 'Sebastian Kolowa',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 3, 1984, 1994, '退休', '正統',
 'ELCT records; LWF; VEM Mission',
 '第三任首席主教；1974年祝聖為ELCT東北教區主教，1984年升任首席主教；長期主持達累斯薩拉姆的ELCT中央辦事處；推動全國神學教育發展；塞巴斯蒂安·科洛瓦紀念大學（Sebastian Kolowa Memorial University）以其命名'),

('薩姆森·穆謝巴',
 'Samson Bajanjabi Mushemba',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 4, 1994, 2007, '退休', '正統',
 'ELCT; GPEN Reformation; VEM Mission obituary',
 '第四任首席主教；1935年6月30日生；任期內推動ELCT教育、醫療和農村發展事業；積極參與泛非洲信義宗網絡（GPEN）活動；2007年退休；晚年逝世（死亡日期記載不詳）'),

('阿利克斯·馬拉蘇薩',
 'Alex Malasusa',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 5, 2007, 2015, '退休', '正統',
 'LWF; The Citizen Tanzania; allafrica.com 2007',
 '第五任首席主教；2007年7月當選並就職；任期兩屆共8年；在任期間見證ELCT持續增長至約600萬信徒；推動教會與坦尚尼亞政府的合作關係'),

('腓特烈·紹',
 'Frederick Onael Shoo',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 6, 2015, 2023, '退休', '正統',
 'LWF news 2015; ILC 2015; New Leadership ELCT: Kolowa to Shoo (Scribd)',
 '第六任首席主教；選前為ELCT北部教區（Northern Diocese）主教；2015年8月24日宣誓就職；首任就職禮有政府要員出席；任期至2023年；任內推動ELCT社會服務與全球夥伴關係'),

('阿利克斯·馬拉蘇薩（第二任期）',
 'Alex Malasusa (2nd term)',
 '達累斯薩拉姆（信義）', '坦尚尼亞信義宗',
 7, 2024, NULL, NULL, '正統',
 'The Citizen Tanzania 2024; Pan African Visions 2024',
 '第七任首席主教（第二次任期）；2024年1月正式就職，接替紹主教；為坦尚尼亞信義宗歷史上首位兩度出任首席主教者；當選後強調領導坦尚尼亞信義宗繼續推動平等、和好與社會服務的使命');

-- predecessor_id 鏈結：坦尚尼亞信義宗
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '達累斯薩拉姆（信義）' AND church = '坦尚尼亞信義宗'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 3. 衣索比亞福音教會（Ethiopian Evangelical Church Mekane Yesus / EECMY）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('衣索比亞福音教會主席座（亞的斯亞貝巴）',
 'Ethiopian Evangelical Church Mekane Yesus (EECMY), President',
 '亞的斯亞貝巴（信義）',
 '衣索比亞福音教會',
 '基督新教', NULL, '現存', 1959,
 'Yonas Yigezu（2017–）', 2017,
 '衣索比亞亞的斯亞貝巴',
 '衣索比亞福音教會「耶穌聖所」（Mekane Yesus，意為「耶穌的居所」）1959年1月21日正式成立，整合多個北歐信義宗傳道差會（瑞典信義宗、挪威信義宗、丹麥信義宗、德國赫爾曼斯堡差會）在衣索比亞的工作；為全球最大的信義宗教會之一，信眾超過1000萬；古迪納·圖姆薩（Gudina Tumsa）總幹事1979年被德爾格軍政府殺害，被視為殉道者，在衣索比亞及全球信義宗廣受尊崇；1977–1982年因德爾格政府迫害而被迫停止公開活動；與世界信義宗聯盟（LWF）、世界教協（WCC）保持密切聯繫；總部設於亞的斯亞貝巴馬卡尼薩（Makanissa）。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承（歷任會長/主席）：衣索比亞福音教會
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('馬可·柯西',
 'Marko Qashe',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 1, 1959, 1963, '退休', '正統',
 'EECMY 50th Anniversary; EECMY history sources',
 'EECMY首任會長（1959年教會成立時選出）；為推動不同差會整合成統一全國性教會作出重要貢獻；任期至1963年第一屆大會'),

('伊曼努爾·亞伯拉罕',
 'Emmanuel Abraham',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 2, 1963, 1979, '逝世', '正統',
 'DACB; Emmanuel Abraham biography; Goolgule.com obituary',
 '第二任會長（1963至1979年）；1913至2016年（享壽約102歲）；曾任外交官及教育家；帶領EECMY度過快速增長期；1979年德爾格政府迫害高峰期間逝世（說法不一，另有資料顯示其存活至1985年後方卸任；本記錄依主流文獻）；任內見證EECMY從草創到規模性增長'),

('古迪納·圖姆薩',
 'Gudina Tumsa',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 3, 1979, 1979, '殉道', '正統',
 'Gudina Tumsa Wikipedia; DACB; Lutheran Forum; Word and World journal; Gudina Tumsa Foundation',
 '第三任總幹事（代行最高領導職責）；1929年生；神學家、EECMY改革領袖；1966年出任EECMY執行秘書，後升任總幹事；因拒絕德爾格軍政府要求教會配合其政治議程，1979年7月28日遭逮捕，隨後被殺害；被全球信義宗視為殉道者；亞的斯亞貝巴的古迪納·圖姆薩神學研究中心（GTRC）以其命名'),

('貝雷奈·穆盧內',
 'Beyene Muluneh',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 4, 1982, 1993, '退休', '正統',
 'EECMY historical records; LWF Africa records',
 '第四任會長；教會在德爾格政府迫害後逐步恢復期間帶領EECMY重建；1977至1982年EECMY被迫停止公開活動，1982年門格斯圖政權稍為放寬管制後教會逐漸復甦；在任期間推動EECMY重建組織架構，擴展農村傳道與社會工作'),

('瓦克賽育姆·伊多薩',
 'Wakseyoum Idosa',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 5, 2009, 2017, '退休', '正統',
 'LWF; EECMY 20th General Assembly 2017; ILC; Union Presbyterian Seminary',
 '第五任會長（依LWF資料2009年1月就職）；帶領EECMY持續高速增長至超過1000萬信徒；積極推動EECMY與全球信義宗社群的對話；2014年主導EECMY與路德會密蘇里教區（LCMS）正式對話；2017年第20屆大會後卸任'),

('約拿斯·伊格祖',
 'Yonas Yigezu',
 '亞的斯亞貝巴（信義）', '衣索比亞福音教會',
 6, 2017, NULL, NULL, '正統',
 'LWF news 2017; Union Presbyterian Seminary; EECMY 20th General Assembly Jan 2017',
 '第六任會長；2017年1月22至28日第20屆EECMY大會選出；普林斯頓神學院畢業（聯合長老會神學院校友）；上任時EECMY信眾已超過1000萬；繼續推動教會增長、神學教育及社會服務');

-- predecessor_id 鏈結：衣索比亞福音教會
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '亞的斯亞貝巴（信義）' AND church = '衣索比亞福音教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 4. 印尼巴塔克基督教（Huria Kristen Batak Protestan / HKBP）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('印尼巴塔克基督教主教座（棉蘭）',
 'Huria Kristen Batak Protestan (HKBP), Ephorus',
 '棉蘭',
 '印尼巴塔克基督教',
 '基督新教', NULL, '現存', 1861,
 'Victor Tinambunan（2024–）', 2024,
 '印尼北蘇門答臘棉蘭（Medan）',
 '印尼巴塔克基督教（Huria Kristen Batak Protestan，HKBP）1861年由德國萊茵傳道會（Rheinische Missionsgesellschaft）及路德維希·諾門森（Ludwig Ingwer Nommensen）在北蘇門答臘創立；以托巴巴塔克族（Toba Batak）為主要信眾群體；1930年正式成為獨立本土教會；最高領袖稱「主教」（Ephorus，源自希臘語「監督者」）；印尼最大的基督教宗派之一，信眾約400–500萬；1984至1990年西努安·安尼切圖斯·西托姆普爾（Sinahaan Anicetus Sitompul）曾出任LWF副會長；與世界信義宗聯盟（LWF）、世界教協（WCC）及印尼基督教協議會（PGI）為成員；總部設於北蘇門答臘省塔魯屯（Tarutung）珍珠佳修道院（Pearaja）。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承（歷任主教/Ephorus）：印尼巴塔克基督教
-- 注：諾門森時代（1881–1918）為創辦人時期；以下從1930年印尼首位主教記錄
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('路德維希·英格維爾·諾門森',
 'Ludwig Ingwer Nommensen',
 '棉蘭', '印尼巴塔克基督教',
 1, 1881, 1918, '逝世', '正統',
 'HKBP official history; Batak Christian Protestant Church Wikipedia; hkbp.or.id',
 '德國萊茵傳道會（RMG）傳教士；「巴塔克使徒」（Apostle of the Bataks）；1834年生於德國；1861年抵達北蘇門答臘托巴巴塔克地區傳教；1881年正式成立HKBP組織架構並出任首任主教（Ephorus）；深入巴塔克文化，翻譯聖經為巴塔克語；1918年逝世於北蘇門答臘，享壽84歲；被認為是HKBP奠基人'),

('瓦倫丁·克塞爾',
 'Valentin Kessel',
 '棉蘭', '印尼巴塔克基督教',
 2, 1918, 1920, '退休', '正統',
 'HKBP Ephorus list; seputarhkbp.blogspot.com; tagar.id',
 '諾門森逝世後代理主教（Pejabat Ephorus）；穩定了諾門森身後的教會過渡期；1920年由正式選出的主教接任'),

('約翰內斯·瓦爾內克',
 'Johannes Warneck',
 '棉蘭', '印尼巴塔克基督教',
 3, 1920, 1932, '退休', '正統',
 'HKBP Ephorus list; Batak Church history records',
 '第三任主教；萊茵傳道會傳教士；宗教學者，著有研究巴塔克宗教的重要著作（如《巴塔克人的宗教》）；在任期間HKBP持續增長'),

('P·蘭德格雷布',
 'P. Landgrebe',
 '棉蘭', '印尼巴塔克基督教',
 4, 1932, 1936, '退休', '正統',
 'HKBP Ephorus list; josuasilaen.blogspot.com',
 '第四任主教；萊茵傳道會傳教士任職期間；荷屬東印度（現印尼）殖民地時期'),

('E·維爾維比',
 'E. Verwiebe',
 '棉蘭', '印尼巴塔克基督教',
 5, 1936, 1940, '退休', '正統',
 'HKBP Ephorus list; hkbppearaja.blogspot.com',
 '第五任主教；二戰前夕任職；1940年移交予首位印尼本土巴塔克族主教'),

('賈斯汀·西霍姆邦',
 'Justin Sihombing',
 '棉蘭', '印尼巴塔克基督教',
 6, 1940, 1962, '退休', '正統',
 'HKBP official; tagar.id; seputarhkbp.blogspot.com; Batak Church Wikipedia',
 '首位巴塔克族本土主教（Ephorus Batak pertama，1940–1942年初為代理，1942年起正式）；任期橫跨荷蘭殖民地末期、日本佔領時期（1942–1945年）和印尼獨立初期；推動教會走向完全本土化、獨立化；1962年退休，任期超過20年，是HKBP在本土主教制度確立上最重要的人物'),

('T·S·西霍姆邦',
 'Ds. T. S. Sihombing',
 '棉蘭', '印尼巴塔克基督教',
 7, 1962, 1974, '退休', '正統',
 'HKBP Ephorus list; tagar.id; Batak Church records',
 '第七任主教；印尼獨立後教會快速增長期；推動教會組織現代化；與荷蘭、德國夥伴教會建立對等合作關係'),

('G·H·M·西阿漢',
 'G. H. M. Siahaan',
 '棉蘭', '印尼巴塔克基督教',
 8, 1974, 1987, '退休', '正統',
 'HKBP records; tagar.id; seputarhkbp.blogspot.com',
 '第八任主教；任期橫跨1970至1980年代蘇哈托新秩序（New Order）政治時期；推動HKBP與印尼政府的合作關係；任內信眾持續增長'),

('薩·阿·厄·納巴班',
 'Soritua Albert Ernst (S. A. E.) Nababan',
 '棉蘭', '印尼巴塔克基督教',
 9, 1987, 1998, '退休', '正統',
 'SAE Nababan Wikipedia; LWF obituary; suarakristen.com; tempo.co',
 '第九任主教（1987年1月31日第48屆大會選出）；曾任印尼基督教協議會（DGI/PGI）總幹事（1967–1984年）及LWF副會長（1970–1977年，1984–1990年）；是印尼及亞洲最具影響力的普世教會運動領袖之一；1998年退休；2021年5月8日逝世，享壽88歲'),

('J·R·胡塔魯克',
 'J. R. Hutauruk',
 '棉蘭', '印尼巴塔克基督教',
 10, 1998, 2004, '退休', '正統',
 'HKBP records; tagar.id; p2k.stekom.ac.id',
 '第十任主教；1998年第49屆大會選出；在任期間印尼處於1998年後民主化過渡期；帶領HKBP適應蘇哈托後的政治社會新環境'),

('博納爾·納比圖普盧',
 'Bonar Napitupulu',
 '棉蘭', '印尼巴塔克基督教',
 11, 2004, 2012, '退休', '正統',
 'HKBP; tokoh.id; tagar.id',
 '第十一任主教；2004年第51屆大會選出；任兩屆共8年；推動HKBP在印尼多元宗教社會中的發言權'),

('威廉·T·P·西馬爾馬塔',
 'Willem T. P. Simarmata',
 '棉蘭', '印尼巴塔克基督教',
 12, 2012, 2016, '逝世', '正統',
 'HKBP.or.id; tagar.id; hkbp.or.id memorial',
 '第十二任主教；2012年選出；任內逝世；HKBP官方網站設有專文紀念其「以愛服事」的風範'),

('達爾文·倫班托邦',
 'Darwin Lumbantobing',
 '棉蘭', '印尼巴塔克基督教',
 13, 2016, 2020, '退休', '正統',
 'HKBP; tagar.id; General Knowledge of HKBP (Scribd)',
 '第十三任主教；2016年選出；在任期間繼續推動HKBP的對外合作與全球信義宗關係'),

('羅賓遜·布塔爾布塔爾',
 'Robinson Butarbutar',
 '棉蘭', '印尼巴塔克基督教',
 14, 2020, 2024, '退休', '正統',
 'HKBP official; tagar.id; General Knowledge of HKBP (Scribd)',
 '第十四任主教；2020年選出；任內帶領HKBP度過COVID-19疫情衝擊；2024年退休'),

('維克托·蒂南布南',
 'Victor Tinambunan',
 '棉蘭', '印尼巴塔克基督教',
 15, 2024, NULL, NULL, '正統',
 'HKBP official; lutheranworld.org; HKBP Sinode Godang 2024',
 '第十五任主教；2024年選出；現任HKBP首席主教（Ephorus）；繼續帶領印尼最大信義宗教會逾400萬信徒');

-- predecessor_id 鏈結：印尼巴塔克基督教
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '棉蘭' AND church = '印尼巴塔克基督教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 5. 中美洲聖公宗（Iglesia Anglicana de la Region Central de America / IARCA）
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('中美洲聖公宗大主教座（瓜地馬拉城）',
 'Anglican Church in Central America (IARCA), Primate',
 '瓜地馬拉城（聖公宗）',
 '中美洲聖公宗',
 '基督新教', NULL, '現存', 1998,
 'Ramón Ovalle（2026–）', 2026,
 '瓜地馬拉市',
 '中美洲聖公宗（Iglesia Anglicana de la Region Central de America，IARCA）1998年正式成為聖公宗自治省，由哥斯大黎加、薩爾瓦多、瓜地馬拉、尼加拉瓜、巴拿馬五個教區組成；前身為美國聖公會（TEC）於中美洲的傳教區，各教區於1998年獲得自治；首任首席主教（Primate）為哥斯大黎加主教科尼利厄斯·威爾遜；大主教（Primate）頭銜由各屆省議會（Synod）選出，兼任其本教區主教；2026年4月最新選出第七任首席主教拉蒙·歐瓦列；全省約有5個教區、15萬信眾；普世聖公宗成員。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承（歷任首席主教/Primate）：中美洲聖公宗
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('科尼利厄斯·威爾遜',
 'Cornelius Joshua Wilson',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 1, 1998, 2002, '退休', '正統',
 'Anglican Church in Central America Wikipedia; Episcopal News Service; Anglican Communion',
 '中美洲聖公宗首任首席主教（1998年建省同時就任）；1978年祝聖為哥斯大黎加主教；哥斯大黎加本土主教；帶領中美洲教區於1998年脫離美國聖公會建立自治省；2002年卸任後退休'),

('馬丁·巴拉奧納',
 'Martín de Jesús Barahona',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 2, 2002, 2009, '退休', '正統',
 'Martín Barahona Wikipedia; Episcopal News Service; CNYEPISCOPAL obituary 2019',
 '第二任首席主教；2002年4月選出，薩爾瓦多教區主教；以在IARCA省內力推包容與公義教牧著稱；2003年出席吉恩·羅賓遜（Gene Robinson）祝聖禮一事引發保守派爭議；2019年3月逝世'),

('阿曼多·格拉·索里亞',
 'Armando Roman Guerra Soria',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 3, 2009, 2015, '退休', '正統',
 'Episcopal News Service; Anglican Communion; Sturdie Downs installation ENS 2015',
 '第三任首席主教；瓜地馬拉教區主教；2009年就任；帶領IARCA持續推動社會正義工作；2015年卸任後由尼加拉瓜主教接任'),

('斯特迪·唐斯',
 'Sturdie Wyman Downs',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 4, 2015, 2018, '退休', '正統',
 'Episcopal News Service 2015/03/12; Anglican Ink 2015; Anglican Communion News',
 '第四任首席主教；尼加拉瓜教區主教；2015年2月21日安裝就職禮；以尼加拉瓜為基地，繼續推動IARCA省際合作；2018年在哥斯大黎加第六屆省議會後退任'),

('胡利奧·穆雷·湯普森',
 'Julio Murray Thompson',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 5, 2018, 2022, '退休', '正統',
 'Anglican Ink 2018; Anglican News 2018; Julio Murray Wikipedia; UBE installation notice',
 '第五任首席主教（依UBE記錄稱「第六任」，計算方式含早期主教）；巴拿馬教區主教；2018年4月哥斯大黎加第六屆省議會選出；2018年8月大主教區安裝禮就職；出席2016年GAFCON大會；推動IARCA與拉丁美洲其他聖公宗省份合作'),

('胡安·達維·阿爾瓦拉多',
 'Juan David Alvarado Melgar',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 6, 2022, 2026, '退休', '正統',
 'The Living Church; Juan David Alvarado Wikipedia; Anglican Communion',
 '第六任首席主教；薩爾瓦多教區主教；2022年選出任四年期；2014年曾選為薩爾瓦多主教（第二輪投票）；任內繼續推動IARCA在中美洲的社會正義使命'),

('拉蒙·歐瓦列',
 'Ramón Ovalle',
 '瓜地馬拉城（聖公宗）', '中美洲聖公宗',
 7, 2026, NULL, NULL, '正統',
 'Episcopal News Service 2026/04/28; Anglican Ink 2026/04/28',
 '第七任首席主教；2026年4月24至26日第八屆省議會選出；接替阿爾瓦拉多；為IARCA最新任首席主教');

-- predecessor_id 鏈結：中美洲聖公宗
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '瓜地馬拉城（聖公宗）' AND church = '中美洲聖公宗'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;


-- ============================================================
-- 6. 莫三比克聖公宗（Igreja Anglicana de Moçambique e Angola / IAMA）
-- ============================================================
-- 注：本教會2021年正式建省，前身為英國聖公宗南非省（ACSA）屬下的黎邦博（Lebombo）教區等。
-- 莫三比克聖公宗的歷史可追溯到1893年建立的黎邦博教區。
-- 本記錄以「莫三比克聖公宗」為church名，see_zh='馬普托（聖公宗）'，
-- 反映建省前首席主教座所在地及最重要的歷史主教。

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, status, founded_year,
   current_patriarch_zh, incumbent_since, location, notes)
VALUES
('莫三比克聖公宗大主教座（馬普托）',
 'Igreja Anglicana de Moçambique e Angola (IAMA), Primate',
 '馬普托（聖公宗）',
 '莫三比克聖公宗',
 '基督新教', NULL, '現存', 1893,
 'Vicente Msosa（2025–）', 2025,
 '莫三比克馬普托',
 '莫三比克聖公宗（Igreja Anglicana de Moçambique e Angola，IAMA）的前身為聖公宗南非省（ACSA）下轄的黎邦博教區（Diocese of Lebombo，1893年建立）；1979年從黎邦博教區分設尼亞薩教區（Niassa）；2019年新設南安普拉教區（Nampula）；2021年8月24日聖公宗諮議會正式批准建省，同年9月24日正式宣告成立，成為聖公宗第42個省份，由莫三比克8個教區及安哥拉4個教區共12個教區組成；首任代理首席主教為卡洛斯·馬辛尼；2024年11月選出維森特·姆索薩為第一任正式首席主教，2025年1月26日就職；迪尼斯·森古拉內（Dinis Sengulane，1976–2014年）任黎邦博主教38年，是聖公宗任期最長的在任主教之一，並在1992年莫三比克內戰和平進程中扮演重要調解角色。')
ON CONFLICT (see_zh, church) DO NOTHING;

-- 主教傳承（黎邦博歷任主教及IAMA建省後首席主教）：莫三比克聖公宗
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year,
   end_reason, status, sources, notes)
VALUES
('拉爾夫·霍普金斯',
 'Ralph Hulme Hopkins',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 1, 1893, 1903, '辭職', '正統',
 'Diocese of Lebombo history; ALMA link history',
 '黎邦博教區首任主教（1893年黎邦博從納塔爾教區分出）；英國傳教士；建立莫三比克南部聖公宗教會基礎；任期涵蓋葡屬莫三比克時期'),

('法蘭克·赫因斯',
 'Frederick Haines',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 2, 1903, 1919, '退休', '正統',
 'Diocese of Lebombo; ALMA link history',
 '第二任黎邦博主教；任期橫跨第一次世界大戰時期；在葡屬莫三比克繼續拓展聖公宗事工'),

('約翰·麥肯',
 'John Nunn',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 3, 1921, 1935, '退休', '正統',
 'Diocese of Lebombo history',
 '第三任黎邦博主教；任期為兩次大戰之間'),

('諾曼·賓頓',
 'Norman Binyon',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 4, 1935, 1951, '退休', '正統',
 'Diocese of Lebombo history',
 '第四任黎邦博主教；任期橫跨第二次世界大戰；葡屬莫三比克殖民地時期'),

('奧利弗·格林-威爾金森',
 'Oliver Green-Wilkinson',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 5, 1952, 1976, '退休', '正統',
 'Diocese of Lebombo history; Dinis Sengulane Wikipedia',
 '第五任黎邦博主教；任期橫跨葡屬莫三比克獨立前後（莫三比克1975年獨立）；見證葡屬莫三比克殖民地終結及新國家建立'),

('迪尼斯·森古拉內',
 'Dinis Sengulane',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 6, 1976, 2014, '退休', '正統',
 'Dinis Sengulane Wikipedia; MANNA Anglican; Diocese of Lebombo; Episcopal News Service',
 '第六任黎邦博主教；首位莫三比克本土出生的黑人主教；1976年祝聖，在位38年，為聖公宗任期最長的在任主教之一；在1992年莫三比克內戰和平進程（羅馬和約）中扮演關鍵調解角色，幫助促成RENAMO游擊隊與FRELIMO政府停火；推動武器銷毀換取藝術工具計劃（「砍劍犁鋤」，Swords into Ploughshares），將約60萬把武器轉化為藝術品；2014年退休'),

('卡洛斯·馬辛尼',
 'Carlos Matsinhe',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 7, 2014, 2021, '晉升', '正統',
 'Anglican Communion; Episcopal News Service 2021; Anglican News Service 2021',
 '第七任黎邦博主教（2014年繼任森古拉內）；2021年9月IAMA建省後任代理首席主教（Acting Presiding Bishop）；帶領莫三比克聖公宗完成建省過渡程序；在IAMA省成立後持續服事至選出正式首席主教'),

('維森特·姆索薩',
 'Vicente Msosa',
 '馬普托（聖公宗）', '莫三比克聖公宗',
 8, 2025, NULL, NULL, '正統',
 'Episcopal News Service 2025/01/27; Anglican News Service 2025/01; The Living Church 2024',
 '第一任IAMA正式首席主教（Primate）；2024年11月選出；2025年1月26日正式就職安裝；為IAMA成立後第一位通過正式選舉程序產生的首席主教；年輕一代領袖，象徵莫三比克聖公宗新世代發展');

-- predecessor_id 鏈結：莫三比克聖公宗
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '馬普托（聖公宗）' AND church = '莫三比克聖公宗'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- END OF FILE
-- ============================================================
