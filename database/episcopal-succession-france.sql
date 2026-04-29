-- ============================================================
-- 天主教大主教傳承——法國（巴黎、蘭斯、里昂）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 巴黎（Paris）
-- 250年為主教區；1622年升為總主教區
-- 此列表含部分前1622年著名主教及1622年後所有總主教
-- ==============================
('聖德尼', 'Saint Denis (Dionysius)', '巴黎', '天主教', 1, 250, 272, '殉道', '使徒傳承', '正統', 'Catholic Hierarchy; Butler''s Lives', '傳統上為巴黎首任主教；斬首殉道；法國主保聖人；孟馬特（Montmartre）即「殉道者之山」'),
('聖馬塞爾', 'Saint Marcel of Paris', '巴黎', '天主教', 9, 360, 436, '逝世', '教會傳承', '正統', 'Duchesne, Fastes', '著名驅魔師；巴黎守護聖人之一'),
('戈茲蘭', 'Gozlin (Gauslin)', '巴黎', '天主教', 27, 884, 886, '逝世', '教會傳承', '正統', 'Annales de Saint-Bertin', '885–886年抵抗諾曼人圍城的英雄；巴黎保衛戰的精神領袖'),
('莫里斯·德蘇利', 'Maurice de Sully', '巴黎', '天主教', 40, 1160, 1196, '退休', '亞歷山大三世', '正統', 'Gallia Christiana', '巴黎聖母院建設的發起者（1163年奠基）；推動神職教育改革'),
('歐德·德蘇利', 'Eudes de Sully', '巴黎', '天主教', 41, 1197, 1208, '逝世', '教宗英諾森三世', '正統', 'Gallia Christiana', '繼續聖母院建設；推行第四次拉特朗大公會議前置改革'),
('吉約姆·德奧韋涅', 'Guillaume d''Auvergne (William of Auvergne)', '巴黎', '天主教', 44, 1228, 1249, '逝世', '教宗額我略九世', '正統', 'Gallia Christiana; DSB', '哲學家神學家；調和亞里士多德哲學與基督教神學；托馬斯·阿奎那早期思想受其影響'),
('艾蒂安·坦皮耶', 'Étienne Tempier', '巴黎', '天主教', 53, 1268, 1279, '逝世', '教宗克萊孟四世', '正統', 'Gallia Christiana; Denifle & Chatelain', '1277年頒布219條禁令（含阿奎那部分命題）；影響中世紀哲學走向'),
('皮埃爾·德拉福雷', 'Pierre de la Forêt', '巴黎', '天主教', 63, 1363, 1371, '轉任', '教宗英諾森六世', '正統', 'Gallia Christiana', '百年戰爭期間；後任樞機'),

-- 1622年後歷任總主教
('讓-弗朗索瓦·德貢迪', 'Jean-François de Gondi', '巴黎', '天主教', 69, 1622, 1654, '退休', '教宗額我略十五世', '正統', 'Gallia Christiana; Catholic Hierarchy', '巴黎首任總主教（1622年路易十三促成升格）'),
('讓-弗朗索瓦·保羅·德貢迪（德雷茲樞機）', 'Jean-François Paul de Gondi (Cardinal de Retz)', '巴黎', '天主教', 70, 1654, 1662, '退休', '教宗英諾森十世', '正統', 'Gallia Christiana; de Retz Mémoires', '著名《回憶錄》作者；投石黨（Fronde）領袖；樞機；最終與路易十四和解後辭職'),
('阿爾東·德佩雷菲克斯', 'Hardouin de Péréfixe', '巴黎', '天主教', 71, 1664, 1671, '逝世', '教宗亞歷山大七世', '正統', 'Gallia Christiana', '路易十四的家庭教師；鎮壓詹森主義'),
('弗朗索瓦·德阿爾萊', 'François de Harlay de Champvallon', '巴黎', '天主教', 72, 1671, 1695, '逝世', '教宗克萊孟十世', '正統', 'Gallia Christiana', '路易十四御用大主教；南特敕令廢除後迫害胡格諾派'),
('路易-安托万·德諾阿耶', 'Louis-Antoine de Noailles', '巴黎', '天主教', 73, 1695, 1729, '逝世', '教宗英諾森十二世', '正統', 'Gallia Christiana', '樞機；初期同情詹森主義，晚年接受《一主通諭》（Unigenitus, 1713）'),
('夏爾·德萬提米爾', 'Charles de Vintimille du Luc', '巴黎', '天主教', 74, 1729, 1746, '逝世', '教宗本篤十三世', '正統', 'Gallia Christiana', '樞機；推行反詹森主義政策'),
('克里斯托弗·德博蒙', 'Christophe de Beaumont', '巴黎', '天主教', 75, 1746, 1781, '逝世', '教宗本篤十四世', '正統', 'Gallia Christiana', '樞機；強烈反詹森主義；拒絕為拒絕接受《一主通諭》者施末傅，引發政治風波'),
('安托万·勒奧納爾·德洛梅尼·德布里耶納', 'Antoine de Loménie de Brienne', '巴黎', '天主教', 76, 1781, 1788, '辭職', '教宗庇護六世', '正統', 'Gallia Christiana', '後出任法國首席大臣（1787–1788）；法國大革命前夕'),
('安托万-埃萊奧諾爾·勒克萊爾·德居尼', 'Antoine de Juigné', '巴黎', '天主教', 77, 1788, 1801, '流亡', '教宗庇護六世', '正統', 'Gallia Christiana', '大革命爆發後流亡；1801年與拿破崙簽訂《政教協議》後辭職'),
('讓-巴蒂斯特·德貝盧瓦-莫朗格勒', 'Jean-Baptiste de Belloy', '巴黎', '天主教', 78, 1802, 1808, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '政教協議後首任大主教；樞機；拿破崙加冕典禮主禮'),
('讓-西弗蘭·莫里', 'Jean-Sifrein Maury', '巴黎', '天主教', 79, 1810, 1816, '撤職', '拿破崙一世（教宗未完全承認）', '爭議', 'Catholic Hierarchy', '波拿巴主義樞機；教宗未正式任命；波旁復辟後被撤職'),
('亞歷山大-安熱利克·德塔列朗-佩里戈爾', 'Alexandre de Talleyrand-Périgord', '巴黎', '天主教', 80, 1817, 1821, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '著名政治家塔列朗的叔父；樞機'),
('路易-阿雅桑特·德克萊昂', 'Louis-Hyacinthe de Quélen', '巴黎', '天主教', 81, 1821, 1839, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '樞機；1830年七月革命期間大主教府被燒毀；保守的保皇黨人'),
('德尼-奧古斯特·阿弗爾', 'Denis-Auguste Affre', '巴黎', '天主教', 82, 1840, 1848, '殉道', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '1848年六月起義中赴街壘調停，中彈身亡；被視為殉道者'),
('瑪麗-多米尼克-奧古斯特·錫布爾', 'Marie-Dominique-Auguste Sibour', '巴黎', '天主教', 83, 1848, 1857, '殉道', '教宗庇護九世', '正統', 'Catholic Hierarchy', '被一名被吊銷神職的神父刺殺；第二位殉道大主教'),
('弗朗索瓦-尼古拉-馬德萊納·莫爾洛', 'François-Nicolas Morlot', '巴黎', '天主教', 84, 1857, 1862, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '樞機'),
('喬治·達爾博伊', 'Georges Darboy', '巴黎', '天主教', 85, 1863, 1871, '殉道', '教宗庇護九世', '正統', 'Catholic Hierarchy', '1871年巴黎公社期間被共產主義者槍決；第三位殉道大主教'),
('若瑟-伊珀利特·吉貝爾', 'Joseph-Hippolyte Guibert', '巴黎', '天主教', 86, 1871, 1886, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '樞機；發起建造聖心聖殿（Sacré-Cœur，1875–1914）以補贖公社罪行'),
('弗朗索瓦-馬里-本雅明·理查', 'François-Marie-Benjamin Richard', '巴黎', '天主教', 87, 1886, 1908, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；德雷福斯事件期間；政教分離法（1905）'),
('萊昂-阿道夫·阿梅特', 'Léon-Adolphe Amette', '巴黎', '天主教', 88, 1908, 1920, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；一戰期間牧養巴黎'),
('路易-埃内斯特·杜布瓦', 'Louis-Ernest Dubois', '巴黎', '天主教', 89, 1920, 1929, '逝世', '教宗本篤十五世', '正統', 'Catholic Hierarchy', '樞機'),
('讓·韋爾迪耶', 'Jean Verdier', '巴黎', '天主教', 90, 1929, 1940, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；大建設時期——在巴黎郊區興建數十座教堂'),
('埃馬紐埃爾·絮阿爾', 'Emmanuel Suhard', '巴黎', '天主教', 91, 1940, 1949, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；二戰德國佔領期間；牧函《教會的成長》（Essor ou Déclin）影響深遠'),
('莫里斯·費爾坦', 'Maurice Feltin', '巴黎', '天主教', 92, 1949, 1966, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議參與者'),
('皮埃爾·伏若', 'Pierre Veuillot', '巴黎', '天主教', 93, 1966, 1968, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；在任僅兩年即逝'),
('弗朗索瓦·馬爾蒂', 'François Marty', '巴黎', '天主教', 94, 1968, 1981, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；1968年五月運動後的巴黎；梵二後改革推動者'),
('讓-馬里·呂斯蒂傑', 'Jean-Marie Lustiger', '巴黎', '天主教', 95, 1981, 2005, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；猶太裔皈依者（生於猶太家庭，1940年受洗）；若望保祿二世的密友；巴黎天主教復興的旗手'),
('安德烈·凡特-特羅瓦', 'André Vingt-Trois', '巴黎', '天主教', 96, 2005, 2017, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；法國主教團主席'),
('米歇爾·奧珀蒂', 'Michel Aupetit', '巴黎', '天主教', 97, 2017, 2021, '辭職', '教宗方濟各', '正統', 'Catholic Hierarchy', '道德醜聞後自請辭職'),
('洛朗·于里克', 'Laurent Ulrich', '巴黎', '天主教', 98, 2022, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '巴黎聖母院大火（2019）後的修復期間就任');

-- 設定前驅關係
WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '巴黎' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 蘭斯（Reims）
-- 法蘭克王國最重要的主教座
-- ==============================
('聖西克斯圖斯', 'Saint Sixtus of Reims', '蘭斯', '天主教', 1, 260, 290, '逝世', '使徒傳承', '正統', 'Gallia Christiana', '蘭斯首任主教；傳統上由教宗西斯篤一世派遣'),
('聖雷米', 'Saint Remigius (Rémi)', '蘭斯', '天主教', 22, 459, 533, '逝世', '教會選舉', '正統', 'Gallia Christiana; Gregory of Tours', '在任74年；為法蘭克國王克洛維一世施洗（496年）——法蘭西基督化的關鍵時刻；「法蘭克使徒」'),
('艾博', 'Ebo (Ebbo)', '蘭斯', '天主教', 33, 816, 845, '廢黜', '教宗斯蒂芬四世', '爭議', 'Gallia Christiana', '查理大帝的奶兄；路易虔誠者廢黜後（835）一度復位（840–845）；傳教士；在梅茨（835年）被迫辭職'),
('欣克馬爾', 'Hincmar of Reims', '蘭斯', '天主教', 34, 845, 882, '逝世', '教宗謝爾吉烏斯二世', '正統', 'Gallia Christiana; MGH', '加洛林帝國最重要的教會法學家；與教宗尼古拉一世就主教管轄權激烈爭論；《論離婚》等著作影響深遠'),
('阿達爾貝隆', 'Adalberon (Adalbéron)', '蘭斯', '天主教', 41, 969, 988, '逝世', '鄂圖二世', '正統', 'Gallia Christiana; Richer', '987年加冕于格·卡佩（Hugues Capet）為法蘭西國王——卡佩王朝的開端；改革本篤會修道'),
('阿爾諾爾一世', 'Arnulf I', '蘭斯', '天主教', 42, 988, 991, '廢黜', '教宗若望十五世', '爭議', 'Gallia Christiana', '查理曼後裔支持者；因向加洛林覬覦者開城被廢黜'),
('日爾貝·道里亞克（後成教宗西爾維斯特二世）', 'Gerbert of Aurillac (later Pope Sylvester II)', '蘭斯', '天主教', 43, 991, 998, '辭職', '法王於格·卡佩', '正統', 'Gallia Christiana; John Contreni', '中世紀最博學者之一；引進阿拉伯數字和算盤至西歐；999年成為第一位法蘭西裔教宗（西爾維斯特二世）'),
('阿爾諾爾一世（復位）', 'Arnulf I (restored)', '蘭斯', '天主教', 44, 998, 1021, '逝世', '教宗西爾維斯特二世', '正統', 'Gallia Christiana', '復位後維持教區穩定'),
('居博·德布朗仙曼', 'Guillaume aux Blanches Mains', '蘭斯', '天主教', 57, 1176, 1202, '逝世', '教宗亞歷山大三世', '正統', 'Gallia Christiana', '腓力二世的叔父；第三次十字軍東征推動者；樞機'),
('雷諾爾·德沙爾特爾', 'Regnault (Renaud) de Chartres', '蘭斯', '天主教', 69, 1414, 1444, '逝世', '教宗若望二十三世（對立）', '正統', 'Gallia Christiana', '1429年主持查理七世加冕典禮（聖女貞德親歷）；外交家；勃艮第和談的斡旋者'),
('夏爾·德吉斯（洛林樞機）', 'Charles de Guise (Cardinal de Lorraine)', '蘭斯', '天主教', 75, 1538, 1574, '逝世', '教宗保羅三世', '正統', 'Gallia Christiana', '特倫托大公會議（1562–1563）的法國代表；哈布斯堡-法國關係的樞紐；吉斯家族核心人物；反宗教改革推手'),
('路易·德吉斯', 'Louis de Guise', '蘭斯', '天主教', 76, 1574, 1578, '逝世', '教宗庇護五世', '正統', 'Gallia Christiana', '樞機；吉斯家族'),
('夏爾·德波旁（「蘭斯的樞機」）', 'Charles de Bourbon', '蘭斯', '天主教', 77, 1578, 1590, '逝世', '教宗額我略十三世', '爭議', 'Gallia Christiana', '天主教聯盟（Catholic League）中期間，西班牙擁立其為「查理十世」；實際在亨利四世手中去世'),
('夏爾-莫里斯·勒泰利耶', 'Charles-Maurice Le Tellier', '蘭斯', '天主教', 81, 1671, 1710, '逝世', '教宗克萊孟十世', '正統', 'Gallia Christiana', '陸軍大臣盧瓦侯爵之兄；路易十四宗教政策的執行者；南特敕令廢除（1685）後鎮壓胡格諾派'),
('阿爾曼-于勒·德羅昂', 'Armand-Jules de Rohan-Gesvres', '蘭斯', '天主教', 83, 1722, 1762, '逝世', '教宗英諾森十三世', '正統', 'Gallia Christiana', '樞機；啟蒙時代；重建蘭斯主教宮'),
('亞歷山大-安熱利克·德塔列朗-佩里戈爾', 'Alexandre de Talleyrand-Périgord', '蘭斯', '天主教', 85, 1777, 1794, '流亡', '教宗庇護六世', '正統', 'Gallia Christiana', '著名政治家塔列朗的叔父；大革命後流亡；後轉任巴黎大主教'),
('托馬斯-瑪麗-約瑟夫·古拉爾', 'Thomas-Marie-Joseph Gousset', '蘭斯', '天主教', 87, 1840, 1866, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '樞機；著名神學家；《道德神學》著作影響深遠'),
('本諾瓦-瑪麗·朗熱內', 'Benoît-Marie Langénieux', '蘭斯', '天主教', 89, 1874, 1905, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '樞機；1896年主持蘭斯主教座堂落成；聖女貞德平反運動的推動者'),
('路易-亨利-約瑟夫·盧松', 'Louis-Henri-Joseph Luçon', '蘭斯', '天主教', 90, 1906, 1930, '退休', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；一戰期間蘭斯大教堂被砲火嚴重破壞（1914）；戰後主持重建'),
('埃里克·德穆蘭-波福爾', 'Éric de Moulins-Beaufort', '蘭斯', '天主教', 95, 2018, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '法國主教團主席（2019–）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '蘭斯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 里昂（Lyon）
-- 西方教會最古老的主教座之一
-- ==============================
('聖波提諾', 'Saint Pothinus (Photinus)', '里昂', '天主教', 1, 150, 177, '殉道', '使徒傳承', '正統', 'Eusebius, Historia Ecclesiastica', '里昂首任主教；177年馬可奧里略迫害中遇難；「里昂殉道者書信」保存了其殉道記錄'),
('聖愛任紐', 'Saint Irenaeus of Lyon', '里昂', '天主教', 2, 177, 202, '殉道（傳統說法）', '教會傳承', '正統', 'Eusebius; Adversus Haereses', '早期教會最偉大的神學家之一；《駁異端》（Adversus Haereses）系統批判諾斯替主義；護教士；「使徒傳統」神學的奠基人'),
('阿戈巴爾德', 'Agobard of Lyon', '里昂', '天主教', 15, 816, 840, '逝世', '查理大帝', '正統', 'MGH; PL 104', '加洛林時代偉大神學家；反對試驗審判（ordeal）和迷信；支持路易虔誠者改革；著作包括《反猶太人書信》（批評迫害）'),
('伊夫·德夏尼', 'Humbert de Romans', '里昂', '天主教', 33, 1272, 1306, '退休', '教宗額我略十世', '正統', 'Gallia Christiana', '1274年里昂第二次大公會議主持教宗額我略十世；臨時東西合一（拜占廷代表參加）；達那實（Dante）在神曲中提及'),
('皮埃爾·德塔朗泰斯（後為英諾森五世）', 'Pierre de Tarentaise (later Pope Innocent V)', '里昂', '天主教', 34, 1272, 1274, '辭職（就任教宗）', '教宗額我略十世', '正統', 'Gallia Christiana', '多明我會；1276年成為短命教宗英諾森五世（在任5個月）'),
('貝特朗·德戈特（後為克萊孟五世）', 'Bertrand de Got (later Pope Clement V)', '里昂', '天主教', 41, 1295, 1299, '辭職（就任教宗）', '教宗本篤八世', '正統', 'Gallia Christiana', '1305年成為教宗克萊孟五世；將教廷遷往阿維尼翁（1309）；「巴比倫之囚」的開端'),
('伊珀利特·達斯泰', 'Hippolyte d''Este', '里昂', '天主教', 56, 1539, 1550, '轉任', '教宗保羅三世', '正統', 'Gallia Christiana', '著名的埃斯特樞機二世；文藝復興風格的非駐地主教；提沃利莊園建造者'),
('皮埃爾·德普尼', 'Antoine de Malvin de Montazet', '里昂', '天主教', 65, 1758, 1788, '逝世', '教宗克萊孟十三世', '正統', 'Gallia Christiana', '啟蒙時代；同情詹森主義；與巴黎議會（Parlement）合作驅逐耶穌會（1762）'),
('皮埃爾-馬里·傑里耶', 'Pierre-Marie Gerlier', '里昂', '天主教', 77, 1937, 1965, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；維希政府時期（1940–1944）；援助猶太兒童；法國天主教大革命後的精神領袖'),
('阿爾貝·德庫爾特雷', 'Albert Decourtray', '里昂', '天主教', 79, 1981, 1994, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；法國主教團主席；推動天主教-猶太對話'),
('路易-馬里·比葉', 'Louis-Marie Billé', '里昂', '天主教', 81, 1998, 2002, '逝世', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；法國主教團主席'),
('菲利普·巴貝蘭', 'Philippe Barbarin', '里昂', '天主教', 82, 2002, 2020, '辭職', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；2019年因包庇戀童癖神父被判緩刑後辭職（後獲撤銷）'),
('奧利維耶·德熱爾梅', 'Olivier de Germay', '里昂', '天主教', 83, 2020, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '接替辭職的巴貝蘭；耶穌會士');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '里昂' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
