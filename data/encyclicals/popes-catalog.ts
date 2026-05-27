/**
 * Pope catalog — 教宗名錄
 *
 * 4 世紀 Sylvester I（尼西亞會議 325 同期）至今全教宗（共 ~270 任）。
 *
 * 中文聖號採天主教官方譯名（思高聖經學會＋台灣主教團）：
 *   John = 若望、Paul = 保祿、Peter = 伯多祿、Mark = 馬爾谷、
 *   Gregory = 額我略、Leo = 良、Pius = 碧岳、Innocent = 諾森、
 *   Clement = 克勉、Stephen = 斯德望、Sixtus = 西斯篤、
 *   Boniface = 鮑尼法、Felix = 斐理斯、Damasus = 達瑪穌、
 *   Sylvester = 西爾物斯德、Anastasius = 阿納大削、
 *   Hormisdas = 何彌斯達、Hadrian = 哈德良。
 *
 * 任期日期：已知精確日填 YYYY-MM-DD；僅知年份填 YYYY-01-01；在位中填空字串。
 * `notesZh` 僅近代 marquee 教宗（19c-21c）保留豐富說明；早期教宗逐步補充。
 */

import type { Pope } from './types'

export const POPES: Pope[] = [
  // ════════════════════ 21 世紀 ════════════════════
  {
    slug: 'leo-xiv',
    nameZh: '良十四世',
    nameEn: 'Leo XIV',
    nameLat: 'Leo PP. XIV',
    birthName: 'Robert Francis Prevost',
    pontificateStart: '2025-05-08',
    pontificateEnd: '',
    century: 21,
    nationality: '美國／秘魯',
    notesZh: '第 267 任教宗。第一位來自美國的教宗，奧斯定會士；2015 起任秘魯 Chiclayo 教區主教，後歸化秘魯籍；2023 升樞機並出任主教部部長。2025-05-08 於方濟各逝後當選；選名 Leo 承襲良十三世社會訓導與工人關懷的傳承，並回應 AI 時代對人類尊嚴的新挑戰。官方中譯為「良十四世」（2025-05 台灣主教團公布）。',
  },
  {
    slug: 'francis',
    nameZh: '方濟各',
    nameEn: 'Francis',
    nameLat: 'Franciscus',
    birthName: 'Jorge Mario Bergoglio',
    pontificateStart: '2013-03-13',
    pontificateEnd: '2025-04-21',
    century: 21,
    nationality: '阿根廷',
    notesZh: '第 266 任教宗。第一位來自美洲與南半球、亦為首位耶穌會出身的教宗。任內以社會訓導（《願祢受讚頌》通諭論生態危機、《眾位弟兄》通諭論友愛與社會友誼）、改革羅馬教廷組織（2022 年使徒憲令《你們去宣講福音》Praedicate Evangelium）與牧靈面向（《福音的喜樂》宗座勸諭）見稱。',
  },
  {
    slug: 'benedict-xvi',
    nameZh: '本篤十六世',
    nameEn: 'Benedict XVI',
    nameLat: 'Benedictus PP. XVI',
    birthName: 'Joseph Aloisius Ratzinger',
    pontificateStart: '2005-04-19',
    pontificateEnd: '2013-02-28',
    century: 21,
    nationality: '德國',
    notesZh: '第 265 任教宗。原任教義部部長（前身為信理部），任內頒布三道「神學三部曲」通諭：《天主是愛》(2005)、《在希望中得救》(2007)、《在真理中的愛德》(2009)。2013 年自願請辭，為近 600 年來首位生前退位的教宗。',
  },

  // ════════════════════ 20 世紀 ════════════════════
  {
    slug: 'john-paul-ii',
    nameZh: '若望保祿二世',
    nameEn: 'John Paul II',
    nameLat: 'Ioannes Paulus PP. II',
    birthName: 'Karol Józef Wojtyła',
    pontificateStart: '1978-10-16',
    pontificateEnd: '2005-04-02',
    century: 20,
    nationality: '波蘭',
    notesZh: '第 264 任教宗。455 年來首位非義大利籍教宗。在位 26 年餘，頒布 14 道通諭，是近代訓導文獻最豐沛的教宗之一。代表作含《人類救主》(1979)、《真理的光輝》(1993)、《生命的福音》(1995)、《信仰與理性》(1998)、《願他們合而為一》(1995)。',
  },
  {
    slug: 'john-paul-i',
    nameZh: '若望保祿一世',
    nameEn: 'John Paul I',
    nameLat: 'Ioannes Paulus PP. I',
    birthName: 'Albino Luciani',
    pontificateStart: '1978-08-26',
    pontificateEnd: '1978-09-28',
    century: 20,
    nationality: '義大利',
    notesZh: '第 263 任教宗。在位僅 33 天即逝世。未頒布通諭。',
  },
  {
    slug: 'paul-vi',
    nameZh: '保祿六世',
    nameEn: 'Paul VI',
    nameLat: 'Paulus PP. VI',
    birthName: 'Giovanni Battista Enrico Antonio Maria Montini',
    pontificateStart: '1963-06-21',
    pontificateEnd: '1978-08-06',
    century: 20,
    nationality: '義大利',
    notesZh: '第 262 任教宗。繼若望二十三世主持完成梵二大公會議。頒布 7 道通諭，含 1968 年具爭議性的《人類生命》通諭，重申天主教對人工避孕的立場。',
  },
  {
    slug: 'john-xxiii',
    nameZh: '若望二十三世',
    nameEn: 'John XXIII',
    nameLat: 'Ioannes PP. XXIII',
    birthName: 'Angelo Giuseppe Roncalli',
    pontificateStart: '1958-10-28',
    pontificateEnd: '1963-06-03',
    century: 20,
    nationality: '義大利',
    notesZh: '第 261 任教宗。1962 年召開梵二大公會議。代表通諭《和平於世》(1963) 首次將通諭收件對象擴及「所有善意人士」。',
  },
  {
    slug: 'pius-xii',
    nameZh: '碧岳十二世',
    nameEn: 'Pius XII',
    nameLat: 'Pius PP. XII',
    birthName: 'Eugenio Maria Giuseppe Giovanni Pacelli',
    pontificateStart: '1939-03-02',
    pontificateEnd: '1958-10-09',
    century: 20,
    nationality: '義大利',
    notesZh: '第 260 任教宗。頒布 41 道通諭。1943 年《在聖神默感之下》(Divino Afflante Spiritu) 開啟現代天主教聖經研究；1950 年使徒憲令《廣施恩寵的天主》(Munificentissimus Deus) 定義聖母蒙召升天信理。',
  },
  {
    slug: 'pius-xi',
    nameZh: '碧岳十一世',
    nameEn: 'Pius XI',
    nameLat: 'Pius PP. XI',
    birthName: 'Ambrogio Damiano Achille Ratti',
    pontificateStart: '1922-02-06',
    pontificateEnd: '1939-02-10',
    century: 20,
    nationality: '義大利',
    notesZh: '第 259 任教宗。1929 年與義大利簽訂《拉特朗條約》，建立梵蒂岡城國。代表通諭《貞潔婚姻》(1930)、《四十年》(1931，紀念《新事》40 周年的社會訓導續篇)、《以憂傷的關切》(1937 德文，譴責納粹)。',
  },
  {
    slug: 'benedict-xv',
    nameZh: '本篤十五世',
    nameEn: 'Benedict XV',
    nameLat: 'Benedictus PP. XV',
    birthName: 'Giacomo Paolo Giovanni Battista della Chiesa',
    pontificateStart: '1914-09-03',
    pontificateEnd: '1922-01-22',
    century: 20,
    nationality: '義大利',
    notesZh: '第 258 任教宗。一戰期間極力斡旋和平。代表通諭《撫慰至深》(1914，反戰)、《撫慰至切》(1920，論慈愛)。',
  },
  {
    slug: 'pius-x',
    nameZh: '碧岳十世',
    nameEn: 'Pius X',
    nameLat: 'Pius PP. X',
    birthName: 'Giuseppe Melchiorre Sarto',
    pontificateStart: '1903-08-04',
    pontificateEnd: '1914-08-20',
    century: 20,
    nationality: '義大利',
    notesZh: '第 257 任教宗。1907 年《應牧放主羊》(Pascendi Dominici Gregis) 大力譴責現代主義。1954 年封聖。',
  },

  // ════════════════════ 19 世紀 ════════════════════
  {
    slug: 'leo-xiii',
    nameZh: '良十三世',
    nameEn: 'Leo XIII',
    nameLat: 'Leo PP. XIII',
    birthName: 'Vincenzo Gioacchino Raffaele Luigi Pecci',
    pontificateStart: '1878-02-20',
    pontificateEnd: '1903-07-20',
    century: 19,
    nationality: '義大利',
    notesZh: '第 256 任教宗。頒布 88 道通諭，現代教廷通諭體裁的奠定者。1891 年《新事》(Rerum Novarum) 開啟近代天主教社會訓導傳統，至今每 10 年由後繼教宗紀念續寫。',
  },
  {
    slug: 'pius-ix',
    nameZh: '碧岳九世',
    nameEn: 'Pius IX',
    nameLat: 'Pius PP. IX',
    birthName: 'Giovanni Maria Mastai-Ferretti',
    pontificateStart: '1846-06-16',
    pontificateEnd: '1878-02-07',
    century: 19,
    nationality: '義大利',
    notesZh: '第 255 任教宗。在位 31 年餘，史上最長。1854 年使徒憲令《不可言傳的天主》(Ineffabilis Deus) 定義聖母無染原罪信理；1864 年《我們是何等關切》(Quanta Cura) 附《當代謬論彙編》(Syllabus Errorum)；1869-70 召開梵一大公會議，確立教宗無謬論信理。',
  },
  { slug: 'gregory-xvi', nameZh: '額我略十六世', nameEn: 'Gregory XVI', nameLat: 'Gregorius PP. XVI', birthName: 'Bartolomeo Alberto Cappellari', pontificateStart: '1831-02-02', pontificateEnd: '1846-06-01', century: 19, nationality: '義大利', notesZh: '第 254 任教宗。1832 年《Mirari Vos》通諭首次系統性譴責自由主義、宗教自由、政教分離。' },
  { slug: 'pius-viii', nameZh: '碧岳八世', nameEn: 'Pius VIII', nameLat: 'Pius PP. VIII', birthName: 'Francesco Saverio Castiglioni', pontificateStart: '1829-03-31', pontificateEnd: '1830-11-30', century: 19, nationality: '義大利' },
  { slug: 'leo-xii', nameZh: '良十二世', nameEn: 'Leo XII', nameLat: 'Leo PP. XII', birthName: 'Annibale Francesco Clemente Melchiorre Girolamo Nicola della Genga', pontificateStart: '1823-09-28', pontificateEnd: '1829-02-10', century: 19, nationality: '義大利' },
  { slug: 'pius-vii', nameZh: '碧岳七世', nameEn: 'Pius VII', nameLat: 'Pius PP. VII', birthName: 'Barnaba Niccolò Maria Luigi Chiaramonti', pontificateStart: '1800-03-14', pontificateEnd: '1823-08-20', century: 19, nationality: '義大利', notesZh: '與拿破崙簽訂 1801《Concordat》，並於 1804 為其加冕；後遭拿破崙監禁於楓丹白露五年。1814 解放後恢復教廷地位。' },

  // ════════════════════ 18 世紀 ════════════════════
  { slug: 'pius-vi', nameZh: '碧岳六世', nameEn: 'Pius VI', nameLat: 'Pius PP. VI', birthName: 'Giovanni Angelo Braschi', pontificateStart: '1775-02-15', pontificateEnd: '1799-08-29', century: 18, nationality: '義大利', notesZh: '在位末年遭法國革命政府廢黜，被擄至 Valence 客死他鄉。' },
  { slug: 'clement-xiv', nameZh: '克勉十四世', nameEn: 'Clement XIV', nameLat: 'Clemens PP. XIV', birthName: 'Giovanni Vincenzo Antonio Ganganelli', pontificateStart: '1769-05-19', pontificateEnd: '1774-09-22', century: 18, nationality: '義大利', notesZh: '1773 年《Dominus ac Redemptor》解散耶穌會（至 1814 由 Pius VII 恢復）。' },
  { slug: 'clement-xiii', nameZh: '克勉十三世', nameEn: 'Clement XIII', nameLat: 'Clemens PP. XIII', birthName: 'Carlo della Torre di Rezzonico', pontificateStart: '1758-07-06', pontificateEnd: '1769-02-02', century: 18, nationality: '義大利' },
  { slug: 'benedict-xiv', nameZh: '本篤十四世', nameEn: 'Benedict XIV', nameLat: 'Benedictus PP. XIV', birthName: 'Prospero Lorenzo Lambertini', pontificateStart: '1740-08-17', pontificateEnd: '1758-05-03', century: 18, nationality: '義大利', notesZh: '現代 encyclical 體裁的奠基者，頒布 32 道通諭（含首道現代意義通諭《Ubi Primum》1740）。重視學術與啟蒙對話。' },
  { slug: 'clement-xii', nameZh: '克勉十二世', nameEn: 'Clement XII', nameLat: 'Clemens PP. XII', birthName: 'Lorenzo Corsini', pontificateStart: '1730-07-12', pontificateEnd: '1740-02-06', century: 18, nationality: '義大利', notesZh: '1738《In Eminenti Apostolatus》首次譴責共濟會。' },
  { slug: 'benedict-xiii', nameZh: '本篤十三世', nameEn: 'Benedict XIII', nameLat: 'Benedictus PP. XIII', birthName: 'Pietro Francesco Orsini', pontificateStart: '1724-05-29', pontificateEnd: '1730-02-21', century: 18, nationality: '義大利' },
  { slug: 'innocent-xiii', nameZh: '諾森十三世', nameEn: 'Innocent XIII', nameLat: 'Innocentius PP. XIII', birthName: 'Michelangelo dei Conti', pontificateStart: '1721-05-08', pontificateEnd: '1724-03-07', century: 18, nationality: '義大利' },
  { slug: 'clement-xi', nameZh: '克勉十一世', nameEn: 'Clement XI', nameLat: 'Clemens PP. XI', birthName: 'Giovanni Francesco Albani', pontificateStart: '1700-11-23', pontificateEnd: '1721-03-19', century: 18, nationality: '義大利', notesZh: '1713《Unigenitus》再譴責 Jansenism 101 命題；1715 在《Ex Illa Die》裁定中國禮儀之爭，禁止祭祖祭孔。' },

  // ════════════════════ 17 世紀 ════════════════════
  { slug: 'innocent-xii', nameZh: '諾森十二世', nameEn: 'Innocent XII', nameLat: 'Innocentius PP. XII', birthName: 'Antonio Pignatelli del Rastrello', pontificateStart: '1691-07-12', pontificateEnd: '1700-09-27', century: 17, nationality: '義大利' },
  { slug: 'alexander-viii', nameZh: '亞歷山大八世', nameEn: 'Alexander VIII', nameLat: 'Alexander PP. VIII', birthName: 'Pietro Vito Ottoboni', pontificateStart: '1689-10-06', pontificateEnd: '1691-02-01', century: 17, nationality: '義大利' },
  { slug: 'innocent-xi', nameZh: '諾森十一世', nameEn: 'Innocent XI', nameLat: 'Innocentius PP. XI', birthName: 'Benedetto Odescalchi', pontificateStart: '1676-09-21', pontificateEnd: '1689-08-12', century: 17, nationality: '義大利', notesZh: '1683 維也納之戰前後組織反鄂圖曼神聖同盟。' },
  { slug: 'clement-x', nameZh: '克勉十世', nameEn: 'Clement X', nameLat: 'Clemens PP. X', birthName: 'Emilio Bonaventura Altieri', pontificateStart: '1670-04-29', pontificateEnd: '1676-07-22', century: 17, nationality: '義大利' },
  { slug: 'clement-ix', nameZh: '克勉九世', nameEn: 'Clement IX', nameLat: 'Clemens PP. IX', birthName: 'Giulio Rospigliosi', pontificateStart: '1667-06-20', pontificateEnd: '1669-12-09', century: 17, nationality: '義大利' },
  { slug: 'alexander-vii', nameZh: '亞歷山大七世', nameEn: 'Alexander VII', nameLat: 'Alexander PP. VII', birthName: 'Fabio Chigi', pontificateStart: '1655-04-07', pontificateEnd: '1667-05-22', century: 17, nationality: '義大利' },
  { slug: 'innocent-x', nameZh: '諾森十世', nameEn: 'Innocent X', nameLat: 'Innocentius PP. X', birthName: 'Giovanni Battista Pamphili', pontificateStart: '1644-09-15', pontificateEnd: '1655-01-07', century: 17, nationality: '義大利', notesZh: '1653《Cum occasione》譴責 Jansenism 五命題。' },
  { slug: 'urban-viii', nameZh: '伍朋八世', nameEn: 'Urban VIII', nameLat: 'Urbanus PP. VIII', birthName: 'Maffeo Vincenzo Barberini', pontificateStart: '1623-08-06', pontificateEnd: '1644-07-29', century: 17, nationality: '義大利', notesZh: '1633 主持伽利略第二次審判。Barberini 家族大力贊助 Baroque 藝術。' },
  { slug: 'gregory-xv', nameZh: '額我略十五世', nameEn: 'Gregory XV', nameLat: 'Gregorius PP. XV', birthName: 'Alessandro Ludovisi', pontificateStart: '1621-02-09', pontificateEnd: '1623-07-08', century: 17, nationality: '義大利', notesZh: '1622 創立 Propaganda Fide（傳信部）統籌全球傳教事務。' },
  { slug: 'paul-v', nameZh: '保祿五世', nameEn: 'Paul V', nameLat: 'Paulus PP. V', birthName: 'Camillo Borghese', pontificateStart: '1605-05-16', pontificateEnd: '1621-01-28', century: 17, nationality: '義大利' },
  { slug: 'leo-xi', nameZh: '良十一世', nameEn: 'Leo XI', nameLat: 'Leo PP. XI', birthName: 'Alessandro Ottaviano de Medici', pontificateStart: '1605-04-01', pontificateEnd: '1605-04-27', century: 17, nationality: '義大利', notesZh: '在位僅 27 天即病逝。' },

  // ════════════════════ 16 世紀 ════════════════════
  { slug: 'clement-viii', nameZh: '克勉八世', nameEn: 'Clement VIII', nameLat: 'Clemens PP. VIII', birthName: 'Ippolito Aldobrandini', pontificateStart: '1592-01-30', pontificateEnd: '1605-03-05', century: 16, nationality: '義大利' },
  { slug: 'innocent-ix', nameZh: '諾森九世', nameEn: 'Innocent IX', nameLat: 'Innocentius PP. IX', birthName: 'Giovanni Antonio Facchinetti', pontificateStart: '1591-10-29', pontificateEnd: '1591-12-30', century: 16, nationality: '義大利' },
  { slug: 'gregory-xiv', nameZh: '額我略十四世', nameEn: 'Gregory XIV', nameLat: 'Gregorius PP. XIV', birthName: 'Niccolò Sfondrati', pontificateStart: '1590-12-05', pontificateEnd: '1591-10-16', century: 16, nationality: '義大利' },
  { slug: 'urban-vii', nameZh: '伍朋七世', nameEn: 'Urban VII', nameLat: 'Urbanus PP. VII', birthName: 'Giovanni Battista Castagna', pontificateStart: '1590-09-15', pontificateEnd: '1590-09-27', century: 16, nationality: '義大利', notesZh: '在位 13 天即病逝，史上最短任期。' },
  { slug: 'sixtus-v', nameZh: '西斯篤五世', nameEn: 'Sixtus V', nameLat: 'Sixtus PP. V', birthName: 'Felice Peretti di Montalto', pontificateStart: '1585-04-24', pontificateEnd: '1590-08-27', century: 16, nationality: '義大利', notesZh: '1588《Immensa Aeterni Dei》重組教廷，設立 15 個樞機部會（信理部前身），現代教廷結構奠基者。' },
  { slug: 'gregory-xiii', nameZh: '額我略十三世', nameEn: 'Gregory XIII', nameLat: 'Gregorius PP. XIII', birthName: 'Ugo Boncompagni', pontificateStart: '1572-05-13', pontificateEnd: '1585-04-10', century: 16, nationality: '義大利', notesZh: '1582 頒布額我略曆（Gregorian Calendar），現代世界通用陽曆即此曆。' },
  { slug: 'pius-v', nameZh: '碧岳五世', nameEn: 'Pius V', nameLat: 'Pius PP. V', birthName: 'Antonio Michele Ghislieri', pontificateStart: '1566-01-07', pontificateEnd: '1572-05-01', century: 16, nationality: '義大利', notesZh: '1568 頒布 Tridentine 禮儀經本（Missale Romanum），統一拉丁禮 400 年；1570《Regnans in Excelsis》絕罰英王伊麗莎白一世；1571 組神聖同盟於 Lepanto 海戰擊敗鄂圖曼海軍。' },
  { slug: 'pius-iv', nameZh: '碧岳四世', nameEn: 'Pius IV', nameLat: 'Pius PP. IV', birthName: 'Giovanni Angelo Medici', pontificateStart: '1559-12-25', pontificateEnd: '1565-12-09', century: 16, nationality: '義大利', notesZh: '1562-63 主持完成 Trent 大公會議第三會期。' },
  { slug: 'paul-iv', nameZh: '保祿四世', nameEn: 'Paul IV', nameLat: 'Paulus PP. IV', birthName: 'Giovanni Pietro Carafa', pontificateStart: '1555-05-23', pontificateEnd: '1559-08-18', century: 16, nationality: '義大利' },
  { slug: 'marcellus-ii', nameZh: '瑪策路二世', nameEn: 'Marcellus II', nameLat: 'Marcellus PP. II', birthName: 'Marcello Cervini degli Spannochi', pontificateStart: '1555-04-09', pontificateEnd: '1555-05-01', century: 16, nationality: '義大利' },
  { slug: 'julius-iii', nameZh: '儒略三世', nameEn: 'Julius III', nameLat: 'Iulius PP. III', birthName: 'Giovanni Maria Ciocchi del Monte', pontificateStart: '1550-02-07', pontificateEnd: '1555-03-23', century: 16, nationality: '義大利' },
  { slug: 'paul-iii', nameZh: '保祿三世', nameEn: 'Paul III', nameLat: 'Paulus PP. III', birthName: 'Alessandro Farnese', pontificateStart: '1534-10-13', pontificateEnd: '1549-11-10', century: 16, nationality: '義大利', notesZh: '1545 召開 Trent 大公會議，啟動反宗教改革；1540 核准耶穌會章程。' },
  { slug: 'clement-vii', nameZh: '克勉七世', nameEn: 'Clement VII', nameLat: 'Clemens PP. VII', birthName: 'Giulio di Giuliano de Medici', pontificateStart: '1523-11-19', pontificateEnd: '1534-09-25', century: 16, nationality: '義大利', notesZh: '1527 羅馬遭神聖羅馬帝國軍隊洗劫。拒批英王亨利八世離婚案，導致英國國教 1534 分裂。' },
  { slug: 'hadrian-vi', nameZh: '哈德良六世', nameEn: 'Hadrian VI', nameLat: 'Hadrianus PP. VI', birthName: 'Adriaan Florensz Boeyens', pontificateStart: '1522-01-09', pontificateEnd: '1523-09-14', century: 16, nationality: '荷蘭', notesZh: '末位非義大利籍教宗，至 1978 若望保祿二世為止。' },
  { slug: 'leo-x', nameZh: '良十世', nameEn: 'Leo X', nameLat: 'Leo PP. X', birthName: 'Giovanni di Lorenzo de Medici', pontificateStart: '1513-03-09', pontificateEnd: '1521-12-01', century: 16, nationality: '義大利', notesZh: '1517 路德張貼 95 條論綱發生於其任內；1520《Exsurge Domine》譴責路德 41 條，1521《Decet Romanum Pontificem》正式絕罰路德。Medici 家族貴族出身，大力贊助文藝復興藝術。' },
  { slug: 'julius-ii', nameZh: '儒略二世', nameEn: 'Julius II', nameLat: 'Iulius PP. II', birthName: 'Giuliano della Rovere', pontificateStart: '1503-11-01', pontificateEnd: '1513-02-21', century: 16, nationality: '義大利', notesZh: '「戰士教宗」，親自率軍出征收復教宗國。1506 委託 Michelangelo 繪西斯篤聖堂天頂畫、Bramante 設計新聖伯多祿大殿。' },
  { slug: 'pius-iii', nameZh: '碧岳三世', nameEn: 'Pius III', nameLat: 'Pius PP. III', birthName: 'Francesco Todeschini Piccolomini', pontificateStart: '1503-09-22', pontificateEnd: '1503-10-18', century: 16, nationality: '義大利' },

  // ════════════════════ 15 世紀 ════════════════════
  { slug: 'alexander-vi', nameZh: '亞歷山大六世', nameEn: 'Alexander VI', nameLat: 'Alexander PP. VI', birthName: 'Rodrigo de Borja', pontificateStart: '1492-08-11', pontificateEnd: '1503-08-18', century: 15, nationality: '西班牙', notesZh: 'Borgia 家族出身，史上爭議最大的教宗之一。1493《Inter Caetera》劃分西葡兩國在新世界的傳教與殖民勢力範圍（子午線劃分）。' },
  { slug: 'innocent-viii', nameZh: '諾森八世', nameEn: 'Innocent VIII', nameLat: 'Innocentius PP. VIII', birthName: 'Giovanni Battista Cybo', pontificateStart: '1484-08-29', pontificateEnd: '1492-07-25', century: 15, nationality: '義大利' },
  { slug: 'sixtus-iv', nameZh: '西斯篤四世', nameEn: 'Sixtus IV', nameLat: 'Sixtus PP. IV', birthName: 'Francesco della Rovere', pontificateStart: '1471-08-09', pontificateEnd: '1484-08-12', century: 15, nationality: '義大利', notesZh: '1473 興建西斯篤聖堂（Cappella Sistina），1478 核准西班牙宗教裁判所。' },
  { slug: 'paul-ii', nameZh: '保祿二世', nameEn: 'Paul II', nameLat: 'Paulus PP. II', birthName: 'Pietro Barbo', pontificateStart: '1464-08-30', pontificateEnd: '1471-07-26', century: 15, nationality: '義大利' },
  { slug: 'pius-ii', nameZh: '碧岳二世', nameEn: 'Pius II', nameLat: 'Pius PP. II', birthName: 'Enea Silvio Piccolomini', pontificateStart: '1458-08-19', pontificateEnd: '1464-08-14', century: 15, nationality: '義大利', notesZh: '文藝復興人文主義學者，自傳《Commentarii》為唯一教宗親撰自傳。1453 君士坦丁堡陷落後致力組織十字軍對抗鄂圖曼。' },
  { slug: 'callixtus-iii', nameZh: '加禮多三世', nameEn: 'Callixtus III', nameLat: 'Callixtus PP. III', birthName: 'Alfonso de Borja', pontificateStart: '1455-04-08', pontificateEnd: '1458-08-06', century: 15, nationality: '西班牙' },
  { slug: 'nicholas-v', nameZh: '尼閣五世', nameEn: 'Nicholas V', nameLat: 'Nicolaus PP. V', birthName: 'Tommaso Parentucelli', pontificateStart: '1447-03-06', pontificateEnd: '1455-03-24', century: 15, nationality: '義大利', notesZh: '創建梵蒂岡圖書館（Biblioteca Apostolica Vaticana），1455《Romanus Pontifex》授權葡萄牙在非洲的傳教與殖民。' },
  { slug: 'eugene-iv', nameZh: '尤金四世', nameEn: 'Eugene IV', nameLat: 'Eugenius PP. IV', birthName: 'Gabriele Condulmer', pontificateStart: '1431-03-03', pontificateEnd: '1447-02-23', century: 15, nationality: '義大利', notesZh: '主持 1431-49 Basel-Ferrara-Florence 大公會議（梵二之前的東西方合一嘗試最重要的一場）。' },
  { slug: 'martin-v', nameZh: '瑪定五世', nameEn: 'Martin V', nameLat: 'Martinus PP. V', birthName: 'Otto/Oddone Colonna', pontificateStart: '1417-11-11', pontificateEnd: '1431-02-20', century: 15, nationality: '義大利', notesZh: '1414-18 Constance 大公會議當選，終結 1378-1417 西方教會大分裂（三位對立教宗並存）。' },
  { slug: 'gregory-xii', nameZh: '額我略十二世', nameEn: 'Gregory XII', nameLat: 'Gregorius PP. XII', birthName: 'Angelo Correr', pontificateStart: '1406-12-19', pontificateEnd: '1415-07-04', century: 15, nationality: '義大利', notesZh: '主動退位以結束西方大分裂；至 2013 本篤十六世為止，唯一生前退位教宗。' },
  { slug: 'innocent-vii', nameZh: '諾森七世', nameEn: 'Innocent VII', nameLat: 'Innocentius PP. VII', birthName: 'Cosimo de Migliorati', pontificateStart: '1404-10-17', pontificateEnd: '1406-11-06', century: 15, nationality: '義大利' },

  // ════════════════════ 14 世紀 ════════════════════
  { slug: 'boniface-ix', nameZh: '鮑尼法九世', nameEn: 'Boniface IX', nameLat: 'Bonifatius PP. IX', birthName: 'Pietro Tomacelli', pontificateStart: '1389-11-02', pontificateEnd: '1404-10-01', century: 14, nationality: '義大利' },
  { slug: 'urban-vi', nameZh: '伍朋六世', nameEn: 'Urban VI', nameLat: 'Urbanus PP. VI', birthName: 'Bartolomeo Prignano', pontificateStart: '1378-04-08', pontificateEnd: '1389-10-15', century: 14, nationality: '義大利', notesZh: '其當選後立即引發西方大分裂（1378-1417），亞維儂派另選 Clement VII 對立教宗。' },
  { slug: 'gregory-xi', nameZh: '額我略十一世', nameEn: 'Gregory XI', nameLat: 'Gregorius PP. XI', birthName: 'Pierre Roger de Beaufort', pontificateStart: '1370-12-30', pontificateEnd: '1378-03-27', century: 14, nationality: '法國', notesZh: '1377 結束 67 年的亞維儂遷都，將教廷遷回羅馬。最後一位法國籍教宗。' },
  { slug: 'urban-v', nameZh: '伍朋五世', nameEn: 'Urban V', nameLat: 'Urbanus PP. V', birthName: 'Guillaume de Grimoard', pontificateStart: '1362-09-28', pontificateEnd: '1370-12-19', century: 14, nationality: '法國' },
  { slug: 'innocent-vi', nameZh: '諾森六世', nameEn: 'Innocent VI', nameLat: 'Innocentius PP. VI', birthName: 'Étienne Aubert', pontificateStart: '1352-12-18', pontificateEnd: '1362-09-12', century: 14, nationality: '法國' },
  { slug: 'clement-vi', nameZh: '克勉六世', nameEn: 'Clement VI', nameLat: 'Clemens PP. VI', birthName: 'Pierre Roger', pontificateStart: '1342-05-07', pontificateEnd: '1352-12-06', century: 14, nationality: '法國', notesZh: '1348 黑死病期間在亞維儂庇護猶太人。' },
  { slug: 'benedict-xii', nameZh: '本篤十二世', nameEn: 'Benedict XII', nameLat: 'Benedictus PP. XII', birthName: 'Jacques Fournier', pontificateStart: '1334-12-20', pontificateEnd: '1342-04-25', century: 14, nationality: '法國', notesZh: '1336《Benedictus Deus》宗座憲令確立「真福直觀」（visio beatifica）信理。' },
  { slug: 'john-xxii', nameZh: '若望二十二世', nameEn: 'John XXII', nameLat: 'Ioannes PP. XXII', birthName: 'Jacques Duèze', pontificateStart: '1316-08-07', pontificateEnd: '1334-12-04', century: 14, nationality: '法國', notesZh: '亞維儂第二任教宗。1323《Cum inter nonnullos》譴責方濟會「神貧爭論」(Spiritual Franciscans)。' },
  { slug: 'clement-v', nameZh: '克勉五世', nameEn: 'Clement V', nameLat: 'Clemens PP. V', birthName: 'Bertrand de Got', pontificateStart: '1305-06-05', pontificateEnd: '1314-04-20', century: 14, nationality: '法國', notesZh: '1309 將教廷遷往亞維儂，開啟「亞維儂遷都」（Avignon Papacy）67 年；1312 Vienne 大公會議解散聖殿騎士團。' },
  { slug: 'benedict-xi', nameZh: '本篤十一世', nameEn: 'Benedict XI', nameLat: 'Benedictus PP. XI', birthName: 'Niccolò Boccasini', pontificateStart: '1303-10-22', pontificateEnd: '1304-07-07', century: 14, nationality: '義大利' },

  // ════════════════════ 13 世紀 ════════════════════
  { slug: 'boniface-viii', nameZh: '鮑尼法八世', nameEn: 'Boniface VIII', nameLat: 'Bonifatius PP. VIII', birthName: 'Benedetto Caetani', pontificateStart: '1294-12-24', pontificateEnd: '1303-10-11', century: 13, nationality: '義大利', notesZh: '1302《Unam Sanctam》詔書，最高度的教宗權威聲明（「在羅馬教宗權下臣服是得救的絕對必要條件」）。與法王腓力四世衝突，1303 遭法王勢力凌辱於 Anagni，旋即病逝。' },
  { slug: 'celestine-v', nameZh: '雷定五世', nameEn: 'Celestine V', nameLat: 'Caelestinus PP. V', birthName: 'Pietro Angelerio (di Murrone)', pontificateStart: '1294-07-05', pontificateEnd: '1294-12-13', century: 13, nationality: '義大利', notesZh: '隱修士出身，被推為教宗後在位 5 個月即退位，史上首位生前退位教宗。但丁《神曲》譴責他「the great refusal」。' },
  { slug: 'nicholas-iv', nameZh: '尼閣四世', nameEn: 'Nicholas IV', nameLat: 'Nicolaus PP. IV', birthName: 'Girolamo Masci', pontificateStart: '1288-02-22', pontificateEnd: '1292-04-04', century: 13, nationality: '義大利', notesZh: '首位方濟會出身教宗。' },
  { slug: 'honorius-iv', nameZh: '何諾理四世', nameEn: 'Honorius IV', nameLat: 'Honorius PP. IV', birthName: 'Giacomo Savelli', pontificateStart: '1285-04-02', pontificateEnd: '1287-04-03', century: 13, nationality: '義大利' },
  { slug: 'martin-iv', nameZh: '瑪定四世', nameEn: 'Martin IV', nameLat: 'Martinus PP. IV', birthName: 'Simon de Brion', pontificateStart: '1281-02-22', pontificateEnd: '1285-03-28', century: 13, nationality: '法國' },
  { slug: 'nicholas-iii', nameZh: '尼閣三世', nameEn: 'Nicholas III', nameLat: 'Nicolaus PP. III', birthName: 'Giovanni Gaetano Orsini', pontificateStart: '1277-11-25', pontificateEnd: '1280-08-22', century: 13, nationality: '義大利' },
  { slug: 'john-xxi', nameZh: '若望二十一世', nameEn: 'John XXI', nameLat: 'Ioannes PP. XXI', birthName: 'Pedro Julião', pontificateStart: '1276-09-08', pontificateEnd: '1277-05-20', century: 13, nationality: '葡萄牙', notesZh: '唯一葡萄牙籍教宗，原為知名邏輯學家、醫師。號數跳過 XX（避免與一位被認定為偽教宗的對立教宗衝突）。' },
  { slug: 'hadrian-v', nameZh: '哈德良五世', nameEn: 'Hadrian V', nameLat: 'Hadrianus PP. V', birthName: 'Ottobono Fieschi', pontificateStart: '1276-07-11', pontificateEnd: '1276-08-18', century: 13, nationality: '義大利' },
  { slug: 'innocent-v', nameZh: '諾森五世', nameEn: 'Innocent V', nameLat: 'Innocentius PP. V', birthName: 'Pierre de Tarentaise', pontificateStart: '1276-01-21', pontificateEnd: '1276-06-22', century: 13, nationality: '法國', notesZh: '首位道明會出身教宗。' },
  { slug: 'gregory-x', nameZh: '額我略十世', nameEn: 'Gregory X', nameLat: 'Gregorius PP. X', birthName: 'Tedaldo Visconti', pontificateStart: '1271-09-01', pontificateEnd: '1276-01-10', century: 13, nationality: '義大利', notesZh: '1274 召開 Lyon II 大公會議，達成短暫東西方合一（旋即破局）。' },
  { slug: 'clement-iv', nameZh: '克勉四世', nameEn: 'Clement IV', nameLat: 'Clemens PP. IV', birthName: 'Gui Foucois', pontificateStart: '1265-02-05', pontificateEnd: '1268-11-29', century: 13, nationality: '法國' },
  { slug: 'urban-iv', nameZh: '伍朋四世', nameEn: 'Urban IV', nameLat: 'Urbanus PP. IV', birthName: 'Jacques Pantaléon', pontificateStart: '1261-08-29', pontificateEnd: '1264-10-02', century: 13, nationality: '法國', notesZh: '1264《Transiturus de hoc mundo》設立基督聖體節（Corpus Christi）為普世瞻禮。' },
  { slug: 'alexander-iv', nameZh: '亞歷山大四世', nameEn: 'Alexander IV', nameLat: 'Alexander PP. IV', birthName: 'Rinaldo Conti', pontificateStart: '1254-12-12', pontificateEnd: '1261-05-25', century: 13, nationality: '義大利' },
  { slug: 'innocent-iv', nameZh: '諾森四世', nameEn: 'Innocent IV', nameLat: 'Innocentius PP. IV', birthName: 'Sinibaldo Fieschi', pontificateStart: '1243-06-25', pontificateEnd: '1254-12-07', century: 13, nationality: '義大利', notesZh: '1245 Lyon I 大公會議廢黜神羅皇帝 Frederick II；1252《Ad Extirpanda》核准在宗教裁判中使用刑求。' },
  { slug: 'celestine-iv', nameZh: '雷定四世', nameEn: 'Celestine IV', nameLat: 'Caelestinus PP. IV', birthName: 'Goffredo da Castiglione', pontificateStart: '1241-10-25', pontificateEnd: '1241-11-10', century: 13, nationality: '義大利' },
  { slug: 'gregory-ix', nameZh: '額我略九世', nameEn: 'Gregory IX', nameLat: 'Gregorius PP. IX', birthName: 'Ugolino dei Conti di Segni', pontificateStart: '1227-03-19', pontificateEnd: '1241-08-22', century: 13, nationality: '義大利', notesZh: '1234 編《Decretales》(Liber Extra)，奠定中世紀教會法基礎；1231 正式設立宗教裁判所；認可道明會（1216）與方濟會（1223）章程。' },
  { slug: 'honorius-iii', nameZh: '何諾理三世', nameEn: 'Honorius III', nameLat: 'Honorius PP. III', birthName: 'Cencio Savelli', pontificateStart: '1216-07-18', pontificateEnd: '1227-03-18', century: 13, nationality: '義大利', notesZh: '1216 核准道明會、1223 核准方濟會。' },
  { slug: 'innocent-iii', nameZh: '諾森三世', nameEn: 'Innocent III', nameLat: 'Innocentius PP. III', birthName: 'Lotario dei Conti di Segni', pontificateStart: '1198-01-08', pontificateEnd: '1216-07-16', century: 13, nationality: '義大利', notesZh: '中世紀盛期教宗權威的頂峰。1215 召開拉特朗四大公會議（最重要的中世紀大公會議）；發動第四次十字軍（攻陷君士坦丁堡 1204，惡名昭著）；批准道明會、方濟會修會雛形。' },

  // ════════════════════ 12 世紀 ════════════════════
  { slug: 'celestine-iii', nameZh: '雷定三世', nameEn: 'Celestine III', nameLat: 'Caelestinus PP. III', birthName: 'Giacinto Bobone', pontificateStart: '1191-03-30', pontificateEnd: '1198-01-08', century: 12, nationality: '義大利' },
  { slug: 'clement-iii', nameZh: '克勉三世', nameEn: 'Clement III', nameLat: 'Clemens PP. III', birthName: 'Paolino Scolari', pontificateStart: '1187-12-19', pontificateEnd: '1191-03-20', century: 12, nationality: '義大利' },
  { slug: 'gregory-viii', nameZh: '額我略八世', nameEn: 'Gregory VIII', nameLat: 'Gregorius PP. VIII', birthName: 'Alberto di Morra', pontificateStart: '1187-10-25', pontificateEnd: '1187-12-17', century: 12, nationality: '義大利', notesZh: '1187 號召第三次十字軍對抗 Saladin。' },
  { slug: 'urban-iii', nameZh: '伍朋三世', nameEn: 'Urban III', nameLat: 'Urbanus PP. III', birthName: 'Uberto Crivelli', pontificateStart: '1185-11-25', pontificateEnd: '1187-10-20', century: 12, nationality: '義大利' },
  { slug: 'lucius-iii', nameZh: '路爵三世', nameEn: 'Lucius III', nameLat: 'Lucius PP. III', birthName: 'Ubaldo Allucingoli', pontificateStart: '1181-09-01', pontificateEnd: '1185-11-25', century: 12, nationality: '義大利' },
  { slug: 'alexander-iii', nameZh: '亞歷山大三世', nameEn: 'Alexander III', nameLat: 'Alexander PP. III', birthName: 'Rolando', pontificateStart: '1159-09-07', pontificateEnd: '1181-08-30', century: 12, nationality: '義大利', notesZh: '1179 召開拉特朗三大公會議；訂立封聖權須由教宗核可（1170）；長期對抗神羅皇帝 Frederick Barbarossa。' },
  { slug: 'hadrian-iv', nameZh: '哈德良四世', nameEn: 'Hadrian IV', nameLat: 'Hadrianus PP. IV', birthName: 'Nicholas Breakspear', pontificateStart: '1154-12-04', pontificateEnd: '1159-09-01', century: 12, nationality: '英格蘭', notesZh: '唯一英格蘭籍教宗。' },
  { slug: 'anastasius-iv', nameZh: '阿納大削四世', nameEn: 'Anastasius IV', nameLat: 'Anastasius PP. IV', birthName: 'Corrado della Suburra', pontificateStart: '1153-07-12', pontificateEnd: '1154-12-03', century: 12, nationality: '義大利' },
  { slug: 'eugene-iii', nameZh: '尤金三世', nameEn: 'Eugene III', nameLat: 'Eugenius PP. III', birthName: 'Bernardo Pignatelli', pontificateStart: '1145-02-15', pontificateEnd: '1153-07-08', century: 12, nationality: '義大利', notesZh: '熙篤會出身，由其師聖伯爾納多（Bernard of Clairvaux）勸下號召第二次十字軍。' },
  { slug: 'lucius-ii', nameZh: '路爵二世', nameEn: 'Lucius II', nameLat: 'Lucius PP. II', birthName: 'Gherardo Caccianemici dal Orso', pontificateStart: '1144-03-12', pontificateEnd: '1145-02-15', century: 12, nationality: '義大利' },
  { slug: 'celestine-ii', nameZh: '雷定二世', nameEn: 'Celestine II', nameLat: 'Caelestinus PP. II', birthName: 'Guido del Castello', pontificateStart: '1143-09-26', pontificateEnd: '1144-03-08', century: 12, nationality: '義大利' },
  { slug: 'innocent-ii', nameZh: '諾森二世', nameEn: 'Innocent II', nameLat: 'Innocentius PP. II', birthName: 'Gregorio Papareschi', pontificateStart: '1130-02-14', pontificateEnd: '1143-09-24', century: 12, nationality: '義大利', notesZh: '1139 召開拉特朗二大公會議。' },
  { slug: 'honorius-ii', nameZh: '何諾理二世', nameEn: 'Honorius II', nameLat: 'Honorius PP. II', birthName: 'Lamberto Scannabecchi', pontificateStart: '1124-12-21', pontificateEnd: '1130-02-13', century: 12, nationality: '義大利' },
  { slug: 'callixtus-ii', nameZh: '加禮多二世', nameEn: 'Callixtus II', nameLat: 'Callixtus PP. II', birthName: 'Guido of Burgundy', pontificateStart: '1119-02-02', pontificateEnd: '1124-12-13', century: 12, nationality: '勃艮第', notesZh: '1122 與神羅皇帝亨利五世簽訂 Worms 協約終結敘任權之爭；1123 召開拉特朗一大公會議（西方首次大公會議）。' },
  { slug: 'gelasius-ii', nameZh: '哲拉削二世', nameEn: 'Gelasius II', nameLat: 'Gelasius PP. II', birthName: 'Giovanni Coniulo', pontificateStart: '1118-01-24', pontificateEnd: '1119-01-29', century: 12, nationality: '義大利' },
  { slug: 'paschal-ii', nameZh: '巴斯加二世', nameEn: 'Paschal II', nameLat: 'Paschalis PP. II', birthName: 'Raniero Ranieri', pontificateStart: '1099-08-13', pontificateEnd: '1118-01-21', century: 12, nationality: '義大利' },

  // ════════════════════ 11 世紀 ════════════════════
  { slug: 'urban-ii', nameZh: '伍朋二世', nameEn: 'Urban II', nameLat: 'Urbanus PP. II', birthName: 'Eudes de Châtillon', pontificateStart: '1088-03-12', pontificateEnd: '1099-07-29', century: 11, nationality: '法國', notesZh: '1095 Clermont 會議號召第一次十字軍。' },
  { slug: 'victor-iii', nameZh: '維篤三世', nameEn: 'Victor III', nameLat: 'Victor PP. III', birthName: 'Dauferius / Desiderius', pontificateStart: '1086-05-24', pontificateEnd: '1087-09-16', century: 11, nationality: '義大利' },
  { slug: 'gregory-vii', nameZh: '額我略七世', nameEn: 'Gregory VII', nameLat: 'Gregorius PP. VII', birthName: 'Ildebrando di Soana', pontificateStart: '1073-04-22', pontificateEnd: '1085-05-25', century: 11, nationality: '義大利', notesZh: '1075《Dictatus Papae》27 條主張教宗至上權；發動敘任權之爭（Investiture Controversy）與神羅皇帝亨利四世對抗，1077 Canossa 之辱。教會改革（Gregorian Reform）的代表人物。' },
  { slug: 'alexander-ii', nameZh: '亞歷山大二世', nameEn: 'Alexander II', nameLat: 'Alexander PP. II', birthName: 'Anselmo da Baggio', pontificateStart: '1061-10-01', pontificateEnd: '1073-04-21', century: 11, nationality: '義大利' },
  { slug: 'nicholas-ii', nameZh: '尼閣二世', nameEn: 'Nicholas II', nameLat: 'Nicolaus PP. II', birthName: 'Gerard of Burgundy', pontificateStart: '1059-01-24', pontificateEnd: '1061-07-27', century: 11, nationality: '勃艮第', notesZh: '1059《In nomine Domini》制度化樞機選舉教宗制度（沿用至今）。' },
  { slug: 'stephen-ix', nameZh: '斯德望九世', nameEn: 'Stephen IX', nameLat: 'Stephanus PP. IX', birthName: 'Frédéric de Lorraine', pontificateStart: '1057-08-03', pontificateEnd: '1058-03-29', century: 11, nationality: '洛林' },
  { slug: 'victor-ii', nameZh: '維篤二世', nameEn: 'Victor II', nameLat: 'Victor PP. II', birthName: 'Gebhard of Dollnstein-Hirschberg', pontificateStart: '1055-04-13', pontificateEnd: '1057-07-28', century: 11, nationality: '德意志' },
  { slug: 'leo-ix', nameZh: '良九世', nameEn: 'Leo IX', nameLat: 'Leo PP. IX', birthName: 'Bruno von Egisheim-Dagsburg', pontificateStart: '1049-02-12', pontificateEnd: '1054-04-19', century: 11, nationality: '亞爾薩斯', notesZh: '1054 派 Humbert 樞機赴君士坦丁堡，在 Hagia Sophia 互擲絕罰，標誌東西教會大分裂（Great Schism）。' },
  { slug: 'damasus-ii', nameZh: '達瑪穌二世', nameEn: 'Damasus II', nameLat: 'Damasus PP. II', birthName: 'Poppo', pontificateStart: '1048-07-17', pontificateEnd: '1048-08-09', century: 11, nationality: '巴伐利亞' },
  { slug: 'benedict-ix', nameZh: '本篤九世', nameEn: 'Benedict IX', nameLat: 'Benedictus PP. IX', birthName: 'Teofilatto III dei Conti di Tuscolo', pontificateStart: '1032-10-21', pontificateEnd: '1048-07-17', century: 11, nationality: '義大利', notesZh: '唯一三度登基教宗（1032-44, 1045, 1047-48）；曾將教宗之位賣給 Gregory VI。' },
  { slug: 'clement-ii', nameZh: '克勉二世', nameEn: 'Clement II', nameLat: 'Clemens PP. II', birthName: 'Suidger von Morsleben', pontificateStart: '1046-12-25', pontificateEnd: '1047-10-09', century: 11, nationality: '德意志' },
  { slug: 'gregory-vi', nameZh: '額我略六世', nameEn: 'Gregory VI', nameLat: 'Gregorius PP. VI', birthName: 'Giovanni Graziano', pontificateStart: '1045-05-05', pontificateEnd: '1046-12-20', century: 11, nationality: '義大利' },
  { slug: 'john-xix', nameZh: '若望十九世', nameEn: 'John XIX', nameLat: 'Ioannes PP. XIX', birthName: 'Romano dei Conti di Tuscolo', pontificateStart: '1024-04-19', pontificateEnd: '1032-10-20', century: 11, nationality: '義大利' },
  { slug: 'benedict-viii', nameZh: '本篤八世', nameEn: 'Benedict VIII', nameLat: 'Benedictus PP. VIII', birthName: 'Teofilatto II dei Conti di Tuscolo', pontificateStart: '1012-05-21', pontificateEnd: '1024-04-09', century: 11, nationality: '義大利' },
  { slug: 'sergius-iv', nameZh: '塞奇四世', nameEn: 'Sergius IV', nameLat: 'Sergius PP. IV', birthName: 'Pietro Martino Boccapecora', pontificateStart: '1009-07-31', pontificateEnd: '1012-05-12', century: 11, nationality: '義大利' },
  { slug: 'john-xviii', nameZh: '若望十八世', nameEn: 'John XVIII', nameLat: 'Ioannes PP. XVIII', birthName: 'Giovanni Fasano', pontificateStart: '1003-12-25', pontificateEnd: '1009-06-01', century: 11, nationality: '義大利' },
  { slug: 'john-xvii', nameZh: '若望十七世', nameEn: 'John XVII', nameLat: 'Ioannes PP. XVII', birthName: 'Giovanni Sicco', pontificateStart: '1003-06-13', pontificateEnd: '1003-12-06', century: 11, nationality: '義大利' },

  // ════════════════════ 10 世紀 ════════════════════
  { slug: 'sylvester-ii', nameZh: '西爾物斯德二世', nameEn: 'Sylvester II', nameLat: 'Silvester PP. II', birthName: 'Gerbert of Aurillac', pontificateStart: '999-04-02', pontificateEnd: '1003-05-12', century: 10, nationality: '法國', notesZh: '首位法國籍教宗，知名數學家、引入阿拉伯數字到歐洲。' },
  { slug: 'gregory-v', nameZh: '額我略五世', nameEn: 'Gregory V', nameLat: 'Gregorius PP. V', birthName: 'Bruno of Carinthia', pontificateStart: '996-05-03', pontificateEnd: '999-02-18', century: 10, nationality: '德意志', notesZh: '首位德意志籍教宗。' },
  { slug: 'john-xv', nameZh: '若望十五世', nameEn: 'John XV', nameLat: 'Ioannes PP. XV', birthName: 'Giovanni di Gallina Alba', pontificateStart: '985-08-01', pontificateEnd: '996-03-01', century: 10, nationality: '義大利', notesZh: '993 首次正式封聖（Ulrich of Augsburg）— 此前封聖是地方教會權力。' },
  { slug: 'john-xiv', nameZh: '若望十四世', nameEn: 'John XIV', nameLat: 'Ioannes PP. XIV', birthName: 'Pietro Canepanova', pontificateStart: '983-12-01', pontificateEnd: '984-08-20', century: 10, nationality: '義大利' },
  { slug: 'benedict-vii', nameZh: '本篤七世', nameEn: 'Benedict VII', nameLat: 'Benedictus PP. VII', birthName: 'Benedetto', pontificateStart: '974-10-01', pontificateEnd: '983-07-10', century: 10, nationality: '義大利' },
  { slug: 'benedict-vi', nameZh: '本篤六世', nameEn: 'Benedict VI', nameLat: 'Benedictus PP. VI', birthName: 'Benedetto', pontificateStart: '973-01-19', pontificateEnd: '974-06-01', century: 10, nationality: '義大利' },
  { slug: 'john-xiii', nameZh: '若望十三世', nameEn: 'John XIII', nameLat: 'Ioannes PP. XIII', birthName: 'Giovanni Crescenzi', pontificateStart: '965-10-01', pontificateEnd: '972-09-06', century: 10, nationality: '義大利' },
  { slug: 'leo-viii', nameZh: '良八世', nameEn: 'Leo VIII', nameLat: 'Leo PP. VIII', birthName: 'Leone', pontificateStart: '963-12-04', pontificateEnd: '965-03-01', century: 10, nationality: '義大利' },
  { slug: 'john-xii', nameZh: '若望十二世', nameEn: 'John XII', nameLat: 'Ioannes PP. XII', birthName: 'Ottaviano dei Conti di Tuscolo', pontificateStart: '955-12-16', pontificateEnd: '964-05-14', century: 10, nationality: '義大利', notesZh: '當選時年僅 18 歲；962 為 Otto I 加冕為神聖羅馬帝國皇帝。' },
  { slug: 'agapetus-ii', nameZh: '亞加丕二世', nameEn: 'Agapetus II', nameLat: 'Agapetus PP. II', birthName: 'Agapito', pontificateStart: '946-05-10', pontificateEnd: '955-11-08', century: 10, nationality: '義大利' },
  { slug: 'marinus-ii', nameZh: '馬里諾二世', nameEn: 'Marinus II', nameLat: 'Marinus PP. II', birthName: 'Marino', pontificateStart: '942-10-30', pontificateEnd: '946-05-01', century: 10, nationality: '義大利' },
  { slug: 'stephen-viii', nameZh: '斯德望八世', nameEn: 'Stephen VIII', nameLat: 'Stephanus PP. VIII', birthName: 'Stefano', pontificateStart: '939-07-14', pontificateEnd: '942-10-01', century: 10, nationality: '義大利' },
  { slug: 'leo-vii', nameZh: '良七世', nameEn: 'Leo VII', nameLat: 'Leo PP. VII', birthName: 'Leone', pontificateStart: '936-01-03', pontificateEnd: '939-07-13', century: 10, nationality: '義大利' },
  { slug: 'john-xi', nameZh: '若望十一世', nameEn: 'John XI', nameLat: 'Ioannes PP. XI', birthName: 'Giovanni', pontificateStart: '931-03-01', pontificateEnd: '935-12-01', century: 10, nationality: '義大利' },
  { slug: 'stephen-vii', nameZh: '斯德望七世', nameEn: 'Stephen VII', nameLat: 'Stephanus PP. VII', birthName: 'Stefano', pontificateStart: '928-12-01', pontificateEnd: '931-02-01', century: 10, nationality: '義大利' },
  { slug: 'leo-vi', nameZh: '良六世', nameEn: 'Leo VI', nameLat: 'Leo PP. VI', birthName: 'Leone', pontificateStart: '928-05-01', pontificateEnd: '928-12-01', century: 10, nationality: '義大利' },
  { slug: 'john-x', nameZh: '若望十世', nameEn: 'John X', nameLat: 'Ioannes PP. X', birthName: 'Giovanni', pontificateStart: '914-03-01', pontificateEnd: '928-05-01', century: 10, nationality: '義大利' },
  { slug: 'lando', nameZh: '蘭多', nameEn: 'Lando', nameLat: 'Lando', birthName: 'Lando', pontificateStart: '913-07-01', pontificateEnd: '914-02-01', century: 10, nationality: '義大利' },
  { slug: 'anastasius-iii', nameZh: '阿納大削三世', nameEn: 'Anastasius III', nameLat: 'Anastasius PP. III', birthName: 'Anastasio', pontificateStart: '911-04-01', pontificateEnd: '913-06-01', century: 10, nationality: '義大利' },
  { slug: 'sergius-iii', nameZh: '塞奇三世', nameEn: 'Sergius III', nameLat: 'Sergius PP. III', birthName: 'Sergio', pontificateStart: '904-01-29', pontificateEnd: '911-04-14', century: 10, nationality: '義大利', notesZh: '「Saeculum Obscurum」黑暗世紀典型代表。' },
  { slug: 'leo-v', nameZh: '良五世', nameEn: 'Leo V', nameLat: 'Leo PP. V', birthName: 'Leone', pontificateStart: '903-07-01', pontificateEnd: '903-09-01', century: 10, nationality: '義大利' },
  { slug: 'benedict-iv', nameZh: '本篤四世', nameEn: 'Benedict IV', nameLat: 'Benedictus PP. IV', birthName: 'Benedetto', pontificateStart: '900-02-01', pontificateEnd: '903-07-01', century: 10, nationality: '義大利' },

  // ════════════════════ 9 世紀 ════════════════════
  { slug: 'john-ix', nameZh: '若望九世', nameEn: 'John IX', nameLat: 'Ioannes PP. IX', birthName: 'Giovanni', pontificateStart: '898-01-01', pontificateEnd: '900-01-01', century: 9, nationality: '義大利' },
  { slug: 'theodore-ii', nameZh: '德奧多二世', nameEn: 'Theodore II', nameLat: 'Theodorus PP. II', birthName: 'Teodoro', pontificateStart: '897-12-01', pontificateEnd: '897-12-20', century: 9, nationality: '義大利' },
  { slug: 'romanus', nameZh: '羅馬諾', nameEn: 'Romanus', nameLat: 'Romanus', birthName: 'Romano', pontificateStart: '897-08-01', pontificateEnd: '897-11-01', century: 9, nationality: '義大利' },
  { slug: 'stephen-vi', nameZh: '斯德望六世', nameEn: 'Stephen VI', nameLat: 'Stephanus PP. VI', birthName: 'Stefano', pontificateStart: '896-05-01', pontificateEnd: '897-08-01', century: 9, nationality: '義大利', notesZh: '897 主持惡名昭著的「Cadaver Synod」— 將前任 Formosus 屍體挖出受審。' },
  { slug: 'boniface-vi', nameZh: '鮑尼法六世', nameEn: 'Boniface VI', nameLat: 'Bonifatius PP. VI', birthName: 'Bonifacio', pontificateStart: '896-04-01', pontificateEnd: '896-04-26', century: 9, nationality: '義大利' },
  { slug: 'formosus', nameZh: '福爾摩肖', nameEn: 'Formosus', nameLat: 'Formosus', birthName: 'Formoso', pontificateStart: '891-10-06', pontificateEnd: '896-04-04', century: 9, nationality: '義大利' },
  { slug: 'stephen-v', nameZh: '斯德望五世', nameEn: 'Stephen V', nameLat: 'Stephanus PP. V', birthName: 'Stefano', pontificateStart: '885-09-14', pontificateEnd: '891-09-14', century: 9, nationality: '義大利' },
  { slug: 'hadrian-iii', nameZh: '哈德良三世', nameEn: 'Hadrian III', nameLat: 'Hadrianus PP. III', birthName: 'Adriano', pontificateStart: '884-05-17', pontificateEnd: '885-09-08', century: 9, nationality: '義大利' },
  { slug: 'marinus-i', nameZh: '馬里諾一世', nameEn: 'Marinus I', nameLat: 'Marinus PP. I', birthName: 'Marino', pontificateStart: '882-12-16', pontificateEnd: '884-05-15', century: 9, nationality: '義大利' },
  { slug: 'john-viii', nameZh: '若望八世', nameEn: 'John VIII', nameLat: 'Ioannes PP. VIII', birthName: 'Giovanni', pontificateStart: '872-12-14', pontificateEnd: '882-12-16', century: 9, nationality: '義大利' },
  { slug: 'hadrian-ii', nameZh: '哈德良二世', nameEn: 'Hadrian II', nameLat: 'Hadrianus PP. II', birthName: 'Adriano', pontificateStart: '867-12-14', pontificateEnd: '872-12-01', century: 9, nationality: '義大利' },
  { slug: 'nicholas-i', nameZh: '尼閣一世', nameEn: 'Nicholas I', nameLat: 'Nicolaus PP. I', birthName: 'Niccolò', pontificateStart: '858-04-24', pontificateEnd: '867-11-13', century: 9, nationality: '義大利', notesZh: '別號「大尼閣」(the Great)。Photian 分裂的關鍵人物；866《Responsa ad consulta Bulgarorum》對保加利亞人 106 問答，是中世紀教宗訓導典範文件。' },
  { slug: 'benedict-iii', nameZh: '本篤三世', nameEn: 'Benedict III', nameLat: 'Benedictus PP. III', birthName: 'Benedetto', pontificateStart: '855-09-29', pontificateEnd: '858-04-17', century: 9, nationality: '義大利' },
  { slug: 'leo-iv', nameZh: '良四世', nameEn: 'Leo IV', nameLat: 'Leo PP. IV', birthName: 'Leone', pontificateStart: '847-04-10', pontificateEnd: '855-07-17', century: 9, nationality: '義大利', notesZh: '848 興建梵蒂岡周圍 Leonine 城牆，抵禦撒拉森人。' },
  { slug: 'sergius-ii', nameZh: '塞奇二世', nameEn: 'Sergius II', nameLat: 'Sergius PP. II', birthName: 'Sergio', pontificateStart: '844-01-01', pontificateEnd: '847-01-27', century: 9, nationality: '義大利' },
  { slug: 'gregory-iv', nameZh: '額我略四世', nameEn: 'Gregory IV', nameLat: 'Gregorius PP. IV', birthName: 'Gregorio', pontificateStart: '827-03-29', pontificateEnd: '844-01-25', century: 9, nationality: '義大利' },
  { slug: 'valentine', nameZh: '瓦倫廷', nameEn: 'Valentine', nameLat: 'Valentinus', birthName: 'Valentino', pontificateStart: '827-08-01', pontificateEnd: '827-09-10', century: 9, nationality: '義大利' },
  { slug: 'eugene-ii', nameZh: '尤金二世', nameEn: 'Eugene II', nameLat: 'Eugenius PP. II', birthName: 'Eugenio', pontificateStart: '824-02-08', pontificateEnd: '827-08-27', century: 9, nationality: '義大利' },
  { slug: 'paschal-i', nameZh: '巴斯加一世', nameEn: 'Paschal I', nameLat: 'Paschalis PP. I', birthName: 'Pasquale Massimi', pontificateStart: '817-01-25', pontificateEnd: '824-02-11', century: 9, nationality: '義大利' },
  { slug: 'stephen-iv', nameZh: '斯德望四世', nameEn: 'Stephen IV', nameLat: 'Stephanus PP. IV', birthName: 'Stefano', pontificateStart: '816-06-22', pontificateEnd: '817-01-24', century: 9, nationality: '義大利' },
  { slug: 'leo-iii', nameZh: '良三世', nameEn: 'Leo III', nameLat: 'Leo PP. III', birthName: 'Leone', pontificateStart: '795-12-26', pontificateEnd: '816-06-12', century: 9, nationality: '義大利', notesZh: '800 聖誕節在聖伯多祿大殿為查理曼加冕為神聖羅馬帝國皇帝（神羅帝國正式起源）。' },

  // ════════════════════ 8 世紀 ════════════════════
  { slug: 'hadrian-i', nameZh: '哈德良一世', nameEn: 'Hadrian I', nameLat: 'Hadrianus PP. I', birthName: 'Adriano', pontificateStart: '772-02-09', pontificateEnd: '795-12-25', century: 8, nationality: '義大利', notesZh: '787 派代表參加 Nicaea II 大公會議解決聖像爭議。' },
  { slug: 'stephen-iii', nameZh: '斯德望三世', nameEn: 'Stephen III', nameLat: 'Stephanus PP. III', birthName: 'Stefano', pontificateStart: '768-08-07', pontificateEnd: '772-01-24', century: 8, nationality: '西西里' },
  { slug: 'paul-i', nameZh: '保祿一世', nameEn: 'Paul I', nameLat: 'Paulus PP. I', birthName: 'Paolo', pontificateStart: '757-05-29', pontificateEnd: '767-06-28', century: 8, nationality: '義大利' },
  { slug: 'stephen-ii', nameZh: '斯德望二世', nameEn: 'Stephen II', nameLat: 'Stephanus PP. II', birthName: 'Stefano', pontificateStart: '752-03-26', pontificateEnd: '757-04-26', century: 8, nationality: '義大利', notesZh: '754 為法蘭克王 Pippin 加冕，奠定教宗國（Papal States）基礎。' },
  { slug: 'zachary', nameZh: '匝加利亞', nameEn: 'Zachary', nameLat: 'Zacharias', birthName: 'Zaccaria', pontificateStart: '741-12-10', pontificateEnd: '752-03-22', century: 8, nationality: '希臘', notesZh: '末位希臘籍教宗。' },
  { slug: 'gregory-iii', nameZh: '額我略三世', nameEn: 'Gregory III', nameLat: 'Gregorius PP. III', birthName: 'Gregorio', pontificateStart: '731-03-18', pontificateEnd: '741-11-28', century: 8, nationality: '敘利亞', notesZh: '末位非歐洲籍教宗，至 2013 方濟各為止。' },
  { slug: 'gregory-ii', nameZh: '額我略二世', nameEn: 'Gregory II', nameLat: 'Gregorius PP. II', birthName: 'Gregorio', pontificateStart: '715-05-19', pontificateEnd: '731-02-11', century: 8, nationality: '義大利' },
  { slug: 'constantine', nameZh: '君士坦丁', nameEn: 'Constantine', nameLat: 'Constantinus', birthName: 'Costantino', pontificateStart: '708-03-25', pontificateEnd: '715-04-09', century: 8, nationality: '敘利亞' },
  { slug: 'sisinnius', nameZh: '西辛紐', nameEn: 'Sisinnius', nameLat: 'Sisinnius', birthName: 'Sisinnio', pontificateStart: '708-01-15', pontificateEnd: '708-02-04', century: 8, nationality: '敘利亞' },
  { slug: 'john-vii', nameZh: '若望七世', nameEn: 'John VII', nameLat: 'Ioannes PP. VII', birthName: 'Giovanni', pontificateStart: '705-03-01', pontificateEnd: '707-10-18', century: 8, nationality: '希臘' },
  { slug: 'john-vi', nameZh: '若望六世', nameEn: 'John VI', nameLat: 'Ioannes PP. VI', birthName: 'Giovanni', pontificateStart: '701-10-30', pontificateEnd: '705-01-11', century: 8, nationality: '希臘' },

  // ════════════════════ 7 世紀 ════════════════════
  { slug: 'sergius-i', nameZh: '塞奇一世', nameEn: 'Sergius I', nameLat: 'Sergius PP. I', birthName: 'Sergio', pontificateStart: '687-12-15', pontificateEnd: '701-09-08', century: 7, nationality: '敘利亞' },
  { slug: 'conon', nameZh: '科農', nameEn: 'Conon', nameLat: 'Conon', birthName: 'Conone', pontificateStart: '686-10-21', pontificateEnd: '687-09-21', century: 7, nationality: '希臘' },
  { slug: 'john-v', nameZh: '若望五世', nameEn: 'John V', nameLat: 'Ioannes PP. V', birthName: 'Giovanni', pontificateStart: '685-07-23', pontificateEnd: '686-08-02', century: 7, nationality: '敘利亞' },
  { slug: 'benedict-ii', nameZh: '本篤二世', nameEn: 'Benedict II', nameLat: 'Benedictus PP. II', birthName: 'Benedetto', pontificateStart: '684-06-26', pontificateEnd: '685-05-08', century: 7, nationality: '義大利' },
  { slug: 'leo-ii', nameZh: '良二世', nameEn: 'Leo II', nameLat: 'Leo PP. II', birthName: 'Leone', pontificateStart: '682-08-17', pontificateEnd: '683-07-03', century: 7, nationality: '西西里', notesZh: '正式確認君士坦丁堡三大公會議（681）對前任 Honorius I 的譴責。' },
  { slug: 'agatho', nameZh: '亞加大', nameEn: 'Agatho', nameLat: 'Agatho', birthName: 'Agatone', pontificateStart: '678-06-27', pontificateEnd: '681-01-10', century: 7, nationality: '西西里', notesZh: '其代表參加君士坦丁堡三大公會議 680-681 譴責 Monothelitism。' },
  { slug: 'donus', nameZh: '多諾', nameEn: 'Donus', nameLat: 'Donus', birthName: 'Dono', pontificateStart: '676-11-02', pontificateEnd: '678-04-11', century: 7, nationality: '義大利' },
  { slug: 'adeodatus-ii', nameZh: '戴德二世', nameEn: 'Adeodatus II', nameLat: 'Adeodatus PP. II', birthName: 'Adeodato', pontificateStart: '672-04-11', pontificateEnd: '676-06-17', century: 7, nationality: '義大利' },
  { slug: 'vitalian', nameZh: '維大利諾', nameEn: 'Vitalian', nameLat: 'Vitalianus', birthName: 'Vitaliano', pontificateStart: '657-07-30', pontificateEnd: '672-01-27', century: 7, nationality: '義大利' },
  { slug: 'eugene-i', nameZh: '尤金一世', nameEn: 'Eugene I', nameLat: 'Eugenius PP. I', birthName: 'Eugenio', pontificateStart: '654-08-10', pontificateEnd: '657-06-02', century: 7, nationality: '義大利' },
  { slug: 'martin-i', nameZh: '瑪定一世', nameEn: 'Martin I', nameLat: 'Martinus PP. I', birthName: 'Martino', pontificateStart: '649-07-05', pontificateEnd: '655-09-16', century: 7, nationality: '義大利', notesZh: '649 拉特朗會議譴責 Monothelitism；遭拜占庭皇帝 Constans II 逮捕流放至 Cherson 殉道。最後一位封聖殉道教宗。' },
  { slug: 'theodore-i', nameZh: '德奧多一世', nameEn: 'Theodore I', nameLat: 'Theodorus PP. I', birthName: 'Teodoro', pontificateStart: '642-11-24', pontificateEnd: '649-05-14', century: 7, nationality: '希臘' },
  { slug: 'john-iv', nameZh: '若望四世', nameEn: 'John IV', nameLat: 'Ioannes PP. IV', birthName: 'Giovanni', pontificateStart: '640-12-24', pontificateEnd: '642-10-12', century: 7, nationality: '達爾馬提亞' },
  { slug: 'severinus', nameZh: '塞維利諾', nameEn: 'Severinus', nameLat: 'Severinus', birthName: 'Severino', pontificateStart: '640-05-28', pontificateEnd: '640-08-02', century: 7, nationality: '義大利' },
  { slug: 'honorius-i', nameZh: '何諾理一世', nameEn: 'Honorius I', nameLat: 'Honorius PP. I', birthName: 'Onorio', pontificateStart: '625-10-27', pontificateEnd: '638-10-12', century: 7, nationality: '義大利', notesZh: '致 Sergius 諸信，後被君士坦丁堡三大公會議（681）譴責為支持 Monothelitism — 梵一教宗無謬論辯論時的歷史 case。' },
  { slug: 'boniface-v', nameZh: '鮑尼法五世', nameEn: 'Boniface V', nameLat: 'Bonifatius PP. V', birthName: 'Bonifacio', pontificateStart: '619-12-23', pontificateEnd: '625-10-25', century: 7, nationality: '義大利' },
  { slug: 'adeodatus-i', nameZh: '戴德一世', nameEn: 'Deusdedit / Adeodatus I', nameLat: 'Deusdedit', birthName: 'Adeodato', pontificateStart: '615-10-19', pontificateEnd: '618-11-08', century: 7, nationality: '義大利' },
  { slug: 'boniface-iv', nameZh: '鮑尼法四世', nameEn: 'Boniface IV', nameLat: 'Bonifatius PP. IV', birthName: 'Bonifacio', pontificateStart: '608-08-25', pontificateEnd: '615-05-08', century: 7, nationality: '義大利', notesZh: '609 將羅馬萬神殿（Pantheon）改建為聖母教堂，是首座異教廟宇改基督教堂之先例。' },
  { slug: 'boniface-iii', nameZh: '鮑尼法三世', nameEn: 'Boniface III', nameLat: 'Bonifatius PP. III', birthName: 'Bonifacio', pontificateStart: '607-02-19', pontificateEnd: '607-11-12', century: 7, nationality: '義大利' },

  // ════════════════════ 6 世紀 ════════════════════
  { slug: 'sabinian', nameZh: '撒比尼盎', nameEn: 'Sabinian', nameLat: 'Sabinianus', birthName: 'Sabiniano', pontificateStart: '604-09-13', pontificateEnd: '606-02-22', century: 7, nationality: '義大利' },
  { slug: 'gregory-i', nameZh: '額我略一世', nameEn: 'Gregory I', nameLat: 'Gregorius PP. I', birthName: 'Gregorio', pontificateStart: '590-09-03', pontificateEnd: '604-03-12', century: 6, nationality: '義大利', notesZh: '別號「大額我略」(the Great)，西方四大教父之一。《Liber Regulae Pastoralis》論牧者職分；《Moralia in Iob》14 冊註約伯傳；《Registrum Epistolarum》約 850 封書信。派遣 Augustine of Canterbury 595 至英格蘭傳教，奠定英國教會基礎。' },
  { slug: 'pelagius-ii', nameZh: '培拉糾二世', nameEn: 'Pelagius II', nameLat: 'Pelagius PP. II', birthName: 'Pelagio', pontificateStart: '579-11-26', pontificateEnd: '590-02-07', century: 6, nationality: '義大利' },
  { slug: 'benedict-i', nameZh: '本篤一世', nameEn: 'Benedict I', nameLat: 'Benedictus PP. I', birthName: 'Benedetto', pontificateStart: '575-06-02', pontificateEnd: '579-07-30', century: 6, nationality: '義大利' },
  { slug: 'john-iii', nameZh: '若望三世', nameEn: 'John III', nameLat: 'Ioannes PP. III', birthName: 'Giovanni', pontificateStart: '561-07-17', pontificateEnd: '574-07-13', century: 6, nationality: '義大利' },
  { slug: 'pelagius-i', nameZh: '培拉糾一世', nameEn: 'Pelagius I', nameLat: 'Pelagius PP. I', birthName: 'Pelagio', pontificateStart: '556-04-16', pontificateEnd: '561-03-04', century: 6, nationality: '義大利' },
  { slug: 'vigilius', nameZh: '維日略', nameEn: 'Vigilius', nameLat: 'Vigilius', birthName: 'Vigilio', pontificateStart: '537-03-29', pontificateEnd: '555-06-07', century: 6, nationality: '義大利', notesZh: '主持 553 君士坦丁堡二大公會議；其立場反覆引發西方教會分裂。' },
  { slug: 'silverius', nameZh: '西爾物理', nameEn: 'Silverius', nameLat: 'Silverius', birthName: 'Silverio', pontificateStart: '536-06-08', pontificateEnd: '537-03-11', century: 6, nationality: '義大利' },
  { slug: 'agapetus-i', nameZh: '亞加丕一世', nameEn: 'Agapetus I', nameLat: 'Agapetus PP. I', birthName: 'Agapito', pontificateStart: '535-05-13', pontificateEnd: '536-04-22', century: 6, nationality: '義大利' },
  { slug: 'john-ii', nameZh: '若望二世', nameEn: 'John II', nameLat: 'Ioannes PP. II', birthName: 'Mercurio', pontificateStart: '533-01-02', pontificateEnd: '535-05-08', century: 6, nationality: '義大利', notesZh: '首位即位時改名的教宗（俗名 Mercurius 與羅馬神 Mercury 重名）。' },
  { slug: 'boniface-ii', nameZh: '鮑尼法二世', nameEn: 'Boniface II', nameLat: 'Bonifatius PP. II', birthName: 'Bonifacio', pontificateStart: '530-09-22', pontificateEnd: '532-10-17', century: 6, nationality: '哥德', notesZh: '首位日耳曼裔教宗。' },
  { slug: 'felix-iv', nameZh: '斐理斯四世', nameEn: 'Felix IV (III)', nameLat: 'Felix PP. IV', birthName: 'Felice', pontificateStart: '526-07-12', pontificateEnd: '530-09-22', century: 6, nationality: '義大利' },
  { slug: 'john-i', nameZh: '若望一世', nameEn: 'John I', nameLat: 'Ioannes PP. I', birthName: 'Giovanni', pontificateStart: '523-08-13', pontificateEnd: '526-05-18', century: 6, nationality: '義大利', notesZh: '遭東哥德王 Theodoric 監禁，在獄中殉道。' },
  { slug: 'hormisdas', nameZh: '何彌斯達', nameEn: 'Hormisdas', nameLat: 'Hormisdas', birthName: 'Ormisda', pontificateStart: '514-07-20', pontificateEnd: '523-08-06', century: 6, nationality: '義大利', notesZh: '515《Libellus Hormisdae》— 解決 Acacian Schism（484-519）35 年東西方分裂的合一公式，東方主教簽署即承認羅馬首席權。' },
  { slug: 'symmachus', nameZh: '西瑪克', nameEn: 'Symmachus', nameLat: 'Symmachus', birthName: 'Simmaco', pontificateStart: '498-11-22', pontificateEnd: '514-07-19', century: 6, nationality: '撒丁尼亞' },

  // ════════════════════ 5 世紀 ════════════════════
  { slug: 'anastasius-ii', nameZh: '阿納大削二世', nameEn: 'Anastasius II', nameLat: 'Anastasius PP. II', birthName: 'Anastasio', pontificateStart: '496-11-24', pontificateEnd: '498-11-19', century: 5, nationality: '義大利' },
  { slug: 'gelasius-i', nameZh: '哲拉削一世', nameEn: 'Gelasius I', nameLat: 'Gelasius PP. I', birthName: 'Gelasio', pontificateStart: '492-03-01', pontificateEnd: '496-11-21', century: 5, nationality: '義大利', notesZh: '494《Famuli vestrae pietatis》（致東羅馬皇帝 Anastasius）首次系統提出「兩權說」(Two Powers / Two Swords)，論教會權與帝國權的分立。' },
  { slug: 'felix-iii', nameZh: '斐理斯三世', nameEn: 'Felix III (II)', nameLat: 'Felix PP. III', birthName: 'Felice', pontificateStart: '483-03-13', pontificateEnd: '492-03-01', century: 5, nationality: '義大利', notesZh: '484 絕罰君士坦丁堡宗主教 Acacius，引發 Acacian Schism。' },
  { slug: 'simplicius', nameZh: '辛布利修', nameEn: 'Simplicius', nameLat: 'Simplicius', birthName: 'Simplicio', pontificateStart: '468-03-03', pontificateEnd: '483-03-10', century: 5, nationality: '義大利', notesZh: '476 在位時西羅馬帝國滅亡。' },
  { slug: 'hilarius', nameZh: '希拉略', nameEn: 'Hilarius', nameLat: 'Hilarius', birthName: 'Ilario', pontificateStart: '461-11-19', pontificateEnd: '468-02-29', century: 5, nationality: '撒丁尼亞' },
  { slug: 'leo-i', nameZh: '良一世', nameEn: 'Leo I', nameLat: 'Leo PP. I', birthName: 'Leone', pontificateStart: '440-09-29', pontificateEnd: '461-11-10', century: 5, nationality: '義大利', notesZh: '別號「大良」(the Great)，西方四大教父之一。449《Tome of Leo》致 Flavianus 論基督一位二性的神學經典，450 迦克墩大公會議奉之為基督論正統依據。173 封書信、96 篇講道存世。452 親自勸退匈奴 Attila 離開義大利。' },
  { slug: 'sixtus-iii', nameZh: '西斯篤三世', nameEn: 'Sixtus III', nameLat: 'Sixtus PP. III', birthName: 'Sisto', pontificateStart: '432-07-31', pontificateEnd: '440-08-19', century: 5, nationality: '義大利' },
  { slug: 'celestine-i', nameZh: '雷定一世', nameEn: 'Celestine I', nameLat: 'Caelestinus PP. I', birthName: 'Celestino', pontificateStart: '422-09-10', pontificateEnd: '432-07-27', century: 5, nationality: '義大利', notesZh: '致 Cyril of Alexandria 諸信支持其反 Nestorius，奠定 431 厄弗所大公會議基調。' },
  { slug: 'boniface-i', nameZh: '鮑尼法一世', nameEn: 'Boniface I', nameLat: 'Bonifatius PP. I', birthName: 'Bonifacio', pontificateStart: '418-12-28', pontificateEnd: '422-09-04', century: 5, nationality: '義大利' },
  { slug: 'zosimus', nameZh: '佐西默', nameEn: 'Zosimus', nameLat: 'Zosimus', birthName: 'Zosimo', pontificateStart: '417-03-18', pontificateEnd: '418-12-26', century: 5, nationality: '希臘' },
  { slug: 'innocent-i', nameZh: '諾森一世', nameEn: 'Innocent I', nameLat: 'Innocentius PP. I', birthName: 'Innocenzo', pontificateStart: '401-12-22', pontificateEnd: '417-03-12', century: 5, nationality: '義大利', notesZh: '譴責 Pelagianism 諸信；強化羅馬主教在西方教會的首席地位。' },

  // ════════════════════ 4 世紀（含尼西亞會議 325 時的教宗） ════════════════════
  { slug: 'anastasius-i', nameZh: '阿納大削一世', nameEn: 'Anastasius I', nameLat: 'Anastasius PP. I', birthName: 'Anastasio', pontificateStart: '399-11-27', pontificateEnd: '401-12-19', century: 4, nationality: '義大利' },
  { slug: 'siricius', nameZh: '西利修', nameEn: 'Siricius', nameLat: 'Siricius', birthName: 'Siricio', pontificateStart: '384-12-15', pontificateEnd: '399-11-26', century: 4, nationality: '義大利', notesZh: '385《Directa》（致 Himerius 主教論教會紀律）是學界普遍認可的第一封正式 Decretal — 現代教廷訓導文件法律體裁的源頭。' },
  { slug: 'damasus-i', nameZh: '達瑪穌一世', nameEn: 'Damasus I', nameLat: 'Damasus PP. I', birthName: 'Damaso', pontificateStart: '366-10-01', pontificateEnd: '384-12-11', century: 4, nationality: '葡萄牙／西班牙', notesZh: '382《Tomus Damasi》（Council of Rome 後的信經 + canon list）是教宗訓導文獻最早正式體裁。委託聖熱羅尼莫翻譯拉丁文聖經 Vulgate（從 382 開始至 405 完成）— 改變整個西方基督教 1000 年的聖經文本傳統。' },
  { slug: 'liberius', nameZh: '利伯里', nameEn: 'Liberius', nameLat: 'Liberius', birthName: 'Liberio', pontificateStart: '352-05-17', pontificateEnd: '366-09-24', century: 4, nationality: '義大利', notesZh: '在 Arian 爭議中曾簽署可疑信條（受脅迫），事後是否仍正統信仰存疑。' },
  { slug: 'julius-i', nameZh: '儒略一世', nameEn: 'Julius I', nameLat: 'Iulius PP. I', birthName: 'Giulio', pontificateStart: '337-02-06', pontificateEnd: '352-04-12', century: 4, nationality: '義大利', notesZh: '343 召開 Sardica 會議支持 Athanasius 反 Arianism，確立羅馬主教為西方教會的最終仲裁者。' },
  { slug: 'mark', nameZh: '馬爾谷', nameEn: 'Mark', nameLat: 'Marcus', birthName: 'Marco', pontificateStart: '336-01-18', pontificateEnd: '336-10-07', century: 4, nationality: '義大利' },
  { slug: 'sylvester-i', nameZh: '西爾物斯德一世', nameEn: 'Sylvester I', nameLat: 'Silvester PP. I', birthName: 'Silvestro', pontificateStart: '314-01-31', pontificateEnd: '335-12-31', century: 4, nationality: '義大利', notesZh: '尼西亞第一次大公會議（325）期間在位。他本人並未親自赴會，僅派代表（priest Vitus 與 Vincent）；會議主導者為君士坦丁大帝。後世偽造的《君士坦丁御賜書》(Donatio Constantini，8 世紀偽作) 將教宗國的權威神話託付於 Sylvester I — 中世紀政教關係最重要的偽造文獻之一。' },
]

export function findPope(slug: string): Pope | undefined {
  return POPES.find(p => p.slug === slug)
}

/** 依 pontificate 起訖推算教宗任期所跨的世紀（含起訖兩端）。
 *  例：John Paul II 1978-2005 → [20, 21]；Leo XIII 1878-1903 → [19, 20]。
 *  在位中（pontificateEnd 空字串）以當下年份計。 */
export function centuriesOfPope(p: Pope): number[] {
  const startY = parseInt(p.pontificateStart.slice(0, 4), 10)
  const endY = p.pontificateEnd
    ? parseInt(p.pontificateEnd.slice(0, 4), 10)
    : new Date().getFullYear()
  const cStart = Math.floor((startY - 1) / 100) + 1
  const cEnd = Math.floor((endY - 1) / 100) + 1
  const out: number[] = []
  for (let c = cStart; c <= cEnd; c++) out.push(c)
  return out
}

/** 按世紀分組教宗（新→舊）。跨世紀的教宗會在兩邊都出現。 */
export function popesByCentury(): { century: number; popes: Pope[] }[] {
  const map = new Map<number, Pope[]>()
  for (const p of POPES) {
    for (const c of centuriesOfPope(p)) {
      if (!map.has(c)) map.set(c, [])
      map.get(c)!.push(p)
    }
  }
  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([century, popes]) => ({
      century,
      popes: popes.sort((a, b) => b.pontificateStart.localeCompare(a.pontificateStart)),
    }))
}

export function popesInCentury(century: number): Pope[] {
  return POPES
    .filter(p => centuriesOfPope(p).includes(century))
    .sort((a, b) => b.pontificateStart.localeCompare(a.pontificateStart))
}
