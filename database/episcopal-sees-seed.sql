-- ============================================================
-- 宗主教座種子資料 — 現存及歷史性宗主教座（約 41 個）
-- 執行前請確保已執行 episcopal-sees.sql
-- 資料截至 2026 年 4 月
-- ============================================================
-- 分組：
--   I.   古代五大宗主教座主線
--   II.  五大宗主教座分裂支線
--   III. 斯拉夫及東歐東正教
--   IV.  亞美尼亞使徒教會系統
--   V.   東方教會（Church of the East）系統
--   VI.  非洲東方正教
--   VII. 印度東方基督教
--   VIII.拉丁禮天主教名義宗主教座
--   IX.  已廢除歷史宗主教座
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- I. 古代五大宗主教座主線
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('羅馬宗主教座',
 'Holy See / Patriarchate of Rome',
 '羅馬', '天主教', '天主教（拉丁禮）', '拉丁禮',
 30, '現存',
 '教宗良十四世', 'Pope Leo XIV', 2025,
 '梵蒂岡',
 '教宗為羅馬主教，同時為全球天主教最高牧首。傳統由聖伯多祿（聖彼得）建立。1054 年大分裂後不再被東方教會承認為五頭制之首。',
 'Irenaeus, AH III.3; Eusebius, HE II.14'),

('君士坦丁堡普世宗主教座',
 'Ecumenical Patriarchate of Constantinople',
 '君士坦丁堡', '東正教', '東正教', '拜占庭禮',
 330, '現存',
 '巴爾多祿茂一世', 'Bartholomew I', 1991,
 '伊斯坦堡法納爾區',
 '東正教聯盟中「首席榮譽」（primus inter pares）。1453 年鄂圖曼帝國滅拜占庭後在土耳其境內受限。傳統由使徒聖安德肋建立。',
 'Council of Chalcedon (451); Trullo Council (692)'),

('希臘東正教亞歷山大宗主教座',
 'Greek Orthodox Patriarchate of Alexandria and All Africa',
 '亞歷山大', '東正教', '東正教', '拜占庭禮',
 42, '現存',
 '泰奧多羅斯二世', 'Theodore II', 2004,
 '埃及亞歷山大',
 '451 年查爾西頓公會議後接受兩性論的亞歷山大主教傳承。管轄非洲大陸，近年成員以非裔信徒為主。傳統由聖馬爾谷建立。',
 'Eusebius, HE II.16; Council of Chalcedon (451)'),

('希臘東正教安提阿宗主教座',
 'Greek Orthodox Patriarchate of Antioch and All the East',
 '安提阿', '東正教', '東正教', '拜占庭禮',
 37, '現存',
 '約翰十世', 'John X', 2012,
 '敘利亞大馬士革',
 '接受查爾西頓公會議的安提阿傳承。1724 年梅基特分裂後，繼續以阿拉伯語敘利亞信徒為主。傳統由聖伯多祿與聖保羅共同建立。',
 'Eusebius, HE III.36'),

('希臘東正教耶路撒冷宗主教座',
 'Greek Orthodox Patriarchate of Jerusalem',
 '耶路撒冷', '東正教', '東正教', '拜占庭禮',
 451, '現存',
 '狄奧菲洛斯三世', 'Theophilos III', 2005,
 '耶路撒冷',
 '451 年查爾西頓大公會議正式確立宗主教地位。負責守護聖地基督教聖所。成員多為阿拉伯裔，但傳統上主教為希臘人。',
 'Council of Chalcedon (451) canon 7');


-- ════════════════════════════════════════════════════════════
-- II. 五大宗主教座分裂支線
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, split_year, notes, sources) VALUES

-- ── 亞歷山大分支 ──────────────────────────────────────────
('科普特東正教亞歷山大宗主教座',
 'Coptic Orthodox Patriarchate of Alexandria',
 '亞歷山大', '科普特正教', '東方正教', '科普特禮',
 451, '現存',
 '教宗塔瓦德羅斯二世', 'Pope Tawadros II', 2012,
 '埃及開羅',
 451,
 '451 年因拒絕查爾西頓「兩性論」而分裂，成為「一性論」（Miaphysite）教會。為埃及最大基督教教派，同時是東方正教聯盟的精神領袖。',
 'Council of Chalcedon (451); Coptic Synaxarion'),

('科普特天主教亞歷山大宗主教座',
 'Coptic Catholic Patriarchate of Alexandria',
 '亞歷山大', '科普特天主教', '東儀天主教', '科普特禮',
 1895, '現存',
 '易卜拉欣·以撒·西德拉克', 'Ibrahim Isaac Sidrak', 2013,
 '埃及開羅',
 1895,
 '17–19 世紀部分科普特基督徒與羅馬建立共融，1895 年正式設立宗主教座。',
 'Catholic Encyclopedia; Annuario Pontificio'),

('拉丁禮亞歷山大宗主教座',
 'Latin Patriarchate of Alexandria',
 '亞歷山大', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1219, '已廢除',
 NULL, NULL, NULL, NULL,
 1219,
 '第五次十字軍後設立，純名義職位。1964 年與拉丁禮君士坦丁堡同年廢除，為梵二合一精神的象徵。',
 'Catholic hierarchy records'),

-- ── 安提阿分支 ──────────────────────────────────────────
('敘利亞東方正教安提阿宗主教座',
 'Syriac Orthodox Patriarchate of Antioch and All the East',
 '安提阿', '敘利亞正教', '東方正教', '西敘利亞禮',
 518, '現存',
 '伊格納提烏斯·阿夫雷姆二世', 'Ignatius Aphrem II', 2014,
 '敘利亞大馬士革',
 518,
 '451 年拒絕查爾西頓後形成，至 518 年正式與查爾西頓派決裂。俗稱「雅各派」（Jacobite）。管轄包含印度的敘利亞基督徒。',
 'John of Ephesus, Ecclesiastical History'),

('馬龍尼特禮天主教安提阿宗主教座',
 'Maronite Catholic Patriarchate of Antioch and All the East',
 '安提阿', '馬龍尼特禮天主教', '東儀天主教', '西敘利亞禮',
 685, '現存',
 '貝沙拉·布特羅斯·拉希', 'Bechara Boutros al-Rahi', 2011,
 '黎巴嫩比克爾凱亞',
 NULL,
 '馬龍尼派從未接受一性論，也從未完全脫離羅馬共融，是唯一從未分裂的東儀教會。為黎巴嫩最重要的基督教傳統之一。',
 'Theodoret, Historia Religiosa; Dau, History of the Maronites'),

('希臘天主教麥勒基特禮安提阿宗主教座',
 'Melkite Greek Catholic Patriarchate of Antioch, Alexandria and Jerusalem',
 '安提阿', '希臘天主教麥勒基特禮', '東儀天主教', '拜占庭禮',
 1724, '現存',
 '優素福·阿布西', 'Youssef Absi', 2017,
 '黎巴嫩拉巴克',
 1724,
 '1724 年希臘正統安提阿宗主教選舉後，支持羅馬共融的一派形成梅基特教會。名義上同時持有安提阿、亞歷山大、耶路撒冷三座的稱號。',
 'Hajjar, Les chrétiens uniates du Proche-Orient'),

('敘利亞天主教安提阿宗主教座',
 'Syriac Catholic Patriarchate of Antioch and All the East',
 '安提阿', '敘利亞天主教', '東儀天主教', '西敘利亞禮',
 1783, '現存',
 '伊格納提烏斯·約瑟夫三世·尤南', 'Ignatius Joseph III Yonan', 2009,
 '黎巴嫩貝魯特',
 1783,
 '17 世紀部分敘利亞東方正教信徒轉入羅馬共融，經歷多次反覆，至 1783 年正式穩定。',
 'Anatolios, Chalcedon in Context'),

('拉丁禮安提阿宗主教座',
 'Latin Patriarchate of Antioch',
 '安提阿', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1099, '已廢除',
 NULL, NULL, NULL, NULL,
 1099,
 '第一次十字軍攻克安提阿後設立。1268 年城市淪陷後成為名義職位，1964 年保祿六世廢除。',
 'William of Tyre, Historia rerum'),

-- ── 耶路撒冷分支 ──────────────────────────────────────────
('拉丁禮耶路撒冷宗主教座',
 'Latin Patriarchate of Jerusalem',
 '耶路撒冷', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1099, '現存',
 '皮耶爾巴蒂斯塔·皮扎巴拉', 'Pierbattista Pizzaballa', 2020,
 '耶路撒冷',
 1099,
 '1099 年第一次十字軍後建立。1291 年十字軍國家滅亡後成為名義職位，1847 年庇護九世恢復為實際居住地的宗主教座。',
 'William of Tyre; Pius IX bull (1847)'),

('亞美尼亞耶路撒冷宗主教座',
 'Armenian Patriarchate of Jerusalem',
 '耶路撒冷', '亞美尼亞正教', '東方正教', '亞美尼亞禮',
 638, '現存',
 '努爾漢·馬拿吉安', 'Nourhan Manougian', 2013,
 '耶路撒冷',
 638,
 '阿拉伯征服後逐漸確立。在耶路撒冷擁有重要的聖雅各修道院建築群，管轄聖地亞美尼亞聖所。',
 'Armenian Patriarchate of Jerusalem archives'),

-- ── 君士坦丁堡分支 ──────────────────────────────────────
('拉丁禮君士坦丁堡宗主教座',
 'Latin Patriarchate of Constantinople',
 '君士坦丁堡', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1204, '已廢除',
 NULL, NULL, NULL, NULL,
 1204,
 '第四次十字軍攻陷君士坦丁堡後設立。1261 年拜占庭收復後成為名義職位。1964 年保祿六世與巴爾多祿茂一世會面後廢除。',
 'Longnon, L''Empire latin de Constantinople'),

('亞美尼亞君士坦丁堡宗主教座',
 'Armenian Patriarchate of Constantinople',
 '君士坦丁堡', '亞美尼亞正教', '東方正教', '亞美尼亞禮',
 1461, '現存',
 '薩哈克·馬沙里揚', 'Sahak Mashalian', 2019,
 '土耳其伊斯坦堡',
 1461,
 '1461 年鄂圖曼蘇丹穆罕默德二世征服後授予。管轄土耳其及希臘克里特島約 82,000 名信徒。地位低於兩個公教主教座。',
 'Ottoman imperial records; Armenian Patriarchate archives');


-- ════════════════════════════════════════════════════════════
-- III. 斯拉夫及東歐東正教宗主教座
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('莫斯科東正教宗主教座',
 'Moscow Patriarchate / Russian Orthodox Church',
 '莫斯科', '東正教（俄羅斯）', '東正教', '拜占庭禮',
 1589, '現存',
 '基里爾一世', 'Kirill I', 2009,
 '俄羅斯莫斯科',
 '1589 年君士坦丁堡正式授予宗主教地位（原為莫斯科都主教座，988 年基輔受洗起算）。全球東正教成員最多的教會。因支持俄羅斯入侵烏克蘭，2022 年後與多個東正教會關係惡化。',
 'Ecumenical Patriarchate synodal tomos (1589)'),

('塞爾維亞東正教宗主教座',
 'Serbian Orthodox Church / Patriarchate of Peć',
 '塞爾維亞', '東正教（塞爾維亞）', '東正教', '拜占庭禮',
 1346, '現存',
 '波爾菲里耶', 'Porfirije', 2021,
 '塞爾維亞貝爾格萊德',
 '1219 年聖薩瓦建立自治大主教區；1346 年升為宗主教；1463 年被鄂圖曼廢除；1920 年恢復並合併各塞爾維亞正教組織。',
 'Serbian Orthodox Church archives'),

('羅馬尼亞東正教宗主教座',
 'Romanian Orthodox Church',
 '羅馬尼亞', '東正教（羅馬尼亞）', '東正教', '拜占庭禮',
 1925, '現存',
 '達尼埃爾', 'Daniel', 2007,
 '羅馬尼亞布加勒斯特',
 '1865 年成立自治教會，1925 年升為宗主教。東正教聯盟中成員第二多的教會（僅次於俄羅斯）。',
 'Romanian Orthodox Church synod records'),

('保加利亞東正教宗主教座',
 'Bulgarian Orthodox Church',
 '保加利亞', '東正教（保加利亞）', '東正教', '拜占庭禮',
 927, '現存',
 '達尼伊爾', 'Daniil', 2024,
 '保加利亞索菲亞',
 '927 年首度獲得承認；1018 年被拜占庭廢除；1235 年恢復；1767 年再廢；1953 年現代宗主教座恢復。世界上最古老的斯拉夫正教宗主教座之一。',
 'Bulgarian Orthodox Church archives'),

('格魯吉亞東正教宗主教座',
 'Georgian Orthodox Church / Catholicate-Patriarchate of All Georgia',
 '格魯吉亞', '東正教（格魯吉亞）', '東正教', '拜占庭禮',
 466, '現存',
 '空缺', NULL, NULL,
 '格魯吉亞提比里斯',
 '4 世紀基督教化；466 年從亞美尼亞教會獨立；1010 年升為宗主教；1811 年俄羅斯帝國廢除；1917 年革命後恢復。伊利亞二世於 2026 年 3 月 17 日辭世，宗主教座暫缺。',
 'Georgian Orthodox Church synod records');


-- ════════════════════════════════════════════════════════════
-- IV. 亞美尼亞使徒教會系統
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('全亞美尼亞公教主教座',
 'Catholicate of All Armenians, Holy See of Etchmiadzin',
 '厄奇米亞津', '亞美尼亞使徒教會', '東方正教', '亞美尼亞禮',
 301, '現存',
 '卡列金二世', 'Karekin II', 1999,
 '亞美尼亞厄奇米亞津',
 '301 年亞美尼亞成為世界第一個國教基督教國家；451 年查爾西頓後形成獨立東方正教傳統。亞美尼亞使徒教會的最高精神中心。2025 年面臨政府施壓要求辭職爭議。',
 'Agathangelos, History of the Armenians; Faustus of Byzantium'),

('基里家公教主教座',
 'Armenian Catholicate of the Great House of Cilicia',
 '基里家', '亞美尼亞使徒教會', '東方正教', '亞美尼亞禮',
 1080, '現存',
 '阿蘭一世', 'Aram I', 1995,
 '黎巴嫩安特利亞斯',
 '1080 年亞美尼亞王國在基里家（今土耳其奇里乞亞）建立；1441 年厄奇米亞津恢復後成為獨立公教主教座，主要管轄中東、敘利亞及部分海外亞美尼亞人。',
 'Armenian Catholicate of Cilicia archives'),

('亞美尼亞天主教基里家宗主教座',
 'Armenian Catholic Patriarchate of Cilicia',
 '基里家', '亞美尼亞天主教', '東儀天主教', '亞美尼亞禮',
 1742, '現存',
 '拉法葉·貝德羅斯二十一世·米納西安', 'Raphaël Bedros XXI Minassian', 2021,
 '黎巴嫩貝魯特',
 '部分亞美尼亞基督徒於 1742 年轉入羅馬共融後形成。1928 年宗主教座遷往黎巴嫩。',
 'Catholic Encyclopedia; Annuario Pontificio');


-- ════════════════════════════════════════════════════════════
-- V. 東方教會（Church of the East）系統
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('亞述東方教會',
 'Assyrian Church of the East',
 '塞琉西亞—泰西封', '東方教會（亞述）', '東方教會', '東敘利亞禮',
 310, '現存',
 '馬爾·阿瓦三世', 'Mar Awa III', 2021,
 '美國伊利諾州摩頓格羅夫',
 '310 年帕帕·巴爾·阿蓋設立統一的大公主教座；431 年以弗所公會議後被標記為「涅斯多里派」（有爭議）。鼎盛時期傳教至印度、中亞、唐代中國（景教）。1552 年因嗣位問題分裂，1976 年現代組織形式確立。',
 'Chabot, Synodicon orientale; Baum & Winkler, Church of the East'),

('古代東方教會',
 'Ancient Church of the East',
 '塞琉西亞—泰西封', '古代東方教會', '東方教會', '東敘利亞禮',
 1968, '現存',
 '格瓦吉斯三世·尤南', 'Gewargis III Younan', 2022,
 '伊拉克巴格達',
 '1968 年因曆法改革爭議從亞述東方教會分出，主要位於伊拉克。與亞述東方教會保持對話。',
 'Church records'),

('迦勒底天主教巴格達宗主教座',
 'Chaldean Catholic Patriarchate of Babylon / Baghdad',
 '巴格達', '迦勒底天主教', '東儀天主教', '東敘利亞禮',
 1552, '現存',
 '馬爾·保祿三世·諾納', 'Mar Paulos III Nona', 2026,
 '伊拉克巴格達',
 '1552 年部分東方教會主教轉入羅馬共融後形成；1830 年現代宗主教座穩定確立。為伊拉克最大的天主教社群，因戰亂而大量移民海外。2026 年 4 月諾納當選，接替辭職的路易·拉法葉一世·薩科。',
 'Vatican News 2026-04; Catholic Encyclopedia');


-- ════════════════════════════════════════════════════════════
-- VI. 非洲東方正教
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('衣索比亞東正教泰瓦赫多宗主教座',
 'Ethiopian Orthodox Tewahedo Church',
 '衣索比亞', '衣索比亞東正教', '東方正教', '衣索比亞禮',
 1959, '現存',
 '阿布訥·瑪帝亞斯一世', 'Abune Mathias I', 2013,
 '衣索比亞阿迪斯阿貝巴',
 '4 世紀基督教化；歷史上長期受科普特亞歷山大教宗管轄；1959 年在海勒·塞拉西皇帝推動下獲得自治。為最大的東方正教教會（約 3,600–6,000 萬信徒）。',
 'Imperial Ethiopian decree (1959); Oriental Orthodox records'),

('厄立特里亞東正教泰瓦赫多宗主教座',
 'Eritrean Orthodox Tewahedo Church',
 '厄立特里亞', '厄立特里亞東正教', '東方正教', '衣索比亞禮',
 1993, '現存',
 '阿布訥·克洛斯（爭議）', 'Abune Qerlos (disputed)', 2021,
 '厄立特里亞阿斯馬拉',
 '1993 年厄立特里亞獨立後從衣索比亞教會分立。現任宗主教任命（2021年）受政府干預，合法性受廣泛質疑；前任阿布訥·安托尼奧斯遭軟禁，2022 年辭世。',
 'Eritrean Orthodox Church records; Human Rights Watch reports');


-- ════════════════════════════════════════════════════════════
-- VII. 印度東方基督教
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('馬拉巴爾東正教宗主教座',
 'Malankara Orthodox Syrian Church',
 '馬拉巴爾', '馬拉巴爾東正教', '東方正教', '西敘利亞禮',
 1912, '現存',
 '巴西利奧斯·馬修斯三世', 'Baselios Marthoma Mathews III', 2021,
 '印度喀拉拉邦科塔亞姆',
 '傳統溯源至使徒多馬（1 世紀）；1912 年從敘利亞東方正教管轄中宣布獨立。長期與敘利亞安提阿宗主教在管轄權有爭議，印度最高法院已多次裁決。',
 'Malankara Orthodox Syrian Church archives; India Supreme Court judgments');


-- ════════════════════════════════════════════════════════════
-- VIII. 拉丁禮天主教名義宗主教座（現存）
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('威尼斯宗主教座',
 'Patriarchate of Venice',
 '威尼斯', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1451, '名義',
 '弗朗切斯科·莫拉利亞', 'Francesco Moraglia', 2012,
 '義大利威尼斯',
 '1451 年繼承格拉多宗主教座。威尼斯宗主教歷史上多人升任教宗（包括聖庇護十世、若望二十三世、若望保祿一世）。現為榮譽性宗主教頭銜。',
 'Venetian patriarchal records'),

('里斯本宗主教座',
 'Patriarchate of Lisbon',
 '里斯本', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1716, '名義',
 '魯伊·曼努埃爾·蘇薩·瓦萊里奧', 'Rui Manuel Sousa Valério', 2023,
 '葡萄牙里斯本',
 '1716 年教宗克萊蒙十一世應葡萄牙國王若昂五世請求設立。1740 年後合併里斯本大主教區，成為葡萄牙天主教最高教座。',
 'Clement XI bull (1716)'),

('果阿宗主教座',
 'Patriarchate of the East Indies (Goa)',
 '果阿', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1886, '名義',
 '菲利普·內里·費拉奧', 'Filipe Neri Ferrão', 2004,
 '印度果阿',
 '果阿大主教座自 1558 年；1886 年正式升格為宗主教座。葡萄牙殖民時代於亞洲設立的主要天主教中心。1961 年印度收回果阿後宗主教依然在任。',
 'Papal bull (1886); Annuario Pontificio');


-- ════════════════════════════════════════════════════════════
-- IX. 已廢除歷史宗主教座
-- ════════════════════════════════════════════════════════════

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, abolished_year, status,
  location, notes, sources) VALUES

('阿奎萊亞宗主教座',
 'Patriarchate of Aquileia',
 '阿奎萊亞', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 557, 1751, '已廢除',
 '義大利烏迪內',
 '北義大利重要古代教座，宗主教頭銜約 557 年確立。1751 年被教宗本篤十四世廢除，分為烏迪內與戈里齊亞兩個大主教座。',
 'Benedict XIV bull Injuncta nobis (1751)'),

('格拉多宗主教座',
 'Patriarchate of Grado',
 '格拉多', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 606, 1451, '已廢除',
 '義大利格拉多',
 '因阿奎萊亞在三章爭議中的分裂而形成（約 606 年）。威尼斯共和國取代拜占庭在亞得里亞海的勢力後，1451 年格拉多地位被威尼斯宗主教座取代。',
 'Venetian patriarchal records'),

('迦太基宗主教座',
 'Patriarchate of Carthage',
 '迦太基', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 200, 1076, '已廢除',
 '突尼西亞迦太基（今突尼斯附近）',
 '2–3 世紀北非最重要的教座，特土良、西普里安、奧古斯丁均與此地有關。7 世紀阿拉伯征服後逐漸消亡，1076 年有最後一筆記載。',
 'Tertullian; Cyprian; Augustine; Arab conquest records'),

('西印度群島宗主教座',
 'Patriarchate of the West Indies',
 '西印度群島', '天主教（拉丁禮）', '天主教（拉丁禮）', '拉丁禮',
 1524, 1963, '已廢除',
 NULL,
 '1524 年設立，純名義職位，從未有實際管轄權，持有者為西班牙宮廷神職人員。1963 年廢除。',
 'Spanish royal chapel records');


-- ════════════════════════════════════════════════════════════
-- 設定 parent_see_id（分裂來源關聯）
-- ════════════════════════════════════════════════════════════

-- 亞歷山大的分支
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '希臘東正教亞歷山大宗主教座')
  WHERE name_zh IN ('科普特東正教亞歷山大宗主教座', '科普特天主教亞歷山大宗主教座', '拉丁禮亞歷山大宗主教座');

-- 安提阿的分支
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '希臘東正教安提阿宗主教座')
  WHERE name_zh IN ('敘利亞東方正教安提阿宗主教座', '馬龍尼特禮天主教安提阿宗主教座', '希臘天主教麥勒基特禮安提阿宗主教座', '敘利亞天主教安提阿宗主教座', '拉丁禮安提阿宗主教座');

-- 耶路撒冷的分支
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '希臘東正教耶路撒冷宗主教座')
  WHERE name_zh IN ('拉丁禮耶路撒冷宗主教座', '亞美尼亞耶路撒冷宗主教座');

-- 君士坦丁堡的分支
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '君士坦丁堡普世宗主教座')
  WHERE name_zh IN ('拉丁禮君士坦丁堡宗主教座', '亞美尼亞君士坦丁堡宗主教座');

-- 敘利亞天主教源自敘利亞東方正教
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '敘利亞東方正教安提阿宗主教座')
  WHERE name_zh = '敘利亞天主教安提阿宗主教座';

-- 科普特天主教源自科普特東正教
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '科普特東正教亞歷山大宗主教座')
  WHERE name_zh = '科普特天主教亞歷山大宗主教座';

-- 衣索比亞與厄立特里亞源自科普特（歷史上的管轄關係）
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '科普特東正教亞歷山大宗主教座')
  WHERE name_zh = '衣索比亞東正教泰瓦赫多宗主教座';

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '衣索比亞東正教泰瓦赫多宗主教座')
  WHERE name_zh = '厄立特里亞東正教泰瓦赫多宗主教座';

-- 馬拉巴爾東正教源自敘利亞東方正教（歷史管轄）
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '敘利亞東方正教安提阿宗主教座')
  WHERE name_zh = '馬拉巴爾東正教宗主教座';

-- 迦勒底天主教源自亞述東方教會
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '亞述東方教會')
  WHERE name_zh = '迦勒底天主教巴格達宗主教座';

-- 古代東方教會源自亞述東方教會
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '亞述東方教會')
  WHERE name_zh = '古代東方教會';

-- 亞美尼亞天主教源自全亞美尼亞公教主教座
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '全亞美尼亞公教主教座')
  WHERE name_zh = '亞美尼亞天主教基里家宗主教座';

-- 格拉多源自阿奎萊亞，威尼斯源自格拉多
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '阿奎萊亞宗主教座')
  WHERE name_zh = '格拉多宗主教座';

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '格拉多宗主教座')
  WHERE name_zh = '威尼斯宗主教座';
