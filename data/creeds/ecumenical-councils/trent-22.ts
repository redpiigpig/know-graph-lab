import type { Creed } from '../types'

export const trent22: Creed = {
  slug: 'trent-22',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S22',
  councilDocOrder: 22,
  order: 1922,
  nameZh: '第 22 會期 ─ 彌撒聖祭令',
  nameEn: 'Session 22 — Doctrine on the Sacrifice of the Mass + Decree on Reformation',
  year: 1562,
  location: '北義特利騰／波隆那（特利騰大公會議第 22 會期）',
  topic: '定義彌撒為「真正、本義的祭祀」(verum et proprium sacrificium)；十架祭與彌撒祭為「同一祭祀」(unum et idem sacrificium)；為亡者獻彌撒有功效',
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
      textKey: 'trent-22-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-22-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-22-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第二十二會期頒《論彌撒聖祭令》9 章 + 9 條 canons：(1) 彌撒為「真正、本義的祭祀」(verum et proprium sacrificium)，非僅紀念或感謝祭 (駁路德、加爾文)；(2) 十架犧牲 (cruentum) 與彌撒中之祭獻 (incruentum, 不流血) 為「同一犧牲」(unum et idem sacrificium)，唯施行方式不同 — 司鐸代基督施行；(3) 彌撒為「贖罪祭」(propitiatoria) 對生者與亡者皆有功效；(4) 私人彌撒 (missa privata, 即僅司鐸領聖體) 合法、有益；(5) 拉丁禮 (lingua latina) 為彌撒禮儀語言之合宜選擇 — 但同時譴責任何「禁止以本地語向會眾解釋禮儀」之主張。同會期之改革令規範彌撒禮儀施行、神職人員生活、教廷財政。`,
  notes: `- 頒佈日期：1562-09-17
- 會期類別：第 22 會期 / Session 22 (第三期 1562-63)
- 主議題：定義彌撒為「真正、本義的祭祀」(verum et proprium sacrificium)；十架祭與彌撒祭為「同一祭祀」(unum et idem sacrificium)；為亡者獻彌撒有功效
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-20',
    'trent-21',
    'trent-23',
    'trent-24',
  ],
}
