-- ============================================================
-- 天主教大主教座補充——歐洲各國主要大主教座
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, abolished_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

-- 法國
('里昂大主教座',
 'Archdiocese of Lyon',
 '里昂', '天主教', '天主教', '羅馬禮', 177, NULL, '現存',
 '大主教奧利維耶·德傑爾梅', 'Archbishop Olivier de Germay', 2021, '法國里昂',
 '177年由愛任紐的前任波提努斯殉道；里昂為高盧教會中心，大主教稱「高盧和納爾邦首席大主教（Primat des Gaules）」。',
 'Catholic Church records; Lyon archdiocese'),

('盧昂大主教座',
 'Archdiocese of Rouen',
 '盧昂', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教多米尼克·勒布倫', 'Archbishop Dominique Lebrun', 2015, '法國盧昂',
 '諾曼第教省首席大主教；聖貞德1431年在此受審並被處死。',
 'Catholic Church records; Rouen archdiocese'),

('波爾多大主教座',
 'Archdiocese of Bordeaux',
 '波爾多', '天主教', '天主教', '羅馬禮', 314, NULL, '現存',
 '大主教讓-保羅·詹姆斯', 'Archbishop Jean-Paul James', 2019, '法國波爾多',
 '阿基坦教省首席大主教。', 'Catholic Church records; Bordeaux archdiocese'),

('圖盧茲大主教座',
 'Archdiocese of Toulouse',
 '圖盧茲', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教克里斯托弗·德克羅', 'Archbishop Christophe de Dreuille', 2024, '法國圖盧茲',
 '朗格多克地區中心；阿爾比十字軍歷史所在地。', 'Catholic Church records; Toulouse archdiocese'),

('都爾大主教座',
 'Archdiocese of Tours',
 '都爾', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教文森特·拉比', 'Archbishop Vincent Labie', 2022, '法國都爾',
 '聖馬爾定（Martin of Tours）在此建立重要主教座；盧瓦爾地區首席大主教。',
 'Catholic Church records; Tours archdiocese'),

('桑斯大主教座',
 'Archdiocese of Sens-Auxerre',
 '桑斯', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教亨利·阿克塔博', 'Archbishop Henri Haguet', 2019, '法國桑斯',
 '中世紀全法地位僅次於蘭斯的大主教座，托馬斯·貝克特曾居此流亡。',
 'Catholic Church records; Sens archdiocese'),

-- 德國
('特里爾大主教座',
 'Archdiocese of Trier',
 '特里爾', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教斯特凡·阿克特貝爾格', 'Archbishop Stephan Ackermann', 2009, '德國特里爾',
 '西歐最古老的主教座之一，傳由使徒馬提亞建立；神聖羅馬帝國選帝侯之一（大主教-選帝侯）；保存有基督的長袍（Holy Robe）聖物。',
 'Catholic Church records; Trier archdiocese'),

('薩爾斯堡大主教座',
 'Archdiocese of Salzburg',
 '薩爾斯堡', '天主教', '天主教', '羅馬禮', 696, NULL, '現存',
 '大主教弗朗茨·拉克納', 'Archbishop Franz Lackner', 2013, '奧地利薩爾斯堡',
 '696年聖儒佩特建立；德語區最古老主教座之一，大主教稱「德意志首席大主教（Primas Germaniae）」；莫札特出生地。',
 'Catholic Church records; Salzburg archdiocese'),

('維也納大主教座',
 'Archdiocese of Vienna',
 '維也納', '天主教', '天主教', '羅馬禮', 1469, NULL, '現存',
 '大主教克里斯托弗·尚邦', 'Archbishop Christoph Schönborn', 1995, '奧地利維也納',
 '1469年腓特烈三世將帕紹主教座分拆設立；1722年升為大主教座；哈布斯堡帝國首都教省。',
 'Catholic Church records; Vienna archdiocese'),

('弗賴堡大主教座',
 'Archdiocese of Freiburg',
 '弗賴堡', '天主教', '天主教', '羅馬禮', 1821, NULL, '現存',
 '大主教斯特凡·布格', 'Archbishop Stephan Burger', 2013, '德國弗賴堡',
 '1821年拿破崙政教協議後重組教省設立。', 'Catholic Church records; Freiburg archdiocese'),

('慕尼黑-弗萊辛大主教座',
 'Archdiocese of Munich and Freising',
 '慕尼黑', '天主教', '天主教', '羅馬禮', 739, NULL, '現存',
 '大主教萊因哈德·馬克思', 'Archbishop Reinhard Marx', 2008, '德國慕尼黑',
 '739年聖博尼法斯建立弗萊辛主教座；1818年升為大主教座並納入慕尼黑；若望保祿二世前任樞機拉青格（本篤十六世）曾任此職1977–1982。',
 'Catholic Church records; Munich archdiocese'),

('柏林大主教座',
 'Archdiocese of Berlin',
 '柏林', '天主教', '天主教', '羅馬禮', 1929, NULL, '現存',
 '大主教海納·科赫', 'Archbishop Heiner Koch', 2015, '德國柏林',
 '1929年設大主教座；跨越東西德分裂時期。', 'Catholic Church records; Berlin archdiocese'),

('帕德博恩大主教座',
 'Archdiocese of Paderborn',
 '帕德博恩', '天主教', '天主教', '羅馬禮', 795, NULL, '現存',
 '大主教漢斯-約瑟夫·貝克爾', 'Archbishop Hans-Josef Becker', 2003, '德國帕德博恩',
 '795年查理曼大帝設立；德國歷史最久的主教座之一。', 'Catholic Church records; Paderborn archdiocese'),

-- 波蘭
('格涅茲諾大主教座',
 'Archdiocese of Gniezno',
 '格涅茲諾', '天主教', '天主教', '羅馬禮', 1000, NULL, '現存',
 '大主教沃伊切赫·波拉克', 'Archbishop Wojciech Polak', 2014, '波蘭格涅茲諾',
 '1000年奧托三世皇帝訪問格涅茲諾，教宗西爾韋斯特二世同意建立大主教座。波蘭天主教首席大主教（Primate of Poland）。',
 'Catholic Church records; Gniezno archdiocese'),

('華沙大主教座',
 'Archdiocese of Warsaw',
 '華沙', '天主教', '天主教', '羅馬禮', 1798, NULL, '現存',
 '大主教卡齊米日·尼奇', 'Archbishop Kazimierz Nycz', 2007, '波蘭華沙',
 '1798年設主教座；1818年升為大主教座；1992年成為大主教省首席。',
 'Catholic Church records; Warsaw archdiocese'),

('克拉科夫大主教座',
 'Archdiocese of Kraków',
 '克拉科夫', '天主教', '天主教', '羅馬禮', 1000, NULL, '現存',
 '大主教馬雷克·延德拉謝夫斯基', 'Archbishop Marek Jędraszewski', 2017, '波蘭克拉科夫',
 '波蘭歷史古都；若望保祿二世（卡羅爾·沃伊提瓦）1964–1978年任此職。',
 'Catholic Church records; Kraków archdiocese'),

('弗羅茨瓦夫大主教座',
 'Archdiocese of Wrocław',
 '弗羅茨瓦夫', '天主教', '天主教', '羅馬禮', 1000, NULL, '現存',
 '大主教約瑟夫·格金布拉滕維爾特', 'Archbishop Josef Kupny', 2013, '波蘭弗羅茨瓦夫',
 '1000年建立（原為布雷斯勞，德文 Breslau）；二戰後劃入波蘭；1930年升為大主教座。',
 'Catholic Church records; Wrocław archdiocese'),

('波茲南大主教座',
 'Archdiocese of Poznań',
 '波茲南', '天主教', '天主教', '羅馬禮', 968, NULL, '現存',
 '大主教史坦尼斯拉夫·甘德克', 'Archbishop Stanisław Gądecki', 2002, '波蘭波茲南',
 '968年皮亞斯特王朝時期建立，波蘭最早的主教座；1821年升為大主教座。',
 'Catholic Church records; Poznań archdiocese'),

-- 匈牙利
('埃斯泰爾根-布達佩斯大主教座',
 'Archdiocese of Esztergom-Budapest',
 '埃斯泰爾根', '天主教', '天主教', '羅馬禮', 1001, NULL, '現存',
 '大主教彼得·厄爾道', 'Archbishop Péter Erdő', 2002, '匈牙利埃斯泰爾根/布達佩斯',
 '1001年教宗西爾韋斯特二世授予斯蒂芬一世（聖斯蒂芬王）王冠，同時建立大主教座；匈牙利天主教首席大主教（Primate of Hungary）；1993年與布達佩斯合併。',
 'Catholic Church records; Esztergom archdiocese'),

('卡洛察-科奇大主教座',
 'Archdiocese of Kalocsa-Kecskemét',
 '卡洛察', '天主教', '天主教', '羅馬禮', 1000, NULL, '現存',
 '大主教喬治·薩諾', 'Archbishop György Udvardy', 2020, '匈牙利卡洛察',
 '匈牙利第二大主教座；1009年由斯蒂芬一世設立。', 'Catholic Church records; Kalocsa archdiocese'),

('埃格爾大主教座',
 'Archdiocese of Eger',
 '埃格爾', '天主教', '天主教', '羅馬禮', 1004, NULL, '現存',
 '大主教安德拉斯·沃雷斯', 'Archbishop András Veres', 2018, '匈牙利埃格爾',
 '1004年聖斯蒂芬王設立；1804年升為大主教座。', 'Catholic Church records; Eger archdiocese'),

-- 捷克
('布拉格大主教座',
 'Archdiocese of Prague',
 '布拉格', '天主教', '天主教', '羅馬禮', 973, NULL, '現存',
 '大主教揚·格勞布納', 'Archbishop Jan Graubner', 2022, '捷克布拉格',
 '973年設主教座；1344年查理四世向教宗克萊孟六世爭取升為大主教座，由巴黎的厄恩斯特出任首任大主教；胡斯運動、反宗教改革激烈地區。',
 'Catholic Church records; Prague archdiocese'),

('奧洛穆茨大主教座',
 'Archdiocese of Olomouc',
 '奧洛穆茨', '天主教', '天主教', '羅馬禮', 1063, NULL, '現存',
 '大主教揚·格羅赫', 'Archbishop Jan Graubner', 2019, '捷克奧洛穆茨',
 '摩拉維亞地區首席大主教座；1063年設主教座；1777年升為大主教座。',
 'Catholic Church records; Olomouc archdiocese'),

-- 奧地利
('格拉茨-塞考大主教座',
 'Diocese of Graz-Seckau (formerly Archdiocese)',
 '格拉茨', '天主教', '天主教', '羅馬禮', 1218, NULL, '現存',
 '大主教威廉·科雷', 'Archbishop Wilhelm Krautwaschl', 2015, '奧地利格拉茨',
 '1218年設塞考主教座；1963年遷格拉茨；為奧地利南方重要教區。',
 'Catholic Church records; Graz archdiocese'),

-- 葡萄牙
('布拉加大主教座',
 'Archdiocese of Braga',
 '布拉加', '天主教', '天主教', '羅馬禮', 45, NULL, '現存',
 '大主教若澤·科爾代羅', 'Archbishop José Cordeiro', 2021, '葡萄牙布拉加',
 '傳統由聖保羅門徒建立；葡萄牙最古老大主教座，葡萄牙天主教首席大主教（Primate of the Spains/Portugal），西班牙教會分立前全伊比利亞半島首席。',
 'Catholic Church records; Braga archdiocese'),

('里斯本大主教座',
 'Patriarchate of Lisbon',
 '里斯本', '天主教', '天主教', '羅馬禮', 1393, NULL, '現存',
 '大主教儒伊·瓦萊里歐', 'Archbishop Rui Valério', 2023, '葡萄牙里斯本',
 '1393年升為大主教座；1716年獲賜宗主教座尊稱（Patriarchate of Lisbon）；地理大發現時代葡萄牙教會中心。',
 'Catholic Church records; Lisbon patriarchate'),

('埃武拉大主教座',
 'Archdiocese of Évora',
 '埃武拉', '天主教', '天主教', '羅馬禮', 1540, NULL, '現存',
 '大主教謝薩爾·羅昂-科拉考', 'Archbishop José Alves', 2020, '葡萄牙埃武拉',
 '1540年設主教座；1570年升為大主教座；阿連特茹地區中心。',
 'Catholic Church records; Évora archdiocese'),

-- 西班牙（補充）
('塔拉戈納大主教座',
 'Archdiocese of Tarragona',
 '塔拉戈納', '天主教', '天主教', '羅馬禮', 67, NULL, '現存',
 '大主教若昂·普拉納斯', 'Archbishop Joan Planellas', 2021, '西班牙塔拉戈納',
 '傳由使徒保羅門徒建立；歷史上西班牙最古老大主教座，一度凌駕托萊多；加泰羅尼亞首席大主教座。',
 'Catholic Church records; Tarragona archdiocese'),

('塞維利亞大主教座',
 'Archdiocese of Seville',
 '塞維利亞', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教何塞·安赫爾·薩伊斯-梅內塞斯', 'Archbishop José Ángel Saiz Meneses', 2022, '西班牙塞維利亞',
 '250年設主教座；西哥德王國重要中心；大主教稱「印度群島首席大主教（Primate of the Indies）」，因大航海時代地位。伊西多爾（Isidore of Seville）在此服事。',
 'Catholic Church records; Seville archdiocese'),

('聖地亞哥-德孔波斯特拉大主教座',
 'Archdiocese of Santiago de Compostela',
 '聖地亞哥-德孔波斯特拉', '天主教', '天主教', '羅馬禮', 830, NULL, '現存',
 '大主教弗朗西斯科·普列托·費爾南德斯', 'Archbishop Francisco Prieto Fernández', 2023, '西班牙聖地亞哥',
 '830年代（可能更早）發現使徒雅各之墓，此後成為基督教三大聖地之一；1120年升為大主教座；聖雅各朝聖路（Camino de Santiago）終點。',
 'Catholic Church records; Santiago archdiocese'),

('薩拉戈薩大主教座',
 'Archdiocese of Zaragoza',
 '薩拉戈薩', '天主教', '天主教', '羅馬禮', 592, NULL, '現存',
 '大主教卡洛斯·曼薩納雷斯·烏爾巴諾', 'Archbishop Carlos Manzanares', 2023, '西班牙薩拉戈薩',
 '亞拉岡地區首席大主教座；建有聖母柱聖殿（Basílica del Pilar）。',
 'Catholic Church records; Zaragoza archdiocese'),

('巴塞羅那大主教座',
 'Archdiocese of Barcelona',
 '巴塞羅那', '天主教', '天主教', '羅馬禮', 343, NULL, '現存',
 '大主教胡安·何塞·奧梅利亞', 'Archbishop Juan José Omella', 2015, '西班牙巴塞羅那',
 '343年設主教座；2004年升為大主教座；加泰羅尼亞最大城市。',
 'Catholic Church records; Barcelona archdiocese'),

('瓦倫西亞大主教座',
 'Archdiocese of Valencia',
 '瓦倫西亞', '天主教', '天主教', '羅馬禮', 304, NULL, '現存',
 '大主教恩里克·博特萊爾-吉塔特', 'Archbishop Enrique Benavent', 2023, '西班牙瓦倫西亞',
 '304年殉道主教聖文森特；1492年首次施洗美洲原住民的塔拉韋拉（Hernando de Talavera）在此任職。',
 'Catholic Church records; Valencia archdiocese'),

('布爾戈斯大主教座',
 'Archdiocese of Burgos',
 '布爾戈斯', '天主教', '天主教', '羅馬禮', 1068, NULL, '現存',
 '大主教馬里奧·伊坎迪', 'Archbishop Mario Iceta', 2020, '西班牙布爾戈斯',
 '卡斯提爾首席大主教座；埃爾西德故鄉；朝聖之路重要站點。',
 'Catholic Church records; Burgos archdiocese'),

('格拉納達大主教座',
 'Archdiocese of Granada',
 '格拉納達', '天主教', '天主教', '羅馬禮', 1492, NULL, '現存',
 '大主教何塞·普列托', 'Archbishop José Prieto Fernández', 2023, '西班牙格拉納達',
 '1492年天主教雙王收復格拉納達後設立，由費爾南多·德塔拉韋拉出任首任大主教；阿罕布拉宮所在地。',
 'Catholic Church records; Granada archdiocese'),

-- 義大利（補充）
('那不勒斯大主教座',
 'Archdiocese of Naples',
 '那不勒斯', '天主教', '天主教', '羅馬禮', 100, NULL, '現存',
 '大主教多梅尼科·巴塔利亞', 'Archbishop Domenico Battaglia', 2020, '義大利那不勒斯',
 '傳由使徒彼得所立；南義大利最重要的大主教座；聖雅努阿里烏斯（San Gennaro）聖物在此保存。',
 'Catholic Church records; Naples archdiocese'),

('佛羅倫薩大主教座',
 'Archdiocese of Florence',
 '佛羅倫薩', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教朱塞佩·貝托裡', 'Archbishop Giuseppe Betori', 2008, '義大利佛羅倫薩',
 '1419年升為大主教座；美第奇家族贊助中心；1439年東西教會合一大公會議（費拉拉—佛羅倫薩公會議）在此召開。',
 'Catholic Church records; Florence archdiocese'),

('波隆那大主教座',
 'Archdiocese of Bologna',
 '波隆那', '天主教', '天主教', '羅馬禮', 300, NULL, '現存',
 '大主教馬泰奧·祖皮', 'Archbishop Matteo Zuppi', 2015, '義大利波隆那',
 '全球最古老大學（1088年）所在地；1582年升為大主教座；多位教宗曾任此職。',
 'Catholic Church records; Bologna archdiocese'),

('熱那亞大主教座',
 'Archdiocese of Genoa',
 '熱那亞', '天主教', '天主教', '羅馬禮', 300, NULL, '現存',
 '大主教馬爾科·塔斯卡', 'Archbishop Marco Tasca', 2020, '義大利熱那亞',
 '利古里亞地區首席大主教座；1133年升為大主教座；哥倫布故鄉。',
 'Catholic Church records; Genoa archdiocese'),

('都靈大主教座',
 'Archdiocese of Turin',
 '都靈', '天主教', '天主教', '羅馬禮', 398, NULL, '現存',
 '大主教羅貝托·雷波萊', 'Archbishop Roberto Repole', 2022, '義大利都靈',
 '皮埃蒙特地區首席大主教座；著名的都靈裹屍布（Shroud of Turin）保存於此。',
 'Catholic Church records; Turin archdiocese'),

('巴勒摩大主教座',
 'Archdiocese of Palermo',
 '巴勒摩', '天主教', '天主教', '羅馬禮', 254, NULL, '現存',
 '大主教科拉多·洛雷菲切', 'Archbishop Corrado Lorefice', 2015, '義大利巴勒摩',
 '西西里島首席大主教座；254年設主教座；諾曼、拜占庭、阿拉伯文化交融地。',
 'Catholic Church records; Palermo archdiocese'),

('拉文納大主教座',
 'Archdiocese of Ravenna-Cervia',
 '拉文納', '天主教', '天主教', '羅馬禮', 250, NULL, '現存',
 '大主教洛倫佐·尼蘭德', 'Archbishop Lorenzo Ghizzoni', 2019, '義大利拉文納',
 '250年設主教座；西羅馬帝國後期首都；拜占庭帝國義大利總督府（Exarchate）所在；但丁長眠於此。著名的早期基督教馬賽克藝術。',
 'Catholic Church records; Ravenna archdiocese'),

-- 克羅埃西亞
('薩格勒布大主教座',
 'Archdiocese of Zagreb',
 '薩格勒布', '天主教', '天主教', '羅馬禮', 1094, NULL, '現存',
 '大主教達里奧·卡西科', 'Archbishop Dario Kasić', 2024, '克羅埃西亞薩格勒布',
 '1094年拉迪斯勞斯一世設主教座；1852年升為大主教座；克羅埃西亞天主教首席大主教座。',
 'Catholic Church records; Zagreb archdiocese'),

('斯普利特-馬卡爾斯卡大主教座',
 'Archdiocese of Split-Makarska',
 '斯普利特', '天主教', '天主教', '羅馬禮', 640, NULL, '現存',
 '大主教馬里安·亞布拉諾維奇', 'Archbishop Marin Barišić', 2012, '克羅埃西亞斯普利特',
 '640年代設立；戴克里先皇帝宮殿（舊城區）所在地；達爾馬提亞地區首席大主教座。',
 'Catholic Church records; Split archdiocese'),

-- 波士尼亞
('薩拉熱窩大主教座',
 'Archdiocese of Sarajevo',
 '薩拉熱窩', '天主教', '天主教', '羅馬禮', 1881, NULL, '現存',
 '大主教文科·普利吉奇', 'Archbishop Vinko Puljić', 1990, '波士尼亞薩拉熱窩',
 '1881年設大主教座；鄂圖曼帝國後建立；1990年至今由普利吉奇擔任（兼樞機）。',
 'Catholic Church records; Sarajevo archdiocese'),

-- 立陶宛
('維爾紐斯大主教座',
 'Archdiocese of Vilnius',
 '維爾紐斯', '天主教', '天主教', '羅馬禮', 1387, NULL, '現存',
 '大主教根塔拉斯·格魯薩斯', 'Archbishop Gintaras Grušas', 2013, '立陶宛維爾紐斯',
 '1387年立陶宛大公雅蓋沃受洗後設主教座；1991年獨立後恢復自由；立陶宛首席大主教座。',
 'Catholic Church records; Vilnius archdiocese'),

-- 拉脫維亞
('里加大主教座（天主教）',
 'Archdiocese of Riga (Catholic)',
 '里加', '天主教', '天主教', '羅馬禮', 1186, NULL, '現存',
 '大主教斯特布林斯-坦杰爾斯', 'Archbishop Zbignevs Stankevičs', 2010, '拉脫維亞里加',
 '1186年條頓騎士團傳教；1202年升為大主教座；新教化後天主教少數，1921年重設。',
 'Catholic Church records; Riga Catholic archdiocese'),

-- 愛爾蘭（都柏林大主教已在前面，再補德羅摩爾等無需，此處略）

-- 比利時
('梅赫倫-布魯塞爾大主教座',
 'Archdiocese of Mechelen-Brussels',
 '梅赫倫', '天主教', '天主教', '羅馬禮', 1559, NULL, '現存',
 '大主教呂克·托格曼斯', 'Archbishop Luc Terlinden', 2024, '比利時梅赫倫/布魯塞爾',
 '1559年菲利普二世建立比利時天主教教省，梅赫倫為首席大主教座；1961年加入布魯塞爾。',
 'Catholic Church records; Mechelen-Brussels archdiocese'),

-- 荷蘭
('烏特勒支大主教座（天主教）',
 'Archdiocese of Utrecht (Catholic)',
 '烏特勒支', '天主教', '天主教', '羅馬禮', 1853, NULL, '現存',
 '大主教威廉·雅各布斯·德克爾', 'Archbishop Wim Eijk', 2008, '荷蘭烏特勒支',
 '1853年荷蘭天主教教省恢復（1724年老天主教分裂後重建）；荷蘭天主教首席大主教座。',
 'Catholic Church records; Utrecht Catholic archdiocese'),

-- 愛爾蘭（補充新教分裂後的情況已在前面處理）

-- 斯洛伐克
('布拉提斯拉瓦大主教座',
 'Archdiocese of Bratislava',
 '布拉提斯拉瓦', '天主教', '天主教', '羅馬禮', 1977, NULL, '現存',
 '大主教斯坦尼斯拉夫·左科', 'Archbishop Stanislav Zvolenský', 2009, '斯洛伐克布拉提斯拉瓦',
 '1977年設大主教座；斯洛伐克首席大主教座之一。', 'Catholic Church records; Bratislava archdiocese'),

('科希策大主教座',
 'Archdiocese of Košice',
 '科希策', '天主教', '天主教', '羅馬禮', 1804, NULL, '現存',
 '大主教貝爾納德·博維尼亞克', 'Archbishop Bernard Bober', 2011, '斯洛伐克科希策',
 '1804年設主教座；1995年升為大主教座。', 'Catholic Church records; Košice archdiocese'),

-- 俄羅斯（覆蓋範圍有限）
('莫斯科大主教座（天主教）',
 'Archdiocese of the Mother of God in Moscow (Catholic)',
 '莫斯科', '天主教', '天主教', '羅馬禮', 2002, NULL, '現存',
 '大主教保羅·佩扎', 'Archbishop Paolo Pezzi', 2007, '俄羅斯莫斯科',
 '2002年設立，俄羅斯天主教教省首席；規模小，主要為移民及少數信徒服務。',
 'Catholic Church records; Moscow Catholic archdiocese');

-- 設定 parent_see_id（同傳統、歐洲各省見前）
-- 各國首席大主教座關係可根據需要補充
