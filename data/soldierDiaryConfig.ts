/**
 * 大兵日記（A Soldier's Diary）— 軍事化自律養成 App 的規則引擎（單一真相來源）
 *
 * 核心設定：兵員須「一一突破」五大軍種，每個軍種代表一種品質；一次只能操練
 * 「當前軍種」，該品質練滿即突破、解鎖下一軍種，五種全破＝結訓。軍階最高至上士。
 *
 * 純資料 + 純函式，前後端共用。UI 只引用不 hardcode。內容純為訓練紀錄與遊戲化。
 */

/* ─────────────────────────  軍階（最高上士）  ───────────────────────── */

export interface Rank {
  key: string
  name: string
  nameEn: string
  minXp: number
  insignia: string
}

export const RANKS: Rank[] = [
  { key: 'pvt2', name: '二等兵', nameEn: 'Private 2nd Class', minXp: 0, insignia: '▎' },
  { key: 'pvt1', name: '一等兵', nameEn: 'Private 1st Class', minXp: 120, insignia: '▎▎' },
  { key: 'pfc', name: '上等兵', nameEn: 'Superior Private', minXp: 300, insignia: '▎▎▎' },
  { key: 'cpl', name: '下士', nameEn: 'Corporal', minXp: 560, insignia: '❯' },
  { key: 'sgt', name: '中士', nameEn: 'Sergeant', minXp: 920, insignia: '❯❯' },
  { key: 'ssg', name: '上士', nameEn: 'Staff Sergeant', minXp: 1420, insignia: '❯❯❯' },
]

export interface RankProgress {
  rank: Rank
  next: Rank | null
  intoRank: number
  span: number
  progress: number
}

export function rankForXp(xp: number): RankProgress {
  const safe = Math.max(0, Math.floor(xp || 0))
  let idx = 0
  for (let i = 0; i < RANKS.length; i++) if (safe >= RANKS[i].minXp) idx = i
  const rank = RANKS[idx]
  const next = idx < RANKS.length - 1 ? RANKS[idx + 1] : null
  const intoRank = safe - rank.minXp
  const span = next ? next.minXp - rank.minXp : 0
  const progress = next ? Math.min(1, intoRank / span) : 1
  return { rank, next, intoRank, span, progress }
}

/* ─────────────────────────  五大品質  ───────────────────────── */

export type QualityKey = 'obedience' | 'strength' | 'endurance' | 'composure' | 'challenge'

export interface QualityDef {
  key: QualityKey
  name: string
  short: string
  color: string
  desc: string
}

export const QUALITIES: QualityDef[] = [
  { key: 'obedience', name: '服從', short: '從', color: '#4d7c0f', desc: '軍人天職，令行禁止、準時到位' },
  { key: 'strength', name: '體力', short: '力', color: '#b45309', desc: '肌力與爆發，鋼鐵般的體魄' },
  { key: 'endurance', name: '耐力', short: '耐', color: '#0f766e', desc: '心肺與續航，長時間不倒下' },
  { key: 'composure', name: '定力', short: '定', color: '#4338ca', desc: '意志與專注，任何情況穩如泰山' },
  { key: 'challenge', name: '挑戰', short: '挑', color: '#b91c1c', desc: '突破極限，迎向最高標準' },
]

export const qualityMap: Record<QualityKey, QualityDef> = Object.fromEntries(
  QUALITIES.map((q) => [q.key, q]),
) as Record<QualityKey, QualityDef>

export const QUALITY_MIN = 0
export const QUALITY_MAX = 100
export const BRANCH_THRESHOLD = 100 // 品質達此值即突破該軍種

export type QualityDelta = Partial<Record<QualityKey, number>>

/* ─────────────────────────  五大軍種（依序突破）  ───────────────────────── */

export interface TrainingItem {
  key: string
  name: string
  desc: string
  gain: number // 每次操練對該軍種品質的基礎成長（再乘時長縮放）
  xp: number // 每次操練固定 XP
}

export interface Branch {
  key: string
  name: string
  nameEn: string
  order: number
  quality: QualityKey
  color: string
  motto: string
  items: TrainingItem[]
}

export const BRANCHES: Branch[] = [
  {
    key: 'army', name: '陸軍', nameEn: 'ARMY', order: 1, quality: 'obedience',
    color: '#4d7c0f', motto: '服從為軍人天職',
    items: [
      { key: 'attention', name: '立正定型', desc: '標準軍姿靜止，令行禁止', gain: 3, xp: 8 },
      { key: 'basic_drill', name: '基本教練', desc: '向左右後轉、看齊、報數', gain: 3, xp: 8 },
      { key: 'march', name: '齊步正步', desc: '齊步、踏步、正步分列', gain: 4, xp: 10 },
      { key: 'obey_cmd', name: '服從指令複誦', desc: '複誦與確實執行口令', gain: 3, xp: 7 },
    ],
  },
  {
    key: 'navy', name: '海軍', nameEn: 'NAVY', order: 2, quality: 'strength',
    color: '#1d4ed8', motto: '鋼鐵體魄，破浪前行',
    items: [
      { key: 'pushup', name: '伏地挺身', desc: '標準伏地挺身組數', gain: 4, xp: 10 },
      { key: 'situp', name: '仰臥起坐', desc: '核心肌群訓練', gain: 3, xp: 8 },
      { key: 'pullup', name: '引體向上', desc: '上肢與背肌拉力', gain: 5, xp: 12 },
      { key: 'ruck', name: '負重行軍', desc: '背負裝備行進', gain: 4, xp: 12 },
    ],
  },
  {
    key: 'airforce', name: '空軍', nameEn: 'AIR FORCE', order: 3, quality: 'endurance',
    color: '#0369a1', motto: '沖天續航，永不停歇',
    items: [
      { key: 'run', name: '長跑', desc: '3000 公尺以上持續跑', gain: 5, xp: 12 },
      { key: 'shuttle', name: '折返跑', desc: '折返衝刺耐乳酸', gain: 4, xp: 10 },
      { key: 'swim', name: '游泳耐力', desc: '長距離游泳', gain: 4, xp: 11 },
      { key: 'cardio', name: '有氧續航', desc: '飛輪、跳繩等有氧', gain: 3, xp: 9 },
    ],
  },
  {
    key: 'marines', name: '海軍陸戰隊', nameEn: 'MARINES', order: 4, quality: 'composure',
    color: '#7c2d12', motto: '永遠忠誠，意志如鋼',
    items: [
      { key: 'stand', name: '站樁久站', desc: '長時間標準站姿不動', gain: 4, xp: 10 },
      { key: 'crawl', name: '低姿匍匐', desc: '低姿前進、意志耐受', gain: 5, xp: 12 },
      { key: 'plank', name: '平板支撐', desc: '棒式核心定住', gain: 4, xp: 10 },
      { key: 'obstacle', name: '障礙滲透', desc: '障礙場與滲透演練', gain: 5, xp: 13 },
    ],
  },
  {
    key: 'mp', name: '憲兵', nameEn: 'MILITARY POLICE', order: 5, quality: 'challenge',
    color: '#b91c1c', motto: '軍紀最高標準，挑戰極限',
    items: [
      { key: 'rifle_drill', name: '儀隊操槍', desc: '持槍、托槍、花式操槍', gain: 5, xp: 13 },
      { key: 'combined_pt', name: '綜合體能', desc: '國軍體能三項綜合測驗', gain: 5, xp: 13 },
      { key: 'combat_skill', name: '戰技訓練', desc: '軍事技能與應用戰技', gain: 4, xp: 12 },
      { key: 'extreme', name: '極限挑戰', desc: '突破個人紀錄的挑戰', gain: 6, xp: 15 },
    ],
  },
]

export const branchMap: Record<string, Branch> = Object.fromEntries(BRANCHES.map((b) => [b.key, b]))

/** 展平所有訓練項目，附上所屬軍種與品質 */
export interface FlatTrainingItem extends TrainingItem {
  branchKey: string
  quality: QualityKey
}
export const trainingItemMap: Record<string, FlatTrainingItem> = Object.fromEntries(
  BRANCHES.flatMap((b) => b.items.map((it) => [it.key, { ...it, branchKey: b.key, quality: b.quality }])),
)

/* ─────────────────────────  軍種進度  ───────────────────────── */

export interface BranchState {
  branch: Branch
  quality: number // 該軍種品質現值
  conquered: boolean // 已突破
  active: boolean // 當前正在突破
  locked: boolean // 尚未解鎖
  progress: number // 0..1
}

/** 依五品質現值算出各軍種狀態；active＝第一個未突破者，其後皆 locked */
export function branchStates(qualities: Record<QualityKey, number>): BranchState[] {
  let activeAssigned = false
  return BRANCHES.map((branch) => {
    const q = Math.max(0, qualities[branch.quality] || 0)
    const conquered = q >= BRANCH_THRESHOLD
    let active = false
    let locked = false
    if (!conquered && !activeAssigned) { active = true; activeAssigned = true }
    else if (!conquered && activeAssigned) locked = true
    return { branch, quality: q, conquered, active, locked, progress: Math.min(1, q / BRANCH_THRESHOLD) }
  })
}

/** 當前正在突破的軍種（全破則回傳 null） */
export function activeBranch(qualities: Record<QualityKey, number>): Branch | null {
  const st = branchStates(qualities).find((s) => s.active)
  return st ? st.branch : null
}

export const emptyQualities = (): Record<QualityKey, number> => ({
  obedience: 0, strength: 0, endurance: 0, composure: 0, challenge: 0,
})

/* ─────────────────────────  每日紀律任務  ───────────────────────── */

export interface Mission {
  key: string
  name: string
  xp: number
  obedience: number // 每日基本任務主要培養服從
}

export const DAILY_MISSIONS: Mission[] = [
  { key: 'wakeup', name: '準時起床出操', xp: 8, obedience: 1 },
  { key: 'quarters', name: '內務整理（棉被摺角、環境清潔）', xp: 6, obedience: 1 },
  { key: 'grooming', name: '服裝儀容整潔（理容、擦鞋、燙服）', xp: 6, obedience: 1 },
  { key: 'report', name: '準時完成當日回報', xp: 6, obedience: 1 },
]

export const missionMap: Record<string, Mission> = Object.fromEntries(DAILY_MISSIONS.map((m) => [m.key, m]))

/* ─────────────────────────  日記 payload 與獎勵公式  ───────────────────────── */

export interface DiaryPayload {
  trainingItems: string[] // 當前軍種的操練項目 key
  durationMin: number
  missions: string[]
  note: string
}

export interface LogRewards {
  xp: number
  qualityDelta: QualityDelta
}

const clampf = (n: number) => (Number.isFinite(n) ? n : 0)

/**
 * 依日記內容計算 XP 與品質成長（純函式，前後端一致）。
 * - 操練 XP：各項目固定 XP + 時長 × 0.8 + 自評 × 4
 * - 品質：各項目 gain × 時長縮放（30 分為 1.0，最高 2.0），累加到所屬軍種品質
 * - 任務：各任務固定 XP，並累加服從
 */
export function computeLogRewards(payload: DiaryPayload, selfScore: number): LogRewards {
  const items = Array.isArray(payload?.trainingItems) ? payload.trainingItems : []
  const missions = Array.isArray(payload?.missions) ? payload.missions : []
  const dur = Math.max(0, Math.min(600, clampf(payload?.durationMin)))
  const score = Math.max(0, Math.min(5, Math.floor(selfScore || 0)))
  const durScale = Math.min(2, dur / 30)

  let xp = 0
  const raw = emptyQualities()

  if (items.length > 0) {
    xp += Math.round(dur * 0.8) + score * 4
    for (const k of items) {
      const it = trainingItemMap[k]
      if (!it) continue
      xp += it.xp
      raw[it.quality] += it.gain * durScale
    }
  }
  for (const k of missions) {
    const m = missionMap[k]
    if (!m) continue
    xp += m.xp
    raw.obedience += m.obedience
  }

  const qualityDelta: QualityDelta = {}
  for (const q of QUALITIES) {
    const g = raw[q.key]
    if (g > 0) qualityDelta[q.key] = Math.max(1, Math.round(g))
  }
  return { xp, qualityDelta }
}

export function applyQualityDelta(
  current: Record<QualityKey, number>,
  delta: QualityDelta,
): Record<QualityKey, number> {
  const out = { ...current }
  for (const q of QUALITIES) {
    const d = delta[q.key] || 0
    out[q.key] = Math.max(QUALITY_MIN, Math.min(QUALITY_MAX, (out[q.key] || 0) + d))
  }
  return out
}

/* ─────────────────────────  徽章  ───────────────────────── */

export interface Badge { key: string; name: string; icon: string; desc: string }
export interface BadgeState extends Badge { earned: boolean }

interface BadgeStats {
  logCount: number
  streak: number
  totalTrainMin: number
  xp: number
  qualities: Record<QualityKey, number>
}

const BADGE_DEFS: Array<Badge & { test: (s: BadgeStats) => boolean }> = [
  { key: 'first', name: '入伍報到', icon: '🎖️', desc: '完成第一篇日記', test: (s) => s.logCount >= 1 },
  { key: 'streak7', name: '鋼鐵紀律', icon: '🔥', desc: '連續 7 日回報', test: (s) => s.streak >= 7 },
  { key: 'streak30', name: '役期不輟', icon: '🏅', desc: '連續 30 日回報', test: (s) => s.streak >= 30 },
  { key: 'logs30', name: '日記三十', icon: '📓', desc: '累積 30 篇日記', test: (s) => s.logCount >= 30 },
  { key: 'br_army', name: '攻克陸軍', icon: '🪖', desc: '突破陸軍（服從滿）', test: (s) => s.qualities.obedience >= BRANCH_THRESHOLD },
  { key: 'br_navy', name: '攻克海軍', icon: '⚓', desc: '突破海軍（體力滿）', test: (s) => s.qualities.strength >= BRANCH_THRESHOLD },
  { key: 'br_air', name: '攻克空軍', icon: '✈️', desc: '突破空軍（耐力滿）', test: (s) => s.qualities.endurance >= BRANCH_THRESHOLD },
  { key: 'br_marines', name: '攻克陸戰隊', icon: '🦅', desc: '突破海軍陸戰隊（定力滿）', test: (s) => s.qualities.composure >= BRANCH_THRESHOLD },
  { key: 'br_mp', name: '攻克憲兵', icon: '⭐', desc: '突破憲兵（挑戰滿）', test: (s) => s.qualities.challenge >= BRANCH_THRESHOLD },
  { key: 'graduate', name: '五軍結訓', icon: '👑', desc: '五大軍種全數突破', test: (s) => BRANCHES.every((b) => s.qualities[b.quality] >= BRANCH_THRESHOLD) },
  { key: 'ssg', name: '晉升上士', icon: '❯', desc: '晉升至上士', test: (s) => s.xp >= 1420 },
]

export function computeBadges(stats: BadgeStats): BadgeState[] {
  return BADGE_DEFS.map((b) => ({ key: b.key, name: b.name, icon: b.icon, desc: b.desc, earned: b.test(stats) }))
}

/** 由日記日期陣列算目前連續天數（含今日或昨日起算） */
export function computeStreak(dates: string[], today: string): number {
  const set = new Set(dates)
  const cursor = new Date(today + 'T00:00:00')
  if (!set.has(fmtDate(cursor))) {
    cursor.setDate(cursor.getDate() - 1)
    if (!set.has(fmtDate(cursor))) return 0
  }
  let streak = 0
  while (set.has(fmtDate(cursor))) { streak++; cursor.setDate(cursor.getDate() - 1) }
  return streak
}

function fmtDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
