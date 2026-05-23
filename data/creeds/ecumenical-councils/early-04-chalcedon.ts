import type { Creed } from '../types'

export const early04: Creed = {
  slug: 'early-04-chalcedon',
  category: 'ecumenical-council',
  councilNo: 4,
  order: 504,
  nameZh: '迦克墩大公會議',
  nameEn: 'Council of Chalcedon',
  nameLat: 'Concilium Chalcedonense',
  year: 451,
  location: '迦克墩（小亞細亞‧今土耳其 Kadıköy，伊斯坦堡亞洲側）',
  topic: '頒佈《迦克墩信經 / Definition of Faith》— 定義基督一位格、兩本性 (神性與人性) — unus in duabus naturis：「不混亂、不改變、不分割、不分離」(ἀσυγχύτως, ἀτρέπτως, ἀδιαιρέτως, ἀχωρίστως)；譴責 Eutyches 一性論；確立 Mary Theotokos；引發東方教會 1500 年分裂',
  authors: [
    '召集皇帝／教宗（詳見 notes）',
    '與會教長表決通過',
  ],
  acceptedBy: ['catholic', 'orthodox', 'protestant', 'lutheran', 'reformed', 'anglican'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '中文版（待手動填入；vatican.va 對前七次大公會議無中文版）',
      text: '',
      textKey: 'early-04-chinese',
      placeholder: true,
      source: '線上 2026-05-22 全網搜尋無公開全文中譯。唯一權威：《公教會之信仰與倫理教義選集》(Denzinger 中譯) — 光啟文化 2013 / ISBN 9789575467418 / 拉中對照。前七次大公會議散落於 DH 100-600 範圍。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'Tanner / Percival English translation (public domain)',
      text: '',
      textKey: 'early-04-english',
      source: 'https://www.papalencyclicals.net/councils/',
    },
    {
      lang: 'lat',
      label: '拉丁文本（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'early-04-latin',
      source: 'Documenta Catholica Omnia, 0451-0451,_Concilium_Chalcedonense,_Documenta_Omnia,_LT.doc — 含 Definition of Faith + 30 canons 之拉丁回譯（Rusticus Diaconi 等）',
    },
    {
      lang: 'grc',
      label: '希臘原文（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'early-04-greek',
      source: 'Documenta Catholica Omnia, 0451-0451,_Concilium_Chalcedonense,_Documenta_Omnia,_GR.pdf — Κανόνες τῆς ἐν Χαλκηδόνι Ἁγίας καὶ Οἰκουμενικῆς Δ´ Συνόδου；30 canons polytonic Greek，pdftotext UTF-8 抽取',
    },
  ],
  summaryZh: `迦克墩大公會議於 451-10-08 至 11-01 由東羅馬皇帝馬西安 (Marcian) 與皇后 Pulcheria 召開於迦克墩（君士坦丁堡對岸，今伊斯坦堡亞洲側 Kadıköy），是基督教歷史上最具規模 (520+ 主教) 與最具決定性的單一大公會議之一。

會議直接背景：以弗所 431 後，Cyril of Alexandria 派內部極端化 — 君士坦丁堡修院長 Eutyches (c.378-454) 主張基督道成肉身後人性被神性完全吸收，故只剩「一個本性」(μία φύσις, mia physis) — 即「一性論」(Monophysitism)。449 年「強盜會議」(Latrocinium / Robber Council of Ephesus) 由亞歷山大牧首 Dioscorus I 主導通過 Eutyches 立場、罷黜君士坦丁堡牧首 Flavian (後死於流放途中)。此會議受教宗良一世 (Leo I the Great) 強烈譴責 — 他於 449-06-13 寫《教宗良致 Flavian 之信》(Tome of Leo)，系統性定義基督兩本性教義；皇帝狄奧多西二世起初支持 Dioscorus，但於 450 年墜馬死後，皇后 Pulcheria 與其夫馬西安召開迦克墩會議修正方向。

會議核心成就：(1) **《迦克墩信經 / Definition of Faith》** — 確認基督「一位格、兩本性」(εἰς ἕνα Πρόσωπον, καὶ μίαν Ὑπόστασιν, οὐκ εἰς δύο πρόσωπα μεριζόμενον ἢ διαιρούμενον)；兩本性「不混亂 ἀσυγχύτως、不改變 ἀτρέπτως、不分割 ἀδιαιρέτως、不分離 ἀχωρίστως」(著名的「迦克墩四副詞」chalcedonian four adverbs)；接受 Cyril 第二封致 Nestorius 信 + Tome of Leo 為正統信仰雙基準；(2) 譴責 Eutyches 一性論 + 罷黜 Dioscorus of Alexandria；(3) 確認 Mary Theotokos（重申以弗所 431）；(4) 重申尼西亞-君士坦丁堡信經 381 為唯一正統信經；(5) 27 條 canons 規範教會紀律（含著名的 canon 28 — 確認君士坦丁堡牧首與羅馬同等榮譽 — 此條為羅馬日後拒絕承認的關鍵點，教宗良一世於 452 年正式駁斥）。

**1500 年分裂**：迦克墩會議造成基督教歷史上最深遠的分裂 — 反對「兩本性」措辭的派系（多在埃及、敘利亞、亞美尼亞、衣索匹亞、努比亞）拒絕接受會議決議，形成今日之「東方東正教」(Oriental Orthodox) — 含科普特正教 (Coptic Orthodox)、敘利亞正教 (Syriac Orthodox)、亞美尼亞使徒教會 (Armenian Apostolic Church)、衣索匹亞 Tewahedo、厄立特里亞 Tewahedo、印度馬蘭卡瑞 (Malankara Orthodox)。彼方稱「Miaphysite」(密 phusite, 強調神性人性合而為一) 自我區別於 Eutyches 純粹 Monophysite — 但仍拒「兩本性」措辭。

現代普世合一進程：1965 教宗保祿六世與君士坦丁堡牧首 Athenagoras 互相取消 1054 革除令；1973-1996 系列雙邊聲明（保祿六世-Shenouda III 1973 / 保祿六世-Vasken I 1970 / 若望保祿二世-Zakka I 1984 / 若望保祿二世-Karekin I 1996）達成共識：雙方對基督論之分歧主要是「語言表達」差異而非實質神學分歧 — 雙方皆肯定基督一位格、其中神性與人性完全合一而互不混淆。雙方至今仍在禮儀上分離但神學上實質和解。

本會議是天主教、東正教與大多數新教傳統的第四次大公會議。**東方東正教 (Oriental Orthodox) 與亞述東方教會皆拒絕**。`,
  notes: `- 通過：451-10-08 至 11-01 於迦克墩 (Kadıköy)
- 與會：約 520 位主教 — 古代規模最大
- 召集者：東羅馬皇帝馬西安 (Marcian) + 皇后 Pulcheria
- 教宗良一世派特使參加；其《Tome of Leo》(449-06-13) 為會議神學基礎
- **《迦克墩信經 / Definition of Faith》**：基督「一位格、兩本性」+ 著名四副詞 (不混亂／不改變／不分割／不分離)
- 譴責 Eutyches 一性論；罷黜亞歷山大牧首 Dioscorus
- 27 條 canons；著名 canon 28 確認君士坦丁堡與羅馬同等榮譽 — 羅馬拒絕
- **東方東正教 (Coptic / Syriac / Armenian / Tewahedo / Malankara) 與亞述東方教會皆拒絕本會議** — 引發 1500 年分裂
- 現代普世合一：1973-1996 系列雙邊聲明達成「語言差異非實質神學分歧」共識；禮儀上仍分離
- 「Chalcedonian」/「non-Chalcedonian」成為基督教分類的根本詞彙
- 中文版尚未從 vatican.va 取得（前七次大公會議無中文官方版）；中譯需從《公教會之信仰與倫理教義選集》(Denzinger 中譯, 光啟 2013, ISBN 9789575467418) 紙本取材
- 原文為希臘文；拉丁版多為中世紀回譯`,
  related: [
    'early-03-ephesus',
    'early-05-constantinople-ii',
    'early-06-constantinople-iii',
  ],
}
