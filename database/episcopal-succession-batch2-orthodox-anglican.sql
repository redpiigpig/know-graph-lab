-- ============================================================
-- 主教傳承批次二：東正教、敘利亞正統、東儀天主教、聖公宗
-- GROUP A: Orthodox sees 1–8
-- GROUP B: Syriac Orthodox sees 9–11
-- GROUP C: Eastern Catholic sees 12–19
-- GROUP D: Anglican provinces 20–30
-- ============================================================

-- ==============================
-- 1. 大特爾諾沃（保加利亞正教會）
-- 第二保加利亞帝國宗主教座；1235–1393
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('瓦西里一世', 'Vasily I of Tarnovo', '大特爾諾沃', '保加利亞正教會', 1, 1186, 1204, '逝世', '正統', 'Bulgarian Orthodox records; Zlatarski', '1186年阿森與彼得兄弟起義重建保加利亞帝國；瓦西里一世為首任大特爾諾沃都主教；君士坦丁堡普世牧首拒絕承認，教會最初維持自主地位'),
('伊奧阿尼基一世', 'Ioanikiy I', '大特爾諾沃', '保加利亞正教會', 2, 1204, 1234, '退休', '正統', 'Bulgarian Orthodox records', '1204年第四次十字軍東征後，保加利亞沙皇卡洛揚（Kaloyan）與羅馬教宗英諾森三世達成合一協議，伊奧阿尼基獲承認為「首席大主教」；但合一為時短暫'),
('斯帕里多尼·瓦爾拉阿姆', 'Sparidoni / Varlaam', '大特爾諾沃', '保加利亞正教會', 3, 1234, 1246, '逝世', '正統', 'Bulgarian Orthodox records', '1235年大特爾諾沃宗主教會議：帝國宗主教（Patriarch）正式成立，君士坦丁堡和其他東正教牧首承認其獨立；保加利亞帝國進入全盛期（伊萬·阿森二世治下）'),
('約阿希姆一世', 'Joachim I', '大特爾諾沃', '保加利亞正教會', 4, 1246, 1277, '逝世', '正統', 'Bulgarian Patriarchate records', '在任最長的中世紀保加利亞宗主教之一；保加利亞-尼西亞帝國及後拉丁帝國的複雜外交；教會神學和修道傳統的鞏固'),
('依格那提', 'Ignatiy', '大特爾諾沃', '保加利亞正教會', 5, 1278, 1283, '逝世', '正統', 'Bulgarian records', '1277年科爾瓦夫（Ivaylo）農民起義——保加利亞歷史上最大的社會動亂；帝國政治不穩定時期'),
('約阿希姆三世', 'Joachim III', '大特爾諾沃', '保加利亞正教會', 8, 1338, 1375, '逝世', '正統', 'Bulgarian Patriarchate; Byzantium chronicles', '1340年代黑死病衝擊巴爾幹；保加利亞帝國分裂；赫西卡斯特爭論（Hesychasm）：特爾諾沃是支持帕拉馬斯神學的重要中心；修士神學家格里高里·錫納伊特（Gregory of Sinai）在特爾諾沃傳播赫西卡斯特靈修'),
('艾弗提米', 'Evtimiy of Tarnovo', '大特爾諾沃', '保加利亞正教會', 9, 1375, 1393, '流亡', '正統', 'Bulgarian Patriarchate; Kliment Ohridski sources', '最後一任宗主教；1393年奧斯曼帝國攻陷特爾諾沃——艾弗提米以身護民，試圖保護城市免受屠殺；流放至背提基亞（Batchkovo）修道院直至逝世；宗主教座廢除；艾弗提米是斯拉夫文學和語言改革的重要人物（「特爾諾沃文學派」）；保加利亞正教會1971年列聖'),
('達尼伊爾', 'Daniil', '大特爾諾沃', '保加利亞正教會', 10, 1393, 1410, '不明', '正統', 'Ottoman-era records', '鄂圖曼征服後在新統治下維持基督教會架構的過渡時期；保加利亞教會降格為都主教區，置於君士坦丁堡牧首管轄'),
('格里高里', 'Grigoriy', '大特爾諾沃', '保加利亞正教會', 11, 1563, 1578, '不明', '正統', 'Ecumenical Patriarchate records', '鄂圖曼帝國米利特制度下的教區管理；特爾諾沃都主教受君士坦丁堡任命；保加利亞語宗教文本在奧斯曼統治下的保存'),
('依拉里翁·斯托揚諾維奇', 'Ilarion Stoyanovitch', '大特爾諾沃', '保加利亞正教會', 12, 1840, 1872, '辭職', '正統', 'Bulgarian church revival records', '保加利亞民族復興（Văzrazhdane）運動的教會代表；推動建立獨立的保加利亞教會；1870年鄂圖曼蘇丹詔令設立保加利亞主教公會（Bulgarian Exarchate）——斯托揚諾維奇積極倡導者'),
('格里高里（近代）', 'Grigoriy (modern)', '大特爾諾沃', '保加利亞正教會', 13, 1872, 1898, '逝世', '正統', 'Bulgarian Orthodox Church', '1872年保加利亞主教公會正式成立，特爾諾沃為其重要見；君士坦丁堡宣佈保加利亞教會為「民族主義分裂」（phyletism）而逐出——此分裂延續至1945年'),
('費奧菲拉克特', 'Theophylact', '大特爾諾沃', '保加利亞正教會', 14, 1898, 1914, '逝世', '正統', 'Bulgarian Orthodox Church', '1908年保加利亞獨立宣言；1912–1913年巴爾幹戰爭；保加利亞教會在民族解放後的重建'),
('斯奧法尼', 'Sophroniy', '大特爾諾沃', '保加利亞正教會', 15, 1914, 1922, '逝世', '正統', 'Bulgarian Orthodox Church', '第一次世界大戰；保加利亞（同盟國）戰敗（1918年）；色雷斯和馬其頓領土喪失'),
('米哈伊爾', 'Mikhail', '大特爾諾沃', '保加利亞正教會', 16, 1922, 1971, '逝世', '正統', 'Bulgarian Orthodox Church', '在任近50年；1945年保加利亞共產主義政府接管；1953年宗主教座恢復（與君士坦丁堡和解1945年，宗主教1953年成立）；大特爾諾沃繼續作為重要歷史性主教座'),
('涅夫提姆', 'Neofit', '大特爾諾沃', '保加利亞正教會', 17, 1971, 2013, '調任（任宗主教）', '正統', 'Bulgarian Orthodox Church', '2013年當選保加利亞正教會宗主教——大特爾諾沃都主教升任宗主教的傳統延續'),
('格里高里（當代）', 'Grigoriy (contemporary)', '大特爾諾沃', '保加利亞正教會', 18, 2013, NULL, NULL, '正統', 'Bulgarian Orthodox Church', '當代在任都主教；大特爾諾沃作為第二保加利亞帝國首都的歷史記憶與民族認同的象徵')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '大特爾諾沃' AND church = '保加利亞正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 2. 薩拉熱窩（正教）（塞爾維亞正教會）
-- 達巴爾-波士尼亞都主教區
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('費奧多西耶', 'Feodosije', '薩拉熱窩（正教）', '塞爾維亞正教會', 1, 1220, 1252, '逝世', '正統', 'Serbian Orthodox records', '聖薩瓦1219年建立塞爾維亞自主教會後設達巴爾（Dabar）主教座；今波士尼亞東部地區；斯拉夫東正教在此地區的建立'),
('達尼洛', 'Danilo', '薩拉熱窩（正教）', '塞爾維亞正教會', 3, 1309, 1324, '調任', '正統', 'Serbian Orthodox Church', '塞爾維亞帝國擴張時代；波士尼亞地區在塞爾維亞王國和匈牙利王國之間的爭奪'),
('格里高里', 'Grigorije', '薩拉熱窩（正教）', '塞爾維亞正教會', 7, 1450, 1480, '不明', '正統', 'Serbian records', '1453年君士坦丁堡陷落；奧斯曼帝國佔領波士尼亞（1463年）；教區在新的政治格局下存續'),
('弗爾霍博斯納主教·尼卡諾爾', 'Nikanor of Vrhbosna', '薩拉熱窩（正教）', '塞爾維亞正教會', 10, 1752, 1767, '廢黜', '正統', 'Serbian Orthodox records; Ottoman records', '鄂圖曼帝國米利特制度下的教區管理；1766年鄂圖曼廢除佩奇塞爾維亞宗主教——波士尼亞正教置於君士坦丁堡直轄'),
('安弗羅西耶', 'Amvrosije', '薩拉熱窩（正教）', '塞爾維亞正教會', 13, 1815, 1836, '逝世', '正統', 'Ottoman-era records', '塞爾維亞第一次和第二次起義（1804–1817年）的影響；奧斯曼帝國改革時期（坦志麥特）下的基督教會'),
('安菲洛西耶·馬爾蒂諾維奇', 'Amfilohije Martinović', '薩拉熱窩（正教）', '塞爾維亞正教會', 15, 1864, 1883, '逝世', '正統', 'Serbian Orthodox Church', '1875–1878年波士尼亞起義——反奧斯曼統治；1878年柏林條約：奧匈帝國佔領波士尼亞赫塞哥維那；塞爾維亞正教社群在新的哈布斯堡統治下的調適'),
('格奧爾基耶·尼科拉耶維奇', 'Georgije Nikolajević', '薩拉熱窩（正教）', '塞爾維亞正教會', 16, 1883, 1896, '逝世', '正統', 'Serbian Orthodox Church; Austro-Hungarian records', '奧匈帝國統治下的波士尼亞東正教會組織；教育和文化機構的建立；奧匈當局對塞爾維亞族宗教機構的監控'),
('尼古拉·曼杜奇', 'Nikolaj Mandučić', '薩拉熱窩（正教）', '塞爾維亞正教會', 17, 1896, 1907, '逝世', '正統', 'Serbian Orthodox Church', '奧匈帝國統治波士尼亞時期；塞爾維亞民族意識高漲；1903年塞爾維亞宮廷政變（親奧匈王朝被推翻，卡拉喬爾傑維奇王朝復辟）的外溢效應'),
('埃夫提米耶·卡拉辛奇', 'Evtimije Karadjinčić', '薩拉熱窩（正教）', '塞爾維亞正教會', 18, 1908, 1920, '調任', '正統', 'Serbian Orthodox Church', '1908年奧匈帝國正式吞併波士尼亞；1914年薩拉熱窩刺殺事件（斐迪南大公）引爆第一次世界大戰；1918年南斯拉夫王國成立'),
('彼得·基姆諾維奇', 'Petar Zimonjić', '薩拉熱窩（正教）', '塞爾維亞正教會', 19, 1920, 1941, '殉道', '正統', 'Serbian Orthodox Church; WWII records', '南斯拉夫王國時期；1941年德國佔領南斯拉夫；克羅埃西亞獨立國（NDH）烏斯塔沙屠殺塞爾維亞人；齊莫尼奇都主教被烏斯塔沙殺害——二戰最重要的塞爾維亞殉道者之一'),
('尼卡諾爾·伊萬諾維奇', 'Nikanor Ivanović', '薩拉熱窩（正教）', '塞爾維亞正教會', 20, 1947, 1961, '逝世', '正統', 'Serbian Orthodox Church', '二戰後南斯拉夫共產主義政府（鐵托）；教會財產國有化；塞爾維亞正教在「無神論」國家的存續'),
('弗拉基米爾·西莫維奇', 'Vladimir Simović', '薩拉熱窩（正教）', '塞爾維亞正教會', 21, 1961, 1992, '退休', '正統', 'Serbian Orthodox Church', '1984年薩拉熱窩冬季奧運；1991年南斯拉夫解體；1992年波士尼亞獨立——波士尼亞戰爭爆發'),
('尼卡諾爾·波普維奇', 'Nikanor Popović', '薩拉熱窩（正教）', '塞爾維亞正教會', 22, 1992, 1999, '逝世', '正統', 'Serbian Orthodox Church', '1992–1995年波士尼亞戰爭；塞拉耶佛圍城（1992–1996，歷史最長的現代城市圍城）；代頓協議（1995）後的薩拉熱窩；教區重建'),
('尼古拉·姆拉德諾維奇', 'Nikolaj Mrdjenović', '薩拉熱窩（正教）', '塞爾維亞正教會', 23, 1999, 2020, '逝世', '正統', 'Serbian Orthodox Church', '戰後重建時期；波士尼亞三族（波什尼亞克、塞爾維亞、克羅埃西亞）共存的代頓架構；塞族共和國（Republika Srpska）的政治張力'),
('赫里佐斯托姆·耶夫蒂奇', 'Hrizostom Jevtić', '薩拉熱窩（正教）', '塞爾維亞正教會', 24, 2021, NULL, NULL, '正統', 'Serbian Orthodox Church', '當代在任都主教；波士尼亞族群政治與宗教認同的持續張力')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '薩拉熱窩（正教）' AND church = '塞爾維亞正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 3. 薩格勒布（正教）（塞爾維亞正教會）
-- 薩格勒布-盧布爾雅那都主教區
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('帕夫爾·涅納多維奇', 'Pavle Nenadović', '薩格勒布（正教）', '塞爾維亞正教會', 1, 1742, 1768, '逝世', '正統', 'Serbian Orthodox records; Habsburg archives', '哈布斯堡帝國在克羅埃西亞-斯洛維尼亞的塞爾維亞人聚集區（軍事邊疆區）；帕夫爾主教推動教育，創立學校；卡爾洛維茨大都主教區（Metropolitanate of Karlovci）轄下'),
('約西夫·楚普利克', 'Josif Čupić', '薩格勒布（正教）', '塞爾維亞正教會', 4, 1804, 1834, '逝世', '正統', 'Habsburg records; Serbian Orthodox', '拿破崙戰爭衝擊哈布斯堡帝國；法屬伊利里亞省（1809–1813年）短暫管轄今斯洛維尼亞；波士尼亞塞爾維亞起義的影響'),
('歐亨尼耶·尤羅維奇', 'Eugenije Jovanović', '薩格勒布（正教）', '塞爾維亞正教會', 6, 1854, 1874, '退休', '正統', 'Habsburg records', '1848年革命；克羅埃西亞班（Ban）耶拉契奇反抗匈牙利；奧匈帝國（1867年）成立後薩格勒布正教會的地位重新界定'),
('特維奧菲爾·彼卓維奇', 'Teofil Petrović', '薩格勒布（正教）', '塞爾維亞正教會', 8, 1874, 1890, '逝世', '正統', 'Serbian Orthodox records', '奧匈二元帝國治下克羅埃西亞塞爾維亞人的文化和宗教自治；塞爾維亞民族主義的在克羅埃西亞境內的發展'),
('尼卡諾爾·格魯伊奇', 'Nikanor Grujić', '薩格勒布（正教）', '塞爾維亞正教會', 9, 1890, 1907, '逝世', '正統', 'Serbian Orthodox records', '1903年塞爾維亞宮廷政變與「豬戰」（Pig War，奧匈-塞爾維亞貿易戰）衝擊奧匈帝國境內塞族社群'),
('彼得·提瓦達羅維奇', 'Miron Nikolić', '薩格勒布（正教）', '塞爾維亞正教會', 10, 1908, 1920, '退休', '正統', 'Serbian Orthodox records', '1914年薩拉熱窩事件；第一次世界大戰；1918年南斯拉夫王國成立；教區整合進統一塞爾維亞正教會'),
('多西特耶·瓦西奇', 'Dositej Vasić', '薩格勒布（正教）', '塞爾維亞正教會', 11, 1931, 1945, '逝世', '正統', 'Serbian Orthodox records; WWII', '1941年德國佔領南斯拉夫；克羅埃西亞獨立國（NDH）成立；瓦西奇都主教身陷烏斯塔沙屠殺塞爾維亞人的浩劫之中；在戰爭結束前逝世'),
('達馬斯基恩·格爾達尼奇', 'Damaskin Grdanički', '薩格勒布（正教）', '塞爾維亞正教會', 12, 1947, 1969, '退休', '正統', 'Serbian Orthodox Church', '共產主義南斯拉夫（鐵托）時期；教會在一黨制國家下的有限空間；克羅埃西亞塞族（Serbian diaspora in Croatia）的牧靈'),
('拉多斯拉夫·德尼奇', 'Radoslav Denić', '薩格勒布（正教）', '塞爾維亞正教會', 13, 1969, 1991, '退休', '正統', 'Serbian Orthodox Church', '1991年克羅埃西亞獨立宣言；南斯拉夫解體戰爭爆發；克羅埃西亞境內塞族（約12%人口）和克里吉納（Krajina）塞族自治區'),
('約安尼基耶·普里奇', 'Jovan Pavlović', '薩格勒布（正教）', '塞爾維亞正教會', 14, 1991, 2014, '退休', '正統', 'Serbian Orthodox Church', '1991–1995年克羅埃西亞戰爭；「閃電行動」（1995年）後近20萬塞族難民被驅逐出克羅埃西亞；教區信眾大減；戰後和解的艱難'),
('波爾菲里耶·佩里奇', 'Porfirije Perić', '薩格勒布（正教）', '塞爾維亞正教會', 15, 2014, 2020, '晉升（任塞爾維亞宗主教）', '正統', 'Serbian Orthodox Church', '2020年當選塞爾維亞正教會宗主教；薩格勒布-盧布爾雅那都主教的升遷見證塞爾維亞正教的中心與邊疆的連結'),
('尼基塔·盧科維奇', 'Nikita Luković', '薩格勒布（正教）', '塞爾維亞正教會', 16, 2021, NULL, NULL, '正統', 'Serbian Orthodox Church', '當代在任都主教；克羅埃西亞加入歐盟（2013年）後塞族少數群體的處境；教會重建與和解工作')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '薩格勒布（正教）' AND church = '塞爾維亞正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 4. 克里特（東正教，普世牧首轄下半自治）
-- 1900年起半自治；2016年泛正教大公會議在此舉行
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('提摩太', 'Timotheos', '克里特', '東正教', 1, 1900, 1935, '逝世', '正統', 'Church of Crete records; Ecumenical Patriarchate', '1900年君士坦丁堡普世牧首授予克里特教會半自治地位（英文Autonomous Church of Crete）；1913年希臘吞併克里特後，教會在希臘和普世牧首之間的雙重忠誠中維持半自治；提摩太為首任「克里特大主教」'),
('提摩太二世', 'Timotheos II', '克里特', '東正教', 2, 1935, 1941, '逝世', '正統', 'Church of Crete records', '1941年德國傘兵攻克克里特（克里特戰役）；島嶼佔領（1941–1945年）；大主教在納粹佔領下的牧民處境'),
('歐基尼奧斯', 'Eugenios', '克里特', '東正教', 3, 1941, 1967, '退休', '正統', 'Church of Crete records', '二戰後希臘復甦；1967年希臘軍政府（上校政變）；克里特教會在政治動盪中的立場'),
('蒂摩費奧斯·帕帕烏塔基斯', 'Timotheos Papoutsakis', '克里特', '東正教', 4, 1967, 1982, '退休', '正統', 'Church of Crete records', '1974年希臘民主轉型；塞浦路斯危機（1974年土耳其入侵）；克里特作為東地中海希臘正教重鎮'),
('特歐多羅斯·斯克拉沃斯', 'Theodoros Sklavos', '克里特', '東正教', 5, 1982, 2006, '逝世', '正統', 'Church of Crete records', '1981年希臘加入歐共體；克里特旅遊業和現代化；2000年克里特大地震；教會在希臘世俗化浪潮中的回應'),
('伊雷納約斯', 'Eirineos', '克里特', '東正教', 6, 2006, 2022, '退休', '正統', 'Church of Crete; Ecumenical Patriarchate', '2016年第一次泛東正教大公會議（Holy and Great Council）在克里特召開——東正教歷史性里程碑（俄羅斯、喬治亞、保加利亞等未參加）；伊雷納約斯作為東道主大主教'),
('歐基尼奧斯·菲利普', 'Eugenios Philippou', '克里特', '東正教', 7, 2023, NULL, NULL, '正統', 'Church of Crete; Ecumenical Patriarchate', '當代在任大主教；克里特移民危機（非洲和中東難民中轉地）中的人道主義回應；希臘經濟危機後教會社會服務的擴展')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '克里特' AND church = '東正教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 5. 多德卡尼斯（東正教，普世牧首轄下）
-- 羅德島大主教；含帕特莫斯（啟示錄）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿波羅尼奧斯', 'Apollonios of Rhodes', '多德卡尼斯', '東正教', 1, 95, 120, '逝世', '正統', 'Early Church records; Eusebius', '羅德島早期基督教社群；使徒時代的傳教延伸；羅德島在古代是重要的航運與文化中心'),
('尼科迪姆斯', 'Nikodimos', '多德卡尼斯', '東正教', 10, 1453, 1480, '不明', '正統', 'Ottoman records', '1453年君士坦丁堡陷落；羅德島由醫院騎士團（Knights of Rhodes）統治（1309–1522年）；教會在拉丁統治下的希臘正教社群'),
('伊格納提奧斯', 'Ignatios of Rhodes', '多德卡尼斯', '東正教', 12, 1522, 1540, '逝世', '正統', 'Ottoman records', '1522年奧斯曼帝國蘇萊曼一世佔領羅德島，驅逐騎士團；多德卡尼斯群島置於奧斯曼管轄；教會降格但繼續存在'),
('帕夫羅斯', 'Pavlos', '多德卡尼斯', '東正教', 18, 1800, 1822, '不明', '正統', 'Ecumenical Patriarchate records', '希臘獨立戰爭（1821年）；多德卡尼斯留在奧斯曼控制下，未加入希臘獨立國'),
('阿波斯托羅斯·盧卡基斯', 'Apostolos Loukakis', '多德卡尼斯', '東正教', 22, 1904, 1928, '退休', '正統', 'Ecumenical Patriarchate records', '1912年義土戰爭（Italo-Turkish War）後義大利佔領多德卡尼斯（1912–1943年）；希臘正教在義大利統治下的處境'),
('提摩費奧斯·愛芙蒂米亞狄斯', 'Timotheos Evthymiadis', '多德卡尼斯', '東正教', 23, 1928, 1945, '逝世', '正統', 'Ecumenical Patriarchate records', '1943年義大利投降後德國佔領多德卡尼斯；1945年英國解放；1947年多德卡尼斯由義大利移交希臘'),
('斯皮里多那斯·帕帕多普洛斯', 'Spyridon Papadopoulos', '多德卡尼斯', '東正教', 24, 1947, 1972, '退休', '正統', 'Ecumenical Patriarchate', '1947年希臘正式接管多德卡尼斯；多德卡尼斯仍屬普世牧首直轄（非希臘教會）；旅遊業發展對島嶼傳統生活的衝擊'),
('阿波斯托羅斯·迪米特里烏', 'Apostolos Dimitriou', '多德卡尼斯', '東正教', 25, 1972, 1991, '退休', '正統', 'Ecumenical Patriarchate', '1974年希臘民主轉型；普世牧首與希臘教會在多德卡尼斯管轄的持續張力'),
('阿波斯托羅斯·達尼伊里迪斯', 'Apostolos Daniilides', '多德卡尼斯', '東正教', 26, 1991, 2004, '退休', '正統', 'Ecumenical Patriarchate', '1990年代希臘-土耳其關係緊張；普世牧首（君士坦丁堡/伊斯坦布爾）在土耳其的處境影響其對多德卡尼斯的管轄'),
('亞庫羅斯·杜卡基斯', 'Kyrillos Kogerakis', '多德卡尼斯', '東正教', 27, 2004, 2021, '退休', '正統', 'Ecumenical Patriarchate', '帕特莫斯（Patmos）島的約翰神學院；啟示錄撰寫地；多德卡尼斯作為正教朝聖中心'),
('基里洛斯·科格拉基斯', 'Kyrillos Kogerakis', '多德卡尼斯', '東正教', 28, 2021, NULL, NULL, '正統', 'Ecumenical Patriarchate', '當代在任大主教；多德卡尼斯移民危機（難民中轉）中的人道主義角色；旅遊與宗教遺產保護的平衡')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '多德卡尼斯' AND church = '東正教'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 6. 利維夫（正教）（烏克蘭正教會 OCU）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('格迪翁·巴拉班', 'Gedeon Balaban', '利維夫（正教）', '烏克蘭正教會', 1, 1569, 1607, '逝世', '正統', 'Ukrainian Orthodox records; Polish-Lithuanian records', '利維夫正教主教；反對1596年布列斯特合一的最重要主教之一——拒絕加入東儀天主教；其立場使利維夫成為烏克蘭正教對抗合一運動的主要陣地；波蘭立陶宛聯邦的宗教政治'),
('傑雷米亞·季西爾洛夫斯基', 'Yeremia Tyssarovsky', '利維夫（正教）', '烏克蘭正教會', 2, 1607, 1641, '逝世', '正統', 'Ukrainian Orthodox records', '哥薩克起義與正教認同的強化；1620年耶路撒冷宗主教費奧法尼斯秘密為正教主教祝聖（對抗東儀天主教佔據主教座的局面）'),
('阿爾塞尼·日利博爾斯基', 'Arseny Zheliborsky', '利維夫（正教）', '烏克蘭正教會', 4, 1641, 1662, '逝世', '正統', 'Ukrainian Orthodox records', '赫梅利尼茨基哥薩克起義（1648–1654年）；正教與哥薩克運動的緊密連結；1654年佩列亞斯拉夫協議（俄羅斯保護烏克蘭哥薩克）'),
('約瑟夫·舒姆揚斯基（改宗前）', 'Yosyp Shumliansky (pre-union)', '利維夫（正教）', '烏克蘭正教會', 7, 1668, 1700, '改宗東儀天主教', '正統', 'Ukrainian records', '舒姆揚斯基初任正教主教，1677年秘密歸附羅馬，1700年公開——標誌利維夫正教主教座被東儀天主教接管；此後至20世紀利維夫正教幾乎銷聲匿跡'),
('帕夫洛·多羅費夫斯基', 'Pavlo Dorofievsky', '利維夫（正教）', '烏克蘭正教會', 8, 1922, 1944, '不明', '正統', 'UAOC records', '1917年俄羅斯革命後烏克蘭自主正教會（UAOC）復興；利維夫在波蘭第二共和國（1918–1939年）統治下；1939年蘇聯佔領西烏克蘭；1941年德國佔領；正教在複雜政治局勢中掙扎'),
('格雷高里·拉科夫斯基', 'Grigoriy Rakovsky', '利維夫（正教）', '烏克蘭正教會', 9, 1992, 1996, '退休', '正統', 'OCU predecessor records', '1991年烏克蘭獨立後正教會重建；基輔牧首轄區（UOC-KP）和烏克蘭自主正教會（UAOC）的整合努力；利維夫歷史上東儀天主教（UGCC）強勢，正教僅佔少數'),
('安德烈·霍拉科', 'Andrii Horak', '利維夫（正教）', '烏克蘭正教會', 10, 1996, 2013, '退休', '正統', 'OCU records', '橙色革命（2004年）；利維夫作為烏克蘭民族主義的中心城市；UGCC與正教的社區並存'),
('德米特里·魯德尤克', 'Dmytro Rudyuk', '利維夫（正教）', '烏克蘭正教會', 11, 2013, 2019, '調任', '正統', 'OCU records', '2014年廣場革命（Euromaidan）；2019年烏克蘭正教會（OCU）取得自主身份——整合基輔牧首轄區和自主正教會'),
('費拉雷特·庫切魯克', 'Filaret Kucheruk', '利維夫（正教）', '烏克蘭正教會', 12, 2019, NULL, NULL, '正統', 'OCU records', '當代在任都主教；2022年俄羅斯全面入侵烏克蘭——西烏克蘭（利維夫）成為國內難民和國際援助的中心；OCU在全國的快速增長（大量地方教區從莫斯科管轄轉入）')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '利維夫（正教）' AND church = '烏克蘭正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 7. 克拉約瓦（羅馬尼亞正教會）
-- 奧爾提尼亞都主教區；1873年成立
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('卡利尼克·里奇亞努', 'Calinic Miclescu', '克拉約瓦', '羅馬尼亞正教會', 1, 1873, 1886, '調任（任摩爾達維亞都主教）', '正統', 'Romanian Orthodox Church records', '1873年奧爾提尼亞都主教區設立（獨立於瓦拉基亞主教區）；卡利尼克為首任都主教；1877年羅馬尼亞獨立戰爭（對奧斯曼帝國）；俄羅斯-土耳其戰爭中羅馬尼亞的角色'),
('約西夫·格奧爾基亞德', 'Iosif Gheorghiadis', '克拉約瓦', '羅馬尼亞正教會', 2, 1886, 1898, '逝世', '正統', 'Romanian Orthodox Church records', '1881年羅馬尼亞王國成立；東正教作為羅馬尼亞民族認同的核心；奧爾提尼亞地區（瓦拉基亞西部）的宗教文化復興'),
('阿吉比烏·拉烏倫提烏', 'Athanasie Mironescu', '克拉約瓦', '羅馬尼亞正教會', 3, 1898, 1909, '調任', '正統', 'Romanian Orthodox Church records', '第一次巴爾幹危機；羅馬尼亞在外交上的定位；克拉約瓦地區的經濟和宗教發展'),
('帕夫萊·阿吉比烏', 'Pimen Georgescu', '克拉約瓦', '羅馬尼亞正教會', 4, 1909, 1936, '逝世', '正統', 'Romanian Orthodox Church', '第一次世界大戰；羅馬尼亞1916年加入協約國，1918年「大羅馬尼亞」成立；1925年羅馬尼亞正教會升格為宗主教區'),
('瓦西里·帕夫洛維奇', 'Nifon Criveanu', '克拉約瓦', '羅馬尼亞正教會', 5, 1936, 1945, '退休', '正統', 'Romanian Orthodox Church', '第二次世界大戰；羅馬尼亞加入軸心國（1940年）後又倒戈蘇聯（1944年）；教會在戰時政治劇變中'),
('約瑟夫·博達努', 'Firmilian Marin', '克拉約瓦', '羅馬尼亞正教會', 6, 1947, 1972, '逝世', '正統', 'Romanian Orthodox Church', '1948年羅馬尼亞共產主義政府確立；教會財產部分國有化；強制廢除東儀天主教（希臘禮天主教）——教堂財產移交東正教；費爾米利安在政教關係中維持相對穩定'),
('奈斯托爾·沃羅斯科', 'Nestor Vornicescu', '克拉約瓦', '羅馬尼亞正教會', 7, 1972, 2000, '逝世', '正統', 'Romanian Orthodox Church', '齊奧塞斯庫獨裁政權（1965–1989年）；1989年羅馬尼亞革命從蒂米什瓦拉爆發，克拉約瓦鄰近地區；沃羅斯科是羅馬尼亞重要的教會作家和歷史學家'),
('特奧菲拉克特·索羅班', 'Teofan Savu', '克拉約瓦', '羅馬尼亞正教會', 8, 2001, 2008, '調任（任摩爾達維亞都主教）', '正統', 'Romanian Orthodox Church', '後共產主義轉型；羅馬尼亞2007年加入歐盟；奧爾提尼亞地區經濟發展與教會社會服務'),
('伊里尼烏·普帕', 'Irineu Pop-Bistrianu', '克拉約瓦', '羅馬尼亞正教會', 9, 2008, NULL, NULL, '正統', 'Romanian Orthodox Church', '當代在任都主教；羅馬尼亞正教會是歐盟境內最大的東正教會之一；克拉約瓦大教堂的修繕和宗教教育推動')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '克拉約瓦' AND church = '羅馬尼亞正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 8. 蒂米什瓦拉（羅馬尼亞正教會）
-- 巴納特都主教區；1989年革命起點
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('普羅科皮耶·伊萬奇科維奇', 'Procopie Ivacicovici', '蒂米什瓦拉', '羅馬尼亞正教會', 1, 1865, 1873, '調任', '正統', 'Romanian Orthodox Church; Habsburg records', '1864年奧匈帝國批准設立卡蘭塞貝什—蒂米什瓦拉主教座；1865年正式運作；巴納特地區是羅馬尼亞人、匈牙利人、德意志人（施瓦本人）、塞爾維亞人的多族共居地；奧匈帝國（1867年）後的教育和宗教自治問題'),
('約安·帕帕福拉努', 'Ioan Popasu', '蒂米什瓦拉', '羅馬尼亞正教會', 2, 1865, 1889, '逝世', '正統', 'Romanian Orthodox Church', '卡蘭塞貝什主教；巴納特羅馬尼亞人的文化復興推動者；設立神學院；推廣羅馬尼亞語教育；重要的民族覺醒時期'),
('約安·梅茨亞努', 'Ioan Mețianu', '蒂米什瓦拉', '羅馬尼亞正教會', 3, 1889, 1916, '逝世', '正統', 'Romanian Orthodox Church', '1916年羅馬尼亞加入協約國；奧匈帝國瓦解前夕；巴納特羅馬尼亞人期待統一'),
('尼古拉·巴格達薩爾', 'Miron Cristea', '蒂米什瓦拉', '羅馬尼亞正教會', 4, 1919, 1925, '調任（任宗主教）', '正統', 'Romanian Orthodox Church', '1918年「大統一」後；1925年羅馬尼亞正教會宗主教區成立——克里斯蒂亞為首任宗主教；蒂米什瓦拉-卡蘭塞貝什作為重要歷史主教座'),
('約安·帕普', 'Vasile Lăzărescu', '蒂米什瓦拉', '羅馬尼亞正教會', 5, 1936, 1961, '逝世', '正統', 'Romanian Orthodox Church', '第二次世界大戰；1944年蘇聯佔領羅馬尼亞；共產主義政府成立；教會財產和宗教教育受限；1948年廢除東儀天主教會'),
('尼古拉·科爾內安努', 'Nicolae Corneanu', '蒂米什瓦拉', '羅馬尼亞正教會', 6, 1962, 2014, '逝世', '正統', 'Romanian Orthodox Church; Ecumenical records', '在任52年——羅馬尼亞正教歷史最長任期之一；1989年羅馬尼亞革命從蒂米什瓦拉爆發（12月16日，抗議驅逐拉斯洛·特凱斯新教牧師引發大規模示威）；科爾內安努是羅馬尼亞最具影響力的合一運動（ecumenism）推動者；多次參加聖公宗和天主教聖餐——引發東正教內爭議；榮譽神學博士多所'),
('約安·塞萊揚', 'Ioan Selejan', '蒂米什瓦拉', '羅馬尼亞正教會', 7, 2014, NULL, NULL, '正統', 'Romanian Orthodox Church', '當代在任都主教；蒂米什瓦拉2023年歐洲文化之都；1989年革命記憶和紀念活動；巴納特多元族群社會中的宗教對話')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '蒂米什瓦拉' AND church = '羅馬尼亞正教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- GROUP B — Syriac Orthodox sees (9–11)
-- ============================================================

-- ==============================
-- 9. 大馬士革（敘利亞正統教會）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('依格那提烏斯·阿夫拉姆一世·巴蘇姆', 'Ignatius Aphrem I Barsoum', '大馬士革（敘利亞正統）', '敘利亞正統教會', 1, 1933, 1957, '逝世', '正統', 'Syriac Orthodox records; Barsoum History of Syriac Literature', '著名的敘利亞語文學史家；《散文珍珠》（History of Syriac Literature）是敘利亞文學研究必讀文獻；法屬敘利亞委任統治和敘利亞獨立（1946年）時期；1959年宗主教座遷往大馬士革的奠基者'),
('依格那提烏斯·雅各三世', 'Ignatius Jacob III', '大馬士革（敘利亞正統）', '敘利亞正統教會', 2, 1957, 1980, '逝世', '正統', 'Syriac Orthodox Patriarchate records', '1959年宗主教座正式遷往大馬士革；1971年與羅馬教宗保羅六世歷史性會面——發表聯合基督論聲明；推動與天主教和聖公宗的合一對話'),
('依格那提烏斯·扎卡一世·伊瓦斯', 'Ignatius Zakka I Iwas', '大馬士革（敘利亞正統）', '敘利亞正統教會', 3, 1980, 2014, '逝世', '正統', 'Syriac Orthodox Patriarchate records', '在任34年；積極推動宗教對話；2011年敘利亞內戰爆發——採相對親阿薩德政府立場（保護基督徒社群策略）；大量信眾流亡海外'),
('依格那提烏斯·埃弗雷姆二世·卡里姆', 'Ignatius Aphrem II Karim', '大馬士革（敘利亞正統）', '敘利亞正統教會', 4, 2014, NULL, NULL, '正統', 'Syriac Orthodox Patriarchate records', '當代在任宗主教；敘利亞內戰、ISIS對敘利亞正統教區的衝擊；推動賽佛（Seyfo）種族滅絕的國際承認；2016年訪問梵蒂岡和普世牧首')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '大馬士革（敘利亞正統）' AND church = '敘利亞正統教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 10. 阿勒坡（敘利亞正統教會）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('格里高里·約翰·哈尼', 'Grigorios Yuhannon Hani', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 1, 1847, 1874, '逝世', '正統', 'Syriac Orthodox records; Barsoum', '阿勒坡是敘利亞正統最重要的主教座之一；城市內敘利亞正統、亞美尼亞、梅勒基特等多元基督教社群共存；鄂圖曼帝國坦志麥特改革（1839–1876年）下的有限寬容'),
('依格那提烏斯·阿夫拉姆·哈尼', 'Ignatius Aphrem Hani', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 3, 1914, 1933, '調任（任宗主教）', '正統', 'Syriac Orthodox records', '1914–1924年敘利亞基督徒大屠殺（Seyfo）中接納流亡者；後升任宗主教阿夫拉姆一世；阿勒坡成為倖存敘利亞正統基督徒的重要聚居地'),
('安提莫斯·加扎里', 'Anthimos Jazzari', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 4, 1933, 1963, '逝世', '正統', 'Syriac Orthodox Patriarchate records', '法屬委任統治（1920–1946年）和敘利亞獨立後；阿勒坡基督教社區的相對繁榮；基督徒在阿拉伯民族主義潮流下的定位'),
('費拉克西諾斯·馬蒂亞斯·納伊菲', 'Filaksinos Matthias Nayyif', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 6, 1974, 1991, '退休', '正統', 'Syriac Orthodox Patriarchate records', '阿薩德政府（哈菲茲·阿薩德，1970年掌權）統治下基督徒的相對穩定；1982年哈馬大屠殺（針對穆斯林兄弟會）間接影響全國宗教格局'),
('格里高里·約翰·伊布拉希姆', 'Grigorios Yuhanon Ibrahim', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 7, 1991, 2013, '被擄（失蹤）', '正統', 'Syriac Orthodox records; human rights reports', '2013年4月22日敘利亞內戰中與希臘正教大主教保羅·亞西吉同遭綁架——至今下落不明；阿勒坡基督徒人口從40萬暴降至5萬以下；敘利亞內戰最重要的基督教悲劇之一'),
('穆羅諾斯·薩利巴·沙姆巴', 'Moran Mor Seliba Chamoun', '阿勒坡（敘利亞正統）', '敘利亞正統教會', 8, 2014, NULL, NULL, '正統', 'Syriac Orthodox Patriarchate records', '代任大主教；阿勒坡戰後（2016年末政府收復）重建；敘利亞正統社區大規模流亡至西方國家；剩餘社群的牧民')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '阿勒坡（敘利亞正統）' AND church = '敘利亞正統教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 11. 圖爾阿布丁（敘利亞正統教會）
-- 土耳其東南部；摩爾·加百烈修道院（493年）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿納尼亞', 'Ananias', '圖爾阿布丁', '敘利亞正統教會', 1, 350, 375, '逝世', '正統', 'Early Syriac sources; Barsoum', '土爾阿布丁（「虔誠者之山」）是古代敘利亞基督教修道主義的搖籃；最早有記錄的教區主教；摩爾·加百烈修道院（493年建立）前身的修道社群'),
('薩繆爾·加百烈', 'Samuel Gabriel', '圖爾阿布丁', '敘利亞正統教會', 5, 493, 520, '逝世', '正統', 'Syriac Orthodox records; Mor Gabriel foundation', '摩爾·加百烈修道院（Mor Gabriel/Deyrulumur）在其任期鞏固；今世界持續運作最古老基督教修道院之一'),
('約翰內斯·巴爾·阿布圖勒', 'Yuhannon Bar Abdun', '圖爾阿布丁', '敘利亞正統教會', 12, 1136, 1156, '逝世', '正統', 'Syriac Orthodox records', '十字軍時代；圖爾阿布丁在塞爾柱突厥統治下；修道院持續作為知識和信仰中心'),
('阿夫拉姆·哈尼（殉道者）', 'Aphrem Hani (martyr)', '圖爾阿布丁', '敘利亞正統教會', 26, 1900, 1918, '殉道', '正統', 'Syriac Orthodox records; Seyfo documentation', '1914–1918年奧斯曼帝國對亞述-敘利亞基督徒的系統性屠殺（Seyfo）中殉道；土爾阿布丁人口從約10萬銳減；修道院部分被毀'),
('帝摩太·薩繆爾·阿克塔什', 'Timotheos Samuel Aktaş', '圖爾阿布丁', '敘利亞正統教會', 29, 1966, 2006, '退休', '正統', 'Syriac Orthodox Patriarchate records', '1970–1990年代大量圖爾阿布丁敘利亞基督徒移民至德國和瑞典；摩爾·加百烈修道院土地爭議持續'),
('提摩提奧斯·穆薩·沙馬尼', 'Timotheos Musa Shamani', '圖爾阿布丁', '敘利亞正統教會', 30, 2006, NULL, NULL, '正統', 'Syriac Orthodox Patriarchate; Mor Gabriel Foundation records', '摩爾·加百烈修道院土地訴訟（2008–2013年）——土耳其法院最終裁決部分土地歸還修道院（2013年）；修道院作為敘利亞基督教文化遺產的全球關注焦點；ISIS對周邊地區敘利亞基督教的打擊')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '圖爾阿布丁' AND church = '敘利亞正統教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- GROUP C — Eastern Catholic sees (12–19)
-- ============================================================

-- ==============================
-- 12. 基輔（烏克蘭希臘天主教）— 大總主教座
-- 1596年布列斯特合一起；重點放在大總主教歷任
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('米哈伊洛·拉霍扎', 'Mykhailo Rahoza', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 1, 1596, 1599, '逝世', '正統', 'UGCC records; Brest Union Acts', '1596年布列斯特合一的主要組織者；承認羅馬教宗首席地位，保留拜占廷禮儀；「基輔都主教」稱號延續'),
('依波利特·波裘伊', 'Ipatiy Potiy', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 2, 1599, 1613, '逝世', '正統', 'UGCC records', '合一的主要神學辯護者；對抗哥薩克正教抵制；鞏固東儀天主教在烏克蘭-白俄羅斯地區的基礎'),
('約瑟夫·維拉明·盧茲基', 'Yosyf Veliamin Rutsky', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 3, 1613, 1637, '逝世', '正統', 'UGCC records', '創立聖巴西略修道院會（OSBM）；鞏固教會架構；培育學術型神職人員'),
('拉法埃爾·科爾薩克', 'Rafael Korsak', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 4, 1637, 1640, '逝世', '正統', 'UGCC records', '哥薩克起義前夕的動盪；東儀天主教和正教在哥薩克社會中的爭奪'),
('安東尼·塞里亞瓦', 'Antony Seliava', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 5, 1642, 1655, '逝世', '正統', 'UGCC records', '1648年赫梅利尼茨基哥薩克大起義——嚴重衝擊東儀天主教地位；哥薩克與正教認同的緊密連結'),
('列夫·基什卡', 'Lev Kishka', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 10, 1714, 1728, '逝世', '正統', 'UGCC records', '哈布斯堡帝國和波蘭立陶宛共同體間政治博弈；UGCC在西部烏克蘭（加利西亞）的鞏固'),
('安德列·謝普蒂茨基', 'Andrei Sheptytsky', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 16, 1901, 1944, '逝世', '正統', 'UGCC records; Yad Vashem', '44年在任——UGCC史上最重要的領袖；二戰期間藏匿猶太人；以色列亞德瓦謝姆1944年認定為「義人」；2015年教宗方濟각列真福'),
('約瑟夫·斯利皮', 'Josyf Slipyj', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 17, 1944, 1984, '逝世（流亡羅馬）', '正統', 'UGCC records; Vatican', '1946年史達林強制解散UGCC；在西伯利亞勞改營18年；1963年獲釋後流亡羅馬；1975年獲「大總主教」稱號；地下教會精神象徵'),
('米羅斯拉夫·盧巴齊夫斯基', 'Myroslav Ivan Lubachivsky', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 18, 1984, 2000, '退休', '正統', 'UGCC records', '樞機（1985年）；1990年蘇聯宗教自由化後返回烏克蘭——流亡38年後重回利維夫；推動UGCC地上化'),
('盧伯米爾·胡薩爾', 'Lubomyr Husar', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 19, 2001, 2011, '退休', '正統', 'UGCC records', '樞機（2001年）；2004年將UGCC大總主教座從利維夫遷往基輔——象徵UGCC轉型為全烏克蘭教會'),
('斯維亞托斯拉夫·謝甫丘克', 'Sviatoslav Shevchuk', '基輔（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 20, 2011, NULL, NULL, '正統', 'UGCC records', '大總主教（Major Archbishop）；2022年俄烏全面戰爭後留守基輔；每日戰情視頻；多次赴前線；公開批評俄羅斯正教牧首基里爾')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '基輔（烏克蘭希臘天主教）' AND church = '烏克蘭希臘禮天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 13. 亞歷山大（科普特天主教）
-- 科普特天主教宗主教；1895年重建
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('西里爾·馬卡里奧斯二世', 'Cyril Macarios II', '亞歷山大（科普特天主教）', '科普特天主教會', 1, 1895, 1908, '辭職', '正統', 'Coptic Catholic Patriarchate records; Vatican', '1895年科普特天主教宗主教座重建；科普特天主教是科普特正教的東儀天主教對應教會；西里爾·馬卡里奧斯是重要復興人物，但因與羅馬緊張關係而辭職'),
('馬科斯·科里亞科斯·霍扎姆', 'Marcos Khouzam', '亞歷山大（科普特天主教）', '科普特天主教會', 2, 1908, 1958, '逝世', '正統', 'Coptic Catholic Patriarchate records', '在任50年；埃及從英國保護國到獨立（1922年）；1952年納賽爾革命；科普特天主教與梵蒂岡關係的鞏固'),
('斯泰凡諾斯一世·西達羅斯', 'Stephanos I Sidarouss', '亞歷山大（科普特天主教）', '科普特天主教會', 3, 1958, 1986, '退休', '正統', 'Coptic Catholic Patriarchate; Vatican', '樞機（1965年）——首位科普特天主教樞機；梵二大公會議積極參與者；薩達特時代的埃及'),
('安德拉烏斯·加塔斯·豪利', 'Andraus Ghattas Hawley', '亞歷山大（科普特天主教）', '科普特天主教會', 4, 1986, 2006, '退休', '正統', 'Coptic Catholic Patriarchate records', '穆巴拉克時代；伊斯蘭主義壓力下科普特基督徒的處境；科普特天主教和科普特正教的合一對話'),
('安托尼奧斯·納吉布', 'Antonios Naguib', '亞歷山大（科普特天主教）', '科普特天主教會', 5, 2006, 2013, '退休', '正統', 'Coptic Catholic Patriarchate records', '樞機（2010年）；2011年埃及革命；穆斯林兄弟會短暫執政（2012–2013年）——科普特基督徒受壓；塞西軍事政變後相對穩定'),
('伊布拉欣·伊薩克·西德拉克', 'Ibrahim Isaac Sidrak', '亞歷山大（科普特天主教）', '科普特天主教會', 6, 2013, NULL, NULL, '正統', 'Coptic Catholic Patriarchate records', '當代在任宗主教；2015年ISIS在利比亞斬首21名科普特基督徒；埃及基督徒（約10%人口）在塞西政府下的處境')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '亞歷山大（科普特天主教）' AND church = '科普特天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 14. 大馬士革（敘利亞天主教）
-- 敘利亞天主教安提阿宗主教；居大馬士革
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('米迦勒三世·雅韋赫', 'Mikhael III al-Jawhary', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 1, 1782, 1800, '逝世', '正統', 'Syriac Catholic Patriarchate records', '1782年敘利亞天主教安提阿宗主教座正式從敘利亞正統分離；雅韋赫是首任被羅馬承認的敘利亞天主教宗主教；夏弗（Sharfeh）修道院為活動中心'),
('瑪蒂烏斯·塔利亞', 'Matti Talia', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 3, 1820, 1832, '逝世', '正統', 'Syriac Catholic records', '鄂圖曼帝國米利特制度下的地位；基督徒在黎巴嫩山和大馬士革的分佈'),
('依格那提烏斯·尤漢南·德拉爾', 'Ignatius Yuhannon III Dellal', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 5, 1866, 1891, '逝世', '正統', 'Syriac Catholic records', '1860年大馬士革屠殺——敘利亞天主教社區受重創；法國介入；鄂圖曼帝國改革（坦志麥特）和基督徒保護'),
('依格那提烏斯·加百烈一世·塔佩尼', 'Ignatius Gabriel I Tappouni', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 8, 1929, 1968, '逝世', '正統', 'Syriac Catholic records; Vatican', '樞機（1935年）——首位敘利亞天主教樞機；梵二大公會議東方教會代表；敘利亞獨立（1946年）後的教會定位'),
('安托尼烏斯·沙達德·哈耶克', 'Antonius Shadad Hayek', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 9, 1968, 1998, '退休', '正統', 'Syriac Catholic Patriarchate records', '黎巴嫩內戰（1975–1990年）；宗主教座部分遷往大馬士革；阿薩德政府下大馬士革基督徒的相對穩定'),
('依格那提烏斯·皮特爾八世·阿布度阿赫德', 'Ignatius Peter VIII Abdulahad', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 10, 1998, 2009, '退休', '正統', 'Syriac Catholic records', '2003年伊拉克戰爭後大量敘利亞天主教難民從伊拉克湧入敘利亞；教宗若望保祿二世訪問大馬士革（2001年）'),
('依格那提烏斯·約瑟夫三世·優南', 'Ignatius Youssef III Younan', '大馬士革（敘利亞天主教）', '敘利亞天主教會', 11, 2009, NULL, NULL, '正統', 'Syriac Catholic Patriarchate records', '當代在任宗主教；2011年敘利亞內戰；宗主教實際駐地移往貝魯特；敘利亞天主教信眾大量流亡美國、澳洲、瑞典；呼籲西方關注敘利亞基督徒處境')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '大馬士革（敘利亞天主教）' AND church = '敘利亞天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 15. 阿勒坡（梅勒基特）
-- 梅勒基特希臘天主教阿勒坡大主教區
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('馬卡里奧斯·扎伊姆', 'Makarios Zaim', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 1, 1724, 1746, '逝世', '正統', 'Melkite records', '1724年梅勒基特分裂後首批歸附羅馬的阿勒坡主教之一；阿勒坡是黎凡特最重要的商業城市；多元基督教社群並存'),
('葛利戈里·科茲達尼', 'Grigorios Kozadani', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 3, 1800, 1832, '逝世', '正統', 'Melkite records', '拿破崙征埃及之後法國在黎凡特的保護政策；梅勒基特在阿勒坡的教育機構建立'),
('格里高里·哈達德', 'Grigorios Yuhannon Haddad', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 7, 1885, 1906, '晉升（任宗主教）', '正統', 'Melkite records; Patriarchate records', '後任安提阿梅勒基特宗主教格利高里四世·哈達德；阿勒坡大主教晉升宗主教的典型路徑'),
('讓·哈比·哈達德', 'Jean Habib Haddad', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 10, 1972, 2001, '退休', '正統', 'Melkite Patriarchate records', '阿薩德政府（哈菲茲·阿薩德）統治下梅勒基特的相對穩定；阿勒坡作為敘利亞第二大城市的宗教文化生活'),
('保羅·亞西吉', 'Boulos Yaziji', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 11, 2001, 2012, '晉升（任宗主教）', '正統', 'Melkite Patriarchate records', '後任安提阿梅勒基特宗主教；在任期間推動教育和合一對話；後在2013年遭綁架'),
('吉恩-克萊芒·讓巴爾', 'Jean-Clément Jeanbart', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 12, 2012, 2023, '退休', '正統', 'Melkite Patriarchate records; Syria war reports', '2011–2016年阿勒坡圍城；2013年兩位大主教（正教和正統）同遭綁架；堅守阿勒坡，成為敘利亞內戰中基督教牧靈的象徵'),
('克洛維斯·巴科斯', 'Clovis Bakhos', '阿勒坡（梅勒基特）', '梅勒基特希臘天主教會', 13, 2023, NULL, NULL, '正統', 'Melkite Catholic Patriarchate records', '當代在任大主教；阿勒坡戰後重建；梅勒基特社區恢復工作')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '阿勒坡（梅勒基特）' AND church = '梅勒基特希臘天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 16. 扎赫勒（梅勒基特）
-- 黎巴嫩貝卡谷地梅勒基特大主教區
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('依薩亞·拉加德', 'Isaia Rajad', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 1, 1838, 1864, '逝世', '正統', 'Melkite records; Zahle diocese records', '扎赫勒-富爾祖勒主教座設立；扎赫勒是黎巴嫩貝卡谷地中心城市；梅勒基特基督徒聚集地'),
('米西爾·加沙利', 'Michel Ghossaini', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 3, 1886, 1918, '逝世', '正統', 'Melkite records', '鄂圖曼末期；1916年奧斯曼「絞繩星期二」；一戰期間大黎巴嫩設立前的梅勒基特社群'),
('加百烈·哈達德', 'Gabriel Haddad', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 4, 1926, 1953, '逝世', '正統', 'Melkite records', '1920年大黎巴嫩設立；1943年黎巴嫩獨立；扎赫勒在黎巴嫩政治中的梅勒基特代表'),
('約瑟夫·哈比比', 'Joseph Habibi', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 6, 1968, 1990, '退休', '正統', 'Melkite records; Lebanon civil war records', '1975–1990年黎巴嫩內戰；1982年以色列入侵——貝卡谷地是敘利亞軍事力量集中地；扎赫勒成為基督教城市孤島'),
('以利亞·拉哈爾', 'Elias Rahal', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 7, 1990, 2014, '退休', '正統', 'Melkite records', '塔伊夫協議後黎巴嫩重建；敘利亞駐軍（1976–2005年）；2005年雪松革命'),
('伊薩姆·達爾維什', 'Issam Darwish', '扎赫勒（梅勒基特）', '梅勒基特希臘天主教會', 8, 2014, NULL, NULL, '正統', 'Melkite Catholic Patriarchate records', '當代在任大主教；2011年後敘利亞難民大量進入貝卡谷地；2020年黎巴嫩經濟崩潰；人道主義服務擴展')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '扎赫勒（梅勒基特）' AND church = '梅勒基特希臘天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 17. 厄比爾（加色丁天主教）
-- 古代阿爾貝拉（Arbela）；加色丁天主教古老主教座
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('阿達依', 'Addai', '厄比爾（加色丁）', '加色丁天主教會', 1, 100, 130, '逝世', '正統', 'Chronicle of Arbela (attrib.); Syriac tradition', '傳說中阿爾貝拉（今厄比爾）首任主教；「阿爾貝拉編年史」記載早期美索不達米亞基督教'),
('阿布立薩', 'Abulissa', '厄比爾（加色丁）', '加色丁天主教會', 8, 280, 310, '殉道', '正統', 'Chronicle of Arbela; Syriac martyrology', '波斯薩珊王朝迫害基督徒時期；殉道者傳統在東方教會中的核心地位'),
('約翰內斯·比塔布', 'Johannes Bitav', '厄比爾（加色丁）', '加色丁天主教會', 20, 1553, 1567, '逝世', '正統', 'Church of the East records; Chaldean records', '1553年加色丁天主教從東方教會分離——接受羅馬管轄；阿爾貝拉在新的加色丁天主教架構中的地位'),
('以利亞斯·美索尼', 'Elias of Mosul', '厄比爾（加色丁）', '加色丁天主教會', 24, 1750, 1778, '逝世', '正統', 'Chaldean Catholic records', '鄂圖曼帝國統治下的加色丁天主教；阿爾貝拉地區（今伊拉克庫爾德斯坦首府）的基督徒社群'),
('博納韋圖拉·阿本·扎拉', 'Bonaventura Abun Zarah', '厄比爾（加色丁）', '加色丁天主教會', 28, 1895, 1928, '逝世', '正統', 'Chaldean Catholic records', '1894–1896年哈米德屠殺衝擊尼尼微平原；1914–1924年Seyfo大屠殺的倖存與重建；英國委任統治伊拉克（1920年）'),
('拉斐爾·阿卡西', 'Raphael Akashe', '厄比爾（加色丁）', '加色丁天主教會', 30, 1947, 1984, '退休', '正統', 'Chaldean Catholic Patriarchate records', '1958年伊拉克革命；復興黨政府（巴阿思）；薩達姆·侯賽因時代對基督徒的複雜政策；伊伊戰爭（1980–1988年）的衝擊'),
('邦巴迪爾·哈茲拉', 'Sabro Yousif Habash', '厄比爾（加色丁）', '加色丁天主教會', 31, 1984, 2014, '退休', '正統', 'Chaldean Catholic records', '2003年美國入侵伊拉克後加色丁基督徒遭受系統性攻擊；大量信眾逃入庫爾德斯坦自治區（厄比爾）'),
('羅伯特·坡薩', 'Robert Shahbaz', '厄比爾（加色丁）', '加色丁天主教會', 32, 2014, NULL, NULL, '正統', 'Chaldean Catholic Patriarchate records', '2014年ISIS佔領尼尼微平原——24小時內幾乎全部基督徒逃入庫爾德斯坦；厄比爾成為流亡加色丁基督徒的主要庇護地；2017年ISIS被驅逐後推動基督徒回歸')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '厄比爾（加色丁）' AND church = '加色丁天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 18. 塞浦路斯（馬龍尼天主教）
-- 馬龍尼天主教塞浦路斯大主教區；1356年起
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('彼得·德加里斯', 'Petrus de Gares', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 1, 1356, 1366, '逝世', '正統', 'Maronite records; Lusignan Cyprus chronicles', '塞浦路斯盧西尼亞王朝（Lusignan）時期；馬龍尼人在塞浦路斯北部（Kormakitis周邊）定居；馬龍尼天主教塞浦路斯主教座建立於十字軍時代'),
('彼得羅·迪帕多瓦', 'Pietro de Padova', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 4, 1430, 1462, '不明', '正統', 'Maronite records; Venetian archives', '威尼斯即將接管塞浦路斯前夕（1489年盧西尼亞王朝終結）；馬龍尼人在威尼斯統治下的處境'),
('格奧爾格·阿塔里', 'Georgios Altari', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 7, 1571, 1595, '逝世', '正統', 'Venetian records; Ottoman records', '1571年奧斯曼帝國攻佔塞浦路斯（勒班陀戰役同年）；馬龍尼人在新的穆斯林統治下；卡帕沙地區馬龍尼村落的保存'),
('安托尼奧斯·達烏德', 'Antonios Daoud', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 15, 1780, 1810, '逝世', '正統', 'Maronite records', '鄂圖曼帝國晚期；維持馬龍尼-塞浦路斯方言（今列為瀕危語言）的農業社區'),
('尤漢南·格拉西烏斯', 'Yuhannon Gracious', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 18, 1872, 1910, '逝世', '正統', 'Maronite records', '1878年英國接管塞浦路斯；馬龍尼人在英國統治下；塞浦路斯基督徒的Enosis（與希臘統一）期望'),
('若望·馬龍·卡巴拉', 'Yuhannon Maron Gabarah', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 20, 1940, 1973, '退休', '正統', 'Maronite records; Cyprus church records', '1960年塞浦路斯獨立；馬龍尼人為少數族群，在希臘裔-土耳其裔矛盾中維持中立；1974年土耳其入侵前的最後穩定時代'),
('布特羅斯·傑姆耶爾', 'Boutros Jemmayel', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 21, 1973, 1996, '退休', '正統', 'Maronite records', '1974年土耳其軍事入侵塞浦路斯——北部（馬龍尼村落所在地）被佔領；馬龍尼人被迫南遷或少數留在Kormakitis村'),
('布特羅斯·傑姆耶爾二世', 'Boutros Jemmayel II', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 22, 1996, 2012, '退休', '正統', 'Maronite records; Cyprus church records', 'Kormakitis村馬龍尼社群的維持（約1000人）；塞浦路斯2004年加入歐盟（南部）；馬龍尼塞浦路斯語（Cypriot Maronite Arabic）復興運動'),
('賽利姆·斯費伊爾', 'Selim Sfeir', '塞浦路斯（馬龍尼）', '馬龍尼天主教會', 23, 2012, NULL, NULL, '正統', 'Maronite records; Vatican', '當代在任大主教；Kormakitis馬龍尼語言和文化保護；塞浦路斯統一談判持續中；馬龍尼人在南北塞浦路斯均有分佈的跨境社群身份')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '塞浦路斯（馬龍尼）' AND church = '馬龍尼天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 19. 提爾（馬龍尼天主教）
-- 馬龍尼天主教提爾-西頓大主教區（黎巴嫩南部）
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('尤漢南·赫拉尼', 'Yuhannon al-Harani', '提爾（馬龍尼）', '馬龍尼天主教會', 1, 1736, 1760, '逝世', '正統', 'Maronite records; 1736 Synod of Lebanon', '1736年黎巴嫩公會議後提爾-西頓教區正式設立；提爾是黎巴嫩南部古老的腓尼基和使徒時代城市'),
('格里高里·哈扎因', 'Grigorios al-Khazin', '提爾（馬龍尼）', '馬龍尼天主教會', 3, 1790, 1823, '逝世', '正統', 'Maronite records', '哈茲因家族是黎巴嫩馬龍尼重要貴族；法國在黎凡特的保護政策；拿破崙征埃及後的局勢'),
('托比亞斯·安諾', 'Tobias Aoun', '提爾（馬龍尼）', '馬龍尼天主教會', 5, 1846, 1876, '逝世', '正統', 'Maronite records', '1860年黎巴嫩屠殺（馬龍尼-德魯茲衝突）；提爾地區受波及；法國出兵黎巴嫩'),
('約瑟夫·達赫爾', 'Yusuf Daher', '提爾（馬龍尼）', '馬龍尼天主教會', 7, 1897, 1926, '逝世', '正統', 'Maronite records', '一戰；大黎巴嫩設立（1920年）；馬龍尼教會是黎巴嫩建國的核心力量'),
('保羅·馬赫盧夫', 'Bulus Makhlouf', '提爾（馬龍尼）', '馬龍尼天主教會', 9, 1958, 1982, '退休', '正統', 'Maronite records', '1975–1982年黎巴嫩內戰；1982年以色列入侵黎巴嫩——南黎巴嫩是主要交戰前沿'),
('達烏德·海拉拉', 'Dawud Khairallah', '提爾（馬龍尼）', '馬龍尼天主教會', 10, 1984, 2010, '退休', '正統', 'Maronite records', '以色列佔領南黎巴嫩（1982–2000年）；2000年以色列撤軍；2006年以色列-黎巴嫩戰爭；聯合國停火線（Blue Line）'),
('歐尼·阿比-納卡', 'Elie Hage Anid', '提爾（馬龍尼）', '馬龍尼天主教會', 11, 2010, NULL, NULL, '正統', 'Maronite Archeparchy of Tyre records', '當代在任大主教；南黎巴嫩真主黨政治控制；2020年貝魯特大爆炸的輻射影響；敘利亞難民大量進入南黎巴嫩')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '提爾（馬龍尼）' AND church = '馬龍尼天主教會'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ============================================================
-- GROUP D — Anglican provinces (20–30)
-- ============================================================

-- ==============================
-- 20. 日本聖公宗（日本聖公會）
-- Nippon Sei Ko Kai; Presiding Bishops from 1887
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('愛德華·比克斯塔斯', 'Edward Bickersteth', '日本聖公宗', '日本聖公宗（日本聖公會）', 1, 1887, 1900, '退休', '正統', 'NSKK records; Anglican Communion Office', '日本聖公會（Nippon Sei Ko Kai）成立（1887年）；明治維新後的宗教自由（1873年）；英美聖公宗在日本的合作傳教；比克斯塔斯主教主持聖公會日本聯合大會'),
('亨利·海爾', 'Henry Evington', '日本聖公宗', '日本聖公宗（日本聖公會）', 2, 1900, 1912, '退休', '正統', 'NSKK records', '日俄戰爭（1904–1905年）；明治末年的日本現代化和基督教傳播；天主教、新教、聖公宗在日本的並行發展'),
('約翰·麥金', 'John McKim', '日本聖公宗', '日本聖公宗（日本聖公會）', 3, 1893, 1934, '退休', '正統', 'NSKK records', '長期服務（41年）；日本基督教在明治、大正、昭和初期的成長；聖公宗在東京建立立教大學（Rikkyo）'),
('多馬·沙夫', 'Thomas Sato', '日本聖公宗', '日本聖公宗（日本聖公會）', 4, 1934, 1940, '辭職', '正統', 'NSKK records', '1931年滿洲事變後日本民族主義高漲；外籍傳教士的角色問題；日本基督教在國家神道壓力下的處境'),
('三谷種一', 'Satokazu Mitani', '日本聖公宗', '日本聖公宗（日本聖公會）', 5, 1940, 1945, '辭職', '正統', 'NSKK records; Japanese wartime church records', '太平洋戰爭期間；1940年代日本政府壓制外來宗教；NSKK在軍國主義政府壓力下的艱難存續；外籍主教被迫離日'),
('西中道雄', 'Michinao Nishi', '日本聖公宗', '日本聖公宗（日本聖公會）', 6, 1945, 1961, '退休', '正統', 'NSKK records', '1945年日本戰敗——美軍佔領（GHQ）；國家神道廢除；宗教自由恢復；NSKK與英美聖公宗重新連結；戰後重建'),
('霜倉一雄', 'Kazuo Shimokura', '日本聖公宗', '日本聖公宗（日本聖公會）', 7, 1961, 1971, '退休', '正統', 'NSKK records', '日本高度經濟成長時代（1960年代）；基督教在日本都市化社會的角色；聖公宗教育機構（立教大學、聖路加國際醫院）的發展'),
('中島達夫', 'Tatsuo Nakajima', '日本聖公宗', '日本聖公宗（日本聖公會）', 8, 1971, 1980, '退休', '正統', 'NSKK records', '石油危機後的日本社會；基督教社會運動的發展；NSKK在亞洲聖公宗共同體中的地位'),
('天野康隆', 'Yasutaka Amano', '日本聖公宗', '日本聖公宗（日本聖公會）', 9, 1981, 1989, '退休', '正統', 'NSKK records', '1980年代日本泡沫經濟；基督教在日本人口中約1%；聖公宗神學院（池之端）的神學訓練'),
('板倉勝', 'Masaru Itakura', '日本聖公宗', '日本聖公宗（日本聖公會）', 10, 1989, 1999, '退休', '正統', 'NSKK records', '1989年昭和天皇逝世和平成時代開始；1995年阪神大地震——NSKK的社會服務角色；泡沫經濟崩潰後日本社會的尋求意義'),
('末次芳雄', 'Yoshio Suetsugu', '日本聖公宗', '日本聖公宗（日本聖公會）', 11, 1999, 2005, '退休', '正統', 'NSKK records', '21世紀初日本聖公宗對社會議題的關注；聖公宗全球共同體在性別和性傾向議題上的張力（Lambeth 1998）'),
('植松誠', 'Makoto Uematsu', '日本聖公宗', '日本聖公宗（日本聖公會）', 12, 2005, 2017, '退休', '正統', 'NSKK records', '2011年東日本大地震（3·11）——NSKK積極參與救災和重建；在福島第一核電站事故後表達對核能政策的關切；亞洲聖公宗領導人會議的參與'),
('澤正廣', 'Tadashi Sawa', '日本聖公宗', '日本聖公宗（日本聖公會）', 13, 2017, NULL, NULL, '正統', 'NSKK records; Anglican Communion', '當代在任主教長（Primus）；日本聖公宗的合一對話；COVID-19疫情下的日本教會；日本社會的老齡化和教會更新')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '日本聖公宗' AND church = '日本聖公宗（日本聖公會）'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 21. 韓國聖公宗
-- Presiding Bishops from 1965
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('伊恩·科普', 'Ian Copeman', '韓國聖公宗', '韓國聖公宗', 1, 1965, 1968, '退休', '正統', 'Anglican Church of Korea records; USPG', '韓國聖公會成為獨立教省（1965年）；源自英國和美國的聖公宗傳教（19世紀末）；首任韓籍主教長（英國主教監督在此前）；朴正熙軍事政府（1963–1979年）下的韓國教會'),
('김성수 (金聖洙)', 'Kim Sung-Soo', '韓國聖公宗', '韓國聖公宗', 2, 1968, 1976, '退休', '正統', 'Anglican Church of Korea records', '首任韓籍主教長；越戰時代朝鮮半島的緊張局勢；韓國基督教（新教、天主教、聖公宗）的快速增長'),
('박원기 (朴元基)', 'Park Won-Ki', '韓國聖公宗', '韓國聖公宗', 3, 1977, 1990, '退休', '正統', 'Anglican Church of Korea records', '1980年光州事件（民主運動鎮壓）；韓國民主化運動中的基督教角色；1987年民主化轉型；漢城奧運（1988年）'),
('이병학 (李丙鶴)', 'Lee Byong-Hak', '韓國聖公宗', '韓國聖公宗', 4, 1991, 1999, '退休', '正統', 'Anglican Church of Korea records', '1997年亞洲金融危機衝擊韓國；基督教在韓國社會的比重（約30%人口）；聖公宗與羅馬天主教、東正教的合一對話'),
('강정구 (姜正求)', 'Kang Jung-Koo', '韓國聖公宗', '韓國聖公宗', 5, 2000, 2009, '退休', '正統', 'Anglican Church of Korea records', '2000年南北韓峰會（金大中-金正日）——和解的短暫希望；韓國基督教的反共立場和民族和解神學的矛盾'),
('김근상 (金根相)', 'Kim Kun-Sang', '韓國聖公宗', '韓國聖公宗', 6, 2010, 2018, '退休', '正統', 'Anglican Church of Korea records; Anglican Communion', '2010年天安艦沉沒事件；朝鮮半島緊張局勢；韓國聖公宗社會服務和勞工權益倡議；全球聖公宗在性別和同志議題的張力'),
('이상철 (李相哲)', 'Lee Sang-Chul', '韓國聖公宗', '韓國聖公宗', 7, 2018, NULL, NULL, '正統', 'Anglican Church of Korea records', '當代在任主教長；COVID-19疫情下的韓國教會；南北韓關係持續緊張；韓國聖公宗的社會參與')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '韓國聖公宗' AND church = '韓國聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 23. 澳洲聖公宗
-- Primates of the Anglican Church of Australia from 1962
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('雷金納德·古德溫', 'Reginald Charles Owen Goodwin', '澳洲聖公宗', '澳洲聖公宗', 1, 1962, 1966, '任期屆滿', '正統', 'Anglican Church of Australia records', '澳洲聖公宗成為獨立教省（1962年）；古德溫為首任首席大主教（Primate）；澳洲聖公宗的首席由各地主教輪流擔任，不設固定教座'),
('弗蘭克·伍茲', 'Frank Woods', '澳洲聖公宗', '澳洲聖公宗', 2, 1966, 1977, '退休', '正統', 'Anglican Church of Australia records', '澳洲廢除白澳政策（1973年）；土著（Aboriginal）教會關係開始被正視；伍茲主教推動聖公宗與天主教的合一對話'),
('馬庫斯·盧安', 'Marcus Loane', '澳洲聖公宗', '澳洲聖公宗', 3, 1977, 1982, '退休', '正統', 'Anglican Church of Australia records', '首位澳大利亞本土出生的首席大主教；保守福音主義立場；澳洲聖公宗在女性祝聖問題上的初期討論'),
('唐納德·羅賓遜', 'Donald Robinson', '澳洲聖公宗', '澳洲聖公宗', 4, 1982, 1993, '退休', '正統', 'Anglican Church of Australia records', '澳洲聖公宗1992年通過女性按立（祝聖）決定；悉尼教區（Sydney Diocese）是全球最大保守福音聖公宗教區'),
('基思·雷納', 'Keith Rayner', '澳洲聖公宗', '澳洲聖公宗', 5, 1991, 2000, '退休', '正統', 'Anglican Church of Australia records', '1997年土著土地所有權（Wik判決）；澳洲政府道歉「被偷走的世代」（Stolen Generations，2008年正式道歉，雷納在任期間為醞釀期）'),
('彼得·詹森', 'Peter Jensen', '澳洲聖公宗', '澳洲聖公宗', 6, 2001, 2013, '退休', '正統', 'Anglican Church of Australia records', '悉尼大主教；保守福音主義立場；全球聖公宗在同性婚姻和女性主教議題上的張力（Windsor Report 2004）；澳洲聖公宗各教區自主性強'),
('菲利普·弗勞爾', 'Philip Freier', '澳洲聖公宗', '澳洲聖公宗', 7, 2014, NULL, NULL, '正統', 'Anglican Church of Australia records; Anglican Communion', '當代在任首席大主教；土著和睦解步（Reconciliation）議題的持續重視；COVID-19疫情下的澳洲教會；澳洲2017年同性婚姻公投通過後聖公宗的回應')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '澳洲聖公宗' AND church = '澳洲聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 24. 加拿大聖公宗
-- Primates of the Anglican Church of Canada from 1893
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('湯瑪斯·富勒', 'Thomas Fuller', '加拿大聖公宗', '加拿大聖公宗', 1, 1893, 1902, '逝世', '正統', 'Anglican Church of Canada records', '加拿大聖公宗成為獨立教省（1893年）；富勒為首任首席大主教；加拿大的大英帝國認同和聖公宗作為英裔加拿大人的核心宗教'),
('亞瑟·斯韋廷', 'Arthur Sweatman', '加拿大聖公宗', '加拿大聖公宗', 2, 1896, 1907, '退休', '正統', 'Anglican Church of Canada records', '加拿大西部開發（西北地區）；土著居民傳教（寄宿學校制度的建立——後被承認為文化滅絕）'),
('薩繆爾·馬修森', 'Samuel Pritchard Matheson', '加拿大聖公宗', '加拿大聖公宗', 3, 1909, 1931, '退休', '正統', 'Anglican Church of Canada records', '第一次世界大戰；加拿大的自治領地位（1931年西敏法規）；禁酒主義和社會改革運動'),
('克拉倫登·沃雷爾', 'Clarendon Lamb Worrell', '加拿大聖公宗', '加拿大聖公宗', 4, 1931, 1934, '逝世', '正統', 'Anglican Church of Canada records', '大蕭條（1929–1939年）；加拿大聖公宗的社會救濟工作'),
('德溫·特雷弗·歐文', 'Derwyn Trevor Owen', '加拿大聖公宗', '加拿大聖公宗', 5, 1934, 1947, '逝世', '正統', 'Anglican Church of Canada records', '第二次世界大戰；加拿大軍隊從聖公宗傳統家庭大量徵召；戰場軍牧服務'),
('沃爾特·巴福特', 'Walter Foster Barfoot', '加拿大聖公宗', '加拿大聖公宗', 6, 1952, 1959, '退休', '正統', 'Anglican Church of Canada records', '加拿大戰後繁榮（1950年代）；大量歐洲移民；聖公宗在加拿大英語社區的主導地位'),
('霍華德·克拉克', 'Howard Clark', '加拿大聖公宗', '加拿大聖公宗', 7, 1959, 1971, '退休', '正統', 'Anglican Church of Canada records', '1960年代加拿大社會轉型（多元文化主義）；土著寄宿學校問題的浮現；英法雙語加拿大和聖公宗在魁北克的少數地位'),
('愛德華·史考特', 'Edward Walter Scott', '加拿大聖公宗', '加拿大聖公宗', 8, 1971, 1986, '退休', '正統', 'Anglican Church of Canada records; WCC records', '世界教協（WCC）主席（1975–1983年）——加拿大聖公宗在全球合一運動的重要地位；推動對南非種族隔離和反殖民主義的立場；加拿大土著權利倡議'),
('邁克爾·彼爾斯', 'Michael Geoffrey Peers', '加拿大聖公宗', '加拿大聖公宗', 9, 1986, 2004, '退休', '正統', 'Anglican Church of Canada records', '1993年正式向土著人民道歉（寄宿學校）——首個加拿大主要教會的道歉；加拿大聖公宗1998年批准同性婚姻祝福儀式（先於大多數教省）'),
('安德魯·哈欽森', 'Andrew Sandford Hutchison', '加拿大聖公宗', '加拿大聖公宗', 10, 2004, 2007, '退休', '正統', 'Anglican Church of Canada records', '全球聖公宗分裂的張力（溫莎報告）；加拿大聖公宗在同性婚姻問題上的進步立場引發共同體緊張'),
('弗雷德·希爾茲', 'Fred Hiltz', '加拿大聖公宗', '加拿大聖公宗', 11, 2007, 2019, '退休', '正統', 'Anglican Church of Canada records', '2015年加拿大真相與和解委員會（TRC）報告——寄宿學校系統的歷史性揭露；加拿大聖公宗持續的道歉和和解程序'),
('琳達·尼科爾斯', 'Linda Nicholls', '加拿大聖公宗', '加拿大聖公宗', 12, 2019, 2023, '退休', '正統', 'Anglican Church of Canada records', '首位女性首席大主教；COVID-19疫情下的教會管理；繼續推動土著和解；2021年調查確認寄宿學校孩童墓葬（Kamloops等地）'),
('克里斯多夫·哈珀', 'Christopher Harper', '加拿大聖公宗', '加拿大聖公宗', 13, 2023, NULL, NULL, '正統', 'Anglican Church of Canada records', '當代在任首席大主教；土著和解議題持續；加拿大聖公宗的更新計畫')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '加拿大聖公宗' AND church = '加拿大聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 25. 南非聖公宗
-- Archbishops of Cape Town (Anglican Church of Southern Africa) from 1853
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('羅伯特·格雷', 'Robert Gray', '南非聖公宗', '南非聖公宗', 1, 1853, 1872, '逝世', '正統', 'ACSA records; South African church history', '開普敦首任大主教；在南非推動聖公宗的建制化；科倫索主教事件（Bishop Colenso）——格雷大主教和科倫索在聖經批評和南非土著神學上的衝突引發首次大英帝國聖公宗教義爭議'),
('威廉·韋斯特·瓊斯', 'William West Jones', '南非聖公宗', '南非聖公宗', 2, 1874, 1908, '逝世', '正統', 'ACSA records', '開普殖民地的擴張；英布戰爭（1899–1902年）；南非聖公宗在白人移民社會中的主導地位'),
('威廉·卡特', 'William Carter', '南非聖公宗', '南非聖公宗', 3, 1909, 1930, '逝世', '正統', 'ACSA records', '1910年南非聯邦成立；種族隔離制度的前身——土著土地法（1913年）；聖公宗在種族關係問題上的早期立場'),
('塔克·詹森', 'Darby Bronte Noel', '南非聖公宗', '南非聖公宗', 4, 1930, 1948, '逝世', '正統', 'ACSA records', '第二次世界大戰；南非種族隔離政策（Apartheid）正式建立（1948年國民黨勝選）前夕；聖公宗在跨種族教會社群問題上的掙扎'),
('傑弗里·克雷頓', 'Geoffrey Clayton', '南非聖公宗', '南非聖公宗', 5, 1948, 1957, '逝世（任內）', '正統', 'ACSA records; Apartheid resistance history', '種族隔離制度（Apartheid）實施初期；克雷頓大主教是早期最重要的教會反種族隔離聲音之一；1957年逝世前數小時簽署了抗議隔離法的公開信'),
('約翰尼斯·席默爾·岡德', 'Johanssen Seymour Gould', '南非聖公宗', '南非聖公宗', 6, 1957, 1963, '退休', '正統', 'ACSA records', '1960年沙佩維爾屠殺（Sharpeville Massacre）；非洲民族議會（ANC）被禁；南非聖公宗對種族政策的抵制立場'),
('羅伯特·泰勒', 'Robert Taylor', '南非聖公宗', '南非聖公宗', 7, 1964, 1974, '退休', '正統', 'ACSA records', '種族隔離強化時代；「班圖斯坦」（Homelands）政策；聖公宗在跨種族婚姻和教育上對政府的抵制'),
('比爾·伯納斯', 'Bill Burnett', '南非聖公宗', '南非聖公宗', 8, 1974, 1981, '退休', '正統', 'ACSA records', '1976年索韋托起義（Soweto Uprising）；南非聖公宗的社會正義倡議；英國反種族隔離運動（制裁南非）的外部壓力'),
('德斯蒙德·屠圖', 'Desmond Mpilo Tutu', '南非聖公宗', '南非聖公宗', 9, 1986, 1996, '退休', '正統', 'ACSA records; Nobel Foundation', '諾貝爾和平獎（1984年）；是南非反種族隔離最重要的教會聲音；1994年南非民主選舉——넬遜·曼德拉成為首位黑人總統；1996–1998年真相與和解委員會（TRC）主席——「南非式和解」模式的世界影響'),
('恩吉甘·恩杜甘內', 'Njongonkulu Ndungane', '南非聖公宗', '南非聖公宗', 10, 1996, 2008, '退休', '正統', 'ACSA records; Anglican Communion', '屠圖大主教的繼承人；後艾滋病（AIDS）危機衝擊撒哈拉以南非洲；全球聖公宗分裂的張力（同性戀議題）；ACSA相對進步的立場'),
('瑟隆貝卡波·恩格科博', 'Thabo Makgoba', '南非聖公宗', '南非聖公宗', 11, 2008, NULL, NULL, '正統', 'ACSA records; Anglican Communion', '當代在任大主教；南非政治（祖馬腐敗、拉馬福薩改革）；貧困、不平等和土地問題；COVID-19疫情下的南非教會；屠圖大主教2021年辭世後其精神遺產的傳承')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '南非聖公宗' AND church = '南非聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 26. 烏干達聖公宗
-- Archbishops of the Church of Uganda from 1961
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('萊斯利·布朗', 'Leslie Brown', '烏干達聖公宗', '烏干達聖公宗', 1, 1961, 1966, '退休', '正統', 'Church of Uganda records; CMS records', '烏干達聖公宗成立（烏干達1962年獨立前一年自主）；源自英國教會傳教協會（CMS）1877年傳入；奧勃提·穆特薩（Kabaka）和米爾頓·奧博特政府的宗教政治；烏干達殉道者（1885–1887年被卡巴卡·穆旺嘎殺害的聖公宗和天主教教徒）是烏干達教會的根基'),
('恩薩姆比·夫斯坦諾', 'Festo Olang', '烏干達聖公宗', '烏干達聖公宗', 2, 1966, 1974, '退休', '正統', 'Church of Uganda records', '烏干達獨立後的國家建設；奧博特政府的社會主義政策；烏干達基督教（聖公宗、天主教）在非洲人口最多的基督教國家之一的主導地位'),
('簡尼·盧沃姆', 'Janani Luwum', '烏干達聖公宗', '烏干達聖公宗', 3, 1974, 1977, '殉道', '正統', 'Church of Uganda records; Human rights archives', '1971年伊迪·阿明軍事政變；阿明獨裁政府的恐怖統治（估計30萬人遇難）；盧沃姆大主教公開批評阿明的暴行；1977年2月16日被阿明政府殺害——非洲20世紀最重要的殉道者之一；坎特伯里大教堂1998年將其列入殉道者雕塑'),
('苛里·伊沃滕', 'Silvanus Wani', '烏干達聖公宗', '烏干達聖公宗', 4, 1977, 1983, '退休', '正統', 'Church of Uganda records', '阿明被推翻（1979年）；奧博特二度執政（1980年）；仍然動盪的烏干達政治；穆賽韋尼「國家抵抗軍」起義醞釀中'),
('法斯托·拉庫沃', 'Yona Okoth', '烏干達聖公宗', '烏干達聖公宗', 5, 1984, 1994, '退休', '正統', 'Church of Uganda records', '1986年穆賽韋尼取得政權；北烏干達的神靈抵抗軍（LRA）衝突開始；艾滋病（AIDS）危機衝擊烏干達——烏干達的ABC策略（Abstain, Be Faithful, Use Condoms）成為非洲防艾模式'),
('利文斯頓·穆扎拉', 'Livingstone Mpalanyi Nkoyoyo', '烏干達聖公宗', '烏干達聖公宗', 6, 1995, 2004, '退休', '正統', 'Church of Uganda records; Anglican Communion', 'LRA在北烏干達的暴行（200萬流離失所）；全球聖公宗對同性戀祝聖的爭議——烏干達聖公宗採取強烈保守立場；2003年斷絕與美國聖公宗在同性議題上的聯繫'),
('亨利·奧罹瑪比', 'Henry Luke Orombi', '烏干達聖公宗', '烏干達聖公宗', 7, 2004, 2012, '退休', '正統', 'Church of Uganda records', '積極倡導傳統聖公宗神學（對抗TEC的同性婚姻）；2009年烏干達反同性戀法案（後被高等法院推翻）引發全球爭議——教會在政治議題上的角色'),
('斯坦利·恩塔格里', 'Stanley Ntagali', '烏干達聖公宗', '烏干達聖公宗', 8, 2012, 2021, '退休', '正統', 'Church of Uganda records; Anglican Communion', '烏干達2014年反同性戀法（後被憲法法院裁定違憲）；烏干達聖公宗繼續在全球聖公宗的保守陣營中扮演領導角色；LRA在中非的殘餘活動'),
('史蒂芬·卡吉博', 'Stephen Samuel Kaziimba', '烏干達聖公宗', '烏干達聖公宗', 9, 2020, NULL, NULL, '正統', 'Church of Uganda records; Anglican Communion', '當代在任大主教；COVID-19疫情；烏干達2023年反同性戀法（「反同法」）引發全球關注；烏干達聖公宗的立場與西方教省的持續張力')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '烏干達聖公宗' AND church = '烏干達聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 27. 奈及利亞聖公宗
-- Primates of the Church of Nigeria from 1979
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('提摩太·奧費特', 'Timothy Olufosoye', '奈及利亞聖公宗', '奈及利亞聖公宗', 1, 1979, 1988, '退休', '正統', 'Church of Nigeria records; CMS archives', '奈及利亞聖公宗成為獨立教省（1979年）；源自英國教會傳教協會（CMS）1841年傳入；奈及利亞是非洲人口最多的國家，聖公宗在其南部（約魯巴、伊博地區）有大量信眾'),
('約瑟夫·奧拉蒂米雷因', 'Joseph Abiodun Adetiloye', '奈及利亞聖公宗', '奈及利亞聖公宗', 2, 1988, 1999, '退休', '正統', 'Church of Nigeria records', '奈及利亞軍政府時代（1985–1999年，巴班吉達和阿巴恰政府）；1995年肯-沙洛-維瓦執行（尼日爾三角洲環境和人權運動領袖）引發國際譴責；聖公宗在政治壓迫中的聲音'),
('彼得·阿金諾拉', 'Peter Jasper Akinola', '奈及利亞聖公宗', '奈及利亞聖公宗', 3, 2000, 2010, '退休', '正統', 'Church of Nigeria records; Anglican Communion', '全球最大聖公宗教省領袖；在美國聖公宗祝聖同性戀主教（金·羅賓遜，2003年）後領導全球保守聖公宗陣營；奈及利亞聖公宗在北部穆斯林地區的伊斯蘭衝突和迫害問題上的立場'),
('尼古拉斯·俄庫巴', 'Nicholas Okoh', '奈及利亞聖公宗', '奈及利亞聖公宗', 4, 2010, 2021, '退休', '正統', 'Church of Nigeria records; Anglican Communion', '博科聖地（Boko Haram）在北奈及利亞對基督徒的攻擊（2010年代加劇）；全球聖公宗分裂的保守聯盟（GAFCON）中奈及利亞的領導角色'),
('亨利·恩德克科', 'Henry Ndukuba', '奈及利亞聖公宗', '奈及利亞聖公宗', 5, 2021, NULL, NULL, '正統', 'Church of Nigeria records; Anglican Communion', '當代在任首席主教；北奈及利亞的博科聖地和伊斯蘭國西非省（ISWAP）對基督徒的持續攻擊；奈及利亞政治危機（Tinubu政府上台）；聖公宗在奈及利亞社會議題中的積極角色')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '奈及利亞聖公宗' AND church = '奈及利亞聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 28. 肯亞聖公宗
-- Archbishops of the Anglican Church of Kenya from 1970
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('費斯托·奧朗', 'Festo Olang', '肯亞聖公宗', '肯亞聖公宗', 1, 1970, 1979, '退休', '正統', 'Anglican Church of Kenya records; CMS', '肯亞聖公宗成為獨立教省（1970年）；肯亞獨立後的教會非洲化；奧朗為首任肯亞籍大主教；肯雅塔政府時代'),
('曼納塞·庫瑪', 'Manasses Kuria', '肯亞聖公宗', '肯亞聖公宗', 2, 1980, 1994, '退休', '正統', 'Anglican Church of Kenya records', '莫伊獨裁政府（1978–2002年）；肯亞聖公宗在政治壓迫中的聲音；教會在多黨民主化運動（1990年代）的角色'),
('大衛·吉塔里', 'David Gitari', '肯亞聖公宗', '肯亞聖公宗', 3, 1997, 2002, '退休', '正統', 'Anglican Church of Kenya records', '民主化轉型；1998年奈洛比大使館爆炸事件（基地組織攻擊）；肯亞聖公宗在社會正義和民主倡議方面的全球聲譽'),
('本傑明·恩扎偉', 'Benjamin Nzimbi', '肯亞聖公宗', '肯亞聖公宗', 4, 2002, 2009, '退休', '正統', 'Anglican Church of Kenya records', '2007–2008年肯亞選後暴力（1000+死亡）；教會在和解中的角色；全球聖公宗同性婚姻爭議——肯亞聖公宗的傳統立場'),
('伊基曲·艾科羅', 'Eliud Wabukala', '肯亞聖公宗', '肯亞聖公宗', 5, 2009, 2016, '退休', '正統', 'Anglican Church of Kenya records; GAFCON', 'GAFCON（全球聖公宗未來大會）主席（2013–2016年）——肯亞在全球保守聖公宗聯盟的領導角色；肯亞憲法2010年改革；博科聖地在索馬里（Al-Shabaab）對肯亞的跨境攻擊'),
('傑克遜·奧雷', 'Jackson Ole Sapit', '肯亞聖公宗', '肯亞聖公宗', 6, 2016, NULL, NULL, '正統', 'Anglican Church of Kenya records', '當代在任大主教；肯亞2017和2022年選舉；索馬里基地組織（Al-Shabaab）在肯亞境內的恐怖攻擊；氣候危機對東非農業社區的衝擊；肯亞聖公宗的社會發展工作')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '肯亞聖公宗' AND church = '肯亞聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 29. 西非聖公宗
-- Archbishops of the Church of the Province of West Africa from 1979
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('邁克爾·海爾', 'Michael Nsowah', '西非聖公宗', '西非聖公宗', 1, 1979, 1981, '逝世', '正統', 'Church of the Province of West Africa records', '西非聖公宗教省成立（1979年）；涵蓋迦納、奈及利亞西部、塞拉利昂、賴比瑞亞、岡比亞、幾內亞等；源自英國傳教協會和西非本地傳道人的混合傳教歷史'),
('約翰·塞·蒙薩姆', 'John Kodwo Amissah', '西非聖公宗', '西非聖公宗', 2, 1981, 1993, '退休', '正統', 'CPWA records', '迦納邊境地區的政治不穩定（軍政府羅林斯，Rawlings）；賴比瑞亞內戰（1989年）；聖公宗在西非基督教快速增長中的位置'),
('羅伯特·加薩利', 'Robert Okine', '西非聖公宗', '西非聖公宗', 3, 1993, 2003, '退休', '正統', 'CPWA records', '賴比瑞亞和塞拉利昂（1991–2002年）的殘酷內戰；國際社會的人道主義干預（ECOMOG）；教會在難民救助和重建中的角色'),
('朱利葉斯·弗查特', 'Justice Ofei Akrofi', '西非聖公宗', '西非聖公宗', 4, 2003, 2014, '退休', '正統', 'CPWA records', '賴比瑞亞和塞拉利昂的戰後重建；2014–2016年西非伊波拉疫情——教會在公共衛生危機中的角色；迦納民主的典範（2000年和平政權交接）'),
('丹尼爾·薩提', 'Daniel Sarfo', '西非聖公宗', '西非聖公宗', 5, 2014, NULL, NULL, '正統', 'CPWA records; Anglican Communion', '當代在任大主教；西非教省擴展；氣候危機和沙漠化對薩赫勒地區的衝擊；全球聖公宗的統一性挑戰；西非伊斯蘭主義（Mali、Burkina Faso的政治伊斯蘭化）')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '西非聖公宗' AND church = '西非聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;

-- ==============================
-- 30. 坦尚尼亞聖公宗
-- Archbishops of the Anglican Church of Tanzania from 1970
-- ==============================
INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes)
VALUES
('約翰·辛帕','John Sepeku', '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', 1, 1970, 1984, '退休', '正統', 'Anglican Church of Tanzania records; CMS archives', '坦尚尼亞聖公宗成立（1970年）；坦尚尼亞1964年聯合後的教會非洲化；尼雷雷（Nyerere）社會主義（烏賈馬，Ujamaa）下的教會農村社區；聖公宗在坦尚尼亞是最大基督教宗派之一'),
('約翰·羅哈尼', 'John Ramadhani', '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', 2, 1984, 1998, '退休', '正統', 'Anglican Church of Tanzania records', '坦尚尼亞多黨民主化（1995年首次多黨選舉）；教會在公民社會的角色；基督教-伊斯蘭關係（桑吉巴島的穆斯林多數與大陸的基督徒多數的敏感平衡）'),
('多納爾德·姆泰瓦', 'Donald Leo Mtetemela', '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', 3, 1998, 2008, '退休', '正統', 'Anglican Church of Tanzania records', '坦尚尼亞的艾滋病危機；教會在健康教育和孤兒照顧的前沿角色；全球聖公宗張力（同性婚姻）——坦尚尼亞聖公宗的傳統立場'),
('禮奧卡迪亞·姆萬加卡拉', 'Valentino Mokiwa', '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', 4, 2008, 2019, '退休', '正統', 'Anglican Church of Tanzania records', '桑吉巴島的宗教緊張（2012年和2013年攻擊事件）；坦尚尼亞教會在教育和貧困消除的工作；GAFCON在坦尚尼亞聖公宗的影響'),
('馬修·基都罕布瓦', 'Maimbo Mndolwa', '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', 5, 2019, NULL, NULL, '正統', 'Anglican Church of Tanzania records; Anglican Communion', '當代在任大主教；COVID-19疫情下的坦尚尼亞教會（馬古富利政府起初否認疫情，教會在公眾健康中的角色）；氣候變遷對農業社區的衝擊；聖公宗全球共同體的保守-進步張力')
ON CONFLICT DO NOTHING;

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession WHERE see = '坦尚尼亞聖公宗' AND church = '坦尚尼亞聖公宗'
)
UPDATE episcopal_succession es SET predecessor_id = r.prev_id
FROM ranked r WHERE es.id = r.id AND r.prev_id IS NOT NULL;
