import type { Creed } from '../types'

export const augsburgConfession: Creed = {
  slug: 'augsburg-confession',
  category: 'protestant-confession',
  order: 3002,
  nameZh: '奧斯堡信條',
  nameEn: 'Augsburg Confession',
  nameLat: 'Confessio Augustana',
  year: 1530,
  location: '奧斯堡（神聖羅馬帝國國會）',
  topic: '信義宗向皇帝 Charles V 提出的官方信仰宣言，28 條，分「信仰要道」(1-21) 與「弊端糾正」(22-28)；為信義宗最核心信仰文件',
  authors: [
    'Philip Melanchthon（執筆）',
    'Martin Luther（背後審定）',
    '七位德意志諸侯與兩座自由城聯署',
  ],
  acceptedBy: ['lutheran', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（Denzinger DH 5503-5523 摘錄）',
      text: '',
      textKey: 'augsburg-confession-chinese',
      source: '《公教會之信仰與倫理教義選集》（Denzinger 中譯）— 光啟文化 2013 / ISBN 9789575467418，附錄五。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'lat',
      label: '拉丁原文（CA Invariata 1530，待補）',
      text: '',
      placeholder: true,
      source: 'Bekenntnisschriften der evangelisch-lutherischen Kirche (BSLK), Vandenhoeck & Ruprecht.',
    },
    {
      lang: 'de',
      label: '德文版（同步原文，待補）',
      text: '',
      placeholder: true,
      source: 'BSLK 德文版；Melanchthon 同時起草拉丁／德文兩版本。',
    },
    {
      lang: 'en',
      label: 'English translation (待補)',
      text: '',
      placeholder: true,
      source: 'Book of Concord, Kolb-Wengert edition (2000).',
    },
  ],
  summaryZh: `1530 年 6 月 25 日由 Melanchthon 執筆，七位德意志諸侯與兩座自由城（紐倫堡‧羅伊特林根）聯署在奧斯堡帝國會議上正式宣讀，呈交神聖羅馬帝國皇帝查理五世。全文 28 條，分「信仰要道」(Articles 1-21，闡述路德派教義) 與「弊端糾正」(Articles 22-28，批判中世紀末期天主教會實踐) 兩部分。

奧斯堡信條是信義宗最重要的信仰宣言，與《小教理問答》《大教理問答》《信義宗條款》《史馬加登條款》《和睦信條》等共組 1580 年《和睦書》(Book of Concord) 的核心文件。本信條成為日後信義宗教會 (Lutheran Church) 在全球的信仰共同基礎，並深刻影響後續所有改革宗、聖公宗信條的書寫格式。`,
  notes: `- 1530-06-25 於奧斯堡帝國會議公開宣讀，由皇帝 Charles V 親自聆聽
- Invariata (1530) vs. Variata (1540)：後者為 Melanchthon 於 1540 修訂以接近 Calvin 立場（特別在聖餐論）— 路德派內部對 Variata 看法分歧
- 28 條：第 1-21 條為信仰陳述（聖三、原罪、稱義、教會、聖事、回頭、自由意志等）；第 22-28 條為對天主教實踐的批判（兩種形體聖餐、神職婚姻、彌撒、認罪、修會誓願等）
- 接受傳統：信義宗全體；歷史上改革宗也曾簽署 Variata 版本
- 中譯來源：Denzinger 第 43 版（光啟 2013）僅收 DH 5503-5523 摘錄
- 1580《和睦書》(Konkordienbuch / Book of Concord) 將奧斯堡列為首要文件`,
  related: ['luther-small-catechism', 'anglican-articles'],
}
