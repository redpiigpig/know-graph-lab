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
  subtitle: '前藏 — 古代近東智慧、神話與律法的正典前驅文獻',
  boundary: '以色列／基督教正典成形之前的古代近東文獻（被吸收、改寫或對照者）。',
  enabled: true,
  collections: [
    {
      key: 'qian',
      name: '前藏',
      name_en: 'Antecedent Texts',
      glyph: '前',
      genres: '智慧‧神話‧律法',
      summary: '古代近東的智慧文學、洪水與創造神話、法典——以色列與基督教傳統據以吸收、改寫或對照的前驅文本。',
      zheng: {
        summary: '被以色列／猶太傳統吸收或歸化的近東前驅文獻。',
        divisions: [
          {
            key: 'wisdom', label: '近東智慧文學', label_en: 'ANE Wisdom',
            works: [
              { title_zh: '亞希夸書', title_orig: 'Story of Ahiqar', author: '佚名', era: '亞述（前 7 世紀）', place: '亞述／埃及（象島）', language: '亞蘭文', note: '宮廷智者亞希夸的箴言與宮廷陰謀傳奇，被猶太《多比傳》歸化吸收', link: '/apocrypha' },
              { title_zh: '阿門內莫普訓言', title_orig: 'Instruction of Amenemope', author: '阿門內莫普', era: '約前 12 世紀', place: '埃及', language: '埃及文', note: '埃及智慧文學，與《箴言》22–24 章高度平行' },
            ],
          },
          {
            key: 'myth', label: '創造與洪水神話', label_en: 'Creation & Flood Myths',
            works: [
              { title_zh: '吉爾伽美什史詩', title_orig: 'Epic of Gilgamesh', author: '佚名（辛雷烏尼尼編訂）', era: '約前 2100–1200 年', place: '美索不達米亞', language: '阿卡德文（蘇美前身）', note: '含洪水敘事，與《創世記》挪亞洪水母題對照' },
              { title_zh: '阿特拉哈西斯史詩', title_orig: 'Atrahasis Epic', author: '佚名', era: '約前 18 世紀', place: '巴比倫', language: '阿卡德文', note: '創造人類與洪水的巴比倫神話' },
              { title_zh: '埃努瑪‧埃利什', title_orig: 'Enuma Elish', author: '佚名', era: '約前 12 世紀', place: '巴比倫', language: '阿卡德文', note: '巴比倫創世史詩，與《創世記》一章創造母題對照' },
            ],
          },
          {
            key: 'law', label: '古代法典', label_en: 'Ancient Law Codes',
            works: [
              { title_zh: '漢摩拉比法典', title_orig: 'Code of Hammurabi', author: '漢摩拉比', era: '約前 1754 年', place: '巴比倫', language: '阿卡德文', note: '與《出埃及記》約書（聖約律）平行的古巴比倫法典' },
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
