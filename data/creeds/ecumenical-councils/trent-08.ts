import type { Creed } from '../types'

export const trent08: Creed = {
  slug: 'trent-08',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S08',
  councilDocOrder: 8,
  order: 1908,
  nameZh: '第 8 會期 ─ 會議遷移令',
  nameEn: 'Session 8 — Decree on the Translation of the Council',
  year: 1547,
  location: '北義特利騰／波隆那（特利騰大公會議第 8 會期）',
  topic: '因特利騰爆發疫情，會議移至教廷國境內波隆那 (Bologna)；與會教長分裂，神羅皇帝查理五世強烈反對',
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
      textKey: 'trent-08-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-08-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-08-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `因特利騰城內爆發傳染病疫情（可能為斑疹傷寒），第八會期投票表決將會議移至教廷國境內的波隆那 (Bologna)。然此舉引發與會教長嚴重分裂：神聖羅馬帝國皇帝查理五世 (Charles V) 強烈反對 — 因 Bologna 為教廷直轄、會議移此將完全脫離帝國影響；德意志教長拒絕同行、留守特利騰。會議實質陷入兩派並行狀態，使後續會期形同癱瘓。此會期為特利騰首度長期休會之開端。`,
  notes: `- 頒佈日期：1547-03-11
- 會期類別：第 8 會期 / Session 8 (第一期 1545-49)
- 主議題：因特利騰爆發疫情，會議移至教廷國境內波隆那 (Bologna)；與會教長分裂，神羅皇帝查理五世強烈反對
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-06',
    'trent-07',
    'trent-09',
    'trent-10',
  ],
}
