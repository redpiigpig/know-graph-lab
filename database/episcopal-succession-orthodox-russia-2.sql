-- ============================================================
-- 東正教主教傳承——俄羅斯正教會都主教座
-- 聖彼得堡、基輔（莫斯科）、基輔（烏克蘭正教）、明斯克
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 聖彼得堡都主教（俄羅斯正教會）
-- 1703年彼得大帝建城；俄羅斯帝國精神首都
-- ==============================
('約布·彼得堡', 'Job of Saint Petersburg', '聖彼得堡', '俄羅斯正教會', 1, 1742, 1750, '退休', '聖主教會議', '正統', 'Moscow Patriarchate', '1742年聖彼得堡主教座正式設立；彼得大帝1703年建城後近40年才建立完整主教轄區；俄羅斯帝國西化與正教傳統的平衡'),
('敘爾維斯特·庫里亞布斯基', 'Sylvestr Kulyabka', '聖彼得堡', '俄羅斯正教會', 2, 1750, 1761, '退休', '女皇伊麗莎白', '正統', 'Moscow Patriarchate', '女皇伊麗莎白時代；芬蘭灣沿岸的教會擴張；聖彼得堡城市快速發展中的教會機構建設'),
('卡提林·基貝爾', 'Gavriil Kremenetsky', '聖彼得堡', '俄羅斯正教會', 5, 1762, 1770, '調任', '女皇凱薩琳二世', '正統', 'Moscow Patriarchate', '葉卡捷琳娜大帝世俗化政策下的教會；1764年修道院財產世俗化（凱薩琳教會改革）——大規模削減修道院土地'),
('格夫里耶爾·彼得羅夫', 'Gavriil Petrov', '聖彼得堡', '俄羅斯正教會', 8, 1770, 1799, '退休', '女皇凱薩琳二世', '正統', 'Moscow Patriarchate', '在任29年；法國大革命期間；凱薩琳大帝「開明君主」政策與正教保守傳統的長期共存；涅瓦修道院（Alexander Nevsky Lavra）的重要建設期'),
('安姆夫洛西·波多比耶多夫', 'Ambrosiy Podobedov', '聖彼得堡', '俄羅斯正教會', 9, 1799, 1818, '退休', '沙皇保羅一世/亞歷山大一世', '正統', 'Moscow Patriarchate', '拿破崙戰爭時代（1812年衛國戰爭）；聖彼得堡教會在帝國危機中的精神動員角色'),
('塞拉菲姆·格拉多夫斯基', 'Seraphim Glagolievsky', '聖彼得堡', '俄羅斯正教會', 11, 1821, 1843, '退休', '沙皇亞歷山大一世', '正統', 'Moscow Patriarchate', '十二月黨人起義（1825年）後教會的保守角色；聖彼得堡神學院的發展；俄羅斯聖經翻譯工作的推進'),
('格里戈里·波斯特尼科夫', 'Grigoriy Postnikov', '聖彼得堡', '俄羅斯正教會', 12, 1856, 1860, '調任', '沙皇亞歷山大二世', '正統', 'Moscow Patriarchate', '克里米亞戰爭（1853-1856）後改革時代；農奴解放（1861年）前夕的教會立場'),
('伊西多爾·尼科爾斯基', 'Isidor Nikolsky', '聖彼得堡', '俄羅斯正教會', 13, 1860, 1892, '逝世', '沙皇亞歷山大二世', '正統', 'Moscow Patriarchate', '在任32年——波別多諾斯采夫（Pobedonostsev）最高檢察長時代的保守教會；1881年亞歷山大二世遇刺；聖彼得堡知識分子與正教信仰的複雜關係（托爾斯泰、陀思妥耶夫斯基時代）'),
('帕拉迪烏斯·拉扎列夫', 'Palladius Raev', '聖彼得堡', '俄羅斯正教會', 14, 1892, 1898, '退休', '沙皇尼古拉二世', '正統', 'Moscow Patriarchate', '尼古拉二世登基（1894年）；俄羅斯工業化與無產階級化引發的社會主義思想衝擊教會'),
('安東尼·瓦卡諾夫斯基', 'Antoniy Vadkovsky', '聖彼得堡', '俄羅斯正教會', 15, 1898, 1912, '逝世', '沙皇尼古拉二世', '正統', 'Moscow Patriarchate', '1905年革命；神父格里戈里·拉斯普廷進入彼得堡宮廷圈（1905年後）；安東尼主教與自由派改革的同情'),
('弗拉基米爾·博哥亞夫連斯基', 'Vladimir Bogoyavlensky', '聖彼得堡', '俄羅斯正教會', 16, 1912, 1915, '調任', '沙皇尼古拉二世', '正統', 'Moscow Patriarchate', '後調任基輔；1918年在基輔被布爾什維克殺害——俄羅斯正教會第一位在蘇維埃政權下殉道的主教；1992年列聖為新殉道者'),
('皮提里姆·奧克諾夫', 'Pitirim Oknov', '聖彼得堡', '俄羅斯正教會', 17, 1915, 1917, '辭退', '臨時政府', '爭議', 'Moscow Patriarchate', '第一次世界大戰；皇后亞歷山德拉與拉斯普廷影響下任命（故稱「拉斯普廷主教」）；1917年2月革命後被臨時政府迫令辭職'),
('本雅明·卡贊斯基', 'Benjamin Kazansky', '聖彼得堡', '俄羅斯正教會', 18, 1917, 1922, '殉道', '全俄主教公會議', '正統', 'Russian Orthodox martyrology; ROCOR', '1917年全俄主教公會議（恢復牧首制）後首任本地選出的都主教；1922年列寧「強制徵收教會財產」（以救濟饑荒為由）；本雅明拒絕交出聖物；以「反革命」罪被起訴——8月13日槍決；1992年列聖為新殉道者；俄羅斯正教會受難時代的象徵人物'),
('尼古拉·亞德洛夫斯基', 'Nikolai Yarushevich', '聖彼得堡', '俄羅斯正教會', 23, 1944, 1960, '被迫辭職', '蘇聯政府/聖主教會議', '正統', 'Moscow Patriarchate', '1944年列寧格勒（聖彼得堡）圍城解除後重建；國家安全委員會（KGB）對教會的滲透與控制；因在日內瓦公開批評蘇聯宗教政策而被克魯曉夫政府迫令辭職——蘇聯唯一敢公開批評政府的大主教'),
('尼科迪姆·羅托夫', 'Nikodim Rotov', '聖彼得堡', '俄羅斯正教會', 25, 1963, 1978, '逝世（梵蒂岡）', '聖主教會議', '正統', 'Moscow Patriarchate; Vatican records', '蘇聯時代最重要的教會外交家；與梵二大公會議期間的天主教建立秘密聯繫；率先與羅馬教廷接觸；1978年9月5日在梵蒂岡覲見甫當選的教宗若望保祿一世時突發心臟病逝世——年僅48歲；是其培養了後來的牧首阿列克謝二世（Aleksiy II）'),
('阿列克謝·里迪格爾', 'Aleksiy Ridiger', '聖彼得堡', '俄羅斯正教會', 27, 1986, 1990, '調任（任牧首）', '聖主教會議', '正統', 'Moscow Patriarchate', '1990年戈爾巴喬夫改革（宗教自由化）前後；該年當選莫斯科牧首（阿列克謝二世，1990-2008）；聖彼得堡正值蘇聯解體前夕，宗教生活恢復活躍；從列寧格勒恢復名稱聖彼得堡（1991年）'),
('約安·斯尼切夫', 'Ioann Snychev', '聖彼得堡', '俄羅斯正教會', 28, 1990, 1995, '逝世', '莫斯科牧首', '正統', 'Moscow Patriarchate', '極保守的民族主義者；著有《俄羅斯統一》等書，宣揚俄羅斯正教民族神話；後期影響了俄羅斯右翼民族主義思潮'),
('弗拉基米爾·科特利亞羅夫', 'Vladimir Kotlyarov', '聖彼得堡', '俄羅斯正教會', 29, 1995, 2014, '退休', '莫斯科牧首', '正統', 'Moscow Patriarchate', '葉利欽和普京時代；聖彼得堡教堂大規模歸還（從博物館/世俗機構歸還教會）；聖以薩大教堂歸還爭議'),
('瓦爾索諾菲·蘇達科夫', 'Varsonofy Sudakov', '聖彼得堡', '俄羅斯正教會', 30, 2014, NULL, NULL, '莫斯科牧首', '正統', 'Moscow Patriarchate', '當代在任都主教；俄羅斯東正教在普京政府的民族-宗教融合政策下；2022年俄烏戰爭後教會的艱難立場');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '聖彼得堡' AND church = '俄羅斯正教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 基輔及全烏克蘭都主教（俄羅斯正教會）
-- 988年弗拉基米爾大公受洗——東斯拉夫基督化的根源
-- ==============================
('米哈伊爾一世', 'Mykhailo I', '基輔（莫斯科）', '俄羅斯正教會', 1, 988, 992, '逝世', '普世牧首（君士坦丁堡）', '正統', 'Kyiv Pechera Chronicle', '基輔魯斯第一任都主教；傳統上由君士坦丁堡派遣；弗拉基米爾大公988年在第聶伯河（Dnipro）集體施洗後組織教會架構；其民族身份不詳（可能是希臘人或保加利亞人）'),
('列昂提耶·翁帕卡諾斯', 'Leontiy', '基輔（莫斯科）', '俄羅斯正教會', 2, 992, 1008, '逝世', '普世牧首（君士坦丁堡）', '正統', 'Chronicle records', '第二任基輔都主教；繼續基督教化工作；基輔山城（城堡山）的教堂建設'),
('伊拉里昂', 'Ilarion', '基輔（莫斯科）', '俄羅斯正教會', 5, 1051, 1054, '不明', '雅羅斯拉夫大公', '正統', 'Chronicle; Sermon on Law and Grace', '第一位本土（斯拉夫人）基輔都主教（非希臘人）；雅羅斯拉夫大公繞過君士坦丁堡自行任命；著《律法與恩典佈道》（Sermon on Law and Grace）——最早的東斯拉夫文學傑作之一；確立羅斯教會本地化的重要一步'),
('佩奧德爾（盧卡斯）', 'Feodor / Lukhas', '基輔（莫斯科）', '俄羅斯正教會', 11, 1147, 1156, '被廢', '基輔大公', '爭議', 'Chronicle records', '分裂時代；基輔大公政治鬥爭中主教任命成為棋子；此時已有複數聲索者'),
('克里蒙·斯莫利亞提奇', 'Kliment Smolyatich', '基輔（莫斯科）', '俄羅斯正教會', 12, 1147, 1155, '流亡', '伊賈斯拉夫二世大公', '爭議', 'Chronicle; Epistle to Thomas', '第二位斯拉夫裔都主教（繞過君士坦丁堡選出）；著《致托馬斯書信》——俄羅斯中世紀神學首部原典；但因政治動盪未能穩定任職'),
('西里爾一世', 'Kyrylo I', '基輔（莫斯科）', '俄羅斯正教會', 17, 1224, 1233, '逝世', '教會', '正統', 'Chronicle records', '蒙古入侵前夜；1223年卡爾卡河之戰（Mongol first raid into Rus''）後的緊張局勢'),
('約瑟夫', 'Iosyp', '基輔（莫斯科）', '俄羅斯正教會', 18, 1236, 1240, '失蹤', '君士坦丁堡', '正統', 'Hypatian Chronicle', '1240年拔都汗（Batu Khan）蒙古軍隊洗劫基輔——基輔魯斯文明的最大劫難；約瑟夫下落不明，或逃亡，或死亡；都主教座開始漂移'),
('馬克西姆', 'Maxym', '基輔（莫斯科）', '俄羅斯正教會', 20, 1283, 1305, '逝世', '君士坦丁堡', '正統', 'Chronicle records', '1299年將都主教居所從基輔遷往弗拉基米爾（Vladimir-on-Klyazma）——基輔魯斯政治重心北移的宗教確認；蒙古金帳汗國統治下，基輔已廢墟'),
('彼得', 'Petro', '基輔（莫斯科）', '俄羅斯正教會', 21, 1308, 1326, '逝世（莫斯科）', '君士坦丁堡', '正統', 'Moscow Patriarchate chronicles', '長期在莫斯科居住；1326年死於莫斯科並埋葬於此——被後世視為莫斯科牧首制的靈性奠基者；列聖；莫斯科克里姆林宮升天大教堂（Uspensky Sobor）的精神前輩'),
('伊西多爾（裂教前）', 'Isidore of Kiev', '基輔（莫斯科）', '俄羅斯正教會', 30, 1436, 1441, '廢黜', '君士坦丁堡', '爭議', 'Florence Council records', '1439年費拉拉-佛羅倫薩大公會議（Council of Florence）代表；簽署東西方合一協議——回到莫斯科後被大公瓦西里二世廢黜和驅逐，因為他簽約承認羅馬教宗優先地位；此事件直接觸發俄羅斯教會與君士坦丁堡的最終決裂'),
('約納（第一任莫斯科牧首前身）', 'Iona', '基輔（莫斯科）', '俄羅斯正教會', 31, 1448, 1461, '逝世', '俄羅斯主教公會議（自選）', '正統', 'Moscow Patriarchate', '1448年俄羅斯主教自行選出——無需君士坦丁堡批准——正式宣告俄羅斯教會的事實自主；1453年君士坦丁堡陷落後此自主獲得廣泛認可；列聖'),
('安德烈·沙格諾夫斯基', 'Andriy Shahnovsky', '基輔（莫斯科）', '俄羅斯正教會', 40, 1631, 1647, '逝世', '君士坦丁堡', '正統', 'Chronicle records', '哥薩克-烏克蘭時代；莫吉拉（Peter Mohyla）都主教（1633-1647）的時代——成立基輔莫吉拉學院（Kyiv-Mohyla Academy，現名），今乃東歐最古老大學之一'),
('吉德昂·斯維亞托波爾克-切特維爾廷斯基', 'Gedeon Sviatopolk-Chetvertinsky', '基輔（莫斯科）', '俄羅斯正教會', 43, 1685, 1690, '逝世', '莫斯科牧首', '正統', 'Moscow Patriarchate', '1685年：基輔都主教轄區從君士坦丁堡移交莫斯科牧首（1686年普世牧首簽署，後被2018年普世牧首召回）——烏克蘭教會命運的歷史轉折；此任命是基輔教會臣服於莫斯科的起點'),
('菲拉列特·杰尼先科', 'Filaret Denysenko', '基輔（莫斯科）', '俄羅斯正教會', 66, 1966, 1990, '辭職（另立）', '莫斯科牧首', '爭議', 'Moscow Patriarchate', '蘇聯解體前夜；1990年申請競選莫斯科牧首失敗；轉而要求烏克蘭教會獨立；1992年被莫斯科牧首革除；另立「基輔牧首轄區」（UOC-KP），被正統世界視為分裂主義——但在烏克蘭民族主義者中享有崇高聲望'),
('弗拉基米爾·薩博丹', 'Volodymyr Sabodan', '基輔（莫斯科）', '俄羅斯正教會', 67, 1992, 2014, '逝世', '莫斯科牧首', '正統', 'Moscow Patriarchate', '烏克蘭獨立後在莫斯科牧首旗幟下維護教會統一；橙色革命（2004年）和廣場革命（2014年）之間的調和立場；2014年逝世時烏克蘭正值革命與俄羅斯入侵克里米亞前夕'),
('奧努弗里·別列佐夫斯基', 'Onufriy Berezovsky', '基輔（莫斯科）', '俄羅斯正教會', 68, 2014, NULL, NULL, '莫斯科牧首', '正統', 'Moscow Patriarchate', '2014年親俄雅努科維奇政府倒台後任命；效忠莫斯科牧首；2022年俄烏全面戰爭後處境極度敏感——大量烏克蘭信眾和神職人員離開UOC（莫斯科牧首轄）轉向OCU；澤倫斯基政府對UOC展開法律調查；烏克蘭議會2023年通過法律限制與「侵略國」有聯繫的宗教組織');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '基輔（莫斯科）' AND church = '俄羅斯正教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 基輔及全烏克蘭都主教（烏克蘭正教會 OCU）
-- 2019年普世牧首授予自主敕令（tomos）
-- ==============================
('菲拉列特·杰尼先科（名譽牧首）', 'Filaret Denysenko (Patriarch Emeritus)', '基輔（烏克蘭）', '烏克蘭正教會', 1, 1995, 2018, '名譽牧首', '基輔牧首轄區主教會議', '爭議', 'UOC-KP; Ecumenical Patriarchate', '1992年被莫斯科牧首革除後自立「基輔牧首轄區」（UOC-KP）並自封牧首；2018年UOC-KP與「烏克蘭自主正教會」（UAOC）合併成立統一OCU前的主要領導人；普世牧首2019年授予OCU自主敕令後改為「名譽牧首」；2019年解除對其革除的處分（象徵性復職）——但此舉被莫斯科牧首拒絕承認；在烏克蘭民族主義者眼中是教會獨立的精神父親'),
('葉皮方尼·杜緬科', 'Epifaniy Dumenko', '基輔（烏克蘭）', '烏克蘭正教會', 2, 2019, NULL, NULL, '統一公會議（Unification Council）', '正統', 'Orthodox Church of Ukraine; Ecumenical Patriarchate', '2019年1月5日普世牧首巴爾多祿茂在君士坦丁堡親自授予OCU自主敕令（tomos of autocephaly）；2月3日聖安得烈教堂在基輔正式接受；葉皮方尼年僅39歲當選——東正教史上最年輕的自主教會領袖之一；莫斯科牧首拒絕承認OCU；2022年俄烏戰爭後大量教眾從UOC（莫斯科）轉向OCU；烏克蘭政府積極支持OCU');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '基輔（烏克蘭）' AND church = '烏克蘭正教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 明斯克及白俄羅斯都主教（俄羅斯正教會）
-- 白俄羅斯正教會中心；長期為莫斯科牧首管轄
-- ==============================
('瓦爾拉姆·霍特緬斯基', 'Varlaam Khotmensky', '明斯克', '俄羅斯正教會', 1, 1793, 1812, '逝世', '聖主教會議', '正統', 'Moscow Patriarchate', '1793年波蘭第二次瓜分後明斯克歸入俄羅斯帝國；明斯克主教區設立；波蘭天主教和東儀天主教（Uniates）在此地區的複雜遺產'),
('阿克薩基·塔蒂奇夫', 'Aksaky Tatishchev', '明斯克', '俄羅斯正教會', 3, 1812, 1821, '調任', '沙皇亞歷山大一世', '正統', 'Moscow Patriarchate', '拿破崙入侵俄羅斯（1812年）——明斯克是法軍進軍路線；戰後重建白俄羅斯教會架構'),
('彼拉·拉夫羅夫', 'Pilar Lavrov', '明斯克', '俄羅斯正教會', 8, 1834, 1840, '調任', '聖主教會議', '正統', 'Moscow Patriarchate', '1839年布列斯特合一教會（Uniate Church）廢除——強制將東儀天主教徒併入俄羅斯正教會；波洛茨克教會合一是沙俄統一主義最重要的宗教政治行動'),
('米哈伊爾·科扎奇斯基', 'Mikhail Kozachinsky', '明斯克', '俄羅斯正教會', 12, 1868, 1880, '逝世', '沙皇亞歷山大二世', '正統', 'Moscow Patriarchate', '1863年波蘭/立陶宛起義後沙俄對白俄羅斯的俄化政策強化；正教教會作為俄羅斯化工具'),
('格奧爾吉·亞洛先科', 'Georgy Yaroshenko', '明斯克', '俄羅斯正教會', 18, 1922, 1927, '逮捕', '蘇聯政府下主教會議', '正統', 'Moscow Patriarchate; Soviet archives', '列寧強制徵收教會財產運動中在任；布爾什維克對白俄羅斯教會的系統性迫害；神職人員逮捕浪潮'),
('潘泰萊蒙·羅任諾夫斯基', 'Panteleimon Rozhnovsky', '明斯克', '俄羅斯正教會', 22, 1942, 1944, '撤退（德軍）', '德國佔領下', '爭議', 'Moscow Patriarchate; German occupation records', '德國佔領白俄羅斯期間（1941-1944）；在德軍許可下重開教堂（納粹「宗教自由化」政策，以對抗蘇聯無神論）；1944年德軍撤退時離境；白俄羅斯是二戰中破壞最嚴重的地區之一（三分之一人口喪生）'),
('皮提里姆·斯維里多夫', 'Pitirim Svridov', '明斯克', '俄羅斯正教會', 24, 1944, 1959, '調任', '莫斯科牧首', '正統', 'Moscow Patriarchate', '戰後重建；赫魯曉夫反宗教運動（1958-1964年）前的短暫相對自由期'),
('菲拉列特·瓦克羅梅耶夫', 'Filaret Vakhromeev', '明斯克', '俄羅斯正教會', 30, 1978, 2013, '退休', '莫斯科牧首', '正統', 'Moscow Patriarchate', '在任35年；白俄羅斯1991年獨立後獲「白俄羅斯教會牧首代表（Exarch）」稱號；盧卡申科威權政府（1994年起）與教會的複雜共生關係；2020年白俄羅斯選舉舞弊抗議期間教會的模糊態度'),
('保羅·波諾馬廖夫', 'Pavel Ponomarev', '明斯克', '俄羅斯正教會', 31, 2013, 2021, '調任', '莫斯科牧首', '正統', 'Moscow Patriarchate', '2020年白俄羅斯大規模抗議運動中的教會態度；部分神職人員為示威者提供庇護，引發當局不滿'),
('本雅明·圖別科', 'Benjamin Tupeko', '明斯克', '俄羅斯正教會', 32, 2021, NULL, NULL, '莫斯科牧首', '正統', 'Moscow Patriarchate', '當代在任都主教；盧卡申科政府下白俄羅斯正教會的政治處境；2022年俄烏戰爭後白俄羅斯作為俄羅斯軍事基地的問題讓教會面臨道德困境');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '明斯克' AND church = '俄羅斯正教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
