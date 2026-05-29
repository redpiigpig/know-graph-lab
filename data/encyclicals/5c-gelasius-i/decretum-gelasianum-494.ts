import type { PapalDocument } from '../types'

export const decretumGelasianum494: PapalDocument = {
  slug: 'decretum-gelasianum-494',
  popeSlug: 'gelasius-i',
  category: 'bull',
  titleLat: 'Decretum Gelasianum',
  titleEn: 'Decree of Gelasius (Canon of Scripture)',
  titleZh: '《哲拉削決議》— 聖經正典與書目分類決議',
  promulgationDate: '494-01-01',
  century: 5,
  summaryZh: `教宗哲拉削一世 494 年於羅馬主教會議頒布的決議文獻，分五部分：(I) 論聖三、聖子降生與聖神；(II) 列出新約 + 舊約正典書目（最早期的官方聖經正典清單之一）；(III) 列舉教會公認的羅馬主教座堂優先性；(IV) 列舉 4 大會議（Nicaea/Constantinople/Ephesus/Chalcedon）權威；(V) 列舉應接受的教父著作（受認可清單）vs 應拒絕的偽典與異端著作（明確 ban 清單）。是中世紀教廷正典觀的奠基文獻；現代學界多認為該文件 5-6c 多次修訂、非 Gelasius 親頒，但傳統名稱沿用。`,
  topics: ['聖經正典', '偽典清單', '教父認可', '信仰宣言'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'decretum-gelasianum-494-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'decretum-gelasianum-494-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'decretum-gelasianum-494-latin',
      source: 'https://la.wikisource.org/wiki/Decretum_Gelasianum',
    },
  ],
  displayMode: 'paragraph-aligned',
}
