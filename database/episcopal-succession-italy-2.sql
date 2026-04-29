-- ============================================================
-- 天主教大主教傳承——義大利（威尼斯、佛羅倫薩、波隆那、那不勒斯）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 威尼斯（Venice）宗主教
-- 1451年設立；三位宗主教後成教宗
-- ==============================
('聖洛倫佐·吉烏斯蒂尼亞尼', 'Lorenzo Giustiniani', '威尼斯', '天主教', 1, 1451, 1456, '逝世', '教宗尼古拉五世', '正統', 'Catholic Hierarchy; Noonan', '威尼斯首任宗主教（1451年升格）；以禁欲苦修聞名；1690年封聖'),
('貝薩里昂（流亡君士坦丁堡宗主教）', 'Bessarion of Nicaea (titular)', '威尼斯', '天主教', 2, 1459, 1472, '逝世', '教宗庇護二世', '正統', 'Catholic Hierarchy', '拜占廷移民樞機；東西方合一推動者；偉大人文主義者；將希臘文稿帶至威尼斯——啟迪西方人文主義'),
('安東尼奧·米耶爾', 'Antonio Contarini', '威尼斯', '天主教', 4, 1497, 1508, '逝世', '教宗亞歷山大六世', '正統', 'Catholic Hierarchy', '威尼斯政治與教會的交織；意大利戰爭期間'),
('喬萬尼·格里馬尼', 'Giovanni Grimani', '威尼斯', '天主教', 9, 1546, 1593, '逝世', '教宗保羅三世', '正統', 'Catholic Hierarchy', '樞機；在位47年；異端嫌疑案（1551）；偉大的藝術贊助人；後提前解除職務接受調查'),
('費德里科·康納羅', 'Federico Corner (Cornaro)', '威尼斯', '天主教', 16, 1631, 1645, '逝世', '教宗烏爾班八世', '正統', 'Catholic Hierarchy', '貝尼尼為其創作《聖特蕾莎的狂喜》——非在威尼斯但為其家族；反宗教改革時代'),
('安傑洛·朱賽佩·龍卡利（後為若望二十三世）', 'Angelo Giuseppe Roncalli (later Pope John XXIII)', '威尼斯', '天主教', 34, 1953, 1958, '辭職（就任教宗）', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '外交官型宗主教；1958年當選教宗若望二十三世——召開梵二大公會議（1962–1965）；「仁慈教宗」'),
('喬萬尼·烏爾巴尼', 'Giovanni Urbani', '威尼斯', '天主教', 35, 1958, 1969, '逝世', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議參與者'),
('阿爾比諾·盧恰尼（後為若望保祿一世）', 'Albino Luciani (later Pope John Paul I)', '威尼斯', '天主教', 36, 1969, 1978, '辭職（就任教宗）', '教宗保羅六世', '正統', 'Catholic Hierarchy', '1978年當選教宗若望保祿一世——在任33天後猝死；以溫馨簡單的演講風格著稱；「微笑教宗」；2022年真福品'),
('馬爾科·賽', 'Marco Cé', '威尼斯', '天主教', 37, 1978, 2002, '退休', '教宗若望保祿一世', '正統', 'Catholic Hierarchy', '樞機；第三位連任宗主教後未成教宗；梵二後牧靈改革'),
('安傑洛·斯柯拉', 'Angelo Scola', '威尼斯', '天主教', 38, 2002, 2011, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後轉任米蘭；2013年為有力的教宗候選人'),
('弗朗切斯科·莫拉利亞', 'Francesco Moraglia', '威尼斯', '天主教', 39, 2012, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '現任宗主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '威尼斯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 佛羅倫薩（Florence）
-- 文藝復興中心；薩伏那羅拉時代
-- ==============================
('聖澤諾比烏斯', 'Saint Zenobius of Florence', '佛羅倫薩', '天主教', 4, 390, 417, '逝世', '教宗達瑪索一世', '正統', 'AA SS May vol.4; Gallia Christiana', '佛羅倫薩第一位本地主教；聖人；佛羅倫薩的主保聖人；奧古斯丁時代的神學家'),
('聖安托尼諾（安東尼·皮埃羅齊）', 'Antoninus (Antonino Pierozzi)', '佛羅倫薩', '天主教', 14, 1446, 1459, '逝世', '教宗尤金尼烏斯四世', '正統', 'Catholic Hierarchy; DSB', '多明我會士；以清廉簡樸著名；精通法律與神學；1523年封聖；梅迪奇家族的朋友'),
('朱利奧·德·梅迪奇（後為克萊孟七世）', 'Giulio de'' Medici (later Pope Clement VII)', '佛羅倫薩', '天主教', 18, 1513, 1523, '辭職（就任教宗）', '教宗利奧十世（其堂兄）', '正統', 'Catholic Hierarchy', '梅迪奇家族；1527年羅馬之劫（Sacco di Roma）期間的教宗'),
('喬萬尼·薩爾維亞蒂', 'Giovanni Salviati', '佛羅倫薩', '天主教', 19, 1523, 1543, '逝世', '教宗克萊孟七世', '正統', 'Catholic Hierarchy', '樞機；梅迪奇時代的政治主教'),
('皮埃爾·弗朗切斯科·里奇', 'Pietro Carnesecchi', '佛羅倫薩', '天主教', 22, 1550, 1552, '轉任', '教宗尤利烏斯三世', '爭議', 'Catholic Hierarchy', '後因異端被火刑處死（1567）'),
('路易斯·德·托雷多', 'Alessandro Ottaviano de'' Medici (later Pope Leo XI)', '佛羅倫薩', '天主教', 27, 1574, 1605, '辭職（就任教宗）', '教宗額我略十三世', '正統', 'Catholic Hierarchy', '1605年短暫成為教宗利奧十一世（在位27天）'),
('阿方索·利貝拉托勒', 'Alessandro Marzi Medici', '佛羅倫薩', '天主教', 28, 1605, 1630, '逝世', '教宗保羅五世', '正統', 'Catholic Hierarchy', '黑死病（1630）期間牧養佛羅倫薩'),
('若望·弗朗切斯科·德·薩萊斯（受命）', 'Charles de Noailles', '佛羅倫薩', '天主教', 35, 1706, 1730, '逝世', '教宗克萊孟十一世', '正統', 'Catholic Hierarchy', '啟蒙時代佛羅倫薩；梅迪奇家族末年（最後一位梅迪奇大公1737年絕嗣）'),
('恩里科·斯圖里納', 'Elia Dalla Costa', '佛羅倫薩', '天主教', 53, 1931, 1961, '退休', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；二戰期間（1943–1945）庇護猶太人——「佛羅倫薩的義人」；2012年被以色列承認為義人（Righteous Among Nations）'),
('若望·弗羅倫薩的班比尼', 'Ermenegildo Florit', '佛羅倫薩', '天主教', 54, 1962, 1977, '退休', '教宗若望二十三世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議積極參與者'),
('喬萬尼·貝内利', 'Giovanni Benelli', '佛羅倫薩', '天主教', 55, 1977, 1982, '逝世', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；1978年最有力的教宗候選人之一；保羅六世的親密助手'),
('西爾瓦諾·皮奧瓦內利', 'Silvano Piovanelli', '佛羅倫薩', '天主教', 56, 1983, 2001, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機'),
('埃諾·安托內利', 'Ennio Antonelli', '佛羅倫薩', '天主教', 57, 2001, 2008, '轉任', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；後任聖座家庭委員會主席'),
('喬治奧·貝托里', 'Giorgio Betori', '佛羅倫薩', '天主教', 58, 2008, NULL, NULL, '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；現任佛羅倫薩大主教');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '佛羅倫薩' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 波隆那（Bologna）
-- 最古老大學所在地；多位主教後登教宗
-- ==============================
('聖扎馬', 'Saint Zama', '波隆那', '天主教', 1, 290, 298, '逝世', '使徒傳承', '正統', 'Catholic Hierarchy', '波隆那首任主教；傳統上由聖彼得派遣'),
('尼科洛·阿爾貝爾加蒂', 'Niccolò Albergati', '波隆那', '天主教', 20, 1417, 1443, '逝世', '教宗馬丁五世', '正統', 'Catholic Hierarchy; Laude', '加爾都西會士；波隆那最受愛戴的主教之一；范·艾克曾為其繪像；1744年真福品'),
('賈科莫·本蒂沃利奧', 'Giacomo Bentivolio', '波隆那', '天主教', 24, 1466, 1508, '驅逐', '教宗保羅二世', '正統', 'Catholic Hierarchy', '本蒂沃利奧家族（波隆那君主）的主教；1506年尤利烏斯二世收復波隆那後流亡'),
('尤利烏斯二世（曾任）', 'Giuliano della Rovere (later Pope Julius II)', '波隆那', '天主教', 22, 1483, 1502, '辭職（就任教宗）', '教宗西斯都四世（其舅）', '正統', 'Catholic Hierarchy', '1503年成為教宗尤利烏斯二世；「戰士教宗」；委托米開朗基羅繪西斯廷禮拜堂天頂'),
('卡洛·博羅美奧（輔理）', 'Gabriele Paleotti', '波隆那', '天主教', 33, 1566, 1597, '逝世', '教宗庇護四世', '正統', 'Catholic Hierarchy', '特倫托大公會議祕書；反宗教改革主要推手；《圖像論》（Discorso intorno alle imagini, 1582）奠定天主教藝術理論'),
('奧多阿爾多·法爾內塞', 'Giambattista Pamphilj (later Pope Innocent X)', '波隆那', '天主教', 35, 1627, 1629, '轉任', '教宗烏爾班八世', '正統', 'Catholic Hierarchy', '1644年成為教宗英諾森十世；委托貝尼尼創作《四河噴泉》'),
('喬萬尼·巴蒂斯塔·蘭貝爾蒂尼（後為本篤十四世）', 'Giovanni Battista Lambertini (later Pope Benedict XIV)', '波隆那', '天主教', 40, 1731, 1740, '辭職（就任教宗）', '教宗克萊孟十二世', '正統', 'Catholic Hierarchy', '1740年當選教宗本篤十四世——啟蒙時代最偉大的教宗；學者型教宗；封聖程序改革；波隆那的驕傲'),
('賈科莫·萊爾卡羅', 'Giacomo Lercaro', '波隆那', '天主教', 54, 1952, 1968, '強制退休', '教宗庇護十二世', '正統', 'Catholic Hierarchy', '樞機；梵二大公會議最具影響力的主教之一；推動禮儀改革；因反對越戰（1968年要求停止轟炸）被保羅六世強制退休——極少見的教宗干預'),
('賈科莫·比菲', 'Giacomo Biffi', '波隆那', '天主教', 57, 1984, 2003, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；保守立場；批評伊斯蘭移民影響歐洲基督教文化；詩人暨神學家'),
('卡洛·卡法拉', 'Carlo Caffarra', '波隆那', '天主教', 58, 2003, 2015, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；家庭神學中心創辦人（若望保祿二世欽點）；《愛的喜樂》（Amoris Laetitia）「五疑問」（Dubia）發起人之一；保守神學立場'),
('馬泰奧·祖皮', 'Matteo Zuppi', '波隆那', '天主教', 59, 2015, NULL, NULL, '教宗方濟各', '正統', 'Catholic Hierarchy', '樞機；聖依沃社區（Sant''Egidio）成員；烏克蘭和談特使（2023–）；進步牧靈立場');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '波隆那' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 那不勒斯（Naples）
-- 義大利南部最大主教座
-- ==============================
('聖亞格里科拉', 'Saint Agrippinus', '那不勒斯', '天主教', 1, 174, 194, '逝世', '使徒傳承', '正統', 'Catholic Hierarchy', '那不勒斯首任主教；傳統上也是主保聖人之一'),
('聖真納羅（傑納羅）', 'Saint Januarius (Gennaro)', '那不勒斯', '天主教', 0, 303, 305, '殉道', NULL, '正統', 'Catholic Hierarchy; Butler''s Lives', '貝內文托主教（非那不勒斯主教）；305年在波佐利被斬首；那不勒斯的主保聖人；其血液每年液化——一大奇蹟'),
('奧利維埃羅·卡拉法', 'Oliviero Carafa', '那不勒斯', '天主教', 38, 1458, 1484, '轉任', '教宗庇護二世', '正統', 'Catholic Hierarchy', '樞機；人文主義藝術贊助人；羅馬的卡拉法禮拜堂（Carafa Chapel）贊助者；推動那不勒斯王國的反土耳其同盟'),
('吉羅拉莫·塞里潘多', 'Girolamo Seripando', '那不勒斯', '天主教', 51, 1554, 1563, '逝世（會議中）', '教宗尤利烏斯三世', '正統', 'Catholic Hierarchy', '奧古斯丁會總會長；特倫托大公會議樞機代表；在路德宗改革壓力下尋求中道；1563年會議期間逝於特倫托'),
('英尼科·卡拉奇奧洛', 'Innico Caracciolo', '那不勒斯', '天主教', 60, 1703, 1730, '逝世', '教宗克萊孟十一世', '正統', 'Catholic Hierarchy', '樞機；西班牙王位繼承戰爭（1701–1714）期間；奧地利佔領那不勒斯'),
('西斯托·里亞里奧·斯福爾扎', 'Sisto Riario Sforza', '那不勒斯', '天主教', 71, 1845, 1877, '逝世', '教宗額我略十六世', '正統', 'Catholic Hierarchy', '樞機；義大利統一（Risorgimento）浪潮中堅定反對；1860年加里波底進入那不勒斯；波旁王朝終結'),
('亞歷希奧·阿斯卡萊西', 'Alessio Ascalesi', '那不勒斯', '天主教', 76, 1924, 1952, '逝世', '教宗庇護十一世', '正統', 'Catholic Hierarchy', '樞機；法西斯時代；二戰盟軍解放那不勒斯（1943）'),
('科拉多·烏爾西', 'Corrado Ursi', '那不勒斯', '天主教', 79, 1966, 1987, '退休', '教宗保羅六世', '正統', 'Catholic Hierarchy', '樞機；梵二後改革；那不勒斯社會問題（卡莫拉、貧困）'),
('米凱萊·吉奧爾達諾', 'Michele Giordano', '那不勒斯', '天主教', 80, 1987, 2006, '退休', '教宗若望保祿二世', '正統', 'Catholic Hierarchy', '樞機；反卡莫拉立場；2000年禧年'),
('克雷申齊奧·塞佩', 'Crescenzio Sepe', '那不勒斯', '天主教', 81, 2006, 2020, '退休', '教宗本篤十六世', '正統', 'Catholic Hierarchy', '樞機；曾任聖座萬民福音部部長'),
('多梅尼科·巴塔利亞', 'Domenico Battaglia', '那不勒斯', '天主教', 82, 2020, NULL, NULL, '教宗方濟각', '正統', 'Catholic Hierarchy', '以社會邊緣人（流浪者、毒品成癮者）服務著稱；方濟各型牧靈風格');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '那不勒斯' AND church = '天主教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
