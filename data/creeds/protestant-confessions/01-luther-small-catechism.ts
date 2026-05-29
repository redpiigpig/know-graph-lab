import type { Creed } from '../types'

export const lutherSmallCatechism: Creed = {
  slug: 'luther-small-catechism',
  category: 'protestant-confession',
  order: 3001,
  nameZh: '路德《小本基督徒要學》（小教理問答）',
  nameEn: 'Luther — Small Catechism',
  nameLat: 'Catechismus Minor',
  year: 1529,
  location: '維騰堡',
  topic: '十誡 / 信經 / 主禱文 / 聖洗 / 聖餐 / 認罪 — 信義宗信仰要理問答；以家長日常教導兒女為對象',
  authors: ['Martin Luther (馬丁路德)'],
  acceptedBy: ['lutheran', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（Denzinger DH 5500-5502 摘錄）',
      text: '',
      textKey: 'luther-small-catechism-chinese',
      source: '《公教會之信仰與倫理教義選集》（Denzinger 中譯）— 光啟文化 2013 / ISBN 9789575467418，附錄五。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'de',
      label: '德文原文（待補）',
      text: '',
      placeholder: true,
      source: 'WA 30/I; Bekenntnisschriften der evangelisch-lutherischen Kirche (BSLK).',
    },
    {
      lang: 'en',
      label: 'English translation (待補)',
      text: '',
      placeholder: true,
      source: 'Book of Concord, Kolb-Wengert edition (2000).',
    },
  ],
  summaryZh: `路德於 1529 年為信徒家庭日常教導所寫的簡明要理問答。以「家長對子女」一問一答的方式編排十誡、信經（含使徒信經）、主禱文、聖洗、聖餐、認罪悔改六大主題，是信義宗宗教改革時期最具影響力的教理教材之一。

《小本基督徒要學》與同年完成的《大本基督徒要學》(Large Catechism) 並列為信義宗 Confessio Augustana 之前的核心要理文件，至今仍是路德宗教會堅信禮教程的標準教材。`,
  notes: `- 1529 年於維騰堡編成，先發行墻報版（plakatform）後改裝訂成手冊
- 影響大本要理（同年）→ 1530 奧斯堡信條 → 1580 協同書 (Book of Concord)
- 中譯來源：Denzinger 第 43 版（光啟 2013）僅收 DH 5500-5502 三段摘錄，全本中譯需參考信義宗禮儀本
- 接受傳統：信義宗全體；改革宗與聖公宗也部分採用（作為教義基準參考）
- 與大本要理 (Large Catechism) 互補：大本為牧者準備講道用、小本為家長日常教導用`,
  related: ['augsburg-confession'],
}
