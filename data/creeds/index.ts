/**
 * Creeds 資料註冊器
 *
 * 新增一份信條：
 *   1. 在對應子資料夾建立 .ts 檔（例：ecumenical-councils/02-constantinople-381.ts）
 *   2. import 並加進對應 array
 *   3. 重啟 dev server 即可在 /creeds 看到
 */

import type { Creed } from './types'

// ── ecumenical-councils ──────────────────────────────────────
import { nicaea325 } from './ecumenical-councils/01-nicaea-325'
import { constantinople381 } from './ecumenical-councils/02-constantinople-381'

export const ECUMENICAL_COUNCILS: Creed[] = [
  nicaea325,
  constantinople381,
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
