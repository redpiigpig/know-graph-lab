-- ============================================================
-- 東方正統教會（Oriental Orthodox）及東儀天主教（Eastern Catholic）
-- 歷任首牧列表
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- 一、科普特東正教亞歷山大宗主教座（Coptic Orthodox）
--     see = '亞歷山大'，church = '科普特正教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('聖馬爾谷', 'Saint Mark the Evangelist', '亞歷山大', '科普特正教', 1, 42, 68, '殉道', '使徒伯多祿', '正統',
 'Eusebius, HE II.16; Coptic Synaxarion',
 '福音書作者，由伯多祿差遣至埃及；約 68 年殉道。科普特正教視其為首任教宗'),

('阿尼阿努斯', 'Anianus', '亞歷山大', '科普特正教', 2, 68, 83, '自然死亡', NULL, '正統',
 'Eusebius, HE II.24; Coptic Synaxarion', '傳統上為馬爾谷所立'),

('阿維里烏斯', 'Avilius', '亞歷山大', '科普特正教', 3, 83, 95, '自然死亡', NULL, '正統',
 'Eusebius, HE III.14', NULL),

('塞爾東', 'Cerdon', '亞歷山大', '科普特正教', 4, 95, 106, '自然死亡', NULL, '正統',
 'Eusebius, HE III.21', NULL),

('普理穆斯', 'Primus', '亞歷山大', '科普特正教', 5, 106, 118, '自然死亡', NULL, '正統',
 'Eusebius, HE IV.1', NULL),

('聖底米特流一世', 'Saint Demetrius I', '亞歷山大', '科普特正教', 12, 189, 231, '自然死亡', NULL, '正統',
 'Eusebius, HE VI.2; Coptic records',
 '任期長達 42 年；開始要求亞歷山大主教須具備修道生活；與奧利振（Origen）有複雜關係'),

('聖濟利祿一世', 'Saint Cyril I of Alexandria', '亞歷山大', '科普特正教', 24, 412, 444, '自然死亡', NULL, '正統',
 'ACO I; Cyril of Alexandria, Opera omnia',
 '主導 431 年以弗所公會議，確立聖母為「天主之母」（Theotokos）；亞歷山大神學傳統頂峰'),

('狄奧斯科魯一世', 'Dioscorus I', '亞歷山大', '科普特正教', 25, 444, 454, '廢黜', NULL, '爭議',
 'ACO II; Price & Gaddis, Acts of Chalcedon',
 '451 年迦克敦公會議廢黜其職；此為東正教與科普特正教統緒正式分裂之起點。科普特正教視其為殉道聖人，東正教視其為異端'),

('本篤十六世·沙努達三世（謝努達三世）', 'Pope Shenouda III', '亞歷山大', '科普特正教', 117, 1971, 2012, '自然死亡', NULL, '正統',
 'Coptic Orthodox Church records',
 '任期長達 41 年；1973 年與教宗保祿六世會面，發表聯合基督論聲明（共同信仰宣言）；1981–1985 年遭沙達特總統軟禁'),

('教宗塔瓦德羅斯二世', 'Pope Tawadros II', '亞歷山大', '科普特正教', 118, 2012, NULL, NULL, NULL, '正統',
 'Coptic Orthodox Church records', '現任科普特教宗；2013 年與教宗方濟各會面');


-- ════════════════════════════════════════════════════════════
-- 二、敘利亞東方正教安提阿宗主教座（Syriac Orthodox）
--     see = '安提阿'，church = '敘利亞正教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('安提阿的塞維魯', 'Severus of Antioch', '安提阿', '敘利亞正教', 34, 512, 518, '廢黜', '正統',
 'John of Ephesus, Lives of the Eastern Saints; Zacharias, Chronicle',
 '敘利亞正教最重要的早期神學家；被查士丁尼一世廢黜，流亡埃及，死後仍受敘利亞正教尊為聖人'),

('雅各布·巴拉代烏斯', 'Jacob Baradaeus', '安提阿', '敘利亞正教', NULL, 543, 578, '自然死亡', '正統',
 'John of Ephesus, HE; Honigmann, Évêques et évêchés',
 '「雅各派」名稱來源；以秘密祝聖方式廣植主教，使敘利亞正教在拜占庭迫害下存活；統緒所繫'),

('依格那提烏斯·努爾·阿拉一世', 'Ignatius Nuh al-Lebnan', '安提阿', '敘利亞正教', NULL, 1493, 1509, '自然死亡', '正統',
 'Syriac Orthodox Church records', NULL),

('依格那提烏斯·艾佛雷姆一世·巴薩姆', 'Ignatius Ephrem I Barsoum', '安提阿', '敘利亞正教', NULL, 1933, 1957, '自然死亡', '正統',
 'Barsoum, History of Syriac Literature',
 '重要學者，著有《散落的珍珠》（敘利亞文學史）；1947 年出席聯合國巴勒斯坦問題特別委員會'),

('依格那提烏斯·雅各布三世', 'Ignatius Jacob III', '安提阿', '敘利亞正教', NULL, 1957, 1980, '自然死亡', '正統',
 'Syriac Orthodox Church records',
 '任內與多個教會推進對話；擴大海外教區'),

('依格那提烏斯·扎卡一世·伊瓦斯', 'Ignatius Zakka I Iwas', '安提阿', '敘利亞正教', NULL, 1980, 2014, '自然死亡', '正統',
 'Syriac Orthodox Church records',
 '任內積極推進東方基督教合一對話；任期長達 34 年'),

('依格那提烏斯·阿夫雷姆二世', 'Ignatius Aphrem II', '安提阿', '敘利亞正教', NULL, 2014, NULL, NULL, '正統',
 'Syriac Orthodox Church records', '現任宗主教');


-- ════════════════════════════════════════════════════════════
-- 三、衣索比亞東正教泰瓦赫多宗主教座
--     see = '衣索比亞'，church = '衣索比亞東正教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('弗魯門提烏斯', 'Frumentius (Abba Selama)', '衣索比亞', '衣索比亞東正教', 1, 330, 383, '自然死亡', '亞歷山大宗主教亞大納削', '正統',
 'Rufinus, HE I.9; Athanasius, Apologia ad Constantium',
 '衣索比亞基督教創立者；由亞大納削祝聖，被稱為「光明之父」（Abba Selama）。此後 1,500 年間，衣索比亞的 Abun（宗主教）一直由亞歷山大科普特教宗任命'),

('阿布訥·馬提奧斯一世', 'Abune Matewos I', '衣索比亞', '衣索比亞東正教', NULL, 1881, 1926, '自然死亡', '科普特教宗', '正統',
 'Ethiopian church records',
 '最後幾位由科普特教宗任命的 Abun 之一；任內見證衣索比亞抵抗義大利入侵'),

('阿布訥·伯多羅斯四世', 'Abune Petros IV', '衣索比亞', '衣索比亞東正教', NULL, 1929, 1936, '殉道', '科普特教宗', '正統',
 'Ethiopian church records',
 '1936 年義大利占領期間因拒絕承認占領而被處決，視為殉道者'),

('阿布訥·巴西利奧斯', 'Abune Basilios', '衣索比亞', '衣索比亞東正教', 1, 1951, 1971, '自然死亡', '科普特教宗', '正統',
 'Ethiopian Imperial decree (1959)',
 '1951 年成為首位衣索比亞籍 Abun；1959 年衣索比亞獲得自治，成為首位宗主教'),

('阿布訥·德歐菲洛斯', 'Abune Theophilos', '衣索比亞', '衣索比亞東正教', 2, 1971, 1979, '殉道', NULL, '正統',
 'Ethiopian church records',
 '1974 年德爾格政變後被囚，1979 年秘密處決；2015 年正式確認其死亡'),

('阿布訥·托庫埃', 'Abune Tekle Haymanot', '衣索比亞', '衣索比亞東正教', 3, 1976, 1988, '自然死亡', '德爾格政府', '爭議',
 'Ethiopian church records',
 '德爾格政府任命，正統性受部分教會人士質疑'),

('阿布訥·梅爾科里奧斯', 'Abune Merkorios', '衣索比亞', '衣索比亞東正教', 4, 1988, 1991, '廢黜', NULL, '廢黜後復位',
 'Ethiopian church records',
 '1991 年德爾格垮台後被廢黜；流亡美國。2018 年歷史性和解後，與現任宗主教共同被承認'),

('阿布訥·保祿斯', 'Abune Paulos', '衣索比亞', '衣索比亞東正教', 5, 1992, 2012, '自然死亡', NULL, '正統',
 'Ethiopian church records',
 '任期長達 20 年；任內擴大海外教區；推動與羅馬天主教的對話'),

('阿布訥·瑪帝亞斯一世', 'Abune Mathias I', '衣索比亞', '衣索比亞東正教', 6, 2013, NULL, NULL, NULL, '正統',
 'Ethiopian church records', '現任宗主教');


-- ════════════════════════════════════════════════════════════
-- 四、厄立特里亞東正教泰瓦赫多宗主教座
--     see = '厄立特里亞'，church = '厄立特里亞東正教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('阿布訥·菲利克索斯', 'Abune Philipos', '厄立特里亞', '厄立特里亞東正教', 1, 1994, 2002, '自然死亡', '正統',
 'Eritrean Orthodox Church records',
 '1993 年厄立特里亞獨立後首任宗主教'),

('阿布訥·雅各布', 'Abune Yacob', '厄立特里亞', '厄立特里亞東正教', 2, 2004, 2004, '自然死亡', '正統',
 'Eritrean Orthodox Church records', '任期甚短'),

('阿布訥·安托尼奧斯', 'Abune Antonios', '厄立特里亞', '厄立特里亞東正教', 3, 2004, 2022, '殉道', '正統',
 'Human Rights Watch; Eritrean Orthodox Church records',
 '2007 年遭政府強制軟禁，直至 2022 年辭世。國際教會界普遍視其為合法宗主教，多個東方正教會不承認繼任者'),

('阿布訥·克洛斯', 'Abune Qerlos', '厄立特里亞', '厄立特里亞東正教', 4, 2021, NULL, NULL, '爭議',
 'Eritrean government announcement',
 '2021 年由厄立特里亞政府任命；合法性受廣泛質疑');


-- ════════════════════════════════════════════════════════════
-- 五、全亞美尼亞公教主教座（厄奇米亞津）
--     see = '厄奇米亞津'，church = '亞美尼亞使徒教會'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('聖額我略·啟蒙者', 'Saint Gregory the Illuminator', '厄奇米亞津', '亞美尼亞使徒教會', 1, 301, 325, '辭職', '國王提里達底三世', '正統',
 'Agathangelos, History of the Armenians',
 '使亞美尼亞成為第一個基督教國家的關鍵人物；約 301 年為國王提里達底三世洗禮；已被封聖'),

('阿里斯塔科斯', 'Aristakes', '厄奇米亞津', '亞美尼亞使徒教會', 2, 325, 333, '殉道', NULL, '正統',
 'Armenian church chronicles',
 '額我略之子；325 年代表亞美尼亞出席尼西亞大公會議'),

('涅爾塞斯一世', 'Nerses I the Great', '厄奇米亞津', '亞美尼亞使徒教會', 4, 353, 373, '殉道', NULL, '正統',
 'Faustus of Byzantium, History of Armenia',
 '大力推動亞美尼亞教會組織化及修道制度；被封為聖涅爾塞斯大帝'),

('聖撒哈克一世', 'Saint Sahak I the Great', '厄奇米亞津', '亞美尼亞使徒教會', 8, 387, 438, '自然死亡', NULL, '正統',
 'Lazar of Pharp, History of Armenia',
 '與梅斯羅布·瑪斯托茨共同創制亞美尼亞字母（405 年）；翻譯聖經為亞美尼亞文；已被封聖'),

('霍夫漢內斯·科莫拉斯', 'Hovhannes V Komouras', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1443, 1465, '自然死亡', NULL, '正統',
 'Armenian church chronicles',
 '1441 年厄奇米亞津重建為首席公教主教座後的首任公教主教'),

('帕爾格夫一世·恰哈克比揚', 'Catholicos Pargen I Chahakpetian', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1748, 1763, '自然死亡', NULL, '正統',
 'Armenian church archives', NULL),

('格奧爾格五世', 'Catholicos Gevorg V', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1911, 1930, '自然死亡', NULL, '正統',
 'Armenian Apostolic Church records',
 '見證亞美尼亞種族滅絕（1915–1923）；在蘇聯早期統治下維護教會'),

('格奧爾格六世', 'Catholicos Gevorg VI', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1945, 1954, '自然死亡', NULL, '正統',
 'Armenian Apostolic Church records',
 '二戰後與史達林交涉，為蘇聯境內亞美尼亞教會爭取有限的運作空間'),

('瓦茲根一世', 'Catholicos Vazgen I', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1955, 1994, '自然死亡', NULL, '正統',
 'Armenian Apostolic Church records',
 '任期長達 39 年；見證亞美尼亞獨立（1991年）；深受亞美尼亞人尊敬'),

('卡列金一世', 'Catholicos Karekin I', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1995, 1999, '自然死亡', NULL, '正統',
 'Armenian Apostolic Church records',
 '曾任基里家公教主教，轉任厄奇米亞津；任期僅 4 年'),

('卡列金二世', 'Catholicos Karekin II', '厄奇米亞津', '亞美尼亞使徒教會', NULL, 1999, NULL, NULL, NULL, '正統',
 'Armenian Apostolic Church records', '現任公教主教；2025 年因政治壓力面臨辭職呼聲');


-- ════════════════════════════════════════════════════════════
-- 六、基里家公教主教座（亞美尼亞使徒教會第二座）
--     see = '基里家'，church = '亞美尼亞使徒教會'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('格奧爾格一世·瑪嘎布達涅茨', 'Catholicos Georg I Mxargrdzetsi', '基里家', '亞美尼亞使徒教會', 1, 1066, 1077, '自然死亡', '正統',
 'Armenian Catholicate of Cilicia records',
 '基里家公教主教座首任公教主教；在十字軍時代的基里家亞美尼亞王國服事'),

('格里高利三世·帕拉夫尼', 'Catholicos Gregory III Pahlawuni', '基里家', '亞美尼亞使徒教會', NULL, 1113, 1166, '自然死亡', '正統',
 'Armenian Catholicate of Cilicia records',
 '基里家時代最重要的公教主教之一；推動與十字軍及拜占庭的外交關係'),

('阿蘭一世', 'Catholicos Aram I', '基里家', '亞美尼亞使徒教會', NULL, 1995, NULL, NULL, '正統',
 'Armenian Catholicate of Cilicia records',
 '現任公教主教；積極推動世界教會協進會的東方正教代表工作');


-- ════════════════════════════════════════════════════════════
-- 七、馬拉巴爾東正教宗主教座
--     see = '馬拉巴爾'，church = '馬拉巴爾東正教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('馬爾·帕烏盧斯', 'Mar Paulose Kadavil', '馬拉巴爾', '馬拉巴爾東正教', NULL, 1653, 1672, '自然死亡', '自立', '正統',
 'Malankara Orthodox Syrian Church records',
 '1653 年庫南十字架誓言（Coonan Cross Oath）後，馬拉巴爾基督徒宣布脫離葡萄牙天主教管轄；傳統從使徒多馬追溯起源'),

('馬爾·帕烏盧斯·阿塔納修斯', 'Paulose Mar Athanasius', '馬拉巴爾', '馬拉巴爾東正教', 1, 1912, 1917, '自然死亡', '敘利亞東方正教宗主教', '正統',
 'Malankara Orthodox Church records',
 '1912 年宣布自主後首任公教主教'),

('格里高利烏斯·帕烏盧斯一世', 'Gregorios Paulose I', '馬拉巴爾', '馬拉巴爾東正教', 2, 1917, 1929, '自然死亡', NULL, '正統',
 'Malankara Orthodox Church records', NULL),

('巴西利奧斯·格里高利烏斯', 'Baselios Geevarghese I', '馬拉巴爾', '馬拉巴爾東正教', 3, 1929, 1964, '自然死亡', NULL, '正統',
 'Malankara Orthodox Church records', '任期長達 35 年'),

('巴西利奧斯·奧格斯丁', 'Baselios Augen I', '馬拉巴爾', '馬拉巴爾東正教', 4, 1964, 1975, '自然死亡', NULL, '正統',
 'Malankara Orthodox Church records', NULL),

('巴西利奧斯·馬修斯一世', 'Baselios Marthoma Mathews I', '馬拉巴爾', '馬拉巴爾東正教', 5, 1975, 1991, '自然死亡', NULL, '正統',
 'Malankara Orthodox Church records', NULL),

('巴西利奧斯·馬修斯二世', 'Baselios Marthoma Mathews II', '馬拉巴爾', '馬拉巴爾東正教', 6, 1991, 2021, '自然死亡', NULL, '正統',
 'Malankara Orthodox Church records', '任期 30 年'),

('巴西利奧斯·馬修斯三世', 'Baselios Marthoma Mathews III', '馬拉巴爾', '馬拉巴爾東正教', 7, 2021, NULL, NULL, NULL, '正統',
 'Malankara Orthodox Church records', '現任公教主教');


-- ════════════════════════════════════════════════════════════
-- 八、馬龍尼特禮天主教安提阿宗主教座
--     see = '安提阿'，church = '馬龍尼特禮天主教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

('若望·馬龍', 'John Maron', '安提阿', '馬龍尼特禮天主教', 1, 685, 707, '自然死亡', NULL, '正統',
 'Maronite Patriarchal sources; Dau, History of the Maronites',
 '馬龍尼特禮首位宗主教；鞏固與羅馬的共融關係'),

('依斯提凡·杜維希', 'Estephan el Duaihi', '安提阿', '馬龍尼特禮天主教', NULL, 1670, 1704, '自然死亡', NULL, '正統',
 'Dau, History of the Maronites',
 '重要馬龍尼特史學家，著有多部馬龍尼特教會史著作；被尊稱為「馬龍尼特教會之父」'),

('保祿二世·馬薩德', 'Boulos Meouchi', '安提阿', '馬龍尼特禮天主教', NULL, 1955, 1975, '自然死亡', NULL, '正統',
 'Maronite Patriarchal records',
 '黎巴嫩內戰前最後一任太平時代的宗主教'),

('安東尼·哈雷克', 'Antoine Pierre Khoraiche', '安提阿', '馬龍尼特禮天主教', NULL, 1975, 1986, '辭職', NULL, '正統',
 'Maronite Patriarchal records', '黎巴嫩內戰期間在位'),

('納斯拉拉·斯法伊爾', 'Nasrallah Boutros Sfeir', '安提阿', '馬龍尼特禮天主教', NULL, 1986, 2011, '辭職', NULL, '正統',
 'Maronite Patriarchal records',
 '任期長達 25 年；領導「3.14 運動」，促成敘利亞軍隊撤出黎巴嫩（2005）；2011 年因年邁辭職'),

('貝沙拉·布特羅斯·拉希', 'Bechara Boutros al-Rahi', '安提阿', '馬龍尼特禮天主教', NULL, 2011, NULL, NULL, NULL, '正統',
 'Maronite Patriarchal records', '現任宗主教；2012 年晉升樞機主教');


-- ════════════════════════════════════════════════════════════
-- 九、希臘天主教麥勒基特禮安提阿宗主教座
--     see = '安提阿'，church = '希臘天主教麥勒基特禮'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('濟利祿六世·塔納斯', 'Cyril VI Tanas', '安提阿', '希臘天主教麥勒基特禮', 1, 1724, 1759, '自然死亡', '正統',
 'Hajjar, Les chrétiens uniates du Proche-Orient',
 '1724 年東正教安提阿宗主教選舉後分裂，為首任梅基特宗主教；隔年（1725）獲羅馬正式承認'),

('濟利祿七世·西阿吉', 'Cyril VII Siaj', '安提阿', '希臘天主教麥勒基特禮', 2, 1759, 1796, '自然死亡', '正統',
 'Melkite Patriarchal records', NULL),

('馬克西莫斯三世·馬祖姆', 'Maximos III Mazloum', '安提阿', '希臘天主教麥勒基特禮', 5, 1833, 1855, '自然死亡', '正統',
 'Melkite Patriarchal records',
 '獲鄂圖曼帝國正式承認；確立梅基特禮在鄂圖曼境內的法律地位'),

('格里高利烏斯二世·尤塞夫', 'Gregorios II Youssef', '安提阿', '希臘天主教麥勒基特禮', 6, 1864, 1897, '自然死亡', '正統',
 'Melkite Patriarchal records',
 '1870 年以梅基特禮代表出席梵蒂岡第一次大公會議，對教宗無謬誤論持批評立場'),

('馬克西莫斯四世·薩伊格', 'Maximos IV Saigh', '安提阿', '希臘天主教麥勒基特禮', NULL, 1947, 1967, '自然死亡', '正統',
 'Melkite Patriarchal records',
 '梵蒂岡第二次大公會議（1962–1965）的關鍵人物；力主在天主教內推動東方禮儀的平等地位，用阿拉伯語而非拉丁語發言'),

('哈肯·穆薩一世', 'Maximos V Hakim', '安提阿', '希臘天主教麥勒基特禮', NULL, 1967, 2000, '辭職', '正統',
 'Melkite Patriarchal records', NULL),

('格里高利烏斯三世·拉哈姆', 'Gregorios III Laham', '安提阿', '希臘天主教麥勒基特禮', NULL, 2000, 2017, '辭職', '正統',
 'Melkite Patriarchal records', '因敘利亞內戰對教區造成的衝擊而辭職'),

('優素福·阿布西', 'Youssef Absi', '安提阿', '希臘天主教麥勒基特禮', NULL, 2017, NULL, NULL, '正統',
 'Melkite Patriarchal records', '現任宗主教');


-- ════════════════════════════════════════════════════════════
-- 十、敘利亞天主教安提阿宗主教座
--     see = '安提阿'，church = '敘利亞天主教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('米迦勒·賈爾韋', 'Michael Jarweh', '安提阿', '敘利亞天主教', 1, 1782, 1800, '自然死亡', '正統',
 'Syriac Catholic Patriarchal records',
 '1782 年從敘利亞正教轉入天主教，首任敘利亞天主教宗主教'),

('依格那提烏斯·若望九世·托尼', 'Ignatius George V Touni', '安提阿', '敘利亞天主教', NULL, 1820, 1847, '自然死亡', '正統',
 'Syriac Catholic Patriarchal records', NULL),

('依格那提烏斯·依弗雷姆二世·拉哈尼', 'Ignatius Ephrem II Rahmani', '安提阿', '敘利亞天主教', NULL, 1898, 1929, '自然死亡', '正統',
 'Syriac Catholic Patriarchal records',
 '重要學者，出版多部敘利亞文獻'),

('依格那提烏斯·安東尼奧斯二世', 'Ignatius Antoine II Hayek', '安提阿', '敘利亞天主教', NULL, 1966, 1998, '辭職', '正統',
 'Syriac Catholic Patriarchal records', NULL),

('依格那提烏斯·約瑟夫三世·尤南', 'Ignatius Joseph III Yonan', '安提阿', '敘利亞天主教', NULL, 2009, NULL, NULL, '正統',
 'Syriac Catholic Patriarchal records', '現任宗主教；2016 年晉升樞機主教');


-- ════════════════════════════════════════════════════════════
-- 十一、亞美尼亞天主教基里家宗主教座
--       see = '基里家'，church = '亞美尼亞天主教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('亞伯拉罕·阿爾扎維揚', 'Abraham Ardzivian', '基里家', '亞美尼亞天主教', 1, 1742, 1749, '自然死亡', '正統',
 'Armenian Catholic Patriarchal records',
 '首位與羅馬建立穩定共融的亞美尼亞天主教公教主教'),

('格里高利烏斯·彼得羅斯十五世·阿加賈尼安', 'Grigoris Petros XV Agagianian', '基里家', '亞美尼亞天主教', NULL, 1937, 1962, '辭職', '正統',
 'Armenian Catholic Patriarchal records; Annuario Pontificio',
 '1946、1958 年兩度在教宗選舉中為呼聲最高人選；1958 年晉升樞機主教；1962 年辭去宗主教職務專任樞機'),

('拉法葉·貝德羅斯二十一世·米納西安', 'Raphaël Bedros XXI Minassian', '基里家', '亞美尼亞天主教', NULL, 2021, NULL, NULL, '正統',
 'Armenian Catholic Patriarchal records', '現任宗主教；2024 年晉升樞機主教');


-- ════════════════════════════════════════════════════════════
-- 十二、科普特天主教亞歷山大宗主教座
--       see = '亞歷山大'，church = '科普特天主教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('西里爾八世·馬卡里烏斯二世', 'Cyril VIII Macarius II', '亞歷山大', '科普特天主教', 1, 1895, 1908, '自然死亡', '正統',
 'Coptic Catholic Patriarchal records; Catholic Encyclopedia',
 '1895 年教宗良十三世正式設立科普特天主教宗主教座，首任宗主教'),

('馬爾科斯二世·克胡贊', 'Marcos II Khouzam', '亞歷山大', '科普特天主教', 2, 1908, 1958, '自然死亡', '正統',
 'Coptic Catholic Patriarchal records', '任期長達 50 年'),

('斯特法諾斯一世·西達魯斯', 'Stephanos I Sidarouss', '亞歷山大', '科普特天主教', 3, 1958, 1986, '辭職', '正統',
 'Coptic Catholic Patriarchal records',
 '1965 年晉升樞機主教，為首位科普特天主教樞機'),

('安德拉烏斯·加拉布', 'Andraouis Ghattas', '亞歷山大', '科普特天主教', 4, 1986, 2006, '辭職', '正統',
 'Coptic Catholic Patriarchal records', NULL),

('安東尼·納吉布', 'Antonios Naguib', '亞歷山大', '科普特天主教', 5, 2006, 2013, '辭職', '正統',
 'Coptic Catholic Patriarchal records', '2010 年晉升樞機主教'),

('易卜拉欣·以撒·西德拉克', 'Ibrahim Isaac Sidrak', '亞歷山大', '科普特天主教', 6, 2013, NULL, NULL, '正統',
 'Coptic Catholic Patriarchal records', '現任宗主教');


-- ════════════════════════════════════════════════════════════
-- 十三、迦勒底天主教巴格達宗主教座
--       see = '巴格達'，church = '迦勒底天主教'
-- ════════════════════════════════════════════════════════════
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, status, sources, notes) VALUES

('約翰·蘇拉卡', 'John Sulaqa', '巴格達', '迦勒底天主教', 1, 1553, 1555, '殉道', '正統',
 'Baum & Winkler, Church of the East',
 '1552 年赴羅馬，由教宗儒略三世祝聖，為首位迦勒底天主教宗主教；返回後被競爭對手謀殺'),

('約瑟夫一世·薩卡', 'Joseph I Saka', '巴格達', '迦勒底天主教', NULL, 1681, 1695, '自然死亡', '正統',
 'Chaldean Catholic Patriarchal records',
 '1681 年迦勒底傳承穩定確立後的關鍵宗主教'),

('若望八世·霍爾米茲德', 'Johannes VIII Hormizd', '巴格達', '迦勒底天主教', NULL, 1830, 1838, '自然死亡', '正統',
 'Chaldean Catholic Patriarchal records',
 '1830 年在其任內，現代迦勒底天主教宗主教座正式穩定確立'),

('依格那提烏斯·喬治·達維德', 'Raphael I Bidawid', '巴格達', '迦勒底天主教', NULL, 1989, 2003, '自然死亡', '正統',
 'Chaldean Catholic Patriarchal records',
 '任內歷經波灣戰爭與制裁；積極維護伊拉克基督徒權益'),

('依曼紐一世·達里·達利', 'Emmanuel III Delly', '巴格達', '迦勒底天主教', NULL, 2003, 2012, '辭職', '正統',
 'Chaldean Catholic Patriarchal records',
 '2007 年晉升樞機主教；任內歷經伊拉克戰爭對基督徒社區的嚴重衝擊'),

('路易·拉法葉一世·薩科', 'Louis Raphael I Sako', '巴格達', '迦勒底天主教', NULL, 2013, 2026, '辭職', '正統',
 'Vatican News; Chaldean Catholic Patriarchal records',
 '2014 年晉升樞機主教；2026 年 4 月辭職'),

('馬爾·保祿三世·諾納', 'Mar Paulos III Nona', '巴格達', '迦勒底天主教', NULL, 2026, NULL, NULL, '正統',
 'Vatican News 2026-04', '現任宗主教；2026 年 4 月當選');
