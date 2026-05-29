import type { PapalDocument } from '../types'

export const epistolaeAdCarolumMagnum: PapalDocument = {
  slug: 'epistolae-ad-carolum-magnum',
  popeSlug: 'hadrian-i',
  category: 'epistola',
  titleLat: 'Epistolae ad Carolum Magnum (Codex Carolinus)',
  titleEn: 'Letters to Charlemagne (Codex Carolinus selection)',
  titleZh: '《致查理曼書信集》★★ — Codex Carolinus 9 篇 marquee',
  promulgationDate: '774-04-06',
  century: 8,
  summaryZh: `教宗哈德良一世（772-795）任內致法蘭克王查理曼大帝（Charlemagne）的書信集合，後收入《Codex Carolinus》（一部 8c 教廷致法蘭克王室書信彙編）。內容涵蓋：① 774 查理曼征服倫巴底王國後對教廷世俗領地 Donation 的確認 ② 787 第二次尼西亞公會議與聖像爭議（教宗支持聖像敬禮，與後來《Libri Carolini》之間的張力）③ 字母 a / b（Christological / soteriological 問題的請示）④ 教士訓練、彌撒禮儀統一（Sacramentarium Hadrianum 由教宗親頒）。是中世紀「教廷 / 法蘭克王國」聯盟形成的關鍵文獻組——直接導致 800 年 Leo III 為查理曼加冕、建立神聖羅馬帝國。`,
  topics: ['查理曼', 'Codex Carolinus', 'Donation of Pepin / Charlemagne', '787 Nicaea II 配合', 'Sacramentarium Hadrianum'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-ad-carolum-magnum-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'epistolae-ad-carolum-magnum-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Hadrian I — Epistolae)',
      textKey: 'epistolae-ad-carolum-magnum-latin',
      source: 'https://la.wikisource.org/wiki/Epistolae_(Hadrianus_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
