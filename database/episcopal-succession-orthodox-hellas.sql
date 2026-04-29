-- ============================================================
-- 東正教主教傳承——希臘正教會都主教座
-- 帕特雷、科林斯、帖撒洛尼迦
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 帕特雷都主教（Church of Greece）
-- 使徒安得烈殉道地；1821年獨立戰爭起點
-- ==============================
('安得烈使徒', 'Andrew the Apostle', '帕特雷', '東正教', 1, 50, 68, '殉道', '主耶穌基督', '正統', 'Orthodox Martyrologium; Menologion', '傳統帕特雷使徒性創始人；被釘於X形（聖安得烈）十字架殉道——X形十字架成為蘇格蘭國旗圖案；1462年遺骨被帶往羅馬；1964年教宗保羅六世將遺骨歸還帕特雷，是東西方合一的象徵性姿態'),
('斯特拉提基奧斯', 'Stratikios', '帕特雷', '東正教', 4, 150, 175, '逝世', '教會', '正統', 'Menologion', '使徒後繼時代；帕特雷基督教社群鞏固期'),
('赫羅德斯', 'Herodes of Patras', '帕特雷', '東正教', 8, 250, 268, '殉道', '教會', '正統', 'Martyrologium', '德西烏斯/瓦勒良迫害期間殉道；帕特雷早期殉道者'),
('馬克西莫斯', 'Maximos of Patras', '帕特雷', '東正教', 15, 325, 350, '逝世', '教會', '正統', 'Byzantine records', '尼西亞信仰的維護者；帕特雷地區抵制阿里烏斯主義'),
('克里松托斯', 'Khrysanthos', '帕特雷', '東正教', 22, 530, 560, '逝世', '拜占廷皇帝', '正統', 'Byzantine Menologion', '查士丁尼時代；帕特雷教堂建設；安得烈聖地保護'),
('帕特羅克勒斯', 'Patrokles', '帕特雷', '東正教', 31, 787, 815, '逝世', '拜占廷教會', '正統', 'Byzantine records', '第二次尼西亞大公會議（787年）參與者；反對聖像破壞主義'),
('阿爾謝尼奧斯', 'Arsenios of Patras', '帕特雷', '東正教', 45, 1098, 1121, '逝世', '拜占廷皇帝', '正統', 'Byzantine records', '塞爾柱突厥入侵後的教會重組；第一次十字軍東征（1099年）期間'),
('傑拉西莫斯', 'Gerasimos', '帕特雷', '東正教', 52, 1430, 1460, '逝世', '教會', '正統', 'Venetian records', '1430年鄂圖曼征服伯羅奔尼撒前後；教會在威尼斯人與奧斯曼人夾縫中存續'),
('傑爾瑪諾斯四世', 'Germanos of Patras', '帕特雷', '東正教', 62, 1819, 1826, '逝世', '鄂圖曼管轄下教會', '正統', 'Greek Revolution records; Church of Greece', '1821年3月25日在卡拉夫里塔聖拉夫拉修道院（Agia Lavra）升起獨立旗幟，宣布希臘獨立戰爭——此時此地成為希臘現代民族史的誕生點；主教鐘聲與革命號角合一；後世公認為民族英雄，現代希臘聖誕節與獨立日同日紀念'),
('聶克塔里奧斯', 'Nektarios', '帕特雷', '東正教', 65, 1856, 1888, '逝世', '希臘正教會聖主教會議', '正統', 'Church of Greece', '帕特雷在19世紀後半的鞏固期；安得烈使徒聖地朝聖活動復興'),
('克里索斯托莫斯一世', 'Chrysostomos I', '帕特雷', '東正教', 68, 1902, 1934, '退休', '希臘正教會聖主教會議', '正統', 'Church of Greece', '1912-1913年巴爾幹戰爭後希臘領土擴張時期；帕特雷港口城市的天主教、新教與正教共存'),
('尼科迪莫斯·瓦林德拉斯', 'Nikodimos Vallindras', '帕特雷', '東正教', 72, 1971, 2004, '退休', '希臘正教會聖主教會議', '正統', 'Church of Greece', '帕特雷聖安得烈大聖堂（1974年奠基，1979年落成）建設的監督者；聖堂收藏安得烈使徒頭顱遺骨（自1964年教宗保羅六世歸還）；大聖堂是希臘正教最大教堂之一'),
('克里索斯托莫斯·卡蘭佐斯', 'Chrysostomos Kalantzes', '帕特雷', '東正教', 73, 2004, NULL, NULL, '希臘正教會聖主教會議', '正統', 'Church of Greece', '當代在任都主教；聖安得烈聖地守護者；帕特雷聖安得烈大聖堂每年11月30日安得烈節的龐大朝聖活動主持人');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '帕特雷' AND church = '東正教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 科林斯都主教（Church of Greece）
-- 保羅書信受信教會；古代希臘文化中心
-- ==============================
('索斯提尼', 'Sosthenes', '科林斯', '東正教', 1, 55, 72, '逝世', '使徒保羅', '正統', '林前1:1; Acts 18:17', '哥林多前書共同作者（保羅與「兄弟索斯提尼」聯名）；原為猶太會堂管理員（徒18:17）；後成為保羅同工；傳統科林斯首任主教'),
('狄奧尼修斯', 'Dionysius of Corinth', '科林斯', '東正教', 4, 168, 180, '逝世', '教會', '正統', 'Eusebius HE IV.23', '科林斯最著名的古代主教；致各教會書信集被尤西比烏（Eusebius）大量保存引用；強調使徒傳承、教義正確性，批評抄改聖經文本；確立哥林多與羅馬的緊密聯繫'),
('普里莫斯', 'Primus', '科林斯', '東正教', 5, 180, 200, '逝世', '教會', '正統', 'Hegesippus (via Eusebius)', '赫革西普（Hegesippus）訪問時的在任主教；尤西比烏記錄他為教義正確的繼承者'),
('巴庫盧斯', 'Bacchylus', '科林斯', '東正教', 6, 200, 218, '逝世', '教會', '正統', 'Eusebius HE V.22-23', '逾越節（復活節）日期爭論的關鍵主教；支持羅馬傳統（主日慶祝復活節）而非亞洲傳統（尼散月十四日）；為東西方教會統一立場'),
('亞歷山大', 'Alexander of Corinth', '科林斯', '東正教', 12, 315, 340, '逝世', '教會', '正統', 'Sozomen', '尼西亞大公會議（325年）參與者；確立尼西亞信經在科林斯的正統地位'),
('以弗拉坦', 'Ephrataios', '科林斯', '東正教', 22, 451, 470, '逝世', '拜占廷帝國', '正統', 'Council records', '卡爾西頓大公會議（451年）後的正統信仰實施；科林斯在希臘的教義監管地位'),
('聖尼康', 'Nikōn of Sparta', '科林斯', '東正教', 48, 962, 998, '逝世', '拜占廷教會', '正統', 'Nicaea-Patras synod records', '薩拉森（阿拉伯）入侵後的科林斯重建；拜占廷反攻時代；聖尼康（「懺悔者」）在此地區傳教的同代人'),
('利奧·庫葛拉斯', 'Leo Kugralas', '科林斯', '東正教', 56, 1204, 1219, '流亡', '拉丁（十字軍）', '爭議', 'Venetian records', '1204年第四次十字軍東征後；拉丁帝國在科林斯設拉丁大主教；正統主教流亡；史稱科林斯天主教大主教管轄期（1210-1395年威尼斯控制）'),
('帕科米奧斯', 'Pachomios', '科林斯', '東正教', 64, 1520, 1550, '逝世', '鄂圖曼管轄下教會', '正統', 'Ottoman church records', '鄂圖曼統治下的科林斯教會維持；希臘民族認同的宗教保存機構'),
('阿吉奧斯', 'Agios', '科林斯', '東正教', 73, 1830, 1855, '逝世', '希臘正教會聖主教會議', '正統', 'Church of Greece', '希臘獨立後科林斯教區正式恢復（1821-1830年戰爭後）；都主教座在科林斯古城（科林斯舊城Archaia Korinthos附近）'),
('狄奧尼修斯', 'Dionysios of Corinth', '科林斯', '東正教', 81, 1977, NULL, NULL, '希臘正教會聖主教會議', '正統', 'Church of Greece', '當代在任都主教；保羅書信考古現場（科林斯集市、比馬石台）的朝聖守護者；每年保羅節慶（6月29日）主持');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '科林斯' AND church = '東正教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 帖撒洛尼迦都主教（Church of Greece，1913年後行政管轄）
-- 保羅書信受信教會；拜占廷帝國西部重鎮；1913年從鄂圖曼解放
-- ==============================
('阿里斯塔克斯', 'Aristarchus of Thessaloniki', '帖撒洛尼迦正教', '東正教', 1, 51, 75, '殉道', '使徒保羅', '正統', 'Acts 27:2; Col 4:10; Philemon 24', '保羅同工；陪同保羅前往羅馬的旅伴（徒27:2）；歌羅西書4:10稱「與我一同坐監的亞里達古」；腓利門書第24節同列「同工」；傳統帖撒洛尼迦首任主教，後在羅馬殉道'),
('塞昆都斯', 'Secundus of Thessaloniki', '帖撒洛尼迦正教', '東正教', 2, 52, 80, '逝世', '使徒保羅', '正統', 'Acts 20:4', '保羅第三次宣教旅程同行者（徒20:4）；帖撒洛尼迦教會的早期鞏固者'),
('奧涅西姆', 'Onesimos', '帖撒洛尼迦正教', '東正教', 3, 80, 110, '殉道', '教會', '正統', 'Menologion', '傳統使徒後繼者；帖撒洛尼迦基督徒共同體早期組織者'),
('亞歷山大一世', 'Alexander I', '帖撒洛尼迦正教', '東正教', 10, 314, 340, '逝世', '教會', '正統', 'Council records', '米蘭詔書（313年）後帖撒洛尼迦教會的公開發展；君士坦丁帝國境內'),
('阿斯科利烏斯', 'Askolius', '帖撒洛尼迦正教', '東正教', 12, 380, 395, '逝世', '羅馬皇帝', '正統', 'Theodoret; Sozomen', '380年帖撒洛尼迦詔令（Edict of Thessaloniki）發布地——狄奧多西烏斯一世在此確立尼西亞信仰為羅馬帝國唯一正統；亞斯科利烏斯見證此歷史時刻；參加君士坦丁堡大公會議（381年）'),
('安菲洛修斯', 'Amphilochios', '帖撒洛尼迦正教', '東正教', 20, 450, 472, '逝世', '拜占廷帝國', '正統', 'Byzantine records', '5世紀伊里里亞教省行政爭議：帖撒洛尼迦先後作為羅馬代牧區（Rome''s vicariate）和君士坦丁堡的轄地；安菲洛修斯時代是羅馬-君士坦丁堡關係緊張的前線'),
('約翰一世', 'John I', '帖撒洛尼迦正教', '東正教', 35, 602, 625, '逝世', '拜占廷皇帝', '正統', 'Byzantine records', '斯拉夫人和阿瓦爾人圍攻帖撒洛尼迦時代（586、597年）；城市守護聖人狄米特里奧斯（Demetrios）信仰高峰；奇蹟傳說大量產生'),
('基里爾（西里爾）與美多德在此出生', 'Cyril and Methodius (birthplace)', '帖撒洛尼迦正教', '東正教', 0, 826, 826, NULL, NULL, '正統', 'Vita Cyrilli; Vita Methodii', '注：西里爾（康斯坦丁，826/827年）和美多德（815年）生於帖撒洛尼迦；父親利奧是拜占廷軍官；他們後來受命赴大摩拉維亞傳教，創制格拉哥里字母（後演化為西里爾字母）——斯拉夫世界書寫文化的奠基'),
('格雷戈里奧斯·帕拉馬斯', 'Gregory Palamas', '帖撒洛尼迦正教', '東正教', 55, 1347, 1359, '逝世', '拜占廷皇帝', '正統', 'Byzantine Hagiography', '東正教神學最偉大的代表之一；發展「神聖光芒」（塔博爾山光：Tabor Light）和「神能」（energies）神學——帕拉馬斯主義（Palamism）；1368年正式列聖；其神學是東西方教會分裂的重要神學背景；帖撒洛尼迦大教堂（Hagia Sophia）至今供奉其遺骨'),
('傑納迪奧斯·亞歷克謝亞狄斯', 'Gennadios Alexiades', '帖撒洛尼迦正教', '東正教', 62, 1912, 1951, '逝世', '普世牧首/希臘正教會聖主教會議', '正統', 'Church of Greece; Holocaust records', '帖撒洛尼迦解放（1912年10月26日）後首任在希臘管轄下的都主教；服務近40年——跨越第一次世界大戰、1922年人口交換（伊斯蘭穆斯林離開、希臘基督徒返回）、1941-1944年德國占領；1943年納粹德國驅逐帖撒洛尼迦猶太人（5萬人）至奧斯維辛——傑納迪奧斯的角色在歷史上存在爭議'),
('潘太利蒙一世·帕帕哲奧爾吉奧斯', 'Panteleimon I Papageorgiou', '帖撒洛尼迦正教', '東正教', 63, 1952, 1986, '退休', '希臘正教會聖主教會議', '正統', 'Church of Greece', '在任34年；戰後帖撒洛尼迦重建時代；軍政府（1967-1974）和民主恢復時期；帖撒洛尼迦從工業化城市向現代都會轉型'),
('潘太利蒙二世·克里佐芳尼季斯', 'Panteleimon II Chrysophanidis', '帖撒洛尼迦正教', '東正教', 64, 1986, 1995, '退休', '希臘正教會聖主教會議', '正統', 'Church of Greece', '冷戰結束後巴爾幹政治重組期；1991年南斯拉夫解體及北馬其頓「馬其頓名稱爭議」引發希臘民族情緒高漲，宗教認同政治化'),
('安提莫斯·亞歷克謝亞狄斯七世', 'Anthimos VII Alexandriadis', '帖撒洛尼迦正教', '東正教', 65, 1995, 2004, '免職', '希臘正教會聖主教會議', '爭議', 'Church of Greece; Greek courts', '2004年因公開仇恨言論（反猶太和反穆斯林言論）被希臘正教會聖主教會議免職；是希臘正教會現代史上罕見的免職案例；希臘正教民族主義與現代民主自由的衝突象徵'),
('潘太利蒙三世', 'Panteleimon III', '帖撒洛尼迦正教', '東正教', 66, 2004, NULL, NULL, '希臘正教會聖主教會議', '正統', 'Church of Greece', '當代在任都主教；帖撒洛尼迦聖狄米特里奧斯（Hagios Demetrios）大教堂的守護者；每年10月26日狄米特里奧斯節是全城最大的宗教慶典');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '帖撒洛尼迦正教' AND church = '東正教'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
