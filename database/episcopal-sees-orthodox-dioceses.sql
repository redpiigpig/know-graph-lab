-- ============================================================
-- 東正教主要都主教區及大主教區主教座
-- ============================================================

INSERT INTO episcopal_sees
  (name_zh, name_en, see_zh, church, tradition, rite, founded_year, abolished_year, status,
   current_patriarch, location, notes, sources)
VALUES

-- 普世牧首轄下
('帖撒羅尼迦大主教區', 'Archdiocese of Thessaloniki', '帖撒羅尼迦', '東正教', '東正教', '拜占廷禮',
 50, NULL, 'current', 'Philotheos Karamitsos（2019–）', '希臘帖撒羅尼迦',
 '保羅使徒書信《帖撒羅尼迦前後書》的受信教會；5世紀為西方（羅馬）伊里里亞代牧區；後歸普世牧首；1913年希臘佔領後改隸希臘正教會', 'Synaxarion; Fedalto'),

('克里特大主教區', 'Church of Crete', '克里特', '東正教', '東正教', '拜占廷禮',
 60, NULL, 'current', 'Eugenios Philippou（2023–）', '希臘克里特',
 '普世牧首直轄的「半自治」教會；保羅書信提多書（提特斯書）的受信地；2016年第一次泛正教會議在此召開', 'Orthodox Church of Crete'),

('多德卡尼斯群島大主教區', 'Archdiocese of Dodecanese', '多德卡尼斯', '東正教', '東正教', '拜占廷禮',
 95, NULL, 'current', 'Metropolitan of Rhodes', '希臘羅德島',
 '普世牧首直轄；羅德島、帕特莫斯（啟示錄撰寫地）等島嶼；拜占廷傳統重鎮', 'Ecumenical Patriarchate records'),

-- 希臘正教會（Church of Greece）
('雅典及全希臘大主教區', 'Archdiocese of Athens', '雅典', '東正教', '東正教', '拜占廷禮',
 54, NULL, 'current', 'Ieronymos II（2008–）', '希臘雅典',
 '使徒保羅於雅典各火神廟演說（徒17:16–34）；現代希臘正教會首席大主教座；1850年自立', 'Church of Greece'),

('帖撒洛尼迦都主教區', 'Metropolis of Thessaloniki', '帖撒羅尼迦正教', '東正教', '東正教', '拜占廷禮',
 50, NULL, 'current', 'Metropolitan Panteleimon', '希臘帖撒羅尼迦',
 '希臘正教會管轄；希臘第二大城市；聖狄米特里歐斯（守護聖人）殉道地；1913年脫離鄂圖曼後歸希臘', 'Church of Greece'),

('科林斯都主教區', 'Metropolis of Corinth', '科林斯', '東正教', '東正教', '拜占廷禮',
 50, NULL, 'current', 'Dionysios', '希臘科林斯',
 '保羅書信《哥林多前後書》的受信教會；保羅曾在此傳教18個月（徒18:11）', 'Church of Greece'),

('帕特雷都主教區', 'Metropolis of Patras', '帕特雷', '東正教', '東正教', '拜占廷禮',
 67, NULL, 'current', 'Chrysostomos', '希臘帕特雷',
 '使徒安得烈殉道地（傳統）；其X形十字架成為蘇格蘭旗幟圖案的來源', 'Church of Greece'),

-- 俄羅斯正教會
('聖彼得堡都主教區', 'Metropolis of Saint Petersburg', '聖彼得堡', '俄羅斯正教會', '東正教', '拜占廷禮',
 1742, NULL, 'current', 'Varsonofy（2014–）', '俄羅斯聖彼得堡',
 '1703年彼得大帝建城；1742年設主教座；1914年改名彼得格勒、1924年改列寧格勒、1991年恢復聖彼得堡；阿列克謝（Aleksiy）大主教1990年出任莫斯科牧首', 'Moscow Patriarchate'),

('基輔及全烏克蘭都主教區（莫斯科牧首轄）', 'Metropolis of Kyiv (Moscow Patriarchate)', '基輔（莫斯科）', '俄羅斯正教會', '東正教', '拜占廷禮',
 988, NULL, 'current', 'Onufriy（2014–）', '烏克蘭基輔',
 '988年弗拉基米爾大公在第聶伯河受洗——東斯拉夫基督化的根源；歷史上是莫斯科牧首的前身；1686年牧首管轄從君士坦丁堡移至莫斯科；2019年普世牧首授予烏克蘭正教會自主性', 'Moscow Patriarchate'),

('基輔及全烏克蘭都主教區（普世牧首轄）', 'Metropolis of Kyiv (Orthodox Church of Ukraine)', '基輔（烏克蘭）', '烏克蘭正教會', '東正教', '拜占廷禮',
 988, NULL, 'current', 'Epifaniy（2019–）', '烏克蘭基輔',
 '2019年1月5日普世牧首巴爾多祿茂授予自主敕令（tomos）；由烏克蘭正教會-基輔牧首轄區和烏克蘭自主正教會合併而成；莫斯科牧首拒絕承認', 'Ecumenical Patriarchate; OCU'),

('明斯克及白俄羅斯都主教區', 'Metropolis of Minsk', '明斯克', '俄羅斯正教會', '東正教', '拜占廷禮',
 1317, NULL, 'current', 'Benjamin（2021–）', '白俄羅斯明斯克',
 '白俄羅斯正教的中心；長期為俄羅斯正教會的一部分；盧卡申科威權體制下的教會角色複雜', 'Moscow Patriarchate'),

('利維夫及加利西亞都主教區（烏克蘭正教）', 'Metropolis of Lviv (OCU)', '利維夫（正教）', '烏克蘭正教會', '東正教', '拜占廷禮',
 1539, NULL, 'current', 'Filaret（Kucheruk）', '烏克蘭利維夫',
 '歷史上烏克蘭希臘禮天主教（UGCC）和正教的爭奪之地；現烏克蘭正教會管轄', 'OCU'),

-- 塞爾維亞正教會
('蒙特內哥羅及沿海都主教區', 'Metropolis of Montenegro and the Littoral', '黑山', '塞爾維亞正教會', '東正教', '拜占廷禮',
 1220, NULL, 'current', 'Joanikije（2020–）', '黑山波德戈里察',
 '歷史上塞蒂涅都主教區；安菲洛齊烏斯（Amfilohije）1990–2020年在任；2020年黑山新教會法引發爭議——塞正教會抵制', 'Serbian Orthodox Church'),

('薩格勒布-盧布爾雅那都主教區', 'Metropolis of Zagreb-Ljubljana', '薩格勒布（正教）', '塞爾維亞正教會', '東正教', '拜占廷禮',
 1708, NULL, 'current', 'Porfirije（2014–2020）/Jovan', '克羅埃西亞薩格勒布',
 '涵蓋克羅埃西亞、斯洛維尼亞；南斯拉夫戰爭（1991–1995）期間受嚴重衝擊；塞裔人口流離失所後教區縮小', 'Serbian Orthodox Church'),

('波士尼亞-赫塞哥維那都主教區（薩拉熱窩）', 'Metropolitanate of Dabar-Bosnia', '薩拉熱窩（正教）', '塞爾維亞正教會', '東正教', '拜占廷禮',
 1220, NULL, 'current', 'Hrizostom（2021–）', '波士尼亞薩拉熱窩',
 '歷史悠久的都主教區；奧斯曼時代的東正教存續；代頓協議（1995）後的波士尼亞三族共存', 'Serbian Orthodox Church'),

-- 羅馬尼亞正教會
('特蘭西瓦尼亞都主教區（西比烏）', 'Metropolitanate of Transylvania (Sibiu)', '特蘭西瓦尼亞', '羅馬尼亞正教會', '東正教', '拜占廷禮',
 1082, NULL, 'current', 'Laurenţiu Streza（1994–）', '羅馬尼亞西比烏',
 '特蘭西瓦尼亞羅馬尼亞人的精神中心；安得烈·沙古納（1848–1873）為最重要的都主教——羅馬尼亞民族精神的奠基者', 'Romanian Orthodox Church'),

('摩爾達維亞及布科維納都主教區（雅西）', 'Metropolitanate of Moldavia and Bukovina', '雅西', '羅馬尼亞正教會', '東正教', '拜占廷禮',
 1386, NULL, 'current', 'Teofan（2008–）', '羅馬尼亞雅西',
 '摩爾達維亞公國的精神中心；史蒂芬大公（Stefan cel Mare）奉獻的多座教堂；米特羅芬·克里斯蒂亞（Dosoftei）翻譯羅馬尼亞語詩篇（1673）', 'Romanian Orthodox Church'),

('奧爾提尼亞都主教區（克拉約瓦）', 'Metropolitanate of Oltenia', '克拉約瓦', '羅馬尼亞正教會', '東正教', '拜占廷禮',
 1370, NULL, 'current', 'Irineu（2008–）', '羅馬尼亞克拉約瓦',
 '瓦拉基亞西部地區；許多拜占廷風格教堂和修道院', 'Romanian Orthodox Church'),

('巴納特都主教區（蒂米什瓦拉）', 'Metropolitanate of Banat', '蒂米什瓦拉', '羅馬尼亞正教會', '東正教', '拜占廷禮',
 1865, NULL, 'current', 'Ioan Selejan（2014–）', '羅馬尼亞蒂米什瓦拉',
 '1989年羅馬尼亞革命（推翻西奧塞斯庫）從蒂米什瓦拉爆發；科內亞努都主教（Corneanu, 1962–2014）是羅馬尼亞最重要的合一運動推動者', 'Romanian Orthodox Church'),

-- 保加利亞正教會
('普洛夫迪夫都主教區', 'Diocese of Plovdiv', '普洛夫迪夫', '保加利亞正教會', '東正教', '拜占廷禮',
 46, NULL, 'current', 'Nikolay（2013–）', '保加利亞普洛夫迪夫',
 '古腓立比城附近；保加利亞第二大城；歷史上是希臘化城市菲利浦波利斯（Philippopolis）', 'Bulgarian Orthodox Church'),

('大特爾諾沃都主教區', 'Diocese of Tarnovo', '大特爾諾沃', '保加利亞正教會', '東正教', '拜占廷禮',
 1235, NULL, 'current', 'Grigory', '保加利亞大特爾諾沃',
 '第二保加利亞帝國首都（1185–1393）；1235年設立宗主教座（獨立於君士坦丁堡）；鄂圖曼征服後被廢除', 'Bulgarian Orthodox Church'),

-- 格魯吉亞正教會
('格魯吉亞-姆茨赫塔宗主教區', 'Catholicate-Patriarchate of All Georgia', '第比利斯', '格魯吉亞正教會', '東正教', '拜占廷禮',
 327, NULL, 'current', 'Ilia II（1977–）', '格魯吉亞第比利斯',
 '聖尼諾（Nina）334年傳教；古姆茨赫塔（Mtskheta）為歷史首都；現宗主教座在第比利斯；伊利亞二世在任近50年——東正教在位最久的宗主教之一', 'Georgian Orthodox Church');
