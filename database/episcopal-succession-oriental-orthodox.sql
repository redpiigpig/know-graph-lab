-- ============================================================
-- 東方正統教會主教傳承——次要宗主教及公教座
-- 基里基亞亞美尼亞、君士坦丁堡亞美尼亞、耶路撒冷亞美尼亞
-- 敘利亞正統（圖爾阿布丁、大馬士革）、馬蘭卡拉正統
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 基里基亞亞美尼亞公教（安特利亞斯）
-- 第二亞美尼亞公教座；1915年後流亡至黎巴嫩
-- ==============================
('薩哈克二世', 'Sahak II of Cilicia', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 1, 353, 377, '逝世', '亞美尼亞教會公會議', '正統', 'Armenian tradition', '公教座在小亞細亞西里西亞地區（今土耳其阿達納省）設立；薩哈克二世傳統上為首任公教座主持人；亞美尼亞西部（「西里西亞」）基督徒的守護者'),
('德奧多羅斯一世', 'Theodoros I', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 3, 420, 444, '逝世', '亞美尼亞教會', '正統', 'Armenian records', '431年以弗所大公會議後亞美尼亞教會的立場；拒絕接受卡爾西頓神學，維持亞美尼亞一性論傳統'),
('格里高里斯六世', 'Grigoris VI', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 12, 1066, 1105, '逝世', '亞美尼亞公教會議', '正統', 'Armenian records', '1064年塞爾柱突厥征服亞美尼亞；西里西亞成為亞美尼亞人的庇護地（亞美尼亞西里西亞王國，1198-1375年）；公教座與亞美尼亞西里西亞王國的互利關係'),
('格里高里四世·德格哈', 'Grigoris IV Tgha', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 15, 1173, 1193, '逝世', '亞美尼亞西里西亞王國', '正統', 'Armenian records', '十字軍東征時代；亞美尼亞西里西亞王國的鼎盛期；公教座在西里西亞政治中的核心地位；與安提阿法蘭克公國的外交關係'),
('康斯坦丁一世', 'Kostandin I', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 18, 1221, 1267, '逝世', '亞美尼亞西里西亞王國', '正統', 'Armenian Cilicia records', '蒙古帝國擴張時代；亞美尼亞西里西亞與蒙古聯盟（反對穆斯林勢力）；1243年科澤達戈之戰後蒙古-亞美尼亞結盟'),
('格里高里七世', 'Grigoris VII', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 22, 1293, 1307, '逝世', '亞美尼亞西里西亞王國', '正統', 'Armenian records', '馬穆魯克蘇丹國（埃及）持續進攻西里西亞亞美尼亞；1375年西里西亞王國滅亡前夕的最後繁榮期之一'),
('格里高里-馬薩耶里安', 'Grigoris-Masayelian', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 35, 1478, 1507, '逝世', '鄂圖曼帝國下', '正統', 'Armenian records', '1375年西里西亞王國滅亡後；鄂圖曼帝國統治下西里西亞亞美尼亞人的延續；公教座維持在西里西亞故地'),
('薩哈克·哈巴揚', 'Sahak Khabayan', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 53, 1902, 1939, '逝世', '亞美尼亞公教會議', '正統', 'Armenian Patriarchate of Cilicia; Genocide records', '1915年亞美尼亞種族滅絕期間；鄂圖曼政府驅逐和屠殺150-180萬亞美尼亞人；薩哈克本人在難民中奔走，保護信眾流亡；戰後暫居敘利亞和黎巴嫩；1930年代決定在黎巴嫩安特利亞斯（Antelias）重建公教座'),
('加列金一世·侯斯達澤', 'Garegin I Hovsepian', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 55, 1943, 1952, '逝世', '亞美尼亞公教會議', '正統', 'Armenian Patriarchate of Cilicia', '在黎巴嫩安特利亞斯主持；二戰期間和戰後；1948年蘇聯鼓勵亞美尼亞人「回歸蘇聯亞美尼亞」運動——導致基里基亞公教座與埃奇米亞津（Etchmiadzin，蘇聯控制）的永久決裂'),
('巴比根一世·古列格希安', 'Papken I Guleserian', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 56, 1931, 1936, '逝世', '亞美尼亞公教會議', '正統', 'Armenian Patriarchate of Cilicia', '安特利亞斯新址的初期建設；黎巴嫩成為最大亞美尼亞海外社群地之一（貝魯特，特別是波爾吉·哈穆德區）'),
('卡里金·薩爾基先（二世）', 'Karekin II Sarkissian', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 61, 1977, 1995, '調任（任埃奇米亞津公教）', '亞美尼亞公教會議', '正統', 'Armenian Church', '1995年離開基里基亞擔任埃奇米亞津公教（加列金二世）——基里基亞-埃奇米亞津歷史上首次一人先後擔任兩座；但此舉加深了兩座間的緊張關係'),
('阿拉姆一世·凱希希安', 'Aram I Keshishian', '基里基亞亞美尼亞', '亞美尼亞使徒教會（基里基亞）', 62, 1995, NULL, NULL, '亞美尼亞公教會議', '正統', 'Armenian Patriarchate of Cilicia; WCC', '世界教協（WCC）中央委員會主席（1991-2006年）——亞美尼亞教會史上國際舞台最活躍的主教；在黎巴嫩內戰後重建時代帶領安特利亞斯；基里基亞公教座繼續作為埃奇米亞津的獨立對等機構；2023年黎巴嫩經濟崩潰對教會基礎設施造成嚴重挑戰');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '基里基亞亞美尼亞' AND church = '亞美尼亞使徒教會（基里基亞）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 君士坦丁堡亞美尼亞宗主教
-- 奧斯曼帝國米利特制度；1915年種族滅絕後
-- ==============================
('約阿基姆一世', 'Joachim I', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 1, 1461, 1478, '逝世', '蘇丹梅赫梅特二世', '正統', 'Ottoman millet records', '1453年君士坦丁堡陷落後蘇丹梅赫梅特二世設立亞美尼亞宗主教——米利特（millet）制度：各民族的宗教和法律自治；約阿基姆一世為首任宗主教；亞美尼亞人可在奧斯曼體制內保持信仰和文化'),
('西蒙一世', 'Simon I', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 5, 1540, 1560, '逝世', '蘇丹蘇萊曼大帝', '正統', 'Ottoman records', '蘇萊曼大帝時代；君士坦丁堡亞美尼亞社群的鼎盛期；希薩爾巴希（Kumkapi）亞美尼亞大教堂建立'),
('格里高里四世（納爾利卡比）', 'Grigoris IV Narlikapi', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 12, 1650, 1680, '逝世', '奧斯曼政府', '正統', 'Ottoman records', '亞美尼亞人印刷業（伊斯坦堡第一家亞美尼亞印刷廠，1567年）和文化的繁榮時代'),
('博格達薩爾·薩利比安', 'Boghdadar Salibian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 25, 1823, 1831, '逝世', '鄂圖曼政府', '正統', 'Ottoman records', '1826年坦志馬特改革（Tanzimat）前夕；亞美尼亞人在奧斯曼帝國的中產階級地位達到頂峰（銀行家、商人、工匠）'),
('馬提奧斯·傑波恰爾嚴', 'Matheos Jebejian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 32, 1846, 1855, '退休', '鄂圖曼政府', '正統', 'Ottoman records', '1847年《亞美尼亞民族憲章》（National Constitution）：奧斯曼帝國允許亞美尼亞人制定自治規章——亞美尼亞人稱之為「小憲法」'),
('訥赫薩爾揚·艾貢揚', 'Nerses Varzhapetian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 35, 1874, 1884, '退休', '鄂圖曼政府', '正統', 'Ottoman records', '1876年鄂圖曼帝國對亞美尼亞省份的首次大規模鎮壓；宗主教試圖通過外交手段保護亞美尼亞人；1878年柏林條約包含保護亞美尼亞少數民族的條款但未執行'),
('奧爾漢·納漢尼揚', 'Haroutiun Vehabedian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 41, 1888, 1894, '退休', '鄂圖曼政府', '正統', 'Ottoman records', '哈米德大屠殺（Hamidian massacres，1894-1896年）前夕；蘇丹阿布杜勒哈米德二世的反亞美尼亞政策；宗主教在夾縫中生存'),
('馬蒂奧斯·伊吉加澤', 'Matheos Izmirlian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 43, 1894, 1896, '流亡', '鄂圖曼政府（迫令）', '正統', 'Armenian records', '1894-1896年哈米德大屠殺——20萬-30萬亞美尼亞人遇難；伊吉加澤被迫離開君士坦丁堡；後任埃奇米亞津公教（1908-1910）'),
('伊紮基‧奧達尼揚', 'Yozghadian Khrimian（Hayrig）', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 44, 1869, 1873, '退休', '亞美尼亞社群', '正統', 'Armenian records', '「哈里里格」（父親之父）的暱稱；為亞美尼亞農民維護土地和人權——「以鐵湯勺從柏林會議（1878年）獲取亞美尼亞自治」的著名比喻；後任埃奇米亞津公教（1892-1907）——亞美尼亞民族運動的精神父親'),
('薩哈克·哈巴延（難民時代）', 'Sahak Habayan', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 75, 1913, 1916, '辭職（種族滅絕）', '亞美尼亞社群', '正統', 'Genocide records', '1915年亞美尼亞種族滅絕爆發——鄂圖曼政府命令驅逐君士坦丁堡亞美尼亞領袖（4月24日，今「亞美尼亞殉道節」）；薩哈克代表被捕和驅逐的亞美尼亞精英；宗主教座功能實際癱瘓'),
('梅斯羅布·穆塔夫揚', 'Mesrob Mutafyan', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 84, 1998, 2019, '因病失能', '亞美尼亞社群/土耳其政府', '正統', 'Armenian Patriarchate of Constantinople', '2008年診斷出早發性癡呆症；土耳其政府（依規定）遲遲不允許選舉繼任人（干預宗教事務）；宗主教座處於長期不確定狀態長達11年——直至2019年'),
('薩哈克二世·馬沙利安', 'Sahak II Mashalian', '君士坦丁堡亞美尼亞', '亞美尼亞使徒教會（君士坦丁堡）', 85, 2019, NULL, NULL, '亞美尼亞社群/土耳其政府', '正統', 'Armenian Patriarchate of Constantinople', '當代在任宗主教；土耳其政府允許後選出；今伊斯坦堡亞美尼亞人僅約5萬（1915年前約10倍）；宗主教座繼續在高壓環境下維持亞美尼亞認同');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '君士坦丁堡亞美尼亞' AND church = '亞美尼亞使徒教會（君士坦丁堡）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 耶路撒冷亞美尼亞宗主教
-- 聖城亞美尼亞社群；聖火儀式守護者
-- ==============================
('亞伯拉罕一世', 'Abraham I', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 1, 638, 669, '逝世', '亞美尼亞教會/哈里發（阿拉伯）', '正統', 'Armenian Jerusalem records', '638年阿拉伯征服耶路撒冷後；亞美尼亞人已在耶路撒冷定居數百年；阿拉伯哈里發延續亞美尼亞宗主教制度；亞美尼亞社群保管聖城多處重要地點'),
('費里奧斯一世', 'Pharios I', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 4, 780, 800, '逝世', '阿拔斯哈里發', '正統', 'Armenian Jerusalem records', '阿拔斯哈里發時代；巴格達是文化中心；耶路撒冷亞美尼亞社群在哈里發寬容政策下存續'),
('帕西卡爾一世', 'Basil I', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 12, 1165, 1189, '流亡', '薩拉丁', '正統', 'Crusader records', '十字軍王國（1099-1187年）時代亞美尼亞人在耶路撒冷的繁榮；1187年薩拉丁重新征服耶路撒冷；亞美尼亞宗主教暫時流亡'),
('薩哈克一世', 'Sahak I of Jerusalem', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 18, 1281, 1313, '逝世', '馬穆魯克蘇丹', '正統', 'Armenian Jerusalem records', '馬穆魯克時代；亞美尼亞人繼續維護聖墓教堂（Holy Sepulchre）內的亞美尼亞區域；亞美尼亞宗主教管轄聖地產業的鞏固'),
('格里高里查哈諾夫', 'Grigor of Tabriz', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 28, 1515, 1543, '逝世', '鄂圖曼蘇丹', '正統', 'Ottoman records', '1517年鄂圖曼征服耶路撒冷；蘇丹塞利姆一世的米利特制度延伸至聖地；亞美尼亞宗主教在新秩序下確立地位'),
('克里科爾一世·沙哈那扎楊', 'Krikor I Shakhnazetian', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 45, 1749, 1768, '逝世', '鄂圖曼蘇丹', '正統', 'Armenian Jerusalem records', '亞美尼亞耶路撒冷印刷廠（1833年）前夕的文化繁榮；聖雅各大教堂（Cathedral of Saint James）的修繕和擴建'),
('依撒亞二世', 'Isaia II', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 55, 1881, 1885, '逝世', '亞美尼亞社群', '正統', 'Armenian Jerusalem records', '1878年柏林條約後的聖地政治；亞美尼亞宗主教在英、俄、法、奧帝國勢力角逐的耶路撒冷的外交處境'),
('薩雷古爾·穆拉迪揚', 'Torkom Koushakian', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 65, 1939, 1947, '辭職', '英國委任管治下', '正統', 'Armenian Jerusalem records', '二戰時代；納粹中東計畫；亞美尼亞宗主教在巴勒斯坦/以色列建國動亂前夕的處境；1948年以色列建國——聖地政治劇變'),
('塔科爾·吉托敦揚', 'Tiran Nersoyan', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 68, 1956, 1990, '退休', '亞美尼亞社群', '正統', 'Armenian Jerusalem records', '以色列建國（1948年）和1967年六日戰爭後耶路撒冷地位的劇變；亞美尼亞宗主教在以色列-巴勒斯坦衝突夾縫中維護亞美尼亞區利益'),
('托科姆·馬努基揚', 'Torkom Manoogian', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 69, 1990, 2012, '退休', '亞美尼亞社群', '正統', 'Armenian Patriarchate of Jerusalem', '奧斯陸和平進程（1990年代）；2000年教宗若望保祿二世訪問耶路撒冷；千禧年朝聖；亞美尼亞宗主教參與聖墓教堂復活節聖火儀式（Holy Fire）——每年最大的亞美尼亞宗教活動'),
('努爾漢·馬努基揚', 'Nourhan Manougian', '耶路撒冷亞美尼亞', '亞美尼亞使徒教會（耶路撒冷）', 70, 2013, NULL, NULL, '亞美尼亞社群', '正統', 'Armenian Patriarchate of Jerusalem', '當代在任宗主教；2021年亞美尼亞宗主教區土地爭議（亞美尼亞區土地租賃給以色列投資人）引發全球亞美尼亞社群強烈抗議；宗主教與社群的公開衝突；以哈戰爭（2023年起）對耶路撒冷亞美尼亞社群的衝擊');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '耶路撒冷亞美尼亞' AND church = '亞美尼亞使徒教會（耶路撒冷）'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 東方公教（馬蘭卡拉正統敘利亞教會，印度）
-- 使徒多馬傳統；喀拉拉邦基督徒
-- ==============================
('帕烏洛斯·馬爾·格雷戈里奧斯', 'Paulose Mar Gregorios', '東方公教座（馬蘭卡拉）', '馬蘭卡拉正統敘利亞教會', 9, 1975, 1996, '逝世', '馬蘭卡拉正統主教公會議', '正統', 'Malankara Orthodox Syrian Church', '印度最偉大的東方神學家之一；世界教協（WCC）中央委員會副主席；致力於科學與神學對話；著作包括《宇宙、人類和上帝》（Cosmic Man）；「東方教父」傳統的復興者；格雷戈里奧斯在德里工作期間推動教育和社會服務'),
('巴西略斯·馬爾托馬·馬太一世', 'Baselios Marthoma Mathews I', '東方公教座（馬蘭卡拉）', '馬蘭卡拉正統敘利亞教會', 12, 2005, 2021, '逝世', '馬蘭卡拉正統主教公會議', '正統', 'Malankara Orthodox Syrian Church', '長期致力於解決馬蘭卡拉正統與雅各賓派（Jacobite）之間對教會財產和管轄的爭議（印度法院多次裁決）；2017年印度最高法院裁定馬蘭卡拉正統對主要教堂的管轄權；推動馬蘭卡拉教會全球化'),
('巴西略斯·馬爾托馬·馬太三世', 'Baselios Marthoma Mathews III', '東方公教座（馬蘭卡拉）', '馬蘭卡拉正統敘利亞教會', 14, 2021, NULL, NULL, '馬蘭卡拉正統主教公會議', '正統', 'Malankara Orthodox Syrian Church', '當代在任東方公教；今約300萬信徒，主要在喀拉拉邦及全球印度僑民社群；使徒多馬（Thomas Christians）傳統在現代印度的延續');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '東方公教座（馬蘭卡拉）' AND church = '馬蘭卡拉正統敘利亞教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
