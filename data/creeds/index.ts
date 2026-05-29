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

// ── 早期東方公會議 (councils #3-#7) ──────────────────────────
import { early03 } from './ecumenical-councils/early-03-ephesus'
import { early04 } from './ecumenical-councils/early-04-chalcedon'
import { early05 } from './ecumenical-councils/early-05-constantinople-ii'
import { early06 } from './ecumenical-councils/early-06-constantinople-iii'
import { early07 } from './ecumenical-councils/early-07-nicaea-ii'

// ── 中世紀大公會議 (councils #8-#18) ─────────────────────────
import { medieval08 } from './ecumenical-councils/medieval-08-constantinople-iv'
import { medieval09 } from './ecumenical-councils/medieval-09-lateran-i'
import { medieval10 } from './ecumenical-councils/medieval-10-lateran-ii'
import { medieval11 } from './ecumenical-councils/medieval-11-lateran-iii'
import { medieval12 } from './ecumenical-councils/medieval-12-lateran-iv'
import { medieval13 } from './ecumenical-councils/medieval-13-lyon-i'
import { medieval14 } from './ecumenical-councils/medieval-14-lyon-ii'
import { medieval15 } from './ecumenical-councils/medieval-15-vienne'
import { medieval16 } from './ecumenical-councils/medieval-16-constance'
import { medieval17 } from './ecumenical-councils/medieval-17-basel-ferrara-florence'
import { medieval18 } from './ecumenical-councils/medieval-18-lateran-v'

// ── Trent (council #19, 25 會期) ─────────────────────────────
import { trent01 } from './ecumenical-councils/trent-01'
import { trent02 } from './ecumenical-councils/trent-02'
import { trent03 } from './ecumenical-councils/trent-03'
import { trent04 } from './ecumenical-councils/trent-04'
import { trent05 } from './ecumenical-councils/trent-05'
import { trent06 } from './ecumenical-councils/trent-06'
import { trent07 } from './ecumenical-councils/trent-07'
import { trent08 } from './ecumenical-councils/trent-08'
import { trent09 } from './ecumenical-councils/trent-09'
import { trent10 } from './ecumenical-councils/trent-10'
import { trent11 } from './ecumenical-councils/trent-11'
import { trent12 } from './ecumenical-councils/trent-12'
import { trent13 } from './ecumenical-councils/trent-13'
import { trent14 } from './ecumenical-councils/trent-14'
import { trent15 } from './ecumenical-councils/trent-15'
import { trent16 } from './ecumenical-councils/trent-16'
import { trent17 } from './ecumenical-councils/trent-17'
import { trent18 } from './ecumenical-councils/trent-18'
import { trent19 } from './ecumenical-councils/trent-19'
import { trent20 } from './ecumenical-councils/trent-20'
import { trent21 } from './ecumenical-councils/trent-21'
import { trent22 } from './ecumenical-councils/trent-22'
import { trent23 } from './ecumenical-councils/trent-23'
import { trent24 } from './ecumenical-councils/trent-24'
import { trent25 } from './ecumenical-councils/trent-25'

// ── Vatican I (council #20, 2 文件) ──────────────────────────
import { vaticanIDF } from './ecumenical-councils/vatican-i-01-df'
import { vaticanIPA } from './ecumenical-councils/vatican-i-02-pa'

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
  // 早期東方公會議 5 場（councils 3-7）
  early03, early04, early05, early06, early07,
  // 中世紀 11 場（councils 8-18）
  medieval08, medieval09, medieval10, medieval11, medieval12,
  medieval13, medieval14, medieval15, medieval16, medieval17,
  medieval18,
  // Trent 25 會期（1545-63；對應 councilNo 19）
  trent01, trent02, trent03, trent04, trent05,
  trent06, trent07, trent08, trent09, trent10,
  trent11, trent12, trent13, trent14, trent15,
  trent16, trent17, trent18, trent19, trent20,
  trent21, trent22, trent23, trent24, trent25,
  // Vatican I 2 文件
  vaticanIDF,  // 1. Dei Filius — 公教信仰教義憲章 (1870-04-24)
  vaticanIPA,  // 2. Pastor Aeternus — 永恆牧人教義憲章 (1870-07-18)
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
// 5 份從 Denzinger 第 43 版附錄五 (DH 5500-5702) 上架；中譯由
// _denzinger_to_creeds.py 從輔仁神學著作編譯會 2013 紙本中譯擷取。
import { lutherSmallCatechism } from './protestant-confessions/01-luther-small-catechism'
import { augsburgConfession } from './protestant-confessions/02-augsburg-confession'
import { anglicanArticles } from './protestant-confessions/03-anglican-articles'
import { reformedBelgic } from './protestant-confessions/04-reformed-belgic'
import { limaBem } from './protestant-confessions/05-lima-bem'

export const PROTESTANT_CONFESSIONS: Creed[] = [
  lutherSmallCatechism,   // DH 5500-5502  (1529)
  augsburgConfession,     // DH 5503-5523  (1530)
  anglicanArticles,       // DH 5524-5562  (1571)
  reformedBelgic,         // DH 5575-5590  (1561)
]

// ── orthodox-confessions ─────────────────────────────────────
export const ORTHODOX_CONFESSIONS: Creed[] = []

// ── ecumenical-dialogue ──────────────────────────────────────
export const ECUMENICAL_DIALOGUES: Creed[] = [
  limaBem,                // DH 5591-5701  (1982)  — 雖在 Denzinger 附錄五但本質為跨宗派對話文件
]

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
