import type { DazangEra } from './types'
import { ANCIENT_ERA } from './ancient'
import { MEDIEVAL_ERA } from './medieval'
import { EARLY_MODERN_ERA } from './early-modern'
import { MODERN_ERA } from './modern'

export * from './types'

// 四個時代：古代 → 中世紀 → 近代 → 現代
// 仿佛教《大藏經》「正藏／續藏」的切割：古代為「正藏」，中世紀以降為「續藏」。
const PRE_CHRISTIAN_ERA: DazangEra = {
  key: 'pre',
  name: '前基督教大藏經',
  name_en: 'Pre-Canonical Antecedents',
  glyph: '前',
  subtitle: '前藏 — 邊界劃分之前的原始啟示母體（埃及‧兩河‧敘利亞‧希臘‧羅馬）',
  boundary: '上帝在歷史長河中尚未被特定宗教群體「邊界劃分」之前的原始啟示母體——普遍之道（Logos）在人類文明初期的漫溢。',
  enabled: true,
  collections: [
    {
      key: 'jing',
      name: '經藏',
      name_en: 'Scriptures (Antecedents)',
      glyph: '經',
      genres: '異教起源‧前驅文獻',
      summary: '尚未被任何宗教群體劃下邊界之前的原始啟示母體：埃及、美索不達米亞、敘利亞、希臘、羅馬的神話、哲學與律法，是隱密的上帝按其主權所賜、全人類共享的屬靈資產，後世一神教與偉大哲學共同汲取的土壤。基督教之前無正／外之分，僅立「前藏」一套目錄；目前先收亞希夸書，餘卷待逐步策展。',
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

// 十藏定稿順序（user 2026-06-16，word-2 最後結論）：經‧律‧論‧宣‧函‧儀‧詩‧譯‧史‧類。
// 各時代資料檔內部可任意排列；此處統一依 CANON_ORDER 重排，作為全站顯示順序的單一真相。
export const CANON_ORDER = ['jing', 'lu', 'lun', 'xuandao', 'shuxin', 'liyi', 'shiwen', 'yijiao', 'shizhuan', 'leishu']

function orderCollections(era: DazangEra): DazangEra {
  return {
    ...era,
    collections: [...era.collections].sort(
      (a, b) => CANON_ORDER.indexOf(a.key) - CANON_ORDER.indexOf(b.key),
    ),
  }
}

export const ERAS: DazangEra[] = [
  PRE_CHRISTIAN_ERA,
  ANCIENT_ERA,
  MEDIEVAL_ERA,
  EARLY_MODERN_ERA,
  MODERN_ERA,
].map(orderCollections)

export function findEra(key: string): DazangEra | undefined {
  return ERAS.find(e => e.key === key)
}
