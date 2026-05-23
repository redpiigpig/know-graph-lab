import type { Creed } from '../types'

export const early07: Creed = {
  slug: 'early-07-nicaea-ii',
  category: 'ecumenical-council',
  councilNo: 7,
  order: 507,
  nameZh: '第二次尼西亞大公會議',
  nameEn: 'Second Council of Nicaea',
  nameLat: 'Concilium Nicaenum II',
  year: 787,
  location: '尼西亞（小亞細亞‧今土耳其 İznik）',
  topic: '終結拜占庭破壞聖像運動 (Iconoclasm)；定義「聖像敬禮」(προσκύνησις proskynesis veneration, 不同於 λατρεία latreia 對天主之崇拜) 之神學基礎；引用 St. Basil「對聖像之敬禮歸於原型」(ἡ τῆς εἰκόνος τιμὴ ἐπὶ τὸ πρωτότυπον διαβαίνει) 為核心論證',
  authors: [
    '召集皇帝／教宗（詳見 notes）',
    '與會教長表決通過',
  ],
  acceptedBy: ['catholic', 'orthodox', 'oriental-orthodox', 'protestant', 'lutheran', 'anglican'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '中文版（待手動填入；vatican.va 對前七次大公會議無中文版）',
      text: '',
      textKey: 'early-07-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。前七次大公會議散落於 DH 100-600 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Percival English translation (public domain)',
      text: '',
      textKey: 'early-07-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁文本（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'early-07-latin',
      source: 'Documenta Catholica Omnia, 0787-0787,_Concilium_Nicaenum_II,_Documenta,_LT.doc — Definition of Faith (含聖像敬禮 latreia/proskynesis 區別) + 22 canons 之拉丁定稿',
    },
    {
      lang: 'grc',
      label: '希臘原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'early-07-greek',
      source: 'Documenta Catholica Omnia, 0787-0787,_Concilium_Nicaenum_II,_Documenta,_GR.pdf — Definition of Faith + 22 canons polytonic Greek，pdftotext UTF-8 抽取',
    },
  ],
  summaryZh: `第二次尼西亞大公會議於 787-09-24 至 10-23 由拜占庭女皇 Irene (代年幼皇帝 Constantine VI 攝政) 召開於小亞細亞尼西亞（即第一次尼西亞 325 同一地點）；君士坦丁堡牧首 Tarasius 主持，教宗 Adrian I 派特使參加。

核心議題為「破壞聖像運動」(Iconoclasm, εἰκονοκλασία, 726-787 + 815-843 兩階段) — 拜占庭皇帝利奧三世 (Leo III, 717-741) 起於 726 年下令移除皇宮 Chalke 門上之基督聖像，引發長達一世紀的聖像論爭。反聖像派 (Iconoclasts) 論點：(1) 出 20:4 第二誡禁造偶像；(2) 對畫像致敬乃對受造物崇拜、違背基督教一神論；(3) 基督神性無法畫像、若僅畫人性則違背迦克墩「不分割」教義 (隱含 Nestorianism)。支持聖像派 (Iconodules / Iconophiles) 核心代表為 **St. John of Damascus (c.675-749, 大馬士革的若望)** — 在伊斯蘭統治下的耶路撒冷修院寫《Three Apologetic Treatises Against Those Who Attack the Divine Images》— 提出三大論證：(1) 道成肉身使天主可見 — 基督的人性即天主之「真聖像」(εἰκών) — 若禁聖像實質上是反基督論；(2) 區別 λατρεία (latreia, 對天主之絕對崇拜) 與 προσκύνησις (proskynesis, 對聖像、聖人、皇帝之敬禮) — 兩者神學上不同；(3) 引 St. Basil「對聖像之敬禮歸於原型」— 敬禮聖像即敬禮所代表之原型。

本次會議採納大馬士革若望之神學：(1) 正式宣告聖像敬禮合法，譴責 754 年 Hieria 反聖像會議；(2) 確立 latreia / proskynesis 區別 — 聖像可受敬禮 (timetike proskynesis) 但唯天主可受崇拜 (latreia)；(3) 教堂與信徒家中皆可懸掛基督、聖母、諸聖、天使的聖像；(4) 22 條 canons 規範主教選任、修院紀律、神職人員不得參與賭博等。

**歷史餘波**：813-843 年第二階段破壞聖像運動再起（利奧五世 Leo V 主導），至 843 年 Theodora 太后召開君士坦丁堡會議正式恢復聖像 — 此日（每年大齋期第一週日）即東正教「正統凱旋日」(Σύναξις τῆς Ὀρθοδοξίας / Triumph of Orthodoxy)。

本會議在西方接受度問題：法蘭克王國 Charlemagne 因翻譯錯誤（拉丁譯本將 proskynesis 譯成 adoratio 而非 veneratio），誤以為會議要求對聖像「崇拜」— 故於 794 年法蘭克福會議 (Synod of Frankfurt) 一度反對。1054 後西方逐漸接受，至 1274 第二次里昂大公會議正式並列為「七次大公會議」之一。

本會議是天主教與東正教皆承認的第七次大公會議；東方東正教 (Oriental Orthodox, 含科普特、敘利亞正教、亞美尼亞使徒) 也承認 — 是少數同時被三大東方派系（迦克墩派的東正教 + 反迦克墩派的東方東正教）皆接受的會議；亞述東方教會則僅承認 1-2 次大公會議。新教傳統中：路德宗保留部分聖像實踐；改革宗（Calvinist）多採反聖像立場、不承認本會議；聖公宗立場介於兩者間。`,
  notes: `- 通過：787-09-24 至 10-23 於尼西亞（同 325 第一次尼西亞地點）
- 與會：約 350 位主教 + 修士、教宗特使、君士坦丁堡牧首
- 召集者：拜占庭女皇 Irene（代 Constantine VI 攝政）
- 君士坦丁堡牧首 Tarasius 主持
- 譴責 754 Hieria 反聖像會議；確立聖像敬禮合法
- **核心區別**：λατρεία (latreia 對天主之崇拜) vs προσκύνησις (proskynesis 對聖像、聖人之敬禮)
- 神學基礎：St. John of Damascus《Three Apologetic Treatises》(c.730-750)
- St. Basil 名言：「對聖像之敬禮歸於原型」(ἡ τῆς εἰκόνος τιμὴ ἐπὶ τὸ πρωτότυπον διαβαίνει)
- 22 條 canons 規範主教選任、修院紀律
- 813-843 第二階段破壞聖像；843 太后 Theodora 召會議恢復 — 即東正教「正統凱旋日」
- 西方接受過程：794 Frankfurt 因譯文錯誤反對 → 1274 Lyon II 正式並列為前七次大公會議之一
- 改革宗多採反聖像立場、不承認本會議
- 中文版尚未從 vatican.va 取得（前七次大公會議無中文官方版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 原文為希臘文；拉丁版多為中世紀回譯`,
  related: [
    'early-05-constantinople-ii',
    'early-06-constantinople-iii',
  ],
}
