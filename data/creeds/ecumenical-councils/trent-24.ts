import type { Creed } from '../types'

export const trent24: Creed = {
  slug: 'trent-24',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S24',
  councilDocOrder: 24,
  order: 1924,
  nameZh: '第 24 會期 ─ 婚姻令',
  nameEn: 'Session 24 — Doctrine on the Sacrament of Matrimony + Decree on Reformation',
  year: 1563,
  location: '北義特利騰／波隆那（特利騰大公會議第 24 會期）',
  topic: '婚姻為基督所立之聖事；獨身、童貞較婚姻更完美；秘密婚姻 (clandestine marriage) 自此無效 — 須有堂區司鐸與兩證人方為有效（Tametsi 詔令）',
  authors: [
    '教宗保祿三世／儒略三世／庇護四世（依會期）頒佈',
    '教廷特使主持（Del Monte／Cervini／Pole／Morone 等樞機）',
    '神學委員會審議；與會教長表決通過',
  ],
  acceptedBy: ['catholic'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 對 Trent 無中文官方版）',
      text: '',
      textKey: 'trent-24-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-24-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-24-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第二十四會期頒《論婚姻聖事令》12 條 canons + 著名的《Tametsi 詔令》：(1) 婚姻為基督所立之聖事，賦予恩寵；唯主教或經主教允許之司鐸為婚禮主持 (witness)；(2) 駁路德「婚姻非聖事、僅為公民契約」之主張；(3) 教會擁有訂立婚姻障礙、廢除無效婚姻之權柄；(4) 確認獨身、童貞 (caelibatus, virginitas) 較婚姻更完美 — 駁路德「神父應結婚」、「童貞較婚姻不更善」之主張；(5)《Tametsi 詔令》(decree of Tametsi) 之歷史里程碑：自此「秘密婚姻」(clandestine marriage, 即無證人之婚誓) 自動無效 — 須於本堂司鐂前並有至少兩證人見證，方為有效婚姻 — 此為西方婚姻法的根本性改革，終結中世紀以來秘密婚姻之亂象。同會期之改革令規範主教選任、教省會議、教廷財政。`,
  notes: `- 頒佈日期：1563-11-11
- 會期類別：第 24 會期 / Session 24 (第三期 1562-63)
- 主議題：婚姻為基督所立之聖事；獨身、童貞較婚姻更完美；秘密婚姻 (clandestine marriage) 自此無效 — 須有堂區司鐸與兩證人方為有效（Tametsi 詔令）
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-22',
    'trent-23',
    'trent-25',
  ],
}
