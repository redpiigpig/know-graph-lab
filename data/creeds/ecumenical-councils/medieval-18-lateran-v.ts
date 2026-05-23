import type { Creed } from '../types'

export const medieval18: Creed = {
  slug: 'medieval-18-lateran-v',
  category: 'ecumenical-council',
  councilNo: 18,
  order: 818,
  nameZh: '第五次拉特朗大公會議',
  nameEn: 'Fifth Council of the Lateran',
  nameLat: 'Concilium Lateranense V',
  year: 1512,
  location: '羅馬‧拉特朗聖若望大殿',
  topic: 'Julius II / Leo X 召開以回應 Pisan schism 對立會議／重申教宗權威壓制 conciliarism／譴責 Pomponazzi 否認靈魂不滅論／為十字軍籌資 — 結束於 1517-03-16，僅 7 個月後路德張貼 95 條論綱',
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
      textKey: 'medieval-18-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-18-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-18-latin',
      source: 'Documenta Catholica Omnia, 1512-1512,_Concilium_Lateranum_V,_Documenta_Omnia,_LT.pdf — 駁 Conciliarism 重申教宗權威；1517 閉幕後 7 個月 Luther 95 條',
    },
  ],
  summaryZh: `第五次拉特朗大公會議於 1512-1517 年由教宗 Julius II 召開、Leo X 結束。本次會議的直接動機為對抗 1511 年由法王路易十二支持、5 位反 Julius II 樞機在比薩 (Pisa) 召開的「對立會議」(Conciliabulum Pisanum) — 試圖以公會議至上主義罷黜教宗。Julius II 召開拉特朗 V 作為正統公會議反制；比薩派最終於 1513 年解散。

核心決議：(1) **教宗權威 vs Conciliarism**：1516-12-19 頒佈「Pastor Aeternus」(同名但與 1870 不同) 宣告教宗權威高於大公會議，正式駁斥 Constance 之 Haec Sancta；此為 1870 Vatican I 教宗首席權的中世紀先聲；(2) **靈魂不滅論**：1513-12-19 頒「Apostolici Regiminis」譴責 Pietro Pomponazzi（帕多瓦哲學家，將於 1516 出版《De immortalitate animae》）以亞里斯多德哲學論證個人靈魂非不朽之主張 — 會議宣告靈魂不朽乃可由理性證明之教義；(3) 廢除 1438 法國《Pragmatic Sanction of Bourges》— 該文件曾賦予法國教會獨立於羅馬之 Gallican 自治權；(4) 規範主教選任、禁神職人員兼任多職、限制聖物販售；(5) 為十字軍籌資（教宗 Leo X 後續以贖罪券大規模籌款計劃即源於此）。

**歷史諷刺**：會議於 1517-03-16 閉幕；同年 1517-10-31 馬丁路德於威登堡張貼《95 條論綱》— 引發宗教改革。本會議雖力圖鞏固教宗權威、推進教會改革，但其改革決議執行不力（特別是聖職買賣與兼任問題），未能阻止 30 年後改教運動席捲歐洲；其改革議程的失敗成為 Trent (1545-63) 啟動的直接動因。`,
  notes: `- 通過：1512-05-03 至 1517-03-16 於拉特朗聖若望大殿
- 與會：以義大利主教為主；法籍主教受 Louis XII 抵制初期缺席
- 召集者：教宗 Julius II → Leo X
- 12 場 sessions
- **Pastor Aeternus 1516** (與 1870 同名)：正式駁斥 Constance Haec Sancta，重申教宗權威高於公會議
- **Apostolici Regiminis 1513**：譴責 Pomponazzi 否認靈魂不滅
- 廢除 1438《Pragmatic Sanction of Bourges》— 削減法國 Gallican 自治
- 1517-03-16 閉幕；同年 1517-10-31 路德《95 條論綱》— 改教運動爆發
- 本會議改革執行不力為 Trent (1545-63) 啟動之直接背景
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-16-constance',
    'medieval-17-basel-ferrara-florence',
  ],
}
