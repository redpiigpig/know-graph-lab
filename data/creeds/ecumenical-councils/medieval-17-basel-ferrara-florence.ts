import type { Creed } from '../types'

export const medieval17: Creed = {
  slug: 'medieval-17-basel-ferrara-florence',
  category: 'ecumenical-council',
  councilNo: 17,
  order: 817,
  nameZh: '巴塞爾－費拉拉－佛羅倫斯大公會議',
  nameEn: 'Council of Basel-Ferrara-Florence',
  nameLat: 'Concilium Basileense-Ferrariense-Florentinum',
  year: 1431,
  location: '巴塞爾／費拉拉／佛羅倫斯（會議因疫情兩度遷址）',
  topic: '東西教會合一短暫達成（佛羅倫斯合一令 Laetentur Caeli 1439-07-06）／結束最後一次公會議至上主義抵抗／與科普特、亞美尼亞、亞述東方教會分別簽署合一令',
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
      textKey: 'medieval-17-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-17-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-17-latin',
      source: 'Documenta Catholica Omnia, 1431-1431,_Concilium_Basileense,_Documenta_Omnia,_LT.pdf — 含 Laetentur Caeli 佛羅倫斯合一令 + 與科普特／亞美尼亞／亞述合一令',
    },
  ],
  summaryZh: `本會議綜合三個地點與兩個競爭階段：(1) 巴塞爾 (Basel, 1431-37) 由教宗 Martin V 召開，原為延續 Constance 改革議程；(2) 費拉拉 (Ferrara, 1438-39) 由教宗 Eugene IV 遷址召開，因巴塞爾派抵制教宗權威而轉移正統會議所在；(3) 佛羅倫斯 (Florence, 1439-43) 因 Ferrara 爆發疫情遷址；(4) 羅馬 (Rome, 1443-45) 最後階段於羅馬閉幕。同時，留在巴塞爾的部分人員選出對立教宗 Felix V (1439-49)，與 Eugene IV 對峙；此「Basel 分裂」於 1449 年和解結束。

**佛羅倫斯合一 (1439-07-06)**：本會議最具歷史意義的成就 — 東羅馬皇帝 John VIII Palaiologos、君士坦丁堡牧首 Joseph II、約 700 位希臘東方教會代表親臨佛羅倫斯與拉丁西方會晤。經數月神學辯論，雙方達成「合一令」(Laetentur Caeli)：(1) 東方接受 filioque 之神學意義 (雖不必加入經文)；(2) 接受煉獄；(3) 接受發酵餅與無酵餅皆可祝聖；(4) 接受教宗首席權。此合一於 1439-07-06 於佛羅倫斯大教堂 (Santa Maria del Fiore) 宣告，希臘文與拉丁文同時頒佈。

然此合一同樣短暫：希臘代表回國後遭拒絕；牧首 Joseph II 於 Florence 去世 (1439-06-10) 未及回國捍衛；君士坦丁堡反對派宣告合一無效；1453 年君士坦丁堡淪陷於奧斯曼帝國前夕，東方教會正式撤銷合一。

**其他東方教會合一**：本會議亦與科普特正教 (1442 Cantate Domino)、亞美尼亞使徒教會 (1439 Exsultate Deo)、敘利亞正教 (1444)、亞述東方教會 (1445) 等分別簽署合一令；雖各自規模有限，但構成天主教首次系統性外展嘗試。

本會議亦推翻 Constance 之「公會議至上主義」— 教宗 Eugene IV 於 1437 年將會議從 Basel 遷至 Ferrara，象徵教宗權威重新凌駕公會議；Lateran V (1512-17) 正式為此定性。`,
  notes: `- 通過：1431-07-23 至 1445 (Basel) / 1438-1443 (Ferrara→Florence→Rome)
- 與會：希臘代表團約 700 餘人 (1438-39) 是本會議最盛時刻
- 召集者：教宗 Martin V → Eugene IV
- **佛羅倫斯合一 1439-07-06** (Laetentur Caeli) — 東西方教會合一；後遭東方撤銷
- 同年與亞美尼亞 (1439 Exsultate Deo)、1442 科普特 (Cantate Domino)、1444 敘利亞、1445 亞述合一令
- 結束最後一次大規模 conciliarism 抵抗
- Basel 分裂 (對立教宗 Felix V, 1439-49)
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-15-vienne',
    'medieval-16-constance',
    'medieval-18-lateran-v',
  ],
}
