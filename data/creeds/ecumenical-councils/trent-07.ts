import type { Creed } from '../types'

export const trent07: Creed = {
  slug: 'trent-07',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S07',
  councilDocOrder: 7,
  order: 1907,
  nameZh: '第 7 會期 ─ 論聖事令',
  nameEn: 'Session 7 — Decree on the Sacraments (general + Baptism + Confirmation) + Decree on Reformation',
  year: 1547,
  location: '北義特利騰／波隆那（特利騰大公會議第 7 會期）',
  topic: '定義七件聖事（洗禮、堅振、聖體、告解、終傅、聖秩、婚配）為基督所立；聖事 ex opere operato 自身有效；批改教派否定多件聖事',
  authors: [
    '教宗保祿三世／儒略三世／庇護四世（依會期）頒佈',
    '教廷特使主持（Del Monte／Cervini／Pole／Morone 等樞機）',
    '神學委員會審議；與會教長表決通過',
  ],
  acceptedBy: ['catholic'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 對 Trent 無中文官方版）',
      text: '',
      textKey: 'trent-07-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-07-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 7（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-07-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `第七會期定義「七件聖事」(septem sacramenta) 教義：聖事為「基督所親自設立、賦予恩寵的可見記號」；七件聖事 — 洗禮、堅振、聖體、告解、終傅、聖秩、婚配 — 皆為基督所立、為救恩所必需（雖非每人皆領每件）。同會期頒兩部分 canons：總論 13 條、洗禮 14 條、堅振 3 條。核心立場：(1) 七件全部、不多不少，駁路德的「僅二件聖事 (洗、餐) 為主立」；(2) 聖事 ex opere operato 因事工自身而有效，非取決於施行者或領受者之德行；(3) 主教為堅振之唯一通常施行者。同會期亦頒《改革令》規範教區之常駐 (residency) 與多重聖俸 (plurality) 之取締。`,
  notes: `- 頒佈日期：1547-03-03
- 會期類別：第 7 會期 / Session 7 (第一期 1545-49)
- 主議題：定義七件聖事（洗禮、堅振、聖體、告解、終傅、聖秩、婚配）為基督所立；聖事 ex opere operato 自身有效；批改教派否定多件聖事
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-05',
    'trent-06',
    'trent-08',
    'trent-09',
  ],
}
