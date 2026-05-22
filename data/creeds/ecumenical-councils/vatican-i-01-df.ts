import type { Creed } from '../types'

export const vaticanIDF: Creed = {
  slug: 'vatican-i-df-dei-filius',
  category: 'ecumenical-council',
  councilNo: 20,
  councilDocCode: 'DF',
  councilDocOrder: 1,
  order: 2001,
  nameZh: '天主子教義憲章（公教信仰教義憲章）',
  nameEn: 'Dogmatic Constitution on the Catholic Faith',
  nameLat: 'Dei Filius',
  year: 1870,
  location: '羅馬‧聖伯多祿大殿（梵蒂岡第一屆大公會議第三會期）',
  topic: '回應啟蒙運動以來理性主義、唯物論、泛神論、信仰主義 (fideism) 對天主教信仰根基的挑戰；正面確立天主存在可由理性認知、啟示與信德的本質、信仰與理性的關係 — 為 19 世紀現代神學重塑護教學基礎',
  authors: [
    '教宗碧岳九世（Pius IX）頒佈',
    '主要起草者：Joseph Kleutgen S.J.（重寫底本）、Johannes Baptist Franzelin S.J.（前期草案）',
    '神學委員會（Deputatio de fide）審議',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 無中文官方版）',
      text: '',
      textKey: 'df-chinese',
      source: '待補：來源候選 → 中華民國天主教主教團《梵蒂岡第一屆大公會議文獻》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Standard English translation (Tanner / Norman P. Tanner, S.J., ed.)',
      text: '',
      textKey: 'df-english',
      source: 'https://www.papalencyclicals.net/councils/ecum20.htm (Session 3, 24 April 1870)',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'df-latin',
      source: 'https://www.vatican.va/archive/hist_councils/i-vatican-council/documents/vat-i_const_18700424_dei-filius_la.html',
    },
  ],
  summaryZh: `《天主子教義憲章》(Dei Filius)，亦稱《公教信仰教義憲章》，是梵蒂岡第一屆大公會議（1869-70）於 1870 年 4 月 24 日第三會期頒佈的兩份教義憲章中第一份。文件以教宗碧岳九世名義，由公會議全體與會教長以無異議方式通過，是天主教對啟蒙運動以來理性主義浪潮的系統性官方回應。

歷史背景：自笛卡兒、康德以降，理性主義 (rationalism)、自然神論 (deism)、泛神論 (pantheism, 受黑格爾與謝林影響)、唯物論 (materialism) 與信仰主義 (fideism, 與傳統主義者 Louis de Bonald 等相關) 等思潮對啟示宗教構成多面挑戰；同期巴登地區 Jakob Frohschammer、Anton Günther、Georg Hermes 等天主教神學家試圖以德國觀念論重構教義，引起教廷高度警覺。碧岳九世於 1864 年頒《謬說要錄》(Syllabus Errorum) 列舉 80 條當代錯謬，本憲章可視為其正面建構版。

全文結構為序言 + 四章 + 對應十八條規條 (canons)：

- **第一章 論萬物的創造主天主**：確立創世論 — 天主以自由意志由無中創造世界，駁泛神論
- **第二章 論啟示**：肯定理性與啟示的雙重認識途徑 — 天主存在可由受造物以自然理性確切認知；超性啟示則為達致天主賜予的超性目標所必需
- **第三章 論信德**：信德是「對天主啟示真理的超性德行」，並非純情感或主觀經驗（駁施萊爾馬赫式情感神學），亦非完全脫離理性的盲信（駁信仰主義）
- **第四章 論信德與理性**：兩者不能彼此衝突，因兩者皆源於同一真理之天主；神學奧蹟可由理性類比探討但不能被完全證明

每章對應 canons（規條）以「若有人主張……應受逐出（anathema）」句型，正面定義教義邊界。其中第二章 canon 1 — 否認天主可由受造物以自然理性認知者受 anathema — 即是後世「自然神學可能性」的官方依據，啟發 Joseph Maréchal、Karl Rahner 的超驗多瑪斯主義 (Transcendental Thomism) 等 20 世紀路線。

本憲章對 20 世紀新多瑪斯主義復興、Lonergan 的認識論神學、John Paul II《Fides et Ratio》（1998）皆有奠基意義；與 Pastor Aeternus（同年 7 月通過的論教宗權力憲章）並列為梵一兩大教義產出。`,
  notes: `- 通過日期：1870-04-24（公會議第三會期 / Session III）
- 表決：與會 667 位教長中 515 位投 placet（贊成），無反對票（少數採 placet juxta modum 即有限度贊成）
- 起草過程：原案由 Franzelin 起草，因過於繁瑣被否決；改由 Kleutgen 重寫精簡版，獲普遍接受
- 文件分四章 + 對應 18 條 canons，以「若有人主張……」開頭、「應受逐出（anathema sit）」收尾，是天主教傳統正面定義教義的句型
- 直接針對：理性主義、自然神論、泛神論、唯物論、信仰主義、傳統主義 (traditionalism)、半理性主義 (semi-rationalism) 等 19 世紀思潮
- 與 1864《謬說要錄》(Syllabus Errorum) 為姊妹文件；前者列出否定的錯謬，本憲章作正面建構
- 後續影響：Aeterni Patris（教宗良十三世 1879 復興多瑪斯）／Pascendi Dominici Gregis（碧岳十世 1907 反現代主義）／Humani Generis（碧岳十二世 1950）／Fides et Ratio（若望保祿二世 1998）皆引述本憲章
- 中文版尚未從 vatican.va 取得（vatican.va 僅提供 Italian + Latin）；中譯需從紙本《梵蒂岡第一屆大公會議文獻》取材`,
  related: [
    'vatican-i-pa-pastor-aeternus',
    'vatican-ii-dv-dei-verbum',
    'vatican-ii-lg-lumen-gentium',
  ],
}
