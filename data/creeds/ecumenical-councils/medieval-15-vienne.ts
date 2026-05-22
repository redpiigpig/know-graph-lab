import type { Creed } from '../types'

export const medieval15: Creed = {
  slug: 'medieval-15-vienne',
  category: 'ecumenical-council',
  councilNo: 15,
  order: 815,
  nameZh: '維埃納大公會議',
  nameEn: 'Council of Vienne',
  nameLat: 'Concilium Viennense',
  year: 1311,
  location: '維埃納（法國‧Vienne）',
  topic: '正式廢除聖殿騎士團（Knights Templar）／譴責 Beguines / Beghards 半修道運動／結束 Olivi 神貧爭論',
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
      textKey: 'medieval-15-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-15-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'medieval-15-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com Latin corpus',
    },
  ],
  summaryZh: `維埃納大公會議於 1311-12 年由教宗 Clement V 召開於法國維埃納，是「亞維儂教廷」(Avignon Papacy, 1309-77) 時期的第一次大公會議。

會議最具歷史影響的決議是**正式廢除聖殿騎士團 (Knights Templar)**：法王腓力四世 (Philip IV the Fair) 自 1307 年大規模逮捕、酷刑、處決聖殿騎士團員 — 動機既包含對其積累財富之覬覦、亦含對其過大政治權勢之恐懼。教宗 Clement V 在法王強大壓力下，於 1312-03-22 頒「Vox in excelso」詔令永久廢除聖殿騎士團（不以「異端」名義，但以「不再可恢復名譽」為由）；其財產轉予醫院騎士團 (Hospitallers)。1314 年最後一任總團長 Jacques de Molay 被火刑處死。

會議其他決議：(1) 譴責 Beguines / Beghards 半修道運動 — 不發隱修誓言但獨身共居之團體，因其遊離於教會結構之外被視為威脅；(2) 結束方濟各會內 Petrus Iohannis Olivi（彼得‧若望‧奧利維）所引發的「神貧爭論」(usus pauper)：基督與宗徒究竟「絕對神貧」抑或「使用權但無所有權」— 此爭論其後被 John XXII 教宗 1323 年 Cum inter nonnullos 詔令終結；(3) 譴責 Marguerite Porete 之《Mirror of Simple Souls》(她已於 1310 年被火刑處死)；(4) 規範東方語言教學 — 巴黎、波隆那、牛津、薩拉曼卡四所大學應設希臘文、希伯來文、阿拉伯文、迦勒底文講座，為傳教與聖經研究服務（落實有限）。`,
  notes: `- 通過：1311-10-16 至 1312-05-06 於維埃納
- 與會：約 300 餘主教（法籍多數，反映亞維儂教廷之法國化）
- 召集者：教宗 Clement V（亞維儂教廷時期）
- **永久廢除聖殿騎士團** (Vox in excelso, 1312-03-22)
- 譴責 Beguines / Beghards 半修道團體
- 結束 Olivi 神貧爭論（後再爆發於 1322-23）
- 規範四大學東方語言教學（執行有限）
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-13-lyon-i',
    'medieval-14-lyon-ii',
    'medieval-16-constance',
    'medieval-17-basel-ferrara-florence',
  ],
}
