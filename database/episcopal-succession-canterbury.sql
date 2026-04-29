-- ============================================================
-- 坎特伯里大主教傳承（天主教 597–1558 + 英格蘭教會 1533–）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources) VALUES

-- 天主教時期（597–1558）
('奧古斯丁', 'Augustine of Canterbury', '坎特伯里', '天主教', 1, 597, 604, '逝世', '教宗額我略一世', '正統', 'Bede, HE I.23; Canterbury records'),
('勞倫斯', 'Laurentius', '坎特伯里', '天主教', 2, 604, 619, '逝世', '奧古斯丁（自任命）', '正統', 'Bede, HE II.4'),
('梅利圖斯', 'Mellitus', '坎特伯里', '天主教', 3, 619, 624, '逝世', '教宗博尼法斯四世', '正統', 'Bede, HE II.7'),
('尤斯圖斯', 'Justus', '坎特伯里', '天主教', 4, 624, 627, '逝世', '教宗博尼法斯五世', '正統', 'Bede, HE II.18'),
('霍諾里烏斯', 'Honorius of Canterbury', '坎特伯里', '天主教', 5, 627, 653, '逝世', '教宗霍諾里烏斯一世', '正統', 'Bede, HE II.18'),
('德奧斯戴迪特', 'Deusdedit', '坎特伯里', '天主教', 6, 655, 664, '逝世（鼠疫）', '坎特伯里主教團', '正統', 'Bede, HE III.20'),
('塔爾蘇斯的西奧多', 'Theodore of Tarsus', '坎特伯里', '天主教', 7, 668, 690, '逝世', '教宗維塔利安', '正統', 'Bede, HE IV.1; organized English church councils'),
('貝特沃爾德', 'Berhtwald', '坎特伯里', '天主教', 8, 693, 731, '逝世', '坎特伯里主教會議', '正統', 'Bede, HE V.8'),
('塔特溫', 'Tatwine', '坎特伯里', '天主教', 9, 731, 734, '逝世', '麥西亞國王', '正統', 'Bede, HE V.23'),
('諾斯黑爾姆', 'Nothelm', '坎特伯里', '天主教', 10, 735, 739, '逝世', '教宗額我略三世', '正統', 'Canterbury records'),
('卡斯伯特', 'Cuthbert of Canterbury', '坎特伯里', '天主教', 11, 740, 758, '逝世', '教宗', '正統', 'Canterbury records'),
('布雷戈溫', 'Bregowine', '坎特伯里', '天主教', 12, 759, 762, '逝世', '教宗保羅一世', '正統', 'Canterbury records'),
('揚伯特', 'Jænberht', '坎特伯里', '天主教', 13, 765, 792, '逝世', '坎特伯里主教會議', '正統', 'Canterbury records'),
('埃塞哈德', 'Æthelhard', '坎特伯里', '天主教', 14, 793, 805, '逝世', '麥西亞國王奧發', '正統', 'Canterbury records'),
('武爾弗雷德', 'Wulfred', '坎特伯里', '天主教', 15, 805, 832, '逝世', '坎特伯里主教', '正統', 'Canterbury records'),
('費奧洛吉爾德', 'Feologild', '坎特伯里', '天主教', 16, 832, 832, '逝世（任內）', '坎特伯里主教', '正統', 'Canterbury records'),
('凱奧諾斯', 'Ceolnoth', '坎特伯里', '天主教', 17, 833, 870, '逝世', '坎特伯里主教', '正統', 'Canterbury records'),
('埃塞爾雷德', 'Æthelred of Canterbury', '坎特伯里', '天主教', 18, 870, 888, '逝世', '西薩克遜國王', '正統', 'Canterbury records'),
('普雷格蒙德', 'Plegmund', '坎特伯里', '天主教', 19, 890, 914, '逝世', '教宗福摩蘇斯', '正統', 'Canterbury records'),
('阿瑟爾姆（一世）', 'Athelm', '坎特伯里', '天主教', 20, 914, 923, '逝世', '西薩克遜國王', '正統', 'Canterbury records'),
('武爾赫爾姆', 'Wulfhelm', '坎特伯里', '天主教', 21, 923, 942, '逝世', '英格蘭國王', '正統', 'Canterbury records'),
('奧達大主教', 'Oda', '坎特伯里', '天主教', 22, 941, 958, '逝世', '英格蘭國王埃德蒙德', '正統', 'Canterbury records'),
('埃爾夫西吉', 'Ælfsige', '坎特伯里', '天主教', 23, 959, 959, '逝世（途中凍死）', '英格蘭國王', '正統', 'Canterbury records'),
('比里赫特黑爾姆', 'Byrhthelm', '坎特伯里', '天主教', 24, 959, 959, '辭職', '英格蘭國王埃德加', '正統', 'Canterbury records'),
('鄧斯坦', 'Dunstan', '坎特伯里', '天主教', 25, 960, 988, '逝世', '教宗約翰十二世', '正統', 'Canterbury records; Dunstan reform movement'),
('埃塞爾加爾', 'Æthelgar', '坎特伯里', '天主教', 26, 988, 990, '逝世', '英格蘭國王', '正統', 'Canterbury records'),
('西格里克·謝里奧', 'Sigeric Serio', '坎特伯里', '天主教', 27, 990, 994, '逝世', '英格蘭國王', '正統', 'Canterbury records'),
('埃爾夫里克', 'Ælfric of Abingdon', '坎特伯里', '天主教', 28, 995, 1005, '逝世', '英格蘭國王', '正統', 'Canterbury records'),
('殉道者阿爾菲吉', 'Alphege (martyr)', '坎特伯里', '天主教', 29, 1006, 1012, '殉道（丹麥人擄殺）', '英格蘭國王埃塞雷德', '正統', 'Canterbury records; ASC'),
('利英', 'Lyfing', '坎特伯里', '天主教', 30, 1013, 1020, '逝世', '英格蘭國王埃塞雷德', '正統', 'Canterbury records'),
('埃塞爾諾斯', 'Æthelnoth', '坎特伯里', '天主教', 31, 1020, 1038, '逝世', '英格蘭國王卡努特', '正統', 'Canterbury records'),
('伊德西吉', 'Eadsige', '坎特伯里', '天主教', 32, 1038, 1050, '逝世', '英格蘭國王', '正統', 'Canterbury records'),
('朱米耶日的羅伯特', 'Robert of Jumièges', '坎特伯里', '天主教', 33, 1051, 1052, '被驅逐', '英格蘭國王愛德華懺悔者', '正統', 'Canterbury records; ASC'),
('斯蒂甘德', 'Stigand', '坎特伯里', '天主教', 34, 1052, 1070, '廢黜', '英格蘭國王哈羅德', '爭議', 'Canterbury records; not recognized by Rome; deposed by Council of Winchester 1070'),
('蘭弗蘭克', 'Lanfranc', '坎特伯里', '天主教', 35, 1070, 1089, '逝世', '教宗亞歷山大二世', '正統', 'Canterbury records; Norman reform'),
('坎特伯里的安瑟倫', 'Anselm of Canterbury', '坎特伯里', '天主教', 36, 1093, 1109, '逝世', '教宗烏爾班二世', '正統', 'Canterbury records; Cur Deus Homo'),
('埃斯居雷的拉爾夫', 'Ralph d''Escures', '坎特伯里', '天主教', 37, 1114, 1122, '逝世', '教宗帕斯加爾二世', '正統', 'Canterbury records'),
('科比爾的威廉', 'William of Corbeil', '坎特伯里', '天主教', 38, 1123, 1136, '逝世', '教宗卡利克斯圖斯二世', '正統', 'Canterbury records'),
('貝克的西奧巴德', 'Theobald of Bec', '坎特伯里', '天主教', 39, 1139, 1161, '逝世', '教宗英諾森二世', '正統', 'Canterbury records'),
('湯瑪斯·貝克特', 'Thomas Becket', '坎特伯里', '天主教', 40, 1162, 1170, '殉道', '英格蘭國王亨利二世（提名）', '正統', 'Canterbury records; canonized 1173'),
('多佛的理查德', 'Richard of Dover', '坎特伯里', '天主教', 41, 1174, 1184, '逝世', '教宗亞歷山大三世', '正統', 'Canterbury records'),
('福爾德的鮑德溫', 'Baldwin of Forde', '坎特伯里', '天主教', 42, 1184, 1190, '逝世（十字軍）', '教宗路修斯三世', '正統', 'Canterbury records'),
('休伯特·沃爾特', 'Hubert Walter', '坎特伯里', '天主教', 43, 1193, 1205, '逝世', '教宗塞萊斯廷三世', '正統', 'Canterbury records; also Justiciar of England'),
('史蒂芬·蘭頓', 'Stephen Langton', '坎特伯里', '天主教', 44, 1207, 1228, '逝世', '教宗英諾森三世', '正統', 'Canterbury records; Magna Carta 1215'),
('理查德·勒格蘭特', 'Richard le Grant', '坎特伯里', '天主教', 45, 1229, 1231, '逝世', '教宗額我略九世', '正統', 'Canterbury records'),
('坎特伯里的聖埃德蒙德', 'Edmund Rich (St Edmund of Canterbury)', '坎特伯里', '天主教', 46, 1234, 1240, '逝世', '教宗額我略九世', '正統', 'Canterbury records; canonized 1246'),
('薩伏依的博尼法斯', 'Boniface of Savoy', '坎特伯里', '天主教', 47, 1245, 1270, '逝世', '教宗英諾森四世', '正統', 'Canterbury records'),
('羅伯特·基爾沃德比', 'Robert Kilwardby', '坎特伯里', '天主教', 48, 1273, 1278, '辭職', '教宗額我略十世', '正統', 'Canterbury records'),
('約翰·佩克漢姆', 'John Peckham', '坎特伯里', '天主教', 49, 1279, 1292, '逝世', '教宗尼古拉三世', '正統', 'Canterbury records'),
('羅伯特·溫切爾西', 'Robert Winchelsey', '坎特伯里', '天主教', 50, 1294, 1313, '逝世', '教宗額我略九世', '正統', 'Canterbury records'),
('沃爾特·雷諾茲', 'Walter Reynolds', '坎特伯里', '天主教', 51, 1313, 1327, '逝世', '教宗克萊孟五世', '正統', 'Canterbury records'),
('西蒙·梅珀漢姆', 'Simon Mepeham', '坎特伯里', '天主教', 52, 1328, 1333, '逝世', '教宗若望二十二世', '正統', 'Canterbury records'),
('約翰·德斯特拉福德', 'John de Stratford', '坎特伯里', '天主教', 53, 1333, 1348, '逝世', '教宗若望二十二世', '正統', 'Canterbury records'),
('湯瑪斯·布拉德沃丁', 'Thomas Bradwardine', '坎特伯里', '天主教', 54, 1349, 1349, '逝世（黑死病）', '教宗克萊孟六世', '正統', 'Canterbury records; Oxford mathematician'),
('西蒙·艾斯利普', 'Simon Islip', '坎特伯里', '天主教', 55, 1349, 1366, '逝世', '教宗克萊孟六世', '正統', 'Canterbury records'),
('西蒙·蘭漢姆', 'Simon Langham', '坎特伯里', '天主教', 56, 1366, 1368, '辭職為樞機', '教宗烏爾班五世', '正統', 'Canterbury records'),
('威廉·惠特爾西', 'William Whittlesey', '坎特伯里', '天主教', 57, 1368, 1374, '逝世', '教宗烏爾班五世', '正統', 'Canterbury records'),
('西蒙·薩德伯里', 'Simon Sudbury', '坎特伯里', '天主教', 58, 1375, 1381, '殉道（農民起義斬首）', '教宗額我略十一世', '正統', 'Canterbury records; Peasants Revolt 1381'),
('威廉·科特尼', 'William Courtenay', '坎特伯里', '天主教', 59, 1381, 1396, '逝世', '教宗烏爾班六世', '正統', 'Canterbury records; persecuted Wycliffites'),
('湯瑪斯·阿倫德爾', 'Thomas Arundel', '坎特伯里', '天主教', 60, 1396, 1414, '逝世', '教宗博尼法斯九世', '正統', 'Canterbury records; twice exiled and restored'),
('羅傑·沃爾登', 'Roger Walden', '坎特伯里', '天主教', 61, 1397, 1399, '廢黜後復位（副主教）', '英格蘭國王理查二世', '對立', 'Canterbury records; appointed by Richard II during Arundel exile; rival_of = 60'),
('亨利·奇切利', 'Henry Chichele', '坎特伯里', '天主教', 62, 1414, 1443, '逝世', '教宗若望二十三世', '正統', 'Canterbury records; All Souls College Oxford'),
('約翰·斯塔福德', 'John Stafford', '坎特伯里', '天主教', 63, 1443, 1452, '逝世', '教宗歐仁四世', '正統', 'Canterbury records'),
('約翰·坎普', 'John Kemp', '坎特伯里', '天主教', 64, 1452, 1454, '逝世', '教宗尼古拉五世', '正統', 'Canterbury records; also Cardinal'),
('湯瑪斯·布奇爾', 'Thomas Bourchier', '坎特伯里', '天主教', 65, 1454, 1486, '逝世', '教宗尼古拉五世', '正統', 'Canterbury records; crowned Richard III and Henry VII'),
('約翰·莫頓', 'John Morton', '坎特伯里', '天主教', 66, 1486, 1500, '逝世', '教宗依諾森八世', '正統', 'Canterbury records; also Lord Chancellor; More served under him'),
('亨利·迪恩', 'Henry Deane', '坎特伯里', '天主教', 67, 1501, 1503, '逝世', '教宗亞歷山大六世', '正統', 'Canterbury records'),
('威廉·沃勒漢姆', 'William Warham', '坎特伯里', '天主教', 68, 1503, 1532, '逝世', '教宗亞歷山大六世', '正統', 'Canterbury records; last pre-Reformation Archbishop'),

-- 過渡至英格蘭教會
('湯瑪斯·克蘭默', 'Thomas Cranmer', '坎特伯里', '英格蘭教會', 69, 1533, 1556, '處決', '英格蘭國王亨利八世', '正統', 'Canterbury records; Book of Common Prayer; executed under Mary I'),
('雷金納德·波爾', 'Reginald Pole', '坎特伯里', '天主教', 70, 1556, 1558, '逝世', '教宗保羅四世', '正統', 'Canterbury records; last Catholic Archbishop; Cardinal; died same day as Mary I'),

-- 英格蘭教會時期（伊麗莎白一世起）
('馬修·帕克', 'Matthew Parker', '坎特伯里', '英格蘭教會', 71, 1559, 1575, '逝世', '英格蘭女王伊麗莎白一世', '正統', 'Canterbury records; Elizabethan Settlement'),
('埃德蒙德·格林達爾', 'Edmund Grindal', '坎特伯里', '英格蘭教會', 72, 1576, 1583, '逝世（免職未成）', '伊麗莎白一世', '正統', 'Canterbury records; suspended by Elizabeth for supporting prophesyings'),
('約翰·懷特吉夫特', 'John Whitgift', '坎特伯里', '英格蘭教會', 73, 1583, 1604, '逝世', '伊麗莎白一世', '正統', 'Canterbury records; enforced uniformity against Puritans'),
('理查德·班克羅夫特', 'Richard Bancroft', '坎特伯里', '英格蘭教會', 74, 1604, 1610, '逝世', '英格蘭國王詹姆斯一世', '正統', 'Canterbury records; oversaw KJV translation'),
('喬治·阿伯特', 'George Abbot', '坎特伯里', '英格蘭教會', 75, 1611, 1633, '逝世', '詹姆斯一世', '正統', 'Canterbury records; accidentally killed a man while hunting'),
('威廉·勞德', 'William Laud', '坎特伯里', '英格蘭教會', 76, 1633, 1645, '處決', '英格蘭國王查理一世', '正統', 'Canterbury records; executed by Parliament 1645; High Church'),
('威廉·朱克森', 'William Juxon', '坎特伯里', '英格蘭教會', 77, 1660, 1663, '逝世', '英格蘭國王查理二世', '正統', 'Canterbury records; attended Charles I at execution'),
('吉爾伯特·謝爾頓', 'Gilbert Sheldon', '坎特伯里', '英格蘭教會', 78, 1663, 1677, '逝世', '查理二世', '正統', 'Canterbury records; Sheldonan Theatre Oxford'),
('威廉·桑克羅夫特', 'William Sancroft', '坎特伯里', '英格蘭教會', 79, 1678, 1690, '免職', '查理二世', '正統', 'Canterbury records; Non-juror; refused oath to William III'),
('約翰·蒂洛森', 'John Tillotson', '坎特伯里', '英格蘭教會', 80, 1691, 1694, '逝世', '威廉三世', '正統', 'Canterbury records; Latitudinarian'),
('湯瑪斯·特尼森', 'Thomas Tenison', '坎特伯里', '英格蘭教會', 81, 1694, 1715, '逝世', '威廉三世', '正統', 'Canterbury records'),
('威廉·韋克', 'William Wake', '坎特伯里', '英格蘭教會', 82, 1716, 1737, '逝世', '喬治一世', '正統', 'Canterbury records; ecumenical contacts with Gallicans'),
('約翰·波特', 'John Potter', '坎特伯里', '英格蘭教會', 83, 1737, 1747, '逝世', '喬治二世', '正統', 'Canterbury records'),
('湯瑪斯·赫林', 'Thomas Herring', '坎特伯里', '英格蘭教會', 84, 1747, 1757, '逝世', '喬治二世', '正統', 'Canterbury records'),
('馬修·赫頓', 'Matthew Hutton', '坎特伯里', '英格蘭教會', 85, 1757, 1758, '逝世', '喬治二世', '正統', 'Canterbury records'),
('湯瑪斯·塞克爾', 'Thomas Secker', '坎特伯里', '英格蘭教會', 86, 1758, 1768, '逝世', '喬治二世', '正統', 'Canterbury records'),
('弗雷德里克·康沃利斯', 'Frederick Cornwallis', '坎特伯里', '英格蘭教會', 87, 1768, 1783, '逝世', '喬治三世', '正統', 'Canterbury records'),
('約翰·摩爾', 'John Moore', '坎特伯里', '英格蘭教會', 88, 1783, 1805, '逝世', '喬治三世', '正統', 'Canterbury records'),
('查爾斯·曼納斯-薩頓', 'Charles Manners-Sutton', '坎特伯里', '英格蘭教會', 89, 1805, 1828, '逝世', '喬治三世', '正統', 'Canterbury records'),
('威廉·豪利', 'William Howley', '坎特伯里', '英格蘭教會', 90, 1828, 1848, '逝世', '喬治四世', '正統', 'Canterbury records; crowned Victoria; last to receive Peter''s Pence'),
('約翰·伯德·薩姆納', 'John Bird Sumner', '坎特伯里', '英格蘭教會', 91, 1848, 1862, '逝世', '維多利亞女王', '正統', 'Canterbury records; first evangelical Archbishop'),
('查爾斯·托馬斯·朗利', 'Charles Thomas Longley', '坎特伯里', '英格蘭教會', 92, 1862, 1868, '逝世', '維多利亞女王', '正統', 'Canterbury records; first Lambeth Conference 1867'),
('阿奇博爾德·坎貝爾·泰特', 'Archibald Campbell Tait', '坎特伯里', '英格蘭教會', 93, 1868, 1882, '逝世', '維多利亞女王', '正統', 'Canterbury records; first Scot to be Archbishop'),
('愛德華·懷特·本森', 'Edward White Benson', '坎特伯里', '英格蘭教會', 94, 1883, 1896, '逝世', '維多利亞女王', '正統', 'Canterbury records; Lincoln Judgment'),
('弗雷德里克·坦普爾', 'Frederick Temple', '坎特伯里', '英格蘭教會', 95, 1897, 1902, '逝世', '維多利亞女王', '正統', 'Canterbury records; Essays and Reviews'),
('蘭德爾·托馬斯·戴維森', 'Randall Thomas Davidson', '坎特伯里', '英格蘭教會', 96, 1903, 1928, '退休', '愛德華七世', '正統', 'Canterbury records; longest-serving modern Archbishop'),
('科斯莫·戈登·朗格', 'Cosmo Gordon Lang', '坎特伯里', '英格蘭教會', 97, 1928, 1942, '退休', '喬治五世', '正統', 'Canterbury records; Edward VIII abdication'),
('威廉·坦普爾', 'William Temple', '坎特伯里', '英格蘭教會', 98, 1942, 1944, '逝世', '喬治六世', '正統', 'Canterbury records; Christianity and Social Order; ecumenism'),
('傑弗里·費雪', 'Geoffrey Fisher', '坎特伯里', '英格蘭教會', 99, 1945, 1961, '退休', '喬治六世', '正統', 'Canterbury records; first Archbishop to visit Rome since 1397'),
('阿瑟·邁克爾·拉姆齊', 'Arthur Michael Ramsey', '坎特伯里', '英格蘭教會', 100, 1961, 1974, '退休', '伊麗莎白二世', '正統', 'Canterbury records; met Pope Paul VI 1966'),
('弗雷德里克·唐納德·科根', 'Frederick Donald Coggan', '坎特伯里', '英格蘭教會', 101, 1974, 1980, '退休', '伊麗莎白二世', '正統', 'Canterbury records'),
('羅伯特·朗西', 'Robert Runcie', '坎特伯里', '英格蘭教會', 102, 1980, 1991, '退休', '伊麗莎白二世', '正統', 'Canterbury records; Falklands War sermon; women ordination debate'),
('喬治·卡里', 'George Carey', '坎特伯里', '英格蘭教會', 103, 1991, 2002, '退休', '伊麗莎白二世', '正統', 'Canterbury records; women''s ordination approved 1992'),
('羅文·威廉斯', 'Rowan Williams', '坎特伯里', '英格蘭教會', 104, 2002, 2012, '退休', '伊麗莎白二世', '正統', 'Canterbury records; first Welsh Archbishop; Sharia controversy'),
('賈斯廷·韋爾比', 'Justin Welby', '坎特伯里', '英格蘭教會', 105, 2013, 2023, '退休', '伊麗莎白二世', '正統', 'Canterbury records; resigned over handling of abuse cases'),
('史蒂芬·科特雷爾', 'Stephen Cottrell', '坎特伯里', '英格蘭教會', 106, 2025, NULL, NULL, '英格蘭國王查理三世', '正統', 'Canterbury records; translated from York');

-- 設定 predecessor_id 鏈
UPDATE episcopal_succession es
SET predecessor_id = prev.id
FROM (
  SELECT id,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id,
    succession_number
  FROM episcopal_succession
  WHERE see = '坎特伯里'
) prev
WHERE es.id = prev.id AND prev.prev_id IS NOT NULL;

-- 修正跨 church 邊界（Warham → Cranmer）
UPDATE episcopal_succession
SET predecessor_id = (SELECT id FROM episcopal_succession WHERE see='坎特伯里' AND church='天主教' AND succession_number=68)
WHERE see='坎特伯里' AND church='英格蘭教會' AND succession_number=69;

-- Roger Walden rival_of Arundel
UPDATE episcopal_succession
SET rival_of = (SELECT id FROM episcopal_succession WHERE see='坎特伯里' AND church='天主教' AND succession_number=60)
WHERE see='坎特伯里' AND church='天主教' AND succession_number=61 AND name_en='Roger Walden';
