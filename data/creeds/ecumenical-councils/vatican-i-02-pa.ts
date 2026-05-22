import type { Creed } from '../types'

export const vaticanIPA: Creed = {
  slug: 'vatican-i-pa-pastor-aeternus',
  category: 'ecumenical-council',
  councilNo: 20,
  councilDocCode: 'PA',
  councilDocOrder: 2,
  order: 2002,
  nameZh: '論基督教會教義憲章第一（永恆牧人）',
  nameEn: 'First Dogmatic Constitution on the Church of Christ',
  nameLat: 'Pastor Aeternus',
  year: 1870,
  location: '羅馬‧聖伯多祿大殿（梵蒂岡第一屆大公會議第四會期）',
  topic: '正式定義教宗對全教會的首席權 (primatus) 與「以宗座權威 ex cathedra」宣告信仰道德問題時的不可錯謬性 (infallibilitas) — 是天主教教制神學最具決定性、也最具爭議的單一文件',
  authors: [
    '教宗碧岳九世（Pius IX）頒佈',
    '主要起草者：Vincenzo Gasser 主教（Brixen，最終文本主筆）',
    '神學委員會（Deputatio de fide）審議',
    '反對派代表（後接受）：Karl Joseph von Hefele、Felix Dupanloup、John Henry Newman（缺席派）',
  ],
  acceptedBy: ['catholic'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 無中文官方版）',
      text: '',
      textKey: 'pa-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《梵蒂岡第一屆大公會議文獻》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Standard English translation (Tanner / Norman P. Tanner, S.J., ed.)',
      text: '',
      textKey: 'pa-english',
      source: 'https://www.papalencyclicals.net/councils/ecum20.htm (Session 4, 18 July 1870)',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'pa-latin',
      source: 'https://www.vatican.va/archive/hist_councils/i-vatican-council/documents/vat-i_const_18700718_pastor-aeternus_la.html',
    },
  ],
  summaryZh: `《永恆牧人教義憲章》(Pastor Aeternus)，全名《論基督教會教義憲章第一》，是梵蒂岡第一屆大公會議於 1870 年 7 月 18 日第四會期通過、由教宗碧岳九世頒佈的歷史性文件。文件以 533 票贊成、2 票反對、150 餘位反對派教長刻意離席方式通過，正式將「教宗首席權」與「教宗不可錯謬論」定為天主教當信教義 — 是自東西方教會 1054 年分裂以來，羅馬天主教在教制神學上最具決定性的單一行動。

歷史脈絡：教宗首席權的爭議源遠流長 — 早至五世紀利奧一世已主張羅馬主教對東方的牧職權威，歷經 1054 大分裂、1438 佛羅倫斯短暫合一（其教令已隱含類似定義）、Gallican 主義 (法國國教派) 對教宗權的限制、Conciliarism (公會議至上論) 之挑戰；至 19 世紀，啟蒙運動後反教權主義 (anti-clericalism) 興起、義大利統一運動 (Risorgimento) 蠶食教皇國領土，碧岳九世藉公會議確立教宗作為「永恆牧人」對普世教會的最高權力。

全文結構為序言 + 四章 + 對應 canons：

- **第一章 論教宗首席權在伯鐸的設立**：依瑪 16:18-19、若 21:15-17，伯鐸從基督直接領受真正而至高的管轄權；非僅榮譽首席或榜樣首席，而是司法權之首席
- **第二章 論伯鐸首席權在羅馬教宗之永久持續**：伯鐸的首席權依神律 (jure divino) 永久存於羅馬主教身上
- **第三章 論羅馬教宗首席權的力量與本質**：教宗對普世教會擁有完全 (plena)、至高 (suprema)、直接 (immediata) 的「真正主教管轄權」(potestas iurisdictionis vere episcopalis)；不僅關信德與道德、亦關治理與紀律
- **第四章 論羅馬教宗的不可錯謬訓導權**：當教宗「以宗座權威」(ex cathedra)、作為「全體基督徒的牧人和導師」、運用其最高使徒權威宣告普世教會須持守的信仰或道德問題時，藉聖伯多祿所得神助，享有「天主聖神所許諾、教會在定義信德或道德教義時當享有的」不可錯謬恩典；此定義「本身、而非由教會同意」(ex sese, non autem ex consensu Ecclesiae) 即不可變更

第四章「ex sese」一句最具爭議 — 它否認 Gallican 派傳統主張的「教宗定義須經教會接受方為定論」的條件，將不可錯謬論置於教會接受過程之外。

反對派（Karl Joseph von Hefele、Felix Dupanloup、Ignaz Döllinger 等）反對的並非教宗首席權本身，而是「現在時機不宜」與「ex sese」措辭。Döllinger 拒絕接受定義後遭絕罰，成為日後「老天主教會」(Old Catholic Church) 的精神起源。

教宗未來行使 ex cathedra 教權正式案例：1854《Ineffabilis Deus》（聖母無染原罪）／1950《Munificentissimus Deus》（聖母升天）— 嚴格意義上僅此兩例（雖然教會其他訓導亦具「平常普通訓導權」之權威性，但 Pastor Aeternus 所定義之 ex cathedra 行為極為審慎使用）。

普世合一意義：本憲章是 1054 大分裂以來、東正教與天主教合一最大的神學障礙。1995 教宗若望保祿二世通諭《Ut Unum Sint》（54-95 段）主動邀請其他基督宗派討論「如何行使教宗首席權之方式」(modus exercendi)，承認首席權之行使方式可重新討論；2007《Ravenna Document》（天主教 + 東正教神學對話）達成「首席與會議制必須在三層次同時運作」的共識，為未來合一鋪設神學基礎。`,
  notes: `- 通過日期：1870-07-18（公會議第四會期 / Session IV）
- 表決：533 placet（贊成）vs 2 non placet（反對）；反對派約 150 位教長為避免投反對票而於前一日離場
- 啟動歷史背景：1870 年 9 月普法戰爭爆發、義大利軍隊隨後佔領羅馬，公會議被迫無限期休會 — 故本應計劃通過的「第二論教會憲章」(Constitutio Secunda de Ecclesia) 未及通過；該文件規劃中的「論主教團」議題延後至梵二《教會憲章》(Lumen Gentium) 才得完成
- 反對派核心人物：Karl Joseph von Hefele 主教（教會史學者）、Felix Dupanloup 主教（Orléans）、Ignaz von Döllinger（慕尼黑神學家，後遭絕罰，老天主教會精神起源）
- 反對非反「教宗首席權」原則，而反「時機」與「ex sese」措辭過度排他化
- 「ex sese, non autem ex consensu Ecclesiae」一句（第四章末）是與 Gallican 派最終決裂的鋒利切割
- 「ex cathedra」嚴格意義行使案例：1854 Ineffabilis Deus（聖母無染原罪）／1950 Munificentissimus Deus（聖母升天）
- 與 Vatican II 對比：本憲章單方面強調教宗權威；梵二《教會憲章》第三章補回「主教團 (collegium episcoporum) 連同教宗 (cum Petro et sub Petro) 共同治理普世教會」維度，是本憲章重要的補充與平衡
- 對普世合一：1995《Ut Unum Sint》§95 邀請其他宗派討論首席權行使方式；2007《Ravenna Document》達成首席—會議互動共識
- 中文版尚未從 vatican.va 取得（vatican.va 僅提供 Italian + Latin）；中譯需從紙本《梵蒂岡第一屆大公會議文獻》取材`,
  related: [
    'vatican-i-df-dei-filius',
    'vatican-ii-lg-lumen-gentium',
    'vatican-ii-ur-unitatis-redintegratio',
  ],
}
