import type { PapalDocument } from '../types'

export const evangeliumVitae1995: PapalDocument = {
  slug: 'evangelium-vitae-1995',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Evangelium Vitae',
  titleEn: 'The Gospel of Life',
  titleZh: '《生命的福音》通諭 — 論人類生命的價值與不可侵犯',
  promulgationDate: '1995-03-25',
  century: 20,
  summaryZh: "若望保祿二世第十一道通諭，被視為其牧職核心文件。回應 20 世紀末「生命議題」全面危機：墮胎、安樂死、死刑、生殖科技、戰爭與貧窮。\n\n核心命題：天主教傳統的「不可殺人」誡命，在現代脈絡下轉譯為「生命福音」（evangelium vitae）vs「死亡文化」（cultura mortis）的對立。第 56 段對死刑提出歷史性立場修正：死刑只在「絕對必要」（rarissima）時才可允許，現代社會幾乎無此必要 — 這段為 2018 年方濟各修訂《天主教教理》第 2267 條（廢死刑）的鋪墊。",
  topics: ["生命倫理", "墮胎", "安樂死", "死刑", "死亡文化", "生命福音"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "evangelium-vitae-1995-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "evangelium-vitae-1995-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "evangelium-vitae-1995-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "evangelium-vitae-1995-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae.html',
  notes: "簽署日 1995-03-25 為聖母領報節（紀念「天主之子降生成人」、生命降臨的禮儀日），與通諭核心呼應。\n\n本通諭與《真理的光輝》（1993）為若望保祿二世「為生命倫理」雙峰文件。",
}
