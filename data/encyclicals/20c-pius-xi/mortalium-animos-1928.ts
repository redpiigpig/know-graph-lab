import type { PapalDocument } from '../types'

export const mortaliumAnimos1928: PapalDocument = {
  slug: 'mortalium-animos-1928',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Mortalium Animos',
  titleEn: 'On Religious Unity',
  titleZh: '《人類心靈》通諭 — 論宗教合一',
  promulgationDate: '1928-01-06',
  century: 20,
  summaryZh: "碧岳十一世對 1920 年代「合一運動」（oecumenismus）的訓導性回應。本通諭立場較保守——強調合一意味著「分離的兄弟回歸羅馬教會」，反對當時某些「萬流歸宗」（pan-Christianismus）相對主義主張。\n\n本通諭的立場後於梵二《大公主義法令》（Unitatis Redintegratio 1964）與若望保祿二《願他們合而為一》（Ut Unum Sint 1995）獲得實質性更新。",
  topics: ["合一運動", "宗教真理", "梵二前"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mortalium-animos-1928-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_19280106_mortalium-animos_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mortalium-animos-1928-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19280106_mortalium-animos.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mortalium-animos-1928-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_19280106_mortalium-animos.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mortalium-animos-1928-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_19280106_mortalium-animos.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19280106_mortalium-animos.html',
  notes: "",
}
