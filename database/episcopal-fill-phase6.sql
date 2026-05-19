-- ========================================================
-- Phase 6: Anglican (英格蘭/海外) + Lutheran 重要缺漏教座
-- ========================================================
-- 英格蘭 Reformers/重要古主教座:
--   倫敦 (Ridley, Tillotson)、達勒姆 (Tunstall, Cosin)、溫徹斯特 (Beaufort, Andrewes)、
--   索爾茲伯里 (Jewel)、烏斯特 (Latimer)、林肯 (Grosseteste)、伊利 (Andrewes)、
--   羅徹斯特 (Fisher)、聖大衛 (Welsh)、巴斯與韋爾斯
-- 海外: 拉各斯 (奈及利亞次)、新加坡、馬達加斯加聖公宗
-- 北歐 Lutheran: 格但斯克、塔爾圖、索菲亞
-- ========================================================

-- Parent see IDs:
--   坎特伯里 英格蘭教會 : c99c3115-5955-465e-a795-0b90f344fdd2
--   坎特伯里 天主教     : 562ca8af-9ad2-430e-bd00-f8fad4e90bbb
--   羅馬                : 3ed0e61a-fae8-4c80-a9b5-2b319caf2faf
--   特里爾              : 572c1134-c9d3-44bb-a70b-ba714acdc8a7


-- =============================================
-- 英格蘭聖公會重要古主教座（Reformers + 重要古教座）
-- =============================================

-- 倫敦 (London) — 597 立座，僅次坎特伯里、約克；Ridley 殉道
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('倫敦主教座（英格蘭教會）', 'Diocese of London', '倫敦', '英格蘭教會', '基督新教', '英國國教禮', 314, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '英格蘭古老主教座，僅次於坎特伯里、約克；314 年阿爾勒會議與會者可考為首；1555 Reformer Nicholas Ridley 殉道；今聖保羅大教堂為駐節地。', 'Acts and Monuments (Foxe); Stubbs, Registrum Sacrum');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('雷斯提圖圖斯', 'Restitutus of London', '倫敦', '英格蘭教會', 1, 314, 320, '正統', 'Mansi II;《阿爾勒會議文獻》', '314 阿爾勒會議與會者；可考最早倫敦主教'),
('梅利圖斯', 'Mellitus of London', '倫敦', '英格蘭教會', 2, 604, 619, '正統', '比德《英吉利教會史》II.3', '額我略大教宗派遣團員之一'),
('尼古拉斯·李德利', 'Nicholas Ridley', '倫敦', '英格蘭教會', 3, 1550, 1553, '廢黜後復位', 'Foxe, Acts and Monuments', '1553 瑪麗一世登基後廢黜；1555 與 Latimer 一同在牛津被火刑殉道；改革派代表'),
('愛德蒙·邦納', 'Edmund Bonner', '倫敦', '英格蘭教會', 4, 1553, 1559, '對立', 'Foxe, Acts and Monuments', '瑪麗一世時代天主教反改革派；伊麗莎白即位後拒簽至上條例被廢黜'),
('愛德蒙·格林達爾', 'Edmund Grindal', '倫敦', '英格蘭教會', 5, 1559, 1570, '正統', 'Strype, Life of Grindal', '後升坎特伯里總主教；伊麗莎白早期改革派'),
('約翰·提利森', 'John Tillotson', '倫敦', '英格蘭教會', 6, 1691, 1694, '正統', 'Birch, Life of Tillotson', '光榮革命後第一任坎特伯里總主教 (1691-1694)；倫敦時期亦掛此職'),
('查爾斯·詹姆斯·布隆菲爾德', 'Charles James Blomfield', '倫敦', '英格蘭教會', 7, 1828, 1856, '正統', 'Crockford', '19 世紀牛津運動時期；倫敦教會建設關鍵人物'),
('薩拉·穆拉莉', 'Sarah Mullally', '倫敦', '英格蘭教會', 8, 2018, NULL, '正統', 'Church of England press releases', '首位倫敦女主教；前護理長官；現任');


-- 達勒姆 (Durham) — Prince-Bishop，宗教改革重要
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('達勒姆主教座', 'Diocese of Durham', '達勒姆', '英格蘭教會', '基督新教', '英國國教禮', 995, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '995 立座，繼承 林迪斯法恩 (Lindisfarne) 古老主教座；中世紀達勒姆主教是 Prince-Bishop（具世俗王權）；改革時期 Tunstall、Cosin 是重要神學家。', 'Symeon of Durham');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('阿爾德海爾姆', 'Aldhun of Durham', '達勒姆', '英格蘭教會', 1, 995, 1018, '正統', 'Symeon of Durham', '首任達勒姆主教；將聖卡斯伯特遺骨移至此'),
('威廉·迪·聖卡萊', 'William of Saint-Calais', '達勒姆', '英格蘭教會', 2, 1080, 1096, '正統', 'Symeon of Durham', '征服者威廉時期；建造達勒姆大教堂'),
('卡斯伯特·圖恩斯托', 'Cuthbert Tunstall', '達勒姆', '英格蘭教會', 3, 1530, 1559, '廢黜後復位', 'Sturge, Cuthbert Tunstall', '改革時期重要溫和派；瑪麗一世時復位、伊麗莎白即位後拒簽至上條例被廢黜'),
('約翰·寇辛', 'John Cosin', '達勒姆', '英格蘭教會', 4, 1660, 1672, '正統', 'Cosin《Devotions》', '王政復辟後高教會派 (High Church) 重要神學家；著《公禱書》改編；劍橋大學三一堂院長'),
('約瑟夫·萊特富特', 'Joseph Lightfoot', '達勒姆', '英格蘭教會', 5, 1879, 1889, '正統', 'Westcott, Joseph Lightfoot', '新約聖經學者；發現 1 Clement 拉丁譯本；建立 Durham School 的學術品牌'),
('保羅·巴特勒', 'Paul Butler', '達勒姆', '英格蘭教會', 6, 2014, NULL, '正統', 'Church of England', '現任');


-- 溫徹斯特 (Winchester) — 古老富有教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('溫徹斯特主教座', 'Diocese of Winchester', '溫徹斯特', '英格蘭教會', '基督新教', '英國國教禮', 660, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '660 立座，韋塞克斯王國古老主教座；中世紀為英格蘭最富有教座之一；蘭斯洛特·安德魯斯主教是「欽定本聖經」翻譯主要負責人。', 'Anglo-Saxon Chronicle');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('溫弗里德', 'Wine of Winchester', '溫徹斯特', '英格蘭教會', 1, 660, 670, '正統', '比德《英吉利教會史》III.7', '韋塞克斯王 Cenwalh 任命首任主教'),
('斯威斯恩', 'Swithun of Winchester', '溫徹斯特', '英格蘭教會', 2, 852, 863, '正統', 'Aelfric, Lives of Saints', '聖斯威斯恩；雨節主保聖人'),
('亨利·博福特', 'Henry Beaufort', '溫徹斯特', '英格蘭教會', 3, 1404, 1447, '正統', 'Crockford', '岡特約翰之子；玫瑰戰爭時期樞機；1431 主持 Joan of Arc 審判'),
('斯蒂芬·加德納', 'Stephen Gardiner', '溫徹斯特', '英格蘭教會', 4, 1531, 1555, '對立', 'Foxe, Acts and Monuments', '亨利八世早期改革派、瑪麗一世時代反改革派代表；著《On True Obedience》'),
('蘭斯洛特·安德魯斯', 'Lancelot Andrewes', '溫徹斯特', '英格蘭教會', 5, 1619, 1626, '正統', 'Andrewes,《Preces Privatae》', '英國國教聖人；「欽定本」聖經翻譯主譯之一；高教會派神學家；《Lectures on the Catechism》'),
('湯瑪斯·肯', 'Thomas Ken', '溫徹斯特', '英格蘭教會', 6, 1685, 1691, '正統', 'Plumptre, Thomas Ken', '《晨歌》《晚歌》《讚美三一頌》(Doxology) 作者；不宣誓派 (Non-Juror) 之首');


-- 索爾茲伯里 (Salisbury) — John Jewel 護教
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('索爾茲伯里主教座', 'Diocese of Salisbury', '索爾茲伯里', '英格蘭教會', '基督新教', '英國國教禮', 1075, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '1075 立座（前身為 Sherborne）；中世紀「Sarum Use」禮典發源地；改革時期 John Jewel 著《英格蘭教會的辯護》是英國國教神學立論名作。', 'Sarum Customary');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('赫爾曼', 'Hermann of Salisbury', '索爾茲伯里', '英格蘭教會', 1, 1075, 1078, '正統', 'Stubbs, Registrum Sacrum', '征服者威廉任命；首任 Old Sarum 主教'),
('奧斯蒙德', 'Osmund of Salisbury', '索爾茲伯里', '英格蘭教會', 2, 1078, 1099, '正統', 'Salisbury Cathedral Records', '聖人；建立 Sarum 禮典；其禮典後傳遍英格蘭及部分歐陸'),
('約翰·杰維爾', 'John Jewel', '索爾茲伯里', '英格蘭教會', 3, 1560, 1571, '正統', 'Jewel, Apologia Ecclesiae Anglicanae', '伊麗莎白時代護教神學家；著《Apologia Ecclesiae Anglicanae》是英國國教立論基石；其挑戰天主教論者公開徵答事件 (Challenge Sermon) 著稱'),
('吉爾伯特·伯內特', 'Gilbert Burnet', '索爾茲伯里', '英格蘭教會', 4, 1689, 1715, '正統', 'Burnet, History of My Own Time', '光榮革命後重要改革派；著《英格蘭宗教改革史》《當代史》');


-- 烏斯特 (Worcester) — Hugh Latimer 殉道
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('烏斯特主教座', 'Diocese of Worcester', '烏斯特', '英格蘭教會', '基督新教', '英國國教禮', 680, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '680 立座，麥西亞王國古老主教座；中世紀重要學術中心；改革時期 Hugh Latimer 主教是「劍橋三聖人」之一、1555 在牛津殉道。', 'Bede, Hist. eccl. IV.23');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('博塞爾', 'Bosel of Worcester', '烏斯特', '英格蘭教會', 1, 680, 691, '正統', '比德《英吉利教會史》IV.23', '麥西亞王國首任 Hwicce 主教'),
('伍夫斯坦', 'Wulfstan of Worcester', '烏斯特', '英格蘭教會', 2, 1062, 1095, '正統', 'William of Malmesbury, Vita Wulfstani', '征服前後過渡時期；唯一保留主教位的盎格魯-撒克遜主教；後封聖'),
('休·拉提莫', 'Hugh Latimer', '烏斯特', '英格蘭教會', 3, 1535, 1539, '正統', 'Foxe, Acts and Monuments', '改革派；著名講道者；1539 因拒絕六條法案辭職；1555 在牛津殉道時對 Ridley 言：「今日我們將點燃如此燭火，在英格蘭上空，靠上主恩典，永不熄滅」'),
('愛德華·斯托克斯利', 'Edward Stokesley', '烏斯特', '英格蘭教會', 4, 1539, 1543, '對立', 'Foxe, Acts and Monuments', '反改革派；拉提莫之繼任');


-- 林肯 (Lincoln) — Grosseteste, Whichcote
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('林肯主教座', 'Diocese of Lincoln', '林肯', '英格蘭教會', '基督新教', '英國國教禮', 1072, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '1072 立座（前身為 Dorchester）；中世紀英格蘭最大主教座，範圍從亨伯河至泰晤士河；羅伯特·格羅斯泰斯特主教是中世紀著名科學家+亞里斯多德學者。', 'Anglo-Saxon Chronicle');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('雷米吉烏斯·迪·非堪普', 'Remigius of Lincoln', '林肯', '英格蘭教會', 1, 1072, 1092, '正統', 'Stubbs, Registrum Sacrum', '征服後首任林肯主教'),
('羅伯特·格羅斯泰斯特', 'Robert Grosseteste', '林肯', '英格蘭教會', 2, 1235, 1253, '正統', 'Grosseteste,《De Luce》《Hexaemeron》', '中世紀學者+神學家+科學家；亞里斯多德《後分析論》《尼各馬可倫理學》拉丁譯者；牛津大學首任校監；對中世紀光學、宇宙論影響深遠'),
('威廉·華勒姆', 'William Wake', '林肯', '英格蘭教會', 3, 1705, 1716, '正統', 'Sykes, William Wake', '後升坎特伯里總主教 1716-1737；高教會派代表');


-- 伊利 (Ely) — 神祕家 Andrewes
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('伊利主教座', 'Diocese of Ely', '伊利', '英格蘭教會', '基督新教', '英國國教禮', 1109, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '1109 從林肯分出；劍橋大學所在主教座；蘭斯洛特·安德魯斯任職 1609-1619；「劍橋柏拉圖學派」相關。', 'Liber Eliensis');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('赫維', 'Hervey le Breton', '伊利', '英格蘭教會', 1, 1109, 1131, '正統', 'Liber Eliensis', '首任伊利主教'),
('蘭斯洛特·安德魯斯', 'Lancelot Andrewes', '伊利', '英格蘭教會', 2, 1609, 1619, '正統', 'Andrewes,《Preces Privatae》', '伊利主教時期，後升溫徹斯特；「欽定本」聖經翻譯主譯之一'),
('馬修·雷恩', 'Matthew Wren', '伊利', '英格蘭教會', 3, 1638, 1667, '正統', 'Crockford', '高教會派；英國革命時被囚塔內 18 年；著《Increpatio Bar-Iesu》');


-- 羅徹斯特 (Rochester) — John Fisher 殉道
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('羅徹斯特主教座', 'Diocese of Rochester', '羅徹斯特', '英格蘭教會', '基督新教', '英國國教禮', 604, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '604 立座，英格蘭第二古老（僅次坎特伯里）；改革時期約翰·費舍爾主教因拒絕承認亨利八世為英國教會最高首領而 1535 殉道。', '比德《英吉利教會史》II.3');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('優士都', 'Justus of Rochester', '羅徹斯特', '英格蘭教會', 1, 604, 624, '正統', '比德《英吉利教會史》II.3', '額我略大教宗派遣團員之一；首任羅徹斯特主教'),
('約翰·費舍爾', 'John Fisher', '羅徹斯特', '英格蘭教會', 2, 1504, 1535, '對立', 'Reynolds, John Fisher', '反改革派；劍橋大學校監；拒絕承認亨利八世為英國教會最高首領；1535 砍頭殉道；1935 封聖 (天主教)；著《七篇懺悔詩篇講道》'),
('尼古拉斯·希思', 'Nicholas Heath', '羅徹斯特', '英格蘭教會', 3, 1539, 1543, '正統', 'Foxe, Acts and Monuments', null);


-- 聖大衛 (St Davids) — 威爾士主保
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('聖大衛主教座', 'Diocese of St Davids', '聖大衛', '英格蘭教會', '基督新教', '英國國教禮', 519, 1533, '現存', 'c99c3115-5955-465e-a795-0b90f344fdd2',
 '6 世紀威爾士主保聖大衛 (Dewi Sant) 建立；中世紀威爾士最高主教座；2020 起加入威爾士聖公會 (Disestablished 1920)。', 'Rhigyfarch, Vita Davidis');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('聖大衛', 'Saint David (Dewi Sant)', '聖大衛', '英格蘭教會', 1, 519, 589, '正統', 'Rhigyfarch, Vita Davidis', '威爾士主保聖人；建立修道院傳統；3 月 1 日聖大衛節'),
('威廉·勞德', 'William Laud', '聖大衛', '英格蘭教會', 2, 1621, 1626, '正統', 'Trevor-Roper, Archbishop Laud', '後升坎特伯里總主教 1633-1645；英國革命中處決'),
('丹尼爾·詹姆斯', 'Daniel James', '聖大衛', '英格蘭教會', 3, 1908, 1923, '正統', 'Crockford', '1920 威爾士國教解體前的最後一任 Established 主教');


-- =============================================
-- 海外聖公宗 sub-diocese (重要 archdiocesan)
-- =============================================

-- 拉各斯 (Lagos) — 奈及利亞聖公宗首座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('拉各斯總教區（聖公宗）', 'Anglican Diocese of Lagos', '拉各斯（聖公宗）', '奈及利亞聖公宗', '基督新教', '英國國教禮', 1864, '現存', NULL,
 '1864 立座；西非聖公宗最重要主教座；後成 奈及利亞聖公宗（Church of Nigeria）核心；現為非洲最大聖公宗教會。', 'Church of Nigeria archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('塞繆爾·阿賈伊·克勞瑟', 'Samuel Ajayi Crowther', '拉各斯（聖公宗）', '奈及利亞聖公宗', 1, 1864, 1891, '正統', 'Walls, The Cross-Cultural Process', '前奴隸出身；第一位非洲裔聖公宗主教；尼日河差會總監督；獻身於翻譯約魯巴語聖經'),
('赫伯特·圖格威爾', 'Herbert Tugwell', '拉各斯（聖公宗）', '奈及利亞聖公宗', 2, 1894, 1921, '正統', 'Church Missionary Society archives', null),
('阿德庫米·奧庫塞德', 'Adelakun Okusode', '拉各斯（聖公宗）', '奈及利亞聖公宗', 3, 1991, 1999, '正統', 'Church of Nigeria archives', '20 世紀末擴張時期');


-- 新加坡聖公宗
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('新加坡主教座（聖公宗）', 'Anglican Diocese of Singapore', '新加坡（聖公宗）', '東南亞聖公宗', '基督新教', '英國國教禮', 1909, '現存', NULL,
 '1909 立座；東南亞聖公宗 (Province of South East Asia) 母教區；近年強烈福音派立場、與全球南方聖公宗結盟，反對自由派 ACNA-aligned。', 'Diocese of Singapore archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('查爾斯·詹姆斯·費里斯', 'Charles James Ferris', '新加坡（聖公宗）', '東南亞聖公宗', 1, 1909, 1927, '正統', 'Diocese of Singapore', '首任新加坡主教'),
('莫澤斯·泰', 'Moses Tay', '新加坡（聖公宗）', '東南亞聖公宗', 2, 1982, 2000, '正統', 'Diocese of Singapore', '東南亞聖公宗首任大主教 1996-2000；福音派改革派'),
('蘇進忠', 'John Chew Hiang Chea', '新加坡（聖公宗）', '東南亞聖公宗', 3, 2000, 2012, '正統', 'Diocese of Singapore', '東南亞大主教 2006-2012；全球南方聖公宗主要召集人'),
('Rennis Ponniah', 'Rennis Ponniah', '新加坡（聖公宗）', '東南亞聖公宗', 4, 2012, 2020, '正統', 'Diocese of Singapore', null),
('Titus Chung', 'Titus Chung', '新加坡（聖公宗）', '東南亞聖公宗', 5, 2020, NULL, '正統', 'Diocese of Singapore', '現任');


-- =============================================
-- 北歐 Lutheran 重要古主教座
-- =============================================

-- 格但斯克 (Gdańsk) — 波蘭信義會
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('格但斯克信義會監督座', 'Lutheran Bishopric of Gdańsk', '格但斯克', '波蘭信義會', '基督新教', '路德禮', 1557, 1557, '已廢除', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '1557 西吉斯蒙德·奧古斯特宣告自治後在格但斯克立信義會監督；1817 與 1945 後逐步消失。', '波蘭信義會檔案');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('彭加奇·阿曼杜斯', 'Pancratius Klemme', '格但斯克', '波蘭信義會', 1, 1557, 1573, '正統', '波蘭信義會檔案', '格但斯克第一任 Lutheran 監督'),
('丹尼爾·貝克爾', 'Daniel Becker', '格但斯克', '波蘭信義會', 2, 1660, 1685, '正統', '波蘭信義會檔案', null),
('卡爾·吉爾根松', 'Karl Jürgensohn', '格但斯克', '波蘭信義會', 3, 1900, 1939, '正統', '波蘭信義會檔案', '末任 Lutheran 監督；二戰後此職位實際消失');


-- 塔爾圖 (Tartu) — 愛沙尼亞古老主教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, split_year, status, parent_see_id, notes, sources) VALUES
('塔爾圖主教座', 'Diocese of Tartu (Dorpat)', '塔爾圖', '愛沙尼亞信義會', '基督新教', '路德禮', 1224, 1531, '已廢除', '3ed0e61a-fae8-4c80-a9b5-2b319caf2faf',
 '1224 條頓騎士團征服後立；13-16 世紀為立窩尼亞重要主教城；1558 利窩尼亞戰爭中遭俄軍洗劫；1582 後成 Lutheran 監督；1710 大北方戰爭後廢除。', '《Heinrich的立窩尼亞編年史》');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('赫爾曼·迪·普魯士', 'Hermann of Buxhövden', '塔爾圖', '愛沙尼亞信義會', 1, 1224, 1248, '正統', 'Heinrici Chronicon Livoniae', '首任塔爾圖主教（中世紀天主教）'),
('約翰·貝爾', 'Johannes Bell', '塔爾圖', '愛沙尼亞信義會', 2, 1571, 1584, '正統', '愛沙尼亞信義會檔案', '宗教改革後首任 Lutheran 監督');
