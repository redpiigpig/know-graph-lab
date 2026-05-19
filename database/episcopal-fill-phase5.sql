-- ========================================================
-- Phase 5: Oriental + Assyrian + 敘利亞神學家教座
-- ========================================================
-- 埃德薩 (Ibas)、居魯士 (Theodoret)、摩普綏厄斯提亞 (Theodore)、
-- 巴格達 (加色丁現代)、巴士拉 (Old East)、泉州 (元代景教)、
-- 霍姆斯 (敘利亞正教現駐)
-- ========================================================

-- Parent see IDs:
--   安提阿 (EO)       : d77b276a-f93a-40af-a714-264fa71ebf4d
--   安提阿 (敘利亞正教): a96afd2d-eae9-4997-a337-d90bc19efebc
--   塞琉西亞 (古東方) : 0bc54720-ec8b-469f-8aea-97c09327b8b7
--   馬拉巴爾           : 9e661cb9-edd6-4c58-923c-3d9621389b92


-- =============================================
-- 敘利亞古典神學家教座
-- =============================================

-- 埃德薩 (Edessa) — Rabbula, Ibas, 聖以法蓮神學中心
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('埃德薩主教座', 'Diocese of Edessa', '埃德薩', '未分裂教會', '希臘正教', '安提阿禮', 100, '已廢除', 'd77b276a-f93a-40af-a714-264fa71ebf4d',
 '美索不達米亞古老主教座；2 世紀基督教中心；聖以法蓮神學詩人駐節地；學派分裂前的東方神學薈萃地；435-457 主教 Ibas 是「三章爭議」核心。', 'Eusebius, HE I.13; Drijvers, Cults and Beliefs at Edessa');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('帕魯特', 'Palut of Edessa', '埃德薩', '未分裂教會', 1, 200, 215, '正統', 'Doctrina Addai', '傳統認為由安提阿宗主教塞拉皮昂祝聖；建立正統教會反對曼達派'),
('庫納', 'Qune of Edessa', '埃德薩', '未分裂教會', 2, 313, 325, '正統', 'Eusebius, HE; 尼西亞會議與會者名單', null),
('拉布拉', 'Rabbula of Edessa', '埃德薩', '未分裂教會', 3, 411, 435, '正統', 'Vita Rabbulae', '反 Nestorius；改革派；其翻譯 Peshitta 影響東敘利亞聖經傳統'),
('伊巴斯', 'Ibas of Edessa', '埃德薩', '未分裂教會', 4, 435, 449, '廢黜後復位', 'Mansi VII; Liberatus, Breviarium', '安提阿學派；翻譯 Theodore of Mopsuestia 著作為敘利亞文；449 以弗所匪會被廢黜、451 卡爾西頓恢復；其「致馬利斯的書信」是「三章」之一'),
('伊巴斯（復位）', 'Ibas (restored)', '埃德薩', '未分裂教會', 5, 451, 457, '廢黜後復位', 'Mansi VII; ACO II', '451 卡爾西頓會議恢復職位');


-- 居魯士 (Cyrrhus) — Theodoret of Cyrrhus
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('居魯士主教座', 'Diocese of Cyrrhus', '居魯士', '未分裂教會', '希臘正教', '安提阿禮', 250, '已廢除', 'd77b276a-f93a-40af-a714-264fa71ebf4d',
 '敘利亞北部小主教座；423-466 提奧多禮 (Theodoret) 任主教，是安提阿學派最重要的神學家；「三章爭議」核心。', 'Theodoret, Historia ecclesiastica');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('提奧多禮', 'Theodoret of Cyrrhus', '居魯士', '未分裂教會', 1, 423, 466, '廢黜後復位', 'Theodoret《教會史》《信仰宣言》', '安提阿學派代表；反對亞歷山大派 Cyril 與 monophysite；著《教會史》《Eranistes》《信仰駁難》；449 以弗所匪會廢黜、451 卡爾西頓恢復；著作被三章列為譴責對象');


-- 摩普綏厄斯提亞 (Mopsuestia) — Theodore of Mopsuestia
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('摩普綏厄斯提亞主教座', 'Diocese of Mopsuestia', '摩普綏厄斯提亞', '未分裂教會', '希臘正教', '安提阿禮', 300, '已廢除', 'd77b276a-f93a-40af-a714-264fa71ebf4d',
 '基里西亞小主教座；392-428 提奧多 (Theodore of Mopsuestia) 任主教，被景教傳統尊為「解經師」(Interpreter)；其神學思想是 Nestorianism 與後來「景教」(東敘利亞教會) 的源頭。', 'Mansi V');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('提奧多', 'Theodore of Mopsuestia', '摩普綏厄斯提亞', '未分裂教會', 1, 392, 428, '正統', '提奧多《十二先知書註》《尼西亞信經評論》', '安提阿學派之父；解經學典範；學生包括 Nestorius；著作 553 年第二次君士坦丁堡公會議「三章譴責」中被定罪；東敘利亞教會仍尊其為「解經師」'),
('奧林皮烏斯', 'Olympius of Mopsuestia', '摩普綏厄斯提亞', '未分裂教會', 2, 431, 451, '正統', 'Mansi VI', null);


-- =============================================
-- 古代東方教會（亞述景教）重要早期 metropolitan + 現代加色丁
-- =============================================

-- 巴士拉 (Basra / Beth Lapat) — 古代東方早期重要 metropolitan
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('巴士拉都主教座', 'Metropolis of Basra', '巴士拉', '古代東方教會', '亞述景教', '東敘利亞禮', 310, '現存', '0bc54720-ec8b-469f-8aea-97c09327b8b7',
 '波斯灣口古老主教座；古代東方教會早期重要 metropolitan；7 世紀後成阿拉伯傳教重鎮；伊斯蘭統治下緩慢衰退。', 'Chronicle of Seert');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('提奧諾娒', 'Theonas of Basra', '巴士拉', '古代東方教會', 1, 310, 325, '正統', 'Chronicle of Seert', '尼西亞會議參與者'),
('巴爾沙烏馬', 'Barsauma of Basra', '巴士拉', '古代東方教會', 2, 484, 491, '正統', 'Chronicle of Seert; Synodicon orientale', '《Liber Karkae》作者；484 努基爾事件支持者'),
('提莫塞鄔斯', 'Timothy of Basra', '巴士拉', '古代東方教會', 3, 780, 823, '正統', 'Chronicle of Seert', '阿拔斯王朝時期，跨宗教對話的著名作品《With the Caliph al-Mahdi》');


-- 巴格達 (Baghdad) — 加色丁天主教 1950 起駐節
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('巴比倫加色丁天主教宗主教座', 'Chaldean Catholic Patriarchate of Babylon', '巴格達', '加色丁天主教', '羅馬公教', '東敘利亞禮', 1950, '現存', '0bc54720-ec8b-469f-8aea-97c09327b8b7',
 '加色丁天主教（1552 自東方教會分出與羅馬共融）駐節地。1950 年由摩蘇爾遷至巴格達。現任宗主教 Mar Louis Raphaël I Sako 是中東基督徒重要代表。', 'GCatholic.org');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬爾·優素福七世·甘加', 'Mar Joseph VII Ghanima', '巴格達', '加色丁天主教', 1, 1947, 1958, '正統', 'GCatholic.org', '1950 將駐節地從摩蘇爾遷至巴格達'),
('馬爾·保祿二世·切伊何', 'Paul II Cheikho', '巴格達', '加色丁天主教', 2, 1958, 1989, '正統', 'GCatholic.org', '梵二大公會議參與者'),
('馬爾·拉斐爾一世·比丹維德', 'Raphael I Bidawid', '巴格達', '加色丁天主教', 3, 1989, 2003, '正統', 'GCatholic.org', '海灣戰爭時期'),
('馬爾·埃馬努埃爾三世·德利', 'Emmanuel III Delly', '巴格達', '加色丁天主教', 4, 2003, 2012, '正統', 'GCatholic.org', '伊拉克戰爭時期；2007 升任樞機'),
('馬爾·路易斯·拉斐爾一世·薩科', 'Louis Raphaël I Sako', '巴格達', '加色丁天主教', 5, 2013, NULL, '正統', 'GCatholic.org', '2018 升任樞機；ISIS 之後伊拉克基督徒重要代言人；現任');


-- 泉州 (Quanzhou) — 元代景教大都主教
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('泉州景教都主教座', 'Metropolis of Zaiton (Quanzhou)', '泉州', '古代東方教會', '亞述景教', '東敘利亞禮', 1278, '已廢除', '0bc54720-ec8b-469f-8aea-97c09327b8b7',
 '元代「也里可溫教」(景教) 在中國海上絲路重要根據地；泉州出土多個敘利亞文+漢文景教碑文 (元代)；明清禁教後消失。', '《元史》本紀；泉州景教碑');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬爾·所羅門', 'Mar Solomon of Zaiton', '泉州', '古代東方教會', 1, 1278, 1289, '正統', '《元史·世祖本紀》', '元世祖時期泉州大都主教，《元史》提及'),
('馬爾·雅·巴拉哈三世', 'Mar Yahballaha III', '泉州', '古代東方教會', 2, 1281, 1281, '正統', 'Histoire de Mar Yahballaha', '泉州出身的回鶻人；後升塞琉西亞—泰西封宗主教 1281-1317（覆蓋古東方主鏈）'),
('凱里揚', 'Mar Kirillos of Zaiton', '泉州', '古代東方教會', 3, 1335, 1345, '正統', '泉州景教碑文', '元末泉州景教碑文記載');


-- =============================================
-- 印度 多馬基督徒
-- =============================================

-- 科欽 (Cochin / Kochi) — 多馬基督徒 7 古教會之一
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('科欽主教座', 'Diocese of Cochin', '科欽', '未分裂教會', '亞述景教', '東敘利亞禮', 200, '現存', '9e661cb9-edd6-4c58-923c-3d9621389b92',
 '印度多馬基督徒 (Saint Thomas Christians) 7 古教會之一；2 世紀建立；中世紀屬東方教會 (景教)；1599 Synod of Diamper 後部分入羅馬共融。', 'Mingana, Early Spread of Christianity in India');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('馬爾·約翰', 'Mar John of Cochin', '科欽', '未分裂教會', 1, 700, 720, '正統', 'Mingana', '8 世紀記載'),
('馬爾·約瑟', 'Mar Joseph the Indian', '科欽', '未分裂教會', 2, 1485, 1503, '正統', 'Letter of Mar Joseph 1502', '葡萄牙人 1498 抵達前的最後一任獨立印度大主教'),
('馬爾·亞伯拉罕', 'Mar Abraham of Angamali', '科欽', '未分裂教會', 3, 1568, 1597, '正統', 'Mingana', '1599 Diamper Synod 前的最後一任獨立大主教');


-- =============================================
-- 敘利亞正教 現代駐節地
-- =============================================

-- 霍姆斯 (Homs) — 敘利亞正教 1959 年遷至大馬士革前的駐節地
INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status, parent_see_id, notes, sources) VALUES
('霍姆斯敘利亞正教座', 'Diocese of Homs (Syriac Orthodox)', '霍姆斯', '敘利亞正統教會', '敘利亞正教', '西敘利亞禮', 1295, '現存', 'a96afd2d-eae9-4997-a337-d90bc19efebc',
 '13 世紀建立；19-20 世紀敘利亞正教安提阿宗主教曾數度駐節此地；1959 後遷至大馬士革。', 'Syriac Orthodox archives');

INSERT INTO episcopal_succession (name_zh, name_en, see, church, succession_number, start_year, end_year, status, sources, notes) VALUES
('伊格那丟·吉巴布六世', 'Ignatius Jirjis VI', '霍姆斯', '敘利亞正統教會', 1, 1933, 1957, '正統', 'Syriac Orthodox archives', '駐節霍姆斯時期的敘利亞正教安提阿宗主教'),
('伊格那丟·雅各布三世', 'Ignatius Jacob III', '霍姆斯', '敘利亞正統教會', 2, 1957, 1959, '正統', 'Syriac Orthodox archives', '1959 將駐節地遷至大馬士革'),
('阿夫赫姆', 'Athanasius Aphrem I Barsoum', '霍姆斯', '敘利亞正統教會', 3, 1933, 1957, '正統', 'Syriac Orthodox archives', '副宗主教；著《歷代敘利亞文學作家》是敘利亞學名作');
