import type { Creed } from '../types'

export const heidelbergCatechism: Creed = {
  slug: 'heidelberg-catechism',
  category: 'protestant-confession',
  order: 3006,
  nameZh: '海德堡要理問答',
  nameEn: 'Heidelberg Catechism',
  nameLat: 'Catechesis Palatina',
  year: 1563,
  location: '普法爾茨選侯國海德堡（神聖羅馬帝國）',
  topic: '129 問答分 52 主日；以「罪愆—救恩—感恩」三段架構貫串；改革宗「合一信經三聯」之一，也是最廣為使用的改革宗要理問答',
  authors: [
    'Zacharias Ursinus 烏爾西努（主要執筆）',
    'Caspar Olevianus 俄利維亞努（協同編纂，傳統歸屬）',
    '選侯 Frederick III 腓特烈三世（下令編纂並作序）',
  ],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Reformed',
      label: '中譯本（分 129 問，附經文出處）',
      text: '',
      textKey: 'heidelberg-catechism-chinese',
      source: 'TRC 改革宗資源站藏本，逐問附經文出處編號。',
    },
    {
      lang: 'zh-Hant-Reformed',
      label: '另一中譯本（按 52 主日編排）',
      text: '',
      textKey: 'heidelberg-catechism-alt-zh',
      source: 'TRC 藏本，保留「主日一～主日五十二」的原始週課編排。',
    },
    {
      lang: 'de',
      label: '德文原文 1563（待補）',
      text: '',
      placeholder: true,
      source: 'Catechismus oder Christlicher Underricht, Heidelberg 1563（第三版含第 80 問全文）。',
    },
    {
      lang: 'lat',
      label: '拉丁文版 1563（待補）',
      text: '',
      placeholder: true,
      source: 'Catechesis religionis Christianae, quae traditur in ecclesiis et scholis Palatinatus.',
    },
    {
      lang: 'en',
      label: 'English translation（待補）',
      text: '',
      placeholder: true,
      source: 'Christian Reformed Church 1975 / United Reformed Churches official translation.',
    },
  ],
  summaryZh: `1563 年由普法爾茨選侯腓特烈三世下令編纂，用於統一其領地內路德宗與改革宗之間的教義爭議，並作為教會、學校與家庭的教導範本。主要執筆者為海德堡大學教授烏爾西努 (Zacharias Ursinus)；俄利維亞努 (Caspar Olevianus) 的參與程度近代學界已有保留。

全書 129 問答，分為三大部分：(1) 論人的罪愆與愁苦（問 3-11）；(2) 論人的拯救（問 12-85）；(3) 論感恩（問 86-129，含十誡與主禱文詳解）。開卷第 1 問「你無論是生是死，唯一的安慰是什麼？」為全書定調，是改革宗傳統中最著名的問答。

與《比利時信條》(1561)、《多特信條》(1619) 並稱改革宗「合一信經三聯」(Three Forms of Unity)。編排上按 52 個主日分課，設計為一年講畢一輪，至今仍是荷蘭系改革宗教會主日下午講道的固定循環。`,
  notes: `- 1563 年初版；同年第三版加入第 80 問（論彌撒為「可咒詛的偶像崇拜」），為回應天特會議而增
- 1618-19 多特總會審定為改革宗合一文件之一
- 三段架構「罪愆—救恩—感恩」(Elend / Erlösung / Dankbarkeit) 影響後世大量要理問答
- 接受傳統：荷蘭改革宗 / 美國 CRC、RCA、URCNA / 匈牙利歸正宗 / 德國改革宗
- 中譯情況：華語改革宗圈通行譯本多家（趙中輝、錢曜誠、呂沛淵、臺灣改革宗長老會），本站先收兩種
- 與《比利時信條》《多特信條》互為「合一信經三聯」，宜並讀`,
  related: ['reformed-belgic', 'canons-of-dort', 'westminster-confession'],
}
