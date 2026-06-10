// ============================================================================
// SM-2 間隔複習演算法（SuperMemo-2）
// quality q：0–5；UI 簡化為 again(2) / hard(3) / good(4) / easy(5)
// ============================================================================

export interface SrsState {
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

export interface SrsResult extends SrsState {
  next_review: string; // YYYY-MM-DD
  mastery_level: number; // 0–5（給 UI/統計用，由 repetitions 推導）
}

export function sm2(prev: SrsState, q: number): SrsResult {
  let ease = prev.ease_factor || 2.5;
  let reps = prev.repetitions || 0;
  let interval = prev.interval_days || 0;

  if (q < 3) {
    // 答錯：重來
    reps = 0;
    interval = 1;
  } else {
    if (reps === 0) interval = 1;
    else if (reps === 1) interval = 6;
    else interval = Math.round(interval * ease);
    reps += 1;
  }

  // 更新 ease factor
  ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
  if (ease < 1.3) ease = 1.3;

  // 用台北時區算下次到期日（與 vocab/review 的 tzToday 比對一致）
  const next = new Date(Date.now() + interval * 86400000).toLocaleDateString("en-CA", { timeZone: "Asia/Taipei" });
  const mastery = Math.min(5, reps);

  return {
    ease_factor: Math.round(ease * 100) / 100,
    interval_days: interval,
    repetitions: reps,
    next_review: next,
    mastery_level: mastery,
  };
}

// ============================================================================
// FSRS（Free Spaced Repetition Scheduler, v4.5）— 取代 SM-2（2026-06-05）
//   - 以 difficulty(D 1–10) / stability(S 天) / retrievability(R) 三參數排程，
//     比 SM-2「ease 只降不升」更準：同樣記憶率下複習量少 ~20–30%。
//   - UI 仍送 quality 2/3/4/5（again/hard/good/easy）→ 內部映射 grade 1–4。
//   - 需要「距上次複習過了幾天」(elapsedDays) 來算 R；新卡走初始公式。
// ============================================================================

// FSRS-4.5 預設權重（17 個，官方 optimizer 預設值）
const W = [0.4072, 1.1829, 3.1262, 15.4722, 7.2102, 0.5316, 1.0651, 0.0234, 1.616, 0.1544, 1.0824, 1.9813, 0.0953, 0.2975, 2.2042, 0.2407, 2.9466];
const DECAY = -0.5;
const FACTOR = 19 / 81; // = 0.9^(1/DECAY) − 1
const REQUEST_RETENTION = 0.9; // 目標記憶率
const MIN_S = 0.1;
const MAX_S = 36500;

const clamp = (x: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, x));

const initStability = (g: number) => clamp(W[g - 1], MIN_S, MAX_S);
const initDifficulty = (g: number) => clamp(W[4] - W[5] * (g - 3), 1, 10);
const retrievability = (t: number, S: number) => Math.pow(1 + FACTOR * Math.max(0, t) / S, DECAY);
const intervalFromS = (S: number) => clamp(Math.round((S / FACTOR) * (Math.pow(REQUEST_RETENTION, 1 / DECAY) - 1)), 1, MAX_S);

function nextDifficulty(D: number, g: number): number {
  const next = D - W[6] * (g - 3);
  // 朝 initDifficulty(easy=4) 均值回歸，避免難度無限漂高
  return clamp(W[7] * initDifficulty(4) + (1 - W[7]) * next, 1, 10);
}
function stabilityAfterRecall(D: number, S: number, R: number, g: number): number {
  const hard = g === 2 ? W[15] : 1;
  const easy = g === 4 ? W[16] : 1;
  const inc = Math.exp(W[8]) * (11 - D) * Math.pow(S, -W[9]) * (Math.exp(W[10] * (1 - R)) - 1) * hard * easy;
  return clamp(S * (1 + inc), MIN_S, MAX_S);
}
function stabilityAfterForget(D: number, S: number, R: number): number {
  const sf = W[11] * Math.pow(D, -W[12]) * (Math.pow(S + 1, W[13]) - 1) * Math.exp(W[14] * (1 - R));
  return clamp(Math.min(sf, S), MIN_S, MAX_S); // 遺忘後穩定度不應高於原本
}

export interface FsrsState {
  difficulty: number | null;
  stability: number | null;
}
export interface FsrsResult {
  difficulty: number;
  stability: number;
  interval_days: number;
  next_review: string;   // YYYY-MM-DD（台北）
  mastery_level: number; // 0–5（由 stability 推導，給 UI/統計）
  retrievability: number;
}

// quality(2/3/4/5) → grade(1/2/3/4)
export function qualityToGrade(q: number): number {
  return clamp(Math.round(q) - 1, 1, 4);
}

function masteryFromStability(S: number): number {
  if (S < 1) return 0;
  if (S < 4) return 1;
  if (S < 14) return 2;
  if (S < 30) return 3;
  if (S < 90) return 4;
  return 5;
}

/**
 * FSRS 排程。
 * @param prev 既有 difficulty/stability（新卡傳 null）
 * @param quality UI 的 2/3/4/5
 * @param elapsedDays 距上次複習過了幾天（新卡可傳 0）
 */
export function fsrs(prev: FsrsState, quality: number, elapsedDays: number): FsrsResult {
  const g = qualityToGrade(quality);
  let D: number, S: number, R = 1;

  if (prev.stability == null || prev.difficulty == null) {
    // 新卡：初始
    S = initStability(g);
    D = initDifficulty(g);
  } else {
    R = retrievability(elapsedDays, prev.stability);
    D = nextDifficulty(prev.difficulty, g);
    S = g === 1 ? stabilityAfterForget(prev.difficulty, prev.stability, R) : stabilityAfterRecall(prev.difficulty, prev.stability, R, g);
  }

  const interval = intervalFromS(S);
  const next = new Date(Date.now() + interval * 86400000).toLocaleDateString("en-CA", { timeZone: "Asia/Taipei" });

  return {
    difficulty: Math.round(D * 100) / 100,
    stability: Math.round(S * 100) / 100,
    interval_days: interval,
    next_review: next,
    mastery_level: masteryFromStability(S),
    retrievability: Math.round(R * 1000) / 1000,
  };
}
