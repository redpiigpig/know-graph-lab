import type { Creed } from '../types'

export const westminsterConfession: Creed = {
  slug: 'westminster-confession',
  category: 'protestant-confession',
  order: 3008,
  nameZh: '西敏信條 / 威斯敏斯特信仰告白',
  nameEn: 'Westminster Confession of Faith',
  nameLat: 'Confessio Fidei Westmonasteriensis',
  year: 1646,
  location: '英格蘭倫敦西敏寺',
  topic: '33 章系統神學式信仰宣言；英語世界長老宗與公理宗的根基文件，影響力僅次於使徒信經',
  authors: [
    '西敏會議（Westminster Assembly, 1643-1653）— 神學家 121 位、議會代表 30 位',
    '蘇格蘭代表 6 位（列席無表決權，含 Samuel Rutherford、George Gillespie）',
  ],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Reformed',
      label: '張麟至譯本（繁體）',
      text: '',
      textKey: 'westminster-confession-chinese',
      source: 'TRC 藏本，33 章全文繁體排印。',
      translator: '張麟至',
    },
    {
      lang: 'zh-Hant-Reformed',
      label: '趙中輝譯本（附歷史導言）',
      text: '',
      textKey: 'westminster-confession-zhao',
      source: '基督教改革宗翻譯社（rtf-usa.com）刊本，卷首有英國聖公會主教制爭議的背景說明。',
      translator: '趙中輝',
    },
    {
      lang: 'en',
      label: 'English 1646（待補）',
      text: '',
      placeholder: true,
      source: 'The Humble Advice of the Assembly of Divines, London 1646.',
    },
  ],
  summaryZh: `1643 年英格蘭長期國會召開西敏會議，原意是修訂聖公會《三十九條》，隨蘇格蘭與英格蘭締結《神聖盟約》(Solemn League and Covenant) 而轉為編纂一套全新的信仰標準。信條於 1646 年完成，1647 年為蘇格蘭教會大會採納，1648 年經英格蘭國會（略作修改）批准。

全書 33 章，自「論聖經」起，依次論神與三位一體、神的預旨、創造、護理、人的墮落、神的約、基督中保、自由意志、有效恩召、稱義、得兒子的名分、成聖、信心、悔改、善行、聖徒堅忍、蒙恩確據、律法、基督徒的自由、敬拜與安息日、誓願、政府、婚姻、教會、聖徒相通、聖禮、洗禮、聖餐、教會懲戒、教會會議、死後狀態與復活、末後審判。

與《西敏大要理問答》《西敏小要理問答》《公共崇拜指南》《教會治理形式》合稱《西敏準則》(Westminster Standards)，是英語世界長老宗最核心的教義文件，亦為公理宗《薩伏伊宣言》(1658) 與浸信宗《1689 信仰告白》所本。`,
  notes: `- 1646 完成，1647 蘇格蘭教會大會採納，1648 英格蘭國會批准（刪去教會懲戒相關部分）
- 美國長老會 1788 年修訂第 23 章（論政府），刪去公權力召集教會會議之權
- 《西敏準則》五件：信條、大要理問答、小要理問答、公共崇拜指南、教會治理形式
- 衍生文件：公理宗《薩伏伊宣言》1658 / 特殊浸信會《1689 信仰告白》— 兩者大量沿用本信條文字，僅改教會論與聖禮論
- 接受傳統：蘇格蘭教會 / 英語世界各長老宗（PCA、OPC、EPC…）/ 華人改革宗長老教會
- 中譯情況：華語通行譯本至少四家（趙中輝、趙天恩、張麟至、王瑞珍），本站先收兩種`,
  related: ['westminster-shorter-catechism', 'westminster-larger-catechism', 'canons-of-dort', 'reformed-belgic'],
}
