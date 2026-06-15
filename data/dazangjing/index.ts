import type { DazangEra } from './types'
import { ANCIENT_ERA } from './ancient'

export * from './types'

// 四個時代：古代 → 中世紀 → 近代 → 現代
// 仿佛教《大藏經》「正藏／續藏」的切割：古代為「正藏」，中世紀以降為「續藏」。
const PRE_CHRISTIAN_ERA: DazangEra = {
  key: 'pre',
  name: '前基督教大藏經',
  name_en: 'Pre-Canonical Antecedents',
  glyph: '前',
  subtitle: '前藏 — 基督教與猶太教之前的異教（埃及‧兩河‧敘利亞‧希臘‧羅馬）起源文獻',
  boundary: '基督教與猶太教之前的古代異教文獻與傳統——埃及、兩河、敘利亞、希臘、羅馬中對猶太-基督教信仰有影響者。',
  enabled: true,
  collections: [
    {
      key: 'jing',
      name: '經藏',
      name_en: 'Scriptures (Antecedents)',
      glyph: '經',
      genres: '異教起源‧前驅文獻',
      summary: '基督教與猶太教成形之前的異教起源：埃及、美索不達米亞、敘利亞、希臘、羅馬等對猶太-基督教信仰與經典有影響的文獻與傳統。基督教之前無正藏／外藏之分，僅立「前藏」一套目錄。目前先收亞希夸書一卷，餘卷待逐步策展。',
      soleCanonLabel: '前藏',
      zheng: {
        summary: '對猶太-基督教傳統有影響的古代異教前驅文獻。',
        divisions: [
          {
            key: 'antecedents', label: '異教前驅文獻', label_en: 'Pagan Antecedents',
            works: [
              { title_zh: '亞希夸書', intro: '前七世紀亞述宮廷背景的亞蘭文智慧傳奇，今存最早抄本出於埃及象島的猶太屯墾區。全篇敘述國王重臣、智者亞希夸遭養子陷害卻終獲昭雪的宮廷陰謀故事，並穿插大量箴言式的處世與道德教訓。它是近東最古老的智慧文學之一，後為猶太《多比傳》明文吸收歸化，又流傳於敘利亞、亞美尼亞、阿拉伯等多語傳統，見證以色列智慧傳統與更廣大的近東文化母體之間的深厚淵源。', title_orig: 'Story of Ahiqar', author: '佚名', era: '亞述（前 7 世紀）', place: '亞述／埃及（象島）', language: '亞蘭文', note: '宮廷智者亞希夸的箴言與宮廷陰謀傳奇，被猶太《多比傳》歸化吸收', link: '/apocrypha' },
            ],
          },
        ],
      },
            wai: { divisions: [] },
    },
  ],
}

export const ERAS: DazangEra[] = [
  PRE_CHRISTIAN_ERA,
  ANCIENT_ERA,
  {
    key: 'medieval',
    name: '中世紀基督教大藏經',
    name_en: 'Medieval Christian Canon (800–1500)',
    glyph: '中',
    subtitle: '經院哲學‧拜占庭神學‧東方教會‧修會運動',
    boundary: '800 年（查理曼加冕）至 1500 年（宗教改革前夕）。',
    enabled: false,
    collections: [],
  },
  {
    key: 'early-modern',
    name: '近代基督教大藏經',
    name_en: 'Early Modern Christian Canon (1500–1800)',
    glyph: '近',
    subtitle: '宗教改革‧反改革‧宣教擴張‧敬虔運動',
    boundary: '1500 年（宗教改革）至 1800 年。',
    enabled: false,
    collections: [],
  },
  {
    key: 'modern',
    name: '現代基督教大藏經',
    name_en: 'Modern Christian Canon (1800–)',
    glyph: '現',
    subtitle: '自由神學‧普世合一‧第三世界神學‧漢語神學',
    boundary: '1800 年至今。',
    enabled: false,
    collections: [],
  },
]

export function findEra(key: string): DazangEra | undefined {
  return ERAS.find(e => e.key === key)
}
