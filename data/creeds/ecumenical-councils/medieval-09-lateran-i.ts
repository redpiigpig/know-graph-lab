import type { Creed } from '../types'

export const medieval09: Creed = {
  slug: 'medieval-09-lateran-i',
  category: 'ecumenical-council',
  councilNo: 9,
  order: 809,
  nameZh: '第一次拉特朗大公會議',
  nameEn: 'First Council of the Lateran',
  nameLat: 'Concilium Lateranense I',
  year: 1123,
  location: '羅馬‧拉特朗聖若望大殿',
  topic: '批准 1122 年《沃姆斯協定》(Concordat of Worms)，正式結束「敘任權鬥爭」(Investiture Controversy) — 確立教會獨立任命主教權；西方第一次大公會議',
  authors: [
    '召集教宗（依各會期詳見 notes）',
    '與會教長表決通過 canons',
  ],
  acceptedBy: ['catholic'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 對中世紀公會議無中文版）',
      text: '',
      textKey: 'medieval-09-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-09-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-09-latin',
      source: 'Documenta Catholica Omnia, 1123-1123,_Concilium_Lateranum_I,_Documenta,_LT.doc — 22 canons 沃姆斯協定批准',
    },
  ],
  summaryZh: `第一次拉特朗大公會議於 1123 年由教宗加里斯都二世 (Callixtus II) 召開於羅馬拉特朗聖若望大殿。**這是天主教歷史上第一次完全由西方教會召開、不邀請東方主教的大公會議**，反映 1054 大分裂後西方教會獨立發展之新階段。

會議核心成就為正式批准 1122 年《沃姆斯協定》(Concordatum Wormatiense)，結束自 1075 年教宗額我略七世以來與神聖羅馬帝國皇帝亨利四世、亨利五世的「敘任權鬥爭」(Investiture Controversy)。協定確立：(1) 主教與隱修院長之精神職權象徵（牧杖與指環）由教會授予；(2) 世俗權威（皇帝）僅可在主教當選後以權杖賦予土地俸祿；(3) 主教選舉於教會內部進行，皇帝不得干預。此協定為日後西方政教分權的奠基模式。

會議同時頒佈 22 條 canons 規範：嚴禁聖職買賣 (simony)、強化神職人員獨身要求、規範十字軍贖罪券、譴責內戰中的偽鑄幣與搶劫聖物。`,
  notes: `- 通過：1123 年 3-4 月於拉特朗聖若望大殿
- 與會：教宗、樞機、約 300 餘西方主教
- 召集者：教宗加里斯都二世
- 22 條 canons
- **西方第一次大公會議** — 1054 大分裂後不再邀請東方主教
- 核心：批准 1122《沃姆斯協定》結束敘任權之爭
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-08-constantinople-iv',
    'medieval-10-lateran-ii',
    'medieval-11-lateran-iii',
  ],
}
