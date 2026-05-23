import type { Creed } from '../types'

export const medieval08: Creed = {
  slug: 'medieval-08-constantinople-iv',
  category: 'ecumenical-council',
  councilNo: 8,
  order: 808,
  nameZh: '第四次君士坦丁堡大公會議',
  nameEn: 'Fourth Council of Constantinople',
  nameLat: 'Concilium Constantinopolitanum IV',
  year: 870,
  location: '君士坦丁堡‧聖索菲亞大殿',
  topic: '罷黜君士坦丁堡宗主教佛迪烏（Photios）／處理「佛迪烏分裂」(Photian Schism)；申斥伊里納神像爭議遺緒；確認羅馬首席權與五大宗主教座階序',
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
      textKey: 'medieval-08-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-08-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-08-latin',
      source: 'Documenta Catholica Omnia, 0869-0870,_Concilium_Constantinopolitanum_IV,_Documenta,_LT.doc — 27 canons + Photian Schism decrees',
    },
  ],
  summaryZh: `第八次大公會議於 869-70 年在君士坦丁堡聖索菲亞大殿舉行，由東羅馬皇帝瓦西里一世 (Basil I) 召集，教宗阿德良二世 (Adrian II) 特使主持。會議核心議題為解決「佛迪烏分裂」(Photian Schism, 858-867) — 廢黜宗主教伊納爵 (Ignatius) 後由佛迪烏 (Photios) 繼任所引發的東西方教會衝突。會議廢黜佛迪烏、復位伊納爵，並頒佈 27 條 canons 規範教會紀律。

本次會議**僅天主教承認為第八次大公會議**；東正教不承認 — 因為 879-80 年另一次君士坦丁堡會議在教宗若望八世特使參與下平反佛迪烏，東正教視此為真正的「第八次」。這是天主教與東正教大公會議計算差異的最早分歧點。

本會議的重大意義：(1) 重申羅馬教座首席權；(2) 確認君士坦丁堡、亞歷山大、安提阿、耶路撒冷的五大宗主教座階序；(3) 譴責一位平信徒（皇帝 Bardas 等人）介入宗主教任命之亂；(4) 重申第二次尼西亞 (787) 對聖像敬禮之決議。會議精神象徵 1054 年大分裂之前最後一場「形式上」的東西方共同會議。`,
  notes: `- 通過日期：869-870 第十次會議閉幕
- 與會教長：東西方共約 100 餘人；羅馬特使主持
- 召集者：拜占庭皇帝 Basil I (the Macedonian)
- 27 條 canons：規範教會紀律、宗主教任命程序、平信徒不得干預教會內部事務
- **東正教不承認**：彼方視 879-80 君士坦丁堡會議為「第八次」 — 這次平反了 869 廢黜的佛迪烏，並譴責 filioque 加入信經
- 1054 大分裂前最後一場名義上的東西方聯席會議
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-09-lateran-i',
    'medieval-10-lateran-ii',
  ],
}
