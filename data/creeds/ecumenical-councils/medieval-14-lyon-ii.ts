import type { Creed } from '../types'

export const medieval14: Creed = {
  slug: 'medieval-14-lyon-ii',
  category: 'ecumenical-council',
  councilNo: 14,
  order: 814,
  nameZh: '第二次里昂大公會議',
  nameEn: 'Second Council of Lyons',
  nameLat: 'Concilium Lugdunense II',
  year: 1274,
  location: '里昂‧聖若望大殿',
  topic: '短暫東西方教會合一（Latin-Greek Union of Lyon, 後遭東方拒絕）／確立 conclave 教宗選舉法（Ubi periculum）／批准托缽修會 Mendicant Orders 永久存在',
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
      textKey: 'medieval-14-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-14-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-14-latin',
      source: 'Documenta Catholica Omnia, 1274-1274,_Concilium_Lugdunense_II,_Documenta,_LT.doc — 31 canons 含 Union of Lyon + Ubi periculum conclave 制度',
    },
  ],
  summaryZh: `第二次里昂大公會議於 1274 年 5 月由教宗額我略十世 (Gregory X) 召開於里昂，三大議題：東西教會合一、收復聖地、教會內部改革。

**東西教會合一 (Union of Lyon, 1274)**：因東羅馬皇帝米該爾八世 (Michael VIII Palaiologos) 面臨拉丁人 Charles of Anjou 入侵威脅，主動派希臘代表赴會議。會議第四場 (1274-07-06) 希臘代表正式接受 filioque、煉獄、教宗首席權三項拉丁教義，宣告東西方教會合一。然此合一遭東方教會強烈反對 — 君士坦丁堡牧首 Joseph I 拒絕、米該爾兒子 Andronicus II 即位 (1282) 後正式撤銷合一。本次合一僅維持 8 年，是中世紀東西方修好的一次失敗嘗試（下一次更深入嘗試為 1439 年佛羅倫斯大公會議）。

**Ubi periculum 憲章**：規範教宗選舉「conclave」制度 — 樞機團於前任教宗去世後 10 日內進入閉鎖式選舉，與外界隔絕、食物逐日縮減、無人離開，直至 2/3 多數選出新教宗。此規定源於 1268-71 年教宗 Clement IV 去世後樞機團爭吵 33 個月未能選出繼任者 — 維泰博 (Viterbo) 市民拆掉樞機們所住宮殿屋頂、限制食物供應方迫其選出 Gregory X。本制度沿用至今（細節經多次調整）。

**Mendicant Orders 永久確認**：方濟各會、道明會等托缽修會經此會議獲得正式承認，駁斥當時學界對托缽修會合法性之質疑（William of Saint-Amour 等）。`,
  notes: `- 通過：1274 年 5 月 7 日 - 7 月 17 日於里昂
- 與會：約 500 餘主教 + 1000 餘其他與會者（含希臘代表團）
- 召集者：教宗額我略十世
- **Union of Lyon 1274**：東西教會短暫合一（8 年後東方撤銷）
- **Ubi periculum**：conclave 教宗選舉法奠基
- 方濟會、道明會等托缽修會永久確認
- St. Thomas Aquinas 受邀赴會途中去世 (1274-03-07)；St. Bonaventure 於會議期間去世 (1274-07-15)
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-12-lateran-iv',
    'medieval-13-lyon-i',
    'medieval-15-vienne',
    'medieval-16-constance',
  ],
}
