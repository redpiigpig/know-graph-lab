import type { Creed } from '../types'

export const medieval13: Creed = {
  slug: 'medieval-13-lyon-i',
  category: 'ecumenical-council',
  councilNo: 13,
  order: 813,
  nameZh: '第一次里昂大公會議',
  nameEn: 'First Council of Lyons',
  nameLat: 'Concilium Lugdunense I',
  year: 1245,
  location: '里昂‧聖儒斯特大殿',
  topic: '教宗依諾增爵四世罷黜神聖羅馬皇帝腓特烈二世（Frederick II Hohenstaufen）／呼籲第七次十字軍／處理蒙古入侵威脅',
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
      textKey: 'medieval-13-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-13-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-13-latin',
      source: 'Documenta Catholica Omnia, 1245-1245,_Concilium_Lugdunense_I,_Documenta,_LT.doc — 22 canons 罷黜 Frederick II + 蒙古應對',
    },
  ],
  summaryZh: `第一次里昂大公會議於 1245 年 6 月由教宗依諾增爵四世 (Innocent IV) 召開於法蘭西里昂，因羅馬處於皇帝腓特烈二世 (Frederick II Hohenstaufen) 軍事威脅下，教宗逃亡至里昂避難。

會議最具戲劇性的決議是**正式罷黜神聖羅馬皇帝腓特烈二世**：教宗判其為「異端、瀆神、傷害教會、毀約之人」(haereticus, sacrilegus, ecclesiae offensor, periurus)，宣告解除其臣民效忠誓言、剝奪一切權威。此舉是中世紀教權-王權衝突之巔峰時刻；雖腓特烈拒不退位（1250 年去世），但霍亨斯陶芬王朝隨之衰落、北義大利城邦走向獨立。

會議其他議題：(1) 呼籲第七次十字軍 (1248-54, 路易九世領導)；(2) 處理 1241 年蒙古軍隊入侵歐洲所造成之恐慌（已退至中亞但記憶猶新）；(3) 規範樞機團選舉教宗之 conclave 制度（封閉式投票、生活條件逐日縮減直至選出新教宗）— 此「Ubi periculum」憲章雖 1274 年才正式頒佈於第二次里昂會議，但本次會議已是其先聲；(4) 規範法律訴訟程序、神職人員財產處分。`,
  notes: `- 通過：1245 年 6 月 28 日 - 7 月 17 日於里昂
- 與會：約 150 位主教（西歐為主，因蒙古恐慌與帝國衝突，東歐主教多缺席）
- 召集者：教宗依諾增爵四世（避難里昂）
- **正式罷黜腓特烈二世** — 中世紀教權鼎盛之象徵性時刻
- 呼籲第七次十字軍
- 處理蒙古入侵威脅
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-11-lateran-iii',
    'medieval-12-lateran-iv',
    'medieval-14-lyon-ii',
    'medieval-15-vienne',
  ],
}
