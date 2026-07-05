/**
 * 大兵日記（A Soldier's Diary）— 軍事化自律養成 App 的規則引擎（單一真相來源）
 *
 * 純資料 + 純函式：軍階階梯、四大屬性、儀隊操課項目、每日紀律任務、
 * XP 與屬性成長公式、徽章判定。前後端共用（server route 算獎勵、前端顯示）。
 *
 * 設計原則：全部集中在此檔，UI 只引用不 hardcode（對齊全站慣例）。
 * 內容純為訓練紀錄與遊戲化，無任何其他用途。
 */

/* ─────────────────────────  軍階  ───────────────────────── */

export interface Rank {
  key: string
  name: string // 繁中軍階名
  nameEn: string
  minXp: number // 達到此階所需累計 XP
  insignia: string // 簡易識別符（前端可換成 SVG 臂章）
}

/** 國軍軍階階梯（二等兵 → 上尉），依累計 XP 晉升 */
export const RANKS: Rank[] = [
  { key: 'pvt2', name: '二等兵', nameEn: 'Private 2nd Class', minXp: 0, insignia: '▎' },
  { key: 'pvt1', name: '一等兵', nameEn: 'Private 1st Class', minXp: 120, insignia: '▎▎' },
  { key: 'pfc', name: '上等兵', nameEn: 'Superior Private', minXp: 300, insignia: '▎▎▎' },
  { key: 'cpl', name: '下士', nameEn: 'Corporal', minXp: 560, insignia: '❯' },
  { key: 'sgt', name: '中士', nameEn: 'Sergeant', minXp: 920, insignia: '❯❯' },
  { key: 'ssg', name: '上士', nameEn: 'Staff Sergeant', minXp: 1420, insignia: '❯❯❯' },
  { key: 'msg', name: '士官長', nameEn: 'Master Sergeant', minXp: 2100, insignia: '❰❱' },
  { key: 'wo', name: '准尉', nameEn: 'Warrant Officer', minXp: 3000, insignia: '◆' },
  { key: '2lt', name: '少尉', nameEn: 'Second Lieutenant', minXp: 4200, insignia: '◆◆' },
  { key: '1lt', name: '中尉', nameEn: 'First Lieutenant', minXp: 5800, insignia: '◆◆◆' },
  { key: 'cpt', name: '上尉', nameEn: 'Captain', minXp: 7800, insignia: '★' },
]

export interface RankProgress {
  rank: Rank
  next: Rank | null
  intoRank: number // 進入本階後累積的 XP
  span: number // 本階到下一階所需（頂階為 0）
  progress: number // 0..1，本階內晉升進度（頂階為 1）
}

/** 依累計 XP 算出目前軍階與晉升進度 */
export function rankForXp(xp: number): RankProgress {
  const safe = Math.max(0, Math.floor(xp || 0))
  let idx = 0
  for (let i = 0; i < RANKS.length; i++) {
    if (safe >= RANKS[i].minXp) idx = i
  }
  const rank = RANKS[idx]
  const next = idx < RANKS.length - 1 ? RANKS[idx + 1] : null
  const intoRank = safe - rank.minXp
  const span = next ? next.minXp - rank.minXp : 0
  const progress = next ? Math.min(1, intoRank / span) : 1
  return { rank, next, intoRank, span, progress }
}

/* ─────────────────────────  四大屬性  ───────────────────────── */

export type AttrKey = 'strength' | 'endurance' | 'discipline' | 'bearing'

export interface AttrDef {
  key: AttrKey
  name: string
  short: string
  color: string
  desc: string
}

export const ATTRIBUTES: AttrDef[] = [
  { key: 'strength', name: '力量', short: '力', color: '#b45309', desc: '肌力與爆發，來自體能訓練與操槍負重' },
  { key: 'endurance', name: '耐力', short: '耐', color: '#4d7c0f', desc: '持久與續航，來自長時間操課與有氧' },
  { key: 'discipline', name: '紀律', short: '律', color: '#0f766e', desc: '自律與服從，來自每日任務與準時回報' },
  { key: 'bearing', name: '儀態', short: '儀', color: '#7c2d12', desc: '軍姿與精神，來自儀隊操課與定型' },
]

export const ATTR_MIN = 0
export const ATTR_MAX = 100
export const ATTR_START = 30

export type AttrDelta = Partial<Record<AttrKey, number>>

/* ─────────────────────────  儀隊操課項目  ───────────────────────── */

export interface DrillItem {
  key: string
  name: string
  desc: string
  /** 主要鍛鍊屬性（每次操練的基礎成長權重） */
  gains: AttrDelta
}

/** 儀隊／基本教練科目（純軍姿與隊列動作） */
export const DRILL_ITEMS: DrillItem[] = [
  { key: 'attention', name: '立正定型', desc: '標準軍姿靜止，鍛鍊定力與軍容', gains: { bearing: 1.4, discipline: 0.6 } },
  { key: 'facing', name: '基本轉法', desc: '向左右後轉、看齊，動作齊一', gains: { bearing: 1.0, discipline: 0.8 } },
  { key: 'march', name: '齊步行進', desc: '齊步與踏步，步幅步速一致', gains: { bearing: 0.8, endurance: 1.0 } },
  { key: 'slowmarch', name: '正步分列', desc: '正步與分列式，儀隊主科', gains: { bearing: 1.6, endurance: 0.8 } },
  { key: 'rifle', name: '托槍持槍', desc: '持槍、托槍、驗槍等槍法操作', gains: { strength: 1.2, bearing: 0.8 } },
  { key: 'flourish', name: '花式操槍', desc: '拋接旋轉等花式，需長期熟練', gains: { strength: 1.0, bearing: 1.2 } },
  { key: 'salute', name: '敬禮致敬', desc: '注目禮、舉手禮、槍禮', gains: { discipline: 1.0, bearing: 0.8 } },
]

export const drillItemMap: Record<string, DrillItem> = Object.fromEntries(
  DRILL_ITEMS.map((d) => [d.key, d]),
)

/* ─────────────────────────  每日紀律任務  ───────────────────────── */

export interface Mission {
  key: string
  name: string
  xp: number
  gains: AttrDelta
}

/** 每日可勾選的自律任務（打卡即得 XP，鼓勵日常習慣） */
export const DAILY_MISSIONS: Mission[] = [
  { key: 'wakeup', name: '準時起床出操', xp: 8, gains: { discipline: 1.0 } },
  { key: 'quarters', name: '內務整理（棉被摺角、環境清潔）', xp: 6, gains: { discipline: 0.8, bearing: 0.4 } },
  { key: 'workout', name: '自主體能（伏地挺身／仰臥起坐等）', xp: 10, gains: { strength: 1.0, endurance: 0.8 } },
  { key: 'run', name: '跑步或有氧 20 分鐘以上', xp: 10, gains: { endurance: 1.2 } },
  { key: 'grooming', name: '服裝儀容整潔（理容、擦鞋、燙服）', xp: 6, gains: { bearing: 1.0 } },
  { key: 'report', name: '準時完成當日回報', xp: 6, gains: { discipline: 0.8 } },
]

export const missionMap: Record<string, Mission> = Object.fromEntries(
  DAILY_MISSIONS.map((m) => [m.key, m]),
)

/* ─────────────────────────  日記 payload 與獎勵公式  ───────────────────────── */

export interface DiaryPayload {
  drillItems: string[] // 今日操練的儀隊科目 key
  durationMin: number // 操課總時長（分）
  missions: string[] // 完成的每日任務 key
  note: string // 一句話心得
}

export interface LogRewards {
  xp: number
  attrDelta: AttrDelta // 各屬性成長（正整數）
}

const clampf = (n: number) => (Number.isFinite(n) ? n : 0)

/**
 * 依日記內容計算 XP 與屬性成長（純函式，前後端一致）。
 * - 操課 XP：時長 × 1.2 + 每科目 6 + 自評 × 5
 * - 任務 XP：各任務固定 XP 加總
 * - 屬性：操課科目 gains × (時長縮放) + 任務 gains，四捨五入取整、每項至少受益 1
 */
export function computeLogRewards(payload: DiaryPayload, selfScore: number): LogRewards {
  const items = Array.isArray(payload?.drillItems) ? payload.drillItems : []
  const missions = Array.isArray(payload?.missions) ? payload.missions : []
  const dur = Math.max(0, Math.min(600, clampf(payload?.durationMin)))
  const score = Math.max(0, Math.min(5, Math.floor(selfScore || 0)))

  // 時長縮放：30 分鐘為基準 1.0，最高 2.0
  const durScale = Math.min(2, dur / 30)

  let xp = 0
  const raw: Record<AttrKey, number> = { strength: 0, endurance: 0, discipline: 0, bearing: 0 }

  if (items.length > 0) {
    xp += Math.round(dur * 1.2) + items.length * 6 + score * 5
    for (const k of items) {
      const it = drillItemMap[k]
      if (!it) continue
      for (const [ak, v] of Object.entries(it.gains)) {
        raw[ak as AttrKey] += (v as number) * durScale
      }
    }
  }

  for (const k of missions) {
    const m = missionMap[k]
    if (!m) continue
    xp += m.xp
    for (const [ak, v] of Object.entries(m.gains)) {
      raw[ak as AttrKey] += v as number
    }
  }

  const attrDelta: AttrDelta = {}
  for (const a of ATTRIBUTES) {
    const g = raw[a.key]
    if (g > 0) attrDelta[a.key] = Math.max(1, Math.round(g))
  }

  return { xp, attrDelta }
}

/** 把成長套到現值上（夾在 0..100） */
export function applyAttrDelta(
  current: Record<AttrKey, number>,
  delta: AttrDelta,
): Record<AttrKey, number> {
  const out = { ...current }
  for (const a of ATTRIBUTES) {
    const d = delta[a.key] || 0
    out[a.key] = Math.max(ATTR_MIN, Math.min(ATTR_MAX, (out[a.key] || 0) + d))
  }
  return out
}

/* ─────────────────────────  徽章  ───────────────────────── */

export interface Badge {
  key: string
  name: string
  icon: string
  desc: string
}

export interface BadgeState extends Badge {
  earned: boolean
}

interface BadgeStats {
  logCount: number
  streak: number // 目前連續回報天數
  maxAttr: number // 四屬性最高值
  totalDrillMin: number
  xp: number
}

const BADGE_DEFS: Array<Badge & { test: (s: BadgeStats) => boolean }> = [
  { key: 'first', name: '入伍報到', icon: '🎖️', desc: '完成第一篇日記', test: (s) => s.logCount >= 1 },
  { key: 'streak7', name: '鋼鐵紀律', icon: '🔥', desc: '連續 7 日回報', test: (s) => s.streak >= 7 },
  { key: 'streak30', name: '役期不輟', icon: '🏅', desc: '連續 30 日回報', test: (s) => s.streak >= 30 },
  { key: 'logs30', name: '日記三十', icon: '📓', desc: '累積 30 篇日記', test: (s) => s.logCount >= 30 },
  { key: 'drill600', name: '操場千錘', icon: '🪖', desc: '累計操課滿 600 分鐘', test: (s) => s.totalDrillMin >= 600 },
  { key: 'attr80', name: '素質破八', icon: '💪', desc: '任一屬性達 80', test: (s) => s.maxAttr >= 80 },
  { key: 'attr100', name: '登峰造極', icon: '⭐', desc: '任一屬性達 100', test: (s) => s.maxAttr >= 100 },
  { key: 'nco', name: '晉身士官', icon: '❯', desc: '晉升至下士以上', test: (s) => s.xp >= 560 },
]

export function computeBadges(stats: BadgeStats): BadgeState[] {
  return BADGE_DEFS.map((b) => ({
    key: b.key,
    name: b.name,
    icon: b.icon,
    desc: b.desc,
    earned: b.test(stats),
  }))
}

/** 由日記日期陣列（YYYY-MM-DD，可亂序）算目前連續天數（含今日或昨日起算） */
export function computeStreak(dates: string[], today: string): number {
  const set = new Set(dates)
  // 允許從今日或昨日起算（今日尚未回報也不中斷昨日之前的連續）
  let cursor = new Date(today + 'T00:00:00')
  if (!set.has(fmtDate(cursor))) {
    cursor.setDate(cursor.getDate() - 1)
    if (!set.has(fmtDate(cursor))) return 0
  }
  let streak = 0
  while (set.has(fmtDate(cursor))) {
    streak++
    cursor.setDate(cursor.getDate() - 1)
  }
  return streak
}

function fmtDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
