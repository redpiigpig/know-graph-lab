import type { Creed } from '../types'

export const medieval10: Creed = {
  slug: 'medieval-10-lateran-ii',
  category: 'ecumenical-council',
  councilNo: 10,
  order: 810,
  nameZh: '第二次拉特朗大公會議',
  nameEn: 'Second Council of the Lateran',
  nameLat: 'Concilium Lateranense II',
  year: 1139,
  location: '羅馬‧拉特朗聖若望大殿',
  topic: '結束「Pierleoni 分裂」(Anacletus II 對立教宗) ／ 30 條 canons 規範神職紀律；強化神職獨身、禁聖職買賣、譴責 Arnold of Brescia',
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
      textKey: 'medieval-10-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-10-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-10-latin',
      source: 'Documenta Catholica Omnia, 1139-1139,_Concilium_Lateranum_II,_Documenta,_LT.doc — 30 canons 結束 Pierleoni 分裂',
    },
  ],
  summaryZh: `第二次拉特朗大公會議於 1139 年 4 月由教宗依諾增爵二世 (Innocent II) 召開，主要目的為結束自 1130 年起 Anacletus II 對立教宗 (antipope) 所造成的「Pierleoni 分裂」— 該分裂於 1138 年 Anacletus II 去世後逐漸瓦解，本次會議正式宣告其全部任命、聖秩、決議皆為無效。

會議頒佈 30 條 canons，涵蓋廣泛紀律議題：(1) 神職人員必須嚴格守獨身 (canon 6-7) — 結婚之神職人員必須與其妻分離，否則喪失聖職；(2) 嚴禁聖職買賣與聖秩買賣 (canons 1-2, 24)；(3) 禁止以暴力侵犯神職人員、毀壞教堂；(4) 禁止借貸取息 (usuram, canon 13)；(5) 譴責 Arnold of Brescia (canon 23) — 一位主張教會應放棄財產之改革派修士，最終於 1155 年被處死。

本次會議標誌中世紀教會「Gregorian Reform」(額我略改革) 的延續，但在實際執行 — 特別是神職獨身規定上 — 仍長期遭遇地方反抗，至特利騰大公會議 (1545-63) 才確立有效制度。`,
  notes: `- 通過：1139 年 4 月於拉特朗聖若望大殿
- 與會：約 500 餘西方主教
- 召集者：教宗依諾增爵二世
- 30 條 canons
- 主議：結束 Pierleoni 分裂 + 神職獨身強化 + 譴責 Arnold of Brescia
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-08-constantinople-iv',
    'medieval-09-lateran-i',
    'medieval-11-lateran-iii',
    'medieval-12-lateran-iv',
  ],
}
