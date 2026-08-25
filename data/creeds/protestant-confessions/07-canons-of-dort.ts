import type { Creed } from '../types'

export const canonsOfDort: Creed = {
  slug: 'canons-of-dort',
  category: 'protestant-confession',
  order: 3007,
  nameZh: '多特信條 / 多特信經',
  nameEn: 'Canons of Dort',
  nameLat: 'Canones Synodi Dordrechtanae',
  year: 1619,
  location: '尼德蘭多德雷赫特（Dordrecht）',
  topic: '針對阿民念派《抗辯文》五條的裁決；分五項教義（揀選與遺棄、基督之死、全然敗壞、恩典不可抗拒、聖徒堅忍），後世濃縮為「加爾文主義五要點」',
  authors: [
    '多特總會（1618-19）— 尼德蘭代表 62 位',
    '英格蘭、普法爾茨、黑森、瑞士、拿騷、日內瓦等外國代表 27 位',
  ],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Reformed',
      label: '小雅各譯本（五項教義全文，附經文出處）',
      text: '',
      textKey: 'canons-of-dort-chinese',
      source: 'TRC 改革宗資源站藏本，逐條附經文出處編號。',
      translator: '小雅各',
    },
    {
      lang: 'zh-Hant-Reformed',
      label: '另一中譯本（含歷史導言）',
      text: '',
      textKey: 'canons-of-dort-alt-zh',
      source: 'TRC 藏本，卷首有阿民念派爭議的背景說明。',
    },
    {
      lang: 'lat',
      label: '拉丁文原文 1619（待補）',
      text: '',
      placeholder: true,
      source: 'Judicium Synodi Nationalis Reformatarum Ecclesiarum Belgicarum, Dordrechti 1619.',
    },
    {
      lang: 'en',
      label: 'English translation（待補）',
      text: '',
      placeholder: true,
      source: 'Christian Reformed Church / URCNA official translation.',
    },
  ],
  summaryZh: `1618 年 11 月至 1619 年 5 月，尼德蘭改革宗教會在多德雷赫特召開全國總會，處理阿民念派（Remonstrants，抗辯派）1610 年《抗辯文》所提五條主張引發的全國性爭議。總會除尼德蘭代表外，另邀英格蘭、普法爾茨、瑞士、日內瓦等地代表與會，是改革宗史上最具國際性的一次會議。

裁決文分五項教義（Hoofdstuk）：第一項神的揀選與遺棄；第二項基督之死與人藉此得贖；第三、四項合併論人的敗壞與歸正的方式；第五項論聖徒的堅忍。每項先立正面條文，再逐一「駁斥謬論」(Rejectio Errorum)。後世英語世界以首字母縮寫 TULIP 概括，但該縮寫晚至二十世紀才出現，且順序與原文不合，讀原文時宜置之不理。

與《比利時信條》(1561)、《海德堡要理問答》(1563) 並稱改革宗「合一信經三聯」。`,
  notes: `- 1618-11-13 開議，1619-05-09 閉幕，共 154 次會議
- 同一總會另議定《多特教會法規》(Church Order of Dort) 與荷蘭文聖經官方譯本 (Statenvertaling)
- 阿民念派代表被逐出會場，非以辯論對手而以受審者身分出席，此程序爭議至今仍有討論
- 「加爾文主義五要點」是對本信條的後世概括，非本信條自身的架構；TULIP 縮寫晚出
- 接受傳統：荷蘭改革宗 / 美國 CRC、RCA、URCNA / 南非 NGK / 長老宗多有引用
- 站上另藏《多特教會法規》中英對照本，屬教會法規非信條，另行處理`,
  related: ['reformed-belgic', 'heidelberg-catechism', 'westminster-confession'],
}
