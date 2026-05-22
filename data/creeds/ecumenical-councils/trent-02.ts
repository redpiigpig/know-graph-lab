import type { Creed } from '../types'

export const trent02: Creed = {
  slug: 'trent-02',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S02',
  councilDocOrder: 2,
  order: 1902,
  nameZh: '第 2 會期 ─ 與會者生活法度令',
  nameEn: 'Session 2 — Decree on the Manner of Living and Other Matters',
  year: 1546,
  location: '北義特利騰／波隆那（特利騰大公會議第 2 會期）',
  topic: '規範與會教長的個人靈修生活、節制飲食、勤領聖事、避免世俗喧鬧；為大公會議奠定屬靈氛圍',
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
      textKey: 'trent-02-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-02-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-02-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第二會期僅頒一份紀律令《與會者生活法度令》(Decree touching the manner of living and other matters)，要求所有與會教長在參與大公會議期間以身作則：勤誦日課、頻領聖事、節制飲食、安撫與其他教長之間的歧見，並以基督徒謙遜的態度共商議題。此令為後續會期奠定屬靈基調，亦為當時普遍譴責的「教廷奢靡」風氣作出自我反省。`,
  notes: `- 頒佈日期：1546-01-07
- 會期類別：第 2 會期 / Session 2 (第一期 1545-49)
- 主議題：規範與會教長的個人靈修生活、節制飲食、勤領聖事、避免世俗喧鬧；為大公會議奠定屬靈氛圍
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-01',
    'trent-03',
    'trent-04',
  ],
}
