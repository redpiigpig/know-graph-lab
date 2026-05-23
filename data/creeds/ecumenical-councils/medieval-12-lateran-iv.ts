import type { Creed } from '../types'

export const medieval12: Creed = {
  slug: 'medieval-12-lateran-iv',
  category: 'ecumenical-council',
  councilNo: 12,
  order: 812,
  nameZh: '第四次拉特朗大公會議',
  nameEn: 'Fourth Council of the Lateran',
  nameLat: 'Concilium Lateranense IV',
  year: 1215,
  location: '羅馬‧拉特朗聖若望大殿',
  topic: '中世紀最重要單一大公會議：正式定義變質說 transubstantiatio／要求信徒每年告解＋復活節領聖體（canon 21 Omnis utriusque sexus）／規範宗教裁判所／呼籲第五次十字軍／譴責 Joachim of Fiore + Amalric of Bena',
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
      textKey: 'medieval-12-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-12-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-12-latin',
      source: 'Documenta Catholica Omnia, 1215-1215,_Concilium_Lateranense_IIII,_Documenta,_LT.pdf — 70 canons 含變質說 transubstantiatio + Omnis utriusque sexus',
    },
  ],
  summaryZh: `第四次拉特朗大公會議於 1215 年 11 月由教宗依諾增爵三世 (Innocent III) 召開，是中世紀最具規模與決定性的大公會議 — 與會超過 1200 位教會代表（含主教、隱修院長、教座代表、各國皇族特使），歷時 3 週通過 70 條 canons（後稱 Constitutiones），涵蓋幾乎所有 13 世紀拉丁西方教會生活面向。

核心神學決議：(1) **canon 1**：正式定義「變質說」(transubstantiatio) — 餅酒之實體於祝聖時變為基督體血；天主教首次以這個術語定義聖體教義；(2) 譴責 Cathar 二元論與 Albigensians 異端；(3) 譴責 Joachim of Fiore 三位一體論之錯誤 (canon 2)；(4) 譴責 Amalric of Bena 之泛神論。

核心紀律決議：(1) **canon 21《Omnis utriusque sexus》**：要求所有達理智年齡之信徒每年至少向本堂神父告解一次、復活節期間領聖體 — 是中世紀以降天主教個人告解實踐之奠基；(2) canon 18：禁神職人員參與血腥審判 (ordeal by fire/water)，加速世俗司法取代教會司法；(3) canon 22-24：規範主教選任、神品授職；(4) canon 67-70：對猶太人之歧視性規定 — 禁猶太人擔任公職、要求穿戴標誌性服裝（後世「黃星」前身）。

會議同時呼籲第五次十字軍 (1217-21) — 1213 年依諾增爵三世已透過教廷文件 Vineam Domini 為之鋪路。本次會議為中世紀教會權勢之巔峰時刻；其神學與紀律決議影響天主教至今。`,
  notes: `- 通過：1215 年 11 月 11-30 日於拉特朗聖若望大殿
- 與會：約 412 主教、800 隱修院長／教座代表 + 各國皇族特使 — 中世紀規模最大會議
- 召集者：教宗依諾增爵三世（中世紀最有權勢教宗之一）
- 70 條 canons（Constitutiones）
- **canon 1**：transubstantiatio（變質說）首次官方定義
- **canon 21 Omnis utriusque sexus**：年告解 + 復活節領聖體之奠基
- canon 67-70：歧視性對猶太人規定（黃色標誌前身）
- 呼籲第五次十字軍
- 中世紀教會權勢巔峰
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-10-lateran-ii',
    'medieval-11-lateran-iii',
    'medieval-13-lyon-i',
    'medieval-14-lyon-ii',
  ],
}
