import type { PapalDocument } from '../types'

export const epistolaeSelectae1000: PapalDocument = {
  slug: 'epistolae-selectae-1000',
  popeSlug: 'sylvester-ii',
  category: 'epistola',
  titleLat: 'Epistolae selectae',
  titleEn: 'Selected Letters of Sylvester II (Gerbert of Aurillac)',
  titleZh: '《精選書信集》— 千禧年教宗、法蘭西學者 Gerbert of Aurillac',
  promulgationDate: '999-04-02',
  century: 10,
  summaryZh: `教宗西爾維斯特二世（即 Gerbert of Aurillac, 999-1003）為首位法蘭西教宗，10c 最傑出學者——精通數學、天文、阿拉伯科學（從 Cordoba 引進 Arabic numerals 與 astrolabe 到拉丁世界）。任教宗期間與神羅皇帝 Otto III 共同推動「神聖羅馬帝國 / 教廷雙頭領導下的基督教世界 renovatio」（renovatio imperii Romanorum 理想）。在位短促（4 年）但寫了大量信件——含致東歐傳教（首批 Apostolic Letters 給匈牙利 King Stephen I → Hungarian crown 「Holy Crown of St. Stephen」由 Sylvester II 親頒；致波蘭 Boleslaw / 致基輔 Vladimir 等中歐皈依文件）。是「黑暗世紀」唯一具學術重量的教宗——後 1378-1517 教廷一直把他視為「轉折性人物」。`,
  topics: ['千禧年', 'Gerbert of Aurillac', 'Apostolic Letters 給匈牙利 / 波蘭', '中歐皈依'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-selectae-1000-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'epistolae-selectae-1000-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 139）',
      textKey: 'epistolae-selectae-1000-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
