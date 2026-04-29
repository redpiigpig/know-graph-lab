-- ============================================================
-- 宗主教座以外的東正教自主教會 — 補充至 episcopal_sees
-- 執行前請確保已執行 episcopal-sees.sql 及 episcopal-sees-seed.sql
-- ============================================================

INSERT INTO episcopal_sees (name_zh, name_en, see_zh, church, tradition, rite, founded_year, status,
  current_patriarch_zh, current_patriarch_en, incumbent_since, location, notes, sources) VALUES

('塞浦路斯自主教會',
 'Autocephalous Greek Orthodox Church of Cyprus',
 '尼科西亞', '東正教（塞浦路斯）', '東正教', '拜占庭禮',
 431, '現存',
 '大主教喬治三世', 'Archbishop George III', 2022,
 '賽普勒斯尼科西亞',
 '431 年以弗所大公會議正式確認自主地位，是東正教中歷史最古老的自主教會之一。傳統由使徒巴拿巴建立。',
 'Council of Ephesus (431) canon 8; Church of Cyprus records'),

('希臘自主教會',
 'Autocephalous Greek Orthodox Church in Greece',
 '雅典', '東正教（希臘）', '東正教', '拜占庭禮',
 1833, '現存',
 '大主教耶羅尼莫斯二世', 'Archbishop Ieronymos II', 2008,
 '希臘雅典',
 '1833 年希臘獨立後宣布自主；1850 年君士坦丁堡普世宗主教正式承認。北部希臘教區仍屬君士坦丁堡管轄。',
 'Ecumenical Patriarchate Tomos (1850)'),

('波蘭自主正教會',
 'Polish Autocephalous Orthodox Church',
 '華沙', '東正教（波蘭）', '東正教', '拜占庭禮',
 1924, '現存',
 '都主教薩瓦', 'Metropolitan Sawa', 1998,
 '波蘭華沙',
 '1924 年 11 月 13 日由君士坦丁堡普世宗主教授予自主地位（Tomos）。二戰後曾一度受莫斯科管轄，1948 年莫斯科授予新的自主地位。',
 'Ecumenical Patriarchate Tomos (1924); Moscow Patriarchate Tomos (1948)'),

('阿爾巴尼亞自主正教會',
 'Autocephalous Orthodox Church of Albania',
 '地拉那', '東正教（阿爾巴尼亞）', '東正教', '拜占庭禮',
 1937, '現存',
 '大主教約亞尼', 'Archbishop Joani', 2025,
 '阿爾巴尼亞地拉那',
 '1922 年宣布自主；1937 年 4 月 12 日君士坦丁堡正式承認。1967–1990 年共產政府宣布阿爾巴尼亞為「無神論國家」，教會被迫中斷；1992 年由安納斯塔修斯大主教重建。',
 'Ecumenical Patriarchate Tomos (1937); Church records'),

('捷克及斯洛伐克正教會',
 'Orthodox Church of the Czech Lands and Slovakia',
 '布拉格', '東正教（捷克斯洛伐克）', '東正教', '拜占庭禮',
 1951, '現存',
 '都主教拉斯提斯拉夫', 'Metropolitan Rastislav', 2014,
 '捷克布拉格',
 '1951 年 12 月 9 日由莫斯科宗主教座授予自主地位；1998 年君士坦丁堡亦承認其自主地位。',
 'Moscow Patriarchate Tomos (1951); Ecumenical Patriarchate (1998)'),

('美洲正教會',
 'Orthodox Church in America (OCA)',
 '北美', '東正教（美洲）', '東正教', '拜占庭禮',
 1970, '現存',
 '都主教提洪', 'Metropolitan Tikhon', 2012,
 '美國紐約',
 '源自 1794 年俄羅斯東正教在阿拉斯加的傳教；1970 年由莫斯科宗主教授予自主地位（Tomos）。君士坦丁堡及多個東正教會尚未承認其自主地位。',
 'Moscow Patriarchate Tomos (1970)'),

('烏克蘭正教會',
 'Orthodox Church of Ukraine (OCU)',
 '基輔', '東正教（烏克蘭）', '東正教', '拜占庭禮',
 2019, '現存',
 '都主教葉皮法尼', 'Metropolitan Epifaniy', 2019,
 '烏克蘭基輔',
 '2018 年 12 月 15 日合一公會議宣告成立；2019 年 1 月 6 日君士坦丁堡普世宗主教授予自主地位（Tomos）。莫斯科宗主教座及其附屬教會不承認。',
 'Ecumenical Patriarchate Tomos (2019-01-06)'),

('北馬其頓正教會',
 'Macedonian Orthodox Church–Ohrid Archbishopric',
 '奧赫里德', '東正教（北馬其頓）', '東正教', '拜占庭禮',
 1967, '現存',
 '大主教斯蒂凡', 'Archbishop Stefan', 1999,
 '北馬其頓斯科普里',
 '1967 年 7 月 17 日宣布脫離塞爾維亞正教會自主；長期不被任何東正教會承認。2022 年 5 月 24 日塞爾維亞正教會正式承認，多個其他教會隨後跟進。',
 'Serbian Orthodox Church recognition (2022-05-24)');


-- 設定 parent_see_id（自主地位來源）
UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '君士坦丁堡普世宗主教座')
  WHERE name_zh IN ('希臘自主教會', '波蘭自主正教會', '阿爾巴尼亞自主正教會', '烏克蘭正教會');

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '莫斯科東正教宗主教座')
  WHERE name_zh IN ('捷克及斯洛伐克正教會', '美洲正教會');

UPDATE episcopal_sees SET parent_see_id = (SELECT id FROM episcopal_sees WHERE name_zh = '塞爾維亞東正教宗主教座')
  WHERE name_zh = '北馬其頓正教會';
