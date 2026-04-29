-- ============================================================
-- 天主教大主教傳承——中歐（薩爾斯堡、維也納、華沙、克拉科夫）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 薩爾斯堡（Salzburg）
-- 「北方羅馬」；神聖羅馬帝國大主教親王
-- ==============================
('聖盧珀特', 'Saint Rupert of Salzburg', '薩爾斯堡', '天主教', 1, 696, 718, '逝世', '巴伐利亞公爵特奧多', '正統', 'MGH; Hauck, Kirchengeschichte', '薩爾斯堡教區創始人；「鹽業使徒」；弗蘭肯主教轉至薩爾斯堡傳教；建聖彼得修道院'),
('聖維爾吉利烏斯（韋爾吉爾）', 'Saint Virgil (Virgilius) of Salzburg', '薩爾斯堡', '天主教', 8, 749, 784, '逝世', '卜尼法斯（爭議）', '正統', 'MGH; R. Sharpe', '愛爾蘭籍主教；被卜尼法斯指控異端（宣揚對跖人antipodes存在）但獲教宗支持；784年封聖；推動斯洛維尼亞基督化'),
('阿諾·一世（第一任大主教）', 'Arno of Salzburg', '薩爾斯堡', '天主教', 9, 785, 821, '逝世', '教宗哈德良一世', '正統', 'MGH', '798年薩爾斯堡升格為大主教區（在查理大帝支持下）；阿爾卑斯以東的傳教大本營；阿爾庫因的友人'),
('孔拉德一世', 'Conrad I of Salzburg', '薩爾斯堡', '天主教', 16, 1106, 1147, '退休（加入西篤會）', '教宗帕斯卡二世', '正統', 'MGH; Hauck', '格里高利改革（Gregorian Reform）的積極推動者；反對神聖羅馬皇帝的主教敘任權'),
('埃貝哈爾德一世', 'Eberhard I of Regensberg', '薩爾斯堡', '天主教', 17, 1147, 1164, '逝世', '教宗尤金尼烏斯三世', '正統', 'MGH', '西篤會士；與弗萊辛的鄂圖（歷史學家）同時代；第二次十字軍東征支持者'),
('沃爾夫·迪特里希·馮·賴特瑙', 'Wolf Dietrich von Raitenau', '薩爾斯堡', '天主教', 55, 1587, 1612, '廢黜', '教宗西斯都五世', '正統', 'Catholic Hierarchy', '巴洛克薩爾斯堡的建造者；大規模城市改造（義大利風格）；晚年因政治失誤被巴伐利亞俘虜囚禁至死'),
('馬科斯·西提庫斯', 'Markus Sittikus von Hohenems', '薩爾斯堡', '天主教', 56, 1612, 1619, '逝世', '教宗保羅五世', '正統', 'Catholic Hierarchy', '建造赫爾布倫宮（Hellbrunn Palace）；建立薩爾斯堡最早的歌劇院（1617）——世界上最早之一'),
('帕黎斯·馮·洛德龍', 'Paris von Lodron', '薩爾斯堡', '天主教', 57, 1619, 1653, '逝世', '教宗保羅五世', '正統', 'Catholic Hierarchy', '三十年戰爭（1618–1648）期間保持薩爾斯堡中立；建城牆防禦；薩爾斯堡大學創建（1622）'),
('海羅尼姆斯·馮·科洛雷多', 'Hieronymus von Colloredo', '薩爾斯堡', '天主教', 64, 1772, 1803, '退休（教區解散）', '教宗克萊孟十四世', '正統', 'Catholic Hierarchy', '啟蒙主義大主教；推行教育改革；與莫扎特（Wolfgang Amadeus Mozart）著名衝突——莫扎特曾任其宮廷樂師，後決裂；1803年世俗化失去親王地位'),
('菲爾明·羅斯科', 'Firmian Rosko', '薩爾斯堡', '天主教', 69, 1823, 1854, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '政教協議後的第一任現代薩爾斯堡大主教；恢復教會組織'),
('安德烈亞斯·羅奧滕施特勞赫', 'Andreas Rohracher', '薩爾斯堡', '天主教', 77, 1943, 1969, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '二戰期間；梵二大公會議參與者'),
('弗蘭茨·拉克納', 'Franz Lackner', '薩爾斯堡', '天主教', 80, 2013, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '方濟各會士；奧地利主教團主席（2020–）');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '薩爾斯堡' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 維也納（Vienna）
-- 哈布斯堡王朝首都；1722年升格為大主教區
-- ==============================
('保羅·祖』·紹', 'Rudolph IV, Duke as founder', '維也納', '天主教', 0, 1365, 1365, NULL, NULL, '正統', 'Austrian Church History', '1365年鲁道夫四世設立維也納教區（同年建維也納大學）；原為帕紹主教下轄教區'),
('格奧爾格·馮·斯拉特科尼亞', 'Georg von Slatkonia', '維也納', '天主教', 5, 1513, 1522, '逝世', '皇帝馬克西米利安一世', '正統', 'Austrian Church History', '馬克西米利安一世宮廷音樂總監；文藝復興人文主義者；維也納宮廷文化推動者'),
('克里斯托夫·安東·馮·米加齊', 'Christoph Anton von Migazzi', '維也納', '天主教', 19, 1757, 1803, '逝世', '教宗本篤十四世', '正統', 'Catholic Hierarchy', '樞機；哈布斯堡啟蒙改革（約瑟夫主義Josephinism）下掙扎；反對馬利亞·特雷莎和約瑟夫二世教育改革；在任46年'),
('西格蒙德·恩斯特·馮·霍恩沃特', 'Sigmund von Hohenwart', '維也納', '天主教', 20, 1803, 1820, '逝世', '教宗庇護七世', '正統', 'Catholic Hierarchy', '拿破崙入侵奧地利期間；維持維也納教會秩序'),
('維也納文森特·爱德华·米尔第', 'Vincenz Eduard Milde', '維也納', '天主教', 21, 1832, 1853, '逝世', '教宗利奧十二世', '正統', 'Catholic Hierarchy', '1848年革命期間維也納大主教；積極推動天主教教育'),
('維也納歷史上首位樞機大主教', 'Joseph Othmar von Rauscher', '維也納', '天主教', 22, 1853, 1875, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '樞機；1855年奧地利-教廷協定談判者；梵一大公會議（1870）期間反對教宗不可錯誤定義（但最終服從）'),
('卡什帕爾·雷姆斯基', 'Cašpar Remigius Stölberg', '維也納', '天主教', 23, 1875, 1881, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '短暫在任；奧匈帝國全盛期'),
('科洛曼·斯特勞爾', 'Cölestin Josef Ganglbauer', '維也納', '天主教', 24, 1881, 1889, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '本篤會大主教；奧地利天主教社會運動'),
('安東·約瑟夫·蒙地格林', 'Anton Josef Gruscha', '維也納', '天主教', 25, 1890, 1911, '逝世', '教宗利奧十三世', '正統', 'Catholic Hierarchy', '樞機；奧匈帝國晚期；天主教社會黨支持者'),
('弗里德里希·古斯塔夫·皮夫爾', 'Friedrich Gustav Piffl', '維也納', '天主教', 26, 1913, 1932, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；一戰期間；奧地利共和國建立（1918）後的天主教政治重建'),
('泰奧多爾·因尼策爾', 'Theodor Innitzer', '維也納', '天主教', 27, 1932, 1955, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；1938年奧地利並入納粹德國（Anschluss）後初步合作，後遭納粹攻擊主教府（1938年10月）而轉為抵抗；教宗庇護十二世警告其「不要捲入政治」'),
('弗朗茨·科尼希', 'Franz König', '維也納', '天主教', 28, 1956, 1985, '退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議影響力人物（促成若望二十三世召開）；東西方橋梁——與東歐共產國家天主教會的秘密外交；推動若望保祿二世當選（1978）'),
('漢斯·赫爾曼·格羅爾', 'Hans Hermann Groër', '維也納', '天主教', 29, 1986, 1995, '退休（醜聞）', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；性醜聞後辭職（被指控對修士性騷擾）；奧地利教會最嚴重的信任危機'),
('克里斯托夫·舍恩博恩', 'Christoph Schönborn', '維也納', '天主教', 30, 1995, NULL, NULL, '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；格羅爾醜聞後重建；天主教教理（Catechism）主要編輯者；《愛的喜樂》（Amoris Laetitia）的積極詮釋者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '維也納' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 華沙（Warsaw）
-- 波蘭現任首都大主教；1798年設立
-- ==============================
('卡斯帕爾·科薩科夫斯基', 'Kasper Józef Kazimierz Cieciszewski', '華沙', '天主教', 1, 1798, 1806, '逝世', '教宗庇護六世', '正統', 'Catholic Hierarchy', '1798年華沙設立大主教區；波蘭瓜分後在普魯士統治下的波蘭中心'),
('皮奧特爾·帕夫·沃倫斯基', 'Piotr Paweł Woronicz', '華沙', '天主教', 4, 1828, 1829, '逝世', '教宗利奧十二世', '正統', 'Catholic Hierarchy', '波蘭浪漫主義詩人兼主教；波蘭十一月起義（1830–1831）前夕'),
('弗費利克斯·萊維茨基', 'Feliks Lewicki', '華沙', '天主教', 8, 1863, 1895, '逝世', '教宗庇護九世', '正統', 'Catholic Hierarchy', '1863年一月起義後俄羅斯帝國迫害波蘭天主教時期；維持教會存在'),
('斯坦尼斯瓦夫·福爾比茨基', 'Aleksander Kakowski', '華沙', '天主教', 12, 1913, 1938, '逝世', '教宗庇護十世', '正統', 'Catholic Hierarchy', '樞機；一戰期間波蘭獨立復國（1918）的宗教支柱；波蘭第二共和國首席樞機'),
('斯特凡·沙皮哈', 'Adam Stefan Sapieha', '華沙', '天主教', 13, 1939, 1951, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；克拉科夫大主教（詳見克拉科夫條目）；同時在克拉科夫；二戰時保護猶太人及抵抗軍；庇護年輕的卡羅爾·沃伊提瓦（後為若望保祿二世）'),
('波勒斯瓦夫·科米內克', 'Stefan Wyszyński', '華沙', '天主教', 14, 1948, 1981, '逝世', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；1953–1956年被共產政府監禁；被稱為「千年首席大主教」（Prymas Tysiąclecia）；獲釋後以「小步走」策略維護教會；若望保祿二世當選後的主要支持者；2021年真福品'),
('若澤夫·格萊普', 'Józef Glemp', '華沙', '天主教', 15, 1981, 2006, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；波蘭團結工會（Solidarność）時代；1981年戒嚴法時調停角色；處理教會-猶太關係的奧斯維辛十字架爭議（1998）'),
('卡齊米日·尼茨', 'Kazimierz Nycz', '華沙', '天主教', 16, 2007, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；波蘭教會的現代化推動者；若望保祿二世紀念館推動者');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '華沙' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 克拉科夫（Kraków）
-- 波蘭歷史首都；若望保祿二世曾任大主教
-- ==============================
('聖斯坦尼斯瓦夫', 'Saint Stanislaus of Kraków', '克拉科夫', '天主教', 2, 1072, 1079, '殉道', '教宗亞歷山大二世', '正統', 'Vita Sancti Stanislai; Dlugosz', '被國王波勒斯瓦夫二世刺殺（1079）；1253年封聖；波蘭主保聖人；被視為波蘭國家統一的象徵'),
('文采斯勞斯·比斯庫帕', 'Wincenty Kadłubek', '克拉科夫', '天主教', 10, 1208, 1218, '退休（入修道院）', '教宗英諾森三世', '正統', 'Chronica Polonorum', '波蘭歷史學家（《波蘭編年史》作者）；主動退休進入西篤會；1764年真福品'),
('斯比格涅夫·奧列希尼茨基', 'Zbigniew Oleśnicki', '克拉科夫', '天主教', 26, 1423, 1455, '逝世', '教宗馬丁五世', '正統', 'Polish historiography; Dlugosz', '波蘭第一位樞機（1449年）；十五世紀波蘭政治的核心人物；與瓦迪斯瓦夫三世的政策分歧'),
('菲奧爾·西格蒙特三世', 'Jan Łaski the Elder (Archbishop of Gniezno)', '克拉科夫', '天主教', 33, 1503, 1513, '轉任至格涅茲諾', '教宗亞歷山大六世', '正統', 'Polish historiography', '見格涅茲諾大主教條目；重要法律改革者'),
('彼得·戈金斯基', 'Piotr Gamrat', '克拉科夫', '天主教', 35, 1538, 1545, '逝世', '教宗保羅三世', '正統', 'Catholic Hierarchy', '人文主義者；西吉斯蒙德一世時代波蘭文藝復興；同時兼任格涅茲諾大主教'),
('卡齊米日·鲁孔斯基', 'Kazimierz Łubieński', '克拉科夫', '天主教', 47, 1710, 1719, '逝世', '教宗克萊孟十一世', '正統', 'Catholic Hierarchy', '波蘭王位繼承戰爭（1701–1721）期間；薩克森-波蘭聯合時代'),
('卡羅爾·沃伊提瓦（後為若望保祿二世）', 'Karol Wojtyła (later Pope John Paul II)', '克拉科夫', '天主教', 63, 1964, 1978, '辭職（就任教宗）', '教宗保羅六世', '正統', 'Catholic Hierarchy', '1964年任大主教；1967年任樞機；1978年當選教宗若望保祿二世——首位斯拉夫裔、首位非義大利裔現代教宗（455年來）；梵二大公會議積極參與者'),
('弗蘭西謝克·馬歇爾斯基', 'Franciszek Macharski', '克拉科夫', '天主教', 64, 1979, 2005, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；奧斯維辛十字架爭議處理；波蘭轉型時期（1989）教會角色'),
('斯坦尼斯瓦夫·季維斯茨', 'Stanisław Dziwisz', '克拉科夫', '天主教', 65, 2005, 2016, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；若望保祿二世的私人秘書長達39年；接掌克拉科夫傳達師承'),
('馬雷克·耶德拉謝夫斯基', 'Marek Jędraszewski', '克拉科夫', '天主教', 66, 2017, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '保守立場；波蘭教會-政治關係爭議中的強硬聲音；「LGBT意識形態」爭議言論引發廣泛批評');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '克拉科夫' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
