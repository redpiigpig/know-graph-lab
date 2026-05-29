import type { Creed } from '../types'

export const reformedBelgic: Creed = {
  slug: 'reformed-belgic',
  category: 'protestant-confession',
  order: 3004,
  nameZh: '比利時信條 / 改革宗信仰綱要',
  nameEn: 'Belgic Confession',
  nameLat: 'Confessio Belgica',
  year: 1561,
  location: '尼德蘭（西班牙統治下）',
  topic: '37 條改革宗信仰宣言；以法文起草，敬獻給西班牙國王腓力二世 (Philip II) 為尼德蘭歸正派信徒護教；改革宗「合一信經三聯」之一',
  authors: [
    'Guido de Brès（執筆 / 殉道）',
    'Adrien de Saravia / Hermann Modet / Godfried van Wingen（協助修訂）',
  ],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（Denzinger DH 5575-5590 摘錄）',
      text: '',
      textKey: 'reformed-belgic-chinese',
      source: '《公教會之信仰與倫理教義選集》（Denzinger 中譯）— 光啟文化 2013 / ISBN 9789575467418，附錄五。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'fr',
      label: 'Confession de Foy 1561（原文待補）',
      text: '',
      placeholder: true,
      source: 'Première impression 1561 (Rouen?); Guido de Brès 法文原稿。',
    },
    {
      lang: 'lat',
      label: '拉丁文版（1581 多德雷赫特會議審定，待補）',
      text: '',
      placeholder: true,
      source: 'Synod of Dort 1618-19 採用拉丁文版本作為改革宗合一文件。',
    },
    {
      lang: 'en',
      label: 'English translation (待補)',
      text: '',
      placeholder: true,
      source: 'Christian Reformed Church / Reformed Church in America official translation.',
    },
    {
      lang: 'zh-Hant-Reformed',
      label: '改革宗中譯本（待補）',
      text: '',
      placeholder: true,
      source: '改革宗出版有限公司／台灣改革宗神學院 譯本。',
    },
  ],
  summaryZh: `1561 年由 Guido de Brès 起草，以法文書寫，用作向西班牙國王腓力二世 (Philip II) 為尼德蘭歸正派信徒護教的信仰宣言。1567 年 de Brès 因信仰殉道於瓦朗謝訥 (Valenciennes)。

本信條共 37 條，內容涵蓋：(1) 天主與聖經（1-7）；(2) 三位一體與基督論（8-21）；(3) 因信稱義與成聖（22-26）；(4) 教會、聖事、教會職分（27-35）；(5) 政府與末日（36-37）。

比利時信條與《海德堡要理問答》(1563)、《多德雷赫特信條》(1619) 並稱為改革宗「合一信經三聯」(Three Forms of Unity)，至今仍是荷蘭改革宗 (Dutch Reformed Church)、美國基督教改革宗教會 (CRC)、美國改革宗教會 (RCA) 等的根基性信仰文件。`,
  notes: `- 1561 法文初版於尼德蘭流通
- 1566 Antwerp Synod 審定通過
- 1571 Emden Synod、1574 Dordrecht Provincial Synod、1581 全國 Synod、1619 Synod of Dort 多次審定確認
- 受 1559 法國加爾文派《巴黎信條》(Gallican Confession / Confessio Gallicana) 啟發但獨立發展
- 「合一信經三聯」(Three Forms of Unity)：比利時信條 + 海德堡要理問答 + 多德雷赫特信條
- 接受傳統：荷蘭改革宗 / 比利時改革宗 / 美國 CRC、RCA / 南非 NGK / 部分長老宗
- 中譯來源：Denzinger 第 43 版（光啟 2013）僅收 DH 5575-5590 摘錄`,
  related: ['augsburg-confession', 'anglican-articles', 'lima-bem'],
}
