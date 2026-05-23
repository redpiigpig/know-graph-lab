import type { Creed } from '../types'

export const medieval11: Creed = {
  slug: 'medieval-11-lateran-iii',
  category: 'ecumenical-council',
  councilNo: 11,
  order: 811,
  nameZh: '第三次拉特朗大公會議',
  nameEn: 'Third Council of the Lateran',
  nameLat: 'Concilium Lateranense III',
  year: 1179,
  location: '羅馬‧拉特朗聖若望大殿',
  topic: '確立教宗選舉須樞機 2/3 多數通過（沿用至今）／譴責 Cathars 卡特里派與 Waldenses 瓦勒度派／規範敘任程序',
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
      textKey: 'medieval-11-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。中世紀公會議散落於 DH 600-1450 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Schroeder English translation (public domain)',
      text: '',
      textKey: 'medieval-11-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'medieval-11-latin',
      source: 'Documenta Catholica Omnia, 1179-1179,_Concilium_Lateranum_III,_Documenta,_LT.doc — 27 canons 含教宗選舉 2/3 多數',
    },
  ],
  summaryZh: `第三次拉特朗大公會議於 1179 年 3 月由教宗亞歷山大三世 (Alexander III) 召開，旨在結束自 1159 年以來與神聖羅馬皇帝腓特烈一世 (Frederick I Barbarossa) 之間的長期衝突 — 後者支持四位對立教宗（Victor IV, Paschal III, Callixtus III, Innocent III）對抗 Alexander III 將近二十年。1177 年《威尼斯和約》(Peace of Venice) 終結戰爭，本次會議為其神學與紀律收尾。

會議最具歷史性的決議是 **canon 1：教宗選舉須由樞機團 2/3 多數通過方為有效** — 此規則自此沿用至今，是天主教選舉法的奠基性規定。會議共頒 27 條 canons：(1) 譴責南法的 Cathars 卡特里派 (Albigensians) 與 Waldenses 瓦勒度派為異端 (canon 27)，授權地方主教採用武力鎮壓；(2) 規範敘任與聖秩授職程序；(3) 禁止神職人員世襲、聚斂財富；(4) 禁止猶太人雇用基督徒奴僕 (canon 26)。

本會議的「異端鎮壓」精神將於 30 多年後的第四次拉特朗大公會議 (1215) 進一步制度化為宗教裁判所 (Inquisition) 的雛形。`,
  notes: `- 通過：1179 年 3 月 5-19 日於拉特朗聖若望大殿
- 與會：約 300 餘主教（含拉丁、希臘、馬龍尼派）
- 召集者：教宗亞歷山大三世
- 27 條 canons
- **canon 1**：教宗選舉須樞機 2/3 多數 — 沿用至今
- canon 27：譴責 Cathars / Waldenses 異端 — 中世紀異端鎮壓制度化之起點
- 中文版尚未從 vatican.va 取得（vatican.va 對中世紀公會議無中文版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 拉丁版待補（candidates: documentacatholicaomnia.eu / Wikisource la）`,
  related: [
    'medieval-09-lateran-i',
    'medieval-10-lateran-ii',
    'medieval-12-lateran-iv',
    'medieval-13-lyon-i',
  ],
}
