import type { Creed } from '../types'

export const medieval16: Creed = {
  slug: 'medieval-16-constance',
  category: 'ecumenical-council',
  councilNo: 16,
  order: 816,
  nameZh: '康斯坦茨大公會議',
  nameEn: 'Council of Constance',
  nameLat: 'Concilium Constantiense',
  year: 1414,
  location: '康斯坦茨（神聖羅馬帝國‧今德國 Konstanz）',
  topic: '結束西方大分裂（Western Schism 1378-1417，三位對立教宗並存）／處死 Jan Hus 揚‧胡斯（1415-07-06 火刑）／追溯譴責 Wycliffe 並掘墓焚屍／頒佈 Haec Sancta 公會議至上主義（後遭駁斥）',
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
      textKey: 'medieval-16-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-16-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'medieval-16-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com Latin corpus',
    },
  ],
  summaryZh: `康斯坦茨大公會議於 1414-1418 年由神聖羅馬皇帝 Sigismund 主導召集，目的為終結 1378 年以來的西方大分裂 (Western Schism) — 期間有三位並立教宗：Gregory XII (羅馬系)、Benedict XIII (亞維儂系)、John XXIII (比薩系，1409 年企圖整合分裂時設立)。三位皆無法獲得普世承認，西方教會陷入治理危機 40 年。

**結束大分裂的方式**：(1) 罷免 John XXIII (1415-05-29) — 罪名為聖職買賣、淫亂等；(2) 接受 Gregory XII 之自願辭職 (1415-07-04)；(3) 罷免拒絕辭職的 Benedict XIII (1417-07-26)；(4) 選出 Martin V (1417-11-11) — 西方教會重新統一。

**Haec Sancta 法令 (1415-04-06)**：宣告大公會議乃源自基督、合法召開後享有至高權威 — 即使教宗亦需服從。此「公會議至上主義」(Conciliarism) 原本是當時解決分裂之必要手段，但日後遭教宗 Eugene IV 與 Lateran V (1512-17) 駁斥；至 Vatican I (1870) Pastor Aeternus 正式確立教宗首席權後完全推翻。

**處死 Jan Hus**：捷克改革家揚‧胡斯 (Jan Hus, c.1369-1415) 在皇帝 Sigismund 給予的「安全通行證」(salvus conductus) 下到會議辯護其神學立場（反聖職買賣、強調聖經權威、贊同 Wycliffe 之部分觀點），但被會議判為異端，於 1415-07-06 火刑處死。次年 1416 同樣處死其同伴 Jerome of Prague。胡斯之死引發捷克「胡斯戰爭」(1419-34) 並成為一個世紀後路德宗教改革之先驅事件。

**追溯譴責 Wycliffe**：1415 年 5 月，會議追溯判英國神學家 John Wycliffe (c.1320-1384) 為異端 — 因其早於 30 年前去世、無法生前處刑，會議命令掘墓焚屍 (1428 年由 Lincoln 主教執行)、骨灰撒入 River Swift。

本會議對禮儀亦有重大決議：禁信徒領聖爵 (chalice) — 重申拉特朗 IV 領聖體規定但保留聖爵僅予司鐸；此規定後成為改教家攻擊重點，特利騰 Session 21 (1562) 再度確認。`,
  notes: `- 通過：1414-11-05 至 1418-04-22 於康斯坦茨
- 與會：約 600 主教 + 數千其他與會者；空前規模
- 召集者：神聖羅馬皇帝 Sigismund (+教宗 John XXIII)
- **結束西方大分裂** (1378-1417) — 三位對立教宗皆解任，選出 Martin V
- **處死 Jan Hus** (1415-07-06) — 引發胡斯戰爭，宗教改革先聲
- 追溯譴責 Wycliffe 掘墓焚屍
- **Haec Sancta 公會議至上主義** — 後遭 Vatican I 推翻
- 禁信徒領聖爵
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-14-lyon-ii',
    'medieval-15-vienne',
    'medieval-17-basel-ferrara-florence',
    'medieval-18-lateran-v',
  ],
}
