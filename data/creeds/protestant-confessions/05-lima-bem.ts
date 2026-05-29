import type { Creed } from '../types'

export const limaBem: Creed = {
  slug: 'lima-bem',
  category: 'ecumenical-dialogue',
  order: 3005,
  nameZh: '利馬文件 — 受洗、聖餐、職事 (BEM)',
  nameEn: 'Baptism, Eucharist and Ministry (Lima Document)',
  nameLat: '—',
  year: 1982,
  location: '秘魯‧利馬（普世教會協會 Faith and Order Commission 全會）',
  topic: '普世教會協會 (WCC) 信仰與秩序委員會 1982 年發表的最重要 ecumenical 文件；分「受洗」「聖餐」「職事」三大部分，是 20 世紀普世合一運動的里程碑',
  authors: [
    '普世教會協會 (WCC) 信仰與秩序委員會 (Faith and Order Commission)',
    '120 位來自天主教、東正教、東方東正教、聖公宗、信義宗、改革宗、衛理宗、浸信宗、五旬節派等的神學家參與',
  ],
  acceptedBy: ['catholic', 'orthodox', 'protestant', 'anglican', 'lutheran', 'reformed', 'methodist', 'baptist'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（Denzinger DH 5591-5701 摘錄）',
      text: '',
      textKey: 'lima-bem-chinese',
      source: '《公教會之信仰與倫理教義選集》（Denzinger 中譯）— 光啟文化 2013 / ISBN 9789575467418，附錄五。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'English original (Faith and Order Paper No. 111)',
      text: '',
      placeholder: true,
      source: 'WCC Faith and Order Paper No. 111 (1982). Available at oikoumene.org.',
    },
    {
      lang: 'fr',
      label: 'Baptême, Eucharistie, Ministère (法文版，待補)',
      text: '',
      placeholder: true,
      source: 'Conseil œcuménique des Églises, Genève.',
    },
  ],
  summaryZh: `1982 年 1 月於秘魯利馬召開的普世教會協會 (WCC) 信仰與秩序委員會 (Faith and Order Commission) 全會通過的劃時代文件。120 位來自天主教（觀察員身份，因天主教非 WCC 正式會員）、東正教、東方東正教、聖公宗、信義宗、改革宗、衛理宗、浸信宗、五旬節派等的神學家參與起草。

文件分三大部分：
- **B (Baptism, 受洗)**：受洗的意義、神學基礎、嬰兒洗 vs 信徒洗 (Believer's Baptism) 兩種傳統的對話；
- **E (Eucharist, 聖餐)**：聖餐論——基督實在臨在、聖餐作為紀念 (anamnesis)、聖神祈求 (epiclesis)、聖餐作為團體之預嘗；
- **M (Ministry, 職事)**：教會職分——使徒統緒 (apostolic succession)、主教‧長老‧執事的三重職分、按手禮、女性按立的差異。

利馬文件是 20 世紀普世合一運動 (ecumenical movement) 最具影響力的成果之一，被 186 個 WCC 會員教會與天主教、五旬節派、靈恩派等非會員教會分別回應、評估、納入後續神學對話。它的影響延伸到《里昂宣言》《奧斯堡聯合宣言》(Joint Declaration on the Doctrine of Justification, 1999) 等後續普世合一文件。`,
  notes: `- 1982-01-12 利馬全會 (Lima Plenary) 通過 (WCC Faith and Order Paper No. 111)
- 別稱 BEM 或「Lima Text」(利馬文本)
- 1982 年同年衍生 Lima Liturgy（利馬禮儀），首次跨宗派 ecumenical 共融禮儀範本
- 1986-1990 WCC 蒐集會員教會回應，編成《Churches Respond to BEM》6 卷
- 影響後續：奧斯堡聯合宣言 (1999 天主教-信義宗)、A Common Mission (1992)、Charta Oecumenica (2001 歐洲)、Lund Statement (2016)
- 中譯來源：Denzinger 第 43 版（光啟 2013）僅收 DH 5591-5701 摘錄（111 條中譯不全）
- 全文中譯：可參考香港基督教協進會《利馬聖洗 ‧ 聖餐 ‧ 職事文件》或台灣神學院出版品`,
  related: ['augsburg-confession', 'reformed-belgic'],
}
