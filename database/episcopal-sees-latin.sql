-- ============================================================
-- 天主教大主教座、聖公宗各省、信義宗大主教座、老天主教
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, abolished_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

-- I. 英格蘭及愛爾蘭天主教大主教座（中世紀）
('坎特伯里大主教座（中世紀天主教）',
 'Archdiocese of Canterbury (Medieval Catholic)',
 '坎特伯里', '天主教', '天主教', '羅馬禮', 597, 1558, '已廢除',
 NULL, NULL, NULL, '英格蘭坎特伯里',
 '597年教宗額我略一世派奧古斯丁建立，英格蘭天主教首席大主教座（Primate of All England）。1533年宗教改革後改為英格蘭教會，但瑪麗一世在位（1553–1558）短暫恢復。最後一任天主教大主教為雷金納德·波爾（1556–1558）。',
 'Bede, Historia Ecclesiastica; Canterbury Cathedral records'),

('約克大主教座（中世紀天主教）',
 'Archdiocese of York (Medieval Catholic)',
 '約克', '天主教', '天主教', '羅馬禮', 627, 1558, '已廢除',
 NULL, NULL, NULL, '英格蘭約克',
 '627年由坎特伯里的鮑利努斯建立，英格蘭北方首席大主教（Primate of England）。1534年宗教改革。',
 'Bede, Historia Ecclesiastica; York Minster records'),

('阿馬大主教座（天主教）',
 'Archdiocese of Armagh (Catholic)',
 '阿馬', '天主教', '天主教', '羅馬禮', 445, NULL, '現存',
 '大主教埃蒙·馬丁', 'Archbishop Eamon Martin', 2014, '北愛爾蘭阿馬',
 '445年由聖派翠克創立，愛爾蘭天主教首席大主教（Primate of All Ireland）。',
 'Catholic Church records; Armagh archdiocese'),

('都柏林大主教座（天主教）',
 'Archdiocese of Dublin (Catholic)',
 '都柏林', '天主教', '天主教', '羅馬禮', 1028, NULL, '現存',
 '大主教戴爾穆德·馬丁', 'Archbishop Dermot Farrell', 2020, '愛爾蘭都柏林',
 '1028年確立；愛爾蘭天主教第二大主教座。',
 'Catholic Church records; Dublin archdiocese'),

('西敏寺大主教座（天主教）',
 'Archdiocese of Westminster (Catholic)',
 '西敏寺', '天主教', '天主教', '羅馬禮', 1850, NULL, '現存',
 '大主教文森特·尼科爾斯', 'Archbishop Vincent Nichols', 2009, '英格蘭倫敦',
 '1850年教宗庇護九世重建英格蘭及威爾士天主教教省，設西敏寺為首席大主教座。',
 'Catholic Church records; Westminster archdiocese'),

-- II. 歐洲大陸天主教大主教座
('托萊多大主教座',
 'Archdiocese of Toledo',
 '托萊多', '天主教', '天主教', '羅馬禮', 56, NULL, '現存',
 '大主教弗朗西斯科·塞羅查韋斯', 'Archbishop Francisco Cerro Chaves', 2022, '西班牙托萊多',
 '傳統由使徒雅各的門徒建立；西班牙天主教首席大主教座（Primate of Spain）。',
 'Catholic Church records; Toledo archdiocese'),

('米蘭大主教座',
 'Archdiocese of Milan',
 '米蘭', '天主教', '天主教', '安布羅禮', 50, NULL, '現存',
 '大主教馬里奧·德爾皮尼', 'Archbishop Mario Delpini', 2017, '義大利米蘭',
 '傳統由使徒巴拿巴建立；以聖安波羅修（374–397）最著名，使用安布羅禮至今。',
 'Catholic Church records; Milan archdiocese'),

('蘭斯大主教座',
 'Archdiocese of Reims',
 '蘭斯', '天主教', '天主教', '羅馬禮', 260, NULL, '現存',
 '大主教埃里克·德穆萊', 'Archbishop Éric de Moulins-Beaufort', 2018, '法國蘭斯',
 '法國加冕地，歷代法王在此受膏；496年聖雷米為克洛維一世施洗。',
 'Catholic Church records; Reims archdiocese'),

('巴黎大主教座',
 'Archdiocese of Paris',
 '巴黎', '天主教', '天主教', '羅馬禮', 1622, NULL, '現存',
 '大主教洛朗·烏萊里奇', 'Archbishop Laurent Ulrich', 2022, '法國巴黎',
 '1622年升為大主教座；法國最重要的教區之一。',
 'Catholic Church records; Paris archdiocese'),

('科隆大主教座',
 'Archdiocese of Cologne',
 '科隆', '天主教', '天主教', '羅馬禮', 313, NULL, '現存',
 '大主教賴納·沃爾基', 'Archbishop Rainer Woelki', 2014, '德國科隆',
 '313年確立主教座；神聖羅馬帝國時期選帝侯之一（Kurfürst）。',
 'Catholic Church records; Cologne archdiocese'),

('美因茨大主教座',
 'Archdiocese of Mainz',
 '美因茨', '天主教', '天主教', '羅馬禮', 347, NULL, '現存',
 '大主教彼得·科默', 'Archbishop Peter Kohlgraf', 2017, '德國美因茨',
 '中世紀神聖羅馬帝國首席大主教（Primas Germaniae），選帝侯之一。',
 'Catholic Church records; Mainz archdiocese'),

('漢堡大主教座',
 'Archdiocese of Hamburg',
 '漢堡', '天主教', '天主教', '羅馬禮', 831, NULL, '現存',
 '大主教斯特凡·黑塞', 'Archbishop Stefan Heße', 2015, '德國漢堡',
 '831年由聖安斯卡爾（北方使徒）建立，最初為漢堡-不萊梅大主教座，向斯堪地納維亞傳教。',
 'Catholic Church records; Hamburg archdiocese'),

-- III. 英格蘭教會（聖公宗）
('坎特伯里大主教座（英格蘭教會）',
 'See of Canterbury (Church of England)',
 '坎特伯里', '英格蘭教會', '聖公宗', '英格蘭教會禮', 1533, NULL, '現存',
 '大主教史蒂芬·科特雷爾', 'Archbishop Stephen Cottrell', 2025, '英格蘭坎特伯里',
 '1533年英格蘭宗教改革後繼承中世紀大主教座；聖公宗精神領袖，全英格蘭首席主教（Primate of All England）。',
 'Church of England records; Lambeth Palace archives'),

('約克大主教座（英格蘭教會）',
 'See of York (Church of England)',
 '約克', '英格蘭教會', '聖公宗', '英格蘭教會禮', 1534, NULL, '現存',
 NULL, NULL, NULL, '英格蘭約克',
 '英格蘭北方首席主教（Primate of England）；史蒂芬·科特雷爾2025年移任坎特伯里後現位出缺。',
 'Church of England records; York Minster archives'),

-- IV. 愛爾蘭教會（聖公宗）
('阿馬大主教座（愛爾蘭教會）',
 'Archdiocese of Armagh (Church of Ireland)',
 '阿馬', '愛爾蘭教會', '聖公宗', '英格蘭教會禮', 1536, NULL, '現存',
 '大主教約翰·麥克道爾', 'Archbishop John McDowell', 2020, '北愛爾蘭阿馬',
 '愛爾蘭教會首席大主教（Primate of All Ireland）。',
 'Church of Ireland records'),

('都柏林大主教座（愛爾蘭教會）',
 'Archdiocese of Dublin and Glendalough (Church of Ireland)',
 '都柏林', '愛爾蘭教會', '聖公宗', '英格蘭教會禮', 1536, NULL, '現存',
 '大主教麥可·傑克遜', 'Archbishop Michael Jackson', 2011, '愛爾蘭都柏林',
 '愛爾蘭教會第二大主教座。',
 'Church of Ireland records'),

-- V. 英倫三島其他聖公宗
('威爾士教會大主教座',
 'Church in Wales — Archbishop',
 '威爾士', '威爾士教會', '聖公宗', '英格蘭教會禮', 1920, NULL, '現存',
 '大主教安德魯·約翰', 'Archbishop Andrew John', 2023, '威爾士',
 '1920年威爾士教會從英格蘭教會分立（disestablishment）；大主教由現任六位主教互選。',
 'Church in Wales records'),

('蘇格蘭聖公會主教長',
 'Scottish Episcopal Church — Primus',
 '蘇格蘭聖公會', '蘇格蘭聖公會', '聖公宗', '英格蘭教會禮', 1689, NULL, '現存',
 '主教長馬克·斯特蘭奇', 'Primus Mark Strange', 2017, '蘇格蘭',
 '1689年威廉三世確立蘇格蘭長老會後，聖公宗主教在蘇格蘭成為非國教；主教長（Primus）由主教互選，非固定教座。',
 'Scottish Episcopal Church records'),

-- VI. 聖公宗各省——非洲
('奈及利亞聖公宗大主教座',
 'Church of Nigeria (Anglican Communion) — Archbishop',
 '奈及利亞聖公宗', '奈及利亞聖公宗', '聖公宗', '英格蘭教會禮', 1979, NULL, '現存',
 '大主教亨利·恩杜庫巴', 'Archbishop Henry Ndukuba', 2019, '奈及利亞阿布加',
 '全球最大聖公宗教會，信徒逾2000萬。1979年獨立為自治省。',
 'Anglican Communion records'),

('烏干達聖公宗大主教座',
 'Church of Uganda — Archbishop',
 '烏干達聖公宗', '烏干達聖公宗', '聖公宗', '英格蘭教會禮', 1961, NULL, '現存',
 '大主教史蒂芬·卡齊姆巴', 'Archbishop Stephen Kaziimba', 2020, '烏干達坎帕拉',
 '1961年成為自治省。',
 'Anglican Communion records'),

('肯亞聖公宗大主教座',
 'Anglican Church of Kenya — Archbishop',
 '肯亞聖公宗', '肯亞聖公宗', '聖公宗', '英格蘭教會禮', 1970, NULL, '現存',
 '大主教傑克遜·奧萊·薩皮特', 'Archbishop Jackson Ole Sapit', 2016, '肯亞奈洛比',
 '1970年成為自治省。',
 'Anglican Communion records'),

('南非聖公宗大主教座',
 'Anglican Church of Southern Africa — Archbishop',
 '南非聖公宗', '南非聖公宗', '聖公宗', '英格蘭教會禮', 1853, NULL, '現存',
 '大主教塔博·馬克戈巴', 'Archbishop Thabo Makgoba', 2008, '南非開普敦',
 '含南非、波札那、萊索托、馬拉威、莫三比克及納米比亞。',
 'Anglican Communion records'),

('坦尚尼亞聖公宗大主教座',
 'Anglican Church of Tanzania — Archbishop',
 '坦尚尼亞聖公宗', '坦尚尼亞聖公宗', '聖公宗', '英格蘭教會禮', 1970, NULL, '現存',
 '大主教馬印博·姆恩多爾瓦', 'Archbishop Maimbo Mndolwa', 2017, '坦尚尼亞達累斯薩拉姆',
 '1970年成為自治省。', 'Anglican Communion records'),

('西非聖公宗省大主教座',
 'Church of the Province of West Africa — Archbishop',
 '西非聖公宗', '西非聖公宗', '聖公宗', '英格蘭教會禮', 1951, NULL, '現存',
 '大主教西里爾·班-史密斯', 'Archbishop Cyril Ben-Smith', 2019, '迦納阿克拉',
 '含迦納、奈及利亞部分地區（已獨立）、幾內亞、賴比瑞亞、塞拉利昂、甘比亞等。',
 'Anglican Communion records'),

('中非聖公宗省大主教座',
 'Church of the Province of Central Africa — Archbishop',
 '中非聖公宗', '中非聖公宗', '聖公宗', '英格蘭教會禮', 1955, NULL, '現存',
 '大主教艾伯特·查馬', 'Archbishop Albert Chama', 2011, '尚比亞盧薩卡',
 '含波札那、辛巴威、馬拉威、尚比亞。',
 'Anglican Communion records'),

('盧安達聖公宗大主教座',
 'Anglican Church of Rwanda — Archbishop',
 '盧安達聖公宗', '盧安達聖公宗', '聖公宗', '英格蘭教會禮', 1992, NULL, '現存',
 '大主教洛朗·姆班達', 'Archbishop Laurent Mbanda', 2018, '盧安達基加利',
 '1992年成為自治省。',
 'Anglican Communion records'),

('南蘇丹聖公宗大主教座',
 'Episcopal Church of South Sudan — Archbishop',
 '南蘇丹聖公宗', '南蘇丹聖公宗', '聖公宗', '英格蘭教會禮', 2017, NULL, '現存',
 '大主教賈斯廷·巴迪', 'Archbishop Justin Badi', 2021, '南蘇丹朱巴',
 '2017年從蘇丹聖公宗分立；南蘇丹獨立後成立。',
 'Anglican Communion records'),

('蘇丹聖公宗大主教座',
 'Episcopal Church of Sudan — Archbishop',
 '蘇丹聖公宗', '蘇丹聖公宗', '聖公宗', '英格蘭教會禮', 1976, NULL, '現存',
 '大主教以西結·庫米爾·孔多', 'Archbishop Ezekiel Kumir Kondo', 2021, '蘇丹喀土穆',
 '1976年成為自治省；2017年南蘇丹分立後重組。',
 'Anglican Communion records'),

('蒲隆地聖公宗大主教座',
 'Anglican Church of Burundi — Archbishop',
 '蒲隆地聖公宗', '蒲隆地聖公宗', '聖公宗', '英格蘭教會禮', 1992, NULL, '現存',
 '大主教馬丁·布萊斯·尼亞博霍', 'Archbishop Martin Blaise Nyaboho', 2013, '蒲隆地布松布拉',
 '1992年成為自治省。', 'Anglican Communion records'),

('亞歷山卓聖公宗省大主教座',
 'Church of the Province of Alexandria — Archbishop',
 '亞歷山卓聖公宗', '亞歷山卓聖公宗', '聖公宗', '英格蘭教會禮', 1976, NULL, '現存',
 '大主教薩米·法烏齊', 'Archbishop Samy Fawzy', 2017, '埃及開羅',
 '含埃及、北非、衣索比亞（部分）、厄利垂亞（部分）聖公宗信徒。',
 'Anglican Communion records'),

('印度洋省聖公宗大主教座',
 'Church of the Province of the Indian Ocean — Archbishop',
 '印度洋聖公宗', '印度洋聖公宗', '聖公宗', '英格蘭教會禮', 1973, NULL, '現存',
 NULL, NULL, NULL, '馬達加斯加安塔那那利佛',
 '含馬達加斯加、模里西斯、塞席爾。', 'Anglican Communion records'),

-- VII. 聖公宗各省——美洲及加勒比海
('美國聖公會首牧教座',
 'The Episcopal Church — Presiding Bishop',
 '美國聖公會', '美國聖公會', '聖公宗', '英格蘭教會禮', 1789, NULL, '現存',
 '首牧主教肖恩·羅', 'Presiding Bishop Sean Rowe', 2024, '美國紐約',
 '1789年美國獨立後脫離英格蘭教會；首牧主教由三年一次的全國大會選出。',
 'TEC records; General Convention'),

('加拿大聖公宗大主教座',
 'Anglican Church of Canada — Primate',
 '加拿大聖公宗', '加拿大聖公宗', '聖公宗', '英格蘭教會禮', 1893, NULL, '現存',
 '首席大主教克里斯多夫·哈珀', 'Primate Christopher Harper', 2023, '加拿大多倫多',
 '1893年成立加拿大大主教省；首席主教由教省大會選出。',
 'Anglican Church of Canada records'),

('西印度群島聖公宗大主教座',
 'Church in the Province of the West Indies — Archbishop',
 '西印度群島聖公宗', '西印度群島聖公宗', '聖公宗', '英格蘭教會禮', 1883, NULL, '現存',
 '大主教霍華德·格雷戈里', 'Archbishop Howard Gregory', 2017, '牙買加京斯敦',
 '含加勒比海地區各英語國家。', 'Anglican Communion records'),

('巴西聖公宗大主教座',
 'Episcopal Anglican Church of Brazil — Primate',
 '巴西聖公宗', '巴西聖公宗', '聖公宗', '英格蘭教會禮', 1965, NULL, '現存',
 '首席主教馬里內斯·巴索托', 'Primate Marinez Bassotto', 2020, '巴西聖保羅',
 '1965年成為自治省。', 'Anglican Communion records'),

('墨西哥聖公宗大主教座',
 'Anglican Church of Mexico — Primate',
 '墨西哥聖公宗', '墨西哥聖公宗', '聖公宗', '英格蘭教會禮', 1995, NULL, '現存',
 '首席主教弗朗西斯科·莫雷諾', 'Primate Francisco Moreno', 2012, '墨西哥墨西哥城',
 '1995年成為自治省。', 'Anglican Communion records'),

('南美南錐聖公宗大主教座',
 'Anglican Church of South America (Southern Cone) — Primate',
 '南美南錐聖公宗', '南錐聖公宗', '聖公宗', '英格蘭教會禮', 1981, NULL, '現存',
 '首席主教布萊恩·威廉斯', 'Primate Brian Williams', 2019, '阿根廷布宜諾斯艾利斯',
 '含阿根廷、玻利維亞、智利、秘魯、烏拉圭、巴拉圭。1981年成為自治省。',
 'Anglican Communion records'),

('古巴聖公宗（直屬）',
 'Episcopal Church of Cuba — Bishop',
 '古巴聖公宗', '古巴聖公宗', '聖公宗', '英格蘭教會禮', 1967, NULL, '現存',
 '主教格里塞爾達·德爾加多', 'Bishop Griselda Delgado del Carpio', 2019, '古巴哈瓦那',
 '直屬坎特伯里大主教，非完整自治省。', 'Anglican Communion records'),

-- VIII. 聖公宗各省——亞太
('韓國聖公宗大主教座',
 'Anglican Church of Korea — Primate',
 '韓國聖公宗', '韓國聖公宗', '聖公宗', '英格蘭教會禮', 1965, NULL, '現存',
 '首席主教歐尼西姆·朴', 'Primate Onesimus Dongsin Park', 2022, '韓國首爾',
 '1965年成為自治省。', 'Anglican Communion records'),

('菲律賓聖公宗大主教座',
 'Episcopal Church in the Philippines — Primate',
 '菲律賓聖公宗', '菲律賓聖公宗', '聖公宗', '英格蘭教會禮', 1990, NULL, '現存',
 '首席主教喬爾·帕喬', 'Primate Joel Atiwag Pachao', 2021, '菲律賓馬尼拉',
 '1990年成為自治省。', 'Anglican Communion records'),

('日本聖公會大主教座',
 'Nippon Sei Ko Kai — Primate',
 '日本聖公宗', '日本聖公宗（日本聖公會）', '聖公宗', '英格蘭教會禮', 1887, NULL, '現存',
 '首席主教中村上植馬克托', 'Primate Nathaniel Makoto Uematsu', 2021, '日本東京',
 '1887年傳教會合並成立日本聖公會（NSKK）；1941年自治。', 'Anglican Communion records'),

('香港聖公宗大主教座',
 'Hong Kong Sheng Kung Hui — Archbishop',
 '香港聖公宗', '香港聖公宗', '聖公宗', '英格蘭教會禮', 1998, NULL, '現存',
 '大主教陳謳明', 'Archbishop Andrew Chan', 2021, '香港',
 '1998年成為自治省。', 'Anglican Communion records'),

('東南亞聖公宗省大主教座',
 'Church of the Province of South East Asia — Archbishop',
 '東南亞聖公宗', '東南亞聖公宗', '聖公宗', '英格蘭教會禮', 1996, NULL, '現存',
 '大主教倫尼斯·龐尼亞', 'Archbishop Rennis Ponniah', 2020, '新加坡',
 '含新加坡、馬來西亞、印尼（部分）。1996年成為自治省。', 'Anglican Communion records'),

('巴布亞紐幾內亞聖公宗大主教座',
 'Anglican Church of Papua New Guinea — Archbishop',
 '巴紐聖公宗', '巴紐聖公宗', '聖公宗', '英格蘭教會禮', 1977, NULL, '現存',
 '大主教拿單·赫倫斯基', 'Archbishop Nathan Hronsky', 2021, '巴紐莫爾茲比港',
 '1977年成為自治省。', 'Anglican Communion records'),

('美拉尼西亞聖公宗省大主教座',
 'Church of the Province of Melanesia — Archbishop',
 '美拉尼西亞聖公宗', '美拉尼西亞聖公宗', '聖公宗', '英格蘭教會禮', 1975, NULL, '現存',
 '大主教倫納德·達維亞', 'Archbishop Leonard Dawea', 2022, '索羅門群島荷尼阿拉',
 '含索羅門群島、萬那杜、新喀里多尼亞。1975年成為自治省。', 'Anglican Communion records'),

('紐西蘭及波利尼西亞聖公宗大主教座',
 'Anglican Church in Aotearoa, New Zealand and Polynesia — Archbishop',
 '紐西蘭聖公宗', '紐西蘭聖公宗', '聖公宗', '英格蘭教會禮', 1857, NULL, '現存',
 '大主教菲利普·理查森', 'Archbishop Philip Richardson', 2019, '紐西蘭威靈頓',
 '含紐西蘭、庫克群島、東加、薩摩亞、法屬波利尼西亞。', 'Anglican Communion records'),

('澳洲聖公宗大主教座',
 'Anglican Church of Australia — Primate',
 '澳洲聖公宗', '澳洲聖公宗', '聖公宗', '英格蘭教會禮', 1962, NULL, '現存',
 '首席大主教杰弗里·史密斯', 'Archbishop Geoffrey Smith', 2014, '澳洲阿德雷德',
 '1962年成為自治省；首席主教每三年由大主教互選一人出任。', 'Anglican Communion records'),

-- IX. 聖公宗各省——南亞及中東
('北印度教會大主教座',
 'Church of North India — Moderator',
 '北印度教會', '北印度教會', '聖公宗', '英格蘭教會禮', 1970, NULL, '現存',
 '議長主教帕里托什·坎寧', 'Moderator Paritosh Canning', 2022, '印度德里',
 '1970年由多個新教教會合一成立，含聖公宗、循道宗、長老宗等。', 'Anglican Communion records'),

('南印度教會大主教座',
 'Church of South India — Moderator',
 '南印度教會', '南印度教會', '聖公宗', '英格蘭教會禮', 1947, NULL, '現存',
 '議長主教托馬斯·歐門', 'Moderator Thomas K. Oommen', 2022, '印度清奈',
 '1947年印度獨立後由聖公宗、循道宗、長老宗合一成立，為最早的合一教會之一。', 'Anglican Communion records'),

('巴基斯坦教會大主教座',
 'Church of Pakistan — Bishop of Lahore',
 '巴基斯坦教會', '巴基斯坦教會', '聖公宗', '英格蘭教會禮', 1970, NULL, '現存',
 '主教阿扎德·馬歇爾', 'Bishop Azad Marshall', 2017, '巴基斯坦拉合爾',
 '1970年成立，為聖公宗與其他新教合一教會；首席主教為拉合爾主教。', 'Anglican Communion records'),

('錫蘭教會大主教座',
 'Church of Ceylon — Bishop of Colombo',
 '錫蘭教會', '錫蘭教會', '聖公宗', '英格蘭教會禮', 1845, NULL, '現存',
 '主教杜桑塔·羅德里戈', 'Bishop Dushantha Rodrigo', 2016, '斯里蘭卡可倫坡',
 '含斯里蘭卡；直屬坎特伯里大主教，非完整自治省。', 'Anglican Communion records'),

('緬甸聖公宗大主教座',
 'Church of the Province of Myanmar — Archbishop',
 '緬甸聖公宗', '緬甸聖公宗', '聖公宗', '英格蘭教會禮', 1970, NULL, '現存',
 '大主教史蒂芬·丹明烏', 'Archbishop Stephen Than Myint Oo', 2017, '緬甸仰光',
 '1970年成為自治省。', 'Anglican Communion records'),

('孟加拉教會大主教座',
 'Church of Bangladesh — Bishop',
 '孟加拉教會', '孟加拉教會', '聖公宗', '英格蘭教會禮', 1971, NULL, '現存',
 '主教薩繆爾·馬恩欽', 'Bishop Samuel Sunil Mankhin', 2015, '孟加拉達卡',
 '直屬坎特伯里大主教，非完整自治省。', 'Anglican Communion records'),

('耶路撒冷及中東聖公宗省大主教座',
 'Episcopal Church in Jerusalem and the Middle East — President Bishop',
 '耶路撒冷聖公宗', '耶路撒冷及中東聖公宗', '聖公宗', '英格蘭教會禮', 1976, NULL, '現存',
 '主教霍薩姆·諾姆', 'President Bishop Hosam Naoum', 2021, '以色列耶路撒冷',
 '含以色列、埃及、伊朗、伊拉克、塞浦路斯。1976年成為自治省。', 'Anglican Communion records'),

-- X. 北歐信義宗大主教座
('烏普薩拉大主教座',
 'Archdiocese of Uppsala (Church of Sweden)',
 '烏普薩拉', '瑞典信義會', '信義宗', '路德宗禮', 1164, NULL, '現存',
 '大主教馬丁·莫多伊斯', 'Archbishop Martin Modéus', 2022, '瑞典烏普薩拉',
 '1164年設大主教座；1527年宗教改革後成為信義宗教會，但保留主教制及歷史繼承。',
 'Church of Sweden records; Uppsala archdiocese'),

('圖爾庫大主教座',
 'Archdiocese of Turku (Evangelical Lutheran Church of Finland)',
 '圖爾庫', '芬蘭信義會', '信義宗', '路德宗禮', 1276, NULL, '現存',
 '大主教塔皮奧·盧奧馬', 'Archbishop Tapio Luoma', 2018, '芬蘭圖爾庫',
 '1276年設主教座；1523年宗教改革（馬丁·斯克特）；1817年升為大主教座。',
 'Evangelical Lutheran Church of Finland records'),

('塔林大主教座（愛沙尼亞信義宗）',
 'Archdiocese of Tallinn (Estonian Evangelical Lutheran Church)',
 '塔林', '愛沙尼亞信義會', '信義宗', '路德宗禮', 1917, NULL, '現存',
 '大主教烏爾馬斯·維爾斯特魯克', 'Archbishop Urmas Viilma', 2015, '愛沙尼亞塔林',
 '1917年建立獨立教會；1940–1991年蘇聯時期被壓制；1991年獨立後重建。',
 'Estonian Evangelical Lutheran Church records'),

('里加大主教座（拉脫維亞信義宗）',
 'Archdiocese of Riga (Evangelical Lutheran Church of Latvia)',
 '里加', '拉脫維亞信義會', '信義宗', '路德宗禮', 1918, NULL, '現存',
 '大主教坎提斯·埃爾斯', 'Archbishop Jānis Vanags', 1993, '拉脫維亞里加',
 '1918年建立獨立教會；蘇聯時期受壓制；1991年重建。',
 'Evangelical Lutheran Church of Latvia records'),

-- XI. 老天主教及獨立天主教
('烏特勒支老天主教大主教座',
 'Old Catholic Archdiocese of Utrecht',
 '烏特勒支', '老天主教', '老天主教', '羅馬禮（老天主教）', 695, NULL, '現存',
 '大主教貝里克-揚·徳科特', 'Archbishop Bernd Wallet', 2020, '荷蘭烏特勒支',
 '695年設主教座。1724年因揚森主義爭議脫離羅馬；1870年第一次梵蒂岡大公會議後吸納拒絕教宗無誤論的主教，形成老天主教聯合（烏特勒支聯合）。',
 'Old Catholic Church records; Utrecht Union'),

-- XII. 北美聖公宗教會（不在聖公宗共融內）
('北美聖公宗教會大主教座',
 'Anglican Church in North America — Archbishop',
 '北美聖公宗', '北美聖公宗教會', '聖公宗', '英格蘭教會禮', 2009, NULL, '現存',
 NULL, NULL, NULL, '美國德克薩斯',
 '2009年由保守聖公宗信眾脫離美國聖公會成立；未被聖公宗共融（Anglican Communion）正式承認，但獲許多省認可。',
 'ACNA records');

-- 設定 parent_see_id
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '坎特伯里大主教座（中世紀天主教）')
  WHERE name_zh = '坎特伯里大主教座（英格蘭教會）';

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '約克大主教座（中世紀天主教）')
  WHERE name_zh = '約克大主教座（英格蘭教會）';

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '坎特伯里大主教座（英格蘭教會）')
  WHERE name_zh IN (
    '約克大主教座（英格蘭教會）',
    '阿馬大主教座（愛爾蘭教會）', '都柏林大主教座（愛爾蘭教會）',
    '威爾士教會大主教座', '蘇格蘭聖公會主教長',
    '奈及利亞聖公宗大主教座', '烏干達聖公宗大主教座', '肯亞聖公宗大主教座',
    '南非聖公宗大主教座', '坦尚尼亞聖公宗大主教座', '西非聖公宗省大主教座',
    '中非聖公宗省大主教座', '盧安達聖公宗大主教座', '南蘇丹聖公宗大主教座',
    '蘇丹聖公宗大主教座', '蒲隆地聖公宗大主教座', '亞歷山卓聖公宗省大主教座',
    '印度洋省聖公宗大主教座',
    '美國聖公會首牧教座', '加拿大聖公宗大主教座', '西印度群島聖公宗大主教座',
    '巴西聖公宗大主教座', '墨西哥聖公宗大主教座', '南美南錐聖公宗大主教座',
    '古巴聖公宗（直屬）',
    '韓國聖公宗大主教座', '菲律賓聖公宗大主教座', '日本聖公會大主教座',
    '香港聖公宗大主教座', '東南亞聖公宗省大主教座', '巴布亞紐幾內亞聖公宗大主教座',
    '美拉尼西亞聖公宗省大主教座', '紐西蘭及波利尼西亞聖公宗大主教座',
    '澳洲聖公宗大主教座',
    '北印度教會大主教座', '南印度教會大主教座', '巴基斯坦教會大主教座',
    '錫蘭教會大主教座', '緬甸聖公宗大主教座', '孟加拉教會大主教座',
    '耶路撒冷及中東聖公宗省大主教座'
  );
