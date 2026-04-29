-- ============================================================
-- 東方天主教主教傳承——主要東儀天主教宗主教及大主教座
-- UGCC（利維夫/基輔）、馬龍尼（貝克爾凱）、梅勒基特（大馬士革）
-- 加色丁（摩蘇爾/厄比爾）、亞美尼亞天主教（布佐馬爾）
-- ============================================================

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 利維夫烏克蘭希臘禮天主教（UGCC）
-- 1596年布列斯特合一；東儀天主教的歷史重鎮
-- ==============================
('米哈伊洛·拉霍扎', 'Mykhailo Rahoza', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 1, 1596, 1599, '逝世', '教宗克肋孟八世', '正統', 'UGCC records; Brest Union documents', '1596年10月布列斯特合一的主要推動者；與烏克蘭-白俄羅斯主教們簽署合一協議——承認羅馬教宗的優先地位，但保留拜占廷禮儀；此事件分裂了基輔都主教轄區，並引發長達數個世紀的東正教與東儀天主教衝突'),
('依波利特·波裘伊', 'Ipatiy Potiy', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 2, 1599, 1613, '逝世', '教宗克肋孟八世', '正統', 'UGCC records', '布列斯特合一最有力的神學辯護者和組織者；對抗哥薩克領袖的正教抵制；奠定東儀天主教在基輔都主教轄區的制度基礎'),
('約瑟夫·維拉明·盧茲基', 'Yosyf Veliamin Rutsky', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 3, 1613, 1637, '逝世', '教宗保祿五世', '正統', 'UGCC records', '在波蘭立陶宛聯邦的政治庇護下鞏固東儀天主教架構；創立聖巴西略修道院會（OSBM）——東儀天主教的修道核心；培育學術神職人員'),
('約瑟夫·魯本·舒姆揚斯基', 'Yosyp Shumliansky', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 7, 1668, 1708, '逝世', '教宗英諾森十一世', '正統', 'UGCC records', '利維夫主教；最初秘密歸附羅馬（1677年），正式公開歸附時間拖延至1700年——象徵東儀天主教在利維夫的最終鞏固；哈布斯堡和波蘭立陶宛的邊境地區政治'),
('阿塔那西·赫雷布尼茨基', 'Atanasiy Sheptytsky', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 11, 1715, 1746, '逝世', '教宗克肋孟十一世', '正統', 'UGCC records', '赫雷布尼茨基家族（後生安德列·謝普蒂茨基）是烏克蘭天主教的重要貴族家族；1736年布列斯特合一後百周年的鞏固時代；利維夫東儀天主教文化的繁榮'),
('安德列·謝普蒂茨基', 'Andrei Sheptytsky', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 16, 1900, 1944, '逝世', '教宗利奧十三世', '正統', 'UGCC records; Yad Vashem', '44年在任——UGCC有史以來最重要的主教；二戰期間秘密藏匿150-160名猶太人（包括拉比大衛·加菲爾卡），1944年以色列以色列亞德瓦謝姆（Yad Vashem）將其列為「國際義人」（Righteous Among Nations）；1941-1944年德國佔領烏克蘭期間親眼目睹大屠殺並公開抗議——向教宗庇護十二世和希特勒分別寫信抗議；推動烏克蘭文化和民族認同的東儀天主教框架；2015年列真福'),
('約瑟夫·斯利皮', 'Josyf Slipyj', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 17, 1944, 1984, '逝世（流亡羅馬）', '教宗庇護十二世', '正統', 'UGCC records; Vatican', '1946年史達林強制解散UGCC（全部主教被捕；以「通敵」罪名流放西伯利亞18年）；斯利皮在西伯利亞勞改營中度過1945-1963年；1963年甘迺迪政府和梵二大公會議壓力下獲釋；流亡羅馬，創立烏克蘭天主教大學；1975年教宗保羅六世任命為「主教長」（Major Archbishop）；烏克蘭流亡教會的精神象徵'),
('米羅斯拉夫·盧巴齊夫斯基', 'Myroslav Ivan Lubachivsky', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 18, 1984, 2000, '退休', '教宗若望保祿二世', '正統', 'UGCC records', '1990年蘇聯宗教自由化——盧巴齊夫斯基在流亡38年後回到利維夫；教宗若望保祿二世（波蘭人）在東歐天主教復興中的重要支持；利維夫UGCC大教堂的重建；UGCC從地下轉為地上教會'),
('盧伯米爾·胡薩爾', 'Lubomyr Husar', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 19, 2001, 2011, '退休', '教宗若望保祿二世', '正統', 'UGCC records', '樞機（2001年）；2004年將UGCC大總主教座從利維夫遷往基輔——象徵UGCC從加利西亞地方教會轉型為全烏克蘭教會；廣場革命（2004年橙色革命）期間的教會立場；推動烏克蘭天主教-東正教對話'),
('斯維亞托斯拉夫·謝甫丘克', 'Sviatoslav Shevchuk', '利維夫（烏克蘭希臘天主教）', '烏克蘭希臘禮天主教會', 20, 2011, NULL, NULL, '教宗本篤十六世', '正統', 'UGCC records', '大總主教（Major Archbishop）；2022年2月24日俄烏全面戰爭爆發後留守基輔——每日發布戰情消息和精神支持影片；成為烏克蘭抵抗的重要精神象徵；多次訪問前線；公開批評俄羅斯正教會牧首基里爾為戰爭辯護的言論');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '利維夫（烏克蘭希臘天主教）' AND church = '烏克蘭希臘禮天主教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 馬龍尼天主教安提阿宗主教（貝克爾凱）
-- 黎巴嫩山；最大東儀天主教會之一
-- ==============================
('約翰·馬龍（聖馬龍傳統）', 'John Maron', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 1, 685, 707, '逝世', '教會傳統', '正統', 'Maronite tradition', '傳統首任馬龍尼宗主教；聖馬龍（Saint Maron，4世紀）的隱修傳統在此後制度化；黎巴嫩山（Qadisha Valley）成為馬龍尼修道院集中地；卡爾西頓信仰的擁護者（單意志論異端期間）'),
('提奧費拉克托斯', 'Theophylactos', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 3, 750, 770, '逝世', '教會', '正統', 'Maronite records', '阿拔斯哈里發時代；馬龍尼人在黎巴嫩山的鞏固；與君士坦丁堡的微妙關係（馬龍尼教義爭議）'),
('依薩亞', 'Isaia', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 15, 1110, 1132, '逝世', '教會', '正統', 'Crusader records', '第一次十字軍東征（1099年）後；馬龍尼宗主教正式向羅馬教宗帕斯卡爾二世宣示服從（1100年）——馬龍尼-羅馬合一的歷史性確認；十字軍國家為馬龍尼人提供政治保護'),
('傑雷米亞二世', 'Jeremias II', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 23, 1278, 1282, '逝世', '教會', '正統', 'Maronite records', '1261年馬穆魯克擊敗十字軍後；馬龍尼人在黎巴嫩山繼續存活；蒙古-馬龍尼接觸（蒙古聯合反穆斯林戰略）'),
('約翰·傑雷吉', 'Yuhanna al-Jraji', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 35, 1524, 1567, '逝世', '教會/鄂圖曼蘇丹', '正統', 'Maronite records', '鄂圖曼帝國統治黎巴嫩（1516年後）；馬龍尼宗主教在鄂圖曼-米利特制度和羅馬的雙重關係下維持社群'),
('彌額爾·利扎齊', 'Mikhael Rizzi', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 40, 1567, 1581, '逝世', '教宗庇護五世', '正統', 'Maronite records', '羅馬馬龍尼學院（Maronite College in Rome）創立（1584年）——馬龍尼神學和精英教育的重要里程碑；特倫托大公會議後的天主教改革對馬龍尼教會的影響'),
('傑夫里·米特里', 'Jibra''il Blawzawi', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 45, 1657, 1670, '逝世', '教宗亞歷山大七世', '正統', 'Maronite records', '1649年：馬龍尼宗主教正式稱「安提阿宗主教」（Patriarch of Antioch）——強調使徒傳承；法蘭西保護黎巴嫩馬龍尼人的傳統（路易十四時代）'),
('雅各·阿烏德', 'Yaqub Awwad', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 48, 1705, 1733, '逝世', '教宗克肋孟十一世', '正統', 'Maronite records', '1736年黎巴嫩公會議（Synod of Lebanon）的準備時代；奠定馬龍尼教規和禮儀的現代架構'),
('約瑟夫·提安', 'Yusuf at-Tian', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 49, 1733, 1742, '逝世', '教宗克肋孟十二世', '正統', 'Maronite records', '1736年黎巴嫩公會議（Concilium Libanese）——馬龍尼教會現代組織的奠基文件；規範聖職訓練、宗主教選舉程序和禮儀改革'),
('米漢納·哈亞克', 'Mikhael el-Khazen', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 55, 1796, 1820, '逝世', '教宗庇護六世', '正統', 'Maronite records', '拿破崙1798年埃及遠征——馬龍尼教會的法國保護傳統在大革命後的持續；奧斯曼帝國與馬龍尼的關係'),
('胡比什·霍亞格', 'Hubaysh al-Khazen', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 57, 1823, 1845, '逝世', '教宗利奧十二世', '正統', 'Maronite records', '1840年馬龍尼-德魯茲衝突（Mountain War）；英法介入黎巴嫩山政治；1843年雙區制（Double Qaimaqamate）建立'),
('馬西莫·瑪扎里納', 'Massimo Jummayil', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 60, 1854, 1890, '逝世', '教宗庇護九世', '正統', 'Maronite records', '1860年達馬士革和黎巴嫩山屠殺（馬龍尼人被屠殺，法國出兵）；1861年黎巴嫩山區自治省（Mutasarrifate）設立；馬龍尼教會在奧斯曼改革後的半自治地位'),
('埃利亞斯·霍亞克', 'Elias Peter Hoyek', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 63, 1898, 1931, '逝世', '教宗利奧十三世', '正統', 'Maronite records; Paris Peace Conference', '1919年巴黎和平會議：霍亞克宗主教親赴巴黎要求設立黎巴嫩大黎巴嫩（Grand Liban）——在凡爾賽的外交努力直接促成1920年法屬大黎巴嫩的設立；馬龍尼教會是黎巴嫩國家建立的核心力量'),
('安托尼·阿里達', 'Antun Arida', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 64, 1932, 1955, '逝世', '教宗庇護十一世', '正統', 'Maronite records', '1943年黎巴嫩獨立——馬龍尼宗主教在「不成文憲法」（National Pact，1943年）中的核心角色：馬龍尼總統、遜尼總理、什葉議長的族群分權安排；阿里達是現代黎巴嫩建國政治的參與者'),
('保羅·梅烏奇', 'Boulos Meouchi', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 65, 1955, 1975, '逝世', '教宗庇護十二世', '正統', 'Maronite records', '1958年黎巴嫩政治危機（艾森豪威爾美軍登陸黎巴嫩）；梵二大公會議（1962-1965年）的馬龍尼代表；1967年以色列-阿拉伯戰爭後巴勒斯坦難民湧入黎巴嫩，開始改變黎巴嫩人口結構'),
('安東尼·哈雷克', 'Antoun Khoreich', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 66, 1975, 1986, '退休', '教宗保羅六世', '正統', 'Maronite records', '黎巴嫩內戰（1975-1990年）的開始；基督教民兵（卡泰布黨，Kataeb）和巴勒斯坦武裝的衝突；1982年薩布拉-夏蒂拉屠殺（以色列入侵和黎巴嫩基督教民兵暴行）；宗主教在複雜的內戰政治中的立場'),
('納斯拉拉·斯費伊爾', 'Nasrallah Sfeir', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 67, 1986, 2011, '退休', '教宗若望保祿二世', '正統', 'Maronite records', '樞機；黎巴嫩內戰結束（1990年塔伊夫協議）後的和解；2005年雪松革命（Cedar Revolution）——斯費伊爾是反對敘利亞駐軍的精神領袖；敘利亞軍撤出黎巴嫩（2005年）'),
('貝沙拉·拉希', 'Bechara Boutros al-Rahi', '貝克爾凱（馬龍尼）', '馬龍尼天主教會', 68, 2011, NULL, NULL, '教宗本篤十六世', '正統', 'Maronite records', '樞機（2012年）；2019-2020年黎巴嫩政治抗議（「旋轉閘革命」）中呼籲改革；2020年8月4日貝魯特港口大爆炸（馬龍尼社群所在地受重創）；黎巴嫩政治癱瘓和經濟崩潰中的教會聲音；呼籲聯合國託管黎巴嫩的爭議言論');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '貝克爾凱（馬龍尼）' AND church = '馬龍尼天主教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 大馬士革梅勒基特希臘天主教大主教區
-- 安提阿希臘天主教宗主教駐地；敘利亞內戰重創
-- ==============================
('西里爾六世·塔納斯', 'Cyril VI Tanas', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 1, 1724, 1759, '逝世', '梅勒基特主教公會議', '正統', 'Melkite records', '1724年梅勒基特教會正式分裂——從安提阿希臘正教脫離歸附羅馬；西里爾六世是首任「安提阿梅勒基特希臘天主教宗主教」；君士坦丁堡普世牧首拒絕承認，安插親俄主教對抗——東西方教會政治在中東的延伸'),
('依諾森·奧達', 'Innocent Aouda', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 2, 1759, 1788, '逝世', '梅勒基特主教公會議', '正統', 'Melkite records', '梅勒基特教會體制的鞏固；阿拉伯語禮儀文本的翻譯；敘利亞-黎巴嫩基督教共同體的建立'),
('格利高里二世·周哈耶', 'Grigorios II Jouhayyel', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 6, 1835, 1864, '逝世', '梅勒基特主教公會議', '正統', 'Melkite records', '1840年代黎巴嫩山和大馬士革的動蕩；1860年大馬士革屠殺（基督徒遇難）；法蘭西保護基督徒社群的介入'),
('格利高里四世·哈達德', 'Grigorios IV Haddad', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 9, 1906, 1928, '逝世', '梅勒基特主教公會議', '正統', 'Melkite records', '第一次世界大戰；奧斯曼帝國解體；法國委任統治敘利亞和黎巴嫩（1920年後）；梅勒基特宗主教在新的民族國家格局中的定位'),
('馬克西莫斯四世·塞格', 'Maximos IV Saigh', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 11, 1947, 1967, '退休', '梅勒基特主教公會議', '正統', 'Vatican II records; Melkite Patriarchate', '梵二大公會議（1962-1965年）中最重要的東方天主教代言人——拒絕以拉丁語演講；主張恢復東方教會傳統；批評天主教的西方文化霸權；梵二後東西方教會對話的先驅；「我是首批東方基督徒——西方是我的子教會」名言；1965年教宗保羅六世授予樞機帽'),
('埃利亞斯·佐格比', 'Elias Zoghby', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 12, 1967, 2000, '退休', '梅勒基特主教公會議', '正統', 'Melkite records', '1995年「佐格比聲明」（Zoghby declaration）：以個人名義聲稱接受東正教信仰（不接受羅馬教宗判無誤論）——引發梵蒂岡嚴厲批評，後撤回聲明；梅勒基特的東西方張力的縮影'),
('格利高里三世·拉漢姆', 'Grigorios III Laham', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 13, 2000, 2017, '退休', '梅勒基特主教公會議', '正統', 'Melkite Patriarchate', '2011年敘利亞內戰爆發後的梅勒基特教會；拉漢姆宗主教力主反對外國干涉、支持阿薩德政府——在西方引發爭議；大量梅勒基特信眾逃離敘利亞'),
('約瑟夫·阿貝西', 'Youssef Absi', '大馬士革（梅勒基特）', '梅勒基特希臘天主教會', 14, 2017, NULL, NULL, '梅勒基特主教公會議', '正統', 'Melkite Patriarchate', '當代在任宗主教；在敘利亞內戰持續的環境下維持梅勒基特教會架構；教宗方濟각2019年阿聯酋訪問後的宗教間對話推動；梅勒基特信眾大規模流亡後的「教會在離散中」管理');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '大馬士革（梅勒基特）' AND church = '梅勒基特希臘天主教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 加色丁天主教摩蘇爾大主教區
-- 尼尼微平原；2014年ISIS幾乎終結千年基督徒歷史
-- ==============================
('尤塞夫·甘尼瑪', 'Yusuf Ghanima', '摩蘇爾（加色丁）', '加色丁天主教會', 1, 1859, 1879, '逝世', '教宗庇護九世', '正統', 'Chaldean Catholic records', '摩蘇爾（古代尼尼微對岸）是東方基督教最古老的中心之一；加色丁天主教在鄂圖曼帝國的最大集中地；與「東方教會」（Church of the East，亞述基督徒）的平行存在'),
('艾利亞·阿博那', 'Eliya Aboona', '摩蘇爾（加色丁）', '加色丁天主教會', 3, 1892, 1906, '逝世', '教宗利奧十三世', '正統', 'Chaldean Catholic records', '鄂圖曼帝國末期；1914-1918年一戰期間奧斯曼帝國對亞述-加色丁基督徒的大屠殺（Seyfo，1914-1924年，死亡約30萬）'),
('彼得·阿扎里亞', 'Petros Azarya', '摩蘇爾（加色丁）', '加色丁天主教會', 5, 1917, 1931, '逝世', '教宗本篤十五世', '正統', 'Chaldean records', '英國委任統治伊拉克（1920年後）；基督徒在新的伊拉克王國的地位；尼尼微平原作為加色丁基督徒的家園'),
('保祿二世·契科', 'Paulos II Cheikho', '摩蘇爾（加色丁）', '加色丁天主教會', 8, 1958, 1989, '逝世', '教宗若望二十三世', '正統', 'Chaldean records', '1958年伊拉克革命（卡塞姆推翻哈希姆王朝）；復興黨政府（巴阿思）對基督徒的複雜政策；伊拉克戰爭（1980-1988年，伊朗-伊拉克）的衝擊；薩達姆·侯賽因政府中的基督徒相對保護時期'),
('邦巴迪爾·圖瑪', 'Raphaël Bidawid', '摩蘇爾（加色丁）', '加色丁天主教會', 9, 1989, 2003, '逝世', '教宗若望保祿二世', '正統', 'Chaldean records', '1991年海灣戰爭後的制裁時代；伊拉克基督徒的苦境；比達維德宗主教（摩蘇爾晉升為加色丁宗主教）；2003年美伊戰爭爆發——開始了一系列對基督徒的迫害'),
('米漢納·迪烏', 'Emmanuel III Delly', '摩蘇爾（加色丁）', '加色丁天主教會', 10, 2003, 2013, '退休', '加色丁主教公會議', '正統', 'Chaldean records', '樞機（2007年）；美國入侵伊拉克後（2003年）基督徒遭受系統性攻擊——教堂爆炸、綁架、暗殺；大量基督徒流離失所；2003年後伊拉克基督徒從約150萬降至30萬以下'),
('路易·薩科', 'Louis Raphaël I Sako', '摩蘇爾（加色丁）', '加色丁天主教會', 11, 2013, NULL, NULL, '加色丁主教公會議', '正統', 'Chaldean Catholic Patriarchate', '樞機（2018年）；2014年ISIS佔領摩蘇爾——「基督徒應信仰伊斯蘭、繳稅、離開或死亡」命令；尼尼微平原基督徒在24小時內幾乎全部逃離；薩科宗主教（當時在巴格達）緊急主持救援行動；2017年ISIS被驅逐後推動基督徒回歸；2019年薩科辭去國家少數民族委員會主席職位以抗議伊拉克政府侵害基督徒財產；2023年教宗方濟각於亞歷山大訪問時致謝薩科的牧民工作');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '摩蘇爾（加色丁）' AND church = '加色丁天主教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;

INSERT INTO episcopal_succession
  (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes) VALUES

-- ==============================
-- 亞美尼亞天主教宗主教區（布佐馬爾）
-- 1742年建立；亞美尼亞禮天主教
-- ==============================
('亞伯拉罕·彼得一世', 'Abraham Pierre I Ardzivian', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 1, 1742, 1749, '逝世', '教宗本篤十四世', '正統', 'Armenian Catholic records', '首任亞美尼亞天主教宗主教；曾是阿勒坡的亞美尼亞使徒教會主教，後歸附羅馬（1737年）；1742年教宗本篤十四世正式確認為安提阿亞美尼亞天主教宗主教；布佐馬爾修道院成為宗主教總部'),
('米迦勒·加薩達', 'Mikael Kasparian', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 4, 1774, 1800, '逝世', '教宗庇護六世', '正統', 'Armenian Catholic records', '法國大革命和拿破崙戰爭時代；鄂圖曼帝國境內亞美尼亞天主教徒的處境'),
('亞歷山大·貝澤傑揚', 'Aleksandr Behzadian', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 11, 1911, 1929, '逝世', '教宗庇護十世', '正統', 'Armenian Catholic records', '1915年亞美尼亞種族滅絕——亞美尼亞天主教徒同樣遭受迫害；大量信眾流亡；宗主教在難民中的緊急牧民'),
('葛雷戈里·彼得十四世', 'Grégoire-Pierre XIV Agagianian', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 12, 1937, 1962, '辭職（調任）', '教宗庇護十一世', '正統', 'Armenian Catholic records; Vatican', '樞機（1946年）；1958年教宗選舉中的主要候選人——多輪投票中票數最多但未過三分之二，最終由隆卡利（若望二十三世）當選；1962年辭去宗主教職調任傳信部部長——東方天主教人在梵二改革中的重要地位'),
('讓·皮埃爾·加斯帕里揚', 'Grégoire-Pierre Ghabroyan', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 17, 1999, 2015, '退休', '教宗若望保祿二世', '正統', 'Armenian Catholic records', '2001年教宗若望保祿二世訪問亞美尼亞（歷史性首次）；亞美尼亞天主教徒在亞美尼亞共和國的地位（少數群體）'),
('拉法埃爾·米納謝安', 'Raphaël Bedros XXI Minassian', '布佐馬爾（亞美尼亞天主教）', '亞美尼亞天主教會', 18, 2015, NULL, NULL, '教宗方濟각', '正統', 'Armenian Catholic Patriarchate', '樞機（2022年）——教宗方濟각在歷史上首次任命在任亞美尼亞天主教宗主教為樞機（非退休）；2023年9月阿塞拜疆攻占納卡（納戈爾諾-卡拉巴赫）——亞美尼亞人逃離，包括亞美尼亞天主教社群；全球亞美尼亞天主教徒的牧民挑戰');

WITH ranked AS (
  SELECT id, succession_number,
    LAG(id) OVER (PARTITION BY see, church ORDER BY succession_number) AS prev_id
  FROM episcopal_succession
  WHERE see = '布佐馬爾（亞美尼亞天主教）' AND church = '亞美尼亞天主教會'
)
UPDATE episcopal_succession es
SET predecessor_id = r.prev_id
FROM ranked r
WHERE es.id = r.id AND r.prev_id IS NOT NULL;
