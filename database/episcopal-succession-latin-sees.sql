-- ============================================================
-- 天主教主要大主教座傳承：托萊多、米蘭、阿馬、西敏寺
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources) VALUES

-- ==============================
-- 托萊多（西班牙首席大主教座）
-- ==============================
('聖尤金一世', 'Eugenius I of Toledo', '托萊多', '天主教', 1, 56, 90, '殉道', '使徒傳統', '正統', 'Toledo archdiocese tradition'),
('聖帕特洛克盧斯', 'Patroklus of Toledo', '托萊多', '天主教', 2, 90, 125, '逝世', '坎特伯里前身', '正統', 'Toledo records'),
('桑克圖斯·塞昆杜斯', 'Sanctus Secundus', '托萊多', '天主教', 3, 400, 420, '逝世', '西班牙教會', '正統', 'Toledo records'),
('阿斯圖里烏斯', 'Asturius of Toledo', '托萊多', '天主教', 4, 400, 430, '逝世', '西班牙教會', '正統', 'Toledo records'),
('托萊多的聖伊爾德豐索', 'Ildefonsus of Toledo', '托萊多', '天主教', 9, 657, 667, '逝世', '西班牙教會', '正統', 'Toledo records; De virginitate Mariae'),
('托萊多的聖朱利安', 'Julian of Toledo', '托萊多', '天主教', 13, 680, 690, '逝世', '西班牙教會', '正統', 'Toledo records; Prognosticum futuri saeculi'),
('費利克斯', 'Felix of Toledo', '托萊多', '天主教', 15, 693, 700, '逝世', '西班牙教會', '正統', 'Toledo records'),
('維斯塔拉', 'Wistremiro', '托萊多', '天主教', 16, 700, 710, '逝世（穆斯林征服前）', '西班牙教會', '正統', 'Toledo records; Arab conquest 711'),
('卡西姆·伊本·哈立德（艾哈邁德）', 'Casim ibn Khalid (Mozarab)', '托萊多', '天主教', 17, 796, 826, '逝世', '阿拔斯哈里發允許', '正統', 'Toledo records; Mozarabic period'),
('雷蒙多·德拉薩瓦', 'Raymond of Toledo', '托萊多', '天主教', 28, 1125, 1152, '逝世', '教宗霍諾里烏斯二世', '正統', 'Toledo records; School of Toledo translators'),
('胡安·德卡斯蒂利亞', 'Rodrigo Jiménez de Rada', '托萊多', '天主教', 33, 1209, 1247, '逝世', '教宗英諾森三世', '正統', 'Toledo records; Historia de rebus Hispaniae'),
('岡薩洛·佩雷斯·克達科', 'Gonzalo Pérez Gudiel', '托萊多', '天主教', 39, 1280, 1299, '逝世', '教宗尼古拉三世', '正統', 'Toledo records'),
('佩德羅·德盧納（本篤十三世）', 'Pedro de Luna (Benedict XIII)', '托萊多', '天主教', 43, 1403, 1408, '轉任教廷', '亞維農教宗', '爭議', 'Toledo records; Western Schism antipope'),
('阿方索·德卡里利亞', 'Alonso Carrillo de Acuña', '托萊多', '天主教', 48, 1446, 1482, '逝世', '教宗尼古拉五世', '正統', 'Toledo records; supported Isabella I'),
('弗朗西斯科·希門尼斯·德錫斯內羅斯', 'Francisco Jiménez de Cisneros', '托萊多', '天主教', 51, 1495, 1517, '逝世', '教宗亞歷山大六世', '正統', 'Toledo records; Complutensian Polyglot Bible; Inquisitor'),
('胡安·德塔韋拉', 'Juan de Tavera', '托萊多', '天主教', 53, 1534, 1545, '逝世', '教宗保羅三世', '正統', 'Toledo records'),
('胡安·馬丁內斯·西利塞奧', 'Juan Martínez Silíceo', '托萊多', '天主教', 54, 1546, 1557, '逝世', '教宗保羅三世', '正統', 'Toledo records; limpieza de sangre statutes'),
('費爾南多·德瓦爾德斯', 'Fernando de Valdés', '托萊多', '天主教', 55, 1559, 1568, '逝世', '教宗庇護四世', '正統', 'Toledo records; Inquisitor General'),
('加斯帕·德基羅加', 'Gaspar de Quiroga', '托萊多', '天主教', 56, 1577, 1594, '逝世', '教宗額我略十三世', '正統', 'Toledo records; Inquisitor General; Cardinal'),
('貝爾納多·桑多瓦爾', 'Bernardo de Sandoval y Rojas', '托萊多', '天主教', 57, 1599, 1618, '逝世', '教宗克萊孟八世', '正統', 'Toledo records; patron of Cervantes'),
('加斯帕爾·德博爾哈-伊-維拉拉戈薩', 'Gaspar de Borja y Velasco', '托萊多', '天主教', 60, 1645, 1645, '逝世（任內）', '菲利普四世', '正統', 'Toledo records'),
('巴爾塔薩爾·莫斯科索', 'Baltasar Moscoso y Sandoval', '托萊多', '天主教', 61, 1646, 1665, '逝世', '菲利普四世', '正統', 'Toledo records'),
('路易斯·費爾南多·波爾圖卡雷羅', 'Luis Fernández de Portocarrero', '托萊多', '天主教', 63, 1677, 1709, '逝世', '卡洛斯二世', '正統', 'Toledo records; supported Philip V; Cardinal'),
('佩德羅·德阿斯坎吉斯', 'Pedro de Ascanio Colonna', '托萊多', '天主教', 65, 1720, 1724, '逝世', '菲利普五世', '正統', 'Toledo records'),
('弗朗西斯科·安東尼奧·德羅倫薩納', 'Francisco Antonio de Lorenzana', '托萊多', '天主教', 71, 1772, 1800, '退休', '教宗庇護六世', '正統', 'Toledo records; opposed French Revolution; Cardinal'),
('路易斯·德波旁', 'Luis de Borbón y Vallabriga', '托萊多', '天主教', 72, 1800, 1823, '逝世', '教宗庇護七世', '正統', 'Toledo records; Cardinal; Infante of Spain'),
('胡安·何塞·博內爾', 'Juan José Bonel y Orbe', '托萊多', '天主教', 77, 1847, 1857, '逝世', '教宗庇護九世', '正統', 'Toledo records'),
('弗朗西斯科·德保拉·比達爾', 'Francisco de Paula Benavides', '托萊多', '天主教', 82, 1884, 1895, '逝世', '教宗利奧十三世', '正統', 'Toledo records'),
('恩里克·雷格·卡薩諾瓦', 'Enrique Reig Casanova', '托萊多', '天主教', 87, 1920, 1927, '逝世', '教宗本篤十五世', '正統', 'Toledo records; Cardinal'),
('伊西德羅·貢薩洛', 'Isidro Gomá y Tomás', '托萊多', '天主教', 88, 1933, 1940, '逝世', '教宗庇護十一世', '正統', 'Toledo records; Civil War; Cardinal'),
('恩里克·普拉', 'Enrique Pla y Deniel', '托萊多', '天主教', 89, 1941, 1968, '逝世', '教宗庇護十二世', '正統', 'Toledo records; Cardinal'),
('瑪策利諾·岡薩雷斯·馬丁', 'Marcelo González Martín', '托萊多', '天主教', 91, 1971, 1995, '退休', '教宗保羅六世', '正統', 'Toledo records; Cardinal'),
('弗朗西斯科·阿爾瓦雷斯·馬丁內斯', 'Francisco Álvarez Martínez', '托萊多', '天主教', 92, 1995, 2002, '退休', '教宗若望保祿二世', '正統', 'Toledo records; Cardinal'),
('安東尼奧·卡尼薩雷斯·略韋拉', 'Antonio Cañizares Llovera', '托萊多', '天主教', 93, 2002, 2008, '轉任聖禮部', '教宗若望保祿二世', '正統', 'Toledo records; Cardinal'),
('布勞里奧·羅德里格斯', 'Braulio Rodríguez Plaza', '托萊多', '天主教', 94, 2009, 2022, '退休', '教宗本篤十六世', '正統', 'Toledo records'),
('弗朗西斯科·塞羅查韋斯', 'Francisco Cerro Chaves', '托萊多', '天主教', 95, 2022, NULL, NULL, '教宗方濟各', '正統', 'Toledo records'),

-- ==============================
-- 米蘭（安布羅禮大主教座）
-- ==============================
('米蘭的聖阿那多利', 'Anatalone of Milan', '米蘭', '天主教', 1, 50, 90, '殉道', '使徒巴拿巴', '正統', 'Milan archdiocese tradition'),
('米蘭的聖迦由斯', 'Caius of Milan', '米蘭', '天主教', 2, 90, 100, '逝世', '傳教士', '正統', 'Milan records'),
('米蘭的卡斯圖斯', 'Castus of Milan', '米蘭', '天主教', 5, 160, 190, '逝世', '西方教會', '正統', 'Milan records'),
('米蘭的聖迪俄尼修斯', 'Dionysius of Milan', '米蘭', '天主教', 9, 351, 355, '流放（亞流派）', '羅馬教宗', '正統', 'Milan records; exiled at Council of Milan'),
('米蘭的安波羅修', 'Ambrose of Milan', '米蘭', '天主教', 12, 374, 397, '逝世', '米蘭民眾擁立', '正統', 'Ambrose works; creator of Ambrosian rite and chant'),
('西文普利西安', 'Simplicianus', '米蘭', '天主教', 13, 397, 400, '逝世', '安波羅修推薦', '正統', 'Milan records; Augustine mentor'),
('維利', 'Venerius', '米蘭', '天主教', 14, 400, 409, '逝世', '西方教會', '正統', 'Milan records'),
('馬丁', 'Martinus of Milan', '米蘭', '天主教', 15, 409, 423, '逝世', '教宗佐西穆斯', '正統', 'Milan records'),
('卡西安', 'Cassiodorus of Milan', '米蘭', '天主教', 18, 439, 449, '逝世', '教宗', '正統', 'Milan records'),
('米蘭的歐塞比烏斯', 'Eusebius of Milan', '米蘭', '天主教', 19, 449, 462, '逝世', '教宗', '正統', 'Milan records'),
('勞倫修斯', 'Laurentius of Milan', '米蘭', '天主教', 22, 490, 512, '逝世', '奧多亞克爾時期', '正統', 'Milan records'),
('達提烏斯', 'Datius of Milan', '米蘭', '天主教', 27, 530, 552, '逝世（流亡中）', '教宗維吉利烏斯', '正統', 'Milan records; fled to Constantinople from Goths'),
('馬南修斯', 'Mansuetus of Milan', '米蘭', '天主教', 35, 672, 681, '逝世', '教宗阿加頓', '正統', 'Milan records; Council of Constantinople III'),
('安塞爾姆·德拉佩爾塔', 'Anselm Puster', '米蘭', '天主教', 57, 1097, 1101, '逝世', '教宗烏爾班二世', '正統', 'Milan records'),
('米蘭的羅貝爾托', 'Roberto of Milan', '米蘭', '天主教', 65, 1185, 1186, '逝世', '教宗烏爾班三世', '正統', 'Milan records'),
('奧托內·維斯孔蒂', 'Ottone Visconti', '米蘭', '天主教', 75, 1262, 1295, '逝世', '教宗烏爾班四世', '正統', 'Milan records; Visconti dynasty founder'),
('喬凡尼·維斯孔蒂', 'Giovanni Visconti', '米蘭', '天主教', 83, 1342, 1354, '逝世', '教宗', '正統', 'Milan records; also Lord of Milan'),
('卡洛·博羅梅奧', 'Charles Borromeo', '米蘭', '天主教', 94, 1560, 1584, '逝世', '教宗庇護四世（其舅父）', '正統', 'Milan records; canonized 1610; Tridentine reform model'),
('費德里科·博羅梅奧', 'Federico Borromeo', '米蘭', '天主教', 96, 1595, 1631, '逝世', '教宗克萊孟八世', '正統', 'Milan records; Biblioteca Ambrosiana; cousin of Charles'),
('切薩雷·莫羅佐尼', 'Cesare Monti', '米蘭', '天主教', 97, 1632, 1650, '逝世', '教宗烏爾班八世', '正統', 'Milan records'),
('阿方索·利塔', 'Alfonso Litta', '米蘭', '天主教', 98, 1652, 1679, '逝世', '教宗英諾森十世', '正統', 'Milan records; Cardinal'),
('費德里科·比薩羅', 'Federico Visconti', '米蘭', '天主教', 101, 1681, 1693, '逝世', '教宗英諾森十一世', '正統', 'Milan records'),
('卡爾洛·加埃塔諾·斯坦帕', 'Carlo Gaetano Stampa', '米蘭', '天主教', 103, 1737, 1742, '逝世', '教宗克萊孟十二世', '正統', 'Milan records'),
('普斯泰拉', 'Pozzobonelli', '米蘭', '天主教', 104, 1743, 1783, '逝世', '教宗本篤十四世', '正統', 'Milan records'),
('菲利波·马利亚·威斯孔蒂', 'Filippo Maria Visconti', '米蘭', '天主教', 105, 1783, 1801, '逝世', '教宗庇護六世', '正統', 'Milan records'),
('卡洛·卡耶坦·加伊薩盧克', 'Carlo Gaetano Gaisruck', '米蘭', '天主教', 106, 1818, 1846, '逝世', '教宗庇護七世', '正統', 'Milan records; Habsburg era'),
('卡爾洛·巴托羅梅奧·比爾蒂', 'Karl Kajetan von Gaisruck', '米蘭', '天主教', 106, 1818, 1846, '逝世', '教宗庇護七世', '正統', 'Milan records'),
('安德烈亞·費拉里', 'Andrea Ferrari', '米蘭', '天主教', 108, 1894, 1921, '逝世', '教宗利奧十三世', '正統', 'Milan records; beatified 1987; Cardinal'),
('阿爾法略', 'Alfredo Ildefonso Schuster', '米蘭', '天主教', 109, 1929, 1954, '逝世', '教宗庇護十一世', '正統', 'Milan records; beatified 1996; Benedictine'),
('喬凡尼·巴蒂斯塔·蒙蒂尼', 'Giovanni Battista Montini', '米蘭', '天主教', 110, 1954, 1963, '轉任教宗', '教宗庇護十二世', '正統', 'Milan records; became Pope Paul VI'),
('喬凡尼·科隆博', 'Giovanni Colombo', '米蘭', '天主教', 111, 1963, 1979, '退休', '教宗保羅六世', '正統', 'Milan records; Cardinal'),
('卡洛·瑪麗亞·馬蒂尼', 'Carlo Maria Martini', '米蘭', '天主教', 112, 1980, 2002, '退休', '教宗若望保祿二世', '正統', 'Milan records; Cardinal; Biblical scholar; Jesuit'),
('迪奧尼吉·泰塔馬齊', 'Dionigi Tettamanzi', '米蘭', '天主教', 113, 2002, 2011, '退休', '教宗若望保祿二世', '正統', 'Milan records; Cardinal'),
('安傑洛·斯科拉', 'Angelo Scola', '米蘭', '天主教', 114, 2011, 2017, '退休', '教宗本篤十六世', '正統', 'Milan records; Cardinal; papal candidate'),
('馬里奧·德爾皮尼', 'Mario Delpini', '米蘭', '天主教', 115, 2017, NULL, NULL, '教宗方濟各', '正統', 'Milan records'),

-- ==============================
-- 阿馬（愛爾蘭天主教首席大主教）
-- ==============================
('聖派翠克', 'Saint Patrick', '阿馬', '天主教', 1, 445, 461, '逝世', '聖日耳馬努斯及羅馬', '正統', 'Book of Armagh; patron saint of Ireland'),
('聖比尼烏斯', 'Benignus', '阿馬', '天主教', 2, 461, 467, '逝世', '派翠克指定', '正統', 'Armagh records'),
('西里尼烏斯', 'Jarlath of Armagh', '阿馬', '天主教', 3, 467, 481, '逝世', '愛爾蘭教會', '正統', 'Armagh records'),
('帕特里克·奧斯卡利', 'Cellach mac Áedo', '阿馬', '天主教', 26, 1105, 1129, '逝世', '愛爾蘭教會', '正統', 'Armagh records; Synod of Rathbreasail 1111'),
('馬拉基', 'Malachy (Máel Máedóc)', '阿馬', '天主教', 27, 1132, 1137, '辭職', '教宗英諾森二世', '正統', 'Armagh records; canonized 1190; brought Cistercians to Ireland'),
('喬治·多德', 'Gelasius', '阿馬', '天主教', 29, 1137, 1174, '逝世', '愛爾蘭教會', '正統', 'Armagh records; Synod of Kells 1152'),
('尤金三世·瑪格麗希', 'Eugenius III Mac Giolla Bhrighde', '阿馬', '天主教', 32, 1202, 1216, '逝世', '教宗英諾森三世', '正統', 'Armagh records'),
('奧利弗·普朗克特', 'Oliver Plunkett', '阿馬', '天主教', 62, 1669, 1681, '殉道', '教宗克萊孟九世', '正統', 'Armagh records; canonized 1975; martyred in England'),
('丹尼爾·特羅伊', 'Daniel Troy', '阿馬', '天主教', 75, 1784, 1839, '逝世', '教宗庇護六世', '正統', 'Armagh records'),
('威廉·施爾', 'William Crolly', '阿馬', '天主教', 77, 1835, 1849, '逝世', '教宗額我略十六世', '正統', 'Armagh records'),
('保羅·庫倫', 'Paul Cullen', '阿馬', '天主教', 78, 1850, 1852, '轉任都柏林', '教宗庇護九世', '正統', 'Armagh records; first Irish Cardinal'),
('約瑟夫·麥凱利', 'Joseph Dixon', '阿馬', '天主教', 79, 1852, 1866, '逝世', '教宗庇護九世', '正統', 'Armagh records'),
('麥克哈爾', 'Daniel McGettigan', '阿馬', '天主教', 82, 1870, 1887, '逝世', '教宗庇護九世', '正統', 'Armagh records; First Vatican Council'),
('邁克爾·洛格', 'Michael Logue', '阿馬', '天主教', 86, 1887, 1924, '逝世', '教宗利奧十三世', '正統', 'Armagh records; Cardinal; Irish independence era'),
('丹尼爾·曼尼克斯', 'Patrick O''Donnell', '阿馬', '天主教', 87, 1924, 1927, '逝世', '教宗庇護十一世', '正統', 'Armagh records; Cardinal'),
('約瑟夫·麥羅里', 'Joseph MacRory', '阿馬', '天主教', 88, 1928, 1945, '逝世', '教宗庇護十一世', '正統', 'Armagh records; Cardinal'),
('約翰·達西', 'John D''Alton', '阿馬', '天主教', 89, 1946, 1963, '逝世', '教宗庇護十二世', '正統', 'Armagh records; Cardinal'),
('威廉·康威', 'William Conway', '阿馬', '天主教', 90, 1963, 1977, '逝世', '教宗若望二十三世', '正統', 'Armagh records; Cardinal; Vatican II'),
('托馬斯·奧菲奇', 'Tomás Ó Fiaich', '阿馬', '天主教', 91, 1977, 1990, '逝世', '教宗保羅六世', '正統', 'Armagh records; Cardinal; Hunger Strikes era'),
('卡哈爾·戴利', 'Cahal Daly', '阿馬', '天主教', 92, 1990, 1996, '退休', '教宗若望保祿二世', '正統', 'Armagh records; Cardinal; peace process'),
('肖恩·布雷迪', 'Seán Brady', '阿馬', '天主教', 93, 1996, 2014, '退休', '教宗若望保祿二世', '正統', 'Armagh records; Cardinal'),
('埃蒙·馬丁', 'Eamon Martin', '阿馬', '天主教', 94, 2014, NULL, NULL, '教宗方濟各', '正統', 'Armagh records'),

-- ==============================
-- 西敏寺（現代英格蘭天主教）
-- ==============================
('尼古拉斯·懷斯曼', 'Nicholas Wiseman', '西敏寺', '天主教', 1, 1850, 1865, '逝世', '教宗庇護九世', '正統', 'Westminster records; restored English Catholic hierarchy; Cardinal'),
('亨利·曼寧', 'Henry Manning', '西敏寺', '天主教', 2, 1865, 1892, '逝世', '教宗庇護九世', '正統', 'Westminster records; Cardinal; social justice'),
('赫伯特·沃恩', 'Herbert Vaughan', '西敏寺', '天主教', 3, 1892, 1903, '逝世', '教宗利奧十三世', '正統', 'Westminster records; Cardinal; Westminster Cathedral'),
('弗朗西斯·博爾尼', 'Francis Bourne', '西敏寺', '天主教', 4, 1903, 1935, '逝世', '教宗利奧十三世', '正統', 'Westminster records; Cardinal'),
('阿瑟·辛斯利', 'Arthur Hinsley', '西敏寺', '天主教', 5, 1935, 1943, '逝世', '教宗庇護十一世', '正統', 'Westminster records; Cardinal; WWII broadcast'),
('伯納德·格里芬', 'Bernard Griffin', '西敏寺', '天主教', 6, 1943, 1956, '逝世', '教宗庇護十二世', '正統', 'Westminster records; Cardinal'),
('威廉·戈弗里', 'William Godfrey', '西敏寺', '天主教', 7, 1956, 1963, '逝世', '教宗庇護十二世', '正統', 'Westminster records; Cardinal'),
('約翰·卡奇', 'John Carmel Heenan', '西敏寺', '天主教', 8, 1963, 1975, '逝世', '教宗若望二十三世', '正統', 'Westminster records; Cardinal; Vatican II'),
('巴茲爾·休姆', 'Basil Hume', '西敏寺', '天主教', 9, 1976, 1999, '逝世', '教宗保羅六世', '正統', 'Westminster records; Cardinal; Benedictine; beatification cause open'),
('科馬克·墨菲-歐康納', 'Cormac Murphy-O''Connor', '西敏寺', '天主教', 10, 2000, 2009, '退休', '教宗若望保祿二世', '正統', 'Westminster records; Cardinal'),
('文森特·尼科爾斯', 'Vincent Nichols', '西敏寺', '天主教', 11, 2009, NULL, NULL, '教宗本篤十六世', '正統', 'Westminster records; Cardinal');

-- 設定 predecessor_id（各 see 內連鏈）
UPDATE episcopal_succession es
SET predecessor_id = prev.id
FROM (
  SELECT id,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see IN ('托萊多', '米蘭', '阿馬', '西敏寺')
) prev
WHERE es.id = prev.id AND prev.prev_id IS NOT NULL;
