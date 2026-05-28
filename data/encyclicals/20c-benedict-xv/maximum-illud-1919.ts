import type { PapalDocument } from '../types'

export const maximumIllud1919: PapalDocument = {
  slug: 'maximum-illud-1919',
  popeSlug: 'benedict-xv',
  category: 'apostolic-letter',
  titleLat: 'Maximum Illud',
  titleEn: 'On the Propagation of the Catholic Faith Throughout the World',
  titleZh: '《夫至大至聖之任務》宗座牧函 — 論天主教傳教事業',
  promulgationDate: '1919-11-30',
  century: 20,
  summaryZh: "本篤十五世論傳教事業的歷史性宗座牧函，是 20 世紀天主教「傳教本地化」（inculturatio）路線的開山文件。\n\n核心命題：傳教不是西方文化的延伸，更不是殖民主義的附庸。傳教士應當（一）培養本地神職、培育本地主教，最終把教會領導權交給本地人；（二）尊重本地語言文化，避免「歐洲化」；（三）超越國家利益、與本國政治脫鉤。\n\n本牧函直接針對一戰中各國傳教團體被政治化（德、法、奧、意傳教士被各自政府利用）的弊端，亦回應中國等地對外國傳教事業的批評。後若望廿三世《牧者之首》（Princeps Pastorum 1959）紀念其頒布 40 週年，碧岳十二世《福音傳播者》（Evangelii Praecones 1951）紀念其頒布 30 週年。",
  topics: ["傳教神學", "本地化", "本地神職", "去殖民化", "中國天主教"],
  versions: [
    {
      lang: "zh-Hant",
      label: "中文（hsscol archive — 馬相伯選譯《馬相伯先生文集》北平：上智編譯館，民 36 年）",
      textKey: "maximum-illud-1919-chinese",
      source: "http://archive.hsscol.org.hk/Archive/database/document/P397.pdf",
      translator: "馬相伯（1840-1939，復旦大學創辦人，中國天主教近代史關鍵人物）",
      placeholder: true,
    },
    {
      lang: "en",
      label: "英文 (vatican.va)",
      textKey: "maximum-illud-1919-english",
      source: "https://www.vatican.va/content/benedict-xv/en/apost_letters/documents/hf_ben-xv_apl_19191130_maximum-illud.html",
    },
    {
      lang: "lat",
      label: "拉丁原文 (vatican.va)",
      textKey: "maximum-illud-1919-latin",
      source: "https://www.vatican.va/content/benedict-xv/la/apost_letters/documents/hf_ben-xv_apl_19191130_maximum-illud.html",
    },
    {
      lang: "it",
      label: "義大利文 (vatican.va)",
      textKey: "maximum-illud-1919-italian",
      source: "https://www.vatican.va/content/benedict-xv/it/apost_letters/documents/hf_ben-xv_apl_19191130_maximum-illud.html",
    },
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/apost_letters/documents/hf_ben-xv_apl_19191130_maximum-illud.html',
  notes: "簽署日 1919-11-30 為將臨期第一主日。本牧函常被視為「現代傳教神學」的開山之作，影響至梵二《教會傳教工作》法令（Ad Gentes 1965）、若望保祿二世《救主的使命》（Redemptoris Missio 1990）、方濟各 2019「特殊傳教月」（紀念本牧函 100 週年）。",
}
