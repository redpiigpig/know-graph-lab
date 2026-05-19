-- ========================================================
-- Phase 4: 希臘正教重要缺漏教座
-- ========================================================
-- 諾夫哥羅德、弗拉基米爾、托博爾斯克、喀山、佩奇、奧赫里德古代、普雷斯拉夫、加沙、特拉布宗、赫爾松、波羅茨克
-- ========================================================

-- Parent see IDs:
--   君士坦丁堡        : cf932373-be6a-4fb2-a195-d26dc3045cba
--   莫斯科            : 847fb539-c37a-40af-ac7e-16631b63154e
--   塞爾維亞          : 34473a5f-77aa-469a-a693-b05636a4135c
--   保加利亞          : c0024ac9-fa07-4181-bb9a-da70240b1fb0
--   亞歷山卓 (EO)     : c2846527-462f-4299-a858-b63624ffbf00
--   耶路撒冷 (EO)     : d215f751-96d4-4902-8e43-1417e19fa793
--   基輔(莫斯科)      : 19fa1944-eb67-4e3b-878b-2b2db7b490d6


-- =============================================
-- 俄羅斯古老都主教座
-- =============================================

-- 諾夫哥羅德 (Novgorod) — 11C 起，俄第二大都主教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('諾夫哥羅德都主教座', 'Metropolis of Novgorod', '諾夫哥羅德', '俄羅斯正教會', '希臘正教', '拜占庭禮', 992, '現存', '19fa1944-eb67-4e3b-878b-2b2db7b490d6',
 '992 年立座，俄羅斯第二古老主教城；中世紀諾夫哥羅德共和國時期半自治；12 世紀起稱大主教 (Archbishop)、16 世紀起稱都主教。', 'Povest vremennykh let');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('約阿希姆·科爾遜尼揚', 'Joachim of Korsun', '諾夫哥羅德', '俄羅斯正教會', 1, 992, 1030, '正統', '羅斯往年紀事', '希臘人；諾夫哥羅德首任主教；伴隨弗拉基米爾大帝受洗'),
('盧卡·日德雅塔', 'Luka Zhydiata', '諾夫哥羅德', '俄羅斯正教會', 2, 1036, 1059, '正統', '羅斯往年紀事', '第一位本族 (East Slav) 主教'),
('馬卡里', 'Macarius of Novgorod', '諾夫哥羅德', '俄羅斯正教會', 3, 1526, 1542, '正統', 'Russian Orthodox archives', '後升莫斯科都主教 1542-1563；伊凡四世時期重要神職'),
('狄奧多西二世', 'Theodosius II', '諾夫哥羅德', '俄羅斯正教會', 4, 1542, 1551, '正統', 'Russian Orthodox archives', null),
('阿爾謝尼·馬采耶維奇', 'Arseny Matseyevich', '諾夫哥羅德', '俄羅斯正教會', 5, 1741, 1772, '正統', 'Russian Orthodox archives', '反對葉卡捷琳娜二世教會財產國有化；新殉道者');


-- 弗拉基米爾 (Vladimir) — 1299-1325 全俄都主教駐節地（基輔之後、莫斯科之前）
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('弗拉基米爾都主教座', 'Metropolis of Vladimir', '弗拉基米爾', '俄羅斯正教會', '希臘正教', '拜占庭禮', 1158, '現存', '19fa1944-eb67-4e3b-878b-2b2db7b490d6',
 '1158 年大公安德烈·博戈柳布斯基立；1299 年基輔受蒙古入侵後都主教座移此；1325 年再移莫斯科。', 'Russian Primary Chronicle');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬克西姆', 'Maximus of Kiev and Vladimir', '弗拉基米爾', '俄羅斯正教會', 1, 1299, 1305, '正統', 'Russian Primary Chronicle', '希臘人；1299 將基輔都主教座遷至弗拉基米爾'),
('彼得', 'Peter of Moscow', '弗拉基米爾', '俄羅斯正教會', 2, 1308, 1325, '正統', 'Russian Primary Chronicle; Vita Petri', '加里西亞人；1325 將都主教座遷至莫斯科；俄羅斯主保聖人之一；莫斯科興起的關鍵'),
('狄奧諾蒂', 'Theognostus of Kiev and All Russia', '弗拉基米爾', '俄羅斯正教會', 3, 1328, 1353, '正統', 'Russian Primary Chronicle', '希臘人；繼任後仍掛弗拉基米爾頭銜，實際駐莫斯科');


-- 托博爾斯克 (Tobolsk) — 1620 西伯利亞首座都主教
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('托博爾斯克都主教座', 'Metropolis of Tobolsk', '托博爾斯克', '俄羅斯正教會', '希臘正教', '拜占庭禮', 1620, '現存', '847fb539-c37a-40af-ac7e-16631b63154e',
 '1620 年沙皇米哈伊爾·羅曼諾夫立；西伯利亞、烏拉爾以東、太平洋、阿拉斯加傳教重要根據地；俄羅斯太平洋傳教皆出自此。', 'Russian Orthodox archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('基普里安', 'Kiprian Starorusenkov', '托博爾斯克', '俄羅斯正教會', 1, 1620, 1624, '正統', 'Russian Orthodox archives', '首任托博爾斯克大主教；西伯利亞傳教先驅'),
('科爾尼利', 'Cornelius of Tobolsk', '托博爾斯克', '俄羅斯正教會', 2, 1664, 1678, '正統', 'Russian Orthodox archives', null),
('菲洛費伊·萊辛斯基', 'Filofei Leshchinsky', '托博爾斯克', '俄羅斯正教會', 3, 1702, 1727, '正統', 'Russian Orthodox archives', '彼得大帝任命；向西伯利亞原住民傳教逾 4 萬人受洗'),
('保羅·科紐什凱維奇', 'Pavel Konyushkevich', '托博爾斯克', '俄羅斯正教會', 4, 1758, 1768, '正統', 'Russian Orthodox archives', '後與葉卡捷琳娜二世衝突被罷免');


-- 喀山 (Kazan) — 1555 伊凡四世征服後設立
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('喀山都主教座', 'Metropolis of Kazan', '喀山', '俄羅斯正教會', '希臘正教', '拜占庭禮', 1555, '現存', '847fb539-c37a-40af-ac7e-16631b63154e',
 '1552 伊凡四世征服喀山汗國後立；伏爾加流域、韃靼人、楚瓦什人傳教重要根據地；喀山聖母像即此教座供奉。', 'Russian Orthodox archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('古里·魯戈金', 'Guriy Rugotin', '喀山', '俄羅斯正教會', 1, 1555, 1563, '正統', 'Russian Orthodox archives', '首任喀山大主教；後封聖；對韃靼人寬鬆傳教'),
('赫爾摩根', 'Hermogenes of Moscow', '喀山', '俄羅斯正教會', 2, 1589, 1606, '正統', 'Russian Orthodox archives', '發現喀山聖母像 (1579)；後升莫斯科宗主教 1606-1612；混亂時代殉道者'),
('馬可', 'Marcellus', '喀山', '俄羅斯正教會', 3, 1690, 1698, '正統', 'Russian Orthodox archives', null);


-- =============================================
-- 巴爾幹正教傳統教座
-- =============================================

-- 佩奇 (Peć / Pejë) — 1219 第一塞爾維亞 Patriarchate
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('佩奇宗主教座', 'Patriarchate of Peć', '佩奇', '塞爾維亞正教會', '希臘正教', '拜占庭禮', 1219, '現存', '34473a5f-77aa-469a-a693-b05636a4135c',
 '1219 聖薩瓦建立塞爾維亞自主大主教座，駐紮 Žiča；1346 升宗主教；1766 鄂圖曼蘇丹廢除；1920 重建。', 'Domentijan, Život Svetoga Save');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('聖薩瓦', 'Saint Sava', '佩奇', '塞爾維亞正教會', 1, 1219, 1233, '正統', 'Domentijan, Život Svetoga Save', '塞爾維亞主保聖人；1219 在君堡尼西亞獲冊封為塞爾維亞首位大主教；建立 Hilandar 修道院'),
('阿森尼一世', 'Arsenije I Sremac', '佩奇', '塞爾維亞正教會', 2, 1233, 1263, '正統', '塞爾維亞教會檔案', '聖薩瓦的指定繼承人；1253 將駐節地遷至佩奇'),
('約阿尼基耶二世', 'Joanikije II', '佩奇', '塞爾維亞正教會', 3, 1338, 1354, '正統', 'Mavro Orbini, Il Regno degli Slavi', '1346 在沙皇杜尚加冕同日升任宗主教，第一任塞爾維亞宗主教'),
('馬卡里耶三世·索科洛維奇', 'Makarije III Sokolović', '佩奇', '塞爾維亞正教會', 4, 1557, 1571, '正統', 'Serbian Orthodox archives', '鄂圖曼大維齊爾穆罕默德·索科洛維奇之兄；1557 重建佩奇宗主教座'),
('阿森尼二世·切爾諾耶維奇', 'Arsenije III Crnojević', '佩奇', '塞爾維亞正教會', 5, 1674, 1690, '正統', 'Serbian Orthodox archives', '1690 大遷徙領導者；率塞族難民越過多瑙河入哈布斯堡領');


-- 奧赫里德 古代 patriarchate (1018-1767)
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('奧赫里德總主教座（古代）', 'Archbishopric of Ohrid (Ancient)', '奧赫里德古代', '希臘東正教（古代）', '希臘正教', '拜占庭禮', 1018, '已廢除', 'cf932373-be6a-4fb2-a195-d26dc3045cba',
 '1018 拜占庭巴西流二世征服第一保加利亞後立；自主大主教座地位由君堡承認；1767 鄂圖曼君士坦丁堡蘇丹廢除併入君堡。', 'Snegarov, History of the Ohrid Archbishopric');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('約安', 'John of Debar', '奧赫里德古代', '希臘東正教（古代）', 1, 1018, 1037, '正統', 'Snegarov', '首任奧赫里德大主教；保加利亞學派延續'),
('特奧菲拉克特', 'Theophylact of Ohrid', '奧赫里德古代', '希臘東正教（古代）', 2, 1078, 1107, '正統', 'Theophylact, Commentaries', '希臘人；著名《新約注釋》家；保留拜占庭希臘傳統'),
('德米特里·霍馬蒂安', 'Demetrios Chomatenos', '奧赫里德古代', '希臘東正教（古代）', 3, 1216, 1236, '正統', 'Chomatenos, Ponemata Diafora', '12-13C 重要拜占庭教會法學家'),
('普羅霍爾', 'Prochor of Ohrid', '奧赫里德古代', '希臘東正教（古代）', 4, 1525, 1550, '正統', 'Snegarov', null),
('阿提肯尼烏斯', 'Athanasius II', '奧赫里德古代', '希臘東正教（古代）', 5, 1758, 1767, '正統', 'Snegarov', '最後一任奧赫里德大主教；1767 教座被廢除');


-- 普雷斯拉夫 (Preslav) — 第一保加利亞 Patriarchate 駐節地
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('普雷斯拉夫宗主教座', 'Patriarchate of Preslav', '普雷斯拉夫', '保加利亞正教會', '希臘正教', '拜占庭禮', 893, '已廢除', 'c0024ac9-fa07-4181-bb9a-da70240b1fb0',
 '893 西緬大帝立保加利亞為帝國同時，將首都從 Pliska 遷至 Preslav；927 君堡承認其為宗主教；1018 拜占庭征服後廢除。', 'Zlatarski, History of the First Bulgarian Empire');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('利奧昆提烏斯', 'Leonty of Preslav', '普雷斯拉夫', '保加利亞正教會', 1, 927, 935, '正統', 'Zlatarski', '第一任保加利亞宗主教；927 與拜占庭簽訂宗主教位承認條約'),
('德米特里', 'Damian of Preslav', '普雷斯拉夫', '保加利亞正教會', 2, 970, 972, '正統', 'Zlatarski', null);


-- =============================================
-- 早期教父+小亞細亞重要教座
-- =============================================

-- 加沙 (Gaza) — Porphyry, 反異教重要人物
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('加沙主教座', 'Diocese of Gaza', '加沙', '未分裂教會', '希臘正教', '拜占庭禮', 200, '已廢除', 'd215f751-96d4-4902-8e43-1417e19fa793',
 '希臘城市加沙古老主教座；4-5 世紀波菲利主教在皇帝阿爾卡狄烏斯支持下拆毀馬納斯神廟，是晚古基督教化典範。', 'Mark the Deacon, Vita Porphyrii');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('波菲利', 'Porphyry of Gaza', '加沙', '未分裂教會', 1, 395, 420, '正統', 'Mark the Deacon, Vita Porphyrii', '修道士出身；402 在阿爾卡狄烏斯皇帝授權下拆毀加沙的馬納斯神廟；晚古基督教化典範人物'),
('馬可·迪雅各', 'Mark the Deacon of Gaza', '加沙', '未分裂教會', 2, 420, 421, '正統', 'Mark the Deacon, Vita Porphyrii', '波菲利之執事與傳記作者'),
('提莫修', 'Timothy of Gaza', '加沙', '未分裂教會', 3, 500, 530, '正統', 'Mansi VIII', null);


-- 特拉布宗 (Trebizond) — 帝國分裂後流亡 patriarchate
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('特拉布宗都主教座', 'Metropolis of Trebizond', '特拉布宗', '東正教', '希臘正教', '拜占庭禮', 350, '已廢除', 'cf932373-be6a-4fb2-a195-d26dc3045cba',
 '黑海南岸古老主教座；1204-1461 拜占庭分裂期間是 Trebizond 帝國的核心教會；1923 希土人口交換後成為名銜職位。', 'Bryer & Winfield, Byzantine Monuments of Pontos');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('阿摩尼亞斯', 'Athenodoros of Trebizond', '特拉布宗', '東正教', 1, 380, 400, '正統', 'Mansi', '4 世紀末特拉布宗主教'),
('喬治', 'George of Trebizond', '特拉布宗', '東正教', 2, 1437, 1486, '正統', 'Mansi', '1439 佛羅倫薩大公會議參與；拜占庭文藝復興時期重要學者'),
('克里斯托福洛斯', 'Christophoros of Trebizond', '特拉布宗', '東正教', 3, 1804, 1822, '正統', '希臘正教檔案', '希臘獨立戰爭時期主教');


-- 赫爾松 (Cherson / Crimea) — 9C 拜占庭斯拉夫傳教士基地
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('赫爾松主教座', 'Diocese of Cherson', '赫爾松', '東正教', '希臘正教', '拜占庭禮', 400, '已廢除', 'cf932373-be6a-4fb2-a195-d26dc3045cba',
 '黑海北岸克里米亞古老主教座；9 世紀聖西里爾與聖梅笃丟在此學斯拉夫語、發明字母；988 弗拉基米爾大帝在此受洗。', 'Vita Constantini-Cyrilli');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('伊塔利烏斯', 'Italus of Cherson', '赫爾松', '東正教', 1, 325, 335, '正統', 'Acta Sanctorum', '尼西亞會議與會者'),
('葛奧蓋', 'George of Cherson', '赫爾松', '東正教', 2, 861, 870, '正統', 'Vita Cyrilli', '聖西里爾與梅笃丟拜訪期間的主教'),
('斯特拉昂', 'Stratophilus of Cherson', '赫爾松', '東正教', 3, 988, 1000, '正統', '羅斯往年紀事', '988 為弗拉基米爾大帝施洗的主教');


-- 波羅茨克 (Polotsk) — 11C 基輔羅斯西北重要主教座
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('波羅茨克主教座', 'Diocese of Polotsk', '波羅茨克', '俄羅斯正教會', '希臘正教', '拜占庭禮', 992, '現存', '19fa1944-eb67-4e3b-878b-2b2db7b490d6',
 '992 立座，基輔羅斯西北重要主教城；12 世紀聖普羅多斯洛瓦 (Saint Euphrosyne of Polotsk) 為東正教女聖人；現屬白俄羅斯正教會。', 'Povest vremennykh let');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('明娜', 'Mina of Polotsk', '波羅茨克', '俄羅斯正教會', 1, 1105, 1116, '正統', 'Russian Primary Chronicle', '波羅茨克主教；同期女聖人聖普羅多斯洛瓦'),
('伊里亞', 'Ilya of Polotsk', '波羅茨克', '俄羅斯正教會', 2, 1117, 1128, '正統', 'Russian Primary Chronicle', null),
('索菲洛霍維奇', 'Cyprian of Polotsk', '波羅茨克', '俄羅斯正教會', 3, 1503, 1535, '正統', 'Russian Orthodox archives', null);


-- =============================================
-- 補完前面 Phase 3 缺少的小幅補丁
-- =============================================
INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('埃沃普提烏斯', 'Evoptius of Ptolemais', '居勒拿', '未分裂教會', 2, 414, 431, '正統', 'Mansi IV', '敘奈西烏斯之弟；繼任兄長為主教；431 以弗所公會議與會者'),
('帕特里基烏斯', 'Patricius of Nyssa', '尼撒', '未分裂教會', 3, 410, 430, '正統', 'Synodicon orientale', null);
