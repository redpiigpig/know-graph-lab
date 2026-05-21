/**
 * Creeds 資料註冊器
 *
 * 新增一份信條：
 *   1. 在對應子資料夾建立 .ts 檔（例：ecumenical-councils/02-constantinople-381.ts）
 *   2. import 並加進對應 array
 *   3. 重啟 dev server 即可在 /creeds 看到
 *
 * 多文件大公會議（同 councilNo 多份 Creed）：例梵二 16 份。
 *   - 每份用獨立 .ts 檔，slug 以 'vatican-ii-{code-lc}-{name}' 格式
 *   - councilNo + councilDocCode + councilDocOrder 三欄共同決定排序與 group
 *   - /creeds 列表會自動把同 councilNo 多份 group 成單張可展開卡片
 */

import type { Creed } from './types'

// ── ecumenical-councils ──────────────────────────────────────
import { nicaea325 } from './ecumenical-councils/01-nicaea-325'
import { constantinople381 } from './ecumenical-councils/02-constantinople-381'

// ── Vatican II (council #21, 16 文件) ────────────────────────
import { vaticanIISC } from './ecumenical-councils/vatican-ii-01-sc'
import { vaticanIIIM } from './ecumenical-councils/vatican-ii-02-im'
import { vaticanIILG } from './ecumenical-councils/vatican-ii-03-lg'
import { vaticanIIOE } from './ecumenical-councils/vatican-ii-04-oe'
import { vaticanIIUR } from './ecumenical-councils/vatican-ii-05-ur'
import { vaticanIICD } from './ecumenical-councils/vatican-ii-06-cd'
import { vaticanIIPC } from './ecumenical-councils/vatican-ii-07-pc'
import { vaticanIIOT } from './ecumenical-councils/vatican-ii-08-ot'
import { vaticanIIGE } from './ecumenical-councils/vatican-ii-09-ge'
import { vaticanIINA } from './ecumenical-councils/vatican-ii-10-na'
import { vaticanIIDV } from './ecumenical-councils/vatican-ii-11-dv'
import { vaticanIIAA } from './ecumenical-councils/vatican-ii-12-aa'
import { vaticanIIDH } from './ecumenical-councils/vatican-ii-13-dh'
import { vaticanIIAG } from './ecumenical-councils/vatican-ii-14-ag'
import { vaticanIIPO } from './ecumenical-councils/vatican-ii-15-po'
import { vaticanIIGS } from './ecumenical-councils/vatican-ii-16-gs'

export const ECUMENICAL_COUNCILS: Creed[] = [
  nicaea325,
  constantinople381,
  // Vatican II 16 文件（時間順序）
  vaticanIISC,  // 1. 禮儀憲章 (1963-12-04)
  vaticanIIIM,  // 2. 大眾傳播工具法令 (1963-12-04)
  vaticanIILG,  // 3. 教會憲章 (1964-11-21)
  vaticanIIOE,  // 4. 東方公教會法令 (1964-11-21)
  vaticanIIUR,  // 5. 大公主義法令 (1964-11-21)
  vaticanIICD,  // 6. 主教在教會內牧靈職務法令 (1965-10-28)
  vaticanIIPC,  // 7. 修會生活革新法令 (1965-10-28)
  vaticanIIOT,  // 8. 司鐸之培養法令 (1965-10-28)
  vaticanIIGE,  // 9. 天主教教育宣言 (1965-10-28)
  vaticanIINA,  // 10. 教會對非基督宗教態度宣言 (1965-10-28)
  vaticanIIDV,  // 11. 啟示憲章 (1965-11-18)
  vaticanIIAA,  // 12. 教友傳教法令 (1965-11-18)
  vaticanIIDH,  // 13. 信仰自由宣言 (1965-12-07)
  vaticanIIAG,  // 14. 教會傳教工作法令 (1965-12-07)
  vaticanIIPO,  // 15. 司鐸職務與生活法令 (1965-12-07)
  vaticanIIGS,  // 16. 牧靈憲章 (1965-12-07)
]

// ── protestant-confessions ───────────────────────────────────
export const PROTESTANT_CONFESSIONS: Creed[] = []

// ── orthodox-confessions ─────────────────────────────────────
export const ORTHODOX_CONFESSIONS: Creed[] = []

// ── ecumenical-dialogue ──────────────────────────────────────
export const ECUMENICAL_DIALOGUES: Creed[] = []

// ── apostolic-creeds（使徒信經 + 亞他那修 + 迦克墩 etc.） ─────
import { apostlesCreed } from './apostolic-creeds/00-apostles'
import { athanasianCreed } from './apostolic-creeds/01-athanasian'

export const APOSTOLIC_CREEDS: Creed[] = [
  apostlesCreed,
  athanasianCreed,
]

// ── 統一列表（依 category + order 排序） ──────────────────────
export const ALL_CREEDS: Creed[] = [
  ...APOSTOLIC_CREEDS,
  ...ECUMENICAL_COUNCILS,
  ...PROTESTANT_CONFESSIONS,
  ...ORTHODOX_CONFESSIONS,
  ...ECUMENICAL_DIALOGUES,
].sort((a, b) => a.order - b.order)

export function findCreed(slug: string): Creed | undefined {
  return ALL_CREEDS.find(c => c.slug === slug)
}

export * from './types'
